using System.Linq;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

public sealed class FocusRingOffsetTests
{
    private static Border Ring(Window window) => window.GetVisualDescendants().OfType<Border>()
        .Single(b => b.Classes.Contains("nm-focus-ring"));

    [AvaloniaTheory]
    [InlineData(0)] // unchanged Current geometry
    [InlineData(1)] // Fluent opt-in, inherited by children
    public void R2006_StandardAndLiveHighContrast_UseOffsetPlusStrokeOnEveryEdge(double offset)
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var input = new TextBox();
        FocusRing.SetIsEnabled(input, true);
        var root = new Border { Padding = new Thickness(20), Child = input };
        FocusRing.SetOffset(root, offset);
        var window = new Window { Width = 400, Height = 200, Content = root };
        try
        {
            window.Show();
            Dispatcher.UIThread.RunJobs();
            input.Focus(NavigationMethod.Tab);
            foreach (var contrast in new[] { ContrastMode.Standard, ContrastMode.High, ContrastMode.Standard })
            {
                Assert.True(manager.SetContrast(contrast), manager.LastError);
                Dispatcher.UIThread.RunJobs();
                window.UpdateLayout();
                var ring = Ring(window);
                var stroke = contrast == ContrastMode.High ? 3d : 2d;
                Assert.True(ring.IsVisible);
                Assert.Equal(stroke, ring.BorderThickness.Left);
                Assert.Equal(input.Bounds.Width + 2 * (stroke + offset), ring.Bounds.Width, 5);
                Assert.Equal(input.Bounds.Height + 2 * (stroke + offset), ring.Bounds.Height, 5);
                var controlOrigin = input.TranslatePoint(default, window)!.Value;
                var ringOrigin = ring.TranslatePoint(default, window)!.Value;
                Assert.Equal(offset, controlOrigin.X - ringOrigin.X - stroke, 5);
                Assert.Equal(offset, controlOrigin.Y - ringOrigin.Y - stroke, 5);
                Assert.Equal(offset, ringOrigin.X + ring.Bounds.Width - stroke - controlOrigin.X - input.Bounds.Width, 5);
                Assert.Equal(offset, ringOrigin.Y + ring.Bounds.Height - stroke - controlOrigin.Y - input.Bounds.Height, 5);
            }
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(false)]
    [InlineData(true)]
    public void R2006_ScrollClipping_IncludesGap_NotOnlyStroke_AndRestoresRing(bool highContrast)
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        manager.SetContrast(highContrast ? ContrastMode.High : ContrastMode.Standard);
        var stroke = highContrast ? 3d : 2d;
        var input = new TextBox();
        FocusRing.SetIsEnabled(input, true);
        var stack = new StackPanel
        {
            Margin = new Thickness(stroke + 3),
            Children = { input, new Border { Height = 500 } },
        };
        FocusRing.SetOffset(stack, 1);
        var scroll = new ScrollViewer { Height = 110, Content = stack };
        var window = new Window { Width = 400, Height = 220, Content = new Border { Padding = new Thickness(20), Child = scroll } };
        try
        {
            window.Show();
            Dispatcher.UIThread.RunJobs();
            input.Focus(NavigationMethod.Tab);
            Dispatcher.UIThread.RunJobs();
            Assert.True(Ring(window).IsVisible);
            scroll.Offset = new Vector(0, 2.75); // stroke fits; the additional 1px gap does not
            Dispatcher.UIThread.RunJobs();
            window.UpdateLayout();
            Assert.False(Ring(window).IsVisible);
            scroll.Offset = default;
            Dispatcher.UIThread.RunJobs();
            window.UpdateLayout();
            Assert.True(Ring(window).IsVisible);
        }
        finally { window.Close(); }
    }
}
