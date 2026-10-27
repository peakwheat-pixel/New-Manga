using NewManga.CoreClient;

namespace NewManga.App.Services;

public enum HostViewState
{
    Starting,
    Ready,
    AlreadyRunning,
    Failed,
}

/// <summary>UI-facing host state. Deliberately free of OS paths: only typed codes + friendly text.</summary>
public sealed record HostViewSnapshot(
    HostViewState State,
    string StatusLine,
    string ModeLine,
    string? ErrorCode,
    string? ErrorMessage,
    IReadOnlyList<BookSummary> Books,
    int WireFrameCount,
    bool AllRequestsAsciiOnly,
    string? LastChineseRoundTrip);

/// <summary>READER-PROGRESS-1: typed outcome of one progress save (never throws into the UI).</summary>
public enum ReaderProgressSaveStatus
{
    /// <summary>Core committed the row (ReadingProgressSnapshot returned).</summary>
    Saved,

    /// <summary>No Core: host is starting / failed / already running.</summary>
    NotReady,

    /// <summary>Host is read-only until parity; nothing was sent to the Core.</summary>
    ReadOnly,

    /// <summary>Core or transport rejected the save; <see cref="ReaderProgressSaveResult.ErrorCode"/> is typed.</summary>
    Failed,
}

/// <summary>READER-PROGRESS-1: result of one <see cref="IReaderProgressSink"/> call.</summary>
public sealed record ReaderProgressSaveResult(
    ReaderProgressSaveStatus Status,
    string? ErrorCode = null,
    double ProgressPercent = 0,
    string? LastPageId = null)
{
    public bool IsSaved => Status == ReaderProgressSaveStatus.Saved;

    public static ReaderProgressSaveResult Saved(double progressPercent, string? lastPageId) =>
        new(ReaderProgressSaveStatus.Saved, null, progressPercent, lastPageId);

    public static ReaderProgressSaveResult NotReady() =>
        new(ReaderProgressSaveStatus.NotReady, "HOST_NOT_READY");

    public static ReaderProgressSaveResult ReadOnly() =>
        new(ReaderProgressSaveStatus.ReadOnly, "HOST_READ_ONLY");

    public static ReaderProgressSaveResult Failed(string code) =>
        new(ReaderProgressSaveStatus.Failed, code);
}

/// <summary>
/// READER-PROGRESS-1: the reader page only needs this one seam to persist its position. The window
/// injects the controller; tests inject a scripted fake. Implementations must never throw — failures
/// come back as <see cref="ReaderProgressSaveResult"/> so a broken save never blocks the UI.
/// </summary>
public interface IReaderProgressSink
{
    Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default);
}

/// <summary>Test seam: the window talks to this, production implementation wraps HostRuntime.</summary>
public interface IHostController : IReaderProgressSink, IAsyncDisposable
{
    HostViewSnapshot Snapshot { get; }

    event EventHandler? Changed;

    Task StartAsync(CancellationToken cancellationToken = default);

    Task RefreshBooksAsync(CancellationToken cancellationToken = default);

    /// <summary>Creates the fixed AC3 Chinese vector; false when the host is read-only.</summary>
    Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default);

    Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default);

    /// <summary>
    /// READER-LIBRARY-WIRE-1 AC1: real reader payload (ListBooks → list_chapters → GetReaderProjection)
    /// for the reader page. Null when the Host is not ready, the library is empty, or the read fails;
    /// the reader then keeps its fixture fallback.
    /// READER-PROGRESS-1: the projection asks for <c>start_position="resume"</c>, so the returned book
    /// carries <see cref="ReaderBookData.InitialPageIndex"/> for the last read page.
    /// </summary>
    Task<ReaderBookData?> LoadReaderBookAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default);
}
