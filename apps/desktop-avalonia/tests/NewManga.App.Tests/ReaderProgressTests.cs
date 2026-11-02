using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Views;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// READER-PROGRESS-1: the reader persists its position through <see cref="IReaderProgressSink"/>
/// (turn / close / reopen), restores it on the next open, keeps books independent, clamps stale
/// positions and degrades with typed results when the host is read-only, absent or failing.
/// </summary>
public sealed class ReaderProgressTests
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    private static byte[] OnePixelPng() => Convert.FromBase64String(OnePixelPngBase64);

    private static ReaderBookData Book(
        string bookId = "book-a",
        string bookTitle = "测试书 A",
        string chapterId = "chapter-1",
        int pages = 8,
        string layout = "rtl")
    {
        var items = Enumerable.Range(0, pages)
            .Select(index => new ReaderPageData(
                $"{chapterId}-page-{index}",
                index,
                1200,
                1660,
                _ => Task.FromResult<byte[]?>(OnePixelPng())))
            .ToList();
        return new ReaderBookData(bookId, bookTitle, chapterId, "第 1 章", layout, items);
    }

    private static FakeHostController Controller(ReaderBookData book)
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot(book.BookTitle))
        {
            ReaderBook = book,
        };
        return controller;
    }

    // ------------------------------------------------------------------
    // AC1: save on turn, restore on reopen
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task TurnPage_PersistsPageThroughController()
    {
        var controller = Controller(Book());
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(Book());

        var applied = await page.GoToPageAsync(2);

        Assert.Equal(2, applied);
        Assert.Equal(2, page.ViewModel.CurrentPageIndex);
        var attempt = Assert.Single(controller.Progress.Attempts);
        Assert.Equal("chapter-1", attempt.ChapterId);
        Assert.Equal("chapter-1-page-2", attempt.PageId);
        Assert.Equal("original", attempt.Mode);
        Assert.Null(attempt.ScrollOffsetY); // paged layout: scroll offset omitted, not sent as junk
        Assert.True(attempt.ElapsedSecondsDelta >= 0);
        Assert.True(page.LastProgressResult!.IsSaved);
        Assert.Equal("chapter-1-page-2", page.LastSavedPageId);
    }

    [AvaloniaFact]
    public async Task CloseAndReopen_RestoresLastPage()
    {
        var controller = Controller(Book());
        var first = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        first.SetViewport(1200, 800, 2.0);
        first.LoadLibrary(Book());
        await first.GoToPageAsync(4);
        await first.FlushProgressAsync();

        // "close the reader, then reopen the same book": a fresh page pulls the projection again and
        // must open on the persisted page (Core start_position=resume semantics).
        var reopenedBook = await controller.LoadReaderBookAsync();
        Assert.NotNull(reopenedBook);
        var second = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        second.SetViewport(1200, 800, 2.0);
        second.LoadLibrary(reopenedBook!);

        Assert.Equal(4, reopenedBook!.InitialPageIndex);
        Assert.Equal("chapter-1-page-4", reopenedBook.SavedPageId);
        Assert.Equal(4, second.ViewModel.CurrentPageIndex);
    }

    [AvaloniaFact]
    public async Task MainWindow_ReaderRestoresPageAfterRelaunch()
    {
        var controller = Controller(Book());
        var first = new MainWindow(controller, new AppOptions());
        await first.EnsureReaderLoadedAsync();
        Assert.NotNull(first.Reader.LibraryBook);
        await first.Reader.GoToPageAsync(5);
        await first.Reader.FlushProgressAsync();
        first.Close();

        // App relaunch: a fresh window with the same durable progress store.
        var second = new MainWindow(controller, new AppOptions());
        await second.EnsureReaderLoadedAsync();
        Assert.NotNull(second.Reader.LibraryBook);
        Assert.Equal(5, second.Reader.ViewModel.CurrentPageIndex);
        Assert.Equal(5, second.Reader.LibraryBook!.InitialPageIndex);
        second.Close();
    }

    // ------------------------------------------------------------------
    // AC2: multi-book independence, clamping, read-only / no-Core
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task Progress_IsIndependentPerBook()
    {
        var controller = Controller(Book());
        var bookA = Book(bookId: "book-a", bookTitle: "书 A", chapterId: "chapter-a");
        var bookB = Book(bookId: "book-b", bookTitle: "书 B", chapterId: "chapter-b");

        var pageA = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        pageA.SetViewport(1200, 800, 2.0);
        controller.ReaderBook = bookA;
        pageA.LoadLibrary(bookA);
        await pageA.GoToPageAsync(3);

        var pageB = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        pageB.SetViewport(1200, 800, 2.0);
        controller.ReaderBook = bookB;
        pageB.LoadLibrary(bookB);
        await pageB.GoToPageAsync(6);

        Assert.Equal("chapter-a-page-3", controller.Progress.TryGet("chapter-a")!.PageId);
        Assert.Equal("chapter-b-page-6", controller.Progress.TryGet("chapter-b")!.PageId);

        controller.ReaderBook = bookA;
        var reopenedA = await controller.LoadReaderBookAsync();
        Assert.Equal(3, reopenedA!.InitialPageIndex);
        controller.ReaderBook = bookB;
        var reopenedB = await controller.LoadReaderBookAsync();
        Assert.Equal(6, reopenedB!.InitialPageIndex);
    }

    [AvaloniaFact]
    public async Task SavedPageOutsideCurrentChapter_FallsBackToFirstPage()
    {
        var controller = Controller(Book());
        var original = Book();
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(original);
        await page.GoToPageAsync(7);
        await page.FlushProgressAsync();

        // Page count shrank: the persisted page id no longer exists in the projection.
        var shrunken = original with
        {
            Pages = original.Pages.Take(3).ToList(),
        };
        controller.ReaderBook = shrunken;
        var reopened = await controller.LoadReaderBookAsync();

        Assert.NotNull(reopened);
        Assert.Equal(0, reopened!.InitialPageIndex);
        Assert.Null(reopened.SavedPageId);
    }

    [AvaloniaFact]
    public async Task PageTurn_IsClampedToPageCount()
    {
        var book = Book(pages: 3);
        var controller = Controller(book);
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(book);

        var applied = await page.GoToPageAsync(99);

        Assert.Equal(2, applied);
        Assert.Equal("chapter-1-page-2", controller.Progress.TryGet("chapter-1")!.PageId);
    }

    [AvaloniaFact]
    public async Task ReadOnlyHost_DoesNotPersist_ButReaderKeepsWorking()
    {
        var controller = Controller(Book());
        controller.ScriptedSaveResults.Enqueue(ReaderProgressSaveResult.ReadOnly());
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(Book());

        var result = await page.GoToPageAsync(1);

        Assert.Equal(1, result);
        Assert.Equal(1, page.ViewModel.CurrentPageIndex);
        Assert.Equal(ReaderProgressSaveStatus.ReadOnly, page.LastProgressResult!.Status);
        Assert.Null(controller.Progress.TryGet("chapter-1")); // nothing was written

        // The UI keeps working and the next turn can persist once the host allows writes.
        await page.TurnPageAsync(1);
        Assert.True(page.LastProgressResult.IsSaved);
        Assert.Equal("chapter-1-page-2", controller.Progress.TryGet("chapter-1")!.PageId);
    }

    [AvaloniaFact]
    public async Task NoCore_ReportsNotReady_WithoutThrowing()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>())
        {
            ProgressSink = NullHostController.Instance,
        };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(Book());

        var result = await page.GoToPageAsync(2);

        Assert.Equal(2, result);
        Assert.Equal(ReaderProgressSaveStatus.NotReady, page.LastProgressResult!.Status);
        Assert.Equal("HOST_NOT_READY", page.LastProgressResult.ErrorCode);
    }

    [AvaloniaFact]
    public async Task SaveFailure_IsTyped_AndNextTurnStillSaves()
    {
        var controller = Controller(Book());
        controller.ScriptedSaveResults.Enqueue(ReaderProgressSaveResult.Failed("INVALID_REQUEST"));
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(Book());

        await page.GoToPageAsync(2);
        Assert.Equal(ReaderProgressSaveStatus.Failed, page.LastProgressResult!.Status);
        Assert.Equal("INVALID_REQUEST", page.LastProgressResult.ErrorCode);
        Assert.Null(controller.Progress.TryGet("chapter-1"));

        await page.TurnPageAsync(1);
        Assert.True(page.LastProgressResult.IsSaved);
    }

    [AvaloniaFact]
    public async Task ElapsedTime_IsNotResentAfterAcceptedSave()
    {
        var controller = Controller(Book());
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(Book());

        await page.GoToPageAsync(1);
        var firstElapsed = controller.Progress.Attempts[^1].ElapsedSecondsDelta;
        Assert.True(firstElapsed >= 0);

        await Task.Delay(40);
        await page.GoToPageAsync(2);
        var secondElapsed = controller.Progress.Attempts[^1].ElapsedSecondsDelta;

        // The clock restarts after an accepted save, so the second delta is a small increment,
        // never the accumulated total again (M2-C1 §5: no replay of accepted intervals).
        Assert.True(secondElapsed >= 0);
        Assert.True(secondElapsed < firstElapsed + 5.0);
        Assert.Equal(2, controller.Progress.SaveCount);
        Assert.True(controller.Progress.TotalReadSeconds >= firstElapsed);
    }

    [AvaloniaFact]
    public async Task NavigateAwayFromReader_FlushesPosition()
    {
        var controller = Controller(Book());
        var window = new MainWindow(controller, new AppOptions());
        await window.EnsureReaderLoadedAsync();
        Assert.NotNull(window.Reader.LibraryBook);

        // Turn without waiting for the save, then leave the page: navigation is a save trigger.
        window.Reader.GoToPage(3);
        window.Navigate("bookshelf");
        await window.Reader.FlushProgressAsync();

        Assert.Equal("chapter-1-page-3", controller.Progress.TryGet("chapter-1")!.PageId);
        window.Close();
    }

    [AvaloniaFact]
    public async Task ClosingMainWindow_FlushesPosition()
    {
        var controller = Controller(Book());
        var window = new MainWindow(controller, new AppOptions());
        await window.EnsureReaderLoadedAsync();
        Assert.NotNull(window.Reader.LibraryBook);

        window.Reader.GoToPage(6);
        window.Close();

        // OnClosed flushes on the thread pool; wait for the durable row (bounded).
        for (var attempt = 0; attempt < 100 && controller.Progress.TryGet("chapter-1") is null; attempt++)
        {
            await Task.Delay(20);
        }

        Assert.Equal("chapter-1-page-6", controller.Progress.TryGet("chapter-1")!.PageId);
    }

    [AvaloniaFact]
    public async Task ReopeningWebtoon_DoesNotOverwriteRestoredPageBeforeUserScroll()
    {
        var book = Book(layout: "webtoon_vertical");
        var controller = Controller(book);
        var first = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        first.SetViewport(1200, 800, 2.0);
        first.LoadLibrary(book);
        await first.GoToPageAsync(3);
        var saved = controller.Progress.TryGet("chapter-1");
        Assert.NotNull(saved);
        Assert.Equal("chapter-1-page-3", saved!.PageId);

        // Reopen: the restore lays the webtoon stack out and fires ScrollChanged events with
        // intermediate geometry. None of that is a user position change, so nothing may be written.
        var reopened = await controller.LoadReaderBookAsync();
        Assert.Equal(3, reopened!.InitialPageIndex);
        var second = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        second.SetViewport(1200, 800, 2.0);
        second.LoadLibrary(reopened);
        Dispatcher.UIThread.RunJobs();
        await Task.Delay(150);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal("chapter-1-page-3", controller.Progress.TryGet("chapter-1")!.PageId);
        Assert.Equal(0, second.ProgressSaveAttempts);

        // A user scroll does persist from now on (the scroll handler may coalesce one write with the
        // explicit save, so only the durable outcome is asserted here).
        second.ApplyWebtoonScrollForTest(1700);
        await second.SaveProgressAsync();
        Assert.True(second.ProgressSaveAttempts >= 1);
        Assert.Equal("chapter-1-page-1", controller.Progress.TryGet("chapter-1")!.PageId);
    }

    [AvaloniaFact]
    public async Task DuplicateSamePositionSave_IsCoalesced()
    {
        var controller = Controller(Book());
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(Book());

        await page.GoToPageAsync(2);
        Assert.Equal(1, controller.Progress.SaveCount);

        // An immediate extra flush of the same position carries no new reading time: it must not be
        // sent again (otherwise elapsed_seconds_delta would be double-counted by the Core).
        await page.SaveProgressAsync();
        Assert.Equal(1, controller.Progress.SaveCount);
    }

    // ------------------------------------------------------------------
    // Webtoon offset + window flush
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task WebtoonScroll_SavesPageIdAndLogicalPixelOffset()
    {
        var book = Book(layout: "webtoon_vertical");
        var controller = Controller(book);
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(book);
        Assert.True(page.LibraryBook!.IsWebtoon);

        // Page 0/1 displayed height = viewport width * (1660/1200) = 1660; scroll 1700 → page 1, 40 px in.
        var index = page.ApplyWebtoonScrollForTest(1700);
        var result = await page.SaveProgressAsync();

        Assert.Equal(1, index);
        Assert.NotNull(result);
        Assert.True(result!.IsSaved);
        var attempt = controller.Progress.Attempts[^1];
        Assert.Equal("chapter-1-page-1", attempt.PageId);
        Assert.NotNull(attempt.ScrollOffsetY);
        Assert.InRange(attempt.ScrollOffsetY!.Value, 30, 50);
        Assert.Equal("chapter-1-page-1", page.LastSavedPageId);
    }

    [AvaloniaFact]
    public async Task ImmersiveWindow_EscapeFlushesProgress()
    {
        var controller = Controller(Book());
        var viewModel = new ReaderViewModel();
        var window = new ReaderWindow(viewModel, Book(), controller);
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(window.TryHandleKey(Key.Right));
        await window.Page.FlushProgressAsync();
        Assert.True(window.TryHandleKey(Key.Escape));
        Assert.Equal(1, window.EscapeCount);

        Assert.Equal("chapter-1-page-1", controller.Progress.TryGet("chapter-1")!.PageId);
        Assert.False(window.IsVisible);
    }

    [AvaloniaFact]
    public async Task FixtureFallback_DoesNotAttemptProgressWrites()
    {
        var controller = Controller(Book());
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>()) { ProgressSink = controller };
        page.SetViewport(1200, 800, 2.0);

        var result = await page.GoToPageAsync(1);

        Assert.Equal(0, result); // empty fixture page list clamps to 0; there is nothing to persist
        Assert.Null(page.LastProgressResult);
        Assert.Empty(controller.Progress.Attempts);
        Assert.Equal(0, page.ProgressSaveAttempts);
    }

    // ------------------------------------------------------------------
    // Projection → book mapping (clamp / resume)
    // ------------------------------------------------------------------

    [Fact]
    public void FromProjection_MapsInitialPageAndClampsUnknownPage()
    {
        var book = new BookSummary("book-a", "书 A", string.Empty, false, false, 8, "t", "t");
        var chapter = new ChapterSummary("chapter-1", "第 1 章", "1", 0);
        var pages = Enumerable.Range(0, 8)
            .Select(index => new ReaderPageSummary($"page-{index}", index, 1200, 1660, null, null, null))
            .ToList();
        var projection = new ReaderProjection("book-a", "chapter-1", "original", "rtl", pages)
        {
            InitialPageId = "page-5",
            InitialScrollOffsetY = 12,
            SavedProgress = new ReadingProgressSnapshot("book-a", "chapter-1", "original", "page-5", 12, 62.5, "t", 3),
        };

        var mapped = ReaderBookData.FromProjection(book, chapter, projection, (_, _) => Task.FromResult<byte[]?>(null));
        Assert.Equal(5, mapped.InitialPageIndex);
        Assert.Equal("page-5", mapped.SavedPageId);
        Assert.True(mapped.HasSavedProgress);
        Assert.Equal(12, mapped.InitialScrollOffsetY);

        var stale = projection with { InitialPageId = "page-404", SavedProgress = null };
        var clamped = ReaderBookData.FromProjection(book, chapter, stale, (_, _) => Task.FromResult<byte[]?>(null));
        Assert.Equal(0, clamped.InitialPageIndex);
        Assert.False(clamped.HasSavedProgress);
    }
}
