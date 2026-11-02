namespace NewManga.ApplicationCore;

public enum DraftBufferStatus
{
    Active,
    Flushed,
    Discarded,
    Conflicted
}

public enum DraftFlushTrigger
{
    Debounce,
    PageChange,
    WorkspaceSwitch,
    Exit,
    WindowClose,
    RunSubmit
}

public sealed record DraftPatch(
    IReadOnlyDictionary<string, object?>? Text = null,
    IReadOnlyDictionary<string, object?>? Geometry = null,
    IReadOnlyDictionary<string, object?>? Style = null,
    int? UndoCursor = null)
{
    public IReadOnlyDictionary<string, object?> ToMap()
    {
        var result = new Dictionary<string, object?>(StringComparer.Ordinal);
        if (Text is not null) result["text"] = Text;
        if (Geometry is not null) result["geometry"] = Geometry;
        if (Style is not null) result["style"] = Style;
        return result;
    }
}

/// <summary>The eleven SC-D01 fields projected into the local UI buffer.</summary>
public sealed record DraftSnapshot(
    string DraftId,
    string SessionId,
    string PageId,
    string? RegionId,
    string? BaseRevisionId,
    int PageBindingVersion,
    int DraftSequence,
    IReadOnlyDictionary<string, object?> Patch,
    int UndoCursor,
    DateTimeOffset SavedAt,
    DraftBufferStatus Status)
{
    public static DraftSnapshot Create(
        string draftId, string sessionId, string pageId, string? regionId,
        string? baseRevisionId, int pageBindingVersion, DateTimeOffset? now = null) =>
        new(draftId, sessionId, pageId, regionId, baseRevisionId, pageBindingVersion,
            0, new Dictionary<string, object?>(StringComparer.Ordinal), 0,
            now ?? DateTimeOffset.UtcNow, DraftBufferStatus.Active);

    public DraftSnapshot Apply(DraftPatch patch)
    {
        var merged = Patch.ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);
        MergeDomain(merged, "text", patch.Text, replace: true);
        MergeDomain(merged, "geometry", patch.Geometry, replace: false);
        MergeDomain(merged, "style", patch.Style, replace: false);
        return this with
        {
            DraftSequence = checked(DraftSequence + 1),
            Patch = merged,
            UndoCursor = patch.UndoCursor ?? UndoCursor,
            Status = DraftBufferStatus.Active
        };
    }

    private static void MergeDomain(
        IDictionary<string, object?> target,
        string domain,
        IReadOnlyDictionary<string, object?>? update,
        bool replace)
    {
        if (update is null) return;
        if (replace)
        {
            target[domain] = update.ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);
            return;
        }
        var merged = target.TryGetValue(domain, out var existing) &&
            existing is IReadOnlyDictionary<string, object?> oldMap
                ? oldMap.ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal)
                : new Dictionary<string, object?>(StringComparer.Ordinal);
        foreach (var pair in update) merged[pair.Key] = pair.Value;
        target[domain] = merged;
    }
}

public sealed record DraftFlushOutcome(
    bool Succeeded,
    DraftSnapshot Snapshot,
    string? ErrorCode = null);

/// <summary>
/// UI-local draft projection with one serialized patch queue and an injectable flush seam.
/// This class has no Host, IPC or CoreClient dependency.
/// </summary>
public sealed class DraftBuffer : IAsyncDisposable
{
    public static readonly TimeSpan DefaultDebounce = TimeSpan.FromMilliseconds(400);

    private readonly SemaphoreSlim _queue = new(1, 1);
    private readonly object _stateGate = new();
    private readonly Func<DraftSnapshot, CancellationToken, Task> _flush;
    private readonly TimeSpan _debounce;
    private DraftSnapshot _snapshot;
    private CancellationTokenSource? _debounceCancellation;
    private bool _disposed;

    public DraftBuffer(
        DraftSnapshot initial,
        Func<DraftSnapshot, CancellationToken, Task> flush,
        TimeSpan? debounce = null)
    {
        ArgumentNullException.ThrowIfNull(initial);
        ArgumentNullException.ThrowIfNull(flush);
        _snapshot = initial;
        _flush = flush;
        _debounce = debounce ?? DefaultDebounce;
        if (_debounce < TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(debounce));
    }

    public DraftSnapshot Snapshot
    {
        get { lock (_stateGate) return _snapshot; }
    }

    public async Task<DraftSnapshot> ApplyPatchAsync(
        DraftPatch patch, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(patch);
        await _queue.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            lock (_stateGate) _snapshot = _snapshot.Apply(patch);
            ScheduleDebouncedFlush();
            return Snapshot;
        }
        finally
        {
            _queue.Release();
        }
    }

    public async Task<DraftFlushOutcome> FlushAsync(
        DraftFlushTrigger trigger, CancellationToken cancellationToken = default)
    {
        if (trigger == DraftFlushTrigger.Debounce)
            throw new ArgumentException("Debounce is an internal trigger", nameof(trigger));
        CancelDebounce();
        return await FlushCoreAsync(trigger, cancellationToken).ConfigureAwait(false);
    }

    private async Task<DraftFlushOutcome> FlushCoreAsync(
        DraftFlushTrigger trigger, CancellationToken cancellationToken)
    {
        await _queue.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            DraftSnapshot current;
            lock (_stateGate) current = _snapshot;
            try
            {
                await _flush(current, cancellationToken).ConfigureAwait(false);
                lock (_stateGate)
                {
                    _snapshot = _snapshot with
                    {
                        SavedAt = DateTimeOffset.UtcNow,
                        Status = DraftBufferStatus.Flushed
                    };
                    return new(true, _snapshot);
                }
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                throw;
            }
            catch
            {
                lock (_stateGate)
                {
                    _snapshot = _snapshot with { Status = DraftBufferStatus.Conflicted };
                    return new(false, _snapshot, "DRAFT_FLUSH_FAILED");
                }
            }
        }
        finally
        {
            _queue.Release();
        }
    }

    private void ScheduleDebouncedFlush()
    {
        CancellationToken token;
        lock (_stateGate)
        {
            _debounceCancellation?.Cancel();
            _debounceCancellation?.Dispose();
            _debounceCancellation = new CancellationTokenSource();
            token = _debounceCancellation.Token;
        }
        _ = DebouncedFlushAsync(token);
    }

    private async Task DebouncedFlushAsync(CancellationToken token)
    {
        try
        {
            await Task.Delay(_debounce, token).ConfigureAwait(false);
            await FlushCoreAsync(DraftFlushTrigger.Debounce, token).ConfigureAwait(false);
        }
        catch (OperationCanceledException) { }
    }

    private void CancelDebounce()
    {
        lock (_stateGate)
        {
            _debounceCancellation?.Cancel();
            _debounceCancellation?.Dispose();
            _debounceCancellation = null;
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed) return;
        var outcome = await FlushAsync(DraftFlushTrigger.WindowClose).ConfigureAwait(false);
        _ = outcome;
        _disposed = true;
        CancelDebounce();
        _queue.Dispose();
    }
}
