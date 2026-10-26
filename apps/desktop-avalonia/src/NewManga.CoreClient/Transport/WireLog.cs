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
        lock (_gate)
        {
            _frames.Add(frame);
            if (!string.IsNullOrWhiteSpace(_ndjsonPath))
            {
                File.AppendAllText(_ndjsonPath!, Serialize(frame) + Environment.NewLine);
            }
        }
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
