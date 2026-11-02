---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: 62fb6c5f5ac086fa5ab388736c2c87c2982b6544
decision: changes_requested
counts:
  P0: 0
  P1: 7
  P2: 5
---

# Review：FEA-07 实现复核 r1

## Reviewer 身份与来源

Reviewer 为本次 fresh Codex CLI 独立上下文；未参与 FEA-07 设计、范围冻结、实现或返修。辅助只读核查来源为同一 Review 派生的 `standards_review` 与 `spec_review` 子任务；均未写文件、未参与实现。固定审查 `cbfb7bbc9..62fb6c5f5`，提交内容与行号以 `git show 62fb6c5f5:<path>` 核对。审查期间工作树变化不纳入被审 head。

## 审查范围与 Reality Check

起始状态核对：`HEAD=62fb6c5f5ac086fa5ab388736c2c87c2982b6544`、分支 `main`、主仓库（`git common dir=.git`）、工作树 clean。`git diff --stat cbfb7bbc9..62fb6c5f5` 为 **53 files changed, 3880 insertions(+), 550 deletions(-)**。范围内未发现 Core、契约、schema、生成物、冻结设计或 Current V2 视觉改写；Fluent 改动以内容面抽取为主，Task 记载的 Fluent 24 项回归有证据通过。

之后工作树出现 4 个 tracked 修改：`App.axaml.cs`、`PresentationWindow.cs`、`PresentationHostCompositionTests.cs`、`PresentationWindowTests.cs`；另出现未跟踪 `verification/FEA-07/slice-6-gapclosing-verification.log`。这些不属于 `reviewed_head`，未纳入结论，也未被我修改。用户要求的 build/test 因此只能在出现这些改动后的工作树上运行，不能作为精确 head 的复跑证据。

## Standards

**executed**。W-1/W-6/W-10 和有效分层边界已核对。App→Presentation 引用在机械测试中获准，Host/CoreClient/ApplicationCore 的禁向检查确实解析 solution 项目引用；TFM 检查只读项目文件内显式 `TargetFramework`，未覆盖继承值，但本 diff 没有改 `Directory.Build.props`。`--shell=legacy` 仍在 `CreateShell` 中优先于 PresentationHost，启动矩阵也覆盖此语义。App glob 未用于视觉重做或页面业务重写。

## Spec

**executed**。AC1–AC8、W-1…W-10 与 Task 的 PARTIAL/MET 声明逐项对照。核心缺口是 AC1 的真实状态保留/阶段验收、AC2/AC3 未接入进程运行路径、AC4 fallback 行为不符、AC5 拓扑规划未接线、AC8 的用户目录隔离证据。

## AC 逐条结论

| AC | Review verdict | 核对结果 |
|---|---|---|
| AC1 | **PARTIAL** | 所称 100 次循环使用 `Border`/`TextBlock` 内容工厂，只验证 coordinator 和 journal；真实 V2/Fluent factory 没有 100 次保真循环。Fluent 每次重建都生成新 Workbench session ID。`Layout/Loaded/Rendered` 在事务中是 `NoOpAsync`，不能证明真实呈现门槛及焦点/输入/窗口材质回滚；DB/current/pinned revision/Lock/source/candidate、IME、ACK/Run 矩阵均无证据。 |
| AC2 | **PARTIAL** | `WindowBroker`、`ExitCoordinator` 各自逻辑有单测，但在被审 head 的生产 App 路径无调用；Broker 只登记 token，不含 `(SessionId, RegionId)` 写 owner。主窗关闭仍直接触发 `ShutdownMode.OnMainWindowClose`。 |
| AC3 | **PARTIAL** | journal 原子写与中断查询有单测，`TryRecoverInterrupted` 未从启动路径调用。journal 不记 previous/last committed frontend；持久化新设置后、journal commit 前崩溃，无法恢复上一已提交 UI。 |
| AC4 | **PARTIAL（Task 标为 MET 不成立）** | Planner 只将 frontend selector fallback 标成 `IsFallback`；外观 warnings 只加入 Diagnostics。App 随后重新调用 `FrontendSelector.Select`，没有使用 planner 的 `EffectiveFrontendId`。所谓视觉主题回退测试实际传入 `--frontend=builtin.fluent-dark`，测的是未知 frontend，不是坏 `theme.visualThemeId` 或 scale。 |
| AC5 | **PARTIAL / BLOCKED** | 原生双屏/拔屏/DPI 矩阵诚实标为 D-1 blocked；PerMonitorV2 清单断言及纯拓扑规划单测存在。但 memento 启动恢复直接采用保存的坐标，`DisplayId` 捕获为 null，生产启动/拓扑变化未调用 `DisplayTopologyPlanner.Clamp`。 |
| AC6 | **PARTIAL（Task 标为 MET 过宽）** | `performance-baseline-release.json` 的 p95 `429.47 ms` 与测试 `p95 <= 1000 ms` 硬断言一致，W-5 的 1000 ms 门槛没有降低。测试为 headless + `NullHostController`，无合成规模工作负载，也没有独立最大 UI freeze 指标；另有 Release/Debug 摘要值混用。 |
| AC7 | **MET（留精确 head 复跑限制）** | 启动矩阵覆盖默认 V2、frontend、unknown fallback、legacy 优先；ProjectReference 方向门禁确实检查指定边；`--shell=legacy` 语义保持。归档基线为 1099/0/57。当前运行是含并发未提交改动的 1102/0/57，不能替代指定 head 的复跑。 |
| AC8 | **PARTIAL** | 9 个 canonical evidence 路径均存在，SHA-256 全部匹配 Task pin。原生矩阵、evidence-index 和两项生成器 `--check` 结果未见归档。另有启动矩阵可能写入真实 `%APPDATA%` 的隔离缺口（R-006）。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 最小返修建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P1 | `FrontendSwitchCoordinator.cs:66-73,147`; `FrontendHostCoordinatorTests.cs:145-159`; `App.axaml.cs:210-223`; `FluentShellSurface.axaml.cs:105-108` | AC1 的 100 次用例 factory 是占位控件；生产 factory 每次新建 V2/Fluent 内容树，Fluent Workbench 还生成新的 Guid session。切换会丢失页面/会话状态，不能证明 Draft/Run/Intent 不变。真实 Layout/Loaded/Rendered 阶段为空操作。 | 固定 head 的 100 次测试只断言占位树与 journal；性能用例最多测 12 次真实 factory 切换，未断言 Session/Draft/Run/Intent；阶段表直接指向 `NoOpAsync`。 | 复用或共享前端会话状态；以真实 factory 做至少 100 次切换并验证 Host/Session/Draft/Run/Intent 与数据零变化；将布局、Loaded、首帧/有效几何验收接入事务和阶段失败回滚。未做的 IME/ACK/真库矩阵继续 BLOCKED。 | open |
| R-002 | P1 | `PresentationWindow.cs:60-66`; `WindowBroker.cs:24-84`; `ExitCoordinator.cs:11-84`; `App.axaml.cs:90-91` | AC2 组件未接入生产路径。Broker 只是 token 登记，不能承载实际窗体归属或相同 `(SessionId, RegionId)` 单写 owner；ExitCoordinator 未阻止带未保存编辑/Run 的进程退出。 | 固定 head 的 `PresentationWindow` 只创建 `FrontendHostCoordinator`；App 仍设置 `OnMainWindowClose`。生产源码没有 Broker/ExitCoordinator 调用。 | 将 broker/退出协调接入组合根和真实 Window 生命周期；实现并测试单一 write owner、关闭/重建不释放 Host、不隐式 Start，以及未保存编辑/Run 阻断退出。 | open |
| R-003 | P1 | `App.axaml.cs:206-227`; `FrontendSwitchCoordinator.cs:47-48,76-99`; `SwitchJournal.cs:7-12` | AC3 没有启动恢复。App 只创建并传递 journal；journal 只有 target/stage，没有 previous 或 last committed frontend。若在 `AppearanceCoordinator.SaveAsync` 写入 target 后、journal commit 前进程中断，重启无法选择上一已提交 UI。 | `git show 62fb6c5f5:.../App.axaml.cs` 的启动段无 `TryRecoverInterrupted`；保存设置发生在 `FrontendHostCoordinator.cs:95-103`，journal commit 在事务随后阶段。 | 在 shell/selector 决策前读取 journal，持久化 last committed frontend；对 interrupted 状态确定性 rollback 到上一已提交 UI，并加入跨进程崩溃/重启测试。 | open |
| R-004 | P1 | `SafeStartupPlanner.cs:45-65`; `App.axaml.cs:74-88`; `SafeStartupPlannerTests.cs:60-67`; `StartupCompatibilityMatrixTests.cs:75-77` | AC4 错误标 MET。外观 warning 不会令 `IsFallback=true`，App 也绕过 planner 的 effective result 重新选择 frontend。测试将 `builtin.fluent-dark` 当作 frontend 参数，未测试 persisted `VisualThemeId` 或 scale 异常；坏视觉设置时仍可能进入 Fluent。 | 用 `FrontendId=builtin.fluent` 且 `VisualThemeId`/scale 非法的真实 AppearanceSettings/JSON 可看到 planner 仅记录 warning，未执行 Current V2 fallback。 | Planner 成为组合根唯一决策源；真实坏 JSON、未知 visual theme/scale/包测试证明 fail-safe 到 Current V2 且保留有效设置；修正 AC4 状态。 | open |
| R-005 | P1 | `PresentationWindow.cs:46-52,74-82`; `App.axaml.cs:225-227`; `DisplayTopology.cs:53-80` | AC5 的拓扑算法未接入。保存位置被直接赋回，DisplayId 永远捕获为 null；显示器变化后主窗可能落在屏外。纯 planner 单测不能证明生产恢复安全。原生矩阵另仍 BLOCKED。 | 固定 head 的 memento restore/capture 段没有枚举显示器或调用 Clamp；`DisplayTopologyPlanner.Clamp` 仅在测试/定义里出现。 | 启动和拓扑变更时枚举当前显示器并 clamp，保存实际 DisplayId；加无效/离屏 memento 的 App 接线测试；继续将原生 100/125/150/200% 矩阵标为 BLOCKED，直到真机证据。 | open |
| R-006 | P1 | `StartupCompatibilityMatrixTests.cs:54-59,88-95`; `ThemeHome.cs:43-59`; `App.axaml.cs:225-238` | W-9/AC8 隔离失败。启动矩阵没有传 `--theme-home`，`ThemeHome.Resolve` 返回 `%APPDATA%/NewManga`；关闭 PresentationWindow 会调用 `WindowStateMementoStore.Save` 到 `window-state.json`。本次全量测试运行了该用例，故可能触达/覆盖真实用户窗口状态。 | 测试 `Create()` 对所有参数调用默认 `ThemeHome.Resolve(options)`；Presentation case 随后 `Close()`；生产关闭回调保存 memento。测试源码未见 APPDATA 临时重定向。 | 所有测试参数显式使用 `_root` 下的 `--theme-home`，断言 journal/memento/theme 路径均位于临时根并对默认 `%APPDATA%` 路径作零写入断言。该风险已发生于本次测试调用；我未检查或修改用户目录内容。 | open |
| R-007 | P1 | `doc/tasks/FEA-07.md:6-23,202-210`; `doc/STATUS.md:7-10`; `doc/REBASELINE_PLAN.md:21,36` | Task 尚未进入正式 Review 状态：卡为 `in_progress`、`reviewer:null`、`delivery_head:null`、`canonical_evidence_status:pending`，且未见 FEA-07 handoff。STATUS/PLAN/LEDGER 当前均一致地指向 in_progress、READY 为空，但这不满足进入集成验证所需的 review/delivery/evidence 生命周期固定。 | 对照 Task frontmatter、当前指针和 handoff 列表；9 条 evidence 虽有 hash，delivery head 与 reviewer 元数据仍空。 | DSH 在处置本 Review 后登记 reviewer/source、固定 delivery_head，补齐 handoff 与 canonical evidence 状态；再按治理检查器复核，集成前不得把 in_progress 当作 approved。 | open |
| R-008 | P2 | `doc/tasks/FEA-07.md:24-45`; `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs:50-55,109-112`; `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:1` | 写域清单与 diff 不一致：`AppOptions.cs` 和 `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` 不在 `allowed_paths`。W-8 明确要求滚动 checkpoint，故 checkpoint 属清单遗漏；`AppOptions.cs` 的 parser 开关改动则未列入允许路径。 | `git diff --name-only cbfb7bbc9..62fb6c5f5` 的越界项为这两条；其他实现、测试、Task、状态、证据路径在允许 glob 内。 | DSH 记录对 `AppOptions.cs` 的范围处置；后续授权需同时把必要文件写入 `allowed_paths`。将 checkpoint 的显式 W-8 需要与允许路径清单对齐。 | open |
| R-009 | P2 | `PerformanceBaselineTests.cs:63-70,86-124`; `performance-baseline-release.json:11-28`; `performance-baseline-debug.json:11-28`; `doc/tasks/FEA-07.md:148` | AC6 只测 headless shell 构建/切换时间，没有独立 UI freeze，也没有实际规模合成数据（使用 `NullHostController`）。JSON release p95/硬断言一致且低于 W-5；但 Task 把 Debug 的 `+1,384,880 bytes / +3 handles` 写成 Release，Release JSON 实为 `+1,363,264 bytes / 0 handles`。 | 对照测试 config、两 JSON 与 Task 汇总；W-5 仍是 p95 ≤1000ms，未发现降门槛。 | 补实际规模合成 workload 和 UI freeze 计量；按 Release/Debug 分开更正摘要，或将 AC6 降为 PARTIAL。 | open |
| R-010 | P2 | `FluentShellSurface.axaml.cs:105-108`; `FluentPageViewModels.cs:88,1053` | 重复切换创建新 Fluent ViewModel；ShelfVM 订阅常驻 Host 的 `Changed`，SettingsVM 订阅常驻 Appearance 的 `Changed`，未见对应退订/Dispose。长期事件源会保留旧 VM/handler，切换次数增加时累积通知与内存开销。 | 两个长寿命 publisher 持有订阅，factory 每次创建新模型；12 次 baseline 未断言订阅或存活对象稳定。 | 为内容树提供显式生命周期/Dispose 并解绑，或复用这些 VM；补重复切换后的订阅/存活对象稳定断言。 | open |
| R-011 | P2 | `verification/FEA-07/slice-5-verification.log:2-10`; `verification/FEA-07/performance-baseline.md:3-10`; commit `0967c5a05` | 证据未精确绑定被测代码快照：slice-5 日志和摘要记录 `head=318fd34f2`，而 `PerformanceBaselineTests.cs`、`ArchitectureDependencyTests.cs` 首次加入的是其后子提交 `0967c5a05`。日志也没有 shell/解释器头。当前能确认 pin 文件字节未变，不能从日志证明测试针对所交付源快照运行。 | `git log --follow` 显示测试文件首次提交为 `0967c5a05`；日志第 3 行仍列父提交 `318fd34f2`。 | 在干净、精确的 candidate head 重跑并归档含命令、shell/解释器、commit 与 exit 的完整日志；测试结果与源快照绑定。 | open |
| R-012 | P2 | `doc/tasks/FEA-07.md:163,191-195`; `verification/FEA-07/` | AC8 要求两项生成器 `--check` 输出，但 FEA-07 证据目录及 slice logs 未找到对应结果；Task 已如实将 AC8 标 PARTIAL，但该项未被单独标为 NOT_RUN。 | 对 `verification/FEA-07/**` 搜索未发现 `--check` 结果或 artefact。 | 将两个生成器的 `--check` 命令/exit/结果归档；不能补证时明确登记 NOT_RUN，并保持 AC8 PARTIAL。 | open |

## 范围、证据与治理核对

- **范围**：`App/Views/**` 仅用于 Fluent 内容面抽取和 Presentation 接线；`FluentShell` facade 下的 24 个既有 Fluent 测试在切片证据中通过。无 Core、契约、schema、生成输出或冻结设计 diff。两个写域偏差见 R-008。
- **AC1/AC2/AC3 证据真实性**：100 次仅占位 factory；阶段测试打到空步骤；WindowBroker/ExitCoordinator 是单测逻辑未接线；journal 启动恢复不存在。卡内 PARTIAL 对部分限制诚实，但不能把这些测试解释为完整 AC 验收。
- **AC5**：原生验收确实记录 D-1 BLOCKED，没有以 headless 代替原生；拓扑 planner 接线缺口另见 R-005。
- **AC6/W-5**：Release JSON `p95Ms=429.47`、`budgetP95Ms=1000`、`passed=true` 与源码断言相符；W-5 未下调。AC6 其余指标不足及摘要值错配见 R-009。
- **AC7/跳过项**：冻结证据为基线 `1034/0/57`、FEA-07 `1099/0/57`，净增 65 passed、fail/skip 不变。当前运行结果是 **1102/0/57**（总计 1159），比被审证据多 3 个 passed；对应运行期间出现的 3 个未提交测试，不能回填为 reviewed_head 结果。57 skips 分组为 Host 28、CoreClient 22、App 7；Fact 属性因 sidecar 或 BOOK/S4 seeded fixture 不可用而跳过，与基线同类；历史 slice 日志另记 CoreClient 时间敏感首跑 1 failed、隔离重跑通过，本次运行 0 failures。
- **证据 pins**：9/9 Task canonical paths 存在且 SHA-256 与 Task 表逐项匹配。`check.ps1` 与 `verify_pins.ps1` 均通过；机器检查不替代上述语义发现。
- **治理指针**：STATUS、PLAN、LEDGER 均指向 FEA-07 `in_progress`；READY 为空；scope approval、owner、base commit 一致。reviewer、delivery_head、canonical 状态缺口见 R-007。未发现远端跟踪分支包含 `62fb6c5f5`；本次未执行 push。
- **工作树边界**：起始时 clean；之后并发变化如“Reality Check”所列。精确 head 的源码行号按 commit 内容读取。因只获准写本报告，没有重置、覆盖、暂存或清理这些外来变化。

## 验证记录

| 场景 | 命令/步骤 | 环境与结果 | 证据/适用边界 |
|---|---|---|---|
| 固定 head / 初始状态 | `git rev-parse HEAD`; `git status --short`; `git branch --show-current`; `git rev-parse --git-common-dir` | 起始 PASS：`62fb6c5f5...`、clean、`main`、`.git` | 随后出现前述并发工作树变化；固定源码仍用 `git show` |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | PASS，0 warnings / 0 errors | 在出现 4 个 tracked 修改后运行；非精确 reviewed_head 复跑 |
| Full tests | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | PASS，当前工作树 1102 passed / 0 failed / 57 skipped | 和固定 head 证据 1099/0/57 相差 3 个新增未提交测试；57 skips 原因同上；用例可能写真实 AppData（R-006） |
| Governance | `pwsh -NoProfile -File tools\governance\check.ps1` | PASS，3 warnings：10 个非终态 Task、STATUS/PLAN 达预算 80% | 工具输出只读，不判定语义 |
| Pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | PASS，15/15 | FEA 合同 pins；另独立核过 FEA-07 的 9 个 SHA |
| 原生矩阵 | Windows 原生双屏/拔屏/DPI 100/125/150/200% | BLOCKED（D-1，无硬件） | `verification/FEA-07/slice-4-verification.log` |
| 生成器 `--check` | 检索 Task 引用的两个生成器结果 | NOT_RUN / 未归档 | AC8 要求未有对应 artefact；见 R-012 |
| 精确 reviewed_head build/test | 未执行干净复跑 | NOT_RUN | 并发工作树改动出现后，为保留他人内容未重置或创建额外 worktree；当前运行不能代替精确 head |

## 结论与返修集

**Decision: `changes_requested`（P0=0 / P1=7 / P2=5）。不建议进入 DSH 集成验证。** P1 涉及切换状态丢失、窗口/退出/崩溃恢复未接线、safe-startup fallback 不符、拓扑恢复不安全、测试可能写真实用户目录，以及 Task Review 生命周期和测试源快照证据未固定。现有 1099/0/57、W-5 p95 数值和 9 个 evidence SHA 有效，但不足以解除这些阻断。

最小返修顺序：

1. 修复 StartupCompatibilityMatrix 的 `--theme-home` 隔离并加真实路径断言；确认并记录本次可能影响的 `window-state.json` 状态，由数据所有者按需恢复。
2. 接通并测试 AC1–AC5 生产路径：真实树状态保留与失败回滚；Broker/ExitCoordinator 与写 owner；启动 journal 恢复；坏主题/scale fail-safe；memento 的 DisplayId/clamp。无法原生验收的部分继续 BLOCKED。
3. 补 AC6 freeze/workload 指标并修正 Debug/Release 汇总；处理 Fluent VM 的事件解绑。
4. 补齐或登记生成器 `--check` artefact；在干净精确 head 重跑 build/test，保存含 shell、解释器、commit、exit 和逐项 skip 原因的证据；绑定测试日志与被测源码快照。
5. 由 DSH 处置 allowed_paths 偏差，登记 reviewer、delivery_head、handoff 与 canonical evidence 状态，再运行治理检查并请求新 head 的独立复审。

## 边界声明

本 Review 只覆盖 `cbfb7bbc9..62fb6c5f5` 的已提交实现；不审查期间出现的未提交/未跟踪实现，不重审 scope-r2 的设计数值，不因已有部分测试或 W-5 PASS 而降低 AC/原生验收判据。我未通过编辑或补丁改动源码、Task、契约、STATUS、PLAN、LEDGER 或证据，没有 commit/push；本 Review 是唯一主动编辑的仓库文件。`dotnet build/test` 产生构建/临时输出；测试可能写入的 `%APPDATA%\NewManga\window-state.json` 另见 R-006，实际文件状态未检查或恢复。

## Review 后仓库变更边界

本报告写作期间 `main` 前进至 `3cf03ff581b4c7552dba9a91e785c00d4f854c51`（`docs(fea-07): 证据索引（SHA-256/基线/生成物/性能/复核状态）`）。该提交及 `62fb6c5f5..HEAD` 后续变化不属于本次审查；本报告只对 front matter 中的 `reviewed_head=62fb6c5f5...` 有效。新 head 需按新交付重新独立复核。


