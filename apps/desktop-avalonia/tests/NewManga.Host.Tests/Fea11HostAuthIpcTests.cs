using System.Diagnostics;
using System.Globalization;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

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
        var wireBefore = fixture.Client.Wire.Count;
        var applyAuthorizationJson = committed.AuthorizationJson!;
        using var applyAuthorization = JsonDocument.Parse(applyAuthorizationJson);

        // (3) ACK with the fresh authorization (real Core, host-control session).
        var acked = await fixture.Operations.AcknowledgeAsync(operationId);
        Assert.Equal("acknowledged", acked.State);
        Assert.NotNull(acked.AcknowledgedAt);
        Assert.True(fixture.Client.Wire.Count > wireBefore, "the ACK must cross the wire");
        // The journal does NOT replay the apply-time authorization any more.
        Assert.NotEqual(applyAuthorizationJson, acked.AuthorizationJson);
        using var freshAuthorization = JsonDocument.Parse(acked.AuthorizationJson!);
        var applyAt = Timestamp(applyAuthorization.RootElement.GetProperty("authorized_at"));
        var freshAt = Timestamp(freshAuthorization.RootElement.GetProperty("authorized_at"));
        Assert.True(freshAt > applyAt,
            $"fresh authorized_at {freshAt:O} must be later than the apply one {applyAt:O}");
        // ... and the identity is preserved (same operation / request digest / receipt).
        Assert.Equal(
            applyAuthorization.RootElement.GetProperty("operation_id").GetString(),
            freshAuthorization.RootElement.GetProperty("operation_id").GetString());
        Assert.Equal(
            applyAuthorization.RootElement.GetProperty("request_digest").GetString(),
            freshAuthorization.RootElement.GetProperty("request_digest").GetString());
        Assert.Equal(
            applyAuthorization.RootElement.GetProperty("host_receipt_id").GetString(),
            freshAuthorization.RootElement.GetProperty("host_receipt_id").GetString());
        evidence.Add("ack_authorized_at_advances=1");

        // (4) The wire ACK frame itself carries that fresh authorization.
        var ackFrame = fixture.Client.Wire.Frames.Last(frame =>
            frame.RequestLine.Contains("\"command\":\"AcknowledgeSourceOperation\"",
                StringComparison.Ordinal));
        using var ackRequest = JsonDocument.Parse(ackFrame.RequestLine);
        var wireAuthorization = ackRequest.RootElement.GetProperty("payload").GetProperty("authorization");
        Assert.Equal(operationId, wireAuthorization.GetProperty("operation_id").GetString());
        Assert.True(Timestamp(wireAuthorization.GetProperty("authorized_at")) > applyAt,
            "the ACK wire authorization must be freshly signed");
        Assert.Equal(
            freshAuthorization.RootElement.GetProperty("authorization_digest").GetString(),
            wireAuthorization.GetProperty("authorization_digest").GetString());
        Assert.Equal(
            freshAuthorization.RootElement.GetProperty("authorization_digest").GetString(),
            CanonicalJson.Sha256Hex(ackRequest.RootElement.GetProperty("payload")
                .GetProperty("authorization").GetProperty("authorizations")
                .EnumerateArray()
                .Select(item => new Dictionary<string, object?>
                {
                    ["registry_id"] = item.GetProperty("registry_id").GetString(),
                    ["generation"] = item.GetProperty("generation").GetInt32(),
                    ["identity_digest"] = item.GetProperty("identity_digest").GetString(),
                })
                .ToList()));
        evidence.Add("ack_wire_authorization=fresh");

        // (5) The gate opened: the SAME page now resolves through the NEW v2 key.
        var resource = await fixture.ResolveAsync();
        Assert.StartsWith("page-rendition-v2-", resource);
        Assert.NotEqual("page-rendition-p1", resource);
        evidence.Add("gate_open_resource=" + resource);

        // (6) A second ACK is a pure no-op: acknowledged early return, ZERO wire frames.
        var wireAfterAck = fixture.Client.Wire.Count;
        var again = await fixture.Operations.AcknowledgeAsync(operationId);
        Assert.Equal("acknowledged", again.State);
        Assert.Equal(wireAfterAck, fixture.Client.Wire.Count);
        evidence.Add("second_ack_frames=0");

        // (7) Replaying the exact same CompletionRequest returns the SAME receipt and
        // creates no binding (C-17 §3.2:165).
        var replay = await fixture.ReplayAckAsync(acked);
        Assert.Equal(acked.CommitDigest, replay.GetProperty("commit_digest").GetString());
        Assert.Equal("acknowledged", replay.GetProperty("state").GetString());
        var rowsAfter = await fixture.CountRowsAsync();
        Assert.Equal(rowsBefore, rowsAfter);
        evidence.Add($"replay_same_receipt=1 rows={rowsAfter.Bindings}/{rowsAfter.Publications}");

        // (8) The source bytes are conserved (hashed before the run).
        Assert.Equal(fixture.NewZipHash, fixture.HashOfNewZip());
        evidence.Add("source_conserved=1");

        await fixture.WriteEvidenceAsync("real-ipc-ack.txt", evidence);
    }

    [Fea11IpcFact]
    public async Task Recovery_UsesAFreshAuthorization_AfterAWrongDigestRefusal()
    {
        await using var fixture = await IpcFixture.CreateAsync();
        var evidence = new List<string>();

        var operationId = await fixture.ApplyAsync();
        var committed = fixture.Operations.Get(operationId)!;
        Assert.Equal("core-committed", committed.State);
        var rowsBefore = await fixture.CountRowsAsync();
        var applyAuthorizationJson = committed.AuthorizationJson!;
        using var applyAuthorization = JsonDocument.Parse(applyAuthorizationJson);
        var applyAt = Timestamp(applyAuthorization.RootElement.GetProperty("authorized_at"));

        // (a) A CompletionRequest with the WRONG commit digest is a typed refusal: the
        // journal stays core-committed, the gate stays pending and no row changes.
        var wrong = await Assert.ThrowsAsync<CoreOperationException>(
            () => fixture.SendCompletionAsync("AcknowledgeSourceOperation", committed,
                new string('0', 64)));
        Assert.Equal("INVALID_REQUEST", wrong.Code);
        Assert.Equal("core-committed", fixture.Operations.Get(operationId)!.State);
        Assert.Equal(rowsBefore, await fixture.CountRowsAsync());
        var stillPending = await Assert.ThrowsAsync<CoreOperationException>(
            () => fixture.ResolveAsync());
        Assert.Equal("SOURCE_ACCESS_DENIED", stillPending.Code);
        evidence.Add("wrong_digest_ack=" + wrong.Code + " gate=pending");

        // (b) Recovery of the never-ACKed committed operation succeeds with a FRESH
        // authorization, opens every gate and is idempotent on a second call.
        var wireBefore = fixture.Client.Wire.Count;
        var recovered = await fixture.Operations.RecoverAsync(operationId);
        Assert.Equal("recovered", recovered.State);
        Assert.True(fixture.Client.Wire.Count > wireBefore, "the recovery must cross the wire");
        Assert.NotEqual(applyAuthorizationJson, recovered.AuthorizationJson);
        using var freshAuthorization = JsonDocument.Parse(recovered.AuthorizationJson!);
        Assert.True(
            Timestamp(freshAuthorization.RootElement.GetProperty("authorized_at")) > applyAt,
            "the recovery authorization must be freshly signed");
        Assert.Equal(
            applyAuthorization.RootElement.GetProperty("host_receipt_id").GetString(),
            freshAuthorization.RootElement.GetProperty("host_receipt_id").GetString());
        evidence.Add("recovery_authorized_at_advances=1");

        var recoveryFrame = fixture.Client.Wire.Frames.Last(frame =>
            frame.RequestLine.Contains("\"command\":\"CompleteSourceOperationRecovery\"",
                StringComparison.Ordinal));
        using var recoveryRequest = JsonDocument.Parse(recoveryFrame.RequestLine);
        var recoveryWireAuthorization = recoveryRequest.RootElement
            .GetProperty("payload").GetProperty("authorization");
        Assert.True(Timestamp(recoveryWireAuthorization.GetProperty("authorized_at")) > applyAt,
            "the recovery wire authorization must be freshly signed");
        Assert.Equal(recovered.CommitDigest, committed.CommitDigest);
        evidence.Add("recovery_wire_authorization=fresh");

        var wireAfterRecovery = fixture.Client.Wire.Count;
        var again = await fixture.Operations.RecoverAsync(operationId);
        Assert.Equal("recovered", again.State);
        Assert.Equal(wireAfterRecovery, fixture.Client.Wire.Count);
        evidence.Add("second_recovery_frames=0");

        var resource = await fixture.ResolveAsync();
        Assert.StartsWith("page-rendition-v2-", resource);
        Assert.Equal(rowsBefore, await fixture.CountRowsAsync());
        Assert.Equal(fixture.NewZipHash, fixture.HashOfNewZip());
        evidence.Add("gate_open_resource=" + resource + " rows_unchanged=1");

        await fixture.WriteEvidenceAsync("real-ipc-recovery.txt", evidence);
    }

    private static DateTimeOffset Timestamp(JsonElement element) =>
        DateTimeOffset.Parse(element.GetString()!, CultureInfo.InvariantCulture,
            DateTimeStyles.AdjustToUniversal);

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

        public static async Task<IpcFixture> CreateAsync()
        {
            var repo = RepositoryRoot();
            var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON")
                ?? "C:/Python314/python.exe";
            var root = Path.Combine(repo + ".workspace", "FEA-11", "fixtures",
                "host-auth-ipc-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            await RunPythonAsync(python, repo, "tests/fea11/support/ipc_seed.py",
                "--data-root", root, "--db", Path.Combine(root, "library.db"));
            using var seedDocument = JsonDocument.Parse(await File.ReadAllTextAsync(
                Path.Combine(root, "ipc-seed-receipt.json")));
            var seed = seedDocument.RootElement.Clone();
            Assert.Equal(9, seed.GetProperty("schema_version").GetInt32());

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
                var registered = registry.Register("fea11-hostauth-ipc", [root]);
                var sources = new SourceReadCoordinator(client, registry, () => true);
                var operations = new SourceOperationCoordinator(client, root, () => true, registry);
                var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
                {
                    ["decoder"] = "zip",
                    ["scale"] = 1.0,
                    ["params_digest"] = new string('a', 64),
                });
                var sourceId = seed.GetProperty("source_id").GetString()!;
                var newZip = seed.GetProperty("new_zip").GetString()!;
                var newGrant = await sources.IssueAsync(
                    registered.RegistryId, registered.Generation, newZip, "zip",
                    sourceId, sourceId + "-candidate", rendition);
                var scan = await ScanAsync(client, seed, newGrant);
                var fixture = new IpcFixture(repo, python, root, client, registry, sources,
                    operations, seed, newZip, Hash(newZip), newGrant, scan);
                await fixture.PlanAsync();
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
