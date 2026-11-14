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
///
/// TRANS-RUN-PATH-FIX AC3: the default is OCR plus <c>translate</c> when the Host knows a configured
/// translate provider id (<c>NEWMANGA_RUN_TRANSLATE_PROVIDER</c> or the explicit argument). Without
/// one the historical OCR-only default is emitted byte-for-byte, so an install that never configured
/// translation keeps exactly the previous run semantics.
/// </summary>
public static class RunBindingDefaults
{
    /// <summary>Environment knob for the Host-side StartRun provider bindings.</summary>
    public const string EnvironmentVariable = "NEWMANGA_RUN_PROVIDER_BINDINGS";

    /// <summary>
    /// TRANS-RUN-PATH-FIX AC3: environment knob naming the translate provider to add to the default
    /// bindings. Absent/blank (or a disabled token) keeps the OCR-only default.
    /// </summary>
    public const string TranslateProviderVariable = "NEWMANGA_RUN_TRANSLATE_PROVIDER";

    /// <summary>Default binding: the only OCR provider registered by the frozen Core.</summary>
    public const string DefaultJson = "{\"ocr\":\"manga-ocr\"}";

    private static readonly string[] DisabledTokens = { "", "off", "none", "disabled", "0" };

    /// <summary>
    /// AC3: OCR plus translate. Written only when a translate provider id is known; the value is
    /// the provider/profile id the frozen Core resolves through <c>provider_bindings["translate"]</c>.
    /// </summary>
    public static string DefaultJsonWithTranslate(string translateProviderId) =>
        $"{{\"ocr\":\"manga-ocr\",\"translate\":{JsonSerializer.Serialize(translateProviderId)}}}";

    /// <summary>
    /// Resolves the configured default bindings. Returns <c>null</c> when the injection is disabled;
    /// throws <see cref="InvalidOperationException"/> when the configuration is not a JSON object of
    /// non-empty provider ids (a host-configuration error must never silently change run semantics).
    /// </summary>
    public static JsonElement? Resolve(string? raw = null, string? translateProviderId = null)
    {
        var configured = raw ?? Environment.GetEnvironmentVariable(EnvironmentVariable);
        if (configured is null)
        {
            var translate = translateProviderId ?? Environment.GetEnvironmentVariable(TranslateProviderVariable);
            if (!string.IsNullOrWhiteSpace(translate) && !IsDisabled(translate.Trim()))
            {
                return Parse(DefaultJsonWithTranslate(translate.Trim()), TranslateProviderVariable);
            }

            return Parse(DefaultJson, EnvironmentVariable + " default");
        }

        var trimmed = configured.Trim();
        if (IsDisabled(trimmed))
        {
            return null;
        }

        return Parse(trimmed, EnvironmentVariable);
    }

    /// <summary>Raw JSON text of the resolved bindings (tests/diagnostics) or null when disabled.</summary>
    public static string? ResolveJson(string? raw = null, string? translateProviderId = null)
    {
        var element = Resolve(raw, translateProviderId);
        return element is null ? null : element.Value.GetRawText();
    }

    private static bool IsDisabled(string value)
    {
        foreach (var token in DisabledTokens)
        {
            if (string.Equals(value, token, StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }
        }

        return false;
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
