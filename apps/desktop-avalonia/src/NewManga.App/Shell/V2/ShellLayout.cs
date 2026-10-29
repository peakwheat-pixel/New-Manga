using Avalonia;
using NewManga.DesignSystem;

namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-INT-0 / repair R-18: the single place where the shell derives layout geometry. Every number
/// that the design system publishes is resolved from its <c>Nm.*</c> token at runtime; only the three
/// frozen responsive breakpoints and two documented aspect/proportion ratios live here as constants
/// (the DS <c>Nm.Size.Breakpoint.*</c> tokens are a design-platform follow-up — see DEVIATIONS).
///
/// Conformance (AC4): C# outside this file must not carry raw design values.
/// </summary>
public static class ShellLayout
{
    // ── R-18 responsive bands (frozen by Lead ruling; DS Breakpoint tokens are a follow-up) ──────
    public const double BreakpointFull = 1600;     // >= 1600: full layout (4-column book grid)
    public const double BreakpointCompact = 1280;  // 1280..1599: compact (3 columns, narrower detail)
    public const double BreakpointNarrow = 1024;   // < 1280: narrow (detail becomes an overlay)

    // ── Documented proportions (not colour/size tokens; derived geometry only) ──────────────────
    /// <summary>Book-cover card aspect ratio from SCREEN_SPECS §2 (cover cards are 1 : 1.3).</summary>
    public const double CoverAspectRatio = 1.3;

    /// <summary>Compact sort combo width as a fraction of the DS tree/search width.</summary>
    public const double SortWidthRatio = 0.6;

    public static bool IsFull(double width) => width >= BreakpointFull;

    public static bool IsCompact(double width) => width is >= BreakpointCompact and < BreakpointFull;

    public static bool IsNarrow(double width) => width < BreakpointCompact;

    /// <summary>Top band height (DS token; screen spec §1).</summary>
    public static double TopBandHeight => Size(NmKeys.Size.TopBand);

    /// <summary>Status band height in its batch/run variant (DS token).</summary>
    public static double StatusBandHeight => Size(NmKeys.Size.StatusBandBatch);

    /// <summary>Side detail/drawer width (DS token).</summary>
    public static double DetailPanelWidth => Size(NmKeys.Size.Drawer);

    /// <summary>Narrower inspector width used in the compact band (DS token).</summary>
    public static double CompactDetailPanelWidth => Size(NmKeys.Size.InspectorExpanded);

    /// <summary>Search field width (DS tree-width token).</summary>
    public static double SearchBoxWidth => Size(NmKeys.Size.TreeWidth);

    /// <summary>Sort combo width derived from the DS search width.</summary>
    public static double SortBoxWidth => SearchBoxWidth * SortWidthRatio;

    /// <summary>Command palette width: drawer + tree width (560 at the frozen token values).</summary>
    public static double PaletteWidth => DetailPanelWidth + SearchBoxWidth;

    /// <summary>Confirmation modal width: drawer + compact sort width (480 at the frozen token values).</summary>
    public static double ConfirmWidth => DetailPanelWidth + SortBoxWidth;

    /// <summary>Gap between book cards / grid cells (DS spacing token, 12).</summary>
    public static double GridGap => Size(NmKeys.Space.S4);

    /// <summary>Library content inset on both sides (DS spacing token, 24).</summary>
    public static double PanelInset => Size(NmKeys.Space.S7);

    /// <summary>Reads a numeric <c>Nm.*</c> token; returns 0 before an Application/token scope exists.</summary>
    public static double Size(string key) =>
        Application.Current is { } application &&
        application.TryGetResource(key, null, out var value) &&
        value is double number
            ? number
            : 0;
}
