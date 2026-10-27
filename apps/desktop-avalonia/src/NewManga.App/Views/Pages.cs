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

/// <summary>AC3 bookshelf page (Saber-informed, not pixel-identical).</summary>
public sealed class BookshelfPage : UserControl
{
    private readonly Border _header;
    private readonly Border _searchCard;
    private readonly StackPanel _detailBody;
    private readonly StackPanel _emptyPanel;
    private readonly StackPanel _noResultsPanel;
    private readonly TextBlock _status;
    private readonly Grid _root;
    private readonly IHostController? _controller;
    private readonly IFilePickerGateway? _picker;
    private readonly ImportPanel? _importPanel;
    private readonly Button _importFilesButton;
    private readonly Button _importFolderButton;

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
        var header = new Border { Padding = new Thickness(28, 18), Background = ThemePackService.Brush("HeaderGradient") };
        var headerGrid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        var headerText = new StackPanel { Spacing = 4 };
        headerText.Children.Add(Ui.Text("书架", 26, null, bold: true));
        headerText.Children.Add(Ui.Text("Saber-informed shell · 顶部渐变 / 1400 居中 / 3:4 书卡", 12, null));
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
        header.Child = headerGrid;
        _header = header;

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

        var chips = new WrapPanel { Orientation = Orientation.Horizontal };
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
        var card = new Border
        {
            Padding = new Thickness(18),
            CornerRadius = new CornerRadius(14),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
            Child = searchGrid,
        };
        _searchCard = card;

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

        var content = new Grid();
        content.Children.Add(scroll);
        content.Children.Add(_emptyPanel);
        content.Children.Add(_noResultsPanel);

        _detailBody = new StackPanel { Spacing = 10 };
        DetailPanel = new Border
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
        var body = new Grid { RowDefinitions = new RowDefinitions("Auto,*,Auto"), RowSpacing = 14 };
        var contentRow = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        Grid.SetRow(contentRow, 2);
        contentRow.Children.Add(content);
        Grid.SetColumn(DetailPanel, 1);
        contentRow.Children.Add(DetailPanel);
        Grid.SetRow(_searchCard, 0);
        body.Children.Add(_searchCard);
        Grid.SetRow(contentRow, 1);
        body.Children.Add(contentRow);

        _root = new Grid
        {
            RowDefinitions = new RowDefinitions("Auto,*"),
            Background = ThemePackService.Brush("AppBg"),
        };
        _root.Children.Add(_header);
        var inner = new Grid
        {
            RowDefinitions = new RowDefinitions("*,Auto"),
            Margin = new Thickness(24, 18, 24, 12),
        };
        Grid.SetRow(inner, 1);
        inner.Children.Add(body);
        var statusRow = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        statusRow.Children.Add(_status);
        Grid.SetRow(statusRow, 1);
        inner.Children.Add(statusRow);
        _root.Children.Add(inner);
        if (_controller is not null)
        {
            _importPanel = new ImportPanel(_controller) { IsVisible = false };
            _importPanel.ImportCompleted += (_, _) => LastImportOperation = RefreshAfterImportAsync();
            Grid.SetRowSpan(_importPanel, 2);
            _root.Children.Add(_importPanel);
        }

        Content = _root;

        ViewModel.PropertyChanged += (_, args) =>
        {
            switch (args.PropertyName)
            {
                case nameof(BookshelfViewModel.ColumnCount):
                    GridPanel.Columns = ViewModel.ColumnCount;
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
        ApplyTheme();
    }

    public BookshelfViewModel ViewModel { get; }

    public TextBox SearchBox { get; }

    public ItemsControl TagChips { get; }

    public ItemsControl BookGrid { get; }

    public UniformGrid GridPanel { get; }

    public Border DetailPanel { get; }

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

    /// <summary>Last import flow (tests await this; the picker itself is faked headless).</summary>
    public Task LastImportOperation { get; private set; } = Task.CompletedTask;

    public void ApplyTheme()
    {
        _root.Background = ThemePackService.Brush("AppBg");
        _header.Background = ThemePackService.Brush("HeaderGradient");
        _searchCard.Background = ThemePackService.Brush("CardBg");
        _searchCard.BorderBrush = ThemePackService.Brush("CardBorder");
        DetailPanel.Background = ThemePackService.Brush("CardBg");
        DetailPanel.BorderBrush = ThemePackService.Brush("CardBorder");
        RebuildChips();
    }

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

    private Control BuildCard(BookCardItem item)
    {
        var cover = new Border
        {
            Height = 226,
            CornerRadius = new CornerRadius(10),
            Background = ThemePackService.Brush("ChipBg"),
            Child = new TextBlock
            {
                Text = item.Glyph,
                FontSize = 44,
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
            CornerRadius = new CornerRadius(0, 0, 10, 10),
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
            Width = BookshelfViewModel.CardWidth,
            Margin = new Thickness(0, 0, BookshelfViewModel.CardGap, BookshelfViewModel.CardGap),
            CornerRadius = new CornerRadius(12),
            Padding = new Thickness(8),
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
        DetailPanel.IsVisible = ViewModel.IsDetailOpen;
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
        DetailPanel.IsVisible = true;
    }
}

/// <summary>AC4 settings skeleton.</summary>
public sealed class SettingsPage : UserControl
{
    private readonly StackPanel _themeList;
    private readonly TextBlock _wired;
    private readonly TextBlock _settingsJson;
    private readonly StackPanel _nsList;
    private readonly Action _onThemeApplied;

    // THEME-MACOS-1: theme card geometry comes from the active pack's Metrics (old packs = corner 12, no
    // shadow; macOS = corner 14 + soft card shadow) and the appearance row toggles Light/Dark.
    private readonly Border _themeCard;
    private readonly StackPanel _appearanceRow;
    private readonly Button _lightVariantButton;
    private readonly Button _darkVariantButton;
    private readonly List<(ThemePack Pack, Button Button)> _themeButtons = new();

    public SettingsPage(SettingsViewModel viewModel, Action onThemeApplied, IHostController? controller = null)
    {
        ViewModel = viewModel;
        _onThemeApplied = onThemeApplied;
        Name = "SettingsPage";
        var root = new Grid
        {
            RowDefinitions = new RowDefinitions("Auto,Auto,*,Auto"),
            Margin = new Thickness(28, 18),
            Background = ThemePackService.Brush("AppBg"),
        };
        root.Children.Add(Ui.Text("设置", 26, "TextPrimary", bold: true));
        _wired = Ui.Text(viewModel.WiredSummary, 12, "TextSecondary");
        Grid.SetRow(_wired, 1);
        root.Children.Add(_wired);

        var content = new Grid { ColumnDefinitions = new ColumnDefinitions("320,*"), ColumnSpacing = 18, Margin = new Thickness(0, 12, 0, 0) };
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
        content.Children.Add(_themeCard);

        var right = new StackPanel { Spacing = 12 };
        var dataCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        _settingsJson = Ui.Text(viewModel.SettingsJson, 11, "TextSecondary");
        var dataBody = new StackPanel();
        dataBody.Children.Add(Ui.Text("已接线 settings 命令 · 展示", 13, "TextPrimary", bold: true));
        dataBody.Children.Add(_settingsJson);
        dataCard.Child = dataBody;
        right.Children.Add(dataCard);

        // GPU-ORT-PROBE-1: packaged device probe (ONNX Runtime EP list recorded in VERSION.json).
        DeviceStatus = Services.DeviceStatus.Load();
        DeviceStatusText = Ui.Text(
            DeviceStatus?.DisplayText ?? "GPU：未打包探测（开发运行）",
            11,
            DeviceStatus?.Available == true ? "TextPrimary" : "TextSecondary");
        var deviceCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        var deviceBody = new StackPanel();
        deviceBody.Children.Add(Ui.Text("运行环境 · GPU", 13, "TextPrimary", bold: true));
        deviceBody.Children.Add(DeviceStatusText);
        deviceBody.Children.Add(Ui.Text(
            "探测源：ONNX Runtime 执行提供程序（打包时写入 VERSION.json）",
            11,
            "TextSecondary"));
        deviceCard.Child = deviceBody;
        right.Children.Insert(0, deviceCard);

        var nsCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        _nsList = new StackPanel { Spacing = 4 };
        _nsList.Children.Add(Ui.Text("S2 NOT_SUPPORTED 批次登记（S3-A/B/C 已由 NS-WIRE-A1 接线）", 13, "TextPrimary", bold: true));
        foreach (var item in viewModel.NsBatch)
        {
            _nsList.Children.Add(Ui.Text($"[{item.Status}] {item.Command} · {item.Page}", 11, "TextSecondary"));
        }

        nsCard.Child = _nsList;
        right.Children.Add(nsCard);

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
        var credentialCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        credentialCard.Child = Credentials;
        right.Children.Insert(0, credentialCard);

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
        right.Children.Insert(1, ProfileUi.Card(ProviderProfiles));
        right.Children.Insert(2, ProfileUi.Card(NetworkProfiles));
        right.Children.Insert(3, ProfileUi.Card(Bindings));
        Grid.SetColumn(right, 1);
        content.Children.Add(right);
        // SETTINGS-PROFILE-UI-1: the settings page is now taller than the window (credential + provider
        // + network + bindings cards), so the contract row scrolls instead of clipping the lower cards.
        var pageScroll = new ScrollViewer
        {
            Content = content,
            HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Auto,
        };
        Grid.SetRow(pageScroll, 2);
        root.Children.Add(pageScroll);
        Content = root;
        ApplyTheme();
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
            // Refresh this page's own theme-centric controls even when the host callback is a no-op
            // (the real shell callback also repaints nav/title bar through MainWindow.ApplyTheme).
            ApplyTheme();
            _onThemeApplied();
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

        RefreshAppearance(pack);
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
