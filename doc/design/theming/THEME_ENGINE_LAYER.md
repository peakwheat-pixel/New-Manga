# Theme Engine 主题层白名单（v1）

状态：`FROZEN`（2026-10-30，Lead 裁决 R-15；R-21 修正主题不变量派生色排除口径）。
适用：`NewManga.ThemeEngine` 的 palette 输出 ⇄ `NewManga.DesignSystem` 的 `ApplyThemeLayer` seam ⇄
Theme Studio／Reviewer 对齐。上游：`V11R_AVALONIA_CONTRACT.md` §2.2/§4.1、`DESIGN_SYSTEM.md` §1/§2/§3、
`doc/design/redesign-v1/40-fusion/tokens.json`。

**权威来源**：本表与 DesignSystem 的 `DesignSystemThemeManager.ThemeLayerRequiredKeys` 必须逐字一致；
引擎侧 `ThemeTokenKeys.ThemeLayer` 直接引用该公开集合，不维护第二份列表。

## 1. 定位

主题 = **性格**（颜色/字体/圆角/材质/阴影/动效）；布局（导航/书架/密度/工作台/阅读器）与外观
（浅/深/系统/高对比）独立于主题、独立持久化。`ThemePackage` 只承载性格，`ThemePaletteComposer`
把它解析成下面这张**整层主题令牌**表；DesignSystem 的 seam 只接受白名单内的键（白名单外一律忽略/
记录，避免主题覆盖布局或发明第二套令牌）。

## 2. 白名单（整层 = 59 键，R-15）

| # | 组 | 键 | 数量 |
|---|---|---|---|
| 1 | 背景 | `Nm.Color.Bg.App` `Nm.Color.Bg.Canvas` `Nm.Color.Bg.Panel` `Nm.Color.Bg.Raised` `Nm.Color.Bg.Overlay` `Nm.Color.Bg.Sunken` | 6 |
| 2 | 描边 | `Nm.Color.Line.Subtle` `Nm.Color.Line.Default` `Nm.Color.Line.Strong` `Nm.Color.Line.Grid` | 4 |
| 3 | 文本 | `Nm.Color.Text.Primary` `Nm.Color.Text.Secondary` `Nm.Color.Text.Tertiary` `Nm.Color.Text.Disabled` `Nm.Color.Text.Inverse` | 5 |
| 4 | 强调 | `Nm.Color.Accent.Base` `Nm.Color.Accent.Hover` `Nm.Color.Accent.Active` `Nm.Color.Accent.Muted` `Nm.Color.Accent.On` `Nm.Color.Accent.Ring` | 6 |
| 5 | 状态 | `Nm.Color.Status.Queued` `Nm.Color.Status.Running` `Nm.Color.Status.Done` `Nm.Color.Status.Failed` `Nm.Color.Status.Blocked` `Nm.Color.Status.Stale` `Nm.Color.Status.Skipped` | 7 |
| 6 | 状态底 | `Nm.Color.StatusMuted.Queued` `Nm.Color.StatusMuted.Running` `Nm.Color.StatusMuted.Done` `Nm.Color.StatusMuted.Failed` `Nm.Color.StatusMuted.Blocked` `Nm.Color.StatusMuted.Stale` `Nm.Color.StatusMuted.Skipped` | 7 |
| 7 | 字体族 | `Nm.FontFamily.Ui` `Nm.FontFamily.Data` `Nm.FontFamily.Display` | 3 |
| 8 | 字号 | `Nm.FontSize.Xs` `Nm.FontSize.Sm` `Nm.FontSize.Md` `Nm.FontSize.Lg` `Nm.FontSize.Xl` `Nm.FontSize.Xxl` | 6 |
| 9 | 行高乘数 | `Nm.LineHeight.Tight` `Nm.LineHeight.Normal` `Nm.LineHeight.Loose` | 3 |
| 10 | 行高绝对值 | `Nm.LineHeight.Display` `Nm.LineHeight.Title` `Nm.LineHeight.Body` `Nm.LineHeight.Label` `Nm.LineHeight.Meta` `Nm.LineHeight.Data` | 6 |
| 11 | 圆角 | `Nm.Corner.None` `Nm.Corner.Sm` `Nm.Corner.Md` | 3 |
| 12 | 动效 | `Nm.Motion.Duration.Fast` `Nm.Motion.Duration.Normal` `Nm.Motion.Duration.Slow`（R-15，默认 220ms） | 3 |
| | **合计** | | **59** |

值类型（Avalonia 资源）：颜色 `ImmutableSolidColorBrush`；字体族 `FontFamily`；字号/行高乘数/行高绝对值
`double`；圆角 `CornerRadius`；动效 `TimeSpan`。`ComposeColorLayer()` 输出第 1–6 组（35 色）供颜色
seam / 预览快照使用。

## 3. 不进入主题层的键（所有权）

| 键组 | 所有者 | 原因 |
|---|---|---|
| `Nm.Color.Scrim`（Modal 遮罩，`rgba(0,0,0,0.55)`） | DesignSystem 全局令牌字典 | **主题不变量派生色**：不参与任何 appearance palette、不参与主题包校验、不属于 59 键白名单（R-21）。主题包若声明它 → warning 并忽略 |
| `Nm.Motion.Duration.Instant`（0ms） | DesignSystem 全局令牌字典 | 主题不变量（恒 0）；主题只拥有 Fast/Normal/Slow 三档 |
| `Nm.Space.*`、`Nm.Size.*`、`Nm.Row.*`（经 Size 键发布）、`Nm.Padding.*` | DesignSystem | 布局/密度，不是主题性格（Comfortable/Compact/Spacious 由 DS 覆盖字典负责） |
| `Nm.Border.*`、`Nm.Icon.*`、`Nm.Opacity.*` | DesignSystem | 控件几何常量 |
| `Nm.FontWeight.*`、`Nm.FontTracking.*` | DesignSystem | 排版固定层级，不在 Theme Studio 编辑范围 |
| `Nm.State.Symbol.*` | DesignSystem | 状态符号唯一来源（DESIGN_SYSTEM §2.2） |
| `Nm.ZIndex.*` | DesignSystem | 层级常量 |
| `Nm.Motion.Enabled` | DesignSystem（reduced-motion 覆盖字典） | 由 `IThemeService.SetReducedMotionAsync` 驱动，不是主题包字段 |
| `material` / `elevation` | ThemeEngine 仅**校验** | 冻结令牌词汇无对应 `Nm.*` 键；不发明第二套令牌（层级表达用五级明度 + `line.*`，高对比用 DS 盘） |

## 4. 语义约定

1. **整层替换**：seam 应用时以白名单键整体替换主题层；白名单同时约束“主题不得覆盖布局”。
2. **保留其它语义**：Density / HighContrast / ReducedMotion / Appearance 由 DS 现有覆盖语义保持，
   主题层不覆盖它们（reduced-motion 时 DS 覆盖字典把三档时长清零/置 0ms）。
3. **失败回退**：层不完整/值类型不符 → seam 拒绝并保留上一层；`ThemeService` 回退 `newmanga-default`，
   仍失败则 `RevertToBuiltInLayer()`（DS `RevertPalette()`）。
4. **可复现**：59 键的值全部可由 `ThemePackage` + frozen `tokens.json` 派生；默认主题由生成器产出，
   `--check` 逐字节校验（不得手抄值）。
5. **变更流程**：任何增删键需先改冻结基线/契约（R-11），再同步本文件、`ThemeTokenKeys`、palette 单测
   与 evidence；Reviewer 以本表为白名单判据。R-21 已明确：DS 新增主题不变量派生色（如 Scrim）不自动
   进入主题层，需显式裁决。

## 5. 相关实现

- 合成：`apps/desktop-avalonia/src/NewManga.ThemeEngine/Palette/ThemePaletteComposer.cs`（`ThemeLayerKeyCount = 59`）
- 键常量：`NewManga.ThemeEngine/Models/ThemeTokenKeys.cs`（`ThemeLayer` = DS `ThemeLayerRequiredKeys`）
- 生成器：`NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen`（`--check`）
- 应用：`IThemeLayerSink`（Part B）→ DS `ApplyThemeLayer(ResourceDictionary, string)` seam
- 验证：`NewManga.ThemeEngine.Tests/ThemePaletteComposerTests.cs`（精确等于 59 键白名单/逐色语义一致）
- 证据：`verification/V11R-C-1/`
