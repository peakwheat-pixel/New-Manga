using Avalonia.Automation;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.CoreClient;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Controls;

namespace NewManga.App.Tests;

/// <summary>FEA-06 page-state, shell accessibility, motion and rendered screenshot evidence.</summary>
public sealed class FluentPageTests
{
    [AvaloniaFact]
    public void ShelfPage_EmptyHostFailure_LeavesRetrySurfaceAndNavigationAvailable()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.Error, shell.ShelfViewModel.State);
        Assert.Equal(FluentPage.Library, shell.CurrentPage);
        Assert.NotNull(shell.NavigationButton(FluentPage.Workbench));
        shell.Close();
    }

    [AvaloniaFact]
    public void WorkbenchPage_UnselectedState_OffersReturnToShelf()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        shell.Navigate(FluentPage.Workbench);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.Empty, shell.WorkbenchViewModel.State);
        var workbench = Assert.IsType<WorkbenchPageView>(shell.FindControl<ContentControl>("FluentPageHost")!.Content);
        Assert.NotNull(workbench.RegionCanvas);
        AssertWorkbenchTabSelection(workbench, 0);

        workbench.ViewTabs.Children[1].RaiseEvent(
            new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(WorkbenchViewTab.Batch, workbench.ActiveTab);
        AssertWorkbenchTabSelection(workbench, 1);

        workbench.ViewTabs.Children[2].RaiseEvent(
            new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(WorkbenchViewTab.Console, workbench.ActiveTab);
        AssertWorkbenchTabSelection(workbench, 2);
        shell.Close();
    }

    private static void AssertWorkbenchTabSelection(WorkbenchPageView workbench, int selectedIndex)
    {
        var tabs = workbench.ViewTabs.Children.OfType<Button>().ToArray();
        Assert.Equal(3, tabs.Length);
        for (var index = 0; index < tabs.Length; index++)
        {
            Assert.Equal(index == selectedIndex, tabs[index].Classes.Contains("selected"));
        }

        Assert.Equal(TokenColor("Nm.Color.Accent.Muted"),
            Assert.IsAssignableFrom<ISolidColorBrush>(tabs[selectedIndex].Background).Color);
        Assert.Equal(TokenColor("Nm.Color.Text.Primary"),
            Assert.IsAssignableFrom<ISolidColorBrush>(tabs[selectedIndex].Foreground).Color);
        Assert.Equal(TokenColor("Nm.Color.Accent.Base"),
            Assert.IsAssignableFrom<ISolidColorBrush>(tabs[selectedIndex].BorderBrush).Color);
        Assert.True(Avalonia.Application.Current!.TryGetResource("Nm.Corner.Fluent.Sm", null, out var radius));
        Assert.Equal(Assert.IsType<CornerRadius>(radius), tabs[selectedIndex].CornerRadius);
    }

    private static Color TokenColor(string key)
    {
        Assert.True(Avalonia.Application.Current!.TryGetResource(key, null, out var value), key);
        return Assert.IsAssignableFrom<ISolidColorBrush>(value).Color;
    }

    [AvaloniaFact]
    public async Task ReaderPage_HostUnavailable_ShowsRecoverableErrorState()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        await shell.ReaderViewModel.LoadAsync(null, null);
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.Error, shell.ReaderViewModel.State);
        Assert.IsType<ReaderPageView>(shell.FindControl<ContentControl>("FluentPageHost")!.Content);
        shell.Close();
    }

    [AvaloniaFact]
    public async Task SettingsPage_HostUnavailable_IsBrowsableButReadOnly()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        await shell.SettingsViewModel.LoadAsync();
        shell.Navigate(FluentPage.Settings);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPageState.ReadOnly, shell.SettingsViewModel.State);
        Assert.True(shell.SettingsViewModel.IsReadOnly);
        Assert.IsType<SettingsPageView>(shell.FindControl<ContentControl>("FluentPageHost")!.Content);
        shell.Close();
    }

    [AvaloniaFact]
    public void FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentResponsiveBand.Narrow, FluentShell.GetResponsiveBand(900));
        Assert.Equal(FluentResponsiveBand.Medium, FluentShell.GetResponsiveBand(1180));
        Assert.Equal(FluentResponsiveBand.Compact, FluentShell.GetResponsiveBand(1400));
        Assert.Equal(FluentResponsiveBand.Full, FluentShell.GetResponsiveBand(1600));
        Assert.Contains("Medium", shell.StatusText, StringComparison.Ordinal);
        Assert.Equal("Medium · 1024–1279", shell.FindControl<TextBlock>("FluentBreakpointText")!.Text);
        Assert.Equal("导航到书架", AutomationProperties.GetName(shell.NavigationButton(FluentPage.Library)!));
        Assert.Equal(17, shell.ShellKeyMap.Definitions.Count(command => command.HasGesture));

        Assert.True(shell.HandleKeyForTest(Key.D2, KeyModifiers.Control));
        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.True(shell.HandleKeyForTest(Key.Tab, KeyModifiers.None));
        Assert.True(shell.WorkbenchViewModel.IsBatch);
        Assert.False(shell.HandleKeyForTest(Key.J, KeyModifiers.None, textInputFocused: true));
        shell.Close();
    }

    [AvaloniaFact]
    public void Shelf_WiresSegmentedViewModeAndChapterList()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.IsType<SegmentedControl>(shell.ShelfView.ViewModeControl);
        Assert.IsType<ChapterList>(shell.ShelfView.ChapterDetails);
        var options = Assert.IsType<StackPanel>(shell.ShelfView.ViewModeControl.Child).Children.OfType<Button>().ToArray();
        Assert.Equal(2, options.Length);
        options[1].RaiseEvent(new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
        Assert.False(shell.ShelfView.ViewModel.IsGrid);
        Assert.Equal(1, shell.ShelfView.ViewModeControl.SelectedIndex);

        shell.Close();
    }

    [AvaloniaFact]
    public void ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.HandleKeyForTest(Key.D3, KeyModifiers.Control));
        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.Equal(WorkbenchViewTab.Console, shell.WorkbenchView.ActiveTab);
        Assert.Equal(3, shell.WorkbenchView.ViewTabs.Children.Count);
        // FEA-06-RESIDUAL-3（改写，原为本索引断言 consoleContent.Children[1]）：改为按类型 +
        // AutomationProperties.Name 定位 Run 投影条，并保留"无假数据"不变量（空态诚实、无推测进度）。
        var consoleContent = Assert.IsType<StackPanel>(shell.WorkbenchView.CurrentViewContent);
        var runBar = consoleContent.GetVisualDescendants().OfType<RunProjectionBar>()
            .FirstOrDefault(bar => AutomationProperties.GetName(bar) == "控制台 Run 投影条");
        Assert.NotNull(runBar);
        Assert.Equal("当前没有运行中的任务", Assert.IsType<TextBlock>(runBar!.Child).Text);
        Assert.DoesNotContain("%", Assert.IsType<TextBlock>(runBar.Child).Text, StringComparison.Ordinal);
        Assert.True(shell.FindControl<Button>("NavSettings")!.IsVisible);

        shell.FindControl<Button>("SettingsCommandButton")!.RaiseEvent(
            new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        Assert.True(shell.FindControl<Button>("NavSettings")!.IsVisible);
        Assert.Contains("selected", shell.FindControl<Button>("SpaceConsole")!.Classes);

        shell.Close();
    }

    [AvaloniaFact]
    public async Task WorkbenchPageShortcutsMoveThroughExistingPageSelection()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] =
        [
            new ChapterPageSummary("page-1", "one.png", 0),
            new ChapterPageSummary("page-2", "two.png", 1),
        ];
        var shell = FluentShell.CreateRoot(host: host);
        shell.Show();
        shell.Navigate(FluentPage.Workbench);
        await shell.WorkbenchView.LoadAsync("chapter-key");
        Dispatcher.UIThread.RunJobs();

        Assert.Equal("page-1", shell.WorkbenchViewModel.SelectedPage?.PageId);
        Assert.True(shell.HandleKeyForTest(Key.OemCloseBrackets, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal("page-2", shell.WorkbenchViewModel.SelectedPage?.PageId);
        Assert.True(shell.HandleKeyForTest(Key.OemOpenBrackets, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal("page-1", shell.WorkbenchViewModel.SelectedPage?.PageId);

        shell.Close();
    }

    [AvaloniaFact]
    public void FluentShell_NavigationFollowsSpaceAndReaderRemainsAnOverlay()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.FindControl<Button>("NavLibrary")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavRecycle")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavImport")!.IsVisible);
        Assert.False(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavSettings")!.IsVisible);

        shell.Navigate(FluentPage.Workbench);
        Assert.False(shell.FindControl<Button>("NavLibrary")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavSettings")!.IsVisible);

        shell.Navigate(FluentPage.Reader);
        Assert.Equal(FluentPage.Reader, shell.CurrentPage);
        Assert.True(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.IsType<ReaderPageView>(shell.FindControl<ContentControl>("FluentPageHost")!.Content);

        shell.Navigate(FluentPage.Settings);
        Assert.False(shell.FindControl<Button>("NavLibrary")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavSettings")!.IsVisible);
        shell.Close();
    }

    /// <summary>
    /// FEA-06-RESIDUAL-1 I-7 (scope-r3 R3-002): default run renders every page and asserts the captured
    /// frame shape without writing any repository/evidence PNG. Explicit opt-in
    /// (`NEWMANGA_CAPTURE_FLUENT_PNGS=1`) writes to this task's evidence directory only; the pinned
    /// `verification/FEA-06/screens/**` bytes are never touched.
    /// </summary>
    [AvaloniaFact]
    public async Task FluentPages_RenderHeadlessPngEvidence()
    {
        var repositoryRoot = RepositoryRoot();
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga"));
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(
            repositoryRoot, "verification", "FEA-06", "runtime", AppearanceStore.FileName)));
        appearance.Reload();
        var shell = FluentShell.CreateRoot(
            selection: FrontendSelector.Select("builtin.fluent", null),
            host: host,
            appearance: appearance);
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        var frames = new List<(string Name, Bitmap Frame)>
        {
            ("shelf", Capture(shell, FluentPage.Library)),
            ("workbench", Capture(shell, FluentPage.Workbench)),
        };
        await shell.ReaderViewModel.LoadAsync("book-0", "chapter-0");
        frames.Add(("reader", Capture(shell, FluentPage.Reader)));
        await shell.SettingsViewModel.LoadAsync();
        frames.Add(("settings", Capture(shell, FluentPage.Settings)));

        Assert.All(frames, item => Assert.True(item.Frame.PixelSize.Width > 0 && item.Frame.PixelSize.Height > 0,
            $"empty rendered frame: {item.Name}"));

        var captureEnabled = string.Equals(
            Environment.GetEnvironmentVariable("NEWMANGA_CAPTURE_FLUENT_PNGS"),
            "1",
            StringComparison.OrdinalIgnoreCase);
        if (captureEnabled)
        {
            var output = Path.Combine(repositoryRoot, "verification", "FEA-06-RESIDUAL-1", "png");
            Directory.CreateDirectory(output);
            Assert.DoesNotContain(Path.Combine("verification", "FEA-06", "screens"), output, StringComparison.OrdinalIgnoreCase);
            foreach (var (name, frame) in frames)
            {
                frame.Save(Path.Combine(output, $"{name}.png"));
            }

            Assert.All(frames, item => Assert.True(
                new FileInfo(Path.Combine(output, item.Name + ".png")).Length > 0,
                $"missing screenshot: {item.Name}"));
        }

        shell.Close();
    }

    private static Bitmap Capture(FluentShell shell, FluentPage page)
    {
        shell.Navigate(page);
        Dispatcher.UIThread.RunJobs();
        return shell.CaptureRenderedFrame() ?? throw new InvalidOperationException($"frame capture failed: {page}");
    }

    private static void Save(FluentShell shell, FluentPage page, string path)
    {
        shell.Navigate(page);
        Dispatcher.UIThread.RunJobs();
        var frame = shell.CaptureRenderedFrame() ?? throw new InvalidOperationException($"frame capture failed: {page}");
        frame.Save(path);
    }

    private static string RepositoryRoot()
    {
        var cursor = new DirectoryInfo(AppContext.BaseDirectory);
        while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc", "tasks", "FEA-06.md")))
        {
            cursor = cursor.Parent;
        }

        return cursor?.FullName ?? throw new DirectoryNotFoundException("could not locate the New Manga repository root");
    }
}
