using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Tests;

public sealed class AsciiWireTests
{
    [Fact]
    public void AsciiText_IsUnchanged()
    {
        const string input = "{\"command\":\"core.ping\"}";
        Assert.Equal(input, AsciiWire.Escape(input));
        Assert.True(AsciiWire.IsAscii(AsciiWire.Escape(input)));
    }

    [Fact]
    public void ChineseText_IsEscapedAsUnicode()
    {
        const string input = "雾港来信・日本語テスト";
        var escaped = AsciiWire.Escape(input);

        Assert.Equal(
            "\\u96fe\\u6e2f\\u6765\\u4fe1\\u30fb\\u65e5\\u672c\\u8a9e\\u30c6\\u30b9\\u30c8",
            escaped);
        Assert.True(AsciiWire.IsAscii(escaped));
        Assert.False(AsciiWire.IsAscii(input));
    }

    [Fact]
    public void EscapedText_IsJsonRoundTrippable()
    {
        const string input = "雾港来信・日本語テスト";
        var escaped = AsciiWire.Escape(input);
        var json = "{\"title\":\"" + escaped + "\"}";

        using var document = JsonDocument.Parse(json);
        Assert.Equal(input, document.RootElement.GetProperty("title").GetString());
    }

    [Fact]
    public void AstralCharacters_UseSurrogatePairEscapes()
    {
        const string input = "😀";
        var escaped = AsciiWire.Escape(input);

        Assert.Equal("\\ud83d\\ude00", escaped);
        Assert.True(AsciiWire.IsAscii(escaped));
        using var document = JsonDocument.Parse("\"" + escaped + "\"");
        Assert.Equal(input, document.RootElement.GetString());
    }

    [Fact]
    public void Hex_IsLowercaseUtf8()
    {
        Assert.Equal("e99bbe", AsciiWire.Hex(AsciiWire.ToBytes("雾")));
    }
}

public sealed class CoreProtocolTests
{
    [Fact]
    public void RequestEnvelope_MatchesProtocol23()
    {
        var line = CoreProtocol.BuildRequest("req-1", "core.ping");

        using var document = JsonDocument.Parse(line);
        var root = document.RootElement;
        Assert.Equal("new-manga.core", root.GetProperty("protocol").GetString());
        Assert.Equal(2, root.GetProperty("version").GetProperty("major").GetInt32());
        Assert.Equal(3, root.GetProperty("version").GetProperty("minor").GetInt32());
        Assert.Equal("req-1", root.GetProperty("request_id").GetString());
        Assert.Equal("core.ping", root.GetProperty("command").GetString());
        Assert.Equal(JsonValueKind.Object, root.GetProperty("payload").ValueKind);
    }

    [Fact]
    public void CreateRequest_UsesMinor8()
    {
        var line = CoreProtocol.BuildCreateRequest("c-1", "CreateBook", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("title", "雾港来信・日本語テスト");
            writer.WriteEndObject();
        });
        var escaped = AsciiWire.Escape(line);

        Assert.True(AsciiWire.IsAscii(escaped));
        using var document = JsonDocument.Parse(escaped);
        Assert.Equal(8, document.RootElement.GetProperty("version").GetProperty("minor").GetInt32());
        Assert.Contains("\\u96fe", escaped, StringComparison.Ordinal);
    }

    [Fact]
    public void ParseResponse_ReadsResultAndError()
    {
        var ok = CoreProtocol.Parse("{\"protocol\":\"new-manga.core\",\"request_id\":\"1\",\"result\":{\"status\":\"ready\"},\"error\":null}");
        Assert.True(ok.IsOk);
        Assert.Equal("ready", ok.Result!.Value.GetProperty("status").GetString());

        var error = CoreProtocol.Parse("{\"request_id\":\"2\",\"result\":null,\"error\":{\"code\":\"UNKNOWN\",\"category\":\"unknown\",\"retryable\":\"unknown\"}}");
        Assert.False(error.IsOk);
        Assert.Equal("UNKNOWN", error.Error!.Code);
    }

    [Fact]
    public void ParseResponse_RejectsMalformedJson_AsTypedError()
    {
        var error = Assert.Throws<SidecarException>(() => CoreProtocol.Parse("not-json"));
        Assert.Equal(SidecarErrorCode.MalformedResponse, error.Code);
    }
}

public sealed class ProcessIntegrityTests
{
    [Theory]
    [InlineData(ProcessIntegrityLevel.Medium, ProcessIntegrityLevel.Medium, true)]
    [InlineData(ProcessIntegrityLevel.High, ProcessIntegrityLevel.High, true)]
    [InlineData(ProcessIntegrityLevel.Medium, ProcessIntegrityLevel.Low, false)]
    [InlineData(ProcessIntegrityLevel.Low, ProcessIntegrityLevel.Medium, false)]
    [InlineData(ProcessIntegrityLevel.Unknown, ProcessIntegrityLevel.Unknown, false)]
    public void Compare_RequiresEqualityAndKnownLevels(ProcessIntegrityLevel parent, ProcessIntegrityLevel child, bool expected)
    {
        Assert.Equal(expected, ProcessIntegrity.Compare(parent, child).Matches);
    }

    [Theory]
    [InlineData(0x1000u, ProcessIntegrityLevel.Low)]
    [InlineData(0x2000u, ProcessIntegrityLevel.Medium)]
    [InlineData(0x3000u, ProcessIntegrityLevel.High)]
    [InlineData(0x4000u, ProcessIntegrityLevel.System)]
    [InlineData(0x1234u, ProcessIntegrityLevel.Unknown)]
    public void FromRid_MapsWindowsIntegrityLevels(uint rid, ProcessIntegrityLevel expected)
    {
        Assert.Equal(expected, ProcessIntegrity.FromRid(rid));
    }
}
