namespace NewManga.Presentation.Avalonia.Switching;

/// <summary>
/// FEA-07 (proposal §7.1/§15.5): the observable stages of one frontend switch. A switch may only be
/// reported as successful after <see cref="Committed"/>; every earlier stage is recoverable.
/// </summary>
public enum SwitchStage
{
    /// <summary>No switch in progress (journal cleared).</summary>
    Idle = 0,

    /// <summary>Validating the requested frontend against the frozen selector semantics.</summary>
    Preparing = 1,

    /// <summary>Building the replacement content tree without touching the live one.</summary>
    Building = 2,

    /// <summary>The replacement tree completed layout with valid geometry.</summary>
    Layout = 3,

    /// <summary>Loaded callbacks completed (input routing and focus can be prepared).</summary>
    Loaded = 4,

    /// <summary>Rendered at least one frame; the swap is committed to the live window.</summary>
    Rendered = 5,

    /// <summary>The switch is committed; the journal entry is cleared.</summary>
    Committed = 6,

    /// <summary>The switch failed and the previous UI was restored.</summary>
    RolledBack = 7,
}
