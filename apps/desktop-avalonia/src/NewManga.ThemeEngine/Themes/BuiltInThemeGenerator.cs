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

    /// <summary>File name of the generated Fluent dark theme package (FEA-06-PREREQ-1 AC5).</summary>
    public const string FluentDarkThemeFileName = "fluent-dark.nmtheme";

    /// <summary>Theme id of the Fluent dark package.</summary>
    public const string FluentDarkThemeId = "builtin.fluent-dark";

    /// <summary>Generated artifacts, project-directory-relative, in emission order.</summary>
    public static IReadOnlyList<string> GeneratedFilePaths =>
    [
        "Themes/" + ThemeFileName,
        "Themes/" + FluentDarkThemeFileName,
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

    /// <summary>
    /// FEA-06-PREREQ-2 P6 / C-02 V-03: the Fluent acrylic material colours come from the frozen Fluent
    /// design baseline (design 01 §41-42, recorded there as AARRGGBB) and are carried by the Fluent
    /// package's <c>colors</c> map — the design system deliberately keeps them out of the global token
    /// dictionary (theme-layer values). The package is dark-only, so both slots repeat the dark values
    /// (impl-r4 P2-8).
    /// </summary>
    private const string FluentAcrylicBaseCss = "#1F1F1F";

    /// <summary>Design <c>#33007ACC</c> (AARRGGBB) as a CSS colour: alpha 0x33 ≈ 20%.</summary>
    private const string FluentAcrylicTintCss = "rgba(0,122,204,0.2)";

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

        var derivationWarnings = new List<string>();

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

        // R-15 registers the slow tier (default 220ms) as a design-system contract extension; the frozen
        // token document still carries only instant/fast/normal, so use the registered default until a
        // motion.duration.slow token exists and then read it without touching this code path.
        var slowMotionMs = byPath.TryGetValue("motion.duration.slow", out var slowMotionEntry)
            ? DurationMilliseconds(slowMotionEntry.Value)
            : ThemeMotion.DefaultSlowMs;
        if (!byPath.ContainsKey("motion.duration.slow"))
        {
            derivationWarnings.Add(
                $"motion slow duration = {ThemeMotion.DefaultSlowMs}ms (R-15 default; no 'motion.duration.slow' token in the frozen baseline)");
        }

        var motion = new ThemeMotion(
            DurationMilliseconds(ReadTokenValue(byPath, "motion.duration.fast")),
            DurationMilliseconds(ReadTokenValue(byPath, "motion.duration.normal")),
            slowMotionMs);

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

        // FEA-06-PREREQ-2 AC5: the Fluent dark package is generated from the same frozen tokens
        // (dark palette, Fluent material/elevation semantics) so ThemeGen --check covers it too.
        var fluentDescriptor = new ThemeDescriptor(
            FluentDarkThemeId,
            "Fluent Dark",
            "1.0.0",
            "New Manga",
            "Fluent visual theme (dark-only) for the Fluent frontend; generated from the frozen design tokens.",
            ThemeKind.BuiltIn,
            ["builtin", "fluent"],
            SupportsLight: false,
            SupportsDark: true,
            PreviewHint: null);
        // C-02 V-03 / FEA-06-PREREQ-2 P6: the Fluent package carries the acrylic material colours in its
        // colors map; the Current theme keeps the frozen 35-key palette and omits them.
        var fluentColors = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (var pair in darkColors)
        {
            fluentColors[pair.Key] = pair.Value;
        }

        fluentColors[NmKeys.Material.Acrylic.Base] = FluentAcrylicBaseCss;
        fluentColors[NmKeys.Material.Acrylic.Tint] = FluentAcrylicTintCss;
        derivationWarnings.Add(
            $"Fluent acrylic material colours (theme layer): {NmKeys.Material.Acrylic.Base}={FluentAcrylicBaseCss}, " +
            $"{NmKeys.Material.Acrylic.Tint}={FluentAcrylicTintCss} (design 01 §41-42)");
        ThemeTokenSet FluentTokenSet(IReadOnlyDictionary<string, string> colors) =>
            new(colors, typography, corners, ThemeMaterial.Solid, ThemeElevation.Raised, motion);
        // C-02 §4 / FEA-06-PREREQ-2 P7: the `nm.fluent.visual/1` manifest lives in metadata.extra (the
        // smallest carrier the existing package schema already has); the Current theme declares no manifest.
        var fluentMetadata = new ThemeMetadata
        {
            EngineVersion = ThemeDefaults.EngineVersion,
            Generator = GeneratorName,
            Extra = new System.Collections.ObjectModel.ReadOnlyDictionary<string, string>(
                new SortedDictionary<string, string>(StringComparer.Ordinal)
                {
                    [ThemeDefaults.FluentVisualManifestKey] = ThemeDefaults.FluentVisualManifestVersion,
                }),
        };
        var fluentPackage = new ThemePackage(
            ThemeDefaults.Schema,
            fluentDescriptor,
            // dark-only package: the light slot repeats the dark palette so an accidental
            // light-mode consumer still resolves to the shipped (dark) values (impl-r4 P2-8).
            FluentTokenSet(fluentColors),
            FluentTokenSet(fluentColors),
            fluentMetadata);

        var baseline = BuildBaseline(byPath, globalBindings, tokensJson);
        var files = new List<GeneratedThemeFile>(GeneratedFilePaths.Count)
        {
            new("Themes/" + ThemeFileName, ThemePackageJson.Write(package)),
            new("Themes/" + FluentDarkThemeFileName, ThemePackageJson.Write(fluentPackage)),
            new("Generated/ThemeTokenBaseline.g.cs", baseline.Content),
        };

        if (!files.Select(static file => file.RelativePath).SequenceEqual(GeneratedFilePaths, StringComparer.Ordinal))
        {
            throw new InvalidOperationException("generated file order drifted from GeneratedFilePaths");
        }

        return new BuiltInThemeGenerationResult(files, package, [.. derivationWarnings, .. baseline.Warnings]);
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
