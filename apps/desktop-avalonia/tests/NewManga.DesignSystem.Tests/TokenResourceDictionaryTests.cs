using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Styling;
using NewManga.DesignSystem.Theming;
using NewManga.DesignSystem.Tokens;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// Loads the generated dictionaries through the real Avalonia XAML pipeline and asserts the published
/// shape: complete palettes, typed global tokens, theme-scoped high contrast and working overlays.
/// Key-set assertions compare the REAL dictionary keys against the expected allow-list in both
/// directions (review P2: no self-referential key test).
/// </summary>
public sealed class TokenResourceDictionaryTests
{
    private const string ThemeRoot = "avares://NewManga.DesignSystem/Themes/";

    [AvaloniaFact]
    public void Dark_and_light_palettes_publish_the_same_complete_key_set()
    {
        var dark = Load("Tokens.Dark.axaml");
        var light = Load("Tokens.Light.axaml");

        var expected = DesignSystemThemeManager.PaletteColorKeys
            .OrderBy(static key => key, StringComparer.Ordinal)
            .ToArray();
        Assert.Equal(35, expected.Length);
        Assert.Equal(expected, ActualStringKeys(dark));
        Assert.Equal(expected, ActualStringKeys(light));

        foreach (var key in expected)
        {
            Assert.IsType<SolidColorBrush>(Resolve(dark, key, ThemeVariant.Dark));
            Assert.IsType<SolidColorBrush>(Resolve(light, key, ThemeVariant.Light));
        }

        Assert.Equal(Color.Parse("#FF0F1012"), ColorOf(dark, "Nm.Color.Bg.Canvas", ThemeVariant.Dark));
        Assert.Equal(Color.Parse("#FFF4F3F0"), ColorOf(light, "Nm.Color.Bg.Canvas", ThemeVariant.Light));
    }

    [AvaloniaFact]
    public void Global_tokens_are_published_with_their_clr_types_and_no_extra_keys()
    {
        var global = Load("Tokens.Global.axaml");

        Assert.Equal(13d, Resolve(global, "Nm.FontSize.Md"));
        Assert.Equal(0d, Resolve(global, "Nm.Space.0"));
        Assert.Equal(12d, Resolve(global, "Nm.Space.4"));
        Assert.Equal(16d, Resolve(global, "Nm.Space.5"));
        Assert.Equal(36d, Resolve(global, "Nm.Size.TopBand"));
        Assert.Equal(28d, Resolve(global, "Nm.Size.ControlHeight"));
        Assert.Equal(24d, Resolve(global, "Nm.Size.ControlHeightSm"));
        Assert.Equal(16d, Resolve(global, "Nm.Size.Marker"));
        Assert.Equal(8d, Resolve(global, "Nm.Size.ScrollBar"));
        Assert.Equal(1.25d, Resolve(global, "Nm.Icon.Stroke"));
        Assert.Equal(0.4d, Resolve(global, "Nm.Opacity.Disabled"));

        var corner = Assert.IsType<CornerRadius>(Resolve(global, "Nm.Corner.Sm"));
        Assert.Equal(new CornerRadius(2), corner);
        var border = Assert.IsType<Thickness>(Resolve(global, "Nm.Border.Focus"));
        Assert.Equal(new Thickness(2), border);
        var padding = Assert.IsType<Thickness>(Resolve(global, "Nm.Padding.Control"));
        Assert.Equal(new Thickness(12, 8, 12, 8), padding);
        var weight = Assert.IsType<FontWeight>(Resolve(global, "Nm.FontWeight.SemiBold"));
        Assert.Equal(FontWeight.SemiBold, weight);

        var family = Assert.IsType<FontFamily>(Resolve(global, "Nm.FontFamily.Ui"));
        Assert.Contains("Microsoft YaHei UI", family.FamilyNames);

        Assert.Equal(TimeSpan.FromMilliseconds(90), Resolve(global, "Nm.Motion.Duration.Fast"));
        Assert.Equal(TimeSpan.FromMilliseconds(140), Resolve(global, "Nm.Motion.Duration.Normal"));
        Assert.True((bool)Resolve(global, "Nm.Motion.Enabled")!);

        // R-14: tracking tokens are em ratios, not pixels; line-height aliases are frozen multipliers.
        Assert.Equal(0.08, Assert.IsType<double>(Resolve(global, "Nm.FontTracking.Caps")));
        Assert.Equal(-0.01, Assert.IsType<double>(Resolve(global, "Nm.FontTracking.Data")));
        Assert.Equal(1.45, Assert.IsType<double>(Resolve(global, "Nm.LineHeight.Body")));
        Assert.Equal(18.85, Assert.IsType<double>(Resolve(global, "Nm.TextLineBox.Body")));

        Assert.Equal("●", Resolve(global, "Nm.State.Symbol.Done"));
        Assert.Equal("▨", Resolve(global, "Nm.State.Symbol.Stale"));
        Assert.Equal(50, Resolve(global, "Nm.ZIndex.Modal"));

        // Real-key allow-list diff (both directions) against the generator's declared rows.
        Assert.Equal(ExpectedGlobalKeys(), ActualStringKeys(global));
    }

    [AvaloniaFact]
    public void High_contrast_dictionary_is_theme_scoped_and_complete()
    {
        var highContrast = Load("Tokens.HighContrast.axaml");
        var expected = DesignSystemThemeManager.PaletteColorKeys
            .OrderBy(static key => key, StringComparer.Ordinal)
            .ToArray();

        var themeKeys = highContrast.ThemeDictionaries.Keys.Select(static variant => variant.ToString()).ToArray();
        Assert.Contains("Dark", themeKeys);
        Assert.Contains("Light", themeKeys);

        foreach (var variant in new[] { ThemeVariant.Dark, ThemeVariant.Light })
        {
            Assert.True(highContrast.ThemeDictionaries.TryGetValue(variant, out var provider));
            var scoped = Assert.IsType<ResourceDictionary>(provider);
            Assert.Equal(expected, ActualStringKeys(scoped));
            foreach (var key in expected)
            {
                Assert.IsType<SolidColorBrush>(Resolve(scoped!, key, variant));
            }
        }

        Assert.Equal(Color.Parse("#FFFFFFFF"), ColorOf(highContrast, "Nm.Color.Text.Primary", ThemeVariant.Dark));
        Assert.Equal(Color.Parse("#FF000000"), ColorOf(highContrast, "Nm.Color.Text.Primary", ThemeVariant.Light));
        // The background ladder intentionally keeps the frozen palette in high contrast.
        Assert.Equal(Color.Parse("#FF0F1012"), ColorOf(highContrast, "Nm.Color.Bg.Canvas", ThemeVariant.Dark));
    }

    [AvaloniaFact]
    public void Density_and_motion_overlays_match_their_allow_lists_exactly()
    {
        var compact = Load("Density.Compact.axaml");
        var spacious = Load("Density.Spacious.axaml");
        var reduced = Load("Motion.Reduced.axaml");

        Assert.Equal(24d, Resolve(compact, "Nm.Size.ControlHeight"));
        Assert.Equal(32d, Resolve(spacious, "Nm.Size.ControlHeight"));
        Assert.Equal(new Thickness(10, 6, 10, 6), Resolve(compact, "Nm.Padding.Control"));

        Assert.Equal(TimeSpan.Zero, Resolve(reduced, "Nm.Motion.Duration.Fast"));
        Assert.Equal(TimeSpan.Zero, Resolve(reduced, "Nm.Motion.Duration.Normal"));
        Assert.False((bool)Resolve(reduced, "Nm.Motion.Enabled")!);

        var expectedCompact = TokenMap.Density.Select(static entry => entry.ResourceKey)
            .OrderBy(static key => key, StringComparer.Ordinal).ToArray();
        Assert.Equal(expectedCompact, ActualStringKeys(compact));
        Assert.Equal(expectedCompact, ActualStringKeys(spacious));

        var reducedKeys = new[] { "Nm.Motion.Duration.Instant", "Nm.Motion.Duration.Fast", "Nm.Motion.Duration.Normal", "Nm.Motion.Duration.Slow", "Nm.Motion.Enabled" }
            .OrderBy(static key => key, StringComparer.Ordinal).ToArray();
        Assert.Equal(reducedKeys, ActualStringKeys(reduced));
    }

    private static string[] ExpectedGlobalKeys()
    {
        var result = TokenGenerator.Generate(File.ReadAllText(TestPaths.TokensFixture));
        return result.Rows
            .Where(static row => row.Scope is "global" or "global-derived")
            .Select(static row => row.ResourceKey)
            .Distinct(StringComparer.Ordinal)
            .OrderBy(static key => key, StringComparer.Ordinal)
            .ToArray();
    }

    private static string[] ActualStringKeys(ResourceDictionary dictionary) => dictionary.Keys
        .OfType<string>()
        .OrderBy(static key => key, StringComparer.Ordinal)
        .ToArray();

    private static ResourceDictionary Load(string fileName) =>
        (ResourceDictionary)AvaloniaXamlLoader.Load(new Uri(ThemeRoot + fileName));

    private static object Resolve(ResourceDictionary dictionary, string key, ThemeVariant? theme = null) =>
        dictionary.TryGetResource(key, theme ?? ThemeVariant.Default, out var value) && value is not null
            ? value
            : throw new InvalidOperationException($"resource '{key}' missing from generated dictionary");

    private static Color ColorOf(ResourceDictionary dictionary, string key, ThemeVariant? theme = null) =>
        Assert.IsType<SolidColorBrush>(Resolve(dictionary, key, theme)).Color;
}

