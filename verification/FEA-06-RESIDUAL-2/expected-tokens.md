# FEA-06-RESIDUAL-2 R2R2 期望令牌与锚点

本表取代旧 expected-tokens 的默认值/主题声明。期望来自冻结设计 `doc/design/fluent-v1/10-component-inventory.md:11` 起的清单和当前样式；EFFECTIVE 仅指解析后属性断言，不代表视觉签署。旧矩阵 `verification/FEA-06-RESIDUAL-1/component-state-matrix.md:5` 定义 EFFECTIVE；其 :11、:17、:23–25、:30 是交叉锚点，原字节未改。

主题：页面和组件两套 light/dark 都重新加载 App.axaml 的真实资源清单，经 DesignSystemThemeManager.Initialize，传入 shell 的 themeManager；AppearanceCoordinator 保存到本卡 workspace 临时根。测试断言 Canvas token 不同，且非文本背景区域像素变化。IN-2A 的 ThemeTestHarness 有效属性测试独立解析同一键；不宣称只保存 Mode 就切换主题。

| 组 | 状态 | 有效属性 | 期望令牌键 | 样式 file:line | 证据级别 |
|---|---|---|---|---|---|
| SurfaceCard | default | Background/BorderBrush/CornerRadius/BoxShadow | Bg.Raised / Line.Subtle / Corner.Fluent.Md / Elevation.1 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:81` | EFFECTIVE |
| SurfaceCard | hover | BorderBrush | Nm.Color.Line.Default | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:90` | EFFECTIVE |
| SurfaceCard | selected | BorderBrush/BoxShadow | Nm.Color.Accent.Base / Nm.Elevation.2 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:93` | EFFECTIVE |
| SurfaceCard | disabled | Opacity | Nm.Opacity.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:97` | EFFECTIVE |
| BookCard | disabled | Opacity | Nm.Opacity.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:164` | EFFECTIVE |
| BookRow | disabled | Opacity | Nm.Opacity.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:187` | EFFECTIVE |
| PrimaryButton | disabled | Background/Foreground/Opacity | Nm.Color.Bg.Raised（Primary/Secondary）；Nm.Color.Text.Disabled / Nm.Opacity.Disabled；Danger 保留 Status.Failed 描边 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:282` | EFFECTIVE |
| SecondaryButton | disabled | Background/Foreground/Opacity | Nm.Color.Bg.Raised（Primary/Secondary）；Nm.Color.Text.Disabled / Nm.Opacity.Disabled；Danger 保留 Status.Failed 描边 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:308` | EFFECTIVE |
| DangerButton | disabled | Background/Foreground/Opacity | Nm.Color.Bg.Raised（Primary/Secondary）；Nm.Color.Text.Disabled / Nm.Opacity.Disabled；Danger 保留 Status.Failed 描边 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:328` | EFFECTIVE |
| IconButton | hover | Background | Nm.Color.Accent.Muted | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:342` | EFFECTIVE |
| IconButton | checked | Background/BorderBrush | Nm.Color.Accent.Muted / Nm.Color.Accent.Base | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:385` | EFFECTIVE |
| ToggleSwitch | disabled | Opacity | Nm.Opacity.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Selection.axaml:45` | EFFECTIVE |
| Slider | normal | Thumb.Background / rendered Border.Background（不是 Slider.Foreground 代替） | Nm.Color.Accent.Base | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:82` | EFFECTIVE |
| Slider | hover | Thumb.Background / rendered Border.Background（不是 Slider.Foreground 代替） | Nm.Color.Accent.Hover | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:85` | EFFECTIVE |
| Slider | disabled | Thumb.Background / rendered Border.Background（不是 Slider.Foreground 代替） | Nm.Color.Text.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:88` | EFFECTIVE |
| Slider | disabled | Opacity | Nm.Opacity.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:78` | EFFECTIVE |
| SegmentedControl | selected | Background / BorderBrush / Foreground（适用通道） | Nm.Color.Accent.Muted / Nm.Color.Accent.Base / Nm.Color.Text.Primary | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:54` | EFFECTIVE |
| SegmentedControl | unselected | Background / BorderBrush / Foreground（适用通道） | Transparent / Transparent / Nm.Color.Text.Secondary | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:48` | EFFECTIVE |
| SegmentedControl | hover | Background / BorderBrush / Foreground（适用通道） | Nm.Color.Bg.Overlay / Nm.Color.Text.Primary | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:60` | EFFECTIVE |
| SegmentedControl | pressed | Background / BorderBrush / Foreground（适用通道） | Nm.Color.Accent.Muted | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:64` | EFFECTIVE |
| TabItem | hover | Foreground | Nm.Color.Accent.Hover；PART_LayoutRoot=Nm.Color.Bg.Raised | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:94` | EFFECTIVE |
| TabStrip | default | Spacing | Nm.Space.2 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:264` | EFFECTIVE |
| SearchField | focus | 内边框不变；外部 nm-focus-ring.BorderBrush/BorderThickness | Nm.Color.Line.Default / Nm.Border.Hairline；外环 Nm.Color.Accent.Base / Nm.Border.Focus（键盘 Tab 焦点） | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Focus.axaml:9` | EFFECTIVE |
| SettingsField | error | 子 TextBox PART_BorderElement.BorderBrush | Nm.Color.Status.Failed | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Inputs.axaml:39` | EFFECTIVE |
| SettingsField | disabled | 子输入 Opacity | Nm.Opacity.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Inputs.axaml:44` | EFFECTIVE |
| SettingsField | 布局 | ColumnSpacing/RowSpacing | Nm.Space.3 / Nm.Space.2 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:259` | EFFECTIVE |
| RegionBox | hover | Background | Nm.Color.Accent.Hover | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:201` | EFFECTIVE |
| ContextMenu | disabled item | Opacity | Nm.Opacity.Disabled | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Navigation.axaml:44` | EFFECTIVE |
| Tooltip | opened | Background/BorderBrush/Foreground/BorderThickness | Nm.Color.Bg.Overlay / Nm.Color.Line.Default / Nm.Color.Text.Primary / Nm.Border.Hairline | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Navigation.axaml:48` | EFFECTIVE |
| ChapterList | default | Spacing | Nm.Space.2 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:191` | EFFECTIVE |
| StreamingThumb | default | Background/CornerRadius | Nm.Color.Bg.Raised / Nm.Corner.Fluent.Sm | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:207` | EFFECTIVE |
| ReaderPage | default | Background | Nm.Color.Bg.Sunken | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:236` | EFFECTIVE |
| ReaderProgressBar | default | Foreground | Nm.Color.Accent.Base | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:240` | EFFECTIVE |
| SettingsGroup | default | Background/Padding | Nm.Color.Bg.Raised / Nm.Padding.Card | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml:252` | EFFECTIVE |

D-11 四态映射是既有九值的证据分组，不新增 AlertBanner 变体。`Feedback.cs` 的 Severity→StatusCatalog.ClassName 驱动 class；`Status.cs` 的 StatusCatalog.ColorKey 为交叉锚点。Failed/Blocked/Stale 的表面通道有特化，其余保留 Panel/Line.Default，绝不把默认表面宣称为特化成功。

| 设计四态 | StatusKind | glyph 期望键 | 表面/边框 | 样式锚点 |
|---|---|---|---|---|
| success | Done | `Nm.Color.Status.Done` | `Nm.Color.Bg.Panel` / `Nm.Color.Line.Default` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:20`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:117` |
| error | Failed | `Nm.Color.Status.Failed` | `Nm.Color.StatusMuted.Failed` / `Nm.Color.Status.Failed` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:23`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:138` |
| warn | Blocked | `Nm.Color.Status.Blocked` | `Nm.Color.StatusMuted.Blocked` / `Nm.Color.Status.Blocked` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:26`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:130` |
| warn | Stale | `Nm.Color.Status.Stale` | `Nm.Color.StatusMuted.Stale` / `Nm.Color.Status.Stale` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:29`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:134` |
| info | Queued | `Nm.Color.Status.Queued` | `Nm.Color.Bg.Panel` / `Nm.Color.Line.Default` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:14`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:117` |
| info | Running | `Nm.Color.Status.Running` | `Nm.Color.Bg.Panel` / `Nm.Color.Line.Default` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:17`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:117` |
| info | Skipped | `Nm.Color.Status.Skipped` | `Nm.Color.Bg.Panel` / `Nm.Color.Line.Default` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:32`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:117` |
| info | NotStarted | `Nm.Color.Text.Secondary` | `Nm.Color.Bg.Panel` / `Nm.Color.Line.Default` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:35`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:117` |
| warn | Locked | `Nm.Color.Status.Blocked` | `Nm.Color.Bg.Panel` / `Nm.Color.Line.Default` | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Status.axaml:39`；`apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Custom.axaml:117` |

D-14 例外保持：NotStarted glyph=Text.Secondary，catalog=Text.Disabled。裁决 A 已发布（`doc/reviews/ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md`），实现待 `D-14-STATUS-COLOR-FIX`；本卡九值交叉断言继续特判，不写 D-14 达成。

像素与覆盖：见 `visuals/visual-inventory.md`；每图明确 HEAD/theme/frontend/frame/SHA256。每项签署均待独立 Reviewer（NOT_RUN）。StatusBand 错误/运行专用投影、原生 200% DPI/a11y 不用默认帧代替，见 Handoff 限制。

R2R2-016：实际粒子执行器已迁至 Views/Fluent 内，尺寸变化才定位，帧内只写 Opacity/RenderTransform；进度为归一化传入值。域外 Controls/FluentUi.cs 的旧工厂/using 未改且不再被播放路径调用，其死代码清理为 NOT_RUN（需 DSH 扩域）。

补充实际模板通道：ReaderProgressBar.Theme 显式解析基类 ProgressBar 的既有 ControlTheme，PageThumbStrip.Theme 显式解析 ItemsControl，ItemsPanel 使用横向 StackPanel/Space.2。属性和真实内容回归在 ReaderProgressAndThumbStrip_ResolveRealTemplatesAndContent；捕获另断言像素颜色种类>2，避免有 Value/items 仍出空白。

Slider 的 PART_DecreaseButton.Background 绑定父 Slider.Foreground（normal=Accent.Base，hover=Accent.Hover），disabled=Text.Disabled；FluentMotionScope 不再给模板 RepeatButton 叠加通用按钮 tween。Fluent 按钮 hover/pressed 同时覆盖模板 PART_Root 背景，避免只有公开属性变色而实际像素仍走通用 ControlTheme。

IN-1.1 渐变仍仅选既有 Bg 令牌：Canvas→Overlay（此前 Canvas→Sunken 的暗色差异不足）；循环仍为 8s，reduce 静态。decor shelf 原像素裁切 [216,95,1048,720]，viewport=1280x900；中间帧采样 2000ms，frame 明确 intermediate-2000ms，而非虚标精确半周期。生产时钟测试另实采 0/4000/7950ms。
