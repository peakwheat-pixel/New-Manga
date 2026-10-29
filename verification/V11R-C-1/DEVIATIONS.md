# V11R-C-1 偏差与裁决记录（DEVIATIONS）

记录实现相对**冻结契约**（`doc/plan/V11R_AVALONIA_CONTRACT.md` §4）与**冻结设计基线**
（`DESIGN_SYSTEM.md`/`tokens.json`）的已知偏差、契约缺口与派生决策。冻结文件一律未修改；
需要裁决的条目已报 Lead，裁决结果记录在此。

## D-1 契约 §4 未定义 `ThemeTokenSet` / `ThemeMetadata`（契约缺口，Lead 已批准）

契约只引用这两个类型名，未给出内部结构。本任务定稿（`Models/ThemeModels.cs`，已报 Lead 批准）：

- `ThemeTokenSet`（每个 light/dark 变体一份）= `Colors`（35 × `Nm.Color.*` 原始 CSS 值）
  + `Typography`（UI/Data/Display 字体族、`Scale` 0.8–1.3、`LineHeightPreset`）
  + `Corners`（none/sm/md ≤3px）+ `Material`（Solid|None）+ `Elevation`（None|Raised）
  + `Motion`（fastMs/normalMs）。
- `ThemeMetadata` = `EngineVersion` / `Generator` / `Extra`（有序字典）/ `LoadWarnings`
  （读取期诊断，不序列化、不参与值相等）。
- 布局/导航/密度**不在** `ThemePackage` 内（DESIGN_SYSTEM §1 解耦硬约束），只在 `LayoutProfile`；
  单测 `Written_package_declares_no_layout_navigation_or_density` 断言序列化结果不含这些字段。

## D-2 Palette 整层口径（Lead 裁决）

Part A `ThemePaletteComposer.Compose()` 输出**整层主题令牌** 59 键：
颜色 35 + 字体族 3 + 字号 6 + 行高乘数 3 + 绝对行高 6 + 圆角 3 + 动效时长 3。
（R-15/R-21 后口径为 **59 键**：35 色 + 3 字体族 + 6 字号 + 9 行高 + 3 圆角 + 3 动效 = 59；`Nm.Motion.Duration.Instant` 与主题不变量派生色 `Nm.Color.Scrim` 由 DS 全局字典提供，不在主题层。详见 D-4/D-16 与 `doc/design/theming/THEME_ENGINE_LAYER.md`。）
`ComposeColorLayer()` 保留 35 色子集（DS 颜色 seam / 预览快照）。

`material` / `elevation` 是主题包的**被校验声明**，但冻结 `tokens.json`/契约 §2.2 没有对应
`Nm.*` 令牌键：本引擎不发明第二套令牌，故不进入生成层（层级表达由 DS 五级明度 + `line.*`
承担，高对比由 DS 盘承担）。若后续设计基线新增 material 令牌，再按 R-11 流程扩展。

字号缩放/行高预设必须有令牌承载（Theme Studio 编辑器提供该控件）：字号的基数与 DESIGN_SYSTEM §3
的层级比来自生成产物 `Generated/ThemeTokenBaseline.g.cs`（由 tokens.json 派生，非手抄），
因此 `Nm.FontSize.*` / `Nm.LineHeight.*` 进入主题层是必要派生，不是新增令牌。

## D-3 对比度判定口径（Lead 裁决 R-09 后）

DESIGN_SYSTEM §2.3 的阈值按 WCAG 2.1 实测，但**判定表面**需要明确（否则 R-09 基线与规范相互矛盾）：

| 通道 | 对 `Bg.Panel` | 对 `Bg.Canvas` | 对 `Bg.Raised` |
|---|---|---|---|
| `Text.Primary` ≥ 7:1 | error | error | 不校验（规范只点名 panel/canvas 正文） |
| `Text.Secondary` ≥ 4.5:1 | error | error | 不校验 |
| `Status.*` ≥ 4.5:1 | **error**（状态组件所在规范表面） | **warning**（同一变体聚合 1 条） | **warning**（聚合 1 条） |
| `Accent.On` on `Accent.Base` ≥ 4.5:1 | error | — | — |
| `Accent.Base` on `Bg.Panel` ≥ 3:1（焦点环非文本） | error | — | — |

依据：Lead 对 V11R-C-1 的说明——R-09 修订保证 panel 门槛；light `status.skipped` 对 canvas 4.07
（对 panel 4.51 达标）属边缘场景，不得判 error，记 warning。当前 R-09 基线实测（内置默认主题）：
light 的 canvas/raised 与 dark 的 raised 有 3 组聚合 warning（`Edge_surface_status_contrast_is_reported_as_a_warning_not_an_error`
以特征化断言 pin 住数量），默认主题本身 **0 error**。若未来修订基线让这些表面也全部达标，
warning 会自然消失，该测试需同步更新（feature 变化而非回归）。

## D-4 动效 slow 档（R-15 已裁决，Part B 已按三档实现）

THEME_STUDIO_SPEC §3.4 要求 fast/normal/slow 三档，冻结契约 §2.2/`tokens.json` 原本只有
Instant/Fast/Normal。Lead 于 2026-10-30 以 **R-15** 登记 `Nm.Motion.Duration.Slow` 为 DS 契约扩展
（默认 220ms），Part B 已实现：

- `ThemeMotion(FastMs, NormalMs, SlowMs)`，默认 slow = `ThemeMotion.DefaultSlowMs = 220`；
- schema `motion.slowMs`（旧包缺失时回落到 R-15 默认，保持向后兼容）；
- 校验：0–1000ms 越界 → error；三档顺序 fast≤normal≤slow 违反 → warning；
- palette 输出 `Nm.Motion.Duration.Slow`（R-15 白名单 59 键中的动效 3 键之一；`Instant` 固定 0 且属 DS 全局令牌），
  reduced-motion 仍由 DS 覆盖字典清零；
- 默认主题生成器当前从 R-15 常量取 220ms，并在 tokens.json 出现 `motion.duration.slow` 时自动改读
  该 token（生成器测试/`--check` 覆盖）；
- DS `Nm.Motion.Duration.Slow` 键已随 R-15 合入 main；白名单单测改为**精确等于** DS `ThemeLayerRequiredKeys`（59 键），不再有“待发布扩展”分支。

## D-5 旧配置来源（事实核查）

旧 App **没有任何主题持久化**（`AppOptions` 只有 `--theme/--variant` CLI 证据钩子，
全仓 grep 无写盘路径）。因此迁移实现对「设置文档中出现旧 ID」这一形态生效，并兼容旧键名
`theme`/`variant` 与旧默认别名 `NewManga.Default`；覆盖退役计划 §2.1 的全部 9 个 ID + 未知 + 空
（共 11 类，见 `MIGRATION_CASES.md`）。未知 id 的「是否已安装」判定在有 `IThemeRegistry` 注入时
走 `Find`，否则保留原 id（由上层校验），不会误删用户主题。

## D-6 预览会话不直接持久化（契约 `void Commit()`）

契约 §4 的 `IThemePreviewSession.Commit()` 是同步 `void`，无法 await 持久化；THEME_STUDIO_SPEC §4
规定「应用 = `Commit()` + `IThemeService.ApplyAsync`」。因此预览引擎只维护会话状态机与
`Changed` 事件（Began/Updated/Committed/Cancelled），持久化由 Part B 的 `IThemeService` 负责。
`Commit`/`Cancel` 幂等，未提交 Dispose 自动回滚。

## D-7 安装写入规范化文档

`IThemeRegistry.InstallAsync` 校验通过后写**规范化**的 `newmanga.theme/1` 文档（kind 归一为
`user`、未知字段丢弃），而不是原始输入字节：保证安装目录里的文件是可复现的规范包，
`ExportAsync` 与其一致；同时避免「声明 kind=builtin 的输入」在磁盘上留下歧义。读取期诊断
（未知字段/被禁声明/重复字段）仍随校验结果返回。

## D-8 JSON 输出采用 relaxed escaping

主题文档是用户可读/可导出的资产，`ThemeJsonWriter` 使用
`JavaScriptEncoder.UnsafeRelaxedJsonEscaping` 保留引号/加号原样（不用于 HTML 渲染）。
输出仍为确定字节（排序键、2 空格缩进、LF、结尾换行），`--check`/单测保证可复现。

## D-9 默认主题 ID 拼写

契约 §4 行为约束 2 写「回退到 `NewManga.Default`」，退役计划 §2.1/§3 写 `newmanga-default`。
本实现采用退役计划拼写 `newmanga-default`（`ThemeDefaults.DefaultThemeId`），并把
`NewManga.Default` 作为旧别名迁移到该 id；契约文本视为笔误（同 D-2 类示例性文本）。

## D-10 生成产物的引导与可复现

`Themes/newmanga-default.nmtheme` 与 `Generated/ThemeTokenBaseline.g.cs` 是生成产物，提交前由
`tools/NewManga.ThemeEngine.ThemeGen` 从合入后的 R-09 `tokens.json` 生成；`--check`（CLI 与单测
`Committed_artifacts_match_the_frozen_token_source_byte_for_byte`）验证逐字节一致。两个文件在
`NewManga.ThemeEngine/.gitattributes` 固定 `eol=lf`，避免 `core.autocrlf` 造成跨机器不一致。

## D-11 高对比模式仍由 Design System 承担

Part A 的主题层只合成 Standard 对比度盘；`ThemeSettings.Contrast`/`IThemeService.SetContrastAsync`
在 Part B 通过 DS 现成的高对比盘（`Tokens.HighContrast.axaml`，DS 已用 WCAG 校验）叠加，
theme 层保持在其下方。这样不在 ThemeEngine 里复制第三份高对比令牌，符合「单一令牌真值」。

## D-12 用户主题目录同时接受 `.json`

契约 §4 写 `%APPDATA%/NewManga/themes/*.json`，任务卡写 `*.nmtheme`；实现两者都扫描，
安装统一写 `.nmtheme`，同名 id 时 `.nmtheme` 优先，重复 id 记 `registry.duplicate-id` warning。

## D-13 `AppearanceMode` 枚举声明顺序对齐契约（自查修正）

初版把 `AppearanceMode` 声明为 `System/Light/Dark`；契约 §4 的冻结声明是 `Light/Dark/System`，
枚举数值属于签名的一部分。已改为契约顺序（`Light=0`、`Dark=1`、`System=2`），并新增
`ThemeContractTests` 用反射冻结全部契约枚举的声明顺序/数值、位置记录的主构造参数、接口成员集与
schema 常量，防止后续无意漂移。序列化始终按名称（`light/dark/system`），不受数值影响。
## D-14 Part B 服务与 seam（实现状态）

`ThemeService : IThemeService` + `IThemeLayerSink` 已实现（Avalonia-free，可单测）：

- **启动路径不抛**：`InitializeAsync` 捕获设置读取/迁移/层应用/保存失败，记录 `LastError`/`LastIssues`，
  继续使用默认主题或 DS 内建层；`IsInitialized` 仍置位，App 可启动（contract §4 behavior 2）。
- **回退顺序**：请求主题（未知 id / 包损坏 / 校验 error / 层应用失败）→ `newmanga-default` →
  `RevertToBuiltInLayer()`（DS 内建层，语义与默认主题一致）；全部失败才返回 `ThemeApplyResult.Failed`
  并保留上一状态（不半应用）。所有恢复都写 `theme.fallback-applied` warning + 原始 issue。
- **外观/对比度/减弱动效**：委托 sink（对应 DS manager 现有方法）；外观切换失败会恢复旧外观并重放旧层，
  避免 UI 停在半切换状态。持久化的外观/对比度/动效在 `InitializeAsync` 先于 palette 应用。
- **预览接线**：`ThemeService` 内聚 `ThemePreviewEngine` 并订阅其事件：`Update` 即时应用会话主题层、
  `Cancel` 重放已应用主题层、`Commit` 由 Studio 随后调用 `ApplyAsync` 持久化；预览不改
  `ThemeSettings`/不触发服务 `Changed`（`ThemePreviewChangedEventArgs` 驱动 Studio UI）。
  若消费者在会话未提交时直接 `ApplyAsync`，服务取消会话自愈而不是抛异常。
- **系统跟随**：`IThemeLayerSink.PlatformThemeChanged` 事件在 `AppearanceMode.System` 下重算变体并重放
  当前主题层（contract §4 behavior 4）；显式浅/深时忽略。
- **对比度 warning 不阻塞**：`ThemeValidationResult.IsValid` 只由 error 决定；`ApplyAsync` 成功结果可携带
  warning（默认主题 3 条边缘表面 warning）。Studio 应把 warning 显示为“可选改进”，error 才阻止导入/应用。
- **seam 缺口**：main 当前 DS 只有 `ApplyPalette`；待 `ApplyThemeLayer(ResourceDictionary, string)` 合入后，
  适配器把 `IReadOnlyDictionary<string, object?>` 转 `ResourceDictionary` 并委托 manager/`ApplyThemeLayer`
  （含失败 LastError 透传），即完成 Part B 最后一块。

## D-15 `ThemeService` 与 App 的接线（Part B 边界）

`ThemeService` 不直接引用 `Application`/`DesignSystemThemeManager`：App 用真实 `IThemeLayerSink`
实现（Part B seam 就绪后）注入；ThemeEngine 侧已用 fake sink 覆盖全部状态机与回退分支（186 tests）。
这样 ThemeEngine 依赖方向保持 `App → ThemeEngine → DesignSystem`，不反向污染。
## D-16 R-21：主题不变量派生色（`Nm.Color.Scrim`）排除口径

DS P1/P2 返修新增了 Modal 遮罩色 `Nm.Color.Scrim`（`rgba(0,0,0,0.55)`），它被刻意放进**全局令牌字典**
（与 `Nm.Space.*` 同层），不属于任何 appearance palette。DS `ThemeLayerRequiredKeys`/`PaletteColorKeys`
已正确排除它。

本引擎修复前按 `NmKeys.Color.*` 前缀推导必需颜色集（36 键），导致内置 `newmanga-default`（35 色）被判
“缺 `Nm.Color.Scrim`”，main 上 46/159 个 ThemeEngine 测试连锁失败。按 **R-21** 修复：

1. `ThemeTokenKeys.Colors` 直接引用 DS 公开权威 `DesignSystemThemeManager.PaletteColorKeys`（35 键），
   不再自行按前缀推导；`ThemeTokenKeys.ThemeLayer` 直接引用 `ThemeLayerRequiredKeys`（59 键）。
2. `ThemePaletteComposer` 输出精确等于 59 键白名单：颜色 35 + 字体族 3 + 字号 6 + 行高 9 + 圆角 3 +
   动效 3（Fast/Normal/Slow）；不再输出 `Nm.Motion.Duration.Instant`（DS 全局不变量）。
3. `RequiredColorKeyCount = 35` 与 tokens.json 实际色键数一致；Scrim 不计入主题层。
4. 主题包若声明 `Nm.Color.Scrim`：校验器给 `colors.unknown-key` warning 并忽略（不是 error，也不是必需键）。
5. 单测新增：`Theme_invariant_derived_colors_are_excluded_from_the_theme_layer`（R-21 回归锚点）、
   `Theme_invariant_scrim_is_not_required_and_is_only_a_warning_when_declared`、
   `Theme_invariant_scrim_stays_out_of_the_composed_layer`；palette 单测改为与 DS 白名单**逐键相等**。
6. 文档：`doc/design/theming/THEME_ENGINE_LAYER.md` §3 明确 Scrim/Instant 的所有权；README 同步。

修复后全量 `dotnet test NewManga.sln --no-build -m:1` = 0 失败（ThemeEngine 188/188）。生成器产物
`Generated/ThemeTokenBaseline.g.cs` 的输入只有 tokens.json（未变，sha 一致），`--check` 仍逐字节一致；
主题包 `.nmtheme` 无颜色/动效值变化（Slow 值仍 220ms）。
## D-17 Part B 真实适配器与 headless 应用验收

`DesignSystemThemeLayerSink(Application, DesignSystemThemeManager)` 是 ThemeEngine 中唯一接触 Avalonia
资源的类型，只做转发（不解释主题语义）：

- `ApplyThemeLayer`：`IReadOnlyDictionary<string, object?>` → `ResourceDictionary` → DS
  `ApplyThemeLayer`（59 键白名单；非白名单键被 DS 忽略并记入 `ThemeLayerIssues`；失败保留原层并透传
  `LastError`）；
- `RevertToBuiltInLayer` → DS `RevertPalette()`；`SetAppearance/SetContrast/SetReducedMotion` → DS
  同名方法（Enum 映射：引擎枚举 ⇄ DS `AppearanceMode`/`ContrastMode`）；
- `PlatformThemeChanged` ← `Application.ActualThemeVariantChanged`（System 外观下服务重算变体并重放层）；
- 值类型与 DS 校验一致（`IBrush`/`FontFamily`/`double`/`CornerRadius`/`TimeSpan`）。

headless 验收（`Avalonia.Headless` + Skia；`DesignSystemThemeLayerSinkTests`，11 tests，全部通过）：

| 验收点 | 结果 |
|---|---|
| 59 键完整层应用后 `Application.Resources` 解析到主题值（含 Slow=220ms、LineHeight.Body=18.85、Corner.Md=3、FontSize.Md=13） | PASS |
| 布局/密度/间距键（`Nm.Space.3`/`Nm.Size.ControlHeight`/`Nm.Padding.Panel`）不被主题层改写 | PASS |
| 不完整层 / 错误值类型 → 返回 false、`LastError` 有值、上一层保持原状 | PASS |
| 非白名单键（如 `Nm.Space.3`）→ DS 忽略并记 issue，层仍应用成功且布局值不变 | PASS |
| `RevertToBuiltInLayer` 恢复 DS 内建盘（`builtin.dark`）且 `AppliedThemeLayerId` 清空 | PASS |
| 服务 initialize/Apply/SetAppearance/Reset 走真实 DS manager（暗→亮资源重算） | PASS |
| 连续切换 5 次不增加 `MergedDictionaries` 数量（无资源提供者泄漏） | PASS |
| **切换主题不重建窗口**：同一 `Window` 实例/同一 `Content` 引用仍可见 | PASS |
| **不改画布像素**：切换前后漫画画布位图区域像素差 = 0（SKBitmap 逐像素比较），同时资源色确实改变 | PASS |

说明：headless 应用共享一个 `Application`，测试 harness 每个用例重置 `MergedDictionaries`（与 DS 测试
同策略）并 `DisableTestParallelization`；测试宿主组合 FluentTheme + DS 样式，等价产品样式栈。
## D-18 C-1 收尾：未验证项登记与 C-3 前置断言

**未验证项**（本任务环境为 headless/CI，见 README §5）：Windows 实机运行、真实 OS 系统跟随端到端、
屏幕阅读器实测、Trim/AOT 发布、真实 `%APPDATA%` 读写（测试有意注入临时路径）、真实用户主题大样本。
均标记 `NOT_RUN`/`PARTIAL`，不作为已验收事实。

**C-3 前置断言**（已补测试）：`DependencyBoundaryTests` 断言 `NewManga.ThemeEngine` 程序集
`GetReferencedAssemblies()` 不含 `NewManga.Theme`、仅向下依赖 `NewManga.DesignSystem`（不含
App/Host/CoreClient），且类型/成员集合中不存在 `ThemePack`/`ThemePackService`/`LayoutKind`/
`NavPlacement` 等退役符号；`LayoutProfile` 作为契约替代类型存在。design-platform 执行 C-3 旧主题退役时，
可直接引用该测试与 `dotnet-test-themeengine.log` 作为“引擎侧零依赖旧 ThemePack”的证据。