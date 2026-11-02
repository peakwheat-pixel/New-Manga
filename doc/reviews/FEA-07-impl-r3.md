---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r3）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: b3fa8dc0c2805f8790061b4d562af7c16ec71122
code_head: 3220abd599aed7e835fc1352a25f8e1f5c214a58
decision: changes_requested
counts:
  P0: 0
  P1: 5
  P2: 2
---

# Review：FEA-07 实现复核 r3

## Reviewer 身份与来源

本报告由用户指定的 fresh Codex CLI 独立上下文撰写；未参与 FEA-07 设计、范围冻结、实现或返修，也未委派子任务。本审查只读；唯一新增文件为本报告，未修改代码、任务卡、状态、证据或用户数据，未 commit/push。

## 范围与 Reality Check

- 复核基线为 `cbfb7bbc92d489541a24290038eae2117f8aa1ce`，文档/证据 reviewed head 为 `b3fa8dc0c2805f8790061b4d562af7c16ec71122`，实际代码 head 为 `3220abd599aed7e835fc1352a25f8e1f5c214a58`。代码判断及行号均以 `3220abd59` 为准。
- 开始时 `git rev-parse HEAD` 为 `7b62c492bfb436416293d50c1725331cf5a98c3a`，分支 `main`，当前 checkout 的 common dir 为 `.git`，`git status --short` 为空。`3220abd59..HEAD` 仅有 Task/证据索引与 checkpoint 文档差异；`b3fa8dc0c..HEAD` 仅有 5 行 checkpoint 增量，不改变代码或证据内容。仓库另有其他 linked worktree；本次未进入或修改它们。
- `git diff --stat cbfb7bbc9..b3fa8dc0c`：65 files changed，4903 insertions(+)，553 deletions(-)。变更路径落在 FEA-07 Task 的 `allowed_paths` 内；没有发现新增越界路径。
- 当前 checkout 的代码与 `3220abd59` 一致。r2 的 `rework-part2-verification.log` 记录的是提交前 `ddef44f81` 的 uncommitted rework；其精确提交后证据由 `final-evidence.log` 绑定至 `3220abd59`。

## r2 findings 闭环表

| ID | r2 级别 | r3 结论 | 核对依据与残余 |
|---|---:|---|---|
| R-001 | P1 | **未闭环，P1 保留** | 100 次真实内容树切换与同实例检查已补；Fluent `CurrentPage` 和 V2 `Tag` 有保留断言。但 `Tag` 是测试标记，不是 Session/Draft/Run/Intent；内容树在 commit 前没有挂入 `FrontendContentHost`。`Layout` 只手工 `Measure/Arrange`，`Loaded`/`Rendered` 只是排队空回调，不能证明真实内容完成加载或渲染。AC1 必须保持 PARTIAL。详见下方 R-001。 |
| R-002 | P1 | **未闭环，P1 保留** | Fluent 设置 dirty/Workbench Running 与 V2 ImportDock 状态已实现 `IPresentationExitState`；`Closing` 也查 live 接口和 `ExitCoordinator`。但只查询当前树，缓存隐藏树的编辑/运行状态被漏掉；`AppShellV2.HasUnsavedEdits` 还固定返回 `false`，没有覆盖 V2 Theme Studio 的 `HasDraft`。生产代码没有状态变化时注册 ExitCoordinator token。详见 R-002。 |
| R-003 | P1 | **r2 finding 闭环；AC3 仍 PARTIAL** | journal 已保存 `PreviousFrontendId`；`App.OnFrameworkInitializationCompleted` 在 planner 前调用恢复；设置已写 target、journal 仍 in-flight 时恢复 previous 的逻辑和测试存在。暂停期间保护状态变化与真实进程中断仍未验，Task 如实标 PARTIAL。另有 journal 最终提交失败后的运行期一致性新问题 R-015。 |
| R-004 | P1 | **r2 finding 闭环；AC4 仍 PARTIAL** | 组合根直接赋值 `startupPlan.Selection`，fallback 警告会强制 Current V2（含显式 CLI Fluent）；损坏 JSON 测试将 planner 的 Selection 传给 `App.CreateShell`。该测试没有走 `OnFrameworkInitializationCompleted`，坏包/scale 的 App 入口矩阵也未覆盖，Task 继续标 PARTIAL 是准确的。 |
| R-005 | P1 | **代码接线闭环；AC5 PARTIAL/BLOCKED 如实** | 最大化状态现由窗口构造恢复；屏幕 clamp、PerMonitorV2 机械检查存在。双屏/拔屏/DPI 原生矩阵仍为 D-1 BLOCKED，没有以 headless 结果代替原生验收。 |
| R-006 | P1 | **闭环** | 启动矩阵使用临时 `--theme-home`；新测试使用临时目录。当前测试运行未触碰真实 AppData。 |
| R-007 | P1 | **未闭环，P1 保留** | `delivery_head=3220abd59` 正确；Task reviewer 仍指 impl-r2，唯一 handoff 文件标题仍为 impl-r1/待 r2 复核，索引仍写“r3 待派”，与本次已发生的 r3 appointment 不一致。`canonical_evidence_status=pending` 在本次尚未裁决前合理；STATUS/PLAN/LEDGER 均指向 FEA-07 `in_progress`，STATUS/PLAN/索引测试数均为 1113/0/57。详见 R-007。 |
| R-008 | P2 | **闭环** | `cbfb7bbc9..b3fa8dc0c` 变更均匹配 Task 的允许路径。 |
| R-009 | P2 | **未完全闭环，P2 保留** | JSON、性能摘要和索引均为 Release p50 99.91 / p95 344.93 / max(UI freeze 上限) 344.93 ms / memory +208B / handles 0；但 Task AC6 验收行仍写旧 p95 `429.47ms`。AC6 保持 PARTIAL 正确，卡内数值需统一。 |
| R-010 | P2 | **闭环** | 组合根每种 frontend 缓存一棵真实内容树；100 次测试确认复用，没有观察到每次切换持续新建树/订阅的增长。 |
| R-011 | P2 | **SHA 自引用问题闭环** | `evidence-index.md` 不再给自己列 SHA；Task canonical evidence 的 13 个文件 pin 均与实测匹配。发现索引说明含 form-feed 控制字符，另列为新 P2 R-016。 |
| R-012 | P2 | **闭环** | `generators-check.log` 在索引与 Task pin 中一致，final evidence 记录 TokenGen/ThemeGen 检查 exit 0。 |
| R-013 | P1 | **部分闭环，P1 保留** | `_switchGate` 在 no-op 判断、`CurrentFrontendId`/UI/settings 快照与事务之前取得，覆盖范围正确。并发测试检查两个请求均成功、最终当前前端/内容对应第二个请求且 journal 清理；没有确定性同步点或失败注入，未实测“第一事务失败回滚时第二事务已排队”这一过期回滚路径。代码中未见锁顺序反转或同步等待 UI dispatcher 的直接死锁/重入路径。详见 R-013。 |
| R-014 | P2 | **闭环** | `PresentationWindow` 从 memento 应用 `WindowState.Maximized`；`MaximizedMemento_IsRestored` 断言窗口状态与捕获值。 |

## AC 逐条 Verdict

| AC | Verdict | r3 依据 |
|---|---|---|
| AC1 | **PARTIAL** | `RealContentRoundTrips...` 使用真实 `FluentShellSurface`/`AppShellV2` factory，50 轮各切换两次，共 100 次切换；Fluent Workbench 页、V2 测试 Tag、树实例和 Window 身份断言有效，但 V2 Tag 不是业务状态。没有 Session/Draft/Run/Intent/DB/current/pinned/Lock/source/ACK 链路；replacement 未附加时的 dispatcher 优先级回调不构成真实 Loaded/Rendered。失败注入测试覆盖协调器阶段回滚，但不证明完整焦点、输入路由、材质/bounds 与旧资源恢复。 |
| AC2 | **PARTIAL** | Fluent 的设置草稿/Workbench 状态及 V2 ImportDock 状态有 live 属性，`Closing` 同时查询 live 与 ExitCoordinator；不过只查当前内容树，隐藏缓存树状态漏检，V2 Theme Studio draft 未纳入，真实 broker 窗口归属/单写 owner/Host 生命周期仍未集成。 |
| AC3 | **PARTIAL** | previous journal 与 target 已持久化崩溃窗口恢复已实现并测试，恢复发生在启动选择之前；暂停期间保护状态变化和真实跨进程 kill 仍待补。journal 最终写失败时的运行期状态回滚也未覆盖（R-015）。 |
| AC4 | **PARTIAL** | Planner Selection 直接进入组合根，坏 appearance warning 会强制 Current V2（含 CLI Fluent）。损坏 JSON 测试为 Planner → `App.CreateShell`；未运行真正 `App.OnFrameworkInitializationCompleted` 组合路径的测试，也无坏包/scale App 矩阵。Task PARTIAL 口径准确。 |
| AC5 | **PARTIAL / 原生矩阵 BLOCKED** | memento/clamp/PerMonitorV2/最大化恢复均有代码与 headless 证据；原生双屏、拔屏与 100/125/150/200% DPI 尚未测。Headless geometry fallback 不能代替真实窗口布局。 |
| AC6 | **PARTIAL** | Release baseline p95 344.93 ms 低于 W-5 的 1000 ms；memory +208B、handles 0。UI freeze 是事务时长上限估计而非真实帧冻结测量，真实规模 workload/真机指标待补；Task AC6 行仍有旧 p95。 |
| AC7 | **MET（headless/机械范围）** | 本次全量测试 1113/0/57；build 0/0。启动兼容和依赖门禁测试在套件中。此 verdict 不扩展为 AC4 的真实 App 初始化覆盖。 |
| AC8 | **PARTIAL** | 测试根与主要 evidence pins 可核验，native 矩阵仍 blocked；索引自 pin 已移除，但索引摘要存在控制字符路径损坏（R-016）。 |

## Findings

| ID | 级别 | 文件/行（按 3220abd59） | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P1 | `FrontendHostCoordinator.cs:105-108,147-170`；`PresentationHostCompositionTests.cs:145-190` | 新树 commit 前未放入视觉树；Loaded/Rendered 是空 dispatcher 回调，Layout 用手工 Measure/Arrange 与 1024×640 fallback。无 bounds 的 headless/窗口尚未 layout 场景也会放行，无法证明真实几何、Loaded、frame render 后才提交。 | 组合测试没有 `Show()` 窗口；`ValidateLayout` 在 host bounds 为零时使用 fallback；`RenderedAsync` 仅 `InvokeAtPriorityAsync(Render)`。 | 用可观察的真实宿主加载/渲染完成信号作为门禁，另测有效/无效几何与逐门失败回滚；继续把未覆盖数据状态如实留为 PARTIAL。 | open |
| R-002 | P1 | `PresentationWindow.cs:102-112`；`App.axaml.cs:216-238`；`AppShellV2.axaml.cs:81-85`；`ThemeStudioViewModel.cs:171-172` | 切换后隐藏树仍缓存，但关闭只读 `ContentHost.Current`，没有查询缓存树或把工作状态注册进 ExitCoordinator；从 Fluent 离开 dirty Settings/运行中 Workbench 后，在 V2 关闭会漏拦。V2 `HasUnsavedEdits` 固定 false，而 Theme Studio 有 `HasDraft`，也可能漏拦。 | `App` 保留两种 frontend 内容树；`OnClosing` 只 cast 当前树；V2 明确返回 false；Theme Studio ViewModel 暴露 `HasDraft`。现有 Closing 测试使用假 `ExitBlockingControl`，没有验证生产 surface。 | 对所有缓存内容树聚合 live edit/run，或在状态变化时注册/完成 ExitCoordinator token；把 V2 Theme Studio draft 纳入并添加生产内容树切换后关闭的测试。 | open |
| R-007 | P1 | `doc/tasks/FEA-07.md:10,20-22`；`doc/handoffs/FEA-07-impl-r1.md:1`；`verification/FEA-07/evidence-index.md:1` | Review 生命周期指针滞后：Task reviewer 是 impl-r2；现存 handoff 标题为 impl-r1/待 r2；索引说 r3 待派。此时本次 r3 已实际执行，之后无法只凭这些字段确认最新 appointment/交付记录。`delivery_head`、测试数、STATUS/PLAN/LEDGER 状态正确；canonical status pending 可保留至 DSH 处置。 | `rg --files doc/handoffs` 仅有 `FEA-07-impl-r1.md`；Task 和索引的上述字段可直接复核。 | DSH 处置本 Review 后更新 Task reviewer/source 与报告指针，生成引用精确 delivery commit 的 handoff；按处置结果更新 canonical evidence 状态与索引。Integration 前保持 Task `in_progress`。 | open |
| R-013 | P1 | `FrontendHostCoordinator.cs:29,70-145`；`PresentationWindowTests.cs:206-219` | 串行门的生产代码范围已正确，但并发测试未确定性制造事务重叠/第一请求失败，因此没有证明无过期快照回滚；目前只证明一次 back-to-back 双请求的成功终态。 | 测试只启动两次调用、`Task.WhenAll` 并断言成功、最终 V2、内容 V2、journal 不存在；没有 TCS/barrier 或失败注入。 | 加确定性 barrier：第一请求持有门并在 commit/保存阶段失败，第二请求排队；断言两个响应、UI、`CurrentFrontendId`、appearance 持久值和 journal 一致，且失败回滚没有覆盖后续状态。 | open |
| R-015 | P1 | `FrontendSwitchCoordinator.cs:108-117`；`FrontendHostCoordinator.cs:108-133` | journal 的最终 `Commit()` 在 app Commit callback 已持久化 target 且已把 `_currentFrontendId` 设为 target 后执行。若 journal Commit 写入失败，catch 会 journal Rollback 并调用只恢复 Host 内容的 `RollbackAsync`；不会恢复 appearance 或 `_currentFrontendId`。可能返回失败但持久值/current id 是 target、显示内容是 previous。若 journal Rollback 自身也失败，rollback callback 不会执行。 | 故障路径可由代码顺序确认；现有 `FailureAtAnyStage` 在 Commit callback 前注入，未覆盖 journal 最终 Commit I/O 失败。 | 将 journal finalize 与 app 持久状态作为一个可补偿事务处理：所有失败路径都恢复内容、settings 和 current id；保证 journal 写失败不跳过 UI rollback；增加 final journal write/rollback fault tests。 | open |
| R-009 | P2 | `doc/tasks/FEA-07.md:196` | AC6 验收行仍记 Release p95 `429.47ms`，而当前 release JSON、summary、索引和实现记录均为 `344.93ms`。 | `performance-baseline-release.json` 的 `p95Ms/maxMs=344.93`；`performance-baseline.md:9`、Task `:150,229` 与索引摘要一致；Task `:196` 为旧值。 | 更正 AC6 行旧数值，并让 Task 所有性能数字保持同一 Release baseline。 | open |
| R-016 | P2 | `verification/FEA-07/evidence-index.md:1` | 索引说明中 `与 \final-evidence.log` 的首字符是实际 form-feed（U+000C），导致引用路径不是可读的 `final-evidence.log`。表格行自身路径正确，Task pin 与 SHA 不受影响。 | 读取文件原文发现控制字符；文件不列自身 SHA，13 个 Task canonical evidence hashes 匹配。 | 将控制字符替换为正常路径文本，复核索引格式与引用。 | open |

## 证据与治理核对

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定 reviewed/code head 与工作区 | `git rev-parse HEAD`、`git status --short`、`git log --oneline -8`、`git diff --name-only 3220abd59..HEAD` | PowerShell；当前 HEAD `7b62c492b`，代码 `3220abd59` | PASS；工作区 clean；HEAD 后只文档/checkpoint | 当前 Git 输出；`3220abd59..HEAD` 无源码路径 |
| 复核范围 | `git diff --stat cbfb7bbc9..b3fa8dc0c` | base `cbfb7bbc9` → reviewed head `b3fa8dc0c` | PASS；65 files，4903 insertions，553 deletions；路径符合 Task allowlist | 当前 Git 输出、`doc/tasks/FEA-07.md:24-47` |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | Windows / .NET 10.0.401；当前源码与 `3220abd59` 相同 | PASS；0 warnings / 0 errors | 本次运行输出 |
| 全量测试 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | Windows / `3220abd59` code tree | PASS；1113 passed / 0 failed / 57 skipped。skip：Host 28（sidecar 环境未设置）、CoreClient 22（sidecar 环境未设置）、App 7（BOOK/S4 fixture 不可用） | 本次运行输出；计数与 `final-evidence.log`、STATUS、PLAN、索引相符 |
| 治理指针 | `pwsh -NoProfile -File tools\governance\check.ps1` | 当前仓库 | PASS；3 warnings（10 个非终态 Task、STATUS/PLAN 预算告警） | 本次运行输出；warning 不代表本 Task 验收失败 |
| 冻结 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 当前仓库 | PASS；15/15 | 本次运行输出 |
| FEA-07 canonical artifact pins | 对 Task canonical evidence 表逐项 `Get-FileHash -Algorithm SHA256` | 当前文件 | PASS；13 个 pinned artifact 均匹配 | Task `:233-249`；final `4ab4386d…`，part2 `725ec7f6…`，Release perf `5dd4c897…` |
| 精确最终证据 | 检查 `final-evidence.log` 与索引记录 | head `3220abd59` | PASS；日志 head、Task final pin、索引 SHA 一致；实测 SHA-256 为 `4ab4386db8503a70ade78679ccaf4edf507378f6bdbe157529d423d0e77c58de` | `verification/FEA-07/final-evidence.log`；Task `:248`；索引 `:1-2` |
| r2 返修日志 | 检查 `rework-part2-verification.log` | 日志 head `ddef44f81`（提交前 rework） | PASS（作为返修过程证据）；它不是精确 delivery head 的最终证据 | SHA-256 `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01`；精确提交证据见 final log |
| 性能证据 | 核对 Release JSON、摘要、Task、索引及 Task pin | Release | PARTIAL；数值 `99.91 / 344.93 / 344.93 ms`、`+208B`、`0 handles` 相互一致，AC6 行 `429.47ms` 不一致 | `performance-baseline-release.json`、`performance-baseline.md:9`、Task `:150,196,229`、索引 `:1,5` |
| 真实窗口/原生矩阵 | 查验可见窗口几何、真实 Loaded/Rendered 与双屏/拔屏/DPI 实测 | 本次未启动产品窗口；当前自动化为 Avalonia.Headless | NOT_RUN；不得由 headless 几何或 Dispatcher priority 推断通过 | Task AC1/AC5 明确列明的缺口；D-1 原生设备矩阵仍 BLOCKED |

### 证据与生命周期指针

- Task、STATUS、PLAN 和 `evidence-index.md` 的全量计数为 1113/0/57；TASK_LEDGER 将 FEA-07 记为 `in_progress`，未提供套件计数。STATUS/PLAN/LEDGER 当前 Task 状态一致。
- Task `delivery_head` 指向 `3220abd59`；`final-evidence.log` 也明确记录该 head 与 clean worktree，且相对 `b3fa8dc0c` 只有 Task/证据文档变化，不改代码。
- `evidence-index.md` 没有自身 SHA 行，解决了 R-011 的自引用问题；Task pins 的 SHA 均匹配。但索引第一行“r3 待派”已随本次实际 r3 复核过时，且同一行有 R-016 的 form-feed。
- 本次报告落盘后，DSH 仍需审查并记录 findings adjudication；由于本结论为 `changes_requested`，不得进入集成验证。修复后应固定新 delivery/code head、重跑 build/test/pins 并更新 canonical evidence 与 handoff，再派发新的独立复核。若后续 Review approved，DSH 还需把 Task reviewer/source、canonical evidence 状态、STATUS/PLAN/LEDGER 与集成 commit/计数同步；集成验证通过及 AC residual 处置前 Task 保持 `in_progress`。

## Architecture 与 Verification 结论

- **Architecture：不通过当前集成门槛。** 稳定宿主/真实内容树缓存、appearance 单写者、前端串行门和启动恢复方向均与本 Task 架构目标一致；但退出状态遗漏、journal 最终提交失败时状态分裂，以及加载/渲染门禁没有观察真实树，仍影响生命周期与事务一致性。
- **Verification：build、headless 全量测试、治理与契约 pins 通过。** AC1/2/3/4/5/6/8 仍为 PARTIAL，AC7 在 headless/机械范围 MET；真实窗口的 Loaded/Rendered、原生显示矩阵和真实保护状态切换后退出没有证据，不能据此批准。

## 结论与复审

**Decision：changes_requested（P0=0 / P1=5 / P2=2）。不建议进入 DSH 集成验证。**

最小返修集：

1. 让真实内容树的 layout/loaded/rendered 成为可观察提交门禁，并补逐阶段实际门禁失败回滚证据；不要把 Dispatcher 优先级空回调当成已渲染。
2. 关闭时聚合所有缓存内容树的 dirty/run 状态，纳入 V2 Theme Studio `HasDraft`，并测试真实 Fluent/V2 切换后的退出阻断。
3. 修复 journal 最终提交失败时 UI、current id、appearance 持久值之间的回滚一致性，补故障注入。
4. 用确定性 barrier 与失败注入强化 R-013 并发证明；更新 Task reviewer、handoff、索引与生命周期状态，统一 Task AC6 的旧 p95，并修正索引 form-feed。

原生 AC5 双屏/拔屏/DPI 仍按 D-1 保持 BLOCKED，不以本次 headless 测试替代。当前 r2 修复中，R-003/R-004/R-005/R-006/R-008/R-010/R-011/R-012/R-014 已达到各自所述闭环；AC3/AC4/AC5/AC6 仍保留卡内 PARTIAL。

## 边界声明

本 Review 固定覆盖 `cbfb7bbc9..b3fa8dc0c`，代码行号按 `3220abd59`。当前 checkout `7b62c492b` 相对 reviewed head 只有 checkpoint 文档增量，没有代码漂移。未修改其他文件，未 commit/push。测试/治理命令按本报告列明结果；native window 与硬件矩阵未运行。Review 不替代 DSH 的 findings 处置、集成验证或 Task 生命周期裁决。
