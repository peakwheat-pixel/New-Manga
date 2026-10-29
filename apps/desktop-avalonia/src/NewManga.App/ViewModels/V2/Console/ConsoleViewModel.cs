using System.Collections.ObjectModel;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.Console;

/// <summary>
/// V11R-B-2: Console space (settings centre, screen spec §5) with nine sections.
/// Data rules: only existing <see cref="IHostController"/> methods are used; credential state is the
/// ONLY credential information rendered (never a secret); every section without a real Host API shows
/// an explicit 能力待接入 banner and never a fake switch. Destructive actions open the shell's
/// confirmation modal (cancel-first, consequences + scope spelled out) and the modal cannot be
/// bypassed.
/// </summary>
public sealed class ConsoleViewModel : ObservableObject
{
    private readonly IHostController _controller;
    private readonly ShellState _state;
    private readonly RunStatusMonitor _runMonitor;
    private bool _runPollingPreferred = true;
    private readonly Action<string, NmStatus> _notify;
    private readonly Action<ConfirmRequest> _requestConfirm;
    private readonly Func<bool> _isDarkTheme;
    private readonly Action _toggleTheme;
    private readonly Action _openThemeStudio;
    private readonly Action _openStudio;

    private ConsoleSectionItem _selectedSection = null!;
    private bool _isLoading;
    private string? _errorMessage;
    private string _statusMessage = string.Empty;
    private bool _initialized;

    private bool _isProviderFormOpen;
    private string _providerFormTitle = "新建 Provider 配置";
    private string? _editingProviderProfileId;
    private string _formProviderId = string.Empty;
    private string _formDisplayName = string.Empty;
    private string _formEndpoint = string.Empty;
    private string _formModel = string.Empty;
    private bool _formEnabled = true;
    private bool _formCapOcr;
    private bool _formCapTranslation;
    private bool _formCapInpaint;
    private bool _formCapDetection;
    private bool _formCapRendering;
    private int _formNetworkIndex;
    private ProviderProfileRowViewModel? _selectedProvider;
    private int _bindingScopeIndex;
    private string _bindingScopeHint = string.Empty;

    private bool _isNetworkFormOpen;
    private string _networkFormTitle = "新建网络配置";
    private string? _editingNetworkProfileId;
    private string _formNetworkName = string.Empty;
    private string _formNetworkMode = NetworkModes.System;
    private string _formProxyEndpoint = string.Empty;
    private bool _formVerifyTls = true;
    private bool _formConfirmDisableTls;
    private bool _formAllowFallback;
    private NetworkProfileRowViewModel? _selectedNetwork;
    private string _defaultNetworkText = "默认网络：读取中…";
    private string _networkTestText = "尚未测试";
    private string _networkResolveText = "尚未解析";

    private string _hostStateText = "—";
    private string _hostStatusLine = "—";
    private string _hostModeLine = "—";
    private string _hostErrorCodeText = "无";
    private string _hostWireFrameText = "—";

    private string _runIdInput = string.Empty;
    private string _runIdempotencyKey = string.Empty;
    private bool _hasRunLoaded;
    private string _runStatusText = "未加载 Run";
    private string _runCommandText = "—";
    private string _runScopeText = "—";
    private string _runProgressText = "—";
    private string _runCountsText = "—";
    private string _runCurrentStepText = "—";
    private string _runBlockedText = "无";
    private bool _runCanPause;
    private bool _runCanStop;
    private bool _runCanContinue;
    private bool _runCanRestart;
    private bool _runCanResumeBlocked;
    private bool _runCanRetryFailed;
    private RunSnapshotInfo? _runSnapshot;
    private TaskProjectionInfo? _runProjection;

    public ConsoleViewModel(
        IHostController controller,
        ShellState state,
        RunStatusMonitor runMonitor,
        Action<string, NmStatus> notify,
        Action<ConfirmRequest> requestConfirm,
        Func<bool> isDarkTheme,
        Action toggleTheme,
        Action openThemeStudio,
        Action openStudio)
    {
        _controller = controller;
        _state = state;
        _runMonitor = runMonitor;
        _notify = notify;
        _requestConfirm = requestConfirm;
        _isDarkTheme = isDarkTheme;
        _toggleTheme = toggleTheme;
        _openThemeStudio = openThemeStudio;
        _openStudio = openStudio;

        Sections = new ObservableCollection<ConsoleSectionItem>
        {
            Section(ConsoleSectionId.Tasks, "01", "任务与队列", "Run 快照 / 任务投影（IRunController，真实）", isWired: true),
            Section(ConsoleSectionId.Providers, "02", "Provider 与凭据", "配置 / 凭据状态 / 能力绑定", isWired: true),
            Section(ConsoleSectionId.Network, "03", "网络与代理", "网络配置 / 默认网络 / 连通测试", isWired: true),
            Section(ConsoleSectionId.Devices, "04", "模型与设备", "设备探测未接入（无 Host 命令）", isWired: false),
            Section(ConsoleSectionId.Storage, "05", "缓存与版本清理", "清理需 Host 方法与影响面预览", isWired: false),
            Section(ConsoleSectionId.Backup, "06", "备份与恢复", ".nmbak 备份/恢复未接入", isWired: false),
            Section(ConsoleSectionId.Plugins, "07", "插件与 Hooks", "插件列表/启停未接入", isWired: false),
            Section(ConsoleSectionId.Diagnostics, "08", "诊断与日志", "Host 状态 / 导出历史（真实）", isWired: true),
            Section(ConsoleSectionId.Appearance, "09", "外观", "深浅外观 / 主题工作室入口", isWired: true),
        };

        ProviderProfiles = new ObservableCollection<ProviderProfileRowViewModel>();
        CredentialTargets = new ObservableCollection<CredentialTargetRowViewModel>();
        CapabilityBindings = new ObservableCollection<CapabilityBindingRowViewModel>();
        NetworkProfiles = new ObservableCollection<NetworkProfileRowViewModel>();
        ExportHistory = new ObservableCollection<ExportHistoryRowViewModel>();
        RunStages = new ObservableCollection<RunStageRowViewModel>();
        RunRows = new ObservableCollection<RunRowViewModel>();
        ProviderNetworkOptions = new ObservableCollection<ConsoleOption> { new(string.Empty, "使用默认网络") };
        BindingScopeOptions = new ObservableCollection<BindingScopeOption>();
        NetworkModeOptions = new ObservableCollection<ConsoleOption>
        {
            new(NetworkModes.Direct, "Direct（直连）"),
            new(NetworkModes.System, "System（系统代理）"),
            new(NetworkModes.Http, "HTTP 代理"),
            new(NetworkModes.Https, "HTTPS 代理"),
            new(NetworkModes.Socks5, "SOCKS5 代理"),
        };

        RefreshCommand = new RelayCommand(() => _ = InitializeAsync(force: true));
        SelectSectionCommand = new RelayCommand(() => { });
        NewProviderCommand = new RelayCommand(NewProviderForm);
        CancelProviderCommand = new RelayCommand(() => IsProviderFormOpen = false);
        SaveProviderCommand = new RelayCommand(() => _ = SaveProviderAsync());
        NewNetworkCommand = new RelayCommand(NewNetworkForm);
        CancelNetworkCommand = new RelayCommand(() => IsNetworkFormOpen = false);
        SaveNetworkCommand = new RelayCommand(() => _ = SaveNetworkAsync());
        EditSelectedProviderCommand = new RelayCommand(EditSelectedProvider);
        DeleteSelectedProviderCommand = new RelayCommand(DeleteSelectedProvider);
        EditSelectedNetworkCommand = new RelayCommand(EditSelectedNetwork);
        SetDefaultSelectedNetworkCommand = new RelayCommand(SetDefaultSelectedNetwork);
        TestSelectedNetworkCommand = new RelayCommand(TestSelectedNetwork);
        DeleteSelectedNetworkCommand = new RelayCommand(DeleteSelectedNetwork);
        RefreshProvidersCommand = new RelayCommand(() => _ = RefreshProvidersAsync());
        RefreshNetworkCommand = new RelayCommand(() => _ = RefreshNetworkAsync());
        RefreshCredentialsViewCommand = new RelayCommand(() => _ = RefreshCredentialsAsync());
        RefreshBindingsViewCommand = new RelayCommand(() => _ = RefreshBindingsAsync());
        ToggleAppearanceCommand = new RelayCommand(ToggleAppearance);
        OpenThemeStudioCommand = new RelayCommand(() => _openThemeStudio());
        OpenStudioCommand = new RelayCommand(() => _openStudio());
        RequestClearCacheCommand = new RelayCommand(RequestClearCache);
        RequestCreateBackupCommand = new RelayCommand(RequestCreateBackup);
        RequestDeleteBackupCommand = new RelayCommand(RequestDeleteBackup);
        RefreshExportHistoryCommand = new RelayCommand(() => _ = RefreshExportHistoryAsync());
        LoadRunCommand = new RelayCommand(() => _ = LoadRunAsync());
        RefreshRunCommand = new RelayCommand(() => _ = RefreshRunAsync(notifyFailure: true));
        PauseRunCommand = new RelayCommand(() => RequestRunControl(RunControlAction.Pause));
        ContinueRunCommand = new RelayCommand(() => RequestRunControl(RunControlAction.Resume));
        StopRunCommand = new RelayCommand(RequestStopRun);
        RestartRunCommand = new RelayCommand(() => RequestRunControl(RunControlAction.Restart));
        ResumeBlockedRunCommand = new RelayCommand(() => _ = ResumeBlockedRunAsync());
        RetryFailedRunCommand = new RelayCommand(() => _ = RetryFailedRunAsync());
        RebuildCapabilityBindings();
        RebuildBindingScopes();
        SelectSection(Sections[0]);
        _state.SelectionChanged += (_, _) => RebuildBindingScopes();
        // R-24: the shared RunStatusMonitor owns polling; leaving the Console does not stop the shared
        // source (the shell StatusBand keeps showing the active Run).
        _runMonitor.Updated += OnRunMonitorUpdated;
    }

    private void OnRunMonitorUpdated(object? sender, EventArgs e)
    {
        if (!HasRunLoaded || _runMonitor.RunId is not { } runId)
        {
            return;
        }

        ApplyRun(runId, _runMonitor.Snapshot, _runMonitor.Projection);
    }

    // ── Sections ─────────────────────────────────────────────────────────────────────────

    public ObservableCollection<ConsoleSectionItem> Sections { get; }

    public ConsoleSectionItem SelectedSection => _selectedSection;

    public bool IsTasksSection => _selectedSection.Id == ConsoleSectionId.Tasks;

    public bool IsProvidersSection => _selectedSection.Id == ConsoleSectionId.Providers;

    public bool IsNetworkSection => _selectedSection.Id == ConsoleSectionId.Network;

    public bool IsDiagnosticsSection => _selectedSection.Id == ConsoleSectionId.Diagnostics;

    public bool IsAppearanceSection => _selectedSection.Id == ConsoleSectionId.Appearance;

    public bool IsNotWiredSection => !_selectedSection.IsWired;

    public string NotWiredTitle => _selectedSection.Label;

    public string NotWiredBody => NotWiredCopy(_selectedSection.Id).Body;

    public string NotWiredRequirement => NotWiredCopy(_selectedSection.Id).Requirement;

    public bool ShowClearCacheDanger => _selectedSection.Id == ConsoleSectionId.Storage;

    public bool ShowBackupDanger => _selectedSection.Id == ConsoleSectionId.Backup;

    public string SectionSummary => _selectedSection.Summary;

    public RelayCommand SelectSectionCommand { get; }

    public RelayCommand RefreshCommand { get; }

    public void SelectSectionById(ConsoleSectionId id)
    {
        var section = Sections.First(item => item.Id == id);
        SelectSection(section);
    }

    private void SelectSection(ConsoleSectionItem section)
    {
        foreach (var item in Sections)
        {
            item.SetSelected(ReferenceEquals(item, section));
        }

        _selectedSection = section;
        OnPropertyChanged(
            nameof(SelectedSection),
            nameof(IsTasksSection),
            nameof(IsProvidersSection),
            nameof(IsNetworkSection),
            nameof(IsDiagnosticsSection),
            nameof(IsAppearanceSection),
            nameof(IsNotWiredSection),
            nameof(NotWiredTitle),
            nameof(NotWiredBody),
            nameof(NotWiredRequirement),
            nameof(ShowClearCacheDanger),
            nameof(ShowBackupDanger),
            nameof(SectionSummary));
    }

    private ConsoleSectionItem Section(
        ConsoleSectionId id,
        string index,
        string label,
        string summary,
        bool isWired) =>
        new(id, index, label, summary, isWired, SelectSection);

    // ── V11R-INT-0 workspace context (section + real ScrollViewer offset) ───────────────────

    /// <summary>Raised when the shell activates this space and the view must restore its scroll offset.</summary>
    public event EventHandler? ScrollRestoreRequested;

    /// <summary>Live offset of the section content ScrollViewer; the shell persists it per space.</summary>
    public double ScrollOffsetY
    {
        get => _state.ConsoleView.ScrollOffsetY;
        set
        {
            if (Math.Abs(_state.ConsoleView.ScrollOffsetY - value) < 0.5)
            {
                return;
            }

            _state.ConsoleView.ScrollOffsetY = value;
            OnPropertyChanged();
        }
    }

    /// <summary>Contract §6.1 OnDeactivated: flush selected section + scroll into the shell state.</summary>
    public void CaptureViewState(SpaceViewState view)
    {
        view.FilterKey = _selectedSection.Id.ToString();
        view.ScrollOffsetY = ScrollOffsetY;
    }

    /// <summary>Contract §6.1 OnActivated: restore the selected section and scroll offset.</summary>
    public void RestoreViewState(SpaceViewState view)
    {
        if (Enum.TryParse<ConsoleSectionId>(view.FilterKey, out var sectionId))
        {
            SelectSectionById(sectionId);
        }

        ScrollOffsetY = view.ScrollOffsetY;
        ScrollRestoreRequested?.Invoke(this, EventArgs.Empty);
    }
    // ── Shared state ─────────────────────────────────────────────────────────────────────

    public bool IsLoading
    {
        get => _isLoading;
        private set => Set(ref _isLoading, value);
    }

    public string? ErrorMessage
    {
        get => _errorMessage;
        private set
        {
            if (Set(ref _errorMessage, value))
            {
                OnPropertyChanged(nameof(HasError));
            }
        }
    }

    public bool HasError => !string.IsNullOrWhiteSpace(ErrorMessage);

    public string StatusMessage
    {
        get => _statusMessage;
        private set
        {
            if (Set(ref _statusMessage, value))
            {
                OnPropertyChanged(nameof(HasStatus));
            }
        }
    }

    public bool HasStatus => _statusMessage.Length > 0;

    public string HostStateText => _hostStateText;

    public string HostStatusLine => _hostStatusLine;

    public string HostModeLine => _hostModeLine;

    public string HostErrorCodeText => _hostErrorCodeText;

    public string HostWireFrameText => _hostWireFrameText;

    public string AppearanceText => _isDarkTheme() ? "深色（Dark）" : "浅色（Light）";

    public RelayCommand ToggleAppearanceCommand { get; }

    public RelayCommand OpenThemeStudioCommand { get; }

    public RelayCommand OpenStudioCommand { get; }

    public RelayCommand RequestClearCacheCommand { get; }

    public RelayCommand RequestCreateBackupCommand { get; }

    public RelayCommand RequestDeleteBackupCommand { get; }

    // ── ① 任务与队列（真实 IRunController；无可列 Run 时要求显式 run_id） ─────────────
    //
    // The frozen contract has no "list runs" command, so the section takes an explicit run id and
    // reads IHostController.GetRunSnapshotAsync / GetTaskProjectionAsync (V11R-A-2) — the same source
    // V11R-B-4 will use. Polling is independent here but never fabricates progress: every counter comes
    // from the Core projection and missing counters render as "—".

    public ObservableCollection<RunStageRowViewModel> RunStages { get; }

    public ObservableCollection<RunRowViewModel> RunRows { get; }

    public string RunIdInput
    {
        get => _runIdInput;
        set => Set(ref _runIdInput, value);
    }

    /// <summary>Restart / Retry Failed require a caller-supplied idempotency key (R-08: never silent).</summary>
    public string RunIdempotencyKey
    {
        get => _runIdempotencyKey;
        set => Set(ref _runIdempotencyKey, value);
    }

    public bool IsRunPollingEnabled
    {
        get => _runMonitor.IsPollingEnabled;
        set
        {
            _runPollingPreferred = value;
            _runMonitor.SetPollingEnabled(value);
        }
    }

    /// <summary>
    /// R-24: entering the Console with a loaded Run resumes the shared mouse-free poller and performs one
    /// immediate refresh, so the snapshot/projection request counter grows deterministically on re-entry.
    /// </summary>
    public void EnterWorkspace()
    {
        if (!HasRunLoaded || !_runPollingPreferred)
        {
            return;
        }

        _runMonitor.SetPollingEnabled(true);
        _ = _runMonitor.RefreshAsync();
    }

    /// <summary>
    /// R-24: leaving the Console pauses the shared poller (no background Host reads while the Console is
    /// not observable). The shell StatusBand keeps the last shared snapshot; re-entry resumes polling.
    /// </summary>
    public void LeaveWorkspace() => _runMonitor.SetPollingEnabled(false);

    public bool HasRunLoaded
    {
        get => _hasRunLoaded;
        private set => Set(ref _hasRunLoaded, value);
    }

    public string RunStatusText
    {
        get => _runStatusText;
        private set => Set(ref _runStatusText, value);
    }

    public string RunCommandText
    {
        get => _runCommandText;
        private set => Set(ref _runCommandText, value);
    }

    public string RunScopeText
    {
        get => _runScopeText;
        private set => Set(ref _runScopeText, value);
    }

    public string RunProgressText
    {
        get => _runProgressText;
        private set => Set(ref _runProgressText, value);
    }

    public string RunCountsText
    {
        get => _runCountsText;
        private set => Set(ref _runCountsText, value);
    }

    public string RunCurrentStepText
    {
        get => _runCurrentStepText;
        private set => Set(ref _runCurrentStepText, value);
    }

    public string RunBlockedText
    {
        get => _runBlockedText;
        private set => Set(ref _runBlockedText, value);
    }

    public bool RunCanPause
    {
        get => _runCanPause;
        private set => Set(ref _runCanPause, value);
    }

    public bool RunCanStop
    {
        get => _runCanStop;
        private set => Set(ref _runCanStop, value);
    }

    public bool RunCanContinue
    {
        get => _runCanContinue;
        private set => Set(ref _runCanContinue, value);
    }

    public bool RunCanRestart
    {
        get => _runCanRestart;
        private set => Set(ref _runCanRestart, value);
    }

    public bool RunCanResumeBlocked
    {
        get => _runCanResumeBlocked;
        private set => Set(ref _runCanResumeBlocked, value);
    }

    public bool RunCanRetryFailed
    {
        get => _runCanRetryFailed;
        private set => Set(ref _runCanRetryFailed, value);
    }

    public string RunSourceNote =>
        "数据同源：IRunController（V11R-A-2）经壳共享 RunStatusMonitor（R-24）单次快照/投影；进入 Console 恢复轮询、离开暂停，不另造状态。";

    public RelayCommand LoadRunCommand { get; }

    public RelayCommand RefreshRunCommand { get; }

    public RelayCommand PauseRunCommand { get; }

    public RelayCommand ContinueRunCommand { get; }

    public RelayCommand StopRunCommand { get; }

    public RelayCommand RestartRunCommand { get; }

    public RelayCommand ResumeBlockedRunCommand { get; }

    public RelayCommand RetryFailedRunCommand { get; }

    /// <summary>Test seam: pauses the SHARED poller (R-24); the tracked run + snapshot stay intact.</summary>
    public void StopRunPolling()
    {
        _runPollingPreferred = false;
        _runMonitor.SetPollingEnabled(false);
    }

    private async Task LoadRunAsync()
    {
        var runId = RunIdInput.Trim();
        if (runId.Length == 0)
        {
            _notify("请输入 run_id：冻结契约没有「列出 Run」命令，run id 由工位批次或外部记录提供", NmStatus.Blocked);
            return;
        }

        _runMonitor.Track(runId);
        // Track starts the shared refresh; only await it when no snapshot exists yet, so StatusBand +
        // Console share exactly one Host read per poll (R-24).
        if (!_runMonitor.HasSnapshot)
        {
            await _runMonitor.RefreshAsync().ConfigureAwait(true);
        }

        if (_runMonitor.Snapshot is null && _runMonitor.Projection is null)
        {
            _notify($"Run 读取被拒绝或不存在：{RunFailureCode()}", NmStatus.Failed);
            return;
        }

        ApplyRun(runId, _runMonitor.Snapshot, _runMonitor.Projection);
    }

    private async Task RefreshRunAsync(bool notifyFailure)
    {
        var runId = _runMonitor.RunId ?? _runSnapshot?.RunId ?? RunIdInput.Trim();
        if (runId.Length == 0)
        {
            return;
        }

        if (!string.Equals(_runMonitor.RunId, runId, StringComparison.Ordinal))
        {
            _runMonitor.Track(runId);
        }

        await _runMonitor.RefreshAsync().ConfigureAwait(true);
        var snapshot = _runMonitor.Snapshot;
        var projection = _runMonitor.Projection;
        if (snapshot is null && projection is null)
        {
            if (notifyFailure)
            {
                _notify($"Run 读取被拒绝或不存在：{RunFailureCode()}", NmStatus.Failed);
            }

            return;
        }

        ApplyRun(runId, snapshot, projection);
    }

    private string RunFailureCode()
    {
        var snapshot = _controller.Snapshot;
        if (!string.IsNullOrEmpty(snapshot.ErrorCode))
        {
            return snapshot.ErrorCode;
        }

        return string.IsNullOrEmpty(snapshot.LastError) ? "UNKNOWN" : snapshot.LastError;
    }

    private void ApplyRun(string runId, RunSnapshotInfo? snapshot, TaskProjectionInfo? projection)
    {
        _runSnapshot = snapshot;
        _runProjection = projection;
        HasRunLoaded = true;
        RunIdInput = runId;

        var status = projection?.RunStatus ?? snapshot?.Status ?? string.Empty;
        RunStatusText = string.IsNullOrEmpty(status) ? "未知" : ConsoleStatusText.RunState(status);
        RunCommandText = snapshot is null || string.IsNullOrEmpty(snapshot.Command) ? "—" : snapshot.Command;
        RunScopeText = DescribeScope(snapshot?.Scope);
        RunProgressText = projection?.OverallProgress is { } progress ? progress.ToString("P0") : "—";
        RunCountsText = DescribeCounts(projection?.Counts);
        RunCurrentStepText = string.IsNullOrEmpty(projection?.CurrentStepType) ? "—" : projection!.CurrentStepType!;
        RunBlockedText = projection is null || projection.BlockedReasons.Count == 0
            ? "无"
            : string.Join("；", projection.BlockedReasons);

        RunStages.Clear();
        if (projection is not null)
        {
            foreach (var stage in projection.StepFlow)
            {
                RunStages.Add(new RunStageRowViewModel(stage));
            }
        }

        RunRows.Clear();
        if (projection is not null)
        {
            var tasksByPage = projection.Tasks
                .GroupBy(task => task.PageId, StringComparer.Ordinal)
                .ToDictionary(group => group.Key, group => group.First(), StringComparer.Ordinal);
            foreach (var row in projection.Rows)
            {
                tasksByPage.TryGetValue(row.PageId, out var task);
                RunRows.Add(new RunRowViewModel(row, task));
            }
        }

        var controls = projection?.Controls;
        RunCanPause = controls?.CanPause ?? false;
        RunCanStop = controls?.CanStop ?? false;
        RunCanContinue = controls?.CanContinue ?? false;
        RunCanRestart = controls?.CanRestart ?? false;
        RunCanRetryFailed = controls?.CanRetryFailed ?? false;
        RunCanResumeBlocked = controls?.CanContinue ?? false;

        OnPropertyChanged(
            nameof(RunStatusText),
            nameof(RunCommandText),
            nameof(RunScopeText),
            nameof(RunProgressText),
            nameof(RunCountsText),
            nameof(RunCurrentStepText),
            nameof(RunBlockedText),
            nameof(HasRunLoaded));
    }

    private static string DescribeScope(RunScopeInfo? scope)
    {
        if (scope is null || string.IsNullOrEmpty(scope.Kind))
        {
            return "—";
        }

        return scope.Kind switch
        {
            "book" => $"book: {scope.BookId}",
            "chapter" => $"chapter: {scope.ChapterId}",
            "page" => $"page: {scope.PageId}",
            "region" => $"region: {scope.RegionId}",
            "page_selection" => $"page_selection: {scope.PageIds?.Count ?? 0} 页",
            _ => scope.Kind,
        };
    }

    private static string DescribeCounts(RunCountsInfo? counts)
    {
        if (counts is null)
        {
            return "—";
        }

        static string Value(int? value) => value?.ToString(System.Globalization.CultureInfo.InvariantCulture) ?? "—";

        return $"总 {Value(counts.Total)} · 完成 {Value(counts.Completed)} · 失败 {Value(counts.Failed)} · " +
               $"跳过 {Value(counts.Skipped)} · 阻塞 {Value(counts.Blocked)} · 等待 {Value(counts.Waiting)} · 处理中 {Value(counts.Processing)}";
    }

    private void RequestRunControl(RunControlAction action)
    {
        var runId = _runSnapshot?.RunId ?? RunIdInput.Trim();
        if (runId.Length == 0)
        {
            _notify("请先加载一个 Run（输入 run_id 并读取）", NmStatus.Blocked);
            return;
        }

        if (action == RunControlAction.Restart && string.IsNullOrWhiteSpace(RunIdempotencyKey))
        {
            _notify("Restart 需要幂等键：请在「幂等键」框填写（R-08：UI 不静默生成）", NmStatus.Blocked);
            return;
        }

        if (action == RunControlAction.Stop)
        {
            _requestConfirm(new ConfirmRequest(
                "停止当前 Run",
                $"将停止 Run「{runId}」：进行中的步骤会终止，未完成页需要重新启动 Run 才能继续。" +
                "已完成的输出保留；此操作不可撤销（可取消）。",
                "停止 Run",
                IsDanger: true,
                OnConfirm: () => _ = ControlRunAsync(runId, action, null)));
            return;
        }

        _ = ControlRunAsync(runId, action, action == RunControlAction.Restart ? RunIdempotencyKey.Trim() : null);
    }

    private void RequestStopRun() => RequestRunControl(RunControlAction.Stop);

    private async Task ControlRunAsync(string runId, RunControlAction action, string? idempotencyKey)
    {
        try
        {
            var result = await _controller
                .ControlRunAsync(runId, action, idempotencyKey)
                .ConfigureAwait(true);
            if (result is null)
            {
                _notify($"Run 控制被拒绝：{RunFailureCode()}", NmStatus.Failed);
                return;
            }

            _notify(
                result.NewRunId is { Length: > 0 }
                    ? $"Run 已{ActionText(action)}，新 Run：{result.NewRunId}"
                    : $"Run 已{ActionText(action)}（状态：{ConsoleStatusText.RunState(result.Status)}）",
                NmStatus.Done);
            await RefreshRunAsync(notifyFailure: false).ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("Run 控制失败：Host 不可用", NmStatus.Failed);
        }
    }

    private static string ActionText(RunControlAction action) => action switch
    {
        RunControlAction.Pause => "暂停",
        RunControlAction.Resume => "继续",
        RunControlAction.Stop => "停止",
        RunControlAction.Restart => "重启",
        _ => action.ToString(),
    };

    private async Task ResumeBlockedRunAsync()
    {
        var runId = _runSnapshot?.RunId ?? RunIdInput.Trim();
        if (runId.Length == 0)
        {
            _notify("请先加载一个 Run", NmStatus.Blocked);
            return;
        }

        try
        {
            var result = await _controller.ResumeBlockedRunAsync(runId).ConfigureAwait(true);
            if (result is null)
            {
                _notify($"恢复阻塞被拒绝：{RunFailureCode()}", NmStatus.Failed);
                return;
            }

            _notify("已请求恢复阻塞 Run", NmStatus.Done);
            await RefreshRunAsync(notifyFailure: false).ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("恢复阻塞失败：Host 不可用", NmStatus.Failed);
        }
    }

    private async Task RetryFailedRunAsync()
    {
        var runId = _runSnapshot?.RunId ?? RunIdInput.Trim();
        if (runId.Length == 0)
        {
            _notify("请先加载一个 Run", NmStatus.Blocked);
            return;
        }

        if (string.IsNullOrWhiteSpace(RunIdempotencyKey))
        {
            _notify("重试失败目标需要幂等键：请在「幂等键」框填写（R-08：UI 不静默生成）", NmStatus.Blocked);
            return;
        }

        try
        {
            var result = await _controller
                .RetryFailedTargetsAsync(runId, RunIdempotencyKey.Trim())
                .ConfigureAwait(true);
            if (result is null)
            {
                _notify($"重试失败目标被拒绝：{RunFailureCode()}", NmStatus.Failed);
                return;
            }

            _notify(
                result.NewRunId is { Length: > 0 } ? $"已创建重试 Run：{result.NewRunId}" : "已请求重试失败目标",
                NmStatus.Done);
            await RefreshRunAsync(notifyFailure: false).ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("重试失败目标失败：Host 不可用", NmStatus.Failed);
        }
    }
    // ── Provider section ─────────────────────────────────────────────────────────────────

    public ObservableCollection<ProviderProfileRowViewModel> ProviderProfiles { get; }

    public ObservableCollection<CredentialTargetRowViewModel> CredentialTargets { get; }

    public ObservableCollection<CapabilityBindingRowViewModel> CapabilityBindings { get; }

    public ObservableCollection<ConsoleOption> ProviderNetworkOptions { get; }

    public ObservableCollection<BindingScopeOption> BindingScopeOptions { get; }

    public bool IsProviderFormOpen
    {
        get => _isProviderFormOpen;
        private set => Set(ref _isProviderFormOpen, value);
    }

    public string ProviderFormTitle
    {
        get => _providerFormTitle;
        private set => Set(ref _providerFormTitle, value);
    }

    public string FormProviderId
    {
        get => _formProviderId;
        set => Set(ref _formProviderId, value);
    }

    public string FormDisplayName
    {
        get => _formDisplayName;
        set => Set(ref _formDisplayName, value);
    }

    public string FormEndpoint
    {
        get => _formEndpoint;
        set => Set(ref _formEndpoint, value);
    }

    public string FormModel
    {
        get => _formModel;
        set => Set(ref _formModel, value);
    }

    public bool FormEnabled
    {
        get => _formEnabled;
        set => Set(ref _formEnabled, value);
    }

    public bool FormCapOcr
    {
        get => _formCapOcr;
        set => Set(ref _formCapOcr, value);
    }

    public bool FormCapTranslation
    {
        get => _formCapTranslation;
        set => Set(ref _formCapTranslation, value);
    }

    public bool FormCapInpaint
    {
        get => _formCapInpaint;
        set => Set(ref _formCapInpaint, value);
    }

    public bool FormCapDetection
    {
        get => _formCapDetection;
        set => Set(ref _formCapDetection, value);
    }

    public bool FormCapRendering
    {
        get => _formCapRendering;
        set => Set(ref _formCapRendering, value);
    }

    public int FormNetworkIndex
    {
        get => _formNetworkIndex;
        set => Set(ref _formNetworkIndex, value);
    }

    public ProviderProfileRowViewModel? SelectedProvider
    {
        get => _selectedProvider;
        private set
        {
            if (Set(ref _selectedProvider, value))
            {
                OnPropertyChanged(nameof(SelectedProviderHint));
            }
        }
    }

    public string SelectedProviderHint => SelectedProvider is null
        ? "未选择 Provider 配置（用于能力绑定 / 网络测试）"
        : $"当前 Provider：{SelectedProvider.DisplayName}";

    public int BindingScopeIndex
    {
        get => _bindingScopeIndex;
        set
        {
            if (Set(ref _bindingScopeIndex, value))
            {
                OnPropertyChanged(nameof(BindingScopeHint));
            }
        }
    }

    public string BindingScopeHint
    {
        get
        {
            if (BindingScopeOptions.Count == 0)
            {
                return "作用域：全局";
            }

            var index = Math.Clamp(BindingScopeIndex, 0, BindingScopeOptions.Count - 1);
            return "作用域：" + BindingScopeOptions[index].Label;
        }
    }

    public RelayCommand NewProviderCommand { get; }

    public RelayCommand CancelProviderCommand { get; }

    public RelayCommand SaveProviderCommand { get; }

    public RelayCommand NewNetworkCommand { get; }

    public RelayCommand CancelNetworkCommand { get; }

    public RelayCommand SaveNetworkCommand { get; }

    public RelayCommand EditSelectedProviderCommand { get; }

    public RelayCommand DeleteSelectedProviderCommand { get; }

    public RelayCommand EditSelectedNetworkCommand { get; }

    public RelayCommand SetDefaultSelectedNetworkCommand { get; }

    public RelayCommand TestSelectedNetworkCommand { get; }

    public RelayCommand DeleteSelectedNetworkCommand { get; }

    public RelayCommand RefreshProvidersCommand { get; }

    public RelayCommand RefreshNetworkCommand { get; }

    public RelayCommand RefreshCredentialsViewCommand { get; }

    public RelayCommand RefreshBindingsViewCommand { get; }

    private void NewProviderForm()
    {
        _editingProviderProfileId = null;
        ProviderFormTitle = "新建 Provider 配置";
        FormProviderId = string.Empty;
        FormDisplayName = string.Empty;
        FormEndpoint = string.Empty;
        FormModel = string.Empty;
        FormEnabled = true;
        FormCapOcr = true;
        FormCapTranslation = true;
        FormCapInpaint = false;
        FormCapDetection = false;
        FormCapRendering = false;
        FormNetworkIndex = 0;
        IsProviderFormOpen = true;
    }

    private void EditProvider(ProviderProfileRowViewModel row)
    {
        SelectProvider(row);
        _editingProviderProfileId = row.ProfileId;
        ProviderFormTitle = $"编辑 Provider 配置：{row.DisplayName}";
        FormProviderId = row.ProviderId;
        FormDisplayName = row.DisplayName;
        FormEndpoint = row.Endpoint;
        FormModel = row.Model;
        FormEnabled = row.Enabled;
        var capabilities = row.CapabilitiesText.Split(" / ", StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        FormCapOcr = capabilities.Contains(SettingsCapabilities.Ocr);
        FormCapTranslation = capabilities.Contains(SettingsCapabilities.Translation);
        FormCapInpaint = capabilities.Contains(SettingsCapabilities.Inpaint);
        FormCapDetection = capabilities.Contains(SettingsCapabilities.Detection);
        FormCapRendering = capabilities.Contains(SettingsCapabilities.Rendering);
        FormNetworkIndex = 0;
        if (row.NetworkProfileId is { Length: > 0 } networkId)
        {
            for (var index = 1; index < ProviderNetworkOptions.Count; index++)
            {
                if (string.Equals(ProviderNetworkOptions[index].Key, networkId, StringComparison.Ordinal))
                {
                    FormNetworkIndex = index;
                    break;
                }
            }
        }

        IsProviderFormOpen = true;
    }

    private async Task SaveProviderAsync()
    {
        var providerId = FormProviderId.Trim();
        var displayName = FormDisplayName.Trim();
        if (providerId.Length == 0 || displayName.Length == 0)
        {
            _notify("Provider 配置无效：provider_id 与显示名称不能为空", NmStatus.Blocked);
            return;
        }

        var capabilities = new List<string>();
        if (FormCapOcr)
        {
            capabilities.Add(SettingsCapabilities.Ocr);
        }

        if (FormCapTranslation)
        {
            capabilities.Add(SettingsCapabilities.Translation);
        }

        if (FormCapInpaint)
        {
            capabilities.Add(SettingsCapabilities.Inpaint);
        }

        if (FormCapDetection)
        {
            capabilities.Add(SettingsCapabilities.Detection);
        }

        if (FormCapRendering)
        {
            capabilities.Add(SettingsCapabilities.Rendering);
        }

        if (capabilities.Count == 0)
        {
            _notify("Provider 配置无效：至少选择一个能力", NmStatus.Blocked);
            return;
        }

        var networkId = FormNetworkIndex > 0 && FormNetworkIndex < ProviderNetworkOptions.Count
            ? ProviderNetworkOptions[FormNetworkIndex].Key
            : null;
        var draft = new ProviderProfileDraft(
            providerId,
            displayName,
            capabilities,
            FormEndpoint.Trim(),
            FormModel.Trim(),
            string.IsNullOrWhiteSpace(networkId) ? null : networkId,
            FormEnabled);

        try
        {
            var result = await _controller
                .SaveProviderProfileAsync(_editingProviderProfileId, draft)
                .ConfigureAwait(true);
            if (!result.IsSuccess)
            {
                _notify(
                    $"保存 Provider 失败：{DescribeSettingsFailure(result)}",
                    NmStatus.Failed);
                return;
            }

            IsProviderFormOpen = false;
            _notify($"已保存 Provider 配置「{displayName}」", NmStatus.Done);
            await RefreshProvidersAsync().ConfigureAwait(true);
            await RefreshCredentialsAsync().ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("保存 Provider 失败：Host 不可用", NmStatus.Failed);
        }
    }

    private void DeleteProvider(ProviderProfileRowViewModel row)
    {
        _requestConfirm(new ConfirmRequest(
            "删除 Provider 配置",
            $"将删除 Provider 配置「{row.DisplayName}」（{row.CapabilitiesText}）。" +
            "使用它的能力绑定会立即失效，相关已保存密钥由 Core 清理。此操作不可撤销。",
            "删除配置",
            IsDanger: true,
            OnConfirm: () => _ = DeleteProviderAsync(row)));
    }

    private async Task DeleteProviderAsync(ProviderProfileRowViewModel row)
    {
        try
        {
            var result = await _controller.DeleteProviderProfileAsync(row.ProfileId).ConfigureAwait(true);
            if (!result.IsSuccess)
            {
                _notify($"删除 Provider 失败：{DescribeSettingsFailure(result)}", NmStatus.Failed);
                return;
            }

            _notify($"已删除 Provider 配置「{row.DisplayName}」", NmStatus.Done);
            await RefreshProvidersAsync().ConfigureAwait(true);
            await RefreshCredentialsAsync().ConfigureAwait(true);
            await RefreshBindingsAsync().ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("删除 Provider 失败：Host 不可用", NmStatus.Failed);
        }
    }

    private void SelectProvider(ProviderProfileRowViewModel row)
    {
        foreach (var item in ProviderProfiles)
        {
            item.SetSelected(ReferenceEquals(item, row));
        }

        SelectedProvider = row;
    }

    private void PutCredential(CredentialTargetRowViewModel row)
    {
        if (!row.HasSecretInput)
        {
            _notify("请先在密码框输入密钥（输入内容不会保存到 UI 或证据中）", NmStatus.Blocked);
            return;
        }

        if (!row.CanPut)
        {
            return;
        }

        _ = PutCredentialAsync(row);
    }

    private async Task PutCredentialAsync(CredentialTargetRowViewModel row)
    {
        row.IsBusy = true;
        try
        {
            var intent = row.IsConfigured ? "replace" : "create";
            var result = await _controller
                .PutCredentialAsync(row.Kind, row.OwnerId, intent, row.SecretInput)
                .ConfigureAwait(true);

            // SECURITY: clear the transient secret on success no matter what the Core said afterwards.
            row.ClearSecretInput();
            if (result.IsSuccess)
            {
                row.UpdateState("configured");
                row.RowStatusText = "已保存（Core 确认）";
                _notify($"密钥已保存：{row.TargetText}", NmStatus.Done);
            }
            else
            {
                row.RowStatusText = $"保存失败：{DescribeCredentialFailure(result)}";
                _notify($"密钥保存失败：{DescribeCredentialFailure(result)}", NmStatus.Failed);
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            row.ClearSecretInput();
            row.RowStatusText = "保存失败：Host 不可用";
            _notify("密钥保存失败：Host 不可用", NmStatus.Failed);
        }
        finally
        {
            row.IsBusy = false;
        }
    }

    private void ClearCredential(CredentialTargetRowViewModel row)
    {
        _requestConfirm(new ConfirmRequest(
            "清除已保存密钥",
            $"将清除「{row.TargetText}」的密钥。依赖它的能力会立即不可用，且不可恢复（需要重新输入）。",
            "清除密钥",
            IsDanger: true,
            OnConfirm: () => _ = ClearCredentialAsync(row)));
    }

    private async Task ClearCredentialAsync(CredentialTargetRowViewModel row)
    {
        row.IsBusy = true;
        try
        {
            var result = await _controller.ClearCredentialAsync(row.Kind, row.OwnerId).ConfigureAwait(true);
            if (result.IsSuccess)
            {
                row.UpdateState("missing");
                row.RowStatusText = "已清除（Core 确认）";
                _notify($"密钥已清除：{row.TargetText}", NmStatus.Done);
                return;
            }

            _notify($"清除密钥失败：{DescribeCredentialFailure(result)}", NmStatus.Failed);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("清除密钥失败：Host 不可用", NmStatus.Failed);
        }
        finally
        {
            row.IsBusy = false;
        }
    }

    private void BindCapability(CapabilityBindingRowViewModel row)
    {
        if (SelectedProvider is not { } provider)
        {
            _notify("请先在 Provider 列表选择一条配置，再设置能力绑定", NmStatus.Blocked);
            return;
        }

        _ = BindCapabilityAsync(row, provider);
    }

    private async Task BindCapabilityAsync(CapabilityBindingRowViewModel row, ProviderProfileRowViewModel provider)
    {
        var scope = CurrentBindingScope();
        try
        {
            var result = await _controller
                .SetProviderBindingAsync(scope, row.Capability, provider.ProfileId)
                .ConfigureAwait(true);
            if (!result.IsSuccess)
            {
                _notify($"设置能力绑定失败：{DescribeSettingsFailure(result)}", NmStatus.Failed);
                return;
            }

            _notify($"已绑定 {row.Title} → {provider.DisplayName}（{BindingScopeHint}）", NmStatus.Done);
            await RefreshBindingsAsync().ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("设置能力绑定失败：Host 不可用", NmStatus.Failed);
        }
    }

    private void ClearBinding(CapabilityBindingRowViewModel row)
    {
        _ = ClearBindingAsync(row);
    }

    private async Task ClearBindingAsync(CapabilityBindingRowViewModel row)
    {
        var scope = CurrentBindingScope();
        try
        {
            var result = await _controller.ClearProviderBindingAsync(scope, row.Capability).ConfigureAwait(true);
            if (!result.IsSuccess)
            {
                _notify($"清除能力绑定失败：{DescribeSettingsFailure(result)}", NmStatus.Failed);
                return;
            }

            _notify($"已清除 {row.Title} 的能力绑定（{BindingScopeHint}）", NmStatus.Done);
            await RefreshBindingsAsync().ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("清除能力绑定失败：Host 不可用", NmStatus.Failed);
        }
    }

    private ProfileBindingScope CurrentBindingScope()
    {
        if (BindingScopeOptions.Count == 0)
        {
            return new ProfileBindingScope(ProfileBindingScope.Global);
        }

        var index = Math.Clamp(BindingScopeIndex, 0, BindingScopeOptions.Count - 1);
        var option = BindingScopeOptions[index];
        return option.Kind switch
        {
            ProfileBindingScope.Book => new ProfileBindingScope(ProfileBindingScope.Book, BookId: _state.Selection.BookId),
            ProfileBindingScope.Chapter => new ProfileBindingScope(
                ProfileBindingScope.Chapter,
                BookId: _state.Selection.BookId,
                ChapterId: _state.Selection.ChapterId),
            _ => new ProfileBindingScope(ProfileBindingScope.Global),
        };
    }

    private void RebuildCapabilityBindings()
    {
        CapabilityBindings.Clear();
        foreach (var capability in SettingsCapabilities.All)
        {
            CapabilityBindings.Add(new CapabilityBindingRowViewModel(capability, BindCapability, ClearBinding));
        }
    }

    private void RebuildBindingScopes()
    {
        var selectedKind = BindingScopeOptions.Count > 0 &&
                           BindingScopeIndex >= 0 &&
                           BindingScopeIndex < BindingScopeOptions.Count
            ? BindingScopeOptions[BindingScopeIndex].Kind
            : ProfileBindingScope.Global;

        BindingScopeOptions.Clear();
        BindingScopeOptions.Add(new BindingScopeOption(ProfileBindingScope.Global, "全局（global）", true));
        var hasBook = _state.Selection.HasBook;
        var hasChapter = _state.Selection.HasChapter;
        BindingScopeOptions.Add(new BindingScopeOption(
            ProfileBindingScope.Book,
            hasBook ? $"当前作品（book: {_state.Selection.BookId}）" : "当前作品（未选择）",
            hasBook));
        BindingScopeOptions.Add(new BindingScopeOption(
            ProfileBindingScope.Chapter,
            hasChapter ? $"当前章节（chapter: {_state.Selection.ChapterId}）" : "当前章节（未选择）",
            hasChapter));

        var index = 0;
        for (var candidate = 0; candidate < BindingScopeOptions.Count; candidate++)
        {
            if (string.Equals(BindingScopeOptions[candidate].Kind, selectedKind, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        BindingScopeIndex = index;
        OnPropertyChanged(nameof(BindingScopeHint));
    }

    // ── Network section ──────────────────────────────────────────────────────────────────

    public ObservableCollection<NetworkProfileRowViewModel> NetworkProfiles { get; }

    public ObservableCollection<ConsoleOption> NetworkModeOptions { get; }

    public bool IsNetworkFormOpen
    {
        get => _isNetworkFormOpen;
        private set => Set(ref _isNetworkFormOpen, value);
    }

    public string NetworkFormTitle
    {
        get => _networkFormTitle;
        private set => Set(ref _networkFormTitle, value);
    }

    public string FormNetworkName
    {
        get => _formNetworkName;
        set => Set(ref _formNetworkName, value);
    }

    public string FormProxyEndpoint
    {
        get => _formProxyEndpoint;
        set => Set(ref _formProxyEndpoint, value);
    }

    public bool FormVerifyTls
    {
        get => _formVerifyTls;
        set => Set(ref _formVerifyTls, value);
    }

    public bool FormConfirmDisableTls
    {
        get => _formConfirmDisableTls;
        set => Set(ref _formConfirmDisableTls, value);
    }

    public bool FormAllowFallback
    {
        get => _formAllowFallback;
        set => Set(ref _formAllowFallback, value);
    }

    public int FormNetworkModeIndex
    {
        get
        {
            for (var index = 0; index < NetworkModeOptions.Count; index++)
            {
                if (string.Equals(NetworkModeOptions[index].Key, _formNetworkMode, StringComparison.Ordinal))
                {
                    return index;
                }
            }

            return 0;
        }
        set
        {
            if (value >= 0 && value < NetworkModeOptions.Count)
            {
                _formNetworkMode = NetworkModeOptions[value].Key;
                OnPropertyChanged();
            }
        }
    }

    public NetworkProfileRowViewModel? SelectedNetwork
    {
        get => _selectedNetwork;
        private set => Set(ref _selectedNetwork, value);
    }

    public string DefaultNetworkText
    {
        get => _defaultNetworkText;
        private set => Set(ref _defaultNetworkText, value);
    }

    public string NetworkTestText
    {
        get => _networkTestText;
        private set => Set(ref _networkTestText, value);
    }

    public string NetworkResolveText
    {
        get => _networkResolveText;
        private set => Set(ref _networkResolveText, value);
    }

    private void NewNetworkForm()
    {
        _editingNetworkProfileId = null;
        NetworkFormTitle = "新建网络配置";
        FormNetworkName = string.Empty;
        _formNetworkMode = NetworkModes.System;
        FormProxyEndpoint = string.Empty;
        FormVerifyTls = true;
        FormConfirmDisableTls = false;
        FormAllowFallback = false;
        OnPropertyChanged(nameof(FormNetworkModeIndex));
        IsNetworkFormOpen = true;
    }

    private void EditNetwork(NetworkProfileRowViewModel row)
    {
        SelectNetwork(row);
        _editingNetworkProfileId = row.NetworkProfileId;
        NetworkFormTitle = $"编辑网络配置：{row.DisplayName}";
        FormNetworkName = row.DisplayName;
        _formNetworkMode = row.Mode;
        FormProxyEndpoint = row.ProxyEndpoint;
        FormVerifyTls = row.VerifyTls;
        FormConfirmDisableTls = false;
        FormAllowFallback = row.AllowDirectFallback;
        OnPropertyChanged(nameof(FormNetworkModeIndex));
        IsNetworkFormOpen = true;
    }

    private async Task SaveNetworkAsync()
    {
        var displayName = FormNetworkName.Trim();
        if (displayName.Length == 0)
        {
            _notify("网络配置无效：显示名称不能为空", NmStatus.Blocked);
            return;
        }

        var mode = _formNetworkMode;
        var endpoint = FormProxyEndpoint.Trim();
        if (NetworkModes.RequiresProxyEndpoint(mode) && endpoint.Length == 0)
        {
            _notify($"网络配置无效：{mode} 模式需要代理端点（host:port）", NmStatus.Blocked);
            return;
        }

        if (!FormVerifyTls && !FormConfirmDisableTls)
        {
            _notify("关闭 TLS 校验前必须勾选「确认关闭 TLS 校验」（安全确认）", NmStatus.Blocked);
            return;
        }

        var draft = new NetworkProfileDraft(
            displayName,
            mode,
            endpoint.Length == 0 ? null : endpoint,
            FormVerifyTls,
            FormConfirmDisableTls,
            FormAllowFallback);

        try
        {
            var result = await _controller
                .SaveNetworkProfileAsync(_editingNetworkProfileId, draft)
                .ConfigureAwait(true);
            if (!result.IsSuccess)
            {
                _notify($"保存网络配置失败：{DescribeSettingsFailure(result)}", NmStatus.Failed);
                return;
            }

            IsNetworkFormOpen = false;
            _notify($"已保存网络配置「{displayName}」", NmStatus.Done);
            await RefreshNetworkAsync().ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("保存网络配置失败：Host 不可用", NmStatus.Failed);
        }
    }

    private void DeleteNetwork(NetworkProfileRowViewModel row)
    {
        _requestConfirm(new ConfirmRequest(
            "删除网络配置",
            $"将删除网络配置「{row.DisplayName}」（{row.Mode} · {row.EndpointText}）。" +
            "使用它的 Provider 会回退默认网络，代理密码由 Core 清理。此操作不可撤销。",
            "删除网络配置",
            IsDanger: true,
            OnConfirm: () => _ = DeleteNetworkAsync(row)));
    }

    private async Task DeleteNetworkAsync(NetworkProfileRowViewModel row)
    {
        try
        {
            var result = await _controller.DeleteNetworkProfileAsync(row.NetworkProfileId).ConfigureAwait(true);
            if (!result.IsSuccess)
            {
                _notify($"删除网络配置失败：{DescribeSettingsFailure(result)}", NmStatus.Failed);
                return;
            }

            _notify($"已删除网络配置「{row.DisplayName}」", NmStatus.Done);
            await RefreshNetworkAsync().ConfigureAwait(true);
            await RefreshCredentialsAsync().ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("删除网络配置失败：Host 不可用", NmStatus.Failed);
        }
    }

    private void SetDefaultNetwork(NetworkProfileRowViewModel row)
    {
        _ = SetDefaultNetworkAsync(row);
    }

    private async Task SetDefaultNetworkAsync(NetworkProfileRowViewModel row)
    {
        try
        {
            var result = await _controller.SetNetworkDefaultAsync(row.NetworkProfileId).ConfigureAwait(true);
            if (!result.IsSuccess)
            {
                _notify($"设置默认网络失败：{DescribeSettingsFailure(result)}", NmStatus.Failed);
                return;
            }

            _notify($"已将「{row.DisplayName}」设为默认网络", NmStatus.Done);
            await RefreshNetworkAsync().ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("设置默认网络失败：Host 不可用", NmStatus.Failed);
        }
    }

    private void TestNetwork(NetworkProfileRowViewModel row)
    {
        _ = TestNetworkAsync(row);
    }

    private async Task TestNetworkAsync(NetworkProfileRowViewModel row)
    {
        var providerId = SelectedProvider?.ProfileId;
        if (string.IsNullOrWhiteSpace(providerId))
        {
            _notify("网络测试需要 Provider 配置：请先在「Provider 与凭据」区选择一条配置", NmStatus.Blocked);
            return;
        }

        try
        {
            NetworkTestText = "测试中…";
            var result = await _controller
                .TestNetworkProfileAsync(row.NetworkProfileId, providerId)
                .ConfigureAwait(true);
            if (result is null)
            {
                NetworkTestText = "测试不可用：Host 未就绪或无真实 Core 探针（未伪造结果）";
                _notify("网络测试不可用：Host 未就绪或未返回真实结果", NmStatus.Blocked);
                return;
            }

            NetworkTestText = result.Summary;
            _notify(
                result.Status is "ok" or "success" or "passed" ? "网络连通测试通过" : "网络连通测试未通过，见测试明细",
                result.Status is "ok" or "success" or "passed" ? NmStatus.Done : NmStatus.Failed);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            NetworkTestText = "测试失败：Host 不可用";
            _notify("网络测试失败：Host 不可用", NmStatus.Failed);
        }
    }

    private void SelectNetwork(NetworkProfileRowViewModel row)
    {
        foreach (var item in NetworkProfiles)
        {
            item.SetSelected(ReferenceEquals(item, row));
        }

        SelectedNetwork = row;
    }

    // ── Diagnostics section ─────────────────────────────────────────────────────────────

    public ObservableCollection<ExportHistoryRowViewModel> ExportHistory { get; }

    public RelayCommand RefreshExportHistoryCommand { get; }

    private async Task RefreshExportHistoryAsync()
    {
        try
        {
            var history = await _controller.GetExportHistoryAsync().ConfigureAwait(true);
            ExportHistory.Clear();
            foreach (var entry in history.Take(20))
            {
                ExportHistory.Add(new ExportHistoryRowViewModel(entry, RevealExport));
            }

            StatusMessage = $"导出历史：{ExportHistory.Count} 条（经 Host/Core 读取）";
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            StatusMessage = "导出历史读取失败：Host 不可用";
        }
    }

    private void RevealExport(ExportHistoryRowViewModel row)
    {
        _ = RevealExportAsync(row);
    }

    private async Task RevealExportAsync(ExportHistoryRowViewModel row)
    {
        row.IsRevealing = true;
        try
        {
            var opened = await _controller.RevealExportFolderAsync(row.ExportId).ConfigureAwait(true);
            row.RevealText = opened ? "已请求 Host 打开目录" : "Host 未打开目录（拒绝或不可用）";
            if (!opened)
            {
                _notify("打开导出目录失败：Host 拒绝或不可用", NmStatus.Blocked);
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            row.RevealText = "打开失败：Host 不可用";
        }
        finally
        {
            row.IsRevealing = false;
        }
    }

    // ── Appearance section ──────────────────────────────────────────────────────────────

    private void ToggleAppearance()
    {
        _toggleTheme();
        OnPropertyChanged(nameof(AppearanceText));
    }

    // ── Not-wired sections / blocked dangerous actions ─────────────────────────────────

    private void RequestClearCache() => _requestConfirm(new ConfirmRequest(
        "清理缓存与过期版本（能力待接入）",
        "清理会删除可重建的缓存、缩略图与过期 revision 文件，可能使部分页面需要重新处理；" +
        "当前 IHostController 未暴露 cleanup_preview / cleanup_run，无法先展示影响面，因此不会执行任何删除。",
        "清理（能力待接入）",
        IsDanger: true,
        OnConfirm: () => _notify("清理缓存：能力待接入，未执行任何删除", NmStatus.Blocked),
        CanConfirm: false,
        BlockedReason: "能力待接入：Host 未暴露 cleanup_preview / cleanup_run 方法"));

    private void RequestCreateBackup() => _requestConfirm(new ConfirmRequest(
        "创建备份（能力待接入）",
        "备份会把当前库与配置打包为 .nmbak；当前 IHostController 未暴露 backup_list / backup_create，无法确认备份目录与体积，因此不会执行。",
        "创建备份（能力待接入）",
        IsDanger: false,
        OnConfirm: () => _notify("创建备份：能力待接入，未执行任何写入", NmStatus.Blocked),
        CanConfirm: false,
        BlockedReason: "能力待接入：Host 未暴露 backup_list / backup_create 方法"));

    private void RequestDeleteBackup() => _requestConfirm(new ConfirmRequest(
        "删除备份（能力待接入）",
        "删除备份会永久移除 .nmbak 文件且无法恢复；当前 IHostController 未暴露备份列表方法，无法确认文件与数量，因此不会执行删除。",
        "删除备份（能力待接入）",
        IsDanger: true,
        OnConfirm: () => _notify("删除备份：能力待接入，未执行任何删除", NmStatus.Blocked),
        CanConfirm: false,
        BlockedReason: "能力待接入：Host 未暴露备份列表 / 删除方法"));

    // ── Loading ─────────────────────────────────────────────────────────────────────────

    public async Task InitializeAsync(bool force = false)
    {
        if (_initialized && !force)
        {
            return;
        }

        _initialized = true;
        IsLoading = true;
        ErrorMessage = null;
        try
        {
            RefreshHostFacts();
            await RefreshProvidersAsync().ConfigureAwait(true);
            await RefreshCredentialsAsync().ConfigureAwait(true);
            await RefreshBindingsAsync().ConfigureAwait(true);
            await RefreshNetworkAsync().ConfigureAwait(true);
            await RefreshExportHistoryAsync().ConfigureAwait(true);
            StatusMessage = "控制台数据已从 Host 读取（Provider / 网络 / 凭据状态 / 导出历史）";
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            ErrorMessage = "控制台数据读取失败：Host 不可用";
        }
        finally
        {
            IsLoading = false;
        }
    }

    public async Task RefreshProvidersAsync()
    {
        var profiles = await _controller.ListProviderProfilesAsync().ConfigureAwait(true);
        ProviderProfiles.Clear();
        foreach (var profile in profiles)
        {
            ProviderProfiles.Add(new ProviderProfileRowViewModel(profile, SelectProvider, EditProvider, DeleteProvider));
        }

        ProviderNetworkOptions.Clear();
        ProviderNetworkOptions.Add(new ConsoleOption(string.Empty, "使用默认网络"));
        foreach (var network in NetworkProfiles)
        {
            ProviderNetworkOptions.Add(new ConsoleOption(network.NetworkProfileId, network.DisplayName));
        }

        if (ProviderProfiles.Count > 0 && SelectedProvider is null)
        {
            SelectProvider(ProviderProfiles[0]);
        }
    }

    public async Task RefreshCredentialsAsync()
    {
        var targets = await _controller.ListCredentialTargetsAsync().ConfigureAwait(true);
        CredentialTargets.Clear();
        foreach (var target in targets)
        {
            CredentialTargets.Add(new CredentialTargetRowViewModel(target, PutCredential, ClearCredential));
        }
    }

    public async Task RefreshBindingsAsync()
    {
        foreach (var row in CapabilityBindings)
        {
            try
            {
                var resolved = await _controller
                    .ResolveProviderBindingAsync(row.Capability)
                    .ConfigureAwait(true);
                if (resolved is null)
                {
                    row.Update(false, null, null);
                }
                else
                {
                    row.Update(!resolved.IsCleared, resolved.ProfileId, resolved.Source);
                }
            }
            catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
            {
                row.Update(false, null, "Host 不可用");
            }
        }
    }

    public async Task RefreshNetworkAsync()
    {
        var profiles = await _controller.ListNetworkProfilesAsync().ConfigureAwait(true);
        NetworkProfiles.Clear();
        foreach (var profile in profiles)
        {
            NetworkProfiles.Add(new NetworkProfileRowViewModel(
                profile,
                SelectNetwork,
                EditNetwork,
                SetDefaultNetwork,
                TestNetwork,
                DeleteNetwork));
        }

        var resolved = await _controller.ResolveNetworkProfileAsync(null).ConfigureAwait(true);
        DefaultNetworkText = resolved is null
            ? "默认网络：未知（Host 未就绪）"
            : $"默认网络：{resolved.Mode}" + (string.IsNullOrEmpty(resolved.NetworkProfileId) ? "（系统/直连）" : $" · {resolved.NetworkProfileId}");
        NetworkResolveText = resolved?.Summary ?? "默认网络：未知";
        foreach (var row in NetworkProfiles)
        {
            row.IsDefault = resolved is not null &&
                            string.Equals(row.NetworkProfileId, resolved.NetworkProfileId, StringComparison.Ordinal);
        }

        if (NetworkProfiles.Count > 0 && SelectedNetwork is null)
        {
            SelectNetwork(NetworkProfiles[0]);
        }

        ProviderNetworkOptions.Clear();
        ProviderNetworkOptions.Add(new ConsoleOption(string.Empty, "使用默认网络"));
        foreach (var network in NetworkProfiles)
        {
            ProviderNetworkOptions.Add(new ConsoleOption(network.NetworkProfileId, network.DisplayName));
        }
    }

    private void RefreshHostFacts()
    {
        var snapshot = _controller.Snapshot;
        _hostStateText = snapshot.State switch
        {
            HostViewState.Ready => "就绪",
            HostViewState.Starting => "启动中",
            HostViewState.AlreadyRunning => "已在运行",
            HostViewState.Failed => "失败",
            _ => "未知",
        };
        _hostStatusLine = snapshot.StatusLine;
        _hostModeLine = snapshot.ModeLine;
        // Security: only the typed code is rendered; the raw error message may contain paths.
        _hostErrorCodeText = string.IsNullOrEmpty(snapshot.ErrorCode)
            ? string.IsNullOrEmpty(snapshot.LastError) ? "无" : snapshot.LastError
            : snapshot.ErrorCode;
        _hostWireFrameText = snapshot.WireFrameCount.ToString(System.Globalization.CultureInfo.InvariantCulture);
        OnPropertyChanged(
            nameof(HostStateText),
            nameof(HostStatusLine),
            nameof(HostModeLine),
            nameof(HostErrorCodeText),
            nameof(HostWireFrameText));
    }

    private void EditSelectedProvider()
    {
        if (SelectedProvider is { } provider)
        {
            EditProvider(provider);
        }
        else
        {
            _notify("请先选择一条 Provider 配置", NmStatus.Blocked);
        }
    }

    private void DeleteSelectedProvider()
    {
        if (SelectedProvider is { } provider)
        {
            DeleteProvider(provider);
        }
        else
        {
            _notify("请先选择一条 Provider 配置", NmStatus.Blocked);
        }
    }

    private void EditSelectedNetwork()
    {
        if (SelectedNetwork is { } network)
        {
            EditNetwork(network);
        }
        else
        {
            _notify("请先选择一条网络配置", NmStatus.Blocked);
        }
    }

    private void SetDefaultSelectedNetwork()
    {
        if (SelectedNetwork is { } network)
        {
            SetDefaultNetwork(network);
        }
        else
        {
            _notify("请先选择一条网络配置", NmStatus.Blocked);
        }
    }

    private void TestSelectedNetwork()
    {
        if (SelectedNetwork is { } network)
        {
            TestNetwork(network);
        }
        else
        {
            _notify("请先选择一条网络配置", NmStatus.Blocked);
        }
    }

    private void DeleteSelectedNetwork()
    {
        if (SelectedNetwork is { } network)
        {
            DeleteNetwork(network);
        }
        else
        {
            _notify("请先选择一条网络配置", NmStatus.Blocked);
        }
    }
    // ── Helpers ─────────────────────────────────────────────────────────────────────────

    private static string DescribeSettingsFailure(SettingsProfileResult result) =>
        $"{StatusText(result.Status)}" + (string.IsNullOrEmpty(result.ErrorCode) ? string.Empty : $"（{result.ErrorCode}）");

    private static string StatusText(SettingsProfileStatus status) => status switch
    {
        SettingsProfileStatus.Success => "成功",
        SettingsProfileStatus.NotFound => "目标不存在",
        SettingsProfileStatus.Conflict => "冲突",
        SettingsProfileStatus.InvalidArguments => "参数无效",
        SettingsProfileStatus.TlsConfirmationRequired => "关闭 TLS 校验需要确认",
        SettingsProfileStatus.Unavailable => "能力不可用",
        SettingsProfileStatus.NotReady => "Host 未就绪",
        _ => "失败",
    };

    private static string DescribeCredentialFailure(CredentialOperationResult result) =>
        result.Status switch
        {
            CredentialOperationStatus.Conflict => "密钥状态冲突（请刷新后重试）",
            CredentialOperationStatus.NotFound => "目标配置不存在（可能已被删除）",
            CredentialOperationStatus.InvalidArguments => "参数无效",
            CredentialOperationStatus.Unavailable => "密钥存储不可用（OS vault / Core bridge）",
            CredentialOperationStatus.NotReady => "Host 未就绪",
            _ => $"失败（{result.ErrorCode ?? "CREDENTIAL_FAILED"}）",
        };

    private static (string Body, string Requirement) NotWiredCopy(ConsoleSectionId id) => id switch
    {
        ConsoleSectionId.Devices => (
            "能力待接入：设备探测当前只存在于打包元数据（VERSION.json），Host 未暴露设备/模型查询命令；按 AD-002 UI 不直读任意文件，" +
            "因此这里不显示 GPU/CPU 状态，也不提供假开关。",
            "依赖：Host 设备状态命令（需契约扩展）；在接入前请以打包 VERSION.json 与日志为准。"),
        ConsoleSectionId.Storage => (
            "能力待接入：缓存预览/清理命令（cleanup_preview / cleanup_run）已在命令注册表中，但 IHostController 未暴露方法，" +
            "无法先展示将删除的缓存量、过期 revision 与影响面，因此不执行清理。",
            "依赖：core-bridge 追加 IHostController 方法；清理前必须展示影响面并二次确认。"),
        ConsoleSectionId.Backup => (
            "能力待接入：备份列表/创建命令（backup_list / backup_create）已在注册表中，但 IHostController 未暴露方法；" +
            ".nmbak 恢复策略尚未接入，因此不提供假备份开关。",
            "依赖：core-bridge 追加 IHostController 方法；恢复必须二次确认并说明覆盖范围。"),
        ConsoleSectionId.Plugins => (
            "能力待接入：插件列表/启停命令（plugins_list / plugins_set_enabled）已在注册表中，但 IHostController 未暴露方法；" +
            "不显示无法生效的开关。",
            "依赖：core-bridge 追加 IHostController 方法；插件启用需要审计记录与权限说明。"),
        _ => (
            "该分区尚未接入真实 Host API。",
            "依赖：对应服务层方法合入后接入。"),
    };
}
