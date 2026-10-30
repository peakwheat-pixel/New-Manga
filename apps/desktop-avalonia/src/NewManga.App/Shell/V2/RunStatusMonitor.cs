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

    /// <summary>
    /// REALUSE-DATA-SAFETY-3 AC2 (audit MA-07): the Console's "任务与队列" section required the user
    /// to type a run_id by hand because the frozen contract has no "list runs" command. Remembering
    /// the run ids this session has actually seen is not a fabricated list — every entry came from a
    /// real StartRun or an explicit load — and it is what makes the section usable without copying
    /// ids out of another window. Most recent first, bounded.
    /// </summary>
    private readonly List<string> _knownRunIds = new();

    private const int MaxKnownRunIds = 12;

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

    /// <summary>
    /// REALUSE-DATA-SAFETY-3 AC2: run ids this session has tracked (most recent first, at most
    /// <see cref="MaxKnownRunIds"/>). Purely a memory aid — it never invents an id and never claims
    /// a run still exists; loading one goes through the normal Host read.
    /// </summary>
    public IReadOnlyList<string> KnownRunIds => _knownRunIds;

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
        // Review r1 M5: remembering here meant a typo was cached as a run the session had "seen",
        // shown as a chip forever while polling a run that does not exist. Only a run the Host
        // actually answers for (RefreshCoreAsync) or a Run the app just created (RememberRunId)
        // enters the list.
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

    /// <summary>
    /// REALUSE-DATA-SAFETY-3 AC2: records a run the application itself just created (StartRun
    /// returned it), so it is offered in the Console list before the first read round-trip.
    /// </summary>
    public void RememberRunId(string runId)
    {
        if (RememberRun(string.IsNullOrWhiteSpace(runId) ? null : runId.Trim()))
        {
            OnPropertyChanged(nameof(KnownRunIds));
        }
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-3 AC2: records a run id the session has actually seen (most recent
    /// first, de-duplicated, bounded). Returns true when the list actually changed.
    /// </summary>
    private bool RememberRun(string? runId)
    {
        if (runId is null)
        {
            return false;
        }

        var existing = _knownRunIds.IndexOf(runId);
        if (existing == 0)
        {
            return false;
        }

        if (existing > 0)
        {
            _knownRunIds.RemoveAt(existing);
        }

        _knownRunIds.Insert(0, runId);
        while (_knownRunIds.Count > MaxKnownRunIds)
        {
            _knownRunIds.RemoveAt(_knownRunIds.Count - 1);
        }

        return true;
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
            if (snapshot is not null && RememberRun(runId))
            {
                // The Host returned this run, so it is real: safe to remember and to offer as a chip.
                OnPropertyChanged(nameof(KnownRunIds));
            }

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

    /// <summary>
    /// Core run states → the frozen seven-state UI language (never a fabricated state).
    /// REALUSE-DATA-SAFETY-3 AC4 (audit MA-10): the enum values come from
    /// <c>src/application/tasks/projection.py</c>; <c>completed_with_failures</c> and
    /// <c>interrupted</c> used to fall through to NotStarted while the raw value leaked into the UI.
    /// A run that finished with failed pages counts as Done (it did finish) but its label says so.
    /// </summary>
    public static NmStatus RunStateStatus(string state) => state switch
    {
        "completed" or "done" or "completed_with_failures" => NmStatus.Done,
        "running" or "processing" => NmStatus.Running,
        "failed" or "error" or "interrupted" => NmStatus.Failed,
        "blocked" => NmStatus.Blocked,
        "waiting" or "pending" or "queued" or "paused" => NmStatus.Queued,
        "skipped" => NmStatus.Skipped,
        "stale" => NmStatus.Stale,
        _ => NmStatus.NotStarted,
    };

    public static string RunStateText(string state) => state switch
    {
        "completed" or "done" => "已完成",
        "completed_with_failures" => "已完成（有失败页）",
        "running" or "processing" => "进行中",
        "failed" or "error" => "失败",
        "interrupted" => "已中断",
        "blocked" => "阻塞",
        "waiting" or "pending" or "queued" => "等待",
        "skipped" => "跳过",
        "cancelled" or "canceled" or "stopped" => "已取消",
        "paused" => "已暂停",
        "stale" => "过期",
        _ => string.IsNullOrEmpty(state) ? "未知" : state,
    };

    /// <summary>
    /// REALUSE-DATA-SAFETY-3 AC4 (audit MA-10): Core step error codes are upper-snake identifiers
    /// (<c>src/application/**</c>); the UI used to print them verbatim. Known codes get a Chinese
    /// explanation, unknown ones keep their code so the failure stays diagnosable — never a generic
    /// "出错了".
    /// </summary>
    public static string StepErrorText(string? code)
    {
        if (string.IsNullOrWhiteSpace(code))
        {
            return "无错误码";
        }

        var explanation = code switch
        {
            "PROVIDER_NOT_CONFIGURED" => "未配置模型 Provider",
            "PROVIDER_UNKNOWN" => "未知的模型 Provider",
            "PROVIDER_RATE_LIMITED" or "RATE_LIMITED" => "Provider 限流，请稍后重试",
            "MISSING_REQUIRED_INPUT" => "缺少必要输入（前置步骤未完成）",
            "OUTPUT_MAPPING_MISMATCH" => "步骤输出映射不一致",
            "ARTIFACT_WRITE_FAILED" => "产物写入失败",
            "ARTIFACT_HASH_MISMATCH" => "产物校验不一致",
            "EXPORT_WRITE_FAILED" => "导出写入失败",
            "COMPOSITION_BASE_CHANGED" => "合成底图已变化，需要重新渲染",
            "TARGET_NOT_FOUND" => "目标不存在",
            _ => null,
        };

        return explanation is null ? code : $"{explanation}（{code}）";
    }
}
