# FEA-12-CORE 分片 A（Python Core）实施记录与证据索引

> Owner：`fea12-core-py`（DSH Agent Teams 分片 A）。本文件是分片 A 的实施记录 +
> Canonical Evidence 索引；分片 B（.NET Host 桥/R-002）的证据见同目录
> `core-host-*.json` / `core-host-implementation-record.md` / `logs/core-host-*`，
> 本分片不修改、不重述。
>
> 范围冻结：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md`（D1–D8）；wire 冻结：
> M2-C1 rev 2.13（FEA-12-PREREQ-1）。任务卡：`doc/tasks/FEA-12-CORE.md`。

## 1. 交付内容（Python Core，分片 A）

### 1.1 A 流程（应用回收站软删/恢复/读取）

| 面 | 实现 |
|---|---|
| Domain | `Book.restore()`（`src/domain/books/entities.py`）：只清 `deleted_at` + bump `updated_at`；不触碰 current/pin/Lock/进度/binding |
| Repository | `SqliteLibraryRepository.move_book_to_trash` / `restore_book_from_trash` / `list_trash_entries`（单语句逐项、`deleted_at` 唯一变更） |
| Core wire | `MoveToTrash` / `RestoreFromTrash`（minor 13，closed shape，`entries[1..200]` + `idempotency_key`），`ListTrash`（opaque base64url cursor + `limit 1..200`，默认 50） |
| 逐项原子 | 每项独立语句/结果；不存在/已软删/不在回收站 → `skipped`/`conflicts`（`TRASH_ENTRY_NOT_FOUND`），不整批失败 |
| 冻结面 | `ListRecycleBinBooks`（minor 2.11 面）零改动：空数组≠失败、`page_count` None 通道保持 |

### 1.2 C 流程（只读预览 → 专门确认 → 单事务彻底删除）

| 面 | 实现 |
|---|---|
| 预览 | `PreviewPermanentDeleteBooks`（minor 11，`bookIds` camelCase frozen）→ `inventoryDigest`/`inventoryDigests`/`computedAt`/`items`；PD-01 全字段；零写、零缓存、零预解锁 |
| digest | C-04b §2.1 canonical（键递归排序、UTF-8、无空白 JSON；`sha256:` 前缀小写 hex）；集合级 = 按 `bookIds` 顺序拼接逐书 hex 后再 SHA-256 |
| 确认 | 单条追加 `inventory_digest`（bind 逐书 digest）；批量追加集合级 `inventory_digest` + 逐书 `inventory_digests`（两级校验）；格式错/缺失 → `INVALID_REQUEST`（不进入预检），不匹配 → `BOOK_DELETE_STALE_PREVIEW` 零副作用 |
| 事务 | `execute_permanent_delete_db` 改显式 `BEGIN IMMEDIATE`；全部内容行/保护行/清理清单同事务；失败整体回滚、不开始文件清理（PD-05/PD-06） |
| D1 X1 | 同事务删除 `source_binding_publications` → `source_revision_lineage` → `page_bindings`（child-first，C-17 无 CASCADE）；`source_sync_plans`/`source_operations` 保留；非终态 operation（started/host-authorized/core-committed）→ `BOOK_BUSY` 零副作用 |
| PD-08 | 可安全拆分的共享 managed 文件/artifact 路径：只删目标书行，共享物理文件与其他项目 binding 保留；out-of-target `source_artifact_revision_id` 悬挂指针在事务内置 NULL（沿用 page 级 purge 先例）；真正不可拆（schema CHECK 不允许 detach 的 publication previous 边/关系图不一致）→ `BOOK_DELETE_CONFLICT` |
| PD-07 | `cleanup_pending` 持久 manifest + 显式重试；重试只针对 pending ID（已完成的 ID 重放 → 预检 `BOOK_NOT_FOUND`），不后台自动重试 |
| 保护披露 | `manualRegionCount`（regions.text_json.manual_edited）、`lockCount`（三锁 ∪ text_json.translation_locked 并集）、`currentRevisionId`、`pinnedRevisionIds`、`activeRunIds`、`draftPageCount`、`deletedFiles/deletedBytes`、`sharedFileRefs` |
| PurgeTrash | **首版不实现**：保留冻结 wire 注册，dispatch 返回 typed `UNKNOWN_COMMAND`（validation/false），零副作用；未追加 digest 字段、无隐藏实现。capability `library.trash.write/1` 仅代表 MoveToTrash/RestoreFromTrash 可用 |

### 1.3 统一 ProtectionPolicy（C-09 SC-B04a）

`src/application/maintenance/ports.py` 提供唯一判定函数
`ProtectionPolicy.evaluate(scope, facts) -> {blocked, reasons[]}`，三条路径共用：

* `SOFT_DELETE`：任何保护事实均不阻断（数据原样保留，恢复只清标记）；
* `AUTO_CLEANUP`：锁/人工修改/current/pinned/草稿 → 阻止（不清人工成果）；
* `PERMANENT_DELETE`：锁/人工/current/pinned/草稿 → **披露但不阻断**（`disclosure_required=True`）；仅非终态 Run/Task/Export（`BOOK_BUSY`）与不可安全拆分共享（`BOOK_DELETE_CONFLICT`）阻断。

`ProtectionPolicy` 不 import infrastructure；Cache 清理面继续使用既有
`is_safe_relative_path`（只清 `cache/` 前缀），AC10 回归见
`tests/maintenance/test_cleanup.py`。

### 1.4 命令面/capability

* `core.ping` 在 **library repository + managed storage 已装配** 时公告
  `library.delete.preview/1`、`library.trash.read/1`、`library.trash.write/1`
  （与 `source.sync.*` 同一"已装配才公告"模式；最小手搭 Core 不虚报）。
* 命令版本：preview minor 11；trash family minor 13；既有 delete family 保持 minor 10
  （digest 为 additive 字段）。错误 envelope 与既有 delete/batch 错误视图同形。

## 2. 实现语义固化（DSH 裁决 2026-11-05，写入本卡）

1. **`currentRevisionId`**：book 无单一 current 列；取该书**首个 lineage-visible
   region** 的 `current_revision_id`（顺序：chapter sort/import/chapter_id →
   page sort/page_id → region reading_order/region_id；可见性过
   `LineageIsolationGuard.is_region_readable`，与 FEA-11-LINEAGE-1 已释放读口径一致）；
   无 region 时取首个 artifact current；均无 → `null`。
2. **`pinnedRevisionIds`** = `region_revisions.is_pinned=1 ∪
   artifact_revisions.is_pinned=1`（去重、排序）；覆盖 PD-01"受保护 artifact"。
3. **`sharedFileRefs.fileId`**：managed 共享文件 = `"managed:" +
   sha256(managed 相对路径) 前 16 hex`（不泄路径）；引用源共享 =
   `source_entries.entry_id`；`otherProjectCount` = 目标集外其他 book 引用数。
4. **digest canonical** 见 1.2，golden 向量：
   `verification/FEA-12-CORE/evidence/core-py-inventory-digest-golden.json`。
5. **PD-08 跨项目 revision 引用**：可安全拆分不阻断；事务内把目标集外行
   `source_artifact_revision_id` 置 NULL（保留存活行/文件），目标行删除；依据
   ADJ-2026-11-05 D3 + page 级 purge 先例（`tests/storage/test_purge_integrity.py`
   `test_purge_clears_cross_page_provenance_instead_of_failing`）。
6. **PurgeTrash**：见 1.2。UI 不得调用，Host 不得以 `UNKNOWN_COMMAND` 探测能力
   （必须先 probe `core.ping`）。
7. **幂等键任务级语义**（M2-C1 §5.14 授权实现卡登记）：`idempotency_key` 必填、
   opaque string(1..128)；不建跨进程持久幂等缓存；同键重放按逐项语义天然幂等
   （已 move → skipped；已 restore → conflict；零额外副作用）。
8. **cleanup_pending 重试**（PD-07/§5.11.1a）：重试请求仍须携带格式合法的 digest，
   但目标 book 行已不存在、无法重算预览 → 仅校验形状（首次预览已绑定）；重算 digest
   的比较只对存活 book 生效。

## 3. 预期行为变更（Review 不得判回归）

1. **digest 变为必填**（M2-C1 rev 2.13 §5.11.1a 冻结）：既有
   `tests/core/test_core_delete_commands.py` 全部 delete 调用改为"先 Preview、
   再回传 digest"；旧 Host 不传 digest 时新 Core `INVALID_REQUEST` fail-closed，
   不降级软删。不是放宽断言，而是按冻结契约更新测试调用面。
2. **PD-08 共享引用**：原"存在共享 managed/共享 artifact/跨项目 revision 引用 →
   一律 `BOOK_DELETE_CONFLICT`"按 ADJ D3 修正为可安全拆分不阻断（原测试 :323/:378
   期望随之更新：共享文件保留、行删除成功；跨项目 provenance 置 NULL；仅真正不可
   拆分才 CONFLICT）。
3. **page 级 purge 补 C-17 子图**（`SqliteLibraryRepository.purge_pages`）：v7/v8
   行存在时不再 FK 失败；`tests/storage/test_purge_integrity.py` fixture 补齐
   v7/v8 行（D1 X1 同语义）。
4. **capability 列表新增 3 名**：`tests/core/test_core_service.py` 生产装配断言随之
   更新；最小手搭 Core（无 library repository）不公告，`tests/fea09` 既有断言不变。

## 4. AC 状态与证据（分片 A）

| AC | 分片 A 状态 | 证据 |
|---|---|---|
| AC1 软删 | MET | `logs/core-py-ac1-move-to-trash.log`；`tests/core/test_core_trash_commands.py` move 组（仅 deleted_at 变更、全表快照、受管文件哈希不变、逐项原子） |
| AC2 恢复 | MET | `logs/core-py-ac2-restore.log`；恢复后全表快照与删除前逐项相等（books 仅 deleted_at/updated_at 变化）、current/pin/进度/manual/binding 不变、逐项冲突 |
| AC3 读取面不回归 | MET | `logs/core-py-ac3-recycle-read.log`；`ListRecycleBinBooks` 冻结投影/`page_count=None`/空数组≠失败；`ListTrash` 形状/分页/排序 |
| AC4 只读预览 | MET | `logs/core-py-ac4-preview.log`；预览前后全表+文件 hash/mtime 不变；PD-01 三强制项；无路径/明文/堆栈；golden digest 独立复算一致 |
| AC5 专门确认绑定 | MET | `logs/core-py-ac5-digest-binding.log`；缺失/格式→INVALID_REQUEST；集合级+逐书两级；重排→STALE；预览后加锁→STALE 零副作用；重预览后可删 |
| AC6 单事务/回滚 | MET | `logs/core-py-ac6-transaction-rollback.log`；`BEGIN IMMEDIATE` 实跑记录；最后一条 DELETE 前注入异常→全表快照相等、文件保留、无 manifest、FK check 空、未开始清理；pending 重试成功 |
| AC7 保护披露/边界 | MET | `logs/core-py-ac7-protection-boundary.log`；含锁+人工+pin+draft 的书披露计数准确、删除后保护行确实删除（披露≠阻断）；非终态 Run → BOOK_BUSY 零副作用；事务前无顺手解锁/改 current |
| AC8 共享引用/原文件 | MET | `logs/core-py-ac8-pd08-shared.log`；共享 managed/artifact 拆分成功且共享文件保留；不可拆分→CONFLICT 零副作用；原文件/源目录零触碰（隔离 + 静态扫描）；零 Windows 回收站 API |
| AC9 C-17 子图（X1） | MET | `logs/core-py-ac9-c17-x1.log`；v7/v8 FK probe 案例由失败转成功、FK check 空；非终态 operation→BOOK_BUSY 零副作用；plans/operations 保留可查；page 级 purge 同语义 |
| AC10 统一 ProtectionPolicy | MET | `logs/core-py-ac10-protection-policy.log`；A/C 共用同一 `evaluate`；有锁+草稿软删通过、彻底删除披露后可执行；非终态 Run 彻底删除 BOOK_BUSY；cache 清理不命中保护对象（回归） |
| AC11 Host 命令桥 | PARTIAL（Python 侧 MET） | `logs/core-py-ac11-python-wire.log`；Core capability 公告 + preview/trash dispatch/closed shape/typed unsupported；.NET registry/dispatcher/client 注册与 R-002 白名单归 `task-7`（fea12-core-host），Lead 集成时合并定稿 |
| AC12 隔离与禁令 | MET | `logs/core-py-ac12-isolation.log` + `evidence/core-py-isolation-scan.json`；全部 fixture 用 `tmp_path`/workspace 临时根；静态扫描 src 零 Windows 回收站 API、删除模块零真实用户根；运行时哨兵证明隔离根外零变化 |

## 5. 真实测量与门禁

* `pytest tests/core tests/storage tests/maintenance tests/fea12 -q`：**1096 passed**（相关组，含新增/改写测试）。
* `pytest tests -q -p no:warnings --tb=no`：见 `logs/gates-core-py.log`（基线 3093 passed / 10 skipped；本分片新增测试，数字按实跑记录）。
* `check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md`、`verify_pins.ps1`：见 `logs/gates-core-py.log`。
* 全量 .NET：属分片 B/Lead 集成门禁；本分片零 .NET 改动，可引用 `logs/core-host-dotnet-full-*.log` 上一轮数字（Lead 复核）。
* 证据探针（可复跑）：
  * `scripts/core_py_inventory_digest.py` → `evidence/core-py-inventory-digest-golden.json`
  * `scripts/core_py_isolation_scan.py` → `evidence/core-py-isolation-scan.json`

## 6. 残余风险 / 已知限制

1. **AC11 的 Host 侧**（capability probe 接线、R-002 白名单/抛出选择、.NET 负向对照）
   由 task-7 交付；本分片只保证 Core 侧 capability 公告与命令 dispatch 可用。
2. **`activeRunIds` 不包含 active export**：wire 无 export 字段；preview 披露仅 run 列表，
   export 作为 BOOK_BUSY 阻断项在确认阶段生效（wire 冻结缺口，登记不扩字段）。
3. **`deletedBytes` 以实际文件 stat 计算**（缺失文件计 0）；digest 因此绑定预览时的
   文件字节数——预览与确认之间文件变化会触发 STALE（符合 PD-04，但大书预览有 stat 成本）。
4. **page 级 purge 的跨页 lineage 外键**：若存在 out-of-target lineage 行引用被 purge
   页的 revision（当前应用层不可产生），FK 会整事务回滚（fail-closed，未静默）；
   book 级 C 流程对该类关系按 PD-08 预检 CONFLICT。
5. **catalog preview 派生文件不计入 deletedFiles/deletedBytes**（可重建缓存，按 manifest
   清理清单处理）；不影响 DB 事务与 AC 语义。
6. 真实 Windows 回收站（D 流程）NOT_RUN：首版按范围冻结零实现、零 OS API。
