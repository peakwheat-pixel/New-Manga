# FEA-06-RESIDUAL-3 Review r3（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | `5cabc1ebd`（r2 返修） |
| 结论 | **changes_requested**（P0=0 / **P1=1** / P2=2 / P3=2） |

## 复核结论
终态集合已与 Core `{completed, completed_with_failures, failed, cancelled}` 对齐、`interrupted` 非终态、`HasActionableControl` 保留 RunId、「重试失败/继续」真发 1 帧（变异 A/B 均 RED 且复原 MATCH）。

## P1（新发现）
- **R3-R3-001**：C061（重试失败目标）返回 `{"run_id": child}`，**无 `new_run_id`**（`core_service.py:6216-6220`；`V11R_COMMAND_CONTRACT_V1.md:143`）；`TrackRunControlResult` 只认 `NewRunId` ⇒ 重试后仍轮询已终态父 Run、**子 Run 进度不可见**。

## P2/P3
R3-R3-002 测试未覆盖子 Run 语义；R3-R3-003 retry 幂等键未轮换；R3-R3-004 restart/abandon 未覆盖（interrupted+disposition dead-end）；R3-R3-005 L-R3-5 措辞（public 非 internal）。
