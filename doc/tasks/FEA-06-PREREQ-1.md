---
id: FEA-06-PREREQ-1
title: 外观持久化与 Fluent 令牌生成（C-03 落地 + G-1/G-1b/G-1c）
kind: implementation
governance_version: 3
status: proposed
approval: pending_review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-04b
base_commit: cad5ebde3
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-06-PREREQ-1.md
  - apps/desktop-avalonia/src/NewManga.Appearance/**
  - apps/desktop-avalonia/src/NewManga.ThemeEngine/**
  - apps/desktop-avalonia/src/NewManga.App/Services/Appearance*.cs
  - apps/desktop-avalonia/src/NewManga.App/AppOptions.cs
  - apps/desktop-avalonia/src/NewManga.App/Program.cs
  - apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - verification/FEA-06-PREREQ-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-06-PREREQ-1-*.md
---

# FEA-06-PREREQ-1：外观持久化与 Fluent 令牌生成

## 来源

- C-03（`doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md`）要求 `NewManga.Appearance` + `AppearanceCoordinator` 写 `presentation-settings.json`；仓库现状**无该项目**（FEA-06-scope-r1 P0-1）。
- 设计基线 `doc/design/fluent-v1/01-design-tokens.md` 的 G-1/G-1b/G-1c（`Nm.Focus.Ring.*`、`Nm.Corner.Fluent.*`、`Nm.Material.*`、`Nm.Elevation.*`）无代码承接（r1 P1-1）。

## 任务拆解

| 项 | 内容 |
|---|---|
| P1 | 新建 `NewManga.Appearance` 项目：`AppearanceSettings` 记录（frontendId/visualThemeId/motion.mode/motion.categories/corners/material/layout.*/followSystemAccent/schemaVersion）、JSON 读写（原子写、schemaVersion 迁移）、默认值 |
| P2 | `AppearanceCoordinator`（App 侧）：读取 → 应用主题/动效 → 变更通知；`AppOptions` 暴露 `FrontendId`；`Program.cs` 装载 |
| P3 | 令牌生成：`NmKeys.g.cs`/`Tokens.Global.axaml` 增加 G-1/G-1b/G-1c 令牌（Focus.Ring / Corner.Fluent / Material / Elevation），与设计基线一致 |
| P4 | 三态动效：`motion.mode` = `off`/`reduce`/`full`；`motion.categories` = `off` 时 0ms 反馈（`02-motion.md`） |

## 验收标准

- [ ] **AC1**：`NewManga.Appearance` 项目 + 记录 + 原子读写 + schemaVersion 迁移；单测覆盖（往返/坏文件/版本迁移）。<<TODO>>
- [ ] **AC2**：`AppearanceCoordinator` 读取后应用主题与动效；`AppOptions.FrontendId` 可注入；既有 ThemeEngine 回归。<<TODO>>
- [ ] **AC3**：G-1/G-1b/G-1c 令牌代码存在且与 `01-design-tokens.md` 值与命名一致；`NmKeys.g.cs` 生成器同步。<<TODO>>
- [ ] **AC4**：`motion.mode` 三态 + `motion.categories=off` 语义有测试；reduce/full 差异可测。<<TODO>>
- [ ] **AC5**：全量 sln 不退化（基线 949/0/57）+ 证据。<<TODO>>

## 禁止范围

- 不改四页 UI（FEA-06）；不改 Core/契约；不 push。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | C-03 实现归属 | 独立前置任务（本卡），不并入 FEA-06 | FEA-06-scope-r1 P0-1 |
| W-2 | 项目命名 | `NewManga.Appearance`（C-03 冻结草案指定名） | C-03 |
| W-3 | 令牌缺口 | G-1/G-1b/G-1c 在本卡生成，FEA-06 只消费 | 设计基线 `01` |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | `dotnet test apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests` + `NewManga.App.Tests` | .NET | NOT_RUN | 待补 |
| AC5 | 全量 sln build/test | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）。

## Closeout Record

- 待关闭时填写。
