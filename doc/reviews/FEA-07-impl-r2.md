---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r2）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: f28d97b995ce53dcd8b672598905dddb2cf0448f
code_head: 7ca2e367b09c41fe0253a68d77bbbfde99e8c772
decision: changes_requested
counts:
  P0: 0
  P1: 6
  P2: 3
---

# Review：FEA-07 实现复核 r2

## Reviewer 身份与来源

本报告由本次 fresh Codex CLI 独立上下文按用户派发编写。未参与 FEA-07 的设计、范围冻结、实现或返修；本次只读复核 `cbfb7bbc9..f28d97b99`，没有子任务或其他 Review 代理。代码行号按 `7ca2e367b` 核对；`f28d97b99` 是 docs/verification 提交，不改变代码。审查时仓库当前 HEAD 为其后的 docs checkpoint `ddef44f81c611aef795440f8f919a55100d2feb7`，该 checkpoint 不纳入指定 reviewed head。

## Reality Check

- 起始核验：`HEAD=ddef44f81c611aef795440f8f919a55100d2feb7`，分支 `main`，`git common dir=.git`，工作区 clean。`7ca2e367b`、`f28d97b99` 与 `cbfb7bbc9` 均可解析。
- `git diff --stat cbfb7bbc9..f28d97b99`：60 files changed，4428 insertions(+)，552 deletions(-)。当前 reviewed implementation 路径均落在 Task `allowed_paths`，包括 `AppOptions.cs` 和 checkpoint；未发现其他越界文件。
- 后续 `git diff --name-only f28d97b99..HEAD` 只有 `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`；不改变本报告固定范围。

## R-001…R-012 闭环表

| ID | 级别 | r2 结论 | 证据与残余 |
|---|---|---|---|
| R-001 | P1 | **部分闭环；AC1 仍 PARTIAL，finding 保留** | `App.CreatePresentationShell` 按 frontend 缓存并返回同一真实内容树；组合测试 10 次往返（20 次切换）断言 Fluent/V2 树实例相同。页面/VM 不再因每次切换而重建，但测试未覆盖要求的 100 次真实内容往返，也未直接断言 Session/Draft/Run/Intent。`Layout`/`Loaded`/`Rendered` 仍指向 `NoOpAsync`，不能证明真实呈现提交条件及焦点/输入路由回滚。代码：`App.axaml.cs:223-245`、`PresentationHostCompositionTests.cs:141-171`、`FrontendSwitchCoordinator.cs:66-73,147`。 |
| R-002 | P1 | **未闭环** | `PresentationWindow` 已在生产窗口注册主窗 broker，并把 `Closing` 接到 `ExitCoordinator`。但生产代码没有任何编辑/Run 状态源调用 `RegisterPendingEdit`、`RegisterActiveRun`；当前窗口 coordinator 因而没有实际保护状态。测试手动注册后验证关闭被取消，只证明钩子和 coordinator 逻辑，不证明生产状态接线。Broker 二级窗口测试只登记 token，没有实际窗口绑定或 `(SessionId, RegionId)` 单写 owner。`ShutdownMode.OnMainWindowClose` 与已取消的 `Closing` 未发现直接语义冲突，但测试没有覆盖 Avalonia app lifetime 的关闭行为。代码：`PresentationWindow.cs:68-70,80,98-105`；`ExitCoordinator.cs:17-68`；`PresentationWindowTests.cs:189-201`。 |
| R-003 | P1 | **启动恢复接线已补；last committed 缺口仍未闭环** | `CreatePresentationShell` 启动时检查未完成 journal 并记录 rollback，测试覆盖 `Rendered` 阶段中断。journal 只保存 target/stage/time/failure，没有 previous/last committed frontend。运行期先保存 target frontend，再由事务最终提交 journal；若进程在两者之间退出，启动恢复只把 journal 标成 rolled back，而启动选择已经从持久化设置算出，仍会启动 target，无法回到上次已提交 frontend。现有测试只验证设置未先变成 target 的普通 interrupted case，未覆盖该崩溃窗口。代码：`App.axaml.cs:74-88,213-220`、`FrontendHostCoordinator.cs:95-103`、`SwitchJournal.cs:7-12`。 |
| R-004 | P1 | **未闭环；Task 的 AC4 `MET` 不成立** | Planner 会把任意 appearance fallback warning 设为 fallback；App 当前分支在 warning 时即使 CLI 指定 Fluent 也会选 Current V2，故该路径的代码行为看起来正确。但组合根没有直接使用 `StartupPlan.EffectiveFrontendId`/`ShellKind`，而是重新调用 `FrontendSelector.Select`；“planner 是唯一决策源”尚未成立。坏 JSON 测试单独调用 planner 后手工构造 V2 selection，再调用 `App.CreateShell`；启动矩阵也自行 Select 后调用 `CreateShell`，没有走 `App.OnFrameworkInitializationCompleted` 的实际接线。Task AC4 仍标 `MET`。代码：`App.axaml.cs:74-91`、`SafeStartupPlanner.cs:79-84`、`StartupCompatibilityMatrixTests.cs:55-63,104-127`。 |
| R-005 | P1 | **代码接线闭环；AC5 仍 BLOCKED/PARTIAL** | 启动 memento 有屏时经 `DisplayTopologyPlanner.Clamp`，并从当前 `ScreenFromWindow(...).DisplayName` 捕获 DisplayId；无屏幕或枚举不可用时跳过位置恢复/返回空拓扑，没有强行 clamp。原生双屏、拔屏、DPI 100/125/150/200% 验收仍正确登记为 D-1 BLOCKED。另见新问题 R-014：已保存的最大化状态未恢复。代码：`App.axaml.cs:278-324`、`PresentationWindow.cs:46-53,88-96`。 |
| R-006 | P1 | **闭环** | 启动矩阵给所有用例追加 `--theme-home <临时根>`；Presentation host 的 memento/journal 也从该根派生。当前 `%APPDATA%\NewManga\window-state.json` 不存在；本次测试后仍不存在。Task 记录此前误写文件已清理及运行前后 mtime 未变；本次没有改动或删除 AppData 文件，也未读写 `theme-settings.json`。代码：`StartupCompatibilityMatrixTests.cs:27-43,55-63`。 |
| R-007 | P1 | **未闭环；不可进入 DSH 集成验证** | Task `delivery_head=7ca2e367b` 正确，但 `reviewer` 仍是 impl-r1、`canonical_evidence_status=pending`；现有 handoff 是 impl-r1 handoff，且未显式写 delivery commit。STATUS/PLAN/LEDGER 均仍指向 FEA-07 `in_progress`，治理检查通过；STATUS/PLAN 的套件计数仍为 1102/0/57，与精确代码树最终证据 1106/0/57 不一致。r2 报告落盘后，仍需 DSH 更新 reviewer/source、handoff commit、canonical evidence 状态和相关计数，再决定是否释放集成验证。 |
| R-008 | P2 | **闭环** | `allowed_paths` 已包含 `AppOptions.cs` 与 `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`；对 `cbfb7bbc9..f28d97b99` 的所有路径核对均匹配白名单或其 glob。未发现新增越界。Task：`doc/tasks/FEA-07.md:24-47`。 |
| R-009 | P2 | **性能判据闭环；Task 数值记录有残余** | Release JSON 的 `p95Ms=344.93` 与测试源码 `p95 <= 1000 ms` 硬断言一致，W-5 未下调；AC6 已正确为 `PARTIAL`，UI freeze 是事务时长上限估计而非渲染冻结测量。Debug JSON 独立记录 `p95=516.05`。但 Task AC6 行和测试要求表仍写旧 Release `429.47 ms`，需统一为当前基线。 |
| R-010 | P2 | **循环分配/增长风险闭环；有界保留可接受** | 每种 frontend 只保留一个真实内容树，重复切换不会持续创建新的 ViewModel/事件订阅；未见每次切换造成的订阅增长。缓存树和订阅会保留到窗口/进程结束，这是为保留页面状态而有界持有；没有证据显示该有界订阅造成错误，不单独登记 P2 residual。 |
| R-011 | P2 | **代码快照绑定有效；索引自身 SHA 残余未闭环** | `final-evidence.log` 记录运行 head `251b5df0d`；Task pin 标 `7ca2e367b` 为代码 head。`git diff --name-only 7ca2e367b..251b5df0d` 仅包含 handoff、Task 与性能证据文档，没有代码差异，因此 build/test 对应的代码树与 delivery code head 相同；最终日志 SHA 与 Task 行一致。`evidence-index.md` 自身列出的 SHA `f3dd70c2…` 与实测文件 SHA `900e0e65…` 不符，索引自 pin 不有效，应从索引移除自引用或改用外部 pin。 |
| R-012 | P2 | **闭环** | `generators-check.log` 已归档 TokenGen 与 ThemeGen 两项 `--check` 输出，均 exit 0；文件 SHA 与 Task canonical pin 相符。最终证据日志也记录两项检查 exit 0。 |

## AC 逐条 Verdict

| AC | Verdict | r2 依据 |
|---|---|---|
| AC1 | **PARTIAL** | 真实内容树 cache 与实例复用成立；实际 factory 测试只有 10 次往返，未满足 100 次真实往返，也未直接断言 Draft/Run/Intent/数据零变化。布局、Loaded、Rendered 仍是 NoOp；原生 IME、DB/current/pinned revision/Lock/source、ACK 重连矩阵未验。 |
| AC2 | **PARTIAL** | Closing 取消钩子及手工注入 pending edit 的测试有效；生产编辑/Run 状态未注册，broker 没有真实窗口和单写 owner 集成。 |
| AC3 | **PARTIAL** | App 启动路径能发现并标记 interrupted journal；没有持久化 previous/last committed frontend，也没有覆盖设置已写 target、journal 未提交时的重启用例。暂停期间保护状态变化仍未验证。 |
| AC4 | **PARTIAL（Task 当前错误标 MET）** | fallback warning 到 Current V2 的当前分支逻辑存在，包括显式 Fluent CLI；planner 结果仍被组合根重新推导，坏 JSON 的测试没有覆盖 App 初始化入口，故不能视为满足单一决策源及真实 App 接线验收。 |
| AC5 | **PARTIAL / 原生矩阵 BLOCKED** | memento clamp、DisplayId 捕获及 headless 空屏保护接线存在；真机双屏/拔屏/DPI 矩阵未做。最大化状态也未从 memento 应用，见 R-014。 |
| AC6 | **PARTIAL** | Release `p95=344.93 ms`，硬断言 `<=1000 ms` 通过；W-5 未改。缺真实规模合成 workload、独立渲染 UI freeze 和真机指标；Debug/Release 分开记录。Task 当前 AC6 旧值需更新。 |
| AC7 | **MET（限于 headless/机械范围）** | 本次全量回归 1106/0/57；架构 ProjectReference/TFM 门禁已在套件内。兼容矩阵直接覆盖 shell 构造与优先级，不等同于 AC4 的真实 App 初始化接线测试。 |
| AC8 | **PARTIAL** | 临时根隔离和性能、生成物、治理证据存在；原生矩阵仍 BLOCKED，evidence-index 自 pin 不匹配，STATUS/PLAN 套件数也滞后。 |

## 新问题

| ID | 级别 | 文件/行 | 问题与影响 |
|---|---|---|---|
| R-013 | P1 | `FrontendHostCoordinator.cs:64-85,123`；`FrontendSwitchCoordinator.cs:63-65` | 并发切换的状态检查和 rollback snapshot 在 `_switcher` semaphore 之前执行。若 V2→Fluent 正在等待异步保存时，用户又请求回 V2，第二次调用看到旧 `CurrentFrontendId=V2`，会立即返回成功 no-op；第一次随后仍可提交 Fluent，最终 UI 与第二次成功响应相反。不同目标并发时，后一个回调也可能持有前一个事务前的 `previous` 内容，失败回滚到过期 UI。应把同一把串行门禁覆盖 no-op 检查、previous/settings 快照与事务执行，并用并发失败注入验证。 |
| R-014 | P2 | `PresentationWindow.cs:46-53`；`WindowStateMemento.cs:14` | memento 保存 `IsMaximized`，但构造恢复只应用 Width/Height/Position，没有设置 `WindowState`。最大化后退出并重启会打开为普通窗口，窗口状态恢复不完整。 |

## 证据与治理核对

- `dotnet build apps\desktop-avalonia\NewManga.sln --nologo`：PASS，0 warnings / 0 errors。
- `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings`：PASS，1106 passed / 0 failed / 57 skipped；skip 为 Host 28、CoreClient 22、App 7，原因与归档证据一致。本次运行的代码树与 `7ca2e367b` 相同。
- `pwsh -NoProfile -File tools\governance\check.ps1`：PASS，3 warnings（10 个非终态 Task，以及 STATUS/PLAN 预算告警）。`verify_pins.ps1`：PASS，15/15。
- Task 中 12 个 canonical evidence 文件的 SHA-256 与实测匹配；`final-evidence.log`、release/debug JSON、`generators-check.log` 的 Task pins 逐项相符。`evidence-index.md` 自身行例外：记录 SHA 与实测不符，见 R-011。
- `final-evidence.log` 的命令 exit 均为 0，准确记录 1106/0/57、skip 原因和治理/pins 结果；日志 head 是 docs commit `251b5df0d`，相对 delivery code head `7ca2e367b` 没有代码差异。
- `performance-baseline-release.json`：p50 99.91 / p95 344.93 / max 与 UI-freeze upper bound 344.93 ms / memory +208 bytes / handles 0 / budget 1000 / passed true。Debug 文件单独记 p95 516.05 ms。`generators-check.log` 两项命令 exit 0。
- 测试后 `git status --short` 仍 clean；当前 AppData `window-state.json` 不存在。Task 声称的此前 mtime 前后测量与误写文件清理记录未被本次重新执行；本次确认新矩阵用例均以临时 theme root 接线。

## 结论

**Decision：changes_requested。** 目前不建议进入 DSH 集成验证。尚有 6 项 P1（R-001/002/003/004/007/013）：真实 factory 循环与状态断言不足、退出状态源和窗口 owner 未生产接线、journal 无 last committed 恢复、AC4 状态和接线测试不成立、生命周期字段未完成，以及并发切换可能返回错误成功并错误回滚。另有 3 项 P2（R-009/011/014）：Task 性能值滞后、evidence-index 自 SHA 错误、最大化 memento 未恢复。

建议 DSH 先处理上述 P1 并更正 Task/evidence 索引，再固定新 delivery head 和 canonical evidence；之后由新的独立上下文复核。原生 AC5 矩阵仍按 D-1 保持 BLOCKED，不因 headless 结果降级或放行。

## 边界声明

本 Review 只覆盖 `cbfb7bbc9..f28d97b99`，实现行号按代码 head `7ca2e367b`。未修改源码、Task、STATUS、PLAN、LEDGER、旧证据或用户数据；本文件是唯一主动写入的仓库文件。未 commit/push。构建及测试按用户要求运行；本次未删除测试或构建输出。Review findings 不替代 DSH 对范围、修复、集成与生命周期的处置。
