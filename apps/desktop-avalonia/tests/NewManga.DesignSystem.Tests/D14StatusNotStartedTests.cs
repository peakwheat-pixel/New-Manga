using Avalonia;
using Avalonia.Headless.XUnit;
using NewManga.DesignSystem.Accessibility;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// D-14 adjudication A (ADJ-2026-11-03): NotStarted is a real state, not a disabled control.
/// StatusCatalog must name the same Secondary token the status glyph style uses, and that token
/// must meet the frozen 4.5:1 text contrast on both surfaces in both themes.
/// </summary>
public sealed class D14StatusNotStartedTests
{
    [AvaloniaFact]
    public void Catalog_maps_NotStarted_to_the_Secondary_text_token()
    {
        Assert.Equal(NmKeys.Color.Text.Secondary, StatusCatalog.ColorKey(StatusKind.NotStarted));
    }

    [AvaloniaTheory]
    [InlineData(AppearanceMode.Light)]
    [InlineData(AppearanceMode.Dark)]
    public void NotStarted_token_meets_4_5_contrast_on_both_surfaces(AppearanceMode mode)
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        Assert.True(manager.SetAppearance(mode), manager.LastError);
        var app = Application.Current!;
        var foreground = ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Secondary);
        foreach (var surfaceKey in new[] { NmKeys.Color.Bg.Canvas, NmKeys.Color.Bg.Panel })
        {
            var background = ThemeTestHarness.ColorOf(app, surfaceKey);
            var ratio = ContrastMath.ContrastRatio(foreground, background);
            Assert.True(ratio >= 4.5, $"{mode}/{surfaceKey} contrast {ratio:F2}:1 must be >= 4.5:1");
        }
    }
}
