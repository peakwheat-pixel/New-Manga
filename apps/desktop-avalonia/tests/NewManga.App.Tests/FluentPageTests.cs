using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;

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
        Assert.IsType<WorkbenchPageView>(shell.FindControl<ContentControl>("FluentPageHost")!.Content);
        Assert.NotNull(Assert.IsType<WorkbenchPageView>(shell.FindControl<ContentControl>("FluentPageHost")!.Content).RegionCanvas);
        shell.Close();
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

        Assert.Equal(FluentResponsiveBand.Narrow, FluentShell.GetResponsiveBand(1180));
        Assert.Equal(FluentResponsiveBand.Compact, FluentShell.GetResponsiveBand(1400));
        Assert.Equal(FluentResponsiveBand.Full, FluentShell.GetResponsiveBand(1600));
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
    public void FluentShell_NavigationFollowsSpaceAndReaderRemainsAnOverlay()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.FindControl<Button>("NavLibrary")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavRecycle")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavImport")!.IsVisible);
        Assert.False(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.False(shell.FindControl<Button>("NavSettings")!.IsVisible);

        shell.Navigate(FluentPage.Workbench);
        Assert.False(shell.FindControl<Button>("NavLibrary")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.False(shell.FindControl<Button>("NavSettings")!.IsVisible);

        shell.Navigate(FluentPage.Reader);
        Assert.Equal(FluentPage.Reader, shell.CurrentPage);
        Assert.True(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.IsType<ReaderPageView>(shell.FindControl<ContentControl>("FluentPageHost")!.Content);

        shell.Navigate(FluentPage.Settings);
        Assert.False(shell.FindControl<Button>("NavLibrary")!.IsVisible);
        Assert.False(shell.FindControl<Button>("NavWorkbench")!.IsVisible);
        Assert.True(shell.FindControl<Button>("NavSettings")!.IsVisible);
        shell.Close();
    }

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
        var output = Path.Combine(repositoryRoot, "verification", "FEA-06", "screens");
        Directory.CreateDirectory(output);

        Save(shell, FluentPage.Library, Path.Combine(output, "shelf.png"));
        Save(shell, FluentPage.Workbench, Path.Combine(output, "workbench.png"));
        await shell.ReaderViewModel.LoadAsync("book-0", "chapter-0");
        Save(shell, FluentPage.Reader, Path.Combine(output, "reader.png"));
        await shell.SettingsViewModel.LoadAsync();
        Save(shell, FluentPage.Settings, Path.Combine(output, "settings.png"));

        Assert.All(new[] { "shelf.png", "workbench.png", "reader.png", "settings.png" },
            file => Assert.True(new FileInfo(Path.Combine(output, file)).Length > 0, $"missing screenshot: {file}"));
        shell.Close();
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
