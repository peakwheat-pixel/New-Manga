using System.Text;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Tests.Support;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// AC2/AC3 against the real frozen <c>core_service.exe</c> (unlabelled copy, AC11). Every test
/// writes its raw wire evidence under verification/HOST-CORECLIENT-1/wire/ when
/// NEWMANGA_EVIDENCE_DIR is set by scripts/test.ps1.
/// </summary>
public sealed class CoreServiceIntegrationTests
{
    /// <summary>AC3 fixed vector (explicit escapes so the test never depends on editor encoding).</summary>
    public const string Ac3Title = "\u96fe\u6e2f\u6765\u4fe1\u30fb\u65e5\u672c\u8a9e\u30c6\u30b9\u30c8";

    [SidecarFact]
    public async Task Ping_ReturnsReady_WithProtocol23()
    {
        var options = SidecarFixture.CreateCoreOptions("core-ping", out var dataRoot);
        try
        {
            await using var client = await CoreServiceClient.StartAsync(options);
            var ping = await client.PingAsync();

            Assert.True(ping.Ready);
            Assert.Equal(2, ping.ProtocolMajor);
            Assert.Equal(3, ping.ProtocolMinor);
            Assert.Contains("library.list_books", ping.Capabilities);
            Assert.True(client.Wire.AllRequestsAsciiOnly);
            Assert.NotEmpty(client.Wire.Frames);

            SidecarFixture.WriteEvidenceJson("wire/core-ping.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2/AC3");
                writer.WriteBoolean("ready", ping.Ready);
                writer.WriteNumber("protocol_major", ping.ProtocolMajor);
                writer.WriteNumber("protocol_minor", ping.ProtocolMinor);
                writer.WriteString("sidecar", SidecarFixture.SidecarDirectory);
                SidecarFixture.WriteFrameSummary(writer, "frames", client.Wire.Frames);
                writer.WriteEndObject();
            });
        }
        finally
        {
            SidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [SidecarFact]
    public async Task ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped()
    {
        var options = SidecarFixture.CreateCoreOptions("core-chinese", out var dataRoot);
        try
        {
            await using var client = await CoreServiceClient.StartAsync(options);
            var created = await client.CreateBookAsync(Ac3Title);
            var books = await client.ListBooksAsync();

            Assert.Equal(Ac3Title, created.Title);
            var found = books.FirstOrDefault(book => string.Equals(book.Title, Ac3Title, StringComparison.Ordinal));
            Assert.NotNull(found);
            Assert.Equal(Ac3Title, found!.Title);

            var frames = client.Wire.Frames;
            Assert.True(client.Wire.AllRequestsAsciiOnly);
            Assert.All(frames, frame => Assert.True(frame.ResponseAsciiOnly));
            Assert.All(frames, frame => Assert.DoesNotContain('\n', frame.RequestLine));

            var createFrame = frames.First(frame => frame.RequestLine.Contains("\"command\":\"CreateBook\"", StringComparison.Ordinal));
            Assert.Contains("\\u96fe", createFrame.RequestLine, StringComparison.Ordinal);
            Assert.DoesNotContain(Ac3Title, createFrame.RequestLine, StringComparison.Ordinal);
            Assert.Contains("5c7539366665", createFrame.RequestUtf8Hex, StringComparison.Ordinal);

            var expectedHex = Convert.ToHexString(Encoding.UTF8.GetBytes(Ac3Title)).ToLowerInvariant();
            var receivedHex = Convert.ToHexString(Encoding.UTF8.GetBytes(found.Title)).ToLowerInvariant();
            Assert.Equal(expectedHex, receivedHex);

            SidecarFixture.WriteEvidenceJson("wire/core-chinese-roundtrip.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC3");
                writer.WriteString("title_expected", Ac3Title);
                writer.WriteString("title_received", found.Title);
                writer.WriteString("utf8_hex_expected", expectedHex);
                writer.WriteString("utf8_hex_received", receivedHex);
                writer.WriteBoolean("exact_match", expectedHex == receivedHex);
                writer.WriteBoolean("all_requests_ascii_only", client.Wire.AllRequestsAsciiOnly);
                writer.WriteBoolean("all_responses_ascii_only", frames.All(frame => frame.ResponseAsciiOnly));
                writer.WriteString("create_request_line", createFrame.RequestLine);
                SidecarFixture.WriteFrameSummary(writer, "frames", frames);
                writer.WriteEndObject();
            });
        }
        finally
        {
            SidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [SidecarFact]
    public async Task RawUtf8Request_ReplicatesUnknownError()
    {
        var options = SidecarFixture.CreateCoreOptions("core-raw-utf8", out var dataRoot);
        try
        {
            await using var client = await CoreServiceClient.StartAsync(options);

            // Deliberately NOT escaped: real UTF-8 bytes on the wire reproduce the historical cp936
            // failure that the ASCII-escaping layer exists to prevent.
            var rawLine =
                "{\"protocol\":\"new-manga.core\",\"version\":{\"major\":2,\"minor\":8}," +
                "\"request_id\":\"raw-1\",\"command\":\"CreateBook\",\"payload\":{\"title\":\"" + Ac3Title + "\"}}";
            var response = await client.SendRawAsync(rawLine);

            Assert.False(response.IsOk);
            Assert.NotNull(response.Error);
            Assert.Equal("UNKNOWN", response.Error!.Code);

            var rawFrame = client.Wire.Frames.Last();
            Assert.False(rawFrame.RequestAsciiOnly);
            Assert.Contains("e99bbe", rawFrame.RequestUtf8Hex, StringComparison.Ordinal);

            SidecarFixture.WriteEvidenceJson("wire/core-raw-utf8-negative.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC3-negative");
                writer.WriteString("raw_request_line", rawLine);
                writer.WriteString("raw_request_utf8_hex", rawFrame.RequestUtf8Hex);
                writer.WriteBoolean("request_ascii_only", rawFrame.RequestAsciiOnly);
                writer.WriteString("response_line", rawFrame.ResponseLine);
                writer.WriteString("error_code", response.Error.Code);
                writer.WriteEndObject();
            });
        }
        finally
        {
            SidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [SidecarFact]
    public async Task WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest()
    {
        var options = SidecarFixture.CreateCoreOptions("core-wire-shape", out var dataRoot);
        try
        {
            await using var client = await CoreServiceClient.StartAsync(options);
            await client.ListBooksAsync();

            foreach (var frame in client.Wire.Frames)
            {
                Assert.True(frame.RequestAsciiOnly);
                Assert.True(frame.ResponseAsciiOnly);
                Assert.DoesNotContain('\n', frame.RequestLine);
                Assert.DoesNotContain('\n', frame.ResponseLine);
                Assert.StartsWith("{", frame.RequestLine, StringComparison.Ordinal);
                Assert.StartsWith("{", frame.ResponseLine, StringComparison.Ordinal);
                Assert.Matches("^[0-9a-f]+$", frame.RequestUtf8Hex);
            }

            SidecarFixture.WriteEvidenceJson("wire/core-wire-shape.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2");
                writer.WriteNumber("frame_count", client.Wire.Count);
                SidecarFixture.WriteFrameSummary(writer, "frames", client.Wire.Frames);
                writer.WriteEndObject();
            });
        }
        finally
        {
            SidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [Fact]
    public void CurrentProcessIntegrityLevel_IsReadableOnWindows()
    {
        var level = ProcessIntegrity.GetForCurrentProcess();
        Assert.NotEqual(ProcessIntegrityLevel.Unknown, level);
    }
}
