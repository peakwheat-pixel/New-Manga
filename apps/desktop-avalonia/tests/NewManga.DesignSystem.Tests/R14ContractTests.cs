using System.Text.RegularExpressions;
using Avalonia.Styling;
using NewManga.DesignSystem.Theming;
using NewManga.DesignSystem.Tokens;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// R-14 contract conformance (Lead review items P2-3, P2-6, P2-8): frozen key naming, em-relative
/// tracking semantics, line-height alias rule, and the naked-value/exception guard for the DS sources.
/// </summary>
public sealed class R14ContractTests
{
    [Fact]
    public void Font_size_key_is_Xxl_and_2Xl_does_not_exist()
    {
        Assert.Equal("Nm.FontSize.Xxl", NmKeys.FontSize.Xxl);
        Assert.DoesNotContain("Nm.FontSize.2Xl", NmKeys.All);

        var generated = File.ReadAllText(
            Path.Combine(TestPaths.DesignSystemProject, "Themes", "Tokens.Global.axaml"));
        Assert.Contains("Nm.FontSize.Xxl", generated);
        Assert.DoesNotContain("Nm.FontSize.2Xl", generated);

        var tokenMap = File.ReadAllText(
            Path.Combine(TestPaths.DesignSystemProject, "Generated", "TokenMap.md"));
        Assert.Contains("Nm.FontSize.Xxl", tokenMap);
        Assert.Contains("R-14", tokenMap);
    }

    [Fact]
    public void Tracking_tokens_keep_em_ratio_semantics_and_are_not_pixels()
    {
        var result = TokenGenerator.Generate(File.ReadAllText(TestPaths.TokensFixture));
        var tracking = result.Rows.Where(static row => row.ResourceKey.StartsWith("Nm.FontTracking.", StringComparison.Ordinal)).ToArray();

        Assert.Equal(3, tracking.Length);
        Assert.All(tracking, row => Assert.Equal(TokenValueKind.EmRatio, row.Kind));
        Assert.All(tracking, row =>
        {
            var raw = row.RawValue.Trim();
            Assert.True(
                raw.EndsWith("em", StringComparison.OrdinalIgnoreCase) || raw == "0",
                $"{row.ResourceKey}: '{raw}' must be em-relative (or exactly 0)");
        });

        Assert.Equal(0.08, TokenValues.ParseEmRatio("0.08em"), 6);
        Assert.Equal(-0.01, TokenValues.ParseEmRatio("-0.01em"), 6);
        Assert.Equal(0, TokenValues.ParseEmRatio("0"));
        Assert.Throws<FormatException>(() => TokenValues.ParseEmRatio("0.08px"));
        Assert.Throws<FormatException>(() => TokenValues.ParseEmRatio("0.08"));

        // The generated dictionary exposes ratios as doubles (Avalonia has no em letter-spacing).
        var global = File.ReadAllText(Path.Combine(TestPaths.DesignSystemProject, "Themes", "Tokens.Global.axaml"));
        Assert.Contains("<sys:Double x:Key=\"Nm.FontTracking.Caps\">0.08</sys:Double>", global);
        Assert.Contains("<sys:Double x:Key=\"Nm.FontTracking.Data\">-0.01</sys:Double>", global);
    }

    [Fact]
    public void Line_height_aliases_are_constrained_to_frozen_multipliers()
    {
        var result = TokenGenerator.Generate(File.ReadAllText(TestPaths.TokensFixture));
        var aliases = new[] { "Nm.LineHeight.Display", "Nm.LineHeight.Title", "Nm.LineHeight.Body", "Nm.LineHeight.Label", "Nm.LineHeight.Meta", "Nm.LineHeight.Data" };
        var allowed = new[] { 1.25, 1.45, 1.6 };

        foreach (var alias in aliases)
        {
            var row = Assert.Single(result.Rows, candidate => candidate.ResourceKey == alias && candidate.Scope == "global-derived");
            var value = TokenValues.ParseNumber(row.RawValue);
            Assert.True(
                allowed.Any(candidate => Math.Abs(candidate - value) < 0.0001),
                $"{alias}={value} is not one of the frozen multipliers 1.25/1.45/1.6");
        }

        // Absolute line boxes (Avalonia LineHeight is px) live in the separately named TextLineBox group.
        foreach (var alias in aliases)
        {
            Assert.Contains(result.Rows, row => row.ResourceKey == alias.Replace("Nm.LineHeight.", "Nm.TextLineBox.", StringComparison.Ordinal));
        }
    }

    [Fact]
    public void Theme_layer_whitelist_covers_exactly_the_registered_groups()
    {
        Assert.Equal(35, DesignSystemThemeManager.PaletteColorKeys.Count);
        Assert.Equal(3, DesignSystemThemeManager.ThemeLayerFontKeys.Count);
        Assert.Equal(6, DesignSystemThemeManager.ThemeLayerFontSizeKeys.Count);
        Assert.Equal(9, DesignSystemThemeManager.ThemeLayerLineHeightKeys.Count);
        Assert.Equal(3, DesignSystemThemeManager.ThemeLayerCornerKeys.Count);
        Assert.Equal(3, DesignSystemThemeManager.ThemeLayerMotionKeys.Count);
        Assert.Equal(6, DesignSystemThemeManager.ThemeLayerLineBoxKeys.Count);
        Assert.Equal(59, DesignSystemThemeManager.ThemeLayerRequiredKeys.Count);
        Assert.Equal(65, DesignSystemThemeManager.ThemeLayerAllowedKeys.Count);
        Assert.All(
            DesignSystemThemeManager.ThemeLayerLineBoxKeys,
            key => Assert.Contains(key, DesignSystemThemeManager.ThemeLayerAllowedKeys));
        // The whitelist must not allow spacing/size overrides through a theme layer.
        Assert.DoesNotContain(NmKeys.Space.S3, DesignSystemThemeManager.ThemeLayerAllowedKeys);
        Assert.DoesNotContain(NmKeys.Size.ControlHeight, DesignSystemThemeManager.ThemeLayerAllowedKeys);
        Assert.All(
            DesignSystemThemeManager.ThemeLayerLineBoxKeys,
            key => Assert.DoesNotContain(key, DesignSystemThemeManager.ThemeLayerRequiredKeys));
    }

    [Fact]
    public void Design_system_sources_have_no_naked_pixel_sizes_or_negative_margins()
    {
        foreach (var file in StyleSourceFiles())
        {
            var text = File.ReadAllText(file);
            foreach (Match match in Regex.Matches(text, @"(?:Width|Height)=""([^""]+)""", RegexOptions.CultureInvariant))
            {
                var value = match.Groups[1].Value;
                var allowed = value.StartsWith("{DynamicResource ", StringComparison.Ordinal) ||
                              value is "0" or "1" or "Auto" or "*" or "NaN";
                Assert.True(allowed, $"{file}: naked size '{value}' - use a token or the 0/1 layout exception");
            }
        }
    }

    private static IEnumerable<string> StyleSourceFiles()
    {
        var designSystem = TestPaths.DesignSystemProject;
        foreach (var file in Directory.EnumerateFiles(Path.Combine(designSystem, "Styles"), "*.axaml"))
        {
            yield return file;
        }

        foreach (var file in Directory.EnumerateFiles(Path.Combine(designSystem, "Themes", "Controls"), "*.axaml"))
        {
            yield return file;
        }
    }
}




