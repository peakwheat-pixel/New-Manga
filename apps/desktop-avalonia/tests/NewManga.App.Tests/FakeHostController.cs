using NewManga.App.Services;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>Scriptable controller for headless UI tests (no sidecars, no window lifecycle).</summary>
public sealed class FakeHostController : IHostController
{
    public FakeHostController(HostViewSnapshot snapshot)
    {
        Snapshot = snapshot;
    }

    public HostViewSnapshot Snapshot { get; set; }

    public int StartCalls { get; private set; }

    public Task? StartGate { get; set; }

    public int RefreshCalls { get; private set; }

    public string? LastRoundTripTitle { get; private set; }

    public event EventHandler? Changed;

    public Task StartAsync(CancellationToken cancellationToken = default)
    {
        StartCalls++;
        return Task.CompletedTask;
    }

    public Task RefreshBooksAsync(CancellationToken cancellationToken = default)
    {
        RefreshCalls++;
        return Task.CompletedTask;
    }

    public bool CreateBookResult { get; set; } = true;

    public Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default) => Task.FromResult(CreateBookResult);

    public Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default)
    {
        LastRoundTripTitle = title;
        Snapshot = Snapshot with
        {
            LastChineseRoundTrip = Snapshot.State == HostViewState.Ready
                ? $"往返一致：{title}"
                : "只读模式：S2 parity 前禁止写生产数据",
        };
        Changed?.Invoke(this, EventArgs.Empty);
        return Task.FromResult(Snapshot.State == HostViewState.Ready);
    }

    /// <summary>READER-LIBRARY-WIRE-1: scripted reader payload (null = empty library).</summary>
    public ReaderBookData? ReaderBook { get; set; }

    public bool ReaderLoadCalled { get; private set; }

    /// <summary>READER-PROGRESS-1: last (bookId, chapterId) requested from the reader seam.</summary>
    public (string? BookId, string? ChapterId) LastReaderRequest { get; private set; }

    /// <summary>READER-PROGRESS-1: in-memory Core stand-in for per (book, chapter, mode) progress.</summary>
    public FakeProgressStore Progress { get; } = new();

    /// <summary>READER-PROGRESS-1: overrides the next save results (queue, consumed in order).</summary>
    public Queue<ReaderProgressSaveResult> ScriptedSaveResults { get; } = new();

    /// <summary>CHAPTER-SELECTOR-1: scripted books by book id (multi-book entry).</summary>
    public Dictionary<string, ReaderBookData> ReaderBooksByBookId { get; } = new(StringComparer.Ordinal);

    /// <summary>CHAPTER-SELECTOR-1: scripted books by chapter id (chapter switching).</summary>
    public Dictionary<string, ReaderBookData> ReaderBooksByChapterId { get; } = new(StringComparer.Ordinal);

    /// <summary>CHAPTER-SELECTOR-1: scripted chapter lists per book (falls back to one chapter).</summary>
    public Dictionary<string, IReadOnlyList<ChapterSummary>> ChaptersByBook { get; } = new(StringComparer.Ordinal);

    /// <summary>CHAPTER-SELECTOR-1: number of ListChaptersAsync calls (tests/evidence).</summary>
    public int ChapterListCalls { get; private set; }

    public Task<ReaderBookData?> LoadReaderBookAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default)
    {
        ReaderLoadCalled = true;
        LastReaderRequest = (bookId, chapterId);

        // CHAPTER-SELECTOR-1: an exact chapter wins, then an exact book, then the legacy single book.
        ReaderBookData? book = null;
        if (!string.IsNullOrWhiteSpace(chapterId) && ReaderBooksByChapterId.TryGetValue(chapterId, out var chapterBook))
        {
            book = chapterBook;
        }
        else if (!string.IsNullOrWhiteSpace(bookId) && ReaderBooksByBookId.TryGetValue(bookId, out var idBook))
        {
            book = idBook;
        }

        book ??= ReaderBook;
        if (book is null)
        {
            return Task.FromResult<ReaderBookData?>(null);
        }

        if (!string.IsNullOrWhiteSpace(bookId) && !string.Equals(book.BookId, bookId, StringComparison.Ordinal))
        {
            book = book with { BookId = bookId };
        }

        if (!string.IsNullOrWhiteSpace(chapterId) && !string.Equals(book.ChapterId, chapterId, StringComparison.Ordinal))
        {
            book = book with { ChapterId = chapterId };
        }

        // Mimic the Core: resume maps the persisted page id back onto this page list.
        var saved = Progress.TryGet(book.ChapterId, "original");
        if (saved is null)
        {
            return Task.FromResult<ReaderBookData?>(book with { InitialPageIndex = 0, InitialScrollOffsetY = 0, SavedPageId = null });
        }

        var index = -1;
        for (var candidate = 0; candidate < book.Pages.Count; candidate++)
        {
            if (string.Equals(book.Pages[candidate].PageId, saved.PageId, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        // Core semantics on a shrunken/reordered chapter: unknown saved page → start from page 1.
        var initialIndex = index < 0 ? 0 : Math.Clamp(index, 0, Math.Max(0, book.Pages.Count - 1));
        return Task.FromResult<ReaderBookData?>(book with
        {
            InitialPageIndex = initialIndex,
            InitialScrollOffsetY = saved.ScrollOffsetY,
            SavedPageId = index < 0 ? null : saved.PageId,
        });
    }

    /// <summary>CHAPTER-SELECTOR-1: read-only chapter list (scripted, else one chapter from the book).</summary>
    public Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(
        string bookId,
        CancellationToken cancellationToken = default)
    {
        ChapterListCalls++;
        if (ChaptersByBook.TryGetValue(bookId, out var chapters))
        {
            return Task.FromResult(chapters);
        }

        if (ReaderBooksByBookId.TryGetValue(bookId, out var book))
        {
            return Task.FromResult<IReadOnlyList<ChapterSummary>>(new[]
            {
                new ChapterSummary(book.ChapterId, book.ChapterTitle, "1", 0),
            });
        }

        return Task.FromResult<IReadOnlyList<ChapterSummary>>(Array.Empty<ChapterSummary>());
    }

    public Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default)
    {
        if (ScriptedSaveResults.Count > 0)
        {
            var scripted = ScriptedSaveResults.Dequeue();
            Progress.Attempts.Add(new FakeProgressAttempt(chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta));
            return Task.FromResult(scripted);
        }

        var result = Progress.Save(ResolveBookForChapter(chapterId), chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta);
        return Task.FromResult(result);
    }

    public ValueTask DisposeAsync() => ValueTask.CompletedTask;

    /// <summary>CHAPTER-SELECTOR-1: resolve the scripted book that owns a chapter id.</summary>
    private ReaderBookData? ResolveBookForChapter(string chapterId)
    {
        if (ReaderBooksByChapterId.TryGetValue(chapterId, out var exact))
        {
            return exact;
        }

        foreach (var book in ReaderBooksByBookId.Values)
        {
            if (string.Equals(book.ChapterId, chapterId, StringComparison.Ordinal))
            {
                return book;
            }
        }

        return ReaderBook is { } fallback && string.Equals(fallback.ChapterId, chapterId, StringComparison.Ordinal)
            ? fallback
            : null;
    }

    public static HostViewSnapshot ReadySnapshot(params string[] titles)
    {
        var books = new List<BookSummary>();
        for (var i = 0; i < titles.Length; i++)
        {
            books.Add(new BookSummary(
                $"book-{i}",
                titles[i],
                string.Empty,
                false,
                false,
                null,
                "2026-10-27T00:00:00Z",
                "2026-10-27T00:00:00Z"));
        }

        return new HostViewSnapshot(
            HostViewState.Ready,
            "Host 就绪 · core_service protocol 2.3 + host_bridge wire v1",
            "只读（S2 parity 前） · sidecars ready",
            null,
            null,
            books,
            4,
            true,
            null);
    }

    public static HostViewSnapshot FailureSnapshot() => new(
        HostViewState.Failed,
        "Host 启动失败",
        "只读（S2 parity 前） · no sidecars",
        "SIDECAR_EXE_MISSING",
        "核心服务程序缺失（core_service.exe）。",
        Array.Empty<BookSummary>(),
        0,
        true,
        null);
}

/// <summary>READER-PROGRESS-1: one scripted save call recorded by <see cref="FakeProgressStore"/>.</summary>
public sealed record FakeProgressAttempt(
    string ChapterId,
    string PageId,
    string Mode,
    double? ScrollOffsetY,
    double ElapsedSecondsDelta);

/// <summary>READER-PROGRESS-1: one persisted position (Core <c>reading_progress</c> row stand-in).</summary>
public sealed record FakeProgressEntry(string PageId, double ScrollOffsetY, double ProgressPercent);

/// <summary>
/// READER-PROGRESS-1: in-memory Core stand-in. It keys progress by (chapter, mode) exactly like
/// <c>reading_progress</c> does by (book, chapter, mode), validates the page belongs to the book, and
/// keeps the accepted elapsed time so tests can assert "no resend after success".
/// </summary>
public sealed class FakeProgressStore
{
    private readonly Dictionary<string, FakeProgressEntry> _entries = new(StringComparer.Ordinal);

    public List<FakeProgressAttempt> Attempts { get; } = new();

    public int SaveCount => Attempts.Count;

    public double TotalReadSeconds { get; private set; }

    public IReadOnlyDictionary<string, FakeProgressEntry> Entries => _entries;

    public FakeProgressEntry? TryGet(string chapterId, string mode = "original") =>
        _entries.TryGetValue(Key(chapterId, mode), out var entry) ? entry : null;

    public ReaderProgressSaveResult Save(
        ReaderBookData? book,
        string chapterId,
        string pageId,
        string mode,
        double? scrollOffsetY,
        double elapsedSecondsDelta)
    {
        Attempts.Add(new FakeProgressAttempt(chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta));
        if (book is null || !string.Equals(book.ChapterId, chapterId, StringComparison.Ordinal))
        {
            return ReaderProgressSaveResult.Failed("TARGET_NOT_FOUND");
        }

        var index = -1;
        for (var candidate = 0; candidate < book.Pages.Count; candidate++)
        {
            if (string.Equals(book.Pages[candidate].PageId, pageId, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        if (index < 0)
        {
            return ReaderProgressSaveResult.Failed("TARGET_NOT_FOUND");
        }

        var percent = Math.Round((index + 1) / (double)Math.Max(1, book.Pages.Count) * 100.0, 2);
        var offset = Math.Max(0, scrollOffsetY ?? 0);
        TotalReadSeconds += Math.Max(0, elapsedSecondsDelta);
        _entries[Key(chapterId, mode)] = new FakeProgressEntry(pageId, offset, percent);
        return ReaderProgressSaveResult.Saved(percent, pageId);
    }

    private static string Key(string chapterId, string mode) => chapterId + "|" + mode;
}
