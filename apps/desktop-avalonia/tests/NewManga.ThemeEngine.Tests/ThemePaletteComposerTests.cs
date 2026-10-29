using Avalonia;
using Avalonia.Media;
using Avalonia.Media.Immutable;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Tokens;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Palette composition: a package plus a variant becomes the flat <c>Nm.*</c> theme layer the design
/// system applies. The shipped theme must reproduce the frozen token values byte-for-byte semantically,
/// and user-theme personality (font scale, line-height preset, corners, motion) must reach the layer.
/// </summary>
public sealed class ThemePaletteComposerTests
{
    private static ThemePackage Default => ThemeFixtures.DefaultPackage;

    [Theory]
    [MemberData(nameof(ThemeFixtures.Variants), MemberType = typeof(ThemeFixtures))]
    public void Composes_the_whole_theme_layer(PaletteVariant variant)
    {
        var layer = ThemePaletteComposer.Compose(Default, variant);

        Assert.Equal(ThemePaletteComposer.ThemeLayerKeyCount, layer.Count);
        // The composed layer must be exactly the DS theme-layer whitelist (R-15/R-21): same 59 keys,
        // no theme-invariant derived colors (scrim) and no layout/density keys.
        Assert.Equal(
            ThemeTokenKeys.ThemeLayer.OrderBy(key => key, StringComparer.Ordinal),
            layer.Keys.OrderBy(key => key, StringComparer.Ordinal));
        Assert.DoesNotContain(NmKeys.Color.Scrim, layer.Keys);
        Assert.DoesNotContain(NmKeys.Motion.Duration.Instant, layer.Keys);
        Assert.All(layer.Keys, key => Assert.StartsWith("Nm.", key, StringComparison.Ordinal));
    }

    [Theory]
    [MemberData(nameof(ThemeFixtures.Variants), MemberType = typeof(ThemeFixtures))]
    public void Color_layer_reproduces_the_frozen_token_values(PaletteVariant variant)
    {
        var layer = ThemePaletteComposer.Compose(Default, variant);
        var expected = FrozenColors(variant);

        Assert.Equal(ThemePaletteComposer.ColorLayerKeyCount, expected.Count);
        foreach (var (key, color) in expected)
        {
            var brush = Assert.IsAssignableFrom<ISolidColorBrush>(layer[key]);
            Assert.Equal(color, brush.Color);
        }
    }

    [Theory]
    [MemberData(nameof(ThemeFixtures.Variants), MemberType = typeof(ThemeFixtures))]
    public void Color_layer_is_a_strict_subset_of_the_theme_layer(PaletteVariant variant)
    {
        var full = ThemePaletteComposer.Compose(Default, variant);
        var colors = ThemePaletteComposer.ComposeColorLayer(Default, variant);

        Assert.Equal(ThemePaletteComposer.ColorLayerKeyCount, colors.Count);
        Assert.All(colors.Keys, key => Assert.StartsWith("Nm.Color.", key, StringComparison.Ordinal));
        foreach (var (key, value) in colors)
        {
            Assert.Equal(
                Assert.IsAssignableFrom<ISolidColorBrush>(value).Color,
                Assert.IsAssignableFrom<ISolidColorBrush>(full[key]).Color);
        }
    }

    [Theory]
    [MemberData(nameof(ThemeFixtures.Variants), MemberType = typeof(ThemeFixtures))]
    public void Palette_brushes_are_immutable_so_resource_dictionaries_stay_shared_safely(PaletteVariant variant)
    {
        var layer = ThemePaletteComposer.Compose(Default, variant);

        foreach (var (key, value) in layer.Where(pair => pair.Key.StartsWith("Nm.Color.", StringComparison.Ordinal)))
        {
            Assert.IsType<ImmutableSolidColorBrush>(value);
        }
    }

    [Fact]
    public void Font_families_are_resolved_to_avalonia_font_families()
    {
        var layer = ThemePaletteComposer.Compose(Default, PaletteVariant.Dark);

        var ui = Assert.IsType<FontFamily>(layer[NmKeys.FontFamily.Ui]);
        var data = Assert.IsType<FontFamily>(layer[NmKeys.FontFamily.Data]);
        var display = Assert.IsType<FontFamily>(layer[NmKeys.FontFamily.Display]);

        Assert.Contains("Segoe UI Variable Text", ui.Name, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Cascadia Mono", data.Name, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Georgia", display.Name, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Theme_invariant_scrim_stays_out_of_the_composed_layer()
    {
        var package = Default with
        {
            Light = ThemeFixtures.WithColor(Default.Light, NmKeys.Color.Scrim, "rgba(0,0,0,0.55)"),
        };

        var layer = ThemePaletteComposer.Compose(package, PaletteVariant.Light);

        Assert.Equal(ThemePaletteComposer.ThemeLayerKeyCount, layer.Count);
        Assert.DoesNotContain(NmKeys.Color.Scrim, layer.Keys);
    }

    [Fact]
    public void Base_font_sizes_match_the_frozen_tokens_at_scale_one()
    {
        var layer = ThemePaletteComposer.Compose(Default, PaletteVariant.Dark);
        var expected = FrozenFontSizes();

        foreach (var (key, value) in expected)
        {
            Assert.Equal(value, Assert.IsType<double>(layer[key]));
        }
    }

    [Fact]
    public void Font_scale_scales_every_font_size_and_line_height_tier()
    {
        var scaled = Default with
        {
            Dark = ThemeFixtures.WithTypography(
                Default.Dark,
                Default.Dark.Typography with { Scale = 1.25 }),
        };

        var layer = ThemePaletteComposer.Compose(scaled, PaletteVariant.Dark);

        var baseSizes = FrozenFontSizes();
        foreach (var (key, value) in baseSizes)
        {
            Assert.Equal(Math.Round(value * 1.25, 2, MidpointRounding.AwayFromZero), Assert.IsType<double>(layer[key]));
        }

        // Body tier = 13px * 1.45 * 1.25 = 23.56
        Assert.Equal(23.56, Assert.IsType<double>(layer[NmKeys.LineHeight.Body]), precision: 2);
    }

    [Fact]
    public void Line_height_preset_scales_the_absolute_tiers_without_touching_the_multipliers()
    {
        var tight = Default with
        {
            Dark = ThemeFixtures.WithTypography(
                Default.Dark,
                Default.Dark.Typography with { LineHeight = LineHeightPreset.Tight }),
        };
        var loose = Default with
        {
            Dark = ThemeFixtures.WithTypography(
                Default.Dark,
                Default.Dark.Typography with { LineHeight = LineHeightPreset.Loose }),
        };

        var normalLayer = ThemePaletteComposer.Compose(Default, PaletteVariant.Dark);
        var tightLayer = ThemePaletteComposer.Compose(tight, PaletteVariant.Dark);
        var looseLayer = ThemePaletteComposer.Compose(loose, PaletteVariant.Dark);

        // Body = 13px * 1.45 (design tier) * preset / 1.45 (normal anchor)
        Assert.Equal(18.85, Assert.IsType<double>(normalLayer[NmKeys.LineHeight.Body]), precision: 2);
        Assert.Equal(16.25, Assert.IsType<double>(tightLayer[NmKeys.LineHeight.Body]), precision: 2);
        Assert.Equal(20.8, Assert.IsType<double>(looseLayer[NmKeys.LineHeight.Body]), precision: 2);

        // The multiplier tokens themselves are frozen values, not the preset.
        Assert.Equal(1.25, Assert.IsType<double>(tightLayer[NmKeys.LineHeight.Tight]));
        Assert.Equal(1.45, Assert.IsType<double>(tightLayer[NmKeys.LineHeight.Normal]));
        Assert.Equal(1.6, Assert.IsType<double>(tightLayer[NmKeys.LineHeight.Loose]));
    }

    [Fact]
    public void Corners_and_motion_come_from_the_theme_personality()
    {
        var package = Default with
        {
            Dark = Default.Dark with
            {
                Corners = new ThemeCorners(0, 1, 3),
                Motion = new ThemeMotion(50, 200, 400),
            },
        };

        var layer = ThemePaletteComposer.Compose(package, PaletteVariant.Dark);

        Assert.Equal(new CornerRadius(0), Assert.IsType<CornerRadius>(layer[NmKeys.Corner.None]));
        Assert.Equal(new CornerRadius(1), Assert.IsType<CornerRadius>(layer[NmKeys.Corner.Sm]));
        Assert.Equal(new CornerRadius(3), Assert.IsType<CornerRadius>(layer[NmKeys.Corner.Md]));
        Assert.Equal(TimeSpan.FromMilliseconds(50), Assert.IsType<TimeSpan>(layer[NmKeys.Motion.Duration.Fast]));
        Assert.Equal(TimeSpan.FromMilliseconds(200), Assert.IsType<TimeSpan>(layer[NmKeys.Motion.Duration.Normal]));
        Assert.Equal(TimeSpan.FromMilliseconds(400), Assert.IsType<TimeSpan>(layer[NmKeys.Motion.Duration.Slow]));
    }

    [Fact]
    public void Light_and_dark_layers_are_independent()
    {
        var light = ThemePaletteComposer.Compose(Default, PaletteVariant.Light);
        var dark = ThemePaletteComposer.Compose(Default, PaletteVariant.Dark);

        Assert.NotEqual(
            Assert.IsAssignableFrom<ISolidColorBrush>(light[NmKeys.Color.Bg.Canvas]).Color,
            Assert.IsAssignableFrom<ISolidColorBrush>(dark[NmKeys.Color.Bg.Canvas]).Color);
    }

    [Theory]
    [InlineData(AppearanceMode.Light, true, PaletteVariant.Light)]
    [InlineData(AppearanceMode.Dark, false, PaletteVariant.Dark)]
    [InlineData(AppearanceMode.System, true, PaletteVariant.Light)]
    [InlineData(AppearanceMode.System, false, PaletteVariant.Dark)]
    public void Resolve_variant_follows_the_requested_appearance(
        AppearanceMode appearance,
        bool platformIsLight,
        PaletteVariant expected)
    {
        Assert.Equal(expected, ThemePaletteComposer.ResolveVariant(appearance, platformIsLight));
    }

    [Fact]
    public void Compose_rejects_a_package_missing_a_required_color()
    {
        var colors = new Dictionary<string, string>(Default.Dark.Colors, StringComparer.Ordinal);
        colors.Remove(NmKeys.Color.Bg.Panel);
        var package = Default with { Dark = Default.Dark with { Colors = colors } };

        var exception = Assert.Throws<ThemePackageException>(
            () => ThemePaletteComposer.Compose(package, PaletteVariant.Dark));

        Assert.Contains(exception.Issues, issue => issue.Code == ThemeIssueCodes.ColorMissingKey);
    }

    [Fact]
    public void Compose_rejects_an_out_of_range_corner()
    {
        var package = Default with
        {
            Dark = Default.Dark with { Corners = new ThemeCorners(0, 2, 12) },
        };

        var exception = Assert.Throws<ThemePackageException>(
            () => ThemePaletteComposer.Compose(package, PaletteVariant.Dark));

        Assert.Contains(exception.Issues, issue => issue.Code == ThemeIssueCodes.CornerOutOfRange);
    }

    private static IReadOnlyDictionary<string, Color> FrozenColors(PaletteVariant variant)
    {
        var scope = variant == PaletteVariant.Light ? TokenMap.LightScope : TokenMap.DarkScope;
        return TokenDocument.Parse(ThemeFixtures.TokensJson)
            .Where(entry => entry.Path.StartsWith(scope, StringComparison.Ordinal) && entry.Type == "color")
            .ToDictionary(
                entry => TokenMap.ColorResourceKey(entry.Path),
                entry => TokenValues.ParseColor(entry.Value),
                StringComparer.Ordinal);
    }

    private static IReadOnlyDictionary<string, double> FrozenFontSizes()
    {
        var entries = TokenDocument.Parse(ThemeFixtures.TokensJson);
        var bindings = TokenMap.GlobalBindings.ToDictionary(
            binding => binding.TokenPath,
            binding => binding.ResourceKey,
            StringComparer.Ordinal);
        return entries
            .Where(entry => entry.Path.StartsWith("font.size.", StringComparison.Ordinal))
            .ToDictionary(
                entry => bindings[entry.Path],
                entry => TokenValues.ParseDimension(entry.Value),
                StringComparer.Ordinal);
    }
}
