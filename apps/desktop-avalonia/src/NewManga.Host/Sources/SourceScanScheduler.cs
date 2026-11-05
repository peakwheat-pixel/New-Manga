using System.Collections.Concurrent;
using System.Globalization;
using System.Security.Cryptography;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11-SCAN-1 (I-4 / AC-S1): one registered Host-side scan target. Registered by the App after a
/// referenced import reaches <c>Completed</c> (I-2); held in memory only (L-A/L-C). The absolute
/// path is required to mint the read grant but is deliberately excluded from logs, status and
/// exception text (see <see cref="ToString"/>).
/// </summary>
public sealed record SourceScanTarget(
    string SourceId,
    string Path,
    IReadOnlyList<string> ProjectIds,
    string Version)
{
    public override string ToString() => "SourceScanTarget(" + SourceId + ")";
}

/// <summary>The closed <c>last_result</c> enum plus the internal <see cref="Deferred"/> marker.
/// <see cref="Deferred"/> is never projected as a result (I-6); the scheduler keeps it out of
/// <see cref="SourceScanStatus"/> results and only reflects it via <c>deferred</c>.</summary>
public enum SourceScanOutcomeKind
{
    Ok,
    Changed,
    Missing,
    Unsupported,
    Denied,
    Error,
    Deferred,
}

/// <summary>One target's scan verdict. <see cref="ErrorCode"/> is a typed code only.</summary>
public sealed record SourceScanOutcome(
    SourceScanOutcomeKind Kind,
    SourceScanCounts? Counts = null,
    string? ErrorCode = null)
{
    public static SourceScanOutcome Ok(SourceScanCounts? counts = null) => new(SourceScanOutcomeKind.Ok, counts);

    public static SourceScanOutcome Changed(SourceScanCounts counts) => new(SourceScanOutcomeKind.Changed, counts);

    public static SourceScanOutcome Missing(SourceScanCounts? counts = null) =>
        new(SourceScanOutcomeKind.Missing, counts);

    public static SourceScanOutcome Unsupported(SourceScanCounts? counts = null) =>
        new(SourceScanOutcomeKind.Unsupported, counts);

    public static SourceScanOutcome Denied(string code) => new(SourceScanOutcomeKind.Denied, null, code);

    public static SourceScanOutcome Error(string? code = null) => new(SourceScanOutcomeKind.Error, null, code);

    public static SourceScanOutcome Deferred() => new(SourceScanOutcomeKind.Deferred);
}

/// <summary>I-4: cheap per-target budget probe (bytes for containers, member count for folders).</summary>
public sealed record SourceScanBudget(long Metric, long Limit)
{
    public bool Exceeded => Metric > Limit;
}

/// <summary>
/// FEA-11-SCAN-1 (I-3/AC-S2): the only operation the scheduler may perform. Production implements
/// it with the real grant chain + <c>ScanSourceSync</c>; tests script it (fake core).
/// </summary>
public interface ISourceScanExecutor
{
    /// <summary>Cheap pre-check; null when the metric cannot be established (treated as "not deferred").</summary>
    SourceScanBudget? ProbeBudget(SourceScanTarget target);

    Task<SourceScanOutcome> ScanAsync(SourceScanTarget target, CancellationToken cancellationToken);
}

/// <summary>FEA-11-SCAN-1 (I-4 / AC-S3) tunables; HostOptions maps onto this and tests override it.</summary>
public sealed record SourceScanOptions
{
    public bool Enabled { get; init; } = true;

    public int IntervalSeconds { get; init; } = SourceScanScheduler.DefaultIntervalSeconds;

    public int MaxTargetsPerTick { get; init; } = SourceScanScheduler.DefaultMaxTargetsPerTick;

    public long MaxBytesPerSource { get; init; } = SourceScanScheduler.DefaultMaxBytesPerSource;

    public int MaxEntriesPerSource { get; init; } = SourceScanScheduler.DefaultMaxEntriesPerSource;

    public int BackoffBaseSeconds { get; init; } = SourceScanScheduler.DefaultBackoffBaseSeconds;

    public int BackoffMaxSeconds { get; init; } = SourceScanScheduler.DefaultBackoffMaxSeconds;
}

/// <summary>
/// FEA-11-SCAN-1 (I-1/I-3/I-5/I-6/AC-S1…S5): the Host-side single-instance, read-only periodic scan
/// scheduler.
///
/// Contract boundaries enforced here:
///  - ONE loop task, idempotent <see cref="Start"/>; ticks are single-flight (an overlapping tick is
///    merged, never queued) and sequential inside a tick;
///  - the scheduler NEVER calls plan/preview/confirm/apply/relink/repoint/resync — only
///    <see cref="ISourceScanExecutor.ScanAsync"/>, whose production implementation sends exactly
///    <c>ScanSourceSync</c>;
///  - results stay in memory (<see cref="Snapshot"/>); logs carry source ids/counts/typed codes only;
///  - failure handling: typed backoff <c>min(60 × 2^n, 3600)</c> seconds, success resets; capability/
///    session/validation verdicts PAUSE the scheduler (fail-closed, no retry, no session reopening).
///
/// No <c>Task.Delay</c>/sleep is used by tests: <see cref="TickAsync"/> is directly invokable against
/// an injected <see cref="TimeProvider"/> and all timestamps come from that provider.
/// </summary>
public sealed class SourceScanScheduler : IAsyncDisposable
{
    public const int DefaultIntervalSeconds = 900;
    public const int MinimumIntervalSeconds = 60;
    public const int MaximumIntervalSeconds = 86400;
    public const int DefaultMaxTargetsPerTick = 8;
    public const long DefaultMaxBytesPerSource = 256L * 1024 * 1024;
    public const int DefaultMaxEntriesPerSource = 10000;
    public const int DefaultBackoffBaseSeconds = 60;
    public const int DefaultBackoffMaxSeconds = 3600;

    /// <summary>AC-S1: environment override for the interval (illegal → 900s + WARN).</summary>
    public const string IntervalEnvironmentVariable = "NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS";

    // I-4 / AC-S3: fail-closed verdicts. A Host that cannot prove the required capability, is told
    // the command is host-only or is told the request shape is invalid must never keep retrying.
    private static readonly HashSet<string> PauseCodes = new(StringComparer.Ordinal)
    {
        "CORE_CAPABILITY_MISSING", "HOST_ONLY_REQUIRED", "INVALID_REQUEST",
        "HOST_SESSION_INVALID", "CORE_SESSION_MISMATCH",
    };

    // Authorization refusals are recorded as "denied" (diagnostic, backoff) — never as success.
    private static readonly HashSet<string> DeniedCodes = new(StringComparer.Ordinal)
    {
        "SOURCE_ACCESS_DENIED", "SOURCE_GRANT_REVOKED", "SOURCE_GRANT_EXPIRED",
        "SOURCE_PASSWORD_REQUIRED", "SOURCE_PASSWORD_INVALID",
    };

    private readonly object _gate = new();
    private readonly SourceScanOptions _options;
    private readonly ISourceScanExecutor _executor;
    private readonly TimeProvider _timeProvider;
    private readonly Action<string>? _info;
    private readonly Action<string>? _warn;
    private readonly Action<string, string>? _error;

    private readonly Dictionary<string, TargetState> _targets = new(StringComparer.Ordinal);
    private readonly SemaphoreSlim _tickGate = new(1, 1);
    private readonly List<SourceScanRecentEntry> _recent = new();
    private int _budgetCursor;
    private bool _paused;
    private bool _disposed;
    private DateTimeOffset? _lastTickAt;
    private DateTimeOffset? _nextTickAt;
    private CancellationTokenSource? _loopCts;
    private Task? _loopTask;

    public SourceScanScheduler(
        SourceScanOptions options,
        ISourceScanExecutor executor,
        TimeProvider? timeProvider = null,
        Action<string>? infoLog = null,
        Action<string>? warnLog = null,
        Action<string, string>? errorLog = null)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(executor);
        _options = options;
        _executor = executor;
        _timeProvider = timeProvider ?? TimeProvider.System;
        _info = infoLog;
        _warn = warnLog;
        _error = errorLog;
    }

    public bool Enabled => _options.Enabled;

    public int IntervalSeconds => _options.IntervalSeconds;

    public bool Paused
    {
        get { lock (_gate) return _paused; }
    }

    /// <summary>I-3: true while the single production loop is running.</summary>
    public bool IsRunning
    {
        get { lock (_gate) return _loopTask is not null && !_loopTask.IsCompleted; }
    }

    /// <summary>AC-S1: idempotent — a second call never creates a second loop.</summary>
    public void Start()
    {
        lock (_gate)
        {
            if (_disposed || _loopTask is not null) return;
            _loopCts = new CancellationTokenSource();
            var token = _loopCts.Token;
            _loopTask = Task.Run(() => LoopAsync(token));
        }
    }

    /// <summary>AC-S1: idempotent; no further tick can start after this returns.</summary>
    public void Stop()
    {
        CancellationTokenSource? cts;
        lock (_gate)
        {
            cts = _loopCts;
            _loopCts = null;
        }

        try { cts?.Cancel(); }
        catch (ObjectDisposedException) { }
        cts?.Dispose();
    }

    /// <summary>
    /// AC-S1: pause/resume. While paused a tick performs zero executor calls; the snapshot exposes
    /// <c>paused</c>. The scheduler never reopens a Core session itself.
    /// </summary>
    public void Pause(string reasonCode)
    {
        bool changed;
        lock (_gate)
        {
            changed = !_paused;
            _paused = true;
        }

        if (changed) _warn?.Invoke("source scan paused reason=" + reasonCode);
    }

    public void Resume()
    {
        bool changed;
        lock (_gate)
        {
            changed = _paused;
            _paused = false;
        }

        if (changed) _info?.Invoke("source scan resumed");
    }

    /// <summary>
    /// I-2: registers/replaces a target by <c>source_id</c> (overwrite, never grow on re-import).
    /// Only the App's completed referenced imports reach this; no path is logged.
    /// </summary>
    public bool RegisterTarget(SourceScanTarget target)
    {
        ArgumentNullException.ThrowIfNull(target);
        if (_disposed || string.IsNullOrWhiteSpace(target.SourceId) || string.IsNullOrWhiteSpace(target.Path))
        {
            return false;
        }

        lock (_gate)
        {
            _targets[target.SourceId] = new TargetState(target);
        }

        _info?.Invoke("source scan target registered source=" + target.SourceId);
        return true;
    }

    /// <summary>
    /// Runs exactly one scan pass. Returns false when the pass was skipped (paused, disabled,
    /// disposed or merged into an in-flight pass). Sequential inside the pass; every Core call is
    /// performed by the executor.
    /// </summary>
    public async Task<bool> TickAsync(CancellationToken cancellationToken = default)
    {
        if (!await _tickGate.WaitAsync(0, cancellationToken).ConfigureAwait(false))
        {
            // I-3: an overlapping tick is merged — never queued.
            return false;
        }

        try
        {
            var now = _timeProvider.GetUtcNow();
            List<KeyValuePair<string, TargetState>> ordered;
            lock (_gate)
            {
                if (_disposed || !_options.Enabled)
                {
                    return false;
                }

                _lastTickAt = now;
                _nextTickAt = now.AddSeconds(EffectiveIntervalSeconds());
                foreach (var state in _targets.Values) state.Deferred = false;
                ordered = _targets.OrderBy(pair => pair.Key, StringComparer.Ordinal).ToList();
            }

            if (Paused || ordered.Count == 0)
            {
                _info?.Invoke("source scan tick skipped paused=" + Paused + " targets=" + ordered.Count);
                return true;
            }

            var processed = 0;
            var attempted = 0;
            var lastAttemptedIndex = -1;
            var targetCount = ordered.Count;
            var start = _budgetCursor % targetCount;
            // Budget selection never wraps inside one tick (AC-S3: 10 targets / budget 4 → 4+4+2);
            // the cursor wraps only after the tail of the list was reached.
            for (var index = start; index < targetCount && attempted < _options.MaxTargetsPerTick; index++)
            {
                if (cancellationToken.IsCancellationRequested) break;
                var pair = ordered[index];
                var state = pair.Value;
                if (state.BackoffUntil is { } until && until > now)
                {
                    continue;
                }

                attempted++;
                lastAttemptedIndex = index;
                _budgetCursor = index + 1 >= targetCount ? 0 : index + 1;
                var outcome = await ExecuteAsync(state.Target, cancellationToken).ConfigureAwait(false);
                if (cancellationToken.IsCancellationRequested) break;
                if (ApplyOutcome(state, outcome, now))
                {
                    processed++;
                }

                if (Paused) break;
            }

            // I-4: targets skipped because THIS tick ran out of budget are marked deferred (never a
            // failure, never a scan result). Backed-off targets are not budget-deferred.
            if (attempted >= _options.MaxTargetsPerTick)
            {
                for (var index = lastAttemptedIndex + 1; index < targetCount; index++)
                {
                    var state = ordered[index].Value;
                    if (state.BackoffUntil is { } until && until > now) continue;
                    state.Deferred = true;
                }
            }

            _info?.Invoke("source scan tick targets=" + ordered.Count + " attempted=" + attempted
                + " processed=" + processed + " paused=" + Paused);
            return true;
        }
        finally
        {
            _tickGate.Release();
        }
    }

    /// <summary>AC-S5: defensive in-process snapshot (no path/grant/session/message ever copied).</summary>
    public SourceScanStatus Snapshot()
    {
        lock (_gate)
        {
            var targets = _targets.OrderBy(pair => pair.Key, StringComparer.Ordinal)
                .Select(pair => new SourceScanTargetStatus(
                    pair.Key, pair.Value.LastScanAt, pair.Value.LastResult, pair.Value.Counts, pair.Value.Deferred))
                .ToArray();
            var recent = _recent.ToArray();
            return new SourceScanStatus(
                _options.Enabled,
                EffectiveIntervalSeconds(),
                _paused,
                _lastTickAt,
                _nextTickAt,
                targets,
                recent);
        }
    }

    /// <summary>AC-S1: stops the loop and joins it; idempotent.</summary>
    public async ValueTask DisposeAsync()
    {
        Task? loop;
        lock (_gate)
        {
            if (_disposed) return;
            _disposed = true;
            loop = _loopTask;
        }

        Stop();
        if (loop is not null)
        {
            try { await loop.ConfigureAwait(false); }
            catch (Exception error) when (error is OperationCanceledException or ObjectDisposedException) { }
        }

        _tickGate.Dispose();
    }

    /// <summary>
    /// AC-S1: resolves the effective interval. Environment override wins; anything outside
    /// <c>[60, 86400]</c> (or non-numeric) falls back to 900s and reports <paramref name="usedFallback"/>
    /// so the Host can WARN without failing startup.
    /// </summary>
    public static int ResolveIntervalSeconds(int configuredSeconds, string? environmentValue, out bool usedFallback)
    {
        var candidate = configuredSeconds;
        if (!string.IsNullOrWhiteSpace(environmentValue))
        {
            if (int.TryParse(environmentValue.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture,
                    out var parsed))
            {
                candidate = parsed;
            }
            else
            {
                usedFallback = true;
                return DefaultIntervalSeconds;
            }
        }

        if (candidate < MinimumIntervalSeconds || candidate > MaximumIntervalSeconds)
        {
            usedFallback = true;
            return DefaultIntervalSeconds;
        }

        usedFallback = false;
        return candidate;
    }

    private int EffectiveIntervalSeconds() => _options.IntervalSeconds is >= MinimumIntervalSeconds
        and <= MaximumIntervalSeconds
        ? _options.IntervalSeconds
        : DefaultIntervalSeconds;

    private async Task LoopAsync(CancellationToken token)
    {
        // Delay first: the scan slice never enumerates all sources at cold start (O-10 / L-A).
        while (!token.IsCancellationRequested)
        {
            try
            {
                await Task.Delay(TimeSpan.FromSeconds(EffectiveIntervalSeconds()), _timeProvider, token)
                    .ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                return;
            }
            catch (ObjectDisposedException)
            {
                return;
            }

            try
            {
                await TickAsync(token).ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                return;
            }
            catch (Exception error) when (error is not OutOfMemoryException)
            {
                // The loop must never die on one pass: the typed verdict was already recorded.
                _error?.Invoke("SOURCE_SCAN_LOOP", error.GetType().Name);
            }
        }
    }

    private async Task<SourceScanOutcome> ExecuteAsync(SourceScanTarget target, CancellationToken cancellationToken)
    {
        try
        {
            var budget = _executor.ProbeBudget(target);
            if (budget is { Exceeded: true })
            {
                // I-4: over-budget targets are postponed (deferred), never a failure.
                _info?.Invoke("source scan source=" + target.SourceId + " deferred=budget");
                return SourceScanOutcome.Deferred();
            }

            return await _executor.ScanAsync(target, cancellationToken).ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (CoreOperationException error)
        {
            return FromCode(error.Code);
        }
        catch (SourceAccessException error)
        {
            return FromCode(error.Code);
        }
        catch (SidecarException error)
        {
            // Sidecar exit / transport loss: the session is not reopened by this slice (I-7).
            Pause(error.Code.ToString());
            return SourceScanOutcome.Error(error.Code.ToString());
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return SourceScanOutcome.Error("SOURCE_SYNC_STORAGE_FAILED");
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            return SourceScanOutcome.Error("UNKNOWN");
        }
    }

    private SourceScanOutcome FromCode(string code)
    {
        if (PauseCodes.Contains(code))
        {
            Pause(code);
            return SourceScanOutcome.Error(code);
        }

        return DeniedCodes.Contains(code) ? SourceScanOutcome.Denied(code) : SourceScanOutcome.Error(code);
    }

    /// <summary>Applies one outcome; returns true when it is a real (non-deferred) scan result.</summary>
    private bool ApplyOutcome(TargetState state, SourceScanOutcome outcome, DateTimeOffset now)
    {
        switch (outcome.Kind)
        {
            case SourceScanOutcomeKind.Deferred:
                state.Deferred = true;
                return false;
            case SourceScanOutcomeKind.Ok:
            case SourceScanOutcomeKind.Changed:
            case SourceScanOutcomeKind.Missing:
            case SourceScanOutcomeKind.Unsupported:
            case SourceScanOutcomeKind.Denied:
                state.Failures = 0;
                state.BackoffUntil = null;
                break;
            case SourceScanOutcomeKind.Error:
            default:
                state.Failures = Math.Min(state.Failures + 1, 32);
                state.BackoffUntil = now.AddSeconds(BackoffSeconds(state.Failures));
                _warn?.Invoke("source scan source=" + state.Target.SourceId + " code="
                    + (outcome.ErrorCode ?? "UNKNOWN") + " backoff=" + BackoffSeconds(state.Failures));
                break;
        }

        state.LastScanAt = now;
        state.LastResult = ResultOf(outcome.Kind);
        state.Counts = outcome.Counts;
        state.Deferred = false;

        // AC-S4: an unchanged scan produces no new "recent" record (dedup/noise control).
        if (state.LastResult != SourceScanResults.Ok)
        {
            _recent.Add(new SourceScanRecentEntry(
                state.Target.SourceId, now, state.LastResult, outcome.Counts, outcome.ErrorCode));
            while (_recent.Count > SourceScanResults.MaxRecentEntries)
            {
                _recent.RemoveAt(0);
            }
        }

        if (_info is not null && state.LastResult != SourceScanResults.Ok)
        {
            _info?.Invoke("source scan source=" + state.Target.SourceId + " result=" + state.LastResult);
        }

        return true;
    }

    private int BackoffSeconds(int failures)
    {
        if (failures <= 0) return 0;
        var exponent = Math.Min(failures - 1, 16);
        var candidate = (long)_options.BackoffBaseSeconds << exponent;
        return (int)Math.Min(candidate, _options.BackoffMaxSeconds);
    }

    private static string ResultOf(SourceScanOutcomeKind kind) => kind switch
    {
        SourceScanOutcomeKind.Ok => SourceScanResults.Ok,
        SourceScanOutcomeKind.Changed => SourceScanResults.Changed,
        SourceScanOutcomeKind.Missing => SourceScanResults.Missing,
        SourceScanOutcomeKind.Unsupported => SourceScanResults.Unsupported,
        SourceScanOutcomeKind.Denied => SourceScanResults.Denied,
        _ => SourceScanResults.Error,
    };

    private sealed class TargetState(SourceScanTarget target)
    {
        public SourceScanTarget Target { get; } = target;

        public DateTimeOffset? LastScanAt { get; set; }

        public string? LastResult { get; set; }

        public SourceScanCounts? Counts { get; set; }

        public bool Deferred { get; set; }

        public int Failures { get; set; }

        public DateTimeOffset? BackoffUntil { get; set; }
    }
}

/// <summary>
/// FEA-11-SCAN-1 (I-3/I-5 / AC-S2/S4): the production executor. Per target it:
///  1. resolves <c>(registry_id, generation)</c> by exact path match against the Host registry;
///  2. stats the source (folder member count / file size) and defers over-budget targets;
///  3. mints one short-lived read grant via the existing <see cref="SourceReadCoordinator"/>;
///  4. sends exactly ONE <c>ScanSourceSync</c> (full re-enumeration; no hill-climbing, no hints);
///  5. projects the Core <c>Totals</c> and the frozen source status; on a missing source it sends
///     the C-17 §5.3 <c>MissingObservation</c> (no grant) using the last verified identity digest.
///
/// The executor never plans/applies/deletes and never writes Core state.
/// </summary>
public sealed class HostSourceScanExecutor : ISourceScanExecutor
{
    private const string ScanCommand = "ScanSourceSync";
    private const string ScopeCurrent = "current";
    private const string KindResync = "resync";

    /// <summary>Stable opaque rendition key (the scan never decodes; identity checks use grant facts).</summary>
    private static readonly string ScanRenditionParamsDigest = Convert.ToHexString(
        SHA256.HashData("fea11-scan-1-rendition-v1"u8.ToArray())).ToLowerInvariant();

    private readonly CoreServiceClient _core;
    private readonly SourceReadCoordinator _sources;
    private readonly SourceScanOptions _options;
    private readonly TimeProvider _timeProvider;
    // source_id → last verified identity digest observed in a successful scan (never persisted);
    // only used to build the C-17 §5.3 MissingObservation. Registry entries carry no per-source
    // identity facts today, so a source that is missing before its first successful tick fails
    // closed with a typed error instead of fabricating an identity.
    private readonly ConcurrentDictionary<string, string> _identityDigests = new(StringComparer.Ordinal);

    public HostSourceScanExecutor(
        CoreServiceClient core,
        SourceReadCoordinator sources,
        SourceScanOptions options,
        TimeProvider? timeProvider = null)
    {
        _core = core;
        _sources = sources;
        _options = options;
        _timeProvider = timeProvider ?? TimeProvider.System;
    }

    public SourceScanBudget? ProbeBudget(SourceScanTarget target)
    {
        try
        {
            if (Directory.Exists(target.Path))
            {
                if (!TryNormalize(target.Path, out var folder)) return null;
                var count = CountFolderMembers(folder, _options.MaxEntriesPerSource);
                return count is { } members ? new SourceScanBudget(members, _options.MaxEntriesPerSource) : null;
            }

            if (!File.Exists(target.Path)) return null;
            var info = new FileInfo(target.Path);
            return new SourceScanBudget(info.Length, _options.MaxBytesPerSource);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or SourceAccessException)
        {
            return null;
        }
    }

    public async Task<SourceScanOutcome> ScanAsync(SourceScanTarget target, CancellationToken cancellationToken)
    {
        var entry = ResolveRegistryEntry(target.Path);
        if (entry is null)
        {
            // Card I-4: an unresolvable path is this target's typed failure (backoff), never a guess.
            return SourceScanOutcome.Error("SOURCE_ACCESS_DENIED");
        }

        var normalized = SourceSecurity.Normalize(target.Path);
        var isFolder = Directory.Exists(normalized);
        var exists = isFolder || File.Exists(normalized);
        if (!exists)
        {
            return await ScanMissingAsync(entry, target, cancellationToken).ConfigureAwait(false);
        }

        var kind = isFolder ? "folder" : KindOf(normalized);
        string grantId;
        try
        {
            grantId = await _sources.IssueAsync(
                    entry.RegistryId, entry.Generation, normalized, kind, target.SourceId, target.Version,
                    RenditionOf(kind), maxBytes: _options.MaxBytesPerSource,
                    maxDecodeBytes: _options.MaxBytesPerSource,
                    maxEntries: _options.MaxEntriesPerSource,
                    cancellationToken: cancellationToken)
                .ConfigureAwait(false);
        }
        catch (SourceAccessException error) when (error.Code == "SOURCE_BUDGET_EXCEEDED")
        {
            return SourceScanOutcome.Deferred();
        }

        var response = await _core.SendHostControlAsync(ScanCommand, writer =>
        {
            writer.WriteString("source_id", target.SourceId);
            writer.WriteStartArray("project_ids");
            foreach (var projectId in target.ProjectIds) writer.WriteStringValue(projectId);
            writer.WriteEndArray();
            writer.WriteString("scope", ScopeCurrent);
            writer.WriteString("kind", KindResync);
            writer.WriteStartArray("grant_ids");
            writer.WriteStringValue(grantId);
            writer.WriteEndArray();
            writer.WriteStartArray("missing");
            writer.WriteEndArray();
        }, cancellationToken).ConfigureAwait(false);

        return ProjectScanResult(response.Result);
    }

    /// <summary>
    /// C-17 §5.3 missing path: stat already failed, so prove the absence with a
    /// <see cref="MissingObservation"/> built from the last verified scan identity (no read grant).
    /// </summary>
    private async Task<SourceScanOutcome> ScanMissingAsync(
        SourceAuthorization entry,
        SourceScanTarget target,
        CancellationToken cancellationToken)
    {
        if (!_identityDigests.TryGetValue(target.SourceId, out var identityDigest)
            || !IsLowerHex64(identityDigest))
        {
            // Fail closed: without a verification baseline the Host must not claim "missing".
            return SourceScanOutcome.Error("SOURCE_ENTRY_MISSING");
        }

        var observedAt = _timeProvider.GetUtcNow()
            .ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", CultureInfo.InvariantCulture);
        var response = await _core.SendHostControlAsync(ScanCommand, writer =>
        {
            writer.WriteString("source_id", target.SourceId);
            writer.WriteStartArray("project_ids");
            foreach (var projectId in target.ProjectIds) writer.WriteStringValue(projectId);
            writer.WriteEndArray();
            writer.WriteString("scope", ScopeCurrent);
            writer.WriteString("kind", KindResync);
            writer.WriteStartArray("grant_ids");
            writer.WriteEndArray();
            writer.WriteStartArray("missing");
            writer.WriteStartObject();
            writer.WriteString("source_id", target.SourceId);
            writer.WriteString("registry_id", entry.RegistryId);
            writer.WriteNumber("generation", entry.Generation);
            writer.WriteString("expected_identity_digest", identityDigest);
            writer.WriteString("observed_at", observedAt);
            writer.WriteEndObject();
            writer.WriteEndArray();
        }, cancellationToken).ConfigureAwait(false);

        return ProjectScanResult(response.Result);
    }

    private SourceScanOutcome ProjectScanResult(JsonElement? result)
    {
        if (result is not { ValueKind: JsonValueKind.Object } value)
        {
            return SourceScanOutcome.Error("UNKNOWN");
        }

        if (!value.TryGetProperty("source", out var source) || source.ValueKind != JsonValueKind.Object)
        {
            return SourceScanOutcome.Error("UNKNOWN");
        }

        var status = source.TryGetProperty("status", out var statusValue)
                     && statusValue.ValueKind == JsonValueKind.String
            ? statusValue.GetString()
            : null;
        var counts = ParseTotals(value);

        if (status == "missing")
        {
            return SourceScanOutcome.Missing(counts);
        }

        if (status is "encrypted" or "unsupported")
        {
            return SourceScanOutcome.Unsupported(counts);
        }

        var identityDigest = source.TryGetProperty("identity_digest", out var identityValue)
                             && identityValue.ValueKind == JsonValueKind.String
            ? identityValue.GetString()
            : null;
        var sourceId = source.TryGetProperty("source_id", out var sourceIdValue)
                       && sourceIdValue.ValueKind == JsonValueKind.String
            ? sourceIdValue.GetString()
            : null;
        if (sourceId is not null && identityDigest is not null && IsLowerHex64(identityDigest))
        {
            _identityDigests[sourceId] = identityDigest;
        }

        return counts is { HasChange: true }
            ? SourceScanOutcome.Changed(counts)
            : SourceScanOutcome.Ok(counts ?? SourceScanCounts.Zero);
    }

    private static SourceScanCounts? ParseTotals(JsonElement scan)
    {
        if (!scan.TryGetProperty("totals", out var totals) || totals.ValueKind != JsonValueKind.Object)
        {
            return null;
        }

        return new SourceScanCounts(
            ReadInt(totals, "unchanged"),
            ReadInt(totals, "added"),
            ReadInt(totals, "missing"),
            ReadInt(totals, "changed"),
            ReadInt(totals, "ambiguous"));
    }

    private static int ReadInt(JsonElement value, string name) =>
        value.TryGetProperty(name, out var property) && property.ValueKind == JsonValueKind.Number
            && property.TryGetInt32(out var parsed)
            ? parsed
            : 0;

    private SourceAuthorization? ResolveRegistryEntry(string path)
    {
        if (!TryNormalize(path, out var normalized)) return null;
        return _sources.Registry.List()
            .Where(entry => entry.RevokedAt is null)
            .Select(entry => new
            {
                Entry = entry,
                Root = entry.Roots
                    .Where(root => root.Readable && SourceSecurity.Contains(root.Root, normalized))
                    .OrderByDescending(root => root.Root.Length)
                    .Select(root => root.Root)
                    .FirstOrDefault(),
            })
            .Where(candidate => candidate.Root is not null)
            .OrderByDescending(candidate => candidate.Root!.Length)
            .Select(candidate => candidate.Entry)
            .FirstOrDefault();
    }

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

    private static int? CountFolderMembers(string root, int limit)
    {
        try
        {
            var count = 0;
            var pending = new Stack<string>();
            pending.Push(root);
            while (pending.TryPop(out var directory))
            {
                foreach (var path in Directory.EnumerateFileSystemEntries(directory))
                {
                    var attributes = File.GetAttributes(path);
                    if ((attributes & (FileAttributes.Hidden | FileAttributes.System)) != 0) continue;
                    if ((attributes & FileAttributes.Directory) != 0)
                    {
                        pending.Push(path);
                        continue;
                    }

                    count++;
                    if (count > limit) return count;
                }
            }

            return count;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or SourceAccessException)
        {
            return null;
        }
    }

    private static string KindOf(string path) => Path.GetExtension(path).ToLowerInvariant() switch
    {
        ".zip" => "zip",
        ".cbz" => "cbz",
        ".pdf" => "pdf",
        _ => "image",
    };

    private static JsonElement RenditionOf(string kind)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            writer.WriteStartObject();
            writer.WriteString("decoder", kind);
            writer.WriteNumber("scale", 1.0);
            writer.WriteString("params_digest", ScanRenditionParamsDigest);
            writer.WriteEndObject();
        }

        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }

    private static bool IsLowerHex64(string? value)
    {
        if (value is not { Length: 64 }) return false;
        foreach (var character in value)
        {
            if (character is not (>= '0' and <= '9') and not (>= 'a' and <= 'f')) return false;
        }

        return true;
    }
}
