---
id: FEA-GOV-4
title: C-02/C-03/C-11 三份契约草案独立复核
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-3_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-3
base_commit: cc1fe0d8c
branch: null
worktree: null
integration_commit: TBD
delivery_head: edc90fd1b
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 C-02 复核**：指派独立 reviewer 审 V11R 修订单（V-01…V-08），报告入库 `doc/reviews/FEA-GOV-4-c02-review.md`；r1 `changes_requested`（4 P1）→ 处置 → r2 **`approved`**（0 P0/0 P1/3 P2）。 <<MET>>
- [x] **AC2 C-03 复核**：同上，r1 `changes_requested`（2 P1）→ 处置 → r2 **`approved`**（0 P0/0 P1/3 P2）。 <<MET>>
- [x] **AC3 C-11 复核**：同上，r1 `changes_requested`（2 P1）→ 处置 → r2 `changes_requested`（1 P1）→ 处置 → r3 **`approved`**（0 P0/0 P1/3 P2）。 <<MET>>

## 禁止范围

- 不冻结契约、不改草案正文（只有 finding 处置时才改，且需窄面复核）；不改代码/用户数据；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 独立 reviewer 只读复核 | 只读 | `approved`（r2） | `doc/reviews/FEA-GOV-4-c02-r2.md` |
| AC2 | 同上 | 只读 | `approved`（r2） | `doc/reviews/FEA-GOV-4-c03-r2.md` |
| AC3 | 同上 | 只读 | `approved`（r3） | `doc/reviews/FEA-GOV-4-c11-r3.md` |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-C02 | AC1 | `doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md` | `(见提交)` | `cebd34fcc6d5b584978fbe282645d09150ba09a4e30d45204ba5ba06efbc3f09` | CANONICAL |
| E-C03 | AC2 | `doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md` | `(见提交)` | `4c558d86eee9919479227223d591292f61c3ec3101912b58947b9718b62c2cc2` | CANONICAL |
| E-C11 | AC3 | `doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md` | `(见提交)` | `ea902d71c11000b49ae0c66682bd97648250df7fc40c44857f7264292b95b568` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## 独立 Review

- C-02：r1 [review](../reviews/FEA-GOV-4-c02-review.md) → r2 [r2](../reviews/FEA-GOV-4-c02-r2.md) **approved**
- C-03：r1 [review](../reviews/FEA-GOV-4-c03-review.md) → r2 [r2](../reviews/FEA-GOV-4-c03-r2.md) **approved**
- C-11：r1 [review](../reviews/FEA-GOV-4-c11-review.md) → r2 [r2](../reviews/FEA-GOV-4-c11-r2.md) → r3 [r3](../reviews/FEA-GOV-4-c11-r3.md) **approved**
- Reviewer：`c01b-reviewer`（Agent Teams durable teammate task-15/16/17，均独立上下文）
- 三份共处置：C-02 4 P1 + 6 P2；C-03 2 P1 + 4 P2；C-11 3 P1 + 8 P2（含 r2 追加）

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：main 直接提交（治理 Task，无 worktree/branch）
- 结果：**C-02/C-03/C-11 三份草案全部 `approved`**（0 P0 / 0 P1 未解决）
- 已知 P2：各报告 K 条目共 9 条，均已在处置提交中修复或无阻断登记
- 资源：无 worktree、无临时产物、无用户数据访问。
