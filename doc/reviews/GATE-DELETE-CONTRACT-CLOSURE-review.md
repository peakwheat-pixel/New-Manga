---
document_id: GATE-DELETE-CONTRACT-CLOSURE
kind: independent_review
task_id: AC9（G-DELETE-CONTRACT 关闭裁定复核）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 2ed4ed91a
reviewed_head_full: 2ed4ed91aad93643bf7c37f48f333f6b246c5bd8
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 2ed4ed91a）"
reviewed_documents:
  - doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md（87 行，新建）
  - doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md（§9 :128，已改 CLOSED）
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md（Gate 判定块 `:12`）
  - 对照：doc/plan/D04-D07-COVERAGE-CHECK-2026-11-01.md（v3）、C-13/C-04b/C-08/C-09 冻结记录、verify_pins
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 4
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 13)，EXIT=0，本次实跑；C-13 冻结 pin = d2cb8de4…（见 P1-1）"
captured_at: 2026-11-01T12:02:00+08:00
captured_by: c01b-reviewer
---

# 独立复核：`G-DELETE-CONTRACT` 关闭裁定（AC9）

**本报告不是** Gate 裁定本身。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 4）。**

**5 处里 1、2、3、5 到位**：L-5 已明文认定（按迁移处理 + 必须持 SC-17 锁 + 实现前置约束/不改字节）；L-1…L-9 九条全部登记且「影响判定」的只有 L-5；§5 五条边界全在；§2 的 D07 行如实标「行 7 ⚠ 部分」。

**唯一 P1 在 §4 Errata**：第 5 行点名 **`FEA-C13_DRAFT_PROTECTION_DRAFT.md :203`**——那是**冻结契约 C-13 的正文（pin `d2cb8de4…`）**，按 Errata 去改会直接破坏冻结字节与 `verify_pins 13/13`，**不属「只改状态描述，不动冻结字节」**可覆盖的范围；必须改为「保持原字节 / 或走 `CONTRACT-UNFREEZE-C13` + 重冻 + 复核」。

| # | 核对项 | 结果 |
|---|---|---|
| 1 | L-5 明文认定 | **✅**（§3 `:40`：整库恢复**按迁移处理**、实现时**必须持 SC-17 独占维护锁**（停写者/Run/lease、staging、校验、commit marker 后切换）、**实现前置约束、不改变冻结字节**、要写入 C-09 走 UNFREEZE；§5 `:72` 再声明「不构成可以不加锁」） |
| 2 | L-1…L-9 登记 | **✅**（9 条全在 §3 `:40`–`:48`；L-7 已正确写「影响**实现层检测精度**，不改条款承载」；L-5 是唯一「影响判定（⚠ 部分）」项） |
| 3 | §5 边界声明 | **✅**（`:69`–`:72` 五条全在：不构成 G-DELETE-IMPL 关闭/自动释放、不构成 DDL 已冻结、不构成 M2-C1 字节修订完成、不构成整库恢复可不加锁、不构成 push 授权） |
| 4 | §4 Errata 可执行 | **❌ P1-1**：5 行中第 5 行指向**冻结契约正文字节**，执行即破坏 C-13 pin；另第 1–2 行（ADJ-001 `:128` / 矩阵）**已在本提交 `2ed4ed91a` 完成**，Errata 却仍写「待更正」 |
| 5 | 「部分」是否被写成「全部」 | **✅**（§2 `:30` 明写「前 6 项 ✅ / **行 7 ⚠ 部分**（见 L-5）」；全文「全部」只剩 `:23` 标题、`:32`（13 份全部冻结，属实）、`:65`（契约语义全部有承载）——均不构成把行 7 写成全覆；`:23` 标题可加限定，P2-3） |

---

## 2. 5 处核对明细

### 2.1 L-5 明文认定 —— ✅

§3 `:40` 原文：「**本裁定认定**：整库恢复**按迁移处理**，实现时**必须持 SC-17 的独占维护锁**（停所有写者/Run/lease、staging、校验、commit marker 后才切换）。**该认定是实现前置约束**，不改变已冻结契约的字节；若后续要写入 C-09，走 UNFREEZE」——
- 「按迁移处理」✓、「必须持 SC-17 锁」✓、「实现前置约束 + 不改字节」✓、「写入 C-09 走 UNFREEZE」✓；
- §5 `:72`「❌ 不构成整库恢复可以不加锁（L-5 的认定必须实现）」✓ 二次固化；
- 与 C-01b SC-17 原文（「任何迁移使用独占维护锁、staging、校验与 commit marker」）在语义上对齐 ✓。

### 2.2 L-1…L-9 —— ✅

- 9 条全在：L-5（`:40`）、L-1（`:41`）、L-2（`:42`）、L-3（`:43`）、L-4（`:44`）、L-6（`:45`）、L-7（`:46`）、L-8（`:47`）、L-9（`:48`）✓；
- 「影响判定」的只有 L-5 ✓（L-7 已按 AC8-r2 的建议改为「影响实现层检测精度，不改条款承载」；其余均「实现前置」）✓；
- 与 AC8 v3 §6 的 9 条一一对应 ✓（L-2 还补全了 `RUN_*` 3 码 + §8 Proposed 的描述）✓。

### 2.3 §5 边界声明 —— ✅

`:69`–`:72` 五条：「不构成 `G-DELETE-IMPL` 的关闭或自动释放」「不构成 DDL 已冻结（L-1）」「不构成 M2-C1 字节修订已完成（L-2）」「不构成整库恢复可以不加锁（L-5 的认定必须实现）」「不构成远端 push 授权」——**五条齐全**，与你要求的五项逐一对应 ✓。

### 2.4 §4 Errata —— ❌ P1-1（不可按字面执行）

| 行 | 文件 | 现状核查 |
|---|---|---|
| 1 | `ADJ-001 §9 :128` | **已在本提交完成** ✓（现为「CLOSED（2026-11-01）…保留项 L-1…L-9，其中 L-5…」）——Errata 仍写「更正为」，属**已完成的待办** |
| 2 | `FEA-CONTRACT_FREEZE_MATRIX.md` | **已在本提交完成** ✓（`:12` 现为「Gate 判定（最终）…`G-DELETE-CONTRACT` ✅ CLOSED…」）——同上 |
| 3 | `FROZEN-C04b/C08/C13` | C04b `:35/:43/:49`、C13 `:61/:63` 确有旧口径 ✓；**C08 `:55` 并无「D07 缺多项」**（现文是「Gate 仍不自动关闭…AC8+AC9 裁定」）——指认不精确；且这三份是**证据记录**，宜「追加注记」而非改写原文 |
| 4 | `GATE-CLOSURE-RULING :63/:111` | 确有旧口径 ✓（`:63`「两个 Gate 都 OPEN 时不满足」、`:112`「保持 OPEN」）——但那是**历史裁定的推理**，改写会篡改历史；宜追加 errata 注记 |
| 5 | **`FEA-C13_DRAFT_PROTECTION_DRAFT.md :203`** | **P1-1 核心**：`:203` 是 C-13 冻结契约正文（「C-09 的条件③（两 Gate 关闭）仍不满足…」）；C-13 的 LF blob sha256 = **`d2cb8de4dd79fb490e3e5c12a6aaad3e1a0bb294c217a79f083ecfeab683837c`**，与冻结记录 `:16`/`:81` 的 pin 一致，`verify_pins` 现为 13/13。**按 Errata 改这一行 → C-13 pin 立刻失配（13/13 → 12/13）**，违反「冻结后任何字节改动须重算 pin 或走 UNFREEZE」的纪律；「只改状态描述，不动冻结字节」这句话无法覆盖**冻结契约内部的一行正文** |

**修法（二选一，均不改已冻结字节）**：
- **（推荐）** 把第 5 行改为：「`FEA-C13_DRAFT_PROTECTION_DRAFT.md :203` **保持原字节**（历史陈述）；以 `ADJ-001 §9 :128` 为 Gate 状态的唯一权威。**若确需修改 C-13 正文，走 `CONTRACT-UNFREEZE-C13` + 独立复核 + 重冻 + 重算 pin**」；
- 或：把 C-13 :203 从本次 Errata 移除，另开 C-13 的 UNFREEZE Task（不建议为一行状态句付出重冻成本）。

### 2.5 「部分写成全部」复核 —— ✅（附 P2-3）

- §2 `:30` D07 行：「7 项（FEA-01 `:58`）+ 方案 `:770` 的 2 项 | C-09 v5 + C-01b + C-04b | **前 6 项 ✅ / 行 7 ⚠ 部分**（见 L-5）」✓ 如实；
- 全文「全部」：`:23`（§2 标题「四包条款级承载全部完成」）、`:32`（13 份契约全部冻结——属实）、`:65`（「契约语义已全部有冻结承载」）——**均未把行 7 写成全覆** ✓；
- **P2-3**：建议 `:23` 标题补「（D07 行 7 依 L-5 认定）」，与 `:30` 的 ⚠ 部分严格对齐（否则只看标题的人会读成四包全 ✅）。

---

## 3. 新增问题（P2 × 4，非阻断）

1. **P2-1（矩阵陈旧计数 + 字面 `\n`）**：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` `:3` 仍写「12 份已冻结」、`:10`「已冻结 12 份：…（未含 C-09）」，而现为 **13 份**（C-09 已冻结，`verify_pins` 13/13）；`:12` 末尾有**字面 `\n`**（`…见该裁定。\n`）需清理。
2. **P2-2（Errata 前两行已完成）**：第 1–2 行（ADJ-001 `:128`、矩阵）已在 `2ed4ed91a` 完成，建议标「**已更正（本提交）**」，避免二次编辑/误读为待办。
3. **P2-3（§2 标题限定）**：见 2.5。
4. **P2-4（证据记录宜追加注记）**：第 3–4 行的 FROZEN-C04b/C08/C13 与 GATE-CLOSURE-RULING 是**冻结记录/历史裁定**；建议改为「**追加 errata 注记，不删除原文**」，并修正对 FROZEN-C08 的指认（`:55` 现文不含「D07 缺多项」口径）。

---

## 4. 其余核对（通过项）

- **ADJ-001 `:128`**：已 `CLOSED（2026-11-01）`，含 D04/D05/D06/D07 承载 + L-1…L-9 与 L-5 提示 + 链接本裁定 ✓。
- **矩阵 Gate 判定块 `:12`**：两 Gate 均 ✅ CLOSED，并注「D04–D07 全覆盖，`approved` r3」「保留项 L-1…L-9（尤其 L-5）与 Errata 见该裁定」✓（除 P2-1 的计数/`\n` 外）。
- **裁定 §1**：Gate 表格「OPEN → ✅ CLOSED（2026-11-01）」、两条 Gate 最终状态表 ✓。
- **裁定 §6**：C-09 冻结不改字节、C-10 不受阻、实现 Task 需 C-11 选候选 ✓ 无夸大。
- **治理**：`check.ps1` PASS（3 warnings）EXIT=0；`verify_pins.ps1` PASS (all 13) EXIT=0；未 push（242）；工作树干净（本次复核新增报告除外）。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文。
- 未参与 AC9 裁定、ADJ-001/矩阵编辑或 AC8 覆盖表撰写（作者 = DSH）；本轮逐条对照 ADJ-001、矩阵、C-13/C-04b/C-08/C-09 记录与 `verify_pins` 实跑结果，未按裁定自述判定。
- 我出具过 AC8-r1/r2/r3 及 C-08/C-09/C-13/C-14 的多轮复核（如实披露）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 6. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 未重核 D04–D07 的条款级承载（AC8 已核；本轮只核 5 处）。
- 未核 C-02/C-03/C-05/C-07/C-11/C-12 内容（只确认 pin）。
- 未核实现代码（`src/` 不在本 checkout）；未核 M2-C1 字节修订执行情况（属 L-2）。
- 未核 C-10 与 Gate 的关系（裁定 §6 只声明不受阻）。

—— 报告结束（`verdict: changes_requested`；5 处中 4 处到位，唯一 P1 为 Errata 第 5 行指向冻结契约 C-13 `:203`，执行会破坏 pin；P2×4 为矩阵计数/`\n`、Errata 已完成行标注、§2 标题限定、证据记录追加注记）。
