# 10 组件清单（Fluent v1）

**用途**：FEA-05/06 实现时的组件边界与令牌依赖基线；每个组件必须能从本表找到：名称、所在页面、令牌依赖、状态、尺寸约束。
**原则**：优先复用 `NewManga.DesignSystem` 既有组件（`Surfaces.cs`/`Inputs.cs`/`Feedback.cs`/`Status.cs`/`Skeleton.cs`/`NmIcon.cs`）；Fluent 只新增**外观层**组件，不复制业务组件。

## 1. 布局组件（四页共用）

| 组件 | 用途 | 令牌 | 状态 |
|---|---|---|---|
| `TopBand` | 顶部命令条（空间/标题/命令/窗口） | `Nm.Surface.Raised`、`Nm.Elevation.1`、`Nm.Text.*` | 默认/紧凑（200% DPI） |
| `NavRail` | 左导航 rail | `Nm.Surface.Sunken`、`Nm.Accent.Subtle` | 折叠/展开 |
| `StatusBand` | 底部状态条 | `Nm.Surface.Raised`、`Nm.Status.*` | 默认/错误/运行中 |
| `SurfaceCard` | 通用卡片容器 | `Nm.Corner.Fluent.Md`、`Elevation.1`、`Nm.Surface.Raised` | 默认/hover/选中/禁用 |
| `Drawer` | 抽屉（检查器/详情/缩略图） | `Nm.Corner.Fluent.Lg`、`Elevation.2` | 开/关 |
| `Dialog` | 模态对话框 | `Nm.Corner.Fluent.Lg`、`Elevation.3` + 遮罩 | 默认/危险/加载 |
| `Toast` / `InfoBar` | 提示与非阻塞通知 | `Nm.Status.*`、`Elevation.3` | info/warn/error/success |
| `EmptyState` | 空态卡 | `Nm.Icon.*`、`Nm.Text.*`、主按钮 | 空/筛选后空/无权限 |
| `ErrorState` | 错误态卡 | `Nm.Status.Error`、`Elevation.1` | 可重试/不可恢复 |
| `Skeleton` | 骨架屏（复用既有） | `Skeleton.cs` | 形状/行/卡 |

## 2. 数据展示组件

| 组件 | 页面 | 令牌 | 备注 |
|---|---|---|---|
| `BookCard` | 书架 | `Corner.Fluent.Md`、`Elevation.1` | 封面 + 标题 + 状态徽标 |
| `BookRow` | 书架（列表视图） | `Corner.Fluent.Sm`、行高 40 | 紧凑模式 |
| `ChapterList` | 书架详情 | `Corner.Fluent.Sm` | 虚拟化滚动 |
| `PageThumbStrip` | 书架/阅读器 | `Corner.Fluent.Sm` | 横向滚动 |
| `RegionBox` | 工作台画布 | 1.5px 描边；锁角标 | hover/选中/锁定/冲突 |
| `StreamingThumb` | 工作台 film-strip | `Corner.Fluent.Sm` | 懒加载 |
| `BatchMatrix` | 工作台批量 | `Corner.Fluent.Sm`、`Nm.Status.*` | 七状态 + 吸顶表头 |
| `RunProjectionBar` | 工作台/控制台 | `Nm.Accent.*`、`Skeleton` | 投影驱动 |
| `ReaderPage` | 阅读器 | `Corner.None` | 单页/双页/滚动 |
| `ReaderProgressBar` | 阅读器 | `Nm.Accent.*` | 可拖动 |
| `SettingsGroup` | 设置 | `Corner.Fluent.Md`、`Elevation.1` | 卡片分组 |
| `SettingsField` | 设置 | `Corner.Fluent.Sm` | 标签+控件+错误 |

## 3. 交互组件

| 组件 | 令牌 | 状态 |
|---|---|---|
| `PrimaryButton` | `Nm.Accent.*`、`Corner.Fluent.Sm` | normal/hover/pressed/disabled/loading |
| `SecondaryButton` | `Nm.Surface.Raised` | 同上 |
| `DangerButton` | `Nm.Status.Error` outline | normal/hover/disabled |
| `IconButton` | `Corner.Fluent.Sm`、`Elevation.1` | normal/hover/checked |
| `ToggleSwitch` | `Nm.Accent.*` | on/off/disabled |
| `Slider` | `Nm.Accent.*` | normal/hover/disabled |
| `SegmentedControl` | `Corner.Fluent.Sm`、`Nm.Accent.Subtle` | 选中/未选 |
| `TabStrip` | 下划线 + `Nm.Accent.*` | 选中/未选/hover |
| `SearchField` | `Corner.Fluent.Sm` | 默认/聚焦/有值/清空 |
| `CommandPalette` | `Elevation.3`、`Corner.Fluent.Lg` | 空/结果/加载 |
| `ContextMenu` | `Elevation.2`、`Corner.Fluent.Md` | 默认/禁用项 |
| `Tooltip` | `Elevation.3` | 默认 |

## 4. 状态与动效依赖

- 所有 hover/pressed 动效遵循 `02-motion.md` §2.2（`reduce` 下仅颜色变化）。
- 所有浮层进入/退出遵循 `02-motion.md` §2.1（`reduce` 下 0ms）。
- 所有状态徽标同时有图标/文字，不只靠颜色（`03-accessibility.md` §4）。

## 5. 评审检查点

- [ ] 每个组件列出令牌依赖（无裸值）。
- [ ] 组件状态覆盖完整（至少 normal/hover/disabled；浮层含开/关）。
- [ ] 未复制业务组件（复用 DesignSystem 既有组件；Fluent 只做外观层）。
- [ ] 组件清单与四页正文引用的组件名一致。
