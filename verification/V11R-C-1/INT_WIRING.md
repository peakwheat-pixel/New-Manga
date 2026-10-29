# INT-1 App 接线点清单（Theme Engine ⇄ App / 新外壳）

面向 `V11R-INT-1` 集成（App 写域）。本文件只列**接线点与顺序约束**，不修改 App 代码。
依赖与用法细节见 [CONSUMER_GUIDE.md](CONSUMER_GUIDE.md)；API 契约见
`doc/plan/V11R_AVALONIA_CONTRACT.md` §4。

现状（main `ecfe8921a`）：

- `NewManga.App.csproj` 已引用 `NewManga.ThemeEngine`（R-20），但 App 仍只使用旧 `ThemePackService` 与
  `DesignSystemThemeManager`，尚未构造 `ThemeService` / `DesignSystemThemeLayerSink`；
- `App.axaml.cs`：`ThemePackService.ApplyDefault` → 旧的 `--theme/--variant` 钩子 → `_designSystemTheme.Initialize(startupAppearance)`
  → `new MainWindow(...)`；
- `AppOptions`：`--theme`（旧 `ThemePack` id）/`--variant light|dark`（THEME-MACOS-2 证据钩子）。

## 1. App 侧构造（建议位置：`App.OnFrameworkInitializationCompleted`）

```csharp
// 现有：旧壳过渡期保留（C-3 退役时删除）
ThemePackService.ApplyDefault(this);
_designSystemTheme = new DesignSystemThemeManager(this);
_designSystemTheme.Initialize(startupAppearance);        // 必须先于 ThemeService.InitializeAsync

// 新增（R-20 已引用 ThemeEngine）：
var registry = new ThemeRegistry();                       // 内置 + %APPDATA%/NewManga/themes
var persistence = new ThemeSettingsStore(registry: registry);
var sink = new DesignSystemThemeLayerSink(this, _designSystemTheme);
_themeService = new ThemeService(registry, persistence, sink);
_themeService.InitializeAsync().GetAwaiter().GetResult(); // 见 §4 顺序/阻塞说明

var window = new MainWindow(controller, options);         // 主题应用之后才构造主窗口
_themeService.Changed += (_, _) => ApplyLayoutPreferences(_themeService.Settings);
ApplyLayoutPreferences(_themeService.Settings);           // 密度等 App 侧关注点
```

要点：

- **`DesignSystemThemeManager` 单例共享**：App 现有 `_designSystemTheme` 实例即 ThemeEngine 的 manager；
  不要把第二个 manager 传给 sink（资源栈会双写）。ThemeEngine 不拥有/不创建 manager。
- **`ThemeService` 生命周期 = App**：字段持有；关闭时先 `_themeService.Dispose()`（解绑预览/平台事件），
  再 `_designSystemTheme.Dispose()`。
- 需要给 Theme Studio / V2 Shell 注入的引用：`IThemeService`（真实 `ThemeService`）与 `IThemeRegistry`。
  Studio 用 `((ThemeService)themeService).PreviewEngine` 或把 `IThemePreviewEngine` 一并注入；
  **不要**让 Studio 自己 new `ThemePreviewEngine`。
- `ThemeService` 的 `LastError`/`LastIssues` 可接到状态条/诊断区。

## 2. 启动时应用持久化设置

1. `ThemeSettingsStore.Load()` 自动完成旧 ID 迁移（退役计划 §2.1）并给出 `LastLoadIssues`；
   服务 `InitializeAsync` 已包含迁移、外观/对比度/减弱动效应用、主题层应用与“需要时回存”，
   App **不需要**再读设置文件或再调 `SetAppearance/SetContrast/SetReducedMotion`。
2. 主窗口构造**之后**不要再调用 `ApplyAsync` 做启动初始化（会二次切层）；只有用户/CLI 覆盖时才调用。
3. 密度/布局：`SetLayoutAsync` 只负责持久化；App 依据 `IThemeService.Changed` 用
   `_designSystemTheme.SetDensity(Map(settings.Layout.Density))` 应用（ThemeEngine 不引用 App/密度枚举）。
   V1 只实现 `Navigation=TopBand`；其余枚举值持久化但无视觉效果（不得做假开关）。

## 3. `--theme-id` / 旧 `--theme` / `--variant` 兼容

推荐在 `AppOptions` 增加 `--theme-id <id>`；`--theme` 继续作为旧别名（THEME-MACOS-2 证据脚本仍在用）：

```csharp
// 服务初始化完成后、MainWindow 构造前
var requestedId = options.ThemeId ?? options.StartupThemeId;      // ThemeId = 新参数
if (!string.IsNullOrWhiteSpace(requestedId))
{
    var wanted = LegacyThemeMigration.Migrate(
        ThemeDefaults.Settings with
        {
            ThemeId = requestedId,
            Appearance = ParseVariant(options.StartupVariant) ?? _themeService.Settings.Appearance,
        },
        id => registry.Find(id) is not null);

    if (!string.Equals(wanted.Settings.ThemeId, _themeService.Settings.ThemeId, StringComparison.Ordinal))
    {
        _themeService.ApplyAsync(wanted.Settings.ThemeId).GetAwaiter().GetResult();
    }

    if (wanted.Settings.Appearance != _themeService.Settings.Appearance)
    {
        _themeService.SetAppearanceAsync(wanted.Settings.Appearance).GetAwaiter().GetResult();
    }
}
else if (!string.IsNullOrWhiteSpace(options.StartupVariant))
{
    _themeService.SetAppearanceAsync(ParseVariant(options.StartupVariant)!.Value).GetAwaiter().GetResult();
}
```

语义：

- 旧 id（`saber-purple`/`midnight`/`macos-*`…）经 `LegacyThemeMigration` 映射到 `newmanga-default`
  + 计划外观（launchpad 额外 Compact 密度）；未知 id → 默认主题 + Dark + warning，不崩溃；
- 新 id 未知 → `ApplyAsync` 回退默认并 `Recovered=true`，App 应记录/提示而不是报错退出；
- CLI 覆盖是否持久化：当前实现会持久化（证据钩子语义）。若 INT-1 要求“仅本次启动生效”，
  在 App 侧保存原设置并在适当时机恢复，或后续由 Lead 裁决加临时覆盖 API（本任务不新增签名）。

## 4. 顺序/约束（硬）

| # | 约束 | 原因 |
|---|---|---|
| 1 | `DesignSystemThemeManager.Initialize(...)` → `ThemeService.InitializeAsync()` → `new MainWindow(...)` | 主题层需要 global tokens；先应用主题避免首帧闪默认；`ApplyThemeLayer` 失败会留在 DS 内建盘 |
| 2 | **不得**在视觉树构造后重建 `MainWindow` / V2 外壳根 | 契约 §4 behavior 1：切主题/外观/布局只替换资源字典并触发布局失效；headless 测试已断言同一窗口实例与画布位图像素不变 |
| 3 | 旧 `ThemePackService.Apply*` 只能在 DS 初始化之前调用；`ThemeService.InitializeAsync` 之后不得再调 | 旧包会改写资源，覆盖数据驱动的主题层；C-3 删除旧入口 |
| 4 | 不要同时让 App 与 `ThemeService` 调用 `manager.SetAppearance/SetContrast/SetReducedMotion` | 双写会造成状态分叉；这些语义归 `IThemeService`（其内部经 sink 调 manager） |
| 5 | `ThemeService.Dispose()` 先于 `DesignSystemThemeManager.Dispose()` | 服务持有 sink 事件订阅 |
| 6 | `ThemeService.InitializeAsync()` 当前实现内部只有本地小文件 IO，启动时可同步等待；若未来引入真异步，改用 Dispatcher 异步引导 | 避免 UI 线程死锁（当前 `await` 的注册表刷新是同步完成，持久化写为 `ConfigureAwait(false)`） |
| 7 | 主题/布局变更后，漫画画布（Image/Bitmap）不得重建 | 契约 §4 behavior 1；headless 验收：画布区域像素差 = 0 |

## 5. 启动/切换验收建议（INT-1）

- `--theme-id newmanga-default`：启动即默认主题，无首帧闪白；
- `--theme saber-purple`：迁移到 `newmanga-default` + Dark，并写入迁移后设置；
- `--variant light`：浅色外观，资源重算，窗口不重建；
- Theme Studio：预览 → 应用（`Commit` + `ApplyAsync`）→ 重启后保持；取消完整回滚；
- 切换主题/外观/布局期间：漫画画布位图区域像素哈希不变、未保存编辑不丢、窗口实例不变；
- 失败演练：把 `%APPDATA%/NewManga/theme-settings.json` 写坏 / 放一个损坏 `.nmtheme` / 用未知 `--theme-id`
  → 应用仍能启动，落到默认主题并显示 `LastError`/warnings；
- 真机/系统跟随/屏幕阅读器/Trim-AOT 见 C-1 README §5“未验证项”（本任务无实机环境）。
