---
document_id: FEA-00-dsh-r8
kind: independent_review
task_id: FEA-00
round: 8
reviewer: fea-reviewer-r8
reviewer_kind: subagent
reviewer_source: "Agent Teams fresh context task-6（DSH Lead 派发的独立上下文 teammate；未参与方案撰写与 r4 修订，未参与 r1/r2/r6/r6b/r6c/r7 任一复核，未参与 AD-003 / ADJ-001 撰写或任何实现）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_document: doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md
reviewed_head: 74a772167
reviewed_head_full: 74a772167f038bc079339aa4b4e4273160d4150c
reviewed_blob_sha256: 8895aebea3ea98f22398696e224766d197077224eb7790f289cd1f9f4231d54c
reviewed_document_lines: 1052
repository: G:/CODEX/New Manga
source_branch: main
appointment: doc/reviews/FEA-00-dsh-r8-appointment.md
predecessor: FEA-00-dsh-r7（changes_requested：0 P0 / 2 P1 / 6 P2）
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 9
captured_at: 2026-11-01T02:07:32+08:00
captured_by: fea-reviewer-r8
---

# 独立 Review：FEA-00 可切换前端架构方案（第 8 轮 / r4 字节）

**本报告不是** ADR、冻结契约、Task 释放、实现验收或集成批准，也不构成对 AD-003 / ADJ-001 / `FEA-01_CONTRACT_DRAFT` 的批准。它固定被审文档的字节与仓库 head，给出 r7 findings 的逐条处置判定、findings 与 NOT_RUN。`verdict: approved` 只表示**方案文本层面**无 P0/P1 阻塞项；9 条 P2 仍应由 DSH 处置。

## 0. 性质与定位

| 项 | 值 |
|---|---|
| 被审对象 | `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`（已跟踪 PROPOSAL，非 ADR / 冻结契约 / Task） |
| 被审提交 | `74a772167f038bc079339aa4b4e4273160d4150c`（`docs(fea): r4 修订处置 FEA-00 r7`），`git show --stat` = **1 file changed, 83 insertions(+), 66 deletions(-)**，只改本方案 |
| 内容指纹 | LF blob SHA-256 `8895aebea3ea98f22398696e224766d197077224eb7790f289cd1f9f4231d54c`，与 Appointment / Task 给定值**逐字节一致**；工作树文件 `Get-FileHash` 同值，`CRLF=0`、`LF=1052` |
| 本轮性质 | 静态文档审查（只读仓库 + 只写本报告）。**不运行**构建、测试、应用、迁移、原型、Mermaid 渲染器 |
| 结论适用范围 | 仅对 `reviewed_head` 与 `reviewed_blob_sha256` 这对字节有效；任一变化即失效，须重算并重新 Appointment |
| 写权 | 唯一写入本文件；未修改任何 tracked 文件、未 `git add/commit/checkout/stash`、未改方案/契约/Task/STATUS/PLAN/AGENTS/AD-002/AD-003/ADJ-001 |

## 1. 基线与漂移（本轮实测）

| 项 | 方案自述 / 期望 | 本轮实测 | 判定 |
|---|---|---|---|
| 仓库 / 分支 | `G:/CODEX/New Manga`、`main` | 同（Git common dir = 仓库内 `.git`） | ✅ |
| 方案自述「指定复审基线」 | `main@29d06c462`（L11、L777、L831） | 实际 `HEAD` = `74a772167`（即被审提交）；`29d06c462..74a772167` 共 **7 个提交**，其中 `apps/` **3 个文件**有改动（`ReaderOverlayViewModel.cs` +45/−7、测试 `FakeHostController.cs` +24/−4、`LibraryProgressRefreshTests.cs` +40/−0） | 方案已如实登记「修订期间 main 并发推进到 `bb7cbda1d`」，**事实结论不受影响**；但提交后基线陈述自动过期（见 R8-01） |
| 方案自述「初稿基线→HEAD，`apps/` 有 4 个文件变化」 | 4 | `git diff --numstat 1180cdba..74a772167 -- apps/` = **4 个文件**（另含 `LibraryViewModel.cs`） | ✅ **核对无误**（R7-06 要求的诚实登记已落地） |
| 被审文档行数 | —— | 1052 | 记录 |
| 治理检查器 | 方案 L29 / L826 引用 | 本轮只读运行 `tools/governance/check.ps1` → `PASS (3 warnings)`、`EXIT=0`、`scope 15 current documents`；第 3 条 warning 为 `doc/STATUS.md` 达预算 80%（r7 记 2 条，属其后并发增长） | ✅ PASS 只证明机械条件 |
| 权威层文档 | AD-003 / ADJ-001 | 均为已入库权威文件；状态分别为 `ACCEPTED_ARCHITECTURE_AMENDMENT` 与 `FROZEN_SEMANTICS / PENDING_IMPLEMENTATION / PROTOCOL_CHANGE_PROPOSED` | 见 §3 R7-01/R7-02 |

**工作区并发登记（不得归因于本报告）**：审查开始与结束 `HEAD` 均未变；`git status --porcelain` 仅两项——` M doc/handoffs/NIGHT-SHIFT-2026-11-01.md`（**其他并行 agent** 的 8 行新增，本报告作者未读、未改）与 `?? doc/reviews/FEA-00-dsh-r8-appointment.md`（本轮 Appointment，未跟踪）。

## 2. 结论

**`approved`（可交 DSH 处置；0 项 P0、0 项 P1、9 项 P2）。**

按 Appointment 与 `doc/09_COLLABORATION.md`「P0/P1 未解决不得 approved」：r7 的 2 项 P1（R7-01 权威层不同步、R7-02 删除流程未映射 PD-01–PD-10）在本字节上**均已实质处置**，r7 的 6 项 P2 **全部有处置**，本轮未发现新的 P0/P1；残留问题均为精度、口径与自指时效类 P2，不阻塞「方案转契约冻结」的下一道 Gate，但建议 DSH 在冻结 C-01…C-12 前顺手修掉 R8-01/R8-02（它们直接影响下一轮 Appointment 模板）。

三层判断：

1. **R7-01（P1）已解决**：方案已把「待权威记录 / 需 DSH 裁定」改写成「AD-003 已记录（`G-ADR: SATISFIED`）+ 契约待冻结（`G-CONTRACT: OPEN`）」，D01/D07 的处置对象已更新，`check.ps1 PASS` 的机械边界与断言面出处均已写明。
2. **R7-02（P1）已解决**：§9.1 新增 5 步 C 流程并把 **PD-01…PD-10 全部编号**落到位置（只读预览 `PreviewPermanentDeleteBooks`、`inventory_digest` 绑定、确认前零变化、同事务全有/全无、失败整体回滚、原文件独立 D 流程、pending 仅显式重试），§15.6 FEA-12-CORE 与 §15.7 §4 行同步，「F-02 裁定」占位已删除。
3. **未引入新的架构级矛盾或与冻结契约的冲突**；`approved` 不等于契约冻结、不等于 Task 释放、不等于承认 AD-003/ADJ-001 已获独立批准。

## 3. r7 findings 逐条处置判定

口径：**已处置** = 文本层已回应且可在本字节定位；**部分处置** = 方向正确但仍有可复核残留（残留另计 P2）；**未处置** = 无对应修订。

| ID | r7 级别 | 本轮判定 | 证据（本字节定位） |
|---|---|---|---|
| **R7-01** | P1 | ✅ **已处置** | L25→L29 改为「**[用户决定，已记录于 AD-003]**」并写明 `ACCEPTED_ARCHITECTURE_AMENDMENT` / `G-ADR: SATISFIED` / `G-CONTRACT: OPEN`；L29 增「`check.ps1 PASS` 只证明机械条件…断言面见 `tools/governance/check.ps1:261-275`，其自身 Review 为 `FEA-00-dsh-r6c`（`approved`）」（本轮逐项复核：`check.ps1:261-275` 确为双哨兵 + bounded scope 注释块；r6c front matter `decision: approved`）；§15.1 标题改为「两个已决策项 + 剩余契约冻结」、L835/L836 两条重写为「已记录/已冻结 + 剩余契约冻结」；L477/L516/L607/L609 同步；D01（L764）改为「AD-003 已记录；冻结 C-01b（存储契约）与下游五项反转清单」、D07（L770）改为「先核对 ADJ-001 §5/§6.1，再冻结 `M2-C1 §5.11` 字段与错误码（`C-04b`）」；全文 `待权威记录 / 需 DSH 裁定 / ADR 正式记录` **0 命中** |
| **R7-02** | P1 | ✅ **已处置** | §9.1 L489–L497 新增「显式彻底删除（C 流程；ADJ-001 PD-01–PD-10）」5 步：①Core 只读 `PreviewPermanentDeleteBooks` + 逐项清单 + UI 不自行估算（PD-01/PD-03）；②`inventory_digest` 绑定 + 确认前零变化 + 拒绝并重新预览（PD-02/PD-04）；③同事务删除内容与保护、失败整体回滚、批量 DB 全有/全无、清理逐项报告（PD-05/PD-06/PD-09）；④不触原件、原文件走独立 D 流程（PD-08）；⑤自动清理/软删保留 PD-01 保护、pending 仅显式重试（PD-07/PD-10）。**PD-01…PD-10 十个编号全部出现**（本轮 grep 复核）。§9.2 L507–L516 重写为 D 流程「分别发起、分别确认」，与 AD-003 §3.7 五项动作一致。§15.6 FEA-12-CORE（L933）出口列已改为预览/摘要/零变化/回滚/不触原件 + 「按 ADJ-001 PD-01–PD-10 实现，D07 冻结 `C-04b` 后接线」；§15.7 §4 行（L948）补 PD AC；§16.4（L1043）同步；「F-02 裁定」占位 **0 命中** |
| **R7-03** | P2 | ✅ 已处置（残留 R8-06） | §12.1 表头改「建议 Owner / Review」；15 行候选写明「DSH Appointment 登记的独立上下文 Review」（其中 14 行原文为「独立上下文 Review（按 DSH Appointment 登记）」L638–L652，FEA-00 行为「Review 由 DSH Appointment 登记的独立上下文执行」L637；FEA-14-* 为「不得由实现者所在会话/实例执行」）；新增 L656 口径段「Review 只要求上下文独立，不要求 Reviewer 与作者/Owner 是不同 Agent 角色…须记录审查者身份和来源」；§13.2 末段、§14.2、§15 首段、§16.1 同步。全文 `ZCode 独审 / 未参与实现的 / reviewer_unavailable / 待有效` 仅剩 §15.6 FEA-00 行「席位状态」1 处 |
| **R7-04** | P2 | ✅ 已处置（残留 R8-01/R8-02） | §13.3 整体重写为「修订 → 新 SHA-256 重新 Appointment → 逐条冻结 C-01…C-12 → 冻结 FEA-01 → 释放 Task」的流程，删除「交 DSH 协调 r2 复审」与轮次编号；可转发指令改为「逐条核对 R7-01–R7-08 处置、AD-003/ADJ-001 一致性及 C-01…C-12 的状态/待冻结边界…Review 不构成契约冻结或实现释放」，不再要求重做 r1 式十项问题。**但新指令仍含两处自指/口径问题**（R8-01、R8-02） |
| **R7-05** | P2 | ✅ **已处置（无残留）** | §16 首段删除 `session-5ba272c1-…` 与 `a66dc75c…`，改为「DSH 技术复核见 `doc/reviews/FEA-00-dsh-r2-technical-recheck.md`；会话级口头复核不作为审查证据」；§16.6 删除 `759f940f…` 与「DSH r3 确认」，改为「不得据此声称 F-08/F-11/F-19/F-25/F-38/F-39 已获独立确认」。全文 `session-[0-9a-f]{8} / a66dc75c / 759f940f` **0 命中** |
| **R7-06** | P2 | ✅ 已处置（残留 R8-05/R8-08） | L11 改为「指定复审基线 `main@29d06c462`…本轮修订期间 main 并发推进到 HEAD `bb7cbda1d`…本文代码行号是原始核查时的定位线索，不代表已对当前基线逐项重核；从初稿代码基线到当前 HEAD，`apps/` 下有 4 个文件变化，相关引用须在实现 Task 冻结前重核」（本轮**实测 4 个文件，核对无误**）；§14.3 L820 标注「首次交付的文档检查」、L826 增 r7 只读记录并把 55/13 明确标为历史数字、检查范围 15 documents（本轮实测同为 15）。残留：F09 锚点已漂移（R8-05）、56/56 只对旧字节成立（R8-08） |
| **R7-07** | P2 | ✅ **已处置（无残留）** | §15.2 新增「**C-10 交互契约（FEA-01 附件，待冻结）**：①手势优先级与移动阈值；②可编辑态判定及其对切换/写入的阻断条件；③ draft owner 归属与跨窗口共享规则…当前不视为已定义或已实现」；§15.6 FEA-01 行补「C-10 交互契约附件」；§15.7 §6 行补「FEA-01 待冻结手势优先级与移动阈值、可编辑态判定、draft owner 归属」 |
| **R7-08** | P2 | ✅ **已处置（无残留）** | §4.1 L144、D02（L765）、§15.2 三处口径现已**统一**为同一枚举「§1.1/§1.2/§2.2/§2.3/§2.4/§3/§4/§6.1/§6.3」；§15.2 表恰为这 9 行 |

**统计**：2 P1 → **2 已处置**；6 P2 → **6 已处置**（其中 4 项带 P2 级残留，见 §4）。

## 4. Findings

严重度口径沿用 r1/r7：**P0 = 阻塞采纳**；**P1 = 进入实现前必须处置**；**P2 = 精度、归属、边界与可验证性改进项**。本轮 **P0 = 0、P1 = 0**。

### 4.1 P0（阻塞采纳）

**无。** 本轮逐条核对：①未发现与 AD-003 / ADJ-001 / `M2-C1 §5.11` / AD-002 冻结语义**相反**的陈述；②未发现把**未冻结**写成**已冻结**（`G-CONTRACT` / `G-DELETE-CONTRACT` 均为 OPEN，且 `M2-C1 §5.11` 字段与错误码一律标注「待 D07 冻结」）；③未发现会改变架构结论的**事实错误**（hash、基线条数、检查器结果、Task/Review 指针、代码事实抽检均与仓库现状一致）。

### 4.2 P1（进入实现前必须处置）

**无。**

### 4.3 P2（可并行修订，不阻断本结论）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **R8-01** | §13.3 L777 | 「**本文尚未提交**，Appointment 必须同时固定方案 SHA-256 与复审 head」在**被审字节上已不成立**：该文件早在 `6cab0b083`（2026-11-01 01:04:49）入库，r4 自身又由 `74a772167` 入库（当前 `HEAD`）。同句「当前复审基线为 `main@29d06c462`」相对本轮 head 落后 7 个提交（含 `apps/` 3 个文件改动） | 改为「本文 r4 修订已入库于 `<commit>`；Appointment 以**提交哈希 + 文档 SHA-256** 双钉住」；属作者写作时点正确、随提交自动过期的自指陈述，非写作时的事实错误 |
| **R8-02** | §13.3 L783（可转发指令） | 「Appointment 固定 `reviewed_head = 本轮交付消息提供的最终 SHA-256` 与 `reviewed_document_sha256 = 同一 SHA-256`」把**提交 head** 与**文档摘要**混为一个值；按字面转发会生成不合规 Appointment（本轮实际为 `reviewed_head=74a772167`、`reviewed_blob_sha256=8895aebe…`，见 `doc/09_COLLABORATION.md` 的 `base_commit`/`reviewed_head` 约定与本轮 Appointment front matter） | 拆成两字段：`reviewed_head = <提交哈希>`、`reviewed_document_sha256 = <LF blob 摘要>`，并注明「两者不同值」 |
| **R8-03** | §9.1 L491 / §15.6 L933 | 直接把 `PreviewPermanentDeleteBooks`（L491）与 `BOOK_DELETE_STALE_PREVIEW`（L933）写成确定名称；ADJ-001 用「如 `PreviewPermanentDeleteBooks`」（§6.1）、明示「本文件**不**冻结具体字段名」（§6.1 末）、并把该错误码列入「**待冻结**的错误码候选」（§6.3）。§9.1 第 2 步（L492）已正确写作「错误码候选」，同一节内两处口径不一致 | L491/L933 加「候选」或「待 D07 冻结（C-04b）」限定，与 L492 对齐；避免下游误读为已冻结协议名 |
| **R8-04** | §9.1 L491 | 影响清单只列「人工修改、有效 Lock、current/pinned Revision 与回收站条目」；ADJ-001 PD-01 还要求**非终态 Run/Task（并作为 `BOOK_BUSY` 阻断项）**、受保护 artifact 数、活动草稿页数、将删除文件数与字节量、其他项目对该源的引用数。虽有「至少列明…（PD-01/PD-03）」与 §15.6「按 PD-01–PD-10 实现」兜底，但**阻断项**未落到方案文本 | 把「非终态 Run/Task → `BOOK_BUSY` 阻断」显式写进第 1 步（其余可在 FEA-12 逐条展开） |
| **R8-05** | §2 F09 L55 | 锚点 `ReaderOverlayViewModel.cs:23` 已失效：该文件在基线漂移区间被改（+45/−7），当前类声明在 `:43`；`1180cdba` 基线时该类在 `:25`、`:23` 亦为注释行。文首 L11 只有「须在实现 Task 冻结前重核」的笼统提示，锚点处无就地标注 | 就地标 `stale`/更新为符号级定位（§15.9 已声明「定位须按当前 head 重新核验」，可引用该条） |
| **R8-06** | §15.6 L918 | FEA-00 候选行出口仍写「hash、finding 逐项、**席位状态**」——这是 R7-03 已废止的席位口径残留；其余候选行均已改为「独立上下文 Review（按 DSH Appointment 登记）」 | 改为「Review 独立性登记（Appointment + 审查者身份/来源）」 |
| **R8-07** | §15.7 L947 | 「§3：直接引用/导入 \| **ADR** + source → FEA-08/09/11」仍以 ADR 作 Gate 标签；权威层现为「AD-003 已记录 + `G-CONTRACT` 冻结」，本表其余行已用新口径 | 改为「AD-003 已记录 + `G-CONTRACT`（+ 原型范围冻结）」 |
| **R8-08** | §14.3 L826 | 「方案引用为 **56/56** 存在且行号有效」记录只对 r3 字节成立；本轮字节含 **58 个相对链接**（本轮独立复核 58/58 存在、`#L` 行号全部在目标文件行数范围内；mermaid 6 块、代码 fence 22 个成对），且本句未注明适用哪个 blob | 加「（对 r3 字节）」或更新为当前数字 |
| **R8-09** | §15.1 L835/L836 | 引用 AD-003 / ADJ-001 作为「已记录 / 已冻结」依据时，未提及其自身 `G-REVIEW: ADDRESSED_PENDING_R2`（两文档的独立 Review 均未获批，见 AD-003 §5、ADJ-001 §9）。当前文本**不会**被读成「契约已冻结」（`G-CONTRACT` 已标 OPEN），但下游可能把「已记录/已冻结」外推为「已审查通过」 | 各加一句「该记录/冻结的独立 Review 为 `ADDRESSED_PENDING_R2`，不由本文代替」 |

## 5. 已核验为真（避免只列问题）

本轮独立复核（全部只读）确认以下关键论断成立：

1. **引用权威层的口径准确**：AD-003 `Status: ACCEPTED_ARCHITECTURE_AMENDMENT`、`G-ADR: SATISFIED`、`G-CONTRACT: OPEN`、`G-REVIEW: ADDRESSED_PENDING_R2`；ADJ-001 `Status: FROZEN_SEMANTICS / PENDING_IMPLEMENTATION / PROTOCOL_CHANGE_PROPOSED`、PD-01–PD-10 冻结于 §5、`G-DELETE-SEMANTICS: SATISFIED`、`G-DELETE-CONTRACT: OPEN`。方案 L29/L477/L516/L607/L764/L770/L835/L836 的引用与这些字段**逐项一致**。
2. **删除流程与 ADJ-001 语义一致、无反向主张**：C 流程「先披露 → 专门确认（绑定摘要）→ 同事务删除 → 失败整体回滚 → 不触原件」与 ADJ-001 §1/§3/§5 同向；D 流程「独立选择 → 检查共享引用与活跃 Run/lease → 确认 → Windows 回收站 → 逐项验证、失败保留」与 AD-003 §3.7 五项动作逐条对应；方案已明确「受保护项不是永久禁止删除」而不再主张「protected 即拒绝」。
3. **与 AD-003 的四项硬要求一致**：引用原件不改不覆盖（§9.1 表 L481、§9.2）；旧 Managed Copy 继续双读（L424、L609）；不自动迁移/删除（L607/L609）；应用内删除不碰原件（L494/L516）。
4. **r7 §6 的机械事实仍成立**：方案 58 个相对链接全部存在且 `#L` 行号在范围内；6 个 mermaid 代码块、22 个代码 fence 成对；`tools/governance/check.ps1` 只读运行 `PASS (3 warnings)`、`EXIT=0`、15 current documents——**该 PASS 只证明机械条件，不证明架构语义**（方案自身也已如此声明）。
5. **状态与指针陈述可复核**：`STATUS` 当前 Task = `REALUSE-DATA-SAFETY-8` `ready`、未开 worktree、`reviewer: null`、`canonical_evidence_status: pending`；来源 Review = `REALUSE-DATA-SAFETY-7-review`（`verdict: approved`、`base_commit: 29d06c462`、`reviewed_head: 58596949a`）——与方案 L9/L13 完全一致。
6. **r7 六项 P2 的处置落点均可定位**（见 §3 表）；未落库的会话级审查引用已全部移除（`session-*` / `a66dc75c` / `759f940f` 0 命中），并有两处显式「会话级口头复核不作为审查证据」。
7. **边界自述完整**：L9 声明 `PROPOSAL` 且「不是 ADR、冻结契约、Task 释放、实现验收或集成批准」；L29 重申「不是 ADR、冻结契约或实现授权」；§12.1 候选 ID「没有创建 Task 文件，没有进入 Plan/STATUS」；§15 / §16 分别自述「修订提案，非裁决或释放」与「作者自修，不构成 DSH adjudication 或独立 Review」；全部 AC 标 `planned`/`NOT_RUN`，无把 planned 写成 PASS 之处。
8. **本轮修订只改一个文件**：`git show --stat 74a772167` = 仅 `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`；未改 AD-002/AD-003/ADJ-001/`M2-C1`/V11R/Region 契约、未改 Task/STATUS/PLAN。

## 6. 边界合规判定

| 检查项 | 结论 | 依据 |
|---|---|---|
| 是否仍自述为非 ADR / 未冻结 / 未释放 Task | ✅ 是 | L9、L29、L631、L831、L1014 |
| 是否把未冻结写成已冻结 | ✅ 未发现 | `G-CONTRACT` / `G-DELETE-CONTRACT` 均标 OPEN；`M2-C1 §5.11` 字段与错误码一律「待 D07 冻结」；残留仅 R8-03 的名称限定 |
| 是否声称验证了未验证的东西 | ✅ 未发现 | 全部新功能与 AC 标 `planned`/`NOT_RUN`；§14.3 的检查结果均标「首次交付时」或「r7 只读记录」并声明「不证明架构语义」 |
| 是否越权修改权威/冻结文件 | ✅ 未发现 | 本轮 diff 只含本方案；未改 AD-002/AD-003/ADJ-001/契约/Task |
| 是否释放了候选 Task | ✅ 未释放 | §12.1/§15.6 全部标「候选」「未释放」；`STATUS` 未见任何 FEA-* Task |

**边界结论**：方案文本仍在 PROPOSAL 权限内，未越权；本报告也不构成任何释放或冻结。

## 7. 独立性声明

- **身份与来源**：`fea-reviewer-r8`，由 DSH Lead 通过 Agent Teams 共享任务 `task-6` 派发的 **fresh context** teammate（`reviewer_kind: subagent`）。**未参与** r4 修订（作者为 Codex）、未参与 r1/r2/r6/r6b/r6c/r7 任一复核、未参与 AD-003 / ADJ-001 / `FEA-01_CONTRACT_DRAFT` 撰写、未参与任何 FEA-00 候选 Task 的实现或返修；被审文档的任何字节均非本人产出。
- **独立性口径**：按 `AGENTS.md` 2026-10-31 用户裁决（独立 = **上下文独立**，不要求 Reviewer 与非作者/不同角色），本会话为新派发的独立上下文，且**未参与实现**，满足该口径；Appointment 已由 DSH 登记于 `doc/reviews/FEA-00-dsh-r8-appointment.md`（`reviewer_kind: subagent`、`reviewer_context: fresh (independent)`），符合 `doc/09_COLLABORATION.md:266`。
- **只读纪律**：仅读取 tracked/untracked 文档与源码；唯一写入 `doc/reviews/FEA-00-dsh-r8.md`；未 `git add/commit/checkout/stash/clean`、未建分支或 worktree、未 push；未修改产品代码、契约、Task、STATUS、PLAN、AGENTS、AD-002/AD-003/ADJ-001 与历史 Review；未触碰 ` M doc/handoffs/NIGHT-SHIFT-2026-11-01.md`（并行 agent 的改动）。
- **不带批准外推**：`verdict: approved` 只针对本报告 §2 的 P0/P1 判定；**不**代表 AD-003 / ADJ-001 / `FEA-01_CONTRACT_DRAFT` 已获独立批准，**不**代表 FEA-00 已转正式架构/契约变更，**不**代表任何 Task 可释放。
- **报告自身指纹**：本文件不内嵌自身 SHA-256（避免自指失效），交付后由 DSH 外部计算并登记。

## 8. 已执行的只读检查

| # | 检查 | 方式 | 结果 |
|---|---|---|---|
| 1 | 被审字节指纹 | `git cat-file blob 74a772167:…` → UTF-8/LF → SHA-256；另 `Get-FileHash` 工作树文件 | 两次同值 `8895aebe…1d54c`，与 Appointment/Task 给定一致；`CRLF=0` / `LF=1052` |
| 2 | 仓库与提交 | `git rev-parse HEAD`、`git status --porcelain`、`git show --stat --format="%H%n%an%n%ad%n%s" 74a772167` | `HEAD=74a772167`、`main`；1 file、+83/−66；状态仅 2 项并发项 |
| 3 | 全量 diff 逐块核对 | `git show 74a772167 -- doc/design/…`（20 个 hunk 全读） | 覆盖 L1、L29、L144、L477–L516、L607–L609、L631–L658、L765–L770、L777–L783、L810–L814、L820–L826、L831–L836、L854、L893、L899、L920、L929、L933、L939、L948、L950、L1014、L1022、L1042–L1048、L1052 |
| 4 | 权威层交叉核对 | 直读 `AD-003`（§2.1/§3/§4/§5/§6）、`ADJ-001`（§1/§2/§3/§4/§5/§6.1/§6.3/§7/§8/§9） | 形成 R7-01/R7-02 判定；见 §5.1–§5.2 |
| 5 | PD 覆盖度 | `Select-String -Pattern "PD-0[1-9]\|PD-10"` | §9.1 覆盖 PD-01…PD-10 全部 10 个编号 |
| 6 | 检查器断言面与自身 Review | 直读 `tools/governance/check.ps1:261-275`、`doc/reviews/FEA-00-dsh-r6c.md` front matter | 双哨兵 + bounded scope 注释块属实；r6c `decision: approved` |
| 7 | 治理检查器只读运行 | `pwsh -NoProfile -File tools/governance/check.ps1` | `PASS (3 warnings)`、`EXIT=0`、`scope 15 current documents` |
| 8 | 链接 / 围栏 / 锚点 | 正则抽取 `](path)` + 存在性 + `#L` 行数范围；计 ```` ```mermaid ```` 与 fence | 64 链接（58 相对，58/58 存在）、0 越界锚点；mermaid 6、fence 22 |
| 9 | 基线漂移与自检数字 | `git diff --numstat 29d06c462..74a772167`、`1180cdba..74a772167 -- apps/` | 7 commits / `apps/` 3 文件；`apps/` 自初稿基线共 **4** 文件（与方案 L11 一致） |
| 10 | 状态与指针 | 直读 `doc/STATUS.md`、`doc/tasks/REALUSE-DATA-SAFETY-8.md` front matter、`doc/reviews/REALUSE-DATA-SAFETY-7-review.md` front matter | 与方案 L9/L13 陈述逐项一致 |
| 11 | 残留口径扫描 | `Select-String`：`独审｜未参与实现的｜席位｜reviewer_unavailable｜待有效`、`待权威记录｜需 DSH 裁定｜ADR 正式记录`、`session-[0-9a-f]{8}｜a66dc75c｜759f940f` | 前三组 0 命中；席位口径仅剩 1 处（R8-06） |
| 12 | 代码事实抽检（漂移文件） | 直读 `ReaderOverlayViewModel.cs`（当前 vs `1180cdba`） | 类声明 `:25 → :43`，F09 锚点 `:23` 已失效（R8-05） |

## 9. NOT_RUN / BLOCKED

**NOT_RUN（不得写成 PASS）**

- `dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror`、`dotnet test … --no-build`、`python -m pytest -q`：静态文档审查，未运行。
- 方案 §12.3 的 A01–A15 全部场景；§14.1 的 H1–H7 原型；F20 的运行时 RED 复现。
- 主题/比例切换实测、Run 暂停恢复真机、源文件 lease、Windows 回收站负向原型、备份/恢复演练、迁移演练、双语界面真机、混合 DPI 双屏。
- Mermaid 渲染器、方案内示例 JSON 的 schema validator（均不存在）。
- AD-003 / ADJ-001 / `FEA-01_CONTRACT_DRAFT` 的独立批准（前两者 `G-REVIEW: ADDRESSED_PENDING_R2`，第三者 `DRAFT`），不在本报告范围；本报告不代替其审查。
- 任何「当前行为未退化」类结论：未运行测试。

**BLOCKED**

- H2（混合 DPI 双屏）/ H3（热切换性能）：无受控桌面与真机双屏环境，未尝试，**不给可行性实测结论**。
- 不提供任何「实现可交付」判断；方案内候选 Task 仍为 `proposed`，未释放。

## 10. 审查前后仓库状态

审查前（本报告写入前实测）：

```
$ git rev-parse HEAD
74a772167f038bc079339aa4b4e4273160d4150c
$ git status --porcelain
 M doc/handoffs/NIGHT-SHIFT-2026-11-01.md
?? doc/reviews/FEA-00-dsh-r8-appointment.md
```

审查后：`HEAD` 未变、无 tracked 修改（除并行 agent 的上述 handoff 文件外）、无 commit、无 worktree/分支变更、无 push；新增唯一文件为本报告。被审方案 hash 在审查前后两次计算同值。

**并发登记（不得归因于本报告）**：`doc/handoffs/NIGHT-SHIFT-2026-11-01.md` 的 8 行新增由**其他并行 agent** 产生，本报告作者未读取其内容、未修改。`doc/reviews/FEA-00-dsh-r8-appointment.md` 为 DSH 本轮登记（审查时未跟踪）。

## 11. 需 DSH 处置（不在本报告写权内）

1. **9 条 P2 的接受/驳回**；其中 **R8-01 / R8-02** 直接影响下一轮 Appointment 模板，建议在冻结 C-01…C-12 之前顺手修正；**R8-09** 建议与 AD-003 / ADJ-001 的 `G-REVIEW` 收口一起处理。
2. **`doc/00_INDEX.md` 登记本报告**（如需 STATUS 指针，另由 DSH 决定）——超出本报告写权。
3. **`doc/plan/FEA-01_CONTRACT_DRAFT.md` 的 C-04c 状态**（现写「缺（转 Codex 修订）」）已被 r4 §9.1 的 PD 映射实质覆盖，建议 DSH 更新该草案（该文件属 DSH，不在本报告范围）。
4. **本轮不改变的事实**：FEA-00 仍非 Task、未释放；Source 线（FEA-09/11/12/13）与删除协议仍分别受 `G-CONTRACT` / `G-DELETE-CONTRACT` 阻塞；`check.ps1 PASS` 不是架构语义证据。

---

**一句话结论**：r4 已把 r7 的两项 P1 实质处置完毕——AD-003/ADJ-001 的引用口径（`G-ADR: SATISFIED` / `G-CONTRACT: OPEN` / `G-DELETE-SEMANTICS: SATISFIED` / `G-DELETE-CONTRACT: OPEN`）与 D01/D07 落点准确，显式彻底删除流程已完整映射 ADJ-001 PD-01–PD-10（只读预览、摘要绑定、零变化门禁、事务回滚、原件独立回收），r7 的 6 项 P2 也全部有处置；本轮 **0 P0 / 0 P1 / 9 P2**，故判 **`approved`**。该结论不构成契约冻结、Task 释放，也不代表 AD-003 / ADJ-001 已获独立批准。
