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

## D-4 动效「slow」档不可表示（THEME_STUDIO_SPEC §3.4 vs 契约 §2.2）

Studio 规格写「时长 fast/normal/slow 三档」，但契约 §2.2 与 `tokens.json` 只有
`Nm.Motion.Duration.Instant/Fast/Normal`。本任务按**契约优先**只提供 Fast/Normal（+冻结
Instant=0）；`ThemeMotion` 不含 slow。若产品确需 slow 档，需先改冻结令牌与契约（R-11 流程），
再由 `ThemeTokenBaseline`/palette 层扩展。已在 README §4 写明。

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