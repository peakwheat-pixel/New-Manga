# V11R-D-1 I2 处置表（r2 独立审查）

- 分支：`v11r/d1-i2`
- Base：`c465d1e4c`（最新 main，含 INT-1 `--shell/--theme-id`）
- 任务：D-1 第二轮独立审查 FAIL（2×P1 + 8×P2）的有界修复
- 结论：**P1-1 / P1-2 全部修复，P2 ①–⑧ 全部实现**；全量测试 0 fail（见 `I2/test.log`）。

## 逐条处置

| # | r2 发现 | 处置 | 实现/证据 |
|---|---|---|---|
| P1-1 | 正常 App 启动后丢全局令牌：`App.axaml` 聚合字典同时含 Global+Dark，`EnsureGlobalTokens()` 见到 `Nm.Space.3` 即认为已加载；`RemovePaletteProviders()` 又因聚合字典含 `Nm.Color.Bg.Canvas` 移除整块 → 间距/字号/Scrim 丢失 | **已修**。① `App.axaml` 拆为 `Tokens.Global.axaml` / `Tokens.Dark.axaml` / `Controls.axaml` 三个独立 provider；② `RemovePaletteProviders()` 跳过任何含 `GlobalProbeKey` 的 provider（聚合字典永不移除，只换 palette 层）；③ 新增 `ReorderResourceStack()` 固定顺序 foreign → Global(含聚合) → palette/theme layer → contrast → density → motion；④ 新增 `RealAppResourceStackTests`：按真实 `App.axaml` 清单加载 provider（非合成栈），断言 `Initialize()` 后、明暗切换后、HC/Compact/ReducedMotion 后 `Nm.Space.3=8`、`Nm.FontSize.Md=13`、`Nm.Color.Scrim`、`Nm.Motion.Duration.Slow=220ms` 全部可解析；另加"聚合 Global+palette 字典"回归用例 | `Theming/DesignSystemThemeManager.cs` 的 `RemovePaletteProviders` / `ReorderResourceStack` / `EnsureGlobalTokens`；`src/NewManga.App/App.axaml`；`RealAppResourceStackTests.cs`（2 例）；`I2/real-app-stack-tests.log` |
| P1-2 | Light `Skipped` 徽标实测 ≈4.01:1：测试只比状态前景 vs 纯 `bg.panel`，未合成 `#1F8A8F94` muted 背景 | **已修**。按合成背景复测发现同类失败 7 处，已最小修订 7 个状态前景令牌（dark running/failed/stale/skipped、light queued/blocked/skipped），合成徽标底 4.54–4.62:1，`statusMuted` 与其它令牌不动（DECISION_LOG §6）。`StatusGlyph.notstarted` 由 `Text.Disabled` 改 `Text.Secondary`（2.52→8.18/5.86 on sunken）。新增 `BadgeCompositeContrastTests`：headless 真实渲染帧**采样徽标背景像素**作为合成背景，与解析后的 `StatusGlyph`/label 前景计算 WCAG 对比度；覆盖 9 状态 × dark/light × standard/HC，全部 ≥4.5:1；采样像素同时断言等于"muted over panel"合成值（防止测错背景） | `tokens.json` 7 值 + 重新生成 DS/ThemeEngine 产物；`Styles/Controls.Status.axaml`；`BadgeCompositeContrastTests.cs`；`DECISION_LOG.md` §6；`I2/badge-contrast-tests.log` |
| P2-① | R-15 行框：主题层白名单只有 3 乘数 + 6 语义别名，文本样式却读 `Nm.TextLineBox.*` 绝对值 | **已修**。6 个 `Nm.TextLineBox.*` 加入 `ThemeLayerAllowedKeys`（required 仍 59）；主题层缺省时按自身 `FontSize × LineHeight` 派生（Xxl×Display…），显式提供则校验后采用；新增真实 `TextBlock.body` 行高断言（25.6） | `DesignSystemThemeManager.cs` `LineBoxDerivations`/`TryDeriveLineBoxes`；`R14ContractTests.cs`（59 required / 65 allowed）；`ThemeManagerI2Tests.cs` 前两例 |
| P2-② | overlay 排序：palette 在索引 0、overlay 末尾，独立 Global provider 可能覆盖主题层字体/字号/行高 | **已修**。用 `ReorderResourceStack()` 取代 `ReorderOverlays()`，固定 Global → palette → overlays；测试手动把独立 Global 字典追加到栈尾，切换 HC/Compact/ReducedMotion 后主题层 Georgia/16/25.6 仍生效并断言 Global 索引 < palette 索引 | `DesignSystemThemeManager.cs`；`ThemeManagerI2Tests.Overlay_toggles_keep_theme_typography_and_use_fixed_provider_order` |
| P2-③ | `ApplyPalette` 补非颜色值时按合并字典正序取第一个值，可能用默认值覆盖主题层 | **已修**。`TryResolveApplicationValue` 改为从**栈尾向前**取有效优先级（last wins），密度 overlay/主题层优先；测试：主题层 Geogia/15/24 后 ApplyPalette 仍保留字体字号行框 | `DesignSystemThemeManager.cs`；`ThemeManagerI2Tests.Applying_a_palette_after_a_theme_layer_preserves_its_typography` |
| P2-④ | ReducedMotion 漏 `Slow=220ms` | **已修**。`Motion.Reduced.axaml` 增加 `Nm.Motion.Duration.Slow=0ms`（生成器 rows 277→278）；`TokenDerivationI2Tests` 断言 Instant/Fast/Normal/Slow 全零 + Enabled=false | `Tokens/TokenGenerator.cs`；重新生成；`TokenDerivationI2Tests.cs` |
| P2-⑤ | FocusRing 无键盘/指针区分、未按祖先 ScrollViewer 裁剪 | **已修**。仅 `NavigationMethod.Tab/Directional` 显示（Pointer 隐藏）；新增 `EffectiveViewportChanged` 订阅与 `IsFullyVisible()`，被祖先 ScrollViewer/窗口裁切时隐藏、滚回后恢复 | `Theming/FocusRing.cs`；`FocusRingBehaviourTests.cs`（指针不显示 / Tab 显示 / 滚出视口隐藏再恢复） |
| P2-⑥ | 失败路径 manager 状态可能已改 | **已修**。`Initialize/SetAppearance/SetContrast/SetDensity/SetReducedMotion` 全部"先加载验证、后一次性提交"；失败时 Appearance/Contrast/Density/ReducedMotion/RequestedThemeVariant/AppliedPaletteId/资源栈均不变；`Initialize` 失败保持 `IsInitialized=false` 与默认值 | `DesignSystemThemeManager.cs`；`ThemeManagerI2Tests` 三个 failure-path 用例（broken light palette / broken overlay×3 / broken global） |
| P2-⑦ | 密度单调验证 `continue` 跳过 Padding | **已修**。`ValidateDensityMonotonic` 用 `Thickness` 四分量严格比较（comfortable 基线同时支持 frozen bindings 与派生 globals，缺基线直接抛错，不再跳过）；新增 committed 字典的逐项分量单调断言 | `Tokens/TokenGenerator.cs`；`TokenDerivationI2Tests.Density_overlays_are_componentwise_strictly_monotonic` |
| P2-⑧ | P3：`VisualEvidenceTests:52` 恒真断言；图标测试只遍历 required 子集 | **已修**。改为 appearance 切换前后 `Assert.Same(galleryContent, window.Content)`（AC7 同一视觉树）；图标测试遍历 `Enum.GetValues<NmIconKind>()` 全部 41 值（几何/尺寸/stroke），required 子集保持存在性断言 | `VisualEvidenceTests.cs`；`CustomControlsTests.cs` |
| — | 继承红（main）：C-2 `MyThemesSectionView.axaml` 的 `BorderThickness="0"` 触发 V2 raw-value conformance | **驱动式修复**：删除该默认值属性（语义不变，一行），`V2Xaml_UsesNoRawDesignValues...` 恢复绿 | `MyThemesSectionView.axaml` |
| — | 连带特征化更新：ThemeEngine edge-surface warning 由 3→1（token 修复后 light canvas/raised 已达标，只剩 dark status on Bg.Raised） | 更新断言为 `Assert.Single` 并注明原因；ThemeEngine 生成基线已按新 token 重生成 | `ThemeValidatorTests.cs`；`newmanga-default.nmtheme` / `ThemeTokenBaseline.g.cs` |

## 验证（全量，worktree 内）

- `dotnet build NewManga.sln -warnaserror`：0 warning / 0 error（`I2/build.log`）
- `dotnet test NewManga.sln --no-build`：**0 fail**
  - NewManga.DesignSystem.Tests **82**（原 67，新增 15）
  - NewManga.ThemeEngine.Tests **229**
  - NewManga.App.Tests **294**（+6 skip）
  - NewManga.Host.Tests **42**（+24 skip）
  - NewManga.CoreClient.Tests **42**（+25 skip）
- 专项：`RealAppResourceStackTests` 2/2、`BadgeCompositeContrastTests` 1/1（`I2/real-app-stack-tests.log`、`I2/badge-contrast-tests.log`）

## 边界说明

- 本包只改：DS（manager/focus/generator/status style/tokens 生成物）、DS 测试、`App.axaml`（P1-1 必需）、冻结 tokens（P1-2 授权）、DECISION_LOG §6、ThemeEngine 由 token 派生的生成物/特征化断言、C-2 一行 conformance 修复。
- 未改：旧 `NewManga.Theme`、旧壳 View/ViewModel、C-2/C-3 产品逻辑；未 push。
