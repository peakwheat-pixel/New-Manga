# V11R-D-1 偏差记录（DEVIATIONS）

记录实现相对**冻结基线**（`tokens.json`、`DESIGN_SYSTEM.md`）与**冻结契约**
（`doc/plan/V11R_AVALONIA_CONTRACT.md`）的已知偏差、缺口与派生扩展。冻结文件一律未修改；
需要基线裁决的条目已/将报 Lead。

## D-1 冻结基线缺失 high-contrast 与 density 令牌集（派生扩展）

`tokens.json` 只定义 dark / light 两套配色与单一尺寸刻度，没有 contrast 与 density 令牌。契约
§4 的 `ContrastMode` / `Density` 需要可切换集合，故本任务提供**派生产物**（不修改冻结文件）：

- `Themes/Tokens.HighContrast.axaml`：完整 35 色高对比盘（ThemeDictionaries: Dark/Light），
  背景五级保持冻结值，前后景重新取值以满足 DESIGN_SYSTEM §2.3（正文 ≥7:1、状态/次要 ≥4.5:1、
  焦点环 ≥3:1），由单测 `ContrastTokenTests.High_contrast_palette_meets_every_floor_in_both_themes` 校验。
- `Themes/Density.Compact.axaml` / `Density.Spacious.axaml`：只覆盖控件高度/行高/内边距；
  Comfortable = 冻结 token 原值（不产生覆盖字典）。
- 派生全局键（生成器 `TokenMap.DerivedGlobals` 记录每个键的推导依据）：`Nm.Size.ControlHeight(28)`、
  `Nm.Size.ControlHeightSm(24)`、`Nm.Padding.Panel/Card/Control/ControlSm/Cell/Section/Icon/IconSm`、
  `Nm.Icon.Stroke(1.25)`、`Nm.Icon.SizeSmall(16)`、`Nm.Motion.Enabled`、
  `Nm.LineHeight.Display/Title/Body/Label/Meta/Data`、`Nm.Opacity.Disabled(0.4)`。
- 建议：下一版设计基线把 high-contrast / density 正式纳入 `tokens.json`，届时删除对应派生表。

## D-2 Motion 时长以冻结 token 为准（已由 Lead 裁决 R-10）

契约 §2.2 示例曾写 `Nm.Motion.Duration.Normal(0:0:0.15)`；冻结 `tokens.json` 为 `140ms`。按
V11R_PROGRAM §1.4「tokens.json 为唯一视觉权威」，资源值取 `00:00:00.1400000`。Lead 已裁决 R-10：
契约示例为笔误、以 tokens.json 为准，并已同步修正契约文本。DS 无需改动。

## D-3 标准盘对比度缺口 → 已按 Lead 裁决 R-09 修订冻结令牌

实测（WCAG 2.1，对 `bg.panel`）发现冻结标准盘有 5 处低于 DESIGN_SYSTEM §2.3 下限。Lead 裁决
**R-09**：规范条款优先于数据，修订 `tokens.json` 数据（记录于
`doc/design/redesign-v1/40-fusion/DECISION_LOG.md` §5），不改规范；高对比模式保留为更强分离档。

修订后标准盘已全部达标，`ContrastTokenTests` 已从"特征化缺口"改为**合规断言**：

| 令牌 | 修订前 | 修订后 |
|---|---|---|
| dark `status.queued` | `#5C6169`（2.74:1） | `#8A9099`（5.31:1） |
| dark `status.skipped` | `#4A4F55`（2.07:1） | `#82878E`（4.72:1） |
| dark `status.failed` | `#C9634F`（4.38:1） | `#CC6A57`（4.69:1） |
| light `status.skipped` | `#8A8F94`（3.26:1） | `#73777B`（4.51:1） |
| light `accent.base`（白字） | `#B4791F`（3.69:1） | `#96651A`（5.03:1） |
| light `accent.hover/active` | `#9C6717`/`#8A5A12` | `#7F5515`/`#6B470F`（明度仍单调） |
| light `accent.muted/ring` | `rgba(180,121,31,…)` | `rgba(150,101,26,…)`（同色相） |

残余说明：light `status.skipped` 对 `bg.canvas`（#F4F3F0）为 4.07:1，略低于 4.5；状态文字/符号
在组件中始终落在 `bg.panel`/`bg.raised` 或 `statusMuted` 底上（对 panel 4.51:1 达标），且一律带
符号与文字标签，高对比模式对 canvas 亦达标。`statusMuted.*` 为装饰性底色，按 R-09 保持不变。

## D-4 Avalonia 11.3 无 OpenType 字体特性 API

`TextBlock` 不支持 `font-feature-settings: "tnum"`。`data`/`num` 层级通过等宽数据字体栈
`Nm.FontFamily.Data`（Cascadia Mono / Consolas）实现等宽数字；比例字体的 tabular-nums 无法强制。

## D-5 键名映射（契约示例名 vs token 原始路径）

契约 §2.2 给出语义键名，`tokens.json` 用设计侧路径。映射表（生成证据）在
`apps/desktop-avalonia/src/NewManga.DesignSystem/Generated/TokenMap.md`，其中命名差异较大的包括：

| token 路径 | 资源键 |
|---|---|
| `size.hTop` | `Nm.Size.TopBand` |
| `size.hBand` / `size.hRunStrip` / `size.hBandOpen` | `Nm.Size.StatusBandPage` / `StatusBandBatch` / `StatusBandExpanded` |
| `size.wTree` | `Nm.Size.TreeWidth` |
| `row.comfy` / `row.page` | `Nm.Size.RowPage` / `Nm.Size.RowPageTall` |
| `size.icon` / `size.iconLg` | `Nm.Icon.Size` / `Nm.Icon.SizeLarge` |

## D-6 LineHeight 语义

契约把 `Nm.LineHeight.Tight/Normal/Loose` 定为 double 乘数（1.25/1.45/1.6）；Avalonia
`TextBlock.LineHeight` 是**绝对像素**。故样式使用派生绝对键 `Nm.LineHeight.Display/Title/Body/Label/Meta/Data`；
DESIGN_SYSTEM §3 的 1.35（label/meta）与 1.30（data）乘数在 `tokens.json` 中不存在，由派生表
按「字号 × §3 乘数」生成并记录推导。

## D-7 High contrast 依赖具体 ThemeVariant

高对比盘用 `ResourceDictionary.ThemeDictionaries`（Dark/Light）实现，必须在具体
`ThemeVariant` 下解析。显式 `AppearanceMode.Light/Dark` 由管理器设置 `RequestedThemeVariant`，正常；
`AppearanceMode.System` 依赖平台上报的 `ActualThemeVariant`（headless 环境可能为 `Default`，此时回退
标准盘，不崩溃）。

## D-8 焦点环的负外边距

焦点环是模板内 `Border#PART_FocusRing`，`Margin="-2"` 使其落在控件边界外 2px。该 `-2` 等于
`Nm.Border.Focus` 的 2px 线宽，是固定几何偏移而非视觉魔数；属于"禁止裸值"规则的显式例外。

## D-9 旧样式栈共存

`App/Styles/AppStyles.axaml`（旧壳）仍在 `Application.Styles` 中且排在 DesignSystem 样式之前；
两者设置同一属性时 DS 生效。旧壳退役（V11R-C-3 / V11R-INT-1）前两套共存。旧 `NewManga.Theme`
未被修改、未新增引用。

## D-10 依赖说明（未引入新外部依赖）

DS 库只引用 `Avalonia` 11.3.22（与主工程同版本）。测试项目新增
`Avalonia.Headless` / `Avalonia.Headless.XUnit` / `Avalonia.Skia` / `Avalonia.Themes.Fluent`，
均为 `NewManga.App.Tests` 已在使用的同版本 Avalonia 组件，不构成新的第三方依赖。

## D-11 生成产物的换行与可复现性

仓库 `core.autocrlf=true`，会重写工作区换行。为让"重建产物逐字节一致"在任何 checkout 成立，
DesignSystem 目录内新增 `.gitattributes`（`*.axaml`、`Generated/*.g.cs`、`Generated/*.md` 固定
`eol=lf`），生成器自身也强制 LF 输出。
