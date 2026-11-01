---
id: FEA-C11-PREREQ-1
title: 实现线强制前置登记（L-1 / L-2 / L-5 → 候选 Task 前置与 AC）
kind: governance
governance_version: 3
status: in_progress
approval: user_ruling_2026-11-01_U09
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-C10-DRAFT
base_commit: 170b384e2
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-C11-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-C11-PREREQ-1.md
  - doc/plan/FEA-C11_IMPL_PREREQS.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-C11-PREREQ-*.md
  - verification/FEA-C11-PREREQ-1/**
---

# FEA-C11-PREREQ-1：实现线强制前置登记

## 来源

用户 2026-11-01 追加裁决 **U-09**（[ADJ-2026-11-01-FEA-DECISIONS](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)「追加裁决」）：**保留 L-1…L-9，不作整体豁免；四表 DDL（L-1）、M2-C1 修订（L-2）、整库恢复独占锁（L-5）分别进入对应实现 Task 的明确前置与 AC。**

本 Task 只做**文档登记**（前置与 AC 落到候选实现 Task 口径），不做实现、不释放任何 Task、不改任何冻结契约字节。

## 验收标准

- [x] **AC1 登记落盘**：`doc/plan/FEA-C11_IMPL_PREREQS.md` 覆盖 L-1 / L-2 / L-5 三项，每项含「归属候选实现 Task（方案 §15.6 口径）→ 实现前必须完成的前置 → 必须写入候选 Task 的 AC → 证据计划（等级/位置）」；并明确 L-1…L-9 其余项维持原约束。
- [x] **AC2 边界**：文档明确「不构成豁免、不释放实现 Task」（`G-DELETE-IMPL` 仍 OPEN；候选须用户确认）；未修改任何冻结契约字节（`verify_pins.ps1` 14/14）；未改代码、未动用户数据、未 push。
- [ ] **AC3 独立复核**：`doc/reviews/FEA-C11-PREREQ-r1.md` 判 `approved`（P0/P1 = 0）。

## 禁止范围

- 不实现任何候选 Task；不创建/释放`ready` 实现卡；不改 `G-DELETE-IMPL` 状态。
- 不改 14 份冻结契约字节；不改 Gate 裁定；不改 C-11 冻结契约正文（本文档为独立登记，不写入 C-11 草案）。
- 不动用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 逐项对照 U-09 与登记文档三列 | 文档 | NOT_RUN | 待复核 |
| AC2 | 14 份 pin 前后对比 + 未改代码检查 | 只读 | NOT_RUN | 待复核 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无 task-env、无构建产物；仓外一次性脚本与 2026-11-01 契约线共用同一批残留（`G:\CODEX\New Manga.workspace\tmp\`），逐项 sha256 见共享清单 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`，处置 `PRESERVE_UNKNOWN`。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项；无进程占用、不在 git 跟踪内；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 收口中（2026-11-01）：AC1/AC2 完成；AC3 待独立复核。
