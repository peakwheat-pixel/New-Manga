using Avalonia.Headless.XUnit;
using Avalonia.Media;
using NewManga.DesignSystem.Accessibility;
using NewManga.DesignSystem.Tokens;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC8 conformance: the published palettes are measured with WCAG 2.1 contrast math against the
/// DESIGN_SYSTEM §2.3 floors. The standard palette is the frozen baseline; where the frozen tokens fall
/// below a floor the gap is pinned here as a characterization (and listed in
/// verification/V11R-D-1/DEVIATIONS.md) instead of silently weakening the gate. High contrast is the
/// design system's derived palette and must meet every floor.
/// </summary>
public sealed class ContrastTokenTests
{
    private static readonly IReadOnlyDictionary<string, Color> FrozenColors = LoadFrozenColors();

    public static IEnumerable<object[]> ThemeScopes => new[]
    {
        new object[] { "color.dark.", "dark" },
        new object[] { "color.light.", "light" },
    };

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
    public void Focus_ring_accent_meets_the_non_text_floor(string scope, string label)
    {
        var panel = Color(scope, "bg.panel");
        var accent = Color(scope, "accent.base");
        var ratio = ContrastMath.ContrastRatio(accent, panel);
        Assert.True(ratio >= 3.0, $"{label}: focus-ring accent {accent} on panel is {ratio:F2}:1 (need >= 3:1)");
    }

    [Fact]
    public void Standard_palette_status_gap_is_pinned_to_the_frozen_baseline()
    {
        // Frozen tokens.json values (not a design-system choice): the dark palette's queued/skipped
        // hues and the marginal failed hue are below the §2.3 floor for status text/symbols. Changing
        // this expectation requires an amendment to the frozen baseline, not a local fix.
        var darkFailures = BelowFloor("color.dark.", floor: 4.5);
        var lightFailures = BelowFloor("color.light.", floor: 4.5);

        Assert.Equal(new[] { "Status.Failed", "Status.Queued", "Status.Skipped" }, darkFailures);
        Assert.Equal(new[] { "Status.Skipped" }, lightFailures);
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
                Assert.True(ContrastMath.ContrastRatio(HighContrast("Text.Primary"), background) >= 7.0,
                    $"{label} HC: text.primary >= 7:1");
                Assert.True(ContrastMath.ContrastRatio(HighContrast("Text.Secondary"), background) >= 4.5,
                    $"{label} HC: text.secondary >= 4.5:1");
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

    private static IReadOnlyList<string> BelowFloor(string scope, double floor)
    {
        var panel = Color(scope, "bg.panel");
        return new[] { "Queued", "Running", "Done", "Failed", "Blocked", "Stale", "Skipped" }
            .Where(status => ContrastMath.ContrastRatio(Color(scope, "status." + status.ToLowerInvariant()), panel) < floor)
            .Select(status => "Status." + status)
            .OrderBy(static status => status, StringComparer.Ordinal)
            .ToArray();
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
