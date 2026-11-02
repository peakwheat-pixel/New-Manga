namespace NewManga.Presentation.Avalonia.Windows;

/// <summary>One physical/virtual display in the current topology (FEA-07 AC5 / A08).</summary>
public sealed record DisplayInfo(
    string Id,
    int X,
    int Y,
    int Width,
    int Height,
    double Scale,
    bool IsPrimary);

/// <summary>What to do with a secondary window after a topology change.</summary>
public enum SecondWindowDisposition
{
    /// <summary>The window's display still exists and the bounds are usable.</summary>
    KeepOnDisplay = 0,

    /// <summary>The window's display is gone; the window is parked inside the main display.</summary>
    MoveToPrimary = 1,

    /// <summary>
    /// The window's display is gone and the content belongs to the main window: content returns to the
    /// corresponding page, and any unflushed edit stays fail-closed in the main window buffer.
    /// </summary>
    ReturnContentToMainWindow = 2,
}

/// <summary>One secondary window's placement plan.</summary>
public sealed record SecondaryWindowPlan(
    string WindowId,
    SecondWindowDisposition Disposition,
    WindowStateMemento Memento);

/// <summary>The whole-topology plan applied at startup and after display changes.</summary>
public sealed record TopologyPlan(
    WindowStateMemento MainMemento,
    IReadOnlyList<SecondaryWindowPlan> Secondary,
    bool RetainUnsavedEditsInMainBuffer);

/// <summary>
/// FEA-07 AC5 / A08: display-topology planning. The pure policy is separated from Avalonia so it can be
/// verified headlessly: clamp mementos into an existing display (never restore off-screen), and when a
/// display disappears, return its second-window content to the main window with unflushed edits kept
/// fail-closed in the main buffer. Mixed-DPI layouts keep each window's own scale (no cross-scale rebase).
/// </summary>
public static class DisplayTopologyPlanner
{
    public const int DefaultMinWidth = 1024;
    public const int DefaultMinHeight = 640;

    /// <summary>Clamps one memento into the current displays; never returns off-screen bounds.</summary>
    public static WindowStateMemento Clamp(
        WindowStateMemento memento,
        IReadOnlyList<DisplayInfo> displays,
        int minWidth = DefaultMinWidth,
        int minHeight = DefaultMinHeight)
    {
        ArgumentNullException.ThrowIfNull(memento);
        ArgumentNullException.ThrowIfNull(displays);

        if (displays.Count == 0)
        {
            return memento;
        }

        var target = ResolveDisplay(memento, displays);
        var width = Math.Clamp(memento.Width, Math.Min(minWidth, target.Width), target.Width);
        var height = Math.Clamp(memento.Height, Math.Min(minHeight, target.Height), target.Height);
        var x = Math.Clamp(memento.X, target.X, target.X + target.Width - width);
        var y = Math.Clamp(memento.Y, target.Y, target.Y + target.Height - height);

        return memento with
        {
            X = x,
            Y = y,
            Width = width,
            Height = height,
            DisplayId = target.Id,
        };
    }

    /// <summary>Plans main + secondary windows after a topology change (拔屏/换主屏/混合 DPI).</summary>
    public static TopologyPlan Plan(
        IReadOnlyList<DisplayInfo> displays,
        WindowStateMemento main,
        IReadOnlyList<(string WindowId, WindowStateMemento Memento, bool HasUnsavedEdits)> secondaryWindows,
        int minWidth = DefaultMinWidth,
        int minHeight = DefaultMinHeight)
    {
        ArgumentNullException.ThrowIfNull(displays);
        ArgumentNullException.ThrowIfNull(main);
        ArgumentNullException.ThrowIfNull(secondaryWindows);

        var plans = new List<SecondaryWindowPlan>(secondaryWindows.Count);
        var retainUnsaved = false;
        foreach (var (windowId, memento, hasUnsavedEdits) in secondaryWindows)
        {
            ArgumentException.ThrowIfNullOrWhiteSpace(windowId);
            var displayExists = memento.DisplayId is { Length: > 0 } id &&
                displays.Any(display => string.Equals(display.Id, id, StringComparison.Ordinal));
            if (displayExists)
            {
                plans.Add(new SecondaryWindowPlan(windowId, SecondWindowDisposition.KeepOnDisplay, Clamp(memento, displays, minWidth, minHeight)));
                continue;
            }

            retainUnsaved |= hasUnsavedEdits;
            plans.Add(new SecondaryWindowPlan(
                windowId,
                SecondWindowDisposition.ReturnContentToMainWindow,
                Clamp(memento, displays, minWidth, minHeight)));
        }

        return new TopologyPlan(
            Clamp(main, displays, minWidth, minHeight),
            plans,
            retainUnsaved);
    }

    private static DisplayInfo ResolveDisplay(WindowStateMemento memento, IReadOnlyList<DisplayInfo> displays)
    {
        if (memento.DisplayId is { Length: > 0 } id)
        {
            var byId = displays.FirstOrDefault(display => string.Equals(display.Id, id, StringComparison.Ordinal));
            if (byId is not null)
            {
                return byId;
            }
        }

        // Prefer the display that contains the window center, then the primary, then the first display.
        var centerX = memento.X + (memento.Width / 2);
        var centerY = memento.Y + (memento.Height / 2);
        var containing = displays.FirstOrDefault(display =>
            centerX >= display.X && centerX < display.X + display.Width &&
            centerY >= display.Y && centerY < display.Y + display.Height);
        return containing ?? displays.FirstOrDefault(display => display.IsPrimary) ?? displays[0];
    }
}
