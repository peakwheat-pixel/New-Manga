using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Controls.Templates;
using Avalonia.Data;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-4 <c>StatusMatrix</c>: rows = pages, columns = the projection's own <c>step_flow</c>
/// (dynamic; never a hard-coded ten), cells 18×18 with the frozen seven-state glyph. Supports single
/// click, Shift/drag box selection (shared with CountChips filtering and Page mode scope), double-click
/// / Enter drill-down. Missing projection data renders "no projection data", never a guessed state.
/// </summary>
public sealed class StudioBatchMatrixControl : Border
{
    private const double CellSize = 18;
    private const double PageColumnWidth = 62;
    private const double HeaderHeight = 30;

    private readonly StudioBatchViewModel _viewModel;
    private readonly StackPanel _header;
    private readonly StackPanel _rowsHost;
    private readonly ScrollViewer _scroll;
    private readonly List<Control> _cellControls = new();
    private readonly List<Control> _rowControls = new();
    private StudioBatchCellViewModel? _dragAnchor;
    private readonly List<string> _rowIds = new();
    private readonly List<TextBlock> _pageLabels = new();
    private readonly List<Border> _rowHosts = new();
    private bool _dragging;

    public StudioBatchMatrixControl(StudioBatchViewModel viewModel)
    {
        _viewModel = viewModel;
        Classes.Add("sunken");
        ClipToBounds = true;
        Focusable = true;

        _header = new StackPanel { Orientation = Orientation.Horizontal, Height = HeaderHeight };
        _rowsHost = new StackPanel { Orientation = Orientation.Vertical, Spacing = 1 };
        _scroll = new ScrollViewer
        {
            Content = _rowsHost,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
        };

        var body = new Grid { RowDefinitions = new RowDefinitions("Auto,*") };
        Grid.SetRow(_header, 0);
        Grid.SetRow(_scroll, 1);
        body.Children.Add(_header);
        body.Children.Add(_scroll);
        Child = body;

        _viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioBatchViewModel.State) or nameof(StudioBatchViewModel.Projection) or null)
            {
                Rebuild();
            }
        };
        _viewModel.Rows.CollectionChanged += (_, _) => Rebuild();
        Rebuild();
        KeyDown += (_, args) =>
        {
            if (args.Key == Key.Enter)
            {
                DrillFocused();
                args.Handled = true;
            }
        };
    }

    /// <summary>All rendered cell controls (headless control-tree assertions).</summary>
    public IReadOnlyList<Control> CellControls => _cellControls;

    public StackPanel HeaderPanel => _header;

    public ScrollViewer Scroll => _scroll;

    public int ColumnCount => _viewModel.StageColumnCount;

    public Control? CellAt(int row, int column)
    {
        var index = row * _viewModel.StageColumnCount + column;
        return index >= 0 && index < _cellControls.Count ? _cellControls[index] : null;
    }

    public void Rebuild()
    {
        _header.Children.Clear();
        _rowsHost.Children.Clear();
        _cellControls.Clear();
        _rowControls.Clear();

        var pageHeader = new TextBlock { Text = "页", Classes = { "meta" }, Width = PageColumnWidth };
        _header.Children.Add(new Border { Child = pageHeader, Padding = new Thickness(6, 0) });
        foreach (var stage in _viewModel.StageColumns)
        {
            var glyph = new TextBlock
            {
                Text = string.IsNullOrEmpty(stage.Label) ? stage.CoreStepType : stage.Label,
                Classes = { "meta" },
                FontSize = 11,
                TextAlignment = TextAlignment.Center,
            };
            ToolTip.SetTip(glyph, stage.Label);
            _header.Children.Add(new Border
            {
                Child = glyph,
                Width = CellSize,
                Height = HeaderHeight,
                Margin = new Thickness(1, 0),
            });
        }

        foreach (var row in _viewModel.Rows)
        {
            var rowPanel = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 1, Height = 22 };
            var pageLabel = new TextBlock
            {
                Text = $"{row.NumberLabel} {row.StateGlyph}",
                Classes = { "data" },
                Width = PageColumnWidth,
                VerticalAlignment = VerticalAlignment.Center,
            };
            ToolTip.SetTip(pageLabel, row.Tooltip);
            var pageButton = StudioUi.Button(string.Empty, "studio-matrix-page", () => _viewModel.SelectRow(row.Index));
            pageButton.Content = pageLabel;
            _pageLabels.Add(pageLabel);
            pageButton.Width = PageColumnWidth;
            pageButton.HorizontalContentAlignment = HorizontalAlignment.Left;
            rowPanel.Children.Add(pageButton);
            _rowControls.Add(pageButton);

            foreach (var cell in row.Cells)
            {
                var cellBorder = new Border
                {
                    Width = CellSize,
                    Height = CellSize,
                    Margin = new Thickness(1, 0),
                };
                cellBorder.Classes.Add("studio-cell");
                var glyph = new TextBlock
                {
                    Text = cell.Glyph,
                    FontSize = 11,
                    HorizontalAlignment = HorizontalAlignment.Center,
                    VerticalAlignment = VerticalAlignment.Center,
                };
                cellBorder.Child = glyph;
                ToolTip.SetTip(cellBorder, cell.Tooltip);
                ApplyCellState(cellBorder, glyph, cell);

                var captured = cell;
                var capturedRow = row;
                cellBorder.PointerPressed += (_, args) =>
                {
                    if (args.GetCurrentPoint(cellBorder).Properties.IsLeftButtonPressed)
                    {
                        _dragAnchor = captured;
                        _dragging = true;
                        cellBorder.Focus();
                        _viewModel.SelectCell(capturedRow.Index, captured.StageType, extend: (args.KeyModifiers & KeyModifiers.Shift) != 0);
                        args.Handled = true;
                    }
                };
                cellBorder.PointerEntered += (_, _) =>
                {
                    if (_dragging && _dragAnchor is { } anchor)
                    {
                        _viewModel.SelectBox(anchor.RowIndex, anchor.StageType, capturedRow.Index, captured.StageType);
                    }
                };
                cellBorder.PointerReleased += (_, args) =>
                {
                    _dragging = false;
                    _dragAnchor = null;
                    args.Handled = true;
                };
                cellBorder.DoubleTapped += (_, args) =>
                {
                    _viewModel.SelectCell(capturedRow.Index, captured.StageType);
                    _viewModel.RequestDrillToPage(capturedRow.Index);
                    args.Handled = true;
                };
                cell.PropertyChanged += (_, _) => ApplyCellState(cellBorder, glyph, cell);
                rowPanel.Children.Add(cellBorder);
                _cellControls.Add(cellBorder);
            }

            var rowHost = new Border { Child = rowPanel, Classes = { "studio-matrix-row" } };
            StudioUi.TrackClass(rowHost, "selected", row, () => row.IsSelected);
            StudioUi.TrackClass(rowHost, "dimmed", row, () => row.IsDimmed);
            StudioUi.TrackClass(rowHost, "highlighted", row, () => row.IsHighlighted);
            _rowsHost.Children.Add(rowHost);
            _rowControls.Add(rowHost);
        }
    }

    private static void ApplyCellState(Border border, TextBlock glyph, StudioBatchCellViewModel cell)
    {
        border.Classes.Set("selected", cell.IsSelected);
        border.Classes.Set("dimmed", cell.IsDimmed);
        border.Classes.Set("highlighted", cell.IsHighlighted);
        foreach (var state in Enum.GetValues<StudioStateKind>())
        {
            border.Classes.Set(StudioBatchCellViewModel.StateFillClass(state), cell.State == state);
        }

        border.Classes.Set("studio-fill-nodata", cell.State is null);
        glyph.Text = cell.Glyph;
        foreach (var state in Enum.GetValues<StudioStateKind>())
        {
            glyph.Classes.Set(StudioStates.StyleClass(state), cell.State == state);
        }

        glyph.Classes.Set("studio-state-nodata", cell.State is null);
        ToolTip.SetTip(border, cell.Tooltip);
    }

    /// <summary>Keyboard Enter on the focused cell drills into Page mode (SCREEN_SPECS §4).</summary>
    public void DrillFocused()
    {
        if (_viewModel.SelectingAnchor is { } anchor)
        {
            _viewModel.RequestDrillToPage(anchor.RowIndex);
        }
    }
}

/// <summary>Top StageRail: per-projection-stage completion, exception count and the gate warning.</summary>
public sealed class StudioBatchStageRailControl : Border
{
    private readonly StudioBatchViewModel _viewModel;
    private readonly StackPanel _rail;
    private readonly TextBlock _gate;

    public StudioBatchStageRailControl(StudioBatchViewModel viewModel)
    {
        _viewModel = viewModel;
        Classes.Add("studio-stage-rail");
        Height = 40;
        _rail = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 2 };
        _gate = new TextBlock { Classes = { "meta" }, VerticalAlignment = VerticalAlignment.Center, Margin = new Thickness(12, 0) };
        var row = new StackPanel { Orientation = Orientation.Horizontal, VerticalAlignment = VerticalAlignment.Center };
        row.Children.Add(_rail);
        row.Children.Add(_gate);
        Child = row;
        viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioBatchViewModel.Projection) or nameof(StudioBatchViewModel.HighlightedStage) or null)
            {
                Rebuild();
            }
        };
        Rebuild();
    }

    public IReadOnlyList<Button> StageButtons => _rail.Children.OfType<Button>().ToList();

    public void Rebuild()
    {
        _rail.Children.Clear();
        foreach (var item in _viewModel.StageRail)
        {
            var column = StudioUi.Column(0);
            var head = StudioUi.Row(4);
            var glyph = StudioUi.Text(item.GateGlyph, "meta");
            glyph.Classes.Add(item.GateClass);
            head.Children.Add(glyph);
            head.Children.Add(StudioUi.Text(item.Label, "label"));
            head.Children.Add(StudioUi.Text(item.RatioText, "data", "muted"));
            if (item.Failed > 0)
            {
                var failed = StudioUi.Text($"✗{item.Failed}", "meta");
                failed.Classes.Add("studio-state-failed");
                head.Children.Add(failed);
            }

            column.Children.Add(head);
            var captured = item;
            var button = StudioUi.Button(string.Empty, "studio-stage-tab", () => _viewModel.HighlightStage(captured.StageType));
            button.Content = column;
            StudioUi.TrackClass(button, "active", item, () => item.IsActive);
            ToolTip.SetTip(button, item.Tooltip);
            _rail.Children.Add(button);
        }

        _gate.Text = _viewModel.GateWarning;
        _gate.Classes.Set("studio-state-failed", _viewModel.HasGateWarning);
        _gate.Classes.Set("studio-state-done", !_viewModel.HasGateWarning);
        _gate.IsVisible = _viewModel.HasGateWarning;
    }
}

/// <summary>CountChips: 总/完成/失败/过期/待确认/阻塞 — click filters the matrix, never reflows it.</summary>
public sealed class StudioBatchCountChipsControl : StackPanel
{
    private readonly StudioBatchViewModel _viewModel;

    public StudioBatchCountChipsControl(StudioBatchViewModel viewModel)
    {
        _viewModel = viewModel;
        Orientation = Orientation.Horizontal;
        Spacing = 6;
        VerticalAlignment = VerticalAlignment.Center;
        Margin = new Thickness(8, 0);
        viewModel.Chips.CollectionChanged += (_, _) => Rebuild();
        viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioBatchViewModel.FilterText) or null)
            {
                foreach (var chip in viewModel.Chips)
                {
                    chip.IsActive = chip.Filter == viewModel.ActiveFilter;
                }
            }
        };
        Rebuild();
    }

    public IReadOnlyList<Button> ChipButtons => Children.OfType<Button>().ToList();

    public void Rebuild()
    {
        Children.Clear();
        foreach (var chip in _viewModel.Chips)
        {
            var captured = chip;
            var button = StudioUi.Button(string.Empty, "studio-count-chip", () => _viewModel.SetFilter(captured.Filter));
            var row = StudioUi.Row(4);
            row.Children.Add(StudioUi.Text(chip.Label, "meta"));
            row.Children.Add(StudioUi.Text(chip.CountText, "data"));
            button.Content = row;
            StudioUi.TrackClass(button, "active", chip, () => chip.IsActive);
            ToolTip.SetTip(button, chip.Tooltip);
            Children.Add(button);
        }
    }
}

/// <summary>Bottom RunStrip (24px): run summary + Core-projected control availability.</summary>
public sealed class StudioBatchRunStripControl : Border
{
    private readonly StudioBatchViewModel _viewModel;
    private readonly Button _pause;
    private readonly Button _resume;
    private readonly Button _stop;
    private readonly Button _retry;
    private readonly Button _resumeBlocked;
    private readonly TextBlock _line;
    private readonly TextBlock _status;

    public StudioBatchRunStripControl(StudioBatchViewModel viewModel)
    {
        _viewModel = viewModel;
        Classes.Add("studio-run-strip");
        Height = 24;

        _line = new TextBlock { Classes = { "data" } };
        _line.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.ProgressText)) { Source = viewModel });
        _status = new TextBlock { Classes = { "meta" }, Margin = new Thickness(12, 0) };
        _status.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.StatusText)) { Source = viewModel });
        var runId = new TextBlock { Classes = { "data", "muted" }, Margin = new Thickness(8, 0) };
        runId.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.RunIdText)) { Source = viewModel });

        _pause = StudioUi.Button("暂停", "ghost sm", () => _ = viewModel.PauseAsync());
        _resume = StudioUi.Button("继续", "ghost sm", () => _ = viewModel.ResumeAsync());
        _stop = StudioUi.Button("停止", "ghost sm", () => _ = viewModel.StopAsync());
        _retry = StudioUi.Button("重试失败", "ghost sm", () => _ = viewModel.RetryFailedAsync());
        _resumeBlocked = StudioUi.Button("恢复阻塞", "ghost sm", () => _ = viewModel.ResumeBlockedAsync());
        var controls = StudioUi.Row(4);
        controls.Children.Add(_pause);
        controls.Children.Add(_resume);
        controls.Children.Add(_stop);
        controls.Children.Add(_retry);
        controls.Children.Add(_resumeBlocked);

        var row = StudioUi.Row(8);
        row.Children.Add(StudioUi.Text("RUN", "meta"));
        row.Children.Add(runId);
        row.Children.Add(_line);
        row.Children.Add(_status);
        row.Children.Add(new Panel { Width = 8 });
        row.Children.Add(controls);
        Child = row;
        viewModel.PropertyChanged += (_, _) => RefreshEnablement();
        RefreshEnablement();
    }

    public Button PauseButton => _pause;

    public Button ResumeButton => _resume;

    public Button StopButton => _stop;

    public Button RetryButton => _retry;

    public Button ResumeBlockedButton => _resumeBlocked;

    private void RefreshEnablement()
    {
        _pause.IsEnabled = _viewModel.CanPause;
        _resume.IsEnabled = _viewModel.CanContinue;
        _stop.IsEnabled = _viewModel.CanStop;
        _retry.IsEnabled = _viewModel.CanRetryFailed;
        _resumeBlocked.IsEnabled = _viewModel.CanResumeBlocked;
    }
}

/// <summary>Right-hand 360px detail drawer: the selected matrix cell/row facts + steps.</summary>
public sealed class StudioBatchDrawerControl : Border
{
    private readonly StudioBatchViewModel _viewModel;
    private readonly TextBlock _title;
    private readonly TextBlock _detail;
    private readonly ItemsControl _steps;

    public StudioBatchDrawerControl(StudioBatchViewModel viewModel)
    {
        _viewModel = viewModel;
        Classes.Add("studio-drawer");
        Width = 360;
        HorizontalAlignment = HorizontalAlignment.Right;
        VerticalAlignment = VerticalAlignment.Stretch;

        _title = new TextBlock { Classes = { "title" } };
        _title.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.DrawerTitle)) { Source = viewModel });
        _detail = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _detail.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.DrawerDetail)) { Source = viewModel });

        _steps = new ItemsControl
        {
            ItemTemplate = new FuncDataTemplate<StudioRunStepState>((step, _) =>
            {
                var glyph = StudioUi.Text(step.State is { } state ? StudioStates.Glyph(state) : "–", "data");
                glyph.Classes.Add(step.State is { } token ? StudioStates.StyleClass(token) : "studio-state-nodata");
                var row = StudioUi.Row(6);
                row.Children.Add(glyph);
                row.Children.Add(StudioUi.Text(step.StepType, "label"));
                row.Children.Add(StudioUi.Text(step.State is { } value ? StudioStates.Label(value) : "无投影数据", "meta", "muted"));
                row.Children.Add(StudioUi.Text(step.ErrorCode ?? string.Empty, "meta"));
                return row;
            }, false),
        };

        var close = StudioUi.Button("关闭", "ghost sm", () => viewModel.CloseDrawer());
        var header = StudioUi.Row(8);
        header.Children.Add(_title);
        header.Children.Add(new Panel { Width = 1 });
        header.Children.Add(close);

        var column = StudioUi.Column(8);
        column.Margin = new Thickness(12, 8);
        column.Children.Add(header);
        column.Children.Add(_detail);
        column.Children.Add(StudioUi.Text("STEPS", "studio-section-title"));
        column.Children.Add(_steps);
        Child = column;

        StudioUi.TrackVisible(this, viewModel, () => viewModel.IsDrawerOpen);
        viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioBatchViewModel.DrawerRow) or nameof(StudioBatchViewModel.IsDrawerOpen) or null)
            {
                _steps.ItemsSource = viewModel.DrawerRow?.Row.Steps;
            }
        };
    }

    public ItemsControl StepsList => _steps;

    public TextBlock Title => _title;
}

/// <summary>Gate confirmation modal: an uncleared gate must show its impact before anything runs.</summary>
public sealed class StudioBatchGateModalControl : Grid
{
    private readonly StudioBatchViewModel _viewModel;
    private readonly TextBlock _impact;

    public StudioBatchGateModalControl(StudioBatchViewModel viewModel)
    {
        _viewModel = viewModel;
        var scrim = StudioUi.Box("studio-scrim");
        Children.Add(scrim);

        var card = StudioUi.Box("studio-modal-card");
        card.HorizontalAlignment = HorizontalAlignment.Center;
        card.VerticalAlignment = VerticalAlignment.Center;
        var column = StudioUi.Column(12);
        column.Children.Add(StudioUi.Text("门禁未清 · 确认影响面", "title"));
        _impact = new TextBlock { Classes = { "body", "studio-wrap" } };
        _impact.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.GateImpactText)) { Source = viewModel });
        column.Children.Add(_impact);
        var actions = StudioUi.Row(8);
        actions.HorizontalAlignment = HorizontalAlignment.Right;
        var cancel = StudioUi.Button("取消", "sm", () => viewModel.CancelGate());
        var confirm = StudioUi.Button("仍然执行", "sm danger", () => _ = viewModel.ConfirmGateAsync());
        actions.Children.Add(cancel);
        actions.Children.Add(confirm);
        column.Children.Add(actions);
        card.Child = column;
        Children.Add(card);
        StudioUi.TrackVisible(this, viewModel, () => viewModel.IsGateConfirmOpen);
    }

    public TextBlock ImpactText => _impact;
}

/// <summary>
/// V11R-B-4 Studio · Batch workspace: StageRail + CountChips + StatusMatrix + Drawer + batch action bar
/// + RunStrip, the empty/NOT_WIRED state, the gate modal and the injectable projection poll.
/// </summary>
public sealed class StudioBatchWorkspace : Grid
{
    private readonly StudioBatchViewModel _viewModel;
    private readonly DispatcherTimer? _timer;
    private Border _emptyHost = null!;
    private TextBlock _emptyTitle = null!;
    private TextBlock _emptyDetail = null!;
    private Button _startButton = null!;
    private Border _actionBar = null!;
    private TextBlock _actionHeader = null!;
    private readonly List<Button> _actionButtons = new();
    private StackPanel _scopeButtons = null!;

    public StudioBatchWorkspace(StudioBatchViewModel viewModel)
    {
        _viewModel = viewModel;
        RowDefinitions = new RowDefinitions("Auto,Auto,*,Auto,Auto");

        var rail = new StudioBatchStageRailControl(viewModel);
        var chips = new StudioBatchCountChipsControl(viewModel);
        var matrixHost = new Grid();
        Matrix = new StudioBatchMatrixControl(viewModel);
        Drawer = new StudioBatchDrawerControl(viewModel);
        GateModal = new StudioBatchGateModalControl(viewModel);
        matrixHost.Children.Add(Matrix);
        matrixHost.Children.Add(Drawer);
        BuildEmptyState();
        matrixHost.Children.Add(_emptyHost);
        matrixHost.Children.Add(GateModal);

        Chips = chips;
        StageRail = rail;
        _scopeButtons = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 4, VerticalAlignment = VerticalAlignment.Center };
        BuildScopeButtons(_scopeButtons);
        var chipRow = new StackPanel { Orientation = Orientation.Horizontal, VerticalAlignment = VerticalAlignment.Center };
        chipRow.Children.Add(chips);
        chipRow.Children.Add(_scopeButtons);
        chipRow.Children.Add(new Panel { Width = 12 });
        chipRow.Children.Add(BuildLegend());
        _actionHeader = new TextBlock { Classes = { "meta" } };
        _actionHeader.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.ActionBarHeader)) { Source = viewModel });
        _actionBar = StudioUi.Box("studio-action-bar");
        _actionBar.Height = 40;
        BuildActionBar();
        var runStrip = new StudioBatchRunStripControl(viewModel);
        RunStrip = runStrip;

        Grid.SetRow(rail, 0);
        Grid.SetRow(chipRow, 1);
        Grid.SetRow(matrixHost, 2);
        Grid.SetRow(_actionBar, 3);
        Grid.SetRow(runStrip, 4);
        Children.Add(rail);
        Children.Add(chipRow);
        Children.Add(matrixHost);
        Children.Add(_actionBar);
        Children.Add(runStrip);

        viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioBatchViewModel.State) or nameof(StudioBatchViewModel.HasSelection) or null)
            {
                RefreshChrome();
            }
        };
        RefreshChrome();

        // Polling: 500–1000 ms by injection; only while Batch is the active workspace.
        _timer = new DispatcherTimer { Interval = viewModel.PollInterval };
        _timer.Tick += (_, _) => _ = viewModel.TickAsync();
        AttachedToVisualTree += (_, _) =>
        {
            if (viewModel.IsWired)
            {
                viewModel.StartPolling();
                _timer.Start();
                _ = viewModel.RefreshAsync();
            }
        };
        DetachedFromVisualTree += (_, _) =>
        {
            viewModel.StopPolling();
            _timer.Stop();
        };
    }

    public StudioBatchMatrixControl Matrix { get; }

    public StudioBatchDrawerControl Drawer { get; }

    public StudioBatchGateModalControl GateModal { get; }

    public StudioBatchStageRailControl StageRail { get; }

    public StudioBatchCountChipsControl Chips { get; }

    public StudioBatchRunStripControl RunStrip { get; }

    public Border EmptyStateHost => _emptyHost;

    public Button StartButton => _startButton;

    public Border ActionBar => _actionBar;

    public TextBlock ActionHeader => _actionHeader;

    public IReadOnlyList<Button> ActionButtons => _actionButtons;

    public StackPanel ScopeButtons => _scopeButtons;

    /// <summary>Always-on seven-state legend row.</summary>
    public StackPanel? Legend { get; private set; }

    /// <summary>Test hook: run one projection read without waiting for the timer.</summary>
    public Task<bool> RefreshNowAsync(CancellationToken cancellationToken = default) =>
        _viewModel.RefreshAsync(cancellationToken);

    private void BuildEmptyState()
    {
        _emptyHost = StudioUi.Box("sunken");
        var card = StudioUi.Box("raised");
        card.Width = 560;
        card.HorizontalAlignment = HorizontalAlignment.Center;
        card.VerticalAlignment = VerticalAlignment.Center;
        var column = StudioUi.Column(12);
        _emptyTitle = new TextBlock { Classes = { "title" } };
        _emptyTitle.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchViewModel.HeaderLine)) { Source = _viewModel });
        _emptyDetail = new TextBlock { Classes = { "meta", "studio-wrap" } };
        column.Children.Add(_emptyTitle);
        column.Children.Add(_emptyDetail);
        _startButton = StudioUi.Button("开始处理", "primary", () => _ = _viewModel.StartProcessingAsync());
        var startRow = StudioUi.Row(8);
        startRow.Children.Add(_startButton);
        column.Children.Add(startRow);
        card.Child = column;
        _emptyHost.Child = card;
    }

    /// <summary>Always-on legend (SCREEN_SPECS §4: 图例常驻) — symbol + label per seven state.</summary>
    private Control BuildLegend()
    {
        var row = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 6, VerticalAlignment = VerticalAlignment.Center };
        foreach (var state in StudioStates.LegendOrder)
        {
            var glyph = StudioUi.Text(StudioStates.Glyph(state), "meta");
            glyph.Classes.Add(StudioStates.StyleClass(state));
            var item = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 2 };
            item.Children.Add(glyph);
            item.Children.Add(StudioUi.Text(StudioStates.Label(state), "meta", "muted"));
            row.Children.Add(item);
        }

        row.Classes.Add("studio-legend");
        Legend = row;
        return row;
    }

    private void BuildActionBar()
    {
        var row = StudioUi.Row(8);
        row.Margin = new Thickness(8, 0);
        row.Children.Add(_actionHeader);
        foreach (var action in _viewModel.Actions)
        {
            var captured = action;
            var button = StudioUi.Button(string.Empty, "sm");
            var label = new TextBlock { Classes = { "label" } };
            label.Bind(TextBlock.TextProperty, new Binding(nameof(StudioBatchActionViewModel.FullLabel)) { Source = captured });
            button.Content = label;
            button.Bind(IsEnabledProperty, new Binding(nameof(StudioBatchActionViewModel.IsEnabled)) { Source = captured });
            ToolTip.SetTip(button, captured.Tooltip);
            button.Click += (_, _) => _ = _viewModel.ExecuteActionAsync(captured);
            action.PropertyChanged += (_, _) => ToolTip.SetTip(button, captured.Tooltip);
            _actionButtons.Add(button);
            row.Children.Add(button);
        }

        _actionBar.Child = row;
    }

    private void BuildScopeButtons(StackPanel host)
    {
        var chips = new List<(StudioBatchScope Scope, string Label)>
        {
            (StudioBatchScope.All, "全部"),
            (StudioBatchScope.Selected, "选中"),
            (StudioBatchScope.CurrentPage, "当前页"),
        };
        foreach (var (scope, label) in chips)
        {
            var captured = scope;
            var button = StudioUi.Button(label, "studio-scope-chip", () => _viewModel.SetScope(captured));
            StudioUi.TrackClass(button, "active", _viewModel, () => _viewModel.Scope == captured);
            _scopeButtons.Children.Add(button);
        }
    }

    private void RefreshChrome()
    {
        var hasData = _viewModel.HasData;
        _emptyHost.IsVisible = !hasData;
        _emptyDetail.Text = _viewModel.State switch
        {
            StudioBatchRunState.NotWired => "本构建没有可用的 IRunController 数据源；不会伪造矩阵或进度。",
            StudioBatchRunState.Error => _viewModel.ErrorText ?? "任务投影读取失败；可重试。",
            _ => "在 Library 选择章节后开始处理，或从 Page 模式进入 Batch。矩阵行=页、列=投影阶段。",
        };
        _startButton.IsEnabled = _viewModel.IsWired;
        ToolTip.SetTip(_startButton, _viewModel.IsWired ? "开始处理（翻译全部）" : StudioCapabilityGate.NotWiredTooltip);
        _actionBar.IsVisible = _viewModel.HasSelection && hasData;
        _scopeButtons.IsVisible = hasData;
    }


}