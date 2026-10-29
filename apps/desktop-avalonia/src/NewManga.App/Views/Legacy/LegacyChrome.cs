using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Styling;

namespace NewManga.App.Views.Legacy;

/// <summary>
/// V11R-C-3: minimal, App-local compatibility vocabulary for the one-release legacy shell
/// (<c>--shell=legacy</c>). The legacy theme packs are retired; the old code-built shell still needs a
/// flat layout profile and a named brush surface to stay startable ("degraded: no theme-pack switching,
/// but launches"). Nothing here reads or re-implements the removed NewManga.Theme package: brushes are
/// resolved from the live design-system tokens, and the fixed Sonoma profile replaces the old pack-defined
/// layouts. New shell / Theme Studio code must never use this namespace.
/// </summary>
public static class LegacyChrome
{
    /// <summary>Metric set used by the remaining legacy cards (fixed values after the pack system retired).</summary>
    public static LegacyMetrics Metrics { get; } = new();

    /// <summary>The single fixed profile the legacy shell runs with after C-3.</summary>
    public static LegacyThemePack Current { get; } = new("legacy-fixed", "旧壳（仅保留可启动）", LegacyLayoutProfiles.Sonoma, Metrics);

    /// <summary>Current Avalonia theme variant (the legacy shell can still toggle light/dark appearance).</summary>
    public static ThemeVariant CurrentVariant => Application.Current?.ActualThemeVariant ?? ThemeVariant.Dark;

    /// <summary>True when the active variant is dark; used by legacy card chrome.</summary>
    public static bool IsDark => CurrentVariant == ThemeVariant.Dark;

    public const string SidebarBackground = "SidebarBackground";
    public const string DockBackground = "DockBackground";

    private static readonly IBrush FallbackPanel = new SolidColorBrush(Color.Parse("#1A1C1F"));
    private static readonly IBrush FallbackCanvas = new SolidColorBrush(Color.Parse("#0F1012"));
    private static readonly IBrush FallbackText = new SolidColorBrush(Color.Parse("#E9EAEC"));
    private static readonly IBrush FallbackMuted = new SolidColorBrush(Color.Parse("#A3A8AF"));
    private static readonly IBrush FallbackAccent = new SolidColorBrush(Color.Parse("#E8B264"));
    private static readonly IBrush FallbackAccentOn = new SolidColorBrush(Color.Parse("#1A1C1F"));
    private static readonly IBrush FallbackTransparent = Brushes.Transparent;

    /// <summary>
    /// Resolves a legacy token name against the design-system palette. The legacy shell may run before the
    /// palette is loaded (unit tests construct pages directly), so every key keeps a neutral fallback.
    /// </summary>
    public static IBrush Brush(string token) => token switch
    {
        "Accent" => Resource("Nm.Color.Accent.Base", FallbackAccent),
        "AccentText" => Resource("Nm.Color.Accent.On", FallbackAccentOn),
        "AppBg" => Resource("Nm.Color.Bg.Canvas", FallbackCanvas),
        "CardBg" => Resource("Nm.Color.Bg.Panel", FallbackPanel),
        "CardBorder" => Resource("Nm.Color.Line.Subtle", FallbackPanel),
        "ChipActiveBg" => Resource("Nm.Color.Accent.Muted", FallbackPanel),
        "ChipBg" => Resource("Nm.Color.Bg.Sunken", FallbackPanel),
        "HeaderBg" => Resource("Nm.Color.Bg.Panel", FallbackPanel),
        "HeaderGradient" => Resource("Nm.Color.Bg.Panel", FallbackPanel),
        "MicaFallback" => Resource("Nm.Color.Bg.Canvas", FallbackCanvas),
        "NavActiveBg" => Resource("Nm.Color.Accent.Muted", FallbackPanel),
        "NavActiveText" => Resource("Nm.Color.Accent.Base", FallbackAccent),
        "NavBg" => Resource("Nm.Color.Bg.Sunken", FallbackPanel),
        "ReaderBackground" => Resource("Nm.Color.Bg.Canvas", FallbackCanvas),
        "SearchBg" => Resource("Nm.Color.Bg.Sunken", FallbackPanel),
        "SidebarBackground" => Resource("Nm.Color.Bg.Sunken", FallbackPanel),
        "DockBackground" => Resource("Nm.Color.Bg.Sunken", FallbackPanel),
        "TextPrimary" => Resource("Nm.Color.Text.Primary", FallbackText),
        "TextSecondary" => Resource("Nm.Color.Text.Secondary", FallbackMuted),
        _ => FallbackTransparent,
    };

    private static IBrush Resource(string key, IBrush fallback) =>
        Application.Current?.TryGetResource(key, null, out var value) == true && value is IBrush brush
            ? brush
            : fallback;
}

/// <summary>Legacy fixed-layout kinds (the old pack-defined layout enum is retired).</summary>
public enum LegacyLayoutKind
{
    Sonoma,
    Launchpad,
    Split,
}

/// <summary>Legacy navigation placement (fixed Sonoma profile keeps the title-bar nav).</summary>
public enum LegacyNavPlacement
{
    TitleBar,
    Dock,
    Sidebar,
}

/// <summary>Legacy shelf presentation styles (fixed Sonoma profile uses the grid).</summary>
public enum LegacyShelfStyle
{
    Grid,
    LaunchpadGrid,
    SplitList,
}

/// <summary>Legacy settings structures (fixed Sonoma profile uses the two-column layout).</summary>
public enum LegacySettingsStyle
{
    TwoColumn,
    SingleColumn,
    SplitSections,
}

/// <summary>Flat replacement for the retired per-pack layout profile.</summary>
public sealed class LegacyLayoutProfile
{
    public required LegacyLayoutKind Kind { get; init; }

    public LegacyNavPlacement Nav { get; init; } = LegacyNavPlacement.TitleBar;

    public LegacyShelfStyle Shelf { get; init; } = LegacyShelfStyle.Grid;

    public LegacySettingsStyle Settings { get; init; } = LegacySettingsStyle.TwoColumn;

    public string DisplayName { get; init; } = "旧壳";

    public double ContentMaxWidth { get; init; } = 1600;

    public double LaunchpadBottomInset { get; init; } = 84;

    public double LaunchpadCardWidth { get; init; } = 148;

    public double LaunchpadCardHeight { get; init; } = 148;

    public double ShelfListWidth { get; init; } = 320;

    public double SettingsMaxWidth { get; init; } = 1120;

    public double SettingsNavWidth { get; init; } = 220;

    public double SidebarWidth { get; init; } = 220;

    public double DockHeight { get; init; } = 64;

    public bool UsesDock => Nav == LegacyNavPlacement.Dock;

    public bool UsesSidebar => Nav == LegacyNavPlacement.Sidebar;
}

/// <summary>The one fixed profile the legacy shell keeps after the pack system retires.</summary>
public static class LegacyLayoutProfiles
{
    public static LegacyLayoutProfile Sonoma { get; } = new() { Kind = LegacyLayoutKind.Sonoma };

    public static LegacyLayoutProfile Launchpad { get; } = new()
    {
        Kind = LegacyLayoutKind.Launchpad,
        Nav = LegacyNavPlacement.Dock,
        Shelf = LegacyShelfStyle.LaunchpadGrid,
        Settings = LegacySettingsStyle.SingleColumn,
        DockHeight = 64,
    };
}

/// <summary>Card metrics formerly carried by a theme pack.</summary>
public sealed class LegacyMetrics
{
    public bool IsDark => LegacyChrome.IsDark;

    public double CornerCard => 12;

    public double CornerButton => 8;

    public double CornerSmall => 6;
}

/// <summary>Legacy shell profile wrapper (flat replacement for the retired pack model).</summary>
public sealed class LegacyThemePack
{
    public LegacyThemePack(string id, string label, LegacyLayoutProfile layout, LegacyMetrics metrics)
    {
        Id = id;
        Label = label;
        Layout = layout;
        Metrics = metrics;
    }

    public string Id { get; }

    public string Label { get; }

    public LegacyLayoutProfile Layout { get; }

    public LegacyMetrics Metrics { get; }

    public bool SupportsVariants => true;
}



