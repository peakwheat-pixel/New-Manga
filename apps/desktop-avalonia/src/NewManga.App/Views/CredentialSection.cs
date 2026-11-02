using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Views.Legacy;

namespace NewManga.App.Views;

/// <summary>
/// CREDENTIAL-UI-1: the settings-page credential block.
///
/// Structure (AC1/AC2): target selector (provider API / proxy targets, each row shows the Core
/// <c>credential_state</c> configured|missing) + <see cref="SecretTextBox"/> masked input + save /
/// clear / refresh actions + typed status line + a replace-confirmation row for
/// <c>CREDENTIAL_CONFLICT</c>.
///
/// Safety (AC3): the secret only lives in the masked <see cref="SecretTextBox"/> until submit; it is
/// cleared immediately after the call, on target switch and through <see cref="ClearSecrets"/> (window
/// close). It is never written to the status line, logs, evidence or automation metadata. Replacing an
/// existing credential always requires the explicit second confirmation button.
/// </summary>
public sealed class CredentialSection : UserControl
{
    private readonly Func<CancellationToken, Task<IReadOnlyList<CredentialTargetOption>>> _listTargets;
    private readonly Func<string, string, string, string, CancellationToken, Task<CredentialOperationResult>> _put;
    private readonly Func<string, string, CancellationToken, Task<CredentialOperationResult>> _clear;
    private readonly ComboBox _targets = new()
    {
        Name = "CredentialTarget",
        HorizontalAlignment = HorizontalAlignment.Stretch,
        MinWidth = 280,
    };

    private readonly SecretTextBox _secret = new();
    private readonly TextBlock _targetState;
    private readonly TextBlock _status;
    private readonly StackPanel _confirm = new() { Spacing = 6, IsVisible = false };
    private readonly Button _save;
    private readonly Button _clearButton;
    private readonly Button _refreshButton;
    private readonly Button _replaceButton;
    private readonly Button _cancelButton;
    private IReadOnlyList<CredentialTargetOption> _options = Array.Empty<CredentialTargetOption>();
    private string? _pendingSecret;
    private CredentialTargetOption? _pendingTarget;

    public CredentialSection(
        Func<CancellationToken, Task<IReadOnlyList<CredentialTargetOption>>> listTargets,
        Func<string, string, string, string, CancellationToken, Task<CredentialOperationResult>> put,
        Func<string, string, CancellationToken, Task<CredentialOperationResult>> clear)
    {
        _listTargets = listTargets;
        _put = put;
        _clear = clear;
        Name = "CredentialSection";

        _targetState = Ui.Text("目标状态：未加载", 11, "TextSecondary");
        _status = Ui.Text(string.Empty, 11, "TextSecondary");
        _status.Name = "CredentialStatus";
        _save = ActionButton("保存凭据", primary: true);
        _save.Name = "CredentialSaveButton";
        _save.Click += (_, _) => LastOperation = SaveAsync();
        _clearButton = ActionButton("清除凭据");
        _clearButton.Name = "CredentialClearButton";
        _clearButton.Click += (_, _) => LastOperation = ClearAsync();
        _refreshButton = ActionButton("刷新状态");
        _refreshButton.Name = "CredentialRefreshButton";
        _refreshButton.Click += (_, _) => LastOperation = RefreshAsync();
        _replaceButton = ActionButton("确认替换", primary: true);
        _replaceButton.Name = "CredentialReplaceButton";
        _replaceButton.Click += (_, _) => LastOperation = ConfirmReplaceAsync();
        _cancelButton = ActionButton("取消");
        _cancelButton.Name = "CredentialCancelButton";
        _cancelButton.Click += (_, _) =>
        {
            ClearPending();
            SetStatus("已取消替换；掩码输入已清空。");
        };

        _targets.SelectionChanged += (_, _) =>
        {
            // Switching target must never carry the previous secret over.
            _secret.Text = string.Empty;
            ClearPending();
            UpdateTargetState();
        };

        var body = new StackPanel { Spacing = 8 };
        body.Children.Add(Ui.Text("凭据 · Credential", 13, "TextPrimary", bold: true));
        body.Children.Add(Ui.Text(
            "选择 provider / proxy 目标后输入 API Key 或代理密码；输入内容始终以掩码显示，保存后立即清空。",
            11,
            "TextSecondary"));
        body.Children.Add(Ui.Text("目标", 11, "TextSecondary"));
        body.Children.Add(_targets);
        body.Children.Add(_targetState);
        body.Children.Add(Ui.Text("凭据内容（掩码，不可复制明文）", 11, "TextSecondary"));
        body.Children.Add(_secret);
        var actions = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        actions.Children.Add(_save);
        actions.Children.Add(_clearButton);
        actions.Children.Add(_refreshButton);
        body.Children.Add(actions);
        body.Children.Add(_status);
        body.Children.Add(_confirm);
        Content = body;

        AddHandler(KeyDownEvent, OnPreviewKeyDown, RoutingStrategies.Tunnel, handledEventsToo: true);
        UpdateTargetState();
    }

    /// <summary>Scripted/test-facing view of the loaded targets (never includes a secret).</summary>
    public IReadOnlyList<CredentialTargetOption> Targets => _options;

    public SecretTextBox SecretInput => _secret;

    public ComboBox TargetSelector => _targets;

    public Button SaveButton => _save;

    public Button ClearButton => _clearButton;

    public Button RefreshButton => _refreshButton;

    public Button ReplaceButton => _replaceButton;

    public Button CancelButton => _cancelButton;

    public TextBlock StatusText => _status;

    public TextBlock TargetStateText => _targetState;

    public StackPanel ConfirmPanel => _confirm;

    /// <summary>Last async UI operation (tests/evidence await this instead of polling).</summary>
    public Task LastOperation { get; private set; } = Task.CompletedTask;

    /// <summary>True while a replace confirmation holds the secret in memory (never rendered).</summary>
    public bool HasPendingSecret => _pendingSecret is not null;

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _options = await _listTargets(cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or OperationCanceledException or IOException)
        {
            _options = Array.Empty<CredentialTargetOption>();
        }

        var previousOwner = Selected?.OwnerId;
        _targets.ItemsSource = _options.Select(option => option.DisplayText).ToList();
        var index = 0;
        for (var candidate = 0; candidate < _options.Count; candidate++)
        {
            if (string.Equals(_options[candidate].OwnerId, previousOwner, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        _targets.SelectedIndex = _options.Count == 0 ? -1 : index;
        UpdateTargetState();
        if (_options.Count == 0)
        {
            SetStatus("未发现可配置的 provider / proxy 目标；请先在设置中创建 profile。");
        }
    }

    /// <summary>AC3: drop every plaintext reference the block may hold (window close / navigation).</summary>
    public void ClearSecrets()
    {
        _secret.Text = string.Empty;
        _pendingSecret = null;
        _pendingTarget = null;
        HideConfirm();
    }

    /// <summary>AC1/AC3: Ctrl+C / Ctrl+X / Ctrl+Insert must not copy the masked plaintext.</summary>
    public static bool ShouldBlockCopyShortcut(Key key, KeyModifiers modifiers) =>
        (modifiers & KeyModifiers.Control) != 0 && key is Key.C or Key.X or Key.Insert;

    public bool SecretHasFocus() =>
        TopLevel.GetTopLevel(this)?.FocusManager?.GetFocusedElement() is Visual focused &&
        (ReferenceEquals(focused, _secret) || focused.FindAncestorOfType<SecretTextBox>(includeSelf: false) is not null);

    private void OnPreviewKeyDown(object? sender, KeyEventArgs e)
    {
        if (!SecretHasFocus() || !ShouldBlockCopyShortcut(e.Key, e.KeyModifiers))
        {
            return;
        }

        e.Handled = true;
        SetStatus("已禁止复制明文：凭据输入仅掩码显示。");
    }

    private CredentialTargetOption? Selected =>
        _targets.SelectedIndex >= 0 && _targets.SelectedIndex < _options.Count
            ? _options[_targets.SelectedIndex]
            : null;

    private void UpdateTargetState()
    {
        var target = Selected;
        if (target is null)
        {
            _targetState.Text = "目标状态：未选择";
            _clearButton.IsEnabled = false;
            return;
        }

        _targetState.Text = target.IsConfigured
            ? $"状态：{target.StateLabel} · {target.KindLabel} · {target.DisplayName}（替换需二次确认）"
            : $"状态：{target.StateLabel} · {target.KindLabel} · {target.DisplayName}";
        _clearButton.IsEnabled = target.IsConfigured;
    }

    private async Task SaveAsync()
    {
        var target = Selected;
        if (target is null)
        {
            SetStatus("请先选择 provider / proxy 目标；列表为空时请先创建 profile。", error: true);
            return;
        }

        var secret = _secret.Text ?? string.Empty;
        _secret.Text = string.Empty;
        if (secret.Length == 0)
        {
            SetStatus("请输入凭据内容（掩码输入，不会显示明文）。", error: true);
            return;
        }

        if (target.IsConfigured)
        {
            _pendingSecret = secret;
            _pendingTarget = target;
            ShowConfirm($"目标 {target.DisplayName} 已配置凭据（configured）。替换将覆盖现有凭据，确认替换？");
            SetStatus("CREDENTIAL_CONFLICT：该目标已配置凭据；替换需二次确认。", error: true);
            return;
        }

        await RunPutAsync(target, "create", secret);
    }

    private async Task ConfirmReplaceAsync()
    {
        var target = _pendingTarget;
        var secret = _pendingSecret;
        if (target is null || secret is null)
        {
            SetStatus("没有待确认的替换操作。");
            return;
        }

        ClearPending();
        await RunPutAsync(target, "replace", secret);
    }

    private async Task RunPutAsync(CredentialTargetOption target, string intent, string secret)
    {
        _save.IsEnabled = false;
        _replaceButton.IsEnabled = false;
        try
        {
            var result = await _put(target.Kind, target.OwnerId, intent, secret, CancellationToken.None);
            switch (result.Status)
            {
                case CredentialOperationStatus.Configured:
                    ClearPending();
                    SetStatus($"已保存：{target.KindLabel} · {target.DisplayName} → configured。");
                    await RefreshAsync();
                    break;
                case CredentialOperationStatus.Conflict:
                    _pendingSecret = secret;
                    _pendingTarget = target;
                    ShowConfirm("CREDENTIAL_CONFLICT：该目标已配置凭据，替换将覆盖现有凭据。确认替换？");
                    SetStatus("CREDENTIAL_CONFLICT：替换需二次确认。", error: true);
                    break;
                default:
                    ClearPending();
                    SetStatus(Describe(result), error: true);
                    break;
            }
        }
        finally
        {
            _save.IsEnabled = true;
            _replaceButton.IsEnabled = true;
            _secret.Text = string.Empty;
        }
    }

    private async Task ClearAsync()
    {
        var target = Selected;
        if (target is null)
        {
            SetStatus("请先选择要清除的目标。", error: true);
            return;
        }

        _clearButton.IsEnabled = false;
        try
        {
            var result = await _clear(target.Kind, target.OwnerId, CancellationToken.None);
            if (result.IsSuccess)
            {
                SetStatus($"已清除：{target.KindLabel} · {target.DisplayName} → missing。");
                await RefreshAsync();
            }
            else
            {
                SetStatus(Describe(result), error: true);
            }
        }
        finally
        {
            _clearButton.IsEnabled = true;
            ClearSecrets();
        }
    }

    private void ShowConfirm(string message)
    {
        _confirm.Children.Clear();
        _confirm.Children.Add(Ui.Text(message, 11, "TextPrimary"));
        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8 };
        row.Children.Add(_replaceButton);
        row.Children.Add(_cancelButton);
        _confirm.Children.Add(row);
        _confirm.IsVisible = true;
    }

    private void HideConfirm() => _confirm.IsVisible = false;

    private void ClearPending()
    {
        _pendingSecret = null;
        _pendingTarget = null;
        HideConfirm();
    }

    private void SetStatus(string message, bool error = false)
    {
        _status.Text = message;
        _status.Foreground = LegacyChrome.Brush(error ? "TextPrimary" : "TextSecondary");
    }

    private static string Describe(CredentialOperationResult result)
    {
        var code = string.IsNullOrEmpty(result.ErrorCode) ? result.Status.ToString() : result.ErrorCode;
        return result.Status switch
        {
            CredentialOperationStatus.NotReady => $"Host 未就绪（{code}）：请等待 Host 启动后重试。",
            CredentialOperationStatus.Unavailable => $"凭据端口不可用（{code}）：检查 Windows 凭据管理器或 Core 连接。",
            CredentialOperationStatus.InvalidArguments => $"参数无效（{code}）：请检查目标与凭据内容。",
            CredentialOperationStatus.NotFound => $"目标不存在（{code}）：profile 可能已被删除，请刷新。",
            CredentialOperationStatus.Conflict => $"冲突（{code}）：已配置状态与操作不一致，替换需二次确认。",
            _ => $"操作失败（{code}）。",
        };
    }

    private static Button ActionButton(string label, bool primary = false) => new()
    {
        Content = label,
        Padding = new Thickness(14, 7),
        CornerRadius = new CornerRadius(8),
        FontSize = 13,
        Background = LegacyChrome.Brush(primary ? "Accent" : "CardBg"),
        Foreground = LegacyChrome.Brush(primary ? "AccentText" : "TextPrimary"),
        BorderBrush = LegacyChrome.Brush("CardBorder"),
        BorderThickness = new Thickness(1),
    };
}

