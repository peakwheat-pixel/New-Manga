---
document_id: FEA-C08-r10
kind: independent_review
task_id: FEA-D06-GAP（AC 复核）
round: 10
scope: C-08 v6（SC-R07 counts 重写、行号、版本、记录去重）+ UNFREEZE 同步 + pin
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 9f294acbf
reviewed_head_full: 9f294acbf018f613d855eab74203e6dc214aacea
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 9f294acbf）"
reviewed_documents:
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（v6，166 行，blob sha256 2e7a5f2b…）
  - doc/plan/FEA-CONTRACT-FROZEN-C08.md（91 行）
  - doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md（104 行）
  - 依据：M2-C1 `:138`/`:200`–`:206`/`:213`/`:223`/`:834`/`:861`、P11 §4.1 `:97`/`:111`/`:115`–`:117`
reviewed_sha256:
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: 2e7a5f2b62655554cc818cc84e4c2358c8ee09d2ab7968e9a9547b2b20f167e6
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 2
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 13)，EXIT=0，本次实跑；C-08 pin = 2e7a5f2b… 与记录 §1 一致"
captured_at: 2026-11-01T11:23:00+08:00
captured_by: c01b-reviewer
---

# 独立复核 r10：C-08 v6（D06 四项补齐的第二轮）

**本报告不是** 冻结动作、不释放任何 Task。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 2）。**

**契约正文（C-08 v6）本身已到位**：SC-R07 的 `counts` 判据可执行、字段名逐字对得上、`succeeded` 已从规范条款中清除、行号 `:213`/`:202`/`:138` 全部正确、C-08 `:3` 已是 FROZEN v5、§4 两条已按事实重写、pin `2e7a5f2b…` 与 `verify_pins` 13/13 一致。

**但两处「记录/载体」没有跟上**，直接影响 AC7 重冻的证据链：

1. **冻结记录仍停留在旧口径（P1-1）**：§1 `:15` 版本仍是 **v4**（你要求核的「记录 §1 版本是否 v5」→ **不是**）；§1A `:77` 的 pin 叙述仍写 `f61d1bef…`（现行 `2e7a5f2b…`）；§1B `:22`/`:24` 仍写「D06 四项补充待 r9 复核」（r9 已出 `changes_requested`、v6 已处置）；§7 变更记录的**标题与表头在去重时丢失**（`:86`–`:89` 直接是表格行）。
2. **UNFREEZE 载体未同步 v6（P1-2）**：`CONTRACT-UNFREEZE-C08-2026-11-01.md` 里 **SC-R07 仍是 v5 的旧三条件**（`:43`–`:53`，仍含 `targets.length = succeeded + failed`）；**SC-R08 仍引 `:204`**（`:66`，应为 `:202`）；变更记录只有 v1 一行，没有「v6 同步」记录。SC-R06（`:213`）与 SC-R09（`:138`）倒是已同步——**只同步了一半**。

| # | 核对项 | 结果 |
|---|---|---|
| 1 | SC-R07 新判据可执行且无误 | **✅ 实质到位**（字段名与 `:834` 逐字一致；共同不变量与逐终态判据自洽；取消 total 等式正确）；附 P2-1（`failed` 的 `waiting=0` 依据） |
| 2 | `succeeded` 残留 | **✅**（全文 1 处，仅在 changelog `:161` 作为「被取消的旧写法」被引用，无规范用法） |
| 3 | 行号 `:213` / `:202` / `:138` | **✅** 逐一对上原文（`:213` Running 行、`:202` fingerprint、`:138` 「不得充当幂等键」；`:223` 的 `IDEMPOTENCY_KEY_REUSED` 也对） |
| 4 | C-08 `:3` 与记录 §1 版本均 v5 | **❌ 一半**：C-08 `:3` = **FROZEN v5** ✓；记录 §1 = **v4** ✗（P1-1） |
| 5 | 记录 §4 两条按 v5 事实改写 | **✅**（`:54` 六项全覆盖 + 以 AC8 为准；`:55` C-09 已解环冻结、不再阻塞） |
| 6 | pin | **✅**（`PIN AUDIT: PASS (all 13)`；C-08 blob `2e7a5f2b…` = 记录 §1 `:16`） |

---

## 2. 6 处核对明细

### 2.1 SC-R07 新判据 —— ✅ 实质到位（附 P2-1）

- **字段名逐字核对**：C-08 `:88` 列的 `{total, completed, failed, skipped, blocked, waiting, processing}` 与 M2-C1 `:834`–`:835` 的 `counts` 定义**完全一致** ✓（我逐字比对了 7 个字段名与顺序）。
- **共同不变量** `processing = 0 && waiting = 0`：
  - `cancelled`：M2-C1 `:221`「未开始 Task 转 cancelled」+ P11 `:115`/`:117`「取消未开始工作 / Pending Task 转 cancelled」→ 终态无活动任务 ✓；
  - `completed` / `completed_with_failures`：完成即无活动任务 ✓（且 C-08 追加 `blocked=0`，与 M2-C1 `:219` 的 CompletedWithFailures 语义相容）；
  - **`failed`：缺明文依据（P2-1）**——P11 `:111` 只写「Run 级 fatal error → `Failed`」，未说未开始 Task 如何处置；若实现允许 `failed` 终态残留 pending（`counts.waiting > 0`），本条会把它判成非法态。建议补一句依据（要求实现把残留 Task 转 cancelled/skipped）或注明这是 C-08 的**额外要求**。
- **取消 total 等式是正确的**：counts **没有 `cancelled`/`interrupted` 字段**（Task 状态域有 `:861`），所以 `cancelled`/`failed` 的 `total` 本来就不闭合；C-08 明确「不要求 total 等式」+「不得用 `targets.length` 与计数相加」→ 与 M2-C1 一致 ✓。
- **验证 4 条可执行** ✓（伪造 `failed>0`+`completed`、`cancelled`+`processing>0`、重启后同一终态与同一 `counts`、断网重读）——比 r9 版本强，且覆盖了「已持久化」的实际验证。

### 2.2 `succeeded` 残留 —— ✅

全文只有 1 处（`:161` changelog v6 行），内容是「取消 `targets.length = succeeded + failed`（`succeeded` 字段不存在…）」——这是**修复记录**，不是规范条款；规范段落（SC-R07 `:80`–`:104`）已无 `succeeded` ✓。

### 2.3 行号 —— ✅

| C-08 引用 | 原文核对 |
|---|---|
| `:213` | M2-C1 `:213` = `Running` 行「pause 先持久化请求…到安全边界后不再开始下一 Step 并转 paused」✓ |
| `:202` | M2-C1 `:202` = fingerprint「它不含首次接受时才读取并冻结的当前 Revision、Lock、settings、Provider、constraint、context…」✓ |
| `:138` | M2-C1 `:138` = 「`request_id` 只做单次请求/响应关联，**不得**充当幂等键」✓ |
| `:223` | M2-C1 `:223` = 「幂等键复用冲突返回 `IDEMPOTENCY_KEY_REUSED`」✓ |

### 2.4 C-08 `:3` 与记录 §1 版本 —— ❌ 记录仍是 v4（P1-1）

- C-08 `:3`：`状态：**FROZEN v5 / 冻结于 2026-11-01**` ✓ 已改。
- 记录 `FEA-CONTRACT-FROZEN-C08.md:15`：`| 版本 | **v4**（r8 复核 approved） |` —— **仍是 v4**，与文件 v6/状态 v5 不一致。这是你要求我核的第 4 处，**不满足**。
- 连带：§1A `:77`「pin 已更新为 `f61d1bef11fb0788…`」——现行 pin 是 `2e7a5f2b…`（v6 后又变一次），该叙述未更新；§1B `:22`/`:24` 仍写「D06 四项补充待 r9 复核」（r9 已复核出 changes_requested，v6 已处置）；§7 变更记录**标题/表头丢失**（`:86`–`:89` 只有表格行，无「## 7. 变更记录」与表头行）——是 §1A 去重时的附带损伤。

### 2.5 记录 §4 —— ✅

- `:54`：「本契约现覆盖 D06 六项声明**全部**——①SC-R01 ②SC-R02 ③SC-R06 ④SC-R07 ⑤SC-R08 ⑥SC-R09。D06 条件**以 AC8 的完整覆盖检查为准**。」✓
- `:55`：「D06 已由本契约覆盖；`G-DELETE-CONTRACT` 的关闭须经 AC8 + AC9 裁定（C-09 已解环并冻结，不再构成阻塞）。」✓
- 不再出现「另 4 项未写入」「两 Gate 仍不满足」✓。

### 2.6 pin —— ✅

- `verify_pins.ps1`：`PIN AUDIT: PASS (all 13)`，EXIT=0 ✓。
- C-08 当前 blob（HEAD LF）：`2e7a5f2b62655554cc818cc84e4c2358c8ee09d2ab7968e9a9547b2b20f167e6`；记录 §1 `:16` 同值 ✓。

---

## 3. 新增问题（P1 × 2 必改，P2 × 2 建议）

1. **P1-1（冻结记录未同步 v6）**：
   - §1 `:15` 版本 `v4` → **v5**；
   - §1A `:77` 的 pin 叙述 `f61d1bef…` → **`2e7a5f2b…`**（或在 §1A 末尾补「v6 重算」一行，保留历史值）；
   - §1B `:22`/`:24`：把「待 r9 复核」更新为「r9 `changes_requested` → v6 处置 → r10 复核（[FEA-C08-r10](../reviews/FEA-C08-r10.md)）」；
   - 恢复 §7 变更记录的标题与表头（`:86`–`:89`）。
2. **P1-2（UNFREEZE 载体未同步 v6）**：
   - `:43`–`:53` 的 SC-R07 **整段替换为 v6 的 counts 判据**（现仍是 `targets.length = succeeded + failed` 旧三条件）；
   - `:66` 的 `:204` → **`:202`**；
   - 变更记录补一行「2026-11-01 v6 同步：SC-R07 counts 重写 / 行号更正」。
3. **P2-1（SC-R07 `failed` 的依据）**：见 2.1；建议在共同不变量后补一句「`failed` 时实现须把未开始 Task 转 cancelled/skipped（P11 §4.3 停止语义）」，或注明这是 C-08 的额外要求。
4. **P2-2（表述可再精确，非必须）**：「不得用 `targets.length` 与计数相加」的理由可补「`counts` 无 `cancelled`/`interrupted` 字段（Task 状态域有，见 M2-C1 `:861`）→ 终态 total 不闭合」——把「为什么」写全，避免实现者误以为可以用 `counts.total`。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文。
- 未参与 C-08 起草、v6 修订、记录与 UNFREEZE 载体撰写（作者 = DSH）；本轮逐字比对 M2-C1 字段与行号、P11 状态语义，未按转述判定。
- 我出具过 C-08 的 r9（changes_requested）及更早的 FEA-GOV-7 r1/r2、Gate readiness 复核（如实披露）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 未核 SC-R01…SC-R05/SC-R06/SC-R08/SC-R09 的语义质量（本轮只核 6 处；SC-R07 已复核）。
- 未核 P11 全文（只按 `:97`/`:111`/`:115`–`:117` 抽查 failed/cancelled 语义）。
- 未核实现代码（`src/` 不在本 checkout）。
- 未核 C-08 与 C-05/C-13/C-14 接口（本轮无改动）。

—— 报告结束（`verdict: changes_requested`；契约正文 6 处中 5 处 ✓、第 4 处记录侧未改；P1×2 = 记录未同步 + UNFREEZE 载体未同步；P2×2 = `failed` 依据 + 表述）。
