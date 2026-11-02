---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r4；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: ad56bea1c（文档/证据 head；代码 head 100d487ff）
code_head: 100d487ffb55518e98be5219d750ab85c8a71d2b
decision: changes_requested
counts:
  P0: 0
  P1: 3
  P2: 3
---

# Review：FEA-07 第 4 轮实现复核（impl-r4）

## Reviewer 身份与来源

本报告由用户指定的 fresh Codex CLI 独立上下文执行，未参与 FEA-07 的设计、实现或返修。辅助只读审查来源为本轮 `/root/standards`（Standards）与 `/root/spec`（Spec）子任务；均未写文件、未参与实现或运行产品测试。主会话核对代码、实跑验证、执行临时复现并承担本报告结论。两视角均为 executed；重叠发现已去重。

唯一主动写入的仓库文件为本报告。临时分析位于 `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-07/impl-r4-analysis-20261102/`；未改源码、测试、Task、状态、既有证据或用户数据，未 commit/push，未进入其他 linked worktree。按要求运行的 build/test 产生常规忽略构建输出和隔离测试临时文件；未启动使用真实数据的产品，未写真实 `%APPDATA%`。

## 范围与 Reality Check

- 起始与报告落盘前 `HEAD=ad56bea1cd6142835ff18c1eecdf114e1a0fced2`，分支 `main`，Git common directory `.git`，`git status --short` 为空。
- 固定累计范围为 `cbfb7bbc92d489541a24290038eae2117f8aa1ce..ad56bea1cd6142835ff18c1eecdf114e1a0fced2`。`git diff --stat cbfb7bbc9..HEAD`：**70 files changed, 5811 insertions(+), 555 deletions(-)**；逐路径匹配 Task `allowed_paths` 为 **70/70，越界 0**，见附录 A。
- `100d487ff..HEAD` 只有 9 个文档/证据文件：STATUS、PLAN、checkpoint、impl-r3 handoff、Task、索引、final log、Release JSON、性能摘要。`git diff --quiet 100d487ff HEAD -- apps/desktop-avalonia` exit 0，无源码或测试漂移。
- **所有代码行号均以 `100d487ff` 为准**；文档行号以 `ad56bea1c` 为准。下文简写文件名指附录 A 中的唯一对应路径。
- 先读 impl-r3，再读 impl-r2/r1、Task、STATUS、PLAN、当前 rolling checkpoint、指定证据与 handoff；同时核对 AD-002 有效架构、C-03 §2.1 和协作协议 §4/§6。历史闭环不等于完整 AC 验收，不能据其推断原生或真实数据链路已完成。

实际 `git log --oneline -8`：

```text
ad56bea1c docs(fea-07): r3 返修 part2 处置 + 精确 head 证据/索引 + delivery/生命周期固定（head 100d487ff；全量 1119/0/57）
100d487ff fix(fea-07): r3 返修 part2（R-001 真实 staging Loaded/Rendered 门禁 + 状态覆盖；R-002 隐藏缓存树退出聚合 + V2 Theme Studio draft）；全量 1119/0/57
cc34f36e1 docs(fea-07): 新会话恢复材料（handoff + checkpoint）
6a31fb92e fix(fea-07): r3 返修 part1（R-015 journal finalize 补偿 + R-013 并发确定性测试 + R-009/R-016/R-007）；全量 1115/0/57
52474fcbf docs: 记录 Codex 模型 ID 与 reasoning effort 实测结论
7b62c492b docs(fea-07): checkpoint r3 复核派发记录
b3fa8dc0c docs(fea-07): impl-r2 处置记录 + 最终证据/索引 pin（代码 head 3220abd59；全量 1113/0/57）
3220abd59 fix(fea-07): impl-r2 返修 part2（并发门/previous journal/planner Selection/真实 100 次切换/live exit 状态/maximize）；全量 1113/0/57
```

## r3 findings 闭环表

| ID | r3 状态/级别 | r4 结论 | 依据与残余 |
|---|---|---|---|
| R-001 | open / P1 | **原门禁缺陷闭环；AC1 PARTIAL** | `PresentationWindow.cs:68-86` 的 staging 在 live Grid，Opacity=0/不可命中；`FrontendHostCoordinator.cs:115-124,181-268` 在挂树前订阅真实 Loaded，等待布局后读真实几何，复核 IsLoaded/root/top-level，等待 RequestAnimationFrame；无 1024×640 fallback 或手工 Measure/Arrange。真实状态测试见下文。新发现的 draft 同步、Loaded 订阅和 staging 键路由分别列 R-017/018/019，不能把“原门禁已改”解释为 AC1 全过。 |
| R-002 | open / P1 | **生产接线闭环；验证未闭环，P1 保留** | `PresentationWindow.cs:132-177` 聚合 visible/staging/cache；`App.axaml.cs:254,401` 注入全 cache 与真实 HasDraft；`AppShellV2.axaml.cs:86-92` 读取 provider。真实隐藏 Fluent dirty 测试有效，但 V2 部分同时覆写 provider、保留 Fluent blocker，见 Findings。 |
| R-003 | r2 finding 已闭环 | **维持闭环；AC3 PARTIAL** | journal 保存 PreviousFrontendId；`App.axaml.cs:74-77` 在 planner 前恢复。真进程 kill、暂停期间源/Lock 变化仍无证据；不改记 MET。 |
| R-004 | r2 finding 已闭环 | **维持闭环；AC4 PARTIAL** | `App.axaml.cs:77-92` 直接使用 planner.Selection；`SafeStartupPlanner.cs:64-90` 对 fallback warning 强制 V2。真实 App 初始化入口、坏包/scale 矩阵缺口仍在。 |
| R-005 | 代码接线闭环 | **维持；原生矩阵 BLOCKED** | `App.axaml.cs:256-259,283-322` 枚举屏幕/clamp/DisplayId；`PresentationWindow.cs:59-65` 恢复最大化。headless 不能替代原生多屏/DPI。 |
| R-006 | closed | **维持闭环** | StartupCompatibilityMatrix 与新 Presentation 测试使用临时 theme/data/journal 根；本次未执行真实用户目录产品启动。 |
| R-007 | open / P1 | **主体修复；剩余降为 P2** | delivery/head/handoff、r3 历史报告指针和 1119/0/57 已一致；STATUS/PLAN/checkpoint 已记 r4 进行中。Task reviewer 与索引仍写 r4 待派，与当前事实不符。已有明确交付与 appointment 来源，故不再维持原先交付无法追溯的 P1，保留 P2 元数据修正。 |
| R-008 | closed | **维持闭环** | 70 个累计变更路径全部匹配 allowed_paths，见附录 A。 |
| R-009 | open / P2 | **数值错配闭环；AC6 PARTIAL** | AC6 当前行和测试要求表为新 Release 496.30ms；摘要/JSON/索引/handoff 一致。旧数字仍存在于明确的历史切片/处置记录，并有新旧口径说明，不再作为当前 AC6 数值。详见性能核对。 |
| R-010 | closed | **原 VM 重建问题维持闭环；新增订阅回归另列 R-018** | `App.axaml.cs:218-238` 仍每前端仅一个树。新 Loaded handler 是对同一缓存树每次附加，不能用“树实例复用”推断没有事件增长。 |
| R-011 | closed | **维持闭环** | 索引无自身 SHA；15 个 Task pin 的文件实测 hash 与 Task、索引三方逐项相同。 |
| R-012 | closed | **维持闭环** | 两生成器本轮实跑 exit 0、byte-for-byte up-to-date；历史 generators log pin 也相符。 |
| R-013 | open / P1 | **代码范围正确；失败并发验证仍未闭环，P1 保留** | `FrontendHostCoordinator.cs:85-108,165-172` 同门覆盖 no-op/快照/事务；新增测试确有首事务 finalize 失败，但第二请求回原 V2，终态断言不能区分“正确排队”与“过早 no-op”。未证明旧缺陷的失败交错被捕获，见 Findings。没有据此声称已发现新的生产死锁。 |
| R-014 | closed | **维持闭环** | `PresentationWindow.cs:59-65` 与 `PresentationWindowTests.cs:305-321` 最大化恢复与捕获一致。 |
| R-015 | open / P1 | **普通 finalize 失败补偿闭环** | `FrontendHostCoordinator.cs:150-162` 同时恢复内容、appearance、current id；`FrontendSwitchCoordinator.cs:119-145` journal rollback 失败也会继续 app 补偿。测试 `FrontendHostCoordinatorTests.cs:175-196` 注入 finalize 前异常并核对旧内容/id/settings/journal。实际持续 I/O 故障未被此 hook 等价覆盖，不将其夸大为所有存储故障均可恢复。 |
| R-016 | open / P2 | **闭环** | 索引非法控制字符计数 0，说明为正常 final-evidence.log 路径，无自身 SHA。 |

## 本轮重点实现判断

### R-001：真实呈现门禁与回滚

`PresentationWindow.cs:75-86` 创建并挂载 staging，未用 IsVisible=false 绕过布局。`FrontendHostCoordinator.cs:184-212` 先挂入 staging，再以 Loaded priority 排队让布局先行，读取 visible host、staging host、tree 三层非零几何；该排队只服务布局顺序，**未再被当作 Loaded/Rendered 的完成证明**。

Loaded 订阅在挂树前（`:118-120`），门禁在 `:222-239` 等待真实事件或确认已经 IsLoaded，并校验 root/top-level。Rendered 在 `:250-268` 请求 TopLevel animation frame，等待有 2s timeout；Loaded 上限 5s（`:25-29`）。窗口最小化/不可见导致没有 frame 时，代码会超时并走 rollback；本轮没有原生最小化帧行为实测，记 NOT_RUN。常量固定本身不构成缺陷，建议后续测试可注入时间界限。RequestAnimationFrame 证明收到框架帧回调，不能外推为原生 compositor/显示器已经呈现像素。

门禁在 commit 前失败时 previousSettings 尚未赋值，不会持久化 target；`RollbackAsync :150-162` 清理 staging、恢复 previous 内容与 current id，事务层记 RolledBack。commit 后 finalize 失败同样走 appearance 补偿。`PresentationWindowTests.cs:325-361` 的零几何/加载后自摘除分别证明失败与 staging 清理；`:108-122` 证明成功切换 staging 清空。渲染超时的真实无帧故障测试仍未新增，不把通用阶段故障注入说成原生渲染超时实测。

`PresentationHostCompositionTests.cs:174-219` 的 50 次往返即 100 次切换，确实保留 Fluent Workbench 页和未应用 Settings draft，并保留 V2 `Session.Shell.CurrentSpace`、`Console.RunIdInput`、`Reader.BookId`；这是实际 VM 字段，不再用 Tag 冒充业务状态。RunIdInput 是输入值，不是真实 Run/Intent 执行。原生 IME、A03 真库 DB/current/pinned/Lock、源文件/candidate 零变化、ACK 重连和真实 Run/Intent 链路仍无验收证据，AC1 保持 PARTIAL 正确。staging 的全局键盘处理另见 R-019。

### R-002：缓存树退出保护

生产 allContentProvider 确实返回 `contentCache.Values.ToArray()`，关闭遍历含可见树、staging 和全部缓存树，未再只读 Current。生产 `WireThemeStudio` 将 provider 闭包指向真实 ThemeStudioViewModel.HasDraft，V2 HasUnsavedEdits 直接读该 provider。

组合测试 `:249-270` 使用真实 FluentShellSurface，修改真实 SettingsViewModel，再切到 V2 并尝试关闭，证明隐藏 Fluent 的 dirty 状态被聚合。V2 段 `:272-278` 则覆写生产 provider，且 Fluent 一直 dirty 到 `:282`；因此那段只证明“此时仍有任一 blocker”，不能证明 V2 真实草稿接线。R-002 关键回归证据未闭环。

### 附带 Settings draft 改动与 C-03

所有持久化仍经 `AppearanceCoordinator.SaveAsync`，未增加第二个文件写者，**C-03 §2.1 的单写者结构未被迁移/绕开**。但 `FluentPageViewModels.cs:1392-1394` 比较 Draft 和新 settings，没有比较前后 canonical settings，因此无法识别“仅 FrontendId 变化”。任何真实 Mode/Contrast/Layout 等变更均可能保留旧值，凭空变 dirty，并可在下一次 SaveAppearanceAsync（`:1170`）覆盖新设置。它直接违背 Task `:204` 的“其它外观变更仍镜像唯一写者”。FEA-06/Fluent 既有测试全过说明该场景未被那些断言捕获，不能据此认定行为兼容。详情与实际复现见 R-017。

### 性能 baseline：AC6 / W-5 / R-009

当前 Release JSON 与摘要、索引、handoff、Task AC6/测试表一致：**p50 102.29 / p95 496.30 / max 496.30 ms，内存 +7088B，句柄 0，冷首次 593.99ms**。12 个热样本计算 ceil(0.95×12)-1=11，所以 p95 等于 max；三次复测摘要为 496.30/575.64/712.28ms，均低于 W-5 的 1000ms，**记录的 W-5 门槛 PASS**。本轮未另跑 Release 三次采样，核验的是已固定原始 JSON/摘要，Debug 全量套件中的预算断言也通过；不得把它称为三次独立 Release 重现。

Task `:150,186,194,206` 仍能检索到 344.93/429.47：前者是 slice-5/impl-r2 历史值及纠错记录，`:150` 明确指向当前新 baseline，AC6 `:218` 和测试表 `:251` 已使用 496.30。`performance-baseline.md:17` 说明新事务多了 staging/Loaded/frame 成本，不能直接与 r2 的 344.93ms 比较。Task `:153` 的切片 5 历史“AC6 MET”没有取代当前 AC6 PARTIAL；建议后续收敛文档时保留历史身份，避免作为当前验收引用。真实规模 workload、独立渲染冻结采样和真机指标仍欠缺，AC6 **PARTIAL** 准确，不能仅凭 p95 PASS 提升为 MET。

### 生命周期指针：R-007

Task `reviewer` 当前正确指向已发生的 impl-r3，delivery_head 精确为 `100d487ff`；新 handoff 标题与 §4 是 r3 处置完成→r4 派发，STATUS/PLAN/checkpoint 均记 r4 进行中，LEDGER 仍为 in_progress。canonical_evidence_status=pending 在本轮未批准、未集成时正确。余下矛盾是 Task `:10,210`、索引 `:9` 仍说 r4 待派；本次执行已是 r4。DSH 需在处置报告后更新 appointment/latest review 与状态文案；报告作者不代写这些文件。无需把 pending 偷换为 complete，亦不得据 handoff 的“通过后”计划提前设置 done。

## AC 逐条 Verdict

| AC | r4 Verdict | 依据与适用边界 |
|---|---|---|
| AC1 | **PARTIAL** | 真实门禁与 100 次真实树字段保留已补；R-017 外部外观同步回归、R-018/019 新问题仍在。原生 IME、A03 真库保护、ACK/真实 Run/Intent 和完整焦点恢复无证据。 |
| AC2 | **PARTIAL** | 可见/staging/cache 聚合与 V2 provider 代码成立；真实隐藏 Fluent 退出测试有效；V2 draft 独立阻断验证 R-002 未闭环。真实二窗归属/同 Session Region 单写 owner 集成未补。 |
| AC3 | **PARTIAL** | previous journal、启动前恢复与 finalize 补偿均实现；R-013 失败并发排队证明不足，真实跨进程 kill、暂停期间配置/源/Lock 变化待补。 |
| AC4 | **PARTIAL** | planner.Selection 接入、warning fail-safe 与坏 JSON 路径存在；真实 App 初始化入口及坏包/scale 矩阵缺口未变。 |
| AC5 | **BLOCKED（原生矩阵，D-1 无硬件）** | memento/clamp/PerMonitorV2/最大化机械部分 PASS（部分完成）；原生双屏、拔屏、换主屏、全屏及 DPI 100/125/150/200% 未执行。不得用 headless 几何代替原生验收。 |
| AC6 | **PARTIAL** | 当前记录 W-5 p95≤1000ms PASS，性能字段已统一；freeze 仍为事务时长上限估计，缺真实规模 workload 与真机指标。 |
| AC7 | **MET（headless 回归/启动构造/机械依赖范围）** | 实跑全量 1119/0/57、build 0/0，两生成物无漂移；ProjectReference/TFM 与启动兼容测试通过。该 MET 不等于 AC4 的真实 App 初始化入口或 sidecar 跳过链路已验收。 |
| AC8 | **PARTIAL** | 隔离测试、15/15 Task pins、无索引自引用/控制字符、生成物与治理检查有效；R-007 文案残余及原生截图/矩阵缺口仍在。 |

## Findings

表中只列本轮仍需处置的问题；闭环项见前表，不重复计数。P0=0 / P1=3 / P2=3。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 可执行建议 | 状态 |
|---|---|---|---|---|---|---|
| R-017 | **P1** | `FluentPageViewModels.cs:1383-1395`；保存 `:1170` | clean 或 dirty draft 收到真实非 FrontendId 外观变更时仍保留旧字段，导致假 dirty；后续保存可覆盖用户刚应用的新设置。尤其隐藏 Fluent 树可因此新增退出 blocker。违反 Task `:204` 的 frontend-only 特例边界。 | 临时探针用真实 AppearanceCoordinator/Store 和 SettingsViewModel，先 clean System，经 coordinator 保存 Dark 并处理 UI dispatcher；结果磁盘/协调器 Dark、Draft System、IsDirty=True，见下方输出。 | 记录上一次已观察 canonical snapshot，用 old/new canonical 判断是否只有 FrontendId 变化；仅此种变化合并 draft，其余变更镜像 coordinator。Changed 若异步排队，应保留准确 snapshot/顺序。补 clean/dirty × frontend-only/Mode/Contrast/Layout、commit/rollback 回归。 | open，新发现 |
| R-002 | **P1** | `PresentationHostCompositionTests.cs:272-285`；生产 `App.axaml.cs:401` | V2 退出测试把 provider 改为假委托，同时隐藏 Fluent 仍 dirty，关闭自然被 Fluent 阻断；即使 V2 HasUnsavedEdits 永远 false 也可通过关键断言。无法证明本轮声明的真实 Theme Studio unapplied draft 接线与退出保护。 | `:275` 覆写 `()=>true`；`:278` 仅查 cancelled；Fluent 到 `:282` 才清理。Assert.NotNull 只证明有委托，未证明它读真实草稿。 | 不覆盖 provider。先清除 Fluent blocker并断言所有树 clean，再通过已注册真实 ThemeStudio VM 产生 unapplied draft，断言原 provider/HasUnsavedEdits true 与 Close 取消；清理真实 draft 后才允许关闭。用移除 V2 provider/HasUnsavedEdits 的反向验证确认测试能失败。 | open，代码已补，验证未闭环 |
| R-013 | **P1** | `FrontendHostCoordinatorTests.cs:199-227`；生产门 `FrontendHostCoordinator.cs:85-108` | 首请求失败后第二请求回原 V2，最终本就应是 V2。测试没有证明第二请求曾等待门，不能区分正确串行与旧实现“第二请求提前成功 no-op，首请求随后失败回滚”。这是 r3 要求的关键失败交错证据缺口，不是新发现生产锁错误。 | 两个请求 `:217-219` 启动后只查最终原 V2/旧内容/RolledBack；若第二请求立即返回原 V2 no-op，这些断言仍全成立。无 barrier/TCS、第二未完成或事务执行次数断言。 | 加显式可控同步点：第一请求持门且暂停，发第二请求后断言其尚未完成；再释放首事务并令 finalize 失败，确认第二在补偿完成后才判定/执行，核对两响应、内容、current id、磁盘 settings、journal。对后续非 no-op 事务再补失败快照场景；回退门范围应使测试失败。 | open，原生产修复成立，判别力不足 |
| R-007 | **P2** | `doc/tasks/FEA-07.md:10,210`；`evidence-index.md:9` | STATUS/PLAN/checkpoint 与新 handoff 已记 r4 进行中，Task reviewer 备注及索引仍写 r4 待派，恢复时出现当前 appointment 文案冲突。交付 head、r3 报告与计数均已固定，原 P1 主体问题消除。 | 本次实际执行 r4；索引仍为“r4 待派”。 | DSH 处置本报告时统一 r4 appointment/latest report 与 reviewer/source 文案；按处置结果保持 pending/in_progress，批准并集成后才置 canonical complete。 | open，降级残余 |
| R-018 | **P2** | `FrontendHostCoordinator.cs:115-120,170-173`；缓存 `App.axaml.cs:218-238` | 每次切换向同一缓存树追加匿名 Loaded handler，捕获本次 TCS；无解绑，历史委托/信号对象线性保留，每次重新挂树调用所有旧 handler。长期热切换产生无界订阅增长。 | `replacement.Loaded +=` 每次执行，无对应 `-=`；outer finally 只释放 gate。真实 100 次缓存往返不会验证订阅数量。 | 用可解绑的具名/局部 handler，并在事件完成或事务 finally 中解除；涵盖成功、超时、取消、回滚。补重复切换后存活 handler/对象数量稳定性验证。 | open，新发现；区别于已闭环的旧 VM 重建问题 |
| R-019 | **P2** | `PresentationWindow.cs:75-85`；`AppShellV2.axaml.cs:148-155,197-201`；`ViewModels/V2/Shell/AppShellViewModel.cs:944-960` | Fluent→V2 挂入透明 staging 时，V2 已向同一 TopLevel 注册 tunnel KeyDown。Opacity/不可命中/父 Focusable=false 不能禁用该全局 handler；提交前即可吞掉可见旧树快捷键、修改隐藏 V2 状态。 | headless 临时探针把真实 V2 放入同参数透明槽，向可见 Button 路由 Ctrl+K：V2 IsPaletteOpen 从 false→true，事件 Handled=true，见下方输出。未声称原生 IME 已测。 | 将快捷键/焦点激活与 active frontend/commit 绑定；staging 只参与布局和帧门禁。回滚后保持旧输入路由，测试挂起 staging 时可见旧树收键、隐藏 V2 不执行，以及 commit/rollback 后仅一套快捷键激活。 | open，新发现 |

### 有判别力的临时复现

位置：`G:/CODEX/New Manga.workspace/agent-output/codex/FEA-07/impl-r4-analysis-20261102/`（`Program.cs`、`ReviewProbe.csproj`、`probe.log`）。只引用本轮 build 的现有 DLL，未改项目源文件；settings 落自身 `probe-data`。键路由探针用 Avalonia.Headless、真实 AppShellV2/NullHost，未运行原生 App 初始化或 sidecar。

```text
command: dotnet run --project "G:\CODEX\New Manga.workspace\agent-output\codex\FEA-07\impl-r4-analysis-20261102\ReviewProbe.csproj" --nologo
shell: PowerShell 7.6.8; SDK 10.0.401; target net9.0
exit: 0
BEFORE persisted=System draft=System dirty=False
AFTER persisted=Dark disk=Dark draft=System dirty=True
STAGING_BEFORE palette=False opacity=0
STAGING_AFTER palette=True handled=True
```

临时辅助 skip 属性读取曾因 Host.Tests 不在 App test 输出目录而 exit 1，修正绝对 DLL 路径后可读取；没有重跑/替代全量测试。该辅助程序与 VSTest 的 fixture 默认根解析不同，不能用它对 models 测试的额外 skip 预测替代全量实际计数。本报告只把 full test 的 57 个实际 skip 记入结果。

## 证据与治理核对

统一环境：Windows / PowerShell **7.6.8** / dotnet SDK **10.0.401**；被测 net9.0 代码树等同 `100d487ff`，checkout 为 `ad56bea1c`。除显式说明外，下表命令均为本轮实际执行，exit **0**；本报告内记录命令、退出码和判别输出，不另写既有 verification 文件。

| 核对项 | 实际命令/步骤 | 结果 | 证据与限制 |
|---|---|---|---|
| Git/工作区 | `git rev-parse HEAD`；`git status --short`；`git branch --show-current`；`git rev-parse --git-common-dir`；`git log --oneline -8` | **PASS** | 起始/落盘前 ad56bea1c、clean、main、.git；日志见 Reality Check。落盘后仅本报告 untracked。 |
| 累计范围 | `git diff --stat cbfb7bbc9..HEAD`；`git diff --name-only cbfb7bbc9..HEAD`；逐路径匹配 Task allowed_paths | **PASS** | 70 files / +5811 / -555，70/70，越界 0；附录 A 列每条路径及规则。 |
| 文档后无源码漂移 | `git diff --name-only 100d487ff..HEAD`；`git diff --quiet 100d487ff HEAD -- apps/desktop-avalonia` | **PASS** | 9 个 docs/evidence 文件；源码树 diff exit 0。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **PASS** | exit 0；**0 warnings / 0 errors**。 |
| 全量 test | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **PASS** | exit 0；**1119 passed / 0 failed / 57 skipped**，总计 1176；分程序集见下表。与 final evidence 无计数差异，比 r3 的 1113 增 6，比 FEA-06 基线 1034 增 85；fail/skip 不变。 |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | **PASS** | exit 0；292 rows；every generated artifact matches the frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | **PASS** | exit 0；generated theme artifacts match the frozen token source byte-for-byte。 |
| 当前治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | **PASS（3 warnings）** | exit 0；10 个非终态 Task；STATUS 3167 bytes/29 lines 与 PLAN 4730 bytes/64 lines 达预算 80%。无新增 FAIL；机械 PASS 不裁决 Findings。 |
| 冻结契约 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | **PASS 15/15** | exit 0；14 份契约 + FEA-01。区别于下行 FEA-07 自身证据 pins。 |
| Task canonical evidence | 对 Canonical Evidence 表逐项 `Get-FileHash -Algorithm SHA256`，比对 Task 与索引对应 SHA | **PASS 15/15** | 每项实测 SHA、Task pin、索引一致，附录 B 列实测完整值。 |
| 索引完整性 | 检测除 CR/LF/TAB 外 ASCII 控制字符；检查自身 hash/表项 | **PASS** | 非法控制字符 0；未列自身 SHA。18 个索引文件的 SHA 另逐路径实测一致。 |
| 精确 final evidence | 读取 final-evidence.log head/shell/exit，并实测 SHA | **PASS** | head `100d487ffb55518e98be5219d750ab85c8a71d2b`；SHA `478b097fb4087aaf48683fc43030a7350481e3b9cda8a67521b9d701a3e373f7` 与 Task/索引相同。 |
| 性能 | 比对 Release JSON/摘要/Task/索引/handoff、预算与样本计算 | **PASS（记录的 W-5）/ AC6 PARTIAL** | 102.29/496.30/496.30ms、+7088B、handles 0；三次摘要均≤1000ms。本轮没有独立三次 Release 重采样。 |
| R-017/019 复现 | 临时 ReviewProbe.csproj，真实 VM/coordinator 与真实 V2 路由 | **复现成功** | exit 0；判别输出见上；未改被审源码。 |
| 原生显示/IME/最小化 frame | 原生双屏、拔屏、DPI 100/125/150/200%、IME、不可见/最小化帧门禁 | **BLOCKED / NOT_RUN** | AC5 按 D-1 无硬件 BLOCKED；其余未运行。不以 headless 探针替代。 |

### 全量程序集与 skip 原因

| 程序集 | passed | failed | skipped |
|---|---:|---:|---:|
| Appearance | 21 | 0 | 0 |
| Presentation.Avalonia | 38 | 0 | 0 |
| Host | 51 | 0 | 28 |
| ThemeEngine | 253 | 0 | 0 |
| DesignSystem | 87 | 0 | 0 |
| ApplicationCore | 31 | 0 | 0 |
| CoreClient | 128 | 0 | 22 |
| App | 510 | 0 | 7 |
| **合计** | **1119** | **0** | **57** |

Host 28 与 CoreClient 22 的直接原因是 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置，Fact 属性在发现时自跳过。**本轮 App 7 的直接原因也同样是 sidecar env unset**：CreateChapter 2、RunController 3、StartupSelfCheck 1、WritePolicy 1；其实际属性均先查 sidecar。`final-evidence.log:23` 写“App 7 (BOOK/S4 fixture unavailable)”是已有概括，不能当成本轮逐条实际原因；RunBookFixture 也是先查 sidecar，再查 BOOK，本轮没有证明 BOOK/S4 fixture 的实际可用性。计数 28+22+7=57 一致，未将 skip 当作通过。附录 C 逐项列出本轮实际跳过用例及共同直接原因。

## Architecture 与 Verification 结论

**Architecture：当前精确 head 不满足集成批准条件。** 稳定窗口/双槽/内容缓存、App→Presentation 依赖、planner 单源、appearance 唯一写者及 journal 补偿方向符合 Task 架构；未发现新增 Core/schema/冻结契约/依赖包或视觉重做越界。R-017 的 canonical→draft 同步错误会造成可见状态与后续持久化回退；staging 的全局键盘激活及 Loaded 订阅也需处置。没有把有界缓存保留本身当作泄漏。

**Verification：指定 build/test、两生成器、治理和两类 pins 均通过；关键回归证据仍有缺口。** R-002 的 V2 测试存在双重假通过，R-013 失败交错测试没有证明排队语义。AC7 在机械/headless 范围 MET；AC1/2/3/4/6/8 PARTIAL；AC5 原生矩阵 BLOCKED。新测试总数增加与预算通过不能替代有判别力的状态/时序断言，原生帧/硬件与真库链路也不能外推。

## 结论与复审

**Decision：changes_requested（P0=0 / P1=3 / P2=3）。当前不建议进入 DSH 集成验证。**

最小返修集：

1. 修复 R-017，仅以新旧 canonical 的 frontend-only 变化决定保留 draft；补真实外观变更镜像和切换回滚回归。
2. 补 R-002 的真实 Theme Studio draft 单独阻断退出测试，清除其它 blocker，保持生产 provider；补 R-013 的显式排队同步和失败时序判别，不用原 V2 的终态 no-op 代替排队证明。
3. 解绑每轮 Loaded 订阅（R-018），隔离 staging 的全局键盘激活（R-019）；更新 R-007 的 r4 实际 appointment/latest report 文案。P2 由 DSH 明确修复或登记处置，不默认为关闭。
4. 固定新 delivery/code head 后重跑本报告列出的 build、全量 test、两 `--check`、check/pins，刷新 canonical evidence/索引/handoff，再派 fresh 独立上下文复核。AC6 继续 PARTIAL，AC5 原生矩阵继续 BLOCKED；任何 residual/waiver 或 Task done 均由 DSH 按授权裁决，不能由本 Review 代批。

推荐下一步：**DSH 处置并返修当前 FEA-07**。当前 Task 尚未完成，不自动释放 `FEA-06-RESIDUAL-1`。可直接转发：

> 在 `G:\CODEX\New Manga`、branch `main`、common dir `.git`，按 `doc/tasks/FEA-07.md` 冻结写域处置 `doc/reviews/FEA-07-impl-r4.md`。Recovery：base `cbfb7bbc92d489541a24290038eae2117f8aa1ce`，reviewed head `ad56bea1cd6142835ff18c1eecdf114e1a0fced2`，代码 head `100d487ffb55518e98be5219d750ab85c8a71d2b`。先核对共享仓库最新 Git/dirty；保留他人内容和本报告。修复 R-017，补 R-002/R-013 判别测试，处置 R-007/R-018/R-019；仅修改 Task allowed_paths 内必要 App/Presentation/测试与本 Task 交付文档，不改冻结契约、Core/schema/生成物、共享依赖或用户数据；新增共享面先由 DSH 冻结授权。交付固定 commit、测试与 `doc/handoffs/FEA-07-*.md`、`verification/FEA-07/` 精确 head 日志和索引/pins。按本报告完整命令重跑 build 0/0、全量无新增 fail/skip、两生成物 byte-for-byte、governance PASS、冻结 pins 15/15，并逐项核证 Task pins。记录实际 skip 原因；AC5 仍 D-1 BLOCKED、AC6 仍 PARTIAL。完成后重新 Appointment fresh 独立 Review，P0/P1 未闭环前不进入集成、不置 done、不 push。

## 附录 A：累计变更逐路径 allowlist 核对

下表由固定 `cbfb7bbc9..ad56bea1c` 的 name-only 与被审 Task front matter 逐项匹配，未将本轮新增报告计入被审范围。

| 变更路径 | 匹配 allowed_paths |
|---|---|
| `apps/desktop-avalonia/NewManga.sln` | `apps/desktop-avalonia/NewManga.sln` |
| `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs` | `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs` |
| `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` | `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` |
| `apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj` | `apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj` |
| `apps/desktop-avalonia/src/NewManga.App/Services/FrontendHostCoordinator.cs` | `apps/desktop-avalonia/src/NewManga.App/Services/**` |
| `apps/desktop-avalonia/src/NewManga.App/Services/IPresentationExitState.cs` | `apps/desktop-avalonia/src/NewManga.App/Services/**` |
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
| `apps/desktop-avalonia/tests/NewManga.App.Tests/PresentationWindowTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/SafeStartupPlannerTests.cs` | `apps/desktop-avalonia/tests/NewManga.App.Tests/**` |
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
| `doc/handoffs/FEA-07-resume-2026-11-02.md` | `doc/handoffs/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r1.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r2.md` | `doc/reviews/FEA-07-*.md` |
| `doc/reviews/FEA-07-impl-r3.md` | `doc/reviews/FEA-07-*.md` |
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
| `verification/FEA-07/slice-1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2b-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2c-part1-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-2c-part2-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-3-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-4-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-5-verification.log` | `verification/FEA-07/**` |
| `verification/FEA-07/slice-6-gapclosing-verification.log` | `verification/FEA-07/**` |

## 附录 B：15 个 Canonical Evidence 实测 SHA-256

以下每个完整 SHA 均与 Task 表及索引相同。合同 verify_pins 的 15/15 是另一组独立核对，不与本表混计。

| evidence_id | path | 实测 SHA-256 / 三方比对 |
|---|---|---|
| EV-FEA07-SLICE1 | `verification/FEA-07/slice-1-verification.log` | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` / PASS |
| EV-FEA07-SLICE2 | `verification/FEA-07/slice-2-verification.log` | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` / PASS |
| EV-FEA07-SLICE2B | `verification/FEA-07/slice-2b-verification.log` | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` / PASS |
| EV-FEA07-SLICE2C1 | `verification/FEA-07/slice-2c-part1-verification.log` | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` / PASS |
| EV-FEA07-SLICE2C2 | `verification/FEA-07/slice-2c-part2-verification.log` | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` / PASS |
| EV-FEA07-SLICE3 | `verification/FEA-07/slice-3-verification.log` | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` / PASS |
| EV-FEA07-SLICE4 | `verification/FEA-07/slice-4-verification.log` | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` / PASS |
| EV-FEA07-SLICE5 | `verification/FEA-07/slice-5-verification.log` | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` / PASS |
| EV-FEA07-PERF | `verification/FEA-07/performance-baseline-release.json` | `03c12a4dc09868236fd4525b8fc8d8483b7b03673bc03c252c4e1c5ea70a1423` / PASS |
| EV-FEA07-GAPCLOSING | `verification/FEA-07/slice-6-gapclosing-verification.log` | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` / PASS |
| EV-FEA07-GENERATORS | `verification/FEA-07/generators-check.log` | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` / PASS |
| EV-FEA07-FINAL | `verification/FEA-07/final-evidence.log` | `478b097fb4087aaf48683fc43030a7350481e3b9cda8a67521b9d701a3e373f7` / PASS |
| EV-FEA07-REWORK2 | `verification/FEA-07/rework-part2-verification.log` | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` / PASS |
| EV-FEA07-REWORK-R3-1 | `verification/FEA-07/rework-r3-part1-verification.log` | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` / PASS |
| EV-FEA07-REWORK-R3-2 | `verification/FEA-07/rework-r3-part2-verification.log` | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` / PASS |

## 附录 C：57 个实际 skip 的逐项原因

共同原因代号 **S**：`reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy)`。以下名称来自全量实际 skip 输出，原因按相应用例 Fact 属性与当前环境核对。未把辅助探针预测的 models-package skip 加入实跑结果。

| 程序集 | 用例（类.方法） | 本轮直接原因 |
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
