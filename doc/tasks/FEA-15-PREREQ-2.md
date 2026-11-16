---
id: FEA-15-PREREQ-2
title: 集成验收基线核对（全量 pytest 与 .NET 8 项目）
kind: acceptance
governance_version: 3
status: done
approval: DSH 自裁 2026-11-09（FEA-15 集成验收前置：确认全量基线可复现、无已知失败）
suggested_owner: dsh
owner: dsh
reviewer: DSH 集成自验（acceptance 证据卡，零代码变更；正式 FEA-15 验收将另派独立验证 Agent）
depends_on: []
base_commit: 25c0a1ecc
branch: null
worktree: null
integration_commit: n/a（零代码变更）
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-15-PREREQ-2
allowed_paths:
  - doc/tasks/FEA-15-PREREQ-2.md
  - doc/reviews/FEA-15-PREREQ-2-*.md
  - doc/handoffs/FEA-15-PREREQ-2-*.md
  - verification/FEA-15-PREREQ-2/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - 不修代码（只核对基线；若发现失败另立修复卡）
  - 不改契约/pins、不改产品行为
  - 不跑真实用户数据/真实硬件路径
---

# FEA-15-PREREQ-2：集成验收基线核对

## 目的

FEA-15 集成验收要求「隔离干净构建/安装/双 UI 回归/升级与回退报告」。验收前必须先确认**当前 head 的全量测试基线可复现**：pytest 全量与 .NET 8 个测试项目各是多少通过/失败/跳过，与 `STATUS` 记录是否一致，有无**新增失败**（相对上次记录）。

## 步骤

1. `python -m pytest -q`（全量，记录 collected/passed/failed/skipped）。
2. `dotnet test` 逐项目（8 个：App / Appearance / ApplicationCore / CoreClient / DesignSystem / Host / Presentation.Avalonia / ThemeEngine）。
3. 与 `STATUS`「测试基线」行核对：pytest **3395/10**、.NET **1794/0/107**（旧记录）。
4. 输出差异与结论：全绿 / 已知失败 / 新增失败（后者须另立修复卡，不得在验收中掩盖）。

## Acceptance Criteria

- [x] **AC1 pytest 基线**：全量 pytest 结果（collected/passed/failed/skipped）记录且可复现（EXIT 与日志）。 <<MET>>
- [x] **AC2 .NET 基线**：8 个项目逐项结果（通过/失败/跳过）记录。 <<MET>>
- [x] **AC3 差异与结论**：与 STATUS 旧基线对比，明确「无新增失败」或列出新增失败并转修复卡。 <<MET>>
- [x] **AC4 门禁**：`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-P2-README | AC1–AC4 | `verification/FEA-15-PREREQ-2/README.md` | `-` | `b2bd5aa06c51915ff4daa03dfe84afce3b0c1211d1cd66e9b17dfe558de5d758` | CANONICAL |
| EV-P2-PYTEST | AC1 | `verification/FEA-15-PREREQ-2/logs/pytest-full.log` | `-` | `8357e1e88746d072760783feda37045df7905673e6e595d4483eaeb864e54167` | CANONICAL |
| EV-P2-APP | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.App.Tests.log` | `-` | `a775840a31fb88da46b93a7499d59af6dcf6012f445d5a921fe945d524291bd5` | CANONICAL |
| EV-P2-HOST | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.Host.Tests.log` | `-` | `cd602f949ebe6ef6a2d773f300dd1542cafa7f7dec080ae5235ad72b703e0eb0` | CANONICAL |
| EV-P2-OTH1 | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.Appearance.Tests.log` | `-` | `4e15ba8a7baf79f86bd87f51022c9ff79dce9baef6d40e790e7cb7ebbaddf9d4` | CANONICAL |
| EV-P2-OTH2 | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.ApplicationCore.Tests.log` | `-` | `55baf1978d596e98e3daee673d9450e265c6c3606c970a0d3ca966bb0879ccda` | CANONICAL |
| EV-P2-OTH3 | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.CoreClient.Tests.log` | `-` | `7f358a8b480fae673c49e321c50cfaa770be1f1729e48d8f54781562cc5f10e5` | CANONICAL |
| EV-P2-OTH4 | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.DesignSystem.Tests.log` | `-` | `2f688fb87747362f5707ec713d7e0b78fd680b7de56d9b2a78b7b489ff1bf47e` | CANONICAL |
| EV-P2-OTH5 | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.Presentation.Avalonia.Tests.log` | `-` | `f1985f08e6bbd65af375766a2d0efd43f352bc81919647a10e4ea073f8c4306f` | CANONICAL |
| EV-P2-OTH6 | AC2 | `verification/FEA-15-PREREQ-2/logs/dotnet-NewManga.ThemeEngine.Tests.log` | `-` | `3c4df18d946ea8d17631dc6761cc6ab226c106cf95312a57501bd5dd3138b884` | CANONICAL |
## 证据计划

| # | 命令 | 判别 |
|---|---|---|
| E1 | `python -m pytest -q` | 记录 EXIT 与统计 |
| E2 | 逐项目 `dotnet test --no-build` | 记录每项目统计 |
| E3 | STATUS 对比 | 差异表 |
| E4 | `check.ps1`、`verify_pins` | PASS / 18/18 |

## 风险与回退

- 全量 pytest 在本环境可能 >15 分钟：如实记录耗时不缩短口径。
- 若出现失败：只登记，不在本卡修（另立修复卡），不得把 NOT_RUN 写成 PASS。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `25c0a1ecc`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | C:/Users/49745/AppData/Local/Temp | DELETE_SAFE | — | — | 测试隔离 |
| build | `apps/desktop-avalonia/**/bin,obj` | NOT_APPLICABLE | — | — | 既有 ignore |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

## Closeout Record

- **2026-11-09 / DSH（关账）**：AC1–AC4 MET。**零代码变更**（acceptance 证据卡）。
- **基线**：pytest **3446 passed / 0 failed / 10 skipped**（3456 collected，299.94s，EXIT 0）；.NET 8 项目 **1804 passed / 0 failed / 107 skipped**。对比旧记录（3395/10、1794/0/107）**无新增失败**。
- **Review 口径**：本卡无实现变更，按上下文独立口径无需实现 Review；证据为 9 份原始测试日志（EV 表 9 行）。正式 FEA-15 集成验收将另派独立验证 Agent。
- **STATUS 更新**：测试基线行已按实测改写。
- **边界**：0 契约字节、0 pin；diff ⊆ allowed_paths（含 STATUS/PLAN/TASK_LEDGER/PLAN-HISTORY 生命周期文件）。