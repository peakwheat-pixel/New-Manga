---
document_id: FEA-C08-r9
kind: independent_review
task_id: FEA-D06-GAP（AC 复核）
round: 9
scope: C-08 v5 的 D06 四项补充（SC-R06…SC-R09）+ UNFREEZE 载体 + 冻结记录 pin
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: a6d0a3263
reviewed_head_full: a6d0a326377902f3b2f78eeeeb2b19f783dcb7e4
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == a6d0a3263）"
reviewed_documents:
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（v5，156 行，blob sha256 f61d1bef…）
  - doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md（104 行）
  - doc/plan/FEA-CONTRACT-FROZEN-C08.md（97 行）
  - 依据：M2-C1 `:137`/`:200`–`:206`/`:213`/`:902`/`:1060`、§6.1 TaskProjection（`:820`–`:859`）、C-04b、P11 §3.3/§4.1
reviewed_sha256:
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: f61d1bef11fb07887753d39c6cb0b36606126eab45a22f0a9a81c34c6e203ea2
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 5
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 13)，EXIT=0，本次实跑（C-08 pin = f61d1bef… 与记录一致）"
captured_at: 2026-11-01T11:18:00+08:00
captured_by: c01b-reviewer
---

# 独立复核 r9：C-08 v5 的 D06 四项补充

**本报告不是** 冻结动作、不释放任何 Task。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 5）。**

四项补充的方向、结构与 UNFREEZE 载体都成立，**但有两处必须先修才能重冻**：

1. **SC-R07 的完成判据用了一个 M2-C1 里不存在的字段**——`succeeded`（M2-C1 全文 0 次；§6.1 投影的字段是 `counts.completed`），且 `targets.length = succeeded + failed` 对 `cancelled`/`failed` 终态与 `skipped` 不成立（会让合法的 `cancelled` Run 被判为「非法态」）。
2. **冻结记录/契约状态行还停在 v4**：文件 `:3` 仍写 `FROZEN v4`，记录 §1 版本仍 `v4`，§4 `:54` 仍写「另 4 项**未写入任何冻结契约**」、`:55` 仍写「C-09 条件③（两 Gate 关闭）**仍不满足**」——与 v5 正文及已冻结的 C-09（`1e0a98734`）矛盾；重冻前必须同步。

| # | 核对项 | 结果 |
|---|---|---|
| 1 | SC-R06 引用 M2-C1 `:203` + 「UI 过渡态」不变量 | **⚠ 部分**：语义对，但**行号错**——`pause/stop 先持久化请求…` 在 **`:213`**（Running 行），`:203` 是 `ControlResult`；「过渡态」是**新增 UI 层要求**，M2-C1 无此条（不冲突，但不该说成「引用」） |
| 2 | SC-R07 完成判定三条件自洽 | **❌ P1**：`succeeded` 字段不存在（应为 `counts.completed`）；等式漏 `skipped`、对 `cancelled`/`failed` 不成立；「已持久化」缺可验证步骤 |
| 3 | SC-R08 retry 两分法 | **✅ 成立**（与 `:200`/`:201`/`:206` 对应；「复用目标集合、不复用冻结上下文」的推论**成立**）——但指纹行号 `:204` 应为 **`:202`** |
| 4 | SC-R09 `request_id` 禁止 + 覆盖范围 | **✅**（明文禁止；覆盖范围与 `:201` 逐字对应；「随 Run History 保留」属实）；建议直接引 M2-C1 `:138`「不得充当幂等键」 |
| 5 | UNFREEZE 载体 + pin + §1A/§1B | **⚠ 部分**：`verify_pins` **13/13 PASS**、pin 与 blob 一致 ✓；但记录 §1 版本 `v4`、§4 两条陈述陈旧（P1-2）、§1A 有重复段落（P2-4） |

---

## 2. 5 处核对明细

### 2.1 SC-R06 vs M2-C1 `:203` —— ⚠ 行号错，语义对

- C-08 v5 SC-R06 写：「**引用 M2-C1 `:203`（不复写）**：`Running` 状态下 `pause`/`stop` **先持久化请求**，当前不可安全中断的 Step 可完成，到安全边界后不再开始下一步。」
- 实核 M2-C1：
  - **`:213`**（状态矩阵 `Running` 行）：「pause 先持久化请求，当前不可安全中断的 Step 可完成，到安全边界后不再开始下一 Step 并转 `paused`；stop 先持久化请求，停止剩余工作并转 `cancelled`，已提交成果保留。」← **这才是被引的原文**。
  - `:203` 是 `ControlResult = {run_id, status, new_run_id?, new_run_status?}` 的定义（「`run_id/status` 始终指被请求的原 Run；仅 `restart` 返回 child」）。
  - 可补强：P11 §4.1 `:97`「`pause_requested`/`stop_requested` 是持久化控制意图，不是额外 Run 状态」——正好支撑「受理≠状态改变」。
- 「UI 显示过渡态而非已暂停」：M2-C1 无「过渡态」条款；该不变量被 C-08 自己标为「**Run 侧不变量（本契约新增）**」——**不算加戏**（而且它是 `:203` ControlResult 语义 + `:902`/`:1060`「事件不是真值」的一致推论），但它是 **UI 层**要求，建议表述为「UI 不得早于 Core 持久化的 `status` 显示 `paused`/`cancelled`；过渡态的具体呈现由 UI 契约/实现决定」，避免把 UI 设计写进 Run 契约（见 P2-2）。

### 2.2 SC-R07 完成判定 —— ❌ P1

C-08 v5 `:87`：条件 2「`targets.length = succeeded + failed`；`completed` ⇔ `failed = 0`；`completed_with_failures` ⇔ `failed > 0` 且 Run 正常结束」。

实核：
- **`succeeded` 在 M2-C1 全文 0 次出现**；§6.1 冻结的 `TaskProjection.counts` 是 `{total, completed, failed, skipped, blocked, waiting, processing}`（`:834`–`:835`），Page 状态是 `waiting|processing|completed|failed|blocked|skipped`（`:846`）。
- 因此等式应写成（终态 completed / completed_with_failures）：`counts.total = counts.completed + counts.failed + counts.skipped`（`skipped` 是计划结果，P11 `:14` 明文）。
- 对 **`cancelled`**（M2-C1 `:221`「未开始 Task 转 cancelled」）与 **`failed`**：存在未处理/被取消目标，`total = completed + failed` **不成立** → 按 C-08 的判据，合法的 `cancelled`/`failed` Run 会被判「非法态」。`failed` 终态同理（部分目标已处理、部分未处理）。
- 修法建议：把条件 2 **限定到** `completed` / `completed_with_failures` 两个状态；`cancelled`/`failed` 另给判据（如「`counts.completed + counts.failed + counts.skipped + counts.waiting + counts.processing + counts.blocked = counts.total`，且 `cancelled` 允许 waiting/processing 残留为 0 或标记 cancelled」——具体以 M2-C1 TaskProjection 的 `PipelineTaskStatus` 值为准，不要发明新字段）。
- 「该状态已持久化」的可验证性：C-08 的验证只测了「伪造投影被拒」与「断网重连靠重读」，**没有测进程重启/事件丢失后重读仍为终态**；建议补一条验证：杀掉/重启后 `GetRunSnapshot` 仍返回同一终态（M2-C1 `:902`/`:1060` 的「以快照为准」）。

### 2.3 SC-R08 retry 两分法 —— ✅ 成立（行号 P2）

- 同键重放：C-08「不重新取快照」← M2-C1 `:200`「同键重放返回该 Run 当前状态」+ `:201`「同键同 fingerprint 返回同一 `run_id` 和当前状态，**不重新展开目标或重取快照**」✓。
- 新建失败目标重试：`RetryFailedTargets`（`:206`）「只接受 `completed_with_failures` 且至少一个失败 Page；新 Run 只冻结该来源 Run 的失败 Page，写 `source_run_id`/`retry_reason="retry_failed_targets"`，源 Run 与其历史不变」✓ C-08 逐条对上。
- **推论成立**：「复用目标集合、不复用冻结上下文」——依据是 `:202` 的 fingerprint「不含首次接受时才读取并冻结的当前 Revision、Lock、settings、Provider、constraint、context 或展开后的目标结果」+ `:201`「新键尝试一次 durable acceptance」→ 新 Run 接受时重新读取并冻结上下文 ✓。**唯一问题**：C-08 把这句引成 `:204`（实际 `:204` 是 `RunSnapshot` DTO），应改 **`:202`**。
- 「对照 P11 §3.3」：P11 §3.3「目标层级」原文「Run / Page Task / StepRun 是不同生命周期层级…失败 Page 可作为新 Run 的输入…」✓ 引用恰当；「新 Run 是独立 Run」还可在 P11 `:50`「新键、相同命令与 scope → 创建独立 Run」找到直接依据（建议一并引）。

### 2.4 SC-R09 断线 receipt —— ✅

- **`request_id` 禁止明文** ✓：「`request_id` 不能充当去重键」；且与 M2-C1 `:138`「`request_id` 只做单次请求/响应关联，**不得**充当幂等键」逐字一致（建议直接引用 `:138` 作为不复写依据，现文只陈述未引）。
- **覆盖范围** ✓ 与 `:201` 一致：「`StartRun` 与 `RetryFailedTargets` 必填；`ControlRun(action="restart")` 必填；其他 `ControlRun` 动作及 `ResumeBlockedRun` 不得传入该字段」→ C-08 的三项清单完全对应 ✓。
- **「随 Run History 保留」** ✓ `:201` 原文「在同一 Core 数据库中跨创建 Run 操作唯一并随 Run History 保留」✓；「不因 Run 结束而清理」是合理推论。
- 「同键重放是唯一找回入口、不新增按 request 查询的命令」✓ 与 M2-C1 无此类命令一致。
- 小项：`:201` 还规定「同键异 fingerprint → `IDEMPOTENCY_KEY_REUSED`」——C-08 SC-R09 未提，建议补一句（让 receipt 语义与幂等键冲突规则闭合）。

### 2.5 UNFREEZE 载体 + pin + §1A/§1B —— ⚠ 部分

- **pin ✓**：`verify_pins.ps1` **PASS (all 13)**；C-08 当前 blob = `f61d1bef11fb0788…`，与记录 §1 `:16` 及 §1A `:77`「pin 已更新为 `f61d1bef…`」一致 ✓。
- **UNFREEZE 载体 ✓**：`doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md` 存在，说明了「为什么需要 UNFREEZE」（D06 六项只覆盖 2 项）、四项条款全文、复核要求与「不构成什么」✓；触发引用 FEA-GATE-READINESS-review P1-1 ✓。
- **§1B ✓/✗**：`§1B :22`「最后一次独立复核 r8 approved；**D06 四项补充待 r9 复核**」、`:24`「v5 的 D06 四项待 r9 复核」——**如实披露** ✓（本报告即 r9；签名后把这两行更新为 r9 approved 即可）。
- **§1 版本 ✗（P1-2）**：`:15` 仍「**v4**（r8 复核 approved）」——文件已是 v5，记录版本与冻结字节口径不一致。
- **§4 陈旧（P1-2）**：`:54`「本契约覆盖 D06 六项中的 **2 项**…**另 4 项未写入任何冻结契约**」、`:55`「C-09 条件③（两 Gate 关闭）仍不满足」——前者与 v5 新增四条款直接矛盾；后者已被 C-09 冻结（`1e0a98734`）与解环取代。
- **§1A 重复（P2-4）**：`§1A` 里「为什么保留原值」「纪律」两段各出现两次（`:75`/`:88`、`:81`–`:85`/`:90`），且 §1A 被排在 §6 之后（`:67`）——与 C-03 记录同类模板残留，建议清理。

---

## 3. 新增问题（P2 × 5，非阻断但建议修）

1. **P2-1（行号引用）**：SC-R06 `:203` → **`:213`**；SC-R08 `:204` → **`:202`**；UNFREEZE 载体 `:30`/`:66` 同样的两处行号需同步（否则重冻后证据链指错）。
2. **P2-2（过渡态措辞）**：SC-R06 第 2 条把「显示过渡态」写进 Run 契约；建议改为「UI 不得早于 Core 持久化的 `status` 显示 `paused`/`cancelled`；过渡态呈现由 UI 契约/实现决定」，并注明这是**本契约新增**（非 M2-C1 引用）。
3. **P2-3（request_id 依据）**：SC-R09 建议直接引 M2-C1 `:138`（「不得充当幂等键」）作为「不复写」依据；另补「同键异 fingerprint → `IDEMPOTENCY_KEY_REUSED`」（`:201`/`:223`）使 receipt 与幂等冲突规则闭合。
4. **P2-4（记录整理）**：FROZEN-C08 §1A 重复段落与位置（见 2.5）；建议同时把 §1B 的「待 r9」更新为 r9 verdict、§1 版本改 v5、§4 两条按 v5 事实改写（P1-2 的具体落点）。
5. **P2-5（「已持久化」验证）**：补「重启/事件丢失后重读仍为终态」的验证动作（见 2.2）；「`GetTaskProjection` 统计与 `RunSnapshot.status` 同源」可引 M2-C1 `:205` 原文。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文。
- 未参与 C-08 起草、v5 修订与 UNFREEZE 载体撰写（作者 = DSH）；本轮逐条对照 M2-C1 原文行号与 §6.1 字段定义，未按转述判定。
- 我出具过 C-08 的更早复核（FEA-GOV-7 r1/r2、Gate readiness 等）与字节复核（如实披露）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 未核 SC-R01…SC-R05 的语义质量（本轮只核 r9 的 5 处）。
- 未核 C-08 与 C-05/C-13/C-14 的接口细节（只确认 §3/§4 未被本 v5 改动）。
- 未核 P11 全文与 M2-C1 其他章节的深层一致性（只按引用行抽查）。
- 未核实现代码（`src/` 不在本 checkout）。

—— 报告结束（`verdict: changes_requested`；P1×2 = SC-R07 判据字段/等式错误 + 冻结记录与文件版本/§4 陈旧；P2×5 = 行号、过渡态措辞、request_id 依据、记录整理、持久化验证）。
