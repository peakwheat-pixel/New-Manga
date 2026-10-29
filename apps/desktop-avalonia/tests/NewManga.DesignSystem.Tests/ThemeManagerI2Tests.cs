using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Styling;
using Avalonia.Threading;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// D-1 I2 regressions for the theme-manager seam (P2-① to P2-③ and P2-⑥):
/// absolute line boxes derived from the theme layer, fixed provider precedence/overlay order,
/// palette-only updates preserving typography, and transactional failure paths.
/// </summary>
public sealed class ThemeManagerI2Tests
{
    [AvaloniaFact]
    public void Theme_layer_derives_absolute_line_boxes_from_its_own_typography()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var layer = CompleteThemeLayer(dictionary =>
        {
            dictionary[NmKeys.FontSize.Md] = 16d;
            dictionary[NmKeys.LineHeight.Body] = 1.6d;
        });

        Assert.True(manager.ApplyThemeLayer(layer, "i2-linebox"), manager.LastError);
        var application = Application.Current!;
        Assert.Equal(25.6d, ThemeTestHarness.ValueOf<double>(application, NmKeys.TextLineBox.Body), 3);

        var text = new TextBlock { Text = "line-box probe", Classes = { "body" } };
        var window = new Window { Content = text };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(25.6d, text.LineHeight, 3);
        window.Close();
    }

    [AvaloniaFact]
    public void Explicit_line_box_supplied_by_the_layer_wins_over_derivation()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var layer = CompleteThemeLayer(dictionary =>
        {
            dictionary[NmKeys.FontSize.Md] = 16d;
            dictionary[NmKeys.LineHeight.Body] = 1.6d;
            dictionary[NmKeys.TextLineBox.Body] = 31d;
        });

        Assert.True(manager.ApplyThemeLayer(layer, "i2-linebox-explicit"), manager.LastError);
        Assert.Equal(31d, ThemeTestHarness.ValueOf<double>(Application.Current!, NmKeys.TextLineBox.Body), 3);
    }

    [AvaloniaFact]
    public void Applying_a_palette_after_a_theme_layer_preserves_its_typography()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var layer = CompleteThemeLayer(dictionary =>
        {
            dictionary[NmKeys.FontFamily.Ui] = new FontFamily("Georgia");
            dictionary[NmKeys.FontSize.Md] = 15d;
            dictionary[NmKeys.LineHeight.Body] = 1.6d;
            dictionary[NmKeys.Color.Bg.Canvas] = new SolidColorBrush(Color.Parse("#123456"));
        });

        Assert.True(manager.ApplyThemeLayer(layer, "i2-typography"), manager.LastError);
        var application = Application.Current!;

        var palette = CompletePalette(dictionary =>
        {
            dictionary[NmKeys.Color.Bg.Canvas] = new SolidColorBrush(Color.Parse("#654321"));
        });

        Assert.True(manager.ApplyPalette(palette, "i2-palette"), manager.LastError);
        Assert.Equal("i2-palette", manager.AppliedPaletteId);
        Assert.Equal("i2-palette", manager.AppliedThemeLayerId);

        // Palette-only application must not reset fonts/sizes/line boxes to the base global dictionary.
        Assert.Equal("Georgia", ThemeTestHarness.ValueOf<FontFamily>(application, NmKeys.FontFamily.Ui).Name);
        Assert.Equal(15d, ThemeTestHarness.ValueOf<double>(application, NmKeys.FontSize.Md), 3);
        Assert.Equal(24d, ThemeTestHarness.ValueOf<double>(application, NmKeys.TextLineBox.Body), 3);
        Assert.Equal(Color.Parse("#654321"), ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));
    }

    [AvaloniaFact]
    public void Overlay_toggles_keep_theme_typography_and_use_fixed_provider_order()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var layer = CompleteThemeLayer(dictionary =>
        {
            dictionary[NmKeys.FontFamily.Ui] = new FontFamily("Georgia");
            dictionary[NmKeys.FontSize.Md] = 16d;
            dictionary[NmKeys.LineHeight.Body] = 1.6d;
        });

        Assert.True(manager.ApplyThemeLayer(layer, "i2-order"), manager.LastError);
        var application = Application.Current!;

        // Simulate an independent Global provider appended after the palette. A fixed precedence order
        // must move it in front of the palette; otherwise it would shadow the theme layer's typography.
        var lateGlobal = (ResourceDictionary)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Themes/Tokens.Global.axaml"));
        application.Resources.MergedDictionaries.Add(lateGlobal);

        Assert.True(manager.SetContrast(ContrastMode.High), manager.LastError);
        AssertThemeTypographyIsIntact(application);
        AssertProviderOrder(application, expectPalette: true, expectContrast: true);

        Assert.True(manager.SetDensity(DensityMode.Compact), manager.LastError);
        AssertThemeTypographyIsIntact(application);
        Assert.Equal(24d, ThemeTestHarness.ValueOf<double>(application, NmKeys.Size.ControlHeight));
        AssertProviderOrder(application, expectPalette: true, expectContrast: true);

        Assert.True(manager.SetReducedMotion(true), manager.LastError);
        Assert.Equal(TimeSpan.Zero, ThemeTestHarness.ValueOf<TimeSpan>(application, NmKeys.Motion.Duration.Slow));

        Assert.True(manager.SetContrast(ContrastMode.Standard), manager.LastError);
        Assert.True(manager.SetDensity(DensityMode.Comfortable), manager.LastError);
        Assert.True(manager.SetReducedMotion(false), manager.LastError);
        AssertThemeTypographyIsIntact(application);
        Assert.Equal(28d, ThemeTestHarness.ValueOf<double>(application, NmKeys.Size.ControlHeight));

        static void AssertThemeTypographyIsIntact(Application application)
        {
            Assert.Equal("Georgia", ThemeTestHarness.ValueOf<FontFamily>(application, NmKeys.FontFamily.Ui).Name);
            Assert.Equal(16d, ThemeTestHarness.ValueOf<double>(application, NmKeys.FontSize.Md), 3);
            Assert.Equal(25.6d, ThemeTestHarness.ValueOf<double>(application, NmKeys.TextLineBox.Body), 3);
        }
    }

    [AvaloniaFact]
    public void Failed_appearance_switch_keeps_previous_appearance_and_resources()
    {
        var application = Application.Current!;
        application.Resources.MergedDictionaries.Clear();
        application.Resources.MergedDictionaries.Add(ThemeTestHarness.LoadControlThemes());

        var manager = new DesignSystemThemeManager(application, new BrokenLightPaletteSource());
        try
        {
            Assert.True(manager.Initialize(AppearanceMode.Dark), manager.LastError);
            var canvasBefore = ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas);

            Assert.False(manager.SetAppearance(AppearanceMode.Light));
            Assert.NotNull(manager.LastError);
            Assert.Equal(AppearanceMode.Dark, manager.Appearance);
            Assert.Equal(ThemeVariant.Dark, application.RequestedThemeVariant);
            Assert.Equal(canvasBefore, ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));
            Assert.Equal(DesignSystemThemeManager.BuiltinDarkPaletteId, manager.AppliedPaletteId);
        }
        finally
        {
            manager.Dispose();
        }
    }

    [AvaloniaFact]
    public void Failed_overlay_switches_keep_previous_mode_and_resources()
    {
        var application = Application.Current!;
        application.Resources.MergedDictionaries.Clear();
        application.Resources.MergedDictionaries.Add(ThemeTestHarness.LoadControlThemes());

        var manager = new DesignSystemThemeManager(application, new BrokenOverlaySource());
        try
        {
            Assert.True(manager.Initialize(AppearanceMode.Dark), manager.LastError);
            var panelBefore = ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Panel);
            var heightBefore = ThemeTestHarness.ValueOf<double>(application, NmKeys.Size.ControlHeight);
            var slowBefore = ThemeTestHarness.ValueOf<TimeSpan>(application, NmKeys.Motion.Duration.Slow);

            Assert.False(manager.SetContrast(ContrastMode.High));
            Assert.Equal(ContrastMode.Standard, manager.Contrast);
            Assert.Equal(panelBefore, ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Panel));

            Assert.False(manager.SetDensity(DensityMode.Compact));
            Assert.Equal(DensityMode.Comfortable, manager.Density);
            Assert.Equal(heightBefore, ThemeTestHarness.ValueOf<double>(application, NmKeys.Size.ControlHeight));

            Assert.False(manager.SetReducedMotion(true));
            Assert.False(manager.ReducedMotion);
            Assert.Equal(slowBefore, ThemeTestHarness.ValueOf<TimeSpan>(application, NmKeys.Motion.Duration.Slow));
        }
        finally
        {
            manager.Dispose();
        }
    }

    [AvaloniaFact]
    public void Failed_initialize_keeps_the_manager_uninitialized_with_defaults()
    {
        var application = Application.Current!;
        application.Resources.MergedDictionaries.Clear();
        application.Resources.MergedDictionaries.Add(ThemeTestHarness.LoadControlThemes());

        var manager = new DesignSystemThemeManager(application, new BrokenGlobalSource());
        try
        {
            Assert.False(manager.Initialize(AppearanceMode.Dark));
            Assert.NotNull(manager.LastError);
            Assert.False(manager.IsInitialized);
            Assert.Equal(AppearanceMode.Dark, manager.Appearance);
            Assert.Equal(ContrastMode.Standard, manager.Contrast);
            Assert.Equal(DensityMode.Comfortable, manager.Density);
            Assert.False(manager.ReducedMotion);
            Assert.Null(manager.AppliedPaletteId);
        }
        finally
        {
            manager.Dispose();
        }
    }

    private static void AssertProviderOrder(Application application, bool expectPalette, bool expectContrast)
    {
        var providers = application.Resources.MergedDictionaries.ToList();
        int IndexOf(string key) => providers.FindIndex(provider => provider.TryGetResource(key, ThemeVariant.Default, out _));

        var globalIndex = IndexOf(NmKeys.Space.S3);
        var paletteIndex = IndexOf(NmKeys.Color.Bg.Canvas);
        Assert.True(globalIndex >= 0, "global token provider must be registered");
        Assert.True(paletteIndex >= 0, "palette provider must be registered");
        Assert.True(globalIndex < paletteIndex, $"global tokens ({globalIndex}) must precede palette ({paletteIndex})");
        if (!expectPalette)
        {
            return;
        }

        if (expectContrast)
        {
            // The contrast overlay is the last provider that carries the complete palette.
            var top = application.TryGetResource(NmKeys.Color.Bg.Canvas, ThemeVariant.Default, out var resolved);
            Assert.True(top);
            Assert.NotNull(resolved);
        }
    }

    private static ResourceDictionary CompletePalette(Action<ResourceDictionary>? mutate = null)
    {
        var source = (ResourceDictionary)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Themes/Tokens.Dark.axaml"));
        var palette = new ResourceDictionary();
        foreach (var key in DesignSystemThemeManager.PaletteColorKeys)
        {
            Assert.True(source.TryGetResource(key, ThemeVariant.Default, out var value), $"builtin palette lacks {key}");
            palette[key] = value;
        }

        mutate?.Invoke(palette);
        return palette;
    }

    private static ResourceDictionary CompleteThemeLayer(Action<ResourceDictionary>? mutate = null)
    {
        var layer = CompletePalette();
        var builtin = (ResourceDictionary)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Themes/Tokens.Global.axaml"));
        foreach (var key in DesignSystemThemeManager.ThemeLayerRequiredKeys
                     .Where(static key => !key.StartsWith("Nm.Color.", StringComparison.Ordinal)))
        {
            Assert.True(builtin.TryGetResource(key, ThemeVariant.Default, out var value), $"global dictionary lacks {key}");
            layer[key] = value;
        }

        mutate?.Invoke(layer);
        return layer;
    }

    private sealed class BrokenLightPaletteSource : IDesignSystemResourceSource
    {
        public Uri GlobalTokens => DesignSystemResourceSource.Default.GlobalTokens;

        public Uri DarkPalette => DesignSystemResourceSource.Default.DarkPalette;

        public Uri LightPalette { get; } = new("avares://NewManga.DesignSystem/Themes/DoesNotExist.axaml");

        public Uri HighContrastPalette => DesignSystemResourceSource.Default.HighContrastPalette;

        public Uri CompactDensity => DesignSystemResourceSource.Default.CompactDensity;

        public Uri SpaciousDensity => DesignSystemResourceSource.Default.SpaciousDensity;

        public Uri ReducedMotion => DesignSystemResourceSource.Default.ReducedMotion;
    }

    private sealed class BrokenOverlaySource : IDesignSystemResourceSource
    {
        public Uri GlobalTokens => DesignSystemResourceSource.Default.GlobalTokens;

        public Uri DarkPalette => DesignSystemResourceSource.Default.DarkPalette;

        public Uri LightPalette => DesignSystemResourceSource.Default.LightPalette;

        public Uri HighContrastPalette { get; } = new("avares://NewManga.DesignSystem/Themes/DoesNotExist.axaml");

        public Uri CompactDensity { get; } = new("avares://NewManga.DesignSystem/Themes/DoesNotExist.axaml");

        public Uri SpaciousDensity => DesignSystemResourceSource.Default.SpaciousDensity;

        public Uri ReducedMotion { get; } = new("avares://NewManga.DesignSystem/Themes/DoesNotExist.axaml");
    }

    private sealed class BrokenGlobalSource : IDesignSystemResourceSource
    {
        public Uri GlobalTokens { get; } = new("avares://NewManga.DesignSystem/Themes/DoesNotExist.axaml");

        public Uri DarkPalette => DesignSystemResourceSource.Default.DarkPalette;

        public Uri LightPalette => DesignSystemResourceSource.Default.LightPalette;

        public Uri HighContrastPalette => DesignSystemResourceSource.Default.HighContrastPalette;

        public Uri CompactDensity => DesignSystemResourceSource.Default.CompactDensity;

        public Uri SpaciousDensity => DesignSystemResourceSource.Default.SpaciousDensity;

        public Uri ReducedMotion => DesignSystemResourceSource.Default.ReducedMotion;
    }
}

