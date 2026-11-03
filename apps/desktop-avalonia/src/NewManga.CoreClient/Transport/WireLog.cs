using System.Text;
using System.Text.Json;
using System.Globalization;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Transport;

/// <summary>One request/response pair crossing a sidecar pipe, captured byte-for-byte for evidence.</summary>
public sealed record WireFrame(
    string Sidecar,
    string RequestLine,
    string ResponseLine,
    string RequestUtf8Hex,
    string ResponseUtf8Hex,
    bool RequestAsciiOnly,
    bool ResponseAsciiOnly,
    double ElapsedMs,
    DateTimeOffset TimestampUtc);

/// <summary>
/// In-memory frame list + optional NDJSON evidence file. AC3 requires raw wire bytes, so every
/// frame carries the exact UTF-8 hex of both directions plus the ASCII-only assertion.
/// </summary>
public sealed class WireLog
{
    private readonly List<WireFrame> _frames = new();
    private readonly object _gate = new();
    private readonly string? _ndjsonPath;

    public WireLog(string? ndjsonPath = null)
    {
        _ndjsonPath = ndjsonPath;
        if (!string.IsNullOrWhiteSpace(ndjsonPath))
        {
            var directory = Path.GetDirectoryName(ndjsonPath);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }
        }
    }

    public IReadOnlyList<WireFrame> Frames
    {
        get
        {
            lock (_gate)
            {
                return _frames.ToArray();
            }
        }
    }

    public int Count
    {
        get
        {
            lock (_gate)
            {
                return _frames.Count;
            }
        }
    }

    public bool AllRequestsAsciiOnly
    {
        get
        {
            lock (_gate)
            {
                foreach (var frame in _frames)
                {
                    if (!frame.RequestAsciiOnly)
                    {
                        return false;
                    }
                }

                return true;
            }
        }
    }

    public void Add(WireFrame frame)
    {
        // Construct the saveable frame only after both directions are rewritten.
        var request = Redact(frame.RequestLine);
        var response = Redact(frame.ResponseLine);
        frame = new WireFrame(frame.Sidecar, request, response,
            AsciiWire.Hex(Encoding.UTF8.GetBytes(request)), AsciiWire.Hex(Encoding.UTF8.GetBytes(response)),
            AsciiWire.IsAscii(request), AsciiWire.IsAscii(response), frame.ElapsedMs, frame.TimestampUtc);
        lock (_gate)
        {
            _frames.Add(frame);
            if (!string.IsNullOrWhiteSpace(_ndjsonPath))
            {
                File.AppendAllText(_ndjsonPath!, Serialize(frame) + Environment.NewLine);
            }
        }
    }

    private static readonly HashSet<string> Sensitive = new(StringComparer.OrdinalIgnoreCase)
    { "secret_ref", "signing_key", "host_session_credential", "path", "source_path", "target_path", "password" };

    public static string Redact(string line)
    {
        if (line.Length == 0) return line;
        try
        {
            using var document = JsonDocument.Parse(line);
            var changed = false;
            var safe = WireJson.Write(writer => Rewrite(writer, document.RootElement, ref changed));
            return changed ? safe : line;
        }
        catch (JsonException) { return "{\"redacted\":\"unparseable frame\"}"; }
    }

    private static void Rewrite(Utf8JsonWriter writer, JsonElement value, ref bool changed)
    {
        if (value.ValueKind == JsonValueKind.Object)
        {
            writer.WriteStartObject();
            foreach (var property in value.EnumerateObject())
            {
                writer.WritePropertyName(property.Name);
                if (Sensitive.Contains(property.Name))
                { writer.WriteStringValue("[REDACTED]"); changed = true; }
                else Rewrite(writer, property.Value, ref changed);
            }
            writer.WriteEndObject();
        }
        else if (value.ValueKind == JsonValueKind.Array)
        {
            writer.WriteStartArray();
            foreach (var item in value.EnumerateArray()) Rewrite(writer, item, ref changed);
            writer.WriteEndArray();
        }
        else if (value.ValueKind == JsonValueKind.String && value.GetString() is { } text
            && (Path.IsPathFullyQualified(text) || text.StartsWith("/")))
        { writer.WriteStringValue("[REDACTED]"); changed = true; }
        else value.WriteTo(writer);
    }

    private static string Serialize(WireFrame frame) => WireJson.Write(writer =>
    {
        writer.WriteStartObject();
        writer.WriteString("timestamp_utc", frame.TimestampUtc.ToString("O", CultureInfo.InvariantCulture));
        writer.WriteString("sidecar", frame.Sidecar);
        writer.WriteString("request", frame.RequestLine);
        writer.WriteString("response", frame.ResponseLine);
        writer.WriteString("request_utf8_hex", frame.RequestUtf8Hex);
        writer.WriteString("response_utf8_hex", frame.ResponseUtf8Hex);
        writer.WriteBoolean("request_ascii_only", frame.RequestAsciiOnly);
        writer.WriteBoolean("response_ascii_only", frame.ResponseAsciiOnly);
        writer.WriteNumber("elapsed_ms", Math.Round(frame.ElapsedMs, 3));
        writer.WriteEndObject();
    });
}
