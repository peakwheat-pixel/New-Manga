# TASK-028：统一 SQLite 持久化设计（冻结）

状态：设计冻结；实现未释放。

冻结基线：`4a1df8fb5bc90e1542113c5ae3b15cb837146f79`（TASK-008 集成收口后）。

适用范围：TASK-006、TASK-007、TASK-008 的持久化收敛。
不包含：业务代码、UI、Pipeline、Provider、StepResultCandidate、Constraint、TM 或发布验收。

本文件是统一 SQLite 持久化的唯一设计记录。后续实现必须以本文件和对应的获批 Task 为准；聊天内容、临时实验或某个 Agent 的私有约定不能覆盖这里的边界。

## 1. 现状证据与问题边界

- `src/infrastructure/sqlite/schema.py` 当前只有 v1 `v1__storage_base`：`books`、`chapters`、`pages`、Artifact revision 及数据库元数据表。
- `src/infrastructure/sqlite/artifacts.py` 已实现 Artifact 的文件发布、Hash 校验、短事务 compare-and-write；不应重写或复制这套逻辑。
- `src/application/library/ports.py` 的 `LibraryRepository` 和 `src/application/importing/images/ports.py` 的 `ImportPageSink` 是 TASK-007 的消费侧契约，当前没有 SQLite adapter。
- `src/application/editing/ports.py` 的 `RegionRepository` 是 TASK-008 的消费侧契约，当前只有测试用的内存 fake，没有 SQLite adapter。
- TASK-007/TASK-008 有意没有修改 `src/ports/repositories/**`、`src/infrastructure/sqlite/**`；这不是缺失事实，而是已记录的后续协调边界。

因此，本设计只解决“同一个 SQLite 数据库承载书架、Page 导入、Region/Revision，并继续兼容 Artifact”的持久化 seam，不把尚未授权的完整产品能力提前实现。

## 2. 决策

### 2.1 采用：共享连接 + 按消费契约拆分 Adapter

一个应用实例只使用一个经现有 `open_database()` 打开、经 `MigrationRunner` 管理的 SQLite 数据库。各 Adapter 共享该连接，但按职责拆分：

| Adapter | 实现的现有契约 | 责任 |
|---|---|---|
| `SqliteArtifactRepository`（已存在） | `ArtifactRepositoryPort` | Artifact 元数据、不可变文件引用、ArtifactRevision current pointer |
| `SqliteLibraryRepository`（拟议） | `LibraryRepository`、`ImportPageSink` | Book/Chapter/Tag/BookTag 与 Page 导入持久化 |
| `SqliteRegionRepository`（拟议） | `RegionRepository` | Region current state、RegionRevision 历史、Pin/恢复所需字段 |

Adapter 接收注入的 `sqlite3.Connection`；不创建全局单例、不在 Domain/Application 中导入 `sqlite3`，也不建立一个包含所有对象操作的“万能 Repository”。这保留深模块 seam：Application 只依赖已有消费侧接口，SQLite 细节留在 Infrastructure。

### 2.2 复用而不是改写现有基础设施

- 继续使用现有 `open_database()` 的 `foreign_keys=ON`、WAL、busy timeout、`query_only` 兼容门控。
- v1 迁移内容不可编辑；统一持久化只能追加 v2 或更高版本迁移。
- 每次迁移仍由现有 MigrationRunner 在迁移前备份、单迁移事务内执行并写入 checksum。
- Artifact 的已验证 commit 顺序、文件安全边界和 `current_revision_id` 约束保持原语义。

### 2.3 不采用的方案

| 方案 | 结论 | 原因 |
|---|---|---|
| 每个切片各自一个数据库 | 拒绝 | 破坏 Book→Chapter→Page→Region/Artifact 的 FK、重启一致性和统一迁移门控 |
| 一个巨型 `SqliteRepository` | 拒绝 | 聚合职责、错误边界和测试 seam 混在一起，后续 Pipeline 会被迫依赖无关 API |
| 把消费侧 Protocol 全部搬到 `src/ports` | 暂不采用 | 会改变 TASK-007/008 已完成的应用依赖方向；没有必要的共享行为证据 |
| 复制一套新的 Region/Artifact revision 表 | 拒绝 | 会造成两套 current/pin/restore 语义；RegionRevision 与 ArtifactRevision 仍是不同数据族，但各自只有一套真值 |

## 3. Schema 设计冻结

下一个迁移版本拟命名为 `v2__library_region_persistence`。具体 SQL 属于后续获批实现 Task；本节冻结表、字段语义、约束和升级行为，不表示本轮已生成迁移。

### 3.1 现有表的扩展

`books` 保留 v1 字段，并补齐 `Book` 当前实体字段：`original_title`、`author`、`publisher`、`series_title`、`description`、`source_language`、`target_language`、`source_url`、`notes`、`default_chapter_type`、`default_reading_direction`、`is_favorite`、`is_archived`、`last_opened_at`。枚举按其字符串值存储，布尔值按 `0/1` 存储；收藏/归档不是 Tag。

`chapters` 保留 v1 字段，并补齐 `Chapter` 当前实体字段：`chapter_number`、`subtitle`、`import_order`、`chapter_type`、`reading_direction`、`notes`。必须保留 `webtoon=vertical`、`paged=rtl/ltr` 的 Domain 不变量；数据库 CHECK 只做稳定的值域保护，完整语义仍由 Domain 校验。

`pages` 保留 v1 的 FK 锚点和排序字段，并补齐 `Page`/本地导入所需的：`source_filename`、`source_order`、`source_hash`、`source_size_bytes`、`width`、`height`、`managed_original_ref`、`page_locked`、`review_state`、`overall_status`。

v1 可能已有仅供 Artifact 外键使用的“结构占位 Page”。迁移不得伪造源文件 Hash、Managed Copy 引用或图像尺寸：新增字段对这类旧行允许为 NULL；新建 Page 必须由 Adapter 写入完整非空值，并由 `Page` mapper 拒绝不完整记录。`existing_source_hashes()` 与 `max_source_order()` 只读取完整导入行。后续若要把旧占位行转成可显示 Page，必须另有明确的回填/迁移 Task，不能在本切片猜测原始文件。

### 3.2 新增书架关系表

- `tags(tag_id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)`。
- `book_tags(book_id TEXT NOT NULL REFERENCES books(book_id), tag_id TEXT NOT NULL REFERENCES tags(tag_id), PRIMARY KEY(book_id, tag_id))`。
- Tag 删除与其 `book_tags` 关系删除必须是同一事务；不得删除 Book。
- `find_tag_by_name()` 使用精确名称匹配，不在 Adapter 中暗自做大小写、语言或空白归一化。

### 3.3 Region 与 RegionRevision

`regions` 保存 Region 的当前可查询状态：

`region_id`、`page_id`、`region_type`、`reading_order`、`geometry_json`、`text_json`、`style_json`、`sfx_policy`、`region_locked`、`translation_locked`、`inpaint_locked`、`current_revision_id`、`created_at`、`updated_at`、`deleted_at`。

其中：

- `geometry_json` 对应 `RegionGeometry.as_jsonable()`；
- `text_json` 覆盖四级文本、`final_source`、`edited_confirmed`、`manual_edited` 和文本级 `translation_locked`；
- `style_json` 对应 `TextStyle.as_jsonable()`；
- `region_type`、`sfx_policy`、Review/Lock 等值域必须与 TASK-002 和 Domain 枚举一致；
- JSON 只承载结构化快照，不承载文件内容或 Secret。

`region_revisions` 保存不可变历史：

`region_revision_id`、`region_id`、`revision_no`、`snapshot_json`、`origin`、`review_state`、`is_pinned`、`source_run_id`、`source_step_run_id`、`restored_from_revision_id`、`created_at`。

必须有：

- `UNIQUE(region_id, revision_no)`；
- `current_revision_id` 与 `region_id` 的复合外键，确保 current 属于同一 Region；
- 首次 Revision 与 Region current pointer 的原子提交边界；
- current pointer 一旦建立不得清回 NULL；
- Pin 只改变 `is_pinned`，不改写历史 snapshot；
- 恢复通过新增 `origin=restored` Revision 并写入 `restored_from_revision_id`，不得把 current 直接重指向旧历史。

Region current state 与 revision snapshot 有意各存一份：前者服务当前查询和软删除，后者保证历史不可变。两者只允许由同一 Revision commit 操作更新，不能由两个不相关的写入路径各自维护。

### 3.4 Artifact 关系

`media_artifacts`、`artifact_revisions` 继续使用 TASK-006 v1 结构和已验证的复合 current 外键。它们通过同一 `pages` 表与 Region 关联，但 Artifact 文件仍在 Managed Storage，SQLite 只保存路径、Hash、尺寸、来源和 provenance 元数据。

## 4. 写入、重启与失败语义

### 4.1 统一连接与事务

- Adapter 的每个公开写操作都必须拥有明确事务边界；普通 CRUD/Tag 关系/Page 插入使用单次短事务。
- 需要 compare-and-write 的操作使用 `BEGIN IMMEDIATE`，事务内重新读取 current 和必要的保护状态，成功才提交。
- 失败、冲突、取消不能改变既有 current pointer；SQLite 回滚不能留下半个关系或半条 revision。
- 每文件导入仍按“读取源文件→解码→Managed Copy→提交 Page”逐文件提交；取消后已经提交的 Page 保留，未处理文件作为 pending，不把整批导入伪装成一个不可取消的大事务。

### 4.2 Region Revision 的原子 seam

当前 `RegionEditingService` 的内存实现按 `add_revision()` 后 `update_region()` 两次调用表达一次逻辑提交。SQLite 实现不得把这两个调用分别提交后就声称满足 TASK-002 的原子 current 语义。

后续实现 Task 必须在最小范围内提供一个“Region + Revision + current pointer”原子提交操作（可在 `RegionRepository` 增加 `commit_region_revision` 之类的明确方法），至少接收调用方的 `expected_current_revision_id`，并在同一 `BEGIN IMMEDIATE` 内：

1. 重新读取 Region current；
2. 检查 expected current 是否仍匹配；
3. 写入新 Revision 与当前 Region 状态；
4. 更新 current pointer；
5. 冲突或数据库失败时整体回滚并保留旧 current。

应用层应把现有两调用路径收敛到这个 seam；不得为了维持旧调用形状而隐藏一个未提交事务，也不得让 `add_revision()` 隐式覆盖 current。自动 Pipeline 写入的 Lock 重读、Candidate 落库和 Step 语义仍由 TASK-011 负责，TASK-028 不把它们提前宣称完成。

## 5. Adapter 与代码边界

后续实现 Task 的最小允许范围拟为：

- `src/infrastructure/sqlite/**`：v2 migration、Library/Page adapter、Region adapter；复用现有 connection/migrator/artifact 实现；
- `src/application/library/ports.py`、`src/application/importing/images/ports.py`、`src/application/editing/ports.py` 及必要的 editing service：仅在原子 Region commit seam 或类型映射确实需要时修改；
- `src/ports/repositories/**`：仅在需要新增共享数据库/事务 Port 时修改；
- `tests/library/**`、`tests/editing/**`、`tests/storage/**`：契约、重启、迁移、回滚和 Artifact 回归证据；
- 对应 `doc/tasks/`、`doc/handoffs/`、`doc/reviews/`、`verification/` 记录。

当前冻结设计 Task 不修改以上源码和测试。实现不得修改 Domain 语义、QML/UI、Provider、Pipeline、依赖清单、用户源文件或现有 v1 migration 内容。

## 6. 实现验收门槛（当前均未执行）

后续实现至少必须提供以下证据；这些条目不把当前 TASK-006/007/008 的内存 fake 测试改标为 SQLite PASS：

- v1 空库初始化、v1→v2 升级、迁移前备份、checksum、失败回滚和旧程序打开新 Schema 的 `TOO_NEW/query_only` 行为；
- 同一数据库重启后 Book/Chapter/Tag/BookTag/Page 与 Region/RegionRevision 的 round-trip；
- FK、软删除、排序、Page source order 与 sort order 分离，源文件未被写入；
- Region 首次 Revision、连续历史、Pin、恢复新 Revision、current 不可清空及冲突回滚；
- 现有 Artifact safe commit 测试在 v2 数据库上回归通过；
- 无 StepResultCandidate、Constraint、TM、Provider Secret 或文件二进制被错误写入 SQLite 的边界检查。

本设计本身只进行文档一致性检查；不执行产品测试，也不改变 `doc/13_ACCEPTANCE_TRACEABILITY.md` 中现有产品 AC 的结果。产品 AC 仍须由绑定实现 Task 的真实代码和固定 commit 证据更新。

## 7. 冻结后的变更规则

本设计冻结的是数据归属、迁移方向、Adapter seam、事务不变量和非目标边界。若实现发现必须改变 Region current 语义、表归属、源文件保护、v1 兼容策略或应用依赖方向，必须先在新 Task 中记录影响并由 Codex/用户重新批准；不能在 ZCode 或 DeepSeek Harness 分支中静默扩大范围。

R-201（`edited_confirmed` 继承）和 R-202（拆分后的 `reading_order` 归一化）仍按 TASK-008 Review 记录为后续产品语义问题；本设计不借 SQLite 落地顺便裁决它们。
