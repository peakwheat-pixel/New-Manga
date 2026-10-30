using System.Collections.ObjectModel;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.CoreClient;
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
    private string _hostSelfCheckText = "启动自检尚未运行";
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

    // REALUSE-DATA-SAFETY-1 AC2: real .nmbak backup packages (list/create/delete/restore).
    private BackupEntryRowViewModel? _selectedBackup;
    private bool _isBackupBusy;
    private string _backupStatusText = "尚未读取备份列表";
    private string? _backupLastResult;

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
            // REALUSE-DATA-SAFETY-4 AC1: cleanup.preview / cleanup.run are wired end to end now, so this
            // section is a real pre-flight + confirmed run instead of a permanent placeholder.
            Section(ConsoleSectionId.Storage, "05", "缓存与版本清理", "预览影响面后清理（真实，二次确认）", isWired: true),
            Section(ConsoleSectionId.Backup, "06", "备份与恢复", "真实 .nmbak 包（列表 / 创建 / 删除 / 恢复）", isWired: true),
            // REALUSE-DATA-SAFETY-4 AC1: plugins.list / plugins.set_enabled / plugins.set_plugin_enabled
            // are wired end to end now, so the section shows the real inventory and real switches.
            Section(ConsoleSectionId.Plugins, "07", "插件与 Hooks", "插件清单与启停（真实，二次确认）", isWired: true),
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
        RefreshCleanupPreviewCommand = new RelayCommand(() => _ = RefreshCleanupPreviewAsync());
        RetryPendingCleanupsCommand = new RelayCommand(RequestRetryPendingCleanups);
        RefreshPluginsCommand = new RelayCommand(() => _ = RefreshPluginsAsync());
        ToggleGlobalPluginsCommand = new RelayCommand(RequestToggleGlobalPlugins);
        GoToProvidersCommand = new RelayCommand(() => SelectSectionById(ConsoleSectionId.Providers));
        RequestCreateBackupCommand = new RelayCommand(() => _ = CreateBackupAsync());
        RequestDeleteBackupCommand = new RelayCommand(RequestDeleteBackup);
        RequestRestoreBackupCommand = new RelayCommand(RequestRestoreBackup);
        RefreshBackupsCommand = new RelayCommand(() => _ = RefreshBackupsAsync());
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
        RefreshKnownRuns();
    }

    private void OnRunMonitorUpdated(object? sender, EventArgs e)
    {
        RefreshKnownRuns();
        if (!HasRunLoaded || _runMonitor.RunId is not { } runId)
        {
            return;
        }

        ApplyRun(runId, _runMonitor.Snapshot, _runMonitor.Projection);
    }

    // ── REALUSE-DATA-SAFETY-3 AC2: this session's runs (audit MA-07) ───────────────────────

    private void RefreshKnownRuns()
    {
        var known = _runMonitor.KnownRunIds;
        if (known.Count == KnownRuns.Count && known.Select((id, index) => id == KnownRuns[index].RunId).All(same => same))
        {
            return;
        }

        KnownRuns.Clear();
        for (var index = 0; index < known.Count; index++)
        {
            KnownRuns.Add(new ConsoleKnownRunRow(known[index], index == 0, SelectKnownRun));
        }

        OnPropertyChanged(nameof(HasKnownRuns), nameof(KnownRunsHint));
    }

    /// <summary>
    /// Loads a run the session already saw, so the section is usable without copying an id out of
    /// another window. The load still goes through the normal Host read (no cached projection).
    /// </summary>
    private void SelectKnownRun(string runId)
    {
        RunIdInput = runId;
        _ = LoadRunAsync();
    }

    /// <summary>REALUSE-DATA-SAFETY-3 AC2: runs this session tracked (most recent first).</summary>
    public ObservableCollection<ConsoleKnownRunRow> KnownRuns { get; } = new();

    public bool HasKnownRuns => KnownRuns.Count > 0;

    public string KnownRunsHint => KnownRuns.Count == 0
        ? "本会话还没有出现过 Run；从工位批次开始处理，或直接输入外部 run_id。"
        : "本会话出现过的 Run（点击读取）；冻结契约没有「列出 Run」命令，跨会话的 Run 仍需输入 run_id。";

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

    // ── ⑦ 插件与 Hooks（REALUSE-DATA-SAFETY-4 AC1：真实 plugins.* 面）──────────────────

    private bool _isPluginsBusy;
    private bool _pluginsGlobalEnabled;
    private string _pluginsSummaryText = "尚未读取插件列表";
    private string? _pluginsLastResult;

    public bool IsPluginsSection => _selectedSection.Id == ConsoleSectionId.Plugins;

    public ObservableCollection<PluginRowViewModel> Plugins { get; } = new();

    public bool HasPlugins => Plugins.Count > 0;

    public bool IsPluginsBusy
    {
        get => _isPluginsBusy;
        private set => Set(ref _isPluginsBusy, value);
    }

    /// <summary>The Core's global master switch; per-plugin switches are meaningless while it is off.</summary>
    public bool PluginsGlobalEnabled
    {
        get => _pluginsGlobalEnabled;
        private set => Set(ref _pluginsGlobalEnabled, value);
    }

    public string PluginsGlobalText => PluginsGlobalEnabled ? "全局插件：已启用" : "全局插件：已停用";

    public string PluginsSummaryText
    {
        get => _pluginsSummaryText;
        private set => Set(ref _pluginsSummaryText, value);
    }

    public string? PluginsLastResult
    {
        get => _pluginsLastResult;
        private set => Set(ref _pluginsLastResult, value);
    }

    public bool HasPluginsResult => !string.IsNullOrWhiteSpace(_pluginsLastResult);

    public RelayCommand RefreshPluginsCommand { get; private set; } = null!;

    /// <summary>REALUSE-DATA-SAFETY-4 AC2: from the devices section straight to the provider section.</summary>
    public RelayCommand GoToProvidersCommand { get; private set; } = null!;

    public RelayCommand ToggleGlobalPluginsCommand { get; private set; } = null!;

    public Task RefreshPluginsAsync() =>
        IsPluginsBusy ? Task.CompletedTask : RefreshPluginsCoreAsync();

    private async Task RefreshPluginsCoreAsync()
    {
        IsPluginsBusy = true;
        try
        {
            var inventory = await _controller.ListPluginsAsync().ConfigureAwait(true);
            Plugins.Clear();
            foreach (var plugin in inventory.Plugins)
            {
                Plugins.Add(new PluginRowViewModel(
                    plugin,
                    inventory.GlobalEnabled,
                    () => RequestTogglePlugin(plugin.PluginId, plugin)));
            }

            PluginsGlobalEnabled = inventory.GlobalEnabled;
            PluginsSummaryText = inventory.Plugins.Count == 0
                ? "没有发现可加载的插件（插件目录为空或未装配 Runtime）"
                : $"发现 {inventory.Plugins.Count} 个插件";
            OnPropertyChanged(nameof(HasPlugins), nameof(PluginsGlobalText));
        }
        finally
        {
            IsPluginsBusy = false;
        }
    }

    private void RequestToggleGlobalPlugins()
    {
        var turningOn = !PluginsGlobalEnabled;
        _requestConfirm(new ConfirmRequest(
            turningOn ? "启用全局插件" : "停用全局插件",
            turningOn
                ? "启用后，已勾选的插件钩子会在处理流程中执行。插件是外部代码，请只启用你信任的来源。"
                : "停用后所有插件钩子立即不再执行（单个插件的启用状态保留）。",
            turningOn ? "启用" : "停用",
            IsDanger: true,
            OnConfirm: () => _ = SetGlobalPluginsAsync(turningOn)));
    }

    private async Task SetGlobalPluginsAsync(bool enabled)
    {
        IsPluginsBusy = true;
        try
        {
            var confirmed = await _controller.SetPluginsGlobalEnabledAsync(enabled).ConfigureAwait(true);
            if (confirmed is null)
            {
                _notify($"插件全局开关被拒绝：{_controller.Snapshot.LastError ?? "未知原因"}", NmStatus.Failed);
                return;
            }

            PluginsLastResult = confirmed.Value ? "全局插件已启用（Core 确认）" : "全局插件已停用（Core 确认）";
            _notify(PluginsLastResult, NmStatus.Done);
            await RefreshPluginsCoreAsync().ConfigureAwait(true);
        }
        finally
        {
            IsPluginsBusy = false;
        }
    }

    private void RequestTogglePlugin(string pluginId, PluginInfo plugin)
    {
        if (!PluginsGlobalEnabled)
        {
            _notify("全局插件已停用：单个插件开关不会生效，请先启用全局插件", NmStatus.Blocked);
            return;
        }

        var turningOn = !plugin.Enabled;
        _requestConfirm(new ConfirmRequest(
            turningOn ? $"启用插件「{plugin.Name}」" : $"停用插件「{plugin.Name}」",
            turningOn
                ? $"该插件声明的钩子：{string.Join(" / ", plugin.Hooks)}。启用后这些钩子会在流程中被调用。"
                : "停用后该插件的钩子不再执行，其启用状态会记录在 Core 侧。",
            turningOn ? "启用" : "停用",
            IsDanger: true,
            OnConfirm: () => _ = SetPluginAsync(pluginId, turningOn, plugin.Name)));
    }

    private async Task SetPluginAsync(string pluginId, bool enabled, string name)
    {
        IsPluginsBusy = true;
        try
        {
            var confirmed = await _controller.SetPluginEnabledAsync(pluginId, enabled).ConfigureAwait(true);
            if (confirmed is null)
            {
                _notify($"插件开关被拒绝：{_controller.Snapshot.LastError ?? "未知原因"}", NmStatus.Failed);
                return;
            }

            PluginsLastResult = confirmed.Value ? $"插件「{name}」已启用（Core 确认）" : $"插件「{name}」已停用（Core 确认）";
            _notify(PluginsLastResult, NmStatus.Done);
            await RefreshPluginsCoreAsync().ConfigureAwait(true);
        }
        finally
        {
            IsPluginsBusy = false;
        }
    }

    // ── ④ 模型与设备（REALUSE-DATA-SAFETY-4 AC2：诚实诊断，不伪造设备状态）──────────

    public bool IsDevicesSection => _selectedSection.Id == ConsoleSectionId.Devices;

    /// <summary>
    /// Whether any ENABLED provider profile declares the detection capability. This is the only
    /// device/model fact the Host can answer today; the missing half (GPU/CPU, weights on disk) needs
    /// a Core command that does not exist yet, and this section says so instead of guessing.
    /// </summary>
    public bool HasDetectionProvider =>
        ProviderProfiles.Any(profile => profile.Enabled && profile.SupportsDetection);

    /// <summary>Review r1 M4: an unloaded provider list is "unknown", never "unbound".</summary>
    private bool _providersLoaded;

    public string DetectionReadinessText => !_providersLoaded
        ? "检测能力：Provider 列表尚未读取，暂时无法判断（切换到「Provider 与凭据」会自动加载）。"
        : HasDetectionProvider
            ? "检测能力：已有启用且声明「检测」的 Provider，检测步骤可以提交。"
            : "检测能力：未绑定——提交检测会失败并返回 PROVIDER_NOT_CONFIGURED（请到「Provider 与凭据」新建或启用一个声明「检测」的 Provider）。";

    public string DeviceStatusText =>
        "设备与权重：Core 尚未暴露设备/权重状态命令，因此这里不显示 GPU/CPU 或权重就绪与否；" +
        "真实状态只能从打包 VERSION.json 与运行日志确认。";

    // ── ⑤ 缓存与版本清理（REALUSE-DATA-SAFETY-4 AC1：真实 cleanup.preview / cleanup.run）──

    private bool _isCleanupBusy;
    private string _cleanupSummaryText = "尚未读取缓存预览";
    private string _cleanupPendingText = string.Empty;
    private string? _cleanupLastResult;

    public bool IsStorageSection => _selectedSection.Id == ConsoleSectionId.Storage;

    public ObservableCollection<CleanupTargetRowViewModel> CleanupTargets { get; } = new();

    public bool HasCleanupTargets => CleanupTargets.Count > 0;

    /// <summary>Review r1 M3: pending removals survive an empty target list, so they need their own flag.</summary>
    public bool HasCleanupPending => !string.IsNullOrWhiteSpace(_cleanupPendingText);

    public bool IsCleanupBusy
    {
        get => _isCleanupBusy;
        private set => Set(ref _isCleanupBusy, value);
    }

    public string CleanupSummaryText
    {
        get => _cleanupSummaryText;
        private set => Set(ref _cleanupSummaryText, value);
    }

    /// <summary>Pending removals the Core persisted after a failed deletion (retryable, never silent).</summary>
    public string CleanupPendingText
    {
        get => _cleanupPendingText;
        private set => Set(ref _cleanupPendingText, value);
    }

    public string? CleanupLastResult
    {
        get => _cleanupLastResult;
        private set => Set(ref _cleanupLastResult, value);
    }

    public bool HasCleanupResult => !string.IsNullOrWhiteSpace(_cleanupLastResult);

    public RelayCommand RefreshCleanupPreviewCommand { get; private set; } = null!;

    /// <summary>REALUSE-DATA-SAFETY-4 AC1 (review r1 M5): retry the Core's persisted failed removals.</summary>
    public RelayCommand RetryPendingCleanupsCommand { get; private set; } = null!;

    /// <summary>Read-only pre-flight; the Confirm gate below is what actually deletes.</summary>
    public Task RefreshCleanupPreviewAsync() =>
        IsCleanupBusy ? Task.CompletedTask : RefreshCleanupPreviewCoreAsync();

    private async Task RefreshCleanupPreviewCoreAsync()
    {
        IsCleanupBusy = true;
        try
        {
            var preview = await _controller.GetCleanupPreviewAsync().ConfigureAwait(true);
            CleanupTargets.Clear();
            foreach (var target in preview.Targets)
            {
                CleanupTargets.Add(new CleanupTargetRowViewModel(target));
            }

            CleanupSummaryText = preview.Targets.Count == 0
                ? "没有可安全清理的缓存（预览为空）"
                : $"将清理 {preview.Targets.Count} 个缓存文件，共 {FormatSize(preview.TotalBytes)}";
            CleanupPendingText = preview.PendingCleanups == 0
                ? string.Empty
                : $"另有 {preview.PendingCleanups} 处上次删除失败，仍待重试（Core 已记录）";
            OnPropertyChanged(nameof(HasCleanupTargets), nameof(HasCleanupPending));
        }
        finally
        {
            IsCleanupBusy = false;
        }
    }

    private void RequestClearCache()
    {
        if (!HasCleanupTargets)
        {
            _notify("没有可清理的缓存：先读取预览", NmStatus.Blocked);
            return;
        }

        _requestConfirm(new ConfirmRequest(
            "清理缓存与过期版本",
            $"将删除 {CleanupTargets.Count} 个可重建的缓存 / 缩略图 / 过期 revision 文件。" +
            "用户原图、人工修改与已锁定版本不在清理范围内；清理后部分页面需要重新处理。",
            "清理",
            IsDanger: true,
            OnConfirm: () => _ = RunCleanupAsync()));
    }

    private async Task RunCleanupAsync()
    {
        IsCleanupBusy = true;
        try
        {
            var outcome = await _controller.RunCleanupAsync().ConfigureAwait(true);
            if (outcome is null)
            {
                _notify($"清理被拒绝：{_controller.Snapshot.LastError ?? "未知原因"}", NmStatus.Failed);
                return;
            }

            CleanupLastResult = outcome.Failed == 0
                ? $"已清理 {outcome.Removed} 个文件（跳过 {outcome.Skipped}）"
                : $"已清理 {outcome.Removed} 个，失败 {outcome.Failed} 个（失败项已记录，可重试）";
            _notify(CleanupLastResult!, outcome.Failed == 0 ? NmStatus.Done : NmStatus.Failed);
            await RefreshCleanupPreviewCoreAsync().ConfigureAwait(true);
        }
        finally
        {
            IsCleanupBusy = false;
        }
    }

    // ── ⑥ 备份与恢复（真实 .nmbak：列表 / 创建 / 删除 / 恢复） ──────────────────────────

    private void RequestRetryPendingCleanups()
    {
        if (!HasCleanupPending)
        {
            _notify("没有待重试的失败项", NmStatus.Blocked);
            return;
        }

        _requestConfirm(new ConfirmRequest(
            "重试上次删除失败的项",
            "只会重试 Core 记录的失败项（不扩大清理范围）；成功的项会从待重试列表移除，仍失败的会保留。",
            "重试",
            IsDanger: true,
            OnConfirm: () => _ = RetryPendingCleanupsAsync()));
    }

    private async Task RetryPendingCleanupsAsync()
    {
        IsCleanupBusy = true;
        try
        {
            var outcome = await _controller.RetryPendingCleanupsAsync().ConfigureAwait(true);
            if (outcome is null)
            {
                _notify($"重试被拒绝：{_controller.Snapshot.LastError ?? "未知原因"}", NmStatus.Failed);
                return;
            }

            CleanupLastResult = outcome.Failed == 0
                ? $"重试完成：{outcome.Removed} 个已删除，待重试项已清空"
                : $"重试完成：{outcome.Removed} 个已删除，仍有 {outcome.Failed} 个失败";
            _notify(CleanupLastResult, outcome.Failed == 0 ? NmStatus.Done : NmStatus.Failed);
            await RefreshCleanupPreviewCoreAsync().ConfigureAwait(true);
        }
        finally
        {
            IsCleanupBusy = false;
        }
    }

    public bool IsBackupSection => _selectedSection.Id == ConsoleSectionId.Backup;

    public ObservableCollection<BackupEntryRowViewModel> BackupEntries { get; } = new();

    public BackupEntryRowViewModel? SelectedBackup
    {
        get => _selectedBackup;
        set
        {
            if (!Set(ref _selectedBackup, value))
            {
                return;
            }

            OnPropertyChanged(nameof(HasBackupSelection));
        }
    }

    public bool HasBackupSelection => _selectedBackup is not null;

    public bool IsBackupBusy
    {
        get => _isBackupBusy;
        private set => Set(ref _isBackupBusy, value);
    }

    public string BackupStatusText
    {
        get => _backupStatusText;
        private set => Set(ref _backupStatusText, value);
    }

    /// <summary>Outcome of the last create/delete/restore, including the Core's own rollback package id.</summary>
    public string? BackupLastResult
    {
        get => _backupLastResult;
        private set
        {
            if (Set(ref _backupLastResult, value))
            {
                OnPropertyChanged(nameof(HasBackupResult));
            }
        }
    }

    public bool HasBackupResult => !string.IsNullOrWhiteSpace(_backupLastResult);

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
        if (section.Id == ConsoleSectionId.Storage)
        {
            _ = RefreshCleanupPreviewAsync();
        }
        else if (section.Id == ConsoleSectionId.Plugins)
        {
            _ = RefreshPluginsAsync();
        }

        OnPropertyChanged(
            nameof(SelectedSection),
            nameof(IsTasksSection),
            nameof(IsProvidersSection),
            nameof(IsNetworkSection),
            nameof(IsDiagnosticsSection),
            nameof(IsAppearanceSection),
            nameof(IsBackupSection),
            nameof(IsNotWiredSection),
            nameof(NotWiredTitle),
            nameof(NotWiredBody),
            nameof(NotWiredRequirement),
            nameof(ShowClearCacheDanger),
            nameof(ShowBackupDanger),
            nameof(SectionSummary));

        if (section.Id == ConsoleSectionId.Backup)
        {
            _ = RefreshBackupsAsync();
        }
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

    /// <summary>REALUSE-DATA-SAFETY-2 AC3: startup self check line (passed / degraded + reason).</summary>
    public string HostSelfCheckText => _hostSelfCheckText;

    public string HostErrorCodeText => _hostErrorCodeText;

    public string HostWireFrameText => _hostWireFrameText;

    public string AppearanceText => _isDarkTheme() ? "深色（Dark）" : "浅色（Light）";

    public RelayCommand ToggleAppearanceCommand { get; }

    public RelayCommand OpenThemeStudioCommand { get; }

    public RelayCommand OpenStudioCommand { get; }

    public RelayCommand RequestClearCacheCommand { get; }

    public RelayCommand RequestCreateBackupCommand { get; }

    public RelayCommand RequestDeleteBackupCommand { get; }

    public RelayCommand RequestRestoreBackupCommand { get; }

    public RelayCommand RefreshBackupsCommand { get; }

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


    private async Task RefreshBackupsAsync()
    {
        if (IsBackupBusy)
        {
            return;
        }

        IsBackupBusy = true;
        try
        {
            var packages = await _controller.ListBackupsAsync().ConfigureAwait(true);
            BackupEntries.Clear();
            foreach (var package in packages)
            {
                BackupEntries.Add(new BackupEntryRowViewModel(package));
            }

            BackupStatusText = packages.Count == 0
                ? "暂无备份包：Core 会在首次可写启动且书库非空时自动创建一个 automatic 包。"
                : $"共 {packages.Count} 个包；恢复前 Core 会自动创建 pre_restore 回滚点。";
            SelectedBackup = null;
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            BackupEntries.Clear();
            BackupStatusText = "备份列表读取失败：Host 不可用。";
        }
        finally
        {
            IsBackupBusy = false;
        }
    }

    /// <summary>
    /// Manual package creation. A null result is a real refusal (not ready / read-only / Core error);
    /// the typed code is already on the Host snapshot, so the UI never invents success.
    /// </summary>
    private async Task CreateBackupAsync()
    {
        if (IsBackupBusy)
        {
            return;
        }

        IsBackupBusy = true;
        try
        {
            var created = await _controller.CreateBackupAsync().ConfigureAwait(true);
            if (created is null)
            {
                BackupLastResult = "创建失败：Host 未就绪、只读或 Core 拒绝（见状态栏错误码）";
                _notify("创建备份失败", NmStatus.Failed);
                return;
            }

            BackupLastResult =
                $"已创建 {created.BackupType} 包 {ShortId(created.BackupId)}（{FormatSize(created.SizeBytes)}）";
            _notify("备份已创建", NmStatus.Done);
            IsBackupBusy = false; // RefreshBackupsAsync refuses to run while busy.
            await RefreshBackupsAsync().ConfigureAwait(true);
        }
        finally
        {
            IsBackupBusy = false;
        }
    }

    private void RequestDeleteBackup()
    {
        if (SelectedBackup is not { } target)
        {
            _notify("请先选择一个备份包", NmStatus.Blocked);
            return;
        }

        _requestConfirm(new ConfirmRequest(
            "删除备份包",
            $"将永久删除 {ShortId(target.BackupId)}（{FormatSize(target.SizeBytes)}）；删除后无法恢复，且不会影响其它包。",
            "删除备份",
            IsDanger: true,
            OnConfirm: () => _ = DeleteBackupAsync(target)));
    }

    private async Task DeleteBackupAsync(BackupEntryRowViewModel target)
    {
        var removed = await _controller.DeleteBackupAsync(target.BackupId).ConfigureAwait(true);
        if (!removed)
        {
            BackupLastResult = $"删除失败：{ShortId(target.BackupId)}（见状态栏错误码）";
            _notify("删除备份失败", NmStatus.Failed);
            return;
        }

        BackupLastResult = $"已删除 {ShortId(target.BackupId)}";
        _notify("备份已删除", NmStatus.Done);
        IsBackupBusy = false;
        await RefreshBackupsAsync().ConfigureAwait(true);
    }

    private void RequestRestoreBackup()
    {
        if (SelectedBackup is not { } target)
        {
            _notify("请先选择一个备份包", NmStatus.Blocked);
            return;
        }

        _requestConfirm(new ConfirmRequest(
            "从备份恢复（覆盖当前书库）",
            $"将用 {ShortId(target.BackupId)}（{FormatSize(target.SizeBytes)}）覆盖当前 library.db 与托管原图。"
            + " Core 会先自动创建一个 pre_restore 回滚点；恢复进行中若有 Run 在跑，Core 会拒绝（BACKUP_RESTORE_BUSY）。",
            "覆盖并恢复",
            IsDanger: true,
            OnConfirm: () => _ = RestoreBackupAsync(target)));
    }

    private async Task RestoreBackupAsync(BackupEntryRowViewModel target)
    {
        var rollback = await _controller.RestoreBackupAsync(target.BackupId).ConfigureAwait(true);
        if (rollback is null)
        {
            BackupLastResult = $"恢复失败：{ShortId(target.BackupId)}（见状态栏错误码）";
            _notify("恢复失败", NmStatus.Failed);
            return;
        }

        BackupLastResult = string.IsNullOrWhiteSpace(rollback)
            ? $"已从 {ShortId(target.BackupId)} 恢复"
            : $"已从 {ShortId(target.BackupId)} 恢复；回滚点 {ShortId(rollback)}";
        _notify("恢复完成", NmStatus.Done);
        IsBackupBusy = false;
        await RefreshBackupsAsync().ConfigureAwait(true);
    }

    private static string ShortId(string backupId) =>
        backupId.Length <= 12 ? backupId : backupId[..12] + "…";

    private static string FormatSize(long bytes)
    {
        const double MiB = 1024d * 1024d;
        return bytes >= MiB ? $"{bytes / MiB:0.0} MiB" : $"{bytes / 1024d:0.0} KiB";
    }

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

            // REALUSE-DATA-SAFETY-4 AC2: the devices section derives its only answer from this list.
            _providersLoaded = true;
            OnPropertyChanged(nameof(HasDetectionProvider), nameof(DetectionReadinessText));

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
        // REALUSE-DATA-SAFETY-2 AC3: the startup self check is rendered, not just logged.
        _hostSelfCheckText = snapshot.SelfCheckLine ?? "启动自检尚未运行";
        // Security: only the typed code is rendered; the raw error message may contain paths.
        _hostErrorCodeText = string.IsNullOrEmpty(snapshot.ErrorCode)
            ? string.IsNullOrEmpty(snapshot.LastError) ? "无" : snapshot.LastError
            : snapshot.ErrorCode;
        _hostWireFrameText = snapshot.WireFrameCount.ToString(System.Globalization.CultureInfo.InvariantCulture);
        OnPropertyChanged(
            nameof(HostStateText),
            nameof(HostStatusLine),
            nameof(HostModeLine),
            nameof(HostSelfCheckText),
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

/// <summary>
/// REALUSE-DATA-SAFETY-1 AC2: one row in the Console backup list. Every field comes from the Core's
/// own <c>backup.list</c> projection; nothing is inferred or prettified into a false success.
/// </summary>
public sealed class BackupEntryRowViewModel
{
    public BackupEntryRowViewModel(NewManga.CoreClient.BackupPackageInfo package)
    {
        BackupId = package.BackupId;
        TypeText = package.BackupType switch
        {
            "automatic" => "自动（首启）",
            "pre_migration" => "迁移前",
            "pre_restore" => "恢复前回滚点",
            "manual" => "手动",
            _ => package.BackupType,
        };
        CreatedText = string.IsNullOrWhiteSpace(package.CreatedAt) ? "—" : package.CreatedAt;
        SizeBytes = package.SizeBytes;
        SizeText = package.SizeBytes >= 1024L * 1024L
            ? $"{package.SizeBytes / (1024d * 1024d):0.0} MiB"
            : $"{package.SizeBytes / 1024d:0.0} KiB";
        Verified = package.Verified;
        VerifiedText = package.Verified ? "已验证" : "校验失败";
    }

    public string BackupId { get; }

    public string ShortId => BackupId.Length <= 12 ? BackupId : BackupId[..12] + "…";

    public string TypeText { get; }

    public string CreatedText { get; }

    public long SizeBytes { get; }

    public string SizeText { get; }

    public bool Verified { get; }

    public string VerifiedText { get; }
}

/// <summary>
/// REALUSE-DATA-SAFETY-3 AC2 (audit MA-07): one row of "runs this session has seen". The Console
/// used to require a hand-typed run_id because the frozen contract exposes no "list runs" command;
/// this list is a memory aid over ids the session actually obtained from the Host, never a
/// fabricated projection.
/// </summary>
public sealed class ConsoleKnownRunRow
{
    public ConsoleKnownRunRow(string runId, bool isMostRecent, Action<string> select)
    {
        RunId = runId;
        IsMostRecent = isMostRecent;
        SelectCommand = new RelayCommand(() => select(runId));
    }

    public string RunId { get; }

    /// <summary>Marks the entry the shared monitor is currently tracking.</summary>
    public bool IsMostRecent { get; }

    public RelayCommand SelectCommand { get; }
}

/// <summary>
/// REALUSE-DATA-SAFETY-4 AC1: one removable cache target from the Core's <c>cleanup.preview</c>.
/// Only a relative path and a size — the Core never sends an OS path and the UI never renders one.
/// </summary>
public sealed class CleanupTargetRowViewModel
{
    public CleanupTargetRowViewModel(CleanupTargetInfo target)
    {
        RelativePath = target.RelativePath;
        SizeBytes = target.SizeBytes;
    }

    public string RelativePath { get; }

    public long SizeBytes { get; }

    public string SizeText => SizeBytes >= 1024 * 1024
        ? $"{SizeBytes / (1024.0 * 1024.0):0.0} MB"
        : SizeBytes >= 1024
            ? $"{SizeBytes / 1024.0:0.0} KB"
            : $"{SizeBytes} B";
}

/// <summary>
/// REALUSE-DATA-SAFETY-4 AC1: one row of the Core's <c>plugins.list</c>. A rejected plugin keeps its
/// reason visible and is never presented as merely "off"; the switch is disabled while the Core's
/// global master switch is off, because a per-plugin toggle would not take effect.
/// </summary>
public sealed class PluginRowViewModel
{
    public PluginRowViewModel(PluginInfo plugin, bool globalEnabled, Action onToggle)
    {
        PluginId = plugin.PluginId;
        Name = string.IsNullOrWhiteSpace(plugin.Name) ? plugin.PluginId : plugin.Name;
        Version = plugin.Version;
        Description = plugin.Description;
        StatusText = plugin.Status switch
        {
            "enabled" => "已启用",
            "disabled" => "已停用",
            "rejected" => "已拒绝（无法加载）",
            _ => plugin.Status,
        };
        HooksText = plugin.Hooks.Count == 0 ? "（无钩子）" : string.Join(" / ", plugin.Hooks);
        PermissionsText = plugin.Permissions.Count == 0 ? "（无权限声明）" : string.Join(" / ", plugin.Permissions);
        IsRejected = string.Equals(plugin.Status, "rejected", StringComparison.Ordinal);
        ReasonText = plugin.Reason ?? string.Empty;
        Enabled = plugin.Enabled;
        ToggleText = plugin.Enabled ? "停用" : "启用";
        // A rejected plugin cannot be enabled; a per-plugin switch is pointless while the master is off.
        CanToggle = !IsRejected && globalEnabled;
        ToggleCommand = new RelayCommand(() => onToggle());
    }

    public string PluginId { get; }

    public string Name { get; }

    public string Version { get; }

    public string Description { get; }

    public string StatusText { get; }

    public string HooksText { get; }

    public string PermissionsText { get; }

    public bool IsRejected { get; }

    public string ReasonText { get; }

    public bool Enabled { get; }

    public bool CanToggle { get; }

    public string ToggleText { get; }

    public RelayCommand ToggleCommand { get; }
}
