---
task_id: FEA-06-PREREQ-2
reviewer: ZCode（DSH Lead 经 subagent_zcode 派发的独立上下文子代理）
reviewer_kind: agent
author: dsh-lead
base_commit: a33778608
reviewed_head: 9478c96fb
decision: changes_requested
counts: { P0: 0, P1: 1, P2: 3 }
---

# FEA-06-PREREQ-2 实现复核 r1（独立上下文；未参与本卡起草/范围处置/实现）

## 0. reviewer 身份与来源（显式声明）

- **身份**：ZCode 独立上下文实现复核子代理，由 **DSH Lead（本项目 DeepSeek Harness Lead 会话）通过 `subagent_zcode` 派发**。
- **来源**：DSH Lead 会话派发 / `subagent_zcode` 子任务（2026-10-31 用户裁决的上下文独立口径：产出变更的会话不得自审，作者可派独立上下文子代理执行 Review）。
- **独立性声明**：本席位未参与 FEA-06-PREREQ-2 的起草、scope r1–r4 处置、W-1…W-12 裁决与任何 P1–P7 实现；只读被审 head。
- **坐标核实**：`git rev-parse HEAD` = `9478c96fbf2504d551fac6387973a5d4c2a6a09e`；`git status --short` 干净（本报告为唯一写入）；`92cac5ab1..9478c96fb` 仅改任务卡 1 文件（证据回填），源码/证据字节两 commit 一致。
- **被审范围**：`a33778608..9478c96fb`（60 files，+2688/−234）。

## 1. 一句话结论

实现质量本身**全部达标**：AC1–AC7 逐条实测 MET，全量 **1022/0/57 复现**、build 0w/0e、两生成器 `--check` EXIT 0、`check.ps1` PASS(3 warnings)、`verify_pins` 15/15、卡内 30 条证据 sha256 机械匹配 30/30、W-12 必需性经本席位独立机械证实且冻结面零触碰。**唯一 P1 是程序性的**：两处源码改动落在 allowed_paths 之外且未获 W-12 式裁决回填——`ThemePaletteComposer.cs`（`ThemeEngine/Palette/**`）与新增 `IThemeSettingsSink.cs`（`ThemeEngine/Service/**`），卡的**全部历史版本**从未覆盖这两个目录（`git log` 全版本 grep `Palette/**|Service/**` = 0）。两处均为 AC5/AC6/AC7 的行为必需、改动正确且在 delivery-notes/checkpoint 有内容披露，但缺「补写域 + 裁决行」的登记动作；返修为 docs-only 卡面补正，无需代码返修。**decision: changes_requested（P0=0 / P1=1 / P2=3）**。

## 2. 逐 AC 判定

| AC | 判定 | 关键实测证据（行号基于 `9478c96fb`） |
|---|---|---|
| AC1 selector 决策表 | **MET** | `FrontendSelector.cs:83-131`：`ResolveCandidate`（:133-148）实现 CLI `--frontend` > persisted `theme.frontendId` > 缺省 `builtin.current-v2`；`builtin.fluent` → Fluent（:97-105）；未知/**`builtin.fluent-dark`** → V2 + `IsFallback` + 专属诊断「is a visual theme id…not a frontend id」（:117-130）+ `Trace.TraceWarning`（:123）；App 层再记 Trace（`App.axaml.cs:71-75`）。`FrontendSelectorTests.cs` 13 例（11 Fact + Theory×3）：CLI 双向优先、persisted、双缺省、空白视为缺省、未知值（CLI/persisted 各一）、`fluent-dark`/错误大小写/下划线负例、trim、有效 id 恒为冻结两值之一（:125-143） |
| AC2 组合根分派 + V2 不回归 | **MET** | `App.axaml.cs:115-140` `CreateShell`：`!options.UseV2Shell`（`--shell=legacy` 运维修回）**优先于** selector；否则 `selection.IsFluent` 选 Fluent/V2。V2 路径对照 `git diff a33778608..9478c96fb -- App.axaml.cs`：仅实例方法→静态 + `this`→`application` + `_designSystemTheme`→显式 `themeManager` + `ThemeHome.Resolve` 前移，语义零变化（`_designSystemTheme is null` 检查因参数非空断言而消除，等价）。`FluentShellTests.cs:122-168` `CompositionRoot_DispatchesToFluentV2AndLegacyShells` 实建三壳：`Assert.IsType<FluentShell>`(:142)/`AppShellV2`(:153)/`MainWindow`(:166)，且 legacy 优先于 fluent 选择(:157-166) |
| AC3 Fluent 壳骨架 | **MET** | `FluentShell.axaml`：顶条 `Nm.Size.TopBand`(:16)、左导航 `Nm.Size.TreeWidth`(:42)、状态条 `Nm.Size.StatusBandPage`(:94) 全 `DynamicResource`，全文无裸尺寸值；四页占位（`FluentShell.axaml.cs:38-53` PageCopy）；`--page` hook `Navigate(string)`(:166-185)。headless 测试：令牌尺寸断言（`FluentShellTests.cs:93-95` `Bounds.Height/Width` vs `TokenDouble(NmKeys.*)` precision 3）、四页切换 + 点击路径（:49-76）、`--page` 映射含未知 id 拒绝（:101-118） |
| AC4 全量不退化 | **MET** | 本席位复跑：`dotnet build` → **0 警告/0 错误**（9.42s）；`dotnet test --no-build` → **1022 passed / 0 failed / 57 skipped**（21+51+253+86+31+128+452），与卡面/交付声明一致；实施前基线 979/0/57（delivery-notes §开头）净增 43 |
| AC5 写者收敛 + 兼容写 | **MET**（一项测试缺口→P2-3） | ① `AppearanceCoordinator` 在 `NewManga.Appearance`（`AppearanceCoordinator.cs:21`，namespace `NewManga.Appearance`）；旧 `App/Services/AppearanceCoordinator.cs` 已删除（diff deleted）；`SaveAsync`(:67-79) → `AppearanceStore.WriteAsync` 为 `presentation-settings.json` 唯一生产写路径（src 全量 grep `.SaveAsync(`：唯一其他调用 = sink→coordinator，`AppearanceThemeSettingsSink.cs:45`；`ThemeService.cs:651` 调的是 `_persistence.SaveAsync` 即兼容写）。② `ThemeSettingsStore` 两参构造器保留（:36-39 委托三参重载 :46-56）；`[Obsolete] SaveAsync`(:159-196) 先原子写 legacy（:173-184）再 `Trace` + sink 镜像（:192-195），sink 异常传播（Compat 测试 `CompatibilityWrite_SurfacesSinkFailures_AfterTheLegacyWrite` 断言 legacy 已写 + 异常上抛）。③ `IThemeSettingsSink.cs` 在 ThemeEngine（`namespace NewManga.ThemeEngine`），无 Appearance 反向引用。④ adapter 字段映射：`ThemeSettings` 6 字段全映射（`AppearanceThemeSettingsSink.cs:36-44`），`ReducedMotion`→`MotionMode.Reduce/Full`（:42，测试 `Sink_PreservesTheLegacyMotionOnOffSemantics` 双向断言）；legacy 无等价物字段保留 coordinator 现值（`with` 表达式）。⑤ 注入：`CreateProduction` 增可选 `presentationSink`（App.axaml.cs:166-172 传入）+ 测试 `ProductionThemeStudio_IsWiredWithTheCompatibilitySink`（写入传播到 sink + legacy 双断言）；`StubThemeStudioService.Create` 增同参（diff :64 传三参构造器）但**无直接注入测试**（→R1-P2-3），沙箱默认 null 安全 |
| AC6 Material 主题层键 | **MET** | `NmKeys.g.cs:414-419` 含 `Base/Tint` 常量（生成物，TokenGen `--check` EXIT 0 自证非手改）；`Themes/Tokens.Global.axaml` grep 仅有 `Acrylic.Opacity`(:50)/`Mica.Enabled`(:51)，无 Base/Tint；`DesignSystemThemeManager.cs:125-132` Required 59 不变 / `:141-142` Allowed = Required+LineBox(6)+Material(2) = **67**（R14 断言 `59/67/2` 实测自洽，`R14ContractTests.cs` 新增 `Material_acrylic_keys_are_registered_but_not_published_globally` 断言 theme-layer scope 恰为两键 + Global 含 Opacity/Mica 不含 Base/Tint）；`ThemePaletteComposer.cs:68/90` 允许 59 或 61（`ThemeLayerMaxKeyCount`）、`AddMaterialColors`(:136-174) 半套抛 `FluentMaterialKeyMissing`（测试 `Compose_rejects_a_half_specified_fluent_material`）；fluent 包 colors 承载两值（`fluent-dark.nmtheme` diff 两变体各 +2 键）；**`newmanga-default.nmtheme` diff 为空（字节不变）**；ThemeGen `--check` EXIT 0 |
| AC7 manifest + 校验 + Current 不生效 | **MET** | `fluent-dark.nmtheme:145-147` `metadata.extra["nm.fluent.visual"]="1"`（`BuiltInThemeGenerator.cs:227-237` 生成，Current 包 `Extra` 为空——`ThemeContractTests` 断言）；`ThemeValidator`：Fluent 判别 = descriptor tag `fluent`（`IsFluentPackage` :83-88）；manifest 缺失（`FluentManifestMissing`）/ 手改值≠`"1"`（`FluentManifestInvalid`）/ 非 Fluent 声明（`FluentManifestInvalid`）均 error（:96-134，测试三负例 :352-381）；材质键 Fluent 缺失（`FluentMaterialKeyMissing`）/ 非 Fluent 声明（`FluentMaterialKeyUnexpected`）均 error（:255-289，测试两负例 :385-409）；`Shipped_fluent_package_validates_without_errors`(:340-348) 无 error；Current 不生效：`ThemeServiceTests.Initialize_applies_the_default_theme_and_reports_readiness`(:44-57) `Current.Id == newmanga-default` + `LastLayer.Count == 59`（default 层无材质键）；常量与 C-02 §4 一致：`ThemeContractTests.Fluent_manifest_constants_match_the_frozen_contract` 显式断言 `nm.fluent.visual`/`1`/`nm.fluent.visual/1` |

## 3. Findings

| ID | 严重度 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R1-P1-1 | **P1** | `apps/desktop-avalonia/src/NewManga.ThemeEngine/Palette/ThemePaletteComposer.cs`（+74 行，`92cac5ab1`）；`apps/desktop-avalonia/src/NewManga.ThemeEngine/Service/IThemeSettingsSink.cs`（新增 21 行） | **实施期写域扩张未回填、未登记**。两文件分别落在 `ThemeEngine/Palette/**` 与 `ThemeEngine/Service/**`——卡的 allowed_paths 只覆盖 ThemeEngine 的 `Persistence/Models/Serialization/Themes/Validation` 五个子目录；本席位对卡**全部历史版本**（11 个 commit）grep `Palette/**|Service/**` 均为 0，即从未被任何 scope 轮覆盖。改动本身**行为必需且正确**：不修 Composer 则 fluent 包（61 键）合成必抛 `expected 59` 异常 → `BuiltInThemes` 加载 fluent 失败 → AC6/AC7 不可能 MET；无 sink 接口文件则 P5「避免 ThemeEngine→Appearance 引用」无承载位。且均在 delivery-notes §1 与 checkpoint §28 有**内容披露**（非暗改），契约面零触碰（`Compose` 公开签名未变，仅新增常量成员；新增接口不改既有接口）。但对比 W-12 对 `Validation/**` 的处理（补 allowed_paths + 附加裁决行），这两处**缺登记动作**——若不记，等于默认写域可不登记扩张，scope 冻结制度失去激励 | 卡面 allowed_paths 回填 `apps/desktop-avalonia/src/NewManga.ThemeEngine/Palette/**` 与 `.../Service/**` 两行 + 「附加裁决点」补一行（建议 W-13，引 C-03 §2.1/§2.2 sink-only 与 V-03 材质组合成链路为依据，注明与 W-12 同性质）。**docs-only 一次 commit 可闭合，无需代码返修**；闭合后本 P1 即消 |
| R1-P2-1 | P2 | 卡 `:92`（W-12 行）；`ThemeValidator.cs:38-40` | W-12（`Validation/**` 写域补口 + id 规则放宽）**合法但属实施期自裁决**：scope-r4 §4.2 曾把「不改 validator、只加测试」认定为隐式最小路径，实施期推翻该路径时未再走一轮独立 scope 复核。必需性本席位已独立证实（见 §4.1），不构成 P1 | 程序注记：同类写域补口建议前置到 scope 轮或事后即时补独立复核确认（本报告即充当该确认）；无行动项 |
| R1-P2-2 | P2 | `ThemeValidator.cs:38-40`（IdPattern） | 放宽面宽于最小必要：`.` 对**所有** id（含 user 主题）放行，而最小改动可仅对 `builtin.*` 前缀放行。威胁面无实质变化（旧规则下 user 已可注册 `builtin-evil` 类前缀伪装；正则仍拒绝首尾非字母数字、仍限 64 字符、大写/下划线仍拒绝），既有 `DescriptorIdInvalid` 用例未削弱 | 登记为已知放宽；若后续需要 user/builtin 命名空间隔离，按 `builtin.` 前缀特判收紧（FEA-06/Theme Studio 导入侧） |
| R1-P2-3 | P2 | `StubThemeStudioService.cs:33-64` | sink 注入的两个生产创建点中，`CreateProduction` 有端到端测试（`ProductionThemeStudio_IsWiredWithTheCompatibilitySink`），`StubThemeStudioService.Create` 的 `presentationSink` 通路**无直接测试**（既有 4 处调用均默认 null；仅靠代码评审确认 :64 传参正确）。沙箱默认 null 不镜像属安全默认，风险低 | 补一个最小测试：`StubThemeStudioService.Create(..., presentationSink: recording)` → 触发保存 → 断言 sink 收到写入（与 CreateProduction 测试对称）；可并入 FEA-06 或本卡 P1 补正 commit 顺手做 |

**无 P0。**

## 4. 专项核验

### 4.1 W-12 合法性（独立结论：**合法；应记 P2 而非 P1**）

1. **必需性（本席位机械复证，非转述）**：旧 IdPattern `^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$` 对 `builtin.fluent-dark` 匹配 = **0**（新 pattern = 1；对照 `newmanga-default` 两版均 1）。即 W-12 行所称「现有 Validate(fluent-dark) 因 id 含 `.` 必失败」为真——不补口则 `DescriptorIdInvalid` error 常在，AC7「Validate(fluent) 通过」不可能。
2. **C-02 §4 义务归属为真**：`FEA-C02_V11R_AMENDMENT_DRAFT.md` §4 明定「manifest 缺失或被手改 → 主题包加载失败；校验器覆盖『令牌齐全性 + 例外仅限 Fluent + 无裸值』」且「校验器归属 = ThemeEngine 的项目内校验器（构建期 + 单测）」。旧 validator 无 manifest 校验逻辑，「不改 validator、只加测试」（scope-r3 R3-P2-2 最小路径）**无法实现**该义务——scope-r3 的最小路径与 C-02 §4 义务本就不相容，W-12 是纠偏而非扩权。
3. **冻结面零触碰（实测）**：`enum ThemeKind`（`ThemeModels.cs:4`，diff hunk 全在 :457+ 常量区）、`IThemeValidator`（`ThemeContracts.cs`，整文件不在 diff）、`Validate(ThemePackage)` 公开签名均零字节变化；新增 `IsFluentPackage` public static 与 `ValidateTokenSet/ValidateColors` 私有参数变化不构成 V-07「不新增枚举值、不改公开方法签名」的违反。`ThemeTokenSet` 构造器签名未变（fluent 复用 `ThemeMaterial.Solid`）。
4. **P2 而非 P1 的理由**：行为必需 + 冻结面合规 + DSH 持有范围裁决权（2026-10-25 用户裁决）+ 卡内完整登记依据与日期 + delivery-notes/checkpoint 披露——与 R1-P1-1 的差别恰在**有无登记动作**，此区分维持制度激励。

### 4.2 R4-OBS-1 披露核验（处置**得当**）

- 工作区 `doc/reviews/FEA-06-PREREQ-2-scope-r4.md` 为并行双席位产物（另一席位版本在 `b2a45af6d`，git 历史字节保留）；`checkpoint §28`（`GOAL-PROGRESS-2026-11-02.md:223` 附近）与 `delivery-notes.md §3` 均如实披露：两席位结论同向（approved/P0=P1=0）、差异仅 P2 计数（1 vs 0）、本会话采纳保守 P2=1 并在实施中顺手关闭（R4-P2-1 计数措辞）。
- **关闭验证**：卡 `:66` 现文已为「**59 不变**（Base/Tint 为可选键，不进 Required 59），**65 → 67**」——r4 指出的「全局令牌数不增」错误归因已移除，R4-P2-1 CLOSED。
- 判定：不重开范围冻结、历史字节保留、口径差异注记——处置得当，无需行动。

### 4.3 证据表机械验证（**30/30 匹配**）

卡 Canonical Evidence 表（26 CANONICAL + 1 SOURCE_PIN，正则抽取 30 行含表头重复匹配）逐条 `sha256(工作区文件)` 比对：**30/30 一致，0 缺失**。注：以 `git show 92cac5ab1:path | sha256sum` 复算时部分文件（18 个 log + 5 个源码）不一致，经查为 `git show` 的行尾归一化（blob LF vs 工作区 CRLF，`file` 实测 test.log 工作区 CRLF）所致，**非证据偏差**；工作区字节口径（`92cac5ab1` 与 `9478c96fb` 内容相同，diff 仅任务卡 1 文件）即 check.ps1 的核验口径。证据覆盖 AC1–AC7 + AC4/Gate 全部验收面，无自证式空缺（每 AC 至少一条独立测试 log + 对应源码文件）。

### 4.4 生成物纪律

- `TokenGen -- --check` → **EXIT 0**「up to date: every generated artifact matches the frozen token source byte-for-byte」（292 rows）；`ThemeGen -- --check` → **EXIT 0**「up to date」。两 check 通过即证 `NmKeys.g.cs`/`TokenMap.md`/`fluent-dark.nmtheme`/`newmanga-default.nmtheme` 均为生成器产物、无手改。
- `Themes/Tokens.Global.axaml` 未被 theme-layer 键污染：Material 键仅 `Acrylic.Opacity`/`Mica.Enabled` 两个全局令牌（:50-51），Base/Tint 仅存在于 `NmKeys` 常量 + 主题包 colors。

### 4.5 治理指针与治理脚本

- 三指针一致：`STATUS.md:7`（in_review，实现完成 1022/0/57，impl 复核待）= `REBASELINE_PLAN.md:22`（DAG 表行）= `:37`（当前 DAG 段）= `TASK_LEDGER.md:43`（in_review）= 卡 frontmatter `status: in_review`、`delivery_head: 92cac5ab1`。
- `check.ps1` → **PASS（3 warnings）**：10 非终态 Task / STATUS 3086B/29 行 / PLAN 4009B/62 行（与 r3/r4 同源、无新增，体积微增系指针文字刷新）；`verify_pins.ps1` → **PASS (all 15)**，14 契约 + FEA-01 冻结字节未被触碰。
- 写域机械核对（`git diff --name-only` 60 文件 vs allowed_paths）：**56 在域、4 越界**——`ThemePaletteComposer.cs`/`IThemeSettingsSink.cs`（→R1-P1-1）；`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` 与 `doc/handoffs/FEA-06-PREREQ-2-session-handoff.md` 属 DSH 治理职权滚动文档，沿 scope-r3 R2-P2-4 / scope-r4 §2.1 先例**如实登记不列为 finding**。

### 4.6 回归削弱检查（**无削弱**）

- `AppearanceCoordinatorTests` 迁移：旧 App.Tests 版 4 个测试方法（Reload 三态 + DoesNotTouchResources）**全部保留**于 Appearance.Tests 新版（方法名逐一对应），并**新增 4 个**（SaveAsync 写文档/Changed 单次、不写 legacy 文档、identical 不重复 raise、legacy 迁移），87→159 行，纯增强。
- 三处 pragma（`ThemeHomeTests.cs:131-133`、`LegacyThemeMigrationTests.cs:131-133`、`LegacyThemeRetirementGateTests.cs:92-94`）：均为单语句 `#pragma warning disable/restore CS0618` + 注释说明「兼容写即被测对象」，禁用范围最小、断言未动——合理，非削弱。
- `ThemeSettingsCompatibilityWriteTests`（4 例）与 `AppearanceThemeSettingsSinkTests`（4 例）为净新增；`ThemeValidatorTests`/`ThemeContractTests`/`R14ContractTests`/`ThemePaletteComposerTests`/`BuiltInThemeGeneratorTests` 均为增量断言，无既有断言删除。

## 5. 结论

**P0 = 0 / P1 = 1 / P2 = 3 → `changes_requested`。**

实现本身七项 AC 全部 MET 且证据链完整可机械验证；W-12 经独立证实合法（P2 注记）。唯一 P1（R1-P1-1：`Palette/**` 与 `Service/**` 两处写域扩张未回填登记）是**程序缺口而非行为缺陷**——修复仅需卡面 docs-only 补正（allowed_paths 回填 + 附加裁决行，可顺带闭合 R1-P2-3 的 Stub sink 测试），补正后即可转 approved，不需要任何代码返修。

## 6. 边界声明

本席位只读被审 head `9478c96fb`（复核期间工作区 clean），除本报告外未修改任何源码/卡/契约/STATUS/PLAN/LEDGER/证据，未 commit/push。行号基于 `9478c96fb` 实测。`check.ps1`/`verify_pins.ps1` 为只读参考，不替代审查。本报告不构成 FEA-06 的集成授权；C-02 V-05 视觉例外仍由其自身判据约束。findings 处置与集成验证归 DSH。
