using System.ComponentModel;
using Avalonia;
using Avalonia.Controls;
using Avalonia.VisualTree;
using NewManga.App.ViewModels.V2.Library;

namespace NewManga.App.Views.V2.Library;

/// <summary>
/// Library space host. The book PageGrid is a WrapPanel whose cell metrics are computed by the
/// ViewModel (4 columns at 1600, 3 at 1280, compliant at 1024 without horizontal page scroll).
/// </summary>
public partial class LibraryView : UserControl
{
    private LibraryViewModel? _viewModel;
    private WrapPanel? _bookPanel;

    public LibraryView()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => AttachViewModel();
        SizeChanged += (_, e) => _viewModel?.SetViewport(e.NewSize.Width, e.NewSize.Height);
        LayoutUpdated += (_, _) => ApplyGridMetrics();
    }

    private void AttachViewModel()
    {
        if (ReferenceEquals(_viewModel, DataContext))
        {
            return;
        }

        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged -= OnViewModelPropertyChanged;
        }

        _viewModel = DataContext as LibraryViewModel;
        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged += OnViewModelPropertyChanged;
            _viewModel.SetViewport(Bounds.Width, Bounds.Height);
        }
    }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName is nameof(LibraryViewModel.CardSlotWidth) or nameof(LibraryViewModel.CardSlotHeight))
        {
            ApplyGridMetrics();
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
