using NewManga.App.Services;
using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.Console;

/// <summary>The nine Console (settings centre) sections of screen spec §5.</summary>
public enum ConsoleSectionId
{
    Tasks,
    Providers,
    Network,
    Devices,
    Storage,
    Backup,
    Plugins,
    Diagnostics,
    Appearance,
}

/// <summary>Left index row of the Console space (①…⑨). Wired flag is real: false = 能力待接入.</summary>
public sealed class ConsoleSectionItem : ObservableObject
{
    private bool _isSelected;

    public ConsoleSectionItem(
        ConsoleSectionId id,
        string index,
        string label,
        string summary,
        bool isWired,
        Action<ConsoleSectionItem> onSelect)
    {
        Id = id;
        Index = index;
        Label = label;
        Summary = summary;
        IsWired = isWired;
        SelectCommand = new RelayCommand(() => onSelect(this));
    }

    public ConsoleSectionId Id { get; }

    public string Index { get; }

    public string Label { get; }

    public string Summary { get; }

    public bool IsWired { get; }

    public NmStatus Status => IsWired ? NmStatus.Done : NmStatus.Blocked;

    public RelayCommand SelectCommand { get; }

    public bool IsSelected
    {
        get => _isSelected;
        private set => Set(ref _isSelected, value);
    }

    public void SetSelected(bool selected) => IsSelected = selected;
}

/// <summary>One provider-profile row. Non-secret fields only (Core never returns a credential secret).</summary>
public sealed class ProviderProfileRowViewModel : ObservableObject
{
    private bool _isSelected;

    public ProviderProfileRowViewModel(
        ProviderProfileInfo profile,
        Action<ProviderProfileRowViewModel> onSelect,
        Action<ProviderProfileRowViewModel> onEdit,
        Action<ProviderProfileRowViewModel> onDelete)
    {
        ProfileId = profile.ProfileId;
        ProviderId = profile.ProviderId;
        DisplayName = profile.DisplayName;
        CapabilitiesText = string.Join(" / ", profile.Capabilities);
        Endpoint = profile.Endpoint;
        Model = profile.Model;
        NetworkProfileId = profile.NetworkProfileId;
        Enabled = profile.Enabled;
        CredentialState = profile.CredentialState;
        SelectCommand = new RelayCommand(() => onSelect(this));
        EditCommand = new RelayCommand(() => onEdit(this));
        DeleteCommand = new RelayCommand(() => onDelete(this));
    }

    public string ProfileId { get; }

    public string ProviderId { get; }

    public string DisplayName { get; }

    public string CapabilitiesText { get; }

    public string Endpoint { get; }

    public string Model { get; }

    public string? NetworkProfileId { get; }

    public bool Enabled { get; }

    public string CredentialState { get; }

    public string CredentialStateText => IsCredentialConfigured ? "密钥已保存" : "密钥未保存";

    public bool IsCredentialConfigured =>
        string.Equals(CredentialState, "configured", StringComparison.Ordinal);

    public bool HasEndpoint => Endpoint.Length > 0;

    public bool HasModel => Model.Length > 0;

    public string EnabledText => Enabled ? "启用" : "停用";

    public string NetworkText => string.IsNullOrEmpty(NetworkProfileId) ? "网络：默认" : $"网络：{NetworkProfileId}";

    public RelayCommand SelectCommand { get; }

    public RelayCommand EditCommand { get; }

    public RelayCommand DeleteCommand { get; }

    public bool IsSelected
    {
        get => _isSelected;
        private set => Set(ref _isSelected, value);
    }

    public void SetSelected(bool selected) => IsSelected = selected;
}

/// <summary>One network-profile row (mode / proxy endpoint / TLS state / credential state; no secret).</summary>
public sealed class NetworkProfileRowViewModel : ObservableObject
{
    private bool _isSelected;
    private bool _isDefault;

    public NetworkProfileRowViewModel(
        NetworkProfileInfo profile,
        Action<NetworkProfileRowViewModel> onSelect,
        Action<NetworkProfileRowViewModel> onEdit,
        Action<NetworkProfileRowViewModel> onSetDefault,
        Action<NetworkProfileRowViewModel> onTest,
        Action<NetworkProfileRowViewModel> onDelete)
    {
        NetworkProfileId = profile.NetworkProfileId;
        DisplayName = profile.DisplayName;
        Mode = profile.Mode;
        ProxyEndpoint = profile.ProxyEndpoint ?? string.Empty;
        VerifyTls = profile.VerifyTls;
        CredentialState = profile.CredentialState;
        AllowDirectFallback = profile.AllowProxyFailureDirectFallback;
        SelectCommand = new RelayCommand(() => onSelect(this));
        EditCommand = new RelayCommand(() => onEdit(this));
        SetDefaultCommand = new RelayCommand(() => onSetDefault(this));
        TestCommand = new RelayCommand(() => onTest(this));
        DeleteCommand = new RelayCommand(() => onDelete(this));
    }

    public string NetworkProfileId { get; }

    public string DisplayName { get; }

    public string Mode { get; }

    public string ProxyEndpoint { get; }

    public bool VerifyTls { get; }

    public string CredentialState { get; }

    public bool AllowDirectFallback { get; }

    public bool HasProxyEndpoint => ProxyEndpoint.Length > 0;

    public string EndpointText => HasProxyEndpoint ? ProxyEndpoint : "无代理端点";

    public string TlsText => VerifyTls ? "TLS 校验开" : "TLS 校验关";

    public string FallbackText => AllowDirectFallback ? "代理失败可直连回退" : "代理失败不回退";

    public string CredentialStateText => string.Equals(CredentialState, "configured", StringComparison.Ordinal)
        ? "代理密码已保存"
        : "代理密码未保存";

    public string DefaultText => _isDefault ? "默认" : string.Empty;

    public RelayCommand SelectCommand { get; }

    public RelayCommand EditCommand { get; }

    public RelayCommand SetDefaultCommand { get; }

    public RelayCommand TestCommand { get; }

    public RelayCommand DeleteCommand { get; }

    public bool IsSelected
    {
        get => _isSelected;
        private set => Set(ref _isSelected, value);
    }

    public bool IsDefault
    {
        get => _isDefault;
        internal set
        {
            if (Set(ref _isDefault, value))
            {
                OnPropertyChanged(nameof(DefaultText));
            }
        }
    }

    public void SetSelected(bool selected) => IsSelected = selected;
}

/// <summary>
/// One credential target row. SECURITY: only the Core-reported state is displayed; the secret is a
/// transient password-box value that is cleared right after a successful put and never rendered,
/// logged, recorded in evidence, or included in any error message.
/// </summary>
public sealed class CredentialTargetRowViewModel : ObservableObject
{
    private string _secretInput = string.Empty;
    private string _rowStatusText = string.Empty;
    private bool _isBusy;
    private string _credentialState;

    public CredentialTargetRowViewModel(
        CredentialTargetOption target,
        Action<CredentialTargetRowViewModel> onPut,
        Action<CredentialTargetRowViewModel> onClear)
    {
        Kind = target.Kind;
        OwnerId = target.OwnerId;
        DisplayName = target.DisplayName;
        _credentialState = target.CredentialState;
        PutCommand = new RelayCommand(() => onPut(this));
        ClearCommand = new RelayCommand(() => onClear(this));
    }

    public string Kind { get; }

    public string OwnerId { get; }

    public string DisplayName { get; }

    public string KindLabel => Kind == CredentialKinds.ProviderApi ? "Provider API Key" : "代理密码";

    public string TargetText => $"{KindLabel} · {DisplayName}";

    public string CredentialState => _credentialState;

    public bool IsConfigured => string.Equals(_credentialState, "configured", StringComparison.Ordinal);

    /// <summary>已保存 / 未保存 — the only state the UI may render for a credential.</summary>
    public string StateLabel => IsConfigured ? "已保存" : "未保存";

    public NmStatus StateStatus => IsConfigured ? NmStatus.Done : NmStatus.NotStarted;

    /// <summary>Transient password-box content. Cleared after a successful put; never displayed elsewhere.</summary>
    public string SecretInput
    {
        get => _secretInput;
        set
        {
            if (Set(ref _secretInput, value))
            {
                OnPropertyChanged(nameof(HasSecretInput), nameof(CanPut));
            }
        }
    }

    public bool HasSecretInput => _secretInput.Length > 0;

    public bool CanPut => HasSecretInput && !IsBusy;

    public bool IsBusy
    {
        get => _isBusy;
        set
        {
            if (Set(ref _isBusy, value))
            {
                OnPropertyChanged(nameof(CanPut));
            }
        }
    }

    public string RowStatusText
    {
        get => _rowStatusText;
        internal set => Set(ref _rowStatusText, value);
    }

    public RelayCommand PutCommand { get; }

    public RelayCommand ClearCommand { get; }

    /// <summary>Updates the Core-reported state after a refresh (never carries a secret).</summary>
    public void UpdateState(string credentialState)
    {
        _credentialState = credentialState;
        OnPropertyChanged(nameof(CredentialState), nameof(IsConfigured), nameof(StateLabel), nameof(StateStatus));
    }

    public void ClearSecretInput()
    {
        SecretInput = string.Empty;
        OnPropertyChanged(nameof(HasSecretInput), nameof(CanPut));
    }
}

/// <summary>One capability → provider binding slot row (real resolve/set/clear IPC).</summary>
public sealed class CapabilityBindingRowViewModel : ObservableObject
{
    public CapabilityBindingRowViewModel(
        string capability,
        Action<CapabilityBindingRowViewModel> onBind,
        Action<CapabilityBindingRowViewModel> onClear)
    {
        Capability = capability;
        BindCommand = new RelayCommand(() => onBind(this));
        ClearCommand = new RelayCommand(() => onClear(this));
    }

    public string Capability { get; }

    public string Title => Capability switch
    {
        SettingsCapabilities.Ocr => "OCR 识别",
        SettingsCapabilities.Translation => "翻译",
        SettingsCapabilities.Inpaint => "修复",
        SettingsCapabilities.Detection => "检测",
        SettingsCapabilities.Rendering => "渲染",
        _ => Capability,
    };

    public string BindingText { get; private set; } = "未绑定";

    public NmStatus BindingStatus { get; private set; } = NmStatus.NotStarted;

    public string BindingSourceText { get; private set; } = string.Empty;

    public RelayCommand BindCommand { get; }

    public RelayCommand ClearCommand { get; }

    public void Update(bool isBound, string? profileId, string? source)
    {
        BindingText = isBound ? $"已绑定 → {profileId}" : "未绑定";
        BindingStatus = isBound ? NmStatus.Done : NmStatus.NotStarted;
        BindingSourceText = string.IsNullOrEmpty(source) ? string.Empty : $"来源：{source}";
        OnPropertyChanged(nameof(BindingText), nameof(BindingStatus), nameof(BindingSourceText));
    }
}

/// <summary>Provider-binding scope option (global / current book / current chapter).</summary>
public sealed record BindingScopeOption(string Kind, string Label, bool IsAvailable)
{
    public ProfileBindingScope ToScope() => new(Kind);
}

/// <summary>Sort/network mode option for the ComboBoxes.</summary>
public sealed record ConsoleOption(string Key, string Label);

/// <summary>One export-history row in the diagnostics section (real GetExportHistoryAsync).</summary>
public sealed class ExportHistoryRowViewModel : ObservableObject
{
    private string _revealText = string.Empty;
    private bool _isRevealing;

    public ExportHistoryRowViewModel(
        ExportHistoryEntry entry,
        Action<ExportHistoryRowViewModel> onReveal)
    {
        ExportId = entry.ExportId;
        Format = entry.Format;
        StatusText = Formatting(entry.Status);
        PageCount = entry.PageCount;
        CompletedAt = entry.CompletedAt ?? "—";
        RevealCommand = new RelayCommand(() => onReveal(this));
    }

    public string ExportId { get; }

    public string Format { get; }

    public string FormatText => Format switch
    {
        "zip" => "ZIP",
        "pdf" => "PDF",
        null or "" => "未知格式",
        _ => Format.ToUpperInvariant(),
    };

    public string StatusText { get; }

    public int PageCount { get; }

    public string CompletedAt { get; }

    public string MetaText => $"{FormatText} · {PageCount} 页 · {CompletedAt}";

    public string RevealText
    {
        get => _revealText;
        internal set => Set(ref _revealText, value);
    }

    public bool IsRevealing
    {
        get => _isRevealing;
        internal set => Set(ref _isRevealing, value);
    }

    public RelayCommand RevealCommand { get; }

    private static string Formatting(string status) => status switch
    {
        "completed" => "已完成",
        "failed" => "失败",
        "cancelled" => "已取消",
        "skipped" => "已跳过",
        "running" => "进行中",
        "pending" => "等待中",
        "publishing" => "写入中",
        _ => status,
    };
}
