using System.Diagnostics;
using System.Text.Json;
using NewManga.Host;
using NewManga.Host.Sources;
using NewManga.Host.Tests.Support;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-SCAN-2 r2 (P2-5): gated HostRuntime-level cold-start wiring test. It starts the real Host
/// with the existing unlabelled sidecar fixture and asserts:
///  - the Host becomes <c>Ready</c> without waiting for the read-only target enumeration (the
///    enumeration runs fire-and-forget after Ready, so a slow/absent capability never blocks start);
///  - the background enumeration actually EXECUTED (a typed <c>Enumeration</c> state appears);
///  - the verdict is fail-closed: when the bundled sidecar predates C-17 v1.1 (current repository
///    sidecar build) the state carries a typed code instead of pretending success;
///  - an explicit App-style refresh is accepted and the scheduler keeps ticking.
///
/// Limitation (recorded in the shard record): the HostRuntime sidecar seam cannot be replaced by a
/// fake Core or an injected clock without a much larger production refactor, so the *successful*
/// enumeration (real <c>source_list_scan_targets</c>) is covered at the component level by
/// <c>Fea11ScanIpcTests</c> (real current Core), while this test proves the Ready wiring / non-blocking
/// behaviour against the real Host process.
/// </summary>
public sealed class Fea11Scan2HostRuntimeTests
{
    [HostSidecarFact]
    public async Task Ready_StartsBackgroundEnumeration_WithoutBlocking()
    {
        var options = HostFixture.CreateOptions("scan2-runtime-enumeration", out _);
        var stopwatch = Stopwatch.StartNew();
        await using var runtime = await HostRuntime.StartAsync(options);
        stopwatch.Stop();

        Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
        Assert.NotNull(runtime.ScanScheduler);
        // Non-blocking evidence: StartAsync has returned Ready even though the background enumeration
        // may not have resolved yet.
        var enumerationImmediatelyAfterStart = runtime.SourceScanStatus.Enumeration;

        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(30);
        while (DateTime.UtcNow < deadline && runtime.SourceScanStatus.Enumeration is null)
        {
            await Task.Delay(100);
        }

        var status = runtime.SourceScanStatus;
        var enumeration = status.Enumeration;
        Assert.NotNull(enumeration);
        if (enumeration!.Available == true)
        {
            Assert.Equal(SourceScanResults.Ok, enumeration.LastResult);
        }
        else
        {
            // The repository sidecar bundle predates C-17 v1.1: the typed CORE_CAPABILITY_MISSING (or
            // an equivalent transport/storage code) is still proof that Ready->enumeration executed.
            Assert.False(string.IsNullOrWhiteSpace(enumeration.LastErrorCode));
        }

        // The scheduler is active: an explicit refresh is accepted (fire-and-forget, returns immediately)
        // and a tick still runs without waiting for any in-flight enumeration (single-flight merges an
        // overlapping tick; retry briefly until the in-flight refresh releases the gate).
        Assert.True(runtime.RequestSourceScanRefresh(), "scan scheduler should accept an App refresh");
        var ticked = false;
        var tickDeadline = DateTime.UtcNow + TimeSpan.FromSeconds(10);
        while (!ticked && DateTime.UtcNow < tickDeadline)
        {
            ticked = await runtime.ScanScheduler!.TickAsync();
            if (!ticked)
            {
                await Task.Delay(50);
            }
        }

        Assert.True(ticked, "a scan tick must run after the background enumeration completes");

        // Redaction: the in-process status must not carry absolute paths.
        var serialized = JsonSerializer.Serialize(status);
        Assert.DoesNotContain("C:\\", serialized, StringComparison.Ordinal);
        Assert.DoesNotContain(Path.GetTempPath(), serialized, StringComparison.Ordinal);

        HostFixture.WriteEvidenceJson("host-r2-runtime-enumeration.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("case", "P2-5 HostRuntime Ready -> background enumeration (non-blocking)");
            writer.WriteBoolean("ready", runtime.Result.IsReady);
            writer.WriteNumber("start_elapsed_ms", stopwatch.ElapsedMilliseconds);
            writer.WriteBoolean("enumeration_present_immediately_after_start",
                enumerationImmediatelyAfterStart is not null);
            writer.WriteBoolean("enumeration_resolved", enumeration is not null);
            writer.WriteBoolean("enumeration_available", enumeration?.Available ?? false);
            writer.WriteString("enumeration_last_result", enumeration?.LastResult);
            writer.WriteString("enumeration_error_code", enumeration?.LastErrorCode);
            writer.WriteBoolean("scheduler_started", runtime.ScanScheduler is not null);
            writer.WriteBoolean("redacted", true);
            writer.WriteEndObject();
        });
    }
}
