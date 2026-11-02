using System.Collections.ObjectModel;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.ViewModels.Fluent;

public enum SettingsGroupId
{
    Appearance,
    Providers,
    Network,
    Backup,
    About,
}

public sealed class SettingsViewModel : FluentViewModel
{
    private readonly IHostController? _host;
    private readonly AppearanceCoordinator? _appearance;
    private readonly DesignSystemThemeManager? _themeManager;
    private AppearanceSettings _draft;
    /// <summary>R-017: the canonical settings the draft was last synchronized from (frontend-switch detection).</summary>
    private AppearanceSettings _observedSettings;
    private SettingsGroupId _selectedGroup;
    private string _search = string.Empty;
    private string _notice = string.Empty;
    private bool _isSaving;
    private ProviderProfileInfo? _selectedProvider;
    private NetworkProfileInfo? _selectedNetwork;
    private BackupPackageInfo? _selectedBackup;

    public SettingsViewModel(IHostController? host, AppearanceCoordinator? appearance, DesignSystemThemeManager? themeManager)
    {
        _host = host;
        _appearance = appearance;
        _themeManager = themeManager;
        _draft = appearance?.Settings ?? AppearanceDefaults.Settings;
        _observedSettings = _draft;
        State = host is null ? FluentPageState.Error : FluentPageState.Ready;
        Status = "设置已加载。";
        if (_appearance is not null)
        {
            _appearance.Changed += OnAppearanceChanged;
        }
    }

    public ObservableCollection<ProviderProfileInfo> Providers { get; } = new();
    public ObservableCollection<NetworkProfileInfo> Networks { get; } = new();
    public ObservableCollection<BackupPackageInfo> Backups { get; } = new();
    public IReadOnlyList<CredentialTargetOption> CredentialTargets { get; private set; } = Array.Empty<CredentialTargetOption>();
    public AppearanceSettings Draft { get => _draft; private set => Set(ref _draft, value); }
    public AppearanceCoordinator? AppearanceCoordinator => _appearance;
    public SettingsGroupId SelectedGroup { get => _selectedGroup; set => Set(ref _selectedGroup, value); }
    public string Search { get => _search; set { if (Set(ref _search, value ?? string.Empty)) Changed(nameof(VisibleGroups)); } }
    public string Notice { get => _notice; private set => Set(ref _notice, value); }
    public bool IsSaving { get => _isSaving; private set => Set(ref _isSaving, value); }
    public bool IsDirty => !Equals(Draft, _appearance?.Settings ?? AppearanceDefaults.Settings);
    public bool IsReadOnly => _host is null || !_host.Snapshot.WritesAllowed || _host.Snapshot.State != HostViewState.Ready;
    public bool FluentMaterialAvailable => Draft.FrontendId == "builtin.fluent" && Draft.VisualThemeId == "builtin.fluent-dark";
    public bool IsFluentTheme => Draft.VisualThemeId == "builtin.fluent-dark";
    public ProviderProfileInfo? SelectedProvider { get => _selectedProvider; set => Set(ref _selectedProvider, value); }
    public NetworkProfileInfo? SelectedNetwork { get => _selectedNetwork; set => Set(ref _selectedNetwork, value); }
    public BackupPackageInfo? SelectedBackup { get => _selectedBackup; set => Set(ref _selectedBackup, value); }
    public IReadOnlyList<SettingsGroupId> VisibleGroups => Enum.GetValues<SettingsGroupId>()
        .Where(group => string.IsNullOrWhiteSpace(Search) || GroupLabel(group).Contains(Search, StringComparison.CurrentCultureIgnoreCase) ||
            SearchFields(group).Any(fieldName => fieldName.Contains(Search, StringComparison.CurrentCultureIgnoreCase)))
        .ToArray();
    public string Version => typeof(SettingsViewModel).Assembly.GetName().Version?.ToString() ?? "未知";
    public string License => "GPL-3.0（组件许可详见随包声明）";

    public static string GroupLabel(SettingsGroupId group) => group switch
    {
        SettingsGroupId.Appearance => "外观",
        SettingsGroupId.Providers => "Provider 与凭据",
        SettingsGroupId.Network => "网络",
        SettingsGroupId.Backup => "备份与恢复",
        SettingsGroupId.About => "关于",
        _ => group.ToString(),
    };

    private static IReadOnlyList<string> SearchFields(SettingsGroupId group) => group switch
    {
        SettingsGroupId.Appearance => ["theme.visualThemeId", "theme.frontendId", "appearance.mode", "appearance.contrast",
            "appearance.followSystemAccent", "motion.mode", "motion.categories.navigation", "motion.categories.feedback",
            "motion.categories.decorative", "corners.scale", "material.acrylicStrength", "material.micaEnabled",
            "layout.id", "layout.navigation", "layout.shelf", "layout.density", "layout.workbench", "layout.reader", "schemaVersion"],
        SettingsGroupId.Providers => ["providerId", "displayName", "endpoint", "model", "capabilities", "credential"],
        SettingsGroupId.Network => ["mode", "proxyEndpoint", "verifyTls", "allowProxyFailureDirectFallback"],
        SettingsGroupId.Backup => ["backup", "restore", "frequency", "directory"],
        SettingsGroupId.About => ["version", "license", "open source"],
        _ => Array.Empty<string>(),
    };

    public async Task LoadAsync(CancellationToken cancellationToken = default)
    {
        State = FluentPageState.Loading;
        Status = "正在读取设置…";
        try
        {
            if (_appearance is not null)
            {
                Draft = _appearance.Settings;
                _observedSettings = Draft;
            }

            if (_host is not null)
            {
                Providers.Clear();
                foreach (var item in await _host.ListProviderProfilesAsync(cancellationToken)) Providers.Add(item);
                Networks.Clear();
                foreach (var item in await _host.ListNetworkProfilesAsync(cancellationToken)) Networks.Add(item);
                Backups.Clear();
                foreach (var item in await _host.ListBackupsAsync(cancellationToken)) Backups.Add(item);
                CredentialTargets = await _host.ListCredentialTargetsAsync(cancellationToken);
                Changed(nameof(CredentialTargets));
            }

            State = IsReadOnly ? FluentPageState.ReadOnly : FluentPageState.Ready;
            Status = IsReadOnly ? _host?.Snapshot.ReadOnlyReason ?? "设置只读" : "设置已加载。";
        }
        catch (Exception ex)
        {
            State = FluentPageState.Error;
            Error = $"设置读取失败（{ex.GetType().Name}），可以重试。";
        }
    }

    public void UpdateDraft(AppearanceSettings settings)
    {
        Draft = settings;
        State = IsReadOnly ? FluentPageState.ReadOnly : FluentPageState.Ready;
        Changed(nameof(IsDirty));
    }

    public async Task<bool> SaveAppearanceAsync(CancellationToken cancellationToken = default)
    {
        if (_appearance is null)
        {
            Error = "AppearanceCoordinator 未注入。";
            State = FluentPageState.Error;
            return false;
        }

        if (IsReadOnly)
        {
            Error = "当前 Host 只读，设置保存已禁用。";
            State = FluentPageState.ReadOnly;
            return false;
        }

        if (!ValidateAppearance(out var reason))
        {
            Error = reason;
            State = FluentPageState.Error;
            return false;
        }

        IsSaving = true;
        try
        {
            await _appearance.SaveAsync(Draft, cancellationToken);
            ApplyToThemeManager(Draft);
            Notice = "外观设置已保存。";
            Status = Notice;
            Error = string.Empty;
            State = FluentPageState.Ready;
            Changed(nameof(IsDirty));
            return true;
        }
        catch (Exception ex)
        {
            Error = $"外观保存失败（{ex.GetType().Name}），输入仍保留；请重试。";
            Notice = Error;
            State = FluentPageState.Error;
            return false;
        }
        finally
        {
            IsSaving = false;
        }
    }

    public void ResetAppearance()
    {
        Draft = AppearanceDefaults.Settings with { FrontendId = Draft.FrontendId };
        Notice = "外观组已恢复为默认值；点击保存后生效。";
        Changed(nameof(IsDirty));
    }

    public async Task<bool> ToggleProviderAsync(ProviderProfileInfo profile, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var draft = new ProviderProfileDraft(profile.ProviderId, profile.DisplayName, profile.Capabilities,
            profile.Endpoint, profile.Model, profile.NetworkProfileId, !profile.Enabled);
        var result = await _host.SaveProviderProfileAsync(profile.ProfileId, draft, cancellationToken);
        Notice = result.IsSuccess ? "Provider 状态已更新。" : $"Provider 更新失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await LoadProfilesAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> SaveProviderAsync(string? profileId, ProviderProfileDraft draft, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.SaveProviderProfileAsync(profileId, draft, cancellationToken);
        Notice = result.IsSuccess ? "Provider Profile 已保存。" : $"Provider 保存失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> DeleteProviderAsync(ProviderProfileInfo profile, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.DeleteProviderProfileAsync(profile.ProfileId, cancellationToken);
        Notice = result.IsSuccess ? "Provider Profile 已删除。" : $"Provider 删除失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> SaveNetworkAsync(string? profileId, NetworkProfileDraft draft, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.SaveNetworkProfileAsync(profileId, draft, cancellationToken);
        Notice = result.IsSuccess ? "网络 Profile 已保存。" : $"网络设置失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> DeleteNetworkAsync(NetworkProfileInfo profile, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.DeleteNetworkProfileAsync(profile.NetworkProfileId, cancellationToken);
        Notice = result.IsSuccess ? "网络 Profile 已删除。" : $"网络 Profile 删除失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<NetworkTestInfo?> TestNetworkAsync(NetworkProfileInfo network, ProviderProfileInfo provider,
        CancellationToken cancellationToken = default)
    {
        if (_host is null) return null;
        var result = await _host.TestNetworkProfileAsync(network.NetworkProfileId, provider.ProfileId, cancellationToken);
        Notice = result?.Summary ?? "网络诊断不可用。";
        return result;
    }

    public async Task<bool> SetNetworkDefaultAsync(NetworkProfileInfo network, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.SetNetworkDefaultAsync(network.NetworkProfileId, cancellationToken);
        Notice = result.IsSuccess ? "默认网络 Profile 已更新。" : $"更新失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        return result.IsSuccess;
    }

    public async Task<bool> CreateBackupAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var backup = await _host.CreateBackupAsync("manual", cancellationToken);
        if (backup is null)
        {
            Notice = $"备份未创建（{_host.Snapshot.LastError ?? "HOST_NOT_READY"}）。";
            return false;
        }

        Backups.Insert(0, backup);
        SelectedBackup = backup;
        Notice = backup.Verified ? "备份已创建并校验。" : "备份已创建，Core 尚未确认校验。";
        return true;
    }

    public async Task<bool> DeleteBackupAsync(BackupPackageInfo backup, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var deleted = await _host.DeleteBackupAsync(backup.BackupId, cancellationToken);
        Notice = deleted ? "备份包已删除。" : $"删除未完成（{_host.Snapshot.LastError ?? "未确认"}）。";
        if (deleted)
        {
            Backups.Remove(backup);
            SelectedBackup = null;
        }

        return deleted;
    }

    public async Task<string?> RestoreBackupAsync(BackupPackageInfo backup, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || !backup.Verified) return null;
        var rollbackBackupId = await _host.RestoreBackupAsync(backup.BackupId, cancellationToken);
        Notice = rollbackBackupId is null
            ? $"恢复未完成（{_host.Snapshot.LastError ?? "Core 未确认"}）。"
            : $"恢复已完成；恢复前回滚包：{rollbackBackupId}";
        return rollbackBackupId;
    }

    public async Task<CredentialOperationResult?> SaveCredentialAsync(
        CredentialTargetOption target, string secret, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || string.IsNullOrEmpty(secret)) return null;
        var intent = target.CredentialState == "configured" ? "replace" : "create";
        var result = await _host.PutCredentialAsync(target.Kind, target.OwnerId, intent, secret, cancellationToken);
        Notice = result.IsSuccess ? "凭据引用已更新；明文不会回显。" : $"凭据保存失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        CredentialTargets = await _host.ListCredentialTargetsAsync(cancellationToken);
        Changed(nameof(CredentialTargets));
        return result;
    }

    private async Task LoadProfilesAsync(CancellationToken cancellationToken)
    {
        if (_host is null) return;
        Providers.Clear();
        foreach (var item in await _host.ListProviderProfilesAsync(cancellationToken)) Providers.Add(item);
    }

    private async Task ReloadProfileListsAsync(CancellationToken cancellationToken)
    {
        if (_host is null) return;
        Providers.Clear();
        foreach (var item in await _host.ListProviderProfilesAsync(cancellationToken)) Providers.Add(item);
        Networks.Clear();
        foreach (var item in await _host.ListNetworkProfilesAsync(cancellationToken)) Networks.Add(item);
    }

    private bool ValidateAppearance(out string reason)
    {
        if (Draft.MaterialAcrylicStrength is < 0 or > 1)
        {
            reason = "Acrylic strength 必须在 0 到 1 之间。";
            return false;
        }

        if (Draft.FrontendId is not ("builtin.current-v2" or "builtin.fluent") ||
            Draft.VisualThemeId is not ("newmanga-default" or "builtin.fluent-dark"))
        {
            reason = "frontendId 或 visualThemeId 不在 C-02 冻结值域内。";
            return false;
        }

        reason = string.Empty;
        return true;
    }

    private void ApplyToThemeManager(AppearanceSettings settings)
    {
        if (_themeManager is null) return;
        var mode = settings.Mode switch
        {
            NewManga.Appearance.AppearanceMode.Light => NewManga.DesignSystem.Theming.AppearanceMode.Light,
            NewManga.Appearance.AppearanceMode.Dark => NewManga.DesignSystem.Theming.AppearanceMode.Dark,
            _ => NewManga.DesignSystem.Theming.AppearanceMode.System,
        };
        _themeManager.SetAppearance(mode);
        _themeManager.SetContrast(settings.Contrast == AppearanceContrast.High
            ? ContrastMode.High
            : ContrastMode.Standard);
        var motion = new MotionResolver(new WindowsMotionPreferenceSource()).Resolve(settings).Settings;
        _themeManager.SetReducedMotion(!motion.Enabled);
        _themeManager.SetDensity(settings.Layout.Density == "compact" ? DensityMode.Compact : DensityMode.Spacious);
    }

    private void OnAppearanceChanged(object? sender, EventArgs args)
    {
        if (_appearance is null) return;
        if (Dispatcher.UIThread.CheckAccess())
        {
            ApplyCoordinatorSettings();
        }
        else
        {
            // FEA-07: the coordinator may raise Changed from a pool thread after an async save; the
            // settings surface mutates controls and must always observe it on the UI thread.
            Dispatcher.UIThread.Post(ApplyCoordinatorSettings);
        }
    }

    private void ApplyCoordinatorSettings()
    {
        if (_appearance is null) return;
        var settings = _appearance.Settings;
        var previous = _observedSettings;
        if (Equals(previous, settings))
        {
            return; // no canonical change; never clobber an unapplied draft on a duplicate notification.
        }

        _observedSettings = settings;

        // FEA-07 R-017/A01: a runtime frontend switch persists only theme.frontendId. Such a
        // frontend-only canonical change must not silently discard the user's unapplied appearance draft
        // (the hidden Fluent tree keeps its state across the switch); adopt the new frontend id into the
        // draft and keep the rest. Any other external appearance change mirrors the single writer.
        Draft = Equals(previous with { FrontendId = settings.FrontendId }, settings)
            ? Draft with { FrontendId = settings.FrontendId }
            : settings;
        Changed(nameof(IsDirty));
    }
}
