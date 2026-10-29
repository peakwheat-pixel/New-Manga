using Avalonia.Controls;
using Avalonia.Input;
using NewManga.App.Shell.V2;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.Console;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.App.Views.V2.Console;
using NewManga.App.Views.V2.Library;
using NewManga.App.Views.V2.Studio.Controls;

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

/// <summary>
/// V11R-INT-0: Studio workspace adapter over ui-studio's <see cref="StudioWorkspaceView"/> (I2c).
/// Selection is the shell's own <see cref="ShellState.Selection"/> via <see cref="StudioSelection"/>, so
/// switching spaces never loses book/chapter/page/region; activation restores viewport and loads the
/// selected chapter through the real Host chain. R-17: Studio keys (Tab/Esc/J/K/[ ]/+/-/0) are offered
/// to the workspace before the shell KeyMap.
/// </summary>
public sealed class StudioWorkspaceAdapter : IWorkspaceView
{
    private readonly StudioWorkspaceView _view;
    private Control? _content;
    private string? _loadedBookId;
    private string? _loadedChapterId;
    private bool _loadInFlight;
    private bool _modeSyncSubscribed;
    private IReadOnlyList<string> _multiPageAtActivation = Array.Empty<string>();

    public StudioWorkspaceAdapter(StudioWorkspaceView view) => _view = view;

    public StudioWorkspaceView View => _view;

    public SpaceId Space => SpaceId.Studio;

    public Control CreateContent() => _content ??= _view;

    public void OnActivated(ShellState state)
    {
        if (!_modeSyncSubscribed)
        {
            _modeSyncSubscribed = true;
            state.ModeChanged += (_, _) => SyncStudioMode(state.StudioMode);
        }

        _view.Activate();
        _view.SwitchMode(state.StudioMode == StudioMode.Page
            ? StudioWorkspaceMode.Page
            : StudioWorkspaceMode.Batch);

        var bookId = state.Selection.BookId;
        var chapterId = state.Selection.ChapterId;
        _multiPageAtActivation = state.Selection.MultiPage;
        if (_loadInFlight
            || (string.Equals(_loadedBookId, bookId, StringComparison.Ordinal)
                && string.Equals(_loadedChapterId, chapterId, StringComparison.Ordinal)))
        {
            return;
        }

        _ = LoadAsync(bookId, chapterId, state);
    }

    private async Task LoadAsync(string? bookId, string? chapterId, ShellState state)
    {
        _loadInFlight = true;
        var multiPage = state.Selection.MultiPage;
        try
        {
            var loaded = await _view.LoadAndRenderAsync(bookId, chapterId).ConfigureAwait(true);
            if (loaded)
            {
                _loadedBookId = _view.ViewModel.Page.Selection.BookId;
                _loadedChapterId = _view.ViewModel.Page.Selection.ChapterId;
                // AC2: reloading the same context through Studio must not wipe the explicit
                // multi-page selection (R-16: explicit selection wins).
                if (multiPage.Count > 0 && state.Selection.MultiPage.Count == 0)
                {
                    state.SetMultiPage(multiPage);
                }
            }
        }
        catch (Exception exception) when (exception is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            // The Studio surface renders its own honest error/empty state; the shell must not crash.
        }
        finally
        {
            _loadInFlight = false;
        }
    }

    public void OnDeactivated(ShellState state)
    {
        // AC2/R-16: Studio re-selects the current book/chapter while loading; never let that wipe the
        // shell's explicit multi-page selection on the way out.
        if (_multiPageAtActivation.Count > 0 && state.Selection.MultiPage.Count == 0)
        {
            state.SetMultiPage(_multiPageAtActivation);
        }

        // StudioSelection is a projection over ShellState.Selection; only the viewport is released.
        _view.Deactivate();
    }

    private void SyncStudioMode(StudioMode mode) =>
        _view.SwitchMode(mode == StudioMode.Page ? StudioWorkspaceMode.Page : StudioWorkspaceMode.Batch);

    public bool TryHandleKey(KeyEventArgs e, ShellState state)
    {
        // R-17: Studio owns Tab/Esc/J/K/[ ]/+/-/0 inside its surface.
        if (StudioKeyboard.Handle(_view.ViewModel.Page, _view, e))
        {
            return true;
        }

        if (e.Key == Key.Tab)
        {
            // R-17 + contract §6.3: Studio owns Tab; keep the shell StudioMode in sync with the
            // workspace guard-aware switch so breadcrumb/StatusBand/palette agree.
            var next = state.StudioMode == StudioMode.Batch ? StudioMode.Page : StudioMode.Batch;
            var viewMode = next == StudioMode.Page ? StudioWorkspaceMode.Page : StudioWorkspaceMode.Batch;
            if (_view.SwitchMode(viewMode))
            {
                state.SetStudioMode(next);
            }

            return true;
        }

        return false;
    }
}
