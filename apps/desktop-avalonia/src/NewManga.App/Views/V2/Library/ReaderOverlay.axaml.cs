using Avalonia.Controls;
using Avalonia.Threading;
using Avalonia.Interactivity;
using Avalonia;
using NewManga.App.ViewModels.V2.Library;

namespace NewManga.App.Views.V2.Library;

public partial class ReaderOverlay : UserControl
{
    public ReaderOverlay() => InitializeComponent();

    private void OnLoaded(object? sender, RoutedEventArgs e)
    {
        if (DataContext is not ReaderOverlayViewModel viewModel) return;
        Dispatcher.UIThread.Post(() => RestoreWebtoonOffset(viewModel), DispatcherPriority.Loaded);
    }

    private void RestoreWebtoonOffset(ReaderOverlayViewModel viewModel)
    {
        if (!viewModel.IsWebtoon || this.FindControl<ScrollViewer>("WebtoonScroll") is not { } scroll) return;
        var scrollable = scroll.Extent.Height - scroll.Viewport.Height;
        if (scrollable <= 0) return;
        scroll.Offset = new Vector(scroll.Offset.X, scrollable * viewModel.WebtoonScrollPercent);
    }

    /// <summary>Webtoon scroll → progress percent (dual-modality progress keeps both page and %).</summary>
    private void OnWebtoonScrollChanged(object? sender, ScrollChangedEventArgs e)
    {
        if (DataContext is not ReaderOverlayViewModel viewModel || sender is not ScrollViewer scroll)
        {
            return;
        }

        var scrollable = scroll.Extent.Height - scroll.Viewport.Height;
        var percent = scrollable <= 0 ? 0 : scroll.Offset.Y / scrollable;
        viewModel.UpdateWebtoonProgress(percent);
    }
}
