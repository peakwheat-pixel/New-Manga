using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Media;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.CoreClient;
using NewManga.Theme;

namespace NewManga.App.Views;

public partial class MainWindow : Window
{
    private readonly IHostController _controller;
    private readonly AppOptions _options;
    private readonly Dictionary<string, Button> _navButtons = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Control> _pages = new(StringComparer.Ordinal);
    private readonly TextBlock _status;
    private WindowMaterialKind _materialKind;

    /// <summary>Design-time / XAML loader constructor.</summary>
    public MainWindow()
        : this(NullHostController.Instance, new AppOptions())
    {
    }

    public MainWindow(IHostController controller, AppOptions options)
    {
        _controller = controller;
        _options = options;
        InitializeComponent();

        Bookshelf = new BookshelfViewModel(
            loader: async cancellationToken =>
            {
                await _controller.RefreshBooksAsync(cancellationToken);
                return _controller.Snapshot.Books.Select(ToCard).ToList();
            },
            creator: _controller.TryCreateBookAsync);
        var settingsViewModel = new SettingsViewModel();

        _status = new TextBlock
        {
            Text = "启动中…",
            FontSize = 11,
            Foreground = ThemePackService.Brush("TextSecondary"),
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        RightPanel.Children.Add(_status);
        var themeCycle = new Button
        {
            Content = "换主题",
            FontSize = 11,
            Padding = new Thickness(10, 4),
            CornerRadius = new CornerRadius(8),
            Background = ThemePackService.Brush("ChipBg"),
            Foreground = ThemePackService.Brush("TextSecondary"),
        };
        themeCycle.Click += (_, _) => CycleTheme();
        RightPanel.Children.Add(themeCycle);

        _pages["bookshelf"] = new BookshelfPage(Bookshelf);
        _pages["workbench"] = new PlaceholderPage("工作台", "S4 插槽：Run / Task / Export 投影（当前 50 条 NS 中的 Run/Export 批次）。");
        _pages["reader"] = new PlaceholderPage("阅读器", "S4 插槽：Reader 投影与进度（NS 批 S3-C）。");
        Settings = new SettingsPage(settingsViewModel, OnThemeApplied);
        _pages["settings"] = Settings;

        AddNav("bookshelf", "书架", "Icon.bookshelf");
        AddNav("workbench", "工作台", "Icon.workbench");
        AddNav("reader", "阅读器", "Icon.reader");
        AddNav("settings", "设置", "Icon.settings");

        _materialKind = WindowMaterial.ForCurrentOs().Kind;
        TransparencyLevelHint = _materialKind == WindowMaterialKind.Mica
            ? new[] { WindowTransparencyLevel.Mica, WindowTransparencyLevel.Blur, WindowTransparencyLevel.None }
            : new[] { WindowTransparencyLevel.None };
        if (_materialKind == WindowMaterialKind.OpaqueFallback)
        {
            Background = ThemePackService.Brush("MicaFallback");
        }

        Loaded += OnLoaded;
        Closed += OnClosed;
        Navigate("bookshelf");
        ApplyTheme();
    }

    public BookshelfViewModel Bookshelf { get; }

    public SettingsPage Settings { get; }

    public ContentControl PageHostControl => PageHost;

    public StackPanel NavPanelControl => NavPanel;

    public IReadOnlyDictionary<string, Button> NavButtons => _navButtons;

    public string CurrentPage { get; private set; } = "bookshelf";

    public WindowMaterialKind MaterialKind => _materialKind;

    public IHostController Controller => _controller;

    public void Navigate(string page)
    {
        if (!_pages.TryGetValue(page, out var target))
        {
            return;
        }

        CurrentPage = page;
        PageHost.Content = target;
        foreach (var pair in _navButtons)
        {
            var active = pair.Key == page;
            pair.Value.Background = ThemePackService.Brush(active ? "NavActiveBg" : "NavBg");
            pair.Value.Foreground = ThemePackService.Brush(active ? "AccentText" : "TextPrimary");
        }
    }

    public void ApplyTheme()
    {
        BookshelfPageControl.ApplyTheme();
        Settings.ApplyTheme();
        foreach (var pair in _navButtons)
        {
            var active = pair.Key == CurrentPage;
            pair.Value.Background = ThemePackService.Brush(active ? "NavActiveBg" : "NavBg");
            pair.Value.Foreground = ThemePackService.Brush(active ? "AccentText" : "TextPrimary");
        }

        _status.Foreground = ThemePackService.Brush("TextSecondary");
    }

    public BookshelfPage BookshelfPageControl => (BookshelfPage)_pages["bookshelf"];

    public void CycleTheme()
    {
        var packs = ThemePacks.All;
        var index = packs.ToList().FindIndex(pack => pack.Id == ThemePackService.Current.Id);
        var next = packs[(index + 1) % packs.Count];
        if (Application.Current is { } application)
        {
            ThemePackService.Apply(application, next);
            OnThemeApplied();
        }
    }

    public void OnThemeApplied()
    {
        ApplyTheme();
        InvalidateVisual();
    }

    private void AddNav(string key, string label, string iconKey)
    {
        var button = new Button
        {
            Content = new StackPanel
            {
                Orientation = Avalonia.Layout.Orientation.Horizontal,
                Spacing = 6,
                Children =
                {
                    new TextBlock
                    {
                        Text = Application.Current?.TryGetResource(iconKey, null, out var glyph) == true
                            ? glyph?.ToString()
                            : string.Empty,
                        FontSize = 13,
                    },
                    new TextBlock { Text = label, FontSize = 13 },
                },
            },
            Padding = new Thickness(14, 6),
            CornerRadius = new CornerRadius(9),
            Background = ThemePackService.Brush("NavBg"),
            Foreground = ThemePackService.Brush("TextPrimary"),
            Focusable = true,
        };
        button.Name = "Nav_" + key;
        button.Click += (_, _) => Navigate(key);
        _navButtons[key] = button;
        NavPanel.Children.Add(button);
    }

    private async void OnLoaded(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        ApplyTheme();
        await StartHostAsync();
    }

    private async Task StartHostAsync()
    {
        try
        {
            await _controller.StartAsync();
            await Bookshelf.RefreshAsync();
            _status.Text = _controller.Snapshot.State switch
            {
                HostViewState.Ready => "Host 就绪",
                HostViewState.AlreadyRunning => "已有实例运行",
                HostViewState.Failed => "Host 失败（只读骨架仍可用）",
                _ => "启动中…",
            };
            BookshelfPageControl.ApplyTheme();
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException)
        {
            _status.Text = "Host 启动异常（只读骨架）";
        }
    }

    private void OnClosed(object? sender, EventArgs e)
    {
        try
        {
            _controller.DisposeAsync().AsTask().GetAwaiter().GetResult();
        }
        catch (Exception ex) when (ex is InvalidOperationException or AggregateException)
        {
            // best effort
        }
    }

    private void OnTitleBarPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.GetCurrentPoint(this).Properties.IsLeftButtonPressed)
        {
            BeginMoveDrag(e);
        }
    }

    private static BookCardItem ToCard(BookSummary book) => new()
    {
        BookId = book.BookId,
        Title = book.Title,
        OriginalTitle = book.OriginalTitle,
        IsFavorite = book.IsFavorite,
        PageCount = book.PageCount,
        Tag = book.IsFavorite ? "收藏" : "未分类",
    };
}
