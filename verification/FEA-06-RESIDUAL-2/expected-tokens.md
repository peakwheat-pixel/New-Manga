# FEA-06-RESIDUAL-2 IN-2A 逐组期望令牌（expected-tokens，冻结口径）

> 由 `FluentResidual2StateEffectiveTests` 断言；PASS = **解析后属性值等于此处令牌解析值**（`ThemeTestHarness.ValueOf`/`ColorOf`，当前 light/dark 由 AppearanceCoordinator 主题决定）。
> 锚点来源：`doc/design/fluent-v1/01-design-tokens.md`、`03-accessibility.md`、`10-component-inventory.md` 与 `NewManga.DesignSystem/Styles/**` 样式。

| 组 | 状态 | 断言属性 | 期望令牌（解析后） |
|---|---|---|---|
| SurfaceCard | default/hover/selected/disabled | Background | `Nm.Color.Bg.Raised` |
| SurfaceCard | 同上 | BorderBrush / BorderThickness | `Nm.Color.Line.Subtle` / `Nm.Border.Hairline` |
| SurfaceCard | 同上 | CornerRadius / BoxShadow | `Nm.Corner.Fluent.Md` / `Nm.Elevation.1` |
| BookCard | default/disabled | Background / BorderBrush | `Nm.Color.Bg.Raised` / `Nm.Color.Line.Subtle` |
| BookCard | disabled | Opacity | `Nm.Opacity.Disabled` |
| BookRow | default/disabled | Background / BorderBrush | `Nm.Color.Bg.Canvas` / `Nm.Color.Line.Subtle` |
| BookRow | disabled | Opacity | `Nm.Opacity.Disabled` |
| PrimaryButton | default/disabled | Background / Foreground / CornerRadius | `Nm.Color.Accent.Base` / `Nm.Color.Accent.On` / `Nm.Corner.Fluent.Sm` |
| PrimaryButton | disabled | Opacity | `Nm.Opacity.Disabled` |
| SecondaryButton | default | Background / BorderBrush | `Nm.Color.Bg.Raised` / `Nm.Color.Line.Default` |
| DangerButton | default | Foreground / BorderBrush | `Nm.Color.Status.Failed` / `Nm.Color.Status.Failed` |
| IconButton | default/checked | （按 `Controls.Fluent.axaml` IconButton 规则） | 现状以样式令牌解析值为准，R2-011 待补状态通道 |
| ToggleSwitch | disabled | Opacity | `Nm.Opacity.Disabled` |
| Slider | normal/hover/disabled | Foreground | `Nm.Color.Accent.Base` / `Nm.Color.Accent.Hover` / `Nm.Opacity.Disabled`(disabled) |
| SegmentedControl | selected/unselected/hover/pressed | Background | `Nm.Color.Accent.Muted` / `Nm.Color.Bg.Overlay` / `Nm.Color.Bg.Overlay` / `Nm.Color.Accent.Muted` |
| TabStrip/TabItem | hover | Foreground | `Nm.Color.Accent.Hover` |
| SearchField | focus | BorderBrush / Background | `Nm.Color.Accent.Base` / `Nm.Color.Bg.Raised` |
| SettingsField | error/disabled | （按 `Grid.fluent-settings-field` + 错误样式） | 以样式令牌解析值为准 |
| RegionBox | hover | Background | `Nm.Color.Accent.Hover` |
| ContextMenu | disabled item | Opacity/Background | `Nm.Opacity.Disabled` / `Nm.Color.Bg.Panel` |
| Tooltip | opened | Background / BorderBrush / Foreground / BorderThickness | `Nm.Color.Bg.Overlay` / `Nm.Color.Line.Default` / `Nm.Color.Text.Primary` / `Nm.Border.Hairline` |
| AlertBanner | StatusKind 九值 | BorderBrush（muted 态） | `Nm.Color.Status.{Failed,Blocked,Stale}`；其余 `Nm.Color.Line.Default` |
| AlertBanner | 九值 | Foreground | 按 `StatusCatalog.ColorKey`；**NotStarted = D-14 特例**（类别：实际样式 `Nm.Color.Text.Secondary`，catalog 仍 `Text.Disabled`，待裁决） |
| EmptyState/ErrorState/Skeleton | default | （按设计 10 §3 令牌） | 以样式解析值为准 |
| ChapterList/PageThumbStrip/ReaderProgressBar | default | 容器/进度令牌 | `Nm.Color.Bg.Raised`/`Nm.Color.Accent.Base` 等按样式 |

> 说明：R2-011 指出 SurfaceCard hover/selected/disabled 与 IconButton checked 在 `Controls.Fluent.axaml` **无独立状态通道**（默认值即状态值）；本表如实标注，不以默认值冒充 PASS 的项按 R2-011 后续处置。
