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
canonical_evidence_status: complete
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

- [ ] **AC1 A1/A5/A6 复核**：干净构建、全量基线、18 pins 三项给出复核时点与 EXIT；与本卡 head 一致或说明差异。 <<PARTIAL: 构建和 pins PASS；pytest 与 .NET 全量 EXIT 1，部分失败根因仍待诊断>>
- [x] **AC2 A2 安装**：安装产物存在则实测安装/启动/四页可达；不存在则 NOT_RUN + 缺口登记（含缺失的打包交付物）。 <<MET>>
- [x] **AC3 A3/A4 真实层**：双入口冒烟与旧库升级/回退的真实层证据；不可得项 NOT_RUN 并给出可用替代证据（App/Host 测试层、FEA-13 五片）。 <<MET>>
- [x] **AC4 A7 汇总与矩阵**：七切片状态/limitation/NOT_RUN 汇总进 `FEA-15-INTEGRATION-ACCEPTANCE.md`，矩阵状态列更新。 <<MET>>
- [ ] **AC5 结论与门禁**：验收结论（通过/带 limitation/不通过）+ `check.ps1`（默认 + `-TaskPath`）+ pins；diff ⊆ allowed_paths。 <<PARTIAL: 验收结论和最终审查由 ZCode 独立会话裁决；最终门禁待固定交付 head 后复核>>
- [x] **AC6 证据**：`verification/FEA-15-ACCEPT-1/` 日志含 EXIT/时点；NOT_RUN 如实登记。 <<MET>>

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
| temp | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\`（隔离根） | PRESERVE_UNKNOWN | — | — | 仓外测试数据、源码档案/对照夹具（含解包失败副本）和专用 Python venv 暂保留；另有 FEA-11 测试硬编码共享 fixtures，候选清单见 `verification/FEA-15-ACCEPT-1/fixture-observation.log`，归属未证明，不清理 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；不写真实用户数据 |
| build | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\clean-tree\apps\desktop-avalonia` | PRESERVE_REFERENCED | — | — | Release 构建产物，暂供复核 |
| worktree | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\clean-tree` | PRESERVE_REFERENCED | — | — | detached `d63d735a712dbe47100db2e72b4d59a73dfd1f62`；主树为任务写入树，不执行清理 |
| runtime ACL | `C:\Python314\python.exe`、`C:\Python314` | PRESERVE_UNKNOWN | — | `verification/FEA-15-ACCEPT-1/python-acl-observation.log` | 插件测试会尝试授予 AppContainer 权限；无运行前 ACL 快照，新增项与归属不明，不擅自撤销 |
| AppContainer profile | 当前用户 profile（测试涉及的插件 profile） | PRESERVE_UNKNOWN | — | — | 测试可创建或复用；无事前清单，不推断新增项，不清理 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1/A1 | `verification/FEA-15-ACCEPT-1/build.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `afb50adff42c1417c0a1a15cec693b15204d7b7d7d4d1417ea0c2bd8abf9ae90` | CANONICAL |
| EV-02 | AC1/A5、AC6 | `verification/FEA-15-ACCEPT-1/pytest-full-retry.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `3f2fe9639e3f349af6f57cd4c4d54da536f655a3b7ed44306cb70136435ccb0b` | CANONICAL |
| EV-03 | AC1/A5、AC3 | `verification/FEA-15-ACCEPT-1/dotnet-full.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `593aac3963b8c2e5fbb857ceab0f1ee6e82fa2d29cf6931d45240029a0f42c70` | CANONICAL |
| EV-04 | AC1/A6、AC2、AC3、AC5、AC6 | `verification/FEA-15-ACCEPT-1/README.md` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `fb83fda733f031e6ff2672a42c6b42b4445677c26afd9b917b1f62244904c77c` | CANONICAL |
| EV-05 | AC2、AC3、AC4 | `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `e60dfcaf686fa4955c870c5ea64d0f31ff8e5bf7b9b93350f55b79d4ea773ddb` | CANONICAL |

## Closeout Record

- 2026-11-10 scope 冻结（`ready`）。未开始。
- 2026-11-10 Codex 认领（`in_progress`），ZCode 独立会话 `sess_2a802094-24f6-4254-9bfa-33cad3a6bf4e` 裁决；主树串行，执行基线 `164ebabcfa90b92fc46c07238280960fc01f7423`。冻结范围不变。
- 2026-11-10 验证进行中：隔离 Release 构建 0 警告/0 错误 EXIT 0；pytest 全量 3515 passed/16 failed/12 skipped EXIT 1；.NET 八项目中 App 与 Host 失败、整体 EXIT 1。日志、隔离限制与 NOT_RUN 见 `verification/FEA-15-ACCEPT-1/README.md`；失败及下一步已交 ZCode 独立会话裁决，未作验收通过结论。
- 2026-11-10 补充证据：四项 App 仓库定位对照 4/4；Host 两项对照 1/1，ACL 异常仍存；专用 venv 插件对照 6 passed/10 failed；legacy/Fluent 仅隐藏进程级 EXIT 0，可见窗口与页面交互 NOT_RUN。现有结论为全量基线未满足、归因部分未定，最终验收结论待上下文独立 Review 与 ZCode 裁决。
