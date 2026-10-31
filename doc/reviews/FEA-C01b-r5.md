---
document_id: FEA-C01b-r5
kind: independent_review
task_id: FEA-C01b
round: 5
scope: very-narrow（只核 r4 findings + 是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams 独立上下文 teammate（r5 派发任务；同一 teammate 出具过 r1–r4，但未参与 C-01b 草案 v1–v5 的撰写与修订，未参与 AD-003 / ADJ-001 / FEA-01 撰写，未参与任何实现）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-C01b-r4（changes_requested：P0×0 / P1×1 / P2×4）
reviewed_document: doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md
reviewed_sha256: ab3fb2d13a81539e759fd1e5de95f4ef2fd1fc837acd143b2e8811f21129f87a
reviewed_blob_sha256: ab3fb2d13a81539e759fd1e5de95f4ef2fd1fc837acd143b2e8811f21129f87a
reviewed_sha256_basis: "git cat-file blob HEAD:doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md 原始字节（LF，18190 B）；工作树副本字节完全一致（同 18190 B / 同一 SHA-256）"
reviewed_head: 56d2c9151
reviewed_head_full: 56d2c9151d26a141c2e407d9200e19fdb53a5342
reviewed_document_v5_at: 56d2c9151
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为不阻断冻结的已知限制（图例写法未在正文落地、依据行未链 r4、§5 v4 行的历史归属），已在 §3 登记；按 r5 派发口径可 `approved`"
captured_at: 2026-11-01T03:12:51+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C01b 存储契约（草案 v5）第 5 轮（极窄面确认）

**本报告不是** ADR、契约冻结、Task 释放、实现验收或集成批准。本轮为**极窄面**确认：只核对 r4 的 5 条 findings（1 P1 + 4 P2）在 v5 中的处置，以及 v5 是否引入新问题。`verdict: approved` 只表示**文本层面**已可进入冻结条件流程；它不冻结契约、不满足 §4 的其余冻结前置（AD-003 `G-REVIEW` 收口、用户确认 AD-002 责任表与哨兵口径、`check.ps1` PASS），也不释放任何实现 Task。

被审对象：`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md`（DRAFT v5，137 行 / 18190 B），LF blob SHA-256 `ab3fb2d1…1129f87a` —— 与派发方给出值**一致**，工作树与 blob **字节完全相同**。HEAD = `56d2c9151`。

**方法与边界**：本轮以 `git diff e95a09609 56d2c9151 -- <草案>` 的**完整补丁**为核对基础（v4→v5 仅 7 处改动，见 §2 表），并对 r4 新提出的每一处代码引用逐行读取验证（§4）。`src/` 与 `apps/` 在 `e95a09609..56d2c9151` **零改动**（该提交只改 `doc/`），故既往代码行号结论继续有效。

---

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断已知限制）。**

| 维度 | 结果 |
|---|---|
| r4 的唯一 P1（`:6` 依据链 + 三处自述一致） | **已处置** ✅ `:6` 已补 `[r2]`/`[r3]` 链接；`:3`（v5 / r1–r4 已过 / P0×0·P1×1·P2×4）、§4.1（`r1/r2/r3/r4 已跑，v5 修订后需 r5`）、§5（v5 行齐备）三处自述**互相一致** |
| r4 P2-1（SC-20 标签错位） | **已处置** ✅ `:206` 改为「reparse 预拒，`:225-226` 抛 `E_REPARSE`」、`:351` 改为「identity 复核，`:352` 抛 `E_IDENTITY_CHANGED`」、新增 `:641`/`:766`（`ManagedRootTrust` 可信根）—— **四处新引用逐行核对全部命中且语义正确**（§4） |
| r4 P2-2（SC-30 标签错位） | **已处置** ✅ 软删 → `library/service.py:97-99`、`trash.py:119`；页级 purge → `trash.py:196`；项目级永久删除事务 → `library.py:1069-1101`（并明确标注「非软删路径」）—— **四处逐行核对全部命中**（§4） |
| r4 P2-3（§5 行序） | **已处置** ✅ 现为 v1→v2→v3→v4→v5（`:133-137`） |
| r4 P2-4（图例写法未收敛） | **部分** ⚠️ —— 图例（`:23`）改为「拆分写法**统一为** `[A：… / B：…]` 形式」，但正文 6 条（SC-03/08/09/12/30/39）**无一处采用该形式**；实测仍是变体写法。按 r5 派发口径登记为**非阻断已知限制**（§3 L-1） |
| 是否引入新问题（草案） | **无**：v4→v5 的 7 处改动全部落在控制字段/证据/图例措辞/变更记录，**条款义务文本零改动** → 覆盖仍 **38/38**、出处仍 **40/40**、ID 仍 **40**、新增语义 **0** |
| 草案外提示 | `doc/00_INDEX.md:35` 仍写「v4…待 r4 窄面复核」且只链 r1/r2/r3（r4 报告已入库）→ 属 DSH 单点更新面，见 §3 D-1 |

---

## 2. r4 findings 逐条核对（1 P1 + 4 P2）

| ID | r4 等级 | r4 要求 | v5 实际 | 判定 |
|---|---|---|---|---|
| **P1-1** | P1 | `:6` 补 `[r2]`/`[r3]`；`:3`、§4.1、§5 三处自述一致（v5 / r1–r4 已过 / 需 r5） | `:6` = 「…[FEA-C01b r1 复核](../reviews/FEA-C01b-r1.md)、**[r2](../reviews/FEA-C01b-r2.md)、[r3](../reviews/FEA-C01b-r3.md)**」✅；`:3` = 「DRAFT **v5** / 已过 **r1、r2、r3、r4** 独立复核（均 `changes_requested`，P0×0 / P1×1 / P2×4 open）」✅；`:122` = 「**r1/r2/r3/r4 已跑，v5 修订后需 r5 极窄面确认**」✅；§5 v5 行（`:137`）✅ | **已处置** ✅ |
| P2-1 | P2 | SC-20 证据标签纠正（`:206` reparse 预拒 / `:351` identity 复核 / `:641`·`:766` 可信根） | `:74` 已按此改写，并补充了 `:225-226 抛 E_REPARSE`、`:352 抛 E_IDENTITY_CHANGED` | **已处置** ✅（4 处新引用全部核对通过，§4） |
| P2-2 | P2 | SC-30 标签纠正（软删 `library/service.py:97-99`/`trash.py:119`、页级 `trash.py:196`、项目级 `library.py:1069-1101`） | `:94` 已按此改写，并加注「（非软删路径）」以免二次误读 | **已处置** ✅（4 处新引用全部核对通过，§4） |
| P2-3 | P2 | §5 行序恢复 v1→v2→v3→v4→v5 | `:133` v1 → `:134` v2 → `:135` v3 → `:136` v4 → `:137` v5 | **已处置** ✅ |
| P2-4 | P2 | 图例与实际写法收敛（或登记等价形式 / 判据补第 5 态） | 图例 `:23` 改为「统一为 `[A：… / B：…]` 形式」；但 6 条拆分条款实际写法未变（SC-03「拆：…；…」、SC-08「备份清单：[现行]；容量预览：[新增]」、SC-09「拆分：…；…」、SC-12「拆分：前半 [现行] / 后半 [新增]」、SC-30「[现行]（…）；…属 [新增]」、SC-39「[现行]（双读）；…为 [新增]」）；`[文档级约束]` 在 SC-06/15/16 仍无方括号；判据（`:24`）仍只 4 态、缺 `[现行→退役]` | **部分** ⚠️ → **非阻断已知限制 L-1** |

**统计**：已处置 4 / 部分 1（P2-4，非阻断）/ 未处置 0；**P1 已清零**。

---

## 3. 已知限制（非阻断，登记备案）

#### L-1 (P2) — 图例声明「统一为 `[A：… / B：…]` 形式」，但正文 6 条无一处采用该形式

- 位置：草案 `:23`（图例）↔ `:36`（SC-03）、`:46`（SC-08）、`:47`（SC-09）、`:56`（SC-12）、`:94`（SC-30）、`:108`（SC-39）。
- 事实：v5 只改了图例措辞（由「如 SC-08/12/30/39」的举例式改为「统一为 `[A：… / B：…]` 形式；用于 SC-03/08/09/12/30/39」），**未改写任何条款的状态单元格**；6 条拆分条款仍各用变体。「文档级约束」在 SC-06/15/16 未加方括号；判据（`:24`）未覆盖第 5 态 `[现行→退役]`。
- 影响：纯可读性/可机械统计性问题，不产生任何语义或代码事实上的误述（各状态均可从上下文唯一判读）。
- 建议（可在冻结提交或其后修）：二选一 —— ①把 6 条状态单元格改写为 `[A：… / B：…]`；②把图例措辞退回「建议形式」并列出已用的等价写法。**不阻断冻结**。

#### L-2 (P2) — `:6` 依据链到 r1/r2/r3，未链 r4（r4 报告已入库）

- 事实：r4 报告 `doc/reviews/FEA-C01b-r4.md` 已在 Git 中（`git ls-files` 命中），`:3` 亦自述「已过 r4」，但 `:6` 依据行止于 r3。**r5 派发口径只要求 r2/r3，故不构成 P1**。
- 建议：冻结提交时补 `[r4](../reviews/FEA-C01b-r4.md)`，使依据链与状态行自述完全对齐。

#### L-3 (P2) — §5 的 v4 行仍把「依据链 r2/r3」记在 v4 名下（实际完成于 v5）

- 位置：草案 `:136`（v4 行）↔ `:6`（v5 才补链）。
- 事实：r4 的 P1-1 曾指出该行的不实陈述；v5 补上了链接，但未在 v4 行加注，因此变更记录仍把该完成动作归属到 v4。
- 建议：v4 行括号内加「（依据链 r2/r3 于 v5 补齐）」，或在 v5 行明确「补链」以免历史归属失真。**不影响任何条款义务**。

#### D-1（草案外，DSH 单点面）— `doc/00_INDEX.md:35` 未同步 v5/r5

- 现状：仍写「存储契约（SC-01…SC-39，**v4** 已处置 r1/r2/r3 全部 findings，**待 r4 窄面复核**）」，且只链 r1/r2/r3。r4 报告已入库。
- 属 DSH 单点更新面，本任务禁改；建议在登记 r5 报告时一并更新为 v5/待冻结并补 r4/r5 链接。

---

## 4. v4→v5 全量改动与代码引用核对

### 4.1 `git diff e95a09609 56d2c9151` 的结果（7 处，全部为文档层）

| # | 位置 | 改动 | 判定 |
|---|---|---|---|
| 1 | `:3` | 状态行 v4→v5，补 r4，open 计数 P2×6→P2×4 | ✅ 一致 |
| 2 | `:6` | 依据行补 `[r2]`、`[r3]` | ✅（L-2 提示可再补 r4） |
| 3 | `:23` | 图例拆分写法措辞改为「统一为 `[A：… / B：…]` 形式」 | ✅ 措辞已改（正文未同步 → L-1） |
| 4 | `:74` | SC-20 证据标签纠正 + 补 `:225-226`、`:352`、`:641`、`:766` | ✅ 全部核对通过（§4.2） |
| 5 | `:94` | SC-30 证据标签纠正（软删/页级 purge/项目级永久删除分列） | ✅ 全部核对通过（§4.2） |
| 6 | `:122` | §4.1 改为「r1/r2/r3/r4 已跑，v5 修订后需 r5 极窄面确认」 | ✅ |
| 7 | `:133-137` | §5：v4 行移至 v3 之后 + 新增 v5 行 | ✅ 行序正确 |
| — | 其余 | **无任何改动** → 条款义务文本、状态列、判据、§3 验证表全部未动 | ✅ 无新增语义 |

### 4.2 r4 新增代码引用逐行核对（8 处，全部命中且语义正确）

| 引用 | 草案括注 | 实际内容 | 判定 |
|---|---|---|---|
| `handle_resolver.py:225` | reparse 预拒 | `if attributes & FILE_ATTRIBUTE_REPARSE_POINT:` | ✅ |
| `handle_resolver.py:226` | 抛 `E_REPARSE` | `raise TypedResourceChannelError(E_REPARSE)` | ✅ |
| `handle_resolver.py:352` | 抛 `E_IDENTITY_CHANGED` | `raise TypedResourceChannelError(E_IDENTITY_CHANGED)` | ✅ |
| `handle_resolver.py:641` | `ManagedRootTrust` 可信根 | `class ManagedRootTrust:` | ✅ |
| `handle_resolver.py:766` | 可信根身份变化 | `E_IDENTITY_CHANGED, "managed root identity changed"` | ✅ |
| `library/service.py:97-99` | 软删 | `def delete_book(...)` → `book.soft_delete()` | ✅ |
| `trash.py:119` | 软删 | `def soft_delete_pages(` | ✅ |
| `trash.py:196` | 页级 purge | `def purge_batch(self, batch_id: str) -> None:` | ✅ |
| `library.py:1069-1101` | 项目级永久删除事务（非软删） | `"DELETE FROM artifact_revisions WHERE artifact_id IN ("` … | ✅ |

另复核 r4 已验的其余引用未受本次改动影响（`schema.py:290-323`、`nmbak.py:184/660-665/50-53`、`cleanup.py:16-20/41`、`AppOptions.cs:65-66`、`StartupSelfCheck.cs:8-95,42`、`HostRuntime.cs:746`、`HostCommandRegistry.cs:133`）；`src/`+`apps/` 零改动，故无需重验。

---

## 5. 对账与出处复验（沿用 + 计数）

| 项 | r4 结论 | v5 复验 | 变化 |
|---|---|---|---|
| AD-003 §3.1–§3.8 边界覆盖 | 38/38 | 38/38 | 无（条款正文零改动） |
| 条款 ID 数 | 40 | 40 | 无 |
| 逐条出处 | 40/40 | 40/40 | 无 |
| 新增语义 | 0 | 0 | 无 |
| 状态分布 | 纯 [现行] 7 / [现行→退役] 1 / [新增] 18 / [未实现] 4 / 拆分 6 / 文档级约束 4 | 同左 | 无 |

---

## 6. 冻结可行性

- **本轮满足 §4 冻结条件第 1 条**：独立复核（r1–r5）已完成，本报告 `approved`，确认草案与 AD-003/ADJ-001 一致、无新增语义。
- **仍未满足（不在本报告范围，且非草案文本可解）**：② AD-003 自身 `G-REVIEW` 收口（AD-003 §5 仍 `ADDRESSED_PENDING_R2`；`doc/reviews/` 仍无 AD-003 独立 Review 产物）；③ 用户确认 AD-002 责任表与哨兵口径（`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md:28` 的 `Managed Copy` 行 + 顶部横幅归口）；④ `check.ps1` PASS（机械检查）。
- **建议的冻结前收尾（可选项，不阻断）**：L-1（图例写法）、L-2（补 r4 链接）、L-3（v4 行归属注记）、D-1（`00_INDEX.md:35` 同步 v5/r5）。
- **`approved` 的效力边界**：仅表示**文本层面**可进入冻结条件流程；不冻结契约、不释放 Source 线（FEA-08/09/11/12/13）、不满足 C-01b 关闭条件。

---

## 7. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams 独立上下文 teammate）身份出具 r5。**r1–r4 亦由我出具**，如实披露；独立性判据落在**与被审文档作者分离**：我未参与 C-01b 草案 v1–v5 的撰写与修订，未参与 AD-003 / ADJ-001 / FEA-01 / 方案文本撰写，未参与 `src/**`、`apps/**` 任何实现。v5 的修订由 DSH 完成。
- 本轮**只读**：唯一写入为新建本报告。未修改草案 / AD-003 / ADJ-001 / FEA-01 / INDEX / 任何 Task / STATUS / PLAN；未 `git add`/`commit`/`push`；未触碰真实数据根；未使用仓外临时目录。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为**空**；草案工作树与 Git blob 字节完全相同（18190 B、同 SHA-256）。报告落盘后 `git status` 为 `?? doc/reviews/FEA-C01b-r5.md`（**我新建**）+ `?? doc/reviews/REALUSE-DATA-SAFETY-12-review.md`（**非我写入**：`reviews/` 写域下另一条并行线的 teammate 产物，我全程未打开或写入该文件）；草案字节在落盘后复核仍为 `ab3fb2d1…1129f87a`（未变）。
- 所有事实均附可复核路径与行号；r4 仅用于「原要求是什么」的对照，本报告判定均在本轮重新核验（含 v4→v5 全量补丁与 8 处新引用逐行读取）。

---

## 8. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建；代码证据均为**静态核对**（行号存在性、语句内容），未执行。
- 未重跑 `tools/governance/check.ps1`（§4 冻结条件第 4 条仍待 DSH 执行；本轮不以其替代语义审查）。
- 未在真实数据根执行任何操作；`derived/`/managed 体量数据沿用既有证据 `verification/REALUSE-DATA-SAFETY-6/ac2-derived-realdata.json`，未重盘。
- 未验证 Host / V2 运行行为、`--shell=legacy` 实机回退、Windows 回收站桥（零实现）。
- 未重做逐条语义对账（极窄面范围；仅通过 v4→v5 全量补丁确认条款义务文本零改动，并复验计数）。
- 未审 FEA-08/09/11/12/13 实现范围与 AC；未审 FEA-01 其余 C-02…C-12。
- 未对 AD-003 / ADJ-001 自身做独立 Review（其 `G-REVIEW` 仍 `ADDRESSED_PENDING_R2`，不在本报告范围）。
- 未更新 `doc/00_INDEX.md`（DSH 单点更新面；其 `:35` 的过期状态见 D-1）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3 非阻断已知限制；r4 处置：4 已处置 / 1 部分（非阻断）/ 0 未处置）。
