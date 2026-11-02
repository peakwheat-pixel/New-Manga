---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r10；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: ebda36be9（文档/证据 head；代码 head aedc7251c）
code_head: aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0
decision: changes_requested
counts:
  P0: 0
  P1: 0
  P2: 1
---

# Review：FEA-07 第 10 轮实现复核（impl-r10）

## Reviewer 身份与来源

Reviewer 为用户本轮明确委派的 fresh Codex CLI 独立上下文，未参与 FEA-07 设计、实现或返修；来源为本轮委派、`doc/handoffs/FEA-07-impl-r9.md` §4、rolling checkpoint §69。审查由当前独立主会话执行，未派发其他 Agent，未虚构 session ID。使用 code-review 的 Standards/Spec 视角；按本仓库协作协议 §6 与 Review 模板，不要求并行子 agent。Architecture、Verification、Standards、Spec 均为 executed。

唯一主动交付写入为本报告。未修改源码、测试、Task、STATUS、PLAN、历史 Review、既有证据或用户数据，未 commit/push，未进入其他 worktree。指定 build/test/生成器命令会产生常规忽略构建输出和测试自带临时夹具；性能用例固有输出为 `%TEMP%/nm-fea07-performance-baseline.json`，未回写仓库 JSON。未启动连接真实用户数据的产品，未写真实 `%APPDATA%/NewManga`，未做源码 mutation 或创建额外探针/日志。

## 范围与 Reality Check

- 工作目录 `G:\CODEX\New Manga`，branch=`main`，common directory=`.git`；起始及报告写入前 `git status --short` 为空。
- 实际 `HEAD=ebda36be9f5a4fb205372da1cf585408308908ac`，与用户固定文档 head 一致；代码 head 为 `aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。恢复事实 **RESUME_SAFE**；文档状态冲突另列 R-007。
- 已实跑 `git rev-parse HEAD`、`git status --short`、`git log --oneline -8`、`git diff --stat cbfb7bbc9..HEAD`、`git diff --name-only cbfb7bbc9..HEAD`。累计 **91 files changed / 9489 insertions(+) / 562 deletions(-)**；按 Task allowed_paths 逐路径匹配 **91/91 合法，越界 0**。固定 base 可解析，three-dot diff stat 相同。
- `aedc7251c..HEAD` 只有 **11 个 docs/evidence 文件**：PLAN、STATUS、checkpoint、handoff r8/r9、Review r8/r9、Task、index、final log、性能摘要。源码/测试无漂移：`git diff --quiet aedc7251c HEAD -- apps/desktop-avalonia` exit **0**；两端该目录 tree 均为 `f2b4459e77394721650d752cb91fed3f7a6518b2`。
- 本批 `563f248c7..ebda36be9` 只有 **8 个文档文件**：PLAN、STATUS、checkpoint、handoff r8、handoff r9、Review r9、Task、index；无源码、测试或原始测量文件变动。
- 已先读用户指定 r9/r8 Review、Task、STATUS、PLAN、final/index/rework-r8/handoff r9；再按引用核对 AD-002/AD-003 有效架构、协作协议相关生命周期条款、Review 模板、checkpoint §68–69、handoff r8、性能摘要/JSON及相关实现/测试。未扫描其他 worktree 或无关 verification。

实际 `git log --oneline -8`（exit 0）：

```text
ebda36be9 docs(fea-07): impl-r9 文档一致性处置（R-007/R-009/R-011）+ 证据索引/指针（code head aedc7251c；全量 1138/0/57）
563f248c7 docs(fea-07): impl-r8 处置 + mutation 判别证据/索引 + delivery 固定（head aedc7251c；全量 1138/0/57）
aedc7251c fix(fea-07): r8 返修（R-023 屏障前移至 Promote 前 + mutation 判别证据 / R-007 文案）；全量 1138/0/57
b6b63574d docs(fea-07): impl-r7 处置 + 返修证据/索引 + delivery/生命周期固定（head 462141f57；全量 1138/0/57）
462141f57 fix(fea-07): r7 返修（R-022 取消路径窗口模式补偿 / R-024 门内快照防陈旧恢复 / R-023 判别性测试）；全量 1138/0/57
226e47c51 docs(fea-07): impl-r6 approved + R-022 修复处置/证据/索引（head 5a495f80a；全量 1135/0/57）
5a495f80a fix(fea-07): r6 R-022 失败切换恢复原窗口全屏模式（含回归测试）；全量 1135/0/57
80b2203e5 docs(fea-07): impl-r5 处置 + 返修证据/索引 + delivery/生命周期固定（head 4e8510d43；全量 1134/0/57）
```

**源码及测试行号均以 `aedc7251c` 为准**；App 源码简称相对于 `apps/desktop-avalonia/src/NewManga.App/`，App 测试相对于 `apps/desktop-avalonia/tests/NewManga.App.Tests/`。新增文档处置用章节定位；文档 finding 的稳定行号核对于被审文档 head `ebda36be9`，不把该 head 新增文字冒充代码 head 已有内容。

## r9 findings 闭环表

| ID | r9 状态 | r10 Verdict | 核对事实 |
|---|---|---|---|
| R-007 | P2 open，appointment 文案 | **仍 open/P2，部分处置** | 最新已完成 Review 已更新到 r9，delivery 正确，canonical 仍 pending 且条件改为 r10 approved 后集成，均正确。但 Task reviewer/当前待办与索引仍为“r10 待派”，STATUS/PLAN 为 r10 进行中、checkpoint §69 已派发，本轮已执行；只把冲突中的轮次从 r9 改成 r10，未消除状态冲突。 |
| R-009 | P2 open，当前 AC6 旧数值 | **本轮数值残余闭环** | 当前 AC6 为 p50 109.89 / p95 381.43 / max 383.05，两次 p95 361.52/381.43，与 JSON/摘要/索引/handoff r8/r9 一致。r7 实施记录仍在其历史标题下；r9 处置段引用旧值说明修正不构成当前测量。PARTIAL/UI freeze 上限与规模负载未验说明保留。 |
| R-011 | P2 open，两条证据 commit 定位 | **本轮定位残余闭环** | FINAL/PERF-MD 均改为 `563f248c7`；逐条 `git show <commit>:<path>` 比较，9 条有明确 commit 的记录全部包含对应正文。文件内部 code head 仍为 aedc7251c；未为了对齐改写证据。12 条原有 `-` 另列未填写固定 commit 的边界，不冒称 21 条均有明确 commit。 |

更早 findings 的状态保留如下；闭环只针对已记录缺陷，不代表整个 AC 完整达成：

| ID | r10 状态与依据 |
|---|---|
| R-001、R-010 | 维持有边界闭环：真实 staging 布局/Loaded/帧门禁、缓存真实树及100次单向切换状态保留相关回归全量通过；原生/真库边界不升级。 |
| R-002 | 维持闭环：组合根传 allContentProvider，退出聚合覆盖可见/staging/缓存树，生产 Theme Studio draft 阻断关闭相关回归通过。 |
| R-003、R-004 | 维持有边界闭环：journal previous/last-committed 恢复、planner 单源 Selection、坏 JSON/启动兼容相关测试通过；真实初始化原生矩阵仍 PARTIAL。 |
| R-005、R-014 | 维持逻辑闭环：memento、拓扑 clamp、PerMonitorV2 回归通过；原生多屏/DPI 保持 D-1。 |
| R-006、R-008 | 维持闭环：测试临时根与本次91项允许路径匹配通过，无新增写域越界。 |
| R-012 | 维持闭环：生成器证据仍在，两项 --check 本轮实跑通过。 |
| R-013、R-015 | 维持闭环：同门串行化、finalize失败后内容/settings/id补偿、取消传播相关回归通过；代码无新漂移。 |
| R-016 | 维持索引结构闭环：23/23 SHA匹配，非法控制字符0、自引用SHA表行0。 |
| R-017、R-018、R-019 | 维持闭环：canonical/draft同步、Loaded解绑、staging输入隔离相关回归通过。 |
| R-020、R-021 | 维持闭环：稳定窗口全屏桥接、重复通知判别相关回归通过；未升级原生键路由/IME验收。 |
| R-022、R-023、R-024 | 维持r9确认的实现/核心判别力闭环：持门快照、失败/取消放门前补偿、Promote前屏障与排队拒绝最终状态，见下文；独立mutation实跑仍NOT_RUN。 |
| R-007、R-009、R-011 | 分别见本轮闭环表，不能笼统写 R-001…R-024 全部关闭。 |

### 关键实现回归与历史字节

`FrontendHostCoordinator.cs:97` 先等待 gate，`:102–116` 完成 reject/no-op，`:190` 才捕获同一 previous 的窗口模式；成功在 `:198` Commit，finally `:205–210` 先解绑/Dispose 再放门。`:146–155` 的屏障在所有真实门禁后、Promote前。模式事务 `PresentationWindow.cs:294–343` 保存窗口和旧reader模式，未提交Dispose恢复，成功后不恢复。没有本批新增的Host生命周期、持久化或分层变化。

`PresentationWindowTests.cs:373–435` 覆盖Promote后finalize失败及取消；`:444–497` 在旧树/reader/Window仍FullScreen时发起B并断言未完成，释放A后检查A成功/B失败、当前V2树、旧reader清全屏、Window Normal、journal清除。它可捕获门外陈旧FullScreen快照，维持r9核心判别力判断。该用例仍没有直接断言settings及B的RolledBack字段，不把关联测试/静态代码解释成该单用例已逐字段断言。作者mutation失败摘要位于rework-r8日志，本轮受只读边界限制**未独立执行mutation（NOT_RUN）**，未进入日志引用的仓外备份路径。

`git diff --quiet 563f248c7 HEAD -- <impl-r1…r8 Review路径>` 与scope-r1/r2比较均exit **0**。r9为本批新增，未被本轮修改。逐Review历史blob核对显示r1/r2/r4…r9与首次入库blob相同；r3在更早 `6a31fb92e` 有已存在的补记/文字修正，本批未触及，不能把“本批字节保留”扩写成从未有历史变动。final/performance-md/release-json/rework-r8相对563f248c7的diff均exit **0**。handoff r8追加了r9执行记录，它本身有一行变更，不能把其中“保留派发时字节”理解为整文件完全没变；历史Review字节要求未因此受损。

## Findings

**P0=0 / P1=0 / P2=1。** 无新增生产代码finding；R-007为r9残余。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R-007 | P2 | `doc/tasks/FEA-07.md:10`、该卡“impl-r9处置”当前appointment/待办；`verification/FEA-07/evidence-index.md:9`；handoff r9 §2 | Task reviewer仍写“r10待派”，索引也写“r10待派”；Task同时宣称“无待派指针矛盾”。STATUS :7 已为“r10独立复核进行中”，PLAN :21/:39为“r10复核中”，checkpoint §69与handoff §4已派发。恢复者会得到待派和执行中两种当前状态；上一轮要求的同步仍未完成。 | `rg -n 'r10\|reviewer:\|待办' doc/tasks/FEA-07.md verification/FEA-07/evidence-index.md doc/STATUS.md doc/REBASELINE_PLAN.md`，结合checkpoint §69与本轮委派；逐项实际读取。 | 分开记录“最新已完成Review=r9及其结果”和“当前Appointment=r10、fresh Codex CLI、来源handoff r9 §4/被审ebda36be9”。统一Task/索引/当前handoff/STATUS/PLAN/checkpoint当前事实；本报告落盘后记录实际结果。canonical保持pending，集成后才complete。避免只滚动成下一轮“待派”而再次冲突。 | open，r9残余 |

规范依据为协作协议 §4.1 当前Review生命周期、§5.2恢复事实、Review模板的Task reviewer/source登记要求。这里不要求预先写r10 approved，也不否认已经完成的r9 reviewer登记和正确的canonical条件；仅要求当前Appointment事实不与权威运行状态冲突。检查器PASS不能替代这一语义核对。

## AC 逐条 Verdict

| AC | r10 Verdict | 依据与边界 |
|---|---|---|
| AC1 | **PARTIAL** | 真实内容树/状态保留、staging门禁、失败/取消补偿与排队拒绝回归通过。原生IME、真库DB/current/pinned/Lock/source/candidate零变化、ACK重连与真实Run/Intent仍未验。 |
| AC2 | **PARTIAL** | Broker/退出聚合、生产Theme Studio draft与隐藏树关闭阻断通过；真实双窗归属与Session/Region单写owner集成仍待补。 |
| AC3 | **PARTIAL** | journal/启动恢复、finalize补偿、同门并发回归通过；暂停期间保护状态变化与跨进程崩溃注入未补。 |
| AC4 | **PARTIAL** | planner单源、坏JSON与CLI/fallback/legacy启动机械矩阵通过；真实App初始化及坏包/scale原生矩阵未补。 |
| AC5 | **原生矩阵BLOCKED / D-1；逻辑PARTIAL** | memento/拓扑/manifest/稳定窗口全屏headless回归通过。双屏/拔屏/换主屏/100/125/150/200% DPI原生NOT_RUN、无截图；不以headless替代。 |
| AC6 | **PARTIAL；W-5 PASS；数值一致性PASS** | Release p50 109.89/p95 381.43/max 383.05；两次p95 361.52/381.43均≤1000ms。当前AC行已同步；UI freeze仅事务总时长上限，真实渲染冻结/规模负载未补。 |
| AC7 | **MET（冻结机械回归范围）** | build 0/0，全量1138/0/57，启动/依赖/TFM门禁及两生成器通过；相对1034/0/57增加104 passed，failed/skipped不增。 |
| AC8 | **PARTIAL，R-007描述待修** | 21项Task SHA、23项索引SHA/结构、9项明确commit内容核对通过，R-011已修；Appointment仍不一致；原生矩阵/截图仍D-1。 |

## 证据与治理核对表

本轮环境：2026-11-02；PowerShell **7.6.8**，解释器 `C:\Program Files\PowerShell\7\pwsh.exe`；Windows NT **10.0.26300.0**；SDK **10.0.401**；测试runtime **.NET 9.0.11**。以下均为本轮实际执行，HEAD=ebda36be9。EXIT与实际输出摘要入本报告，未覆盖既有verification日志。

| 场景 | 实跑命令/核对 | EXIT / 结果 | 输出与限制 |
|---|---|---|---|
| Git/写域 | 前述Git五条命令、branch/common-dir、逐路径glob及code tree比较 | **0 / PASS** | main/.git；91/91合法；11项docs/evidence；源码树一致。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **0 / PASS** | **0 warnings / 0 errors**；9.18s。 |
| 全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **0 / PASS** | **1138 passed / 0 failed / 57 skipped**；App 2m41s；各程序集见下表。 |
| TokenGen | `dotnet run --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | **0 / PASS** | **292 rows**；every generated artifact matches the frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | **0 / PASS** | generated theme artifacts match the frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | **0 / PASS（3 warnings）** | 15 current documents；10非终态Task；STATUS3146 bytes/29 lines、PLAN4761 bytes/64 lines达到预算80%的既有告警。 |
| 契约pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **0 / PASS，15/15** | 与Task证据pins分开验证。 |
| Task SHA | Python内存解析21行，hashlib.sha256读取文件原始字节，与Task及索引对应路径核对 | **0 / PASS，21/21** | 20 CANONICAL + 1 SUPPORTING；完整SHA与commit见附录。 |
| 每条commit内容 | subprocess原始bytes读取 `git show <commit>:<path>`；正文仅归一CRLF/LF比较 | **0 / PASS，9/9明确commit** | 12行commit为既有 `-`，不计固定commit成功；额外与当前HEAD正文比较12/12相同。不是21/21明确commit定位。 |
| 索引 | 23行SHA逐项重算，检查自引用SHA行与非法控制字符 | **0 / PASS，23/23** | 自引用SHA行0；除合法TAB/LF/CR外控制字符0；路径/Task SHA一致。 |
| final/摘要内部head | 当前文件与563f248c7正文、Task/index/handoff对照 | **PASS** | 内部仍为完整aedc7251c代码head；不把563f248c7误写成被测代码head。 |
| 性能一致性 | release JSON排序20样本重算nearest-rank；摘要/当前AC6/index/handoff/rework逐项比对 | **PASS；W-5 PASS** | 第10项109.89，第19项381.43，max383.05；两次361.52/381.43，4预热+20单向切换。 |
| 本轮Debug性能 | 全量性能用例固有临时JSON | **PASS** | p50 122.32/p95 410.17/max510.45ms，冷首次230ms，内存+216B/handles -3；未替换canonical Release。 |
| 历史Review/原证据字节 | 563f248c7与HEAD指定路径git diff、历史blob比较 | **0 / PASS（本批）** | 既有Review和原始final/性能/rework内容未改；r3更早补记边界见前文。 |
| 当前appointment | Task/index/handoff对照STATUS/PLAN/checkpoint | **FAIL / R-007** | 待派与执行中同时存在；其余当前delivery/canonical pending正确。 |
| 独立mutation | 未改源码、未进入其他worktree | **NOT_RUN** | 作者日志有摘要；本轮只核对机制与当前回归，不冒称独立反向实跑。 |
| 原生矩阵 | 双屏/拔屏/换主屏/混合DPI 100/125/150/200% | **BLOCKED / D-1；NOT_RUN** | 未执行原生硬件验收，未生成截图，不签发完整产品验收。 |

`core.autocrlf=true`。Task SHA是工作区原始文件字节；Git blob可能为LF。FINAL在563f248c7的blob SHA为 `32ce2c5b3f488d2948253e90fa5e9439512c1a8f24da2168cd11a7b132f3c595`，工作区CRLF SHA为 `e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785`；仅行尾不同，正文一致。PERF-MD blob与工作区字节均为 `d6b87c5a99868d90619354c1f71f0616669f5f6ac92a0d39cee44a586f85b458`。9个明确commit全部核对正文，未把行尾差异误报为旧内容。

索引本身SHA为 `fb703bae03c3a97387fbf7c9b84020a8c5f8049fff65f7f0accc93e2d383b376`，仅在本报告外部记录，不回填索引自pin。12个 `-` 是现有定位精度限制，本轮未修改表或把它们伪称具体提交；R-011的两条错误commit已实际纠正。

### 全量计数与skip直接原因

| 程序集 | passed | failed | skipped |
|---|---:|---:|---:|
| Appearance | 21 | 0 | 0 |
| Presentation.Avalonia | 38 | 0 | 0 |
| Host | 51 | 0 | 28 |
| ThemeEngine | 253 | 0 | 0 |
| DesignSystem | 87 | 0 | 0 |
| ApplicationCore | 31 | 0 | 0 |
| CoreClient | 128 | 0 | 22 |
| App | 529 | 0 | 7 |
| **总计** | **1138** | **0** | **57** |

总数1195；28+22+7=57。`Test-Path Env:NEWMANGA_CORECLIENT_SIDECAR_DIR` 实测False。HostFixture、SidecarFixture、App的CreateChapterSidecarFixture/RunFixture/WritePolicy夹具均先检查该变量，返回“reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR …”。本次直接原因是该环境变量未设置，未执行后续BOOK/S4等夹具检查；没有把后续可能缺失的夹具当成本次直接原因。附录逐条列出57个skip，均适用该直接原因，未计入passed。

性能口径保留：20次单向切换=10次往返；p95为nearest-rank第19项，事务总时长只是UI freeze上限。12样本取max也是合法的小样本分位数，摘要“才是真正的p95”的旧解释不严谨，前轮已记录，本轮未改写该历史解释，也不据此扩大新finding。

## Architecture 与 Verification 结论

**Architecture：在本轮范围内通过。** 本批仅文档变化，代码树保持aedc7251c；窗口模式快照、补偿、同门串行化和Promote前屏障仍成立。App→Presentation依赖方向、appearance唯一写者、Host/Core/SQLite/源文件保护边界未出现本批回归；未引入依赖、schema或共享冻结契约变化。此判断不替代原生多屏、IME和真库保护矩阵验收。

**Verification：指定机械检查全部通过，文档语义核对仍有1项P2。** R-009/R-011本轮残余闭环；R-007仍存在可直接定位的当前状态矛盾。AC1–AC4/AC6/AC8保持PARTIAL、AC5原生BLOCKED/D-1、AC7限定范围MET。Standards未发现本批新增实现规范问题；Spec/恢复指针一致性未通过。检查器绿灯与1138/0/57不替代文档事实一致性。

## 结论与复审

**Decision：`changes_requested`（P0=0 / P1=0 / P2=1）。** 本轮只保留R-007的appointment文案残余；不要求修改已通过回归的生产代码或测试，不撤改r6 approved及r7/r8/r9历史报告。本结论不是Task done、集成或push授权。

最小返修集：

1. DSH在当前FEA-07范围内统一当前Appointment事实：分开“最新完成Review”与“正在执行/已完成的本轮Appointment”，登记真实Reviewer/source、固定文档/代码head及本报告结果；修正Task/index/当前handoff中“r10待派”及“无矛盾”断言，与STATUS/PLAN/checkpoint一致。历史Review不改写，canonical继续pending，避免仅把待派轮次顺延。
2. 保留R-009当前数值、R-011两条563f248c7定位及内部aedc7251c、现有21/23项SHA；只在实际改动对应证据时重算其pin。原生D-1和其他PARTIAL保持明确，不得改成通过。
3. 交付纯文档固定commit和handoff，运行check/verify_pins、21项SHA/9项明确commit内容/23行索引和源码树不变核对，再Appointment fresh只读定点复审。若源码树未变，产品测试无需仅因文案修正重复运行；若改代码/测试则新代码head重跑相应完整验证。通过后由DSH执行集成验证及closeout。

推荐下一步：**DSH继续当前FEA-07的R-007文档返修与定点复审**。启动条件为接收本报告并Reality Check；这是现有任务内的安全返修，不自动释放proposed的FEA-06-RESIDUAL-1。Recovery point为主仓库/main/.git，base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`，文档head=`ebda36be9f5a4fb205372da1cf585408308908ac`，代码head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。允许Task/index/当前handoff/STATUS/PLAN/checkpoint的必要文档处置与后续新Review；不改生产源码、测试、Core/schema/冻结契约/依赖/真实用户数据、历史Review，不进入其他worktree。交付固定文档commit、更新handoff/证据核对结果、新的独立复审报告；完成Gate为R-007无当前状态矛盾、机械核对通过，再由DSH集成及生命周期裁定。

可直接转发给DSH：

> 在 `G:\CODEX\New Manga`、main、common dir `.git` 继续FEA-07；base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`，文档head=`ebda36be9f5a4fb205372da1cf585408308908ac`，代码head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。先核对Git并保护dirty及本报告原文。按 `doc/reviews/FEA-07-impl-r10.md` 仅处置R-007：分开最新已完成Review与当前Appointment，统一Task/index/当前handoff/STATUS/PLAN/checkpoint的r10实际执行及本报告结果；不要只把“待派”滚动到下一轮。保留R-009当前109.89/381.43/383.05和两次361.52/381.43，保留R-011的FINAL/PERF-MD commit=563f248c7与内部code_head=aedc7251c，canonical保持pending，原生AC5 BLOCKED/D-1及其他PARTIAL不改为PASS。只改当前Task允许的必要治理/交付文档；不改源码、测试、Core/schema/冻结契约/依赖、历史Review或真实用户数据，不进入其他worktree。交付固定文档commit、handoff与核对结果，执行 `pwsh -NoProfile -File tools/governance/check.ps1`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`，核对Task21项SHA、9项明确commit内容、12项原有未填commit边界、索引23行/自引用0/控制字符0及aedc到新head源码树不变。纯文档可复用本轮1138/0/57及两生成器通过证据；若改代码/测试则重新固定head并跑完整build/test/两--check。Appointment fresh只读定点复审通过后再由DSH做集成验证/closeout；不自动启动FEA-06-RESIDUAL-1。

落盘后复核：`check.ps1` 再跑 exit **0 / PASS（同3个告警）**；HEAD仍为 `ebda36be9f5a4fb205372da1cf585408308908ac`，`git diff --stat` 为空，`git status --short` 唯一条目为 `?? doc/reviews/FEA-07-impl-r10.md`。报告附录21项pin、57项skip条目齐全，非法控制字符0。未commit/push。

## 附录A：21项Task pin逐条核对

以下SHA均按工作区原始字节计算，和Task及索引唯一路径行相同。commit内容比较仅归一行尾；`-` 表示Task未指定固定commit，额外与HEAD正文一致，不能称固定commit验证成功。

| evidence_id（EV-FEA07-） | Task commit | 实测SHA-256 | 内容核对 |
|---|---|---|---|
| SLICE1 | `-` | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` | 未指定；HEAD正文一致 |
| SLICE2 | `-` | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` | 未指定；HEAD正文一致 |
| SLICE2B | `-` | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` | 未指定；HEAD正文一致 |
| SLICE2C1 | `-` | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` | 未指定；HEAD正文一致 |
| SLICE2C2 | `-` | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` | 未指定；HEAD正文一致 |
| SLICE3 | `-` | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` | 未指定；HEAD正文一致 |
| SLICE4 | `-` | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` | 未指定；HEAD正文一致 |
| SLICE5 | `-` | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` | 未指定；HEAD正文一致 |
| PERF | `aedc7251c` | `2ab2f5cfd7241238ca7676890db00b8a292548bb020eae9bbb8bcf7717ee20b7` | 指定commit正文一致 |
| GAPCLOSING | `-` | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` | 未指定；HEAD正文一致 |
| GENERATORS | `-` | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` | 未指定；HEAD正文一致 |
| FINAL | `563f248c7` | `e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785` | 指定commit正文一致 |
| PERF-MD | `563f248c7` | `d6b87c5a99868d90619354c1f71f0616669f5f6ac92a0d39cee44a586f85b458` | 指定commit正文一致 |
| REWORK2 | `-` | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` | 未指定；HEAD正文一致 |
| REWORK-R3-1 | `-` | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` | 未指定；HEAD正文一致 |
| REWORK-R3-2 | `100d487ff` | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` | 指定commit正文一致 |
| REWORK-R4 | `b328f3488` | `f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b` | 指定commit正文一致 |
| REWORK-R5 | `4e8510d43` | `e773a93def145d258ff09f8cb02ae9783823e7588e06443de28ba3381a3619b9` | 指定commit正文一致 |
| REWORK-R6 | `5a495f80a` | `322475cb618a71cf1f69e3422908a4d2b435ac53567462ffe1ba2309b01c5ae9` | 指定commit正文一致 |
| REWORK-R7 | `462141f57` | `9e4e04bd57bd9eadc238dd334b4cd502817fcfd2c7e8ac4904534b6c586e1144` | 指定commit正文一致 |
| REWORK-R8 | `aedc7251c` | `b739ac7c1f4c782e981a06b0ad01afa58ea12d64b38487998aeaa89c6504784a` | 指定commit正文一致 |

## 附录B：57项skip逐条来源与原因

下列每项的直接原因均为 **NEWMANGA_CORECLIENT_SIDECAR_DIR未设置**；是skip，不是PASS。名称省略公共命名空间，各组对应其测试程序集。

### NewManga.Host.Tests（28）

- `ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory` — sidecar环境变量未设置。
- `ExportE2ETests.Export_Cancel_LeavesNoArtifact` — sidecar环境变量未设置。
- `HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe` — sidecar环境变量未设置。
- `HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames` — sidecar环境变量未设置。
- `HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry` — sidecar环境变量未设置。
- `HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged` — sidecar环境变量未设置。
- `StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites` — sidecar环境变量未设置。
- `StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable` — sidecar环境变量未设置。
- `StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites` — sidecar环境变量未设置。
- `CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain` — sidecar环境变量未设置。
- `HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked` — sidecar环境变量未设置。
- `HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost` — sidecar环境变量未设置。
- `HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` — sidecar环境变量未设置。
- `RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration` — sidecar环境变量未设置。
- `GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths` — sidecar环境变量未设置。
- `GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages` — sidecar环境变量未设置。
- `GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant` — sidecar环境变量未设置。
- `GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled` — sidecar环境变量未设置。
- `HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes` — sidecar环境变量未设置。
- `HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection` — sidecar环境变量未设置。
- `HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall` — sidecar环境变量未设置。
- `WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook` — sidecar环境变量未设置。
- `WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError` — sidecar环境变量未设置。
- `WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog` — sidecar环境变量未设置。
- `LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites` — sidecar环境变量未设置。
- `HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized` — sidecar环境变量未设置。
- `HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection` — sidecar环境变量未设置。
- `ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames` — sidecar环境变量未设置。

### NewManga.CoreClient.Tests（22）

- `Commands.S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore` — sidecar环境变量未设置。
- `HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly` — sidecar环境变量未设置。
- `HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling` — sidecar环境变量未设置。
- `HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle` — sidecar环境变量未设置。
- `Commands.CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` — sidecar环境变量未设置。
- `Commands.CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore` — sidecar环境变量未设置。
- `Commands.CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce` — sidecar环境变量未设置。
- `Commands.CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons` — sidecar环境变量未设置。
- `Commands.CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake` — sidecar环境变量未设置。
- `Commands.CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars` — sidecar环境变量未设置。
- `Commands.RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame` — sidecar环境变量未设置。
- `Commands.RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings` — sidecar环境变量未设置。
- `Commands.RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty` — sidecar环境变量未设置。
- `Commands.RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides` — sidecar环境变量未设置。
- `SidecarFailureTests.StartupTimeout_IsTyped_NotAHang` — sidecar环境变量未设置。
- `CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError` — sidecar环境变量未设置。
- `CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` — sidecar环境变量未设置。
- `CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23` — sidecar环境变量未设置。
- `CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest` — sidecar环境变量未设置。
- `Commands.CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture` — sidecar环境变量未设置。
- `Commands.CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore` — sidecar环境变量未设置。
- `Commands.CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` — sidecar环境变量未设置。

### NewManga.App.Tests（7）

- `CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures` — sidecar环境变量未设置。
- `CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly` — sidecar环境变量未设置。
- `WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason` — sidecar环境变量未设置。
- `RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly` — sidecar环境变量未设置。
- `RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey` — sidecar环境变量未设置。
- `RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys` — sidecar环境变量未设置。
- `StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot` — sidecar环境变量未设置。

