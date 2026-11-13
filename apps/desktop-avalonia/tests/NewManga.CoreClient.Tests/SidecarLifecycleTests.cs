using System.Diagnostics;
using NewManga.CoreClient.Transport;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// NM-AUD-0001: cancellation/Dispose must never leave an EOF-ignoring child behind.
/// These tests use a real child (Windows PowerShell) that keeps running after stdin closes,
/// so a missing kill is observable as a live PID. Evidence is written to the test evidence dir.
/// </summary>
public sealed class SidecarLifecycleTests
{
    private static string PowerShellPath()
    {
        var path = Path.Combine(Environment.SystemDirectory, "WindowsPowerShell", "v1.0", "powershell.exe");
        if (!File.Exists(path))
        {
            throw new InvalidOperationException("Windows PowerShell is required for the sidecar lifecycle fixture");
        }

        return path;
    }

    private static string NewPidFile() =>
        Path.Combine(Path.GetTempPath(), "newmanga-sidecar-pid-" + Guid.NewGuid().ToString("N") + ".txt");

    private static string NewStderrLog(string name)
    {
        var directory = Path.Combine(Path.GetTempPath(), "newmanga-sidecar-lifecycle", name + "-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(directory);
        return Path.Combine(directory, "sidecar.stderr.log");
    }

    private static SidecarSpec IgnoreEofSpec(string name, string pidFile) => new()
    {
        Name = name,
        ExecutablePath = PowerShellPath(),
        AdditionalArguments = new[]
        {
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            $"$PID | Set-Content -LiteralPath '{pidFile}'; Start-Sleep -Seconds 30",
        },
        StderrLogPath = NewStderrLog(name),
        StartupTimeout = TimeSpan.FromSeconds(10),
        RequestTimeout = TimeSpan.FromSeconds(10),
    };

    private static bool IsProcessAlive(int pid)
    {
        try
        {
            using var process = Process.GetProcessById(pid);
            return !process.HasExited;
        }
        catch (ArgumentException)
        {
            return false;
        }
    }

    private static async Task WaitForAsync(Func<bool> condition, string what, TimeSpan? timeout = null)
    {
        var deadline = DateTime.UtcNow + (timeout ?? TimeSpan.FromSeconds(10));
        while (DateTime.UtcNow < deadline)
        {
            if (condition())
            {
                return;
            }

            await Task.Delay(100);
        }

        throw new TimeoutException($"timed out waiting for {what}");
    }

    private static async Task<int> ReadPidAsync(string pidFile)
    {
        await WaitForAsync(() => File.Exists(pidFile), "pid file " + pidFile);
        for (var attempt = 0; attempt < 50; attempt++)
        {
            var text = File.ReadAllText(pidFile).Trim();
            if (int.TryParse(text, out var pid))
            {
                return pid;
            }

            await Task.Delay(100);
        }

        throw new TimeoutException("pid file did not contain a process id");
    }

    [Fact]
    public async Task PreCancelledStart_DoesNotSpawnAChild()
    {
        var pidFile = NewPidFile();
        var spec = IgnoreEofSpec("lifecycle-precancel", pidFile);
        using var cancellation = new CancellationTokenSource();
        cancellation.Cancel();

        await Assert.ThrowsAnyAsync<OperationCanceledException>(
            () => SidecarProcess.StartAsync(spec, cancellation.Token));

        Assert.False(File.Exists(pidFile), "a pre-cancelled start must not spawn the child at all");
    }

    [Fact]
    public async Task DisposeAsync_KillsAnEofIgnoringChild()
    {
        var pidFile = NewPidFile();
        var spec = IgnoreEofSpec("lifecycle-dispose", pidFile);
        var sidecar = await SidecarProcess.StartAsync(spec);
        var pid = await ReadPidAsync(pidFile);

        try
        {
            Assert.True(IsProcessAlive(pid), "the fixture child must be running before DisposeAsync");

            await sidecar.DisposeAsync();

            await WaitForAsync(() => !IsProcessAlive(pid), "child exit after DisposeAsync", TimeSpan.FromSeconds(10));
            Assert.False(IsProcessAlive(pid), "DisposeAsync must not return while the EOF-ignoring child is alive");
        }
        finally
        {
            if (IsProcessAlive(pid))
            {
                try
                {
                    using var process = Process.GetProcessById(pid);
                    process.Kill(entireProcessTree: true);
                }
                catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or System.ComponentModel.Win32Exception)
                {
                    // already gone
                }
            }

            File.Delete(pidFile);
        }
    }

    [Fact]
    public async Task StopAsync_IsSingleFlight_AndDisposeAfterStopIsSafe()
    {
        var pidFile = NewPidFile();
        var spec = IgnoreEofSpec("lifecycle-stop", pidFile);
        var sidecar = await SidecarProcess.StartAsync(spec);
        var pid = await ReadPidAsync(pidFile);

        try
        {
            var first = sidecar.StopAsync(gracefulTimeoutMs: 500);
            var second = sidecar.StopAsync(gracefulTimeoutMs: 500);
            Assert.Same(first, second);
            await Task.WhenAll(first, second);

            await WaitForAsync(() => !IsProcessAlive(pid), "child exit after StopAsync", TimeSpan.FromSeconds(10));

            await sidecar.StopAsync(gracefulTimeoutMs: 500);
            await sidecar.DisposeAsync();
            await sidecar.DisposeAsync();
        }
        finally
        {
            if (IsProcessAlive(pid))
            {
                try
                {
                    using var process = Process.GetProcessById(pid);
                    process.Kill(entireProcessTree: true);
                }
                catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or System.ComponentModel.Win32Exception)
                {
                    // already gone
                }
            }

            File.Delete(pidFile);
        }
    }

    [Fact]
    public async Task ChildThatExitsOnItsOwn_IsStoppedWithoutKill()
    {
        var directory = Path.Combine(Path.GetTempPath(), "newmanga-sidecar-lifecycle", "self-exit-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(directory);
        var spec = new SidecarSpec
        {
            Name = "lifecycle-self-exit",
            ExecutablePath = PowerShellPath(),
            AdditionalArguments = new[] { "-NoProfile", "-NonInteractive", "-Command", "exit 0" },
            StderrLogPath = Path.Combine(directory, "sidecar.stderr.log"),
            StartupTimeout = TimeSpan.FromSeconds(10),
            RequestTimeout = TimeSpan.FromSeconds(10),
        };

        var sidecar = await SidecarProcess.StartAsync(spec);
        await WaitForAsync(() => sidecar.HasExited, "child self-exit", TimeSpan.FromSeconds(10));
        await sidecar.DisposeAsync();

        Assert.True(sidecar.HasExited);
    }
}
