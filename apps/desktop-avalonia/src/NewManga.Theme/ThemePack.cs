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
/// AC2 ThemePack: one skin = manifest + tokens + control-theme keys + materials + motion + icons.
/// Hot switching swaps a ThemeDictionaries resource dictionary in place: controls use DynamicResource,
/// so no control is recreated and no restart is needed.
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
    public bool ReducedMotion => Motion.Reduced;

    public ThemePack WithReducedMotion(bool reduced) => this with
    {
        Motion = new MotionProfile(Motion.Fast, Motion.Normal, Motion.Slow, reduced),
    };
}

public static class ThemePacks
{
    public const string SaberPurpleId = "saber-purple";

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

    public static IReadOnlyList<ThemePack> All { get; } = new[] { SaberPurple, SaberLight, Midnight, Sakura, Emerald, Mono };

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
        IReadOnlyDictionary<string, string> materials) =>
        new(
            id,
            label,
            $"{{\"schema\":\"nm.themepack/1\",\"id\":\"{id}\",\"label\":\"{label}\",\"isDark\":{isDark.ToString().ToLowerInvariant()}," +
            "\"parts\":[\"manifest\",\"tokens\",\"controlthemes\",\"materials\",\"motion\",\"icons\"]}",
            isDark,
            tokens,
            materials,
            ControlThemeSet,
            Motion,
            IconSet);
}

/// <summary>
/// AC2 theme service. Applies packs by swapping one merged ResourceDictionary whose ThemeDictionaries
/// hold Light/Dark variants, so DynamicResource consumers update without recreation or restart.
/// </summary>
public static class ThemePackService
{
    public const string AppBackground = "AppBg";
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
    public const string EmptyBackground = "EmptyBg";
    public const string MicaFallback = "MicaFallback";

    private static ResourceDictionary? _active;
    private static long _switchTicks;

    public static ThemePack Current { get; private set; } = ThemePacks.Default;

    /// <summary>Duration of the last apply (used by the p95 regression test).</summary>
    public static TimeSpan LastApplyDuration { get; private set; }

    public static TimeSpan LastSwitchDuration => TimeSpan.FromTicks(_switchTicks);

    public static void Apply(Application application, ThemePack pack)
    {
        var start = System.Diagnostics.Stopwatch.GetTimestamp();
        if (_active is not null)
        {
            application.Resources.MergedDictionaries.Remove(_active);
        }

        var light = BuildVariant(pack);
        var dark = BuildVariant(pack);
        var root = new ResourceDictionary
        {
            ThemeDictionaries =
            {
                [ThemeVariant.Light] = light,
                [ThemeVariant.Dark] = dark,
            },
        };

        application.Resources.MergedDictionaries.Add(root);
        _active = root;
        Current = pack;
        application.RequestedThemeVariant = pack.IsDark ? ThemeVariant.Dark : ThemeVariant.Light;
        LastApplyDuration = System.Diagnostics.Stopwatch.GetElapsedTime(start);
        _switchTicks = LastApplyDuration.Ticks;
    }

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

    private static ResourceDictionary BuildVariant(ThemePack pack)
    {
        var dictionary = new ResourceDictionary();
        foreach (var pair in pack.Tokens)
        {
            dictionary[pair.Key] = new SolidColorBrush(Color.Parse(pair.Value));
        }

        foreach (var pair in pack.Materials)
        {
            dictionary[pair.Key] = new SolidColorBrush(Color.Parse(pair.Value));
        }

        dictionary["HeaderGradient"] = new LinearGradientBrush
        {
            StartPoint = new RelativePoint(0, 0, RelativeUnit.Relative),
            EndPoint = new RelativePoint(1, 0.2, RelativeUnit.Relative),
            GradientStops =
            {
                new GradientStop(Color.Parse(pack.Materials["HeaderGradientStart"]), 0),
                new GradientStop(Color.Parse(pack.Materials["HeaderGradientEnd"]), 1),
            },
        };

        foreach (var pair in pack.Icons)
        {
            dictionary["Icon." + pair.Key] = pair.Value;
        }

        dictionary["Motion.Reduced"] = pack.Motion.Reduced;
        dictionary["Motion.NormalMs"] = pack.Motion.Normal.TotalMilliseconds;
        return dictionary;
    }
}
