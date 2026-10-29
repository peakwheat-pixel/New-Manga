using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// CHAPTER-SELECTOR-1: the reader lists the chapters of the loaded book (list_chapters), switching a
/// chapter reloads that chapter's projection, and any library book can be opened from the bookshelf
/// (no longer "first book, first chapter").
/// </summary>
public sealed class ReaderChapterSelectorTests
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    private static byte[] OnePixelPng() => Convert.FromBase64String(OnePixelPngBase64);

    private static ReaderBookData Book(
        string bookId,
        string bookTitle,
        string chapterId,
        string chapterTitle,
        int pages)
    {
        var items = Enumerable.Range(0, pages)
            .Select(index => new ReaderPageData(
                $"{chapterId}-page-{index}",
                index,
                1200,
                1660,
                _ => Task.FromResult<byte[]?>(OnePixelPng())))
            .ToList();
        return new ReaderBookData(bookId, bookTitle, chapterId, chapterTitle, "rtl", items);
    }

    private static FakeHostController Controller(params ReaderBookData[] books)
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot(books.Select(book => book.BookTitle).ToArray()))
        {
            ReaderBook = books.FirstOrDefault(),
        };
        foreach (var book in books)
        {
            controller.ReaderBooksByBookId[book.BookId] = book;
            controller.ReaderBooksByChapterId[book.ChapterId] = book;
        }

        foreach (var group in books.GroupBy(book => book.BookId))
        {
            var chapters = group
                .Select((book, index) => new ChapterSummary(book.ChapterId, book.ChapterTitle, (index + 1).ToString(), index))
                .ToList();
            controller.ChaptersByBook[group.Key] = chapters;
        }

        return controller;
    }

    private const string BookA = "book-a";
    private const string BookB = "book-b";

    private static ReaderBookData ChapterA1() => Book(BookA, "书 A", "chapter-a1", "第 1 章", 8);

    private static ReaderBookData ChapterA2() => Book(BookA, "书 A", "chapter-a2", "第 2 章", 4);

    private static ReaderBookData BookBBook() => Book(BookB, "书 B", "chapter-b1", "第 1 章", 5);

    // ------------------------------------------------------------------
    // AC1: chapter list + switching
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public void ReaderPage_LoadChapters_ShowsSelectorAndRaisesSelection()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(ChapterA1());
        var chapters = new[]
        {
            new ChapterSummary("chapter-a1", "第 1 章", "1", 0),
            new ChapterSummary("chapter-a2", "第 2 章", "2", 1),
        };

        page.LoadChapters(chapters, "chapter-a1");

        Assert.Equal(2, page.Chapters.Count);
        Assert.True(page.ChapterSelector.IsVisible);
        Assert.Equal("chapter-a1", page.SelectedChapterId);
        Assert.Equal("chapter-a1", page.CurrentChapterId);
        Assert.Contains("书 A", page.BookContext.Text);
        Assert.Contains("第 1 章", page.BookContext.Text);

        string? requested = null;
        page.ChapterSelectionRequested += (_, chapterId) => requested = chapterId;
        page.ChapterSelector.SelectedItem = page.ChapterSelector.ItemsSource!.OfType<ReaderPage.ChapterChoice>().Last();

        Assert.Equal("chapter-a2", requested);
    }

    [AvaloniaFact]
    public void SingleChapterBook_HidesSelector()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(ChapterA1());
        page.LoadChapters(new[] { new ChapterSummary("chapter-a1", "第 1 章", "1", 0) }, "chapter-a1");

        Assert.False(page.ChapterSelector.IsVisible);
        Assert.Single(page.Chapters);
    }

    [AvaloniaFact]
    public void PreviousNextChapterButtons_RaiseSelectionAndRespectBoundaries()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(ChapterA1());
        var chapters = new[]
        {
            new ChapterSummary("chapter-a1", "第 1 章", "1", 0),
            new ChapterSummary("chapter-a2", "第 2 章", "2", 1),
        };
        page.LoadChapters(chapters, "chapter-a1");

        Assert.True(page.PreviousChapterButton.IsVisible);
        Assert.True(page.NextChapterButton.IsVisible);
        Assert.False(page.PreviousChapterButton.IsEnabled);
        Assert.True(page.NextChapterButton.IsEnabled);

        string? requested = null;
        page.ChapterSelectionRequested += (_, chapterId) => requested = chapterId;
        Assert.True(page.SelectAdjacentChapter(1));
        Assert.Equal("chapter-a2", requested);

        // The window then reloads that chapter; at the last chapter "next" is a no-op.
        page.LoadLibrary(ChapterA2());
        page.LoadChapters(chapters, "chapter-a2");
        Assert.False(page.NextChapterButton.IsEnabled);
        Assert.True(page.PreviousChapterButton.IsEnabled);
        Assert.False(page.SelectAdjacentChapter(1));
    }

    [AvaloniaFact]
    public void ToolbarAndScrollbarPresses_DoNotPageTurn()    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(ChapterA1());

        // Toolbar controls (chapter picker / immersive button) must not page-turn.
        Assert.False(page.IsPageTurnSourceForTest(page.ChapterSelector));
        Assert.False(page.IsPageTurnSourceForTest(page.ImmersiveButton));
        // The reading surface still turns pages.
        Assert.True(page.IsPageTurnSourceForTest(page.PageImage));
        Assert.True(page.IsPageTurnSourceForTest(page.WebtoonScroll));
    }

    [AvaloniaFact]
    public async Task SwitchingChapter_UpdatesPageCountProjectionAndContext()
    {
        var controller = Controller(ChapterA1(), ChapterA2());
        var window = new MainWindow(controller, new AppOptions());
        Assert.True(await window.OpenReaderForBookAsync(BookA, "chapter-a1"));
        await window.LastReaderNavigation;
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(BookA, window.CurrentReaderBookId);
        Assert.Equal("chapter-a1", window.CurrentReaderChapterId);
        Assert.Equal(8, window.Reader.ViewModel.PageCount);
        Assert.True(window.Reader.ChapterSelector.IsVisible);
        Assert.Contains("第 1 章", window.Reader.BookContext.Text);

        // User picks chapter 2 in the selector → the window reloads that chapter.
        var choices = window.Reader.ChapterSelector.ItemsSource!.OfType<ReaderPage.ChapterChoice>().ToList();
        window.Reader.ChapterSelector.SelectedItem = choices.Single(choice => choice.ChapterId == "chapter-a2");
        await window.LastReaderNavigation;
        Dispatcher.UIThread.RunJobs();

        Assert.Equal("chapter-a2", window.CurrentReaderChapterId);
        Assert.Equal(4, window.Reader.ViewModel.PageCount);
        Assert.Equal("chapter-a2", window.Reader.LibraryBook!.ChapterId);
        Assert.Equal("chapter-a2", window.Reader.SelectedChapterId);
        Assert.Equal(0, window.Reader.ViewModel.CurrentPageIndex);
        Assert.Contains("第 2 章", window.Reader.BookContext.Text);
        window.Close();
    }

    [AvaloniaFact]
    public async Task SwitchingChapter_FlushesPreviousChapterProgress()
    {
        var controller = Controller(ChapterA1(), ChapterA2());
        var window = new MainWindow(controller, new AppOptions());
        await window.OpenReaderForBookAsync(BookA, "chapter-a1");
        await window.Reader.GoToPageAsync(2);
        Assert.Equal("chapter-a1-page-2", controller.Progress.TryGet("chapter-a1")!.PageId);

        var choices = window.Reader.ChapterSelector.ItemsSource!.OfType<ReaderPage.ChapterChoice>().ToList();
        // The picker may not be populated yet when the load was direct; populate defensively.
        if (choices.Count == 0)
        {
            await window.PopulateChaptersAsync();
            choices = window.Reader.ChapterSelector.ItemsSource!.OfType<ReaderPage.ChapterChoice>().ToList();
        }

        window.Reader.ChapterSelector.SelectedItem = choices.Single(choice => choice.ChapterId == "chapter-a2");
        await window.LastReaderNavigation;

        Assert.Equal("chapter-a2", window.CurrentReaderChapterId);
        // chapter a1 position is durable, chapter a2 opens at its own start
        Assert.Equal("chapter-a1-page-2", controller.Progress.TryGet("chapter-a1")!.PageId);
        Assert.Null(controller.Progress.TryGet("chapter-a2"));
        window.Close();
    }

    // ------------------------------------------------------------------
    // AC2: any library book opens from the bookshelf
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task MultiBookEntry_OpensRequestedBook()
    {
        var controller = Controller(ChapterA1(), BookBBook());
        var window = new MainWindow(controller, new AppOptions());

        Assert.True(await window.OpenReaderForBookAsync(BookB));
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(BookB, window.CurrentReaderBookId);
        Assert.Equal("chapter-b1", window.CurrentReaderChapterId);
        Assert.Equal(5, window.Reader.ViewModel.PageCount);
        Assert.Contains("书 B", window.Reader.BookContext.Text);
        Assert.Contains("第 1 章", window.Reader.BookContext.Text);
        window.Close();
    }

    [AvaloniaFact]
    public async Task BookshelfOpenRequest_OpensThatBookInTheReader()
    {
        var controller = Controller(ChapterA1(), BookBBook());
        var window = new MainWindow(controller, new AppOptions());
        var card = new BookCardItem
        {
            BookId = BookB,
            Title = "书 B",
            PageCount = 5,
        };

        // Cards open on double-click; the detail panel exposes the same request.
        window.BookshelfPageControl.RequestOpenReader(card);
        await window.LastReaderNavigation;
        Dispatcher.UIThread.RunJobs();

        Assert.Same(card, window.BookshelfPageControl.LastOpenReaderRequest);
        Assert.Equal(BookB, window.CurrentReaderBookId);
        window.Close();
    }

    [AvaloniaFact]
    public async Task OpeningDifferentBook_FlushesCurrentBookProgress()
    {
        var controller = Controller(ChapterA1(), BookBBook());
        var window = new MainWindow(controller, new AppOptions());
        await window.OpenReaderForBookAsync(BookA);
        await window.Reader.GoToPageAsync(3);

        Assert.True(await window.OpenReaderForBookAsync(BookB));
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(BookB, window.CurrentReaderBookId);
        Assert.Equal("chapter-a1-page-3", controller.Progress.TryGet("chapter-a1")!.PageId);

        // Back to book A: it resumes the persisted page.
        Assert.True(await window.OpenReaderForBookAsync(BookA));
        Assert.Equal(3, window.Reader.ViewModel.CurrentPageIndex);
        window.Close();
    }

    [AvaloniaFact]
    public async Task DefaultReaderEntry_StillOpensFirstReadableBook()
    {
        var controller = Controller(ChapterA1(), ChapterA2(), BookBBook());
        var window = new MainWindow(controller, new AppOptions());

        await window.EnsureReaderLoadedAsync();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(BookA, window.CurrentReaderBookId);
        Assert.True(controller.ChapterListCalls >= 1, $"chapter list calls={controller.ChapterListCalls}");
        Assert.Equal(2, controller.ChaptersByBook[BookA].Count);
        var loadedIds = string.Join(",", window.Reader.Chapters.Select(chapter => chapter.ChapterId));
        Assert.True(
            window.Reader.Chapters.Count == 2,
            $"reader chapters={window.Reader.Chapters.Count} [{loadedIds}] calls={controller.ChapterListCalls} lastRequest={window.Reader.LibraryBook?.BookId}/{window.Reader.LibraryBook?.ChapterId}");
        Assert.Null(window.BookshelfPageControl.LastOpenReaderRequest);
        window.Close();
    }

    [AvaloniaFact]
    public async Task EmptyChapterList_HidesSelectorWithoutCrash()
    {
        var controller = Controller(ChapterA1());
        controller.ChaptersByBook.Clear(); // Host returned nothing (e.g. Core read failure)
        controller.ReaderBooksByBookId.Clear();
        var window = new MainWindow(controller, new AppOptions());

        Assert.True(await window.OpenReaderForBookAsync(BookA, "chapter-a1"));
        await window.PopulateChaptersAsync();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal("chapter-a1", window.CurrentReaderChapterId);
        Assert.False(window.Reader.ChapterSelector.IsVisible);
        window.Close();
    }

    [AvaloniaFact]
    public async Task ImmersiveWindow_ShowsContextButNoChapterPicker()
    {
        var controller = Controller(ChapterA1(), ChapterA2());
        var window = new MainWindow(controller, new AppOptions());
        await window.OpenReaderForBookAsync(BookA, "chapter-a1");
        await window.PopulateChaptersAsync();
        Dispatcher.UIThread.RunJobs();

        var immersive = window.OpenImmersiveReader();
        Dispatcher.UIThread.RunJobs();

        Assert.False(immersive.Page.ChapterSelector.IsVisible);
        Assert.Equal(2, immersive.Page.Chapters.Count);
        Assert.Contains("第 1 章", immersive.Page.BookContext.Text);
        immersive.Close();
        window.Close();
    }
}
