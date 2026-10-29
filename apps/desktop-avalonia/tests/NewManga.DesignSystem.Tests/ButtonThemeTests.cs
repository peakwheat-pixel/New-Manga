using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC4/AC8: the Button control theme applies the contract's variants/sizes/icon classes from tokens and
/// draws a real 2px accent focus outline (no shadow) on keyboard focus.
/// </summary>
public sealed class ButtonThemeTests
{
    [AvaloniaFact]
    public void Variants_and_sizes_resolve_design_tokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var primary = new Button { Content = "保存", Classes = { "primary" } };
        var secondary = new Button { Content = "取消", Classes = { "secondary" } };
        var ghost = new Button { Content = "跳过", Classes = { "ghost" } };
        var danger = new Button { Content = "删除", Classes = { "danger" } };
        var small = new Button { Content = "sm", Classes = { "sm" } };
        var icon = new Button { Content = "…", Classes = { "icon" } };

        var window = new Window
        {
            Width = 640,
            Height = 240,
            Content = new StackPanel
            {
                Children = { primary, secondary, ghost, danger, small, icon },
            },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(Color.Parse("#FFD9A04B"), RootOf(primary).Background is SolidColorBrush fill ? fill.Color : default);
        Assert.Equal(Color.Parse("#FF17181A"), ((SolidColorBrush)primary.Foreground!).Color);

        Assert.Equal(Color.Parse("#FF22252A"), RootOf(secondary).Background is SolidColorBrush secondaryFill ? secondaryFill.Color : default);
        Assert.Equal(Colors.Transparent, Assert.IsAssignableFrom<ISolidColorBrush>(ghost.Background).Color);
        Assert.Equal(Color.Parse("#FFC9634F"), ((SolidColorBrush)danger.BorderBrush!).Color);

        Assert.Equal(24d, small.MinHeight);
        Assert.Equal(28d, icon.MinWidth);
        Assert.Equal(28d, primary.MinHeight);

        window.Close();
    }

    [AvaloniaFact]
    public void Keyboard_focus_shows_a_two_pixel_accent_outline()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var button = new Button { Content = "focus" };
        var window = new Window { Width = 320, Height = 160, Content = button };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var ring = RoleOf(button, "PART_FocusRing");
        Assert.False(ring.IsVisible);
        var thickness = Assert.IsType<Thickness>(Application.Current!.TryGetResource(
            NmKeys.Border.Focus, null, out var thicknessValue) ? thicknessValue : null);
        Assert.Equal(new Thickness(2), thickness);
        Assert.Equal(Color.Parse("#FFD9A04B"), ((SolidColorBrush)ring.BorderBrush!).Color);

        // Tab navigation sets :focus-visible (programmatic pointer focus must not show the ring).
        button.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();
        Assert.True(ring.IsVisible, "focus-visible should show the accent outline");

        window.Close();
    }

    private static Border RootOf(Button button) => RoleOf(button, "PART_Root");

    private static Border RoleOf(Button button, string name) =>
        button.GetVisualDescendants().OfType<Border>().FirstOrDefault(border => border.Name == name)
        ?? throw new InvalidOperationException($"{name} not found in Button template");
}
