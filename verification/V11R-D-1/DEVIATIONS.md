# V11R-D-1 偏差记录（DEVIATIONS）

记录实现相对**冻结基线**（`tokens.json`、`DESIGN_SYSTEM.md`）与**冻结契约**
（`doc/plan/V11R_AVALONIA_CONTRACT.md`）的已知偏差、缺口与派生扩展。冻结文件一律未修改（R-09 修订由
Lead 裁决并在 DECISION_LOG 记录）；需要基线裁决的条目已/将报 Lead。

## D-1 冻结基线缺失 high-contrast / density / 派生尺寸令牌（派生扩展）

`tokens.json` 只定义 dark / light 两套配色与单一尺寸刻度，没有 contrast 与 density 令牌。契约 §4 的
`ContrastMode` / `Density` 需要可切换集合，故本任务提供**派生产物**（不修改冻结文件）：

- `Themes/Tokens.HighContrast.axaml`：完整 35 色高对比盘（ThemeDictionaries: Dark/Light），背景五级保持
  冻结值，前后景按 DESIGN_SYSTEM §2.3 派生（正文 ≥7:1、状态 ≥4.5:1）。R-14 登记为**规则派生扩展，非第二
  真值源**；生成器在生成期断言这些下限（`ValidateHighContrastContrast`），超出即 fail。
- `Themes/Density.Compact.axaml` / `Density.Spacious.axaml`：只覆盖控件高度/行高/内边距；Comfortable =
  冻结 token 原值。生成期断言 Compact < Comfortable < Spacious（`ValidateDensityMonotonic`）。
- 派生全局键（`TokenMap.DerivedGlobals` 记录推导依据）：`Nm.Size.ControlHeight(28/Sm24)`、
  `Nm.Padding.*`、`Nm.Icon.Stroke(1.25)`、`Nm.Icon.SizeSmall(16)`、`Nm.Motion.Enabled`、
  `Nm.Motion.Duration.Slow(220ms，R-15 新增)`、`Nm.LineHeight.*`、`Nm.TextLineBox.*`、
  `Nm.Size.Marker/MarkerCore/ScrollBar`、`Nm.Color.Scrim`、`Nm.Opacity.Disabled(0.4)`。
- 建议：下一版设计基线把 high-contrast / density 正式纳入 `tokens.json`，届时删除对应派生表。

## D-2 Motion 时长以冻结 token 为准（Lead 裁决 R-10）

契约 §2.2 示例曾写 `Nm.Motion.Duration.Normal(0:0:0.15)`；冻结 `tokens.json` 为 `140ms`。按
V11R_PROGRAM §1.4「tokens.json 为唯一视觉权威」，资源值取 `00:00:00.1400000`。Lead 已裁决 R-10：契约
示例为笔误、以 tokens.json 为准并修正契约；R-15 再新增 `Slow(220ms)` 扩展。DS 无需改动。

## D-3 标准盘对比度缺口 → 已按 Lead 裁决 R-09 修订冻结令牌

实测（WCAG 2.1，对 `bg.panel`）发现冻结标准盘有 5 处低于 DESIGN_SYSTEM §2.3 下限。Lead 裁决 **R-09**：
规范条款优先于数据，修订 `tokens.json` 数据（记录于 `doc/design/redesign-v1/40-fusion/DECISION_LOG.md`
§5），不改规范；高对比模式保留为更强分离档。修订后标准盘已全部达标，`ContrastTokenTests` 为合规断言：

| 令牌 | 修订前 | 修订后 |
|---|---|---|
| dark `status.queued` | `#5C6169`（2.74:1） | `#8A9099`（5.31:1） |
| dark `status.skipped` | `#4A4F55`（2.07:1） | `#82878E`（4.72:1） |
| dark `status.failed` | `#C9634F`（4.38:1） | `#CC6A57`（4.69:1） |
| light `status.skipped` | `#8A8F94`（3.26:1） | `#73777B`（4.51:1） |
| light `accent.base`（白字） | `#B4791F`（3.69:1） | `#96651A`（5.03:1） |
| light `accent.hover/active` | `#9C6717`/`#8A5A12` | `#7F5515`/`#6B470F`（明度仍单调） |
| light `accent.muted/ring` | `rgba(180,121,31,…)` | `rgba(150,101,26,…)`（同色相） |

残余：light `status.skipped` 对 `bg.canvas`（#F4F3F0）4.07:1（<4.5）；组件内状态文字/符号落在
`bg.panel`/`bg.raised`/`statusMuted` 上（对 panel 4.51:1 达标），且始终三编码（色+符号+文字）。高对比模式
对 canvas 亦达标。`statusMuted.*` 为装饰性底色，按 R-09 保持不变。

## D-4 Avalonia 11.3 无 OpenType 字体特性 API

`TextBlock` 不支持 `font-feature-settings: "tnum"`。`data`/`num` 层级通过等宽数据字体栈
`Nm.FontFamily.Data`（Cascadia Mono / Consolas）实现等宽数字；比例字体的 tabular-nums 无法强制。

## D-5 键名映射（契约示例名 vs token 原始路径）

契约 §2.2 给出语义键名，`tokens.json` 用设计侧路径。映射表在 `Generated/TokenMap.md`，命名差异较大的：

| token 路径 | 资源键 |
|---|---|
| `size.hTop` | `Nm.Size.TopBand` |
| `size.hBand` / `size.hRunStrip` / `size.hBandOpen` | `Nm.Size.StatusBandPage` / `StatusBandBatch` / `StatusBandExpanded` |
| `size.wTree` | `Nm.Size.TreeWidth` |
| `row.comfy` / `row.page` | `Nm.Size.RowPage` / `Nm.Size.RowPageTall` |
| `size.icon` / `size.iconLg` | `Nm.Icon.Size` / `Nm.Icon.SizeLarge` |

## D-6 LineHeight 语义（R-14 后已对齐）

契约把 `Nm.LineHeight.Tight/Normal/Loose` 定为 double 乘数（1.25/1.45/1.6）；R-14 规定语义别名
`Nm.LineHeight.Display/Title/Body/Label/Meta/Data` 的值**必须等于**三个冻结乘数之一，生成器断言
（Display/Title/Label/Meta/Data = 1.25，Body = 1.45）。Avalonia `TextBlock.LineHeight` 是**绝对像素**，
故样式消费另组派生绝对键 `Nm.TextLineBox.*`（字号 × 别名乘数），生成器不把其放入主题层白名单。

## D-7 High contrast 依赖具体 ThemeVariant

高对比盘用 `ResourceDictionary.ThemeDictionaries`（Dark/Light）实现，必须在具体 `ThemeVariant` 下解析。
显式 `AppearanceMode.Light/Dark` 由管理器设置 `RequestedThemeVariant`，正常；`AppearanceMode.System`
依赖平台上报的 `ActualThemeVariant`（headless 可能为 `Default`，此时回退标准盘，不崩溃）。

## D-8 焦点环实现（Avalonia FocusAdorner 不渲染，改为 overlay 承载）

目标为 DESIGN_SYSTEM §8 的「2px accent 外侧 outline，不用阴影」。实测 Avalonia 11.3 的
`Control.FocusAdorner` 属性在 Window/headless 的 adorner 层不被渲染（属性值存在但无绘制），且 Fluent
TextBox 会自行加 2px 系统蓝内边框。实现改为：

- `NewManga.DesignSystem.Theming.FocusRing` 附加行为：`GotFocus` 时把 2px accent `Border` 加入窗口
  `OverlayLayer` 并按控件 bounds 外扩一个线宽定位，`LostFocus`/detach 移除；线宽从
  `Nm.Border.Focus` 令牌读取（无裸值），控件模板几何不变。
- `Styles/Inputs.axaml` 覆盖 Fluent TextBox 的 `PART_BorderElement` 聚焦态，恢复 1px 边框，使唯一焦点
  信号为外侧 accent outline（截图 `screenshots/focus-ring-dark.png` / `-light.png` 可见）。
- 该实现不使用负 margin（D-8 旧记录的 `Margin="-2"` 已移除），也不引入 material/elevation。

## D-9 旧样式栈共存

`App/Styles/AppStyles.axaml`（旧壳）仍在 `Application.Styles` 中且排在 DesignSystem 样式之前；DS 样式
在后，同属性时 DS 生效。旧壳退役（V11R-C-3 / V11R-INT-1）前两套共存；旧 `NewManga.Theme` 未修改、未
新增引用。DS 全局样式（字体、TextBlock 继承、TextBox、Border）会作用于仍在运行的旧 `MainWindow`，属过渡
期已知限制：旧壳会被替换，新壳在 INT-1 成为默认入口后 DS 样式全局生效即可（Codex r1 已登记，不修）。

## D-10 依赖说明（未引入新外部依赖）

DS 库只引用 `Avalonia` 11.3.22（与主工程同版本）。测试项目新增 `Avalonia.Headless` /
`Avalonia.Headless.XUnit` / `Avalonia.Skia` / `Avalonia.Themes.Fluent`，均为 `NewManga.App.Tests` 已在
使用的同版本 Avalonia 组件，不构成新的第三方依赖。

## D-11 生成产物的换行与可复现性

仓库 `core.autocrlf=true`，会重写工作区换行。为让「重建产物逐字节一致」在任何 checkout 成立，
DesignSystem 目录新增 `.gitattributes`（`*.axaml`、`Generated/*.g.cs`、`Generated/*.md` 固定
`eol=lf`），生成器自身也强制 LF 输出。

## D-12 ReducedMotion 只覆盖 DS 动效令牌，不恢复旧壳过渡（过渡期）

ReducedMotion overlay 把 `Nm.Motion.Duration.*` 置零并关闭 `Nm.Motion.Enabled`，DS 控件与样式使用这些
令牌；旧 `AppStyles.axaml` 的 `Transitions`（如 `Border.nm-bookcard` 的 0.12s 过渡）仍为固定值，不受
reduced-motion 影响。旧壳随 V11R-C-3 退役；新壳不在 `AppStyles` 中声明过渡，因此 C-3 后自然满足。
本轮不修改旧壳样式（不在授权路径内）。

## D-13 em 跟踪令牌发布为「比率」而非像素

`tokens.json` 的 `font.tracking.*` 为 em 值（`0.08em`、`-0.01em`、`0`）。Avalonia 11 无 em 字距 API
（`TextBlock.LetterSpacing` 单位是 DIP），无法在不结合字号的情况下静态换算，故 `TokenValueKind.EmRatio`
发布**比率 double**（`Nm.FontTracking.Caps=0.08` 等），不当作 px 使用；生成器断言 tracking 必须为 em
（或恰好 0）。消费方若需设备像素须自行乘字号（当前 DS 样式不应用字距）。契约 §2.2 未列 tracking 键，
属映射扩展，已在 `Generated/TokenMap.md` 注明。

## D-14 主题层白名单不含 material/elevation（契约 §4.1 / R-15）

`ApplyThemeLayer` 只接受 59 键（35 色 + 3 字体族 + 6 字号 + 9 行高 + 3 圆角 + 3 动效），
material/elevation 按 R-15 **不接受**，白名单外键忽略并记入 `ThemeLayerIssues`（供 Theme Studio 诊断）。
冻结系统只通过五级表面阶梯表达 elevation，无阴影/材质令牌。

## D-15 主题层覆盖与密度/高对比叠加顺序

主题层随 palette 槽位合并在全局令牌之后、高对比/密度/动效 overlay 之前：主题层的字号/行高会被用户密度
档覆盖（用户偏好优先），高对比继续覆盖颜色。`ReorderOverlays` 保证该顺序稳定；`RemovePaletteProviders`
跳过 overlay 字典，避免切换时误删用户叠加状态。

## D-16 发布与裁剪（NOT_RUN）

Trim / AOT / single-file 发布未验证：DS 未引入 trim 特性、未做反射注册，但也没有为裁剪编写测试；发布路径
不在 V11R-D-1 范围。若后续需要自包含发布，需在集成 Task 补 `PublishTrimmed` 冒烟。

## D-17 高对比/Density 的规则派生扩展由生成期断言守护（R-14/R-15）

`Tokens.HighContrast.axaml` 与 `Density.*.axaml` 的取值由生成器内登记并断言（高对比文本 ≥7:1、状态与
accent ≥4.5:1；密度 Compact<Comfortable<Spacious），`--check` 保证生成产物不漂移；它们不是第二真值源。
若 Lead 后续把这两套数据移入 `tokens.json`，删除对应派生表与断言即可。

## D-18 生成器新增派生键与 R-14/R-15 命名备注

`Nm.FontSize.Xxl` 为冻结键（R-14，契约 §2.2 已改）；`Nm.TextLineBox.*`、`Nm.Size.Marker/MarkerCore/
ScrollBar`、`Nm.Motion.Duration.Slow`、`Nm.LineHeight.Tight/Normal/Loose` 属新增（不重命名已发布键与
Classes，符合 Lead「只允许新增」要求），推导与用途见 `Generated/TokenMap.md` 的 R-14/R-15 备注。

## D-19 R-18 断点与 Skeleton 扩展（Lead 新增要求）

按 Lead R-18，DS 追加：

- Nm.Size.Breakpoint.Full=1600 / .Compact=1280 / .Narrow=1024（double，生成器派生全局）；两个 UI
  工作面必须使用该组键，禁止再各自维护 1400/1200/1600/1400/1280 三套本地断点。
- Skeleton 控件（NewManga.DesignSystem.Controls.Skeleton，SkeletonVariant.BookCard/Row/Panel）
  与 Styles/Controls.Skeleton.axaml：书卡 180、行 28（复用 Nm.Size.RowPage）、面板 96（派生
  Nm.Size.SkeletonBookCard/SkeletonPanel）。**有意不做 pulse/shimmer 动画**：reduced-motion 下静态
  占位不产生闪烁，视觉证据 gallery-*.png 可直接复核。
- 图标枚举扩充到 41 个线性图标（原 27 + 14），覆盖 4 个一级空间、播放/暂停/停止/重试、导入/导出、设置/
  搜索/命令/主题/锁/历史/刷新/关闭/删除/编辑/文件夹/文件/章节/页/眼睛/分屏/缩放±/适应窗口；统一由
  Nm.Icon.Size(20) / Nm.Icon.Stroke(1.25) 与描边令牌驱动，UI 不得使用字母/汉字占位。
