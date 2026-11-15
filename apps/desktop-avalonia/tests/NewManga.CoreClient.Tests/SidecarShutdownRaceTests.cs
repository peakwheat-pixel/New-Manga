using System.Diagnostics;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Transport;
using NewManga.CoreClient.Wire;
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

            // r1 P2-1: assert the EXACT code. SidecarErrorCode.IoFailure has no throw site anywhere in the
            // product (it only appears in the message template), so tolerating it here would be a dead
            // allowance that can never fail -- a future change could regress silently.
            Assert.Equal(SidecarErrorCode.ProcessExited, failure.Code);
        }
        finally
        {
            await sidecar.DisposeAsync();
        }
    }

    /// <summary>
    /// r1 P2-3: the "half-written response" window is NOT an unreproducible narrow race — it reproduces
    /// deterministically. The child writes a TRUNCATED JSON line and flushes it; <c>ReadLineAsync</c>
    /// returns that complete-but-invalid line, and <c>CoreProtocol.Parse</c> rejects it.
    /// </summary>
    /// <remarks>
    /// This pins the real answer to "what does an in-flight command see when shutdown lands mid-response?":
    /// not always <c>ProcessExited</c> (which is what the E-7 #5 line says) but <c>MalformedResponse</c> when
    /// the child managed to emit a partial line first. Both are typed and handleable; the point is that the
    /// E-7 wording is only accurate outside this window.
    /// </remarks>
    [Fact]
    public async Task HalfWrittenResponseLine_SurfacesMalformedResponse_NotProcessExited()
    {
        var pidFile = NewPidFile();
        var spec = HalfLineSpec("shutdown-halfline", pidFile);
        await using var sidecar = await SidecarProcess.StartAsync(spec);
        await ReadPidAsync(pidFile);

        // The child immediately emits an unterminated-JSON line (still a full *line*), then parks.
        // ExchangeAsync itself only reads a line and wraps it in a WireFrame -- the JSON rejection happens
        // in CoreProtocol.Parse, which is where CoreServiceClient calls it. So drive the same two steps.
        var frame = await sidecar.ExchangeAsync(
            "{\"id\":1}",
            escapeNonAscii: false,
            TimeSpan.FromSeconds(10));

        Assert.Equal("{\"id\":1,\"resu", frame.ResponseLine);

        var failure = Assert.Throws<SidecarException>(() => CoreProtocol.Parse(frame.ResponseLine));

        Assert.Equal(SidecarErrorCode.MalformedResponse, failure.Code);
    }

    /// <summary>
    /// r1 P2-2: the product's real shutdown path is <c>CoreServiceClient.DisposeAsync</c>
    /// (HostRuntime calls it without holding <c>_pipeGate</c>). The first test used
    /// <c>await inFlight</c> before <c>await stop</c>, which structurally avoids that path. This one
    /// disposes while an exchange is genuinely in flight.
    /// </summary>
    [Fact]
    public async Task DisposeWhileExchangeInFlight_DoesNotLeakBclException()
    {
        var pidFile = NewPidFile();
        var spec = SlowRespondingSpec("shutdown-dispose", pidFile);
        var sidecar = await SidecarProcess.StartAsync(spec);
        await ReadPidAsync(pidFile);

        var inFlight = sidecar.ExchangeAsync(
            "{\"id\":1}",
            escapeNonAscii: false,
            TimeSpan.FromSeconds(30));

        await Task.Delay(500);

        // Dispose concurrently with the in-flight exchange (the product path), then collect its outcome.
        var dispose = sidecar.DisposeAsync().AsTask();

        Exception? observed = null;
        try
        {
            await inFlight;
        }
        catch (Exception ex)
        {
            observed = ex;
        }

        await dispose;

        Assert.NotNull(observed);
        // Whatever we see must be a typed SidecarException: callers only catch that.
        var failure = Assert.IsType<SidecarException>(observed);
        Assert.Equal(SidecarErrorCode.ProcessExited, failure.Code);
    }

    private static SidecarSpec HalfLineSpec(string name, string pidFile) => new()
    {
        Name = name,
        ExecutablePath = PowerShellPath(),
        AdditionalArguments = new[]
        {
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            // Emit a truncated JSON line (no closing braces) as a complete line, then park.
            $"$PID | Set-Content -LiteralPath '{pidFile}'; "
                + "[Console]::Out.WriteLine('{\"id\":1,\"resu'); "
                + "[Console]::Out.Flush(); "
                + "Start-Sleep -Seconds 30",
        },
        StderrLogPath = NewStderrLog(name),
        StartupTimeout = TimeSpan.FromSeconds(10),
        RequestTimeout = TimeSpan.FromSeconds(10),
    };

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
