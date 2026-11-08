# FEA-06-RESIDUAL-3 Review r4（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | **`ddc29ecb3`**（r3 返修；父 `5cabc1ebd`；基线 `9429fc210`） |
| 结论 | **`approved`** —— P0=0 / P1=0 / P2=0 / **P3=5** |

## 实跑（reviewer 一手）
build 0/0；全量 .NET **1731 / 0 / 98**（App 804/0/7）；pytest **3390/10**；pins **18/18**；`check.ps1` PASS；API `--check` EXIT 0；diff 24 文件 ⊆ allowed_paths；禁止面零 diff；FEA-09 已恢复。

## P1 复核（R3-R3-001）
- 契约事实：C061 仅 `run_id`（子 Run），C057 才有 `new_run_id`（`core_service.py:6216-6220` / `:6173-6177`；契约 `:143` / `:139`）。
- 代码：`TrackRunControlResult(adoptResultRunId)` 在 C061 采用 `result.RunId`，C057 仍 `NewRunId`；`RetryFailedAsync` 成功 → 轮换键 → 采用子 Run → `StartRunPolling()` → 立即 poll；终态释放语义未回退（`HasActionableControl` 保留）；「开始处理」仍以 `RunId is null` 门控 ⇒ **无双 Run**。
- **变异实测**：①C061 退回只认 `NewRunId` → 2 RED（`Expected "child-run-1" Actual "fake-run-1"`）；②删 retry 后 `StartRunPolling()` → 2 RED；均 sha256 MATCH 复原后 3/3 复绿。

## P3（非阻塞，登记）
- **R4-001** 采纳子 Run 时未失效 `_runProjection`（≈1 poll 窗口内仍显示父终态；连点重试会被 Core 以 `INVALID_RUN_TRANSITION` 拒绝，无数据破坏，1s 自愈）。
- **R4-002** `NewRunId` 分支在 Fluent 侧当前不可达（restart 需 key，Fluent 恒传 null）→ 只能算代码走查结论。
- **R4-003** `TaskProjectionRequests.Last()=="child"` 不能证明由 tick 触发（立即 poll 也记录）。
- **R4-004** 缺「子 Run 无可动作终态 → 释放」用例。
- **R4-005** `limitations.md` r2-P1 段「new_run_id」措辞与 r3 条目矛盾，需收窄。

## 未核实
L-R3-7 跨前端 dead-end 未真机复现；未跑 Release；未重放 opt-in 9 图；未真实 Core C061 联调（App 侧为 fake）。

## DSH 处置
P3 全部登记（R4-001…005 → `FEA-06-RESIDUAL-5`/后续卡）；**P0/P1/P2=0 ⇒ approved**，进入 closeout。
