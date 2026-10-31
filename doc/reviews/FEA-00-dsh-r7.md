---
document_id: FEA-00-dsh-r7
kind: independent_review
reviewer: fea-reviewer（DSH 派发 teammate）
reviewer_kind: subagent
reviewer_source: "Agent Teams fresh context：由 DSH Lead 通过共享任务 `task-1` 派发的独立上下文 teammate `fea-reviewer`；未参与方案撰写，未参与 r1 / r2 / r3 / r6 / r6b / r6c 任一复核，未参与 AD-003、ADJ-001 撰写或任何实现"
reviewer_independent: true
reviewed_by_implementer: false
round: 7
task: FEA-00（候选切片；仓库无 FEA-00 Task 文件、未释放实现）
reviewed_document: doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md
reviewed_document_sha256: 2f925cca7229d17a13943bfd4c297386ae21010f7bf8b61c3ae5169795afa120
reviewed_document_lines: 1035
source_head: 841cbdc4b53620fed2a6ac3534feb881c20ed2e4
source_branch: main
proposal_declared_baseline: 1180cdba79e4d610521dde13f0c8a458220f9d90
prior_reviews:
  - FEA-00-dsh-r1（independent, changes_requested）
  - FEA-00-dsh-r2-technical-recheck（DSH 技术复核，非独立 Review）
verdict: changes_requested
captured_at: 2026-11-01T00:48:20+08:00
captured_by: fea-reviewer
---

# 独立 Review：FEA-00 可切换前端架构方案（第 7 轮 / r3 字节）

**本报告不是** ADR、冻结契约、Task 释放、实现验收或集成批准。它固定被审文档的字节与仓库 head，给出 findings、r1 findings 的处置对照、C-01…C-12 契约清单状态与 NOT_RUN。`verdict: changes_requested` —— 不含批准语义。

## 0. 性质与定位

| 项 | 值 |
|---|---|
| 被审对象 | `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`，**未跟踪 PROPOSAL**，不是 ADR / 冻结契约 / Task |
| 本轮性质 | 静态文档审查（只读仓库 + 只写本报告）。**不运行**构建、测试、应用、迁移、原型 |
| 结论适用范围 | 仅对 `reviewed_document_sha256` 与 `source_head` 这对字节有效；任一变化即失效，须重算并重新 Appointment |
| 写权 | 唯一写入本文件；未修改任何 tracked 文件、未 `git add/commit/checkout/stash`、未改产品代码/契约/Task 状态 |

## 1. 基线与漂移

| 项 | 期望 / 声明 | 实测 | 判定 |
|---|---|---|---|
| 仓库 | `G:/CODEX/New Manga`（Git common dir = 仓库内 `.git`） | 同 | ✅ |
| 分支 / HEAD | —— | `main` / `841cbdc4b53620fed2a6ac3534feb881c20ed2e4` | 记录 |
| 被审方案 SHA-256 | `2f925cca7229d17a13943bfd4c297386ae21010f7bf8b61c3ae5169795afa120` | **逐字节一致**（审查开始与写入报告前各算一次，两次同值） | ✅ |
| 方案行数 | 1035 | 1035 | ✅ |
| 方案自述源码基线 | `main@1180cdba79e4d610521dde13f0c8a458220f9d90`（方案 L7/L763/L816） | 实际 HEAD 已前进 7 个 commit（全部 `doc/**` + `tools/governance/check.ps1`）；被引 **16 个源码文件** 在 `1180cdba..841cbdc` 间 `git diff --numstat` 均为空 | 事实结论不受影响，陈述过期（R7-06） |
| 方案文件 mtime | —— | `2026-10-31 19:55:08` | 早于 AD-003（`20:48:27`）与 ADJ-001（`20:48:23`） |
| 需求文档 | `doc/design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md`（未跟踪） | 未参与本轮，未修改 | 记录 |
| 权威层新文档 | 方案未引用 AD-003 / ADJ-001 | 两文档均已入库（commit `504797ba7`），状态分别为 `ACCEPTED_ARCHITECTURE_AMENDMENT` 与 `FROZEN_SEMANTICS` | **核心 findings 来源（R7-01/R7-02）** |

**漂移登记（不覆盖、不还原他人内容）**：审查开始时 `git status --porcelain` 为 2 个未跟踪项（方案 + 需求文档），无 tracked 修改。方案自述"当前 head 1180cdba"与实际 head 的差异属审查时点漂移，非作者错误，但影响若干"当前状态"陈述，见 R7-06。

## 2. 结论

**`changes_requested`。** 0 项 P0、2 项 P1、6 项 P2。

三层判断：

1. **r1 的 2 项 P0 已不再成立为 P0，但也不是"方案已销案"。** r3 已按要求把 F-01/F-02 改写成"与现行冻结语义相反、需裁决"，这是 r1 要求的修订方向，**已完成**；其销案条件（用户裁决 + 正式 ADR 记录 + 删除语义冻结）已由**方案之外**的 [AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)（`G-ADR: SATISFIED`）与 [ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)（`G-DELETE-SEMANTICS: SATISFIED`）满足。因此本轮**不把 F-01/F-02 列为 P0**；但方案当前字节仍把这两件事写成"待 DSH 正式记录 / 待裁定"（P1，R7-01）。
2. **r1 的 14 项 P1 在文本层面已全部有处置**（见 §4），绝大多数是 `[建议]`/待 DSH 冻结的草案，符合 PROPOSAL 性质；未被文本处置的只有 F-03 的三处口径同步（P2，R7-08）与 F-18 的交互契约承接（P2，R7-07）。
3. **r3 未引入新的架构级矛盾**，但引入了两类可复核缺陷：删除流程设计**未映射 ADJ-001 已冻结的 PD-01–PD-10**（P1，R7-02），以及 §13.3/§15.8/§16 的**状态与证据链陈述过期/不可复核**（P2，R7-03–R7-06）。按 `doc/09_COLLABORATION.md`（§6 第 8 条）"P0/P1 未解决不能批准"，故结论为 `changes_requested`。

**与 r1 的对比要点**：r1 是 `changes_requested`（2 P0 + 14 P1）；r7 是 `changes_requested`（0 P0 + 2 P1 + 6 P2）。**阻塞层级下降，但不能批准**：P1 两项都直接落在"用户可见数据安全"与"权威层一致性"上。

## 3. Findings

严重度口径沿用 r1：**P0 = 阻塞采纳**（处置前不得转契约冻结或释放候选 Task）；**P1 = 进入实现前必须处置**；**P2 = 精度、归属、边界与可验证性改进项**。

### 3.1 P0（阻塞采纳）

**无。** 说明：r1 的 F-01/F-02 之所以不再定 P0，依据是 AD-003 §5（`G-ADR: SATISFIED`）与 ADJ-001 §9（`G-DELETE-SEMANTICS: SATISFIED`）已把"需要用户裁决 / 需要 DSH 记录"两项前置关闭，且 AD-003 §5/§6 与 ADJ-001 §9 明确"记录决定 ≠ 冻结契约"——契约冻结（`G-CONTRACT` / `G-DELETE-CONTRACT`）仍 OPEN，这属于方案设计要配合的事项，不构成对方案本身的否决。

### 3.2 P1（进入实现前必须处置）

#### R7-01（P1）| 权威层已变化，方案仍把已完成的用户裁决与 ADR 记录写成"待办"，且 D01/D07 的处置对象过期

| 字段 | 内容 |
|---|---|
| 位置 | 方案 L25（`[用户决定，待权威记录]`、"DSH 须将该决定记录为架构 ADR"）、L473（"需 DSH 裁定"）、L504（"待 DSH 对照 `M2-C1 §5.11.2` 裁定并冻结"）、L597（"在 ADR 正式记录及契约处置前现行 Managed Copy 仍有效"）、§15.1 标题 L818（"两个阻塞裁决"）与 L820 / L821、§13.2 D01 L750 / D07 L756、§12.1 L644 与 §15.6 L922（Source 线阻塞条件） |
| 证据 | **AD-003**（`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`）：`Status: ACCEPTED_ARCHITECTURE_AMENDMENT`、`Decision authority: User`、§2.1 双哨兵口径、§3.3–§3.7 逐项处置备份/迁移/资源信任根/删除授权（即方案 L820 所要求的六项）、§5 `G-ADR: SATISFIED` / `G-CONTRACT: OPEN`。**ADJ-001**（`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`）：§1 "§5.11.2 语义保持有效、用户决定 #5 是增量前置而非反向语义"、§5 PD-01–PD-10 冻结、§9 `G-DELETE-SEMANTICS: SATISFIED` / `G-DELETE-CONTRACT: OPEN`。两文档于 commit `504797ba7` 入库，mtime 均晚于方案（19:55 → 20:48）。`tools/governance/check.ps1:261-275,570-587` 已按 r2 `G-02` 扩展为双哨兵 + 架构断言面校验，并经 [r6c](FEA-00-dsh-r6c.md) 独立 Review `approved`；即方案 D01 要求的"治理哨兵修改方案"也已落地。**方案对 AD-003 / ADJ-001 的引用数：1 处，且只作为"可能的文件名"出现（L820"AD-002 修订或新 AD-003 的记录方式交 DSH 协调"）**，未引用其内容。 |
| 触发条件与失败场景 | ① **重复权威**：DSH 依 D01 再起草一份"架构补充决策 + 五项反转清单 + 哨兵方案"，与 AD-003 §2.1/§3 重复；若再改 AD-002 历史哨兵字面量，`check.ps1` 架构断言面直接判红。② **错误 Gate 判定**：按 §15.1 标题与 L820/L821，读者会认为 F-01/F-02 仍是"阻塞裁决"，从而把 Source 线阻塞理由写成"ADR 未记录"（实际是 `G-CONTRACT` 未冻结），把删除线阻塞理由写成"语义未裁定"（实际是 `G-DELETE-CONTRACT` 未冻结）。③ **冻结范围漏项**：D07 未引用 ADJ-001 §6.1 的 `PreviewPermanentDeleteBooks` / `inventory_digest` 提案，冻结 D07 时可能只冻结"§5.11.2 原语义"而漏掉已冻结语义所要求的新增可观测面。④ **复审噪声**：新 Reviewer 会再次把 F-01/F-02 报为 P0（r2 技术复核已因同类陈旧产生 S-01…S-07，见 [r2](FEA-00-dsh-r2-technical-recheck.md) §3.2）。 |
| 建议修订（可直接替换的文本草案） | §1 L25 首句改为"**[用户决定，已记录；契约未冻结]** 用户 2026-10-31 决定已由 AD-003 正式记录（`G-ADR: SATISFIED`），删除语义已由 ADJ-001 冻结（`G-DELETE-SEMANTICS: SATISFIED`）；两者均为**决策记录**，其自身 `G-REVIEW` 为 `ADDRESSED_PENDING_R2`、`G-CONTRACT`/`G-DELETE-CONTRACT` 仍 OPEN。Source 线阻塞条件因此是**契约与范围冻结**，不是 ADR 记录。"；§15.1 标题改为"两个已记录决定与未关闭的契约 Gate"；L820/L821 逐项把"尚待 DSH 正式记录 / 仍须正式裁定"改为"已由 AD-003 / ADJ-001 记录/冻结，剩余为 D01–D08 契约冻结"；L473/L504/L597 同步；D01 拆为 D01a（引用已完成记录）与 D01b（`G-CONTRACT` 及其下游反转冻结），D07 增引用 ADJ-001 §5/§6.1。 |

#### R7-02（P1）| 显式彻底删除（C 流程）设计未映射 ADJ-001 已冻结的 PD-01–PD-10，FEA-12 验收点仍写"F-02 裁定"占位

| 字段 | 内容 |
|---|---|
| 位置 | 方案 §9.1 L473–L485（保护语义与 C 流程）、§9.2 L495–L504、§15.6 FEA-12-CORE L916（AC 列"软删/恢复命令、外部路径拒绝、期限及 **F-02 裁定**"）、§15.7 §4 行 L931、§12.3 A11 L713 |
| 证据 | **ADJ-001 §5**（自本文件生效、`PENDING` 仅指实现未做）要求：PD-01 逐项影响清单（人工修改区域数、锁定区域数、current/pinned 列表与数量、受保护 artifact、活动草稿页、非终态 Run、将被删除文件数与字节、其他项目引用数）、PD-02 单条/批量**分别**绑定 `inventory_digest`（单条命令明确拒收数组）、PD-03 清单必须由 Core 只读、零副作用计算（**UI 不得自行估算**）、PD-04 **确认前零变化、任何目标状态变化即拒绝并重新预览**、PD-07 `cleanup_pending` 只允许显式重试。方案 §9.1 对 C 流程仅有"逐项展示受影响内容 + 专门确认 + 同一事务删除"，**无只读预览命令、无摘要绑定、无"确认前零变化"门禁**；§9.2 的 `DeletePlan`/逐项 journal 属 D 流程（原文件删除），不能替代 C 流程的 PD 要求。方案全文 `inventory` / `inventory_digest` / `PreviewPermanentDelete` / `PD-0` **均 0 命中**（本轮 grep 复核）。 |
| 触发条件与失败场景 | FEA-12-CORE 按方案现有 AC 验收：UI 端自行计算"将删除的人工修改/锁定/固定版本"数量 → 用户看到的清单与 Core 实际删除集合不一致（违反 PD-03）；用户确认后、事务开始前另一窗口保存了人工译文或新 pin → 仍被删除（违反 PD-04），且方案 AC 无此断言，测试不会发现；批量命令引入批量字段/单条命令被塞入数组 → 与 `M2-C1:723` closed shape 冲突。后果是**人工译文 / Lock / current·pinned 在"已确认"名义下丢失**，属本项目最高风险类；而验收仍判定通过。 |
| 建议修订 | §9.1/§9.2 增一节"显式彻底删除（C 流程）契约映射表"，逐行列出 PD-01…PD-10 → 方案落点 → FEA-12 AC；FEA-12-CORE 的出口列改为"ADJ-001 §5 逐条 + §6.1 提案字段（`PreviewPermanentDeleteBooks`、`inventory_digest`、`BOOK_DELETE_STALE_PREVIEW`）"，删除"F-02 裁定"占位；§15.7 §4 行补 PD 行；D07 明确"冻结 ADJ-001 §6.1 字段与码表"。 |

### 3.3 P2（可并行修订）

#### R7-03（P2）| Review 席位与批准路径口径过期：仍写"ZCode 独审 / 待有效席位"

- **位置**：方案 §12.1 L625（`S0 FEA-00 … ZCode 独审，Codex 不审自己的方案`）、L634（FEA-07 写"未参与实现的独审 Agent"，与本表其余行"ZCode/Codex 独审"口径不一）、§13.3 L763、§14.2 L800、§15 L816。
- **证据**：`AGENTS.md:32`（2026-10-31 用户裁决：**独立 = 上下文独立**，不再要求非作者/不同角色；作者可派发独立上下文子 agent 执行 Review）；`doc/09_COLLABORATION.md:266`（`reviewer_kind=subagent` 定义 + "作者派发子 agent 审查仍须经 DSH Appointment 登记"）；ZCode CLI 不可用（r1 §1.4、r2 §6）。**本轮 r7 即该路径的实证：DSH 派发 fresh-context teammate 完成**。
- **失败场景**：FEA-00 的出口（§12.1"每条 blocking finding 有处置"）名义上依赖一个不可用席位，导致 FEA-00 无法被合法批准；或 DSH 沿用 r1 §1.4 的旧口径（L800、L816）反复声明"r1 不构成独立批准"，而按现行口径 r1 的独立性障碍只剩"缺 Appointment 登记"，理由已不成立。
- **建议**：§12.1 席位列统一为"DSH Appointment 登记的独立上下文 Reviewer（`subagent`/`agent`）"；L763/L800/L816 的"待有效席位"改为"待 DSH Appointment 登记 + 对精确 hash 复审"。

#### R7-04（P2）| §13.3 的"下一步"与可直接转发指令已过期，且与 §16.5/§16.6 自相矛盾

- **位置**：方案 §13.3 L763（"下一步是 **将修订版交 DSH 协调 r2 复审**"）、L769（可转发指令：基线 `main@1180cdba`、审查重点"十项问题"）。
- **证据**：同一文件 §16.5 L1031 与 §16.6 L1035 已记录 r2、r3 复核**已发生**；产物侧现有 r1、r2-technical-recheck、r6/r6b/r6c 与本 r7。L769 的指令要求 Reviewer 回答"十项架构问题"，不要求核 r1 findings 处置、C-01–C-12、AD-003/ADJ-001 一致性。
- **失败场景**：DSH 若按 L767–L769 原文转发 Appointment，新任 Reviewer 会重做 r1 式十项问题审查、以旧 head 为基线、不知道要核处置台账 → 重复劳动且结论与 r1 同构，浪费一轮；同时"r2 复审"的措辞会让后续轮次编号继续混乱（本报告已是第 7 轮）。
- **建议**：§13.3 整体重写为"下一轮 Appointment 输入模板"：精确 `reviewed_document_sha256`、`reviewed_head`、必读产物（r1 / r2 / 本报告）、要求逐条 disposition + C-01…C-12 + NOT_RUN，并删除轮次编号。

#### R7-05（P2）| §16 以未落库的会话级审查作为"已确认"依据

- **位置**：方案 §16 首段 L997（`session-5ba272c1-…`、hash `a66dc75c…`，自称"r2 结果仅在会话中，未写 Review 文件"）、§16.6 L1035（hash `759f940f…`，"DSH r3 **确认** F-08/F-11/F-19/F-25/F-38/F-39 的文本修订到位"）。
- **证据**：`doc/reviews/` 内无 `a66dc75c` / `759f940f` 对应的任何产物（本轮列目录复核）；[r2 技术复核](FEA-00-dsh-r2-technical-recheck.md) §1 与 §5 `G-01` 已提出该治理缺口并要求"补落库或从正文删除"，**当前字节仍未处置**；`doc/09_COLLABORATION.md:87`（当前 Review/adjudication 须绑定 `base_commit`/`reviewed_head`）、`:266`（"不得以'已派发子 agent'代替实际完成的审查"）。
- **失败场景**：§16.6 用不可复核的会话确认支撑"修订到位"的判断，后续若被当作"已复核"引用，会在审查链上留一个无法追溯的环；与 G-01 的处置要求直接冲突。
- **建议**：删除两处会话 hash 与"确认"措辞，改为"作者自修，未获可复核 Review；独立复核结论见本报告"。

#### R7-06（P2）| 基线 head 与自检数字过期（事实结论不受影响）

- **位置**：方案 L7（"本文代码位置均指此 HEAD `1180cdba`"）、L763、L816；§14.3 L808–L811（"55 个文件链接"、"`PASS (2 warnings)`…13 个当前文档"）。
- **证据**：实测 HEAD = `841cbdc4`，距 `1180cdba` 共 7 个 commit，全部为 `doc/**` 与 `tools/governance/check.ps1`；**被引 16 个源码文件（`step_writes.py`、`library.py`、`pipeline.py`、`service.py`、`nmbak.py`、`schema.py`、`managed_storage.py`、`handle_resolver.py`、`trash.py`、`migrator.py`、`App.axaml.cs`、`AppOptions.cs`、`IHostController.cs`、`ThemeModels.cs`、`AppShellV2.axaml.cs`、`StudioPageViewModel.cs`）在该区间 diff 均为 0**，故 §2/§15.9 的代码事实仍成立。本轮只读运行 `tools/governance/check.ps1` → `PASS (2 warnings)`、`EXIT=0`，但 scope 已是 **15 current documents**（AD-003 入册 + 检查器扩面），且方案内 62 个链接中 56 个相对链接 + 6 个 mermaid 图在本轮全量复核为 **56/56 存在且行号在范围内**。
- **失败场景**：实现方据 L7 在旧基线上开 worktree/准备 Task，错过检查器新断言面与 AD-003/ADJ-001；或把 §14.3 的"13 个当前文档"当作现状证据引用（§14.3 本身已标"首次交付时"，但 §15/§16 未更新）。
- **建议**：L7/L763/L816 改为"被引源码自 `1180cdba` 起未变更（本轮抽检 16 个文件 diff=0）；当前 HEAD 为 `<head>`"；§14.3 明确标注"r1 交付时点，现为 15 个当前文档"。

#### R7-07（P2）| C-10 的"交互契约"仍无承接（r1 F-18 残留）

- **位置**：方案 §15.7 L924–L938（追溯矩阵）、§15.2 §6.3 行 L837（快捷键作用域）、§15.3 L872（draft owner）；缺少"手势优先级 / 移动阈值 / 可编辑态"的冻结交付物。
- **证据**：全文"阈值"唯一命中是 L1015 的**对比度**阈值；"移动距离""长按"0 命中；"可编辑态"唯一命中是 L265 的草稿 token 语境；"手势"7 处仅为角色描述与 Flush/AC 语境，`§12.2 FEA-14-READ` 只有"手势缩放后松开不翻页"单点 AC。r1 F-18 引概念 §7 要求 DSH 在交互契约中冻结移动阈值/工具快捷键/可编辑状态。
- **失败场景**：FEA-06/FEA-14-EDIT 各自实现手势判定（如画布拖动 vs 区域选中的移动阈值），两套 UI 与画布行为不一致；FEA-01 冻结端口时无交互契约可引，阻断/可编辑判定（"绘制中/拖拽中不得切换"）只能各写各的。
- **建议**：§13.2 增 D09"交互契约"（手势优先级与移动阈值、工具快捷键作用域、可编辑态与阻断条件），或并入 D03 并写明交付物归属 FEA-01。

#### R7-08（P2）| V11R 修订范围三处口径仍不一致（r1 F-03 残留）

- **位置**：方案 §4.1 L140（"需要 DSH 对 V11R **§2/§3/§6** 的适用范围作正式修订"）、§13.2 D02 L751（"V11R **§1/§2/§3/§4/§6**"）、§15.2 L827–L837（逐条覆盖 **§1.1/§1.2/§2.2/§2.3/§2.4/§3/§4/§6.1/§6.3**）。
- **证据**：r1 F-03 要求"合并为一张逐条契约修订清单"；§15.2 已满足该要求且是最完整口径，但 §4.1 与 D02 的枚举未同步。
- **失败场景**：FEA-05 依 §4.1 只请求 §2/§3/§6 的修订，则 §1.2 写权（新建 `Frontends.Fluent` 等项目）与 §6.3 KeyMap 单一注册表未获正式修订 → 实现时或越权、或因"未登记例外"被独立审查判违规而返工。
- **建议**：§4.1 与 D02 统一改为"见 §15.2 条款级修订单（§1.1/§1.2/§2.2/§2.3/§2.4/§3/§4/§6.1/§6.3）"，保留 §4.1 仅作"设计系统作用域"的局部说明。

## 4. 与 r1 findings 的 disposition 对照

口径：**已处置** = 文本层面已回应且方案内可定位；**部分处置** = 方向正确但缺已被冻结/已存在的具体要求；**外部处置** = 由方案之外的权威文档完成，方案未同步。

| r1 ID | 级别 | r3 处置位置 | r7 判定 |
|---|---|---|---|
| F-01 | P0 | §1 L25、§13.2 D01、§15.1 L820 | **外部处置 + 未同步**（AD-003 `G-ADR: SATISFIED`）→ R7-01 |
| F-02 | P0 | §9.1 L473/L479/L485、§9.2、§15.1 L821 | **外部处置 + 部分处置**（ADJ-001 冻结 §5.11.2 语义 + PD-01–PD-10；方案未映射 PD）→ R7-01/R7-02 |
| F-03 | P1 | §15.2 L827–L837（条款级修订单）、§16.3、L839 重申 R-03 | 已处置（残留口径不一致 → R7-08） |
| F-04 | P1 | 新增 `FEA-04b`（L631、L650、L662、L908）；FEA-06 依赖 L633 | 已处置 |
| F-05 | P1 | §15.6 L897–L920 全表 `write_scopes`；组合根四文件 DSH 单点 L897；§16.1 重叠处置 | 已处置（CoreClient 双写权显式交 DSH 裁定，属合规 deferral） |
| F-06 | P1 | §15.2 L835/L841（Appearance coordinator 唯一写者 + `IThemePersistence` 适配同文档）+ 15 行字段矩阵 | 已处置 |
| F-07 | P1 | F20 改判 `[事实]` L62；FEA-00a L627/L890/L902；§10.3 L574 | 已处置（修复本身仍 `NOT_RUN`） |
| F-08 | P1 | §15.5 L891（默认复用 source snapshot、不可用则阻塞） | 已处置 |
| F-09 | P1 | §15.3 L863–L870 六行迁出表 + L861 fail-closed | 已处置 |
| F-10 | P1 | §5.2 L267 draft owner + §15.3 L872 分域串行 | 已处置 |
| F-11 | P1 | §15.4 L876（`incomplete/complete` 谓词）+ §16.2 五读路径 | 已处置 |
| F-12 | P1 | §15.4 L878（grant 种类、续租、持久 registry、递归根、parity） | 已处置 |
| F-13 | P1 | §15.4 L882（命令面 vs V2 可达性分开）+ §15.6 FEA-12 | 已处置（精度差：ADJ-001 §7 四层现状更准，"V2 连硬删都不可达"） |
| F-14 | P1 | §15.4 L884（备份覆盖清单、独占锁、staging）+ §9.3 | 已处置 |
| F-15 | P1 | §15.4 L880（不变量退役、`remove_managed` 只接受受管相对路径、负测） | 已处置 |
| F-16 | P1 | §15.2 L843–L855 字段迁移矩阵 | 已处置 |
| F-17 | P2 | §10.1 快照表 L535（上下文页内容/不可变 blob 引用）+ §15.5 L891 | 已处置 |
| F-18 | P2 | §15.7 L924–L938 追溯矩阵（成立）；交互契约缺 | **部分处置** → R7-07 |
| F-19 | P2 | §4.2 L194 `IReadOnlyList<FrontendWindowContent>` + §15.5 L892 定义 | 已处置 |
| F-20 | P2 | §15.5 L892（layout pass + Loaded + Render 回调 + 几何非零） | 已处置 |
| F-21 | P2 | §15.5 L892 回滚含窗口级材质/背景/MinWidth/Title/bounds | 已处置 |
| F-22 | P2 | §15.8 F-22 → §15.6 FEA-01"接口生成清单"；§15.9 符号表 | 已处置（委托 FEA-01 交付） |
| F-23 | P2 | §2 F08 L50 已改"legacy Undo=revision 恢复；V2 无 Undo/Ctrl+Z" | 已处置 |
| F-24 | P2 | §2 F10 L52 改引 `app.manifest:6` + §15.5 A01/A08 manifest 生效校验 | 已处置（本轮抽检 `app.manifest:6-7` = `PerMonitorV2` 属实） |
| F-25 | P2 | §2 表锚点已更正（`App.axaml.cs:56`、`AppOptions.cs:71`、`MainWindow.axaml.cs:484`）+ §15.9 | 已处置（本轮抽检三处一致） |
| F-26 | P2 | §15.5 L893（单一调度器 + 领域 ownership + 调用次数断言） | 已处置 |
| F-27 | P2 | §5.2 L265/L247、§15.3 L872（"未 ACK 内存内容不承诺崩溃恢复""journal 不在 `cache/`"） | 已处置 |
| F-28 | P2 | §15.5 L893 ExitCoordinator + sidecar 存活/清理测试 | 已处置 |
| F-29 | P2 | §15.4 L886 content identity vs rendition observation | 已处置 |
| F-30 | P2 | §15.4 L884 `DatabaseId` 标注新增 + 回填方式 | 已处置 |
| F-31 | P2 | §15.4 L878 递归授权根 + ZIP/CBZ 明确新增 | 已处置 |
| F-32 | P2 | §15.4 L880 三路径现状矩阵 + ProtectionPolicy 新建 | 已处置 |
| F-33 | P2 | §15.3 L861 现状（draft journal/edit token 尚不存在）+ 新增声明 | 已处置 |
| F-34 | P2 | §15.4 L886 书名唯一为新增应用级不变量 + 五条路径 | 已处置 |
| F-35 | P2 | §16.3 `componentContracts` 结构与 major/minor/fallback | 已处置 |
| F-36 | P2 | §15.2 L857（`motion.mode=on/off/system` + 三类强度） | 已处置 |
| F-37 | P2 | §15.2 L857 比例 slot 清单 + 多套 profile + 单项/全部重置 | 已处置 |
| F-38 | P2 | §16.4 L1023 FEA-09 逐项 AC（五格式/排序/重复名/密码/跳过/取消/进度） | 已处置 |
| F-39 | P2 | §16.4 L1025（SET 覆盖范围）+ §15.6/§15.7 归属 | 已处置 |
| F-40 | P2 | §15.5 L891（canonical builder 唯一归 FEA-10，FEA-14-AI 只做 adapter） | 已处置 |
| F-41 | P2 | §15.6 全表补等级 / `evidence_dir` / 可观察出口 | 已处置 |
| F-42 | P2 | §15.6 每行"中止/回退"列 + §11.2 引用 | 已处置 |
| F-43 | P2 | §6.1 L323 改为"App/Presentation 组合根经 `--theme-home` 解析注入" | 已处置 |

**统计**：2 P0 → 均不再构成 P0（F-01 由 AD-003 外部处置但方案未同步；F-02 由 ADJ-001 外部冻结但方案未映射 PD）；14 P1 → 14 已处置（F-03 残留口径不一致，另计 R7-08）；27 P2 → **26 已处置 / 1 部分处置**（F-18 → R7-07）。**无拒绝项**，与方案 §15.8"所有 findings 接受"一致。

## 5. C-01…C-12 契约清单状态

| C# | r1 要求 | r3 现状 | 判定 |
|---|---|---|---|
| C-01 | 架构默认存储语义的**用户 ADR** + 下游五项反转清单 + 哨兵处置 + "PASS 不证明语义" | 方案 D01/L25/L820 仍为"待记录/待裁定"；AD-003 已记录决定（`G-ADR SATISFIED`）、AD-002 顶部横幅 + 双哨兵、`check.ps1` 断言面扩面且经 r6c 批准 | **实质已落地、方案未同步** → R7-01；建议拆 `C-01a`（记录，已 SATISFIED）/`C-01b`（`G-CONTRACT` 冻结，OPEN）/`C-01c`（检查器口径，已实现） |
| C-02 | V11R 条款级修订单 + R-03 重申 + `nm.fluent.visual/1` 定位 | §15.2 九条逐条表 + §16.3 schema 草案 + L839/L1019 R-03 | **成立**（草案，待 DSH 冻结）；口径残留 → R7-08 |
| C-03 | 外观唯一写者 + 字段迁移矩阵 + 动效模型 | §15.2 L835/L841 + L843–L855 字段表 + L857 动效/比例 | **成立** |
| C-04 | 彻底删除三层区分 + `M2-C1` 处置 | §9.1 L473/L479/L485 有三层区分；ADJ-001 已裁定"语义保持 + 增量前置"并冻结 PD-01–PD-10；方案未映射、D07 仍写"先裁定" | **部分** → 拆 `C-04a`（语义=已冻结，改为引用）/`C-04b`（协议字段/码表=D07 待冻结）/`C-04c`（PD→§9/FEA-12 AC 映射，缺）→ R7-02 |
| C-05 | 页可见性/完整性谓词 + 5 处读路径 + 不削弱半写防护 | §15.4 L876 + §16.2（五路径、半写负例、新列默认 `incomplete`） | **成立** |
| C-06 | Source 授权面：grant 种类/续租/撤销/递归根/持久 registry/预算 | §15.4 L878（含 `ManagedRootTrust` 每根每代等价快照、旧 grant 不混用） | **成立** |
| C-07 | 应用端口/兼容面：代码生成方法清单替换"36"、错误、握手、增量 | §13.2 D03 + §15.6 FEA-01"接口生成清单"；方案本身未产出清单 | **成立**（委托 FEA-01，符合 PROPOSAL 性质） |
| C-08 | Run 快照/幂等：preview 同源、内容 pin、retry 语义、pending、完成口径、断线 receipt | §10.1/§10.2 + §15.5 L891 | **成立** |
| C-09 | 删除/备份/迁移：软删/恢复命令面、三路径统一、备份覆盖、`backup/2`、`DatabaseId`、调度归属、独占锁 | §9.2/§9.3 + §15.4 L884 + D07 | **成立**（但 D07 的"先裁定"表述过期，见 R7-01） |
| C-10 | 交互契约（手势优先级/移动阈值/可编辑态、draft owner）+ 需求→能力→Task→AC→证据矩阵 | 追溯矩阵 §15.7 成立；draft owner §15.3 L872 成立；快捷键 §15.2 §6.3 成立；**手势阈值/可编辑态缺** | **部分** → R7-07 |
| C-11 | 候选表补 `write_scopes`/校验等级/`evidence_dir`/per-task 回退/前置 Gate/设计冻结前置 | §15.6 全表 + DAG + FEA-04b | **成立**；席位列过期 → R7-03 |
| C-12 | 治理检查器定位：不检测"哨兵+覆盖性决策"、不扫 `doc/design/**` | L25/L820 已写"PASS 仅机械条件"；但未写具体边界，且检查器已扩面（双哨兵断言面、00_INDEX 指针、AGENTS 边界断言），r6c 已独立批准 | **部分**（定向正确、已过期）→ 并入 R7-01 处置；建议补一句"检查器断言面见 `tools/governance/check.ps1:261-275`，其自身审查为 r6c" |

## 6. 已核验为真（避免只列问题）

本轮独立复核（全部只读）确认方案以下关键论断成立，且与 AD-003 / ADJ-001 的技术边界**逐项一致**：

1. **F20 既有数据安全缺陷成立**：`src/infrastructure/providers/step_writes.py:207` `BEGIN IMMEDIATE` → `:248-266` `INSERT region_revisions` → `:269-276` `UPDATE regions SET text_json` → `:277` `commit()`，指针留给 seam（`:267-268` 注释自述）。与方案 F20 / FEA-00a 描述一致。
2. **符号存在性反证**：`IRunProjectionPoller`、`WindowBroker`、`FrontendRegistry`、`FrontendSwitchCoordinator`、Python 侧 `edit_token`/`edit_session`/`draft_journal` 在本轮 grep 中 **均 0 命中**；`library.py:299-302` `_COMPLETE_PAGE_WHERE` 确含 `managed_original_ref IS NOT NULL`。
3. **删除命令面现状**：`src/bootstrap/core_service.py` 仅 `PermanentlyDeleteBook`（`:4403` 处理分支、`:298` 命令集合）、`PermanentlyDeleteBooks`（`:298` 集合）、`ListRecycleBinBooks`（`:4559`），**无书籍软删/恢复命令**，与方案 §15.4 L882 一致（ADJ-001 §7 补充的服务层实现不推翻该结论）。
4. **与 AD-003 的一致性（四项硬要求）**：引用原件（§8/§11.1，`[建议]`）✅；旧 Managed Copy 继续读、`ManagedSourceAdapter`（§8.1 L420、§11.1 L593）✅；不自动迁移（§11.1 第 5 步"可选、显式"、L595"不在本迁移中自动删除"）✅；删除不碰原件（§9.2 L504、§9.1 表 L477）✅。
5. **与 ADJ-001 的方向一致性**：三层流程区分（GC/软删/显式彻底删除，L473）、先披露后专门确认再同事务删除（L473）、确认前不静默解锁/取消 pin（L473）、应用内删除不顺带删原件（L504）、双 Lock 有效并集交 Core 统一（L487）——均与 ADJ-001 §1/§3/§4 一致。**缺的是 PD-01–PD-10 的具体映射（R7-02），不是方向相反。**
6. **机械核验**：方案内 56 个相对链接 **56/56** 存在且 `#L` 行号在文件范围内；6 个 mermaid 代码块成对；`tools/governance/check.ps1` 只读运行 `PASS (2 warnings)`、`EXIT=0`（scope 15 documents）——**该 PASS 只证明机械条件，不证明架构语义**。
7. **方案的自律表述成立**：L5 声明非 ADR/契约/Task；§13.2 末"作者不能独立审核自己的方案"；§14.2 "自查不替代独立 Review"；§16.5 "以上是作者自修，不是 Reviewer 确认"；§15.8 无拒绝项。**方案未把 planned 写成 PASS**，也未把 AD-003/ADJ-001 假装成已冻结（它根本未引用）。

## 7. 独立性声明

- **身份与来源**：`fea-reviewer`，DSH Lead 通过 Agent Teams 共享任务 `task-1` 派发的 **fresh context** teammate（`reviewer_kind: subagent`）。被审文档的任何字节均非本人产出。
- **未参与**：方案撰写（作者 Codex）；r1 独立 Review（DSH reviewer 池切片 + DSH 汇总）；r2 技术复核；r3 会话复核；r6/r6b/r6c 检查器 Review；AD-003 / ADJ-001 撰写；任何 FEA-00 候选 Task 的实现或返修。
- **只读纪律**：仅读取 tracked/untracked 文档与源码；唯一写入 `doc/reviews/FEA-00-dsh-r7.md`；未 `git add/commit/checkout/stash`；未修改产品代码、契约、Task、STATUS、Plan、AGENTS、AD-002/AD-003/ADJ-001 与历史 Review。
- **Appointment 观察（供 DSH 处置，非方案 finding）**：审查时点 `doc/reviews/` 内未发现本轮 `FEA-00-dsh-r7` 的 Appointment 登记文件（现有 `FEA-00-codex-r4-appointment.md`、`FEA-00-codex-r5-appointment.md`、`FEA-00-dsh-r6-appointment.md`）。按 `doc/09_COLLABORATION.md:266`，作者派发子 agent 审查须经 DSH Appointment 登记；**该登记属 DSH 责任，不在本报告写权内**，请 DSH 在对本报告作出处置时补登记审查者身份与来源。
- **口径**：本报告受 `AGENTS.md:32`（2026-10-31 上下文独立裁决）与 `doc/09_COLLABORATION.md` §6 约束。它**不构成**实现释放、契约冻结或集成批准。

## 8. 已执行的只读检查

| # | 检查 | 方式 | 结果 |
|---|---|---|---|
| 1 | 方案指纹（两次） | `Get-FileHash -Algorithm SHA256` | `2f925cca…5afa120`，两次同值，与任务给定一致 |
| 2 | 仓库状态（审查前） | `git rev-parse HEAD`、`git status --porcelain` | `841cbdc4…`；2 个未跟踪项，无 tracked 修改 |
| 3 | 方案自述基线与漂移 | `git log/rev-list/diff --numstat 1180cdba..HEAD` | 7 commits（全 doc/tools）；16 个被引源码文件 diff 均为空 |
| 4 | 全部相对链接 | PowerShell 正则抽取 `](path#Lx)` + 存在性/行号范围 | 56/56 通过；mermaid 6 块、代码 fence 22 |
| 5 | 符号反证 | `Select-String` 全仓（`IRunProjectionPoller`/`WindowBroker`/`FrontendRegistry`/`FrontendSwitchCoordinator`/`edit_token`/`edit_session`/`draft_journal`） | 均 0 命中 |
| 6 | 代码事实抽检 | 直读 `step_writes.py:195-281`、`library.py:299-302`、`core_service.py:298/4403/4559`、`App.axaml.cs:56`、`AppOptions.cs:71`、`app.manifest:6-7` | 与方案/`r1` 描述一致 |
| 7 | 权威层交叉核对 | 直读 AD-003、ADJ-001、AD-002 横幅、`AGENTS.md:32/45`、`doc/09_COLLABORATION.md:262-266`、`doc/STATUS.md:7` | 形成 R7-01/R7-02/R7-03 |
| 8 | 治理检查器（只读运行） | `pwsh -NoProfile -File tools/governance/check.ps1` | `PASS (2 warnings)`、`EXIT=0`、scope 15 documents |
| 9 | 会话审查产物核对 | 列 `doc/reviews/` | 无 `a66dc75c`/`759f940f` 对应产物（R7-05）；无 r7 Appointment |

## 9. NOT_RUN / BLOCKED

**NOT_RUN（不得写成 PASS）**

- `dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror`、`dotnet test … --no-build`、`python -m pytest -q`：本审查为静态文档审查，未运行。
- 方案 §12.3 的 A01–A15 全部场景；§14.1 的 H1–H7 原型；F20 的运行时 RED 复现。
- 主题/比例切换实测、Run 暂停恢复真机、源文件 lease、Windows 回收站负向原型、备份/恢复演练、迁移演练、双语界面真机、混合 DPI 双屏。
- Mermaid 渲染器、方案内示例 JSON 的 schema validator（均不存在）。
- AD-003 / ADJ-001 的独立批准（其 `G-REVIEW` 为 `ADDRESSED_PENDING_R2`，不在本报告范围）。
- 任何"当前行为未退化"类结论：未运行测试。

**BLOCKED**

- H2（混合 DPI 双屏）/ H3（热切换性能）：无受控桌面与真机双屏环境，未尝试，**不给可行性实测结论**。
- 本报告不提供任何"实现可交付"判断；方案内所有候选 Task 仍为 `proposed`，未释放。

## 10. 审查前后仓库状态

**审查前**（本报告写入前实测）

```
$ git rev-parse HEAD
841cbdc4b53620fed2a6ac3534feb881c20ed2e4
$ git status --porcelain
?? doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md
?? doc/design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md
```

**审查后**（本报告写入后实测）

```
$ git rev-parse HEAD
841cbdc4b53620fed2a6ac3534feb881c20ed2e4
$ git status --porcelain
?? doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md
?? doc/design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md
?? doc/plan/FEA-01_CONTRACT_DRAFT.md
?? doc/reviews/FEA-00-dsh-r7.md
```

**并发登记（不得归因于本报告）**：`doc/plan/FEA-01_CONTRACT_DRAFT.md` 在本审查期间由**其他并行 agent** 新增，本报告作者未读取、未修改、未创建它（未提交内容归原作者所有）。本报告作者的唯一写入是 `doc/reviews/FEA-00-dsh-r7.md`；**本报告自身 hash 由交付后外部计算并登记（不自嵌，避免自指失效）**。除该新增外：HEAD 未变、无 tracked 修改、无 commit、无 worktree/分支变更、无 push；被审方案 hash 在审查前后两次均一致。

## 11. 需 DSH 处置（不在本报告写权内）

1. **R7-01 / R7-02 的修订要求转交方案作者（Codex）并在新 hash 上复审**；两者都是文本级修订，不改变方案架构方向。
2. **Appointment 登记**：为本轮补记审查者身份与来源（`doc/09_COLLABORATION.md:266`）。
3. **R7-05 的治理缺口**：`a66dc75c` / `759f940f` 会话复核要么补落库为 Review 文件，要么从方案正文移除（与 r2 `G-01` 同一项，仍未处置）。
4. **D07 的冻结前置**：在冻结 `M2-C1 §5.11` 相关字段前，先核对 ADJ-001 §5/§6.1，避免漏冻结 `PreviewPermanentDeleteBooks` / `inventory_digest`。
5. **`doc/00_INDEX.md` 登记本报告**、并决定 `STATUS`/Task 指针是否引用它——超出本报告写权。

---

**一句话结论**：方案的架构方向与事实基础在 r3 仍然成立，r1 的 2 项 P0 已由 AD-003/ADJ-001 在方案之外消解、14 项 P1 在文本层面全部处置；但方案**尚未同步这两个权威文档**（R7-01），且**显式彻底删除设计未吸收已冻结的 PD-01–PD-10**（R7-02），因此 `changes_requested`，不得据此转为契约冻结或释放任何候选实现 Task。
