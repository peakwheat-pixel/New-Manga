using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Presenters;
using Avalonia.Controls.Templates;
using Avalonia.Data;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3 <c>FilmStrip</c>: 56px collapsed (44×56 thumbnail + number + status dot) ⇄ 200px expanded
/// (+ filename + state text). Thumbnails are the real page bytes read through the Host resource
/// channel; a page without a decoded thumbnail shows a neutral placeholder, never a fake image.
/// </summary>
public sealed class StudioFilmStrip : Border
{
    private readonly StudioPageViewModel _viewModel;
    private readonly Button _expandButton;
    private readonly ItemsControl _items;
    private readonly List<(StudioFilmPageItem Item, Control Expanded)> _expandedParts = new();

    public StudioFilmStrip(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;
        Classes.Add("studio-rail");

        _expandButton = StudioUi.Button("»", "icon ghost", () => _viewModel.FilmStripExpanded = !_viewModel.FilmStripExpanded);
        _expandButton.Width = 24;
        _expandButton.Height = 24;
        ToolTip.SetTip(_expandButton, "展开/收起胶片条（56 ⇄ 200）");

        var header = StudioUi.Row(4);
        header.Margin = new Thickness(4, 2);
        header.Children.Add(_expandButton);
        var count = StudioUi.BoundText(nameof(StudioPageViewModel.PageCount), "nm-num", "nm-muted");
        header.Children.Add(count);

        _items = new ItemsControl
        {
            ItemTemplate = new FuncDataTemplate<StudioFilmPageItem>((item, _) => BuildItem(item), true),
            ItemsSource = _viewModel.Pages,
            Margin = new Thickness(0, 2, 0, 4),
        };

        var scroll = new ScrollViewer
        {
            Content = _items,
            HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Auto,
        };

        var root = new Grid { RowDefinitions = new RowDefinitions("Auto,*") };
        Grid.SetRow(header, 0);
        Grid.SetRow(scroll, 1);
        root.Children.Add(header);
        root.Children.Add(scroll);
        Child = root;

        Width = _viewModel.FilmStripWidth;
        _viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioPageViewModel.FilmStripWidth) or null)
            {
                Width = _viewModel.FilmStripWidth;
                _expandButton.Content = _viewModel.FilmStripExpanded ? "«" : "»";
                UpdateExpandedParts();
            }
        };
    }

    /// <summary>One button per page (headless tests assert count/labels/selection).</summary>
    public IReadOnlyList<Button> PageButtons =>
        _items.GetRealizedContainers()
            .OfType<ContentPresenter>()
            .Select(presenter => presenter.Child)
            .OfType<Button>()
            .ToList();

    public ItemsControl ItemsHost => _items;

    public Button ExpandButton => _expandButton;

    private Button BuildItem(StudioFilmPageItem item)
    {
        var thumb = new Grid { Width = 44, Height = 56 };
        var placeholder = StudioUi.Box("studio-film-placeholder");
        placeholder.Child = StudioUi.Text("·", "nm-meta", "nm-center");
        thumb.Children.Add(placeholder);

        var image = new Image { Stretch = Stretch.Uniform, Classes = { "studio-film-thumb" } };
        thumb.Children.Add(image);

        var number = StudioUi.Text(item.NumberLabel, "nm-num");
        number.HorizontalAlignment = HorizontalAlignment.Right;
        number.VerticalAlignment = VerticalAlignment.Bottom;
        number.Margin = new Thickness(2);
        thumb.Children.Add(number);

        var stateGlyph = StudioUi.Text("·", "nm-num", "nm-state-nodata");
        stateGlyph.HorizontalAlignment = HorizontalAlignment.Left;
        stateGlyph.VerticalAlignment = VerticalAlignment.Top;
        stateGlyph.Margin = new Thickness(3);
        thumb.Children.Add(stateGlyph);

        var title = StudioUi.BoundText(nameof(StudioFilmPageItem.SourceFilename), "nm-meta");
        title.TextTrimming = TextTrimming.CharacterEllipsis;
        var stateText = StudioUi.BoundText(nameof(StudioFilmPageItem.StateLabel), "nm-meta", "nm-muted");
        var expanded = new StackPanel
        {
            Orientation = Orientation.Vertical,
            Spacing = 2,
            Width = 140,
            Margin = new Thickness(6, 0, 0, 0),
            VerticalAlignment = VerticalAlignment.Center,
            IsVisible = _viewModel.FilmStripExpanded,
        };
        expanded.Children.Add(title);
        expanded.Children.Add(stateText);

        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 4 };
        row.Children.Add(thumb);
        row.Children.Add(expanded);

        var button = StudioUi.Button(string.Empty, "studio-film-item");
        button.Content = row;
        button.HorizontalContentAlignment = HorizontalAlignment.Stretch;
        button.Width = _viewModel.FilmStripWidth - 2;
        ToolTip.SetTip(button, item.Tooltip);
        button.Click += (_, _) => _viewModel.RequestSelectPage(item.PageId);

        StudioUi.TrackClass(button, "active", item, () => item.IsCurrent);
        ApplyThumbnail(image, placeholder, item);
        item.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioFilmPageItem.ThumbnailBytes) or nameof(StudioFilmPageItem.HasThumbnail) or null)
            {
                ApplyThumbnail(image, placeholder, item);
            }

            if (args.PropertyName is nameof(StudioFilmPageItem.HasState) or nameof(StudioFilmPageItem.State) or null)
            {
                stateGlyph.Text = item.HasState ? item.StateGlyph : "·";
                stateGlyph.Classes.Set("nm-state-nodata", !item.HasState);
                foreach (var state in Enum.GetValues<StudioStateKind>())
                {
                    stateGlyph.Classes.Set(StudioStates.StyleClass(state), item.HasState && item.State == state);
                }
            }

            if (args.PropertyName is nameof(StudioFilmPageItem.IsCurrent) or null)
            {
                button.Classes.Set("active", item.IsCurrent);
            }
        };

        _expandedParts.Add((item, expanded));
        return button;
    }

    private static void ApplyThumbnail(Image image, Border placeholder, StudioFilmPageItem item)
    {
        if (!item.HasThumbnail)
        {
            image.Source = null;
            placeholder.IsVisible = true;
            return;
        }

        try
        {
            using var stream = new MemoryStream(item.ThumbnailBytes!);
            image.Source = new Bitmap(stream);
            placeholder.IsVisible = false;
        }
        catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or NotSupportedException)
        {
            image.Source = null;
            placeholder.IsVisible = true;
        }
    }

    private void UpdateExpandedParts()
    {
        var expanded = _viewModel.FilmStripExpanded;
        foreach (var (_, control) in _expandedParts)
        {
            control.IsVisible = expanded;
        }
    }
}
