using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Styling;

namespace NewManga.Theme;

public sealed record MotionProfile(TimeSpan Fast, TimeSpan Normal, TimeSpan Slow, bool Reduced)
{
    public TimeSpan For(string key) => Reduced
        ? TimeSpan.Zero
        : key switch
        {
            "fast" => Fast,
            "slow" => Slow,
            _ => Normal,
        };
}

/// <summary>
/// THEME-MACOS-1: non-color design tokens (shape + shadow). Colors stay in
/// <see cref="ThemePack.Tokens"/> / <see cref="ThemePack.Materials"/>; geometry and shadows live here so a
/// pack can define its own chrome without changing every other pack's look.
/// </summary>
public sealed record ThemePackMetrics(
    double CornerWindow,
    double CornerCard,
    double CornerButton,
    double CornerSmall,
    string CardShadowLight,
    string CardShadowDark)
{
    /// <summary>Legacy geometry: existing packs keep corner 12/12/8/6 and no box shadow.</summary>
    public static ThemePackMetrics Default { get; } = new(12, 12, 8, 6, string.Empty, string.Empty);

    public string CardShadowFor(ThemeVariant variant) => IsDark(variant) ? CardShadowDark : CardShadowLight;

    public static bool IsDark(ThemeVariant variant) =>
        string.Equals(variant.Key?.ToString(), "Dark", StringComparison.Ordinal);
}

/// <summary>
/// THEME-MACOS-LAYOUTS-1: which shell layout a pack requests. Kept in the Theme module so a theme pack
/// owns its layout (not only its colors) and the shell never hard-codes a pack id.
/// </summary>
public enum LayoutKind
{
    /// <summary>THEME-MACOS-1 layout: centred nav in the title bar, 1400 centred grid, two-column settings.</summary>
    Sonoma,

    /// <summary>Full-screen Launchpad grid with a floating bottom Dock and a single centred settings column.</summary>
    Launchpad,

    /// <summary>Finder-style left sidebar, book list + right content grid, split settings sections.</summary>
    Split,
}

/// <summary>Where the four primary navigation entries live.</summary>
public enum NavPlacement
{
    /// <summary>Centred inside the 48px title bar (Sonoma / the legacy six packs).</summary>
    TitleBar,

    /// <summary>Floating rounded Dock capsule at the bottom edge of the window.</summary>
    Dock,

    /// <summary>Vertical sidebar on the left edge, below the title bar strip.</summary>
    Sidebar,
}

/// <summary>Bookshelf page structure.</summary>
public enum ShelfStyle
{
    /// <summary>Gradient header + search card + 1400-wide centred 3:4 grid (Sonoma).</summary>
    CenteredGrid,

    /// <summary>Compact top bar + large 168x220 icon grid centred at 1200 with a bottom inset for the Dock.</summary>
    LaunchpadGrid,

    /// <summary>260px book list on the left + search/grid/detail on the right.</summary>
    SplitList,
}

/// <summary>Settings page structure.</summary>
public enum SettingsStyle
{
    /// <summary>320px theme card + scrolling card column (Sonoma).</summary>
    TwoColumn,

    /// <summary>Single centred column (max width from <see cref="LayoutProfile.SettingsMaxWidth"/>).</summary>
    SingleColumn,

    /// <summary>Left section directory + right section content, switched by visibility only.</summary>
    SplitSections,
}

/// <summary>
/// THEME-MACOS-LAYOUTS-1: one layout profile = navigation placement + page structures + key geometry.
/// A <see cref="ThemePack"/> may carry one; packs that do not carry one fall back to
/// <see cref="LayoutProfiles.Sonoma"/>, which is exactly the pre-existing (THEME-MACOS-1) layout — so the
/// legacy six packs keep their layout with zero visual change.
/// </summary>
public sealed record LayoutProfile(
    LayoutKind Kind,
    string Label,
    NavPlacement Nav,
    ShelfStyle Shelf,
    SettingsStyle Settings,
    double DockHeight,
    double SidebarWidth,
    double ShelfListWidth,
    double SettingsNavWidth,
    double LaunchpadCardWidth,
    double LaunchpadCardHeight,
    double ContentMaxWidth,
    double SettingsMaxWidth)
{
    public bool UsesDock => Nav == NavPlacement.Dock;

    public bool UsesSidebar => Nav == NavPlacement.Sidebar;

    /// <summary>Bottom inset the Launchpad grid must leave free so the floating Dock never covers a card.</summary>
    public double LaunchpadBottomInset => UsesDock ? DockHeight + 44 : 0;
}

/// <summary>The three frozen macOS layout profiles (design table in doc/tasks/THEME-MACOS-LAYOUTS-1.md).</summary>
public static class LayoutProfiles
{
    /// <summary>THEME-MACOS-1 layout, reused verbatim so the legacy six packs never move.</summary>
    public static LayoutProfile Sonoma { get; } = new(
        LayoutKind.Sonoma,
        "macOS 风",
        NavPlacement.TitleBar,
        ShelfStyle.CenteredGrid,
        SettingsStyle.TwoColumn,
        DockHeight: 0,
        SidebarWidth: 0,
        ShelfListWidth: 0,
        SettingsNavWidth: 0,
        LaunchpadCardWidth: 168,
        LaunchpadCardHeight: 220,
        ContentMaxWidth: 1400,
        SettingsMaxWidth: 0);

    public static LayoutProfile Launchpad { get; } = new(
        LayoutKind.Launchpad,
        "macOS 启动台",
        NavPlacement.Dock,
        ShelfStyle.LaunchpadGrid,
        SettingsStyle.SingleColumn,
        DockHeight: 76,
        SidebarWidth: 0,
        ShelfListWidth: 0,
        SettingsNavWidth: 0,
        LaunchpadCardWidth: 168,
        LaunchpadCardHeight: 220,
        ContentMaxWidth: 1200,
        SettingsMaxWidth: 900);

    public static LayoutProfile Split { get; } = new(
        LayoutKind.Split,
        "macOS 分栏",
        NavPlacement.Sidebar,
        ShelfStyle.SplitList,
        SettingsStyle.SplitSections,
        DockHeight: 0,
        SidebarWidth: 220,
        ShelfListWidth: 260,
        SettingsNavWidth: 240,
        LaunchpadCardWidth: 168,
        LaunchpadCardHeight: 220,
        ContentMaxWidth: 1400,
        SettingsMaxWidth: 0);

    public static IReadOnlyList<LayoutProfile> All { get; } = new[] { Sonoma, Launchpad, Split };

    public static LayoutProfile For(LayoutKind kind) => kind switch
    {
        LayoutKind.Launchpad => Launchpad,
        LayoutKind.Split => Split,
        _ => Sonoma,
    };
}

/// <summary>
/// AC2 ThemePack: one skin = manifest + tokens + control-theme keys + materials + motion + icons.
/// Hot switching swaps a ThemeDictionaries resource dictionary in place: controls use DynamicResource,
/// so no control is recreated and no restart is needed.
/// THEME-MACOS-1 extends this record backwards-compatibly: <see cref="DarkTokens"/> /
/// <see cref="DarkMaterials"/> are optional (null = reuse Tokens/Materials, exactly the old behaviour),
/// and <see cref="Metrics"/> / <see cref="FontFamily"/> default to the legacy geometry and font stack.
/// </summary>
public sealed record ThemePack(
    string Id,
    string Label,
    string Manifest,
    bool IsDark,
    IReadOnlyDictionary<string, string> Tokens,
    IReadOnlyDictionary<string, string> Materials,
    IReadOnlyDictionary<string, string> ControlThemes,
    MotionProfile Motion,
    IReadOnlyDictionary<string, string> Icons)
{
    /// <summary>Optional Dark token override; null/empty keeps the legacy "same tokens both variants" behaviour.</summary>
    public IReadOnlyDictionary<string, string>? DarkTokens { get; init; }

    /// <summary>Optional Dark material override; null/empty reuses <see cref="Materials"/>.</summary>
    public IReadOnlyDictionary<string, string>? DarkMaterials { get; init; }

    public ThemePackMetrics Metrics { get; init; } = ThemePackMetrics.Default;

    /// <summary>Font stack string bridged to <c>AppFontFamily</c> (no font binaries ship with the app).</summary>
    public string FontFamily { get; init; } = ThemePacks.DefaultFontFamily;

    /// <summary>
    /// THEME-MACOS-LAYOUTS-1: shell/shelf/settings layout this pack requests. Defaults to the Sonoma layout
    /// (the pre-existing structure), so every pack without an explicit profile keeps the old layout exactly.
    /// </summary>
    public LayoutProfile Layout { get; init; } = LayoutProfiles.Sonoma;

    /// <summary>True when this pack drives the macOS shell chrome (traffic lights + title-bar fill).</summary>
    public bool IsMacOsPack =>
        Id.StartsWith("macos-", StringComparison.Ordinal);

    /// <summary>True when this single pack carries its own Light and Dark token sets.</summary>
    public bool SupportsVariants => DarkTokens is { Count: > 0 };

    public bool ReducedMotion => Motion.Reduced;

    public ThemePack WithReducedMotion(bool reduced) => this with
    {
        Motion = new MotionProfile(Motion.Fast, Motion.Normal, Motion.Slow, reduced),
    };
}

public static class ThemePacks
{
    public const string SaberPurpleId = "saber-purple";

    /// <summary>THEME-MACOS-1 pack id (single pack, two token sets; THEME-MACOS-LAYOUTS-1 keeps its layout).</summary>
    public const string MacOsSonomaId = "macos-sonoma";

    /// <summary>THEME-MACOS-LAYOUTS-1: Launchpad layout pack (full-screen grid + bottom Dock).</summary>
    public const string MacOsLaunchpadId = "macos-launchpad";

    /// <summary>THEME-MACOS-LAYOUTS-1: Split layout pack (left sidebar + split pages).</summary>
    public const string MacOsSplitId = "macos-split";

    /// <summary>Every macOS pack id, in registration order (all share the Sonoma color spec).</summary>
    public static IReadOnlyList<string> MacOsPackIds { get; } =
        new[] { MacOsSonomaId, MacOsLaunchpadId, MacOsSplitId };

    /// <summary>True for any of the three macOS packs (drives traffic lights / title-bar chrome).</summary>
    public static bool IsMacOsPack(ThemePack pack) => pack.IsMacOsPack;

    /// <summary>Legacy font stack shared by every pre-existing pack (system fallbacks only, no bundled font).</summary>
    public const string DefaultFontFamily = "Segoe UI, Microsoft YaHei UI, PingFang SC, Noto Sans CJK SC, sans-serif";

    /// <summary>macOS pack font stack: prefers Segoe UI Variable Text / Inter, keeps the CJK system fallbacks.</summary>
    public const string MacOsFontFamily =
        "Segoe UI Variable Text, Inter, Segoe UI, Microsoft YaHei UI, PingFang SC, Noto Sans CJK SC, sans-serif";

    private static readonly IReadOnlyDictionary<string, string> IconSet = new Dictionary<string, string>
    {
        ["bookshelf"] = "\uE8F1",
        ["workbench"] = "\uE9D9",
        ["reader"] = "\uE7C3",
        ["settings"] = "\uE713",
        ["search"] = "\uE721",
        ["add"] = "\uE710",
        ["refresh"] = "\uE72C",
        ["back"] = "\uE72B",
    };

    private static readonly IReadOnlyDictionary<string, string> ControlThemeSet = new Dictionary<string, string>
    {
        ["nm.navbutton"] = "class:nm-nav",
        ["nm.bookcard"] = "class:nm-bookcard",
        ["nm.chip"] = "class:nm-chip",
        ["nm.searchbox"] = "class:nm-search",
        ["nm.primarybutton"] = "class:nm-primary",
    };

    private static readonly MotionProfile Motion = new(
        TimeSpan.FromMilliseconds(90),
        TimeSpan.FromMilliseconds(160),
        TimeSpan.FromMilliseconds(240),
        Reduced: false);

    public static ThemePack SaberPurple { get; } = Create(
        SaberPurpleId,
        "Saber Purple",
        isDark: false,
        tokens: new Dictionary<string, string>
        {
            ["AppBg"] = "#F5F3FA",
            ["HeaderBg"] = "#FFFFFF",
            ["CardBg"] = "#FFFFFF",
            ["CardBorder"] = "#E6E1F2",
            ["TextPrimary"] = "#241C33",
            ["TextSecondary"] = "#6B647D",
            ["Accent"] = "#764BA2",
            ["AccentText"] = "#FFFFFF",
            ["ChipBg"] = "#F1EDF9",
            ["ChipActiveBg"] = "#764BA2",
            ["SearchBg"] = "#FFFFFF",
            ["NavBg"] = "#F0EBF7",
            ["NavActiveBg"] = "#764BA2",
            ["EmptyBg"] = "#FBF9FE",
        },
        materials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#667EEA",
            ["HeaderGradientEnd"] = "#764BA2",
            ["CardShadow"] = "#22000000",
            ["MicaFallback"] = "#F5F3FA",
        });

    public static ThemePack SaberLight { get; } = Create(
        "saber-light",
        "Saber Light",
        isDark: false,
        tokens: new Dictionary<string, string>
        {
            ["AppBg"] = "#FAFAFC",
            ["HeaderBg"] = "#FFFFFF",
            ["CardBg"] = "#FFFFFF",
            ["CardBorder"] = "#E4E7EE",
            ["TextPrimary"] = "#1F2430",
            ["TextSecondary"] = "#5C6675",
            ["Accent"] = "#4F46E5",
            ["AccentText"] = "#FFFFFF",
            ["ChipBg"] = "#EEF0F8",
            ["ChipActiveBg"] = "#4F46E5",
            ["SearchBg"] = "#FFFFFF",
            ["NavBg"] = "#F2F4F9",
            ["NavActiveBg"] = "#4F46E5",
            ["EmptyBg"] = "#F7F8FC",
        },
        materials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#8B9BF3",
            ["HeaderGradientEnd"] = "#6366F1",
            ["CardShadow"] = "#1A000000",
            ["MicaFallback"] = "#FAFAFC",
        });

    public static ThemePack Midnight { get; } = Create(
        "midnight",
        "Midnight",
        isDark: true,
        tokens: new Dictionary<string, string>
        {
            ["AppBg"] = "#101322",
            ["HeaderBg"] = "#171B2E",
            ["CardBg"] = "#1A1F36",
            ["CardBorder"] = "#2A3150",
            ["TextPrimary"] = "#EDEFF7",
            ["TextSecondary"] = "#9AA3BE",
            ["Accent"] = "#8B9BF3",
            ["AccentText"] = "#0B0F1C",
            ["ChipBg"] = "#232A45",
            ["ChipActiveBg"] = "#8B9BF3",
            ["SearchBg"] = "#1A1F36",
            ["NavBg"] = "#141828",
            ["NavActiveBg"] = "#8B9BF3",
            ["EmptyBg"] = "#141828",
        },
        materials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#2B2350",
            ["HeaderGradientEnd"] = "#151A2E",
            ["CardShadow"] = "#66000000",
            ["MicaFallback"] = "#101322",
        });

    public static ThemePack Sakura { get; } = Create(
        "sakura",
        "Sakura",
        isDark: false,
        tokens: new Dictionary<string, string>
        {
            ["AppBg"] = "#FDF5F7",
            ["HeaderBg"] = "#FFFFFF",
            ["CardBg"] = "#FFFFFF",
            ["CardBorder"] = "#F2DDE4",
            ["TextPrimary"] = "#3A2430",
            ["TextSecondary"] = "#7D6571",
            ["Accent"] = "#D96C8E",
            ["AccentText"] = "#FFFFFF",
            ["ChipBg"] = "#FBEAF0",
            ["ChipActiveBg"] = "#D96C8E",
            ["SearchBg"] = "#FFFFFF",
            ["NavBg"] = "#F9EDF1",
            ["NavActiveBg"] = "#D96C8E",
            ["EmptyBg"] = "#FEF8FA",
        },
        materials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#F3A6C0",
            ["HeaderGradientEnd"] = "#D96C8E",
            ["CardShadow"] = "#1A000000",
            ["MicaFallback"] = "#FDF5F7",
        });

    public static ThemePack Emerald { get; } = Create(
        "emerald",
        "Emerald",
        isDark: true,
        tokens: new Dictionary<string, string>
        {
            ["AppBg"] = "#0F1A17",
            ["HeaderBg"] = "#152420",
            ["CardBg"] = "#182A25",
            ["CardBorder"] = "#28443B",
            ["TextPrimary"] = "#E8F5EF",
            ["TextSecondary"] = "#96B5A8",
            ["Accent"] = "#3DDC97",
            ["AccentText"] = "#08211A",
            ["ChipBg"] = "#1F3630",
            ["ChipActiveBg"] = "#3DDC97",
            ["SearchBg"] = "#182A25",
            ["NavBg"] = "#12201C",
            ["NavActiveBg"] = "#3DDC97",
            ["EmptyBg"] = "#12201C",
        },
        materials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#1D5C4A",
            ["HeaderGradientEnd"] = "#103228",
            ["CardShadow"] = "#66000000",
            ["MicaFallback"] = "#0F1A17",
        });

    public static ThemePack Mono { get; } = Create(
        "mono",
        "Mono",
        isDark: false,
        tokens: new Dictionary<string, string>
        {
            ["AppBg"] = "#F6F6F6",
            ["HeaderBg"] = "#FFFFFF",
            ["CardBg"] = "#FFFFFF",
            ["CardBorder"] = "#E2E2E2",
            ["TextPrimary"] = "#1C1C1C",
            ["TextSecondary"] = "#626262",
            ["Accent"] = "#3A3A3A",
            ["AccentText"] = "#FFFFFF",
            ["ChipBg"] = "#EEEEEE",
            ["ChipActiveBg"] = "#3A3A3A",
            ["SearchBg"] = "#FFFFFF",
            ["NavBg"] = "#F0F0F0",
            ["NavActiveBg"] = "#3A3A3A",
            ["EmptyBg"] = "#FBFBFB",
        },
        materials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#6A6A6A",
            ["HeaderGradientEnd"] = "#3A3A3A",
            ["CardShadow"] = "#1A000000",
            ["MicaFallback"] = "#F6F6F6",
        });

    // THEME-MACOS-LAYOUTS-1: the three macOS packs share one color spec (frozen by THEME-MACOS-1), one
    // metric/motion/font contract and one icon set; only the LayoutProfile differs. Launchpad/Split
    // micro-adjust the page / sidebar / dock background (still WCAG-passing, checked by the tests) so
    // each layout reads as its own skin.
    private static readonly IReadOnlyDictionary<string, string> MacLightTokens = new Dictionary<string, string>
    {
        ["AppBg"] = "#F5F5F7",
        ["HeaderBg"] = "#E6FFFFFF",
        ["CardBg"] = "#FFFFFF",
        ["CardBorder"] = "#D2D2D7",
        ["TextPrimary"] = "#1D1D1F",
        ["TextSecondary"] = "#6E6E73",
        ["Accent"] = "#007AFF",
        ["AccentText"] = "#FFFFFF",
        ["ChipBg"] = "#F0F0F3",
        ["ChipActiveBg"] = "#007AFF",
        ["SearchBg"] = "#FFFFFF",
        ["NavBg"] = "#ECECEF",
        ["NavActiveBg"] = "#D6E9FF",
        ["NavActiveText"] = "#003E7E",
        ["EmptyBg"] = "#FAFAFC",
        ["Danger"] = "#FF3B30",
        ["Success"] = "#34C759",
        ["Warning"] = "#FF9500",
        ["Separator"] = "#D2D2D7",
        // THEME-MACOS-LAYOUTS-1: chrome surfaces for the Dock / Sidebar layouts (unused by Sonoma).
        ["SidebarBg"] = "#ECECEF",
        ["DockBg"] = "#E8F2F2F7",
    };

    private static readonly IReadOnlyDictionary<string, string> MacDarkTokens = new Dictionary<string, string>
    {
        ["AppBg"] = "#1E1E1E",
        ["HeaderBg"] = "#E6252527",
        ["CardBg"] = "#2C2C2E",
        ["CardBorder"] = "#3A3A3C",
        ["TextPrimary"] = "#F5F5F7",
        ["TextSecondary"] = "#98989D",
        ["Accent"] = "#0A84FF",
        ["AccentText"] = "#FFFFFF",
        ["ChipBg"] = "#3A3A3C",
        ["ChipActiveBg"] = "#0A84FF",
        ["SearchBg"] = "#2C2C2E",
        ["NavBg"] = "#252527",
        ["NavActiveBg"] = "#1F3A5F",
        ["NavActiveText"] = "#D7E9FF",
        ["EmptyBg"] = "#1E1E1E",
        ["Danger"] = "#FF453A",
        ["Success"] = "#32D74B",
        ["Warning"] = "#FF9F0A",
        ["Separator"] = "#3A3A3C",
        ["SidebarBg"] = "#252527",
        ["DockBg"] = "#E82C2C2E",
    };

    private static readonly IReadOnlyDictionary<string, string> MacLightMaterials = new Dictionary<string, string>
    {
        ["HeaderGradientStart"] = "#FDFDFE",
        ["HeaderGradientEnd"] = "#ECECEF",
        ["CardShadow"] = "#14000000",
        ["MicaFallback"] = "#F5F5F7",
    };

    private static readonly IReadOnlyDictionary<string, string> MacDarkMaterials = new Dictionary<string, string>
    {
        ["HeaderGradientStart"] = "#2C2C2E",
        ["HeaderGradientEnd"] = "#1E1E1E",
        ["CardShadow"] = "#66000000",
        ["MicaFallback"] = "#1E1E1E",
    };

    private static readonly ThemePackMetrics MacMetrics = new(
        CornerWindow: 12,
        CornerCard: 14,
        CornerButton: 8,
        CornerSmall: 6,
        CardShadowLight: "0 1 3 0 #14000000",
        CardShadowDark: "0 1 3 0 #66000000");

    private static readonly MotionProfile MacMotion = new(
        TimeSpan.FromMilliseconds(120),
        TimeSpan.FromMilliseconds(160),
        TimeSpan.FromMilliseconds(240),
        Reduced: false);

    /// <summary>
    /// THEME-MACOS-1: macOS Sonoma skin. One pack carries both token sets (Light in Tokens/Materials,
    /// Dark in DarkTokens/DarkMaterials); the plugin lists it once and ThemePackService switches variants.
    /// Spec source: doc/tasks/THEME-MACOS-1.md「设计规格（用户冻结）」. System fonts only (no bundled font).
    /// THEME-MACOS-LAYOUTS-1 keeps this exact color spec and gives it the Sonoma layout profile.
    /// </summary>
    public static ThemePack MacOsSonoma { get; } =
        CreateMacPack(MacOsSonomaId, "macOS 风", LayoutProfiles.Sonoma);

    /// <summary>
    /// THEME-MACOS-LAYOUTS-1「macOS 启动台」: full-screen Launchpad icon grid, floating bottom Dock,
    /// single centred settings column. Same macOS color spec, slightly lighter/darker page background.
    /// </summary>
    public static ThemePack MacOsLaunchpad { get; } = CreateMacPack(
        MacOsLaunchpadId,
        "macOS 启动台",
        LayoutProfiles.Launchpad,
        lightTokens: Derive(MacLightTokens, ("AppBg", "#EFEFF2"), ("SidebarBg", "#E7E7EB"), ("DockBg", "#E8F7F7FA")),
        darkTokens: Derive(MacDarkTokens, ("AppBg", "#1A1A1C"), ("SidebarBg", "#232325"), ("DockBg", "#E82C2C2E")),
        lightMaterials: Derive(MacLightMaterials, ("MicaFallback", "#EFEFF2")),
        darkMaterials: Derive(MacDarkMaterials, ("MicaFallback", "#1A1A1C")));

    /// <summary>
    /// THEME-MACOS-LAYOUTS-1「macOS 分栏」: Finder-style left sidebar, book list + right grid/detail, and
    /// system-settings-style section directory. Same macOS color spec, slightly cooler page/sidebar tone.
    /// </summary>
    public static ThemePack MacOsSplit { get; } = CreateMacPack(
        MacOsSplitId,
        "macOS 分栏",
        LayoutProfiles.Split,
        lightTokens: Derive(MacLightTokens, ("AppBg", "#F2F2F5"), ("SidebarBg", "#E9E9ED"), ("DockBg", "#E8F2F2F7")),
        darkTokens: Derive(MacDarkTokens, ("AppBg", "#202022"), ("SidebarBg", "#28282A"), ("DockBg", "#E82C2C2E")),
        lightMaterials: Derive(MacLightMaterials, ("MicaFallback", "#F2F2F5")),
        darkMaterials: Derive(MacDarkMaterials, ("MicaFallback", "#202022")));

    public static IReadOnlyList<ThemePack> All { get; } = new[]
    {
        SaberPurple, SaberLight, Midnight, Sakura, Emerald, Mono,
        MacOsSonoma, MacOsLaunchpad, MacOsSplit,
    };

    public static ThemePack Default => SaberPurple;

    public static ThemePack ById(string id)
    {
        foreach (var pack in All)
        {
            if (string.Equals(pack.Id, id, StringComparison.Ordinal))
            {
                return pack;
            }
        }

        return Default;
    }

    /// <summary>
    /// THEME-MACOS-LAYOUTS-1: one macOS pack = the shared dual-token color spec + metrics/motion/font +
    /// the layout profile the shell should switch to.
    /// </summary>
    private static ThemePack CreateMacPack(
        string id,
        string label,
        LayoutProfile layout,
        IReadOnlyDictionary<string, string>? lightTokens = null,
        IReadOnlyDictionary<string, string>? darkTokens = null,
        IReadOnlyDictionary<string, string>? lightMaterials = null,
        IReadOnlyDictionary<string, string>? darkMaterials = null) =>
        Create(
            id,
            label,
            isDark: false,
            tokens: lightTokens ?? MacLightTokens,
            materials: lightMaterials ?? MacLightMaterials,
            darkTokens: darkTokens ?? MacDarkTokens,
            darkMaterials: darkMaterials ?? MacDarkMaterials,
            metrics: MacMetrics,
            fontFamily: MacOsFontFamily,
            motion: MacMotion) with
        {
            Layout = layout,
        };

    /// <summary>Copy-on-write token override so the three macOS packs never mutate the shared spec.</summary>
    private static IReadOnlyDictionary<string, string> Derive(
        IReadOnlyDictionary<string, string> source,
        params (string Key, string Value)[] overrides)
    {
        var copy = new Dictionary<string, string>(source, StringComparer.Ordinal);
        foreach (var (key, value) in overrides)
        {
            copy[key] = value;
        }

        return copy;
    }

    private static ThemePack Create(
        string id,
        string label,
        bool isDark,
        IReadOnlyDictionary<string, string> tokens,
        IReadOnlyDictionary<string, string> materials,
        IReadOnlyDictionary<string, string>? darkTokens = null,
        IReadOnlyDictionary<string, string>? darkMaterials = null,
        ThemePackMetrics? metrics = null,
        string? fontFamily = null,
        MotionProfile? motion = null) =>
        new(
            id,
            label,
            $"{{\"schema\":\"nm.themepack/1\",\"id\":\"{id}\",\"label\":\"{label}\",\"isDark\":{isDark.ToString().ToLowerInvariant()}," +
            "\"parts\":[\"manifest\",\"tokens\",\"controlthemes\",\"materials\",\"motion\",\"icons\"]}",
            isDark,
            tokens,
            materials,
            ControlThemeSet,
            motion ?? Motion,
            IconSet)
        {
            DarkTokens = darkTokens,
            DarkMaterials = darkMaterials,
            Metrics = metrics ?? ThemePackMetrics.Default,
            FontFamily = fontFamily ?? DefaultFontFamily,
        };
}

/// <summary>
/// AC2 theme service. Applies packs by swapping one merged ResourceDictionary whose ThemeDictionaries
/// hold Light/Dark variants, so DynamicResource consumers update without recreation or restart.
/// THEME-MACOS-1 adds <see cref="ApplyVariant"/> / <see cref="CurrentVariant"/> for packs that carry
/// both token sets; existing <see cref="Apply(Application, ThemePack)"/> semantics are unchanged.
/// </summary>
public static class ThemePackService
{
    public const string AppBackground = "AppBg";
    public const string HeaderBackground = "HeaderBg";
    public const string HeaderGradientStart = "HeaderGradientStart";
    public const string HeaderGradientEnd = "HeaderGradientEnd";
    public const string CardBackground = "CardBg";
    public const string CardBorder = "CardBorder";
    public const string TextPrimary = "TextPrimary";
    public const string TextSecondary = "TextSecondary";
    public const string Accent = "Accent";
    public const string AccentText = "AccentText";
    public const string ChipBackground = "ChipBg";
    public const string ChipActiveBackground = "ChipActiveBg";
    public const string SearchBackground = "SearchBg";
    public const string NavBackground = "NavBg";
    public const string NavActiveBackground = "NavActiveBg";
    public const string NavActiveText = "NavActiveText";
    public const string EmptyBackground = "EmptyBg";
    public const string MicaFallback = "MicaFallback";

    /// <summary>THEME-MACOS-LAYOUTS-1: sidebar surface token (Synced fallback: NavBg for packs without it).</summary>
    public const string SidebarBackground = "SidebarBg";

    /// <summary>THEME-MACOS-LAYOUTS-1: floating Dock surface token (fallback: CardBg).</summary>
    public const string DockBackground = "DockBg";

    /// <summary>Font stack resource key consumed by AppStyles.axaml Window style (THEME-MACOS-1).</summary>
    public const string AppFontFamily = "AppFontFamily";

    /// <summary>Card shadow resource key (THEME-MACOS-1): a BoxShadows string, empty = no shadow.</summary>
    public const string CardShadowBox = "CardShadowBox";

    private static ResourceDictionary? _active;
    private static long _switchTicks;

    public static ThemePack Current { get; private set; } = ThemePacks.Default;

    /// <summary>THEME-MACOS-1: the variant currently applied (Light or Dark).</summary>
    public static ThemeVariant CurrentVariant { get; private set; } = ThemeVariant.Light;

    /// <summary>Duration of the last apply (used by the p95 regression test).</summary>
    public static TimeSpan LastApplyDuration { get; private set; }

    public static TimeSpan LastSwitchDuration => TimeSpan.FromTicks(_switchTicks);

    public static void Apply(Application application, ThemePack pack)
    {
        var variant = pack.IsDark ? ThemeVariant.Dark : ThemeVariant.Light;
        ApplyCore(application, pack, variant);
    }

    /// <summary>
    /// THEME-MACOS-1: switches only the Light/Dark variant of the pack that is already applied.
    /// Packs without <see cref="ThemePack.DarkTokens"/> keep their existing token values in Dark
    /// (BuildVariant falls back to the pack's single token set), so old themes behave exactly as before.
    /// </summary>
    public static void ApplyVariant(Application application, ThemeVariant variant) =>
        ApplyCore(application, Current, variant);

    public static void ApplyDefault(Application application) => Apply(application, ThemePacks.Default);

    /// <summary>Resolves a token brush from the live resource stack (test/evidence helper).</summary>
    public static IBrush Brush(string key)
    {
        if (Application.Current is { } application &&
            application.TryGetResource(key, application.ActualThemeVariant, out var value) &&
            value is IBrush brush)
        {
            return brush;
        }

        return Brushes.Magenta;
    }

    public static Color ColorOf(string key) => Brush(key) is ISolidColorBrush solid ? solid.Color : Colors.Magenta;

    private static void ApplyCore(Application application, ThemePack pack, ThemeVariant variant)
    {
        var start = System.Diagnostics.Stopwatch.GetTimestamp();
        if (_active is not null)
        {
            application.Resources.MergedDictionaries.Remove(_active);
        }

        var root = new ResourceDictionary
        {
            ThemeDictionaries =
            {
                [ThemeVariant.Light] = BuildVariant(pack, ThemeVariant.Light),
                [ThemeVariant.Dark] = BuildVariant(pack, ThemeVariant.Dark),
            },
        };

        application.Resources.MergedDictionaries.Add(root);
        _active = root;
        Current = pack;
        CurrentVariant = variant;
        application.RequestedThemeVariant = variant;
        LastApplyDuration = System.Diagnostics.Stopwatch.GetElapsedTime(start);
        _switchTicks = LastApplyDuration.Ticks;
    }

    private static ResourceDictionary BuildVariant(ThemePack pack, ThemeVariant variant)
    {
        var dark = ThemePackMetrics.IsDark(variant);
        var tokens = dark && pack.DarkTokens is { Count: > 0 } ? pack.DarkTokens : pack.Tokens;
        var materials = dark && pack.DarkMaterials is { Count: > 0 } ? pack.DarkMaterials : pack.Materials;

        var dictionary = new ResourceDictionary();
        foreach (var pair in tokens)
        {
            dictionary[pair.Key] = new SolidColorBrush(Color.Parse(pair.Value));
        }

        // THEME-MACOS-1: legacy packs have no NavActiveText token; fall back to AccentText so the old
        // six themes keep their exact nav-selected colour. macOS defines it per variant.
        if (!tokens.ContainsKey(NavActiveText))
        {
            dictionary[NavActiveText] = new SolidColorBrush(Color.Parse(tokens[AccentText]));
        }

        // THEME-MACOS-LAYOUTS-1: the Dock / Sidebar chrome tokens only exist on the macOS packs. Legacy
        // packs fall back to their nav/card surface so the hidden hosts never resolve to magenta.
        if (!tokens.ContainsKey(SidebarBackground))
        {
            dictionary[SidebarBackground] = dictionary[NavBackground];
        }

        if (!tokens.ContainsKey(DockBackground))
        {
            dictionary[DockBackground] = dictionary[CardBackground];
        }

        foreach (var pair in materials)
        {
            dictionary[pair.Key] = new SolidColorBrush(Color.Parse(pair.Value));
        }

        dictionary["HeaderGradient"] = new LinearGradientBrush
        {
            StartPoint = new RelativePoint(0, 0, RelativeUnit.Relative),
            EndPoint = new RelativePoint(1, 0.2, RelativeUnit.Relative),
            GradientStops =
            {
                new GradientStop(Color.Parse(materials[HeaderGradientStart]), 0),
                new GradientStop(Color.Parse(materials[HeaderGradientEnd]), 1),
            },
        };

        // THEME-MACOS-1: non-color tokens + font stack bridged as resources. FontFamily is stored as a
        // parsed FontFamily (not a string) because DynamicResource assigns the resource verbatim to the
        // Window.FontFamily property; a string resource would fail the property cast.
        dictionary[AppFontFamily] = new FontFamily(pack.FontFamily);
        dictionary[CardShadowBox] = pack.Metrics.CardShadowFor(variant);
        dictionary["Corner.Window"] = pack.Metrics.CornerWindow;
        dictionary["Corner.Card"] = pack.Metrics.CornerCard;
        dictionary["Corner.Button"] = pack.Metrics.CornerButton;
        dictionary["Corner.Small"] = pack.Metrics.CornerSmall;

        foreach (var pair in pack.Icons)
        {
            dictionary["Icon." + pair.Key] = pair.Value;
        }

        dictionary["Motion.Reduced"] = pack.Motion.Reduced;
        dictionary["Motion.FastMs"] = pack.Motion.Fast.TotalMilliseconds;
        dictionary["Motion.NormalMs"] = pack.Motion.Normal.TotalMilliseconds;
        dictionary["Motion.SlowMs"] = pack.Motion.Slow.TotalMilliseconds;
        return dictionary;
    }
}
