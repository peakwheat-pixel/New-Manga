using Avalonia;
using NewManga.DesignSystem;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// The single place where the Theme Studio derives layout geometry (review C2-P2-1, mirroring
/// <c>Shell/V2/ShellLayout.cs</c> and the Studio metrics module): every number the design system
/// publishes is resolved from its <c>Nm.*</c> token at runtime, so the ViewModels and views carry no
/// literal design values.
///
/// <para>
/// Structural column counts (4 at the full breakpoint, 3 at compact, 2 below) are fixed by
/// THEME_STUDIO_SPEC §3.1 — they are counts, not geometry tokens — and the minimum card width is
/// derived from the frozen breakpoint arithmetic instead of a literal.
/// </para>
/// </summary>
public static class ThemeStudioMetrics
{
    /// <summary>Card grid columns at/above the full breakpoint (spec §3.1).</summary>
    public const int MaxColumns = 4;

    /// <summary>Card grid columns in the compact band (spec §3.1).</summary>
    public const int CompactColumns = 3;

    /// <summary>Card grid columns below the compact breakpoint (spec §3.1).</summary>
    public const int NarrowColumns = 2;

    /// <summary>Gap between cards (DS spacing token, 12).</summary>
    public static double CardGap => Size(NmKeys.Space.S4);

    /// <summary>Initial card width before the first layout pass (DS inspector width token, 320).</summary>
    public static double CardWidthDefault => Size(NmKeys.Size.InspectorExpanded);

    /// <summary>Full-width breakpoint (DS token, 1600).</summary>
    public static double BreakpointFull => Size(NmKeys.Size.Breakpoint.Full);

    /// <summary>Compact breakpoint (DS token, 1280).</summary>
    public static double BreakpointCompact => Size(NmKeys.Size.Breakpoint.Compact);

    /// <summary>
    /// Minimum readable card width: the content area left at the full breakpoint (window − tree rail −
    /// inspector rail − both content insets − the inter-card gaps) divided by the max column count.
    /// At the frozen token values this is (1600 − 200 − 320 − 48 − 36) / 4 = 249.
    /// </summary>
    public static double CardMinWidth
    {
        get
        {
            var full = BreakpointFull;
            if (full <= 0)
            {
                return 0;
            }

            var available = full
                - Size(NmKeys.Size.TreeWidth)
                - Size(NmKeys.Size.InspectorExpanded)
                - (Size(NmKeys.Space.S7) * 2)
                - (CardGap * (MaxColumns - 1));
            return available / MaxColumns;
        }
    }

    /// <summary>
    /// Frozen breakpoint rule (THEME_STUDIO_SPEC §3.1): ≥ full → 4 columns, ≥ compact → 3, otherwise 2.
    /// Falls back to the widest layout while no Application/resource scope exists (design-time, unit VMs).
    /// </summary>
    public static int ColumnsForWidth(double width)
    {
        var full = BreakpointFull;
        var compact = BreakpointCompact;
        if (full <= 0 || compact <= 0)
        {
            return MaxColumns;
        }

        return width >= full ? MaxColumns : width >= compact ? CompactColumns : NarrowColumns;
    }

    /// <summary>Reads a numeric <c>Nm.*</c> token; returns 0 before an Application/token scope exists.</summary>
    public static double Size(string key) =>
        Application.Current is { } application &&
        application.TryGetResource(key, null, out var value) &&
        value is double number
            ? number
            : 0;
}
