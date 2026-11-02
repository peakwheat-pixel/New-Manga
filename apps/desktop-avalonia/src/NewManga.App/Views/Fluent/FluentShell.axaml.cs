using System;
using System.Collections.Generic;
using Avalonia.Controls;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Shell.V2;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Views.Fluent;

/// <summary>The four product pages the Fluent shell navigates (one level, frozen product scope).</summary>
public enum FluentPage
{
    /// <summary>书架 (library).</summary>
    Library,

    /// <summary>工作台 (workbench).</summary>
    Workbench,

    /// <summary>阅读器 (reader).</summary>
    Reader,

    /// <summary>设置 (settings).</summary>
    Settings,
}

/// <summary>
/// FEA-06-PREREQ-2 P3/AC3: the Fluent shell skeleton. It hosts the frame frozen design 04 §1 defines —
/// top command band (<c>Nm.Size.TopBand</c>), left navigation rail (<c>Nm.Size.TreeWidth</c>) and status
/// band (<c>Nm.Size.StatusBandPage</c>) — with the four product pages as placeholders. Page content is
/// FEA-06 work; this shell only has to start headlessly and navigate between the four pages.
/// </summary>
public partial class FluentShell : Window
{
    /// <summary>Navigation order of the four product pages.</summary>
    public static IReadOnlyList<FluentPage> Pages { get; } =
        [FluentPage.Library, FluentPage.Workbench, FluentPage.Reader, FluentPage.Settings];

    private static readonly IReadOnlyDictionary<FluentPage, (string Title, string Placeholder)> PageCopy =
        new Dictionary<FluentPage, (string, string)>
        {
            [FluentPage.Library] = (
                "书架",
                "书架页占位：书库网格、搜索/排序、书籍详情与导入坞由 FEA-06 实现。"),
            [FluentPage.Workbench] = (
                "工作台",
                "工作台页占位：批量/页面模式、画布与检查器由 FEA-06 实现。"),
            [FluentPage.Reader] = (
                "阅读器",
                "阅读器页占位：翻页、缩放与阅读设置由 FEA-06 实现。"),
            [FluentPage.Settings] = (
                "设置",
                "设置页占位：外观、材质、动效与快捷键由 FEA-06 实现。"),
        };

    private readonly Dictionary<FluentPage, Button> _navButtons = new();
    private readonly TextBlock? _pageTitle;
    private readonly TextBlock? _pagePlaceholder;
    private readonly TextBlock? _statusText;
    private readonly TextBlock? _frontendLabel;
    private readonly string _frontendId;

    /// <summary>Design-time / XAML loader constructor.</summary>
    public FluentShell()
        : this(options: null, selection: null)
    {
    }

    /// <summary>
    /// Creates the shell for the selected frontend. <paramref name="options"/> only supplies geometry.
    /// FEA-06 scope-r2 P0: the composition root injects the single shared services (Host controller,
    /// appearance writer, design-system theme manager) so the four pages can reach data, Draft commands
    /// and appearance persistence without creating a second Host/sidecar or a second appearance writer.
    /// </summary>
    public FluentShell(
        AppOptions? options = null,
        FrontendSelection? selection = null,
        IHostController? host = null,
        AppearanceCoordinator? appearance = null,
        DesignSystemThemeManager? themeManager = null)
    {
        HostController = host;
        Appearance = appearance;
        ThemeManager = themeManager;

        InitializeComponent();

        _frontendId = selection?.EffectiveFrontendId ?? FrontendSelector.CurrentV2FrontendId;
        Width = options?.WindowWidth ?? 1180;
        Height = options?.WindowHeight ?? 780;
        MinWidth = ShellLayout.BreakpointNarrow;

        _pageTitle = this.FindControl<TextBlock>("FluentPageTitle");
        _pagePlaceholder = this.FindControl<TextBlock>("FluentPagePlaceholder");
        _statusText = this.FindControl<TextBlock>("FluentStatusText");
        _frontendLabel = this.FindControl<TextBlock>("FluentFrontendLabel");

        _navButtons[FluentPage.Library] = RequireButton("NavLibrary");
        _navButtons[FluentPage.Workbench] = RequireButton("NavWorkbench");
        _navButtons[FluentPage.Reader] = RequireButton("NavReader");
        _navButtons[FluentPage.Settings] = RequireButton("NavSettings");
        foreach (var pair in _navButtons)
        {
            var page = pair.Key;
            pair.Value.Click += (_, _) => Navigate(page);
        }

        if (_frontendLabel is not null)
        {
            _frontendLabel.Text = $"Fluent frontend · {_frontendId}";
        }

        Navigate(FluentPage.Library);
    }

    /// <summary>
    /// FEA-06 scope-r2 P0: the single shared host controller injected by the composition root. FEA-06
    /// pages read library/Draft state through this instance (never by constructing a second controller).
    /// </summary>
    public IHostController? HostController { get; }

    /// <summary>
    /// FEA-06 scope-r2 P0: the single appearance writer shared with the V2 shell; Fluent pages must save
    /// appearance through <c>SaveAsync</c> on this coordinator (never by writing the JSON directly).
    /// </summary>
    public AppearanceCoordinator? Appearance { get; }

    /// <summary>
    /// FEA-06 scope-r2 P0: the application's single design-system theme manager (tokens/palette/overlays).
    /// </summary>
    public DesignSystemThemeManager? ThemeManager { get; }

    /// <summary>
    /// The composition-root factory: applies the same window-material policy as the other shells
    /// (Mica on Windows 11, opaque fallback elsewhere — C-3-I1) and forwards the injected shared services.
    /// </summary>
    public static FluentShell CreateRoot(
        AppOptions? options = null,
        FrontendSelection? selection = null,
        IHostController? host = null,
        AppearanceCoordinator? appearance = null,
        DesignSystemThemeManager? themeManager = null)
    {
        var shell = new FluentShell(options, selection, host, appearance, themeManager);
        var material = WindowMaterial.ForCurrentOs();
        shell.TransparencyLevelHint = material.Hints
            .Select(hint => hint switch
            {
                "Mica" => WindowTransparencyLevel.Mica,
                "Blur" => WindowTransparencyLevel.Blur,
                _ => WindowTransparencyLevel.None,
            })
            .ToArray();
        return shell;
    }

    /// <summary>The currently selected product page.</summary>
    public FluentPage CurrentPage { get; private set; }

    /// <summary>Title currently rendered for the selected page (empty before the first navigate).</summary>
    public string CurrentPageTitle => _pageTitle?.Text ?? string.Empty;

    /// <summary>Placeholder copy currently rendered for the selected page (empty before the first navigate).</summary>
    public string CurrentPlaceholderText => _pagePlaceholder?.Text ?? string.Empty;

    /// <summary>Status-band text (records the frontend id and the selected page).</summary>
    public string StatusText => _statusText?.Text ?? string.Empty;

    /// <summary>The selected page's navigation button (UI evidence/tests).</summary>
    public Button? NavigationButton(FluentPage page) =>
        _navButtons.TryGetValue(page, out var button) ? button : null;

    /// <summary>Switches the page and updates the skeleton content + status band.</summary>
    public void Navigate(FluentPage page)
    {
        CurrentPage = page;
        var copy = PageCopy[page];
        if (_pageTitle is not null)
        {
            _pageTitle.Text = copy.Title;
        }

        if (_pagePlaceholder is not null)
        {
            _pagePlaceholder.Text = copy.Placeholder;
        }

        foreach (var pair in _navButtons)
        {
            pair.Value.Classes.Set("selected", pair.Key == page);
        }

        if (_statusText is not null)
        {
            _statusText.Text = $"Fluent shell · {_frontendId} · 当前页：{copy.Title}";
        }
    }

    /// <summary>
    /// Maps the existing <c>--page</c> evidence hook onto the four Fluent pages (the same page ids the V2
    /// and legacy shells accept). Unknown ids leave the selection unchanged and return false.
    /// </summary>
    public bool Navigate(string page)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(page);
        var target = page.ToLowerInvariant() switch
        {
            "bookshelf" or "library" => FluentPage.Library,
            "workbench" or "studio" => FluentPage.Workbench,
            "reader" => FluentPage.Reader,
            "settings" or "console" => FluentPage.Settings,
            _ => (FluentPage?)null,
        };

        if (target is not { } page2)
        {
            return false;
        }

        Navigate(page2);
        return true;
    }

    private Button RequireButton(string name) =>
        this.FindControl<Button>(name) ??
        throw new InvalidOperationException($"the Fluent shell skeleton is missing the '{name}' navigation button");
}
