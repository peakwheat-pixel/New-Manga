---
document_id: FEA-GOV-5-c04b-r2
kind: independent_review
task_id: FEA-GOV-5
round: 2
scope: narrow（只核 r1 的 5×P1 + 4×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-18；独立上下文；未参与 C-04b 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-5-c04b-review（r1：changes_requested，P0×0 / P1×5 / P2×4）
reviewed_head: c16359e6f
reviewed_head_full: c16359e6fc0e8d56f129a129e66ffd7df76d7212
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == c16359e6f）"
reviewed_document: doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md
reviewed_sha256: 5bde9c0182f675866016b44508bee6587897ed5c5b8796cd8c8b8f1a24b82315
reviewed_sha256_basis: "HEAD 的 LF blob（125 行，blob 9fd2c76af）"
baseline: "doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md §5（PD-01/02/04/07/08/09）/§6.1–§6.3 · doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.11.1–§5.11.5"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 2
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:08:51+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（窄面）：FEA-C04b 删除协议 v2 处置确认

**本报告不是** 冻结动作、不构成对 ADJ-001 / M2-C1 的修改，也不构成执行授权。本轮只核 r1 的 5×P1 + 4×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 2）。**

r1 的 **5 条 P1 中有 4 条完全闭环**（上限 20、码表补全、PD-01 三项、投影扩展 + 冻结顺序），**1 条在修正过程中改出了新的语义偏差**：

- **P1-1 ✅**：`bookIds: BookId[1..20]`、§1「批量上限 **20**」（引 §5.11.2 `:733`、§5.11.3 `:748`）✓。
- **P1-4 ✅（形状拆分到位，但引出 N-1）**：§2.0 已拆单条/批量两形状，明确「不得用单一 `inventory_digest` 同时服务两种形状」✓；但批量改用 `inventory_digests: { [bookId]: string }` 逐书 map，与 ADJ-001 PD-02 的「**绑定该有序集合**的清单摘要」语义不一致 → 见 **P1-2（新）**。
- **P1-2 ✅**：§1「错误表 12 行稳定码」+ §2.3 表 14 行沿用（12 稳定 + host 级 `CORE_UNAVAILABLE` + 兜底 `UNKNOWN`），并对 `BOOK_NOT_FOUND`/`BOOK_BUSY`/`BOOK_DELETE_CONFLICT` 标注「批量为 item code」✓；逐行 category/retryable 与 §5.11.3 `:746-758` 一致 ✓。
- **P1-3 ✅**：`DeletePreviewItem` 已补 `protection.manualRegionCount`、`protection.draftPageCount`、`contentSummary.deletedFiles`/`deletedBytes`，并单列「PD-01 三项（必须）」✓。
- **P1-5 ✅**：§2.4 给出 4 个扩展点（§5.11.3 表 / 两个 ErrorView / batch `items[].error_code` 白名单）+ 冻结顺序「先 §5.11.3 → 再 ErrorView → 最后 C-04b」+「M2-C1 修订走独立 Task」✓。
- **P2-1 ✅**：`BOOK_DELETE_CONFLICT` 触发已含「关系图/归属/安全枚举不一致（含 **PD-08 共享关系不可安全拆分**）」✓。
- **P2-2 ✅**：`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 的 category 已明确为 **`unavailable`**（retryable=true）✓。
- **P2-3 ✅**：§5 冻结条件已扩为 6 条，含「C-01b 已冻结」「DSH 批准 2.11 minor」「M2-C1 扩展由独立 Task 完成并复核」✓。
- **P2-4 ⚠️ 部分**：digest 格式已定义 `sha256:<64 hex>`（小写）✓；**`title` 字段的用途仍未注明** → 见 P2-2（新）。

| 核实项 | 结果 |
|---|---|
| 1. P1-1 上限 20 | **✅** |
| 2. P1-4 单条/批量拆分 | **✅**（但批量 digest 形状引出 P1-2） |
| 3. P1-2 码表 12+2 与 item code 标注 | **✅** |
| 4. P1-3 PD-01 三项 | **✅** |
| 5. P1-5 §5.11.5 扩展点 + 冻结顺序 | **✅** |
| 6. P2-1 PD-08 | **✅** |
| 7. P2-2 category = unavailable | **✅** |
| 8. P2-3 冻结条件三项 | **✅** |
| 9. P2-4 digest 格式 / title 用途 | **⚠️ 部分**（格式 ✓、title ✗） |
| 10. 新问题 + `check.ps1` | 新增 1 P1 + 2 P2；**`check.ps1` PASS(3 warnings) EXIT=0**；无代码改动、未 push |

---

## 2. 9 处核对明细

### 2.1（P1-1）上限 20 —— ✅

- §2.1 入参（`:39`）：「`{ bookIds: BookId[1..20] }`（非空、去重、**上限 20**，与 M2-C1 §5.11.2 一致）」；§1（`:18`）：「批量上限 **20**（`BookId[1..20]`；超过 → `BOOK_DELETE_BATCH_LIMIT_EXCEEDED`）｜§5.11.2 `:733`、§5.11.3 `:748`」✓ 与冻结契约一致。

### 2.2（P1-4）单条/批量形状拆分 —— ✅（引出 N-1）

- §2.0（`:27-32`）：
  - 单条 `PermanentlyDeleteBook` = `{book_id, confirm_permanent_delete: true}` + `inventory_digest: string` ✓（与 PD-02 单条一致）；
  - 批量 `PermanentlyDeleteBooks` = `{book_ids[1..20], confirmed_book_ids[1..20], confirm_count, confirm_permanent_delete: true}` + `inventory_digests: { [bookId]: string }`；
  - 「**不得**用单一 `inventory_digest` 字段同时服务两种形状；`confirmed_book_ids`/`confirm_count` 语义保持」✓。
- 问题在批量的 digest 形状（P1-2）。

### 2.3（P1-2）码表补全 —— ✅

- §2.3 沿用表 14 行：`INVALID_REQUEST`/`DUPLICATE_BOOK_ID`/`BOOK_DELETE_BATCH_LIMIT_EXCEEDED`/`BOOK_DELETE_BATCH_WHOLE_LIBRARY`/`BOOK_NOT_FOUND`/`BOOK_BUSY`/`BOOK_DELETE_CONFLICT`/`BOOK_DELETE_FAILED`/`BOOK_DELETE_CLEANUP_PENDING`/`BOOK_DELETE_BATCH_PREFLIGHT_FAILED`/`BOOK_DELETE_BATCH_CLEANUP_PENDING`/`PROTOCOL_VERSION_UNSUPPORTED`/`CORE_UNAVAILABLE`/`UNKNOWN` —— 覆盖 §5.11.3 `:746-758` 的 12 稳定码 + host 级 + 兜底 ✓；category/retryable 逐行对照一致（`BOOK_DELETE_FAILED` internal/unknown、两个 `*_CLEANUP_PENDING` internal/true、`BATCH_PREFLIGHT_FAILED` conflict/false ✓）。
- item code 标注 ✓（`BOOK_NOT_FOUND`/`BOOK_BUSY`/`BOOK_DELETE_CONFLICT` 在批量下为 item code）。
- 新增 2 码表格：`BOOK_DELETE_STALE_PREVIEW`（conflict/false）、`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（unavailable/true）✓ 与 ADJ-001 §6.3 一致。

### 2.4（P1-3）PD-01 三项 —— ✅

- `DeletePreviewItem`（`:41-42`）：`protection: { lockCount, currentRevisionId, pinnedRevisionIds[], activeRunIds[], draftPageCount, manualRegionCount }`、`contentSummary: { chapters, pages, artifacts, deletedFiles, deletedBytes }`；并单列「**PD-01 三项**（必须）① manualRegionCount ② draftPageCount ③ deletedFiles + deletedBytes」✓ 与 ADJ-001 PD-01 `:58` 的九项对齐（lock/current/pinned/artifact/Run + 新增三项 + `sharedFileRefs.otherProjectCount`）。

### 2.5（P1-5）§5.11.5 投影扩展 —— ✅

- §2.4（`:87-96`）：4 处扩展点 + 「冻结顺序：先扩 §5.11.3 表（M2-C1 修订）→ 再扩两个 ErrorView → 最后 C-04b 冻结。M2-C1 的修订须走独立 Task（不得由本草案直接改其字节）」✓ 可执行。

### 2.6（P2-1）PD-08 —— ✅

- §2.3 `BOOK_DELETE_CONFLICT` 行：「关系图/归属/安全枚举不一致（含 **PD-08 共享关系不可安全拆分**；批量为 item code）」✓。

### 2.7（P2-2）category = `unavailable` —— ✅

- 新增码表：`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE | **unavailable** | true | 清单计算失败（DB 错/临时故障）；零副作用」✓ 不再有「internal/unavailable」二义。

### 2.8（P2-3）冻结条件 —— ✅

- §5（`:113-118`）6 条：①独立复核 ②**C-01b 已冻结** ③`G-DELETE-CONTRACT` 关闭 ④**DSH 批准 2.11 minor** ⑤M2-C1 §5.11.3+§5.11.5 扩展已由独立 Task 完成并复核 ⑥`check.ps1` PASS ✓。

### 2.9（P2-4）digest 格式 / title 用途 —— ⚠️ 部分

- `:44`：「digest 格式 `sha256:<64 hex>`（小写）；格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW`」✓。
- **`title` 字段**（`:41`）无任何用途/边界说明 → 见 P2-2（新）。

### 2.10 `check.ps1` 与数据安全 —— ✅

- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2911 B / 80%、`REBASELINE_PLAN.md` 6554 B / 80%）；运行后 `git status` 为空 ✓。
- **提交面**：`c16359e6f` 只改 C-04b（+83/−36）与 r1 报告（+196）；`git diff --stat 59342d6bf..HEAD -- src apps` 为空；**未 push**（`c16359e6f` 非 `origin/main` 祖先）✓。
- 被审字节：C-04b @ `c16359e6f`，LF blob SHA-256 `5bde9c0182f6…1a24b82315`（125 行，blob `9fd2c76af`）。

---

## 3. Findings

### P1

#### P1-2（新）— 批量 digest 改为逐书 map，丢失 ADJ-001 PD-02 要求的「有序集合」绑定语义

- 位置：C-04b `:30`（§2.0 批量 `inventory_digests: { [bookId]: string }`）、`:40`（§2.1 预览出参 `inventoryDigests: { [bookId]: string }`）、`:92`（§2.4 批量投影说明）。
- 证据（ADJ-001，冻结语义）：
  - **PD-02**（`:61`）：「**批量**：沿用 `{book_ids, confirmed_book_ids, confirm_count, confirm_permanent_delete:true}` 的**有序绑定**，**追加** `inventory_digest`（**绑定该有序集合**的清单摘要）」——批量确认的摘要绑定的是**整个有序集合**；单条才是「绑定该 `book_id` 的清单摘要」（`:60`）。
  - **§6.1**（`:78`）：预览「返回清单 + `inventoryDigest` + `computedAt`」——提案为**单字段**摘要。
- 现文问题：逐书 map 以 `bookId` 为键，**重排 `book_ids` 顺序不会改变 map**，也无法检出「集合层面」的变化（例如同一组书、不同确认顺序），与 PD-02「有序绑定」的保护意图不符；同时把 PD-02 的集合级摘要替换为按书摘要，语义被弱化。
- 影响：PD-02/PD-04 的「确认后目标或保护被替换即拒绝」在批量场景下只覆盖「逐书内容变化」，不覆盖「顺序/集合绑定变化」；且与 ADJ-001 冻结语义不一致，冻结后需回头改 ADJ-001 才能自洽。
- 建议（三选一，推荐 A）：
  - **A（保留逐书 + 增加集合级）**：预览返回 `inventoryDigest`（集合级，绑定 `book_ids` 有序集合）+ `inventoryDigests`（逐书，供 UI 展示/逐书重预览）；批量确认同时校验集合级与逐书（缺失/不匹配 → `STALE_PREVIEW`）。
  - **B（恢复单字段）**：完全按 PD-02 —— 批量确认只带 `inventory_digest`（集合级），逐书摘要仅作 UI 数据。
  - **C（显式派生）**：定义批量摘要 = `sha256(bookIds 顺序拼接的逐书摘要)`，并在字段说明写清算法，使「逐书 map」可确定性重建集合级摘要（需注明重排会使摘要变化）。
  - 无论哪种，均需在 §2.2/§2.4 说明批量与单条摘要的**绑定对象差异**，并注明与 PD-02 的对应关系。

### P2

#### P2-1（新）— 批量下 `BOOK_DELETE_STALE_PREVIEW` 的返回位置二义（顶层 vs item）

- 位置：C-04b `:92`（§2.4 表「批量逐书 digest 不匹配时返回单条级码，**或**整体 `BOOK_DELETE_STALE_PREVIEW`」）。
- 问题：「或」留给实现二选一，而 §5.11.5 批量 `ErrorView` 的顶层码与 `items[].error_code` 是两套白名单，冻结后两种实现会产出不同形状。
- 建议：明确其一（推荐：顶层 `BOOK_DELETE_STALE_PREVIEW` + `phase:"preflight"` + 逐项 `items[]`，与 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` 的形状一致），另一取值从白名单移除。

#### P2-2（新）— `title` 用途未注明；「12 行 + 2 新增」计数表述与表内 14 行易误读

- 位置：C-04b `:41`（`title`）、`:57`（表头「**完整 12 行 + 2 新增**」）、`:61-76`（沿用表 14 行）。
- 问题：① `title` 是预览展示数据，但未注明「非保护输入、不参与 digest 计算、不随确认校验」（PD-01/PD-02 均无此项，需说明其来源与安全性）；② 表头写「12 行 + 2 新增」，而沿用表实为 14 行（12 稳定 + host 级 `CORE_UNAVAILABLE` + 兜底 `UNKNOWN`），建议改为「12 稳定 + 2 host 级/兜底」以免被当作码表数量错误。
- 建议：补一句 `title` 说明；表头/§1 计数口径统一。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与** C-04b 撰写（作者 = DSH）、未参与 ADJ-001 / M2-C1 / C-01b 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-04b / ADJ-001 / M2-C1 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- P1-2 的判定**直接引用 ADJ-001 PD-02 `:60-61` 与 §6.1 `:78` 原文**（非引用我 r1 结论），并注意 r2 派发口径本身也写了 `inventory_digests{}` —— 该设计在 ADJ-001 语义下需要上述 A/B/C 之一的补充说明才算自洽。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == c16359e6f`；被审文件 blob `9fd2c76af`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理）。
- 未执行任何冻结或代码改动（草案为 DRAFT；冻结须 C-01b 先冻结 + `G-DELETE-CONTRACT` 关闭 + D04/D07 裁决 + DSH 批准 minor）。
- 未审计 M2-C1 §5.11 之外的协议面（§8 ErrorEnvelope、§6 projections 只在涉及处引用）。
- 未验证 `PreviewPermanentDeleteBooks` / `inventory_digest(s)` 的 Core 实现可行性（当前无实现，属计划态）。
- 未核 ADJ-001 的 D05 裁定时间表与 `G-DELETE-CONTRACT` 关闭路径（只核现状 OPEN）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×2；9 处核实：8 到位 + 1 部分）。
