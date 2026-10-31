---
id: FEA-GOV-6
title: C-05/C-06 复核 + C-08/C-09/C-12 契约草案
kind: governance
governance_version: 3
status: in_progress
approval: follow_up_of_FEA-GOV-5_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-5
base_commit: f7b22742d
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 C-05/C-06 复核**：派独立 reviewer 复核两份草案，报告入库 `doc/reviews/FEA-GOV-6-c05-c06-review.md`。 <<PARTIAL: 待实现>>
- [ ] **AC2 C-08 草案**：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`——PreparedRun / request builder / candidate store / 配置变化不改已接受任务的契约。 <<PARTIAL: 待实现>>
- [ ] **AC3 C-09 草案**：`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md`——删除/备份/迁移的数据边界与 journal 契约。 <<PARTIAL: 待实现>>
- [ ] **AC4 C-12 草案**：`doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md`——`tools/governance/check.ps1` 的职责边界（机械检查 vs 语义审查）。 <<PARTIAL: 待实现>>

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

## Closeout Record

- Closeout date / DSH：待关闭时填写。
