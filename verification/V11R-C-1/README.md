# V11R-C-1 新 Theme Engine — 最终交付证据与 Handoff

- Task：`task-10 / V11R-C-1`（10 子系统：Tokens/Registry/Schema/Resolver/State/Persistence/Preview/ImportExport/Validation/Fallback，取代旧 `ThemePack`）
- Owner：theme-engine（**独立 Reviewer 待 Lead 指派；Owner 未自审**）
- 处置：Lead 按 **PASS_WITH_PENDING_REVIEW** 接收（代码 + 测试齐；复审排队）
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-THEME-ENGINE`；Branch：`v11r/theme-engine`
- Part A 已合入 main：`cc14a41d5`；Part B 已合入 main：`907339511`（merge `d8b953055`）
- **本轮 C-1 收尾代码 head（构建/测试对象）**：`daff73dbaefcd5ba960d8852d6cc2a6b0cfaac32`
  （相对 main `ecfe8921a` 仅新增 C-3 前置的零依赖测试；其后 commit 仅更新本证据/交接文档，不改代码）
- 交付状态：**Part A + Part B 代码与测试全部完成**；待办只剩独立复审、INT-1 App 接线（App 写域）与真机证据（见 §5/§6）。

## 1. 质量门（全部通过；日志含命令/HEAD/EXIT）

| 门 | 命令（`apps/desktop-avalonia`） | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror -t:Rebuild -v m -nologo` | **0 warning / 0 error**，EXIT=0（全量重编） | [build.log](build.log) |
| 全量测试（串行） | `dotnet test NewManga.sln --no-build -m:1 -v q --nologo` | **失败 0 / 通过 586 / 跳过 55 / 总计 641**，EXIT=0 | [dotnet-test-full.log](dotnet-test-full.log) |
| 本任务测试 | `dotnet test tests/NewManga.ThemeEngine.Tests -v n` | **203/203 通过** | [dotnet-test-themeengine.log](dotnet-test-themeengine.log) |
| 生成器可复现 | `dotnet run --project src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen --no-build -- --check` | up to date（逐字节一致），EXIT=0 | [generator-check.log](generator-check.log) |
| C-3 前置证据 | `DependencyBoundaryTests`（见 §6） | 引擎程序集对 `NewManga.Theme` **零引用**、无旧符号；仅向下依赖 DS | 日志同上 |

分套件：ThemeEngine 203/203；App 232（6 skip）；DS 67/67；Host 42（24 skip）；CoreClient 42（25 skip）。
跳过均为既有 `Skip=reason`（AC11 sidecar 副本缺失时保持裸 `dotnet test` 绿），与本次改动无关。

## 2. R-21 修复（main 红 → 绿，已随 Part B 合入）

DS 返修新增的主题不变量派生色 `Nm.Color.Scrim`（Modal 遮罩，属 global 令牌字典、不属于任何 palette）
曾使引擎按 `NmKeys.Color.*` 前缀推导的必需色集（36）拒绝内置默认主题（35 色），main 上 46/159 失败。
按 R-21 修复：必需色集改用 DS 公开权威 `DesignSystemThemeManager.PaletteColorKeys`（35）；59 键白名单
改用 `ThemeLayerRequiredKeys`；`Nm.Motion.Duration.Instant` 与 Scrim 均为全局不变量，不进入主题层
（59 = 35 色 + 3 字体族 + 6 字号 + 9 行高 + 3 圆角 + 3 动效）；主题包声明 Scrim → warning 并忽略。
修复 commit：`27e3eb430`；回归锚点 3 条；`--check` 逐字节一致。详见 [DEVIATIONS.md](DEVIATIONS.md) D-16。

## 3. 十子系统 AC 对照表（实现 / 测试 / 证据 / 未验证）

| # | 子系统 | 实现 | 测试 | 证据 | 未验证项 |
|---|---|---|---|---|---|
| 1 | **Tokens**（令牌生成/基线/主题层合成） | `Themes/BuiltInThemeGenerator.cs`（tokens.json→`newmanga-default` + `ThemeTokenBaseline.g.cs`，可复现）；`Palette/ThemePaletteComposer.cs`（59 键整层 + 35 色子集，值与 DS 生成盘逐色一致） | `BuiltInThemeGeneratorTests`、`ThemePaletteComposerTests` | generator-check.log、schema-sample.nmtheme、[THEME_ENGINE_LAYER.md](../../doc/design/theming/THEME_ENGINE_LAYER.md) | Trim/AOT 发布下的实际裁剪结果 |
| 2 | **Registry**（内置+用户目录） | `Registry/ThemeRegistry.cs`：`All/Find/Load/RefreshAsync/InstallAsync/UninstallAsync/ExportAsync`；损坏隔离进 `Diagnostics`；内置 id 保留 | `ThemeRegistryTests` | 单测 + §1 | 真实 `%APPDATA%` 写入（测试注入临时目录） |
| 3 | **Schema**（`newmanga.theme/1`） | `Serialization/ThemePackageJson.cs`（手写 JsonDocument/Utf8JsonWriter，确定性、未知字段 warning、禁用效果 error、版本校验）；`ThemeSettingsJson.cs` | `ThemePackageJsonTests`、`ThemeContractTests` | schema-sample.nmtheme | 第三方手写主题包多样性样本（目前只有生成/构造 fixture） |
| 4 | **Resolver**（主题层解析与应用） | `Palette/ThemePaletteComposer.cs` + `Service/DesignSystemThemeLayerSink.cs`（→ DS `ApplyThemeLayer` 59 键 seam） | `ThemePaletteComposerTests`、`DesignSystemThemeLayerSinkTests`（headless 11） | 日志 + §4 | Windows 实机渲染/多 DPI（headless 96dpi） |
| 5 | **State**（`IThemeService` 状态机） | `Service/ThemeService.cs`：Initialize/Apply/Appearance/Contrast/Layout/ReducedMotion/Reset + `Changed` + `LastError/LastIssues` | `ThemeServiceTests`（27） | 单测 | 真实 App Dispatcher/SynchronizationContext 时序（headless 已覆盖调用路径） |
| 6 | **Persistence**（设置+旧 ID 迁移） | `Persistence/ThemeSettingsStore.cs`（原子写、损坏回退不抛）+ `LegacyThemeMigration.cs`（退役计划 §2.1 全 11 类） | `LegacyThemeMigrationTests` | [MIGRATION_CASES.md](MIGRATION_CASES.md) | 真实用户配置文件/漫游目录策略（测试用注入路径） |
| 7 | **Preview**（会话状态机+服务接线） | `Preview/ThemePreviewEngine.cs`；`ThemeService` 内聚并同步应用/回滚；预览不写盘 | `ThemePreviewEngineTests`、服务预览接线用例 | 单测 | Studio 真实交互（C-2） |
| 8 | **ImportExport** | Registry `InstallAsync`（校验→规范化落盘）/`ExportAsync`（规范 JSON，round-trip） | `ThemeRegistryTests`、`ThemePackageJsonTests` | 单测 | 真实文件选择器/拖拽（UI 层） |
| 9 | **Validation** | `Validation/ThemeValidator.cs` + `ThemeContrast.cs`（必填键/色值/≤3px/禁用效果/字体/动效/WCAG；R-21 口径） | `ThemeValidatorTests`（39） | 单测 + DEVIATIONS D-3 | 大样本真实主题库扫验（当前仅生成/构造 fixture） |
| 10 | **Fallback**（回退/恢复） | 未知 id/坏包/校验 error/层失败 → `newmanga-default` → DS 内建 `RevertPalette()`；启动路径不抛、不半应用、`LastError` | `ThemeServiceTests` 失败分支、`DesignSystemThemeLayerSinkTests` 失败保持原状 | 单测 | 真实文件系统故障注入（磁盘满/权限拒绝用 fake persistence 覆盖） |

## 4. Part B 交接段落（适配器/调用路径/回退/不重建窗口）

- **适配器设计**：`IThemeLayerSink` 是 Avalonia-free 的 seam，`DesignSystemThemeLayerSink(Application,
  DesignSystemThemeManager)` 是唯一接触 Avalonia 资源的 ThemeEngine 类型；只做转发，不解释主题语义。
  `ThemeService` 通过它应用整层、切换外观/对比度/动效、回退，自身不引用 `Application`/App。
- **`ApplyThemeLayer` 调用路径**：
  `ThemeService.ApplyAsync(id)` → 注册表 `Find/Load` → `ThemeValidator.Validate`（errors 阻止）→
  `ThemePaletteComposer.Compose(package, ResolveVariant(Appearance, sink.IsPlatformLight))`（59 键）→
  `IThemeLayerSink.ApplyThemeLayer(layer, id)` → `DesignSystemThemeLayerSink` 转 `ResourceDictionary` →
  DS `DesignSystemThemeManager.ApplyThemeLayer`（白名单过滤 + 值类型校验 + 原子 Swap；失败保留原层）。
  成功后 `ThemeSettings` 更新 → `ThemeSettingsStore.SaveAsync`（原子写）→ `Changed`。
- **失败回退**：未知 id/损坏包/校验 error/层应用失败 → 先回退 `newmanga-default`（同路径合成应用）；
  仍失败 → DS `RevertPalette()` 内建盘；全部失败 → `ThemeApplyResult.Success=false`、Settings 不变、
  `LastError` 有值。每次回退写 `theme.fallback-applied` warning + 原始 issue（`LastIssues`）。
- **`LastError`/`LastIssues`**：服务公开；sink 透传 DS `LastError`/`ThemeLayerIssues`。对比度 warning 不阻塞
  应用（`IsValid` 只由 error 决定），Studio 显示为“可选改进”。
- **不重建窗口**：headless 验收（`DesignSystemThemeLayerSinkTests`）在同一 `Window` 实例上切主题：
  `IsVisible` 保持、`Content` 同引用；连续 5 次切换 `MergedDictionaries` 数量不变（无 provider 泄漏）。
- **画布像素断言**：窗口内嵌 32×32 纯净色 `WriteableBitmap`（模拟漫画画布），切换主题前后帧捕获 →
  SKBitmap 逐像素比较画布区域：**差异像素 = 0**；同时 `Nm.Color.Bg.Canvas` 资源确实改变（证明主题已生效）。
- **平台主题跟随**：`DesignSystemThemeLayerSink` 把 `Application.ActualThemeVariantChanged` 转成
  `IThemeLayerSink.PlatformThemeChanged`；`AppearanceMode.System` 下服务重算变体重放当前主题层。
  （fake-sink 单测 + 适配器接线覆盖；真实 OS 切换见 §5 未验证项。）

## 5. 未验证项（诚实登记）

| 项 | 状态 | 说明/后续 |
|---|---|---|
| **Windows 实机运行** | `NOT_RUN` | 本任务环境为 headless/CI；未在真实桌面窗口做主题切换/截图证据。INT-1 真机验收项（§4 的窗口/像素断言在 headless 已过）。 |
| **系统跟随（真实 OS 浅/深切换）** | `PARTIAL` | 事件转接与重算逻辑有 fake-sink 单测 + 适配器接线；真实 `ActualThemeVariantChanged` 端到端未在实机跑。 |
| **屏幕阅读器/无障碍** | `NOT_RUN` | 主题切换不改控件文本/焦点环语义；Narrator 等实测属 UI 集成验收，本任务未执行。 |
| **Trim/AOT 发布** | `NOT_RUN` | 引擎手写 `JsonDocument`/`Utf8JsonWriter`（无反射序列化）以兼容 trim；未实测 `PublishTrimmed` 后的主题加载。 |
| **真实 `%APPDATA%` 读写** | `NOT_RUN`（设计上有意） | 单测全部注入临时路径，不触碰用户真实配置；默认路径解析逻辑简单（`Environment.GetFolderPath` + 固定文件名）。 |
| **真实用户主题大样本** | `NOT_RUN` | 校验/导入以生成主题与构造 fixture 覆盖；无社区主题语料。 |

## 6. 交接 / 消费方文档

| 文档 | 用途 |
|---|---|
| [CONSUMER_GUIDE.md](CONSUMER_GUIDE.md) | **Theme Studio（C-2）集成指南**：构造依赖、`IThemeService` 全部方法语义、`Changed`、失败语义、线程/Dispatcher、预览→应用流程、导入导出、旧 ID 迁移入口 |
| [INT_WIRING.md](INT_WIRING.md) | **INT-1 App 接线点清单**：构造时机/顺序（DS manager 单例共享、Initialize 在 MainWindow 前）、`--theme-id`/旧 `--theme`/`--variant` 兼容映射、不得重建窗口的约束、启动验收建议 |
| [THEME_ENGINE_LAYER.md](../../doc/design/theming/THEME_ENGINE_LAYER.md) | 59 键主题层白名单（DS seam/Reviewer 对齐权威） |
| [DEVIATIONS.md](DEVIATIONS.md) | 偏差、契约缺口、裁决（D-1…D-18） |
| [MIGRATION_CASES.md](MIGRATION_CASES.md) | 旧 ID 迁移 11 类用例表 |
| `DependencyBoundaryTests`（测试源码） | **C-3 退役前置证据**：`NewManga.ThemeEngine` 程序集不引用 `NewManga.Theme`、仅依赖 `NewManga.DesignSystem`、不暴露 `ThemePack/ThemePackService/LayoutKind/NavPlacement` 等旧符号（design-platform 执行 C-3 时直接引用该测试与日志） |

## 7. 证据文件

| 文件 | 内容 |
|---|---|
| [build.log](build.log) | `-warnaserror -t:Rebuild` 全量构建原始日志（命令/HEAD/EXIT） |
| [dotnet-test-full.log](dotnet-test-full.log) | 全解决方案串行测试日志（`-m:1`） |
| [dotnet-test-themeengine.log](dotnet-test-themeengine.log) | 本任务 203 例逐例日志 |
| [generator-check.log](generator-check.log) | 生成器 `--check` 可复现校验 |
| [git-diff-stat.log](git-diff-stat.log) | 收尾轮相对 main 的变更规模 |
| [schema-sample.nmtheme](schema-sample.nmtheme) | 内置默认主题包全文样例（含 `motion.slowMs`） |
| [git-head.txt](git-head.txt) | 证据采集时的代码 HEAD、分支与基线 |
| [CONSUMER_GUIDE.md](CONSUMER_GUIDE.md) / [INT_WIRING.md](INT_WIRING.md) | 消费方/集成方交接文档 |
