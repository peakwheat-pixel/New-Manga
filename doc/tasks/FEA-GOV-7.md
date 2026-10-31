---
id: FEA-GOV-7
title: C-08/C-09/C-12 三份契约草案独立复核
kind: governance
governance_version: 3
status: in_progress
approval: follow_up_of_FEA-GOV-6_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-6
base_commit: 677f316ac
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 C-08 复核**：Run 快照（SC-R01…R05）独立复核，报告 `doc/reviews/FEA-GOV-7-c08-review.md`。 <<PARTIAL: 待实现>>
- [ ] **AC2 C-09 复核**：删除/备份/迁移（SC-B01…B05）独立复核，报告 `doc/reviews/FEA-GOV-7-c09-review.md`。 <<PARTIAL: 待实现>>
- [ ] **AC3 C-12 复核**：检查器边界独立复核，报告 `doc/reviews/FEA-GOV-7-c12-review.md`。 <<PARTIAL: 待实现>>

## 禁止范围

- 不冻结契约、不改代码/用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 独立 reviewer 只读复核 | 只读 | NOT_RUN | 待补 |
| AC2 | 同上 | 只读 | NOT_RUN | 待补 |
| AC3 | 同上 | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
