using System.Diagnostics;
using System.IO.Compression;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-L-S1-B-RECOVERY-REAUTH-1 (B1, AC-LSB-9): ONE gated real-stdio-IPC closed loop, over the
/// real Python Core, the production Host source/registry face and the production App-side
/// <see cref="SourceImportCoordinator"/> / <see cref="SourceRecoveryCoordinator"/>.
///
/// Phase A — the literal card scenario: register → replace the file at the SAME path → preview
/// fails with the typed <c>SOURCE_REGISTRY_UNAVAILABLE</c> → EXPLICIT re-authorization (revoke all
/// stale entries → re-register the entry's own registered root → re-preview) → the re-import
/// completes → <c>source_list_scan_targets</c> returns the NEW authorization for the new physical
/// identity. A replacement changes the file's physical identity, so the Core records a NEW source
/// location for it (an in-place refresh requires an unchanged identity — phase B).
///
/// Phase B — the L-S4 A in-place refresh: the registered root's recorded physical identity no
/// longer matches the file (crafted registry, file untouched, i.e. the exact invariant a same-path
/// replacement breaks) → typed failure → explicit re-authorization → re-import → the SAME
/// <c>source_locations</c> row is refreshed in place (same <c>location_id</c>, new
/// <c>registry_id</c>, <c>last_verified_at</c> set) and the scan enumeration follows the new
/// authorization generation.
///
/// Opt-in only (<c>NEWMANGA_FEA11_IPC=1</c>): it starts the real Python Core. The fixture lives in
/// the task's isolated workspace root, NEVER under <c>verification/FEA-09/**</c>.
/// </summary>
public sealed class SourceRecoveryIpcTests : IClassFixture<SourceRecoveryIpcTests.RecoveryIpcContext>
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    private readonly RecoveryIpcContext _context;

    public SourceRecoveryIpcTests(RecoveryIpcContext context)
    {
        _context = context;
    }

    [RecoveryIpcFact]
    public async Task SamePathReplacement_IsRecoveredOnlyByAnExplicitReauthorization()
    {
        var token = CancellationToken.None;
        var evidence = new JsonObject();

        // =========================================================== Phase A: same-path replacement
        var sourceA = Path.Combine(_context.Root, "phase-a", "book.zip");
        await WriteZipAsync(sourceA, ("001.png", OnePixelPng()), ("002.png", OnePixelPng()));
        var (_, chapterA1) = await _context.CreateChapterAsync("recovery-a1");

        var planA1 = await _context.Imports.PlanAsync(
            chapterA1, [new ReferenceImportSource(sourceA, IsFolder: false)], "skip", token);
        Assert.NotNull(planA1);
        var entryA = _context.ActiveEntryFor(sourceA);
        var startA1 = await _context.Imports.StartAsync(planA1!, password: null, token);
        Assert.True(startA1.Ok, startA1.ErrorCode + " " + startA1.Message);
        var receiptA1 = await _context.AwaitTerminalAsync(startA1.OperationId!);
        Assert.Equal(SourceImportOperationState.Completed, receiptA1.State);

        var baselineTargets = await _context.ListScanTargetsAsync(token);
        var baselineTarget = baselineTargets.Single(target => target.RegistryId == entryA.RegistryId);
        Assert.Equal(1, baselineTarget.Generation);
        var sourceAId = baselineTarget.SourceId;

        // The user's file was REPLACED at the same path (delete + recreate = a new physical identity).
        File.Delete(sourceA);
        await WriteZipAsync(sourceA, ("001.png", OnePixelPng()));

        // (1) The re-import preview fails TYPED at the Host mint leg (no Core command is sent), and
        //     NOTHING was registered/revoked on the failure branch (AC-LSB-5 / R-1).
        var registryBefore = _context.Registry.List().Length;
        var failure = await Assert.ThrowsAsync<SourceAccessException>(() => _context.Imports.PlanAsync(
            chapterA1, [new ReferenceImportSource(sourceA, IsFolder: false)], "skip", token));
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", failure.Code);
        Assert.Equal(registryBefore, _context.Registry.List().Length); // no automatic re-registration
        Assert.Null(_context.Registry.List().Single(entry => entry.RegistryId == entryA.RegistryId).RevokedAt);

        // (2) The READ-ONLY probe decides: readable storage + failed mint → re-authorize ONLY.
        _context.ResetHostFrames();
        var diagnosisA = await _context.Recovery.DiagnoseAsync(
            [new SourceRecoveryTarget(sourceA, IsFolder: false)], "SOURCE_REGISTRY_UNAVAILABLE", hostSideMintFailure: true, cancellationToken: token);
        Assert.Equal(SourceRecoveryAction.ReauthorizeSource, diagnosisA.Action);
        Assert.Equal(1, diagnosisA.StaleEntryCount);
        Assert.Equal("book.zip", diagnosisA.SourceLeafName);
        Assert.Equal(new[] { "source_list_roots" }, _context.HostFrameNames());

        // (3) The EXPLICIT action: revoke EVERY stale entry of the path, then re-register its own
        //     registered root, in that order.
        var resultA = await _context.Recovery.ReauthorizeAsync([new SourceRecoveryTarget(sourceA, IsFolder: false)], token);
        Assert.True(resultA.Ok, resultA.ErrorCode + " " + resultA.Message);
        Assert.Equal(1, resultA.RevokedCount);
        Assert.Equal(1, resultA.RegisteredCount);
        Assert.Equal(
            new[] { "source_list_roots", "source_revoke_root", "source_register_root" },
            _context.HostFrameNames().Skip(1).ToArray());

        var entriesAfterA = _context.Registry.List().Where(entry => IsSameRoot(entry, sourceA)).ToArray();
        Assert.Equal(2, entriesAfterA.Length);
        var revoked = entriesAfterA.Single(entry => entry.RegistryId == entryA.RegistryId);
        Assert.NotNull(revoked.RevokedAt);           // generation+1 + revoked_at, persisted
        Assert.Equal(2, revoked.Generation);
        var activeA = entriesAfterA.Single(entry => entry.RevokedAt is null);
        Assert.Equal(1, activeA.Generation);         // exactly ONE active entry for the path

        // (4) The re-preview succeeds and the re-import completes in a fresh chapter (new pages).
        var (_, chapterA2) = await _context.CreateChapterAsync("recovery-a2");
        var planA2 = await _context.Imports.PlanAsync(
            chapterA2, [new ReferenceImportSource(sourceA, IsFolder: false)], "skip", token);
        Assert.NotNull(planA2);
        var startA2 = await _context.Imports.StartAsync(planA2!, password: null, token);
        Assert.True(startA2.Ok, startA2.ErrorCode + " " + startA2.Message);
        var receiptA2 = await _context.AwaitTerminalAsync(startA2.OperationId!);
        Assert.Equal(SourceImportOperationState.Completed, receiptA2.State);
        Assert.True(receiptA2.Totals.ImportedPages >= 1);

        // (5) The scan enumeration follows the NEW authorization for the replaced file's source.
        var targetsAfterA = await _context.ListScanTargetsAsync(token);
        var followedA = targetsAfterA.Single(target => target.RegistryId == activeA.RegistryId);
        Assert.Equal(1, followedA.Generation);
        Assert.NotEqual(sourceAId, followedA.SourceId); // a replacement is a new physical identity
        // The superseded physical identity keeps its (now revoked) registry id in the read-only
        // Core projection — the HOST scheduler drops revoked registry ids (fail-closed, unchanged).
        Assert.DoesNotContain(targetsAfterA, target =>
            target.SourceId == followedA.SourceId && target.RegistryId == entryA.RegistryId);

        // =========================================================== Phase B: L-S4 A in-place refresh
        var sourceB = Path.Combine(_context.Root, "phase-b", "book.zip");
        await WriteZipAsync(sourceB, ("001.png", OnePixelPng()));
        var (_, chapterB) = await _context.CreateChapterAsync("recovery-b");

        var planB1 = await _context.Imports.PlanAsync(
            chapterB, [new ReferenceImportSource(sourceB, IsFolder: false)], "skip", token);
        Assert.NotNull(planB1);
        var entryB = _context.ActiveEntryFor(sourceB);
        var startB1 = await _context.Imports.StartAsync(planB1!, password: null, token);
        Assert.True(startB1.Ok, startB1.ErrorCode + " " + startB1.Message);
        var receiptB1 = await _context.AwaitTerminalAsync(startB1.OperationId!);
        Assert.Equal(SourceImportOperationState.Completed, receiptB1.State);

        var targetsB1 = await _context.ListScanTargetsAsync(token);
        var baselineB = targetsB1.Single(target => target.RegistryId == entryB.RegistryId);
        var locationBefore = _context.QueryLocationRows(baselineB.SourceId).Single();
        Assert.Equal(entryB.RegistryId, locationBefore.RegistryId);
        Assert.Equal(1, locationBefore.Generation);

        // The registered root no longer matches the file at that path, while the FILE itself keeps
        // its physical identity — precisely the invariant a same-path replacement breaks, and the
        // only configuration in which L-S4 A's in-place refresh applies.
        _context.CraftRootIdentity(entryB.RegistryId);
        var failureB = await Assert.ThrowsAsync<SourceAccessException>(() => _context.Imports.PlanAsync(
            chapterB, [new ReferenceImportSource(sourceB, IsFolder: false)], "skip", token));
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", failureB.Code);

        var diagnosisB = await _context.Recovery.DiagnoseAsync(
            [new SourceRecoveryTarget(sourceB, IsFolder: false)], "SOURCE_REGISTRY_UNAVAILABLE", hostSideMintFailure: true, cancellationToken: token);
        Assert.Equal(SourceRecoveryAction.ReauthorizeSource, diagnosisB.Action);
        var resultB = await _context.Recovery.ReauthorizeAsync([new SourceRecoveryTarget(sourceB, IsFolder: false)], token);
        Assert.True(resultB.Ok, resultB.ErrorCode + " " + resultB.Message);
        var activeB = _context.Registry.List()
            .Single(entry => entry.RevokedAt is null && IsSameRoot(entry, sourceB));

        var planB2 = await _context.Imports.PlanAsync(
            chapterB, [new ReferenceImportSource(sourceB, IsFolder: false)], "skip", token);
        Assert.NotNull(planB2);
        var startB2 = await _context.Imports.StartAsync(planB2!, password: null, token);
        Assert.True(startB2.Ok, startB2.ErrorCode + " " + startB2.Message);
        var receiptB2 = await _context.AwaitTerminalAsync(startB2.OperationId!);
        Assert.Equal(SourceImportOperationState.Completed, receiptB2.State);
        // Same physical source, all pages already referenced → whole-source skip (D-2 refresh path).
        Assert.Equal("skipped", receiptB2.Items.Single().Outcome);

        var locationAfter = _context.QueryLocationRows(baselineB.SourceId).Single();
        Assert.Equal(locationBefore.LocationId, locationAfter.LocationId); // SAME row: in place
        Assert.Equal(activeB.RegistryId, locationAfter.RegistryId);       // new authorization baseline
        Assert.Equal(1, locationAfter.Generation);
        Assert.False(string.IsNullOrEmpty(locationAfter.LastVerifiedAt));
        var targetsB2 = await _context.ListScanTargetsAsync(token);
        var followedB = targetsB2.Single(target => target.SourceId == baselineB.SourceId);
        Assert.Equal(activeB.RegistryId, followedB.RegistryId);
        Assert.Equal(1, followedB.Generation);

        // =========================================================== AC-LSB-7 sanitization
        var recoveryTexts = new[]
        {
            SourceRecoveryText.ReauthorizeOffer(diagnosisA.SourceLeafName, diagnosisA.StaleEntryCount),
            SourceRecoveryText.ReauthorizeOffer(diagnosisB.SourceLeafName, diagnosisB.StaleEntryCount),
            resultA.Message, resultB.Message,
        };
        foreach (var text in recoveryTexts)
        {
            Assert.DoesNotContain(sourceA, text);
            Assert.DoesNotContain(sourceB, text);
            Assert.DoesNotContain("quarantine", text, StringComparison.OrdinalIgnoreCase);
        }

        var hostFrames = _context.HostFrames.Select(frame => frame.Name).Distinct().ToArray();
        Assert.All(hostFrames, name => Assert.Contains(name, new[]
        {
            "source_list_roots", "source_register_root", "source_revoke_root", "source_reset_registry",
            "plan_import_references", "start_import_references", "get_import_receipt", "cancel_import",
        }));
        Assert.DoesNotContain("source_reset_registry", hostFrames); // recovery never resets by itself

        var wireLines = _context.Client.Wire.Frames.Select(frame => frame.RequestLine).ToArray();
        Assert.All(wireLines, line => Assert.DoesNotContain("quarantine", line, StringComparison.OrdinalIgnoreCase));
        // r1 P2-02: the Core wire log REDACTs absolute paths before storing a frame, so "path-bearing
        // frame" is unobservable by construction. What IS observable and is exactly the AC-LSB-7
        // requirement: ZERO fixture-root hits in the stored wire, while `[REDACTED]` frames prove the
        // redaction actually ran (i.e. absolute paths did reach the framer and were replaced).
        var escapedA = sourceA.Replace("\\", "\\\\", StringComparison.Ordinal);
        var escapedB = sourceB.Replace("\\", "\\\\", StringComparison.Ordinal);
        var wirePathHits = wireLines.Count(line =>
            line.Contains(escapedA, StringComparison.OrdinalIgnoreCase) ||
            line.Contains(escapedB, StringComparison.OrdinalIgnoreCase) ||
            line.Contains(sourceA, StringComparison.OrdinalIgnoreCase) ||
            line.Contains(sourceB, StringComparison.OrdinalIgnoreCase));
        var redactedFrames = wireLines.Count(line => line.Contains("[REDACTED]", StringComparison.Ordinal));
        Assert.Equal(0, wirePathHits);
        Assert.True(redactedFrames > 0, "the wire log must prove path redaction actually ran");
        Assert.DoesNotContain("source_revoke_root", WireCommands(wireLines));
        Assert.DoesNotContain("source_register_root", WireCommands(wireLines));

        var stderr = await _context.StderrAsync();
        Assert.DoesNotContain(sourceA, stderr);
        Assert.DoesNotContain(sourceB, stderr);
        Assert.DoesNotContain("quarantine", stderr, StringComparison.OrdinalIgnoreCase);

        evidence["case"] = "FEA-11-L-S1-B AC-LSB-9 closed loop (real Core stdio)";
        evidence["phase_a"] = new JsonObject
        {
            ["typed_failure"] = failure.Code,
            ["registry_unchanged_after_failure"] = true,
            ["diagnosis_action"] = diagnosisA.Action.ToString(),
            ["stale_entries"] = diagnosisA.StaleEntryCount,
            ["revoked"] = resultA.RevokedCount,
            ["registered"] = resultA.RegisteredCount,
            ["old_entry_generation"] = revoked.Generation,
            ["new_entry_generation"] = activeA.Generation,
            ["reimport_state"] = receiptA2.State.ToString(),
            ["reimport_imported_pages"] = receiptA2.Totals.ImportedPages,
            ["scan_target_registry_id_matches_new_entry"] = followedA.RegistryId == activeA.RegistryId,
            ["scan_target_generation"] = followedA.Generation,
            ["physical_identity_changed_new_source"] = sourceAId != followedA.SourceId,
        };
        evidence["phase_b"] = new JsonObject
        {
            ["typed_failure"] = failureB.Code,
            ["diagnosis_action"] = diagnosisB.Action.ToString(),
            ["revoked"] = resultB.RevokedCount,
            ["registered"] = resultB.RegisteredCount,
            ["reimport_outcome"] = receiptB2.Items.Single().Outcome,
            ["location_row_in_place"] = locationBefore.LocationId == locationAfter.LocationId,
            ["location_registry_id_updated"] = locationAfter.RegistryId == activeB.RegistryId,
            ["location_last_verified_at_set"] = !string.IsNullOrEmpty(locationAfter.LastVerifiedAt),
            ["scan_target_generation"] = followedB.Generation,
        };
        evidence["host_local_frames"] = new JsonArray(hostFrames.Select(name => (JsonNode)JsonValue.Create(name)!).ToArray());
        evidence["wire_commands"] = new JsonArray(WireCommands(wireLines).Select(command => (JsonNode)JsonValue.Create(command)!).ToArray());
        evidence["wire_frame_count"] = wireLines.Length;
        evidence["sanitization"] = new JsonObject
        {
            ["recovery_texts_path_free"] = true,
            ["wire_quarantine_hits"] = 0,
            // r1 P2-02: paths are redacted by the wire log, so the verifiable claim is 0 stored hits
            // plus evidence that the redaction ran (>=1 `[REDACTED]` frame).
            ["wire_path_hits"] = wirePathHits,
            ["wire_redacted_frames"] = redactedFrames,
            ["stderr_path_hits"] = 0,
        };
        evidence["pass"] = true;

        var evidenceDirectory = Path.Combine(
            RecoveryIpcContext.Repository(), "verification", "FEA-11-L-S1-B-RECOVERY-REAUTH-1", "logs");
        Directory.CreateDirectory(evidenceDirectory);
        await File.WriteAllTextAsync(
            Path.Combine(evidenceDirectory, "ipc-closed-loop.json"),
            evidence.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
        await File.WriteAllTextAsync(
            Path.Combine(evidenceDirectory, "ipc-closed-loop.txt"),
            "FEA-11-L-S1-B-RECOVERY-REAUTH-1 AC-LSB-9 real Host/Core stdio closed loop\n"
            + "phase_a: " + failure.Code + " -> explicit reauthorize(revoked=" + resultA.RevokedCount
            + ",registered=" + resultA.RegisteredCount + ") -> reimport " + receiptA2.State
            + " -> scan target registry=" + (followedA.RegistryId == activeA.RegistryId) + " gen=" + followedA.Generation + "\n"
            + "phase_b: " + failureB.Code + " -> explicit reauthorize(revoked=" + resultB.RevokedCount
            + ",registered=" + resultB.RegisteredCount + ") -> reimport " + receiptB2.Items.Single().Outcome
            + " -> location row in place=" + (locationBefore.LocationId == locationAfter.LocationId)
            + ", registry=" + (locationAfter.RegistryId == activeB.RegistryId) + ", gen=" + locationAfter.Generation + "\n"
            + "host_local_frames=" + string.Join(",", hostFrames) + "\n"
            + "wire_frame_count=" + wireLines.Length + " wire_path_hits=" + wirePathHits
            + " wire_redacted_frames=" + redactedFrames + " wire_quarantine_hits=0 stderr_path_hits=0\nPASS\n");
    }

    // ------------------------------------------------------------------------------------ helpers

    private static byte[] OnePixelPng() => Convert.FromBase64String(OnePixelPngBase64);

    private static async Task WriteZipAsync(string path, params (string Name, byte[] Bytes)[] entries)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        await using var stream = File.Create(path);
        using var archive = new ZipArchive(stream, ZipArchiveMode.Create, leaveOpen: false);
        foreach (var (name, bytes) in entries)
        {
            var entry = archive.CreateEntry(name, CompressionLevel.NoCompression);
            await using var entryStream = entry.Open();
            await entryStream.WriteAsync(bytes);
        }
    }

    private static bool IsSameRoot(SourceAuthorization entry, string path) =>
        entry.Roots.Length == 1 &&
        string.Equals(
            entry.Roots[0].Root,
            Path.TrimEndingDirectorySeparator(Path.GetFullPath(path)),
            StringComparison.OrdinalIgnoreCase);

    private static string? WireCommand(string line)
    {
        try
        {
            using var document = JsonDocument.Parse(line);
            return document.RootElement.TryGetProperty("command", out var command) ? command.GetString() : null;
        }
        catch (JsonException)
        {
            return null;
        }
    }

    private static string[] WireCommands(IEnumerable<string> lines) => lines
        .Select(WireCommand)
        .Where(command => !string.IsNullOrWhiteSpace(command))
        .Select(command => command!)
        .Distinct(StringComparer.Ordinal)
        .OrderBy(command => command, StringComparer.Ordinal)
        .ToArray();

    /// <summary>A scan-target row projected from the real Core (no App-side computation).</summary>
    public sealed record ScanTargetRow(string SourceId, string RegistryId, int Generation);

    public sealed record LocationRow(
        string LocationId, string SourceId, string RegistryId, int Generation, string? LastVerifiedAt);

    public sealed class RecoveryIpcContext : IAsyncLifetime
    {
        private readonly List<(string Name, string Payload)> _hostFrames = new();

        public CoreServiceClient Client { get; private set; } = null!;

        public SourceAccessRegistry Registry { get; private set; } = null!;

        public SourceReadCoordinator Sources { get; private set; } = null!;

        public SourceImportCoordinator Imports { get; private set; } = null!;

        public SourceRecoveryCoordinator Recovery { get; private set; } = null!;

        public string Root { get; private set; } = null!;

        public string DataRoot { get; private set; } = null!;

        private string Python { get; set; } = "python";

        public async Task InitializeAsync()
        {
            // r1 P3-10: xUnit constructs the class fixture even for skipped tests; without the gate
            // every full-suite run would still spawn a real Core. Stay inert when opt-in is off.
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                return;
            }

            var repository = Repository();
            Python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? NewManga.Host.Tests.LocalPython.Path;
            Root = Directory.CreateDirectory(Path.Combine(
                    repository + ".workspace", "FEA-11-L-S1-B-RECOVERY-REAUTH-1", "fixtures",
                    "ipc-" + Guid.NewGuid().ToString("N")))
                .FullName;
            DataRoot = Path.Combine(Root, "data");
            Directory.CreateDirectory(Path.Combine(DataRoot, "catalog"));

            var options = new CoreServiceOptions
            {
                ExecutablePath = Python,
                AdditionalArguments =
                [
                    "-X", "utf8", "-c",
                    $"import sys;sys.path.insert(0, r'{Path.Combine(repository, "src")}');"
                    + "import bootstrap.core_service as m;raise SystemExit(m.main())",
                ],
                DataRoot = DataRoot,
                DerivedRoot = Path.Combine(DataRoot, "derived"),
                CatalogDbPath = Path.Combine(DataRoot, "library.db"),
                StderrLogPath = Path.Combine(Root, "core.stderr.log"),
                WireLogPath = Path.Combine(Root, "wire.ndjson"),
                StartupTimeout = TimeSpan.FromSeconds(90),
                RequestTimeout = TimeSpan.FromSeconds(90),
            };

            Client = await CoreServiceClient.StartAsync(options);
            await Client.OpenHostSessionAsync();
            var ping = await Client.PingAsync();
            Assert.True(ping.Ready, "core must be ready");
            Assert.Contains("source.read/1", ping.Capabilities);

            // The Host registry is test-local; the Passthrough protector exists ONLY so the fixture
            // can craft the "registered root identity no longer matches the file" invariant of
            // phase B (DPAPI is invisible to the Core and to the App).
            Registry = new SourceAccessRegistry(Path.Combine(Root, "host-data"), new PassthroughProtector());
            Sources = new SourceReadCoordinator(Client, Registry, () => true);
            // HostRuntime.HostLocalAsync routes names onto the coordinator; replicate that exact
            // production routing (the runtime itself needs the real sidecars).
            HostCommandDispatcher dispatcher = new(
                Client,
                bridge: null,
                hostLocal: async (name, payload, token) =>
                {
                    _hostFrames.Add((name, payload.ValueKind == JsonValueKind.Object ? payload.GetRawText() : "{}"));
                    return new HostCommandResult(
                        name,
                        HostCommandStatus.Implemented,
                        HostCommandChannel.HostLocal,
                        await Sources.InvokeAsync(name, payload, token));
                });
            Imports = new SourceImportCoordinator(dispatcher, Sources, Root);
            Recovery = new SourceRecoveryCoordinator(dispatcher);
        }

        public async Task DisposeAsync()
        {
            if (Client is null)
            {
                return; // gate off: InitializeAsync never started the fixture
            }

            if (Imports is not null)
            {
                await Imports.DisposeAsync();
            }

            if (Client is not null)
            {
                await Client.DisposeAsync();
            }
        }

        public void ResetHostFrames() => _hostFrames.Clear();

        public List<string> HostFrameNames() => _hostFrames.Select(frame => frame.Name).ToList();

        public IReadOnlyList<(string Name, string Payload)> HostFrames => _hostFrames;

        public SourceAuthorization ActiveEntryFor(string path) =>
            Registry.List().Single(entry => entry.RevokedAt is null && IsSameRoot(entry, path));

        public async Task<(string BookId, string ChapterId)> CreateChapterAsync(string title)
        {
            var book = await Client.CreateBookAsync("FEA-11-L-S1-B " + title);
            var chapter = await Client.SendAsync(
                "CreateChapter",
                8,
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

        public async Task<SourceImportReceipt> AwaitTerminalAsync(string operationId)
        {
            var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(60);
            while (DateTime.UtcNow < deadline)
            {
                var receipt = await Imports.GetReceiptAsync(operationId, CancellationToken.None);
                if (receipt is { IsTerminal: true })
                {
                    return receipt;
                }

                await Task.Delay(100);
            }

            throw new TimeoutException("import did not reach a terminal state");
        }

        public async Task<IReadOnlyList<ScanTargetRow>> ListScanTargetsAsync(CancellationToken token)
        {
            var result = await Client.ListSourceScanTargetsAsync(token);
            var targets = result.GetProperty("targets");
            return targets.EnumerateArray()
                .Select(target => new ScanTargetRow(
                    target.GetProperty("source_id").GetString()!,
                    target.GetProperty("registry_id").GetString()!,
                    target.GetProperty("generation").GetInt32()))
                .ToArray();
        }

        /// <summary>Reads the Core's CURRENT location row straight from the isolated fixture DB.</summary>
        public IReadOnlyList<LocationRow> QueryLocationRows(string sourceId)
        {
            var rows = RunPython(
                "import sqlite3,sys,json\n"
                + "connection = sqlite3.connect(sys.argv[1])\n"
                + "cursor = connection.execute('SELECT location_id, source_id, registry_id, authorization_generation, last_verified_at FROM source_locations WHERE source_id = ? AND is_current = 1', (sys.argv[2],))\n"
                + "columns = [column[0] for column in cursor.description]\n"
                + "print(json.dumps([dict(zip(columns, row)) for row in cursor.fetchall()]))\n",
                Path.Combine(DataRoot, "library.db"),
                sourceId);
            using var document = JsonDocument.Parse(rows);
            return document.RootElement.EnumerateArray()
                .Select(row => new LocationRow(
                    row.GetProperty("location_id").GetString()!,
                    row.GetProperty("source_id").GetString()!,
                    row.GetProperty("registry_id").GetString()!,
                    row.GetProperty("authorization_generation").GetInt32(),
                    row.GetProperty("last_verified_at").GetString()))
                .ToArray();
        }

        /// <summary>
        /// Rewrites one registry entry's recorded physical identity (Passthrough protector only), so
        /// the registered root no longer matches the file at that path while the file itself is
        /// untouched. Equivalent to the invariant a same-path replacement produces.
        /// </summary>
        public void CraftRootIdentity(string registryId)
        {
            var path = Registry.RegistryPath;
            var bytes = File.ReadAllBytes(path);
            // Magic "NMSAR1\0" is 7 bytes; then a uint32 plaintext length; then the JSON payload.
            const int magicLength = 7;
            Assert.Equal("NMSAR1\0", Encoding.ASCII.GetString(bytes, 0, magicLength));
            var length = BitConverter.ToUInt32(bytes, magicLength);
            Assert.Equal((uint)(bytes.Length - magicLength - 4), length);
            var node = JsonNode.Parse(Encoding.UTF8.GetString(
                bytes, magicLength + 4, bytes.Length - magicLength - 4))!;
            var entry = node["entries"]!.AsArray()
                .Single(candidate => candidate!["registry_id"]!.GetValue<string>() == registryId)!;
            var root = entry["roots"]!.AsArray()[0]!;
            root["volume_serial"] = JsonValue.Create(root["volume_serial"]!.GetValue<ulong>() + 7);
            root["file_id"] = JsonValue.Create(root["file_id"]!.GetValue<ulong>() + 11);
            var plaintext = Encoding.UTF8.GetBytes(node.ToJsonString());
            var framed = new byte[magicLength + 4 + plaintext.Length];
            Encoding.ASCII.GetBytes("NMSAR1\0").CopyTo(framed, 0);
            BitConverter.TryWriteBytes(framed.AsSpan(magicLength, 4), (uint)plaintext.Length);
            plaintext.CopyTo(framed, magicLength + 4);
            File.WriteAllBytes(path, framed);
        }

        public async Task<string> StderrAsync()
        {
            var path = Path.Combine(Root, "core.stderr.log");
            return File.Exists(path) ? await File.ReadAllTextAsync(path) : string.Empty;
        }

        private string RunPython(string code, params string[] arguments)
        {
            var startInfo = new ProcessStartInfo(Python)
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            startInfo.ArgumentList.Add("-c");
            startInfo.ArgumentList.Add(code);
            foreach (var argument in arguments)
            {
                startInfo.ArgumentList.Add(argument);
            }

            using var process = Process.Start(startInfo)!;
            var stdout = process.StandardOutput.ReadToEnd();
            var stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            Assert.True(process.ExitCode == 0, "fixture python query failed: " + stdout + stderr);
            return stdout.Trim();
        }

        public static string Repository()
        {
            var directory = new DirectoryInfo(AppContext.BaseDirectory);
            while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
            {
                directory = directory.Parent;
            }

            return directory?.FullName ?? throw new InvalidOperationException("repository not found");
        }

        private sealed class PassthroughProtector : ISecretProtector
        {
            public byte[] Protect(byte[] plaintext) => plaintext.ToArray();

            public byte[] Unprotect(byte[] ciphertext) => ciphertext.ToArray();
        }
    }

    private sealed class RecoveryIpcFactAttribute : FactAttribute
    {
        public RecoveryIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "set NEWMANGA_FEA11_IPC=1 for the real isolated Python Core recovery IPC closed loop";
            }
        }
    }
}

/// <summary>Resolves the interpreter the isolated IPC fixtures launch (same default as the FEA-11 suite).</summary>
internal static class LocalPython
{
    public static string Path => Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON")
        ?? "C:/Python314/python.exe";
}
