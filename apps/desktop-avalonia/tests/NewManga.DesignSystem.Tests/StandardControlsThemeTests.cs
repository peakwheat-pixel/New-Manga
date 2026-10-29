using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC4: the remaining standard controls are themed from tokens — CheckBox/RadioButton/ToggleSwitch/
/// ComboBox (with the compact class)/TabControl/ProgressBar/Separator/ScrollBar/MenuFlyout/ContextMenu/
/// ToolTip. Each assertion reads the effective brush/size back from the realized control tree.
/// </summary>
public sealed class StandardControlsThemeTests
{
    [AvaloniaFact]
    public void CheckBox_and_RadioButton_use_token_colors_and_show_selection_markers()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var checkBox = new CheckBox { Content = "启用", IsChecked = true };
        var radio = new RadioButton { Content = "选项", IsChecked = true };
        var window = new Window { Width = 320, Height = 160, Content = new StackPanel { Children = { checkBox, radio } } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var checkBoxBox = Named<Border>(checkBox, "PART_Box");
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Base), ((ISolidColorBrush)checkBoxBox.Background!).Color);
        Assert.True(Named<Avalonia.Controls.Shapes.Path>(checkBox, "PART_CheckGlyph").IsVisible);
        Assert.Equal(28d, checkBox.MinHeight);
        Assert.Equal(28d, radio.MinHeight);
        Assert.True(Named<Border>(radio, "PART_Core").IsVisible);

        checkBox.IsChecked = false;
        Dispatcher.UIThread.RunJobs();
        Assert.False(Named<Avalonia.Controls.Shapes.Path>(checkBox, "PART_CheckGlyph").IsVisible);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Line.Default), ((ISolidColorBrush)checkBoxBox.BorderBrush!).Color);

        window.Close();
    }

    [AvaloniaFact]
    public void ToggleSwitch_track_uses_the_accent_when_checked()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var toggle = new ToggleSwitch { IsChecked = true, OnContent = "开", OffContent = "关" };
        var window = new Window { Width = 320, Height = 120, Content = toggle };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var track = Named<Border>(toggle, "OuterBorder");
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Base), ((ISolidColorBrush)track.Background!).Color);
        Assert.Equal(28d, toggle.MinHeight);

        window.Close();
    }

    [AvaloniaFact]
    public void ComboBox_uses_surface_tokens_and_compact_class()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var combo = new ComboBox { ItemsSource = new[] { "a", "b" }, SelectedIndex = 0 };
        var compact = new ComboBox { Classes = { "compact" }, ItemsSource = new[] { "a" }, SelectedIndex = 0 };
        var window = new Window { Width = 320, Height = 200, Content = new StackPanel { Children = { combo, compact } } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(28d, combo.MinHeight);
        Assert.Equal(24d, compact.MinHeight);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Raised), ((ISolidColorBrush)combo.Background!).Color);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Line.Default), ((ISolidColorBrush)combo.BorderBrush!).Color);

        window.Close();
    }

    [AvaloniaFact]
    public void TabItem_shows_the_accent_selection_pipe()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var first = new TabItem { Header = "页面" };
        var second = new TabItem { Header = "成品" };
        var tabs = new TabControl { Items = { first, second }, SelectedIndex = 0 };
        var window = new Window { Width = 420, Height = 240, Content = tabs };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var pipe = Named<Border>(first, "PART_SelectedPipe");
        Assert.True(pipe.IsVisible);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Base), ((ISolidColorBrush)pipe.Background!).Color);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary), ((ISolidColorBrush)first.Foreground!).Color);

        tabs.SelectedIndex = 1;
        Dispatcher.UIThread.RunJobs();
        Assert.False(pipe.IsVisible);

        window.Close();
    }

    [AvaloniaFact]
    public void ProgressBar_separator_and_scrollbar_are_themed_from_tokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var progress = new ProgressBar { Value = 30, Maximum = 100 };
        var separator = new Separator();
        var scrollBar = new ScrollBar { Orientation = Avalonia.Layout.Orientation.Vertical, Height = 120, Maximum = 100, ViewportSize = 10 };
        var scrollViewer = new ScrollViewer { Content = new TextBlock { Text = "scroll" }, Height = 80 };
        var window = new Window
        {
            Width = 320,
            Height = 280,
            Content = new StackPanel { Children = { progress, separator, scrollBar, scrollViewer } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(4d, progress.MinHeight);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Base), ((ISolidColorBrush)progress.Foreground!).Color);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Line.Subtle), ((ISolidColorBrush)separator.Background!).Color);

        var scrollRoot = scrollBar.GetVisualDescendants().OfType<Grid>().FirstOrDefault(grid => grid.Name == "Root");
        Assert.NotNull(scrollRoot);
        Assert.Equal(8d, scrollRoot!.Width);
        var thumb = scrollBar.GetVisualDescendants().OfType<Thumb>().First();
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Line.Default), ((ISolidColorBrush)thumb.Background!).Color);

        window.Close();
    }

    [AvaloniaFact]
    public void Overlay_chrome_uses_the_overlay_surface_tokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var presenter = new MenuFlyoutPresenter();
        var contextMenu = new ContextMenu();
        var toolTip = new ToolTip { Content = "提示" };
        var menuItem = new MenuItem { Header = "命令" };
        var window = new Window
        {
            Width = 320,
            Height = 200,
            Content = new StackPanel { Children = { presenter, contextMenu, toolTip, menuItem } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Overlay), ((ISolidColorBrush)presenter.Background!).Color);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Line.Default), ((ISolidColorBrush)contextMenu.BorderBrush!).Color);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Overlay), ((ISolidColorBrush)toolTip.Background!).Color);
        Assert.Equal(24d, menuItem.MinHeight);

        window.Close();
    }

    private static T Named<T>(Control control, string name)
        where T : Control =>
        control.GetVisualDescendants().OfType<T>().FirstOrDefault(candidate => candidate.Name == name)
        ?? throw new InvalidOperationException($"{name} not found in {control.GetType().Name} template");
}
