namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-B-1: the frozen seven-state status language (+ not_started / locked) from
/// doc/design/redesign-v1/40-fusion/DESIGN_SYSTEM.md §2.2 and the Avalonia contract §2.3.
/// A state ALWAYS carries three channels: colour token + symbol + text label; the symbol table here
/// is the single local source until NewManga.DesignSystem.Controls.StatusGlyph is merged (V11R-D-1).
/// </summary>
public enum NmStatus
{
    NotStarted,
    Queued,
    Running,
    Done,
    Failed,
    Blocked,
    Stale,
    Skipped,
    Locked,
}

public static class NmStatusInfo
{
    /// <summary>Frozen DESIGN_SYSTEM §2.2 symbol set (Lead ruling 2026-10-30: queued = "·", not "◦").</summary>
    public static string Symbol(NmStatus status) => status switch
    {
        NmStatus.NotStarted => "○",
        NmStatus.Queued => "·",
        NmStatus.Running => "◐",
        NmStatus.Done => "●",
        NmStatus.Failed => "✗",
        NmStatus.Blocked => "▲",
        NmStatus.Stale => "▨",
        NmStatus.Skipped => "–",
        NmStatus.Locked => "▮",
        _ => "○",
    };

    public static string Label(NmStatus status) => status switch
    {
        NmStatus.NotStarted => "未开始",
        NmStatus.Queued => "排队",
        NmStatus.Running => "进行中",
        NmStatus.Done => "完成",
        NmStatus.Failed => "失败",
        NmStatus.Blocked => "阻塞",
        NmStatus.Stale => "过期",
        NmStatus.Skipped => "跳过",
        NmStatus.Locked => "锁定",
        _ => "未知",
    };

    /// <summary>Local style-class suffix used by the pre-DS fallback styles (removed after V11R-D-1).</summary>
    public static string ClassName(NmStatus status) => status switch
    {
        NmStatus.NotStarted => "st-not-started",
        NmStatus.Queued => "st-queued",
        NmStatus.Running => "st-running",
        NmStatus.Done => "st-done",
        NmStatus.Failed => "st-failed",
        NmStatus.Blocked => "st-blocked",
        NmStatus.Stale => "st-stale",
        NmStatus.Skipped => "st-skipped",
        NmStatus.Locked => "st-locked",
        _ => "st-not-started",
    };

    /// <summary>Colour token key backing one state (contract §2.2 naming).</summary>
    public static string BrushKey(NmStatus status) => status switch
    {
        NmStatus.NotStarted => "Nm.Color.Text.Disabled",
        NmStatus.Queued => "Nm.Color.Status.Queued",
        NmStatus.Running => "Nm.Color.Status.Running",
        NmStatus.Done => "Nm.Color.Status.Done",
        NmStatus.Failed => "Nm.Color.Status.Failed",
        NmStatus.Blocked => "Nm.Color.Status.Blocked",
        NmStatus.Stale => "Nm.Color.Status.Stale",
        NmStatus.Skipped => "Nm.Color.Status.Skipped",
        NmStatus.Locked => "Nm.Color.Status.Blocked",
        _ => "Nm.Color.Text.Disabled",
    };
}
