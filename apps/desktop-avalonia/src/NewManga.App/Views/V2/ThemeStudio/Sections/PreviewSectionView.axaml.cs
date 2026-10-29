using System.ComponentModel;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.ThemeStudio;

namespace NewManga.App.Views.V2.ThemeStudio.Sections;

/// <summary>
/// ② 预览 view. Applies the 50/75/100% zoom as a render transform on the preview host (layout is not
/// rebuilt, so switching zoom cannot re-create the control tree) and re-renders on VM changes.
/// </summary>
public partial class PreviewSectionView : UserControl
{
    private ThemeStudioPreviewViewModel? _viewModel;

    public PreviewSectionView()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => AttachViewModel();
    }

    /// <summary>
    /// Installs an integration-supplied surface provider (V11R-INT-1 seam). A null mode keeps the studio's
    /// own real control tree, so this call is always safe.
    /// </summary>
    public void ApplySurfaceProvider(Preview.IPreviewSurfaceProvider? provider)
    {
        if (provider is null)
        {
            return;
        }

        ShelfHost.Content = provider.CreateSurface(ThemeStudioPreviewMode.Shelf) ?? ShelfHost.Content;
        WorkbenchHost.Content = provider.CreateSurface(ThemeStudioPreviewMode.Workbench) ?? WorkbenchHost.Content;
        ReaderHost.Content = provider.CreateSurface(ThemeStudioPreviewMode.Reader) ?? ReaderHost.Content;
    }

    private void AttachViewModel()
    {
        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged -= OnViewModelPropertyChanged;
        }

        _viewModel = DataContext as ThemeStudioPreviewViewModel;
        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged += OnViewModelPropertyChanged;
            ApplyZoom();
        }
    }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(ThemeStudioPreviewViewModel.Zoom))
        {
            ApplyZoom();
        }
    }

    private void ApplyZoom()
    {
        var zoom = _viewModel?.Zoom ?? 1.0;
        PreviewHost.RenderTransform = Math.Abs(zoom - 1.0) < 0.001
            ? null
            : new ScaleTransform(zoom, zoom);
        PreviewHost.RenderTransformOrigin = new RelativePoint(0, 0, RelativeUnit.Relative);
    }
}
