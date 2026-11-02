using System.Globalization;
using System.IO;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.Views;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-PREREQ-2 AC3 (P3): the Fluent shell skeleton starts headlessly with the frozen design-04 §1
/// frame (top band / navigation rail / status band, all token-driven) and navigates the four placeholder
/// pages. AC2 (P2): the composition root dispatches the selected frontend to the right shell.
/// </summary>
public sealed class FluentShellTests
{
    [AvaloniaFact]
    public void FluentShell_StartsHeadless_WithTheFourNavigationEntries()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(FluentPage.Library, shell.CurrentPage);
        Assert.Equal(4, FluentShell.Pages.Count);
        Assert.Equal(FluentPage.Library, FluentShell.Pages[0]);
        Assert.Equal(FluentPage.Workbench, FluentShell.Pages[1]);
        Assert.Equal(FluentPage.Reader, FluentShell.Pages[2]);
        Assert.Equal(FluentPage.Settings, FluentShell.Pages[3]);
        Assert.All(FluentShell.Pages, page => Assert.NotNull(shell.NavigationButton(page)));
        Assert.Equal("书架", shell.NavigationButton(FluentPage.Library)!.Content);
        Assert.Equal("工作台", shell.NavigationButton(FluentPage.Workbench)!.Content);
        Assert.Equal("阅读器", shell.NavigationButton(FluentPage.Reader)!.Content);
        Assert.Equal("设置", shell.NavigationButton(FluentPage.Settings)!.Content);

        shell.Close();
    }

    [AvaloniaFact]
    public void FluentShell_NavigatesTheFourPlaceholderPages()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();
        var libraryPlaceholder = shell.CurrentPlaceholderText;
        Assert.Contains("书架", shell.CurrentPageTitle, StringComparison.Ordinal);
        Assert.NotEmpty(shell.StatusText);

        shell.Navigate(FluentPage.Workbench);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.Contains("工作台", shell.CurrentPageTitle, StringComparison.Ordinal);
        Assert.NotEqual(libraryPlaceholder, shell.CurrentPlaceholderText);

        shell.Navigate(FluentPage.Reader);
        Assert.Contains("阅读器", shell.CurrentPageTitle, StringComparison.Ordinal);

        shell.Navigate(FluentPage.Settings);
        Assert.Contains("设置", shell.CurrentPageTitle, StringComparison.Ordinal);

        // The click path and the automation/id path use the same navigation funnel.
        shell.NavigationButton(FluentPage.Library)!.RaiseEvent(new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(FluentPage.Library, shell.CurrentPage);

        shell.Close();
    }

    [AvaloniaFact]
    public void FluentShell_FrameUsesTheFrozenDesignTokens()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        var topBand = shell.FindControl<Border>("FluentTopBand");
        var navRail = shell.FindControl<Border>("FluentNavRail");
        var statusBand = shell.FindControl<Border>("FluentStatusBand");
        Assert.NotNull(topBand);
        Assert.NotNull(navRail);
        Assert.NotNull(statusBand);

        // Design 04 §1: top command band Nm.Size.TopBand, rail Nm.Size.TreeWidth, status Nm.Size.StatusBandPage.
        Assert.Equal(TokenDouble(NmKeys.Size.TopBand), topBand!.Bounds.Height, precision: 3);
        Assert.Equal(TokenDouble(NmKeys.Size.TreeWidth), navRail!.Bounds.Width, precision: 3);
        Assert.Equal(TokenDouble(NmKeys.Size.StatusBandPage), statusBand!.Bounds.Height, precision: 3);

        shell.Close();
    }

    [AvaloniaFact]
    public void FluentShell_StartupPageHookMapsTheProductPages()
    {
        var shell = FluentShell.CreateRoot();
        shell.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.Navigate("settings"));
        Assert.Equal(FluentPage.Settings, shell.CurrentPage);
        Assert.True(shell.Navigate("bookshelf"));
        Assert.Equal(FluentPage.Library, shell.CurrentPage);
        Assert.True(shell.Navigate("studio"));
        Assert.Equal(FluentPage.Workbench, shell.CurrentPage);
        Assert.True(shell.Navigate("reader"));
        Assert.Equal(FluentPage.Reader, shell.CurrentPage);
        Assert.False(shell.Navigate("not-a-page"));
        Assert.Equal(FluentPage.Reader, shell.CurrentPage);

        shell.Close();
    }

    [AvaloniaFact]
    public void CompositionRoot_DispatchesToFluentV2AndLegacyShells()
    {
        var application = Application.Current!;
        using var manager = new DesignSystemThemeManager(application);
        Assert.True(manager.Initialize(NewManga.DesignSystem.Theming.AppearanceMode.Dark), manager.LastError);
        using var temp = new TempRoot();
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var coordinator = new AppearanceCoordinator(new AppearanceStore(Path.Combine(temp.Path, AppearanceStore.FileName)));
        coordinator.Reload();

        var options = AppOptions.Parse(["--theme-home", temp.Path]);
        var themeHome = ThemeHome.Resolve(options);
        var fluent = App.CreateShell(
            options,
            controller,
            FrontendSelector.Select("builtin.fluent", null),
            coordinator,
            themeHome,
            manager,
            application);
        Assert.IsType<FluentShell>(fluent);
        fluent.Close();

        var v2 = App.CreateShell(
            options,
            controller,
            FrontendSelector.Select("builtin.current-v2", null),
            coordinator,
            themeHome,
            manager,
            application);
        Assert.IsType<AppShellV2>(v2.Content);
        v2.Close();

        // --shell=legacy stays the one-release operator rollback and wins over the frontend selection.
        var legacyOptions = AppOptions.Parse(["--shell", "legacy", "--theme-home", temp.Path]);
        var legacy = App.CreateShell(
            legacyOptions,
            controller,
            FrontendSelector.Select("builtin.fluent", null),
            coordinator,
            ThemeHome.Resolve(legacyOptions),
            manager,
            application);
        Assert.IsType<MainWindow>(legacy);
        legacy.Close();
    }

    private static double TokenDouble(string key)
    {
        Assert.True(Application.Current!.TryGetResource(key, null, out var value), $"{key} is not loaded");
        return Assert.IsType<double>(value);
    }

    private sealed class TempRoot : IDisposable
    {
        public TempRoot()
        {
            Path = System.IO.Path.Combine(
                System.IO.Path.GetTempPath(),
                "nm-fluent-shell-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Path);
        }

        public string Path { get; }

        public void Dispose()
        {
            if (Directory.Exists(Path))
            {
                Directory.Delete(Path, recursive: true);
            }
        }
    }
}
