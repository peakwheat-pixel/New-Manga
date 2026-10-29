using Avalonia.Controls;
using Avalonia.Input;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Console;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.Views.V2.Console;
using NewManga.App.Views.V2.Library;

namespace NewManga.App.ViewModels.V2.Shell;

/// <summary>
/// V11R-INT-0: Library workspace adapter (contract §6.1). The content is created exactly once and the
/// hooks only flush/restore retained context; the shell never rebuilds this ViewModel (AC2).
/// </summary>
public sealed class LibraryWorkspaceView : IWorkspaceView
{
    private readonly LibraryViewModel _viewModel;
    private Control? _content;

    public LibraryWorkspaceView(LibraryViewModel viewModel) => _viewModel = viewModel;

    public SpaceId Space => SpaceId.Library;

    public Control CreateContent() => _content ??= new LibraryView { DataContext = _viewModel };

    public void OnActivated(ShellState state)
    {
        _viewModel.RestoreViewState(state.LibraryView);
    }

    public void OnDeactivated(ShellState state)
    {
        _viewModel.CaptureViewState(state.LibraryView);
    }

    public bool TryHandleKey(KeyEventArgs e, ShellState state) => false;
}

/// <summary>
/// V11R-INT-0: Console workspace adapter (contract §6.1). Section + scroll context is written back to
/// the per-space <see cref="SpaceViewState"/> and restored on activation.
/// </summary>
public sealed class ConsoleWorkspaceView : IWorkspaceView
{
    private readonly ConsoleViewModel _viewModel;
    private Control? _content;

    public ConsoleWorkspaceView(ConsoleViewModel viewModel) => _viewModel = viewModel;

    public SpaceId Space => SpaceId.Console;

    public Control CreateContent() => _content ??= new ConsoleView { DataContext = _viewModel };

    public void OnActivated(ShellState state)
    {
        _viewModel.RestoreViewState(state.ConsoleView);
    }

    public void OnDeactivated(ShellState state)
    {
        _viewModel.CaptureViewState(state.ConsoleView);
    }

    public bool TryHandleKey(KeyEventArgs e, ShellState state) => false;
}
