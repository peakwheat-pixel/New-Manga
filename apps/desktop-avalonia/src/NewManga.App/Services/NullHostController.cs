using NewManga.CoreClient;

namespace NewManga.App.Services;

/// <summary>
/// Inert controller used by the XAML runtime loader / visual designers. It never starts a sidecar;
/// production always constructs <see cref="HostController"/>.
/// </summary>
public sealed class NullHostController : IHostController
{
    public static NullHostController Instance { get; } = new();

    private NullHostController()
    {
    }

    public HostViewSnapshot Snapshot { get; } = new(
        HostViewState.Starting,
        "设计时占位",
        "—",
        null,
        null,
        Array.Empty<BookSummary>(),
        0,
        true,
        null);

    public event EventHandler? Changed
    {
        add { }
        remove { }
    }

    public Task StartAsync(CancellationToken cancellationToken = default) => Task.CompletedTask;

    public Task RefreshBooksAsync(CancellationToken cancellationToken = default) => Task.CompletedTask;

    public Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default) =>
        Task.FromResult(false);

    public Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default) =>
        Task.FromResult(false);

    public Task<ReaderBookData?> LoadReaderBookAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<ReaderBookData?>(null);

    public Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(
        string bookId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<ChapterSummary>>(Array.Empty<ChapterSummary>());

    public Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(ReaderProgressSaveResult.NotReady());

    public ValueTask DisposeAsync() => ValueTask.CompletedTask;
}
