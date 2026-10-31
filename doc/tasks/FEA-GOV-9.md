---
id: FEA-GOV-9
title: 夜班收尾与全域一致性核验
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-8_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-8
base_commit: be8726c86
branch: null
worktree: null
integration_commit: 8395205e0
delivery_head: 8395205e0
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-GOV-9
allowed_paths:
  - doc/tasks/FEA-GOV-9.md
  - doc/handoffs/NIGHT-SHIFT-2026-11-01.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-9-*.md
  - verification/FEA-GOV-9/**
---

# FEA-GOV-9：夜班收尾与全域一致性核验

## 来源

FEA-GOV-8 完成：10 份契约全部 `approved`、冻结矩阵 `approved`。夜班可推进的**文档侧**工作已到边界（冻结需用户裁决）。本 Task 做收尾核验，确保夜间成果自洽。

## 验收标准

- [x] **AC1 全域一致性**：STATUS/PLAN/TASK_LEDGER 三处指针一致；10 份契约的 `approved` 状态与各自 review 报告对应；`check.ps1` PASS（3 warnings）。STATUS/PLAN/TASK_LEDGER 一致；10 份契约 review 齐全。 <<MET>>
- [x] **AC2 晨报定稿**：`doc/handoffs/NIGHT-SHIFT-2026-11-01.md` 最终状态（一句话结论/主线/新架构/契约总表/待裁决/明早推荐第一步）；契约总表 + 待裁决 7 项（含推荐与理由）+ 明早推荐第一步。 <<MET>>
- [x] **AC3 独立核验**：由独立 reviewer 只读核验 AC1/AC2，**`approved`**（0 P0/0 P1/9 P2 非阻断，已修 8 条）。 <<MET>>

## 禁止范围

- 不冻结契约、不改代码/用户数据、不 push、不删任何文件。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `check.ps1` + 手工对表 | 只读 | PASS（3 warnings） | `doc/TASK_LEDGER.md` |
| AC2 | 人工审阅 | 文档 | 定稿 | `doc/handoffs/NIGHT-SHIFT-2026-11-01.md` |
| AC3 | 独立 reviewer 只读 | 只读 | `approved` | `doc/reviews/FEA-GOV-9-review.md` |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-NIGHT | AC1/AC2 | `doc/handoffs/NIGHT-SHIFT-2026-11-01.md` | `(见提交)` | `d0ca047dd7f1a95449bf6f60349a12e7c27f413c7cb66bacfb977027547aa2b7` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## 独立 Review

- [FEA-GOV-9-review.md](../reviews/FEA-GOV-9-review.md)：**`approved`**（0 P0/0 P1/9 P2 非阻断；8 条已处置）
- Reviewer：`c01b-reviewer`（Agent Teams durable teammate task-22，独立上下文）

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：main 直接提交（治理 Task）
- 结果：夜班收尾核验通过；晨报定稿；全域指针一致
- 资源：无 worktree、无临时产物、无用户数据访问。
