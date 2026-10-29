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
        var window = new Window { Width = 320, Height = 200, Content = textBox };
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
        var window = new Window { Width = 320, Height = 200, Content = textBox };
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
        var stack = new StackPanel { Spacing = 8 };
        for (var index = 0; index < 12; index++)
        {
            var textBox = new TextBox { Text = $"row {index}" };
            FocusRing.SetIsEnabled(textBox, true);
            stack.Children.Add(textBox);
        }

        var scrollViewer = new ScrollViewer { Height = 110, Content = stack };
        var window = new Window { Width = 320, Height = 200, Content = scrollViewer };
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

    private static Border? VisibleRingOf(Window window) => window.GetVisualDescendants()
        .OfType<Border>()
        .FirstOrDefault(border => border.Classes.Contains("nm-focus-ring") && border.IsVisible);
}

