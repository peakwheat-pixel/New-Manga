# GATE3-APP-SKIP-TRIAGE-1：App.Tests 4 个 with-fixture skip 的归因（实测）

基线 `6cc62dd01`。无夹具基线 App.Tests **953 / 0 / 11 / 964**；带夹具 **957 / 0 / 4 / 961**。

## 1. 4 个 skip 的实测抓取

`dotnet test --logger "console;verbosity=normal"` + 带 sidecar 目录，实测 `已跳过` 行：

```
NewManga.App.Tests.StartupDiagnosticsTests.RealProcessLaunchMatrix_ExitZeroAndDiagnosableStartupLog
NewManga.App.Tests.PerformanceBaselineTests.Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget
NewManga.App.Tests.Fea07Residual3CrashTests.Park_ProductionSwitchStopsBetweenPersistedTargetAndJournalCommit
NewManga.App.Tests.Fea07Residual3CrashTests.Recover_NewProcessRollsBackAndAdoptsTheLatestProtectedState
```

（**没有**用源码正则统计 —— 这是第三次提醒自己，前几次都因此出错。）

## 2. 四个门禁变量（读 attribute 源码）

| 测试 | attribute | 门禁变量 |
|---|---|---|
| `RealProcessLaunchMatrix_…` | `FEA07StartupProcessFact` | `NEWMANGA_FEA07_STARTUP_PROCESS=1`（注释还要求 interactive desktop session） |
| `Gated_HotSwitch_…` | （`NEWMANGA_FEA07_PERF`） | `NEWMANGA_FEA07_PERF=1` |
| `Park_…` | `Fea07CrashParkFact` | `NEWMANGA_FEA07_CRASH=1` **且** `NEWMANGA_FEA07_CRASH_PHASE=park` |
| `Recover_…` | `Fea07CrashRecoverFact` | `NEWMANGA_FEA07_CRASH=1` **且** `NEWMANGA_FEA07_CRASH_PHASE=recover` |

## 3. 开开关实测结果（★ 四个里两个可转）

| 测试 | 开变量后 | 结论 |
|---|---|---|
| `RealProcessLaunchMatrix_…` | **1 passed** | ✅ **可转真实执行**（只需 `NEWMANGA_FEA07_STARTUP_PROCESS=1`） |
| `Gated_HotSwitch_…` | **1 passed**（21 s） | ✅ **可转真实执行**（只需 `NEWMANGA_FEA07_PERF=1`） |
| `Park_…` | **1 failed**：`NEWMANGA_FEA07_CRASH_ROOT must point at the prepared isolated crash root (phase=park)` | ❌ **需外部崩溃注入**（`verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1` 准备隔离根 + 在崩溃点杀进程） |
| `Recover_…` | 未单独跑（同一 `ApplyGate` 机制，phase=recover） | ❌ 同 Park（**推断，未实测**） |

## 4. 结论

| 归类 | 数量 | 明细 |
|---|---|---|
| **① 仅缺 opt-in 变量，可转真实执行** | **2** | `RealProcessLaunchMatrix`、`Gated_HotSwitch` |
| ② 需外部崩溃注入（不是环境变量能解决） | **2** | `Park`、`Recover` |

**⇒ 4 个 with-fixture skip 里，2 个其实是"开关没开"，不是"跑不了"。**

**这与 Host 那 44 个的结论同型**：大量 skip 是 opt-in 门禁，不是能力缺失。

## 5. 诚实边界

- `Recover_…` **未单独实测**（只跑了 Park），其"同机制"是**推断**。
- **没有**把这两个的默认门禁改成常开 —— 那是**产品/CI 策略决定**（开常开会显著拉长默认套件时间：
  Perf 单测 21 s）。本卡只做归因，不改默认。
- 带夹具基线 957/0/4 与无夹具 953/0/11 **均未变化**（本卡只做了跑测，未改测试）。
- 条件 3 仍不判 MET。
