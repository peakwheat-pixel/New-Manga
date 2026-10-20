---
id: P11-PROJECTION-TEST-ALIGN-1
title: 让 projection 测试对齐 P11 §4.5 冻结契约
kind: test-alignment
governance_version: 3
status: ready
language: zh-CN
parent: P13
blocked_by: null
approval: released_by_r42_20261020
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: 0e93a5687
branch: agent/dsh/P11-PROJECTION-TEST-ALIGN-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P11-PROJECTION-TEST-ALIGN-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P11-PROJECTION-TEST-ALIGN-1
allowed_paths:
  - tests/workbench/
  - verification/P11-PROJECTION-TEST-ALIGN-1/
---

# P11-PROJECTION-TEST-ALIGN-1：让 projection 测试对齐 P11 §4.5

## 来源与目标

**来源**：`verification/PDF-STREAM-FIX-1/full-suite-failure-classification.md`（C1）与 r42 裁定 §四。

**两个测试要求 `pending` 状态的 Run 可 `pause`，而 P11 §4.5 明确要求拒绝。**

**P11 §4.5「非法转换拒绝清单」**：

| 当前状态 | 仅允许 | **必须拒绝** |
|---|---|---|
| **`Pending`** | scheduler start、`stop` | **`pause`**、`continue`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets` |

**`src/application/tasks/projection.py:417-418` 正是这么实现的**（`PENDING` 只返回 `can_stop=True`）。

**时间线（`git log -L` 证据）**：

| 提交 | 内容 |
|---|---|
| `da1daf11e`（TASK-013） | 测试写下 `pending → pause 可用` 的期望 |
| `78b0d439a`（P13） | **故意**把 `_button_enablement` 拆开：`RUNNING` → pause+stop；**`PENDING` → 仅 stop** |
| —— | **测试未随之更新** |

**所以代码符合冻结契约，测试不符合。**

## Acceptance Criteria

- [ ] **AC1 `pending` 行**：`can_pause` 为 `False`、`can_stop` 为 `True`；
  测试名与断言一致（当前测试名 `..._pause_stop_enabled` 若与新语义冲突，须改名或加注说明）。
- [ ] **AC2 其余状态矩阵**：`running` / `paused` / `blocked` / `interrupted` / `completed` /
  `completed_with_failures` / `failed` / `cancelled` 的可达按钮组合与 P11 §4.5 一致。
- [ ] **AC3 双文件一致**：`test_pending_run_all_waiting_and_pause_stop_enabled` 与
  `test_button_matrix_all_statuses` 的期望互相一致，且都与契约一致。
- [ ] **AC4 零 `src/`**：**不改 `projection.py` 去迎合旧期望**；不改任何产品代码。
- [ ] **AC5 历史保留**：TASK-013 的历史内容与提交保持历史事实，不因测试更新而改写。
- [ ] **AC6 不回归**：`tests/workbench` 其余测试与 `tests/pipeline`（94 passed）保持通过。

## 允许修改范围

- `tests/workbench/test_projection.py`
- `verification/P11-PROJECTION-TEST-ALIGN-1/`

## 禁止范围

- 不得修改 `src/application/tasks/projection.py` 或任何 `src/**`
- 不得修改 `doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md`
- **不得因为「旧栈不修」的策略而跳过本 Task**——`test_projection.py` 测的是应用层
  `build_projection`，**不是 PySide6 专属**，该策略不适用
- 不得修改 `tests/workbench/test_workbench_viewmodel.py`（属旧 Qt 栈，不修）

## 测试要求

- 更新后两个测试须在 `pending` 行断言 `can_pause=False`
- 须给出**逐状态**的矩阵对照表作为证据，而不只是「测试变绿」
- 验证记录区分 `pass` / `skip` / `fail`

## 依赖、风险与阻塞

| # | 项 |
|---|---|
| **R1** | 更新后可能出现「除 `pending` 外还有别的状态与契约不一致」——若发现，须记录并交 Codex，不得顺手扩大到本 Task 之外的修复 |
| **R2** | 测试名含 `pause_stop_enabled`，与新语义（pending 无 pause）冲突。改名会削弱与历史提交的可追溯性，**须在测试内加注释说明改名/保留的理由** |

## 交付与运行记录

（未开始）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

**本 Task 无资源删除、迁移或归档。**

| resource | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|
| **（无）** | — | **NOT_APPLICABLE** | — | — | 仅测试对齐与证据 |

**closeout_counts**：`deleted=0`、`moved=0`、`migrated=0`、`archived=0`。

## Closeout Record

（未开始）
