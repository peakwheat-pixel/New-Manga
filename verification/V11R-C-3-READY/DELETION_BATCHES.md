# V11R-C-3 删除批次清单与顺序（C-3 执行手册）

- 任务：`V11R-C-3-READY`（就绪包）；执行任务：`V11R-C-3`
- 基线：`df883f2ceec98d2fa521c10ec1e5d4ce2bdafb1e`（R1 tag `v11r-pre-retire`，当前 main）
- 依赖图证据：`DEPENDENCY_GRAPH.md` / `dependency-graph.json`（634 引用 / 69 文件）
- 原则：**先建新（R1–R2）→ 迁移入口（R3）→ 替换测试后删（R4）→ 删项目（R5）→ 零引用门（R6）**
- 回滚点：R1 创建的 tag `v11r-pre-retire`（脚本 `tools/v11r/rollback-theme-retire.ps1`）

## 1. 三类文件与处置

### A 类：可删（前置条件满足后直接删除）

| 批次 | 文件 | 引用数 | 前置条件 | 删除步骤 |
|---|---|---:|---|---|
| A1 旧测试 | `tests/NewManga.App.Tests/ThemeMacosTests.cs` | 88 | 替代断言已存在（见 §2）；先补“字体二进制审计”断言 | R4 |
| A1 旧测试 | `tests/NewManga.App.Tests/ThemeLayoutsTests.cs` | 100 | 同上 | R4 |
| A1 旧测试 | `tests/NewManga.App.Tests/ThemeMacosAuditTests.cs` | 9 | 同上 | R4 |
| A1 旧测试 | `tests/NewManga.App.Tests/S3ShellTests.cs` | 20 | 同上 | R4 |
| A1 旧测试 | `tests/NewManga.App.Tests/S4ReaderWorkbenchTests.cs` | 1 | 同上 | R4 |
| A2 旧项目 | `src/NewManga.Theme/ThemePack.cs` | 83（含自引用） | 生产入口已迁移（B 类全部完成） | R5 |
| A2 旧项目 | `src/NewManga.Theme/NewManga.Theme.csproj` | — | 同上 | R5 |
| A2 工程文件 | `NewManga.sln` 中 `NewManga.Theme` 项目行（第 12 行及对应配置） | — | 同上 | R5 |
| A2 工程文件 | `src/NewManga.App/NewManga.App.csproj` 的 `NewManga.Theme` ProjectReference（第 40 行） | — | 同上 | R5 |
| A2 启动钩子 | `src/NewManga.App/AppOptions.cs` 的 `--theme` 旧钩子（保留 `--variant`） | 1 | 新 `--theme-id`（ThemeEngine）就位 | R5 |

### B 类：需先迁移（不可直接删）

这些文件是**仍在运行的生产路径**（旧壳仍为默认入口，`App.axaml.cs:62` `new MainWindow(...)`）。必须先迁移到
新壳/新引擎，C-3 才能删除或改写；其中 `Views/**` 整体退役依赖 **INT-1（V2 壳成为默认入口）**。

| 文件 | 引用数 | 迁移动作 | 前置 |
|---|---:|---|---|
| `src/NewManga.App/Views/Pages.cs` | 124 | 主题中心/旧书架：主题选择→Theme Studio（ThemeEngine）；`ThemePackService.Brush(...)`→DS `DynamicResource Nm.*`/Classes；旧页面随旧壳退役 | INT-1 + Theme Studio 页面就位 |
| `src/NewManga.App/Views/MainWindow.axaml.cs` | 33 | 移除窗口级 `ThemePackService.Apply/ApplyVariant`、macOS 红黄绿/标题栏旧逻辑；改用 DS 根样式 + 新壳 chrome | INT-1 |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | 13 | 旧工作台页退役，能力由 V2 Studio/Reader 承接 | INT-1 |
| `src/NewManga.App/Views/ProfileSections.cs` | 7 | 用 DS 控件重写设置分区（新设置页） | 新设置页就位 |
| `src/NewManga.App/Views/ImportExportPanels.cs` | 4 | 4 处 `Brush("CardBg"/"CardBorder")`→`Border.card`/`Border.panel` Classes | 低风险，可先做 |
| `src/NewManga.App/Views/CredentialSection.cs` | 4 | 4 处 `Brush(...)`→DS 令牌/Classes | 低风险，可先做 |
| `src/NewManga.App/Views/ProviderBindingsSection.cs` | 1 | 1 处 `Brush(...)`→DS 令牌/Classes | 低风险，可先做 |
| `src/NewManga.App/ViewModels/MainViewModels.cs` | 2 | 删除 `ThemePacks`/`SelectedPack` 旧模型，换 Theme Studio 绑定 | Theme Studio 就位 |
| `src/NewManga.App/App.axaml.cs` | 3 | 删除 `ThemePackService.ApplyDefault/Apply/ApplyVariant`；启动改由 ThemeEngine/DS（`--variant` 已由 `Initialize` 消费）；同时切默认入口到 V2 壳（INT-1） | INT-1 + ThemeEngine `IThemeService` 就位 |
| `src/NewManga.App/AppOptions.cs` | 1 | `--theme` → `--theme-id`（ThemeEngine）；`--variant` 保留 | R5 |

**门禁**：B 类未清零前，A2 不得删除（否则 App 编译失败）；R3 完成标准 = 上述 10 个文件旧符号引用为 0
（`git grep` 复核，允许 ThemeEngine README 的“已取代”说明文字）。

### C 类：受证据 pin 保护（禁止修改/删除）

87 处 / 30 文件（完整清单见 `DEPENDENCY_GRAPH.md` §6）：计划/契约/任务/交接/历史验证证据（`doc/**`、
`verification/THEME-MACOS-2/**`、`verification/V11R-C-1/**`、`verification/RELEASE-REPACK-5/**` 等）。
处理原则：保持原字节；如新事实与旧文档冲突，由 Lead 追加新说明/新证据，不就地改写；删除任务不得以
“清理旧文档”为名触碰这些文件。

## 2. 旧测试 → 替代断言映射（R4 硬门）

| 旧测试（要删） | 替代断言（已存在，除非标注“需新增”） |
|---|---|
| `ThemeMacosTests.MacosPack_IsRegistered_WithChineseLabel_AndDefaultIsUnchanged` | `ThemeEngine.Tests/BuiltInThemeGeneratorTests.Generated_descriptor_is_the_shipped_builtin_default`、`Embedded_default_theme_is_the_generated_package` |
| `ThemeMacosTests.MacosPack_LightAndDarkMatchFrozenSpec_EveryTokenAndMaterial` | `BuiltInThemeGeneratorTests.Generated_theme_layer_matches_the_design_system_palette_semantically`、`Generated_colors_are_the_frozen_token_values`、`ThemePaletteComposerTests.Color_layer_reproduces_the_frozen_token_values` |
| `ThemeMacosTests.LegacyPacks_KeepTheirKeyTokens_AndFallbackNavActiveText` | `LegacyThemeRetirementGateTests`（9 旧 ID → `newmanga-default` 全映射）+ `ThemePaletteComposerTests.Composes_the_whole_theme_layer` |
| `ThemeMacosTests.HotSwitch_MacosLightDarkAndLegacyPacks_P95Under100ms` | `V2ShellUiTests.ThemeToggle_SwapsTokens_WithoutRebuildingShellOrLosingSelection`、`DesignSystemThemeLayerSinkTests.Theme_switch_keeps_the_window_instance_and_canvas_pixels`、`Repeated_theme_switches_do_not_duplicate_resource_providers` |
| `ThemeMacosTests.MacosContrast_MeetsWcag_ForBodyAndSecondaryText` | `ThemeValidatorTests`（对比度校验）+ `verification/V11R-D-1/contrast-matrix.md`（L3 矩阵证据） |
| `ThemeMacosTests.MacosMotion_ReducedMotionZeroesEveryDuration` | `DesignSystemThemeLayerSinkTests`（reduced-motion 令牌）+ `ThemeEngine.Tests` 动效范围校验 |
| `ThemeMacosTests.SettingsPage_AppearanceSwitch_AppliesMatchingVariant_AndLeavesNoResidue` | `ThemeServiceTests.Set_appearance_recomposes_the_palette_for_the_new_variant_and_persists`、`V2ShellUiTests.ThemeToggle_...` |
| `ThemeMacosTests.MainWindow_TrafficLights_VisibleOnlyForMacosPack_AndFontStackFollowsPack` | `V2ShellUiTests` 壳渲染 + `V2ConformanceTests`；**需新增**：字体二进制审计断言（`git ls-files '*.ttf' '*.otf'` 为空）；窗口 chrome 断言随新壳测试 |
| `ThemeMacosTests.MacosScreenshots_RenderFourRealFrames_WithVariantBackgrounds` | `VisualEvidenceTests.Gallery_renders_dark_light_and_high_contrast_from_the_same_window`；新壳截图证据由 `ShellEvidenceWriteTests` 承接 |
| `ThemeLayoutsTests.ThreeMacosLayoutPacks_AreRegistered_WithDistinctLayouts_...` | `ThemeServiceTests.SetLayout...`（`LayoutProfile` 独立持久化）、`ThemeContractTests`（`LayoutProfile` 形状） |
| `ThemeLayoutsTests.AllThreeMacosPacks_CarryCompleteLightAndDarkTokens...` | `BuiltInThemeGeneratorTests.Generated_theme_validates_without_errors`、`ThemePaletteComposerTests.Light_and_dark_layers_are_independent` |
| `ThemeLayoutsTests.SwitchingLayoutPacks_MovesNavHosts_AndAppliesBookshelfAndSettingsLayouts` | `V2ShellUiTests.Shell_RendersAt1600x1000_...`、`Shell_RendersAt1280And1024_WithoutBreakingLayout`、`V2ShellCoreTests.SpaceAndModeSwitch_...` |
| `ThemeLayoutsTests.LayoutAndVariantHotSwitch_P95Under100ms` | `DesignSystemThemeLayerSinkTests.Theme_switch_keeps_the_window_instance_and_canvas_pixels` + `V2ShellUiTests.ThemeToggle_...` |
| `ThemeLayoutsTests.TwelveRealScreenshots_ShowThreeDifferentLayoutsInLightAndDark` | `VisualEvidenceTests`（dark/light/HC）+ 新壳截图证据 |
| `ThemeLayoutsTests.LegacyPacks_KeepSonomaStructure_AndExistingGridThemeListAssertions` | `LegacyThemeRetirementGateTests`（旧 ID 映射）+ `V2ShellCoreTests`（网格/选择不变量） |
| `ThemeMacosAuditTests.MacosFontStack_ShipsNoFontBinary_AndIsSystemOrOflFallbackOnly` | **需新增**：字体二进制审计断言；字体族令牌由 `TokenResourceDictionaryTests` 覆盖 |
| `ThemeMacosAuditTests.MacosTrafficLights_AreVisualOnly_AndDoNotChangeWindowBehaviour` | `V2ShellUiTests` 窗口 chrome/布局；**需新增**：新壳 chrome 不改窗口行为断言 |
| `S3ShellTests.SixPacks_WithManifestParts_AndSaberPurpleDefault` | `LegacyThemeRetirementGateTests`（旧六包映射）+ `BuiltInThemeGeneratorTests` |
| `S3ShellTests.ThemeDictionaries_HoldLightAndDarkVariants_AndHotSwitchUnder100msP95` | `TokenResourceDictionaryTests.Dark_and_light_palettes_publish_the_same_complete_key_set`、`DesignSystemThemeLayerSinkTests.Theme_switch_...` |
| `S3ShellTests.ReducedMotion_ZeroesAllDurations` | `ThemeEngine.Tests` 动效 + DS reduced-motion overlay 测试 |
| `S3ShellTests.Columns_AreComputedInViewModel_ForWideAndNarrow` | `V2ShellUiTests.Shell_RendersAt1600x1000`、`Shell_RendersAt1280And1024_WithoutBreakingLayout` |
| `S3ShellTests.SearchAndTags_Filter_AndEmptyNoResultsStates` | `V2ShellCoreTests.SpaceAndModeSwitch_KeepSelectionFiltersAndScroll` + `V2ShellUiTests` |
| `S3ShellTests.BookCard_Click_OpensDetails_AndCreateFlowReported` | `V2ShellCoreTests.SelectingBook_...` + 新壳交互测试 |
| `S3ShellTests.Page_RendersSearchChipsAndGrid_WithThemeTokens` | `V2ConformanceTests`（令牌/无裸值）+ `V2ShellUiTests` |
| `S3ShellTests.WindowMaterial_MicaOnWin11_OpaqueFallbackOnWin10` | **需新增**：窗口材质在两种 OS 的 fallback 断言；DS 无 material 令牌（D-14） |
| `S3ShellTests.FourPageNavigation_AndKeyboardFocus` | `V2ShellUiTests` 键盘/导航 + `V2ShellCoreTests` |
| `S3ShellTests.Startup_DoesNotBlockFirstFrame` | 新壳启动证据（`ShellEvidenceWriteTests`）；**需新增**首帧非阻塞断言 |
| `S3ShellTests.SettingsWiring_CoversImplementedCommands_AndRegistersNsBatch` | `SettingsProfileUiTests`、新设置页 wiring 测试 |
| `S3ShellTests.SettingsPage_RendersThemeCenterAndNsBatch` | 新设置页 + Theme Studio 测试（Theme Studio Task） |
| `S4ReaderWorkbenchTests.*`（10 个，旧壳 reader workbench） | `ReaderLibraryTests`、`ReaderProgressTests`、`ReaderChapterSelectorTests`、`RegionWorkbenchUiTests`、`V2ShellUiTests.ReaderOverlay_...` |

> 标“**需新增**”的 5 条断言是 R4 前的硬门：C-3 执行时先补测试并通过，再删对应旧测试；否则 R4 不通过。
> 其余映射均已存在于当前 main 测试中（基线 `c5037b65` 全绿）。

## 3. 执行顺序与门禁

| 步骤 | 动作 | 前置 | 验证 | 回滚点 |
|---|---|---|---|---|
| R1 | 建 tag `v11r-pre-retire`；确认本 READY 包（依赖图/迁移门测试/删除清单/回滚脚本/L3 矩阵）已合入 main | 本 Task 合并 | `LegacyThemeRetirementGateTests` 绿（26 例） | tag 本身 |
| R2 | 运行迁移门测试 + 依赖图重核（脚本刷新）；确认 `MIGRATE-THEN-DELETE`/`REPLACE-BEFORE-DELETE` 数量与清单一致 | R1 | `dependency-graph.json` 与 `DELETION_BATCHES.md` 一致 | R1 tag |
| R3 | 迁移 B 类 10 文件：低风险 4 处 `Brush(...)`→DS class 先做；主题中心→Theme Studio；App 启动切 ThemeEngine/DS；INT-1 切默认入口到 V2 壳；旧 Views 随旧壳退役 | R2 + INT-1 + Theme Studio | 旧符号引用 → 0（仅允许 ThemeEngine README 说明） | R1 tag |
| R4 | 补齐 5 条“需新增”断言 → 删除 5 个旧测试文件 → 跑新测试全绿 | R3 | 新测试全绿；`ThemeMacosTests` 等 5 文件不存在 | R1 tag |
| R5 | 删 `NewManga.Theme` 项目 + sln/App.csproj 引用 + `AppOptions --theme` 旧钩子 | R4 | `dotnet build NewManga.sln -warnaserror` 0W/0E | R1 tag |
| R6 | 零引用门：重跑本 READY 依赖图脚本，确认无 `DELETE-WITH-C3/MIGRATE-THEN-DELETE/REPLACE-BEFORE-DELETE` 引用；全仓测试绿 | R5 | 依赖图 + build/test 日志 | R1 tag |

**硬门**：R3–R6 任一步出现“仍有生产引用/旧配置无法启动/新测试红”，立即回滚到 R1 tag 并记录原因；
回滚操作见 `ROLLBACK_DRILL.md` 与 `tools/v11r/rollback-theme-retire.ps1`。

## 4. 本 READY 包已完成的验证

- 迁移门测试：`tests/NewManga.ThemeEngine.Tests/LegacyThemeRetirementGateTests.cs` 26 例全绿（9 旧 ID ×
  文件级端到端 + 未知 ID（有/无 registry）+ 空/缺失 + 旧键组合 + 幂等 + 表完整性）。
- 依赖图：634 引用/69 文件已分类，含机器可读 JSON 与全表。
- 回滚脚本：dry-run 通过（见 `verification/V11R-C-3-READY/rollback-dry-run.log`）；实际 git 回滚 + 启动
  smoke 演练留到 C-3 执行（`ROLLBACK_DRILL.md` 标注 NOT_RUN 步骤）。
- L3 对比度矩阵：`verification/V11R-D-1/contrast-matrix.md`（4 套盘 × 5 背景，含 6 行/7 对未达标明细与判定依据）。




