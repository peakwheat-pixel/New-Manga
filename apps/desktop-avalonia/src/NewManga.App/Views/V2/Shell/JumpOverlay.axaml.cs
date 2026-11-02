using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.Shell;

namespace NewManga.App.Views.V2.Shell;

public partial class JumpOverlay : UserControl
{
    private AppShellViewModel? _viewModel;

    public JumpOverlay()
    {
        InitializeComponent();
        PropertyChanged += (_, e) =>
        {
            if (e.Property == IsVisibleProperty && IsVisible)
            {
                AttachViewModel();
                FocusSearchLater();
            }
        };
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

    private void OnViewModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(AppShellViewModel.IsJumpOpen) && _viewModel?.IsJumpOpen == true)
        {
            FocusSearchLater();
        }
    }

    private void FocusSearchLater() =>
        Dispatcher.UIThread.Post(
            () =>
            {
                JumpSearch.Focus();
                JumpSearch.SelectAll();
            },
            DispatcherPriority.Loaded);

    private void OnJumpDoubleTapped(object? sender, TappedEventArgs e) => _viewModel?.ExecuteJumpSelection();
}
