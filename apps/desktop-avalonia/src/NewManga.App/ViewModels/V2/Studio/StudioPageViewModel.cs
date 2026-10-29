using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.CoreClient;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>Load lifecycle of one Studio page (DESIGN_SYSTEM §7 six states, no full-page spinner).</summary>
public enum StudioLoadState
{
    Idle,
    Loading,
    Ready,

    /// <summary>Host is up but there is nothing to show (no book / no pages / no regions).</summary>
    Empty,

    /// <summary>The read that mattered failed; the reason is shown in place with a retry.</summary>
    Error,

    /// <summary>Page or regions loaded, the other read failed — render what exists (partial).</summary>
    Partial,
}

/// <summary>The three exits of the unsaved-changes modal (SCREEN_SPECS §3).</summary>
public enum StudioLeaveChoice
{
    Save,
    Discard,
    Cancel,
}

/// <summary>Outcome of one leave attempt (typed: the UI never throws over a failed save).</summary>
public enum StudioLeaveOutcome
{
    NoChanges,
    Saved,
    Discarded,
    Cancelled,
    SaveFailed,
}

/// <summary>One film-strip page item (thumbnails load lazily through the Host resource channel).</summary>
public sealed class StudioFilmPageItem : StudioObservable
{
    private bool _isCurrent;
    private StudioStateKind? _state;
    private byte[]? _thumbnail;

    public StudioFilmPageItem(ChapterPageSummary page, int index)
    {
        PageId = page.PageId;
        SourceFilename = page.SourceFilename;
        Index = index;
    }

    public string PageId { get; }

    public string SourceFilename { get; }

    /// <summary>0-based index inside the chapter (page numbering shown as 1-based).</summary>
    public int Index { get; }

    public string NumberLabel => (Index + 1).ToString("00");

    public string Tooltip => $"第 {Index + 1} 页 · {SourceFilename}";

    private bool _isSelected;

    /// <summary>Selected in the strip (current page holds the accent left bar).</summary>
    public bool IsSelected
    {
        get => _isSelected;
        internal set => Set(ref _isSelected, value);
    }

    public bool IsCurrent
    {
        get => _isCurrent;
        internal set => Set(ref _isCurrent, value);
    }

    /// <summary>Per-page state once a run projection exists (null = no projection, no invented dot).</summary>
    public StudioStateKind? State
    {
        get => _state;
        internal set
        {
            if (Set(ref _state, value))
            {
                Raise(nameof(HasState));
                Raise(nameof(StateGlyph));
                Raise(nameof(StateClass));
                Raise(nameof(StateLabel));
            }
        }
    }

    public bool HasState => _state is not null;

    public string StateGlyph => _state is { } state ? StudioStates.Glyph(state) : string.Empty;

    public string StateClass => _state is { } state ? StudioStates.StyleClass(state) : "nm-state-notstarted";

    public string StateLabel => _state is { } state ? StudioStates.Label(state) : "状态未接入";

    /// <summary>Real page image bytes used as the strip thumbnail (null while loading / unavailable).</summary>
    public byte[]? ThumbnailBytes
    {
        get => _thumbnail;
        internal set
        {
            if (Set(ref _thumbnail, value))
            {
                Raise(nameof(HasThumbnail));
            }
        }
    }

    public bool HasThumbnail => _thumbnail is { Length: > 0 };

    public override string ToString() => $"第 {Index + 1} 页 {SourceFilename}";
}

/// <summary>One dot of the Page-mode pipeline band (10 canonical stages).</summary>
public sealed class StudioPipelineStageItem : StudioObservable
{
    private StudioStateKind? _state;

    public StudioPipelineStageItem(StudioStage stage)
    {
        Stage = stage;
    }

    public StudioStage Stage { get; }

    public string Key => Stage.Key;

    public string Label => Stage.Label;

    public string Abbreviation => Stage.Abbreviation;

    public int Index => Stage.Index;

    /// <summary>Null = no projection evidence (renders a neutral "no data" dot, never a fake state).</summary>
    public StudioStateKind? State
    {
        get => _state;
        internal set
        {
            if (Set(ref _state, value))
            {
                Raise(nameof(HasState));
                Raise(nameof(Glyph));
                Raise(nameof(StateClass));
                Raise(nameof(StateLabel));
                Raise(nameof(Tooltip));
            }
        }
    }

    public bool HasState => _state is not null;

    public string Glyph => _state is { } state ? StudioStates.Glyph(state) : "–";

    public string StateClass => _state is { } token ? StudioStates.StyleClass(token) : "nm-state-nodata";

    public string StateLabel => _state is { } state ? StudioStates.Label(state) : "无投影数据";

    public string Tooltip => $"{Stage.Index:00} {Stage.Label} · {StateLabel}";
}

/// <summary>One HUD ring action rendered around the selected region.</summary>
public sealed class StudioHudSlotViewModel : StudioObservable
{
    private bool _isEnabled;
    private bool _isFocused;

    public StudioHudSlotViewModel(StudioHudSlot slot)
    {
        Slot = slot;
    }

    public StudioHudSlot Slot { get; }

    public StudioHudAction Action => Slot.Action;

    public string Position => Slot.Position;

    public string Label => Slot.Label;

    public string Glyph => Slot.Glyph;

    public bool IsEnabled
    {
        get => _isEnabled;
        internal set => Set(ref _isEnabled, value);
    }

    public bool IsFocused
    {
        get => _isFocused;
        internal set
        {
            if (Set(ref _isFocused, value))
            {
                Raise(nameof(StyleClass));
            }
        }
    }

    public string Tooltip { get; internal set; } = string.Empty;

    public string StyleClass => !IsEnabled
        ? "studio-hud-slot disabled"
        : IsFocused
            ? "studio-hud-slot focused"
            : "studio-hud-slot";
}

/// <summary>
/// V11R-B-3: Studio · Page mode. Owns the real load chain
/// (book → chapter → pages → page image + list_regions → revisions), the shared
/// <see cref="StudioSelection"/>, zoom/pan, the HUD ring, the inspector and the unsaved-change guard.
/// It never touches a database, a file path or a model: only <see cref="IHostController"/>.
/// </summary>
public sealed class StudioPageViewModel : StudioObservable
{
    /// <summary>Cap on how many film-strip thumbnails are decoded eagerly (resource channel cost).</summary>
    public const int ThumbnailLimit = 60;

    private readonly IHostController _host;
    private StudioCapabilityGate _gate;
    private StudioLoadState _loadState = StudioLoadState.Idle;
    private string _statusText = string.Empty;
    private string? _errorText;
    private string? _partialReason;
    private string? _bookTitle;
    private string? _chapterTitle;
    private string? _chapterId;
    private string? _bookId;
    private RegionPageProjection? _projection;
    private byte[]? _pageImageBytes;
    private bool _pageImageMissing;
    private StudioRegionItem? _selectedRegion;
    private double _viewportWidth;
    private double _viewportHeight;
    private int _hudFocusIndex = -1;
    private bool _isLoadingPage;
    private bool _leaveModalOpen;
    private string? _leaveError;
    private Func<Task>? _pendingNavigation;
    private string? _lastRerenderSummary;
    private StudioRunProjection? _runProjection;
    private string? _regionDetailsError;
    private bool _isLoadingRegionDetails;
    private int _loadGeneration;

    public StudioPageViewModel(
        IHostController host,
        StudioSelection? selection = null,
        IRunDataSource? runSource = null,
        IRegionTextSource? textSource = null,
        IRegionFlagSource? flagSource = null)
    {
        _host = host;
        Selection = selection ?? new StudioSelection();
        RunSource = runSource ?? NotWiredRunDataSource.Instance;
        TextSource = textSource ?? new NotWiredRegionTextSource();
        FlagSource = flagSource ?? new NotWiredRegionFlagSource();
        _gate = BuildGate();

        Pages = new ObservableCollection<StudioFilmPageItem>();
        Regions = new ObservableCollection<StudioRegionItem>();
        PipelineStages = new ObservableCollection<StudioPipelineStageItem>(
            StudioStages.Canonical.Select(stage => new StudioPipelineStageItem(stage)));
        HudSlots = new ObservableCollection<StudioHudSlotViewModel>(
            StudioHudRing.Slots.Select(slot => new StudioHudSlotViewModel(slot)));
        NotWiredCapabilities = new List<string>();

        Inspector = new StudioInspectorViewModel(this);
        Inspector.PendingEditChanged += (_, _) =>
        {
            Raise(nameof(HasUnsavedChanges));
            Raise(nameof(UnsavedSummary));
            Raise(nameof(LeaveSaveEnabled));
            Raise(nameof(LeaveSaveTooltip));
            UpdateHudSlots();
        };
        Selection.Changed += OnSelectionChanged;

        UpdateHudSlots();
        RefreshPipelineBand();
    }

    /// <summary>Raised whenever the canvas/overlay must re-render (zoom, pan, page, regions).</summary>
    public event EventHandler? CanvasInvalidated;

    /// <summary>Raised when a not-wired action was attempted (view shows an in-place hint, no fake success).</summary>
    public event EventHandler<string>? NotWiredAttempted;

    public IHostController Host => _host;

    public StudioSelection Selection { get; }

    public StudioInspectorViewModel Inspector { get; }

    public IRunDataSource RunSource { get; }

    public IRegionTextSource TextSource { get; }

    public IRegionFlagSource FlagSource { get; }

    public StudioCapabilityGate Gate => _gate;

    public ObservableCollection<StudioFilmPageItem> Pages { get; }

    public ObservableCollection<StudioRegionItem> Regions { get; }

    public ObservableCollection<StudioPipelineStageItem> PipelineStages { get; }

    public ObservableCollection<StudioHudSlotViewModel> HudSlots { get; }

    /// <summary>Every capability this build cannot execute, with its reason (evidence + banner).</summary>
    public IReadOnlyList<string> NotWiredCapabilities { get; private set; }

    // ---------------------------------------------------------------- lifecycle

    public StudioLoadState LoadState
    {
        get => _loadState;
        private set
        {
            if (Set(ref _loadState, value))
            {
                Raise(nameof(IsIdle));
                Raise(nameof(IsLoading));
                Raise(nameof(IsReady));
                Raise(nameof(IsEmpty));
                Raise(nameof(HasError));
                Raise(nameof(IsPartial));
            }
        }
    }

    public bool IsIdle => LoadState == StudioLoadState.Idle;

    public bool IsLoading => LoadState == StudioLoadState.Loading;

    public bool IsReady => LoadState == StudioLoadState.Ready;

    public bool IsEmpty => LoadState == StudioLoadState.Empty;

    public bool HasError => LoadState == StudioLoadState.Error;

    public bool IsPartial => LoadState == StudioLoadState.Partial;

    /// <summary>Transient result of the last action ("类型已更新…"), shown in the canvas status line.</summary>
    public string StatusText
    {
        get => _statusText;
        private set => Set(ref _statusText, value);
    }

    public string? ErrorText
    {
        get => _errorText;
        private set
        {
            if (Set(ref _errorText, value))
            {
                Raise(nameof(HasErrorText));
            }
        }
    }

    public bool HasErrorText => !string.IsNullOrEmpty(_errorText);

    /// <summary>Reason shown by the partial banner (one read worked, the other failed).</summary>
    public string? PartialReason
    {
        get => _partialReason;
        private set
        {
            if (Set(ref _partialReason, value))
            {
                Raise(nameof(HasPartialReason));
            }
        }
    }

    public bool HasPartialReason => !string.IsNullOrEmpty(_partialReason);

    public bool HostReady => _gate.HostReady;

    public bool WritesAllowed => _gate.WritesAllowed;

    public string HostBannerText => !HostReady
        ? $"Host 未就绪（{_host.Snapshot.State}）：{_host.Snapshot.StatusLine}"
        : WritesAllowed
            ? string.Empty
            : StudioCapabilityGate.ReadOnlyTooltip;

    public bool HostBannerVisible => !HostReady || !WritesAllowed;

    public string? BookTitle
    {
        get => _bookTitle;
        private set
        {
            if (Set(ref _bookTitle, value))
            {
                Raise(nameof(BreadcrumbText));
            }
        }
    }

    public string? ChapterTitle
    {
        get => _chapterTitle;
        private set
        {
            if (Set(ref _chapterTitle, value))
            {
                Raise(nameof(BreadcrumbText));
            }
        }
    }

    public string? BookId => _bookId;

    public string? ChapterId => _chapterId;

    public string BreadcrumbText
    {
        get
        {
            var book = string.IsNullOrWhiteSpace(BookTitle) ? "（未选择作品）" : BookTitle;
            var chapter = string.IsNullOrWhiteSpace(ChapterTitle) ? "（未选择章节）" : ChapterTitle;
            var page = CurrentPageItem is { } item ? $"第 {item.Index + 1} 页" : "—";
            return $"{book} › {chapter} › {page}";
        }
    }

    public int PageCount => Pages.Count;

    public string PageCounterText => Pages.Count == 0
        ? "— / —"
        : $"{CurrentPageIndex + 1:00} / {Pages.Count:00}";

    public int CurrentPageIndex
    {
        get
        {
            for (var index = 0; index < Pages.Count; index++)
            {
                if (Pages[index].IsCurrent)
                {
                    return index;
                }
            }

            return -1;
        }
    }

    public StudioFilmPageItem? CurrentPageItem =>
        Pages.FirstOrDefault(page => page.IsCurrent);

    public string? CurrentPageId => CurrentPageItem?.PageId ?? Selection.CurrentPageId;

    public RegionPageSize? PageSize => _projection?.PageSize;

    public string PageSizeText => PageSize is { } size ? $"{size.Width}×{size.Height}" : "—";

    public byte[]? PageImageBytes => _pageImageBytes;

    public bool HasPageImage => _pageImageBytes is { Length: > 0 };

    public bool PageImageMissing => _pageImageMissing;

    /// <summary>True when the page image read failed while regions loaded (partial).</summary>
    public bool IsPageImageUnavailable => PageImageMissing;

    public string PageImageNote => _pageImageBytes is { Length: > 0 }
        ? string.Empty
        : _isLoadingPage
            ? "正在读取页面图…"
            : "页面图不可用";

    public int RegionCount => Regions.Count;

    public string RegionCountText => Regions.Count == 0 ? "无 Region" : $"{Regions.Count} 个 Region";

    public StudioRegionItem? SelectedRegion
    {
        get => _selectedRegion;
        private set
        {
            if (ReferenceEquals(_selectedRegion, value))
            {
                return;
            }

            if (_selectedRegion is not null)
            {
                _selectedRegion.IsSelected = false;
            }

            _selectedRegion = value;
            if (_selectedRegion is not null)
            {
                _selectedRegion.IsSelected = true;
                Selection.CurrentRegionId = _selectedRegion.RegionId;
            }
            else
            {
                Selection.CurrentRegionId = null;
            }

            Raise();
            Raise(nameof(HasSelectedRegion));
            Raise(nameof(SelectedRegionSummary));
            Raise(nameof(SelectedRegionDetail));
            Raise(nameof(HudVisible));
            UpdateHudSlots();
            Raise(nameof(Inspector));
            CanvasInvalidated?.Invoke(this, EventArgs.Empty);
        }
    }

    public bool HasSelectedRegion => _selectedRegion is not null;

    public string SelectedRegionSummary => _selectedRegion?.DisplayLabel ?? "未选择 Region";

    public string SelectedRegionDetail => _selectedRegion is { } region
        ? $"{region.ShortLabel} · {region.RegionType} · {region.OriginLabel} · rev {region.RevisionNo} · sfx {region.SfxPolicy}"
        : "在画布或胶片条上选择一个 Region";

    public StudioSurfaceMode SurfaceMode
    {
        get => Selection.SurfaceMode;
        set
        {
            if (Selection.SurfaceMode == value)
            {
                return;
            }

            Selection.SurfaceMode = value;
            Raise();
            Raise(nameof(SurfaceModeIndex));
            Raise(nameof(SurfaceModeLabel));
            Raise(nameof(SurfaceModeNote));
            CanvasInvalidated?.Invoke(this, EventArgs.Empty);
        }
    }

    public int SurfaceModeIndex => (int)SurfaceMode;

    public string SurfaceModeLabel => SurfaceMode switch
    {
        StudioSurfaceMode.Page => "页面",
        StudioSurfaceMode.Final => "成品",
        StudioSurfaceMode.Split => "分屏",
        _ => "页面",
    };

    public string SurfaceModeNote => SurfaceMode switch
    {
        StudioSurfaceMode.Page => "页面：原图 + Region 覆盖",
        StudioSurfaceMode.Final => "成品：渲染结果（成品预览读取待接入）",
        StudioSurfaceMode.Split => "分屏：原图 / 成品对照（成品预览读取待接入）",
        _ => string.Empty,
    };

    /// <summary>成品/分屏 need the rendered page resource read, which is not on the frozen face yet.</summary>
    public bool FinalSurfaceNotWired => SurfaceMode != StudioSurfaceMode.Page;

    public bool FilmStripExpanded
    {
        get => Selection.FilmStripExpanded;
        set
        {
            if (Selection.FilmStripExpanded == value)
            {
                return;
            }

            Selection.FilmStripExpanded = value;
            Raise();
            Raise(nameof(FilmStripWidth));
        }
    }

    /// <summary>56 collapsed / 200 expanded (contract §2.2 <c>Nm.Size.FilmStrip*</c>).</summary>
    public double FilmStripWidth => FilmStripExpanded ? 200 : 56;

    public bool InspectorExpanded
    {
        get => Selection.InspectorExpanded;
        set
        {
            if (Selection.InspectorExpanded == value)
            {
                return;
            }

            Selection.InspectorExpanded = value;
            Raise();
            Raise(nameof(InspectorToggleLabel));
            Raise(nameof(InspectorToggleTooltip));
        }
    }

    public string InspectorToggleLabel => InspectorExpanded ? "›" : "‹";

    /// <summary>40 collapsed (icon rail) / 320 expanded (contract §2.2 Inspector sizes).</summary>
    public double InspectorWidth => InspectorExpanded ? 320 : 40;

    public string InspectorToggleTooltip => InspectorExpanded ? "收起检查器（40px）" : "展开检查器（320px）";

    // ---------------------------------------------------------------- zoom / pan

    public double Zoom => Selection.Zoom;

    public string ZoomText => StudioCoordinates.ZoomLabel(Zoom);

    public double ContentWidth => StudioCoordinates.ContentSize(PageSize, Zoom).Width;

    public double ContentHeight => StudioCoordinates.ContentSize(PageSize, Zoom).Height;

    public double OffsetX => Selection.OffsetX;

    public double OffsetY => Selection.OffsetY;

    public bool CanFitWindow => _viewportWidth > 0 && _viewportHeight > 0;

    // ---------------------------------------------------------------- HUD

    public bool HudVisible => HasSelectedRegion && SelectedRegion is { HasGeometry: true };

    public int HudFocusIndex => _hudFocusIndex;

    public StudioHudSlotViewModel? FocusedHudSlot =>
        _hudFocusIndex >= 0 && _hudFocusIndex < HudSlots.Count ? HudSlots[_hudFocusIndex] : null;

    public string HudFocusText => FocusedHudSlot is { } slot
        ? $"{slot.Position} · {slot.Label}"
        : "Tab 选择 HUD 动作";

    // ---------------------------------------------------------------- pipeline band

    public bool PipelineWired => RunSource.IsWired;

    public bool PipelineExpanded { get; private set; }

    public string PipelineHeaderText
    {
        get
        {
            if (_runProjection is { } projection)
            {
                return $"{projection.Title} · {projection.CompletedPageCount}/{projection.TotalPageCount} 页 · {projection.FailedPageCount} 失败";
            }

            return PipelineWired ? "无活动 Run" : "流水线投影未接入 · NOT_WIRED";
        }
    }

    public string PipelineToggleLabel => PipelineExpanded ? "▾ 收起" : "▸ 展开 10 阶段";

    public bool PipelineNotWired => _runProjection is null;

    public string PipelineNotWiredNote =>
        "阶段状态来自 GetTaskProjection（V11R-A-2 未合入）· 当前不显示任何伪造进度";

    // ---------------------------------------------------------------- regions

    public string RegionOverlayNote => _projection?.PageSize is null
        ? "页面尺寸未知：Region 覆盖不可用"
        : $"Region 覆盖以百分比坐标投影到 {PageSizeText}";

    public bool RegionOverlayAvailable => _projection?.PageSize is not null;

    public string RegionDetailsStatus => _isLoadingRegionDetails
        ? "正在读取 Region 历史…"
        : _regionDetailsError is { } error
            ? $"Region 历史读取失败：{error}"
            : string.Empty;

    public bool IsLoadingRegionDetails => _isLoadingRegionDetails;

    public bool HasRegionDetailsError => _regionDetailsError is not null;

    public string? LastRerenderSummary
    {
        get => _lastRerenderSummary;
        private set => Set(ref _lastRerenderSummary, value);
    }

    // ---------------------------------------------------------------- leave guard

    public bool HasUnsavedChanges => Inspector.HasPendingTypeEdit;

    public string UnsavedSummary => Inspector.PendingEditSummary;

    public bool IsLeaveModalOpen
    {
        get => _leaveModalOpen;
        private set => Set(ref _leaveModalOpen, value);
    }

    public string LeaveTitle => "离开前保存更改？";

    public string LeaveBody => HasUnsavedChanges
        ? $"{UnsavedSummary}。保存后写入 Core 并生成新 revision；放弃则丢弃本次修改。"
        : "没有未保存的修改。";

    public string? LeaveError
    {
        get => _leaveError;
        private set
        {
            if (Set(ref _leaveError, value))
            {
                Raise(nameof(HasLeaveError));
            }
        }
    }

    public bool HasLeaveError => !string.IsNullOrEmpty(_leaveError);

    public bool LeaveSaveEnabled => HasUnsavedChanges && Gate.CanExecute(StudioCommand.SetRegionType);

    public string LeaveSaveTooltip => LeaveSaveEnabled
        ? "保存并继续"
        : HasUnsavedChanges
            ? Gate.Tooltip(StudioCommand.SetRegionType)
            : "没有可保存的修改";

    // ---------------------------------------------------------------- load chain

    /// <summary>
    /// AC1: real read chain. <paramref name="bookId"/>/<paramref name="chapterId"/> come from the
    /// shell selection; when omitted the Studio bootstraps from the reader projection (first readable
    /// book/chapter) so it works standalone too.
    /// </summary>
    public async Task<bool> LoadAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default)
    {
        _gate = BuildGate();
        Raise(nameof(Gate));
        Raise(nameof(HostReady));
        Raise(nameof(WritesAllowed));
        Raise(nameof(HostBannerText));
        Raise(nameof(HostBannerVisible));
        ErrorText = null;
        PartialReason = null;
        StatusText = string.Empty;

        if (!_gate.HostReady)
        {
            LoadState = StudioLoadState.Error;
            ErrorText = $"Host 未就绪（{_host.Snapshot.State}）：{_host.Snapshot.StatusLine}";
            return false;
        }

        LoadState = StudioLoadState.Loading;
        try
        {
            if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(chapterId))
            {
                var readerBook = await _host.LoadReaderBookAsync(bookId, chapterId, cancellationToken).ConfigureAwait(true);
                if (readerBook is null)
                {
                    LoadState = StudioLoadState.Empty;
                    StatusText = "没有可打开的作品或章节";
                    return false;
                }

                bookId = readerBook.BookId;
                chapterId = readerBook.ChapterId;
                BookTitle ??= readerBook.BookTitle;
                ChapterTitle ??= readerBook.ChapterTitle;
            }

            _bookId = bookId;
            _chapterId = chapterId;
            Selection.BookId = bookId;
            Selection.ChapterId = chapterId;
            BookTitle = ResolveBookTitle(bookId);
            await LoadChaptersAsync(bookId, chapterId, cancellationToken).ConfigureAwait(true);

            var chapterPages = await _host.ListChapterPagesAsync(chapterId, cancellationToken).ConfigureAwait(true);
            Pages.Clear();
            for (var index = 0; index < chapterPages.Count; index++)
            {
                Pages.Add(new StudioFilmPageItem(chapterPages[index], index));
            }

            if (Pages.Count == 0)
            {
                LoadState = StudioLoadState.Empty;
                StatusText = "本章还没有页面";
                Raise(nameof(PageCount));
                Raise(nameof(PageCounterText));
                Raise(nameof(BreadcrumbText));
                return false;
            }

            Raise(nameof(PageCount));
            Raise(nameof(BreadcrumbText));

            var targetPageId = Selection.CurrentPageId;
            if (targetPageId is null || Pages.All(page => page.PageId != targetPageId))
            {
                targetPageId = Pages[0].PageId;
            }

            var loaded = await LoadPageCoreAsync(targetPageId, cancellationToken).ConfigureAwait(true);
            LoadState = loaded == false ? StudioLoadState.Error : StudioLoadState.Ready;
            await RefreshRunProjectionAsync(cancellationToken).ConfigureAwait(true);
            _ = LoadThumbnailsAsync(cancellationToken);
            return loaded;
        }
        catch (OperationCanceledException)
        {
            LoadState = StudioLoadState.Idle;
            return false;
        }
    }

    /// <summary>Reloads the current page (after a page-level action). Keeps zoom/pan and selection.</summary>
    public async Task<bool> RefreshPageAsync(CancellationToken cancellationToken = default)
    {
        var pageId = CurrentPageId;
        return pageId is null || await LoadPageCoreAsync(pageId, cancellationToken).ConfigureAwait(true) is false
            ? false
            : true;
    }

    private async Task LoadChaptersAsync(string bookId, string chapterId, CancellationToken cancellationToken)
    {
        var chapters = await _host.ListChaptersAsync(bookId, cancellationToken).ConfigureAwait(true);
        var current = chapters.FirstOrDefault(chapter =>
            string.Equals(chapter.ChapterId, chapterId, StringComparison.Ordinal));
        if (current is not null && string.IsNullOrWhiteSpace(ChapterTitle))
        {
            ChapterTitle = current.Title;
        }

        Raise(nameof(BreadcrumbText));
    }

    private string? ResolveBookTitle(string? bookId)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            return BookTitle;
        }

        var book = _host.Snapshot.Books.FirstOrDefault(item =>
            string.Equals(item.BookId, bookId, StringComparison.Ordinal));
        return book?.Title ?? BookTitle;
    }

    /// <summary>
    /// AC1/AC3: page image + <c>list_regions</c> in one pass. The two reads are independent: one can
    /// fail and the page still renders the other (partial state), with a banner and a retry.
    /// </summary>
    private async Task<bool> LoadPageCoreAsync(string pageId, CancellationToken cancellationToken)
    {
        var generation = ++_loadGeneration;
        _isLoadingPage = true;
        Raise(nameof(PageImageNote));
        Raise(nameof(IsLoadingRegionDetails));

        var projectionTask = _host.LoadPageRegionsAsync(pageId, cancellationToken);
        var imageTask = _host.ReadPageImageAsync(pageId, cancellationToken);
        await Task.WhenAll(projectionTask, imageTask).ConfigureAwait(true);
        if (generation != _loadGeneration)
        {
            return false;
        }

        _projection = projectionTask.Result;
        _pageImageBytes = imageTask.Result;
        _pageImageMissing = _projection is not null && !HasPageImage;
        _isLoadingPage = false;

        foreach (var page in Pages)
        {
            page.IsCurrent = string.Equals(page.PageId, pageId, StringComparison.Ordinal);
            page.IsSelected = page.IsCurrent;
        }

        Selection.CurrentPageId = pageId;
        Raise(nameof(CurrentPageIndex));
        Raise(nameof(CurrentPageItem));
        Raise(nameof(CurrentPageId));
        Raise(nameof(PageCounterText));
        Raise(nameof(BreadcrumbText));
        Raise(nameof(PageSize));
        Raise(nameof(PageSizeText));
        Raise(nameof(PageImageBytes));
        Raise(nameof(HasPageImage));
        Raise(nameof(PageImageMissing));
        Raise(nameof(IsPageImageUnavailable));
        Raise(nameof(PageImageNote));
        Raise(nameof(RegionOverlayAvailable));
        Raise(nameof(RegionOverlayNote));
        Raise(nameof(ContentWidth));
        Raise(nameof(ContentHeight));
        ReclampOffsets();
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);

        if (_projection is null && !HasPageImage)
        {
            LoadState = StudioLoadState.Error;
            ErrorText = $"页面读取失败（{pageId}）：Region 与页面图均不可用";
            PartialReason = null;
            return false;
        }

        if (_projection is null)
        {
            LoadState = StudioLoadState.Partial;
            PartialReason = "Region 列表读取失败：可查看页面图，Region 覆盖暂不可用";
            ReplaceRegions(Array.Empty<RegionSummary>());
            return true;
        }

        if (!HasPageImage)
        {
            LoadState = StudioLoadState.Partial;
            PartialReason = "页面图读取失败：Region 仍可查看，重新读取后恢复图像";
        }
        else if (LoadState != StudioLoadState.Loading)
        {
            LoadState = StudioLoadState.Ready;
            PartialReason = null;
        }

        ReplaceRegions(_projection.Regions);
        return true;
    }

    private void ReplaceRegions(IReadOnlyList<RegionSummary> rows)
    {
        var previousId = SelectedRegion?.RegionId;
        Regions.Clear();
        for (var index = 0; index < rows.Count; index++)
        {
            var item = new StudioRegionItem(rows[index], _projection?.PageSize);
            item.SetOrder(index + 1);
            Regions.Add(item);
        }

        Raise(nameof(RegionCount));
        Raise(nameof(RegionCountText));

        var match = previousId is null
            ? null
            : Regions.FirstOrDefault(region => string.Equals(region.RegionId, previousId, StringComparison.Ordinal));
        _selectedRegion = null;
        SelectedRegion = match ?? Regions.FirstOrDefault();
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
        _ = LoadSelectedRegionDetailsAsync();
    }

    // ---------------------------------------------------------------- selection

    /// <summary>
    /// Fire-and-forget selection entry point for the film strip. Returns false when the unsaved-change
    /// guard intercepted the navigation (the modal is then open and continues on 保存/放弃).
    /// </summary>
    public bool RequestSelectPage(string pageId)
    {
        if (string.Equals(pageId, CurrentPageId, StringComparison.Ordinal))
        {
            return true;
        }

        if (HasUnsavedChanges)
        {
            _pendingNavigation = () => LoadPageCoreAsync(pageId, CancellationToken.None);
            OpenLeaveModal();
            return false;
        }

        _ = SelectPageAsync(pageId);
        return true;
    }

    /// <summary>Guard-aware page switch used by views (awaitable, returns false when intercepted).</summary>
    public async Task<bool> SelectPageAsync(string pageId, CancellationToken cancellationToken = default)
    {
        if (string.Equals(pageId, CurrentPageId, StringComparison.Ordinal))
        {
            return true;
        }

        if (HasUnsavedChanges)
        {
            _pendingNavigation = () => LoadPageCoreAsync(pageId, CancellationToken.None);
            OpenLeaveModal();
            return false;
        }

        LoadState = StudioLoadState.Loading;
        await LoadPageCoreAsync(pageId, cancellationToken).ConfigureAwait(true);
        return true;
    }

    public void SelectRegion(StudioRegionItem? region)
    {
        SelectedRegion = region;
        if (region is not null)
        {
            _ = LoadSelectedRegionDetailsAsync();
        }
    }

    public void SelectRegionById(string? regionId)
    {
        if (string.IsNullOrEmpty(regionId))
        {
            return;
        }

        var match = Regions.FirstOrDefault(region => string.Equals(region.RegionId, regionId, StringComparison.Ordinal));
        if (match is not null)
        {
            SelectRegion(match);
        }
    }

    public void HoverRegion(StudioRegionItem? region)
    {
        foreach (var item in Regions)
        {
            item.IsHovered = ReferenceEquals(item, region);
        }

        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
    }

    public void MoveRegionSelection(int delta)
    {
        if (Regions.Count == 0)
        {
            return;
        }

        var index = SelectedRegion is null ? -1 : Regions.IndexOf(SelectedRegion);
        var next = Math.Clamp(index + delta, 0, Regions.Count - 1);
        SelectRegion(Regions[next]);
    }

    public async Task MovePageAsync(int delta, CancellationToken cancellationToken = default)
    {
        var index = CurrentPageIndex;
        if (index < 0)
        {
            return;
        }

        var next = Math.Clamp(index + delta, 0, Pages.Count - 1);
        if (next != index)
        {
            await SelectPageAsync(Pages[next].PageId, cancellationToken).ConfigureAwait(true);
        }
    }

    // ---------------------------------------------------------------- region details (text/locks/history)

    /// <summary>
    /// Loads the selected region's revision history (frozen read face) plus the two not-wired read
    /// seams (text tiers / locks). Every failure is typed and rendered in place; nothing throws.
    /// </summary>
    public async Task LoadSelectedRegionDetailsAsync(CancellationToken cancellationToken = default)
    {
        var region = SelectedRegion;
        if (region is null)
        {
            Inspector.Refresh(null);
            return;
        }

        _isLoadingRegionDetails = true;
        _regionDetailsError = null;
        Raise(nameof(RegionDetailsStatus));
        Raise(nameof(IsLoadingRegionDetails));
        Raise(nameof(HasRegionDetailsError));
        Inspector.BeginHistoryLoad();

        try
        {
            var textTask = TextSource.IsWired
                ? TextSource.LoadAsync(region.RegionId, cancellationToken)
                : Task.FromResult<RegionTextTiers?>(null);
            var flagsTask = FlagSource.IsWired
                ? FlagSource.LoadAsync(region.RegionId, cancellationToken)
                : Task.FromResult<RegionFlags?>(null);
            var historyTask = _host.LoadRegionRevisionsAsync(region.RegionId, cancellationToken);
            await Task.WhenAll(textTask, flagsTask, historyTask).ConfigureAwait(true);

            if (!ReferenceEquals(SelectedRegion, region))
            {
                return;
            }

            var tiers = textTask.Result;
            var flags = flagsTask.Result;
            var history = historyTask.Result;
            region.IsLocked = flags?.RegionLocked ?? false;
            region.HasFailed = flags?.Failed ?? false;
            if (history is not null)
            {
                region.SetReviewState(StudioStates.FromReviewState(
                    history.Revisions.FirstOrDefault(item => item.IsCurrent)?.ReviewState));
            }

            Inspector.Refresh(tiers, flags, history?.Revisions);
            Inspector.EndHistoryLoad(history is null ? "list_region_revisions 读取失败" : null);
            if (history is null)
            {
                _regionDetailsError = "list_region_revisions 读取失败";
            }
        }
        catch (OperationCanceledException)
        {
            Inspector.EndHistoryLoad(null);
        }
        finally
        {
            _isLoadingRegionDetails = false;
            Raise(nameof(RegionDetailsStatus));
            Raise(nameof(IsLoadingRegionDetails));
            Raise(nameof(HasRegionDetailsError));
            Raise(nameof(RegionCountText));
            CanvasInvalidated?.Invoke(this, EventArgs.Empty);
        }
    }

    // ---------------------------------------------------------------- writes (only the wired three)

    /// <summary>AC2: commits the pending region-type edit through <c>set_region_type</c>.</summary>
    public async Task<RegionOperationResult?> ApplyRegionTypeAsync(CancellationToken cancellationToken = default)
    {
        var region = SelectedRegion;
        var newType = Inspector.PendingRegionType;
        if (region is null || newType is null)
        {
            return null;
        }

        if (!Gate.CanExecute(StudioCommand.SetRegionType))
        {
            var refusal = !Gate.HostReady
                ? RegionOperationResult.NotReady()
                : !Gate.WritesAllowed
                    ? RegionOperationResult.ReadOnly()
                    : RegionOperationResult.Failed("CAPABILITY_NOT_WIRED", StudioCapabilityGate.NotWiredTooltip);
            StatusText = refusal.Message ?? "类型修改不可用";
            return refusal;
        }

        var result = await _host.SetRegionTypeAsync(region.RegionId, newType, region.RevisionNo, cancellationToken)
            .ConfigureAwait(true);
        if (result.IsSuccess)
        {
            Inspector.ClearPendingAfterSave();
            StatusText = result.Message ?? $"类型已更新为 {result.RegionType}";
            await RefreshPageAsync(cancellationToken).ConfigureAwait(true);
        }
        else
        {
            StatusText = $"类型修改失败：{result.ErrorCode}";
            LeaveError = StatusText;
        }

        return result;
    }

    /// <summary>AC2: restores one revision (new revision appended, history never overwritten).</summary>
    public async Task<RegionOperationResult?> RestoreRevisionAsync(int revisionNo, CancellationToken cancellationToken = default)
    {
        var region = SelectedRegion;
        if (region is null)
        {
            return null;
        }

        if (!Gate.CanExecute(StudioCommand.RestoreRevision))
        {
            var refusal = !Gate.HostReady
                ? RegionOperationResult.NotReady()
                : RegionOperationResult.ReadOnly();
            StatusText = refusal.Message ?? "恢复不可用";
            return refusal;
        }

        var result = await _host
            .RestoreRegionRevisionAsync(region.RegionId, revisionNo, region.RevisionNo, cancellationToken)
            .ConfigureAwait(true);
        StatusText = result.IsSuccess
            ? result.Message ?? $"已恢复 revision {revisionNo}"
            : $"恢复失败：{result.ErrorCode}";
        if (result.IsSuccess)
        {
            await RefreshPageAsync(cancellationToken).ConfigureAwait(true);
            await LoadSelectedRegionDetailsAsync(cancellationToken).ConfigureAwait(true);
        }

        return result;
    }

    /// <summary>AC2: manual page rerender through <c>rerender_page</c>.</summary>
    public async Task<PageRerenderOutcome?> RerenderPageAsync(CancellationToken cancellationToken = default)
    {
        var pageId = CurrentPageId;
        if (pageId is null)
        {
            return null;
        }

        if (!Gate.CanExecute(StudioCommand.RerenderPage))
        {
            var refusal = !Gate.HostReady ? PageRerenderOutcome.NotReady() : PageRerenderOutcome.ReadOnly();
            StatusText = refusal.Message ?? "重渲染不可用";
            return refusal;
        }

        var outcome = await _host.RerenderPageAsync(pageId, cancellationToken).ConfigureAwait(true);
        LastRerenderSummary = outcome.IsSuccess
            ? outcome.Message ?? "重渲染完成"
            : $"重渲染失败：{outcome.ErrorCode}";
        StatusText = LastRerenderSummary;
        if (outcome.IsSuccess)
        {
            await RefreshPageAsync(cancellationToken).ConfigureAwait(true);
        }

        Raise(nameof(LastRerenderSummary));
        return outcome;
    }

    /// <summary>Refreshes the pipeline band from the run data source (NOT_WIRED today).</summary>
    public async Task RefreshRunProjectionAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _runProjection = RunSource.IsWired
                ? await RunSource.GetProjectionAsync(_chapterId, cancellationToken).ConfigureAwait(true)
                : null;
        }
        catch (OperationCanceledException)
        {
            return;
        }

        RefreshPipelineBand();
    }

    private void RefreshPipelineBand()
    {
        var mapped = StudioRunStageMapper.MapBandStages(_runProjection);
        for (var index = 0; index < PipelineStages.Count; index++)
        {
            PipelineStages[index].State = mapped[index].State;
        }

        Raise(nameof(PipelineWired));
        Raise(nameof(PipelineHeaderText));
        Raise(nameof(PipelineNotWired));
        Raise(nameof(PipelineNotWiredNote));
    }

    public void TogglePipelineExpanded()
    {
        PipelineExpanded = !PipelineExpanded;
        Raise(nameof(PipelineExpanded));
        Raise(nameof(PipelineToggleLabel));
    }

    // ---------------------------------------------------------------- zoom / pan operations

    public void SetViewportSize(double width, double height)
    {
        _viewportWidth = width;
        _viewportHeight = height;
        ReclampOffsets();
        Raise(nameof(CanFitWindow));
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>
    /// Re-clamps (or centres) the pan offset for the current viewport and page extent. Called when the
    /// viewport is measured, the page changes, or the zoom changes; keeps the page reachable.
    /// </summary>
    private void ReclampOffsets()
    {
        var (width, height) = StudioCoordinates.ContentSize(PageSize, Zoom);
        var (offsetX, offsetY) = StudioCoordinates.ClampOffset(
            Selection.OffsetX, Selection.OffsetY, width, height, _viewportWidth, _viewportHeight);
        Selection.OffsetX = offsetX;
        Selection.OffsetY = offsetY;
    }

    public void ZoomIn() => SetZoom(StudioCoordinates.ZoomIn(Zoom));

    public void ZoomOut() => SetZoom(StudioCoordinates.ZoomOut(Zoom));

    public void ResetZoom() => SetZoom(StudioCoordinates.DefaultZoom);

    public void FitWindow()
    {
        if (!CanFitWindow)
        {
            return;
        }

        var (zoom, offsetX, offsetY) = StudioCoordinates.FitAndCenter(
            _viewportWidth, _viewportHeight, PageSize);
        Selection.Zoom = zoom;
        Selection.OffsetX = offsetX;
        Selection.OffsetY = offsetY;
        Raise(nameof(ZoomText));
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Wheel zoom anchored at the pointer (AC): the content point under the cursor stays put.</summary>
    public void HandleWheel(int notches, double pointerX, double pointerY)
    {
        var next = StudioCoordinates.ApplyWheelZoom(Zoom, notches);
        if (Math.Abs(next - Zoom) < 0.0001)
        {
            return;
        }

        var (offsetX, offsetY) = StudioCoordinates.ZoomAroundPoint(
            Selection.OffsetX, Selection.OffsetY, pointerX, pointerY, Zoom, next);
        var (width, height) = StudioCoordinates.ContentSize(PageSize, next);
        (offsetX, offsetY) = StudioCoordinates.ClampOffset(
            offsetX, offsetY, width, height, _viewportWidth, _viewportHeight);
        Selection.Zoom = next;
        Selection.OffsetX = offsetX;
        Selection.OffsetY = offsetY;
        Raise(nameof(ZoomText));
        Raise(nameof(ContentWidth));
        Raise(nameof(ContentHeight));
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Drag pan; the offset is clamped so the page cannot leave the viewport.</summary>
    public void PanBy(double deltaX, double deltaY)
    {
        var (width, height) = StudioCoordinates.ContentSize(PageSize, Zoom);
        var (offsetX, offsetY) = StudioCoordinates.ClampOffset(
            Selection.OffsetX + deltaX,
            Selection.OffsetY + deltaY,
            width,
            height,
            _viewportWidth,
            _viewportHeight);
        Selection.OffsetX = offsetX;
        Selection.OffsetY = offsetY;
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
    }

    private void SetZoom(double zoom)
    {
        var next = StudioCoordinates.ClampZoom(zoom);
        if (Math.Abs(next - Zoom) < 0.0001)
        {
            return;
        }

        var (offsetX, offsetY) = StudioCoordinates.ZoomAroundPoint(
            Selection.OffsetX, Selection.OffsetY,
            _viewportWidth / 2, _viewportHeight / 2,
            Zoom, next);
        var (width, height) = StudioCoordinates.ContentSize(PageSize, next);
        (offsetX, offsetY) = StudioCoordinates.ClampOffset(
            offsetX, offsetY, width, height, _viewportWidth, _viewportHeight);
        Selection.Zoom = next;
        Selection.OffsetX = offsetX;
        Selection.OffsetY = offsetY;
        Raise(nameof(ZoomText));
        Raise(nameof(ContentWidth));
        Raise(nameof(ContentHeight));
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
    }

    // ---------------------------------------------------------------- HUD ring

    /// <summary>AC: <c>Tab</c> cycles the ring; disabled slots are skipped.</summary>
    public void CycleHud(int direction)
    {
        var next = StudioHudRing.Cycle(
            _hudFocusIndex,
            direction,
            slot => slot.Command is null || Gate.CanExecute(slot.Command.Value));
        SetHudFocus(next);
    }

    public void SetHudFocus(int index)
    {
        if (_hudFocusIndex == index && index >= 0 && index < HudSlots.Count)
        {
            UpdateHudSlots();
            return;
        }

        _hudFocusIndex = index;
        for (var slotIndex = 0; slotIndex < HudSlots.Count; slotIndex++)
        {
            HudSlots[slotIndex].IsFocused = slotIndex == index;
        }

        Raise(nameof(HudFocusIndex));
        Raise(nameof(FocusedHudSlot));
        Raise(nameof(HudFocusText));
    }

    /// <summary>AC: <c>Enter</c> executes the focused slot. Returns false for NOT_WIRED actions.</summary>
    public async Task<bool> ExecuteFocusedHudAsync(CancellationToken cancellationToken = default)
    {
        var slot = FocusedHudSlot;
        if (slot is null || !slot.IsEnabled)
        {
            var blocked = slot is null ? "先选择一个 HUD 动作" : slot.Tooltip;
            StatusText = blocked;
            return false;
        }

        switch (slot.Action)
        {
            case StudioHudAction.ShowTextTier:
                Inspector.ActiveTab = StudioInspectorTab.Text;
                return true;
            case StudioHudAction.ShowStyle:
                Inspector.ActiveTab = StudioInspectorTab.Style;
                return true;
            case StudioHudAction.ShowHistory:
                Inspector.ActiveTab = StudioInspectorTab.History;
                await LoadSelectedRegionDetailsAsync(cancellationToken).ConfigureAwait(true);
                return true;
            case StudioHudAction.RerenderPage:
                await RerenderPageAsync(cancellationToken).ConfigureAwait(true);
                return true;
            case StudioHudAction.RestorePreviousRevision:
            {
                var previous = Inspector.Revisions
                    .Where(revision => !revision.IsCurrent)
                    .OrderByDescending(revision => revision.RevisionNo)
                    .FirstOrDefault();
                if (previous is null)
                {
                    StatusText = "没有可恢复的历史版本";
                    return false;
                }

                await RestoreRevisionAsync(previous.RevisionNo, cancellationToken).ConfigureAwait(true);
                return true;
            }

            default:
                StatusText = StudioCapabilityGate.NotWiredTooltip;
                NotWiredAttempted?.Invoke(this, $"{slot.Label}：{StudioCapabilityGate.NotWiredTooltip}");
                return false;
        }
    }

    private void UpdateHudSlots()
    {
        foreach (var slot in HudSlots)
        {
            var command = slot.Slot.Command;
            var enabled = command is null || Gate.CanExecute(command.Value);
            slot.IsEnabled = enabled;
            slot.Tooltip = enabled
                ? slot.Label
                : Gate.Tooltip(command!.Value);
        }

        if (_hudFocusIndex >= HudSlots.Count)
        {
            _hudFocusIndex = -1;
        }

        Raise(nameof(HudVisible));
        Raise(nameof(HudFocusText));
    }

    // ---------------------------------------------------------------- thumbnails

    /// <summary>
    /// Loads real page images as strip thumbnails through the Host resource channel. Sequential and
    /// capped (<see cref="ThumbnailLimit"/>) so a 240-page chapter cannot flood the channel.
    /// </summary>
    public async Task LoadThumbnailsAsync(CancellationToken cancellationToken = default)
    {
        var count = Math.Min(Pages.Count, ThumbnailLimit);
        for (var index = 0; index < count; index++)
        {
            if (cancellationToken.IsCancellationRequested)
            {
                return;
            }

            var item = Pages[index];
            if (item.HasThumbnail)
            {
                continue;
            }

            try
            {
                var bytes = await _host.ReadPageImageAsync(item.PageId, cancellationToken).ConfigureAwait(true);
                item.ThumbnailBytes = bytes;
            }
            catch (OperationCanceledException)
            {
                return;
            }
        }
    }

    // ---------------------------------------------------------------- leave guard

    public void OpenLeaveModal()
    {
        LeaveError = null;
        IsLeaveModalOpen = true;
        Raise(nameof(LeaveBody));
        Raise(nameof(LeaveSaveEnabled));
        Raise(nameof(LeaveSaveTooltip));
    }

    public void CloseLeaveModal()
    {
        IsLeaveModalOpen = false;
        LeaveError = null;
        _pendingNavigation = null;
    }

    /// <summary>
    /// AC: the unsaved-changes modal with three exits. 保存 writes through the wired
    /// <c>set_region_type</c>; 放弃 drops the pending edit; 取消 returns and keeps the edit.
    /// </summary>
    public async Task<StudioLeaveOutcome> ResolveLeaveAsync(
        StudioLeaveChoice choice,
        CancellationToken cancellationToken = default)
    {
        var navigation = _pendingNavigation;
        switch (choice)
        {
            case StudioLeaveChoice.Cancel:
                CloseLeaveModal();
                return StudioLeaveOutcome.Cancelled;

            case StudioLeaveChoice.Discard:
                Inspector.DiscardPendingType();
                IsLeaveModalOpen = false;
                LeaveError = null;
                _pendingNavigation = null;
                Raise(nameof(LeaveBody));
                if (navigation is not null)
                {
                    await navigation().ConfigureAwait(true);
                }

                return StudioLeaveOutcome.Discarded;

            case StudioLeaveChoice.Save:
            default:
                if (!HasUnsavedChanges)
                {
                    CloseLeaveModal();
                    if (navigation is not null)
                    {
                        await navigation().ConfigureAwait(true);
                    }

                    return StudioLeaveOutcome.NoChanges;
                }

                if (!LeaveSaveEnabled)
                {
                    LeaveError = LeaveSaveTooltip;
                    return StudioLeaveOutcome.SaveFailed;
                }

                var result = await ApplyRegionTypeAsync(cancellationToken).ConfigureAwait(true);
                if (result is null || !result.IsSuccess)
                {
                    LeaveError = result?.ErrorCode is { } code
                        ? $"保存失败：{code}"
                        : "保存失败";
                    return StudioLeaveOutcome.SaveFailed;
                }

                IsLeaveModalOpen = false;
                LeaveError = null;
                _pendingNavigation = null;
                Raise(nameof(LeaveBody));
                if (navigation is not null)
                {
                    await navigation().ConfigureAwait(true);
                }

                return StudioLeaveOutcome.Saved;
        }
    }

    /// <summary>Guard used by the shell before leaving the Studio space. Returns false when a modal opened.</summary>
    public bool TryBeginLeave()
    {
        if (!HasUnsavedChanges)
        {
            return true;
        }

        OpenLeaveModal();
        return false;
    }

    // ---------------------------------------------------------------- misc

    private StudioCapabilityGate BuildGate()
    {
        var snapshot = _host.Snapshot;
        var ready = snapshot.State == HostViewState.Ready;
        return new StudioCapabilityGate(ready, ready && snapshot.WritesAllowed);
    }

    private void OnSelectionChanged(object? sender, EventArgs e)
    {
        Raise(nameof(Zoom));
        Raise(nameof(ZoomText));
        Raise(nameof(OffsetX));
        Raise(nameof(OffsetY));
        Raise(nameof(ContentWidth));
        Raise(nameof(ContentHeight));
        Raise(nameof(SurfaceMode));
        Raise(nameof(SurfaceModeIndex));
        Raise(nameof(SurfaceModeLabel));
        Raise(nameof(SurfaceModeNote));
        Raise(nameof(FinalSurfaceNotWired));
        Raise(nameof(FilmStripExpanded));
        Raise(nameof(FilmStripWidth));
        Raise(nameof(InspectorExpanded));
        Raise(nameof(InspectorToggleLabel));
        Raise(nameof(InspectorToggleTooltip));
        CanvasInvalidated?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Evidence helper: the exact NOT_WIRED capability list of this build.</summary>
    public IReadOnlyList<string> BuildNotWiredInventory()
    {
        var items = new List<string>();
        foreach (var command in Enum.GetValues<StudioCommand>())
        {
            if (!StudioCapabilityGate.IsWired(command))
            {
                items.Add($"{command}: {StudioCapabilityGate.NotWiredTooltip}");
            }
        }

        if (!RunSource.IsWired)
        {
            items.Add("IRunDataSource: NOT_WIRED（GetTaskProjection / V11R-A-2 未合入）");
        }

        if (!TextSource.IsWired)
        {
            items.Add("IRegionTextSource: NOT_WIRED（四级文本读取命令不存在）");
        }

        if (!FlagSource.IsWired)
        {
            items.Add("IRegionFlagSource: NOT_WIRED（四把锁 / 失败角标读取命令不存在）");
        }

        items.Add("PageSurface.Final/Split: NOT_WIRED（成品页资源读取命令不存在）");
        NotWiredCapabilities = items;
        Raise(nameof(NotWiredCapabilities));
        return items;
    }
}
