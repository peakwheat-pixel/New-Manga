---
id: DIAG-M2-REGIONLESS-LOCK-CHANGED-001
kind: research
status: blocked
owner: DeepSeek Harness
base_commit: 5789b30b37dfbf79d9bca707b5fdaaa562ada707
worktree: G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh
branch: agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001
execution_state: BLOCKED_NO_SANDBOX_EXECUTION
evidence_class: STATIC_ONLY (no command executed)
---

# M2 regionless planner `LOCK_CHANGED` 诊断（静态）

## 0. 执行状态声明

本次 Owner 会话**未能执行任何命令**：DSH 沙箱在命令执行前准备阶段失败
（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`，多次、含
子代理独立复现），worktree 写入被 `workspace-write` 拒绝，升级审批无可用通道。
因此 AC1/AC2/AC5 = BLOCKED，AC3/AC4 与 AC2 的比较点定位 = **静态分析（STATIC）**。
所有结论均可由 §4 的行级证据与 `verification/.../reproduce.py` 一次性证伪或证实。

## 1. 结论

regionless page 走 `detect → backfill → ocr` 时，`_backfill_detected_regions`
只重绑 `PlanUnit.region_id`，**未重绑 `target_id`**；`ocr` 的
`StepRun.input_refs` 因而仍冻结自 **Page** target（无 `"region"` 键 ⇒ `None`），
而实际写目标是 **Region**，`RegionStepWriter._persist` 的乐观守卫以 `None` 比对
Region 真实 current revision（detect 已原子写入首版）⇒ `LockBlocked`
(`error_code="LOCK_CHANGED"`)。

**失败比较点**：`src/infrastructure/providers/step_writes.py:219-231`，
不是 `catalog.commit_step` 的锁分支（后者同源比较，恒等）。

## 2. 证据链（worktree @ 5789b30b）

| # | 位置 | 事实 |
|---|---|---|
| 1 | `src/application/tasks/service.py:329-336` | 页面无 Region ⇒ `_plan_region(..., region=None)` |
| 2 | `service.py:346-358` | 计划链前插 `detect` ⇒ `("detect","ocr",...)` |
| 3 | `service.py:360-365` | `target_id = target.page_id`（regionless） |
| 4 | `service.py:384-395` | `PlanUnit(target_id=page_id, region_id=None, expected_lock=page lock)`；`expected_*` 经 grep 确认仅审计、从不用于守卫 |
| 5 | `service.py:650-655` | detect 提交成功后才调用 `_backfill_detected_regions` |
| 6 | `service.py:921-946` | **只 `replace(item, region_id=primary)`**；全文件 grep 证明 `target_id` 无第二处写入 |
| 7 | `service.py:605-618` | `input_refs`/`lock_snapshot` 取自 `catalog.current(unit.target_id)` = Page |
| 8 | `src/infrastructure/sqlite/pipeline.py:562-566, 733-738` | Page `current_revisions` = `{artifact_type: rev}`，**无 `"region"` 键** |
| 9 | `pipeline.py:701-725` | Region `current_revisions` = `{"region": rev}` |
| 10 | `src/infrastructure/providers/handlers.py:341-350` | `expected_current_revision_id=step_run.input_refs.get("region")` ⇒ `None` |
| 11 | `step_writes.py:206-231` + `:278-280` | `BEGIN IMMEDIATE` 内比对 ⇒ `LockBlocked`（rollback 正确，无事务泄漏） |
| 12 | `src/ports/providers/errors.py:152-155` | `LockBlocked.error_code == "LOCK_CHANGED"` |
| 13 | `src/application/editing/service.py:247-274` | `create_region` 原子写首版 ⇒ `current_revision_id` 非空 |
| 14 | `handlers.py:194-217` → `service.py:790-792` | 错误码穿越 seam 保留 |
| 15 | `service.py:966-981` | 终态 `COMPLETED_WITH_FAILURES` |

## 3. 先红判别性预测（`reproduce.py` 会断言；本会话 NOT_RUN）

- ocr `StepRun`: `status=FAILED`, `error_code=LOCK_CHANGED`, `error_detail` 含 `expected None`；
- ocr `target_id == page_id` 且 `region_id == <region>`；`"region" not in input_refs`；
- run `COMPLETED_WITH_FAILURES`；Region `region_revisions` 恰 1 条（零写）。

## 4. 反事实（AC3）

- 正确不变式：`PlanUnit.target_id ≡ 写目标`；应在 `_backfill_detected_regions`
  （detect 提交后、`_record_step_attempt(ocr)` 前）同时重绑 `target_id=primary` 与
  `region_id=primary`，且**不改 `unit_id`**（`terminal_unit_ids` 以它为键）。
- 半修（只改 snapshot 来源）会把 `LOCK_CHANGED` 变成 `TARGET_NOT_FOUND`
  （`commit_step_result` 仍以 Page 为 `target_id` ⇒ `pipeline.py:601-610` rowcount 0）。
- 多 Region fan-out：现状只绑 `region_ids[0]`，其余 Region 停 `NOT_STARTED`；
  修复须保持该语义（fan-out 属调度切片，不得混入）。
- 重启/恢复会自愈：`plan_run(mode="continue")`/`retry_failed_targets` 走
  `catalog.current` 重规划 ⇒ 已有 Region 时按 Region fan-out ⇒ 不再触发。
  **用户症状 = 首次运行失败、重试成功**；修复必须同时固定两条路径。
- 终态计数：`_fail_step`+`_cancel_remaining` 会把进度推到 1.0 而 run 为
  `COMPLETED_WITH_FAILURES`（既有语义）。崩溃窗口内 `continue` 会重置
  `terminal_unit_ids` 但保留 `step_runs`（`service.py:310-312`）——相邻既有风险。

## 5. 修复建议（AC4，须另立 Task，本 Task 未实施）

最小修复 = `service.py:_backfill_detected_regions` 单函数；共享 seam =
`_record_step_attempt` 的 target 权威约定 + `PlanUnit.target_id == 写目标` 不变式。
回归 R0–R5、负向 N1–N7、持久化风险 R-a–R-c 见 Handoff §矩阵。

## 6. 未覆盖 / 未验证

- 全部运行时证据（命令、日志、pytest、git）未执行；
- `$py` 版本未复验；`git diff --check` 未运行；
- 本报告不含任何已执行的运行观测，除文件级 git 元数据读取外无运行事实。
