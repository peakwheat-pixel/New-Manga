using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using NewManga.App.ViewModels.V2.ThemeStudio;

namespace NewManga.App.Views.V2.ThemeStudio.Sections;

/// <summary>
/// ① 主题库 view. Owns the responsive grid metric (the ViewModel computes 4/3/2 columns and the card
/// width), the search-focus hook for Ctrl+F and the arrow/Enter card navigation.
/// </summary>
public partial class LibrarySectionView : UserControl
{
    private ThemeStudioLibraryViewModel? _viewModel;

    public LibrarySectionView()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => AttachViewModel();
        SizeChanged += (_, _) => UpdateGridMetrics();
        AddHandler(KeyDownEvent, OnKeyDown, RoutingStrategies.Bubble);
    }

    /// <summary>Focuses the search field (Ctrl+F from the surface).</summary>
    public void FocusSearch() => SearchBox.Focus();

    /// <summary>Scrolls the selected card into view (keyboard navigation).</summary>
    public void BringSelectionIntoView()
    {
        if (_viewModel?.SelectedCard is { } card)
        {
            CardItems.ContainerFromItem(card)?.BringIntoView();
        }
    }

    private void AttachViewModel()
    {
        if (ReferenceEquals(_viewModel, DataContext))
        {
            return;
        }

        _viewModel = DataContext as ThemeStudioLibraryViewModel;
        if (_viewModel is not null)
        {
            UpdateGridMetrics();
        }
    }

    /// <summary>
    /// The frozen breakpoints are window widths, while the card width depends on the content width this
    /// view actually gets (1600 window ≈ 1080px of content). Both are forwarded to the ViewModel.
    /// </summary>
    private void UpdateGridMetrics()
    {
        if (_viewModel is null)
        {
            return;
        }

        var windowWidth = TopLevel.GetTopLevel(this)?.ClientSize.Width ?? Bounds.Width;
        _viewModel.SetViewportMetrics(windowWidth, Bounds.Width);
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        if (_viewModel is null || e.Handled)
        {
            return;
        }

        if (TopLevel.GetTopLevel(this)?.FocusManager?.GetFocusedElement() is TextBox)
        {
            return;
        }

        switch (e.Key)
        {
            case Key.Down:
            case Key.Right:
                _viewModel.MoveSelection(1);
                BringSelectionIntoView();
                e.Handled = true;
                break;
            case Key.Up:
            case Key.Left:
                _viewModel.MoveSelection(-1);
                BringSelectionIntoView();
                e.Handled = true;
                break;
            case Key.Enter:
                _viewModel.PreviewSelected();
                e.Handled = true;
                break;
        }
    }
}
