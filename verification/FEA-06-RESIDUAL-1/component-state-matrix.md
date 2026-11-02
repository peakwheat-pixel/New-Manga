# FEA-06-RESIDUAL-1 组件 × 状态矩阵（I-4 证据）

> 依据：`doc/design/fluent-v1/10-component-inventory.md` §1–§3（FROZEN v1.0.0）。
> 口径（scope v3 I-4）：断言**有效属性/命令/焦点行为**；无法 headless 验证的视觉格标 **NOT_RUN**，不得以「选择器存在」计视觉 PASS。
> 图例：**EFFECTIVE** = 断言控件解析后的有效属性值（对齐所有权）；**COMMAND** = 断言命令/行为零触发或动作；**FOCUS** = 断言焦点移入/返还/排除；**DECLARED** = 样式已声明但未做有效属性断言（仅登记）；**NOT_RUN** = 视觉/hover/pressed 等无法在 headless 断言。
> 测试位置：`tests/NewManga.DesignSystem.Tests/FluentComponentStateEffectiveTests.cs`（EFFECTIVE）、`.../FluentComponentStateCoverageTests.cs`（声明覆盖，作为辅助索引）、`tests/NewManga.App.Tests/FluentResidualSettingsLeaveTests.cs`/`FocusOrderResidualTests.cs`/`FluentMotionResidualTests.cs`（FOCUS/外溢）、`StandardControlsThemeTests.cs`（TabItem 选择态）。

| 组件 | 适用状态（清单） | 本批断言 | 状态 | 备注 |
|---|---|---|---|---|
| TopBand / NavRail / StatusBand | 默认/紧凑/折叠 | 页面级布局与断点测试（Batch A） | DECLARED | 结构样式 + 现有页面测试；无像素断言 |
| SurfaceCard | 默认/hover/选中/禁用 | Background=Raised、BorderThickness=Hairline、BoxShadow=Elevation.1、Corner=Corner.Fluent.Md | **EFFECTIVE** | hover/选中视觉 NOT_RUN |
| Drawer | 开/关 | 打开/关闭行为（Shelf 回收站既有测试） | COMMAND | Elevation.2 声明；开合动画视觉 NOT_RUN |
| Dialog | 默认/危险/加载 | Background/Border/BoxShadow=Elevation.3/Corner=Corner.Fluent.Lg/ZIndex=Modal | **EFFECTIVE** | 危险/加载态视觉 NOT_RUN |
| Toast / InfoBar | info/warn/error/success | AlertBanner severity：既有 `CustomControlsTests` 断言 Blocked 的 StatusMuted 背景 + 类名；其余 severity 声明存在于 `Controls.Custom.axaml` | DECLARED（Blocked 背景已断言） | 四种 severity 组合未逐格有效属性断言（纯视觉格 NOT_RUN） |
| EmptyState / ErrorState | 空/筛选空/无权限/可重试 | 页面空态/错误态功能测试（Batch A/B） | COMMAND | 视觉 NOT_RUN |
| Skeleton | 形状/行/卡 | DesignSystem Skeleton 既有测试 | EFFECTIVE（既有） | 本批未改 |
| BookCard / BookRow | 默认/hover/pressed/selected/disabled | 选择/点击行为（Shelf 既有测试）；样式声明 hover/pressed/disabled | DECLARED | hover/pressed 视觉 **NOT_RUN** |
| ChapterList / PageThumbStrip | 默认/选中/滚动 | 选择/滚动功能测试（Batch A） | COMMAND | 视觉 NOT_RUN |
| RegionBox | hover/选中/锁定/冲突 | 选中/锁定功能（Workbench 既有测试）；冲突数据 B-7 BLOCKED | COMMAND | hover 视觉 NOT_RUN |
| StreamingThumb / BatchMatrix / RunProjectionBar | 七状态/吸顶/投影 | BatchMatrix 数据绑定 B-2 BLOCKED；骨架样式声明 | DECLARED | 数据面由 B-2 承担 |
| ReaderPage / ReaderProgressBar | 单页/双页/滚动、可拖动 | 阅读器分页/进度功能测试（Batch A）；双页/滚动数据 B-3 BLOCKED | COMMAND | 视觉 NOT_RUN |
| SettingsGroup / SettingsField | 默认/错误/禁用 | 设置页字段/错误/禁用功能测试（Batch A） | COMMAND | 视觉 NOT_RUN |
| PrimaryButton | normal/hover/pressed/disabled/loading | normal Effective（Accent.Base/Accent.On/Corner/ControlHeight）；disabled Effective（Opacity.Disabled 且 IsEffectivelyEnabled=false） | **EFFECTIVE** | hover/pressed/loading 视觉 **NOT_RUN** |
| SecondaryButton | normal/hover/pressed/disabled | 声明覆盖 + 设置页按钮行为 | DECLARED | hover/pressed 视觉 **NOT_RUN** |
| DangerButton | normal/hover/disabled | normal Effective（Status.Failed 前景/描边、Hairline） | **EFFECTIVE** | hover/disabled 视觉 **NOT_RUN** |
| IconButton | normal/hover/checked | 声明 hover/pressed/disabled；点击行为（页面测试） | DECLARED | checked 视觉 NOT_RUN |
| ToggleSwitch | on/off/disabled | Inputs 既有测试 + 声明 | DECLARED | disabled 视觉 NOT_RUN |
| Slider | normal/hover/disabled | 本批新增声明（Foreground Accent.Base/Hover、disabled 透明度） | DECLARED | 无有效属性断言 → 视觉格 NOT_RUN |
| SegmentedControl | 选中/未选 | 本批新增 hover/pressed/disabled 声明；设置页分段选择行为 | DECLARED | 选中视觉由既有页面测试覆盖，无像素断言 |
| TabStrip / TabItem | 选中/未选/hover | TabItem：未选 Foreground=Text.Secondary；选中=Text.Primary；Accent pipe（既有测试） | **EFFECTIVE** | hover 视觉 NOT_RUN |
| SearchField | 默认/聚焦/有值/清空 | 声明；搜索行为（Shelf 既有测试） | DECLARED | 聚焦视觉 NOT_RUN |
| CommandPalette | 空/结果/加载 | 打开/关闭行为测试（shell 既有测试）；复用 Dialog 样式 | COMMAND | 结果/加载数据态 NOT_RUN |
| ContextMenu | 默认/禁用项 | 列表上下文菜单构建（Shelf 既有测试）；声明 | COMMAND | 禁用项视觉 NOT_RUN |
| Tooltip | 默认 | 声明；Tooltip 设置逻辑（Settings/Reader 既有） | DECLARED | 视觉 NOT_RUN |
| 焦点环（所有可聚焦控件） | 键盘焦点/高对比 | 2px↔3px 有效几何（`FocusRingHighContrastTests`）、浮层焦点移入/返还（`I11_LeaveOverlay...`）、隐藏控件不可聚焦（`FocusOrderResidualTests`） | **EFFECTIVE/FOCUS** | 指针焦点不画环；四页至少各 1 场景由页面键盘测试覆盖 |
| disabled 命令零触发 | — | 未新增自动化（部分 I-10/I-3 禁用写入测试覆盖） | **NOT_RUN** | 后续以 `ShellCommand` CanExecute 注入补齐 |

## 结论（诚实口径）

- I-4 的**有效属性/焦点**子集已达成（PrimaryButton/DangerButton/SurfaceCard/Dialog/TabItem/焦点环）；
- hover/pressed/loading/checked 等**纯视觉伪类格**在本环境不可复现，全部标 **NOT_RUN**，不以声明存在计 PASS；
- 组件矩阵其余行按 DECLARED/COMMAND 登记，缺口（Toast severity 组合、CommandPalette 结果态、disabled 命令零触发、视觉格）留待后续批次或独立视觉复核。
