using System.Text.Json;
using NewManga.CoreClient.Diagnostics;

namespace NewManga.CoreClient.Commands;

/// <summary>
/// RUN-BINDING-FIX-1: Host-side default <c>overrides.provider_bindings</c> for <c>StartRun</c>.
///
/// RUN-OCR-DIAG-1 proved the OCR step fails with <c>PROVIDER_NOT_CONFIGURED</c> because the frozen
/// Core's <c>pipeline_defaults.provider_bindings_json</c> is <c>{}</c>; one StartRun override
/// (<c>{"ocr":"manga-ocr"}</c>) makes the very same OCR step complete. The fix belongs to the Host:
/// every StartRun carries the default binding unless the caller already sent
/// <c>overrides.provider_bindings</c> (user overrides always win) or the default is disabled through
/// the environment (<c>NEWMANGA_RUN_PROVIDER_BINDINGS</c>: a JSON object overrides the value,
/// empty / "off" / "none" / "disabled" / "0" turns the injection off).
/// </summary>
public static class RunBindingDefaults
{
    /// <summary>Environment knob for the Host-side StartRun provider bindings.</summary>
    public const string EnvironmentVariable = "NEWMANGA_RUN_PROVIDER_BINDINGS";

    /// <summary>Default binding: the only OCR provider registered by the frozen Core.</summary>
    public const string DefaultJson = "{\"ocr\":\"manga-ocr\"}";

    private static readonly string[] DisabledTokens = { "", "off", "none", "disabled", "0" };

    /// <summary>
    /// Resolves the configured default bindings. Returns <c>null</c> when the injection is disabled;
    /// throws <see cref="InvalidOperationException"/> when the configuration is not a JSON object of
    /// non-empty provider ids (a host-configuration error must never silently change run semantics).
    /// </summary>
    public static JsonElement? Resolve(string? raw = null)
    {
        var configured = raw ?? Environment.GetEnvironmentVariable(EnvironmentVariable);
        if (configured is null)
        {
            return Parse(DefaultJson, EnvironmentVariable + " default");
        }

        var trimmed = configured.Trim();
        foreach (var token in DisabledTokens)
        {
            if (string.Equals(trimmed, token, StringComparison.OrdinalIgnoreCase))
            {
                return null;
            }
        }

        return Parse(trimmed, EnvironmentVariable);
    }

    /// <summary>Raw JSON text of the resolved bindings (tests/diagnostics) or null when disabled.</summary>
    public static string? ResolveJson(string? raw = null)
    {
        var element = Resolve(raw);
        return element is null ? null : element.Value.GetRawText();
    }

    private static JsonElement Parse(string json, string source)
    {
        try
        {
            using var document = JsonDocument.Parse(json);
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                throw new InvalidOperationException($"{source} must be a JSON object of provider bindings (got {root.ValueKind})");
            }

            foreach (var property in root.EnumerateObject())
            {
                if (property.Value.ValueKind != JsonValueKind.String ||
                    string.IsNullOrWhiteSpace(property.Value.GetString()))
                {
                    throw new InvalidOperationException(
                        $"{source} entry '{property.Name}' must be a non-empty provider id string");
                }
            }

            return root.Clone();
        }
        catch (JsonException ex)
        {
            throw new InvalidOperationException($"{source} is not valid JSON: {ex.Message}", ex);
        }
    }
}
