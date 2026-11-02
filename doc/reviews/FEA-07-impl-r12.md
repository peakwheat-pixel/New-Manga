---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r12；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: 527a7ec37（文档/证据 head；代码 head aedc7251c）
code_head: aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0
decision: approved
counts:
  P0: 0
  P1: 0
  P2: 1
---

# Review：FEA-07 第 12 轮实现复核（impl-r12）

## Reviewer 身份与来源

本报告由用户委派的 fresh Codex CLI 独立上下文完成；未参与 FEA-07 的设计、实现或返修。Appointment 来源为本轮只读委派、Task reviewer 字段、`doc/handoffs/FEA-07-impl-r11.md` §4、rolling checkpoint §73。未派发子 agent，未虚构会话 ID。项目 Lead / Architect / Integrator 为 DSH，本报告不代行生命周期、集成、资源处置或 push 权限。

采用 `code-review` 技能；依仓库 Review 模板及协作协议 §6 的明确覆盖，不要求双轴并行子 agent。Architecture、Verification、Standards、Spec 均为 **executed**。

唯一主动交付写入为本报告；没有修改源码、测试、Task、STATUS、PLAN、checkpoint、历史 Review、canonical 证据或用户数据，没有 commit/push，没有进入其他 worktree。指定 build/test/生成器会产生通常的忽略构建输出、测试临时夹具及性能用例固有的 `%TEMP%/nm-fea07-performance-baseline.json`；未将运行产物回写 canonical 证据。未启动连接真实数据的产品，未主动写真实 `%APPDATA%`，未进行源码 mutation。

## 范围与 Reality Check

- 实际仓库 `G:\CODEX\New Manga`，branch=`main`，Git common directory=`.git`。起始和报告写入前 HEAD 均为 **`527a7ec3797f39c24b92ee3e2062fa41777b7b32`**，`git status --short` 为空；固定 base 可解析，**RESUME_SAFE**。
- 已实跑 `git rev-parse HEAD`、`git status --short`、`git log --oneline -10`、`git diff --stat cbfb7bbc9..HEAD`、`git diff --name-only cbfb7bbc9..HEAD`；累计 **95 files changed / 10078 insertions(+) / 562 deletions(-)**。three-dot diff 统计相同；按 Task allowed_paths 逐路径匹配 **95/95 合法，越界 0**。
- `aedc7251c..HEAD` 只有 **15 个 docs/evidence 文件**。`git diff --quiet aedc7251c HEAD -- apps/desktop-avalonia` 为 **exit 0**，两端 `apps/desktop-avalonia` tree 均为 **`f2b4459e77394721650d752cb91fed3f7a6518b2`**。无源码、测试、依赖或生成物漂移。
- 本批 `91de6a345..527a7ec37` 仅 **8 个文档文件 / +531/-10**：PLAN、STATUS、checkpoint、handoff r11、Review r10/r11、Task、evidence-index。Review r10/r11 为新增；没有修改任何该批之前已入库的 FEA-07 Review。
- 已读用户指定的 r11/r10/r9 Review、Task、STATUS、PLAN、handoff r11、final log、index、rework-r8；按当前引用补读 checkpoint 当前 §72/§73、Review 模板、协作协议 §4/§5.1/§6、AD-002/AD-003 当前边界、性能摘要/JSON、相关模式事务及排队回归实现。没有扫描无关 Task、历史 verification 目录或其他 worktree。

实际最近 10 个提交（`git log --oneline -10`，exit 0）：

```text
527a7ec37 docs(fea-07): impl-r11 处置（恢复 r10 原始报告 + 指针一致性，Appointment=impl-r12）+ 索引（code head aedc7251c；全量 1138/0/57）
91de6a345 docs(fea-07): impl-r10 R-007 最终处置（已完成 Review 与当前 Appointment 分离）+ 索引/指针（code head aedc7251c；全量 1138/0/57）
ebda36be9 docs(fea-07): impl-r9 文档一致性处置（R-007/R-009/R-011）+ 证据索引/指针（code head aedc7251c；全量 1138/0/57）
563f248c7 docs(fea-07): impl-r8 处置 + mutation 判别证据/索引 + delivery 固定（head aedc7251c；全量 1138/0/57）
aedc7251c fix(fea-07): r8 返修（R-023 屏障前移至 Promote 前 + mutation 判别证据 / R-007 文案）；全量 1138/0/57
b6b63574d docs(fea-07): impl-r7 处置 + 返修证据/索引 + delivery/生命周期固定（head 462141f57；全量 1138/0/57）
462141f57 fix(fea-07): r7 返修（R-022 取消路径窗口模式补偿 / R-024 门内快照防陈旧恢复 / R-023 判别性测试）；全量 1138/0/57
226e47c51 docs(fea-07): impl-r6 approved + R-022 修复处置/证据/索引（head 5a495f80a；全量 1135/0/57）
5a495f80a fix(fea-07): r6 R-022 失败切换恢复原窗口全屏模式（含回归测试）；全量 1135/0/57
80b2203e5 docs(fea-07): impl-r5 处置 + 返修证据/索引 + delivery/生命周期固定（head 4e8510d43；全量 1134/0/57）
```

**源码及测试行号均以 `aedc7251c` 为准**。下文 App 源码简称相对于 `apps/desktop-avalonia/src/NewManga.App/`，App 测试相对于 `apps/desktop-avalonia/tests/NewManga.App.Tests/`。新增文档以章节定位；R-026 所引索引第 9 行在 `aedc7251c` 和文档 head 中均为第 9 行，不混用新增文档与代码 head 行号。

## r11 findings 闭环表

| ID | r11 状态 | r12 Verdict | 本轮事实 |
|---|---|---|---|
| R-025 | 唯一 P2；r10 原报告未入库 | **闭环** | r10/r11 均在 HEAD 和工作区存在，`git cat-file -e HEAD:<path>` 均 exit 0；r10 为 271 行完整报告，包含身份/来源、固定 head、R-007、AC、实跑记录、结论及 skip 附录；r11 为 188 行完整报告，保留其缺报告 finding 与 changes_requested。内容并非 Owner 摘要占位。 |
| R-007 | 当前状态文案已消除冲突 | **维持闭环** | 最新已完成=r11 changes_requested、P2 已处置；当前 Appointment=r12 fresh Codex CLI、复核进行中；canonical=pending，r12 approved 并集成后才 complete。未将 r12 预写为 approved 或待派。 |
| R-009 | 数值一致性闭环 | **维持闭环** | JSON/摘要/当前 AC6/index 均为 109.89/381.43/383.05 ms；摘要/AC6/index/rework-r8/handoff 的两次 p95 均为 361.52/381.43。UI freeze 上限和规模负载 PARTIAL 保留。 |
| R-011 | FINAL/PERF-MD commit 定位闭环 | **维持闭环** | 两项均指向实际包含当前正文的 `563f248c7`；内部被测代码 head 仍为 `aedc7251c`，未改写证据来迁就 commit。 |

当前指针逐载体核对：

| 载体 | 最新已完成 / 当前 Appointment / 完成条件 |
|---|---|
| Task reviewer、impl-r11 处置、canonical 字段 | r11 changes_requested，缺 r10 原报告已补；r12 进行中，来源 handoff r11 §4；pending，集成后 complete |
| evidence-index 当前复核行 | impl-r1–r5/r7–r11 changes_requested 已处置，impl-r6 approved；Appointment=r12 复核中；scope 历史摘要另有非阻塞 R-026 |
| STATUS 当前 Task、下一步 | 最新 r11 P2 已处置；r12 复核中；Task 仍 in_progress |
| PLAN FEA-07 行、当前 DAG | r3–r11 返修 done 指返修实施完成；Appointment=r12 复核中，FEA-07 仍 in_progress，未冒充 Task done |
| checkpoint §72/§73 | r11 changes_requested 已处置，r12 fresh 只读；canonical 仍 pending，approved 后另行集成验证 |
| handoff r11 §1/§2/§4/§5 | 最新已完成 r11；当前 r12，被审文档为该 handoff 所在提交 `527a7ec37`；代码 aedc7251c；集成/残余/closeout 后再决定 done |

旧 checkpoint/handoff/Task 历史处置段中的旧轮次按其标题保留，不再作为当前 Appointment。没有新增当前轮次或运行状态矛盾。

更早 findings 仅在原有边界内维持：

| ID | r12 状态与依据 |
|---|---|
| R-001、R-010 | 维持真实内容树缓存、100 次单向切换与 staging layout/Loaded/帧门禁闭环；全量回归通过，原生 IME/真库边界仍 PARTIAL。 |
| R-002 | 维持 visible/staging/cache 退出聚合、生产 Theme Studio draft 与隐藏树关闭阻断闭环；真实双窗单写 owner 集成未升级。 |
| R-003、R-004、R-005 | 维持 journal 恢复、planner 单源/坏 JSON、memento/拓扑/manifest 逻辑闭环；真实初始化/多屏矩阵未升级。 |
| R-006、R-008、R-012 | 临时根夹具、95/95 allowed_paths、两生成器实跑通过；无新增隔离或写域问题。 |
| R-013、R-014、R-015 | 同门串行/补偿、memento、journal finalize 故障回滚相关回归通过；源码不变。 |
| R-016 | 23/23 索引文件 SHA 一致，自身 SHA 行 0、非法控制字符 0；历史结论摘要 R-026 与哈希/结构问题分开记录。 |
| R-017、R-018、R-019 | 外观/draft 同步、Loaded 解绑、staging 输入隔离回归通过，未改其实现。 |
| R-020、R-021 | 稳定窗口全屏桥接与重复通知回归通过；原生路由、IME 未扩大签认。 |
| R-022、R-024 | `FrontendHostCoordinator.cs:97,102,114,190,198,205–210`：快照在持门且 reject/no-op 后，成功 Commit，失败/取消补偿后放门；`PresentationWindow.cs:294–343` 同时恢复窗口及旧 reader 模式；维持闭环。 |
| R-023 | `FrontendHostCoordinator.cs:151–155` 的屏障位于 Promote 前；`PresentationWindowTests.cs:448–491` 明确旧树全屏、B 排队、A 成功/B 拒绝及最终 Normal/journal 清除。维持核心判别力闭环；单用例 settings/RolledBack 直接断言边界、独立 mutation NOT_RUN 均不扩大。 |

## Review 报告完整性及历史字节

13 份所需报告全部存在于工作区及 HEAD，均有真实正文、front matter、固定点与结论，非占位文件。front matter 核对如下；counts 顺序为 P0/P1/P2：

| 报告 | decision | counts | reviewed_head（文档 head 简写） |
|---|---|---|---|
| scope-r1 | changes_requested | 0/6/2 | e9d542ab4 |
| scope-r2 | approved | 0/0/1 | cbfb7bbc9 |
| impl-r1 | changes_requested | 0/7/5 | 62fb6c5f5 |
| impl-r2 | changes_requested | 0/6/3 | f28d97b99 |
| impl-r3 | changes_requested | 0/5/2 | b3fa8dc0c |
| impl-r4 | changes_requested | 0/3/3 | ad56bea1c |
| impl-r5 | changes_requested | 0/1/2 | ea27a7b10 |
| impl-r6 | approved | 0/0/2 | 80b2203e5 |
| impl-r7 | changes_requested | 0/0/4 | 226e47c51 |
| impl-r8 | changes_requested | 0/0/2 | b6b63574d |
| impl-r9 | changes_requested | 0/0/3 | 563f248c7 |
| impl-r10 | changes_requested | 0/0/1 | ebda36be9 |
| impl-r11 | changes_requested | 0/0/1 | 91de6a345 |

r10 的唯一 finding 为 R-007，R-009/R-011 明确闭环；r11 的唯一 finding 为 R-025，明确承认 R-007 文案已消除。二者 front matter、Findings、结论与 Task 的历史转述相符；保留 changes_requested 原文，没有把“已处置”回写成历史批准。scope-r1 的 Task 处置节也正确记为 changes_requested；只有索引把两轮 scope 合并写为 approved，见 R-026。

- 逐文件比较 `91de6a345:<report>` 与 `HEAD:<report>`，该时点已存在的 impl-r1–r9、scope-r1/r2 共 **11/11 Git 原始 blob 完全一致**。本批只有新增 r10/r11。r3 更早曾有补记/文字修正，不能声称所有报告从首次入库起从未变化；本批没有改写它。
- r10 当前工作区 SHA-256：`fa04289c33f8c64a1e6227dc5d8cfcdd58a69e92d1a5930448e2ea6ad6a5f82d`；HEAD blob：`d168fcb5d8ce37345976195da7d0a1840c122161`。
- r11 当前工作区 SHA-256：`434c954517cf47664c83fb299a1913a5df138c15a082ad37477f87809f39d05b`；HEAD blob：`2123d29cb0a0db4d0fec9ebf74a4037fd858a125`。
- r10/r11 首次入库提交均为 `527a7ec37`。本轮固定其内容指纹并确认正文及历史 head 可核验；仓库没有恢复前的独立原始字节指纹，故不将 Owner 的“SHA 不变”扩写成跨仓外原件的密码学证明。未发现重写/伪造的仓库证据，R-025 的报告缺失与来源不可读问题已消除。

## AC 逐条 Verdict

| AC | r12 Verdict | 证据及保留边界 |
|---|---|---|
| AC1 | **PARTIAL** | 真实树/状态保留、staging 门禁、失败/取消及排队拒绝回归通过；原生 IME、真库 DB/current/pinned/Lock/source/candidate 零变化、ACK 重连及真实 Run/Intent 未补验。 |
| AC2 | **PARTIAL** | Broker/退出聚合、真实 draft 与隐藏树关闭保护回归通过；真实双窗归属与 Session/Region 单写 owner 集成待补。 |
| AC3 | **PARTIAL** | journal/启动恢复、同门串行、finalize 补偿回归通过；暂停期间保护状态变化及真实跨进程崩溃注入待补。 |
| AC4 | **PARTIAL** | planner/坏 JSON/fallback/CLI/legacy 机械矩阵通过；真实 App 初始化与坏包/scale 原生矩阵待补。 |
| AC5 | **原生矩阵 BLOCKED / D-1；逻辑 PARTIAL** | memento/拓扑/PerMonitorV2/全屏 headless 回归通过；原生双屏/拔屏/换主屏、100/125/150/200% DPI 矩阵 NOT_RUN，无硬件矩阵和截图，不以 headless 替代。 |
| AC6 | **PARTIAL；W-5 PASS** | 20 样本重算 109.89/381.43/383.05 ms，两次既存 p95 361.52/381.43≤1000 ms，当前四处一致；真实 UI freeze/规模负载/真机指标待补。 |
| AC7 | **MET（冻结机械回归范围）** | build 0/0、全量 1138/0/57、启动/依赖/TFM 门禁与两生成器通过；相对 1034/0/57 基线 +104 passed，failed/skip 不增。 |
| AC8 | **PARTIAL** | Review 缺报告闭环；21 pin、23 行索引和 9 条明确 commit 正文核对通过；非阻塞历史摘要 R-026 待处置，原生矩阵/截图仍 D-1。 |

本轮批准是对固定 head 的本次补全与既有实现边界的 Review 接受，不把 PARTIAL、BLOCKED 或 Task 的勾选解释为所有 AC 已 MET。Task 仍 in_progress；残余/waiver、集成验证、资源 closeout 和 done 判定由 DSH 另行处理。

## Findings

**P0=0 / P1=0 / P2=1。** R-025 已闭环，无新增生产代码 finding。新增一项**非阻塞 P2**，属于历史 Review 摘要准确性，不是当前 Appointment 冲突，也不重开 R-007。

| ID | 级别 | 文件/定位 | 触发与影响 | 复现证据 | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R-026 | P2，非阻塞 | `verification/FEA-07/evidence-index.md:9`；对照 `doc/reviews/FEA-07-scope-r1.md` front matter 和 Task scope-r1 处置节 | 索引写 `scope-r1/r2 approved`，但 scope-r1 原结论是 changes_requested（0/6/2），只有 scope-r2 approved（0/0/1）。按索引恢复历史时会误读 r1 的实际结论。该摘要在前序 head 已存在，本批改写该行时保留；没有影响 r2 的实际范围批准、当前 r12 Appointment、代码或 SHA pin。 | 读取两份 scope 原报告、Task 处置节及索引第 9 行；`git show 91de6a345:verification/FEA-07/evidence-index.md` 可确认并非本批新增的范围授权变化。 | 只将当前索引摘要改为 `scope-r1 changes_requested 已处置；scope-r2 approved`，保留 scope 原报告和历史署名字节。 | open，交 DSH 处置 |

规范依据为协作协议 §4.1 的历史 Review 原结论不改写、§5 的可恢复证据，以及本轮要求的报告结论/指针核对。该偏差没有隐藏未处理 P0/P1，也没有造成缺报告或当前状态歧义；按 Review 模板“P0/P1 未解决或关键验证缺失不可批准”的门槛，不阻塞本轮 R-025 补全批准。

## 证据与治理核对表

本轮 shell/environment：2026-11-02，PowerShell **7.6.8**，Windows NT **10.0.26300.0**，SDK **10.0.401**，测试目标 **net9.0**，已安装 runtime **9.0.11**。以下为本会话实跑或直接重算，未覆盖原 verification 日志；EXIT 与摘要入本报告。

报告落盘后复查：HEAD 未变，`git status --short` 仅有 `?? doc/reviews/FEA-07-impl-r12.md`，`git diff --name-only` 为空；治理再次实跑 exit 0、PASS（同样 3 warnings）。

| 检查 | 实际命令/方法 | EXIT / Verdict | 结果 |
|---|---|---|---|
| Git 固定点/写域 | 前述五条命令、branch/common-dir、逐路径 glob | **0 / PASS** | 起始 clean，main/.git，95/95 合法，15 项 docs/evidence，代码树相同。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **0 / PASS** | **0 warnings / 0 errors**；6.74s。 |
| 全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **0 / PASS** | **1138 passed / 0 failed / 57 skipped**；App 2m32s。 |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | **0 / PASS** | **292 rows**，every generated artifact matches the frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | **0 / PASS** | generated theme artifacts match the frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | **0 / PASS，3 warnings** | 15 current documents；10 非终态 Task；STATUS 3161 bytes/29 lines、PLAN 4803 bytes/64 lines 达预算 80%。 |
| 冻结契约 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | **0 / PASS，15/15** | 不将此结果冒充 Task 证据 commit 内容核对。 |
| Task Canonical Evidence | Python 内存解析，hashlib 对工作区原始字节重算 SHA-256 | **0 / PASS，21/21** | 20 CANONICAL + 1 SUPPORTING，与 Task/index 对应路径匹配。 |
| Task commit 正文 | subprocess 原始 bytes 读取 `git show <commit>:<path>`，归一 CRLF/LF 比正文 | **0 / PASS，9/9 明确 commit** | 另 12 项 commit 为既有 `-`，只按 SHA pin 验证；不冒称 21 条都有明确 commit。 |
| 索引 SHA/结构 | 重算所有文件行 SHA，检查自身路径及控制字节 | **0 / PASS，23/23** | 自身 SHA 行 0；非法控制字符 0，允许正常 TAB/CR/LF。历史 Review 摘要 R-026 不影响文件 SHA。 |
| FINAL/PERF-MD 定位 | `563f248c7:<path>` 对比 HEAD blob/工作区正文 | **0 / PASS** | 正文匹配，内部完整代码 head 均为 aedc7251c。 |
| Review 完整性/历史字节 | 13 份正文/front matter、Git tree/history/blob 比较 | **PASS；摘要 R-026** | r10/r11 新增且内容/结论相符，旧 11 份相对 r11 被审 head 字节不变。 |
| 当前指针 | Task/index/STATUS/PLAN/checkpoint/handoff 当前段 | **PASS** | 已完成 r11 / 当前 r12 进行中 / canonical pending。 |
| 性能四处及 W-5 | JSON/摘要/Task 当前 AC6/index，交叉 rework-r8/handoff | **PASS** | 109.89/381.43/383.05，两次 361.52/381.43，W-5 PASS。 |
| 独立 Release 两次复测/mutation | 未另跑 Release，未修改源码 | **NOT_RUN** | 两次性能及 mutation 为既存证据，未冒充本轮独立复现。 |
| 原生多屏/DPI | 真机双屏/拔屏/换主屏/四档 DPI | **BLOCKED / D-1；NOT_RUN** | 无硬件矩阵/截图，不签发原生验收。 |

### 全量计数与 skip 直接原因

| 项目 | passed | failed | skipped |
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

共 **1195** 项，57=28+22+7。本轮 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 实测 **UNSET**；每一项 skip 的直接原因为该 sidecar 环境前置。Host `Support/HostFixture.cs:13–20`、CoreClient `Support/SidecarFixture.cs:28–35` 在检查其他 fixture 前返回 skip。App 7 项为 CreateChapterHostIntegration 2、RunControllerHostIntegration 3、WritePolicyUiIntegration 1、StartupSelfCheckUi 1；`RunControllerTests.cs` 的 RunFixture 与 `WritePolicyUiTests.cs` 的 attribute 同样先检查该变量。未将下游 book/其他夹具未设写成本轮直接原因，未设置变量伪造通过。

### 精确证据及性能

- EV-FEA07-FINAL：commit=`563f248c7`，工作区 SHA-256=`e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785`，blob=`a1caf2a111e4bfa9398c3b357f2aedfe688bc868`。
- EV-FEA07-PERF-MD：commit=`563f248c7`，工作区 SHA-256=`d6b87c5a99868d90619354c1f71f0616669f5f6ac92a0d39cee44a586f85b458`，blob=`b516b255e8942c4b7eb36c6fa40a897d82991e2f`。
- 原始工作区字节用于 SHA；Git 内容对比才归一 CRLF/LF。两文件内部被测 head 均为完整 `aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`；其余 7 条明确 commit 正文也匹配。
- Release JSON 20 样本重排，nearest-rank p50 为第 10 项 **109.89**，p95 为第 19 项 **381.43**，max **383.05**；4 次预热不混入测量。JSON `passed=true`，p95≤1000 ms。第 1 次 361.52 来自已存 rework-r8，未声称本轮新跑两次。
- 本轮全量包含 Debug 性能预算用例并通过；未用其结果替换 canonical Release JSON。事务总时长仅为 UI freeze 上限，不是原生冻结采样或规模压力测量。

## Architecture 与 Verification 结论

**Architecture：PASS（本轮增量及既有已审实现边界）。** 本批纯文档，代码/测试树与 aedc7251c 完全相同；模式快照、持门补偿、Promote 前屏障与排队回归机制保持。没有引入依赖、修改契约/schema，未破坏 Appearance 唯一写者、Host/IPC/Core/SQLite 分层或源文件/Lock/current/pinned 保护边界。没有重新签认未测的原生矩阵与数据安全全链。

**Verification：PASS（本轮指定机械与补全检查）；原生 D-1 保留。** build 0/0、1138/0/57、两生成器、治理 PASS(3)、契约 pins 15/15、Task SHA 21/21、index SHA 23/23、明确 commit 正文 9/9 均实跑/直接核对通过。r10 原文可读取，r11 原 finding 留存，R-025 闭环。历史 scope 摘要 R-026 为非阻塞文档准确性问题。

**Standards：已执行。** 当前写域及历史 Review 保留合规；未对未变代码强加 smell finding；记录 R-026 的历史摘要偏差。

**Spec：已执行。** r11 补全目标已达成，R-007/R-009/R-011 维持闭环，AC1–AC8 按上表保留实际边界；无本批 scope creep。

## 结论与复审

**Decision：`approved`（P0=0 / P1=0 / P2=1，R-026 非阻塞）。** 接受固定文档 head `527a7ec37` 对 r11 唯一 P2 的补全；代码 head 保持 aedc7251c。当前已完成 Review、Appointment、canonical 条件一致，没有需要继续返修生产代码或重开 R-007 的证据。本结论不等于 Task done、原生验收通过或 push 授权。

最小返修集仅为 **DSH 处置 R-026，修正当前索引的 scope 历史摘要**；不改 scope 原报告、既有运行日志或代码。该项不要求本轮再滚动 Appointment；DSH 可在集成处置中明确记录其修正和新文档 head。新 head 不自动继承本报告为对其全部内容的批准，仍须遵守固定点与集成验证纪律。

推荐下一步：**DSH 继续当前 FEA-07 的 P2 处置与集成验证/closeout 切片**。不释放新实现 Task，不自动启动 FEA-06-RESIDUAL-1。启动条件为接收本报告、确认代码树不漂移及记录非阻塞 finding disposition；按 handoff r11 §5 和 checkpoint §73 执行。允许范围仅 Task allowed_paths 内必要治理/证据文档；不需要共享接口/schema/依赖变更授权。交付集成验证日志、处置记录、AC residual/waiver、资源 closeout 与经核验的生命周期指针；未完成的 AC 不改成 PASS。资源清理不由本报告授权。

可直接转发给 DSH：

> 在 `G:\CODEX\New Manga`、main、common dir `.git` 继续 FEA-07 集成处置；base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`，本次被审文档 head=`527a7ec3797f39c24b92ee3e2062fa41777b7b32`，代码 head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。先 Reality Check，保留 dirty 与全部历史 Review 原字节。接收 `doc/reviews/FEA-07-impl-r12.md`：approved，0/0/1，R-025 已闭环；处置非阻塞 R-026，仅将 evidence-index 当前摘要的 scope-r1/r2 approved 改为 scope-r1 changes_requested 已处置、scope-r2 approved。只改 Task allowed_paths 内必要治理/证据文档，不改源码/测试/Core/schema/契约/依赖/生成物/用户数据，不进其他 worktree，不据此清理资源。按 handoff r11 §5 实跑 build、全量 test、TokenGen/ThemeGen --check、check.ps1、verify_pins.ps1，复核 Task 21 pin/索引 23 SHA/9 条明确 commit 正文及代码树无漂移，记录 shell、EXIT、skip/BLOCKED/NOT_RUN 至 `verification/FEA-07/integration-verification.log`。登记 AC5 原生 BLOCKED/D-1 与其余 PARTIAL 的正式 residual/waiver，完成资源 closeout 和 Closeout Record 后，依治理要求决定 Task 状态、canonical/resource complete、integration_commit 和 STATUS/PLAN 指针；不得直接把未达成 AC 写 MET。交付固定文档提交、disposition/Handoff 与集成证据。FEA-06-RESIDUAL-1 仍 proposed，须按端口依赖另行冻结释放，不自动启动。
