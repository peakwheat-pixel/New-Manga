using System.Diagnostics;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>Real Python source process, production client, isolated FEA-10 data root.</summary>
public sealed class Fea10RunIpcTests
{
    [Fea10IpcFact]
    public async Task PrepareAcceptAndReplayAfterCoreRestart()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git"))) directory = directory.Parent;
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-10", "fixtures", "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var seedInfo = new ProcessStartInfo(python) { WorkingDirectory = repo, UseShellExecute = false,
            CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true };
        foreach (var arg in new[] { "tests/fea10/support/restart_core.py", "--data-root", root, "--db", Path.Combine(root, "library.db"), "--stop" })
            seedInfo.ArgumentList.Add(arg);
        using (var seed = Process.Start(seedInfo)!)
        {
            var stdout = seed.StandardOutput.ReadToEndAsync(); var stderr = seed.StandardError.ReadToEndAsync();
            await seed.WaitForExitAsync();
            Assert.True(seed.ExitCode == 0, await stdout + await stderr);
        }
        using var fixture = JsonDocument.Parse(await File.ReadAllTextAsync(Path.Combine(root, "restart-receipt.json")));
        var region = fixture.RootElement.GetProperty("region_id").GetString()!;
        var options = new CoreServiceOptions
        {
            ExecutablePath = python,
            AdditionalArguments = ["-X", "utf8", "-c", $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');import bootstrap.core_service as m;raise SystemExit(m.main())"],
            DataRoot = root, DerivedRoot = Path.Combine(root, "derived"), CatalogDbPath = Path.Combine(root, "catalog.sqlite"),
            StderrLogPath = Path.Combine(root, "core.stderr.log"), WireLogPath = Path.Combine(root, "wire.ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(90), RequestTimeout = TimeSpan.FromSeconds(30),
        };
        JsonElement candidate;
        string runId;
        await using (var client = await CoreServiceClient.StartAsync(options))
        {
            using var request = JsonDocument.Parse("{\"command\":\"ocr_region\",\"scope\":{\"kind\":\"region\",\"region_id\":\"" + region + "\"}}");
            var preview = await client.PrepareRunAsync(request.RootElement);
            Assert.StartsWith("sha256:", preview.SnapshotDigest);
            Assert.False(preview.RedactedPayloadPreview.TryGetProperty("settingsSnapshot", out _));
            var wrongGeneration = await Assert.ThrowsAsync<CoreOperationException>(() =>
                client.AcceptRunAsync(preview.PreparedRunId, preview.Generation + 1, "bad-generation"));
            Assert.Equal("RUN_STALE_PREVIEW", wrongGeneration.Code);
            var frame = client.Wire.Frames.Single(item => item.RequestLine.Contains("\"PrepareRun\"", StringComparison.Ordinal));
            using var response = JsonDocument.Parse(frame.ResponseLine);
            candidate = response.RootElement.GetProperty("result").Clone();
            var accepted = await client.AcceptRunAsync(preview.PreparedRunId, preview.Generation, "fea10-ipc-accept");
            runId = accepted.GetProperty("run_id").GetString()!;
            var replay = await client.AcceptRunAsync(preview.PreparedRunId, preview.Generation, "fea10-ipc-accept");
            Assert.Equal(runId, replay.GetProperty("run_id").GetString());
            var freshPreview = await client.PrepareRunAsync(request.RootElement);
            var freshReplay = await client.AcceptRunAsync(freshPreview.PreparedRunId, freshPreview.Generation, "fea10-ipc-accept");
            Assert.Equal(runId, freshReplay.GetProperty("run_id").GetString());
        }
        await using (var restarted = await CoreServiceClient.StartAsync(options))
        {
            var replay = await restarted.SendAsync("AcceptRun", 12, writer =>
            {
                writer.WriteStartObject(); writer.WritePropertyName("prepared_run"); candidate.WriteTo(writer);
                writer.WriteString("idempotency_key", "fea10-ipc-accept"); writer.WriteEndObject();
            }, TimeSpan.FromSeconds(30));
            Assert.Equal(runId, replay.Result!.Value.GetProperty("run_id").GetString());
        }
        var evidence = Path.Combine(repo, "verification", "FEA-10", "ipc");
        Directory.CreateDirectory(evidence);
        await File.WriteAllTextAsync(Path.Combine(evidence, "real-ipc.txt"),
            $"DataRoot={root}\nPrepareRun -> Host candidate -> AcceptRun -> same-key replay -> Core process restart -> replay same run_id\nrun_id={runId}\nPASS\n");
    }

    private sealed class Fea10IpcFactAttribute : FactAttribute
    {
        public Fea10IpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA10_IPC") != "1")
                Skip = "set NEWMANGA_FEA10_IPC=1 for real isolated Python Core stdio IPC";
        }
    }
}
