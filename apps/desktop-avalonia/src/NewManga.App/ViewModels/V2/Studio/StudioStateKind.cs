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
    /// <summary>State symbols frozen by the Avalonia contract §2.3.</summary>
    public static string Glyph(StudioStateKind state) => state switch
    {
        StudioStateKind.Queued => "·",
        StudioStateKind.Running => "◐",
        StudioStateKind.Done => "●",
        StudioStateKind.Failed => "✗",
        StudioStateKind.Blocked => "▲",
        StudioStateKind.Stale => "▨",
        StudioStateKind.Skipped => "–",
        StudioStateKind.NotStarted => "○",
        _ => "○",
    };

    /// <summary>Chinese text label; a state must never be conveyed by colour alone (§2.2).</summary>
    public static string Label(StudioStateKind state) => state switch
    {
        StudioStateKind.Queued => "排队",
        StudioStateKind.Running => "进行中",
        StudioStateKind.Done => "完成",
        StudioStateKind.Failed => "失败",
        StudioStateKind.Blocked => "阻塞",
        StudioStateKind.Stale => "过期",
        StudioStateKind.Skipped => "跳过",
        StudioStateKind.NotStarted => "未开始",
        _ => "未开始",
    };

    /// <summary>
    /// Style class applied by the Studio stylesheet. Colour comes from
    /// <c>{DynamicResource Nm.Color.Status.*}</c>; code never assigns a raw brush.
    /// </summary>
    public static string StyleClass(StudioStateKind state) => state switch
    {
        StudioStateKind.Queued => "studio-state-queued",
        StudioStateKind.Running => "studio-state-running",
        StudioStateKind.Done => "studio-state-done",
        StudioStateKind.Failed => "studio-state-failed",
        StudioStateKind.Blocked => "studio-state-blocked",
        StudioStateKind.Stale => "studio-state-stale",
        StudioStateKind.Skipped => "studio-state-skipped",
        StudioStateKind.NotStarted => "studio-state-notstarted",
        _ => "studio-state-notstarted",
    };

    /// <summary>The token key backing <see cref="StyleClass"/> (used by tests + evidence).</summary>
    public static string ColorTokenKey(StudioStateKind state) => state switch
    {
        StudioStateKind.Queued => "Nm.Color.Status.Queued",
        StudioStateKind.Running => "Nm.Color.Status.Running",
        StudioStateKind.Done => "Nm.Color.Status.Done",
        StudioStateKind.Failed => "Nm.Color.Status.Failed",
        StudioStateKind.Blocked => "Nm.Color.Status.Blocked",
        StudioStateKind.Stale => "Nm.Color.Status.Stale",
        StudioStateKind.Skipped => "Nm.Color.Status.Skipped",
        StudioStateKind.NotStarted => "Nm.Color.Text.Disabled",
        _ => "Nm.Color.Text.Disabled",
    };

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
