using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Accessibility;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;
using SkiaSharp;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// D-1 I2 P1-2 regression: badge contrast must be measured against the ACTUAL rendered badge surface,
/// not against the opaque panel behind it. The badge background is translucent statusMuted color, so the
/// effective background is the composite over the parent surface; the test samples that pixel from a real
/// headless render and compares it with the resolved status glyph brush (all statuses, both themes and
/// high contrast).
/// </summary>
public sealed class BadgeCompositeContrastTests
{
    private static readonly (AppearanceMode Appearance, ContrastMode Contrast)[] Modes =
    [
        (AppearanceMode.Dark, ContrastMode.Standard),
        (AppearanceMode.Light, ContrastMode.Standard),
        (AppearanceMode.Dark, ContrastMode.High),
        (AppearanceMode.Light, ContrastMode.High),
    ];

    [AvaloniaFact]
    public void Status_badge_glyph_contrast_is_measured_against_the_rendered_composited_background()
    {
        foreach (var (appearance, contrast) in Modes)
        {
            using var manager = ThemeTestHarness.CreateInitialized(appearance);
            if (contrast == ContrastMode.High)
            {
                Assert.True(manager.SetContrast(ContrastMode.High), manager.LastError);
            }

            // D-1 I3: badges may be used on every allowed surface (panel / raised / overlay). The
            // composited badge background differs per surface, so all three are rendered and sampled.
            foreach (var surfaceKey in AllowedSurfaces)
            {
                var badges = new List<StatusBadge>();
                foreach (var kind in Enum.GetValues<StatusKind>())
                {
                    badges.Add(new StatusBadge { Status = kind });
                }

                var surfaceColor = ThemeTestHarness.ColorOf(Application.Current!, surfaceKey);
                var panel = new Border
                {
                    Background = new SolidColorBrush(surfaceColor),
                    Padding = new Thickness(16),
                    Child = new StackPanel { Spacing = 8, Children = { } },
                };
                foreach (var badge in badges)
                {
                    ((StackPanel)panel.Child!).Children.Add(badge);
                }

                var window = new Window { Width = 420, Height = 520, Content = panel };
                window.Show();
                Dispatcher.UIThread.RunJobs();
                Assert.True(window.CaptureRenderedFrame() is not null);

                using var bitmap = SKBitmap.Decode(SaveBytes(window));

                foreach (var badge in badges)
                {
                    var glyph = badge.GetVisualDescendants().OfType<StatusGlyph>().Single();
                    var label = badge.GetVisualDescendants().OfType<TextBlock>().Single(text => text.Classes.Contains("label"));
                    var glyphBrush = Assert.IsAssignableFrom<ISolidColorBrush>(glyph.Foreground);
                    var labelBrush = Assert.IsAssignableFrom<ISolidColorBrush>(label.Foreground);
                    var badgeBrush = Assert.IsAssignableFrom<ISolidColorBrush>(badge.Background);

                    var composite = Composite(badgeBrush.Color, surfaceColor);
                    var topLeft = badge.TranslatePoint(default, window);
                    Assert.NotNull(topLeft);
                    var sampleX = (int)Math.Round(topLeft!.Value.X) + 3;
                    var sampleY = (int)Math.Round(topLeft.Value.Y) + 3;
                    var pixel = bitmap.GetPixel(sampleX, sampleY);
                    var rendered = Color.FromArgb(255, pixel.Red, pixel.Green, pixel.Blue);

                    // The sampled pixel proves the render really shows the composite, not the raw surface;
                    // allow a tiny tolerance for sRGB rounding and border antialiasing.
                    Assert.True(
                        Math.Abs(rendered.R - composite.R) <= 4 &&
                        Math.Abs(rendered.G - composite.G) <= 4 &&
                        Math.Abs(rendered.B - composite.B) <= 4,
                        $"{appearance}/{contrast}/{surfaceKey} {badge.Status}: rendered background {rendered} != composite {composite}");

                    var glyphRatio = ContrastMath.ContrastRatio(glyphBrush.Color, rendered);
                    Assert.True(
                        glyphRatio >= 4.5,
                        $"{appearance}/{contrast}/{surfaceKey} {badge.Status}: glyph contrast {glyphRatio:F2}:1 vs rendered " +
                        $"badge background {rendered} (glyph {glyphBrush.Color}) must be >= 4.5:1");

                    var labelRatio = ContrastMath.ContrastRatio(labelBrush.Color, rendered);
                    Assert.True(
                        labelRatio >= 4.5,
                        $"{appearance}/{contrast}/{surfaceKey} {badge.Status}: label contrast {labelRatio:F2}:1 must be >= 4.5:1");
                }

                window.Close();
            }
        }
    }

    /// <summary>The surfaces a status badge is allowed to sit on (DESIGN_SYSTEM §2.3).</summary>
    private static readonly string[] AllowedSurfaces =
    [
        NmKeys.Color.Bg.Panel,
        NmKeys.Color.Bg.Raised,
        NmKeys.Color.Bg.Overlay,
    ];

    private static Color Composite(Color overlay, Color background)
    {
        var alpha = overlay.A / 255d;
        byte Channel(byte top, byte bottom) => (byte)Math.Round((top * alpha) + (bottom * (1 - alpha)));
        return Color.FromArgb(255, Channel(overlay.R, background.R), Channel(overlay.G, background.G), Channel(overlay.B, background.B));
    }

    private static byte[] SaveBytes(Window window)
    {
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException("frame capture failed");
        using var stream = new MemoryStream();
        frame.Save(stream);
        return stream.ToArray();
    }
}
