using NewManga.CoreClient.Diagnostics;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// AC2/AC3/AC4/AC5 end-to-end through the Host layer against the real frozen sidecars. All tests use
/// an isolated data root, a unique Local mutex and the unlabelled sidecar copy (AC11).
/// </summary>
public sealed class HostRuntimeIntegrationTests
{
    public const string Ac3Title = "\u96fe\u6e2f\u6765\u4fe1\u30fb\u65e5\u672c\u8a9e\u30c6\u30b9\u30c8";

    [Fact]
    public async Task ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked()
    {
        var options = HostFixture.CreateOptions("runtime-readonly", out var dataRoot);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);

            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(HostMode.ReadOnlyUntilParity, runtime.Mode);
            Assert.False(runtime.Policy.WritesAllowed);
            Assert.NotNull(runtime.CoreService);
            Assert.NotNull(runtime.HostBridge);
            Assert.NotEmpty(runtime.CoreService!.Wire.Frames);
            Assert.NotEmpty(runtime.HostBridge!.Wire.Frames);

            var books = await runtime.ListBooksAsync();
            Assert.Empty(books);

            var write = await Assert.ThrowsAsync<ReadOnlyHostException>(() => runtime.CreateBookAsync(Ac3Title));
            Assert.Equal("HOST_READ_ONLY", write.Code);

            Assert.True(File.Exists(runtime.Log.HostLogPath));
            Assert.True(File.Exists(Path.Combine(runtime.WireEvidenceDirectory, "core-service.ndjson")));
            Assert.True(File.Exists(Path.Combine(runtime.WireEvidenceDirectory, "host-bridge.ndjson")));

            HostFixture.WriteEvidenceJson("host/runtime-readonly.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC4/AC5");
                writer.WriteBoolean("ready", runtime.Result.IsReady);
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("write_blocked_code", write.Code);
                writer.WriteNumber("core_wire_frames", runtime.CoreService!.Wire.Count);
                writer.WriteNumber("bridge_wire_frames", runtime.HostBridge!.Wire.Count);
                writer.WriteBoolean("all_core_requests_ascii", runtime.CoreService!.Wire.AllRequestsAsciiOnly);
                writer.WriteString("host_log", "host-logs/runtime-readonly/host.log");
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [Fact]
    public async Task ParityReached_ChineseRoundTrip_IsExact_ThroughHost()
    {
        var options = HostFixture.CreateOptions("runtime-parity-roundtrip", out var dataRoot, parity: true);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(HostMode.ReadWrite, runtime.Mode);

            var result = await runtime.RoundTripChineseTitleAsync(Ac3Title);
            Assert.True(result.ExactMatch, $"expected={result.Expected} received={result.Received}");

            var books = await runtime.ListBooksAsync();
            Assert.Contains(books, book => string.Equals(book.Title, Ac3Title, StringComparison.Ordinal));

            HostFixture.WriteEvidenceJson("host/runtime-chinese-roundtrip.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC3");
                writer.WriteString("title_expected", result.Expected);
                writer.WriteString("title_received", result.Received);
                writer.WriteBoolean("exact_match", result.ExactMatch);
                writer.WriteNumber("book_count", books.Count);
                writer.WriteBoolean("all_requests_ascii_only", runtime.CoreService!.Wire.AllRequestsAsciiOnly);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [Fact]
    public async Task MissingSidecarDirectory_IsTypedFailure_NoThrow()
    {
        var emptySidecarDirectory = Path.Combine(
            Path.GetTempPath(),
            "newmanga-empty-sidecar-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(emptySidecarDirectory);
        try
        {
            var options = HostFixture.CreateOptions(
                "runtime-missing-sidecar",
                out var dataRoot,
                sidecarDirectoryOverride: emptySidecarDirectory);
            try
            {
                await using var runtime = await HostRuntime.StartAsync(options);
                Assert.Equal(HostStatus.Failed, runtime.Result.Status);
                Assert.Equal(SidecarErrorCode.SidecarBundleMissing.ToString(), runtime.Result.ErrorCode);
                Assert.Null(runtime.CoreService);
                Assert.Null(runtime.HostBridge);
                Assert.Contains("核心服务", runtime.Result.UserMessage!, StringComparison.Ordinal);
                Assert.DoesNotContain(dataRoot, runtime.Result.UserMessage!, StringComparison.OrdinalIgnoreCase);

                HostFixture.WriteEvidenceJson("host/runtime-missing-sidecar.json", writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("ac", "AC4");
                    writer.WriteString("status", runtime.Result.Status.ToString());
                    writer.WriteString("error_code", runtime.Result.ErrorCode);
                    writer.WriteString("user_message", runtime.Result.UserMessage);
                    writer.WriteBoolean("ui_message_has_no_absolute_path", !runtime.Result.UserMessage!.Contains('\\'));
                    writer.WriteEndObject();
                });
            }
            finally
            {
                HostFixture.TryDeleteDirectory(dataRoot);
            }
        }
        finally
        {
            HostFixture.TryDeleteDirectory(emptySidecarDirectory);
        }
    }

    [Fact]
    public async Task SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars()
    {
        var mutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12];
        var options = HostFixture.CreateOptions("runtime-second-instance", out var dataRoot, mutexName: mutexName);
        try
        {
            Assert.True(SingleInstanceGuard.TryAcquire(mutexName, out var holder));
            try
            {
                await using var runtime = await HostRuntime.StartAsync(options);
                Assert.Equal(HostStatus.AlreadyRunning, runtime.Result.Status);
                Assert.Equal("HOST_ALREADY_RUNNING", runtime.Result.ErrorCode);
                Assert.Null(runtime.CoreService);
                Assert.Null(runtime.HostBridge);

                HostFixture.WriteEvidenceJson("host/second-instance.json", writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("ac", "AC5");
                    writer.WriteString("mutex", mutexName);
                    writer.WriteString("status", runtime.Result.Status.ToString());
                    writer.WriteString("error_code", runtime.Result.ErrorCode);
                    writer.WriteBoolean("sidecars_spawned", runtime.CoreService is not null);
                    writer.WriteEndObject();
                });
            }
            finally
            {
                holder!.Dispose();
            }
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }
}
