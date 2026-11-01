using System;
using System.Collections.Generic;
using System.Text.Json;

namespace NewManga.Appearance;

/// <summary>Result of reading the persisted appearance document.</summary>
public sealed record AppearanceReadResult(AppearanceSettings Settings, IReadOnlyList<string> Warnings)
{
    /// <summary>True when a document object was parsed (it may still have needed fallbacks).</summary>
    public bool DocumentParsed { get; init; }
}

/// <summary>
/// C-03 v6 §2.2/§2.5: reads and writes <c>presentation-settings.json</c>. The reader is
/// forgiving (corrupt JSON / wrong types / legacy names fall back field-by-field with
/// warnings, never blocking startup); the writer is canonical (sorted, two-space indent,
/// LF, final newline) and always writes <c>schemaVersion: 2</c>.
/// </summary>
public static class AppearanceJson
{
    /// <summary>Reads a document; never throws.</summary>
    public static AppearanceReadResult Read(string json)
    {
        ArgumentNullException.ThrowIfNull(json);

        var warnings = new List<string>();
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
            warnings.Add($"appearance document is not valid JSON ({exception.Message}); shipped defaults are used");
            return new AppearanceReadResult(AppearanceDefaults.Settings, warnings) { DocumentParsed = false };
        }

        using (document)
        {
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                warnings.Add("appearance document root must be a JSON object; shipped defaults are used");
                return new AppearanceReadResult(AppearanceDefaults.Settings, warnings) { DocumentParsed = false };
            }

            var properties = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
            foreach (var property in root.EnumerateObject())
            {
                properties[property.Name] = property.Value;
            }

            var defaults = AppearanceDefaults.Settings;
            var schemaVersion = ReadInt(properties, "schemaVersion") ?? 1;
            if (schemaVersion < 1)
            {
                warnings.Add($"unsupported schemaVersion {schemaVersion}; migrating from the legacy document");
                schemaVersion = 1;
            }

            var frontendId = ReadString(properties, "theme.frontendId") ?? defaults.FrontendId;
            var visualThemeId =
                ReadString(properties, "theme.visualThemeId") ??
                ReadString(properties, "themeId") ??
                ReadString(properties, "theme") ??
                defaults.VisualThemeId;

            var mode = ReadAppearanceMode(properties, warnings);
            var contrast = ReadContrast(properties, warnings);
            var followSystemAccent = ReadBool(properties, "appearance.followSystemAccent") ?? false;
            var motion = ReadMotion(properties, warnings);
            var categories = ReadMotionCategories(properties, warnings);
            var corners = ReadCorners(properties, warnings);
            var acrylic = ReadDouble(properties, "material.acrylicStrength") ?? ReadNestedDouble(properties, "material", "acrylicStrength") ?? defaults.MaterialAcrylicStrength;
            var mica = ReadBool(properties, "material.micaEnabled") ?? ReadNestedBool(properties, "material", "micaEnabled") ?? defaults.MaterialMicaEnabled;
            var layout = ReadLayout(properties, warnings);

            var settings = new AppearanceSettings
            {
                FrontendId = NormalizeFrontend(frontendId, warnings),
                VisualThemeId = NormalizeVisualTheme(visualThemeId, warnings),
                Mode = mode,
                Contrast = contrast,
                FollowSystemAccent = followSystemAccent,
                MotionMode = motion,
                MotionCategories = categories,
                CornersScale = corners,
                MaterialAcrylicStrength = Math.Clamp(acrylic, 0, 1),
                MaterialMicaEnabled = mica,
                Layout = layout,
                SchemaVersion = AppearanceSettings.CurrentSchemaVersion,
            };

            return new AppearanceReadResult(settings, warnings) { DocumentParsed = true };
        }
    }

    /// <summary>Writes the canonical document (schemaVersion 2).</summary>
    public static string Write(AppearanceSettings settings)
    {
        ArgumentNullException.ThrowIfNull(settings);

        using var stream = new System.IO.MemoryStream();
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true }))
        {
            writer.WriteStartObject();
            writer.WriteNumber("schemaVersion", AppearanceSettings.CurrentSchemaVersion);
            writer.WriteString("theme.frontendId", settings.FrontendId);
            writer.WriteString("theme.visualThemeId", settings.VisualThemeId);
            writer.WriteString("appearance.mode", ToJson(settings.Mode));
            writer.WriteString("appearance.contrast", ToJson(settings.Contrast));
            writer.WriteBoolean("appearance.followSystemAccent", settings.FollowSystemAccent);
            writer.WriteString("motion.mode", ToJson(settings.MotionMode));
            writer.WriteStartObject("motion.categories");
            writer.WriteBoolean("feedback", settings.MotionCategories.HasFlag(MotionCategories.Feedback));
            writer.WriteBoolean("transition", settings.MotionCategories.HasFlag(MotionCategories.Transition));
            writer.WriteBoolean("emphasis", settings.MotionCategories.HasFlag(MotionCategories.Emphasis));
            writer.WriteEndObject();
            writer.WriteStartObject("corners");
            writer.WriteString("scale", ToJson(settings.CornersScale));
            writer.WriteEndObject();
            writer.WriteStartObject("material");
            writer.WriteNumber("acrylicStrength", settings.MaterialAcrylicStrength);
            writer.WriteBoolean("micaEnabled", settings.MaterialMicaEnabled);
            writer.WriteEndObject();
            writer.WriteStartObject("layout");
            writer.WriteString("id", settings.Layout.Id);
            writer.WriteString("navigation", settings.Layout.Navigation);
            writer.WriteString("shelf", settings.Layout.Shelf);
            writer.WriteString("density", settings.Layout.Density);
            writer.WriteString("workbench", settings.Layout.Workbench);
            writer.WriteString("reader", settings.Layout.Reader);
            writer.WriteEndObject();
            writer.WriteEndObject();
        }

        var text = System.Text.Encoding.UTF8.GetString(stream.ToArray()).Replace("\r\n", "\n");
        return text.EndsWith('\n') ? text : text + "\n";
    }

    /// <summary>
    /// §2.3 equivalence: a legacy boolean <c>reducedMotion</c> maps to <c>motion.mode</c>.
    /// Old <c>true</c> = reduce + all categories disabled; old <c>false</c> = full
    /// (removing the overlay = full motion, NOT auto).
    /// </summary>
    private static MotionMode ReadMotion(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<string> warnings)
    {
        var raw = ReadString(properties, "motion.mode") ?? ReadNestedString(properties, "motion", "mode");
        if (raw is not null)
        {
            if (Enum.TryParse<MotionMode>(raw, ignoreCase: true, out var parsed))
            {
                return parsed;
            }

            warnings.Add($"unsupported motion.mode '{raw}'; falling back to 'auto'");
            return MotionMode.Auto;
        }

        var legacy = ReadBool(properties, "reducedMotion") ?? ReadBool(properties, "reduced-motion");
        if (legacy is { } value)
        {
            warnings.Add("legacy 'reducedMotion' migrated to 'motion.mode'");
            return value ? MotionMode.Reduce : MotionMode.Full;
        }

        return MotionMode.Auto;
    }

    private static MotionCategories ReadMotionCategories(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<string> warnings)
    {
        if (!properties.TryGetValue("motion.categories", out var element))
        {
            return MotionCategories.All;
        }

        if (element.ValueKind == JsonValueKind.String &&
            string.Equals(element.GetString(), "off", StringComparison.OrdinalIgnoreCase))
        {
            return MotionCategories.None;
        }

        if (element.ValueKind != JsonValueKind.Object)
        {
            warnings.Add("'motion.categories' must be an object or 'off'; all categories are enabled");
            return MotionCategories.All;
        }

        var categories = MotionCategories.None;
        foreach (var property in element.EnumerateObject())
        {
            if (property.Value.ValueKind != JsonValueKind.True &&
                property.Value.ValueKind != JsonValueKind.False)
            {
                warnings.Add($"'motion.categories.{property.Name}' must be a boolean; ignored");
                continue;
            }

            if (!property.Value.GetBoolean())
            {
                continue;
            }

            categories |= property.Name switch
            {
                "feedback" => MotionCategories.Feedback,
                "transition" => MotionCategories.Transition,
                "emphasis" => MotionCategories.Emphasis,
                _ => MotionCategories.None,
            };
            if (categories == MotionCategories.None)
            {
                warnings.Add($"unknown motion category '{property.Name}'; ignored");
            }
        }

        return categories;
    }

    private static CornersScale ReadCorners(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<string> warnings)
    {
        var raw = ReadString(properties, "corners.scale") ?? ReadNestedString(properties, "corners", "scale");
        if (raw is null)
        {
            return CornersScale.Md;
        }

        if (Enum.TryParse<CornersScale>(raw, ignoreCase: true, out var parsed))
        {
            return parsed;
        }

        warnings.Add($"unsupported corners.scale '{raw}'; falling back to 'md'");
        return CornersScale.Md;
    }

    private static AppearanceMode ReadAppearanceMode(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<string> warnings)
    {
        var raw = ReadString(properties, "appearance.mode") ?? ReadString(properties, "appearance");
        if (raw is null)
        {
            return AppearanceMode.System;
        }

        if (Enum.TryParse<AppearanceMode>(raw, ignoreCase: true, out var parsed))
        {
            return parsed;
        }

        warnings.Add($"unsupported appearance.mode '{raw}'; falling back to 'system'");
        return AppearanceMode.System;
    }

    private static AppearanceContrast ReadContrast(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<string> warnings)
    {
        var raw = ReadString(properties, "appearance.contrast") ?? ReadString(properties, "contrast");
        if (raw is null)
        {
            return AppearanceContrast.Standard;
        }

        if (Enum.TryParse<AppearanceContrast>(raw, ignoreCase: true, out var parsed))
        {
            return parsed;
        }

        warnings.Add($"unsupported appearance.contrast '{raw}'; falling back to 'standard'");
        return AppearanceContrast.Standard;
    }

    private static LayoutSettings ReadLayout(
        IReadOnlyDictionary<string, JsonElement> properties,
        List<string> warnings)
    {
        var defaults = LayoutSettings.Default;
        if (!properties.TryGetValue("layout", out var element) || element.ValueKind != JsonValueKind.Object)
        {
            return defaults;
        }

        var map = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
        foreach (var property in element.EnumerateObject())
        {
            map[property.Name] = property.Value;
        }

        return defaults with
        {
            Id = ReadString(map, "id") ?? defaults.Id,
            Navigation = ReadString(map, "navigation") ?? defaults.Navigation,
            Shelf = ReadString(map, "shelf") ?? defaults.Shelf,
            Density = ReadString(map, "density") ?? defaults.Density,
            Workbench = ReadString(map, "workbench") ?? defaults.Workbench,
            Reader = ReadString(map, "reader") ?? defaults.Reader,
        };
    }

    private static string NormalizeFrontend(string value, List<string> warnings)
    {
        if (string.Equals(value, "builtin.fluent", StringComparison.Ordinal) ||
            string.Equals(value, "builtin.current-v2", StringComparison.Ordinal))
        {
            return value;
        }

        warnings.Add($"unknown theme.frontendId '{value}'; falling back to '{AppearanceDefaults.FrontendId}'");
        return AppearanceDefaults.FrontendId;
    }

    private static string NormalizeVisualTheme(string value, List<string> warnings)
    {
        if (string.Equals(value, "newmanga-default", StringComparison.Ordinal) ||
            string.Equals(value, "builtin.fluent-dark", StringComparison.Ordinal))
        {
            return value;
        }

        warnings.Add($"unknown theme.visualThemeId '{value}'; falling back to '{AppearanceDefaults.VisualThemeId}'");
        return AppearanceDefaults.VisualThemeId;
    }

    private static string? ReadNestedString(
        IReadOnlyDictionary<string, JsonElement> properties,
        string parent,
        string name) =>
        properties.TryGetValue(parent, out var element) && element.ValueKind == JsonValueKind.Object &&
        element.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static bool? ReadNestedBool(
        IReadOnlyDictionary<string, JsonElement> properties,
        string parent,
        string name) =>
        properties.TryGetValue(parent, out var element) && element.ValueKind == JsonValueKind.Object &&
        element.TryGetProperty(name, out var value) && value.ValueKind is JsonValueKind.True or JsonValueKind.False
            ? value.GetBoolean()
            : null;

    private static double? ReadNestedDouble(
        IReadOnlyDictionary<string, JsonElement> properties,
        string parent,
        string name) =>
        properties.TryGetValue(parent, out var element) && element.ValueKind == JsonValueKind.Object &&
        element.TryGetProperty(name, out var value) && value.TryGetDouble(out var number)
            ? number
            : null;
    private static string? ReadString(IReadOnlyDictionary<string, JsonElement> properties, string name) =>
        properties.TryGetValue(name, out var element) && element.ValueKind == JsonValueKind.String
            ? element.GetString()
            : null;

    private static bool? ReadBool(IReadOnlyDictionary<string, JsonElement> properties, string name) =>
        properties.TryGetValue(name, out var element) &&
        element.ValueKind is JsonValueKind.True or JsonValueKind.False
            ? element.GetBoolean()
            : null;

    private static int? ReadInt(IReadOnlyDictionary<string, JsonElement> properties, string name) =>
        properties.TryGetValue(name, out var element) && element.TryGetInt32(out var value) ? value : null;

    private static double? ReadDouble(IReadOnlyDictionary<string, JsonElement> properties, string name) =>
        properties.TryGetValue(name, out var element) && element.TryGetDouble(out var value) ? value : null;

    private static string ToJson(AppearanceMode mode) => mode switch
    {
        AppearanceMode.Light => "light",
        AppearanceMode.Dark => "dark",
        _ => "system",
    };

    private static string ToJson(AppearanceContrast contrast) =>
        contrast == AppearanceContrast.High ? "high" : "standard";

    private static string ToJson(MotionMode mode) => mode switch
    {
        MotionMode.Full => "full",
        MotionMode.Reduce => "reduce",
        _ => "auto",
    };

    private static string ToJson(CornersScale scale) => scale switch
    {
        CornersScale.Sm => "sm",
        CornersScale.Lg => "lg",
        _ => "md",
    };
}
