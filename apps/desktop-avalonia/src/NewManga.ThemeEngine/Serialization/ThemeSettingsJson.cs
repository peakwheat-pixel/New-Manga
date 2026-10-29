using System.Text.Json;

namespace NewManga.ThemeEngine;

/// <summary>Result of reading the persisted settings document.</summary>
/// <param name="Settings">The parsed settings (defaults plus every recoverable field).</param>
/// <param name="Issues">Findings collected while reading (all warnings: settings must never block startup).</param>
public sealed record ThemeSettingsReadResult(ThemeSettings Settings, IReadOnlyList<ThemeValidationIssue> Issues)
{
    /// <summary>True when a settings object was found and parsed (it may still have needed fallbacks).</summary>
    public bool DocumentParsed { get; init; }
}

/// <summary>
/// Reads and writes the persisted settings document (<c>newmanga.theme-settings/1</c>). The reader is
/// forgiving by design: corrupt JSON, wrong types, unknown enums and legacy field names all fall back
/// field-by-field and produce warnings only, so a broken settings file can never block startup
/// (contract §4 behavior 2/3). Theme-id migration itself lives in <see cref="LegacyThemeMigration"/>.
/// </summary>
public static class ThemeSettingsJson
{
    /// <summary>Reads a settings document; never throws.</summary>
    public static ThemeSettingsReadResult Read(string json)
    {
        ArgumentNullException.ThrowIfNull(json);

        var issues = new List<ThemeValidationIssue>();
        JsonDocument document;
        try
        {
            document = JsonDocument.Parse(json, new JsonDocumentOptions
            {
                AllowTrailingCommas = false,
                CommentHandling = JsonCommentHandling.Disallow,
            });
        }
        catch (JsonException exception)
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.SettingsJsonInvalid,
                $"settings document is not valid JSON ({exception.Message}); shipped defaults are used"));
            return new ThemeSettingsReadResult(ThemeDefaults.Settings, issues) { DocumentParsed = false };
        }

        using (document)
        {
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.SettingsJsonInvalid,
                    "settings document root must be a JSON object; shipped defaults are used"));
                return new ThemeSettingsReadResult(ThemeDefaults.Settings, issues) { DocumentParsed = false };
            }

            var properties = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
            foreach (var property in root.EnumerateObject())
            {
                properties[property.Name] = property.Value;
            }

            var schema = ReadString(properties, "schema");
            if (schema is not null && !string.Equals(schema, ThemeDefaults.SettingsSchema, StringComparison.Ordinal))
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.SettingsSchemaUnsupported,
                    $"settings schema '{schema}' is not '{ThemeDefaults.SettingsSchema}'; unknown fields are ignored",
                    "schema"));
            }

            var themeId =
                ReadString(properties, "themeId") ??
                ReadString(properties, "theme") ??
                string.Empty;

            var appearance = ReadAppearance(properties, issues);
            var contrast = ReadContrast(properties, issues);
            var layout = ReadLayout(properties, issues);
            var reducedMotion = ReadBool(properties, issues, "reducedMotion", "reduced-motion") ?? false;
            var followSystemAccent = ReadBool(properties, issues, "followSystemAccent", "followAccent") ?? false;

            ReportUnknownProperties(properties, issues);

            var settings = new ThemeSettings(
                themeId.Trim(),
                appearance,
                contrast,
                layout,
                reducedMotion,
                followSystemAccent);

            return new ThemeSettingsReadResult(settings, issues) { DocumentParsed = true };
        }
    }

    /// <summary>Writes the canonical settings document (sorted, two-space indent, LF, final newline).</summary>
    public static string Write(ThemeSettings settings)
    {
        ArgumentNullException.ThrowIfNull(settings);

        return ThemeJsonWriter.Write(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("schema", ThemeDefaults.SettingsSchema);
            writer.WriteString("themeId", settings.ThemeId);
            writer.WriteString("appearance", ThemeEnumNames.ToJson(settings.Appearance));
            writer.WriteString("contrast", ThemeEnumNames.ToJson(settings.Contrast));

            writer.WriteStartObject("layout");
            writer.WriteString("id", settings.Layout.Id);
            writer.WriteString("navigation", ThemeEnumNames.ToJson(settings.Layout.Navigation));
            writer.WriteString("shelf", ThemeEnumNames.ToJson(settings.Layout.Shelf));
            writer.WriteString("density", ThemeEnumNames.ToJson(settings.Layout.Density));
            writer.WriteString("workbench", ThemeEnumNames.ToJson(settings.Layout.Workbench));
            writer.WriteString("reader", ThemeEnumNames.ToJson(settings.Layout.Reader));
            writer.WriteEndObject();

            writer.WriteBoolean("reducedMotion", settings.ReducedMotion);
            writer.WriteBoolean("followSystemAccent", settings.FollowSystemAccent);
            writer.WriteEndObject();
        });
    }

    private static AppearanceMode ReadAppearance(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<ThemeValidationIssue> issues)
    {
        foreach (var name in new[] { "appearance", "variant", "themeMode" })
        {
            var raw = ReadString(properties, name);
            if (raw is null)
            {
                continue;
            }

            if (ThemeEnumNames.TryParseAppearance(raw, out var parsed))
            {
                return parsed;
            }

            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.SettingsInvalidValue,
                $"unsupported appearance '{raw}'; falling back to 'system'",
                name));
            return AppearanceMode.System;
        }

        return AppearanceMode.System;
    }

    private static ContrastMode ReadContrast(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<ThemeValidationIssue> issues)
    {
        var raw = ReadString(properties, "contrast");
        if (raw is null)
        {
            return ContrastMode.Standard;
        }

        if (ThemeEnumNames.TryParseContrast(raw, out var parsed))
        {
            return parsed;
        }

        issues.Add(ThemeValidationIssue.Warning(
            ThemeIssueCodes.SettingsInvalidValue,
            $"unsupported contrast '{raw}'; falling back to 'standard'",
            "contrast"));
        return ContrastMode.Standard;
    }

    private static LayoutProfile ReadLayout(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<ThemeValidationIssue> issues)
    {
        var defaults = LayoutProfile.Default;
        string id = defaults.Id;
        var navigation = defaults.Navigation;
        var shelf = defaults.Shelf;
        var density = defaults.Density;
        var workbench = defaults.Workbench;
        var reader = defaults.Reader;

        if (properties.TryGetValue("layout", out var layoutElement))
        {
            if (layoutElement.ValueKind != JsonValueKind.Object)
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.SettingsInvalidValue,
                    "'layout' must be an object; the default layout is used",
                    "layout"));
            }
            else
            {
                var layout = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
                foreach (var property in layoutElement.EnumerateObject())
                {
                    layout[property.Name] = property.Value;
                }

                id = ReadString(layout, "id") ?? id;

                if (ReadEnum(layout, "navigation", issues, ThemeEnumNames.TryParseNavigation, navigation, out var parsedNavigation))
                {
                    navigation = parsedNavigation;
                }

                if (ReadEnum(layout, "shelf", issues, ThemeEnumNames.TryParseShelf, shelf, out var parsedShelf))
                {
                    shelf = parsedShelf;
                }

                if (ReadEnum(layout, "density", issues, ThemeEnumNames.TryParseDensity, density, out var parsedDensity))
                {
                    density = parsedDensity;
                }

                if (ReadEnum(layout, "workbench", issues, ThemeEnumNames.TryParseWorkbench, workbench, out var parsedWorkbench))
                {
                    workbench = parsedWorkbench;
                }

                if (ReadEnum(layout, "reader", issues, ThemeEnumNames.TryParseReader, reader, out var parsedReader))
                {
                    reader = parsedReader;
                }

                foreach (var name in layout.Keys)
                {
                    if (name is not ("id" or "navigation" or "shelf" or "density" or "workbench" or "reader"))
                    {
                        issues.Add(ThemeValidationIssue.Warning(
                            ThemeIssueCodes.UnknownField,
                            $"unknown field 'layout.{name}' was ignored",
                            $"layout.{name}"));
                    }
                }
            }
        }

        // Legacy flat density (pre-layout-profile settings) is still honoured when the nested layout
        // does not define one.
        if (!properties.TryGetValue("layout", out _))
        {
            if (ReadEnum(properties, "density", issues, ThemeEnumNames.TryParseDensity, density, out var legacyDensity))
            {
                density = legacyDensity;
            }
        }

        return new LayoutProfile(id, navigation, shelf, density, workbench, reader);
    }

    private static bool ReadEnum<T>(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        List<ThemeValidationIssue> issues,
        TryParseEnum<T> tryParse,
        T fallback,
        out T value)
        where T : struct
    {
        value = fallback;
        if (!properties.TryGetValue(name, out var element))
        {
            return false;
        }

        if (element.ValueKind == JsonValueKind.String && tryParse(element.GetString(), out var parsed))
        {
            value = parsed;
            return true;
        }

        issues.Add(ThemeValidationIssue.Warning(
            ThemeIssueCodes.SettingsInvalidValue,
            $"unsupported '{name}' value '{element.GetRawText()}'; falling back to '{fallback}'",
            name));
        return false;
    }

    private static string? ReadString(IReadOnlyDictionary<string, JsonElement> properties, string name) =>
        properties.TryGetValue(name, out var element) && element.ValueKind == JsonValueKind.String
            ? element.GetString()
            : null;

    private static bool? ReadBool(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<ThemeValidationIssue> issues,
        params string[] names)
    {
        foreach (var name in names)
        {
            if (!properties.TryGetValue(name, out var element))
            {
                continue;
            }

            if (element.ValueKind is JsonValueKind.True or JsonValueKind.False)
            {
                return element.GetBoolean();
            }

            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.SettingsInvalidValue,
                $"'{name}' must be a boolean; falling back to false",
                name));
            return false;
        }

        return null;
    }

    private static void ReportUnknownProperties(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<ThemeValidationIssue> issues)
    {
        foreach (var name in properties.Keys)
        {
            if (name is "schema" or "themeId" or "theme" or "appearance" or "variant" or "themeMode" or
                "contrast" or "layout" or "density" or "reducedMotion" or "reduced-motion" or
                "followSystemAccent" or "followAccent")
            {
                continue;
            }

            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.UnknownField,
                $"unknown settings field '{name}' was ignored",
                name));
        }
    }

    private delegate bool TryParseEnum<T>(string? raw, out T value)
        where T : struct;
}
