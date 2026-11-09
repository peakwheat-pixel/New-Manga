---
id: FEA-15-PREREQ-3
title: 集成验收准备（隔离干净构建 + 验收矩阵）
kind: acceptance
governance_version: 3
status: done
approval: DSH 自裁 2026-11-09（FEA-15 前置准备；不含正式验收）
suggested_owner: dsh
owner: dsh
reviewer: DSH 集成自验（准备卡，零生产代码变更；正式验收将派独立验证 Agent）
depends_on: []
base_commit: afbc7e411
branch: null
worktree: null
integration_commit: n/a（准备卡，零生产代码）
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-15-PREREQ-3
allowed_paths:
  - doc/tasks/FEA-15-PREREQ-3.md
  - doc/reviews/FEA-15-PREREQ-3-*.md
  - doc/handoffs/FEA-15-PREREQ-3-*.md
  - verification/FEA-15-PREREQ-3/**
  - doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - 不做正式验收（安装包/真实 UI 会话/真实旧库升级按验收计划待条件具备）
  - 不改生产代码、契约、pins
  - 不释放 FEA-14 切片
---

# FEA-15-PREREQ-3：集成验收准备

## 目的

正式验收（方案 §S5）需要安装包、真实 UI 会话与真实旧库升级，当前尚缺 FEA-14 六切片。本卡做**可提前完成**的准备：隔离干净构建验证 + 验收矩阵/前置清单，使正式验收可执行、可复核。

## 交付

1. **隔离干净构建**：在全新 worktree（detached @ `afbc7e411`，无 bin/obj）做 `Release` 解决方案构建。
2. **验收矩阵**：`doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md`（A1–A7 状态、可验收子集、FEA-14 切片顺序、正式验收前置清单）。

## Acceptance Criteria

- [x] **AC1 干净构建**：全新 worktree + `Release` 构建 0 警告 / 0 错误（EXIT 0），日志含 worktree 与 head。 <<MET>>
- [x] **AC2 验收矩阵**：文档列出 A1–A7 状态与正式验收前置清单，注明「准备版不构成正式验收」。 <<MET>>
- [x] **AC3 门禁**：`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-P3-README | AC1–AC3 | `verification/FEA-15-PREREQ-3/README.md` | `-` | `4c23f9d6baab66fa0a0453c51e11b138543de748f5f7fbad008b4304d0f7de2d` | CANONICAL |
| EV-P3-BUILD | AC1 | `verification/FEA-15-PREREQ-3/logs/clean-worktree-build.log` | `-` | `e4d0c5db818946906ee571d4d265674ce0e7de370119dcd1638e86bb2e0b411b` | CANONICAL |
## 证据计划

| # | 命令/步骤 | 判别 |
|---|---|---|
| E1 | `git worktree add <workspace>/FEA-15-PREREQ-3 afbc7e411` + `dotnet build ... -c Release` | EXIT 0、0/0 |
| E2 | 验收矩阵文档评审（DSH） | 覆盖 A1–A7 |
| E3 | `check.ps1`、`verify_pins` | PASS / 18/18 |

## 风险与回退

- worktree 构建会占用磁盘/时间（本次一次性）；构建完成后 worktree 保留在 `G:\CODEX\New Manga.workspace\FEA-15-PREREQ-3`，删除须按 WORKTREE_SAFETY_INVENTORY 流程（登记为资源已知位置）。
- 本卡不做正式验收；不得以本卡结论替代 A2/A3/A4。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| logs | `verification/FEA-15-PREREQ-3/logs/clean-worktree-build.log` | PRESERVE_REFERENCED | `verification/FEA-15-PREREQ-3/logs/clean-worktree-build.log` | `e4d0c5db818946906ee571d4d265674ce0e7de370119dcd1638e86bb2e0b411b` | 证据 |
| build | worktree `bin,obj` | NOT_APPLICABLE | — | — | 一律不提交（workspace 内） |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

## Closeout Record

- **2026-11-09 / DSH（关账）**：AC1–AC3 MET。准备卡（零生产代码变更）。
- **干净构建**：全新 worktree（detached @ `afbc7e411`）Release 构建 **0 警告 / 0 错误**（EXIT 0）。
- **验收矩阵**：`doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md`（A1–A7；正式验收前置 5 条）。
- **Review 口径**：准备卡、零生产代码；DSH 集成自验。正式 FEA-15 验收将派独立验证 Agent。
- **资源**：worktree 保留（KEEP，删除须 inventory 流程）。
- **边界**：0 契约字节、0 pin。
