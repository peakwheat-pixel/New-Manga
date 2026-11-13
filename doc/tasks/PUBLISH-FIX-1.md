---
id: PUBLISH-FIX-1
title: 修复 S0 单文件发布配方 trimming 失败（IL2026）
kind: implementation
governance_version: 3
status: ready
resume_status: ready
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [REL-GATE-1]
base_commit: 53470bee3
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/PUBLISH-FIX-1
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.DesignSystem/NewManga.DesignSystem.csproj
  - apps/desktop-avalonia/src/NewManga.CoreClient/NewManga.CoreClient.csproj
  - verification/PUBLISH-FIX-1/**
  - doc/tasks/PUBLISH-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# PUBLISH-FIX-1：修复 S0 单文件发布配方 trimming 失败（IL2026）

## 来源与目标

REL-GATE-1（`verification/REL-GATE-1/evidence/rel-gate.json`）实测：`dotnet publish -c Release -r win-x64 -p:PublishTrimmed=true ...` **EXIT 1**，`IL2026` 错误两处：
- `DesignSystemThemeManager.cs(519)`：`AvaloniaXamlLoader.Load(Uri, Uri)` 标注 `RequiresUnreferencedCode`；
- `HostCommandDispatcher.cs(364)`：`JsonSerializer.SerializeToElement<TValue>` 标注 `RequiresUnreferencedCode`。
本 Task 修复这两个 trimming 分析错误（正确标注/抑制或改用可分析 API），使 S0 配方发布成功；不改变运行时行为与既有测试语义。

## Acceptance Criteria

- [ ] **AC1**：定位两处 IL2026 的调用语义与项目 trimming 配置，选择最小、可维护的修复（正确 `UnconditionalSuppressMessage`/`RequiresUnreferencedCode` 标注或可分析替代），记录理由。
- [ ] **AC2**：实施修复；`dotnet build` 解决方案 0 warnings/errors。
- [ ] **AC3**：`dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:PublishTrimmed=true ...` **EXIT 0**，产物为单文件，记录大小；真实 GUI 运行 NOT_RUN（缺少隔离数据根，保持 REL-GATE-1 边界）。
- [ ] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。

## 允许修改范围

- `apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs`
- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`
- 必要时上述两个 `.csproj`（仅 trimming 分析相关属性）
- `verification/PUBLISH-FIX-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

运行时行为改变（除标注/可分析替代）、其他产品模块、契约、依赖、真实用户数据、安装/发布/上传、远端、历史改写。

## 测试要求

`dotnet build` + S0 `dotnet publish` 复验（EXIT/产物/大小）；相关单测（若有）运行；GUI 冒烟仍为 NOT_RUN。
