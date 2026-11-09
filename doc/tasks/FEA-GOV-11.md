---
id: FEA-GOV-11
title: 冻结执行待命（等待用户 4 项裁决）
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-10_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: null
depends_on:
  - FEA-GOV-10
base_commit: f9eb0f859
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-GOV-11
allowed_paths:
  - doc/tasks/FEA-GOV-11.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/plan/FEA-CONTRACT-FROZEN-*.md
  - verification/FEA-GOV-11/**
---

# FEA-GOV-11：冻结执行待命（等待用户 4 项裁决）

## 来源

FEA-GOV-10 完成：**11 份已起草契约全部 `approved`**（C-01b/C-02/C-03/C-04b/C-05/C-06/C-07/C-08/C-09/C-11/C-12），冻结矩阵 `approved`。本 Task 是**待命状态**：等用户回 4 项裁决后，DSH 按冻结矩阵 §2 的 8 步执行。

## 待用户裁决（阻塞本 Task 的唯一输入）

1. **`R`** —— AD-002 责任表/哨兵口径（C-01b 冻结前置③）
2. **U-04** —— Fluent 视觉 per-scheme 例外（C-02 V-05）
3. **U-05a** —— 外观持久化纳动效三态/三类（C-03）
4. **U-05b** —— （C-03 附带项，见晨报）

裁决后 DSH 动作：按 [FEA-CONTRACT_FREEZE_MATRIX](../plan/FEA-CONTRACT_FREEZE_MATRIX.md) §2 执行 C-01b → C-05/C-12 → C-02 → C-03/C-11 → … 每步产出 `doc/plan/FEA-CONTRACT-FROZEN-<ID>.md`。

## 验收标准

- [x] **AC1 冻结 C-01b**：用户回 `R` 后，C-01b 冻结记录落盘（4 条条件逐条勾选）。 <<MET>>
- [x] **AC2 冻结 C-02/C-03/C-11**：U-04/U-05a/U-05b 裁决后冻结。 <<MET>>
- [x] **AC3 释放第一个实现候选**：按 C-11 §7 选候选 → 建卡 → 派独立 Review。**7 份契约已冻结，C-11 已可用**；候选选择待 DSH 提名 + 用户确认（FEA-01/FEA-04b 涉及产品取舍）。 <<MET>>

## 禁止范围

- 未裁决前不冻结、不释放实现 Task、不改契约字节、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 冻结 + `check.ps1` | 用户裁决 | NOT_RUN | 待补 |
| AC2 | 同上 | 用户裁决 | NOT_RUN | 待补 |
| AC3 | 建卡 + Review | 冻结完成 | NOT_RUN | 待补 |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- **2026-11-09 / DSH（FEA-DOC-RECONCILE-1 对账关闭）**：4 项待裁决输入已全部由 [ADJ-2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) 裁决并落盘——`R` = C1=D 零字节 / C3=是；U-04 = 批准（per-scheme + 令牌强制）；U-05a = 纳入（三态三类）；U-05b = 保留（转只读）。C-01b / C-02 / C-03 / C-11 冻结记录均已产出：`doc/plan/FEA-CONTRACT-FROZEN-C01b.md:38`、`FEA-CONTRACT-FROZEN-C02.md:34`、`FEA-CONTRACT-FROZEN-C03.md:35`、`FEA-CONTRACT-FROZEN-C11.md`。AC3 已由 `FEA-01-FREEZE-1`（集成 `bf1c8eb00`）及其后续实现线（FEA-02…FEA-12 done）实际完成。测试表 `NOT_RUN` 为 2026-11-01 当时记录，原字节保留；本轮不改写历史字节。状态 `done` 依据：AC1–AC3 均 MET，且冻结矩阵 §2 的 8 步已由各冻结记录与实现线取代执行。
