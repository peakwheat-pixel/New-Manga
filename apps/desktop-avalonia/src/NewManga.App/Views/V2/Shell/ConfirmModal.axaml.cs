using Avalonia;
using Avalonia.Controls;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.Shell;

namespace NewManga.App.Views.V2.Shell;

public partial class ConfirmModal : UserControl
{
    private AppShellViewModel? _viewModel;

    public ConfirmModal()
    {
        InitializeComponent();
        PropertyChanged += (_, e) =>
        {
            if (e.Property == IsVisibleProperty && IsVisible)
            {
                AttachViewModel();
                FocusCancelLater();
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
        if (e.PropertyName == nameof(AppShellViewModel.IsConfirmOpen) && _viewModel?.IsConfirmOpen == true)
        {
            FocusCancelLater();
        }
    }

    /// <summary>DESIGN_SYSTEM §6.2: the modal opens with focus on 取消, never on the destructive action.</summary>
    private void FocusCancelLater() =>
        Dispatcher.UIThread.Post(() => CancelButton.Focus(), DispatcherPriority.Loaded);
}
