using System.Diagnostics;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
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
