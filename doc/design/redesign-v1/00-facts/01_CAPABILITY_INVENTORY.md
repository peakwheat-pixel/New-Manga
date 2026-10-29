# 01 能力全量清单（能力兜底基线）

> **文档性质**：L1 只读事实盘点。本文件是新 UI/UX 设计的「能力兜底清单」——新设计不允许丢掉这里判定为「已实现/部分」的真实能力，也不允许把「未实现 / 仅有 domain / 仅测试通道」的能力当成产品能力来设计。
>
> **事实优先级**：`src/**` 与 `apps/**` 源码 > 测试 > `doc/**`。`doc/**` 只作为「声称」来源，与代码冲突时以代码为准，并在 `05_GAP_LIST.md` 记差异。
>
> **证据约定**：所有结论附 `file:line`。路径相对仓库根 `G:\CODEX\New Manga`。查不到的写 `UNVERIFIED` 并说明查了哪里。**本文件不含设计建议**（那是 Lead 的职责）；「新 UI 是否必须暴露」只表达能力完整性层面的要求。

---

## 0. 命令面总览（CORE ↔ TAURI ↔ 前端）

### 0.1 协议信封

| 项 | 值 | 证据 |
|---|---|---|
| 协议名 | `new-manga.core` | `src/bootstrap/core_service.py:204` |
| 协议主版本（全局冻结） | `PROTOCOL_MAJOR = 2` | `src/bootstrap/core_service.py:205` |
| 协议次版本（默认服务面） | `PROTOCOL_MINOR = 3` | `src/bootstrap/core_service.py:233` |
| P15 设置面次版本 | `_P15_PROTOCOL_MINOR = 7` | `src/bootstrap/core_service.py:234` |
| CreateBook/CreateChapter 次版本 | `_CREATE_PROTOCOL_MINOR = 8` | `src/bootstrap/core_service.py:235` |
| 永久删除次版本 | `_DELETE_PROTOCOL_MINOR = 10` | `src/bootstrap/core_service.py:236` |
| 传输 | stdio JSON-lines（一行一请求） | `src/bootstrap/core_service.py:1-15`, `4553-4573` |

**语义**：`major` 不符 → `PROTOCOL_VERSION_UNSUPPORTED`(validation)；`minor` 不符按命令族再判定（旧命令保持各自冻结的 minor 语义）。同一 major 内新增命令/可选字段属「向后兼容加宽」，`minor` 只在加命令时 bump（`core_service.py:206-236` 的注释是冻结的演进记录）。

### 0.2 Core 侧命令全集（按分发分支清点）

| 命令族 | 命令 | 证据 |
|---|---|---|
| 握手 / 生命周期 | `core.ping`、`core.shutdown` | `core_service.py:3608-3618`, `4472-4500` |
| Host 控制通道（独立信封 `channel=host-control`） | `OpenHostSession`、`CloseHostSession`、`RegisterImportSource`、`RevokeImportSource`、`RegisterExportTarget`、`RevokeExportTarget` | `core_service.py:244-247`, `1114-1223` |
| 作品/章节 | `ListBooks`、`ListRecycleBinBooks`、`CreateBook`、`CreateChapter`、`PermanentlyDeleteBook`、`PermanentlyDeleteBooks` | `core_service.py:237-238`, `3533`, `3578-3581`, `3734-3840` |
| 导入 | `ImportPages` | `core_service.py:3620-3647` |
| 阅读 | `GetReaderProjection`、`SaveReadingProgress` | `core_service.py:3649-3696` |
| 页面/章节导航 | `list_chapters`、`list_chapter_pages`、`resolve_page_resource` | `core_service.py:4335-4471` |
| 区域 | `set_region_type`、`list_regions`、`list_region_revisions`、`restore_region_revision`、`rerender_page` | `core_service.py:4164-4256`, `4257-4334` |
| Run | `StartRun`、`ControlRun`、`ResumeBlockedRun`、`GetRunSnapshot`、`GetTaskProjection`、`RetryFailedTargets` | `core_service.py:248-251`, `3698-3705` |
| 导出 | `StartExport`、`GetExportSnapshot`、`GetExportHistory`、`CancelExport` | `core_service.py:3649-3696` |
| 设置（基础） | `settings.get`、`settings.update_section` | `core_service.py:3928-3982` |
| 设置（P15 面，19 条） | `settings_provider_profiles_{list,create,update,delete}`、`settings_provider_bindings_{set,clear,resolve}`、`settings_provider_run_snapshot_get`、`settings_resolve_overrides`、`settings_network_profiles_{list,create,update,delete,test}`、`settings_network_profile_default_{set,clear}`、`settings_network_profile_resolve`、`BindProfileCredential`、`ClearProfileCredential` | `core_service.py:310-330`, `3707-3733` |
| 备份 | `backup.create`、`backup.list`、`backup.restore`、`backup.delete` | `core_service.py:267-272`, `3983-4032` |
| 缓存清理 | `cleanup.preview`、`cleanup.run`、`cleanup.retry_pending` | `core_service.py:259-263`, `4087-4163` |
| 插件 | `plugins.list`、`plugins.set_enabled`、`plugins.set_plugin_enabled`、`plugins.audit_list` | `core_service.py:279-284`, `4033-4086` |
| 探针（非产品能力） | `core.detect` | `core_service.py:21-37`（docstring 明确 "Verification/tooling surface only"）, `3833-3927` |

### 0.3 Tauri 命令全集（生产模式注册）

生产 `generate_handler!` 注册 **66 条**命令，全部列在同一处清单里：`apps/desktop/src-tauri/src/main.rs:1853-1920`。其中 **19 条**的实现体在 `apps/desktop/src-tauri/src/settings_bridge.rs`（`credential_put:288`、`credential_clear:335`、15 条 `settings_*`、`settings_provider_run_snapshot_get:1030`、`settings_resolve_overrides:1161`），其余定义在 `main.rs`（`core_ping:394` … `library_delete_books_permanently:1176`）。

- probe 模式命令（`probe_config`/`probe_write_results`/`probe_exit`/`probe_issue_url`）**只在 probe 模式注册**：`main.rs:1826-1834`。
- ac1 模式命令（`ac1_request`/`ac1_write_results`/`ac1_exit`）**只在 ac1 模式注册**：`main.rs:1840-1847`。
- `register_catalog` **任何模式都不注册**：`main.rs:1811-1813`（前端仍在 probe 路径尝试调用以验证其被拒，`App.tsx:129`, `366-371`）。

### 0.4 前端实际调用的命令（UI 出口现状）

| 客户端文件 | 覆盖命令 | 证据 |
|---|---|---|
| `frontend/src/library/client.ts` | `core_ping`、`library_list_books`、`library_list_recycle_bin_books`、`library_create_book`、`create_chapter`、`library_delete_book_permanently`、`library_delete_books_permanently`、`library_import_file`、`library_import_folder`、`list_chapters`、`list_chapter_pages`、`resolve_page_resource` | `library/client.ts:48-71`, `112`, `122` |
| `frontend/src/reader/client.ts` | `library_get_reader_projection`、`library_save_reading_progress` | `reader/client.ts:39-40` |
| `frontend/src/region/client.ts` | `list_regions`、`set_region_type`、`list_region_revisions`、`restore_region_revision`、`rerender_page` | `region/client.ts:41-48` |
| `frontend/src/workbench/client.ts` | `library_start_run`、`library_control_run`、`library_resume_blocked_run`、`library_get_run_snapshot`、`library_get_task_projection`、`library_retry_failed_targets`、`library_start_export`、`library_cancel_export`、`library_get_export_snapshot`、`library_get_export_history`、`library_reveal_export_folder` | `workbench/client.ts:224-314` |
| `frontend/src/settings/client.ts` | `settings_get`、`settings_update_section`、Provider/网络/凭据 15 条、`cleanup_*`、`backup_*`、`plugins_*` | `settings/client.ts:55-141` |
| `frontend/src/resourceChannel/client.ts` | `issue_resource_url`、`revoke_ref` | `resourceChannel/client.ts:58`, `69` |

**未被任何前端客户端引用的生产命令**（B 类缺口，详见 `05_GAP_LIST.md`）：`settings_provider_run_snapshot_get`、`settings_resolve_overrides`、`revoke_resource_refs`、`core.shutdown`。

**另有 3 类需要区分**：
- `plugins_open_directory` 是 **Tauri 本地动作**（无 Core 命令），前端有调用（`settings/client.ts:141`）；
- 6 条 Host 控制命令（`OpenHostSession` 等）由 Rust 侧内部驱动，**不面向前端**（`core_service.py:244-247`, `1114-1223`）；
- `library_reveal_export_folder` 有前端调用（`workbench/client.ts:314`），Core 侧无同名命令（由宿主按可信导出历史解析目录，`library_bridge.rs:956-965`）。

---

## 1. 启动与首次使用（CAP-BOOT）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-BOOT-01 | 确认软件后端已就绪 | 系统启动 + 前端每 2s 心跳 | Core sidecar 已装配 | `{}` → `{status:"ready", protocol_version:{major:2,minor:3}, capabilities:["library.list_books"]}` | 桥缺失 → `TAURI_BRIDGE_MISSING`（前端）；通道失效 → `CORE_UNAVAILABLE` | `core.ping` | `core_ping` | 已实现 | `core_service.py:1249-1258`；`main.rs:393-406`；`library/client.ts:110-118`；`AppShell.tsx:68-90` | 必须 |
| CAP-BOOT-02 | （透明）协议版本握手 | 系统 | 每个请求 | 请求信封 `protocol`+`version` → 接受/拒绝 | `PROTOCOL_VERSION_UNSUPPORTED` / `INVALID_REQUEST` | 全命令前置 | — | 已实现 | `core_service.py:3498-3506`, `3590-3605` | 不建议 |
| CAP-BOOT-03 | Core 崩溃后被自动拉起并告知用户 | 宿主 supervisor 自动 | 心跳失败 / 通道 unhealthy | — → 按重试预算重启 sidecar，并推事件 `core:lifecycle_status`（`restarting`/`recovered`/`fatal`），带用户可读消息 | 重启次数耗尽 → `fatal` | （事件通道） | 事件 `core:lifecycle_status` + `trigger_restart()` | 已实现 | `library_bridge.rs:5028-5230`（supervisor：`is_unhealthy:5051`、`trigger_restart:5065`、重启预算与 `MAX_RETRIES`、消息 `5121`/`5212`/`5216`）；`main.rs:1772-1789`（status emitter 注册 + 启动即自愈）；`events.ts:48-62`；`AppShell.tsx:41-107` | 必须 |
| CAP-BOOT-04 | 上次被强行中断的任务不装死、可继续或重来 | 系统启动 | 存在 `status=running` 的 Run | — → 该 Run 及其中 RUNNING 的 Task/Step 全部转 `interrupted` | — | 装配期直接调用（无 wire） | — | 已实现 | `core_assembly.py:1273-1277`；`application/tasks/service.py:1094-1110` | 必须（必须让用户做出 continue/restart/abandon 决定） |
| CAP-BOOT-05 | 同一数据根只允许一个任务执行者（防双跑） | 系统启动 | 数据根可写 | 抢占调度器租约 → 成为 run owner；未抢到则只能服务读命令 | `INVALID_RUN_TRANSITION`（owner 不可用） | 进程内 | — | 已实现 | `core_service.py:851-905`, `1003-1063`, `3270-3273` | 不建议 |
| CAP-BOOT-06 | （透明）启动时回收陈旧预览/瓦片缓存 | 系统启动 | — | — → 回收 retired preview 与 webtoon 瓦片 | — | 装配期 | — | 已实现 | `core_service.py:4667-4745` | 不建议 |
| CAP-BOOT-07 | 第一次打开就知道下一步做什么 | 用户 | 书架为空 / 无可用章节 | — → 空态引导；无章节时导入被明确禁止 | — | — | — | 已实现（纯前端） | `BookshelfPage.tsx`；`EmptyStateBookshelf.tsx`；`ImportDialog.tsx:279-280` | 必须 |
| CAP-BOOT-08 | 升级版本后旧数据仍能打开 | 系统启动 | 数据库存在 | 数据库 `schema_version` → 顺序执行 v1..v6 迁移 | `SchemaTooNewError`（数据库版本高于本程序已知版本，拒绝且不改库） | 装配期 `MigrationRunner` | — | 已实现 | `infrastructure/sqlite/schema.py:24-32`, `597-605`；`migrator.py:69-100` | 不建议（但失败必须可见） |
| CAP-BOOT-09 | 迁移前自动留一份可回滚备份 | 系统启动 | 有 pending 迁移 | — → 每个迁移执行前创建 `pre_migration` 备份 | — | 装配期（`_BackupProvider`） | — | 已实现 | `migrator.py:86-93`；`schema.py:121-134`（`backup_records` 表） | 不建议 |

---

## 2. 作品与章节管理（CAP-LIB）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-LIB-01 | 看到我的书架 | 用户 / 启动 | Core 就绪 | `{}` → `BookSummary[]`（`book_id,title,original_title,is_favorite,is_archived,page_count,created_at,updated_at`） | `LIST_BOOKS_FAILED` | `ListBooks` | `library_list_books` | 已实现 | `core_service.py:1260-1283`, `3784-3832`；`library/client.ts:120-128` | 必须 |
| CAP-LIB-02 | 新建作品 | 用户 | Core 就绪 | `{title}` → `BookSummary` | `INVALID_REQUEST`(validation) / `LIBRARY_WRITE_FAILED`(internal) / `UNKNOWN` | `CreateBook`（minor 8） | `library_create_book` | 已实现 | `core_service.py:1316-1328`, `3505-3560`；`main.rs:567-579` | 必须 |
| CAP-LIB-03 | 在作品下新建章节 | 用户 | 作品存在 | `{book_id,title,chapter_number?}` → `{chapter_id,title,chapter_number}` | `TARGET_NOT_FOUND` / `INVALID_REQUEST` / `LIBRARY_WRITE_FAILED` | `CreateChapter`（minor 8） | `create_chapter` | 已实现 | `core_service.py:1329-1341`；`main.rs:580-603` | 必须 |
| CAP-LIB-04 | 看到作品的章节列表（按我的排序） | 用户 | 作品存在 | `{book_id}` → `{chapters:[...]}`；未知作品 = 空列表（不是错误） | `INVALID_REQUEST` / `UNKNOWN` | `list_chapters` | `list_chapters` | 已实现 | `core_service.py:2313-2338`；`frontend/library/client.ts:54` | 必须 |
| CAP-LIB-05 | 看到某章节的页面列表 | 用户 | 章节存在 | `{chapter_id}` → `{pages:[...]}`；未知章节 = 空列表 | `INVALID_REQUEST` / `UNKNOWN` | `list_chapter_pages` | `list_chapter_pages` | 已实现 | `core_service.py:2339-2363` | 必须 |
| CAP-LIB-06 | 彻底删除一个作品 | 用户 | 作品已软删除（在回收站） | `{book_id,confirm_permanent_delete:true}` → `{book_id,deleted:true}` | `INVALID_REQUEST`（缺确认）/`BOOK_NOT_FOUND`(not_found)/`BOOK_DELETE_CONFLICT`(conflict)/`BOOK_DELETE_FAILED`/`BOOK_DELETE_CLEANUP_PENDING`(可重试) | `PermanentlyDeleteBook`（minor 10） | `library_delete_book_permanently` | 已实现 | `core_service.py:1342-1407`, `3562-3588` | 必须 |
| CAP-LIB-07 | 批量彻底删除 | 用户 | 同上 | `{book_ids:[...],confirm_permanent_delete:true}` → 逐项结果 | 逐项 `error_code`（`details.items`），清理未完成 = `cleanup_pending` 可重试 | `PermanentlyDeleteBooks`（minor 10） | `library_delete_books_permanently` | 已实现 | `core_service.py:1409-1532`；`library/client.ts:29-37`（`details` 注释） | 必须 |
| CAP-LIB-08 | 找回误删的作品（回收站） | 用户 | 有软删除作品 | `{}` → `BookSummary[]`（仅 `deleted_at IS NOT NULL`） | `UNKNOWN` | `ListRecycleBinBooks` | `library_list_recycle_bin_books` | 已实现 | `core_service.py:1285-1314`, `3734-3783` | 必须 |
| CAP-LIB-09 | 在书架里搜索/筛选/排序 | 用户 | 书架已加载 | UI 本地过滤 `search`/`favoriteOnly`/`archivedOnly`/`sortBy(title,updated_at)`/`viewMode(grid,list)` | — | 无（纯前端） | 无 | 已实现（纯前端） | `BookshelfToolbar.tsx:111-215`；`bookshelf/types.ts:3-13` | 必须 |
| CAP-LIB-10 | 编辑作品元信息（原名/作者/出版社/系列/简介/语种/来源/备注） | 用户 | 作品存在 | `LibraryService.update_book(**changes)`（字段白名单） | `ValueError`（未知字段/空标题） | **无 wire** | 无 | 部分（仅应用层，`Book.apply_edit` 允许 10 个字段） | `application/library/service.py:91-96`；`domain/books/entities.py:69-83`；`core_service.py` 无 `update_book`（grep `update_book` = NONE） | 必须 |
| CAP-LIB-11 | 收藏 / 取消收藏作品 | 用户 | 作品存在 | `LibraryService.set_favorite(book_id,bool)` | — | **无 wire** | 无 | 部分（应用层已实现；UI 有 `GAP-G3` 占位说明） | `application/library/service.py:102-107`；`BookCard.tsx:49`, `61`；`BookshelfToolbar.tsx:163-183` | 必须 |
| CAP-LIB-12 | 归档 / 取消归档作品 | 用户 | 作品存在 | `LibraryService.set_archived(book_id,bool)` | — | **无 wire** | 无 | 部分（应用层已实现） | `application/library/service.py:108-117`；`BookshelfToolbar.tsx:185-204` | 必须 |
| CAP-LIB-13 | 编辑章节信息（标题/副标题/话号/备注） | 用户 | 章节存在 | `LibraryService.update_chapter(**changes)`（白名单 4 字段） | `ValueError` | **无 wire** | 无 | 部分 | `application/library/service.py:174-179`；`domain/books/entities.py:141-150` | 必须 |
| CAP-LIB-14 | 删除章节 | 用户 | 章节存在 | `LibraryService.delete_chapter`（软删除） | — | **无 wire** | 无 | 部分 | `application/library/service.py:180-184`；grep `delete_chapter` in `core_service.py` = NONE | 必须 |
| CAP-LIB-15 | 调整章节顺序 | 用户 | 作品有 ≥2 章节 | `LibraryService.reorder_chapters(book_id,[chapter_id...])` → 重排 `sort_order` | — | **无 wire** | 无 | 部分 | `application/library/service.py:185-202`；`domain/books/entities.py:152-155`（`import_order` 冻结） | 必须 |
| CAP-LIB-16 | 调整页面顺序 | 用户 | 章节有 ≥2 页面 | `Page.reorder(sort_order)`（`source_order` 冻结） | — | **无 wire** | 无 | 部分（domain 有；UI 有 `gap-g14-page-order` 占位） | `domain/pages/entities.py:46-49`；`PageListPanel.tsx:127` | 必须 |
| CAP-LIB-17 | 页面软删除 + 批量恢复（页面级回收站） | 用户 | 页面存在 | `TrashService.soft_delete_pages(...)` → 批次；`restore_batch` / `purge_batch` / `retry_pending_purges` | `TrashManifest` 级错误（见实现） | **无 wire**（装配已注入） | 无 | 部分（服务已装配，无命令出口） | `application/maintenance/trash.py:103-256`；`core_assembly.py:964-970`；`core_service.py` 无 `trash` 引用（grep `.trash.` = NONE） | 可选 |
| CAP-LIB-18 | 用标签组织作品 | 用户 | 标签存在 | `create_tag/rename_tag/delete_tag/list_tags/add_tag_to_book/remove_tag_from_book/tags_of_book` | `DuplicateTagName`（精确匹配，不归一化） | **无 wire** | 无 | 部分（应用层 + `tags`/`book_tags` 表已建） | `application/library/service.py:203-241`；`schema.py:210-221`；`domain/books/entities.py:165-180` | 可选 |
| CAP-LIB-19 | 为作品/章节设定默认阅读方向与章节类型 | 用户 | 作品/章节存在 | `Book.default_chapter_type/default_reading_direction`；`Chapter.chapter_type/reading_direction`（webtoon 必须 vertical） | `ValueError`（方向不变式） | **无 wire**（`CreateChapter` 不接受这两个字段） | 无 | 部分（domain 有；设置页明确「阅读方向是书/章属性，不提供全局默认」） | `domain/books/entities.py:55-56`, `127-139`；`SettingsPage.tsx:275-294`；`core_service.py:239-242`（`_CREATE_FIELDS` 仅 title/chapter_number） | 必须 |

---

## 3. 导入（CAP-IMP）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-IMP-01 | 把图片文件导入章节 | 用户（原生文件选择器） | 章节存在 + 宿主签发 import source | `{chapter_id, sources:[ref], duplicate_policy?}` → `{chapter_id,duplicate_policy,cancelled,sources:[{source_index,source_name,files:[...]}]}` | `INVALID_REQUEST` / `TARGET_NOT_FOUND` / `REF_*`（`_IMPORT_ERROR_CATEGORIES` 白名单投影） | `ImportPages` | `library_import_file` | 已实现 | `core_service.py:2591-2656`, `3620-3647`；`main.rs:1189-1218`；`host_issuer.rs`（grant 签发） | 必须 |
| CAP-IMP-02 | 把整个文件夹导入章节 | 用户（原生目录选择器） | 同上 | 同上（一个 source 展开为多文件） | 同上 | `ImportPages` | `library_import_folder` | 已实现 | `core_service.py:2546-2590`（`_register_import_source`）；`main.rs:1219-1240` | 必须 |
| CAP-IMP-03 | 重复页面按我的策略处理 | 用户 | 同上 | `duplicate_policy` ∈ `skip` \| `import_as_new`（默认 `skip`，按 `source_hash` 判重） | `INVALID_REQUEST`（非法策略） | `ImportPages` | `library_import_file/folder`（`duplicate_policy` 可选参数） | 已实现 | `core_service.py:2600-2607`；`application/importing/images/service.py:30-32`, `55-59`；`main.rs:1194`, `1224` | 必须 |
| CAP-IMP-04 | 坏图不会进入书架 | 系统 | 导入进行中 | 每文件：判重 → 解码校验 → Managed Copy → 提交 Page（失败的文件永不落到仓储） | 逐文件 `error`（`INVALID_IMAGE`/`UNSUPPORTED_FORMAT`/`COPY_FAILED`/`SOURCE_READ_FAILED`/…，见 `_IMPORT_ERROR_CATEGORIES`） | `ImportPages` | 同上 | 已实现 | `application/importing/images/service.py:1-9`；`core_service.py:755-800`（`_IMPORT_ERROR_CATEGORIES`） | 必须 |
| CAP-IMP-05 | 我的原图不被修改 | 系统 | 导入 | 源文件只读；写入的是 Managed Copy（`managed_original_ref` 必填） | `COPY_FAILED` | `ImportPages` | 同上 | 已实现 | `domain/pages/entities.py:9-17`, `43-44`；`application/importing/images/service.py:7-8`；`core_service.py:2658-2853` | 必须（作为安全承诺呈现） |
| CAP-IMP-06 | 导入顺序符合人类直觉（page2 < page10） | 系统 | 文件夹导入 | 文件名自然排序 + 目录内直读 | — | `ImportPages` | `library_import_folder` | 已实现 | `application/importing/images/sorting.py:13`, `19-24`, `27-30` | 可选 |
| CAP-IMP-07 | 支持图片格式 | 系统 | 导入 | 解码器支持的格式集合（MIME 映射派生，`.png/.jpg/.jpeg/.webp/.gif/.bmp/.tif/.heic` 等以 `_MIME_TYPES` 为准） | `UNSUPPORTED_FORMAT` | `ImportPages` | 同上 | 已实现 | `infrastructure/importing.py:18-37`（`_MIME_TYPES`、`SUPPORTED_IMAGE_SUFFIXES` 派生）；`core_service.py:374`（`_ORIGINAL_SUFFIXES` 复用同一权威） | 必须（格式说明） |
| CAP-IMP-08 | 导入 PDF（按页光栅化） | 用户 | 章节存在 | 文档字节 → PDFium 逐页渲染成 PNG → 走同一 Managed Copy/Page 提交 | `INVALID_DOCUMENT` / `UNSUPPORTED_FORMAT` / `COPY_FAILED` / `SOURCE_READ_FAILED` | `ImportPages` | `library_import_file/folder` | 已实现 | `application/importing/documents/service.py:22-26`；`infrastructure/importing.py:170-282`；`core_assembly.py:953-963` | 必须 |
| CAP-IMP-09 | 导入 MOBI（KF7 图片型） | 用户 | 章节存在 | MOBI 字节 → 抽取 `mobi7/Images/*` 作为页 | DRM/文本文档/KF8 → `INVALID_DOCUMENT`/`UNSUPPORTED_FORMAT` | `ImportPages` | 同上 | **部分（适配器已实现，生产装配未接线）** | `infrastructure/importing.py:283-388`（`MobiDocumentRaster`）；`core_assembly.py:958` 仅注入 `PdfiumDocumentRaster()`；`MobiDocumentRaster` 全仓仅自身定义处出现 | 可选（若不接线不应在 UI 声称支持） |
| CAP-IMP-10 | 取消导入时已完成的页保留、未处理的明确标记 | 用户 | 导入进行中 | 取消回调 → 未处理文件 `outcome:"pending"`，已提交页保留 | — | `ImportPages` | `library_import_file/folder` | 已实现 | `core_service.py:2618-2640`；`application/importing/images/service.py:6-7` | 必须 |
| CAP-IMP-11 | 看到逐页导入进度 | 用户 | 导入进行中 | **当前只有同步返回的最终结果**，无分片进度 snapshot | — | 无 | 无 | 未实现（UI 明确占位 `gap-g26-import-progress`） | `WorkbenchToolbar.tsx:84` | 可选（若不实现则不要承诺进度条） |

---

## 4. 页面与阅读（CAP-PAGE / CAP-READ）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-PAGE-01 | 看到页面的原图（不经过普通 JSON/Base64） | 系统 | 页面有 Managed Copy | `{page_id}` → 资源目录键（首次发布原图到派生只读根，之后幂等命中） | `INVALID_REQUEST` / `PAGE_NOT_FOUND`(not_found) / `UNKNOWN` | `resolve_page_resource` | `resolve_page_resource` → `issue_resource_url` | 已实现 | `core_service.py:2364-2428`, `4390-4471`；`main.rs:935-949`；`library/client.ts:48` | 必须 |
| CAP-PAGE-02 | 原图/译图逐页对照阅读 | 用户 | 章节有页；译图存在 | `{chapter_id,mode:"original"\|"translated",start_position:"resume"\|"beginning"}` → `{book_id,chapter_id,mode,layout,pages[],saved_progress,initial_position}` | `INVALID_REQUEST` / `TARGET_NOT_FOUND` / `EXPORT_INPUT_UNAVAILABLE`（译图不可用） | `GetReaderProjection` | `library_get_reader_projection` | 已实现 | `core_service.py:2429-2494`；`reader/client.ts:62-85` | 必须 |
| CAP-PAGE-03 | 阅读版式跟随作品设定 | 系统 | — | `layout` ∈ `webtoon_vertical` \| `rtl` \| `ltr`（webtoon 章节 → `webtoon_vertical`；否则取 `chapter.reading_direction`） | — | `GetReaderProjection` | 同上 | 已实现 | `core_service.py:2441-2442`；`domain/books/entities.py:26-31` | 必须 |
| CAP-PAGE-04 | 关闭后回到上次读到的地方 | 用户（自动） | 有历史进度 | `{chapter_id,mode,page_id,scroll_offset_y?,elapsed_seconds_delta?}` → `{progress_percent,...}` + 事件 `ReadingProgressChanged` | `INVALID_REQUEST`（越界/非有限值/与版式不符）/ `TARGET_NOT_FOUND` | `SaveReadingProgress` | `library_save_reading_progress` | 已实现 | `core_service.py:2496-2520`；`reading/client.ts:93-123`；`application/reading/service.py:164-224` | 必须 |
| CAP-PAGE-05 | 原图与译图各自记住进度 | 用户 | — | 进度唯一键 `(book_id, chapter_id, mode)` | — | 同上 | 同上 | 已实现 | `schema.py:420-433`（`UNIQUE (book_id, chapter_id, mode)`）；`ReadingPage.tsx:209-224` | 必须 |
| CAP-PAGE-06 | 进度变化被其他视图感知 | 系统 | — | 事件 `ReadingProgressChanged`（前端须重新查询快照，不得把事件当状态） | — | — | 事件 `core:ReadingProgressChanged` | 已实现 | `events.ts:5-9`, `42-46`, `59`；`library_bridge.rs:1129-1136`；`ReaderPage.tsx:117-152` | 可选 |
| CAP-PAGE-07 | 页面缩略图 | 用户 | 页面存在 | **无低清缩略图通道**（只有原图/译图资源通道） | — | 无 | 无 | 未实现（UI 明确占位 `gap-g18-page-thumbnails`） | `PageListPanel.tsx:128`；`TaskProgressPanel.tsx:113` | 可选 |
| CAP-PAGE-08 | Page Lock（整页锁定，禁止自动写入） | 用户 | 页面存在 | `Page.page_locked`（DB 列 + domain 字段）；规划阶段 `SKIP_LOCK:"page_or_region_locked"` | — | **无 wire** | 无 | 部分（存储/规划已实现，缺写入命令） | `schema.py:197-198`；`domain/pages/entities.py:29`；`application/tasks/service.py:517-518` | 必须 |
| CAP-PAGE-09 | 页面阶段状态与校对状态可见 | 用户 | 页面存在 | `Page.overall_status` ∈ 9 值；`Page.review_state` ∈ 3 值 | — | 无（投影现算） | 无 | **未实现（列存在但无推进代码、无读面）** | `schema.py:199-205`；`domain/pages/entities.py:30-31`；`infrastructure/sqlite/library.py:99`, `387-394`；`src/**` 无 `.overall_status=`/`.review_state=` 赋值（grep = NONE）；页状态由 Task 现算 `projection.py:327-345` | 可选 |

---

## 5. 检测 / OCR / 配色 / 术语抽取（CAP-DET / CAP-OCR）

> 前置：这些步骤全部由 **Run 规划器**调度，不是独立命令。命令入口是 `StartRun` + `CommandType`；步骤实现由 `ProductionHandlers` 注入（`infrastructure/providers/handlers.py:185-231`）。

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-DET-01 | 自动框出页面上的文字区域 | Run（`translate_*` / `reocr_*` / `ocr_region` 链）；探针 `core.detect` | 检测器已装配（manga 权重 / doctr 权重） | 页面图 → 候选框（`provider_label`、`polygon`、`reading_order`、`confidence`、`coordinate_space`） | `PROVIDER_NOT_CONFIGURED`（无权重/无检测器）/ 检测器自身 typed code | `core.detect`（仅探针面）；产品路径走 Run 的 `detect` step | `probe_issue_url` 之外无产品命令 | 已实现 | `core_service.py:1555-1754`（`handle_detect` docstring 明确「SAME instance the pipeline detect step uses」）, `3833-3927`；`core_assembly.py:1055-1130`（`NEWMANGA_DETECTOR_BACKEND` = `manga`(默认)/`doctr`/`mock`） | 必须（作为流程步骤可见） |
| CAP-DET-02 | 检测结果自动变成可编辑区域 | 系统 | detect step 成功 | 检测候选 → 落 `Region`（含 SFX 类型分派），后续区域步骤重排到真实 Region 上 | `MISSING_REQUIRED_INPUT` / `INVALID_INPUT` | Run 内部（`_backfill_detected_regions`） | — | 已实现 | `application/tasks/service.py:448-460`, `747-748`, `1188-1290`；`core_service.py:809-843`（`_detected_region_type`） | 必须（间接） |
| CAP-DET-03 | 拟声词（SFX）检测可开关并可调阈值 | 用户 | 环境变量 `NEWMANGA_SFX_DETECTION` / `NEWMANGA_SFX_CONF_THRESHOLD` / `NEWMANGA_SFX_WEIGHTS` | 页面 → SFX 候选（与主检测并行） | 未知取值 → 启动期失败（fail-closed，不做静默回退） | Run 内部（装配期读环境） | — | 已实现（装配级开关） | `core_assembly.py:1014-1030`；`infrastructure/providers/detection_sfx.py`；`infrastructure/providers/handlers.py:1-20` | 可选（若要暴露，必须是设置项而不是环境变量） |
| CAP-OCR-01 | 把气泡里的文字识别成原文 | Run（`ocr` step） | 区域存在 + OCR Provider Ready | 区域裁切图 → `ocr_text`（+ confidence，写入新 revision） | `PROVIDER_NOT_CONFIGURED`/`PROVIDER_DEPENDENCY_MISSING`/`PROVIDER_AUTH_FAILED`/`PROVIDER_TIMEOUT`/…（`ports/providers/errors.py` 全表） | `StartRun`（`CommandType` 含 ocr） | `library_start_run` | 已实现 | `infrastructure/providers/handlers.py:353-427`；`application/editing/service.py:619-646` | 必须（作为流程步骤） |
| CAP-OCR-02 | 重新 OCR 不会冲掉我人工改过的译文 | 用户 | — | `RegionText.apply_ocr` 只更新 `ocr_text`；人工译文/final 保留；原文变化 → 返回「原文已变化，现有译文可能需要重译」 | — | Run 内 `ocr` step | `library_start_run` | 已实现 | `domain/regions/entities.py:154-163` | 可选 |
| CAP-OCR-03 | OCR 语种/方向按我的设置 | 用户 | — | 设置 section `ocr`：`script` ∈ {japanese,korean,chinese,latin}；`direction` ∈ {horizontal,vertical} | `INVALID_REQUEST`（越域） | `settings.update_section` | `settings_update_section` | 已实现 | `bootstrap/settings_sections.py:54-59`, `105-112`；`OcrSettingsPanel.tsx` | 必须 |
| CAP-OCR-04 | 自动提取原文配色用于排版 | Run（`color` step） | 有 OCR 结果 | 页面像素 → 源样式（`SourceStyleService`） | Provider typed code | Run 内 `color` step | `library_start_run` | 已实现 | `application/translation/color/service.py`；`application/tasks/service.py:80-89`（`_FULL_TRANSLATION` 含 `color`） | 可选（流程步骤） |
| CAP-OCR-05 | 自动抽取术语候选 | Run（`term_extract` step） | 有 OCR 结果 | 原文 → 术语候选（上限 20，其中重复 n-gram 最多 10，最短 2 字符） | — | Run 内 `term_extract` step | `library_start_run` | 已实现（抽取本身） | `application/translation/knowledge/term_extraction.py:37-41`, `66-143`；`core_assembly.py:1237` | 可选 |
| CAP-OCR-06 | 从 OCR 模型看原文识别质量（置信度） | 用户 | — | step 输出含 `confidence`，但任务投影 wire 不含该字段 | — | — | — | UNVERIFIED（见证据列） | `infrastructure/providers/handlers.py:404-407` 确认 handler 输出 `confidence`；`core_service.py:3206-3219`（`_task_projection_to_wire`）不含置信度；是否为产品需求源码中无定论 | 可选 |

---

## 6. 翻译（CAP-TRANS）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-TRANS-01 | 把原文翻译成目标语言 | Run（`translate` step） | 区域有 `ocr_text` + 翻译 Provider Ready | 区域文本 + 上下文 → `machine_translation`（写入新 revision） | `PROVIDER_NOT_CONFIGURED` / `PROVIDER_AUTH_FAILED` / `PROVIDER_RATE_LIMITED`(retryable) / `PROVIDER_TIMEOUT`(retryable) / `PROVIDER_INVALID_OUTPUT`(retryable) / `MISSING_CREDENTIAL` / `INVALID_INPUT` | `StartRun` | `library_start_run` | 已实现 | `infrastructure/providers/handlers.py:428-517`；`ports/providers/errors.py:59-231`；`application/tasks/service.py:90` | 必须 |
| CAP-TRANS-02 | 翻译时带上上下文（前几页/Token 预算） | 用户 | — | 设置 `translate.context_pages` ∈ [1,5]；`translate.context_token_budget` ∈ [200,8000]；上下文策略写入 Run 快照 | `INVALID_REQUEST`（越界） | `settings.update_section` / `StartRun`（`context_policy`） | `settings_update_section` / `library_start_run` | 已实现 | `bootstrap/settings_sections.py:61-64`；`application/translation/context/builder.py:161-335`；`domain/tasks/models.py:398`（`context_policy`） | 必须 |
| CAP-TRANS-03 | 我改过的译文不会被自动流程覆盖 | 用户 | 区域译文被人工编辑/确认 | 规划期 `SKIP_LOCK:"translation_locked"` / `"manual_translation_protected"`；运行时 `translation_locked` 抛 `PermissionError` | — | Run 内 `translate` step | — | 已实现 | `application/tasks/service.py:527-531`；`domain/regions/entities.py:165-190` | 必须（作为「保护」承诺） |
| CAP-TRANS-04 | 最终译文取值规则可预期 | 系统 | — | `final = 已确认的人工译文 > 机器译文 > 空` | `ValueError`（无内容可确认） | — | — | 已实现 | `domain/regions/entities.py:141-151` | 可选 |
| CAP-TRANS-05 | 拟声词按全局策略跳过/翻译/手工 | 用户 | 区域 `region_type=sfx` | 全局 `settings["sfx"]["policy"]` ∈ {skip,translate,manual}；`skip` 时 translate/segment/mask_refine/inpaint/render 全部 `SKIP_POLICY` | `INVALID_REQUEST`（非法值，写侧即拒） | `settings.update_section`；`set_region_type`（重定类型时重快照） | `settings_update_section` / `set_region_type` | 已实现 | `domain/regions/entities.py:48-53`；`application/tasks/service.py:141-180`, `520-525`；`core_service.py:1959-1979`；`ports/inpaint/...` | 必须 |
| CAP-TRANS-06 | 翻译失败按 1-3 次重试、可调退避 | 用户 | — | 设置 `tasks.retry_max_attempts` ∈ [1,3]；`tasks.retry_backoff_seconds` ∈ [0.1,30.0] | `INVALID_REQUEST`（越界） | `settings.update_section` | `settings_update_section` | 已实现 | `bootstrap/settings_sections.py:96-101`；`infrastructure/providers/retry.py`；`TasksSettingsPanel.tsx` | 必须 |
| CAP-TRANS-07 | 用「术语表 / 不译表」约束翻译 | 用户 | 约束存在 | 约束合并（chapter > book > global；人工优先）→ 翻译 payload 携带 `terminology` / `do_not_translate` | — | **无 wire** | 无 | **部分（仅 domain + 上下文装配；无存储表、无命令、无 UI）** | `domain/constraints/entities.py:32-61`, `92-114`；`domain/constraints/merge.py:45-75`；`application/translation/context/snapshot.py:27-70`；`schema.py` 无 `constraints` 表（grep `terminology`/`do_not_translate` in `src/infrastructure` = NONE） | 必须（产品主承诺之一） |
| CAP-TRANS-08 | 复用历史译文（翻译记忆） | 用户 | TM 有条目 | `TranslationMemoryService.record_confirmed_translation` / `find_matches` / `set_disabled` / `record_usage` | `UnconfirmedTranslationError` | **无 wire** | 无 | **部分（应用层已实现，未装配进 Core）** | `application/translation/knowledge/tm.py:37-294`；`core_assembly.py` 无 `TranslationMemoryService`（grep = NONE） | 可选 |
| CAP-TRANS-09 | 按 Provider 参数（模型/温度等）翻译 | 用户 | Provider 配置存在 | `settings["providers"]["profiles"][provider_id] = {base_url, model, credential_ref, enabled, options}` | `PROVIDER_NOT_CONFIGURED` | `settings_provider_profiles_*` | 同名 Tauri 命令 | 已实现 | `infrastructure/providers/runtime.py:14-21`, `602-643`；`ProviderProfilePanel.tsx` | 必须 |

---

## 7. 图像修复 / 文字消除（CAP-INP）

> 修复采用「Mask 生成 → Mask 精修 → 修复路由」三段式，全部在 Run 内执行（`segment` / `mask_refine` / `inpaint` 三个 step）。

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-INP-01 | 精确圈出要擦掉的文字像素（而不是整个框） | 系统 | 区域几何存在 | 区域几何 → mask artifact（`ARTIFACT_MASK`） | `MISSING_REQUIRED_INPUT`（无干净底图/无区域） | Run 内 `segment` step | `library_start_run` | 已实现 | `infrastructure/providers/handlers.py:518-560`；`application/translation/inpaint/mask.py`；`application/tasks/service.py:567-579` | 可选（流程步骤） |
| CAP-INP-02 | 修整 mask（膨胀/腐蚀/边界保护/线稿保护） | 用户（设置）+ 系统 | mask 存在 | `inpaint.dilate_radius` ∈ [0,10]、`inpaint.erode_radius` ∈ [0,10] 等 → 精修后 mask | `INVALID_REQUEST` | `settings.update_section` + Run 内 `mask_refine` step | `settings_update_section` / `library_start_run` | 已实现 | `bootstrap/settings_sections.py:66-71`；`application/translation/inpaint/protection.py`；`application/tasks/service.py:567-579` | 必须（参数可见） |
| CAP-INP-03 | 按质量/背景复杂度自动选修复路线 | 用户（设置） | — | `inpaint.preferred_quality` ∈ {fast,balanced,quality}；`inpaint.background_complexity` ∈ {low,medium,high} → `RoutePolicy` 选路 | `PROVIDER_NOT_IMPLEMENTED`（选中未实现路线） | `settings.update_section` + Run 内 `inpaint` step | 同名 | 已实现（策略）/ 部分（可执行路线只有 2 条） | `bootstrap/settings_sections.py:66-71`；`application/translation/inpaint/router.py`；`application/translation/inpaint/route_catalog.py:13-19` | 必须 |
| CAP-INP-04 | 纯色气泡/小面积文字的高质量擦除 | 系统 | 区域 mask 存在 | 像素 → 修复后 clean artifact（`ARTIFACT_CLEAN`） | `NON_TARGET_WRITE`（越界改写 = 硬失败，结果不提交） | Run 内 `inpaint` step | `library_start_run` | 已实现（`inpaint-simple-fill`、`inpaint-edge-bleed` 两条） | `application/translation/inpaint/route_catalog.py:63-80`；`infrastructure/providers/inpaint_routes.py`；`ports/providers/errors.py:158-165` | 可选 |
| CAP-INP-05 | 复杂背景（网点/彩色 Webtoon/渐变）的高质量修复 | 系统 | 学习型模型依赖 + 权重 | 声明了 4 条学习型路线 | `PROVIDER_NOT_IMPLEMENTED`（本 build 内 `implements=False`） | Run 内 `inpaint` step | — | **未实现（仅注册声明，依赖满足也不可运行）** | `infrastructure/providers/runtime.py:666-686`；`application/translation/inpaint/route_catalog.py:15-19`；`ports/inpaint/ports.py`（`LEARNED_ROUTES`/`NOT_IMPLEMENTED`） | 必须（必须如实显示「不可用」，不能假装可选） |
| CAP-INP-06 | 修复不会改到 mask 之外的像素 | 系统 | 修复进行中 | 写回前校验目标范围 | `NON_TARGET_WRITE`（hard failure） | Run 内 `inpaint` step | — | 已实现 | `ports/providers/errors.py:158-166`；`infrastructure/providers/handlers.py`（`handle_inpaint` 写回校验） | 不建议 |
| CAP-INP-07 | 锁定某个区域的修复结果，禁止重跑覆盖 | 用户 | 区域存在 | `Region.inpaint_locked` / `RegionLockSnapshot.inpaint_locked` → 规划期 `SKIP_LOCK:"inpaint_locked"` | — | **无 wire** | 无 | 部分（字段/DB 列/规划已实现，缺写入命令） | `domain/regions/entities.py:233`, `255-257`；`schema.py:237`；`application/tasks/service.py:532-534`；grep `inpaint_locked` in `core_service.py` = 仅注释/无命令 | 必须 |

---

## 8. 排版渲染（CAP-RENDER）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-RENDER-01 | 手动重渲染某一页（不跑整条流水线） | 用户 | 该页有 clean 底图 + 译文 | `{page_id}` → `{page_id,artifact_id,revision_no,reports[],preview,preview_error}` | `INVALID_REQUEST` / `TARGET_NOT_FOUND` / `INPUT_REVISION_CHANGED`(conflict) / `MISSING_REQUIRED_INPUT`(unavailable) / `ARTIFACT_WRITE_FAILED` | `rerender_page` | `rerender_page` | 已实现 | `core_service.py:2136-2312`, `4257-4334`；`main.rs:906-934`；`region/client.ts:48` | 必须 |
| CAP-RENDER-02 | 只重渲染某个区域 | 用户 | 区域存在 | `RenderService.rerender_region(...)` | 同渲染错误族 | **无 wire** | 无 | 部分（应用层已实现，无命令） | `application/rendering/service.py:292-422` | 必须 |
| CAP-RENDER-03 | 字号自动适配气泡，必要时逐级缩小 | 系统 | 文本 + 区域几何 | 自动字号：起始字号 → `shrink_to_fit` 逐 0.5 递减至 1.0 下限；`font_size_offset` ∈ [-5,5] | `StyleResolutionError`（不支持的 overflow 策略/无法拟合） | — | — | 已实现 | `application/rendering/style.py:20-45`, `109-160`；`domain/regions/entities.py:192-208` | 可选 |
| CAP-RENDER-04 | 手动字号/关闭自动字号 | 用户 | — | `typeset.auto_font_size` (bool)、`typeset.manual_font_size`（可空，[1,500]）；关闭自动字号时手写字号必填 | `INVALID_REQUEST`（交叉字段：`auto_font_size=false` 且无 `manual_font_size` 直接拒绝） | `settings.update_section` | `settings_update_section` | 已实现 | `bootstrap/settings_sections.py:73-87`, `144-159`；`TypesetSettingsPanel.tsx` | 必须 |
| CAP-RENDER-05 | 设置全局排版样式（颜色/描边/行距/对齐/方向/字号偏移） | 用户 | — | `typeset.text_color/stroke_enabled/stroke_color/stroke_width/line_spacing/text_align/text_direction/font_size_offset` | `INVALID_REQUEST`（越域；`text_align=right` 被显式拒绝） | `settings.update_section` | `settings_update_section` | 已实现 | `bootstrap/settings_sections.py:73-87`（`right` 拒绝见 `:79` 注释） | 必须 |
| CAP-RENDER-06 | 选择字体 | 用户 | 字体目录可读 | `FontCatalog.resolve(font_family)` → 可用字体；不可用则替代并标 `font_substituted` | 渲染报告 `font_substituted=true` | `rerender_page`（reports）/ Run 内 `render` step | `rerender_page` | 已实现 | `application/rendering/service.py:118`, `498`；`infrastructure/rendering/font_catalog.py`；`core_service.py:2205-2211`（`font_substituted` 上报） | 必须 |
| CAP-RENDER-07 | 渲染结果的预览缩略 | 用户 | 渲染成功 | 预览发布 → `preview` 资源引用；失败时 `preview_error:"PREVIEW_UNAVAILABLE"`（不影响渲染成功判定） | `PREVIEW_UNAVAILABLE`（非致命） | `rerender_page` | `rerender_page` | 已实现 | `core_service.py:2257-2312`；`infrastructure/resource_channel/render_preview.py` | 必须 |
| CAP-RENDER-08 | 重渲染前提示「输入已变」 | 系统 | 渲染输入 revision 与当前不一致 | `COMPOSITION_BASE_CHANGED` → 线上投影为 `INPUT_REVISION_CHANGED`(conflict) | `INPUT_REVISION_CHANGED` | `rerender_page` | `rerender_page` | 已实现 | `core_service.py:2206-2210`（码映射）, `2214-2226`（category/message） | 必须 |

---

## 9. 区域（Region）编辑与重定类型（CAP-REGION）

> **核心事实**：区域编辑的应用层能力远比线上命令面丰富。线上只有「读列表 / 重定类型 / 版本列表 / 版本恢复 / 页重渲染」5 条；创建、删除、几何、合并、拆分、排序、人工译文保存、译文确认、revision pin、锁切换 **均无 Core 命令**。前端已用 `DisabledFeature` 显式标出这些缺口（`WorkbenchToolbar.tsx:80-84`、`RegionInspector.tsx:133-137`）。

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-REGION-01 | 看到一页上所有区域及其类型/顺序/几何 | 用户 | 页面存在 | `{page_id}` → `{regions:[{region_id,region_type,sfx_policy,origin,revision_no,geometry?}],page_size:{width,height}\|null}`；未知页 = 空 + `null`（不是错误） | `INVALID_REQUEST` / `UNKNOWN` | `list_regions` | `list_regions` | 已实现 | `core_service.py:2055-2085`, `4164-4256`；`main.rs:865-877`；`region/client.ts:41` | 必须 |
| CAP-REGION-02 | 把某区域改判成别的类型（对白/旁白/拟声词/标题/注释/其他） | 用户 | 区域存在 | `{region_id,new_region_type,expected_revision?}` → `{region_id,revision_no,region_type,sfx_policy}`（一次往返） | `INVALID_REQUEST` / `INPUT_REVISION_CHANGED`(conflict) / `TARGET_NOT_FOUND`(not_found) / `UNKNOWN` | `set_region_type` | `set_region_type` | 已实现 | `core_service.py:1980-2054`, `4164-4256`；`main.rs:846-864`；`region/client.ts:44` | 必须 |
| CAP-REGION-03 | 改判类型时 SFX 策略跟着正确重算 | 系统 | 重定类型 | 改判为 `sfx` → 从**当前全局** `sfx.policy` 重快照；改成其它类型 → 强制 `SKIP`；同时产出一个新 revision（`origin=user`,`review_state=unreviewed`） | — | `set_region_type` | `set_region_type` | 已实现 | `core_service.py:59-73`（docstring EV-8 裁定）, `2000-2020` | 可选（透明规则，但 UI 应显示结果） |
| CAP-REGION-04 | 看某区域的历史版本 | 用户 | 区域存在 | `{region_id}` → 版本摘要列表 | `TARGET_NOT_FOUND` | `list_region_revisions` | `list_region_revisions` | 已实现 | `core_service.py:2086-2096`；`main.rs:878-890`；`region/client.ts:46` | 必须 |
| CAP-REGION-05 | 把某区域回退到某个历史版本 | 用户 | 区域存在 + 版本存在 | `{region_id,revision_no,expected_revision}` → `{region_id,revision_no,region_type,sfx_policy}`（回退 = 新建 revision，带 `restored_from` 溯源，不重指历史） | `INVALID_REQUEST` / `TARGET_NOT_FOUND` / `INPUT_REVISION_CHANGED` | `restore_region_revision` | `restore_region_revision` | 已实现 | `core_service.py:2097-2135`；`application/editing/service.py:1-19`, `726-785`；`main.rs:891-905` | 必须 |
| CAP-REGION-06 | 手工新建区域 | 用户 | 页面存在 | `RegionEditingService.create_region(...)`（创建即产生首个 revision） | — | **无 wire** | 无 | 部分（UI 占位 `gap-g10-create-region`） | `application/editing/service.py:262-290`, `1-7`；`WorkbenchToolbar.tsx:80` | 必须 |
| CAP-REGION-07 | 删除区域（软删除） | 用户 | 区域存在 | `delete_region(region_id)`（`deleted_at`） | `RegionNotFound` | **无 wire** | 无 | 部分（UI 占位 `gap-g10-delete-region`） | `application/editing/service.py:298-306`；`domain/regions/entities.py:259-265`；`WorkbenchToolbar.tsx:81` | 必须 |
| CAP-REGION-08 | 拖动/缩放区域几何 | 用户 | 区域存在 | `save_geometry(region_id, geometry)` → 新 revision | `RegionRevisionChanged`（乐观锁） | **无 wire** | 无 | 部分（UI 占位 `gap-g11-region-geometry`） | `application/editing/service.py:468-490`；`WorkbenchToolbar.tsx:82` | 必须 |
| CAP-REGION-09 | 合并两个区域 | 用户 | ≥2 区域 | `merge_regions(...)`（covering bbox + polygon 拼接） | — | **无 wire** | 无 | 部分 | `application/editing/service.py:491-547`；`domain/regions/entities.py:111-114` | 可选 |
| CAP-REGION-10 | 拆分一个区域 | 用户 | 区域存在 | `split_region(...)` | — | **无 wire** | 无 | 部分 | `application/editing/service.py:548-588` | 可选 |
| CAP-REGION-11 | 调整区域内阅读/翻译顺序 | 用户 | 页面有 ≥2 区域 | `reorder_regions(page_id,[region_id...])` → 创建 user revision | — | **无 wire** | 无 | 部分 | `application/editing/service.py:589-609`；`application/editing/service.py:14-17`（reorder 也产生 user revision） | 必须 |
| CAP-REGION-12 | 手工改写译文并保存 | 用户 | 区域有原文 | `save_manual_translation(region_id,edited)` → 自动置 `manual_edited=true` + `translation_locked=true`，状态停 `needs_review` | — | **无 wire** | 无 | 部分（UI 占位 `gap-g9-save-manual-translation`，输入框被禁用） | `application/editing/service.py:697-706`；`domain/regions/entities.py:172-179`；`RegionInspector.tsx:133-135` | 必须 |
| CAP-REGION-13 | 确认译文（校对通过） | 用户 | 有人工译文 | `confirm_final(region_id)` → `edited_confirmed=true`，人工译文成为 final | `ValueError`（无内容可确认） | **无 wire** | 无 | 部分 | `application/editing/service.py:707-725`；`domain/regions/entities.py:180-185` | 必须 |
| CAP-REGION-14 | 锁定某版本不被清理/覆盖 | 用户 | 版本存在 | `set_revision_pinned(region_id,revision_no,pinned)` | — | **无 wire** | 无 | 部分（UI 占位 `gap-g13-revision-pin`） | `application/editing/service.py:786-791`；`schema.py:260`（`is_pinned`）；`RegionInspector.tsx:137` | 必须 |
| CAP-REGION-15 | 锁定区域（禁自动改结构/译文） | 用户 | 区域存在 | `region_locked` / `translation_locked` / `inpaint_locked` 三把锁 | — | **无 wire** | 无 | 部分（UI 占位 `gap-g12-region-lock`） | `domain/regions/entities.py:231-233`, `251-257`；`RegionInspector.tsx:136` | 必须 |
| CAP-REGION-16 | 并发写入不丢我的人工修改 | 系统 | 自动化写入进行中 | `expected_revision` 不匹配 → 零写入并返回 `INPUT_REVISION_CHANGED`；冲突载荷以 `StepResultCandidate` 落库供人工复核 | `INPUT_REVISION_CHANGED` / `LOCK_CHANGED` | `set_region_type`（带 `expected_revision`）/ `restore_region_revision` | 同名 | 已实现 | `core_service.py:59-73`（C4 guard）, `1980-2054`；`application/editing/service.py:10-13`；`application/editing/errors.py` | 必须（冲突提示必须可操作） |

---

## 10. 版本历史与 Run 快照（CAP-REV）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-REV-01 | 区域版本可查可回退 | 用户 | 见 CAP-REGION-04/05 | 同 CAP-REGION-04/05 | 同 | `list_region_revisions` / `restore_region_revision` | 同名 | 已实现 | `core_service.py:2086-2135` | 必须 |
| CAP-REV-02 | 产物（原图/mask/clean/translated）也有版本与 pin | 用户 | 产物存在 | `media_artifacts.current_revision_id` + `artifact_revisions.revision_no` / `is_pinned` / `integrity_status` | — | **无 wire** | 无 | 部分（表结构与写入已实现，无读/写命令） | `schema.py:64-106`；`schema.py:140-146`（current 指针不可清空触发器） | 可选（至少要有「当前用的是哪版」的可见性） |
| CAP-REV-03 | 我的 Run 用哪套设置/Provider 可复现 | 用户 | Run 存在 | `{run_id}` → `{run_id,command,scope,status,targets[],source_run_id?,retry_reason?}`（设置/绑定快照在创建时冻结） | `TARGET_NOT_FOUND` / `INVALID_REQUEST` | `GetRunSnapshot` | `library_get_run_snapshot` | 已实现 | `core_service.py:3328-3351`；`domain/tasks/models.py:389-419`；`schema.py:290-311` | 必须 |
| CAP-REV-04 | 恢复历史版本时溯源清晰 | 系统 | 回退操作 | 回退产生新 revision，`restored_from_revision_id` 指向来源；`origin=restored` | — | `restore_region_revision` | 同名 | 已实现 | `schema.py:251-271`；`domain/regions/entities.py:313-327` | 可选 |

---

## 11. 任务队列 / Run / 暂停继续停止 / 失败重试 / blocked 恢复（CAP-RUN）

> **状态机事实**：Run 状态 9 值、Task 状态 8 值、Step 状态 5 值、Stage 状态 9 值、PlanDecision 5 值（`domain/tasks/models.py:90-147`）。最终状态细节见 `02_DATA_MODEL_AND_STATES.md`。

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-RUN-01 | 对选定范围发起一次翻译/重跑任务 | 用户 | 有可用目标 + 幂等键 | `{command,scope,idempotency_key,overrides?}` → `{run_id,status}`（`command` 必须是 18 个 `PipelineCommand` 之一） | `INVALID_REQUEST` / `TARGET_NOT_FOUND` / `EMPTY_TARGET_SELECTION` / `TARGET_DELETED` / `IDEMPOTENCY_KEY_REUSED`(conflict) / `INVALID_RUN_TRANSITION` | `StartRun` | `library_start_run` | 已实现 | `core_service.py:3274-3301`；`domain/tasks/models.py:66-88`；`workbench/client.ts:3-8`, `219-226` | 必须 |
| CAP-RUN-02 | 18 种任务命令语义 | 用户 | — | 全量翻译 = `ocr→color→term_extract→translate→segment→mask_refine→inpaint→render`；重渲染 = `render`；重修复 = `segment→mask_refine→inpaint`；重 OCR = `ocr`；区域重译 = `translate→render`；区域整链 = 全量 | 同上 | `StartRun` | `library_start_run` | 已实现 | `application/tasks/service.py:80-115`；`domain/tasks/models.py:66-88` | 必须（命令选择器） |
| CAP-RUN-03 | 任务范围可选整本/整章/页面选择/单页/单区域 | 用户 | — | `scope.kind` ∈ `chapter` \| `page_selection` \| `page` \| `region`（`ScopeType` 另有 `book`，但 wire 解析只实现 4 种，见证据） | `INVALID_REQUEST`（非法 scope） | `StartRun` | `library_start_run` | 已实现 | `core_service.py:3131-3173`（`_parse_run_scope`）；`workbench/client.ts:10-14`；`domain/tasks/models.py:53-58`；`application/tasks/service.py:673-677`（区域命令必须 region scope） | 必须 |
| CAP-RUN-04 | 暂停任务 | 用户 | Run 处于 `running` | `{run_id,action:"pause"}` → 置 `pause_requested`；当前不可中断 step 完成后再停 | `INVALID_RUN_TRANSITION`（非 running） | `ControlRun` | `library_control_run` | 已实现 | `core_service.py:3302-3322`；`application/tasks/service.py:1008-1013`, `956-960` | 必须 |
| CAP-RUN-05 | 继续任务 | 用户 | Run 处于 `paused` 或 `interrupted`（未处置） | `{run_id,action:"continue"}` → paused→running；interrupted→重新规划 | `INVALID_RUN_TRANSITION` | `ControlRun` | `library_control_run` | 已实现 | `application/tasks/service.py:1030-1045` | 必须 |
| CAP-RUN-06 | 停止任务（已完成成果不回滚） | 用户 | Run ∈ {pending,running,paused,blocked} | `{run_id,action:"stop"}` → `cancel_requested`；非 running 时立即 `cancelled` | `INVALID_RUN_TRANSITION` | `ControlRun` | `library_control_run` | 已实现 | `application/tasks/service.py:1015-1028`；`01_FUNCTIONAL_ARCHITECTURE.md:202`（文档口径） | 必须 |
| CAP-RUN-07 | 对「被中断」的任务选择重来 | 用户 | Run 处于 `interrupted` 且未处置 | `{run_id,action:"restart",idempotency_key}` → 新建子 Run（`source_run_id`/`retry_reason="restart_after_interruption"`），父 Run 记 `interruption_disposition="restarted"` | `INVALID_REQUEST`（缺幂等键）/ `INVALID_RUN_TRANSITION` / `IDEMPOTENCY_KEY_REUSED` | `ControlRun` | `library_control_run` | 已实现 | `application/tasks/service.py:1047-1079`；`core_service.py:3309-3313` | 必须 |
| CAP-RUN-08 | 放弃被中断的任务 | 用户 | Run 处于 `interrupted` 且未处置 | `{run_id,action:"abandon"}` → `cancelled` + `termination_reason="abandoned_after_interruption"` | `INVALID_RUN_TRANSITION` | `ControlRun` | `library_control_run` | 已实现 | `application/tasks/service.py:1081-1090` | 必须 |
| CAP-RUN-09 | 恢复 blocked 的任务 | 用户 | Run 处于 `blocked` | `{run_id}` → 重新规划（`mode="resume_blocked"`） | `INVALID_RUN_TRANSITION`（非 blocked） | `ResumeBlockedRun` | `library_resume_blocked_run` | 已实现 | `application/tasks/service.py:981-985`；`core_service.py:3323-3327` | 必须 |
| CAP-RUN-10 | 看到总体进度/当前页/当前步骤/各页状态/阻塞原因 | 用户（轮询） | Run 存在 | `{run_id}` → 完整投影：`overall_progress`、`current_page_id`、`current_step_type`、`step_flow[]`、`rows[]`、`tasks[]`（含每 step 的 provider/model/device）、`counts{total,completed,failed,skipped,blocked,waiting,processing}`、`blocked_reasons[]`、`controls{can_pause,can_stop,can_continue,can_restart,can_abandon,can_retry_failed}`、`extra` | `TARGET_NOT_FOUND` | `GetTaskProjection` | `library_get_task_projection` | 已实现 | `core_service.py:3352-3355`, `3174-3255`（含 0.25s 投影缓存）；`workbench/client.ts:18-31` | 必须 |
| CAP-RUN-11 | 少量页失败时整批不算全败 | 系统 | 批量结束 | 有失败但其它完成 → Run = `completed_with_failures`（不是 `failed`） | — | `GetTaskProjection`（`run_status`） | `library_get_task_projection` | 已实现 | `domain/tasks/models.py:96`；`01_FUNCTIONAL_ARCHITECTURE.md:206`（文档口径） | 必须 |
| CAP-RUN-12 | 只重试失败的目标 | 用户 | Run 处于 `completed_with_failures` | `{run_id,idempotency_key}` → 新建子 Run（`retry_reason="retry_failed_targets"`，scope = 失败页集合） | `INVALID_RUN_TRANSITION` / `TARGET_NOT_FOUND`（无失败页）/ `IDEMPOTENCY_KEY_REUSED` | `RetryFailedTargets` | `library_retry_failed_targets` | 已实现 | `application/tasks/service.py:1112-1138`, `1140-1187`；`core_service.py:3356-3365` | 必须 |
| CAP-RUN-13 | 重复点击不会重复建任务 | 系统 | 带幂等键 | 同键同请求 → 返回同一 Run；同键不同请求 → 拒绝 | `IDEMPOTENCY_KEY_REUSED`(conflict) | `StartRun` / `ControlRun(restart)` / `RetryFailedTargets` | 同名 | 已实现 | `application/tasks/service.py:299-320`, `992-1006`；`workbench/client.ts:92-97` | 不建议（透明，但按钮必须防抖） |
| CAP-RUN-14 | 任务进展自动推送 | 系统 | 事件通道 | 6 类事件：`TaskFailed` / `RunPaused` / `RunCompleted` / `CurrentPageStepChanged` / `ExportProgressChanged` / `ReadingProgressChanged`；**事件只是失效提示，必须重新查询** | — | — | 事件映射 | 已实现 | `library_bridge.rs:1129-1136`；`events.ts:5-9`, `53-60`；`core_service.py:1224-1248` | 可选 |
| CAP-RUN-15 | 看到历史任务列表 | 用户 | — | **无命令**：`GetTaskProjection` 只按已知 `run_id` 查询，Core 无 `ListRuns` | — | 无 | 无 | 未实现（UI 明确占位 `gap-g16`/ListRuns） | `TaskProgressPanel.tsx:106-113`；grep `ListRuns`/`list_runs` in `core_service.py` = NONE | 必须（否则刷新后任务不可见） |
| CAP-RUN-16 | 单页/单区域的强制重跑不受「已完成即跳过」影响 | 用户 | 指定命令 | `forced` step 集合让指定步骤无视 `stage_completed`（如 `rerender_*` 强跑 render） | — | `StartRun` | `library_start_run` | 已实现 | `application/tasks/service.py:630-639`, `536-537` | 可选 |
| CAP-RUN-17 | 明白为什么某页被跳过/阻塞 | 用户 | Run 有 skip/blocked | `PlanDecision` 与原因串：`page_or_region_locked` / `translation_locked` / `manual_translation_protected` / `inpaint_locked` / `SFX_SKIP_REASON` / `stage_completed` / `MISSING_REQUIRED_INPUT` / `missing_clean_artifact` / `PROVIDER_UNAVAILABLE` | — | `GetTaskProjection`（`blocked_reasons`、row/step `error_code`） | `library_get_task_projection` | 已实现 | `application/tasks/service.py:503-558`, `149-180`；`core_service.py:3174-3242` | 必须 |

---

## 12. 导出（CAP-EXPORT）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-EXPORT-01 | 导出一张译图 PNG | 用户（原生保存对话框 → 宿主签发 target ref） | 该页有译图产物且未 stale | `{book_id,chapter_ids,ordered_page_ids(1 个),format:"png",format_options:{},stale_policy,target_ref}` → `{export_id,status}` | `INVALID_REQUEST`（png 必须单页）/ `TARGET_NOT_FOUND` / `EXPORT_INPUT_UNAVAILABLE` / `EXPORT_STALE`(conflict) / `EXPORT_WRITE_FAILED` / `REF_*` | `StartExport` | `library_start_export` | 已实现 | `core_service.py:2854-2962`, `2963-2972`；`export/service.py:45-52`；`workbench/client.ts:33` | 必须 |
| CAP-EXPORT-02 | 导出 ZIP（可选压缩级别） | 用户 | 同上 | `format:"zip"`，`format_options:{compression:"standard"\|"fast"\|"store"}` | 同上 | `StartExport` | `library_start_export` | 已实现 | `core_service.py:2967-2970` | 必须 |
| CAP-EXPORT-03 | 导出 CBZ | 用户 | 同上 | `format:"cbz"`，`format_options:{}` | 同上 | `StartExport` | `library_start_export` | 已实现 | `core_service.py:2967-2970`；`export/service.py:50` | 必须 |
| CAP-EXPORT-04 | 导出 PDF（纯图 / 可搜索双层） | 用户 | 同上 | `format:"pdf"`，`format_options:{pdf_content:"image_only"\|"searchable_dual_layer"}` | 同上 + `EXPORT_INPUT_UNAVAILABLE`（PDF 编码器不可用） | `StartExport` | `library_start_export` | 已实现 | `core_service.py:2969`；`export/service.py:109-113`（`PdfUnavailableError`）；`export/pdf_qt.py` | 必须 |
| CAP-EXPORT-05 | 导出文本（txt / json / markdown） | 用户 | 同上 | `format:"text"`，`format_options:{text_representation:"txt"\|"json"\|"markdown"}` | 同上 | `StartExport` | `library_start_export` | 已实现 | `core_service.py:2970`, `3080-3090`；`export/service.py:256` | 必须 |
| CAP-EXPORT-06 | 译文过期时由我决定中止还是照旧导出 | 用户 | 存在 stale 页 | `stale_policy` ∈ `abort` \| `continue_existing`；abort 时返回 `EXPORT_STALE` 并带 `details[]`（每页 `reason:"stale"`） | `EXPORT_STALE`(conflict) | `StartExport` | `library_start_export` | 已实现 | `core_service.py:2901-2903`, `2940-2941`；`export/service.py:63-67` | 必须 |
| CAP-EXPORT-07 | 导出进度/结果/历史可查、可取消 | 用户 | 导出已启动 | `GetExportSnapshot{export_id}` → `{export_id,status,completed_pages,total_pages,current_page_id,completed_at,output:{format,sha256}\|null,error_code}`；`GetExportHistory{}` → `{exports:[...]}`；`CancelExport{export_id}` | `EXPORT_NOT_FOUND` / `INVALID_REQUEST` | `GetExportSnapshot` / `GetExportHistory` / `CancelExport` | `library_get_export_snapshot` / `library_get_export_history` / `library_cancel_export` | 已实现 | `core_service.py:3660-3682`；`workbench/client.ts:44-63`, `271-310`；`schema.py:439-455` | 必须 |
| CAP-EXPORT-08 | 打开导出所在文件夹 | 用户 | 本会话内有该导出 | `{exportId}` → 宿主打开目录（Core 只提供可信历史路径，不下发路径给前端） | `EXPORT_NOT_FOUND` | — | `library_reveal_export_folder` | 已实现 | `main.rs:1285-1310`；`library_bridge.rs:956-965`；`workbench/client.ts:312-315` | 必须 |
| CAP-EXPORT-09 | 不让我把结果写到受保护位置 | 系统 | 导出落点已签发 | 受保护路径 → 拒绝 | `REF_SCOPE_DENIED` | `StartExport` | `library_start_export` | 已实现 | `core_service.py:2938-2939`, `3091-3118`（`_is_protected_export_target`） | 不建议 |
| CAP-EXPORT-10 | 导出历史可「按原设置再导一次」 | 用户 | 历史记录存在 | `ExportService.repeat(export_id, ...)`（复用 scope/format/策略快照） | `EXPORT_NOT_FOUND` / 缺页 | **无 wire** | 无 | 部分（应用层已实现） | `application/export/service.py:398-437` | 可选 |

---

## 13. 术语表与不译表（CAP-CONSTRAINT）

> **关键事实**：这是产品主承诺（`01_FUNCTIONAL_ARCHITECTURE.md:46`, `62-65`, `114-115`；`03_DATA_MODEL.md` §12-§13）中**实现落差最大**的一块。领域规则、候选生命周期、三层作用域合并、进入翻译 payload 的通道都写好了，但**没有持久化表、没有 Core 命令、没有 UI**。

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-CONSTRAINT-01 | 维护术语表（原文→固定译法） | 用户 | 作品/章节上下文 | `TranslationConstraint(constraint_kind=TERMINOLOGY, source_term, target_term, scope_type, scope_id)` | `ValueError`（global 不能带 scope_id / book 或 chapter 必须带；`do_not_translate` 不得带 target_term） | **无 wire** | 无 | **未实现（仅 domain 实体 + 规则）** | `domain/constraints/entities.py:32-61`, `92-120`, `190-198`；`schema.py` 无约束表 | 必须 |
| CAP-CONSTRAINT-02 | 维护不译表（保持原文不翻译） | 用户 | 同上 | `constraint_kind=DO_NOT_TRANSLATE`（`target_term` 必须为空） | 同上 | **无 wire** | 无 | 未实现 | `domain/constraints/entities.py:43-44`, `194-198` | 必须 |
| CAP-CONSTRAINT-03 | 候选生命周期：自动候选先待审、人工优先、拒绝后不再重复提议 | 系统 + 用户 | 有自动抽取 | `ConstraintStatus` ∈ {active,pending,rejected,disabled}；`ConstraintOrigin` ∈ {manual,auto}；被拒条目保留 `normalized_key` 以防重复提议 | — | **无 wire** | 无 | 部分（规则与候选创建已实现） | `domain/constraints/entities.py:47-61`, `23-29`（normalize：NFKC+casefold+折叠空白）；`domain/constraints/candidates.py:19-120` | 必须 |
| CAP-CONSTRAINT-04 | 作用域优先级：章节 > 作品 > 全局 | 系统 | 约束存在 | `merge` 按 `origin` 等级与 `scope` 具体度选胜者，输出 `EffectiveConstraint` 快照供翻译步骤使用 | — | **无 wire** | 无 | 部分（合并与快照纯函数已实现，无数据来源） | `domain/constraints/merge.py:45-75`；`application/translation/context/snapshot.py:27-70`；`application/translation/context/step.py:107-131` | 必须 |
| CAP-CONSTRAINT-05 | 约束变更留历史 | 用户 | 约束存在 | `ConstraintRevision`（不可变，`UNIQUE(constraint_id, revision_no)` 由调用方保证；支持 `is_pinned`/`source_run_id`） | — | **无 wire** | 无 | 未实现（实体在，无存储/无命令） | `domain/constraints/entities.py:72-88` | 可选 |
| CAP-CONSTRAINT-06 | 翻译记忆（TM）：确认过的译文可复用、可停用 | 用户 | TM 条目 | `TranslationMemoryService`：`record_confirmed_translation` / `find_matches`（相似度）/ `set_disabled` / `record_usage` | `UnconfirmedTranslationError` | **无 wire** | 无 | 部分（应用层完整，未装配进 Core） | `application/translation/knowledge/tm.py:37-294` | 可选 |

---

## 14. 设置（CAP-SET）

> 冻结的 section 白名单共 **6 个**（`ocr`/`translate`/`inpaint`/`typeset`/`model_gpu`/`tasks`）+ `sfx` 单值门 + 其余 section 透传。设置页当前 12 个分类（`SettingsPage.tsx:62-73`）。

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-SET-01 | 读取全部设置 | 用户 / 系统 | — | `{}` → `{settings:{...}}`（`PipelineDefaults.settings` 投影） | `INVALID_REQUEST` / `SETTINGS_INVALID_INPUT` | `settings.get` | `settings_get` | 已实现 | `core_service.py:1755-1773`, `3928-3982`；`application/settings/pipeline_defaults.py:28-36` | 必须 |
| CAP-SET-02 | 只读某一分区，并能区分「未设置」与「空」 | 用户 | — | `{section}` → `{settings:{<section>: {...} 或 null}}`（null = 从未写入） | `INVALID_REQUEST` | `settings.get` | `settings_get` | 已实现 | `core_service.py:38-46`（docstring 冻结 None 通道）, `1755-1773` | 必须 |
| CAP-SET-03 | 保存一个分区（整段替换） | 用户 | — | `{section,values}` → 全量投影（一次往返回同步） | `INVALID_REQUEST`（未知 key/非法值/越界 → 写侧 fail-closed，绝不落库） | `settings.update_section` | `settings_update_section` | 已实现 | `core_service.py:1774-1833`；`bootstrap/settings_sections.py:117-141` | 必须 |
| CAP-SET-04 | OCR 分区（语种/方向） | 用户 | — | `ocr.script` / `ocr.direction` | `INVALID_REQUEST` | `settings.update_section` | `settings_update_section` | 已实现 | `bootstrap/settings_sections.py:54-59` | 必须 |
| CAP-SET-05 | 翻译分区（上下文页数/Token 预算） | 用户 | — | `translate.context_pages` [1,5] / `translate.context_token_budget` [200,8000] | `INVALID_REQUEST` | 同上 | 同上 | 已实现 | `bootstrap/settings_sections.py:61-64` | 必须 |
| CAP-SET-06 | 图片修复分区（质量/背景/膨胀/腐蚀） | 用户 | — | `inpaint.preferred_quality` / `background_complexity` / `dilate_radius` [0,10] / `erode_radius` [0,10] | `INVALID_REQUEST` | 同上 | 同上 | 已实现 | `bootstrap/settings_sections.py:66-71` | 必须 |
| CAP-SET-07 | 排版分区（颜色/描边/行距/对齐/方向/自动字号/字号偏移） | 用户 | — | `typeset.*`（9 个 key，含交叉字段校验） | `INVALID_REQUEST` | 同上 | 同上 | 已实现 | `bootstrap/settings_sections.py:73-87`, `144-159` | 必须 |
| CAP-SET-08 | 模型/GPU 分区（设备偏好 / 是否允许 CPU 回退） | 用户 | — | `model_gpu.device_preference` ∈ {auto,cpu,gpu}；`model_gpu.allow_cpu_fallback` (bool) | `INVALID_REQUEST` | 同上 | 同上 | 已实现 | `bootstrap/settings_sections.py:89-94`；`ModelGpuSettingsPanel.tsx:45`（该分区仍有「只解释不可改」的历史注释，需以代码为准） | 必须 |
| CAP-SET-09 | 任务/并发分区（重试次数/退避） | 用户 | — | `tasks.retry_max_attempts` [1,3] / `tasks.retry_backoff_seconds` [0.1,30] | `INVALID_REQUEST` | 同上 | 同上 | 已实现 | `bootstrap/settings_sections.py:96-101` | 必须 |
| CAP-SET-10 | 全局 SFX 策略 | 用户 | — | `settings["sfx"]["policy"]` ∈ {skip,translate,manual}（默认 skip） | `INVALID_REQUEST` | `settings.update_section` | `settings_update_section` | 已实现 | `core_service.py:376-381`（`_SFX_POLICY_VALUES` 取自 domain 枚举）, `1774-1833`；`SfxPolicyControl.tsx` | 必须 |
| CAP-SET-11 | 分层的设置覆盖（任务 > 章节 > 作品 > 全局），且知道值从哪来 | 用户 | 覆盖存在 | `SettingsResolutionService.resolve/resolve_all` → `EffectiveSetting{key,value,source_scope_type,source_scope_id,source_label}`；Core 侧 `settings_resolve_overrides` | `SettingsError`（key 空 / 无任何值） | `settings_resolve_overrides` | `settings_resolve_overrides` | **部分（应用层 + Tauri 命令已实现；前端无调用点）** | `application/settings/models.py:18-23`, `46-60`；`application/settings/resolution.py:22-109`；`src/bootstrap/settings_commands.py:724`（handler）；`main.rs:1892`（注册）；grep 前端 `settings_resolve_overrides` = NONE | 必须 |
| CAP-SET-12 | 未冻结的分区照旧可读写（向后兼容） | 系统 | 未知 section | 未知 section → `validate_settings_section` 返回 `None` → 走历史整段 upsert | — | `settings.update_section` | `settings_update_section` | 已实现 | `bootstrap/settings_sections.py:103-104`, `127-129` | 不建议 |
| CAP-SET-13 | 阅读方向不作为全局设置，而是作品/章节属性 | 用户 | — | 设置页只给指引，不提供全局方向控件 | — | — | — | 已实现（前端策略） | `SettingsPage.tsx:275-294`；`domain/books/entities.py:26-31`, `134-139` | 必须（信息架构约束） |

---

## 15. Provider Profile 与凭据（CAP-PROV）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-PROV-01 | 管理 Provider Profile（含 base_url/model/选项/启停） | 用户 | — | `settings_provider_profiles_list{}` → `{profiles:[...]}`；`create/update/delete` | `SETTINGS_INVALID_INPUT` / `SETTINGS_CONFLICT` / `SETTINGS_UNAVAILABLE` / `SETTINGS_NOT_FOUND` | 4 条 `settings_provider_profiles_*` | 同名 4 条 | 已实现 | `src/bootstrap/settings_commands.py:112-133`；`main.rs:1876-1879`；`settings/client.ts:98-101`；`ProviderProfilePanel.tsx` | 必须 |
| CAP-PROV-02 | 把某个流水线步骤绑定到某个 Provider（可绑/解/查） | 用户 | 步骤名合法 | `settings_provider_bindings_set{step_type,binding}` / `clear` / `resolve`；binding 形状 = provider id 字符串或含 fallback 的映射 | `BindingValidationError` → `SETTINGS_INVALID_INPUT` | 3 条 `settings_provider_bindings_*` | 同名 3 条 | 已实现 | `application/settings/pipeline_defaults.py:62-100`；`settings_commands.py:655-709`；`CapabilityBindingPanel.tsx` | 必须 |
| CAP-PROV-03 | 看某次 Run 实际用了哪套 Provider 快照 | 用户 | Run 存在 | `settings_provider_run_snapshot_get{run_id}` → `RunSnapshot` | `SETTINGS_NOT_FOUND` / `SETTINGS_INVALID_INPUT` | `settings_provider_run_snapshot_get` | `settings_provider_run_snapshot_get` | **部分（Core + Tauri 已实现；前端零调用）** | `settings_commands.py:710-723`；`settings_bridge.rs:1029-1039`；`main.rs:1883`；grep 前端 = NONE | 必须（Run 可复现性） |
| CAP-PROV-04 | 保存/清除 Provider 凭据 | 用户 | — | `BindProfileCredential{profile_id,secret,...}` / `ClearProfileCredential{profile_id}`；凭据进平台凭据库，设置面永不含明文 | `MISSING_CREDENTIAL`（引用不存在）/ `PROVIDER_AUTH_FAILED` | `BindProfileCredential` / `ClearProfileCredential` | `credential_put` / `credential_clear` | 已实现 | `settings_commands.py:327-380`；`settings_bridge.rs:288`, `335`；`ports/providers/credentials.py:20-22`, `40-80`；`CredentialField.tsx` | 必须 |
| CAP-PROV-05 | 知道哪些 Provider 现在真的可用（为什么不可用） | 用户 | — | `ProviderRegistry.status(provider_id)` → `ProviderStatus{state,detail,...}`；就绪探测不导入重依赖 | — | **无 wire**（`settings_provider_profiles_list` 只回配置，不回 readiness） | 无 | 部分（应用层/基础设施已实现，无读面命令） | `infrastructure/providers/registry.py:178-260`；`infrastructure/providers/dependencies.py`（`Requirement`/probe）；`capabilities` 5 类见 `ports/providers/profiles.py:29-40` | 必须 |
| CAP-PROV-06 | 缺席的重依赖不拖垮程序（Not-Ready 而非崩溃） | 系统 | — | 依赖/权重缺失 → `PROVIDER_DEPENDENCY_MISSING`，程序继续运行 | `PROVIDER_DEPENDENCY_MISSING` / `MODEL_INCOMPLETE` / `MODEL_LOAD_FAILED` | — | — | 已实现 | `ports/providers/errors.py:65-96`, `185-195`；`infrastructure/providers/runtime.py:1-21` | 必须（必须显示为「不可用」而不是「坏掉」） |

---

## 16. 网络代理 Profile（CAP-NET）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-NET-01 | 管理网络代理 Profile | 用户 | — | `settings_network_profiles_{list,create,update,delete}`；`mode` ∈ `direct`/`system`/`http`/`https`/`socks5` | `SETTINGS_INVALID_INPUT` / `SETTINGS_CONFLICT` / `SETTINGS_NOT_FOUND` | 4 条 | 同名 4 条 | 已实现 | `ports/network/profiles.py:22-26`；`settings_commands.py:139-260`；`settings_bridge.rs:1042-1112`；`NetworkProfilePanel.tsx` | 必须 |
| CAP-NET-02 | 指定/清除默认代理 | 用户 | profile 存在 | `settings_network_profile_default_set{profile_id}` / `_clear` | `SETTINGS_NOT_FOUND` | 2 条 | 同名 2 条 | 已实现 | `settings_commands.py`（`_network_profile_default_set/clear`）；`main.rs:1889-1890` | 必须 |
| CAP-NET-03 | 查询某个 Provider/步骤实际会走哪条网络路线 | 用户 | — | `settings_network_profile_resolve` → 解析结果（含 stage/reason，如 `Proxy/system_route_is_direct`、`ProviderAuth/provider_auth_not_required`） | `SETTINGS_INVALID_INPUT` | `settings_network_profile_resolve` | 同名 | 已实现 | `settings_commands.py:99-103`, `_network_profile_resolve`；`main.rs:1891` | 必须 |
| CAP-NET-04 | 测试代理连通性 | 用户 | profile 存在 | `settings_network_profiles_test{...}` → 连接测试结果 | 测试失败以结果字段表达，非命令失败 | `settings_network_profiles_test` | 同名 | 已实现 | `settings_commands.py:130`；`infrastructure/network/profile_test.py`；`settings_bridge.rs:1113-1125` | 必须 |
| CAP-NET-05 | 每个 Provider 可覆盖代理策略（继承/用自己/强制直连） | 用户 | — | `ProxyPolicy` ∈ {inherit, profile, direct} | `SETTINGS_INVALID_INPUT` | Provider Profile 的 option | 同 Provider 命令 | 已实现 | `ports/providers/profiles.py:19-27`；`infrastructure/providers/runtime.py`（`_network_gate`） | 必须 |
| CAP-NET-06 | 本地服务默认直连、TLS 校验可关闭但需二次确认 | 用户 | — | `verify_tls` / `confirm_disable_tls_verification` / `allow_proxy_failure_direct_fallback` 参数 | `SETTINGS_INVALID_INPUT`（未确认就关 TLS） | `settings_network_profiles_create/update` | 同名 | 已实现 | `settings_bridge.rs:1049-1057`；`ports/network/profiles.py:29-30`（默认 bypass `localhost/127.0.0.1/::1`） | 可选 |

---

## 17. 缓存与 Revision 清理（CAP-CACHE）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-CACHE-01 | 先看清要清理什么、占多少空间 | 用户 | — | `{}` → `{targets:[{relative_path,size_bytes}],total_bytes,pending_cleanups}`（只列 `cache/` 前缀） | `INVALID_REQUEST` / `CORE_UNAVAILABLE`(可重试) / `UNKNOWN` | `cleanup.preview` | `cleanup_preview` | 已实现 | `core_service.py:88-97`, `1846-1858`；`application/maintenance/cleanup.py:41`, `127-132` | 必须 |
| CAP-CACHE-02 | 执行清理（幂等，不碰用户数据与 revision） | 用户 | — | `{}` → `{items:{rel:{status,reason}},removed,failed,skipped}`；只能删 `cache/` 前缀 | 同上；失败项写入共享 trash manifest 的 `pending_cleanups` | `cleanup.run` | `cleanup_run` | 已实现 | `core_service.py:98-105`, `1859-1864`；`cleanup.py:41`, `133-159` | 必须 |
| CAP-CACHE-03 | 重试上次没删掉的缓存 | 用户 | 有 pending | `{}` → 同 `cleanup.run` 投影；settled 项出账，再失败仍 pending | 同上（pending 未写过 = 空重试，不是错误） | `cleanup.retry_pending` | `cleanup_retry_pending` | 已实现 | `core_service.py:106-110`, `1865-1874`；`cleanup.py:160-192`；`CacheRevisionPanel.tsx` | 必须 |
| CAP-CACHE-04 | Revision 保留策略 / 按天数自动清理 | 用户 | — | **未开放**：无调度器与存储消费点 | — | 无 | 无 | 未实现（UI 明确只读说明） | `CacheRevisionPanel.tsx:171`；`01_FUNCTIONAL_ARCHITECTURE.md` 未定义保留策略 | 可选（若不做，不要提供控件） |
| CAP-CACHE-05 | 缓存清理绝不触及原始文件/业务行/current 或 pinned revision | 系统 | — | 只把 `cache/` 前缀相对路径交给受控删除器 | — | `cleanup.*` | `cleanup_*` | 已实现 | `core_service.py:103-105`；`cleanup.py:193-199`（`_safe_targets`） | 不建议 |

---

## 18. 备份 .nmbak（CAP-BACKUP）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-BACKUP-01 | 手动创建一份完整备份 | 用户 | 数据根可写 | `{}` 或 `{backup_type:"manual"}` → `{backup_id,path,size_bytes,created_at,verified}`；zip 原子写入 + 回读校验后才 `verified=true` | `INVALID_REQUEST`（非 manual）/ `BACKUP_CREATE_FAILED` | `backup.create` | `backup_create` | 已实现 | `core_service.py:1883-1895`；`infrastructure/sqlite/nmbak.py:1-28`, `127-208` | 必须 |
| CAP-BACKUP-02 | 看现有备份列表 | 用户 | — | `{}` → `[{backup_id,backup_type,created_at,size_bytes,schema_version,verified}]`；manifest 不可读的仍列出（`verified=false`） | `UNKNOWN` | `backup.list` | `backup_list` | 已实现 | `core_service.py:1896-1898`；`nmbak.py:16-18`, `95-126` | 必须 |
| CAP-BACKUP-03 | 从备份恢复（必须二次确认，且先留回滚点） | 用户 | 无活跃 Run | `{backup_id,confirm_restore:true}` → `{restored_from,pre_restore_backup_id,schema_versions,managed_consistency}` | `BACKUP_RESTORE_REQUIRES_CONFIRMATION` / `BACKUP_NOT_FOUND` / `BACKUP_CORRUPT` / `BACKUP_RESTORE_BUSY`(可重试) / `BACKUP_RESTORE_INCOMPLETE` | `backup.restore` | `backup_restore` | 已实现 | `core_service.py:1899-1909`；`nmbak.py:19-23`, `209-269`；`BackupSettingsPanel.tsx` | 必须 |
| CAP-BACKUP-04 | 删除某份备份 | 用户 | 备份存在 | `{backup_id}` → `{removed:true}` | `BACKUP_NOT_FOUND` / `BACKUP_DELETE_FAILED` | `backup.delete` | `backup_delete` | 已实现 | `core_service.py:1910-1921`；`nmbak.py:270-282` | 必须 |
| CAP-BACKUP-05 | 备份包含 Managed Copy，而不只是数据库 | 系统 | 创建备份 | 包内含 `manifest.json` + `library.db` + sidecar + `managed/**`（当前/pinned revision 引用的文件） | `BACKUP_CORRUPT` | `backup.create` | `backup_create` | 已实现 | `nmbak.py:3-11`, `319-387`（`_revision_refs` / `_copy_managed_files`） | 不建议 |
| CAP-BACKUP-06 | 自动备份（定时/启动/迁移前） | 用户 | — | `backup_type` 枚举含 `automatic`/`pre_migration`/`pre_restore`，但**只有 `pre_migration`（迁移器内部）与 `pre_restore`（恢复时强制）会真正产生**；`automatic` 无调度器 | `INVALID_REQUEST`（面板只能 `manual`） | `backup.create` 只接受 `manual` | `backup_create` | 部分（自动备份未开放） | `core_service.py:1883-1895`（只 manual）；`nmbak.py:56`（4 类枚举）；`migrator.py:86-93`；`BackupSettingsPanel.tsx:391` | 可选（如实说明「无自动备份」） |

---

## 19. 回收站（CAP-TRASH）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-TRASH-01 | 删除作品先是「进回收站」，不是真删 | 用户 | 作品存在 | 软删除：`deleted_at` 置位；文件与业务行保留 | — | **无 wire**（作品软删除本身无命令；`LibraryService.delete_book` 存在但无命令） | 无 | 部分 | `application/library/service.py:97-101`；`domain/books/entities.py:96-102`；`schema.py:35-41`（`deleted_at`） | 必须 |
| CAP-TRASH-02 | 回收站里看得见、能彻底删、删不干净能重试 | 用户 | 有软删除作品 | 见 CAP-LIB-06/07/08；清理不完整 → `BOOK_DELETE_CLEANUP_PENDING`(可重试) | 见 CAP-LIB-06 | `ListRecycleBinBooks` / `PermanentlyDeleteBook(s)` | 同名 Tauri | 已实现 | 同 CAP-LIB-06/07/08；`RecycleBinPage.tsx`；`PermanentDeleteConfirmDialog.tsx` | 必须 |
| CAP-TRASH-03 | 页面级删除与批量恢复（批次化） | 用户 | 页面存在 | `TrashService`：`soft_delete_pages` → `list_batches` → `restore_batch` / `purge_batch` / `retry_pending_purges` / `pending_purge_count` | 见 `trash.py` 实现 | **无 wire** | 无 | 部分（服务已装配进 Core，无命令） | `application/maintenance/trash.py:103-256`；`core_assembly.py:964-970` | 可选 |
| CAP-TRASH-04 | 回收站自动清理（按天数） | 用户 | — | **未开放**：无调度器消费自动清理天数 | — | 无 | 无 | 未实现（UI 明确只读说明） | `RecycleBinSettingsPanel.tsx:309` | 可选（不做就不要控件） |

---

## 20. 插件与 Hooks（CAP-PLUGIN）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-PLUGIN-01 | 看到本机装了哪些插件 | 用户 | 插件目录存在 | `{}` → `{plugins:[{id,name,version,hooks[],enabled,...}],global_enabled}` | `PLUGIN_INVALID_REQUEST` / `PLUGIN_OPERATION_FAILED` | `plugins.list` | `plugins_list` | 已实现 | `core_service.py:1930-1932`；`infrastructure/plugins/service.py:158-204`；`PluginSettingsPanel.tsx` | 必须 |
| CAP-PLUGIN-02 | 一键停用所有插件 | 用户 | — | `plugins.set_enabled{enabled:bool}` → 新状态 | `PLUGIN_INVALID_REQUEST` | `plugins.set_enabled` | `plugins_set_enabled` | 已实现 | `core_service.py:1933-1938`；`service.py:205-213` | 必须 |
| CAP-PLUGIN-03 | 单独启停某个插件 | 用户 | 插件存在 | `plugins.set_plugin_enabled{plugin_id,enabled}` | `PLUGIN_NOT_FOUND` / `PLUGIN_NOT_LOADED` | `plugins.set_plugin_enabled` | `plugins_set_plugin_enabled` | 已实现 | `core_service.py:1939-1948`；`service.py:214-230` | 必须 |
| CAP-PLUGIN-04 | 审计：谁在什么时候跑了什么 Hook、出了什么错 | 用户 | — | `plugins.audit_list{limit?}` → 事件列表（含 `hook_name`/`detail_json`，不含 payload 与绝对路径） | `PLUGIN_INVALID_REQUEST` | `plugins.audit_list` | `plugins_audit_list` | 已实现 | `core_service.py:1949-1958`；`service.py:231-257`；`schema.py:581-593`（`plugin_events`） | 必须 |
| CAP-PLUGIN-05 | 打开插件目录放插件 | 用户 | — | Tauri 本地动作（无 Core 命令） | — | — | `plugins_open_directory` | 已实现 | `main.rs:811-845`；`settings/client.ts:141` | 必须 |
| CAP-PLUGIN-06 | 6 个冻结 Hook 在流水线/导出前后可介入 | 系统 | 插件启用且声明该 hook | `HOOK_NAMES` = `before_detect`/`after_detect`/`before_ocr`/`after_ocr`/`before_export`/`after_export`；`before_*` 可返回覆盖对象，`after_*` 只读 | `PLUGIN_HOOK_UNKNOWN` / `PLUGIN_HOOK_TIMEOUT`(可重试) / `PLUGIN_HOOK_FAILED`(可重试) / `PLUGIN_HOOK_UNAVAILABLE` | **无专门命令**（Core 内部调用） | 无 | 已实现 | `infrastructure/plugins/manifest.py:42-49`, `66-70`；`service.py:260-345`；`core_service.py:286-297`（错误映射） | 可选 |
| CAP-PLUGIN-07 | 插件权限边界（第一版只允许 network） | 系统 | manifest 声明 | `ALLOWED_PERMISSIONS` 4 个，`SUPPORTED_PERMISSIONS` 只有 `("network",)`；`permissions:[]` = 不授予任何能力句柄；hook 子进程 `python -I` + 10s 超时 + 256 KiB 输出上限 | `PLUGIN_INVALID_REQUEST`（越权声明） | 装配/加载期 | — | 已实现 | `infrastructure/plugins/manifest.py:8-16`, `52-63`；`service.py:55-64`, `346-380` | 必须（必须如实说明「不是 OS 级沙箱」） |
| CAP-PLUGIN-08 | 插件系统未实现时的诚实降级 | 用户 | — | UI 明确「插件系统尚未实现」而非渲染假控件 | — | — | — | 已实现（但文案与代码现状已不一致，见 `05_GAP_LIST.md` A-03） | `SettingsPage.tsx:85-89`；`PluginSettingsPanel.tsx`（实际已接 5 条命令） | 必须 |

---

## 21. 资源通道 issue_resource_url / revoke（CAP-RES）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-RES-01 | 把受管图片安全地交给界面显示（不让前端拿到路径） | 系统 | Core 目录已登记该资源 | `resolve_page_resource` 产出的目录键 → 宿主签发 URL（`http://m2res.localhost/m2id/<43 字符 id>`） | `REF_*` 全族（`REF_UNKNOWN_ID`/`REF_REVOKED`/`REF_EXPIRED`/`REF_OUT_OF_SCOPE`/`REF_REPARSE_POINT`/`REF_SCOPE_DENIED`/`RESOURCE_TOO_LARGE`/`RESOURCE_LIMIT_EXCEEDED`/`FILE_IDENTITY_CHANGED`/`CONTENT_DIGEST_MISMATCH`/`OPEN_FAILED_*`） | （Core 目录侧） | `issue_resource_url` | 已实现 | `resource_protocol.rs:1-42`, `100-112`；`application/resource_channel/dto.py:77-94`；`main.rs:1372-1384` | 必须（技术必要） |
| CAP-RES-02 | 用完就撤销某个资源引用 | 系统 / 用户关闭视图 | 引用存在 | `{opaque_id}` → 撤销（之后访问 = `REF_REVOKED`/410） | `REF_MALFORMED` | `revoke_ref` | `revoke_ref` | 已实现 | `main.rs:1385-1389`；`resourceChannel/client.ts:69` | 不建议 |
| CAP-RES-03 | 批量撤销（视图整体关闭） | 系统 | 多个引用 | `revoke_resource_refs{ids[]}` | `REF_MALFORMED` | **无 Core 命令**（Tauri 本地批量） | `revoke_resource_refs` | 部分（Tauri 已实现；前端零调用） | `main.rs:1390-1401`；grep 前端 `revoke_resource_refs` = NONE | 不建议 |
| CAP-RES-04 | 大图能传输（不塞进普通 JSON/Base64） | 系统 | — | 单资源上限 **256 MiB**；每次请求分块 **≤16 MiB**（`?chunk=<n>`）；超限 → `RESOURCE_TOO_LARGE` | `RESOURCE_TOO_LARGE` / `RESOURCE_LIMIT_EXCEEDED` | — | 资源协议 | 已实现 | `resource_protocol.rs:40-41`；`application/resource_channel/dto.py:18`, `22`, `26` | 必须（决定大图/长条 Webtoon 的呈现策略） |
| CAP-RES-05 | 引用有过期时间且可被滑动续期 | 系统 | — | 默认 TTL **300s** 滑动续期；调用方只能**缩短**不能延长；活跃引用上限 **32**，单资源订阅上限 **16** | `REF_EXPIRED` / `RESOURCE_LIMIT_EXCEEDED` | — | 资源协议 | 已实现 | `application/resource_channel/service.py:81-178`；`dto.py:29`；`resource_protocol.rs:23-26` | 不建议（但多图并发的上限会实际影响体验） |
| CAP-RES-06 | 只能访问受控作用域（派生只读 / 受管只读），用户源文件永不可被前端读取 | 系统 | — | `scope_class` ∈ `derived-read-only` \| `managed-read-only`；`user-source` 明确不可服务 | `REF_SCOPE_DENIED` | — | 资源协议 | 已实现 | `resource_protocol.rs:56-62`；`dto.py:66-74` | 不建议 |

---

## 22. 维护 / 诊断 / 部署（CAP-MAINT）

| ID | 用户目标 | 触发者 | 前置条件 | 输入 → 成功结果 | 失败 / 错误码 | Core 命令 | Tauri 命令 | 状态 | 证据 | 新 UI 必须暴露 |
|---|---|---|---|---|---|---|---|---|---|---|
| CAP-MAINT-01 | 一键导出诊断包给支持人员 | 用户 | — | `DiagnosticsService.export(generated_at=...)` → 写诊断报告并返回路径；含敏感信息脱敏（密钥/Bearer/sk-） | — | **无 wire** | 无 | 部分（服务已装配进 Core，无命令；旧 Qt 入口 `app.py:54` 用过） | `application/maintenance/diagnostics.py:24-60`, `92-260`；`core_assembly.py:674`, `1301-1316`；`core_service.py` grep `diagnostic` = NONE | 可选 |
| CAP-MAINT-02 | 最近的错误有界留存，供诊断 | 系统 | — | `BoundedErrorLog`（默认 50 条） | — | — | — | 已实现（内部） | `application/maintenance/diagnostics.py:202-224`；`infrastructure/filesystem/bounded_log_store.py` | 不建议 |
| CAP-MAINT-03 | 模型/权重安装状态可查（含 hash/size 校验） | 用户 | — | `ModelManager` / `ModelSpec{weights_path,sha256,size_bytes,source_url,requires_gpu}`；校验失败 → `MODEL_INCOMPLETE` | `MODEL_INCOMPLETE` / `MODEL_LOAD_FAILED` | **无 wire** | 无 | 部分（基础设施已实现，无命令） | `infrastructure/providers/models.py`；`infrastructure/providers/runtime.py:19-20`；`ports/providers/errors.py:185-195` | 可选 |
| CAP-MAINT-04 | 数据库版本比程序新时拒绝启动而不是写坏数据 | 系统 | — | `SchemaTooNewError`，不改库 | `SchemaTooNewError` | 装配期 | — | 已实现 | `migrator.py:69-80`；`doc/08_ACCEPTANCE_CRITERIA.md` 的 AC-DB-005 口径（注释引用） | 不建议（但必须给用户可读提示） |
| CAP-MAINT-05 | 旧版 JSON 数据能被读入（一次迁移） | 系统 | 存在 legacy JSON | 装配期 legacy JSON import（头部注释声明） | — | 装配期（无命令） | — | UNVERIFIED（见证据列） | `core_assembly.py:6-17` 的模块注释声明该步骤存在；本次盘点未逐行确认其输入/幂等/失败语义 | 不建议 |

---

## 23. 统计与结论

### 23.1 计数（按 §1-§22 表格逐行统计）

| 项 | 数量 |
|---|---|
| 能力条目总数 | **193** |
| 状态 = 已实现 | 141 |
| 状态 = 部分（应用层/domain 有，但线上命令或 UI 缺一段） | 40 |
| 状态 = 未实现 | 10 |
| 状态 = UNVERIFIED（CAP-OCR-06, CAP-MAINT-05） | 2 |
| 其中性质为「仅测试/探针通道」的产品外命令 | 1（`core.detect`，CAP-DET-01；其 docstring 自述 "Verification/tooling surface only"） |
| 新 UI 必须暴露 | 139 |
| 新 UI 可选 | 36 |
| 新 UI 不建议暴露 | 18 |

> 「必须暴露」不等于「必须首屏可见」，只表达**能力不能丢**。18 条「不建议」全部是内部/安全/协议级机制（协议协商、调度器租约、启动 GC、路径保护、身份校验等），暴露反而会成为设计负担。

### 23.2 三条不可让步的能力面结论

1. **Run 是唯一的重活入口**。检测/OCR/翻译/修复/渲染都不是独立命令，只有 `CommandType` + `scope`（`application/tasks/service.py:80-115`）。新 UI 的任务模型必须围绕「Run + Task 投影 + 控制动作」设计，而不是围绕「按钮各调一个 API」。
2. **保护性能力比生产能力更容易被设计漏掉**。四把锁（page/region/translation/inpaint）、区域 `origin`/`review_state`、`current vs pinned revision`、`expected_revision` 乐观锁，全部是「不许覆盖用户劳动」的机制；它们在当前线上命令面只露出一小部分（锁与 pin 甚至没有写命令），但设计上必须预留位置。注意：**页面级** `review_state`/`overall_status` 是另一回事——那两列没有任何推进代码（见 §7 CAP-PAGE-09）。
3. **术语表/不译表、页面级回收站、诊断导出、历史任务列表** 这四类在文档里像既有能力，实际是缺口（详见 `05_GAP_LIST.md`）。新 UI 不能把它们画成可用控件。

### 23.3 本次盘点的边界

- 未逐行审计 Legacy PySide6/QML 侧（`src/ui/**`, `src/bootstrap/app.py`）：按 `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 与 `AGENTS.md`，该侧只作历史证据，不计入新架构能力面。
- 未跑任何构建/测试；本文件不声称任何测试通过。
- `settings_provider_*` 的 19 条 P15 命令逐条参数形状以 `src/bootstrap/settings_commands.py` 的 handler 为准，本文件只列族与关键语义。
