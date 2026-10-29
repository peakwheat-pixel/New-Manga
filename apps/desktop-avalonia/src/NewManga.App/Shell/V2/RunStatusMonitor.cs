using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.CoreClient.Diagnostics;

namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-INT-0 / R-24: the ONE shared Run-status source for the shell, Console and (later) Studio Batch.
/// It owns a single 1s poll over <see cref="IRunController.GetRunSnapshotAsync"/> +
/// <see cref="IRunController.GetTaskProjectionAsync"/> for the tracked run id; consumers subscribe to
/// <see cref="Updated"/> instead of starting their own timers. No projection is invented: when the Host
/// refuses, the snapshot is dropped and the status reverts to "未加载".
/// </summary>
public sealed class RunStatusMonitor : ObservableObject, IDisposable
{
    private readonly IRunController _controller;
    private readonly DispatcherTimer _timer;
    private string? _runId;
    private RunSnapshotInfo? _snapshot;
    private TaskProjectionInfo? _projection;
    private bool _pollingEnabled = true;
    private Task? _inFlight;

    public RunStatusMonitor(IRunController controller)
    {
        _controller = controller;
        _timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
        _timer.Tick += (_, _) => _ = RefreshAsync();
    }

    /// <summary>Raised after every successful/attempted refresh (consumers re-read Snapshot/Projection).</summary>
    public event EventHandler? Updated;

    public string? RunId => _runId;

    public bool IsActive => !string.IsNullOrEmpty(_runId);

    public RunSnapshotInfo? Snapshot => _snapshot;

    public TaskProjectionInfo? Projection => _projection;

    public bool HasSnapshot => _snapshot is not null;

    /// <summary>True while the shared poller is running (tests can pause it for determinism).</summary>
    public bool IsPollingEnabled => _pollingEnabled;

    public string StatusText
    {
        get
        {
            var status = _projection?.RunStatus ?? _snapshot?.Status;
            return string.IsNullOrEmpty(status) ? "状态未知" : RunStateText(status);
        }
    }

    public NmStatus Status
    {
        get
        {
            var status = _projection?.RunStatus ?? _snapshot?.Status;
            return RunStateStatus(status ?? string.Empty);
        }
    }

    public string SummaryText
    {
        get
        {
            if (!IsActive)
            {
                return "无活动 Run";
            }

            var progress = _projection?.OverallProgress is { } value ? $" · {value:P0}" : string.Empty;
            return $"Run · {StatusText}{progress} · {_runId}";
        }
    }

    /// <summary>Tracks a run id (null clears). The shared poller starts/stops accordingly.</summary>
    public void Track(string? runId)
    {
        var normalized = string.IsNullOrWhiteSpace(runId) ? null : runId.Trim();
        if (string.Equals(_runId, normalized, StringComparison.Ordinal))
        {
            return;
        }

        _runId = normalized;
        _snapshot = null;
        _projection = null;
        OnPropertyChanged(
            nameof(RunId),
            nameof(IsActive),
            nameof(Snapshot),
            nameof(Projection),
            nameof(HasSnapshot),
            nameof(StatusText),
            nameof(Status),
            nameof(SummaryText));

        if (_runId is null)
        {
            StopTimer();
            Updated?.Invoke(this, EventArgs.Empty);
            return;
        }

        if (_pollingEnabled)
        {
            StartTimer();
        }

        _ = RefreshAsync();
    }

    /// <summary>Disables automatic polling (tests / explicit refresh only) without clearing the tracked run.</summary>
    public void SetPollingEnabled(bool enabled)
    {
        if (_pollingEnabled == enabled)
        {
            return;
        }

        _pollingEnabled = enabled;
        if (!enabled)
        {
            StopTimer();
        }
        else if (IsActive)
        {
            StartTimer();
        }
    }

    /// <summary>
    /// One shared refresh of snapshot + projection (never throws into the UI). Concurrent callers share
    /// the in-flight task, so two consumers (StatusBand + Console) can never double-read the Host (R-24).
    /// </summary>
    public Task RefreshAsync()
    {
        if (_runId is null)
        {
            return Task.CompletedTask;
        }

        if (_inFlight is { IsCompleted: false } running)
        {
            return running;
        }

        _inFlight = RefreshCoreAsync();
        return _inFlight;
    }

    private async Task RefreshCoreAsync()
    {
        var runId = _runId!;
        try
        {
            var snapshot = await _controller.GetRunSnapshotAsync(runId).ConfigureAwait(true);
            if (!string.Equals(_runId, runId, StringComparison.Ordinal))
            {
                return;
            }

            var projection = snapshot is null
                ? null
                : await _controller.GetTaskProjectionAsync(runId).ConfigureAwait(true);
            if (!string.Equals(_runId, runId, StringComparison.Ordinal))
            {
                return;
            }

            _snapshot = snapshot;
            _projection = projection;
            OnPropertyChanged(
                nameof(Snapshot),
                nameof(Projection),
                nameof(HasSnapshot),
                nameof(StatusText),
                nameof(Status),
                nameof(SummaryText));
        }
        catch (Exception exception) when (exception is InvalidOperationException or SidecarException)
        {
            _snapshot = null;
            _projection = null;
            OnPropertyChanged(
                nameof(Snapshot),
                nameof(Projection),
                nameof(HasSnapshot),
                nameof(StatusText),
                nameof(Status),
                nameof(SummaryText));
        }
        finally
        {
            _inFlight = null;
            Updated?.Invoke(this, EventArgs.Empty);
        }
    }

    public void Dispose()
    {
        StopTimer();
    }

    private void StartTimer()
    {
        if (!_timer.IsEnabled)
        {
            _timer.Start();
        }
    }

    private void StopTimer()
    {
        if (_timer.IsEnabled)
        {
            _timer.Stop();
        }
    }

    /// <summary>Core run states → the frozen seven-state UI language (never a fabricated state).</summary>
    public static NmStatus RunStateStatus(string state) => state switch
    {
        "completed" or "done" => NmStatus.Done,
        "running" or "processing" => NmStatus.Running,
        "failed" or "error" => NmStatus.Failed,
        "blocked" => NmStatus.Blocked,
        "waiting" or "pending" or "queued" => NmStatus.Queued,
        "skipped" => NmStatus.Skipped,
        "stale" => NmStatus.Stale,
        _ => NmStatus.NotStarted,
    };

    public static string RunStateText(string state) => state switch
    {
        "completed" or "done" => "已完成",
        "running" or "processing" => "进行中",
        "failed" or "error" => "失败",
        "blocked" => "阻塞",
        "waiting" or "pending" or "queued" => "等待",
        "skipped" => "跳过",
        "cancelled" or "canceled" or "stopped" => "已取消",
        "paused" => "已暂停",
        "stale" => "过期",
        _ => string.IsNullOrEmpty(state) ? "未知" : state,
    };
}
