---
document_id: GATE-DELETE-CONTRACT-CLOSURE-r2
kind: independent_review
task_id: AC9（关闭裁定 · r2 窄面）
round: 2
scope: Errata 第 5 行/铁律 / 第 1–4 行标注 / §2 标题 / 矩阵计数与字面 \n
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: c144bf380
reviewed_head_full: c144bf380bc626532986c70e7a73b092e57a6896
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == c144bf380）"
reviewed_documents:
  - doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md（v2，87 行）
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md（85 行）
  - 对照：C-13 冻结 pin `d2cb8de4…`、ADJ-001 `:128`、verify_pins
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 1
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 13)，EXIT=0，本次实跑"
captured_at: 2026-11-01T12:10:00+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2：AC9 关闭裁定 v2（4 处窄面）

**本报告不是** Gate 裁定本身。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 1）。**

**4 处里 1、2、3 全部到位**：Errata 第 5 行已明确「保持 C-13 原字节、冻结契约正文一律不动」，§4 铁律句在；第 1–2 行已标「已更正」，第 3–4 行已改「追加注记」；§2 标题已加 L-5 限定。

**唯一 P1 在第 4 处（矩阵）**：**计数已改 13 ✓，但字面 `\n` 仍在**（`:12` 末尾），且矩阵 `:8`/`:10` 仍保留旧 Gate 口径（`:10` 还写「`G-DELETE-CONTRACT` ❌ 不满足——D06 有 4 项…D07 多项未冻且与 C-09 循环。仅剩 C-09（不可冻）」），与 `:12` 的「✅ CLOSED（最终）」自相矛盾。

| # | 核对项 | 结果 |
|---|---|---|
| 1 | Errata 第 5 行 + §4 铁律 | **✅**（`:60`：保持原字节/冻结契约正文 Errata 不得改动/唯一权威 `ADJ-001 §9 :128`/确需改走 `CONTRACT-UNFREEZE-C13` + 复核 + 重冻 + 重算 pin；`:52` 铁律：只改状态描述类文字、冻结契约正文一律不动、证据/历史裁定只追加注记不删原文） |
| 2 | 第 1–4 行标注 | **✅**（`:56` 第 1 行「已更正（提交 `2ed4ed91a`）」；`:57` 第 2 行「Gate 判定块已更正（`2ed4ed91a`）；其余计数见 P2-1 处置」；`:58` 第 3 行「追加 errata 注记、不删原文」+ FROZEN-C08 `:55` 说明；`:59` 第 4 行「追加 errata 注记、不删原文」） |
| 3 | §2 标题限定 | **✅**（`:23`「D04–D07 四包条款级承载已完成（D07 行 7 依 L-5 认定）」） |
| 4 | 矩阵计数 13 / 字面 `\n` | **❌**：计数 ✓（`:3` 13 份、`:10` 已冻结 13 份）；**字面 `\n` 仍在 `:12` 末尾**（`…见该裁定。\n`）；另 `:8`「13 份已冻结契约 + C-10 + **C-09（未冻）**」与 `:10` 的「❌ 不满足…D06 有 4 项…D07 多项未冻且与 C-09 循环…仅剩 C-09（不可冻）」均为旧口径，与 `:12` 矛盾 → **P1-1** |

---

## 2. 4 处核对明细

### 2.1 Errata 第 5 行 + §4 铁律 —— ✅

- `:60` 现文：「`FEA-C13_DRAFT_PROTECTION_DRAFT.md :203` | 同上 | **保持原字节**（历史陈述，属**冻结契约 C-13 正文**，Errata **不得**改动——改它会立即破坏 pin）。Gate 状态的唯一权威是 `ADJ-001 §9 :128`。若确需改 C-13 正文，须走 `CONTRACT-UNFREEZE-C13` + 独立复核 + 重冻 + 重算 pin」——完全符合我 r1 的建议 ✓；并明确 pin 会破坏、给出 UNFREEZE 路径 ✓。
- `:52` 铁律：「只改**状态描述类**文字；**冻结契约正文一律不动**（改了会破坏 pin）。证据/历史裁定文件只**追加注记**，不删原文」✓——把「Errata 的边界」写成了规则，比 r1 的「只改状态描述，不动冻结字节」更明确 ✓。
- 复核确认：C-13 文件 LF sha256 仍 = `d2cb8de4dd79fb490e3e5c12a6aaad3e1a0bb294c217a79f083ecfeab683837c`（与冻结 pin 一致），`verify_pins` 13/13 ✓——本轮 v2 未触碰 C-13 ✓。

### 2.2 Errata 第 1–4 行标注 —— ✅

- 第 1 行（ADJ-001 `:128`）：标注「**已更正（提交 `2ed4ed91a`）**」✓（实核 ADJ-001 `:128` = CLOSED）。
- 第 2 行（矩阵）：标注「Gate 判定块已更正（`2ed4ed91a`）；其余计数见 P2-1 处置」✓（矩阵 `:12` 的 Gate 判定块确已更正——但该行的「其余计数见 P2-1」正好对应本报告 P1-1：P2-1 未真正处置完，见 2.4）。
- 第 3 行（FROZEN-C04b/C08/C13）：「**追加 errata 注记、不删原文**」+「FROZEN-C08 `:55` 现文其实已更新，本行指认以其 §5 历史段落为准」✓——修正了 r1 指出的指认不准问题。
- 第 4 行（GATE-CLOSURE-RULING `:63/:111`）：「**追加 errata 注记、不删原文**」✓——保留历史裁定原文，符合证据纪律。

### 2.3 §2 标题 —— ✅

- `:23`「## 2. 关闭依据：D04–D07 四包条款级承载已完成（**D07 行 7 依 L-5 认定**）」✓——标题不再压过 `:30` 的「行 7 ⚠ 部分」，与 §3 L-5 明文认定一致。

### 2.4 矩阵（P1-1） —— ❌

计数方面已到位：`:3`「13 份已冻结；Gate 判定见下」✓、`:10`「已冻结 13 份」✓。但：

1. **字面 `\n` 仍在**：`:12` 末尾 =「…**Errata** 见该裁定。`\n`」——该行 length = 258，`Contains("\n")`（字面反斜杠+n）= **True**。r1 的 P2-1 明确包含此项，v2 未清。
2. **`:8` 旧口径**：「把 **13 份已冻结契约 + C-10（未起草）+ C-09（未冻）** 的冻结依赖链…」——C-09 已冻结（v5）且**已计入 13 份**，此处重复列出且标「未冻」，等于 14 份，错误。
3. **`:10` 旧 Gate 口径**：「**Gate 判定**（FEA-GATE-READINESS-review，2026-11-01）：…`G-DELETE-CONTRACT`（D04–D07）**❌ 不满足**——D04 ✓、D05 ✓，但 **D06 有 4 项声明范围无条款**、**D07 多项未冻且与 C-09 循环**。仅剩 **C-09**（不可冻）、**C-10**（U-03 已裁，可起草）」——与 `:12` 的「✅ CLOSED（最终）」直接矛盾；且「仅剩 C-09（不可冻）」也已过时（C-09 已冻结）。这正是 Errata 第 2 行承诺的「D06/D07 的陈旧阻塞列 → 指向本裁定」**未完成的剩余部分**。
4. **P2-1（附）**：`:61` 的 Gate 表 `G-DELETE-CONTRACT` 行未像 `:62` 的 `G-CONTRACT` 行那样标「**已 CLOSED 2026-11-01**」——建议一并补，避免矩阵内三处 Gate 状态不一致（`:12` CLOSED / `:10` ❌ / `:61` 无状态）。

**修法（只改矩阵，不碰冻结契约）**：
- `:12` 删掉行尾字面 `\n`；
- `:8` 改为「13 份已冻结契约（含 C-09）+ C-10（未起草）」；
- `:10` 把「Gate 判定」句改为「`G-CONTRACT` ✅ CLOSED / `G-DELETE-CONTRACT` ✅ CLOSED（2026-11-01，见裁定）；C-09 已冻结（v5）」或整句改为「状态见 `:12` 最终判定」；
- `:61` 的 `G-DELETE-CONTRACT` 行补「**已 CLOSED 2026-11-01**」。

---

## 3. 其余核对（通过项）

- **裁定 v2 的 §1/§5/§6** 未被本次修改破坏：§1 Gate 表仍「✅ CLOSED（2026-11-01）」；§5 五条边界仍在（`:69`–`:72`）；§6 后续说明正确 ✓。
- **ADJ-001 `:128`**：仍为 CLOSED 且含 L-1…L-9 与 L-5 提示 ✓。
- **治理**：`check.ps1` PASS（3 warnings）EXIT=0；`verify_pins.ps1` PASS (all 13) EXIT=0；未 push（243）；工作树干净（本次复核新增报告除外）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文。
- 未参与裁定 v2、矩阵或 Errata 的编辑（作者 = DSH）；本轮逐字核对裁定 §4 五行、§2 标题与矩阵 `:3`/`:8`/`:10`/`:12`/`:61`，并对 `\n` 做了字面检测（`Contains("\n")` = True），未按自述判定。
- 我出具过 AC9-r1（changes_requested）与 AC8-r1…r3、C-08/C-09/C-13/C-14 多轮复核（如实披露）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 未重核 D04–D07 条款级承载（AC8 已核）与裁定 §2 表格各包内容（上一轮已核）。
- 未核 C-02/C-03/C-05/C-07/C-11/C-12 内容（只确认 pin）。
- 未核实现代码（`src/` 不在本 checkout）；未核 M2-C1 字节修订执行；未核 C-10 与 Gate 关系。

—— 报告结束（`verdict: changes_requested`；4 处中 1、2、3 到位，第 4 处矩阵：计数 ✓ 但字面 `\n` 残留 + `:8`/`:10` 旧 Gate 口径未清；P1×1 + P2×1）。
