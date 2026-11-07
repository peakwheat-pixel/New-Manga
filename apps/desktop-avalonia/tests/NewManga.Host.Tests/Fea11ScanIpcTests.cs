using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-SCAN-1 (AC-S4): the real end-to-end chain — real volatile Python Core over stdio, a real
/// v8 library, a real zip container and an isolated workspace DataRoot. It proves the production
/// <see cref="HostSourceScanExecutor"/> mints a live grant and sends exactly <c>ScanSourceSync</c>
/// per tick: an unchanged container reports <c>ok</c>, a deleted source reports the C-17 §5.3
/// <c>missing</c> observation, and a same-name/same-size/different-bytes container reports
/// <c>changed</c>. The SQLite snapshot (page_bindings/source_versions/entries) must be unchanged:
/// the scan is read-only.
///
/// Opt-in only (<c>NEWMANGA_FEA11_IPC=1</c>) because it starts the real Python Core. Fixtures live
/// under the FEA-11 fixtures root (the frozen seed script's isolation guard) and evidence is written
/// there, never to a tracked repository file.
/// </summary>
public sealed class Fea11ScanIpcTests
{
    [Fea11ScanIpcFact]
    public async Task PeriodicScan_DetectsMissingThenChanged_WithZeroCoreWrites()
    {
        var (repo, python, root, receipt) = await SeedAsync();
        var dbPath = Path.Combine(root, "library.db");
        var sourceId = receipt.GetProperty("source_id").GetString()!;
        var versionId = receipt.GetProperty("version_id").GetString()!;
        var oldZip = receipt.GetProperty("old_zip").GetString()!;
        var newZip = receipt.GetProperty("new_zip").GetString()!;
        var oldBytes = await File.ReadAllBytesAsync(oldZip);
        var newBytes = await File.ReadAllBytesAsync(newZip);
        Assert.Equal(oldBytes.Length, newBytes.Length); // AC-S4: same name/size, different bytes
        Assert.NotEqual(
            Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(oldBytes)),
            Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(newBytes)));

        var options = BuildOptions(repo, python, root);
        await using var client = await CoreServiceClient.StartAsync(options);
        await client.OpenHostSessionAsync();
        Assert.Contains("source.sync.scan/1", (await client.PingAsync()).Capabilities);

        var registry = new SourceAccessRegistry(root);
        var registered = registry.Register("fea11-scan-1", new[] { root });
        // The frozen seed writes the C-17 location row with synthetic identity placeholders
        // (volume=7/file=8/size=100) because it exists for matcher tests, and v7 entries carry no
        // pixel profile (a changed container then degrades to needs-confirmation by design after
        // FEA-11-MATCH-1). Both are fixture facts the scan slice legitimately consumes: align them
        // with the real file identity, the Host registry identity and the real old-image pixel
        // profiles so the C-17 §5.3 missing cross-check and the deterministic "changed" verdict are
        // both observable at all (fixture-only alignment; no product code writes this DB).
        var facts = ReadFileIdentity(oldZip);
        UpdateLocationRow(python, dbPath, registered.RegistryId, facts);
        SeedOldPixelProfiles(python, repo, oldZip, dbPath);
        var bindingsBefore = QuerySnapshot(python, dbPath);

        var scanOptions = new SourceScanOptions
        {
            Enabled = true,
            IntervalSeconds = 60,
            MaxTargetsPerTick = 8,
            MaxBytesPerSource = 256L * 1024 * 1024,
            MaxEntriesPerSource = 10000,
        };
        var sources = new SourceReadCoordinator(client, registry, () => true);
        var executor = new HostSourceScanExecutor(client, sources, scanOptions);
        await using var scheduler = new SourceScanScheduler(scanOptions, executor);
        Assert.True(scheduler.RegisterTarget(new SourceScanTarget(sourceId, oldZip, new[] { "b1" }, versionId)));

        var steps = new List<object>();

        async Task<SourceScanTargetStatus> TickAsync(string step)
        {
            Assert.True(await scheduler.TickAsync());
            var target = Assert.Single(scheduler.Snapshot().Targets);
            steps.Add(new
            {
                step,
                result = target.LastResult ?? "null",
                unchanged = target.Counts?.Unchanged ?? 0,
                added = target.Counts?.Added ?? 0,
                missing = target.Counts?.Missing ?? 0,
                changed = target.Counts?.Changed ?? 0,
                deferred = target.Deferred,
            });
            return target;
        }

        // 1) Unchanged container → ok (and the scan caches the verified identity for a later
        //    C-17 §5.3 missing observation).
        var unchanged = await TickAsync("unchanged");
        Assert.Equal(SourceScanResults.Ok, unchanged.LastResult);

        // 2) Same name, same size, different bytes → changed (full re-enumeration; no hints).
        await File.WriteAllBytesAsync(oldZip, newBytes);
        Assert.Equal(oldBytes.Length, new FileInfo(oldZip).Length);
        var changed = await TickAsync("changed");
        Assert.Equal(SourceScanResults.Changed, changed.LastResult);
        Assert.True(changed.Counts!.Changed >= 1, "changed scan must report totals.changed >= 1");

        // 3) r1 P1-1: a changed observation must NOT overwrite the recorded missing baseline
        //    identity; the last unchanged/ok observation (1) is the Core-recorded location. A source
        //    deleted right after a changed tick therefore still reports the Contract's missing
        //    observation instead of a SOURCE_PLAN_STALE error (this is the r1 P1 sequence).
        File.Delete(oldZip);
        var changedThenDeleted = await TickAsync("changed-deleted");
        Assert.Equal(SourceScanResults.Missing, changedThenDeleted.LastResult);

        // 4) Source restored → full re-enumeration reports ok again (no stale cached state is used
        //    for the content verdict; the recorded location identity is not re-attested).
        await File.WriteAllBytesAsync(oldZip, oldBytes);
        var restored = await TickAsync("restored");
        Assert.Equal(SourceScanResults.Ok, restored.LastResult);

        // 5) A second same-size rewrite is still observed as changed (full re-enumeration).
        await File.WriteAllBytesAsync(oldZip, newBytes);
        var changedAgain = await TickAsync("changed-again");
        Assert.Equal(SourceScanResults.Changed, changedAgain.LastResult);

        // Zero Core writes: the SQLite page/binding/version/entry snapshot is byte-for-byte equal.
        var bindingsAfter = QuerySnapshot(python, dbPath);
        Assert.Equal(bindingsBefore, bindingsAfter);
        Assert.Equal(SourceScanResults.Changed, scheduler.Snapshot().Targets.Single().LastResult);

        // Only the read face was used on the wire: exactly the four frozen commands (ScanSourceSync +
        // the ping / host-session / grant frames), never a plan/apply/write command.
        var wireCommands = client.Wire.Frames
            .Select(frame => RequestCommand(frame.RequestLine))
            .Where(command => command is not null)
            .Select(command => command!)
            .Distinct(StringComparer.Ordinal)
            .OrderBy(command => command, StringComparer.Ordinal)
            .ToArray();
        var forbidden = new[]
        {
            "PlanSourceSync", "PreviewSourceSyncPlan", "ConfirmSourceSyncPlan", "ApplySourceSyncPlan",
            "RelinkSource", "RepointSource", "ResyncSource", "AcknowledgeSourceOperation",
            "CompleteSourceOperationRecovery", "RecordSourceOperationFailure",
        };
        Assert.Equal(
            new[] { "OpenHostSession", "RegisterSourceReadGrant", "ScanSourceSync", "core.ping" },
            wireCommands);
        Assert.All(forbidden, command => Assert.DoesNotContain(command, wireCommands));

        var evidence = new
        {
            @case = "AC-S4",
            core = "real volatile python core (stdio IPC)",
            schema_version = receipt.GetProperty("schema_version").GetInt32(),
            source_id = sourceId,
            registry_generation = registered.Generation,
            same_size_rewrite = new { size = oldBytes.Length, old_sha256 = Sha256(oldBytes), new_sha256 = Sha256(newBytes) },
            steps,
            identity_baseline_kept_after_changed = true,
            db_snapshot_unchanged = true,
            wire_commands = wireCommands,
            forbidden_write_commands_absent = true,
            scheduler_status = new
            {
                enabled = scheduler.Snapshot().Enabled,
                paused = scheduler.Snapshot().Paused,
                interval_seconds = scheduler.Snapshot().IntervalSeconds,
                recent = scheduler.Snapshot().Recent.Count,
            },
        };
        await File.WriteAllTextAsync(
            Path.Combine(root, "real-ipc.json"),
            JsonSerializer.Serialize(evidence, new JsonSerializerOptions { WriteIndented = true }));
        await File.WriteAllTextAsync(
            Path.Combine(root, "real-ipc.txt"),
            "FEA-11-SCAN-1 AC-S4 real IPC (r2: changed->deleted->missing included)\n"
            + "DataRoot=" + root + "\n"
            + "steps=" + string.Join(",", steps.Select(step => step.GetType().GetProperty("step")!.GetValue(step))) + "\n"
            + "results=" + string.Join(",", steps.Select(step => step.GetType().GetProperty("result")!.GetValue(step))) + "\n"
            + "identity_baseline_kept_after_changed=true\n"
            + "db_snapshot_unchanged=true\nwire_commands=" + string.Join(",", wireCommands) + "\nPASS\n");
    }

    /// <summary>
    /// FEA-11-SCAN-2 (B1 / AC-S2-1/2/4/5/8): the cold-start chain. A fresh Host-side object graph (NO
    /// App registration, no in-memory targets) enumerates the Core's authoritative scan targets,
    /// re-verifies the persistent Host registry, mints a grant and scans exactly like SCAN-1. When the
    /// Core shard is not merged yet (no source.sync.enumerate/1 capability) the attempt records a
    /// typed NOT_RUN evidence line and returns: it never pretends the enumeration happened.
    /// </summary>
    [Fea11ScanIpcFact]
    public async Task ColdStartEnumeration_WithoutAppRegistration_IsReadOnly()
    {
        var (repo, python, root, receipt) = await SeedAsync();
        var dbPath = Path.Combine(root, "library.db");
        var oldZip = receipt.GetProperty("old_zip").GetString()!;
        var options = BuildOptions(repo, python, root);
        await using var client = await CoreServiceClient.StartAsync(options);
        await client.OpenHostSessionAsync();
        var ping = await client.PingAsync();
        if (!ping.Capabilities.Contains("source.sync.enumerate/1"))
        {
            await File.WriteAllTextAsync(
                Path.Combine(root, "cold-start.txt"),
                "FEA-11-SCAN-2 cold-start IPC: NOT_RUN (Core does not advertise source.sync.enumerate/1; "
                + "Core shard pending). Core capabilities=" + string.Join(",", ping.Capabilities) + "\n");
            return;
        }

        var registry = new SourceAccessRegistry(root);
        var registered = registry.Register("fea11-scan-2", new[] { oldZip });
        var facts = ReadFileIdentity(oldZip);
        UpdateLocationGenerationRow(python, dbPath, registered.RegistryId, registered.Generation, facts);
        var coreSourceId = QuerySourceId(python, dbPath);
        var snapshotBefore = QueryScanSnapshot(python, dbPath);

        var scanOptions = new SourceScanOptions
        {
            Enabled = true,
            IntervalSeconds = 60,
            MaxTargetsPerTick = 8,
            MaxBytesPerSource = 256L * 1024 * 1024,
            MaxEntriesPerSource = 10000,
        };
        var sources = new SourceReadCoordinator(client, registry, () => true);
        var executor = new HostSourceScanExecutor(client, sources, scanOptions);
        var enumerator = new HostSourceScanTargetEnumerator(client, registry);
        await using var scheduler = new SourceScanScheduler(
            scanOptions, executor, enumerator: enumerator);

        Assert.True(await scheduler.RefreshTargetsAsync(), "cold-start enumeration must succeed");
        var status = scheduler.Snapshot();
        Assert.NotNull(status.Enumeration);
        Assert.True(status.Enumeration!.Available);
        var target = Assert.Single(status.Targets);
        // S-2 discriminator: the authoritative id is the Core sources.source_id, never the App-side
        // StableSourceId used by SCAN-1.
        Assert.Equal(coreSourceId, target.SourceId);
        Assert.NotEqual(ExpectedStableSourceId(Path.GetFullPath(oldZip)), target.SourceId);

        Assert.True(await scheduler.TickAsync());
        var scanned = scheduler.Snapshot().Targets.Single();
        Assert.NotEqual(SourceScanResults.Error, scanned.LastResult);

        var snapshotAfter = QueryScanSnapshot(python, dbPath);
        Assert.Equal(snapshotBefore, snapshotAfter);
        var wireCommands = client.Wire.Frames
            .Select(frame => RequestCommand(frame.RequestLine))
            .Where(command => command is not null)
            .Select(command => command!)
            .Distinct(StringComparer.Ordinal)
            .OrderBy(command => command, StringComparer.Ordinal)
            .ToArray();
        Assert.Equal(
            new[]
            {
                "OpenHostSession", "RegisterSourceReadGrant", "ScanSourceSync", "core.ping",
                "source_list_scan_targets",
            },
            wireCommands);

        var evidence = new
        {
            @case = "AC-S2-1/S2-2/S2-4/S2-5/S2-8",
            core = "real volatile python core (stdio IPC)",
            app_registration_used = false,
            core_source_id = coreSourceId,
            target_source_id = target.SourceId,
            target_source_kind = "zip",
            enumeration = new { available = status.Enumeration!.Available, last_result = status.Enumeration.LastResult, skipped = status.Enumeration.SkippedTargets },
            scan_result = scanned.LastResult,
            db_snapshot_unchanged = true,
            db_tables = QueryScanTables,
            db_table_count = QueryScanTables.Length,
            wire_commands = wireCommands,
        };
        await File.WriteAllTextAsync(
            Path.Combine(root, "cold-start.json"),
            JsonSerializer.Serialize(evidence, new JsonSerializerOptions { WriteIndented = true }));
        await File.WriteAllTextAsync(
            Path.Combine(root, "cold-start.txt"),
            "FEA-11-SCAN-2 AC-S2 cold-start IPC\n"
            + "DataRoot=" + root + "\n"
            + "app_registration_used=false\n"
            + "core_source_id=" + coreSourceId + "\n"
            + "target_source_id=" + target.SourceId + "\n"
            + "scan_result=" + scanned.LastResult + "\n"
            + "db_snapshot_unchanged=true (15 tables)\n"
            + "wire_commands=" + string.Join(",", wireCommands) + "\nPASS\n");
    }

    /// <summary>Aligns the isolated fixture's C-17 location row with real file + Host registry facts.</summary>
    private static void UpdateLocationGenerationRow(
        string python, string dbPath, string registryId, int generation, FileIdentity facts)
    {
        var code =
            "import sqlite3,sys\n" +
            "c=sqlite3.connect(sys.argv[1])\n" +
            "c.execute('UPDATE source_locations SET registry_id=?, authorization_generation=?, volume_serial=?, file_id=?, size_bytes=? WHERE location_id=?'," +
            "(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),'sl-s1'))\n" +
            "c.commit()\n" +
            "c.close()\n" +
            "print('LOCATION_GENERATION_UPDATED')\n";
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
        startInfo.ArgumentList.Add(generation.ToString());
        startInfo.ArgumentList.Add(facts.Volume.ToString());
        startInfo.ArgumentList.Add(facts.FileId.ToString());
        startInfo.ArgumentList.Add(facts.Size.ToString());
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
    }

    /// <summary>Reads the Core-authoritative source id straight from the isolated fixture DB.</summary>
    private static string QuerySourceId(string python, string dbPath)
    {
        const string code =
            "import sqlite3,sys\n" +
            "c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True)\n" +
            "row=c.execute('SELECT source_id FROM sources ORDER BY source_id LIMIT 1').fetchone()\n" +
            "c.close()\n" +
            "print('' if row is None else row[0])\n";
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
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
        return stdout.Trim();
    }

    /// <summary>
    /// FEA-11-SCAN-2 AC-S2-8: the C-17 v1.1 scan-relevant table snapshot (sources, locations,
    /// versions, entries, books, chapters, pages, bindings, regions, revisions, plans, operations,
    /// publications, lineage, rendition cache). The enumeration + scan must leave every row equal.
    /// </summary>
    private static readonly string[] QueryScanTables =
    [
        "sources", "source_locations", "source_versions", "source_entries", "books", "chapters",
        "pages", "page_bindings", "regions", "region_revisions", "source_sync_plans",
        "source_operations", "source_binding_publications", "source_revision_lineage",
        "rendition_cache",
    ];

    private static string QueryScanSnapshot(string python, string dbPath)
    {
        const string code =
            "import sqlite3,sys,json\n" +
            "tables=sys.argv[2].split(',')\n" +
            "c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True)\n" +
            "c.row_factory=sqlite3.Row\n" +
            "snap={t:[dict(row) for row in c.execute('SELECT * FROM '+t)] for t in tables}\n" +
            "c.close()\n" +
            "print(json.dumps(snap,sort_keys=True))\n";
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
        startInfo.ArgumentList.Add(string.Join(",", QueryScanTables));
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
        return stdout.Trim();
    }

    /// <summary>Mirrors the production file identity derivation (sha256 of the upper path, first 16 hex).</summary>
    private static string ExpectedStableSourceId(string normalizedPath)
    {
        var digest = System.Security.Cryptography.SHA256.HashData(
            System.Text.Encoding.UTF8.GetBytes(normalizedPath.ToUpperInvariant()));
        return "src-" + Convert.ToHexString(digest).ToLowerInvariant()[..16];
    }

    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    /// <summary>
    /// FEA-11-SCAN-2 r2 (P2-3 / P1-1): the real import -> enumeration E2E. Two books reference the SAME
    /// real source imported through the production <see cref="SourceImportCoordinator"/>: the first
    /// single-book tick must send `scope=current`, the shared-source tick must send `scope=all` with
    /// both project ids (the r1 P1-1 discriminator), and `target.source_id` must be the Core
    /// `src-<uuid>` authority (≠ the App-side StableSourceId). Scan/refresh write zero Core rows.
    /// </summary>
    [Fea11ScanIpcFact]
    public async Task RealImportThenEnumeration_SharedSource_UsesAllScope_AndCoreSourceId()
    {
        var repo = FindRepository();
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(
            repo + ".workspace", "FEA-11", "fixtures", "scan-import-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var dataRoot = Path.Combine(root, "data");
        Directory.CreateDirectory(dataRoot);
        await using var client = await CoreServiceClient.StartAsync(BuildImportOptions(repo, python, dataRoot));
        await client.OpenHostSessionAsync();
        var ping = await client.PingAsync();
        Assert.Contains("source.sync.enumerate/1", ping.Capabilities);
        Assert.Contains("source.read/1", ping.Capabilities);

        var registry = new SourceAccessRegistry(Path.Combine(root, "host-data"));
        var sources = new SourceReadCoordinator(client, registry, () => true);
        HostCommandDispatcher dispatcher = new(
            client,
            bridge: null,
            hostLocal: async (name, payload, token) => new HostCommandResult(
                name,
                HostCommandStatus.Implemented,
                HostCommandChannel.HostLocal,
                await sources.InvokeAsync(name, payload, token)));
        await using var imports = new SourceImportCoordinator(dispatcher, sources, root);

        var png = await WriteOnePixelPngAsync(root);
        var imported = new ReferenceImportSource(png, IsFolder: false);
        var dbPath = Path.Combine(dataRoot, "library.db");

        var (book1, chapter1) = await CreateBookChapterAsync(client, "scan2-shared-1");
        var receipt1 = await ImportAsync(imports, chapter1, imported);
        Assert.Equal(SourceImportOperationState.Completed, receipt1.State);

        var scanOptions = new SourceScanOptions
        {
            Enabled = true,
            IntervalSeconds = 60,
            MaxTargetsPerTick = 8,
            MaxBytesPerSource = 256L * 1024 * 1024,
            MaxEntriesPerSource = 10000,
        };
        var executor = new HostSourceScanExecutor(client, sources, scanOptions);
        var enumerator = new HostSourceScanTargetEnumerator(client, registry);
        await using var scheduler = new SourceScanScheduler(scanOptions, executor, enumerator: enumerator);

        Assert.True(await scheduler.RefreshTargetsAsync());
        var target1 = Assert.Single(scheduler.Snapshot().Targets);
        var coreSourceId = QuerySingleSourceId(python, dbPath);
        Assert.StartsWith("src-", coreSourceId, StringComparison.Ordinal);
        Assert.Equal(coreSourceId, target1.SourceId);
        Assert.NotEqual(ExpectedStableSourceId(Path.GetFullPath(png)), target1.SourceId);
        Assert.Equal(new[] { book1 }, QueryBookIdsForSource(python, dbPath, coreSourceId));

        Assert.True(await scheduler.TickAsync());
        Assert.NotEqual(SourceScanResults.Error, scheduler.Snapshot().Targets.Single().LastResult);
        var singlePayload = LatestScanSourceSyncPayload(client);
        Assert.Equal("current", singlePayload.GetProperty("scope").GetString());
        Assert.Equal(new[] { book1 }, PayloadProjectIds(singlePayload));

        // The SAME real source imported into a second book: Core reuses src-<uuid> and enumeration
        // now returns two project ids; the scan payload must switch to scope=all.
        var (book2, chapter2) = await CreateBookChapterAsync(client, "scan2-shared-2");
        var receipt2 = await ImportAsync(imports, chapter2, imported);
        Assert.Equal(SourceImportOperationState.Completed, receipt2.State);
        Assert.Equal(coreSourceId, QuerySingleSourceId(python, dbPath));
        Assert.Equal(
            new[] { book1, book2 }.OrderBy(id => id, StringComparer.Ordinal).ToArray(),
            QueryBookIdsForSource(python, dbPath, coreSourceId));

        var snapshotBefore = QueryScanSnapshot(python, dbPath);
        Assert.True(await scheduler.RefreshTargetsAsync());
        Assert.Single(scheduler.Snapshot().Targets);
        Assert.True(await scheduler.TickAsync());
        Assert.NotEqual(SourceScanResults.Error, scheduler.Snapshot().Targets.Single().LastResult);
        var sharedPayload = LatestScanSourceSyncPayload(client);
        Assert.Equal("all", sharedPayload.GetProperty("scope").GetString());
        Assert.Equal(
            new[] { book1, book2 }.OrderBy(id => id, StringComparer.Ordinal).ToArray(),
            PayloadProjectIds(sharedPayload));

        // Refresh + scans stay read-only; repeated Refresh is idempotent.
        var snapshotAfter = QueryScanSnapshot(python, dbPath);
        Assert.Equal(snapshotBefore, snapshotAfter);
        Assert.True(await scheduler.RefreshTargetsAsync());
        Assert.Single(scheduler.Snapshot().Targets);

        var evidence = new
        {
            @case = "P2-3 real import -> enumeration E2E + P1-1 shared-source scope",
            core = "real volatile python core (stdio IPC)",
            app_registration_used = false,
            core_source_id = coreSourceId,
            stable_source_id = ExpectedStableSourceId(Path.GetFullPath(png)),
            books = new[] { book1, book2 }.OrderBy(id => id, StringComparer.Ordinal).ToArray(),
            single_book_scope = singlePayload.GetProperty("scope").GetString(),
            shared_book_scope = sharedPayload.GetProperty("scope").GetString(),
            shared_project_ids = PayloadProjectIds(sharedPayload),
            db_snapshot_unchanged = true,
        };
        await File.WriteAllTextAsync(
            Path.Combine(root, "import-e2e.json"),
            JsonSerializer.Serialize(evidence, new JsonSerializerOptions { WriteIndented = true }));
        await File.WriteAllTextAsync(
            Path.Combine(root, "import-e2e.txt"),
            "FEA-11-SCAN-2 r2 real import -> enumeration E2E\n"
            + "DataRoot=" + dataDirOrRoot(dataRoot) + "\n"
            + "core_source_id=" + coreSourceId + "\n"
            + "single_book_scope=current\n"
            + "shared_book_scope=all\n"
            + "db_snapshot_unchanged=true\nPASS\n");
    }

    private static string dataDirOrRoot(string dataRoot) => Path.GetDirectoryName(dataRoot) ?? dataRoot;

    // ---------------------------------------------------------------------------------------
    // FEA-11-L-S4-B (C-16 v1.5 §2.5): B1 explicit re-authorization -> reattest -> enumeration
    // ---------------------------------------------------------------------------------------

    /// <summary>
    /// AC-LS4B-6 (real IPC closed loop): a source the user explicitly re-authorized (B1's
    /// Registry-level revoke + re-register over the SAME file) is no longer dropped by the
    /// cold-start/refresh enumeration once the Host re-attests the Core location row. Phase A
    /// proves the current typed skip (the Core still records the REVOKED registry);
    /// phase B proves exactly ONE <c>ReattestSourceLocation</c> frame (ids only, no path) and the
    /// recovered target carrying the LIVE registry/generation.
    ///
    /// FEA-11-L-S4-B-1 (AC-SER-1): the recovered target's EXECUTION face is asserted too — the
    /// following tick authorizes the scan with the target's OWN live <c>(registry_id, generation)</c>
    /// entry and sends exactly ONE <c>ScanSourceSync</c> (no path on the wire), so the tick result is
    /// <c>ok</c> instead of the pre-fix <c>error</c>/<c>SOURCE_ACCESS_DENIED</c> (the L-S4-B baseline
    /// evidence recorded that error; no backoff applies here because this phase-B scheduler never
    /// ticked before).
    /// </summary>
    [Fea11ScanIpcFact]
    public async Task ReauthorizedSource_IsReattested_ThenEnumerated_WithoutReimport()
    {
        var (repo, python, root, receipt) = await SeedAsync();
        var dbPath = Path.Combine(root, "library.db");
        var oldZip = receipt.GetProperty("old_zip").GetString()!;
        var options = BuildOptions(repo, python, root);
        await using var client = await CoreServiceClient.StartAsync(options);
        await client.OpenHostSessionAsync();
        Assert.Contains("source.reattest/1", (await client.PingAsync()).Capabilities);

        var registry = new SourceAccessRegistry(root);
        var oldEntry = registry.Register("fea11-l-s4b", [oldZip]);
        var facts = ReadFileIdentity(oldZip);
        UpdateLocationGenerationRow(
            python, dbPath, oldEntry.RegistryId, oldEntry.Generation, facts);
        var coreSourceId = QuerySourceId(python, dbPath);

        // The user's EXPLICIT B1 action at the Registry level: revoke the stale entry, then
        // register ONE new entry over the SAME registered root (exactly what B1 does). The Core
        // location row is deliberately left on the OLD (now revoked) registry pair.
        registry.Revoke(oldEntry.RegistryId);
        await Task.Delay(5);
        var liveEntry = registry.Register("fea11-l-s4b-reauth", [oldZip]);
        var entriesBefore = DescribeRegistryEntries(registry.List());
        var locationBefore = QueryLocationRow(python, dbPath);

        var scanOptions = new SourceScanOptions
        {
            Enabled = true,
            IntervalSeconds = 60,
            MaxTargetsPerTick = 8,
            MaxBytesPerSource = 256L * 1024 * 1024,
            MaxEntriesPerSource = 10000,
        };
        var sources = new SourceReadCoordinator(client, registry, () => true);

        // ---- phase A: B1-only state (Core records the REVOKED registry) -> typed skip.
        var legacyEnumerator = new HostSourceScanTargetEnumerator(client, registry);
        await using (var legacyScheduler = new SourceScanScheduler(
                         scanOptions,
                         new HostSourceScanExecutor(client, sources, scanOptions),
                         enumerator: legacyEnumerator))
        {
            Assert.True(await legacyScheduler.RefreshTargetsAsync());
            Assert.Empty(legacyScheduler.Snapshot().Targets);
            Assert.Equal(1, legacyScheduler.Snapshot().Enumeration!.SkippedTargets);
        }

        Assert.Empty(RequestLines(client, "ReattestSourceLocation"));
        var tablesBefore = QueryScanSnapshot(python, dbPath);

        // ---- phase B: the production enumerator (coordinator + options) re-attests ONCE.
        var warnings = new List<string>();
        var enumerator = new HostSourceScanTargetEnumerator(
            client, registry, sources, scanOptions, warnLog: warnings.Add);
        await using var scheduler = new SourceScanScheduler(
            scanOptions,
            new HostSourceScanExecutor(client, sources, scanOptions),
            enumerator: enumerator);

        Assert.True(await scheduler.RefreshTargetsAsync(), string.Join(";", warnings));
        var status = Assert.Single(scheduler.Snapshot().Targets);
        Assert.Equal(coreSourceId, status.SourceId);
        Assert.Equal(0, scheduler.Snapshot().Enumeration!.SkippedTargets);
        // The scheduler status projection is path/target-id free (frozen Host surface); the mapped
        // target's live registry identity is verified through the same production enumerator (the
        // Core row is already re-attested, so this second read maps WITHOUT a second re-attest).
        var mapped = await enumerator.EnumerateAsync(CancellationToken.None);
        Assert.True(mapped.Ok, mapped.ErrorCode);
        var target = Assert.Single(mapped.Targets);
        Assert.Equal(coreSourceId, target.SourceId);
        Assert.Equal(liveEntry.RegistryId, target.RegistryId);
        Assert.Equal(liveEntry.Generation, target.Generation);
        Assert.Equal("zip", target.SourceKind);

        // Exactly ONE re-attest frame; closed ids-only payload; no absolute path.
        var reattestLines = RequestLines(client, "ReattestSourceLocation");
        Assert.Single(reattestLines);
        using (var document = JsonDocument.Parse(reattestLines[0]))
        {
            var payload = document.RootElement.GetProperty("payload");
            Assert.Equal(
                new[] { "grant_id", "source_id" },
                payload.EnumerateObject().Select(property => property.Name)
                    .OrderBy(name => name, StringComparer.Ordinal).ToArray());
            Assert.Equal(coreSourceId, payload.GetProperty("source_id").GetString());
            Assert.DoesNotContain(oldZip, reattestLines[0], StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(root, reattestLines[0], StringComparison.OrdinalIgnoreCase);
        }

        // The Core location row moved ONLY its two auth columns; the audit time/identity stayed.
        var locationAfter = QueryLocationRow(python, dbPath);
        foreach (var name in new[]
                 {
                     "location_id", "content_digest", "volume_serial", "file_id", "size_bytes",
                     "is_current", "observed_at", "last_verified_at",
                 })
        {
            Assert.Equal(
                locationBefore.GetProperty(name).GetRawText(),
                locationAfter.GetProperty(name).GetRawText());
        }

        Assert.Equal(liveEntry.RegistryId, locationAfter.GetProperty("registry_id").GetString());
        Assert.Equal(liveEntry.Generation, locationAfter.GetProperty("authorization_generation").GetInt32());

        // The Host registry itself was NOT touched by the re-attest (no new/revoked entry, no
        // roots/identity/generation change; minting keeps its pre-existing last_used_at audit).
        Assert.Equal(entriesBefore, DescribeRegistryEntries(registry.List()));

        // The scan table snapshot: only source_locations differs; every other table byte-identical.
        var tablesAfter = QueryScanSnapshot(python, dbPath);
        using (var before = JsonDocument.Parse(tablesBefore))
        using (var after = JsonDocument.Parse(tablesAfter))
        {
            foreach (var table in before.RootElement.EnumerateObject())
            {
                if (table.Name == "source_locations") continue;
                Assert.Equal(
                    table.Value.GetRawText(),
                    after.RootElement.GetProperty(table.Name).GetRawText());
            }
        }

        // FEA-11-L-S4-B-1 (AC-SER-1): the recovered target's EXECUTION face is recovered too. The tick
        // authorizes the scan with the target's OWN live (registry_id, generation) entry (verified from
        // the same snapshot, never re-resolved by path) and sends exactly ONE ScanSourceSync. Before
        // this card the same tick was Error(SOURCE_ACCESS_DENIED): the path-exact resolver met the
        // sibling REVOKED row first, even though the live exact row existed.
        Assert.True(await scheduler.TickAsync());
        var tickVerdict = scheduler.Snapshot().Targets.Single();
        Assert.Equal(SourceScanResults.Ok, tickVerdict.LastResult);
        var scanLines = RequestLines(client, "ScanSourceSync");
        Assert.Single(scanLines);
        Assert.DoesNotContain(oldZip, scanLines[0], StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain(root, scanLines[0], StringComparison.OrdinalIgnoreCase);
        // The EXECUTION face did not touch the Host registry either: the scan reuses the verified live
        // entry and the mint's pre-existing last_used_at audit is excluded from the structure check.
        Assert.Equal(entriesBefore, DescribeRegistryEntries(registry.List()));

        var evidence = new
        {
            @case = "AC-LS4B-6 + FEA-11-L-S4-B-1 AC-SER-1 (real IPC closed loop: B1 -> reattest -> "
                + "enumeration recovery -> scan execution recovery)",
            core = "real volatile python core (stdio IPC)",
            app_registration_used = false,
            core_source_id = coreSourceId,
            old_registry_id = oldEntry.RegistryId,
            live_registry_id = liveEntry.RegistryId,
            live_generation = liveEntry.Generation,
            reattest_frames = reattestLines.Length,
            reattest_payload_keys = new[] { "grant_id", "source_id" },
            enumeration_recovered = true,
            recovered_target = new
            {
                source_id = target.SourceId,
                registry_id = target.RegistryId,
                generation = target.Generation,
                source_kind = target.SourceKind,
            },
            location_after = new
            {
                registry_id = locationAfter.GetProperty("registry_id").GetString(),
                authorization_generation = locationAfter.GetProperty("authorization_generation").GetInt32(),
                identity_unchanged = true,
                last_verified_at_unchanged = true,
            },
            host_registry_unchanged = true,
            other_tables_unchanged = true,
            tick_verdict = new
            {
                last_result = tickVerdict.LastResult,
                scan_frames = scanLines.Length,
                counts = tickVerdict.Counts,
                execution_face_recovered = true,
                path_hits = 0,
            },
            reimport_or_apply = false,
        };
        await File.WriteAllTextAsync(
            Path.Combine(root, "reattest-ipc.json"),
            JsonSerializer.Serialize(evidence, new JsonSerializerOptions { WriteIndented = true }));
        await File.WriteAllTextAsync(
            Path.Combine(root, "reattest-ipc.txt"),
            "FEA-11-L-S4-B AC-LS4B-6 + FEA-11-L-S4-B-1 AC-SER-1 real IPC "
            + "(B1 explicit re-auth -> reattest -> enumeration -> scan execution)\n"
            + "DataRoot=" + root + "\n"
            + "phase_a_targets=0 phase_a_skipped=1\n"
            + "reattest_frames=" + reattestLines.Length + " payload=ids-only path_hits=0\n"
            + "phase_b_targets=1 core_source_id=" + coreSourceId + "\n"
            + "live_registry_id=" + liveEntry.RegistryId + " generation=" + liveEntry.Generation + "\n"
            + "location_auth_columns_only=true last_verified_at_unchanged=true\n"
            + "host_registry_unchanged=true other_tables_unchanged=true reimport_or_apply=false\n"
            + "tick_last_result=" + tickVerdict.LastResult + " scan_frames=" + scanLines.Length
            + " wire_path_hits=0 (execution face recovered with the target's own live registry pair)\n"
            + "PASS\n");
    }

    private static JsonElement QueryLocationRow(string python, string dbPath)
    {
        const string code =
            "import sqlite3,sys,json\n" +
            "c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True)\n" +
            "c.row_factory=sqlite3.Row\n" +
            "row=c.execute('SELECT * FROM source_locations ORDER BY location_id LIMIT 1').fetchone()\n" +
            "print(json.dumps(dict(row) if row is not None else {}))\n" +
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
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
        return JsonDocument.Parse(stdout.Trim()).RootElement.Clone();
    }

    private static string[] RequestLines(CoreServiceClient client, string command) =>
        client.Wire.Frames.Select(frame => frame.RequestLine)
            .Where(line => RequestCommand(line) == command).ToArray();

    private static string[] DescribeRegistryEntries(SourceAuthorization[] entries) =>
        entries.Select(entry =>
                entry.RegistryId + "|" + entry.Locator + "|" + entry.Generation + "|"
                + entry.CreatedAt + "|" + entry.RevokedAt + "|"
                + string.Join(";", entry.Roots.Select(rootEntry =>
                    rootEntry.Root + "|" + rootEntry.VolumeSerial + "|" + rootEntry.FileId)))
            .ToArray();


    private static string FindRepository()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }

        return directory?.FullName ?? throw new InvalidOperationException("repository not found");
    }

    private static CoreServiceOptions BuildImportOptions(string repo, string python, string dataRoot) => new()
    {
        ExecutablePath = python,
        AdditionalArguments =
        [
            "-X", "utf8", "-c",
            $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');"
            + "import bootstrap.core_service as m;raise SystemExit(m.main())",
        ],
        DataRoot = dataRoot,
        DerivedRoot = Path.Combine(dataRoot, "derived"),
        CatalogDbPath = Path.Combine(dataRoot, "catalog", "catalog.sqlite"),
        StderrLogPath = Path.Combine(dataRoot, "..", "core.stderr.log"),
        WireLogPath = Path.Combine(dataRoot, "..", "wire.ndjson"),
        StartupTimeout = TimeSpan.FromSeconds(90),
        RequestTimeout = TimeSpan.FromSeconds(90),
    };

    private static async Task<string> WriteOnePixelPngAsync(string root)
    {
        var directory = Path.Combine(root, "source");
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, "page.png");
        await File.WriteAllBytesAsync(path, Convert.FromBase64String(OnePixelPngBase64));
        return path;
    }

    private static async Task<(string BookId, string ChapterId)> CreateBookChapterAsync(
        CoreServiceClient client, string title)
    {
        var book = await client.CreateBookAsync("FEA-11-SCAN-2 " + title);
        var chapter = await client.SendAsync(
            "CreateChapter", 8,
            writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("book_id", book.BookId);
                writer.WriteString("title", title);
                writer.WriteEndObject();
            },
            TimeSpan.FromSeconds(30));
        return (book.BookId, chapter.Result!.Value.GetProperty("chapter_id").GetString()!);
    }

    private static async Task<SourceImportReceipt> ImportAsync(
        SourceImportCoordinator imports, string chapterId, ReferenceImportSource source)
    {
        var plan = await imports.PlanAsync(chapterId, new[] { source }, "skip", CancellationToken.None);
        Assert.NotNull(plan);
        var start = await imports.StartAsync(plan!, null, CancellationToken.None);
        Assert.True(start.Ok, start.ErrorCode);
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(90);
        while (DateTime.UtcNow < deadline)
        {
            var receipt = await imports.GetReceiptAsync(start.OperationId!, CancellationToken.None);
            if (receipt is { IsTerminal: true })
            {
                return receipt;
            }

            await Task.Delay(100);
        }

        throw new TimeoutException("import did not reach a terminal state");
    }

    private static string QuerySingleSourceId(string python, string dbPath)
    {
        var ids = QueryLines(python, dbPath, "SELECT source_id FROM sources ORDER BY source_id");
        Assert.True(ids.Length == 1, "expected exactly one real Core source, got: " + string.Join(",", ids));
        return ids[0];
    }

    private static string[] QueryBookIdsForSource(string python, string dbPath, string sourceId)
    {
        var safe = sourceId.Replace("'", "''", StringComparison.Ordinal);
        return QueryLines(python, dbPath,
            "SELECT DISTINCT c.book_id FROM page_bindings pb"
            + " JOIN pages p ON p.page_id=pb.page_id JOIN chapters c ON c.chapter_id=p.chapter_id"
            + " WHERE pb.source_id='" + safe + "' ORDER BY c.book_id");
    }

    private static string[] QueryLines(string python, string dbPath, string sql)
    {
        var startInfo = new ProcessStartInfo(python)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(
            "import sqlite3,sys\n"
            + "c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True)\n"
            + "print('\\n'.join(str(row[0]) for row in c.execute(sys.argv[2])))\n"
            + "c.close()\n");
        startInfo.ArgumentList.Add(dbPath);
        startInfo.ArgumentList.Add(sql);
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
        return stdout.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
    }

    private static JsonElement LatestScanSourceSyncPayload(CoreServiceClient client)
    {
        for (var index = client.Wire.Frames.Count - 1; index >= 0; index--)
        {
            using var document = JsonDocument.Parse(client.Wire.Frames[index].RequestLine);
            var root = document.RootElement;
            if (root.TryGetProperty("command", out var command)
                && command.ValueKind == JsonValueKind.String
                && command.GetString() == "ScanSourceSync"
                && root.TryGetProperty("payload", out var payload))
            {
                return payload.Clone();
            }
        }

        throw new InvalidOperationException("no ScanSourceSync frame was sent");
    }

    private static string[] PayloadProjectIds(JsonElement payload) =>
        payload.GetProperty("project_ids").EnumerateArray().Select(value => value.GetString()!).ToArray();

    // ---------------------------------------------------------------------------------------
    // Fixture plumbing (isolated workspace root; no real user data).
    // ---------------------------------------------------------------------------------------

    private static string Sha256(byte[] bytes) =>
        Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant();

    private static string? RequestCommand(string requestLine)
    {
        try
        {
            using var document = JsonDocument.Parse(requestLine);
            return document.RootElement.TryGetProperty("command", out var command)
                   && command.ValueKind == JsonValueKind.String
                ? command.GetString()
                : null;
        }
        catch (JsonException)
        {
            return null;
        }
    }

    private static readonly SemaphoreSlim SeedGate = new(1, 1);

    private static async Task<(string Repo, string Python, string Root, JsonElement Receipt)> SeedAsync()
    {
        await SeedGate.WaitAsync();
        try
        {
            var directory = new DirectoryInfo(AppContext.BaseDirectory);
            while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
            {
                directory = directory.Parent;
            }

            var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
            var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
            var root = Path.Combine(
                repo + ".workspace", "FEA-11", "fixtures", "scan-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            await RunPythonAsync(
                python, repo,
                "tests/fea11/support/ipc_seed.py",
                "--data-root", root,
                "--db", Path.Combine(root, "library.db"));
            using var receiptDocument = JsonDocument.Parse(
                await File.ReadAllTextAsync(Path.Combine(root, "ipc-seed-receipt.json")));
            return (repo, python, root, receiptDocument.RootElement.Clone());
        }
        finally
        {
            SeedGate.Release();
        }
    }

    private static CoreServiceOptions BuildOptions(string repo, string python, string root) => new()
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

    private static async Task RunPythonAsync(string python, string repo, params string[] arguments)
    {
        var startInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        foreach (var argument in arguments) startInfo.ArgumentList.Add(argument);
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0, await stdout + await stderr);
    }

    /// <summary>Aligns the isolated fixture's C-17 location row with real file + Host registry facts.</summary>
    private static void UpdateLocationRow(string python, string dbPath, string registryId, FileIdentity facts)
    {
        const string code =
            "import sqlite3,sys\n" +
            "c=sqlite3.connect(sys.argv[1])\n" +
            "c.execute('UPDATE source_locations SET registry_id=?, volume_serial=?, file_id=?, size_bytes=? WHERE location_id=?',(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),'sl-s1'))\n" +
            "c.commit()\n" +
            "c.close()\n" +
            "print('LOCATION_UPDATED')\n";
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
        startInfo.ArgumentList.Add(facts.Volume.ToString());
        startInfo.ArgumentList.Add(facts.FileId.ToString());
        startInfo.ArgumentList.Add(facts.Size.ToString());
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
    }

    /// <summary>
    /// Seeds the old version's entry rows with the REAL frozen pixel-digest/1 profiles of the old
    /// container members (the production matcher can only assert <c>changed</c> when both sides carry
    /// complete comparable pixel evidence; legacy v7 rows otherwise degrade to needs-confirmation).
    /// Isolated fixture only; evidence computed with the production helpers, never forged.
    /// </summary>
    private static void SeedOldPixelProfiles(string python, string repo, string zipPath, string dbPath)
    {
        const string code =
            "import sys,hashlib,io,json,zipfile,sqlite3\n" +
            "repo=sys.argv[1]\n" +
            "sys.path.insert(0,repo)\n" +
            "sys.path.insert(0,repo+'/src')\n" +
            "from application.sources.scanner import (_rgb_pixel_columns,_exif_orientation," +
            "canonical_pixel_params_json,PIXEL_PROFILE_ALGORITHM,PIXEL_DECODER_NAME,PIXEL_DECODER_VERSION)\n" +
            "from PIL import Image, ImageOps\n" +
            "zip_path,db_path=sys.argv[2],sys.argv[3]\n" +
            "conn=sqlite3.connect(db_path)\n" +
            "with zipfile.ZipFile(zip_path) as archive:\n" +
            "    for locator in ('001.png','002.png'):\n" +
            "        image=Image.open(io.BytesIO(archive.read(locator)))\n" +
            "        orientation=_exif_orientation(image)\n" +
            "        normalised=ImageOps.exif_transpose(image)\n" +
            "        columns=_rgb_pixel_columns(normalised)\n" +
            "        assert columns is not None, 'old container member has no pixel profile'\n" +
            "        width,height,pixels=columns\n" +
            "        digest=hashlib.sha256(); digest.update(f'{width}x{height}'.encode('ascii'));" +
            "digest.update(b'\\x00'); digest.update(pixels)\n" +
            "        conn.execute('UPDATE source_entries SET pixel_digest=?, pixel_digest_algorithm=?,'" +
            " ' width=?, height=?, orientation=?, decoder_name=?, decoder_version=?,'" +
            " ' decoder_params_json=? WHERE locator=? AND version_id=\\'sv1\\''," +
            " (digest.hexdigest(),PIXEL_PROFILE_ALGORITHM,width,height,orientation," +
            "PIXEL_DECODER_NAME,PIXEL_DECODER_VERSION,canonical_pixel_params_json(),locator))\n" +
            "conn.commit()\n" +
            "conn.close()\n" +
            "print('PIXEL_PROFILES_SEEDED')\n";
        var startInfo = new ProcessStartInfo(python)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(code);
        startInfo.ArgumentList.Add(repo);
        startInfo.ArgumentList.Add(zipPath);
        startInfo.ArgumentList.Add(dbPath);
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
    }

    /// <summary>Reads the read-only SQLite snapshot that the scan must never change.</summary>
    private static string QuerySnapshot(string python, string dbPath)
    {
        const string code =
            "import sqlite3,sys,json\n" +
            "c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True)\n" +
            "c.row_factory=sqlite3.Row\n" +
            "query=lambda sql:[dict(row) for row in c.execute(sql)]\n" +
            "snap={'page_bindings':query('SELECT binding_id,page_id,binding_version,source_id,entry_id,accepted_source_version,status,authorization_generation FROM page_bindings ORDER BY binding_id')," +
            "'source_versions':query('SELECT version_id,source_id,content_digest,size_bytes FROM source_versions ORDER BY version_id')," +
            "'source_entries':query('SELECT source_id,version_id,entry_id,locator,ordinal,content_digest FROM source_entries ORDER BY entry_id')," +
            "'sources':query('SELECT source_id,source_kind FROM sources ORDER BY source_id')," +
            "'source_locations':query('SELECT location_id,source_id,registry_id,authorization_generation,content_digest,volume_serial,file_id,size_bytes,is_current FROM source_locations ORDER BY location_id')}\n" +
            "c.close()\n" +
            "print(json.dumps(snap,sort_keys=True))\n";
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
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        Assert.True(process.ExitCode == 0, stdout + stderr);
        return stdout.Trim();
    }

    private sealed record FileIdentity(ulong Volume, ulong FileId, long Size);

    /// <summary>Real file identity (volume serial + file index + size), the facts the Host grant carries.</summary>
    private static FileIdentity ReadFileIdentity(string path)
    {
        using var handle = File.OpenHandle(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (!GetFileInformationByHandle(handle, out var info))
        {
            throw new InvalidOperationException("GetFileInformationByHandle failed");
        }

        var fileId = ((ulong)info.IndexHigh << 32) | info.IndexLow;
        var size = ((long)info.SizeHigh << 32) | info.SizeLow;
        return new FileIdentity(info.Volume, fileId, size);
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct ByHandleFileInformation
    {
        public uint Attributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
        public uint Volume;
        public uint SizeHigh;
        public uint SizeLow;
        public uint Links;
        public uint IndexHigh;
        public uint IndexLow;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetFileInformationByHandle(
        SafeFileHandle handle, out ByHandleFileInformation information);

    private sealed class Fea11ScanIpcFactAttribute : FactAttribute
    {
        public Fea11ScanIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "set NEWMANGA_FEA11_IPC=1 for the real isolated Python Core scan IPC test";
            }
        }
    }
}
