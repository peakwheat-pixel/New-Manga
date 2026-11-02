using NewManga.Appearance;
using NewManga.ThemeEngine;

namespace NewManga.App.Services;

/// <summary>
/// FEA-06-PREREQ-2 P5 / AC5 (W-9/Q-32): the app-side compatibility adapter that lets the Theme Engine
/// mirror its settings into the canonical <c>presentation-settings.json</c> without referencing
/// <c>NewManga.Appearance</c>. The mapping target is the sole writer
/// (<see cref="AppearanceCoordinator.SaveAsync"/>), so the coordinator remains the only production write
/// path of the new document.
/// </summary>
/// <remarks>
/// Field mapping is total and documented: the theme id becomes <c>theme.visualThemeId</c>; the persisted
/// light/dark/system mode, contrast, layout and follow-system-accent map one-to-one; the legacy
/// <c>ReducedMotion</c> boolean maps to <c>motion.mode</c> <c>reduce</c> (true) / <c>full</c> (false) so the
/// old on/off semantics are preserved exactly (the three-category flags are left untouched because the
/// legacy document has no equivalent).
/// </remarks>
public sealed class AppearanceThemeSettingsSink : IThemeSettingsSink
{
    private readonly AppearanceCoordinator _coordinator;

    /// <summary>Wraps the app's appearance coordinator (must be loaded before the first write).</summary>
    public AppearanceThemeSettingsSink(AppearanceCoordinator coordinator)
    {
        ArgumentNullException.ThrowIfNull(coordinator);
        _coordinator = coordinator;
    }

    /// <inheritdoc />
    public Task WriteAsync(ThemeSettings settings, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(settings);

        var next = _coordinator.Settings with
        {
            VisualThemeId = settings.ThemeId,
            Mode = Map(settings.Appearance),
            Contrast = Map(settings.Contrast),
            FollowSystemAccent = settings.FollowSystemAccent,
            MotionMode = settings.ReducedMotion ? MotionMode.Reduce : MotionMode.Full,
            Layout = Map(settings.Layout),
        };
        return _coordinator.SaveAsync(next, cancellationToken);
    }

    private static NewManga.Appearance.AppearanceMode Map(NewManga.ThemeEngine.AppearanceMode mode) => mode switch
    {
        NewManga.ThemeEngine.AppearanceMode.Light => NewManga.Appearance.AppearanceMode.Light,
        NewManga.ThemeEngine.AppearanceMode.Dark => NewManga.Appearance.AppearanceMode.Dark,
        _ => NewManga.Appearance.AppearanceMode.System,
    };

    private static AppearanceContrast Map(NewManga.ThemeEngine.ContrastMode mode) =>
        mode == NewManga.ThemeEngine.ContrastMode.High
            ? AppearanceContrast.High
            : AppearanceContrast.Standard;

    private static LayoutSettings Map(LayoutProfile layout) => new()
    {
        Id = layout.Id,
        Navigation = Map(layout.Navigation),
        Shelf = Map(layout.Shelf),
        Density = Map(layout.Density),
        Workbench = Map(layout.Workbench),
        Reader = Map(layout.Reader),
    };

    private static string Map(LayoutNavigation navigation) => navigation switch
    {
        LayoutNavigation.TopBand => "top-band",
        LayoutNavigation.Sidebar => "sidebar",
        LayoutNavigation.Dock => "dock",
        _ => "top-band",
    };

    private static string Map(ShelfLayout shelf) => shelf switch
    {
        ShelfLayout.Grid => "grid",
        ShelfLayout.List => "list",
        ShelfLayout.Masonry => "masonry",
        _ => "grid",
    };

    private static string Map(Density density) => density switch
    {
        Density.Compact => "compact",
        Density.Spacious => "spacious",
        _ => "comfortable",
    };

    private static string Map(WorkbenchLayout workbench) => workbench switch
    {
        WorkbenchLayout.Split => "split",
        _ => "stacked",
    };

    private static string Map(ReaderLayout reader) => reader switch
    {
        ReaderLayout.FitWidth => "fit-width",
        ReaderLayout.DoublePage => "double-page",
        ReaderLayout.Webtoon => "webtoon",
        _ => "fit-page",
    };
}
