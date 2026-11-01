---
task_id: FEA-06-PREREQ-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 2c5658fae
reviewed_head: 97677e402
decision: approved
counts: { P0: 0, P1: 0, P2: 16 }
---

# FEA-06-PREREQ-1 范围冻结复核 r3（独立上下文；本席位未参与本卡起草）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-1.md`（v3；`proposed`） |
| base_commit | `2c5658fae`（r2 被审 head） |
| reviewed_head | `97677e402`（`chore(status): 压缩 STATUS 至预算内`；上一提交 `673db5d4` 为范围 v3） |
| 上游 | `doc/reviews/FEA-06-PREREQ-1-scope-r2.md`（P0=0/P1×4/P2×12） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；本任务只读，未参与 PREREQ-1 起草；此前复核 FEA-05/FEA-06 系列均为只读评审，无实现关系；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-02 |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 16（16 条均为接受遗留/建议，不阻断冻结）** |

> **一句话结论**：**approved**。r2 的 4 条 P1 **全部实质关闭**：P5b 主题包交付物已进 AC5（`Themes/fluent-dark.nmtheme` + manifest `nm.fluent.visual/1` + 注册表 + `ThemeGen --check`），AC3 已写明 Material「有 `NmKeys` 常量但不写入 `Tokens.Global.axaml`」、主题包 schema/`ThemeLayerAllowedKeys`/`R14ContractTests` 59-65 计数同步与 G-1b 96 常量，测试命令改为四工程并覆盖两个 `--check`，AC5/AC6 编号与内容对齐。**写域无剩余必须缺口**：`Themes/**` 与 `Generated/**` 均在 `apps/desktop-avalonia/src/NewManga.ThemeEngine/**` 之下（`BuiltInThemes.cs:15`、`BuiltInThemeGenerator.cs:31-42`），无需单独条目；`tokens.json` 亦无需入写域（Focus/Corner/Elevation 走 `DerivedGlobals`，Material 走主题包，冻结源不动）。残留均为 P2 级：任务表仍缺 P5b 行、AC6 测试行落在 Closeout 之后（表外）、AC5「主题包校验」与 `--check` 语义混同、AC1–AC4 命令未给四工程路径、96 常量命名/落点、以及 r2 未处理的接口/路径/治理细则。`check.ps1` PASS、`verify_pins` 15/15、自 `24600bbee` 无代码变更（949/0/57 基线成立）。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改卡/代码/设计；`git status --porcelain` 为空；未 commit/push。本报告为本轮唯一新增文件。
- 本轮实测：`check.ps1` → **PASS（3 warnings：STATUS 3172B/43 行 80%；PLAN 3917B/58 行 80%；非终态 11）**；`verify_pins.ps1` → **PASS（all 15）**；`git log 2c5658fae..HEAD -- apps tools` 为空 → **949/0/57 基线仍成立**；`git merge-base --is-ancestor cad5ebde3 HEAD` → 0。
- diff 范围（`2c5658fae..HEAD`）：`doc/tasks/FEA-06-PREREQ-1.md`（+4/−3 行表格与 AC）、`doc/STATUS.md`（预算压缩 6 行）、本席位 r2 报告；无 `REBASELINE_PLAN`/代码变更。

---

## 1. r2 findings 逐项 disposition

| r2 ID | 判定 | 证据（v3） |
|---|---|---|
| **P1-A** 主题包无任务/AC | **CLOSED（附 P2-13/15）** | 新增 **AC5**（`:64`：`Themes/fluent-dark.nmtheme` + manifest `nm.fluent.visual/1` + 注册表条目 + `ThemeGen -- --check`）；W-8（`:82`）为归属；测试表 `:90` 增 AC5 行 ✓。**但任务表 `:51-56` 仍只有 P1–P4，无 P5b 行**（Lead 所称「新增 P5b」未落卡；见 P2-13），AC5 的「主题包校验」以 `--check`（漂移检查）表述（见 P2-15） |
| **P1-B** AC3 生成落点 | **CLOSED（附 P2-16）** | AC3（`:62`）已写明：G-1/G-1b/G-1c 经 `DerivedGlobals` + `TokenValueKind.BoxShadows` 生成；**`Nm.Material.*` 有 `NmKeys` 常量但不写入 `Tokens.Global.axaml`**（主题包承载取值）；主题包 schema/`ThemeLayerAllowedKeys`（`DesignSystemThemeManager.cs:123-130`）与 `R14ContractTests` 59/65 计数同步更新；G-1b 96 作为设计常量登记（`Nm.Size.MatrixColumnMin`）而非令牌派生 ✓（96 命名/落点细节见 P2-16） |
| **P1-C** 测试命令 | **CLOSED（附 P2-14）** | 测试表 `:88` 改为「`dotnet test` 四工程（Appearance/DesignSystem/ThemeEngine/App）」；`:89` AC3 含 `TokenGen -- --check` + `ThemeGen -- --check`；`:90` AC5 ✓。**但 `AC6` 行（`:105`）落在 `## Closeout Record` 之后（表外）**，且四工程命令未给具体项目路径（P2-14） |
| **P1-D** G-1b 96 | **CLOSED（附 P2-16）** | AC3（`:62`）增「G-1b 矩阵列宽 96 作为设计常量登记（`Nm.Size.MatrixColumnMin`）而非令牌派生」✓；名称与「非令牌派生」的矛盾/登记位置留待实现裁决（P2-16） |
| P2-1（FrontendId） | 开（P2-1） | 卡 `:54` 仍只写「`AppOptions` 暴露 `FrontendId`」，未定语义/来源/与持久化值冲突时的优先级 |
| P2-2（路径/ThemeHome） | 开（P2-2） | P1 只说 `presentation-settings.json`，未写路径解析/`--theme-home` 语义；`ThemeHome.cs` 仍不在写域 |
| P2-3（schemaVersion） | 开（P2-3） | AC1 有坏文件；未写 `schemaVersion=2`、默认值、缺字段 warning（C-03:44/57-60/70） |
| P2-4（Program.cs 重叠） | 开（P2-4） | PREREQ-1 `:31` 与 PREREQ-2 `:25` 均含 `Program.cs`，未声明「只做装载点」分工 |
| P2-5（frontendId/visualThemeId） | 开（P2-5） | 字段已列但枚举域/校验未入 AC；PREREQ-2 AC1 仍把 `builtin.fluent-dark`（visualThemeId）与 `builtin.fluent`（frontendId）并列当 selector 值（其卡未改） |
| P2-6（C-03 称谓） | 开（P2-6） | 卡 `:46`/W-2 `:76` 仍称「C-03 冻结草案」；实为 FROZEN v6（`FEA-C03...:3`，有 `FEA-CONTRACT-FROZEN-C03.md`） |
| P2-7（AC 基线） | 开（P2-7） | AC6 已含 949/0/57 基线 ✓；仍未写释放时复核/证据条目 |
| P2-8（W-6 下游） | 开（P2-8） | `FEA-06-PREREQ-2` 未改（diff 无），其任务/AC 仍无「读取 `AppearanceSettings`→应用主题/动效」；W-6 把应用落点交给它，责任需在 PREREQ-2 复核时承接 |
| P2-9（取值来源） | 开（P2-9） | Material/Elevation 取值来源（design 01 §2.2/§2.4）与主题包生成/校验测试未点名；`ThemePackageJson` 现有 `material`/`elevation` 是**枚举模式**（`:141-142`），Fluent 的 `Nm.Material.*` 值需新增 schema 字段 |
| P2-10（W-3 表格） | 开（P2-10） | W 表 4 列，`:77` W-3 行仍只有 3 个单元格（少「裁决」列） |
| P2-11（STATUS） | **部分** | `:10` 已改「下一候选：PREREQ-1（r3 复核）→ PREREQ-2 → FEA-06」✓；**`:7` 仍「上一 `FEA-04b` `in_review`（r5 approved，AC5 待确认）」**（实际 done）→ P2-11 |
| P2-12（Q-30） | 开（P2-12） | 卡 `:8` 仍 `suggested_owner: dsh` 未引用 goal §11 Q-30「待裁决」记录 |

---

## 2. 六项必核查（v3 结论）

1. **C-03 落地范围**：P1/AC1 逐字段（含 `appearance.mode/contrast/followSystemAccent`、`corners.scale`、`material.acrylicStrength/micaEnabled`、`theme.frontendId/visualThemeId`、`motion.mode/categories`、`layout.*`、`schemaVersion`）✓；原子写/迁移/幂等/旧文件只读顺序/兼容写入 AC1 ✓。残留 P2-1/2/3/5。
2. **令牌生成**：机制已裁并写入 AC3（DerivedGlobals、BoxShadows、Material 主题层、`NmKeys` 有常量而 `Tokens.Global` 不写、主题包 schema/`ThemeLayerAllowedKeys`/R14 计数、96 常量）✓；`tokens.json` 不需要改（`DerivedGlobals` 不读新增键；Material 值进主题包）✓。残留 P2-9/16（取值来源、96 命名/落点、schema 字段细节）。
3. **写域审计**：无必须缺口。`Themes/**`、`Generated/ThemeTokenBaseline.g.cs`、`BuiltInThemes.cs`、`ThemeGen` 均在 `NewManga.ThemeEngine/**` 内（`BuiltInThemes.cs:15`；`BuiltInThemeGenerator.cs:31-42`）→ **无需为 `Themes/**` 单独加 allowed_paths**；`NewManga.sln`/`App.csproj`/`NewManga.Appearance/**`/`DesignSystem/**`/DS 测试/Appearance 测试/ThemeEngine 测试/App 测试均在 ✓；新测试工程可加入 sln（无需 `Directory.Packages.props`，仓库无该文件；`Directory.Build.props` 自动继承）。
4. **AC 可验收**：AC1（Appearance 项目/字段/迁移/测试）可验收（命令精度 P2-14）；AC2（读取/校验/通知 + `FrontendId` 注入 + ThemeEngine 回归）可验收（应用落点归 PREREQ-2，下游见 P2-8）；AC3（生成/主题层/96/计数）可验收（细节 P2-9/16）；AC4（auto/full/reduce + IMotionPreferenceSource + ①–⑤）可验收；AC5（主题包落盘/manifest/注册表 + `--check`）基本可验收（校验口径 P2-15）；AC6（全量不退化）可验收（测试行位置 P2-14）。
5. **依赖与顺序**：`depends_on: FEA-04b`（done）✓；PREREQ-2 `depends_on: PREREQ-1` ✓（下游待补 P2-8）；FEA-06 依赖两前置 ✓（`FEA-06.md:11-15`）；`frontendId`/`visualThemeId` 枚举域需在 P1 定义时锁定（P2-5）。
6. **治理**：`check.ps1` PASS（3 warnings）、`verify_pins` 15/15 ✓；PLAN `:20-22/:37` 与 LEDGER `:45-47` 已同步 PREREQ 链 ✓；STATUS `:10` 已修、`:7` 前句仍 stale（P2-11）；Q-29/Q-30 仍「待裁决」（goal §11），本轮按 Q-29 推荐先审 PREREQ-1 与推荐顺序一致 ✓。

---

## 3. AC 逐项（可机械验收？）

| AC | 判定 | 说明 |
|---|---|---|
| AC1（`:60`） | **可验收** | 字段/迁移/幂等/兼容写入 AC；命令需具体化四工程路径（P2-14） |
| AC2（`:61`） | **可验收** | 读取/校验/通知 + `FrontendId` 注入 + ThemeEngine 回归；应用落点 PREREQ-2（P2-8） |
| AC3（`:62`） | **可验收** | 生成机制/主题层/96/R14 计数写入；取值来源与 96 落点细化（P2-9/16） |
| AC4（`:63`） | **可验收** | `auto/full/reduce` + 注入 + 判据①–⑤ |
| AC5（`:64`） | **可验收** | 包/manifest/注册表 + `--check`；校验口径细化（P2-15） |
| AC6（`:65`） | **可验收** | 949/0/57 当前成立；释放时复核（P2-7） |

---

## 4. Findings（16 条 P2，均不阻断）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | 卡 `:54`；C-03 `:36` | `AppOptions.FrontendId` 语义/来源未定义（C-03 只规定持久化 `theme.frontendId`；CLI 注入为新增面，与持久化值冲突时优先级未写） | 明确「仅测试/诊断覆盖；不替代持久化值」或删除 |
| P2-2 | 卡 `:53`；`ThemeHome.cs:6-14,34-38` | `presentation-settings.json` 路径/根（是否沿用 `--theme-home`）、`ThemeHome` 是否需改未写；`ThemeHome.cs` 不在写域 | AC1 写路径解析规则；如需改则补写域或由 Appearance 自带解析 |
| P2-3 | 卡 `:60`；C-03 `:44,57-60,70` | `schemaVersion=2` 具体值、默认值（`auto`/`full`）、缺字段回退 warning 未入 AC | AC1 列明 |
| P2-4 | `PREREQ-1:31` vs `PREREQ-2:25` | 两卡都含 `Program.cs`；未声明「只做装载点，selector 分支归 PREREQ-2」 | 卡内写明分工，避免返工 |
| P2-5 | 卡 `:53`/`:60`；`PREREQ-2:54`；C-03 `:73` | `frontendId`/`visualThemeId` 枚举域/校验未入 AC；PREREQ-2 AC1 仍把两维度混用 | AC1 增枚举域校验断言；PREREQ-2 按 `frontendId` 决策 |
| P2-6 | 卡 `:46`、W-2 `:76` | 仍称「C-03 冻结草案」；实为 FROZEN v6（2026-11-01，`FEA-CONTRACT-FROZEN-C03.md`） | 引用冻结记录/版本 |
| P2-7 | 卡 `:65`（AC6） | 949/0/57 基线当前成立（自 `24600bbee` 无 code 变更），未写释放时复核；Canonical Evidence 仍空 | 释放时复跑并填证据 |
| P2-8 | `FEA-06-PREREQ-2` 任务/AC（`:43-57`） | **W-6 下游未记录**：PREREQ-2 未改，其任务/AC 无「读取 `AppearanceSettings`→应用主题/动效」；W-6 责任需其承接 | PREREQ-2 复核/修订补 P/AC 与 `AppearanceSettings` 读取依赖 |
| P2-9 | 卡 `:55`/`:62`/`:64`；`design/01:41-47`；`ThemePackageJson.cs:141-142,191` | Material/Elevation 取值来源未点名；主题包现有 `material`/`elevation` 是**枚举模式**，`Nm.Material.*`（Brush/double/bool）与 `Nm.Elevation.*`（BoxShadows）需新增 schema 字段/校验；AC5 的「主题包校验」未点名 `ThemeValidator`/`BuiltInThemes` 测试 | AC3/AC5 写明值来源（design 01）、schema 字段、`ThemeValidator`/包加载/Current 不生效断言 |
| P2-10 | 卡 `:77`（W-3） | W 表 4 列，W-3 行只有 3 个单元格（少「裁决」列），渲染错位 | 补「裁决」列 |
| P2-11 | `doc/STATUS.md:7` | r2 P2-11 残留：`:7` 仍「上一 `FEA-04b` `in_review`（r5 approved，AC5 待确认）」（实际 done）；`:10` 已修 ✓ | 同步上一 Task 状态 |
| P2-12 | 卡 `:8`；goal §11 `:96-97` | Q-30（`suggested_owner: dsh` vs ZCode UI 主责）仍「待裁决」，卡未引用 | 卡内引用 Q-30 决议与「ZCode 可用时交接」 |
| P2-13 | 卡 `:51-56`（任务表）、`:64`（AC5）、`:82`（W-8） | **任务表缺 P5b 行**：W-8/AC5 已定义主题包交付，但 P1–P4 任务拆解无对应项（Lead 所称「新增 P5b」未落卡） | 任务表增 P5b（包/manifest/注册表/schema/校验）并与 AC5 对应 |
| P2-14 | 卡 `:88`（AC1–AC4 行）、`:105`（AC6 行） | ①AC6 测试行落在 `## Closeout Record` 之后（Markdown 表外）；②AC1–AC4 只写「`dotnet test` 四工程（…）」未给项目路径/命令，证据不可直接复制执行 | 把 AC6 行移回测试表；四工程写成完整 `dotnet test <path>` 命令 |
| P2-15 | 卡 `:64`（AC5）、`:90`（测试行） | AC5 把「主题包校验通过」等同于 `ThemeGen -- --check`——`--check` 是**生成产物漂移检查**（`BuiltInThemeGenerator.IsUpToDate`，`ThemeGen/Program.cs:74-83`），不等价于包 schema/`ThemeValidator`/加载校验（现有 `BuiltInThemeGeneratorTests.cs:55/65/73` 才是校验类断言） | AC5 增「`ThemeValidator.Validate`/`BuiltInThemes` 加载/注册表条目/Current 下不生效」测试点；`--check` 仅作漂移证据 |
| P2-16 | 卡 `:62`（AC3） | 96 常量「登记为 `Nm.Size.MatrixColumnMin`（非令牌派生）」名称像资源键但声明非令牌派生，登记位置（代码常量表/DS 常量类）与 FEA-06 消费方式未定；G-1b 原设计称「FEA-05 生成令牌时登记」 | 定义为常量类（如 `LayoutConstants.MatrixColumnMin=96`，注释引 `06:37`）或明确登记处；同步改 AC3 表述避免与令牌键混淆 |

---

## 5. 处置建议

1. **范围可冻结**（P0/P1=0）：DSH 可批准 v3 并置 `ready` 释放实现。
2. 建议实现前顺手修 P2-13（补 P5b 行）、P2-14（AC6 行归位 + 四工程命令具体化）、P2-15（AC5 校验口径）——这三条直接影响实现/证据的可操作性；其余 P2 可在实现/收口期处置。
3. **PREREQ-2 复核时必须覆盖 P2-8**（W-6 应用落点）与 P2-5（selector 按 `frontendId`，勿混 `visualThemeId`）。

## 6. 边界声明

本报告只审**范围/卡/冻结契约/生成器契约/写域/可执行性**，不审 C-02/C-03 内容本身（已 FROZEN），不审未实现代码；未运行 UI/生成器（除只读检查外）。`check.ps1`/`verify_pins` 为只读参考，不替代审查。本席位未参与 FEA-06-PREREQ-1 起草或实现，未修改被审文件、未 commit/push；行号基于 `97677e402` 实测。
