using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host;

namespace NewManga.App.Services;

/// <summary>Production controller: starts <see cref="HostRuntime"/> and maps typed failures to UI text.</summary>
public sealed class HostController : IHostController
{
    private readonly HostOptions _options;
    private HostRuntime? _runtime;
    private HostViewSnapshot _snapshot = new(
        HostViewState.Starting,
        "正在启动 Host…",
        "—",
        null,
        null,
        Array.Empty<BookSummary>(),
        0,
        true,
        null);

    public HostController(HostOptions options)
    {
        _options = options;
    }

    public HostViewSnapshot Snapshot => _snapshot;

    public event EventHandler? Changed;

    public async Task StartAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _runtime = await HostRuntime.StartAsync(_options, cancellationToken).ConfigureAwait(false);
            UpdateFromRuntime();
        }
        catch (Exception ex) when (ex is SidecarException or IOException or UnauthorizedAccessException or OperationCanceledException)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "Host 启动失败",
                ErrorCode = ex is SidecarException sidecar ? sidecar.Code.ToString() : "HOST_START_IO",
                ErrorMessage = ex is SidecarException typed ? typed.UserMessage : "Host 启动时发生 I/O 错误，详见 host.log。",
            };
            Changed?.Invoke(this, EventArgs.Empty);
        }

        if (_snapshot.State == HostViewState.Ready)
        {
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
        }
    }

    public async Task RefreshBooksAsync(CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return;
        }

        try
        {
            var books = await _runtime.ListBooksAsync(cancellationToken).ConfigureAwait(false);
            UpdateFromRuntime(books);
        }
        catch (CoreOperationException ex)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "读取书架失败",
                ErrorCode = ex.Code,
                ErrorMessage = "Core 返回了错误码，详见 host.log。",
            };
            Changed?.Invoke(this, EventArgs.Empty);
        }
        catch (SidecarException ex)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "核心服务中断",
                ErrorCode = ex.Code.ToString(),
                ErrorMessage = ex.UserMessage,
            };
            Changed?.Invoke(this, EventArgs.Empty);
        }
    }

    public async Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return false;
        }

        try
        {
            var result = await _runtime.RoundTripChineseTitleAsync(title, cancellationToken).ConfigureAwait(false);
            _snapshot = _snapshot with
            {
                LastChineseRoundTrip = result.ExactMatch
                    ? $"往返一致：{result.Expected}"
                    : $"往返不一致：expected={result.Expected} received={result.Received}",
            };
            Changed?.Invoke(this, EventArgs.Empty);
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
            return result.ExactMatch;
        }
        catch (ReadOnlyHostException)
        {
            _snapshot = _snapshot with
            {
                LastChineseRoundTrip = "只读模式：S2 parity 前禁止写生产数据",
            };
            Changed?.Invoke(this, EventArgs.Empty);
            return false;
        }
        catch (Exception ex) when (ex is CoreOperationException or SidecarException)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "中文往返失败",
                ErrorCode = ex is CoreOperationException core ? core.Code : ((SidecarException)ex).Code.ToString(),
                ErrorMessage = "核心服务返回错误，详见 host.log。",
            };
            Changed?.Invoke(this, EventArgs.Empty);
            return false;
        }
    }

    public async Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return false;
        }

        try
        {
            await _runtime.CreateBookAsync(title, cancellationToken).ConfigureAwait(false);
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
            return true;
        }
        catch (Exception ex) when (ex is ReadOnlyHostException or CoreOperationException or SidecarException or OperationCanceledException)
        {
            return false;
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_runtime is not null)
        {
            await _runtime.DisposeAsync().ConfigureAwait(false);
            _runtime = null;
        }
    }

    private void UpdateFromRuntime(IReadOnlyList<BookSummary>? books = null)
    {
        if (_runtime is null)
        {
            return;
        }

        var result = _runtime.Result;
        var wireCount = _runtime.CoreService?.Wire.Count ?? 0;
        var bridgeFrames = _runtime.HostBridge?.Wire.Count ?? 0;
        var allAscii = _runtime.CoreService?.Wire.AllRequestsAsciiOnly ?? false;
        _snapshot = new HostViewSnapshot(
            result.Status switch
            {
                HostStatus.Ready => HostViewState.Ready,
                HostStatus.AlreadyRunning => HostViewState.AlreadyRunning,
                _ => HostViewState.Failed,
            },
            result.Status switch
            {
                HostStatus.Ready => "Host 就绪 · core_service protocol 2.3 + host_bridge wire v1",
                HostStatus.AlreadyRunning => "已有 New Manga 主机在运行",
                _ => "Host 启动失败",
            },
            $"{CoexistenceRules.Describe(result.Mode)} · {(result.Status == HostStatus.Ready ? "sidecars ready" : "no sidecars")}",
            result.ErrorCode,
            result.UserMessage,
            books ?? Array.Empty<BookSummary>(),
            wireCount + bridgeFrames,
            allAscii,
            _snapshot.LastChineseRoundTrip);
        Changed?.Invoke(this, EventArgs.Empty);
    }
}
