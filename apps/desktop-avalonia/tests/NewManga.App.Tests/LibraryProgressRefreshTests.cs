using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.ViewModels.V2.Shell;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// REALUSE-DATA-SAFETY-6 AC1 (audit MA-09): the shelf and the reader must show the SAME current
/// progress after a save, and the shelf line must not stay stale after an import.
///
/// These are behaviour tests, not "the method is called" tests:
///  - the shelf line is asserted as the exact string the reader shows (page label + percentage),
///  - a <see cref="System.ComponentModel.INotifyPropertyChanged"/> for
///    <see cref="LibraryViewModel.DetailProgressText"/> must fire (that is what re-renders the
///    bound detail panel),
///  - <see cref="LibraryViewModel.ProgressRefreshes"/> must move (the refresh path really ran),
///  - closing the reader must produce a REAL Host projection read
///    (<see cref="FakeHostController.ReaderLoadCount"/>), and the import test drives the real
///    import dock so the production <c>afterImport</c> hook is what refreshes the shelf.
/// A refused save (read-only Host) must NOT fabricate a shelf update.
/// </summary>
public sealed class LibraryProgressRefreshTests
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    private const string BookId = "book-0";

    private const string ChapterId = "ch-0";

    private static byte[] OnePixelPng() => Convert.FromBase64String(OnePixelPngBase64);

    /// <summary>Paged (not webtoon) reader book so the reader's percentage is page-derived, exactly
    /// like the Core's <c>reading_progress.progress_percent</c> for a paged chapter.</summary>
    private static ReaderBookData Book(int pages) => new(
        BookId,
        "夜光列车",
        ChapterId,
        "第 1 话 · 灯を消すな",
        "rtl",
        Enumerable.Range(0, pages)
            .Select(index => new ReaderPageData(
                $"page-{index}",
                index,
                1200,
                1660,
                _ => Task.FromResult<byte[]?>(OnePixelPng())))
            .ToList());

    private static FakeHostController CreateController(int pages = 8)
    {
        var snapshot = new HostViewSnapshot(
            HostViewState.Ready,
            "Host 就绪 · core_service protocol 2.3 + host_bridge wire v1",
            "读写（隔离数据根） · sidecars ready",
            null,
            null,
            new[]
            {
                new BookSummary(
                    BookId,
                    "夜光列车",
                    string.Empty,
                    false,
                    false,
                    pages,
                    "2026-10-20T00:00:00Z",
                    "2026-10-29T00:00:00Z"),
            },
            4,
            true,
            null);

        var controller = new FakeHostController(snapshot);
        controller.ChaptersByBook[BookId] = new[]
        {
            new ChapterSummary(ChapterId, "第 1 话 · 灯を消すな", "1", 0),
        };
        controller.ChapterPagesByChapter[ChapterId] = Enumerable.Range(0, pages)
            .Select(index => new ChapterPageSummary($"page-{index}", $"{index + 1:000}.jpg", index))
            .ToList();
        controller.ReaderBooksByChapterId[ChapterId] = Book(pages);
        return controller;
    }

    private static async Task<(FakeHostController Controller, AppShellViewModel Shell, LibraryViewModel Library)>
        CreateLibraryAsync(int pages = 8)
    {
        var controller = CreateController(pages);
        var shell = new AppShellViewModel(controller);
        await shell.Library.InitializeAsync();
        return (controller, shell, shell.Library);
    }

    // ------------------------------------------------------------------
    // AC1-A: a committed save refreshes the shelf in the same action
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task CommittedSave_RefreshesShelfDetail_AndShelfMatchesReader()
    {
        var (_, _, library) = await CreateLibraryAsync(pages: 8);
        Assert.Equal(ChapterId, library.SelectedChapter?.ChapterId);
        Assert.Equal("未开始阅读 · 共 8 页", library.DetailProgressText);

        var notified = new List<string?>();
        library.PropertyChanged += (_, args) => notified.Add(args.PropertyName);
        var refreshesBefore = library.ProgressRefreshes;

        Assert.True(await library.Reader.OpenAsync(BookId, ChapterId));
        await library.Reader.GoToAsync(4); // 0-based index 4 == 第 5 页

        // The reader committed the page through IHostController.SaveReadingProgressAsync.
        Assert.Equal(ReaderProgressSaveStatus.Saved, library.Reader.LastSaveResult?.Status);
        Assert.Equal(5, library.Reader.PageIndex + 1);

        // 1) The shelf line now shows the same dual-modality progress the reader shows.
        Assert.Equal("读到 " + library.Reader.ProgressText, library.DetailProgressText);
        Assert.Contains("第 5 / 8 页", library.DetailProgressText, StringComparison.Ordinal);
        Assert.DoesNotContain("未开始阅读", library.DetailProgressText, StringComparison.Ordinal);

        // 2) The refresh really happened: the bound property was re-raised and the refresh path ran.
        Assert.Contains(nameof(LibraryViewModel.DetailProgressText), notified);
        Assert.True(
            library.ProgressRefreshes > refreshesBefore,
            $"ProgressRefreshes must move ({refreshesBefore} -> {library.ProgressRefreshes})");
    }

    [AvaloniaFact]
    public async Task ClosingReader_ReReadsHostProjection_AndShelfShowsResumePage()
    {
        var (controller, _, library) = await CreateLibraryAsync(pages: 8);
        Assert.True(await library.Reader.OpenAsync(BookId, ChapterId));
        await library.Reader.GoToAsync(4);
        var readerLine = library.Reader.ProgressText;
        Assert.Contains("第 5 / 8 页", readerLine, StringComparison.Ordinal);

        var loadsBefore = controller.ReaderLoadCount;
        var refreshesBefore = library.ProgressRefreshes;

        await library.Reader.CloseAsync();

        // A real Host read happened on close -- not just a cached re-render.
        Assert.True(
            controller.ReaderLoadCount > loadsBefore,
            $"closing the reader must re-read the Core projection ({loadsBefore} -> {controller.ReaderLoadCount})");
        Assert.Equal((BookId, ChapterId), controller.LastReaderRequest);
        Assert.True(library.ProgressRefreshes > refreshesBefore);
        Assert.Equal("读到 " + readerLine, library.DetailProgressText);
        Assert.False(library.Reader.IsOpen);

        // Reopening the same chapter resumes on the persisted page: reader and shelf still agree.
        Assert.True(await library.Reader.OpenAsync(BookId, ChapterId));
        Assert.Equal(5, library.Reader.PageIndex + 1);
        Assert.Equal("读到 " + library.Reader.ProgressText, library.DetailProgressText);
    }

    // ------------------------------------------------------------------
    // AC1-B: an import must not leave stale progress information
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task Import_RefreshesProgressLine_WithNewPageCount()
    {
        var (controller, _, library) = await CreateLibraryAsync(pages: 8);
        Assert.True(await library.Reader.OpenAsync(BookId, ChapterId));
        await library.Reader.GoToAsync(4);
        await library.Reader.CloseAsync();
        Assert.Equal("读到 第 5 / 8 页 · 63%", library.DetailProgressText);

        // The Core grows the chapter by two pages (what a real import does), then the REAL import dock
        // runs: its afterImport hook is the production path under test.
        var grown = 10;
        controller.ChapterPagesByChapter[ChapterId] = Enumerable.Range(0, grown)
            .Select(index => new ChapterPageSummary($"page-{index}", $"{index + 1:000}.jpg", index))
            .ToList();
        controller.ReaderBooksByChapterId[ChapterId] = Book(grown);
        controller.ScriptedImportResults.Enqueue(ImportOutcome.Success(2, 0));

        var loadsBefore = controller.ReaderLoadCount;
        var pageCallsBefore = controller.ChapterPageCalls.Count;
        await library.ImportDock.OpenWithFilesAsync(new[] { "/pick/009.jpg", "/pick/010.jpg" });

        Assert.Equal(2, library.ImportDock.Rows.Count);
        Assert.All(library.ImportDock.Rows, row => Assert.Equal(ImportRowState.Imported, row.State));
        Assert.True(controller.ChapterPageCalls.Count > pageCallsBefore, "import must reload the page list");
        Assert.True(
            controller.ReaderLoadCount > loadsBefore,
            $"import must re-read the progress projection ({loadsBefore} -> {controller.ReaderLoadCount})");

        // Neither the old denominator nor the old percentage may survive the import.
        Assert.DoesNotContain("/ 8 页", library.DetailProgressText, StringComparison.Ordinal);
        Assert.Equal("读到 第 5 / 10 页 · 50%", library.DetailProgressText);
        Assert.Equal(10, library.Pages.Count);
    }

    // ------------------------------------------------------------------
    // AC1-C: a refused save must not fabricate a shelf update
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task RefusedSave_DoesNotFabricateShelfRefresh()
    {
        var (controller, _, library) = await CreateLibraryAsync(pages: 8);
        Assert.True(await library.Reader.OpenAsync(BookId, ChapterId));
        var refreshesBefore = library.ProgressRefreshes;
        controller.ScriptedSaveResults.Enqueue(ReaderProgressSaveResult.ReadOnly());

        await library.Reader.GoToAsync(2);

        Assert.Contains("Host 只读", library.Reader.SaveStatusText, StringComparison.Ordinal);
        // Nothing reached the Core, so the shelf keeps the truthful "never read" line.
        Assert.Equal("未开始阅读 · 共 8 页", library.DetailProgressText);
        Assert.Equal(refreshesBefore, library.ProgressRefreshes);
        Assert.Empty(controller.Progress.Entries);
    }

    // ------------------------------------------------------------------
    // AC1-D: an unrelated chapter must not be overwritten by a deep-linked reader
    // ------------------------------------------------------------------

    [AvaloniaFact]
    public async Task ReaderOnAnotherChapter_DoesNotRewriteTheSelectedChapterLine()
    {
        var (controller, _, library) = await CreateLibraryAsync(pages: 8);
        // A second chapter exists, its own reader projection has 3 pages.
        controller.ChaptersByBook[BookId] = new[]
        {
            new ChapterSummary(ChapterId, "第 1 话 · 灯を消すな", "1", 0),
            new ChapterSummary("ch-1", "第 2 话 · 車掌の記憶", "2", 1),
        };
        var other = Book(3) with { ChapterId = "ch-1", ChapterTitle = "第 2 话 · 車掌の記憶" };
        controller.ReaderBooksByChapterId["ch-1"] = other;
        controller.ChapterPagesByChapter["ch-1"] = Enumerable.Range(0, 3)
            .Select(index => new ChapterPageSummary($"page-{index}", $"{index + 1:000}.jpg", index))
            .ToList();

        Assert.Equal(ChapterId, library.SelectedChapter?.ChapterId);
        Assert.Equal("未开始阅读 · 共 8 页", library.DetailProgressText);
        var refreshesBefore = library.ProgressRefreshes;

        // Deep link: the reader opens the other chapter without changing the shelf selection.
        Assert.True(await library.Reader.OpenAsync(BookId, "ch-1"));
        await library.Reader.GoToAsync(1);
        Assert.Equal(ReaderProgressSaveStatus.Saved, library.Reader.LastSaveResult?.Status);

        Assert.Equal(ChapterId, library.SelectedChapter?.ChapterId);
        Assert.Equal("未开始阅读 · 共 8 页", library.DetailProgressText);
        Assert.Equal(refreshesBefore, library.ProgressRefreshes);
    }

    // ------------------------------------------------------------------
    // AC1-E (REALUSE-DATA-SAFETY-7 R-001): closing while a save is in flight
    // ------------------------------------------------------------------

    /// <summary>
    /// R-001 reproducer-turned-regression test: a page save is held inside the Host await, the user
    /// closes the reader, and the pending save then resumes. Before the fix this dereferenced a
    /// <c>_book</c> the close had already set to null (unhandled NRE, propagated out of
    /// <c>GoToAsync</c>) and the closing authoritative re-read was skipped because
    /// <c>_isSaving</c> short-circuited the closing pass.
    /// </summary>
    [AvaloniaFact]
    public async Task ClosingWhileSaveInFlight_DoesNotThrow_AndStillReReadsProjection()
    {
        var (controller, _, library) = await CreateLibraryAsync(pages: 8);
        Assert.True(await library.Reader.OpenAsync(BookId, ChapterId));
        var loadsBefore = controller.ReaderLoadCount;

        // Hold the next progress save inside the Host await so the close races it deterministically.
        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        controller.SaveGate = gate.Task;

        var navigation = library.Reader.GoToAsync(3); // starts the save, blocks on the gate
        await controller.SaveGateStarted.Task.WaitAsync(TimeSpan.FromSeconds(5));
        Assert.True(controller.ProgressSaveCalls >= 1);

        // Close while the save is pending: must not throw and must still re-read the projection.
        var closing = library.Reader.CloseAsync();
        gate.SetResult(true);
        await navigation; // throws NullReferenceException without the R-001 fix
        await closing;

        Assert.False(library.Reader.IsOpen);
        Assert.True(
            controller.ReaderLoadCount > loadsBefore,
            $"closing during an in-flight save must re-read the projection ({loadsBefore} -> {controller.ReaderLoadCount})");
        Assert.Equal(ReaderProgressSaveStatus.Saved, library.Reader.LastSaveResult?.Status);
        Assert.NotEmpty(controller.Progress.Entries);
    }
}
