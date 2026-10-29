# V11R 命令契约 V1（C001–C066 基线 + C067–C076 增量 PENDING）

状态：`ISSUED`（2026-10-30，DSH 委派 `core-bridge` 起草；独立 Reviewer 待指派）。
基线：`c73239999`（审计快照 `clean-snapshot-20261029@22de860` 的 66 条 Host 命令静态清册）。
上游：`doc/plan/V11R_AVALONIA_CONTRACT.md`（FROZEN）、审计附件
`G:/CODEX/New Manga.workspace/tasks/AUDIT-V11-INTAKE-1/命令清册_C001-C066.csv`。
生成器：`verification/V11R-A-3/tools/extract_contract_facts.py` +
`verification/V11R-A-3/tools/build_contract_doc.py`（行号/样例可机械复现；改契约后重新生成）。

> 本契约**不是** OpenAPI：它签发的是"当前真实注册表 + Dispatcher + Core 源码 + 真实样例"三者一致的
> 可验证边界。`FROZEN` 只表示该行的路由/通道/minor/入参校验/成功结果外形/至少一个真实样例已核实；
> 它**不**表示每条错误分支都已运行验证（逐条见 §6 缺口）。`PARTIAL` 明确写出缺口，`GAP` 表示不可核实。
> **禁止**把 Dispatcher 透传当作"已冻结 schema"——透传行一律按 §6 标注。

## 1. 使用方式与状态语义

| 状态 | 含义 | 可依赖的内容 |
|---|---|---|
| `FROZEN` | 注册表绑定 + Dispatcher 参数约束（或 Core 严格 key 集校验）+ Core 源码行 + 至少一个真实请求/响应样例（或等价测试断言）全部可核实 | 路由、通道、protocol minor、入参键集、成功结果外形、已定位错误码族 |
| `PARTIAL` | 上述证据链有一项缺失（典型：Dispatcher 透传未约束入参；Host-local 无自动化样例；结果未在 C# 类型化） | 仅可依赖已写明的部分；缺口列在 §6 |
| `GAP` | 无注册绑定或无法核实 | 不得据此实现 UI |
| `PENDING(...)` | 尚未合入的增量命令（C067–C076，来自 V11R-F0-1） | **不得**当作已冻结契约使用 |

权威顺序：**Core 源码 / 真实 wire 样例 > `HostCommandRegistry` > `HostCommandDispatcher` > 审计静态清册**。
审计附件是线索，不是事实来源；本契约每条都以仓库源码行号与证据文件锚定。

## 2. 共享信封与协议

应用通道（`core_service`，JSON-lines）：

```json
{"protocol":"new-manga.core","version":{"major":2,"minor":<N>},"request_id":"...","command":"<route>","payload":{...}}
```

响应：`{"protocol","version","request_id","result":<object|array|null>,"error":<null|{code,category,message,retryable,details?}>}`。
异步事件帧混在 stdout（`event_type`/`event_id`，无 `request_id`），客户端必须过滤（`CoreProtocol.IsEventFrame`）。

| minor | 用途 | 约束 |
|---:|---|---|
| 3 | 默认应用命令（读、settings 基础、cleanup/backup/plugin、Region/Reader、Run/Export） | 请求 `minor` 必须等于 3（`_P15_SETTINGS_COMMANDS`/`_RUN_COMMANDS` 之外按 3 校验） |
| 7 | P15 settings / provider / network / credential 面（C015–C031） | Core 拒绝 minor≠7（`core_service.py:3706-3711`） |
| 8 | `CreateBook` / `CreateChapter`（C036/C037） | Core 拒绝 minor≠8（`core_service.py:240,3504-3518`） |
| 10 | `PermanentlyDeleteBook(s)`（C040/C041） | Core 拒绝 minor≠10（`core_service.py:241,3561-3575`） |

Host-local 与 HostBridge 命令没有 Core minor（表中记 `—`）。

## 3. 命令总表（按域）

共 66 条：Settings 33 / Library 8 / Region 6 / Reader 4 / Resource 3 / Workbench 12。
统计：**FROZEN 49 条 · PARTIAL 17 条 · GAP 0 条**。

## 4. 逐条清册

### 4.1 Settings（33 条）

| ID | 前端命令 | 路由目标 | 通道 | minor | 入参（校验/实测） | 结果外形（实测/类型） | 错误码族 | UI 消费者 | 状态 | 源码引用 · 样例 |
|---|---|---|---|:--:|---|---|---|---|---|---|
| C001 | `settings_get` | `settings.get` | core | 3 | 透传（Core 校验；实测空 payload） | `{settings}` | §5.1 | — | **PARTIAL** | registry:127 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:1754（handle_settings_get）；core_service.py:3927-3960（settings 分支） · 样例参考: `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C002 | `settings_update_section` | `settings.update_section` | core | 3 | `section!: string` `values!: object` | `{settings}` | §5.1 | — | **FROZEN** | registry:135 · HostCommandDispatcher.cs:175 · src/bootstrap/core_service.py:1773（handle_settings_update_section）；core_service.py:3927-3960（settings 分支） · 样例(wire): `verification/NS-WIRE-A1/probe-results.json` |
| C003 | `cleanup_preview` | `cleanup.preview` | core | 3 | 透传（Core 校验；实测空 payload） | `{pending_cleanups, targets, total_bytes}` | §5.1 | — | **PARTIAL** | registry:130 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:1845（handle_cleanup_preview） · 样例参考: `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C004 | `cleanup_run` | `cleanup.run` | core | 3 | `{}`（无参数；Dispatcher 丢弃输入） | `{failed, items, removed, skipped}` | §5.1 | — | **FROZEN** | registry:141 · HostCommandDispatcher.cs:182 · src/bootstrap/core_service.py:1858（handle_cleanup_run） · 样例(wire): `verification/NS-WIRE-A1/probe-results.json` |
| C005 | `cleanup_retry_pending` | `cleanup.retry_pending` | core | 3 | `{}`（无参数；Dispatcher 丢弃输入） | `{failed, items, removed, skipped}` | §5.1 | — | **FROZEN** | registry:161 · HostCommandDispatcher.cs:259 · src/bootstrap/core_service.py:1864（handle_cleanup_retry_pending） · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C006 | `backup_create` | `backup.create` | core | 3 | `backup_type?: string` | `{backup_id, created_at, path, size_bytes, verified}` | §5.1 | — | **FROZEN** | registry:139 · HostCommandDispatcher.cs:192 · src/bootstrap/core_service.py:1882（handle_backup_create） · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C007 | `backup_list` | `backup.list` | core | 3 | 透传（Core 校验；实测空 payload） | `[array]` | §5.1 | — | **PARTIAL** | registry:128 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:1895（handle_backup_list） · 样例参考: `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C008 | `backup_restore` | `backup.restore` | core | 3 | `backup_id!: string` `confirm_restore!: bool` | 错误样例：`error.code=BACKUP_RESTORE_REQUIRES_CONFIRMATION`（成功外形见 Core handler） | §5.1 | — | **PARTIAL** | registry:189 · HostCommandDispatcher.cs:255 · src/bootstrap/core_service.py:1898（handle_backup_restore） · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C009 | `backup_delete` | `backup.delete` | core | 3 | `backup_id!: string` | `{removed}` | §5.1 | — | **FROZEN** | registry:160 · HostCommandDispatcher.cs:249 · src/bootstrap/core_service.py:1909（handle_backup_delete） · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C010 | `plugins_list` | `plugins.list` | core | 3 | 透传（Core 校验；实测空 payload） | `{global_enabled, plugins}` | §5.1 | — | **PARTIAL** | registry:129 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:1929（handle_plugins_list） · 样例参考: `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C011 | `plugins_set_enabled` | `plugins.set_enabled` | core | 3 | `enabled!: bool` | `{global_enabled}` | §5.1 | — | **FROZEN** | registry:140 · HostCommandDispatcher.cs:195 · src/bootstrap/core_service.py:1932（handle_plugins_set_enabled） · 样例(wire): `verification/NS-WIRE-A1/probe-results.json` |
| C012 | `plugins_set_plugin_enabled` | `plugins.set_plugin_enabled` | core | 3 | `plugin_id!: string` `enabled!: bool` | 错误样例：`error.code=PLUGIN_NOT_FOUND`（成功外形见 Core handler） | §5.1 | — | **PARTIAL** | registry:163 · HostCommandDispatcher.cs:266 · src/bootstrap/core_service.py:1938（handle_plugins_set_plugin_enabled） · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C013 | `plugins_audit_list` | `plugins.audit_list` | core | 3 | `limit?: int` | `[array]` | §5.1 | — | **FROZEN** | registry:162 · HostCommandDispatcher.cs:263 · src/bootstrap/core_service.py:1948（handle_plugins_audit_list） · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C014 | `plugins_open_directory` | — | host-local | — | 见 Host 实现（Host-local 参数校验） | `HostCommandResult`（shell 动作成功/typed 拒绝；HostGrantCoordinator.cs:343） | §5.8 | — | **PARTIAL** | registry:40 · HostCommandDispatcher.cs:417（default 透传） · —（无 Core 路由） · 样例：缺 |
| C015 | `settings_provider_profiles_list` | `settings_provider_profiles_list` | core | 7 | 透传（Core 校验） | `{profiles}` | §5.2 | UI | **FROZEN** | registry:136 · HostCommandDispatcher.cs:180 · src/bootstrap/core_service.py:316 · 样例(wire): `verification/NS-WIRE-A1/probe-results.json` |
| C016 | `settings_provider_profiles_create` | `settings_provider_profiles_create` | core | 7 | `provider_id!: string` `display_name!: string` `endpoint!: string` `model!: string` `enabled!: bool` `capabilities!: string[]` `network_profile_id?: nullable-string` | 错误样例：`error.code=INVALID_REQUEST`（成功外形见 Core handler） | §5.2 | UI | **PARTIAL** | registry:190 · HostCommandDispatcher.cs:337 · src/bootstrap/core_service.py:317 · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C017 | `settings_provider_profiles_update` | `settings_provider_profiles_update` | core | 7 | `profile_id!: string` `display_name!: string` `endpoint!: string` `model!: string` `enabled!: bool` `capabilities!: string[]` `network_profile_id?: nullable-string` | 错误样例：`error.code=INVALID_REQUEST`（成功外形见 Core handler） | §5.2 | UI | **PARTIAL** | registry:191 · HostCommandDispatcher.cs:347 · src/bootstrap/core_service.py:318 · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C018 | `settings_provider_profiles_delete` | `settings_provider_profiles_delete` | core | 7 | `profile_id!: string` | 错误样例：`error.code=INVALID_REQUEST`（成功外形见 Core handler） | §5.2 | UI | **PARTIAL** | registry:192 · HostCommandDispatcher.cs:357 · src/bootstrap/core_service.py:319 · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C019 | `settings_provider_bindings_set` | `settings_provider_bindings_set` | core | 7 | `capability!: string` `profile_id!: string` `scope!: object` | 错误样例：`error.code=INVALID_REQUEST`（成功外形见 Core handler） | §5.2 | UI | **PARTIAL** | registry:193 · HostCommandDispatcher.cs:360 · src/bootstrap/core_service.py:320 · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C020 | `settings_provider_bindings_clear` | `settings_provider_bindings_clear` | core | 7 | `capability!: string` `scope!: object` | `{cleared}` | §5.2 | UI | **FROZEN** | registry:170 · HostCommandDispatcher.cs:373 · src/bootstrap/core_service.py:321 · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C021 | `settings_provider_bindings_resolve` | `settings_provider_bindings_resolve` | core | 7 | `capability!: string` `book_id?: string` `chapter_id?: string` `run_id?: string` | `{profile_id, source}` | §5.2 | UI | **FROZEN** | registry:171 · HostCommandDispatcher.cs:378 · src/bootstrap/core_service.py:322 · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C022 | `settings_provider_run_snapshot_get` | `settings_provider_run_snapshot_get` | core | 7 | `run_id!: string` | 错误样例：`error.code=TARGET_NOT_FOUND`（成功外形见 Core handler） | §5.2 | — | **PARTIAL** | registry:172 · HostCommandDispatcher.cs:384 · src/bootstrap/core_service.py:323 · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C023 | `settings_network_profiles_list` | `settings_network_profiles_list` | core | 7 | `{}`（无参数；Dispatcher 丢弃输入） | `{profiles}` | §5.2 | UI | **FROZEN** | registry:137 · HostCommandDispatcher.cs:181 · src/bootstrap/core_service.py:325 · 样例(wire): `verification/NS-WIRE-A1/probe-results.json` |
| C024 | `settings_network_profiles_create` | `settings_network_profiles_create` | core | 7 | `display_name!: string` `mode!: string` `proxy_endpoint?: nullable-string` `verify_tls?: bool` `confirm_disable_tls_verification?: bool` `allow_proxy_failure_direct_fallback?: bool` | `{profile}` | §5.2 | UI | **FROZEN** | registry:167 · HostCommandDispatcher.cs:311 · src/bootstrap/core_service.py:326 · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C025 | `settings_network_profiles_update` | `settings_network_profiles_update` | core | 7 | `network_profile_id!: string` `display_name!: string` `mode!: string` `verify_tls!: bool` `allow_proxy_failure_direct_fallback!: bool` `proxy_endpoint?: nullable-string` `confirm_disable_tls_verification?: bool` | `{profile}` | §5.2 | UI | **FROZEN** | registry:169 · HostCommandDispatcher.cs:319 · src/bootstrap/core_service.py:327 · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C026 | `settings_network_profiles_delete` | `settings_network_profiles_delete` | core | 7 | `network_profile_id!: string` | `{deleted}` | §5.2 | UI | **FROZEN** | registry:168 · HostCommandDispatcher.cs:330 · src/bootstrap/core_service.py:328 · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C027 | `settings_network_profiles_test` | `settings_network_profiles_test` | core | 7 | `network_profile_id!: string` `provider_profile_id?: string` | 错误样例：`error.code=INVALID_REQUEST`（成功外形见 Core handler） | §5.2 | UI | **PARTIAL** | registry:194 · HostCommandDispatcher.cs:366 · src/bootstrap/core_service.py:332 · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C028 | `settings_network_profile_default_set` | `settings_network_profile_default_set` | core | 7 | `network_profile_id!: string` | `{network_profile_id}` | §5.2 | UI | **FROZEN** | registry:166 · HostCommandDispatcher.cs:308 · src/bootstrap/core_service.py:329 · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C029 | `settings_network_profile_default_clear` | `settings_network_profile_default_clear` | core | 7 | `{}`（无参数；Dispatcher 丢弃输入） | `{network_profile_id}` | §5.2 | UI | **FROZEN** | registry:165 · HostCommandDispatcher.cs:260 · src/bootstrap/core_service.py:330 · 样例(wire): `verification/NS-RECLASSIFY-1/probe-results.json` |
| C030 | `settings_network_profile_resolve` | `settings_network_profile_resolve` | core | 7 | `provider_profile_id?: string` | 错误样例：`error.code=INVALID_REQUEST`（成功外形见 Core handler） | §5.2 | UI | **PARTIAL** | registry:195 · HostCommandDispatcher.cs:370 · src/bootstrap/core_service.py:331 · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |
| C031 | `settings_resolve_overrides` | `settings_resolve_overrides` | core | 7 | `book_id?: string` `chapter_id?: string` `run_id?: string` `keys?: string[]` | `{values}` | §5.2 | — | **FROZEN** | registry:138 · HostCommandDispatcher.cs:185 · src/bootstrap/core_service.py:324 · 样例(wire): `verification/NS-WIRE-A1/probe-results.json` |
| C032 | `credential_put` | — | host-local | — | 见 Host 实现（Host-local 参数校验） | `CredentialOperationResult`（HostCredentialCoordinator.cs:26；secret 不回显） | §5.8 | UI | **FROZEN** | registry:58 · HostCommandDispatcher.cs:417（default 透传） · —（无 Core 路由） · 样例(test): `apps/desktop-avalonia/tests/NewManga.App.Tests/CredentialUiTests.cs:398` |
| C033 | `credential_clear` | — | host-local | — | 见 Host 实现（Host-local 参数校验） | `CredentialOperationResult`（HostCredentialCoordinator.cs:27） | §5.8 | UI | **FROZEN** | registry:59 · HostCommandDispatcher.cs:417（default 透传） · —（无 Core 路由） · 样例(test): `apps/desktop-avalonia/tests/NewManga.App.Tests/CredentialUiTests.cs:406` |

### 4.2 Library（8 条）

| ID | 前端命令 | 路由目标 | 通道 | minor | 入参（校验/实测） | 结果外形（实测/类型） | 错误码族 | UI 消费者 | 状态 | 源码引用 · 样例 |
|---|---|---|---|:--:|---|---|---|---|---|---|
| C034 | `library_list_books` | `ListBooks` | core | 3 | 透传（Core 校验；实测空 payload） | `[{ book_id, created_at, is_archived, is_favorite, original_title, page_count, title, updated_at }]` | §5.1 | UI | **FROZEN** | registry:120 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:3783-3806（ListBooks 分支） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C035 | `library_list_recycle_bin_books` | `ListRecycleBinBooks` | core | 3 | 透传（Core 校验；实测空 payload） | `[array]` | §5.1 | — | **FROZEN** | registry:121 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:3733-3760（ListRecycleBinBooks 分支） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C036 | `library_create_book` | `CreateBook` | core | 8 | `{title!}`（Core `_CREATE_FIELDS`，:244-247） | `{book_id, created_at, is_archived, is_favorite, original_title, page_count, title, updated_at}` | §5.3 | UI | **FROZEN** | registry:122 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:3531（handle_create_book 调用；校验 :921-941） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C037 | `create_chapter` | `CreateChapter` | core | 8 | `{book_id!, title!, chapter_number?}`（Core `_CREATE_FIELDS`，:244-247） | `{chapter_id, chapter_number, sort_order, title}` | §5.3 | — | **FROZEN** | registry:123 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:3533（handle_create_chapter 调用；校验 :921-941） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C038 | `library_import_file` | — | host-local | — | 见 Host 实现（Host-local 参数校验） | `ImportOutcome{ok, message, error_code, imported_files, skipped_files}`（App/Services/ImportExportContracts.cs:27） | §5.8 | UI | **FROZEN** | registry:68 · HostCommandDispatcher.cs:417（default 透传） · —（无 Core 路由） · 样例(test): `apps/desktop-avalonia/tests/NewManga.Host.Tests/GrantIssuerTests.cs:82` |
| C039 | `library_import_folder` | — | host-local | — | 见 Host 实现（Host-local 参数校验） | `ImportOutcome{...}`（同上） | §5.8 | UI | **PARTIAL** | registry:69 · HostCommandDispatcher.cs:417（default 透传） · —（无 Core 路由） · 样例：缺 |
| C040 | `library_delete_book_permanently` | `PermanentlyDeleteBook` | core | 10 | `{book_id!, confirm_permanent_delete!}`（core_service.py:1341-1352） | `{book_id, deleted}` | §5.4 | — | **FROZEN** | registry:164 · HostCommandDispatcher.cs:270 · src/bootstrap/core_service.py:3577-3578（handle_permanently_delete_book） · 样例(wire): `verification/NS-WIRE-B1/probe-results.json` |
| C041 | `library_delete_books_permanently` | `PermanentlyDeleteBooks` | core | 10 | `{book_ids!, confirmed_book_ids!, confirm_count!, confirm_permanent_delete!}`（core_service.py:1360+） | 错误样例：`error.code=INVALID_REQUEST`（成功外形见 Core handler） | §5.4 | — | **PARTIAL** | registry:196 · HostCommandDispatcher.cs:282 · src/bootstrap/core_service.py:3579-3580（handle_permanently_delete_books） · 样例参考: `verification/NS-RECLASSIFY-1/probe-results.json` |

### 4.3 Region（6 条）

| ID | 前端命令 | 路由目标 | 通道 | minor | 入参（校验/实测） | 结果外形（实测/类型） | 错误码族 | UI 消费者 | 状态 | 源码引用 · 样例 |
|---|---|---|---|:--:|---|---|---|---|---|---|
| C042 | `set_region_type` | `set_region_type` | core | 3 | `region_id!: string` `new_region_type!: string` `expected_revision?: int` | `{region_id, region_type, revision_no, sfx_policy}` | §5.7 | UI | **FROZEN** | registry:177 · HostCommandDispatcher.cs:394 · src/bootstrap/core_service.py:1979（handle_set_region_type）；src/bootstrap/core_service.py:4164 · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C043 | `list_regions` | `list_regions` | core | 3 | 透传（Core 校验；实测 payload：`{page_id}`） | `{page_size, regions}` | §5.7 | UI | **FROZEN** | registry:126 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:2054（handle_list_regions）；src/bootstrap/core_service.py:4165 · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C044 | `list_region_revisions` | `list_region_revisions` | core | 3 | `region_id!: string` | `{current_revision_no, region_id, revisions}` | §5.7 | UI | **FROZEN** | registry:197 · HostCommandDispatcher.cs:389 · src/bootstrap/core_service.py:2085（handle_list_region_revisions）；src/bootstrap/core_service.py:4166 · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C045 | `restore_region_revision` | `restore_region_revision` | core | 3 | `region_id!: string` `revision_no!: int` `expected_revision!: int` | `{region_id, region_type, revision_no, sfx_policy}` | §5.7 | UI | **FROZEN** | registry:178 · HostCommandDispatcher.cs:399 · src/bootstrap/core_service.py:2096（handle_restore_region_revision）；src/bootstrap/core_service.py:4167 · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C046 | `rerender_page` | `rerender_page` | core | 3 | `page_id!: string` | `{artifact_id, page_id, preview, preview_error, reports, revision_no}` | §5.7 | UI | **FROZEN** | registry:179 · HostCommandDispatcher.cs:404 · src/bootstrap/core_service.py:2135（handle_rerender_page）；src/bootstrap/core_service.py:4256 · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C047 | `resolve_page_resource` | `resolve_page_resource` | core | 3 | `page_id!: string` | `{resource_id, revision}` | §5.7 | UI | **FROZEN** | registry:180 · HostCommandDispatcher.cs:407 · src/bootstrap/core_service.py:2363（handle_resolve_page_resource）；src/bootstrap/core_service.py:4389 · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |

### 4.4 Reader（4 条）

| ID | 前端命令 | 路由目标 | 通道 | minor | 入参（校验/实测） | 结果外形（实测/类型） | 错误码族 | UI 消费者 | 状态 | 源码引用 · 样例 |
|---|---|---|---|:--:|---|---|---|---|---|---|
| C048 | `list_chapters` | `list_chapters` | core | 3 | 透传（Core 校验；实测 payload：`{book_id}`） | `{chapters}` | §5.1 | UI | **FROZEN** | registry:124 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:4334-4350（list_chapters 分支） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C049 | `list_chapter_pages` | `list_chapter_pages` | core | 3 | 透传（Core 校验；实测 payload：`{chapter_id}`） | `{pages}` | §5.1 | UI | **FROZEN** | registry:125 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:4334-4360（list_chapter_pages 分支） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C050 | `library_get_reader_projection` | `GetReaderProjection` | core | 3 | `chapter_id!: string` `mode!: string` `start_position!: string` | `{book_id, chapter_id, last_page_id, last_read_at, mode, progress_percent, scroll_offset_y, total_read_seconds}` | §5.6 | UI | **FROZEN** | registry:142 · HostCommandDispatcher.cs:239 · src/bootstrap/core_service.py:3653-3654（handle_get_reader_projection） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C051 | `library_save_reading_progress` | `SaveReadingProgress` | core | 3 | `chapter_id!: string` `mode!: string` `page_id!: string` `scroll_offset_y?: double` `elapsed_seconds_delta?: double` | `null` | §5.6 | UI | **FROZEN** | registry:181 · HostCommandDispatcher.cs:410 · src/bootstrap/core_service.py:3655-3656（handle_save_reading_progress） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |

### 4.5 Resource（3 条）

| ID | 前端命令 | 路由目标 | 通道 | minor | 入参（校验/实测） | 结果外形（实测/类型） | 错误码族 | UI 消费者 | 状态 | 源码引用 · 样例 |
|---|---|---|---|:--:|---|---|---|---|---|---|
| C052 | `issue_resource_url` | — | bridge | — | `resource_id!: string` `revision!: string` | `{id, size}`（HostCommandDispatcher.cs:118-124） | §5.9 | 间接UI | **FROZEN** | registry:94 · HostCommandDispatcher.cs:109 · —（无 Core 路由） · 样例(test): `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:237` |
| C053 | `revoke_ref` | — | bridge | — | `opaque_id!: string` | `{revoked:true}`（HostCommandDispatcher.cs:135-140） | §5.9 | 间接UI | **FROZEN** | registry:95 · HostCommandDispatcher.cs:127 · —（无 Core 路由） · 样例(test): `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:245` |
| C054 | `revoke_resource_refs` | — | bridge | — | `resource_id!: string` | `{revoked_count}`（HostCommandDispatcher.cs:151-156） | §5.9 | 间接UI | **FROZEN** | registry:96 · HostCommandDispatcher.cs:143 · —（无 Core 路由） · 样例(test): `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:251` |

### 4.6 Workbench（12 条）

| ID | 前端命令 | 路由目标 | 通道 | minor | 入参（校验/实测） | 结果外形（实测/类型） | 错误码族 | UI 消费者 | 状态 | 源码引用 · 样例 |
|---|---|---|---|:--:|---|---|---|---|---|---|
| C055 | `core_ping` | `core.ping` | core | 3 | 透传（Core 校验；实测空 payload） | `{capabilities, protocol_version, status}` | §5.1 | Host启动 | **FROZEN** | registry:119 · HostCommandDispatcher.cs:417（default 透传） · src/bootstrap/core_service.py:3610-3613（core.ping 分支） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C056 | `library_start_run` | `StartRun` | core | 3 | `command!: string` `idempotency_key!: string` `scope!: object` `overrides?: object` | `RunStartInfo{run_id,status}`（App/Services/RunContracts.cs） | §5.5 | — | **FROZEN** | registry:147 · HostCommandDispatcher.cs:198 · src/bootstrap/core_service.py:3256（_dispatch_run_command）; :3273-3300（StartRun 分支） · 样例(wire): `verification/V11R-A-2/core-wire-run.ndjson` |
| C057 | `library_control_run` | `ControlRun` | core | 3 | `run_id!: string` `action!: string` `idempotency_key?: string` | `RunControlInfo{run_id,status,new_run_id?,new_run_status?}`（RunContracts.cs） | §5.5 | — | **FROZEN** | registry:148 · HostCommandDispatcher.cs:207 · src/bootstrap/core_service.py:3256; :3301-3321（ControlRun 分支） · 样例(wire): `verification/V11R-A-2/core-wire-run.ndjson` |
| C058 | `library_resume_blocked_run` | `ResumeBlockedRun` | core | 3 | 透传（Core 校验） | `RunControlInfo{run_id,status}`（RunContracts.cs） | §5.5 | — | **FROZEN** | registry:149 · HostCommandDispatcher.cs:212 · src/bootstrap/core_service.py:3256; :3322-3326（ResumeBlockedRun 分支） · 样例(wire): `verification/V11R-A-2/core-wire-run.ndjson` |
| C059 | `library_get_run_snapshot` | `GetRunSnapshot` | core | 3 | `run_id!: string` | `RunSnapshotInfo{run_id,command,scope,status,targets[]}`（RunContracts.cs） | §5.5 | — | **FROZEN** | registry:150 · HostCommandDispatcher.cs:213 · src/bootstrap/core_service.py:3256; :3327-3350（GetRunSnapshot 分支） · 样例(wire): `verification/V11R-A-2/core-wire-run.ndjson` |
| C060 | `library_get_task_projection` | `GetTaskProjection` | core | 3 | `run_id!: string` | `TaskProjectionInfo{run_id,run_status,run_title,overall_progress,current_page_id,current_step_type,step_flow[],rows[],tasks[],counts,blocked_reasons[],controls}`（RunContracts.cs） | §5.5 | — | **FROZEN** | registry:151 · HostCommandDispatcher.cs:214 · src/bootstrap/core_service.py:3256; :3351-3354（GetTaskProjection 分支） · 样例(wire): `verification/V11R-A-2/core-wire-run.ndjson` |
| C061 | `library_retry_failed_targets` | `RetryFailedTargets` | core | 3 | `run_id!: string` `idempotency_key!: string` | `RunControlInfo{run_id,status}`（RunContracts.cs） | §5.5 | — | **FROZEN** | registry:152 · HostCommandDispatcher.cs:217 · src/bootstrap/core_service.py:3256; :3355-3364（RetryFailedTargets 分支） · 样例(wire): `verification/V11R-A-2/core-wire-run.ndjson` |
| C062 | `library_reveal_export_folder` | — | host-local | — | 见 Host 实现（Host-local 参数校验） | `bool`（HostGrantCoordinator.RevealExportFolderAsync） | §5.8 | UI | **PARTIAL** | registry:108 · HostCommandDispatcher.cs:417（default 透传） · —（无 Core 路由） · 样例：缺 |
| C063 | `library_get_export_history` | `GetExportHistory` | core | 3 | `{}`（无参数；Dispatcher 丢弃输入） | `{exports}` | §5.6 | UI | **FROZEN** | registry:131 · HostCommandDispatcher.cs:237 · src/bootstrap/core_service.py:3677-3680（GetExportHistory 分支） · 样例(wire): `verification/S4-CMD-BATCH-1/commands/core-command-probe.json` |
| C064 | `library_start_export` | `StartExport` | core | 3 | `book_id!: string` `format!: string` `stale_policy!: string` `target_ref!: string` `format_options!: object` `chapter_ids!: string[]` `ordered_page_ids!: string[]` | `ExportStartInfo{export_id,status,page_count}`（App/Services/ImportExportContracts.cs:52） | §5.6 | UI | **FROZEN** | registry:153 · HostCommandDispatcher.cs:221 · src/bootstrap/core_service.py:3657-3658（handle_start_export） · 样例(test): `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:196` |
| C065 | `library_cancel_export` | `CancelExport` | core | 3 | `export_id!: string` | `ExportSnapshotInfo{...}`（App/Services/ImportExportContracts.cs:71） | §5.6 | UI | **FROZEN** | registry:154 · HostCommandDispatcher.cs:233 · src/bootstrap/core_service.py:3668-3676（CancelExport 分支） · 样例(test): `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:193` |
| C066 | `library_get_export_snapshot` | `GetExportSnapshot` | core | 3 | `export_id!: string` | `ExportSnapshotInfo{...}`（同上） | §5.6 | UI | **FROZEN** | registry:155 · HostCommandDispatcher.cs:234 · src/bootstrap/core_service.py:3659-3667（GetExportSnapshot 分支） · 样例(test): `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:191` |

## 5. 错误码族（源码定位）

| 族 | 错误码集 | 源码 |
|---|---|---|
| §5.1 `settings-generic` | 通用应用 envelope：`INVALID_REQUEST` / `PROTOCOL_VERSION_UNSUPPORTED` / `UNKNOWN`（core_service.py:3589+）；命令特定码见 §5.1 | 见族内引用 |
| §5.2 `p15` | P15 settings：`SETTINGS_INVALID_INPUT` / `SETTINGS_NOT_FOUND` / `SETTINGS_CONFLICT` / `SETTINGS_UNAVAILABLE`（core_service.py:3372-3388、3706-3731；settings_commands.py:106-112） | 见族内引用 |
| §5.3 `create` | 创建面：`PROTOCOL_VERSION_UNSUPPORTED` / `INVALID_REQUEST`(+details) / `TARGET_NOT_FOUND` / `LIBRARY_WRITE_FAILED` / `UNKNOWN`（core_service.py:3504-3559、921-941） | 见族内引用 |
| §5.4 `delete` | 删除面：`PROTOCOL_VERSION_UNSUPPORTED` / `INVALID_REQUEST` / `TARGET_NOT_FOUND` / `UNKNOWN`（core_service.py:3561-3587、1341-1400） | 见族内引用 |
| §5.5 `run` | Run 面：`INVALID_REQUEST` / `TARGET_NOT_FOUND` / `IDEMPOTENCY_KEY_REUSED` / `INVALID_RUN_TRANSITION`（core_service.py:3389-3411） | 见族内引用 |
| §5.6 `reader-export` | 阅读/导出面：`INVALID_REQUEST` / `EXPORT_NOT_FOUND` / `EXPORT_INPUT_UNAVAILABLE` / `EXPORT_PATH_UNAVAILABLE` / `UNKNOWN`（core_service.py:3648-3695） | 见族内引用 |
| §5.7 `region` | Region/Reader 写面：`INVALID_REQUEST` / `TARGET_NOT_FOUND` / `LOCK_CHANGED` / `UNKNOWN`（core_service.py:4160-4300） | 见族内引用 |
| §5.8 `host-local` | Host-local：`HOST_READ_ONLY` / `INVALID_ARGUMENTS` / typed `ShellActionException`（HostGrantCoordinator / HostCredentialCoordinator） | 见族内引用 |
| §5.9 `bridge` | HostBridge：`SidecarException` typed code（资源 grant 拒绝/撤销，HostCommandDispatcher.cs:96-162） | 见族内引用 |

> 说明：以上是**源码定位**到的错误码集；除 A-1/A-2 已运行验证的 CreateChapter / Run 面之外，
> 各命令的错误分支未逐条注入运行。§6 已按命令记录状态。

## 6. 缺口清单（PARTIAL / GAP 逐条）

| ID | 命令 | 缺口 |
|---|---|---|
| C001 | `settings_get` | Dispatcher 未约束入参（透传），结果投影未在 C# 类型化；已实测成功样例，错误码集未逐条运行核实 |
| C003 | `cleanup_preview` | Dispatcher 未约束入参（透传），结果未在 C# 类型化；错误码集未逐条运行核实 |
| C007 | `backup_list` | Dispatcher 未约束入参（透传），结果未在 C# 类型化；错误码集未逐条运行核实 |
| C008 | `backup_restore` | 仅记录到错误样例（BACKUP_RESTORE_REQUIRES_CONFIRMATION）；成功响应外形未实证（见 Core handle_backup_restore 源码） |
| C010 | `plugins_list` | Dispatcher 未约束入参（透传），结果未在 C# 类型化；错误码集未逐条运行核实 |
| C012 | `plugins_set_plugin_enabled` | 仅记录到错误样例（PLUGIN_NOT_FOUND）；成功响应外形未实证（见 Core handle_plugins_set_plugin_enabled 源码） |
| C014 | `plugins_open_directory` | Host-local shell 动作无自动化样例（仅实现源码定位 + 人工调用路径） |
| C016 | `settings_provider_profiles_create` | 仅有 Dispatcher 约束 + Core handler 源码 + 集成 basis=success 请求，无响应外形样例 |
| C017 | `settings_provider_profiles_update` | 同 C016：无响应外形样例 |
| C018 | `settings_provider_profiles_delete` | 同 C016：无响应外形样例 |
| C019 | `settings_provider_bindings_set` | 同 C016：无响应外形样例 |
| C022 | `settings_provider_run_snapshot_get` | 同 C016：无响应外形样例（需真实 run 才能实证） |
| C027 | `settings_network_profiles_test` | 同 C016：无响应外形样例（需 network/profile 配置才能实证） |
| C030 | `settings_network_profile_resolve` | 同 C016：无响应外形样例 |
| C039 | `library_import_folder` | Host-local 文件夹导入无自动化集成样例（仅实现源码定位），需补 E2E 证据 |
| C041 | `library_delete_books_permanently` | 仅有 Dispatcher 约束 + Core 源码 + 集成 basis=success 请求，无响应外形样例 |
| C062 | `library_reveal_export_folder` | Host-local shell 动作无自动化成功样例（仅实现源码 + 未知导出 id 的 typed 拒绝测试） |

## 7. 关键兼容边界：`library_start_run` minor=3 vs Core 2.6 provider overrides

**结论：当前命令路径（C056 `library_start_run` → Core `StartRun`，注册 minor=3）无法通过
`overrides.provider_profiles`；该参数只有请求 `minor=7` 时 Core 才接受。因此"新增 Provider 覆盖参数
能经现有命令路径通过"这一假设不成立，不能按 UI 设置等同 Run 成功。**

依据（`src/bootstrap/core_service.py`）：

- `_dispatch_run_command` 把请求 version 的 minor 传入（`:3697-3703`）；
- `StartRun` 分支：`if "provider_profiles" in overrides and protocol_minor != _P15_PROTOCOL_MINOR: raise PipelineError("INVALID_REQUEST", "provider profile overrides require Core 2.6")`（`:3283-3284`，`_P15_PROTOCOL_MINOR=7`，`:239`）；
- 只有 `protocol_minor == 7` 时才调用 `P15SettingsCommands.prepare_run_snapshot(scope, overrides)` 生成快照（`:3287-3290`）；
- `HostCommandRegistry` 的 `library_start_run` 注册为 minor=3（`HostCommandRegistry.cs:147`），Dispatcher 只写 `command/scope/overrides/idempotency_key`，不改 minor（`HostCommandDispatcher.cs:198-206`）。

验证方法（已复跑，证据 `verification/V11R-A-3/minor-compat/start-run-minor-probe.json`，
脚本 `verification/V11R-A-3/tools/probe_start_run_minor.py`，冻结 sidecar + BOOK-FIXTURE 副本，
四条 StartRun 使用同一有效 book scope 对照）：

| 变体 | 请求 minor | overrides | 实测响应 |
|---|---:|---|---|
| (a) 普通 overrides | 3 | `provider_bindings` | `{"run_id":"run-44e5…","status":"pending"}` → 成功 |
| (b) Provider 覆盖 | 3 | `provider_profiles` | `INVALID_REQUEST`（"Run request is invalid"；Core 源码 :3283-3284 的 minor 门拒绝） |
| (c) Provider 覆盖 | 7 | `provider_profiles` | `INVALID_REQUEST` + `details={phase:"binding",action:"select_profile",message_key:"SETTINGS_INVALID_INPUT"}` → 已进入 P15 `prepare_run_snapshot`，需要有效 provider profile 配置才可能成功 |
| (d) 普通 overrides | 7 | `provider_bindings` | `{"run_id":"run-431c…","status":"pending"}` → 成功（证明 minor=7 本身被接受） |

结论补充：(a) 成功而 (b) 在同一 book scope 下失败，差异只可能来自 `provider_profiles` 的 minor 门；
(c) 证明 minor=7 能进入 P15 解析路径（当前配置下返回 SETTINGS_INVALID_INPUT，属 P15 配置态而非协议拒绝）；
(d) 证明 minor=7 的普通 overrides 可成功。因此"把 `library_start_run` 升到 minor=7 就能透传 provider overrides"
只是必要条件，不是充分条件：还必须 P15 provider profile/binding 配置有效。
UI 侧结论：在命令路径升级为 minor=7 之前，`IRunController.StartRunAsync` 只承诺
`provider_bindings` 等普通 overrides；`provider_profiles` 应视为未支持的边界并在 UI 禁用/提示。

## 8. C067–C077 增量命令（PENDING, V11R-F0-1 / F0-2）

`V11R-F0-1`（core-writer）为 Region 写面新增 10 条 Host 命令，命令总数从 66 增至 76；`V11R-F0-2` 另新增
1 条 Region 文本投影读命令（C077），合入后为 77。本表保留 `PENDING` 状态，**不得**当作已冻结契约。
这些命令已在 `v11r/region-write` 分支实现并注册，合入 main 后本表可升级为 `FROZEN`。
上游契约（core-writer 产出，合入后本表可升级为 `FROZEN`）：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`。

| ID | 前端命令（待合入） | 域 | 预期通道 | minor | 参数外形（待 core-writer 契约确认） | 状态 |
|---|---|---|---|---|---|---|
| C067 | `create_region` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C068 | `delete_region` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C069 | `save_region_geometry` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C070 | `merge_regions` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C071 | `split_region` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C072 | `reorder_regions` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C073 | `save_manual_translation` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C074 | `confirm_region_final` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C075 | `set_region_lock` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C076 | `pin_revision` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C077 | `list_page_region_texts` | Region | core | 3（读命令，zero protocol bump） | `PENDING(V11R-F0-2)` |

约束：`C067–C077` 在 `V11R_REGION_WRITE_CONTRACT.md` 合入并由 DSH 签发前，任何一方不得在 UI 中
把它们当稳定契约消费；`CommandContractV11RTests` 会断言这 11 条不进入"已冻结集合"。

## 9. 已知偏差与后续

1. **`plugins_open_directory` / `library_import_folder` / `library_reveal_export_folder`** 为 Host-local 面，
   无完整自动化成功样例（前两者仅实现源码定位；`reveal` 只有未知 id 的 typed 拒绝测试）→ `PARTIAL`。
2. **`settings_get` / `cleanup_preview` / `backup_list` / `plugins_list`** 是 Dispatcher 透传读，
   结果未在 C# 类型化 → `PARTIAL`；补证方式：为每个命令补一条真实 probe 样例 + C# 投影类型。
3. **错误分支未逐条注入运行**：§5 的码集来自源码定位；若某命令错误码需要签发级保证，需新增
   negative probe（建议纳入 `V11R-A-4` 快照 CI）。
4. **`core.ping`** 在 Host 侧作为启动探针（`HostCommandRegistry.cs:119`），其 `capabilities` 只有
   `library.list_books`，不代表全部命令可用性。
5. **`abandon`**：Core `ControlRun` 支持 `abandon`（中断处置），但冻结的 `RunControlAction` 只暴露
   4 个动作（`doc/plan/V11R_AVALONIA_CONTRACT.md` §5.2）→ UI 契约 GAP，留待中断恢复任务补齐。

## 10. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-10-30 | 初版：C001–C066 逐条签发（FROZEN {frozen} / PARTIAL {partial} / GAP {gap}）+ C067–C076 PENDING + minor 兼容结论 | core-bridge（V11R-A-3） |
