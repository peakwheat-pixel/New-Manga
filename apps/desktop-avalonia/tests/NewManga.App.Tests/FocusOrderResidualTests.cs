using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-11 (design 03 §3): controls that are not visible must not accept focus, so they
/// stay out of the Tab order; visible siblings remain focusable.
/// </summary>
public sealed class FocusOrderResidualTests
{
    [AvaloniaFact]
    public void HiddenControl_IsNotFocusable_AndVisibleSiblingIs()
    {
        var hidden = new Button { Content = "hidden", IsVisible = false };
        var visible = new Button { Content = "visible" };
        var window = new Window
        {
            Width = 240,
            Height = 120,
            Content = new StackPanel { Spacing = 8, Children = { hidden, visible } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.False(hidden.Focus(NavigationMethod.Tab), "an invisible control must not accept keyboard focus");
        Assert.True(visible.Focus(NavigationMethod.Tab), "the visible sibling must remain focusable");
        window.Close();
    }
}
