using System.Diagnostics;
using NewManga.CoreClient.Diagnostics;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// AC5 real-machine evidence: a process literally named <c>new-manga.exe</c> is detected and forces
/// the new host into read-only mode (the chosen coexistence policy), and the default
/// <c>Global\NewManga.Host</c> mutex either works or falls back to <c>Local\NewManga.Host</c>.
/// </summary>
public sealed class LegacyShellRealTests
{
    [Fact]
    public void RealProcessNamedNewManga_IsDetectedByProbe()
    {
        var (process, tempDirectory) = StartFakeLegacyShell();
        try
        {
            var state = new LegacyShellDetector().Detect();
            Assert.True(state.Detected);
            Assert.Contains(process.Id, state.ProcessIds);

            HostFixture.WriteEvidenceJson("legacy-shell/detected.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC5");
                writer.WriteString("probe", "Process.GetProcessesByName(\"new-manga\")");
                writer.WriteBoolean("detected", state.Detected);
                writer.WriteStartArray("pids");
                foreach (var id in state.ProcessIds)
                {
                    writer.WriteNumberValue(id);
                }

                writer.WriteEndArray();
                writer.WriteEndObject();
            });
        }
        finally
        {
            Kill(process);
            HostFixture.TryDeleteDirectory(tempDirectory);
        }
    }

    [Fact]
    public async Task LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites()
    {
        var (process, tempDirectory) = StartFakeLegacyShell();
        var options = HostFixture.CreateOptions(
            "runtime-legacy-running",
            out var dataRoot,
            parity: true,
            sidecarDirectoryOverride: HostFixture.SidecarDirectory,
            detectLegacyShell: true);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);

            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(HostMode.ReadOnlyLegacyShellRunning, runtime.Mode);
            Assert.True(runtime.LegacyShell.Detected);
            Assert.False(runtime.Policy.WritesAllowed);
            var write = await Assert.ThrowsAsync<ReadOnlyHostException>(
                () => runtime.CreateBookAsync(HostRuntimeIntegrationTests.Ac3Title));
            Assert.Equal("HOST_READ_ONLY", write.Code);

            HostFixture.WriteEvidenceJson("legacy-shell/runtime-readonly.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC5");
                writer.WriteBoolean("ready", runtime.Result.IsReady);
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("legacy_detected", runtime.LegacyShell.Detected);
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("write_blocked_code", write.Code);
                writer.WriteEndObject();
            });
        }
        finally
        {
            Kill(process);
            HostFixture.TryDeleteDirectory(tempDirectory);
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [Fact]
    public void DefaultGlobalMutex_AcquiresOrFallsBackToLocal()
    {
        Assert.True(SingleInstanceGuard.TryAcquire(SingleInstanceGuard.DefaultMutexName, out var guard));
        try
        {
            Assert.NotNull(guard);
            Assert.Contains(
                guard!.Name,
                new[] { MutexNames.GlobalDefault, MutexNames.LocalFallback });
            Assert.Equal(guard.Name, guard.Name);
        }
        finally
        {
            guard!.Dispose();
        }
    }

    private static (Process Process, string TempDirectory) StartFakeLegacyShell()
    {
        var tempDirectory = Path.Combine(
            Path.GetTempPath(),
            "newmanga-legacy-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(tempDirectory);
        var fakeLegacy = Path.Combine(tempDirectory, "new-manga.exe");
        File.Copy(Path.Combine(Environment.SystemDirectory, "cmd.exe"), fakeLegacy);

        var process = Process.Start(new ProcessStartInfo
        {
            FileName = fakeLegacy,
            Arguments = "/c timeout /t 30 /nobreak >nul",
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        }) ?? throw new InvalidOperationException("could not start fake legacy process");

        var deadline = Environment.TickCount64 + 5000;
        while (Environment.TickCount64 < deadline)
        {
            var detected = new LegacyShellDetector().Detect();
            if (detected.Detected && detected.ProcessIds.Contains(process.Id))
            {
                return (process, tempDirectory);
            }

            Thread.Sleep(100);
        }

        Kill(process);
        throw new InvalidOperationException("fake legacy process never appeared in the process probe");
    }

    private static void Kill(Process process)
    {
        try
        {
            if (!process.HasExited)
            {
                process.Kill(entireProcessTree: true);
                process.WaitForExit(5000);
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
        {
            // already gone
        }
        finally
        {
            process.Dispose();
        }
    }
}
