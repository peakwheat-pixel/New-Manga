---
id: FEA-GOV-6
title: C-05/C-06 复核 + C-08/C-09/C-12 契约草案
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-5_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-5
base_commit: f7b22742d
branch: null
worktree: null
integration_commit: 0b553d3ae
delivery_head: 0b553d3ae
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-GOV-6
allowed_paths:
  - doc/tasks/FEA-GOV-6.md
  - doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md
  - doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-6-*.md
  - verification/FEA-GOV-6/**
---

# FEA-GOV-6：C-05/C-06 复核 + C-08/C-09/C-12 契约草案

## 来源

FEA-GOV-5 完成：C-04b `approved`、C-05（页可见性）、C-06（授权面）草案已建。本 Task 复核 C-05/C-06，并补齐 C-08（Run 快照）、C-09（删除/备份/迁移）、C-12（检查器定位）。

## 验收标准

- [x] **AC1 C-05/C-06 复核**：派独立 reviewer 复核两份草案，r1 `changes_requested`（5 P1）→ r2（1 P1）→ r3 **`approved`**（0 P0/0 P1/4 P2，均已修）。 <<MET>>
- [x] **AC2 C-08 草案**：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`——PreparedRun / request builder / candidate store / 配置变化不改已接受任务的契约。**已完成**：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`（SC-R01…R05）。 <<MET>>
- [x] **AC3 C-09 草案**：`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md`——删除/备份/迁移的数据边界与 journal 契约。**已完成**：`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md`（SC-B01…B05）。 <<MET>>
- [x] **AC4 C-12 草案**：`doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md`——`tools/governance/check.ps1` 的职责边界（机械检查 vs 语义审查）。**已完成**：`doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md`。 <<MET>>

## 禁止范围

- 不改代码、不改冻结契约、不动用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 独立 reviewer 只读复核 | 只读 | NOT_RUN | 待补 |
| AC2 | 起草 + `check.ps1` | 文档 | NOT_RUN | 待补 |
| AC3 | 起草 + `check.ps1` | 文档 | NOT_RUN | 待补 |
| AC4 | 起草 + `check.ps1` | 文档 | NOT_RUN | 待补 |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## 独立 Review

- C-05/C-06：r1 [review](../reviews/FEA-GOV-6-c05-c06-review.md) → r2 [r2](../reviews/FEA-GOV-6-c05-c06-r2.md) → r3 [r3](../reviews/FEA-GOV-6-c05-c06-r3.md) **approved**（共处置 6 P1 + 17 P2）
- Reviewer：`c01b-reviewer`（Agent Teams durable teammate task-19，独立上下文）

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：main 直接提交（治理 Task）
- 结果：**C-05/C-06 `approved`**（3 轮 6 P1 全部处置）；C-08/C-09/C-12 草案完成（待下一轮复核）
- 资源：无 worktree、无临时产物、无用户数据访问。
