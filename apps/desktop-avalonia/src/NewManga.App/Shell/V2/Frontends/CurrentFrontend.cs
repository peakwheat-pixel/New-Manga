using System.Runtime.CompilerServices;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.ApplicationCore;

namespace NewManga.App.Shell.V2.Frontends;

/// <summary>One immutable read round for one Run, shared by every Current consumer.</summary>
public sealed record CurrentRunView(
    RunSnapshotInfo Snapshot,
    TaskProjectionInfo? Projection,
    StudioRunProjection? StudioProjection);

/// <summary>The structured result of the read-only Current-to-next-frontend preflight.</summary>
public sealed record PreflightBlocker(string Code, string Source, string Detail);

public sealed record CurrentPreflightResult(bool Allowed, IReadOnlyList<PreflightBlocker> Blockers);

/// <summary>Explicit state inputs are also a deterministic seam for proving each frozen blocker.</summary>
public sealed record CurrentPreflightSignals(
    bool PendingRegionType = false,
    bool PendingConfirmation = false,
    bool UnacknowledgedRunKey = false,
    bool UnmappedReaderAnchor = false,
    bool UnmappedShellState = false);

/// <summary>
/// In-app Current façade. It owns no Host lifetime and starts no work. All Run reads go through one
/// ApplicationCore RunMonitor; the rest of this type forwards existing seams and maps UI mementos.
/// </summary>
public sealed class CurrentFrontend
{
    private static readonly ConditionalWeakTable<IRunController, CurrentFrontend> Instances = new();
    private static readonly object ActiveGate = new();
    private static WeakReference<CurrentFrontend>? _active;
    private readonly object _draftGate = new();
    private readonly Dictionary<(string PageId, string RegionId), DraftBuffer> _regionDrafts = new();

    private CurrentFrontend(IRunController controller)
    {
        Controller = controller;
        Session = new CurrentSessionMemento();
        RunMonitor = new RunMonitor<CurrentRunView>(ReadRunAsync, TimeSpan.FromSeconds(1));
        RunIntents = new CurrentRunIntentCoordinator();
    }

    /// <summary>Read-only bridge for Theme Studio: Current only records whether its draft maps losslessly.</summary>
    public static CurrentFrontend? Active
    {
        get
        {
            lock (ActiveGate) return _active is not null && _active.TryGetTarget(out var current) ? current : null;
        }
    }

    public static void Activate(CurrentFrontend current)
    {
        ArgumentNullException.ThrowIfNull(current);
        lock (ActiveGate) _active = new WeakReference<CurrentFrontend>(current);
    }

    public static void UpdateAppearanceDraft(bool isDirty, string? draftKey, string? draftValue)
    {
        var appearance = Active?.Session.Appearance;
        if (appearance is null) return;
        appearance.IsDirty = isDirty;
        appearance.IsMapped = !isDirty;
        appearance.DraftKey = draftKey;
        appearance.DraftValue = draftValue;
    }

    public static CurrentFrontend For(IRunController controller)
    {
        ArgumentNullException.ThrowIfNull(controller);
        return Instances.GetValue(controller, static key => new CurrentFrontend(key));
    }

    public IRunController Controller { get; }

    public IHostController? HostController => Controller as IHostController;

    public CurrentSessionMemento Session { get; }

    public RunMonitor<CurrentRunView> RunMonitor { get; }

    public CurrentRunIntentCoordinator RunIntents { get; }

    /// <summary>Raised by the shared monitor after a Run read; callbacks may arrive off the UI thread.</summary>
    public event EventHandler<CurrentRunObservedEventArgs>? RunObserved;

    /// <summary>Creates new view content over the same session memento and Host instance.</summary>
    public ShellState CreateShellState() => new(Session.Shell);

    public CurrentRunView? GetRun(string? runId)
    {
        if (string.IsNullOrWhiteSpace(runId)) return null;
        return RunMonitor.State.GetSnapshot(runId)?.Value;
    }

    public IDisposable SubscribeRun(string runId, Action<CurrentRunView?> observer)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(runId);
        ArgumentNullException.ThrowIfNull(observer);
        return RunMonitor.Subscribe(runId, observation =>
        {
            var value = observation.Snapshot?.Value;
            if (value is not null) Session.RememberRunId(runId);
            RunObserved?.Invoke(this, new CurrentRunObservedEventArgs(runId, value));
            observer(value);
        });
    }

    public Task<RequestResult<CurrentRunView>> RefreshRunAsync(
        string runId,
        CancellationToken cancellationToken = default) =>
        RunMonitor.RefreshAsync(runId, cancellationToken);

    public string? PendingRunIntentKey => RunIntents.PendingKey;

    public Task<RunStartInfo?> ExecuteRunStartAsync(
        RunStartRequest request,
        CancellationToken cancellationToken = default) =>
        RunIntents.ExecuteAsync(
            (key, token) => Controller.StartRunAsync(request with { IdempotencyKey = key }, token),
            cancellationToken);

    /// <summary>
    /// Pure preflight. It reads only session mementos and local buffers; it never calls the Host/Core.
    /// S5 filters and monitor selection are rebuildable UI state, so they do not create a blocker.
    /// </summary>
    public CurrentPreflightResult Preflight(CurrentPreflightSignals? signals = null)
    {
        var state = signals ?? new CurrentPreflightSignals(
            PendingRegionType: HasPendingRegionTypeDraft,
            PendingConfirmation: Session.Studio.HasPendingConfirmation,
            UnacknowledgedRunKey: RunIntents.PendingKey is not null,
            UnmappedReaderAnchor: Session.Reader.HasAnchor && !Session.Reader.AnchorMapped,
            UnmappedShellState: Session.Shell.HasUnmappedState ||
                (Session.Appearance.IsDirty && !Session.Appearance.IsMapped));

        var blockers = new List<PreflightBlocker>(5);
        if (state.PendingRegionType)
            blockers.Add(new("PENDING_REGION_TYPE", "S1", "Region type 草稿尚未确认保存或放弃。"));
        if (state.PendingConfirmation)
            blockers.Add(new("PENDING_CONFIRMATION", "S2", "Studio 存在未决确认；preflight 不会替用户执行。"));
        if (state.UnacknowledgedRunKey)
            blockers.Add(new("UNFLUSHED_RUN_KEY", "S3", "Run intent 尚未收到可确认的结果。"));
        if (state.UnmappedReaderAnchor)
            blockers.Add(new("UNMAPPED_READER_ANCHOR", "S4", "Reader 的 page ID / 语义锚点无法无损映射。"));
        if (state.UnmappedShellState)
            blockers.Add(new("UNMAPPED_SHELL_STATE", "S6", "Shell 或 Appearance draft 中存在未映射编辑。"));

        return new(blockers.Count == 0, blockers.AsReadOnly());
    }

    public DraftBuffer GetRegionTypeDraft(string pageId, string regionId, int baseRevision) =>
        GetRegionTypeDraft(pageId, regionId, baseRevision, null);

    /// <summary>Optional local journal seam; Current never supplies a Host/Core writer.</summary>
    public DraftBuffer GetRegionTypeDraft(
        string pageId,
        string regionId,
        int baseRevision,
        Func<DraftSnapshot, CancellationToken, Task>? flush)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(pageId);
        ArgumentException.ThrowIfNullOrWhiteSpace(regionId);
        var key = (pageId, regionId);
        lock (_draftGate)
        {
            if (_regionDrafts.TryGetValue(key, out var existing)) return existing;
            var snapshot = DraftSnapshot.Create(
                Guid.NewGuid().ToString("N"), "current", pageId, regionId, baseRevision.ToString(), 1);
            // DraftBuffer is the local authority. The adapter's local flush has no Host/Core writer;
            // the existing SetRegionType command is called only by the explicit Save action.
            var localFlush = flush ?? (static (_, _) => Task.CompletedTask);
            DraftBuffer? buffer = null;
            buffer = new DraftBuffer(snapshot, async (draft, token) =>
            {
                lock (_draftGate)
                {
                    if (!_regionDrafts.TryGetValue(key, out var registered) || !ReferenceEquals(registered, buffer)) return;
                }
                await localFlush(draft, token).ConfigureAwait(false);
            }, TimeSpan.FromDays(30));
            _regionDrafts.Add(key, buffer);
            return buffer;
        }
    }

    public bool TryGetRegionTypeDraft(string pageId, string regionId, out DraftBuffer? buffer)
    {
        lock (_draftGate) return _regionDrafts.TryGetValue((pageId, regionId), out buffer);
    }

    public string? ReadPendingRegionType(string pageId, string regionId, int baseRevision)
    {
        if (!TryGetRegionTypeDraft(pageId, regionId, out var buffer) || buffer is null) return null;
        var snapshot = buffer.Snapshot;
        if (!snapshot.Patch.TryGetValue("style", out var style) ||
            style is not IReadOnlyDictionary<string, object?> values ||
            !values.TryGetValue("regionType", out var value))
            return null;
        return value as string;
    }

    public bool HasPendingRegionTypeDraft
    {
        get
        {
            lock (_draftGate)
            {
                return _regionDrafts.Values.Any(buffer =>
                    buffer.Snapshot.Status != DraftBufferStatus.Flushed &&
                    buffer.Snapshot.Patch.TryGetValue("style", out var style) &&
                    style is IReadOnlyDictionary<string, object?> values &&
                    values.ContainsKey("regionType"));
            }
        }
    }

    public void ClearRegionTypeDraft(string pageId, string regionId)
    {
        DraftBuffer? removed;
        lock (_draftGate)
        {
            if (!_regionDrafts.Remove((pageId, regionId), out removed)) return;
        }
        // DisposeAsync flushes by contract. The adapter flush checks registration first, so a
        // detached (discarded or already saved) draft is released without persisting it.
        if (removed is not null) _ = removed.DisposeAsync();
    }

    private async Task<CurrentRunView> ReadRunAsync(string runId, CancellationToken cancellationToken)
    {
        var snapshot = await Controller.GetRunSnapshotAsync(runId, cancellationToken).ConfigureAwait(false);
        if (snapshot is null) throw new InvalidOperationException("Run snapshot is unavailable.");
        var projection = await Controller.GetTaskProjectionAsync(runId, cancellationToken).ConfigureAwait(false);
        return new(snapshot, projection, projection is null ? null : RunControllerRunDataSource.Map(projection));
    }
}

public sealed class CurrentRunObservedEventArgs(string runId, CurrentRunView? value) : EventArgs
{
    public string RunId { get; } = runId;
    public CurrentRunView? Value { get; } = value;
}

/// <summary>ApplicationCore idempotency coordinator plus the one outstanding UI acknowledgement key.</summary>
public sealed class CurrentRunIntentCoordinator
{
    private readonly object _gate = new();
    private readonly IntentCoordinator<RunStartAck> _coordinator = new();
    private string? _pendingKey;

    public string? PendingKey
    {
        get { lock (_gate) return _pendingKey; }
    }

    public async Task<RunStartInfo?> ExecuteAsync(
        Func<string, CancellationToken, Task<RunStartInfo?>> operation,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(operation);
        string key;
        lock (_gate) key = _pendingKey ??= Guid.NewGuid().ToString("N");

        var result = await _coordinator.ExecuteAsync(
            key,
            async (intentKey, token) => new RunStartAck(await operation(intentKey, token).ConfigureAwait(false)),
            cancellationToken).ConfigureAwait(false);
        if (!result.IsSuccess) return null;

        lock (_gate)
        {
            if (string.Equals(_pendingKey, key, StringComparison.Ordinal)) _pendingKey = null;
        }
        return result.Value?.Run;
    }

    private sealed record RunStartAck(RunStartInfo? Run);
}
