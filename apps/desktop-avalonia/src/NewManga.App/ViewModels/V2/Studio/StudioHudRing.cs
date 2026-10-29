namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// The eight HUD ring actions (DESIGN_SYSTEM §6.4 <c>HUDRing</c>: N/NE/E/SE/S/SW/W/NW).
/// Navigation actions are always available; write actions go through
/// <see cref="StudioCapabilityGate"/>, so the F0-1 ones render disabled with the "能力待接入"
/// tooltip instead of silently doing nothing.
/// </summary>
public enum StudioHudAction
{
    /// <summary>N — open the inspector 文本 tab.</summary>
    ShowTextTier,

    /// <summary>NE — open the inspector 样式 tab (region type picker).</summary>
    ShowStyle,

    /// <summary>E — open the inspector 历史 tab (revision list).</summary>
    ShowHistory,

    /// <summary>SE — rerender the current page (wired: rerender_page).</summary>
    RerenderPage,

    /// <summary>S — restore the previous revision (wired: restore_region_revision).</summary>
    RestorePreviousRevision,

    /// <summary>SW — re-OCR this region (NOT_WIRED: V11R-F0-1).</summary>
    ReOcrRegion,

    /// <summary>W — toggle the region lock (NOT_WIRED: V11R-F0-1).</summary>
    ToggleLock,

    /// <summary>NW — delete this region (NOT_WIRED: V11R-F0-1).</summary>
    DeleteRegion,
}

/// <summary>One HUD ring slot: position, face label and the command it executes.</summary>
public sealed record StudioHudSlot(
    StudioHudAction Action,
    string Position,
    string Label,
    string Glyph,
    StudioCommand? Command,
    bool IsNavigation)
{
    /// <summary>True when the slot only switches inspector context (always available).</summary>
    public bool AlwaysEnabled => IsNavigation;
}

/// <summary>
/// The frozen HUD ring: eight slots in ring order. <c>Tab</c> cycles the focus through this list and
/// <c>Enter</c> executes the focused slot (SCREEN_SPECS §3). Disabled slots are skipped by the cycle
/// (an action you cannot run must not trap keyboard focus).
/// </summary>
public static class StudioHudRing
{
    public static IReadOnlyList<StudioHudSlot> Slots { get; } = new[]
    {
        new StudioHudSlot(StudioHudAction.ShowTextTier, "N", "编辑文本", "T", null, true),
        new StudioHudSlot(StudioHudAction.ShowStyle, "NE", "改类型", "Y", null, true),
        new StudioHudSlot(StudioHudAction.ShowHistory, "E", "历史版本", "H", null, true),
        new StudioHudSlot(StudioHudAction.RerenderPage, "SE", "重渲染页", "R", StudioCommand.RerenderPage, false),
        new StudioHudSlot(StudioHudAction.RestorePreviousRevision, "S", "恢复上版", "U", StudioCommand.RestoreRevision, false),
        new StudioHudSlot(StudioHudAction.ReOcrRegion, "SW", "重 OCR", "O", StudioCommand.ReOcrRegion, false),
        new StudioHudSlot(StudioHudAction.ToggleLock, "W", "锁定", "L", StudioCommand.LockRegion, false),
        new StudioHudSlot(StudioHudAction.DeleteRegion, "NW", "删除", "D", StudioCommand.DeleteRegion, false),
    };

    public static int Count => Slots.Count;

    /// <summary>
    /// Deterministic cycle: positive = clockwise. Starts from <paramref name="current"/> (-1 = no
    /// focus yet) and always lands on an executable slot; returns -1 only when nothing is executable.
    /// </summary>
    public static int Cycle(int current, int direction, Func<StudioHudSlot, bool> canExecute)
    {
        if (Slots.Count == 0 || direction == 0)
        {
            return current;
        }

        var step = direction > 0 ? 1 : -1;
        var index = current;
        for (var attempt = 0; attempt < Slots.Count; attempt++)
        {
            index = ((index + step) % Slots.Count + Slots.Count) % Slots.Count;
            if (canExecute(Slots[index]))
            {
                return index;
            }
        }

        return -1;
    }

    /// <summary>Slots in ring order (used by tests to assert the N→NE→…→NW order).</summary>
    public static IReadOnlyList<string> Positions { get; } = Slots.Select(slot => slot.Position).ToArray();
}
