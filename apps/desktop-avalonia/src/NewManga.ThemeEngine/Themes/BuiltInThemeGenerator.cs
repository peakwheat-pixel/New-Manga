using System.Security.Cryptography;
using System.Text;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Tokens;

namespace NewManga.ThemeEngine;

/// <summary>One generated artifact (project-directory-relative path plus full UTF-8 content, LF newlines).</summary>
public sealed record GeneratedThemeFile(string RelativePath, string Content);

/// <summary>Deterministic output of one theme-generation run.</summary>
public sealed record BuiltInThemeGenerationResult(
    IReadOnlyList<GeneratedThemeFile> Files,
    ThemePackage Package,
    IReadOnlyList<string> Warnings);

/// <summary>
/// Reproducible generator for the shipped default theme (<c>newmanga-default</c>), built from
/// <c>doc/design/redesign-v1/40-fusion/tokens.json</c> so no token value is ever copied by hand
/// (retirement plan §3). It emits two artifacts:
/// <list type="bullet">
///   <item><c>Themes/newmanga-default.nmtheme</c> — the embedded theme package (dark + light),</item>
///   <item><c>Generated/ThemeTokenBaseline.g.cs</c> — the typography baseline the palette composer
///   needs to scale font sizes / line heights for user themes.</item>
/// </list>
/// The output depends only on the frozen token document: no timestamps, no machine paths, LF newlines,
/// ordinal ordering. <c>--check</c> re-runs the pipeline and compares byte-for-byte.
/// </summary>
public static class BuiltInThemeGenerator
{
    /// <summary>Repository-relative path of the frozen token source (single visual authority).</summary>
    public const string TokensRelativePath = "doc/design/redesign-v1/40-fusion/tokens.json";

    /// <summary>File name of the generated default theme package.</summary>
    public const string ThemeFileName = "newmanga-default.nmtheme";

    /// <summary>Generated artifacts, project-directory-relative, in emission order.</summary>
    public static IReadOnlyList<string> GeneratedFilePaths { get; } =
    [
        "Themes/" + ThemeFileName,
        "Generated/ThemeTokenBaseline.g.cs",
    ];

    /// <summary>Number of color tokens contract §2.2 requires for a complete palette.</summary>
    public const int RequiredColorKeyCount = 35;

    /// <summary>Descriptor name of the shipped theme.</summary>
    public const string DefaultThemeName = "New Manga Default";

    /// <summary>Generator identifier written into <see cref="ThemeMetadata.Generator"/>.</summary>
    public const string GeneratorName = "newmanga-theme-gen/1";

    /// <summary>
    /// Line-height tiers published by the design system. The multiplier column mirrors the frozen
    /// DESIGN_SYSTEM §3 typography table (Display/Title 1.25, Body 1.45, Label/Meta 1.35, Data 1.30);
    /// <c>tokens.json</c> only carries the three named multipliers, not the per-tier ratios.
    /// </summary>
    private static readonly (string LineHeightKey, string FontSizeTokenPath, double Multiplier)[] LineHeightTierTable =
    [
        (NmKeys.LineHeight.Display, "font.size.2xl", 1.25),
        (NmKeys.LineHeight.Title, "font.size.xl", 1.25),
        (NmKeys.LineHeight.Body, "font.size.md", 1.45),
        (NmKeys.LineHeight.Label, "font.size.sm", 1.35),
        (NmKeys.LineHeight.Meta, "font.size.xs", 1.35),
        (NmKeys.LineHeight.Data, "font.size.sm", 1.30),
    ];

    /// <summary>Font-size token paths in canonical scale order (xs → 2xl).</summary>
    private static readonly string[] FontSizeTokenPaths =
    [
        "font.size.xs",
        "font.size.sm",
        "font.size.md",
        "font.size.lg",
        "font.size.xl",
        "font.size.2xl",
    ];

    /// <summary>Line-height multiplier token paths (tight / normal / loose).</summary>
    private static readonly string[] LineHeightMultiplierTokenPaths =
    [
        "font.lineHeight.tight",
        "font.lineHeight.normal",
        "font.lineHeight.loose",
    ];

    /// <summary>Builds the default theme package from the frozen token document.</summary>
    public static ThemePackage GenerateDefaultTheme(string tokensJson)
    {
        ArgumentNullException.ThrowIfNull(tokensJson);
        return Generate(tokensJson).Package;
    }

    /// <summary>Runs the generator in memory.</summary>
    public static BuiltInThemeGenerationResult Generate(string tokensJson)
    {
        ArgumentNullException.ThrowIfNull(tokensJson);

        var entries = TokenDocument.Parse(tokensJson);
        var byPath = entries.ToDictionary(static entry => entry.Path, static entry => entry, StringComparer.Ordinal);
        var globalBindings = TokenMap.GlobalBindings.ToDictionary(
            static binding => binding.TokenPath,
            static binding => binding.ResourceKey,
            StringComparer.Ordinal);

        var darkColors = ReadColors(entries, TokenMap.DarkScope, "dark");
        var lightColors = ReadColors(entries, TokenMap.LightScope, "light");
        if (darkColors.Count != RequiredColorKeyCount || lightColors.Count != RequiredColorKeyCount)
        {
            throw new InvalidOperationException(
                $"tokens.json must define {RequiredColorKeyCount} color keys per palette " +
                $"(dark={darkColors.Count}, light={lightColors.Count})");
        }

        if (!darkColors.Keys.SequenceEqual(lightColors.Keys, StringComparer.Ordinal))
        {
            throw new InvalidOperationException("dark and light palettes define different color key sets");
        }

        var fontUi = ReadTokenValue(byPath, "font.family.ui");
        var fontData = ReadTokenValue(byPath, "font.family.data");
        var fontDisplay = ReadTokenValue(byPath, "font.family.display");

        var typography = new ThemeTypography(
            fontUi,
            fontData,
            fontDisplay,
            ThemeTypography.DefaultScale,
            LineHeightPreset.Normal);

        var corners = new ThemeCorners(
            TokenValues.ParseDimension(ReadTokenValue(byPath, "radius.none")),
            TokenValues.ParseDimension(ReadTokenValue(byPath, "radius.sm")),
            TokenValues.ParseDimension(ReadTokenValue(byPath, "radius.md")));

        var motion = new ThemeMotion(
            DurationMilliseconds(ReadTokenValue(byPath, "motion.duration.fast")),
            DurationMilliseconds(ReadTokenValue(byPath, "motion.duration.normal")));

        ThemeTokenSet TokenSet(IReadOnlyDictionary<string, string> colors) =>
            new(colors, typography, corners, ThemeMaterial.Solid, ThemeElevation.None, motion);

        var descriptor = new ThemeDescriptor(
            ThemeDefaults.DefaultThemeId,
            DefaultThemeName,
            "1.0.0",
            "New Manga",
            "Shipped A+C fusion theme generated from the frozen design tokens (dark + light).",
            ThemeKind.BuiltIn,
            ["builtin", "fusion", "a+c"],
            SupportsLight: true,
            SupportsDark: true,
            PreviewHint: null);

        var metadata = new ThemeMetadata
        {
            EngineVersion = ThemeDefaults.EngineVersion,
            Generator = GeneratorName,
            Extra = ThemeMetadata.EmptyExtra,
        };

        var package = new ThemePackage(ThemeDefaults.Schema, descriptor, TokenSet(lightColors), TokenSet(darkColors), metadata);

        var baseline = BuildBaseline(byPath, globalBindings, tokensJson);
        var files = new List<GeneratedThemeFile>(GeneratedFilePaths.Count)
        {
            new("Themes/" + ThemeFileName, ThemePackageJson.Write(package)),
            new("Generated/ThemeTokenBaseline.g.cs", baseline.Content),
        };

        if (!files.Select(static file => file.RelativePath).SequenceEqual(GeneratedFilePaths, StringComparer.Ordinal))
        {
            throw new InvalidOperationException("generated file order drifted from GeneratedFilePaths");
        }

        return new BuiltInThemeGenerationResult(files, package, baseline.Warnings);
    }

    /// <summary>Compares generated artifacts with what is committed on disk (reproducibility gate).</summary>
    public static bool IsUpToDate(
        BuiltInThemeGenerationResult result,
        string themeEngineDirectory,
        out IReadOnlyList<string> mismatches)
    {
        ArgumentNullException.ThrowIfNull(result);
        ArgumentException.ThrowIfNullOrWhiteSpace(themeEngineDirectory);

        var stale = new List<string>();
        foreach (var file in result.Files)
        {
            var path = Path.Combine(
                themeEngineDirectory,
                file.RelativePath.Replace('/', Path.DirectorySeparatorChar));
            if (!File.Exists(path))
            {
                stale.Add($"{file.RelativePath}: missing");
                continue;
            }

            if (!string.Equals(File.ReadAllText(path), file.Content, StringComparison.Ordinal))
            {
                stale.Add($"{file.RelativePath}: content differs");
            }
        }

        mismatches = stale;
        return stale.Count == 0;
    }

    /// <summary>Writes every generated artifact, creating directories as needed.</summary>
    public static void Write(BuiltInThemeGenerationResult result, string themeEngineDirectory)
    {
        ArgumentNullException.ThrowIfNull(result);
        ArgumentException.ThrowIfNullOrWhiteSpace(themeEngineDirectory);

        foreach (var file in result.Files)
        {
            var path = Path.Combine(
                themeEngineDirectory,
                file.RelativePath.Replace('/', Path.DirectorySeparatorChar));
            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            File.WriteAllText(path, file.Content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        }
    }

    private static IReadOnlyDictionary<string, string> ReadColors(
        IReadOnlyList<TokenEntry> entries,
        string scope,
        string label)
    {
        var colors = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (var entry in entries)
        {
            if (!entry.Path.StartsWith(scope, StringComparison.Ordinal))
            {
                continue;
            }

            var key = TokenMap.ColorResourceKey(entry.Path);
            if (!colors.TryAdd(key, entry.Value))
            {
                throw new InvalidOperationException($"color key '{key}' is defined twice in the {label} palette");
            }
        }

        return colors;
    }

    private static string ReadTokenValue(IReadOnlyDictionary<string, TokenEntry> byPath, string tokenPath) =>
        byPath.TryGetValue(tokenPath, out var entry)
            ? entry.Value
            : throw new InvalidOperationException($"tokens.json is missing required token '{tokenPath}'");

    private static int DurationMilliseconds(string raw) =>
        (int)Math.Round(TokenValues.ParseDuration(raw).TotalMilliseconds, MidpointRounding.AwayFromZero);

    private static (string Content, IReadOnlyList<string> Warnings) BuildBaseline(
        IReadOnlyDictionary<string, TokenEntry> byPath,
        IReadOnlyDictionary<string, string> globalBindings,
        string tokensJson)
    {
        var warnings = new List<string>();

        var fontSizePairs = new List<(string Key, string TokenPath, double Value)>(FontSizeTokenPaths.Length);
        foreach (var tokenPath in FontSizeTokenPaths)
        {
            var resourceKey = MapGlobal(globalBindings, tokenPath);
            var value = TokenValues.ParseDimension(ReadTokenValue(byPath, tokenPath));
            fontSizePairs.Add((resourceKey, tokenPath, value));
        }

        var multiplierPairs = new List<(string Key, string TokenPath, double Value)>(LineHeightMultiplierTokenPaths.Length);
        foreach (var tokenPath in LineHeightMultiplierTokenPaths)
        {
            var resourceKey = MapGlobal(globalBindings, tokenPath);
            var value = TokenValues.ParseNumber(ReadTokenValue(byPath, tokenPath));
            multiplierPairs.Add((resourceKey, tokenPath, value));
        }

        var tiers = new List<LineHeightTier>(LineHeightTierTable.Length);
        foreach (var (lineHeightKey, fontSizeTokenPath, multiplier) in LineHeightTierTable)
        {
            var fontSizeKey = MapGlobal(globalBindings, fontSizeTokenPath);
            tiers.Add(new LineHeightTier(lineHeightKey, fontSizeKey, multiplier));
            warnings.Add(
                $"line-height tier {lineHeightKey} = {fontSizeTokenPath} x {TokenValues.FormatDouble(multiplier)} " +
                "(DESIGN_SYSTEM §3)");
        }

        var sha256 = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(tokensJson))).ToLowerInvariant();
        var builder = new StringBuilder(4096);
        builder.AppendLine("// <auto-generated>");
        builder.AppendLine("//   @generated by NewManga.ThemeEngine theme pipeline — do not edit by hand.");
        builder.AppendLine("//   Typography baseline derived from the frozen token document; the palette composer");
        builder.AppendLine("//   scales these values for theme font-size / line-height personality.");
        builder.AppendLine("//   source: " + TokensRelativePath + " (FROZEN)");
        builder.AppendLine("//   tokens.json sha256: " + sha256);
        builder.AppendLine("// </auto-generated>");
        builder.AppendLine();
        builder.AppendLine("namespace NewManga.ThemeEngine;");
        builder.AppendLine();
        builder.AppendLine("/// <summary>");
        builder.AppendLine("/// Typography baseline used by <see cref=\"ThemePaletteComposer\"/>. Values are generated from the");
        builder.AppendLine("/// frozen token document so user themes can scale font sizes without hard-coding base sizes.");
        builder.AppendLine("/// </summary>");
        builder.AppendLine("public static class ThemeTokenBaseline");
        builder.AppendLine("{");
        builder.AppendLine("    /// <summary>Repository-relative path of the frozen token source.</summary>");
        builder.AppendLine("    public const string SourcePath = \"" + TokensRelativePath + "\";");
        builder.AppendLine();
        builder.AppendLine("    /// <summary>SHA-256 of the token document this baseline was generated from.</summary>");
        builder.AppendLine("    public const string SourceSha256 = \"" + sha256 + "\";");
        builder.AppendLine();
        builder.AppendLine("    /// <summary>Base font sizes at scale 1.0, keyed by <c>Nm.FontSize.*</c>.</summary>");
        builder.AppendLine("    public static IReadOnlyDictionary<string, double> FontSizes { get; } =");
        builder.AppendLine("        new System.Collections.ObjectModel.ReadOnlyDictionary<string, double>(");
        builder.AppendLine("            new Dictionary<string, double>(StringComparer.Ordinal)");
        builder.AppendLine("            {");
        foreach (var (key, _, value) in fontSizePairs)
        {
            builder.AppendLine($"                [\"{key}\"] = {TokenValues.FormatDouble(value)},");
        }

        builder.AppendLine("            });");
        builder.AppendLine();
        builder.AppendLine("    /// <summary>Line-height multipliers from the frozen tokens (tight / normal / loose).</summary>");
        builder.AppendLine("    public static IReadOnlyDictionary<string, double> LineHeightMultipliers { get; } =");
        builder.AppendLine("        new System.Collections.ObjectModel.ReadOnlyDictionary<string, double>(");
        builder.AppendLine("            new Dictionary<string, double>(StringComparer.Ordinal)");
        builder.AppendLine("            {");
        foreach (var (key, _, value) in multiplierPairs)
        {
            builder.AppendLine($"                [\"{key}\"] = {TokenValues.FormatDouble(value)},");
        }

        builder.AppendLine("            });");
        builder.AppendLine();
        builder.AppendLine("    /// <summary>Absolute line-height tiers (DESIGN_SYSTEM §3 ratios, Avalonia expects absolute pixels).</summary>");
        builder.AppendLine("    public static IReadOnlyList<LineHeightTier> LineHeightTiers { get; } =");
        builder.AppendLine("    [");
        foreach (var tier in tiers)
        {
            builder.AppendLine(
                $"        new(\"{tier.ResourceKey}\", \"{tier.FontSizeKey}\", {TokenValues.FormatDouble(tier.DesignMultiplier)}),");
        }

        builder.AppendLine("    ];");
        builder.AppendLine("}");

        var content = builder.ToString().Replace("\r\n", "\n", StringComparison.Ordinal);
        return (content, warnings);
    }

    private static string MapGlobal(IReadOnlyDictionary<string, string> globalBindings, string tokenPath) =>
        globalBindings.TryGetValue(tokenPath, out var resourceKey)
            ? resourceKey
            : throw new InvalidOperationException($"tokens.json has no resource-key mapping for '{tokenPath}'");


}
