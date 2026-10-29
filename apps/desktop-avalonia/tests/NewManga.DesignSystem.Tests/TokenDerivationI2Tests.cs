using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Markup.Xaml;
using Avalonia;
using NewManga.DesignSystem.Tokens;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// D-1 I2 P2-④/⑦: generator-side derivations are asserted on the committed dictionaries.
/// </summary>
public sealed class TokenDerivationI2Tests
{
    [AvaloniaFact]
    public void Density_overlays_are_componentwise_strictly_monotonic()
    {
        var global = Load("Tokens.Global.axaml");
        var compact = Load("Density.Compact.axaml");
        var spacious = Load("Density.Spacious.axaml");

        foreach (var density in TokenMap.Density)
        {
            if (density.Kind == TokenValueKind.Thickness)
            {
                var reference = Resolve<Thickness>(global, density.ResourceKey);
                var compactValue = Resolve<Thickness>(compact, density.ResourceKey);
                var spaciousValue = Resolve<Thickness>(spacious, density.ResourceKey);
                AssertStrictlySmaller(compactValue, reference, density.ResourceKey);
                AssertStrictlySmaller(reference, spaciousValue, density.ResourceKey);
            }
            else
            {
                var reference = Resolve<double>(global, density.ResourceKey);
                var compactValue = Resolve<double>(compact, density.ResourceKey);
                var spaciousValue = Resolve<double>(spacious, density.ResourceKey);
                Assert.True(
                    compactValue < reference && reference < spaciousValue,
                    $"{density.ResourceKey}: compact {compactValue} < comfortable {reference} < spacious {spaciousValue}");
            }
        }
    }

    [AvaloniaFact]
    public void Reduced_motion_zeroes_every_published_duration_key()
    {
        var reduced = Load("Motion.Reduced.axaml");
        Assert.Equal(TimeSpan.Zero, Resolve<TimeSpan>(reduced, "Nm.Motion.Duration.Instant"));
        Assert.Equal(TimeSpan.Zero, Resolve<TimeSpan>(reduced, "Nm.Motion.Duration.Fast"));
        Assert.Equal(TimeSpan.Zero, Resolve<TimeSpan>(reduced, "Nm.Motion.Duration.Normal"));
        Assert.Equal(TimeSpan.Zero, Resolve<TimeSpan>(reduced, "Nm.Motion.Duration.Slow"));
        Assert.False(Resolve<bool>(reduced, "Nm.Motion.Enabled"));
    }

    private static void AssertStrictlySmaller(Thickness smaller, Thickness larger, string key)
    {
        Assert.True(
            smaller.Left < larger.Left &&
            smaller.Top < larger.Top &&
            smaller.Right < larger.Right &&
            smaller.Bottom < larger.Bottom,
            $"{key}: {smaller} must be strictly smaller than {larger} component-wise");
    }

    private static ResourceDictionary Load(string file) =>
        (ResourceDictionary)AvaloniaXamlLoader.Load(
            new Uri($"avares://NewManga.DesignSystem/Themes/{file}"));

    private static T Resolve<T>(ResourceDictionary dictionary, string key)
    {
        Assert.True(dictionary.TryGetResource(key, Avalonia.Styling.ThemeVariant.Default, out var value), $"missing {key}");
        return Assert.IsType<T>(value);
    }
}

