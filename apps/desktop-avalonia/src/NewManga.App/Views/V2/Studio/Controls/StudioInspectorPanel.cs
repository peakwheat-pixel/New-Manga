using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Templates;
using Avalonia.Controls.Primitives;
using Avalonia.Data;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3 <c>Inspector</c>: 40px icon rail ⇄ 320px panel, five tabs (文本 / 样式 / 修复 / 锁定 / 历史).
/// All five tab bodies are built once and kept alive, so switching tabs never loses a pending edit or a
/// loaded revision list (AC2). Controls whose command lives in the unmerged F0-1 write face are visible,
/// disabled and carry the "能力待接入" tooltip — the panel never pretends a write succeeded.
/// </summary>
public sealed class StudioInspectorPanel : Border
{
    private readonly StudioPageViewModel _page;
    private readonly StudioInspectorViewModel _inspector;
    private readonly Dictionary<StudioInspectorTab, Button> _tabButtons = new();
    private readonly Dictionary<StudioInspectorTab, Control> _tabPanels = new();
    private readonly Dictionary<StudioInspectorTab, Control> _tabContentWrappers = new();
    private readonly Border _rail;
    private readonly ScrollViewer _content;
    private readonly TextBlock _header;
    private readonly Button _collapseButton;
    private Button _saveTranslationButton = null!;
    private Button _applyTypeButton = null!;
    private Button _rerenderButton = null!;
    private Button _restoreButton = null!;
    private readonly List<Button> _lockButtons = new();
    private readonly List<Button> _typeOptionButtons = new();

    public StudioInspectorPanel(StudioPageViewModel page)
    {
        _page = page;
        _inspector = page.Inspector;
        Classes.Add("studio-inspector");
        Width = page.InspectorWidth;

        _tabButtons[StudioInspectorTab.Text] = CreateTabButton(StudioInspectorTab.Text, "文", "文本");
        _tabButtons[StudioInspectorTab.Style] = CreateTabButton(StudioInspectorTab.Style, "样", "样式");
        _tabButtons[StudioInspectorTab.Repair] = CreateTabButton(StudioInspectorTab.Repair, "修", "修复");
        _tabButtons[StudioInspectorTab.Locks] = CreateTabButton(StudioInspectorTab.Locks, "锁", "锁定");
        _tabButtons[StudioInspectorTab.History] = CreateTabButton(StudioInspectorTab.History, "史", "历史");

        _collapseButton = StudioUi.Button(page.InspectorToggleLabel, "studio-tab ghost", () =>
        {
            page.InspectorExpanded = !page.InspectorExpanded;
        });
        ToolTip.SetTip(_collapseButton, page.InspectorToggleTooltip);

        var railStack = new StackPanel { Orientation = Orientation.Vertical, Spacing = 2 };
        railStack.Children.Add(_collapseButton);
        railStack.Children.Add(WithHeight(StudioUi.Box("studio-divider"), 1));
        foreach (var (tab, _, _) in _inspector.Tabs)
        {
            railStack.Children.Add(_tabButtons[tab]);
        }

        _rail = StudioUi.Box("studio-inspector-rail");
        _rail.Width = 40;
        _rail.Child = railStack;

        _header = new TextBlock { Classes = { "nm-label" } };
        _header.Bind(TextBlock.TextProperty, new Binding(nameof(StudioInspectorViewModel.ActiveTabLabel)));
        var titleRow = StudioUi.Row(8);
        titleRow.Margin = new Thickness(12, 8);
        titleRow.Children.Add(_header);

        var regionSummary = new TextBlock { Classes = { "nm-meta", "nm-muted" } };
        regionSummary.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.SelectedRegionSummary)) { Source = _page });
        titleRow.Children.Add(regionSummary);

        _tabPanels[StudioInspectorTab.Text] = BuildTextPanel();
        _tabPanels[StudioInspectorTab.Style] = BuildStylePanel();
        _tabPanels[StudioInspectorTab.Repair] = BuildRepairPanel();
        _tabPanels[StudioInspectorTab.Locks] = BuildLocksPanel();
        _tabPanels[StudioInspectorTab.History] = BuildHistoryPanel();


        var panelHost = new Grid();
        foreach (var (tab, panel) in _tabPanels)
        {
            panel.DataContext = _inspector;
            var wrapper = new Border { Child = panel, IsVisible = tab == StudioInspectorTab.Text };
            _tabContentWrappers[tab] = wrapper;
            panelHost.Children.Add(wrapper);
        }

        _content = new ScrollViewer
        {
            Content = panelHost,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
        };

        var contentColumn = new Grid { RowDefinitions = new RowDefinitions("Auto,*") };
        Grid.SetRow(titleRow, 0);
        Grid.SetRow(_content, 1);
        contentColumn.Children.Add(titleRow);
        contentColumn.Children.Add(_content);
        var contentBorder = StudioUi.Box(contentColumn);
        contentBorder.Width = 280;

        var root = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,Auto") };
        Grid.SetColumn(_rail, 0);
        Grid.SetColumn(contentBorder, 1);
        root.Children.Add(_rail);
        root.Children.Add(contentBorder);
        Child = root;

        _inspector.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioInspectorViewModel.ActiveTab) or null)
            {
                ApplyActiveTab();
            }

            SyncTooltips();
        };
        page.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioPageViewModel.InspectorExpanded) or nameof(StudioPageViewModel.InspectorWidth) or null)
            {
                Width = page.InspectorWidth;
                contentBorder.IsVisible = page.InspectorExpanded;
                _collapseButton.Content = page.InspectorToggleLabel;
                ToolTip.SetTip(_collapseButton, page.InspectorToggleTooltip);
            }

            if (args.PropertyName is nameof(StudioPageViewModel.SelectedRegion) or null)
            {
                SyncTooltips();
            }
        };

        contentBorder.IsVisible = page.InspectorExpanded;
        ApplyActiveTab();
        SyncTooltips();
    }

    public Border Rail => _rail;

    public ScrollViewer Content => _content;

    public Button TabButton(StudioInspectorTab tab) => _tabButtons[tab];

    /// <summary>All five tab bodies (headless tests assert they exist and switch without rebuild).</summary>
    public IReadOnlyDictionary<StudioInspectorTab, Control> TabPanels => _tabPanels;

    public Button SaveTranslationButton => _saveTranslationButton;

    public Button ApplyTypeButton => _applyTypeButton;

    public Button RerenderButton => _rerenderButton;

    public Button RestoreRevisionButton => _restoreButton;

    public IReadOnlyList<Button> LockButtons => _lockButtons;

    public IReadOnlyList<Button> RegionTypeButtons => _typeOptionButtons;

    private static Border WithHeight(Border border, double height)
    {
        border.Height = height;
        return border;
    }

    private Button CreateTabButton(StudioInspectorTab tab, string glyph, string label)
    {
        var button = StudioUi.Button(glyph, "studio-tab ghost", () =>
        {
            _inspector.ActiveTab = tab;
            _page.InspectorExpanded = true;
        });
        ToolTip.SetTip(button, label);
        return button;
    }

    private void ApplyActiveTab()
    {
        foreach (var (tab, button) in _tabButtons)
        {
            button.Classes.Set("active", tab == _inspector.ActiveTab);
        }

        foreach (var (tab, wrapper) in _tabContentWrappers)
        {
            wrapper.IsVisible = tab == _inspector.ActiveTab;
        }

        _header.Text = _inspector.ActiveTabLabel;
    }

    private void SyncTooltips()
    {
        StudioUi.SetTooltip(_saveTranslationButton, _inspector.SaveTranslationTooltip);
        _saveTranslationButton.IsEnabled = _inspector.SaveTranslationEnabled;
        StudioUi.SetTooltip(_applyTypeButton, _inspector.ApplyRegionTypeTooltip);
        _applyTypeButton.IsEnabled = _inspector.ApplyRegionTypeEnabled;
        StudioUi.SetTooltip(_rerenderButton, _inspector.RerenderTooltip);
        _rerenderButton.IsEnabled = _inspector.RerenderEnabled;
        StudioUi.SetTooltip(_restoreButton, _inspector.RestoreTooltip);
        _restoreButton.IsEnabled = _inspector.RestoreEnabled;
    }

    // ---------------------------------------------------------------- 文本 tab

    private Control BuildTextPanel()
    {
        var panel = StudioUi.Column(8);
        panel.Margin = new Thickness(12, 8);
        panel.Children.Add(StudioUi.Text("四级文本", "studio-section-title"));
        var note = StudioUi.BoundText(nameof(StudioInspectorViewModel.TextTiersNote), "nm-meta", "nm-wrap");
        panel.Children.Add(note);

        var tiers = new ItemsControl
        {
            ItemsSource = _inspector.TextTiers,
            ItemTemplate = new FuncDataTemplate<StudioTextTierViewModel>((tier, _) => BuildTierRow(tier), true),
        };
        panel.Children.Add(tiers);

        var save = StudioUi.BoundLabelButton(
            nameof(StudioInspectorViewModel.SaveTranslationLabel),
            "studio-action",
            () => _ = SaveTranslationAsync());
        _saveTranslationButton = save;
        panel.Children.Add(save);
        panel.Children.Add(StudioUi.Text(
            "人工译文输入框：能力待接入（F0-1 save_manual_translation）· 本构建不提供可输入的假字段",
            "nm-meta",
            "nm-muted",
            "nm-wrap"));
        panel.Name = "TextPanel";
        return panel;
    }

    private static Control BuildTierRow(StudioTextTierViewModel tier)
    {
        var row = StudioUi.Column(4);
        row.Margin = new Thickness(0, 4);

        var head = StudioUi.Row(6);
        head.Children.Add(StudioUi.Text(tier.Label, "nm-label"));
        head.Children.Add(StudioUi.Text(tier.SourceHint, "nm-meta", "nm-muted"));
        var lockBadge = StudioUi.Text("▮", "nm-state-blocked", "nm-num");
        head.Children.Add(lockBadge);
        var notWired = StudioUi.Box(StudioUi.Text("能力待接入", "nm-meta"), "studio-chip");
        head.Children.Add(notWired);
        row.Children.Add(head);

        var value = new TextBlock { Classes = { "nm-body", "nm-wrap" } };
        value.Bind(TextBlock.TextProperty, new Binding(nameof(StudioTextTierViewModel.ValueDisplay)));
        var valueHost = StudioUi.Box(value, "studio-field-readonly");
        valueHost.MinHeight = 26;
        row.Children.Add(valueHost);

        void Apply()
        {
            lockBadge.IsVisible = tier.IsLocked;
            notWired.IsVisible = tier.IsNotWired;
            valueHost.Classes.Set("studio-field-readonly", true);
        }

        tier.PropertyChanged += (_, _) => Apply();
        Apply();
        return row;
    }

    // ---------------------------------------------------------------- 样式 tab

    private Control BuildStylePanel()
    {
        var panel = StudioUi.Column(8);
        panel.Margin = new Thickness(12, 8);
        panel.Name = "StylePanel";

        panel.Children.Add(StudioUi.Text("REGION", "studio-section-title"));
        panel.Children.Add(FieldRow("类型", nameof(StudioInspectorViewModel.PendingRegionType)));
        panel.Children.Add(FieldRow("来源", nameof(StudioInspectorViewModel.OriginText)));
        panel.Children.Add(FieldRow("revision", nameof(StudioInspectorViewModel.RevisionText)));
        panel.Children.Add(FieldRow("sfx 策略", nameof(StudioInspectorViewModel.SfxPolicyText)));
        panel.Children.Add(FieldRow("几何（归一化）", nameof(StudioInspectorViewModel.GeometryText), wrap: true));

        panel.Children.Add(StudioUi.Text("改类型（已接入 set_region_type）", "studio-section-title"));
        var options = StudioUi.Row(4);
        foreach (var type in _inspector.RegionTypeOptions)
        {
            var captured = type;
            var button = StudioUi.Button(type, "studio-action", () => _inspector.SetPendingRegionType(captured));
            StudioUi.TrackClass(
                button,
                "active",
                _inspector,
                () => string.Equals(_inspector.PendingRegionType, captured, StringComparison.Ordinal));
            _typeOptionButtons.Add(button);
            options.Children.Add(button);
        }

        var optionScroll = new ScrollViewer
        {
            Content = options,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
            VerticalScrollBarVisibility = ScrollBarVisibility.Disabled,
            Height = 32,
        };
        panel.Children.Add(optionScroll);

        var apply = StudioUi.Button("应用类型修改", "studio-action primary", () => _ = _page.ApplyRegionTypeAsync());
        _applyTypeButton = apply;
        panel.Children.Add(apply);

        var applyHint = StudioUi.BoundText(nameof(StudioInspectorViewModel.PendingEditSummary), "nm-meta", "nm-muted", "nm-wrap");
        panel.Children.Add(applyHint);
        panel.Children.Add(StudioUi.BoundText(nameof(StudioInspectorViewModel.FontFamilyNote), "nm-meta", "nm-muted", "nm-wrap"));

        return panel;
    }

    private static Control FieldRow(string label, string path, bool wrap = false)
    {
        var row = StudioUi.Column(2);
        row.Children.Add(StudioUi.Text(label, "nm-meta", "nm-muted"));
        var value = new TextBlock { Classes = { "nm-body" } };
        if (wrap)
        {
            value.Classes.Add("nm-wrap");
        }

        value.Bind(TextBlock.TextProperty, new Binding(path));
        row.Children.Add(StudioUi.Box(value, "studio-field-readonly"));
        return row;
    }

    // ---------------------------------------------------------------- 修复 tab

    private Control BuildRepairPanel()
    {
        var panel = StudioUi.Column(8);
        panel.Margin = new Thickness(12, 8);
        panel.Name = "RepairPanel";
        panel.Children.Add(StudioUi.Text("重渲染（已接入 rerender_page）", "studio-section-title"));
        var rerender = StudioUi.BoundLabelButton(
            nameof(StudioInspectorViewModel.RerenderLabel),
            "studio-action",
            () => _ = _page.RerenderPageAsync());
        _rerenderButton = rerender;
        panel.Children.Add(rerender);
        panel.Children.Add(StudioUi.BoundText(nameof(StudioInspectorViewModel.LastRerenderText), "nm-meta", "nm-wrap"));

        panel.Children.Add(StudioUi.Text("修复路线 / MASK", "studio-section-title"));
        panel.Children.Add(StudioUi.BoundText(nameof(StudioInspectorViewModel.RepairNote), "nm-meta", "nm-muted", "nm-wrap"));
        foreach (var label in new[] { "换 Mask · 能力待接入", "换路线 · 能力待接入", "重新修复 · 能力待接入" })
        {
            var button = StudioUi.Button(label, "studio-action");
            button.IsEnabled = false;
            ToolTip.SetTip(button, StudioCapabilityGate.NotWiredTooltip);
            panel.Children.Add(button);
        }

        return panel;
    }

    // ---------------------------------------------------------------- 锁定 tab

    private Control BuildLocksPanel()
    {
        var panel = StudioUi.Column(8);
        panel.Margin = new Thickness(12, 8);
        panel.Name = "LocksPanel";
        panel.Children.Add(StudioUi.Text("四把锁", "studio-section-title"));
        panel.Children.Add(StudioUi.BoundText(nameof(StudioInspectorViewModel.LocksNote), "nm-meta", "nm-muted", "nm-wrap"));

        var locks = new ItemsControl
        {
            ItemsSource = _inspector.Locks,
            ItemTemplate = new FuncDataTemplate<StudioLockItemViewModel>((item, _) => BuildLockRow(item), true),
        };
        panel.Children.Add(locks);
        return panel;
    }

    private Control BuildLockRow(StudioLockItemViewModel item)
    {
        var row = StudioUi.Row(6);
        row.Margin = new Thickness(0, 4);
        var glyph = StudioUi.Text(item.Glyph, "nm-num");
        row.Children.Add(glyph);
        var column = StudioUi.Column(2);
        column.Width = 200;
        column.Children.Add(StudioUi.Text(item.Label, "nm-label"));
        column.Children.Add(StudioUi.Text(item.Explanation, "nm-meta", "nm-muted", "nm-wrap"));
        row.Children.Add(column);
        var toggle = StudioUi.Button(item.IsLocked ? "已锁定" : "锁定", "studio-action");
        toggle.IsEnabled = false;
        ToolTip.SetTip(toggle, StudioCapabilityGate.NotWiredTooltip);
        _lockButtons.Add(toggle);
        row.Children.Add(toggle);
        return row;
    }

    // ---------------------------------------------------------------- 历史 tab

    private Control BuildHistoryPanel()
    {
        var panel = StudioUi.Column(8);
        panel.Margin = new Thickness(12, 8);
        panel.Name = "HistoryPanel";
        panel.Children.Add(StudioUi.Text("REVISION", "studio-section-title"));

        var loading = StudioUi.Text("正在读取 revision…", "nm-meta", "nm-muted");
        StudioUi.TrackVisible(loading, _inspector, () => _inspector.IsHistoryLoading);
        panel.Children.Add(loading);

        var empty = new TextBlock { Classes = { "nm-meta", "nm-muted" } };
        empty.Bind(TextBlock.TextProperty, new Binding(nameof(StudioInspectorViewModel.HistoryEmptyNote)));
        StudioUi.TrackVisible(empty, _inspector, () => _inspector.IsHistoryEmpty);
        panel.Children.Add(empty);

        var error = new TextBlock { Classes = { "nm-meta" } };
        error.Bind(TextBlock.TextProperty, new Binding(nameof(StudioInspectorViewModel.HistoryError)));
        StudioUi.TrackVisible(error, _inspector, () => _inspector.HasHistoryError);
        panel.Children.Add(error);

        var list = new ItemsControl
        {
            ItemsSource = _inspector.Revisions,
            ItemTemplate = new FuncDataTemplate<StudioRevisionItemViewModel>((item, _) => BuildRevisionRow(item), true),
        };
        panel.Children.Add(list);

        var preview = StudioUi.Column(4);
        preview.Children.Add(StudioUi.Text("预览（元数据）", "studio-section-title"));
        preview.Children.Add(StudioUi.BoundText(nameof(StudioInspectorViewModel.PreviewTitle), "nm-label"));
        preview.Children.Add(StudioUi.BoundText(nameof(StudioInspectorViewModel.PreviewDetail), "nm-meta", "nm-muted", "nm-wrap"));
        panel.Children.Add(preview);

        var restore = StudioUi.BoundLabelButton(
            nameof(StudioInspectorViewModel.RestoreLabel),
            "studio-action",
            () => _ = RestoreSelectedRevisionAsync());
        _restoreButton = restore;
        panel.Children.Add(restore);
        panel.Children.Add(StudioUi.Text(
            "恢复会生成一个新的 revision，历史版本不会被覆盖（Core restore_region_revision 语义）",
            "nm-meta",
            "nm-muted",
            "nm-wrap"));
        return panel;
    }

    private Control BuildRevisionRow(StudioRevisionItemViewModel item)
    {
        var row = StudioUi.Row(6);
        row.Children.Add(StudioUi.Text(item.RevisionLabel, "nm-num"));
        row.Children.Add(StudioUi.Text(item.OriginLabel, "nm-meta"));
        var glyph = StudioUi.Text(item.StateGlyph, "nm-num");
        glyph.Classes.Add(item.StateClass);
        row.Children.Add(glyph);
        row.Children.Add(StudioUi.Text(item.StateLabel, "nm-meta", "nm-muted"));
        var current = StudioUi.Box(StudioUi.Text("当前", "nm-meta"), "studio-chip-accent");
        current.IsVisible = item.IsCurrent;
        row.Children.Add(current);
        var pinned = StudioUi.Text("▮", "nm-state-blocked", "nm-num");
        pinned.IsVisible = item.IsPinned;
        row.Children.Add(pinned);

        var host = StudioUi.Box(row, "studio-revision-row");
        host.PointerPressed += (_, args) =>
        {
            _inspector.SelectedRevision = item;
            args.Handled = true;
        };
        StudioUi.TrackClass(host, "selected", _inspector, () => ReferenceEquals(_inspector.SelectedRevision, item));
        return host;
    }

    private async Task SaveTranslationAsync()
    {
        // The save path is NOT_WIRED in this build: the module never writes anything, it only reports
        // the degradation through the same status channel as the wired actions.
        await Task.Yield();
        _inspector.ReportAction(StudioCapabilityGate.NotWiredTooltip);
    }

    private async Task RestoreSelectedRevisionAsync()
    {
        if (_inspector.SelectedRevision is { } revision)
        {
            await _page.RestoreRevisionAsync(revision.RevisionNo);
        }
    }
}
