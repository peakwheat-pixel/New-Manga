---
task_id: FEA-06-PREREQ-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: efcd48022
reviewed_head: 2c5658fae
decision: changes_requested
counts: { P0: 0, P1: 4, P2: 12 }
---

# FEA-06-PREREQ-1 范围冻结复核 r2（独立上下文；本席位未参与本卡起草）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-1.md`（v2；`proposed`） |
| base_commit | `efcd48022`（r1 被审 head） |
| reviewed_head | `2c5658fae`（`docs(fea-06-prereq-1): 范围 v2（r1 P0×2/P1×8 处置…）`） |
| 上游 | `doc/reviews/FEA-06-PREREQ-1-scope-r1.md`（P0×2/P1×8/P2×11） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；本任务只读，未参与 PREREQ-1 起草；此前复核 FEA-05/FEA-06 系列均为只读评审，无实现关系；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-02 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 4 / P2 = 12（共 16）** |

> **一句话结论**：**changes_requested**。**r1 的 P0×2 已实质关闭**：写域补齐（`NewManga.sln`/`App.csproj`/`DesignSystem/**`/DS 测试/Appearance 测试）——经核无剩余必须缺口，且 `tokens.json` 按 `DerivedGlobals` 方案**确实无需入写域**（仅 Focus/Corner/Elevation 走派生；Material 走主题包，值来自设计 01，不进冻结源）；G-1 生成机制已裁决（W-4/W-5，禁手改生成产物、`BoxShadows` 新类型、Material 主题层）。r1 的 P1-1/2/3/4/5 已关闭。但仍有 **4 条 P1**：①**W-8 的 `builtin.fluent-dark` 主题包没有对应任务行/AC**（任务表仍只有 P1–P4，AC1–AC5 无主题包条目，仅测试表出现 `ThemeGen --check`）；②**AC3 生成落点不完整**——`Material.*` 作为主题层键如何进 `NmKeys.g.cs` 常量而不进 `Tokens.Global.axaml`、主题包 schema/校验、`R14ContractTests` 的 59/65 计数更新均未写明；`Elevation`/`Focus.Ring.Color` 的 global vs 主题层归属仍留歧义；③**测试计划仍缺 `NewManga.Appearance.Tests` 与 `NewManga.DesignSystem.Tests` 两条命令**（AC1 明写 Appearance.Tests 覆盖、AC3 明写计数更新，但命令表未跑新项目）；④**AC3 声称覆盖 G-1b 却未含 96 列宽常量的登记**。另 W-3 表格列数错误、STATUS 残留旧指针、W-6 下游（PREREQ-2）未记录应用落点等 12 条 P2。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改卡/代码/设计；`git status --porcelain` 为空；未 commit/push。本报告为本轮唯一新增文件。
- 本轮实测：`check.ps1` → **PASS（3 warnings：11 非终态；STATUS 3185B/41 行 80%；PLAN 3917B/58 行 80%）**；`verify_pins` → **PASS（all 15）**；`git log efcd48022..HEAD -- apps tools` 为空 → **949/0/57 基线仍成立**；`git merge-base --is-ancestor cad5ebde3 HEAD` → 0。
- diff 范围：仅 `doc/tasks/FEA-06-PREREQ-1.md`（+29/−…）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 与本席位 r1 报告；**`FEA-06-PREREQ-2`/`FEA-06` 未改动**。

---

## 1. r1 findings 逐项 disposition

| r1 ID | 判定 | 证据（v2） |
|---|---|---|
| **P0-1** 写域 | **CLOSED** | 卡 `:21-39` 已补 `NewManga.sln`、`App/NewManga.App.csproj`、`NewManga.DesignSystem/**`、`NewManga.DesignSystem.Tests/**`、`NewManga.Appearance.Tests/**`；核实现有仓库无 `Directory.Packages.props`（新测试 csproj 自含版本即可），`Directory.Build.props` 由新项目自动继承 → 无剩余必须缺口。**`tokens.json` 结论：无需入写域**——Focus/Corner/Elevation 走 `TokenMap.DerivedGlobals`（`TokenMap.cs:149-236`，不读 tokens.json 新增键），Material 走主题包（见 P1-2），冻结源不动 ✓ |
| **P0-2** G-1 生成机制 | **CLOSED** | W-4（`:77`）分三组归属、W-5（`:78`）禁手改生成产物；P3（`:55`）改为 DerivedGlobals/`BoxShadows`/主题层；AC3（`:62`）重写；测试表（`:88`）补 `TokenGen -- --check`/`ThemeGen -- --check` ✓（残留 P1-2/P1-4） |
| **P1-1** C-03 字段 | **CLOSED** | P1（`:53`）逐字段列 `appearance.mode/contrast/followSystemAccent`、`corners.scale`、`material.acrylicStrength/micaEnabled`、`theme.frontendId/visualThemeId`、`motion.mode/categories`、`layout.*`、`schemaVersion`，与 C-03 §2.2（`:34-44`）一致 ✓（枚举域校验见 P2-5） |
| **P1-2** 迁移/写者纪律 | **CLOSED** | P1（`:53`）+AC1（`:60`）含旧 `ReducedMotion`→`motion.mode` 等价、幂等、旧文件只读顺序、`ThemeSettingsStore` 一个 release 兼容写，测试含「兼容写」✓（C-03 `:56-72`） |
| **P1-3** `motion.mode` 取值 | **CLOSED** | P4（`:56`）/AC4（`:63`）改为 `auto`/`full`/`reduce` 并明写「无 `off`」✓（C-03 `:48`；设计 02） |
| **P1-4** 三态实现面 | **CLOSED** | P4 增 `IMotionPreferenceSource`（平台 SPI、默认实现+可注入）；AC4 要求设计 02 判据 ①–⑤ 有测试 ✓（残留 categories 细则 P2） |
| **P1-5** Coordinator 归属 | **CLOSED（本卡）** | P1（`:53`）写者在 `NewManga.Appearance`（C-03:68）；P2（`:54`）App 侧只读取/校验/变更通知；应用主题/动效归 PREREQ-2（W-6 `:79`）✓。**但下游 PREREQ-2 未更新**（见 P2-8） |
| **P1-6** `builtin.fluent-dark` | **PARTIAL → P1-A** | W-8（`:81`）表「本卡交付主题包」，但任务表 `:51-56` 无 P5/P5b 行、AC1–AC5（`:60-64`）无主题包 AC；仅测试表（`:88`）有 `ThemeGen --check` → 交付物无任务/验收承载 |
| **P1-7** 生成管线证据 | **PARTIAL → P1-C** | AC3/测试表已补 `TokenGen --check`/`ThemeGen --check` ✓；但 AC1–AC4 命令（`:87`）仍只有 ThemeEngine.Tests+App.Tests，**缺 `NewManga.Appearance.Tests` 与 `NewManga.DesignSystem.Tests`**（AC1/AC3 明写要覆盖） |
| **P1-8** 治理指针 | **PARTIAL → P2-11** | PLAN DAG（`:37`）已改「PREREQ-1→PREREQ-2→FEA-06」✓；LEDGER 计数更新 ✓；但 `STATUS:7` 仍「上一 `FEA-04b` `in_review`（r5 approved，AC5 待确认）」、`STATUS:10` 仍「下一候选：`FEA-04b`（设计基线待用户确认）；`FEA-05-PORT-1` 待建卡」→ 残留 stale |
| P2-1（96） | **升级为 P1-D** | AC3 声称覆盖 G-1b，但全文无 96 列宽常量登记方式 |
| P2-2（FrontendId） | 开（P2-1） | 卡 `:54` 仍只写「`AppOptions` 暴露 `FrontendId`」，无语义/来源/是否替代持久化值 |
| P2-3（路径/ThemeHome） | 开（P2-2） | P1 只说 `presentation-settings.json`，未写路径解析/`--theme-home` 语义；`ThemeHome.cs` 仍不在写域 |
| P2-4（schemaVersion） | 部分（P2-3） | AC1 有坏文件；未写 `schemaVersion=2`（C-03:44）、默认值（C-03:57-60）、缺字段 warning（C-03:70） |
| P2-5（Appearance 测试落点） | **CLOSED** | `allowed_paths:33` + AC1 明写 `NewManga.Appearance.Tests` 覆盖 ✓ |
| P2-6（categories 语义） | **CLOSED（基本）** | AC4 含 `categories=off` 0ms + 判据 ①–⑤；细分见 P2-12 |
| P2-7（Program.cs 重叠） | 开（P2-4） | PREREQ-1 `:31` 与 PREREQ-2 `:25` 均含 `Program.cs`，卡未声明「只做装载点」分工 |
| P2-8（frontendId/visualThemeId 语义） | 部分（P2-5） | 字段已列，但枚举域/校验未写入 AC；PREREQ-2 AC1 仍混用两者（其卡未更新） |
| P2-9（Q-30 owner） | 开（P2-12） | 卡 `:8` 仍 `suggested_owner: dsh`，未引用 Q-30 待裁决记录（goal §11） |
| P2-10（C-03 称谓） | 开（P2-6） | 卡 `:46`/W-2 `:75` 仍称「C-03 冻结草案」；实为 FROZEN v6（`FEA-C03...:3`，有 `FEA-CONTRACT-FROZEN-C03.md`） |
| P2-11（AC5 基线） | 开（P2-7） | AC5 沿用 949/0/57（当前成立），未写释放时复核/证据条目 |

---

## 2. 六项必核查（v2 结论）

1. **C-03 落地范围**：字段逐项一致 ✓；写者在 Appearance ✓；迁移/幂等/顺序/兼容写进 AC1 ✓（残留 P2-1/2/3/5）。
2. **令牌生成**：机制已裁决（DerivedGlobals + `BoxShadows` + Material 主题层）✓；但 **Material 主题层键的 `NmKeys.g.cs` 常量来源、`Tokens.Global.axaml` 排除、主题包 schema/校验、`R14ContractTests` 59/65 计数**未写明（P1-B）；`Elevation`/`Focus.Ring.Color` 的 global vs 主题层归属仍有歧义（W-4 只写组级归属）。
3. **写域审计**：无必须缺口（P0-1 关闭）；`tokens.json` 无需入写域（DSH 判断正确，理由见 P0-1）；`Appearance.Tests` 新项目可入 sln ✓；`ThemeEngine/tools/**` 在 `ThemeEngine/**` 内 ✓。
4. **AC 可验收**：AC1 需补 Appearance.Tests 命令；AC2 可执行（读取/校验/通知；应用归 PREREQ-2）；AC3 需补 DS 测试命令与主题包/计数验收；AC4 可执行；AC5 基线成立。→ **AC1/AC3 仍差命令与主题包 AC**（P1-A/P1-C）。
5. **依赖与顺序**：`depends_on: FEA-04b`（done）✓；PREREQ-2 `depends_on: PREREQ-1` ✓（其未改，见 P2-8）；FEA-06 依赖两前置 ✓（`FEA-06.md:11-15`）；`frontendId`/`visualThemeId` 语义需在 AppearanceSettings 定义时锁定（P2-5）。
6. **治理**：check.ps1 PASS（3 warnings）、verify_pins 15/15 ✓；PLAN DAG/LEDGER 已同步 ✓；STATUS 两处残留 stale（P2-11）；Q-29/Q-30 仍「待裁决」（goal §11），Q-29 本次先审 PREREQ-1 与推荐顺序一致 ✓。

---

## 3. Findings

### P1（4 条，必须修）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P1-A** | 卡 `:81`（W-8）、`:51-56`（任务表）、`:60-64`（AC） | **W-8 的 `builtin.fluent-dark` 主题包无任务行/AC。** 任务表只有 P1–P4；AC1–AC5 无主题包/注册表/manifest 条目；仅测试表 `:88` 出现 `ThemeGen --check`。r1 P1-6 的所有权已裁，但交付物仍未落到可验收项，实现易漏 `Themes/*.nmtheme`、`BuiltInThemes`/`ThemeRegistry` 注册与 C-02 V-07 `nm.fluent.visual/1` manifest | 任务表增 P5（`builtin.fluent-dark` 主题包 + ThemeGen 生成 + 注册表 + manifest）；AC1–AC5 增一条 AC（包可加载、Material 键在包内、Current 下不生效、`ThemeGen --check` EXIT 0、主题包单测） |
| **P1-B** | 卡 `:55`（P3）、`:62`（AC3）；`TokenMap.cs:4-17,149-236`；`TokenDictionaryWriter.cs:242-262`；`DesignSystemThemeManager.cs:114-130`；`R14ContractTests.cs:85-93`；`ThemePackageJson`/`ThemeValidator` | **AC3 生成落点不完整**：①`Material.*` 归主题层后，`NmKeys.g.cs` 仍需常量（FEA-06/XAML 要引用），但 `DerivedGlobals` 是**全局**资源机制（`TokenMap.cs:149-152`），不能同时产出「常量有、`Tokens.Global.axaml` 无」——需要新增「主题层键清单/生成通道」并写明；②主题包 schema/校验（`ThemeLayerAllowedKeys` 现为「59 required + 6 line boxes，其他忽略」，`DesignSystemThemeManager.cs:123-130`）须扩展并更新 `R14ContractTests`（59/65）——AC3 只点名 `ThemeGeneratorTests`/`TokenPipelineTests`；③`Elevation`/`Focus.Ring.Color` 是全局还是主题层在 W-4 组级归属下仍歧义（`Focus.Ring.Color` 随主题 accent 变化） | 在 P3/AC3 写明：主题层键清单（Material.* + 可能的 Focus.Ring.Color）、`NmKeys` 常量来源、`Tokens.Global` 排除规则、主题包 schema/`ThemeLayerAllowedKeys` 扩展、`R14ContractTests` 计数更新与「Current 下不生效」断言；BoxShadows writer 的 XAML 值格式/解析测试也写入 AC3 |
| **P1-C** | 卡 `:87`（测试要求）；`:60`（AC1）、`:62`（AC3） | **测试命令缺新项目**：AC1 明写 `NewManga.Appearance.Tests` 覆盖、AC3 明写计数更新，但 AC1–AC4 命令只跑 `ThemeEngine.Tests` + `App.Tests`；新项目/DS 计数测试不在证据清单，AC1/AC3 无法机械验收 | 测试表增 `dotnet test .../tests/NewManga.Appearance.Tests`、`.../tests/NewManga.DesignSystem.Tests`（或明确合并理由，如新 csproj 加入 sln 后全量命令覆盖；则 AC5 全量命令可覆盖，但需写明） |
| **P1-D** | 卡 `:62`（AC3）；`design/01:22`；`06:37`；`selfcheck:44` | **AC3 声称覆盖 G-1b，但未含列宽 96 常量**：G-1b 要求「批量矩阵列宽最小 96」登记（`01:22`/`06:37`，FEA-04b r4 明确从 `RowNormal` 改回 96 并登记），AC3 全文只有「G-1/G-1b/G-1c 令牌经 DerivedGlobals…」，96 的落点（派生 `Nm.Size.BatchMatrixColumnMin` 还是设计常量表）未写 → G-1b 未真正可验收 | AC3/P3 增「G-1b：96 作为 `DerivedGlobal`（`Double`，derivation 引 `06:37`）或设计常量，并给 FEA-06 消费断言」；若归 FEA-06 常量则改 G-1b 表述 |

### P2（12 条，建议/接受）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | 卡 `:54`；C-03 `:36` | `AppOptions.FrontendId` 语义/来源未定义（C-03 只规定持久化 `theme.frontendId`；CLI 注入为新增面，若与持久化值冲突以谁为准未写） | 明确「仅测试/诊断覆盖；不替代持久化值」或删除 |
| P2-2 | 卡 `:53`；`ThemeHome.cs:6-14,34-38` | `presentation-settings.json` 路径/根（是否沿用 `--theme-home` 目录）、`ThemeHome` 是否需改未定义；`ThemeHome.cs` 仍不在写域 | AC1 写路径解析规则；如需改 `ThemeHome` 则补写域或改由 Appearance 自带解析 |
| P2-3 | 卡 `:60`；C-03 `:44,57-60,70` | `schemaVersion=2` 具体值、默认值（`auto`/`full`）、缺字段回退 warning 未写入 AC | AC1 列明 |
| P2-4 | `PREREQ-1:31` vs `PREREQ-2:25` | 两卡都含 `Program.cs`；虽 depends_on 保证顺序，PREREQ-1 未声明「只做装载点，selector 分支归 PREREQ-2」 | 卡内写明分工/W 记录，避免返工 |
| P2-5 | 卡 `:53`/`:60`；`PREREQ-2:54`；C-03 `:73` | `frontendId`/`visualThemeId` 枚举域/校验未写入 AC；PREREQ-2 AC1 仍把 `builtin.fluent-dark`（visualThemeId）与 `builtin.fluent`（frontendId）并列当 selector 值 | AC1 增枚举域校验断言；PREREQ-2 修正为按 `frontendId` 决策 |
| P2-6 | 卡 `:46`、W-2 `:75` | 仍称「C-03 冻结草案」；实为 FROZEN v6（2026-11-01，`FEA-CONTRACT-FROZEN-C03.md`） | 引用冻结记录/版本 |
| P2-7 | 卡 `:64`（AC5） | 949/0/57 基线当前成立（自 `24600bbee` 无 code 变更），但未写释放时复核；Canonical Evidence 仍空 | 释放时复跑并填证据 |
| P2-8 | `PREREQ-2` 任务/AC（`:43-57`） | **W-6 下游未记录**：PREREQ-2 未改，其任务/AC 无「读取 `AppearanceSettings` → 应用主题/动效」，而 W-6 把应用落点交给它；PREREQ-1 关闭 P1-5 后 PREREQ-2 需承接，否则责任空洞 | PREREQ-2 复核/修订时补 P/AC 与 `AppearanceSettings` 读取依赖 |
| P2-9 | 卡 `:55`/`:62`；`design/01:41-47` | Material/Elevation 的**取值来源**（设计 01 §2.2/§2.4）与主题包生成/校验测试未点名（W-4 只说归主题层/BoxShadows） | P3/AC3 写明值来源（design 01 值表）、生成与校验测试（Current 不生效/坏包） |
| P2-10 | 卡 `:76`（W-3 行） | 表格列数错误：W 表 4 列，W-3 行只有 3 个单元格（`| W-3 | 令牌缺口归本卡，FEA-06 只消费 | 设计基线 01 |`），渲染错位 | 补「裁决」列 |
| P2-11 | `doc/STATUS.md:7,10` | r1 P1-8 残留：`:7` 仍「上一 `FEA-04b` `in_review`（r5 approved，AC5 待确认）」、`:10` 仍「下一候选：`FEA-04b`…；`FEA-05-PORT-1` 待建卡」 | 同步 STATUS 当前/上一/下一候选 |
| P2-12 | 卡 `:8`；goal §11 `:96-97` | Q-30（`suggested_owner: dsh` vs ZCode UI 主责）仍「待裁决」，卡未引用 | 卡内引用 Q-30 决议与「ZCode 可用时交接」条件 |

---

## 4. AC 逐项（可机械验收？）

| AC | 判定 | 说明 |
|---|---|---|
| AC1（`:60`） | **基本可验收（差命令）** | 字段逐项/迁移/幂等/兼容写已写；需补 Appearance.Tests 命令（P1-C）、schemaVersion/默认值细节（P2-3）、路径（P2-2） |
| AC2（`:61`） | **可验收** | 读取/校验/通知 + `FrontendId` 注入 + ThemeEngine 回归；应用落点已移 PREREQ-2（P2-8 下游待补） |
| AC3（`:62`） | **部分** | 机制已裁；但主题层键生成通道/R14 计数/主题包 schema 未写（P1-B）、96 未写（P1-D）、DS 测试命令缺（P1-C） |
| AC4（`:63`） | **可验收** | `auto/full/reduce` + `IMotionPreferenceSource` 注入 + 判据 ①–⑤ + categories 0ms |
| AC5（`:64`） | **可验收** | 基线 949/0/57 当前成立；释放时复核（P2-7） |

---

## 5. 处置建议（按序）

1. **补 AC/任务（P1）**：①增 P5 主题包任务与 AC（P1-A）；②AC3 写明主题层键的 `NmKeys` 常量来源/`Tokens.Global` 排除/主题包 schema/`R14ContractTests` 计数（P1-B）；③测试表补 `NewManga.Appearance.Tests` + `NewManga.DesignSystem.Tests` 命令（P1-C）；④AC3 增 G-1b 96 常量登记（P1-D）。
2. **P2 逐项**：优先 P2-8（PREREQ-2 承接应用落点，否则 W-6 责任空洞）、P2-10（W 表列）、P2-11（STATUS），其余随文修正。
3. 修完派 **rev-r3**；P0/P1=0 后冻结并释放实现（随后 PREREQ-2 → FEA-06）。

## 6. 边界声明

本报告只审**范围/卡/冻结契约/生成器契约/写域/可执行性**，不审 C-02/C-03 内容本身（已 FROZEN），不审未实现代码；未运行 UI/生成器（除只读检查外）。`check.ps1`/`verify_pins` 为只读参考，不替代审查。本席位未参与 FEA-06-PREREQ-1 起草或实现，未修改被审文件、未 commit/push；行号基于 `2c5658fae` 实测。
