using Avalonia.Controls;
using Avalonia.Interactivity;
using NewManga.App.ViewModels.V2.Library;

namespace NewManga.App.Views.V2.Library;

public partial class BookDetailPanel : UserControl
{
    public BookDetailPanel() => InitializeComponent();

    /// <summary>Page multi-selection checkbox: the selection lives in ShellState (single source).</summary>
    private void OnPageMultiToggle(object? sender, RoutedEventArgs e)
    {
        if (sender is Control { DataContext: PageRowViewModel page } &&
            DataContext is LibraryViewModel library)
        {
            library.TogglePageSelection(page);
        }
    }
}
