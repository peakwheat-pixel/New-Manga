---
id: FEA-06-PREREQ-2
title: Fluent frontend 激活与 V2 并存边界（组合根 + 双壳入口）
kind: implementation
governance_version: 3
status: proposed
approval: pending_review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-06-PREREQ-1
base_commit: cad5ebde3
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-PREREQ-2
allowed_paths:
  - doc/tasks/FEA-06-PREREQ-2.md
  - apps/desktop-avalonia/src/NewManga.App/Services/**
  - apps/desktop-avalonia/src/NewManga.ThemeEngine/Persistence/**
  - apps/desktop-avalonia/src/NewManga.ThemeEngine/Models/**
  - apps/desktop-avalonia/src/NewManga.ThemeEngine/Serialization/**
  - apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/**
  - apps/desktop-avalonia/src/NewManga.Appearance/**
  - apps/desktop-avalonia/src/NewManga.App/App.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/App.axaml
  - apps/desktop-avalonia/src/NewManga.App/Program.cs
  - apps/desktop-avalonia/src/NewManga.App/Shell/**
  - apps/desktop-avalonia/src/NewManga.App/Services/FrontendSelector*.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Appearance.Tests/**
  - verification/FEA-06-PREREQ-2/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-06-PREREQ-2-*.md
---

# FEA-06-PREREQ-2：Fluent frontend 激活与 V2 并存边界

## 来源

- 设计基线限定 Fluent 仅在 `theme.frontendId` = `builtin.fluent` / `builtin.fluent-dark` 生效，Current V2 不受影响；现状 `App.axaml.cs:96` 无条件创建 `AppShellV2`，无 `frontendId`/`FluentFrontend`/双壳入口（FEA-06-scope-r1 P0-2）。

## 任务拆解

| 项 | 内容 |
|---|---|
| P1 | `FrontendSelector`：读 `AppearanceSettings.FrontendId`，决定启动 V2 壳或 Fluent 壳；未知/缺省 → V2（fail-safe） |
| P2 | `App.axaml.cs`/`Program.cs` 改造：按 selector 创建对应 Shell；V2 既有路径不变 |
| P3 | `Views/Fluent/` 目录与 Shell 骨架（仅导航 + 四页占位；页面内容由 FEA-06 实现） |
| P4 | 测试：selector 选择逻辑（fluent/fluent-dark/v2/未知）+ V2 回归不破 |
| P5 | **W-9 承接（Q-32）**：写者收敛——**先把 `AppearanceCoordinator` 从 `NewManga.App/Services` 迁入 `NewManga.Appearance`（C-03 §2.1 唯一写者位置；PREREQ-1 偏差 D-1）**，再加 `AppearanceCoordinator.SaveAsync` 调 `AppearanceStore.WriteAsync`（唯一写者 = `NewManga.Appearance`，不引入反向引用）；`ThemeSettingsStore.SaveAsync` 标 `[Obsolete]` 并在一个 release 内双写 `presentation-settings.json`（App 侧 sink adapter `IThemeSettingsSink`，避免 ThemeEngine→Appearance 引用） |
| P6 | **W-9 承接（Q-32）**：`Nm.Material.Acrylic.Base/Tint` —— 选 **`ThemeTokenSet` 扩展**路径：`ThemeMaterial` 枚举加 `Fluent` 值 + `ThemeTokenSet` 增加 `Material(Base/Tint)` 字段 + `ThemePackageJson` 序列化；`NmKeys` 加两常量但**不进 `Tokens.Global.axaml`**；`ThemeLayerAllowedKeys`（`DesignSystemThemeManager.cs:123-130`）与 `R14ContractTests` 的 **59/65 计数**同步；C-02 V-07 公开面（`ThemeMaterial` 枚举值）在变更记录中登记 |

## 验收标准

- [ ] **AC1**：`FrontendSelector` 决策表按 **frontendId**（`builtin.current-v2` / `builtin.fluent`）——`builtin.fluent` → Fluent 壳；其余（含缺失/非法）→ V2 + 记录（`builtin.fluent-dark` 是 **visualThemeId**，不参与 selector）。<<TODO>>
- [ ] **AC2**：组合根按 selector 建壳；V2 启动路径与既有测试不回归。<<TODO>>
- [ ] **AC3**：Fluent Shell 骨架存在（四页占位 + 导航），可启动（headless 测试）。<<TODO>>
- [ ] **AC4**：全量 sln 不退化 + 证据。<<TODO>>
- [ ] **AC5（W-9/Q-32）**：双写者收敛 + `ThemeSettingsStore` 兼容写（一个 release）+ 测试。<<TODO>>
- [ ] **AC6（W-9/Q-32）**：`Nm.Material.Acrylic.Base/Tint` 主题层键落地 + 主题包 schema/`ThemeLayerAllowedKeys`/`R14ContractTests` 计数同步。<<TODO>>

## 禁止范围

- 不实现四页内容（FEA-06）；**不改 ThemeEngine 的既有主题包语义**（`newmanga-default` 字节不变；新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围）；不改 Core/契约；不 push。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 并存策略 | 双壳并存：`frontendId` 选择；默认 V2（fail-safe）；Fluent 为可选前端 | 设计基线 + r1 P0-2 |
| W-2b | CLI 优先级 | `--frontend`（显式）**优先于** `AppearanceSettings.FrontendId`；两者都缺省 → `builtin.current-v2`（fail-safe V2） | PREREQ-1 `AppOptions.FrontendId`；AC1 |
| W-2 | 写域 | `App.axaml.cs`/`Program.cs`/`Shell/**`/`Views/Fluent/**` 纳入本卡（r1 P2 指出原 FEA-06 写域缺组合根） | r1 P0-2 |
| W-3 | V2 回归 | V2 既有路径不改语义，只加 selector 分支 | AC2 |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC3 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests` | Avalonia.Headless | NOT_RUN | 待补 |
| AC4 | 全量 sln build/test | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）。

## Closeout Record

- 待关闭时填写。
