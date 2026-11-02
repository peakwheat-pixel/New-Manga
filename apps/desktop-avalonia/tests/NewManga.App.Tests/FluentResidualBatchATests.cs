using System.IO;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Animation;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 Batch A：I-12（控制台入口）/I-14（源不可用警示）/I-9（未保存圆点）/
/// I-10（工具条自动隐藏）/I-1（UI memento）/I-2（分栏折叠）/I-13（9 行状态视觉骨架）。
/// </summary>
public sealed class FluentResidualBatchATests : IDisposable
{
    private static readonly byte[] TinyPng = Convert.FromBase64String(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==");

    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea06-residual-a-{Guid.NewGuid():N}");

    public FluentResidualBatchATests() => Directory.CreateDirectory(_root);

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    private static FluentShell CreateShell(FakeHostController? host = null, AppearanceCoordinator? appearance = null)
    {
        var shell = FluentShell.CreateRoot(host: host, appearance: appearance);
        shell.Show();
        Dispatcher.UIThread.RunJobs();
        return shell;
    }

    private static Button? FindButton(Control root, string content) =>
        root.GetVisualDescendants().OfType<Button>()
            .FirstOrDefault(button => string.Equals(button.Content?.ToString(), content, StringComparison.Ordinal));

    // ---------------------------------------------------------------- I-12：控制台入口

    [AvaloniaFact]
    public void I12_SpaceConsole_Click_NavigatesToConsoleSpace()
    {
        var shell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        Assert.Equal(FluentPage.Library, shell.CurrentPage);

        shell.FindControl<Button>("SpaceConsole")!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.Equal(WorkbenchViewTab.Console, shell.WorkbenchView.ActiveTab);
        Assert.Contains("selected", shell.FindControl<Button>("SpaceConsole")!.Classes);
    }

    [AvaloniaFact]
    public async Task I12_WorkbenchErrorCard_ConsoleEntry_NavigatesToConsoleSpace()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        Dispatcher.UIThread.RunJobs();

        // LoadPageRegionsAsync has no projection for page-1 → the workbench surfaces the error card.
        Assert.Equal(FluentPageState.Error, shell.WorkbenchViewModel.State);
        var entry = FindButton(shell.WorkbenchView, "打开控制台");
        Assert.NotNull(entry);

        entry!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(WorkbenchViewTab.Console, shell.WorkbenchView.ActiveTab);
        Assert.Contains("selected", shell.FindControl<Button>("SpaceConsole")!.Classes);
    }

    [AvaloniaFact]
    public async Task I12_ShelfErrorCard_ConsoleEntry_NavigatesToConsoleSpace()
    {
        var host = new FakeHostController(FakeHostController.FailureSnapshot());
        var shell = CreateShell(host);
        await shell.ShelfViewModel.RefreshAsync();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.Error, shell.ShelfViewModel.State);
        var entry = FindButton(shell.ShelfView, "打开控制台");
        Assert.NotNull(entry);

        entry!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.Equal(WorkbenchViewTab.Console, shell.WorkbenchView.ActiveTab);
    }

    [AvaloniaFact]
    public void I12_ConsolePlaceholder_KeepsHonestNoDataCopy()
    {
        var shell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        shell.Navigate("console");
        Dispatcher.UIThread.RunJobs();

        var content = Assert.IsType<StackPanel>(shell.WorkbenchView.CurrentViewContent);
        Assert.Contains(content.GetVisualDescendants().OfType<TextBlock>(),
            block => block.Text?.Contains("端口尚未接入", StringComparison.Ordinal) == true);
    }

    // ---------------------------------------------------------------- I-14：源不可用警示本体

    [AvaloniaFact]
    public async Task I14_SourceUnavailable_ShowsWarningBannerWithDisabledRecovery()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "fit-page",
            [new ReaderPageData("page-1", 0, 1, 1, LoadImageAsync: null)]);
        var shell = CreateShell(host);
        await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.ReaderViewModel.IsSourceUnavailable);
        var banner = shell.ReaderView.GetVisualDescendants().OfType<AlertBanner>()
            .FirstOrDefault(banner => banner.Title == "源文件不可用");
        Assert.NotNull(banner);
        Assert.Contains("不会写入不可用页", banner.Message, StringComparison.Ordinal);
        var recover = FindButton(shell.ReaderView, "恢复源文件");
        Assert.NotNull(recover);
        Assert.False(recover!.IsEnabled);
    }

    [AvaloniaFact]
    public async Task I14_SourceAvailable_HidesWarningBanner()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "fit-page",
            [new ReaderPageData("page-1", 0, 1, 1, _ => Task.FromResult<byte[]?>(TinyPng))]);
        var shell = CreateShell(host);
        await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();

        Assert.False(shell.ReaderViewModel.IsSourceUnavailable);
        Assert.DoesNotContain(shell.ReaderView.GetVisualDescendants().OfType<AlertBanner>(),
            banner => banner.Title == "源文件不可用");
    }

    // ---------------------------------------------------------------- I-9：未保存圆点

    [AvaloniaFact]
    public void I9_SettingsDirtyDot_VisibleOnlyWhenDirty_AndSurvivesPageRoundTrip()
    {
        var appearance = new AppearanceCoordinator(
            new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        appearance.Reload();
        var shell = CreateShell(appearance: appearance);
        shell.Navigate(FluentPage.Settings);
        Dispatcher.UIThread.RunJobs();
        var settings = shell.SettingsViewModel;

        Assert.False(settings.IsDirty);
        Assert.All(shell.SettingsView.GetVisualDescendants().OfType<Avalonia.Controls.Shapes.Ellipse>(), dot => Assert.False(dot.IsVisible));

        settings.UpdateDraft(settings.Draft with { MotionMode = MotionMode.Reduce });
        Dispatcher.UIThread.RunJobs();
        Assert.True(settings.IsDirty);
        Assert.Contains(shell.SettingsView.GetVisualDescendants().OfType<Avalonia.Controls.Shapes.Ellipse>(), dot => dot.IsVisible);

        // 切页往返（同一运行期 UI memento 语义）：圆点状态仍由 dirty 决定。
        shell.Navigate(FluentPage.Library);
        shell.Navigate(FluentPage.Settings);
        Dispatcher.UIThread.RunJobs();
        Assert.True(settings.IsDirty);
        Assert.Contains(shell.SettingsView.GetVisualDescendants().OfType<Avalonia.Controls.Shapes.Ellipse>(), dot => dot.IsVisible);

        settings.UpdateDraft(appearance.Settings);
        Dispatcher.UIThread.RunJobs();
        Assert.False(settings.IsDirty);
        Assert.All(shell.SettingsView.GetVisualDescendants().OfType<Avalonia.Controls.Shapes.Ellipse>(), dot => Assert.False(dot.IsVisible));
    }

    [AvaloniaFact]
    public async Task I9_WorkbenchDirtyDot_VisibleOnlyWithUnsavedDraft()
    {
        var host = CreateHostWithEditableDraft(out var draft);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        Dispatcher.UIThread.RunJobs();
        var workbench = shell.WorkbenchViewModel;

        // LoadAsync 恢复既有 draft 文本 → 干净（无未保存修改）。
        Assert.False(workbench.HasUnsavedDraft);
        Assert.False(shell.WorkbenchView.DirtyDot.IsVisible);
        Assert.False(shell.WorkbenchView.DirtyStatus.IsVisible);

        workbench.DraftText = "修改后的译文";
        Dispatcher.UIThread.RunJobs();
        Assert.True(workbench.HasUnsavedDraft);
        Assert.True(shell.WorkbenchView.DirtyDot.IsVisible);
        Assert.True(shell.WorkbenchView.DirtyStatus.IsVisible);

        workbench.DraftText = draftTextOf(draft);
        Dispatcher.UIThread.RunJobs();
        Assert.False(workbench.HasUnsavedDraft);
        Assert.False(shell.WorkbenchView.DirtyDot.IsVisible);
    }

    // ---------------------------------------------------------------- I-10：工具条自动隐藏

    [AvaloniaFact]
    public void I10_ToolBars_AutoHideAfterIdle_WakeByInteraction_TwoSecondWindow()
    {
        var shell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();

        // 2s 空闲窗口（07:23）：interval 固定 2s；到期隐藏；交互唤醒。
        Assert.Equal(TimeSpan.FromSeconds(2), shell.ReaderView.AutoHideTimerInterval);
        Assert.True(shell.ReaderViewModel.AreToolBarsVisible);
        Assert.True(shell.ReaderView.TopBar.IsVisible);
        Assert.True(shell.ReaderView.BottomBar.IsVisible);

        shell.ReaderViewModel.AreToolBarsReducedMotion = true; // This case verifies the instant reduce path.
        shell.ReaderViewModel.HideToolBarsAfterIdle();
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ReaderViewModel.AreToolBarsVisible);
        Assert.False(shell.ReaderView.TopBar.IsVisible);
        Assert.False(shell.ReaderView.BottomBar.IsVisible);

        shell.ReaderViewModel.PokeToolBars();
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ReaderViewModel.AreToolBarsVisible);
        Assert.True(shell.ReaderView.TopBar.IsVisible);
    }

    [AvaloniaFact]
    public async Task I10_ToolBars_TapCenterToggles_EdgeBandDoesNot()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData(
            "book-1", "Sample", "chapter-key", "第 1 章", "fit-page",
            [new ReaderPageData("page-1", 0, 1, 1, _ => Task.FromResult<byte[]?>(TinyPng))]);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Reader);
        await shell.ReaderViewModel.LoadAsync("book-1", "chapter-key");
        Dispatcher.UIThread.RunJobs();
        var surface = shell.ReaderView.PageSurface;
        Assert.True(surface.IsVisible);
        surface.Width = 800;
        surface.Height = 600;
        surface.Measure(new Size(800, 600));
        surface.Arrange(new Rect(0, 0, 800, 600));
        Assert.True(surface.Bounds.Height > 0, "reader surface must be laid out for the tap-band test");

        var visibleBefore = shell.ReaderViewModel.AreToolBarsVisible;
        Assert.False(shell.ReaderView.HandleReadingAreaTap(new Point(surface.Bounds.Width / 2, surface.Bounds.Height * 0.05)));
        Assert.Equal(visibleBefore, shell.ReaderViewModel.AreToolBarsVisible);

        Assert.True(shell.ReaderView.HandleReadingAreaTap(new Point(surface.Bounds.Width / 2, surface.Bounds.Height / 2)));
        Assert.NotEqual(visibleBefore, shell.ReaderViewModel.AreToolBarsVisible);
    }

    [AvaloniaFact]
    public void I10_ToolBars_ReducedMotion_SwitchesDirectlyWithoutFade()
    {
        var shell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();

        var clock = new ManualFluentMotionClock();
        shell.ReaderView.ConfigureMotion(MotionTimings.Resolve(new MotionSettings(MotionMode.Full, true, true, true, true)), clock);
        // Full: assert real opacity interpolation, rather than a transition descriptor.
        shell.ReaderViewModel.AreToolBarsReducedMotion = false;
        shell.ReaderViewModel.HideToolBarsAfterIdle();
        clock.Advance(80);
        Assert.True(shell.ReaderView.TopBar.IsVisible);
        Assert.InRange(shell.ReaderView.TopBar.Opacity, .000001, .999999);

        // reduce：直接切换（07:23），无过渡。
        shell.ReaderViewModel.AreToolBarsReducedMotion = true;
        Dispatcher.UIThread.RunJobs();
        Assert.Null(shell.ReaderView.TopBar.Transitions);
        Assert.Null(shell.ReaderView.BottomBar.Transitions);
        Assert.False(shell.ReaderView.TopBar.IsVisible);
        Assert.Equal(0, shell.ReaderView.TopBar.Opacity);
    }

    [AvaloniaFact]
    public void I10_SideRail_AlwaysVisibleByDefault_HideableAndRestorable_IgnorsIdleHide()
    {
        var shell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.ReaderViewModel.IsSideRailVisible);
        Assert.True(shell.ReaderView.SideRail.IsVisible);

        // 2s 空闲隐藏只作用于顶部/底部条；右侧浮动条常显（07:62）。
        shell.ReaderViewModel.AreToolBarsReducedMotion = true;
        shell.ReaderViewModel.HideToolBarsAfterIdle();
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ReaderView.TopBar.IsVisible);
        Assert.True(shell.ReaderView.SideRail.IsVisible);

        // 显式隐藏后右缘保留恢复入口。
        shell.ReaderViewModel.ToggleSideRail();
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ReaderViewModel.IsSideRailVisible);
        Assert.False(shell.ReaderView.SideRail.IsVisible);
        Assert.Contains(shell.ReaderView.GetVisualDescendants().OfType<Button>(),
            button => button.Content?.ToString() == "显示浮动工具条");

        shell.ReaderViewModel.ToggleSideRail();
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ReaderView.SideRail.IsVisible);
    }

    [AvaloniaFact]
    public void I10_FullScreenToggle_WakesToolBars()
    {
        var shell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();
        shell.ReaderViewModel.HideToolBarsAfterIdle();
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ReaderViewModel.AreToolBarsVisible);

        shell.ReaderViewModel.IsFullScreen = true;
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ReaderViewModel.AreToolBarsVisible);
    }

    // ---------------------------------------------------------------- I-1：UI memento

    [AvaloniaFact]
    public async Task I1_ShelfMemento_CollapseScrollSelection_SurvivePageRoundTrip()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot(Enumerable.Range(1, 20)
            .Select(index => $"Book {index:D2}").ToArray()));
        var shell = CreateShell(host);
        var shelf = shell.ShelfViewModel;
        await shelf.SelectBookAsync(shelf.Books[0]);
        Dispatcher.UIThread.RunJobs();

        shelf.IsDetailPaneCollapsed = true;
        shelf.ListScrollOffset = 120;
        shelf.Search = "Book"; // 触发一次 Render（列表重建）：memento 值不受重建影响。
        Dispatcher.UIThread.RunJobs();

        shell.Navigate(FluentPage.Settings);
        shell.Navigate(FluentPage.Library);
        Dispatcher.UIThread.RunJobs();

        // 三字段（折叠/滚动偏移/选中项）在同一运行期往返后保留；视图级 Offset 恢复需要真实布局
        // （headless 无渲染布局，登记 NOT_RUN），可断言的是 memento 值本身与 Render 不破坏它。
        Assert.True(shelf.IsDetailPaneCollapsed);
        Assert.Equal(120, shelf.ListScrollOffset);
        Assert.Equal(shelf.Books[0].BookId, shelf.SelectedBook?.BookId);
    }

    [AvaloniaFact]
    public async Task I1_WorkbenchMemento_CollapseScrollSelection_SurvivePageRoundTrip()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] =
        [
            new ChapterPageSummary("page-1", "one.png", 0),
            new ChapterPageSummary("page-2", "two.png", 1),
        ];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        host.RegionsByPage["page-2"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        await shell.WorkbenchViewModel.SelectPageAsync("page-2");
        Dispatcher.UIThread.RunJobs();

        shell.WorkbenchViewModel.IsInspectorCollapsed = true;
        shell.WorkbenchViewModel.FilmStripScrollOffset = 48;
        shell.WorkbenchViewModel.IsBatch = true; // 触发 Render（内容重建）：memento 值不受重建影响。
        Dispatcher.UIThread.RunJobs();

        shell.Navigate(FluentPage.Library);
        shell.Navigate(FluentPage.Workbench);
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.WorkbenchViewModel.IsInspectorCollapsed);
        Assert.Equal(48, shell.WorkbenchViewModel.FilmStripScrollOffset);
        Assert.Equal("page-2", shell.WorkbenchViewModel.SelectedPage?.PageId);
    }

    [AvaloniaFact]
    public async Task I1_Memento_SurvivesFrontendSwitchRoundTrip_InStableWindow()
    {
        var application = Avalonia.Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = new AppearanceCoordinator(
            new AppearanceStore(Path.Combine(_root, "presentation-settings.json")));
        appearance.Reload();
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null);
        var window = App.CreatePresentationShell(options, NullHostController.Instance, selection, appearance,
            new ThemeHomePaths(
                SettingsFilePath: Path.Combine(_root, "theme-home", "theme-settings.json"),
                ThemesDirectory: Path.Combine(_root, "theme-home", "themes"),
                FavoritesFilePath: Path.Combine(_root, "theme-home", "theme-studio-favorites.json"),
                IsCustom: true),
            themeManager, application);
        var presentation = Assert.IsType<NewManga.App.Views.Presentation.PresentationWindow>(window);
        try
        {
            presentation.Show();
            var fluent = Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);
            var shelf = fluent.ShelfViewModel;
            shelf.IsDetailPaneCollapsed = true;
            shelf.ListScrollOffset = 64;
            var workbench = fluent.WorkbenchViewModel;
            workbench.IsInspectorCollapsed = true;
            workbench.FilmStripScrollOffset = 32;

            var toV2 = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(toV2.Succeeded, toV2.Failure);
            var toFluent = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
            Assert.True(toFluent.Succeeded, toFluent.Failure);
            var back = Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);
            Assert.Same(fluent, back);

            // FEA-07 缓存树复用：同一运行期 UI memento 三字段在 frontend 切换往返后保留。
            Assert.True(back.ShelfViewModel.IsDetailPaneCollapsed);
            Assert.Equal(64, back.ShelfViewModel.ListScrollOffset);
            Assert.True(back.WorkbenchViewModel.IsInspectorCollapsed);
            Assert.Equal(32, back.WorkbenchViewModel.FilmStripScrollOffset);
        }
        finally
        {
            presentation.Close();
        }
    }

    [AvaloniaFact]
    public void I1_NewShellStartsWithMementoDefaults_AndWritesNoDataFiles()
    {
        var filesBefore = Directory.GetFiles(_root, "*", SearchOption.AllDirectories);
        var shell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        {
            Assert.False(shell.ShelfViewModel.IsDetailPaneCollapsed);
            Assert.Equal(0, shell.ShelfViewModel.ListScrollOffset);
            Assert.Null(shell.ShelfViewModel.SelectedBook);
            Assert.False(shell.WorkbenchViewModel.IsInspectorCollapsed);
            Assert.Equal(0, shell.WorkbenchViewModel.FilmStripScrollOffset);

            shell.Navigate(FluentPage.Settings);
            shell.Navigate(FluentPage.Library);
            shell.Navigate(FluentPage.Workbench);
            shell.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();
        }

        // UI memento 不落盘：页面往返不写任何数据文件（appearance 未注入时无写入面）。
        var filesAfter = Directory.GetFiles(_root, "*", SearchOption.AllDirectories);
        Assert.Equal(filesBefore, filesAfter);
    }

    // ---------------------------------------------------------------- I-2：分栏折叠

    [AvaloniaFact]
    public async Task I2_ShelfDetailPane_CollapseByClickAndKeyboard_KeepsConstraints()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Book A"));
        var shell = CreateShell(host);
        var shelf = shell.ShelfViewModel;
        await shelf.SelectBookAsync(shelf.Books[0]);
        Dispatcher.UIThread.RunJobs();
        var details = shell.ShelfView.DetailPane;
        var toggle = shell.ShelfView.DetailPaneToggle;

        Assert.True(details.IsVisible);
        Assert.Equal(320, details.Width);
        Assert.Equal(240, details.MinWidth);
        Assert.Equal(480, details.MaxWidth);
        Assert.True(toggle.IsVisible);
        Assert.True(toggle.Focusable);

        toggle.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shelf.IsDetailPaneCollapsed);
        Assert.False(details.IsVisible); // Auto 列宽 0 → 列表占满
        Assert.Equal("展开详情栏", toggle.Content);

        // 键盘可达：Enter 在折叠按钮上触发展开（Button 类键盘激活路径）。
        toggle.RaiseEvent(new KeyEventArgs { Key = Key.Enter, RoutedEvent = InputElement.KeyDownEvent });
        Dispatcher.UIThread.RunJobs();
        Assert.False(shelf.IsDetailPaneCollapsed);
        Assert.True(details.IsVisible);

        toggle.Focus();
        toggle.RaiseEvent(new KeyEventArgs { Key = Key.Space, RoutedEvent = InputElement.KeyDownEvent });
        toggle.RaiseEvent(new KeyEventArgs { Key = Key.Space, RoutedEvent = InputElement.KeyUpEvent });
        Dispatcher.UIThread.RunJobs();
        Assert.True(shelf.IsDetailPaneCollapsed);
    }

    [AvaloniaFact]
    public async Task I2_WorkbenchInspector_CollapseByClickAndKeyboard_KeepsConstraints()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        Dispatcher.UIThread.RunJobs();
        var pane = shell.WorkbenchView.InspectorPane;
        var toggle = shell.WorkbenchView.InspectorToggle;

        Assert.True(pane.IsVisible);
        Assert.Equal(320, pane.Width);
        Assert.Equal(240, pane.MinWidth);
        Assert.Equal(480, pane.MaxWidth);

        toggle.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.WorkbenchViewModel.IsInspectorCollapsed);
        Assert.False(pane.IsVisible);
        Assert.Equal("展开检查器", toggle.Content);

        toggle.RaiseEvent(new KeyEventArgs { Key = Key.Enter, RoutedEvent = InputElement.KeyDownEvent });
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.WorkbenchViewModel.IsInspectorCollapsed);
        Assert.True(pane.IsVisible);
    }

    // ---------------------------------------------------------------- I-13：9 行状态视觉骨架

    [AvaloniaFact]
    public async Task I13_WorkbenchNineRowSkeleton_DataFreeRowsHaveHonestVisuals()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection([], null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        Dispatcher.UIThread.RunJobs();

        // 行 1（空·未选章节）：无章节时画布空态。
        var emptyShell = CreateShell(new FakeHostController(FakeHostController.ReadySnapshot()));
        emptyShell.Navigate(FluentPage.Workbench);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(FluentPageState.Empty, emptyShell.WorkbenchViewModel.State);
        Assert.Contains(emptyShell.WorkbenchView.GetVisualDescendants().OfType<EmptyState>(),
            empty => empty.Title == "未选章节");
        emptyShell.Close();

        // 行 2（空·批量无 Run）：批量空态卡 + 禁用「开始处理」占位（动作归 B-2）。
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Batch);
        Dispatcher.UIThread.RunJobs();
        var batchContent = shell.WorkbenchView.CurrentViewContent!;
        Assert.Contains(batchContent.GetVisualDescendants().OfType<EmptyState>(),
            empty => empty.Title == "没有正在处理的批量任务");
        var start = FindButton(shell.WorkbenchView, "开始处理");
        Assert.NotNull(start);
        Assert.False(start!.IsEnabled);

        // 行 9（运行中·控制台）：Run 控制禁用占位（数据归 B-2）。
        shell.WorkbenchView.SelectTab(WorkbenchViewTab.Console);
        Dispatcher.UIThread.RunJobs();
        Assert.False(FindButton(shell.WorkbenchView, "暂停")!.IsEnabled);
        Assert.False(FindButton(shell.WorkbenchView, "停止")!.IsEnabled);
    }

    [AvaloniaFact]
    public async Task I13_WorkbenchErrorRow_ErrorCardWithRetryAndConsoleEntry()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.Error, shell.WorkbenchViewModel.State);
        var banner = shell.WorkbenchView.GetVisualDescendants().OfType<AlertBanner>()
            .FirstOrDefault(banner => banner.Title == "工作台错误");
        Assert.NotNull(banner);
        Assert.NotNull(FindButton(shell.WorkbenchView, "打开控制台"));
    }

    [AvaloniaFact]
    public async Task I13_WorkbenchConflictRow_ConflictBannerShowsWithoutFabricatedCompare()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection(
        [
            new RegionSummary("region-1", "speech", "skip", "detect", 1,
                new RegionGeometrySummary(0.1, 0.1, 0.3, 0.2, [])),
        ], new RegionPageSize(100, 100));
        // lease 不可编辑 → Conflict 态（B-7 的「查看对照」不在此批）。
        host.DraftLeasesByPageRegion["page-1|region-1"] =
            new DraftLease(CreateDraft("draft-1", "page-1", "region-1", "draft text"), CanEdit: false, Token: null);
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        await shell.WorkbenchViewModel.SelectRegionAsync(shell.WorkbenchViewModel.Regions[0]);
        Dispatcher.UIThread.RunJobs();

        // Host 返回不可编辑 lease → 显式开草稿被拒 → 冲突条（B-7 的「查看对照」不在此批）。
        Assert.False(await shell.WorkbenchViewModel.OpenDraftAsync(1));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(FluentPageState.Conflict, shell.WorkbenchViewModel.State);
        var banner = shell.WorkbenchView.GetVisualDescendants().OfType<AlertBanner>()
            .FirstOrDefault(banner => banner.Title == "并发冲突");
        Assert.NotNull(banner);
        Assert.DoesNotContain(shell.WorkbenchView.GetVisualDescendants().OfType<Button>(),
            button => button.Content?.ToString()?.Contains("查看对照", StringComparison.Ordinal) == true);
    }

    [AvaloniaFact]
    public async Task I13_WorkbenchReadOnlyRow_InspectorDisabledWithWarning()
    {
        var host = new FakeHostController(FakeHostController.ReadOnlySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection(
        [
            new RegionSummary("region-1", "speech", "skip", "detect", 1,
                new RegionGeometrySummary(0.1, 0.1, 0.3, 0.2, [])),
        ], new RegionPageSize(100, 100));
        var shell = CreateShell(host);
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        await shell.WorkbenchViewModel.SelectRegionAsync(shell.WorkbenchViewModel.Regions[0]);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.ReadOnly, shell.WorkbenchViewModel.State);
        var banner = shell.WorkbenchView.GetVisualDescendants().OfType<AlertBanner>()
            .FirstOrDefault(banner => banner.Title == "只读模式");
        Assert.NotNull(banner);
        Assert.All(shell.WorkbenchView.GetVisualDescendants().OfType<Button>().Where(
            button => button.Content?.ToString() is "开启草稿" or "写入恢复日志" or "丢弃草稿"),
            button => Assert.False(button.IsEnabled));
    }

    // ---------------------------------------------------------------- helpers

    private static FakeHostController CreateHostWithEditableDraft(out Draft draft)
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection(
        [
            new RegionSummary("region-1", "speech", "skip", "detect", 1,
                new RegionGeometrySummary(0.1, 0.1, 0.3, 0.2, [])),
        ], new RegionPageSize(100, 100));
        host.RevisionsByRegion["region-1"] = new RegionRevisionHistory("region-1", 1,
        [
            new RegionRevisionSummary("rev-1", 1, "detect", "reviewed", IsPinned: false,
                RestoredFromRevisionId: null, CreatedAt: "2026-11-02T00:00:00Z", RegionType: "speech",
                SfxPolicy: "skip", IsCurrent: true),
        ]);
        draft = CreateDraft("draft-1", "page-1", "region-1", "draft text");
        host.ScriptedDrafts = [draft];
        host.DraftLeasesByPageRegion["page-1|region-1"] =
            new DraftLease(draft, CanEdit: true,
            Token: new EditToken("token-1", "draft-1", DraftSequence: 1, SessionId: "session-1",
                IssuedAt: "2026-11-02T00:00:00Z", ExpiresAt: "2026-11-03T00:00:00Z"));
        return host;
    }

    private static Draft CreateDraft(string draftId, string pageId, string regionId, string text) => new(
        draftId, "session-1", pageId, regionId, "rev-1", PageBindingVersion: 1, DraftSequence: 1,
        Patch: JsonSerializer.SerializeToElement(new { text }), UndoCursor: null,
        SavedAt: "2026-11-02T00:00:00Z", Status: "open");

    private static string draftTextOf(Draft draft) =>
        draft.Patch?.TryGetProperty("text", out var text) == true ? text.GetString() ?? string.Empty : string.Empty;
}
