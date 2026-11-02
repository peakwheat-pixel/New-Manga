---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r9；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: 563f248c7（文档/证据 head；代码 head aedc7251c）
code_head: aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0
decision: changes_requested
counts:
  P0: 0
  P1: 0
  P2: 3
---

# Review：FEA-07 第 9 轮实现复核（impl-r9）

## Reviewer 身份与来源

本报告由用户明确委派的 fresh Codex CLI 独立上下文执行，未参与 FEA-07 的设计、实现或返修。来源为本轮只读委派、`doc/handoffs/FEA-07-impl-r8.md` §4、当前 rolling checkpoint §67。主会话执行 Git、调用链、指定命令及证据核对；`code-review` 技能的辅助只读审查来源为 `/root/standards`（Standards/Architecture）与 `/root/spec`（Spec/Verification），均未写文件、运行测试或参与实现。Architecture、Verification、Standards、Spec 四个视角均为 **executed**。没有用虚构的 CLI session ID 代替来源记录。

唯一主动交付写入为本报告；未修改代码、测试、Task、STATUS、既有证据、历史 Review 或用户数据，未 commit/push，未进入其他 worktree。按指定命令产生了通常的忽略构建输出、测试隔离临时夹具，以及性能测试固有的 `%TEMP%/nm-fea07-performance-baseline.json`；没有将其复制回 canonical JSON。未启动连接真实数据的产品，未写真实 `%APPDATA%/NewManga`。未修改源码进行 mutation，也未新建探针或额外日志文件。

## 范围与 Reality Check

- 起始及落盘前：`HEAD=563f248c771a79c6f913486258fb34f7ac200cff`，branch=`main`，common directory=`.git`，工作目录=`G:\CODEX\New Manga`；`git status --short` 为空。固定点及工作区与委派一致，**RESUME_SAFE**。
- 已实跑 `git rev-parse HEAD`、`git status --short`、`git log --oneline -6`、`git diff --stat cbfb7bbc9..HEAD`、`git diff --name-only cbfb7bbc9..HEAD`。累计 **89 files changed / 9186 insertions(+) / 562 deletions(-)**；逐条按 Task `allowed_paths` 匹配，**89/89 合法，越界 0**。three-dot diff stat 相同；固定 base 可解析。
- `aedc7251c..563f248c7` 仅 9 个 docs/evidence 文件：PLAN、STATUS、rolling checkpoint、impl-r8 handoff、impl-r8 Review、Task、index、final log、性能摘要。`git diff --quiet aedc7251c 563f248c7 -- apps/desktop-avalonia` **exit 0**；两端源码树均为 `f2b4459e77394721650d752cb91fed3f7a6518b2`。
- 本轮代码增量 `git diff 462141f57 aedc7251c -- apps` 仅三文件：`FrontendHostCoordinator.cs`（+7/-1）、`PresentationWindow.cs`（+8/-4）、`PresentationWindowTests.cs`（+31/-13）。未新增依赖或修改 Core/schema/冻结契约/生成物。
- 先读指定 r8/r7 Review、Task、STATUS、PLAN、final/index/rework-r8/handoff；再按引用读当前 checkpoint 尾部、性能摘要/JSON、AD-002 当前有效边界及 AD-003 修订提示、协作协议 §4/§5.1/§6、Task/Review 模板。未扫描无关历史 Task 或 verification 目录。

实际 `git log --oneline -6`（exit 0）：

```text
563f248c7 docs(fea-07): impl-r8 处置 + mutation 判别证据/索引 + delivery 固定（head aedc7251c；全量 1138/0/57）
aedc7251c fix(fea-07): r8 返修（R-023 屏障前移至 Promote 前 + mutation 判别证据 / R-007 文案）；全量 1138/0/57
b6b63574d docs(fea-07): impl-r7 处置 + 返修证据/索引 + delivery/生命周期固定（head 462141f57；全量 1138/0/57）
462141f57 fix(fea-07): r7 返修（R-022 取消路径窗口模式补偿 / R-024 门内快照防陈旧恢复 / R-023 判别性测试）；全量 1138/0/57
226e47c51 docs(fea-07): impl-r6 approved + R-022 修复处置/证据/索引（head 5a495f80a；全量 1135/0/57）
5a495f80a fix(fea-07): r6 R-022 失败切换恢复原窗口全屏模式（含回归测试）；全量 1135/0/57
```

**源码行号均以 `aedc7251c` 为准**。下文 App 源码简称相对于 `apps/desktop-avalonia/src/NewManga.App/`，同名 App 测试相对于 `apps/desktop-avalonia/tests/NewManga.App.Tests/`。文档 findings 明确引用被审文档 head **`563f248c7`** 的行号：这些处置与 pin 更新尚不存在于代码提交中的旧版文档，不能把两版本行号混用。

## r8 findings 闭环表

| ID | r8 状态 | r9 Verdict | 依据与边界 |
|---|---|---|---|
| R-023 残余 | 排队用例无判别力，P2 open | **核心判别力闭环** | 屏障位于 Promote 前，旧 Fluent 树/reader/Window 仍全屏；B 发起后明确未完成；释放后 A 成功、B 失败、目标树/frontend、旧 VM 清全屏、Normal、journal 清除均有断言。定向与全量均 PASS；旧门外快照会使最终 Normal 断言失败。单用例的 settings/RolledBack 直接断言边界见下文。 |
| R-007 | appointment 文案，P2 open | **仍 open/P2** | delivery、最新已完成 r8 Review、handoff 与 canonical=pending 正确；Task/索引依旧写“r9 待派”，与 STATUS/PLAN/checkpoint 的 r9 已派执行冲突。 |
| R-022 残余、R-024 | r8 已确认实现闭环 | **维持闭环** | 快照在 gate 内且在 reject/no-op 后；失败/取消在放门前 Dispose，成功 finalize 后 Commit。真实全屏提升后故障、取消、排队拒绝三个定向用例 3/3 PASS。 |

更早 findings 按本轮事实复核如下；不覆盖或改写历史 Review：

| ID | 当前状态 | 核对依据 |
|---|---|---|
| R-001、R-010 | 维持已记录闭环及 AC 边界 | 组合根按 frontend 缓存；真实 staging 布局/Loaded/帧门禁、真实树 100 次切换与状态保留回归通过。 |
| R-002 | 维持闭环 | `PresentationWindow` 聚合可见/staging/cache 树的退出状态；生产 Theme Studio draft 与隐藏内容关闭阻断回归通过。 |
| R-003、R-004 | 维持闭环及 PARTIAL | 启动 journal 恢复与 planner 单源、坏 JSON/启动兼容矩阵回归通过；不升级未测原生初始化矩阵。 |
| R-005 | 维持有边界闭环 | memento/拓扑/manifest 机械回归通过；原生多屏/DPI 仍 D-1。 |
| R-006、R-008 | 维持闭环 | 隔离夹具与当前写域核对；无本轮越界路径。 |
| R-009 | **数值一致性重新打开，P2** | 当前 AC6 验收行残留 r7 数值，详见 finding；原 UI freeze 上限/规模负载 PARTIAL 不变。 |
| R-011 | **证据定位重新打开，P2** | 两条证据 commit 指向旧内容，详见 finding；不是否认当前文件 SHA 匹配。 |
| R-012 | 维持闭环 | 两生成器日志已归档；本轮两项 `--check` 均实跑通过。 |
| R-013、R-014、R-015 | 维持闭环 | 同门排队/补偿顺序、memento、journal finalize 后内容/settings/id 补偿回归通过。 |
| R-016 | 索引结构维持闭环 | 23 个索引文件 SHA 均匹配，无自引用 SHA 行、非法控制字符 0；证据 commit 定位问题另归 R-011。 |
| R-017、R-018、R-019 | 维持闭环 | canonical/draft 同步、Loaded 解绑、staging 输入隔离相关回归通过；本轮未改其实现。 |
| R-020、R-021、R-022 | 维持闭环 | 稳定窗口全屏桥接、重复通知判别、提升后失败/取消补偿均有既有或本轮定向测试；没有新增生产回归证据。 |

因此不能笼统宣称 R-001…R-022 全部闭环：R-007 未关，R-009/R-011 有当前可定位残余，其余维持此前限定结论。

## 本轮重点实现判断

### R-023：屏障位置、排队与反向判别

`Services/FrontendHostCoordinator.cs:146–155` 在真实 layout/Loaded/render 门禁完成后、`PromoteStagedContent` 前调用 `_beforeContentCommit`。此时仍持有 `:97` 取得的 `_switchGate`。测试 `PresentationWindowTests.cs:453–467` 注入屏障；`:469–476` 等到屏障后，分别断言旧 Fluent 树身份、reader 全屏和 `WindowState.FullScreen`，所以不再像 r8 被审版本那样在 Normal 后才发 B。

`:478–480` 发起未知 frontend B，等待 100ms 后断言其未完成，证明它没有绕过门提前拒绝；`:482–491` 释放 A 后等待两者完成，检查 A success、B failure、当前 frontend 为 V2、目标 Border 内容、旧 reader=false、Window Normal、journal 文件消失。finally `:495` 释放屏障，避免断言失败时不释放。该定向测试本轮 **227ms PASS**。

断言覆盖应准确描述：**该排队用例本身没有直接断言 `_appearance.FrontendId` 或 `results[1].RolledBack=false`**。前者由既有 `PresentationWindowTests.cs:112–124`、`FrontendHostCoordinatorTests.cs:79–89,93–115` 的成功持久化/拒绝不改设置回归补充；后者由 coordinator `:102–109` 在快照前直接返回 false 明确保证，最终树/窗口/journal 也未被 B 改写。它不能被描述成一个已显式断言全部提交字段的排队用例；建议补这两条断言以便单独阅读，但当前缺少它们不再使原陈旧 FullScreen 缺陷逃过测试，不另计核心判别力 finding。

`rework-r8-verification.log:25–28` 记录了临时门外快照 mutation 的 Normal/FullScreen 失败摘要及恢复后 19/19。其机制可由当前代码重建：把模式快照在等待 `_switchGate` 前取得，并让拒绝结果也 Dispose 未提交快照，则 B 捕获 FullScreen；A 成功清全屏；B 拒绝后的 Dispose 将 V2 窗口改回 FullScreen，必然违反测试 `:490`。原 `5a495f80a` wrapper 的失败恢复也具有同一问题。**静态反事实支持日志所述判别力，当前实现实跑 PASS；独立 mutation 实跑为 NOT_RUN**。本轮受只读边界约束未修改源码；日志未保存完整 mutation patch/原始失败栈，不能把摘要称为本轮独立复现或完整原始 artefact。

### 生产构造、失败/取消/关闭与 standalone 回归

`PresentationWindow.cs:39–58` 公开生产 ctor 签名未变，向内部 ctor 明确传 `beforeCommit:null`；`:126–136` 透传诊断钩子。`App.axaml.cs:246–254` 仍调用公开 ctor；`beforeContentCommit` 在生产为 null，仅多一次空值检查，不修改 journal/settings/Host 生命周期。standalone `FluentShell.axaml.cs:31–48` 自行宿主 surface 与全屏桥接，不进入新钩子路径。

模式快照 `FrontendHostCoordinator.cs:190` 在 gate 内、reject/no-op 之后，且绑定同一 `previous`；成功只有在 switcher 返回成功后 `:198` Commit；finally `:205–210` 先解绑 Loaded、Dispose，再释放 gate。窗口事务 `PresentationWindow.cs:294–343` 同时保存 WindowState 与旧 reader 模式，未提交则恢复，已 Commit 则不写窗口。真实全屏提升后 finalize 失败与取消两个定向用例分别 **531ms/116ms PASS**，取消仍传播 OCE。退出聚合/关闭阻断和 standalone/启动/输入回归包含在全量中；未发现本轮新增生产故障。Normal/Maximized 的原生故障矩阵、IME、真实双屏不据此宣称完成。

## Standards（辅助视角，executed）

按辅助报告顺序：新增生产代码未发现记录标准的硬性违反；快照持门范围、唯一写者、App→Presentation 依赖和测试钩子默认 null 均符合 Task W-1/W-6/W-9/W-10；未发现值得单列的 Fowler smell。文档残余交由 Spec 与证据核对归并，不重复计数。

## Spec（辅助视角，executed）

按辅助报告顺序：R-007 派发文案仍冲突；AC6 当前数值未同步；R-023 核心反向判别已成立，但 settings/RolledBack 没有单用例直接断言。随后补核 canonical commit 语义，确认 R-011 两条证据定位错误。没有新增 scope creep；既有 PARTIAL/D-1 不转成新生产 finding。

## Findings

本轮仍需处置 **3 项 P2**，均为文档/证据残余；P0=0、P1=0。无新增生产代码 finding。

| ID | 级别 | 文件/行（文档 head `563f248c7`） | 触发与影响 | 复现证据 | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R-007 | **P2** | `doc/tasks/FEA-07.md:10,263,265`；`verification/FEA-07/evidence-index.md:9`；handoff `:28` | Task/索引仍写“r9 待派”，且声明与 STATUS/PLAN/checkpoint 同步；STATUS `:7`、PLAN `:21,39` 及 checkpoint §67 已为 r9 进行中，本次实际委派也已执行。当前 reviewer/source 状态互相矛盾。delivery 与 pending 值本身正确。 | 当前文件逐项对照，本轮用户委派及本报告来源。 | DSH 处置本报告时登记 r9 实际 reviewer/source/结果，统一 Task/索引/handoff 当前派发描述；集成前保持 canonical=pending。 | open，r8 残余 |
| R-009 | **P2** | `doc/tasks/FEA-07.md:273` | 当前 AC6 验收行仍列 r7 p50 **99.28** / p95 **374.09** / max **389.99**、两次 **299.40/374.09**；当前 JSON、摘要、索引及 Task `:264,306` 为 **109.89/381.43/383.05**、两次 **361.52/381.43**。这不是带历史标题的旧记录，而是当前验收行，导致无法按同一值核对 AC6。W-5 PASS 不受影响。 | JSON 20 样本重新排序计算；四处文本直接对照。 | 仅更新当前 AC6 数值及两次复测，保留 PARTIAL/UI freeze 上限说明；历史实施记录原样保留。 | open，数值一致性残余重新打开 |
| R-011 | **P2** | `doc/tasks/FEA-07.md:325–326`（EV-FEA07-FINAL、EV-FEA07-PERF-MD） | commit 列填 `aedc7251c`，但该提交内 final log/性能摘要仍为 **r7 / code head 462141f57**。依据该 pin 恢复会得到旧证据，无法恢复本表宣称的 r8 文件；当前工作区 SHA 正确不补足 commit 定位。 | `git show aedc7251c:verification/FEA-07/final-evidence.log`、同提交性能摘要均为 r7；`563f248c7` 对应文件才与当前内容一致。差异包含 head、时间、性能及测试时长，归一行尾后仍不同。 | 将这两行 commit 改为含本轮文件的 `563f248c7` 或后续实际含该版本的提交；文件内部被测 code_head 继续保留 `aedc7251c`。不要为了对齐而改写旧证据。 | open，精确证据定位残余重新打开 |

R-011 的规范依据是协作协议 `§4.1:85` 的“当前证据项…含该文件的 commit”和 Task 模板 `:63` 的“仓库内文件 pin commit”；表中 commit 没有被定义为被测代码 head。`check.ps1:691–714` 优先接受工作区 SHA，匹配后不会再比较该 commit 的 blob，故 PASS 不证明这些列语义正确。没有据此要求修改检查器或扩大 Task 范围。

## AC 逐条 Verdict

| AC | r9 Verdict | 依据与保留边界 |
|---|---|---|
| AC1 | **PARTIAL** | 真实树/状态保留、staging 门禁、提升后失败/取消补偿及排队拒绝不恢复旧模式均通过；R-023 核心判别力已补。原生 IME、真库 DB/current/pinned/Lock/source/candidate 零变化、ACK 重连和真实 Run/Intent 仍未验。 |
| AC2 | **PARTIAL** | Broker/退出聚合、真实 Theme Studio draft 和隐藏树关闭阻断回归通过；真实双窗归属与 Session/Region 单写 owner 集成未补。 |
| AC3 | **PARTIAL** | journal/启动恢复、finalize 补偿与同门排队回归通过；暂停期间真实保护状态变化、跨进程崩溃注入仍未补。 |
| AC4 | **PARTIAL** | planner 单源、坏 JSON、fallback/CLI/legacy 启动矩阵通过；真实 App 初始化与坏包/scale 原生矩阵仍未补。 |
| AC5 | **原生矩阵 BLOCKED / D-1；逻辑 PARTIAL** | memento/拓扑/PerMonitorV2 与稳定窗口全屏 headless 回归通过；双屏/拔屏/换主屏/100/125/150/200% DPI 原生验收 NOT_RUN，无截图，不能用 headless 替代。 |
| AC6 | **PARTIAL；W-5 PASS，文案一致性 FAIL** | 当前 Release p95 381.43ms≤1000ms，两次 361.52/381.43 均过；本轮 Debug 用例也过。R-009 当前 AC 行待同步；真实渲染冻结/规模负载未补。 |
| AC7 | **MET（冻结机械回归范围）** | build 0/0，全量1138/0/57，启动/依赖/TFM门禁及两生成器通过；相对1034/0/57增104 passed，fail/skip不增。 |
| AC8 | **PARTIAL，证据定位/描述待修** | 当前21项Task SHA、23项索引SHA与结构通过；R-007/R-011待修；原生矩阵/截图继续D-1，隔离夹具未升级为全部原生数据安全验收。 |

## 证据与治理核对表

本轮环境：2026-11-02，PowerShell **7.6.8**，Windows NT **10.0.26300.0**，SDK **10.0.401**，测试 runtime **.NET 9.0.11**。以下结果来自本轮实际命令，HEAD=`563f248c7`，源码树等同固定 code head。EXIT 和判别力输出记录于本报告，不覆盖原 verification 日志。

| 场景 | 命令/步骤 | EXIT / 结果 | 输出与边界 |
|---|---|---|---|
| Git/写域 | 前述五条 Git 命令，branch/common-dir、逐路径glob | **0 / PASS** | main/.git；89/89合法；代码树一致。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **0 / PASS** | **0 warnings / 0 errors**；5.67s。 |
| 全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **0 / PASS** | **1138 passed / 0 failed / 57 skipped**；App 2m15s。 |
| 重点定向 | 下列完整 filter 命令 | **0 / PASS，3/0/0** | finalize失败531ms；排队拒绝227ms；取消116ms。 |
| Presentation复核 | `dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` | **0 / PASS，38/0/0** | 单项目再次通过，325ms。 |
| TokenGen | `dotnet run --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | **0 / PASS** | 292 rows；every generated artifact matches frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | **0 / PASS** | generated theme artifacts match frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | **0 / PASS（3 warnings）** | 15 current documents；10个非终态Task、STATUS3169 bytes/29 lines、PLAN4759 bytes/64 lines既有告警。 |
| 契约 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **0 / PASS，15/15** | 与Task证据pins分开核对。 |
| Task工作区SHA | 解析Canonical Evidence逐项SHA256，与索引唯一路径行三方比较 | **0 / PASS，21/21** | 20 CANONICAL + 1 SUPPORTING；完整实测SHA见附录。 |
| 索引文件/结构 | 对23条文件行全部重新计算SHA；检查控制字符/自身SHA行 | **0 / PASS，23/23** | 非法控制字符0；自身SHA行0。 |
| final log | 内部head/工作区SHA/Task/index核对 | **PASS（当前文件）** | head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`；SHA=`e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785`。 |
| evidence commit | 按Task commit读取FINAL/PERF-MD原始blob，并归一CRLF比较正文 | **FAIL / R-011** | 指向aedc中的r7旧文件；563f248c7才含当前正文。 |
| 性能原始数据 | 排序20个样本，重算nearest-rank p50/p95/max | **PASS；W-5 PASS** | 第10项109.89，第19项381.43，max383.05；4预热+20单向切换。 |
| 性能四处一致性 | JSON/摘要/Task/索引及rework/handoff | **FAIL / R-009** | 除Task当前AC6行残留r7值外，其余当前记录为109.89/381.43/383.05，两次361.52/381.43。 |
| 本轮Debug性能 | 全量中的 `PerformanceBaselineTests.HotSwitch_P95_StaysWithinTheFrozenW5Budget` | **PASS** | p50 93.61/p95 312.79/max409.61ms；冷首次197.21ms；内存-10952B，handles+3；独立数值不替换canonical Release。 |
| 过程日志/交接 | rework-r8/final/handoff/Task关联 | **交付关联PASS；文案R-007** | 过程日志为b6b63574d+未提交返修；final单独绑定提交后代码head；没有把过程日志冒充提交后实跑。 |
| mutation反向独立实跑 | 未改源码/测试，未另建探针 | **NOT_RUN** | 仓库日志记有作者实测摘要；本轮只核对其反事实机制与当前测试，不称独立复现。 |
| 原生多屏/DPI | 双屏/拔屏/换主屏/100/125/150/200%矩阵 | **BLOCKED / D-1，NOT_RUN** | 不签发硬件验收，不伪造截图。 |

重点定向命令（exit 0）：

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --filter 'FullyQualifiedName~FailedSwitchAfterPromote_RestoresTheOriginalFullScreenMode|FullyQualifiedName~CancelledSwitchAfterPromote_RestoresTheOriginalFullScreenMode|FullyQualifiedName~QueuedRejectedSwitch_DoesNotRestoreAStaleWindowMode' --logger 'console;verbosity=normal'
```

### 全量计数与 skip 直接原因

| 项目 | passed | failed | skipped | 直接原因 |
|---|---:|---:|---:|---|
| Appearance | 21 | 0 | 0 | 无 |
| Presentation.Avalonia | 38 | 0 | 0 | 无 |
| Host | 51 | 0 | 28 | sidecar环境前置未满足 |
| ThemeEngine | 253 | 0 | 0 | 无 |
| DesignSystem | 87 | 0 | 0 | 无 |
| ApplicationCore | 31 | 0 | 0 | 无 |
| CoreClient | 128 | 0 | 22 | sidecar环境前置未满足 |
| App | 529 | 0 | 7 | CreateChapterHostIntegration 2、RunControllerHostIntegration 3、WritePolicyUiIntegration 1、StartupSelfCheckUi 1，均为sidecar前置 |
| **总计** | **1138** | **0** | **57** | **1195 tests；28+22+7=57** |

实测 `NEWMANGA_CORECLIENT_SIDECAR_DIR` **UNSET**。Host `Support/HostFixture.cs:13–20`、CoreClient `Support/SidecarFixture.cs:28–35` 先于其他路径/fixture检查返回skip；App对应集成夹具走相同前置。没有把后续BOOK/S4等夹具未设置当成本次直接原因，也未设置变量伪造通过。相对r8计数不变（测试改写未新增）；相对Task基线增加104 passed。

性能统计边界不变：20次单向切换=10次往返；p95取nearest-rank第19项，W-5≤1000ms通过。12样本取max也是合法的小样本分位数，摘要“才是真正的p95”的历史解释不严谨，前轮已记录，不另计新finding。事务总时长只是UI freeze上限，不是原生冻结测量或长期泄漏趋势证据。

### R-011 的 Git 复现与行尾区分

```powershell
git show aedc7251c:verification/FEA-07/final-evidence.log
git show aedc7251c:verification/FEA-07/performance-baseline.md
git show 563f248c7:verification/FEA-07/final-evidence.log
git show 563f248c7:verification/FEA-07/performance-baseline.md
```

前两项明确显示r7、head=`462141f57`，摘要p95=374.09；后两项为r8、head=`aedc7251c`、p95=381.43。上述命令均exit 0。未执行checkout或写临时文件。

原始blob SHA：aedc中的final=`bcccb071656e2f28ca62dc4b9bf1d91621c23038c0158ee25fc9bc603ce68cc8`，PERF-MD=`a1559f8595570d5f3688568150faf56c34aea291bc6d9fd4fe1777cbd94dc84f`。本地`core.autocrlf=true`；final工作区CRLF、blob LF，因此563中的final blob SHA为`32ce2c5b3f488d2948253e90fa5e9439512c1a8f24da2168cd11a7b132f3c595`，与工作区pin不同但归一行尾后相同。这种行尾差异**不是**本finding；aedc与当前两份正文归一行尾后依然不同，才是可定位缺陷。PERF JSON仅存在行尾差异，本轮没有误报它的commit正文不符。

## Architecture 与 Verification 结论

**Architecture：本轮代码返修成立。** beforeContentCommit仅测试诊断注入，生产ctor默认null；窗口模式仍属于同门事务，取消/失败补偿和拒绝路径没有新增越界。App→Presentation依赖、appearance唯一写者、Host/Core/SQLite/源文件保护边界保持，未发现本轮生产回归。

**Verification：机械与核心判别检查通过，当前文档/证据交付未完全一致。** build、全量1138/0/57、重点3/3、两生成器、治理、冻结pins15/15、工作区证据pins21/21及索引23/23均通过；R-023原排队判别缺口已关闭。R-007状态冲突、R-009当前AC旧值、R-011证据commit定位仍须处置。独立mutation未实跑与原生D-1均明确标记，不混作PASS。它们不构成新生产缺陷，也不允许将全部AC改为MET。

## 结论与复审

**Decision：`changes_requested`（P0=0 / P1=0 / P2=3）。** 本轮不要求重写窗口模式事务或扩大实现范围；剩余返修集中在当前Task/交接描述与证据定位。不能对包含矛盾的固定文档head签认完整交付。该结论不改变历史r6批准，不等于Task done、集成或push授权。

最小返修集：

1. DSH统一r9实际reviewer/source/本报告结果与Task/index/handoff的当前状态；保留历史Review原字节及canonical=pending。
2. 将当前AC6行更新为109.89/381.43/383.05ms、两次361.52/381.43ms；保留PARTIAL及原生/规模测量边界，不改历史阶段数值。
3. 修正FINAL、PERF-MD证据commit为实际含当前版本的`563f248c7`或后续真实提交，保留证据内部code_head=`aedc7251c`。如修改索引/摘要/证据，刷新受影响SHA；只改定位列不必重写已固定运行日志。
4. 固定新文档head后，重跑治理、15个契约pins、21项Task工作区SHA/索引以及**按commit取文件正文**核对；fresh上下文复核这三项。若源码树不变，可复用本报告代码审查与运行结果；任何新代码/测试改动均须相应build/test/生成器检查。DSH后续集成验证和closeout仍需另记，原生AC5继续BLOCKED/D-1，其他PARTIAL不得静默关闭。

推荐下一步：由 **DSH继续当前FEA-07的文档/证据返修**，不释放新实现Task。Recovery point为`G:\CODEX\New Manga`、main/.git、base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`、文档head=`563f248c771a79c6f913486258fb34f7ac200cff`、代码head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。范围限Task allowed_paths内必要文档/pin，不需要共享接口/schema/依赖变更；交付固定文档commit、处置记录、必要SHA和Handoff，再Appointment独立复核。`FEA-06-RESIDUAL-1`仍proposed，不因本报告自动启动。

可直接转发给DSH：

> 在`G:\CODEX\New Manga`、main、common dir`.git`继续FEA-07；base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`，被审文档head=`563f248c771a79c6f913486258fb34f7ac200cff`，代码head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。先Reality Check并保留dirty与本报告原文。按`doc/reviews/FEA-07-impl-r9.md`处置R-007/R-009/R-011：统一r9实际派发/结果；更新当前AC6为109.89/381.43/383.05与两次361.52/381.43；修正FINAL/PERF-MD证据commit使其能恢复当前r8文件，内部被测code_head仍为aedc7251c。只改Task allowed_paths内必要文档与pin，不改Core/schema/冻结契约/生成物/共享依赖/用户数据，不动其他worktree或历史Review。交付固定文档commit、disposition、Handoff及受影响SHA；执行`pwsh -NoProfile -File tools/governance/check.ps1`、`verify_pins.ps1`、21项Task/23项索引SHA核对和按commit读正文比对，记录EXIT与skip/BLOCKED/NOT_RUN。代码树不变则复用本轮build0/0、1138/0/57、两--check与R-023判别结论；如另改源码/测试则补相应验证。保留canonical pending、AC5原生BLOCKED/D-1与其他PARTIAL，Appointment fresh只读复核三项，再决定集成验证/closeout；不自动释放FEA-06-RESIDUAL-1。

## 附录：21项Task证据SHA-256三方核对

以下为实际工作区文件SHA，均与Task及索引对应唯一路径行一致，**21/21 PASS**；PERF-MD为SUPPORTING，其余20项为CANONICAL。该表证明当前文件哈希匹配，不能替代上文commit正文定位检查。

| evidence_id（EV-FEA07-） | 实测sha256 |
|---|---|
| SLICE1 | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` |
| SLICE2 | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` |
| SLICE2B | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` |
| SLICE2C1 | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` |
| SLICE2C2 | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` |
| SLICE3 | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` |
| SLICE4 | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` |
| SLICE5 | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` |
| PERF | `2ab2f5cfd7241238ca7676890db00b8a292548bb020eae9bbb8bcf7717ee20b7` |
| GAPCLOSING | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` |
| GENERATORS | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` |
| FINAL | `e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785` |
| PERF-MD | `d6b87c5a99868d90619354c1f71f0616669f5f6ac92a0d39cee44a586f85b458` |
| REWORK2 | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` |
| REWORK-R3-1 | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` |
| REWORK-R3-2 | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` |
| REWORK-R4 | `f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b` |
| REWORK-R5 | `e773a93def145d258ff09f8cb02ae9783823e7588e06443de28ba3381a3619b9` |
| REWORK-R6 | `322475cb618a71cf1f69e3422908a4d2b435ac53567462ffe1ba2309b01c5ae9` |
| REWORK-R7 | `9e4e04bd57bd9eadc238dd334b4cd502817fcfd2c7e8ac4904534b6c586e1144` |
| REWORK-R8 | `b739ac7c1f4c782e981a06b0ad01afa58ea12d64b38487998aeaa89c6504784a` |
