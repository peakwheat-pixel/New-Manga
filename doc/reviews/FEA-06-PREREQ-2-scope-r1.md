---
task_id: FEA-06-PREREQ-2
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: cad5ebde3
reviewed_head: a81771bdd
decision: changes_requested
counts: { P0: 3, P1: 7, P2: 9 }
---

# FEA-06-PREREQ-2 范围冻结复核 r1（独立上下文；本席位未参与本卡起草）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-2.md`（`proposed`；`approval: pending_review`） |
| base_commit | `cad5ebde3`（卡声明；`git merge-base --is-ancestor` 通过） |
| reviewed_head | `a81771bdd`（`docs(fea-06-prereq-1/prereq-2): … Q-32 正式裁决（W-9 转 PREREQ-2 并承接：任务 P5/P6 + AC5/AC6 + 写域）…`） |
| 上游 | `doc/tasks/FEA-06-PREREQ-1.md`（`in_review`；AC1/AC3/AC5 PARTIAL）、`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` §22（Q-32 正式裁决 `:168-173`） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；未参与 FEA-06-PREREQ-2 起草；此前只读评审 FEA-06/FEA-05/PREREQ-1 范围与实现系列；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-03 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 3 / P1 = 7 / P2 = 9（共 19）** |

> **一句话结论**：**changes_requested**。Q-32 裁决与 W-9 承接方向正确（P5/P6、AC5/AC6、`allowed_paths` 已加 `ThemeEngine/Persistence/**`/`DesignSystem/**`/`Appearance/**`），但**当前仍不可执行**：①**P5/P6 写域与测试落点不足**——`allowed_paths` 缺 `NewManga.App/Services/**`（`AppearanceCoordinator` 所在）、`NewManga.ThemeEngine/Models|Serialization|Themes/**`（`ThemeTokenSet`/`ThemeMaterial`/主题包 schema/`fluent-dark.nmtheme`）与 `tests/NewManga.ThemeEngine.Tests|NewManga.DesignSystem.Tests|NewManga.Appearance.Tests/**`；②**依赖环**——`PREREQ-2` `depends_on: FEA-06-PREREQ-1`（`in_review`），而 PREREQ-1 的 AC1/AC3/AC5 已转由 PREREQ-2 闭环，PREREQ-1 不 done → PREREQ-2 不 release，PREREQ-2 不完成 → PREREQ-1 不 done；③AC1 决策表把 `builtin.fluent-dark`（visualThemeId）当 frontendId；AC5/AC6 无测试命令；P5/P6 未落到方法/字段/测试；`禁止范围` 还写「不改 ThemeEngine 语义」，与 P5/P6 直接冲突。需补写域、拆依赖环、明确 selector/API/测试后再 rev-r2。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改卡/代码/设计；`git status --porcelain` 为空；未 commit/push；本报告为本轮唯一新增文件。
- 本轮实测：`check.ps1` → **PASS（4 warnings：11 非终态、STATUS/PLAN 80%、PREREQ-1 `evidence_dir` 3 个未登记过程文件）**；`verify_pins.ps1` → **PASS（all 15）**；`git merge-base --is-ancestor cad5ebde3 HEAD` → 0。
- 阅读：本卡全文；PREREQ-1 卡（`in_review`/AC PARTIAL/证据表）；goal §22 Q-32；设计 `04-layout-responsive.md`、`02-motion.md`；`App.axaml.cs`/`Program.cs`/`Shell/**`/`App.Tests`；`ThemeSettingsStore`/`IThemePersistence`/`ThemeService`；`ThemeModels`/`ThemePackageJson`/`BuiltInThemes`/`Themes/**`；`DesignSystemThemeManager`/`R14ContractTests`；`Appearance`/`AppearanceCoordinator`；STATUS/PLAN/LEDGER。

---

## 1. 六项必核查逐项

### 1.1 W-9 承接完整性（P5/P6 可执行性/write domain）

- **P5/P6 已入卡**：任务 `:54-55`、AC5/AC6 `:63-64`，方向正确 ✓。
- **写域不足**：`allowed_paths`（`:21-37`）含 `NewManga.ThemeEngine/Persistence/**`、`NewManga.DesignSystem/**`、`NewManga.Appearance/**`，但：
  - P5 的 `AppearanceCoordinator` 实际在 `apps/desktop-avalonia/src/NewManga.App/Services/AppearanceCoordinator.cs`（只读/通知），P5 要其成为唯一写者 → 缺 `NewManga.App/Services/**`（或等价明确路径）；
  - P5 要 `ThemeSettingsStore` 标 deprecated + 一个 release 兼容写 → `Persistence/**` 可覆盖类本身，但若需 `IThemePersistence`（`Models/ThemeContracts.cs:93-103`）/`ThemeService`（`Service/ThemeService.cs:651`）适配，缺 `Models/**`/`Service/**`；
  - P6 的 Material 主题层键需 `ThemeTokenSet`/`ThemeMaterial`（`Models/ThemeModels.cs:93-107,240-245`）、主题包 schema（`Serialization/ThemePackageJson.cs:141-142,291`）、`Themes/fluent-dark.nmtheme`/`BuiltInThemeGenerator`（`Themes/**`）——均不在 `allowed_paths`；
  - **测试落点缺失**：仅 `tests/NewManga.App.Tests/**`（`:32`），缺 `tests/NewManga.ThemeEngine.Tests/**`、`tests/NewManga.DesignSystem.Tests/**`、`tests/NewManga.Appearance.Tests/**`；AC5/AC6 无法落测试。
- **P5/P6 内容不具体**：P5 未给 `AppearanceCoordinator` 的方法签名/字段/唯一写者路径；P6 未给 `Nm.Material.Acrylic.Base/Tint` 的承载模型（`ThemeTokenSet` 新字段 vs `NmKeys` + 包字段）、主题包 schema 字段、`R14ContractTests` 59/65 改动清单。
- 结论：**P0-1/P0-2**（见下）。

### 1.2 双壳 selector 设计

- `App.axaml.cs:96` 仍无条件 `AppShellV2.CreateRoot`；`Program.cs:11-22` 无 selector 分支；本卡 P1/P2 `:50-51` 计划补 ✓。
- **AC1 决策表错误（P1-1）**：`:59` 写 `builtin.fluent`/`builtin.fluent-dark` → Fluent；但 C-02 V-07（`FEA-C02...:89-90,110`）定义 **frontendId** = `builtin.current-v2`/`builtin.fluent`，**visualThemeId** = `newmanga-default`/`builtin.fluent-dark`；`builtin.fluent-dark` 不是 frontendId。`AppearanceSettings.FrontendId`/`VisualThemeId`（`AppearanceSettings.cs:16-19,116-118`）已分离，将 `builtin.fluent-dark` 作为 selector 值会误选。
- **CLI 优先 vs 持久化优先未定义（P1-2）**：PREREQ-1 已建 `AppOptions.FrontendId`（`AppOptions.cs:36`，`--frontend` case `:228`）；本卡 P1 只写「读 `AppearanceSettings.FrontendId`」，未规定 `--frontend` 覆盖优先级、非法值回退与「其余 → V2」的先后，AC1 无对应断言。
- **非法值记录 sink 未定义（P2-1）**：AC1 要求「非法值 → V2 + 记录」，未指定记录面（诊断/日志/Shell 状态）。
- **V2 回归**：AC2 `:60` 只有「组合根按 selector 建壳；V2 路径与既有测试不回归」，未列具体测试/断言；P2-2。
- **Fluent Shell 骨架**：`Views/Fluent/**` 允许 ✓；设计 04 `:9-22` 定义四页共用骨架（顶部命令条+左导航+状态条），卡 P3 `:52` 只写「导航 + 四页占位」，AC3 `:61` 只写「可启动（headless）」；`App.Tests` 有 `Avalonia.Headless.XUnit`（`AssemblyInfo.cs:1`）✓，但未给具体 headless 用例/断言；P2-3。

### 1.3 P2 循环依赖

- P5（`:54`）称由 App 侧 sink 适配避免 `ThemeEngine↔Appearance` 循环；但 `NewManga.Appearance.csproj` 仍有未使用的 `NewManga.ThemeEngine` 引用（`NewManga.Appearance.csproj:11`），`AppearanceCoordinator`（App 侧）当前只读，真正写者是 `AppearanceStore.WriteAsync`（`Appearance/AppearanceStore.cs:62`）；C-03 `:68` 规定写者为 `NewManga.Appearance` 的 `AppearanceCoordinator`。
- 卡未写清：唯一写者用哪个类/放哪个项目；`IThemePersistence` sink adapter 放 App 还是 Appearance；`--theme-home`/`presentation-settings.json` 路径与旧 store 如何共存；`ThemeSettingsStore` deprecated 的 public surface 变化。
- 结论：P1-3（P5 可执行路径不清）；若按当前 P5 字面实现，确实可能引入循环/重复写者（`Appearance→ThemeEngine` 未移除 + ThemeEngine 反接 Appearance）；P2-4。

### 1.4 Material 主题层

- P6（`:55`）要求 `Nm.Material.Acrylic.Base/Tint` 主题层 + 主题包 schema 演进 + `ThemeLayerAllowedKeys` + `R14ContractTests` 59/65；但未选实现路径：
  - **`ThemeTokenSet` 扩展**：`ThemeMaterial` 当前枚举仅 `Solid/None`（`ThemeModels.cs:93-99`），要承载 `IBrush` Base/Tint/Opacity 需改 `Models/**`（不在写域）且可能触碰 V11R §4 公开面；
  - **`NmKeys` 常量 + 主题包字段**：`NmKeys`/`Generated` 在 `DesignSystem/**` ✓，但主题包字段在 `Serialization/**`、包值在 `Themes/**`（均不在写域）；
  - `ThemeLayerAllowedKeys`（`DesignSystemThemeManager.cs:114-130`）由 `PaletteColorKeys + Font + Corner + Motion` 组成；加 Material 键会改动 `ThemeLayerRequiredKeys`/`AllowedKeys` 的 59/65 计数，且 `R14ContractTests.cs:85-93` 将连带断言 Palette=35、Font=3、Corner=3、Required=59、Allowed=65（可能还需改其他计数）；卡未列改动面。
- 结论：P0-2（写域） + P1-4（实现路径未定） + P1-6（公开面/契约分析缺失）。

### 1.5 AC 可验收性

| AC | 现状判定 | 问题 |
|---|---|---|
| AC1 `:59` | **P1** | frontendId/visualThemeId 混用；非法值记录 sink、CLI 优先级未定 |
| AC2 `:60` | **P2** | 组合根改造/回归无具体测试断言 |
| AC3 `:61` | **P2** | Fluent Shell 骨架 + headless 可测，但无具体用例/设计 04 骨架对照 |
| AC4 `:62` | **可验收** | 全量 sln |
| AC5 `:63` | **P1** | 写域/测试落点不足；P5 无方法/字段；测试表 `:82-83` 无 AC5 命令 |
| AC6 `:64` | **P1** | 写域/测试落点不足；P6 无 schema/API/测试清单；测试表无 AC6 命令 |

- **测试要求表 `:82-83` 只有 AC1–AC3（App.Tests）+ AC4（全量 sln）**，AC5/AC6 完全无命令/证据；AC5/AC6 是 Q-32 强制任务，不能被遗漏（P1-5）。

### 1.6 治理

- `check.ps1` **PASS（4 warnings：11 非终态、STATUS/PLAN 80%、PREREQ-1 `evidence_dir` 未登记过程文件）**；`verify_pins` **15/15** ✓；4 warnings 均非阻塞（P2-5）。
- **STATUS 指针（P2-6）**：`STATUS:7` 当前 Task 仍是 `FEA-06-PREREQ-1 in_review`，`:10` 下一候选仍是 `FEA-06-PREREQ-1`（r3 复核）→ 未指向 PREREQ-2。
- **PLAN 指针（P2-6）**：`:22` PREREQ-2 `proposed` ✓；但 `:21` PREREQ-1 `in_review` 与 `:37` 当前 DAG 行仍写 `FEA-06-PREREQ-1（**proposed**）` → 不一致。
- **LEDGER**：`:43` PREREQ-1 in_review、`:47` PREREQ-2 proposed ✓。
- **依赖环（P0-3）**：本卡 `:11-12` `depends_on: FEA-06-PREREQ-1`；PREREQ-1 仍 `in_review` 且 AC1/AC3/AC5 已转由本卡闭环（goal `:170-172`）→ PREREQ-2 无法在 PREREQ-1 done 前 release，PREREQ-1 也无法在本卡完成前 done；需 DSH 拆环。

---

## 2. 结论与 findings

### P0（3 条，阻塞范围冻结）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P0-1** | 卡 `:21-37`、`:54`、`:63`；`AppearanceCoordinator.cs`；`tests/NewManga.Appearance.Tests/**`/`ThemeEngine.Tests/**` | **P5 写域/测试落点不足**：`AppearanceCoordinator` 在 `NewManga.App/Services/`（不在 allowed）；P5 要其为唯一写者、且 `ThemeSettingsStore` deprecated/compat 写需 `ThemeEngine/Persistence`（已含）但缺 `App/Services/**` 与两张测试工程；P5 无方法/字段/测试定义。 | 补 `NewManga.App/Services/**`（或明确把 writer 放 `NewManga.Appearance/**` 并说明 App 侧只接线）、`tests/NewManga.ThemeEngine.Tests/**`、`tests/NewManga.Appearance.Tests/**`；P5 写清 `AppearanceCoordinator.Save/Reload` 方法、唯一写者、sink adapter 接口、compat 写/双写测试。 |
| **P0-2** | 卡 `:21-37`、`:55`、`:64`；`ThemeModels.cs:93-107,240-245`；`ThemePackageJson.cs:141-142,291`；`Themes/fluent-dark.nmtheme`；`R14ContractTests.cs:85-93` | **P6 写域/测试落点不足**：Material Base/Tint 需 `ThemeEngine/Models/**`（`ThemeTokenSet`/`ThemeMaterial`）、`Serialization/**`（包 schema）、`Themes/**`（`fluent-dark.nmtheme`/生成器），均不在 allowed；`R14ContractTests` 在 `tests/NewManga.DesignSystem.Tests/**` 也不在 allowed。AC6 无法实现/验证。 | 补 `NewManga.ThemeEngine/Models/**`、`Serialization/**`、`Themes/**`、`tests/NewManga.DesignSystem.Tests/**`、`tests/NewManga.ThemeEngine.Tests/**`；在 P6 明确 schema 字段/`ThemeTokenSet` 模型、包值来源、`ThemeLayerAllowedKeys` 与 R14 59/65 的完整改动面。 |
| **P0-3** | 卡 `:11-12`；PREREQ-1 `in_review`/AC1/AC3/AC5 PARTIAL；goal §22 `:170-172` | **依赖环/发布顺序不可满足**：本卡 `depends_on: FEA-06-PREREQ-1`（in_review）；PREREQ-1 的 AC1/AC3/AC5 已按 Q-32 转本卡闭环 → PREREQ-2 无法在 PREREQ-1 done 前 release，PREREQ-1 无法在本卡完成前 done。 | DSH 拆环：①先以「Q-32 正式裁决 + PREREQ-1 接受 residual」方式置 PREREQ-1 done（或 done-with-residual），再释放本卡；或②去掉本卡对 PREREQ-1 的 `depends_on` 并改由 Q-32 记录交付顺序；③在本卡 AC 表中标明移植自 PREREQ-1 的 AC 与来源。 |

### P1（7 条，必须修）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P1-1** | 卡 `:59`（AC1）；C-02 V-07 `:89-90,110`；`AppearanceSettings.cs:16-19` | **AC1 决策表 ID 混用**：`builtin.fluent-dark` 是 visualThemeId，不是 frontendId；frontendId 只有 `builtin.current-v2`/`builtin.fluent`。 | AC1 改为按 `FrontendId` 决策：`builtin.fluent` → Fluent；`builtin.current-v2`/缺省/未知 → V2；visualThemeId 仅作主题选择输入，不参与 frontend 决策；补非法值/失败回退断言。 |
| **P1-2** | 卡 `:50`（P1）、`:59`（AC1）；`AppOptions.cs:36`（`--frontend`） | **CLI 与持久化优先级未定义**：`--frontend`（PREREQ-1 已建）vs `AppearanceSettings.FrontendId`；AC1 未写谁优先、非法 CLI 是否回退、是否覆盖持久化。 | 明确「CLI 非 null 优先；非法 CLI → fail-safe V2 + 记录；否则读持久化」并补测试。 |
| **P1-3** | 卡 `:54`（P5）；`AppearanceCoordinator.cs`；`AppearanceStore.cs`；C-03 `:68`；`IThemePersistence`（`ThemeContracts.cs:93-103`） | **P5 唯一写者/sink 路径不清**：`AppearanceCoordinator` App 侧只读，写者是 `AppearanceStore`；P5 要 coordinator 唯一写者但未指定类/项目/方法；sink adapter 接口/位置未定。 | 明确唯一写者类（C-03 要求 `NewManga.Appearance` 的 `AppearanceCoordinator`）、Store 与 Coordinator 职责、App 侧 sink 适配接口/位置；补写入/兼容期/双写收敛测试。 |
| **P1-4** | 卡 `:55`（P6）；`ThemeModels.cs:93-107,240-245`；`ThemePackageJson.cs:141-142,291`；`ThemeLayerAllowedKeys`（`DesignSystemThemeManager.cs:114-130`） | **Material 主题层实现路径未选**：`ThemeTokenSet` 扩展（需 Models）vs `NmKeys` 常量 + 主题包字段（需 Serialization/Themes）；未给 `Nm.Material.Acrylic.Base/Tint` 的字段、包 schema、Current 不生效断言。 | 在 P6 选定一条路径并写清模型/schema/包字段/`NmKeys` 常量/校验测试；同步列 `R14ContractTests` 59/65 及 Palette/Font/Corner 计数的改动面。 |
| **P1-5** | 卡 `:82-83`（测试要求）；AC5/AC6 `:63-64` | **AC5/AC6 无测试命令/测试工程**：测试表只有 AC1–AC3+AC4；AC5（双写/兼容）与 AC6（Material/schema/R14）无 `dotnet test` 目标/证据。 | 测试表增 AC5（ThemeEngine.Tests/Appearance.Tests）与 AC6（DesignSystem.Tests/ThemeEngine.Tests）命令与具体断言；写入 `verification/FEA-06-PREREQ-2/**`。 |
| **P1-6** | 卡 `:55`（P6）；`ThemeModels.cs`/`ThemePackageJson.cs`；C-02 V-07 `:90`；V11R §4 | **P6 未做公开面/契约分析**：`ThemeMaterial`/`ThemeTokenSet` 为 ThemeEngine 公开模型，扩 Material 值/字段可能改变公开签名/枚举，与 C-02 V-07「ThemeKind 枚举与公开方法签名不得变化」需核对；卡未引用/论证。 | 在 P6 明确 schema 演进是否触碰公开面；如触碰需先 DSH 架构裁决/契约变更；否则选不改变公开枚举的承载方式（如新增可选 token 字段/包 metadata）。 |
| **P1-7** | 卡 `:66-68`（禁止范围）；P5/P6 `:54-55` | **禁止范围与任务自相矛盾**：禁止范围写「不改 ThemeEngine 语义（前置 1 已做）」，但 P5 要改 `ThemeSettingsStore`/双写、P6 要改主题包 schema/模型；会误导实现者。 | 把「不改 ThemeEngine **既有语义/公开面**（除 P5/P6 明确列出的兼容写与 schema 演进）」写入禁止范围；或提升 P5/P6 为范围变更并注明。 |

### P2（9 条，建议/接受遗留）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | 卡 `:59`（AC1） | 「非法值 → V2 + 记录」的记录面未定义（日志/诊断/Shell 状态） | 指定记录通道与可测断言 |
| P2-2 | 卡 `:60`（AC2） | 「组合根按 selector 建壳；V2 路径不回归」无具体测试/断言 | 列 `App.axaml.cs` 改造点 + V2 既有 headless/回归测试名 |
| P2-3 | 卡 `:61`（AC3）；设计 `04:9-22` | Fluent Shell 骨架只写「导航+四页占位」；未对照设计 04 §1（顶部命令条+左导航+状态条）与 headless 用例 | 补骨架元素/样式引用（`Nm*` 令牌）与 headless 测试（可用 `AssemblyInfo.cs:1` 现有 Headless.XUnit） |
| P2-4 | 卡 `:54`；`NewManga.Appearance.csproj:11` | P5 说避免循环，但 Appearance 仍引用 ThemeEngine（当前未使用）；若 sink 放 App 需明确依赖方向 | 移除未使用引用或说明 adapter 依赖方向；把循环规避写成设计约束 |
| P2-5 | `check.ps1` 第 4 警告；`verification/FEA-06-PREREQ-1/**` | PREREQ-1 `evidence_dir` 仍有 3 个未登记过程文件（`appearance-coordinator-tests.log`/`delivery-notes.md`/`theme-tests.log`），4 warnings 非阻塞但属证据卫生 | 移入 workspace 或登记 SOURCE_PIN；本卡证据目录保持干净 |
| P2-6 | `STATUS:7,10`；`PLAN:37` | STATUS 当前 Task/下一候选仍指 PREREQ-1（r3）；PLAN 当前 DAG 行仍写 PREREQ-1 `proposed`（行 `:21` 已 in_review） | 同步指向 PREREQ-2 范围复核/实现，修正 DAG |
| P2-7 | 卡 `:72-76`（附加裁决点） | P5/P6 引用 W-9，但附加裁决点表只有 W-1–W-3；W-9/Q-32 正式裁决仅在 goal §22 | 在卡内补 W-9 行（Q-32 依据/承接 P5/P6） |
| P2-8 | 卡 `:54-55` | P5 文字「双者收敛」笔误；P5/P6 缺依赖图/先后（P5 先还是 P6 先） | 修正文案；列 P5/P6 实现顺序/依赖 |
| P2-9 | 卡 `:13`/`:11-12`；PREREQ-1 卡 | `base_commit: cad5ebde3` 早于 PREREQ-1 实现；本卡不包含 `doc/tasks/FEA-06-PREREQ-1.md`，完成移植 AC 后需更新 PREREQ-1 状态/证据 | 明确 PREREQ-1 closeout 由谁/在何路径更新；或允许本卡更新该卡 |

---

## 3. 处置建议

1. **补 P0-1/P0-2 写域与测试**：`App/Services/**`、`ThemeEngine/Models/**`、`Serialization/**`、`Themes/**`、`tests/NewManga.ThemeEngine.Tests/**`、`tests/NewManga.DesignSystem.Tests/**`、`tests/NewManga.Appearance.Tests/**`；P5/P6 写清方法/字段/schema/测试。
2. **拆 P0-3 依赖环**：由 DSH 决定 PREREQ-1 以「Q-32 裁决 + PARTIAL residual 接受」done，或改本卡 `depends_on`/交付顺序；在卡内标明移植 AC 来源。
3. **修 P1-1→P1-7**：selector 按 `frontendId`；CLI 优先级；P5 唯一写者/sink；P6 实现路径+公开面分析；AC5/AC6 测试表；禁止范围措辞。
4. P2 逐项并入；补 check/STATUS/PLAN/LEDGER 指针；修完派 **scope-r2**（同一独立席位），P0/P1=0 后再释放实现。

## 4. 边界声明

本报告只审**范围/卡/冻结契约/写域/可执行性/治理指针**，不实现本卡，不审 PREREQ-2 未来代码；`check.ps1`/`verify_pins` 为只读参考，不替代审查。未修改源码/卡/设计，未 commit/push；行号基于 `a81771bdd` 实测。
