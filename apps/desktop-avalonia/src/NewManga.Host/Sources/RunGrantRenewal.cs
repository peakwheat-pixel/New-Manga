using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11-RUN-GRANT-2C (C-06 v1.3 §2.2 / C-16 v1.6 §2.4): the liveness of one dispatched Run as seen by
/// the renewal loop. ONLY <see cref="Alive"/> keeps the loop running; anything unprovable is a
/// fail-closed stop (never "assume alive").
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
    /// <summary>
    /// The round could not finish inside the explicit round budget (interval + round &lt; 300 s). The
    /// round is SKIPPED (typed + counted) and the Run stays tracked for the next interval; nothing is
    /// ever retried mid-round.
    /// </summary>
    SkippedBudget,
    /// <summary>The Run reached a terminal state (or disappeared).</summary>
    StoppedTerminal,
    /// <summary>The Run was never tracked / already stopped by this renewal.</summary>
    StoppedNotTracked,
    /// <summary>The per-Run round cap (<see cref="RunGrantRenewalOptions.MaxRenewals"/>) is exhausted.</summary>
    StoppedRoundsExhausted,
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

    /// <summary>True when the loop must continue (a successful round or a budget skip).</summary>
    public bool KeepsTracking => Kind is RunGrantRenewalKind.Renewed or RunGrantRenewalKind.SkippedBudget;

    public static RunGrantRenewalOutcome Success(
        int boundPages, int mintedGrants, int skippedSources) =>
        new(RunGrantRenewalKind.Renewed, boundPages, mintedGrants, skippedSources);

    public static RunGrantRenewalOutcome BudgetSkip(
        string code, int boundPages = 0, int mintedGrants = 0, int skippedSources = 0) =>
        new(RunGrantRenewalKind.SkippedBudget, boundPages, mintedGrants, skippedSources, code);

    public static RunGrantRenewalOutcome Stop(RunGrantRenewalKind kind, string? code = null) =>
        new(kind, Code: code);
}

/// <summary>Counts-only in-process status of the renewal loop (never a wire command or DTO).</summary>
public sealed record RunGrantRenewalStatus(
    bool Enabled,
    int IntervalSeconds,
    int MaxRenewals,
    int TrackedRuns,
    int Attempts,
    int Renewals,
    int BudgetSkips,
    int Stops,
    string? LastCode,
    int RoundBudgetMilliseconds)
{
    public static RunGrantRenewalStatus Disabled(RunGrantRenewalOptions options) =>
        new(false, options.IntervalSeconds, options.MaxRenewals, 0, 0, 0, 0, 0, null,
            (int)RunGrantRenewalOptions.RoundBudget.TotalMilliseconds);
}

/// <summary>
/// FEA-11-RUN-GRANT-2C (D-4): the explicit renewal budget. The frozen grant TTL upper bound is 300 s
/// (C-06 §2.2 / C-16 §2.4); a round must finish with room to spare before the NEXT round, so
/// <c>interval + round budget &lt; 300 s</c> is enforced on the frozen defaults. The per-round budget
/// is passed INTO the mint path (bounded cold-cache on-demand scans) and re-checked after the round.
/// </summary>
public sealed record RunGrantRenewalOptions(bool Enabled, int IntervalSeconds, int MaxRenewals)
{
    public const int DefaultIntervalSeconds = 240;
    public const int DefaultMaxRenewals = 12;

    /// <summary>The whole round (cold fills + mint + one AuthorizeSourceReadForRun) must fit in this.</summary>
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
/// WHEN one round runs, whether the round fits the explicit budget, and whether the Run stays tracked.
/// </summary>
public sealed class RunGrantRenewal : IAsyncDisposable
{
    private sealed class TrackedRun(string runId, string command, JsonElement scope)
    {
        public string RunId { get; } = runId;
        public string Command { get; } = command;
        public JsonElement Scope { get; } = scope;
        public CancellationTokenSource Lifetime { get; } = new();
        public int Attempts { get; set; }
        public Task? Loop { get; set; }
    }

    /// <summary>
    /// One renewal round: (run_id, frozen command, frozen scope, round budget, token). The budget is
    /// handed to the mint path so bounded on-demand scans stop before the interval+TTR safety bound;
    /// the implementation must never change the command/scope.
    /// </summary>
    private readonly Func<string, string, JsonElement, TimeSpan, CancellationToken, Task<RunGrantRenewalOutcome>>
        _renew;

    private readonly RunGrantRenewalOptions _options;
    private readonly TimeProvider _timeProvider;
    private readonly Func<string, CancellationToken, Task<RunLiveness>> _liveness;
    private readonly Action<string>? _info;
    private readonly Action<string>? _warn;
    private readonly CancellationTokenSource _lifetime = new();
    private readonly object _gate = new();
    private readonly Dictionary<string, TrackedRun> _runs = new(StringComparer.Ordinal);
    private int _attempts;
    private int _renewals;
    private int _budgetSkips;
    private int _stops;
    private string? _lastCode;
    private bool _disposed;

    public RunGrantRenewal(
        RunGrantRenewalOptions options,
        TimeProvider timeProvider,
        Func<string, CancellationToken, Task<RunLiveness>> liveness,
        Func<string, string, JsonElement, TimeSpan, CancellationToken, Task<RunGrantRenewalOutcome>> renew,
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
                    _attempts,
                    _renewals,
                    _budgetSkips,
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
    /// calls this after the interval. Every attempt (success, budget skip or failure) counts toward
    /// the hard per-Run round cap; a failure stops the loop, a budget skip keeps it for the next
    /// interval (never a mid-round retry).
    /// </summary>
    public async Task<RunGrantRenewalOutcome> TickAsync(string runId, CancellationToken token)
    {
        int attempt;
        TrackedRun? tracked;
        lock (_gate)
        {
            if (!_runs.TryGetValue(runId, out tracked))
            {
                return NotTracked();
            }

            if (tracked.Attempts >= _options.MaxRenewals)
            {
                attempt = -1;
            }
            else
            {
                attempt = ++tracked.Attempts;
                _attempts++;
            }
        }

        if (attempt < 0)
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

        // PRE-ROUND budget: the frozen interval already guarantees interval + RoundBudget < 300 s
        // (options validation); the explicit round budget is handed to the mint path so bounded
        // cold-cache on-demand scans cannot burn past it.
        var roundBudget = RunGrantRenewalOptions.RoundBudget;
        var started = _timeProvider.GetTimestamp();
        RunGrantRenewalOutcome outcome;
        try
        {
            outcome = await _renew(runId, tracked.Command, tracked.Scope, roundBudget, token)
                .ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
            // The caller's token wins; a budget-cancelled round is handled by the elapsed check.
            if (token.IsCancellationRequested) throw;
            return BudgetSkip(runId, "RENEWAL_ROUND_CANCELLED");
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
        if (elapsed > roundBudget)
        {
            // POST-ROUND guard (belt and braces; the cold-fill path already bounds itself). A round
            // that overruns skips to the NEXT interval instead of stopping: the run keeps renewing,
            // but the budget breach is recorded and counted, and a real mint is still counted.
            if (outcome.Renewed)
            {
                lock (_gate) _renewals++;
            }

            return BudgetSkip(
                runId, "RENEWAL_ROUND_BUDGET_EXCEEDED",
                outcome.BoundPages, outcome.MintedGrants, outcome.SkippedSources);
        }

        if (!outcome.KeepsTracking)
        {
            return Stop(runId, outcome);
        }

        if (outcome.Kind == RunGrantRenewalKind.SkippedBudget)
        {
            return BudgetSkip(
                runId, outcome.Code ?? "RENEWAL_ROUND_SKIPPED_BUDGET",
                outcome.BoundPages, outcome.MintedGrants, outcome.SkippedSources);
        }

        lock (_gate) _renewals++;

        _info?.Invoke("run grant renewal round counts_only"
            + " minted=" + outcome.MintedGrants
            + " bound_pages=" + outcome.BoundPages
            + " skipped=" + outcome.SkippedSources);
        return outcome;
    }

    private static RunGrantRenewalOutcome NotTracked() =>
        RunGrantRenewalOutcome.Stop(RunGrantRenewalKind.StoppedNotTracked, "RENEWAL_NOT_TRACKED");

    private RunGrantRenewalOutcome BudgetSkip(
        string runId, string code, int boundPages = 0, int mintedGrants = 0, int skippedSources = 0)
    {
        lock (_gate)
        {
            if (!_runs.ContainsKey(runId))
            {
                return NotTracked();
            }

            _budgetSkips++;
            _lastCode = code;
        }

        _warn?.Invoke("run grant renewal round skipped code=" + code
            + " minted=" + mintedGrants + " bound_pages=" + boundPages);
        return RunGrantRenewalOutcome.BudgetSkip(code, boundPages, mintedGrants, skippedSources);
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
                if (!outcome.KeepsTracking) return;
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
