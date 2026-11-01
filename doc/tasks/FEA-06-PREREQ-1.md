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
  - apps/desktop-avalonia/NewManga.sln
  - apps/desktop-avalonia/src/NewManga.Appearance/**
  - apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj
  - apps/desktop-avalonia/src/NewManga.DesignSystem/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - apps/desktop-avalonia/src/NewManga.ThemeEngine/**
  - apps/desktop-avalonia/src/NewManga.App/Services/Appearance*.cs
  - apps/desktop-avalonia/src/NewManga.App/AppOptions.cs
  - apps/desktop-avalonia/src/NewManga.App/Program.cs
  - apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Appearance.Tests/**
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
| P1 | 新建 `NewManga.Appearance` 项目：`AppearanceSettings` 记录 **按 C-03 §2.2 逐字段**（`appearance.mode`/`appearance.contrast`/`appearance.followSystemAccent`/`corners.scale`/`material.acrylicStrength`/`material.micaEnabled`/`motion.mode`（`auto`/`full`/`reduce`）/`motion.categories`/`theme.frontendId`/`theme.visualThemeId`/`layout.*`/`schemaVersion`）+ `presentation-settings.json` 原子写 + schemaVersion 迁移（旧 `ReducedMotion`→`motion.mode` 等价、幂等、旧文件只读顺序、`ThemeSettingsStore` 一个 release 兼容写）。**写者在 Appearance 项目内**（C-03:68）。 |
| P2 | `AppearanceCoordinator`（App 侧）：**只做读取/校验/变更通知**（应用主题与动效的落点在 PREREQ-2 的 `App.axaml.cs`）；`AppOptions` 暴露 `FrontendId`；`Program.cs` 装载 |
| P3 | 令牌生成（**不得手改生成产物**）：`Nm.Focus.Ring.*`/`Nm.Corner.Fluent.*` 走 `TokenMap.DerivedGlobals`（全局派生）；`Nm.Elevation.*` 需新增 `TokenValueKind.BoxShadows`（`TokenMap.cs:4-17` + Writer）；`Nm.Material.*` 归**主题层**（dark/light 取值，主题包 schema，非全局常量）→ 重生成 `NmKeys.g.cs`/`Tokens.Global.axaml` 并跑 `TokenGen -- --check` |
| P4 | 三态动效：`motion.mode` = **`auto`/`full`/`reduce`**（C-03:48 + 设计 02）；`auto` 经 `IMotionPreferenceSource`（平台 SPI，Avalonia 无 API → 提供默认实现 + 可注入）；`motion.categories=off` 时 0ms 反馈；设计 02 判据 ①–⑤ 有测试点 |

## 验收标准

- [ ] **AC1**：`NewManga.Appearance` 项目 + `AppearanceSettings` **C-03 §2.2 逐字段** + 原子读写 + schemaVersion 迁移（旧 `ReducedMotion`→`motion.mode` 等价/幂等/旧文件只读顺序）；`NewManga.Appearance.Tests` 覆盖（往返/坏文件/迁移/兼容写）。<<TODO>>
- [ ] **AC2**：`AppearanceCoordinator` 读取/校验/变更通知（应用落点归 PREREQ-2）；`AppOptions.FrontendId` 可注入；既有 ThemeEngine 回归。<<TODO>>
- [ ] **AC3**：G-1/G-1b/G-1c 令牌经 `TokenMap.DerivedGlobals`（+ `TokenValueKind.BoxShadows`）生成，`NmKeys.g.cs`/`Tokens.Global.axaml` 由生成器产出（`TokenGen -- --check` EXIT 0）。**主题层例外**：`Nm.Material.*` 有 `NmKeys` 常量但**不写入** `Tokens.Global.axaml`（主题包承载取值）；主题包 schema/`ThemeLayerAllowedKeys`（`DesignSystemThemeManager.cs:123-130`）与 `R14ContractTests` 的 59/65 计数同步更新；**G-1b 矩阵列宽 96** 作为设计常量登记（`Nm.Size.MatrixColumnMin`）而非令牌派生。<<TODO>>
- [ ] **AC4**：`motion.mode` = `auto`/`full`/`reduce`（**无 `off`**）；`auto` 经 `IMotionPreferenceSource`（默认实现 + 注入测试）；`motion.categories=off` 0ms；设计 02 判据 ①–⑤ 有测试。<<TODO>>
- [ ] **AC5**：`builtin.fluent-dark` 主题包落盘（`Themes/fluent-dark.nmtheme` + manifest `nm.fluent.visual/1` + 注册表条目）+ 主题包校验通过（`ThemeGen -- --check`）。<<TODO>>
- [ ] **AC6**：全量 sln 不退化（基线 949/0/57）+ 证据。<<TODO>>

## 禁止范围

- 不改四页 UI（FEA-06）；不改 Core/契约；不 push。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | C-03 实现归属 | 独立前置任务（本卡），不并入 FEA-06 | FEA-06-scope-r1 P0-1 |
| W-2 | 项目命名 | `NewManga.Appearance`（C-03 冻结草案指定名） | C-03 |
| W-3 | 令牌缺口归本卡，FEA-06 只消费 | 设计基线 `01` |
| W-4 | G-1 键归属 | `Focus.Ring.*`/`Corner.Fluent.*` → 全局派生；`Elevation.*` → 新增 `BoxShadows` 类型；`Material.*` → 主题层（dark/light） | r1 P0-2 裁决 |
| W-5 | 生成机制 | 禁止手改生成产物；一律走 `TokenMap.DerivedGlobals`/`TokenValueKind` + TokenGen 重生成 + `--check` | r1 P0-2 |
| W-6 | Coordinator 归属 | 写者在 `NewManga.Appearance`；应用主题/动效在 PREREQ-2 | C-03:68；r1 P1-5 |
| W-7 | `motion.mode` 取值 | `auto`/`full`/`reduce`（无 `off`）；`auto` 用 `IMotionPreferenceSource` 默认实现 | C-03:48 + 设计 02；r1 P1-3/4 |
| W-8 | `builtin.fluent-dark` | 本卡交付主题包（ThemeEngine 写域） | C-02 V-07；r1 P1-6 |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | `dotnet test` 四工程（Appearance/DesignSystem/ThemeEngine/App） | .NET | NOT_RUN | 待补 |
| AC3 | `dotnet run --project apps/desktop-avalonia/src/NewManga.DesignSystem.TokenGen -- --check` + `NewManga.ThemeEngine.ThemeGen -- --check` | 生成管线 | NOT_RUN | 待补 |
| AC5 | `ThemeGen -- --check` + 主题包校验 | 生成管线 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）。

## Closeout Record

- 待关闭时填写。
| AC6 | 全量 sln build/test（基线 949/0/57） | 全量 | NOT_RUN | 待补 |
