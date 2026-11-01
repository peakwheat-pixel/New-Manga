---
id: FEA-D07-UNBLOCK
title: D07 解环（修正 C-09 冻结前置 + 补齐五项 D07 条款）
kind: docs
governance_version: 3
status: in_progress
approval: user_ruling_2026-11-01_option_1
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-C14-DRAFT
base_commit: 11b4f4061
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-D07-UNBLOCK
allowed_paths:
  - doc/tasks/FEA-D07-UNBLOCK.md
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md
  - doc/plan/GATE-CONTRACT-CLOSURE-2026-11-01.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-D07-*.md
  - verification/FEA-D07-UNBLOCK/**
---

# FEA-D07-UNBLOCK：D07 解环

## 来源

用户 2026-11-01 裁决：**采用方案①（修正 C-09 的冻结前置并补齐其 D07 条款）**，否决方案②（拆独立小契约，理由：拆得不够完整，三路径 ProtectionPolicy/完整备份清单/软删恢复命令面仍需承载，且会与 C-09 重复定义）。

## 目标

1. 把 C-09 §4 条件③从「`G-DELETE-CONTRACT` 关闭 + `G-CONTRACT` 关闭」改为**可核验的上游契约条件** → 消除循环
2. 补齐 C-09 的 **五项** D07 条款，使 C-09 成为 D07 的完整承载者
3. 不引入任何「部分关闭」Gate 状态

## 验收标准

- [x] **AC1 前置修正**：C-09 §4 条件③改为「C-01b/C-04b/C-06/C-14 均已冻结 + `G-CONTRACT` 已关闭；**本契约不再要求 `G-DELETE-CONTRACT` 关闭**（本契约正是 D07 的承载者）」；并写明 D07 完整覆盖 = 本契约 + C-04b + C-01b 相关条款。 <<MET>>
- [x] **AC2 补软删/恢复/TrashEntry 命令面**：命令名、payload、结果、错误码（引用 ADJ-001 不复写语义）。 <<MET>>
- [x] **AC3 补三路径统一 ProtectionPolicy**：软删/自动清理/显式彻底删除三层如何共用同一判定；引用 ADJ-001 的保护语义。 <<MET>>
- [x] **AC4 补完整备份覆盖清单**：`settings/*.json`、`catalog.sqlite`、`backup/1`、`backup/2` 各自的归属与是否入包；解决方案 `:901` 的「catalog 归属待 D07 冻结」。 <<MET>>
- [x] **AC5 补 `backup/2` 格式契约**：与 `backup/1` 的关系、版本协商、旧包读取（legacy adapter）。 <<MET>>
- [x] **AC6 补自动备份调度归属**：归 Core 还是 Host、与用户手动备份的关系、与 `DatabaseId` 的关系（引用 C-01b SC-18 不复写）。 <<MET>>
- [x] **AC7 独立复核** `approved`（P0/P1 = 0）后冻结 C-09。 <<MET>>
- [ ] **AC8 重新判定 `G-DELETE-CONTRACT`**：仅在 D04/D05/D06/D07 **全部**覆盖后关闭；不引入「部分关闭」。 <<MET>>

## 禁止范围

- **不改 C-01b/C-04b/C-06/C-08/C-14 的冻结字节**（只引用）。若发现冲突 → 走 `CONTRACT-UNFREEZE-<DATE>.md`。
- 不改代码、不动用户数据、不 push。
- **不得把 「D07 已覆盖」写成事实**，直到 AC1–AC6 全部完成且经复核。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 对表 C-09 §4 vs 五份冻结记录 | 文档 | PASS | `doc/plan/FEA-CONTRACT-FROZEN-C09.md:28` |
| AC2–AC6 | 逐项 vs FEA-01 `:58` 七项声明 | 文档 | PASS | 冻结记录 §3 七项覆盖表 |
| AC7 | 独立复核 | 只读 | PASS | `doc/reviews/FEA-C09-r4.md` approved |
| AC8 | Gate 判定 vs 覆盖表 | 文档 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

文档 Task：无 worktree、无构建产物；仓外 tmp 脚本用后即弃。

- worktree：NOT_APPLICABLE
- 临时产物：NOT_APPLICABLE
- 构建产物：NOT_APPLICABLE
- 资源处置：NOT_APPLICABLE

## Closeout Record

- 待关闭时填写。
