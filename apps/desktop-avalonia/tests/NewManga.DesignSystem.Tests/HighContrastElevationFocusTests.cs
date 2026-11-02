using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-8/I-11 (design 01 §2.3, 03 §4): high contrast keeps the generated palette file
/// untouched while degenerating elevation shadows to the existing 1px hairline border and thickening the
/// shared focus ring token from 2px to 3px; standard contrast restores the frozen tokens unchanged.
/// </summary>
public sealed class HighContrastElevationFocusTests
{
    [AvaloniaFact]
    public void HighContrast_DegeneratesElevationToHairline_AndThickensFocusToken()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var application = Application.Current!;

        var surface = new Border
        {
            Width = 120,
            Height = 48,
            Classes = { "fluent-surface-card" },
        };
        var window = new Window { Width = 320, Height = 200, Content = surface };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(surface.BoxShadow.Count > 0, "standard contrast must consume Nm.Elevation.1");
        Assert.Equal(1d, surface.BorderThickness.Left, 3);
        Assert.Equal(2d, ThemeTestHarness.ValueOf<Thickness>(application, "Nm.Border.Focus").Left);

        Assert.True(manager.SetContrast(ContrastMode.High), manager.LastError);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(0, surface.BoxShadow.Count);
        Assert.Equal(1d, surface.BorderThickness.Left, 3);
        Assert.Equal(3d, ThemeTestHarness.ValueOf<Thickness>(application, "Nm.Border.Focus").Left);

        Assert.True(manager.SetContrast(ContrastMode.Standard), manager.LastError);
        Dispatcher.UIThread.RunJobs();

        Assert.True(surface.BoxShadow.Count > 0, "standard contrast must restore Nm.Elevation.1");
        Assert.Equal(2d, ThemeTestHarness.ValueOf<Thickness>(application, "Nm.Border.Focus").Left);
        window.Close();
    }
}
