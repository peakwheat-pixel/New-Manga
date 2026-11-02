namespace NewManga.App.Services;

/// <summary>
/// FEA-07 R-019: a frontend content tree that installs global (TopLevel-level) input handlers can be
/// parked while it sits in the hidden staging slot. Only the visible, committed frontend may consume
/// application shortcuts/focus, so a half-switched tree cannot swallow the previous UI's keys.
/// </summary>
public interface IPresentationInputState
{
    /// <summary>
    /// True for the active visible frontend, false while the tree is staged before commit. Implementations
    /// must detach/ignore their global input handlers while inactive.
    /// </summary>
    bool IsInputActive { get; set; }
}
