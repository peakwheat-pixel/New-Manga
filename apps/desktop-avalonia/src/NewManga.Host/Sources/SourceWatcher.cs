using System.IO;

namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11-WATCH-1 (AC-W5): the injectable watcher tunables. Invalid values are normalised to the
/// frozen defaults (fail-safe: a bad option never fails Host startup), and every value has a testable
/// boundary.
/// </summary>
public sealed record SourceWatchOptions
{
    public const int DefaultMaxWatches = 256;
    public const int MinimumMaxWatches = 1;
    public const int MaximumMaxWatches = 4096;
    public const int DefaultInternalBufferBytes = 64 * 1024;
    public const int MinimumInternalBufferBytes = 4 * 1024;
    public const int MaximumInternalBufferBytes = 64 * 1024;
    public const int DefaultDebounceMilliseconds = 2000;
    public const int MinimumDebounceMilliseconds = 250;
    public const int MaximumDebounceMilliseconds = 60_000;

    public bool Enabled { get; init; } = true;

    public int MaxWatches { get; init; } = DefaultMaxWatches;

    public int InternalBufferBytes { get; init; } = DefaultInternalBufferBytes;

    public int DebounceMilliseconds { get; init; } = DefaultDebounceMilliseconds;

    /// <summary>
    /// Clamps every tunable into its frozen range. Illegal values fall back to the default (WARN-level
    /// fail-safe semantics; the watcher is an optimisation, never a correctness dependency).
    /// </summary>
    public SourceWatchOptions Normalized() => this with
    {
        MaxWatches = MaxWatches is >= MinimumMaxWatches and <= MaximumMaxWatches
            ? MaxWatches
            : DefaultMaxWatches,
        // FileSystemWatcher rejects values above 64 KiB and below 4096: clamp instead of throwing.
        InternalBufferBytes = Math.Clamp(InternalBufferBytes, MinimumInternalBufferBytes, MaximumInternalBufferBytes),
        DebounceMilliseconds = DebounceMilliseconds is >= MinimumDebounceMilliseconds
            and <= MaximumDebounceMilliseconds
            ? DebounceMilliseconds
            : DefaultDebounceMilliseconds,
    };
}

/// <summary>
/// FEA-11-WATCH-1 (I-6 testability): the minimal FileSystemWatcher surface the watcher needs. Tests
/// substitute a fake adapter (deterministic events/overflow) while production wraps the real BCL
/// <see cref="FileSystemWatcher"/>; the production behaviour is additionally covered by a real
/// isolated-tree test.
/// </summary>
public interface ISourceWatchHandle : IDisposable
{
    bool EnableRaisingEvents { get; set; }

    int InternalBufferSize { get; set; }

    event FileSystemEventHandler? Changed;

    event FileSystemEventHandler? Created;

    event FileSystemEventHandler? Deleted;

    event RenamedEventHandler? Renamed;

    event ErrorEventHandler? Error;
}

/// <summary>FEA-11-WATCH-1 (I-6): creates one watch handle; injectable for fake-adapter tests.</summary>
public interface ISourceWatchFactory
{
    ISourceWatchHandle Create(string directory, bool includeSubdirectories, string filter, int internalBufferBytes);
}

/// <summary>FEA-11-WATCH-1: production factory over the BCL <see cref="FileSystemWatcher"/>.</summary>
public sealed class FileSystemSourceWatchFactory : ISourceWatchFactory
{
    public ISourceWatchHandle Create(
        string directory, bool includeSubdirectories, string filter, int internalBufferBytes) =>
        new FileSystemSourceWatchHandle(directory, includeSubdirectories, filter, internalBufferBytes);
}

internal sealed class FileSystemSourceWatchHandle : ISourceWatchHandle
{
    private readonly FileSystemWatcher _watcher;

    public FileSystemSourceWatchHandle(
        string directory, bool includeSubdirectories, string filter, int internalBufferBytes)
    {
        _watcher = new FileSystemWatcher(directory)
        {
            IncludeSubdirectories = includeSubdirectories,
            Filter = filter,
            InternalBufferSize = internalBufferBytes,
            NotifyFilter = NotifyFilters.FileName | NotifyFilters.DirectoryName
                | NotifyFilters.LastWrite | NotifyFilters.Size | NotifyFilters.CreationTime,
            EnableRaisingEvents = false,
        };
        _watcher.Changed += (_, args) => Changed?.Invoke(this, args);
        _watcher.Created += (_, args) => Created?.Invoke(this, args);
        _watcher.Deleted += (_, args) => Deleted?.Invoke(this, args);
        _watcher.Renamed += (_, args) => Renamed?.Invoke(this, args);
        _watcher.Error += (_, args) => Error?.Invoke(this, args);
    }

    public bool EnableRaisingEvents
    {
        get => _watcher.EnableRaisingEvents;
        set => _watcher.EnableRaisingEvents = value;
    }

    public int InternalBufferSize
    {
        get => _watcher.InternalBufferSize;
        set => _watcher.InternalBufferSize = value;
    }

    public event FileSystemEventHandler? Changed;

    public event FileSystemEventHandler? Created;

    public event FileSystemEventHandler? Deleted;

    public event RenamedEventHandler? Renamed;

    public event ErrorEventHandler? Error;

    public void Dispose() => _watcher.Dispose();
}

/// <summary>
/// FEA-11-WATCH-1 (I-1..I-5): the Host-side read-only directory watcher. It NEVER reads content and
/// never produces diff/changed/deleted facts — an event only sets a per-source "due" hint on the
/// existing <see cref="SourceScanScheduler"/>, which then runs one full <c>ScanSourceSync</c>
/// re-enumeration (budget/backoff/pause/single-flight all apply). Status is closed and path-free.
///
/// Scope: only roots of the scheduler's currently registered targets are watched, and only after a
/// persistent-registry authorization re-check (registry id / generation / revocation / readable
/// root). A target that cannot be covered is counted as <c>uncovered</c> and stays on the periodic
/// fallback path; watcher errors/overflow are fail-open (periodic scan remains the correctness
/// baseline, hint is only a latency optimisation).
/// </summary>
public sealed class SourceWatcher : IDisposable
{
    /// <summary>Typed reason codes for watcher degradation (status/logs only; never a path).</summary>
    public const string CodeUncovered = "SOURCE_WATCH_UNCOVERED";
    public const string CodeOverflow = "SOURCE_WATCH_OVERFLOW";
    public const string CodeRootLost = "SOURCE_WATCH_ROOT_LOST";
    public const string CodeRegistryUnavailable = "SOURCE_REGISTRY_UNAVAILABLE";
    public const string CodeRevoked = "SOURCE_GRANT_REVOKED";
    public const string CodeGenerationDrift = "SOURCE_REGISTRY_BUSY";
    public const string CodeEntryMissing = "SOURCE_ENTRY_MISSING";

    private readonly object _gate = new();
    private readonly SourceScanScheduler _scheduler;
    private readonly SourceAccessRegistry _registry;
    private readonly SourceWatchOptions _options;
    private readonly TimeProvider _timeProvider;
    private readonly ISourceWatchFactory _factory;
    private readonly Action<string>? _info;
    private readonly Action<string>? _warn;
    private readonly Dictionary<string, WatchSlot> _slots = new(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, DebounceState> _debounce = new(StringComparer.Ordinal);
    private bool _started;
    private bool _disposed;
    private int _uncovered;
    private int _overflowCount;
    private int _debouncedEvents;
    private int _hintCount;
    private bool _degraded;
    private DateTimeOffset? _lastHintAt;

    public SourceWatcher(
        SourceScanScheduler scheduler,
        SourceAccessRegistry registry,
        SourceWatchOptions options,
        TimeProvider timeProvider,
        ISourceWatchFactory? factory = null,
        Action<string>? infoLog = null,
        Action<string>? warnLog = null)
    {
        ArgumentNullException.ThrowIfNull(scheduler);
        ArgumentNullException.ThrowIfNull(registry);
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(timeProvider);
        _scheduler = scheduler;
        _registry = registry;
        _options = options.Normalized();
        _timeProvider = timeProvider;
        _factory = factory ?? new FileSystemSourceWatchFactory();
        _info = infoLog;
        _warn = warnLog;
    }

    /// <summary>FEA-11-WATCH-1 (AC-W1): true while armed; Stop/Dispose make it false and zero future hints.</summary>
    public bool IsStarted
    {
        get { lock (_gate) return _started; }
    }

    /// <summary>
    /// AC-W1: arms the watcher (idempotent) and subscribes to scheduler target-set changes. Only
    /// targets present at arm time and later merged/enumerated targets are covered; nothing else.
    /// </summary>
    public void Start()
    {
        lock (_gate)
        {
            if (_started || _disposed || !_options.Enabled)
            {
                return;
            }

            _started = true;
            _degraded = false;
        }

        _scheduler.TargetSetChanged += OnTargetSetChanged;
        try
        {
            Sync();
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            _warn?.Invoke("source watch arm failed code=" + error.GetType().Name);
        }

        PublishStatus();
        _info?.Invoke("source watch started enabled=" + _options.Enabled
            + " max_watches=" + _options.MaxWatches + " buffer=" + _options.InternalBufferBytes
            + " debounce_ms=" + _options.DebounceMilliseconds);
    }

    /// <summary>AC-W1: idempotent disarm; after this returns no hint can be produced (pending timers are cancelled).</summary>
    public void Stop()
    {
        List<WatchSlot> slots;
        List<DebounceState> pending;
        lock (_gate)
        {
            if (!_started)
            {
                return;
            }

            _started = false;
            slots = _slots.Values.ToList();
            _slots.Clear();
            pending = _debounce.Values.ToList();
            _debounce.Clear();
            _uncovered = 0;
        }

        _scheduler.TargetSetChanged -= OnTargetSetChanged;
        foreach (var debounce in pending)
        {
            debounce.Timer.Dispose();
        }

        foreach (var slot in slots)
        {
            DisposeSlot(slot);
        }
    }

    public void Dispose()
    {
        Stop();
        lock (_gate)
        {
            _disposed = true;
        }
    }

    /// <summary>
    /// AC-W1/AC-W5 status projection: closed, path-free (typed counts/codes only).
    /// </summary>
    public SourceScanWatcherStatus Status()
    {
        lock (_gate)
        {
            return new SourceScanWatcherStatus(
                _options.Enabled,
                _started,
                _slots.Count,
                _uncovered,
                _overflowCount,
                _degraded,
                _lastHintAt,
                _hintCount,
                _debouncedEvents,
                _debounce.Count);
        }
    }

    private void OnTargetSetChanged()
    {
        try
        {
            Sync();
            PublishStatus();
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            _warn?.Invoke("source watch sync failed code=" + error.GetType().Name);
        }
    }

    /// <summary>
    /// Reconciles the armed watches with the scheduler's current target set: newly eligible targets are
    /// armed (registry re-verified), no-longer-present/revoked/replaced targets are disarmed. One
    /// watcher per normalized target path; the same source id never adds a second watcher.
    /// </summary>
    private void Sync()
    {
        IReadOnlyList<SourceScanTarget> targets;
        lock (_gate)
        {
            if (!_started)
            {
                return;
            }
        }

        targets = _scheduler.TargetSnapshot();

        var desired = new Dictionary<string, WatchPlan>(StringComparer.OrdinalIgnoreCase);
        var uncovered = 0;
        foreach (var target in targets)
        {
            if (!TryPlan(target, out var plan, out var reason) || plan is null)
            {
                uncovered++;
                _warn?.Invoke("source watch uncovered source=" + target.SourceId
                    + " code=" + (reason ?? CodeUncovered));
                continue;
            }

            if (desired.TryGetValue(plan.Key, out var existing))
            {
                existing.SourceIds.Add(target.SourceId);
            }
            else
            {
                desired[plan.Key] = plan;
            }
        }

        List<WatchSlot> toDispose = new();
        List<WatchPlan> toArm = new();
        lock (_gate)
        {
            if (!_started)
            {
                return;
            }

            foreach (var pair in _slots.ToList())
            {
                if (!desired.TryGetValue(pair.Key, out var plan)
                    || plan.Folder != pair.Value.Folder
                    || !string.Equals(plan.Directory, pair.Value.Directory, StringComparison.OrdinalIgnoreCase))
                {
                    _slots.Remove(pair.Key);
                    toDispose.Add(pair.Value);
                }
                else
                {
                    pair.Value.SourceIds.IntersectWith(plan.SourceIds);
                    pair.Value.SourceIds.UnionWith(plan.SourceIds);
                }
            }

            foreach (var plan in desired.Values)
            {
                if (_slots.ContainsKey(plan.Key))
                {
                    continue;
                }

                if (_slots.Count + toArm.Count >= _options.MaxWatches)
                {
                    _uncovered++;
                    _warn?.Invoke("source watch uncovered code=" + CodeUncovered + " cap=" + _options.MaxWatches);
                    continue;
                }

                toArm.Add(plan);
            }

            _uncovered += uncovered;
        }

        foreach (var slot in toDispose)
        {
            DisposeSlot(slot);
        }

        foreach (var plan in toArm)
        {
            Arm(plan);
        }
    }

    private bool TryPlan(SourceScanTarget target, out WatchPlan? plan, out string? reason)
    {
        plan = null;
        reason = null;
        SourceAuthorization[] entries;
        try
        {
            entries = _registry.List();
        }
        catch (SourceAccessException error)
        {
            // L-S1: a missing/replaced production file-root makes the persistent registry unreadable;
            // the watcher degrades to the periodic fallback (no watch, no crash, typed only).
            reason = error.Code;
            return false;
        }

        SourceAuthorization? entry;
        string normalized;
        try
        {
            normalized = SourceSecurity.Normalize(target.Path);
        }
        catch (SourceAccessException)
        {
            reason = CodeUncovered;
            return false;
        }

        if (target.IsEnumerated)
        {
            entry = entries.SingleOrDefault(candidate =>
                string.Equals(candidate.RegistryId, target.RegistryId, StringComparison.Ordinal));
            if (entry is null)
            {
                reason = CodeRegistryUnavailable;
                return false;
            }

            if (entry.RevokedAt is not null)
            {
                reason = CodeRevoked;
                return false;
            }

            if (entry.Generation != target.Generation)
            {
                reason = CodeGenerationDrift;
                return false;
            }

            if (!entry.Roots.Any(root => root.Readable && TryNormalize(root.Root, out var rootPath)
                    && string.Equals(rootPath, normalized, StringComparison.OrdinalIgnoreCase)))
            {
                reason = CodeRegistryUnavailable;
                return false;
            }
        }
        else
        {
            entry = entries.FirstOrDefault(candidate =>
                candidate.RevokedAt is null
                && candidate.Roots.Any(root => root.Readable
                    && SourceSecurity.Contains(root.Root, normalized)));
            if (entry is null)
            {
                reason = CodeRegistryUnavailable;
                return false;
            }
        }

        var isDirectory = Directory.Exists(normalized);
        var isFile = File.Exists(normalized);
        var declaredKind = target.SourceKind;
        var declaredFolder = string.Equals(declaredKind, "folder", StringComparison.Ordinal);
        var declaredFile = declaredKind is "image" or "zip" or "cbz" or "pdf";

        if (declaredFolder)
        {
            if (!isDirectory)
            {
                reason = CodeUncovered;
                return false;
            }

            plan = new WatchPlan
            {
                Key = normalized,
                Directory = normalized,
                Folder = true,
                Filter = "*",
                SourceIds = new HashSet<string>(StringComparer.Ordinal) { target.SourceId },
            };
            return true;
        }

        if (declaredFile)
        {
            // AC-W1: a declared file target whose path is now a directory is NOT watched with a guessed
            // file name — it stays uncovered on the periodic fallback path.
            if (!isFile || isDirectory)
            {
                reason = CodeUncovered;
                return false;
            }

            var parent = Path.GetDirectoryName(normalized);
            if (string.IsNullOrEmpty(parent) || !Directory.Exists(parent))
            {
                reason = CodeUncovered;
                return false;
            }

            plan = new WatchPlan
            {
                Key = normalized,
                Directory = parent,
                Folder = false,
                ExactFile = Path.GetFileName(normalized),
                Filter = Path.GetFileName(normalized),
                SourceIds = new HashSet<string>(StringComparer.Ordinal) { target.SourceId },
            };
            return true;
        }

        if (isDirectory)
        {
            plan = new WatchPlan
            {
                Key = normalized,
                Directory = normalized,
                Folder = true,
                Filter = "*",
                SourceIds = new HashSet<string>(StringComparer.Ordinal) { target.SourceId },
            };
            return true;
        }

        if (isFile)
        {
            var parent = Path.GetDirectoryName(normalized);
            if (string.IsNullOrEmpty(parent) || !Directory.Exists(parent))
            {
                reason = CodeUncovered;
                return false;
            }

            plan = new WatchPlan
            {
                Key = normalized,
                Directory = parent,
                Folder = false,
                ExactFile = Path.GetFileName(normalized),
                Filter = Path.GetFileName(normalized),
                SourceIds = new HashSet<string>(StringComparer.Ordinal) { target.SourceId },
            };
            return true;
        }

        reason = CodeEntryMissing;
        return false;
    }

    private void Arm(WatchPlan plan)
    {
        ISourceWatchHandle handle;
        try
        {
            handle = _factory.Create(plan.Directory, plan.Folder, plan.Filter, _options.InternalBufferBytes);
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            lock (_gate) _uncovered++;
            _warn?.Invoke("source watch arm failed code=" + error.GetType().Name);
            return;
        }

        var slot = new WatchSlot
        {
            Key = plan.Key,
            Directory = plan.Directory,
            Folder = plan.Folder,
            ExactFile = plan.ExactFile,
            Handle = handle,
            SourceIds = plan.SourceIds,
        };

        handle.Changed += (_, args) => OnFileEvent(slot, args.FullPath, rootLost: false);
        handle.Created += (_, args) => OnFileEvent(slot, args.FullPath, rootLost: false);
        handle.Deleted += (_, args) => OnFileEvent(slot, args.FullPath, rootLost: true);
        handle.Renamed += (_, args) => OnFileEvent(slot, args.FullPath, rootLost: true);
        handle.Error += (_, args) => OnWatchError(slot);

        var armed = false;
        try
        {
            handle.EnableRaisingEvents = true;
            armed = true;
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            _warn?.Invoke("source watch arm failed code=" + error.GetType().Name);
        }

        if (!armed)
        {
            handle.Dispose();
            lock (_gate) _uncovered++;
            return;
        }

        lock (_gate)
        {
            if (!_started)
            {
                handle.Dispose();
                return;
            }

            _slots[plan.Key] = slot;
        }
    }

    private void OnFileEvent(WatchSlot slot, string fullPath, bool rootLost)
    {
        bool started;
        lock (_gate) started = _started;
        if (!started)
        {
            return;
        }

        string normalized;
        try
        {
            normalized = SourceSecurity.Normalize(fullPath);
        }
        catch (SourceAccessException)
        {
            return;
        }

        if (slot.Folder)
        {
            // A directory-target root that disappeared/renamed itself, or an event for the root, means
            // the coverage is gone: degrade, hint ALL targets and try to re-arm (or count uncovered).
            if (rootLost && string.Equals(normalized, slot.Directory, StringComparison.OrdinalIgnoreCase))
            {
                HandleRootLost(slot);
                return;
            }
        }
        else
        {
            if (slot.ExactFile is null
                || !string.Equals(Path.GetFileName(normalized), slot.ExactFile, StringComparison.OrdinalIgnoreCase))
            {
                return;
            }
        }

        List<string> sourceIds;
        lock (_gate) sourceIds = slot.SourceIds.ToList();
        foreach (var sourceId in sourceIds)
        {
            QueueHint(sourceId);
        }
    }

    private void OnWatchError(WatchSlot slot)
    {
        bool started;
        lock (_gate) started = _started;
        if (!started)
        {
            return;
        }

        // AC-W3: overflow / unknown invalidation is fail-open: no crash, all targets become due (one
        // full re-enumeration request), the affected watch is dropped and re-armed if still coverable.
        lock (_gate)
        {
            _overflowCount++;
            _degraded = true;
        }

        _warn?.Invoke("source watch overflow code=" + CodeOverflow);
        RemoveSlot(slot, countUncovered: false);
        _scheduler.HintAllTargets(CodeOverflow);
        PublishStatus();
        try
        {
            Sync();
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            _warn?.Invoke("source watch rearm failed code=" + error.GetType().Name);
        }
    }

    private void HandleRootLost(WatchSlot slot)
    {
        lock (_gate) _degraded = true;
        _warn?.Invoke("source watch root lost code=" + CodeRootLost);
        RemoveSlot(slot, countUncovered: true);
        _scheduler.HintAllTargets(CodeRootLost);
        PublishStatus();
        try
        {
            Sync();
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            _warn?.Invoke("source watch rearm failed code=" + error.GetType().Name);
        }
    }

    private void RemoveSlot(WatchSlot slot, bool countUncovered)
    {
        lock (_gate)
        {
            if (!_slots.Remove(slot.Key))
            {
                return;
            }

            if (countUncovered)
            {
                _uncovered++;
            }
        }

        DisposeSlot(slot);
    }

    private static void DisposeSlot(WatchSlot slot)
    {
        try
        {
            slot.Handle.EnableRaisingEvents = false;
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            // best effort: a disposed/invalid handle is about to be disposed anyway
        }

        try
        {
            slot.Handle.Dispose();
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            // best effort
        }
    }

    /// <summary>
    /// AC-W2: one debounce window per source. Every event inside the window merges into the single
    /// pending hint; only the elapsed timer calls the scheduler (hint = per-source due bit only —
    /// no path/change type is ever passed along).
    /// </summary>
    private void QueueHint(string sourceId)
    {
        DebounceState? created = null;
        lock (_gate)
        {
            if (!_started || string.IsNullOrWhiteSpace(sourceId))
            {
                return;
            }

            _debouncedEvents++;
            if (_debounce.TryGetValue(sourceId, out var existing))
            {
                existing.Events++;
                return;
            }

            var state = new DebounceState { Events = 1 };
            state.Timer = _timeProvider.CreateTimer(
                _ => OnDebounceElapsed(sourceId, state),
                state,
                TimeSpan.FromMilliseconds(_options.DebounceMilliseconds),
                Timeout.InfiniteTimeSpan);
            _debounce[sourceId] = state;
            created = state;
        }

        if (created is not null)
        {
            PublishStatus();
        }
    }

    private void OnDebounceElapsed(string sourceId, DebounceState state)
    {
        lock (_gate)
        {
            if (!_started || !_debounce.TryGetValue(sourceId, out var current) || !ReferenceEquals(current, state))
            {
                return;
            }

            _debounce.Remove(sourceId);
            _hintCount++;
            _lastHintAt = _timeProvider.GetUtcNow();
        }

        state.Timer.Dispose();
        _scheduler.HintSource(sourceId);
        PublishStatus();
    }

    private void PublishStatus() => _scheduler.SetWatcherStatus(Status());

    private static bool TryNormalize(string path, out string normalized)
    {
        try
        {
            normalized = SourceSecurity.Normalize(path);
            return true;
        }
        catch (SourceAccessException)
        {
            normalized = string.Empty;
            return false;
        }
    }

    private sealed class WatchPlan
    {
        public required string Key { get; init; }
        public required string Directory { get; init; }
        public required bool Folder { get; init; }
        public string? ExactFile { get; init; }
        public required string Filter { get; init; }
        public required HashSet<string> SourceIds { get; init; }
    }

    private sealed class WatchSlot
    {
        public required string Key { get; init; }
        public required string Directory { get; init; }
        public required bool Folder { get; init; }
        public string? ExactFile { get; init; }
        public required ISourceWatchHandle Handle { get; init; }
        public required HashSet<string> SourceIds { get; init; }
    }

    private sealed class DebounceState
    {
        public ITimer Timer { get; set; } = null!;
        public int Events { get; set; }
    }
}
