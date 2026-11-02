---
id: FEA-06-PREREQ-1
title: 外观持久化与 Fluent 令牌生成（C-03 落地 + G-1/G-1b/G-1c）
kind: implementation
governance_version: 3
status: in_review
approval: scope_review_r3_approved_2026-11-02; impl_review_r4_approved_2026-11-03（AC1/AC3/AC5 PARTIAL 保持 in_review）
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-04b
base_commit: cad5ebde3
branch: null
worktree: null
integration_commit: 06b7a1b10
delivery_head: 06b7a1b10
canonical_evidence_status: partial（AC1/AC3/AC5 待 PREREQ-2 闭环）
resource_closeout_status: partial（同 AC 状态）
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
  - apps/desktop-avalonia/src/NewManga.App/Services/MotionResolver.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/WindowsMotionPreferenceSource.cs
  - apps/desktop-avalonia/src/NewManga.App/AppOptions.cs
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
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
| P5b | `builtin.fluent-dark` 视觉主题包：`Themes/fluent-dark.nmtheme` + manifest `nm.fluent.visual/1` + C-02 V-07 注册表 + 主题包校验（`ThemeValidator`/`BuiltInThemes` 加载 + Current 不生效测试） |

## 验收标准

- [ ] **AC1**：`NewManga.Appearance` 项目 + `AppearanceSettings` **C-03 §2.2 逐字段** + 原子读写 + schemaVersion 迁移（旧 `ReducedMotion`→`motion.mode` 等价/幂等/旧文件只读顺序）；`NewManga.Appearance.Tests` 覆盖（往返/坏文件/迁移/兼容写）。<<PARTIAL: 读写与迁移已交付（13 测试）；`ThemeSettingsStore` 兼容写按 W-9 转 PREREQ-2（Q-32），本卡未闭环>>
- [x] **AC2**：`AppearanceCoordinator` 读取/校验/变更通知（应用落点归 PREREQ-2）；`AppOptions.FrontendId` 可注入；既有 ThemeEngine 回归。<<MET>>
- [ ] **AC3**：G-1/G-1b/G-1c 令牌经 `TokenMap.DerivedGlobals`（+ `TokenValueKind.BoxShadows`）生成，`NmKeys.g.cs`/`Tokens.Global.axaml` 由生成器产出（`TokenGen -- --check` EXIT 0）。**主题层例外**：`Nm.Material.*` 有 `NmKeys` 常量但**不写入** `Tokens.Global.axaml`（主题包承载取值）；主题包 schema/`ThemeLayerAllowedKeys`（`DesignSystemThemeManager.cs:123-130`）与 `R14ContractTests` 的 59/65 计数同步更新；**G-1b 矩阵列宽 96** 作为设计常量登记（`Nm.Size.MatrixColumnMin`）而非令牌派生。<<PARTIAL: Focus/Corner/Elevation/Material 开关共 12 键已生成（--check up to date）；`Nm.Material.Acrylic.Base/Tint` 与主题层 schema/R14 计数按 W-9 转 PREREQ-2（Q-32）>>
- [x] **AC4**：`motion.mode` = `auto`/`full`/`reduce`（**无 `off`**）；`auto` 经 `IMotionPreferenceSource`（默认实现 + 注入测试）；`motion.categories=off` 0ms；设计 02 判据 ①–⑤ 有测试。<<MET>>
- [ ] **AC5**：`builtin.fluent-dark` 主题包落盘（`Themes/fluent-dark.nmtheme` + manifest `nm.fluent.visual/1` + 注册表条目）；**两项校验**：`ThemeGen -- --check`（产物漂移）+ `ThemeValidator.Validate`/`BuiltInThemes` 加载（schema 合法）+ Current 主题不生效测试。<<PARTIAL: 包由 ThemeGen 生成（`--check` 覆盖）+ `BuiltInThemes` 懒加载 + Current 不变测试；`nm.fluent.visual/1` manifest 与 `ThemeValidator` 显式测试未加（P2-17）>>
- [x] **AC6**：全量 sln 不退化（基线 949/0/57）+ 证据。<<MET>>

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
| W-9 | r2-P1-2（ThemeSettingsStore 兼容写）/ r2-P1-4（Material Base/Tint 主题层）归属 | **转入 FEA-06-PREREQ-2**，本卡作为 P2 接受：前者写者收敛会形成 `ThemeEngine ↔ Appearance` 循环引用（`AppearanceStore.Read` 已覆盖读路径迁移）；后者需扩主题包 schema/R14 计数，与本卡「不扩 schema」边界冲突 | Q-32（2026-11-03，DSH 裁决）；impl-r2 报告 |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | `dotnet test` 四工程（Appearance/DesignSystem/ThemeEngine/App） | .NET | NOT_RUN | 待补 |
| AC3 | `TokenGen -- --check` + `ThemeGen -- --check` | 生成管线 | **PASS**（均 up to date，rows 290） | `verification/FEA-06-PREREQ-1/tokengen-check.log` |
| AC5 | `ThemeGen -- --check` + 主题包校验 | 生成管线 | **PASS**（fluent 纳入 --check） | `verification/FEA-06-PREREQ-1/themegen-check.log` |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-P1-APPEARANCE | AC1 | `apps/desktop-avalonia/src/NewManga.Appearance/AppearanceJson.cs` | `a57e6a811` | `f94ec74f2d523ecf4abe68c408a88ba91d97cbe1a2120df7037c6900bb2a7a0f` | CANONICAL |
| E-P1-APPEARANCE-TESTS | AC1 | `verification/FEA-06-PREREQ-1/appearance-tests.log` | `a57e6a811` | `b191462943321b1ddc324843c3a0d7d456ec00790597e693a359c3ef472cec97` | CANONICAL |
| E-P1-COORDINATOR | AC2 | `apps/desktop-avalonia/src/NewManga.App/Services/AppearanceCoordinator.cs` | `a57e6a811` | `6f5b2487393299c4b7cc30fd2290bfada42048fd91aa8aa8a0928f88ad3553f7` | CANONICAL |
| E-P1-TOKENS | AC3 | `verification/FEA-06-PREREQ-1/tokengen-check.log` | `a57e6a811` | `b76bf6c6a12c22828662a19da43764bd449cd5f80d20111fa97026ef4058d4bb` | CANONICAL |
| E-P1-MOTION | AC4 | `verification/FEA-06-PREREQ-1/motion-tests.log` | `a57e6a811` | `34cf6c28b95c42762b0935eaaf5150698aaf5b8b1e50167d01173d02fc926616` | CANONICAL |
| E-P1-THEME | AC5 | `verification/FEA-06-PREREQ-1/themegen-check.log` | `a57e6a811` | `28a3115171bd2d6e6227a439ce22d3fb855104c741681efef8b41cec0a584f49` | CANONICAL |
| E-P1-SLN | AC6 | `verification/FEA-06-PREREQ-1/sln-test.log` | `a57e6a811` | `b8753cd8d8506337794fa5926f9bc2b683f1cd0b8b530e83943e42ccfd44876a` | CANONICAL |
| E-P1-BUILD | AC6 | `verification/FEA-06-PREREQ-1/build.log` | `a57e6a811` | `ca5cb82c5c06631c132cf49e23aea8c026e73fbf342b46e75eb28b5a2ac077b5` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）。

## Closeout Record

- 待关闭时填写。
| AC6 | 全量 sln build/test | 全量 | **PASS**（**978/0/57**） | `verification/FEA-06-PREREQ-1/sln-test.log` |
- 2026-11-02：范围复核 r1（P0×2/P1×8）→ r2（P0=0/P1×4）→ **r3 approved（P0/P1=0，P2×16）**；置 
eady，DSH 实现。
- 2026-11-03 / DSH：FEA-06-PREREQ-1 实现完成并收口（ 6b7a1b10）——范围 r1–r3（r3 approved）、实现 impl-r1（P1×10 全关闭）→ impl-r2（P1×5：3 关闭 + W-9 裁决 P1-2/P1-4 转 PREREQ-2）；全量 sln **977/0/57**；TokenGen/ThemeGen --check up to date；置 in_review 待 impl-r3。
