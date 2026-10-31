---
id: FEA-GOV-4
title: C-02/C-03/C-11 三份契约草案独立复核
kind: governance
governance_version: 3
status: in_progress
approval: follow_up_of_FEA-GOV-3_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-3
base_commit: cc1fe0d8c
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-GOV-4
allowed_paths:
  - doc/tasks/FEA-GOV-4.md
  - doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md
  - doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md
  - doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-4-*.md
  - verification/FEA-GOV-4/**
---

# FEA-GOV-4：C-02/C-03/C-11 三份契约草案独立复核

## 来源

冻结包（[FEA-CONTRACT_FREEZE_PACKAGE](../plan/FEA-CONTRACT_FREEZE_PACKAGE.md)）列出 C-02/C-03/C-11 各差一轮独立复核。本 Task 在用户裁决前**先把复核做完**，使用户回 `R` 后可直接进入冻结阶段 2/3。

## 验收标准

- [ ] **AC1 C-02 复核**：指派独立 reviewer 审 V11R 修订单（V-01…V-08），报告入库 `doc/reviews/FEA-GOV-4-c02-review.md`；P0/P1 必须处置或明确不通过。 <<PARTIAL: 待实现>>
- [ ] **AC2 C-03 复核**：同上，报告 `doc/reviews/FEA-GOV-4-c03-review.md`。 <<PARTIAL: 待实现>>
- [ ] **AC3 C-11 复核**：同上，报告 `doc/reviews/FEA-GOV-4-c11-review.md`。 <<PARTIAL: 待实现>>

## 禁止范围

- 不冻结契约、不改草案正文（只有 finding 处置时才改，且需窄面复核）；不改代码/用户数据；不 push。

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
