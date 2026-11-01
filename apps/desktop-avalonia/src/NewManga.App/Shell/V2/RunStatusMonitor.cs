using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.CoreClient.Diagnostics;
using NewManga.App.Shell.V2.Frontends;

namespace NewManga.App.Shell.V2;

/// <summary>
/// Current's dispatcher adapter over the application-owned ApplicationCore RunMonitor. This type
/// keeps the existing shell API but owns no poll loop, snapshot, projection, or Host lifecycle.
/// </summary>
public sealed class RunStatusMonitor : ObservableObject, IDisposable
{
    private readonly CurrentFrontend _current;
    private IDisposable? _subscription;
    private bool _pollingEnabled = true;

    public RunStatusMonitor(IRunController controller) : this(CurrentFrontend.For(controller)) { }

    public RunStatusMonitor(CurrentFrontend current)
    {
        _current = current ?? throw new ArgumentNullException(nameof(current));
        _pollingEnabled = _current.Session.Console.PollingPreferred;
        EnsureSubscription();
    }

    public event EventHandler? Updated;

    public CurrentFrontend Current => _current;

    private string? _runId => _current.Session.Console.TrackedRunId;

    public string? RunId => _runId;

    public bool IsActive => !string.IsNullOrEmpty(_runId);

    public RunSnapshotInfo? Snapshot => _current.GetRun(_runId)?.Snapshot;

    public TaskProjectionInfo? Projection => _current.GetRun(_runId)?.Projection;

    public bool HasSnapshot => Snapshot is not null;

    public IReadOnlyList<string> KnownRunIds => _current.Session.KnownRunIds;

    public bool IsPollingEnabled => _pollingEnabled;

    public string StatusText
    {
        get
        {
            var status = Projection?.RunStatus ?? Snapshot?.Status;
            return string.IsNullOrEmpty(status) ? "状态未知" : RunStateText(status);
        }
    }

    public NmStatus Status
    {
        get
        {
            var status = Projection?.RunStatus ?? Snapshot?.Status;
            return RunStateStatus(status ?? string.Empty);
        }
    }

    public string SummaryText
    {
        get
        {
            if (!IsActive) return "无活动 Run";
            var progress = Projection?.OverallProgress is { } value ? $" · {value:P0}" : string.Empty;
            return $"Run · {StatusText}{progress} · {_runId}";
        }
    }

    /// <summary>Tracks a Run through the shared ApplicationCore monitor.</summary>
    public void Track(string? runId)
    {
        var normalized = string.IsNullOrWhiteSpace(runId) ? null : runId.Trim();
        if (string.Equals(_runId, normalized, StringComparison.Ordinal)) return;

        ReleaseSubscription();
        _current.Session.Console.TrackedRunId = normalized;
        EnsureSubscription();
        RaiseRunProperties();
        if (normalized is null) Updated?.Invoke(this, EventArgs.Empty);
        else _ = RefreshAsync();
    }

    public void RememberRunId(string runId)
    {
        if (string.IsNullOrWhiteSpace(runId)) return;
        var before = _current.Session.KnownRunIds.ToArray();
        _current.Session.RememberRunId(runId.Trim());
        if (!before.SequenceEqual(_current.Session.KnownRunIds, StringComparer.Ordinal))
            OnPropertyChanged(nameof(KnownRunIds));
    }

    public void SetPollingEnabled(bool enabled)
    {
        if (_pollingEnabled == enabled) return;
        _pollingEnabled = enabled;
        _current.Session.Console.PollingPreferred = enabled;
        if (enabled) EnsureSubscription();
        else ReleaseSubscription();
        OnPropertyChanged(nameof(IsPollingEnabled));
    }

    public async Task RefreshAsync()
    {
        if (_runId is not { } runId) return;
        if (!_pollingEnabled)
        {
            using var oneShot = _current.SubscribeRun(runId, _ => { });
            await RefreshAndNotifyAsync(runId).ConfigureAwait(true);
            return;
        }

        EnsureSubscription();
        await RefreshAndNotifyAsync(runId).ConfigureAwait(true);
    }

    private async Task RefreshAndNotifyAsync(string runId)
    {
        await _current.RefreshRunAsync(runId).ConfigureAwait(true);
        NotifyRunUpdated(runId);
    }

    private void EnsureSubscription()
    {
        if (!_pollingEnabled || _runId is not { } runId || _subscription is not null) return;
        _subscription = _current.SubscribeRun(runId, _ => NotifyRunUpdated(runId));
    }

    private void ReleaseSubscription()
    {
        _subscription?.Dispose();
        _subscription = null;
    }

    private void NotifyRunUpdated(string runId)
    {
        void Update()
        {
            if (!string.Equals(_runId, runId, StringComparison.Ordinal)) return;
            RaiseRunProperties();
            Updated?.Invoke(this, EventArgs.Empty);
        }

        if (Dispatcher.UIThread.CheckAccess()) Update();
        else Dispatcher.UIThread.Post(Update);
    }

    private void RaiseRunProperties() => OnPropertyChanged(
        nameof(RunId), nameof(IsActive), nameof(Snapshot), nameof(Projection), nameof(HasSnapshot),
        nameof(StatusText), nameof(Status), nameof(SummaryText));

    public void Dispose() => ReleaseSubscription();

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
