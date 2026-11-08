# FEA-07-RESIDUAL-2 scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立只读 fresh subagent（未参与 FEA-07 实现）；DSH 落盘 |
| 被审 head | `0a39a78f0`（clean） |
| 结论 | **`NOT_RECOMMENDED`**（占位卡按现文）；按 §5 改写后可冻结 |
| 口径更正 | ①FEA-07 的 ADJ 锚点是 **§2 裁决表 `:33-37`（W-01…W-05）+ §4 矩阵行 `:66`**，**不是 §7.4**（那是 FEA-06-RESIDUAL-3 附录）；②FEA-07 Residual 实际 `:377-387`、AC 行 `:297-304`；③`PerformanceBaselineTests.cs` 在 **`tests/NewManga.App.Tests/`**；④启动矩阵现 **10 项**（「9 项」陈旧）；⑤`WindowBroker.cs` 120 行、角色面 `:24-119` |

## 1. 逐 AC 三分类（关键结论）

| AC 子项 | 分类 | 证据锚点 |
|---|---|---|
| AC1 IME | **NA**（W-01） | 无可执行原生 IME 会话 |
| AC1 A03 真库 | **新做** | gated 真实 sidecar：`ChapterCreationTests.cs:161-254`、`RunControllerTests.cs:288-434`；**真库断言沿用内嵌 Python 读库**（`Fea11RunGrantIpcTests.cs:1030-1109`），**不引入 `Microsoft.Data.Sqlite`**；「真库」= 临时根下真实 SQLite（ADJ W-02） |
| AC1 ACK/Intent | **拆分**：本地去重可回填（`FEA04CurrentAdapterTests.cs:188-198`）；ACK 丢失/重连需新做 | `IntentCoordinator`、`RunStartAck` |
| AC1 阶段注入 | **回填 MET** | `FrontendSwitchCoordinatorTests.cs:48-54`（6 阶段 Theory） |
| AC2 owner | **新做**（Core 侧 `DraftLease.CanEdit` 已在，缺窗口层绑定/拒绝/转移） | `DraftCommands.cs:13`、`HostController.cs:2611-2639`、`DraftBuffer.cs:103-241` |
| AC2 生命周期 | **回填 MET**（+建议补窗口级断言） | `FEA04CurrentAdapterTests.cs:201-233` |
| AC2 双屏 / AC5 | **NA**（W-04/W-05） | 需交互式原生会话 |
| AC3 同进程恢复 | **回填 MET** | `PresentationHostCompositionTests.cs:125-155` |
| AC3 跨进程崩溃 | **新做（可做）** | 仓内无先例，但**FEA-11 的阻塞不迁移**（崩溃对象是 `switch-journal.json`，非 Core grant） |
| AC3 暂停期保护状态 | **新做 + 需先定义观测面** | 注入点 `FrontendSwitchCoordinator.cs:113` |
| AC4 planner/坏 JSON | **回填 MET** | `SafeStartupPlannerTests.cs:30-111`、`StartupCompatibilityMatrixTests.cs:46-127` |
| AC4 真实入口 | **新做** | 现矩阵只调 `App.CreateShell`，绕 `App.axaml.cs:39-120`；真进程先例 `tools/e2e/v2-launch-matrix.ps1:254-274`（但不含 `--presentation-host/--theme-home`） |
| AC4 坏包/scale | **新做（低成本纯单元）** | `corners.scale`=`AppearanceJson.cs:250-266`；9 类 warning 源齐全 |
| AC4 可诊断 | **需新做决策项**：`App.axaml.cs:78-86` 仅 `Trace`，**全 src/NewManga.App 无 TraceListener** | 建议加最小 `StartupDiagnostics` sink |
| AC6 p95 | **回填 MET**（阈值 1000ms=W-5 冻结，不得改）；历史 p95 236–712 ms（3x 波动）→ 建议 **3 次中位数** | `PerformanceBaselineTests.cs:27-33,151-156` |
| AC6 真实规模 | **新做** | `FakeHostController.ReadySnapshot(:1420)` 合成规模 |
| AC6 UI freeze | **新做 + 改口径**：`uiFreezeUpperBoundMs=ordered[^1]`（`:127`）是切换耗时上限，**不是** UI 线程调度间隔 | 需新指标 `uiThreadSchedulingGapMs`（心跳最大间隔） |
| AC8 | **回填 MET**（NA 只在 AC5 写一次） | 残项仅原生截图 |

## 2. AC2 语义冲突与冻结解释（DSH 已采纳）

- **冲突**：FEA-07 AC2 `:298`「第二窗口仅承载只读或独立会话内容」 vs C-13 SC-D03 `:60`（`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66`）「主画布与浮动面板共享 DraftId、均可编辑、单一串行队列、禁止自动合并」。
- **冻结解释**：
  - 「第二窗口」= **独立 OS 窗口**（`WindowBroker.WindowRole.Floating`）→ 按 AC2 只读或独立 Session；
  - 「同 Session 主画布 + 浮动面板」= **同一窗口内的浮动面板**→ 按 SC-D03 共享 DraftId 可编辑；
  - owner 键 = `(SessionId, RegionId)`；跨 Session 一律 ReadOnly；转移需显式请求。
- **只引用不复述** SC-D03（避免双权威，`FEA-C10-r1.md:83` 判例）。
- **无生产调用者**：`WindowBroker.RegisterSecondary` 当前零调用（全 src 仅 `PresentationWindow.cs:139` `RegisterMain`）。

## 3. AC3 跨进程崩溃最小方案（DSH 采纳）

外部驱动脚本（`verification/FEA-07-RESIDUAL-2/tools/crash-switch.ps1`）+ 两阶段 env-gated fact：park（production 路径在 `beforeJournalCommit`/staging 门禁处写 `park.json` 并阻塞）→ `Process.Kill(entireProcessTree:true)`（断言真死，exit code 10/11/12/2 语义）→ 新进程 recover（断言 journal `RolledBack`、frontend=上一已提交、appearance 未被 target 污染、二次恢复零变化）。**禁止** `Environment.FailFast`、同进程新 coordinator 冒充、生产 backdoor 开关。「暂停期保护状态」拆两条断言：切换零写保护列（内嵌 Python 读库逐列比对）+ 恢复采用最新状态（pause 后改 Lock/current 后，release 不回写旧快照且重新读取）。

## 4. AC4 / AC6 增量（DSH 采纳）

- **AC4**：新增最小 `StartupDiagnostics` sink（`App/Services/StartupDiagnostics.cs` + `App.axaml.cs` ≤5 行接线，写 `<log-dir>/startup.log`）；9 类 warning 逐项 fail-safe 单元矩阵；真实进程 `dotnet run ... --presentation-host=true --theme-home <tmp> ... --exit-after=4000`（新脚本，**不改 `tools/e2e/**`/`scripts/**`**）。
- **AC6**：p95 门槛 1000ms 不变，改「3 次独立运行 p95 中位数」；新增 `uiThreadSchedulingGapMs`（UI 线程心跳最大间隔，阈值由首轮基线定标后写死）；真实规模 N∈{50,200,500} 合成负载。

## 5. 拆分建议（DSH 采纳）

| 卡 | 内容 | 轮次 |
|---|---|---|
| **`FEA-07-RESIDUAL-2`（R4a，headless）** | AC2 owner + 生命周期断言、AC6 指标/规模、AC8 证据回填 | 1–2 |
| **`FEA-07-RESIDUAL-3`（R4b，gated/进程）** | AC1 A03/ACK、AC3 跨进程崩溃 + 保护状态、AC4 真实入口/矩阵/sink | 2–3 |

两卡均 0 pin；FEA-07 在**两卡都完成并 MET** 后翻 done。

## 6. 风险（评审）

R-1 复述 SC-D03 → 双权威（只引用）；R-2 AC2 不冻结解释 → Reviewer 必判 P1；R-3 改 `doc/plan/**`/`doc/contracts/**` 破 0 pin（ADJ 只 append）；R-4 gated 默认 skip 须带 reason 且不掩盖默认基线；R-5 AC8 不重复 NA；R-6 真进程测试无桌面会话须 default-skip 并分开记证据；R-7 AC6 单次 p95 flaky（3x 波动）；R-8 `Kill(entireProcessTree)` 语义/exit code 必须显式；R-9 写域 glob 只含 Broker + owner registry，勿碰 `Switching/**`。
