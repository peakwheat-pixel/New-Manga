---
document_id: FEA-C08-r11
kind: independent_review
task_id: FEA-D06-GAP（AC7 重冻前复核）
round: 11
scope: 冻结记录 + UNFREEZE 载体同步 + C-08 的 P2 依据句 + pin 一致性
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 3008be284
reviewed_head_full: 3008be2847a9c9e41ae397d9995b1d899094cca2
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 3008be284）"
reviewed_documents:
  - doc/plan/FEA-CONTRACT-FROZEN-C08.md（95 行）
  - doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md（111 行）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（v6+，166 行，blob sha256 b509271c…）
  - 依据：M2-C1 `:202`/`:204`/`:834`/`:861`、P11 `:111`
reviewed_sha256:
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: b509271cc56fbbb219e4d30c040f1df80018dc9fe5dca20dc8268dd988db38e5
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 1
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 13)，EXIT=0，本次实跑；C-08 pin = b509271c… 与文件一致"
captured_at: 2026-11-01T11:27:00+08:00
captured_by: c01b-reviewer
---

# 独立复核 r11：C-08 记录/载体同步（极窄面 4 处）

**本报告不是** 冻结动作、不释放任何 Task。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 1）。**

四项里 **pin（第 4 处）与 P2 依据句（第 3 处）已到位**；但第 1、2 处仍有**具体残留**——不是「大体改好了」，而是三处可指名的文本问题：

| # | 核对项 | 结果 |
|---|---|---|
| 1 | 冻结记录 §1/§1A/§1B/§7 | **⚠ 部分**：§1 版本 v5 ✓、§1 pin `b509271c…` 与文件一致 ✓、§1B 已更新 ✓；**§1A 的 pin 叙述仍是 `2e7a5f2b…`**（不是你说的 `b509271c…`）；**§7 有一行表格行 `:89` 掉在标题/表头之上**（结构未恢复完整） |
| 2 | UNFREEZE 载体旧写法 | **❌ 未清干净**：`succeeded` / `targets.length = succeeded + failed` 已 0 命中 ✓，但 **`:72` 仍写 `M2-C1 `:204``（应为 `:202`）**；另 SC-R07 缺 r11 新增的「`waiting=0` 依据」句（载体 ≠ 最终正文） |
| 3 | C-08 的 P2 依据句 | **✅**（`:94` 已写清：P11 `:111` 只规定 Run 级 fatal，未规定未开始 Task → 本契约作为额外要求） |
| 4 | pin 一致性 | **✅**（`PIN AUDIT: PASS (all 13)`；C-08 blob `b509271c…` = 记录 §1 `:16`） |

**三处必改（都很小）**：§1A 的 pin 写法、§7 的孤儿表格行、UNFREEZE `:72` 的 `:204`（+ 补 `waiting=0` 依据句）。

---

## 2. 4 处核对明细

### 2.1 冻结记录 —— ⚠ 部分

- **§1 版本** `:15` = `**v5**（D06 四项已补；v6 正文；r10 核查后重冻）` ✓。
- **§1 pin** `:16` = `b509271cc56fbbb219e4d30c040f1df80018dc9fe5dca20dc8268dd988db38e5`，与当前文件的 LF blob **逐字一致** ✓。
- **§1A** `:77`：「…pin 已更新为 `2e7a5f2b…`」——**不是** `b509271c…`。你消息里写「§1A pin 叙述 → `b509271c…`（原文 `f61d1bef…`）」，实际文件里 `f61d1bef` 确实已清掉 ✓，但换成的是**上一版**的 `2e7a5f2b`，不是当前 `b509271c`。→ §1A 与 §1 的 pin 口径不一致（这正是要避免的证据链错位）。
- **§1B** `:22`「最后一次独立复核 | **r10**：核查 6 项中 5 项通过…」、`:24`「v5 的 D06 四项经 r9（changes_requested → v6 处置）→ **r10 认定正文通过**；剩余为记录同步（本轮完成）」✓ 已更新；本报告（r11）通过后应把该行更新为 r11。
- **§7**：`:90`「## 7. 变更记录」与 `:92` 表头「| 日期 | 变更 | 记录 |」都已恢复 ✓，**但 `:89` 有一行「| 2026-11-01 | 冻结后补充（FEA-D06-GAP）… | DSH |」掉在标题上方**——它不在任何表头之下，Markdown 渲染会变成裸文本，等于这一条变更记录「丢失」；`:86`–`:88` 还残留三行空行。结构未恢复完整。

### 2.2 UNFREEZE 载体 —— ❌ 未清干净

- `succeeded`：**0 命中** ✓；`targets.length = succeeded + failed`：**0 命中** ✓。
- **`:204`：2 命中**——
  - `:72`（SC-R08 的「冻结上下文」条）：「…（M2-C1 **`:204`**：「不含首次接受时才读取并冻结的当前 Revision、Lock、settings、Provider、constraint、context」）」——**仍是错的 `:204`，应为 `:202`**；
  - `:111`（变更记录行）：「SC-R08 行号 `:204`→`:202`」——这是**描述修复历史**，可接受。
- **SC-R07 与 C-08 v6 正文比对**：`:45`–`:59` 的 counts 判据、`failed`/`cancelled` 行、验证句都与 C-08 一致 ✓（你还额外补了「counts 没有 cancelled/interrupted 字段（`:861`）」的理由，比 C-08 更准确）；**但缺 C-08 在 r11 新增的「`waiting=0` 的依据」句**（`:94` 那句 P11 `:111` 的说明）——载体是「冻结后条款新增」的权威文本，正文与载体应当一致。

### 2.3 C-08 的 P2 依据句 —— ✅

- `:94`「`failed` / `cancelled` | …只要求共同不变量。**`waiting=0` 的依据**：P11 `:111` 只规定 Run 级 fatal → Failed，未规定未开始 Task 的处置，故本契约把「无 waiting/processing」作为**额外要求**——终态下不应再有排队工作」✓ 说清楚了：既承认 M2-C1/P11 没有明文，又把它定位成 C-08 的额外要求（与我在 r10 的建议一致）。

### 2.4 pin 一致性 —— ✅

- `verify_pins.ps1`：`PIN AUDIT: PASS (all 13)`，EXIT=0。
- C-08 当前 blob `b509271cc56f…` = 记录 §1 `:16` ✓。
- **附带提醒（P2-1）**：C-08 本次为补 P2 依据句改了正文，但 `§6 变更记录`（`:157`–`:166`）**没有新增行**登记这次改动（仍停在 v6 / v5 行）；记录 §1B 也写「剩余为记录同步（本轮完成）」，未提这次正文补句。建议补一行「v6.1/v7：SC-R07 补 `waiting=0` 依据句（r10 P2）」。

---

## 3. 必改清单

1. **P1-1（记录）**：
   - §1A `:77` 的 `2e7a5f2b…` → **`b509271c…`**（或改为「v6 重算：`b509271c…`；历史值 `2e7a5f2b…`」保留证据）；
   - §7 `:86`–`:89`：把孤儿行挪回表内（表头之下），删多余空行。
2. **P1-2（UNFREEZE 载体）**：
   - `:72` 的 `:204` → **`:202`**；
   - SC-R07 补 C-08 `:94` 的「`waiting=0` 依据」句（或注明「以 C-08 正文为准，载体只记新增要点」——二选一，但要写明）。
3. **P2-1（变更记录）**：C-08 §6 补一行登记「P2 依据句」的正文改动（配合 §1B 口径）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文。
- 未参与 C-08、记录、UNFREEZE 载体的撰写与修订（作者 = DSH）；本轮逐字比对 M2-C1 `:202`/`:204`/`:834` 与 P11 `:111`，未按转述判定。
- 我出具过 C-08 的 r9/r10（均 changes_requested）及更早复核（如实披露）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 未核 C-08 的 SC-R01…SC-R06/SC-R08/SC-R09 正文（本轮只核 P2 那一句）。
- 未核记录 §2/§3（冻结条件与协议注册）是否有其他陈旧内容（本轮只核 4 处）。
- 未核实现代码（`src/` 不在本 checkout）。

—— 报告结束（`verdict: changes_requested`；4 处中第 1、2 处各有具体残留，第 3、4 处 ✓；P1×2 + P2×1）。
