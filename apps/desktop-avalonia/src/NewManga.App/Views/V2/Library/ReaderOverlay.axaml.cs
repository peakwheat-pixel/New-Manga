using Avalonia.Controls;
using NewManga.App.ViewModels.V2.Library;

namespace NewManga.App.Views.V2.Library;

public partial class ReaderOverlay : UserControl
{
    public ReaderOverlay() => InitializeComponent();

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
