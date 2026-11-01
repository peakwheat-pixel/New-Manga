---
task_id: FEA-06-PREREQ-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-implementer
base_commit: 97677e402
reviewed_head: b547e229e
decision: changes_requested
counts: { P0: 0, P1: 10, P2: 16 }
---

# FEA-06-PREREQ-1 实现复核 r1（独立上下文；本席位未参与实现）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-1.md`（范围 r3 approved `97677e402`；`status: ready`） |
| base_commit | `97677e402`（范围 r3 head） |
| reviewed_head | `b547e229e`（`feat(fea-06-prereq-1): AC5 …全部 AC 完成，全量 974/0/57`） |
| 实现者 | DSH（Codex 通道故障、ZCode 未安装，记录在 `verification/FEA-06-PREREQ-1/delivery-notes.md:3`） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；未参与 PREREQ-1 实现或返修；此前只读评审本卡范围 r1–r3 与 FEA-05/FEA-06 系列；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-02 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 10 / P2 = 16（共 26）** |

> **一句话结论**：**changes_requested**。AC6 与生成管线自洽性实测通过（独立全量 sln **974 passed / 0 failed / 57 skipped**；`TokenGen --check`、`ThemeGen --check` EXIT 0；`check.ps1` PASS、`verify_pins` 15/15），AC3 的 11 个新键确实经 `TokenMap.DerivedGlobals` + TokenGen 重生成（非手改产物）。但**实现与已冻结 C-03/设计基线/范围 r3 存在多处契约级偏差**：`motion.categories` 的 JSON/C# 词表是 `feedback/transition/emphasis` 而 C-03 §2.3 冻结的是 `navigation/feedback/decorative`；`layout.*` 词表/默认值是 `expanded/split/fit`（`expanded`/`fit` 在既有枚举中不存在）而非 `top-band/stacked/fit-page`；旧 `ReducedMotion=true` 迁移未置「三类全禁」（测试名却写 WithAllCategoriesOff 无断言）；旧 `theme-settings.json` 从未读取、`ThemeSettingsStore` 兼容写未实现；`AppOptions.FrontendId` 不存在且 Coordinator 未接入启动；`Nm.Material.Acrylic.Base/Tint` 完全缺失、`Acrylic.Opacity=0.8`（设计 0.85）、`Nm.Elevation.1/2/3` 值与设计 01:52-54 不符、G-1b 96 常量缺失、`ThemeLayerAllowedKeys`/`R14ContractTests` 未按范围 AC3 更新；AC4 判据⑤迁移测试缺失；AC5 的 `fluent-dark.nmtheme` 是**默认主题复制改 descriptor**、无 `nm.fluent.visual/1` manifest、无 Fluent 材质值、未被 ThemeGen 覆盖（`ThemeGen --check` 只校验 default），证据被高估；此外 `App/Services/MotionResolver.cs`/`WindowsMotionPreferenceSource.cs` 不在 `allowed_paths`（`Appearance*.cs` 之外）。需修复后 rev-r2。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改源码/卡/设计；`git status --porcelain` 为空；未 commit/push；本报告为本轮唯一新增文件（仅报告）。
- 独立实测（非引用交付日志）：
  - `dotnet test apps/desktop-avalonia/NewManga.sln` → **EXIT 0**；各测试项目汇总：Appearance 12、Host 51/28 skip、ThemeEngine 237、DesignSystem 85、ApplicationCore 31、CoreClient 128/22 skip、App 430/7 skip → **974 passed / 0 failed / 57 skipped**（与 AC6 声明一致）。
  - `TokenGen -- --check` → **EXIT 0**（`rows: 289`，up to date）。
  - `ThemeGen -- --check` → **EXIT 0**（输出仅 `theme: newmanga-default 1.0.0`，**未包含 fluent-dark**）。
  - `pwsh tools/governance/check.ps1` → **PASS（3 warnings：11 非终态；STATUS 3173B/44 行、PLAN 3951B/59 行 80%）**；`verify_pins.ps1` → **PASS（all 15）**。
- 阅读：任务卡（范围 r3）、C-03 v6 §2.1–2.3、设计 01/02/03、全部新增/修改源码与测试、ThemeEngine 主题包与注册表、`verification/FEA-06-PREREQ-1/**`、`delivery-notes.md`、STATUS/PLAN/LEDGER、goal checkpoint diff。

---

## 1. AC1–AC6 逐项

| AC | 判定 | 核查结果 |
|---|---|---|
| **AC1**（Appearance 项目/字段/原子写/迁移/测试） | **P1（部分实现）** | 项目、`AppearanceSettings`、`AppearanceJson`、`AppearanceStore`、`IMotionPreferenceSource`、12 测试均存在；字段大多齐全，原子写有 temp+move，坏 JSON 回退默认。但：①`motion.categories` 词表错误（`transition/emphasis`）；②`layout.*` 词表/默认值错误（`expanded/split/fit`）；③旧迁移不完整（true 未置三禁、旧 `theme-settings.json` 未读、`ThemeSettingsStore` 兼容写未做、`followSystemAccent`/`themeId→frontendId` 未迁移）；④`LegacyDocument` 语义是「同一新文件的首次内容」，不是旧文档；⑤测试名 `Legacy_ReducedMotion_True_MigratesToReduce_WithAllCategoriesOff` 并未断言 categories off（`AppearanceJsonTests.cs:54-60`）；⑥无布局/模式的枚举词表校验。 |
| **AC2**（Coordinator 读取/校验/通知、FrontendId、ThemeEngine 回归） | **P1（部分实现）** | `App/Services/AppearanceCoordinator.cs` 实现读取/校验/Changed 事件，4 测试通过；`Reload_DoesNotTouchResources_LeavingApplicationToTheShell` 证明不碰资源。但 **`AppOptions.FrontendId` 不存在**（`AppOptions.cs` 无任何 frontend 相关代码，`git diff` 无 AppOptions 改动）；Coordinator/Store 未接入 `Program.cs`/启动路径（`git grep` 仅测试引用），AC2「可注入 + 装载」未完成。 |
| **AC3**（11 键生成/BoxShadows/主题层/96/R14 计数） | **P1（多项不符）** | 11 键确经 `TokenMap.DerivedGlobals`（`TokenMap.cs:206+`）+ `TokenValueKind.BoxShadows`（`TokenValues.cs`）+ Writer 分支，`TokenGen --check` up to date，`NmKeys.g.cs`/`Tokens.Global.axaml` 为生成产物（非手改）✓。但：①**Material.Base/Tint 完全缺失**（`NmKeys`/`Tokens.Global`/主题包均无），只实现了 `.Opacity`/`Mica.Enabled` 2 键；②`Nm.Material.Acrylic.Opacity` 生成值 **0.8**，设计 01:43 为 **0.85**；③`Nm.Elevation.1/2/3` 生成值 `0 1 3 #24000000` / `0 4 12 #33000000` / `0 8 24 #40000000`，与设计 01:52-54 的 `0 1 2 0 #26000000` / `0 4 8 0 #33000000` / `0 8 16 0 #40000000` **不符**（blur/spread/颜色均偏）；④**G-1b 96 常量完全缺失**（全仓无 `MatrixColumnMin` 实现；仅评审/设计文档提及）；⑤范围 r3 AC3 要求的 `ThemeLayerAllowedKeys`/`R14ContractTests` 59/65 计数与主题包 schema 更新**未发生**（`git diff` 无 `Theming/**`、无 `NewManga.DesignSystem.Tests/**` 变更）；⑥Material Base/Tint 声称由主题包承载，但主题包 schema 仅有 `material`/`elevation` **枚举模式**，无 Acrylic 值。 |
| **AC4**（auto/full/reduce + IMotionPreferenceSource + 判据①–⑤） | **P1（部分实现）** | `WindowsMotionPreferenceSource`（SPI_GETCLIENTAREAANIMATION）+ `MotionResolver` + 7 测试存在；auto 平台读取、null/throw 降级 full、full 不读平台、reduce 全禁/`Enabled=false`、categories=off 均有测试。但设计 02 §3 **判据⑤（旧 ReducedMotion=true 迁移后三类全禁）没有对应测试**，且迁移实现并未生成 categories None（AC1）；**判据④（navigation 在 reduce 下 0ms）没有 navigation 专属测试**（类别又被命名为 Transition）；测试注释把 ①–⑤ 映射到别的要求（`MotionResolver.cs:13-15` 把 ① 写成「reduce 全时长 0」、②写成「禁用 emphasis」、③写成「feedback 保留颜色」），与设计 02:57-61 不对应。`reduce` 下 feedback 标志保留但 `Enabled=false` 与 `IsEnabled(Feedback)=false` 的消费语义未在代码/测试中定义（仅 Auto 用例断言 Feedback 为 true）。 |
| **AC5**（`builtin.fluent-dark` 主题包/manifest/注册表/校验） | **P1（不达标）** | 包可加载、注册表含两 builtin、默认主题不变测试通过。但：①`Themes/fluent-dark.nmtheme` 与 `newmanga-default.nmtheme` 相比**仅 descriptor 4 行不同**（id/name/description/supportsLight），light/dark 调色板、material/elevation 全部沿用 default（`"material":"solid"`、`"elevation":"none"`）；②无 C-02 V-07 要求的 **`nm.fluent.visual/1` manifest**（`schema` 仍 `newmanga.theme/1`）；③无 Fluent Material/Acrylic 值；④文件是**手工复制改 descriptor**，不在 `BuiltInThemeGenerator.GeneratedFilePaths`，不被 `ThemeGen --check` 覆盖（我独立运行 `ThemeGen --check` 只输出 newmanga-default）；⑤`BuiltInThemeGeneratorTests` 新增两测只验加载/注册，未做 `ThemeValidator` 校验、未验 Fluent 设计值、未验 Current 下不生效（仅验 default id 不变）；`BuiltInThemes.LoadFromResource`（`BuiltInThemes.cs:58-85`）只做反序列化，不跑 `ThemeValidator`。 |
| **AC6**（全量 sln 不退化，974/0/57） | **通过** | 独立运行：**974 passed / 0 failed / 57 skipped**，EXIT 0；`build.log` 0 警告/0 错误；两个生成器 `--check` EXIT 0。 |

---

## 2. P1（10 条，必须修）

| ID | 位置 | 问题 | 证据/影响 |
|---|---|---|---|
| **P1-1** | `AppearanceSettings.cs:77-85`；`AppearanceJson.cs:119-122,213-219`；`MotionResolver.cs:20-48`；C-03 `:50-55`；设计 02 `:24-51` | **`motion.categories` 词表错误**：C-03/设计冻结为 **`navigation`/`feedback`/`decorative`**，实现为 `feedback`/`transition`/`emphasis`；JSON writer 写 `transition`/`emphasis`，reader 对 `navigation`/`decorative` 视为未知（`ReadMotionCategories` `:213-219`）。 | AC1/AC4 与 C-03 §2.3 直接冲突；FEA-06 按设计 02 消费 `navigation`/`decorative` 将读不到该设置；MotionResolver 的 Transition/Emphasis 语义与设计类别错位。 |
| **P1-2** | `AppearanceSettings.cs:96-111`；`AppearanceJson.cs:286-311`；`LayoutProfile`（`ThemeModels.cs:330-345`）；`JsonSupport.cs:93-121`；C-03 `:39` | **`layout.*` 词表/默认值错误**：`navigation` 默认 `"expanded"`、`reader` 默认 `"fit"`——既有枚举 JSON 为 `"top-band"`/`"fit-page"`；`workbench` 默认 `"split"`，而 `LayoutProfile.Default` 是 `"stacked"`；C-03 §2.2 要求旧 `LayoutProfile` 六字段「同名保留」。 | 旧 `theme-settings.json` 的 layout 值会与本模型互不兼容；FEA-06/PREREQ-2 若按 `LayoutProfile`/`JsonSupport` 名称消费将出现无效值；迁移「同名保留」不成立。 |
| **P1-3** | `AppearanceJson.cs:151-175,177-227`；`AppearanceStore.cs:24-41`；`AppearanceJsonTests.cs:54-60`；C-03 `:39-41,56-60`；`AppearanceStore`/ThemeEngine 无 `theme-settings.json` 引用 | **旧文档迁移不完整/兼容写缺失**：①旧 `theme-settings.json` 从未被读取（`git grep "theme-settings"` 仅命中 `ThemeHome.cs`）；②旧 `ReducedMotion=true` 只映射 `MotionMode.Reduce`，**未将 categories 置 None**（`ReadMotionCategories` 默认 All；测试名 `WithAllCategoriesOff` 无断言）；③`FollowSystemAccent` 只读新键 `appearance.followSystemAccent`，无旧键回退；④旧 `themeId=builtin.fluent-dark` 未同步设置 `theme.frontendId=builtin.fluent`（C-02 V-07 两 id 映射）；⑤`LegacyDocument` 保存的是**新文件首次内容**而非旧文档；⑥ThemeEngine `ThemeSettingsStore.SaveAsync` 一个 release 兼容写未实现（ThemeEngine 无改动）。 | AC1「旧文档读一次/兼容写/等价迁移」不成立；用户从旧版本升级时 `ReducedMotion` 的「三类全禁」与 `FollowSystemAccent`/frontendId 会丢失或错配。 |
| **P1-4** | `AppOptions.cs`（无 FrontendId）；`AppearanceCoordinator.cs`；`Program.cs`/启动；AC2 | **AC2 未完成**：`AppOptions` 没有 `FrontendId` 属性/解析；Coordinator 与 Store 未接入 `Program.cs`/启动组合根（`git grep AppearanceCoordinator` 仅该文件与测试）。 | AC2 的「`AppOptions.FrontendId` 可注入」不存在；Coordinator 只是可单测的孤立类型，无法产出 AC2 所要求的启动读取/通知行为；PREREQ-2 依赖的注入面未建立。 |
| **P1-5** | `TokenMap.cs:206-208`；`Generated/NmKeys.g.cs`；`Generated/Tokens.Global.axaml`；`fluent-dark.nmtheme`；设计 01 `:41-43,65`；C-02 V-03 | **Material 键不完整/值错误**：只生成 `Nm.Material.Mica.Enabled` 与 `Nm.Material.Acrylic.Opacity`；**`Nm.Material.Acrylic.Base/Tint` 在代码/生成物/主题包中均不存在**；`Acrylic.Opacity` 生成 `0.8`，设计 01:43 为 `0.85`。注释声称 Base/Tint 由主题包承载，但主题包只有 `"material":"solid"` 枚举，无 Base/Tint 值；`NmKeys` 也无对应常量。 | G-1 的 4 个 Material 键只落地 2 个且值偏差；FEA-06 无法 `{DynamicResource Nm.Material.Acrylic.Base/Tint}`，C-02 V-03/V-05 的 Fluent 材质表达式缺资源，AC3「Material 主题层」实际未实现。 |
| **P1-6** | `TokenMap.cs`（Elevation 派生值）；`Generated/Tokens.Global.axaml`；设计 01 `:52-54` | **Elevation 值与设计基线不符**：生成 `0 1 3 #24000000` / `0 4 12 #33000000` / `0 8 24 #40000000`；设计冻结 `0 1 2 0 #26000000` / `0 4 8 0 #33000000` / `0 8 16 0 #40000000`（blur、spread、颜色 alpha/RGB 均不同；生成 XAML 还丢了 spread 分量）。 | AC3「取值与设计 01 一致」不成立；Fluent 卡片/弹层/对话框阴影视觉将偏离基线；`TokenGen --check` 只证明生成器自洽，不证明取值正确。 |
| **P1-7** | AC3；设计 01 `:22`、`06:37`、FEA-04b selfcheck `:44` | **G-1b `96` 常量完全缺失**：全仓 `MatrixColumnMin` 无实现（仅评审/设计文档提及）；范围 r3 AC3 明确要求「96 作为设计常量登记（`Nm.Size.MatrixColumnMin`）而非令牌派生」。 | AC3 的 G-1b 不可验收；FEA-06 批量矩阵列宽无注册常量，C-02 V-05 判据将无令牌/常量可引。 |
| **P1-8** | `tests/NewManga.App.Tests/MotionResolverTests.cs`（无 ⑤）；`AppearanceJsonTests.cs:54-60`；`MotionResolver.cs:13-15`；设计 02 `:53-61` | **AC4 判据⑤缺失、①–④映射错误**：设计 02 §3 ⑤要求「旧 ReducedMotion=true 迁移→motion.mode=reduce + 三类关（feedback 颜色过渡 0ms）」的迁移测试；实现无此测试，迁移也未置三类关。测试注释把 ①–⑤ 写成「reduce 全时长 0 / 禁用 emphasis / feedback 保留颜色 / …」，与设计 02 的 ①decorative 0、②full 不跟随系统、③auto 假源、④navigation reduce 0ms 不对应；④无 navigation 专属测试。 | AC4「判据①–⑤有测试」不成立；FEA-06 依据错误映射实现动效降级会与设计 02 不一致（尤其 ⑤ 与 feedback 色过渡 0ms）。 |
| **P1-9** | `Themes/fluent-dark.nmtheme`（全文）；`BuiltInThemeGenerator.cs:31-42`；`BuiltInThemes.cs:58-85`；`BuiltInThemeGeneratorTests.cs` 新增两测；`themegen-check.log`；C-02 V-07；范围 r3 AC5 | **AC5 主题包是手工复制的 default，不是 Fluent 主题**：与 default 仅 descriptor 4 行差异；无 `nm.fluent.visual/1` manifest、无 Fluent 材质/阴影值；不在 `BuiltInThemeGenerator.GeneratedFilePaths`，`ThemeGen --check` 只覆盖 default（独立运行确认），却在 AC5 宣称「`ThemeGen --check`」证据；`BuiltInThemes` 注释称「build time generated / never validated」，实际文件非生成且无 `ThemeValidator` 校验；测试只验加载/注册，未验 `nm.fluent.visual/1`、Fluent 值、Current 不生效。 | AC5 的主题包语义/来源/校验均不满足范围 r3 AC5 与 C-02 V-07；手改生成物违反 W-5 纪律；`ThemeGen --check` 证据被高估（不能证明 fluent 包可重现/正确）。 |
| **P1-10** | `apps/desktop-avalonia/src/NewManga.App/Services/MotionResolver.cs`；`WindowsMotionPreferenceSource.cs`；卡 `allowed_paths:29` | **写域外改动**：本卡 `allowed_paths` 只有 `App/Services/Appearance*.cs`，AC4 的两个文件 `MotionResolver.cs`/`WindowsMotionPreferenceSource.cs` 不在允许范围；卡片未被更新补入（diff 无 `allowed_paths` 变更）。`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` 同样在写域外（见 P2-14）。 | 实现超出范围冻结写域；应由 DSH 追认并补 `allowed_paths`（或回退/迁移文件到允许路径），否则范围控制失效。 |

---

## 3. 写域/证据审计

| 项 | 结果 |
|---|---|
| 新项目/测试/sln/App.csproj/DesignSystem/ThemeEngine/verification/STATUS/PLAN/LEDGER/doc/tasks | 均在 `allowed_paths` 内 ✓ |
| `App/Services/MotionResolver.cs`、`WindowsMotionPreferenceSource.cs` | **在写域外**（allowed 仅 `Appearance*.cs`）→ P1-10 |
| `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` | **在写域外** → P2-14（DSH 集成记录，非实现代码） |
| 生成产物真实性 | `NmKeys.g.cs`/`Tokens.Global.axaml`/`TokenMap.md` 经 TokenGen 重生成，`--check` EXIT 0（非手改）✓；`Themes/fluent-dark.nmtheme` 为手改 default（P1-9） |
| 交付证据 | `appearance-tests.log` 12、`appearance-coordinator-tests.log` 4、`motion-tests.log` 7、`theme-tests.log` 17、`sln-test.log` 汇总 974/0/57、`build.log` 0 警告/0 错误；我独立复跑结果一致 ✓；但 `themegen-check.log` 只覆盖 default，不能支撑 AC5「fluent-dark 校验」（P1-9） |
| Canonical Evidence / 卡状态 | 卡仍 `status: ready`、`approval: scope_review_r3_approved_2026-11-02`、Canonical Evidence 表空；实现完成后未进入交付/复核状态（P2-13） |

---

## 4. P2（16 条，建议/接受遗留）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `ThemeRegistryTests` 期望改动；`ThemeRegistry.cs:40` | 两 builtin 按 id ordinal 排序后 `ids[0]` 从 `newmanga-default` 变为 `builtin.fluent-dark`；测试只断言 `ids.Skip(1)`，未断言 `ids[0]`，也未核查是否还有消费者依赖「第一个是默认主题」。 | 保留默认主题优先（sort key: builtin 中 default 优先）或显式断言 `ids[0]`/按 id 查找；记录行为变化。 |
| P2-2 | `fluent-dark.nmtheme`；`BuiltInThemes.cs:6-9` | 包仍保留 `light` token 块但 `supportsLight=false`（死数据）；注释称 built-in「build time generated / never validated」，与实际手改文件不符。 | 删除/生成 light 块；改注释或改生成路径（P1-9 修复后自然消失）。 |
| P2-3 | `TokenMap.cs` Focus.Ring.Color；设计 03 `:53` | `Nm.Focus.Ring.Color` 取值 `rgba(217,160,75,0.45)` 是实现推导（accent.primary），设计 01/03 只给键名未给值，缺设计依据引用/冻结值核对。 | 在 derivation 中引用 accent 令牌来源并加测试，或由 DSH 裁决值。 |
| P2-4 | `TokenValues.cs` `ParseBoxShadows`；`TokenDictionaryWriter` BoxShadows 分支；生成 `Tokens.Global.axaml` | 生成 XAML 输出 `0 1 3 #24000000`（丢 spread、颜色通道/格式与输入 `#00000024` 不一致），`FormatBoxShadows` 依赖 `BoxShadows.ToString()`；无 DS 单测覆盖 parse/format 往返与非法输入。 | 显式格式化 `x y blur spread #AARRGGBB`；加 DS 单测（含非法输入/多阴影）。 |
| P2-5 | `AppearanceJson.cs:112-138`、reader 各分支 | 规范 JSON 混用扁平 dotted key（`theme.frontendId`）与嵌套对象（`material`/`motion.categories`）；C-03 未定义实际 JSON 形状，reader/writer 自身一致但外部消费者/迁移核对困难。 | 统一形状（建议全部嵌套或全部 dotted）并在 C-03/验证文档记录。 |
| P2-6 | `AppearanceJson.cs:181-227,59-64` | `ReadMotionCategories` 未知键警告只在累积 categories 仍为 None 时触发（`{"feedback":true,"bogus":true}` 不警告）；`schemaVersion > 2` 无处理（未来版本会被当 2 读取）；无 layout 词表校验（`ReadLayout` 接受任意字符串）。 | 逐键报告未知项；schemaVersion 高于 2 时按「未来版本」回退并警告；layout 值按枚举词表校验。 |
| P2-7 | `AppearanceStore.cs:28-41` | `File.ReadAllText` 的 IO/权限异常未捕获，`Read()` 可能抛出并阻断启动（C-03 要求读失败不阻断）；仅 JSON 异常被容错。 | catch IOException/UnauthorizedAccessException 并返回默认+警告；加测试。 |
| P2-8 | `AppearanceStore.cs:44-58`；`AppearanceJsonTests.cs:140-154` | 原子写用 `File.Move(temp, target, overwrite:true)`，无 fsync/File.Replace；测试只断言 `.tmp` 不存在，未验证崩溃/中断语义。 | 使用 `File.Replace`（或说明 NTFS MoveFileEx 语义）；测试模拟写入中断/旧文件保留。 |
| P2-9 | `AppearanceCoordinator.cs`；`AppearanceCoordinatorTests.cs:75-86` | Coordinator 无保存 API（C-03 写者名 `AppearanceCoordinator` 在 Appearance 项目，实际写者是 `AppearanceStore`，App 侧同名类只读）；测试 `Reload_DoesNotTouchResources` 未断言任何资源副作用（仅断言 settings）。 | 明确写者/读取者命名；补「不碰资源」的可验证断言；考虑把 `Save` 放入 Appearance 侧。 |
| P2-10 | `AppearanceStore.cs:9`、`AppearanceJson.cs:15`、`MotionResolver.cs:13-15` | 注释引用不存在的 `C-03 §2.5`（C-03 只有 §2.1–2.3、§3–§7）；`MotionResolver` 的判据①–⑤映射错误（见 P1-8）。 | 修正文档引用/判据编号。 |
| P2-11 | `WindowsMotionPreferenceSource.cs:18-52` | `SystemParametersInfo` 以 `[Out] bool[]` 传 `BOOL*`，未校验 `SetLastError`，仅捕获 Dll/EntryPoint 异常（其他 marshalling 异常可能逃逸）；无平台源单测（可只测非 Windows 返回 null）。 | 改用 `out int`/`ref int` 并检查返回；覆盖非 Windows/失败路径。 |
| P2-12 | `NewManga.Appearance.csproj` | 引用了 `NewManga.ThemeEngine`，但 Appearance 源码未使用其任何类型（自有 `LayoutSettings`/枚举），该引用会形成不必要的依赖方向。 | 删除引用，或改为复用 `LayoutProfile`（与 P1-2 一并处理）。 |
| P2-13 | 卡 frontmatter/Canonical Evidence；`delivery-notes.md` | 实现完成后卡仍 `status: ready`、`approval` 为非枚举自由文本、Canonical Evidence 空；交付说明按阶段性记录「AC3 完成/全量 974」等，但 AC 完成语句与实际缺陷（P1-1…P1-9）不一致。 | 按生命周期置 `delivered`/`in_review`，填 Canonical Evidence（含生成器与全量测试日志）；交付说明改为如实标注未达标项。 |
| P2-14 | `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` | 写域外改动（goal checkpoint 不在本卡 `allowed_paths`）；内容为 AC 完成记录，属 DSH 集成记录。 | 由 DSH 在集成时统一更新，或在卡内补充允许路径并说明。 |
| P2-15 | `AppearanceSettings.cs:40,120`；设计 01 `:43` | `MaterialAcrylicStrength` 默认 `0.5`，设计 `Nm.Material.Acrylic.Opacity` 为 `0.85`；C-03 未明确该字段默认值，实现值与设计材质不一致。 | 默认值取 0.85（或明确 acrylicStrength 与 opacity 的映射/差异）；写入 AC1 测试。 |
| P2-16 | `AppearanceJsonTests.cs:54-60`；`MotionResolverTests` | 迁移测试名 `...WithAllCategoriesOff` 无对应断言（P1-3 已列）；`Reduce` 测试未验证「feedback 标志保留 + Enabled=false」的消费语义（Lead 指定重点）；测试命名/断言与 AC 叙事不一致。 | 补 `Assert.Equal(MotionCategories.None, ...)`；补 feedback 标志/Enabled 组合断言并注明 FEA-06 消费契约。 |

---

## 5. 结论与修复建议

1. **修复 P1-1/P1-2/P1-3**：按 C-03 §2.2/§2.3 冻结词表重写 `motion.categories`（`navigation/feedback/decorative`）与 `layout.*`（`top-band/sidebar/dock`、`grid/list/masonry`、`comfortable/compact/spacious`、`stacked/split`、`fit-page/fit-width`/既有枚举），并复用/对齐 `ThemeEngine.LayoutProfile`；补旧 `theme-settings.json` 读取、true→reduce+三禁、`FollowSystemAccent`/`themeId→frontendId` 迁移、`ThemeSettingsStore` 一个 release 兼容写、`LegacyDocument` 语义与测试断言。
2. **补 AC2**：`AppOptions.FrontendId`（解析/校验/默认 fail-safe）并接入启动读取/通知路径（Application 应用落点仍归 PREREQ-2）。
3. **修 AC3**：Material.Base/Tint 真正落地（全局或主题包 schema，二者择一并写清）、Opacity=0.85、Elevation 值按设计 01:52-54、补 G-1b 96 常量、按范围 r3 更新 `ThemeLayerAllowedKeys`/`R14ContractTests` 59/65 与相应测试；DS 测试覆盖 `NmKeys` 键集/取值与 BoxShadows 往返。
4. **修 AC4**：补判据⑤迁移测试（三类全禁、feedback 色过渡 0ms）与④ navigation 专属测试，修正判据注释/类别命名。
5. **修 AC5**：`builtin.fluent-dark` 必须由 ThemeGen 生成（纳入 `GeneratedFilePaths`/`--check`），补 `nm.fluent.visual/1` manifest、Fluent Material/Elevation 取值、`ThemeValidator`/Current 不生效测试；`ThemeGen --check` 证据覆盖 fluent 包。
6. **写域/证据**：将 `MotionResolver.cs`/`WindowsMotionPreferenceSource.cs` 补入 `allowed_paths`（或调整文件归位）；移除/说明 goal checkpoint 写域外改动；更新卡状态与 Canonical Evidence；P2 逐项处置。
7. 修完派 **impl-r2**（同一独立席位），P0/P1=0 且 AC1–AC6 逐条可验收后方可批准。

## 6. 边界声明

本报告只审被审 head 的实现/测试/证据/写域与冻结契约一致性，不审 PREREQ-2 与 FEA-06 主卡；未修改任何源码/卡/设计，未 commit/push；`check.ps1`/`verify_pins` 为只读参考。独立测试与生成器检查命令、结果见 §0；行号基于 `b547e229e` 实测。
