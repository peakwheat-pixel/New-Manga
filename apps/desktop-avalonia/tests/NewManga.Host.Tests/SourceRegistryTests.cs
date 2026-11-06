using System.Text;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

public sealed class SourceRegistryTests
{
    // ------------------------------------------------------------------
    // FEA-11-RUN-GRANT-1 (R-8/L-G7): the Run authorization ledger is bounded
    // ------------------------------------------------------------------

    [Fact]
    public void RunGrantLedgerIsBoundedAndPrunesExpiredGrants()
    {
        var now = 1000.0;
        var root = Path.Combine(FindRepository(), ".workspace", "FEA-11-RUN-GRANT-1",
            "fixtures", "ledger-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var registry = new SourceAccessRegistry(root);
        var coordinator = new SourceReadCoordinator(null!, registry, () => true, () => now);

        // Mint far more tracked ids than the frozen cap. ``Track`` is the same
        // accounting path every real issuance uses.
        for (var index = 0; index < SourceReadCoordinator.MaxTrackedPayloads * 2 + 7; index++)
        {
            coordinator.Track("source-" + index.ToString("D32"), "reg-run-grant", now + 300);
        }

        Assert.Equal(SourceReadCoordinator.MaxTrackedPayloads, coordinator.TrackedGrantCount);

        // Expiry prune: nothing survives the frozen 300s window.
        now += 301;
        Assert.True(coordinator.PruneExpired() > 0);
        Assert.Equal(0, coordinator.TrackedGrantCount);
        Assert.Equal(0, coordinator.TrackedPayloadCount);
        Assert.Empty(coordinator.IssuedGrantIds);
    }

    // ------------------------------------------------------------------
    // FEA-11-RUN-GRANT-1 (R-4/R-5): the Run authorization hook runs BEFORE
    // dispatch and only for the Run commands that trigger step execution.
    // ------------------------------------------------------------------

    [Fact]
    public async Task RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns()
    {
        var invoked = new List<string>();
        var dispatcher = new HostCommandDispatcher(
            runAuthorize: (name, _, _) =>
            {
                invoked.Add(name);
                throw new CoreOperationException(
                    "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null);
            });

        var startRun = JsonSerializer.SerializeToElement(new
        {
            command = "reocr_all",
            scope = new { kind = "page", page_id = "p1" },
            idempotency_key = "run-grant-hook",
        });
        var authorization = await Assert.ThrowsAsync<CoreOperationException>(
            () => dispatcher.InvokeAsync("library_start_run", startRun));
        // R-5: the authorization's own code is returned and the Run command is
        // never dispatched (a dispatched call would fail on the null Core with
        // a SidecarException instead).
        Assert.Equal("SOURCE_ACCESS_DENIED", authorization.Code);
        Assert.Equal(["library_start_run"], invoked);

        // Read-only Run commands never trigger the authorization hook.
        invoked.Clear();
        await Assert.ThrowsAnyAsync<Exception>(() => dispatcher.InvokeAsync(
            "library_get_run_snapshot", JsonSerializer.SerializeToElement(new { run_id = "run-1" })));
        await Assert.ThrowsAnyAsync<Exception>(() => dispatcher.InvokeAsync(
            "library_get_task_projection", JsonSerializer.SerializeToElement(new { run_id = "run-1" })));
        Assert.Empty(invoked);

        // The remaining step-triggering Run commands do call it (R-4).
        foreach (var (name, payload) in new (string, object)[]
                 {
                     ("library_control_run", new { run_id = "run-1", action = "restart", idempotency_key = "k" }),
                     ("library_resume_blocked_run", new { run_id = "run-1" }),
                     ("library_retry_failed_targets", new { run_id = "run-1", idempotency_key = "k" }),
                 })
        {
            invoked.Clear();
            var error = await Assert.ThrowsAsync<CoreOperationException>(
                () => dispatcher.InvokeAsync(name, JsonSerializer.SerializeToElement(payload)));
            Assert.Equal("SOURCE_ACCESS_DENIED", error.Code);
            Assert.Equal([name], invoked);
        }
    }

    [Fact]
    public async Task RunAuthorizationHookWithoutARefusalLetsTheRunCommandReachDispatch()
    {
        var invoked = new List<string>();
        var dispatcher = new HostCommandDispatcher(
            runAuthorize: (name, _, _) =>
            {
                invoked.Add(name);
                return Task.CompletedTask;
            });
        // No Core is wired: a hook that admits the Run must reach the real
        // dispatch path, which fails typed (not with the authorization code).
        var error = await Assert.ThrowsAsync<SidecarException>(() => dispatcher.InvokeAsync(
            "library_start_run",
            JsonSerializer.SerializeToElement(new
            {
                command = "reocr_all",
                scope = new { kind = "page", page_id = "p1" },
                idempotency_key = "run-grant-hook-ok",
            })));
        Assert.Equal(SidecarErrorCode.ProcessExited, error.Code);
        Assert.Equal(["library_start_run"], invoked);
    }

    [Fact]
    public void NativeDpapiCurrentUserRoundTripAndTamperRefusal()
    {
        var protector = new DpapiSecretProtector();
        var plaintext = Encoding.UTF8.GetBytes("synthetic-registry-payload");
        var ciphertext = protector.Protect(plaintext);
        Assert.False(ciphertext.SequenceEqual(plaintext));
        Assert.Equal(plaintext, protector.Unprotect(ciphertext));
        ciphertext[^1] ^= 0x42;
        Assert.Throws<SourceAccessException>(() => protector.Unprotect(ciphertext));
    }

    [Fact]
    public void EncryptedPersistenceGenerationCorruptionAndExplicitReset()
    {
        // This retained fixture is canonical evidence, not a production data root.
        var repo = FindRepository();
        var evidence = Path.Combine(repo, "verification", "FEA-09", "native-registry", Guid.NewGuid().ToString("N"));
        var source = Path.Combine(evidence, "synthetic-source");
        Directory.CreateDirectory(source);
        File.WriteAllText(Path.Combine(source, "page.txt"), "synthetic source bytes");
        var registry = new SourceAccessRegistry(Path.Combine(evidence, "isolated-data"));
        var entry = registry.Register("synthetic", [source]);
        Assert.Equal(1, entry.Generation);
        var reopened = new SourceAccessRegistry(Path.Combine(evidence, "isolated-data"));
        Assert.Equal(entry.RegistryId, Assert.Single(reopened.List()).RegistryId);
        Assert.Equal(1, reopened.Authorize(entry.RegistryId, 1, [Path.Combine(source, "page.txt")]).Generation);
        var revoked = reopened.Revoke(entry.RegistryId);
        Assert.Equal(2, revoked.Generation);
        Assert.Equal("SOURCE_GRANT_REVOKED", Assert.Throws<SourceAccessException>(() => reopened.Authorize(entry.RegistryId, 2, [source])).Code);
        var bytes = File.ReadAllBytes(registry.RegistryPath);
        Assert.StartsWith("NMSAR1", Encoding.ASCII.GetString(bytes, 0, 6));
        Assert.DoesNotContain(source, Encoding.UTF8.GetString(bytes));
        File.WriteAllBytes(registry.RegistryPath, [1, 2, 3]);
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", Assert.Throws<SourceAccessException>(() => reopened.List()).Code);
        Assert.Equal(new byte[] { 1, 2, 3 }, File.ReadAllBytes(registry.RegistryPath));
        Assert.NotEmpty(Directory.GetFiles(Path.GetDirectoryName(registry.RegistryPath)!, "*.corrupt-*"));
        Assert.Equal("INVALID_REQUEST", Assert.Throws<SourceAccessException>(() => reopened.Reset(false)).Code);
        Assert.True(Directory.Exists(reopened.Reset(true)));
        Assert.Empty(reopened.List());
    }

    // ==================================================================
    // Review r1 rework (R1-01 / R1-02 / R1-04): the Run pre-authorization
    // orchestration is a standalone, best-effort, unit-testable seam.
    // ==================================================================

    private static SourceScanTarget ScanTarget(string sourceId, string path, params string[] projectIds) =>
        new(sourceId, path, projectIds, "1");

    /// <summary>FEA-11-RUN-GRANT-2A (S-2): a warm Core-authoritative identity cache. The scan targets
    /// keep the production placeholder version "1"; only this cache may supply the minting version.</summary>
    private static SourceIdentityCache WarmCache(params (string SourceId, string Version)[] identities)
    {
        var cache = new SourceIdentityCache();
        foreach (var (sourceId, version) in identities)
        {
            Assert.True(cache.Remember(sourceId, version, []), "warm cache identity");
        }
        return cache;
    }

    private static SourceAuthorization RegistryEntry(string registryId, string root, int generation = 1) =>
        new(registryId, root, generation, "t", "t", null,
            [new SourceRoot(root, 0, 0, "t", true)]);

    private static System.Text.Json.JsonElement Json(string raw) =>
        System.Text.Json.JsonDocument.Parse(raw).RootElement.Clone();

    private static string NewSourceDirectory(out string file)
    {
        var directory = Path.Combine(
            Path.GetTempPath(), "newmanga-run-grant-" + Guid.NewGuid().ToString("N")[..12]);
        Directory.CreateDirectory(directory);
        file = Path.Combine(directory, "source.zip");
        File.WriteAllBytes(file, [0x50, 0x4b, 0x05, 0x06, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
        return directory;
    }

    private static RunSourceAuthorizer Authorizer(
        bool probe,
        IReadOnlyList<SourceScanTarget>? known,
        IReadOnlyList<SourceAuthorization>? entries,
        Func<IReadOnlyList<RunSourceScope>, string, System.Text.Json.JsonElement, CancellationToken, Task<RunAuthorizationResult>> authorize,
        Func<string, CancellationToken, Task<(string Command, System.Text.Json.JsonElement Scope)>>? resolve = null,
        List<string>? warnings = null,
        SourceIdentityCache? identities = null,
        Func<SourceScanTarget, CancellationToken, Task>? onDemandScan = null) =>
        new(true,
            () => known ?? Array.Empty<SourceScanTarget>(),
            () => entries ?? Array.Empty<SourceAuthorization>(),
            _ => Task.FromResult(probe),
            authorize,
            resolve ?? ((_, _) => throw new InvalidOperationException("no run slice expected")),
            _ => { },
            message => warnings?.Add(message),
            identities ?? new SourceIdentityCache(),
            onDemandScan);

    [Fact]
    public void RunCommandPolicyAuthorizesOnlyStepTriggeringCommands()
    {
        var empty = Json("{}");
        foreach (var name in new[]
                 {
                     "library_start_run", "library_resume_blocked_run",
                     "library_retry_failed_targets",
                 })
        {
            Assert.True(RunCommandPolicy.TriggersStepExecution(name, empty), name);
        }
        Assert.True(RunCommandPolicy.TriggersStepExecution(
            "library_control_run", Json("""{"action":"continue"}""")));
        Assert.True(RunCommandPolicy.TriggersStepExecution(
            "library_control_run", Json("""{"action":"restart"}""")));
        foreach (var action in new[] { "pause", "stop", "abandon" })
        {
            Assert.False(RunCommandPolicy.TriggersStepExecution(
                "library_control_run", Json($$"""{"action":"{{action}}"}""")), action);
        }
        Assert.False(RunCommandPolicy.TriggersStepExecution(
            "library_control_run", Json("{}")));
        foreach (var readOnly in new[]
                 {
                     "library_get_run_snapshot", "library_get_task_projection",
                     "library_list_books",
                 })
        {
            Assert.False(RunCommandPolicy.TriggersStepExecution(readOnly, empty), readOnly);
        }
    }

    [Fact]
    public void RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources()
    {
        var root = NewSourceDirectory(out var file);
        var outside = NewSourceDirectory(out var outsideFile);
        var entries = new[] { RegistryEntry("reg-1", root) };
        var known = new[]
        {
            ScanTarget("s1", file, "b1"),
            ScanTarget("s2", file, "b2"),
            // Inside the authorized root but the file is gone: it resolves to a
            // scope here and the MINT is what fails (best-effort skip).
            ScanTarget("s3", Path.Combine(root, "missing.zip"), "b1"),
            // Outside every authorized root: unresolvable at range resolution.
            ScanTarget("s4", outsideFile, "b1"),
        };

        var targets = RunSourceRange.Resolve(
            known, Json("""{"kind":"book","book_id":"b1"}"""), entries,
            WarmCache(("s1", "sv-core-1"), ("s2", "sv-core-2"), ("s3", "sv-core-3")));
        Assert.Equal(["s1", "s3"], targets.Targets.Select(target => target.SourceId));
        Assert.Equal("sv-core-1", targets.Targets[0].Version);
        Assert.NotEqual("1", targets.Targets[0].Version);
        Assert.Empty(targets.ColdSources);
        Assert.Equal(1, targets.Unresolved); // s4 outside the authorized root
        _ = outside;

        var all = RunSourceRange.Resolve(
            known, Json("""{"kind":"page","page_id":"p1"}"""), entries,
            WarmCache(("s1", "sv-core-1"), ("s2", "sv-core-2"), ("s3", "sv-core-3")));
        Assert.Equal(["s1", "s2", "s3"], all.Targets.Select(target => target.SourceId));
        Assert.Equal(1, all.Unresolved);

        Assert.Empty(RunSourceRange.Resolve(
            Array.Empty<SourceScanTarget>(),
            Json("""{"kind":"page","page_id":"p1"}"""), entries, new SourceIdentityCache()).Targets);
        Assert.Empty(RunSourceRange.Resolve(
            known, Json("""{"kind":"book","book_id":"b9"}"""), entries,
            WarmCache(("s1", "sv-core-1"))).Targets);
    }

    [Fact]
    public async Task RunAuthorizerSkipsWhenTheRegistryCannotBeRead()
    {
        var root = NewSourceDirectory(out var file);
        var warnings = new List<string>();
        // A registry that cannot list its entries is a skip (no throw): the
        // caller keeps dispatching (R1-01).
        var failing = new RunSourceAuthorizer(
            true, () => [ScanTarget("s1", file, "b1")],
            () => throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE"),
            _ => Task.FromResult(true),
            (_, _, _, _) => throw new InvalidOperationException("must not mint"),
            (_, _) => throw new InvalidOperationException("must not resolve"),
            _ => { }, message => warnings.Add(message),
            new SourceIdentityCache());
        await failing.AuthorizeForCommandAsync(
            "library_start_run",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"}}"""),
            CancellationToken.None);
        Assert.Contains(warnings, message => message.Contains("skipped", StringComparison.Ordinal));
        _ = root;
    }

    [Fact]
    public async Task RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting()
    {
        // Review r2 R2-02 (discriminating): a REAL known source set means the
        // capability gate is the only thing that can prevent the mint — removing
        // the gate makes `minted` become 1 and this test red.
        var root = NewSourceDirectory(out var file);
        var minted = 0;
        var authorizer = Authorizer(
            probe: false,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => { minted++; return Task.FromResult(new RunAuthorizationResult(1, 1, 0, [])); });
        await authorizer.AuthorizeSliceAsync(
            "reocr_all",
            Json("""{"kind":"page","page_id":"p1"}"""),
            CancellationToken.None);
        Assert.Equal(0, minted);
    }

    [Fact]
    public async Task RunAuthorizerCapabilityMissingStillReachesDispatch()
    {
        // R2-02/R2-01: with a known source present, a missing capability must
        // SKIP the authorization and let the Run command reach dispatch (no
        // Core is wired -> SidecarException proves the dispatch was attempted).
        var root = NewSourceDirectory(out var file);
        var authorizer = Authorizer(
            probe: false,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => throw new InvalidOperationException("must not mint"));
        var dispatcher = new HostCommandDispatcher(
            runAuthorize: (name, payload, token) =>
                authorizer.AuthorizeForCommandAsync(name, payload, token));
        var dispatched = await Assert.ThrowsAsync<SidecarException>(() => dispatcher.InvokeAsync(
            "library_start_run",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"},"idempotency_key":"k"}""")));
        Assert.Equal(SidecarErrorCode.ProcessExited, dispatched.Code);
    }

    [Fact]
    public void RunSourceRangeKindDetectsFolderSources()
    {
        // R2-01: the extension-only guess classified every folder as "image"
        // (mint then opened the directory as a file and skipped the source).
        var folder = NewSourceDirectory(out var insideFile);
        var fileDir = NewSourceDirectory(out var archive);
        _ = insideFile;
        Assert.Equal("folder", RunSourceRange.KindOfSource(
            ScanTarget("f1", folder, "b1"), folder));
        // A declared folder kind wins even for a path that looks like a file.
        var declaredFolder = ScanTarget("f2", archive, "b1") with { SourceKind = "folder" };
        Assert.Equal("folder", RunSourceRange.KindOfSource(declaredFolder, archive));
        // Container / image kinds keep their frozen names.
        Assert.Equal("zip", RunSourceRange.KindOfSource(ScanTarget("s1", archive, "b1"), archive));
        var image = Path.Combine(fileDir, "page.png");
        File.WriteAllBytes(image, [0x89, 0x50, 0x4e, 0x47]);
        Assert.Equal("image", RunSourceRange.KindOfSource(ScanTarget("i1", image, "b1"), image));
        // Declared kind is authoritative when the caller already knows it.
        Assert.Equal("zip", RunSourceRange.KindOfSource(
            ScanTarget("s2", archive, "b1") with { SourceKind = "zip" }, archive));
    }

    [Fact]
    public async Task AcceptRunAuthorizationSeamUsesTheFrozenSlice()
    {
        // R2-03: the production HostRuntime.AcceptRunAsync delegates to this
        // seam; deleting the authorizer call makes this test red.
        var root = NewSourceDirectory(out var file);
        var calls = new List<(string Command, string PageId)>();
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, command, scope, _) =>
            {
                calls.Add((command, scope.GetProperty("page_id").GetString()!));
                return Task.FromResult(new RunAuthorizationResult(1, 1, 0, []));
            },
            identities: WarmCache(("s1", "sv-core-1")));
        var now = DateTimeOffset.Parse("2026-11-07T00:00:00+00:00");
        var slices = new PreparedRunSlices(() => now);
        Assert.True(slices.Remember(
            "prepared-accept",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"}}"""),
            now.AddMinutes(5)));
        await HostRuntime.AuthorizePreparedRunForAcceptAsync(
            slices, authorizer, "prepared-accept", CancellationToken.None);
        Assert.Equal(("reocr_all", "p1"), Assert.Single(calls));
    }

    [Fact]
    public async Task AcceptRunAuthorizationSeamIsTypedWithoutAUsableSlice()
    {
        var root = NewSourceDirectory(out var file);
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => throw new InvalidOperationException("must not authorize"));
        var now = DateTimeOffset.Parse("2026-11-07T00:00:00+00:00");
        var slices = new PreparedRunSlices(() => now);

        // Missing prepared run (never prepared in this Host process).
        var missing = await Assert.ThrowsAsync<CoreOperationException>(() =>
            HostRuntime.AuthorizePreparedRunForAcceptAsync(
                slices, authorizer, "prepared-unknown", CancellationToken.None));
        Assert.Equal("RUN_STALE_PREVIEW", missing.Code);

        // Expired prepared run.
        Assert.True(slices.Remember(
            "prepared-expired",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"}}"""),
            now.AddSeconds(30)));
        now = now.AddSeconds(31);
        var expired = await Assert.ThrowsAsync<CoreOperationException>(() =>
            HostRuntime.AuthorizePreparedRunForAcceptAsync(
                slices, authorizer, "prepared-expired", CancellationToken.None));
        Assert.Equal("RUN_STALE_PREVIEW", expired.Code);

        // The slice ledger is consulted even when no authorizer exists (the
        // pre-R1-11 direct pass-through is intentionally gone).
        var noAuthorizer = await Assert.ThrowsAsync<CoreOperationException>(() =>
            HostRuntime.AuthorizePreparedRunForAcceptAsync(
                slices, null, "prepared-missing", CancellationToken.None));
        Assert.Equal("RUN_STALE_PREVIEW", noAuthorizer.Code);
    }

    [Fact]
    public async Task RunAuthorizerTreatsMintFailuresAsBestEffortSkips()
    {
        var root = NewSourceDirectory(out var file);
        var warnings = new List<string>();
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => throw new SourceAccessException("SOURCE_ENTRY_MISSING"),
            warnings: warnings,
            identities: WarmCache(("s1", "sv-core-1")));
        // No exception: the dispatch must continue (R1-01).
        await authorizer.AuthorizeForCommandAsync(
            "library_start_run",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"}}"""),
            CancellationToken.None);
        Assert.Contains(warnings, message => message.Contains("skipped", StringComparison.Ordinal));
    }

    [Fact]
    public async Task RunAuthorizerPropagatesOnlyACoreTypedPageRefusal()
    {
        var root = NewSourceDirectory(out var file);
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => throw new CoreOperationException(
                "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null),
            identities: WarmCache(("s1", "sv-core-1")));
        var error = await Assert.ThrowsAsync<CoreOperationException>(() =>
            authorizer.AuthorizeForCommandAsync(
                "library_start_run",
                Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"}}"""),
                CancellationToken.None));
        Assert.Equal("SOURCE_ACCESS_DENIED", error.Code);
    }

    [Fact]
    public async Task RunAuthorizerControlActionsPauseStopDoNotAuthorize()
    {
        var minted = 0;
        var resolved = 0;
        var authorizer = Authorizer(
            probe: true, known: [], entries: [],
            authorize: (_, _, _, _) => { minted++; return Task.FromResult(new RunAuthorizationResult(0, 0, 0, [])); },
            resolve: (_, _) => { resolved++; return Task.FromResult(("reocr_all", Json("{}"))); });
        foreach (var action in new[] { "pause", "stop", "abandon" })
        {
            await authorizer.AuthorizeForCommandAsync(
                "library_control_run", Json($$"""{"action":"{{action}}","run_id":"r1"}"""),
                CancellationToken.None);
        }
        Assert.Equal(0, minted);
        Assert.Equal(0, resolved);
    }

    [Fact]
    public async Task RunAuthorizerControlContinueResolvesTheFrozenSliceAndAuthorizes()
    {
        var root = NewSourceDirectory(out var file);
        var seen = new List<(string Command, string Scope)>();
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (scopes, command, scope, _) =>
            {
                seen.Add((command, scope.GetProperty("page_id").GetString()!));
                return Task.FromResult(new RunAuthorizationResult(1, scopes.Count, 0, []));
            },
            resolve: (runId, _) => Task.FromResult((
                "reocr_all",
                Json("""{"kind":"page","page_id":"p1"}"""))),
            identities: WarmCache(("s1", "sv-core-1")));
        await authorizer.AuthorizeForCommandAsync(
            "library_control_run", Json("""{"action":"continue","run_id":"run-1"}"""),
            CancellationToken.None);
        Assert.Equal(("reocr_all", "p1"), Assert.Single(seen));
    }

    [Fact]
    public async Task RunAuthorizerAcceptSeamUsesThePreparedSliceCommandAndScope()
    {
        var root = NewSourceDirectory(out var file);
        var seen = new List<string>();
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, command, _, _) =>
            {
                seen.Add(command);
                return Task.FromResult(new RunAuthorizationResult(1, 1, 0, []));
            },
            identities: WarmCache(("s1", "sv-core-1")));
        await authorizer.AuthorizePreparedRunAsync(
            "reocr_all", Json("""{"kind":"page","page_id":"p1"}"""), CancellationToken.None);
        Assert.Equal(["reocr_all"], seen);
        // The AcceptRun path in HostRuntime takes the command/scope from the
        // prepared-run slice ledger and feeds exactly this seam.
    }

    [Fact]
    public void PreparedRunSlicesTakeRequiresASameProcessPreparedRun()
    {
        var now = DateTimeOffset.Parse("2026-11-07T00:00:00+00:00");
        var slices = new PreparedRunSlices(() => now);
        var request = Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"}}""");
        Assert.True(slices.Remember("prepared-1", request, now.AddMinutes(5)));
        var (command, scope) = slices.Take("prepared-1");
        Assert.Equal("reocr_all", command);
        Assert.Equal("p1", scope.GetProperty("page_id").GetString());

        // Missing slice -> the frozen host-side typed refusal (R1-11).
        var missing = Assert.Throws<CoreOperationException>(() => slices.Take("prepared-unknown"));
        Assert.Equal("RUN_STALE_PREVIEW", missing.Code);

        // Expired slice is no longer usable.
        Assert.True(slices.Remember("prepared-2", request, now.AddSeconds(30)));
        now = now.AddSeconds(31);
        var expired = Assert.Throws<CoreOperationException>(() => slices.Take("prepared-2"));
        Assert.Equal("RUN_STALE_PREVIEW", expired.Code);

        // Malformed requests are not remembered; the ledger stays bounded.
        Assert.False(slices.Remember("prepared-bad", Json("""{"command":"reocr_all"}"""), now.AddMinutes(5)));
        for (var index = 0; index < PreparedRunSlices.MaxEntries * 2; index++)
        {
            slices.Remember("prepared-" + index, request, now.AddMinutes(10));
        }
        Assert.Equal(PreparedRunSlices.MaxEntries, slices.Count);
    }

    [Fact]
    public void RunSourceAuthorizerMapsMintIoFailuresToFrozenCodes()
    {
        Assert.Equal("SOURCE_ENTRY_MISSING",
            SourceReadCoordinator.MapMintFailure(new FileNotFoundException()).Code);
        Assert.Equal("SOURCE_ENTRY_MISSING",
            SourceReadCoordinator.MapMintFailure(new UnauthorizedAccessException()).Code);
        Assert.Equal("FILE_IDENTITY_CHANGED",
            SourceReadCoordinator.MapMintFailure(new IOException()).Code);
        Assert.Equal("SOURCE_ACCESS_DENIED",
            SourceReadCoordinator.MapMintFailure(new ArgumentException()).Code);
    }

    [Fact]
    public async Task RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot()
    {
        var root = NewSourceDirectory(out var file);
        var request = Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"},"idempotency_key":"k"}""");

        // (a) Host-side mint failure -> the Run command reaches dispatch (no Core
        // is wired, so dispatch itself fails typed: proof it was NOT blocked by
        // the pre-authorization).
        var skipping = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => throw new SourceAccessException("SOURCE_ENTRY_MISSING"),
            identities: WarmCache(("s1", "sv-core-1")));
        var dispatching = new HostCommandDispatcher(
            runAuthorize: (name, payload, token) =>
                skipping.AuthorizeForCommandAsync(name, payload, token));
        var dispatched = await Assert.ThrowsAsync<SidecarException>(() =>
            dispatching.InvokeAsync("library_start_run", request));
        Assert.Equal(SidecarErrorCode.ProcessExited, dispatched.Code);

        // (b) Core typed page refusal -> the Run command is NOT dispatched and
        // the authorization code is returned unchanged.
        var refusing = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => throw new CoreOperationException(
                "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null),
            identities: WarmCache(("s1", "sv-core-1")));
        var blocked = new HostCommandDispatcher(
            runAuthorize: (name, payload, token) =>
                refusing.AuthorizeForCommandAsync(name, payload, token));
        var refusal = await Assert.ThrowsAsync<CoreOperationException>(() =>
            blocked.InvokeAsync("library_start_run", request));
        Assert.Equal("SOURCE_ACCESS_DENIED", refusal.Code);
    }

    // ==================================================================
    // FEA-11-RUN-GRANT-2A (card S-2/S-3/S-4/S-6, AC-G1…G3/G6): the Core
    // version channel (scan response -> identity cache -> Run mint), the
    // bounded cold-cache policy and the AcceptRun delegation line.
    // ==================================================================

    /// <summary>One production-shaped <c>ScanSourceSync</c> result (the projection the Host projects).</summary>
    private static string ScanObservation(
        string sourceId,
        string status,
        string? versionId,
        int added = 0,
        int changed = 0,
        string entriesJson = """[{"entry_id":"se1","locator":"001.png","ordinal":0}]""")
    {
        var version = versionId is null ? "null" : "\"" + versionId + "\"";
        return "{\"source\":{\"source_id\":\"" + sourceId + "\",\"version_id\":" + version
            + ",\"status\":\"" + status + "\",\"identity_digest\":\"" + new string('a', 64)
            + "\",\"entries\":" + entriesJson + "},"
            + "\"totals\":{\"unchanged\":1,\"added\":" + added + ",\"missing\":0,\"changed\":"
            + changed + ",\"ambiguous\":0}}";
    }

    private static HostRuntime CreateUnstartedHostRuntime(HostOptions options, HostLog log)
    {
        var constructor = typeof(HostRuntime).GetConstructor(
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic,
            binder: null,
            [typeof(HostOptions), typeof(HostLog)],
            modifiers: null) ?? throw new InvalidOperationException("HostRuntime ctor not found");
        return (HostRuntime)constructor.Invoke([options, log]);
    }

    private static object? ReadPrivate(object instance, string name) =>
        instance.GetType()
            .GetField(name, System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!
            .GetValue(instance);

    private static void WritePrivate(object instance, string name, object value) =>
        instance.GetType()
            .GetField(name, System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!
            .SetValue(instance, value);

    [Fact]
    public void SourceIdentityCacheIsBoundedAndPrunesExpiredEntries()
    {
        // AC-G2 (S-4): the cache is in-memory, keyed by source_id, bounded by MaxEntries and prunes
        // expired entries. A placeholder version/entry can never be remembered.
        var now = 1000.0;
        var cache = new SourceIdentityCache(() => now);
        Assert.True(cache.Remember("s0", "sv-committed", []));
        Assert.True(cache.TryGet("s0", out var first));
        Assert.Equal("sv-committed", first.VersionId);
        Assert.False(cache.Remember(" ", "sv-x", []));
        Assert.False(cache.Remember("s-x", " ", []));
        Assert.False(cache.Remember(
            "s-x", "sv-x",
            Enumerable.Range(0, SourceIdentityCache.MaxEntriesPerIdentity + 1)
                .Select(index => new SourceIdentityEntry("entry-" + index, "m" + index, index))
                .ToArray()));

        now += SourceIdentityCache.DefaultTtlSeconds + 1;
        Assert.True(cache.PruneExpired() >= 1);
        Assert.False(cache.TryGet("s0", out _));

        for (var index = 0; index < SourceIdentityCache.MaxEntries + 25; index++)
        {
            Assert.True(cache.Remember("s" + index, "sv-" + index, []));
        }
        Assert.Equal(SourceIdentityCache.MaxEntries, cache.Count);
        Assert.True(cache.Remember("s-new", "sv-new", [new SourceIdentityEntry("se1", "001.png", 0)]));
        Assert.True(cache.TryGet("s-new", out var newest));
        Assert.Equal(("se1", "001.png", 0), (newest.Entries[0].EntryId, newest.Entries[0].Locator, newest.Entries[0].Ordinal));
    }

    [Fact]
    public void SourceScanResponseRefreshesTheCacheOnlyWhenUnchangedAndOk()
    {
        // AC-G2 discriminating matrix: only status=ok + changed=false may refresh; every other
        // observation INVALIDATES the entry instead of caching a candidate version (a `changed`
        // overwrite would make this test red — break B2).
        var cache = new SourceIdentityCache(() => 1000.0);
        HostSourceScanExecutor.ApplySourceIdentity(cache, "s1", Json(ScanObservation("s1", "ok", "sv-committed")));
        Assert.True(cache.TryGet("s1", out var identity));
        Assert.Equal("sv-committed", identity.VersionId);
        Assert.Single(identity.Entries);

        // A changed observation carries the NEW candidate version (not Core-committed): it must not
        // replace the cache, and the fail-closed outcome is "no identity" (skip, never a guess).
        HostSourceScanExecutor.ApplySourceIdentity(
            cache, "s1", Json(ScanObservation("s1", "ok", "sv-candidate", changed: 1)));
        Assert.False(cache.TryGet("s1", out _));
        Assert.False(HostSourceScanExecutor.ReadSourceIdentity(
            Json(ScanObservation("s1", "ok", "sv-candidate", changed: 1)), "s1").Cacheable);

        foreach (var (status, reason) in new[]
                 {
                     ("missing", "status_missing"),
                     ("encrypted", "status_encrypted"),
                     ("unsupported", "status_unsupported"),
                 })
        {
            HostSourceScanExecutor.ApplySourceIdentity(cache, "s1", Json(ScanObservation("s1", "ok", "sv-committed")));
            Assert.True(cache.TryGet("s1", out _));
            var verdict = HostSourceScanExecutor.ReadSourceIdentity(
                Json(ScanObservation("s1", status, "sv-candidate")), "s1");
            Assert.False(verdict.Cacheable);
            Assert.Equal(reason, verdict.Reason);
            HostSourceScanExecutor.ApplySourceIdentity(cache, "s1", Json(ScanObservation("s1", status, "sv-candidate")));
            Assert.False(cache.TryGet("s1", out _));
        }

        // Malformed / mismatched / missing-version observations never become a cached identity.
        Assert.False(HostSourceScanExecutor.ReadSourceIdentity(
            Json(ScanObservation("other", "ok", "sv-committed")), "s1").Cacheable);
        Assert.Equal("source_id_mismatch", HostSourceScanExecutor.ReadSourceIdentity(
            Json(ScanObservation("other", "ok", "sv-committed")), "s1").Reason);
        Assert.Equal("version_missing", HostSourceScanExecutor.ReadSourceIdentity(
            Json(ScanObservation("s1", "ok", null)), "s1").Reason);
        Assert.Equal("entries_missing", HostSourceScanExecutor.ReadSourceIdentity(
            Json(ScanObservation("s1", "ok", "sv-committed", entriesJson: "\"not-an-array\"")), "s1").Reason);
        Assert.Equal("entry_malformed", HostSourceScanExecutor.ReadSourceIdentity(
            Json(ScanObservation("s1", "ok", "sv-committed", entriesJson: """[{"locator":"001.png"}]""")), "s1").Reason);
    }

    [Fact]
    public void RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources()
    {
        // AC-G1: the minting version is the Core-authoritative cached version; the scan target's
        // constant placeholder ("1") is never used, and a cold source is reported instead of minted.
        var root = NewSourceDirectory(out var file);
        var entries = new[] { RegistryEntry("reg-1", root) };
        var known = new[] { ScanTarget("s1", file, "b1") };
        var scope = Json("""{"kind":"page","page_id":"p1"}""");

        var cold = RunSourceRange.Resolve(known, scope, entries, new SourceIdentityCache());
        Assert.Empty(cold.Targets);
        Assert.Equal("s1", Assert.Single(cold.ColdSources).SourceId);
        Assert.Equal(0, cold.Unresolved);

        var warm = RunSourceRange.Resolve(
            known, scope, entries, WarmCache(("s1", "sv-core-committed")));
        var target = Assert.Single(warm.Targets);
        Assert.Equal("sv-core-committed", target.Version);
        Assert.NotEqual("1", target.Version);
        Assert.Empty(warm.ColdSources);
    }

    [Fact]
    public async Task RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch()
    {
        // AC-G3 (break B3): with no Core-proven version the source is SKIPPED; deleting that branch
        // (minting with the placeholder "1") makes the Core refuse typed and blocks a managed Run.
        var root = NewSourceDirectory(out var file);
        var authorizeCalls = 0;
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) =>
            {
                authorizeCalls++;
                // The real Core refuses a version that does not match the page binding.
                throw new CoreOperationException(
                    "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null);
            },
            identities: new SourceIdentityCache());
        var dispatcher = new HostCommandDispatcher(
            runAuthorize: (name, payload, token) =>
                authorizer.AuthorizeForCommandAsync(name, payload, token));
        var dispatched = await Assert.ThrowsAsync<SidecarException>(() => dispatcher.InvokeAsync(
            "library_start_run",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"},"idempotency_key":"k"}""")));
        Assert.Equal(SidecarErrorCode.ProcessExited, dispatched.Code); // dispatch was reached
        Assert.Equal(0, authorizeCalls);
    }

    [Fact]
    public async Task RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource()
    {
        // AC-G3 (break B4): a cold cache triggers exactly ONE bounded on-demand scan per source; the
        // second slice finds the cache warm and never scans again.
        var root = NewSourceDirectory(out var file);
        var cache = new SourceIdentityCache();
        var scans = new List<string>();
        var versions = new List<string>();
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (targets, _, _, _) =>
            {
                versions.Add(targets.Single().Version);
                return Task.FromResult(new RunAuthorizationResult(1, 1, 0, []));
            },
            identities: cache,
            onDemandScan: (target, _) =>
            {
                scans.Add(target.SourceId);
                cache.Remember(target.SourceId, "sv-from-scan", []);
                return Task.CompletedTask;
            });
        var scope = Json("""{"kind":"page","page_id":"p1"}""");
        await authorizer.AuthorizeSliceAsync("reocr_all", scope, CancellationToken.None);
        Assert.Equal(["s1"], scans);
        Assert.Equal(["sv-from-scan"], versions);

        await authorizer.AuthorizeSliceAsync("reocr_all", scope, CancellationToken.None);
        Assert.Equal(["s1"], scans); // warm cache: no second on-demand scan
        Assert.Equal(["sv-from-scan", "sv-from-scan"], versions);
    }

    [Fact]
    public async Task RunAuthorizerOnDemandScanBudgetIsExplicitAndBounded()
    {
        // AC-G3: the per-slice on-demand budget is explicit; the surplus cold sources are skipped
        // (counted), never scanned in a loop.
        var root = NewSourceDirectory(out var file);
        var scans = 0;
        var warnings = new List<string>();
        var known = Enumerable.Range(0, RunSourceAuthorizer.MaxOnDemandScansPerSlice + 4)
            .Select(index => ScanTarget("s" + index, file, "b1"))
            .ToArray();
        var authorizer = Authorizer(
            probe: true,
            known: known,
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => throw new InvalidOperationException("must not authorize"),
            warnings: warnings,
            identities: new SourceIdentityCache(),
            onDemandScan: (_, _) => { scans++; return Task.CompletedTask; /* still cold */ });
        await authorizer.AuthorizeSliceAsync(
            "reocr_all", Json("""{"kind":"page","page_id":"p1"}"""), CancellationToken.None);
        Assert.Equal(RunSourceAuthorizer.MaxOnDemandScansPerSlice, scans);
        Assert.Contains(warnings, message => message.Contains("on_demand_budget_exhausted=4", StringComparison.Ordinal));
        // The failed fills leave every source cold; the authorization is skipped (counted only).
        Assert.Contains(warnings, message => message.Contains("cold_sources=12", StringComparison.Ordinal));
        Assert.Contains(warnings, message => message.Contains("on_demand_attempts=8", StringComparison.Ordinal));
    }

    [Fact]
    public async Task RunAuthorizerOnDemandScanFailureIsASkipNotABlock()
    {
        // AC-G3: a failed/timeout on-demand scan is a best-effort skip; the Run command still reaches
        // dispatch (no Core wired -> the dispatcher's own typed failure proves the dispatch happened).
        var root = NewSourceDirectory(out var file);
        var authorizeCalls = 0;
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, _, _, _) => { authorizeCalls++; return Task.FromResult(new RunAuthorizationResult(1, 1, 0, [])); },
            identities: new SourceIdentityCache(),
            onDemandScan: (_, _) => throw new IOException("synthetic scan failure"));
        var dispatcher = new HostCommandDispatcher(
            runAuthorize: (name, payload, token) =>
                authorizer.AuthorizeForCommandAsync(name, payload, token));
        var dispatched = await Assert.ThrowsAsync<SidecarException>(() => dispatcher.InvokeAsync(
            "library_start_run",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"},"idempotency_key":"k"}""")));
        Assert.Equal(SidecarErrorCode.ProcessExited, dispatched.Code);
        Assert.Equal(0, authorizeCalls);
    }

    [Fact]
    public async Task AcceptRunAsyncDelegatesToTheAuthorizationSeam()
    {
        // R3-02 / AC-G6 (break B5): the R2-03 seam tests cover the seam; THIS case discriminates the
        // production AcceptRunAsync delegation LINE itself. With the call deleted, AcceptRunAsync
        // falls through to the (unstarted) Core and throws a different error -> red.
        var root = NewSourceDirectory(out var file);
        var dataRoot = Path.Combine(root, "host-data");
        var logRoot = Path.Combine(root, "host-logs");
        Directory.CreateDirectory(dataRoot);
        var options = new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = logRoot,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
        };
        await using var runtime = CreateUnstartedHostRuntime(options, new HostLog(logRoot));
        // The real start path derives a writable policy from the data-root decision.
        WritePrivate(runtime, "_policy", DataRootPolicy.For(dataRoot, HostMode.ReadWrite));
        var slices = (PreparedRunSlices)ReadPrivate(runtime, "_preparedSlices")!;
        Assert.True(slices.Remember(
            "prepared-r302",
            Json("""{"command":"reocr_all","scope":{"kind":"page","page_id":"p1"}}"""),
            DateTimeOffset.UtcNow.AddMinutes(5)));
        var requested = new List<string>();
        WritePrivate(runtime, "_runAuthorizer", Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (_, command, _, _) =>
            {
                requested.Add(command);
                throw new CoreOperationException(
                    "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null);
            },
            identities: WarmCache(("s1", "sv-core-1"))));

        var error = await Assert.ThrowsAsync<CoreOperationException>(
            () => runtime.AcceptRunAsync("prepared-r302", 1, "idempotency-key"));
        Assert.Equal("SOURCE_ACCESS_DENIED", error.Code);
        Assert.Equal(["reocr_all"], requested);
    }

    // ==================================================================
    // FEA-11-RUN-GRANT-2 (2B, C-16 v1.4 §2): container member entries
    // ==================================================================

    private static SourceIdentityCache WarmContainerCache(
        string sourceId, string version, params (string Locator, int Ordinal)[] members)
    {
        var cache = new SourceIdentityCache();
        Assert.True(cache.Remember(
            sourceId, version,
            members.Select(item => new SourceIdentityEntry(null, item.Locator, item.Ordinal)).ToArray()));
        return cache;
    }

    [Fact]
    public void RunSourceRangeCarriesContainerMemberIdentitiesVerbatim()
    {
        // AC-H3 / card S-5: only zip/cbz/pdf scopes carry member identities, and they are the CACHED
        // Core values VERBATIM (never inferred from the container, never renumbered to 0..N-1);
        // image and folder keep their frozen shapes.
        var root = NewSourceDirectory(out var file);
        var entries = new[] { RegistryEntry("reg-1", root) };
        var scope = Json("""{"kind":"page","page_id":"p1"}""");
        var imagePath = Path.Combine(root, "page.png");
        File.WriteAllBytes(imagePath, [0x89, 0x50, 0x4e, 0x47]);
        var cache = new SourceIdentityCache();
        Assert.True(cache.Remember("s1", "sv-core",
            [new SourceIdentityEntry(null, "001.png", 0), new SourceIdentityEntry(null, "002.png", 5),
             new SourceIdentityEntry(null, "003.png", 9)]));
        Assert.True(cache.Remember("i1", "sv-img", [new SourceIdentityEntry(null, "page.png", 0)]));
        var resolution = RunSourceRange.Resolve(
            [ScanTarget("s1", file, "b1"), ScanTarget("i1", imagePath, "b1")], scope, entries, cache);
        var archive = resolution.Targets.Single(target => target.SourceId == "s1");
        Assert.NotNull(archive.ContainerEntries);
        Assert.Equal(["001.png", "002.png", "003.png"], archive.ContainerEntries!.Select(m => m.Locator));
        Assert.Equal([0, 5, 9], archive.ContainerEntries!.Select(m => m.Ordinal));
        Assert.Null(resolution.Targets.Single(target => target.SourceId == "i1").ContainerEntries);

        // cbz/pdf share the frozen container semantics.
        foreach (var kind in new[] { "cbz", "pdf" })
        {
            var containerPath = Path.Combine(root, "book." + kind);
            File.WriteAllBytes(containerPath, [1, 2, 3]);
            var target = ScanTarget("c-" + kind, containerPath, "b1") with { SourceKind = kind };
            Assert.True(cache.Remember(target.SourceId, "sv-" + kind,
                [new SourceIdentityEntry(null, "1", 0), new SourceIdentityEntry(null, "2", 1)]));
            var resolved = RunSourceRange.Resolve([target], scope, entries, cache).Targets.Single();
            Assert.Equal(kind, resolved.Kind);
            Assert.Equal(2, resolved.ContainerEntries!.Count);
            Assert.Equal([0, 1], resolved.ContainerEntries!.Select(m => m.Ordinal));
        }

        // A folder source keeps its per-member enumeration (no container member plan).
        var folderPath = Path.Combine(root, "folder");
        Directory.CreateDirectory(folderPath);
        File.WriteAllBytes(Path.Combine(folderPath, "001.png"), [1]);
        Assert.True(cache.Remember("f1", "sv-folder", [new SourceIdentityEntry(null, "001.png", 0)]));
        Assert.Null(RunSourceRange.Resolve(
            [ScanTarget("f1", folderPath, "b1")], scope, entries, cache).Targets.Single().ContainerEntries);
    }

    [Fact]
    public void ContainerEntryPlanIsVerbatimAndTypedOverTheBudget()
    {
        // AC-H3/AC-J3: the container member plan is the Core list verbatim; a list over the grant
        // ``max_entries`` budget is a typed SOURCE_BUDGET_EXCEEDED and NEVER truncated; image/folder/
        // undefined keep their frozen shapes (single entry / per-member enumeration).
        var members = new[]
        {
            new SourceIdentityEntry(null, "001.png", 0),
            new SourceIdentityEntry(null, "002.png", 1),
            new SourceIdentityEntry(null, "003.png", 2),
        };
        Assert.Same(members, SourceReadCoordinator.ContainerEntryPlan("zip", members, 10000));
        Assert.Same(members, SourceReadCoordinator.ContainerEntryPlan("cbz", members, 3));
        Assert.Same(members, SourceReadCoordinator.ContainerEntryPlan("pdf", members, 10000));
        Assert.Null(SourceReadCoordinator.ContainerEntryPlan("image", members, 10000));
        Assert.Null(SourceReadCoordinator.ContainerEntryPlan("folder", members, 10000));
        Assert.Null(SourceReadCoordinator.ContainerEntryPlan("zip", [], 10000));
        Assert.Null(SourceReadCoordinator.ContainerEntryPlan("zip", null, 10000));

        var over = new[]
        {
            new SourceIdentityEntry(null, "001.png", 0),
            new SourceIdentityEntry(null, "002.png", 1),
            new SourceIdentityEntry(null, "003.png", 2),
            new SourceIdentityEntry(null, "004.png", 3),
        };
        var refused = Assert.Throws<SourceAccessException>(
            () => SourceReadCoordinator.ContainerEntryPlan("zip", over, 3));
        Assert.Equal("SOURCE_BUDGET_EXCEEDED", refused.Code);
        // Boundary: exactly the budget is still accepted (no off-by-one truncation).
        Assert.Same(over, SourceReadCoordinator.ContainerEntryPlan("zip", over, 4));
    }

    [Fact]
    public async Task RunAuthorizerForwardsTheContainerMemberPlanToTheMint()
    {
        // AC-H3: the authorizer hands the Core-authoritative member identities to the mint. Without
        // this the container grant would carry one entry again (the 2A L-G12② boundary).
        var root = NewSourceDirectory(out var file);
        var seen = new List<RunSourceScope>();
        var authorizer = Authorizer(
            probe: true,
            known: [ScanTarget("s1", file, "b1")],
            entries: [RegistryEntry("reg-1", root)],
            authorize: (scopes, _, _, _) =>
            {
                seen.AddRange(scopes);
                return Task.FromResult(new RunAuthorizationResult(3, scopes.Count, 0, []));
            },
            identities: WarmContainerCache("s1", "sv-core", ("001.png", 0), ("002.png", 1), ("003.png", 2)));
        await authorizer.AuthorizeSliceAsync(
            "reocr_all", Json("""{"kind":"page","page_id":"p1"}"""), CancellationToken.None);
        var scope = Assert.Single(seen);
        Assert.NotNull(scope.ContainerEntries);
        Assert.Equal(["001.png", "002.png", "003.png"], scope.ContainerEntries!.Select(member => member.Locator));
        Assert.Equal([0, 1, 2], scope.ContainerEntries!.Select(member => member.Ordinal));
    }

    private static string FindRepository()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git"))) directory = directory.Parent;
        return directory?.FullName ?? throw new InvalidOperationException("isolated repository not found");
    }
}
