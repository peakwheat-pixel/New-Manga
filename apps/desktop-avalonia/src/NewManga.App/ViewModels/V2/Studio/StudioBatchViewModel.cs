using System.Collections.ObjectModel;
using NewManga.App.Services;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>Batch overview chip filters (CountChips): 总/完成/失败/过期/待确认/阻塞.</summary>
public enum StudioBatchFilter
{
    All,
    Completed,
    Failed,
    Stale,
    NeedsReview,
    Blocked,
}

/// <summary>Batch action scope; the suffix is always rendered next to the action (§2.3).</summary>
public enum StudioBatchScope
{
    All,
    Selected,
    CurrentPage,
}

/// <summary>The four batch action families of SCREEN_SPECS §4.</summary>
public enum StudioBatchActionKind
{
    Translate,
    Reocr,
    Reinpaint,
    Rerender,
}

/// <summary>Batch data lifecycle; <see cref="NotWired"/> is reserved for a missing IRunController.</summary>
public enum StudioBatchRunState
{
    NotWired,
    NoRun,
    Loading,
    Ready,
    Error,
    Partial,
}

/// <summary>One matrix cell (page × stage) — the smallest selectable unit.</summary>
public sealed class StudioBatchCellViewModel : StudioObservable
{
    private bool _isSelected;
    private bool _isDimmed;
    private bool _isHighlighted;

    public StudioBatchCellViewModel(int rowIndex, string stageType, string stageLabel, StudioStateKind? state, string? errorCode)
    {
        RowIndex = rowIndex;
        StageType = stageType;
        StageLabel = stageLabel;
        State = state;
        ErrorCode = errorCode;
    }

    public int RowIndex { get; }

    public string StageType { get; }

    public string StageLabel { get; }

    /// <summary>Null = the projection carries no such step (rendered as "no projection data").</summary>
    public StudioStateKind? State { get; }

    public string? ErrorCode { get; }

    public string Glyph => State is { } value ? StudioStates.Glyph(value) : "–";

    public string StateLabel => State is { } value ? StudioStates.Label(value) : "无投影数据";

    public string StateClass => State is { } value ? StudioStates.StyleClass(value) : "studio-state-nodata";

    public string FillClass => State is { } value ? StateFillClass(value) : "studio-fill-nodata";

    public string Tooltip => $"{StageLabel} · {StateLabel}{(ErrorCode is null ? string.Empty : $" · {ErrorCode}")}";

    public bool IsSelected
    {
        get => _isSelected;
        internal set => Set(ref _isSelected, value);
    }

    public bool IsDimmed
    {
        get => _isDimmed;
        internal set => Set(ref _isDimmed, value);
    }

    public bool IsHighlighted
    {
        get => _isHighlighted;
        internal set => Set(ref _isHighlighted, value);
    }

    internal static string StateFillClass(StudioStateKind state) => state switch
    {
        StudioStateKind.Queued => "studio-fill-queued",
        StudioStateKind.Running => "studio-fill-running",
        StudioStateKind.Done => "studio-fill-done",
        StudioStateKind.Failed => "studio-fill-failed",
        StudioStateKind.Blocked => "studio-fill-blocked",
        StudioStateKind.Stale => "studio-fill-stale",
        StudioStateKind.Skipped => "studio-fill-skipped",
        StudioStateKind.NotStarted => "studio-fill-notstarted",
        _ => "studio-fill-nodata",
    };
}

/// <summary>One matrix row (a page) with its cells in projection column order.</summary>
public sealed class StudioBatchRowViewModel : StudioObservable
{
    private bool _isSelected;
    private bool _isDimmed;
    private bool _isHighlighted;

    public StudioBatchRowViewModel(int index, StudioRunPageRow row, IReadOnlyList<StudioBatchCellViewModel> cells)
    {
        Index = index;
        Row = row;
        Cells = cells;
    }

    public int Index { get; }

    public StudioRunPageRow Row { get; }

    public string PageId => Row.PageId;

    public string NumberLabel => (Row.PageOrder > 0 ? Row.PageOrder : Index + 1).ToString("000");

    public string? Filename => Row.Filename;

    public StudioStateKind? State => Row.State;

    public string StateGlyph => State is { } value ? StudioStates.Glyph(value) : "–";

    public string StateClass => State is { } value ? StudioStates.StyleClass(value) : "studio-state-nodata";

    public string StateLabel => State is { } value ? StudioStates.Label(value) : "无投影数据";

    public bool IsLocked => Row.IsLocked;

    public bool IsPipelineCurrent => Row.IsPipelineCurrent;

    public string? ErrorCode => Row.ErrorCode;

    public IReadOnlyList<StudioBatchCellViewModel> Cells { get; }

    public string Tooltip => $"页 {NumberLabel} · {StateLabel}{(ErrorCode is null ? string.Empty : $" · {ErrorCode}")}";

    public bool IsSelected
    {
        get => _isSelected;
        internal set => Set(ref _isSelected, value);
    }

    public bool IsDimmed
    {
        get => _isDimmed;
        internal set => Set(ref _isDimmed, value);
    }

    public bool IsHighlighted
    {
        get => _isHighlighted;
        internal set => Set(ref _isHighlighted, value);
    }
}

/// <summary>One StageRail segment: completion + exception count + gate state.</summary>
public sealed class StudioBatchStageRailItemViewModel : StudioObservable
{
    private bool _isActive;

    public StudioBatchStageRailItemViewModel(string stageType, string label, int completed, int total, int failed)
    {
        StageType = stageType;
        Label = label;
        Completed = completed;
        Total = total;
        Failed = failed;
    }

    public string StageType { get; }

    public string Label { get; }

    public int Completed { get; }

    public int Total { get; }

    public int Failed { get; }

    public double Ratio => Total <= 0 ? 0 : (double)Completed / Total;

    public string RatioText => $"{Math.Round(Ratio * 100):0}%";

    public StudioStateKind GateState =>
        Failed > 0 ? StudioStateKind.Failed : Ratio >= 1 ? StudioStateKind.Done : StudioStateKind.Running;

    public string GateGlyph => StudioStates.Glyph(GateState);

    public string GateClass => StudioStates.StyleClass(GateState);

    public bool IsActive
    {
        get => _isActive;
        internal set => Set(ref _isActive, value);
    }

    public string Tooltip => $"{Label} · 完成 {Completed}/{Total} · 异常 {Failed}";
}

/// <summary>One overview chip.</summary>
public sealed class StudioBatchCountChipViewModel : StudioObservable
{
    private bool _isActive;

    public StudioBatchCountChipViewModel(StudioBatchFilter filter, string label, int? count, string tooltip)
    {
        Filter = filter;
        Label = label;
        Count = count;
        Tooltip = tooltip;
    }

    public StudioBatchFilter Filter { get; }

    public string Label { get; }

    /// <summary>Null = the projection does not carry this metric (rendered "—", never a fake 0).</summary>
    public int? Count { get; }

    public string CountText => Count is { } value ? value.ToString() : "—";

    public bool IsAvailable => Count is not null;

    public string Tooltip { get; }

    public bool IsActive
    {
        get => _isActive;
        internal set => Set(ref _isActive, value);
    }
}

/// <summary>One batch action (family × scope) with its always-visible scope suffix.</summary>
public sealed class StudioBatchActionViewModel : StudioObservable
{
    private bool _isEnabled;
    private string _scopeSuffix = string.Empty;
    private string _tooltip = string.Empty;

    public StudioBatchActionViewModel(StudioBatchActionKind kind, string label)
    {
        Kind = kind;
        Label = label;
    }

    public StudioBatchActionKind Kind { get; }

    public string Label { get; }

    public string ScopeSuffix
    {
        get => _scopeSuffix;
        internal set
        {
            if (Set(ref _scopeSuffix, value))
            {
                Raise(nameof(FullLabel));
            }
        }
    }

    public string FullLabel => $"{Label}{ScopeSuffix}";

    public bool IsEnabled
    {
        get => _isEnabled;
        internal set => Set(ref _isEnabled, value);
    }

    public string Tooltip
    {
        get => _tooltip;
        internal set => Set(ref _tooltip, value);
    }
}

/// <summary>
/// V11R-B-4 Studio · Batch mode: real <see cref="IRunController"/> projection, dynamic stage columns
/// (projection <c>step_flow</c>, never a hard-coded ten), shared multi-page selection, chip filtering,
/// scope-suffixed batch actions, gate confirmation and bidirectional drill-down.
/// </summary>
public sealed class StudioBatchViewModel : StudioObservable
{
    public const string GateWarningText = "门禁未清";
    public const string NotWiredText = "IRunController 不可用（Host 未就绪）· NOT_WIRED";

    private readonly IHostController _host;
    private readonly StudioPageViewModel _page;
    private readonly IRunController? _controller;
    private readonly TimeSpan _pollInterval;
    private readonly IRunDataSource _dataSource;
    private bool _polling;
    private DateTime _lastPollUtc = DateTime.MinValue;
    private string? _runId;
    private StudioBatchRunState _state = StudioBatchRunState.NoRun;
    private StudioRunProjection? _projection;
    private StudioBatchFilter _filter = StudioBatchFilter.All;
    private StudioBatchScope _scope = StudioBatchScope.All;
    private string? _highlightedStage;
    private string? _highlightedPageId;
    private string? _statusText;
    private string? _errorText;
    private bool _gateConfirmOpen;
    private string _gateImpactText = string.Empty;
    private StudioBatchActionViewModel? _pendingGateAction;
    private StudioBatchRowViewModel? _drawerRow;
    private bool _submitInFlight;
    private string? _intentIdempotencyKey;
    private bool _stopArmed;
    private IReadOnlyList<StudioRunStageState> _stageColumns = Array.Empty<StudioRunStageState>();

    public StudioBatchViewModel(
        IHostController host,
        StudioSelection selection,
        StudioPageViewModel page,
        IRunController? controller,
        TimeSpan? pollInterval = null)
    {
        _host = host;
        Selection = selection;
        _page = page;
        _controller = controller ?? host as IRunController;
        _pollInterval = pollInterval ?? TimeSpan.FromMilliseconds(750);
        _dataSource = _controller is null
            ? NotWiredRunDataSource.Instance
            : new RunControllerRunDataSource(_controller, () => _runId);

        Rows = new ObservableCollection<StudioBatchRowViewModel>();
        StageRail = new ObservableCollection<StudioBatchStageRailItemViewModel>();
        Chips = new ObservableCollection<StudioBatchCountChipViewModel>();
        Actions = new ObservableCollection<StudioBatchActionViewModel>
        {
            new(StudioBatchActionKind.Translate, "翻译"),
            new(StudioBatchActionKind.Reocr, "重 OCR"),
            new(StudioBatchActionKind.Reinpaint, "重修复"),
            new(StudioBatchActionKind.Rerender, "重渲染"),
        };
        RebuildChips();
        BuildActions();
        Selection.Changed += (_, _) =>
        {
            BuildActions();
            Raise(nameof(ScopeSuffix));
            Raise(nameof(ActionBarHeader));
        };
    }

    /// <summary>Raised when the matrix asks to drill into Page mode for one page (+ optional stage).</summary>
    public event EventHandler<(string PageId, string? StageType)>? DrillToPageRequested;

    /// <summary>P1-A: ONE notification per poll; the matrix diffs cells instead of rebuilding the tree.</summary>
    public event EventHandler? ProjectionApplied;

    public StudioSelection Selection { get; }

    public IRunDataSource DataSource => _dataSource;

    public ObservableCollection<StudioBatchRowViewModel> Rows { get; }

    public ObservableCollection<StudioBatchStageRailItemViewModel> StageRail { get; }

    public ObservableCollection<StudioBatchCountChipViewModel> Chips { get; }

    public ObservableCollection<StudioBatchActionViewModel> Actions { get; }

    public IReadOnlyList<StudioRunStageState> StageColumns => _stageColumns;

    public int StageColumnCount => _stageColumns.Count;

    public StudioRunProjection? Projection => _projection;

    public string? RunId => _runId;

    public string RunIdText => _runId ?? "—";

    public string RunStatus => _projection?.RunStatus ?? (_runId is null ? "无运行" : "读取中");

    public bool IsWired => _dataSource.IsWired;

    public TimeSpan PollInterval => _pollInterval;

    public StudioBatchRunState State
    {
        get => _state;
        private set
        {
            if (Set(ref _state, value))
            {
                Raise(nameof(ShowsEmptyState));
                Raise(nameof(ShowsNotWired));
                Raise(nameof(ShowsError));
                Raise(nameof(HasData));
                Raise(nameof(HeaderLine));
            }
        }
    }

    public bool ShowsEmptyState => State == StudioBatchRunState.NoRun;

    public bool ShowsNotWired => State == StudioBatchRunState.NotWired;

    public bool ShowsError => State == StudioBatchRunState.Error;

    public bool HasData => State is StudioBatchRunState.Ready or StudioBatchRunState.Partial && Rows.Count > 0;

    public string HeaderLine => State switch
    {
        StudioBatchRunState.NotWired => NotWiredText,
        StudioBatchRunState.NoRun => "无活动 Run",
        StudioBatchRunState.Loading => "正在读取任务投影…",
        StudioBatchRunState.Error => _errorText ?? "任务投影读取失败",
        StudioBatchRunState.Partial => "部分投影读取失败（保留上次投影）",
        _ => $"{_projection?.Title ?? "Run"} · {RunStatus} · {Math.Round((_projection?.Percent ?? 0) * 100):0}%",
    };

    public string ProgressText => _projection is { } projection
        ? $"{Math.Round(projection.Percent * 100):0}% · {projection.CompletedPageCount}/{projection.TotalPageCount} 页 · 失败 {projection.FailedPageCount}"
        : "—";

    public string? StatusText => _statusText;

    public string? ErrorText => _errorText;

    public bool HasError => !string.IsNullOrWhiteSpace(_errorText);

    public StudioBatchFilter ActiveFilter
    {
        get => _filter;
        private set
        {
            if (Set(ref _filter, value))
            {
                ApplyFilter();
                foreach (var chip in Chips)
                {
                    chip.IsActive = chip.Filter == value;
                }

                Raise(nameof(FilterText));
            }
        }
    }

    public string FilterText => ActiveFilter == StudioBatchFilter.All
        ? "筛选：全部"
        : $"筛选：{Chips.FirstOrDefault(chip => chip.Filter == ActiveFilter)?.Label}";

    public StudioBatchScope Scope
    {
        get => _scope;
        private set
        {
            if (Set(ref _scope, value))
            {
                BuildActions();
                Raise(nameof(ScopeSuffix));
                Raise(nameof(ActionBarHeader));
            }
        }
    }

    /// <summary>Always-visible scope suffix for every batch action (FUSION §2.3).</summary>
    /// <summary>
    /// FUSION hard rule 1 / R-16: an explicit multi-page selection always wins over the manual scope
    /// selector, so a Batch box selection of 3 pages keeps suffix " · 选中 3 页" in every mode.
    /// </summary>
    public string ScopeSuffix => Selection.ResolvedScope == StudioScopeKind.SelectedPages
        ? Selection.ScopeSuffix
        : _scope switch
        {
            StudioBatchScope.All => " · 全部",
            StudioBatchScope.Selected => " · 选中 0 页",
            _ => CurrentPageLabel is null ? " · 当前页（未选择）" : $" · 当前页 {CurrentPageLabel}",
        };

    private string? CurrentPageLabel =>
        _projection?.RowFor(Selection.CurrentPageId)?.Filename ?? Selection.CurrentPageId;

    public string ActionBarHeader => $"已选 {SelectedCellCount} 单元 · 作用域{ScopeSuffix}";

    public int SelectedCellCount => Rows.Sum(row => row.Cells.Count(cell => cell.IsSelected));

    public int SelectedRowCount => Rows.Count(row => row.IsSelected);

    public bool HasSelection => SelectedCellCount > 0;

    public bool IsPolling => _polling;

    public bool CanPause => _projection?.Controls.CanPause ?? false;

    public bool CanStop => _projection?.Controls.CanStop ?? false;

    public bool CanContinue => _projection?.Controls.CanContinue ?? false;

    public bool CanRestart => _projection?.Controls.CanRestart ?? false;

    public bool CanRetryFailed => _projection?.Controls.CanRetryFailed ?? false;

    /// <summary>R-22: intent-level idempotency key (generated once, reused on retry, cleared on success).</summary>
    public string? CurrentIntentKey => _intentIdempotencyKey;

    /// <summary>R-22: while a submit is in flight the actions are disabled (double-click guard).</summary>
    public bool IsSubmitInFlight => _submitInFlight;

    /// <summary>B-2 D-4 parity: the first 「停止」 arms the confirmation, the second cancels the run.</summary>
    public bool StopArmed => _stopArmed;

    public async Task<RunControlInfo?> RequestStopAsync(CancellationToken cancellationToken = default)
    {
        if (!_stopArmed)
        {
            _stopArmed = true;
            _statusText = $"确认停止？再次点击「停止」将中止 Run {_runId}（未完成页保留现状）";
            Raise(nameof(StopArmed));
            Raise(nameof(StatusText));
            return null;
        }

        return await CancelConfirmedStopAsync(cancellationToken).ConfigureAwait(true);
    }

    /// <summary>Cancel exit of the stop confirmation: no Core call, no residual state.</summary>
    public void CancelStop()
    {
        _stopArmed = false;
        _statusText = "已取消停止（Run 继续运行）";
        Raise(nameof(StopArmed));
        Raise(nameof(StatusText));
    }

    /// <summary>Confirm exit of the stop confirmation (used by the modal's 确认 button).</summary>
    public async Task<RunControlInfo?> CancelConfirmedStopAsync(CancellationToken cancellationToken = default)
    {
        _stopArmed = false;
        Raise(nameof(StopArmed));
        return await ControlAsync(RunControlAction.Stop, cancellationToken).ConfigureAwait(true);
    }

    public bool CanResumeBlocked => _projection is { } projection &&
        (string.Equals(projection.RunStatus, "blocked", StringComparison.OrdinalIgnoreCase) ||
         projection.BlockedPageCount > 0);

    public bool HasGateWarning => _projection is { } projection &&
        (projection.FailedPageCount > 0 || projection.BlockedPageCount > 0);

    public string GateWarning => HasGateWarning && _projection is { } projection
        ? $"{GateWarningText}（失败 {projection.FailedPageCount} · 阻塞 {projection.BlockedPageCount}）"
        : string.Empty;

    public string GateWarningGlyph => HasGateWarning ? StudioStates.Glyph(StudioStateKind.Failed) : StudioStates.Glyph(StudioStateKind.Done);

    public string GateWarningClass => HasGateWarning ? "studio-state-failed" : "studio-state-done";

    public StudioBatchRowViewModel? DrawerRow
    {
        get => _drawerRow;
        private set
        {
            if (Set(ref _drawerRow, value))
            {
                Raise(nameof(IsDrawerOpen));
                Raise(nameof(DrawerTitle));
                Raise(nameof(DrawerDetail));
            }
        }
    }

    public bool IsDrawerOpen => _drawerRow is not null;

    public string DrawerTitle => _drawerRow is { } row ? $"页 {row.NumberLabel}" : string.Empty;

    public string DrawerDetail => _drawerRow is { } row
        ? $"{row.StateLabel} · {row.ErrorCode ?? "无错误码"} · steps {row.Row.Steps.Count}"
        : string.Empty;

    public bool IsGateConfirmOpen
    {
        get => _gateConfirmOpen;
        private set => Set(ref _gateConfirmOpen, value);
    }

    public string GateImpactText => _gateImpactText;

    public string? HighlightedStage => _highlightedStage;

    public string? HighlightedPageId => _highlightedPageId;

    // ---------------------------------------------------------------- projection refresh

    /// <summary>One projection read. Never throws; a failed refresh keeps the last good projection.</summary>
    public async Task<bool> RefreshAsync(CancellationToken cancellationToken = default)
    {
        if (!_dataSource.IsWired)
        {
            State = StudioBatchRunState.NotWired;
            RebuildChips();
            return false;
        }

        if (string.IsNullOrWhiteSpace(_runId))
        {
            State = StudioBatchRunState.NoRun;
            _projection = null;
            _stageColumns = Array.Empty<StudioRunStageState>();
            Rows.Clear();
            StageRail.Clear();
            RebuildChips();
            RaiseProjectionProps();
            return false;
        }

        _lastPollUtc = DateTime.UtcNow;
        StudioRunProjection? projection;
        try
        {
            projection = await _dataSource.GetProjectionAsync(_page.ChapterId, cancellationToken).ConfigureAwait(true);
        }
        catch (OperationCanceledException)
        {
            return false;
        }

        if (projection is null)
        {
            _errorText = _host.Snapshot.LastError ?? "GetTaskProjection 返回空";
            State = _projection is null ? StudioBatchRunState.Error : StudioBatchRunState.Partial;
            Raise(nameof(HeaderLine));
            Raise(nameof(HasError));
            Raise(nameof(ErrorText));
            return false;
        }

        ApplyProjection(projection);
        _errorText = null;
        State = StudioBatchRunState.Ready;
        Raise(nameof(HeaderLine));
        Raise(nameof(HasError));
        Raise(nameof(ErrorText));
        return true;
    }

    /// <summary>Starts the injectable 500–1000 ms poll (no push channel exists).</summary>
    public void StartPolling()
    {
        if (_polling)
        {
            return;
        }

        _polling = true;
        Raise(nameof(IsPolling));
    }

    public void StopPolling()
    {
        if (!_polling)
        {
            return;
        }

        _polling = false;
        Raise(nameof(IsPolling));
    }

    /// <summary>Tick invoked from the view's DispatcherTimer (interval = <see cref="PollInterval"/>).</summary>
    public async Task TickAsync(CancellationToken cancellationToken = default)
    {
        if (!_polling || DateTime.UtcNow - _lastPollUtc < _pollInterval)
        {
            return;
        }

        await RefreshAsync(cancellationToken).ConfigureAwait(true);
    }

    public void SetRunId(string? runId)
    {
        _runId = runId;
        Raise(nameof(RunId));
        Raise(nameof(RunIdText));
        Raise(nameof(RunStatus));
    }

    private void ApplyProjection(StudioRunProjection projection)
    {
        var selected = Rows
            .SelectMany(row => row.Cells
                .Where(cell => cell.IsSelected)
                .Select(cell => (row.PageId, cell.StageType)))
            .ToHashSet();
        var selectedRows = Rows.Where(row => row.IsSelected).Select(row => row.PageId).ToHashSet();

        _projection = projection;
        _stageColumns = projection.Columns;
        Rows.Clear();
        for (var index = 0; index < projection.Rows.Count; index++)
        {
            var row = projection.Rows[index];
            var cells = projection.Columns
                .Select(stage => new StudioBatchCellViewModel(
                    index,
                    stage.CoreStepType,
                    stage.Label,
                    row.StageState(stage.CoreStepType),
                    row.Steps.FirstOrDefault(step =>
                        string.Equals(step.StepType, stage.CoreStepType, StringComparison.OrdinalIgnoreCase))?.ErrorCode))
                .ToList();
            Rows.Add(new StudioBatchRowViewModel(index, row, cells)
            {
                IsSelected = selectedRows.Contains(row.PageId),
            });
        }

        // Selection survives a poll refresh through the stable (page id, stage type) identity.
        foreach (var row in Rows)
        {
            foreach (var cell in row.Cells)
            {
                cell.IsSelected = selected.Contains((row.PageId, cell.StageType));
            }

            row.IsSelected = row.IsSelected || row.Cells.Any(cell => cell.IsSelected);
        }

        RebuildStageRail();
        RebuildChips();
        ApplyFilter();
        ApplyHighlight();
        RaiseProjectionProps();
        SyncSelectionToSharedModel();
        ProjectionApplied?.Invoke(this, EventArgs.Empty);
    }

    private void RaiseProjectionProps()
    {
        Raise(nameof(Projection));
        Raise(nameof(StageColumns));
        Raise(nameof(StageColumnCount));
        Raise(nameof(RunStatus));
        Raise(nameof(ProgressText));
        Raise(nameof(HeaderLine));
        Raise(nameof(HasData));
        Raise(nameof(CanPause));
        Raise(nameof(CanStop));
        Raise(nameof(CanContinue));
        Raise(nameof(CanRestart));
        Raise(nameof(CanRetryFailed));
        Raise(nameof(CanResumeBlocked));
        Raise(nameof(HasGateWarning));
        Raise(nameof(GateWarning));
        Raise(nameof(GateWarningGlyph));
        Raise(nameof(GateWarningClass));
        Raise(nameof(SelectedCellCount));
        Raise(nameof(SelectedRowCount));
        Raise(nameof(HasSelection));
        Raise(nameof(ActionBarHeader));
        Raise(nameof(ScopeSuffix));
        BuildActions();
    }

    private void RebuildStageRail()
    {
        StageRail.Clear();
        foreach (var stage in _stageColumns)
        {
            var stageType = stage.CoreStepType;
            var completed = Rows.Count(row => row.Row.StageState(stageType) == StudioStateKind.Done);
            var failed = Rows.Count(row => row.Row.StageState(stageType) == StudioStateKind.Failed);
            StageRail.Add(new StudioBatchStageRailItemViewModel(
                stageType, stage.Label, completed, Rows.Count, failed)
            {
                IsActive = string.Equals(stageType, _highlightedStage, StringComparison.Ordinal),
            });
        }
    }

    private void RebuildChips()
    {
        var projection = _projection;
        Chips.Clear();
        Chips.Add(new StudioBatchCountChipViewModel(StudioBatchFilter.All, "总", projection?.TotalPageCount,
            "总页数（任务投影）"));
        Chips.Add(new StudioBatchCountChipViewModel(StudioBatchFilter.Completed, "完成", projection?.CompletedPageCount,
            "完成页数（任务投影）"));
        Chips.Add(new StudioBatchCountChipViewModel(StudioBatchFilter.Failed, "失败", projection?.FailedPageCount,
            "失败页数（任务投影）"));
        Chips.Add(new StudioBatchCountChipViewModel(StudioBatchFilter.Stale, "过期", null,
            "任务投影不提供 stale 口径：由上游变更/Region review 面提供（V11R-F0-2+）"));
        Chips.Add(new StudioBatchCountChipViewModel(StudioBatchFilter.NeedsReview, "待确认", null,
            "任务投影不提供待确认口径：review 状态在 Region revision 面（V11R-F0-2+）"));
        Chips.Add(new StudioBatchCountChipViewModel(StudioBatchFilter.Blocked, "阻塞", projection?.BlockedPageCount,
            "阻塞页数（任务投影）"));
        foreach (var chip in Chips)
        {
            chip.IsActive = chip.Filter == ActiveFilter;
        }

        Raise(nameof(FilterText));
    }

    // ---------------------------------------------------------------- filter

    public void SetFilter(StudioBatchFilter filter)
    {
        var chip = Chips.FirstOrDefault(item => item.Filter == filter);
        if (chip is { IsAvailable: false })
        {
            _statusText = $"{chip.Label}：{chip.Tooltip}";
            Raise(nameof(StatusText));
            return;
        }

        ActiveFilter = filter;
    }

    private void ApplyFilter()
    {
        foreach (var row in Rows)
        {
            var matches = ActiveFilter switch
            {
                StudioBatchFilter.All => true,
                StudioBatchFilter.Completed => row.State == StudioStateKind.Done,
                StudioBatchFilter.Failed => row.State == StudioStateKind.Failed,
                StudioBatchFilter.Blocked => row.State == StudioStateKind.Blocked,
                StudioBatchFilter.Stale => row.State == StudioStateKind.Stale,
                StudioBatchFilter.NeedsReview => false,
                _ => true,
            };
            row.IsDimmed = !matches;
            foreach (var cell in row.Cells)
            {
                cell.IsDimmed = !matches;
            }
        }
    }

    // ---------------------------------------------------------------- selection

    public (int RowIndex, string? StageType)? SelectingAnchor { get; private set; }

    public void SelectCell(int rowIndex, string? stageType = null, bool extend = false)
    {
        if (rowIndex < 0 || rowIndex >= Rows.Count)
        {
            return;
        }

        var type = stageType ?? Rows[rowIndex].Cells.FirstOrDefault()?.StageType;
        if (extend && SelectingAnchor is { } anchor)
        {
            SelectBox(anchor.RowIndex, anchor.StageType, rowIndex, type);
            return;
        }

        ClearSelectionCore();
        var cell = Rows[rowIndex].Cells.FirstOrDefault(item =>
            string.Equals(item.StageType, type, StringComparison.Ordinal));
        if (cell is null)
        {
            return;
        }

        cell.IsSelected = true;
        Rows[rowIndex].IsSelected = true;
        SelectingAnchor = (rowIndex, cell.StageType);
        DrawerRow = Rows[rowIndex];
        SyncSelectionToSharedModel();
    }

    public void SelectRow(int rowIndex, bool extend = false)
    {
        if (rowIndex < 0 || rowIndex >= Rows.Count)
        {
            return;
        }

        if (extend && SelectingAnchor is { } anchor)
        {
            var types = _stageColumns.Select(stage => stage.CoreStepType).ToList();
            SelectBox(anchor.RowIndex, types.FirstOrDefault(), rowIndex, types.LastOrDefault());
            return;
        }

        ClearSelectionCore();
        var row = Rows[rowIndex];
        foreach (var cell in row.Cells)
        {
            cell.IsSelected = true;
        }

        row.IsSelected = true;
        SelectingAnchor = (rowIndex, row.Cells.FirstOrDefault()?.StageType);
        DrawerRow = row;
        SyncSelectionToSharedModel();
    }

    /// <summary>Box selection: every cell inside the (anchor..focus) rectangle (matrix drag / Shift).</summary>
    public void SelectBox(int anchorRow, string? anchorStage, int focusRow, string? focusStage)
    {
        if (Rows.Count == 0 || _stageColumns.Count == 0)
        {
            return;
        }

        ClearSelectionCore();
        var fromStage = StageIndex(anchorStage);
        var toStage = StageIndex(focusStage);
        if (fromStage < 0 || toStage < 0)
        {
            fromStage = 0;
            toStage = _stageColumns.Count - 1;
        }

        var first = Math.Min(fromStage, toStage);
        var last = Math.Max(fromStage, toStage);
        var fromRow = Math.Clamp(Math.Min(anchorRow, focusRow), 0, Rows.Count - 1);
        var toRow = Math.Clamp(Math.Max(anchorRow, focusRow), 0, Rows.Count - 1);
        for (var row = fromRow; row <= toRow; row++)
        {
            for (var column = first; column <= last; column++)
            {
                Rows[row].Cells[column].IsSelected = true;
            }

            Rows[row].IsSelected = true;
        }

        SelectingAnchor = (fromRow, _stageColumns[first].CoreStepType);
        DrawerRow = Rows[fromRow];
        SyncSelectionToSharedModel();
    }

    private int StageIndex(string? stageType) =>
        string.IsNullOrWhiteSpace(stageType)
            ? -1
            : _stageColumns.ToList().FindIndex(stage =>
                string.Equals(stage.CoreStepType, stageType, StringComparison.OrdinalIgnoreCase));

    public void ClearSelection()
    {
        ClearSelectionCore();
        SyncSelectionToSharedModel();
    }

    private void ClearSelectionCore()
    {
        foreach (var row in Rows)
        {
            row.IsSelected = false;
            foreach (var cell in row.Cells)
            {
                cell.IsSelected = false;
            }
        }

        SelectingAnchor = null;
    }

    /// <summary>Shares the page scope with Page mode (same <see cref="StudioSelection"/>, AC2).</summary>
    private void SyncSelectionToSharedModel()
    {
        Selection.SetSelectedPages(Rows
            .Where(row => row.Cells.Any(cell => cell.IsSelected))
            .Select(row => row.PageId));
        Raise(nameof(SelectedCellCount));
        Raise(nameof(SelectedRowCount));
        Raise(nameof(HasSelection));
        Raise(nameof(ActionBarHeader));
        Raise(nameof(ScopeSuffix));
        BuildActions();
    }

    // ---------------------------------------------------------------- drill / highlight

    public void HighlightStage(string? stageType, string? pageId = null)
    {
        _highlightedStage = stageType;
        _highlightedPageId = pageId;
        foreach (var item in StageRail)
        {
            item.IsActive = string.Equals(item.StageType, stageType, StringComparison.Ordinal);
        }

        ApplyHighlight();
        Raise(nameof(HighlightedStage));
        Raise(nameof(HighlightedPageId));
    }

    private void ApplyHighlight()
    {
        foreach (var row in Rows)
        {
            row.IsHighlighted = _highlightedPageId is not null &&
                string.Equals(row.PageId, _highlightedPageId, StringComparison.Ordinal);
            foreach (var cell in row.Cells)
            {
                cell.IsHighlighted = _highlightedStage is not null &&
                    string.Equals(cell.StageType, _highlightedStage, StringComparison.Ordinal);
            }
        }
    }

    /// <summary>Matrix Enter / double-click: asks the workspace to open Page mode on this page.</summary>
    public bool RequestDrillToPage(int rowIndex)
    {
        if (rowIndex < 0 || rowIndex >= Rows.Count)
        {
            return false;
        }

        var row = Rows[rowIndex];
        var stage = row.Cells.FirstOrDefault(cell => cell.IsSelected)?.StageType ?? _highlightedStage;
        DrillToPageRequested?.Invoke(this, (row.PageId, stage));
        return true;
    }

    public void CloseDrawer() => DrawerRow = null;

    // ---------------------------------------------------------------- run actions

    public async Task<RunStartInfo?> StartRunAsync(string command, CancellationToken cancellationToken = default)
    {
        if (_controller is null)
        {
            _statusText = NotWiredText;
            Raise(nameof(StatusText));
            return null;
        }

        var scope = BuildScope();
        if (scope is null)
        {
            _statusText = "没有可用作用域（未选择章节或页面）";
            Raise(nameof(StatusText));
            return null;
        }

        if (_submitInFlight)
        {
            _statusText = "提交中：请等待当前动作返回（双击已被阻止）";
            Raise(nameof(StatusText));
            return null;
        }

        _intentIdempotencyKey ??= Guid.NewGuid().ToString("N");
        Raise(nameof(CurrentIntentKey));
        _submitInFlight = true;
        Raise(nameof(IsSubmitInFlight));
        BuildActions();
        RunStartInfo? started = null;
        try
        {
            started = await _controller
                .StartRunAsync(new RunStartRequest(command, scope, null, _intentIdempotencyKey), cancellationToken)
                .ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or IOException or TimeoutException)
        {
            _errorText = $"提交失败：{ex.GetType().Name}";
            State = StudioBatchRunState.Error;
            Raise(nameof(HeaderLine));
            Raise(nameof(ErrorText));
            return null;
        }
        finally
        {
            _submitInFlight = false;
            Raise(nameof(IsSubmitInFlight));
            BuildActions();
        }
        if (started is null)
        {
            _errorText = _host.Snapshot.LastError ?? "StartRun 被拒绝";
            State = StudioBatchRunState.Error;
            Raise(nameof(HeaderLine));
            Raise(nameof(ErrorText));
            return null;
        }

        if (started is null)
        {
            return null;
        }

        SetRunId(started.RunId);
        _intentIdempotencyKey = null;
        Raise(nameof(CurrentIntentKey));
        _statusText = $"已创建 Run {started.RunId}（{started.Status}）";
        Raise(nameof(StatusText));
        State = StudioBatchRunState.Loading;
        await RefreshAsync(cancellationToken).ConfigureAwait(true);
        return started;
    }

    /// <summary>「开始处理」empty-state main action: full translation over the current scope.</summary>
    public Task<RunStartInfo?> StartProcessingAsync(CancellationToken cancellationToken = default) =>
        StartRunAsync(_scope switch
        {
            StudioBatchScope.Selected => "translate_selected",
            StudioBatchScope.CurrentPage => "translate_single",
            _ => "translate_all",
        }, cancellationToken);

    public Task<RunControlInfo?> PauseAsync(CancellationToken cancellationToken = default) =>
        ControlAsync(RunControlAction.Pause, cancellationToken);

    public Task<RunControlInfo?> ResumeAsync(CancellationToken cancellationToken = default) =>
        ControlAsync(RunControlAction.Resume, cancellationToken);

    public Task<RunControlInfo?> StopAsync(CancellationToken cancellationToken = default) =>
        ControlAsync(RunControlAction.Stop, cancellationToken);

    public async Task<RunControlInfo?> RetryFailedAsync(CancellationToken cancellationToken = default)
    {
        if (_controller is null || _runId is null)
        {
            return null;
        }

        var info = await _controller
            .RetryFailedTargetsAsync(_runId, Guid.NewGuid().ToString("N"), cancellationToken)
            .ConfigureAwait(true);
        if (info is not null)
        {
            _statusText = $"已重试失败目标（{info.Status}）";
            Raise(nameof(StatusText));
            await RefreshAsync(cancellationToken).ConfigureAwait(true);
        }

        return info;
    }

    public async Task<RunControlInfo?> ResumeBlockedAsync(CancellationToken cancellationToken = default)
    {
        if (_controller is null || _runId is null)
        {
            return null;
        }

        var info = await _controller.ResumeBlockedRunAsync(_runId, cancellationToken).ConfigureAwait(true);
        if (info is not null)
        {
            _statusText = $"已恢复阻塞（{info.Status}）";
            Raise(nameof(StatusText));
            await RefreshAsync(cancellationToken).ConfigureAwait(true);
        }

        return info;
    }

    private async Task<RunControlInfo?> ControlAsync(RunControlAction action, CancellationToken cancellationToken)
    {
        if (_controller is null || _runId is null)
        {
            return null;
        }

        var info = await _controller.ControlRunAsync(_runId, action, null, cancellationToken).ConfigureAwait(true);
        if (info is not null)
        {
            _statusText = $"{action} → {info.Status}";
            Raise(nameof(StatusText));
            await RefreshAsync(cancellationToken).ConfigureAwait(true);
        }

        return info;
    }

    /// <summary>P1-B: the scope can only be materialized from real ids; no silent chapter fallback.</summary>
    public bool CanMaterializeScope()
    {
        if (!_dataSource.IsWired)
        {
            return false;
        }

        var chapterId = Selection.ChapterId ?? _page.ChapterId;
        if (Selection.ResolvedScope == StudioScopeKind.SelectedPages)
        {
            return Selection.SelectedPageIds.Count > 0 && !string.IsNullOrWhiteSpace(chapterId);
        }

        return _scope switch
        {
            StudioBatchScope.Selected => Selection.SelectedPageIds.Count > 0,
            StudioBatchScope.CurrentPage => !string.IsNullOrWhiteSpace(Selection.CurrentPageId),
            _ => !string.IsNullOrWhiteSpace(chapterId),
        };
    }

    private Dictionary<string, object?>? BuildScope()
    {
        var chapterId = Selection.ChapterId ?? _page.ChapterId;
        if (Selection.ResolvedScope == StudioScopeKind.SelectedPages)
        {
            return new Dictionary<string, object?>
            {
                ["kind"] = "page_selection",
                ["chapter_id"] = chapterId,
                ["page_ids"] = Selection.SelectedPageIds.ToArray(),
            };
        }

        if (_scope == StudioBatchScope.Selected && Selection.SelectedPageIds.Count > 0)
        {
            return new Dictionary<string, object?>
            {
                ["kind"] = "page_selection",
                ["chapter_id"] = chapterId,
                ["page_ids"] = Selection.SelectedPageIds.ToArray(),
            };
        }

        if (_scope == StudioBatchScope.CurrentPage && Selection.CurrentPageId is { } pageId)
        {
            return new Dictionary<string, object?>
            {
                ["kind"] = "page",
                ["chapter_id"] = chapterId,
                ["page_id"] = pageId,
            };
        }

        return string.IsNullOrWhiteSpace(chapterId)
            ? null
            : new Dictionary<string, object?>
            {
                ["kind"] = "chapter",
                ["chapter_id"] = chapterId,
            };
    }

    public void SetScope(StudioBatchScope scope)
    {
        if (scope == StudioBatchScope.Selected && Selection.SelectedPageIds.Count == 0)
        {
            _statusText = "选中作用域需要先在矩阵中选择页面";
            Raise(nameof(StatusText));
            return;
        }

        Scope = scope;
    }

    /// <summary>Sets the current page scope; selection carries over to Page mode.</summary>
    public void UseCurrentPageScope() => SetScope(StudioBatchScope.CurrentPage);

    // ---------------------------------------------------------------- gate

    /// <summary>
    /// Batch action entry. Uncleared gate (failed/blocked) opens an impact confirmation modal instead
    /// of silently running (SCREEN_SPECS §4 门禁). Returns true only when the action actually started.
    /// </summary>
    public async Task<bool> ExecuteActionAsync(
        StudioBatchActionViewModel action,
        CancellationToken cancellationToken = default)
    {
        if (!action.IsEnabled)
        {
            _statusText = CanMaterializeScope()
                ? "提交中或动作不可用：" + action.Tooltip
                : "动作不可用：作用域无法物化（缺少章节/选中页），未发起任何 Run，未回落到整章";
            Raise(nameof(StatusText));
            return false;
        }

        if (HasGateWarning)
        {
            _pendingGateAction = action;
            _gateImpactText = $"{GateWarning} · 作用域{ScopeSuffix} · 仍然执行会产生不完整产物";
            IsGateConfirmOpen = true;
            Raise(nameof(GateImpactText));
            return false;
        }

        return await ExecuteActionCoreAsync(action, cancellationToken).ConfigureAwait(true);
    }

    public async Task<bool> ConfirmGateAsync(CancellationToken cancellationToken = default)
    {
        IsGateConfirmOpen = false;
        if (_pendingGateAction is not { } action)
        {
            return false;
        }

        _pendingGateAction = null;
        return await ExecuteActionCoreAsync(action, cancellationToken).ConfigureAwait(true);
    }

    public void CancelGate()
    {
        IsGateConfirmOpen = false;
        _pendingGateAction = null;
        _statusText = "已取消（门禁未清，未执行任何动作）";
        Raise(nameof(StatusText));
    }

    private async Task<bool> ExecuteActionCoreAsync(
        StudioBatchActionViewModel action,
        CancellationToken cancellationToken)
    {
        var command = action.Kind switch
        {
            StudioBatchActionKind.Translate => _scope switch
            {
                StudioBatchScope.Selected => "translate_selected",
                StudioBatchScope.CurrentPage => "translate_single",
                _ => "translate_all",
            },
            StudioBatchActionKind.Reocr => _scope switch
            {
                StudioBatchScope.Selected => "reocr_selected",
                StudioBatchScope.CurrentPage => "reocr_single",
                _ => "reocr_all",
            },
            StudioBatchActionKind.Reinpaint => _scope switch
            {
                StudioBatchScope.Selected => "reinpaint_selected",
                StudioBatchScope.CurrentPage => "reinpaint_single",
                _ => "reinpaint_all",
            },
            _ => _scope switch
            {
                StudioBatchScope.Selected => "rerender_selected",
                StudioBatchScope.CurrentPage => "rerender_single",
                _ => "rerender_all",
            },
        };

        var started = await StartRunAsync(command, cancellationToken).ConfigureAwait(true);
        return started is not null;
    }

    /// <summary>Rebuilds the scope suffix + enablement of the four batch actions.</summary>
    private void BuildActions()
    {
        foreach (var action in Actions)
        {
            action.ScopeSuffix = ScopeSuffix;
            action.IsEnabled = CanMaterializeScope() && !_submitInFlight;
            action.Tooltip = _dataSource.IsWired
                ? $"{action.Label}{ScopeSuffix}"
                : StudioCapabilityGate.NotWiredTooltip;
        }

        Raise(nameof(ScopeSuffix));
        Raise(nameof(ActionBarHeader));
    }

    /// <summary>Re-applies the shared page scope after a mode switch (context retention, AC2).</summary>
    public void RestoreFromSharedSelection()
    {
        foreach (var row in Rows)
        {
            var selected = Selection.SelectedPageIds.Contains(row.PageId, StringComparer.Ordinal);
            row.IsSelected = selected;
            foreach (var cell in row.Cells)
            {
                cell.IsSelected = selected;
            }
        }

        Raise(nameof(SelectedCellCount));
        Raise(nameof(SelectedRowCount));
        Raise(nameof(HasSelection));
        Raise(nameof(ActionBarHeader));
    }
}