# V11R-C-2 偏差 / 例外 / 缺口登记

契约基准：`doc/plan/V11R_AVALONIA_CONTRACT.md` §2.2/§2.4、`doc/design/redesign-v1/40-fusion/DESIGN_SYSTEM.md`、`doc/design/theming/THEME_STUDIO_SPEC.md`。
本文件登记**所有**与冻结契约/屏幕规范的偏差、例外、缺口；未登记项即视为违规。

---

## GAP-3 · 跟随系统强调色无法经引擎持久化（Lead 已裁定）

- **事实**：冻结的 `IThemeService`（V11R-C-1 Part B）没有 `SetFollowSystemAccentAsync`，
  `ThemeSettings.FollowSystemAccent` 没有写入路径；`ThemeStudioPaletteBuilder` 只能在作用域调色板合成时叠加
  「应用级强调色基线」。
- **V1 行为（裁定后）**：
  - 「跟随系统强调色（仅作用域）」开关**仅作用于 Theme Studio 的作用域调色板**，可见效果为预览/编辑器使用
    应用级强调色基线；关闭时使用主题自带强调色。
  - **不写入 `theme-settings.json`、不跨重启保持**（重启后回到关闭态）。
  - UI 已明示「（仅作用域）」，右栏能力说明写明原因。
- **裁定**：V1 **不扩** `IThemeService`（避免接口抖动）；登记为 **V11R-C-1 follow-up**，V1.x 扩接口后再持久化。
- **影响面**：仅「跟随系统强调色」一项；其它外观项（浅/深/系统、高对比、减少动效、密度）均真实持久化并有测试。

---

## DEV-1 · 预览三视图未复用生产 `LibraryView` / `StudioWorkspaceView`（Lead 已批准）

- **原因**：生产视图依赖 `IHostController` + `ShellState` + notify/confirm 委托，且属 ui-shell 写域；
  作为 Studio 预览宿主过重，且会引入跨 Owner 写域冲突。
- **替代**：Studio 内用**真实 Avalonia 控件树**渲染书架/工作台/阅读器（非图片、非截图），
  数据为明示「示例内容 · 非真实书库」的 fixture；配色走作用域 `PaletteScope`。
- **接缝**：`IPreviewSurfaceProvider`（`ThemeStudioView.PreviewSurfaceProvider`）供 INT-1 在能轻量构造生产视图时替换；
  返回 `null` 保留默认。
- **验收影响**：AC3 仍成立（真实控件 + 真实主题令牌渲染），但**不是**生产视图的像素级复刻；L3 复审按此判定。

## DEV-2 · 左栏宽度 200px（规范文字 224px）

- 使用 DS 令牌 `Nm.Size.TreeWidth = 200`；224 无对应令牌，而契约 §2.2 禁止裸值。
- 右栏 320px = `Nm.Size.InspectorExpanded`（与规范一致）。
- 视觉影响：左栏比规范窄 24px，副标题仍完整显示（12 字符内），无功能影响。

## DEV-3 · 动效三档预设为 Studio 侧声明值

- 引擎 `ThemeMotion` 为 `(FastMs, NormalMs, SlowMs)`，R-15 默认 `SlowMs=220`，上限 `MaxDurationMs=1000`。
- Studio 提供 `fast(90/140/220)`、`normal(140/200/260)`、`slow(240/320/440)` 三档，全部 ≤ 1000；
  这些是编辑器的**预设值**，写入主题包后由引擎校验，不新增引擎令牌。

---

## 例外申请：无（C2-P2-1 通过令牌解析解决，不需例外）

本任务未申请新的裸值例外、未新增设计令牌、未放宽 conformance 规则。

- 卡片间距 `Nm.Space.4`、卡片默认宽度 `Nm.Size.InspectorExpanded`、断点 `Nm.Size.Breakpoint.Full/Compact`
  均在运行期由 `ThemeStudioMetrics` 从 DS 解析（与 `ShellLayout` 同构的单一令牌解析模块，已列入 conformance 允许清单）。
- 最小卡片宽度为**纯令牌推导**：`(BreakpointFull − TreeWidth − InspectorExpanded − 2·S7 − 3·S4) / 4`（≈249），不是字面值。
- 列数 4/3/2 为 THEME_STUDIO_SPEC §3.1 冻结的**结构计数**，不属于设计几何值。

## C2-P2 整改（独立复审 r1，2026-10-30）

| 编号 | 复审问题 | 整改 | 证据 |
|---|---|---|---|
| **C2-P2-1** | `CardGap=12`、`MinCardWidth=248`、`_cardWidth=320`、`_width=320` 为 C# 裸几何值；`V2ConformanceTests` 的 C# 扫描显式排除 ThemeStudio，导致 DEVIATIONS「例外申请：无」与 README「C# 无裸间距」不成立 | 新增 `ViewModels/V2/ThemeStudio/ThemeStudioMetrics.cs`（唯一令牌解析模块，`Nm.Space.4` / `Nm.Size.InspectorExpanded` / `Nm.Size.Breakpoint.*`，最小卡宽由令牌推导）；VM 不再持有字面几何值；`V2ConformanceTests.OwnedCSharpDirectories` 增加 `ViewModels/V2/ThemeStudio`、`Views/V2/ThemeStudio`，允许清单加入 `ThemeStudioMetrics.cs`（理由：与 `ShellLayout` 相同的单一解析器）。编辑器 swatch 的 `Brushes.Transparent` / `new SolidColorBrush(...)` 一并改为可空 + `ImmutableSolidColorBrush`，ThemeStudio C# 扫描 0 命中 | `compliance.md` §2（71 个 C# 文件 0 命中）、`V2ConformanceTests` 6/6、`test.log` |
| **C2-P2-2** | AC9 像素探针是离线 `RenderTargetBitmap` 的字面面色 Border，未挂窗口/资源树 → 三个哈希相同由构造保证，`passed:true` 是字面量 | 探针改为**真实窗口内**的混合控件：① `{DynamicResource Nm.Color.Accent.Base}` 绑定的 Border（正向控制：换外观/换主题必须改变其像素，否则测试红）② `WriteableBitmap` 文档画布（画布区域像素哈希必须不变）。全部哈希/布尔值由比较派生写入 `screens/pixel-hash.json`（5 步帧 + 区域 SHA-256 + 9 项检查） | `screens/pixel-hash.json`（accent 哈希在 appearance/preview 变化、canvas 哈希 5 步恒定 `BD57…`、cancel 精确还原）、`screens/probe-*.png` |
| 附 P3 | `rollback-preview` 帧只截图未比较 | 增加断言：`preview` 与 `before` 至少 5/160 格不同（实测 128/160），`after` 与 `before` ≤3 格（实测 0），并把两个差值写进 `screens.json.rollback` | `screens.json` → `rollback.preview_vs_before_cell_difference=128`、`after_vs_before_cell_difference=0` |

---

## CONFORMANCE-1 · 合入 main 后的静态合规修正（2026-10-30）

- 触发：Lead 全量测试报 `V2ConformanceTests.V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects`
  命中 `MyThemesSectionView.axaml: raw padding/margin/spacing`。
- 原因：`ListBox BorderThickness="0"` 为字面量；conformance 正则禁止属性字面量数字（即使值为契约允许的 0）。
- 修正：删除该属性，改用控件默认值（0），视觉无变化（截图重跑一致）；未新增令牌、未登记数值例外。
- 复验：`dotnet test --filter "FullyQualifiedName~V2ConformanceTests|FullyQualifiedName~V2StudioConformanceTests"` → 10/10 通过；
  全量 `dotnet test -m:1` → 0 失败（见 `test.log`）。

---

## 复审 r1 P3 备注

- 行为测试的边界：状态机/导入/迁移等行为用例走 `StubThemeStudioService`（**真实引擎链路** + 临时目录 + `NullThemeLayerSink`）；
  应用级（真实 `DesignSystemThemeLayerSink` + `Application.Resources`）证据集中在 4 个 `CreateProductionService` 用例 + 24 张真渲染帧 + 新像素探针。
  README §4.1 已按此边界改写，AC 表不再混用两类宿主。
- **GAP-3 需登记进 V11R-C-1 follow-up 清单**（Lead 侧维护）；本任务只保留 C-2 侧记录，避免只活在 C-2 文档里。

## C2-P1 · 主题层行高契约漂移（V11R-C-2 诊断发现，Lead 授权修复，2026-10-30）

**症状**：合入 main 后重跑 C-2 截图，24 帧版式全部崩坏（文字行高把控件撑开 ~12 倍）。
**诊断**（C-2，临时 headless 探针）：
- 应用主题层前：`Nm.LineHeight.Label = 1.25`、`Nm.TextLineBox.Label = 15`；
  `ThemeService.InitializeAsync()` 之后：`Nm.LineHeight.Label = 16.2`、`Nm.TextLineBox.Label = 194.4`（= 12 × 16.2）。
- 根因链：`ThemeEngine/Palette/ThemePaletteComposer.AddTypography` 把 `Nm.LineHeight.Display/Title/Body/Label/Meta/Data`
  写成**绝对像素**；而 `DesignSystem/Theming/DesignSystemThemeManager` 的 `LineBoxDerivations` 按契约把这些键当**倍数**，
  再乘一次字号 → `Nm.TextLineBox.*` 被放大 `字号` 倍。
- 契约依据：`DesignSystem/Generated/TokenMap.cs:210` 与 `TokenDocumentWriter` 明确「`Nm.LineHeight.*` 只能是
  1.25/1.45/1.6 倍数；绝对像素行高在 `Nm.TextLineBox.*`」（静态 `Tokens.Global.axaml` 亦如此）。
**影响**：任何主题层应用后全局文本行高 ×字号；INT-1 在 v2 shell 启动即调用 `service.InitializeAsync()`，所以默认壳启动即中招。
此前测试（D-1 颜色/对比度、C-1 层内容）均未覆盖行高/布局，故漏网。
**修复**（Lead 授权扩大写域到 ThemeEngine + DS 最小防御）：
1. `ThemePaletteComposer.AddTypography`：6 个 tier 别名写**倍数**（按设计比例 × 预设修正后量化到冻结集合 1.25/1.45/1.6，tie 取低值）；
   层仍严格 59 键（`Compose` 的 59 键断言保持不变）；绝对值由 DS 按 `fontSize × multiplier` 派生。
2. `DesignSystemThemeManager.TryDeriveLineBoxes` 最小防御：层里 `Nm.LineHeight.*` 必须是 double 且落在 `[1.0, 2.5]`，
   越界 → `LastError` + 拒绝该层（保留上一层），不再静默放大。
3. 回归测试（`tests/NewManga.ThemeEngine.Tests/LineHeightContractTests.cs`，6 例）：
   别名 ∈ 冻结倍数且 ∈[1,2.5]；层仍 59 键；越界层被拒绝且资源不变；sink 应用后 `TextLineBox = fontSize × multiplier`；
   真实窗口 `TextBlock`（`Classes="body"`）的 `LineHeight`/`DesiredSize.Height` ≤ `fontSize × 2.5`（应用层后、以及
   `ThemeService.InitializeAsync()` 之后两条路径）。
4. 更新受影响断言：`ThemePaletteComposerTests`、`DesignSystemThemeLayerSinkTests`（`Nm.TextLineBox.Body` 才是绝对 18.85，
   `Nm.LineHeight.Body` 为 1.45）。
**验证**：`dotnet test -m:1` 全绿（ThemeEngine 235 通过，含新增 6 例；App 305/7 skip）；24 帧 + probe 证据已重建，版式恢复正常。

---

## 其他已声明缺口（非本任务写域）

- **NOT_WIRED-1** 文件选择器：等 INT-1 注入 `IThemeStudioFileGateway` 的 `StorageProvider` 实现（详见 `INT_NOTES.md §2.2`）。
- **NOT_WIRED-2/3** shell 入口接线与 App 唯一 manager 注入：归 `V11R-INT-1`（详见 `INT_NOTES.md §1/§3`）。
