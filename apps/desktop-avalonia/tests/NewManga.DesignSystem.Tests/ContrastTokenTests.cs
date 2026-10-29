using Avalonia.Headless.XUnit;
using Avalonia.Media;
using NewManga.DesignSystem.Accessibility;
using NewManga.DesignSystem.Theming;
using NewManga.DesignSystem.Tokens;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC8 conformance: the published palettes are measured with WCAG 2.1 contrast math against the
/// DESIGN_SYSTEM §2.3 floors. The frozen standard palette was remediated for the failing status/accent
/// tokens under Lead decision R-09 (see doc/design/redesign-v1/40-fusion/DECISION_LOG.md §5), so the
/// standard palette is now a hard compliance assertion instead of a characterization. High contrast is
/// the stronger, derived mode and must meet every floor as well.
/// </summary>
public sealed class ContrastTokenTests
{
    private static readonly IReadOnlyDictionary<string, Color> FrozenColors = LoadFrozenColors();
    private static readonly string[] StatusNames = ["Queued", "Running", "Done", "Failed", "Blocked", "Stale", "Skipped"];

    [Theory]
    [InlineData("color.dark.", "dark")]
    [InlineData("color.light.", "light")]
    public void Primary_and_secondary_text_meet_the_design_system_floors(string scope, string label)
    {
        var panel = Color(scope, "bg.panel");
        var canvas = Color(scope, "bg.canvas");

        foreach (var background in new[] { panel, canvas })
        {
            Assert.True(
                ContrastMath.ContrastRatio(Color(scope, "text.primary"), background) >= 7.0,
                $"{label}: text.primary must be >= 7:1 against the panel/canvas ladder");
            Assert.True(
                ContrastMath.ContrastRatio(Color(scope, "text.secondary"), background) >= 4.5,
                $"{label}: text.secondary must be >= 4.5:1 against the panel/canvas ladder");
        }
    }

    [Theory]
    [InlineData("color.dark.", "dark")]
    [InlineData("color.light.", "light")]
    public void Status_text_meets_the_design_system_floor(string scope, string label)
    {
        var panel = Color(scope, "bg.panel");
        foreach (var status in StatusNames)
        {
            var ratio = ContrastMath.ContrastRatio(Color(scope, "status." + status.ToLowerInvariant()), panel);
            Assert.True(ratio >= 4.5, $"{label}: status.{status} is {ratio:F2}:1 against bg.panel (need >= 4.5:1)");
        }
    }

    [Theory]
    [InlineData("color.dark.", "dark")]
    [InlineData("color.light.", "light")]
    public void Accent_fill_supports_its_on_color_and_the_focus_ring_floor(string scope, string label)
    {
        var accent = Color(scope, "accent.base");
        var on = Color(scope, "accent.on");
        var panel = Color(scope, "bg.panel");

        Assert.True(
            ContrastMath.ContrastRatio(on, accent) >= 4.5,
            $"{label}: accent.on on accent.base is {ContrastMath.ContrastRatio(on, accent):F2}:1 (need >= 4.5:1)");
        Assert.True(
            ContrastMath.ContrastRatio(accent, panel) >= 3.0,
            $"{label}: focus-ring accent on bg.panel is {ContrastMath.ContrastRatio(accent, panel):F2}:1 (need >= 3:1)");
    }

    [Theory]
    [InlineData("color.dark.", "dark")]
    [InlineData("color.light.", "light")]
    public void Focus_ring_accent_meets_the_non_text_floor(string scope, string label)
    {
        var panel = Color(scope, "bg.panel");
        var accent = Color(scope, "accent.base");
        var ratio = ContrastMath.ContrastRatio(accent, panel);
        Assert.True(ratio >= 3.0, $"{label}: focus-ring accent {accent} on panel is {ratio:F2}:1 (need >= 3:1)");
    }

    [Fact]
    public void Light_accent_interaction_ladder_stays_luminance_monotonic()
    {
        // R-09: the light accent was darkened; base > hover > active must stay strictly monotonic so the
        // interaction states keep their visual order (lighter = base, darker = pressed).
        var baseLuminance = ContrastMath.RelativeLuminance(Color("color.light.", "accent.base"));
        var hoverLuminance = ContrastMath.RelativeLuminance(Color("color.light.", "accent.hover"));
        var activeLuminance = ContrastMath.RelativeLuminance(Color("color.light.", "accent.active"));

        Assert.True(baseLuminance > hoverLuminance, "light accent.base must be lighter than accent.hover");
        Assert.True(hoverLuminance > activeLuminance, "light accent.hover must be lighter than accent.active");
    }

    [Fact]
    public void Dark_accent_interaction_ladder_stays_luminance_monotonic()
    {
        // Dark theme's hover is the brighter state; the ladder still has a single direction.
        var baseLuminance = ContrastMath.RelativeLuminance(Color("color.dark.", "accent.base"));
        var hoverLuminance = ContrastMath.RelativeLuminance(Color("color.dark.", "accent.hover"));
        var activeLuminance = ContrastMath.RelativeLuminance(Color("color.dark.", "accent.active"));

        Assert.True(hoverLuminance > baseLuminance, "dark accent.hover must be lighter than accent.base");
        Assert.True(baseLuminance > activeLuminance, "dark accent.base must be lighter than accent.active");
    }

    [AvaloniaFact]
    public void High_contrast_palette_meets_every_floor_in_both_themes()
    {
        var highContrast = (Avalonia.Controls.ResourceDictionary)Avalonia.Markup.Xaml.AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Themes/Tokens.HighContrast.axaml"));

        foreach (var (variant, label) in new[] { (Avalonia.Styling.ThemeVariant.Dark, "dark"), (Avalonia.Styling.ThemeVariant.Light, "light") })
        {
            Color HighContrast(string key) =>
                Assert.IsType<SolidColorBrush>(highContrast.TryGetResource("Nm.Color." + key, variant, out var value) ? value : null).Color;

            var panel = HighContrast("Bg.Panel");
            var canvas = HighContrast("Bg.Canvas");

            foreach (var background in new[] { panel, canvas })
            {
                // R-14: in high contrast every normal text tier is >= 7:1.
                foreach (var text in new[] { "Text.Primary", "Text.Secondary", "Text.Tertiary" })
                {
                    Assert.True(ContrastMath.ContrastRatio(HighContrast(text), background) >= 7.0,
                        $"{label} HC: {text} >= 7:1");
                }

                foreach (var status in new[] { "Queued", "Running", "Done", "Failed", "Blocked", "Stale", "Skipped" })
                {
                    Assert.True(ContrastMath.ContrastRatio(HighContrast("Status." + status), background) >= 4.5,
                        $"{label} HC: status.{status} >= 4.5:1 against {background}");
                }

                Assert.True(ContrastMath.ContrastRatio(HighContrast("Accent.Base"), background) >= 4.5,
                    $"{label} HC: accent.base >= 4.5:1");
            }
        }
    }

    private static Color Color(string scope, string path) => FrozenColors[scope + path];

    private static IReadOnlyDictionary<string, Color> LoadFrozenColors()
    {
        var text = File.ReadAllText(TestPaths.TokensFixture);
        var entries = TokenDocument.Parse(text);
        return entries
            .Where(static entry => entry.Type == "color")
            .ToDictionary(
                static entry => entry.Path,
                static entry => TokenValues.ParseColor(entry.Value),
                StringComparer.Ordinal);
    }
}

