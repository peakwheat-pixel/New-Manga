using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>FEA-14-READ-2: the Fluent reader consumes the READ wire (P9/P10/P14/P15).</summary>
public sealed class ReaderReadingPreferencesTests
{
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
        return host;
    }

    [Fact]
    public async Task LoadAppliesStoredPreferencesAndBookProgress()
    {
        var host = HostWithBook();
        host.ReadingPreferences = new ReadingPreferencesInfo(
            "b1", "translated", "rtl", 1.5, true, "double", "2026-01-01", false);
        host.BookProgress = new BookReadingProgressInfo(3, 10, 30.0, false);
        var viewModel = new ReaderViewModel(host);

        await viewModel.LoadAsync("b1", "c1");

        Assert.Equal(1.5, viewModel.Zoom);
        Assert.True(viewModel.DoublePage);
        Assert.True(viewModel.ReverseDirection);
        Assert.Equal("double", viewModel.Layout);
        Assert.True(viewModel.HasBookProgress);
        Assert.Contains("整书进度", viewModel.BookProgressLabel);
    }

    [Fact]
    public async Task SavePreferencesSendsThePartialPatch()
    {
        var host = HostWithBook();
        host.ReadingPreferences = new ReadingPreferencesInfo(
            "b1", "original", "ltr", 1.0, false, "single", "2026-01-01", true);
        var viewModel = new ReaderViewModel(host);
        await viewModel.LoadAsync("b1", "c1");

        viewModel.ZoomBy(1.0);
        await viewModel.SaveReadingPreferencesAsync();

        // R1-001: only the changed field is sent (partial), the rest stay null.
        var patch = host.LastSavedPreferences;
        Assert.NotNull(patch);
        Assert.Equal(2.0, patch!.Zoom);
        Assert.Null(patch.Mode);
        Assert.Null(patch.Direction);
        Assert.Null(patch.DoublePage);
        Assert.Null(patch.Layout);
    }

    [Fact]
    public async Task ResetRequiresExplicitConfirmation()
    {
        var host = HostWithBook();
        var viewModel = new ReaderViewModel(host);
        await viewModel.LoadAsync("b1", "c1");

        await viewModel.ResetReadingProgressAsync(confirm: false);
        Assert.False(host.LastResetConfirmed);

        await viewModel.ResetReadingProgressAsync(confirm: true);
        Assert.True(host.LastResetConfirmed);
    }
    [Fact]
    public async Task BookmarksCreateListDeleteRoundTrip()
    {
        var host = HostWithBook();
        var viewModel = new ReaderViewModel(host);
        await viewModel.LoadAsync("b1", "c1");

        var bookmarkId = await viewModel.CreateBookmarkAsync(side: "left", note: "keep");
        Assert.NotNull(bookmarkId);
        var listed = await viewModel.ListBookmarksAsync();
        Assert.Single(listed);
        Assert.Equal("left", listed[0].Side);

        Assert.True(await viewModel.DeleteBookmarkAsync(bookmarkId!));
        Assert.Empty(await viewModel.ListBookmarksAsync());
    }



    [Fact]
    public async Task ApplyReadingPreferencesAppliesModeAndVerticalDirection()
    {
        var host = HostWithBook();
        host.ReadingPreferences = new ReadingPreferencesInfo(
            "b1", "translated", "vertical", 1.25, false, "single", "2026-01-01", false);
        var viewModel = new ReaderViewModel(host);

        await viewModel.LoadAsync("b1", "c1");

        Assert.Equal("translated", viewModel.Mode);
        Assert.True(viewModel.VerticalDirection);
        Assert.False(viewModel.ReverseDirection);

        await viewModel.SaveReadingPreferencesAsync();
        Assert.Null(host.LastSavedPreferences); // nothing dirty -> no save
    }

}
