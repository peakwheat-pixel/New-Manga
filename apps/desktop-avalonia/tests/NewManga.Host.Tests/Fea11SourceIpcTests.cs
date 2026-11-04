using System.Diagnostics;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
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
        Assert.Equal(8, receipt.GetProperty("schema_version").GetInt32());

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
        var registered = registry.Register("fea11-ipc", [receipt.GetProperty("old_zip").GetString()!]);
        var sources = new SourceReadCoordinator(client, registry, () => true);
        var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["decoder"] = "zip", ["scale"] = 1.0, ["params_digest"] = new string('a', 64),
        });
        var grantId = await sources.IssueAsync(
            registered.RegistryId, registered.Generation,
            receipt.GetProperty("old_zip").GetString()!, "zip",
            receipt.GetProperty("source_id").GetString()!,
            receipt.GetProperty("version_id").GetString()!, rendition);

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
        var scanResult = scan.Result ?? throw new InvalidOperationException("scan returned no result");
        var scanPath = Path.Combine(root, "scan.json");
        await File.WriteAllTextAsync(scanPath, scanResult.GetRawText());

        var applyScript = Path.Combine(repo, "tests", "fea11", "support", "ipc_apply.py");
        var bodyPath = Path.Combine(root, "plan-body.json");
        await RunPythonAsync(python, repo, applyScript,
            "--mode", "body", "--data-root", root, "--db", Path.Combine(root, "library.db"),
            "--scan-json", scanPath, "--grant-id", grantId, "--out", bodyPath);
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

        var applyPath = Path.Combine(root, "apply.json");
        await RunPythonAsync(python, repo, applyScript,
            "--mode", "apply", "--data-root", root, "--db", Path.Combine(root, "library.db"),
            "--scan-json", scanPath, "--grant-id", grantId, "--body-json", bodyPath,
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
            writer.WriteStringValue(grantId);
            writer.WriteEndArray();
            writer.WritePropertyName("authorization");
            apply.GetProperty("authorization").WriteTo(writer);
        });
        Assert.NotNull(applied.Result);
        var operationId = applyPayloads.GetProperty("operation_id").GetString()!;
        // The commit receipt digest is read on the operation query face (the
        // dispatch result carries the state; the receipt lives on the row).
        var operation = await client.SendAsync("source_get_operation", 3, writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("operation_id", operationId);
            writer.WriteEndObject();
        }, TimeSpan.FromSeconds(60));
        var operationRow = operation.Result ?? throw new InvalidOperationException("operation query returned no result");
        var commitDigest = operationRow.GetProperty("commit_digest").GetString()!;
        Assert.Equal("core-committed", operationRow.GetProperty("state").GetString());

        await client.SendHostControlAsync("AcknowledgeSourceOperation", writer =>
        {
            var ack = applyPayloads.GetProperty("ack");
            writer.WriteString("operation_id", ack.GetProperty("operation_id").GetString());
            writer.WriteString("request_digest", ack.GetProperty("request_digest").GetString());
            writer.WriteString("commit_digest", commitDigest);
            writer.WriteString("host_receipt_id", ack.GetProperty("host_receipt_id").GetString());
            writer.WriteStartArray("grant_ids");
            writer.WriteStringValue(grantId);
            writer.WriteEndArray();
            writer.WritePropertyName("authorization");
            ack.GetProperty("authorization").WriteTo(writer);
        });

        // A sync switch binds a new source version: reads need a fresh grant
        // scoped to that version (C-16 §3.1; stale grants stay fail-closed).
        var newVersion = scanResult.GetProperty("source").GetProperty("version_id").GetString()!;
        var newGrantId = await sources.IssueAsync(
            registered.RegistryId, registered.Generation,
            receipt.GetProperty("new_zip").GetString()!, "zip",
            receipt.GetProperty("source_id").GetString()!, newVersion, rendition);

        var resolved = await client.SendAsync("resolve_page_resource", 3, writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("page_id", "p1");
            writer.WriteEndObject();
        }, TimeSpan.FromSeconds(60));
        var resolvedResult = resolved.Result ?? throw new InvalidOperationException("resolve returned no result");
        var resourceId = resolvedResult.GetProperty("resource_id").GetString()!;
        Assert.StartsWith("page-rendition-v2-", resourceId);

        await File.WriteAllTextAsync(Path.Combine(root, "real-ipc.txt"),
            $"DataRoot={root}\nscan -> plan -> preview -> confirm -> ResyncSource -> ACK -> resolve\n"
            + $"operation_id={operationId}\ncommit_digest={commitDigest}\nresource_id={resourceId}\nPASS\n");
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
