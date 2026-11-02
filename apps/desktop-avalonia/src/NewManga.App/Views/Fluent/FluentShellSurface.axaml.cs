using Avalonia;
using Avalonia.Animation;
using Avalonia.Animation.Easings;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
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
public partial class FluentShellSurface : UserControl, IPresentationExitState
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
    private IInputElement? _focusBeforeDialog;
    private bool _motionNavigationEnabled;
    private MotionTimingProfile? _motionTimings;
    private bool _textInputFocused;

    public FluentShellSurface() : this(null, null) { }

    public FluentShellSurface(
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
        // I-12：错误卡「打开控制台」入口走 shell 空间导航（进入 Console 空间，含导航/空间选中态更新）。
        var openConsole = () => NavigateSpace(SpaceId.Console);
        _shelfView = new ShelfPageView(_shelfModel, picker, OpenReader, OpenWorkbench, openConsole);
        Require<Button>("NavRecycle").Click += (_, _) => _shelfView.OpenRecycleDrawer();
        Require<Button>("NavImport").Click += async (_, _) => await _shelfView.ImportFilesAsync();
        _workbenchView = new WorkbenchPageView(_workbenchModel, () => Navigate(FluentPage.Library), openConsole);
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
        ApplyResponsiveBand(ShellLayout.BreakpointFull);
        ApplyMotion(appearance?.Settings ?? AppearanceDefaults.Settings);
        // I-5: repeat the frozen motion resolution whenever the single appearance writer changes the
        // settings dome (mode/categories), so runtime changes take effect without recreating the tree.
        if (Appearance is not null)
        {
            Appearance.Changed += OnAppearanceChangedForMotion;
        }

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
    public ReaderPageView ReaderView => _readerView;
    public SettingsPageView SettingsView => _settingsView;
    public FluentResponsiveBand ResponsiveBand { get; private set; }

    /// <summary>Applies the hosting window viewport width to the responsive bands.</summary>
    public void SetViewportWidth(double width) { ApplyResponsiveBand(width); UpdateStatus(); }

    /// <summary>Raised when the surface wants the hosting window to toggle full screen.</summary>
    public Action<bool>? FullScreenRequested { get; set; }

    /// <summary>Raised after the visible page changed (the stable window uses it to keep chrome consistent).</summary>
    public event EventHandler<FluentPage>? CurrentPageChanged;

    /// <summary>
    /// Leaves full-screen reading without user input (e.g. the stable window switches to another frontend),
    /// keeping the reader state and the hosting window state consistent.
    /// </summary>
    public void ExitFullScreen()
    {
        if (!_readerModel.IsFullScreen)
        {
            return;
        }

        _readerModel.IsFullScreen = false;
        FullScreenRequested?.Invoke(false);
    }
    public Button? NavigationButton(FluentPage page) => _navButtons.GetValueOrDefault(page);

    /// <summary>FEA-07 AC2: the host checks real content state before closing the stable window.</summary>
    public bool HasUnsavedEdits => _settingsModel.IsDirty;

    /// <summary>FEA-07 AC2: a running workbench job blocks process exit.</summary>
    public bool HasActiveRuns => _workbenchModel.State == FluentPageState.Running;

    public static FluentResponsiveBand GetResponsiveBand(double width) =>
        width < ShellLayout.BreakpointNarrow ? FluentResponsiveBand.Narrow :
        width < ShellLayout.BreakpointCompact ? FluentResponsiveBand.Medium :
        width < ShellLayout.BreakpointFull ? FluentResponsiveBand.Compact :
        FluentResponsiveBand.Full;

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
            CurrentPageChanged?.Invoke(this, _currentPage);
            return;
        }

        // I-3：设置页有未保存修改时，导航被挂起，先走三分支离开确认（保存并离开/丢弃并离开/取消）。
        if (_currentPage == FluentPage.Settings && page != FluentPage.Settings && _settingsModel.IsDirty)
        {
            _settingsView.TryBeginLeave(() => Navigate(page));
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
        CurrentPageChanged?.Invoke(this, _currentPage);
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
        // I-3：空间切换在设置页 dirty 时同样先走三分支离开确认；确认（dirty 清零）后才执行完整空间进入序列，
        // 保证 Console/Studio 的空间选中态与页签状态不会因确认挂起而丢失。
        if (_currentPage == FluentPage.Settings && _settingsModel.IsDirty)
        {
            _settingsView.TryBeginLeave(() => NavigateSpace(space));
            return;
        }

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
        FullScreenRequested?.Invoke(enabled);
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
            case ShellCommandIds.SurfaceBack: HandleSurfaceBack(); break;
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

    /// <summary>
    /// I-3（设计 03 §2「Esc=关闭当前浮层（若有），否则返回上一级」+ 08 §5）的 Esc 优先级：
    /// 设置页浮层（离开确认/普通确认）打开时 Esc=取消浮层；设置页 dirty 且无浮层时 Esc=触发离开确认流；
    /// 其余保持既有 surface.back 语义（shell 浮层/阅读器返回）。
    /// </summary>
    private void HandleSurfaceBack()
    {
        if (_currentPage == FluentPage.Settings)
        {
            if (_settingsView.LeaveConfirmationVisible)
            {
                _settingsView.CancelLeave();
                return;
            }

            if (_settingsView.HasOpenConfirmation)
            {
                _settingsView.CancelConfirmation();
                return;
            }

            if (_settingsModel.IsDirty)
            {
                // 页面内 Esc 触发离开流；确认后的离开目标为一级页（书架）。
                _settingsView.TryBeginLeave(() => Navigate(FluentPage.Library));
                return;
            }
        }

        CloseTopSurface();
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
        // I-11 (design 03 §3): remember the trigger so closing the overlay returns keyboard focus.
        _focusBeforeDialog = TopLevel.GetTopLevel(this)?.FocusManager?.GetFocusedElement();
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
            RestoreFocusAfterDialog();
            return;
        }
        if (_currentPage == FluentPage.Reader) CloseReader();
    }

    /// <summary>I-11: closing a shell overlay returns focus to the control that opened it.</summary>
    private void RestoreFocusAfterDialog()
    {
        var previous = _focusBeforeDialog;
        _focusBeforeDialog = null;
        if (previous is Control control && control.Focusable && control.IsEffectivelyEnabled && control.IsEffectivelyVisible)
        {
            control.Focus();
        }
    }

    private void ToggleTheme()
    {
        if (ThemeManager is null) return;
        var next = ThemeManager.Appearance == NewManga.DesignSystem.Theming.AppearanceMode.Dark
            ? NewManga.DesignSystem.Theming.AppearanceMode.Light
            : NewManga.DesignSystem.Theming.AppearanceMode.Dark;
        ThemeManager.SetAppearance(next);
    }

    private void OnAppearanceChangedForMotion(object? sender, EventArgs args)
    {
        // AppearanceCoordinator raises Changed after its atomic write, which may run on a pool thread;
        // motion application mutates the visual tree, so marshal it back to the UI thread when needed.
        if (Dispatcher.UIThread.CheckAccess())
        {
            ApplyMotion(Appearance?.Settings ?? AppearanceDefaults.Settings);
            return;
        }

        Dispatcher.UIThread.Post(() => ApplyMotion(Appearance?.Settings ?? AppearanceDefaults.Settings));
    }

    private void ApplyMotion(AppearanceSettings settings)
    {
        var resolution = new MotionResolver(new WindowsMotionPreferenceSource()).Resolve(settings).Settings;
        _motionNavigationEnabled = resolution.IsEnabled(MotionCategories.Navigation);
        // I-5: consume the frozen motion parameter table instead of hard-coded durations. The page host
        // fades for the resolved navigation duration; reduce/category-off resolves to 0ms (no transition).
        _motionTimings = MotionTimings.Resolve(resolution);
        ApplyNavigationTransition(_motionTimings);
        ThemeManager?.SetReducedMotion(!resolution.Enabled);
        Classes.Set("motion-navigation", _motionNavigationEnabled);
        // I-5: feedback keeps its colour change but owns a transition only when motion is enabled;
        // reduce/category-off removes the class so the colour applies instantly.
        Classes.Set("motion-feedback", _motionTimings.FeedbackHoverMilliseconds > 0);
        ApplyFeedbackTransitions(_motionTimings);
        Classes.Set("motion-reduced", !resolution.Enabled);
        // I-10：reduce 下阅读器工具条直接切换、无淡出过渡（07:23）。
        _readerModel.AreToolBarsReducedMotion = !resolution.Enabled;
    }

    private void ApplyNavigationTransition(MotionTimingProfile timings)
    {
        var duration = timings.NavigationPageMilliseconds;
        _pageHost.Transitions = duration > 0
            ? new Transitions
            {
                new DoubleTransition
                {
                    Property = OpacityProperty,
                    Duration = TimeSpan.FromMilliseconds(duration),
                    Easing = new CubicEaseOut(),
                },
            }
            : null;
    }

    /// <summary>
    /// I-5 (design 02 §2.2 判据③): feedback colour changes own a transition only while motion is enabled;
    /// reduce / category-off clears it, leaving the colour change instant. Applied on attach and on every
    /// re-resolve so runtime settings changes take effect without recreating the content tree.
    /// </summary>
    private void ApplyFeedbackTransitions(MotionTimingProfile? timings)
    {
        var enabled = timings is not null && timings.FeedbackHoverMilliseconds > 0;
        Transitions? transitions = enabled
            ? new Transitions
            {
                new BrushTransition
                {
                    Property = TemplatedControl.BackgroundProperty,
                    Duration = TimeSpan.FromMilliseconds(timings!.FeedbackHoverMilliseconds),
                    Easing = new CubicEaseOut(),
                },
            }
            : null;

        foreach (var button in this.GetVisualDescendants().OfType<Button>())
        {
            button.Transitions = transitions;
        }
    }

    protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
    {
        base.OnAttachedToVisualTree(e);
        ApplyFeedbackTransitions(_motionTimings);
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
