---
id: FEA-06-PREREQ-2
title: Fluent frontend 激活与 V2 并存边界（组合根 + 双壳入口）
kind: implementation
governance_version: 3
status: in_review
approval: scope_review_r4_approved_2026-11-02
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-06-PREREQ-1
base_commit: a33778608
branch: null
worktree: null
integration_commit: null
delivery_head: 92cac5ab1
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
  - apps/desktop-avalonia/src/NewManga.ThemeEngine/Validation/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/**
  - apps/desktop-avalonia/src/NewManga.Appearance/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/ThemeStudio/ThemeEngineThemeStudioService.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/ThemeStudio/StubThemeStudioService.cs
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
| P7 | **Q-33 residual ③ 承接（R2-P1-2 处置）**：`builtin.fluent-dark` 的 `nm.fluent.visual/1` manifest 条目（写入主题包 `metadata.extra` 或 descriptor 扩展位，按 `ThemePackageJson` 现有 schema 能承载的最小形式）+ `ThemeValidator.Validate` 显式测试 + `BuiltInThemes` 加载/Current 不生效断言；C-02 §4 的校验器义务由本卡承担（W-12：manifest 缺失/手改 → 失败、Fluent 材质键完整性、视觉主题 id 命名空间），写域含 `Validation/**` |
| P6 | **W-9 承接（Q-32）+ C-02 V-07 合规路径（R2-P1-3 处置）**：`Nm.Material.Acrylic.Base/.Tint` 以**主题层令牌**承载——`NmKeys` 加两常量（**不写入** `Tokens.Global.axaml`）、`ThemeLayerAllowedKeys` 放行、主题包 `colors` 承载取值；`Nm.Material.Acrylic.Opacity`/`Mica.Enabled` 保持 PREREQ-1 已交付的全局令牌。**明确不新增 `ThemeMaterial` 枚举值、不改 `ThemeTokenSet` 构造器签名**（C-02 V-07：「不新增枚举值、不改公开方法签名」），因此**不需要契约 UNFREEZE**；`R14ContractTests` 的计数：**59 不变**（Base/Tint 为可选键，不进 Required 59），**65 → 67**（主题层可覆写键面 +2，即 `Nm.Material.Acrylic.Base/.Tint`）。 |

## 验收标准

- [x] **AC1**：`FrontendSelector` 决策表按 **frontendId**（`builtin.current-v2` / `builtin.fluent`）——`builtin.fluent` → Fluent 壳；其余（含缺失/非法）→ V2 + 记录（`builtin.fluent-dark` 是 **visualThemeId**，不参与 selector）。<<MET>>
- [x] **AC2**：组合根按 selector 建壳；V2 启动路径与既有测试不回归。<<MET>>
- [x] **AC3**：Fluent Shell 骨架存在（四页占位 + 导航），可启动（headless 测试）。<<MET>>
- [x] **AC4**：全量 sln 不退化 + 证据。<<MET>>
- [x] **AC5（W-9/Q-32）**：双写者收敛 + `ThemeSettingsStore` 兼容写（一个 release）+ 测试。<<MET>>
- [x] **AC6（W-9/Q-32）**：`Nm.Material.Acrylic.Base/Tint` 主题层键落地 + 主题包 schema/`ThemeLayerAllowedKeys`/`R14ContractTests` 计数同步。<<MET>>
- [x] **AC7（Q-33 residual ③）**：`nm.fluent.visual/1` manifest 落地 + `ThemeValidator.Validate(fluent)` 通过 + `BuiltInThemes` 加载/Current（`newmanga-default`）不生效测试。<<MET>>

## 禁止范围

- 不实现四页内容（FEA-06）；**不改 ThemeEngine 的既有主题包语义**（`newmanga-default` 字节不变；**不新增 `ThemeMaterial` 枚举值、不改 `ThemeTokenSet` 构造器签名**——Material 走主题层令牌，见 P6/W-11）；不改 Core/契约；不 push。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 并存策略 | 双壳并存：`frontendId` 选择；默认 V2（fail-safe）；Fluent 为可选前端 | 设计基线 + r1 P0-2 |
| W-2b | CLI 优先级 | `--frontend`（显式）**优先于** `AppearanceSettings.FrontendId`；两者都缺省 → `builtin.current-v2`（fail-safe V2） | PREREQ-1 `AppOptions.FrontendId`；AC1 |
| W-2 | 写域 | `App.axaml.cs`/`Program.cs`/`Shell/**`/`Views/Fluent/**` 纳入本卡（r1 P2 指出原 FEA-06 写域缺组合根） | r1 P0-2 |
| W-3 | V2 回归 | V2 既有路径不改语义，只加 selector 分支 | AC2 |
| W-10 | D-1 偏差 | C-03 §2.1 的唯一写者是 `NewManga.Appearance` 内的 `AppearanceCoordinator`；PREREQ-1 交付在 App 层（只读）。本卡须迁移到 `NewManga.Appearance` 并使其成为写者 | C-03 §2.1；PREREQ-1 Closeout D-1 |
| W-11 | C-02 V-07 适用口径（DSH 裁决 Q-35） | ThemeEngine 公开面（enum/接口签名）**冻结**；`Nm.Material.Acrylic.Base/.Tint` 用**主题层令牌**承载（`NmKeys` 常量 + `ThemeLayerAllowedKeys` + 主题包 colors），`ThemeMaterial` 枚举与 `ThemeTokenSet` 签名**不变**，故**无需 UNFREEZE**；若后续确需改公开面，须先出 UNFREEZE 记录再改 | C-02 V-07「不新增枚举值、不改接口签名」；scope-r2 R2-P1-3 |
| W-12 | P7 校验器归属与写域补口（DSH 实施期裁决，2026-11-02） | C-02 §4 明定「manifest 缺失或被手改 → 主题包加载失败；校验器覆盖令牌齐全性 + 例外仅限 Fluent + 无裸值」，该义务由本卡 P7 承担：`allowed_paths` 增 `NewManga.ThemeEngine/Validation/**`；`ThemeValidator` 增加 manifest 校验（Fluent 包缺/改 manifest 或非 Fluent 包声明 → error）、Fluent 材质键完整性（Fluent 缺键或非 Fluent 声明 → error），并把视觉主题 id 命名空间放宽到接受冻结的 `builtin.fluent-dark`（`.` 合法）。**只改校验规则，不改 `ThemeKind` 枚举与任何公开方法签名**（V-07 不触碰，无需 UNFREEZE）。scope-r3 的 R3-P2-2 把「不改 validator、只加测试」列为最小路径并注明「完整校验器义务归属由 DSH 注记」——本行即该注记的落点；实施期实测现有 `Validate(fluent-dark)` 因 id 含 `.` 必失败，不补此口则 AC7 不可能通过 | C-02 §4 校验器判据；scope-r3 R3-P2-2；实施期实测 |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC3 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests`（`FrontendSelectorTests` + `FluentShellTests` + V2 回归） | Avalonia.Headless | **PASS**（13 + 5 + V2 25，0 failed） | `verification/FEA-06-PREREQ-2/ac1-selector-tests.log`、`ac2-ac3-shell-tests.log` |
| AC5 | `dotnet test apps/desktop-avalonia/tests/NewManga.Appearance.Tests` + `NewManga.App.Tests`（sink）+ `NewManga.ThemeEngine.Tests`（兼容写） | .NET 9 / Avalonia.Headless | **PASS**（21 + 4 + 24） | `ac5-appearance-tests.log`、`ac5-sink-tests.log`、`ac5-compat-write-tests.log` |
| AC6 | `dotnet test apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests` + `NewManga.ThemeEngine.Tests` + `TokenGen -- --check` + `ThemeGen -- --check` | .NET 9 + 生成管线 | **PASS**（11 + 51；两 `--check` up to date） | `ac6-r14-tests.log`、`ac6-material-tests.log`、`tokengen-check.log`、`themegen-check.log` |
| AC7 | `dotnet test apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests`（`ThemeValidator`/`BuiltInThemes`） | .NET 9 | **PASS**（60） | `ac7-manifest-tests.log` |
| AC4 | 全量 sln build/test | 全量 | **PASS**（build 0 warnings/0 errors；**1022/0/57**） | `build.log`、`test.log` |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-P2-SELECTOR | AC1 | `apps/desktop-avalonia/src/NewManga.App/Services/FrontendSelector.cs` | `92cac5ab1` | `6234f5861cc238489cf0307ca01a0050bf17c14454f1bd0000071392c0241f57` | CANONICAL |
| E-P2-SELECTOR-TESTS | AC1 | `verification/FEA-06-PREREQ-2/ac1-selector-tests.log` | `92cac5ab1` | `cc8141e3b205d8d8d75af33f02b3d83ef931bf4c6404dbd62ad2f219f73dae1a` | CANONICAL |
| E-P2-COMPOSITION | AC2 | `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs` | `92cac5ab1` | `582fec7ff55fb991583b1cc1c62900d52dd16598e2994bc6ee0a66a75de1028b` | CANONICAL |
| E-P2-FLUENT-SHELL | AC2/AC3 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShell.axaml.cs` | `92cac5ab1` | `d8665fb48daf11abe0ae7d6aa13a098763567d35ad31973bbc57930e9690a7c8` | CANONICAL |
| E-P2-SHELL-TESTS | AC2/AC3 | `verification/FEA-06-PREREQ-2/ac2-ac3-shell-tests.log` | `92cac5ab1` | `2c3d58e4e199113bf199dae68c69ad00f1eedc1c863b12cee58ec34d41784eac` | CANONICAL |
| E-P2-COORDINATOR | AC5 | `apps/desktop-avalonia/src/NewManga.Appearance/AppearanceCoordinator.cs` | `92cac5ab1` | `09232db8e315370d02122868f9c7bf27fb7c7ddec06483d9b61d79d79da344ea` | CANONICAL |
| E-P2-SINK-CONTRACT | AC5 | `apps/desktop-avalonia/src/NewManga.ThemeEngine/Service/IThemeSettingsSink.cs` | `92cac5ab1` | `170bc3f30d77ee6b2e1ea549317e93611b492cb7cd608af445d573f91d3cd637` | CANONICAL |
| E-P2-COMPAT-WRITE | AC5 | `apps/desktop-avalonia/src/NewManga.ThemeEngine/Persistence/ThemeSettingsStore.cs` | `92cac5ab1` | `c9c4d05beb17cca21588712e60c4044eb837327121e90eb50fe1038700f48ae2` | CANONICAL |
| E-P2-SINK-ADAPTER | AC5 | `apps/desktop-avalonia/src/NewManga.App/Services/AppearanceThemeSettingsSink.cs` | `92cac5ab1` | `f96092e26503d0b7c96532c3914fe16becaefd01d622bce2cbf8664f50115158` | CANONICAL |
| E-P2-APPEARANCE-TESTS | AC5 | `verification/FEA-06-PREREQ-2/ac5-appearance-tests.log` | `92cac5ab1` | `9640258b6bc62ad684b3aec81453f6131b9dfb299104d1898f796adb8b62f759` | CANONICAL |
| E-P2-SINK-TESTS | AC5 | `verification/FEA-06-PREREQ-2/ac5-sink-tests.log` | `92cac5ab1` | `9476b0da4a7da644a932c467a14719772c5da5685c5dc37d134824f637f4712d` | CANONICAL |
| E-P2-COMPAT-TESTS | AC5 | `verification/FEA-06-PREREQ-2/ac5-compat-write-tests.log` | `92cac5ab1` | `53d3ffed096ea40760a4dacb6eadd619bc078801b7429faf0e8b409b398d4eb0` | CANONICAL |
| E-P2-TOKEN-MAP | AC6 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Tokens/TokenMap.cs` | `92cac5ab1` | `4a5b37fce512de571f7ecc050a887f15bf51736c8a252c7f7d933afe9aa11180` | CANONICAL |
| E-P2-THEME-LAYER | AC6 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs` | `92cac5ab1` | `3472fa13368d9c4c00defcc6f04eef8b249b5fb22f1a053963d01b483239d157` | CANONICAL |
| E-P2-FLUENT-PACKAGE | AC6/AC7 | `apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/fluent-dark.nmtheme` | `92cac5ab1` | `0d2d223a3c653bf6ce032679d6c2d0e3d395966d9b06722fe10d0c143d938602` | CANONICAL |
| E-P2-GENERATOR | AC6/AC7 | `apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/BuiltInThemeGenerator.cs` | `92cac5ab1` | `28b3a577d51ab6bbbf12144012a2e44c83c9df7aac99a8d0f4b170ee0ec91ca3` | CANONICAL |
| E-P2-VALIDATOR | AC7 | `apps/desktop-avalonia/src/NewManga.ThemeEngine/Validation/ThemeValidator.cs` | `92cac5ab1` | `3bbf8f6157dfa42dc63caf2e4cc498808800b8381200782f56772dad035401a9` | CANONICAL |
| E-P2-R14-TESTS | AC6 | `verification/FEA-06-PREREQ-2/ac6-r14-tests.log` | `92cac5ab1` | `308d9e50197a91e593fa5fd23f39ca2e9dd639ae05be7eb3cf68cc7ae542d4f5` | CANONICAL |
| E-P2-MATERIAL-TESTS | AC6 | `verification/FEA-06-PREREQ-2/ac6-material-tests.log` | `92cac5ab1` | `8417e073cac264e497cc92291d2569d08804992ea147814c5ebca511e7056ab8` | CANONICAL |
| E-P2-MANIFEST-TESTS | AC7 | `verification/FEA-06-PREREQ-2/ac7-manifest-tests.log` | `92cac5ab1` | `8d87afed2931e281f76cedbdbe9ffc63ff99cd71c1beb614fd9c36af31734702` | CANONICAL |
| E-P2-TOKENGEN | AC6 | `verification/FEA-06-PREREQ-2/tokengen-check.log` | `92cac5ab1` | `a81c35f854f379465c8494e19e61e93ff809e868ae57a1f1204f0f983234bba2` | CANONICAL |
| E-P2-THEMEGEN | AC6/AC7 | `verification/FEA-06-PREREQ-2/themegen-check.log` | `92cac5ab1` | `d9c4cf9b070a0b847b759fad7d1f497fd734cb4e0cbdce076e71f211242a65f0` | CANONICAL |
| E-P2-BUILD | AC4 | `verification/FEA-06-PREREQ-2/build.log` | `92cac5ab1` | `dafdb95132eb7c9f593da253522fbe2ecf00015bef04ef219cd51095a9a1d73c` | CANONICAL |
| E-P2-TEST | AC4 | `verification/FEA-06-PREREQ-2/test.log` | `92cac5ab1` | `1325f8408d401440cbd33ec6dfb2a4c6fa2c4eecb2794605c86897a6000f2dcf` | CANONICAL |
| E-P2-CHECK | Gate | `verification/FEA-06-PREREQ-2/governance-check.log` | `92cac5ab1` | `9fd5ad40131a58dab5c8409df053f967e6efd30dff8da7f65e21cf93d5a5edc4` | CANONICAL |
| E-P2-PINS | Gate | `verification/FEA-06-PREREQ-2/verify-pins.log` | `92cac5ab1` | `cf0df19a460c144428b4f973b0f1de8b36e0e106d73c0593e15b4e95f84d3615` | CANONICAL |
| E-P2-DELIVERY-NOTES | All | `verification/FEA-06-PREREQ-2/delivery-notes.md` | `92cac5ab1` | `5043754da6159495c65cb0b5501e984c1753c620bddc3efeb2070dc89f6ec0f9` | CANONICAL |
| E-P2-FLUENT-SMOKE | AC2/AC3 | `verification/FEA-06-PREREQ-2/ac2-ac3-fluent-smoke.log` | `PENDING` | `d679b34e04a0ba1a295bcf37eadb73c0b37d45d1335753c53c66928f9ef77a51` | CANONICAL |
| E-P2-V2-SMOKE | AC2 | `verification/FEA-06-PREREQ-2/ac2-v2-smoke.log` | `PENDING` | `11cb9ee6bb72b01648c23fa318eb336371d79fae2d98c68d6432eaf357e7f536` | CANONICAL |
| E-P2-LEDGER-SOURCE | Gate | `verification/FEA-06-PREREQ-2/task-ledger.log` | `92cac5ab1` | `5faa94d01a8863486b362457850d8525eac69da23d9929469635f7b551d0456d` | SOURCE_PIN |

## Resource Manifest

- worktree：无（main 直接实现）。
- 过程文件（非独立证据，登记为 SOURCE_PIN）：`verification/FEA-06-PREREQ-2/task-ledger.log`（台账重算输出，`doc/TASK_LEDGER.md` 由 `task_ledger.py --write` 生成；已列入 Canonical Evidence 的 SOURCE_PIN 行）。

## Closeout Record

- **实施完成（2026-11-02）**：P1–P7 / AC1–AC7 全部实现并自测（全量 **1022/0/57**；两 `--check` up to date；`check.ps1` PASS 3 warnings；`verify_pins` 15/15）。
- **偏差**：D-1 已关闭（coordinator 迁入 `NewManga.Appearance`）；W-12（P7 校验器归属 + `Validation/**` 写域补口）已入附加裁决点；详见 `verification/FEA-06-PREREQ-2/delivery-notes.md`。
- **待办**：实现复核（独立上下文）；approve 后填 canonical_evidence_status / resource_closeout_status、integration_commit 与本段最终结论。
- 待关闭时填写。
