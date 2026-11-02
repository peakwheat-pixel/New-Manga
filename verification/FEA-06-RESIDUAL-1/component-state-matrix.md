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
| BookCard / BookRow | 默认/hover/pressed/selected/disabled | BookCard：hover=Bg.Overlay、pressed/selected=Accent.Muted；BookRow：Bg.Canvas→hover Bg.Overlay→pressed/selected Accent.Muted（指针合成/类切换）；点击/选择行为（Shelf 既有测试） | **EFFECTIVE**（两类的 hover/pressed/selected） | disabled 视觉 NOT_RUN |
| ChapterList / PageThumbStrip | 默认/选中/滚动 | 选择/滚动功能测试（Batch A） | COMMAND | 视觉 NOT_RUN |
| RegionBox | hover/选中/锁定/冲突 | 选中/锁定功能（Workbench 既有测试）；冲突数据 B-7 BLOCKED | COMMAND | hover 视觉 NOT_RUN |
| StreamingThumb / BatchMatrix / RunProjectionBar | 七状态/吸顶/投影 | BatchMatrix 数据绑定 B-2 BLOCKED；骨架样式声明 | DECLARED | 数据面由 B-2 承担 |
| ReaderPage / ReaderProgressBar | 单页/双页/滚动、可拖动 | 阅读器分页/进度功能测试（Batch A）；双页/滚动数据 B-3 BLOCKED | COMMAND | 视觉 NOT_RUN |
| SettingsGroup / SettingsField | 默认/错误/禁用 | 设置页字段/错误/禁用功能测试（Batch A） | COMMAND | 视觉 NOT_RUN |
| PrimaryButton | normal/hover/pressed/disabled/loading | `FluentComponentPointerStatesTests`：normal=Accent.Base、hover=Accent.Hover、pressed=Accent.Base（指针合成）；disabled=Opacity.Disabled 且 IsEffectivelyEnabled=false；几何/前景见 Effective 测试 | **EFFECTIVE** | loading 态视觉 **NOT_RUN** |
| SecondaryButton | normal/hover/pressed/disabled | `FluentComponentPointerStatesTests`：normal=Bg.Raised、hover=Bg.Overlay、pressed=Accent.Muted（指针合成） | **EFFECTIVE** | disabled 视觉 NOT_RUN；设置页行为测试另见 Batch A |
| DangerButton | normal/hover/disabled | normal=Status.Failed 前景/描边 + Hairline；hover=StatusMuted.Failed 背景（指针合成） | **EFFECTIVE** | disabled 视觉 NOT_RUN |
| IconButton | normal/hover/checked | 声明 hover/pressed/disabled；点击行为（页面测试） | DECLARED | checked 视觉 NOT_RUN |
| ToggleSwitch | on/off/disabled | Inputs 既有测试 + 声明 | DECLARED | disabled 视觉 NOT_RUN |
| Slider | normal/hover/disabled | 本批新增声明（Foreground Accent.Base/Hover、disabled 透明度） | DECLARED | 无有效属性断言 → 视觉格 NOT_RUN |
| SegmentedControl | 选中/未选 | 本批新增 hover/pressed/disabled 声明；设置页分段选择行为 | DECLARED | 选中视觉由既有页面测试覆盖，无像素断言 |
| TabStrip / TabItem | 选中/未选/hover | TabItem：未选 Foreground=Text.Secondary；选中=Text.Primary；Accent pipe（既有测试） | **EFFECTIVE** | hover 视觉 NOT_RUN |
| SearchField | 默认/聚焦/有值/清空 | 声明；搜索行为（Shelf 既有测试） | DECLARED | 聚焦视觉 NOT_RUN |
| CommandPalette | 空/结果/加载 | `FluentCommandPaletteFocusTests`：打开后焦点进入搜索框、Esc 关闭后焦点返还触发按钮；复用 Dialog 样式 | COMMAND/FOCUS | 结果/加载数据态 NOT_RUN |
| ContextMenu | 默认/禁用项 | 列表上下文菜单构建（Shelf 既有测试）；声明 | COMMAND | 禁用项视觉 NOT_RUN |
| Tooltip | 默认 | 声明；Tooltip 设置逻辑（Settings/Reader 既有） | DECLARED | 视觉 NOT_RUN |
| 焦点环（所有可聚焦控件） | 键盘焦点/高对比 | 2px↔3px 有效几何（`FocusRingHighContrastTests`）、浮层焦点移入/返还（`I11_LeaveOverlay...`/`FluentCommandPaletteFocusTests`）、隐藏控件不可聚焦（`FocusOrderResidualTests`）、Current 往返资源不污染（`FluentCurrentComparisonTests`） | **EFFECTIVE/FOCUS** | 指针焦点不画环；四页各 1 场景（`FluentFocusPageCoverageTests`） |
| disabled 命令零触发 | — | `FluentDisabledAutomationTests`：自动化 Invoke 抛 `ElementNotEnabledException`、Click 0 次、Command 0 次执行；`CanExecute=false` | **EFFECTIVE/COMMAND** | 非自动化路径的鼠标点击禁用语义由 Avalonia 输入层保证（未做像素点击） |

## 结论（诚实口径，impl-r1 返修后 2026-11-03 更新）

- I-4 的**有效属性/焦点**子集已达成（Primary/Secondary/Danger/BookCard/BookRow 的指针态、SurfaceCard/Dialog/TabItem、disabled 零触发、命令面板结果/空态、焦点环）；
- hover/pressed 已用 headless 指针合成升级为 EFFECTIVE；loading/checked 等**剩余视觉格**标 NOT_RUN，不以声明存在计 PASS；
- 组件矩阵其余行按 DECLARED/COMMAND 登记，缺口（Toast severity 组合、CommandPalette 结果态、disabled 命令零触发、视觉格）留待后续批次或独立视觉复核。


## 当前快照（R2-005，2026-11-03）

> 本节取代前文“当前/最新”口径；前文及其1194/1195/1197等计数全部保留为历史快照，不自动升级为当前证据。历史impl-r2基线为 **1213/0/57**；本轮最新为 **1233/0/57**。
> 被测实现 head：`8b39b13982cfaae9e7606fe62f13353700be68fe`（`8b39b1398`）；后续交付只追加证据/Handoff，不改源码测试字节。证据：`impl-r2-rework-verification.log`；四条验收命令原文/输出/EXIT及57条skip逐项原因均在其中。
> build / 无过滤全量test / check.ps1 / verify_pins.ps1：**EXIT=0 / 0 / 0 / 0**；check PASS(3既有warnings)，pins **15/15**；TokenGen/ThemeGen --check 均EXIT=0。App=614/0/7、DesignSystem=97/0/0；合计1233 passed / 0 failed / 57 skipped（总1290），比基线+20（App+16、DS+4）。

本节按有效属性/真实输入/命令/焦点证据登记，**EFFECTIVE不等于像素视觉验收**。NOT_RUN细分：①普通headless可验证但尚无断言；②原生/逐像素未跑。D-8属于待裁决且本体未实现，不能算已批准豁免。

| 组件/状态组 | 当前有效证据 | 尚未覆盖的适用格 |
|---|---|---|
| TopBand/NavRail/StatusBand | 布局/断点既有行为回归 | 逐像素视觉NOT_RUN |
| SurfaceCard | Raised/边框/Elevation/圆角有效属性 | hover/selected/disabled适用视觉格NOT_RUN，未新增普通属性断言 |
| Drawer / Dialog | Shelf抽屉/对话框、Settings离开/普通确认的200ms进入、160ms退出及scrim160ms，full/reduce/navigation-off真实过程断言 | 危险/loading外观、抽屉焦点完整遍历及原生视觉NOT_RUN |
| Toast / InfoBar | Blocked的StatusMuted背景既有断言 | 其余severity组合有效属性NOT_RUN（可headless验证的测试缺口） |
| EmptyState / ErrorState / Skeleton | 页面功能、Skeleton既有属性回归 | 逐像素视觉NOT_RUN |
| BookCard / BookRow | normal/hover/pressed/selected真实指针与有效颜色；既有选择行为 | disabled视觉逐格NOT_RUN，不影响通用disabled零命令触发已验证事实 |
| ChapterList / PageThumbStrip | 选择/滚动行为 | 逐像素视觉NOT_RUN |
| RegionBox | 选择/锁定行为 | hover有效属性NOT_RUN；冲突数据B-7 BLOCKED |
| StreamingThumb / BatchMatrix / RunProjectionBar | 九行视觉骨架/声明 | 逐状态有效属性NOT_RUN；真实数据绑定B-2 BLOCKED |
| ReaderPage / ReaderProgressBar | 分页/进度行为；顶底条80/159/160ms、真实交互后2s及detach断言 | 双页第二图/滚动数据B-3 BLOCKED；像素视觉NOT_RUN |
| SettingsGroup / SettingsField | 分组、错误/只读行为；动态Providers/Backup重建后hover/pressed过程 | 错误/disabled全部有效外观格NOT_RUN |
| Primary / Secondary / Danger Button | 既有normal/hover/pressed颜色、几何/前景/禁用透明度及零命令；本轮动态按钮120ms颜色插值与90ms缩放同源，分类切换/再次重建后仍正确 | loading完整外观、每种组件的disabled视觉格NOT_RUN |
| IconButton | 页面点击/pressed缩放、Fluent局部持续配置 | hover/checked各自有效颜色NOT_RUN（可headless验证） |
| ToggleSwitch | 既有on/off功能 | disabled有效属性NOT_RUN（可headless验证） |
| Slider | 样式声明 | normal/hover/disabled有效属性NOT_RUN（可headless验证） |
| SegmentedControl | 分段选择行为 | 选中/未选/hover/pressed全部有效外观格NOT_RUN |
| TabStrip / TabItem | 已选/未选前景与accent pipe；180ms切换消费既有断言 | hover有效属性NOT_RUN |
| SearchField | 搜索/清空行为、页面焦点 | 聚焦等全部有效外观格NOT_RUN |
| CommandPalette | **结果/空态已验证**：真实命令行数>0→不匹配查询0→清空后>0（FluentCommandPaletteFocusTests）；焦点移入/返还；200/160ms既有时序断言 | loading态NOT_RUN，不再错误登记结果态为缺口 |
| ContextMenu / Tooltip | 构建/绑定既有功能 | 禁用项/Tooltip有效视觉属性NOT_RUN |
| 焦点环 | 新FocusRingOffsetTests：offset+stroke外宽高/四边gap、标准/高对比实时切换与滚动裁剪；Fluent=1，Current=0对照；既有四页焦点/返还回归 | 完整Tab遍历、原生a11y/200%DPI NOT_RUN，B-5仍BLOCKED |
| disabled命令零触发 | **已验证**：FluentDisabledAutomationTests的Invoke异常、Click=0、Command=0、CanExecute=false；不再列为未完成 | 原生像素对照NOT_RUN |

I-4整体仍PARTIAL；剩余普通有效属性格不能称为“硬件视觉阻塞”。I-5 decorative本体仍D-8未裁决、未实现。B-5原生桌面/DPI/a11y/视觉矩阵与最新PNG opt-in为NOT_RUN。旧快照中的“命令面板结果态、disabled零触发缺口”由本节明确取代，保留旧字节只为历史溯源。
