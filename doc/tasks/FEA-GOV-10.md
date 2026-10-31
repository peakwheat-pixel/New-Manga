---
id: FEA-GOV-10
title: C-07 API Inventory 独立复核
kind: governance
governance_version: 3
status: in_progress
approval: follow_up_of_FEA-GOV-9_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-9
base_commit: 8395205e0
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-GOV-10
allowed_paths:
  - doc/tasks/FEA-GOV-10.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-10-*.md
  - verification/FEA-GOV-10/**
---

# FEA-GOV-10：C-07 API Inventory 独立复核

## 来源

FEA-01 契约清单中 C-07（`doc/plan/FEA-C07_API_INVENTORY.md`，54 个成员）**已生成但未复核**。本 Task 是契约清单的最后一份复核，完成后 11 份已起草契约全部达到「已复核」。

## 验收标准

- [ ] **AC1 C-07 复核**：独立 reviewer 复核 54 个成员清单与实际代码的一致性（`IReaderProgressSink` 1 + `IHostController` 47 + `IRunController` 6），报告 `doc/reviews/FEA-GOV-10-review.md`；P0/P1 必须处置。 <<PARTIAL: 待实现>>

## 禁止范围

- 不改代码、不改冻结契约、不动用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 独立 reviewer 只读复核 | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
