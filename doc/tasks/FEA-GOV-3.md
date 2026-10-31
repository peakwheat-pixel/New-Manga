---
id: FEA-GOV-3
title: 契约冻结包准备（C-01b/C-02/C-03/C-11）
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-2_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-2
base_commit: 937cbad2a
branch: null
worktree: null
integration_commit: cc1fe0d8c
delivery_head: 18f59e8b8
canonical_evidence_status: complete
resource_closeout_status: complete
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
| E-FREEZE-PKG | AC1/AC2 | `doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md` | `(见提交)` | `5ff040b1e8227f79e57b0b612e8474ee76996a5c511838c1d62e4dab43e439b6` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## 独立 Review

- r1 [FEA-GOV-3-review.md](../reviews/FEA-GOV-3-review.md)：`changes_requested`（P0×0 / P1×1 / P2×5）——C-01b 条件② 漏 ADJ-001 子条件
- r2 [FEA-GOV-3-r2.md](../reviews/FEA-GOV-3-r2.md)：`changes_requested`（P0×0 / P1×2 / P2×3）——FEA-00a 排除理由错误 + pin 未回填
- r3 [FEA-GOV-3-r3.md](../reviews/FEA-GOV-3-r3.md)：**`approved`**（P0×0 / P1×0 / P2×3 非阻断，K-1/K-2/K-3 均已修）
- Reviewer：`c01b-reviewer`（Agent Teams durable teammate task-14，独立上下文）

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：main 直接提交 `cc1fe0d8c`（治理 Task，无 worktree/branch）
- 结果：冻结包定稿（四份草案条件核对 + 11 步四阶段序列 + 回退表 + UNFREEZE 载体）；**C-01b 差 ②b（ADJ-001 依赖注明）+ ③（用户口径）**
- 已知 P2：K-1/K-2/K-3 均已处置
- 资源：无 worktree、无临时产物、无用户数据访问。
