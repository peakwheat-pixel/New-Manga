using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.CoreClient.Tests.Support;
using Xunit;

namespace NewManga.CoreClient.Tests.Bridge;

/// <summary>
/// PIPE-EXCLUSIVE-TRANSPORT-1 r1 复核 R-003: the <c>responsa id</c> validation added to
/// <c>HostBridgeClient.ParseResponse</c> had NO test — deleting it left every bridge test green.
/// These facts pin it directly.
/// </summary>
public sealed class BridgeResponseIdValidationTests
{
    [Fact]
    public void MismatchedNumericId_ThrowsMalformedResponse()
    {
        var line = "{\"id\":999,\"result\":{\"ok\":true}}";

        var error = Assert.Throws<SidecarException>(
            () => HostBridgeClient.ParseResponse("Ping", line, expectedId: 1));

        Assert.Equal(SidecarErrorCode.MalformedResponse, error.Code);
        Assert.Contains("999", error.Message, StringComparison.Ordinal);
        Assert.Contains("1", error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void MatchingNumericId_IsAccepted()
    {
        var line = "{\"id\":7,\"result\":{\"ok\":true}}";

        var result = HostBridgeClient.ParseResponse("Ping", line, expectedId: 7);

        Assert.Equal(JsonValueKind.Object, result.ValueKind);
    }

    /// <summary>
    /// Known limitation (r1 复核 R-002): an id-less (or non-numeric id) response still passes — the
    /// validation is fail-open for those shapes. Pinned so a future fail-closed change is deliberate.
    /// </summary>
    [Fact]
    public void MissingId_CurrentlyFailsOpen_DocumentedLimitation()
    {
        var line = "{\"result\":{\"ok\":true}}";

        var result = HostBridgeClient.ParseResponse("Ping", line, expectedId: 1);

        Assert.Equal(JsonValueKind.Object, result.ValueKind);
    }
}

/// <summary>
/// PIPE-EXCLUSIVE-TRANSPORT-1 r1 复核 R-004: <c>CoreServiceClient.SendRawAsync</c> was put behind
/// <c>_pipeGate</c>, but no test failed when that gate was removed. This drives the raw hook concurrently
/// with a normal command and requires both to keep their own responses.
/// </summary>
public sealed class RawSendPipeExclusivityTests
{
    [SidecarFact]
    public async Task RawSendMixedWithCommands_DoesNotTripTheSharedStream()
    {
        var options = SidecarFixture.CreateCoreOptions("raw-pipe-exclusive", out var dataRoot);
        try
        {
            await using var client = await CoreServiceClient.StartAsync(options);
            Assert.True((await client.PingAsync()).Ready);

            const string rawPing =
                "{\"protocol\":\"new-manga.core\",\"version\":{\"major\":2,\"minor\":3},"
                + "\"request_id\":\"raw-1\",\"command\":\"core.ping\",\"payload\":{}}";

            var raws = Enumerable.Range(0, 6)
                .Select(i => client.SendRawAsync(rawPing.Replace("raw-1", $"raw-{i}")))
                .ToArray();
            var books = Enumerable.Range(0, 6)
                .Select(_ => client.SendAsync(
                    "ListBooks",
                    CoreProtocol.DefaultMinor,
                    WireJson.EmptyObject,
                    TimeSpan.FromSeconds(60)))
                .ToArray();

            await Task.WhenAll(raws.Cast<Task>().Concat(books.Cast<Task>()));

            foreach (var raw in raws)
            {
                Assert.Null(raw.Result.Error);
                // core.ping's result is an object with "status"; ListBooks' is an array. A crossed
                // response shows up here immediately.
                Assert.Equal(JsonValueKind.Object, raw.Result.Result!.Value.ValueKind);
            }

            foreach (var listBooks in books)
            {
                Assert.Null(listBooks.Result.Error);
                Assert.Equal(JsonValueKind.Array, listBooks.Result.Result!.Value.ValueKind);
            }
        }
        finally
        {
            try
            {
                if (Directory.Exists(dataRoot))
                {
                    Directory.Delete(dataRoot, recursive: true);
                }
            }
            catch (IOException)
            {
            }
            catch (UnauthorizedAccessException)
            {
            }
        }
    }
}
