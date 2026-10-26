using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Styling;

namespace NewManga.Theme;

/// <summary>One skin: a palette of named brushes plus the Fluent theme variant it rides on.</summary>
public sealed record ThemeTokens(string Id, string Label, bool IsDark, IReadOnlyDictionary<string, string> Palette);

/// <summary>
/// Runtime skinning layer (S0 spike gate 4, p95 ≈ 3.7 ms): the active skin is one merged
/// ResourceDictionary swapped on the live Application; controls resolve colours through
/// DynamicResource, so nothing is recreated and no restart is needed.
/// </summary>
public static class ThemeManager
{
    public const string AppBackground = "AppBg";
    public const string HeaderBackground = "HeaderBg";
    public const string CardBackground = "CardBg";
    public const string CardAltBackground = "CardBgAlt";
    public const string TextPrimary = "TextPrimary";
    public const string TextSecondary = "TextSecondary";
    public const string Accent = "Accent";
    public const string AccentText = "AccentText";
    public const string Border = "Border";
    public const string StatusBackground = "StatusBg";
    public const string ReaderBackground = "ReaderBg";

    public static readonly ThemeTokens Light = new(
        "light",
        "Light",
        false,
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [AppBackground] = "#F6F7F9",
            [HeaderBackground] = "#FFFFFF",
            [CardBackground] = "#FFFFFF",
            [CardAltBackground] = "#F2F3F6",
            [TextPrimary] = "#1A1D21",
            [TextSecondary] = "#5C6670",
            [Accent] = "#3B82F6",
            [AccentText] = "#FFFFFF",
            [Border] = "#D9DEE5",
            [StatusBackground] = "#FFFFFF",
            [ReaderBackground] = "#E9ECF1",
        });

    public static readonly ThemeTokens Dark = new(
        "dark",
        "Dark",
        true,
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [AppBackground] = "#12161C",
            [HeaderBackground] = "#1A1F27",
            [CardBackground] = "#1A1F27",
            [CardAltBackground] = "#222833",
            [TextPrimary] = "#E8EDF2",
            [TextSecondary] = "#9AA7B4",
            [Accent] = "#60A5FA",
            [AccentText] = "#0B1220",
            [Border] = "#2C3440",
            [StatusBackground] = "#1A1F27",
            [ReaderBackground] = "#0B0E13",
        });

    public static readonly ThemeTokens SaberPurple = new(
        "saber-purple",
        "Saber Purple",
        true,
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [AppBackground] = "#1A0F26",
            [HeaderBackground] = "#241435",
            [CardBackground] = "#241435",
            [CardAltBackground] = "#2D1A42",
            [TextPrimary] = "#F4E8FF",
            [TextSecondary] = "#BCA3D8",
            [Accent] = "#C77DFF",
            [AccentText] = "#1A0F26",
            [Border] = "#3D2258",
            [StatusBackground] = "#241435",
            [ReaderBackground] = "#120A1C",
        });

    public static IReadOnlyList<ThemeTokens> All { get; } = new[] { Light, Dark, SaberPurple };

    private static ResourceDictionary? _activeDictionary;

    public static ThemeTokens Current { get; private set; } = Light;

    public static ThemeTokens ById(string id)
    {
        foreach (var theme in All)
        {
            if (string.Equals(theme.Id, id, StringComparison.Ordinal))
            {
                return theme;
            }
        }

        return Light;
    }

    /// <summary>Applies a skin in place (no window/control recreation).</summary>
    public static void Apply(Application application, ThemeTokens theme)
    {
        var resources = application.Resources;
        if (_activeDictionary is not null)
        {
            resources.MergedDictionaries.Remove(_activeDictionary);
        }

        var dictionary = new ResourceDictionary();
        foreach (var pair in theme.Palette)
        {
            dictionary[pair.Key] = new SolidColorBrush(Color.Parse(pair.Value));
        }

        resources.MergedDictionaries.Add(dictionary);
        _activeDictionary = dictionary;
        Current = theme;
        application.RequestedThemeVariant = theme.IsDark ? ThemeVariant.Dark : ThemeVariant.Light;
    }

    /// <summary>Resolves a palette brush through the live resource stack (fallback for tests).</summary>
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
}
