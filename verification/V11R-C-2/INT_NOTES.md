# V11R-C-2 → V11R-INT-1 接线说明（Theme Studio）

本文件只写**接线事实与约束**，不含实现建议之外的产品设计。所有符号均在
`apps/desktop-avalonia/src/NewManga.App` 下可编译验证（HEAD 见 Task pin）。

---

## 1. 硬约束：整个应用只能有一个 `DesignSystemThemeManager`

主题应用 = `ThemeService` → `DesignSystemThemeLayerSink` → `DesignSystemThemeManager` **整层替换
`Application.Resources`**。`DesignSystemThemeManager` 内部保存「当前已应用层/调色板」状态，
两个实例会互相认为对方是"未知状态"，导致：

- 外观（浅/深/高对比/密度）互相覆盖，最后一次调用赢；
- `RevertPalette()` 由一个实例执行会把另一个实例的应用结果抹掉；
- 主题 Studio 的「取消」回滚会与 shell 的外观切换打架。

**因此：** INT-1 必须在 `App` 里持有唯一 `DesignSystemThemeManager`（当前是私有字段
`App._designSystemTheme`），把**同一实例**注入：

1. V2 shell / 现有外观入口（改用 `ThemeService` 或直接复用该 manager）；
2. `ThemeEngineThemeStudioService.CreateProduction(application, manager, …)`。

不要在 Theme Studio 内部再 `new DesignSystemThemeManager(...)`（生产路径已禁止；`StubThemeStudioService`
只在测试里创建沙箱实例）。

---

## 2. 精确构造入口（当前 HEAD 的真实签名）

### 2.1 服务（唯一生产构造路径）

```csharp
// NewManga.App.ViewModels.V2.ThemeStudio.ThemeEngineThemeStudioService
public static ThemeEngineThemeStudioService CreateProduction(
    Avalonia.Application application,
    NewManga.DesignSystem.Theming.DesignSystemThemeManager manager,
    string? themeDirectory = null,       // 默认 %APPDATA%/NewManga/themes（ThemeRegistry 默认）
    string? settingsFilePath = null,     // 默认 %APPDATA%/NewManga/theme-settings.json
    string? favoritesFilePath = null);    // 默认 %APPDATA%/NewManga/theme-studio-favorites.json
```

内部会构造 `ThemeRegistry` + `ThemeSettingsStore` + `DesignSystemThemeLayerSink` + `ThemeService`，
返回 `IThemeStudioService` 的生产实现（`isSandbox: false, persistsToDisk: true`）。
`InitializeAsync()` 由 ViewModel 的 `OpenAsync` 调用，**不要重复调用**。

### 2.2 文件选择器（可选，NOT_WIRED 现状）

```csharp
// NewManga.App.ViewModels.V2.ThemeStudio.IThemeStudioFileGateway
bool IsAvailable { get; }
Task<string?> PickPackagePathAsync(CancellationToken ct = default);
Task<string?> PickExportPathAsync(string suggestedFileName, CancellationToken ct = default);
Task<bool> WriteTextAsync(string path, string text, CancellationToken ct = default);
```

不注入时使用 `NullThemeStudioFileGateway.Instance`（`IsAvailable == false`），UI 明示
「文件选择器未接线（NOT_WIRED）：可拖入文件或粘贴 JSON」，导入导出仍可用（拖拽/粘贴/导出内容回读）。

### 2.3 ViewModel

```csharp
// NewManga.App.ViewModels.V2.ThemeStudio.ThemeStudioViewModel : ObservableObject, IDisposable
public ThemeStudioViewModel(IThemeStudioService service, IThemeStudioFileGateway? fileGateway = null);
public event EventHandler? RequestClose;          // 表面要求 shell 出栈
public event EventHandler? FocusSearchRequested;  // Ctrl+F 已由 View 处理，shell 无需关心
public Task OpenAsync(ThemeStudioSection section = ThemeStudioSection.Library, CancellationToken ct = default);
public void SelectSection(ThemeStudioSection section);
public void Close();
public void Dispose();                            // shell 关闭时调用（解绑服务事件）
```

`ThemeStudioSection`：`Library=0, Preview=1, MyThemes=2, Editor=3, Appearance=4, ImportExport=5, Reset=6`。

### 2.4 表面（推荐入口）

```csharp
// NewManga.App.Shell.V2.ThemeStudio.ThemeStudioSurface : UserControl
public ThemeStudioSurface();                              // 未绑定，DataContext 由外层赋值
public ThemeStudioSurface(ThemeStudioViewModel viewModel); // 推荐
public event EventHandler? RequestClose;                  // 订阅 → 从 ShellState.SurfaceStack 弹出
public ThemeStudioView StudioView { get; }
public Task OpenAsync(ThemeStudioSection section = ThemeStudioSection.Library);
public void Close();
```

也可直接用 `ThemeStudioView`（`NewManga.App.Views.V2.ThemeStudio.ThemeStudioView`）：
`new ThemeStudioView(vm)` + `OpenAsync/Close` + `CloseRequested` 事件（Surface 只是加了一层事件转发）。
`Ctrl+,` / TopBand「主题」/ Console「外观」三个入口最终都调用同一个
`surface.OpenAsync(section)`（各自传 `ThemeStudioSection.Appearance` / `.Library` 等）。

### 2.5 可选：预览三视图替换 seam

```csharp
// NewManga.App.Views.V2.ThemeStudio.Preview.IPreviewSurfaceProvider
Control? CreateSurface(ThemeStudioPreviewMode mode);
// 注入点：ThemeStudioView.PreviewSurfaceProvider { get; set; }
```

未注入时用 Studio 自带真实控件树（真实 Avalonia 控件 + 示例内容）。生产 `LibraryView` /
`StudioWorkspaceView` 目前依赖 `IHostController` + `ShellState`，INT-1 若能在轻量宿主中构造，
可在此返回生产视图；返回 `null` 则保留默认。

---

## 3. 接线配方（伪代码，不含产品决策）

```csharp
// App（唯一 manager 的持有者；本任务不改 App.axaml.cs）
_designSystemTheme = new DesignSystemThemeManager(Application.Current!);
_designSystemTheme.Initialize();
// …把 _designSystemTheme 传给 V2 shell 与 Theme Studio 的构造方（INT-1 重构点）…

// Theme Studio 单例（随 shell 生命周期）
var studioService = ThemeEngineThemeStudioService.CreateProduction(
    Application.Current!, manager, themeDirectory: null, settingsFilePath: null, favoritesFilePath: null);
var studioVm = new ThemeStudioViewModel(studioService /*, fileGateway */);
var surface  = new ThemeStudioSurface(studioVm);
surface.RequestClose += (_, _) => shell.PopSurface(ShellSurface.ThemeStudio);

// 打开
await shell.PushSurfaceAsync(ShellSurface.ThemeStudio);   // 现有 shell 语义
await surface.OpenAsync(ThemeStudioSection.Library);      // 或 .Appearance / .Preview …

// 关闭（走 Esc 三出口；脏草稿会弹三选一）
surface.Close();
// 关 shell 时：studioVm.Dispose()
```

注意：

- `OpenAsync` 会 `BeginPreview()` 创建引擎预览会话；同一表面重复 `OpenAsync` 是幂等的（会话已存在则复用）。
- 主题「应用」在 Studio 内部完成（`ThemeService.ApplyAsync` + 落盘），shell 不需要额外调用。
- shell 自己的外观状态（浅/深/高对比/密度）如仍有独立开关，**必须**改走同一 `ThemeService`
  （`SetAppearanceAsync` / `SetContrastAsync` / `SetLayoutAsync` / `SetReducedMotionAsync`）或读取
  `IThemeService.Changed`，不得绕过它直接改 `DesignSystemThemeManager`，否则会与 Studio 的
  「取消回滚/应用」互相覆盖。
- `ShellSurface.ThemeStudio` 已存在于 `ShellState`（V11R-INT-1 只需推入/弹出）。

---

## 4. GAP-3（已裁定，V1 不扩接口）

`IThemeService` **没有** `SetFollowSystemAccentAsync`；`ThemeSettings.FollowSystemAccent` 无法经引擎持久化。

- V1 行为：Studio 的「跟随系统强调色」**仅在作用域调色板生效**（可见效果 = 使用应用级强调色基线），
  关闭时使用主题自带强调色；**不写入设置文件、不跨重启保持**。
- UI 已明示「（仅作用域）」；右栏能力说明也写明「IThemeService 无该 setter，V1 仅在工作室的作用域调色板生效（GAP-3）」。
- 登记为 **V11R-C-1 follow-up**：V1.x 扩 `IThemeService` 后再持久化；届时只需在
  `ThemeEngineThemeStudioService.SetFollowSystemAccentAsync` 内改为调用引擎接口，UI 与作用域合成逻辑不变。

---

## 5. 契约边界（INT-1 不要碰的实现细节）

- `ViewModels/V2/ThemeStudio/**`、`Views/V2/ThemeStudio/**`、`Shell/V2/ThemeStudio/**` 是 C-2 Owner 写域；
  INT-1 只做构造/推入/弹出与文件选择器注入，不修改内部实现。
- 主题引擎（`NewManga.ThemeEngine`）与设计系统（`NewManga.DesignSystem`）为冻结共享契约，
  INT-1 不新增令牌、不改 `IThemeService`（GAP-3 已裁定 V1 不扩）。
- 应用内不得出现第二个 `DesignSystemThemeManager`（见 §1）。
