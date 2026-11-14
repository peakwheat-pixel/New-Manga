using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// READER-PREF-PERSIST AC4 (view level): the r1 review found that the first version of this card
/// only asserted the VM methods, so reverting <c>ReaderPageView</c> to its broken state kept the
/// suite green (the production wiring had zero coverage). These facts drive the REAL buttons in the
/// REAL view tree, so removing the wiring makes them fail.
/// </summary>
public sealed class ReaderPreferenceWiringTests
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    private static FakeHostController HostWithBook()
    {
        var host = new FakeHostController(new HostViewSnapshot(
            HostViewState.Ready, "ready", "—", null, null, Array.Empty<BookSummary>(), 0, false, null));
        host.ReaderBook = new ReaderBookData(
            "b1", "Book", "c1", "Ch", "single",
            new[]
            {
                new ReaderPageData("p1", 0, 100, 200),
                new ReaderPageData("p2", 1, 100, 200),
            });
        host.ReadingPreferences = new ReadingPreferencesInfo(
            "b1", "original", "ltr", 1.0, false, "single", "2026-01-01", false);
        host.PageImagesByPage["p1"] = Convert.FromBase64String(OnePixelPngBase64);
        host.PageImagesByPage["p2"] = Convert.FromBase64String(OnePixelPngBase64);
        return host;
    }

    private static async Task<(FluentShell Shell, ReaderPageView View)> OpenReaderAsync(FakeHostController host)
    {
        var shell = FluentShell.CreateRoot(host: host);
        shell.Show();
        await shell.ReaderViewModel.LoadAsync("b1", "c1");
        shell.Navigate(FluentPage.Reader);
        Dispatcher.UIThread.RunJobs();
        var view = shell.GetVisualDescendants().OfType<ReaderPageView>().First();
        return (shell, view);
    }

    private static Button FindButton(Control root, string accessibleName) =>
        root.GetVisualDescendants().OfType<Button>()
            .FirstOrDefault(button => AutomationProperties.GetName(button) == accessibleName)
        ?? throw new InvalidOperationException(
            $"button '{accessibleName}' not found; available: " + string.Join(
                " | ", root.GetVisualDescendants().OfType<Button>()
                    .Select(button => AutomationProperties.GetName(button) ?? "(no name)")));

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static async Task SettleAsync(FakeHostController host, int minimum)
    {
        for (var spin = 0; spin < 400 && host.SaveReadingPreferencesCallCount < minimum; spin++)
        {
            await Task.Delay(5);
        }
        // Let the save continuation finish before asserting on VM/snapshot state.
        for (var spin = 0; spin < 20; spin++)
        {
            await Task.Delay(5);
        }
    }

    [AvaloniaFact]
    public async Task ToolbarDoublePageButton_PersistsTheToggle()
    {
        var host = HostWithBook();
        var (shell, view) = await OpenReaderAsync(host);
        try
        {
            Assert.False(shell.ReaderViewModel.DoublePage);

            Click(FindButton(view, "切换单页或双页"));
            await SettleAsync(host, 1);

            Assert.True(shell.ReaderViewModel.DoublePage);
            Assert.NotNull(host.LastSavedPreferences);
            Assert.True(host.LastSavedPreferences!.DoublePage);
        }
        finally
        {
            shell.Close();
        }
    }

    [AvaloniaFact]
    public async Task ToolbarDirectionButton_PersistsTheDirection()
    {
        var host = HostWithBook();
        var (shell, view) = await OpenReaderAsync(host);
        try
        {
            Click(FindButton(view, "切换阅读方向"));
            await SettleAsync(host, 1);

            Assert.True(shell.ReaderViewModel.ReverseDirection);
            Assert.Equal("rtl", host.LastSavedPreferences!.Direction);
        }
        finally
        {
            shell.Close();
        }
    }

    [AvaloniaFact]
    public async Task SideRailZoomButton_PersistsTheZoom()
    {
        var host = HostWithBook();
        var (shell, view) = await OpenReaderAsync(host);
        try
        {
            Click(FindButton(view, "放大页面"));
            await SettleAsync(host, 1);

            Assert.Equal(1.1, shell.ReaderViewModel.Zoom, 3);
            Assert.Equal(1.1, host.LastSavedPreferences!.Zoom!.Value, 3);
        }
        finally
        {
            shell.Close();
        }
    }

    [AvaloniaFact]
    public async Task BottomBarFitPageButton_PersistsTheZoomReset()
    {
        var host = HostWithBook();
        var (shell, view) = await OpenReaderAsync(host);
        try
        {
            Click(FindButton(view, "放大页面"));
            await SettleAsync(host, 1);
            var before = host.SaveReadingPreferencesCallCount;

            Click(FindButton(view, "重置缩放"));
            await SettleAsync(host, before + 1);

            Assert.Equal(1.0, shell.ReaderViewModel.Zoom, 3);
            Assert.Equal(1.0, host.LastSavedPreferences!.Zoom!.Value, 3);
        }
        finally
        {
            shell.Close();
        }
    }
}
