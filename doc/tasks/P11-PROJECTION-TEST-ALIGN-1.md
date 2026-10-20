---
id: P11-PROJECTION-TEST-ALIGN-1
title: 让 projection 测试对齐 P11 §4.5 冻结契约
kind: test-alignment
governance_version: 3
status: closed_with_limitations
language: zh-CN
parent: P13
blocked_by: null
approval: released_by_r42_20261020
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: 20b087d7e
branch: agent/dsh/P11-PROJECTION-TEST-ALIGN-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P11-PROJECTION-TEST-ALIGN-1
integration_commit: 9c594cd4f
delivery_head: 9c594cd4f
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P11-PROJECTION-TEST-ALIGN-1
allowed_paths:
  - tests/workbench/
  - verification/P11-PROJECTION-TEST-ALIGN-1/
<!-- r191: base_commit is the parent of this branch's first commit; delivery_head is the branch tip; integration_commit is the mainline fast-forward point. Previously all three carried the commit that happened to be HEAD when the file was authored. -->
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

- [x] **AC1 `pending` 行** <<MET>>
- [x] **AC2 其余状态矩阵** <<MET>>
- [x] **AC3 双文件一致** <<MET>>
- [x] **AC4 零 `src/`** <<MET>>
- [x] **AC5 历史保留** <<MET>>
- [x] **AC6 不回归** <<MET>>

### AC 证据

| AC | 证据 |
|---|---|
| AC1 | `can_pause is False` / `can_stop is True`；测试改名 `..._stop_enabled_only` 并在 docstring 说明理由 |
| AC2 | `P11_BUTTON_MATRIX` 表覆盖全部 **9 个** `PipelineRunStatus`；另加 Interrupted-with-disposition 与 retry-only-when-failures 两个专项 |
| AC3 | `test_button_matrix_matches_p11_4_5_for_every_status` + `test_button_matrix_all_statuses`（端到端）互相一致，且都与 §4.5 一致 |
| AC4 | `src/` 零改动 |
| AC5 | TASK-013 历史与 `da1daf11e` 未改写；改名理由记录在 docstring 与证据 |
| AC6 | `tests/workbench/test_projection.py` 16 passed；`tests/pipeline` 94 passed |

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
| EV-PROJ-TEST | AC1/AC2 | `tests/workbench/test_projection.py` | 9c594cd4f | - | CANONICAL |
| EV-PROJ-DOC | AC2/AC3 | `verification/P11-PROJECTION-TEST-ALIGN-1/matrix-alignment.md` | 9c594cd4f | - | CANONICAL |
| EV-ZC-REVIEW | Review | `verification/TEST-ENV-ASSUMPTIONS-1/dsh-zcode-review-r189.md` | b047e5947 | - | CANONICAL |
| EV-R101R102 | R-101/R-102 | `verification/P11-PROJECTION-TEST-ALIGN-1/r101-r102-closure.md` | 871a0171d | - | CANONICAL |

## Resource Manifest

**本 Task 无资源删除、迁移或归档。**

| resource_type | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|
| （无） | — | NOT_APPLICABLE | — | — | 仅测试对齐与证据 |

**closeout_counts**：`deleted=0`、`moved=0`、`migrated=0`、`archived=0`。

## Closeout Record

- **Closeout date**：2026-10-20 · **Reviewer**：待 ZCode（按协作协议 §5）
- **canonical_evidence_status**：`complete`
- **resource_closeout_status**：`complete`
- **删除、迁移、归档数量/字节数**：**0**

### 改动清单

| 文件 | 性质 |
|---|---|
| `tests/workbench/test_projection.py` | 1 个测试改名 + 1 个测试拆成 4 个（表驱动 9 状态）|

**`src/` 零改动。**

### 限制

| # | 限制 |
|---|---|
| **L1** | **已由 ZCode 独立 Review（r189）**：**`approve`**（无阻断条件）|
| **L2** | **仅断言按钮**enabled**状态**；按钮的可见性/布局不在范围 |
| **L3** | **`P11_BUTTON_MATRIX` 是对 §4.5 的人工转写**，若契约变更需同步更新——表驱动让它只改一行，但不会自动发现契约变更 |
| **L4** | **`test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately` 仍失败**，属旧 PySide6 栈，r42 §五 不释放 |

### ZCode Review r189 的处置

**产出**：`verification/TEST-ENV-ASSUMPTIONS-1/dsh-zcode-review-r189.md`（两个 Task 同一份）
**结论**：**`approve`**（无阻断条件）。ZCode **独立读取 P11 §4.5 原文**逐行核对了 9 行矩阵，全部一致。

**确认的两点**：

- **`INTERRUPTED` 无处置时 `can_stop=False` 是契约明文，不是我的推论**——
  §4.5 的 Interrupted 行「必须拒绝」列逐字写有 `stop`。我在 Task 里的表述过谦。
- **`can_retry_failed` 不进 5 列矩阵是有意拆分**，不是遗漏：
  它是 `has_failures` 的函数而非 status 的函数，且已有两个专项测试覆盖两个方向。

**两条非阻断建议：r190 已全部闭合**（见 `verification/P11-PROJECTION-TEST-ALIGN-1/r101-r102-closure.md`）：

| 项 | 内容 |
|---|---|
| **R-101** | **已闭合**：补两条端到端测试（有/无 disposition 各一条），双向钉住 `build_projection` 的接线 |
| **R-102** | **已闭合**：矩阵改为 dict 全等；实测旧五列检查会漏报多余键 |

### r190 补充：R-101 / R-102 已闭合

| 项 | 结果 |
|---|---|
| `test_projection.py` 测试数 | 16 → **18** |
| 判别力 | 破坏接线 → R-101 测试 **RED**；PENDING 多发键 → 矩阵 **RED** |

**判别力验证中我犯的错（本会话第三次同类）**：第一次 sabotage patch 了
`application.tasks.projection._button_enablement`，测试仍绿——**因为测试文件
`from ... import _button_enablement` 持有自己的引用**。改 patch 测试模块的绑定后才 RED。

**「测试没红」与「缺陷不存在」在输出上无法区分，这是三次共同的表现形式。**

### 后续建议

1. 建议在契约（P11）与投影矩阵之间加一个自动对照（L3），避免人工转写漂移
2. R-003 / R-103（`base_commit` 口径）移交 Codex

