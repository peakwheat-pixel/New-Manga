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

/// <summary>Test seam: the window talks to this, production implementation wraps HostRuntime.</summary>
public interface IHostController : IAsyncDisposable
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
    /// </summary>
    Task<ReaderBookData?> LoadReaderBookAsync(string? bookId = null, CancellationToken cancellationToken = default);
}
