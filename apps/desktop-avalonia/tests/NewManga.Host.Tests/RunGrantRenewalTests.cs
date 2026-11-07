using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-RUN-GRANT-2C (C-06 v1.3 §2.2 / C-16 v1.6 §2.4): the Host-side Run grant renewal.
///
/// The Core runs a Run to completion on its own scheduler, while the Host-minted source-read grants
/// are each ≤300 s. The renewal loop re-mints the SAME frozen <c>{command, scope}</c> (new grant ids,
/// new ≤300 s expiry) while the Run is not terminal, and STOPS fail-closed on any typed refusal
/// (revocation / generation drift / lost root / capability loss / round budget) — it never extends an
/// existing grant, never widens the scope, never re-attests and never retries. These are deterministic
/// unit tests: no Core is started, the loop's timing seam is injected, and one round is driven by
/// <see cref="RunGrantRenewal.TickAsync"/> directly (the real 240 s wait is never slept).
/// </summary>
public sealed class RunGrantRenewalTests
{
    private static readonly JsonElement FrozenScope =
        JsonDocument.Parse("""{"kind":"page","page_id":"p1"}""").RootElement.Clone();

    private sealed class AdvancingTimeProvider : TimeProvider
    {
        private long _timestamp;

        // 1 tick == 1 ms, so TimeProvider.GetElapsedTime maps the advanved timestamps directly.
        public override long TimestampFrequency => 1000;

        public override long GetTimestamp() => _timestamp;

        public void AdvanceMilliseconds(long milliseconds) => _timestamp += milliseconds;
    }

    private static RunGrantRenewal NewRenewal(
        AdvancingTimeProvider? clock = null,
        RunGrantRenewalOptions? options = null,
        Func<string, CancellationToken, Task<RunLiveness>>? liveness = null,
        Func<string, string, JsonElement, TimeSpan, CancellationToken, Task<RunGrantRenewalOutcome>>? renew = null,
        List<string>? warnings = null) =>
        new(
            options ?? RunGrantRenewalOptions.Default,
            clock ?? new AdvancingTimeProvider(),
            liveness ?? ((_, _) => Task.FromResult(RunLiveness.Alive)),
            renew ?? ((_, _, _, _, _) => Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0))),
            warn: message => warnings?.Add(message));

    // ---------------------------------------------------------------------------------------
    // AC-2C-2 (main AC / D1): renewal rebinds the SAME frozen scope and keeps the Run authorized.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Renewal_RebindsAfterTheWindow_AndTheRunKeepsReading()
    {
        var renewCalls = new List<(string RunId, string Command, JsonElement Scope)>();
        await using var renewal = NewRenewal(
            renew: (runId, command, scope, _, _) =>
            {
                renewCalls.Add((runId, command, scope.Clone()));
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            });

        // The first round bound one page -> the Run is tracked.
        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        Assert.True(renewal.IsTracking("run-1"));

        var first = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.Renewed, first.Kind);
        Assert.Equal(1, first.MintedGrants);
        Assert.Equal(1, first.BoundPages);

        var second = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.Renewed, second.Kind);

        // Every round re-binds the SAME frozen command/scope with a NEW grant set.
        Assert.Equal(2, renewCalls.Count);
        Assert.All(renewCalls, call =>
        {
            Assert.Equal("run-1", call.RunId);
            Assert.Equal("reocr_all", call.Command);
            Assert.Equal(FrozenScope.GetRawText(), call.Scope.GetRawText());
        });
        var status = renewal.Status;
        Assert.Equal(2, status.Renewals);
        Assert.Equal(1, status.TrackedRuns);
        Assert.Equal(0, status.Stops);
        Assert.Equal(RunGrantRenewalOptions.DefaultIntervalSeconds, status.IntervalSeconds);
    }

    [Fact]
    public async Task Renewal_NeverWidensTheFrozenCommandOrScope()
    {
        var renewCalls = new List<(string Command, string Scope)>();
        await using var renewal = NewRenewal(
            renew: (_, command, scope, _, _) =>
            {
                renewCalls.Add((command, scope.GetRawText()));
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            });

        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));

        // A second Track with a DIFFERENT slice (the widening attempt) is a no-op: the Run keeps the
        // frozen slice its dispatch used — a renewal may never change command or scope.
        Assert.True(renewal.ObserveDispatch(
            "run-1", "translate_all", JsonDocument.Parse("""{"kind":"book","book_id":"b1"}""").RootElement.Clone(),
            boundPages: 1));
        await renewal.TickAsync("run-1", CancellationToken.None);

        var captured = Assert.Single(renewCalls);
        Assert.Equal("reocr_all", captured.Command);
        Assert.Equal(FrozenScope.GetRawText(), captured.Scope);
    }

    // ---------------------------------------------------------------------------------------
    // AC-2C-4: a typed refusal / revocation / drift STOPS the renewal; no retry, no re-attest.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Renewal_StopsOnRevokedRegistry_WithoutAnyRetry()
    {
        var renewCalls = 0;
        var warnings = new List<string>();
        await using var renewal = NewRenewal(
            renew: (_, _, _, _, _) =>
            {
                renewCalls++;
                return Task.FromResult(RunGrantRenewalOutcome.Stop(
                    RunGrantRenewalKind.StoppedTyped, "SOURCE_GRANT_REVOKED"));
            },
            warnings: warnings);

        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        var outcome = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.StoppedTyped, outcome.Kind);
        Assert.Equal("SOURCE_GRANT_REVOKED", outcome.Code);
        Assert.False(renewal.IsTracking("run-1"));
        Assert.Equal(1, renewCalls); // a typed refusal is never retried

        // A later tick does not resurrect the Run.
        var again = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.StoppedNotTracked, again.Kind);
        Assert.Equal(1, renewCalls);
        Assert.Contains(warnings, message => message.Contains("SOURCE_GRANT_REVOKED", StringComparison.Ordinal));
        Assert.Equal("SOURCE_GRANT_REVOKED", renewal.Status.LastCode);
    }

    [Fact]
    public async Task Renewal_ProbeFailure_IsAFailClosedStop_NotRetry()
    {
        var renewCalls = 0;
        await using var renewal = NewRenewal(
            liveness: (_, _) => throw new IOException("synthetic probe failure"),
            renew: (_, _, _, _, _) =>
            {
                renewCalls++;
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            });

        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        var outcome = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.StoppedLivenessUnknown, outcome.Kind);
        Assert.Equal(0, renewCalls); // an unprovable liveness is never "alive"
        Assert.False(renewal.IsTracking("run-1"));
    }

    // ---------------------------------------------------------------------------------------
    // AC-2C-5: lifecycle (terminal / shutdown), round cap, round budget, options.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Renewal_StopsAtTerminalRun_AndOnShutdown()
    {
        var liveness = RunLiveness.Alive;
        var renewCalls = 0;
        var renewal = NewRenewal(
            liveness: (_, _) => Task.FromResult(liveness),
            renew: (_, _, _, _, _) =>
            {
                renewCalls++;
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            });
        await using (renewal)
        {
            Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
            Assert.True(renewal.ObserveDispatch("run-2", "reocr_all", FrozenScope, boundPages: 1));

            liveness = RunLiveness.Terminal;
            var terminal = await renewal.TickAsync("run-1", CancellationToken.None);
            Assert.Equal(RunGrantRenewalKind.StoppedTerminal, terminal.Kind);
            Assert.False(renewal.IsTracking("run-1"));
            Assert.Equal(0, renewCalls); // a terminal Run is never re-minted
            Assert.True(renewal.IsTracking("run-2"));
        }

        // Dispose (Host shutdown) stops and joins every remaining loop.
        Assert.False(renewal.IsTracking("run-2"));
    }

    [Fact]
    public async Task Renewal_ObserveDispatch_DoesNotStartWhenNoPageWasBound()
    {
        await using var renewal = NewRenewal();
        // A managed-only / all-skipped Run has nothing to renew.
        Assert.False(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 0));
        Assert.False(renewal.IsTracking("run-1"));
        Assert.False(renewal.ObserveDispatch(null, "reocr_all", FrozenScope, boundPages: 1));
        Assert.False(renewal.IsTracking(string.Empty));
        Assert.Equal(0, renewal.Status.TrackedRuns);
    }

    [Fact]
    public async Task Renewal_DoesNotExceedTheRoundsCap()
    {
        var options = new RunGrantRenewalOptions(true, 240, 2);
        var renewCalls = 0;
        await using var renewal = NewRenewal(
            options: options,
            renew: (_, _, _, _, _) =>
            {
                renewCalls++;
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            });

        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        Assert.Equal(RunGrantRenewalKind.Renewed,
            (await renewal.TickAsync("run-1", CancellationToken.None)).Kind);
        Assert.Equal(RunGrantRenewalKind.Renewed,
            (await renewal.TickAsync("run-1", CancellationToken.None)).Kind);
        var capped = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.StoppedRoundsExhausted, capped.Kind);
        Assert.Equal("RENEWAL_ROUNDS_EXHAUSTED", capped.Code);
        Assert.Equal(2, renewCalls); // the cap is a hard stop, never a retry
    }

    [Fact]
    public async Task Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking()
    {
        // Review r1 P2-01/P3-01: a round that overruns the explicit budget is a TYPED SKIP (recorded,
        // counted) that keeps the Run tracked for the next interval — it is not a silent stop, and a
        // real mint that did happen is still counted.
        var clock = new AdvancingTimeProvider();
        var renewCalls = 0;
        var budgets = new List<TimeSpan>();
        var warnings = new List<string>();
        await using var renewal = NewRenewal(
            clock: clock,
            renew: (_, _, _, roundBudget, _) =>
            {
                renewCalls++;
                budgets.Add(roundBudget);
                // A round that takes longer than the explicit budget: interval + round must stay < 300 s.
                clock.AdvanceMilliseconds(
                    (RunGrantRenewalOptions.RoundBudgetSeconds + 10) * 1000);
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            },
            warnings: warnings);

        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        var outcome = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.SkippedBudget, outcome.Kind);
        Assert.Equal("RENEWAL_ROUND_BUDGET_EXCEEDED", outcome.Code);
        Assert.True(outcome.KeepsTracking);
        Assert.Equal(RunGrantRenewalOptions.RoundBudget, Assert.Single(budgets));
        Assert.Equal(1, renewCalls);
        Assert.True(renewal.IsTracking("run-1"));

        var status = renewal.Status;
        Assert.Equal(1, status.BudgetSkips);
        Assert.Equal(1, status.Renewals);   // the real mint is counted, never swallowed
        Assert.Equal(1, status.Attempts);
        Assert.Equal("RENEWAL_ROUND_BUDGET_EXCEEDED", status.LastCode);
        Assert.Contains(warnings, message =>
            message.Contains("RENEWAL_ROUND_BUDGET_EXCEEDED", StringComparison.Ordinal));
    }

    [Fact]
    public async Task Renewal_BudgetSkip_DoesNotConsumeTheGateOrStopTheRun()
    {
        // The budget skip leaves the loop alive: a later tick (next interval) can still renew.
        var clock = new AdvancingTimeProvider();
        var calls = 0;
        await using var renewal = NewRenewal(
            clock: clock,
            renew: (_, _, _, roundBudget, _) =>
            {
                calls++;
                if (calls == 1)
                {
                    clock.AdvanceMilliseconds(
                        (RunGrantRenewalOptions.RoundBudgetSeconds + 5) * 1000);
                }

                Assert.Equal(RunGrantRenewalOptions.RoundBudget, roundBudget);
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            });

        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        Assert.Equal(RunGrantRenewalKind.SkippedBudget,
            (await renewal.TickAsync("run-1", CancellationToken.None)).Kind);
        Assert.Equal(RunGrantRenewalKind.Renewed,
            (await renewal.TickAsync("run-1", CancellationToken.None)).Kind);
        Assert.Equal(2, calls);
        Assert.Equal(1, renewal.Status.BudgetSkips);
        Assert.Equal(2, renewal.Status.Renewals); // both rounds really minted; the skip is a TYPED count
        Assert.Equal(2, renewal.Status.Attempts);
    }

    [Fact]
    public void Renewal_Options_NormalizeIllegalValues_AndKeepTheContractBound()
    {
        // Frozen defaults.
        Assert.Equal(240, RunGrantRenewalOptions.DefaultIntervalSeconds);
        Assert.Equal(12, RunGrantRenewalOptions.DefaultMaxRenewals);
        Assert.Equal(240, RunGrantRenewalOptions.Default.IntervalSeconds);
        Assert.Equal(12, RunGrantRenewalOptions.Default.MaxRenewals);

        // interval + round budget MUST stay under the frozen 300 s single-grant TTL.
        Assert.True(
            RunGrantRenewalOptions.DefaultIntervalSeconds + RunGrantRenewalOptions.RoundBudgetSeconds
            < 300);

        var valid = RunGrantRenewalOptions.Normalize(true, 245, 10, out var validFallback);
        Assert.False(validFallback);
        Assert.Equal(245, valid.IntervalSeconds);
        Assert.Equal(10, valid.MaxRenewals);

        foreach (var interval in new[] { 0, -1, 239, 250, 300, 100000 })
        {
            var normalized = RunGrantRenewalOptions.Normalize(true, interval, 12, out var fallback);
            Assert.True(fallback, "interval " + interval + " must fall back");
            Assert.Equal(RunGrantRenewalOptions.DefaultIntervalSeconds, normalized.IntervalSeconds);
        }

        foreach (var rounds in new[] { 0, -3, 101, 1000 })
        {
            var normalized = RunGrantRenewalOptions.Normalize(true, 240, rounds, out var fallback);
            Assert.True(fallback, "maxRenewals " + rounds + " must fall back");
            Assert.Equal(RunGrantRenewalOptions.DefaultMaxRenewals, normalized.MaxRenewals);
        }
    }

    [Fact]
    public void Renewal_TerminalStatusVocabulary_IsTheFrozenRunStateSet()
    {
        foreach (var terminal in new[]
                 {
                     "completed", "completed_with_failures", "failed", "cancelled", "interrupted",
                 })
        {
            Assert.True(RunGrantRenewal.IsTerminalRunStatus(terminal), terminal);
        }

        foreach (var live in new[] { "pending", "running", "paused", "blocked", null, "" })
        {
            Assert.False(RunGrantRenewal.IsTerminalRunStatus(live), live);
        }
    }

    [Fact]
    public async Task Renewal_DisabledOption_TracksNothing()
    {
        var options = new RunGrantRenewalOptions(false, 240, 12);
        await using var renewal = NewRenewal(options: options);
        Assert.False(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        Assert.False(renewal.IsTracking("run-1"));
        var status = renewal.Status;
        Assert.False(status.Enabled);
        Assert.Equal(0, status.Renewals);
    }

    // ---------------------------------------------------------------------------------------
    // AC-2C-1/AC-2C-6 seams: the dispatcher authorization returns REAL counts (never "sent = ok")
    // and renewal only ever runs through the same best-effort mint+bind path.
    // ---------------------------------------------------------------------------------------

    private static readonly string FixturePath = @"C:\fixtures\book.zip";

    private static SourceAuthorization RegistryEntry(string registryId, string root) =>
        new(registryId, root, 1, "t", "t", null, new[] { new SourceRoot(root, 0, 0, "t", true) });

    private static RunSourceAuthorizer NewAuthorizer(
        bool probe,
        SourceIdentityCache cache,
        SourceScanTarget[] known,
        SourceAuthorization[] entries,
        Func<IReadOnlyList<RunSourceScope>, string, JsonElement, CancellationToken, Task<RunAuthorizationResult>> authorize,
        Func<SourceScanTarget, CancellationToken, Task>? onDemandScan = null) =>
        new(
            enabled: true,
            knownTargets: () => known,
            registryEntries: () => entries,
            capabilityProbe: _ => Task.FromResult(probe),
            authorize: authorize,
            resolveRunSlice: (_, _) => throw new InvalidOperationException("no run slice expected"),
            info: _ => { },
            warn: _ => { },
            identities: cache,
            onDemandScan: onDemandScan);

    [Fact]
    public async Task AuthorizeSliceAsync_ReturnsTheRealMintAndBindCounts()
    {
        var cache = new SourceIdentityCache();
        Assert.True(cache.Remember("s1", "sv-core-1", []));
        var authorizer = NewAuthorizer(
            probe: true,
            cache,
            new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
            new[] { RegistryEntry("reg-1", FixturePath) },
            (targets, command, _, _) =>
            {
                Assert.Equal("reocr_all", command);
                Assert.Single(targets);
                return Task.FromResult(new RunAuthorizationResult(2, 1, 0, Array.Empty<string>()));
            });

        var result = await authorizer.AuthorizeSliceAsync(
            "reocr_all", FrozenScope, CancellationToken.None);
        Assert.NotNull(result);
        Assert.Equal(2, result!.BoundPages);
        Assert.Equal(1, result.MintedGrants);
        Assert.False(result.Skipped);

        // A probe failure / unusable stack is a best-effort skip (null), never a fabricated success.
        var noProbe = NewAuthorizer(
            probe: false,
            cache,
            new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
            new[] { RegistryEntry("reg-1", FixturePath) },
            (_, _, _, _) => throw new InvalidOperationException("must not authorize"));
        Assert.Null(await noProbe.AuthorizeSliceAsync("reocr_all", FrozenScope, CancellationToken.None));
    }

    [Fact]
    public async Task AuthorizeForCommandResultAsync_CarriesTheFrozenSlice_ForRenewal()
    {
        var cache = new SourceIdentityCache();
        Assert.True(cache.Remember("s1", "sv-core-1", []));
        var authorizer = NewAuthorizer(
            probe: true,
            cache,
            new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
            new[] { RegistryEntry("reg-1", FixturePath) },
            (_, _, _, _) => Task.FromResult(new RunAuthorizationResult(1, 1, 0, Array.Empty<string>())));

        var payload = JsonDocument.Parse(
            """
            {"command":"reocr_all","scope":{"kind":"page","page_id":"p1"},"idempotency_key":"k"}
            """).RootElement.Clone();
        var authorized = await authorizer.AuthorizeForCommandResultAsync(
            "library_start_run", payload, CancellationToken.None);
        Assert.NotNull(authorized);
        Assert.Equal("reocr_all", authorized!.Command);
        Assert.Equal(
            JsonDocument.Parse("""{"kind":"page","page_id":"p1"}""").RootElement.GetRawText(),
            authorized.Scope.GetRawText());
        Assert.Equal(1, authorized.Result!.BoundPages);

        // A read-only / non-executing command is deliberately NOT authorized (null summary).
        Assert.Null(await authorizer.AuthorizeForCommandResultAsync(
            "library_get_run_snapshot",
            JsonDocument.Parse("""{"run_id":"r1"}""").RootElement.Clone(),
            CancellationToken.None));
    }

    // ---------------------------------------------------------------------------------------
    // Review r1 P2-01: the round budget reaches the mint path (bounded on-demand cold fills).
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task AuthorizeSliceAsync_BoundsOnDemandScansByTheRoundBudget()
    {
        var cache = new SourceIdentityCache(); // cold: the source needs one on-demand scan
        var scans = 0;
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        var authorizer = NewAuthorizer(
            probe: true,
            cache,
            new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
            new[] { RegistryEntry("reg-1", FixturePath) },
            (_, _, _, _) => throw new InvalidOperationException("must not authorize a still-cold source"),
            onDemandScan: async (_, token) =>
            {
                scans++;
                // A scan that honors its token: the round budget must cancel it long before 2 s.
                await Task.Delay(TimeSpan.FromSeconds(2), token);
            });

        var result = await authorizer.AuthorizeSliceAsync(
            "reocr_all", FrozenScope, CancellationToken.None, TimeSpan.FromMilliseconds(150));

        Assert.Null(result); // the source is still cold; nothing was minted
        Assert.Equal(1, scans);
        Assert.True(
            stopwatch.Elapsed < TimeSpan.FromSeconds(1.5),
            "the on-demand scan must be bounded by the round budget, not the frozen 30 s timeout");
    }

    [Fact]
    public async Task AuthorizeSliceAsync_WithoutRoundBudget_KeepsTheFrozenOnDemandTimeout()
    {
        // No regression for the dispatch path: a null budget keeps the pre-2C 30 s scan timeout.
        var cache = new SourceIdentityCache();
        var authorizer = NewAuthorizer(
            probe: true,
            cache,
            new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
            new[] { RegistryEntry("reg-1", FixturePath) },
            (_, _, _, _) => Task.FromResult(new RunAuthorizationResult(1, 1, 0, Array.Empty<string>())),
            onDemandScan: (target, _) =>
            {
                cache.Remember(target.SourceId, "sv-from-scan", []);
                return Task.CompletedTask;
            });

        var result = await authorizer.AuthorizeSliceAsync(
            "reocr_all", FrozenScope, CancellationToken.None);
        Assert.NotNull(result);
        Assert.Equal(1, result!.MintedGrants);
    }

    // ---------------------------------------------------------------------------------------
    // Review r1 P1-01: HOST-WIRING tests. They drive the EXACT production entry points the
    // dispatcher / AcceptRun paths and the renewal loop use (pre-dispatch summary -> dispatch
    // notification -> Track -> ONE production Tick), ON the production HostRuntime instance.
    // Removing the installation line (reviewer Probe-C: `_runGrantRenewal = null`) makes these RED.
    // ---------------------------------------------------------------------------------------

    private static HostRuntime CreateUnstartedHostRuntime(HostOptions options, HostLog log)
    {
        var constructor = typeof(HostRuntime).GetConstructor(
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic,
            binder: null,
            [typeof(HostOptions), typeof(HostLog)],
            modifiers: null) ?? throw new InvalidOperationException("HostRuntime ctor not found");
        return (HostRuntime)constructor.Invoke([options, log]);
    }

    private static void WritePrivate(object instance, string name, object value) =>
        instance.GetType()
            .GetField(name, System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!
            .SetValue(instance, value);

    private static HostRuntime CreateWiredHostRuntime(
        string root,
        AdvancingTimeProvider clock,
        RunSourceAuthorizer authorizer,
        SourceAccessRegistry registry,
        bool renewalEnabled = true)
    {
        var dataRoot = Path.Combine(root, "data");
        var logRoot = Path.Combine(root, "logs");
        Directory.CreateDirectory(dataRoot);
        Directory.CreateDirectory(logRoot);
        var options = new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = logRoot,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            RunGrantRenewalEnabled = renewalEnabled,
            RunGrantRenewalTimeProvider = clock,
            RunGrantRenewalLivenessProbe = (_, _) => Task.FromResult(RunLiveness.Alive),
        };
        var runtime = CreateUnstartedHostRuntime(options, new HostLog(logRoot));
        WritePrivate(runtime, "_runAuthorizer", authorizer);
        WritePrivate(runtime, "<Registry>k__BackingField", registry);
        WritePrivate(
            runtime, "<Sources>k__BackingField",
            new SourceReadCoordinator(null!, registry, () => true));
        return runtime;
    }

    [Fact]
    public async Task HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope()
    {
        var root = Path.Combine(Path.GetTempPath(), "fea11-2c-wiring-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            var clock = new AdvancingTimeProvider();
            var registry = new SourceAccessRegistry(root);
            var cache = new SourceIdentityCache();
            Assert.True(cache.Remember("s1", "sv-core-1", []));
            var authorizeCalls = new List<string>();
            var authorizer = NewAuthorizer(
                probe: true,
                cache,
                new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
                new[] { RegistryEntry("reg-1", FixturePath) },
                (_, command, _, _) =>
                {
                    authorizeCalls.Add(command);
                    return Task.FromResult(new RunAuthorizationResult(1, 1, 0, Array.Empty<string>()));
                });
            await using var runtime = CreateWiredHostRuntime(root, clock, authorizer, registry);

            // The production installation line (same line the Host start path runs).
            Assert.True(runtime.StartRunGrantRenewalForTests());
            Assert.NotNull(runtime.RunGrantRenewalForTests);

            // 1) The REAL dispatcher pre-dispatch summary (production method).
            var payload = JsonDocument.Parse(
                """
                {"command":"reocr_all","scope":{"kind":"page","page_id":"p1"},"idempotency_key":"k"}
                """).RootElement.Clone();
            var summary = await runtime.AuthorizeRunCommandForTestsAsync("library_start_run", payload);
            Assert.NotNull(summary);
            Assert.Single(authorizeCalls); // the dispatch round minted+bound once

            // 2) The REAL dispatcher post-dispatch wiring (production method): a Run whose first round
            //    bound a page becomes TRACKED on the Host.
            var dispatched = JsonDocument.Parse(
                """{"run_id":"run-1","status":"pending"}""").RootElement.Clone();
            await runtime.NotifyRunDispatchedForTestsAsync(dispatched, summary);
            Assert.True(runtime.RunGrantRenewalForTests!.IsTracking("run-1"));
            Assert.Equal(1, runtime.RunGrantRenewalStatus.TrackedRuns);

            // 3) The AcceptRun wiring entry shares the SAME frozen-slice start gate.
            await runtime.NotifyAcceptedRunForTestsAsync("run-2", "reocr_all", FrozenScope, boundPages: 1);
            Assert.True(runtime.RunGrantRenewalForTests!.IsTracking("run-2"));

            // 4) ONE production renewal round: the installed loop's renew delegate is the REAL
            //    HostRuntime.RenewRunGrantsAsync (same registry-authorize + mint + ONE bind path).
            var outcome = await runtime.TickRunGrantRenewalForTestsAsync("run-1");
            Assert.Equal(RunGrantRenewalKind.Renewed, outcome.Kind);
            Assert.Equal(1, outcome.BoundPages);
            Assert.Equal(1, outcome.MintedGrants);
            Assert.Equal(2, authorizeCalls.Count); // dispatch round + renewal round
            Assert.All(authorizeCalls, command => Assert.Equal("reocr_all", command));
            Assert.Equal(1, runtime.RunGrantRenewalStatus.Renewals);
            Assert.Equal(1, runtime.RunGrantRenewalStatus.Attempts);
        }
        finally
        {
            try
            {
                if (Directory.Exists(root)) Directory.Delete(root, recursive: true);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                // isolated temp fixture expires with the OS temp directory
            }
        }
    }

    [Fact]
    public async Task HostWiring_ManagedOnlyRun_StartsNoRenewal()
    {
        // AC-2C-6: a first round that bound 0 pages (managed-only / all-skipped) never starts renewal.
        var root = Path.Combine(Path.GetTempPath(), "fea11-2c-wiring-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            var clock = new AdvancingTimeProvider();
            var registry = new SourceAccessRegistry(root);
            var cache = new SourceIdentityCache();
            Assert.True(cache.Remember("s1", "sv-core-1", []));
            var authorizer = NewAuthorizer(
                probe: true,
                cache,
                new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
                new[] { RegistryEntry("reg-1", FixturePath) },
                (_, _, _, _) => throw new InvalidOperationException("must not mint"));
            await using var runtime = CreateWiredHostRuntime(root, clock, authorizer, registry);
            Assert.True(runtime.StartRunGrantRenewalForTests());

            await runtime.NotifyAcceptedRunForTestsAsync(
                "run-managed", "reocr_all", FrozenScope, boundPages: 0);
            Assert.Equal(0, runtime.RunGrantRenewalStatus.TrackedRuns);
            var tick = await runtime.TickRunGrantRenewalForTestsAsync("run-managed");
            Assert.Equal(RunGrantRenewalKind.StoppedNotTracked, tick.Kind);
        }
        finally
        {
            try
            {
                if (Directory.Exists(root)) Directory.Delete(root, recursive: true);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
            }
        }
    }

    [Fact]
    public async Task HostWiring_DisabledOption_InstallsNoLoopAndNeverTracks()
    {
        var root = Path.Combine(Path.GetTempPath(), "fea11-2c-wiring-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            var clock = new AdvancingTimeProvider();
            var registry = new SourceAccessRegistry(root);
            var cache = new SourceIdentityCache();
            Assert.True(cache.Remember("s1", "sv-core-1", []));
            var authorizer = NewAuthorizer(
                probe: true,
                cache,
                new[] { new SourceScanTarget("s1", FixturePath, new[] { "b1" }, "1", SourceKind: "zip") },
                new[] { RegistryEntry("reg-1", FixturePath) },
                (_, _, _, _) => throw new InvalidOperationException("must not mint"));
            await using var runtime = CreateWiredHostRuntime(
                root, clock, authorizer, registry, renewalEnabled: false);

            // No loop is installed when the option is off: the "renewal disabled" direction of
            // AC-2C-1/2 (no renewal -> the Run's window is not extended) is enforced here.
            Assert.False(runtime.StartRunGrantRenewalForTests());
            Assert.Null(runtime.RunGrantRenewalForTests);
            await runtime.NotifyAcceptedRunForTestsAsync("run-1", "reocr_all", FrozenScope, boundPages: 1);
            var tick = await runtime.TickRunGrantRenewalForTestsAsync("run-1");
            Assert.Equal(RunGrantRenewalKind.StoppedNotTracked, tick.Kind);
            Assert.Equal(0, runtime.RunGrantRenewalStatus.TrackedRuns);
            Assert.False(runtime.RunGrantRenewalStatus.Enabled);
        }
        finally
        {
            try
            {
                if (Directory.Exists(root)) Directory.Delete(root, recursive: true);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
            }
        }
    }
}
