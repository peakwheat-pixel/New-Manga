---
id: FEA-D07-UNBLOCK
title: D07 解环（修正 C-09 冻结前置 + 补齐五项 D07 条款）
kind: docs
governance_version: 3
status: done
approval: user_ruling_2026-11-01_option_1
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-C14-DRAFT
base_commit: 11b4f4061
branch: null
worktree: null
integration_commit: c22aea60c
delivery_head: c22aea60c
canonical_evidence_status: complete
resource_closeout_status: complete
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
- [x] **AC8 重新判定 `G-DELETE-CONTRACT`**：仅在 D04/D05/D06/D07 **全部**覆盖后关闭；不引入「部分关闭」。 <<MET>>

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
| EV-D07-CONTRACT | AC1–AC6 | `doc/plan/FEA-CONTRACT-FROZEN-C09.md` | `-` | `a3bc17fddb96fc82727aef92caa3552d694e0ea82a154e143bd114d78babc445` | CANONICAL |
| EV-D07-GATE | AC8 | `doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` | `-` | `855b5ade844aab43b3ae70acbad060e7b6361136bc4ba9573d22393f6c1cb4cb` | CANONICAL |

## Resource Manifest

文档 Task：无 worktree、无构建产物；仓外 tmp 脚本用后即弃。

- worktree：NOT_APPLICABLE
- 临时产物：NOT_APPLICABLE
- 构建产物：NOT_APPLICABLE
- 资源处置：NOT_APPLICABLE

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-only | — | NOT_APPLICABLE | — | — | 本卡只改仓库内文档/代码，未创建仓外 worktree、task-env、临时目录或用户数据；2026-11-17 补登表格 |
## Closeout Record

- 待关闭时填写。
- **2026-11-09 / DSH（FEA-DOC-RECONCILE-1 对账关闭）**：AC8 行原有勾选与标记不一致（`[ ]` + `<<MET>>`），本轮修正为 `[x] <<MET>>`；判定依据为 [GATE-DELETE-CONTRACT-CLOSURE-2026-11-01](../plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)（`G-DELETE-CONTRACT` 于 2026-11-01 **✅ CLOSED**，D04–D07 四包条款级承载经 r3 approved 复核）。测试表 AC8 的 `NOT_RUN` 为当时记录，原字节保留，不据此判 PASS。AC1–AC8 全部 MET，故置 `done`。
- **口径补充（2026-11-09，Review REC-06）**：Gate 裁定中 **D07 行 7 为「⚠ 部分」**，由保留项 **L-5** 明文认定关闭（`GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:30,39-40`）；本卡 AC8「全部覆盖」应读作该裁定口径，不表示 D07 逐项无保留，也不表示四表 DDL 已因此冻结。以上为本轮新增说明，不改写既有字节。

