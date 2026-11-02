using System.ComponentModel;
using Avalonia;
using Avalonia.Controls;
using Avalonia.VisualTree;
using NewManga.App.ViewModels.V2.Library;

namespace NewManga.App.Views.V2.Library;

/// <summary>
/// Library space host. The book PageGrid is a WrapPanel whose cell metrics are computed by the
/// ViewModel from DS tokens + R-18 breakpoints (4 columns at 1600, 3 at 1280–1599, overlay detail
/// below 1280). Scroll position is written back to the ViewModel (and thus ShellState) on every
/// ScrollChanged and restored by <see cref="IWorkspaceView.OnActivated"/> — real ScrollViewer.Offset,
/// not a test-only copy.
/// </summary>
public partial class LibraryView : UserControl
{
    private LibraryViewModel? _viewModel;
    private WrapPanel? _bookPanel;
    private ScrollViewer? _booksScroll;

    public LibraryView()
    {
        InitializeComponent();
        _booksScroll = this.FindControl<ScrollViewer>("BooksScroll");
        DataContextChanged += (_, _) => AttachViewModel();
        SizeChanged += (_, e) => _viewModel?.SetViewport(e.NewSize.Width, e.NewSize.Height);
        LayoutUpdated += (_, _) => ApplyGridMetrics();
    }

    /// <summary>Test/integration seam: the real book-grid ScrollViewer (assert Offset across space switches).</summary>
    public ScrollViewer? BooksScrollView => _booksScroll;

    private void AttachViewModel()
    {
        if (ReferenceEquals(_viewModel, DataContext))
        {
            return;
        }

        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged -= OnViewModelPropertyChanged;
            _viewModel.ScrollRestoreRequested -= OnScrollRestoreRequested;
        }

        _viewModel = DataContext as LibraryViewModel;
        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged += OnViewModelPropertyChanged;
            _viewModel.ScrollRestoreRequested += OnScrollRestoreRequested;
            _viewModel.SetViewport(Bounds.Width, Bounds.Height);
            RestoreScrollOffset();
        }
    }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName is nameof(LibraryViewModel.CardSlotWidth) or nameof(LibraryViewModel.CardSlotHeight))
        {
            ApplyGridMetrics();
        }
    }

    private void OnScrollRestoreRequested(object? sender, EventArgs e) => RestoreScrollOffset();

    private void RestoreScrollOffset()
    {
        if (_booksScroll is null || _viewModel is null)
        {
            return;
        }

        var offset = _booksScroll.Offset;
        _booksScroll.Offset = new Vector(offset.X, _viewModel.ScrollOffsetY);
    }

    private void OnBooksScrollChanged(object? sender, ScrollChangedEventArgs e)
    {
        if (_viewModel is not null && sender is ScrollViewer scrollViewer)
        {
            _viewModel.ScrollOffsetY = scrollViewer.Offset.Y;
        }
    }

    private void ApplyGridMetrics()
    {
        if (_viewModel is null)
        {
            return;
        }

        _bookPanel ??= BookGrid.GetVisualDescendants().OfType<WrapPanel>().FirstOrDefault();
        if (_bookPanel is null)
        {
            return;
        }

        if (Math.Abs(_bookPanel.ItemWidth - _viewModel.CardSlotWidth) > 0.5)
        {
            _bookPanel.ItemWidth = _viewModel.CardSlotWidth;
        }

        if (Math.Abs(_bookPanel.ItemHeight - _viewModel.CardSlotHeight) > 0.5)
        {
            _bookPanel.ItemHeight = _viewModel.CardSlotHeight;
        }
    }
}
