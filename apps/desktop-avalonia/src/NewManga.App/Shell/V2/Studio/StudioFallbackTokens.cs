using Avalonia;
using Avalonia.Media;

namespace NewManga.App.Shell.V2.Studio;

/// <summary>
/// V11R-B-3 BRIDGE (temporary, delete at V11R-INT-1): <c>NewManga.DesignSystem</c> owns the frozen
/// <c>Nm.*</c> resource keys (contract §2.2) but is still being built in its own task branch. Until it
/// merges, the Studio area injects the frozen dark token set from
/// <c>doc/design/redesign-v1/40-fusion/tokens.json</c> so every Studio style can keep using
/// <c>{DynamicResource Nm.*}</c> (no raw values anywhere) and still render.
///
/// Injection rules:
/// * only when the app resource dictionary does NOT already define <c>Nm.Color.Bg.Canvas</c> — a real
///   DesignSystem dictionary always wins, so this shim dies automatically at integration;
/// * values are the FROZEN dark theme of tokens.json (the direction is the A darkroom base);
/// * no layout decision lives here — only token values.
/// </summary>
public static class StudioFallbackTokens
{
    private static readonly object Sync = new();
    private static bool _injected;

    /// <summary>True when this build had to inject the fallback set (evidence + integration check).</summary>
    public static bool WasInjected
    {
        get
        {
            lock (Sync)
            {
                return _injected;
            }
        }
    }

    /// <summary>Idempotent. Safe to call from every Studio view constructor.</summary>
    public static void EnsureMerged()
    {
        var app = Application.Current;
        if (app is null)
        {
            return;
        }

        lock (Sync)
        {
            if (app.TryGetResource(Key("Color", "Bg", "Canvas"), null, out _))
            {
                return;
            }

            foreach (var (key, value) in Build())
            {
                app.Resources[key] = value;
            }

            _injected = true;
        }
    }

    /// <summary>The frozen dark token table (contract §2.2 keys, tokens.json values).</summary>
    internal static IEnumerable<KeyValuePair<string, object>> Build()
    {
        // ---------------------------------------------------------------- bg (5 levels + sunken)
        yield return ColorPair("Color.Bg.Canvas", "#0F1012");
        yield return ColorPair("Color.Bg.App", "#141518");
        yield return ColorPair("Color.Bg.Panel", "#1A1C1F");
        yield return ColorPair("Color.Bg.Raised", "#22252A");
        yield return ColorPair("Color.Bg.Overlay", "#2A2E34");
        yield return ColorPair("Color.Bg.Sunken", "#0B0C0E");

        // ---------------------------------------------------------------- lines
        yield return ColorPair("Color.Line.Subtle", "#0FFFFFFF"); // rgba(255,255,255,0.06)
        yield return ColorPair("Color.Line.Default", "#1AFFFFFF"); // rgba(255,255,255,0.10)
        yield return ColorPair("Color.Line.Strong", "#29FFFFFF"); // rgba(255,255,255,0.16)
        yield return ColorPair("Color.Line.Grid", "#0AFFFFFF"); // rgba(255,255,255,0.04)

        // ---------------------------------------------------------------- text
        yield return ColorPair("Color.Text.Primary", "#E9EAEC");
        yield return ColorPair("Color.Text.Secondary", "#A3A8AF");
        yield return ColorPair("Color.Text.Tertiary", "#71767D");
        yield return ColorPair("Color.Text.Disabled", "#4E5359");
        yield return ColorPair("Color.Text.Inverse", "#0F1012");

        // ---------------------------------------------------------------- accent (amber, focus only)
        yield return ColorPair("Color.Accent.Base", "#D9A04B");
        yield return ColorPair("Color.Accent.Hover", "#E8B264");
        yield return ColorPair("Color.Accent.Active", "#C08A34");
        yield return ColorPair("Color.Accent.Muted", "#24D9A04B"); // rgba(217,160,75,0.14)
        yield return ColorPair("Color.Accent.On", "#17181A");
        yield return ColorPair("Color.Accent.Ring", "#73D9A04B"); // rgba(217,160,75,0.45)

        // ---------------------------------------------------------------- status (7) + muted (7)
        yield return ColorPair("Color.Status.Queued", "#5C6169");
        yield return ColorPair("Color.Status.Running", "#5B93B8");
        yield return ColorPair("Color.Status.Done", "#6FA97D");
        yield return ColorPair("Color.Status.Failed", "#C9634F");
        yield return ColorPair("Color.Status.Blocked", "#C8903F");
        yield return ColorPair("Color.Status.Stale", "#9A8AB0");
        yield return ColorPair("Color.Status.Skipped", "#4A4F55");

        yield return ColorPair("Color.StatusMuted.Queued", "#2E5C6169");
        yield return ColorPair("Color.StatusMuted.Running", "#295B93B8");
        yield return ColorPair("Color.StatusMuted.Done", "#246FA97D");
        yield return ColorPair("Color.StatusMuted.Failed", "#29C9634F");
        yield return ColorPair("Color.StatusMuted.Blocked", "#29C8903F");
        yield return ColorPair("Color.StatusMuted.Stale", "#299A8AB0");
        yield return ColorPair("Color.StatusMuted.Skipped", "#244A4F55");

        // ---------------------------------------------------------------- fonts
        yield return new KeyValuePair<string, object>(
            Key("FontFamily", "Ui"),
            FontFamily.Parse("Segoe UI Variable Text, Microsoft YaHei UI, Noto Sans SC"));
        yield return new KeyValuePair<string, object>(
            Key("FontFamily", "Data"),
            FontFamily.Parse("Cascadia Mono, Consolas, Noto Sans SC"));
        yield return new KeyValuePair<string, object>(
            Key("FontFamily", "Display"),
            FontFamily.Parse("Georgia, Noto Serif SC"));

        yield return Pair("FontSize.Xs", 11d);
        yield return Pair("FontSize.Sm", 12d);
        yield return Pair("FontSize.Md", 13d);
        yield return Pair("FontSize.Lg", 14d);
        yield return Pair("FontSize.Xl", 18d);
        yield return Pair("FontSize.2Xl", 24d);

        yield return new KeyValuePair<string, object>(Key("FontWeight", "Regular"), FontWeight.Normal);
        yield return new KeyValuePair<string, object>(Key("FontWeight", "Medium"), FontWeight.Medium);
        yield return new KeyValuePair<string, object>(Key("FontWeight", "SemiBold"), FontWeight.SemiBold);

        yield return Pair("LineHeight.Tight", 1.25d);
        yield return Pair("LineHeight.Normal", 1.45d);
        yield return Pair("LineHeight.Loose", 1.6d);

        // ---------------------------------------------------------------- space scale
        yield return Pair("Space.0", 0d);
        yield return Pair("Space.1", 2d);
        yield return Pair("Space.2", 4d);
        yield return Pair("Space.3", 8d);
        yield return Pair("Space.4", 12d);
        yield return Pair("Space.5", 16d);
        yield return Pair("Space.6", 20d);
        yield return Pair("Space.7", 24d);
        yield return Pair("Space.8", 32d);

        // ---------------------------------------------------------------- radius (≤ 3px, hard rule)
        yield return new KeyValuePair<string, object>(Key("Corner", "None"), new CornerRadius(0));
        yield return new KeyValuePair<string, object>(Key("Corner", "Sm"), new CornerRadius(2));
        yield return new KeyValuePair<string, object>(Key("Corner", "Md"), new CornerRadius(3));

        // ---------------------------------------------------------------- sizes (contract §2.2)
        yield return Pair("Size.TopBand", 36d);
        yield return Pair("Size.StatusBandPage", 28d);
        yield return Pair("Size.StatusBandBatch", 24d);
        yield return Pair("Size.FilmStripCollapsed", 56d);
        yield return Pair("Size.FilmStripExpanded", 200d);
        yield return Pair("Size.InspectorCollapsed", 40d);
        yield return Pair("Size.InspectorExpanded", 320d);
        yield return Pair("Size.Drawer", 360d);
        yield return Pair("Size.RowPage", 28d);
        yield return Pair("Size.RowBatch", 22d);
        yield return Pair("Size.ControlHeight", 28d);
        yield return Pair("Size.ControlHeightSm", 24d);
        yield return Pair("Size.HudSlot", 22d);
        yield return Pair("Size.IconLg", 24d);
        yield return Pair("Size.CanvasPadding", 32d);
        yield return Pair("Size.FilmThumb", 44d);
        yield return Pair("Size.FilmThumbExpanded", 176d);

        // ---------------------------------------------------------------- padding
        yield return new KeyValuePair<string, object>(Key("Padding", "Panel"), new Thickness(12));
        yield return new KeyValuePair<string, object>(Key("Padding", "Card"), new Thickness(12));
        yield return new KeyValuePair<string, object>(Key("Padding", "Control"), new Thickness(8, 12));
        yield return new KeyValuePair<string, object>(Key("Padding", "ControlSm"), new Thickness(6, 8));
        yield return new KeyValuePair<string, object>(Key("Padding", "Cell"), new Thickness(8));
        yield return new KeyValuePair<string, object>(Key("Padding", "Section"), new Thickness(16));

        // ---------------------------------------------------------------- motion (feedback only)
        yield return new KeyValuePair<string, object>(Key("Motion", "Duration", "Fast"), TimeSpan.FromMilliseconds(90));
        yield return new KeyValuePair<string, object>(Key("Motion", "Duration", "Normal"), TimeSpan.FromMilliseconds(140));
        yield return Pair("Motion.Enabled", true);

        // ---------------------------------------------------------------- icons (1.25px stroke / 20 grid)
        yield return Pair("Icon.Size", 20d);
        yield return Pair("Icon.Stroke", 1.25d);
    }

    private static KeyValuePair<string, object> Pair(string suffix, object value) =>
        new(Key(suffix), value);

    /// <summary>Colour token: the value is always an <see cref="IBrush"/> (never a raw string).</summary>
    private static KeyValuePair<string, object> ColorPair(string suffix, string colorHex) =>
        new(Key(suffix), Brush(colorHex));

    private static string Key(string suffix) => "Nm." + suffix;

    private static string Key(params string[] segments) => "Nm." + string.Join('.', segments);

    private static KeyValuePair<string, object> Pair(string group, string name, object value) =>
        new(Key(group, name), value);

    private static KeyValuePair<string, object> Pair(string group, string name, string colorHex) =>
        new(Key(group, name), Brush(colorHex));

    private static IBrush Brush(string hex)
    {
        var color = Color.Parse(hex);
        return new SolidColorBrush(color);
    }
}
