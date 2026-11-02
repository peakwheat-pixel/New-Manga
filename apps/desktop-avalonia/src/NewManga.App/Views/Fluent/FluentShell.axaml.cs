using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.Fluent;
using NewManga.CoreClient;
using NewManga.Appearance;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;
using FluentReaderViewModel = NewManga.App.ViewModels.Fluent.ReaderViewModel;

namespace NewManga.App.Views.Fluent;

/// <summary>Four content surfaces hosted by the FEA Fluent shell.</summary>
public enum FluentPage
{
    Library,
    Workbench,
    Reader,
    Settings,
}

/// <summary>Responsive bands resolved from the frozen 1024/1280/1600 token breakpoints.</summary>
public enum FluentResponsiveBand
{
    Narrow,
    Medium,
    Compact,
    Full,
}

/// <summary>Fluent frontend shell; all application services are the shared composition-root instances.</summary>
public partial class FluentShell : Window
{
    public static IReadOnlyList<FluentPage> Pages { get; } =
        [FluentPage.Library, FluentPage.Workbench, FluentPage.Reader, FluentPage.Settings];

    private readonly string _frontendId;
    private readonly Dictionary<FluentPage, Button> _navButtons = new();
    private readonly ShelfViewModel _shelfModel;
    private readonly WorkbenchViewModel _workbenchModel;
    private readonly FluentReaderViewModel _readerModel;
    private readonly SettingsViewModel _settingsModel;
    private readonly ShelfPageView _shelfView;
    private readonly WorkbenchPageView _workbenchView;
    private readonly ReaderPageView _readerView;
    private readonly SettingsPageView _settingsView;
    private readonly ContentControl _pageHost;
    private readonly Border _navRail;
    private readonly Border _modalHost;
    private readonly TextBlock _statusText;
    private readonly TextBlock _breakpointText;
    private readonly Button _spaceLibrary;
    private readonly Button _spaceStudio;
    private readonly Button _spaceConsole;
    private readonly KeyMap _keyMap = KeyMap.Default;
    private SpaceId _currentSpace = SpaceId.Library;
    private StudioMode _studioMode = StudioMode.Page;
    private FluentPage _pageBeforeReader = FluentPage.Library;
    private FluentPage _currentPage;
    private Control? _activeDialog;
    private bool _motionNavigationEnabled;
    private bool _textInputFocused;

    public FluentShell() : this(null, null) { }

    public FluentShell(
        AppOptions? options = null,
        FrontendSelection? selection = null,
        IHostController? host = null,
        AppearanceCoordinator? appearance = null,
        DesignSystemThemeManager? themeManager = null)
    {
        HostController = host;
        Appearance = appearance;
        ThemeManager = themeManager;
        InitializeComponent();
        KeyMap.EnsureValid(_keyMap);

        _frontendId = selection?.EffectiveFrontendId ?? FrontendSelector.CurrentV2FrontendId;
        Width = options?.WindowWidth ?? 1180;
        Height = options?.WindowHeight ?? 780;
        MinWidth = ShellLayout.BreakpointNarrow;
        _pageHost = Require<ContentControl>("FluentPageHost");
        _navRail = Require<Border>("FluentNavRail");
        _modalHost = Require<Border>("FluentModalHost");
        _statusText = Require<TextBlock>("FluentStatusText");
        _breakpointText = Require<TextBlock>("FluentBreakpointText");
        _spaceLibrary = Require<Button>("SpaceLibrary");
        _spaceStudio = Require<Button>("SpaceStudio");
        _spaceConsole = Require<Button>("SpaceConsole");

        _navButtons[FluentPage.Library] = Require<Button>("NavLibrary");
        _navButtons[FluentPage.Workbench] = Require<Button>("NavWorkbench");
        _navButtons[FluentPage.Settings] = Require<Button>("NavSettings");
        foreach (var pair in _navButtons)
        {
            var page = pair.Key;
            pair.Value.Click += (_, _) => Navigate(page);
        }
        _shelfModel = new ShelfViewModel(host);
        _workbenchModel = new WorkbenchViewModel(host, Guid.NewGuid().ToString("N"));
        _readerModel = new FluentReaderViewModel(host);
        _settingsModel = new SettingsViewModel(host, appearance, themeManager);
        var picker = new AvaloniaFilePickerGateway(_ => TopLevel.GetTopLevel(this));
        _shelfView = new ShelfPageView(_shelfModel, picker, OpenReader, OpenWorkbench);
        Require<Button>("NavRecycle").Click += (_, _) => _shelfView.OpenRecycleDrawer();
        Require<Button>("NavImport").Click += async (_, _) => await _shelfView.ImportFilesAsync();
        _workbenchView = new WorkbenchPageView(_workbenchModel, () => Navigate(FluentPage.Library));
        _workbenchView.TabChanged += tab =>
        {
            if (tab == WorkbenchViewTab.Page) _studioMode = StudioMode.Page;
            else if (tab == WorkbenchViewTab.Batch) _studioMode = StudioMode.Batch;
        };
        _readerView = new ReaderPageView(_readerModel, CloseReader, SetFullScreen);
        _settingsView = new SettingsPageView(_settingsModel);

        Require<TextBlock>("FluentFrontendLabel").Text = $"Fluent frontend · {_frontendId}";
        _spaceLibrary.Click += (_, _) => NavigateSpace(SpaceId.Library);
        _spaceStudio.Click += (_, _) => NavigateSpace(SpaceId.Studio);
        _spaceConsole.Click += (_, _) => NavigateSpace(SpaceId.Console);
        Require<Button>("CommandPaletteButton").Click += (_, _) => OpenCommandPalette();
        Require<Button>("SettingsCommandButton").Click += (_, _) => Navigate(FluentPage.Settings);
        Require<Button>("HelpButton").Click += (_, _) => OpenShortcutHelp();
        SizeChanged += (_, args) => ApplyResponsiveBand(args.NewSize.Width);
        AddHandler(KeyDownEvent, OnPreviewKeyDown, RoutingStrategies.Tunnel);
        ApplyResponsiveBand(Width);
        ApplyMotion(appearance?.Settings ?? AppearanceDefaults.Settings);
        Navigate(FluentPage.Library);
        if (!string.IsNullOrWhiteSpace(options?.StartupPage)) Navigate(options.StartupPage);
    }

    public IHostController? HostController { get; }
    public AppearanceCoordinator? Appearance { get; }
    public DesignSystemThemeManager? ThemeManager { get; }
    public FluentPage CurrentPage => _currentPage;
    public string CurrentPageTitle => PageTitle(_currentPage);
    public string CurrentPlaceholderText => _currentPage switch
    {
        FluentPage.Library => "书架：作品网格、筛选、章节和页面预览。",
        FluentPage.Workbench => "工作台：页面画布、区域检查器和批量状态矩阵。",
        FluentPage.Reader => "阅读器：页导航、缩放、阅读进度和方向设置。",
        FluentPage.Settings => "设置：外观、Provider、网络、备份与关于。",
        _ => string.Empty,
    };
    public string StatusText => _statusText.Text ?? string.Empty;
    public KeyMap ShellKeyMap => _keyMap;
    public ShelfViewModel ShelfViewModel => _shelfModel;
    public WorkbenchViewModel WorkbenchViewModel => _workbenchModel;
    public FluentReaderViewModel ReaderViewModel => _readerModel;
    public SettingsViewModel SettingsViewModel => _settingsModel;
    public ShelfPageView ShelfView => _shelfView;
    public WorkbenchPageView WorkbenchView => _workbenchView;
    public FluentResponsiveBand ResponsiveBand { get; private set; }
    public Button? NavigationButton(FluentPage page) => _navButtons.GetValueOrDefault(page);

    public static FluentResponsiveBand GetResponsiveBand(double width) =>
        width < ShellLayout.BreakpointNarrow ? FluentResponsiveBand.Narrow :
        width < ShellLayout.BreakpointCompact ? FluentResponsiveBand.Medium :
        width < ShellLayout.BreakpointFull ? FluentResponsiveBand.Compact :
        FluentResponsiveBand.Full;

    public static FluentShell CreateRoot(
        AppOptions? options = null,
        FrontendSelection? selection = null,
        IHostController? host = null,
        AppearanceCoordinator? appearance = null,
        DesignSystemThemeManager? themeManager = null)
    {
        var shell = new FluentShell(options, selection, host, appearance, themeManager);
        var material = WindowMaterial.ForCurrentOs();
        shell.TransparencyLevelHint = material.Hints.Select(hint => hint switch
        {
            "Mica" => WindowTransparencyLevel.Mica,
            "Blur" => WindowTransparencyLevel.Blur,
            _ => WindowTransparencyLevel.None,
        }).ToArray();
        return shell;
    }

    public void Navigate(FluentPage page)
    {
        if (page == FluentPage.Reader)
        {
            if (_currentPage != FluentPage.Reader) _pageBeforeReader = _currentPage;
            _currentPage = FluentPage.Reader;
            _pageHost.Content = _readerView;
            UpdateNavigationItems();
            UpdateNavSelection(_pageBeforeReader);
            UpdateStatus();
            return;
        }

        _currentPage = page;
        _currentSpace = page switch
        {
            FluentPage.Library => SpaceId.Library,
            FluentPage.Workbench => SpaceId.Studio,
            _ => _currentSpace,
        };
        _pageHost.Content = page switch
        {
            FluentPage.Library => _shelfView,
            FluentPage.Workbench => _workbenchView,
            FluentPage.Settings => _settingsView,
            _ => _shelfView,
        };
        UpdateNavigationItems();
        UpdateNavSelection(page);
        UpdateSpaceSelection();
        if (page == FluentPage.Workbench)
        {
            _studioMode = StudioMode.Page;
            _workbenchView.SelectPageTab();
        }
        UpdateStatus();
    }

    public bool Navigate(string page)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(page);
        var target = page.ToLowerInvariant() switch
        {
            "bookshelf" or "library" => FluentPage.Library,
            "workbench" or "studio" => FluentPage.Workbench,
            "reader" => FluentPage.Reader,
            "settings" => FluentPage.Settings,
            "console" => null,
            _ => (FluentPage?)null,
        };
        if (page.Equals("console", StringComparison.OrdinalIgnoreCase))
        {
            NavigateSpace(SpaceId.Console);
            return true;
        }
        if (target is not { } resolved) return false;
        Navigate(resolved);
        return true;
    }

    public bool HandleKeyForTest(Key key, KeyModifiers modifiers, bool textInputFocused = false)
    {
        if (textInputFocused && IsPlainTypingKey(key, modifiers)) return false;
        if (_keyMap.TryMatch(key, modifiers, _currentSpace, _studioMode, out var command))
        {
            ExecuteCommand(command);
            return true;
        }

        var noModifiers = (modifiers & (KeyModifiers.Control | KeyModifiers.Shift | KeyModifiers.Alt | KeyModifiers.Meta)) == KeyModifiers.None;
        if (!noModifiers || _currentPage != FluentPage.Workbench ||
            _currentSpace is not (SpaceId.Studio or SpaceId.Console) ||
            key is not (Key.OemOpenBrackets or Key.OemCloseBrackets))
        {
            return false;
        }

        var pageCommand = ShellCommands.Find(key == Key.OemCloseBrackets
            ? ShellCommandIds.PageNext
            : ShellCommandIds.PagePrevious);
        if (pageCommand is null) return false;
        ExecuteCommand(pageCommand);
        return true;
    }

    private void NavigateSpace(SpaceId space)
    {
        if (space == SpaceId.Console)
        {
            Navigate(FluentPage.Workbench);
            _currentSpace = SpaceId.Console;
            _workbenchView.SelectConsoleTab();
            UpdateNavigationItems();
            UpdateSpaceSelection();
            UpdateStatus();
            return;
        }

        _currentSpace = space;
        Navigate(space == SpaceId.Library ? FluentPage.Library : FluentPage.Workbench);
        if (space == SpaceId.Studio)
        {
            _studioMode = StudioMode.Page;
            _workbenchView.SelectPageTab();
        }
    }

    private void UpdateNavSelection(FluentPage page)
    {
        foreach (var pair in _navButtons) pair.Value.Classes.Set("selected", pair.Key == page);
    }

    private void UpdateNavigationItems()
    {
        var inLibrary = _currentSpace == SpaceId.Library;
        var inStudio = _currentSpace == SpaceId.Studio;
        Require<Button>("NavLibrary").IsVisible = inLibrary;
        Require<Button>("NavRecycle").IsVisible = inLibrary;
        Require<Button>("NavImport").IsVisible = inLibrary;
        Require<Button>("NavWorkbench").IsVisible = inStudio || _currentSpace == SpaceId.Console;
        Require<Button>("NavSettings").IsVisible = true;
    }

    private void UpdateSpaceSelection()
    {
        _spaceLibrary.Classes.Set("selected", _currentSpace == SpaceId.Library);
        _spaceStudio.Classes.Set("selected", _currentSpace == SpaceId.Studio);
        _spaceConsole.Classes.Set("selected", _currentSpace == SpaceId.Console);
    }

    private void ApplyResponsiveBand(double width)
    {
        ResponsiveBand = GetResponsiveBand(width);
        _navRail.IsVisible = ResponsiveBand != FluentResponsiveBand.Narrow;
        _breakpointText.Text = ResponsiveBand switch
        {
            FluentResponsiveBand.Narrow => "Narrow · <1024",
            FluentResponsiveBand.Medium => "Medium · 1024–1279",
            FluentResponsiveBand.Compact => "Compact · 1280–1599",
            _ => "Full · ≥1600",
        };
    }

    private void UpdateStatus()
    {
        _statusText.Text = $"Fluent · {_frontendId} · {PageTitle(_currentPage)} · {ResponsiveBand}";
    }

    private void OpenReader(BookSummary book, ChapterSummary chapter)
    {
        _pageBeforeReader = _currentPage;
        Navigate(FluentPage.Reader);
        _ = _readerView.LoadAsync(book.BookId, chapter.ChapterId);
    }

    private void OpenWorkbench(BookSummary book, ChapterSummary chapter)
    {
        Navigate(FluentPage.Workbench);
        _ = _workbenchView.LoadAsync(chapter.ChapterId);
    }

    private void CloseReader() => Navigate(_pageBeforeReader == FluentPage.Reader ? FluentPage.Library : _pageBeforeReader);

    private void SetFullScreen(bool enabled)
    {
        WindowState = enabled ? WindowState.FullScreen : WindowState.Normal;
    }

    private void OnPreviewKeyDown(object? sender, KeyEventArgs args)
    {
        var focused = TopLevel.GetTopLevel(this)?.FocusManager?.GetFocusedElement();
        _textInputFocused = focused is TextBox;
        if (HandleKeyForTest(args.Key, args.KeyModifiers, _textInputFocused)) args.Handled = true;
    }

    private void ExecuteCommand(ShellCommandDefinition command)
    {
        if (!command.IsAvailable)
        {
            _statusText.Text = command.UnavailableReason ?? $"“{command.Title}”当前不可用。";
            return;
        }

        switch (command.Id)
        {
            case ShellCommandIds.SpaceLibrary: NavigateSpace(SpaceId.Library); break;
            case ShellCommandIds.SpaceStudio: NavigateSpace(SpaceId.Studio); break;
            case ShellCommandIds.SpaceConsole: NavigateSpace(SpaceId.Console); break;
            case ShellCommandIds.StudioModeToggle: _studioMode = _studioMode == StudioMode.Page ? StudioMode.Batch : StudioMode.Page; _workbenchView.SelectTab(_studioMode == StudioMode.Batch ? WorkbenchViewTab.Batch : WorkbenchViewTab.Page); UpdateStatus(); break;
            case ShellCommandIds.CommandPalette: OpenCommandPalette(); break;
            case ShellCommandIds.QuickJump: OpenCommandPalette("快速跳转"); break;
            case ShellCommandIds.ThemeStudio: _settingsModel.SelectedGroup = SettingsGroupId.Appearance; Navigate(FluentPage.Settings); break;
            case ShellCommandIds.Help: OpenShortcutHelp(); break;
            case ShellCommandIds.SurfaceBack: CloseTopSurface(); break;
            case ShellCommandIds.ThemeToggle: ToggleTheme(); break;
            case ShellCommandIds.ObjectNext: _ = _shelfModel.MoveSelection(1); break;
            case ShellCommandIds.ObjectPrevious: _ = _shelfModel.MoveSelection(-1); break;
            case ShellCommandIds.PageNext: NavigatePage(1); break;
            case ShellCommandIds.PagePrevious: NavigatePage(-1); break;
            case ShellCommandIds.ChapterNext: _ = _shelfModel.MoveChapter(1); break;
            case ShellCommandIds.ChapterPrevious: _ = _shelfModel.MoveChapter(-1); break;
            case ShellCommandIds.LibraryRefresh: _ = _shelfModel.RefreshAsync(); break;
            case ShellCommandIds.LibraryImportFiles: _ = _shelfView.ImportFilesAsync(); break;
            case ShellCommandIds.LibraryImportFolder: _ = _shelfView.ImportFolderAsync(); break;
            case ShellCommandIds.LibraryRecycle: _shelfView.OpenRecycleDrawer(); break;
            case ShellCommandIds.LibraryNewBook: _shelfView.ShowNewBookDialog(); break;
            case ShellCommandIds.LibraryNewChapter: _shelfView.ShowNewChapterDialog(); break;
            case ShellCommandIds.LibraryOpenReader: _shelfView.OpenSelectedReader(); break;
            case ShellCommandIds.LibraryClearSelection: _shelfModel.ClearSelection(); break;
            case ShellCommandIds.StudioPage: _studioMode = StudioMode.Page; _workbenchView.SelectPageTab(); break;
            case ShellCommandIds.StudioBatch: _studioMode = StudioMode.Batch; _workbenchView.SelectTab(WorkbenchViewTab.Batch); break;
            default: _statusText.Text = $"“{command.Title}”尚无可调用操作。"; break;
        }
    }

    private void NavigatePage(int direction)
    {
        if (_currentPage == FluentPage.Workbench)
        {
            _workbenchView.MovePage(direction);
            return;
        }

        if (_currentPage == FluentPage.Reader || _currentSpace == SpaceId.Library)
        {
            _ = _readerModel.NavigateAsync(direction);
        }
    }

    private void OpenCommandPalette(string? initialQuery = null)
    {
        var search = new TextBox { Watermark = "输入命令名称", Text = initialQuery };
        AutomationProperties.SetName(search, "搜索命令");
        var list = new StackPanel { Classes = { "fluent-command-list" } };
        void RenderCommands()
        {
            list.Children.Clear();
            var query = search.Text ?? string.Empty;
            foreach (var command in ShellCommands.Definitions.Where(item =>
                         string.IsNullOrWhiteSpace(query) || item.Title.Contains(query, StringComparison.CurrentCultureIgnoreCase)))
            {
                var label = command.HasGesture ? $"{command.Title} · {command.GestureText}" : command.Title;
                if (!command.IsAvailable) label += " · 不可用";
                var button = new Button { Content = label, Classes = { "fluent-command-row" }, IsEnabled = command.IsAvailable };
                AutomationProperties.SetName(button, label);
                button.Click += (_, _) => { CloseTopSurface(); ExecuteCommand(command); };
                list.Children.Add(button);
            }
        }
        search.TextChanged += (_, _) => RenderCommands();
        RenderCommands();
        var scroll = new ScrollViewer { Content = list, VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Auto };
        OpenDialog("命令面板", new Control[] { search, scroll });
        search.Focus();
    }

    private void OpenShortcutHelp()
    {
        var rows = ShellCommands.Definitions.Where(item => item.HasGesture).Select(command =>
            (Control)new TextBlock
            {
                Text = $"{command.GestureText}  ·  {command.Title}",
                Classes = { "fluent-status-text" },
                TextWrapping = Avalonia.Media.TextWrapping.Wrap,
            }).ToArray();
        OpenDialog("键位速查", rows);
    }

    private void OpenDialog(string title, IEnumerable<Control> content)
    {
        var panel = new StackPanel { Classes = { "fluent-dialog-content" } };
        panel.Children.Add(new TextBlock { Text = title, Classes = { "fluent-page-title" } });
        foreach (var child in content) panel.Children.Add(child);
        panel.Children.Add(new Button { Content = "关闭", Classes = { "fluent-secondary" }, Command = null });
        var close = (Button)panel.Children[^1];
        close.Click += (_, _) => CloseTopSurface();
        var dialog = new FluentDialog { Child = panel, IsOpen = true, HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center, MaxWidth = ShellLayout.PaletteWidth };
        var scrim = new Border { Classes = { "fluent-modal-scrim" }, Child = dialog };
        scrim.PointerPressed += (_, args) =>
        {
            if (ReferenceEquals(args.Source, scrim)) CloseTopSurface();
        };
        _activeDialog = scrim;
        _modalHost.Child = scrim;
        _modalHost.IsVisible = true;
        _modalHost.Focus();
    }

    private void CloseTopSurface()
    {
        if (_modalHost.IsVisible)
        {
            _modalHost.IsVisible = false;
            _modalHost.Child = null;
            _activeDialog = null;
            return;
        }
        if (_currentPage == FluentPage.Reader) CloseReader();
    }

    private void ToggleTheme()
    {
        if (ThemeManager is null) return;
        var next = ThemeManager.Appearance == NewManga.DesignSystem.Theming.AppearanceMode.Dark
            ? NewManga.DesignSystem.Theming.AppearanceMode.Light
            : NewManga.DesignSystem.Theming.AppearanceMode.Dark;
        ThemeManager.SetAppearance(next);
    }

    private void ApplyMotion(AppearanceSettings settings)
    {
        var resolution = new MotionResolver(new WindowsMotionPreferenceSource()).Resolve(settings).Settings;
        _motionNavigationEnabled = resolution.IsEnabled(MotionCategories.Navigation);
        ThemeManager?.SetReducedMotion(!resolution.Enabled);
        Classes.Set("motion-navigation", _motionNavigationEnabled);
        Classes.Set("motion-reduced", !resolution.Enabled);
    }

    private static bool IsPlainTypingKey(Key key, KeyModifiers modifiers) =>
        (modifiers & (KeyModifiers.Control | KeyModifiers.Alt | KeyModifiers.Meta)) == 0 &&
        (key is >= Key.A and <= Key.Z or >= Key.D0 and <= Key.D9 or Key.Space or Key.OemMinus or Key.OemPlus or
            Key.OemComma or Key.OemPeriod or Key.OemOpenBrackets or Key.OemCloseBrackets or Key.Tab);

    private static string PageTitle(FluentPage page) => page switch
    {
        FluentPage.Library => "书架",
        FluentPage.Workbench => "工作台",
        FluentPage.Reader => "阅读器",
        FluentPage.Settings => "设置",
        _ => page.ToString(),
    };

    private T Require<T>(string name) where T : Control =>
        this.FindControl<T>(name) ?? throw new InvalidOperationException($"Fluent shell missing control '{name}'");
}
