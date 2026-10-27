# NS-WIRE-A1 报告：NS 命令接线第一批（settings / plugins / backup / cleanup）

- Task: `doc/tasks/NS-WIRE-A1.md`（team task-23）；Branch/Worktree: `task/NS-WIRE-A1` /
  `G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1`；卡面 Base `230164c5c`，实际分支基于释放提交
  `b50ab8fc5`（该提交才包含任务卡与治理 PASS 的 STATUS/PLAN/LEDGER；230164c5c 早于卡片创建）
- 未 push；未改 Python Core 语义、未改 Host 契约（wire 契约不变）、未改旧壳；未把未验证命令标 IMPLEMENTED。

## 0. 结论

| AC | 判定 | 证据 |
|---|---|---|
| AC1 清单 | **MET** | 8 条 S3-A/B/C 命令逐条列出 name/domain/旧壳 handler/参数/返回/错误类型/Core 路由/minor/实测结果：`verification/NS-WIRE-A1/command-list.json` |
| AC2 实现 | **MET** | `HostCommandRegistry` 新增 8 条 Core 绑定（`settings.update_section(3)`、P15 settings 3 条 `(7)`、`backup.create(3)`、`plugins.set_enabled(3)`、`cleanup.run(3)`、`GetReaderProjection(3)`）；dispatcher 按旧壳签名做参数边界校验并翻译为 Core 负载；集成测试对冻结 sidecar **真实执行**（7 条成功 + reader projection 空 chapter 的 `TARGET_NOT_FOUND` 路由证明 + BOOK-FIXTURE 数据根 8 页 success probe） |
| AC3 parity | **MET** | `extract-command-surface.py --check` **PASS（66 命令零漂移）**；快照未变（sha `4c6a4da0…`）；registry 状态 **16→24 IMPLEMENTED / 50→42 NOT_SUPPORTED**（8 条 `NOT_SUPPORTED → IMPLEMENTED`）：`parity-update.json` + `evidence/`（parity-contract/integration-results/domain-services/not-supported/wiring 新鲜生成） |
| AC4 回归 | **MET** | `scripts/test.ps1` **110/110 passed, 0 skipped**；旧壳 vitest **60/60 文件、567/567 用例**；pytest **3F/2739P/9S**（与基线相同失败集合，0 新增） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

## 1. AC1 清单（8 条，S3-A/B/C）

| # | 命令 | 域 | 旧壳参数 | 旧壳返回 | Core 路由 | minor |
|---|---|---|---|---|---|---|
| 1 | `settings_update_section` | settings | `section: String, values: JSON` | `Value`（settings 投影） | `settings.update_section` | 3 |
| 2 | `settings_provider_profiles_list` | settings | （无） | `ProfileList<ProviderProfile>` | `settings_provider_profiles_list` | 7 |
| 3 | `settings_network_profiles_list` | settings | （无） | `ProfileList<NetworkProfile>` | `settings_network_profiles_list` | 7 |
| 4 | `settings_resolve_overrides` | settings | `keys, book_id?, chapter_id?, run_id?` | `OverridesResult` | `settings_resolve_overrides` | 7 |
| 5 | `backup_create` | settings | `backup_type?: String`（缺省 `manual`） | `Value`（备份投影） | `backup.create` | 3 |
| 6 | `plugins_set_enabled` | settings | `enabled: bool` | `Value`（global_enabled 投影） | `plugins.set_enabled` | 3 |
| 7 | `cleanup_run` | settings | （无） | `Value`（CleanupOutcome） | `cleanup.run` | 3 |
| 8 | `library_get_reader_projection` | reader | `chapter_id, mode, start_position` | `Value`（reader 投影） | `GetReaderProjection` | 3 |

每条的逐字段记录（旧壳 handler 文件:行、`legacy_returns`、`legacy_error_type`/`error_codes`、
probe 响应摘要）见 `verification/NS-WIRE-A1/command-list.json`。
**P15 面（2/3/4）必须 minor=7**：probe 反证 minor=3 返回 `INVALID_REQUEST`（`probe-results.json` 的 `negative_p15_wrong_minor`）。

## 2. AC2 实现（C# Host）

- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs`：
  `CoreBindings` 新增 8 条（含 minor）；`library_get_reader_projection` 从"Core 路由存在但未验证"表移除。
- `HostCommandDispatcher.cs`：新增 `WriteCorePayload` 与参数边界校验（对应旧壳 Tauri 签名）：
  - `settings_update_section` 要求 `section` 非空 string + `values` object；
  - `settings_provider_profiles_list` / `settings_network_profiles_list` / `cleanup_run` 传输空对象
    （旧壳无参数；Core 面拒收多余键）；
  - `settings_resolve_overrides` 要求 `keys: string[]`，可选 `book_id/chapter_id/run_id`；
  - `backup_create` 可选 `backup_type`，缺省 `manual`（与 Rust 侧 `.unwrap_or("manual")` 一致）；
  - `plugins_set_enabled` 要求 bool `enabled`；
  - `library_get_reader_projection` 要求 `chapter_id/mode/start_position` 三个非空 string。
  参数缺失/类型错 → `HostCommandInvalidArgumentsException`（`INVALID_ARGUMENTS`），与旧壳边界拒绝同语义；
  Core 返回的业务错误码原样透传（`CoreOperationException.Code`）。
- `DomainServices.cs` 无需改动：6 个 domain service 从 registry 派生，接入即覆盖（测试断言
  `services.Sum(ImplementedCount) == 24`、每个命令有恰一个归属）。

**真实执行证据**（`verification/NS-WIRE-A1/`）：

- `probe-results.json`：冻结 `core_service.exe`（无标签副本）直接执行 8 条 Core 路由的成功/失败结果，
  含 `settings.update_section` → `{"settings":{"ocr":{}}}`、profile lists → `{"profiles":[]}`、
  `resolve_overrides` → `{"values":[…sfx.policy…]}`、`backup_create` → `{backup_id,path,…}`、
  `plugins_set_enabled` → `{"global_enabled":false}`、`cleanup_run` → `{items,removed,…}`；
  `library_get_reader_projection` 在 BOOK-FIXTURE-1 数据根上返回 8 页投影（`layout=webtoon_vertical`）；
  反证：P15 minor 错 → `INVALID_REQUEST`、空 chapter → `TARGET_NOT_FOUND`。
- `evidence/integration-results.json`：C# dispatcher 对冻结 sidecar 真实执行 **24 条 implemented**
  （20 core + 4 bridge；本轮新增 7 条成功 + reader projection 路由到 `TARGET_NOT_FOUND` 的类型化证明），
  `all_ok=true`。
- `evidence/not-supported-typed-errors.json`：剩余 42 条仍为 typed `NOT_SUPPORTED` + 原因（不静默缺失）。
- `evidence/domain-services.json`、`evidence/parity-contract.json`、`evidence/wiring.json`：域归属/契约/UI 账本。

## 3. AC3 parity 前后对比

| 指标 | 前（S2 基线） | 后（本 Task） |
|---|---|---|
| registry IMPLEMENTED | 16 | **24** |
| registry NOT_SUPPORTED | 50 | **42** |
| Rust 命令面快照 | 66 命令，sha `4c6a4da0…` | 未变（`--check` PASS） |

8 条变更：`settings_update_section`、`settings_provider_profiles_list`、`settings_network_profiles_list`、
`settings_resolve_overrides`、`backup_create`、`plugins_set_enabled`、`cleanup_run`、
`library_get_reader_projection`（`NOT_SUPPORTED → IMPLEMENTED`，Core 路由/minor 见 §1）。
证据：`parity-update.json` + `parity-check.log` + `evidence/parity-contract.json`。

## 4. AC4 回归

| 门 | 结果 |
|---|---|
| `apps/desktop-avalonia/scripts/test.ps1`（真实 sidecar） | **TEST PASS (Debug): 110/110 passed, 0 skipped**（CoreClient 40 / Host 37 / App 33） |
| 旧壳 vitest | **Test Files 60 passed (60) / Tests 567 passed (567)** |
| `python -m pytest -q` | **3 failed, 2739 passed, 9 skipped**（与基线 3F/2739P/9S 相同失败集合，0 新增） |
| 不污染 | 全部命令在隔离 data root/无标签 sidecar 副本执行；真实 `%APPDATA%` 未使用 |

## 5. 遗留 / NOT_RUN

1. 本批只接 **S3-A/B/C 8 条**；S4-A/B/C 10 条（region 写/save_reading_progress/Run/Export）仍 NOT_SUPPORTED，
   留给后续批次（A 组后续/独立 Task）。
2. `library_get_reader_projection` 的成功路径依赖带页面的数据根（BOOK-FIXTURE-1）；集成测试数据根无页面，
   只证明路由与 `TARGET_NOT_FOUND` 错误码透传（成功路径由 probe 证据覆盖）。
3. `cleanup_run` 在空缓存上只验证了 `{items:{},removed:0,...}` 形状；真实有 pending 缓存时的清理未构造。
4. `backup_create` 在隔离根生成 `.nmbak` 包（已留 task-env）；恢复/删除不在本批。
5. 需独立 Review（Owner 不得自审）。
