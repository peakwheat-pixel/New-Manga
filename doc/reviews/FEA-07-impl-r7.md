---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r7；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: 226e47c51（文档/证据 head；代码 head 5a495f80a）
code_head: 5a495f80a208ccc17a34eededc21c91f6e18e720
decision: changes_requested
counts:
  P0: 0
  P1: 0
  P2: 4
---

# Review：FEA-07 第 7 轮实现复核（impl-r7）

## Reviewer 身份与来源

本报告由用户明确委派的 fresh Codex CLI 独立上下文执行，未参与 FEA-07 的设计、实现或返修。来源为本轮用户委派、`doc/handoffs/FEA-07-impl-r6.md` §4 和当前 rolling checkpoint §63；不以自报 session ID 代替独立性依据。主会话负责 Git、调用链、实跑验证、证据核对和本报告。`code-review` 技能的辅助只读审查来源为 `/root/standards`（Standards/Architecture）和 `/root/spec`（Spec/Verification），均未写文件、运行测试或参与实现；两者与主会话独立确认测试判别力、取消及排队快照问题。四个视角均为 **executed**。

唯一主动交付写入为本报告。未修改源码、测试、Task、STATUS、证据、历史 Review 或用户数据，未 commit/push，未进入其他 worktree。指定 build/test/生成器检查产生常规忽略构建输出及测试隔离临时夹具；性能测试还写其固有 `%TEMP%/nm-fea07-performance-baseline.json`，没有回写 canonical JSON。未启动连接真实用户数据的产品，未写真实 `%APPDATA%/NewManga`。没有修改旧实现做 mutation test，也没有创建额外探针或证据文件。

## 范围与 Reality Check

- 起始及报告写入前：`HEAD=226e47c51fe2fcbb5642e5969bd9cf645c5931ca`、branch `main`、common dir `.git`，`git status --short` 为空，工作路径为 `G:\CODEX\New Manga`。**RESUME_SAFE**：与本轮指定 head、Task、STATUS、PLAN 和 checkpoint §62–63 一致。
- 累计 `git diff --stat cbfb7bbc9..HEAD`：**82 files changed / 8261 insertions(+) / 562 deletions(-)**；`git diff --name-only` 的 82 条路径逐条匹配 Task front matter glob，**82/82 合法，越界 0**。同时捕获 `git diff cbfb7bbc9...HEAD --stat`，范围一致。
- `5a495f80a..226e47c51` 仅 9 个 docs/evidence 文件：PLAN、STATUS、rolling checkpoint、impl-r6 handoff、impl-r6 Review、Task、索引、final log、性能摘要。`git diff --quiet 5a495f80a HEAD -- apps/desktop-avalonia` **exit 0**；两端源码树均为 `d1a63271af9ec93d68cde92e8f8a75d3e5f02820`。
- 本轮代码增量 `git diff 4e8510d43 5a495f80a -- apps` 仅 `PresentationWindow.cs` 和 `PresentationWindowTests.cs`，不涉及 `tokens/`、生成产物、Core、schema、冻结契约、依赖或 standalone FluentShell。
- 读取 r6、r5 Review、Task、STATUS、PLAN、指定 final/index/rework-r6/handoff、性能摘要/JSON及当前 checkpoint；架构和生命周期依据为 AD-002 当前边界（含 AD-003 修订提示）、Task W-1/W-6/W-9/W-10、协作协议 §4/§5.1/§6 与 Review 模板。未扫描无关历史 Task 或 verification 目录。

实际 `git log --oneline -6`：

```text
226e47c51 docs(fea-07): impl-r6 approved + R-022 修复处置/证据/索引（head 5a495f80a；全量 1135/0/57）
5a495f80a fix(fea-07): r6 R-022 失败切换恢复原窗口全屏模式（含回归测试）；全量 1135/0/57
80b2203e5 docs(fea-07): impl-r5 处置 + 返修证据/索引 + delivery/生命周期固定（head 4e8510d43；全量 1134/0/57）
4e8510d43 fix(fea-07): r5 返修（R-020 Fluent 全屏桥接到稳定窗口 / R-021 重复通知测试判别力 / 性能口径措辞）；全量 1134/0/57
ea27a7b10 docs(fea-07): impl-r4 处置 + 返修证据/索引 + delivery/生命周期固定（head b328f3488；全量 1132/0/57）
b328f3488 fix(fea-07): r4 返修（R-017 canonical 快照同步 / R-002 真实 Theme Studio draft 验证 / R-013 排队屏障 / R-018 Loaded 订阅解绑 / R-019 staging 输入隔离）；全量 1132/0/57
```

下文源码行号均以 **`5a495f80a`** 为准；文档行号以 **`226e47c51`** 为准。`PresentationWindow.cs` 位于 `apps/desktop-avalonia/src/NewManga.App/Views/Presentation/`；`FrontendHostCoordinator.cs` 位于该 App 的 `Services/`；`FrontendSwitchCoordinator.cs` 位于 `src/NewManga.Presentation.Avalonia/Switching/`；同名测试位于 `tests/NewManga.App.Tests/`。

## r6 findings 闭环表

| ID | r6 | r7 Verdict | 依据与边界 |
|---|---|---|---|
| R-022 | P2 open | **部分修复，未完全闭环** | 单请求、非取消的失败返回现在能恢复旧树的 reader VM 和 WindowState；Promote 后取消抛异常仍跳过恢复。本轮新增用例在构建阶段失败，不能证明原缺陷修复，另列 R-023；门外旧快照引入排队状态污染，另列 R-024。 |
| R-007 | P2 open | **交付关联正确，appointment 文案仍 open** | reviewer 指最新已完成 r6、delivery 精确为 `5a495f80a`、handoff/final/index 关联正确，canonical=pending 合理；Task/索引仍称 r7 另派/待派，与 STATUS/PLAN 的 r7 进行中及本次实际执行不一致。 |

R-020/R-021 不重新打开：全屏接线和设置重复通知实现本轮未改；真实组合根全屏主路径本轮全量及定向均通过。r5/r6 已记录的其他 PARTIAL、D-1 和测试边界继续保留，不因本轮机械检查全绿升级为完整验收。

## 本轮重点实现判断

### 窗口模式恢复与失败阶段

`PresentationWindow.cs:257-259` 同时保存 `WindowState`、当前 Fluent surface 身份和 `ReaderViewModel.IsFullScreen`；`:261-264` 在 coordinator 返回失败后恢复。`RestoreWindowMode:270-280` 仅对仍为当前树的同一 Fluent 恢复 VM，随后恢复原 WindowState。它不重建内容树，也不调用 FullScreenRequested。

构建、layout、Loaded、Rendered 失败时，coordinator 的 RollbackAsync 先恢复旧树（`FrontendHostCoordinator.cs:161-175,301-305`），正常返回失败后 wrapper 恢复模式。单请求的 Promote 后 SaveAsync 普通异常，也先由 CommitAsync catch 恢复内容/settings（`:138-157`），再经 switcher rollback 返回失败；journal finalize 普通异常由 `FrontendSwitchCoordinator.cs:113-133` 进入同一补偿。因此**非取消失败返回路径静态上覆盖本轮原始缺陷**。本轮没有实际执行真实全屏 + Promote 后 Save/finalize 故障，不能把这段静态判断写成对应故障实跑 PASS。

两处边界不完整：一是取消时 switcher 在 rollback 后重新抛出 OCE（`:135-147`），没有失败结果返回，wrapper 不恢复模式；二是 wrapper 快照在 `_switchGate` 之前，恢复在 coordinator 返回之后，未包含在原 R-013 的串行化事务内。详见 R-022/R-024。

成功时不调用 RestoreWindowMode，离开 Fluent 仍按 R-020 的 `OnVisibleContentChanged:183-193` 清 reader 全屏并使全屏窗口 Normal。单请求且用户未中途改变模式时，Normal/Maximized 均按原值保留，不被无条件改成 Normal。新增 Normal 断言只覆盖构建失败；Maximized 的失败补偿未新增实跑用例，现有 memento 最大化测试通过不等于该失败矩阵已验。

### 事件、递归和回归

`FluentPageViewModels.cs:885` 的 IsFullScreen setter 仅经 Set 发属性变化；FullScreenRequested 由按钮/键命令或 ExitFullScreen 显式调用。直接恢复 VM 不会反向发全屏请求或再次触发切换。RestoreWindowMode 没有增减事件订阅，原 `OnVisibleContentChanged:165-179,183-193` 的同实例检查、成对页面事件挂摘和单委托赋值未改；没有代码依据表明本增量引入重复订阅或事件泄漏。

standalone `FluentShell.axaml.cs:44` 的桥接未改；V2、输入路由、退出协调、全屏成功/隐藏请求相关测试包含在全量中。定向真实组合根全屏测试再次通过。这里仅签认本轮已跑的 headless 范围，未运行原生指针命中、IME、多屏或长期泄漏验证。

### 新回归测试的判别力

`PresentationWindowTests.cs:313-359` 确实创建真实 FluentShellSurface，导航 Reader，经真实“全屏”按钮 Click 同时断言 VM=true、WindowState.FullScreen，再执行失败切换并断言旧树和全屏状态，fixture 的 appearance/journal 使用临时根。它不是单纯假 VM 测试。

但 factory 在 `:327-329` 构建 V2 时直接 throw。该失败发生在 BuildTree，未到 `PromoteStagedContent`，因此没有执行离开 Fluent 时的 ExitFullScreen。旧 `4e8510d43` 的直接转发实现也会保持原 VM/Window 全屏；rollback 对同一 Fluent SetContent 只进入 Fluent 重接线分支，不清全屏。**静态反事实结论：删去本轮 wrapper 修复，该用例仍会通过。**本轮实际运行当前 head 的此用例为 PASS；旧版本 mutation 为 **NOT_RUN**，没有冒充实跑反向证据。至少需要一个提升后 Save/finalize 故障用例，证明清理确实发生且补偿恢复，见 R-023。

## Standards（辅助视角，executed）

按辅助报告原顺序：①门外快照使排队拒绝请求覆盖成功结果（R-024）；②取消绕过模式恢复（R-022）；③构建失败测试无法区分旧实现（R-023）。均有 Task AC1 的事务/失败恢复依据，建议严重性均 P2。未发现新增依赖方向、唯一写者、源码写域或许可边界违规，也不以 Fowler smell 为由增加纯风格 finding。

## Spec（辅助视角，executed）

按辅助报告原顺序：单请求非取消的普通失败补偿方向成立；新增测试判别力不足（R-023）；门外快照污染后续模式（R-024）；取消仍漏恢复（R-022）；r7 appointment 文案残留（R-007）。均指向 Task AC1/AC8 与 r6 本轮返修要求，无范围扩张。这些与 Standards 重合的观察不重复计数。

## Findings

仅计仍需处置的 **4 项 P2**；未发现 P0/P1。代码缺陷为静态控制流确认，未新增故障探针运行，不把下表触发步骤称为本轮已执行复现。

| ID | 级别 | 文件/行 | 触发与影响 | 证据性质 | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R-022 | **P2** | `PresentationWindow.cs:261-264`；`FrontendHostCoordinator.cs:138-157`；`FrontendSwitchCoordinator.cs:135-147` | Fluent Reader 全屏→V2 已 Promote 清全屏，此时 SaveAsync 接收的 token 被取消。coordinator 补偿旧内容树和设置后，switcher 重新抛 OCE；wrapper 没有 catch/finally，跳过模式恢复，旧 Fluent 恢复可见但 reader=false、Window Normal。原“失败恢复原全屏”不能宣称完全闭环。 | 静态确认：`AppearanceStore.cs:65-78` 将 token 传入真实异步写；取消分支明确 rollback 后 rethrow。该窗口故障实跑 NOT_RUN。 | 将事务开始后的异常/取消纳入窗口模式补偿，保留取消向上传播；须与串行化门和实际事务快照统一，不能只补门外 finally。增加 Promote 后取消回归。 | open，r6 残余 |
| R-023 | **P2** | `PresentationWindowTests.cs:327-329,351-359` | 新测试在 Building 抛错，未执行会清全屏的 Promote，未修复代码同样满足旧树/VM/Window 断言。真实 surface 和真实全屏成立，但不是 R-022 原缺陷的有判别力验证。 | 当前用例实跑 PASS；旧代码控制流反事实确认，无 mutation 实跑。现有 coordinator finalize 测试使用普通内容树，不补足真实全屏断言。 | 增加真实 Fluent 全屏→目标成功挂 staging→Promote 后 Save/finalize 失败；同时断言失败阶段、原树、VM、Window、frontend/settings/journal，并证明旧实现会失败。至少一个原缺陷路径须有实际可审查证据。 | open，新验证缺口 |
| R-024 | **P2** | `PresentationWindow.cs:257-264,272-279`；`FrontendHostCoordinator.cs:90-113,183-187` | 全屏 Fluent 发起 A→V2，在 A staging 等待期间再发起 B→未知 frontend。B 在门外快照 FullScreen 后排队；A 成功变成 V2/Normal；B 获门后校验拒绝，返回 Succeeded=false/RolledBack=false，wrapper 把过期 FullScreen 写回当前 V2。VM 有树身份守卫而 WindowState 没有。新增修复可改变本应“不触 live UI”的拒绝请求行为。 | 静态确认公开切换 API 和已有异步 staging/排队机制；无需依赖两个恢复 continuation 的调度先后。本轮未新增并发模式探针；生产菜单触发未实测。 | 把窗口模式快照/恢复纳入同一 `_switchGate` 事务，快照在获门后且绑定本事务旧树；拒绝/未开始请求不恢复别的事务状态。增加 A 成功+B 排队失败的屏障测试。 | open，新回归 |
| R-007 | **P2** | `doc/tasks/FEA-07.md:10,242,244`；`verification/FEA-07/evidence-index.md:9` | 当前仍写 r7“另派/待派”，但 STATUS、PLAN、checkpoint §63 及本次实际复核均为 r7 已派执行。delivery/handoff/最新已完成 r6 关联正确，canonical=pending 正确；问题限定为当前 appointment 文案。 | 当前文件与本次派发事实直接核对。 | DSH 处置本报告时统一 r7 reviewer/source/实际结果及索引；历史 Review 保持原字节；集成及残余处置前保留 pending/in_progress。 | open，r6 文案残余 |

## AC 逐条 Verdict

| AC | r7 Verdict | 依据与未覆盖范围 |
|---|---|---|
| AC1 | **PARTIAL** | 原真实树 100 次切换、staging 门禁、draft/会话/输入等测试继续通过；普通失败模式补偿静态成立，但取消、门外旧快照和新用例判别力仍待补。原生 IME、真库 DB/current/pinned/Lock/source/candidate 零变化、ACK 重连、真实 Run/Intent 仍未验。 |
| AC2 | **PARTIAL** | live/cache 退出聚合与真实 Theme Studio draft 关闭阻断回归通过；真实双窗归属、Session/Region 单写 owner/完整 Host 生命周期集成未补。 |
| AC3 | **PARTIAL** | journal/启动恢复/普通 finalize 补偿和排队测试通过；新增模式补偿边界见 findings；真实跨进程 kill 和暂停期间保护状态变化仍未验。 |
| AC4 | **PARTIAL** | planner 单源、warnings fail-safe、启动矩阵回归通过；真实 App 初始化与坏包/scale 完整矩阵仍缺。 |
| AC5 | **BLOCKED / D-1（原生矩阵）** | headless 全屏按钮/F/Esc、成功切换/隐藏请求主路径 PASS；memento/topology/PerMonitorV2 机械回归通过。失败补偿仍有限制；原生双屏/拔屏/换主屏/混合 DPI 100/125/150/200% 与第二窗回迁未运行，保持 BLOCKED，绝不以 headless 替代。 |
| AC6 | **PARTIAL；W-5 PASS** | canonical p50 88.42 / p95 261.38 / max 275.14 ms，两次记录复测 p95 292.65/261.38；本轮独立 Release p95 294.45ms≤1000ms。UI freeze 仍为事务总时长上限，真实规模 workload/原生冻结采样未补。 |
| AC7 | **MET（已列机械/headless 范围）** | 本轮 build 0/0，全量 1135/0/57；启动兼容、依赖方向及 net9.0 门禁通过。57 skipped 的真实 sidecar 链路不能当已验。 |
| AC8 | **PARTIAL** | 临时根、19/19 Task pins、15/15 契约 pins、两生成器及治理通过。R-007 文案和 R-023 关键故障证据缺口未补；原生截图/矩阵仍缺。 |

## 证据与治理核对

以下均为本轮 **executed**，除明确标示 NOT_RUN/BLOCKED 项。环境：Windows NT 10.0.26300.0、PowerShell 7.6.8、.NET SDK 10.0.401、测试 runtime .NET 9.0.11；项目 TFM 仍 net9.0。执行结果、EXIT 和必要输出直接保存在本报告中，不覆盖已有 verification 日志。

| 场景 | 本轮命令/核对 | EXIT / 结果 | 输出与边界 |
|---|---|---|---|
| Git | `git rev-parse HEAD`、`git status --short`、`git log --oneline -6`、branch/common-dir | **0 / PASS** | 精确 HEAD、main/.git、起始及写报告前 clean；6 条日志见前文。 |
| 累计范围 | `git diff --stat cbfb7bbc9..HEAD`、`git diff --name-only cbfb7bbc9..HEAD`，逐条 glob 核对 | **0 / PASS** | 82 files / +8261 / -562；82/82 allowed。 |
| 源码无漂移 | `git diff --name-only 5a495f80a..226e47c51`、源码 quiet diff、两端 tree hash | **0 / PASS** | 仅 9 docs/evidence，源码 tree 一致。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **0 / PASS** | **0 warnings / 0 errors**，4.81s。 |
| 全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **0 / PASS** | **1135 passed / 0 failed / 57 skipped**；App 1m40s。 |
| 定向全屏 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter "FullyQualifiedName~FailedSwitch_RestoresTheOriginalFullScreenMode\|FullyQualifiedName~FluentFullScreenRequests_DriveTheStableWindowState" --logger "console;verbosity=normal"` | **0 / PASS，2/0/0** | 当前新测试449ms、真实组合根全屏测试1s；过滤器实际为普通 `|`，此处仅作 Markdown 转义。新测试 PASS 不消除 R-023。 |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | **0 / PASS** | 292 rows；every generated artifact matches frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | **0 / PASS** | generated theme artifacts match frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | **0 / PASS，3 warnings** | 15 current documents；10 个非终态 Task、STATUS 3149 bytes/29 lines、PLAN 4792 bytes/64 lines 的既有预算/状态告警。只证明机械条件，非语义批准。落盘后再次执行仍 PASS(3)。 |
| 契约 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | **0 / PASS，15/15** | 14 契约+FEA-01，与 Task artifact pins 分开核对。 |
| Task evidence pins | 解析 Canonical Evidence，逐项 SHA-256，再按 path 匹配索引唯一行 | **0 / PASS，19/19** | 18 CANONICAL + 1 SUPPORTING；完整实测 SHA 见附录。索引无自身 SHA 行，非法控制字符0。 |
| final evidence | 日志 head、实际 SHA 与 Task/索引比对 | **PASS** | head=`5a495f80a208ccc17a34eededc21c91f6e18e720`；SHA=`7fb048abbfcafa8055cb604a833bf6dc8eeb583c4b74b695cffc432187305d89`。 |
| rework/handoff | 过程日志与精确交付、计数、性能对照 | **PASS（过程/交付关联）** | rework 说明 `80b2203e5 + uncommitted rework`，final 另绑定提交后 head，无冒充同一精确 head。handoff delivery/测试数/性能一致；其 R-022“已修复/已覆盖”声明须按本报告缩窄。 |
| 性能一致性 | JSON/摘要/Task 当前 AC6/索引/handoff/过程日志，排序重算20样本 | **PASS；W-5 PASS** | 第10项88.42、第19项261.38、max275.14ms；4预热+20单向切换；两次复测292.65/261.38ms一致。 |
| 独立 Release | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj -c Release --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter FullyQualifiedName~PerformanceBaselineTests --logger "console;verbosity=detailed"` | **0 / PASS，1/0/0** | 本轮 p50 87.92 / p95 294.45 / max764.69ms；冷首次634.92ms；+20560B / +3 handles；W-5 PASS。未回写 canonical JSON。 |
| 原缺陷判别/异常模式 | 旧版本 mutation；真实全屏+Promote后 Save/finalize/取消故障；并发模式探针 | **NOT_RUN** | 静态结论与当前测试 PASS 分开记录；当前测试不覆盖上述模式矩阵。不能以全量通过代替。 |
| 原生矩阵 | 双屏/拔屏/换主屏/混合 DPI 100/125/150/200% | **BLOCKED / D-1；NOT_RUN** | 未运行原生产品/设备矩阵；不签发原生验收。 |

### 全量计数与 skip 直接原因

| 项目 | passed | failed | skipped | 直接原因 |
|---|---:|---:|---:|---|
| Appearance | 21 | 0 | 0 | 无。 |
| Presentation.Avalonia | 38 | 0 | 0 | 无。 |
| Host | 51 | 0 | 28 | HostSidecarFact→HostFixture，sidecar env 未设置。 |
| ThemeEngine | 253 | 0 | 0 | 无。 |
| DesignSystem | 87 | 0 | 0 | 无。 |
| ApplicationCore | 31 | 0 | 0 | 无。 |
| CoreClient | 128 | 0 | 22 | SidecarFact/相关 fixture→SidecarFixture，同一 env 未设置。 |
| App | 526 | 0 | 7 | CreateChapterHostIntegration 2、RunControllerHostIntegration 3、WritePolicyUiIntegration 1、StartupSelfCheckUi 1；HostFixture/RunFixture sidecar 检查先跳过。 |
| **总计** | **1135** | **0** | **57** | **1192 tests；28+22+7=57**。 |

本轮实际环境 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置；Host `Support/HostFixture.cs:13-20`、CoreClient `Support/SidecarFixture.cs:28-35` 先于目录/可执行文件/BOOK/S4 夹具检查返回 skip。App 的7项走相同 sidecar 前置；没有设置变量或用空夹具把 skip 转 PASS。对照 r6 的1134/0/57，本轮+1 passed；对照 Task 基线1034/0/57，+101 passed；fail/skip 不增。不是1135项真实 sidecar端到端测试通过。

### 性能适用范围

canonical 记录：p50 **88.42** / p95 **261.38** / max **275.14ms**，冷首次 **605.39ms**、+22496B、+3 handles；过程记录两次复测 **292.65/261.38ms**，与 Task/摘要/索引一致。历史切片旧值带旧 head 语境，不作为当前数值。独立 Release 运行 p95 **294.45ms** 同样≤1000ms，保留其独立身份，不替换已 pin 的记录。独立 run 的 max764.69ms等差异不足以证明泄漏或所有机器稳定。

20个交替单向切换即10次往返；nearest-rank 第19项为p95。摘要仍沿用“12样本不是p95/20样本才是真正p95”的不严谨解释，r5/r6已说明12样本取max也是合法小样本分位数；本轮未改该计算或门槛，不重复计新 finding。真实渲染冻结采样、长期内存/句柄趋势和规模 workload未补，AC6保持PARTIAL。

## Architecture 与 Verification 结论

**Architecture：边界与依赖方向保留，模式状态未完全纳入原切换事务。** 未发现本轮 Core/schema/冻结契约/依赖/用户源文件保护越界；App→Presentation 与 appearance 唯一写者未改变。单请求普通失败返回的修复方向正确，事件桥接无新增递归/重复订阅证据；R-024 的门外快照和 R-022 的取消遗漏需处置。

**Verification：所有指定机械检查通过，本轮关键返修验证不足。** build、1135/0/57、定向2/0/0、两生成器、治理、15/15冻结 pins、19/19 Task pins、性能一致性和独立Release W-5均PASS。但唯一新增全屏失败用例不能捕获原始提升后失败缺陷，后续失败/取消/并发模式没有对应运行证据。依协作协议 Review 模板“P0/P1未解决或关键验证缺失时不可批准”，本轮不沿用r6批准。AC1/2/3/4/6/8仍PARTIAL；AC7限定范围MET；AC5原生BLOCKED/D-1。

## 结论与复审

**Decision：`changes_requested`（P0=0 / P1=0 / P2=4）。** 严重性沿用窗口模式缺陷的P2，不人为升级；要求返修的理由是本轮核心R-022修复缺少能捕获原缺陷的关键验证，且取消/排队边界尚有可定位残余。该结论不撤改历史r6报告，不是Task done、集成或push授权。

最小返修集：

1. DSH把窗口模式快照与补偿纳入同一串行化事务，覆盖事务开始后的取消/异常，避免拒绝请求/过期快照改写前次成功结果。保留成功离开Fluent退出全屏策略及Normal/Maximized行为。
2. 补至少一个真实Fluent全屏、**Promote后**Save或finalize失败的有判别力测试，明确失败阶段并同时验证旧树/VM/Window/持久frontend/journal；另补取消和排队失败模式回归。当前构建失败用例可保留，不能继续作为原R-022缺陷的独立闭环证据。证明旧实现失败时，记录真实反向验证方式和结果，不用文字推论冒充实跑。
3. 统一r7 reviewer/source/结果及handoff/索引文案；固定新code/delivery head，刷新精确head final证据与全部pins。按本报告命令重跑build、全量、两生成器、check/pins及性能门槛，fresh上下文复审。既有PARTIAL/D-1由DSH依授权处置，不能自动升级或先置done/canonical complete。

推荐下一步为 **DSH继续当前FEA-07返修与复审**，启动条件为接收本报告并完成Reality Check；尚不释放proposed的FEA-06-RESIDUAL-1。Recovery为本报告固定main、base/code/document head；范围为Task allowed_paths内必要App/Presentation/测试与本Task交付文档，禁止Core/schema/冻结契约/生成物/新增共享依赖/真实用户数据改动，扩大共享面先由DSH冻结授权。交付物为findings处置、固定修复commit、对应测试、handoff、精确head日志/索引/pins；Gate为有判别力测试、完整指定验证与fresh复审，再由DSH集成。可直接转发：

> 在 `G:\CODEX\New Manga`、branch `main`、common dir `.git`，继续Task FEA-07；base `cbfb7bbc92d489541a24290038eae2117f8aa1ce`，本次文档head `226e47c51fe2fcbb5642e5969bd9cf645c5931ca`、代码head `5a495f80a208ccc17a34eededc21c91f6e18e720`。先Reality Check并保留他人dirty与本报告原文。按 `doc/reviews/FEA-07-impl-r7.md` 处置R-022取消补偿、R-023提升后失败验证、R-024门外快照和R-007文案；仅在Task allowed_paths内修改必要App/Presentation/测试及当前交付文档，不改Core/schema/冻结契约/生成物/共享依赖/真实用户数据，不进入其他worktree，不push。交付固定新commit、真实全屏Promote后失败/取消/排队回归及旧实现反向判别证据、handoff和精确head final/index/pins。重跑本报告完整build/test/两--check/check/verify_pins与Task证据SHA，基线1135/0/57，新增测试另计，记录skip和blocker；Release热切换p95≤1000ms。AC5原生矩阵保留BLOCKED/D-1，其他PARTIAL不自动升级；完成处置后Appointment fresh只读复审，再决定集成/生命周期。不要自动释放FEA-06-RESIDUAL-1。

## 附录：19项 Task evidence SHA-256 三方核对

下表实际文件SHA均与Task表及索引对应唯一路径行相同，**19/19 PASS**；PERF-MD为SUPPORTING，其余18项为CANONICAL。索引自身SHA仅在本报告外部记录：`c1e97ed2ddc568950d56b4f9df1a2e499bb7d0469c20aca462cafc75f218730e`，不回写索引自pin。

| evidence_id（EV-FEA07-） | 实测 sha256 |
|---|---|
| SLICE1 | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` |
| SLICE2 | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` |
| SLICE2B | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` |
| SLICE2C1 | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` |
| SLICE2C2 | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` |
| SLICE3 | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` |
| SLICE4 | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` |
| SLICE5 | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` |
| PERF | `a06e3cfda3b362f3bc1bff7cf61fe173a68fcf247f45be21a4b3df9cf658a102` |
| GAPCLOSING | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` |
| GENERATORS | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` |
| FINAL | `7fb048abbfcafa8055cb604a833bf6dc8eeb583c4b74b695cffc432187305d89` |
| PERF-MD | `1161f6368d3a6f13740516daa61b4c9272b655192995e15d24e74d4b6d0d8966` |
| REWORK2 | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` |
| REWORK-R3-1 | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` |
| REWORK-R3-2 | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` |
| REWORK-R4 | `f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b` |
| REWORK-R5 | `e773a93def145d258ff09f8cb02ae9783823e7588e06443de28ba3381a3619b9` |
| REWORK-R6 | `322475cb618a71cf1f69e3422908a4d2b435ac53567462ffe1ba2309b01c5ae9` |

## 只读与最终状态

本报告仅对所列固定head有效。写入后再次检查HEAD、治理与工作区；预期且实际唯一未跟踪交付为 `doc/reviews/FEA-07-impl-r7.md`，无其他tracked修改、无commit/push。后续外部提交不自动纳入本报告结论。
