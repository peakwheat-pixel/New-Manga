using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.Services;
using NewManga.Theme;

namespace NewManga.App.Views;

/// <summary>SETTINGS-PROFILE-UI-1 shared UI helpers for the profile management cards.</summary>
internal static class ProfileUi
{
    public static TextBlock Label(string text) => Ui.Text(text, 11, "TextSecondary");

    public static TextBox Input(string name, string? watermark = null) => new()
    {
        Name = name,
        Watermark = watermark,
        FontSize = 12,
        MinHeight = 30,
    };

    public static Button Action(string label, Action onClick, bool primary = false)
    {
        var button = new Button
        {
            Content = label,
            Padding = new Thickness(12, 5),
            CornerRadius = new CornerRadius(7),
            FontSize = 12,
            Background = ThemePackService.Brush(primary ? "Accent" : "CardBg"),
            Foreground = ThemePackService.Brush(primary ? "AccentText" : "TextPrimary"),
            BorderBrush = ThemePackService.Brush("CardBorder"),
            BorderThickness = new Thickness(1),
        };
        button.Click += (_, _) => onClick();
        return button;
    }

    public static StackPanel Row(params Control[] children)
    {
        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, VerticalAlignment = VerticalAlignment.Center };
        foreach (var child in children)
        {
            row.Children.Add(child);
        }

        return row;
    }

    public static string Describe(SettingsProfileResult result)
    {
        var code = string.IsNullOrEmpty(result.ErrorCode) ? result.Status.ToString() : result.ErrorCode;
        return result.Status switch
        {
            SettingsProfileStatus.Success => result.Message ?? "已完成",
            SettingsProfileStatus.NotReady => $"Host 未就绪（{code}）：请等待 Host 启动后重试。",
            SettingsProfileStatus.NotFound => $"目标不存在（{code}）：请刷新列表后重试。",
            SettingsProfileStatus.Conflict => $"冲突（{code}）：该 profile 仍被绑定/运行引用，需先清除绑定。",
            SettingsProfileStatus.InvalidArguments => $"参数无效（{code}）：请检查表单字段与 Core 校验规则。",
            SettingsProfileStatus.TlsConfirmationRequired => $"关闭 TLS 校验需确认（{code}）：勾选「确认关闭 TLS 校验」后重试。",
            SettingsProfileStatus.Unavailable => $"服务不可用（{code}）：Host/Core 未就绪或凭据端口不可用。",
            _ => $"操作失败（{code}）。",
        };
    }

    public static Border Card(Control child) => new()
    {
        Padding = new Thickness(16),
        CornerRadius = new CornerRadius(12),
        Background = ThemePackService.Brush("CardBg"),
        BorderBrush = ThemePackService.Brush("CardBorder"),
        BorderThickness = new Thickness(1),
        Child = child,
    };
}

/// <summary>
/// SETTINGS-PROFILE-UI-1 AC1: provider profile management (list + create/update/delete form with the
/// P15 schema fields display_name/provider_id/capabilities/endpoint/model/network_profile/enabled).
/// Every call goes through the injected delegates, which production wires to
/// <c>settings_provider_profiles_*</c>; tests inject a scripted fake and assert the exact arguments.
/// </summary>
public sealed class ProviderProfileSection : UserControl
{
    private readonly Func<CancellationToken, Task<IReadOnlyList<ProviderProfileInfo>>> _list;
    private readonly Func<CancellationToken, Task<IReadOnlyList<NetworkProfileInfo>>> _listNetworks;
    private readonly Func<string?, ProviderProfileDraft, CancellationToken, Task<SettingsProfileResult>> _save;
    private readonly Func<string, CancellationToken, Task<SettingsProfileResult>> _delete;
    private readonly ListBox _profileList = new() { Name = "ProviderProfileList", MinHeight = 90, MaxHeight = 140 };
    private readonly TextBox _displayName = ProfileUi.Input("ProviderDisplayName", "显示名称");
    private readonly TextBox _providerId = ProfileUi.Input("ProviderId", "provider 类型，如 openai / deepl / manga-ocr");
    private readonly TextBox _endpoint = ProfileUi.Input("ProviderEndpoint", "Base URL，如 https://api.example.com/v1");
    private readonly TextBox _model = ProfileUi.Input("ProviderModel", "模型名，如 gpt-4o-mini");
    private readonly ComboBox _networkProfile = new() { Name = "ProviderNetworkProfile", MinWidth = 240 };
    private readonly CheckBox _enabled = new() { Name = "ProviderEnabled", Content = "启用（enabled）", IsChecked = true };
    private readonly Dictionary<string, CheckBox> _capabilityChecks = new(StringComparer.Ordinal);
    private readonly TextBlock _status;
    private readonly TextBlock _empty;
    private readonly Button _saveButton;
    private readonly Button _deleteButton;
    private readonly Button _newButton;
    private readonly Button _refreshButton;
    private IReadOnlyList<ProviderProfileInfo> _profiles = Array.Empty<ProviderProfileInfo>();
    private IReadOnlyList<NetworkProfileInfo> _networks = Array.Empty<NetworkProfileInfo>();
    private string? _editingId;

    public ProviderProfileSection(
        Func<CancellationToken, Task<IReadOnlyList<ProviderProfileInfo>>> list,
        Func<CancellationToken, Task<IReadOnlyList<NetworkProfileInfo>>> listNetworks,
        Func<string?, ProviderProfileDraft, CancellationToken, Task<SettingsProfileResult>> save,
        Func<string, CancellationToken, Task<SettingsProfileResult>> delete)
    {
        _list = list;
        _listNetworks = listNetworks;
        _save = save;
        _delete = delete;
        Name = "ProviderProfileSection";

        _status = Ui.Text(string.Empty, 11, "TextSecondary");
        _status.Name = "ProviderProfileStatus";
        _empty = Ui.Text(
            "尚无 provider profile。填写下面的表单后点「新建」，即可创建第一个 provider 目标。",
            11,
            "TextSecondary");
        _empty.Name = "ProviderProfileEmpty";
        _saveButton = ProfileUi.Action("保存", OnSave, primary: true);
        _saveButton.Name = "ProviderProfileSave";
        _deleteButton = ProfileUi.Action("删除", OnDelete);
        _deleteButton.Name = "ProviderProfileDelete";
        _newButton = ProfileUi.Action("新建", OnNew);
        _newButton.Name = "ProviderProfileNew";
        _refreshButton = ProfileUi.Action("刷新", () => LastOperation = RefreshAsync());
        _refreshButton.Name = "ProviderProfileRefresh";

        _profileList.SelectionChanged += (_, _) => OnSelectionChanged();

        var body = new StackPanel { Spacing = 8 };
        body.Children.Add(Ui.Text("Provider Profile 管理", 13, "TextPrimary", bold: true));
        body.Children.Add(Ui.Text(
            "P15 provider profile：模型提供方（OCR/翻译/上色…）的 endpoint、模型、网络 profile 与启用状态。凭证请在下方「凭据」区块配置。",
            11,
            "TextSecondary"));
        body.Children.Add(_profileList);
        body.Children.Add(_empty);
        body.Children.Add(ProfileUi.Label("显示名称（display_name）"));
        body.Children.Add(_displayName);
        body.Children.Add(ProfileUi.Label("Provider 类型（provider_id，创建后不可改）"));
        body.Children.Add(_providerId);
        body.Children.Add(ProfileUi.Label("能力（capabilities，至少选一项）"));
        var capabilities = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 10, Name = "ProviderCapabilities" };
        foreach (var capability in SettingsCapabilities.All)
        {
            var check = new CheckBox { Content = capability, Name = "Capability_" + capability };
            _capabilityChecks[capability] = check;
            capabilities.Children.Add(check);
        }

        body.Children.Add(capabilities);
        body.Children.Add(ProfileUi.Label("Endpoint（base_url）"));
        body.Children.Add(_endpoint);
        body.Children.Add(ProfileUi.Label("模型（model）"));
        body.Children.Add(_model);
        body.Children.Add(ProfileUi.Label("绑定的 network profile（可选）"));
        body.Children.Add(_networkProfile);
        body.Children.Add(_enabled);
        body.Children.Add(ProfileUi.Row(_newButton, _saveButton, _deleteButton, _refreshButton));
        body.Children.Add(_status);
        Content = body;
        UpdateButtons();
    }

    public IReadOnlyList<ProviderProfileInfo> Profiles => _profiles;

    public ListBox ProfileList => _profileList;

    public TextBox DisplayNameInput => _displayName;

    public TextBox ProviderIdInput => _providerId;

    public TextBox EndpointInput => _endpoint;

    public TextBox ModelInput => _model;

    public ComboBox NetworkProfileInput => _networkProfile;

    public CheckBox EnabledInput => _enabled;

    public IReadOnlyDictionary<string, CheckBox> CapabilityChecks => _capabilityChecks;

    public Button SaveButton => _saveButton;

    public Button DeleteButton => _deleteButton;

    public Button NewButton => _newButton;

    public Button RefreshButton => _refreshButton;

    public TextBlock StatusText => _status;

    public TextBlock EmptyText => _empty;

    public string? EditingProfileId => _editingId;

    public Task LastOperation { get; private set; } = Task.CompletedTask;

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _networks = await _listNetworks(cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            _networks = Array.Empty<NetworkProfileInfo>();
        }

        try
        {
            _profiles = await _list(cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            _profiles = Array.Empty<ProviderProfileInfo>();
        }

        var previousId = _editingId;
        _profileList.ItemsSource = _profiles.Select(profile => profile.DisplayText).ToList();
        var networkItems = new List<string> { "（无 network profile）" };
        networkItems.AddRange(_networks.Select(network => network.DisplayText));
        _networkProfile.ItemsSource = networkItems;
        _networkProfile.SelectedIndex = 0;
        _empty.IsVisible = _profiles.Count == 0;
        if (_profiles.Count == 0)
        {
            _editingId = null;
            _profileList.SelectedIndex = -1;
            UpdateButtons();
            return;
        }

        var index = 0;
        for (var candidate = 0; candidate < _profiles.Count; candidate++)
        {
            if (string.Equals(_profiles[candidate].ProfileId, previousId, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        _profileList.SelectedIndex = index;
    }

    public void StartNew()
    {
        _editingId = null;
        _profileList.SelectedIndex = -1;
        _providerId.Text = string.Empty;
        _displayName.Text = string.Empty;
        _endpoint.Text = string.Empty;
        _model.Text = string.Empty;
        _enabled.IsChecked = true;
        if (_networkProfile.ItemCount > 0)
        {
            _networkProfile.SelectedIndex = 0;
        }

        foreach (var check in _capabilityChecks.Values)
        {
            check.IsChecked = false;
        }

        UpdateButtons();
        SetStatus("新建模式：填写字段后点「保存」。");
    }

    private void OnNew() => LastOperation = Task.Run(() =>
    {
        StartNew();
        return Task.CompletedTask;
    });

    private void OnSelectionChanged()
    {
        if (_profileList.SelectedIndex < 0 || _profileList.SelectedIndex >= _profiles.Count)
        {
            return;
        }

        var profile = _profiles[_profileList.SelectedIndex];
        _editingId = profile.ProfileId;
        _displayName.Text = profile.DisplayName;
        _providerId.Text = profile.ProviderId;
        _endpoint.Text = profile.Endpoint;
        _model.Text = profile.Model;
        _enabled.IsChecked = profile.Enabled;
        foreach (var (capability, check) in _capabilityChecks)
        {
            check.IsChecked = profile.Capabilities.Contains(capability, StringComparer.Ordinal);
        }

        var networkIndex = 0;
        for (var candidate = 0; candidate < _networks.Count; candidate++)
        {
            if (string.Equals(_networks[candidate].NetworkProfileId, profile.NetworkProfileId, StringComparison.Ordinal))
            {
                networkIndex = candidate + 1;
                break;
            }
        }

        _networkProfile.SelectedIndex = networkIndex;
        UpdateButtons();
    }

    private void UpdateButtons()
    {
        _deleteButton.IsEnabled = _editingId is not null;
        _saveButton.Content = _editingId is null ? "新建并保存" : "保存修改";
    }

    private void OnSave() => LastOperation = SaveAsync();

    private async Task SaveAsync()
    {
        if (string.IsNullOrWhiteSpace(_displayName.Text) || string.IsNullOrWhiteSpace(_endpoint.Text) ||
            string.IsNullOrWhiteSpace(_model.Text))
        {
            SetStatus("参数无效（INVALID_ARGUMENTS）：display_name / endpoint / model 必填。", error: true);
            return;
        }

        var capabilities = _capabilityChecks
            .Where(pair => pair.Value.IsChecked == true)
            .Select(pair => pair.Key)
            .ToList();
        if (capabilities.Count == 0)
        {
            SetStatus("参数无效（INVALID_ARGUMENTS）：capabilities 至少选一项。", error: true);
            return;
        }

        if (_editingId is null && string.IsNullOrWhiteSpace(_providerId.Text))
        {
            SetStatus("参数无效（INVALID_ARGUMENTS）：新建时 provider_id 必填。", error: true);
            return;
        }

        var networkId = _networkProfile.SelectedIndex > 0 && _networkProfile.SelectedIndex - 1 < _networks.Count
            ? _networks[_networkProfile.SelectedIndex - 1].NetworkProfileId
            : null;
        var draft = new ProviderProfileDraft(
            _providerId.Text ?? string.Empty,
            _displayName.Text ?? string.Empty,
            capabilities,
            _endpoint.Text ?? string.Empty,
            _model.Text ?? string.Empty,
            networkId,
            _enabled.IsChecked == true);
        _saveButton.IsEnabled = false;
        try
        {
            var result = await _save(_editingId, draft, CancellationToken.None);
            SetStatus(ProfileUi.Describe(result), error: !result.IsSuccess);
            if (result.IsSuccess)
            {
                await RefreshAsync();
            }
        }
        finally
        {
            _saveButton.IsEnabled = true;
            UpdateButtons();
        }
    }

    private void OnDelete() => LastOperation = DeleteAsync();

    private async Task DeleteAsync()
    {
        if (_editingId is null)
        {
            SetStatus("请选择要删除的 profile。", error: true);
            return;
        }

        var target = _editingId;
        var result = await _delete(target, CancellationToken.None);
        SetStatus(ProfileUi.Describe(result), error: !result.IsSuccess);
        if (result.IsSuccess)
        {
            _editingId = null;
            await RefreshAsync();
        }
    }

    private void SetStatus(string message, bool error = false)
    {
        _status.Text = message;
        _status.Foreground = ThemePackService.Brush(error ? "TextPrimary" : "TextSecondary");
    }
}

/// <summary>
/// SETTINGS-PROFILE-UI-1 AC2: network profile management + the real Core network diagnostic
/// (<c>settings_network_profiles_test</c>) and resolution view (<c>settings_network_profile_resolve</c>).
/// The diagnostic text is always the Core result (never fabricated): an unavailable call renders an
/// explicit "不可用" message instead of a fake pass.
/// </summary>
public sealed class NetworkProfileSection : UserControl
{
    private readonly Func<CancellationToken, Task<IReadOnlyList<NetworkProfileInfo>>> _list;
    private readonly Func<CancellationToken, Task<IReadOnlyList<ProviderProfileInfo>>> _listProviders;
    private readonly Func<string?, NetworkProfileDraft, CancellationToken, Task<SettingsProfileResult>> _save;
    private readonly Func<string, CancellationToken, Task<SettingsProfileResult>> _delete;
    private readonly Func<string?, CancellationToken, Task<SettingsProfileResult>> _default;
    private readonly Func<string, string, CancellationToken, Task<NetworkTestInfo?>> _test;
    private readonly Func<string?, CancellationToken, Task<NetworkResolveInfo?>> _resolve;
    private readonly ListBox _profileList = new() { Name = "NetworkProfileList", MinHeight = 80, MaxHeight = 130 };
    private readonly TextBox _displayName = ProfileUi.Input("NetworkDisplayName", "显示名称");
    private readonly ComboBox _mode = new() { Name = "NetworkMode", MinWidth = 160 };
    private readonly TextBox _proxyEndpoint = ProfileUi.Input("NetworkProxyEndpoint", "代理地址，如 http://127.0.0.1:7890");
    private readonly CheckBox _verifyTls = new() { Name = "NetworkVerifyTls", Content = "校验 TLS（verify_tls）", IsChecked = true };
    private readonly CheckBox _confirmDisableTls = new() { Name = "NetworkConfirmDisableTls", Content = "确认关闭 TLS 校验", IsChecked = false };
    private readonly CheckBox _allowFallback = new() { Name = "NetworkAllowFallback", Content = "代理失败时回退直连" };
    private readonly ComboBox _providerForProbe = new() { Name = "NetworkProviderForProbe", MinWidth = 240 };
    private readonly TextBlock _status;
    private readonly TextBlock _empty;
    private readonly TextBlock _testResult;
    private readonly TextBlock _resolveResult;
    private readonly Button _saveButton;
    private readonly Button _deleteButton;
    private readonly Button _newButton;
    private readonly Button _refreshButton;
    private readonly Button _testButton;
    private readonly Button _resolveButton;
    private readonly Button _defaultButton;
    private readonly Button _clearDefaultButton;
    private IReadOnlyList<NetworkProfileInfo> _profiles = Array.Empty<NetworkProfileInfo>();
    private IReadOnlyList<ProviderProfileInfo> _providers = Array.Empty<ProviderProfileInfo>();
    private string? _editingId;

    public NetworkProfileSection(
        Func<CancellationToken, Task<IReadOnlyList<NetworkProfileInfo>>> list,
        Func<CancellationToken, Task<IReadOnlyList<ProviderProfileInfo>>> listProviders,
        Func<string?, NetworkProfileDraft, CancellationToken, Task<SettingsProfileResult>> save,
        Func<string, CancellationToken, Task<SettingsProfileResult>> delete,
        Func<string?, CancellationToken, Task<SettingsProfileResult>> defaultProfile,
        Func<string, string, CancellationToken, Task<NetworkTestInfo?>> test,
        Func<string?, CancellationToken, Task<NetworkResolveInfo?>> resolve)
    {
        _list = list;
        _listProviders = listProviders;
        _save = save;
        _delete = delete;
        _default = defaultProfile;
        _test = test;
        _resolve = resolve;
        Name = "NetworkProfileSection";

        _status = Ui.Text(string.Empty, 11, "TextSecondary");
        _status.Name = "NetworkProfileStatus";
        _empty = Ui.Text("尚无 network profile。填写表单后点「新建」；直连/系统代理也建议建一个 profile 以便切换。", 11, "TextSecondary");
        _empty.Name = "NetworkProfileEmpty";
        _testResult = Ui.Text("诊断结果：尚未执行 test。", 11, "TextSecondary");
        _testResult.Name = "NetworkTestResult";
        _resolveResult = Ui.Text("解析结果：尚未执行 resolve。", 11, "TextSecondary");
        _resolveResult.Name = "NetworkResolveResult";

        _mode.ItemsSource = NetworkModes.All.ToList();
        _mode.SelectedIndex = 0;
        _mode.SelectionChanged += (_, _) => UpdateModeFields();
        _verifyTls.IsCheckedChanged += (_, _) =>
            _confirmDisableTls.IsVisible = _verifyTls.IsChecked != true;

        _saveButton = ProfileUi.Action("保存", () => LastOperation = SaveAsync(), primary: true);
        _saveButton.Name = "NetworkProfileSave";
        _deleteButton = ProfileUi.Action("删除", () => LastOperation = DeleteAsync());
        _deleteButton.Name = "NetworkProfileDelete";
        _newButton = ProfileUi.Action("新建", () => LastOperation = Task.Run(StartNew));
        _newButton.Name = "NetworkProfileNew";
        _refreshButton = ProfileUi.Action("刷新", () => LastOperation = RefreshAsync());
        _refreshButton.Name = "NetworkProfileRefresh";
        _testButton = ProfileUi.Action("测试网络", () => LastOperation = TestAsync());
        _testButton.Name = "NetworkProfileTest";
        _resolveButton = ProfileUi.Action("解析网络", () => LastOperation = ResolveAsync());
        _resolveButton.Name = "NetworkProfileResolve";
        _defaultButton = ProfileUi.Action("设为默认", () => LastOperation = SetDefaultAsync(set: true));
        _defaultButton.Name = "NetworkProfileDefaultSet";
        _clearDefaultButton = ProfileUi.Action("清除默认", () => LastOperation = SetDefaultAsync(set: false));
        _clearDefaultButton.Name = "NetworkProfileDefaultClear";

        _profileList.SelectionChanged += (_, _) => OnSelectionChanged();

        var body = new StackPanel { Spacing = 8 };
        body.Children.Add(Ui.Text("Network Profile 管理", 13, "TextPrimary", bold: true));
        body.Children.Add(Ui.Text(
            "P15 network profile：Direct/System/HTTP/HTTPS/SOCKS5；诊断由 Core 真实执行 Proxy/DNS/TCP/TLS/HTTP/ProviderAuth 六段。",
            11,
            "TextSecondary"));
        body.Children.Add(_profileList);
        body.Children.Add(_empty);
        body.Children.Add(ProfileUi.Label("显示名称（display_name）"));
        body.Children.Add(_displayName);
        body.Children.Add(ProfileUi.Label("模式（mode）"));
        body.Children.Add(_mode);
        body.Children.Add(ProfileUi.Label("代理地址（proxy_endpoint，HTTP/HTTPS/SOCKS5 必填）"));
        body.Children.Add(_proxyEndpoint);
        body.Children.Add(_verifyTls);
        body.Children.Add(_confirmDisableTls);
        body.Children.Add(_allowFallback);
        body.Children.Add(ProfileUi.Row(_newButton, _saveButton, _deleteButton, _refreshButton));
        body.Children.Add(ProfileUi.Row(_defaultButton, _clearDefaultButton));
        body.Children.Add(_status);
        body.Children.Add(ProfileUi.Label("测试需选择 provider profile（诊断会检查 ProviderAuth 阶段）"));
        body.Children.Add(_providerForProbe);
        body.Children.Add(ProfileUi.Row(_testButton, _resolveButton));
        body.Children.Add(_testResult);
        body.Children.Add(_resolveResult);
        Content = body;
        UpdateButtons();
        UpdateModeFields();
    }

    public IReadOnlyList<NetworkProfileInfo> Profiles => _profiles;

    public IReadOnlyList<ProviderProfileInfo> Providers => _providers;

    public ListBox ProfileList => _profileList;

    public TextBox DisplayNameInput => _displayName;

    public ComboBox ModeInput => _mode;

    public TextBox ProxyEndpointInput => _proxyEndpoint;

    public CheckBox VerifyTlsInput => _verifyTls;

    public CheckBox ConfirmDisableTlsInput => _confirmDisableTls;

    public CheckBox AllowFallbackInput => _allowFallback;

    public ComboBox ProviderForProbeInput => _providerForProbe;

    public TextBlock TestResultText => _testResult;

    public TextBlock ResolveResultText => _resolveResult;

    public TextBlock StatusText => _status;

    public TextBlock EmptyText => _empty;

    public Button SaveButton => _saveButton;

    public Button DeleteButton => _deleteButton;

    public Button NewButton => _newButton;

    public Button TestButton => _testButton;

    public Button ResolveButton => _resolveButton;

    public Button DefaultSetButton => _defaultButton;

    public Button DefaultClearButton => _clearDefaultButton;

    public string? EditingNetworkProfileId => _editingId;

    public Task LastOperation { get; private set; } = Task.CompletedTask;

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _providers = await _listProviders(cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            _providers = Array.Empty<ProviderProfileInfo>();
        }

        try
        {
            _profiles = await _list(cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            _profiles = Array.Empty<NetworkProfileInfo>();
        }

        _profileList.ItemsSource = _profiles.Select(profile => profile.DisplayText).ToList();
        _providerForProbe.ItemsSource = _providers.Select(provider => provider.DisplayText).ToList();
        _providerForProbe.SelectedIndex = _providers.Count > 0 ? 0 : -1;
        _empty.IsVisible = _profiles.Count == 0;
        if (_profiles.Count == 0)
        {
            _editingId = null;
            _profileList.SelectedIndex = -1;
            UpdateButtons();
            return;
        }

        _profileList.SelectedIndex = 0;
    }

    public void StartNew()
    {
        _editingId = null;
        _profileList.SelectedIndex = -1;
        _displayName.Text = string.Empty;
        _mode.SelectedIndex = 0;
        _proxyEndpoint.Text = string.Empty;
        _verifyTls.IsChecked = true;
        _confirmDisableTls.IsChecked = false;
        _allowFallback.IsChecked = false;
        UpdateButtons();
        SetStatus("新建模式：填写字段后点「保存」。");
    }

    private void OnSelectionChanged()
    {
        if (_profileList.SelectedIndex < 0 || _profileList.SelectedIndex >= _profiles.Count)
        {
            return;
        }

        var profile = _profiles[_profileList.SelectedIndex];
        _editingId = profile.NetworkProfileId;
        _displayName.Text = profile.DisplayName;
        _mode.SelectedIndex = Math.Max(0, NetworkModes.All.ToList().IndexOf(profile.Mode));
        _proxyEndpoint.Text = profile.ProxyEndpoint ?? string.Empty;
        _verifyTls.IsChecked = profile.VerifyTls;
        _confirmDisableTls.IsChecked = !profile.VerifyTls;
        _allowFallback.IsChecked = profile.AllowProxyFailureDirectFallback;
        UpdateButtons();
        UpdateModeFields();
    }

    private void UpdateModeFields()
    {
        var mode = _mode.SelectedItem as string ?? NetworkModes.Direct;
        var requiresProxy = NetworkModes.RequiresProxyEndpoint(mode);
        _proxyEndpoint.IsEnabled = requiresProxy;
        _proxyEndpoint.Watermark = requiresProxy
            ? "代理地址，如 http://127.0.0.1:7890"
            : "Direct/System 模式必须留空";
        _confirmDisableTls.IsVisible = _verifyTls.IsChecked != true;
    }

    private void UpdateButtons()
    {
        _deleteButton.IsEnabled = _editingId is not null;
        _defaultButton.IsEnabled = _editingId is not null;
        _testButton.IsEnabled = _editingId is not null && _providers.Count > 0;
        _resolveButton.IsEnabled = true;
        _saveButton.Content = _editingId is null ? "新建并保存" : "保存修改";
    }

    private async Task SaveAsync()
    {
        if (string.IsNullOrWhiteSpace(_displayName.Text))
        {
            SetStatus("参数无效（INVALID_ARGUMENTS）：display_name 必填。", error: true);
            return;
        }

        var mode = _mode.SelectedItem as string ?? NetworkModes.Direct;
        if (NetworkModes.RequiresProxyEndpoint(mode) && string.IsNullOrWhiteSpace(_proxyEndpoint.Text))
        {
            SetStatus($"参数无效（INVALID_ARGUMENTS）：{mode} 模式必须填写 proxy_endpoint。", error: true);
            return;
        }

        var draft = new NetworkProfileDraft(
            _displayName.Text ?? string.Empty,
            mode,
            NetworkModes.RequiresProxyEndpoint(mode) ? _proxyEndpoint.Text : null,
            _verifyTls.IsChecked == true,
            _confirmDisableTls.IsChecked == true,
            _allowFallback.IsChecked == true);
        _saveButton.IsEnabled = false;
        try
        {
            var result = await _save(_editingId, draft, CancellationToken.None);
            SetStatus(ProfileUi.Describe(result), error: !result.IsSuccess);
            if (result.IsSuccess)
            {
                await RefreshAsync();
            }
        }
        finally
        {
            _saveButton.IsEnabled = true;
            UpdateButtons();
        }
    }

    private async Task DeleteAsync()
    {
        if (_editingId is null)
        {
            SetStatus("请选择要删除的 network profile。", error: true);
            return;
        }

        var result = await _delete(_editingId, CancellationToken.None);
        SetStatus(ProfileUi.Describe(result), error: !result.IsSuccess);
        if (result.IsSuccess)
        {
            _editingId = null;
            await RefreshAsync();
        }
    }

    private async Task SetDefaultAsync(bool set)
    {
        if (set && _editingId is null)
        {
            SetStatus("请选择要设为默认的 network profile。", error: true);
            return;
        }

        var result = await _default(set ? _editingId : null, CancellationToken.None);
        SetStatus(ProfileUi.Describe(result), error: !result.IsSuccess);
    }

    private async Task TestAsync()
    {
        var network = _editingId;
        var provider = SelectedProviderId();
        if (network is null || provider is null)
        {
            _testResult.Text = "诊断结果：请先选择 network profile 与 provider profile（Host 未就绪时不可用）。";
            return;
        }

        _testButton.IsEnabled = false;
        try
        {
            var info = await _test(network, provider, CancellationToken.None);
            _testResult.Text = info is null
                ? "诊断结果：不可用（Host/Core 未就绪或参数不足，未伪造结果）。"
                : "诊断结果：" + info.Summary;
        }
        finally
        {
            _testButton.IsEnabled = true;
        }
    }

    private async Task ResolveAsync()
    {
        var provider = SelectedProviderId();
        var info = await _resolve(provider, CancellationToken.None);
        _resolveResult.Text = info is null
            ? "解析结果：不可用（Host/Core 未就绪）。"
            : "解析结果：" + info.Summary;
    }

    private string? SelectedProviderId() =>
        _providerForProbe.SelectedIndex >= 0 && _providerForProbe.SelectedIndex < _providers.Count
            ? _providers[_providerForProbe.SelectedIndex].ProfileId
            : null;

    private void SetStatus(string message, bool error = false)
    {
        _status.Text = message;
        _status.Foreground = ThemePackService.Brush(error ? "TextPrimary" : "TextSecondary");
    }
}
