using NewManga.DesignSystem.Tokens;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Reproducible generation of the shipped theme from the frozen token document: deterministic output,
/// <c>--check</c>-equivalent staleness detection, a clean validator result and no hand-copied token
/// values (every color/size is compared back to <c>tokens.json</c>).
/// </summary>
public sealed class BuiltInThemeGeneratorTests
{
    private static string TokensJson => ThemeFixtures.TokensJson;

    private static BuiltInThemeGenerationResult Generate() => BuiltInThemeGenerator.Generate(TokensJson);

    [Fact]
    public void Committed_artifacts_match_the_frozen_token_source_byte_for_byte()
    {
        var result = Generate();

        Assert.True(
            BuiltInThemeGenerator.IsUpToDate(result, TestPaths.ThemeEngineProject, out var mismatches),
            "generated theme artifacts are stale: " + string.Join(", ", mismatches));
        Assert.Empty(mismatches);
    }

    [Fact]
    public void Generation_is_deterministic()
    {
        var first = Generate();
        var second = Generate();

        Assert.Equal(first.Files.Count, second.Files.Count);
        for (var index = 0; index < first.Files.Count; index++)
        {
            Assert.Equal(first.Files[index].RelativePath, second.Files[index].RelativePath);
            Assert.Equal(first.Files[index].Content, second.Files[index].Content);
        }
    }

    [Fact]
    public void Generated_file_set_matches_the_declared_artifact_paths()
    {
        var result = Generate();

        Assert.Equal(
            BuiltInThemeGenerator.GeneratedFilePaths,
            result.Files.Select(file => file.RelativePath).ToArray());
        Assert.Contains("Themes/newmanga-default.nmtheme", BuiltInThemeGenerator.GeneratedFilePaths);
        Assert.Contains("Generated/ThemeTokenBaseline.g.cs", BuiltInThemeGenerator.GeneratedFilePaths);
    }

    [Fact]
    public void Committed_theme_file_deserializes_to_the_generated_package()
    {
        var result = Generate();
        var committed = ThemePackageJson.Read(File.ReadAllText(TestPaths.DefaultThemeFile));

        Assert.True(committed.Success);
        Assert.Equal(result.Package, committed.Package);
    }

    [Fact]
    public void Embedded_default_theme_is_the_generated_package()
    {
        Assert.True(BuiltInThemes.IsDefaultAvailable);
        Assert.Empty(BuiltInThemes.DefaultLoadIssues);
        Assert.Equal(Generate().Package, BuiltInThemes.Default);
    }

    [Fact]
    public void Generated_theme_validates_without_errors()
    {
        var result = ThemeValidator.Default.Validate(Generate().Package);

        Assert.True(result.IsValid, string.Join(" | ", result.Errors.Select(issue => $"{issue.Code}: {issue.Message}")));
    }

    [Fact]
    public void Generated_descriptor_is_the_shipped_builtin_default()
    {
        var descriptor = Generate().Package.Descriptor;

        Assert.Equal(ThemeDefaults.DefaultThemeId, descriptor.Id);
        Assert.Equal(ThemeKind.BuiltIn, descriptor.Kind);
        Assert.True(descriptor.SupportsLight);
        Assert.True(descriptor.SupportsDark);
        Assert.Contains("builtin", descriptor.Tags);
    }

    [Theory]
    [MemberData(nameof(ThemeFixtures.Variants), MemberType = typeof(ThemeFixtures))]
    public void Generated_colors_are_the_frozen_token_values(PaletteVariant variant)
    {
        var package = Generate().Package;
        var tokens = variant == PaletteVariant.Light ? package.Light.Colors : package.Dark.Colors;
        var scope = variant == PaletteVariant.Light ? TokenMap.LightScope : TokenMap.DarkScope;
        var expected = TokenDocument.Parse(TokensJson)
            .Where(entry => entry.Path.StartsWith(scope, StringComparison.Ordinal) && entry.Type == "color")
            .ToDictionary(
                entry => TokenMap.ColorResourceKey(entry.Path),
                entry => entry.Value,
                StringComparer.Ordinal);

        Assert.Equal(expected.Count, tokens.Count);
        foreach (var (key, value) in expected)
        {
            Assert.Equal(value, tokens[key]);
        }
    }

    [Fact]
    public void Generated_typography_corners_and_motion_match_the_frozen_tokens()
    {
        var package = Generate().Package;

        foreach (var variant in new[] { package.Light, package.Dark })
        {
            Assert.Equal(1.0, variant.Typography.Scale);
            Assert.Equal(LineHeightPreset.Normal, variant.Typography.LineHeight);
            Assert.Equal(ThemeMaterial.Solid, variant.Material);
            Assert.Equal(ThemeElevation.None, variant.Elevation);
            Assert.Equal(new ThemeCorners(0, 2, 3), variant.Corners);
            Assert.Equal(new ThemeMotion(90, 140), variant.Motion);
            Assert.Contains("Segoe UI Variable Text", variant.Typography.Ui, StringComparison.Ordinal);
            Assert.Contains("Cascadia Mono", variant.Typography.Data, StringComparison.Ordinal);
            Assert.Contains("Georgia", variant.Typography.Display, StringComparison.Ordinal);
        }
    }

    [Fact]
    public void Generated_metadata_records_the_generator_and_engine_version()
    {
        var metadata = Generate().Package.Metadata;

        Assert.Equal(ThemeDefaults.EngineVersion, metadata.EngineVersion);
        Assert.Equal(BuiltInThemeGenerator.GeneratorName, metadata.Generator);
        Assert.Empty(metadata.Extra);
        Assert.Empty(metadata.LoadWarnings);
    }

    [Theory]
    [InlineData(PaletteVariant.Dark, "Tokens.Dark.axaml")]
    [InlineData(PaletteVariant.Light, "Tokens.Light.axaml")]
    public void Generated_theme_layer_matches_the_design_system_palette_semantically(
        PaletteVariant variant,
        string designSystemFile)
    {
        // Both artifacts are generated independently from the same frozen token document: the design
        // system's compiled AXAML palette and the theme engine's composed palette must agree exactly.
        var package = Generate().Package;
        var palette = ThemePaletteComposer.Compose(package, variant);
        var designSystem = DesignSystemPalette(designSystemFile);

        Assert.Equal(ThemePaletteComposer.ColorLayerKeyCount, designSystem.Count);
        foreach (var (key, color) in designSystem)
        {
            var brush = Assert.IsAssignableFrom<Avalonia.Media.ISolidColorBrush>(palette[key]);
            Assert.Equal(color, brush.Color);
        }
    }

    [Fact]
    public void Typography_baseline_is_derived_from_the_frozen_tokens()
    {
        var entries = TokenDocument.Parse(TokensJson);
        var bindings = TokenMap.GlobalBindings.ToDictionary(
            binding => binding.TokenPath,
            binding => binding.ResourceKey,
            StringComparer.Ordinal);

        foreach (var entry in entries.Where(entry => entry.Path.StartsWith("font.size.", StringComparison.Ordinal)))
        {
            var key = bindings[entry.Path];
            Assert.True(ThemeTokenBaseline.FontSizes.ContainsKey(key), $"baseline misses font size '{key}'");
            Assert.Equal(TokenValues.ParseDimension(entry.Value), ThemeTokenBaseline.FontSizes[key]);
        }

        foreach (var entry in entries.Where(entry => entry.Path.StartsWith("font.lineHeight.", StringComparison.Ordinal)))
        {
            var key = bindings[entry.Path];
            Assert.True(ThemeTokenBaseline.LineHeightMultipliers.ContainsKey(key));
            Assert.Equal(TokenValues.ParseNumber(entry.Value), ThemeTokenBaseline.LineHeightMultipliers[key]);
        }

        Assert.Equal(6, ThemeTokenBaseline.LineHeightTiers.Count);
        Assert.All(ThemeTokenBaseline.LineHeightTiers, tier =>
        {
            Assert.True(ThemeTokenBaseline.FontSizes.ContainsKey(tier.FontSizeKey));
            Assert.StartsWith("Nm.LineHeight.", tier.ResourceKey, StringComparison.Ordinal);
        });
    }

    [Fact]
    public void Typography_baseline_records_the_source_fingerprint()
    {
        var expected = Hashing.Sha256(TokensJson);

        Assert.Equal(BuiltInThemeGenerator.TokensRelativePath, ThemeTokenBaseline.SourcePath);
        Assert.Equal(ThemeTokenBaseline.SourceSha256, expected);
    }

    private static IReadOnlyDictionary<string, Avalonia.Media.Color> DesignSystemPalette(string fileName)
    {
        var path = Path.Combine(
            TestPaths.RepositoryRoot,
            "apps",
            "desktop-avalonia",
            "src",
            "NewManga.DesignSystem",
            "Themes",
            fileName);
        var text = File.ReadAllText(path);
        var colors = new Dictionary<string, Avalonia.Media.Color>(StringComparer.Ordinal);
        foreach (System.Text.RegularExpressions.Match match in System.Text.RegularExpressions.Regex.Matches(
                     text,
                     "<SolidColorBrush x:Key=\"(?<key>Nm\\.Color\\.[^\"]+)\" Color=\"(?<color>#[0-9A-Fa-f]+)\" />"))
        {
            colors[match.Groups["key"].Value] = Avalonia.Media.Color.Parse(match.Groups["color"].Value);
        }

        return colors;
    }
}
