using System.Text.RegularExpressions;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC3/AC8 hard-rule guard: the design-system sources are scanned for forbidden constructs so a
/// hand-typed colour, a StaticResource (which would not follow theme switches), a shadow, a gradient,
/// blur or a radius above the 3px rule cannot slip into a stylesheet unnoticed.
/// </summary>
public sealed class DesignRulesTests
{
    private static readonly string[] ForbiddenBrushProperties =
    [
        "Foreground",
        "Background",
        "BorderBrush",
        "Fill",
        "Stroke",
    ];

    [Fact]
    public void Styles_and_control_themes_never_hardcode_colors()
    {
        foreach (var file in StyleSourceFiles())
        {
            var text = File.ReadAllText(file);
            var color = Regex.Match(text, @"#[0-9A-Fa-f]{6,8}\b", RegexOptions.CultureInvariant);
            Assert.False(color.Success, $"{file}: hardcoded colour '{color.Value}' - use a DynamicResource token");

            Assert.DoesNotContain("StaticResource", text, StringComparison.Ordinal);
        }
    }

    [Fact]
    public void Styles_never_use_shadows_gradients_or_blur()
    {
        foreach (var file in StyleSourceFiles())
        {
            var text = File.ReadAllText(file);
            Assert.DoesNotContain("BoxShadow", text, StringComparison.Ordinal);
            Assert.DoesNotContain("LinearGradient", text, StringComparison.Ordinal);
            Assert.DoesNotContain("RadialGradient", text, StringComparison.Ordinal);
            Assert.DoesNotContain("BlurEffect", text, StringComparison.Ordinal);
            Assert.DoesNotContain("DropShadow", text, StringComparison.Ordinal);
        }
    }

    [Fact]
    public void Brush_properties_are_dynamic_resources()
    {
        foreach (var file in StyleSourceFiles())
        {
            var text = File.ReadAllText(file);
            foreach (var property in ForbiddenBrushProperties)
            {
                foreach (Match match in Regex.Matches(
                             text,
                             $"Property=\"{property}\"\\s+Value=\"([^\"]+)\"",
                             RegexOptions.CultureInvariant))
                {
                    var value = match.Groups[1].Value;
                    var allowed = value.StartsWith("{DynamicResource ", StringComparison.Ordinal) ||
                                  value.Equals("Transparent", StringComparison.Ordinal);
                    Assert.True(allowed, $"{file}: {property} uses non-token value '{value}'");
                }
            }
        }
    }

    [Fact]
    public void Corner_radius_tokens_never_exceed_the_three_pixel_rule()
    {
        var globalDictionary = File.ReadAllText(
            Path.Combine(TestPaths.DesignSystemProject, "Themes", "Tokens.Global.axaml"));
        foreach (Match match in Regex.Matches(
                     globalDictionary,
                     "x:Key=\"Nm\\.Corner\\.(None|Sm|Md)\">([0-9.]+)<",
                     RegexOptions.CultureInvariant))
        {
            Assert.True(
                double.Parse(match.Groups[2].Value, System.Globalization.CultureInfo.InvariantCulture) <= 3,
                $"corner token {match.Groups[1].Value} exceeds the 3px rule");
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
