---
id: FEA-15-ACCEPT-1
title: FEA-15 集成正式验收（A1–A7 执行与缺口披露）
kind: acceptance
governance_version: 3
status: in_progress
approval: **DSH 2026-11-10 冻结**；2026-11-10 用户授权接续，ZCode 独立会话裁决改派 Codex 并在 main 主树串行执行（见 `verification/FEA-15-ACCEPT-1/appointment.md`）
suggested_owner: codex
owner: codex
reviewer: null
depends_on:
  - FEA-14-AI-1
base_commit: 164ebabcfa90b92fc46c07238280960fc01f7423
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-15-ACCEPT-1
allowed_paths:
  - doc/tasks/FEA-15-ACCEPT-1.md
  - doc/reviews/FEA-15-ACCEPT-1-*.md
  - doc/handoffs/FEA-15-ACCEPT-1-*.md
  - doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-15-ACCEPT-1/**
out_of_scope:
  - 不修改生产源码/测试（发现问题转诊断/修复卡，不在验收卡内顺手修）
  - 不新建安装包打包管线（若无安装包产物，A2 记 NOT_RUN + 打包缺口登记，不伪造通过）
  - 不改冻结契约字节；不 push
  - 不修改 FEA-14 已收口卡的历史证据
---

# FEA-15-ACCEPT-1：集成正式验收

## 背景

FEA-14 S5 七切片（SET/PREQ/EXPORT/READ/FONT/LIB/EDIT/AI 相关实现卡）已全部收口；`FEA-15-PREREQ-3` 已产出验收矩阵 `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md`（准备版，非正式验收）。本卡执行 FEA-15 §S5 的正式验收：按 A1–A7 复用/重跑证据，对**依赖安装包、真实 UI 会话、真实旧库**的项如实登记 NOT_RUN 或执行，并给出可复核的验收结论与缺口清单。

## Scope 冻结（2026-11-10，DSH）

1. **A1 隔离干净构建**：在无 `bin/obj` 的干净 worktree 复核 Release 构建 0 错误 0 警告（重跑或复用 `FEA-15-PREREQ-3` 证据并核对 head）。
2. **A2 安装**：若存在可安装产物（安装包），执行安装→启动→四页面可达冒烟；若不存在，A2 = NOT_RUN + 明确打包缺口（不伪造）。
3. **A3 双 UI 回归**：legacy `MainWindow.Show()` 与 Fluent shell 两入口冒烟 + 关键路径测试；真实 UI 会话不可得时按测试层证据 + NOT_RUN 登记。
4. **A4 升级与回退**：旧库升级（FEA-13 迁移/备份/恢复证据）+ pre_restore 回退可执行性；真实用户库升级不可得时按 FEA-13/NEW-DB 证据 + NOT_RUN。
5. **A5 全量基线**：pytest + .NET 全量重跑（或复用 PREREQ-2 证据并核对 head）。
6. **A6 契约与 pin**：`verify_pins` 18/18、无未决 UNFREEZE。
7. **A7 FEA-14 汇总**：按冻结卡逐切片汇总（SET/PREQ/EXPORT/READ-1/READ-2/FONT-1/LIB-1/EDIT-1/AI-1 状态、limitation、NOT_RUN），并更新验收矩阵当前状态列。

## Acceptance Criteria

- [ ] **AC1 A1/A5/A6 复核**：干净构建、全量基线、18 pins 三项给出复核时点与 EXIT；与本卡 head 一致或说明差异。 <<PENDING>>
- [ ] **AC2 A2 安装**：安装产物存在则实测安装/启动/四页可达；不存在则 NOT_RUN + 缺口登记（含缺失的打包交付物）。 <<PENDING>>
- [ ] **AC3 A3/A4 真实层**：双入口冒烟与旧库升级/回退的真实层证据；不可得项 NOT_RUN 并给出可用替代证据（App/Host 测试层、FEA-13 五片）。 <<PENDING>>
- [ ] **AC4 A7 汇总与矩阵**：七切片状态/limitation/NOT_RUN 汇总进 `FEA-15-INTEGRATION-ACCEPTANCE.md`，矩阵状态列更新。 <<PENDING>>
- [ ] **AC5 结论与门禁**：验收结论（通过/带 limitation/不通过）+ `check.ps1`（默认 + `-TaskPath`）+ pins；diff ⊆ allowed_paths。 <<PENDING>>
- [ ] **AC6 证据**：`verification/FEA-15-ACCEPT-1/` 日志含 EXIT/时点；NOT_RUN 如实登记。 <<PENDING>>

## 证据计划（L2）

`verification/FEA-15-ACCEPT-1/`：`logs/`（构建、全量基线、pins/api、真实层冒烟或缺口说明）、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 无安装包/真实 UI 不可得 | A2/A3 记 NOT_RUN + 缺口清单，不伪造通过 |
| 真实用户库不可得 | A4 按 FEA-13/NEW-DB 证据 + NOT_RUN |
| 验收发现缺陷 | 只登记，另开诊断/修复卡，不在验收卡内改生产代码 |
| 基线漂移 | 全量基线以本卡 head 重跑为准，记录命令/时点/EXIT |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\`（隔离根） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；不写真实用户数据 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树执行 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Closeout Record

- 2026-11-10 scope 冻结（`ready`）。未开始。
- 2026-11-10 Codex 认领（`in_progress`），ZCode 独立会话 `sess_2a802094-24f6-4254-9bfa-33cad3a6bf4e` 裁决；主树串行，执行基线 `164ebabcfa90b92fc46c07238280960fc01f7423`。冻结范围不变。
