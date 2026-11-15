using System.Diagnostics;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Transport;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// E-7 / R-005 (P1): caller-initiated cancellation must poison the channel — <b>both</b> poison sites.
///
/// <para>There are two places where a cancelled read leaves the pipe in an unknown state:</para>
/// <list type="number">
///   <item><c>ExchangeAsync</c> — the request line was already written.</item>
///   <item><c>ReadNextResponseLineAsync</c> — it is only ever called <b>after</b> an <c>ExchangeAsync</c>
///   wrote a request and returned an event frame (see <c>CoreServiceClient</c> event-skip loops), so the
///   command's real response is still unread. Cancelling here leaves that response on the wire exactly
///   like case 1.</item>
/// </list>
///
/// <para>The original R-005 fix only covered case 1. The event-skip path was missed, and its
/// "only reads, never writes, so it cannot desynchronise" justification was wrong: the write happened in
/// the preceding <c>ExchangeAsync</c>; this read is the one that has not happened yet.</para>
///
/// <para>These tests use a real child (Windows PowerShell) that never reads stdin, so
/// "request written but no response" is reproducible without the 792 MB core sidecar.</para>
/// </summary>
public sealed class SidecarCancellationPoisonTests
{
    [Fact]
    public async Task CallerCancellation_PoisonsChannel_SoTheNextExchangeFailsClosed()
    {
        var pidFile = NewPidFile();
        var spec = NeverRespondingSpec("cancel-poison", pidFile);
        await using var sidecar = await SidecarProcess.StartAsync(spec);
        await ReadPidAsync(pidFile);

        using var cancellation = new CancellationTokenSource();
        var inFlight = sidecar.ExchangeAsync(
            "{\"id\":1}",
            escapeNonAscii: false,
            TimeSpan.FromSeconds(30),
            cancellation.Token);

        // Let the request line actually reach the child's stdin before cancelling.
        await Task.Delay(500);
        cancellation.Cancel();

        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => inFlight);

        // R-005: the request was written and its response was never read, so the stream state is
        // unknown. The channel MUST be poisoned now, and the next exchange must fail closed instead of
        // writing another request (which would then read request #1's response as request #2's).
        var follow = await Assert.ThrowsAsync<SidecarException>(() =>
            sidecar.ExchangeAsync("{\"id\":2}", escapeNonAscii: false, TimeSpan.FromSeconds(5)));

        Assert.Equal(SidecarErrorCode.RequestTimeout, follow.Code);
        Assert.Contains("poisoned", follow.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task CallerCancellation_DuringEventSkip_PoisonsChannel()
    {
        // R-005 second poison site: ReadNextResponseLineAsync runs AFTER an ExchangeAsync already wrote
        // the request and returned an event frame; the command's real response is still unread.
        // Cancelling there must poison exactly like case 1.
        var pidFile = NewPidFile();
        var spec = OneEventThenSilentSpec("cancel-poison-eventskip", pidFile);
        await using var sidecar = await SidecarProcess.StartAsync(spec);
        await ReadPidAsync(pidFile);

        // First exchange reads the single event line the child emits.
        var eventFrame = await sidecar.ExchangeAsync(
            "{\"id\":1}",
            escapeNonAscii: false,
            TimeSpan.FromSeconds(15));
        Assert.Contains("\"event_type\"", eventFrame.ResponseLine, StringComparison.Ordinal);
        Assert.True(CoreProtocol.IsEventFrame(eventFrame.ResponseLine), "fixture line must parse as an event frame");

        using var cancellation = new CancellationTokenSource();
        var skipping = sidecar.ReadNextResponseLineAsync(TimeSpan.FromSeconds(30), cancellation.Token);

        await Task.Delay(500);
        cancellation.Cancel();

        await Assert.ThrowsAnyAsync<OperationCanceledException>(() => skipping);

        var follow = await Assert.ThrowsAsync<SidecarException>(() =>
            sidecar.ExchangeAsync("{\"id\":2}", escapeNonAscii: false, TimeSpan.FromSeconds(5)));

        Assert.Equal(SidecarErrorCode.RequestTimeout, follow.Code);
        Assert.Contains("poisoned", follow.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task Timeout_StillPoisonsChannel_Unchanged()
    {
        // Control: the pre-existing timeout path must keep poisoning (guards against a fix that
        // accidentally narrows it).
        var pidFile = NewPidFile();
        var spec = NeverRespondingSpec("timeout-poison", pidFile);
        await using var sidecar = await SidecarProcess.StartAsync(spec);
        await ReadPidAsync(pidFile);

        var timeoutFailure = await Assert.ThrowsAsync<SidecarException>(() =>
            sidecar.ExchangeAsync("{\"id\":1}", escapeNonAscii: false, TimeSpan.FromSeconds(1)));

        Assert.Equal(SidecarErrorCode.RequestTimeout, timeoutFailure.Code);

        var follow = await Assert.ThrowsAsync<SidecarException>(() =>
            sidecar.ExchangeAsync("{\"id\":2}", escapeNonAscii: false, TimeSpan.FromSeconds(5)));

        Assert.Contains("poisoned", follow.Message, StringComparison.OrdinalIgnoreCase);
    }

    private static SidecarSpec NeverRespondingSpec(string name, string pidFile) => new()
    {
        Name = name,
        ExecutablePath = PowerShellPath(),
        AdditionalArguments = new[]
        {
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            // Never reads stdin, never writes stdout; just parks so the pipe stays open.
            $"$PID | Set-Content -LiteralPath '{pidFile}'; Start-Sleep -Seconds 30",
        },
        StderrLogPath = NewStderrLog(name),
        StartupTimeout = TimeSpan.FromSeconds(10),
        RequestTimeout = TimeSpan.FromSeconds(10),
    };

    private static SidecarSpec OneEventThenSilentSpec(string name, string pidFile) => new()
    {
        Name = name,
        ExecutablePath = PowerShellPath(),
        AdditionalArguments = new[]
        {
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            // Emit exactly one line, then stay silent: models "event frame arrived, command response
            // still pending".
            $"$PID | Set-Content -LiteralPath '{pidFile}'; "
                // CoreProtocol.IsEventFrame requires an "event_type" key and NO "request_id",
                // so the fixture must emit that exact shape to be a real event frame.
                + "[Console]::Out.WriteLine('{\"event_type\":\"ReadingProgressChanged\"}'); "
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
            throw new InvalidOperationException("Windows PowerShell is required for the sidecar cancellation fixture");
        }

        return path;
    }

    private static string NewPidFile() =>
        Path.Combine(Path.GetTempPath(), "newmanga-cancel-pid-" + Guid.NewGuid().ToString("N") + ".txt");

    private static string NewStderrLog(string name)
    {
        var directory = Path.Combine(
            Path.GetTempPath(),
            "newmanga-cancel-poison",
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
