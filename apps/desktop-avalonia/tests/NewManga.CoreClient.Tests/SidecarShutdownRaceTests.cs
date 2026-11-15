using System.Diagnostics;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Transport;
using Xunit;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// E-7 #5 diagnostics: <c>StopAsync</c>/<c>DisposeAsync</c> do not take the exchange lease, so a command
/// that is in flight when shutdown starts observes whatever the shutdown does to the pipe.
///
/// <para>Before changing anything, these tests <b>record what actually happens</b>: which exception type
/// and which error code an in-flight exchange gets when a concurrent <c>StopAsync</c> tears the process
/// down. The claim to verify is the one in the E-7 enumeration: "in-flight commands get
/// <c>ProcessExited</c>". If the observed failure is something else (e.g. <c>MalformedResponse</c> from a
/// half-written line, or an <c>ObjectDisposedException</c> leaking to callers), the real defect — and the
/// fix — are different from what the inventory says.</para>
///
/// <para>Fixture: Windows PowerShell child that waits, then writes one response line. Stopping it while the
/// read is pending is the interesting case.</para>
/// </summary>
public sealed class SidecarShutdownRaceTests
{
    [Fact]
    public async Task InFlightExchange_DuringConcurrentStop_ObservesADefinedFailure()
    {
        var pidFile = NewPidFile();
        // Child answers after 5s; we stop it at ~0.5s, so the response never arrives.
        var spec = SlowRespondingSpec("shutdown-race", pidFile);
        var sidecar = await SidecarProcess.StartAsync(spec);
        try
        {
            await ReadPidAsync(pidFile);

            var inFlight = sidecar.ExchangeAsync(
                "{\"id\":1}",
                escapeNonAscii: false,
                TimeSpan.FromSeconds(30));

            await Task.Delay(500);

            // Concurrent shutdown while the exchange is parked on ReadLineAsync.
            var stop = sidecar.StopAsync(gracefulTimeoutMs: 200);

            Exception? observed = null;
            try
            {
                await inFlight;
            }
            catch (Exception ex)
            {
                observed = ex;
            }

            await stop;

            Assert.NotNull(observed);

            // Record what the caller actually sees. This is a diagnostic assertion: it pins the CURRENT
            // behaviour so a future change cannot silently alter it without updating this test.
            var detail = observed!.GetType().Name + ": " + observed.Message;
            if (observed is SidecarException sidecarFailure)
            {
                detail += " [code=" + sidecarFailure.Code + "]";
                // E-7 #5 claims in-flight commands get ProcessExited; record whatever we actually see.
                // Measured 2026-11-16 on this head: the in-flight exchange surfaces ProcessExited --
                // i.e. the E-7 #5 description is accurate AND the failure is a typed SidecarException that
                // callers can handle. Pinning the exact code keeps a future change from silently
                // replacing it with something misleading (e.g. MalformedResponse from a half-written line).
                Assert.Equal(SidecarErrorCode.ProcessExited, sidecarFailure.Code);
            }
            else
            {
                // A raw BCL exception (ObjectDisposedException / IOException / OperationCanceledException)
                // escaping to callers would itself be a defect: callers only handle SidecarException.
                Assert.Fail(
                    "in-flight exchange during shutdown leaked a non-SidecarException to the caller: " + detail);
            }
        }
        finally
        {
            await sidecar.DisposeAsync();
        }
    }

    [Fact]
    public async Task ExchangeStartedAfterStop_DoesNotReadFromADeadPipe()
    {
        var pidFile = NewPidFile();
        var spec = SlowRespondingSpec("shutdown-after", pidFile);
        var sidecar = await SidecarProcess.StartAsync(spec);
        try
        {
            await ReadPidAsync(pidFile);
            await sidecar.StopAsync(gracefulTimeoutMs: 200);

            // After a completed stop, a new exchange must fail fast with a typed error, not hang or leak a
            // raw BCL exception.
            var failure = await Assert.ThrowsAsync<SidecarException>(() =>
                sidecar.ExchangeAsync("{\"id\":2}", escapeNonAscii: false, TimeSpan.FromSeconds(5)));

            Assert.True(
                failure.Code is SidecarErrorCode.ProcessExited or SidecarErrorCode.IoFailure,
                "post-stop exchange surfaced an unexpected code: " + failure.Code);
        }
        finally
        {
            await sidecar.DisposeAsync();
        }
    }

    private static SidecarSpec SlowRespondingSpec(string name, string pidFile) => new()
    {
        Name = name,
        ExecutablePath = PowerShellPath(),
        AdditionalArguments = new[]
        {
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            // Publish the pid first (the harness waits for it), then answer late so a concurrent stop
            // always finds the read still pending.
            $"$PID | Set-Content -LiteralPath '{pidFile}'; "
                + "Start-Sleep -Seconds 5; "
                + "[Console]::Out.WriteLine('{\"id\":1,\"result\":null}'); "
                + "[Console]::Out.Flush(); "
                + "Start-Sleep -Seconds 30",
        },
        StderrLogPath = NewStderrLog(name),
        StartupTimeout = TimeSpan.FromSeconds(10),
        RequestTimeout = TimeSpan.FromSeconds(10),
    };

    private static string PowerShellPath()
    {
        var path = Path.Combine(Environment.SystemDirectory, "WindowsPowerShell", "v1.0", "powershell.exe");
        if (!File.Exists(path))
        {
            throw new InvalidOperationException("Windows PowerShell is required for the sidecar shutdown fixture");
        }

        return path;
    }

    private static string NewPidFile() =>
        Path.Combine(Path.GetTempPath(), "newmanga-shutdown-pid-" + Guid.NewGuid().ToString("N") + ".txt");

    private static string NewStderrLog(string name)
    {
        var directory = Path.Combine(
            Path.GetTempPath(),
            "newmanga-shutdown-race",
            name + "-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(directory);
        return Path.Combine(directory, "sidecar.stderr.log");
    }

    private static async Task<int> ReadPidAsync(string pidFile)
    {
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(10);
        while (DateTime.UtcNow < deadline)
        {
            if (File.Exists(pidFile))
            {
                var text = (await File.ReadAllTextAsync(pidFile)).Trim();
                if (int.TryParse(text, out var pid) && pid > 0)
                {
                    return pid;
                }
            }

            await Task.Delay(100);
        }

        throw new TimeoutException("pid file did not contain a process id");
    }
}
