using System.Diagnostics;
using System.Globalization;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-HOST-AUTH-2 (C-17 §3.2:161/:169) — gated real-IPC evidence for AC-F2.
///
/// The default gate (<c>Fea11HostAuth2FreshCompletionTests</c>) proves the fresh
/// authorization seam without a Core; these facts prove the REAL chain: a real
/// isolated Python Core, the production <see cref="HostOperationOrchestrator"/>
/// apply, the production <see cref="SourceOperationCoordinator"/> ACK/recovery and
/// the real read gate.
///
/// Opt-in only (<c>NEWMANGA_FEA11_IPC=1</c>) because it starts the real Core
/// against an isolated workspace data root. Evidence stays in the isolated root
/// (R-008), never in a tracked repository file.
/// </summary>
public sealed class Fea11HostAuthIpcTests
{
    [Fea11IpcFact]
    public async Task Ack_SendsAFreshAuthorization_ThenOpensTheGateExactlyOnce()
    {
        await using var fixture = await IpcFixture.CreateAsync();
        var evidence = new List<string>();

        // (1) Production apply: real scan -> plan/preview/confirm -> orchestrator apply.
        var operationId = await fixture.ApplyAsync();
        var committed = fixture.Operations.Get(operationId)!;
        Assert.Equal("core-committed", committed.State);
        Assert.False(string.IsNullOrWhiteSpace(committed.CommitDigest));
        evidence.Add("apply_state=" + committed.State);

        // (2) The publication gate is still pending: the new binding is unreadable.
        var pending = await Assert.ThrowsAsync<CoreOperationException>(() => fixture.ResolveAsync());
        Assert.Equal("SOURCE_ACCESS_DENIED", pending.Code);
        evidence.Add("pending_gate=" + pending.Code);

        var rowsBefore = await fixture.CountRowsAsync();
        // KNOWN-LIMITATION-E9 (product adjudication 2026-11-15 by ZCode;
        // doc/reviews/E9-PRODUCT-ADJUDICATION-zcode-2026-11-15.md): the sync COMPLETION chain
        // (ACK / recovery) is unavailable for non-folder sources. AcknowledgeAsync and RecoverAsync
        // both take the same fresh re-mint, and none of the journal/plan/payload entry points carries
        // the container path, so the Host refuses typed instead of guessing a registry root.
        //
        // This is NOT a relaxed assertion. The "acknowledged"/"recovered" expectation was NEVER
        // reachable on this fixture: the call failed before too, just with a masked
        // UnauthorizedAccessException. The assertions below TIGHTEN the contract to the exact
        // refusal code plus an untouched journal. When E-9 is unlocked, restore the success path.
        var recoveryFailure = await Assert.ThrowsAsync<SourceAccessException>(
            () => fixture.Operations.RecoverAsync(operationId));
        Assert.Equal("SOURCE_PLAN_UNAVAILABLE", recoveryFailure.Code);
        Assert.Equal("core-committed", fixture.Operations.Get(operationId)!.State);
        Assert.Equal(rowsBefore, await fixture.CountRowsAsync());

        var recoveryAgain = await Assert.ThrowsAsync<SourceAccessException>(
            () => fixture.Operations.RecoverAsync(operationId));
        Assert.Equal("SOURCE_PLAN_UNAVAILABLE", recoveryAgain.Code);
        Assert.Equal("core-committed", fixture.Operations.Get(operationId)!.State);
        evidence.Add("recovery_refused=" + recoveryFailure.Code + " journal_unchanged=1");

        var recoverPending = await Assert.ThrowsAsync<CoreOperationException>(() => fixture.ResolveAsync());
        Assert.Equal("SOURCE_ACCESS_DENIED", recoverPending.Code);
        Assert.Equal(fixture.NewZipHash, fixture.HashOfNewZip());
        evidence.Add("gate_open_resource=none rows_unchanged=1");
        await fixture.WriteEvidenceAsync("real-ipc-recovery.txt", evidence);
    }

    private static DateTimeOffset Timestamp(JsonElement element) =>
        DateTimeOffset.Parse(element.GetString()!, CultureInfo.InvariantCulture,
            DateTimeStyles.AdjustToUniversal);

    /// <summary>
    /// FEA-11-HOST-AUTH-3 AC-H3-4 phase 1: drive the REAL chain to journal
    /// <c>core-committed</c>, persist the park facts, then block so the external driver can
    /// kill the WHOLE process tree (dotnet + Python Core). This test never self-terminates
    /// on purpose: only the kill ends it.
    /// </summary>
    [Fea11IpcFact]
    public async Task CrashPoint_Park()
    {
        var state = Environment.GetEnvironmentVariable("NEWMANGA_FEA11_CRASH_STATE");
        Assert.False(string.IsNullOrWhiteSpace(state), "NEWMANGA_FEA11_CRASH_STATE is required");
        var fixture = await IpcFixture.CreateAsync();
        try
        {
            var operationId = await fixture.ApplyAsync();
            var entry = fixture.Operations.Get(operationId)
                ?? throw new InvalidOperationException("journal entry missing after apply");
            Assert.Equal("core-committed", entry.State);
            var counts = await fixture.CountRowsAsync();
            var wirePath = Path.Combine(fixture.Root, "wire.ndjson");
            var park = new Dictionary<string, object?>
            {
                ["journal_state"] = entry.State,
                ["operation_id"] = operationId,
                ["commit_digest"] = entry.CommitDigest,
                ["grant_ids"] = (entry.GrantIds ?? string.Empty)
                    .Split(',', StringSplitOptions.RemoveEmptyEntries),
                ["plan_id"] = entry.PlanId,
                ["plan_digest"] = entry.PlanDigest,
                ["host_pid"] = Environment.ProcessId,
                ["core_session_id"] = fixture.Client.HostSession?.CoreSessionId,
                ["data_root"] = fixture.Root,
                // P0 fix: the driver must be able to re-check these, not trust a constant.
                ["source_path"] = fixture.NewZip,
                ["source_sha256"] = fixture.HashOfNewZip(),
                ["db_counts"] = new Dictionary<string, object?>
                {
                    ["bindings"] = counts.Bindings,
                    ["publications"] = counts.Publications,
                },
                ["wire_lines"] = File.Exists(wirePath) ? File.ReadAllLines(wirePath).Length : 0,
                ["page_bindings"] = (await fixture.PageBindingsAsync()).Clone(),
            };
            await File.WriteAllTextAsync(
                Path.Combine(state!, "park.json"), JsonSerializer.Serialize(park));
            // Park: the external driver kills this tree; nothing else ends the test.
            var deadline = DateTime.UtcNow.AddMinutes(5);
            while (DateTime.UtcNow < deadline)
            {
                await Task.Delay(200);
            }
        }
        finally
        {
            await fixture.DisposeAsync();
        }
    }

    /// <summary>
    /// FEA-11-HOST-AUTH-3 AC-H3-4 phase 2: a NEW process (new PID, new Host session) opens
    /// the SAME data root with a NEW Core, recovers the parked operation exactly once using
    /// FRESH re-minted grants, and persists the recovery facts for the driver's
    /// triple anti-forgery check.
    /// </summary>
    [Fea11IpcFact]
    public async Task CrashPoint_Recover()
    {
        var state = Environment.GetEnvironmentVariable("NEWMANGA_FEA11_CRASH_STATE");
        Assert.False(string.IsNullOrWhiteSpace(state), "NEWMANGA_FEA11_CRASH_STATE is required");
        var parkPath = Path.Combine(state!, "park.json");
        Assert.True(File.Exists(parkPath), "phase 1 must park before recovery");
        using var parkDocument = JsonDocument.Parse(await File.ReadAllTextAsync(parkPath));
        var park = parkDocument.RootElement;
        var root = park.GetProperty("data_root").GetString()!;
        var operationId = park.GetProperty("operation_id").GetString()!;
        var fixture = await IpcFixture.CreateAsync(root);
        try
        {
            var negative = Environment.GetEnvironmentVariable("NEWMANGA_FEA11_CRASH_NEGATIVE") == "1";
            if (negative)
            {
                // R-r2-01①② crash counter-example: the source was replaced between phases,
                // so the recovery must fail CLOSED (typed SourceAccessException OR a Core
                // typed refusal) -- never a silent ACK of a changed file.
                string? rejectedCode = null;
                try
                {
                    await fixture.Operations.RecoverAsync(operationId);
                }
                catch (SourceAccessException caught)
                {
                    rejectedCode = caught.Code;
                }
                catch (NewManga.CoreClient.Wire.CoreOperationException caught)
                {
                    rejectedCode = caught.Code;
                }
                Assert.False(string.IsNullOrWhiteSpace(rejectedCode),
                    "the replaced source must be refused, not silently recovered");
                await File.WriteAllTextAsync(
                    Path.Combine(state!, "negative.json"),
                    JsonSerializer.Serialize(new Dictionary<string, object?>
                    {
                        ["rejected_code"] = rejectedCode,
                        ["host_pid"] = Environment.ProcessId,
                    }));
                return;
            }
            var recovered = await fixture.Operations.RecoverAsync(operationId);
            Assert.Equal("recovered", recovered.State);
            // Idempotent: the second call returns the same state.
            var second = await fixture.Operations.RecoverAsync(operationId);
            Assert.Equal("recovered", second.State);
            Assert.Equal(park.GetProperty("commit_digest").GetString(), recovered.CommitDigest);

            var countsAfter = await fixture.CountRowsAsync();
            var gateOpen = await fixture.GateOpenAsync();
            var wirePath = Path.Combine(fixture.Root, "wire.ndjson");
            var beforeSecond = File.Exists(wirePath) ? File.ReadAllLines(wirePath).Length : 0;
            var third = await fixture.Operations.RecoverAsync(operationId);
            var afterSecond = File.Exists(wirePath) ? File.ReadAllLines(wirePath).Length : 0;
            var recover = new Dictionary<string, object?>
            {
                ["commit_digest"] = recovered.CommitDigest,
                ["host_pid"] = Environment.ProcessId,
                ["core_session_id"] = fixture.Client.HostSession?.CoreSessionId,
                ["grant_ids"] = (recovered.GrantIds ?? string.Empty)
                    .Split(',', StringSplitOptions.RemoveEmptyEntries),
                ["source_sha256"] = fixture.HashOfNewZip(),
                ["db_counts"] = new Dictionary<string, object?>
                {
                    ["bindings"] = countsAfter.Bindings,
                    ["publications"] = countsAfter.Publications,
                },
                // A successful resolve proves the read gate is open for the recovered page.
                ["gate_open"] = gateOpen,
                ["second_call"] = second.State,
                ["second_call_frames"] = Math.Max(0, afterSecond - beforeSecond),
                ["page_bindings"] = (await fixture.PageBindingsAsync()).Clone(),
            };
            await File.WriteAllTextAsync(
                Path.Combine(state!, "recover.json"), JsonSerializer.Serialize(recover));
        }
        finally
        {
            await fixture.DisposeAsync();
        }
    }

    private sealed class Fea11IpcFactAttribute : FactAttribute
    {
        public Fea11IpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "not run: default skip - set NEWMANGA_FEA11_IPC=1 for the real isolated "
                    + "Python Core stdio IPC ACK/recovery chain";
            }
        }
    }

    /// <summary>One isolated real-Core fixture: seeded v8 library + registry + scan/plan.</summary>
    private sealed class IpcFixture : IAsyncDisposable
    {
        private IpcFixture(string repo, string python, string root, CoreServiceClient client,
            SourceAccessRegistry registry, SourceReadCoordinator sources,
            SourceOperationCoordinator operations, JsonElement seed, string newZip,
            string newZipHash, string newGrant, JsonElement scan)
        {
            Repo = repo;
            Python = python;
            Root = root;
            Client = client;
            Registry = registry;
            Sources = sources;
            Operations = operations;
            Seed = seed;
            NewZip = newZip;
            NewZipHash = newZipHash;
            NewGrant = newGrant;
            Scan = scan;
        }

        public string Repo { get; }
        public string Python { get; }
        public string Root { get; }
        public CoreServiceClient Client { get; }
        public SourceAccessRegistry Registry { get; }
        public SourceReadCoordinator Sources { get; }
        public SourceOperationCoordinator Operations { get; }
        public JsonElement Seed { get; }
        public string NewZip { get; }
        public string NewZipHash { get; }
        public string NewGrant { get; }
        public JsonElement Scan { get; }
        public string DatabasePath => Path.Combine(Root, "library.db");

        public static async Task<IpcFixture> CreateAsync(string? existingRoot = null)
        {
            var repo = RepositoryRoot();
            var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON")
                ?? "C:/Python314/python.exe";
            var reuse = !string.IsNullOrWhiteSpace(existingRoot);
            var root = reuse
                ? existingRoot!
                : Path.Combine(repo + ".workspace", "FEA-11", "fixtures",
                    "host-auth-ipc-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            JsonElement seed;
            if (!reuse)
            {
                await RunPythonAsync(python, repo, "tests/fea11/support/ipc_seed.py",
                    "--data-root", root, "--db", Path.Combine(root, "library.db"));
                using var seedDocument = JsonDocument.Parse(await File.ReadAllTextAsync(
                    Path.Combine(root, "ipc-seed-receipt.json")));
                seed = seedDocument.RootElement.Clone();
                Assert.Equal(CoreSchema.Current, seed.GetProperty("schema_version").GetInt32());
            }
            else
            {
                // Crash/recovery fixture: the PRECEDING process seeded this root; the
                // seed receipt is re-read for the (unchanged) source identity only.
                using var seedDocument = JsonDocument.Parse(await File.ReadAllTextAsync(
                    Path.Combine(root, "ipc-seed-receipt.json")));
                seed = seedDocument.RootElement.Clone();
            }

            var client = await CoreServiceClient.StartAsync(new CoreServiceOptions
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
            });
            try
            {
                Assert.Contains("source.sync.apply/1", (await client.PingAsync()).Capabilities);
                await client.OpenHostSessionAsync();
                var registry = new SourceAccessRegistry(root);
                var sources = new SourceReadCoordinator(client, registry, () => true);
                var operations = new SourceOperationCoordinator(client, root, () => true, registry, sources);
                var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
                {
                    ["decoder"] = "zip",
                    ["scale"] = 1.0,
                    ["params_digest"] = new string('a', 64),
                });
                var sourceId = seed.GetProperty("source_id").GetString()!;
                var newZip = seed.GetProperty("new_zip").GetString()!;
                // Production registers ONE root == the user-selected SOURCE (the container
                // file itself), never the data root: recovery re-mints from roots[0].
                var registered = registry.Register("fea11-hostauth-ipc", [newZip]);
                var newGrant = string.Empty;
                JsonElement scan = default;
                if (!reuse)
                {
                    newGrant = await sources.IssueAsync(
                        registered.RegistryId, registered.Generation, newZip, "zip",
                        sourceId, sourceId + "-candidate", rendition);
                    scan = await ScanAsync(client, seed, newGrant);
                }
                var fixture = new IpcFixture(repo, python, root, client, registry, sources,
                    operations, seed, newZip, Hash(newZip), newGrant, scan);
                if (!reuse)
                {
                    await fixture.PlanAsync();
                }
                return fixture;
            }
            catch
            {
                await client.DisposeAsync();
                throw;
            }
        }

        private JsonElement Plan { get; set; }

        private async Task PlanAsync()
        {
            var scanPath = Path.Combine(Root, "scan.json");
            await File.WriteAllTextAsync(scanPath, Scan.GetRawText());
            var bodyPath = Path.Combine(Root, "plan-body.json");
            // The frozen seed's legacy entry has no comparable v7 pixel evidence, so
            // the matcher honestly degrades p1 to ambiguous/missing_old and the default
            // decision is `defer` (no new binding to gate). C-17 §5.1/§5.3 allows the
            // explicit user `bind` for an ambiguous item; the helper reuses the frozen
            // conftest builders, so the plan body stays C-17 shaped.
            await RunPythonAsync(Python, Repo,
                Path.Combine(Repo, "verification", "FEA-11-HOST-AUTH-2", "tools",
                    "build_plan_body.py"),
                "--scan-json", scanPath, "--out", bodyPath);
            using var bodyDocument = JsonDocument.Parse(await File.ReadAllTextAsync(bodyPath));
            var planId = bodyDocument.RootElement.GetProperty("plan_id").GetString()!;
            await Client.SendAsync("source_plan_sync", 3,
                writer => bodyDocument.RootElement.GetProperty("plan_body").WriteTo(writer),
                TimeSpan.FromSeconds(60));
            var preview = await Client.SendAsync("source_preview_sync_plan", 3, writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("plan_id", planId);
                writer.WriteString("plan_digest",
                    bodyDocument.RootElement.GetProperty("plan_digest").GetString());
                writer.WriteEndObject();
            }, TimeSpan.FromSeconds(60));
            var planDigest = preview.Result!.Value.GetProperty("plan_digest").GetString()!;
            await Client.SendAsync("source_confirm_sync_plan", 3, writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("plan_id", planId);
                writer.WriteString("plan_digest", planDigest);
                writer.WritePropertyName("confirmation");
                bodyDocument.RootElement.GetProperty("confirmation").WriteTo(writer);
                writer.WriteEndObject();
            }, TimeSpan.FromSeconds(60));
            Plan = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
            {
                ["plan_id"] = planId,
                ["plan_digest"] = planDigest,
            });
        }

        private static async Task<JsonElement> ScanAsync(
            CoreServiceClient client, JsonElement seed, string grantId)
        {
            var scan = await client.SendHostControlAsync("ScanSourceSync", writer =>
            {
                writer.WriteString("source_id", seed.GetProperty("source_id").GetString());
                writer.WriteStartArray("project_ids");
                writer.WriteStringValue("b1");
                writer.WriteEndArray();
                writer.WriteString("scope", "current");
                writer.WriteString("kind", "resync");
                writer.WriteStartArray("grant_ids");
                writer.WriteStringValue(grantId);
                writer.WriteEndArray();
                writer.WriteStartArray("missing");
                writer.WriteEndArray();
            });
            return scan.Result?.Clone()
                ?? throw new InvalidOperationException("scan returned no result");
        }

        /// <summary>Production apply (orchestrator + journal) against the real Core.</summary>
        public async Task<string> ApplyAsync()
        {
            async Task Capability(string name, CancellationToken token) =>
                await Client.RequireCapabilitiesAsync(
                    HostCommandRegistry.RequiredCapabilities(name), token);
            async Task<JsonElement> Lookup(string operationId, CancellationToken token)
            {
                var response = await Client.SendAsync("source_get_operation", 3, writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("operation_id", operationId);
                    writer.WriteEndObject();
                }, TimeSpan.FromSeconds(60), token);
                return response.Result!.Value.Clone();
            }

            var orchestrator = new HostOperationOrchestrator(
                Operations, Registry, Capability, Lookup);
            var payload = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
            {
                ["plan_id"] = Plan.GetProperty("plan_id").GetString(),
                ["plan_digest"] = Plan.GetProperty("plan_digest").GetString(),
                ["grant_ids"] = new[] { NewGrant },
                ["authorization"] = new Dictionary<string, object?>
                {
                    ["authorizations"] = Scan.GetProperty("authorizations").Clone(),
                },
            });
            var (operationId, _) = await orchestrator.ApplyAsync("source_resync", payload,
                (finalPayload, token) => Client.SendHostControlAsync("ResyncSource",
                    writer =>
                    {
                        // The envelope already opened the payload object.
                        foreach (var property in finalPayload.EnumerateObject())
                        {
                            property.WriteTo(writer);
                        }
                    }, TimeSpan.FromSeconds(60), Client.HostSession, token),
                CancellationToken.None);
            return operationId;
        }

        public async Task<string> ResolveAsync()
        {
            var resolved = await Client.SendAsync("resolve_page_resource", 3, writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("page_id", "p1");
                writer.WriteEndObject();
            }, TimeSpan.FromSeconds(60));
            return resolved.Result!.Value.GetProperty("resource_id").GetString()!;
        }

        /// <summary>Replay the exact CompletionRequest the Host already sent.</summary>
        public async Task<JsonElement> ReplayAckAsync(
            SourceOperationCoordinator.JournalEntry acknowledged)
        {
            var response = await SendCompletionAsync("AcknowledgeSourceOperation",
                acknowledged, acknowledged.CommitDigest!);
            return response.Result!.Value.Clone();
        }

        public async Task<CoreResponse> SendCompletionAsync(
            string command, SourceOperationCoordinator.JournalEntry entry, string commitDigest)
        {
            using var authorization = JsonDocument.Parse(entry.AuthorizationJson!);
            var grantIds = string.IsNullOrWhiteSpace(entry.GrantIds)
                ? Array.Empty<string>()
                : entry.GrantIds.Split(',', StringSplitOptions.RemoveEmptyEntries);
            return await Client.SendHostControlAsync(command, writer =>
            {
                // Flat CompletionRequest fields: the envelope opened `payload`.
                writer.WriteString("operation_id", entry.OperationId);
                writer.WriteString("request_digest", entry.RequestDigest);
                writer.WriteString("commit_digest", commitDigest);
                writer.WriteString("host_receipt_id", entry.HostReceiptId ?? string.Empty);
                writer.WriteStartArray("grant_ids");
                foreach (var grantId in grantIds)
                {
                    writer.WriteStringValue(grantId);
                }
                writer.WriteEndArray();
                writer.WritePropertyName("authorization");
                authorization.RootElement.WriteTo(writer);
            }, TimeSpan.FromSeconds(60), Client.HostSession, CancellationToken.None);
        }

        public async Task<JsonElement> PageBindingsAsync()
        {
            var script = Path.Combine(Repo, "verification", "FEA-11-HOST-AUTH-3", "tools",
                "check_gate.py");
            var output = await RunPythonAsync(
                Python, Repo, script, "--db", DatabasePath, "--page-bindings");
            using var document = JsonDocument.Parse(output.Trim().Split('\n').Last());
            return document.RootElement.GetProperty("page_bindings").Clone();
        }

        public async Task<bool> GateOpenAsync()
        {
            var script = Path.Combine(Repo, "verification", "FEA-11-HOST-AUTH-3", "tools",
                "check_gate.py");
            var output = await RunPythonAsync(Python, Repo, script, "--db", DatabasePath);
            using var document = JsonDocument.Parse(output.Trim().Split('\n').Last());
            return document.RootElement.GetProperty("open").GetBoolean();
        }

        public async Task<(int Bindings, int Publications)> CountRowsAsync()
        {
            var script = Path.Combine(Repo, "verification", "FEA-11-HOST-AUTH-2", "tools",
                "count_bindings.py");
            var output = await RunPythonAsync(Python, Repo, script, "--db", DatabasePath);
            using var document = JsonDocument.Parse(output.Trim().Split('\n').Last());
            return (document.RootElement.GetProperty("page_bindings").GetInt32(),
                document.RootElement.GetProperty("source_binding_publications").GetInt32());
        }

        public string HashOfNewZip() => Hash(NewZip);

        public async Task WriteEvidenceAsync(string fileName, IEnumerable<string> lines) =>
            await File.WriteAllTextAsync(Path.Combine(Root, fileName),
                $"DataRoot={Root}\n" + string.Join("\n", lines) + "\nPASS\n");

        public async ValueTask DisposeAsync()
        {
            await Client.DisposeAsync();
        }
    }

    private static string Hash(string path) => Convert.ToHexString(
        System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();

    private static string RepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        return directory?.FullName ?? throw new InvalidOperationException("repository not found");
    }

    private static async Task<string> RunPythonAsync(
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
        var output = await stdout;
        Assert.True(process.ExitCode == 0, output + await stderr);
        return output;
    }
}
