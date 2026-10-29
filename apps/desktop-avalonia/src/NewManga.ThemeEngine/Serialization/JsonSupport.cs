using System.Buffers;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;

namespace NewManga.ThemeEngine;

/// <summary>
/// Deterministic UTF-8 JSON emission shared by every Theme Engine document (packages and settings).
/// Two-space indent, LF newlines, trailing newline, no timestamps and no machine paths, so a
/// regenerate produces byte-identical files (<c>--check</c> guard). The relaxed encoder keeps theme
/// documents human-readable (quotes/plus signs are not escaped) — these files are authored, imported
/// and exported by users, never rendered as HTML.
/// </summary>
internal static class ThemeJsonWriter
{
    private static readonly JavaScriptEncoder Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping;

    /// <summary>Runs <paramref name="body"/> against a deterministic writer and returns the document text.</summary>
    public static string Write(Action<Utf8JsonWriter> body)
    {
        ArgumentNullException.ThrowIfNull(body);

        var buffer = new ArrayBufferWriter<byte>(initialCapacity: 4096);
        var options = new JsonWriterOptions
        {
            Indented = true,
            IndentSize = 2,
            NewLine = "\n",
            Encoder = Encoder,
            SkipValidation = false,
        };

        using (var writer = new Utf8JsonWriter(buffer, options))
        {
            body(writer);
        }

        return Encoding.UTF8.GetString(buffer.WrittenSpan) + "\n";
    }
}

/// <summary>
/// Canonical string forms for every enum that appears in a theme/settings document. Values are
/// lowercase kebab-case; reading is tolerant of case, underscores and hyphens.
/// </summary>
internal static class ThemeEnumNames
{
    public static string ToJson(ThemeKind value) => value switch
    {
        ThemeKind.BuiltIn => "builtin",
        ThemeKind.User => "user",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported ThemeKind"),
    };

    public static string ToJson(AppearanceMode value) => value switch
    {
        AppearanceMode.System => "system",
        AppearanceMode.Light => "light",
        AppearanceMode.Dark => "dark",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported AppearanceMode"),
    };

    public static string ToJson(ContrastMode value) => value switch
    {
        ContrastMode.Standard => "standard",
        ContrastMode.High => "high",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported ContrastMode"),
    };

    public static string ToJson(LineHeightPreset value) => value switch
    {
        LineHeightPreset.Tight => "tight",
        LineHeightPreset.Normal => "normal",
        LineHeightPreset.Loose => "loose",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported LineHeightPreset"),
    };

    public static string ToJson(ThemeMaterial value) => value switch
    {
        ThemeMaterial.Solid => "solid",
        ThemeMaterial.None => "none",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported ThemeMaterial"),
    };

    public static string ToJson(ThemeElevation value) => value switch
    {
        ThemeElevation.None => "none",
        ThemeElevation.Raised => "raised",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported ThemeElevation"),
    };

    public static string ToJson(LayoutNavigation value) => value switch
    {
        LayoutNavigation.TopBand => "top-band",
        LayoutNavigation.Sidebar => "sidebar",
        LayoutNavigation.Dock => "dock",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported LayoutNavigation"),
    };

    public static string ToJson(ShelfLayout value) => value switch
    {
        ShelfLayout.Grid => "grid",
        ShelfLayout.List => "list",
        ShelfLayout.Masonry => "masonry",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported ShelfLayout"),
    };

    public static string ToJson(Density value) => value switch
    {
        Density.Comfortable => "comfortable",
        Density.Compact => "compact",
        Density.Spacious => "spacious",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported Density"),
    };

    public static string ToJson(WorkbenchLayout value) => value switch
    {
        WorkbenchLayout.Stacked => "stacked",
        WorkbenchLayout.Split => "split",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported WorkbenchLayout"),
    };

    public static string ToJson(ReaderLayout value) => value switch
    {
        ReaderLayout.FitPage => "fit-page",
        ReaderLayout.FitWidth => "fit-width",
        ReaderLayout.DoublePage => "double-page",
        ReaderLayout.Webtoon => "webtoon",
        _ => throw new ArgumentOutOfRangeException(nameof(value), value, "unsupported ReaderLayout"),
    };

    public static bool TryParseKind(string? raw, out ThemeKind value) =>
        TryParse(raw, out value, ThemeKind.User, ("builtin", ThemeKind.BuiltIn), ("built-in", ThemeKind.BuiltIn),
            ("user", ThemeKind.User));

    public static bool TryParseAppearance(string? raw, out AppearanceMode value) =>
        TryParse(raw, out value, AppearanceMode.System, ("system", AppearanceMode.System),
            ("light", AppearanceMode.Light), ("dark", AppearanceMode.Dark));

    public static bool TryParseContrast(string? raw, out ContrastMode value) =>
        TryParse(raw, out value, ContrastMode.Standard, ("standard", ContrastMode.Standard),
            ("high", ContrastMode.High));

    public static bool TryParseLineHeight(string? raw, out LineHeightPreset value) =>
        TryParse(raw, out value, LineHeightPreset.Normal, ("tight", LineHeightPreset.Tight),
            ("normal", LineHeightPreset.Normal), ("loose", LineHeightPreset.Loose));

    public static bool TryParseMaterial(string? raw, out ThemeMaterial value) =>
        TryParse(raw, out value, ThemeMaterial.Solid, ("solid", ThemeMaterial.Solid), ("none", ThemeMaterial.None));

    public static bool TryParseElevation(string? raw, out ThemeElevation value) =>
        TryParse(raw, out value, ThemeElevation.None, ("none", ThemeElevation.None),
            ("raised", ThemeElevation.Raised));

    public static bool TryParseNavigation(string? raw, out LayoutNavigation value) =>
        TryParse(raw, out value, LayoutNavigation.TopBand, ("topband", LayoutNavigation.TopBand),
            ("sidebar", LayoutNavigation.Sidebar), ("dock", LayoutNavigation.Dock));

    public static bool TryParseShelf(string? raw, out ShelfLayout value) =>
        TryParse(raw, out value, ShelfLayout.Grid, ("grid", ShelfLayout.Grid), ("list", ShelfLayout.List),
            ("masonry", ShelfLayout.Masonry));

    public static bool TryParseDensity(string? raw, out Density value) =>
        TryParse(raw, out value, Density.Comfortable, ("comfortable", Density.Comfortable),
            ("compact", Density.Compact), ("spacious", Density.Spacious));

    public static bool TryParseWorkbench(string? raw, out WorkbenchLayout value) =>
        TryParse(raw, out value, WorkbenchLayout.Stacked, ("stacked", WorkbenchLayout.Stacked),
            ("split", WorkbenchLayout.Split));

    public static bool TryParseReader(string? raw, out ReaderLayout value) =>
        TryParse(raw, out value, ReaderLayout.FitPage, ("fitpage", ReaderLayout.FitPage),
            ("fitwidth", ReaderLayout.FitWidth), ("doublepage", ReaderLayout.DoublePage),
            ("webtoon", ReaderLayout.Webtoon));

    private static bool TryParse<T>(string? raw, out T value, T fallback, params (string Name, T Value)[] options)
        where T : struct
    {
        if (!string.IsNullOrWhiteSpace(raw))
        {
            var normalized = Normalize(raw);
            foreach (var (name, candidate) in options)
            {
                if (string.Equals(normalized, Normalize(name), StringComparison.Ordinal))
                {
                    value = candidate;
                    return true;
                }
            }
        }

        value = fallback;
        return false;
    }

    private static string Normalize(string raw)
    {
        var builder = new StringBuilder(raw.Length);
        foreach (var character in raw.Trim())
        {
            if (character is '-' or '_' or ' ')
            {
                continue;
            }

            builder.Append(char.ToLowerInvariant(character));
        }

        return builder.ToString();
    }
}
