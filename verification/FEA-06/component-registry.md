# FEA-06 Fluent 组件登记表

基线：`doc/design/fluent-v1/10-component-inventory.md`（FROZEN v1.0.0）。
实现：`Controls.Fluent.axaml`、`FluentComponents.cs`、既有 `Surfaces.cs` / `Inputs.cs` / `Feedback.cs`。

## AC6 清单（20 个组件）

| 组件 | 页面 | 令牌依赖 | 状态实现 / 证据 | 测试 |
|---|---|---|---|---|
| SurfaceCard | 四页 | `Nm.Color.Bg.Raised`、`Nm.Color.Line.Subtle`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Md`、`Nm.Padding.Card` | normal；hover/pressed/disabled 状态未覆盖 | `FluentComponentsTests`（类标识） |
| Drawer | Shelf / Workbench | `Nm.Color.Bg.Raised`、`Nm.Color.Line.Subtle`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Lg`、`Nm.Size.Drawer`、`Nm.ZIndex.Drawer` | open/closed；headless 验证可见状态 | `FluentComponentsTests` |
| Dialog (`FluentDialog`) | 四页 | `Nm.Color.Bg.Raised`、`Nm.Color.Line.Strong`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Lg`、`Nm.Padding.Section`、`Nm.ZIndex.Modal` | open/closed；headless 验证可见状态 | `FluentComponentsTests` |
| EmptyState | Shelf / Workbench / Reader / Settings | `Nm.FontSize.*`、`Nm.Color.Text.*`、按钮 `Nm.Color.Accent.*` | 空态、带动作/无动作；复用 DesignSystem 控件 | `FluentPageTests` 状态用例 |
| ErrorState (`AlertBanner`) | 四页 | `Nm.Color.Status.*`、`Nm.Color.Text.*`、`Nm.Border.*` | severity、可重试/只读；LiveSetting 在设置通知区启用 | `FluentPageTests` 状态用例 |
| Toast / InfoBar (`AlertBanner`) | 四页 | `Nm.Corner.Fluent.Md`、`Nm.Padding.Control`、`Nm.Color.Status.*` | info/warn/error/locked 语义；复用 DesignSystem 控件 | `FluentPageTests` 状态用例 |
| BookCard | Shelf | `Nm.Color.Bg.Raised/Overlay`、`Nm.Color.Line.Subtle`、`Nm.Color.Accent.*`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Md`、`Nm.Padding.Card` | normal/hover/pressed/selected/disabled | `ShelfPage_EmptyHostFailure...`；全量设计规则 |
| BookRow | Shelf | `Nm.Color.Bg.Canvas/Overlay`、`Nm.Color.Line.Subtle`、`Nm.Color.Accent.*`、`Nm.Corner.Fluent.Sm`、`Nm.Padding.ControlSm`、`Nm.Size.RowNormal` | normal/hover/pressed/selected/disabled | `ShelfPage_EmptyHostFailure...`；全量设计规则 |
| RegionBox | Workbench | `Nm.Color.Accent.Muted/Hover/Base`、`Nm.Border.Focus`、`Nm.Corner.None`、`Nm.Padding.Snug`、`Nm.Focus.Ring.Color` | normal/hover/selected；pressed/disabled/locked/conflict 状态尚缺 | `WorkbenchPage_UnselectedState...` |
| BatchMatrix | Workbench | `Nm.Color.Bg.Sunken`、`Nm.Padding.Panel` | 可滚动容器；状态矩阵尚未绑定运行投影 | `FluentComponentsTests`（类标识） |
| RunProjectionBar | Workbench | `Nm.Color.Bg.Raised`、`Nm.Color.Accent.Base`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Md`、`Nm.Padding.Control` | 空投影提示；活动 Run 投影及控制尚未接入 | `FluentComponentsTests`（类标识） |
| SettingsGroup | Settings | `Nm.Color.Bg.Raised`、`Nm.Color.Line.Subtle`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Md`、`Nm.Padding.Card` | normal | `SettingsPage_HostUnavailable...` |
| SettingsField | Settings | `Nm.Space.3`、`Nm.Space.2`、`Nm.Padding.Snug` | normal、help/error text；禁用随 Host 只读策略 | `SettingsPage_HostUnavailable...` |
| PrimaryButton | 四页 | `Nm.Color.Accent.Base/Hover/On`、`Nm.Color.Bg.Raised`、`Nm.Color.Text.Disabled`、`Nm.Opacity.Disabled`、`Nm.Corner.Fluent.Sm`、`Nm.Padding.Control`、`Nm.Size.ControlHeight` | normal/hover/pressed/disabled | `FluentPageTests` + `DesignRulesTests` |
| SecondaryButton | 四页 | `Nm.Color.Bg.Raised/Overlay`、`Nm.Color.Accent.Muted`、`Nm.Color.Line.Default`、`Nm.Color.Text.*`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Sm`、`Nm.Padding.Control`、`Nm.Size.ControlHeight` | normal/hover/pressed/disabled | `FluentPageTests` + `DesignRulesTests` |
| DangerButton | Shelf / Workbench / Settings | `Nm.Color.Bg.Raised`、`Nm.Color.Status.Failed/Muted.Failed`、`Nm.Color.Bg.App`、`Nm.Color.Text.Disabled`、`Nm.Opacity.Disabled`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Sm`、`Nm.Padding.Control`、`Nm.Size.ControlHeight` | normal/hover/pressed/disabled | `FluentPageTests` + `DesignRulesTests` |
| IconButton | 四页 | `Nm.Color.Bg.Raised`、`Nm.Color.Line.Subtle`、`Nm.Color.Accent.Muted/Base`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Sm`、`Nm.Padding.Icon`、`Nm.Size.ControlHeight` | normal/hover/pressed/disabled；图标复用 `NmIcon` | `FluentPageTests` + `DesignRulesTests` |
| SearchField | Shelf / Settings | 复用 DesignSystem `SearchField`；文本/边框/焦点取既有 `Nm.*` 输入令牌 | 默认、聚焦、输入和清空；复用而不复制 | `FluentPageTests`；全量设计规则 |
| TabStrip | Workbench | `Nm.Space.2`；次级按钮基础/hover/pressed/disabled 依赖 `Nm.Color.Bg.Raised/Overlay`、`Nm.Color.Line.Default`、`Nm.Color.Text.Primary/Disabled`、`Nm.Color.Accent.Muted/Base`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Sm`、`Nm.Padding.Control`、`Nm.Size.ControlHeight`、`Nm.Opacity.Disabled` | 已接入页面/批量/控制台三视图；`Button.fluent-secondary.selected` 实际应用 Accent.Muted 背景、Accent.Base 边框、Text.Primary 前景和 Fluent.Sm 圆角；切换时恰有一个 Tab 选中；hover/键盘切换未覆盖 | `FluentPageTests`（状态 class 与令牌视觉属性） |
| SegmentedControl | Shelf | 复用 DesignSystem `SegmentedControl`；背景/边框/选中态取既有 `Nm.*` 输入令牌 | 已接入书架网格/列表切换；选中/未选；headless 树含两个选项 | `FluentPageTests`；`FluentComponentsTests` |

## 页面支撑组件

| 组件 | 页面 | 令牌依赖 | 状态 / 测试 |
|---|---|---|---|
| ChapterList | Shelf | `Nm.Space.2` | 已接入作品详情章节选择列表；随书籍选择生成 |
| PageThumbStrip | Shelf / Reader | `Nm.Corner.Fluent.Sm`、`Nm.Color.Accent.*` | 页选择；`FluentComponentsTests` 类标识 |
| StreamingThumb | Workbench | `Nm.Color.Bg.Raised`、`Nm.Color.Line.Subtle`、`Nm.Border.Hairline`、`Nm.Corner.Fluent.Sm`、`Nm.Padding.Snug` | 占位缩略图；真实流式加载尚未接入 |
| ReaderPage | Reader | `Nm.Color.Bg.Sunken`、`Nm.Corner.None` | 单图页面；双页模式尚未呈现第二页 |
| ReaderProgressBar | Reader | `Nm.Color.Accent.Base`、`Nm.Color.Bg.Sunken`、`Nm.Corner.Fluent.Sm` | 可读进度；拖动跳页尚未接入 |
| Skeleton | 四页 | 复用 DesignSystem `Skeleton` 变体 | 6 个书架封面、页面/设置骨架；`FluentPageTests` |

### 返修登记与剩余口径

- `Nm.Elevation.1/2/3` 已冻结但当前 Fluent 样式未消费；组件以 1px 边框表达层级。后续样式 Task 再补阴影，避免本轮扩大视觉改动。
- 本次返修审查的页面归属按当前接线填写：TabStrip、SegmentedControl、ChapterList 均已由相应页面实际使用；其他组件继续按各自当前状态和缺口登记。
- 新增 `FluentTokenResourceTests` 扫描 DesignSystem/App Styles 与 Fluent View XAML 中的 `{DynamicResource Nm.*}` 并通过 Avalonia 应用资源栈解析，防止悬空令牌回归。

AC6 结论：已登记并实现全部 20 个基线项目，令牌存在性、主要按钮和书卡状态有自动化覆盖；每个组件完整覆盖 `normal/hover/pressed/disabled` 的要求尚未全部满足（见逐行缺口），因此任务卡标记 `PARTIAL`。
