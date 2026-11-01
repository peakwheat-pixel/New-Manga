---
task_id: FEA-06-PREREQ-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: cad5ebde3
reviewed_head: efcd48022
decision: changes_requested
counts: { P0: 2, P1: 8, P2: 11 }
---

# FEA-06-PREREQ-1 范围冻结复核 r1（独立上下文；本席位未参与本卡起草）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-1.md`（`proposed`；C-03 落地 + G-1/G-1b/G-1c 令牌 + 三态动效） |
| base_commit | `cad5ebde3`（卡创建前的 commit；`git merge-base --is-ancestor` 通过） |
| reviewed_head | `efcd48022`（`docs(goal): FEA-04b 冻结 + FEA-06 拆前置记录；待裁决 Q-29/Q-30`） |
| 上游 | `doc/reviews/FEA-06-scope-r1.md:117`（P0-1 C-03 实现不存在）/`:124`（P1-1 令牌无承接）；`doc/tasks/FEA-06.md:84-87`（W-5…W-8） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；本任务只读，未参与 PREREQ-1 起草；此前复核 FEA-05-WIRE-1/PORT-1 与 FEA-06 范围 r1，均为只读评审，无实现关系；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-02 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 2 / P1 = 8 / P2 = 11（共 21）** |

> **一句话结论**：**changes_requested**。卡把上游 P0-1/P1-1 拆成独立前置的方向正确（W-1/W-2/W-3 与 FEA-06 `W-7` 一致，依赖 `FEA-04b` 成立），但**当前写法不可执行**：①**写域不足以承载 P1–P4/AC1–AC5**——新增 `NewManga.Appearance` 项目需要 `NewManga.sln` 与 `NewManga.App.csproj`（均不在 `allowed_paths`），G-1 令牌必须改 `NewManga.DesignSystem/**`（`TokenMap`/`TokenGenerator`/`TokenDictionaryWriter`/生成产物）与 `NewManga.DesignSystem.Tests`（`TokenPipelineTests` 硬编码 71/141 等计数），也都不在写域；②**令牌“生成”机制未裁决**——`tokens.json` 是 FROZEN 源、`NmKeys.g.cs`/`Tokens.Global.axaml` 是 auto-generated（`--check` 守护），G-1 四组键在冻结源中不存在，只能走 `DerivedGlobals` 扩展，而 `Nm.Elevation.*` 需要的 `BoxShadows` 类型在 `TokenValueKind` 中不存在；`Nm.Material.*` 是 dark/light 取值、应归主题层而非全局常量，涉及 `ThemeLayerRequiredKeys/AllowedKeys`（R14 测试计数）与 ThemeEngine 主题包——卡未裁决亦未写域。另 `motion.mode` 三态写成 `off/reduce/full`（C-03/设计为 `auto/full/reduce`）、C-03 §2.2 字段漏 `appearance/contrast`、迁移/唯一写者/顺序铁律未进 AC、AC2 所需 `App.axaml.cs` 不在本卡写域、`builtin.fluent-dark` 主题包无归属。需 DSH 先裁决并补齐写域/AC，再派 rev-r2。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改卡/代码/设计；`git status --porcelain` 为空；未 commit/push。本报告为本轮唯一新增文件。
- 本轮实测：`pwsh tools/governance/check.ps1` → **PASS（3 warnings：11 非终态；STATUS 3184B/40 行 80%；PLAN 3923B/57 行 80%）**；`verify_pins.ps1` → **PASS（all 15）**；`git merge-base --is-ancestor cad5ebde3 HEAD` → 0；`git log 24600bbee..HEAD -- apps tools` 为空（**949/0/57 基线仍成立**）。
- 阅读：本卡与 `FEA-06-PREREQ-2`、`FEA-06` 更新版；上游 r1；`doc/design/fluent-v1/01/02`；C-02/C-03 冻结草案与冻结记录目录；`NewManga.ThemeEngine/**`（`ThemeModels/ThemeSettingsJson/ThemeContracts/ThemeService/ThemeSettingsStore/ThemeHome/Themes`）、`NewManga.DesignSystem/Tokens|Generated|Themes|tools/TokenGen` 与 DS 测试；`NewManga.App/{Program.cs,AppOptions.cs,App.axaml.cs,Services}`；STATUS/PLAN/LEDGER；goal checkpoint §11（Q-29/Q-30）。

---

## 1. 六项必核查逐项

### 1.1 C-03 落地范围（字段一致性/原子写/迁移/与 ThemeEngine 关系）

- **字段不一致（P1-1）**：卡 P1（`:48`）列 `frontendId/visualThemeId/motion.mode/motion.categories/corners/material/layout.*/followSystemAccent/schemaVersion`；C-03 §2.2（`:34-44`）实际字段为 `theme.visualThemeId` + `theme.frontendId`、`appearance.mode`、`appearance.contrast`、`layout.*`、`motion.mode`、`appearance.followSystemAccent`、`material.acrylicStrength`/`material.micaEnabled`、`corners.scale`、`schemaVersion`（`motion.categories` 见 §2.3 `:50-55`）。卡**漏 `appearance.mode`/`appearance.contrast`**，`material` 未拆子键，命名未用 C-03 键名 → AC1「与 C-03 §2.2 逐字段一致」不成立。
- **与 ThemeEngine 的关系**：C-03 要求 `theme-settings.json`→`presentation-settings.json` **迁移矩阵**（`:34-44`）、旧 `ReducedMotion` 迁移等价（`:56-61`）、唯一写者 `NewManga.Appearance` 的 `AppearanceCoordinator`（`:68`）、旧文件只读**顺序铁律**（`:72`）、迁移幂等（`:69`）；现有 `ThemeSettings` 只有 `ThemeId/Appearance/Contrast/Layout/ReducedMotion/FollowSystemAccent`（`ThemeModels.cs:349-355`），`ThemeSettingsJson` 也只有 `reducedMotion` 布尔（`:79/:118`）。卡 AC1 只写「schemaVersion 迁移」，AC2 只写「既有 ThemeEngine 回归」，**未含旧→新映射、幂等、兼容写/顺序约束**（P1-2）。
- **写者归属冲突（P1-5）**：卡 P2（`:49`）把 `AppearanceCoordinator` 放 **App 侧**（`App/Services/Appearance*.cs`），C-03 `:68` 规定写者在 **`NewManga.Appearance`**；若按 C-03，则 Appearance 项目需引用 ThemeEngine 的 `IThemePersistence`/sink 面，若按卡写法则违反冻结契约的唯一写者定义——卡未裁决。
- **原子写/schemaVersion**：P1 有「原子写、schemaVersion 迁移」但未给 `schemaVersion=2`（C-03 `:44`）、默认值（C-03 `:57-60`）、坏文件回退（C-03 `:70`）的可测点（P2-4/P1-2）。

### 1.2 令牌生成（现有生成器契约/产物/可扩展性）

- **产物是 auto-generated，禁止手改**：`NmKeys.g.cs:1-4` 与 `Tokens.Global.axaml:5-7` 均标「@generated … do not edit by hand」；生成器为 `NewManga.DesignSystem.TokenGen`（`tools/.../Program.cs:5-11`，支持 `--check` 漂移检测，exit 1）→ 卡 P3（`:50`）「`NmKeys.g.cs`/`Tokens.Global.axaml` 增加 G-1…令牌」若按字面手改会违反管线并被 `--check` 判红（**P0-2**）。
- **源是 FROZEN tokens.json**：`tokens.json:1-8` `meta.status=FROZEN`（version 1.0.0）；`TokenGenerator.TokensRelativePath` 指向它（`TokenGenerator.cs:31-32`）；G-1 四组键在 tokens.json **不存在**（grep 仅 `focus: 2px`，`tokens.json:159`）。现有可扩展机制是 `TokenMap.DerivedGlobals`（`TokenMap.cs:149-236`，每条必须写 `Derivation` 审计）→ G-1 只能走「派生全局」扩展；卡未写用此机制/未提 `tokens.json` 不可改（P0-2）。
- **`Nm.Elevation.*` 类型缺口**：C-02 V-03（`:50-53`）规定 `Nm.Elevation.1/2/3` 为 `BoxShadows`；`TokenValueKind` 枚举**无 BoxShadows**（`TokenMap.cs:4-17`），`TokenDictionaryWriter` 的 kind 分支也无（`:242-262`）→ 必须扩生成器枚举/写出器/DS 测试，卡未提（P0-2）。
- **测试会红**：`TokenPipelineTests.cs:54-58` 硬编码 `globals==71`、`entries==141` 等；新增派生键必须同步改 `NewManga.DesignSystem.Tests`（不在写域，P0-1）。另 `R14ContractTests.cs:85-93` 把 `PaletteColorKeys=35`、`ThemeLayerRequiredKeys=59`、`ThemeLayerAllowedKeys=65` 等固定——若 `Nm.Material.*`（dark/light 取值）归主题层，则必须动这些集合与主题包格式，涉及 R-14 冻结口径，需 DSH 裁决（P0-2/P1-6）。
- **G-1b（列宽 96 常量）**：设计 `01:22` 要求「FEA-05 生成令牌时登记」；卡 P3 只提 `NmKeys/Tokens.Global` 增加「Focus.Ring/Corner.Fluent/Material/Elevation」，未给 96 的落点（DerivedGlobal Double vs 设计常量表）→ P2-1。

### 1.3 写域审计（`FEA-06-PREREQ-1.md:21-34`）

| 需要改动 | 是否在 allowed_paths | 影响 |
|---|---|---|
| 新项目 `NewManga.Appearance/**`（含 csproj） | ✓ | 但**未含** `apps/desktop-avalonia/NewManga.sln`（加入解决方案）与 `NewManga.App/NewManga.App.csproj`（App→Appearance ProjectReference）→ 全量 build/test 覆盖不到新项目/新测试（**P0-1**） |
| G-1 生成（Generator/TokenMap/Writer/产物） | ✗（缺 `NewManga.DesignSystem/**`） | P3/AC3 不可执行（**P0-1**） |
| DS 令牌管线测试（计数/键集） | ✗（缺 `tests/NewManga.DesignSystem.Tests/**`） | AC3/AC5 必红（**P0-1**） |
| `NewManga.Appearance` 单测 | ✗（无 `tests/NewManga.Appearance.Tests/**`；卡未说明借 ThemeEngine.Tests） | AC1「单测覆盖」落点不明（P2-5） |
| `App/Services/Appearance*.cs`（App 侧 coordinator） | ✓ | 但与 C-03 写者归属冲突（P1-5） |
| `AppOptions.cs` / `Program.cs` | ✓ | `Program.cs` 与 `PREREQ-2:25` **重叠**（见 1.5） |
| `App.axaml.cs`（主题/动效应用真正落点） | ✗ | AC2 不可在本卡完成（P1-5） |
| `App/Services/ThemeHome.cs`（`presentation-settings.json` 路径/根） | ✗ | 新文件路径无落点（P2-3） |
| `NewManga.ThemeEngine/**`（sink/兼容写/主题包） | ✓ | 卡未列 ThemeService/ThemeSettingsStore 迁移任务（P1-2）、未列 `builtin.fluent-dark` 主题包（P1-6） |
| 冻结源 `doc/design/redesign-v1/40-fusion/tokens.json` | ✗ | 若最终裁决改冻结源则不可行；推荐走 DerivedGlobals（P0-2） |
| `verification/FEA-06-PREREQ-1/**`、doc 指针 | ✓ | — |

### 1.4 AC 可验收（AC1–AC5）

- **AC1**（`:55`）：「项目+记录+原子读写+schemaVersion 迁移；单测（往返/坏文件/版本迁移）」——可机械但字段清单不全/迁移≠旧→新迁移（P1-1/P1-2）、测试落点缺（P2-5）。
- **AC2**（`:56`）：「读取后应用主题与动效；`AppOptions.FrontendId` 可注入；既有 ThemeEngine 回归」——**不可执行**：应用主题/动效的现有落点在 `App.axaml.cs:47-48/96/107-113`（创建 `DesignSystemThemeManager`、接 `ThemeHome`/Theme Studio），该文件不在本卡写域（归 PREREQ-2）；`Program.cs` 只做 `BuildAvaloniaApp().StartWithClassicDesktopLifetime`（`:11-22`），无法单独完成应用（P1-5）。`AppOptions.FrontendId` 语义未定义（C-03 只规定持久化 `theme.frontendId`；CLI 注入为新增面，P2-2）。
- **AC3**（`:57`）：「G-1/G-1b/G-1c 令牌代码存在且与 `01` 值与命名一致；`NmKeys.g.cs` 生成器同步」——机制未定（P0-2）、写域缺（P0-1）；`--check` 漂移守卫未进测试表（P1-7）。
- **AC4**（`:58`）：「`motion.mode` 三态 + `motion.categories=off` 语义有测试；reduce/full 差异可测」——**取值写成 `off`（P1-3）**；三态实现需 `IMotionPreferenceSource`/平台注入与 `auto` 系统源（设计 `02:57-61`、C-03 `:62`；卡未提，P1-4）；`categories=off` 的 0ms 语义只写了 feedback 一面（02:39/判据⑤；P2-6）。
- **AC5**（`:59`）：「全量 sln 不退化（949/0/57）+ 证据」——基线当前成立（自 `24600bbee` 无 apps/tools 变更，实测记录一致）✓；但需在释放时复核（P2-11）。

### 1.5 依赖与顺序

- `depends_on: FEA-04b`（`:11-12`）成立：FEA-04b 已 done（`doc/tasks/FEA-04b.md:6`），设计基线 frozen v1.0.0；C-02/C-03 已 FROZEN（`FEA-C02...:3`；`FEA-C03...:3`；目录有 `FEA-CONTRACT-FROZEN-C02/C03.md`）✓。
- **顺序**：`FEA-06-PREREQ-2` `depends_on: FEA-06-PREREQ-1`（`PREREQ-2:12`）✓；`FEA-06` 已依赖两前置（`FEA-06.md:11-15`）✓——DAG 方向正确。
- **需锁 `frontendId` 语义（Lead #5）**：C-03 `:36` 规定 `theme.frontendId` ∈ {`builtin.current-v2`,`builtin.fluent`}、`theme.visualThemeId` ∈ {`newmanga-default`,`builtin.fluent-dark`}（两个维度）；PREREQ-2 AC1（`:54`）却把 `builtin.fluent`/`builtin.fluent-dark` 并列当 selector 条件——PREREQ-1 作为 `AppearanceSettings` 定义方，应在卡内把两 id 的类型/枚举/校验（C-03 `:73`）写清并在 W 中记录，避免 PREREQ-2 误用（P2-8；跨卡接口）。
- **写域重叠**：两卡都含 `App/Program.cs`（PREREQ-1 `:27`；PREREQ-2 `:25`）；虽有 depends_on 保证顺序，PREREQ-1 应声明「只做装载点、不写 selector 分支」，否则返工（P2-7）。

### 1.6 治理

- `check.ps1` PASS（3 warnings）；`verify_pins` 15/15 ✓；`doc/TASK_LEDGER.md:45-47` 三卡 `proposed` 一致 ✓；`REBASELINE_PLAN:20-22` 三行已列且依赖正确 ✓。
- **指针不一致（P1-8）**：`doc/STATUS.md:7` 仍「…`FEA-04b` in_review；上一 `FEA-04b` in_review」（实际 done，PLAN `:17` 已改 done）；`STATUS:10` 仍「下一候选：`FEA-04b`（设计基线待用户确认）；`FEA-05-PORT-1` 待建卡」；`REBASELINE_PLAN:37`「当前 DAG：FEA-06…、FEA-05-PORT-1…、FEA-05-WIRE-1…、FEA-04b…」未含 PREREQ-1/2。`check.ps1` 不校验此一致性。
- **待裁决项**：goal §11 记 **Q-29**（三卡复核派发顺序；本次先审 PREREQ-1 与推荐一致 ✓）与 **Q-30**（`suggested_owner: dsh` vs ZCode UI 主责；ZCode 未安装）仍「待裁决」（`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:96-97`）。本卡 `suggested_owner: dsh`（`:8`）无括注，基础设施卡可接受，但应在卡内引用 Q-30 决议（P2-9）。

---

## 2. Findings

### P0（2 条，阻塞范围冻结）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P0-1** | 卡 `:21-34`（allowed_paths）、`:50`（P3）、`:55/:57（AC1/AC3）；`apps/desktop-avalonia/NewManga.sln`；`apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj`；`NewManga.DesignSystem/**`；`tests/NewManga.DesignSystem.Tests/**`；`NmKeys.g.cs:1-4`；`Tokens.Global.axaml:5-7`；`TokenPipelineTests.cs:54-58` | **写域不足以承载本卡任务/AC。** 新增 `NewManga.Appearance` 项目必须改 `NewManga.sln`（否则全量 build/test 不含新项目）且 App 需 `ProjectReference`（`App.csproj` 不在写域）；G-1 令牌只能经 `NewManga.DesignSystem/**`（`TokenMap.cs`/`TokenGenerator.cs`/`TokenDictionaryWriter.cs`）+ 重生成 `NmKeys.g.cs`/`Tokens.Global.axaml` 实现；`TokenPipelineTests` 硬编码 71/141 等计数，新增键必红但 DS 测试不在写域；`NewManga.Appearance` 单测也无落点 | 补写域：`NewManga.sln`、`NewManga.App.csproj`、`NewManga.DesignSystem/**`（含 tools/TokenGen）、`tests/NewManga.DesignSystem.Tests/**`、`tests/NewManga.Appearance.Tests/**`（或明确借 ThemeEngine.Tests 并给 csproj 改动权）；若必须改 `tokens.json` 则另加 `doc/design/redesign-v1/40-fusion/tokens.json` 并走冻结源变更裁决 |
| **P0-2** | 卡 `:50`（P3）、`:57`（AC3）；`tokens.json:1-8`（FROZEN）；`TokenGenerator.cs:31-32`；`TokenMap.cs:4-17,149-236`；`TokenDictionaryWriter.cs:242-262`；`design/01:13-22`；`C-02:50-53` | **G-1 令牌“生成”机制未裁决，且现有生成器无法直接产出。** 生成产物为 auto-generated（禁止手改、`--check` 守护）；FROZEN `tokens.json` 不含 G-1 四组键；唯一扩展点是 `DerivedGlobals`（需逐条 `Derivation`），但 `Nm.Elevation.*` 的 `BoxShadows` 类型在 `TokenValueKind`/Writer 中不存在；`Nm.Material.*` 是 dark/light 取值（`01:41-42`），应归主题层而非全局常量，涉及 `ThemeLayerRequiredKeys/AllowedKeys`（R14 测试 59/65）与 ThemeEngine 主题包格式；设计 `01:20` 明确「若 FEA-05 无法在 C-02 已冻结名义下生成，须先由 DSH 裁决」——卡未裁决就写「生成」 | DSH 先裁决：①哪些键为全局派生（Corner.Fluent、Focus.Ring.Width/Offset）、哪些为主题层/主题包键（Material、Elevation、Focus.Ring.Color）；②是否扩 `TokenValueKind.BoxShadows`/主题包 schema/`ThemeLayerAllowedKeys`；③`DerivedGlobals` 的 derivation 文本与 R-14/R-15 口径；④`--check` 回归命令。AC3 改为「`TokenGen --check` 0 + 生成键集/取值单测」 |

### P1（8 条，必须修）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P1-1** | 卡 `:48`（P1）、`:55`（AC1）；C-03 `:34-44`；`08:45-54` | **C-03 §2.2 字段清单不完整/命名不一致**：漏 `appearance.mode`/`appearance.contrast`；`material` 未拆 `acrylicStrength`/`micaEnabled`；未用 `theme.visualThemeId`/`theme.frontendId`/`appearance.followSystemAccent`/`corners.scale` 键名 | 按 C-03 §2.2 逐字段列表重写 P1/AC1（含嵌套结构与枚举域：`motion.mode`、`material.*`、`corners.scale`、`frontendId`/`visualThemeId` 域，C-03 `:73`） |
| **P1-2** | 卡 `:55-56`（AC1/AC2）；C-03 `:56-61,68-72`；`ThemeModels.cs:349-355`；`ThemeSettingsJson.cs:79,118`；`ThemeService.cs:163/326/375-400` | **C-03 迁移与写者纪律未进 AC**：缺旧 `ReducedMotion`→`motion.mode`/三类迁移等价（true→reduce+三禁；false→full；auto 仅新装/显式）、迁移幂等、旧文件只读顺序铁律、`ThemeSettingsStore` 一个 release 兼容写；AC2 只「既有回归」 | AC1 增「迁移矩阵逐行 + 幂等 + 兼容写/顺序」测试；AC2 增 ThemeService/ThemeSettingsStore 兼容期行为测试与 `AppearanceCoordinator` 唯一写者断言 |
| **P1-3** | 卡 `:51`（P4）、`:58`（AC4）；C-03 `:48`；design `02:24-51` | **`motion.mode` 取值错误**：卡写 `off`/`reduce`/`full`；C-03/设计三态为 `auto`（跟随系统）/`full`/`reduce`，不存在 `off`；错误命名会传染 AC4/实现/测试 | 改为 `auto/full/reduce`，并给默认值（C-03 `:57-60`）与迁移映射 |
| **P1-4** | 卡 `:51`（P4）、`:58`（AC4）；design `02:57-61,63-68`；C-03 `:62` | **三态实现面未定义**：`auto` 需平台源 `IMotionPreferenceSource`（Windows SPI/UISettings；Avalonia 11.3.22 无 API）；缺判据 ①–⑤ 测试点（decorative 0；feedback 保留颜色无位移；auto 注入；navigation 无动画；迁移等价）；无渲染环境关动效要求未提 | P4/AC4 增平台抽象（`IMotionPreferenceSource` + 假源测试）、①–⑤ 逐条断言、无渲染关闭开关 |
| **P1-5** | 卡 `:49`（P2）、`:56`（AC2）；`App.axaml.cs:47-48,96,107-113`；`Program.cs:11-22`；C-03 `:68` | **AC2 在本卡写域内不可执行 + 写者归属冲突**：应用主题/动效的现有落点在 `App.axaml.cs`（本卡无写权，归 PREREQ-2），`Program.cs` 只是启动器；卡又把 `AppearanceCoordinator` 放 App 侧，与 C-03「写者在 `NewManga.Appearance`」冲突 | 二选一：①把「应用主题/动效」移给 PREREQ-2（PREREQ-1 只交持久化+模型+令牌），AC2 改为「Appearance 项目输出 + App 侧装载钩子（PREREQ-2 消费）」；②把 `App.axaml.cs` 纳入本卡并在 W 中改 `AppearanceCoordinator` 归属为 `NewManga.Appearance`（按 C-03） |
| **P1-6** | 卡 P1-P4/AC 全篇；C-02 `:86-90,110,117`；`BuiltInThemes.cs:15`；`Themes/` 仅 `newmanga-default.nmtheme` | **`builtin.fluent-dark` 视觉主题包无归属**：C-02 V-07 要求视觉主题注册表新增 `builtin.fluent-dark` 条目（manifest `nm.fluent.visual/1`）；PREREQ-1 P2「应用主题」需要该主题包，但卡未含创建/生成（ThemeEngine 写域在本卡，主题包生成器 ThemeGen 也在 ThemeEngine/tools；PREREQ-2/主卡无 ThemeEngine 写域） | 在本卡 P 增「`builtin.fluent-dark` 主题包/清单（含 Material/Elevation/Focus.Ring 取值）+ ThemeGen 生成 + 注册表条目」并给 AC；或明确由后续卡承担并在依赖中登记 |
| **P1-7** | 卡 `:73-78`（测试要求）；`:57`（AC3） | **测试/证据不覆盖生成管线**：只跑 ThemeEngine.Tests/App.Tests/全量 sln，缺 `TokenGen -- --check`（漂移守卫）与 `ThemeGen -- --check`（若动主题包）；AC3「生成器同步」无证据 | 测试表增：`dotnet run --project .../NewManga.DesignSystem.TokenGen -- --check`（EXIT 0）、`ThemeGen --check`（如适用）、DS 生成键集/取值断言 |
| **P1-8** | `doc/STATUS.md:7,10`；`doc/REBASELINE_PLAN.md:37` | **治理指针不一致**：STATUS 仍 FEA-04b in_review / 上一 in_review、下一候选 FEA-04b/待建卡；PLAN `:37` DAG 行未含 PREREQ-1/2（`:20-22` 行已正确）；check.ps1 PASS 不校验 | 释放前同步 STATUS 当前 Task/上一 Task/下一候选；PLAN DAG 行补两前置；再跑 check.ps1 |

### P2（11 条，建议/接受）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | 卡 `:50`；design `01:22`；`06:37` | G-1b 列宽 96 常量落点未定（DerivedGlobal `Double` vs 设计常量表） | 明确「`Nm.Size.BatchMatrixColumnMin=96`（派生，derivation 引用 06:37）」或「设计常量类」并登记 |
| P2-2 | 卡 `:49/56`；C-03 `:36` | `AppOptions.FrontendId` 语义/来源未定义（C-03 仅规定持久化 `theme.frontendId`；CLI 注入为新增面） | 明确「仅测试/诊断覆盖，不替代持久化值」或删除 |
| P2-3 | 卡 P1/P2；`ThemeHome.cs:6-14,34-38` | `presentation-settings.json` 路径/根（是否沿用 `--theme-home` 目录）未定义；该文件在 `ThemeHome`（不在写域） | 在 AC1 写路径解析规则；补 `ThemeHome.cs` 写权或改为 `AppearanceSettingsStore` 自带 `--theme-home` 兼容解析 |
| P2-4 | 卡 `:55`；C-03 `:44,57-60,70` | `schemaVersion=2` 具体值、默认值（`auto`/`full`）、坏文件回退 warning 未写入 AC | AC1 列明 |
| P2-5 | 卡 `:55`、`:77` | AC1 单测落点不明（无 Appearance.Tests；借 ThemeEngine.Tests 需 csproj 改动权） | 明确测试项目与 ProjectReference；或归入 P0-1 写域 |
| P2-6 | 卡 `:58`；design `02:39,57-61` | `motion.categories=off` 语义表述过窄（只写 feedback 0ms；navigation/decorative 的 off 列与 feedback 颜色过渡 0ms 需覆盖） | AC4 按 §3 判据①–⑤ 逐条写 |
| P2-7 | `PREREQ-1:27` vs `PREREQ-2:25` | 两卡都写 `Program.cs`；虽 depends_on 保证顺序，仍可能返工 | PREREQ-1 声明只做装载点，selector 分支留 PREREQ-2；两卡 W 记录接口 |
| P2-8 | `PREREQ-2:54`；C-03 `:73` | PREREQ-2 AC1 把 `builtin.fluent-dark`（visualThemeId）与 `builtin.fluent`（frontendId）并列当 selector 值；两维度语义需在 PREREQ-1 定义时锁定 | PREREQ-1 的 `AppearanceSettings` 明确两枚举域并在 W 记录；PREREQ-2 按 frontendId 决策 |
| P2-9 | 卡 `:8`；goal `:96-97`（Q-30） | `suggested_owner: dsh` 与 ZCode UI 主责/故障转移的裁决仍「待裁决」；本卡为基础设施卡可接受 | 卡内引用 Q-30 决议与「ZCode 可用时交接」条件 |
| P2-10 | 卡 `:41`；C-03 `:3`；`FEA-CONTRACT-FROZEN-C03.md` | 卡称「C-03 冻结草案」不准确——C-03 已 FROZEN v6（2026-11-01，有冻结记录）；应引用冻结记录而非「草案」 | 改「C-03（FROZEN v6，`FEA-CONTRACT-FROZEN-C03.md`）」 |
| P2-11 | 卡 `:59`（AC5） | 949/0/57 基线当前成立（自 `24600bbee` 无 code 变更），但释放时需复核；证据表尚无条目 | 释放时复跑并填 Canonical Evidence |

---

## 3. AC 逐项（可机械验收？）

| AC | 判定 | 说明 |
|---|---|---|
| AC1（`:55`） | **部分** | 字段清单不全（P1-1）、迁移≠旧→新（P1-2）、测试落点缺（P0-1/P2-5） |
| AC2（`:56`） | **不可执行** | 需 `App.axaml.cs`（不在写域，P1-5）；协调器归属冲突；FrontendId 语义未定（P2-2） |
| AC3（`:57`） | **不可执行** | 生成机制未裁决/写域缺（P0-1/P0-2）；无 `--check` 证据（P1-7） |
| AC4（`:58`） | **部分** | 取值错误 `off`（P1-3）；三态实现面缺（P1-4）；categories 语义窄（P2-6） |
| AC5（`:59`） | **可执行** | 949/0/57 当前成立；释放时复核（P2-11） |

---

## 4. 处置建议（按序）

1. **DSH 裁决（P0）**：①G-1 各键的归属（全局派生 / 主题层 / 主题包）与生成机制（`DerivedGlobals` + `TokenValueKind.BoxShadows` + ThemeGen/主题包 schema 扩展）；②`AppearanceCoordinator` 归属（`NewManga.Appearance` 按 C-03）与「应用主题/动效」落在哪张卡（PREREQ-1 vs PREREQ-2）；③`builtin.fluent-dark` 主题包/清单归属；④是否允许扩 `ThemeLayerAllowedKeys` 等 R-14 冻结口径。
2. **补写域（P0-1）**：`NewManga.sln`、`App.csproj`、`NewManga.DesignSystem/**`、`tests/NewManga.DesignSystem.Tests/**`、`tests/NewManga.Appearance.Tests/**`（或明确借用）、必要时 `tokens.json`（仅当裁决改冻结源）。
3. **改 AC/任务（P1）**：C-03 §2.2 逐字段（含 appearance/contrast）；迁移矩阵/幂等/顺序铁律/兼容写；`motion.mode=auto/full/reduce`；平台源与判据①–⑤；AC2 落点；主题包；`--check` 证据；同步 STATUS/PLAN（P1-8）。
4. **P2 逐项并入**；修完派 **rev-r2**（独立上下文），P0/P1=0 再冻结范围并释放实现（随后 PREREQ-2 → FEA-06）。

## 5. 边界声明

本报告只审**范围/卡/冻结契约/生成器契约/写域/可执行性**，不审 C-02/C-03 内容本身（互已 FROZEN，独立复核记录在案），也不审未实现的代码；未运行 UI/生成器（除只读检查外）。`check.ps1`/`verify_pins` 为只读参考，不替代审查。本席位未参与 FEA-06-PREREQ-1 起草或实现，未修改被审文件、未 commit/push；行号基于 `efcd48022` 实测。
