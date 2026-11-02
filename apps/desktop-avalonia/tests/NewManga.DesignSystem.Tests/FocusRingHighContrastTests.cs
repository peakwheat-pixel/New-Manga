using System.Linq;
using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-11 (design 03 §3–§4): the shared keyboard focus ring is 2px with 1px offset in
/// standard contrast and thickens to 3px under high contrast; it is keyboard-only and follows focus.
/// </summary>
public sealed class FocusRingHighContrastTests
{
    [AvaloniaFact]
    public void FocusRing_Is2pxStandard_And3pxHighContrast()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var textBox = new TextBox();
        var other = new TextBox();
        FocusRing.SetIsEnabled(textBox, true);
        FocusRing.SetIsEnabled(other, true);
        AutomationProperties.SetName(textBox, "focus probe");
        var window = new Window
        {
            Width = 320,
            Height = 200,
            Content = new Border { Padding = new Thickness(12), Child = new StackPanel { Children = { textBox, other } } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        var ring = VisibleRingOf(window);
        Assert.NotNull(ring);
        Assert.Equal(2d, ring!.BorderThickness.Left, 3);

        Assert.True(manager.SetContrast(ContrastMode.High), manager.LastError);
        other.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        ring = VisibleRingOf(window);
        Assert.NotNull(ring);
        Assert.Equal(3d, ring!.BorderThickness.Left, 3);

        Assert.True(manager.SetContrast(ContrastMode.Standard), manager.LastError);
        Assert.Equal(2d, ThemeTestHarness.ValueOf<Thickness>(Application.Current!, "Nm.Border.Focus").Left);
        other.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        ring = VisibleRingOf(window);
        Assert.NotNull(ring);
        Assert.Equal(2d, ring!.BorderThickness.Left, 3);

        // Pointer focus never paints the keyboard ring (design 03 §3).
        other.Focus(NavigationMethod.Pointer);
        Dispatcher.UIThread.RunJobs();
        Assert.Null(VisibleRingOf(window));
        window.Close();
    }

    private static Border? VisibleRingOf(Window window) =>
        window.GetVisualDescendants()
            .OfType<Border>()
            .FirstOrDefault(border => border.Classes.Contains("nm-focus-ring") && border.IsVisible);
}
