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
    /// E-7 bridge-side fail-closed (Codex ruling 2026-11-16 §4): this used to pin the FAIL-OPEN behaviour
    /// for an id-less response. The ruling made a production response require the exact Int32 id, so a
    /// missing id is now a typed rejection. Migrated from <c>MissingId_CurrentlyFailsOpen_DocumentedLimitation</c>.
    /// </summary>
    [Fact]
    public void MissingId_ThrowsMalformedResponse()
    {
        var line = "{\"result\":{\"ok\":true}}";

        var error = Assert.Throws<SidecarException>(
            () => HostBridgeClient.ParseResponse("Ping", line, expectedId: 1));

        Assert.Equal(SidecarErrorCode.MalformedResponse, error.Code);
        Assert.Contains("missing id", error.Message, StringComparison.Ordinal);
        Assert.Contains("1", error.Message, StringComparison.Ordinal);
    }

    /// <summary>
    /// The ruling's hole 2 also covers "present but unusable": a non-Int32 id/kind must be rejected, not
    /// silently accepted. (<c>null</c> and strings/objects/arrays/floats are all non-Int32 numbers here.)
    /// </summary>
    [Theory]
    [InlineData("null")]
    [InlineData("\"1\"")]
    [InlineData("true")]
    [InlineData("{}")]
    [InlineData("[]")]
    [InlineData("1.5")]
    [InlineData("99999999999999999999")]
    public void NonInt32Id_ThrowsMalformedResponse(string idJson)
    {
        var line = "{\"id\":" + idJson + ",\"result\":{\"ok\":true}}";

        var error = Assert.Throws<SidecarException>(
            () => HostBridgeClient.ParseResponse("Ping", line, expectedId: 1));

        Assert.Equal(SidecarErrorCode.MalformedResponse, error.Code);
        Assert.Contains("not an Int32", error.Message, StringComparison.Ordinal);
    }

    /// <summary>
    /// Ruling §4 / hole 1: <c>expectedId: null</c> (the <c>raw</c> call site) must KEEP the
    /// observe-whatever-came-back semantics — an id-less frame is still returned there.
    /// </summary>
    [Fact]
    public void RawWithNoExpectedId_StillObservesIdlessFrame()
    {
        const string line = "{\"result\":{\"ok\":true}}";

        var result = HostBridgeClient.ParseResponse("raw", line);

        Assert.Equal(JsonValueKind.Object, result.ValueKind);
    }
}

/// <summary>
/// PIPE-EXCLUSIVE-TRANSPORT-1 r1 复核 R-004: <c>CoreServiceClient.SendRawAsync</c> was put behind
/// the client's own gate (<c>_pipeGate</c>, since removed by E-7 #1 in favour of the transport lease), but no test failed when that gate was removed. This drives the raw hook concurrently
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
