---
document_id: FEA-GOV-5-c04b-r3
kind: independent_review
task_id: FEA-GOV-5
round: 3
scope: very-narrow（只核 r2 的 1×P1 + 2×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-18；独立上下文；未参与 C-04b 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-5-c04b-r2（changes_requested：P0×0 / P1×1 / P2×2）
reviewed_head: fc670f248
reviewed_head_full: fc670f2483092cdb6031f5499a15e0152d6d9cb3
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == fc670f248）"
reviewed_document: doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md
reviewed_sha256: 5ffe9ed665f86f3c61f291cf020b2d5eacdaf02912dfe8ca54b1a751cf0eb74c
reviewed_sha256_basis: "HEAD 的 LF blob（125 行，blob 90cc3fb62）"
baseline: "doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md PD-02/§6.1–§6.3 · doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.11.1–§5.11.5"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为非阻断（字段命名大小写不统一、§2.2 未区分两级 digest 校验、逐书 digest 输入集合未逐字段定义），登记为 K-1/K-2/K-3"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:10:24+08:00
captured_by: c01b-reviewer
---

# 独立复核 r3（极窄面）：FEA-C04b 集合级 digest 恢复确认

**本报告不是** 冻结动作、不构成对 ADJ-001 / M2-C1 的修改，也不构成执行授权。本轮只核 r2 的 1×P1 + 2×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断）。**

r2 的 P1 **已闭环**：批量确认恢复为「**集合级 `inventoryDigest`（绑定有序 `book_ids`）** + 逐书 `inventory_digests`（诊断用）」双字段，并逐步写明校验（两者都校验、缺失→`INVALID_REQUEST`、不匹配→`BOOK_DELETE_STALE_PREVIEW`）；预览出参同步含 `inventoryDigest`；digest 算法也写清了**有序拼接再 sha256** 的派生规则 —— 与 ADJ-001 PD-02 `:61`「绑定该有序集合的清单摘要」语义一致 ✓。

两条 P2 也到位：批量 `BOOK_DELETE_STALE_PREVIEW` 的返回形状已定为「顶层码 + `phase:"preflight"` + 逐项 `items[]`」（P2-1 ✅）；`title` 已注明「仅展示用；不参与 digest 计算或确认校验」，§2.3 表头已改为「12 行稳定 + 2 host 级/兜底 + 2 新增」（P2-2 ✅）。

3 条新的非阻断 P2 为**命名/精度**问题（同一协议内 snake_case 与 camelCase 混用、§2.2 校验表未分两级、逐书 digest 的输入字段集合未逐项列出），不影响语义与冻结判断。

| 核实项 | 结果 |
|---|---|
| 1. P1-2 集合级 digest（形状 + 出参 + 算法） | **✅ 已处置**（恢复 PD-02 有序集合绑定） |
| 2. P2-1 批量 STALE 返回形状 | **✅ 已处置** |
| 3. P2-2 `title` 注释 + §2.3 计数口径 | **✅ 已处置** |
| 4. 新问题 + `check.ps1` | 无新增实质问题；3 条非阻断 P2（K-1/K-2/K-3）；**PASS(3 warnings) EXIT=0**；无代码改动、未 push |

---

## 2. 3 处核对明细

### 2.1（P1-2）集合级 digest —— ✅

- §2.0（`:30`）批量：「`{book_ids[1..20], confirmed_book_ids[1..20], confirm_count, confirm_permanent_delete: true}` + **`inventoryDigest: string`（集合级）+ `inventory_digests: { [bookId]: string }`（逐书）**」；说明列：「集合级 digest 绑定**有序 `book_ids`**（PD-02 原文）；逐书 map 用于逐项诊断；**两者都校验**，任一缺失 → `INVALID_REQUEST`，任一不匹配 → `BOOK_DELETE_STALE_PREVIEW`」✓。
- §2.1 出参（`:40`）：「`{ inventoryDigest: string, inventoryDigests: { [bookId]: string }, computedAt: string(ISO-8601), items: DeletePreviewItem[] }`」✓。
- §2.1 digest 格式（`:44`）：「`sha256:<64 hex>`（小写）；**集合级 digest 算法**：对 `book_ids` 按调用方顺序拼接各 book 的逐书 digest（`sha256:` 前缀去掉、小写 hex），再整体 `sha256`；逐书 digest = 该 book 的保护+内容清单的 sha256。格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW`」✓ —— 重排 `book_ids` 会改变集合级 digest，**有序绑定语义恢复**（与 ADJ-001 PD-02 `:61` 一致）。
- 单条仍为 `inventory_digest`（`:29`）✓ 与 PD-02 `:60` 一致。

### 2.2（P2-1）批量 STALE 返回形状 —— ✅

- §2.4（`:92`）：「`PermanentlyDeleteBooksErrorView.code` ｜ 同上；批量 digest 不匹配时返回**顶层 `BOOK_DELETE_STALE_PREVIEW`** + `phase:"preflight"` + 逐项 `items[]`（与 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` 同形状）」✓ 不再是「或」二义。

### 2.3（P2-2）`title` 与计数口径 —— ✅

- §2.1 `DeletePreviewItem`（`:41`）：「`bookId, title（**仅展示用；不参与 digest 计算或确认校验**）, protection …`」✓。
- §2.3 表头（`:57`）：「错误码表（**12 行稳定 + 2 host 级/兜底 + 2 新增**）」✓ 与表内 14 行沿用（12 稳定 + `CORE_UNAVAILABLE` + `UNKNOWN`）一致。

### 2.4 `check.ps1` 与数据安全 —— ✅

- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2911 B / 80%、`REBASELINE_PLAN.md` 6554 B / 80%）；运行后 `git status` 为空 ✓。
- **提交面**：`fc670f248` 只改 C-04b（+6/−6）与 r2 报告（+172）；`git diff --stat c16359e6f..HEAD -- src apps` 为空；**未 push**（`fc670f248` 非 `origin/main` 祖先）✓。
- 被审字节：C-04b @ `fc670f248`，LF blob SHA-256 `5ffe9ed665f8…cf0eb74c`（125 行，blob `90cc3fb62`）。

---

## 3. 已知限制（非阻断）

#### K-1 — 同一协议内 snake_case 与 camelCase 混用

- 位置：`:29`（单条 `inventory_digest`，snake）↔ `:30`（批量 `inventoryDigest` + `inventory_digests`，camel）↔ `:40`（预览出参 `inventoryDigest`/`inventoryDigests`/`computedAt`/`bookId`，camel）。
- 依据：M2-C1 §5.11.1 的 DTO 与 payload 全部为 snake_case（`book_id`/`book_ids`/`confirmed_book_ids`/`confirm_count`/`requested_count`/`items[].error_code`）；ADJ-001 PD-02 的确认字段本身也是 `inventory_digest`（snake），§6.1 的预览返回是 `inventoryDigest`（camel）—— 本草案同时继承了两种风格。
- 建议：冻结前统一（推荐全 snake_case，与 M2-C1 一致：`inventory_digest` / `inventory_digests` / `computed_at` / `book_id` / `items[].book_id`），或在 §2.1 注明「返回体沿用 proposal 的 camelCase、请求体沿用 M2-C1 的 snake_case」并保持全稿一致（现稿两者混在批量一行内）。

#### K-2 — §2.2 校验表未区分集合级 / 逐书两级规则

- 位置：`:47-55`（§2.2 `inventory_digest` 校验）。
- 问题：表内「绑定 / 不匹配 / 缺失/格式错 / 时机」仍按**单一 digest** 描述；§2.0 已规定「两者都校验」，但 §2.2 未列两级各自的判定与优先级（例如：逐书 map 多出/缺少键、仅逐书不匹配、集合级不匹配但逐书全对）。
- 建议：§2.2 拆成两行组（集合级 / 逐书），或补「校验顺序：先集合级（含键集合与顺序）→ 再逐书内容」并给出各类失败的码。

#### K-3 — 逐书 digest 的输入字段集合未逐项定义

- 位置：`:44`（「逐书 digest = 该 book 的保护+内容清单的 sha256」）。
- 问题：「保护+内容清单」未列明具体字段（`protection.*` 全部？`contentSummary.*` 全部？`sharedFileRefs` 是否参与？序列化顺序、编码、数值格式），而 digest 是**跨进程可复现**的校验值，测试向量需要固定输入。
- 建议：冻结前列出参与计算的字段清单与序列化规则（或注明「由实现 Task 固化 canonical JSON 并纳入测试向量，本节只冻结语义」）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r3，`reviewer_kind: subagent`，独立上下文；r1/r2 亦由我出具（如实披露）。
- **未参与** C-04b 撰写（作者 = DSH）、未参与 ADJ-001 / M2-C1 / C-01b 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-04b / ADJ-001 / M2-C1 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- P1-2 的判定**直接对照 ADJ-001 PD-02 `:60-61` 原文**（有序集合绑定）与 §6.1 `:78`，未引用 r2 结论作为依据。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == fc670f248`；被审文件 blob `90cc3fb62`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理）。
- 未执行任何冻结或代码改动（草案为 DRAFT；冻结须 C-01b 先冻结 + `G-DELETE-CONTRACT` 关闭 + D04/D07 裁决 + DSH 批准 2.11 minor + M2-C1 扩展独立 Task）。
- 未审计 M2-C1 §5.11 之外的协议面（§8 ErrorEnvelope、§6 projections 只在涉及处引用）。
- 未验证 `PreviewPermanentDeleteBooks` / digest 算法的 Core 实现可行性（当前无实现，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3 非阻断；3 处核实全部到位）。
