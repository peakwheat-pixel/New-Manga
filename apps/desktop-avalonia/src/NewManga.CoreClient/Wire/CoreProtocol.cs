using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Wire;

/// <summary>Protocol-2.3 envelope (core_service) shared by every application-channel request.</summary>
public static class CoreProtocol
{
    public const string ProtocolName = "new-manga.core";
    public const int Major = 2;
    public const int DefaultMinor = 3;
    public const int CreateMinor = 8;

    public static string BuildRequest(
        string requestId,
        string command,
        int minor = DefaultMinor,
        Action<Utf8JsonWriter>? payload = null)
    {
        payload ??= WireJson.EmptyObject;
        return WireJson.Write(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("protocol", ProtocolName);
            writer.WritePropertyName("version");
            writer.WriteStartObject();
            writer.WriteNumber("major", Major);
            writer.WriteNumber("minor", minor);
            writer.WriteEndObject();
            writer.WriteString("request_id", requestId);
            writer.WriteString("command", command);
            writer.WritePropertyName("payload");
            payload(writer);
            writer.WriteEndObject();
        });
    }

    public static string BuildCreateRequest(string requestId, string command, Action<Utf8JsonWriter> payload) =>
        BuildRequest(requestId, command, CreateMinor, payload);

    /// <summary>
    /// READER-PROGRESS-1: true when a stdout line is an unsolicited event envelope
    /// (<c>event_type</c>/<c>event_id</c>, no <c>request_id</c>). core_service mixes these into the
    /// response stream right before answering the command that produced them.
    /// </summary>
    public static bool IsEventFrame(string line) =>
        line.Contains("\"event_type\"", StringComparison.Ordinal) &&
        !line.Contains("\"request_id\"", StringComparison.Ordinal);

    /// <summary>Parses a response line; throws <see cref="SidecarException"/> on malformed JSON.</summary>
    public static CoreResponse Parse(string line)
    {
        try
        {
            using var document = JsonDocument.Parse(line);
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                throw Malformed("response root is not an object");
            }

            var requestId = root.TryGetProperty("request_id", out var id) && id.ValueKind == JsonValueKind.String
                ? id.GetString()
                : null;
            CoreErrorInfo? error = null;
            if (root.TryGetProperty("error", out var err) && err.ValueKind == JsonValueKind.Object)
            {
                error = new CoreErrorInfo(
                    ReadString(err, "code") ?? "UNKNOWN",
                    ReadString(err, "category"),
                    ReadString(err, "message"),
                    err.TryGetProperty("retryable", out var retryable)
                        ? retryable.ValueKind switch
                        {
                            JsonValueKind.True => true,
                            JsonValueKind.False => false,
                            _ => null,
                        }
                        : null);
            }

            JsonElement? result = null;
            if (root.TryGetProperty("result", out var resultElement))
            {
                result = resultElement.Clone();
            }

            return new CoreResponse(requestId, result, error);
        }
        catch (JsonException ex)
        {
            throw Malformed(ex.Message, ex);
        }
    }

    private static SidecarException Malformed(string detail, Exception? inner = null) =>
        new(SidecarErrorCode.MalformedResponse, "core_service", $"malformed response: {detail}", null, inner);

    private static string? ReadString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;
}

public sealed record CoreErrorInfo(string Code, string? Category, string? Message, bool? Retryable);

public sealed class CoreResponse
{
    public CoreResponse(string? requestId, JsonElement? result, CoreErrorInfo? error)
    {
        RequestId = requestId;
        Result = result;
        Error = error;
    }

    public string? RequestId { get; }

    /// <summary>Cloned result element (safe after the source document is disposed).</summary>
    public JsonElement? Result { get; }

    public CoreErrorInfo? Error { get; }

    public bool IsOk => Error is null;
}

/// <summary>Typed application error returned by the Core (code/category/retryable passthrough).</summary>
public sealed class CoreOperationException : Exception
{
    public CoreOperationException(string code, string? category, bool? retryable, string? message, string? requestId)
        : base($"[{code}] {message ?? "core operation failed"}")
    {
        Code = code;
        Category = category;
        Retryable = retryable;
        CoreMessage = message;
        RequestId = requestId;
    }

    public string Code { get; }

    public string? Category { get; }

    public bool? Retryable { get; }

    public string? CoreMessage { get; }

    public string? RequestId { get; }
}
