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

## 例外申请：无

本任务未申请新的裸值例外、未新增设计令牌、未放宽 conformance 规则。

---

## CONFORMANCE-1 · 合入 main 后的静态合规修正（2026-10-30）

- 触发：Lead 全量测试报 `V2ConformanceTests.V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects`
  命中 `MyThemesSectionView.axaml: raw padding/margin/spacing`。
- 原因：`ListBox BorderThickness="0"` 为字面量；conformance 正则禁止属性字面量数字（即使值为契约允许的 0）。
- 修正：删除该属性，改用控件默认值（0），视觉无变化（截图重跑一致）；未新增令牌、未登记数值例外。
- 复验：`dotnet test --filter "FullyQualifiedName~V2ConformanceTests|FullyQualifiedName~V2StudioConformanceTests"` → 10/10 通过；
  全量 `dotnet test -m:1` → 0 失败（见 `test.log`）。

---

## 其他已声明缺口（非本任务写域）

- **NOT_WIRED-1** 文件选择器：等 INT-1 注入 `IThemeStudioFileGateway` 的 `StorageProvider` 实现（详见 `INT_NOTES.md §2.2`）。
- **NOT_WIRED-2/3** shell 入口接线与 App 唯一 manager 注入：归 `V11R-INT-1`（详见 `INT_NOTES.md §1/§3`）。
