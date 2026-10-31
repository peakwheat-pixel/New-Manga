---
id: FEA-GOV-3
title: 契约冻结包准备（C-01b/C-02/C-03/C-11）
kind: governance
governance_version: 3
status: in_progress
approval: follow_up_of_FEA-GOV-2_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: null
depends_on:
  - FEA-GOV-2
base_commit: 937cbad2a
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-GOV-3
allowed_paths:
  - doc/tasks/FEA-GOV-3.md
  - doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-3-*.md
  - verification/FEA-GOV-3/**
---

# FEA-GOV-3：契约冻结包准备

## 来源

四份契约草案已就位：C-01b（r5 `approved`）、C-02（V11R 修订单）、C-03（外观持久化）、C-11（候选表口径）。本 Task 做冻结之前的**打包与逐条条件核对**，产出「冻结清单」与「用户确认后的执行序列」。

## 验收标准

- [x] **AC1 冻结条件核对表**：对四份草案逐条核对冻结条件（独立复核状态 / 用户裁决项 / `check.ps1`），标注「满足 / 待用户 / 待复核」，并指出每项**阻塞谁**（哪个实现候选）。**已完成**：`doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md` §2（四份 × 3–4 条件全表）。 <<MET>>
- [x] **AC2 执行序列**：给出用户确认后 DSH 的**有序动作清单**（冻结哪份、按什么顺序、每步的验证与回退），使 C-01b→C-02→C-03→C-11 的冻结可以一次性执行且可核。**已完成**：§4 四阶段序列 + §5 回退表。 <<MET>>

## 禁止范围

- 不冻结任何契约（冻结需用户确认前置③ + 独立复核）；不改代码/用户数据；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 四份草案条件核对 + `check.ps1` | 只读 | 核对表完成；check.ps1 PASS | `doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md` §2 |
| AC2 | 序列推演 | 只读 | 四阶段 + 回退表完成 | 同上 §4/§5 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-FREEZE-PKG | AC1/AC2 | `doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md` | `9e350dd6e` | `d8c7d1c4020125b837fb51d543f5c437524652d9758b089ab00d067f777a45d2` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
