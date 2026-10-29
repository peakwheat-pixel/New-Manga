using System.Text.Json;

namespace NewManga.DesignSystem.Tokens;

/// <summary>
/// One DTCG leaf token as published by <c>doc/design/redesign-v1/40-fusion/tokens.json</c>.
/// </summary>
/// <param name="Path">Dotted JSON path, e.g. <c>color.dark.bg.canvas</c>.</param>
/// <param name="Value">Raw CSS-ish value as authored, e.g. <c>#0F1012</c> or <c>11px</c>.</param>
/// <param name="Type">DTCG <c>$type</c>, e.g. <c>color</c>, <c>dimension</c>, <c>duration</c>.</param>
public sealed record TokenEntry(string Path, string Value, string Type);

/// <summary>
/// Flattens the frozen DTCG token document into an ordered leaf list. <c>meta</c> and
/// <c>$schema</c> are not tokens; every other object with a <c>$value</c> is a leaf.
/// </summary>
public static class TokenDocument
{
    /// <summary>Parses a tokens.json document into deterministic (ordinal path) order.</summary>
    public static IReadOnlyList<TokenEntry> Parse(string json)
    {
        ArgumentNullException.ThrowIfNull(json);

        using var document = JsonDocument.Parse(json, new JsonDocumentOptions
        {
            AllowTrailingCommas = false,
            CommentHandling = JsonCommentHandling.Disallow,
        });

        var entries = new List<TokenEntry>(capacity: 141);
        Walk(document.RootElement, string.Empty, entries);
        entries.Sort(static (left, right) => string.CompareOrdinal(left.Path, right.Path));
        return entries;
    }

    private static void Walk(JsonElement element, string path, List<TokenEntry> entries)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            return;
        }

        if (element.TryGetProperty("$value", out var valueElement))
        {
            if (!element.TryGetProperty("$type", out var typeElement))
            {
                throw new InvalidOperationException($"token '{path}' is missing $type");
            }

            var value = valueElement.ValueKind switch
            {
                JsonValueKind.String => valueElement.GetString()!,
                JsonValueKind.Number => valueElement.GetRawText(),
                JsonValueKind.True => "true",
                JsonValueKind.False => "false",
                _ => throw new InvalidOperationException(
                    $"token '{path}' has unsupported $value kind {valueElement.ValueKind}"),
            };

            entries.Add(new TokenEntry(path, value, typeElement.GetString()!));
            return;
        }

        foreach (var property in element.EnumerateObject())
        {
            // "$schema", "$description" (if ever added) and the document metadata block are not tokens.
            if (property.Name.StartsWith('$') || property.Name == "meta")
            {
                continue;
            }

            Walk(property.Value, path.Length == 0 ? property.Name : path + "." + property.Name, entries);
        }
    }
}
