using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Accessibility;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC4/AC8: the Button control theme applies the contract's variants/sizes/icon classes from tokens,
/// the label colour is inherited (review P1: a global TextBlock style must not override Accent.On), the
/// effective render contrast is asserted, and keyboard focus shows the 2px accent outline outside the
/// control without changing its geometry.
/// </summary>
public sealed class ButtonThemeTests
{
    [AvaloniaFact]
    public void Variants_and_sizes_resolve_design_tokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

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
        var failedBrush = Assert.IsAssignableFrom<ISolidColorBrush>(
            app.TryGetResource(NmKeys.Color.Status.Failed, null, out var failedValue) ? failedValue : null);
        Assert.Equal(failedBrush.Color, Assert.IsAssignableFrom<ISolidColorBrush>(danger.BorderBrush).Color);

        Assert.Equal(24d, small.MinHeight);
        Assert.Equal(28d, icon.MinWidth);
        Assert.Equal(28d, primary.MinHeight);

        window.Close();
    }

    [AvaloniaFact]
    public void Primary_and_secondary_button_labels_inherit_the_right_foreground_and_contrast()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var primary = new Button { Content = "主要操作", Classes = { "primary" } };
        var secondary = new Button { Content = "次要操作", Classes = { "secondary" } };
        var window = new Window { Width = 480, Height = 200, Content = new StackPanel { Children = { primary, secondary } } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var accentOn = ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.On);
        var accentBase = ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Base);
        var textPrimary = ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary);

        var primaryLabel = primary.GetVisualDescendants().OfType<TextBlock>().First();
        var secondaryLabel = secondary.GetVisualDescendants().OfType<TextBlock>().First();

        // P1 regression: the label must inherit the Button.Foreground (Accent.On), not be forced to
        // Text.Primary by a global TextBlock style.
        Assert.Equal(accentOn, Assert.IsAssignableFrom<ISolidColorBrush>(primaryLabel.Foreground).Color);
        Assert.Equal(textPrimary, Assert.IsAssignableFrom<ISolidColorBrush>(secondaryLabel.Foreground).Color);
        Assert.Equal(accentOn, Assert.IsAssignableFrom<ISolidColorBrush>(primary.Foreground).Color);

        var renderedRatio = ContrastMath.ContrastRatio(ColorOf(primaryLabel.Foreground), ColorOf(RootOf(primary).Background));
        Assert.True(renderedRatio >= 4.5, $"primary button label contrast is {renderedRatio:F2}:1 (need >= 4.5:1)");
        Assert.True(
            ContrastMath.ContrastRatio(accentOn, accentBase) >= 4.5,
            "accent.on on accent.base must be >= 4.5:1");

        window.Close();
    }

    [AvaloniaFact]
    public void Keyboard_focus_shows_an_outside_two_pixel_accent_outline()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var button = new Button { Content = "focus" };
        var window = new Window { Width = 320, Height = 160, Content = button };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var ring = FocusRingOf(window);
        Assert.True(ring is null, "focus ring must not be visible before keyboard focus");

        var borderThicknessBefore = button.BorderThickness;
        button.Focus(NavigationMethod.Tab);
        Dispatcher.UIThread.RunJobs();

        ring = FocusRingOf(window);
        Assert.NotNull(ring);
        Assert.True(ring!.IsVisible, "keyboard focus should show the accent outline");
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Base), Assert.IsAssignableFrom<ISolidColorBrush>(ring.BorderBrush).Color);
        Assert.Equal(new Thickness(2), ring.BorderThickness);
        // The outline is drawn outside: the ring is larger than the control and the control's own
        // geometry is untouched.
        Assert.True(ring.Bounds.Width >= button.Bounds.Width + 4, $"ring width {ring.Bounds.Width} vs button {button.Bounds.Width}");
        Assert.Equal(borderThicknessBefore, button.BorderThickness);

        window.Close();
    }

    private static Border? FocusRingOf(Window window) => window.GetVisualDescendants()
        .OfType<Border>()
        .FirstOrDefault(border => border.Classes.Contains("nm-focus-ring") && border.IsVisible);

    private static Border RootOf(Button button) => RoleOf(button, "PART_Root");

    private static Border RoleOf(Button button, string name) =>
        button.GetVisualDescendants().OfType<Border>().FirstOrDefault(border => border.Name == name)
        ?? throw new InvalidOperationException($"{name} not found in Button template");

    private static Color ColorOf(IBrush? brush) => Assert.IsAssignableFrom<ISolidColorBrush>(brush).Color;
}


