using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// D-1 I2 P2-⑤: the shared focus outline is keyboard-only (pointer focus must not paint it) and it is
/// suppressed while the focused control is clipped by an ancestor ScrollViewer.
/// </summary>
public sealed class FocusRingBehaviourTests
{
    [AvaloniaFact]
    public void Pointer_focus_does_not_draw_the_keyboard_outline()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var textBox = new TextBox();
        FocusRing.SetIsEnabled(textBox, true);
        var window = new Window { Width = 320, Height = 200, Content = new Border { Padding = new Thickness(12), Child = textBox } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        textBox.Focus(NavigationMethod.Pointer);
        Dispatcher.UIThread.RunJobs();

        Assert.Null(VisibleRingOf(window));
        window.Close();
    }

    [AvaloniaFact]
    public void Keyboard_focus_draws_the_outline()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var textBox = new TextBox();
        FocusRing.SetIsEnabled(textBox, true);
        var window = new Window { Width = 320, Height = 200, Content = new Border { Padding = new Thickness(12), Child = textBox } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();

        Assert.NotNull(VisibleRingOf(window));
        window.Close();
    }

    [AvaloniaFact]
    public void Scrolling_the_focused_control_out_of_the_viewport_hides_the_outline()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var stack = new StackPanel { Spacing = 8, Margin = new Thickness(4) };
        for (var index = 0; index < 12; index++)
        {
            var textBox = new TextBox { Text = $"row {index}" };
            FocusRing.SetIsEnabled(textBox, true);
            stack.Children.Add(textBox);
        }

        var scrollViewer = new ScrollViewer { Height = 110, Content = stack };
        var window = new Window { Width = 320, Height = 220, Content = new Border { Padding = new Thickness(12), Child = scrollViewer } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var first = (TextBox)stack.Children[0];
        first.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        Assert.NotNull(VisibleRingOf(window));

        scrollViewer.Offset = new Vector(0, 300);
        Dispatcher.UIThread.RunJobs();
        Assert.Null(VisibleRingOf(window));

        scrollViewer.Offset = new Vector(0, 0);
        Dispatcher.UIThread.RunJobs();
        Assert.NotNull(VisibleRingOf(window));
        window.Close();
    }

    [AvaloniaFact]
    public void Repeated_enable_and_focus_cycles_do_not_leak_rings_or_handlers()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var textBox = new TextBox();
        var window = new Window { Width = 320, Height = 200, Content = new Border { Padding = new Thickness(12), Child = textBox } };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        

        for (var index = 0; index < 25; index++)
        {
            FocusRing.SetIsEnabled(textBox, true);
            Assert.True(FocusRing.IsSubscribedFor(textBox));
            textBox.Focus(NavigationMethod.Tab);
            Dispatcher.UIThread.RunJobs();
            FocusRing.SetIsEnabled(textBox, false);
            Dispatcher.UIThread.RunJobs();
            Assert.False(FocusRing.IsSubscribedFor(textBox));
        }

        FocusRing.SetIsEnabled(textBox, true);
        Assert.True(FocusRing.IsSubscribedFor(textBox));
        var callsBeforeFocus = FocusRing.PositionCallCountFor(textBox);
        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        Assert.True(FocusRing.PositionCallCountFor(textBox) > callsBeforeFocus, "focus must drive the ring position callback");

        var rings = window.GetVisualDescendants()
            .OfType<Border>()
            .Where(border => border.Classes.Contains("nm-focus-ring"))
            .ToArray();
        var ring = Assert.Single(rings);
        Assert.True(ring.IsVisible);

        FocusRing.SetIsEnabled(textBox, false);
        Dispatcher.UIThread.RunJobs();
        Assert.False(FocusRing.IsSubscribedFor(textBox));
        Assert.Null(VisibleRingOf(window));

        // With the handlers removed, another focus event must not invoke the position callback.
        var callsAfterDisable = FocusRing.PositionCallCountFor(textBox);
        textBox.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(callsAfterDisable, FocusRing.PositionCallCountFor(textBox));
        window.Close();
    }

    private static Border? VisibleRingOf(Window window) => window.GetVisualDescendants()
        .OfType<Border>()
        .FirstOrDefault(border => border.Classes.Contains("nm-focus-ring") && border.IsVisible);
}




