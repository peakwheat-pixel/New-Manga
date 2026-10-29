using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.Shell;

namespace NewManga.App.Views.V2.Shell;

public partial class CommandPaletteOverlay : UserControl
{
    private AppShellViewModel? _viewModel;

    public CommandPaletteOverlay()
    {
        InitializeComponent();
        PropertyChanged += OnOwnPropertyChanged;
        DataContextChanged += (_, _) => AttachViewModel();
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

        _viewModel = DataContext as AppShellViewModel;
        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }

    private void OnOwnPropertyChanged(object? sender, AvaloniaPropertyChangedEventArgs e)
    {
        if (e.Property == IsVisibleProperty && IsVisible)
        {
            AttachViewModel();
            FocusSearchLater();
        }
    }

    private void OnViewModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(AppShellViewModel.IsPaletteOpen) && _viewModel?.IsPaletteOpen == true)
        {
            FocusSearchLater();
        }
    }

    private void FocusSearchLater() =>
        Dispatcher.UIThread.Post(
            () =>
            {
                PaletteSearch.Focus();
                PaletteSearch.SelectAll();
            },
            DispatcherPriority.Loaded);

    private void OnPaletteDoubleTapped(object? sender, TappedEventArgs e) => _viewModel?.ExecutePaletteSelection();
}
