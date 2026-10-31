---
document_id: FEA-C01b-r4
kind: independent_review
task_id: FEA-C01b
round: 4
scope: narrow（只核 r3 findings 处置 + 是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams 独立上下文 teammate（r4 派发任务；同一 teammate 出具过 r1/r2/r3，但未参与 C-01b 草案 v1–v4 的撰写与修订，未参与 AD-003 / ADJ-001 / FEA-01 撰写，未参与任何实现）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-C01b-r3（changes_requested：P0×0 / P1×1 / P2×6）
reviewed_document: doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md
reviewed_sha256: 6a2873fc2fa878fa3c396682b2078d7a5abfa71be6800ddca2af56e0b672e663
reviewed_blob_sha256: 6a2873fc2fa878fa3c396682b2078d7a5abfa71be6800ddca2af56e0b672e663
reviewed_sha256_basis: "git cat-file blob HEAD:doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md 原始字节（LF，17378 B）；工作树副本字节完全一致（同为 17378 B / 同一 SHA-256，0×CR）"
reviewed_head: e95a09609
reviewed_head_full: e95a09609ad1a852a53fad04d821557996dfd6c8
reviewed_document_v4_at: e95a09609
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 4
captured_at: 2026-11-01T03:10:17+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C01b 存储契约（草案 v4）第 4 轮（窄面）

**本报告不是** ADR、契约冻结、Task 释放、实现验收或集成批准。它是**窄面**复核：只核对 r3 的 7 条 findings（1 P1 + 6 P2）在 v4 中的处置，以及 v4 是否引入新问题；不重新审查已连续三轮判定一致的语义对账（该结论沿用并在 §5 复验其计数未变）。

被审对象：`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md`（DRAFT v4，136 行 / 17378 B），LF blob SHA-256 `6a2873fc…0b672e663` —— 与派发方给出值**一致**，且工作树字节与 blob **完全相同**（17378 B、同 hash、0×CR）。HEAD = `e95a09609`，草案在该提交内。

**前置事实**：`src/` 与 `apps/` 在 r3 固定点 `3bcbb2565` 与本轮 `e95a09609` 之间**零改动**（该提交仅改 `doc/`），故 r3 及更早的代码行号核验继续有效；本轮另对 v4 新增/修改的 **11 处**引用逐条抽查（§6），发现 **2 处标签错位**（P2-1 / P2-2），未发现行号失效。

---

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / P1 × 1 / P2 × 4）。**

| 维度 | 结果 |
|---|---|
| r3 的 P1（P1-1 控制字段） | **部分处置（2/3）**：`:3` 状态行 ✅（已是 v4 + 「已过 r1、r2、r3 均 changes_requested」+「P0×0 / P1×1 / P2×6 open」）、§4.1 ✅（已改「r1/r2/r3 已跑，v4 修订后需 r4」）；❌ **`:6` 依据行仍只链 r1，未链 r2/r3**，而 §5 v4 行却声称「依据链 r2/r3」已做 |
| r3 的 6 条 P2 | **已处置 5**（P2-1 / P2-2 / P2-4 / P2-5 / P2-6）、**未处置 1**（P2-3 图例与判据格式，§2 说明） |
| 是否引入新问题 | **有，均为 P2**：SC-20 的证据行号与括注标签**错位**（`:206` 标「可信根」实为 reparse 预拒；`:351` 标「reparse 拒绝」实为 identity 复核）；SC-30 的「软删/GC：`library.py:1069-1101`」标签错位（该区间是项目级**永久删除**事务）；§5 变更记录**时间顺序倒置**（v4 行排在 v3 行之前） |
| 语义/覆盖 | **无新增语义、无遗漏**：条款正文本次未改动（仅状态/证据/变更记录），覆盖仍 **38/38**、出处仍 **40/40** |
| `doc/00_INDEX.md` | 已同步 ✅（`:35` 现为「SC-01…SC-39，v4 已处置 r1/r2/r3 全部 findings，待 r4 窄面复核」并三链 r1/r2/r3） |

**一句话**：v4 把 r3 的 6 条 P2 处理了 5 条，实质内容与 r3 判断一致；**唯一 P1 残留是 `:6` 依据行的两个链接**（外加 §5 一句措辞），加上 3 条新 P2（其中 2 条是证据标签错位、1 条是变更记录排序）。**全部为文档层、零内容风险**；补齐后 r5 会是极窄面确认。

---

## 2. r3 findings 逐条处置核对（7 条：1 P1 + 6 P2）

| ID | r3 等级 | r3 的具体要求 | v4 实际 | 判定 |
|---|---|---|---|---|
| **P1-1** | **P1** | ①`:3` 状态行改 v4 且写明 r1/r2/r3 已过与 P0×0/P1×1/P2×6；②`:6` 依据链 r2/r3；③§4.1 改「r1/r2/r3 已跑，v4 修订后需 r4」 | ①✅ `:3` = 「DRAFT **v4** / 已过 **r1、r2、r3** 独立复核（均 `changes_requested`，**P0×0 / P1×1 / P2×6 open**）/ 未冻结」；③✅ `:122` = 「**r1/r2/r3 已跑，v4 修订后需 r4 窄面复核**」；②❌ `:6` 依据行仍为「AD-003、ADJ-001、方案 r4、FEA-01、**FEA-C01b r1 复核**」—— **只链 r1**，r2/r3 既无链接也无提及 | **部分（2/3）** ⚠️ → 残留 P1 |
| P2-1 | P2 | SC-09 拆「禁止自动执行 [文档级约束] / 盘点与预览任务 [新增]」 | `:47` = 「拆分：禁止自动执行 [文档级约束]；盘点与可预览清理任务 [新增]（能力缺位）」+ 验证列「当前无盘点/预览任务面；实现 Task 须补」 | **已处置** ✅ |
| P2-2 | P2 | SC-10b 旁注纠正（Run 快照结构存在、`nmbak.py:184` 整库打包、真实缺口=不含上下文页、补 `trash-manifest.json` 白名单证据） | `:54` 已逐项写入：「`settings/*.json`、`catalog.sqlite` 未入包；`managed/trash-manifest.json` 被 `nmbak.py:660-665` 白名单排除、草稿 journal 未入包；Run 快照结构**已存在** `schema.py:290-323`，真实缺口是『快照不含上下文页内容』」；验证列补「`nmbak.py:184` 打包整库（Run 快照随库入包）」 | **已处置** ✅（4 处行号本轮全部命中，§6） |
| P2-3 | P2 | 图例/判据与实际写法收敛（4 种拆分写法、"文档级约束"无方括号、判据缺第 5 态） | `:18-24` 图例与判据**未改**；SC-09/SC-12 改用「拆分：…」前缀（略有收敛），但 SC-08「备份清单：[现行]；容量预览：[新增]」、SC-30「[现行]（…）；… 属 [新增]」、SC-39「[现行]（双读）；引用页部分为 [新增]」仍各异；SC-06/15/16 的「文档级约束」仍**无方括号**；判据仍只 4 态、无 `[现行→退役]` | **未处置** ⚠️（r4 派发清单亦未点名此条，故不阻断冻结；见 P2-4） |
| P2-4 | P2 | SC-20/30/36/12/24 证据补文件:行 | 五条均已补：SC-20 `handle_resolver.py:284-320/206/351`（`:74`）、SC-30 `library.py:1069-1101`（`:94`）、SC-36 `AppOptions.cs:65-66`（`:105`）、SC-12 `nmbak.py:50-53`（`:56`）、SC-24 `cleanup.py:16-20`（`:78`） | **已处置** ✅（但其中 2 处括注标签与实际行内容不符 → 新 P2-1 / P2-2） |
| P2-5 | P2 | §5 变更记录补 old→new | `:136` v3 行已改为「状态变更（old→new）：SC-10 [新增]→拆分…；SC-09 [新增]→[文档级约束]；SC-17 [新增]→（保持）；SC-06 [现行]→[文档级约束]；SC-15/16 [现行]→[文档级约束]；SC-03 [现行]→拆分；SC-38 证据换载」 | **已处置** ✅（但该行被排在 v4 行之后 → 新 P2-3） |
| P2-6 | P2 | SC-18/21/31 按判据重标 `[未实现]` | `:67` SC-18 `[未实现]`（`DatabaseId` 无结构）、`:75` SC-21 `[未实现]`（`SourceAccessRegistry` 无结构）、`:95` SC-31 `[未实现]`（回收站桥与授权流程无结构）；与 SC-22 一致，判据（`:24`）自洽 | **已处置** ✅ |

**统计：已处置 5 / 部分 1（P1-1）/ 未处置 1（P2-3）。**

---

## 3. 派发方 7 项复核重点的逐项答复

| # | 重点 | 答复 |
|---|---|---|
| 1 | **P1-1 三处控制字段** | `:3` ✅、§4.1 ✅、**`:6` ❌ 未链 r2/r3**（且 §5 v4 行声称「依据链 r2/r3」已做 → 自述与事实不符） |
| 2 | **P2-2 SC-10b 旁注** | ✅ 已纠正，且我自行核对：`schema.py:290` = `CREATE TABLE pipeline_runs (`、`:323` = `UNIQUE (pipeline_run_id, target_order)`（`pipeline_run_targets` 内）→ 区间成立；`nmbak.py:184` = `self._write_database(workdir / DB_NAME)`；`nmbak.py:660-665` = 「unexpected managed member」拒绝分支 → 三处证据**真实** |
| 3 | **P2-1 SC-09 拆分** | ✅ 已拆，且括注了「能力缺位」 |
| 4 | **P2-3/P2-4 证据文件:行** | 五条均已补；抽查 4 处：`cleanup.py:16-20` ✅（never-cleanable 清单）、`nmbak.py:50-53` ✅（包成员常量，无凭据项）、`AppOptions.cs:65-66` ✅（`--shell=legacy` one-release rollback）、`schema.py:290-323` ✅、`nmbak.py:184` ✅；**但 2 处括注标签错位**（SC-20、SC-30）→ P2-1 / P2-2 |
| 5 | **P2-5 变更记录 old→new** | ✅ 已补（v3 行），但该行被移到 v4 行**之后**，时间顺序倒置 → P2-3 |
| 6 | **P2-6 SC-18/21/31 重标** | ✅ 三条均改 `[未实现]` 并与 SC-22 及判据（`:24`）一致 |
| 7 | **是否引入新问题 / verdict** | 新问题：3 条 P2（SC-20 标签错位、SC-30 标签错位、§5 排序）+ 残留 1 条 P2（图例格式，r3 P2-3 未处置）。**无新增语义、无遗漏、无行号失效**。因 P1-1 未完成 → `changes_requested`；补齐后可 `approved` |

---

## 4. Findings

### P1（残留）

#### P1-1（残）(P1) — `:6` 依据行仍未链 r2/r3，而 §5 v4 行声称已做

- 位置：草案 `:6`（依据行）、`:135`（§5 v4 行）。
- 事实：
  1. `:6` = 「依据：AD-003、ADJ-001、方案 r4（`74a772167`）、FEA-01 契约清单、**[FEA-C01b r1 复核]**」—— 只链 r1；r2（`doc/reviews/FEA-C01b-r2.md`）与 r3（`doc/reviews/FEA-C01b-r3.md`）**均未链接、也未在依据行提及**（两份报告均已入库，`git ls-files` 可查）。
  2. 同一份文件的 `:135` v4 行却写「P1-1 文档控制字段同步（状态行 v4、**依据链 r2/r3**、§4.1 改『需 r4』）」—— 声明了一件未发生的事。
- 影响：r3 的 P1-1 是**三分项要求**（状态行 / 依据链 / §4.1），本项属其中一项；且 v4 的变更记录对自身完成度作了不实陈述。冻结后这些字节不可变，一条自述不实的变更记录会被永久固化在契约里。
- 建议（两处一行级）：①`:6` 改为「…[r1](../reviews/FEA-C01b-r1.md) / [r2](../reviews/FEA-C01b-r2.md) / [r3](../reviews/FEA-C01b-r3.md) 复核」；②`:135` 保持如实的措辞（若已完成则保留，否则删除「依据链 r2/r3」字样）。

### P2

#### P2-1 (P2，新) — SC-20 的证据行号与其括注标签错位

- 位置：草案 `:74`（SC-20 验证列）：「`handle_resolver.py:284-320`（identity/size/digest）、`:206`（**可信根**）、`:351`（**reparse 拒绝**）」。
- 事实（本轮逐行核对）：
  - `:284-320` ✅ 正确（`:284` 为该方法的 docstring「Open a file and verify its handle-derived scope, identity and size」；digest 计算在其后）；
  - `:206` = `def _preopen_reparse_walk(root: Path, rel_path: str) -> None:`，`:207` 起 docstring 为「Early rejection of a reparse component」、`:225-226` 抛 `E_REPARSE` → 该行是**reparse 预拒**，不是「可信根」；
  - `:351` = `if _identity_of(handle) != (grant.facts.volume_serial, grant.facts.file_index):` → 该行是**identity 复核**（不符抛 `E_IDENTITY_CHANGED`，`:352`），不是「reparse 拒绝」；
  - 「可信根」的真实位置：`handle_resolver.py:641`（`class ManagedRootTrust`）、`:766`（`E_IDENTITY_CHANGED, "managed root identity changed"`）。
- 影响：r3 的 P2-4 目标是「证据可核对」，但两处括注指向了错的机制；读者按标签复核会得出错误结论（好在两行都真实存在且都与本条款相关，属标签错位而非捏造）。
- 建议：改为「identity/size/digest：`:284-320`；reparse 预拒：`:206-226`；可信根（`ManagedRootTrust`）：`:641`、`:766`；identity 复核：`:351-352`」。

#### P2-2 (P2，新) — SC-30 的「软删/GC」证据行号指向的是项目级永久删除事务

- 位置：草案 `:94`（SC-30 验证列）：「软删/GC：`library.py:1069-1101`」。
- 事实：`library.py:1069` 起是 `DELETE FROM artifact_revisions …` / `DELETE FROM media_artifacts …` 等语句，位于**项目级（Book）永久删除事务**内 —— 与 ADJ-001 §2 对 `library.py:1069-1101` 的描述一致（「在事务内直接删除 regions/region_revisions/artifact_revisions/pages/books 等（含保护数据）」）。该区间是 SC-30 的「**用户显式彻底删除**」路径，不是「软删/GC」。
- 软删的真实位置：`src/application/library/service.py:97-99`（`delete_book` → `book.soft_delete()`）、`src/application/maintenance/trash.py:119`（`soft_delete_pages`）；页级 purge 在 `trash.py:196`。
- 影响：标签错位会让复核者把「软删不触原文件」的证据挂到永久删除事务上；结论（不触原文件）仍成立，但证据链不准确。
- 建议：改为「软删：`library/service.py:97-99`、`trash.py:119`；页级 purge：`trash.py:196`；项目级彻底删除事务：`library.py:1069-1101`」。

#### P2-3 (P2，新) — §5 变更记录时间顺序倒置（v4 行排在 v3 行之前）

- 位置：草案 `:133-136`：v1（`:133`）→ v2（`:134`）→ **v4（`:135`）→ v3（`:136`）**。
- 影响：变更记录是审计链；顺序倒置会使「最新状态」与「上一轮改动」的阅读顺序错乱（且 v4 行引用了「P1-1/P2-1…P2-6」编号，正好需要在 v3 行之后读）。
- 建议：把 v3 行移回 v4 行之前（按 v1→v2→v3→v4 排列）。

#### P2-4 (P2，残留 r3 P2-3) — 图例格式与判据仍未收敛

- 位置：草案 `:18-24`（图例/判据）↔ `:39/46/64/65`（「文档级约束」无方括号）、`:46` SC-08、`:94` SC-30、`:108` SC-39（三种不同拆分写法）、`:24` 判据（只 4 态，缺 `[现行→退役]`）。
- 事实：v4 仅在 SC-09/SC-12 改用「拆分：…」前缀，其余写法未统一；图例声明的 `[A：… / B：…]` 仍无一处实际采用；判据仍未覆盖 SC-24 使用的第 5 态。
- 影响：不影响语义，但使「按状态机械统计」不可稳定复现（本轮统计口径见 §5）。
- 建议：在冻结提交中一并统一（或把已用写法登记为等价形式并给判据补第 5 态）。**不阻断冻结**——r4 派发清单未将本条列为阻断项。

---

## 5. 对账复核（沿用 + 计数复验）

| 项 | r3 结论 | v4 复验 | 变化 |
|---|---|---|---|
| AD-003 §3.1–§3.8 边界覆盖 | 38/38 | 38/38 | 无（条款正文未改；SC-09 拆分不增 ID、SC-10a/10b 维持） |
| 条款 ID 数 | 40 | 40 | 无 |
| 逐条出处 | 40/40 | 40/40 | 无 |
| 新增语义 | 无 | 无（v4 仅改状态列/证据列/变更记录；条款义务文本零改动） | 无 |
| 状态分布（字面统计） | 纯 [现行] 7 / [现行→退役] 1 / [新增] 21 / [未实现] 1 / 拆分 5 / 文档级约束 4 | 纯 [现行] 7 / [现行→退役] 1 / **[新增] 18** / **[未实现] 4**（+SC-18/21/31）/ 拆分 6（SC-03/08/09/12/30/39）/ 文档级约束 4 | **仅状态重标**（P2-6 的设计结果，合计仍 40 ✔） |

**结论**：v4 未触碰任何条款的义务内容，语义层与 r3 判定一致；本次变化全部落在标注与证据层。

---

## 6. 证据与行号抽查（本轮，共 11 处）

| # | 引用 | 结果 |
|---|---|---|
| 1 | `schema.py:290` / `:323` | ✅ `CREATE TABLE pipeline_runs (` / `UNIQUE (pipeline_run_id, target_order)`（`pipeline_run_targets` 内） |
| 2 | `nmbak.py:184` | ✅ `self._write_database(workdir / DB_NAME)`（SQLite backup API 整库） |
| 3 | `nmbak.py:660-665` | ✅ 「unexpected managed member」拒绝分支（白名单外 managed 成员被判 `BACKUP_CORRUPT`） |
| 4 | `nmbak.py:50-53` | ✅ `MANIFEST_NAME`/`DB_NAME`/`SIDECAR_NAME`/`MANAGED_PREFIX`（包成员常量，无凭据项） |
| 5 | `cleanup.py:16-20` | ✅ never-cleanable 清单（用户源文件、current/pinned、Lock/任务可恢复性） |
| 6 | `AppOptions.cs:65-66` | ✅ `--shell=legacy` one-release rollback 注释 |
| 7 | `handle_resolver.py:284-320` | ✅ identity/size/digest 校验方法（含 docstring 与 digest 计算） |
| 8 | `handle_resolver.py:206` | ⚠️ **标签错位**：实为 `_preopen_reparse_walk`（reparse 预拒），非「可信根」→ P2-1 |
| 9 | `handle_resolver.py:351` | ⚠️ **标签错位**：实为 identity 复核（`E_IDENTITY_CHANGED`），非「reparse 拒绝」→ P2-1 |
| 10 | `library.py:1069-1101` | ⚠️ **标签错位**：实为项目级永久删除事务，非「软删/GC」→ P2-2 |
| 11 | 行号失效扫描 | **未发现失效**（`3bcbb2565..e95a09609` 只改 `doc/`；上述全部行号均存在且语义可核对） |

---

## 7. 冻结可行性

- **已满足**：语义层无新增/无遗漏（38/38、40/40）、r3 的 6 条 P2 中 5 条已处置、P2-6 重标使「冻结后仍需 BLOCKED 的条款」可判定、§3.8 完整、冻结条件含 AD-003 `G-REVIEW` 收口与 ADJ-001 `G-DELETE-CONTRACT` 依赖标注、`doc/00_INDEX.md` 已同步到 v4/r4。
- **仍缺**：① P1-1 残留（依据行两个链接 + §5 一句措辞）；② 3 条新 P2（两条证据标签错位、一条变更记录排序）建议同轮清；③ 残留 P2-4 可在冻结提交顺带统一。
- **判**：`changes_requested`。仅 P1-1 修复（2 个链接 + 1 句措辞）+ 3 条 P2 顺手改，即可 `approved`；`approved` 仍只表示文本层面可进入冻结条件流程 —— AD-003 `G-REVIEW` 收口（现仍 `ADDRESSED_PENDING_R2`、无独立 Review 产物）、用户确认 AD-002 责任表与哨兵口径、`check.ps1` PASS 仍是冻结前置。

---

## 8. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams 独立上下文 teammate）身份出具 r4。**r1/r2/r3 亦由我出具**，如实披露；独立性判据落在**与被审文档作者分离**：我未参与 C-01b 草案 v1–v4 的撰写或修订，未参与 AD-003 / ADJ-001 / FEA-01 / 方案文本撰写，未参与 `src/**`、`apps/**` 任何实现。v4 的修订由 DSH 完成。
- 本轮**只读**：唯一写入为新建本报告。未修改草案 / AD-003 / ADJ-001 / FEA-01 / INDEX / 任何 Task / STATUS / PLAN；未 `git add`/`commit`/`push`；未触碰真实数据根；未使用仓外临时目录。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为**空**；草案工作树副本与 Git LF blob 字节完全相同（17378 B、同 SHA-256、0×CR），无 EOL 差异。
- 所有事实均附可复核路径与行号；r3 只用于「原要求是什么」的对照，本报告的判定均在本轮重新核验（含 11 处行号逐行读取）。

---

## 9. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建；全部代码证据为**静态核对**（存在性、行号、语句内容），未执行。
- 未重跑 `tools/governance/check.ps1`（本轮未跑；该检查器不校验草案正文语义，且 r1 期在旧 head 的 PASS 只证明当时的机械条件）。
- 未在真实数据根执行任何操作；`derived/`/managed 体量数据沿用既有证据，未重盘。
- 未验证 Host / V2 运行行为、`--shell=legacy` 实机回退、Windows 回收站桥（零实现）。
- 未重做语义对账的逐条比对（窄面范围；仅复验计数与「条款正文未改」这一前提）。
- 未审 FEA-08/09/11/12/13 实现范围与 AC；未审 FEA-01 其余 C-02…C-12。
- 未对 AD-003 / ADJ-001 自身做独立 Review（`G-REVIEW: ADDRESSED_PENDING_R2`）。
- 未更新 `doc/00_INDEX.md`（本轮无需更新：DSH 已在 `e95a09609` 同步到 v4/r4；该文件属 DSH 单点更新面）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×4；r3 处置：5 已处置 / 1 部分 / 1 未处置）。
