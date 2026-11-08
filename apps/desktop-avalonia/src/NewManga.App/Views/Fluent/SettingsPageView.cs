using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Markup.Xaml.MarkupExtensions;
using Avalonia.Automation;
using Avalonia.Controls.Primitives;
using Avalonia.Controls.Shapes;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.Controls;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.DesignSystem.Controls;

namespace NewManga.App.Views.Fluent;

/// <summary>Fluent Settings surface; appearance persistence is delegated to the injected coordinator.</summary>
public sealed class SettingsPageView : UserControl
{
    private readonly SettingsViewModel _viewModel;
    private readonly StackPanel _groups;
    private readonly Border _contentHost;
    private readonly TextBlock _notice;
    private readonly Border _stateHost;
    private readonly SearchField _search;
    private readonly Button _saveButton;
    private readonly Button _cancelButton;
    private readonly Ellipse _dirtyDot;
    private readonly FluentDialog _confirmation;
    private readonly FluentDialog _leaveDialog;
    private readonly Button _leaveCancelButton;
    private readonly Border _scrim;
    private readonly FluentVisibilityMotion _scrimMotion;
    private readonly FluentVisibilityMotion[] _dialogMotions;
    private Action? _pendingLeave;
    private IInputElement? _focusBeforeLeave;
    private BackupPackageInfo? _pendingBackup;
    private string _pendingAction = string.Empty;

    public SettingsPageView(SettingsViewModel viewModel)
    {
        _viewModel = viewModel;
        _groups = FluentUi.Stack("fluent-page-layout");
        _contentHost = new Border();
        _notice = FluentUi.Text(string.Empty, "fluent-status-text");
        _stateHost = new Border { IsVisible = false };
        // I-9：设置页未保存圆点（dirty 指示；语义色 + Name，非仅颜色）。
        _dirtyDot = new Ellipse { Width = 8, Height = 8, IsVisible = false };
        _dirtyDot.Classes.Add("fluent-feedback-badge");
        _dirtyDot[!Shape.FillProperty] = new DynamicResourceExtension("Nm.Color.Status.Blocked");
        AutomationProperties.SetName(_dirtyDot, "有未保存的设置修改");
        _search = FluentUi.Search("搜索设置", "搜索设置分组");
        NameSearchInput(_search, "搜索设置");
        _search.PropertyChanged += (_, args) =>
        {
            if (args.Property != SearchField.TextProperty) return;
            _viewModel.Search = _search.Text ?? string.Empty;
            if (_viewModel.VisibleGroups.Count > 0 && !_viewModel.VisibleGroups.Contains(_viewModel.SelectedGroup))
            {
                _viewModel.SelectedGroup = _viewModel.VisibleGroups[0];
            }
            RenderGroupNavigation();
            RenderGroupContent();
        };
        _saveButton = FluentUi.Button("保存", "fluent-primary", () => _ = _viewModel.SaveAppearanceAsync(), "保存外观设置");
        _cancelButton = FluentUi.Button("取消", "fluent-secondary", CancelDraft, "取消未保存修改");
        _confirmation = new FluentDialog { IsOpen = false };
        _leaveCancelButton = FluentUi.Button("取消", "fluent-secondary", CancelLeave, "取消离开设置页");
        _leaveDialog = new FluentDialog { IsOpen = false, Child = BuildLeaveDialogContent() };
        _scrim = new Border { Classes = { "fluent-modal-scrim" }, IsVisible = false };
        _scrimMotion = new FluentVisibilityMotion(_scrim);
        _dialogMotions = [new(_confirmation, FluentDialog.IsOpenProperty), new(_leaveDialog, FluentDialog.IsOpenProperty)];

        var root = new Grid { RowDefinitions = new RowDefinitions("Auto,*,Auto") };
        root.Children.Add(BuildToolbar());
        var body = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,*") };
        var groupScroll = new ScrollViewer { Content = _groups, VerticalScrollBarVisibility = ScrollBarVisibility.Auto };
        groupScroll.Classes.Add("fluent-settings-groups-pane");
        body.Children.Add(groupScroll);
        var pageArea = FluentUi.Stack("fluent-page-layout");
        pageArea.Children.Add(_stateHost);
        pageArea.Children.Add(new ScrollViewer { Content = _contentHost, VerticalScrollBarVisibility = ScrollBarVisibility.Auto });
        Grid.SetColumn(pageArea, 1);
        body.Children.Add(pageArea);
        Grid.SetRow(body, 1);
        root.Children.Add(body);
        var footer = BuildFooter();
        Grid.SetRow(footer, 2);
        root.Children.Add(footer);
        Content = BuildConfirmationLayer(root);

        _viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(SettingsViewModel.SelectedGroup) or nameof(SettingsViewModel.VisibleGroups) or nameof(SettingsViewModel.State))
            {
                RenderGroupNavigation();
                RenderGroupContent();
            }

            if (args.PropertyName is nameof(SettingsViewModel.State) or nameof(SettingsViewModel.Error)) RenderState();
            if (args.PropertyName is nameof(SettingsViewModel.Notice) or nameof(SettingsViewModel.Status)) RenderNotice();
            if (args.PropertyName is nameof(SettingsViewModel.IsDirty) or nameof(SettingsViewModel.IsSaving) or nameof(SettingsViewModel.IsReadOnly))
            {
                RenderButtons();
                RenderNotice();
                RenderDirtyState();
            }
        };
        RenderGroupNavigation();
        RenderGroupContent();
        RenderState();
        RenderNotice();
        RenderButtons();
        RenderDirtyState();
        _ = _viewModel.LoadAsync();
    }

    public SettingsViewModel ViewModel => _viewModel;

    /// <summary>I-3：离开确认浮层当前是否打开。</summary>
    public bool LeaveConfirmationVisible => _leaveDialog.IsOpen;

    /// <summary>I-3：本页任意确认浮层（备份/Provider/网络编辑等）是否打开；Esc 优先于离开流关闭它。</summary>
    public bool HasOpenConfirmation => _confirmation.IsOpen;

    /// <summary>
    /// I-3：离开设置页的确认流入口。干净（非 dirty）直接离开；有未保存修改时打开
    /// 三分支确认（保存并离开 / 丢弃并离开 / 取消）并挂起导航，返回 false。
    /// </summary>
    public bool TryBeginLeave(Action proceed)
    {
        if (!_viewModel.IsDirty)
        {
            proceed();
            return true;
        }

        _pendingLeave = proceed;
        // I-11 (design 03 §3): move focus into the overlay and remember the trigger so closing the
        // confirmation returns focus instead of dropping it to the window root.
        _focusBeforeLeave = TopLevel.GetTopLevel(this)?.FocusManager?.GetFocusedElement();
        _leaveDialog.IsOpen = true;
        UpdateScrimVisibility();
        _leaveCancelButton.Focus();
        return false;
    }

    /// <summary>I-3：「取消」分支：关闭确认浮层，留在本页且草稿保留。</summary>
    public void CancelLeave()
    {
        _pendingLeave = null;
        _leaveDialog.IsOpen = false;
        UpdateScrimVisibility();
        RestoreFocusAfterLeave();
    }

    /// <summary>I-3/08 §7：浮层内 Esc=取消——普通确认浮层的公开关闭入口（供 shell Esc 协调）。</summary>
    public void CancelConfirmation() => CloseConfirmation();

    private Control BuildLeaveDialogContent()
    {
        // I-3：三分支 = 保存并离开 / 丢弃并离开 / 取消（设计 08 §5「保存/丢弃/取消」）；
        // 默认焦点在「取消」（08 §7 危险确认口径）。
        var panel = FluentUi.Stack("fluent-page-layout");
        panel.Children.Add(FluentUi.Text("未保存的设置修改", "fluent-page-title"));
        panel.Children.Add(FluentUi.Text("离开设置页前，请选择保存、丢弃或取消；保存失败时会留在本页并保留未保存值。"));
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("保存并离开", "fluent-primary", () => _ = SaveAndLeaveAsync(), "保存设置后离开"));
        actions.Children.Add(FluentUi.Button("丢弃并离开", "fluent-danger", DiscardAndLeave, "丢弃未保存修改后离开"));
        actions.Children.Add(_leaveCancelButton);
        panel.Children.Add(actions);
        return panel;
    }

    private async Task SaveAndLeaveAsync()
    {
        var saved = await _viewModel.SaveAppearanceAsync();
        if (!saved)
        {
            // I-3：保存失败保护——留在本页、draft 保留（SaveAppearanceAsync 失败不改 Draft）、错误可见。
            _pendingLeave = null;
            _leaveDialog.IsOpen = false;
            UpdateScrimVisibility();
            RenderGroupContent();
            RenderNotice();
            RenderButtons();
            RenderDirtyState();
            return;
        }

        var proceed = TakePendingLeave();
        proceed?.Invoke();
    }

    private void DiscardAndLeave()
    {
        if (_viewModel.AppearanceCoordinator is not null)
        {
            _viewModel.UpdateDraft(_viewModel.AppearanceCoordinator.Settings);
        }

        var proceed = TakePendingLeave();
        RenderGroupContent();
        RenderButtons();
        RenderDirtyState();
        proceed?.Invoke();
    }

    private Action? TakePendingLeave()
    {
        _leaveDialog.IsOpen = false;
        UpdateScrimVisibility();
        var proceed = _pendingLeave;
        _pendingLeave = null;
        RestoreFocusAfterLeave();
        return proceed;
    }

    /// <summary>I-11: closing the leave overlay returns focus to the element that opened it.</summary>
    private void RestoreFocusAfterLeave()
    {
        var previous = _focusBeforeLeave;
        _focusBeforeLeave = null;
        if (previous is Control control && control.Focusable && control.IsEffectivelyEnabled && control.IsVisible)
        {
            control.Focus();
        }
    }

    private void UpdateScrimVisibility() => _scrimMotion.SetVisible(_confirmation.IsOpen || _leaveDialog.IsOpen);

    internal void ConfigureMotion(MotionTimingProfile timings, IFluentMotionClock clock)
    {
        _scrimMotion.Configure(timings.NavigationOverlayInMilliseconds > 0 ? timings.NavigationOverlayOutMilliseconds : 0,
            timings.NavigationOverlayOutMilliseconds, clock);
        foreach (var motion in _dialogMotions)
            motion.Configure(timings.NavigationOverlayInMilliseconds, timings.NavigationOverlayOutMilliseconds, clock);
    }

    private void HandleScrimPressed()
    {
        // I-3/08 §7：遮罩点击与 Esc 同义——离开确认打开时=取消离开；否则关闭普通确认浮层。
        if (_leaveDialog.IsOpen)
        {
            CancelLeave();
        }
        else
        {
            CloseConfirmation();
        }
    }

    private void RenderDirtyState() => _dirtyDot.IsVisible = _viewModel.IsDirty;

    private Control BuildToolbar()
    {
        var toolbar = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        var title = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        title.Children.Add(FluentUi.Text("设置", "fluent-page-title"));
        title.Children.Add(_dirtyDot);
        toolbar.Children.Add(title);
        toolbar.Children.Add(_search);
        toolbar.Children.Add(_notice);
        return toolbar;
    }

    private Control BuildFooter()
    {
        var footer = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        footer.Children.Add(_saveButton);
        footer.Children.Add(_cancelButton);
        footer.Children.Add(FluentUi.Button("重置外观", "fluent-secondary", ResetAppearance, "重置外观分组"));
        return footer;
    }

    private Control BuildConfirmationLayer(Control root)
    {
        var overlay = new Grid { RowDefinitions = new RowDefinitions("*,Auto,*") };
        overlay.Children.Add(root);
        overlay.Children.Add(_scrim);
        Grid.SetRowSpan(_scrim, 3);
        _scrim.PointerPressed += (_, _) => HandleScrimPressed();
        _confirmation.Child ??= FluentUi.Stack("fluent-page-layout");
        overlay.Children.Add(_confirmation);
        Grid.SetRow(_confirmation, 1);
        overlay.Children.Add(_leaveDialog);
        Grid.SetRow(_leaveDialog, 1);
        return overlay;
    }

    private void RenderGroupNavigation()
    {
        _groups.Children.Clear();
        foreach (var group in _viewModel.VisibleGroups)
        {
            var button = FluentUi.Button(SettingsViewModel.GroupLabel(group), "fluent-nav",
                () => _viewModel.SelectedGroup = group, SettingsViewModel.GroupLabel(group));
            button.Classes.Set("selected", _viewModel.SelectedGroup == group);
            _groups.Children.Add(button);
        }
    }

    private void RenderGroupContent()
    {
        if (_viewModel.VisibleGroups.Count == 0)
        {
            _contentHost.Child = FluentUi.Card(FluentUi.Empty("无匹配", "没有匹配的设置分组。", "清空搜索", () => _search.Text = string.Empty));
            return;
        }

        _contentHost.Child = _viewModel.SelectedGroup switch
        {
            SettingsGroupId.Appearance => BuildAppearanceGroup(),
            SettingsGroupId.Providers => BuildProviderGroup(),
            SettingsGroupId.Network => BuildNetworkGroup(),
            SettingsGroupId.Backup => BuildBackupGroup(),
            SettingsGroupId.About => BuildAboutGroup(),
            _ => FluentUi.Empty("没有可用设置", "请重试读取设置。", "重试", () => _ = _viewModel.LoadAsync()),
        };

        if (_viewModel.IsReadOnly && _contentHost.Child is Control content)
        {
            DisableWriteControls(content);
        }

        if (!string.IsNullOrWhiteSpace(_viewModel.Search) && _contentHost.Child is Control filtered)
        {
            ApplyFieldSearch(filtered, _viewModel.Search);
        }
    }

    /// <summary>
    /// FEA-06-RESIDUAL-3 AC-5 A3：SearchField 的真实 Tab 落点是其内部 TextBox（DesignSystem 控件，
    /// 不在本卡 allowed_paths）；在视图侧把同一语义名补到内部输入框，保证 Tab 落点有可读名。
    /// </summary>
    private static void NameSearchInput(SearchField field, string name)
    {
        if (field.Child is Control input)
        {
            AutomationProperties.SetName(input, name);
        }
    }

    private static void ApplyFieldSearch(Control root, string search)
    {
        foreach (var field in Descendants(root).OfType<SettingsField>())
        {
            var label = field.Children.OfType<TextBlock>().FirstOrDefault()?.Text ?? string.Empty;
            var name = AutomationProperties.GetName(field.Children.OfType<Control>().Skip(1).FirstOrDefault() ?? field) ?? string.Empty;
            field.IsVisible = label.Contains(search, StringComparison.CurrentCultureIgnoreCase) ||
                name.Contains(search, StringComparison.CurrentCultureIgnoreCase);
        }
    }

    private static void DisableWriteControls(Control root)
    {
        foreach (var control in Descendants(root))
        {
            if (control is Button or ComboBox or CheckBox or TextBox or Slider)
            {
                control.IsEnabled = false;
                if (string.IsNullOrWhiteSpace(ToolTip.GetTip(control)?.ToString()))
                {
                    ToolTip.SetTip(control, "Host 处于只读状态；设置可浏览，写入已禁用。");
                }
            }
        }
    }

    private static IEnumerable<Control> Descendants(Control root)
    {
        yield return root;
        if (root is ContentControl { Content: Control content })
        {
            foreach (var nested in Descendants(content)) yield return nested;
        }

        if (root is Border { Child: Control borderChild })
        {
            foreach (var nested in Descendants(borderChild)) yield return nested;
        }

        if (root is Panel panel)
        {
            foreach (var child in panel.Children.OfType<Control>())
            {
                foreach (var nested in Descendants(child)) yield return nested;
            }
        }
    }

    private Control BuildAppearanceGroup()
    {
        var cardContent = FluentUi.Stack("fluent-page-layout");
        cardContent.Children.Add(FluentUi.Text("外观", "fluent-page-title"));
        AddCombo(cardContent, "theme.visualThemeId", ["newmanga-default", "builtin.fluent-dark"], _viewModel.Draft.VisualThemeId,
            selected => _viewModel.UpdateDraft(_viewModel.Draft with { VisualThemeId = selected }));
        AddCombo(cardContent, "theme.frontendId", ["builtin.current-v2", "builtin.fluent"], _viewModel.Draft.FrontendId,
            selected => _viewModel.UpdateDraft(_viewModel.Draft with { FrontendId = selected }));
        cardContent.Children.Add(FluentUi.Text("frontendId 的更改在下次启动时由 FrontendSelector 读取。", "fluent-subtle-text"));
        AddCombo(cardContent, "appearance.mode", ["system", "light", "dark"], ToString(_viewModel.Draft.Mode),
            selected => _viewModel.UpdateDraft(_viewModel.Draft with { Mode = ParseAppearance(selected) }));
        AddCombo(cardContent, "appearance.contrast", ["standard", "high"], _viewModel.Draft.Contrast == AppearanceContrast.High ? "high" : "standard",
            selected => _viewModel.UpdateDraft(_viewModel.Draft with { Contrast = selected == "high" ? AppearanceContrast.High : AppearanceContrast.Standard }));
        AddCombo(cardContent, "motion.mode", ["auto", "full", "reduce"], ToString(_viewModel.Draft.MotionMode),
            selected => _viewModel.UpdateDraft(_viewModel.Draft with { MotionMode = ParseMotion(selected) }));
        cardContent.Children.Add(FluentUi.Text("motion.categories", "fluent-status-text"));
        cardContent.Children.Add(FluentUi.Check("motion.categories.navigation", _viewModel.Draft.MotionCategories.HasFlag(MotionCategories.Navigation)));
        cardContent.Children.Add(FluentUi.Check("motion.categories.feedback", _viewModel.Draft.MotionCategories.HasFlag(MotionCategories.Feedback)));
        cardContent.Children.Add(FluentUi.Check("motion.categories.decorative", _viewModel.Draft.MotionCategories.HasFlag(MotionCategories.Decorative)));
        foreach (var check in cardContent.Children.OfType<CheckBox>().TakeLast(3))
        {
            check.IsEnabled = !_viewModel.IsReadOnly;
            check.IsCheckedChanged += (_, _) =>
            {
                var flags = MotionCategories.None;
                var categories = cardContent.Children.OfType<CheckBox>().TakeLast(3).ToArray();
                if (categories[0].IsChecked == true) flags |= MotionCategories.Navigation;
                if (categories[1].IsChecked == true) flags |= MotionCategories.Feedback;
                if (categories[2].IsChecked == true) flags |= MotionCategories.Decorative;
                _viewModel.UpdateDraft(_viewModel.Draft with { MotionCategories = flags });
            };
        }
        AddCombo(cardContent, "corners.scale", ["sm", "md", "lg"], ToString(_viewModel.Draft.CornersScale),
            selected => _viewModel.UpdateDraft(_viewModel.Draft with { CornersScale = selected switch { "sm" => CornersScale.Sm, "lg" => CornersScale.Lg, _ => CornersScale.Md } }),
            enabled: _viewModel.FluentMaterialAvailable,
            disabledReason: "圆角字段仅在 Fluent frontend + Fluent visualTheme 下可用；Current 下字段保留但忽略。");
        var acrylic = FluentUi.Slider("material.acrylicStrength", 0, 1, _viewModel.Draft.MaterialAcrylicStrength);
        acrylic.IsEnabled = _viewModel.FluentMaterialAvailable && !_viewModel.IsReadOnly;
        acrylic.ValueChanged += (_, args) => _viewModel.UpdateDraft(_viewModel.Draft with { MaterialAcrylicStrength = args.NewValue });
        cardContent.Children.Add(FluentUi.Field("material.acrylicStrength", acrylic,
            _viewModel.FluentMaterialAvailable ? null : "仅 Fluent 外观可用；Current 下忽略。"));
        var mica = FluentUi.Check("material.micaEnabled", _viewModel.Draft.MaterialMicaEnabled);
        mica.IsEnabled = _viewModel.FluentMaterialAvailable && !_viewModel.IsReadOnly;
        mica.IsCheckedChanged += (_, _) => _viewModel.UpdateDraft(_viewModel.Draft with { MaterialMicaEnabled = mica.IsChecked == true });
        if (!_viewModel.FluentMaterialAvailable) ToolTip.SetTip(mica, "仅 Fluent 外观可用；Current 下忽略。");
        cardContent.Children.Add(mica);
        cardContent.Children.Add(FluentUi.Field("layout.id", FluentUi.Input("layout.id", initialText: _viewModel.Draft.Layout.Id)));
        cardContent.Children.OfType<SettingsField>().Last().Children.OfType<TextBox>().First().IsReadOnly = true;
        AddCombo(cardContent, "layout.navigation", ["top-band", "sidebar", "dock"], _viewModel.Draft.Layout.Navigation,
            selected => UpdateLayout(layout => layout with { Navigation = selected }));
        AddCombo(cardContent, "layout.shelf", ["grid", "list", "masonry"], _viewModel.Draft.Layout.Shelf,
            selected => UpdateLayout(layout => layout with { Shelf = selected }));
        AddCombo(cardContent, "layout.density", ["comfortable", "compact", "spacious"], _viewModel.Draft.Layout.Density,
            selected => UpdateLayout(layout => layout with { Density = selected }));
        AddCombo(cardContent, "layout.workbench", ["stacked", "split"], _viewModel.Draft.Layout.Workbench,
            selected => UpdateLayout(layout => layout with { Workbench = selected }));
        AddCombo(cardContent, "layout.reader", ["fit-page", "fit-width", "double-page", "webtoon"], _viewModel.Draft.Layout.Reader,
            selected => UpdateLayout(layout => layout with { Reader = selected }));
        var accent = FluentUi.Check("appearance.followSystemAccent", _viewModel.Draft.FollowSystemAccent);
        accent.IsEnabled = !_viewModel.IsReadOnly;
        accent.IsCheckedChanged += (_, _) => _viewModel.UpdateDraft(_viewModel.Draft with { FollowSystemAccent = accent.IsChecked == true });
        cardContent.Children.Add(accent);
        cardContent.Children.Add(FluentUi.Field("schemaVersion", FluentUi.Input("schemaVersion", initialText: _viewModel.Draft.SchemaVersion.ToString())));
        cardContent.Children.OfType<SettingsField>().Last().Children.OfType<TextBox>().First().IsReadOnly = true;
        return new SettingsGroup { Child = cardContent };
    }

    private Control BuildProviderGroup()
    {
        var stack = FluentUi.Stack("fluent-page-layout");
        stack.Children.Add(FluentUi.Text("Provider 与凭据", "fluent-page-title"));
        stack.Children.Add(FluentUi.Button("添加 Provider", "fluent-primary", () => ShowProviderEditor(null), "添加 Provider Profile"));
        if (_viewModel.Providers.Count == 0)
        {
            stack.Children.Add(FluentUi.Empty("暂无 Provider", "列表来自 Host；凭据不会回显明文。", null, null));
        }

        foreach (var profile in _viewModel.Providers)
        {
            var card = FluentUi.Stack("fluent-page-layout");
            card.Children.Add(FluentUi.Text(profile.DisplayText, "fluent-status-text"));
            card.Children.Add(FluentUi.Text($"端点：{profile.Endpoint} · 模型：{profile.Model}", "fluent-subtle-text"));
            card.Children.Add(FluentUi.Text($"凭据：{profile.CredentialState}", "fluent-subtle-text"));
            card.Children.Add(FluentUi.Button(profile.Enabled ? "禁用 Provider" : "启用 Provider", "fluent-secondary",
                () => _ = _viewModel.ToggleProviderAsync(profile), profile.Enabled ? "禁用 Provider" : "启用 Provider"));
            var profileActions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
            profileActions.Children.Add(FluentUi.Button("编辑", "fluent-secondary", () => ShowProviderEditor(profile), $"编辑 {profile.DisplayName}"));
            profileActions.Children.Add(FluentUi.Button("删除…", "fluent-danger", () => ShowSimpleConfirmation(
                "删除 Provider Profile", $"将删除「{profile.DisplayName}」配置；不会删除凭据明文。",
                async () => await _viewModel.DeleteProviderAsync(profile)), $"删除 {profile.DisplayName}"));
            card.Children.Add(profileActions);
            stack.Children.Add(new SettingsGroup { Child = card });
        }

        stack.Children.Add(FluentUi.Text("凭据引用", "fluent-status-text"));
        if (_viewModel.CredentialTargets.Count == 0)
        {
            stack.Children.Add(FluentUi.Text("暂无凭据目标。", "fluent-subtle-text"));
        }

        foreach (var target in _viewModel.CredentialTargets)
        {
            var row = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
            row.Children.Add(FluentUi.Text(target.DisplayText, "fluent-status-text"));
            var password = new TextBox { PasswordChar = '●', Watermark = "仅输入新凭据，不回显已有值" };
            Avalonia.Automation.AutomationProperties.SetName(password, $"{target.DisplayName} 凭据");
            var save = FluentUi.Button("保存凭据", "fluent-secondary", null, "保存凭据");
            save.IsEnabled = !_viewModel.IsReadOnly;
            save.Click += async (_, _) =>
            {
                var secret = password.Text;
                password.Text = string.Empty;
                await _viewModel.SaveCredentialAsync(target, secret ?? string.Empty);
            };
            row.Children.Add(password);
            row.Children.Add(save);
            stack.Children.Add(row);
        }

        return new SettingsGroup { Child = stack };
    }

    private Control BuildNetworkGroup()
    {
        var stack = FluentUi.Stack("fluent-page-layout");
        stack.Children.Add(FluentUi.Text("网络", "fluent-page-title"));
        stack.Children.Add(FluentUi.Text("只显示 Host 返回的现有 Profile 字段。代理凭据以 credential_state 表示，不显示明文。", "fluent-subtle-text"));
        stack.Children.Add(FluentUi.Text("当前冻结 Host Profile 契约不含超时与并发字段；此页仅编辑 mode、proxy endpoint、TLS 与直连回退。", "fluent-subtle-text"));
        stack.Children.Add(FluentUi.Button("添加网络 Profile", "fluent-primary", () => ShowNetworkEditor(null), "添加网络 Profile"));
        if (_viewModel.Networks.Count == 0)
        {
            stack.Children.Add(FluentUi.Empty("暂无网络 Profile", "可从既有网络管理 surface 配置代理、TLS 和回退策略。", null, null));
        }

        foreach (var network in _viewModel.Networks)
        {
            var card = FluentUi.Stack("fluent-page-layout");
            card.Children.Add(FluentUi.Text(network.DisplayText, "fluent-status-text"));
            card.Children.Add(FluentUi.Text($"TLS：{network.TlsVerificationState} · 代理失败直连：{network.AllowProxyFailureDirectFallback}", "fluent-subtle-text"));
            card.Children.Add(FluentUi.Button("设为默认网络", "fluent-secondary", () => _ = _viewModel.SetNetworkDefaultAsync(network), "设为默认网络 Profile"));
            var provider = _viewModel.Providers.FirstOrDefault();
            card.Children.Add(FluentUi.Button("运行网络诊断", "fluent-secondary",
                provider is null ? null : () => _ = _viewModel.TestNetworkAsync(network, provider), "运行网络诊断"));
            var profileActions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
            profileActions.Children.Add(FluentUi.Button("编辑", "fluent-secondary", () => ShowNetworkEditor(network), $"编辑 {network.DisplayName}"));
            profileActions.Children.Add(FluentUi.Button("删除…", "fluent-danger", () => ShowSimpleConfirmation(
                "删除网络 Profile", $"将删除「{network.DisplayName}」网络配置。",
                async () => await _viewModel.DeleteNetworkAsync(network)), $"删除 {network.DisplayName}"));
            card.Children.Add(profileActions);
            stack.Children.Add(new SettingsGroup { Child = card });
        }

        return new SettingsGroup { Child = stack };
    }

    private Control BuildBackupGroup()
    {
        var stack = FluentUi.Stack("fluent-page-layout");
        stack.Children.Add(FluentUi.Text("备份与恢复", "fluent-page-title"));
        stack.Children.Add(FluentUi.Text("恢复由 Core 执行整库锁与恢复前回滚包；这里只在用户确认后调用既有 Host 端口。", "fluent-subtle-text"));
        var create = FluentUi.Button("创建手动备份", "fluent-primary", () => _ = _viewModel.CreateBackupAsync(), "创建手动备份");
        create.IsEnabled = !_viewModel.IsReadOnly;
        stack.Children.Add(create);
        if (_viewModel.Backups.Count == 0)
        {
            stack.Children.Add(FluentUi.Empty("没有备份包", "Core 尚未返回任何备份。", null, null));
        }

        foreach (var backup in _viewModel.Backups)
        {
            var card = FluentUi.Stack("fluent-page-layout");
            card.Children.Add(FluentUi.Text($"{backup.BackupType} · {backup.CreatedAt}", "fluent-status-text"));
            card.Children.Add(FluentUi.Text($"{backup.SizeBytes} bytes · schema {backup.SchemaVersion} · {(backup.Verified ? "已校验" : "未校验")}", "fluent-subtle-text"));
            var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
            var restore = FluentUi.Button("恢复…", "fluent-secondary", () => ShowBackupConfirmation(backup, "restore"), "恢复此备份");
            restore.IsEnabled = !_viewModel.IsReadOnly && backup.Verified;
            var delete = FluentUi.Button("删除…", "fluent-danger", () => ShowBackupConfirmation(backup, "delete"), "删除此备份包");
            delete.IsEnabled = !_viewModel.IsReadOnly;
            actions.Children.Add(restore);
            actions.Children.Add(delete);
            card.Children.Add(actions);
            stack.Children.Add(new SettingsGroup { Child = card });
        }

        return new SettingsGroup { Child = stack };
    }

    private Control BuildAboutGroup()
    {
        var stack = FluentUi.Stack("fluent-page-layout");
        stack.Children.Add(FluentUi.Text("关于", "fluent-page-title"));
        stack.Children.Add(FluentUi.Field("版本", FluentUi.Input("版本", initialText: _viewModel.Version)));
        stack.Children.OfType<SettingsField>().Last().Children.OfType<TextBox>().First().IsReadOnly = true;
        stack.Children.Add(FluentUi.Field("许可证", FluentUi.Input("许可证", initialText: _viewModel.License)));
        stack.Children.OfType<SettingsField>().Last().Children.OfType<TextBox>().First().IsReadOnly = true;
        stack.Children.Add(FluentUi.Text("开源声明随包发布；本界面不下载或引入额外字体、图标资产。", "fluent-subtle-text"));
        return new SettingsGroup { Child = stack };
    }

    private void AddCombo(StackPanel stack, string label, IReadOnlyList<string> items, string selected,
        Action<string> changed, bool enabled = true, string? disabledReason = null)
    {
        var combo = FluentUi.Combo(label, items, selected);
        combo.IsEnabled = enabled && !_viewModel.IsReadOnly;
        combo.SelectionChanged += (_, _) =>
        {
            if (combo.SelectedItem is string value) changed(value);
        };
        if (!string.IsNullOrWhiteSpace(disabledReason)) ToolTip.SetTip(combo, disabledReason);
        stack.Children.Add(FluentUi.Field(label, combo, disabledReason));
    }

    private void UpdateLayout(Func<LayoutSettings, LayoutSettings> update) =>
        _viewModel.UpdateDraft(_viewModel.Draft with { Layout = update(_viewModel.Draft.Layout) });

    private void RenderState()
    {
        _stateHost.IsVisible = _viewModel.State is FluentPageState.Error or FluentPageState.Loading or FluentPageState.ReadOnly;
        if (_viewModel.State == FluentPageState.Loading)
        {
            var loading = FluentUi.Stack("fluent-page-layout");
            loading.Children.Add(new Skeleton { Variant = SkeletonVariant.Panel });
            loading.Children.Add(FluentUi.Text("正在读取设置…", "fluent-status-text"));
            _stateHost.Child = FluentUi.Card(loading);
        }
        else if (_viewModel.State == FluentPageState.Error)
        {
            _stateHost.Child = FluentUi.Banner(StatusKind.Failed, "设置错误", _viewModel.Error, "重试", () => _ = _viewModel.LoadAsync());
        }
        else if (_viewModel.State == FluentPageState.ReadOnly)
        {
            _stateHost.Child = FluentUi.Banner(StatusKind.Locked, "只读模式", _viewModel.Status, null, null);
        }
    }

    private void RenderNotice()
    {
        _notice.Text = string.IsNullOrWhiteSpace(_viewModel.Error) ? _viewModel.Notice : _viewModel.Error;
        AutomationProperties.SetLiveSetting(_notice, AutomationLiveSetting.Polite);
    }

    private void RenderButtons()
    {
        _saveButton.IsEnabled = !_viewModel.IsReadOnly && !_viewModel.IsSaving && _viewModel.IsDirty;
        _cancelButton.IsEnabled = !_viewModel.IsReadOnly && _viewModel.IsDirty;
    }

    private void CancelDraft()
    {
        if (_viewModel.AppearanceCoordinator is null) return;
        _viewModel.UpdateDraft(_viewModel.AppearanceCoordinator.Settings);
        RenderGroupContent();
        RenderButtons();
    }

    private void ResetAppearance()
    {
        _viewModel.ResetAppearance();
        RenderGroupContent();
        RenderButtons();
    }

    private void ShowBackupConfirmation(BackupPackageInfo backup, string action)
    {
        _pendingBackup = backup;
        _pendingAction = action;
        var stack = FluentUi.Stack("fluent-page-layout");
        var isRestore = action == "restore";
        stack.Children.Add(FluentUi.Text(isRestore ? "确认整库恢复" : "确认删除备份", "fluent-page-title"));
        stack.Children.Add(FluentUi.Text(isRestore
            ? $"将恢复 {backup.BackupType} · {backup.CreatedAt}。Core 会持有整库锁并先创建恢复前回滚包。"
            : $"将删除备份包 {backup.BackupId}。此操作不会删除任何用户源文件。"));
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("取消", "fluent-secondary", CloseConfirmation, "取消危险操作"));
        actions.Children.Add(FluentUi.Button(isRestore ? "确认恢复" : "确认删除", "fluent-danger",
            () => _ = ConfirmBackupActionAsync(), isRestore ? "确认整库恢复" : "确认删除备份"));
        stack.Children.Add(actions);
        _confirmation.Child = stack;
        _confirmation.IsOpen = true;
        UpdateScrimVisibility();
        actions.Children.OfType<Button>().First().Focus();
    }

    private void ShowProviderEditor(ProviderProfileInfo? profile)
    {
        var providerId = FluentUi.Input("providerId", initialText: profile?.ProviderId ?? string.Empty);
        var displayName = FluentUi.Input("displayName", initialText: profile?.DisplayName ?? string.Empty);
        var endpoint = FluentUi.Input("endpoint", initialText: profile?.Endpoint ?? string.Empty);
        var model = FluentUi.Input("model", initialText: profile?.Model ?? string.Empty);
        var enabled = FluentUi.Check("enabled", profile?.Enabled ?? true);
        var caps = SettingsCapabilities.All.Select(capability =>
            (Capability: capability, Check: FluentUi.Check(capability, profile?.Capabilities.Contains(capability) == true))).ToArray();
        var networkOptions = new[] { "—" }.Concat(_viewModel.Networks.Select(item => item.NetworkProfileId)).ToArray();
        var network = FluentUi.Combo("networkProfileId", networkOptions, profile?.NetworkProfileId ?? "—");
        var content = FluentUi.Stack("fluent-page-layout");
        content.Children.Add(FluentUi.Text(profile is null ? "新建 Provider Profile" : "编辑 Provider Profile", "fluent-page-title"));
        content.Children.Add(FluentUi.Field("providerId", providerId));
        content.Children.Add(FluentUi.Field("displayName", displayName));
        content.Children.Add(FluentUi.Field("endpoint", endpoint));
        content.Children.Add(FluentUi.Field("model", model));
        content.Children.Add(FluentUi.Field("networkProfileId", network));
        content.Children.Add(FluentUi.Text("capabilities", "fluent-status-text"));
        foreach (var item in caps) content.Children.Add(item.Check);
        content.Children.Add(enabled);
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("取消", "fluent-secondary", CloseConfirmation, "取消编辑"));
        actions.Children.Add(FluentUi.Button("保存", "fluent-primary", async () =>
        {
            CloseConfirmation();
            var capabilities = caps.Where(item => item.Check.IsChecked == true).Select(item => item.Capability).ToArray();
            await _viewModel.SaveProviderAsync(profile?.ProfileId,
                new ProviderProfileDraft(providerId.Text ?? string.Empty, displayName.Text ?? string.Empty,
                    capabilities, endpoint.Text ?? string.Empty, model.Text ?? string.Empty,
                    network.SelectedItem is string networkId && networkId != "—" ? networkId : null,
                    enabled.IsChecked == true));
            RenderGroupContent();
            RenderNotice();
        }, "保存 Provider Profile"));
        content.Children.Add(actions);
        ShowDialog(content, actions.Children.OfType<Button>().First());
    }

    private void ShowNetworkEditor(NetworkProfileInfo? profile)
    {
        var displayName = FluentUi.Input("displayName", initialText: profile?.DisplayName ?? string.Empty);
        var mode = FluentUi.Combo("mode", NetworkModes.All, profile?.Mode ?? NetworkModes.Direct);
        var endpoint = FluentUi.Input("proxyEndpoint", initialText: profile?.ProxyEndpoint ?? string.Empty);
        var verifyTls = FluentUi.Check("verifyTls", profile?.VerifyTls ?? true);
        var confirmTls = FluentUi.Check("confirmDisableTlsVerification", false);
        var fallback = FluentUi.Check("allowProxyFailureDirectFallback", profile?.AllowProxyFailureDirectFallback ?? false);
        var content = FluentUi.Stack("fluent-page-layout");
        content.Children.Add(FluentUi.Text(profile is null ? "新建网络 Profile" : "编辑网络 Profile", "fluent-page-title"));
        content.Children.Add(FluentUi.Field("displayName", displayName));
        content.Children.Add(FluentUi.Field("mode", mode));
        content.Children.Add(FluentUi.Field("proxyEndpoint", endpoint));
        content.Children.Add(verifyTls);
        content.Children.Add(confirmTls);
        content.Children.Add(fallback);
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("取消", "fluent-secondary", CloseConfirmation, "取消编辑"));
        actions.Children.Add(FluentUi.Button("保存", "fluent-primary", async () =>
        {
            CloseConfirmation();
            var selectedMode = mode.SelectedItem?.ToString() ?? NetworkModes.Direct;
            await _viewModel.SaveNetworkAsync(profile?.NetworkProfileId,
                new NetworkProfileDraft(displayName.Text ?? string.Empty, selectedMode,
                    string.IsNullOrWhiteSpace(endpoint.Text) ? null : endpoint.Text,
                    verifyTls.IsChecked == true, confirmTls.IsChecked == true,
                    fallback.IsChecked == true));
            RenderGroupContent();
            RenderNotice();
        }, "保存网络 Profile"));
        content.Children.Add(actions);
        ShowDialog(content, actions.Children.OfType<Button>().First());
    }

    private void ShowSimpleConfirmation(string title, string message, Func<Task> confirm)
    {
        var content = FluentUi.Stack("fluent-page-layout");
        content.Children.Add(FluentUi.Text(title, "fluent-page-title"));
        content.Children.Add(FluentUi.Text(message, "fluent-status-text"));
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("取消", "fluent-secondary", CloseConfirmation, "取消危险操作"));
        actions.Children.Add(FluentUi.Button("确认删除", "fluent-danger", async () =>
        {
            CloseConfirmation();
            await confirm();
            RenderGroupContent();
            RenderNotice();
        }, "确认删除配置"));
        content.Children.Add(actions);
        ShowDialog(content, actions.Children.OfType<Button>().First());
    }

    private void ShowDialog(Control content, Control initialFocus)
    {
        _confirmation.Child = content;
        _confirmation.IsOpen = true;
        UpdateScrimVisibility();
        initialFocus.Focus();
    }

    private async Task ConfirmBackupActionAsync()
    {
        if (_pendingBackup is not { } backup) return;
        if (_pendingAction == "restore") await _viewModel.RestoreBackupAsync(backup);
        else await _viewModel.DeleteBackupAsync(backup);
        CloseConfirmation();
        RenderGroupContent();
        RenderNotice();
    }

    private void CloseConfirmation()
    {
        _confirmation.IsOpen = false;
        UpdateScrimVisibility();
        _pendingBackup = null;
        _pendingAction = string.Empty;
    }

    private static string ToString(AppearanceMode mode) => mode switch
    {
        AppearanceMode.Light => "light",
        AppearanceMode.Dark => "dark",
        _ => "system",
    };

    private static string ToString(MotionMode mode) => mode switch
    {
        MotionMode.Full => "full",
        MotionMode.Reduce => "reduce",
        _ => "auto",
    };

    private static string ToString(CornersScale scale) => scale switch
    {
        CornersScale.Sm => "sm",
        CornersScale.Lg => "lg",
        _ => "md",
    };

    private static AppearanceMode ParseAppearance(string value) => value switch
    {
        "light" => AppearanceMode.Light,
        "dark" => AppearanceMode.Dark,
        _ => AppearanceMode.System,
    };

    private static MotionMode ParseMotion(string value) => value switch
    {
        "full" => MotionMode.Full,
        "reduce" => MotionMode.Reduce,
        _ => MotionMode.Auto,
    };
}
