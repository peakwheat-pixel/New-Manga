using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Theming;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// C-2-I1 regression: a theme layer must keep the R-15 line-height split — the
/// <c>Nm.LineHeight.*</c> aliases carry frozen multipliers (1.25 / 1.45 / 1.6) and the absolute pixels
/// Avalonia renders are <c>Nm.TextLineBox.*</c>, derived by the design system as fontSize x multiplier.
/// Before this fix the composer emitted pixels into the alias keys, the manager multiplied them by the
/// font size again, and every text line box grew ~12x as soon as any theme layer was applied (including
/// the v2 shell startup path, which initializes the theme service).
/// </summary>
public sealed class LineHeightContractTests : IDisposable
{
    private static readonly double[] FrozenMultipliers = [1.25, 1.45, 1.6];

    private readonly TempDirectory _temp = new();

    public void Dispose() => _temp.Dispose();

    [Fact]
    public void ComposedLayer_CarriesFrozenMultipliersInTheAliasKeys()
    {
        var layer = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);

        foreach (var tier in ThemeTokenBaseline.LineHeightTiers)
        {
            var value = Assert.IsType<double>(layer[tier.ResourceKey]);
            Assert.Contains(value, FrozenMultipliers);
            Assert.InRange(value, 1.0, 2.5);
        }

        // The three contract multipliers stay the frozen values as well.
        Assert.Equal(1.25, Assert.IsType<double>(layer[NmKeys.LineHeight.Tight]));
        Assert.Equal(1.45, Assert.IsType<double>(layer[NmKeys.LineHeight.Normal]));
        Assert.Equal(1.6, Assert.IsType<double>(layer[NmKeys.LineHeight.Loose]));
    }

    [Fact]
    public void ComposedLayer_KeepsTheFrozenFiftyNineKeysAndNoPixels()
    {
        var layer = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);

        // The frozen layer is exactly 59 keys: the absolute line boxes are derived by the design system,
        // not carried in the layer (contract §4.1 / R-15).
        Assert.Equal(59, layer.Count);
        Assert.All(
            DesignSystemThemeManager.ThemeLayerRequiredKeys,
            key => Assert.True(layer.ContainsKey(key), $"composed layer is missing required key {key}"));

        foreach (var tier in ThemeTokenBaseline.LineHeightTiers)
        {
            var multiplier = Assert.IsType<double>(layer[tier.ResourceKey]);
            var fontSize = Assert.IsType<double>(layer[tier.FontSizeKey]);
            Assert.InRange(multiplier, 1.0, 2.5);
            Assert.InRange(multiplier * fontSize, fontSize, fontSize * 2.5);
        }
    }

    [AvaloniaFact]
    public void Manager_RejectsLayerThatPutsPixelsInTheMultiplierAliases()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var layer = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);
        var dictionary = new ResourceDictionary();
        foreach (var (key, value) in layer)
        {
            dictionary[key] = value;
        }

        dictionary[NmKeys.LineHeight.Label] = 16.2; // absolute pixels leaked into an alias

        var applied = manager.ApplyThemeLayer(dictionary, "c2-i1-broken-alias");

        Assert.False(applied);
        Assert.Contains("line-height aliases must stay within", manager.LastError, StringComparison.Ordinal);
        Assert.Equal(
            1.25,
            ThemeTestHarness.ValueOf<double>(ThemeTestHarness.Application, NmKeys.LineHeight.Label));
    }

    [AvaloniaFact]
    public void AppliedThemeLayer_ProducesAbsoluteLineBoxesNearTheFontSize()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var layer = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);

        Assert.True(sink.ApplyThemeLayer(layer, ThemeDefaults.DefaultThemeId), sink.LastError);

        var application = ThemeTestHarness.Application;
        var bodySize = ThemeTestHarness.ValueOf<double>(application, NmKeys.FontSize.Md);
        var bodyMultiplier = ThemeTestHarness.ValueOf<double>(application, NmKeys.LineHeight.Body);
        var bodyLineBox = ThemeTestHarness.ValueOf<double>(application, NmKeys.TextLineBox.Body);

        Assert.InRange(bodyMultiplier, 1.0, 2.5);
        Assert.InRange(bodyLineBox, bodySize, bodySize * 2.5);
        Assert.Equal(Math.Round(bodySize * bodyMultiplier, 2), bodyLineBox, precision: 2);
    }

    [AvaloniaFact]
    public void RenderedTextBlock_KeepsItsLineBoxBounded_AfterLayerApply()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var layer = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);
        Assert.True(sink.ApplyThemeLayer(layer, ThemeDefaults.DefaultThemeId), sink.LastError);

        var metrics = RenderProseBlock();
        Assert.InRange(metrics.FontSize, 1, 100);
        Assert.InRange(metrics.LineHeight, metrics.FontSize, metrics.FontSize * 2.5);
        Assert.InRange(metrics.LineBoxHeight, metrics.LineHeight - 1, metrics.LineHeight + 1);
    }

    [AvaloniaFact]
    public void RenderedTextBlock_KeepsItsLineBoxBounded_AfterThemeServiceInitialize()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var registry = new ThemeRegistry(_temp.Path);
        var store = new ThemeSettingsStore(_temp.File("theme-settings.json"), registry);
        var service = new ThemeService(registry, store, sink);

        service.InitializeAsync().GetAwaiter().GetResult();

        var application = ThemeTestHarness.Application;
        Assert.InRange(
            ThemeTestHarness.ValueOf<double>(application, NmKeys.LineHeight.Body),
            1.0,
            2.5);

        var metrics = RenderProseBlock();
        Assert.InRange(metrics.LineHeight, metrics.FontSize, metrics.FontSize * 2.5);
        Assert.InRange(metrics.LineBoxHeight, metrics.LineHeight - 1, metrics.LineHeight + 1);
    }

    private readonly record struct ProseMetrics(
        double FontSize,
        double LineHeight,
        double LineBoxHeight);

    /// <summary>Shows a real window with a DS "body" text block and measures its rendered line box.</summary>
    private static ProseMetrics RenderProseBlock()
    {
        var block = new TextBlock
        {
            Text = "行高回归基线",
            TextWrapping = TextWrapping.NoWrap,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Top,
            Classes = { "body" },
        };

        var window = new Window
        {
            Width = 420,
            Height = 240,
            Content = new Border { Padding = new Thickness(12), Child = block },
        };
        window.Show();
        for (var i = 0; i < 5; i++)
        {
            Dispatcher.UIThread.RunJobs();
            window.UpdateLayout();
        }

        Assert.True(block.Bounds.Height > 0, "the text block was not laid out");
        var metrics = new ProseMetrics(block.FontSize, block.LineHeight, block.DesiredSize.Height);
        window.Close();
        return metrics;
    }
}
