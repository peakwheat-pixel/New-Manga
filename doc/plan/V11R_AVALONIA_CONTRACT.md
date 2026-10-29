# V11R Avalonia 并行实施契约 v1（FROZEN）

状态：`FROZEN`（2026-10-30，DSH）。本文件是 V11R 并行开发的**共享接口契约**。任何 Owner 不得单方面修改本文件；
需变更时在 `doc/V11R_PROGRAM.md §8` 追加裁定并通知所有波次中的 Agent。

上游：`doc/design/redesign-v1/40-fusion/{FUSION_SPEC,DESIGN_SYSTEM}.md` + `tokens.json`（设计，冻结）；
`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md`（架构，冻结：Avalonia 不直连 DB/模型/任意 OS 路径）。

---

## 1. 工程与命名

### 1.1 项目

| 项目 | 路径 | 说明 |
|---|---|---|
| Design System | `apps/desktop-avalonia/src/NewManga.DesignSystem/NewManga.DesignSystem.csproj` | **新建**。令牌资源、样式、自定义控件、图标。命名空间 `NewManga.DesignSystem`（控件 `NewManga.DesignSystem.Controls`） |
| Theme Engine | `apps/desktop-avalonia/src/NewManga.ThemeEngine/NewManga.ThemeEngine.csproj` | **新建**。命名空间 `NewManga.ThemeEngine`。取代 `NewManga.Theme` |
| App | `apps/desktop-avalonia/src/NewManga.App/` | 现有。新 UI 代码全部落在 **`Views/V2/**.axaml(.cs)`、`ViewModels/V2/**`、`Shell/V2/**`**，不改旧文件 |
| 旧主题（退役对象） | `apps/desktop-avalonia/src/NewManga.Theme/` | 仅 `V11R-C-3` 可动；其它任务禁止新增引用 |
| 测试 | `apps/desktop-avalonia/tests/NewManga.App.Tests/`（SDK 自动 glob，无需改 csproj） | DS/Themes 测试可新建独立测试项目 |

引用关系（单向，禁止环）：`App → ThemeEngine → DesignSystem`；`App → DesignSystem`；`DesignSystem` 不引用 App/Host/CoreClient。

### 1.2 共享写权边界

| 文件 | 唯一写者 |
|---|---|
| `NewManga.sln`、`App.axaml`、`App.csproj`、`src/NewManga.App/App.axaml.cs` | `design-platform`（M0 阶段），之后仅 DSH |
| `App/Services/IHostController.cs`、`HostController.cs`、`NullHostController.cs`、`Services/Run*.cs`、`CoreClient/**` | `core-bridge` |
| `App/Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**` | `ui-shell`（Shell/Library/Console/ThemeStudio 子目录）与 `ui-studio`（**仅** `Views/V2/Studio/**`、`ViewModels/V2/Studio/**`、`Shell/V2/Studio/**`） |
| `src/**`（Python）、`NewManga.Host/**`、`CoreClient/**`（协议） | `V11R-F0-1` Owner（Codex） |
| 本文件、`doc/V11R_PROGRAM.md` | DSH |

冲突处理：先到者提交；后者 `git rebase`/重新生成，不得强推覆盖他人未提交内容。

---

## 2. 令牌契约（DesignSystem ⇄ ThemeEngine ⇄ UI）

### 2.1 命名

DTCG 令牌 `color.dark.bg.canvas` → Avalonia 资源键 **`Nm.Color.Bg.Canvas`**；通用映射 `{group}.{path}` → `Nm.{Group}.{Path}`（PascalCase 逐段）。
CSS 变量 `--nm-color-bg-canvas` 与本键一一对应。

### 2.2 必须有资源键的组（V1 最低集）

| 组 | 键示例 | 类型 |
|---|---|---|
| 背景 5 级 | `Nm.Color.Bg.App/Canvas/Panel/Raised/Overlay/Sunken` | `IBrush` |
| 描边 | `Nm.Color.Line.Subtle/Default/Strong/Grid` | `IBrush` |
| 文本 | `Nm.Color.Text.Primary/Secondary/Tertiary/Disabled/Inverse` | `IBrush` |
| 强调 | `Nm.Color.Accent.Base/Hover/Active/Muted/On/Ring` | `IBrush` |
| 状态 7+未开始 | `Nm.Color.Status.Queued/Running/Done/Failed/Blocked/Stale/Skipped` | `IBrush` |
| 状态底 | `Nm.Color.StatusMuted.*` | `IBrush` |
| 字体族 | `Nm.FontFamily.Ui/Data/Display` | `FontFamily` |
| 字号 | `Nm.FontSize.Xs(11)/Sm(12)/Md(13)/Lg(14)/Xl(18)/2Xl(24)` | `double` |
| 字重/行高 | `Nm.FontWeight.Regular/Medium/SemiBold`、`Nm.LineHeight.Tight(1.25)/Normal(1.45)/Loose(1.6)` | `FontWeight`/`double` |
| 间距 | `Nm.Space.0=0,1=2,2=4,3=8,4=12,5=16,6=20,7=24,8=32` | `double` |
| 圆角 | `Nm.Corner.None/Sm(2)/Md(3)` | `CornerRadius` |
| 尺寸 | `Nm.Size.TopBand(36)/StatusBandPage(28)/StatusBandBatch(24)/FilmStripCollapsed(56)/FilmStripExpanded(200)/InspectorCollapsed(40)/InspectorExpanded(320)/Drawer(360)/RowPage(28)/RowBatch(22)/ControlHeight(28)/ControlHeightSm(24)` | `double` |
| 内边距 | `Nm.Padding.Panel(12)/Card(12)/Control(8,12)/ControlSm(6,8)/Cell(8)/Section(16)` | `Thickness` |
| 动效 | `Nm.Motion.Duration.Fast(0:0:0.09)/Normal(0:0:0.15)`、`Nm.Motion.Enabled` | `TimeSpan`/`bool` |
| 图标 | `Nm.Icon.Size(20)/Stroke(1.25)` | `double` |

**硬规则**：组件 XAML/C# 中禁止裸色值、裸字号、裸间距、`border-radius > 3px`、阴影、渐变、模糊（DESIGN_SYSTEM §1、§9）。
一律 `{DynamicResource Nm.*}`（保证主题/密度/高对比实时切换）——**唯一例外**：`0`、`1px` 线宽、`Grid` 的 `*`/`Auto`。

### 2.3 状态令牌的使用方式

每个状态必须同时有色相 + 符号 + 文字标签（DESIGN_SYSTEM §2.2）。符号常量：
`◦ queued · ◐ running ● done ✗ failed ▲ blocked ▨ stale – skipped ○ not_started ▮ locked`，由 `NewManga.DesignSystem.Controls.StatusGlyph` 提供，UI 不得自造。

---

## 3. Design System 公开面（UI 只依赖这些）

### 3.1 标准控件样式（无自定义控件，直接用 Avalonia 内置 + `Classes`）

| 控件 | Classes（`~` 表示变体互斥） |
|---|---|
| `Button` | `~primary/secondary/ghost/danger`、`icon`、`sm`（默认 md） |
| `TextBox` | `search`、`mono`、`invalid` |
| `TextBlock` | `display/title`、`body/label/meta/data`、`muted`、`num`（tabular-nums） |
| `Border` | `card/panel/raised/overlay/sunken`、`hairline` |
| `ComboBox` | `compact` |
| `CheckBox`/`RadioButton`/`ToggleSwitch` | 默认样式即设计系统样式 |
| `TabControl`/`TabItem` | 默认样式即设计系统样式 |
| `ScrollViewer`/`ScrollBar` | 默认样式即设计系统样式（8px、hover 显形） |
| `ProgressBar` | `indeterminate` |
| `Separator`/`MenuFlyout`/`ContextMenu`/`ToolTip` | 默认样式即设计系统样式 |

### 3.2 自定义控件（`NewManga.DesignSystem.Controls`，UI 通过 `xmlns:nmc` 使用）

`StatusGlyph`（符号文本）、`StatusBadge`、`Chip`、`Kbd`、`SegmentedControl`、`SearchField`、`EmptyState`、`AlertBanner`、`CountChips`、`DataTable`、`StatusMatrix`、`MatrixCell`、`FilmStrip`/`FilmItem`、`PageGrid`、`RunStrip`、`StageRail`、`RevisionList`、`CanvasViewport`、`RegionOverlay`、`RegionBox`、`HUDRing`、`HUDAction`、`TrackStrip`、`SplitCompare`、`Drawer`、`Modal`、`CommandPalette`、`TopBand`、`SpaceTabs`、`Breadcrumb`、`ScopeSelector`、`AttentionMenu`、`Inspector`、`TextTierPanel`、`LockControls`、`ImportDock`、`ProviderStatusCard`、`ExportPreflight`、`TaskPanel`。

**分阶段**：`design-platform` 在 M0 交付 §3.1 + `StatusGlyph/StatusBadge/Chip/Kbd/EmptyState/AlertBanner/ProgressBar` 与 `Drawer/Modal/TopBand` 基础版；
其余控件由各 UI Owner **在自己目录先本地实现**（`Views/V2/<Area>/Controls/**`），M3 再上收 DS（避免互相等待）。上收规则：仅当同一个控件被 ≥2 个工作面使用时。

---

## 4. Theme Engine 公开面（冻结）

```csharp
namespace NewManga.ThemeEngine;

public enum ThemeKind { BuiltIn, User }
public enum AppearanceMode { Light, Dark, System }
public enum ContrastMode { Standard, High }

public sealed record ThemeDescriptor(
    string Id, string Name, string Version, string? Author, string? Description,
    ThemeKind Kind, IReadOnlyList<string> Tags, bool SupportsLight, bool SupportsDark, string? PreviewHint);

/// 主题包 = 只能定义“性格”：颜色/字体/圆角/材质/阴影/动效。禁止定义布局与导航。
public sealed record ThemePackage(string Schema, ThemeDescriptor Descriptor,
    ThemeTokenSet Light, ThemeTokenSet Dark, ThemeMetadata Metadata);

/// 布局 = 独立于主题，用户选择，持久化分离。
public sealed record LayoutProfile(
    string Id, LayoutNavigation Navigation, ShelfLayout Shelf, Density Density,
    WorkbenchLayout Workbench, ReaderLayout Reader);
public enum LayoutNavigation { TopBand, Sidebar, Dock }   // 注意：V1 只实现 TopBand，其余保留枚举
public enum ShelfLayout { Grid, List, Masonry }
public enum Density { Comfortable, Compact, Spacious }
public enum WorkbenchLayout { Stacked, Split }
public enum ReaderLayout { FitPage, FitWidth, DoublePage, Webtoon }

public sealed record ThemeSettings(
    string ThemeId, AppearanceMode Appearance, ContrastMode Contrast, LayoutProfile Layout,
    bool ReducedMotion, bool FollowSystemAccent);

public sealed record ThemeValidationIssue(string Code, string Severity, string Message, string? Path);
public sealed record ThemeValidationResult(bool IsValid, IReadOnlyList<ThemeValidationIssue> Issues);
public sealed record ThemeApplyResult(bool Success, string? AppliedThemeId, IReadOnlyList<ThemeValidationIssue> Issues, bool Recovered);

public interface IThemeService
{
    ThemeDescriptor Current { get; }
    ThemeSettings Settings { get; }
    event EventHandler? Changed;
    Task InitializeAsync(CancellationToken ct = default);
    Task<ThemeApplyResult> ApplyAsync(string themeId, CancellationToken ct = default);
    Task SetAppearanceAsync(AppearanceMode mode);
    Task SetContrastAsync(ContrastMode mode);
    Task SetLayoutAsync(LayoutProfile layout);
    Task SetReducedMotionAsync(bool enabled);
    Task ResetToDefaultAsync();
}

public interface IThemeRegistry
{
    IReadOnlyList<ThemeDescriptor> All { get; }
    ThemeDescriptor? Find(string id);
    ThemePackage Load(string id);
    Task RefreshAsync(CancellationToken ct = default);
    Task<ThemeValidationResult> InstallAsync(Stream packageJson, CancellationToken ct = default);
    Task<bool> UninstallAsync(string id);
    Task<string> ExportAsync(string id);
}

public interface IThemePreviewSession : IDisposable
{
    void Update(string themeId);
    void Commit();
    void Cancel();
}

public interface IThemePreviewEngine { IThemePreviewSession Begin(); }

public interface IThemeValidator { ThemeValidationResult Validate(ThemePackage package); }
public interface IThemePersistence { ThemeSettings Load(); Task SaveAsync(ThemeSettings settings); }
```

**行为约束**：
1. 切换主题/外观/布局**不得**重建窗口、不得改变漫画原图像素、不得丢弃未保存编辑或翻译结果；只替换资源字典并触发布局失效。
2. 主题包损坏/未知 ID → 记录 issue 并回退到 `NewManga.Default`，**不得抛异常导致启动失败**。
3. 旧配置中的旧主题 ID（saber/midnight/sakura/emerald/mono/macos 等）→ 由 `IThemePersistence` 迁移映射到默认主题，且保留外观模式与密度。
4. 系统跟随：`AppearanceMode.System` 监听平台主题变化；`ReducedMotion` 关闭全部动效。
5. 主题包 schema：`newmanga.theme/1`，JSON；内置主题以嵌入资源随包分发，用户主题在 `%APPDATA%/NewManga/themes/*.json`。

---

## 5. 服务层契约（core-bridge 交付，UI 消费）

### 5.1 CreateChapter（补齐审计 P-01）

```csharp
// IHostController / HostController / NullHostController 同步增加
Task<ChapterSummary?> CreateChapterAsync(string bookId, string title, CancellationToken ct = default);
```
- 走 Core 命令 `CreateChapter`（C037，minor=8）；返回新章节；失败返回 null 并记录 `LastError`（沿用现有错误通道风格）。
- `NullHostController` 提供确定性假实现（返回递增章节），供 UI 单测。

### 5.2 Run 控制（补齐审计 P-02）

```csharp
public interface IRunController
{
    Task<RunStartInfo?> StartRunAsync(RunStartRequest request, CancellationToken ct = default);
    Task<RunControlInfo?> ControlRunAsync(string runId, RunControlAction action, CancellationToken ct = default);
    Task<RunControlInfo?> ResumeBlockedRunAsync(string runId, CancellationToken ct = default);
    Task<RunSnapshotInfo?> GetRunSnapshotAsync(string runId, CancellationToken ct = default);
    Task<TaskProjectionInfo?> GetTaskProjectionAsync(string runId, CancellationToken ct = default);
    Task<RunControlInfo?> RetryFailedTargetsAsync(string runId, CancellationToken ct = default);
    Task<bool> CancelExportAsync(string exportId, CancellationToken ct = default); // 已存在则复用
}
public enum RunControlAction { Pause, Resume, Stop, Restart }
public sealed record RunStartRequest(string Command, IReadOnlyDictionary<string, object?> Scope, IReadOnlyDictionary<string, object?>? Overrides, string IdempotencyKey);
```
宿主：`HostController` 实现（`IHostController` 可继承 `IRunController`）；`NullHostController` 提供确定性假实现。
UI 通过 `IRunController` 订阅/轮询 `GetRunSnapshotAsync` + `GetTaskProjectionAsync`（无 push 通道时 500–1000ms 轮询，可注入）。

### 5.3 既有方法（不得改签名）

`IHostController` 已有 36 方法保持原签名与行为（审计 §6）。新增方法只允许**追加**。

---

## 6. 新 UI 结构契约

### 6.1 空间与模式（FUSION_SPEC §2）

```csharp
namespace NewManga.App.Shell.V2;
public enum SpaceId { Library, Studio, Console }         // Ctrl+1/2/3
public enum StudioMode { Page, Batch }                    // Tab
public enum ShellSurface { Spaces, ThemeStudio, ReaderOverlay }  // ThemeStudio/Reader 为覆盖式表面
```
- **唯一状态源**：`ShellState`（`Shell/V2/ShellState.cs`）持有 `CurrentSpace`、`StudioMode`、`Selection`（book/chapter/page/region/multiPage）、各空间滚动与筛选、`Surface` 栈。禁止任何 ViewModel 私存第二份选择。
- 工作区接入接口：

```csharp
public interface IWorkspaceView
{
    SpaceId Space { get; }
    Controls.Control CreateContent();
    void OnActivated(ShellState state);   // 从状态恢复滚动/筛选/聚焦
    void OnDeactivated(ShellState state); // 写回状态
}
```
- 外壳 `AppShellV2`（`Shell/V2/AppShellV2.axaml`）是唯一窗口内容；`MainWindow` 只在 `V11R-INT-1` 由 DSH 切换为承载 `AppShellV2`。

### 6.2 Theme Studio（工作流 C3）

- 独立覆盖式表面 `ShellSurface.ThemeStudio`，入口：TopBand「主题」按钮 + `Ctrl+,`（设置内） + Console「外观」分区。
- 左侧 7 分区：`主题库`（搜索/分类/筛选）、`预览`（书架/工作台/阅读器三视图 + 明暗 + 高对比）、`我的主题`（已安装/收藏/自定义）、`编辑器`（配色/字体/圆角/背景/材质/阴影/动效）、`外观`（浅/深/系统 + 无障碍）、`导入导出`、`恢复默认`。
- 实时预览 = `IThemePreviewEngine` 会话；「应用」提交并持久化，「取消」完整回滚；预览期间禁止重建主界面。
- 独立文件范围：`Views/V2/ThemeStudio/**`、`ViewModels/V2/ThemeStudio/**`、`Shell/V2/ThemeStudio/**`。

### 6.3 快捷键（DESIGN_SYSTEM §8，全局注册，避免冲突）

`Ctrl+1/2/3` 空间、`Tab` Studio 模式、`Ctrl+K` 命令面板、`Ctrl+P` 跳转、`Ctrl+E` 导出、`Ctrl+,` 主题/设置、`F1` 速查、`F5`/`Ctrl+Shift+F` 下一个需要我处理、`Esc` 逐级退出、`J/K` 对象导航、`[`/`]` 页/章节、`Shift+[`/`]` 章节遍历。
实现方式：`Shell/V2/KeyMap.cs` 单一注册表（`ui-shell` 所有），注册冲突在启动时断言失败。

---

## 7. 构建、测试与证据

| 动作 | 命令（在 `apps/desktop-avalonia`） |
|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror` |
| 测试 | `dotnet test NewManga.sln --no-build`（或按项目） |
| Python（如需） | `python -m pytest -q`（仓库根） |
| 旧 UI 脚本 | `pwsh scripts/test.ps1`（有本机绝对路径，干净环境不可用 → 由 `V11R-A-4` 修） |

- 每个任务证据目录 `verification/<TASK-ID>/`，至少：命令、exit code、摘要日志、截图（UI 任务）、偏差记录。
- 提交信息：`<type>(<task-id>): <summary>`，一个任务可多 commit，但 Handoff 必须钉最终 SHA。
- **禁止**：修改冻结设计文件（除追加 DECISION_LOG）、修改他人写域、push 远端、删除用户数据、在 UI 中直连 DB/模型/任意 OS 路径。

## 8. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-10-30 | 初版冻结（DSH） |
