using Avalonia.Controls;
using Avalonia.Input;

namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-INT-0 / contract §6.1: the workspace integration seam. The shell owns <see cref="ShellState"/>
/// and hands every workspace its activate/deactivate hooks so the workspace restores retained context
/// (scroll/filter/focus/selection) on entry and writes it back on exit — without ever being rebuilt.
///
/// R-17 extension: <see cref="TryHandleKey"/> gives a workspace first refusal on its own keys
/// (Studio: Tab/Esc/J/K/[ ]/+/-/0) before the shell's single KeyMap handles them; returning false means
/// "not mine" and the shell continues.
/// </summary>
public interface IWorkspaceView
{
    SpaceId Space { get; }

    /// <summary>Content hosted by the shell for this space (created once and reused).</summary>
    Control CreateContent();

    /// <summary>Restore scroll/filter/focus from <paramref name="state"/> when the space becomes active.</summary>
    void OnActivated(ShellState state);

    /// <summary>Write scroll/filter/selection back into <paramref name="state"/> before the space is left.</summary>
    void OnDeactivated(ShellState state);

    /// <summary>
    /// R-17: workspace-specific key handling before the shell KeyMap. Only called for the active space,
    /// and only after shell overlays (confirm/palette/jump/help) and IME safety took their turn.
    /// </summary>
    bool TryHandleKey(KeyEventArgs e, ShellState state);
}

/// <summary>
/// V11R-INT-0: an overlay-surface workspace (currently Theme Studio). Same lifecycle contract as
/// <see cref="IWorkspaceView"/>, but bound to a <see cref="ShellSurface"/> on the overlay stack instead
/// of a top-level space.
/// </summary>
public interface ISurfaceWorkspace
{
    ShellSurface Surface { get; }

    string DisplayName { get; }

    Control CreateContent();

    void OnActivated(ShellState state);

    void OnDeactivated(ShellState state);
}
