using System.Text;
using System.Text.Json;
using NewManga.CoreClient.Transport;
using NewManga.CoreClient.Wire;
using Xunit;
using NewManga.CoreClient.Tests.Support;

namespace NewManga.CoreClient.Tests;

public sealed class WireLogSourceRedactionTests
{
    [Fact]
    public void SourceSecretsAndPathsAreRemovedFromFramesAndHex()
    {
        var log = new WireLog();
        const string line = "{\"command\":\"RegisterSourceReadGrant\",\"payload\":{\"secret_ref\":{\"token\":\"sentinel-token\",\"path\":\"C:/private/source-secret.bin\"},\"signing_key\":\"sentinel-signing-key\",\"host_session_credential\":\"sentinel-credential\",\"scope\":{\"entries\":[{\"path\":\"C:/private/page.png\"}]}}}";
        log.Add(new WireFrame("core_service", line, line, "unsafe-raw-hex", "unsafe-raw-hex", true, true, 1, DateTimeOffset.UtcNow));
        var frame = Assert.Single(log.Frames);
        foreach (var raw in new[] { "sentinel-token", "source-secret.bin", "sentinel-signing-key", "sentinel-credential", "C:/private", "unsafe-raw-hex" })
        {
            Assert.DoesNotContain(raw, frame.RequestLine); Assert.DoesNotContain(raw, frame.ResponseLine);
            Assert.DoesNotContain(raw, Encoding.UTF8.GetString(Convert.FromHexString(frame.RequestUtf8Hex)));
            Assert.DoesNotContain(raw, Encoding.UTF8.GetString(Convert.FromHexString(frame.ResponseUtf8Hex)));
        }
        using var request = JsonDocument.Parse(frame.RequestLine);
        Assert.Equal("[REDACTED]", request.RootElement.GetProperty("payload").GetProperty("secret_ref").GetString());
        Assert.Equal(AsciiWire.Hex(Encoding.UTF8.GetBytes(frame.RequestLine)), frame.RequestUtf8Hex);
    }

    [Fact]
    public void PersistedNdjsonContainsOnlyRewrittenBytes()
    {
        var path = Path.Combine(RepoLocator.Root, "verification", "FEA-09", "logs", "wire-redacted.ndjson");
        var log = new WireLog(path);
        const string raw = "{\"payload\":{\"secret_ref\":{\"token\":\"sentinel-token\",\"path\":\"C:/private/source-secret.bin\"},\"signing_key\":\"sentinel-signing-key\",\"nested\":{\"path\":\"C:/private/source.png\"}}}";
        log.Add(new WireFrame("core_service", raw, raw, "rawhex", "rawhex", true, true, 1, DateTimeOffset.UtcNow));
        var text = File.ReadAllText(path);
        Assert.DoesNotContain("sentinel-token", text);
        Assert.DoesNotContain("sentinel-signing-key", text);
        Assert.DoesNotContain("source-secret.bin", text);
        foreach (var line in File.ReadLines(path))
        {
            using var document = JsonDocument.Parse(line);
            foreach (var direction in new[] { "request", "response" })
            {
                var safe = document.RootElement.GetProperty(direction).GetString()!;
                Assert.Equal(AsciiWire.Hex(Encoding.UTF8.GetBytes(safe)),
                    document.RootElement.GetProperty(direction + "_utf8_hex").GetString());
                using var safeJson = JsonDocument.Parse(safe);
            }
        }
    }

    [Fact]
    public void MalformedLineIsWithheldAndOrdinaryFrameKeepsItsBytes()
    {
        Assert.Equal("{\"ok\":true}", WireLog.Redact("{\"ok\":true}"));
        Assert.DoesNotContain("private", WireLog.Redact("malformed C:/private"));
        using var safe = JsonDocument.Parse(WireLog.Redact("malformed C:/private"));
    }
}
