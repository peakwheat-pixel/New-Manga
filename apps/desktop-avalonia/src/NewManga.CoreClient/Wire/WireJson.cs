using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;

namespace NewManga.CoreClient.Wire;

/// <summary>
/// Thin <see cref="Utf8JsonWriter"/> helpers: request/response JSON is produced without reflection
/// so the trimmed single-file publish stays valid (the S0 spike hit exactly this: JsonValue.Create
/// (double) throws NotSupportedException once the reflection resolver is trimmed away).
/// </summary>
public static class WireJson
{
    public static string Write(Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream(128);
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions
        {
            Indented = false,
            Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        }))
        {
            write(writer);
        }

        return Encoding.UTF8.GetString(stream.ToArray());
    }

    public static Action<Utf8JsonWriter> EmptyObject { get; } = static writer =>
    {
        writer.WriteStartObject();
        writer.WriteEndObject();
    };
}
