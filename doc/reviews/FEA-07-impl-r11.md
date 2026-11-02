---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r11；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: 91de6a345（文档/证据 head；代码 head aedc7251c）
code_head: aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0
decision: changes_requested
counts:
  P0: 0
  P1: 0
  P2: 1
---

# Review：FEA-07 第 11 轮实现复核（impl-r11）

## Reviewer 身份与来源

本报告由用户明确委派的 fresh Codex CLI 独立上下文执行；本会话未参与 FEA-07 的设计、实现或返修。Appointment 来源为本轮用户只读指令、`doc/handoffs/FEA-07-impl-r10.md` §4、Task reviewer 字段与 rolling checkpoint §71。项目 Lead / Architect / Integrator 为 DSH，本报告不行使任务关闭、集成或 push 权限。

Git、文档、实现调用链、指定实跑及证据核对均由本会话完成，没有派发子 agent。使用 `code-review` 技能；按仓库 Review 模板的本地覆盖，双轴并行不是强制项。Architecture、Verification、Standards、Spec 视角均为 **executed**，未虚构会话 ID 或辅助审查来源。

唯一主动交付写入为本报告。未修改源码、测试、Task、STATUS、PLAN、checkpoint、既有 Review、证据或用户数据；未 commit/push，未进入其他 worktree。指定 build/test/生成器命令产生通常的忽略构建输出、测试临时夹具及性能测试固有的 `%TEMP%/nm-fea07-performance-baseline.json`；未复制回 canonical 证据。未启动连接真实用户数据的产品，未主动写真实 `%APPDATA%`；未执行源码 mutation。

## 范围与 Reality Check

- 仓库为 `G:\CODEX\New Manga`，branch=`main`，common directory=`.git`。起始及落盘前 HEAD 均为 **`91de6a3454fb6ad715fa160c8db7db73e42e75b3`**；落盘前 `git status --short` 为空，固定 base 可解析。
- 已实跑指定五条 Git 命令：`git rev-parse HEAD`、`git status --short`、`git log --oneline -8`、`git diff --stat cbfb7bbc9..HEAD`、`git diff --name-only cbfb7bbc9..HEAD`。累计 **92 files changed / 9557 insertions(+) / 562 deletions(-)**，按 Task `allowed_paths` 匹配 **92/92，越界 0**；three-dot diff 统计相同。
- `aedc7251c..HEAD` 仅 **12 个 docs/evidence 文件**，无源码/测试漂移。`git diff --quiet aedc7251c HEAD -- apps/desktop-avalonia` 为 **exit 0**；两端 `apps/desktop-avalonia` 树对象均为 `f2b4459e77394721650d752cb91fed3f7a6518b2`。
- 本轮 `ebda36be9..91de6a345` 仅 **6 个文档文件 / +78/-10**：PLAN、STATUS、checkpoint、handoff r10、Task、evidence-index；未改既有证据正文、源码、测试、契约、schema、依赖或生成物。
- 已读 Task、STATUS、PLAN、r9 Review、handoff r10、final log、index、rework-r8 log；按当前引用补读 checkpoint 当前段、性能摘要/Release JSON、AD-002 当前边界及 AD-003 修订提示、协作协议 §4/§5.1、Review 模板及相关实现/测试。未扫描无关 Task 或 verification 历史目录。
- **指定的 r10 Review 无法读取：文件不存在。** `Get-Content` 报路径不存在；`Test-Path` 为 False；`git ls-tree HEAD doc/reviews/FEA-07-impl-r10.md` 无条目；`git cat-file -e HEAD:doc/reviews/FEA-07-impl-r10.md` 为 **exit 128**；`git log --all --format=%h -- doc/reviews/FEA-07-impl-r10.md` 无记录。没有把 Task/handoff 对该报告的转述当作已读取原文。此为 R-025。

实际 `git log --oneline -8`（exit 0）：

```text
91de6a345 docs(fea-07): impl-r10 R-007 最终处置（已完成 Review 与当前 Appointment 分离）+ 索引/指针（code head aedc7251c；全量 1138/0/57）
ebda36be9 docs(fea-07): impl-r9 文档一致性处置（R-007/R-009/R-011）+ 证据索引/指针（code head aedc7251c；全量 1138/0/57）
563f248c7 docs(fea-07): impl-r8 处置 + mutation 判别证据/索引 + delivery 固定（head aedc7251c；全量 1138/0/57）
aedc7251c fix(fea-07): r8 返修（R-023 屏障前移至 Promote 前 + mutation 判别证据 / R-007 文案）；全量 1138/0/57
b6b63574d docs(fea-07): impl-r7 处置 + 返修证据/索引 + delivery/生命周期固定（head 462141f57；全量 1138/0/57）
462141f57 fix(fea-07): r7 返修（R-022 取消路径窗口模式补偿 / R-024 门内快照防陈旧恢复 / R-023 判别性测试）；全量 1138/0/57
226e47c51 docs(fea-07): impl-r6 approved + R-022 修复处置/证据/索引（head 5a495f80a；全量 1135/0/57）
5a495f80a fix(fea-07): r6 R-022 失败切换恢复原窗口全屏模式（含回归测试）；全量 1135/0/57
```

**源码及测试行号均以 `aedc7251c` 为准**。下文源码简称相对于 `apps/desktop-avalonia/src/NewManga.App/`，App 测试相对于 `apps/desktop-avalonia/tests/NewManga.App.Tests/`。新增文档处置位于 `91de6a345`，以字段、表行和章节定位，不套用代码 head 中旧文档的行号。

## r10 findings 闭环表

r10 原报告缺失，以下 r10 背景仅来自当前 Task/handoff 的明确转述；r11 Verdict 则来自本轮直接核对，不声称已复核 r10 原文。

| ID | 当前文档转述的 r10 状态 | r11 Verdict | 本轮依据 |
|---|---|---|---|
| R-007 | 唯一 P2；最新已完成 Review 与当前 Appointment 文案冲突 | **原文案冲突已消除；最终证据链尚缺 r10 原报告，另计 R-025** | Task reviewer、索引、STATUS、PLAN、checkpoint §70/§71、handoff r10 均将 r11 表达为当前进行中的 Appointment；Task/handoff/STATUS/checkpoint 将 r10 表达为已完成并已处置的 Review。无将 r11 实际状态写成“待派”的条目；出现“待派”的当前说明均是否定旧口径。 |
| R-009 | 确认闭环 | **维持闭环** | AC6 当前验收行为 109.89/381.43/383.05 ms，两次 361.52/381.43；与 Release JSON、摘要、索引、rework-r8、handoff 一致；UI freeze 上限及规模负载仍为 PARTIAL。 |
| R-011 | 确认闭环 | **这两条证据定位修正维持闭环** | FINAL/PERF-MD 均定位 `563f248c7`；按 commit 取正文与当前文件归一行尾后相同，内部被测 code head 仍为 `aedc7251c`。r10 Review 本身缺失另归 R-025，不重开这两条已修正 pin。 |

R-007 状态语义的具体交叉核对：

| 当前载体 | 最新已完成 Review | 当前 Appointment / canonical |
|---|---|---|
| Task reviewer、impl-r10 处置节 | impl-r10，changes_requested，P0=0/P1=0/P2=1，已处置 | impl-r11；fresh Codex CLI；来源 handoff r10 §4；复核进行中；canonical=pending，r11 approved 并集成后置 complete |
| evidence-index 复核行 | 历史 r10 changes_requested 已处置；不是 r11 已批准 | impl-r11 复核中；代码 head 保持 aedc7251c |
| STATUS 当前 Task / 下一步 | 最新已完成 impl-r10，P2 已处置 | 当前 Appointment=impl-r11，复核进行中；仍 in_progress |
| PLAN 当前 FEA-07 行 / 当前 DAG | r3–r10 返修 done，未声称 Review approved | Appointment=impl-r11 复核中；FEA-07 仍 in_progress |
| checkpoint §70/§71 | impl-r10 changes_requested P2=1，已处置 | r11 fresh 只读；本批文档 head；代码 aedc7251c；canonical pending |
| handoff r10 §1/§2/§4 | impl-r10 changes_requested P2=1，已处置 | r11 fresh Codex CLI；文档 head=本 handoff 所在提交，即 91de6a345；代码 aedc7251c；复核进行中 |

这些当前描述没有新的轮次/进行状态冲突。旧 checkpoint 的历史派发和旧轮次 approved 后计划由 §70/§71 的当前段接替，不作为当前 Appointment。问题在于这些描述共同指向了一个未入库的已完成 Review，不能仅靠文案一致签认完整闭环。

更早 findings 的状态及边界：

| ID | r11 状态 | 核对依据 |
|---|---|---|
| R-001、R-010 | 维持已记录实现闭环与 AC1 PARTIAL | 组合根缓存内容树；真实 staging/Loaded/帧门禁与状态保留测试纳入本轮全量；无代码漂移。 |
| R-002 | 维持闭环及 AC2 边界 | 可见/staging/cache 退出聚合、生产 Theme Studio draft 和隐藏树关闭阻断回归；未扩张双窗验收。 |
| R-003、R-004、R-005 | 维持有边界闭环 | 启动恢复、planner 单源、坏 JSON、memento/拓扑/manifest 回归；原生初始化和多屏矩阵未升级为 PASS。 |
| R-006、R-008、R-012 | 维持闭环 | 临时根夹具、92/92 allowed_paths、两生成器本轮实跑通过。 |
| R-013、R-014、R-015 | 维持闭环 | 同门串行与补偿、memento、journal finalize 故障回滚测试通过；实现未变。 |
| R-016 | 索引结构维持闭环 | 23 行 SHA 匹配；无自身 SHA 行、无非法控制字符。 |
| R-017、R-018、R-019 | 维持闭环 | 外观/draft 同步、Loaded 解绑、staging 输入隔离回归纳入全量，未改其实现。 |
| R-020、R-021 | 维持闭环 | 稳定窗口全屏桥接与重复通知相关回归通过。 |
| R-022、R-024 | 维持实现闭环 | `FrontendHostCoordinator.cs:97,102,114,190,198,205–210`：快照在同门且 reject/no-op 后；失败/取消 Dispose 后才放门；成功 Commit；`PresentationWindow.cs:294–343` 恢复 WindowState 与旧 reader 模式。 |
| R-023 | 核心判别力维持闭环 | `FrontendHostCoordinator.cs:151–155` 屏障在 Promote 前；`PresentationWindowTests.cs:448–491` 验证旧全屏状态、B 排队、A 成功/B 拒绝及最终 Normal/journal 清除。独立 mutation 未跑，不扩大单用例 settings/RolledBack 直接断言覆盖。 |

本轮 `ebda36be9..HEAD` 未改既有 Review。Task 中 r9 处置以前的 **17 个历史实施/返修章节正文与 ebda36be9 逐段字节一致**（按 Git LF 归一行尾比较）；r7 实施记录也与 `563f248c7` 相同。没有为同步当前 AC6 而回写历史性能数值。

## AC 逐条 Verdict

| AC | r11 Verdict | 依据与保留边界 |
|---|---|---|
| AC1 | **PARTIAL** | 真实树 100 次切换、状态保留、真实门禁、失败/取消补偿和排队拒绝回归通过；原生 IME、真库 DB/current/pinned/Lock/source/candidate 零变化、ACK 重连及真实 Run/Intent 未补验。 |
| AC2 | **PARTIAL** | Broker/退出聚合和真实 draft 关闭保护回归通过；真实双窗归属与 Session/Region 单写 owner 集成待补。 |
| AC3 | **PARTIAL** | journal/启动恢复、并发与 finalize 补偿回归通过；暂停期间保护状态变化及真实跨进程崩溃注入待补。 |
| AC4 | **PARTIAL** | planner、坏 JSON、fallback/CLI/legacy 矩阵通过；真实 App 初始化、坏包/scale 原生矩阵待补。 |
| AC5 | **原生矩阵 BLOCKED / D-1；逻辑 PARTIAL** | 拓扑/memento/PerMonitorV2/全屏 headless 回归通过；原生双屏/拔屏/换主屏及 100/125/150/200% DPI 矩阵 NOT_RUN，无硬件/截图，不以 headless 代替。 |
| AC6 | **PARTIAL；W-5 PASS** | 当前数值一致；20 样本重算 p50=109.89、p95=381.43、max=383.05 ms；两次 p95=361.52/381.43≤1000 ms；真实 UI freeze、规模负载与真机指标待补。 |
| AC7 | **MET（冻结机械回归范围）** | build 0/0、全量 1138/0/57、启动/依赖/TFM 门禁、两生成器通过；相对 1034/0/57 基线增加 104 passed，fail/skip 不增。 |
| AC8 | **PARTIAL；Review 来源缺口待补** | 21 项 Task SHA、23 行 index、已填写证据 commit 正文及隔离夹具通过；R-025 待处置；原生矩阵/截图继续 D-1。 |

Task 仍 in_progress，本报告不把已有 PARTIAL 标记或勾选解释成全部 AC 已满足，也不签发 done。残余/waiver 与 closeout 仍由 DSH 正式登记。

## Findings

本轮 **P0=0 / P1=0 / P2=1**；无新增生产代码 finding。R-007 原状态措辞不再重复计数。

| ID | 级别 | 文件/定位 | 触发与影响 | 复现证据 | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R-025 | **P2** | `doc/tasks/FEA-07.md` 的 reviewer 字段、impl-r10 处置节；`doc/handoffs/FEA-07-impl-r10.md` §1/§2；指向缺失的 `doc/reviews/FEA-07-impl-r10.md` | 当前权威描述将 r10 声明为最新已完成独立 Review，并转述其 changes_requested/P2=1 与 R-009/R-011 结论，但被审 HEAD 和工作区均无该报告。恢复者无法核验 r10 的 reviewer 来源、精确 head、原 findings 与判定；故不能确认完整的“已完成 Review→处置→r11”审查链。 | `Test-Path`=False；`git ls-tree HEAD <path>` 无条目；`git cat-file -e HEAD:<path>` exit 128；`git log --all --format=%h -- <path>` 无记录。治理 PASS 不补足原始报告。 | DSH 从实际 r10 审查产物恢复原始报告并原字节纳入后续固定文档提交，核验其身份/被审 head/decision/counts 与当前转述一致。不得用 Owner 摘要重造 Reviewer 报告；若原件不可恢复，应明确登记缺口并由 fresh reviewer 重新建立可核验审查来源。保留本报告及既有历史文件。 | **open** |

依据：协作协议 §4.1 要求当前 Review 绑定精确 base/reviewed_head；§5 要求 Agent 会话、仓外临时路径或未提交状态不能成为唯一证据；Review 模板要求 reviewer 来源与实际审查范围。缺口仅涉及本次文档交付/审查追溯，未发现代码漂移或新增运行故障，故定为 P2；仍需最小文档返修后再签认交付。

## 证据与治理核对表

本轮环境：2026-11-02，Windows NT **10.0.26300.0**，PowerShell **7.6.8**，SDK **10.0.401**，测试目标 **net9.0**，已安装 runtime **9.0.11**。下表为本会话实际执行，HEAD=`91de6a345`。EXIT 与关键输出记录于本报告，未覆盖原 verification 日志。

| 检查 | 实际命令/方法 | EXIT / Verdict | 结果与边界 |
|---|---|---|---|
| Git 固定点/写域 | 前述五条 Git 命令、branch/common-dir、逐路径 glob | **0 / PASS** | main/.git；起始 clean；92/92 合法；代码树相同。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **0 / PASS** | **0 warnings / 0 errors**；6.46s。 |
| 全量测试 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **0 / PASS** | **1138 passed / 0 failed / 57 skipped**；App 2m52s。 |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | **0 / PASS** | **292 rows**；every generated artifact matches frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | **0 / PASS** | generated theme artifacts match frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | **0 / PASS，3 warnings** | 15 current documents；10 个非终态 Task；STATUS 3183 bytes/29 lines、PLAN 4803 bytes/64 lines 达预算 80%。 |
| 冻结契约 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | **0 / PASS，15/15** | 与 Task 证据 pin 分开核对。 |
| Task SHA | 解析 Canonical Evidence，以 Python hashlib 对原始工作区字节计算 SHA-256，并与 index 三方比较 | **0 / PASS，21/21** | 20 CANONICAL + 1 SUPPORTING；非只凭 checker PASS。 |
| Task commit 正文 | 逐条 `git show <commit>:<path>` 与当前正文比较 | **0 / PASS，9/9 已填写 commit** | 另 12 条沿用 `-`/SHA pin；未臆造 commit。原始字节用于 SHA，CRLF→LF 仅用于 Git 正文对比。 |
| evidence-index | 对所有文件行重算 SHA；查自身路径与非法控制字节 | **0 / PASS，23/23** | 无 SHA 不匹配；无自身 SHA 行；非法控制字符 0（允许正常 TAB/CR/LF）。 |
| FINAL/PERF-MD 定位 | 比较 `563f248c7:<path>` 与 HEAD blob 及当前正文 | **0 / PASS** | 两项 commit 均为 563f248c7；对应 blob 与 HEAD 相同；内部 code head 仍为 aedc7251c。 |
| 性能四处一致性 | JSON/摘要/Task 当前 AC6/index，交叉核对 rework-r8/handoff | **0 / PASS，W-5 PASS** | p50 109.89 / p95 381.43 / max 383.05；两次 361.52/381.43 ms，未混用历史 r7 值。 |
| 历史实施记录 | 按章节比较 Task 正文；检查 Review diff | **0 / PASS** | 本批以前 17 个实施/返修章节正文未变；已有 Review 未修改。 |
| Appointment 语义 | Task/index/STATUS/PLAN/checkpoint/handoff 当前段交叉核对 | **文案 PASS；来源 FAIL/R-025** | 无 r11 实际“待派”状态；r10 报告缺失，不能把引用的存在当作报告的存在。 |
| r10 原报告 | `git cat-file -e HEAD:doc/reviews/FEA-07-impl-r10.md` | **128 / FAIL，R-025** | 路径不存在，工作区也不存在；原文读取 NOT_AVAILABLE。 |
| 独立 mutation | 未修改源码/测试 | **NOT_RUN** | 仅核对 rework-r8 已存摘要、当前测试与反事实机制，不声称本轮独立反跑。 |
| 原生多屏/DPI | 真机双屏/拔屏/换主屏/100/125/150/200% DPI | **BLOCKED / D-1；NOT_RUN** | 无硬件矩阵与截图，不签发原生验收。 |

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

总数 **1195**；57=28+22+7。本轮实测 `NEWMANGA_CORECLIENT_SIDECAR_DIR` **UNSET**。Host `Support/HostFixture.cs:13–20` 与 CoreClient `Support/SidecarFixture.cs:28–35` 在后续 fixture 检查之前即返回 skip。App 7 项为 RunControllerHostIntegration 3、CreateChapterHostIntegration 2、StartupSelfCheckUi 1、WritePolicyUiIntegration 1，直接前置同为 sidecar env。没有将其他下游夹具未设当作本轮直接原因。

### 证据定位与性能判别

- `EV-FEA07-FINAL`：commit=`563f248c7`，工作区 SHA-256=`e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785`，blob=`a1caf2a111e4bfa9398c3b357f2aedfe688bc868`。
- `EV-FEA07-PERF-MD`：commit=`563f248c7`，工作区 SHA-256=`d6b87c5a99868d90619354c1f71f0616669f5f6ac92a0d39cee44a586f85b458`，blob=`b516b255e8942c4b7eb36c6fa40a897d82991e2f`。
- 两文件在 `563f248c7` 与 `91de6a345` 的 blob ID 分别相同；内部完整被测代码 head 均为 `aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。其余 7 条已填写 commit 的证据正文也逐项匹配；未将工作区 CRLF SHA 与 Git LF blob SHA 的差异误判为内容漂移。
- Release JSON 的 20 样本重新排序：nearest-rank p50 取第 10 项 **109.89**、p95 取第 19 项 **381.43**、max **383.05**；4 次预热不混入测量。JSON `passed=true` 与 p95≤1000 ms 一致。第 1 次复测 361.52 来自 rework-r8 的已有记录；本轮未另跑 Release 性能，不冒充新的两次复测。
- 本轮全量包含 Debug 性能预算断言并通过，未据此改写 canonical Release JSON。事务总时长依然只是 UI freeze 上限；规模负载/真机指标仍保留 PARTIAL。

## Architecture 与 Verification 结论

**Architecture：PASS（本轮增量与已记录实现边界）。** `aedc7251c..HEAD` 没有代码/测试变化；App 内容缓存、同门窗口模式事务、appearance 唯一写者、Host/Core/SQLite 边界未被本次文档改动破坏。对照稳定窗口、快照/补偿、staging 屏障及 journal 恢复调用链，未发现新增生产回归。未引入新依赖或触及源文件/Lock/current/pinned Revision 数据面。

**Standards：文档追溯不完整，R-025。** 原始 Review 未入库而当前记录已声称其完成，不满足可恢复的审查来源要求；不对未变代码硬加 smell finding。

**Spec：R-007 文案目标、R-009 数值和 R-011 pin 定位目标均已实现；原始 r10 Review 核验要求未满足。** AC1–AC8 保留上表边界，特别是 AC5 原生 BLOCKED/D-1。

**Verification：指定机械检查均实跑通过，Review 来源链未通过。** build 0/0、全量 1138/0/57、两生成物 byte-for-byte up-to-date、治理 PASS(3)、契约 pins 15/15、Task SHA 21/21、index SHA 23/23、已填写证据 commit 正文 9/9 均成立；这些结果不能替代缺失的 r10 审查原文。

## 结论与复审

**Decision：`changes_requested`（P0=0 / P1=0 / P2=1）。** 本轮没有要求继续滚动修改 Appointment 文案，也没有要求修改生产代码。R-007 的措辞冲突已修复，但固定文档 head `91de6a345` 缺少其声明的最新已完成 r10 Review，因此不能签认完整审查交付。

最小返修集：

1. DSH 找回实际 r10 原始审查报告并按原字节入库 `doc/reviews/FEA-07-impl-r10.md`；确认 reviewer/source、base、被审文档 `ebda36be9`、代码 `aedc7251c`、decision/counts/findings 与当前记录相符。不从处置摘要伪造报告，也不覆盖本轮 r11 文件。
2. 若原件不可恢复，显式记录证据缺失及来源边界，Appointment fresh 只读审查建立真实可核验来源；不能继续把不可核验的转述当作已归档报告。保持当前状态语义分离，不再为消除文案冲突反复轮转“待派”。
3. 固定新文档 head，核验 r10 文件在工作区和该 commit 中均存在、正文与来源一致；执行治理、冻结 pins、21 项 Task/23 行 index SHA 和 9 条已填写 commit 正文检查，确认源码/测试树仍为 aedc7251c；由 fresh reviewer 核验 R-025 处置。无代码变化时可复用本轮运行证据，DSH 的正式集成验证仍须另记。
4. 保留 canonical=pending、resource_closeout=pending、AC5 原生 BLOCKED/D-1 与其余 PARTIAL；待复核、集成验证、残余处置和资源 closeout 完成后由 DSH 决定生命周期，不因本报告自动启动 FEA-06-RESIDUAL-1。

推荐下一步为 **DSH 继续当前 FEA-07 的审查证据补全**，无需释放新实现 Task。Recovery point：`G:\CODEX\New Manga`、main、common dir `.git`；base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`；当前文档 head=`91de6a3454fb6ad715fa160c8db7db73e42e75b3`；代码 head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。范围限 Task allowed_paths 内必要 Review/处置/Handoff 文档，不需共享接口/schema/依赖变更授权；交付固定文档 commit、真实来源和处置记录，完成上述核验后再申请独立复核。

可直接转发给 DSH：

> 在 `G:\CODEX\New Manga`、main、common dir `.git` 继续 FEA-07；base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`，文档 head=`91de6a3454fb6ad715fa160c8db7db73e42e75b3`，代码 head=`aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`。先 Reality Check 并保留 dirty 与既有审查原字节。按 `doc/reviews/FEA-07-impl-r11.md` 处置唯一 P2 R-025：当前 Task/handoff 声称 r10 Review 已完成，但 `doc/reviews/FEA-07-impl-r10.md` 不在工作区或 HEAD。找回真实 r10 原件并原字节入库，核验其身份、来源、base/head、decision/counts/findings；不得从 Owner 摘要重建 Reviewer 报告。原件不可恢复时显式记录缺口并 Appointment fresh 只读核验来源。只改 Task allowed_paths 内必要文档，保留本报告，不改源码/测试/Core/schema/契约/依赖/用户数据，不进入其他 worktree。交付固定文档 commit、disposition/Handoff 与来源核验，执行 check.ps1、verify_pins.ps1、21 项 Task SHA/23 行 index SHA、9 条已填写证据 commit 正文及代码树无漂移检查，记录 EXIT 与 BLOCKED/NOT_RUN。当前代码不变则复用 r11 build 0/0、1138/0/57 与两生成器通过证据；新 head 交 fresh reviewer 核验 R-025，后续由 DSH 另行集成验证和 closeout。保持 canonical pending、AC5 原生 BLOCKED/D-1 和其余 PARTIAL，不自动释放 FEA-06-RESIDUAL-1。
