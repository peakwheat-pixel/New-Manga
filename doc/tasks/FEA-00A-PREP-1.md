---
id: FEA-00A-PREP-1
title: FEA-00a 数据安全评估与下一实现候选建议（FEA-03 前置）
kind: governance
governance_version: 3
status: in_review
approval: pending_user_confirmation
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-02-CORE
base_commit: 135479270
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-00A-PREP-1
allowed_paths:
  - doc/tasks/FEA-00A-PREP-1.md
  - doc/plan/FEA-00A_PREP.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-00A-PREP-*.md
  - verification/FEA-00A-PREP-1/**
---

# FEA-00A-PREP-1：FEA-00a 数据安全评估与下一实现候选建议

## 来源

用户 2026-11-01 裁决（U-12）：首个实现候选 `FEA-02-CORE`（已完成并集成）；**`FEA-03` 还额外依赖 `FEA-00a` 数据安全修复，应后置**（方案 `:640` 候选依赖）。`FEA-02-CORE` done 后无已授权的下一实现候选，本卡先做**只读评估 + 建议**，不实现、不释放任何 Task。

## 验收标准

- [x] **AC1 现状评估**：核对 `FEA-00a` 在方案 §15.6 的口径（`src/infrastructure/providers/`、`src/infrastructure/sqlite/pipeline.py`、明确测试；L2 高风险；§15.5 三处零变化及重启）与当前仓库实际代码/测试现状，列出缺口。 <<MET>>
- [x] **AC2 下一候选建议**：给出 `FEA-03`（及可选 `FEA-00a`）作为下一实现候选的**前置清单、风险、写域与验证等级建议**，并明确「需用户确认后才建 ready 卡」。 <<MET>>
- [x] **AC3 边界**：只读评估 + 文档；不改代码、不释放 Task、不改冻结契约字节、不动用户数据、不 push。 <<MET>>
- [ ] **AC4 独立复核**：`doc/reviews/FEA-00A-PREP-r1.md` 判 `approved`（P0/P1 = 0）。 <<BLOCKED: 待独立复核 FEA-00A-PREP-r1>>

## L 前置适用性（预估）

本卡为文档评估，判 `L-1/L-2/L-5 = NOT_APPLICABLE`（不触及 DB/schema、wire 码、恢复路径）；评估结论若建议 FEA-00a/FEA-03，须在建议里写明它们各自适用的保留项与前置。

## 禁止范围

- 不实现任何候选 Task；不创建 ready 实现卡；不改 `G-DELETE-IMPL` 状态。
- 不改 15 份冻结契约字节（pins 15/15 必须保持）；不动用户数据；不 push。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-PREP-DOC | AC1,AC2 | `doc/plan/FEA-00A_PREP.md` | `-` | `2d8ee1f4ca592a2dba0c8a345973ddad3e8c2149a97951b2308d529ae302de62` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无构建产物；仓外共享临时残留处置沿用 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 2026-11-01 / DSH：评估文档落盘（快照 `15aa7bf3b`；G1–G7、A1–A6、D1–D4）；AC1–AC3 MET；AC4 待独立复核。
