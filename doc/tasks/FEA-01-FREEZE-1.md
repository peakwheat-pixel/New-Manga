---
id: FEA-01-FREEZE-1
title: FEA-01 稳定端口冻结（门禁链最后一环）
kind: governance
governance_version: 3
status: in_progress
approval: user_ruling_2026-11-01_U11_U12
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-C11-PREREQ-1
base_commit: a2bda2f1d
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-01-FREEZE
allowed_paths:
  - doc/tasks/FEA-01-FREEZE-1.md
  - doc/plan/FEA-01_CONTRACT_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-FEA01.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - tools/governance/verify_pins.ps1
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-01-FREEZE-*.md
  - verification/FEA-01-FREEZE/**
---

# FEA-01-FREEZE-1：FEA-01 稳定端口冻结（门禁链最后一环）

## 来源

用户 2026-11-01 追加确认（[ADJ 追加裁决](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) U-12）：首个实现候选选 `FEA-02-CORE`，**但当前明确前置是 FEA-01 稳定端口尚未冻结**（`STATUS` 与 FEA-01 门禁链均如此记载；14 份子契约冻结不能代替这一步）。推进顺序第 1 步 = **完成 FEA-01 稳定端口冻结及完成证据**。

FEA-01 §1 门禁链：用户裁决 → 方案修订+新 hash 复审 → C-01…C-12 逐条冻结 → **FEA-01 冻结** → Task 释放 → 实现。

## 验收标准

- [x] **AC1 冻结落盘**：`doc/plan/FEA-01_CONTRACT_DRAFT.md` 置 `FROZEN v2`（状态行、§1 门禁链 4/4 标注、§2 快照说明、新增 §2A 冻结对账、变更记录冻结行）；`doc/plan/FEA-CONTRACT-FROZEN-FEA01.md` 含 §1 冻结字节 + §1A + §1B + 条件核验 + 稳定端口说明 + 不构成项；pin 为**全部编辑完成后**计算。
- [x] **AC2 端口清单唯一载体**：明确稳定端口清单 = `doc/plan/FEA-C07_API_INVENTORY.md`（C-07 pin `17c8f7016a36…`），FEA-01 不另建第二份（避免双权威）；`verify_pins.ps1` 纳入 FEA01 → **15/15**。
- [x] **AC3 完成证据**：`verification/FEA-01-FREEZE/closeout-check.md` 记录门禁链 4/4、pin 15/15、冻结前后差异与边界。
- [ ] **AC4 独立复核**：`doc/reviews/FEA-01-FREEZE-r1.md` 判 `approved`（P0/P1 = 0）。

## 禁止范围

- **不释放实现 Task**：`FEA-02-CORE` 等候选须另建卡 + 范围冻结 + 独立复核 + 用户确认 `ready`；`G-DELETE-IMPL` 仍 OPEN。
- 不改 14 份已冻结子契约字节（pin 值须保持不变）。
- 不动用户数据、不 push、不改代码。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 冻结前后字节对比 + pin 计算 | 只读 | PASS | 记录 §1B；`Get-FileHash` = `0370c189…` |
| AC2 | pin 审计 15/15 | 只读 | PASS | `verify_pins.ps1` → `PASS (all 15)` |
| AC3 | 完成证据核对 | 只读 | PASS | `verification/FEA-01-FREEZE/closeout-check.md` |
| AC4 | 独立复核 | 只读 | NOT_RUN | 待复核 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无构建产物；仓外一次性脚本与契约线共用同一批残留（`G:\CODEX\New Manga.workspace\tmp\`），处置 `PRESERVE_UNKNOWN`，清单见 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项；无进程占用；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 收口中（2026-11-01）：AC1–AC3 完成（pin `0370c189…`，pins 15/15）；AC4 待独立复核。
