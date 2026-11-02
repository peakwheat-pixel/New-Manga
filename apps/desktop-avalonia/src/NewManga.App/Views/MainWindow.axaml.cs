using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.Media;
using Avalonia.Styling;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.CoreClient;
using NewManga.App.Views.Legacy;
using NewManga.DesignSystem.Theming;
using DesignSystemAppearance = NewManga.DesignSystem.Theming.AppearanceMode;

namespace NewManga.App.Views;

public partial class MainWindow : Window
{
    private readonly IHostController _controller;
    private readonly IFilePickerGateway? _filePickerOverride;
    private readonly IFilePickerGateway _filePicker;
    private readonly AppOptions _options;
    private readonly DesignSystemThemeManager? _themeManager;
    private readonly Dictionary<string, Button> _navButtons = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Control> _pages = new(StringComparer.Ordinal);
    private readonly List<string> _navOrder = new();
    private readonly Dictionary<string, NavVisual> _navVisuals = new(StringComparer.Ordinal);
    private readonly TextBlock _status;
    private WindowMaterialKind _materialKind;
    private double _lastRenderScaling;

    /// <summary>THEME-MACOS-LAYOUTS-1: layout profile currently applied to the shell and both pages.</summary>
    private LegacyLayoutProfile _layout = LegacyLayoutProfiles.Sonoma;

    /// <summary>One navigation button plus the parts whose geometry/orientation change per layout.</summary>
    private sealed record NavVisual(Button Button, StackPanel Content, TextBlock Icon, TextBlock Label);

    /// <summary>F11-HOTKEY-1: page to return to after an F11-initiated immersive session (null = reader).</summary>
    private string? _pageBeforeImmersive;

    /// <summary>Design-time / XAML loader constructor.</summary>
    public MainWindow()
        : this(NullHostController.Instance, new AppOptions())
    {
    }

    public MainWindow(
        IHostController controller,
        AppOptions options,
        IFilePickerGateway? filePicker = null,
        DesignSystemThemeManager? themeManager = null)
    {
        _controller = controller;
        _options = options;
        _filePickerOverride = filePicker;
        _themeManager = themeManager;
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
            Foreground = LegacyChrome.Brush("TextSecondary"),
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        RightPanel.Children.Add(_status);
        var themeCycle = new Button
        {
            Content = "换主题",
            FontSize = 11,
            Padding = new Thickness(10, 4),
            CornerRadius = new CornerRadius(8),
            Background = LegacyChrome.Brush("ChipBg"),
            Foreground = LegacyChrome.Brush("TextSecondary"),
        };
        themeCycle.Click += (_, _) => CycleTheme();
        RightPanel.Children.Add(themeCycle);

        // IMPORT-EXPORT-UI-1: one storage-provider gateway for every import/export entry; the picker
        // resolves the window's TopLevel lazily so construction stays headless-safe.
        _filePicker = _filePickerOverride ?? new AvaloniaFilePickerGateway(_ => TopLevel.GetTopLevel(this));
        _pages["bookshelf"] = new BookshelfPage(Bookshelf, _controller, _filePicker);
        Workbench = new WorkbenchPage(new WorkbenchViewModel(), _controller, _filePicker);
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
        Reader.SetExportController(_controller, _filePicker);
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
        // THEME-MACOS-LAYOUTS-1: place the four buttons in the host the active pack asks for (title bar /
        // Dock / sidebar) and build the pages' shelf/settings structure before the first navigation.
        ApplyLayout();

        _materialKind = WindowMaterial.ForCurrentOs().Kind;
        TransparencyLevelHint = _materialKind == WindowMaterialKind.Mica
            ? new[] { WindowTransparencyLevel.Mica, WindowTransparencyLevel.Blur, WindowTransparencyLevel.None }
            : new[] { WindowTransparencyLevel.None };
        if (_materialKind == WindowMaterialKind.OpaqueFallback)
        {
            Background = LegacyChrome.Brush("MicaFallback");
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

    /// <summary>THEME-MACOS-LAYOUTS-1: bottom Dock host (visible only for a Dock layout pack).</summary>
    public Border DockHostControl => DockHost;

    /// <summary>THEME-MACOS-LAYOUTS-1: left Sidebar host (visible only for a Sidebar layout pack).</summary>
    public Border SidebarHostControl => SidebarHost;

    /// <summary>THEME-MACOS-LAYOUTS-1: body host whose first column is the Split sidebar (0 width otherwise).</summary>
    public Grid BodyHostControl => BodyHost;

    /// <summary>THEME-MACOS-LAYOUTS-1: panel that currently holds the four navigation buttons.</summary>
    public StackPanel DockNavPanelControl => DockNavPanel;

    public StackPanel SidebarNavPanelControl => SidebarNavPanel;

    /// <summary>THEME-MACOS-LAYOUTS-1: layout profile currently applied to the shell (kind + geometry).</summary>
    public LegacyLayoutProfile Layout => _layout;

    public LegacyLayoutKind CurrentLayout => _layout.Kind;

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
        UpdateNavVisuals();

        if (string.Equals(page, "reader", StringComparison.Ordinal))
        {
            // READER-LIBRARY-WIRE-1 AC1: entering the reader loads the real library book (fixtures stay as fallback).
            _ = EnsureReaderLoadedAsync();
        }

        if (string.Equals(page, "workbench", StringComparison.Ordinal))
        {
            // READER-WORKBENCH-1 AC1: entering the workbench loads the real book → chapter → page
            // chain and the Core region projection (no-op until the Host is ready).
            _ = Workbench.EnsureLoadedAsync();
        }

        if (string.Equals(page, "settings", StringComparison.Ordinal))
        {
            // CREDENTIAL-UI-1 AC2 / SETTINGS-PROFILE-UI-1: refresh credential states and profile lists
            // every time settings opens.
            _ = Settings.RefreshCredentialsAsync();
            _ = Settings.RefreshProfilesAsync();
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
        ApplyWindowChrome();
        UpdateNavVisuals();
        _status.Foreground = LegacyChrome.Brush("TextSecondary");
    }

    /// <summary>
    /// THEME-MACOS-1 / THEME-MACOS-LAYOUTS-1: macOS-only window chrome — show the three traffic lights and
    /// paint the title-bar strip with the pack's HeaderBg token. Every non-macOS pack keeps the legacy title
    /// bar untouched so the existing six themes look exactly as before. The Dock / Sidebar hosts get the
    /// pack's chrome surfaces (they are only visible when the active pack asks for those layouts).
    /// </summary>
    private void ApplyWindowChrome()
    {
        var macChrome = false; // V11R-C-3: macOS pack chrome retired with the legacy theme system.
        TrafficLights.IsVisible = macChrome;
        TitleBar.Background = macChrome ? LegacyChrome.Brush("HeaderBg") : null;
        SidebarHost.Background = LegacyChrome.Brush(LegacyChrome.SidebarBackground);
        SidebarHost.BorderBrush = LegacyChrome.Brush("CardBorder");
        DockHost.Background = LegacyChrome.Brush(LegacyChrome.DockBackground);
        DockHost.BorderBrush = LegacyChrome.Brush("CardBorder");
    }

    /// <summary>THEME-MACOS-1 AC1: true when the macOS pack's traffic lights are currently shown.</summary>
    public bool AreTrafficLightsVisible => TrafficLights.IsVisible;

    public BookshelfPage BookshelfPageControl => (BookshelfPage)_pages["bookshelf"];

    /// <summary>
    /// V11R-C-3: the legacy pack cycle is retired. The legacy shell keeps a single fixed profile and only
    /// toggles the light/dark appearance (degraded but startable, as agreed for --shell=legacy).
    /// </summary>
    public void CycleTheme()
    {
        if (Application.Current is { } application)
        {
            var target = application.ActualThemeVariant == ThemeVariant.Dark
                ? ThemeVariant.Light
                : ThemeVariant.Dark;
            ApplyAppearance(target);
        }
    }

    /// <summary>
    /// C-3-I1: the legacy shell's appearance switch must move the DesignSystem palette, not only the
    /// Avalonia theme variant. Without this the window kept the previous palette while text colours
    /// followed the new variant. The manager is shared with the v2 shell; a null manager only happens in
    /// standalone legacy tests, where the variant remains the fallback.
    /// </summary>
    private void ApplyAppearance(ThemeVariant variant)
    {
        if (Application.Current is not { } application)
        {
            return;
        }

        application.RequestedThemeVariant = variant;
        SyncDesignSystemAppearance(variant);
        OnThemeApplied();
    }

    private void SyncDesignSystemAppearance(ThemeVariant? variant)
    {
        if (_themeManager is null || variant is null || variant == ThemeVariant.Default)
        {
            return;
        }

        var appearance = variant == ThemeVariant.Light ? DesignSystemAppearance.Light : DesignSystemAppearance.Dark;
        if (!_themeManager.SetAppearance(appearance))
        {
            System.Diagnostics.Trace.TraceWarning(
                $"legacy shell could not sync DesignSystem palette: {_themeManager.LastError}");
        }
    }

    /// <summary>Re-applies the fixed legacy chrome after an appearance change.</summary>
    public void OnThemeApplied()
    {
        SyncDesignSystemAppearance(Application.Current?.RequestedThemeVariant);
        ApplyTheme();
        InvalidateVisual();
    }

    /// <summary>
    /// THEME-MACOS-LAYOUTS-1: applies the active pack's <see cref="LegacyLayoutProfile"/> to the shell and to the
    /// two code-built pages. The four nav buttons keep their instances (and their click handlers) and are
    /// moved between the three pre-built hosts, because Avalonia allows one visual parent per control.
    /// </summary>
    public void ApplyLayout()
    {
        var profile = LegacyChrome.Current.Layout;
        _layout = profile;

        foreach (var key in _navOrder)
        {
            DetachFromParent(_navButtons[key]);
        }

        var host = profile.Nav switch
        {
            LegacyNavPlacement.Dock => (Panel)DockNavPanel,
            LegacyNavPlacement.Sidebar => SidebarNavPanel,
            _ => NavPanel,
        };
        foreach (var key in _navOrder)
        {
            StyleNavVisual(key, profile);
            host.Children.Add(_navButtons[key]);
        }

        NavPanel.IsVisible = profile.Nav == LegacyNavPlacement.TitleBar;
        DockHost.IsVisible = profile.UsesDock;
        SidebarHost.IsVisible = profile.UsesSidebar;
        DockHost.Height = profile.DockHeight > 0 ? profile.DockHeight : DockHost.Height;
        BodyHost.ColumnDefinitions[0].Width = new GridLength(profile.UsesSidebar ? profile.SidebarWidth : 0);
        if (profile.UsesSidebar)
        {
            MoveBrandToSidebar();
        }
        else
        {
            MoveBrandToTitleBar();
        }

        BookshelfPageControl.ApplyLayout(profile);
        Settings.ApplyLayout(profile);
        // The floating Dock overlays the page host, so the host itself reserves the Dock band: no page can
        // slide under the capsule (this is what the Launchpad profile's bottom inset is for).
        PageHost.Margin = new Thickness(0, 0, 0, profile.UsesDock ? profile.LaunchpadBottomInset : 0);
        ApplyTheme();
        InvalidateMeasure();
        InvalidateVisual();
    }

    /// <summary>Moves the traffic-lights / brand block into the Split sidebar (Finder-like chrome).</summary>
    private void MoveBrandToSidebar()
    {
        if (ReferenceEquals(TitleBrandPanel.Parent, SidebarBrand))
        {
            return;
        }

        DetachFromParent(TitleBrandPanel);
        TitleBrandPanel.Margin = new Thickness(0);
        SidebarBrand.Children.Insert(0, TitleBrandPanel);
    }

    /// <summary>Restores the traffic-lights / brand block to the title bar (Sonoma / Launchpad).</summary>
    private void MoveBrandToTitleBar()
    {
        if (ReferenceEquals(TitleBrandPanel.Parent, TitleBar))
        {
            return;
        }

        DetachFromParent(TitleBrandPanel);
        TitleBrandPanel.Margin = new Thickness(16, 0, 0, 0);
        Grid.SetColumn(TitleBrandPanel, 0);
        TitleBar.Children.Insert(0, TitleBrandPanel);
    }

    /// <summary>
    /// Per-layout navigation button geometry: Sonoma keeps the THEME-MACOS-1 pill, Launchpad uses an
    /// icon-over-label Dock tile, Split uses a full-width sidebar row.
    /// </summary>
    private void StyleNavVisual(string key, LegacyLayoutProfile profile)
    {
        if (!_navVisuals.TryGetValue(key, out var visual))
        {
            return;
        }

        switch (profile.Nav)
        {
            case LegacyNavPlacement.Dock:
                visual.Content.Orientation = Avalonia.Layout.Orientation.Vertical;
                visual.Content.Spacing = 3;
                visual.Content.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center;
                visual.Icon.FontSize = 18;
                visual.Label.FontSize = 11;
                visual.Button.Width = 76;
                visual.Button.Height = 54;
                visual.Button.Padding = new Thickness(4, 4);
                visual.Button.CornerRadius = new CornerRadius(14);
                visual.Button.HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center;
                visual.Button.VerticalContentAlignment = Avalonia.Layout.VerticalAlignment.Center;
                visual.Button.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center;
                break;
            case LegacyNavPlacement.Sidebar:
                visual.Content.Orientation = Avalonia.Layout.Orientation.Horizontal;
                visual.Content.Spacing = 10;
                visual.Content.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left;
                visual.Icon.FontSize = 14;
                visual.Label.FontSize = 13;
                visual.Button.Width = double.NaN;
                visual.Button.Height = double.NaN;
                visual.Button.Padding = new Thickness(12, 9);
                visual.Button.CornerRadius = new CornerRadius(9);
                visual.Button.HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Left;
                visual.Button.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch;
                break;
            default:
                visual.Content.Orientation = Avalonia.Layout.Orientation.Horizontal;
                visual.Content.Spacing = 6;
                visual.Content.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left;
                visual.Icon.FontSize = 13;
                visual.Label.FontSize = 13;
                visual.Button.Width = double.NaN;
                visual.Button.Height = double.NaN;
                visual.Button.Padding = new Thickness(14, 6);
                visual.Button.CornerRadius = new CornerRadius(9);
                visual.Button.HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center;
                visual.Button.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left;
                break;
        }
    }

    /// <summary>Paints the four nav buttons for the active layout + selected page (single source of truth).</summary>
    private void UpdateNavVisuals()
    {
        var chromeOnly = _layout.Nav is LegacyNavPlacement.Dock or LegacyNavPlacement.Sidebar;
        foreach (var pair in _navButtons)
        {
            var active = pair.Key == CurrentPage;
            pair.Value.Background = active
                ? LegacyChrome.Brush("NavActiveBg")
                : chromeOnly ? Brushes.Transparent : LegacyChrome.Brush("NavBg");
            pair.Value.Foreground = LegacyChrome.Brush(active ? "NavActiveText" : "TextPrimary");
        }
    }

    private static void DetachFromParent(Control control)
    {
        if (control.Parent is Panel panel)
        {
            panel.Children.Remove(control);
        }
    }

    private void AddNav(string key, string label, string iconKey)
    {
        var icon = new TextBlock
        {
            Text = Application.Current?.TryGetResource(iconKey, null, out var glyph) == true
                ? glyph?.ToString()
                : string.Empty,
            FontSize = 13,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        var labelBlock = new TextBlock
        {
            Text = label,
            FontSize = 13,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        var content = new StackPanel
        {
            Orientation = Avalonia.Layout.Orientation.Horizontal,
            Spacing = 6,
            Children = { icon, labelBlock },
        };
        var button = new Button
        {
            Content = content,
            Padding = new Thickness(14, 6),
            CornerRadius = new CornerRadius(9),
            Background = LegacyChrome.Brush("NavBg"),
            Foreground = LegacyChrome.Brush("TextPrimary"),
            Focusable = true,
        };
        button.Name = "Nav_" + key;
        button.Click += (_, _) => Navigate(key);
        _navButtons[key] = button;
        _navVisuals[key] = new NavVisual(button, content, icon, labelBlock);
        _navOrder.Add(key);
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

            // READER-WORKBENCH-1 AC1: a `--page=workbench` startup navigation happens before the Host
            // starts, so the real region load is re-attempted once the Host is ready.
            if (string.Equals(CurrentPage, "workbench", StringComparison.Ordinal))
            {
                await Workbench.EnsureLoadedAsync(CancellationToken.None);
            }

            // CREDENTIAL-UI-1 AC2: configured/missing states once the Host is ready.
            await Settings.RefreshCredentialsAsync();
            // SETTINGS-PROFILE-UI-1: provider/network profile lists once the Host is ready.
            await Settings.RefreshProfilesAsync();
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




