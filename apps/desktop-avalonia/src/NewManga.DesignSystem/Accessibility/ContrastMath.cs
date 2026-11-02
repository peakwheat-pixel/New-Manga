using Avalonia.Media;

namespace NewManga.DesignSystem.Accessibility;

/// <summary>
/// WCAG 2.1 relative luminance and contrast ratio helpers. The design system validates every status,
/// text and focus-ring token against <c>DESIGN_SYSTEM §2.3</c> with these formulas, independently of
/// any rendering backend, so contrast regressions fail in unit tests rather than in review.
/// </summary>
public static class ContrastMath
{
    /// <summary>WCAG 2.1 relative luminance for an sRGB color (alpha is ignored: tokens are composited first).</summary>
    public static double RelativeLuminance(Color color) =>
        0.2126 * Linearize(color.R) + 0.7152 * Linearize(color.G) + 0.0722 * Linearize(color.B);

    /// <summary>
    /// WCAG 2.1 contrast ratio in [1, 21]. <paramref name="over"/> is the effective backdrop: if the
    /// foreground carries alpha it is composited over the backdrop before measuring.
    /// </summary>
    public static double ContrastRatio(Color foreground, Color over)
    {
        var composited = Composite(foreground, over);
        var first = RelativeLuminance(composited);
        var second = RelativeLuminance(over);
        var lighter = Math.Max(first, second);
        var darker = Math.Min(first, second);
        return (lighter + 0.05) / (darker + 0.05);
    }

    /// <summary>Source-over alpha compositing of <paramref name="foreground"/> onto an opaque backdrop.</summary>
    public static Color Composite(Color foreground, Color background)
    {
        if (foreground.A == 255)
        {
            return foreground;
        }

        var alpha = foreground.A / 255d;
        static byte Blend(byte top, byte bottom, double a) =>
            (byte)Math.Clamp((int)Math.Round(top * a + bottom * (1 - a), MidpointRounding.AwayFromZero), 0, 255);

        return Color.FromArgb(
            255,
            Blend(foreground.R, background.R, alpha),
            Blend(foreground.G, background.G, alpha),
            Blend(foreground.B, background.B, alpha));
    }

    private static double Linearize(byte channel)
    {
        var value = channel / 255d;
        return value <= 0.04045 ? value / 12.92 : Math.Pow((value + 0.055) / 1.055, 2.4);
    }
}
