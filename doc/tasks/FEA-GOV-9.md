---
id: FEA-GOV-9
title: 夜班收尾与全域一致性核验
kind: governance
governance_version: 3
status: in_progress
approval: follow_up_of_FEA-GOV-8_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-8
base_commit: be8726c86
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 全域一致性**：STATUS/PLAN/TASK_LEDGER 三处指针一致；10 份契约的 `approved` 状态与各自 review 报告对应；`check.ps1` PASS。 <<PARTIAL: 待实现>>
- [ ] **AC2 晨报定稿**：`doc/handoffs/NIGHT-SHIFT-2026-11-01.md` 最终状态（一句话结论/主线/新架构/契约总表/待裁决/明早推荐第一步）；待裁决项完整、含推荐与理由。 <<PARTIAL: 待实现>>
- [ ] **AC3 独立核验**：由独立 reviewer 只读核验 AC1/AC2，报告 `doc/reviews/FEA-GOV-9-review.md`。 <<PARTIAL: 待实现>>

## 禁止范围

- 不冻结契约、不改代码/用户数据、不 push、不删任何文件。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `check.ps1` + 手工对表 | 只读 | NOT_RUN | 待补 |
| AC2 | 人工审阅 | 文档 | NOT_RUN | 待补 |
| AC3 | 独立 reviewer 只读 | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
