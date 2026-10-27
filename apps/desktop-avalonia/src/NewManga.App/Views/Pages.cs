using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Controls.Templates;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Immutable;
using NewManga.App.ViewModels;
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

    public BookshelfPage(BookshelfViewModel viewModel)
    {
        ViewModel = viewModel;
        Name = "BookshelfPage";

        _status = Ui.Text("只读骨架 · 数据经 Core command dispatcher", 12, "TextSecondary");
        var header = new Border { Padding = new Thickness(28, 18), Background = ThemePackService.Brush("HeaderGradient") };
        var headerGrid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        var headerText = new StackPanel { Spacing = 4 };
        headerText.Children.Add(Ui.Text("书架", 26, null, bold: true));
        headerText.Children.Add(Ui.Text("Saber-informed shell · 顶部渐变 / 1400 居中 / 3:4 书卡", 12, null));
        headerGrid.Children.Add(headerText);
        var actions = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, VerticalAlignment = VerticalAlignment.Center };
        var newButton = Ui.Action("新建", () => OpenNewDialog(), primary: true);
        newButton.Name = "NewBookButton";
        var refreshButton = Ui.Action("刷新", () => _ = ViewModel.RefreshAsync());
        refreshButton.Name = "RefreshButton";
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

    public SettingsPage(SettingsViewModel viewModel, Action onThemeApplied)
    {
        ViewModel = viewModel;
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
        var themeCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
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
                CornerRadius = new CornerRadius(8),
                Background = pack.Id == ThemePackService.Current.Id ? ThemePackService.Brush("ChipActiveBg") : ThemePackService.Brush("ChipBg"),
                Foreground = pack.Id == ThemePackService.Current.Id ? ThemePackService.Brush("AccentText") : ThemePackService.Brush("TextPrimary"),
            };
            button.Click += (_, _) =>
            {
                if (Application.Current is { } app)
                {
                    ThemePackService.Apply(app, pack);
                    onThemeApplied();
                }
            };
            return button;
        });
        _themeList.Children.Add(ThemeList);
        themeCard.Child = _themeList;
        content.Children.Add(themeCard);

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

        var nsCard = new Border
        {
            Padding = new Thickness(16),
            CornerRadius = new CornerRadius(12),
            Background = ThemePackService.Brush("CardBg"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        _nsList = new StackPanel { Spacing = 4 };
        _nsList.Children.Add(Ui.Text("S2 NOT_SUPPORTED 批次登记（S3-A/B/C）", 13, "TextPrimary", bold: true));
        foreach (var item in viewModel.NsBatch)
        {
            _nsList.Children.Add(Ui.Text($"[{item.Status}] {item.Command} · {item.Page}", 11, "TextSecondary"));
        }

        nsCard.Child = _nsList;
        right.Children.Add(nsCard);
        Grid.SetColumn(right, 1);
        content.Children.Add(right);
        Grid.SetRow(content, 2);
        root.Children.Add(content);
        Content = root;
        ApplyTheme();
    }

    public SettingsViewModel ViewModel { get; }

    public ItemsControl ThemeList { get; }

    public StackPanel NsList => _nsList;

    public void UpdateSettingsJson(System.Text.Json.JsonElement value)
    {
        ViewModel.UpdateSettingsJson(value);
        _settingsJson.Text = ViewModel.SettingsJson;
    }

    public void ApplyTheme()
    {
        _wired.Text = ViewModel.WiredSummary;
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
