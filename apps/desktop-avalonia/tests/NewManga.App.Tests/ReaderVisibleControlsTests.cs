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
/// MAINT-2-C1-BATCH-1 AC1 (C1-1 / L-R2-1): the three READ-2 behaviours that already lived in
/// <see cref="ReaderViewModel"/> now have VISIBLE controls in the Fluent reader — whole-book
/// progress (P14), the bookmark panel (P11/P12/P13) and the reset confirm flow (P15).
///
/// These are user-visible acceptance tests: they drive the real buttons in the real view tree and
/// assert both the surface (control exists / panel visible) and the effect (the Host received the
/// call). A revert of the controls makes them fail — the panel/confirm row never appears.
/// </summary>
public sealed class ReaderVisibleControlsTests
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    [AvaloniaFact]
    public async Task Reader_ShowsWholeBookProgressFromTheHostProjection()
    {
        var host = HostWithBook();
        host.BookProgress = new BookReadingProgressInfo(3, 10, 30.0, false);
        var (shell, view) = await OpenReaderAsync(host);

        Assert.True(view.BookProgressText.IsVisible);
        Assert.Contains("整书进度", view.BookProgressText.Text);
        Assert.Contains("3/10", view.BookProgressText.Text);

        shell.Close();
    }

    [AvaloniaFact]
    public async Task Reader_HidesWholeBookProgressWhenTheHostHasNoProjection()
    {
        var host = HostWithBook();
        host.BookProgress = null;
        var (shell, view) = await OpenReaderAsync(host);

        // No projection => the control stays hidden; never a fabricated percentage.
        Assert.False(view.BookProgressText.IsVisible);
        Assert.Equal(string.Empty, view.BookProgressText.Text);

        shell.Close();
    }

    [AvaloniaFact]
    public async Task Reader_BookmarkPanel_ListsExistingAndAddsAndDeletes()
    {
        var host = HostWithBook();
        host.Bookmarks.Add(new BookmarkInfo("bm-1", "b1", "c1", "p1", null, "标记", "2026-01-01"));
        var (shell, view) = await OpenReaderAsync(host);

        Assert.False(view.BookmarkPanelHost.IsVisible);

        var toggle = FindButton(shell, "书签");
        Click(toggle);
        Dispatcher.UIThread.RunJobs();

        Assert.True(view.BookmarkPanelHost.IsVisible);
        var texts = view.BookmarkPanelHost.GetVisualDescendants().OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty).ToArray();
        Assert.Contains(texts, text => text.Contains("标记", StringComparison.Ordinal));

        // P12：「添加当前页书签」必须真的调用 Host（多一行来自 Host 的记录，不是本地伪造行）。
        Click(FindButtonIn(view.BookmarkPanelHost, "添加当前页书签"));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(2, host.Bookmarks.Count);
        Assert.Equal("p1", host.Bookmarks[^1].PageId);

        // P13：删除行同时删除 Host 侧记录与本地列表。
        var deleteButton = view.BookmarkPanelHost.GetVisualDescendants().OfType<Button>()
            .First(button => AutomationProperties.GetName(button)?.StartsWith("删除书签", StringComparison.Ordinal) == true);
        Click(deleteButton);
        Dispatcher.UIThread.RunJobs();
        Assert.Single(host.Bookmarks);
        var after = view.BookmarkPanelHost.GetVisualDescendants().OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty).ToArray();
        Assert.DoesNotContain(after, text => text.Contains("标记", StringComparison.Ordinal));

        shell.Close();
    }

    [AvaloniaFact]
    public async Task Reader_ResetProgress_RequiresExplicitConfirmation()
    {
        var host = HostWithBook();
        host.BookProgress = new BookReadingProgressInfo(3, 10, 30.0, false);
        var (shell, view) = await OpenReaderAsync(host);

        Assert.False(view.ResetConfirmRow.IsVisible);

        // 只展开确认行不写任何东西：Host 此时仍未收到 reset。
        Click(FindButton(shell, "重置进度"));
        Dispatcher.UIThread.RunJobs();
        Assert.True(view.ResetConfirmRow.IsVisible);
        Assert.False(host.LastResetConfirmed);

        // 取消后状态完全不变。
        Click(FindButton(shell, "取消重置进度"));
        Dispatcher.UIThread.RunJobs();
        Assert.False(view.ResetConfirmRow.IsVisible);
        Assert.False(host.LastResetConfirmed);

        // 只有显式确认才写入 Host（P15 要求 confirm: true）。
        Click(FindButton(shell, "重置进度"));
        Dispatcher.UIThread.RunJobs();
        Click(FindButton(shell, "确认重置进度"));
        Dispatcher.UIThread.RunJobs();
        Assert.True(host.LastResetConfirmed);
        Assert.False(view.ResetConfirmRow.IsVisible);

        shell.Close();
    }

    // ------------------------------------------------------------------ helpers

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
        // ApplyReadingPreferencesAsync 是唯一加载 BookProgress（P14）的路径，必须有偏好投影。
        host.ReadingPreferences = new ReadingPreferencesInfo("b1", "original", "ltr", 1.0, false, "single", "2026-01-01", false);
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
                " | ",
                root.GetVisualDescendants().OfType<Button>()
                    .Select(button => AutomationProperties.GetName(button) ?? "(no name)")));

    private static Button FindButtonIn(Control root, string accessibleName) =>
        root.GetVisualDescendants().OfType<Button>()
            .First(button => AutomationProperties.GetName(button) == accessibleName);

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
}
