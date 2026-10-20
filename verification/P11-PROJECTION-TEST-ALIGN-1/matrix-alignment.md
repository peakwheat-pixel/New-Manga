# P11-PROJECTION-TEST-ALIGN-1：投影测试对齐 P11 §4.5

**产出**：2026-10-20 · **分支** `agent/dsh/P11-PROJECTION-TEST-ALIGN-1` · **base** `20b087d7e`

## 一、冲突

**两个测试要求 `pending` 状态的 Run 可 `pause`。**

**P11 §4.5「非法转换拒绝清单」**：

| 当前状态 | 仅允许 | **必须拒绝** |
|---|---|---|
| **`Pending`** | scheduler start、`stop` | **`pause`**、`continue`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets` |

**`projection.py:417-418` 与契约一致**：

```python
if status is PipelineRunStatus.PENDING:
    return dict(can_stop=True)        # 无 can_pause
```

**时间线**：

| 提交 | 内容 |
|---|---|
| `da1daf11e`（TASK-013） | 测试写下 `pending → pause 可用` |
| `78b0d439a`（P13） | **故意**把 `PENDING` 从 `running` 集合中拆出 |
| —— | 测试未更新 |

**原始实现是**：

```python
running = {PipelineRunStatus.PENDING, PipelineRunStatus.RUNNING}
if status in running:
    return dict(can_pause=True, can_stop=True)
```

**P13 之后 Pending 单独一支，无 `can_pause`。**

**所以：代码符合冻结契约，测试不符合。改测试，不改代码。**

## 二、改动一：`pending` 测试改名 + 改断言

| 项 | 改前 | 改后 |
|---|---|---|
| 名字 | `test_pending_run_all_waiting_and_pause_stop_enabled` | **`test_pending_run_all_waiting_and_stop_enabled_only`** |
| `can_pause` | `is True` | **`is False`** |

**为什么改名而不是只改断言**（AC1 要求）：

**一个**名字断言了契约禁止的行为**的测试，会持续邀请旧期望回来。**
**改断言而留名字，等于留了一个写着错误结论的标签。**

**改名理由写进了 docstring，包含 P13 与 P11 §4.5 的时间线。**

## 三、改动二：`test_button_matrix_all_statuses` 曾名不副实

**旧函数体只断言了 `pending` 和 `completed` 两个状态，函数名却叫 `all_statuses`。**

**而 `pending` 那半是错的，另外**七个**状态从未被看过**——
**包括 `RUNNING`，也就是暂停按钮存在的理由。**

**改后拆成四个测试**：

### 3.1 `test_button_matrix_matches_p11_4_5_for_every_status` —— 表驱动

```python
P11_BUTTON_MATRIX = {
    # status: (can_pause, can_stop, can_continue, can_restart, can_abandon)
    PENDING:                  (False, True,  False, False, False),
    RUNNING:                  (True,  True,  False, False, False),
    PAUSED:                   (False, True,  True,  False, False),
    BLOCKED:                  (False, True,  False, False, False),
    INTERRUPTED:              (False, False, True,  True,  True),
    COMPLETED:                (False, False, False, False, False),
    COMPLETED_WITH_FAILURES:  (False, False, False, False, False),
    FAILED:                   (False, False, False, False, False),
    CANCELLED:                (False, False, False, False, False),
}
```

**9 个状态全覆盖。失败消息会指出是哪个状态、期望什么、实际什么。**

### 3.2 `test_interrupted_with_a_disposition_offers_nothing`

**P11 §4.5：已有 `interruption_disposition` 的 Interrupted 必须拒绝新的 Continue/Restart/Abandon。**

### 3.3 `test_retry_is_offered_only_for_failures_that_exist`

**`completed_with_failures` 只有在**确实有失败**时才给 `can_retry_failed`。**

### 3.4 `test_button_matrix_all_statuses`（保留）

**仍走 `build_projection` 的端到端路径，断言 `pending` → `(False, True, False)`。**

## 四、判别力：5 个 sabotage 全部被抓

**矩阵测试若与**错误实现**一致就毫无价值。破坏实现，矩阵必须红。**

| # | sabotage（回退成一种可信的错误） | 结果 |
|---:|---|---|
| 1 | **`PENDING` 恢复可暂停**（**正是本 Task 修的缺陷**） | **RED** |
| 2 | `RUNNING` 失去 `pause` | **RED** |
| 3 | `PAUSED` 失去 `continue` | **RED** |
| 4 | `COMPLETED` 仍给 `stop` | **RED** |
| 5 | `INTERRUPTED` 忽略 `disposition` | **RED** |

**`ALL 5 SABOTAGES CAUGHT`。**

**第 1 条是关键**：如果旧期望还在（pending 可 pause），这个 sabotage 会**绿**——
**即旧的测试与缺陷实现彼此同意，谁也不会报警。**

## 五、套件结果

| 范围 | 改动前 | 改动后 |
|---|---|---|
| `tests/workbench/test_projection.py` | **3 failed**, 13 passed | **16 passed** |

**`tests/workbench` 整体剩余失败**：仅 `test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately`，
**属旧 PySide6 栈，r42 §五 明确不释放修复 Task。**

## 六、明确未做

- **未修改 `src/application/tasks/projection.py`**（AC4：不迎合旧期望改产品代码）
- **未修改 `doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md`**
- **未修改 `tests/workbench/test_workbench_viewmodel.py`**（旧栈，不在范围）
- **未改写 TASK-013 的历史内容或提交**（AC5）
- **未新增生产接口**

## 七、可复现

```powershell
$env:PYTHONPATH = "G:\CODEX\New Manga;G:\CODEX\New Manga\src"
python -m pytest tests/workbench/test_projection.py -q
# 期望：16 passed
```

**判别力检查脚本未入库**（一次性验证工具）；逻辑见 §四，
对 `projection._button_enablement` 施加表中破坏即可复现。
