---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r5；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: ea27a7b10a486e50cd9068c67b5d3085c6508b11（文档/证据 head；代码 head b328f3488）
code_head: b328f3488615fcad10e455e6f1196e6622cbb889
decision: changes_requested
counts:
  P0: 0
  P1: 1
  P2: 2
---

# Review：FEA-07 第 5 轮实现复核（impl-r5）

## Reviewer 身份与来源

本报告由用户指定的 fresh Codex CLI 独立上下文执行，未参与 FEA-07 设计、实现或返修。主会话阅读代码、核对证据并实跑验证；辅助只读审查来源为 `/root/standards`、`/root/spec` 两个子任务，均未修改文件或参与实现。Standards、Spec、Architecture、Verification 四个视角均为 executed。全屏接线发现由主会话定位，Spec 子任务独立确认；本报告对合并后的结论负责。

唯一主动交付写入为本报告；未修改源码、测试、Task、状态、既有证据或用户数据，未 commit/push，未进入其他 linked worktree。执行用户明确要求的 build/test 产生常规忽略构建输出和测试自带的临时夹具；额外 Release 性能用例也使用自身临时 theme/settings 根，输出自身 `%TEMP%` 指标 JSON。未使用真实 `%APPDATA%/NewManga`，未启动连接真实数据的产品，未创建外部探针或修改被审代码做 mutation test。

## 范围与 Reality Check

- 起始及报告落盘前 `HEAD=ea27a7b10a486e50cd9068c67b5d3085c6508b11`，`main`，common directory `.git`，`git status --short` 为空。用户给出的 front matter 示例 `ea27a7b1c` 与实际 Git 不同，本报告绑定上述真实完整 SHA。
- 累计范围 `cbfb7bbc9..HEAD`：**76 files changed / 7037 insertions(+) / 562 deletions(-)**；逐路径匹配 Task `allowed_paths`：**76/76，越界 0**，附录 A 记录每条路径及匹配规则。
- `b328f3488..HEAD` 仅 9 个 docs/evidence 文件：STATUS、PLAN、rolling checkpoint、impl-r4 handoff、impl-r4 Review、Task、索引、final log、性能摘要。`git diff --quiet b328f3488 HEAD -- apps/desktop-avalonia` exit 0，无源码或测试漂移。
- **代码行号全部以 `b328f3488` 为准**；文档行号按真实 reviewed head。下文同名简写均指 `apps/desktop-avalonia/src/NewManga.App/` 或 `tests/NewManga.App.Tests/` 下对应唯一文件。
- 按要求先读 r4，再核对 r3/r2/r1、当前 Task/STATUS/PLAN/rolling checkpoint、指定日志、索引、性能 JSON/摘要和 handoff。架构依据为 AD-002（含 AD-003 修订边界）、C-03 §2.1、Task 冻结范围及协作协议 §4/§5.1/§6；旧报告仅用于定位待核项，没有把其判断当作本轮实现事实。

实际 `git log --oneline -8`：

```text
ea27a7b10 docs(fea-07): impl-r4 处置 + 返修证据/索引 + delivery/生命周期固定（head b328f3488；全量 1132/0/57）
b328f3488 fix(fea-07): r4 返修（R-017 canonical 快照同步 / R-002 真实 Theme Studio draft 验证 / R-013 排队屏障 / R-018 Loaded 订阅解绑 / R-019 staging 输入隔离）；全量 1132/0/57
ad56bea1c docs(fea-07): r3 返修 part2 处置 + 精确 head 证据/索引 + delivery/生命周期固定（head 100d487ff；全量 1119/0/57）
100d487ff fix(fea-07): r3 返修 part2（R-001 真实 staging Loaded/Rendered 门禁 + 状态覆盖；R-002 隐藏缓存树退出聚合 + V2 Theme Studio draft）；全量 1119/0/57
cc34f36e1 docs(fea-07): 新会话恢复材料（handoff + checkpoint）
6a31fb92e fix(fea-07): r3 返修 part1（R-015 journal finalize 补偿 + R-013 并发确定性测试 + R-009/R-016/R-007）；全量 1115/0/57
52474fcbf docs: 记录 Codex 模型 ID 与 reasoning effort 实测结论
7b62c492b docs(fea-07): checkpoint r3 复核派发记录
```

## r4 findings 闭环表

| ID | r4 状态 | r5 结论 | 本轮依据与残余 |
|---|---|---|---|
| R-017 | P1 open | **生产缺陷闭环；测试残余另列 R-021/P2** | `FluentPageViewModels.cs:1390-1405` 按 old/new canonical 判断 frontend-only；Mode clean/dirty 回归能够拦住 r4 错误实现。重复通知用例实际不发通知，不能宣称完整覆盖。 |
| R-002 | P1 验证 open | **闭环** | `PresentationHostCompositionTests.cs:301-367` 使用生产注册 VM/service 造真实 draft，不替换 provider，真实取消后 HasUnsavedEdits 清除；移除 provider 后同一真实 draft 不再拦关闭，排除隐藏树/staging 的其它 blocker 假通过。 |
| R-013 | P1 判别力 open | **闭环；持久值断言有小范围限制** | `FrontendHostCoordinatorTests.cs:208-251` 首事务持门暂停，第二同目标请求明确未完成；补偿后第二请求真实切到 Fluent。两响应、内容、current id、canonical appearance、journal 均检查；appearance 未独立重读磁盘，不能称已有磁盘断言。 |
| R-018 | P2 open | **原订阅泄漏闭环** | `FrontendHostCoordinator.cs:120-133,183-187,317-340` 追踪原 handler，事务 finally 等待真实解绑后释放门。反射测试仅直接证明 tracking 清空，不直接证明事件表为空；源码存在实际 `-=`。 |
| R-019 | P2 open | **原 staging 快捷键缺陷闭环** | coordinator `:199-204,292-305` 控制激活；`AppShellV2.axaml.cs:98-110,170-175,205-254` 挂摘和守卫正确；真实 headless 路由测试有可见控件收键和 palette 状态断言。新发现全屏桥接遗漏另列 R-020，不把其混入原 tunnel handler 缺陷。 |
| R-007 | P2 open | **交付指针主体正确；appointment 文案仍 open/P2** | delivery/handoff/final head 已一致，canonical pending 合理；Task reviewer 及索引仍“r5 待派”，STATUS/PLAN/checkpoint 已是 r5 进行中，本次也确已执行。 |
| R-009 | 数值错配已闭环 | **维持数值闭环；AC6 PARTIAL** | 摘要/JSON/Task/索引/handoff 当前值一致，样本排序重算一致；独立 Release 复测 W-5 PASS。20 样本改进分位数分辨率，不构成门槛数值变更；与 12 样本不可直接比较。 |
| R-001 | 原门禁已闭环 | **维持；AC1 PARTIAL** | staging live Grid、真实几何/Loaded/animation frame 门禁仍存在（`PresentationWindow.cs:68-86`；coordinator `:196-288`）；100 次真实树状态保留测试仍在。原生 IME/真库/ACK/Run/Intent 未补齐。 |
| R-003 | 已闭环 | **维持；AC3 PARTIAL** | journal previous 与启动前恢复接线仍在，`App.axaml.cs:74-77,332-377`；真进程 kill、保护状态变化仍未验。 |
| R-004 | 已闭环 | **维持；AC4 PARTIAL** | `App.axaml.cs:77-92` 使用 planner Selection；`SafeStartupPlanner.cs:64-90` warnings fail-safe；真实 App 初始化及坏包/scale 矩阵未补。 |
| R-005 | 接线闭环 | **维持原范围；AC5 原生 BLOCKED** | 屏幕枚举/clamp、最大化恢复仍在；不能把纯 topology policy 当作真实拔屏/混合 DPI 集成。全屏遗漏是本轮另行确认的 R-020。 |
| R-006 | closed | **维持** | 新增测试/性能使用临时 theme/settings/journal 根；本次未运行真实用户数据产品。 |
| R-008 | closed | **维持** | 76/76 变更路径匹配 allowlist，附录 A。 |
| R-010 | closed | **维持** | `App.axaml.cs:218-238` 每种前端缓存一个树；原 VM 重建问题与 Loaded 订阅问题分别核验。 |
| R-011 | closed | **维持** | 17/17 Task evidence pins 三方一致，索引无自身 SHA。 |
| R-012 | closed | **维持** | 本轮两生成器实跑 exit 0、byte-for-byte up-to-date。 |
| R-014 | closed | **维持** | `PresentationWindow.cs:59-65,123-130` 最大化恢复/捕获保留。 |
| R-015 | closed | **维持普通 finalize 故障补偿闭环** | coordinator `:138-175` 恢复 UI/settings/id；Presentation `FrontendSwitchCoordinator.cs:119-145` journal rollback 失败不阻止 UI 补偿。未扩张为持续磁盘故障全恢复保证。 |
| R-016 | closed | **维持** | 索引非法控制字符 0；final 路径正常；无自身 SHA。 |

## 本轮重点实现判断

### R-017：canonical 快照、草稿与唯一写者

构造 `FluentPageViewModels.cs:1048-1051` 初始化 `_observedSettings`，`LoadAsync:1113-1116` 同步 Draft 与快照。`ApplyCoordinatorSettings:1390-1405` 先处理同值，再更新观察快照，用 `previous with { FrontendId = settings.FrontendId }` 与新 canonical 全记录比较；只有 frontendId 单字段变更保留 draft 其余字段，Mode、Contrast、Layout 等任何真实差异均走 canonical 镜像，不再拿 dirty draft 判断变化类型。保存 `:1174` 仍调用 `AppearanceCoordinator.SaveAsync`，Changed 处理更新快照；没有新增持久化写者，符合 C-03 §2.1。

后台 Changed 经 `:1372-1384` Post 到 UI，再读取最新 canonical，属于最新状态同步，并非逐通知保存事件快照。当前串行切换的 frontend commit/rollback 合并仍保持最终 id 和 draft；没有据此推断逐事件中间状态都已被实测。保存路径没有另加快照赋值，依赖 Changed 路径；同值保存本就没有 canonical 差异。Load 与保存路径未见本轮可证实的快照回退错误。

`SettingsDraftSyncTests.cs:68-120` 覆盖 clean/dirty × frontend-only/Mode；`:142-157` 覆盖顺序 commit+rollback；`:162-176` 覆盖 dirty frontend 合并后的真实 Contrast 变化，**未覆盖 clean Contrast，也不是完整 clean/dirty × Contrast 笛卡尔矩阵**。这些核心变更测试对 r4 实现有判别力；但 `:124-134` 的“重复通知”实际上无 Changed（`AppearanceCoordinator.cs:73-77`），另列 R-021。未运行改坏代码的反向 mutation，不把静态判别分析称为实跑反向证据。

### R-002：真实 Theme Studio 退出保护

`PresentationHostCompositionTests.cs:320-338` 从 `GetSurfaceWorkspace(ThemeStudio)` 取生产 adapter 的 VM 和真实 `ThemeEngineThemeStudioService`，等待初始化，再由 Editor 造 unapplied draft；没有用 `()=>true` 覆写生产 provider。真实 provider 位于 `App.axaml.cs:401`，`AppShellV2.HasUnsavedEdits:91` 读取它。

测试 `:326-348` 验证初始 clean、draft true、HasUnsavedEdits true、关闭取消、真实 CancelPreview 后 draft/HasUnsavedEdits false。**取消后没有立即再调用 Close**，故不将其表述为“取消后同一步已实测关闭放行”。随后再次造 draft、确认取消，再移除 provider，Close 放行（`:350-367`）；这同时证明隐藏 Fluent/staging/cache 没有其它 blocker，弥补了没有逐树 clean 断言的局限。结合 `PresentationWindow.cs:132-177` 聚合逻辑，原双重假通过已消除；建议以后补取消后直接关闭的独立场景，非本轮 P1。

### R-013：失败事务与排队

`FrontendHostCoordinatorTests.cs:220-240` 用 ManualResetEventSlim 把首事务暂停在 journal finalize，持有外层 switch gate。首事务已暂设 Fluent，第二请求也为 Fluent；若 no-op 判断仍在门外，会提前完成而触发 `Assert.False(second.IsCompleted)` 失败。释放后首事务失败回滚到 V2，第二必须执行真实 V2→Fluent 才能满足最终 Fluent 内容/id/appearance 和 journal 清理断言（`:242-251`）。不再是“第二回 V2、终态本就 V2”的假通过。

检查了两个响应及首失败原因；最终 appearance 断言为 `_appearance.FrontendId`，**没有重读 `AppearanceStore` 磁盘文件**。真实保存路径仍调用 Store，未发现生产丢写问题；建议补磁盘重读断言，以完全对应“持久值”的验证声明。屏障有 10s 上限、第二等待观察为 150ms，本轮全量通过；没有把一次通过当作长期无抖动证明。

### R-018：Loaded 清理、异常与测试有效范围

每事务原 handler 存字典并在 `finally:183-187` 等待 `ReleaseLoadedSubscriptionAsync` 完成后才释放 gate；没有让下一事务抢先覆盖同一缓存树 handler 的正常竞态。字典 Remove 幂等，真实 `Loaded -= handler` 在 UI dispatcher 上执行，未出现重复解绑。未进入事务前的 wait 取消没有创建订阅；进入事务后的失败、门禁超时、取消均到相同 finally。

清理函数 `:333-340` 仅捕获清理自身的 InvalidOperationException/ObjectDisposedException，**不会吞掉 layout/Loaded/render 原始失败**。它会在实际解绑前先移除 tracking；若清理确实抛这两类异常，计数 0 本身不证明事件已移除。本轮没有可达的运行期 cleanup 异常复现，不据此新增生产 finding。更稳健的防御是最终无条件释放 gate，并记录清理失败；dispatcher 关闭后的继续切换未验。

测试 `FrontendHostCoordinatorTests.cs:256-279,318-325` 在 6 次成功和一次零几何失败后反射读取字典，验证 tracking 生命周期，**不是事件表/弱引用直接泄漏测试**；删掉 `-=` 而保留 Remove 仍可能通过。原泄漏闭环依据为真实 `-=` 源码与持门清理结构，不能声称已独立实测 timeout/cancel 的订阅数量。

### R-019：staging 输入、V2 回归与原生限制

coordinator `:199-204` 在同一 UI 回调内挂 staging 后立即停用输入，中间没有 await；提交 `:292-297` 激活目标，回滚 `:301-305` 恢复旧树。移出可见槽时 V2 detach 自动摘 handler，缓存树的布尔值不等于仍有活动 TopLevel handler。

`AppShellV2.axaml.cs:170-175,205-254` attach 时按 active 挂载、detach 时摘除，标志避免双挂；`OnPreviewKeyDown` 再守卫。默认 active=true 保留 standalone V2 行为；未改 HandleKey/KeyMap 语义。Fluent 的 tunnel handler 绑定自身（`FluentShellSurface.axaml.cs:130`），不会截获可见兄弟树路由。

`PresentationInputRoutingTests.cs:62-80` 用 headless 键输入验证停用时 visible Button 收到 Ctrl+K、隐藏 palette 不开，激活后 palette 开，再停用恢复收键，具有判别力；coordinator 激活顺序、失败不激活及生产切换终态也有测试。全量包含既有 `V2ShellUiTests.cs:375-457`、`V2StudioPageTests.cs:459-486` 等键盘/文本输入保护测试并通过。未发现有代码依据的新焦点或无障碍回归；`AccessibilityView.Raw` 与 inactive 快捷键不能充当原生 IME、Tab 焦点遍历或屏幕阅读器验收。

### 新问题与稳定性

**稳定窗口漏接 Fluent 全屏请求，见 R-020/P1。** 这是累计范围中内容面抽取产生的可见行为回归，r4 增量没有修到；无需等待多屏设备即可修正接线。现有 facade 保留全屏订阅，故 facade 与既有 V2 键测试全绿不能覆盖新组合根。

共享 `NullHostController.Instance` 的 memento 清理位于 `PresentationHostCompositionTests.cs:226-232`，在全部 100 次保留断言之后执行，不在循环中复位，没有掩盖被验证的状态丢失；键路由用例先复位 Library 是确定作用域。清理未置于 finally，断言失败时可能污染后续测试，是夹具稳健性限制；本轮没有实际失败链证据，不新增生产 finding。20 样本性能用例独立运行约 7s，整套 App 2m6s，和交付日志 2m7s 接近；未见本轮计数或稳定性退化，不外推为所有机器性能保证。

## Findings

仅计仍需处置项：**P0=0 / P1=1 / P2=2**。P1 来自累计实现，不是把未跑原生矩阵重新包装为代码缺陷。

| ID | 级别 | 文件/行 | 触发、影响及依据 | 验证性质 | 可执行建议 | 状态 |
|---|---|---|---|---|---|---|
| R-020 | **P1** | `App.axaml.cs:229-238`；`Views/Fluent/FluentShellSurface.axaml.cs:119,164,342-344`；`Views/Fluent/FluentShell.axaml.cs:44-45`；`Views/Fluent/ReaderPageView.cs:78,172-175,205-214` | `--presentation-host=true` 下 Fluent Reader 点“全屏”或 F/Esc，Reader 改 IsFullScreen 后调用 surface 回调；新组合根直接建 surface，却从未订阅 FullScreenRequested，因此 WindowState 不变。唯一订阅在 standalone facade，基线 `cbfb7bbc9` 原 SetFullScreen 直接改窗口状态。违反 Task W-1 保持行为、P5/AC5 全屏切换要求。 | **静态调用链确认**：全 src 搜索唯一订阅；新 factory 与 PresentationWindow 均无桥接。未新增探针/未实跑按钮→WindowState，现有全绿套件不覆盖此接线。 | 在稳定宿主连接当前 Fluent surface 的全屏请求与同一 PresentationWindow 状态，避免缓存重复订阅及隐藏树控制窗口；补真实 CreatePresentationShell 组合根的按钮/F/Esc→WindowState 回归，覆盖切换前后与退出全屏。不要等待 D-1 硬件或以 VM 布尔断言替代窗口状态。 | open，新发现 |
| R-021 | **P2** | `SettingsDraftSyncTests.cs:124-134`；`AppearanceCoordinator.cs:73-77` | 名为重复通知的用例只做同值 SaveAsync；生产 coordinator 不发 Changed，故该用例没有执行待验证的通知处理。错误的“收到同值通知就 Draft=canonical”实现仍可能通过，现有覆盖声明过强。 | **测试控制流确认**，无 mutation 实跑；生产同值 guard 本身正确。Contrast 也仅有 dirty 合并后场景，非完整矩阵。 | 显式产生可观察的重复 Changed/调用生产通知接收路径，断言确实处理过且 draft 保留；补 clean Contrast。不要只删 early-return 当反向证明，因为后续 frontend-only 分支对同值也可保留 draft。 | open，新验证缺口 |
| R-007 | **P2** | `doc/tasks/FEA-07.md:10`；`verification/FEA-07/evidence-index.md:9` | reviewer 指 impl-r4 且说 r5 待派，索引仍待派；STATUS/PLAN/checkpoint 与本次事实均为 r5 已执行。delivery head、handoff、final pin 正确，canonical pending 在未批准时合理。 | 本轮 Git/文件及实际 appointment 直接核对。 | DSH 处置本报告时统一最新 Review/source 与 r5 appointment；保留历史报告原字节，当前继续 pending/in_progress；不得因报告落盘先置 complete/done。 | open，r4 残余 |

## AC 逐条 Verdict

| AC | r5 Verdict | 依据与未覆盖范围 |
|---|---|---|
| AC1 | **PARTIAL** | 真实树 50 往返/100 次、页/draft/会话 memento 保留、真实 staging 几何/Loaded/frame 门禁、失败补偿和输入隔离成立。真实 Host/Run/Intent、DB/current/pinned revision/Lock/source/candidate 零变化、ACK 重连、原生 IME/焦点和全部失败阶段真实矩阵仍未补齐。 |
| AC2 | **PARTIAL** | visible/staging/cache 退出状态聚合及真实 Theme Studio draft provider 已确认；真实双窗口归属、Session/Region 单写 owner 与完整 Host 生命周期集成仍待补。 |
| AC3 | **PARTIAL** | previous journal、启动前恢复、finalize 补偿和确定性排队通过；暂停期间保护状态改变、真实跨进程中断/kill 未验。 |
| AC4 | **PARTIAL** | Planner Selection 单源、appearance warnings fail-safe 和现有启动矩阵通过；真实 App 初始化入口及坏包/scale 完整矩阵未验。 |
| AC5 | **BLOCKED / D-1（原生矩阵）** | 原生双屏/拔屏/DPI 100/125/150/200%、混合 DPI、第二窗内容回迁无硬件证据，绝不升级为 MET。headless memento/topology/manifest 仅机械部分通过；另有无需该硬件即可确认的全屏接线 **FAIL：R-020**，不能用 D-1 豁免。 |
| AC6 | **PARTIAL；W-5 PASS** | 记录 baseline p95 313.95ms，独立 Release p95 314.65ms，均≤1000ms。UI freeze 仍是事务总时长上限，真实冻结采样/规模负载/原生指标未补齐。 |
| AC7 | **MET（机械/headless 已列范围）** | build 0/0，全量 1132/0/57；启动兼容、依赖方向、TFM 测试均通过。此项不抵销 R-020 未覆盖行为。 |
| AC8 | **PARTIAL** | 两生成器、治理、冻结 pins 和 Task evidence pins 通过，路径隔离有效；原生截图/矩阵缺失，部分针对性判别测试仍有上述限制。 |

## 证据与治理核对

本节均为本轮 executed，环境 **Windows 10.0.26300.0 / PowerShell 7.6.8**（`C:\Program Files\PowerShell\7\pwsh.exe`）/ **SDK 10.0.401 / net9.0 runtime 9.0.11**。被测代码树与 `b328f3488` 相同。运行输出摘录和退出码直接写入本报告，未追加既有 verification 日志。

| 核对项 | 命令/步骤 | 本轮结果 | 证据与限制 |
|---|---|---|---|
| Git | `git rev-parse HEAD`、`git status --short`、`git log --oneline -8`、branch/common dir | **PASS / exit 0** | 精确 head、clean、main/.git；落盘后仅本报告新增。 |
| 累计范围 | `git diff --stat cbfb7bbc9..HEAD`、`git diff --name-only cbfb7bbc9..HEAD`，逐路径匹配 Task allowlist | **PASS / exit 0** | 76 files/+7037/-562；76/76，无越界。附录 A。 |
| 源码漂移 | `git diff --name-only b328f3488..HEAD`；`git diff --quiet b328f3488 HEAD -- apps/desktop-avalonia` | **PASS / exit 0** | 后续仅 9 docs/evidence 路径。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **PASS / exit 0** | **0 warnings / 0 errors**，约 6.12s。 |
| 全量 test | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **PASS / exit 0** | **1132 passed / 0 failed / 57 skipped**，共1189；分程序集见下。 |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | **PASS / exit 0** | 292 rows；every generated artifact matches the frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | **PASS / exit 0** | generated theme artifacts match the frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | **PASS / exit 0 / 3 warnings** | 10 非终态 Task，STATUS 3158 bytes/29 lines、PLAN 4734 bytes/64 lines 达预算80%；既有 warnings。 |
| 冻结契约 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | **PASS / exit 0 / 15/15** | 14份契约+FEA-01，不与下行17项 Task evidence 混淆。 |
| Task pins | Canonical Evidence 表逐项 Get-FileHash SHA256，与 Task pin/索引对应行比较 | **PASS / 17/17** | 每项实际 SHA 及三方结果见附录 B。 |
| 索引 | 检查表项、自引用及 ASCII 非法控制字符 | **PASS** | 控制字符0，无自身 SHA/表项；19项索引路径可读。 |
| final log | 读取 head、实测 SHA、比对 Task/索引 | **PASS** | head=`b328f3488615fcad10e455e6f1196e6622cbb889`；SHA=`06975fc74553cf84fdf21ec4402ef3042b7bb5b1c9ca46381d44af5ea7f7b36d`。 |
| 性能数据一致性 | JSON排序重算；比对摘要/Task/索引/handoff/r4 rework log | **PASS（当前数值）** | p50 106.46/p95 313.95/max 331.89ms，+10592B，handles0；四次p95 292.92/295.41/295.59/313.95ms。 |
| 独立 Release 性能 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj -c Release --filter FullyQualifiedName~PerformanceBaselineTests --settings apps\desktop-avalonia\tests\NewManga.runsettings --logger 'console;verbosity=detailed'` | **PASS / exit 0 / 1 passed** | 4预热+20测量；p50 103.99/p95 314.65/max 510.46ms；冷684.96ms；+12608B/handles0；总8.4592s。下节保留本次样本。 |
| 原生矩阵 | 双屏/拔屏/DPI/IME/原生辅助功能 | **BLOCKED D-1 / NOT_RUN** | 本轮未做原生产品启动，未用 headless 替代。 |
| 反向/额外故障探针 | 改坏源码、真实超时/取消 cleanup、按钮→窗口全屏运行探针 | **NOT_RUN** | 只读限制下没有改生产代码/测试。R-020/R-021 为已引用代码控制流证据，未虚构实跑复现。 |

全量实际输出摘要（同一次运行，exit 0）：

| 程序集 | passed | failed | skipped |
|---|---:|---:|---:|
| Appearance | 21 | 0 | 0 |
| Presentation.Avalonia | 38 | 0 | 0 |
| Host | 51 | 0 | 28 |
| ThemeEngine | 253 | 0 | 0 |
| DesignSystem | 87 | 0 | 0 |
| ApplicationCore | 31 | 0 | 0 |
| CoreClient | 128 | 0 | 22 |
| App | 523 | 0 | 7 |
| **合计** | **1132** | **0** | **57** |

App 耗时2m6s；交付日志2m7s。相较r4的1119/0/57，增加13 passed；相较FEA-06基线1034/0/57，增加98 passed；fail/skip 均未增加。当前 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 为空。Host 28/CoreClient 22/App 7 的直接原因均为此变量未设置；Fact 属性在检查 BOOK/S4 等后续前置前已返回 Skip，不能再概括为“App 7因BOOK/S4不可用”。附录 C 逐条列同一次运行的57项与直接原因。首次定向读取个别测试文件时路径名称不匹配，已用 rg 定位到 `ChapterCreationTests.cs`/`RunControllerTests.cs`/`WritePolicyUiTests.cs` 及相应 fixture，未将定位失败当验证通过。

## 性能口径结论（R-009 / W-5）

记录 JSON 20 个样本排序后，第10个=106.46，第19个=313.95，第20个=331.89，与字段/摘要一致。Task当前AC6、测试表、索引与handoff均为这组数据；历史切片旧数字带明确历史语境，没有作为当前 baseline 使用。四次历史复测的 p95 来自 `rework-r4-verification.log`，本轮没有重新产生这四次结果，独立复测另列，不能混为第五次交付 baseline。

**门槛语义保持“热切换 p95≤1000ms”**，没有改为平均值或放宽数值。原 nearest-rank 公式对12样本取第12个，本身也是合法的小样本 p95 估计，只是恰等于max；20样本取第19个，允许一个最高样本不进入p95，改善分位数分辨率，有限样本的验收行为因此有变化。不能说原p95“不是p95”，也不能将两种口径的下降全部归因于实现提速。W-5没有冻结样本数或max门槛，因此该采样调整**不构成W-5数值/指标语义变更**，但必须保留口径说明；当前记录及独立复测的max也均<1000ms，不依赖排除超预算离群点才通过。

`performance-baseline.md:7` 写“20次往返”不精确：测试 `PerformanceBaselineTests.cs:99-108` 实际为20次交替单向切换，即10次往返；4次预热也为单向切换。JSON 的 measuredSwitches=20 是正确的。建议DSH处置时将摘要改成“20次切换（10次往返）”，不改变本轮计算/预算结论。UI freezeUpperBound仍是异步事务总时长上限估计，不是采样得到的最大真实UI冻结；AC6继续PARTIAL。

本轮独立Release输出（同一机器，exit 0）：

```json
{"warmupSwitches":4,"measuredSwitches":20,"coldFirstSwitchMs":684.96,"p50Ms":103.99,"p95Ms":314.65,"maxMs":510.46,"uiFreezeUpperBoundMs":510.46,"samplesMs":[510.46,94.26,268.77,80.51,247.12,59.49,284.79,65.17,253.07,73.21,314.65,63.02,293.32,56.92,245.62,103.99,205.09,62.65,202.11,70.09],"managedMemoryDeltaBytes":12608,"handleDelta":0,"budgetP95Ms":1000,"passed":true}
```

## Architecture 与 Verification 结论

**Architecture：原r4生产缺陷的修复方向成立，当前head仍有一项P1窗口行为接线遗漏。** 稳定窗口/缓存/事务/唯一appearance写者与依赖方向保持Task边界，未见Core/schema/冻结契约/依赖包或额外视觉设计改动。Loaded清理及staging键路由没有发现本轮可证实的新生产竞态；Fluent全屏回调抽取后未接稳定宿主，必须修复。

**Verification：所有指定机械/自动化命令通过，不能据此批准遗漏的生产接线。** R-002/R-013的原关键假通过已消除；重复通知用例仍有非阻塞判别力缺口，部分断言只覆盖tracking/canonical而非事件表/磁盘，已明确列界。AC7在列明范围MET；AC1/2/3/4/6/8继续PARTIAL；AC5原生矩阵继续BLOCKED/D-1。本报告没有签发Task完成、原生验收或发布批准。

## 结论与复审

**Decision：changes_requested（P0=0 / P1=1 / P2=2）。暂不建议进入批准后的集成收口。**

最小返修集：

1. **R-020/P1**：将Fluent全屏请求连接到稳定PresentationWindow，并补真实生产组合根按钮/F/Esc与WindowState的断言，含切换前后及退出全屏；保持唯一窗口，不重建Host，不把硬件blocked作为不修接线的理由。
2. **R-021/P2**：让重复通知测试实际执行通知处理并验证draft保留，补clean Contrast；**R-007/P2**：由DSH统一r5 reviewer/source/索引与本报告实际状态。P2如延期需明确处置，不能直接声称已完整覆盖。顺手更正性能摘要“20次往返”的措辞。
3. 固定新code/delivery head，更新handoff/final evidence/Task pins和索引，按本报告完整命令重跑build、全量test、两生成器、check/pins；新行为测试应能捕获旧接线遗漏。若修改生产代码或测试，需fresh上下文复审新head。原生AC5与其它PARTIAL残余由DSH按授权登记并处置，本报告不代裁waiver或done。

推荐下一步：**DSH继续处置当前FEA-07返修与复审，不释放下一实现Task。** 当前FEA-06-RESIDUAL-1仍为proposed且受依赖约束，不能自动开工。可直接转发：

> 在 `G:\CODEX\New Manga`、branch `main`、common dir `.git`，接续Task `doc/tasks/FEA-07.md`。Recovery：base `cbfb7bbc92d489541a24290038eae2117f8aa1ce`；本次reviewed head `ea27a7b10a486e50cd9068c67b5d3085c6508b11`，code head `b328f3488615fcad10e455e6f1196e6622cbb889`。先Reality Check并保留他人dirty与Review原文。按 `doc/reviews/FEA-07-impl-r5.md` 处置R-020全屏桥接P1、R-021重复通知测试P2、R-007元数据P2；范围限Task allowed_paths内必要App/Presentation/测试及本Task文档证据，不改Core/schema/冻结契约/生成物/共享依赖/用户数据，不进入其它worktree，不push。共享面若需扩大先由DSH冻结授权。交付固定commit、真实组合根全屏回归、handoff、精确head final日志、性能口径说明和三方一致pins/索引；重跑 `dotnet build apps\desktop-avalonia\NewManga.sln --nologo`（0/0）、本报告全量test（1132基线，无新增fail/skip，新增测试另计）、TokenGen/ThemeGen `-- --check`、`pwsh -NoProfile -File tools\governance\check.ps1`、`pwsh -NoProfile -File tools\governance\verify_pins.ps1`及Task全部evidence SHA；所有产品验证使用临时theme/data根。AC5原生矩阵保留BLOCKED/D-1，AC1/2/3/4/6/8不自动升级。DSH完成findings处置并固定新head后Appointment fresh只读复审，P1未闭环前不批准集成或置done。


## 附录 A：累计76路径逐项allowlist核对

| 变更路径 | 匹配Task规则 |
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
| `doc/handoffs/FEA-07-resume-2026-11-02.md` | `doc/handoffs/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r1.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r2.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r3.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r4.md` | `doc/reviews/FEA-07-*.md` |
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
| `verification/FEA-07/slice-1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2b-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2c-part1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2c-part2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-3-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-4-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-5-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-6-gapclosing-verification.log` | `verification/FEA-07/**` |

## 附录 B：17项Task evidence实际SHA-256

以下每项实际文件SHA与Task及索引对应行均一致。

| evidence_id | 实际SHA-256 | Task/索引 |
|---|---|---|
| EV-FEA07-SLICE1 | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` | PASS / PASS |
| EV-FEA07-SLICE2 | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` | PASS / PASS |
| EV-FEA07-SLICE2B | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` | PASS / PASS |
| EV-FEA07-SLICE2C1 | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` | PASS / PASS |
| EV-FEA07-SLICE2C2 | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` | PASS / PASS |
| EV-FEA07-SLICE3 | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` | PASS / PASS |
| EV-FEA07-SLICE4 | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` | PASS / PASS |
| EV-FEA07-SLICE5 | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` | PASS / PASS |
| EV-FEA07-PERF | `1aa295ffc5fff3b41ce699c43d55e4e3823ef954392a1c919c976f11d535380e` | PASS / PASS |
| EV-FEA07-GAPCLOSING | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` | PASS / PASS |
| EV-FEA07-GENERATORS | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` | PASS / PASS |
| EV-FEA07-FINAL | `06975fc74553cf84fdf21ec4402ef3042b7bb5b1c9ca46381d44af5ea7f7b36d` | PASS / PASS |
| EV-FEA07-PERF-MD | `ed528f6c677653651789e68a217b80c9da786ee704c56c9d19974612b9a2220f` | PASS / PASS |
| EV-FEA07-REWORK2 | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` | PASS / PASS |
| EV-FEA07-REWORK-R3-1 | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` | PASS / PASS |
| EV-FEA07-REWORK-R3-2 | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` | PASS / PASS |
| EV-FEA07-REWORK-R4 | `f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b` | PASS / PASS |

索引其余Debug JSON与rework-part1两项也逐项实测一致：共19/19项，未含索引自身。

## 附录 C：本轮实际57项skip与直接原因

本次全量输出逐名称核对后使用下表记录；历史表仅作名称排版来源。共同原因S：NEWMANGA_CORECLIENT_SIDECAR_DIR未设置，Fact首先判定sidecar不可用；未继续验证BOOK/S4或其它后续条件。Host 28 / CoreClient 22 / App 7。

| 程序集 | 用例（类.方法） | 直接原因 |
|---|---|---|
| Host | `CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain` | S |
| Host | `ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory` | S |
| Host | `ExportE2ETests.Export_Cancel_LeavesNoArtifact` | S |
| Host | `ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames` | S |
| Host | `GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant` | S |
| Host | `GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages` | S |
| Host | `GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled` | S |
| Host | `GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths` | S |
| Host | `HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection` | S |
| Host | `HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized` | S |
| Host | `HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes` | S |
| Host | `HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection` | S |
| Host | `HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall` | S |
| Host | `HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry` | S |
| Host | `HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged` | S |
| Host | `HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames` | S |
| Host | `HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe` | S |
| Host | `HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked` | S |
| Host | `HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost` | S |
| Host | `HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` | S |
| Host | `LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites` | S |
| Host | `RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration` | S |
| Host | `StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable` | S |
| Host | `StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites` | S |
| Host | `StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites` | S |
| Host | `WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook` | S |
| Host | `WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError` | S |
| Host | `WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog` | S |
| CoreClient | `CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23` | S |
| CoreClient | `CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` | S |
| CoreClient | `CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError` | S |
| CoreClient | `CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest` | S |
| CoreClient | `HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle` | S |
| CoreClient | `HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling` | S |
| CoreClient | `HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly` | S |
| CoreClient | `SidecarFailureTests.StartupTimeout_IsTyped_NotAHang` | S |
| CoreClient | `CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars` | S |
| CoreClient | `CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake` | S |
| CoreClient | `CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons` | S |
| CoreClient | `CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce` | S |
| CoreClient | `CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore` | S |
| CoreClient | `CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | S |
| CoreClient | `CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore` | S |
| CoreClient | `CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture` | S |
| CoreClient | `CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | S |
| CoreClient | `RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty` | S |
| CoreClient | `RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides` | S |
| CoreClient | `RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings` | S |
| CoreClient | `RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame` | S |
| CoreClient | `S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore` | S |
| App | `CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures` | S |
| App | `CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly` | S |
| App | `RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys` | S |
| App | `RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey` | S |
| App | `RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly` | S |
| App | `StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot` | S |
| App | `WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason` | S |
