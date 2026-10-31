---
id: FEA-GOV-5
title: C-04b 复核 + C-05/C-06 契约草案（冻结前置补齐）
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-4_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-4
base_commit: edc90fd1b
branch: null
worktree: null
integration_commit: f7b22742d
delivery_head: fc670f248
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-GOV-5
allowed_paths:
  - doc/tasks/FEA-GOV-5.md
  - doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md
  - doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-GOV-5-*.md
  - verification/FEA-GOV-5/**
---

# FEA-GOV-5：C-04b 复核 + C-05/C-06 契约草案

## 来源

C-02/C-03/C-11 已 `approved`（FEA-GOV-4）。FEA-01 契约清单里还有 C-04b（删除协议字段/码表，草案已建）、C-05（页可见性谓词）、C-06（授权面）需要补齐；本 Task 做 C-04b 的独立复核 + C-05/C-06 的草案。

## 验收标准

- [ ] **AC1 C-04b 复核**：指派独立 reviewer 复核 `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`，报告入库 `doc/reviews/FEA-GOV-5-c04b-review.md`；r1 `changes_requested`（5 P1）→ r2（1 P1）→ r3 **`approved`**（0 P0/0 P1/3 P2）。 <<MET>>
- [x] **AC2 C-05 草案**：`doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md`——页可见性谓词（`page.committed >= X ∧ active probe = false ∧ no live save`）的可验证定义、判别方法、失败语义。**已完成**：`doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md`（P1–P6 谓词 + 判别 SQL + 失败语义）。 <<MET>>
- [x] **AC3 C-06 草案**：`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`——授权面（`SourceAccessRegistry` + `source-read` grant）的命令/字段/版本草案。**已完成**：`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`（registry + grant + 4 命令 + 5 安全约束）。 <<MET>>

## 禁止范围

- 不改代码、不改冻结契约（ADJ-001/M2-C1 字节不动）、不动用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 独立 reviewer 只读复核 | 只读 | `approved`（r3） | `doc/reviews/FEA-GOV-5-c04b-r3.md` |
| AC2 | 起草 + `check.ps1` | 文档 | 草案完成；check.ps1 PASS | `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` |
| AC3 | 起草 + `check.ps1` | 文档 | 草案完成；check.ps1 PASS | `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-C04B | AC1 | `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` | `(见提交)` | `2ad91a22c84533654ee403a8a84e6e7170d211862f29b40c48346bdbf0839927` | CANONICAL |
| E-C05 | AC2 | `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` | `(见提交)` | `8d24b4f464b888561bbae80bceb994cfdc481202a65172ffb243bbb21c117673` | CANONICAL |
| E-C06 | AC3 | `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `(见提交)` | `9d8b395ecfbad6649211240748364bbd0e141ec7493c5dbabfe633fbc501be89` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## 独立 Review

- C-04b：r1 [review](../reviews/FEA-GOV-5-c04b-review.md) → r2 [r2](../reviews/FEA-GOV-5-c04b-r2.md) → r3 [r3](../reviews/FEA-GOV-5-c04b-r3.md) **approved**（共处置 6 P1 + 6 P2）
- Reviewer：`c01b-reviewer`（Agent Teams durable teammate task-18，独立上下文）
- C-05/C-06：本 Task 内起草，**待下一轮复核**

## Closeout Record

- Closeout date / DSH：2026-11-01，DSH（Lead / Architect / Integrator）
- 集成：main 直接提交（治理 Task，无 worktree/branch）
- 结果：**C-04b `approved`**（3 轮，6 P1 全部处置）；C-05/C-06 草案完成
- 已知 P2：C-04b 的 K-1/K-2/K-3 已在 `f7b22742d` 处置
- 资源：无 worktree、无临时产物、无用户数据访问。
