using Avalonia;
using Avalonia.Controls;
using NewManga.App.ViewModels.V2.Console;

namespace NewManga.App.Views.V2.Console;

/// <summary>
/// V11R-B-2/V11R-INT-0 Console space host. Section + content scroll offset are written back to the
/// ViewModel (and thus ShellState) so Ctrl+1/2/3 round-trips restore the exact ScrollViewer.Offset.
/// </summary>
public partial class ConsoleView : UserControl
{
    private ConsoleViewModel? _viewModel;
    private ScrollViewer? _contentScroll;

    public ConsoleView()
    {
        InitializeComponent();
        _contentScroll = this.FindControl<ScrollViewer>("ConsoleScroll");
        DataContextChanged += (_, _) => AttachViewModel();
    }

    /// <summary>Test/integration seam: the real section content ScrollViewer.</summary>
    public ScrollViewer? ContentScrollView => _contentScroll;

    private void AttachViewModel()
    {
        if (ReferenceEquals(_viewModel, DataContext))
        {
            return;
        }

        if (_viewModel is not null)
        {
            _viewModel.ScrollRestoreRequested -= OnScrollRestoreRequested;
        }

        _viewModel = DataContext as ConsoleViewModel;
        if (_viewModel is not null)
        {
            _viewModel.ScrollRestoreRequested += OnScrollRestoreRequested;
            RestoreScrollOffset();
        }
    }

    private void OnScrollRestoreRequested(object? sender, EventArgs e) => RestoreScrollOffset();

    private void RestoreScrollOffset()
    {
        if (_contentScroll is null || _viewModel is null)
        {
            return;
        }

        var offset = _contentScroll.Offset;
        _contentScroll.Offset = new Vector(offset.X, _viewModel.ScrollOffsetY);
    }

    private void OnConsoleScrollChanged(object? sender, ScrollChangedEventArgs e)
    {
        if (_viewModel is not null && sender is ScrollViewer scrollViewer)
        {
            _viewModel.ScrollOffsetY = scrollViewer.Offset.Y;
        }
    }
}
