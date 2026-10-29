using System.Text.Json;

namespace NewManga.ThemeEngine;

/// <summary>Result of reading a theme-package document.</summary>
/// <param name="Package">The parsed package, or null when the document is structurally unusable.</param>
/// <param name="Issues">Everything found while reading (warnings tolerated, errors explained).</param>
public sealed record ThemeReadResult(ThemePackage? Package, IReadOnlyList<ThemeValidationIssue> Issues)
{
    /// <summary>True when a package was produced (it may still carry content errors; the validator decides).</summary>
    public bool Success => Package is not null;

    /// <summary>Returns the package or throws a <see cref="ThemePackageException"/> carrying the findings.</summary>
    public ThemePackage PackageOrThrow() =>
        Package ?? throw new ThemePackageException("theme package document is not usable", Issues);
}

/// <summary>
/// Reads and writes the <c>newmanga.theme/1</c> package document (contract §4/§5). The reader is
/// deliberately hand-rolled over <see cref="JsonDocument"/> (no reflection metadata) so the engine is
/// trim-safe like the App's other JSON paths. Unknown fields are tolerated and reported as warnings;
/// fields that declare a forbidden visual effect (shadow/gradient/blur/mica/acrylic) are reported as
/// errors. Structural failures produce no package; content findings stay on the package itself so the
/// validator can report them together.
/// </summary>
public static class ThemePackageJson
{
    /// <summary>Maximum accepted document size for import/load (1 MiB; a package is a few dozen KiB).</summary>
    public const int MaxDocumentBytes = 1024 * 1024;

    /// <summary>Reads a package document, never throwing for invalid input.</summary>
    public static ThemeReadResult Read(string json)
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
            issues.Add(ThemeValidationIssue.Error(ThemeIssueCodes.JsonInvalid, exception.Message));
            return new ThemeReadResult(null, issues);
        }

        using (document)
        {
            try
            {
                var package = ReadPackage(document.RootElement, issues);
                var enriched = package with
                {
                    Metadata = package.Metadata with { LoadWarnings = issues.ToArray() },
                };
                return new ThemeReadResult(enriched, issues);
            }
            catch (PackageStructureException exception)
            {
                issues.Add(exception.Issue);
                return new ThemeReadResult(null, issues);
            }
        }
    }

    /// <summary>Reads a package document, throwing when the document is structurally unusable.</summary>
    public static ThemePackage ReadOrThrow(string json) => Read(json).PackageOrThrow();

    /// <summary>Writes a package document deterministically (sorted keys, two-space indent, LF, final newline).</summary>
    public static string Write(ThemePackage package)
    {
        ArgumentNullException.ThrowIfNull(package);

        return ThemeJsonWriter.Write(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("schema", package.Schema);
            WriteDescriptor(writer, package.Descriptor);
            WriteTokenSet(writer, "light", package.Light);
            WriteTokenSet(writer, "dark", package.Dark);
            WriteMetadata(writer, package.Metadata);
            writer.WriteEndObject();
        });
    }

    private static void WriteDescriptor(Utf8JsonWriter writer, ThemeDescriptor descriptor)
    {
        writer.WriteStartObject("descriptor");
        writer.WriteString("id", descriptor.Id);
        writer.WriteString("name", descriptor.Name);
        writer.WriteString("version", descriptor.Version);
        WriteNullableString(writer, "author", descriptor.Author);
        WriteNullableString(writer, "description", descriptor.Description);
        writer.WriteString("kind", ThemeEnumNames.ToJson(descriptor.Kind));
        writer.WriteStartArray("tags");
        foreach (var tag in descriptor.Tags ?? [])
        {
            writer.WriteStringValue(tag);
        }

        writer.WriteEndArray();
        writer.WriteBoolean("supportsLight", descriptor.SupportsLight);
        writer.WriteBoolean("supportsDark", descriptor.SupportsDark);
        WriteNullableString(writer, "previewHint", descriptor.PreviewHint);
        writer.WriteEndObject();
    }

    private static void WriteTokenSet(Utf8JsonWriter writer, string propertyName, ThemeTokenSet tokens)
    {
        writer.WriteStartObject(propertyName);

        writer.WriteStartObject("colors");
        foreach (var pair in tokens.Colors.OrderBy(static pair => pair.Key, StringComparer.Ordinal))
        {
            writer.WriteString(pair.Key, pair.Value);
        }

        writer.WriteEndObject();

        writer.WriteStartObject("font");
        writer.WriteStartObject("family");
        writer.WriteString("ui", tokens.Typography.Ui);
        writer.WriteString("data", tokens.Typography.Data);
        writer.WriteString("display", tokens.Typography.Display);
        writer.WriteEndObject();
        writer.WriteNumber("scale", tokens.Typography.Scale);
        writer.WriteString("lineHeight", ThemeEnumNames.ToJson(tokens.Typography.LineHeight));
        writer.WriteEndObject();

        writer.WriteStartObject("corners");
        writer.WriteNumber("none", tokens.Corners.None);
        writer.WriteNumber("sm", tokens.Corners.Sm);
        writer.WriteNumber("md", tokens.Corners.Md);
        writer.WriteEndObject();

        writer.WriteString("material", ThemeEnumNames.ToJson(tokens.Material));
        writer.WriteString("elevation", ThemeEnumNames.ToJson(tokens.Elevation));

        writer.WriteStartObject("motion");
        writer.WriteNumber("fastMs", tokens.Motion.FastMs);
        writer.WriteNumber("normalMs", tokens.Motion.NormalMs);
        writer.WriteEndObject();

        writer.WriteEndObject();
    }

    private static void WriteMetadata(Utf8JsonWriter writer, ThemeMetadata metadata)
    {
        writer.WriteStartObject("metadata");
        writer.WriteString("engineVersion", metadata.EngineVersion);
        WriteNullableString(writer, "generator", metadata.Generator);
        writer.WriteStartObject("extra");
        foreach (var pair in metadata.Extra.OrderBy(static pair => pair.Key, StringComparer.Ordinal))
        {
            writer.WriteString(pair.Key, pair.Value);
        }

        writer.WriteEndObject();
        writer.WriteEndObject();
    }

    private static void WriteNullableString(Utf8JsonWriter writer, string propertyName, string? value)
    {
        if (value is null)
        {
            writer.WriteNull(propertyName);
        }
        else
        {
            writer.WriteString(propertyName, value);
        }
    }

    private static ThemePackage ReadPackage(JsonElement root, List<ThemeValidationIssue> issues)
    {
        if (root.ValueKind != JsonValueKind.Object)
        {
            throw new PackageStructureException(
                ThemeValidationIssue.Error(ThemeIssueCodes.RootNotObject, "theme package root must be a JSON object"));
        }

        var properties = ReadObjectProperties(root, string.Empty, issues);
        ReportUnknownProperties(
            properties,
            ["schema", "descriptor", "light", "dark", "metadata"],
            string.Empty,
            issues);

        if (!properties.TryGetValue("schema", out var schemaElement) ||
            schemaElement.ValueKind != JsonValueKind.String)
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.SchemaUnsupported,
                "theme package must declare a string 'schema' field (expected 'newmanga.theme/1')",
                "schema"));
        }

        var schema = schemaElement.GetString()!;
        if (!string.Equals(schema, ThemeDefaults.Schema, StringComparison.Ordinal))
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.SchemaUnsupported,
                $"unsupported theme schema '{schema}'; this engine reads '{ThemeDefaults.Schema}'",
                "schema"));
        }

        var descriptor = ReadDescriptor(RequireObject(properties, "descriptor", string.Empty), issues);
        var light = ReadTokenSet(RequireObject(properties, "light", string.Empty), "light", issues);
        var dark = ReadTokenSet(RequireObject(properties, "dark", string.Empty), "dark", issues);

        ThemeMetadata metadata;
        if (properties.TryGetValue("metadata", out var metadataElement))
        {
            if (metadataElement.ValueKind != JsonValueKind.Object)
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.FieldType, "'metadata' must be an object", "metadata"));
                metadata = new ThemeMetadata();
            }
            else
            {
                metadata = ReadMetadata(metadataElement, issues);
            }
        }
        else
        {
            metadata = new ThemeMetadata();
        }

        return new ThemePackage(schema, descriptor, light, dark, metadata);
    }

    private static ThemeDescriptor ReadDescriptor(JsonElement element, List<ThemeValidationIssue> issues)
    {
        const string Path = "descriptor";
        var properties = ReadObjectProperties(element, Path, issues);
        ReportUnknownProperties(
            properties,
            ["id", "name", "version", "author", "description", "kind", "tags", "supportsLight", "supportsDark", "previewHint"],
            Path,
            issues);

        var id = ReadRequiredString(properties, "id", Path, issues);
        var name = ReadRequiredString(properties, "name", Path, issues);
        var version = ReadOptionalString(properties, "version", Path, issues) ?? "1.0.0";
        var author = ReadOptionalString(properties, "author", Path, issues);
        var description = ReadOptionalString(properties, "description", Path, issues);
        var previewHint = ReadOptionalString(properties, "previewHint", Path, issues);

        var kind = ThemeKind.User;
        if (properties.TryGetValue("kind", out var kindElement))
        {
            if (kindElement.ValueKind == JsonValueKind.String &&
                ThemeEnumNames.TryParseKind(kindElement.GetString(), out var parsedKind))
            {
                kind = parsedKind;
            }
            else
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.EnumInvalid, $"unsupported descriptor.kind '{kindElement.GetRawText()}'", $"{Path}.kind"));
            }
        }

        var tags = ReadStringArray(properties, "tags", Path, issues);
        var supportsLight = ReadOptionalBoolean(properties, "supportsLight", Path, issues, fallback: true);
        var supportsDark = ReadOptionalBoolean(properties, "supportsDark", Path, issues, fallback: true);

        return new ThemeDescriptor(
            id ?? string.Empty,
            name ?? string.Empty,
            version,
            author,
            description,
            kind,
            tags,
            supportsLight,
            supportsDark,
            previewHint);
    }

    private static ThemeTokenSet ReadTokenSet(JsonElement element, string scope, List<ThemeValidationIssue> issues)
    {
        var properties = ReadObjectProperties(element, scope, issues);
        ReportUnknownProperties(properties, ["colors", "font", "corners", "material", "elevation", "motion"], scope, issues);

        var colors = new Dictionary<string, string>(StringComparer.Ordinal);
        var colorsElement = RequireObject(properties, "colors", scope);
        foreach (var colorProperty in colorsElement.EnumerateObject())
        {
            if (colorProperty.Value.ValueKind != JsonValueKind.String)
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.FieldType,
                    $"color '{colorProperty.Name}' must be a string",
                    $"{scope}.colors.{colorProperty.Name}"));
                continue;
            }

            var colorValue = colorProperty.Value.GetString()!;
            if (!colors.TryAdd(colorProperty.Name, colorValue))
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.DuplicateField,
                    $"color '{colorProperty.Name}' appears more than once; the last value wins",
                    $"{scope}.colors.{colorProperty.Name}"));
                colors[colorProperty.Name] = colorValue;
            }
        }

        var typography = ReadTypography(RequireObject(properties, "font", scope), scope, issues);
        var corners = ReadCorners(RequireObject(properties, "corners", scope), scope, issues);
        var material = ReadEnum(
            properties,
            "material",
            scope,
            issues,
            ThemeEnumNames.TryParseMaterial,
            ThemeMaterial.Solid);
        var elevation = ReadEnum(
            properties,
            "elevation",
            scope,
            issues,
            ThemeEnumNames.TryParseElevation,
            ThemeElevation.None);
        var motion = ReadMotion(RequireObject(properties, "motion", scope), scope, issues);

        return new ThemeTokenSet(colors, typography, corners, material, elevation, motion);
    }

    private static ThemeTypography ReadTypography(JsonElement element, string scope, List<ThemeValidationIssue> issues)
    {
        var path = $"{scope}.font";
        var properties = ReadObjectProperties(element, path, issues);
        ReportUnknownProperties(properties, ["family", "scale", "lineHeight"], path, issues);

        var familyElement = RequireObject(properties, "family", path);
        var familyPath = $"{path}.family";
        var family = ReadObjectProperties(familyElement, familyPath, issues);
        ReportUnknownProperties(family, ["ui", "data", "display"], familyPath, issues);

        var ui = ReadRequiredString(family, "ui", familyPath, issues);
        var data = ReadRequiredString(family, "data", familyPath, issues);
        var display = ReadRequiredString(family, "display", familyPath, issues);
        var scale = ReadOptionalNumber(properties, "scale", path, issues, ThemeTypography.DefaultScale);

        var lineHeight = LineHeightPreset.Normal;
        if (properties.TryGetValue("lineHeight", out var lineHeightElement))
        {
            if (lineHeightElement.ValueKind == JsonValueKind.String &&
                ThemeEnumNames.TryParseLineHeight(lineHeightElement.GetString(), out var parsed))
            {
                lineHeight = parsed;
            }
            else
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.EnumInvalid,
                    $"unsupported font.lineHeight '{lineHeightElement.GetRawText()}'",
                    $"{path}.lineHeight"));
            }
        }

        return new ThemeTypography(
            ui ?? string.Empty,
            data ?? string.Empty,
            display ?? string.Empty,
            scale,
            lineHeight);
    }

    private static ThemeCorners ReadCorners(JsonElement element, string scope, List<ThemeValidationIssue> issues)
    {
        var path = $"{scope}.corners";
        var properties = ReadObjectProperties(element, path, issues);
        ReportUnknownProperties(properties, ["none", "sm", "md"], path, issues);

        return new ThemeCorners(
            ReadRequiredNumber(properties, "none", path, issues),
            ReadRequiredNumber(properties, "sm", path, issues),
            ReadRequiredNumber(properties, "md", path, issues));
    }

    private static ThemeMotion ReadMotion(JsonElement element, string scope, List<ThemeValidationIssue> issues)
    {
        var path = $"{scope}.motion";
        var properties = ReadObjectProperties(element, path, issues);
        ReportUnknownProperties(properties, ["fastMs", "normalMs"], path, issues);

        return new ThemeMotion(
            ReadRequiredInt32(properties, "fastMs", path, issues),
            ReadRequiredInt32(properties, "normalMs", path, issues));
    }

    private static ThemeMetadata ReadMetadata(JsonElement element, List<ThemeValidationIssue> issues)
    {
        const string Path = "metadata";
        var properties = ReadObjectProperties(element, Path, issues);
        ReportUnknownProperties(properties, ["engineVersion", "generator", "extra"], Path, issues);

        var engineVersion = ReadOptionalString(properties, "engineVersion", Path, issues) ?? ThemeDefaults.EngineVersion;
        var generator = ReadOptionalString(properties, "generator", Path, issues);

        var extra = new Dictionary<string, string>(StringComparer.Ordinal);
        if (properties.TryGetValue("extra", out var extraElement))
        {
            if (extraElement.ValueKind != JsonValueKind.Object)
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.FieldType, "'metadata.extra' must be an object", $"{Path}.extra"));
            }
            else
            {
                foreach (var property in extraElement.EnumerateObject())
                {
                    extra[property.Name] = property.Value.ValueKind switch
                    {
                        JsonValueKind.String => property.Value.GetString()!,
                        JsonValueKind.Null => string.Empty,
                        _ => property.Value.GetRawText(),
                    };
                }
            }
        }

        return new ThemeMetadata
        {
            EngineVersion = engineVersion,
            Generator = generator,
            Extra = extra,
        };
    }

    private static T ReadEnum<T>(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string scope,
        List<ThemeValidationIssue> issues,
        TryParseEnum<T> tryParse,
        T fallback)
        where T : struct
    {
        if (!properties.TryGetValue(name, out var element))
        {
            return fallback;
        }

        if (element.ValueKind == JsonValueKind.String && tryParse(element.GetString(), out var parsed))
        {
            return parsed;
        }

        issues.Add(ThemeValidationIssue.Error(
            ThemeIssueCodes.EnumInvalid,
            $"unsupported {name} value '{element.GetRawText()}'",
            $"{scope}.{name}"));
        return fallback;
    }

    private delegate bool TryParseEnum<T>(string? raw, out T value)
        where T : struct;

    private static Dictionary<string, JsonElement> ReadObjectProperties(
        JsonElement element,
        string path,
        List<ThemeValidationIssue> issues)
    {
        var properties = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
        foreach (var property in element.EnumerateObject())
        {
            if (properties.ContainsKey(property.Name))
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.DuplicateField,
                    $"field '{Join(path, property.Name)}' appears more than once; the last value wins",
                    Join(path, property.Name)));
            }

            properties[property.Name] = property.Value;
        }

        return properties;
    }

    /// <summary>
    /// Reports every property not in <paramref name="known"/>. Unknown fields are tolerated
    /// (warning) unless their name declares a visual effect the design system forbids (error).
    /// </summary>
    private static void ReportUnknownProperties(
        IReadOnlyDictionary<string, JsonElement> properties,
        IReadOnlyCollection<string> known,
        string path,
        List<ThemeValidationIssue> issues)
    {
        foreach (var name in properties.Keys)
        {
            if (known.Contains(name, StringComparer.Ordinal))
            {
                continue;
            }

            var fullPath = Join(path, name);
            if (ThemeForbiddenFields.IsForbidden(name))
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.ForbiddenDeclaration,
                    $"field '{fullPath}' declares a visual effect the design system forbids " +
                    "(no shadow, gradient, blur, backdrop-filter, mica or acrylic)",
                    fullPath));
            }
            else
            {
                issues.Add(ThemeValidationIssue.Warning(
                    ThemeIssueCodes.UnknownField,
                    $"unknown field '{fullPath}' was ignored",
                    fullPath));
            }
        }
    }

    private static JsonElement RequireObject(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path)
    {
        if (!properties.TryGetValue(name, out var element))
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldMissing,
                $"required object '{Join(path, name)}' is missing",
                Join(path, name)));
        }

        if (element.ValueKind != JsonValueKind.Object)
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldType,
                $"'{Join(path, name)}' must be an object",
                Join(path, name)));
        }

        return element;
    }

    private static string? ReadRequiredString(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path,
        List<ThemeValidationIssue> issues)
    {
        if (!properties.TryGetValue(name, out var element))
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldMissing,
                $"required string '{Join(path, name)}' is missing",
                Join(path, name)));
        }

        if (element.ValueKind != JsonValueKind.String)
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldType,
                $"'{Join(path, name)}' must be a string",
                Join(path, name)));
        }

        return element.GetString();
    }

    private static string? ReadOptionalString(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path,
        List<ThemeValidationIssue> issues)
    {
        if (!properties.TryGetValue(name, out var element) || element.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (element.ValueKind != JsonValueKind.String)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldType,
                $"'{Join(path, name)}' must be a string",
                Join(path, name)));
            return null;
        }

        return element.GetString();
    }

    private static double ReadRequiredNumber(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path,
        List<ThemeValidationIssue> issues)
    {
        if (!properties.TryGetValue(name, out var element))
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldMissing,
                $"required number '{Join(path, name)}' is missing",
                Join(path, name)));
        }

        if (element.ValueKind != JsonValueKind.Number || !element.TryGetDouble(out var value))
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldType,
                $"'{Join(path, name)}' must be a number",
                Join(path, name)));
        }

        return value;
    }

    private static double ReadOptionalNumber(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path,
        List<ThemeValidationIssue> issues,
        double fallback)
    {
        if (!properties.TryGetValue(name, out var element))
        {
            return fallback;
        }

        if (element.ValueKind != JsonValueKind.Number || !element.TryGetDouble(out var value))
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldType,
                $"'{Join(path, name)}' must be a number",
                Join(path, name)));
            return fallback;
        }

        return value;
    }

    private static int ReadRequiredInt32(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path,
        List<ThemeValidationIssue> issues)
    {
        if (!properties.TryGetValue(name, out var element))
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldMissing,
                $"required integer '{Join(path, name)}' is missing",
                Join(path, name)));
        }

        if (element.ValueKind != JsonValueKind.Number || !element.TryGetInt32(out var value))
        {
            throw new PackageStructureException(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldType,
                $"'{Join(path, name)}' must be an integer",
                Join(path, name)));
        }

        return value;
    }

    private static bool ReadOptionalBoolean(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path,
        List<ThemeValidationIssue> issues,
        bool fallback)
    {
        if (!properties.TryGetValue(name, out var element))
        {
            return fallback;
        }

        if (element.ValueKind is JsonValueKind.True or JsonValueKind.False)
        {
            return element.GetBoolean();
        }

        issues.Add(ThemeValidationIssue.Error(
            ThemeIssueCodes.FieldType,
            $"'{Join(path, name)}' must be a boolean",
            Join(path, name)));
        return fallback;
    }

    private static IReadOnlyList<string> ReadStringArray(
        IReadOnlyDictionary<string, JsonElement> properties,
        string name,
        string path,
        List<ThemeValidationIssue> issues)
    {
        if (!properties.TryGetValue(name, out var element) || element.ValueKind == JsonValueKind.Null)
        {
            return [];
        }

        if (element.ValueKind != JsonValueKind.Array)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.FieldType,
                $"'{Join(path, name)}' must be an array of strings",
                Join(path, name)));
            return [];
        }

        var values = new List<string>(element.GetArrayLength());
        foreach (var item in element.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.String)
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.FieldType,
                    $"'{Join(path, name)}' entries must be strings",
                    Join(path, name)));
                continue;
            }

            values.Add(item.GetString()!);
        }

        return values;
    }

    private static string Join(string path, string name) => path.Length == 0 ? name : path + "." + name;

    /// <summary>Thrown when a document is structurally unusable (no package can be produced).</summary>
    private sealed class PackageStructureException : Exception
    {
        public PackageStructureException(ThemeValidationIssue issue)
            : base(issue.Message)
        {
            Issue = issue;
        }

        public ThemeValidationIssue Issue { get; }
    }
}

/// <summary>
/// Names that declare visual treatments the frozen design system forbids (DESIGN_SYSTEM §9:
/// gradients, glass/mica/acrylic, blur filters, colored shadows). A theme package may not define them,
/// so an unknown field with one of these names is an error rather than a tolerated warning.
/// </summary>
internal static class ThemeForbiddenFields
{
    /// <summary>
    /// Effect vocabulary the frozen design system forbids. Matching is word-based (camelCase, kebab and
    /// snake case are split) so a field such as <c>boxShadow</c> is caught while a harmless future field
    /// like <c>shadowLess</c> would still be reported — the engine prefers a false positive over silently
    /// accepting a forbidden visual-effect declaration.
    /// </summary>
    private static readonly HashSet<string> ForbiddenWords = new(StringComparer.OrdinalIgnoreCase)
    {
        "shadow",
        "shadows",
        "gradient",
        "gradients",
        "blur",
        "blurred",
        "backdrop",
        "backdropfilter",
        "filter",
        "filters",
        "mica",
        "acrylic",
        "glass",
        "glassmorphism",
        "glow",
    };

    public static bool IsForbidden(string fieldName)
    {
        if (string.IsNullOrEmpty(fieldName))
        {
            return false;
        }

        foreach (var word in SplitWords(fieldName))
        {
            if (ForbiddenWords.Contains(word))
            {
                return true;
            }
        }

        return false;
    }

    private static IEnumerable<string> SplitWords(string value)
    {
        var current = new System.Text.StringBuilder(16);
        for (var index = 0; index < value.Length; index++)
        {
            var character = value[index];
            if (!char.IsLetterOrDigit(character))
            {
                if (current.Length > 0)
                {
                    yield return current.ToString();
                    current.Clear();
                }

                continue;
            }

            if (current.Length > 0 && char.IsUpper(character) && !char.IsUpper(value[index - 1]))
            {
                yield return current.ToString();
                current.Clear();
            }

            current.Append(character);
        }

        if (current.Length > 0)
        {
            yield return current.ToString();
        }
    }
}