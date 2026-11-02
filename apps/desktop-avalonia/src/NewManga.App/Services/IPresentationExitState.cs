namespace NewManga.App.Services;

/// <summary>
/// FEA-07 AC2: production content trees expose their live exit-blocking state so the stable window can
/// consult real edit/run state (not just registered tokens) when the user asks to close.
/// </summary>
public interface IPresentationExitState
{
    /// <summary>True when the hosted content has unsaved edits.</summary>
    bool HasUnsavedEdits { get; }

    /// <summary>True when a run/import is still active in the hosted content.</summary>
    bool HasActiveRuns { get; }
}
