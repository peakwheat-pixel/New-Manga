# verification/FEA-07-RESIDUAL-3（R4b 证据）

> 来源卡：`doc/tasks/FEA-07-RESIDUAL-3.md`（0 pin、gated/进程级）。base `8855baaac`。
> scope 依据：`doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md` §3（AC3 崩溃最小方案）、§4（AC4 增量）、§5.2（R4b 面）、风险 R-1…R-9。
> 本目录只保存证据；证据字节与 `doc/tasks/FEA-07.md` 的 append-only 回填一致。

## 0. 结论（口径严格）

- **AC-R4b-1（AC1 / A03 + ACK/Intent）= MET（gated：真实 Host/Core）**。默认 `skip + reason`（`NEWMANGA_FEA07_A03=1` 才跑）。原生 IME 仍 `NOT_APPLICABLE`，唯一登记在 `doc/tasks/FEA-07.md` 的 AC5 行，本目录不重复。
- **AC-R4b-2（AC3 / A06 跨进程崩溃）= MET（进程级）**。外部脚本驱动 park → `Process.Kill(entireProcessTree:true)` → 新进程 recover；真死由心跳冻结证明。
- **AC-R4b-3（AC4 / A07 真实入口 + 诊断 sink + 9 类矩阵）= MET（真实进程 + 纯单元）**。
- **AC-R4b-4（证据/回填）= MET（本目录 + `doc/tasks/FEA-07.md` append-only）**。
- 不写「FEA-07 完全实现 / AC5 达成 / 生产双屏可用」。`skip` 与 `NOT_RUN` 都不写成 PASS。

## 1. 目录

| 路径 | 内容 |
|---|---|
| `README.md` | 本文件：口径、命令、结果、证据强度边界 |
| `DEFECTS.md` | 观测到的既有缺陷/口径偏差（含未修项；不掩盖） |
| `mutation-selfcheck.md` | 3 组变异自检（RED → sha256 MATCH → 复绿）逐字记录 |
| `RESOURCE-MANIFEST.json` | 资源处置清单（worktree/evidence/temp/test-fixture/user-data/tracked-side-effect/tool） |
| `evidence/crash-switch-r4b.json` | AC3 三阶段真实结果（park/kill/recover 全部字段） |
| `evidence/startup-matrix-r4b.json` | AC4 四组真实进程参数结果 |
| `logs/*.log` | 各次运行的原始输出（Host/App/全量/pytest/AC1 门禁/崩溃脚本/启动矩阵/变异） |
| `tools/crash-switch.ps1` | AC3 外部驱动脚本（park/kill/recover；exit code 0/10/11/12/2） |
| `tools/startup-matrix.ps1` | AC4 真实进程 4 组参数矩阵（exit code 0/2/12） |
| `tools/backfill-fea07.py` | `doc/tasks/FEA-07.md` append-only 回填脚本（可复现） |

## 2. 复现命令

```pwsh
# AC1（gated，需要仓库 Python；默认 skip + reason）
$env:NEWMANGA_FEA07_A03='1'
dotnet test apps\desktop-avalonia\tests\NewManga.Host.Tests\NewManga.Host.Tests.csproj -c Release `
  --filter "FullyQualifiedName~Fea07Residual3IpcTests"

# AC3（外部驱动 park/kill/recover）
pwsh -NoProfile -File verification\FEA-07-RESIDUAL-3\tools\crash-switch.ps1

# AC4 真实进程矩阵
pwsh -NoProfile -File verification\FEA-07-RESIDUAL-3\tools\startup-matrix.ps1
# AC4 gated fact（同一矩阵的测试形态）
$env:NEWMANGA_FEA07_STARTUP_PROCESS='1'
dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj -c Release `
  --filter "FullyQualifiedName~StartupDiagnosticsTests"
```

默认（不设门禁）下：AC1 fact、AC3 两个 fact、AC4 真实进程 fact **全部 skip + reason**；9 类 warning 矩阵与 sink 单元用例始终运行。

## 3. AC-R4b-1（AC1 / A03 + ACK/Intent）

测试：`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea07Residual3IpcTests.cs`
→ `A03_RealHostCore_FiftyRoundTripsAndAckReplay_KeepProtectedColumnsIdentical`

- **真实 Host/Core**：真实 Python `core_service`（production `CoreServiceClient` over stdio）+ 真实 `library.db`（由**生产装配**建出 book/chapter/page/region，同 `tests/fea10/support/restart_core.py` 先例），Core 在切换全程保持运行。
- **≥50 次前端往返**：`RoundTrips = 50` → **100 次**生产切换事务（`FrontendSwitchCoordinator` + `SwitchJournal` + 唯一写者 `AppearanceCoordinator`），与 App 侧 `FrontendHostCoordinator` 的 commit/rollback 同序。
- **逐列相同**：`regions.text_json` / `regions.current_revision_id` / `region_locked` / `translation_locked` / `inpaint_locked` / `sfx_policy`（含 `manual` 计数）/ `region_revisions` 行数 / 候选 store 行数 → 切换前后 **0 diff**。
- **读库方式**：既有「.NET 内嵌 Python 脚本」先例（`Fea11RunGrantIpcTests.cs:1178-1197` 形态）；**零新增 SQLite 托管依赖**（`NewManga.Host.Tests.csproj` 未改）。
- **ACK 丢失/重连**：`CurrentRunIntentCoordinator`（生产 intent 去重）+ `HostCommandDispatcher.InvokeAsync("library_start_run", RunPayloads.StartRun(...))`（生产 dispatcher + 生产 payload）+ `RunStartInfo.FromJson`（生产结果映射）。第 1 次 Core 已 accept 后抛 `IOException` 模拟 ACK 丢失 → pending key 保留 → 同 key 重连 → **同一 `run_id`**，`pipeline_runs` 仅 **+1**。
- **旧结果仅 candidate**：候选 store 行数 `0 → 0`、零解析、陈旧 base 未进入 `current_revision_id`（见 §6 证据强度边界 (a)）。
- **erratum（P3-01）**：冻结卡写作 `sfx_locked`，冻结 schema 实际列是 **`region_locked`**（另 `translation_locked`/`inpaint_locked` + `sfx_policy ∈ {skip,translate,manual}`）；本卡比对按真实列名执行，见 §6.5 与 `DEFECTS.md` D-R4b-6。

## 4. AC-R4b-2（AC3 / A06 跨进程崩溃）

事实：`apps/desktop-avalonia/tests/NewManga.App.Tests/Fea07Residual3CrashTests.cs`（两个 gated fact）
驱动：`verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1`

| 阶段 | 进程 | 断言 |
|---|---|---|
| park | `dotnet test --filter …Park_` | 生产切换事务在 `beforeJournalCommit` 停住：`journal.Stage=Rendered`（未完成）、`appearance.FrontendId=builtin.fluent`（目标已由唯一写者落盘）、心跳推进 |
| kill | 本脚本 | `Process.Kill(entireProcessTree: true)`（launcher 树 + 被测宿主）；launcher/testhost 均 `WaitForExit` 真退出；**心跳冻结**证明真死 |
| recover | `dotnet test --filter …Recover_` | 生产入口 `App.RecoverInterruptedSwitch`：journal 终态 `RolledBack`；`frontend=builtin.current-v2`（上一已提交）；`appearance.FrontendId` 未被 target 污染；**二次恢复零变化**（journal + appearance 字节不变）；暂停期外部改动被采用、**不回写旧快照**（r1：不只 appearance `Mode`，还包括**真实 `library.db` 的保护状态** —— 独立连接新增 revision 3 并设为 current + 翻转 `inpaint_locked`，恢复后仍是新 revision/新锁值/新文本）；真实 `library.db` 保护列 **0 diff**（park/kill 窗口与 recover 窗口各一次） |

- **禁止面自证**：无 `Environment.FailFast`；无同进程新 coordinator 冒充；`park` 用的是 `FrontendSwitchCoordinator`/`PresentationWindow` **既有** `beforeJournalCommit` seam（此前已被既有 headless 用例使用），未新增生产 backdoor。
- **「真死」三件套（P3-05）**：launcher `WaitForExit` + **testhost 已消失**（`testhostGone=true`）+ **heartbeat frozen**；证据 JSON 的 `kill.realDeathProven` 由三者合取。
- exit code 语义：`0` 全通过、`10` kill 后未真死、`11` park 未到达/现场不成立、`12` recover 断言失败、`2` 前置条件错误。本次实跑 `0`（`evidence/crash-switch-r4b.json`）。

## 5. AC-R4b-3（AC4 真实入口 + 诊断 sink + 9 类矩阵）

实现：
- 新增 `apps/desktop-avalonia/src/NewManga.App/Services/StartupDiagnostics.cs`：`Install(logDirectory)`（进程内幂等、目录不可写则降级为无 sink、**永不抛**）+ `Report(plan)` 一行摘要；sink 是 `TraceListener`，因此**复用组合根既有 `Trace.TraceInformation/TraceWarning`**，`startup.log` 与 Trace 输出同源（Trace 兼容）。`ResetForTests` 会还原进程级 `Trace.AutoFlush`（P3-03）。
- `App.axaml.cs` 接线 **2 行**（= `Install(...)` + `Report(startupPlan)`），未改组合根语义，未改组合根判定顺序。
- **r1（P1-01）红线修复（DSH 裁决 A，扩域单文件）**：`src/NewManga.App/Views/MainWindow.axaml.cs` 的 `WriteMaterialDiagnostics` 改为「显式 `--log-dir` 时 `LogDirectory` 拥有全部日志文件（含 `window-material.log`）；无 `--log-dir` 保留历史每用户位置（发行默认行为不变）」。
- **r2（P1-01）第二条分支同样收口**：`MainWindow.axaml.cs` 的 `PropertyChanged`→`RenderScaling` 分支原先把 `window-material.log` 路径**再次硬编码**（绕过 `--log-dir`）；r2 抽出 `internal static ResolveDiagnosticsRoot(AppOptions)`，材质行（`WriteMaterialDiagnostics`）与缩放行（`AppendScalingDiagnostics`）**共用**同一解析。`MainWindow.axaml.cs` 相对 r0 累计 **+38/−10**（r1 +5/−1 + r2 收口与理由注释）。

测试：`apps/desktop-avalonia/tests/NewManga.App.Tests/StartupDiagnosticsTests.cs`
- sink 单元：落盘内容/级别前缀、幂等、Trace 兼容、目录不可用降级、`Trace.AutoFlush` 还原（5 项）。
- **legacy 窗口 `window-material` 两条分支**（r2）：`MaterialDiagnosticsRoot_IsSharedByBothBranches`（纯函数：有/无 `--log-dir`）+ `ScalingDiagnosticsLandInTheIsolatedLogDirectory`（真实 `MainWindow` 驱动缩放写入口：落隔离 `--log-dir`、cwd 无 `com.newmanga.desktop`、真实 `%APPDATA%` 行数不增长）。
- **9 类 warning 逐项 fail-safe**（Theory，9 例）：坏 JSON / `schemaVersion` / `corners.scale` / `appearance.mode` / `appearance.contrast` / `motion.mode` / `motion.categories` / `theme.frontendId` / `theme.visualThemeId` → 每类都产生 warning 且 planner **强制 Current V2**。
- **真实进程 4 组参数**（gated）：默认 / `--presentation-host=true` / `--shell=legacy` / 坏外观文档 → `exit_code=0`、无 `fatal.log`、`startup.log` 含对应诊断行（坏文档还须 `fallback=True`）。
  - **隔离（r1，r2 改为 App 可见断言）**：每组用例的 `--data-root`/`--log-dir`/`--theme-home` 在临时根；env 注入只记录 App 侧实见值（**不是**隔离保证，见 §6.8）；断言 = `startup.log` install 行指向隔离 log 目录、`isolation` 行 `log-dir=` 一致且 `appdata=` 不被指向用例根、**cwd 下无 `com.newmanga.desktop`**、`window-material.log` 只出现在隔离 `--log-dir`、真实 `%APPDATA%` 行数不增长。
  - **红线断言（r1/r2）**：整轮矩阵前后真实 `%APPDATA%\com.newmanga.desktop\logs\window-material.log` 行数必须**不增长**（每组用例后与收尾各断言一次）。

实跑（有交互桌面会话 session 1；逐轮基线不同，均为 `delta=0`）：

| case | exit_code | fatal.log | startup.log | 命中行 | 隔离 `window-material.log` | 该轮真实 `%APPDATA%` 行数 |
|---|---|---|---|---|---|---|
| default | 0 | 无 | 2818 B | `startup: shell=Default` + `fallback=False` | 0 行 | 14443（不变） |
| `--presentation-host=true` | 0 | 无 | 2846 B | `startup: shell=PresentationHost` + `fallback=False` | 0 行 | 14443（不变） |
| `--shell=legacy` | 0 | 无 | 715 B | `startup: shell=Legacy` + `fallback=False` | **1 行（隔离目录）** | 14443（不变） |
| 坏外观文档 | 0 | 无 | 3295 B | `startup: appearance: appearance document is not valid JSON` + `fallback=True` | 0 行 | 14443（不变） |

- 红线汇总：本轮 `14443 → 14443`（delta=0）；历轮基线分别为 r1 `14275`、r2 首轮 `14340`、`14406`、`14411`、`14443`（每次变异实验后重设基线），**每轮均 `delta=0`**。`startup-matrix.ps1` 4/4 同样 delta=0（`evidence/startup-matrix-r4b.json` 的 `realUserProfileWindowMaterialLog`）。
- 无桌面会话（Windows session 0）时脚本 exit `12` 且 gated fact `skip + reason`：本期有会话，4/4 实跑。

## 6. 证据强度边界（如实登记，不掩盖）

1. **`region_candidates` 表不存在**：冻结卡把候选 store 写作 `region_candidates`，但冻结 schema 无该表；真实候选 store 是 `step_result_candidates`（V5 迁移改名为 `step_result_candidates_v5`）。因此 AC1 的「旧结果仅 candidate」断言 = 候选存量 `0 → 0`、零解析、陈旧 base 未进入 `current`；**不是**「预置一条陈旧候选并观察其状态」的强证据（成因见 `DEFECTS.md` D-R4b-1）。
2. **AC1 的 50 次往返在 Host 侧驱动生产切换事务**（journal + 唯一写者 + 同一 commit/rollback 顺序），UI 侧 layout/Loaded/render 门禁由既有 headless 用例（`PresentationHostCompositionTests`/`FrontendHostCoordinatorTests`）覆盖；本卡不重复实现 Avalonia 依赖。
3. **AC4 真实进程矩阵需要交互桌面会话**；本机 session 1 有桌面，实跑 4/4；CI/服务会话下会 skip/exit 12，不得记 PASS。
4. **AC3 的 kill 是可观测真死**（launcher `WaitForExit` + testhost 已消失 + heartbeat frozen），不是 OS 级 crash dump 分析；`exit code 语义显式`（0/10/11/12/2）。
5. **erratum（P3-01）**：冻结卡把 `region_locked` 写作 `sfx_locked`；实际 schema 列为 `region_locked`/`translation_locked`/`inpaint_locked` + `sfx_policy ∈ {skip,translate,manual}`（「manual 位」= `sfx_policy='manual'` 行数）。比对按真实列名执行，见 `DEFECTS.md` D-R4b-6。
6. **红线残留与基线（r1/r2，如实登记）**：`--shell=legacy` 写真实 `%APPDATA%` 的既有缺陷已在 r1（材质行）与 r2（缩放行）修复 —— 显式 `--log-dir` 下两条分支都落隔离目录。变异实验主动回退造成的行数增量**不删除**（删除又是一次真实目录写入），每轮实验后重设基线：r1 `14275 → 14276`（M4b）、r2 `14406 → 14408`（M5，+2）、`14410 → 14411`（M4b-r2，+1）；**M4b/M4b-r2 之后基线起，所有修复态运行 `delta=0`**。见 `DEFECTS.md` D-R4b-2 / D-R4b-9 / `mutation-selfcheck.md` §④⑤。
7. **红线范围边界（D-R4b-7）**：r1/r2 修的是**有 `--log-dir` 的路径**。既有 headless UI 用例里有一批 `Show()` 过 legacy `MainWindow` 且**不传** `--log-dir`，按「无 `--log-dir` 保留历史每用户位置」的设计仍会各写 1 行 —— 对照实测 **每轮 App.Tests 稳定 +16 行**（修复前后行为相同，属**既有**测试隔离缺口，不是 r1/r2 回归）。建议另立卡给这些用例补 `--log-dir`；本卡 AC4 红线断言在各次运行均 `delta=0`。
8. **env 注入不是隔离保证（r2 P2-01 更正）**：r1 曾称「注入 `APPDATA`+`USERPROFILE` 可让 `GetFolderPath(ApplicationData)` 返回隔离路径」——**错误**。真实 App 进程实测：注入后该 API 返回**空**，`Path.Combine("", …)` 落成 **cwd 相对路径** `<cwd>\com.newmanga.desktop\logs\window-material.log`。因此隔离的主闸只有「显式 `--log-dir` 拥有全部日志文件」这条产品契约；env 注入仅用于让 `startup.log` 的 `startup-diagnostics: isolation log-dir=… appdata=… cwd=…` 行记录 App 侧实见值，并配合 **cwd 断言**兜底。M4 的 RED 由「隔离目录断言 + `--log-dir` 契约」承担，**不宣称两道闸独立**。

## 7. 测试基线（本卡执行）

| 套件 | 结果 | 基线 | 差异 |
|---|---|---|---|
| `NewManga.Host.Tests` | **302 passed / 0 failed / 72 skipped** | 302/0/71 | +1 skipped（AC1 gated fact） |
| `NewManga.App.Tests` | **831 passed / 0 failed / 11 skipped** | 816/0/8 | +15 passed（sink 5 + 两条分支 2 + 9 类矩阵 9 - 1 gated skip 不计）、+3 skipped（AC4 真实进程 + AC3 park/recover） |
| 全量 `NewManga.sln` | **1794 passed / 0 failed / 107 skipped**（r2 静默树复跑；r1 首轮曾在并发写入 `verification/` 时被既有 `FluentResidual2VisualEvidenceTests` 的「运行期间 `git status` 不变」断言打红，见 §7.2） | 1779/0/103 | +15 passed、+4 skipped |
| `pytest tests -q` | **3395 passed / 0 failed / 10 skipped** | 3394/1（既有 flaky）/10 | 零 Python 源码改动 |

### 7.1 pytest

`C:/Python314/python.exe -m pytest tests -q`（`logs/pytest-r4b.txt`，254.53 s）→ **3395 passed / 0 failed / 10 skipped**
（基线 3394 passed / 1 failed（既有 flaky）/ 10 skipped；本轮既有 flaky
`tests/plugin/test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren` **未复现**，故 0 failed，属于改善而非恶化）。
本卡对 `src/**`（Python）与 `tests/**`（Python）**零 diff**（`git diff HEAD -- src tests` 为空）。既有 flaky 登记见 `DEFECTS.md` D-R4b-3。

### 7.2 一次并发写入导致的假红（如实登记）

r1 首轮全量运行出现 **1 failed**：`FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In`，
断言对比 `git status --porcelain -- verification` 的前后快照（该用例要求运行期间 `verification/` 不变）。当轮同时有
本会话的文档编辑与 `gates-lead.log` 落盘 ⇒ 快照从 `??` 变 ` M`，属**并发写入假红**，不是代码回归；
随后在静默树复跑为 **1792/0/107**（r1）/ **1794/0/107**（r2）。原失败日志保留在
`logs/full-solution-tests-first-run-concurrent-write.txt`。

## 8. 门禁自查

- 工作树 clean（提交前）；`git show --stat --oneline HEAD` 见交付报告。
- 禁止面零 diff：`doc/plan/**`、`doc/contracts/**`、18 pins、`tools/e2e/**`、`apps/desktop-avalonia/scripts/**`、`src/**`（Python）、`Switching/**`、`AppearanceCoordinator`/`FrontendSelector`、`NewManga.DesignSystem/**`、`NewManga.Appearance/**`、`*.axaml`、`*.csproj`、其它 `src/NewManga.App/**`。
- `App.axaml.cs` **+2 行**（≤5）。
- **r1/r2 扩域（DSH 裁决 A；仅该单文件）**：`apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs`
  相对 r0 累计 **+38/−10**（r1 的材质行 +5/−1；r2 把 `RenderScaling` 分支收口到 `ResolveDiagnosticsRoot` +
  `AppendScalingDiagnostics` 并加理由注释）。未改该文件其它内容、未改组合根逻辑、未改 `*.axaml`、
  未动其它 `src/NewManga.App/**`、未动契约/pins。
- 全量后 `git checkout -- verification/FEA-09` 已执行（该路径为既有副作用，不在提交内）。
