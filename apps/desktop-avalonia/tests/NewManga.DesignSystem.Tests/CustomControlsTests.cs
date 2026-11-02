using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Presenters;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Accessibility;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC5/AC6: the M0 custom-control set renders from tokens, the status language is a strict
/// hue+symbol+text encoding whose symbols come only from the generated token catalog, and the
/// controls refresh values from the live resource stack.
/// </summary>
public sealed class CustomControlsTests
{
    [AvaloniaFact]
    public void Status_catalog_has_nine_unique_symbols_and_labels()
    {
        var kinds = Enum.GetValues<StatusKind>();
        Assert.Equal(9, kinds.Length);

        var symbols = kinds.Select(StatusCatalog.Symbol).ToArray();
        Assert.Equal(9, symbols.Distinct(StringComparer.Ordinal).Count());
        Assert.All(kinds, kind => Assert.False(string.IsNullOrEmpty(StatusCatalog.Label(kind))));
        Assert.All(kinds, kind => Assert.StartsWith("Nm.Color.", StatusCatalog.ColorKey(kind), StringComparison.Ordinal));

        // Symbols are the frozen token values, not hand-typed literals in the control.
        Assert.Equal(NmStatusSymbols.Done, StatusCatalog.Symbol(StatusKind.Done));
        Assert.Equal(NmStatusSymbols.Stale, StatusCatalog.Symbol(StatusKind.Stale));
        Assert.Equal(NmStatusSymbols.Locked, StatusCatalog.Symbol(StatusKind.Locked));
    }

    [AvaloniaFact]
    public void StatusGlyph_and_StatusBadge_encode_hue_symbol_and_text()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var glyph = new StatusGlyph { Status = StatusKind.Failed };
        var badge = new StatusBadge { Status = StatusKind.Stale };
        var window = new Window { Width = 320, Height = 160, Content = new StackPanel { Children = { glyph, badge } } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(NmStatusSymbols.Failed, glyph.Text);
        Assert.Contains("failed", glyph.Classes);
        Assert.True(glyph.FontSize > 0);

        var badgeGlyph = badge.GetVisualDescendants().OfType<StatusGlyph>().First();
        Assert.Equal(NmStatusSymbols.Stale, badgeGlyph.Text);
        Assert.Contains(StatusCatalog.Label(StatusKind.Stale), badge.GetVisualDescendants().OfType<TextBlock>().Select(block => block.Text));
        Assert.Equal(
            ThemeTestHarness.ColorOf(app, NmKeys.Color.StatusMuted.Stale),
            ((ISolidColorBrush)badge.Background!).Color);

        window.Close();
    }

    [AvaloniaFact]
    public void Chip_toggles_and_raises_clicked()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var chip = new Chip { Text = "失败 12", Status = StatusKind.Failed };
        var window = new Window { Width = 320, Height = 120, Content = new StackPanel { Children = { chip } } };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var clicks = 0;
        chip.Clicked += (_, _) => clicks++;
        Assert.False(chip.IsActive);

        chip.RaiseEvent(CreatePointerPressed(chip));
        Dispatcher.UIThread.RunJobs();
        Assert.True(chip.IsActive);
        Assert.Equal(1, clicks);
        Assert.Contains("active", chip.Classes);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Muted), ((ISolidColorBrush)chip.Background!).Color);

        var label = Assert.IsType<TextBlock>(chip.Child);
        Assert.Equal("失败 12", label.Text);
        Assert.Contains("nm-status-failed", label.Classes);

        window.Close();
    }

    [AvaloniaFact]
    public void Kbd_SegmentedControl_and_SearchField_expose_their_behaviour()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var kbd = new Kbd { Gesture = "Ctrl+K" };
        var segmented = new SegmentedControl { Items = new[] { "页面", "成品", "分屏" }, SelectedIndex = 0 };
        var search = new SearchField { Placeholder = "搜索作品" };
        var window = new Window
        {
            Width = 480,
            Height = 240,
            Content = new StackPanel { Children = { kbd, segmented, search } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal("Ctrl+K", Assert.IsType<TextBlock>(kbd.Child).Text);

        var segmentButtons = segmented.GetVisualDescendants().OfType<Button>().ToArray();
        Assert.Equal(3, segmentButtons.Length);
        Assert.Contains("selected", segmentButtons[0].Classes);
        var selections = 0;
        segmented.SelectionChanged += (_, index) => selections += index == 2 ? 1 : 0;
        segmentButtons[2].RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(2, segmented.SelectedIndex);
        Assert.Equal(1, selections);

        var textBox = search.GetVisualDescendants().OfType<TextBox>().First();
        Assert.Equal("搜索作品", textBox.Watermark);
        textBox.Text = "猎人";
        Dispatcher.UIThread.RunJobs();
        Assert.Equal("猎人", search.Text);
        textBox.RaiseEvent(new KeyEventArgs { RoutedEvent = InputElement.KeyDownEvent, Key = Key.Escape });
        Assert.Equal(string.Empty, textBox.Text);

        window.Close();
    }

    [AvaloniaFact]
    public void EmptyState_AlertBanner_and_CountChips_compose_actions_and_counts()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var empty = new EmptyState { Title = "还没有作品", Hint = "导入第一部漫画开始翻译", ActionText = "导入" };
        var banner = new AlertBanner
        {
            Severity = StatusKind.Blocked,
            Title = "需要解除阻塞",
            Message = "3 个页面等待人工确认",
            ActionText = "查看",
        };
        var counts = new CountChips
        {
            Counts = new[]
            {
                new CountChipItem("总页数", 120),
                new CountChipItem("失败", 3, StatusKind.Failed),
                new CountChipItem("过期", 2, StatusKind.Stale),
            },
        };
        var window = new Window
        {
            Width = 560,
            Height = 320,
            Content = new StackPanel { Children = { empty, banner, counts } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var emptyAction = empty.GetVisualDescendants().OfType<Button>().First();
        Assert.True(emptyAction.IsVisible);
        Assert.Contains(empty.GetVisualDescendants().OfType<TextBlock>(), block => block.Text == "还没有作品");
        var invoked = 0;
        empty.ActionInvoked += (_, _) => invoked++;
        emptyAction.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Assert.Equal(1, invoked);

        Assert.Contains("blocked", banner.Classes);
        Assert.Equal(
            ThemeTestHarness.ColorOf(app, NmKeys.Color.StatusMuted.Blocked),
            ((ISolidColorBrush)banner.Background!).Color);
        Assert.Equal(NmStatusSymbols.Blocked, banner.GetVisualDescendants().OfType<StatusGlyph>().First().Text);

        var chips = counts.GetVisualDescendants().OfType<Chip>().ToArray();
        Assert.Equal(3, chips.Length);
        Assert.Equal("失败 3", chips[1].Text);
        CountChipItem? clicked = null;
        counts.ChipClicked += (_, item) => clicked = item;
        chips[1].RaiseEvent(CreatePointerPressed(chips[1]));
        Assert.Equal("失败", clicked?.Label);

        window.Close();
    }

    [AvaloniaFact]
    public void Drawer_Modal_TopBand_and_Icon_use_tokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var drawer = new Drawer { IsOpen = true, Header = "详情", Content = new TextBlock { Text = "body" } };
        var modal = new Modal { IsOpen = true, Title = "确认", Content = new TextBlock { Text = "danger" }, PrimaryActionText = "继续" };
        var topBand = new TopBand
        {
            LeftContent = new TextBlock { Text = "Library" },
            CenterContent = new TextBlock { Text = "作品 › 章节" },
            RightContent = new TextBlock { Text = "Ctrl+K" },
        };
        var icon = new NmIcon { Kind = NmIconKind.Search };
        var window = new Window
        {
            Width = 640,
            Height = 360,
            Content = new Grid { Children = { topBand, drawer, modal, icon } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(drawer.IsVisible);
        Assert.Equal(360d, drawer.Width);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Panel), ((ISolidColorBrush)drawer.Background!).Color);

        Assert.True(modal.IsVisible);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Scrim), ((ISolidColorBrush)modal.Background!).Color);
        var closeRequested = 0;
        modal.CloseRequested += (_, _) => closeRequested++;
        modal.RaiseEvent(new KeyEventArgs { RoutedEvent = InputElement.KeyDownEvent, Key = Key.Escape });
        Assert.Equal(1, closeRequested);

        Assert.Equal(36d, topBand.Height);
        Assert.Equal(3, topBand.GetVisualDescendants().OfType<ContentPresenter>()
            .Count(presenter => presenter.Content is TextBlock));

        Assert.NotNull(icon.Data);
        Assert.Equal(20d, icon.Width);
        Assert.Equal(1.25d, icon.StrokeThickness);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Secondary), ((ISolidColorBrush)icon.Stroke!).Color);
        icon.Classes.Add("active");
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Accent.Base), ((ISolidColorBrush)icon.Stroke!).Color);

        window.Close();
    }

    [AvaloniaFact]
    public void Skeleton_renders_the_three_canonical_shapes_from_tokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var bookCard = new Skeleton { Variant = SkeletonVariant.BookCard, Width = 120 };
        var row = new Skeleton { Variant = SkeletonVariant.Row, Width = 320 };
        var panel = new Skeleton { Variant = SkeletonVariant.Panel, Width = 240 };
        var window = new Window
        {
            Width = 520,
            Height = 420,
            Content = new StackPanel { Spacing = 12, Children = { bookCard, row, panel } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(180d, bookCard.Height);
        Assert.Equal(28d, row.Height);
        Assert.Equal(96d, panel.Height);
        Assert.Equal(ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Raised), ((ISolidColorBrush)bookCard.Background!).Color);
        Assert.Equal(new CornerRadius(2), bookCard.CornerRadius);
        Assert.Contains("book-card", bookCard.Classes);
        Assert.Contains("row", row.Classes);
        Assert.Contains("panel", panel.Classes);

        // Skeleton blocks are static: no pulse/shimmer animation is attached.
        Assert.Null(bookCard.Transitions);

        window.Close();
    }

    [AvaloniaFact]
    public void Icon_set_covers_the_primary_spaces_and_state_actions()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var required = new[]
        {
            // four primary spaces
            NmIconKind.Library, NmIconKind.Studio, NmIconKind.Reader, NmIconKind.Settings,
            // transport / run state actions
            NmIconKind.Play, NmIconKind.Pause, NmIconKind.Stop, NmIconKind.Retry,
            // data and navigation actions
            NmIconKind.Export, NmIconKind.Import, NmIconKind.Search, NmIconKind.Command,
            NmIconKind.Theme, NmIconKind.Lock, NmIconKind.History, NmIconKind.Refresh,
            NmIconKind.Close, NmIconKind.Delete, NmIconKind.Edit, NmIconKind.Folder,
            NmIconKind.File, NmIconKind.Chapter, NmIconKind.Page, NmIconKind.Eye,
            NmIconKind.Split, NmIconKind.ZoomIn, NmIconKind.ZoomOut, NmIconKind.FitWindow,
        };

        var missing = required.Where(kind => !Enum.IsDefined(kind)).ToArray();
        Assert.Empty(missing);

        var window = new Window
        {
            Width = 880,
            Height = 220,
            Content = new WrapPanel(),
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var wrap = (WrapPanel)window.Content!;
        // I2/P3: render EVERY declared icon kind, not only the required subset.
        var allKinds = Enum.GetValues<NmIconKind>();
        Assert.Equal(41, allKinds.Length);
        foreach (var kind in allKinds)
        {
            var icon = new NmIcon { Kind = kind };
            wrap.Children.Add(icon);
            Assert.NotNull(icon.Data);
            Assert.True(icon.Data!.Bounds.Width > 0 && icon.Data.Bounds.Height > 0, $"{kind} has empty geometry");
            Assert.Equal(20d, icon.Width);
            Assert.Equal(1.25d, icon.StrokeThickness);
        }

        Assert.All(required, kind => Assert.True(Enum.IsDefined(kind), $"{kind} must stay in the vocabulary"));
        window.Close();
    }

    [AvaloniaFact]
    public void Breakpoint_tokens_are_the_single_shared_layout_scale()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        Assert.Equal(1600d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.Breakpoint.Full));
        Assert.Equal(1280d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.Breakpoint.Compact));
        Assert.Equal(1024d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.Breakpoint.Narrow));
    }

    private static PointerPressedEventArgs CreatePointerPressed(Control target) =>
        new(
            target,
            new Pointer(id: 1, PointerType.Mouse, isPrimary: true),
            target,
            new Point(4, 4),
            timestamp: 0,
            new PointerPointProperties(RawInputModifiers.LeftMouseButton, PointerUpdateKind.LeftButtonPressed),
            KeyModifiers.None);
}

