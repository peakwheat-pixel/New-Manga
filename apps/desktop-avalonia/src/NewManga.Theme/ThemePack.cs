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

    /// <summary>THEME-MACOS-1 pack id (single pack, two token sets).</summary>
    public const string MacOsSonomaId = "macos-sonoma";

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

    /// <summary>
    /// THEME-MACOS-1: macOS Sonoma skin. One pack carries both token sets (Light in Tokens/Materials,
    /// Dark in DarkTokens/DarkMaterials); the plugin lists it once and ThemePackService switches variants.
    /// Spec source: doc/tasks/THEME-MACOS-1.md「设计规格（用户冻结）」. System fonts only (no bundled font).
    /// </summary>
    public static ThemePack MacOsSonoma { get; } = Create(
        MacOsSonomaId,
        "macOS 风",
        isDark: false,
        tokens: new Dictionary<string, string>
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
        },
        materials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#FDFDFE",
            ["HeaderGradientEnd"] = "#ECECEF",
            ["CardShadow"] = "#14000000",
            ["MicaFallback"] = "#F5F5F7",
        },
        darkTokens: new Dictionary<string, string>
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
        },
        darkMaterials: new Dictionary<string, string>
        {
            ["HeaderGradientStart"] = "#2C2C2E",
            ["HeaderGradientEnd"] = "#1E1E1E",
            ["CardShadow"] = "#66000000",
            ["MicaFallback"] = "#1E1E1E",
        },
        metrics: new ThemePackMetrics(
            CornerWindow: 12,
            CornerCard: 14,
            CornerButton: 8,
            CornerSmall: 6,
            CardShadowLight: "0 1 3 0 #14000000",
            CardShadowDark: "0 1 3 0 #66000000"),
        fontFamily: MacOsFontFamily,
        motion: new MotionProfile(
            TimeSpan.FromMilliseconds(120),
            TimeSpan.FromMilliseconds(160),
            TimeSpan.FromMilliseconds(240),
            Reduced: false));

    public static IReadOnlyList<ThemePack> All { get; } =
        new[] { SaberPurple, SaberLight, Midnight, Sakura, Emerald, Mono, MacOsSonoma };

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
