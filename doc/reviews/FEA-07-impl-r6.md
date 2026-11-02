---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r6；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: 80b2203e5（文档/证据 head；代码 head 4e8510d43）
code_head: 4e8510d431ac82df54b82991d14975da5c27f9a0
decision: approved
counts:
  P0: 0
  P1: 0
  P2: 2
---

# Review：FEA-07 第 6 轮实现复核（impl-r6）

## Reviewer 身份与来源

本报告由用户本次明确委派的 fresh Codex CLI 独立上下文执行，未参与 FEA-07 的设计、实现或返修。来源为本轮用户只读委派，以及被审 `doc/handoffs/FEA-07-impl-r5.md` §4 的 Codex CLI r6 派发入口；不以自报 session ID 作为独立性证明。主会话执行 Git 核对、代码与测试分析、指定命令及报告落盘；辅助只读审查为 `/root/standards`（Standards/Architecture）与 `/root/spec`（Spec/Verification），两者均未写文件、运行测试或参与实现。新增全屏回滚残余由主会话定位，两子任务均独立核对调用链。四个视角均为 **executed**。

本次唯一主动交付写入是本报告；未修改源码、测试、Task、状态、历史 Review、既有证据或用户数据，未 commit/push，未进入其他 linked worktree。用户明确要求的 build/test 和生成器检查产生常规忽略构建输出及测试自带的隔离临时夹具；Release 性能用例另写其自身 `%TEMP%/nm-fea07-performance-baseline.json`。没有启动使用真实用户数据的产品，没有写真实 `%APPDATA%/NewManga`。未创建额外探针文件或修改代码做 mutation test。

## 范围与 Reality Check

- 起始及报告落盘前均为 `HEAD=80b2203e512392a38452a24fff983d719775b1f0`、branch `main`、common dir `.git`；起始 `git status --short` 为空。全文代码行号以 **`4e8510d43`** 为准，文档行号以 **`80b2203e5`** 为准。
- 累计范围 `git diff cbfb7bbc9..HEAD`：**79 files changed / 7757 insertions(+) / 562 deletions(-)**。79 条变更路径逐项匹配 Task `allowed_paths`，**79/79，越界 0**，见附录 A。未将本轮新报告计入被审提交范围。
- `4e8510d43..HEAD` 只有 9 个 docs/evidence 文件：PLAN、STATUS、rolling checkpoint、impl-r5 handoff、impl-r5 Review、Task、索引、final log、性能摘要。`git diff --quiet 4e8510d43 HEAD -- apps/desktop-avalonia` exit 0；两个提交的 `apps/desktop-avalonia` Git tree 均为 **`a3dd3da5d44874f0ca345e9b355f93a8b46a80cd`**，无源码/测试漂移。
- 先读 r5，再回溯 r4/r3/r2/r1；核对 Task、STATUS、PLAN、当前 rolling checkpoint 和本次指定的 final/index/performance/rework/handoff。架构依据为 AD-002 的当前有效边界（含文件内 AD-003 修订提示）、Task W-1/W-6/W-9/W-10、方案 §7/§15.5 及协作协议 §4/§5.1/§6。未扫描其他 Task 或非引用的历史证据目录。
- 本轮代码增量 `b328f3488..4e8510d43` 为 Fluent surface API、PresentationWindow 全屏桥接、FrontendContentHost 事件及对应两组测试；没有 Core/schema/冻结契约/生成产物/新增依赖变更。累计改动仍是窗口与切换装配范围。

实际 `git log --oneline -8`：

```text
80b2203e5 docs(fea-07): impl-r5 处置 + 返修证据/索引 + delivery/生命周期固定（head 4e8510d43；全量 1134/0/57）
4e8510d43 fix(fea-07): r5 返修（R-020 Fluent 全屏桥接到稳定窗口 / R-021 重复通知测试判别力 / 性能口径措辞）；全量 1134/0/57
ea27a7b10 docs(fea-07): impl-r4 处置 + 返修证据/索引 + delivery/生命周期固定（head b328f3488；全量 1132/0/57）
b328f3488 fix(fea-07): r4 返修（R-017 canonical 快照同步 / R-002 真实 Theme Studio draft 验证 / R-013 排队屏障 / R-018 Loaded 订阅解绑 / R-019 staging 输入隔离）；全量 1132/0/57
ad56bea1c docs(fea-07): r3 返修 part2 处置 + 精确 head 证据/索引 + delivery/生命周期固定（head 100d487ff；全量 1119/0/57）
100d487ff fix(fea-07): r3 返修 part2（R-001 真实 staging Loaded/Rendered 门禁 + 状态覆盖；R-002 隐藏缓存树退出聚合 + V2 Theme Studio draft）；全量 1119/0/57
cc34f36e1 docs(fea-07): 新会话恢复材料（handoff + checkpoint）
6a31fb92e fix(fea-07): r3 返修 part1（R-015 journal finalize 补偿 + R-013 并发确定性测试 + R-009/R-016/R-007）；全量 1115/0/57
```

下文源码简写对应 `apps/desktop-avalonia/src/NewManga.App/`、Presentation 模块对应 `src/NewManga.Presentation.Avalonia/`；同名测试均在 `apps/desktop-avalonia/tests/NewManga.App.Tests/`。完整路径另见附录 A。

## r5 findings 闭环表

| ID | r5 状态 | r6 结论 | 依据与边界 |
|---|---|---|---|
| R-020 | P1 open | **原全屏接线缺陷闭环** | `PresentationWindow.cs:70-74,163-222` 将可见树全屏请求接到稳定 Window；真实组合根按钮/F/Esc、成功切换和隐藏请求测试本轮两次通过。失败补偿丢原模式单列新 **R-022/P2**，不把成功路径未接线的原 P1 留开。 |
| R-021 | P2 open | **闭环** | `SettingsDraftSyncTests.cs:124-165` 新增 clean Contrast；重复通知通过反射直接执行生产 `OnAppearanceChanged`，不再是同值 SaveAsync 空转；dirty draft 完整记录及 IsDirty 断言有效。 |
| R-007 | P2 open | **交付主体正确，appointment 文案仍 open/P2** | Task reviewer 已指 r5、delivery 精确为 `4e8510d43`，handoff/final/index 的交付关联正确；但 Task `:10,232,235` 与索引 `:9` 仍称 r6 待派，本次及 STATUS/PLAN 已是 r6 执行中。canonical=pending 正确。 |

### r4 及更早 findings 状态确认

| ID | r6 状态 | 当前代码/证据依据与残余 |
|---|---|---|
| R-001 | 维持原缺陷闭环；AC1 PARTIAL | `PresentationWindow.cs:76-91` live staging；coordinator `:118-137,196-288` 真实几何/Loaded/frame 门禁；组合测试 `:179-237` 真实树 50 往返/100 切换保留页面、草稿及 V2 会话字段。真实 DB/Lock/ACK/Run/IME 仍未补。 |
| R-002 | 维持闭环；AC2 PARTIAL | `PresentationWindow.cs:137-155,225-247` 聚合 visible/staging/cache；`App.axaml.cs:254,401` 接全 cache 和真实 HasDraft；组合测试 `:306-372` 生产 Theme Studio draft/关闭阻断及移除 provider 反向判别保留。 |
| R-003 | 维持闭环；AC3 PARTIAL | `App.axaml.cs:74-77,336-371` 在 planner 前恢复 previous frontend；跨进程 kill、保护状态变化未验。 |
| R-004 | 维持闭环；AC4 PARTIAL | `App.axaml.cs:77-92` 采用 planner.Selection；`SafeStartupPlanner.cs:64-90` warnings fail-safe。真实 App 初始化及坏包/scale 完整矩阵未验。 |
| R-005 | 维持代码接线闭环；AC5 原生 BLOCKED | `App.axaml.cs:256-259,283-326` 枚举/clamp/捕获 DisplayId；不把纯 topology 测试当原生拔屏。 |
| R-006 | 维持闭环 | StartupCompatibilityMatrix 显式临时 theme-home；本轮组合/性能/draft 测试使用临时根，未启用真实数据产品。 |
| R-008 | 维持闭环 | 本轮累计 79/79 路径匹配 allowlist。 |
| R-009 | 维持数值闭环；AC6 PARTIAL | 当前 JSON/摘要/Task/索引/handoff 相符，20 样本重算正确，本轮独立 Release W-5 PASS；freeze/workload 限制仍在。 |
| R-010 | 维持闭环 | `App.axaml.cs:218-238` 每 frontend 一树缓存；有界缓存不等于持续增长。 |
| R-011 | 维持闭环 | 18/18 Task artifact pins 与实际字节、索引对应行三方一致；索引无自身 SHA 行。 |
| R-012 | 维持闭环 | 两生成器本轮实际 `--check` 均 exit 0、byte-for-byte up-to-date。 |
| R-013 | 维持闭环；保留测试边界 | coordinator `:90-113,183-187` 同门覆盖判定/快照/补偿；测试 `:208-251` 首请求持门失败、第二同目标未完成及随后真实切换。appearance 断言仍是 coordinator 值，没有另重读磁盘。 |
| R-014 | 维持闭环 | `PresentationWindow.cs:61-67,128-135` 最大化恢复/捕获仍在，对应测试通过。 |
| R-015 | 维持原 settings/id/UI 补偿闭环 | coordinator `:138-175` 与 Presentation `FrontendSwitchCoordinator.cs:113-145` 保留 finalize 故障补偿；新增窗口模式补偿遗漏单列 R-022，不宣称所有窗口状态已完整回滚。 |
| R-016 | 维持闭环 | 索引非法控制字符 0、路径正常、无自引用 pin。 |
| R-017 | 维持闭环 | `FluentPageViewModels.cs:1390-1405` 按 old/new canonical 判断 frontend-only，Mode/Contrast 等真实变化镜像唯一写者；本轮 8 个 SettingsDraftSync 测试全通过。 |
| R-018 | 维持原订阅泄漏闭环 | coordinator `:120-133,183-187,317-340` 保存 handler，finally 等待 UI 解绑再释放门；tracking 测试仍不能单独证明事件表为空，闭环包含源码实际 `-=` 依据。 |
| R-019 | 维持闭环 | coordinator `:199-204,292-305` staging 停用/commit 激活；V2 `AppShellV2.axaml.cs:98-110,170-175,205-254` 成对挂摘及 handler 守卫；本轮全量输入回归通过。 |

## 本轮重点实现判断

### 1. R-020：可见树、窗口状态与调用顺序

`FrontendContentHost.cs:29-40` 先更新槽内容，再发 `ContentChanged`；稳定窗口在初始 SetContent 前订阅（`PresentationWindow.cs:70-74`），staging 槽没有挂该窗口 handler。初始即 Fluent 和由 V2 切入 Fluent 都会接线。只有 visible Fluent 获得 `FullScreenRequested = ApplyFullScreenRequest`（`:165-179`）；换出时摘 `CurrentPageChanged`、调用 `ExitFullScreen()`、清 owner，并仅在当前状态为 FullScreen 时置 Normal（`:183-193`），不会把普通 V2 初始最大化无条件改掉。

换出后旧 surface 仍保留这一个 FullScreenRequested 委托，**并未置 null**；可见性守卫 `:217` 在 owner 为空或 Current 不匹配时忽略请求。生产 `App.axaml.cs:218-238` 对 Fluent 仅缓存一树，所以当前可达组合下隐藏/缓存请求不会控制窗口。不能将这个结论扩展为任意多个 Fluent 实例：委托不携带 source，未来多实例需要按来源绑定与校验；当前没有该生产触发链，不新增理论 finding。

同一 Fluent 重复 SetContent 受 ReferenceEquals 防止重复订阅；换出一次 `-=`、换入一次 `+=`，FullScreenRequested 为单个属性赋值而非每次追加。ContentHost 与 Window 同生命周期，不是每切换新增常驻 publisher。没有观察到本次改动引入订阅线性增长或递归。窗口关闭后跨窗口重用同一 surface 不在当前 factory 路径内，未把它宣称为已验。

`FluentShellSurface.ExitFullScreen():173-181` 先设 reader VM=false，再发 false；窗口回调只写 WindowState，不反向再次调用 ExitFullScreen。换出时 ContentHost.Current 已是 V2，因此该 false 回调被守卫忽略，随后窗口显式 Normal 仍使 VM/Window 一致。离开 Reader 时 `CurrentPageChanged:207,234` 触发窗口 `:200-211`，在窗口 FullScreen 时重置 VM 和 Window；成功路径没有“窗口 Normal 而 VM 仍 true”的状态遗留。

### 2. Esc、按钮/F 测试的判别力与边界

按钮链为 `ReaderPageView.cs:78,172-175` → surface `:362-364` → Window `:214-222`。F 在 reader 的 KeyDown `:205-208`；surface tunnel `:367-371` 未匹配 F 时才到 reader。Esc 优先被 FEA-06 全局键表 `ShellCommands.cs:78` 的 `SurfaceBack` 捕获，经 `CloseTopSurface:488-497`、`CloseReader:360` 离开 Reader，再由页面事件退出全屏；这里不是 reader 自身 `:210-214` 的“仅退出全屏”分支。该行为与冻结键表一致，测试也明确检查 reader 已关闭、VM=false、Window Normal。存在 modal 时 Esc 先关闭 modal，Reader 尚未离开且仍全屏，属于现有 SurfaceBack 栈顺序，不是状态分裂。

`PresentationHostCompositionTests.cs:385-476` 通过真实 `App.CreatePresentationShell`、真实 Fluent reader 和 Window 运行；`:411-419` 在按钮操作后立即同时断言 VM 与 Window。旧实现会在首个 WindowState.FullScreen 断言失败，无法仅凭 VM 真值蒙混通过。F/Esc 使用 `KeyPressQwerty` 的 raw headless 路由，并先断言 reader.Focus() 成功（`:422-440`），没有直接调用 HandleKeyForTest；成功切换及隐藏请求在 `:443-461`，切回重接线在 `:464-475`。本轮全量及定向复跑均通过，键路径有判别力。

按钮通过 RaiseEvent 验证 Click→回调接线，未模拟原生指针命中；隐藏请求通过委托直接注入验证守卫，未模拟隐藏树获得真实焦点；这两点不能外推为原生输入/焦点/多屏验收。测试也未覆盖提升后的 commit/finalize 失败，见 R-022。**R-020 使 AC5 的该 headless 主路径恢复 PASS，原生矩阵仍 BLOCKED/D-1。**

### 3. R-021：生产通知入口与错误实现区分

`SettingsDraftSyncTests.cs:141-165` 先造真实 dirty draft，再反射取非空 `SettingsViewModel.OnAppearanceChanged` 并 Invoke，随后 RunJobs。生产 handler 在 UI 线程立即执行 `ApplyCoordinatorSettings`（`FluentPageViewModels.cs:1372-1383`）；这是实际接收通知的方法调用，不再依赖 coordinator 同值 SaveAsync 发 Changed。没有断言通知次数，但反射查找及调用是必经步骤，且实际方法非空实现已核对；无条件 `Draft=canonical` 的错误处理会让完整 Draft equality 和 IsDirty 断言失败。

只删除 `:1392-1395` 的 early-return 不保证测试失败，因为后面的 frontend-only 比较对同值也可保留 draft；这不是本轮测试失效，不能把这种等价正确行为当反向失败要求。新增 clean+Contrast `:124-134` 用真实 SaveAsync、settle 条件和 canonical 全记录/clean 断言；dirty frontend merge 后 Contrast `:188-204` 仍保留。**R-021 闭环**，但这不是 Layout 等所有字段的完整笛卡尔矩阵，也未实跑改坏代码的 mutation。

### 4. R-007、兼容路径与剩余回归

reviewer 指 r5 是当前已完成报告，delivery/head/handoff/索引均指同一返修版本，canonical=pending、integration_commit=null、Task in_progress 适合尚未集成状态。问题仅在 r6 appointment 仍称待派，与 STATUS/PLAN、handoff 派发及本次执行不符；本报告不代 DSH 修改这些字段。

standalone `FluentShell.axaml.cs:43-45` 继续把 surface 回调接到自己的 Window；其按钮/F 接线没有被稳定宿主替换。standalone 的 Esc/离开 Reader 未挂 CurrentPageChanged，原先可能留在全屏非 reader 页的行为在 base `cbfb7bbc9` 已存在，本轮未新增，不列作此次返修回归，也不宣称本轮修复了 standalone Esc。V2 的 TopLevel handler 激活规则、退出状态聚合、selector 和唯一 appearance 写者均未被本轮增量改写；全量包含既有 Fluent facade、V2 键盘和关闭测试并通过。没有有据可报的新焦点/无障碍回归，但 Raw accessibility 和 headless Focus 不是原生 IME、Tab 遍历或屏幕阅读器证据。

新增的**窗口模式失败补偿残余 R-022** 是静态可达问题：提升到 V2 已清掉旧 Fluent 全屏；后续持久化或 journal finalize 失败时仅恢复旧树/id/settings，返回 Fluent 分支只重接回调，没有快照恢复全屏。旧阅读页和数据仍在，VM/Window 均 Normal，可按 F 恢复，所以定为 P2，区别于原 R-020 的主路径完全不可用。未运行额外故障探针，不能称运行复现。

## Findings

仅计仍需处置项：**P0=0 / P1=0 / P2=2**。不把既有如实登记的 AC PARTIAL 或 D-1 原生设备缺口重复报成新增代码缺陷。

| ID | 级别 | 文件/行 | 触发、影响及依据 | 证据性质 | 可执行建议 | 状态 |
|---|---|---|---|---|---|---|
| R-022 | **P2** | `Views/Presentation/PresentationWindow.cs:165-192`；`Services/FrontendHostCoordinator.cs:138-175,292-305`；Presentation `Switching/FrontendSwitchCoordinator.cs:113-145` | 全屏 Fluent Reader→V2，Promote 先换树，触发 ExitFullScreen/Normal；随后 SaveAsync 或 journal finalize 失败则 RestoreContent(previous)。回到 Fluent 只接回调，原 VM/Window 全屏模式未恢复；失败响应仍改变旧窗口模式。Task AC1 `:238`、方案 §7.1 `:382` / §7.3 `:404` / §15.5 `:909,928` 要求完整窗口回滚/保留全屏意图。页面/业务数据不丢、状态最终一致且用户可按 F 恢复，故 P2。 | **静态必经调用链确认**，两辅助审查确认；未运行故障复现。新全屏测试只测成功切换，现有 finalize 故障测试不同时检查全屏窗口。 | 将切换前 WindowState/reader fullscreen 纳入事务快照与失败补偿；成功离开仍按当前策略清理。补真实宿主“全屏→提升后 Save/finalize 失败→旧树、VM 和原 WindowState 一并恢复”的回归，并验证普通/最大化路径不受影响。 | open，新发现；由 DSH 修复或书面处置 |
| R-007 | **P2** | `doc/tasks/FEA-07.md:10,232,235`；`verification/FEA-07/evidence-index.md:9`；handoff `:28` | 当前仍写 r6 待派/待办，而本次已经执行 r6，STATUS/PLAN 也写进行中。delivery 与 latest completed r5 指针正确，canonical=pending 合理；不再是交付不可追溯的 P1。 | 当前文件、Git 与实际 r6 委派直接核对。 | DSH 处置本报告时将 latest Review/source、reviewer 与 r6 appointment 文案统一；集成与 residual 处置前继续 pending/in_progress。保留历史报告字节。 | open，r5 残余 |

## AC 逐条 Verdict

| AC | r6 Verdict | 依据与未覆盖范围 |
|---|---|---|
| AC1 | **PARTIAL** | 真实树 100 次切换、页面/draft/V2 会话字段、真实 staging 门禁、输入隔离及原失败补偿测试通过。完整 window rollback 新残余 R-022/P2；原生 IME、真库 DB/current/pinned/Lock/source/candidate 零变化、ACK 重连、真实 Run/Intent 仍待补。 |
| AC2 | **PARTIAL** | 全 cache 退出聚合、生产 Theme Studio draft provider 和真实关闭阻断通过；真实双窗口归属/Session Region 单写 owner/完整 Host 生命周期集成未补。 |
| AC3 | **PARTIAL** | previous journal、启动前恢复、finalize settings/id/UI 补偿及排队屏障通过；窗口模式补偿见 R-022，真实进程 kill 与暂停期间保护状态变化未验。 |
| AC4 | **PARTIAL** | planner.Selection 单源、warnings fail-safe、启动构造矩阵通过；真实 App 初始化及坏包/scale 完整矩阵仍无证据。 |
| AC5 | **BLOCKED / D-1（原生矩阵）** | **headless 全屏主路径恢复 PASS**：按钮/F/Esc→真实稳定 WindowState、成功切换前后及隐藏请求；memento/topology/manifest 机械部分通过。全屏失败补偿有 R-022/P2。原生双屏/拔屏/换主屏/DPI 100/125/150/200%、混合 DPI/第二窗回迁仍 BLOCKED，绝不以 headless 代替。 |
| AC6 | **PARTIAL；W-5 PASS** | 固定记录 p95 248.42ms，本轮独立 Release 244.91ms，均≤1000ms；UI freeze 是事务总时长上限，真实渲染冻结采样、规模合成 workload/原生指标仍缺。 |
| AC7 | **MET（已列机械/headless 范围）** | build 0/0，全量 1134/0/57；启动兼容、依赖方向与 TFM 门禁通过。57 跳过链路不能当作已验。 |
| AC8 | **PARTIAL** | 临时根、两生成器、治理、冻结 pins、18/18 Task pins 均通过；R-007 appointment 文案残余、原生截图/矩阵仍缺。 |

## 证据与治理核对

本节检查均为本轮 **executed**；环境为 **Windows NT 10.0.26300.0 / PowerShell 7.6.8 / .NET SDK 10.0.401 / test runtime .NET 9.0.11**，项目仍为 net9.0。执行输出由本报告记录，未写额外证据文件；既有日志只读保留。以下 exit 均为本轮工具返回值，不是从历史日志抄录。

| 场景 | 实跑命令/核对步骤 | 结果 | 证据与适用边界 |
|---|---|---|---|
| HEAD / 工作区 / 日志 | `git rev-parse HEAD`；`git status --short`；`git log --oneline -8`；branch/common-dir | **PASS** | HEAD `80b2203e512392a38452a24fff983d719775b1f0`，main/.git，起始与落盘前 clean；8 条日志见前文。 |
| 累计范围 | `git diff --stat cbfb7bbc9..HEAD`；`git diff --name-only cbfb7bbc9..HEAD`；逐路径 glob 匹配 Task | **PASS** | 79 files / +7757 / -562；79/79 合法、0 越界，附录 A。 |
| 代码无漂移 | `git diff --name-only 4e8510d43..HEAD`；`git diff --quiet 4e8510d43 HEAD -- apps/desktop-avalonia` | **PASS，exit 0** | 仅 9 docs/evidence；源码 Git tree 指纹一致，见 Reality Check。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **PASS，exit 0，0 warnings / 0 errors** | 本轮真实源码；耗时 4.67s。 |
| 全量测试 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **PASS，exit 0，1134 passed / 0 failed / 57 skipped** | App 1m38s；逐项目计数与 skip 原因见下表。较 r5 +2 passed，较 Task 基线 1034 +100，fail/skip 不增。 |
| 定向复跑 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter "FullyQualifiedName~FluentFullScreenRequests_DriveTheStableWindowState\|FullyQualifiedName~SettingsDraftSyncTests" --logger "console;verbosity=normal"` | **PASS，exit 0，9/0/0** | 全屏组合根 1 + SettingsDraftSync 8；原命令过滤符是普通 `|`，表格中仅为 Markdown 转义。两组在全量及定向运行均通过。 |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | **PASS，exit 0** | 292 rows；every generated artifact matches frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | **PASS，exit 0** | generated theme artifacts match frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | **PASS，exit 0，3 warnings** | 10 个非终态 Task、STATUS 3161 bytes/29 lines 与 PLAN 4744 bytes/64 lines 预算告警；既有 warning 不替代语义 Review。报告落盘后再检查仍 PASS。 |
| 冻结契约 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | **PASS，exit 0，15/15** | 14 契约 + FEA-01；与 Task evidence pins 是两类不同检查。 |
| Task evidence pins | 解析 Canonical Evidence，逐文件 SHA-256，再按路径匹配索引唯一行 | **PASS，18/18** | 17 CANONICAL + 1 SUPPORTING，实测完整 SHA 见附录 B；索引无自身 SHA 行、非法控制字符 0。 |
| final evidence | 核日志 head、实际 SHA、Task/索引 pin；核 head 后无源码漂移 | **PASS** | 日志绑定 `4e8510d431ac82df54b82991d14975da5c27f9a0`；SHA **`3021dbb071c71e450d08827ebbcdd3e1e1a1334a85cc787188e7ab1de2e1fa64`**。 |
| rework-r5 / handoff | 过程日志与最终日志/精确交付对照 | **PASS（过程证据）** | rework 标明 ea27a7b10 + uncommitted rework，不冒充精确 delivery；final log 在提交后绑定 4e8510d43。handoff delivery/测试数/性能与当前文件一致。 |
| 性能三方与分位数 | JSON、摘要、Task 当前 AC6/测试表、索引、handoff；排序重算 20 样本 | **PASS，W-5 PASS** | 记录 p50 96.50 / p95 248.42 / max 349.30ms、+2528B、handles 0；两次历史复测 p95 236.48/248.42ms。详见下节。 |
| 独立 Release 性能 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj -c Release --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter FullyQualifiedName~PerformanceBaselineTests --logger "console;verbosity=detailed"` | **PASS，exit 0，1/0/0** | 本轮独立 p50 99.14 / p95 244.91 / max 681.76ms，冷首次 635.09ms，+20560B / +3 handles；为独立 run，不回写 canonical JSON。 |
| 原生矩阵 | 双屏/拔屏/换主屏/混合 DPI 100/125/150/200% | **BLOCKED / D-1；NOT_RUN** | 本轮未运行原生产品和设备矩阵；headless WindowState 断言不作为原生证据。 |

### 全量计数与 skip 直接原因

| 测试项目 | passed | failed | skipped | 原因与核对依据 |
|---|---:|---:|---:|---|
| Appearance | 21 | 0 | 0 | 无跳过。 |
| Presentation.Avalonia | 38 | 0 | 0 | 无跳过。 |
| Host | 51 | 0 | 28 | `HostSidecarFactAttribute` → `HostFixture.TryGetSidecarDirectory`；当前 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置，先于目录/可执行文件检查返回 skip。 |
| ThemeEngine | 253 | 0 | 0 | 无跳过。 |
| DesignSystem | 87 | 0 | 0 | 无跳过。 |
| ApplicationCore | 31 | 0 | 0 | 无跳过。 |
| CoreClient | 128 | 0 | 22 | `SidecarFactAttribute` 及相关 fixture facts → `SidecarFixture.TryGetSidecarDirectory`；同一 env 未设置。 |
| App | 525 | 0 | 7 | 2 CreateChapterHostIntegration、1 WritePolicyUiIntegration、1 StartupSelfCheckUi、3 RunControllerHostIntegration；各 Fact 在 HostFixture/RunFixture sidecar 检查处先 skip，直接原因同上。 |
| **合计** | **1134** | **0** | **57** | **总计 1191；28+22+7=57**。与 final/rework/STATUS/PLAN/索引一致。 |

skip 的下游 BOOK/S4 seeded fixture 缺失并不是本次先触发的原因。源码依据：Host `Support/HostFixture.cs:13-20`、CoreClient `Support/SidecarFixture.cs:28-35`、App `ChapterCreationTests.cs:260-285`、`RunControllerTests.cs:446-490`、`WritePolicyUiTests.cs:132-141`。没有设置 sidecar env 或用空夹具把 skip 转为 PASS。

### 性能口径与稳定性

canonical Release JSON 的 20 个样本按 nearest-rank 重算：p50 为排序第 10 项 **96.50**，p95 为第 19 项 **248.42**，max 为 **349.30**。冷首次 **612.38ms** 不计入热样本；4 次预热、**20 次单向切换（10 次往返）** 与摘要一致。Task 当前 AC6、测试表、索引、handoff 的 p50/p95/max/内存/句柄及两次复测 236.48/248.42 均一致；历史段旧值明确属于旧 head，不混算。

本轮独立 Release p95 **244.91ms**，与两次 canonical head 复测接近，满足 **W-5 p95≤1000ms**。独立 run 的最大样本 681.76ms、+20560B、+3 handles 与记录值不同，反映短样本/初始化噪声；这些不是门槛字段，也不能据一次差值推断泄漏或声称所有机器稳定。本次短时性能采样不构成长期内存/句柄泄漏验证。12 样本 nearest-rank 的 p95 等于 max 仍是合法分位数计算；增加到20改善尾部分辨率，没有改 W-5 数值。UI freeze 继续仅为切换事务总时长上限估计，真实负载/原生指标未补，故 AC6 不升级为 MET。

## Architecture 与 Verification 结论

**Architecture：在本次实施复核范围可批准，保留 R-022/P2。** App→Presentation 的允许依赖、Host/Core/ApplicationCore 禁向、net9.0、appearance 单写者、前端缓存及稳定 Window 边界保留；未发现新增源码写域、共享契约、schema、依赖或源文件保护越界。全屏主桥接方向正确，窗口模式补偿尚不完整；不把该 P2 等同于完整事务状态已经验收。

**Verification：指定实跑与关键返修回归通过；不签发完整原生验收。** build、1134/0/57、定向 9/0、两生成器、治理、15/15 契约 pins、18/18 Task pins 及独立 Release W-5 均 PASS。R-020/R-021 有真实入口与判别断言；R-022 仅静态确认，未做故障运行复现。AC1/2/3/4/6/8 PARTIAL，AC7 在已列范围 MET，AC5 原生 BLOCKED/D-1。批准基于未解决 P0/P1=0 与本轮关键返修验证通过，**不等于所有 AC 已满足，也不代替 DSH 的 residual/waiver、集成或 Task done 裁决**。

## 结论与复审

**Decision：`approved`（P0=0 / P1=0 / P2=2）。** R-020 原 P1 与 R-021 已闭环；可交 DSH 进行 findings 处置及集成准备。R-007 与 R-022 为需明确处置的 P2，不能默认为已关闭；本报告不授予 push 或 Task 关闭授权。

最小处置/返修集：

1. DSH 统一 r6 reviewer/source、最新报告与 appointment 文案，保留历史报告原字节，集成完成前保留 canonical=pending/in_progress。
2. R-022 建议补窗口模式快照/补偿和全屏失败回滚回归；如决定延期，须由 DSH 书面记录影响、归属与后续 Gate。若修代码，固定新 head、重跑相关与全量检查，再 Appointment fresh 上下文复核受影响范围；本批准不自动沿用新 head。
3. DSH 明确处置已有 PARTIAL 和 D-1 原生矩阵 residual/waiver，完成集成验证后才决定 Task 生命周期。原生矩阵继续 BLOCKED，不能把本轮 headless PASS 改写为原生 MET。

推荐下一步：**Agent=DSH，继续当前 FEA-07 的 r6 findings 处置与集成验证准备**；尚不自动释放 proposed 的 `FEA-06-RESIDUAL-1`。可直接转发：

> 在 `G:\CODEX\New Manga`、branch `main`、common dir `.git`，先核对最新 Git/dirty，保留他人内容及 `doc/reviews/FEA-07-impl-r6.md`。Recovery：Task FEA-07，base `cbfb7bbc92d489541a24290038eae2117f8aa1ce`，reviewed head `80b2203e512392a38452a24fff983d719775b1f0`，代码 head `4e8510d431ac82df54b82991d14975da5c27f9a0`。本次 approved（0/0/2），请处置 R-007 appointment 文案及 R-022 全屏失败回滚残余；只在 Task allowed_paths 内修改必要 App/Presentation/测试及当前 Task 交付文档，不改冻结契约、Core/schema/依赖、生成物或真实用户数据，新增共享面先冻结范围。交付 findings disposition、必要固定修复 commit、全屏失败补偿测试与精确 head 的 handoff/verification/index/pins。按本报告命令验证 build 0/0、全量无新增 fail/skip、两 --check byte-for-byte、check PASS、契约 pins 15/15、Task artifact pins 全匹配及 Release p95≤1000ms；记录真实 skip 与 blocker。改代码则重新独立复核；未改代码也须完成集成检查并处置 PARTIAL/D-1，才能决定 done/canonical complete。不要自动释放 FEA-06-RESIDUAL-1，不 push。

## 只读与最终状态

本报告仅对上述固定 reviewed/code head 有效。Git 代码 tree 指纹、起始/落盘前 clean 检查及落盘后仅新增本报告的工作区检查共同约束只读范围；本轮没有 commit/push。证据索引自身文件 SHA-256 为 **`d5b9f5b2ca081cd87b81d621d83443cee727723026a2342567d52f2c2051ecb2`**，只在本报告外部记录，不回写索引自 pin。报告落盘后的治理检查与最终状态见本报告所列核对；任何随后外部提交不自动纳入本批准。

## 附录 A：累计变更逐路径 allowlist 核对

下表由固定 `cbfb7bbc9..80b2203e5` 的 79 条路径逐一匹配 Task front matter；不含本轮新报告。

| 变更路径 | 匹配 allowed_paths |
|---|---|
| `apps/desktop-avalonia/NewManga.sln` | `apps/desktop-avalonia/NewManga.sln` |
| `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs` | `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs` |
| `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` | `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` |
| `apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj` | `apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj` |
| `apps/desktop-avalonia/src/NewManga.App/Services/FrontendHostCoordinator.cs` | `apps/desktop-avalonia/src/NewManga.App/Services/**` |
| `apps/desktop-avalonia/src/NewManga.App/Services/IPresentationExitState.cs` | `apps/desktop-avalonia/src/NewManga.App/Services/**` |
| `apps/desktop-avalonia/src/NewManga.App/Services/IPresentationInputState.cs` | `apps/desktop-avalonia/src/NewManga.App/Services/**` |
| `apps/desktop-avalonia/src/NewManga.App/Services/SafeStartupPlanner.cs` | `apps/desktop-avalonia/src/NewManga.App/Services/**` |
| `apps/desktop-avalonia/src/NewManga.App/Shell/V2/AppShellV2.axaml.cs` | `apps/desktop-avalonia/src/NewManga.App/Shell/**` |
| `apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/FluentPageViewModels.cs` | `apps/desktop-avalonia/src/NewManga.App/ViewModels/**` |
| `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShell.axaml` | `apps/desktop-avalonia/src/NewManga.App/Views/**` |
| `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShell.axaml.cs` | `apps/desktop-avalonia/src/NewManga.App/Views/**` |
| `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShellSurface.axaml` | `apps/desktop-avalonia/src/NewManga.App/Views/**` |
| `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs` | `apps/desktop-avalonia/src/NewManga.App/Views/**` |
| `apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs` | `apps/desktop-avalonia/src/NewManga.App/Views/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Hosting/FrontendContentHost.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Lifecycle/ExitCoordinator.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/NewManga.Presentation.Avalonia.csproj` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Switching/FrontendSwitchCoordinator.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Switching/SwitchJournal.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Switching/SwitchStage.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DisplayTopology.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/WindowBroker.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/WindowStateMemento.cs` | `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/ArchitectureDependencyTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/DpiManifestTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/FrontendHostCoordinatorTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/PerformanceBaselineTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/PresentationHostCompositionTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/PresentationInputRoutingTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/PresentationWindowTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/SafeStartupPlannerTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsDraftSyncTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/StartupCompatibilityMatrixTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/StartupDecisionTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/DisplayTopologyTests.cs` | `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/ExitCoordinatorTests.cs` | `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/FrontendSwitchCoordinatorTests.cs` | `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/GlobalUsings.cs` | `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj` | `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/SwitchJournalTests.cs` | `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/WindowBrokerTests.cs` | `apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**` |
| `doc/REBASELINE_PLAN.md` | `doc/REBASELINE_PLAN.md` |
| `doc/STATUS.md` | `doc/STATUS.md` |
| `doc/TASK_LEDGER.md` | `doc/TASK_LEDGER.md` |
| `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` | `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` |
| `doc/handoffs/FEA-07-impl-r1.md` | `doc/handoffs/FEA-07-*.md` |
| `doc/handoffs/FEA-07-impl-r3.md` | `doc/handoffs/FEA-07-*.md` |
| `doc/handoffs/FEA-07-impl-r4.md` | `doc/handoffs/FEA-07-*.md` |
| `doc/handoffs/FEA-07-impl-r5.md` | `doc/handoffs/FEA-07-*.md` |
| `doc/handoffs/FEA-07-resume-2026-11-02.md` | `doc/handoffs/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r1.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r2.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r3.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r4.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r5.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-scope-r2.md` | `doc/reviews/FEA-07-*.md` |
| `doc/tasks/FEA-07.md` | `doc/tasks/FEA-07.md` |
| `verification/FEA-07/evidence-index.md` | `verification/FEA-07/**` |
| `verification/FEA-07/final-evidence.log` | `verification/FEA-07/**` |
| `verification/FEA-07/generators-check.log` | `verification/FEA-07/**` |
| `verification/FEA-07/performance-baseline-debug.json` | `verification/FEA-07/**` |
| `verification/FEA-07/performance-baseline-release.json` | `verification/FEA-07/**` |
| `verification/FEA-07/performance-baseline.md` | `verification/FEA-07/**` |
| `verification/FEA-07/rework-part1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/rework-part2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/rework-r3-part1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/rework-r3-part2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/rework-r4-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/rework-r5-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2b-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2c-part1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2c-part2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-3-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-4-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-5-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-6-gapclosing-verification.log` | `verification/FEA-07/**` |

## 附录 B：18 个 Task pins 逐项 SHA-256

每行均已计算实际文件字节的 SHA-256，并与 Task 记录及索引唯一对应行比较；三方一致列全部为 PASS。

| evidence_id | 实际文件 | 实测 SHA-256 | Task / 索引 |
|---|---|---|---|
| EV-FEA07-SLICE1 | `verification/FEA-07/slice-1-verification.log` | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` | PASS / PASS |
| EV-FEA07-SLICE2 | `verification/FEA-07/slice-2-verification.log` | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` | PASS / PASS |
| EV-FEA07-SLICE2B | `verification/FEA-07/slice-2b-verification.log` | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` | PASS / PASS |
| EV-FEA07-SLICE2C1 | `verification/FEA-07/slice-2c-part1-verification.log` | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` | PASS / PASS |
| EV-FEA07-SLICE2C2 | `verification/FEA-07/slice-2c-part2-verification.log` | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` | PASS / PASS |
| EV-FEA07-SLICE3 | `verification/FEA-07/slice-3-verification.log` | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` | PASS / PASS |
| EV-FEA07-SLICE4 | `verification/FEA-07/slice-4-verification.log` | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` | PASS / PASS |
| EV-FEA07-SLICE5 | `verification/FEA-07/slice-5-verification.log` | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` | PASS / PASS |
| EV-FEA07-PERF | `verification/FEA-07/performance-baseline-release.json` | `8e031becf9fcd38d2448d6758ddfab33ee566560b6a1873e270566a932561ed6` | PASS / PASS |
| EV-FEA07-GAPCLOSING | `verification/FEA-07/slice-6-gapclosing-verification.log` | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` | PASS / PASS |
| EV-FEA07-GENERATORS | `verification/FEA-07/generators-check.log` | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` | PASS / PASS |
| EV-FEA07-FINAL | `verification/FEA-07/final-evidence.log` | `3021dbb071c71e450d08827ebbcdd3e1e1a1334a85cc787188e7ab1de2e1fa64` | PASS / PASS |
| EV-FEA07-PERF-MD | `verification/FEA-07/performance-baseline.md` | `f18dbb25c731cf77c2d6911385f0d18f865c20b691f626438883faebe6d13498` | PASS / PASS |
| EV-FEA07-REWORK2 | `verification/FEA-07/rework-part2-verification.log` | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` | PASS / PASS |
| EV-FEA07-REWORK-R3-1 | `verification/FEA-07/rework-r3-part1-verification.log` | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` | PASS / PASS |
| EV-FEA07-REWORK-R3-2 | `verification/FEA-07/rework-r3-part2-verification.log` | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` | PASS / PASS |
| EV-FEA07-REWORK-R4 | `verification/FEA-07/rework-r4-verification.log` | `f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b` | PASS / PASS |
| EV-FEA07-REWORK-R5 | `verification/FEA-07/rework-r5-verification.log` | `e773a93def145d258ff09f8cb02ae9783823e7588e06443de28ba3381a3619b9` | PASS / PASS |
