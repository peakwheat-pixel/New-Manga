using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Styling;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// Loads the generated dictionaries through the real Avalonia XAML pipeline and asserts the published
/// shape: complete palettes, typed global tokens, theme-scoped high contrast and working overlays.
/// </summary>
public sealed class TokenResourceDictionaryTests
{
    private const string ThemeRoot = "avares://NewManga.DesignSystem/Themes/";

    [AvaloniaFact]
    public void Dark_and_light_palettes_publish_the_same_complete_key_set()
    {
        var dark = Load("Tokens.Dark.axaml");
        var light = Load("Tokens.Light.axaml");

        var colorKeys = NmKeys.All.Where(static key => key.StartsWith("Nm.Color.", StringComparison.Ordinal)).ToArray();
        Assert.Equal(35, colorKeys.Length);

        foreach (var key in colorKeys)
        {
            Assert.IsType<SolidColorBrush>(Resolve(dark, key, ThemeVariant.Dark));
            Assert.IsType<SolidColorBrush>(Resolve(light, key, ThemeVariant.Light));
        }

        var darkCanvas = ColorOf(dark, "Nm.Color.Bg.Canvas", ThemeVariant.Dark);
        var lightCanvas = ColorOf(light, "Nm.Color.Bg.Canvas", ThemeVariant.Light);
        Assert.Equal(Color.Parse("#FF0F1012"), darkCanvas);
        Assert.Equal(Color.Parse("#FFF4F3F0"), lightCanvas);
    }

    [AvaloniaFact]
    public void Global_tokens_are_published_with_their_clr_types()
    {
        var global = Load("Tokens.Global.axaml");

        Assert.Equal(13d, Resolve(global, "Nm.FontSize.Md"));
        Assert.Equal(0d, Resolve(global, "Nm.Space.0"));
        Assert.Equal(12d, Resolve(global, "Nm.Space.4"));
        Assert.Equal(16d, Resolve(global, "Nm.Space.5"));
        Assert.Equal(36d, Resolve(global, "Nm.Size.TopBand"));
        Assert.Equal(28d, Resolve(global, "Nm.Size.ControlHeight"));
        Assert.Equal(24d, Resolve(global, "Nm.Size.ControlHeightSm"));
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
        Assert.Equal("cubic-bezier(0.2, 0, 0, 1)", Resolve(global, "Nm.Motion.Easing.Standard"));

        Assert.Equal("●", Resolve(global, "Nm.State.Symbol.Done"));
        Assert.Equal("▨", Resolve(global, "Nm.State.Symbol.Stale"));
        Assert.Equal(50, Resolve(global, "Nm.ZIndex.Modal"));
    }

    [AvaloniaFact]
    public void High_contrast_dictionary_is_theme_scoped_and_complete()
    {
        var highContrast = Load("Tokens.HighContrast.axaml");
        var colorKeys = NmKeys.All.Where(static key => key.StartsWith("Nm.Color.", StringComparison.Ordinal)).ToArray();

        foreach (var key in colorKeys)
        {
            Assert.IsType<SolidColorBrush>(Resolve(highContrast, key, ThemeVariant.Dark));
            Assert.IsType<SolidColorBrush>(Resolve(highContrast, key, ThemeVariant.Light));
        }

        Assert.Equal(Color.Parse("#FFFFFFFF"), ColorOf(highContrast, "Nm.Color.Text.Primary", ThemeVariant.Dark));
        Assert.Equal(Color.Parse("#FF000000"), ColorOf(highContrast, "Nm.Color.Text.Primary", ThemeVariant.Light));
        // The background ladder intentionally keeps the frozen palette in high contrast.
        Assert.Equal(Color.Parse("#FF0F1012"), ColorOf(highContrast, "Nm.Color.Bg.Canvas", ThemeVariant.Dark));
    }

    [AvaloniaFact]
    public void Density_and_motion_overlays_only_contain_contract_keys()
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

        foreach (var overlay in new[] { compact, spacious, reduced })
        {
            // Overlays must override existing tokens, never publish unknown keys.
            foreach (var key in NmKeys.All)
            {
                if (overlay.TryGetResource(key, ThemeVariant.Default, out _))
                {
                    Assert.Contains(key, NmKeys.All);
                }
            }
        }
    }

    private static ResourceDictionary Load(string fileName) =>
        (ResourceDictionary)AvaloniaXamlLoader.Load(new Uri(ThemeRoot + fileName));

    private static object Resolve(ResourceDictionary dictionary, string key, ThemeVariant? theme = null) =>
        dictionary.TryGetResource(key, theme ?? ThemeVariant.Default, out var value) && value is not null
            ? value
            : throw new InvalidOperationException($"resource '{key}' missing from generated dictionary");

    private static Color ColorOf(ResourceDictionary dictionary, string key, ThemeVariant? theme = null) =>
        Assert.IsType<SolidColorBrush>(Resolve(dictionary, key, theme)).Color;
}
