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
        List<string>? warnings = null) =>
        new(true,
            () => known ?? Array.Empty<SourceScanTarget>(),
            () => entries ?? Array.Empty<SourceAuthorization>(),
            _ => Task.FromResult(probe),
            authorize,
            resolve ?? ((_, _) => throw new InvalidOperationException("no run slice expected")),
            _ => { },
            message => warnings?.Add(message));

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

        var (targets, unresolved) = RunSourceRange.Resolve(
            known, Json("""{"kind":"book","book_id":"b1"}"""), entries);
        Assert.Equal(["s1", "s3"], targets.Select(target => target.SourceId));
        Assert.Equal(1, unresolved); // s4 outside the authorized root
        _ = outside;

        var all = RunSourceRange.Resolve(known, Json("""{"kind":"page","page_id":"p1"}"""), entries);
        Assert.Equal(["s1", "s2", "s3"], all.Targets.Select(target => target.SourceId));
        Assert.Equal(1, all.Unresolved);

        Assert.Empty(RunSourceRange.Resolve(
            Array.Empty<SourceScanTarget>(),
            Json("""{"kind":"page","page_id":"p1"}"""), entries).Targets);
        Assert.Empty(RunSourceRange.Resolve(
            known, Json("""{"kind":"book","book_id":"b9"}"""), entries).Targets);
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
            _ => { }, message => warnings.Add(message));
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
            });
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
            warnings: warnings);
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
                "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null));
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
                Json("""{"kind":"page","page_id":"p1"}"""))));
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
            });
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
            authorize: (_, _, _, _) => throw new SourceAccessException("SOURCE_ENTRY_MISSING"));
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
                "SOURCE_ACCESS_DENIED", "authorization", false, "denied", null));
        var blocked = new HostCommandDispatcher(
            runAuthorize: (name, payload, token) =>
                refusing.AuthorizeForCommandAsync(name, payload, token));
        var refusal = await Assert.ThrowsAsync<CoreOperationException>(() =>
            blocked.InvokeAsync("library_start_run", request));
        Assert.Equal("SOURCE_ACCESS_DENIED", refusal.Code);
    }

    private static string FindRepository()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git"))) directory = directory.Parent;
        return directory?.FullName ?? throw new InvalidOperationException("isolated repository not found");
    }
}
