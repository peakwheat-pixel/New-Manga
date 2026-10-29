using System.Collections.ObjectModel;
using Avalonia.Input;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Console;
using NewManga.App.ViewModels.V2.Library;
using NewManga.CoreClient;

namespace NewManga.App.ViewModels.V2.Shell;

/// <summary>
/// V11R-B-1: the new shell ViewModel (screen spec §1). Owns the TopBand chrome state, the command
/// palette / jump / help overlays, the confirmation modal and the space routing. All navigation
/// state lives in <see cref="ShellState"/>; the Library ViewModel instance is created exactly once
/// so switching spaces or Studio modes never rebuilds it and never loses context (AC2).
/// </summary>
public sealed class AppShellViewModel : ObservableObject
{
    private readonly IHostController _controller;
    private readonly KeyMap _keyMap = KeyMap.Default;
    private Task? _initialization;
    private bool _paletteOpen;
    private bool _jumpOpen;
    private bool _helpOpen;
    private bool _confirmOpen;
    private string _paletteQuery = string.Empty;
    private string _jumpQuery = string.Empty;
    private int _paletteIndex = -1;
    private int _jumpIndex = -1;
    private bool _isDarkTheme = true;
    private bool _isCompact;
    private bool _isNarrow;
    private string? _noticeText;
    private NmStatus _noticeStatus = NmStatus.Blocked;
    private ConfirmRequest? _confirm;

    public AppShellViewModel(IHostController controller, IFilePickerGateway? picker = null)
    {
        _controller = controller;
        State = new ShellState();
        RunMonitor = new RunStatusMonitor(controller);
        Library = new LibraryViewModel(controller, State, Notify, RequestConfirm, picker);
        Console = new ConsoleViewModel(
            controller,
            State,
            RunMonitor,
            Notify,
            RequestConfirm,
            () => IsDarkTheme,
            ToggleTheme,
            OpenThemeStudio,
            () => SwitchSpace(SpaceId.Studio));
        SpaceTabs = new[]
        {
            new SpaceTabItem(SpaceId.Library, "资料柜", "1", () => SwitchSpace(SpaceId.Library)),
            new SpaceTabItem(SpaceId.Studio, "工位", "2", () => SwitchSpace(SpaceId.Studio)),
            new SpaceTabItem(SpaceId.Console, "控制台", "3", () => SwitchSpace(SpaceId.Console)),
        };

        AttentionItems = new[]
        {
            new AttentionItem("pending", "待确认", "—", NmStatus.Queued, isWired: false, JumpToAttention),
            new AttentionItem("failed", "失败", "—", NmStatus.Failed, isWired: false, JumpToAttention),
            new AttentionItem("blocked", "阻塞", "—", NmStatus.Blocked, isWired: false, JumpToAttention),
            new AttentionItem("stale", "过期", "—", NmStatus.Stale, isWired: false, JumpToAttention),
        };

        LibrarySpaceCommand = new RelayCommand(() => SwitchSpace(SpaceId.Library));
        StudioSpaceCommand = new RelayCommand(() => SwitchSpace(SpaceId.Studio));
        ConsoleSpaceCommand = new RelayCommand(() => SwitchSpace(SpaceId.Console));
        ToggleStudioModeCommand = new RelayCommand(ToggleStudioMode);
        PageModeCommand = new RelayCommand(() =>
        {
            SwitchSpace(SpaceId.Studio);
            SetStudioMode(StudioMode.Page);
        });
        BatchModeCommand = new RelayCommand(() =>
        {
            SwitchSpace(SpaceId.Studio);
            SetStudioMode(StudioMode.Batch);
        });
        OpenPaletteCommand = new RelayCommand(OpenPalette);
        OpenJumpCommand = new RelayCommand(OpenJump);
        OpenHelpCommand = new RelayCommand(OpenHelp);
        CloseHelpCommand = new RelayCommand(CloseHelp);
        ToggleThemeCommand = new RelayCommand(ToggleTheme);
        DismissNoticeCommand = new RelayCommand(DismissNotice);
        ConfirmCommand = new RelayCommand(ConfirmNow);
        CancelConfirmCommand = new RelayCommand(CancelConfirm);
        OpenThemeStudioCommand = new RelayCommand(OpenThemeStudio);
        CloseThemeStudioCommand = new RelayCommand(CloseThemeStudio);

        State.SpaceChanged += (_, _) => RefreshChrome();
        State.WorkspacesChanged += (_, _) => RaiseWorkspaceChrome();
        State.ModeChanged += (_, _) => RefreshChrome();
        State.SelectionChanged += (_, _) => RefreshChrome();
        State.SurfaceChanged += (_, _) =>
        {
            OnPropertyChanged(nameof(IsReaderSurfaceVisible), nameof(IsThemeStudioOpen), nameof(IsOverlayOpen));
            RaiseWorkspaceChrome();
        };
        RunMonitor.Updated += (_, _) => RaiseRunChrome();
        Library.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(LibraryViewModel.SelectedChapter)
                or nameof(LibraryViewModel.SelectedBook)
                or nameof(LibraryViewModel.Pages)
                or nameof(LibraryViewModel.Chapters)
                or nameof(LibraryViewModel.DetailProgressText)
                or nameof(LibraryViewModel.SelectionCount))
            {
                RefreshChrome();
            }
        };
        Console.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName == nameof(ConsoleViewModel.SelectedSection))
            {
                RefreshChrome();
            }
        };
        Library.Reader.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName == nameof(ReaderOverlayViewModel.IsOpen))
            {
                SynchronizeReaderSurface();
            }
        };
        Library.ImportDock.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(ImportDockViewModel.IsRunning)
                or nameof(ImportDockViewModel.Summary))
            {
                UpdateStatusBand();
            }
        };

        RefreshChrome();
    }

    public ShellState State { get; }

    public LibraryViewModel Library { get; }

    public ConsoleViewModel Console { get; }

    public KeyMap KeyMap => _keyMap;

    public IReadOnlyList<SpaceTabItem> SpaceTabs { get; }

    public ObservableCollection<BreadcrumbItem> Breadcrumb { get; } = new();

    public IReadOnlyList<AttentionItem> AttentionItems { get; }

    public RelayCommand LibrarySpaceCommand { get; }

    public RelayCommand StudioSpaceCommand { get; }

    public RelayCommand ConsoleSpaceCommand { get; }

    public RelayCommand ToggleStudioModeCommand { get; }

    public RelayCommand PageModeCommand { get; }

    public RelayCommand BatchModeCommand { get; }

    public RelayCommand OpenPaletteCommand { get; }

    public RelayCommand OpenJumpCommand { get; }

    public RelayCommand OpenHelpCommand { get; }

    public RelayCommand CloseHelpCommand { get; }

    public RelayCommand ToggleThemeCommand { get; }

    public RelayCommand DismissNoticeCommand { get; }

    public RelayCommand ConfirmCommand { get; }

    public RelayCommand CancelConfirmCommand { get; }

    public RelayCommand OpenThemeStudioCommand { get; }

    public RelayCommand CloseThemeStudioCommand { get; }

    public Task Initialization => _initialization ??= InitializeCoreAsync();

    // ── Chrome ────────────────────────────────────────────────────────────────────────────

    public bool IsLibrarySpace => State.CurrentSpace == SpaceId.Library;

    public bool IsStudioSpace => State.CurrentSpace == SpaceId.Studio;

    public bool IsConsoleSpace => State.CurrentSpace == SpaceId.Console;

    public string StudioModeLabel => State.StudioMode == StudioMode.Page ? "页面" : "批次";

    public bool IsPageMode => State.StudioMode == StudioMode.Page;

    public bool IsBatchMode => State.StudioMode == StudioMode.Batch;

    public string ScopeText
    {
        get
        {
            if (State.Selection.MultiPageCount > 0)
            {
                return $"选中 {State.Selection.MultiPageCount} 页";
            }

            if (Library.SelectedChapter is { } chapter)
            {
                return $"本章 {Library.Pages.Count} 页 · {chapter.Title}";
            }

            if (Library.SelectedBook is { } book)
            {
                return $"作品《{book.Title}》（未选章节）";
            }

            return "未选择对象";
        }
    }

    public bool IsOverlayOpen => State.HasOverlay;

    public bool IsReaderSurfaceVisible => State.IsReaderOpen;

    public bool IsThemeStudioOpen => State.IsThemeStudioOpen;

    public string HostStatusText => _controller.Snapshot.State switch
    {
        HostViewState.Ready => "Host 就绪",
        HostViewState.Starting => "Host 启动中",
        HostViewState.AlreadyRunning => "Host 已运行",
        HostViewState.Failed => "Host 失败",
        _ => "Host 未知",
    };

    public bool IsHostReady => _controller.Snapshot.State == HostViewState.Ready;

    // ── Notice / status band ──────────────────────────────────────────────────────────────

    public bool HasNotice => !string.IsNullOrEmpty(_noticeText);

    public string NoticeText => _noticeText ?? string.Empty;

    public NmStatus NoticeStatus => _noticeStatus;

    public string NoticeSymbol => NmStatusInfo.Symbol(_noticeStatus);

    public string NoticeLabel => NmStatusInfo.Label(_noticeStatus);

    /// <summary>
    /// Status band is only an activity strip here (screen spec §1: it exists for a Run). Before the Run
    /// projection lands it appears for real activity/status only; notices live in the AlertBanner.
    /// </summary>
    /// <summary>
    /// Status band: R-24 — the single shared <see cref="RunStatusMonitor"/> snapshot is the Run source
    /// (no Run ⇒ hidden); real import/Host activity still shows before any Run exists.
    /// </summary>
    public bool IsStatusBandVisible =>
        (RunMonitor.IsActive && RunMonitor.HasSnapshot) || Library.ImportDock.IsRunning || !IsHostReady;

    public string StatusBandLeft => RunMonitor.IsActive && RunMonitor.HasSnapshot
        ? RunMonitor.SummaryText
        : Library.ImportDock.IsRunning
            ? $"导入中 · {Library.ImportDock.Summary}"
            : "Host 未就绪：等待 Core sidecar";

    public string StatusBandRight => $"作用域 {ScopeText} · {HostStatusText}";

    public NmStatus StatusBandState => RunMonitor.IsActive && RunMonitor.HasSnapshot
        ? RunMonitor.Status
        : Library.ImportDock.IsRunning
            ? NmStatus.Running
            : NmStatus.Blocked;

    public string StatusBandSymbol => NmStatusInfo.Symbol(StatusBandState);

    /// <summary>R-24: the ONE Run snapshot/poller shared by StatusBand, Console and (later) Studio Batch.</summary>
    public RunStatusMonitor RunMonitor { get; }

    /// <summary>Shell-level seam for INT-1/B-4: track the active run on the shared monitor.</summary>
    public void TrackRun(string? runId) => RunMonitor.Track(runId);

    // ── Theme / viewport ─────────────────────────────────────────────────────────────────

    public bool IsDarkTheme
    {
        get => _isDarkTheme;
        private set
        {
            if (Set(ref _isDarkTheme, value))
            {
                OnPropertyChanged(nameof(ThemeLabel), nameof(ThemeToggleTooltip));
            }
        }
    }

    public string ThemeLabel => IsDarkTheme ? "深色" : "浅色";

    public string ThemeToggleTooltip => IsDarkTheme ? "切换到浅色外观" : "切换到深色外观";

    public bool IsCompact
    {
        get => _isCompact;
        private set => Set(ref _isCompact, value);
    }

    /// <summary>R-18 narrow band (&lt; 1280): secondary labels collapse and Library uses overlay detail.</summary>
    public bool IsNarrow
    {
        get => _isNarrow;
        private set => Set(ref _isNarrow, value);
    }

    // ── V11R-INT-0 workspaces ─────────────────────────────────────────────────────────────

    /// <summary>Registers a workspace with the shell and activates it when its space is current.</summary>
    public bool RegisterWorkspace(IWorkspaceView workspace)
    {
        if (!State.RegisterWorkspace(workspace))
        {
            return false;
        }

        if (State.CurrentSpace == workspace.Space)
        {
            workspace.OnActivated(State);
        }

        RaiseWorkspaceChrome();
        return true;
    }

    public bool UnregisterWorkspace(SpaceId space)
    {
        var workspace = State.GetWorkspace(space);
        if (workspace is not null && State.CurrentSpace == space)
        {
            workspace.OnDeactivated(State);
        }

        var removed = State.UnregisterWorkspace(space);
        RaiseWorkspaceChrome();
        return removed;
    }

    public bool IsLibraryWorkspaceRegistered => State.IsWorkspaceRegistered(SpaceId.Library);

    public bool IsConsoleWorkspaceRegistered => State.IsWorkspaceRegistered(SpaceId.Console);

    public bool IsStudioWorkspaceRegistered => State.IsWorkspaceRegistered(SpaceId.Studio);

    public object? LibraryWorkspaceContent =>
        State.GetWorkspace(SpaceId.Library)?.CreateContent();

    public object? ConsoleWorkspaceContent =>
        State.GetWorkspace(SpaceId.Console)?.CreateContent();

    public object? StudioWorkspaceContent =>
        State.GetWorkspace(SpaceId.Studio)?.CreateContent();

    public bool IsLibraryPlaceholderVisible => IsLibrarySpace && !IsLibraryWorkspaceRegistered;

    public bool IsConsolePlaceholderVisible => IsConsoleSpace && !IsConsoleWorkspaceRegistered;

    public bool IsStudioPlaceholderVisible => IsStudioSpace && !IsStudioWorkspaceRegistered;

    public string LibraryPlaceholderDetail => ShellState.WorkspacePlaceholderDetail(SpaceId.Library);

    public string ConsolePlaceholderDetail => ShellState.WorkspacePlaceholderDetail(SpaceId.Console);

    public string StudioPlaceholderDetail => ShellState.WorkspacePlaceholderDetail(SpaceId.Studio);

    /// <summary>Registers the Theme Studio surface implementation (C-2/INT-1); null keeps the placeholder.</summary>
    public bool RegisterSurfaceWorkspace(ISurfaceWorkspace workspace)
    {
        var registered = State.RegisterSurfaceWorkspace(workspace);
        RaiseWorkspaceChrome();
        return registered;
    }

    public bool UnregisterSurfaceWorkspace(ShellSurface surface)
    {
        var removed = State.UnregisterSurfaceWorkspace(surface);
        RaiseWorkspaceChrome();
        return removed;
    }

    public bool IsThemeStudioWorkspaceRegistered =>
        State.IsSurfaceWorkspaceRegistered(ShellSurface.ThemeStudio);

    public object? ThemeStudioWorkspaceContent =>
        State.GetSurfaceWorkspace(ShellSurface.ThemeStudio)?.CreateContent();

    public bool IsThemeStudioPlaceholderVisible =>
        IsThemeStudioOpen && !IsThemeStudioWorkspaceRegistered;

    public string ThemeStudioPlaceholderDetail => ShellState.ThemeStudioPlaceholderDetail;

    private void RaiseRunChrome() => OnPropertyChanged(
        nameof(IsStatusBandVisible),
        nameof(StatusBandLeft),
        nameof(StatusBandState),
        nameof(StatusBandSymbol));
    private void RaiseWorkspaceChrome() => OnPropertyChanged(
        nameof(IsLibraryWorkspaceRegistered),
        nameof(IsConsoleWorkspaceRegistered),
        nameof(IsStudioWorkspaceRegistered),
        nameof(LibraryWorkspaceContent),
        nameof(ConsoleWorkspaceContent),
        nameof(StudioWorkspaceContent),
        nameof(IsLibraryPlaceholderVisible),
        nameof(IsConsolePlaceholderVisible),
        nameof(IsStudioPlaceholderVisible),
        nameof(LibraryPlaceholderDetail),
        nameof(ConsolePlaceholderDetail),
        nameof(StudioPlaceholderDetail),
        nameof(IsThemeStudioWorkspaceRegistered),
        nameof(ThemeStudioWorkspaceContent),
        nameof(IsThemeStudioPlaceholderVisible),
        nameof(ThemeStudioPlaceholderDetail));

    // ── Command palette ──────────────────────────────────────────────────────────────────

    public bool IsPaletteOpen
    {
        get => _paletteOpen;
        private set
        {
            if (Set(ref _paletteOpen, value))
            {
                OnPropertyChanged(nameof(IsAnyOverlayOpen));
            }
        }
    }

    public bool IsJumpOpen
    {
        get => _jumpOpen;
        private set
        {
            if (Set(ref _jumpOpen, value))
            {
                OnPropertyChanged(nameof(IsAnyOverlayOpen));
            }
        }
    }

    public bool IsHelpOpen
    {
        get => _helpOpen;
        private set
        {
            if (Set(ref _helpOpen, value))
            {
                OnPropertyChanged(nameof(IsAnyOverlayOpen));
            }
        }
    }

    public bool IsAnyOverlayOpen => IsPaletteOpen || IsJumpOpen || IsHelpOpen || IsConfirmOpen;

    /// <summary>Palette panel width (DS-token derived; see <see cref="ShellLayout"/>).</summary>
    public double PaletteWidth => ShellLayout.PaletteWidth;

    /// <summary>Centered confirmation-modal width (DS-token derived).</summary>
    public double ConfirmWidth => ShellLayout.ConfirmWidth;

    public ObservableCollection<CommandPaletteEntry> PaletteItems { get; } = new();

    public string PaletteQuery
    {
        get => _paletteQuery;
        set
        {
            if (Set(ref _paletteQuery, value))
            {
                RebuildPalette();
            }
        }
    }

    public int PaletteIndex
    {
        get => _paletteIndex;
        set
        {
            if (Set(ref _paletteIndex, value))
            {
                OnPropertyChanged(nameof(PaletteHint));
            }
        }
    }

    public string PaletteHint => PaletteItems.Count == 0
        ? "没有匹配的命令"
        : $"{PaletteItems.Count} 条命令 · ↑↓ 选择 · Enter 执行 · Esc 关闭";

    public string PaletteScopeNote => $"当前作用域：{SpaceLabel()} · {StudioModeLabel} · {ScopeText}";

    private string SpaceLabel() => State.CurrentSpace switch
    {
        SpaceId.Library => "资料柜",
        SpaceId.Studio => "工位",
        SpaceId.Console => "控制台",
        _ => "资料柜",
    };

    // ── Ctrl+P jump ──────────────────────────────────────────────────────────────────────

    public ObservableCollection<JumpEntry> JumpItems { get; } = new();

    public string JumpQuery
    {
        get => _jumpQuery;
        set
        {
            if (Set(ref _jumpQuery, value))
            {
                RebuildJump();
            }
        }
    }

    public int JumpIndex
    {
        get => _jumpIndex;
        set => Set(ref _jumpIndex, value);
    }

    public string JumpHint => JumpItems.Count == 0
        ? "没有匹配的对象"
        : $"{JumpItems.Count} 个对象 · ↑↓ 选择 · Enter 跳转 · Esc 关闭";

    // ── F1 help ──────────────────────────────────────────────────────────────────────────

    public IReadOnlyList<HelpGroup> HelpGroups { get; } = BuildHelpGroups();

    // ── Confirmation modal ───────────────────────────────────────────────────────────────

    public bool IsConfirmOpen
    {
        get => _confirmOpen;
        private set
        {
            if (Set(ref _confirmOpen, value))
            {
                OnPropertyChanged(nameof(IsAnyOverlayOpen));
            }
        }
    }

    public string ConfirmTitle => _confirm?.Title ?? string.Empty;

    public string ConfirmBody => _confirm?.Body ?? string.Empty;

    public string ConfirmText => _confirm?.ConfirmText ?? "确认";

    public bool ConfirmIsDanger => _confirm?.IsDanger ?? false;

    public bool ConfirmCanConfirm => _confirm?.CanConfirm ?? true;

    public string ConfirmBlockedReason => _confirm?.BlockedReason ?? string.Empty;

    public bool HasConfirmBlockedReason => !string.IsNullOrEmpty(ConfirmBlockedReason);

    // ── Initialization ───────────────────────────────────────────────────────────────────

    private async Task InitializeCoreAsync()
    {
        await Library.InitializeAsync().ConfigureAwait(true);
        RefreshChrome();
    }

    public void Notify(string text, NmStatus status)
    {
        _noticeText = text;
        _noticeStatus = status;
        OnPropertyChanged(
            nameof(HasNotice),
            nameof(NoticeText),
            nameof(NoticeStatus),
            nameof(NoticeSymbol),
            nameof(NoticeLabel),
            nameof(IsStatusBandVisible),
            nameof(StatusBandLeft),
            nameof(StatusBandRight),
            nameof(StatusBandState),
            nameof(StatusBandSymbol));
    }

    public void DismissNotice()
    {
        _noticeText = null;
        OnPropertyChanged(
            nameof(HasNotice),
            nameof(NoticeText),
            nameof(IsStatusBandVisible),
            nameof(StatusBandLeft),
            nameof(StatusBandState),
            nameof(StatusBandSymbol));
    }

    public void SetViewport(double width, double height)
    {
        IsCompact = ShellLayout.IsCompact(width);
        IsNarrow = ShellLayout.IsNarrow(width);
        Library.SetViewport(width, height);
        OnPropertyChanged(nameof(ScopeText), nameof(StatusBandRight));
    }

    public void SwitchSpace(SpaceId space)
    {
        if (State.CurrentSpace == space)
        {
            return;
        }

        // Contract §6.1: deactivate the outgoing workspace (writes scroll/filter/selection back) before
        // switching, then activate the incoming one (restores its retained context). ViewModels are
        // never rebuilt, so this is a context hand-off, not a subscription swap.
        State.GetWorkspace(State.CurrentSpace)?.OnDeactivated(State);
        State.SwitchSpace(space);
        State.GetWorkspace(space)?.OnActivated(State);

        if (space == SpaceId.Console)
        {
            _ = Console.InitializeAsync();
        }
    }

    /// <summary>Sets the Studio mode with the §6.1 workspace hooks (same workspace, new retained mode).</summary>
    public void SetStudioMode(StudioMode mode)
    {
        var workspace = State.GetWorkspace(SpaceId.Studio);
        var active = State.CurrentSpace == SpaceId.Studio;
        if (active)
        {
            workspace?.OnDeactivated(State);
        }

        State.SetStudioMode(mode);

        if (active)
        {
            workspace?.OnActivated(State);
        }
    }

    public void ToggleStudioMode() =>
        SetStudioMode(State.StudioMode == StudioMode.Page ? StudioMode.Batch : StudioMode.Page);

    public void ToggleTheme() => IsDarkTheme = !IsDarkTheme;

    public void OpenThemeStudio() => State.PushSurface(ShellSurface.ThemeStudio);

    public void CloseThemeStudio() => State.CloseTopSurface();

    public void OpenPalette()
    {
        CloseJump();
        CloseHelp();
        PaletteQuery = string.Empty;
        RebuildPalette();
        PaletteIndex = PaletteItems.Count > 0 ? 0 : -1;
        IsPaletteOpen = true;
    }

    public void ClosePalette() => IsPaletteOpen = false;

    public void OpenJump()
    {
        ClosePalette();
        CloseHelp();
        JumpQuery = string.Empty;
        RebuildJump();
        JumpIndex = JumpItems.Count > 0 ? 0 : -1;
        IsJumpOpen = true;
    }

    public void CloseJump() => IsJumpOpen = false;

    public void OpenHelp()
    {
        ClosePalette();
        CloseJump();
        IsHelpOpen = true;
    }

    public void CloseHelp() => IsHelpOpen = false;

    public void RequestConfirm(ConfirmRequest request)
    {
        _confirm = request;
        IsConfirmOpen = true;
        OnPropertyChanged(
            nameof(ConfirmTitle),
            nameof(ConfirmBody),
            nameof(ConfirmText),
            nameof(ConfirmIsDanger),
            nameof(ConfirmCanConfirm),
            nameof(ConfirmBlockedReason),
            nameof(HasConfirmBlockedReason));
    }

    public void ConfirmNow()
    {
        if (!ConfirmCanConfirm)
        {
            Notify(ConfirmBlockedReason, NmStatus.Blocked);
            return;
        }

        var request = _confirm;
        IsConfirmOpen = false;
        _confirm = null;
        request?.OnConfirm();
    }

    public void CancelConfirm()
    {
        IsConfirmOpen = false;
        _confirm = null;
    }

    public void MovePaletteSelection(int delta)
    {
        if (PaletteItems.Count == 0)
        {
            return;
        }

        PaletteIndex = Math.Clamp(PaletteIndex + delta, 0, PaletteItems.Count - 1);
    }

    public void ExecutePaletteSelection()
    {
        if (PaletteIndex < 0 || PaletteIndex >= PaletteItems.Count)
        {
            return;
        }

        var entry = PaletteItems[PaletteIndex];
        OnPaletteEntryExecuted(entry);
    }

    public void MoveJumpSelection(int delta)
    {
        if (JumpItems.Count == 0)
        {
            return;
        }

        JumpIndex = Math.Clamp(JumpIndex + delta, 0, JumpItems.Count - 1);
    }

    public void ExecuteJumpSelection()
    {
        if (JumpIndex < 0 || JumpIndex >= JumpItems.Count)
        {
            return;
        }

        var entry = JumpItems[JumpIndex];
        _ = ExecuteJumpAsync(entry);
    }

    // ── Keyboard entry point (also used by the headless tests) ──────────────────────────

    /// <summary>
    /// One keyboard funnel for the whole shell. Returns true when the key was consumed.
    /// <paramref name="isTextInputFocused"/> implements the IME-safety rule (AC5): while a text box
    /// has focus plain letter/digit shortcuts yield to typing; Ctrl/F-key/Esc shortcuts still apply.
    /// </summary>
    /// <summary>Window key funnel: workspace first refusal (R-17), then the shell KeyMap.</summary>
    public bool HandleKey(KeyEventArgs e, bool isTextInputFocused)
    {
        var shellOverlayTakesKeys = IsConfirmOpen || IsPaletteOpen || IsJumpOpen || IsHelpOpen || State.IsReaderOpen;
        if (!shellOverlayTakesKeys && !(isTextInputFocused && IsPlainTypingKey(e.Key, e.KeyModifiers)))
        {
            var workspace = State.GetWorkspace(State.CurrentSpace);
            if (workspace is not null && workspace.TryHandleKey(e, State))
            {
                e.Handled = true;
                return true;
            }
        }

        if (HandleKeyCore(e.Key, e.KeyModifiers, isTextInputFocused))
        {
            e.Handled = true;
            return true;
        }

        return false;
    }

    /// <summary>Test/automation wrapper for the same funnel (no real KeyEventArgs required).</summary>
    public bool HandleKey(Key key, KeyModifiers modifiers, bool isTextInputFocused) =>
        HandleKey(
            new KeyEventArgs
            {
                RoutedEvent = InputElement.KeyDownEvent,
                Key = key,
                KeyModifiers = modifiers,
            },
            isTextInputFocused);

    private bool HandleKeyCore(Key key, KeyModifiers modifiers, bool isTextInputFocused)
    {
        if (IsConfirmOpen)
        {
            if (key == Key.Escape)
            {
                CancelConfirm();
                return true;
            }

            return false;
        }

        if (IsPaletteOpen)
        {
            switch (key)
            {
                case Key.Escape:
                    ClosePalette();
                    return true;
                case Key.Up:
                    MovePaletteSelection(-1);
                    return true;
                case Key.Down:
                    MovePaletteSelection(1);
                    return true;
                case Key.Enter:
                    ExecutePaletteSelection();
                    return true;
            }

            return false;
        }

        if (IsJumpOpen)
        {
            switch (key)
            {
                case Key.Escape:
                    CloseJump();
                    return true;
                case Key.Up:
                    MoveJumpSelection(-1);
                    return true;
                case Key.Down:
                    MoveJumpSelection(1);
                    return true;
                case Key.Enter:
                    ExecuteJumpSelection();
                    return true;
            }

            return false;
        }

        if (IsHelpOpen)
        {
            if (key == Key.Escape)
            {
                CloseHelp();
                return true;
            }

            return false;
        }

        if (isTextInputFocused && IsPlainTypingKey(key, modifiers))
        {
            return false;
        }

        if (isTextInputFocused && key == Key.Tab)
        {
            return false;
        }

        if (State.IsReaderOpen)
        {
            switch (key)
            {
                case Key.Left:
                case Key.PageUp:
                case Key.J:
                    _ = Library.Reader.PreviousAsync();
                    return true;
                case Key.Right:
                case Key.PageDown:
                case Key.K:
                case Key.Space:
                    _ = Library.Reader.NextAsync();
                    return true;
            }
        }

        if (_keyMap.TryMatch(key, modifiers, State.CurrentSpace, State.StudioMode, out var command))
        {
            ExecuteCommand(command.Id);
            return true;
        }

        return false;
    }

    public void ExecuteCommand(string id)
    {
        switch (id)
        {
            case ShellCommandIds.SpaceLibrary:
                SwitchSpace(SpaceId.Library);
                return;
            case ShellCommandIds.SpaceStudio:
                SwitchSpace(SpaceId.Studio);
                return;
            case ShellCommandIds.SpaceConsole:
                SwitchSpace(SpaceId.Console);
                return;
            case ShellCommandIds.StudioModeToggle:
                ToggleStudioMode();
                return;
            case ShellCommandIds.CommandPalette:
                if (IsPaletteOpen)
                {
                    ClosePalette();
                }
                else
                {
                    OpenPalette();
                }

                return;
            case ShellCommandIds.QuickJump:
                OpenJump();
                return;
            case ShellCommandIds.Export:
                Notify(ReasonOf(ShellCommandIds.Export), NmStatus.Blocked);
                return;
            case ShellCommandIds.ThemeStudio:
                OpenThemeStudio();
                return;
            case ShellCommandIds.ThemeToggle:
                ToggleTheme();
                return;
            case ShellCommandIds.Help:
                OpenHelp();
                return;
            case ShellCommandIds.AttentionNext:
                SwitchSpace(SpaceId.Studio);
                SetStudioMode(StudioMode.Batch);
                Notify(ReasonOf(ShellCommandIds.AttentionNext), NmStatus.Blocked);
                return;
            case ShellCommandIds.SurfaceBack:
                HandleBack();
                return;
            case ShellCommandIds.ObjectNext:
                Library.MoveObjectSelection(1);
                return;
            case ShellCommandIds.ObjectPrevious:
                Library.MoveObjectSelection(-1);
                return;
            case ShellCommandIds.PageNext:
                Library.MovePageSelection(1);
                return;
            case ShellCommandIds.PagePrevious:
                Library.MovePageSelection(-1);
                return;
            case ShellCommandIds.ChapterNext:
                Library.MoveChapterSelection(1);
                return;
            case ShellCommandIds.ChapterPrevious:
                Library.MoveChapterSelection(-1);
                return;
            case ShellCommandIds.LibraryRefresh:
                _ = Library.RefreshAsync();
                return;
            case ShellCommandIds.LibraryImportFiles:
                _ = Library.ImportDock.PickFilesAsync();
                return;
            case ShellCommandIds.LibraryImportFolder:
                _ = Library.ImportDock.PickFolderAsync();
                return;
            case ShellCommandIds.LibraryRecycle:
                Library.ShowRecycleBin();
                return;
            case ShellCommandIds.LibraryNewBook:
                Library.ShowCreateBook();
                return;
            case ShellCommandIds.LibraryNewChapter:
                Library.ShowCreateChapter();
                return;
            case ShellCommandIds.LibraryOpenReader:
                _ = Library.OpenReaderAsync();
                return;
            case ShellCommandIds.LibraryClearSelection:
                State.ClearMultiPage();
                return;
            case ShellCommandIds.StudioPage:
                SwitchSpace(SpaceId.Studio);
                SetStudioMode(StudioMode.Page);
                return;
            case ShellCommandIds.StudioBatch:
                SwitchSpace(SpaceId.Studio);
                SetStudioMode(StudioMode.Batch);
                return;
        }
    }

    public void HandleBack()
    {
        if (IsConfirmOpen)
        {
            CancelConfirm();
            return;
        }

        if (IsPaletteOpen)
        {
            ClosePalette();
            return;
        }

        if (IsJumpOpen)
        {
            CloseJump();
            return;
        }

        if (IsHelpOpen)
        {
            CloseHelp();
            return;
        }

        if (State.IsReaderOpen)
        {
            _ = Library.Reader.CloseAsync();
            return;
        }

        if (State.IsThemeStudioOpen)
        {
            State.CloseTopSurface();
            return;
        }

        if (Library.IsRecycleBinView)
        {
            Library.CloseRecycleBin();
            return;
        }

        if (Library.IsCreateBookOpen)
        {
            Library.CancelCreateBookCommand.Execute(null);
            return;
        }

        if (State.Selection.MultiPageCount > 0)
        {
            State.ClearMultiPage();
            return;
        }

        if (State.Selection.HasPage)
        {
            State.SelectPage(null);
            return;
        }

        if (State.Selection.HasChapter)
        {
            State.SelectChapter(null);
            return;
        }

        if (State.Selection.HasBook)
        {
            _ = Library.SelectBookAsync(null);
            return;
        }

        _ = State.CloseTopSurface();
    }

    public void JumpToAttention(AttentionItem item)
    {
        SwitchSpace(SpaceId.Studio);
        State.SetStudioMode(StudioMode.Batch);
        Notify(
            $"「{item.Label}」跳转需要工位批次筛选与 Run 投影（V11R-A-2 / V11R-B-4），当前显示能力待接入",
            NmStatus.Blocked);
    }

    public void ActivateBreadcrumb(BreadcrumbItem item)
    {
        switch (item.Level)
        {
            case 0:
                SwitchSpace(State.CurrentSpace);
                _ = Library.SelectBookAsync(null);
                return;
            case 1:
                if (Library.AllBooks.FirstOrDefault(book =>
                        string.Equals(book.Title, item.Label, StringComparison.Ordinal)) is { } book)
                {
                    _ = Library.SelectBookAsync(book);
                }

                return;
            case 2:
                if (Library.Chapters.FirstOrDefault(chapter =>
                        string.Equals(chapter.Title, item.Label, StringComparison.Ordinal)) is { } chapter)
                {
                    _ = Library.SelectChapterAsync(chapter);
                }

                return;
            case 3:
                if (Library.Pages.FirstOrDefault(page =>
                        string.Equals("第 " + (page.Index + 1) + " 页", item.Label, StringComparison.Ordinal)) is { } page)
                {
                    Library.SelectPage(page);
                }

                return;
        }
    }

    public async Task ApplyDeepLinkAsync(ShellDeepLink link)
    {
        State.SwitchSpace(link.Space);
        if (link.Space == SpaceId.Studio)
        {
            State.SetStudioMode(link.Mode);
        }

        await Library.InitializeAsync().ConfigureAwait(true);

        if (link.BookId is { } bookId && Library.AllBooks.FirstOrDefault(book =>
                string.Equals(book.BookId, bookId, StringComparison.Ordinal)) is { } book)
        {
            await Library.SelectBookAsync(book).ConfigureAwait(true);
            if (link.ChapterId is { } chapterId && Library.Chapters.FirstOrDefault(chapter =>
                    string.Equals(chapter.ChapterId, chapterId, StringComparison.Ordinal)) is { } chapter)
            {
                await Library.SelectChapterAsync(chapter).ConfigureAwait(true);
            }
        }

        if (link.Page is { } page)
        {
            await Library.OpenReaderAtAsync(page).ConfigureAwait(true);
        }

        RefreshChrome();
    }

    // ── Internal ─────────────────────────────────────────────────────────────────────────

    private void RefreshChrome()
    {
        foreach (var tab in SpaceTabs)
        {
            tab.SetActive(tab.Space == State.CurrentSpace);
        }

        RebuildBreadcrumb();
        UpdateStatusBand();
        OnPropertyChanged(
            nameof(IsLibraryPlaceholderVisible),
            nameof(IsConsolePlaceholderVisible),
            nameof(IsStudioPlaceholderVisible),
            nameof(IsLibrarySpace),
            nameof(IsStudioSpace),
            nameof(IsConsoleSpace),
            nameof(StudioModeLabel),
            nameof(IsPageMode),
            nameof(IsBatchMode),
            nameof(ScopeText),
            nameof(PaletteScopeNote),
            nameof(IsReaderSurfaceVisible),
            nameof(IsThemeStudioOpen),
            nameof(IsOverlayOpen));
    }

    private void RebuildBreadcrumb()
    {
        Breadcrumb.Clear();
        var spaceLabel = State.CurrentSpace switch
        {
            SpaceId.Library => "资料柜",
            SpaceId.Studio => "工位",
            SpaceId.Console => "控制台",
            _ => "资料柜",
        };
        var book = Library.SelectedBook;
        var chapter = Library.SelectedChapter;
        var hasDeeper = book is not null;
        Breadcrumb.Add(new BreadcrumbItem(0, spaceLabel, IsCurrent: !hasDeeper));
        if (book is not null)
        {
            Breadcrumb.Add(new BreadcrumbItem(1, book.Title, IsCurrent: chapter is null));
        }

        if (chapter is not null)
        {
            Breadcrumb.Add(new BreadcrumbItem(2, chapter.Title, IsCurrent: State.Selection.MultiPageCount == 0 && !State.Selection.HasPage));
        }

        if (State.Selection.MultiPageCount > 0)
        {
            Breadcrumb.Add(new BreadcrumbItem(3, $"选中 {State.Selection.MultiPageCount} 页", IsCurrent: true));
        }
        else if (Library.SelectedPage is { } page)
        {
            Breadcrumb.Add(new BreadcrumbItem(3, $"第 {page.Index + 1} 页", IsCurrent: true));
        }
    }

    private void UpdateStatusBand()
    {
        OnPropertyChanged(
            nameof(IsStatusBandVisible),
            nameof(StatusBandLeft),
            nameof(StatusBandRight),
            nameof(StatusBandState),
            nameof(StatusBandSymbol),
            nameof(HostStatusText),
            nameof(IsHostReady));
    }

    private void SynchronizeReaderSurface()
    {
        if (Library.Reader.IsOpen)
        {
            State.PushSurface(ShellSurface.ReaderOverlay);
        }
        else if (State.IsReaderOpen)
        {
            State.CloseTopSurface();
        }

        OnPropertyChanged(nameof(IsReaderSurfaceVisible));
    }

    private void RebuildPalette()
    {
        PaletteItems.Clear();
        var query = _paletteQuery.Trim();
        foreach (var definition in ShellCommands.Definitions
                     .Select(definition => new
                     {
                         Definition = definition,
                         Contextual = definition.AppliesTo(State.CurrentSpace, State.StudioMode),
                     })
                     .Where(item => query.Length == 0
                         || PinyinIndex.Matches(item.Definition.Title, query)
                         || PinyinIndex.Matches(item.Definition.ScopeLabel, query))
                     .OrderByDescending(item => item.Contextual)
                     .ThenBy(item => item.Definition.Title, StringComparer.Ordinal))
        {
            PaletteItems.Add(new CommandPaletteEntry(definition.Definition, definition.Contextual, OnPaletteEntryExecuted));
        }

        if (PaletteItems.Count > 0)
        {
            PaletteIndex = Math.Clamp(PaletteIndex < 0 ? 0 : PaletteIndex, 0, PaletteItems.Count - 1);
        }
        else
        {
            PaletteIndex = -1;
        }

        OnPropertyChanged(nameof(PaletteHint), nameof(PaletteScopeNote));
    }

    private void RebuildJump()
    {
        JumpItems.Clear();
        var query = _jumpQuery.Trim();
        var matches = new Func<string?, string?, bool>((title, subtitle) =>
            query.Length == 0
            || PinyinIndex.Matches(title, query)
            || PinyinIndex.Matches(subtitle, query));

        foreach (var book in Library.AllBooks.Where(book => matches(book.Title, book.OriginalTitle)))
        {
            JumpItems.Add(new JumpEntry("作品", book.Title, book.MetaText, book.BookId, null, null, null, OnJumpEntryActivated));
        }

        foreach (var chapter in Library.Chapters.Where(chapter => matches(chapter.Title, chapter.MetaText)))
        {
            JumpItems.Add(new JumpEntry(
                "章节",
                chapter.Title,
                Library.SelectedBook?.Title ?? string.Empty,
                Library.SelectedBook?.BookId,
                chapter.ChapterId,
                null,
                null,
                OnJumpEntryActivated));
        }

        foreach (var page in Library.Pages.Where(page => matches(page.FileNameText, page.Label)))
        {
            JumpItems.Add(new JumpEntry(
                "页",
                page.FileNameText,
                Library.SelectedChapter?.Title ?? string.Empty,
                Library.SelectedBook?.BookId,
                Library.SelectedChapter?.ChapterId,
                page.Index,
                page.PageId,
                OnJumpEntryActivated));
        }

        JumpIndex = JumpItems.Count > 0 ? Math.Clamp(JumpIndex < 0 ? 0 : JumpIndex, 0, JumpItems.Count - 1) : -1;
        OnPropertyChanged(nameof(JumpHint));
    }

    private async Task ExecuteJumpAsync(JumpEntry entry)
    {
        CloseJump();
        SwitchSpace(SpaceId.Library);
        if (entry.KindLabel == "作品" && entry.BookId is { } bookId)
        {
            var book = Library.AllBooks.FirstOrDefault(item => string.Equals(item.BookId, bookId, StringComparison.Ordinal));
            if (book is not null)
            {
                await Library.SelectBookAsync(book).ConfigureAwait(true);
            }
        }
        else if (entry.KindLabel == "章节" && entry.ChapterId is { } chapterId)
        {
            var chapter = Library.Chapters.FirstOrDefault(item => string.Equals(item.ChapterId, chapterId, StringComparison.Ordinal));
            if (chapter is not null)
            {
                await Library.SelectChapterAsync(chapter).ConfigureAwait(true);
            }
        }
        else if (entry.KindLabel == "页" && entry.PageId is { } pageId)
        {
            var page = Library.Pages.FirstOrDefault(item => string.Equals(item.PageId, pageId, StringComparison.Ordinal));
            if (page is not null)
            {
                Library.SelectPage(page);
                await Library.OpenReaderAtAsync(page.Index + 1).ConfigureAwait(true);
            }
        }

        RefreshChrome();
    }

    private void OnPaletteEntryExecuted(CommandPaletteEntry entry)
    {
        ClosePalette();
        ExecuteCommand(entry.Id);
    }

    private void OnJumpEntryActivated(JumpEntry entry) => _ = ExecuteJumpAsync(entry);

    private static string ReasonOf(string commandId) =>
        ShellCommands.Find(commandId)?.UnavailableReason ?? "能力待接入（Host 未暴露该方法）";

    private static bool IsPlainTypingKey(Key key, KeyModifiers modifiers)
    {
        if ((modifiers & (KeyModifiers.Control | KeyModifiers.Alt | KeyModifiers.Meta)) != 0)
        {
            return false;
        }

        return key is (>= Key.A and <= Key.Z)
            or (>= Key.D0 and <= Key.D9)
            or Key.OemOpenBrackets
            or Key.OemCloseBrackets
            or Key.OemComma
            or Key.Space
            or Key.Back
            or Key.Delete;
    }

    private static IReadOnlyList<HelpGroup> BuildHelpGroups()
    {
        var groups = new List<HelpGroup>();
        foreach (var group in ShellCommands.Definitions
                     .Where(definition => definition.HasGesture)
                     .GroupBy(definition => definition.ScopeLabel.Split('·')[0].Trim()))
        {
            var entries = group
                .OrderBy(definition => definition.Title, StringComparer.Ordinal)
                .Select(definition => new HelpEntry(
                    definition.Title,
                    string.Join(" / ", definition.Gestures.Select(gesture => gesture.Display)),
                    definition.IsAvailable))
                .ToList();
            groups.Add(new HelpGroup(group.Key, entries));
        }

        return groups;
    }
}
