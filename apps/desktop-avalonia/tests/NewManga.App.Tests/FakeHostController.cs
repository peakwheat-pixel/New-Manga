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

    public ValueTask DisposeAsync() => ValueTask.CompletedTask;

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
