using System.Diagnostics;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-RUN-GRANT-1 (C-16 v1.3 §2.4) real stdio IPC evidence.
///
/// Opt-in only (<c>NEWMANGA_FEA11_IPC=1</c>): starts the real Python Core over
/// an isolated workspace data root. The seed is one real zip container with two
/// real PNG members and TWO pure referenced pages bound to them, so the test can
/// prove:
///
/// * the Host mints the Run-scoped grant (real <c>IssueAsync</c>), the new
///   <c>AuthorizeSourceReadForRun</c> command binds it and the Core's
///   <c>resolve_page_resource</c> then reads the page through that binding;
/// * entry granularity is fail-closed: a page bound to another archive member
///   is refused typed (SOURCE_ACCESS_DENIED) with no partial success;
/// * a revoked grant is a typed refusal;
/// * the wire log/ndjson and the Core stderr carry NO fixture path (C-16 §7).
///
/// The fixture/evidence directories are the task's isolated workspace root
/// (<c>&lt;repo&gt;.workspace/FEA-11-RUN-GRANT-1/</c>), never a tracked file.
/// </summary>
public sealed class Fea11RunGrantIpcTests
{
    [Fea11RunGrantIpcFact]
    public async Task MintBindResolveAndRevoke_TypedWithNoPathLeak()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11-RUN-GRANT-1", "fixtures",
            "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var receipt = await SeedAsync(repo, python, root);
        var archive = receipt.GetProperty("archive").GetString()!;
        var evidence = new List<string>();

        var options = new CoreServiceOptions
        {
            ExecutablePath = python,
            AdditionalArguments =
            [
                "-X", "utf8", "-c",
                $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');"
                + "import bootstrap.core_service as m;raise SystemExit(m.main())",
            ],
            DataRoot = root,
            DerivedRoot = Path.Combine(root, "derived"),
            CatalogDbPath = Path.Combine(root, "catalog.sqlite"),
            StderrLogPath = Path.Combine(root, "core.stderr.log"),
            WireLogPath = Path.Combine(root, "wire.ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };

        await using (var client = await CoreServiceClient.StartAsync(options))
        {
            Assert.Contains("source.read.run/1", (await client.PingAsync()).Capabilities);
            await client.OpenHostSessionAsync();

            var registry = new SourceAccessRegistry(root);
            var authorized = registry.Register("fea11-run-grant", [root]);
            var coordinator = new SourceReadCoordinator(client, registry, () => true);
            Assert.True(await coordinator.SupportsRunAuthorizationAsync(CancellationToken.None));
            var registryId = authorized.RegistryId;
            var generation = authorized.Generation;
            // NOTE (FEA-11-RUN-GRANT-2A): this case exercises the Core authorization face and passes
            // the seed version ("sv1") by hand — it is NOT production-version-path evidence. The
            // production version channel (scan response → cache → mint, no manual version) is proven by
            // ``ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`` below.
            var renditionScope = new RunSourceScope(
                registryId, generation, archive, "zip", "s1", "sv1");

            // (1) R1-03 boundary: page p1 is bound to the archive's FIRST member
            // (001.png, source_entries.ordinal = 0). The Host-minted CONTAINER
            // grant has one entry (locator = container name, ordinal = 0), so it
            // only matches via the ordinal-0 clause — this is the archive
            // first-member boundary of L-G12, NOT generic entry granularity.
            var bound = await coordinator.AuthorizeRunAsync(
                [renditionScope], "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p1" }));
            Assert.Equal(1, bound.BoundPages);
            Assert.Equal(1, bound.MintedGrants);
            Assert.False(bound.Skipped);
            evidence.Add("AuthorizeSourceReadForRun(p1=first member) -> bound_pages=1");

            var resolved = await client.SendAsync(
                "resolve_page_resource", 3,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", "p1");
                    writer.WriteEndObject();
                }, TimeSpan.FromSeconds(60));
            Assert.NotNull(resolved.Result);
            Assert.True(resolved.Result!.Value.ValueKind == JsonValueKind.Object,
                "resolve_page_resource returned no object");
            evidence.Add("resolve_page_resource(first member) -> OK");

            // (2) R1-03 boundary: page p2 is bound to member 002.png
            // (source_entries.ordinal = 1). The container grant cannot carry a
            // member entry identity, so the Core refuses the whole request typed
            // (L-G12 second half; fail-closed, no partial binding, not an
            // authorization bypass).
            var refused = await Assert.ThrowsAsync<CoreOperationException>(() =>
                coordinator.AuthorizeRunAsync(
                    [renditionScope], "reocr_all",
                    JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p2" })));
            Assert.Equal("SOURCE_ACCESS_DENIED", refused.Code);
            evidence.Add("AuthorizeSourceReadForRun(p2=second member) -> L-G12 " + refused.Code);

            // (2b) R1-01/R1-04: a Host-side mint failure (missing file) is a
            // BEST-EFFORT SKIP with a frozen §6 code — no exception, no Core
            // call, and a managed/unrelated Run is never blocked by it.
            var missingArchive = Path.Combine(
                root, "missing-" + Guid.NewGuid().ToString("N") + ".zip");
            var skippedMint = await coordinator.AuthorizeRunAsync(
                [new RunSourceScope(registryId, generation, missingArchive, "zip", "s1", "sv1")],
                "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p1" }));
            Assert.True(skippedMint.Skipped);
            Assert.Equal(0, skippedMint.BoundPages);
            Assert.Equal(0, skippedMint.MintedGrants);
            Assert.Equal(1, skippedMint.SkippedSources);
            Assert.Contains(
                skippedMint.SkippedCodes.Single(),
                new[] { "SOURCE_ENTRY_MISSING", "SOURCE_ACCESS_DENIED" });
            evidence.Add("mint failure (missing file) -> best-effort skip "
                         + skippedMint.SkippedCodes.Single());

            // (2c) partial source failure: the resolvable source is still
            // minted/bound; only the broken one is skipped.
            var mixed = await coordinator.AuthorizeRunAsync(
                [
                    renditionScope,
                    new RunSourceScope(registryId, generation, missingArchive, "zip", "s1", "sv1"),
                ],
                "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p1" }));
            Assert.Equal(1, mixed.BoundPages);
            Assert.Equal(1, mixed.MintedGrants);
            Assert.Equal(1, mixed.SkippedSources);
            evidence.Add("partial mint failure -> minted=1 bound_pages=1 skipped=1");

            // (3) revoking the root kills the page read typed (no silent read)
            // and prunes the Host ledger (R-8/L-G7).
            var revoked = await coordinator.InvokeAsync(
                "source_revoke_root",
                JsonSerializer.SerializeToElement(new { registry_id = registryId }),
                CancellationToken.None);
            Assert.Equal(JsonValueKind.Object, revoked.ValueKind);
            var afterRevoke = await Assert.ThrowsAsync<CoreOperationException>(() =>
                client.SendAsync("resolve_page_resource", 3, writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", "p1");
                    writer.WriteEndObject();
                }, TimeSpan.FromSeconds(60)));
            Assert.Equal("SOURCE_ACCESS_DENIED", afterRevoke.Code);
            evidence.Add("resolve_page_resource after revoke -> " + afterRevoke.Code);
            Assert.Equal(0, coordinator.TrackedGrantCount);
        }

        // (4) C-16 §7: neither the wire frame log nor the Core stderr may carry
        // the fixture path (the new command never carries paths at all).
        var wirePath = Path.Combine(root, "wire.ndjson");
        var stderrPath = Path.Combine(root, "core.stderr.log");
        var wire = File.Exists(wirePath) ? await File.ReadAllTextAsync(wirePath) : string.Empty;
        var stderr = File.Exists(stderrPath) ? await File.ReadAllTextAsync(stderrPath) : string.Empty;
        Assert.DoesNotContain(root, wire, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain(root, stderr, StringComparison.OrdinalIgnoreCase);
        // The signed grant carries the container path; the saveable frame is
        // rewritten BEFORE it is stored (C-16 §7) and the new command carries
        // no path at all.
        Assert.Contains("[REDACTED]", wire, StringComparison.Ordinal);
        Assert.DoesNotContain(archive, wire, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("AuthorizeSourceReadForRun", wire, StringComparison.Ordinal);
        evidence.Add("wire/stderr path leak -> 0");

        await File.WriteAllTextAsync(
            Path.Combine(root, "run-grant-ipc.txt"),
            $"DataRoot={root}\n" + string.Join("\n", evidence) + "\nPASS\n");
    }

    [Fea11RunGrantIpcFact]
    public async Task CoreAdvertisesTheRunAuthorizationCapability_AndRefusesWithoutGrants()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11-RUN-GRANT-1", "fixtures",
            "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        await SeedAsync(repo, python, root);
        var options = new CoreServiceOptions
        {
            ExecutablePath = python,
            AdditionalArguments =
            [
                "-X", "utf8", "-c",
                $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');"
                + "import bootstrap.core_service as m;raise SystemExit(m.main())",
            ],
            DataRoot = root,
            DerivedRoot = Path.Combine(root, "derived"),
            CatalogDbPath = Path.Combine(root, "catalog.sqlite"),
            StderrLogPath = Path.Combine(root, "core.stderr.log"),
            WireLogPath = Path.Combine(root, "wire.ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
        await using var client = await CoreServiceClient.StartAsync(options);
        await client.OpenHostSessionAsync();
        Assert.Contains("source.read.run/1", (await client.PingAsync()).Capabilities);
        // The command itself is host-control only and typed without a grant.
        var refused = await Assert.ThrowsAsync<CoreOperationException>(() =>
            client.SendHostControlAsync("AuthorizeSourceReadForRun", writer =>
            {
                writer.WriteStartArray("grant_ids");
                writer.WriteStringValue("source-" + new string('0', 32));
                writer.WriteEndArray();
                writer.WriteString("command", "reocr_all");
                writer.WriteStartObject("scope");
                writer.WriteString("kind", "page");
                writer.WriteString("page_id", "p1");
                writer.WriteEndObject();
            }));
        Assert.Equal("SOURCE_ACCESS_DENIED", refused.Code);
        var application = await Assert.ThrowsAsync<CoreOperationException>(() =>
            client.SendAsync("AuthorizeSourceReadForRun", 3, WireJson.EmptyObject,
                TimeSpan.FromSeconds(30)));
        Assert.Equal("HOST_ONLY_REQUIRED", application.Code);
        await File.WriteAllTextAsync(
            Path.Combine(root, "run-grant-ipc-capability.txt"),
            $"DataRoot={root}\ncapability=source.read.run/1\nno_grant={refused.Code}\n"
            + $"application_channel={application.Code}\nPASS\n");
    }

    [Fea11RunGrantIpcFact]
    public async Task FolderSourceMintsABindableGrantThroughTheProductionRange()
    {
        // Review r2 R2-01: the folder kind detection used to be extension-only,
        // so a DIRECTORY was classified as "image", the mint opened the
        // directory as a file and the whole folder source was skipped. This test
        // is the discriminating folder evidence: the Host production range
        // resolver classifies the directory as "folder", the real mint succeeds,
        // and the real Core binds the folder member entry.
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11-RUN-GRANT-1", "fixtures",
            "ipc-folder-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var receipt = await SeedFolderAsync(repo, python, root);
        var folderPath = receipt.GetProperty("folder").GetString()!;
        var options = new CoreServiceOptions
        {
            ExecutablePath = python,
            AdditionalArguments =
            [
                "-X", "utf8", "-c",
                $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');"
                + "import bootstrap.core_service as m;raise SystemExit(m.main())",
            ],
            DataRoot = root,
            DerivedRoot = Path.Combine(root, "derived"),
            CatalogDbPath = Path.Combine(root, "catalog.sqlite"),
            StderrLogPath = Path.Combine(root, "core.stderr.log"),
            WireLogPath = Path.Combine(root, "wire.ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
        var evidence = new List<string>();
        await using (var client = await CoreServiceClient.StartAsync(options))
        {
            await client.OpenHostSessionAsync();
            var registry = new SourceAccessRegistry(root);
            var authorized = registry.Register("fea11-run-grant-folder", [root]);
            var coordinator = new SourceReadCoordinator(client, registry, () => true);
            Assert.True(await coordinator.SupportsRunAuthorizationAsync(CancellationToken.None));

            // No declared SourceKind: the filesystem must decide "folder".
            var target = new SourceScanTarget(
                "f1", folderPath, ["b1"], receipt.GetProperty("version_id").GetString()!);
            Assert.Equal("folder", RunSourceRange.KindOfSource(target, folderPath));
            // This case covers the folder MINT/kind path (RUN-GRANT-1 r2); the version here comes from
            // the seed receipt. The PRODUCTION version channel (scan response -> identity cache ->
            // Run mint, no manual version) is covered by
            // ``ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`` below.
            var warmIdentities = new SourceIdentityCache();
            Assert.True(warmIdentities.Remember(
                "f1", receipt.GetProperty("version_id").GetString()!, []));
            var resolvedRange = RunSourceRange.Resolve(
                [target],
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "pf1" }),
                registry.List(),
                warmIdentities);
            var targets = resolvedRange.Targets;
            var unresolved = resolvedRange.Unresolved;
            Assert.Single(targets);
            Assert.Equal("folder", targets[0].Kind);
            Assert.Equal(0, unresolved);
            evidence.Add("RunSourceRange folder -> kind=folder, targets=1, unresolved=0");

            var bound = await coordinator.AuthorizeRunAsync(
                targets, "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "pf1" }));
            Assert.Equal(1, bound.BoundPages);
            Assert.Equal(1, bound.MintedGrants);
            Assert.False(bound.Skipped);
            evidence.Add("folder mint+bind -> bound_pages=1 minted=1");

            var resolved = await client.SendAsync(
                "resolve_page_resource", 3,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", "pf1");
                    writer.WriteEndObject();
                }, TimeSpan.FromSeconds(60));
            Assert.NotNull(resolved.Result);
            evidence.Add("resolve_page_resource(folder member) -> OK");
        }
        var wire = File.Exists(Path.Combine(root, "wire.ndjson"))
            ? await File.ReadAllTextAsync(Path.Combine(root, "wire.ndjson"))
            : string.Empty;
        Assert.DoesNotContain(root, wire, StringComparison.OrdinalIgnoreCase);
        evidence.Add("wire path leak -> 0");
        await File.WriteAllTextAsync(
            Path.Combine(root, "run-grant-ipc-folder.txt"),
            $"DataRoot={root}\n" + string.Join("\n", evidence) + "\nPASS\n");
    }

    /// <summary>
    /// FEA-11-RUN-GRANT-2A (AC-G1/G3/G4) real stdio IPC evidence: the Run-minting
    /// <c>scope.version</c> is obtained through the PRODUCTION path — a real
    /// <c>ScanSourceSync</c> response feeds <see cref="SourceIdentityCache"/>, and
    /// <see cref="RunSourceRange"/> takes the version from there. No test passes a
    /// version by hand: the scan targets deliberately carry the pre-2A production
    /// placeholder <c>"1"</c>, so the authorization can only succeed when the
    /// Core-authoritative version replaced the constant (L-G15).
    ///
    /// Coverage: image single-entry source (COLD cache → exactly one bounded
    /// on-demand scan, AC-G3), folder source (scheduled scan path), archive first
    /// member (scheduled scan path). The archive's second member stays typed
    /// fail-closed (L-G12② / 2B boundary, NOT fixed here).
    /// </summary>
    [Fea11RunGrantIpcFact]
    public async Task ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11-RUN-GRANT-2A", "fixtures",
            "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var receipt = await SeedProductionSourcesAsync(repo, python, root);
        var archive = receipt.GetProperty("archive").GetString()!;
        var image = receipt.GetProperty("image").GetString()!;
        var folder = receipt.GetProperty("folder").GetString()!;
        var zipVersion = receipt.GetProperty("zip_version").GetString()!;
        var imageVersion = receipt.GetProperty("image_version").GetString()!;
        var folderVersion = receipt.GetProperty("folder_version").GetString()!;
        var dbPath = Path.Combine(root, "library.db");
        var evidence = new List<string>();

        var options = new CoreServiceOptions
        {
            ExecutablePath = python,
            AdditionalArguments =
            [
                "-X", "utf8", "-c",
                $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');"
                + "import bootstrap.core_service as m;raise SystemExit(m.main())",
            ],
            DataRoot = root,
            DerivedRoot = Path.Combine(root, "derived"),
            CatalogDbPath = Path.Combine(root, "catalog.sqlite"),
            StderrLogPath = Path.Combine(root, "core.stderr.log"),
            WireLogPath = Path.Combine(root, "wire.ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };

        await using (var client = await CoreServiceClient.StartAsync(options))
        {
            Assert.Contains("source.read.run/1", (await client.PingAsync()).Capabilities);
            await client.OpenHostSessionAsync();
            var registry = new SourceAccessRegistry(root);
            var authorized = registry.Register("fea11-run-grant-2a", [root]);
            await AlignRegistryAsync(python, dbPath, authorized.RegistryId);
            var coordinator = new SourceReadCoordinator(client, registry, () => true);
            Assert.True(await coordinator.SupportsRunAuthorizationAsync(CancellationToken.None));

            var identities = new SourceIdentityCache();
            var scanOptions = new SourceScanOptions
            {
                Enabled = true,
                IntervalSeconds = 60,
                MaxTargetsPerTick = 8,
                MaxBytesPerSource = 256L * 1024 * 1024,
                MaxEntriesPerSource = 10000,
            };
            var executor = new HostSourceScanExecutor(
                client, coordinator, scanOptions, identities: identities);
            // Production scan targets: the pre-2A placeholder version ("1") is exactly what
            // HostRuntime.RegisterSourceScanTarget defaults to; nothing here passes a real version.
            var targets = new[]
            {
                new SourceScanTarget("i1", image, ["b1"], "1"),
                new SourceScanTarget("f1", folder, ["b1"], "1"),
                new SourceScanTarget("s1", archive, ["b1"], "1"),
            };
            Assert.All(targets, target => Assert.Equal("1", target.Version));

            // (1) Production scheduled-scan path: real ScanSourceSync responses fill the cache with the
            // Core committed versions (they equal the seed's committed rows only because the Core
            // echoed its own committed version — never a Host guess).
            var folderOutcome = await executor.ScanAsync(targets[1], CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Ok, folderOutcome.Kind);
            Assert.True(identities.TryGet("f1", out var folderIdentity));
            Assert.Equal(folderVersion, folderIdentity.VersionId);
            Assert.Equal(
                ["001.png", "002.png"],
                folderIdentity.Entries.Select(entry => entry.Locator));
            evidence.Add($"scan response -> cache: f1={folderIdentity.VersionId} entries={folderIdentity.Entries.Count}");
            var zipOutcome = await executor.ScanAsync(targets[2], CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Ok, zipOutcome.Kind);
            Assert.True(identities.TryGet("s1", out var zipIdentity));
            Assert.Equal(zipVersion, zipIdentity.VersionId);
            Assert.True(zipIdentity.Entries.Count >= 2,
                "the archive scan response must carry the Core member identities (locator/ordinal)");
            Assert.Equal("001.png", zipIdentity.Entries[0].Locator);
            evidence.Add($"scan response -> cache: s1={zipIdentity.VersionId} entries={zipIdentity.Entries.Count}");

            // (2) The Run authorizer: same wiring as HostRuntime.CreateRunSourceAuthorizer (cache +
            // bounded on-demand scan); command/scope supplied directly (this test drives the slice).
            var scanCount = 0;
            var log = new List<string>();
            var authorizer = new RunSourceAuthorizer(
                enabled: true,
                knownTargets: () => targets,
                registryEntries: registry.List,
                capabilityProbe: coordinator.SupportsRunAuthorizationAsync,
                authorize: coordinator.AuthorizeRunAsync,
                resolveRunSlice: (_, _) => throw new InvalidOperationException("no run slice expected"),
                info: message => log.Add("info: " + message),
                warn: message => log.Add("warn: " + message),
                identities: identities,
                onDemandScan: async (target, token) =>
                {
                    scanCount++;
                    await executor.ScanAsync(target, token);
                });
            // Evidence (hero): a source whose scheduled scan has not run yet gets exactly one bounded
            // on-demand scan, and the Run grant is then minted with the Core version it learned.
            Assert.False(identities.TryGet("i1", out _));
            await authorizer.AuthorizeSliceAsync(
                "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "pi1" }),
                CancellationToken.None);
            Assert.Equal(1, scanCount);
            Assert.True(identities.TryGet("i1", out var imageIdentity));
            Assert.Equal(imageVersion, imageIdentity.VersionId);
            Assert.Contains(log, message => message.Contains("bound_pages=1", StringComparison.Ordinal));
            evidence.Add($"cold i1 -> on_demand_scans={scanCount} cached={imageIdentity.VersionId} bound_pages=1");
            await ResolvePageAsync(client, "pi1");
            evidence.Add("resolve_page_resource(image single entry, production version) -> OK");

            // (3) Folder source: per-member entries, minted with the cached Core version.
            await authorizer.AuthorizeSliceAsync(
                "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "pf1" }),
                CancellationToken.None);
            Assert.Contains(log, message => message.Contains("bound_pages=1", StringComparison.Ordinal));
            await ResolvePageAsync(client, "pf1");
            evidence.Add("resolve_page_resource(folder member, production version) -> OK");

            // (4) Archive first member (Core ordinal=0) through the cached Core version.
            await authorizer.AuthorizeSliceAsync(
                "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p1" }),
                CancellationToken.None);
            Assert.Contains(log, message => message.Contains("bound_pages=1", StringComparison.Ordinal));
            await ResolvePageAsync(client, "p1");
            evidence.Add("resolve_page_resource(archive first member, production version) -> OK");

            // (5) L-G12② boundary unchanged: the archive's SECOND member is still refused typed
            // (2A only fixes the version channel; container member entries need 2B).
            var refused = await Assert.ThrowsAsync<CoreOperationException>(() =>
                authorizer.AuthorizeSliceAsync(
                    "reocr_all",
                    JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p2" }),
                    CancellationToken.None));
            Assert.Equal("SOURCE_ACCESS_DENIED", refused.Code);
            evidence.Add("archive second member -> L-G12 boundary kept: " + refused.Code);
        }

        // C-16 §7: neither the wire frame log nor the Core stderr may carry the fixture path.
        var wire = File.Exists(Path.Combine(root, "wire.ndjson"))
            ? await File.ReadAllTextAsync(Path.Combine(root, "wire.ndjson"))
            : string.Empty;
        var stderr = File.Exists(Path.Combine(root, "core.stderr.log"))
            ? await File.ReadAllTextAsync(Path.Combine(root, "core.stderr.log"))
            : string.Empty;
        Assert.DoesNotContain(root, wire, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain(root, stderr, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain(archive, wire, StringComparison.OrdinalIgnoreCase);
        evidence.Add("wire/stderr path leak -> 0");

        await File.WriteAllTextAsync(
            Path.Combine(root, "run-grant-2a-version-channel.txt"),
            $"DataRoot={root}\n" + string.Join("\n", evidence) + "\nPASS\n");
    }

    /// <summary>Resolves one page through the real Core (the read the Run would perform).</summary>
    private static async Task ResolvePageAsync(CoreServiceClient client, string pageId)
    {
        var resolved = await client.SendAsync(
            "resolve_page_resource", 3,
            writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("page_id", pageId);
                writer.WriteEndObject();
            }, TimeSpan.FromSeconds(60));
        Assert.NotNull(resolved.Result);
        Assert.Equal(JsonValueKind.Object, resolved.Result!.Value.ValueKind);
    }

    private static async Task<JsonElement> SeedProductionSourcesAsync(string repo, string python, string root)
    {
        var script = $$"""
import hashlib
import io
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

repo = Path(r"{{repo}}")
root = Path(r"{{root}}")
sys.path[:0] = [str(repo), str(repo / "src"), str(repo / "tests" / "fea11")]

from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from application.importing.referenced.model import folder_manifest_digest
import conftest as fixture
from PIL import Image


def png(color):
    buffer = io.BytesIO()
    Image.new("RGB", (8, 6), color).save(buffer, format="PNG")
    return buffer.getvalue()


root.mkdir(parents=True, exist_ok=True)
db = root / "library.db"
red, blue, green = png((255, 0, 0)), png((0, 0, 255)), png((0, 255, 0))
red_digest = hashlib.sha256(red).hexdigest()
blue_digest = hashlib.sha256(blue).hexdigest()
green_digest = hashlib.sha256(green).hexdigest()

# (a) archive source s1: two real PNG members (first member is the 2A boundary).
archive = root / "source-v1.zip"
with zipfile.ZipFile(archive, "w") as archive_file:
    archive_file.writestr("001.png", red)
    archive_file.writestr("002.png", blue)
zip_facts = fixture.file_facts(archive)

# (b) image source i1: one real PNG file (single-entry source).
image = root / "page.png"
image.write_bytes(green)
image_facts = fixture.file_facts(image)

# (c) folder source f1: two real PNG members.
folder = root / "folder-source"
folder.mkdir(parents=True, exist_ok=True)
(folder / "001.png").write_bytes(red)
(folder / "002.png").write_bytes(blue)
folder_first_facts = fixture.file_facts(folder / "001.png")
folder_manifest = folder_manifest_digest([
    {"rel_path": "001.png", "size_bytes": len(red), "sha256": red_digest},
    {"rel_path": "002.png", "size_bytes": len(blue), "sha256": blue_digest},
])
folder_total = len(red) + len(blue)

conn = sqlite3.connect(db, isolation_level=None)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
MigrationRunner(conn, default_migrations()).apply_pending()
conn.execute(
    "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('b1','IPC2A',?,?)",
    (fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
    " VALUES ('c1','b1','Ch',?,?)", (fixture.NOW, fixture.NOW))
conn.commit()

# archive source (container single-entry grant matches the Core ordinal=0 member).
fixture.add_source_tree(
    conn, source_id="s1", version_id="sv1", digest=zip_facts["sha256"],
    entries=[("se1", "001.png", red_digest), ("se2", "002.png", blue_digest)],
    volume_serial=zip_facts["volume_serial"], file_id=zip_facts["file_id"],
    legacy_v7_evidence=False)
conn.execute(
    "UPDATE source_locations SET size_bytes = ? WHERE source_id = 's1'",
    (zip_facts["size"],))

# image source: one entry, the file's own name/identity.
conn.execute(
    "INSERT INTO sources (source_id, source_kind, display_name, created_at, updated_at)"
    " VALUES ('i1','image','page.png',?,?)", (fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO source_locations (location_id, source_id, registry_id,"
    " authorization_generation, content_digest, volume_serial, file_id,"
    " size_bytes, observed_at, created_at)"
    " VALUES ('sl-i1','i1','reg-pending',1,?,?,?,?,?,?)",
    (image_facts["sha256"], image_facts["volume_serial"], image_facts["file_id"],
     image_facts["size"], fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO source_versions (version_id, source_id, location_id,"
    " content_digest, size_bytes, observed_at, created_at)"
    " VALUES ('sv-img','i1','sl-i1',?,?,?,?)",
    (image_facts["sha256"], image_facts["size"], fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO source_entries (source_id, version_id, entry_id, locator,"
    " ordinal, stable_sort_key, content_digest_kind, content_digest,"
    " encoded_digest, size_bytes, width, height, decoder_name,"
    " decoder_version, created_at)"
    " VALUES ('i1','sv-img','se-img','page.png',0,'00000000','encoded',?,?,?,8,6,'image','1.0',?)",
    (image_facts["sha256"], image_facts["sha256"], image_facts["size"], fixture.NOW))

# folder source: one entry per real member.
conn.execute(
    "INSERT INTO sources (source_id, source_kind, display_name, created_at, updated_at)"
    " VALUES ('f1','folder','folder-source',?,?)", (fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO source_locations (location_id, source_id, registry_id,"
    " authorization_generation, content_digest, volume_serial, file_id,"
    " size_bytes, observed_at, created_at)"
    " VALUES ('sl-f1','f1','reg-pending',1,?,?,?,?,?,?)",
    (folder_manifest, folder_first_facts["volume_serial"],
     folder_first_facts["file_id"], folder_total, fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO source_versions (version_id, source_id, location_id,"
    " content_digest, size_bytes, observed_at, created_at)"
    " VALUES ('svf1','f1','sl-f1',?,?,?,?)",
    (folder_manifest, folder_total, fixture.NOW, fixture.NOW))
for ordinal, (entry_id, locator, digest, size) in enumerate([
        ("se-101", "001.png", red_digest, len(red)),
        ("se-102", "002.png", blue_digest, len(blue)),
]):
    conn.execute(
        "INSERT INTO source_entries (source_id, version_id, entry_id, locator,"
        " ordinal, stable_sort_key, content_digest_kind, content_digest,"
        " encoded_digest, size_bytes, width, height, decoder_name,"
        " decoder_version, created_at)"
        " VALUES ('f1','svf1',?,?,?,?,'encoded',?,?,?,8,6,'folder','1.0',?)",
        (entry_id, locator, ordinal, f"{ordinal:08d}", digest, digest, size,
         fixture.NOW))
conn.commit()

fixture.add_referenced_page(
    conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
    entry_id="se1", digest=red_digest, width=8, height=6)
fixture.add_referenced_page(
    conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
    entry_id="se2", digest=blue_digest, width=8, height=6)
fixture.add_referenced_page(
    conn, "pi1", "c1", "b1", order=3, source_id="i1", version_id="sv-img",
    entry_id="se-img", digest=green_digest, width=8, height=6)
fixture.add_referenced_page(
    conn, "pf1", "c1", "b1", order=4, source_id="f1", version_id="svf1",
    entry_id="se-101", digest=red_digest, width=8, height=6)
conn.commit()
conn.close()
receipt = {
    "root": str(root), "db": str(db), "archive": str(archive),
    "image": str(image), "folder": str(folder),
    "zip_version": "sv1", "image_version": "sv-img", "folder_version": "svf1",
}
(root / "ipc-run-grant-2a-receipt.json").write_text(
    json.dumps(receipt), encoding="utf-8")
print("FEA11_RUN_GRANT_2A_SEED_OK")
""";
        var startInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(script);
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0, await stdout + await stderr);
        using var document = JsonDocument.Parse(
            await File.ReadAllTextAsync(Path.Combine(root, "ipc-run-grant-2a-receipt.json")));
        return document.RootElement.Clone();
    }

    /// <summary>Aligns the isolated fixture's C-17 location rows with the real Host registry id (the
    /// Host mints the read grant with its own registry identity; the fixture is created before it).</summary>
    private static async Task AlignRegistryAsync(string python, string dbPath, string registryId)
    {
        const string code =
            "import sqlite3,sys\n" +
            "c=sqlite3.connect(sys.argv[1])\n" +
            "c.execute('UPDATE source_locations SET registry_id=?, authorization_generation=1',(sys.argv[2],))\n" +
            "c.commit()\n" +
            "print('REGISTRY_ALIGNED', c.total_changes)\n" +
            "c.close()\n";
        var startInfo = new ProcessStartInfo(python)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(code);
        startInfo.ArgumentList.Add(dbPath);
        startInfo.ArgumentList.Add(registryId);
        using var process = Process.Start(startInfo)!;
        var stdout = await process.StandardOutput.ReadToEndAsync();
        var stderr = await process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0, stdout + stderr);
    }

    private static async Task<JsonElement> SeedAsync(string repo, string python, string root)
    {
        var script = $$"""
import hashlib
import io
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

repo = Path(r"{{repo}}")
root = Path(r"{{root}}")
sys.path[:0] = [str(repo), str(repo / "src"), str(repo / "tests" / "fea11")]

from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
import conftest as fixture
from PIL import Image


def png(color):
    buffer = io.BytesIO()
    Image.new("RGB", (8, 6), color).save(buffer, format="PNG")
    return buffer.getvalue()


root.mkdir(parents=True, exist_ok=True)
db = root / "library.db"
archive = root / "source-v1.zip"
first, second = png((255, 0, 0)), png((0, 0, 255))
with zipfile.ZipFile(archive, "w") as archive_file:
    archive_file.writestr("001.png", first)
    archive_file.writestr("002.png", second)
facts = fixture.file_facts(archive)
first_digest = hashlib.sha256(first).hexdigest()
second_digest = hashlib.sha256(second).hexdigest()
conn = sqlite3.connect(db, isolation_level=None)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
MigrationRunner(conn, default_migrations()).apply_pending()
conn.execute(
    "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('b1','IPC',?,?)",
    (fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
    " VALUES ('c1','b1','Ch',?,?)", (fixture.NOW, fixture.NOW))
conn.commit()
fixture.add_source_tree(
    conn, source_id="s1", version_id="sv1", digest=facts["sha256"],
    entries=[("se1", "001.png", first_digest), ("se2", "002.png", second_digest)],
    volume_serial=facts["volume_serial"], file_id=facts["file_id"],
    legacy_v7_evidence=False)
conn.execute(
    "UPDATE source_locations SET size_bytes = ? WHERE source_id = 's1'",
    (facts["size"],))
fixture.add_referenced_page(
    conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
    entry_id="se1", digest=first_digest, width=8, height=6)
fixture.add_referenced_page(
    conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
    entry_id="se2", digest=second_digest, width=8, height=6)
conn.commit()
conn.close()
receipt = {
    "root": str(root), "db": str(db), "archive": str(archive),
    "source_id": "s1", "version_id": "sv1",
}
(root / "ipc-run-grant-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
print("FEA11_RUN_GRANT_SEED_OK")
""";
        var startInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(script);
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0, await stdout + await stderr);
        using var document = JsonDocument.Parse(
            await File.ReadAllTextAsync(Path.Combine(root, "ipc-run-grant-receipt.json")));
        return document.RootElement.Clone();
    }

    private static async Task<JsonElement> SeedFolderAsync(string repo, string python, string root)
    {
        var script = $$"""
import hashlib
import io
import json
import sqlite3
import sys
from pathlib import Path

repo = Path(r"{{repo}}")
root = Path(r"{{root}}")
sys.path[:0] = [str(repo), str(repo / "src"), str(repo / "tests" / "fea11")]

from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from application.importing.referenced.model import folder_manifest_digest
import conftest as fixture
from PIL import Image


def png(color):
    buffer = io.BytesIO()
    Image.new("RGB", (8, 6), color).save(buffer, format="PNG")
    return buffer.getvalue()


root.mkdir(parents=True, exist_ok=True)
db = root / "library.db"
folder = root / "folder-source"
folder.mkdir(parents=True, exist_ok=True)
first, second = png((255, 0, 0)), png((0, 0, 255))
(folder / "001.png").write_bytes(first)
(folder / "002.png").write_bytes(second)
first_facts = fixture.file_facts(folder / "001.png")
first_digest = hashlib.sha256(first).hexdigest()
second_digest = hashlib.sha256(second).hexdigest()
manifest_digest = folder_manifest_digest([
    {"rel_path": "001.png", "size_bytes": len(first), "sha256": first_digest},
    {"rel_path": "002.png", "size_bytes": len(second), "sha256": second_digest},
])
total_size = len(first) + len(second)
conn = sqlite3.connect(db, isolation_level=None)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
MigrationRunner(conn, default_migrations()).apply_pending()
conn.execute(
    "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('b1','IPC',?,?)",
    (fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
    " VALUES ('c1','b1','Ch',?,?)", (fixture.NOW, fixture.NOW))
conn.commit()
conn.execute(
    "INSERT INTO sources (source_id, source_kind, display_name, created_at, updated_at)"
    " VALUES ('f1','folder','folder-source',?,?)", (fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO source_locations (location_id, source_id, registry_id,"
    " authorization_generation, content_digest, volume_serial, file_id,"
    " size_bytes, observed_at, created_at)"
    " VALUES ('sl-f1','f1','fea11-run-grant-folder',1,?,?,?,?,?,?)",
    (manifest_digest, first_facts["volume_serial"], first_facts["file_id"],
     total_size, fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO source_versions (version_id, source_id, location_id,"
    " content_digest, size_bytes, observed_at, created_at)"
    " VALUES ('svf1','f1','sl-f1',?,?,?,?)",
    (manifest_digest, total_size, fixture.NOW, fixture.NOW))
for ordinal, (entry_id, locator, digest, size) in enumerate([
        ("se-101", "001.png", first_digest, len(first)),
        ("se-102", "002.png", second_digest, len(second)),
]):
    conn.execute(
        "INSERT INTO source_entries (source_id, version_id, entry_id, locator,"
        " ordinal, stable_sort_key, content_digest_kind, content_digest,"
        " encoded_digest, size_bytes, width, height, decoder_name,"
        " decoder_version, created_at)"
        " VALUES ('f1','svf1',?,?,?,?,'encoded',?,?,?,8,6,'folder','1.0',?)",
        (entry_id, locator, ordinal, f"{ordinal:08d}", digest, digest, size,
         fixture.NOW))
conn.execute(
    "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at,"
    " source_filename, source_order, source_hash, source_size_bytes, width,"
    " height, managed_original_ref, source_mode, integrity_status)"
    " VALUES ('pf1','c1',1,?,?, '001.png', 1, ?, ?, 8, 6, NULL, 'referenced',"
    " 'complete')",
    (fixture.NOW, fixture.NOW, first_digest, len(first)))
conn.execute(
    "INSERT INTO page_bindings (binding_id, page_id, project_id, binding_version,"
    " source_id, entry_id, accepted_source_version, status,"
    " authorization_generation, authorized_at, verified_digest, created_at,"
    " updated_at)"
    " VALUES ('pb-pf1','pf1','b1',1,'f1','se-101','svf1','healthy',1,?,?,?,?)",
    (fixture.NOW, first_digest, fixture.NOW, fixture.NOW))
conn.commit()
conn.close()
receipt = {
    "root": str(root), "db": str(db), "folder": str(folder),
    "source_id": "f1", "version_id": "svf1", "entry_id": "se-101",
}
(root / "ipc-run-grant-folder-receipt.json").write_text(
    json.dumps(receipt), encoding="utf-8")
print("FEA11_RUN_GRANT_FOLDER_SEED_OK")
""";
        var startInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(script);
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0, await stdout + await stderr);
        using var document = JsonDocument.Parse(
            await File.ReadAllTextAsync(Path.Combine(root, "ipc-run-grant-folder-receipt.json")));
        return document.RootElement.Clone();
    }

    private sealed class Fea11RunGrantIpcFactAttribute : FactAttribute
    {
        public Fea11RunGrantIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "set NEWMANGA_FEA11_IPC=1 for the real isolated Python Core Run-grant IPC test";
            }
        }
    }
}
