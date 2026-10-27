using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.Media;
using Avalonia.VisualTree;
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
    private double _lastRenderScaling;

    /// <summary>F11-HOTKEY-1: page to return to after an F11-initiated immersive session (null = reader).</summary>
    private string? _pageBeforeImmersive;

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
        Workbench = new WorkbenchPage(new WorkbenchViewModel());
        var readerUserViewModel = new ReaderViewModel();
        Reader = new ReaderPage(
            readerUserViewModel,
            NewManga.App.Views.ReaderFixtureLocator.TypographyPaths(),
            NewManga.App.Views.ReaderFixtureLocator.TileDirectory)
        {
            // READER-PROGRESS-1 AC1: the page persists its position through the controller seam.
            ProgressSink = _controller,
        };
        Reader.ImmersiveRequested += (_, _) => OpenImmersiveReader();
        // CHAPTER-SELECTOR-1: book-card double-click / detail action opens that exact book, and the
        // reader's chapter picker re-loads the chosen chapter.
        BookshelfPageControl.OpenReaderRequested += (_, item) =>
            LastReaderNavigation = OpenReaderForBookAsync(item.BookId);
        Reader.ChapterSelectionRequested += (_, chapterId) =>
            LastReaderNavigation = OpenReaderForBookAsync(Reader.LibraryBook?.BookId, chapterId);
        _pages["workbench"] = Workbench;
        _pages["reader"] = Reader;
        Settings = new SettingsPage(settingsViewModel, OnThemeApplied, _controller);
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

        Opened += (_, _) =>
        {
            _lastRenderScaling = RenderScaling;
            WriteMaterialDiagnostics();
        };
        PropertyChanged += (_, args) =>
        {
            if (string.Equals(args.Property?.Name, "RenderScaling", StringComparison.Ordinal))
            {
                var previous = _lastRenderScaling;
                _lastRenderScaling = RenderScaling;
                InvalidateMeasure();
                InvalidateVisual();
                Dispatcher.UIThread.Post(() =>
                {
                    InvalidateMeasure();
                    InvalidateVisual();
                    WriteMaterialDiagnostics();
                }, DispatcherPriority.Render);
                try
                {
                    var root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "com.newmanga.desktop", "logs");
                    Directory.CreateDirectory(root);
                    File.AppendAllText(Path.Combine(root, "window-material.log"), $"{DateTime.UtcNow:o} scaling {previous:0.##} -> {RenderScaling:0.##}{Environment.NewLine}");
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                }
            }
        };
        Loaded += OnLoaded;
        Closed += OnClosed;
        // F11-HOTKEY-1: application-internal F11 toggle. Tunnelling so the window sees F11 before
        // focused controls (the handler still refuses when a text input has focus).
        AddHandler(KeyDownEvent, OnWindowKeyDown, RoutingStrategies.Tunnel, handledEventsToo: true);
        Navigate("bookshelf");
        ApplyTheme();
    }

    public BookshelfViewModel Bookshelf { get; }

    public SettingsPage Settings { get; }

    public WorkbenchPage Workbench { get; private set; } = null!;

    public ReaderPage Reader { get; private set; } = null!;

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

        // READER-PROGRESS-1 AC1: leaving the reader page is a save trigger (关闭阅读器).
        if (string.Equals(CurrentPage, "reader", StringComparison.Ordinal) &&
            !string.Equals(page, "reader", StringComparison.Ordinal))
        {
            _ = Reader.FlushProgressAsync();
        }

        CurrentPage = page;
        PageHost.Content = target;
        foreach (var pair in _navButtons)
        {
            var active = pair.Key == page;
            pair.Value.Background = ThemePackService.Brush(active ? "NavActiveBg" : "NavBg");
            pair.Value.Foreground = ThemePackService.Brush(active ? "AccentText" : "TextPrimary");
        }

        if (string.Equals(page, "reader", StringComparison.Ordinal))
        {
            // READER-LIBRARY-WIRE-1 AC1: entering the reader loads the real library book (fixtures stay as fallback).
            _ = EnsureReaderLoadedAsync();
        }

        if (string.Equals(page, "settings", StringComparison.Ordinal))
        {
            // CREDENTIAL-UI-1 AC2: refresh configured/missing states every time settings opens.
            _ = Settings.RefreshCredentialsAsync();
        }
    }

    /// <summary>READER-LIBRARY-WIRE-1 AC2: the immersive window created by the reader page entry.</summary>
    public ReaderWindow? LastImmersiveWindow { get; private set; }

    /// <summary>F11-HOTKEY-1: page to restore when an F11-initiated immersive session closes.</summary>
    public string? ImmersiveRestorePage => _pageBeforeImmersive;

    /// <summary>F11-HOTKEY-1: last F11 toggle task (headless tests / evidence await this).</summary>
    public Task LastImmersiveToggle { get; private set; } = Task.CompletedTask;

    /// <summary>
    /// F11-HOTKEY-1 AC1/AC2: one application-level F11 press.
    /// Behaviour (Record Decision): bare F11 only (no modifiers); ignored while a text input has
    /// focus; opens the immersive reader for the current book — switching to the reader page first
    /// when pressed elsewhere — and closes it (restoring the page the user came from) when already
    /// open. Returns true when the key was consumed.
    /// </summary>
    public bool TryHandleGlobalKey(Key key, KeyModifiers modifiers = KeyModifiers.None)
    {
        if (key != Key.F11)
        {
            return false;
        }

        if (modifiers != KeyModifiers.None)
        {
            return false;
        }

        if (IsTextInputFocused())
        {
            return false;
        }

        LastImmersiveToggle = ToggleImmersiveAsync();
        return true;
    }

    /// <summary>F11-HOTKEY-1 AC2: true when the focused element is (inside) a text input.</summary>
    public bool IsTextInputFocused()
    {
        var focused = FocusManager?.GetFocusedElement();
        if (focused is null)
        {
            return false;
        }

        if (focused is TextBox)
        {
            return true;
        }

        return focused is Visual visual && visual.FindAncestorOfType<TextBox>(includeSelf: false) is not null;
    }

    /// <summary>
    /// F11-HOTKEY-1 AC1: F11 toggle. Opening from a non-reader page first enters the reader (loading
    /// the current/default book) and remembers that page so Esc/F11 returns there; opening from the
    /// reader page keeps the reader page as the return target. While an immersive window is open,
    /// toggling again closes it.
    /// </summary>
    public async Task ToggleImmersiveAsync()
    {
        if (LastImmersiveWindow is { } open)
        {
            if (open.IsVisible)
            {
                open.Close();
            }
            else
            {
                LastImmersiveWindow = null;
            }

            return;
        }

        var origin = CurrentPage;
        if (!string.Equals(origin, "reader", StringComparison.Ordinal))
        {
            Navigate("reader");
            await EnsureReaderLoadedAsync().ConfigureAwait(true);
        }

        OpenImmersiveReader();
        if (!string.Equals(origin, "reader", StringComparison.Ordinal))
        {
            _pageBeforeImmersive = origin;
        }
    }

    private void OnWindowKeyDown(object? sender, KeyEventArgs e)
    {
        if (TryHandleGlobalKey(e.Key, e.KeyModifiers))
        {
            e.Handled = true;
        }
    }

    private void OnImmersiveWindowClosed(ReaderWindow window)
    {
        if (ReferenceEquals(LastImmersiveWindow, window))
        {
            LastImmersiveWindow = null;
        }

        if (_pageBeforeImmersive is { } origin)
        {
            _pageBeforeImmersive = null;
            Navigate(origin);
        }
    }

    /// <summary>
    /// READER-LIBRARY-WIRE-1 AC1: pull the real book through Host/CoreClient
    /// (ListBooks → list_chapters → GetReaderProjection); on empty/failure keep the fixture fallback
    /// and show the empty-state hint. <c>NEWMANGA_READER_SOURCE=fixtures</c> forces the fixture path.
    /// READER-PROGRESS-1: the projection resumes the persisted page, so reopening the reader shows
    /// the position the user left.
    /// </summary>
    public async Task EnsureReaderLoadedAsync(CancellationToken cancellationToken = default)
    {
        if (Reader.LibraryBook is not null)
        {
            return;
        }

        if (await LoadReaderAsync(null, null, cancellationToken).ConfigureAwait(true))
        {
            await PopulateChaptersAsync(cancellationToken).ConfigureAwait(true);
        }
    }

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC2: open the reader on a specific book (and optionally chapter). The
    /// current position is flushed first when switching book/chapter; then the target chapter is
    /// loaded with the Core-resumed page and its chapter list is populated.
    /// </summary>
    public async Task<bool> OpenReaderForBookAsync(
        string? bookId,
        string? chapterId = null,
        CancellationToken cancellationToken = default)
    {
        if (Reader.LibraryBook is { } current &&
            (!string.IsNullOrWhiteSpace(bookId) || !string.IsNullOrWhiteSpace(chapterId)) &&
            (!string.Equals(current.BookId, bookId, StringComparison.Ordinal) ||
             (!string.IsNullOrWhiteSpace(chapterId) && !string.Equals(current.ChapterId, chapterId, StringComparison.Ordinal))))
        {
            // Leaving this (book, chapter, mode) session: persist where the user stopped.
            await Reader.FlushProgressAsync().ConfigureAwait(true);
        }

        var loaded = await LoadReaderAsync(bookId, chapterId, cancellationToken).ConfigureAwait(true);
        if (!loaded)
        {
            return false;
        }

        Navigate("reader");
        await PopulateChaptersAsync(cancellationToken).ConfigureAwait(true);
        return true;
    }

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC1: pull the chapter list for the loaded book and hand it to the reader
    /// page (single-chapter books keep the selector hidden). Stale responses for a previous book are
    /// dropped.
    /// </summary>
    public async Task PopulateChaptersAsync(CancellationToken cancellationToken = default)
    {
        if (Reader.LibraryBook is not { } book)
        {
            Reader.LoadChapters(Array.Empty<ChapterSummary>());
            return;
        }

        var chapters = await _controller.ListChaptersAsync(book.BookId, cancellationToken).ConfigureAwait(true);
        if (Reader.LibraryBook is not { } stillLoaded ||
            !string.Equals(stillLoaded.BookId, book.BookId, StringComparison.Ordinal))
        {
            return;
        }

        Reader.LoadChapters(chapters, stillLoaded.ChapterId);
        Reader.SetBookContext(stillLoaded.BookTitle, stillLoaded.ChapterTitle);
    }

    /// <summary>CHAPTER-SELECTOR-1: last reader navigation task (tests/evidence await this).</summary>
    public Task LastReaderNavigation { get; private set; } = Task.CompletedTask;

    /// <summary>CHAPTER-SELECTOR-1 AC2: current reader book id (null = fixture/empty).</summary>
    public string? CurrentReaderBookId => Reader.LibraryBook?.BookId;

    /// <summary>CHAPTER-SELECTOR-1 AC1: current reader chapter id (null = fixture/empty).</summary>
    public string? CurrentReaderChapterId => Reader.LibraryBook?.ChapterId;

    /// <summary>
    /// READER-PROGRESS-1/CHAPTER-SELECTOR-1: (re)loads one book/chapter from the Host and applies the
    /// Core-resumed page. Null book ids mean "the reader's default book/chapter".
    /// </summary>
    public async Task<bool> LoadReaderAsync(
        string? bookId,
        string? chapterId,
        CancellationToken cancellationToken = default)
    {
        var source = Environment.GetEnvironmentVariable("NEWMANGA_READER_SOURCE");
        if (string.Equals(source, "fixtures", StringComparison.OrdinalIgnoreCase))
        {
            Reader.SetLibraryEmpty("fixture 模式：NEWMANGA_READER_SOURCE=fixtures（跳过真实书库）");
            return false;
        }

        try
        {
            var book = await _controller.LoadReaderBookAsync(bookId, chapterId, cancellationToken).ConfigureAwait(true);
            if (book is null)
            {
                Reader.SetLibraryEmpty("书架为空或 Core 未就绪：已保留 fixture 回退；导入一本书后重试。");
                return false;
            }

            Reader.LoadLibrary(book);
            return true;
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            Reader.SetLibraryEmpty("读取书库失败：已保留 fixture 回退。");
            return false;
        }
    }

    /// <summary>READER-LIBRARY-WIRE-1 AC2: instantiate the immersive window for the active source.</summary>
    public ReaderWindow OpenImmersiveReader()
    {
        var window = Reader.LibraryBook is { } book
            ? new ReaderWindow(Reader.ViewModel, book, Reader.ProgressSink)
            : new ReaderWindow(
                Reader.ViewModel,
                NewManga.App.Views.ReaderFixtureLocator.TypographyPaths(),
                NewManga.App.Views.ReaderFixtureLocator.TileDirectory);
        if (Reader.LibraryBook is { } loadedBook)
        {
            // CHAPTER-SELECTOR-1: the immersive chrome shows the book/chapter context but keeps the
            // fullscreen surface distraction-free (chapter switching happens in the reader page).
            window.Page.LoadChapters(Reader.Chapters, Reader.CurrentChapterId);
            window.Page.HideChapterSelector();
            window.Page.SetBookContext(loadedBook.BookTitle, loadedBook.ChapterTitle);
        }

        LastImmersiveWindow = window;
        // F11-HOTKEY-1: closing (Esc / F11 / toolbar) restores the page F11 came from, if any.
        window.Closed += (_, _) => OnImmersiveWindowClosed(window);
        window.Show();
        return window;
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
            if (string.Equals(CurrentPage, "reader", StringComparison.Ordinal))
            {
                await EnsureReaderLoadedAsync(CancellationToken.None);
            }

            // CREDENTIAL-UI-1 AC2: configured/missing states once the Host is ready.
            await Settings.RefreshCredentialsAsync();
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException)
        {
            _status.Text = "Host 启动异常（只读骨架）";
        }
    }

    private void OnClosed(object? sender, EventArgs e)
    {
        // CREDENTIAL-UI-1 AC3: closing the window must not leave a plaintext credential reference.
        Settings.ClearCredentialSecrets();

        // READER-PROGRESS-1 AC1: closing the app is a save trigger. Flush on the thread pool so the
        // UI-thread continuations of the save chain can run (a sync wait here would deadlock).
        try
        {
            var flush = Task.Run(() => Reader.FlushProgressAsync());
            flush.Wait(TimeSpan.FromSeconds(5));
        }
        catch (Exception ex) when (ex is AggregateException or InvalidOperationException or OperationCanceledException)
        {
            // best effort: a failed progress save must never block shutdown
        }

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
    /// <summary>AC2 diagnostics: material kind + requested/actual transparency level.</summary>
    public string MaterialDiagnostics =>
        $"material={_materialKind}; requested={string.Join(",", TransparencyLevelHint)}; actual={ActualTransparencyLevel}";

    public string? DiagnosticsPath { get; private set; }

    private void WriteMaterialDiagnostics()
    {
        try
        {
            var root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "com.newmanga.desktop", "logs");
            Directory.CreateDirectory(root);
            DiagnosticsPath = Path.Combine(root, "window-material.log");
            File.AppendAllText(DiagnosticsPath, $"{DateTime.UtcNow:o} {MaterialDiagnostics}{Environment.NewLine}");
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
        {
            DiagnosticsPath = null;
        }
    }
}
