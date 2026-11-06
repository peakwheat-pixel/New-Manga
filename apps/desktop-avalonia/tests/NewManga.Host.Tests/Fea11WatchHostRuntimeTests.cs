using System.Text.Json;
using NewManga.Host;
using NewManga.Host.Sources;
using NewManga.Host.Tests.Support;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-WATCH-1 (AC-W1 gated smoke): the real HostRuntime lifecycle end-to-end — Ready → watcher
/// armed, a registered target of an isolated file tree becomes watched, a real file event produces a
/// debounced hint, and Dispose disarms the watcher before the scheduler goes away (zero hints after).
///
/// Limitation (recorded in the shard record): the HostRuntime seam has no fake-Core/clock injection, so
/// the deterministic debounce/overflow/budget assertions live in <c>SourceWatcherTests</c> /
/// <c>SourceScanSchedulerTests</c>; this gated test proves the production wiring and the real
/// <see cref="System.IO.FileSystemWatcher"/> arm path over an isolated temp tree (no user data).
/// </summary>
public sealed class Fea11WatchHostRuntimeTests
{
    [HostSidecarFact]
    public async Task Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms()
    {
        var options = HostFixture.CreateOptions("watch-runtime", out var dataRoot);
        await using var runtime = await HostRuntime.StartAsync(options);
        Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
        Assert.NotNull(runtime.Watcher);
        Assert.NotNull(runtime.Registry);

        var watchStatus = runtime.SourceScanStatus.Watcher;
        Assert.NotNull(watchStatus);
        Assert.True(watchStatus!.Enabled);
        Assert.True(watchStatus.Armed);

        var sourceRoot = Path.Combine(dataRoot, "watch-source");
        Directory.CreateDirectory(sourceRoot);
        var sourceFile = Path.Combine(sourceRoot, "book.zip");
        await File.WriteAllBytesAsync(sourceFile, new byte[] { 1, 2, 3 });
        runtime.Registry!.Register("watch-fixture", new[] { sourceRoot });
        Assert.True(runtime.RegisterSourceScanTarget(
            "src-watch-fixture", sourceFile, new[] { "book-watch" }));

        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(15);
        while (DateTime.UtcNow < deadline && runtime.SourceScanStatus.Watcher?.Active < 1)
        {
            await Task.Delay(25);
        }

        var armedStatus = runtime.SourceScanStatus.Watcher;
        Assert.NotNull(armedStatus);
        Assert.True(armedStatus!.Active >= 1, "expected at least one armed watch over the isolated root");

        // Real OS event -> debounce (default 2000ms) -> hint; no user data involved, isolated temp tree.
        await Task.Delay(250);
        await File.WriteAllBytesAsync(sourceFile, new byte[] { 9, 9, 9, 9 });
        var hintDeadline = DateTime.UtcNow + TimeSpan.FromSeconds(20);
        while (DateTime.UtcNow < hintDeadline && (runtime.SourceScanStatus.Watcher?.HintCount ?? 0) < 1)
        {
            await Task.Delay(50);
        }

        var hintedStatus = runtime.SourceScanStatus.Watcher;
        Assert.NotNull(hintedStatus);
        Assert.True(hintedStatus!.HintCount >= 1, "expected a debounced hint from the real file event");
        Assert.Equal(0, hintedStatus.OverflowCount);

        // Redaction: the watcher slice of the status must not leak absolute paths.
        var serialized = JsonSerializer.Serialize(hintedStatus);
        Assert.DoesNotContain("C:\\", serialized, StringComparison.Ordinal);
        Assert.DoesNotContain(dataRoot, serialized, StringComparison.Ordinal);
        Assert.DoesNotContain("book.zip", serialized, StringComparison.Ordinal);

        HostFixture.WriteEvidenceJson("host-watch-runtime.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("case", "AC-W1 gated HostRuntime Ready->arm->hint->dispose");
            writer.WriteBoolean("ready", runtime.Result.IsReady);
            writer.WriteBoolean("watcher_attached", runtime.Watcher is not null);
            writer.WriteBoolean("armed", watchStatus.Armed);
            writer.WriteNumber("active_watches", armedStatus.Active);
            writer.WriteNumber("hint_count", hintedStatus.HintCount);
            writer.WriteNumber("overflow_count", hintedStatus.OverflowCount);
            writer.WriteBoolean("redacted", true);
            writer.WriteEndObject();
        });

        await runtime.DisposeAsync();
        Assert.Null(runtime.Watcher);
        Assert.Null(runtime.ScanScheduler);
        Assert.Null(runtime.SourceScanStatus.Watcher); // no watcher surface after disarm
    }
}
