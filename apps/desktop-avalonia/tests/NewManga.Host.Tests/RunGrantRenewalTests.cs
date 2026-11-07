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
        Func<string, string, JsonElement, CancellationToken, Task<RunGrantRenewalOutcome>>? renew = null,
        List<string>? warnings = null) =>
        new(
            options ?? RunGrantRenewalOptions.Default,
            clock ?? new AdvancingTimeProvider(),
            liveness ?? ((_, _) => Task.FromResult(RunLiveness.Alive)),
            renew ?? ((_, _, _, _) => Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0))),
            warn: message => warnings?.Add(message));

    // ---------------------------------------------------------------------------------------
    // AC-2C-2 (main AC / D1): renewal rebinds the SAME frozen scope and keeps the Run authorized.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Renewal_RebindsAfterTheWindow_AndTheRunKeepsReading()
    {
        var renewCalls = new List<(string RunId, string Command, JsonElement Scope)>();
        await using var renewal = NewRenewal(
            renew: (runId, command, scope, _) =>
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
            renew: (_, command, scope, _) =>
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
            renew: (_, _, _, _) =>
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
            renew: (_, _, _, _) =>
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
            renew: (_, _, _, _) =>
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
            renew: (_, _, _, _) =>
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
    public async Task Renewal_RoundOverBudget_IsATypedStop()
    {
        var clock = new AdvancingTimeProvider();
        var renewCalls = 0;
        await using var renewal = NewRenewal(
            clock: clock,
            renew: (_, _, _, _) =>
            {
                renewCalls++;
                // A round that takes longer than the explicit budget: interval + round must stay < 300 s.
                clock.AdvanceMilliseconds(
                    (RunGrantRenewalOptions.RoundBudgetSeconds + 10) * 1000);
                return Task.FromResult(RunGrantRenewalOutcome.Success(1, 1, 0));
            });

        Assert.True(renewal.ObserveDispatch("run-1", "reocr_all", FrozenScope, boundPages: 1));
        var outcome = await renewal.TickAsync("run-1", CancellationToken.None);
        Assert.Equal(RunGrantRenewalKind.StoppedBudget, outcome.Kind);
        Assert.Equal("RENEWAL_ROUND_BUDGET_EXCEEDED", outcome.Code);
        Assert.Equal(1, renewCalls);
        Assert.False(renewal.IsTracking("run-1"));
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
        Func<IReadOnlyList<RunSourceScope>, string, JsonElement, CancellationToken, Task<RunAuthorizationResult>> authorize) =>
        new(
            enabled: true,
            knownTargets: () => known,
            registryEntries: () => entries,
            capabilityProbe: _ => Task.FromResult(probe),
            authorize: authorize,
            resolveRunSlice: (_, _) => throw new InvalidOperationException("no run slice expected"),
            info: _ => { },
            warn: _ => { },
            identities: cache);

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
}
