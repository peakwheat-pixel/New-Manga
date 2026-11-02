using Avalonia;
using Avalonia.Controls;
using NewManga.DesignSystem;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// I2c DS 上收：Studio geometry/typography values resolve from DesignSystem resource keys so the area
/// stops carrying its own literals. Fallbacks exist only for design-time (no Application resources).
/// </summary>
public static class StudioMetrics
{
    public static double BreakpointFull => Resource(NmKeys.Size.Breakpoint.Full, 1600);
    public static double BreakpointCompact => Resource(NmKeys.Size.Breakpoint.Compact, 1280);
    public static double BreakpointNarrow => Resource(NmKeys.Size.Breakpoint.Narrow, 1024);
    public static double FontXs => Resource(NmKeys.FontSize.Xs, 11);
    public static double FontSm => Resource(NmKeys.FontSize.Sm, 12);

    private static double Resource(string key, double fallback)
    {
        if (Application.Current is { } app && app.TryFindResource(key, out var value))
        {
            return value switch
            {
                double d => d,
                int i => i,
                string s when double.TryParse(s, out var parsed) => parsed,
                _ => fallback,
            };
        }

        return fallback;
    }
}
