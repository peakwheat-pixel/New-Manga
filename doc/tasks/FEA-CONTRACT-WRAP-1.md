---
id: FEA-CONTRACT-WRAP-1
title: 契约线收尾（L-3 Errata + PLAN 预算卫生）
kind: governance
governance_version: 3
status: in_progress
approval: user_instruction_2026-11-01_autonomous_closeout
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-C14-DRAFT
base_commit: ff432e97c
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-CONTRACT-WRAP-1
allowed_paths:
  - doc/tasks/FEA-CONTRACT-WRAP-1.md
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md
  - doc/plan/FEA-CONTRACT-FROZEN-C04b.md
  - doc/plan/FEA-CONTRACT-FROZEN-C08.md
  - doc/plan/FEA-CONTRACT-FROZEN-C09.md
  - doc/plan/FEA-CONTRACT-FROZEN-C13.md
  - doc/REBASELINE_PLAN.md
  - doc/PLAN-HISTORY.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-WRAP-*.md
  - verification/FEA-CONTRACT-WRAP-1/**
---

# FEA-CONTRACT-WRAP-1：契约线收尾（L-3 Errata + PLAN 预算卫生）

## 来源

用户 2026-11-01 指令：契约线最后两项收尾——**L-3 Errata**（依据 [GATE-DELETE-CONTRACT-CLOSURE-2026-11-01](../plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) §4 的 Errata 表）与**文档预算卫生**（`doc/REBASELINE_PLAN.md` 触发 80% 预算告警）。

边界：**不 push、不改任何已冻结契约字节、不改 Gate 状态、不删改用户数据**。Errata 的处置方式是「**只追加注记、不删原文**」，冻结契约正文一律不动。

## 验收标准

- [ ] **AC1 L-3 Errata**：`doc/plan/GATE-CLOSURE-RULING-2026-11-01.md` 的 `:63`/`:111` 与三份冻结记录（`FEA-CONTRACT-FROZEN-C04b.md` / `-C08.md` / `-C13.md`）的旧「D07 缺多项 / Gate 保持 OPEN / C-09 仍 blocked」口径均**追加 errata 注记、保留原文**；`FEA-CONTRACT-FROZEN-C09.md` 的 L-1 残留项追加处置注记；13 份冻结契约 DRAFT 字节 **0 改动**（`verify_pins.ps1` 13/13 且 pin 值不变）；**C-13 草案 `:203` 保持原字节**（属冻结契约正文，Errata 不得改）。
- [ ] **AC2 PLAN 预算**：`doc/REBASELINE_PLAN.md` 压缩到 **< 5600 B 且 ≤ 50 行**（80% 阈值 = 5600 B / 51 行）；历史终态节点**原样迁入** `doc/PLAN-HISTORY.md`；**不删仍被引用的当前状态**（READY 行、当前 DAG、活动程序、历史快照约束段）；每轮压缩后 `check.ps1` PASS。
- [ ] **AC3 收尾与指针**：`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` / `doc/TASK_LEDGER.md` 指向真实状态；`doc/checkpoints/AUTONOMOUS-2026-11-01.md` 完整（每项一行 + 待裁决 + 收尾）；独立复核 `approved`（P0/P1 = 0）。

## 禁止范围

- **不改 13 份冻结契约草案字节**（改则须 UNFREEZE + 重算 pin，本 Task 无此授权）。
- 不改 Gate 状态（`G-CONTRACT` / `G-DELETE-CONTRACT` 已 CLOSED，`G-DELETE-IMPL` 仍 OPEN，不自我放宽）。
- 不改代码、不动用户数据、不 push、不改其它 Task 的既有证据正文（只追加本 Task 的注记）。

## 测试要求

| 场景/AC | 计划命令或手工命令 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 13 份 DRAFT 与 pins 前后对比 | 只读 | NOT_RUN | 待复核时补 |
| AC1 | 追加注记 vs 裁定 §4 对照 | 文档 | NOT_RUN | 待补 |
| AC2 | PLAN 字节/行数实测 + `check.ps1` | 只读 | NOT_RUN | 待补 |
| AC3 | `check.ps1` + `verify_pins.ps1` | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无构建产物；仓外一次性脚本与 2026-11-01 契约线共用同一批残留（`G:\CODEX\New Manga.workspace\tmp\`），逐项 sha256 见共享清单 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`，处置 `PRESERVE_UNKNOWN`（不删除，保留冻结字节可复现性）。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项；无进程占用、不在 git 跟踪内；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 收口中（2026-11-01）：AC1–AC3 进行中；收口时回填 `integration_commit` / `canonical_evidence_status` / `resource_closeout_status` 与复核报告。
