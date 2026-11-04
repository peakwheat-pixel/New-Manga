using System.Globalization;
using System.Text;

namespace NewManga.CoreClient.Commands;

/// <summary>
/// canonical-json/1 (C-17 §1): UTF-8, object keys sorted by Unicode code
/// point, no whitespace, raw strings un-normalised, only
/// int/bool/null/string/array/object (no floats); control characters escape
/// as lowercase \u00xx. The Host must produce byte-identical digests to the
/// Core (doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md §5.2).
/// </summary>
public static class CanonicalJson
{
    public static byte[] Bytes(object? value) => Encoding.UTF8.GetBytes(Text(value));

    public static string Text(object? value)
    {
        var builder = new StringBuilder();
        Write(builder, value);
        return builder.ToString();
    }

    public static string Sha256Hex(object? value) =>
        Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(Bytes(value)))
            .ToLowerInvariant();

    private static void Write(StringBuilder builder, object? value)
    {
        switch (value)
        {
            case null:
                builder.Append("null");
                return;
            case bool flag:
                builder.Append(flag ? "true" : "false");
                return;
            case int number:
                builder.Append(number.ToString(CultureInfo.InvariantCulture));
                return;
            case long number:
                builder.Append(number.ToString(CultureInfo.InvariantCulture));
                return;
            case string text:
                WriteString(builder, text);
                return;
            case System.Collections.IDictionary dictionary:
                WriteObject(builder, dictionary);
                return;
            case System.Collections.IEnumerable items:
                WriteArray(builder, items);
                return;
            default:
                throw new ArgumentException(
                    "canonical-json/1 has no representation for " + value.GetType().Name);
        }
    }

    private static void WriteObject(StringBuilder builder, System.Collections.IDictionary dictionary)
    {
        var keys = new List<string>();
        foreach (var key in dictionary.Keys)
        {
            if (key is not string name)
            {
                throw new ArgumentException("canonical-json/1 object keys must be strings");
            }
            keys.Add(name);
        }
        keys.Sort(StringComparer.Ordinal);
        builder.Append('{');
        for (var index = 0; index < keys.Count; index++)
        {
            if (index > 0)
            {
                builder.Append(',');
            }
            WriteString(builder, keys[index]);
            builder.Append(':');
            Write(builder, dictionary[keys[index]]);
        }
        builder.Append('}');
    }

    private static void WriteArray(StringBuilder builder, System.Collections.IEnumerable items)
    {
        builder.Append('[');
        var first = true;
        foreach (var item in items)
        {
            if (!first)
            {
                builder.Append(',');
            }
            first = false;
            Write(builder, item);
        }
        builder.Append(']');
    }

    private static void WriteString(StringBuilder builder, string text)
    {
        builder.Append('"');
        foreach (var rune in text.EnumerateRunes())
        {
            var codePoint = rune.Value;
            switch (codePoint)
            {
                case '"':
                    builder.Append("\\\"");
                    continue;
                case '\\':
                    builder.Append("\\\\");
                    continue;
                case '\b':
                    builder.Append("\\b");
                    continue;
                case '\f':
                    builder.Append("\\f");
                    continue;
                case '\n':
                    builder.Append("\\n");
                    continue;
                case '\r':
                    builder.Append("\\r");
                    continue;
                case '\t':
                    builder.Append("\\t");
                    continue;
            }
            if (codePoint < 0x20)
            {
                builder.Append("\\u").Append(codePoint.ToString("x4", CultureInfo.InvariantCulture));
                continue;
            }
            builder.Append(rune.ToString());
        }
        builder.Append('"');
    }
}
