using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Controls.Templates;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Immutable;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.CoreClient;
using NewManga.Theme;

namespace NewManga.App.Views;

internal static class Ui
{
    public static SolidColorBrush B(string token) => (SolidColorBrush)ThemePackService.Brush(token);

    public static TextBlock Text(string text, double size, string? colorToken = "TextPrimary", bool bold = false) => new()
    {
        Text = text,
        FontSize = size,
        FontWeight = bold ? FontWeight.SemiBold : FontWeight.Normal,
        Foreground = colorToken is null ? null : ThemePackService.Brush(colorToken),
        TextWrapping = TextWrapping.Wrap,
    };

    public static Button Action(string label, Action onClick, bool primary = false)
    {
        var button = new Button
        {
            Content = label,
            Padding = new Thickness(14, 7),
            CornerRadius = new CornerRadius(8),
            FontSize = 13,
            Background = primary ? ThemePackService.Brush("Accent") : ThemePackService.Brush("CardBg"),
            Foreground = primary ? ThemePackService.Brush("AccentText") : ThemePackService.Brush("TextPrimary"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        button.Click += (_, _) => onClick();
        return button;
    }
}

/// <summary>
/// AC3 bookshelf page (Saber-informed, not pixel-identical).
/// THEME-MACOS-LAYOUTS-1: three structural layouts share one ViewModel, one book-card template and the
/// same public members. The Sonoma tree is the THEME-MACOS-1 tree, unchanged; the Launchpad / Split
/// layouts re-parent the same header, search card, grid and detail panel into their own pre-built slots,
/// because Avalonia allows one visual parent per control (every switch detaches before it attaches).
/// </summary>
public sealed class BookshelfPage : UserControl
{
    private readonly Border _header;
    private readonly TextBlock _headerTitle;
    private readonly TextBlock _headerSubtitle;
    private readonly Border _searchCard;
    private readonly StackPanel _detailBody;
    private readonly Border _detailPanel;
    private readonly StackPanel _emptyPanel;
    private readonly StackPanel _noResultsPanel;
    private readonly TextBlock _status;
    private readonly StackPanel _statusRow;
    private readonly Grid _contentGrid;
    private readonly IHostController? _controller;
    private readonly IFilePickerGateway? _picker;
    private readonly ImportPanel? _importPanel;
    private readonly Button _importFilesButton;
    private readonly Button _importFolderButton;
    private readonly ItemsControl _splitBookList;

    // Sonoma (THEME-MACOS-1) tree: the structure is persistent, only the shared blocks move between slots.
    private readonly Grid _sonomaRoot;
    private readonly Grid _sonomaInner;
    private readonly Grid _sonomaBody;
    private readonly Grid _sonomaContentRow;
    private readonly Grid _sonomaHeaderSlot;
    private readonly Grid _sonomaSearchSlot;
    private readonly Grid _sonomaGridSlot;
    private readonly Grid _sonomaDetailSlot;
    private readonly StackPanel _sonomaStatusSlot;
    private readonly Grid _sonomaOverlaySlot;

    // Launchpad tree: compact header + centred 1200-wide icon grid + right detail overlay + bottom inset.
    private readonly Grid _launchpadRoot;
    private readonly Grid _launchpadHeaderSlot;
    private readonly Grid _launchpadSearchSlot;
    private readonly Grid _launchpadContentHost;
    private readonly Grid _launchpadGridSlot;
    private readonly Grid _launchpadDetailSlot;
    private readonly StackPanel _launchpadStatusSlot;
    private readonly Grid _launchpadOverlaySlot;

    // Split tree: 260px book list on the left, search / grid / detail on the right (Finder style).
    private readonly Grid _splitRoot;
    private readonly Grid _splitBody;
    private readonly Border _splitLeft;
    private readonly TextBlock _splitListTitle;
    private readonly Grid _splitHeaderSlot;
    private readonly Grid _splitSearchSlot;
    private readonly Grid _splitGridSlot;
    private readonly Grid _splitDetailSlot;
    private readonly StackPanel _splitStatusSlot;
    private readonly Grid _splitOverlaySlot;
    private readonly Grid _splitRight;
    private readonly Grid _splitRightBody;

    /// <summary>THEME-MACOS-LAYOUTS-1: layout currently applied to this page.</summary>
    private LayoutProfile _layout = LayoutProfiles.Sonoma;

    public BookshelfPage(
        BookshelfViewModel viewModel,
        IHostController? controller = null,
        IFilePickerGateway? picker = null)
    {
        ViewModel = viewModel;
        _controller = controller;
        _picker = picker;
        Name = "BookshelfPage";

        _status = Ui.Text("只读骨架 · 数据经 Core command dispatcher", 12, "TextSecondary");
        _statusRow = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        _statusRow.Children.Add(_status);

        // ---- header: one instance, restyled/reparented per layout ----
        _headerTitle = Ui.Text("书架", 26, null, bold: true);
        _headerSubtitle = Ui.Text("Saber-informed shell · 顶部渐变 / 1400 居中 / 3:4 书卡", 12, null);
        var headerText = new StackPanel { Spacing = 4 };
        headerText.Children.Add(_headerTitle);
        headerText.Children.Add(_headerSubtitle);
        var headerGrid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        headerGrid.Children.Add(headerText);
        var actions = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, VerticalAlignment = VerticalAlignment.Center };
        // IMPORT-EXPORT-UI-1 AC1: system-picker entries. The buttons are always present; an inert
        // controller/picker reports the typed "not ready" state instead of pretending to import.
        _importFilesButton = Ui.Action("导入文件", () => LastImportOperation = BeginImportAsync(ImportSourceKind.Files));
        _importFilesButton.Name = "ImportFilesButton";
        _importFolderButton = Ui.Action("导入文件夹", () => LastImportOperation = BeginImportAsync(ImportSourceKind.Folder));
        _importFolderButton.Name = "ImportFolderButton";
        var newButton = Ui.Action("新建", () => OpenNewDialog(), primary: true);
        newButton.Name = "NewBookButton";
        var refreshButton = Ui.Action("刷新", () => _ = ViewModel.RefreshAsync());
        refreshButton.Name = "RefreshButton";
        actions.Children.Add(_importFilesButton);
        actions.Children.Add(_importFolderButton);
        actions.Children.Add(newButton);
        actions.Children.Add(refreshButton);
        Grid.SetColumn(actions, 1);
        headerGrid.Children.Add(actions);
        _header = new Border
        {
            Padding = new Thickness(28, 18),
            Background = ThemePackService.Brush("HeaderGradient"),
            Child = headerGrid,
        };

        // ---- search card: search box + tag chips (shared by all three layouts) ----
        var searchBox = new TextBox
        {
            Watermark = "搜索书名 / 原书名",
            FontSize = 13,
            Height = 36,
            CornerRadius = new CornerRadius(9),
            Background = ThemePackService.Brush("SearchBg"),
            Name = "SearchBox",
        };
        searchBox.TextChanged += (_, _) => ViewModel.SearchText = searchBox.Text ?? string.Empty;
        SearchBox = searchBox;

        TagChips = new ItemsControl { ItemsPanel = new FuncTemplate<Panel?>(() => new WrapPanel()), ItemsSource = ViewModel.Tags };
        TagChips.ItemTemplate = new FuncDataTemplate<string>((tag, _) =>
        {
            var chip = new Button
            {
                Content = tag,
                Margin = new Thickness(0, 0, 8, 0),
                Padding = new Thickness(12, 5),
                CornerRadius = new CornerRadius(14),
                FontSize = 12,
                Background = string.Equals(tag, ViewModel.SelectedTag, StringComparison.Ordinal)
                    ? ThemePackService.Brush("ChipActiveBg")
                    : ThemePackService.Brush("ChipBg"),
                Foreground = string.Equals(tag, ViewModel.SelectedTag, StringComparison.Ordinal)
                    ? ThemePackService.Brush("AccentText")
                    : ThemePackService.Brush("TextSecondary"),
            };
            chip.Click += (_, _) => ViewModel.SelectedTag = tag;
            return chip;
        });
        var searchGrid = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto"), RowSpacing = 10 };
        searchGrid.Children.Add(searchBox);
        var chipScroll = new ScrollViewer
        {
            HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
            VerticalScrollBarVisibility = ScrollBarVisibility.Disabled,
            Content = TagChips,
        };
        Grid.SetRow(chipScroll, 1);
        searchGrid.Children.Add(chipScroll);
        _searchCard = new Border
        {
            Padding = new Thickness(18),
            CornerRadius = new CornerRadius(14),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
            Child = searchGrid,
        };

        // ---- book grid + empty / no-results states (one content grid, never reparented internally) ----
        GridPanel = new UniformGrid { Columns = ViewModel.ColumnCount };
        BookGrid = new ItemsControl { ItemsSource = ViewModel.Books, ItemsPanel = new FuncTemplate<Panel?>(() => GridPanel) };
        BookGrid.ItemTemplate = new FuncDataTemplate<BookCardItem>((item, _) => BuildCard(item));
        var scroll = new ScrollViewer
        {
            Content = BookGrid,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
        };

        _emptyPanel = BuildState("书架还是空的", "新建一本书，或让 Host 导入文件；数据只经 Core 访问。");
        _noResultsPanel = BuildState("没有匹配的书", "换个关键词，或切回「全部」标签。");
        _noResultsPanel.IsVisible = false;

        _contentGrid = new Grid();
        _contentGrid.Children.Add(scroll);
        _contentGrid.Children.Add(_emptyPanel);
        _contentGrid.Children.Add(_noResultsPanel);

        // ---- detail panel: right-side card, overlay in the Launchpad layout ----
        _detailBody = new StackPanel { Spacing = 10 };
        _detailPanel = new Border
        {
            Width = 360,
            Padding = new Thickness(20),
            HorizontalAlignment = HorizontalAlignment.Right,
            VerticalAlignment = VerticalAlignment.Stretch,
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1, 0, 0, 0),
            IsVisible = false,
            Child = new ScrollViewer { Content = _detailBody },
        };

        // ---- Sonoma tree (THEME-MACOS-1 structure) ----
        _sonomaHeaderSlot = new Grid();
        _sonomaSearchSlot = new Grid();
        _sonomaGridSlot = new Grid();
        _sonomaDetailSlot = new Grid();
        _sonomaStatusSlot = new StackPanel { Orientation = Orientation.Horizontal };
        _sonomaOverlaySlot = new Grid();
        _sonomaContentRow = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        _sonomaContentRow.Children.Add(_sonomaGridSlot);
        Grid.SetColumn(_sonomaDetailSlot, 1);
        _sonomaContentRow.Children.Add(_sonomaDetailSlot);
        _sonomaBody = new Grid { RowDefinitions = new RowDefinitions("Auto,*,Auto"), RowSpacing = 14 };
        _sonomaBody.Children.Add(_sonomaSearchSlot);
        Grid.SetRow(_sonomaContentRow, 1);
        _sonomaBody.Children.Add(_sonomaContentRow);
        _sonomaInner = new Grid { RowDefinitions = new RowDefinitions("*,Auto"), Margin = new Thickness(24, 18, 24, 12) };
        _sonomaInner.Children.Add(_sonomaBody);
        Grid.SetRow(_sonomaStatusSlot, 1);
        _sonomaInner.Children.Add(_sonomaStatusSlot);
        _sonomaRoot = new Grid { RowDefinitions = new RowDefinitions("Auto,*") };
        _sonomaRoot.Children.Add(_sonomaHeaderSlot);
        Grid.SetRow(_sonomaInner, 1);
        _sonomaRoot.Children.Add(_sonomaInner);
        Grid.SetRowSpan(_sonomaOverlaySlot, 2);
        _sonomaRoot.Children.Add(_sonomaOverlaySlot);

        // ---- Launchpad tree ----
        _launchpadHeaderSlot = new Grid();
        _launchpadSearchSlot = new Grid { HorizontalAlignment = HorizontalAlignment.Center };
        _launchpadGridSlot = new Grid();
        _launchpadDetailSlot = new Grid { HorizontalAlignment = HorizontalAlignment.Right };
        _launchpadStatusSlot = new StackPanel { Orientation = Orientation.Horizontal };
        _launchpadOverlaySlot = new Grid();
        _launchpadContentHost = new Grid
        {
            RowDefinitions = new RowDefinitions("*,Auto"),
            HorizontalAlignment = HorizontalAlignment.Center,
            MaxWidth = LayoutProfiles.Launchpad.ContentMaxWidth,
            Margin = new Thickness(24, 10, 24, LayoutProfiles.Launchpad.LaunchpadBottomInset),
        };
        _launchpadContentHost.Children.Add(_launchpadGridSlot);
        _launchpadContentHost.Children.Add(_launchpadDetailSlot);
        Grid.SetRow(_launchpadStatusSlot, 1);
        _launchpadContentHost.Children.Add(_launchpadStatusSlot);
        _launchpadRoot = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto,*") };
        _launchpadRoot.Children.Add(_launchpadHeaderSlot);
        Grid.SetRow(_launchpadSearchSlot, 1);
        _launchpadRoot.Children.Add(_launchpadSearchSlot);
        Grid.SetRow(_launchpadContentHost, 2);
        _launchpadRoot.Children.Add(_launchpadContentHost);
        Grid.SetRow(_launchpadOverlaySlot, 1);
        Grid.SetRowSpan(_launchpadOverlaySlot, 2);
        _launchpadRoot.Children.Add(_launchpadOverlaySlot);

        // ---- Split tree ----
        _splitListTitle = Ui.Text("书库", 12, "TextSecondary", bold: true);
        _splitBookList = new ItemsControl
        {
            Name = "SplitBookList",
            ItemsSource = ViewModel.Books,
            ItemsPanel = new FuncTemplate<Panel?>(() => new StackPanel { Spacing = 2 }),
        };
        _splitBookList.ItemTemplate = new FuncDataTemplate<BookCardItem>((item, _) => BuildSplitRow(item));
        _splitHeaderSlot = new Grid();
        _splitSearchSlot = new Grid { Margin = new Thickness(20, 14, 20, 0) };
        _splitGridSlot = new Grid();
        _splitDetailSlot = new Grid { HorizontalAlignment = HorizontalAlignment.Right };
        _splitStatusSlot = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(4, 6, 4, 2) };
        _splitOverlaySlot = new Grid();
        _splitLeft = new Border
        {
            Background = ThemePackService.Brush(ThemePackService.SidebarBackground),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(0, 0, 1, 0),
        };
        var leftGrid = new Grid { RowDefinitions = new RowDefinitions("Auto,*,Auto") };
        _splitListTitle.Margin = new Thickness(12, 10, 12, 6);
        leftGrid.Children.Add(_splitListTitle);
        var listScroll = new ScrollViewer
        {
            Content = _splitBookList,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
            Margin = new Thickness(8, 0, 8, 0),
        };
        Grid.SetRow(listScroll, 1);
        leftGrid.Children.Add(listScroll);
        Grid.SetRow(_splitStatusSlot, 2);
        leftGrid.Children.Add(_splitStatusSlot);
        _splitLeft.Child = leftGrid;
        _splitRight = new Grid { RowDefinitions = new RowDefinitions("Auto,*") };
        _splitRight.Children.Add(_splitSearchSlot);
        _splitRightBody = new Grid { Margin = new Thickness(20, 12, 20, 16) };
        _splitRightBody.Children.Add(_splitGridSlot);
        _splitRightBody.Children.Add(_splitDetailSlot);
        Grid.SetRow(_splitRightBody, 1);
        _splitRight.Children.Add(_splitRightBody);
        _splitBody = new Grid { ColumnDefinitions = new ColumnDefinitions("260,*") };
        _splitBody.Children.Add(_splitLeft);
        Grid.SetColumn(_splitRight, 1);
        _splitBody.Children.Add(_splitRight);
        _splitRoot = new Grid { RowDefinitions = new RowDefinitions("Auto,*") };
        _splitRoot.Children.Add(_splitHeaderSlot);
        Grid.SetRow(_splitBody, 1);
        _splitRoot.Children.Add(_splitBody);
        Grid.SetRow(_splitOverlaySlot, 0);
        Grid.SetRowSpan(_splitOverlaySlot, 2);
        _splitRoot.Children.Add(_splitOverlaySlot);

        if (_controller is not null)
        {
            _importPanel = new ImportPanel(_controller) { IsVisible = false };
            _importPanel.ImportCompleted += (_, _) => LastImportOperation = RefreshAfterImportAsync();
        }

        ViewModel.PropertyChanged += (_, args) =>
        {
            switch (args.PropertyName)
            {
                case nameof(BookshelfViewModel.ColumnCount):
                    GridPanel.Columns = EffectiveColumns(_layout);
                    break;
                case nameof(BookshelfViewModel.IsDetailOpen):
                    UpdateDetail();
                    break;
                case nameof(BookshelfViewModel.SelectedTag):
                    RebuildChips();
                    break;
                case nameof(BookshelfViewModel.StatusMessage):
                    _status.Text = ViewModel.StatusMessage ?? string.Empty;
                    break;
            }
        };
        ViewModel.BooksChanged += (_, _) =>
        {
            _emptyPanel.IsVisible = ViewModel.IsEmpty;
            _noResultsPanel.IsVisible = ViewModel.HasNoResults;
            if (!string.IsNullOrEmpty(ViewModel.StatusMessage))
            {
                _status.Text = ViewModel.StatusMessage!;
            }
        };
        ApplyLayout(LayoutProfiles.Sonoma);
    }

    public BookshelfViewModel ViewModel { get; }

    public TextBox SearchBox { get; }

    public ItemsControl TagChips { get; }

    public ItemsControl BookGrid { get; }

    public UniformGrid GridPanel { get; }

    public Border DetailPanel => _detailPanel;

    public StackPanel EmptyPanel => _emptyPanel;

    public StackPanel NoResultsPanel => _noResultsPanel;

    public Border Header => _header;

    public Button? NewBookButton => this.FindControl<Button>("NewBookButton");

    /// <summary>IMPORT-EXPORT-UI-1 AC1: header entries.</summary>
    public Button ImportFilesButton => _importFilesButton;

    public Button ImportFolderButton => _importFolderButton;

    public ImportPanel? ImportPanelControl => _importPanel;

    /// <summary>IMPORT-EXPORT-UI-1: last page-level status line (picker/refresh feedback).</summary>
    public string StatusLine => _status.Text ?? string.Empty;

    /// <summary>THEME-MACOS-LAYOUTS-1: the Split layout's left-hand book list.</summary>
    public ItemsControl SplitBookList => _splitBookList;

    /// <summary>THEME-MACOS-LAYOUTS-1: layout profile currently applied to this page.</summary>
    public LayoutProfile Layout => _layout;

    public LayoutKind CurrentLayout => _layout.Kind;

    /// <summary>Last import flow (tests await this; the picker itself is faked headless).</summary>
    public Task LastImportOperation { get; private set; } = Task.CompletedTask;

    /// <summary>
    /// THEME-MACOS-LAYOUTS-1: switches this page between the three frozen shelf structures. The public
    /// members above stay valid in every layout because the same control instances are re-parented.
    /// </summary>
    public void ApplyLayout(LayoutProfile profile)
    {
        _layout = profile;
        DetachSharedControls();
        switch (profile.Shelf)
        {
            case ShelfStyle.LaunchpadGrid:
                AttachLaunchpad(profile);
                break;
            case ShelfStyle.SplitList:
                AttachSplit(profile);
                break;
            default:
                AttachSonoma();
                break;
        }

        ApplyShelfChrome(profile);
        GridPanel.Columns = EffectiveColumns(profile);
        // Cards are sized per layout (168x220 in Launchpad), so rebuild the item template once.
        BookGrid.ItemTemplate = new FuncDataTemplate<BookCardItem>((item, _) => BuildCard(item));
        ApplyTheme();
        InvalidateMeasure();
        InvalidateVisual();
    }

    public void ApplyTheme()
    {
        _sonomaRoot.Background = ThemePackService.Brush("AppBg");
        _launchpadRoot.Background = ThemePackService.Brush("AppBg");
        _splitRoot.Background = ThemePackService.Brush("AppBg");
        _searchCard.Background = ThemePackService.Brush("CardBg");
        _searchCard.BorderBrush = ThemePackService.Brush("CardBorder");
        _detailPanel.Background = ThemePackService.Brush("CardBg");
        _detailPanel.BorderBrush = ThemePackService.Brush("CardBorder");
        _splitLeft.Background = ThemePackService.Brush(ThemePackService.SidebarBackground);
        _splitLeft.BorderBrush = ThemePackService.Brush("CardBorder");
        _splitListTitle.Foreground = ThemePackService.Brush("TextSecondary");
        RebuildChips();
        ApplyShelfChrome(_layout);
    }

    private void AttachSonoma()
    {
        _sonomaHeaderSlot.Children.Add(_header);
        _sonomaSearchSlot.Children.Add(_searchCard);
        _sonomaGridSlot.Children.Add(_contentGrid);
        _sonomaDetailSlot.Children.Add(_detailPanel);
        _sonomaStatusSlot.Children.Add(_statusRow);
        if (_importPanel is not null)
        {
            _sonomaOverlaySlot.Children.Add(_importPanel);
        }

        Content = _sonomaRoot;
    }

    private void AttachLaunchpad(LayoutProfile profile)
    {
        _launchpadContentHost.MaxWidth = profile.ContentMaxWidth;
        // The shell reserves the Dock band on PageHost (MainWindow.ApplyLayout), so the page itself only
        // needs its normal content margin; the bottom inset stays in the profile for the shell.
        _launchpadContentHost.Margin = new Thickness(24, 10, 24, 16);
        _launchpadHeaderSlot.Children.Add(_header);
        _launchpadSearchSlot.Children.Add(_searchCard);
        _launchpadGridSlot.Children.Add(_contentGrid);
        _launchpadDetailSlot.Children.Add(_detailPanel);
        _launchpadStatusSlot.Children.Add(_statusRow);
        if (_importPanel is not null)
        {
            _launchpadOverlaySlot.Children.Add(_importPanel);
        }

        Content = _launchpadRoot;
    }

    private void AttachSplit(LayoutProfile profile)
    {
        _splitBody.ColumnDefinitions[0].Width = new GridLength(profile.ShelfListWidth > 0 ? profile.ShelfListWidth : 260);
        _splitHeaderSlot.Children.Add(_header);
        _splitSearchSlot.Children.Add(_searchCard);
        _splitGridSlot.Children.Add(_contentGrid);
        _splitDetailSlot.Children.Add(_detailPanel);
        _splitStatusSlot.Children.Add(_statusRow);
        if (_importPanel is not null)
        {
            _splitOverlaySlot.Children.Add(_importPanel);
        }

        Content = _splitRoot;
    }

    /// <summary>Removes every shared block from whatever slot currently owns it (one parent per control).</summary>
    private void DetachSharedControls()
    {
        Detach(_header);
        Detach(_searchCard);
        Detach(_contentGrid);
        Detach(_detailPanel);
        Detach(_statusRow);
        if (_importPanel is not null)
        {
            Detach(_importPanel);
        }
    }

    private static void Detach(Control control)
    {
        if (control.Parent is Panel panel)
        {
            panel.Children.Remove(control);
        }
    }

    /// <summary>Per-layout geometry / copy / chrome for the shared header, search card and detail panel.</summary>
    private void ApplyShelfChrome(LayoutProfile profile)
    {
        var launchpad = profile.Shelf == ShelfStyle.LaunchpadGrid;
        var split = profile.Shelf == ShelfStyle.SplitList;

        ApplyHeaderChrome(profile);        _header.Padding = launchpad
            ? new Thickness(24, 12, 24, 6)
            : split ? new Thickness(24, 12, 24, 8) : new Thickness(28, 18);
        _headerTitle.FontSize = launchpad || split ? 18 : 26;
        _headerSubtitle.FontSize = split ? 11 : 12;
        _headerSubtitle.Text = launchpad
            ? "Launchpad 网格 · 168×220 卡片 · 底部 Dock"
            : split
                ? "Finder 分栏 · 左栏书列表 · 右侧网格/详情"
                : "Saber-informed shell · 顶部渐变 / 1400 居中 / 3:4 书卡";

        _searchCard.MaxWidth = launchpad ? 900 : double.PositiveInfinity;
        _searchCard.HorizontalAlignment = launchpad ? HorizontalAlignment.Center : HorizontalAlignment.Stretch;

        if (launchpad)
        {
            _detailPanel.Width = 420;
            _detailPanel.BorderThickness = new Thickness(1);
            _detailPanel.CornerRadius = new CornerRadius(16);
            _detailPanel.Padding = new Thickness(20);
        }
        else if (split)
        {
            _detailPanel.Width = 340;
            _detailPanel.BorderThickness = new Thickness(1, 0, 0, 0);
            _detailPanel.CornerRadius = new CornerRadius(0);
            _detailPanel.Padding = new Thickness(18);
        }
        else
        {
            _detailPanel.Width = 360;
            _detailPanel.BorderThickness = new Thickness(1, 0, 0, 0);
            _detailPanel.CornerRadius = new CornerRadius(0);
            _detailPanel.Padding = new Thickness(20);
        }
    }

    /// <summary>Header surface per layout: gradient (Sonoma), transparent (Launchpad), translucent strip (Split).</summary>
    private void ApplyHeaderChrome(LayoutProfile profile)
    {
        _header.Background = profile.Shelf == ShelfStyle.LaunchpadGrid
            ? Brushes.Transparent
            : profile.Shelf == ShelfStyle.SplitList
                ? ThemePackService.Brush("HeaderBg")
                : ThemePackService.Brush("HeaderGradient");
    }

    /// <summary>Columns per layout: Sonoma keeps the ViewModel's 1400-wide calculation, the other two are fixed.</summary>
    private int EffectiveColumns(LayoutProfile profile) => profile.Shelf switch
    {
        // 1200-wide centred Launchpad grid with 168px cards (+16 gap) => 6 columns.
        ShelfStyle.LaunchpadGrid => Math.Clamp(
            (int)Math.Floor((profile.ContentMaxWidth - 48 + BookshelfViewModel.CardGap) / (profile.LaunchpadCardWidth + BookshelfViewModel.CardGap)),
            2,
            8),
        // Right-hand grid of the split view: the 1280-wide default window minus the 260px list column.
        ShelfStyle.SplitList => BookshelfViewModel.ComputeColumns(Math.Max(480, 1280 - profile.ShelfListWidth - 48)),
        _ => ViewModel.ColumnCount,
    };

    private void RebuildChips()
    {
        TagChips.ItemsSource = null;
        TagChips.ItemsSource = ViewModel.Tags;
        RebuildChipsTemplate();
    }

    private void RebuildChipsTemplate()
    {
        TagChips.ItemTemplate = new FuncDataTemplate<string>((tag, _) =>
        {
            var active = string.Equals(tag, ViewModel.SelectedTag, StringComparison.Ordinal);
            var chip = new Button
            {
                Content = tag,
                Margin = new Thickness(0, 0, 8, 0),
                Padding = new Thickness(12, 5),
                CornerRadius = new CornerRadius(14),
                FontSize = 12,
                Background = ThemePackService.Brush(active ? "ChipActiveBg" : "ChipBg"),
                Foreground = ThemePackService.Brush(active ? "AccentText" : "TextSecondary"),
            };
            chip.Click += (_, _) => ViewModel.SelectedTag = tag;
            return chip;
        });
    }

    private static StackPanel BuildState(string title, string hint)
    {
        var panel = new StackPanel
        {
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            IsVisible = false,
            Margin = new Thickness(0, 40, 0, 40),
        };
        panel.Children.Add(Ui.Text(title, 18, "TextPrimary", bold: true));
        panel.Children.Add(Ui.Text(hint, 12, "TextSecondary"));
        return panel;
    }

    /// <summary>One book row of the Split layout's left list (cover thumb + title + tag).</summary>
    private Control BuildSplitRow(BookCardItem item)
    {
        var cover = new Border
        {
            Width = 38,
            Height = 52,
            CornerRadius = new CornerRadius(6),
            Background = ThemePackService.Brush("ChipBg"),
            Child = new TextBlock
            {
                Text = item.Glyph,
                FontSize = 18,
                FontWeight = FontWeight.SemiBold,
                Foreground = ThemePackService.Brush("Accent"),
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            },
        };
        var text = new StackPanel
        {
            Spacing = 2,
            VerticalAlignment = VerticalAlignment.Center,
            Children =
            {
                new TextBlock
                {
                    Text = item.Title,
                    FontSize = 12,
                    FontWeight = FontWeight.SemiBold,
                    Foreground = ThemePackService.Brush("TextPrimary"),
                    TextTrimming = TextTrimming.CharacterEllipsis,
                },
                Ui.Text(item.Tag, 11, "TextSecondary"),
            },
        };
        var row = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,*"), ColumnSpacing = 10 };
        row.Children.Add(cover);
        Grid.SetColumn(text, 1);
        row.Children.Add(text);
        var button = new Button
        {
            Content = row,
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Stretch,
            Padding = new Thickness(10, 7),
            CornerRadius = new CornerRadius(8),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        button.Click += (_, _) => ViewModel.OpenDetails(item);
        button.DoubleTapped += (_, args) =>
        {
            args.Handled = true;
            RequestOpenReader(item);
        };
        return button;
    }

    private Control BuildCard(BookCardItem item)
    {
        var launchpad = _layout.Shelf == ShelfStyle.LaunchpadGrid;
        var cardWidth = launchpad ? _layout.LaunchpadCardWidth : BookshelfViewModel.CardWidth;
        // Launchpad cards are the frozen 168x220 icon tiles: the cover takes the remaining height and the
        // Border keeps the fixed tile height so the uniform grid cells never stretch the card.
        var coverHeight = launchpad ? Math.Max(140, _layout.LaunchpadCardHeight - 70) : 226;
        var cover = new Border
        {
            Height = coverHeight,
            CornerRadius = new CornerRadius(launchpad ? 14 : 10),
            Background = ThemePackService.Brush("ChipBg"),
            Child = new TextBlock
            {
                Text = item.Glyph,
                FontSize = launchpad ? 52 : 44,
                FontWeight = FontWeight.SemiBold,
                Foreground = ThemePackService.Brush("Accent"),
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            },
        };
        var hint = Ui.Text("查看详情", 11, "AccentText");
        hint.Classes.Add("nm-hint");
        hint.Opacity = 0;
        hint.HorizontalAlignment = HorizontalAlignment.Center;
        var overlay = new Border
        {
            Background = new ImmutableSolidColorBrush(Color.Parse("#73000000")),
            CornerRadius = new CornerRadius(0, 0, launchpad ? 14 : 10, launchpad ? 14 : 10),
            Padding = new Thickness(6),
            VerticalAlignment = VerticalAlignment.Bottom,
            Child = hint,
        };
        var coverHost = new Grid();
        coverHost.Children.Add(cover);
        coverHost.Children.Add(overlay);

        var text = new StackPanel { Spacing = 2, Margin = new Thickness(2, 8, 2, 0) };
        text.Children.Add(new TextBlock
        {
            Text = item.Title,
            FontSize = 13,
            FontWeight = FontWeight.SemiBold,
            Foreground = ThemePackService.Brush("TextPrimary"),
            TextTrimming = TextTrimming.CharacterEllipsis,
        });
        text.Children.Add(Ui.Text(item.Meta, 11, "TextSecondary"));

        var card = new Border
        {
            Width = cardWidth,
            Height = launchpad ? _layout.LaunchpadCardHeight : double.NaN,
            VerticalAlignment = launchpad ? VerticalAlignment.Top : VerticalAlignment.Stretch,
            Margin = new Thickness(0, 0, BookshelfViewModel.CardGap, BookshelfViewModel.CardGap),
            CornerRadius = new CornerRadius(launchpad ? 16 : 12),
            Padding = new Thickness(launchpad ? 10 : 8),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
            Child = new StackPanel { Children = { coverHost, text } },
        };
        card.Classes.Add("nm-bookcard");
        card.PointerPressed += (_, _) => ViewModel.OpenDetails(item);
        // CHAPTER-SELECTOR-1 AC2: double-click a card opens the reader on THAT book (single click
        // still opens the detail panel).
        card.DoubleTapped += (_, args) =>
        {
            args.Handled = true;
            RequestOpenReader(item);
        };
        return card;
    }

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC2: raised when the user opens the reader from a book card (double-click)
    /// or from the detail panel. The window loads that book id instead of the first library book.
    /// </summary>
    public event EventHandler<BookCardItem>? OpenReaderRequested;

    /// <summary>CHAPTER-SELECTOR-1 AC2: last book the user asked to open (tests/evidence).</summary>
    public BookCardItem? LastOpenReaderRequest { get; private set; }

    /// <summary>CHAPTER-SELECTOR-1 AC2: request the reader for one book (card double-click / panel).</summary>
    public void RequestOpenReader(BookCardItem? item)
    {
        if (item is null)
        {
            return;
        }

        LastOpenReaderRequest = item;
        OpenReaderRequested?.Invoke(this, item);
    }

    private void UpdateDetail()
    {
        _detailBody.Children.Clear();
        _detailPanel.IsVisible = ViewModel.IsDetailOpen;
        if (ViewModel.SelectedBook is not { } book)
        {
            return;
        }

        _detailBody.Children.Add(Ui.Text("查看详情", 12, "TextSecondary"));
        _detailBody.Children.Add(Ui.Text(book.Title, 20, "TextPrimary", bold: true));
        if (!string.IsNullOrEmpty(book.OriginalTitle))
        {
            _detailBody.Children.Add(Ui.Text(book.OriginalTitle, 12, "TextSecondary"));
        }

        _detailBody.Children.Add(Ui.Text($"{book.Meta} · 标签：{book.Tag}", 12, "TextSecondary"));
        _detailBody.Children.Add(Ui.Text("ID：" + book.BookId, 11, "TextSecondary"));
        _detailBody.Children.Add(new TextBox { Watermark = "新书名（示例：雾港来信・日本語テスト）", Name = "NewTitleBox" });
        var actions = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        actions.Children.Add(Ui.Action("关闭", ViewModel.CloseDetails));
        // CHAPTER-SELECTOR-1 AC2: explicit reader entry for this book (in addition to double-click).
        var openReader = Ui.Action("进入阅读", () => RequestOpenReader(book), primary: true);
        openReader.Name = "OpenReaderFromDetail";
        actions.Children.Add(openReader);
        actions.Children.Add(Ui.Action("新建", () => OpenNewDialog(), primary: false));
        _detailBody.Children.Add(actions);
    }

    private async Task BeginImportAsync(ImportSourceKind kind)
    {
        if (_importPanel is null)
        {
            _status.Text = "Host 未接线：导入不可用";
            return;
        }

        if (_picker is null)
        {
            _status.Text = "系统文件选择器不可用：导入不可用";
            return;
        }

        try
        {
            IReadOnlyList<string> paths = kind == ImportSourceKind.Folder
                ? (await _picker.PickFolderAsync() is { } folder ? new[] { folder } : Array.Empty<string>())
                : await _picker.PickFilesAsync();
            if (paths.Count == 0)
            {
                _status.Text = "未选择文件";
                return;
            }

            await _importPanel.OpenAsync(kind, paths);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
            _status.Text = "系统文件选择器不可用：导入不可用";
        }
    }

    private async Task RefreshAfterImportAsync()
    {
        await ViewModel.RefreshAsync();
        if (!string.IsNullOrEmpty(ViewModel.StatusMessage))
        {
            _status.Text = ViewModel.StatusMessage;
        }
    }

    private void OpenNewDialog()
    {
        var title = "雾港来信・日本語テスト";
        var stack = new StackPanel { Spacing = 8 };
        stack.Children.Add(Ui.Text("新建书（写入经 Core command dispatcher）", 12, "TextSecondary"));
        var box = new TextBox { Text = title, Name = "CreateBookTitle" };
        stack.Children.Add(box);
        var create = Ui.Action("创建", async () =>
        {
            await ViewModel.CreateBookAsync(box.Text ?? string.Empty);
            UpdateDetail();
        }, primary: true);
        stack.Children.Add(create);
        _detailBody.Children.Clear();
        _detailBody.Children.Add(stack);
        _detailPanel.IsVisible = true;
    }
}

/// <summary>
/// AC4 settings skeleton.
/// THEME-MACOS-LAYOUTS-1: three settings structures (two-column / single centred column / split
/// directory) share the same card instances, the same theme centre and the same Host seams. The cards are
/// re-parented between layouts; inside the Split layout switching sections only toggles visibility, so no
/// section control is ever recreated.
/// </summary>
public sealed class SettingsPage : UserControl
{
    private readonly StackPanel _themeList;
    private readonly TextBlock _wired;
    private readonly TextBlock _settingsJson;
    private readonly StackPanel _nsList;
    private readonly Action _onThemeApplied;
    private readonly TextBlock _title;

    // THEME-MACOS-1: theme card geometry comes from the active pack's Metrics (old packs = corner 12, no
    // shadow; macOS = corner 14 + soft card shadow) and the appearance row toggles Light/Dark.
    private readonly Border _themeCard;
    private readonly StackPanel _appearanceRow;
    private readonly Button _lightVariantButton;
    private readonly Button _darkVariantButton;
    private readonly List<(ThemePack Pack, Button Button)> _themeButtons = new();

    // Section cards: one instance each, re-parented per layout (never rebuilt).
    private readonly Border _credentialCard;
    private readonly Border _providerCard;
    private readonly Border _networkCard;
    private readonly Border _bindingsCard;
    private readonly Border _deviceCard;
    private readonly Border _dataCard;
    private readonly Border _nsCard;

    // Sonoma tree (THEME-MACOS-1 two-column settings).
    private readonly Grid _sonomaRoot;
    private readonly Grid _sonomaContent;
    private readonly Grid _sonomaThemeSlot;
    private readonly StackPanel _sonomaRightSlot;

    // Launchpad tree (single centred column, max width from the profile).
    private readonly Grid _launchpadRoot;
    private readonly Grid _launchpadColumnHost;
    private readonly StackPanel _launchpadStack;

    // Split tree (section directory + one visible section panel).
    private readonly Grid _splitRoot;
    private readonly Grid _splitBody;
    private readonly Border _splitNavBorder;
    private readonly StackPanel _splitNav;
    private readonly StackPanel _splitPages;
    private readonly Dictionary<string, StackPanel> _splitSectionPanels = new(StringComparer.Ordinal);
    private readonly List<(string Key, string Label, Button Button)> _splitSectionButtons = new();

    private LayoutProfile _layout = LayoutProfiles.Sonoma;
    private string _splitSection = SplitSectionTheme;

    private const string SplitSectionTheme = "theme";
    private const string SplitSectionCredentials = "credentials";
    private const string SplitSectionProvider = "provider";
    private const string SplitSectionNetwork = "network";
    private const string SplitSectionBindings = "bindings";
    private const string SplitSectionRegistry = "registry";

    public SettingsPage(SettingsViewModel viewModel, Action onThemeApplied, IHostController? controller = null)
    {
        ViewModel = viewModel;
        _onThemeApplied = onThemeApplied;
        Name = "SettingsPage";

        _title = Ui.Text("设置", 26, "TextPrimary", bold: true);
        _wired = Ui.Text(viewModel.WiredSummary, 12, "TextSecondary");

        _themeCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(ThemePackService.Current.Metrics.CornerCard),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        _themeList = new StackPanel { Spacing = 8 };
        _themeList.Children.Add(Ui.Text("主题中心 · ThemePack", 13, "TextPrimary", bold: true));
        ThemeList = new ItemsControl { ItemsSource = viewModel.ThemePacks, ItemsPanel = new FuncTemplate<Panel?>(() => new StackPanel()) };
        ThemeList.ItemTemplate = new FuncDataTemplate<ThemePack>((pack, _) =>
        {
            var button = new Button
            {
                Content = pack.Label + (pack.Id == ThemePacks.Default.Id ? "（默认）" : string.Empty),
                HorizontalAlignment = HorizontalAlignment.Stretch,
                HorizontalContentAlignment = HorizontalAlignment.Left,
                Padding = new Thickness(10, 6),
                CornerRadius = new CornerRadius(pack.Metrics.CornerButton),
                Background = pack.Id == ThemePackService.Current.Id ? ThemePackService.Brush("ChipActiveBg") : ThemePackService.Brush("ChipBg"),
                Foreground = pack.Id == ThemePackService.Current.Id ? ThemePackService.Brush("AccentText") : ThemePackService.Brush("TextPrimary"),
            };
            button.Name = "ThemePack_" + pack.Id;
            button.Click += (_, _) => SelectTheme(pack);
            // THEME-MACOS-LAYOUTS-1: re-parenting the theme card into another layout tree may make the
            // ItemsControl regenerate its containers, which re-runs this factory. Keep one entry per pack
            // so ThemeButtons never accumulates duplicates across layout switches.
            _themeButtons.RemoveAll(entry => string.Equals(entry.Pack.Id, pack.Id, StringComparison.Ordinal));
            _themeButtons.Add((pack, button));
            return button;
        });
        _themeList.Children.Add(ThemeList);

        // THEME-MACOS-1: minimal「外观：浅色 / 深色」row; visible only for packs that carry both token sets.
        _appearanceRow = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Margin = new Thickness(0, 6, 0, 0),
            IsVisible = false,
        };
        _appearanceRow.Children.Add(new TextBlock
        {
            Text = "外观",
            FontSize = 12,
            VerticalAlignment = VerticalAlignment.Center,
            Foreground = ThemePackService.Brush("TextSecondary"),
        });
        _lightVariantButton = CreateVariantButton("浅色");
        _darkVariantButton = CreateVariantButton("深色");
        _lightVariantButton.Click += (_, _) => SwitchVariant(Avalonia.Styling.ThemeVariant.Light);
        _darkVariantButton.Click += (_, _) => SwitchVariant(Avalonia.Styling.ThemeVariant.Dark);
        _appearanceRow.Children.Add(_lightVariantButton);
        _appearanceRow.Children.Add(_darkVariantButton);
        _themeList.Children.Add(_appearanceRow);
        _themeCard.Child = _themeList;

        _settingsJson = Ui.Text(viewModel.SettingsJson, 11, "TextSecondary");
        var dataBody = new StackPanel();
        dataBody.Children.Add(Ui.Text("已接线 settings 命令 · 展示", 13, "TextPrimary", bold: true));
        dataBody.Children.Add(_settingsJson);
        _dataCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
            Child = dataBody,
        };

        // GPU-ORT-PROBE-1: packaged device probe (ONNX Runtime EP list recorded in VERSION.json).
        DeviceStatus = Services.DeviceStatus.Load();
        DeviceStatusText = Ui.Text(
            DeviceStatus?.DisplayText ?? "GPU：未打包探测（开发运行）",
            11,
            DeviceStatus?.Available == true ? "TextPrimary" : "TextSecondary");
        var deviceBody = new StackPanel();
        deviceBody.Children.Add(Ui.Text("运行环境 · GPU", 13, "TextPrimary", bold: true));
        deviceBody.Children.Add(DeviceStatusText);
        deviceBody.Children.Add(Ui.Text(
            "探测源：ONNX Runtime 执行提供程序（打包时写入 VERSION.json）",
            11,
            "TextSecondary"));
        _deviceCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
            Child = deviceBody,
        };

        _nsList = new StackPanel { Spacing = 4 };
        _nsList.Children.Add(Ui.Text("S2 NOT_SUPPORTED 批次登记（S3-A/B/C 已由 NS-WIRE-A1 接线）", 13, "TextPrimary", bold: true));
        foreach (var item in viewModel.NsBatch)
        {
            _nsList.Children.Add(Ui.Text($"[{item.Status}] {item.Command} · {item.Page}", 11, "TextSecondary"));
        }

        _nsCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
            Child = _nsList,
        };

        // CREDENTIAL-UI-1: settings-page credential block (masked input → credential_put/clear).
        // It is injected with the Host controller seam: production passes HostController; tests pass a
        // scripted fake; the XAML designer path (controller == null) renders a typed "Host 未就绪" stub.
        Credentials = new CredentialSection(
            controller is null
                ? _ => Task.FromResult<IReadOnlyList<CredentialTargetOption>>(Array.Empty<CredentialTargetOption>())
                : controller.ListCredentialTargetsAsync,
            controller is null
                ? (_, _, _, _, _) => Task.FromResult(CredentialOperationResult.NotReady())
                : controller.PutCredentialAsync,
            controller is null
                ? (_, _, _) => Task.FromResult(CredentialOperationResult.NotReady())
                : controller.ClearCredentialAsync);
        _credentialCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
            Child = Credentials,
        };

        // SETTINGS-PROFILE-UI-1: provider / network profile management + binding slots. Same controller
        // seam as the credential block; the designer path (controller == null) shows typed empty states.
        ProviderProfiles = new ProviderProfileSection(
            controller is null
                ? _ => Task.FromResult<IReadOnlyList<ProviderProfileInfo>>(Array.Empty<ProviderProfileInfo>())
                : controller.ListProviderProfilesAsync,
            controller is null
                ? _ => Task.FromResult<IReadOnlyList<NetworkProfileInfo>>(Array.Empty<NetworkProfileInfo>())
                : controller.ListNetworkProfilesAsync,
            controller is null
                ? (_, _, _) => Task.FromResult(SettingsProfileResult.NotReady())
                : controller.SaveProviderProfileAsync,
            controller is null
                ? (_, _) => Task.FromResult(SettingsProfileResult.NotReady())
                : controller.DeleteProviderProfileAsync);
        NetworkProfiles = new NetworkProfileSection(
            controller is null
                ? _ => Task.FromResult<IReadOnlyList<NetworkProfileInfo>>(Array.Empty<NetworkProfileInfo>())
                : controller.ListNetworkProfilesAsync,
            controller is null
                ? _ => Task.FromResult<IReadOnlyList<ProviderProfileInfo>>(Array.Empty<ProviderProfileInfo>())
                : controller.ListProviderProfilesAsync,
            controller is null
                ? (_, _, _) => Task.FromResult(SettingsProfileResult.NotReady())
                : controller.SaveNetworkProfileAsync,
            controller is null
                ? (_, _) => Task.FromResult(SettingsProfileResult.NotReady())
                : controller.DeleteNetworkProfileAsync,
            controller is null
                ? (_, _) => Task.FromResult(SettingsProfileResult.NotReady())
                : controller.SetNetworkDefaultAsync,
            controller is null
                ? (_, _, _) => Task.FromResult<NetworkTestInfo?>(null)
                : controller.TestNetworkProfileAsync,
            controller is null
                ? (_, _) => Task.FromResult<NetworkResolveInfo?>(null)
                : controller.ResolveNetworkProfileAsync);
        // READER-SELECTOR-UI-1: real library reads for the book/chapter selectors.
        Func<CancellationToken, Task<IReadOnlyList<BookSummary>>> listBooks = controller is null
            ? _ => Task.FromResult<IReadOnlyList<BookSummary>>(Array.Empty<BookSummary>())
            : async cancellationToken =>
            {
                await controller.RefreshBooksAsync(cancellationToken);
                return controller.Snapshot.Books;
            };
        Func<string, CancellationToken, Task<IReadOnlyList<ChapterSummary>>> listChapters = controller is null
            ? (_, _) => Task.FromResult<IReadOnlyList<ChapterSummary>>(Array.Empty<ChapterSummary>())
            : controller.ListChaptersAsync;
        Bindings = new ProviderBindingsSection(
            controller is null
                ? _ => Task.FromResult<IReadOnlyList<ProviderProfileInfo>>(Array.Empty<ProviderProfileInfo>())
                : controller.ListProviderProfilesAsync,
            listBooks,
            listChapters,
            controller is null
                ? (_, _, _, _) => Task.FromResult(SettingsProfileResult.NotReady())
                : controller.SetProviderBindingAsync,
            controller is null
                ? (_, _, _) => Task.FromResult(SettingsProfileResult.NotReady())
                : controller.ClearProviderBindingAsync,
            controller is null
                ? (_, _) => Task.FromResult<ProviderBindingResult?>(null)
                : controller.ResolveProviderBindingAsync);
        _providerCard = ProfileUi.Card(ProviderProfiles);
        _networkCard = ProfileUi.Card(NetworkProfiles);
        _bindingsCard = ProfileUi.Card(Bindings);

        // ---- Sonoma tree: 320px theme card + scrolling card column ----
        _sonomaThemeSlot = new Grid();
        _sonomaRightSlot = new StackPanel { Spacing = 12 };
        _sonomaContent = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("320,*"),
            ColumnSpacing = 18,
            Margin = new Thickness(0, 12, 0, 0),
        };
        _sonomaThemeSlot.Children.Add(_themeCard);
        _sonomaContent.Children.Add(_sonomaThemeSlot);
        Grid.SetColumn(_sonomaRightSlot, 1);
        _sonomaContent.Children.Add(_sonomaRightSlot);
        var sonomaScroll = new ScrollViewer
        {
            Content = _sonomaContent,
            HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Auto,
        };
        Grid.SetRow(sonomaScroll, 2);
        _sonomaRoot = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto,*,Auto"), Margin = new Thickness(28, 18) };
        _sonomaRoot.Children.Add(sonomaScroll);

        // ---- Launchpad tree: one centred column (max width from the profile) ----
        _launchpadStack = new StackPanel { Spacing = 14 };
        _launchpadColumnHost = new Grid
        {
            MaxWidth = LayoutProfiles.Launchpad.SettingsMaxWidth,
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 14, 0, 28),
        };
        _launchpadColumnHost.Children.Add(_launchpadStack);
        var launchpadScroll = new ScrollViewer
        {
            Content = _launchpadColumnHost,
            HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Auto,
        };
        Grid.SetRow(launchpadScroll, 2);
        _launchpadRoot = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto,*,Auto"), Margin = new Thickness(28, 18) };
        _launchpadRoot.Children.Add(launchpadScroll);

        // ---- Split tree: section directory + one visible section panel ----
        _splitNav = new StackPanel { Spacing = 4, Margin = new Thickness(10, 14, 10, 0) };
        foreach (var (key, label) in new[]
                 {
                     (SplitSectionTheme, "主题"),
                     (SplitSectionCredentials, "凭证"),
                     (SplitSectionProvider, "Provider"),
                     (SplitSectionNetwork, "网络"),
                     (SplitSectionBindings, "绑定"),
                     (SplitSectionRegistry, "登记"),
                 })
        {
            var button = new Button
            {
                Content = label,
                HorizontalAlignment = HorizontalAlignment.Stretch,
                HorizontalContentAlignment = HorizontalAlignment.Left,
                Padding = new Thickness(12, 8),
                CornerRadius = new CornerRadius(8),
                FontSize = 13,
                Background = ThemePackService.Brush("ChipBg"),
                Foreground = ThemePackService.Brush("TextPrimary"),
            };
            button.Name = "SettingsSection_" + key;
            button.Click += (_, _) => SelectSplitSection(key);
            _splitSectionButtons.Add((key, label, button));
            _splitNav.Children.Add(button);
        }

        _splitNavBorder = new Border
        {
            Background = ThemePackService.Brush(ThemePackService.SidebarBackground),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(0, 0, 1, 0),
            Child = _splitNav,
        };
        _splitPages = new StackPanel { Spacing = 0 };
        foreach (var (key, _) in new[]
                 {
                     (SplitSectionTheme, "主题"),
                     (SplitSectionCredentials, "凭证"),
                     (SplitSectionProvider, "Provider"),
                     (SplitSectionNetwork, "网络"),
                     (SplitSectionBindings, "绑定"),
                     (SplitSectionRegistry, "登记"),
                 })
        {
            var panel = new StackPanel { Spacing = 14, IsVisible = key == SplitSectionTheme };
            _splitSectionPanels[key] = panel;
            _splitPages.Children.Add(panel);
        }

        var splitContentScroll = new ScrollViewer
        {
            Content = _splitPages,
            HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Auto,
            Margin = new Thickness(20, 14, 20, 20),
        };
        _splitBody = new Grid { ColumnDefinitions = new ColumnDefinitions("240,*") };
        _splitBody.Children.Add(_splitNavBorder);
        Grid.SetColumn(splitContentScroll, 1);
        _splitBody.Children.Add(splitContentScroll);
        Grid.SetRow(_splitBody, 2);
        _splitRoot = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto,*,Auto"), Margin = new Thickness(24, 16, 24, 16) };
        _splitRoot.Children.Add(_splitBody);

        ApplyLayout(LayoutProfiles.Sonoma);
    }

    public SettingsViewModel ViewModel { get; }

    public ItemsControl ThemeList { get; }

    public StackPanel NsList => _nsList;

    /// <summary>CREDENTIAL-UI-1: credential block (target list + masked input + put/clear).</summary>
    public CredentialSection Credentials { get; }

    /// <summary>CREDENTIAL-UI-1: reload targets + configured/missing states from the Host.</summary>
    public Task RefreshCredentialsAsync() => Credentials.RefreshAsync();

    /// <summary>CREDENTIAL-UI-1 AC3: drop the masked plaintext (window close / leaving settings).</summary>
    public void ClearCredentialSecrets() => Credentials.ClearSecrets();

    /// <summary>SETTINGS-PROFILE-UI-1: provider profile management card.</summary>
    public ProviderProfileSection ProviderProfiles { get; }

    /// <summary>SETTINGS-PROFILE-UI-1: network profile management card (CRUD + test/resolve/default).</summary>
    public NetworkProfileSection NetworkProfiles { get; }

    /// <summary>SETTINGS-PROFILE-UI-1: provider binding slot card.</summary>
    public ProviderBindingsSection Bindings { get; }

    /// <summary>SETTINGS-PROFILE-UI-1: reload provider/network profiles and binding targets.</summary>
    public async Task RefreshProfilesAsync()
    {
        await ProviderProfiles.RefreshAsync();
        await NetworkProfiles.RefreshAsync();
        await Bindings.RefreshAsync();
    }

    /// <summary>GPU-ORT-PROBE-1: packaged device probe (null in a dev run).</summary>
    public DeviceStatusInfo? DeviceStatus { get; }

    public TextBlock DeviceStatusText { get; }

    public List<(ThemePack Pack, Button Button)> ThemeButtons => _themeButtons;

    /// <summary>THEME-MACOS-1: theme card border (reads the active pack's Metrics).</summary>
    public Border ThemeCard => _themeCard;

    /// <summary>THEME-MACOS-1:「外观：浅色 / 深色」row (visible only for a dual-variant pack).</summary>
    public StackPanel AppearanceRow => _appearanceRow;

    public Button LightVariantButton => _lightVariantButton;

    public Button DarkVariantButton => _darkVariantButton;

    /// <summary>THEME-MACOS-LAYOUTS-1: layout profile currently applied to this page.</summary>
    public LayoutProfile Layout => _layout;

    public LayoutKind CurrentLayout => _layout.Kind;

    /// <summary>THEME-MACOS-LAYOUTS-1: Split layout section buttons (主题/凭证/Provider/网络/绑定/登记).</summary>
    public IReadOnlyList<Button> SplitSectionButtons => _splitSectionButtons.Select(entry => entry.Button).ToList();

    /// <summary>THEME-MACOS-LAYOUTS-1: Split layout section currently shown.</summary>
    public string SelectedSplitSection => _splitSection;

    public IReadOnlyDictionary<string, StackPanel> SplitSections => _splitSectionPanels;

    public void UpdateSettingsJson(System.Text.Json.JsonElement value)
    {
        ViewModel.UpdateSettingsJson(value);
        _settingsJson.Text = ViewModel.SettingsJson;
    }

    /// <summary>THEME-MACOS-1 AC1: applies one theme pack (same path as clicking its list button).</summary>
    public void SelectTheme(ThemePack pack)
    {
        if (Application.Current is { } app)
        {
            ThemePackService.Apply(app, pack);
            ViewModel.SelectedPack = pack;
            // The shell callback re-lays out this page when the pack changes the layout kind; run it
            // before ApplyTheme so the refreshed styling lands on the new structure.
            _onThemeApplied();
            ApplyTheme();
        }
    }

    /// <summary>THEME-MACOS-1: switches the Light/Dark variant of the active dual-variant pack.</summary>
    public void SwitchVariant(Avalonia.Styling.ThemeVariant variant)
    {
        if (Application.Current is { } app)
        {
            ThemePackService.ApplyVariant(app, variant);
            ApplyTheme();
            _onThemeApplied();
        }
    }

    /// <summary>
    /// THEME-MACOS-LAYOUTS-1: switches this page between the three frozen settings structures. The theme
    /// centre and every section card keep their instances and public members in all three layouts.
    /// </summary>
    public void ApplyLayout(LayoutProfile profile)
    {
        _layout = profile;
        DetachCards();
        switch (profile.Settings)
        {
            case SettingsStyle.SingleColumn:
                AttachLaunchpad(profile);
                break;
            case SettingsStyle.SplitSections:
                AttachSplit(profile);
                break;
            default:
                AttachSonoma();
                break;
        }

        ApplyPageChrome(profile);
        ApplyTheme();
        InvalidateMeasure();
        InvalidateVisual();
    }

    public void ApplyTheme()
    {
        _wired.Text = ViewModel.WiredSummary;
        ViewModel.SelectedPack = ThemePackService.Current;
        var pack = ThemePackService.Current;

        // Metrics are pack-level (not per variant), so corner radius + card shadow follow the pack even
        // during an in-place variant switch. Text/background colours of the code-built cards keep their
        // construction-time values (pre-existing behaviour of this shell's code-built pages).
        _themeCard.CornerRadius = new CornerRadius(pack.Metrics.CornerCard);
        var shadow = pack.Metrics.CardShadowFor(ThemePackService.CurrentVariant);
        _themeCard.BoxShadow = string.IsNullOrWhiteSpace(shadow) ? default : BoxShadows.Parse(shadow);
        foreach (var (themePack, button) in _themeButtons)
        {
            var selected = string.Equals(themePack.Id, pack.Id, StringComparison.Ordinal);
            button.Background = ThemePackService.Brush(selected ? "ChipActiveBg" : "ChipBg");
            button.Foreground = ThemePackService.Brush(selected ? "AccentText" : "TextPrimary");
            button.CornerRadius = new CornerRadius(pack.Metrics.CornerButton);
        }

        _sonomaRoot.Background = ThemePackService.Brush("AppBg");
        _launchpadRoot.Background = ThemePackService.Brush("AppBg");
        _splitRoot.Background = ThemePackService.Brush("AppBg");
        _splitNavBorder.Background = ThemePackService.Brush(ThemePackService.SidebarBackground);
        _splitNavBorder.BorderBrush = ThemePackService.Brush("CardBorder");
        StyleSectionButtons();

        RefreshAppearance(pack);
    }

    /// <summary>THEME-MACOS-LAYOUTS-1: Split directory selection (visibility only, no re-parenting).</summary>
    public void SelectSplitSection(string section)
    {
        if (!_splitSectionPanels.ContainsKey(section))
        {
            return;
        }

        _splitSection = section;
        foreach (var pair in _splitSectionPanels)
        {
            pair.Value.IsVisible = string.Equals(pair.Key, section, StringComparison.Ordinal);
        }

        StyleSectionButtons();
    }

    private void AttachSonoma()
    {
        _sonomaRoot.Children.Add(_title);
        Grid.SetRow(_wired, 1);
        _sonomaRoot.Children.Add(_wired);
        _sonomaThemeSlot.Children.Add(_themeCard);
        _sonomaRightSlot.Children.Add(_credentialCard);
        _sonomaRightSlot.Children.Add(_providerCard);
        _sonomaRightSlot.Children.Add(_networkCard);
        _sonomaRightSlot.Children.Add(_bindingsCard);
        _sonomaRightSlot.Children.Add(_deviceCard);
        _sonomaRightSlot.Children.Add(_dataCard);
        _sonomaRightSlot.Children.Add(_nsCard);
        Content = _sonomaRoot;
    }

    private void AttachLaunchpad(LayoutProfile profile)
    {
        _launchpadRoot.Children.Add(_title);
        Grid.SetRow(_wired, 1);
        _launchpadRoot.Children.Add(_wired);
        _launchpadColumnHost.MaxWidth = profile.SettingsMaxWidth > 0 ? profile.SettingsMaxWidth : 900;
        _launchpadStack.Children.Add(_themeCard);
        _launchpadStack.Children.Add(_credentialCard);
        _launchpadStack.Children.Add(_providerCard);
        _launchpadStack.Children.Add(_networkCard);
        _launchpadStack.Children.Add(_bindingsCard);
        _launchpadStack.Children.Add(_deviceCard);
        _launchpadStack.Children.Add(_dataCard);
        _launchpadStack.Children.Add(_nsCard);
        Content = _launchpadRoot;
    }

    private void AttachSplit(LayoutProfile profile)
    {
        _splitRoot.Children.Add(_title);
        Grid.SetRow(_wired, 1);
        _splitRoot.Children.Add(_wired);
        _splitBody.ColumnDefinitions[0].Width = new GridLength(profile.SettingsNavWidth > 0 ? profile.SettingsNavWidth : 240);
        _splitSectionPanels[SplitSectionTheme].Children.Add(_themeCard);
        _splitSectionPanels[SplitSectionCredentials].Children.Add(_credentialCard);
        _splitSectionPanels[SplitSectionProvider].Children.Add(_providerCard);
        _splitSectionPanels[SplitSectionNetwork].Children.Add(_networkCard);
        _splitSectionPanels[SplitSectionBindings].Children.Add(_bindingsCard);
        _splitSectionPanels[SplitSectionRegistry].Children.Add(_nsCard);
        _splitSectionPanels[SplitSectionRegistry].Children.Add(_deviceCard);
        _splitSectionPanels[SplitSectionRegistry].Children.Add(_dataCard);
        SelectSplitSection(_splitSection);
        Content = _splitRoot;
    }

    /// <summary>Removes every shared block from whatever slot currently owns it (one parent per control).</summary>
    private void DetachCards()
    {
        foreach (var card in new Control[] { _themeCard, _credentialCard, _providerCard, _networkCard, _bindingsCard, _deviceCard, _dataCard, _nsCard, _title, _wired })
        {
            if (card.Parent is Panel panel)
            {
                panel.Children.Remove(card);
            }
        }
    }

    private void ApplyPageChrome(LayoutProfile profile)
    {
        var launchpad = profile.Settings == SettingsStyle.SingleColumn;
        var split = profile.Settings == SettingsStyle.SplitSections;
        _title.FontSize = launchpad || split ? 22 : 26;
        _wired.FontSize = split ? 11 : 12;
        if (launchpad)
        {
            _launchpadRoot.Margin = new Thickness(28, 18);
        }
        else if (split)
        {
            _splitRoot.Margin = new Thickness(24, 16, 24, 16);
        }
        else
        {
            _sonomaRoot.Margin = new Thickness(28, 18);
        }
    }

    private void StyleSectionButtons()
    {
        foreach (var (key, _, button) in _splitSectionButtons)
        {
            var active = string.Equals(key, _splitSection, StringComparison.Ordinal);
            button.Background = ThemePackService.Brush(active ? "ChipActiveBg" : "ChipBg");
            button.Foreground = ThemePackService.Brush(active ? "AccentText" : "TextPrimary");
        }
    }

    private void RefreshAppearance(ThemePack pack)
    {
        _appearanceRow.IsVisible = pack.SupportsVariants;
        if (!pack.SupportsVariants)
        {
            return;
        }

        var dark = ThemePackMetrics.IsDark(ThemePackService.CurrentVariant);
        StyleVariantButton(_lightVariantButton, active: !dark);
        StyleVariantButton(_darkVariantButton, active: dark);
    }

    private static Button CreateVariantButton(string label) => new()
    {
        Content = label,
        FontSize = 12,
        Padding = new Thickness(10, 4),
        CornerRadius = new CornerRadius(ThemePackService.Current.Metrics.CornerSmall),
        Background = ThemePackService.Brush("ChipBg"),
        Foreground = ThemePackService.Brush("TextSecondary"),
        BorderBrush = ThemePackService.Brush("CardBorder"),
        BorderThickness = new Thickness(1),
    };

    private static void StyleVariantButton(Button button, bool active)
    {
        button.Background = ThemePackService.Brush(active ? "ChipActiveBg" : "ChipBg");
        button.Foreground = ThemePackService.Brush(active ? "AccentText" : "TextSecondary");
        button.BorderBrush = ThemePackService.Brush("CardBorder");
    }
}

public sealed class PlaceholderPage : UserControl
{
    public PlaceholderPage(string title, string hint)
    {
        Name = title;
        var panel = new StackPanel
        {
            Spacing = 10,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
        };
        panel.Children.Add(Ui.Text(title, 24, "TextPrimary", bold: true));
        panel.Children.Add(Ui.Text(hint, 12, "TextSecondary"));
        Content = new Grid { Background = ThemePackService.Brush("AppBg"), Children = { panel } };
    }
}
