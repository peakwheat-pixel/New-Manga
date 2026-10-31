---
id: FEA-GOV-8
title: 契约冻结准备总表（C-01b…C-12 依赖链与可执行顺序）
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-7_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-7
base_commit: 79402e5f6
branch: null
worktree: null
integration_commit: 43740a7f9
delivery_head: be8726c86
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-GOV-8
allowed_paths:
  - doc/tasks/FEA-GOV-8.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-8-*.md
  - verification/FEA-GOV-8/**
---

# FEA-GOV-8：契约冻结准备总表

## 来源

FEA-01 契约清单中 C-01b/C-02/C-03/C-04b/C-05/C-06/C-08/C-09/C-11/C-12 均已 `approved`（C-07 已生成、C-10 待 U-03）。冻结依赖链分散在各草案的冻结条件里，缺一张**可执行总表**。

## 验收标准

- [x] **AC1 冻结矩阵**：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`——10 份契约 × 冻结条件 × 依赖关系 × 可执行顺序 × 每步阻塞项，一张表可执行。**已完成**：11 份已起草 + C-10（部分）共 12 行、8 步顺序、5 Gate。 <<MET>>
- [x] **AC2 独立复核**：矩阵由独立 reviewer 复核（准确性与可执行性），r1 `changes_requested`（1 P1 + 7 P2）→ r2 **`approved`**（2 编辑项已修）。 <<MET>>

## 禁止范围

- 不冻结契约、不改草案正文、不改代码/用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 起草 + `check.ps1` | 文档 | 矩阵完成；check.ps1 PASS | `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` |
| AC2 | 独立 reviewer 只读复核 | 只读 | `approved`（r2） | `doc/reviews/FEA-GOV-8-r2.md` |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-MATRIX | AC1 | `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | `(见提交)` | `7a5e39c253040be207db78bbc6501c1e19231a91fff0f8ce4c9de58d64029c58` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## 独立 Review

- r1 [review](../reviews/FEA-GOV-8-review.md) → r2 [r2](../reviews/FEA-GOV-8-r2.md) **approved**（共处置 1 P1 + 9 P2）
- Reviewer：`c01b-reviewer`（Agent Teams durable teammate task-21，独立上下文）

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：main 直接提交（治理 Task）
- 结果：**冻结矩阵 `approved`**——12 行 × 条件 × 8 步顺序 × 5 Gate，可执行
- 资源：无 worktree、无临时产物、无用户数据访问。
