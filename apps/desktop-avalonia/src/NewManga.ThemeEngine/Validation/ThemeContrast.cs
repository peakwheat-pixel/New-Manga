using Avalonia.Media;
using NewManga.DesignSystem.Accessibility;
using NewManga.DesignSystem.Tokens;

namespace NewManga.ThemeEngine;

/// <summary>
/// WCAG 2.1 contrast helpers over theme token values (DESIGN_SYSTEM §2.3). Theme Studio uses this to
/// show live ratios in the editor; the validator uses it to enforce the floors on import.
/// </summary>
public static class ThemeContrast
{
    /// <summary>Parses a theme color token value (hex, <c>rgb()</c>, <c>rgba()</c>).</summary>
    public static bool TryParse(string? raw, out Color color)
    {
        color = default;
        if (string.IsNullOrWhiteSpace(raw))
        {
            return false;
        }

        try
        {
            color = TokenValues.ParseColor(raw);
            return true;
        }
        catch (FormatException)
        {
            return false;
        }
    }

    /// <summary>
    /// WCAG 2.1 contrast ratio in [1, 21] between two theme color token values. Alpha foregrounds are
    /// composited over the background first (same math as the design system).
    /// </summary>
    public static double Ratio(string foreground, string background)
    {
        if (!TryParse(foreground, out var fg))
        {
            throw new FormatException($"unsupported foreground color value '{foreground}'");
        }

        if (!TryParse(background, out var bg))
        {
            throw new FormatException($"unsupported background color value '{background}'");
        }

        return ContrastMath.ContrastRatio(fg, bg);
    }

    /// <summary>True when <paramref name="foreground"/> reaches <paramref name="floor"/> against <paramref name="background"/>.</summary>
    public static bool Meets(string foreground, string background, double floor) =>
        Ratio(foreground, background) >= floor;
}
