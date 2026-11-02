using Avalonia.Controls;
using NewManga.App.Services;
using NewManga.App.Shell.V2;

namespace NewManga.App.Shell.V2.Studio;

/// <summary>
/// INT-1 hand-off: the ui-shell registers Studio through this factory (it owns <see cref="ShellState"/>
/// and the host). The factory returns an <see cref="IWorkspaceView"/>; no shell file is modified here.
/// </summary>
public static class StudioWorkspaceFactory
{
    public static IWorkspaceView Create(IHostController host, ShellState state) =>
        new StudioWorkspaceView(new ViewModels.V2.Studio.StudioWorkspaceViewModel(
            host,
            new ViewModels.V2.Studio.StudioSelection(state)));
}
