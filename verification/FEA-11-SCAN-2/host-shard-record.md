# FEA-11-SCAN-2 分片 B 实施记录（Host/App 冷启动枚举接线）

- Task：`doc/tasks/FEA-11-SCAN-2.md`（B1；ready，作者未改卡面，AC 收口归 Lead/DSH）
- 分片：**B = Host/App .NET**；Core 分片 A = `0cb5177ca`
- 仓库：`G:\CODEX\New Manga`（main；不 push）；卡 base `703d9eb12`
- 实施者：`fea12-core-host`（DSH Agent Teams）；未自审
- 交付 commit：**`6c8b4cb2b`**（`feat(fea-11-scan-2): Host/App 冷启动枚举接线（分片 B）`；apps/** + host-* 证据）
- 提交后复核：`check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2.md` → **PASS（3 既有全局 warnings）**，EXIT 0；日志 `G:\CODEX\New Manga.workspace\FEA-11-SCAN-2\logs\host-check-postcommit.log`（仓外，避免 evidence 自指）

## 1. 实现摘要（本分片改动；含 1 个编译必需连带文件，见 §2 P2-4 例外）

### Host（`apps/desktop-avalonia/src/NewManga.Host/`）

- `Sources/SourceScanScheduler.cs`
  - `SourceScanTarget` 增补 enumerated 字段（`RegistryId/Generation/SourceKind/IdentityDigest`，`IsEnumerated`）；路径仍只在 Host 本地解析，不经 wire。
  - 新增 `SourceScanEnumerationResult` / `ISourceScanTargetEnumerator`；`SourceScanOutcomeKind.Skipped` + `SourceScanOutcome.Skipped(code)`（status 结果 `skipped`，无 scan 帧、无失败退避）。
  - `SourceScanScheduler.RefreshTargetsAsync`：单飞（与 tick 共用 `_tickGate`，重叠请求合并）；结果按 `source_id` 合并/去重（重复 Refresh 幂等，SCAN-1 同 id 目标被 enumerated 字段权威更新）；枚举失败为 typed 状态、不阻塞 tick、不自动重试（无重试风暴）。
  - `Snapshot()` 增补 `Enumeration`（`{available, last_refresh_at, last_result, last_error_code, skipped_targets}`，closed record；无路径/grant/session）。
  - `HostSourceScanExecutor.VerifyEnumeratedTarget`：扫描前用持久 `SourceAccessRegistry` 重新核验 `registry_id/generation/revoked/root readable/root identity`；
    - registry 缺失/撤销/代次漂移 → `Skipped`（typed code，未扫描、未铸 grant、未发 `ScanSourceSync`、不自动重新授权、不泄露路径）；
    - registry `List()` 抛 `SOURCE_REGISTRY_UNAVAILABLE`（L-S1：file-root 缺失/替换使整库不可读）→ fail-closed `Error(SOURCE_REGISTRY_UNAVAILABLE)`（S-1②，**不**输出 missing、**不**发 scan 帧）；
    - 同一路径不同物理文件（替换）→ `SOURCE_REGISTRY_UNAVAILABLE`；
    - 通过核验后用 Core 枚举的 `identity_digest` 作为 C-17 §5.3 missing baseline（后续会话内消失可产生 `missing` 观察；冷启动即缺失仍 fail-closed）。
  - 新增 `HostSourceScanTargetEnumerator`（production）：
    - `CoreServiceClient.ListSourceScanTargetsAsync`（客户端侧先 `RequireCapabilitiesAsync({"source.sync.enumerate/1"})`，不发命令探测；application 面、`{}` closed request）；
    - 纯映射 `TryMap`：closed `ScanTarget` 字段校验；未知 `source_kind` → typed skip 计数（P3-3）；`project_ids` 去重后 1..20，>20 → typed skip 计数、不截断、不回退 current（P3-4）；registry 缺失/撤销/代次不符/无可读 root → typed skip 计数；返回按 `source_id` 升序去重。
- `Sources/SourceScanStatus.cs`：`SourceScanEnumerationStatus` closed record + `SourceScanStatus.Enumeration` init 属性；`SourceScanResults.Skipped`。
- `HostRuntime.cs`：
  - Ready 后在 `StartSourceScanScheduler()` 内构造生产 enumerator（`SourceScanColdStartEnumeration` 控制）并**后台**触发一次 `RefreshTargetsAsync`（不阻塞启动；异常只记 typed 日志，不产生未观察任务异常）；
  - 公开 `RequestSourceScanRefresh()`（App Completed 触发；非阻塞，Host 未就绪/关闭时返回 false）；
  - 保留 SCAN-1 `RegisterSourceScanTarget`（既有单测/兼容），但生产 App 已不再调用（S-2）。
- `HostOptions.cs`：`SourceScanColdStartEnumeration = true`。

### CoreClient

- `CoreServiceClient.cs`：`SourceListScanTargetsCommand`/`SourceEnumerateCapability` 常量 + `ListSourceScanTargetsAsync`（capability 先 probe，缺失 → `CoreOperationException("CORE_CAPABILITY_MISSING", "protocol", false, ...)`；不登记 HostCommandRegistry/C-07，无 UI 面）。

### App（S-2）

- `ISourceImportController`：删除 `RegisterCompletedImportScanTargets(bookId, sources)`，新增无参 `RequestSourceScanRefresh()`（**不再由 App 计算/传递任何 source_id/path**）。
- `SourceImportCoordinator`：删除 SCAN-1 的 target 派生/注册逻辑与 `SourceScanTargetRegistration` 记录（App 不再以 StableSourceId/folder registry_id 作为权威）。
- `HostController`/`NullHostController`：实现 `RequestSourceScanRefresh()`（best-effort 直连 `HostRuntime`，失败不影响导入结果）。
- `ImportDockViewModel`：仅在引用导入终态 `Completed` 时调用一次 `RequestSourceScanRefresh()`（Failed/Cancelled 不触发）；删除 `bookId` 构造参数与 `_referenceBookId` 捕获逻辑。
- `LibraryViewModel`：移除 `bookId` 参数传递。

### 测试

- `tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs`（+10 例）：Refresh 合并/去重/幂等；枚举不可用 typed 状态 + 不阻塞 tick + 不自动重试；Refresh 与 tick 单飞；`skipped` 结果记录且不暂停；枚举状态脱敏；`TryMap` 合法映射/未知 kind/非法 digest/0 与 >20 project_ids/registry 缺失/撤销/代次漂移；executor 对 enumerated target 的撤销/代次漂移/冷启动 file-root 缺失/替换（typed skip 或 `SOURCE_REGISTRY_UNAVAILABLE`，零 scan 帧）。
- `tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs`：新增 `ColdStartEnumeration_WithoutAppRegistration_IsReadOnly`（真实 Core + 真实 v8 库 + 隔离 DataRoot + 新 Host 侧对象图、**无 App 注册**）：枚举成功、`target.source_id == Core sources.source_id` 且 `!= StableSourceId`、铸 grant 后 `ScanSourceSync`、wire 精确五命令、15 表快照逐行相等、脱敏；`NEWMANGA_FEA11_IPC=1` 门控；Core 未合入时写 NOT_RUN 证据并返回（本次 Core 分片已合入，真实通过）。
- `tests/NewManga.App.Tests/FakeHostController.cs`：`SourceScanRefreshRequests` 计数 + `RequestSourceScanRefresh`；`Fea11ScanRefreshVmTests`（5 例）：Completed 恰好一次 Refresh、Failed/Cancelled 不触发、接口无参数（S-2 判别：App 无法夹带 id）、confirm 在途时选择切换仍只触发一次。

## 2. 冻结决策落实

| 决策 | 落实 |
|---|---|
| B1 权威 | 仅 Core `source_list_scan_targets` 产生目标；Host 不自行发明 target；App 不再提供 id（S-2） |
| S-1②（file-root 缺失 = fail-closed） | `SOURCE_REGISTRY_UNAVAILABLE` typed error，**不**输出 missing、**不**发 `ScanSourceSync`；L-G 保留 |
| S-2（Core source_id 唯一权威） | App 接口无参数；VM 级测试断言；真实 IPC 断言 `target.source_id == sources.source_id` 且 ≠ `StableSourceId` |
| P3-3（未知 source_kind fail-closed） | `TryMap` typed skip 计数，不猜测 |
| P3-4（project_ids 1..20，>20 不进入） | `TryMap` typed skip 计数，不截断/不回退 current |
| 预算/单飞/退避/取消 | 沿用 SCAN-1（8 目标/256MiB、单飞含枚举、退避 60..3600、`Stop`/`Dispose` join） |
| 零写 | 枚举与扫描零 Core 业务写：真实 IPC 15 表快照逐行相等；Host registry 仅 `authorize` 更新 last-used（AC-S2-9 允许） |

## 3. 门禁实跑（2026-11-06，Asia/Shanghai）

| Gate | 命令 | 结果 | 证据 |
|---|---|---|---|
| Host 单测 | `dotnet test ...Host.Tests --filter "FullyQualifiedName~SourceScanScheduler"` | **47 passed / 0 failed / 0 skipped**，EXIT 0（SCAN-1 37 + 本片 10） | `logs/host-unit.log` |
| App VM 刷新 | `dotnet test ...App.Tests --filter "FullyQualifiedName~Fea11ScanRefreshVm"` | **5 / 0 / 0**，EXIT 0 | `logs/host-app-refresh.log` |
| 真实重启 IPC | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ...Host.Tests --filter "FullyQualifiedName~Fea11ScanIpcTests"` | **2 / 0 / 0**，EXIT 0（含 cold-start 1 例） | `logs/host-restart-ipc.log`、`host-cold-start.json`、`host-cold-start.txt` |
| 全量 .NET 基线（改动前） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | **1486 passed / 0 failed / 82 skipped / 1568**，EXIT 0 | `logs/host-dotnet-baseline.log` |
| 全量 .NET RUN1 | 同上 | 1495 / **1 failed** / 83 skipped；失败 = 已知 flaky `FluentResidual2VisualEvidenceTests`（见 §4） | `logs/host-dotnet-full-1.log` |
| 全量 .NET RUN2 | 同上 | 1494 / **2 failed** / 83 skipped；失败 = `FluentResidual2VisualEvidenceTests` + `TileChannelTests.TamperedTile_PreservingSize_Rejected`（各自隔离复跑 PASS，见 §4） | `logs/host-dotnet-full-2.log` |
| 全量 .NET RUN3（复跑） | 同上 | **1496 passed / 0 failed / 83 skipped / 1579**，EXIT 0 | `logs/host-dotnet-full-3.log` |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2.md` | **PASS（3 既有全局 warnings）**，EXIT 0 | `logs/host-check.log` |
| pins | `verify_pins.ps1` | **PASS 18/18**，EXIT 0 | `logs/host-pins.log` |
| API inventory | `python tools/generate_api_inventory.py --check` | **PASS**，EXIT 0（C-07 未变） | `logs/host-api-inventory.log` |
| 范围 | 见 `host-scope-validation.log`、`host-changed-files.txt` | 本片仅 apps/** + host-* 证据；`src/**` 为 Core 分片 `0cb5177ca` | 同名文件 |
| pytest | 本分片无 Python 改动，未重复全量 pytest（Core 分片的 `logs/core-pytest-*.log` 为 Python 侧证据） | NOT_RUN（by design） | — |

全量 .NET 分程序集（RUN3 = 通过）：Appearance 21 / Presentation 38 / ThemeEngine 253 / DesignSystem 117 / ApplicationCore 31 / Host 154(+10) / CoreClient 167 / App 715；跳过 83（+1 = 冷启动 IPC 门控测试）。
回归判定：passed **+10**（本片新增 Host 单测），failed 0（RUN3），skip 解释见上；无既有测试被删除或放宽。

## 4. Flaky 记录（如实，不称稳定 PASS）

- `NewManga.App.Tests.FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In`
  - 已知跨测试 `git status -- verification` 证据写竞争（PREREQ-1 债务；与 SCAN-1 r1/r2 记录一致）。
  - RUN1/RUN2 失败；隔离复跑 1 次仍失败（残留 `verification/FEA-09` 写竞态）、复跑第 2 次 **PASS**（`logs/host-flaky-fluent-rerun.log` 失败记录、`logs/host-flaky-fluent-rerun2.log` PASS）。
- `NewManga.Host.Tests.TileChannelTests.TamperedTile_PreservingSize_Rejected`
  - RUN2 单次失败（`Expected: "TileDigestMismatch" / Actual: "NO_ERROR"`），隔离复跑 **PASS 1/0/0**（`logs/host-flaky-tilechannel-rerun.log`）；与本片改动无代码交集，记录为环境/时序 flaky。
- RUN3 全量干净通过；每次全量后执行 `git checkout -- verification/FEA-09` 恢复。

## 5. AC-S2 本片证据映射（Host 侧）

| AC | 本片证据 | 状态 |
|---|---|---|
| AC-S2-1 冷启动枚举 | 真实 IPC cold-start（无 App 注册）：枚举 ok、wire 精确五命令、无 plan/apply | PASS（审计：真实 Host 对象图 + 真实 Core；未跑完整 HostRuntime 启动） |
| AC-S2-2 合并/去重/幂等 | 单测 `Refresh_...` + VM Completed 一次 Refresh | PASS |
| AC-S2-3 Core source_id 权威（S-2） | 真实 IPC：`target.source_id == Core sources.source_id` 且 ≠ `StableSourceId`；App 接口无参 | Host 侧 PASS；**完整 App 真实导入 → 枚举 E2E 未跑**（需 App 导入链，登记集成阶段） |
| AC-S2-4 registry 授权核验 | executor 单测（撤销/代次漂移/缺失）+ 真实 IPC registry 匹配 | PASS |
| AC-S2-5 启动前缺失/替换（S-1②） | executor 单测：冷启动缺失/替换 → `SOURCE_REGISTRY_UNAVAILABLE`，零 scan 帧 | PASS（单测级；L-S1 记录） |
| AC-S2-6 共享源 >20 project_ids | `TryMap` 单测（21 → typed skip；0 拒绝；1..20 通过） | PASS（Host 侧；Core 侧见分片 A） |
| AC-S2-7 预算/单飞/退避/取消 | SCAN-1 既有 47 例 + Refresh-tick 单飞单测 + 注入时钟零 sleep | PASS |
| AC-S2-8 零写/脱敏 | 真实 IPC 15 表快照相等；状态/日志脱敏单测；无路径/secret/grant/session | PASS（Host 侧） |
| AC-S2-9 门禁/回归/scope | 见 §3、§6 | Host 侧 PASS；**AC11-1 仍 PARTIAL、L10 不解决** |

## 6. 残余风险与未运行项

- **L-S1（既有，登记于卡）**：生产 file-root 缺失/替换会使持久 registry 整库不可读 → 本片对**所有**目标 fail-closed `SOURCE_REGISTRY_UNAVAILABLE`（typed skip/error），不会伪造 missing；registry 韧性修复另立缺陷卡，不在本卡。
- **L-S4（既有）**：`refresh_source_location_auth` 死代码；撤销/重注册后 Core location auth 不更新，本只读切片无法恢复。
- **冷启动 missing 语义（L-G）**：枚举成功后以 Core `identity_digest` 建立 baseline；真实 file-root 缺失的 fail-closed 语义保留（S-1②）。隔离 seed fixture 使用合成 `sources.source_id=s1`（非 `src-<uuid>`），Host 侧断言“等于 Core DB 权威值且 ≠ StableSourceId”；完整真实导入 E2E 待集成阶段。
- **HostRuntime 接线**：Ready 后后台枚举/`RequestSourceScanRefresh` 由代码审查 + 组件级真实 IPC 覆盖；未新增 HostRuntime 级 sidecar 测试（避免扩大卡面），既有 gated HostRuntime 集成测试未纳入本片。
- **pytest 全量**：本片无 Python 改动，未重复跑；Python 侧以 Core 分片证据为准。
- 真实 IPC 测试受 `NEWMANGA_FEA11_IPC=1` 门控且能力缺失时写 NOT_RUN 返回（本次 Core 分片已合入，真实 PASS）。

## 7. 证据 sha256（host-*）

| file | sha256 |
|---|---|
| `logs/host-unit.log` | `ec1c5eb450b9540fa770ac17158e36e272b04c5cfd4ad2e45c53653d7cff7950` |
| `logs/host-app-refresh.log` | `32c67251abf8c233ee055d601a17b4163c8e02c34bde3d029f908ff273c121b0` |
| `logs/host-restart-ipc.log` | `f34eb3a52608fe31ba3cd5fde09e6b45f96cbbcab1846ee8f60005cb65f48b48` |
| `host-cold-start.json` | `b1c1ae4dc5d77c4b39b3f5a0f17a08ff7230a9085afc849f75539a6616f07d37` |
| `host-cold-start.txt` | `d6d316f1a1dc05cd025b642e33dad141dce3aa6855551715683ee3d1e503e739` |
| `logs/host-dotnet-baseline.log` | `438d1adc838a4c9e18e67163046c295831daa3514aad493cb989fa9eeb4c8eec` |
| `logs/host-dotnet-full-1.log` | `522b4b55400aa2f7e15bc38a0b6a6420eefed6e67e5bb3f2b73140bedc85f1ba` |
| `logs/host-dotnet-full-2.log` | `6d8c9861f2849d355a4bf4192d32f147b12a5a1825b1faaf418ac8c4622e0f39` |
| `logs/host-dotnet-full-3.log` | `9b032c03f5c2f9a11d8865487d79f90087add06c5e6d6895c9c423dc7de450c5` |
| `logs/host-flaky-fluent-rerun.log` | `dc9bd907d80b5aa5fb858a5c1579928336fe92b010fda751316a4f25323c2668` |
| `logs/host-flaky-fluent-rerun2.log` | `25ea1a387b9b87a34e4f4d19024a4ebcc2b0c2d0a4ac08c0a20e7d70c9fb5214` |
| `logs/host-flaky-tilechannel-rerun.log` | `0e440494feb268bbb8a94b89fc447aea731186471ebec58ad95cb968241d0346` |
| `logs/host-check.log` | `b7822e3c851d010f7a0bc1a57a1ef270ede87595fd7d6d6056e0d4393365a3f4` |
| `logs/host-pins.log` | `f198eda409309d359a700135e0ecb1d56c6b3df8f0bed0cfcef6f7427a7336db` |
| `logs/host-api-inventory.log` | `b4b9e68e1f7fce0dc4aeecfae9d887da0c0661b346a9434930ae62b3a2270c47` |
| `host-scope-validation.log` | `cdd72d4f67d8880f264e8b5d11657c2bcdd509195313601f778ed842709211f2` |
| `host-changed-files.txt` | `bb409150138a2ada3f413816796e97452baa4db7616f62095854081a003b71b4` |

## 8. 复现

```
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceScanScheduler"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Fea11ScanRefreshVm"
$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Fea11ScanIpcTests"
dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build            # 全量；跑后 git checkout -- verification/FEA-09
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
C:/Python314/python.exe tools/generate_api_inventory.py --check
```

## 9. r2 返修（SCAN-2 r1 Review CHANGES：P1-1 / P2-1 / P2-3 / P2-5 + P2-4 措辞）

r1 Review：`doc/reviews/FEA-11-SCAN-2-r1.md`（reviewed_head `fa38c47ef`；CHANGES，P0=0/P1=1/P2=5/P3=6）。
本节对应 r2 返修 commit（见 §10.6）。

### 10.1 P1-1（阻断）：共享源 scope=current → all

- 根因：`HostSourceScanExecutor` 的 scan/missing 两处硬编码 `scope="current"` 且携带全部 project_ids；Core 对 `scope=current` 强制恰好 1 个 project（`scanner.py`），多 book 共享源每轮 `INVALID_REQUEST` → 永不被扫描。
- 修复：`ResolveScanScope(target)` 按 `ProjectIds.Count` 选 `current`(1)/`all`(>1)；scan 与 missing 帧统一走 `WriteScanSyncFields` / `WriteScanMissingFields`，并公开 `BuildScanSourceSyncPayload` / `BuildScanMissingPayload` 供 frame 级测试。
- 单元判别（`SourceScanSchedulerTests`，+3）：`ScanPayload_SingleProject_UsesCurrentScope`、`ScanPayload_SharedSource_UsesAllScope_AndAllProjectIds`、`MissingPayload_UsesSameScopeSelection_AndCarriesObservation`（解析真实 payload JSON 断言 scope/project_ids/grant_ids/missing 形状）。
- 真实 IPC 判别：新增 `RealImportThenEnumeration_SharedSource_UsesAllScope_AndCoreSourceId`（见 §10.3）——同一真实源导入两个 book 后，第二 tick 的 `ScanSourceSync` 帧 `scope=all` 且 project_ids 恰为两个 book；单 book tick 为 `scope=current`。`host-r2-import-e2e.json`。

### 10.2 P2-1：tick 期间 Refresh 丢失 → pending/coalesce + tick 后重放

- 根因：`RefreshTargetsAsync` 在 `_tickGate.WaitAsync(0)` 失败时只返回 false，无 pending 标志；tick 结束也不补跑 → Completed 导入恰逢 tick 时新源本会话不再枚举。
- 修复：新增 `_refreshPending`（gate 竞争失败时置位，日志 “refresh queued”）；`TickAsync` 拆为 wrapper + `TickCoreAsync`，wrapper 在释放 gate 后 `ReplayPendingRefreshAsync`（一次、防重入、异常仅 typed 日志）；`Dispose`/取消安全。
- 单元判别：`RefreshRequestedDuringTick_IsReplayedAfterTickCompletes`——tick 阻塞期间请求 Refresh 返回 false 且入队，tick 完成后一次重放使新 target 出现在快照，下一 tick 实际扫描该 target。

### 10.3 P2-3：真实导入 → 枚举 E2E（gated）

- 新测试：`Fea11ScanIpcTests.RealImportThenEnumeration_SharedSource_UsesAllScope_AndCoreSourceId`（`NEWMANGA_FEA11_IPC=1`）。
- 装置：真实 Python Core（当前 src）+ 全新隔离 DataRoot + 生产 `SourceImportCoordinator`（与 FEA-09 真实 IPC 相同的 Host-local 路由）；真实导入一个 PNG 到 book1，再导入同一物理源到 book2。
- 断言：`sources.source_id`（真实 `src-<uuid>`，本 fixture 为 `src-b1e32669881c4022a70c075b6f18c624`）== `target.source_id` 且 ≠ `StableSourceId`（`src-d902593b57fa0f4a`）；`page_bindings` 派生 book 集合恰为两本；两次 Refresh 幂等（仍 1 个 target）；Refresh/扫描前后 15 表逐行相等；wire 单 book `scope=current`、共享 `scope=all`。
- **AC-S2-3 由此从 PARTIAL 升为完整 E2E 证据**（此前仅合成 `s1`）。

### 10.4 P2-5：HostRuntime Ready → 后台枚举（gated）

- 新测试：`Fea11Scan2HostRuntimeTests.Ready_StartsBackgroundEnumeration_WithoutBlocking`（`[HostSidecarFact]`，需要 `NEWMANGA_CORECLIENT_SIDECAR_DIR`；本仓库 build/sidecar 包可满足）。
- 断言：真实 `HostRuntime.StartAsync` 返回 Ready（evidence：start_elapsed_ms≈460）；`ScanScheduler` 已启动；Ready 后后台枚举状态出现（`Enumeration` 非 null），当前仓库 sidecar 包为 C-17 v1.1 之前构建 → typed `CORE_CAPABILITY_MISSING`（fail-closed，不阻塞）；`RequestSourceScanRefresh()` 被接受；refresh 结束后仍可执行 Tick；状态 JSON 无绝对路径。
- **限制（明确登记）**：HostRuntime 的 sidecar 装配没有 fake-Core/注入时钟 seam（不重构生产不可注入），因此“Ready→后台枚举且不阻塞”由本 gated 用例证明，“成功枚举”由 §10.3 组件级真实 Core E2E 证明；仓库 sidecar 包未含新 Core 命令（重建 sidecar 不在本卡授权范围），故本用例在 Available=true 分支为前向兼容断言。
- 证据：`host-r2-runtime-enumeration.json`（`enumeration_error_code=CORE_CAPABILITY_MISSING`，`redacted=true`）。

### 10.5 P2-4：allowlist 例外措辞更正（不改代码）

- `host-shard-record.md` §1 原写“本分片改动，均在卡 allowed_paths”不准确；已改为“含 1 个编译必需连带文件”。
- 明确：`apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs` 为删除 ImportDock `bookId` 形参的编译必需连带修改，**不在**冻结 allowed_paths；Lead 已在 r1 Review 处置记录 allowlist 例外（P2-4）；本片 r2 未再次修改该文件。`host-changed-files.txt` 同步标注。

### 10.6 P3 同批小修（非阻断）

- `HostRuntime.cs` 过期注释（“Cold start enumerates no sources (L-A)…only over App-registered targets”）改为 SCAN-2 语义（Ready 后后台枚举）。
- `SourceScanScheduler.VerifyEnumeratedTarget` generation-drift 注释补充：`SOURCE_REGISTRY_BUSY` 的 retryable 投影不代表本切片自动重新授权。
- App VM 测试名/注释更正（`ConfirmInFlight_CompletesOnce_ThenExactlyOneRefresh`；S-2 下选择切换不参与刷新请求）。

### 10.7 r2 门禁（2026-11-06；HEAD 含 Core r2 `20faf062a`）

| Gate | 命令 | 结果 | 证据 |
|---|---|---|---|
| Host 单测 | `--filter FullyQualifiedName~SourceScanScheduler` | **51 / 0 / 0**，EXIT 0（r1 47 + P1-1/P2-1 的 4 例） | `logs/host-r2-unit.log` |
| App VM | `--filter FullyQualifiedName~Fea11ScanRefreshVm` | **5 / 0 / 0**，EXIT 0 | `logs/host-r2-app-refresh.log` |
| 真实 IPC（含共享源/真实导入 E2E） | `$env:NEWMANGA_FEA11_IPC=1; --filter Fea11ScanIpcTests` | **3 / 0 / 0**，EXIT 0 | `logs/host-r2-real-ipc.log`、`host-r2-import-e2e.json/.txt`、`host-r2-cold-start.json/.txt` |
| HostRuntime gated | `$env:NEWMANGA_CORECLIENT_SIDECAR_DIR=<repo build sidecar>; --filter Fea11Scan2HostRuntimeTests` | **1 / 0 / 0**，EXIT 0 | `logs/host-r2-runtime-enumeration.log`、`host-r2-runtime-enumeration.json` |
| pytest tests/fea11（按需） | `python -m pytest tests/fea11 -q -p no:cacheprovider` | **108 passed**，EXIT 0 | `logs/host-r2-pytest-fea11.log` |
| 全量 .NET RUN1 | `dotnet test …NewManga.sln -c Release --no-build` | 1499 / **1 failed** / 85 skipped；失败 = CoreClient `RunBindingFixTests…OcrNoLongerProviderNotConfigured`（`library.db-shm` 文件锁竞态；隔离复跑 PASS） | `logs/host-r2-dotnet-full-1.log`、`logs/host-r2-flaky-runbinding-rerun.log` |
| 全量 .NET RUN2 | 同上 | 1499 / **1 failed** / 85 skipped；失败 = 已知 flaky `FluentResidual2VisualEvidenceTests`（git-status 写竞态；隔离复跑 PASS） | `logs/host-r2-dotnet-full-2.log`、`logs/host-r2-flaky-fluent-rerun.log` |
| 全量 .NET RUN3（复跑） | 同上 | **1500 passed / 0 failed / 85 skipped / 1585**，EXIT 0 | `logs/host-r2-dotnet-full-3.log` |
| check | `check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2.md` | **PASS（3 既有 warnings）**，EXIT 0 | `logs/host-r2-check.log` |
| pins | `verify_pins.ps1` | **PASS 18/18**，EXIT 0 | `logs/host-r2-pins.log` |
| API inventory | `generate_api_inventory.py --check` | **PASS**（C-07 未变），EXIT 0 | `logs/host-r2-api-inventory.log` |

全量 .NET 口径：r1 集成基线 **1496/0/83**（Lead `fa38c47ef`）→ r2 **1500/0/85**（+4 passed = 新增单测；+2 skipped = 新增 2 个 gated 测试：真实导入 E2E + HostRuntime gated）。每次全量后 `git checkout -- verification/FEA-09`。

### 10.8 r2 证据 sha256

| file | sha256 |
|---|---|
| `host-r2-import-e2e.json` | `29672d5f7110162f1209d8d5dbb9c0bdd1ca579ef613abe29ac3ec3d0fe72378` |
| `host-r2-import-e2e.txt` | `bc489cfe6c598bba9986b51c87a4ce55ad0a4fcffd76dfb32621810b519fdf81` |
| `host-r2-cold-start.json` | `b1c1ae4dc5d77c4b39b3f5a0f17a08ff7230a9085afc849f75539a6616f07d37` |
| `host-r2-cold-start.txt` | `9b7b241c7fc869af4bfdc5b19b0ff43bbf1c9de9d4112623c7a58c07b1c06ac2` |
| `host-r2-runtime-enumeration.json` | `fc692a69c304c4522445163e76e24f2263b72f5278273b966ae0cc1032135cec` |
| `host-r2-scope-validation.log` | `45138c709e0c0e0bbd1e6969a905c943dd36f7ab5497a43da5e88a97866fc413` |
| `logs/host-r2-unit.log` | `247c870678ef152f96dd36cf7a18e3903877a8f8e35c72cf431efcc990ac43b3` |
| `logs/host-r2-app-refresh.log` | `9e1d385bb978299dba9f90a3ba2d69dd4160d188044efaf7403e38265279ac2f` |
| `logs/host-r2-real-ipc.log` | `471442c12c67bafd36b1200eb23d3c840485fe7a091ade4c5707c136378ba9c0` |
| `logs/host-r2-runtime-enumeration.log` | `f1a42bacf6507e19b570638e55e24d587cfb8b0ff1d36871cc222381115cf0e7` |
| `logs/host-r2-dotnet-full-1.log` | `297626c1fbbbd29430c9569c432ec716832e3c2ac9b64223f05391ad23b1c794` |
| `logs/host-r2-dotnet-full-2.log` | `2f5483099e8a5424af3e7595dd08f65beeaa917801d07a3dc223450e22cf6d61` |
| `logs/host-r2-dotnet-full-3.log` | `8bd2cc10a7ea7d7ad29f9c260641d1c7b103fc4b6f6425c78777f7e95da98ee6` |
| `logs/host-r2-flaky-runbinding-rerun.log` | `20f8ba2824fe3e1165524a4d8f5f129f6c6534d80a298d09adbff6d1e93efdcb` |
| `logs/host-r2-flaky-fluent-rerun.log` | `25ea1a387b9b87a34e4f4d19024a4ebcc2b0c2d0a4ac08c0a20e7d70c9fb5214` |
| `logs/host-r2-pytest-fea11.log` | `da2fa25e398c7d5a3357a7b536963ee88477278f3e2ac4a26f0e3f6ee619c6a0` |
| `logs/host-r2-check.log` | `f46f843311c6f817f96a28792f48a75374ffe56a47b408b7c35def2c1d0a3fbb` |
| `logs/host-r2-pins.log` | `f198eda409309d359a700135e0ecb1d56c6b3df8f0bed0cfcef6f7427a7336db` |
| `logs/host-r2-api-inventory.log` | `b60105ac624c7e4d681a36cb45129471c16a4ed72e7751076bed4bbe818ba758` |

### 10.9 r2 残余 limitation

- **L-S1（不变）**：生产 file-root 缺失/替换使持久 registry 整库不可读 → 全目标 typed fail-closed；registry 韧性另立缺陷卡。
- **P2-5 限定**：HostRuntime 成功枚举路径受 sidecar 版本限制（仓库包早于 C-17 v1.1），由组件级真实 Core E2E 补足；HostRuntime 无 fake Core/注入时钟 seam，登记 limitation。
- **P2-3 之后的 AC-S2-3**：真实导入→枚举 E2E 已通过（AC-S2-3 可完整 MET）；但仅覆盖单文件 PNG 导入，未覆盖 folder/encrypted 源（同 SCAN-1 口径）。
- 其余 L-A/L-G/L-S4/L10/AC11-1 PARTIAL 不变。

## 10. 交给 Lead 的收口提示

- 本片只提交 apps/** 与 `verification/FEA-11-SCAN-2/host-*`；**未改卡面/STATUS/PLAN/LEDGER/reviews**，AC 标记与 Handoff 收口由 Lead/DSH 执行。
- 与 Core 分片 `0cb5177ca` 合并后建议：真实重启 IPC 复跑（已在本工作树通过）、App 真实导入 → 枚举 E2E 补测（AC-S2-3 完整口径）、registry 韧性（L-S1）另立缺陷卡。
