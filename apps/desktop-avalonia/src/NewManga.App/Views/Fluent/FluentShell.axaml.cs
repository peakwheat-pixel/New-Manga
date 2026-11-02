using System;
using System.Collections.Generic;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using FluentReaderViewModel = NewManga.App.ViewModels.Fluent.ReaderViewModel;

namespace NewManga.App.Views.Fluent;

/// <summary>
/// FEA-07 slice 2c: the Fluent shell window is a thin host around the reusable
/// <see cref="FluentShellSurface"/> content tree. The surface can be hosted by the stable
/// <c>PresentationWindow</c> for runtime frontend switching; this window keeps the standalone
/// launch path (and the headless tests) unchanged.
/// </summary>
public partial class FluentShell : Window
{
    private readonly FluentShellSurface _surface;

    /// <summary>Four content surfaces hosted by the FEA Fluent shell.</summary>
    public static IReadOnlyList<FluentPage> Pages => FluentShellSurface.Pages;

    public FluentShell() : this(null, null) { }

    public FluentShell(
        AppOptions? options = null,
        FrontendSelection? selection = null,
        IHostController? host = null,
        AppearanceCoordinator? appearance = null,
        DesignSystemThemeManager? themeManager = null)
    {
        InitializeComponent();
        Width = options?.WindowWidth ?? 1180;
        Height = options?.WindowHeight ?? 780;
        MinWidth = ShellLayout.BreakpointNarrow;

        _surface = new FluentShellSurface(options, selection, host, appearance, themeManager);
        _surface.FullScreenRequested += enabled =>
            WindowState = enabled ? WindowState.FullScreen : WindowState.Normal;
        SizeChanged += (_, args) => _surface.SetViewportWidth(args.NewSize.Width);
        _surface.SetViewportWidth(Width);
        Content = _surface;
    }

    /// <summary>The reusable content tree (hosted by this window or by the stable presentation window).</summary>
    public FluentShellSurface Surface => _surface;

    /// <summary>
    /// Named-control lookup deferred to the surface (the window itself carries no XAML content any more,
    /// so the headless tests and diagnostics keep working through the window facade).
    /// </summary>
    public T? FindControl<T>(string name) where T : Control => _surface.FindControl<T>(name);

    public static FluentResponsiveBand GetResponsiveBand(double width) => FluentShellSurface.GetResponsiveBand(width);

    public IHostController? HostController => _surface.HostController;

    public AppearanceCoordinator? Appearance => _surface.Appearance;

    public DesignSystemThemeManager? ThemeManager => _surface.ThemeManager;

    public FluentPage CurrentPage => _surface.CurrentPage;

    public string CurrentPageTitle => _surface.CurrentPageTitle;

    public string CurrentPlaceholderText => _surface.CurrentPlaceholderText;

    public string StatusText => _surface.StatusText;

    public KeyMap ShellKeyMap => _surface.ShellKeyMap;

    public ShelfViewModel ShelfViewModel => _surface.ShelfViewModel;

    public WorkbenchViewModel WorkbenchViewModel => _surface.WorkbenchViewModel;

    public FluentReaderViewModel ReaderViewModel => _surface.ReaderViewModel;

    public SettingsViewModel SettingsViewModel => _surface.SettingsViewModel;

    public ShelfPageView ShelfView => _surface.ShelfView;

    public WorkbenchPageView WorkbenchView => _surface.WorkbenchView;

    public FluentResponsiveBand ResponsiveBand => _surface.ResponsiveBand;

    public Button? NavigationButton(FluentPage page) => _surface.NavigationButton(page);

    public void Navigate(FluentPage page) => _surface.Navigate(page);

    public bool Navigate(string page) => _surface.Navigate(page);

    public bool HandleKeyForTest(Key key, KeyModifiers modifiers, bool textInputFocused = false) =>
        _surface.HandleKeyForTest(key, modifiers, textInputFocused);

    /// <summary>
    /// The standalone composition-root factory: applies the same window-material policy as the other
    /// shells (Mica on Windows 11, opaque fallback elsewhere — C-3-I1).
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
}
