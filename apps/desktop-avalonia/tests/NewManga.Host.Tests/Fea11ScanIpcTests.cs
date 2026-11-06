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
