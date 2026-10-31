---
id: FEA-GOV-1
title: AD-003 独立 Review 收口（C-01b 冻结前置②）
kind: governance
governance_version: 3
status: ready
approval: follow_up_of_FEA-C01b_r5_approved_2026-11-01
suggested_owner: dsh
owner: null
reviewer: null
depends_on: []
base_commit: b421c89fc
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-GOV-1
allowed_paths:
  - doc/tasks/FEA-GOV-1.md
  - doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/00_INDEX.md
  - doc/reviews/FEA-GOV-1-*.md
  - verification/FEA-GOV-1/**
---

# FEA-GOV-1：AD-003 独立 Review 收口

## 来源

C-01b 存储契约的 r5 复核已 `approved`（文本层面），但**冻结前置②**未满足：
[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md) 自身记 `G-REVIEW: ADDRESSED_PENDING_R2`，
`doc/reviews/` 中**没有** AD-003 的独立 Review 产物。AD-003 §6 明文要求"复审通过前不作为契约冻结依据"。

## 验收标准

- [ ] **AC1 AD-003 独立复核**：派上下文独立 reviewer 对 AD-003（用户 2026-10-31 裁决记录）做一次只读复核——核对：① 与用户裁决范围一致、无自行扩大；② 与 AD-002 的取代关系（限定 Managed Copy 默认策略）表述准确；③ §3 边界（新导入/旧 Managed/备份/迁移/信任根/外部变化/删除授权/回退）与 ADJ-001 无冲突；④ §4「未冻结与未实现」清单不虚报；⑤ §5 Gate 与 §6 审查安排可执行；⑥ 字节与哨兵口径。报告入库 `doc/reviews/FEA-GOV-1-ad003-review.md`。 <<PARTIAL: 待实现>>
- [ ] **AC2 `G-REVIEW` 状态收口**：复核通过后，更新 AD-003 §5/§6 的 `G-REVIEW` 字段（记录 reviewer / head / 结论 / 日期），并在 `doc/00_INDEX.md` 登记该 Review；若不通过，按 findings 处置后再复核。 <<PARTIAL: 待实现>>

## 禁止范围

- 不修改 AD-003 的**裁决正文**（那是用户裁决记录）；只更新 `G-REVIEW` 状态字段与索引。
- 不改 AD-002/ADJ-001 正文；不改代码；不动用户数据；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 独立 reviewer 只读复核 + 报告 | 只读 | NOT_RUN | 待补 |
| AC2 | 更新 G-REVIEW 字段 + INDEX；`check.ps1` | 只读+文档 | NOT_RUN | 待补 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
