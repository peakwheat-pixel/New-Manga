using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.Host;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-RESIDUAL-4A AC-R3-2 (AC11-9): the PRODUCTION Host chain over the real
/// stdio Core.
///
/// Opt-in only (<c>NEWMANGA_FEA11_IPC=1</c>) because it starts the real Python
/// Core against an isolated workspace data root. The launcher technique is the
/// Fea09 one (there is no <c>Fea11ProductionFixture</c> in this repository):
/// a tiny csc-compiled stdio launcher plus a Python prelude that runs the
/// CURRENT checkout's <c>src</c>, so the stale bundled sidecar is never used.
///
/// Unlike <see cref="Fea11SourceIpcTests"/> (which talks to
/// <see cref="CoreServiceClient"/> directly), this chain goes through
/// <see cref="HostRuntime.Commands"/> — the production
/// <see cref="HostCommandDispatcher"/> and the Host-owned durable journal /
/// authorization orchestrator:
///
/// scan → plan → preview → confirm → apply (Host-signed) → read gate → ACK →
/// resolve (new v2 key + new bytes), with the old published digest and the
/// source files proven unchanged.
/// </summary>
public sealed class Fea11Residual4AIpcTests
{
    [Fea11Residual4AIpcFact]
    public async Task ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved()
    {
        await using var fixture = await ProductionHostFixture.CreateAsync();
        var runtime = fixture.Runtime;
        var root = fixture.Root;
        var seed = fixture.Seed;
        var sourceId = seed.GetProperty("source_id").GetString()!;
        var newZip = seed.GetProperty("new_zip").GetString()!;
        var oldPageDigest = seed.GetProperty("old_page_digest").GetString()!;
        var evidence = new List<string>();

        // Source conservation baseline: bytes + size + mtime of every source
        // container, plus the zip file SET (the app may create derived data).
        var sourceBefore = SourceSnapshot(root);

        // (1) Sync-before state: the seeded legacy binding's already-published
        // digest is recorded from the DB. The read face refuses typed because a
        // seeded binding has no import-time grant mapping (C-16 R1-I002) —
        // recorded honestly as fail-closed, never faked as a read.
        var stateBefore = await fixture.InspectAsync();
        var oldBinding = BindingsOf(stateBefore, "p1").Single();
        Assert.Equal("healthy", oldBinding.GetProperty("status").GetString());
        Assert.Equal(oldPageDigest, oldBinding.GetProperty("verified_digest").GetString());
        var preResolve = await Assert.ThrowsAsync<CoreOperationException>(
            () => ResolveAsync(runtime));
        Assert.Equal("SOURCE_ACCESS_DENIED", preResolve.Code);
        evidence.Add("pre_sync_resolve=" + preResolve.Code);
        // (2) A Host-issued grant over the NEW container through the production
        // coordinator; the production dispatcher then drives every step it can.
        var registered = runtime.Registry!.Register("fea11-r4a", [root]);
        var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["decoder"] = "zip",
            ["scale"] = 1.0,
            ["params_digest"] = new string('a', 64),
        });
        var grantId = await runtime.Sources!.IssueAsync(
            registered.RegistryId, registered.Generation, newZip, "zip",
            sourceId, sourceId + "-candidate", rendition);

        var scanArgs = new Dictionary<string, object?>
        {
            ["source_id"] = sourceId,
            ["project_ids"] = new[] { "b1" },
            ["scope"] = "current",
            ["kind"] = "resync",
            ["grant_ids"] = new[] { grantId },
            ["missing"] = Array.Empty<object>(),
        };
        // The FULL production dispatcher path (FEA-11-RESIDUAL-4A D-1 fix):
        // no direct-client fallback any more.
        var scan = await InvokeAsync(runtime, "source_scan_sync", scanArgs);
        evidence.Add("scan_via=dispatcher");
        // Wire-level proof (D-1): the dispatcher wrote the scan payload as
        // FIELDS into the host-control envelope (the Core answered a valid frame).
        var scanWire = await LastHostControlPayloadAsync(runtime, "ScanSourceSync");
        Assert.Equal(sourceId, scanWire.GetProperty("source_id").GetString());
        Assert.Equal("current", scanWire.GetProperty("scope").GetString());
        Assert.Equal(grantId, scanWire.GetProperty("grant_ids")[0].GetString());
        var scanPath = Path.Combine(root, "scan.json");
        await File.WriteAllTextAsync(scanPath, scan.GetRawText());
        evidence.Add("scan_changed=" + scan.GetProperty("totals").GetProperty("changed").GetInt32());

        var bodyPath = Path.Combine(root, "plan-body.json");
        await RunPythonAsync(fixture.Python, fixture.Repo,
            Path.Combine(fixture.Repo, "verification", "FEA-11-RESIDUAL-4A",
                "tools", "build_plan_body.py"),
            "--scan-json", scanPath, "--out", bodyPath);
        using var bodyDocument = JsonDocument.Parse(
            await File.ReadAllTextAsync(bodyPath));
        var body = bodyDocument.RootElement;
        var planId = body.GetProperty("plan_id").GetString()!;
        await InvokeAsync(runtime, "source_plan_sync", body.GetProperty("plan_body"));
        var preview = await InvokeAsync(runtime, "source_preview_sync_plan",
            new Dictionary<string, object?>
            {
                ["plan_id"] = planId,
                ["plan_digest"] = body.GetProperty("plan_digest").GetString(),
            });
        var planDigest = preview.GetProperty("plan_digest").GetString()!;
        await InvokeAsync(runtime, "source_confirm_sync_plan",
            new Dictionary<string, object?>
            {
                ["plan_id"] = planId,
                ["plan_digest"] = planDigest,
                ["confirmation"] = body.GetProperty("confirmation"),
            });
        evidence.Add("plan_confirmed=1");

        // (3) Apply through the production journal branch of the SAME
        // dispatcher (FEA-11-RESIDUAL-4A D-1 fix: the Host-signed payload is
        // flattened into the host-control envelope; the caller never supplies
        // operation/authorization).
        var applyArgs = new Dictionary<string, object?>
        {
            ["plan_id"] = planId,
            ["plan_digest"] = planDigest,
            ["grant_ids"] = new[] { grantId },
            ["authorization"] = new Dictionary<string, object?>
            {
                ["authorizations"] = scan.GetProperty("authorizations").Clone(),
            },
        };
        var applied = await InvokeAsync(runtime, "source_resync", applyArgs);
        var operationId = applied.GetProperty("operation_id").GetString()!;
        evidence.Add("apply_via=dispatcher");
        // Wire-level proof (D-1): the journal branch flattened the Host-signed
        // payload (plan/operation/authorization) into the host-control envelope.
        var applyWire = await LastHostControlPayloadAsync(runtime, "ResyncSource");
        Assert.Equal(planId, applyWire.GetProperty("plan_id").GetString());
        Assert.Equal(operationId,
            applyWire.GetProperty("operation_id").GetString());
        Assert.Equal(JsonValueKind.Object,
            applyWire.GetProperty("authorization").ValueKind);
        Assert.False(await WireHasInvalidJsonAsync(runtime),
            "the Core must not refuse any dispatcher frame as INVALID_JSON");
        Assert.NotNull(runtime.Operations!.Get(operationId));
        Assert.Equal("core-committed", runtime.Operations!.Get(operationId)!.State);
        evidence.Add("apply=core-committed");

        // (4) Pending publication gate: the new binding is not readable yet.
        var pending = await Assert.ThrowsAsync<CoreOperationException>(
            () => ResolveAsync(runtime));
        Assert.Equal("SOURCE_ACCESS_DENIED", pending.Code);
        evidence.Add("pending_gate=" + pending.Code);

        // (5) ACK through the production dispatcher -> Host durable ACK.
        var acked = await InvokeAsync(runtime, "source_acknowledge_operation",
            new Dictionary<string, object?> { ["operation_id"] = operationId });
        Assert.Equal("acknowledged", acked.GetProperty("State").GetString());
        Assert.Equal("acknowledged", runtime.Operations!.Get(operationId)!.State);
        evidence.Add("ack=acknowledged");

        // (6) The page now resolves through a DIFFERENT v2 key and serves the
        // NEW content (blue), not the old one (red).
        var resource = (await InvokeAsync(runtime, "resolve_page_resource",
            new Dictionary<string, object?> { ["page_id"] = "p1" }))
            .GetProperty("resource_id").GetString()!;
        Assert.StartsWith("page-rendition-v2-", resource);
        Assert.NotEqual("page-rendition-p1", resource);
        var newBytes = await runtime.ReadPageImageAsync("p1");
        Assert.Equal(new byte[] { 0x89, 0x50, 0x4E, 0x47 },
            newBytes.Take(4).ToArray());
        var servedPath = Path.Combine(root, "p1-after.png");
        await File.WriteAllBytesAsync(servedPath, newBytes);
        var probe = await fixture.ProbePngAsync(servedPath);
        Assert.Equal(4, probe.GetProperty("width").GetInt32());
        Assert.Equal(3, probe.GetProperty("height").GetInt32());
        Assert.Equal(
            new[] { 0, 0, 255 },
            probe.GetProperty("pixel").EnumerateArray()
                .Select(value => value.GetInt32()).ToArray());
        evidence.Add("new_resource=" + resource);

        // (7) The OLD digest is immutable: the old binding keeps its
        // verified_digest (now superseded) and the old entry digest is
        // unchanged; the legacy page key was never (re)published.
        var stateAfter = await fixture.InspectAsync();
        var oldBindingId = oldBinding.GetProperty("binding_id").GetString()!;
        var oldBindingAfter = BindingsOf(stateAfter, "p1")
            .Single(row => row.GetProperty("binding_id").GetString() == oldBindingId);
        Assert.Equal(oldBinding.GetProperty("verified_digest").GetString(),
            oldBindingAfter.GetProperty("verified_digest").GetString());
        Assert.Equal("superseded", oldBindingAfter.GetProperty("status").GetString());
        foreach (var entry in stateBefore.GetProperty("old_entries").EnumerateArray())
        {
            var entryId = entry.GetProperty("entry_id").GetString()!;
            var after = stateAfter.GetProperty("old_entries").EnumerateArray()
                .Single(row => row.GetProperty("entry_id").GetString() == entryId);
            Assert.Equal(entry.GetProperty("content_digest").GetString(),
                after.GetProperty("content_digest").GetString());
        }
        var renditions = stateAfter.GetProperty("renditions").EnumerateArray().ToList();
        Assert.DoesNotContain(renditions,
            row => row.GetProperty("cache_key").GetString() == "page-rendition-p1");
        // The served rendition is recorded in the derived catalog with exactly
        // the bytes ReadPageImageAsync returned (the v2 key is the catalog key;
        // the rendition-cache row key is the cache identity).
        Assert.Contains(renditions, row => row.GetProperty("content_digest").GetString()
            == probe.GetProperty("sha256").GetString());
        evidence.Add("old_digest_immutable=1");

        // (8) The source files are untouched (hash/size/mtime + zip set).
        Assert.Equal(sourceBefore, SourceSnapshot(root));
        evidence.Add("source_conserved=1");

        // (9) A revoked Host registry fails closed for the next Host-issued
        // grant (the Grant registry is the only authorization source).
        runtime.Registry!.Revoke(registered.RegistryId);
        var revoked = await Assert.ThrowsAsync<SourceAccessException>(() =>
            runtime.Sources!.IssueAsync(registered.RegistryId,
                registered.Generation, newZip, "zip", sourceId,
                sourceId + "-candidate", rendition));
        Assert.Contains(revoked.Code, new[]
        {
            "SOURCE_ACCESS_DENIED", "SOURCE_REGISTRY_UNAVAILABLE",
            "SOURCE_GRANT_REVOKED",
        });
        evidence.Add("revoked_registry=" + revoked.Code);

        await File.WriteAllTextAsync(Path.Combine(root, "real-ipc.txt"),
            "DataRoot=" + root + "\n" + string.Join("\n", evidence) + "\nPASS\n");
    }

    [Fea11Residual4AIpcFact]
    public async Task ProductionDispatcherMissingCapabilityFailsClosed()
    {
        await using var fixture = await ProductionHostFixture.CreateAsync();
        var runtime = fixture.Runtime;
        var root = fixture.Root;
        var seed = fixture.Seed;
        var sourceId = seed.GetProperty("source_id").GetString()!;
        var newZip = seed.GetProperty("new_zip").GetString()!;
        var registered = runtime.Registry!.Register("fea11-r4a-capability", [root]);
        var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["decoder"] = "zip",
            ["scale"] = 1.0,
            ["params_digest"] = new string('a', 64),
        });
        var grantId = await runtime.Sources!.IssueAsync(
            registered.RegistryId, registered.Generation, newZip, "zip",
            sourceId, sourceId + "-candidate", rendition);

        // The production dispatcher probes capabilities BEFORE dispatch. A Host
        // gate that reports a missing source.sync.scan/1 must refuse typed with
        // ZERO wire frames (the command itself is never dispatched unprobed).
        var framesBefore = runtime.CoreService!.Wire.Count;
        var gated = new HostCommandDispatcher(
            runtime.CoreService,
            bridge: null,
            hostLocal: null,
            journal: null,
            operationJournal: null,
            capabilityGate: (name, _) => Task.FromException(new CoreOperationException(
                "CORE_CAPABILITY_MISSING", "protocol", false,
                "the Core does not advertise source.sync.scan/1", null)));
        var refused = await Assert.ThrowsAsync<CoreOperationException>(async () =>
        {
            await gated.InvokeAsync("source_scan_sync",
                JsonSerializer.SerializeToElement(new Dictionary<string, object?>
                {
                    ["source_id"] = sourceId,
                    ["project_ids"] = new[] { "b1" },
                    ["scope"] = "current",
                    ["kind"] = "resync",
                    ["grant_ids"] = new[] { grantId },
                    ["missing"] = Array.Empty<object>(),
                }), CancellationToken.None);
        });
        Assert.Equal("CORE_CAPABILITY_MISSING", refused.Code);
        Assert.Equal(framesBefore, runtime.CoreService.Wire.Count);
        await File.WriteAllTextAsync(Path.Combine(root, "real-ipc.txt"),
            "DataRoot=" + root + "\nscan_without_capability=" + refused.Code
            + "\nzero_wire_frames=1\nPASS\n");
    }

    /// <summary>
    /// FEA-11-RESIDUAL-4A D-1 discrimination: one host-control command through
    /// the PRODUCTION dispatcher must reach the real Core as a VALID frame whose
    /// <c>payload</c> carries FLAT fields.
    ///
    /// Before the fix the dispatcher wrote a second complete payload object into
    /// the already-opened envelope, so the Core answered <c>INVALID_JSON</c> and
    /// no host-control command ever completed through the dispatcher.
    /// Mutation self-check: restoring the nested writer turns this test RED.
    /// </summary>
    [Fea11Residual4AIpcFact]
    public async Task ProductionDispatcherHostControlPayloadIsFlattened()
    {
        await using var fixture = await ProductionHostFixture.CreateAsync();
        var runtime = fixture.Runtime;
        var root = fixture.Root;
        var seed = fixture.Seed;
        var sourceId = seed.GetProperty("source_id").GetString()!;
        var newZip = seed.GetProperty("new_zip").GetString()!;
        var registered = runtime.Registry!.Register("fea11-r4a-wire", [root]);
        var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["decoder"] = "zip",
            ["scale"] = 1.0,
            ["params_digest"] = new string('a', 64),
        });
        var grantId = await runtime.Sources!.IssueAsync(
            registered.RegistryId, registered.Generation, newZip, "zip",
            sourceId, sourceId + "-candidate", rendition);

        var scan = await InvokeAsync(runtime, "source_scan_sync",
            new Dictionary<string, object?>
            {
                ["source_id"] = sourceId,
                ["project_ids"] = new[] { "b1" },
                ["scope"] = "current",
                ["kind"] = "resync",
                ["grant_ids"] = new[] { grantId },
                ["missing"] = Array.Empty<object>(),
            });
        Assert.Equal(sourceId,
            scan.GetProperty("source").GetProperty("source_id").GetString());

        var payload = await LastHostControlPayloadAsync(runtime, "ScanSourceSync");
        // Flat, frozen ScanSourceSync request fields (C-17 §5.1).
        Assert.Equal(sourceId, payload.GetProperty("source_id").GetString());
        Assert.Equal("current", payload.GetProperty("scope").GetString());
        Assert.Equal("resync", payload.GetProperty("kind").GetString());
        Assert.Equal(grantId, payload.GetProperty("grant_ids")[0].GetString());
        Assert.Equal(JsonValueKind.Array, payload.GetProperty("missing").ValueKind);
        // No nested payload object anywhere (the pre-fix double-object shape).
        foreach (var property in payload.EnumerateObject())
        {
            Assert.False(
                property.Value.ValueKind == JsonValueKind.Object
                && property.Value.TryGetProperty("source_id", out _),
                "nested payload object detected under '" + property.Name + "'");
        }
        Assert.False(await WireHasInvalidJsonAsync(runtime),
            "the Core must not refuse any dispatcher frame as INVALID_JSON");

        await File.WriteAllTextAsync(Path.Combine(root, "real-ipc.txt"),
            "DataRoot=" + root + "\nhostcontrol_payload=flattened\n"
            + "invalid_json_frames=0\nPASS\n");
    }

    // ------------------------------------------------------------- helpers

    private static async Task<JsonElement> InvokeAsync(
        HostRuntime runtime, string name, object? args)
    {
        var element = args is null
            ? default
            : JsonSerializer.SerializeToElement(args);
        var result = await runtime.Commands!.InvokeAsync(
            name, element, CancellationToken.None);
        return result.Value.Clone();
    }

    /// <summary>
    /// FEA-11-RESIDUAL-4A D-1: read back the LAST host-control wire frame for
    /// one command from the Host's own wire evidence and return its
    /// <c>payload</c> object. This is the machine check that the dispatcher
    /// wrote the payload FIELDS into the envelope (flattened) instead of a
    /// second complete object (which the Core rejected as INVALID_JSON).
    /// </summary>
    private static async Task<JsonElement> LastHostControlPayloadAsync(
        HostRuntime runtime, string command)
    {
        var wirePath = Path.Combine(runtime.WireEvidenceDirectory,
            "core-service.ndjson");
        Assert.True(File.Exists(wirePath), "wire evidence missing: " + wirePath);
        JsonElement? found = null;
        foreach (var line in await File.ReadAllLinesAsync(wirePath))
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            using var row = JsonDocument.Parse(line);
            if (!row.RootElement.TryGetProperty("request", out var requestText)
                || requestText.ValueKind != JsonValueKind.String)
            {
                continue;
            }
            using var request = JsonDocument.Parse(requestText.GetString()!);
            var root = request.RootElement;
            if (root.ValueKind != JsonValueKind.Object
                || !root.TryGetProperty("command", out var commandText)
                || commandText.GetString() != command)
            {
                continue;
            }
            if (root.TryGetProperty("payload", out var payload)
                && payload.ValueKind == JsonValueKind.Object)
            {
                found = payload.Clone();
            }
        }
        Assert.True(found.HasValue, "no valid wire frame for " + command);
        return found!.Value;
    }

    /// <summary>True when the Host's own wire evidence contains an
    /// <c>INVALID_JSON</c> refusal from the Core (the pre-fix dispatcher shape).</summary>
    private static async Task<bool> WireHasInvalidJsonAsync(HostRuntime runtime)
    {
        var wirePath = Path.Combine(runtime.WireEvidenceDirectory,
            "core-service.ndjson");
        if (!File.Exists(wirePath)) return false;
        foreach (var line in await File.ReadAllLinesAsync(wirePath))
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            using var row = JsonDocument.Parse(line);
            if (!row.RootElement.TryGetProperty("response", out var responseText)
                || responseText.ValueKind != JsonValueKind.String)
            {
                continue;
            }
            using var response = JsonDocument.Parse(responseText.GetString()!);
            if (response.RootElement.TryGetProperty("error", out var error)
                && error.ValueKind == JsonValueKind.Object
                && error.TryGetProperty("code", out var code)
                && code.GetString() == "INVALID_JSON")
            {
                return true;
            }
        }
        return false;
    }

    private static async Task<JsonElement> ResolveAsync(HostRuntime runtime) =>
        await InvokeAsync(runtime, "resolve_page_resource",
            new Dictionary<string, object?> { ["page_id"] = "p1" });

    private static IEnumerable<JsonElement> BindingsOf(JsonElement state, string pageId) =>
        state.GetProperty("bindings").EnumerateArray()
            .Where(row => row.GetProperty("page_id").GetString() == pageId);

    private static string SourceSnapshot(string root) =>
        string.Join("\n", Directory.EnumerateFiles(root, "*.zip")
            .OrderBy(path => path, StringComparer.Ordinal)
            .Select(path =>
                Path.GetFileName(path) + "|" + Hash(path) + "|"
                + new FileInfo(path).Length + "|"
                + new FileInfo(path).LastWriteTimeUtc.ToString("O")));

    private static string Hash(string path) => Convert.ToHexString(
            SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();

    private static string RepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null
               && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        return directory?.FullName
            ?? throw new InvalidOperationException("repository not found");
    }

    private static async Task RunPythonAsync(
        string python, string cwd, string script, params string[] arguments)
    {
        var info = new ProcessStartInfo(python)
        {
            WorkingDirectory = cwd,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        info.ArgumentList.Add(script);
        foreach (var argument in arguments)
        {
            info.ArgumentList.Add(argument);
        }
        using var process = Process.Start(info)!;
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0, await stdout + await stderr);
    }

    private sealed class Fea11Residual4AIpcFactAttribute : FactAttribute
    {
        public Fea11Residual4AIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "reason: set NEWMANGA_FEA11_IPC=1 for the real isolated "
                    + "Python Core HostRuntime/dispatcher production chain "
                    + "(FEA-11-RESIDUAL-4A AC-R3-2 / AC11-9)";
            }
        }
    }

    /// <summary>
    /// One isolated real-Core production Host: seeded v8 library + the real
    /// <see cref="HostRuntime"/> over the launcher sidecars. Mirrors the Fea09
    /// fixture's launcher technique; nothing bundled is used or modified.
    /// </summary>
    private sealed class ProductionHostFixture : IAsyncDisposable
    {
        private ProductionHostFixture(
            string repo, string python, string root, HostRuntime runtime,
            JsonElement seed)
        {
            Repo = repo;
            Python = python;
            Root = root;
            Runtime = runtime;
            Seed = seed;
        }

        public string Repo { get; }
        public string Python { get; }
        public string Root { get; }
        public HostRuntime Runtime { get; }
        public JsonElement Seed { get; }

        public static async Task<ProductionHostFixture> CreateAsync()
        {
            var repo = RepositoryRoot();
            var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON")
                ?? "C:/Python314/python.exe";
            var root = Path.Combine(repo + ".workspace", "FEA-11", "fixtures",
                "r4a-production-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            await RunPythonAsync(python, repo, "tests/fea11/support/ipc_seed.py",
                "--data-root", root, "--db", Path.Combine(root, "library.db"));
            using var seedDocument = JsonDocument.Parse(
                await File.ReadAllTextAsync(
                    Path.Combine(root, "ipc-seed-receipt.json")));
            var seed = seedDocument.RootElement.Clone();
            Assert.Equal(9, seed.GetProperty("schema_version").GetInt32());

            var sidecars = Directory.CreateDirectory(
                Path.Combine(root, "sidecars")).FullName;
            await WriteSidecarsAsync(repo, python, sidecars);

            var runtime = await HostRuntime.StartAsync(new HostOptions
            {
                DataRoot = root,
                LogDirectory = Path.Combine(root, "logs"),
                SidecarDirectoryOverride = sidecars,
                MutexName = @"Local\NewManga.Host.Test.R4A."
                    + Guid.NewGuid().ToString("N")[..12],
                DetectLegacyShell = false,
                ParityReached = true,
                FirstRunBackupEnabled = false,
                EnableWireEvidence = true,
                SourceScanEnabled = false,
                SourceWatchEnabled = false,
                RunGrantRenewalEnabled = false,
                StartupTimeout = TimeSpan.FromSeconds(90),
                RequestTimeout = TimeSpan.FromSeconds(90),
            });
            Assert.NotNull(runtime.Commands);
            Assert.NotNull(runtime.CoreService);
            Assert.NotNull(runtime.Registry);
            Assert.NotNull(runtime.Sources);
            Assert.NotNull(runtime.Operations);
            return new ProductionHostFixture(repo, python, root, runtime, seed);
        }

        public Task<JsonElement> InspectAsync() => InspectStateAsync();

        private async Task<JsonElement> InspectStateAsync()
        {
            var outputPath = Path.Combine(Root,
                "state-" + Guid.NewGuid().ToString("N")[..8] + ".json");
            await RunPythonAsync(Python, Repo,
                Path.Combine(Repo, "verification", "FEA-11-RESIDUAL-4A",
                    "tools", "inspect_state.py"),
                "--db", Path.Combine(Root, "library.db"),
                "--out", outputPath);
            using var document = JsonDocument.Parse(
                await File.ReadAllTextAsync(outputPath));
            return document.RootElement.Clone();
        }

        public async Task<JsonElement> ProbePngAsync(string path)
        {
            var info = new ProcessStartInfo(Python)
            {
                WorkingDirectory = Repo,
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            info.ArgumentList.Add(Path.Combine(Repo, "verification",
                "FEA-11-RESIDUAL-4A", "tools", "probe_png.py"));
            info.ArgumentList.Add("--path");
            info.ArgumentList.Add(path);
            using var process = Process.Start(info)!;
            var stdout = await process.StandardOutput.ReadToEndAsync();
            var stderr = await process.StandardError.ReadToEndAsync();
            await process.WaitForExitAsync();
            Assert.True(process.ExitCode == 0, stdout + stderr);
            var json = stdout.Trim().Split('\n').Last();
            Assert.StartsWith("FEA11_R4A_PNG_OK ", json);
            using var document = JsonDocument.Parse(
                json["FEA11_R4A_PNG_OK ".Length..]);
            return document.RootElement.Clone();
        }

        private static async Task WriteSidecarsAsync(
            string repo, string python, string sidecars)
        {
            var launcherSource = Path.Combine(sidecars, "Launcher.cs");
            var launcher = """
using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
class Launcher {
    static int Main() {
        string script = Path.ChangeExtension(System.Reflection.Assembly.GetExecutingAssembly().Location, ".py");
        var info = new ProcessStartInfo(@"PYTHON", "-X utf8 \"" + script + "\"");
        info.UseShellExecute = false;
        info.CreateNoWindow = true;
        info.RedirectStandardInput = info.RedirectStandardOutput = info.RedirectStandardError = true;
        using (var child = Process.Start(info)) {
            var stdout = new Thread(() => { try { child.StandardOutput.BaseStream.CopyTo(Console.OpenStandardOutput()); Console.Out.Flush(); } catch (IOException) {} catch (ObjectDisposedException) {} });
            var stderr = new Thread(() => { try { child.StandardError.BaseStream.CopyTo(Console.OpenStandardError()); Console.Error.Flush(); } catch (IOException) {} catch (ObjectDisposedException) {} });
            stdout.IsBackground = true; stderr.IsBackground = true;
            stdout.Start(); stderr.Start();
            string line;
            while ((line = Console.ReadLine()) != null) {
                child.StandardInput.WriteLine(line);
                child.StandardInput.Flush();
            }
            try { child.StandardInput.Close(); } catch (IOException) {}
            child.WaitForExit();
            stdout.Join(2000); stderr.Join(2000);
            return child.ExitCode;
        }
    }
}
""".Replace("PYTHON", python.Replace("\"", "\"\""));
            await File.WriteAllTextAsync(launcherSource, launcher);
            var csc = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.Windows),
                "Microsoft.NET", "Framework64", "v4.0.30319", "csc.exe");
            var exe = Path.Combine(sidecars, "core_service.exe");
            RunProcess(csc, "/nologo", "/target:exe", "/out:" + exe, launcherSource);
            File.Copy(exe, Path.Combine(sidecars, "host_bridge.exe"));

            var prelude = "import sys; sys.path.insert(0, "
                + PythonString(Path.Combine(repo, "src")) + ")\n";
            await File.WriteAllTextAsync(
                Path.Combine(sidecars, "host_bridge.py"),
                prelude
                + "from infrastructure.resource_channel.host_bridge import main\n"
                + "raise SystemExit(main())\n");
            await File.WriteAllTextAsync(
                Path.Combine(sidecars, "core_service.py"),
                prelude
                + "import bootstrap.core_service as m\n"
                + "raise SystemExit(m.main())\n");
        }

        private static string PythonString(string value) =>
            "r'" + value.Replace("'", "\\'") + "'";

        private static void RunProcess(
            string executablePath, params string[] arguments)
        {
            var info = new ProcessStartInfo(executablePath)
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            foreach (var argument in arguments)
            {
                info.ArgumentList.Add(argument);
            }
            using var process = Process.Start(info)
                ?? throw new InvalidOperationException(
                    "failed to start " + executablePath);
            var stdout = process.StandardOutput.ReadToEnd();
            var stderr = process.StandardError.ReadToEnd();
            process.WaitForExit(60_000);
            Assert.True(process.ExitCode == 0, stdout + stderr);
        }

        public async ValueTask DisposeAsync()
        {
            await Runtime.DisposeAsync();
        }
    }
}
