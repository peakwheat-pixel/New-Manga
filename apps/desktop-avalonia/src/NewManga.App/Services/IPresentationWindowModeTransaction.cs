using System;

namespace NewManga.App.Services;

/// <summary>
/// FEA-07 R-022/R-024: a window-mode snapshot taken at the start of one switch transaction. The owner
/// commits it when the transaction succeeds; disposing an uncommitted snapshot restores the previous
/// user-visible window mode (full screen / normal / maximized) together with the rolled-back content tree.
/// The snapshot lives inside the switch gate so queued or rejected requests never restore a stale mode.
/// </summary>
public interface IPresentationWindowModeTransaction : IDisposable
{
    /// <summary>Marks the transaction successful: disposal must not change the window mode.</summary>
    void Commit();
}
