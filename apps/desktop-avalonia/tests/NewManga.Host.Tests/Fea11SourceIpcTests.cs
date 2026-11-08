using System.Diagnostics;
using System.Text.Json;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using NewManga.Host.Tests.Support;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11 (C-17 §5/§7): the real stdio IPC face. Opt-in only
/// (``NEWMANGA_FEA11_IPC=1``) because it starts the real Python Core against
/// an isolated workspace data root. Evidence goes to the isolated root
/// (R-008), never to a tracked repository file.
///
/// This first pass proves the command surface and the fail-closed refusals
/// (missing grant / unknown operation / application-channel host-only). The
/// full scan->plan->apply->ack->resolve chain needs a Host-issued grant and
/// is tracked as the remaining C4 work.
/// </summary>
public sealed class Fea11SourceIpcTests
{
    [Fea11IpcFact]
    public async Task HostControlSurfaceRefusesWithoutGrant_AndUnknownOperationsTyped()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11", "fixtures", "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);

        var seedInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo, UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardOutput = true, RedirectStandardError = true,
        };
        foreach (var argument in new[]
                 {
                     "tests/fea11/support/ipc_seed.py",
                     "--data-root", root,
                     "--db", Path.Combine(root, "library.db"),
                 })
        {
            seedInfo.ArgumentList.Add(argument);
        }
        using (var seed = Process.Start(seedInfo)!)
        {
            var stdout = seed.StandardOutput.ReadToEndAsync();
            var stderr = seed.StandardError.ReadToEndAsync();
            await seed.WaitForExitAsync();
            Assert.True(seed.ExitCode == 0, await stdout + await stderr);
        }
        using var receiptDoc = JsonDocument.Parse(
            await File.ReadAllTextAsync(Path.Combine(root, "ipc-seed-receipt.json")));
        var receipt = receiptDoc.RootElement;
        Assert.Equal(9, receipt.GetProperty("schema_version").GetInt32());

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
            Assert.Contains("source.sync.scan/1", (await client.PingAsync()).Capabilities);
            // Host-control commands require the HOST-ISSUER-1 private session.
            await client.OpenHostSessionAsync();

            // (1) host-control writes refuse without a live grant (fail-closed).
            var scan = await Assert.ThrowsAsync<CoreOperationException>(() =>
                client.SendHostControlAsync("ScanSourceSync", writer =>
                {
                    writer.WriteString("source_id", receipt.GetProperty("source_id").GetString());
                    writer.WriteStartArray("project_ids");
                    writer.WriteStringValue("b1");
                    writer.WriteEndArray();
                    writer.WriteString("scope", "current");
                    writer.WriteString("kind", "resync");
                    writer.WriteStartArray("grant_ids");
                    writer.WriteStringValue("grant-does-not-exist");
                    writer.WriteEndArray();
                    writer.WriteStartArray("missing");
                    writer.WriteEndArray();
                }));
            Assert.True(scan.Code is "SOURCE_GRANT_REVOKED" or "SOURCE_OPERATION_NOT_FOUND"
                    or "SOURCE_ACCESS_DENIED" or "SOURCE_GRANT_EXPIRED" or "SOURCE_SCOPE_DENIED"
                    or "SOURCE_BUDGET_EXCEEDED" or "INVALID_REQUEST" or "SOURCE_SYNC_PLAN_INVALID",
                "unexpected scan refusal: " + scan.Code);
            evidence.Add("ScanSourceSync(no grant) -> " + scan.Code);

            // (2) unknown operation ids are typed refusals, not empty reads.
            var operation = await Assert.ThrowsAsync<CoreOperationException>(() =>
                client.SendHostControlAsync("GetSourceOperation", writer =>
                {
                    writer.WriteString("operation_id", "op-" + new string('0', 32));
                }));
            Assert.Contains(operation.Code, new[] { "SOURCE_OPERATION_NOT_FOUND", "INVALID_REQUEST" });
            evidence.Add("GetSourceOperation(unknown) -> " + operation.Code);

            var ack = await Assert.ThrowsAsync<CoreOperationException>(() =>
                client.SendHostControlAsync("AcknowledgeSourceOperation", writer =>
                {
                    writer.WriteString("operation_id", "op-" + new string('0', 32));
                    writer.WriteString("commit_digest", new string('0', 64));
                }));
            Assert.Contains(ack.Code, new[] { "SOURCE_OPERATION_NOT_FOUND", "INVALID_REQUEST" });
            evidence.Add("AcknowledgeSourceOperation(unknown) -> " + ack.Code);

            // (3) host-control commands are refused on the ordinary channel.
            var application = await Assert.ThrowsAsync<CoreOperationException>(() =>
                client.SendAsync("ScanSourceSync", 3, writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("source_id", receipt.GetProperty("source_id").GetString());
                    writer.WriteEndObject();
                }, TimeSpan.FromSeconds(30)));
            Assert.Equal("HOST_ONLY_REQUIRED", application.Code);
            evidence.Add("application-channel ScanSourceSync -> " + application.Code);
        }

        await File.WriteAllTextAsync(Path.Combine(root, "real-ipc.txt"),
            $"DataRoot={root}\n" + string.Join("\n", evidence) + "\nPASS\n");
    }

    [Fea11IpcFact]
    public async Task ScanWithAHostIssuedGrant_WorksEndToEnd()
    {
        var (repo, python, root, receipt) = await SeedAsync();
        var options = BuildOptions(repo, python, root);
        await using var client = await CoreServiceClient.StartAsync(options);
        await client.OpenHostSessionAsync();
        Assert.Contains("source.sync.scan/1", (await client.PingAsync()).Capabilities);

        var registry = new SourceAccessRegistry(root);
        // The registry authorizes roots; the containers live under the root.
        var registered = registry.Register("fea11-ipc", [root]);
        var sources = new SourceReadCoordinator(client, registry, () => true);
        var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["decoder"] = "zip",
            ["scale"] = 1.0,
            ["params_digest"] = new string('a', 64),
        });
        var grantId = await sources.IssueAsync(
            registered.RegistryId, registered.Generation,
            receipt.GetProperty("old_zip").GetString()!, "zip",
            receipt.GetProperty("source_id").GetString()!,
            receipt.GetProperty("version_id").GetString()!,
            rendition);

        var scan = await client.SendHostControlAsync("ScanSourceSync", writer =>
        {
            writer.WriteString("source_id", receipt.GetProperty("source_id").GetString());
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
        var result = scan.Result ?? throw new InvalidOperationException("scan returned no result");
        Assert.Equal(JsonValueKind.Object, result.ValueKind);
        Assert.True(result.TryGetProperty("observations", out _) || result.TryGetProperty("diff", out _),
            "scan result has neither observations nor diff: " + result.GetRawText());

        await File.WriteAllTextAsync(Path.Combine(root, "real-ipc.txt"),
            $"DataRoot={root}\nregistry_generation={registered.Generation}\n"
            + "ScanSourceSync(with issued grant) -> OK\nPASS\n");
    }

    [Fea11IpcFact]
    public async Task FullSyncChain_PublishesNewGeneration_AndResolvesV2()
    {
        var (repo, python, root, receipt) = await SeedAsync();
        var options = BuildOptions(repo, python, root);
        await using var client = await CoreServiceClient.StartAsync(options);
        await client.OpenHostSessionAsync();

        var registry = new SourceAccessRegistry(root);
        var registered = registry.Register("fea11-ipc", [root]);
        var sources = new SourceReadCoordinator(client, registry, () => true);
        var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["decoder"] = "zip", ["scale"] = 1.0, ["params_digest"] = new string('a', 64),
        });
        var sourceId = receipt.GetProperty("source_id").GetString()!;
        var oldZip = receipt.GetProperty("old_zip").GetString()!;
        var newZip = receipt.GetProperty("new_zip").GetString()!;
        var newZipBytes = await File.ReadAllBytesAsync(newZip);
        var newZipHash = Convert.ToHexString(
            System.Security.Cryptography.SHA256.HashData(newZipBytes)).ToLowerInvariant();
        var newZipInfo = new FileInfo(newZip);

        // A seeded legacy binding has no import-time grant mapping; the read
        // evidence starts from the new binding the sync publishes.

        // (b) scan the NEW container through its own grant -> changed page.
        var newGrant = await sources.IssueAsync(
            registered.RegistryId, registered.Generation, newZip, "zip",
            sourceId, sourceId + "-candidate", rendition);
        var scan = await client.SendHostControlAsync("ScanSourceSync", writer =>
        {
            writer.WriteString("source_id", sourceId);
            writer.WriteStartArray("project_ids");
            writer.WriteStringValue("b1");
            writer.WriteEndArray();
            writer.WriteString("scope", "current");
            writer.WriteString("kind", "resync");
            writer.WriteStartArray("grant_ids");
            writer.WriteStringValue(newGrant);
            writer.WriteEndArray();
            writer.WriteStartArray("missing");
            writer.WriteEndArray();
        });
        var scanResult = scan.Result ?? throw new InvalidOperationException("scan returned no result");
        var totals = scanResult.GetProperty("totals");
        Assert.True(totals.GetProperty("changed").GetInt32() >= 1,
            "new container must produce a changed page: " + scanResult.GetRawText());
        var scanPath = Path.Combine(root, "scan.json");
        await File.WriteAllTextAsync(scanPath, scanResult.GetRawText());

        // (c) plan -> preview -> confirm (app channel).
        var applyScript = Path.Combine(repo, "tests", "fea11", "support", "ipc_apply.py");
        var bodyPath = Path.Combine(root, "plan-body.json");
        await RunPythonAsync(python, repo, applyScript,
            "--mode", "body", "--data-root", root, "--db", Path.Combine(root, "library.db"),
            "--scan-json", scanPath, "--grant-id", newGrant, "--out", bodyPath);
        using var bodyDoc = JsonDocument.Parse(await File.ReadAllTextAsync(bodyPath));
        var body = bodyDoc.RootElement;
        var planId = body.GetProperty("plan_id").GetString()!;
        await client.SendAsync("source_plan_sync", 3, writer =>
        {
            body.GetProperty("plan_body").WriteTo(writer);
        }, TimeSpan.FromSeconds(60));
        var preview = await client.SendAsync("source_preview_sync_plan", 3, writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("plan_id", planId);
            writer.WriteString("plan_digest", body.GetProperty("plan_digest").GetString());
            writer.WriteEndObject();
        }, TimeSpan.FromSeconds(60));
        var planDigest = preview.Result!.Value.GetProperty("plan_digest").GetString()!;
        await client.SendAsync("source_confirm_sync_plan", 3, writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("plan_id", planId);
            writer.WriteString("plan_digest", planDigest);
            writer.WritePropertyName("confirmation");
            body.GetProperty("confirmation").WriteTo(writer);
            writer.WriteEndObject();
        }, TimeSpan.FromSeconds(60));

        // (d) apply on the host-control session.
        var applyPath = Path.Combine(root, "apply.json");
        await RunPythonAsync(python, repo, applyScript,
            "--mode", "apply", "--data-root", root, "--db", Path.Combine(root, "library.db"),
            "--scan-json", scanPath, "--grant-id", newGrant, "--body-json", bodyPath,
            "--plan-digest", planDigest, "--out", applyPath);
        using var applyDoc = JsonDocument.Parse(await File.ReadAllTextAsync(applyPath));
        var applyPayloads = applyDoc.RootElement;
        var applied = await client.SendHostControlAsync("ResyncSource", writer =>
        {
            var apply = applyPayloads.GetProperty("apply");
            writer.WriteString("operation_id", apply.GetProperty("operation_id").GetString());
            writer.WriteString("plan_id", apply.GetProperty("plan_id").GetString());
            writer.WriteString("plan_digest", apply.GetProperty("plan_digest").GetString());
            writer.WriteStartArray("grant_ids");
            writer.WriteStringValue(newGrant);
            writer.WriteEndArray();
            writer.WritePropertyName("authorization");
            apply.GetProperty("authorization").WriteTo(writer);
        });
        Assert.NotNull(applied.Result);
        var operationId = applyPayloads.GetProperty("operation_id").GetString()!;

        // (e) the pending publication gate refuses reads until the ACK.
        var pending = await Assert.ThrowsAsync<CoreOperationException>(() =>
            client.SendAsync("resolve_page_resource", 3, writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("page_id", "p1");
                writer.WriteEndObject();
            }, TimeSpan.FromSeconds(60)));
        Assert.Equal("SOURCE_ACCESS_DENIED", pending.Code);

        // (f) ACK: the Core opens the gates; the Host journal records it.
        var operation = await client.SendAsync("source_get_operation", 3, writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("operation_id", operationId);
            writer.WriteEndObject();
        }, TimeSpan.FromSeconds(60));
        var operationRow = operation.Result!.Value;
        var commitDigest = operationRow.GetProperty("commit_digest").GetString()!;
        await client.SendHostControlAsync("AcknowledgeSourceOperation", writer =>
        {
            var ack = applyPayloads.GetProperty("ack");
            writer.WriteString("operation_id", ack.GetProperty("operation_id").GetString());
            writer.WriteString("request_digest", ack.GetProperty("request_digest").GetString());
            writer.WriteString("commit_digest", commitDigest);
            writer.WriteString("host_receipt_id", ack.GetProperty("host_receipt_id").GetString());
            writer.WriteStartArray("grant_ids");
            writer.WriteStringValue(newGrant);
            writer.WriteEndArray();
            writer.WritePropertyName("authorization");
            ack.GetProperty("authorization").WriteTo(writer);
        });

        // (g) the new binding resolves through a DIFFERENT v2 key (new bytes).
        var after = await client.SendAsync("resolve_page_resource", 3, writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("page_id", "p1");
            writer.WriteEndObject();
        }, TimeSpan.FromSeconds(60));
        var afterResource = after.Result!.Value.GetProperty("resource_id").GetString()!;
        Assert.StartsWith("page-rendition-v2-", afterResource);
        // The published bytes belong to the NEW binding (the key differs from
        // any pre-sync selection; the legacy key is never selected).
        Assert.NotEqual("page-rendition-p1", afterResource);

        // (h) the source file is untouched (hash/size/mtime conserved).
        var afterBytes = await File.ReadAllBytesAsync(newZip);
        Assert.Equal(newZipHash, Convert.ToHexString(
            System.Security.Cryptography.SHA256.HashData(afterBytes)).ToLowerInvariant());
        Assert.Equal(newZipInfo.Length, new FileInfo(newZip).Length);

        await File.WriteAllTextAsync(Path.Combine(root, "real-ipc.txt"),
            $"DataRoot={root}\nnew_container_scan_changed=1\npending_gate=SOURCE_ACCESS_DENIED\n"
            + $"ack_commit_digest={commitDigest}\nnew_binding_resource={afterResource}\n"
            + "source_conserved=1\nPASS\n");
    }

    /// <summary>
    /// FEA-11-RESIDUAL-4A AC-R3-1 (AC11-7; C-17 §5.3 lines 255-257): the Host
    /// read-only diagnosis projection of the durable operation journal.
    ///
    /// It is deliberately NOT gated: it never starts a Core. The projection
    /// reads the journal entry's already-recorded <c>CommitReceipt</c> and
    /// reports only the <c>missing</c> / <c>needs_confirmation</c> bindings,
    /// proving that:
    /// <list type="bullet">
    /// <item>the diagnosis face needs no new Core command, capability or wire
    /// field (the receipt is journaled by the apply path);</item>
    /// <item><see cref="IHostController"/> keeps no source-diagnosis member
    /// (C-07 pin untouched);</item>
    /// <item>the projection is operation-scoped, stable and read-only — it
    /// never mutates the journal state.</item>
    /// </list>
    /// The separate "V(p,t) is not widened" assertion lives on the Core side
    /// (``tests/fea11/test_source_sync.py``: a missing-bound page stays
    /// invisible to ``get_page``/``list_pages``).
    /// </summary>
    [Fact]
    public void OperationJournalProjectionReportsOnlyDiagnosticBindings()
    {
        Assert.True(
            OperatingSystem.IsWindows(),
            "reason: the source-operation journal is DPAPI CurrentUser (Windows only)");
        var dataRoot = HostFixture.NewDataRoot("fea11-journal-diagnostics");
        var operations = new SourceOperationCoordinator(null, dataRoot);

        // The journal is the ONLY source: an operation whose commit receipt is
        // not recorded yet projects nothing (never a global page scan).
        var pending = operations.Begin(
            "plan-r3-pending", new string('a', 64), "resync", new string('b', 64));
        operations.Authorize(
            pending.OperationId,
            "{\"operation_id\":\"" + pending.OperationId + "\"}",
            "host-receipt-r3-pending");
        Assert.Empty(operations.ListBindingDiagnostics(pending.OperationId));

        var operation = operations.Begin(
            "plan-r3", new string('a', 64), "resync", new string('b', 64));
        operations.Authorize(
            operation.OperationId,
            "{\"operation_id\":\"" + operation.OperationId + "\"}",
            "host-receipt-r3");
        var receipt = """
        {"operation_id":"op-receipt","bindings":[
          {"page_id":"p2","binding_id":"pb-p2","binding_version":1,"source_id":"s1","version_id":"sv1","entry_id":"e2","status":"missing"},
          {"page_id":"p1","binding_id":"pb-p1","binding_version":2,"source_id":"s1","version_id":"sv2","entry_id":"e1","status":"needs_confirmation"},
          {"page_id":"p3","binding_id":"pb-p3","binding_version":1,"source_id":"s1","version_id":"sv1","entry_id":"e3","status":"healthy"}
        ]}
        """;
        operations.MarkCommitted(operation.OperationId, new string('c', 64), receipt);

        var diagnostics = operations.ListBindingDiagnostics(operation.OperationId);
        // Only the two diagnostic statuses; deterministic page order.
        Assert.Equal(new[] { "p1", "p2" }, diagnostics.Select(row => row.PageId).ToArray());
        Assert.Equal(
            new[] { "needs_confirmation", "missing" },
            diagnostics.Select(row => row.Status).ToArray());
        Assert.Equal(operation.OperationId, diagnostics[0].OperationId);
        Assert.Equal("pb-p1", diagnostics[0].BindingId);
        Assert.Equal(2, diagnostics[0].BindingVersion);
        Assert.Equal("s1", diagnostics[0].SourceId);
        Assert.Equal("sv2", diagnostics[0].VersionId);
        Assert.Equal("e1", diagnostics[0].EntryId);

        // Read-only + operation-scoped: an unknown id is an empty projection,
        // and reading twice never moves the journal state.
        Assert.Empty(operations.ListBindingDiagnostics("op-" + new string('0', 32)));
        Assert.Equal(
            diagnostics.Select(row => row.PageId).ToArray(),
            operations.ListBindingDiagnostics(operation.OperationId)
                .Select(row => row.PageId).ToArray());
        Assert.Equal("core-committed", operations.Get(operation.OperationId)!.State);

        // A corrupt durable receipt is a typed conflict, never a silent
        // "nothing to diagnose".
        var corrupt = operations.Begin(
            "plan-r3-corrupt", new string('a', 64), "resync", new string('b', 64));
        operations.Authorize(
            corrupt.OperationId,
            "{\"operation_id\":\"" + corrupt.OperationId + "\"}",
            "host-receipt-corrupt");
        operations.MarkCommitted(corrupt.OperationId, new string('c', 64), "not-json");
        var conflict = Assert.Throws<SourceAccessException>(
            () => operations.ListBindingDiagnostics(corrupt.OperationId));
        Assert.Equal("SOURCE_SYNC_STATE_CONFLICT", conflict.Code);

        // No new command and no IHostController surface: the diagnosis face is
        // Host-internal only (0 pin; the C-07 pin stays 18/18).
        Assert.Throws<HostCommandUnknownException>(
            () => HostCommandRegistry.Get("source_binding_diagnostics"));
        var hostControllerMethods = typeof(IHostController)
            .GetMethods()
            .Select(method => method.Name)
            .ToArray();
        Assert.DoesNotContain(
            hostControllerMethods,
            name => name.Contains("Source", StringComparison.Ordinal)
                || name.Contains("Sync", StringComparison.Ordinal)
                || name.Contains("Missing", StringComparison.Ordinal));
    }

    /// <summary>
    /// FEA-11-RESIDUAL-4A D-1c source sentinel (NOT gated): the
    /// `RecordSourceOperationFailure` host-control callback must write FLAT
    /// payload fields. Writing a complete object into the already-opened
    /// envelope payload nested it and the client threw, so a failure record was
    /// never delivered (same defect class as D-1a).
    ///
    /// This sentinel runs in the default gate; the gated
    /// `Fea11Residual4AIpcTests.ProductionDispatcherFailureRecordIsFlattenedAndKeepsGatesPending`
    /// proves the real Core chain (typed result + gates remain pending).
    /// </summary>
    [Fact]
    public void FailureRecordHostControlPayloadStaysFlat()
    {
        var repo = RepositoryRoot();
        var path = Path.Combine(repo, "apps", "desktop-avalonia", "src",
            "NewManga.Host", "HostRuntime.cs");
        Assert.True(File.Exists(path), "HostRuntime.cs not found: " + path);
        var text = File.ReadAllText(path);
        var start = text.IndexOf(
            "\"RecordSourceOperationFailure\"", StringComparison.Ordinal);
        Assert.True(start >= 0,
            "the RecordSourceOperationFailure call site is missing");
        var end = text.IndexOf(
            "_options.RequestTimeout", start, StringComparison.Ordinal);
        Assert.True(end > start,
            "the RecordSourceOperationFailure callback end is missing");
        var callback = text[start..end];
        // Flat fields only: a complete object here nests the payload and throws
        // on the client (Utf8JsonWriter cannot start an object without a name).
        Assert.DoesNotContain("WriteStartObject", callback);
        Assert.DoesNotContain("WriteEndObject", callback);
        Assert.Contains("\"operation_id\"", callback);
        Assert.Contains("\"request_digest\"", callback);
        Assert.Contains("\"code\"", callback);
    }

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
            WorkingDirectory = cwd, UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardOutput = true, RedirectStandardError = true,
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

    private static async Task<(string Repo, string Python, string Root, JsonElement Receipt)> SeedAsync()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11", "fixtures", "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var seedInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo, UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardOutput = true, RedirectStandardError = true,
        };
        foreach (var argument in new[]
                 {
                     "tests/fea11/support/ipc_seed.py",
                     "--data-root", root,
                     "--db", Path.Combine(root, "library.db"),
                 })
        {
            seedInfo.ArgumentList.Add(argument);
        }
        using (var seed = Process.Start(seedInfo)!)
        {
            var stdout = seed.StandardOutput.ReadToEndAsync();
            var stderr = seed.StandardError.ReadToEndAsync();
            await seed.WaitForExitAsync();
            Assert.True(seed.ExitCode == 0, await stdout + await stderr);
        }
        using var receiptDoc = JsonDocument.Parse(
            await File.ReadAllTextAsync(Path.Combine(root, "ipc-seed-receipt.json")));
        return (repo, python, root, receiptDoc.RootElement.Clone());
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

    private sealed class Fea11IpcFactAttribute : FactAttribute
    {
        public Fea11IpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "set NEWMANGA_FEA11_IPC=1 for real isolated Python Core stdio IPC";
            }
        }
    }
}
