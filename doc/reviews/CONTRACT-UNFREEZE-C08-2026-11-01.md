# CONTRACT-UNFREEZE-C08-2026-11-01（D06 四项补齐）

**载体类型**：UNFREEZE 记录（冻结契约的字节修订留痕）
**日期**：2026-11-01
**执行人**：DSH（Lead / Architect / Integrator）
**任务**：[FEA-D06-GAP](../tasks/FEA-D06-GAP.md)
**触发**：[FEA-GATE-READINESS-review](FEA-GATE-READINESS-review.md) P1-1（D06 六项声明范围中四项无承载）+ 用户 2026-11-01 裁决「激活 FEA-D06-GAP，走 C-08 的 UNFREEZE 流程补齐四项」

---

## 1. 为什么需要 UNFREEZE

C-08（Run 快照）已于 2026-11-01 冻结（`sha256 37586fb2…`）。独立复核发现它只覆盖 D06 六项声明范围中的 **2 项**：

| D06 声明项（FEA-01 `:57`） | C-08 现状 |
|---|---|
| preview 与发送同源 | ✅ SC-R01 |
| 不可变内容 pin | ✅ SC-R02 |
| **控制 pending 状态** | ❌ 无条款 |
| **真实完成口径** | ❌ 无条款 |
| **retry 是否复用 source run 快照** | ❌ 未回答 |
| **断线 receipt** | ❌ 无条款 |

按冻结纪律，新增条款必须走本载体，不能只重算 pin。

## 2. 补充的四项条款（SC-R06…SC-R09）

### SC-R06 控制 pending 状态（AC1）

**引用 M2-C1 `:213`（控制状态矩阵 Running 行，不复写）**：`Running` 状态下 `pause`/`stop` **先持久化请求**，当前不可安全中断的 Step 可完成，到安全边界后不再开始下一步。

**Run 侧不变量（本契约新增）**：
1. **「控制请求已持久化」≠「状态已改变」**。`ControlRun` 成功返回只证明请求被 Core 接受并持久化，**不证明** Run 已进入 `paused`/`cancelled`。
2. **UI 不得因控制受理而提前显示暂停或结束**：必须以 Core 持久化的 `status` 为准；请求受理后、状态变更前，UI 应显示「暂停中…」这类**过渡态**，而非「已暂停」。
3. **状态变更的唯一权威**是 Core 的 Run 状态持久化（与 SC-R07 的权威源一致）。

**验证**：发出 `pause` → 断言 `ControlResult.status` 仍可为 `running`；UI 断言显示过渡态而非「已暂停」；等到安全边界后再查 → 断言 `status="paused"`。

### SC-R07 真实完成口径（AC2）

**权威持久状态**：Run 的完成状态只以 **Core 持久化的 Run/Task/StepRun 数据**为准（M2-C1 `:137`「同步响应表示接受，不表示长任务完成」；`:902`/`:1060`「事件不是状态真值」）。

**完成判定**：

**所有终态的共同不变量**：`status ∈ {completed, completed_with_failures, failed, cancelled}` **且** `counts.processing = 0` **且** `counts.waiting = 0`（不再有活动工作）。

**逐终态的附加判据**（字段用 M2-C1 §6.1 冻结的 `TaskProjection.counts: {total, completed, failed, skipped, blocked, waiting, processing}`，`:834`）：

| 终态 | 附加判据 |
|---|---|
| `completed` | `counts.failed = 0` 且 `counts.blocked = 0` |
| `completed_with_failures` | `counts.failed > 0` 且 `counts.blocked = 0` |
| `failed` / `cancelled` | **不要求**满足 total 等式——`counts` 没有 `cancelled`/`interrupted` 字段（Task 状态域有，`:861`），终态 total 本就不闭合；只要求共同不变量 |

**不得**用 `targets.length` 与计数相加作等式：`skipped` 是计划结果（P11 `:14`），`blocked`/`waiting`/`processing` 各有语义，简单相加会误判。

**明文的否定**：`RunAccepted` 不证明完成；事件不是状态真值；`GetTaskProjection` 的统计与 `RunSnapshot.status` 必须同源。

**`failed`/`cancelled` 的 `waiting=0` 依据**：P11 `:111` 只规定 Run 级 fatal → `Failed`，未规定未开始 Task 的处置，故本契约把「无 waiting/processing」作为**额外要求**——终态下不应再有排队工作。

**验证**：①伪造 `counts.failed>0` 但 `status=completed` → 非法态；②`status=cancelled` 且 `counts.processing>0` → 非法态；③**重启后** `GetRunSnapshot` 仍返回同一终态与同一 `counts`；④断网重连 → UI 靠重读状态恢复。

### SC-R08 retry 的快照来源（AC3）

**必须先区分两种情形**：

| 情形 | 键 | 是否新建 Run | 快照来源 |
|---|---|---|---|
| **同键重放** | 同一 `idempotency_key` | **否** | **不重新取快照**——M2-C1 `:200` 明文「同键重放返回该 Run 当前状态」 |
| **新建失败目标重试** | 新 `idempotency_key` | **是**（`RetryFailedTargets`） | **见下** |

**新 Run 的快照来源（本契约明确回答）**：
- **目标集合**：**复用**源 Run 的失败 Page 集合（M2-C1 `:206`「只冻结该来源 Run 的失败 Page」），写 `source_run_id` + `retry_reason="retry_failed_targets"`；
- **冻结上下文**（当前 Revision / Lock / settings / Provider / constraint / context）：**重新读取并冻结**——因为 fingerprint 明确**不含**这些（M2-C1 `:202`：「不含首次接受时才读取并冻结的当前 Revision、Lock、settings、Provider、constraint、context」）；
- **结论**：retry **复用「目标集合」但不复用「冻结上下文」**；源 Run 的历史与快照**不变**（`:206`）。

**对照 P11 §3.3**：新 Run 是**独立的 Run**，不是源 Run 的延续；`source_run_id` 只是溯源标记，不构成状态继承。

**验证**：对 `completed_with_failures` 的 Run 发起 retry → 断言新 Run 有 `source_run_id`、目标是失败 Page 子集、且其 `targets` 的 Revision 是**接受时重新读取的**而非源 Run 的；对同键重放 → 断言返回原 `run_id` 且未新建。

### SC-R09 断线 receipt（AC4）

**已有基础（M2-C1 `:200`，不复写）**：事务提交后响应丢失时，**同键重放须找回原 Run**。

**本契约补充的三件事**：

1. **覆盖范围**：仅对**带 `idempotency_key` 的操作**有效——`StartRun`、`RetryFailedTargets`、`ControlRun(action="restart")`（M2-C1 `:201`）。其余 `ControlRun` 动作与 `ResumeBlockedRun` **不得**传入该字段，因此**不提供** receipt 找回能力（它们本身是幂等或可由状态重读判定）。
2. **查询方式**：**同键重放**是唯一的找回入口；**不新增**「按 request 查询」的专用命令。
3. **生命周期**：`idempotency_key` 记录**随 Run History 保留**（M2-C1 `:201`），不因 Run 结束而清理；一旦清理，该键的找回能力即失效——因此**不得**清理仍在 Run History 中的键。

**明文的否定**：
- **`request_id` 不能充当去重键**——M2-C1 `:138` 明文「`request_id` 只做单次请求/响应关联，**不得**充当幂等键」；同键异 fingerprint → `IDEMPOTENCY_KEY_REUSED`（`:201`/`:223`）。
- **不得**用「时间窗口」近似去重（重启后时间基准不可靠）。

**验证**：注入「提交成功但响应丢失」→ 用同键重放 → 断言找回原 `run_id`、无第二个 Run；用 `request_id` 相同但 `idempotency_key` 不同 → 断言这是**两个不同操作**（不被去重）。

## 3. 复核要求

- 四项条款须经**上下文独立**复核（新子 agent，只读被审 head）。
- 复核须特别检查：**是否把 M2-C1 的既有语义重写了一遍**（应引用不复写）；**`request_id` 禁止作去重键**是否明文；**retry 的两分法**是否与 M2-C1 `:200`/`:206` 一致。

## 4. 不构成什么

- 不构成 M2-C1 的修改（本载体只改 C-08）。
- 不构成 `G-DELETE-CONTRACT` 的关闭（须 AC8 完整覆盖检查后另行裁定）。
- 不构成远端 push 授权。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：四项条款（SC-R06…SC-R09）+ 用户给的既有语义约束 + 复核要求 | DSH |
| 2026-11-01 | **v6 同步**：SC-R07 改为 `counts.*` 判据（M2-C1 `:834`）；SC-R08 行号 `:204`→`:202`；SC-R06 引 `:213`；SC-R09 引 `:138` + `IDEMPOTENCY_KEY_REUSED` | DSH |
