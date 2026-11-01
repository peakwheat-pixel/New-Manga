---
document_id: FEA-C14-r2
kind: independent_review
task_id: FEA-C14-DRAFT（r2）
round: 2
scope: 极窄面复核 r1 的 P1×5 + P2×4 处置（9 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 172eae3c8
reviewed_head_full: 172eae3c84c66950e1dbb306f72f43e88dd1bfd6
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 172eae3c8）；v1 基线 0ab75f990"
reviewed_documents:
  - doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md（v2，216 行，blob sha256 926a2dce…）
  - 对照：v1（0ab75f990，sha256 2c314aad…）；方案 `:419`–`:422`/`:432`/`:459`/`:461`/`:768`；AD-003 `:117`；C-01b SC-26/27/34/02/03/20/21/22；C-06 `:52`/`:64`/`:65`；C-04b `:43`/`:72`；ADJ-001 PD-08；FEA-C14-r1.md
reviewed_sha256:
  doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md: 926a2dce597f46be6808947a63b96cebd9728275b240f2930f1b9d281105b4ea
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 4
p2_note: "4 条均为非阻断澄清/记账建议（K-1…K-4），不影响本轮 9 处处置的成立"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 12)；C14 = MISSING-RECORD (not yet frozen; skipped) —— 符合预期"
captured_at: 2026-11-01T10:22:20+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（极窄面）：C-14 v2 的 9 处处置

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 r1 的 P1×5 + P2×4。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0；P2 × 4 非阻断，登记为 K-1…K-4）。**

**9 处全部核过，全部落位正确；v1→v2 的 diff 只动了这 9 处相关行，无夹带其它改动。**
r1 指出的两个核心风险已消除：**§4 不再声称 C-01b 冻结了四张表**（与 §0 行 3/4 自洽），**SC-S04/S05/S07 不再复写 C-01b**（改为引用不复写 + 只补增量）。

| # | 核对项 | 结果 |
|---|---|---|
| 1 | P1-1 §4 不再声称 C-01b 冻结表结构；与 §0 自洽 | **✅**（`:196` 明写「C-01b 未冻结…AD-003 `:117`」；§0 行 3 部分 / 行 4 无 与之一致） |
| 2 | P1-2 §0 行 3「部分」+ SC-34/26/27 覆盖准确；SC-S04/S05/S07 无残留复写 | **✅**（三条目描述与 C-01b `:85`/`:86`/`:98` 原文相符；三条改为「引用 C-01b SC-xx——本契约不重写」+ 仅增量） |
| 3 | P1-3 SC-S08 不再要求 C-04b 加字段；PD-08 与 C-04b `:72` 引用正确 | **✅**（`:146-148` 明写不扩协议形状、字段加入属 C-04b UNFREEZE/M2-C1 独立 Task；ADJ-001 `:68` PD-08、C-04b `:72` `BOOK_DELETE_CONFLICT` 均实核存在且语义对得上） |
| 4 | P1-4 C-06 entry 不再断言等于 `EntryId` | **✅**（`:197` 改为「定位键；对齐规则须在 C-06 侧或协议实现 Task 确认，不单方面重定义」） |
| 5 | P1-5 身份公式 + 行键自洽；改名后 EntryId 不变可成立；SC-S01/S12 一致 | **✅**（`:42` = SourceId + 稳定排序键、SourceVersionId 不参与；`:43` 行键；`:44` 改名不变；SC-S01 `:88`/`:92`、SC-S03 `:104`、SC-S12 `:67` 全部相洽） |
| 6 | P2-1 SC-S14 正文与验证统一「大文件先清」 | **✅**（`:160` 与 `:164` 均写大文件先清） |
| 7 | P2-2 SC-S15 引用改为 SC-03 | **✅**（`:169`「C-01b SC-03 的清理前缀白名单，`cleanup.py:41`」） |
| 8 | P2-3 SC-S13 引用 + §5 条件 4 | **✅**（`:74` → SC-S01/SC-S02；`:206` 准确记录 `MISSING-RECORD (not yet frozen; skipped)`，并写「冻结记录建立后转为实际校验（已纳入清单）」） |
| 9 | P2-4 矩阵加「正文 §x」 | **✅**（行 3/4/5 分别加「（正文 §2）」「（正文 §1）」「（正文 §3）」） |

治理实跑：`check.ps1` PASS（3 warnings）EXIT=0；`verify_pins.ps1` PASS（all 12）+ C14 skipped（符合预期）；未 push（224）；工作树干净；被审文件 blob `926a2dce…` 未改变。

---

## 2. 9 处核对明细

### 2.1 P1-1（§4 虚假已承载）—— ✅

- `:196` 现文：「C-01b **未冻结** 四张表（AD-003 `:117` 明文「这些表均未定，由 DSH 在 D05 范围冻结」）→ 表结构留给后续存储契约，本契约只定义语义与不变量、不定义 DDL」。
- 实核：AD-003 `:117` 原文即「…的表名、索引、外键、约束与迁移版本**均未定**，由 DSH 在 D05 范围冻结」✓；C-01b 全文对这四张表 0 命中 ✓。
- §4 新增的引用清单也准确：SC-02/03/20（缓存）✓、SC-26/27/34（同步/缺失/operation journal）✓、SC-21/22（授权面，**非**表结构）✓。
- 与 §0 自洽：行 3「部分：SC-34/26/27」✓、行 4「无（C-06 只到 entry 授权）」✓ —— 不再出现「已承载」与「无」并存。

### 2.2 P1-2（双权威）—— ✅

- §0 行 3 现文把「已有承载」改为「**部分**：C-01b **SC-34**（operation journal + receipt、崩溃恢复先核对 OS 事实）、**SC-26**（Dirty→扫描→diff→预览→事务发布新绑定）、**SC-27**（缺失页 tombstone 不连带删除；变化页新建 binding generation）」——三条描述与 C-01b `:98`/`:85`/`:86` 原文相符 ✓。
- SC-S04 `:111`「**引用 C-01b SC-34**…本契约不重写其语义」+ `:112` 只补 `kind: relink|repoint|resync` 与步骤序列 ✓；SC-S05 `:120` 引用 SC-26 + 只补 sync 判据 ✓；SC-S07 `:138` 引用 SC-27 + 只补 resync 操作序列 ✓。
- **残留复写检查**：三条内剩余描述现在挂的是**方案原文**（`:422`/`:459`/`:421`/`:432`），不是 C-01b 冻结字节——契约实例化方案是正常分工，不构成双权威 ✓。

### 2.3 P1-3（SC-S08 vs 冻结 C-04b）—— ✅

- `:146`「**本契约不扩展 C-04b 的协议形状**」+ 明确指出 `DeletePreviewItem`（C-04b `:43`）无 pending 字段 ✓；
- `:147`「需求声明（不含协议改动）…该字段的加入属 **C-04b 的 UNFREEZE 或 M2-C1 §5.11.2 的独立字节修订 Task**（照 C-08 块② 模式）」✓ —— 与 C-14 自身 `:8`/`:198` 的「不改已冻结字节」一致；
- `:148` 引用 **ADJ-001 PD-08**（`:68` 共享引用）与 **C-04b `:72`**（`BOOK_DELETE_CONFLICT` 关系图/归属预检）——两者均实核存在，且「不清理被引用记录」靠关系图预检承载的方向正确 ✓。

### 2.4 P1-4（C-06 entry 混同）—— ✅

- `:197` 现文：「`scope.entry` 语义是『可解析到授权根内路径的定位键』（C-06 `:52`）；本契约的 `EntryId` 经 `source_entries.locator` 解析后可与之对应——**对齐规则须在 C-06 侧或协议实现 Task 中确认，本契约不单方面重定义已冻结字段**」✓。
- 与 C-06 `:52` 原文（「`scope.sourceId/entry` 必须解析到某 `authorizedRoots` 内的路径」）完全对得上 ✓。

### 2.5 P1-5（身份公式）—— ✅

- `:42`：「身份 = `EntryId`，由 **`SourceId` + 稳定排序键**（内容指纹用于区分「同名不同内容」）共同确定；**`SourceVersionId` 不参与身份**」；
- `:43`：「**行键** = (`SourceVersionId`, `EntryId`)——同一身份在不同内容版本下是不同行」；
- 自洽性：改名/移动不改稳定排序键、不改内容指纹 → `EntryId` 不变（`:44` ✓、SC-S01 `:88`/`:92` ✓、SC-S03 `:104` ✓）；内容版本变化 → 行键变化但身份不变（SC-S12 `:67` 的「未变成员保留」✓）；验证 `:46`「改名 ZIP 内成员 → EntryId 不变」在 v2 公式下**可成立** ✓。

### 2.6 P2×4 —— ✅

- **P2-1** `:160`/`:164` 统一「同 last-use 时**大文件先清**」✓（v1 的「变小文件先于小」已删）。
- **P2-2** `:169` 改引「C-01b **SC-03** 的清理前缀白名单，`cleanup.py:41`」✓（不再提 SC-01）。
- **P2-3** `:74`「恢复路径见 **SC-S01/SC-S02**（relink/repoint 入口与范围选择）」✓；`:206` 条件 4 如实写 `MISSING-RECORD (not yet frozen; skipped)` 与「冻结记录建立后转为实际校验（已纳入清单）」✓。
- **P2-4** §0 矩阵行 3/4/5 已加「（正文 §2）」「（正文 §1）」「（正文 §3）」✓。

---

## 3. 新增问题（P2 × 4，非阻断）

1. **K-1（`§4 :198` 口径可再对齐）**：C-04b 行仍写「删除 preflight 的 pending operation 披露（SC-S08）；**不改 C-04b 字节**」。SC-S08 已明确该字段属「需求声明（不含协议改动）」，建议此行改为「需求声明（SC-S08）；字节修订属 C-04b UNFREEZE / 独立 Task」，避免读者误以为 C-14 直接定义该接口。
2. **K-2（`SC-S08 :148` 不变量可判定化）**：「删除**不得**清理被 `page_bindings` 引用为『唯一来源』的记录」——ADJ-001 PD-08 的口径是「可安全拆分的共享引用不是阻断条件、保留共享物理原文件与其他项目绑定」，与「唯一来源」不是同一概念。建议把不变量写成可判定形式（如「删除后任一 `page_bindings` 行仍可解析到其 `SourceEntry`/`SourceVersion`，或被显式置 `missing`」），并把主依据挂在 C-04b `:72` 关系图预检上（PD-08 作为补充）。
3. **K-3（`SC-S09/SC-S11` 稳定排序键的稳定性前提）**：身份 = `SourceId` + 稳定排序键，但 SC-S11 允许「`SourceVersion` 变化时可重排」。建议补一句：**排序键由容器语义确定（如 PDF 页序）；若同内容重排导致排序键变化，应视为新 entry 还是保留身份**——当前与 SC-S12「未变成员保留」之间存在解释空间（非矛盾，但实现会问）。
4. **K-4（表 DDL 承载时点记账）**：§4 说「表结构留给后续存储契约」，而 AD-003 `:117` 写「由 DSH 在 D05 范围冻结」。建议在 C-14 冻结记录或 Gate 记账里明确「四张表 DDL 的承载契约与时点」，避免 D05 冻结时该承诺悬空（不影响 D05 五项判定，但在 Gate 关闭说明里应可见）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文；未参与 C-14 起草与 v2 修订（作者 = DSH）。
- 我出具过 C-01b/C-06/C-04b/C-08 的部分复核报告及 C-14 r1（如实披露）；本轮按「9 处是否真正处置」标准核，未因 r1 系我出具而放宽（9 处均另做原文/行号实核）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；`check.ps1`/`verify_pins.ps1` 为只读校验。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档 diff、冻结字节与脚本输出比对。
- 未重核 r1 已核过、v2 未动的其余条款（§0.1 四条、SC-S09 之外方案对齐等）。
- 未核 C-14 与 C-07/C-09 接口；未核 §4 提到的「后续存储契约」是否已有起草计划。
- 未核 C-04b UNFREEZE/独立 Task 的具体字节修订范围（只核 C-14 引用口径）。
- 未核 `doc/tasks/FEA-C14-DRAFT.md` 的 AC 与 v2 条款的逐条对应。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×4；9 处处置全部成立，4 条 K 项为非阻断澄清/记账建议）。
