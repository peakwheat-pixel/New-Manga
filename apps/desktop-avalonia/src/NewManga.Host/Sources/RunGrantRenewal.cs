using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11-RUN-GRANT-2C (C-06 v1.3 §2.2 / C-16 v1.6 §2.4): the Host-side renewal of the Run-scoped
/// source-read authorization. A Run is executed by the Core's single background scheduler, so the
/// grants minted before dispatch (each ≤300 s) can expire while the Run is still queued or running.
/// While the Run is NOT terminal, the Host re-mints the grants for the SAME frozen
/// <c>{command, scope}</c> and calls <c>AuthorizeSourceReadForRun</c> again — a NEW set of grants
/// (new ids, new ≤300 s expiry), never an extension of an existing grant, never a widened scope, and
/// never a rebuild of a revoked/refused authorization.
///
/// Contract boundaries kept here:
/// * every round goes through the SAME best-effort authorizer as dispatch (<c>AuthorizeSliceAsync</c>),
///   which re-runs <c>Registry.Authorize</c> + the physical facts re-check for every source;
/// * a typed refusal / revoked registry / generation drift / lost root / Core capability loss stops
///   the renewal immediately (no retry, no re-attest, no auto re-authorization);
/// * one round == one <c>AuthorizeSourceReadForRun</c> (the coordinator's own mint gate serialises);
/// * <c>interval + round budget &lt; 300 s</c> keeps a fresh grant alive across the next round;
/// * terminal Runs / a missing Run / Host shutdown stop the loop.
/// </summary>
public enum RunLiveness
{
    Alive,
    Terminal,
    Unknown,
}

/// <summary>The result of ONE renewal round (counts only — never a path, grant id or source id).</summary>
public enum RunGrantRenewalKind
{
    /// <summary>A new grant set was minted and bound; the Run stays tracked.</summary>
    Renewed,
    /// <summary>The Run reached a terminal state (or disappeared).</summary>
    StoppedTerminal,
    /// <summary>The Run was never tracked / already stopped by this renewal.</summary>
    StoppedNotTracked,
    /// <summary>The per-Run round cap (<see cref="RunGrantRenewalOptions.MaxRenewals"/>) is exhausted.</summary>
    StoppedRoundsExhausted,
    /// <summary>The round exceeded the explicit round budget (a typed stop + count, never a retry).</summary>
    StoppedBudget,
    /// <summary>A typed authorization refusal / Host-side failure stopped the renewal.</summary>
    StoppedTyped,
    /// <summary>The liveness probe could not prove the Run alive (fail-closed stop).</summary>
    StoppedLivenessUnknown,
}

public sealed record RunGrantRenewalOutcome(
    RunGrantRenewalKind Kind,
    int BoundPages = 0,
    int MintedGrants = 0,
    int SkippedSources = 0,
    string? Code = null)
{
    public bool Renewed => Kind == RunGrantRenewalKind.Renewed;

    public static RunGrantRenewalOutcome Success(
        int boundPages, int mintedGrants, int skippedSources) =>
        new(RunGrantRenewalKind.Renewed, boundPages, mintedGrants, skippedSources);

    public static RunGrantRenewalOutcome Stop(RunGrantRenewalKind kind, string? code = null) =>
        new(kind, Code: code);
}

/// <summary>Counts-only in-process status of the renewal loop (never a wire command or DTO).</summary>
public sealed record RunGrantRenewalStatus(
    bool Enabled,
    int IntervalSeconds,
    int MaxRenewals,
    int TrackedRuns,
    int Renewals,
    int Stops,
    string? LastCode,
    int RoundBudgetMilliseconds)
{
    public static RunGrantRenewalStatus Disabled(RunGrantRenewalOptions options) =>
        new(false, options.IntervalSeconds, options.MaxRenewals, 0, 0, 0, null,
            (int)RunGrantRenewalOptions.RoundBudget.TotalMilliseconds);
}

/// <summary>
/// FEA-11-RUN-GRANT-2C (D-4): the explicit renewal budget. The frozen grant TTL upper bound is 300 s
/// (C-06 §2.2 / C-16 §2.4); a round must finish with room to spare before the NEXT round, so
/// <c>interval + round budget &lt; 300 s</c> is enforced on the frozen defaults.
/// </summary>
public sealed record RunGrantRenewalOptions(bool Enabled, int IntervalSeconds, int MaxRenewals)
{
    public const int DefaultIntervalSeconds = 240;
    public const int DefaultMaxRenewals = 12;

    /// <summary>A renewal round may take at most this long before it is a typed stop + count.</summary>
    public const int RoundBudgetSeconds = 50;

    /// <summary>Renewing more often than this is pure mint cost; the default (240 s) is the floor.</summary>
    public const int MinimumIntervalSeconds = 240;

    /// <summary><c>interval + round budget &lt; 300 s</c> (the frozen single-grant TTL bound).</summary>
    public const int MaximumIntervalSeconds = 300 - RoundBudgetSeconds - 1;

    public const int MinimumMaxRenewals = 1;
    public const int MaximumMaxRenewals = 100;

    public static readonly TimeSpan Interval = TimeSpan.FromSeconds(DefaultIntervalSeconds);
    public static readonly TimeSpan RoundBudget = TimeSpan.FromSeconds(RoundBudgetSeconds);

    public static RunGrantRenewalOptions Default { get; } =
        new(true, DefaultIntervalSeconds, DefaultMaxRenewals);

    /// <summary>
    /// Illegal configuration falls back to the frozen defaults (never a Host start failure), exactly
    /// like the scan interval seam. <paramref name="usedFallback"/> reports the degradation so the
    /// caller can log it once.
    /// </summary>
    public static RunGrantRenewalOptions Normalize(
        bool enabled, int intervalSeconds, int maxRenewals, out bool usedFallback)
    {
        usedFallback = false;
        var interval = intervalSeconds;
        if (interval < MinimumIntervalSeconds || interval > MaximumIntervalSeconds)
        {
            interval = DefaultIntervalSeconds;
            usedFallback = true;
        }

        var rounds = maxRenewals;
        if (rounds < MinimumMaxRenewals || rounds > MaximumMaxRenewals)
        {
            rounds = DefaultMaxRenewals;
            usedFallback = true;
        }

        return new RunGrantRenewalOptions(enabled, interval, rounds);
    }
}

/// <summary>
/// FEA-11-RUN-GRANT-2C: one per-Run renewal loop, owned by the Host runtime. It is deliberately a
/// standalone class (no Core, no UI) so the whole lifecycle is unit-testable with an injected
/// <see cref="TimeProvider"/> and injected liveness/renew delegates.
///
/// The loop is per Run and serialised by the coordinator's own mint gate; this class only decides
/// WHEN one round runs and whether the Run stays tracked.
/// </summary>
public sealed class RunGrantRenewal : IAsyncDisposable
{
    private sealed class TrackedRun(string runId, string command, JsonElement scope)
    {
        public string RunId { get; } = runId;
        public string Command { get; } = command;
        public JsonElement Scope { get; } = scope;
        public CancellationTokenSource Lifetime { get; } = new();
        public int Rounds { get; set; }
        public Task? Loop { get; set; }
    }

    private readonly RunGrantRenewalOptions _options;
    private readonly TimeProvider _timeProvider;
    private readonly Func<string, CancellationToken, Task<RunLiveness>> _liveness;
    private readonly Func<string, string, JsonElement, CancellationToken, Task<RunGrantRenewalOutcome>> _renew;
    private readonly Action<string>? _info;
    private readonly Action<string>? _warn;
    private readonly CancellationTokenSource _lifetime = new();
    private readonly object _gate = new();
    private readonly Dictionary<string, TrackedRun> _runs = new(StringComparer.Ordinal);
    private int _renewals;
    private int _stops;
    private string? _lastCode;
    private bool _disposed;

    public RunGrantRenewal(
        RunGrantRenewalOptions options,
        TimeProvider timeProvider,
        Func<string, CancellationToken, Task<RunLiveness>> liveness,
        Func<string, string, JsonElement, CancellationToken, Task<RunGrantRenewalOutcome>> renew,
        Action<string>? info = null,
        Action<string>? warn = null)
    {
        _options = options ?? throw new ArgumentNullException(nameof(options));
        _timeProvider = timeProvider ?? throw new ArgumentNullException(nameof(timeProvider));
        _liveness = liveness ?? throw new ArgumentNullException(nameof(liveness));
        _renew = renew ?? throw new ArgumentNullException(nameof(renew));
        _info = info;
        _warn = warn;
    }

    public bool Enabled => _options.Enabled;

    /// <summary>Counts-only snapshot (no path / grant / source id).</summary>
    public RunGrantRenewalStatus Status
    {
        get
        {
            lock (_gate)
            {
                return new RunGrantRenewalStatus(
                    _options.Enabled,
                    _options.IntervalSeconds,
                    _options.MaxRenewals,
                    _runs.Count,
                    _renewals,
                    _stops,
                    _lastCode,
                    (int)RunGrantRenewalOptions.RoundBudget.TotalMilliseconds);
            }
        }
    }

    public bool IsTracking(string runId)
    {
        lock (_gate) return _runs.ContainsKey(runId);
    }

    /// <summary>
    /// FEA-11-RUN-GRANT-2C (D-5): the dispatch-side start gate. A Run is only tracked when the command
    /// produced a run id and its FIRST authorization round bound ≥1 page (a managed-only or
    /// all-skipped Run has no source pages to keep authorized). Returns true when tracking started;
    /// never throws (best-effort bookkeeping on an already dispatched Run).
    /// </summary>
    public bool ObserveDispatch(string? runId, string command, JsonElement scope, int boundPages)
    {
        if (boundPages <= 0 || string.IsNullOrWhiteSpace(runId)) return false;
        return Track(runId, command, scope);
    }

    /// <summary>
    /// Starts the renewal loop for ONE successfully dispatched Run. The caller must only pass the
    /// Run's own frozen <c>{command, scope}</c> and a first round that actually bound ≥1 page
    /// (a managed-only / all-skipped Run has nothing to renew). Idempotent by run id.
    /// </summary>
    public bool Track(string runId, string command, JsonElement scope)
    {
        if (!_options.Enabled || string.IsNullOrWhiteSpace(runId)
            || string.IsNullOrWhiteSpace(command) || scope.ValueKind != JsonValueKind.Object)
        {
            return false;
        }

        lock (_gate)
        {
            if (_disposed || _runs.ContainsKey(runId)) return _runs.ContainsKey(runId);
            var tracked = new TrackedRun(runId, command, scope.Clone());
            _runs[runId] = tracked;
            tracked.Loop = Task.Run(() => LoopAsync(tracked));
        }

        _info?.Invoke("run grant renewal tracking source-run");
        return true;
    }

    /// <summary>Stops tracking one Run (terminal Run observed by the dispatch path).</summary>
    public bool Untrack(string runId)
    {
        TrackedRun? tracked;
        lock (_gate)
        {
            if (!_runs.Remove(runId, out tracked)) return false;
        }

        Cancel(tracked);
        return true;
    }

    /// <summary>
    /// ONE renewal round. Public so the whole state machine is deterministic in tests: the loop only
    /// calls this after the interval. Every non-<see cref="RunGrantRenewalKind.Renewed"/> outcome
    /// stops the Run's loop (fail-closed, never retried).
    /// </summary>
    public async Task<RunGrantRenewalOutcome> TickAsync(string runId, CancellationToken token)
    {
        TrackedRun? tracked;
        lock (_gate)
        {
            if (!_runs.TryGetValue(runId, out tracked))
            {
                return RunGrantRenewalOutcome.Stop(
                    RunGrantRenewalKind.StoppedNotTracked, "RENEWAL_NOT_TRACKED");
            }
        }

        if (tracked is null)
        {
            return RunGrantRenewalOutcome.Stop(
                RunGrantRenewalKind.StoppedNotTracked, "RENEWAL_NOT_TRACKED");
        }

        if (tracked.Rounds >= _options.MaxRenewals)
        {
            return Stop(runId, RunGrantRenewalOutcome.Stop(
                RunGrantRenewalKind.StoppedRoundsExhausted, "RENEWAL_ROUNDS_EXHAUSTED"));
        }

        RunLiveness liveness;
        try
        {
            liveness = await _liveness(runId, token).ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            // A probe failure is never treated as "alive": stop without retrying.
            return Stop(runId, RunGrantRenewalOutcome.Stop(
                RunGrantRenewalKind.StoppedLivenessUnknown, "RENEWAL_PROBE_FAILED"));
        }

        if (liveness == RunLiveness.Terminal)
        {
            return Stop(runId, RunGrantRenewalOutcome.Stop(
                RunGrantRenewalKind.StoppedTerminal, "RENEWAL_RUN_TERMINAL"));
        }

        if (liveness != RunLiveness.Alive)
        {
            return Stop(runId, RunGrantRenewalOutcome.Stop(
                RunGrantRenewalKind.StoppedLivenessUnknown, "RENEWAL_PROBE_UNKNOWN"));
        }

        var started = _timeProvider.GetTimestamp();
        RunGrantRenewalOutcome outcome;
        try
        {
            outcome = await _renew(runId, tracked.Command, tracked.Scope, token)
                .ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (CoreOperationException error)
        {
            outcome = RunGrantRenewalOutcome.Stop(RunGrantRenewalKind.StoppedTyped, error.Code);
        }
        catch (SourceAccessException error)
        {
            outcome = RunGrantRenewalOutcome.Stop(RunGrantRenewalKind.StoppedTyped, error.Code);
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            outcome = RunGrantRenewalOutcome.Stop(
                RunGrantRenewalKind.StoppedTyped, error.GetType().Name);
        }

        var elapsed = _timeProvider.GetElapsedTime(started);
        if (elapsed > RunGrantRenewalOptions.RoundBudget)
        {
            // AC-2C-5: a round that cannot finish inside the explicit budget is a typed stop +
            // count — never a retry and never a silent overlap with the next interval.
            return Stop(runId, RunGrantRenewalOutcome.Stop(
                RunGrantRenewalKind.StoppedBudget, "RENEWAL_ROUND_BUDGET_EXCEEDED"));
        }

        if (!outcome.Renewed)
        {
            return Stop(runId, outcome);
        }

        lock (_gate)
        {
            if (!_runs.ContainsKey(runId)) return outcome;
            tracked.Rounds++;
            _renewals++;
        }

        _info?.Invoke("run grant renewal round counts_only"
            + " minted=" + outcome.MintedGrants
            + " bound_pages=" + outcome.BoundPages
            + " skipped=" + outcome.SkippedSources);
        return outcome;
    }

    private RunGrantRenewalOutcome Stop(string runId, RunGrantRenewalOutcome outcome)
    {
        TrackedRun? tracked;
        lock (_gate)
        {
            _runs.Remove(runId, out tracked);
            _stops++;
            _lastCode = outcome.Code;
        }

        if (tracked is not null)
        {
            Cancel(tracked);
        }

        if (outcome.Code is not null)
        {
            _warn?.Invoke("run grant renewal stopped code=" + outcome.Code);
        }

        return outcome;
    }

    private async Task LoopAsync(TrackedRun tracked)
    {
        try
        {
            while (true)
            {
                await Task.Delay(
                        TimeSpan.FromSeconds(_options.IntervalSeconds),
                        _timeProvider,
                        tracked.Lifetime.Token)
                    .ConfigureAwait(false);
                var outcome = await TickAsync(tracked.RunId, tracked.Lifetime.Token)
                    .ConfigureAwait(false);
                if (!outcome.Renewed) return;
            }
        }
        catch (OperationCanceledException)
        {
            // Host shutdown / Run terminal: the normal stop path.
        }
        catch (ObjectDisposedException)
        {
        }
    }

    private static void Cancel(TrackedRun tracked)
    {
        try { tracked.Lifetime.Cancel(); }
        catch (ObjectDisposedException) { }
    }

    /// <summary>
    /// The frozen terminal Run states (C-08 run status vocabulary): a Run in one of these states has
    /// no further source reads, so the renewal MUST stop. Non-terminal states (pending/running/
    /// paused/blocked) keep the renewal alive (a paused/blocked Run may still be continued).
    /// </summary>
    public static bool IsTerminalRunStatus(string? status) => status switch
    {
        "completed" or "completed_with_failures" or "failed" or "cancelled" or "interrupted" => true,
        _ => false,
    };

    public async ValueTask DisposeAsync()
    {
        TrackedRun[] tracked;
        lock (_gate)
        {
            if (_disposed) return;
            _disposed = true;
            tracked = _runs.Values.ToArray();
            _runs.Clear();
        }

        _lifetime.Cancel();
        foreach (var run in tracked)
        {
            Cancel(run);
        }

        await _lifetime.CancelAsync().ConfigureAwait(false);
        foreach (var run in tracked)
        {
            if (run.Loop is { } loop)
            {
                try
                {
                    await loop.ConfigureAwait(false);
                }
                catch (OperationCanceledException)
                {
                }
                catch (Exception error) when (error is not OutOfMemoryException)
                {
                    // A stopped loop never blocks Host shutdown.
                }
            }

            run.Lifetime.Dispose();
        }

        _lifetime.Dispose();
    }
}
