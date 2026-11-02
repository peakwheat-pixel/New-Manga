using NewManga.DesignSystem;
using NewManga.DesignSystem.Controls;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// V11R-B-3: the one status vocabulary of the product (DESIGN_SYSTEM §2.2 / contract §2.3).
/// Seven pipeline states plus <see cref="NotStarted"/>; <c>locked</c> is a separate overlay flag
/// (<see cref="StudioRegionItem.IsLocked"/>), never a replacement state.
/// </summary>
public enum StudioStateKind
{
    NotStarted,
    Queued,
    Running,
    Done,
    Failed,
    Blocked,
    Stale,
    Skipped,
}

/// <summary>
/// Single source for the state glyph / label / style-class / token key mapping. No page may invent
/// its own symbol or colour: everything resolves through here (DESIGN_SYSTEM §2.2, §9 rule 4).
/// </summary>
public static class StudioStates
{
    /// <summary>Placeholder for "no projection data" — deliberately distinct from Skipped (–).</summary>
    public const string NoDataGlyph = "–";

    /// <summary>Maps the Studio vocabulary to the DS status vocabulary (single symbol source).</summary>
    public static StatusKind ToStatusKind(StudioStateKind state) => state switch
    {
        StudioStateKind.Queued => StatusKind.Queued,
        StudioStateKind.Running => StatusKind.Running,
        StudioStateKind.Done => StatusKind.Done,
        StudioStateKind.Failed => StatusKind.Failed,
        StudioStateKind.Blocked => StatusKind.Blocked,
        StudioStateKind.Stale => StatusKind.Stale,
        StudioStateKind.Skipped => StatusKind.Skipped,
        _ => StatusKind.NotStarted,
    };

    /// <summary>State symbols come from the DS <see cref="NmStatusSymbols"/> source (no local table).</summary>
    public static string Glyph(StudioStateKind state) => StatusCatalog.Symbol(ToStatusKind(state));

    /// <summary>Chinese label from the DS catalog; a state is never conveyed by colour alone (§2.2).</summary>
    public static string Label(StudioStateKind state) => StatusCatalog.Label(ToStatusKind(state));

    /// <summary>
    /// Style class applied by the Studio stylesheet. Colour comes from
    /// <c>{DynamicResource Nm.Color.Status.*}</c>; code never assigns a raw brush.
    /// </summary>
    public static string StyleClass(StudioStateKind state) => "studio-state-" + StatusCatalog.ClassName(ToStatusKind(state));

    /// <summary>The token key backing <see cref="StyleClass"/> (used by tests + evidence).</summary>
    public static string ColorTokenKey(StudioStateKind state) => StatusCatalog.ColorKey(ToStatusKind(state));

    /// <summary>
    /// Region review state (Core <c>list_region_revisions.review_state</c>) → product state. Only
    /// confirmed/needs_review/unreviewed exist; anything else stays unknown (null, never guessed).
    /// </summary>
    public static StudioStateKind? FromReviewState(string? reviewState) => reviewState?.Trim().ToLowerInvariant() switch
    {
        "confirmed" => StudioStateKind.Done,
        "needs_review" => StudioStateKind.Queued,
        "unreviewed" => StudioStateKind.NotStarted,
        _ => null,
    };

    /// <summary>
    /// <c>GetTaskProjection</c> page/step status → product state. The Core vocabulary is
    /// waiting / processing / completed / failed / skipped / blocked (projection.py); anything else
    /// returns null so the matrix can render "no projection row" instead of inventing a state.
    /// </summary>
    public static StudioStateKind? FromProjectionStatus(string? status) => status?.Trim().ToLowerInvariant() switch
    {
        "waiting" => StudioStateKind.Queued,
        "pending" => StudioStateKind.Queued,
        "processing" => StudioStateKind.Running,
        "running" => StudioStateKind.Running,
        "completed" => StudioStateKind.Done,
        "done" => StudioStateKind.Done,
        "failed" => StudioStateKind.Failed,
        "blocked" => StudioStateKind.Blocked,
        "stale" => StudioStateKind.Stale,
        "skipped" => StudioStateKind.Skipped,
        "not_started" => StudioStateKind.NotStarted,
        _ => null,
    };

    /// <summary>Legend rows in the canonical order (Batch matrix legend / Page track strip help).</summary>
    public static IReadOnlyList<StudioStateKind> LegendOrder { get; } = new[]
    {
        StudioStateKind.Queued,
        StudioStateKind.Running,
        StudioStateKind.Done,
        StudioStateKind.Failed,
        StudioStateKind.Blocked,
        StudioStateKind.Stale,
        StudioStateKind.Skipped,
        StudioStateKind.NotStarted,
    };

    /// <summary>Full legend text ("● 完成") used by tooltips and the always-on legend strip.</summary>
    public static string LegendText(StudioStateKind state) => $"{Glyph(state)} {Label(state)}";
}
