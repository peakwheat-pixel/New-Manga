---
id: FEA-GOV-7
title: C-08/C-09/C-12 三份契约草案独立复核
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-6_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-6
base_commit: 677f316ac
branch: null
worktree: null
integration_commit: d29cf3698
delivery_head: 79402e5f6
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-GOV-7
allowed_paths:
  - doc/tasks/FEA-GOV-7.md
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md
  - doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-7-*.md
  - verification/FEA-GOV-7/**
---

# FEA-GOV-7：C-08/C-09/C-12 三份契约草案独立复核

## 来源

FEA-GOV-6 完成：C-05/C-06 `approved`，C-08/C-09/C-12 草案已建但未复核。本 Task 补齐这三份的独立复核，使 FEA-01 契约清单除 C-10（待 U-03）外全部达到「已复核」状态。

## 验收标准

- [x] **AC1 C-08 复核**：Run 快照（SC-R01…R05）独立复核，r1 `changes_requested`（1 P1 + 3 P2）→ r2 **`approved`**（3 编辑项）。 <<MET>>
- [x] **AC2 C-09 复核**：删除/备份/迁移（SC-B01…B05）独立复核，r1 `changes_requested`（2 P1 + 4 P2）→ r2 **`approved`**。 <<MET>>
- [x] **AC3 C-12 复核**：检查器边界独立复核，r1 `changes_requested`（2 P2）→ r2 **`approved`**。 <<MET>>

## 禁止范围

- 不冻结契约、不改代码/用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 独立 reviewer 只读复核 | 只读 | `approved`（r2） | `doc/reviews/FEA-GOV-7-r2.md` |
| AC2 | 同上 | 只读 | `approved`（r2） | `doc/reviews/FEA-GOV-7-r2.md` |
| AC3 | 同上 | 只读 | `approved`（r2） | `doc/reviews/FEA-GOV-7-r2.md` |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-C08 | AC1 | `doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md` | `(见提交)` | `1022d7c20d8ad0a499dc7f3dc39d056e14e3f345dd220330c2cf006805e8d2cb` | CANONICAL |
| E-C09 | AC2 | `doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md` | `(见提交)` | `60cf8e3032eeef9d1ad259090d38e98792faea131044e491a25c6f1b10fb9a39` | CANONICAL |
| E-C12 | AC3 | `doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md` | `(见提交)` | `292a54e5eff1afb31f0535bd14ed3c9d55c44ff98f3a9efd769190c1df902ed8` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## 独立 Review

- 三份合并：r1 [review](../reviews/FEA-GOV-7-review.md) → r2 [r2](../reviews/FEA-GOV-7-r2.md) **approved**（共处置 3 P1 + 12 P2）
- Reviewer：`c01b-reviewer`（Agent Teams durable teammate task-20，独立上下文）

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：main 直接提交（治理 Task）
- 结果：**C-08/C-09/C-12 三份 `approved`**（2 轮，3 P1 全部处置）
- 至此 FEA-01 契约清单中除 **C-10**（待 U-03）外全部达到「已复核」
- 资源：无 worktree、无临时产物、无用户数据访问。
