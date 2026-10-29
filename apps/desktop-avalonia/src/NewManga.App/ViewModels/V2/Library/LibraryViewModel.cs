using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.CoreClient;

namespace NewManga.App.ViewModels.V2.Library;

/// <summary>
/// V11R-B-1: the Library space ViewModel (screen spec §2). Owns no second selection — every
/// selection read/write goes through <see cref="ShellState"/>. Data comes exclusively from the
/// existing <see cref="IHostController"/> read faces; import/reader results are typed and honest.
/// </summary>
public sealed class LibraryViewModel : ObservableObject
{
    private const string SortUpdated = "updated";
    private const string SortTitle = "title";
    private const string SortPages = "pages";

    private readonly IHostController _controller;
    private readonly ShellState _state;
    private readonly Action<string, NmStatus> _notify;
    private readonly Action<ConfirmRequest> _requestConfirm;
    private readonly List<BookRowViewModel> _allBooks = new();
    private readonly IReadOnlyList<LibrarySortOption> _sortOptions = new[]
    {
        new LibrarySortOption(SortUpdated, "最近更新"),
        new LibrarySortOption(SortTitle, "标题 A→Z"),
        new LibrarySortOption(SortPages, "页数从多到少"),
    };

    private bool _initialized;
    private bool _isLoading;
    private bool _isChaptersLoading;
    private bool _isPagesLoading;
    private string? _errorMessage;
    private string _statusMessage = string.Empty;
    private bool _isRecycleBinView;
    private bool _isCreateBookOpen;
    private bool _isCreateChapterOpen;
    private bool _isCreatingChapter;
    private string _newChapterTitle = string.Empty;
    private string _newBookTitle = string.Empty;
    private string _detailProgressText = "—";
    private string _detailChapterCountText = "—";
    private string _loadedChapterId = string.Empty;
    private double _cardWidth = 272;
    private double _cardHeight = 354;
    private double _cardGap = 8;
    private double _detailPanelWidth;
    private bool _isNarrowLayout;
    private int _columnCount = 4;

    public LibraryViewModel(
        IHostController controller,
        ShellState state,
        Action<string, NmStatus> notify,
        Action<ConfirmRequest> requestConfirm,
        IFilePickerGateway? picker = null)
    {
        _controller = controller;
        _state = state;
        _notify = notify;
        _requestConfirm = requestConfirm;

        ImportDock = new ImportDockViewModel(
            controller,
            picker,
            notify,
            chapterId: () => SelectedChapter?.ChapterId,
            chapterTitle: () => SelectedChapter?.Title,
            afterImport: ReloadAfterImportAsync,
            requestCreateChapter: ShowCreateChapter);
        Reader = new ReaderOverlayViewModel(controller, notify);

        FilterChips = new ObservableCollection<FilterChipItem>
        {
            new("all", "全部", ToggleFilter),
            new("favorite", "收藏", ToggleFilter),
            new("archived", "已归档", ToggleFilter),
        };

        RefreshCommand = new RelayCommand(() => _ = RefreshAsync());
        ShowRecycleBinCommand = new RelayCommand(ShowRecycleBin);
        CloseRecycleBinCommand = new RelayCommand(CloseRecycleBin);
        NewBookCommand = new RelayCommand(ShowCreateBook);
        CancelCreateBookCommand = new RelayCommand(() => IsCreateBookOpen = false);
        ConfirmCreateBookCommand = new RelayCommand(() => _ = CreateBookAsync());
        ShowCreateChapterCommand = new RelayCommand(ShowCreateChapter);
        CancelCreateChapterCommand = new RelayCommand(() => IsCreateChapterOpen = false);
        ConfirmCreateChapterCommand = new RelayCommand(() => _ = CreateChapterAsync());
        CreateChapterCommand = new RelayCommand(ShowCreateChapter);
        ImportFilesCommand = new RelayCommand(() => _ = ImportDock.PickFilesAsync());
        ImportFolderCommand = new RelayCommand(() => _ = ImportDock.PickFolderAsync());
        OpenReaderCommand = new RelayCommand(() => _ = OpenReaderAsync());
        ClearSelectionCommand = new RelayCommand(() => _state.ClearMultiPage());
        ClearFiltersCommand = new RelayCommand(ClearFilters);
        RecycleRestoreCommand = new RelayCommand(() => RequestRecycleAction("恢复"));
        RecyclePurgeCommand = new RelayCommand(() => RequestRecycleAction("永久删除"));
        ExportSelectionCommand = new RelayCommand(() => _notify(
            "导出：能力待接入（导出预检归 V11R-B-5，旧版导出流程未迁移到 V2）",
            NmStatus.Blocked));
        MarkSelectionCommand = new RelayCommand(() => _notify(
            "标记：能力待接入（Host 未暴露页/书目标记命令）",
            NmStatus.Blocked));
        DeleteSelectionCommand = new RelayCommand(() => _notify(
            "删除：能力待接入（Host 未暴露页/书删除命令，不能用假成功代替）",
            NmStatus.Blocked));

        _state.SelectionChanged += OnSelectionChanged;
        _state.SpaceChanged += (_, _) => ImportDock.NotifyChapterContextChanged();
    }

    public ObservableCollection<BookRowViewModel> Books { get; } = new();

    public ObservableCollection<ChapterRowViewModel> Chapters { get; } = new();

    public ObservableCollection<PageRowViewModel> Pages { get; } = new();

    public ObservableCollection<FilterChipItem> FilterChips { get; }

    public IReadOnlyList<LibrarySortOption> SortOptions => _sortOptions;

    public IReadOnlyList<BookRowViewModel> AllBooks => _allBooks;

    public ImportDockViewModel ImportDock { get; }

    public ReaderOverlayViewModel Reader { get; }

    public RelayCommand RefreshCommand { get; }

    public RelayCommand ShowRecycleBinCommand { get; }

    public RelayCommand CloseRecycleBinCommand { get; }

    public RelayCommand NewBookCommand { get; }

    public RelayCommand CancelCreateBookCommand { get; }

    public RelayCommand ConfirmCreateBookCommand { get; }

    public RelayCommand ShowCreateChapterCommand { get; }

    public RelayCommand CancelCreateChapterCommand { get; }

    public RelayCommand ConfirmCreateChapterCommand { get; }

    public RelayCommand CreateChapterCommand { get; }

    public RelayCommand ImportFilesCommand { get; }

    public RelayCommand ImportFolderCommand { get; }

    public RelayCommand OpenReaderCommand { get; }

    public RelayCommand ClearSelectionCommand { get; }

    public RelayCommand ClearFiltersCommand { get; }

    public RelayCommand RecycleRestoreCommand { get; }

    public RelayCommand RecyclePurgeCommand { get; }

    public RelayCommand ExportSelectionCommand { get; }

    public RelayCommand MarkSelectionCommand { get; }

    public RelayCommand DeleteSelectionCommand { get; }

    // ── Shell-facing state (read from ShellState, never duplicated) ─────────────────────────

    public BookRowViewModel? SelectedBook =>
        _state.Selection.BookId is { } bookId
            ? _allBooks.FirstOrDefault(book => string.Equals(book.BookId, bookId, StringComparison.Ordinal))
            : null;

    public ChapterRowViewModel? SelectedChapter =>
        _state.Selection.ChapterId is { } chapterId
            ? Chapters.FirstOrDefault(chapter => string.Equals(chapter.ChapterId, chapterId, StringComparison.Ordinal))
            : null;

    public PageRowViewModel? SelectedPage =>
        _state.Selection.PageId is { } pageId
            ? Pages.FirstOrDefault(page => string.Equals(page.PageId, pageId, StringComparison.Ordinal))
            : null;

    public bool IsDetailOpen => SelectedBook is not null;

    public bool IsMultiSelectActive => _state.Selection.MultiPageCount > 0;

    public int SelectionCount => _state.Selection.MultiPageCount;

    public string SelectionSummary => IsMultiSelectActive
        ? $"已选 {SelectionCount} 页 · 作用域：{SelectedChapter?.Title ?? "本章"}"
        : "未选择页面";

    // ── View state ─────────────────────────────────────────────────────────────────────────

    public string SearchText
    {
        get => _state.LibraryView.SearchText;
        set
        {
            if (string.Equals(_state.LibraryView.SearchText, value, StringComparison.Ordinal))
            {
                return;
            }

            _state.SetSearch(SpaceId.Library, null, value ?? string.Empty);
            OnPropertyChanged();
            RebuildBooks();
        }
    }

    public int SortIndex
    {
        get
        {
            var key = _state.LibraryView.SortKey;
            if (string.IsNullOrEmpty(key))
            {
                return 0;
            }

            for (var index = 0; index < _sortOptions.Count; index++)
            {
                if (string.Equals(_sortOptions[index].Key, key, StringComparison.Ordinal))
                {
                    return index;
                }
            }

            return 0;
        }
        set
        {
            var clamped = Math.Clamp(value, 0, _sortOptions.Count - 1);
            _state.SetSort(SpaceId.Library, null, _sortOptions[clamped].Key);
            OnPropertyChanged();
            RebuildBooks();
        }
    }

    public string FilterKey
    {
        get
        {
            var key = _state.LibraryView.FilterKey;
            return string.IsNullOrEmpty(key) ? "all" : key;
        }
    }

    // ── V11R-INT-0 workspace context (real ScrollViewer offset, written back by the view) ──────

    /// <summary>Raised when the shell activates this space and the view must restore its scroll offset.</summary>
    public event EventHandler? ScrollRestoreRequested;

    /// <summary>Live offset of the book grid ScrollViewer; the shell persists it per space.</summary>
    public double ScrollOffsetY
    {
        get => _state.LibraryView.ScrollOffsetY;
        set
        {
            if (Math.Abs(_state.LibraryView.ScrollOffsetY - value) < 0.5)
            {
                return;
            }

            _state.LibraryView.ScrollOffsetY = value;
            OnPropertyChanged();
        }
    }

    /// <summary>Contract §6.1 OnDeactivated: flush retained context into the shell state.</summary>
    public void CaptureViewState(SpaceViewState view)
    {
        view.SearchText = SearchText;
        view.SortKey = SortOptions[SortIndex].Key;
        view.FilterKey = FilterKey;
        view.ScrollOffsetY = ScrollOffsetY;
    }

    /// <summary>Contract §6.1 OnActivated: restore the retained scroll offset from the shell state.</summary>
    public void RestoreViewState(SpaceViewState view)
    {
        ScrollOffsetY = view.ScrollOffsetY;
        ScrollRestoreRequested?.Invoke(this, EventArgs.Empty);
    }

    public bool IsLoading
    {
        get => _isLoading;
        private set
        {
            if (Set(ref _isLoading, value))
            {
                RaiseListStates();
            }
        }
    }

    public bool IsChaptersLoading
    {
        get => _isChaptersLoading;
        private set => Set(ref _isChaptersLoading, value);
    }

    public bool IsPagesLoading
    {
        get => _isPagesLoading;
        private set => Set(ref _isPagesLoading, value);
    }

    public string? ErrorMessage
    {
        get => _errorMessage;
        private set
        {
            if (Set(ref _errorMessage, value))
            {
                OnPropertyChanged(nameof(HasError));
                RaiseListStates();
            }
        }
    }

    public bool HasError => !string.IsNullOrWhiteSpace(ErrorMessage);

    /// <summary>
    /// V11R-INT-2 P1: exactly one center block may be visible. Priority (highest first):
    /// HostNotReady → Loading → Error → EmptyLibrary → NoResults → BookGrid.
    /// </summary>
    public bool ShowHostNotReadyState => _initialized && !IsLoading && _controller.Snapshot.State != HostViewState.Ready;

    public bool ShowLoadingState => _initialized && !ShowHostNotReadyState && IsLoading;

    public bool ShowErrorState => _initialized && !ShowHostNotReadyState && !IsLoading && HasError;

    public bool ShowEmptyLibraryState => _initialized && !ShowHostNotReadyState && !IsLoading && !HasError
        && _controller.Snapshot.State == HostViewState.Ready && _allBooks.Count == 0;

    public bool ShowNoResultsState => _initialized && !ShowHostNotReadyState && !IsLoading && !HasError
        && _controller.Snapshot.State == HostViewState.Ready && _allBooks.Count > 0 && Books.Count == 0;

    /// <summary>True when one of the full-surface state blocks is visible (exactly one by construction).</summary>
    public bool ShowEmptyState => ShowHostNotReadyState || ShowErrorState || ShowEmptyLibraryState || ShowNoResultsState;

    // Legacy property names (kept for external bindings/tests); all derive from the exclusive selectors.
    public bool HostNotReady => ShowHostNotReadyState;

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

    public bool IsEmptyLibrary => ShowEmptyLibraryState;

    public bool HasNoResults => ShowNoResultsState;

    public bool IsRecycleBinView
    {
        get => _isRecycleBinView;
        private set
        {
            if (Set(ref _isRecycleBinView, value))
            {
                OnPropertyChanged(nameof(ShowGrid));
            }
        }
    }

    public bool ShowGrid => !IsRecycleBinView;

    /// <summary>Book grid is hidden while the initial Host read is in flight (skeleton takes its place).</summary>
    /// <summary>Book grid is visible only when exactly one data/state block applies (never under a state).</summary>
    public bool ShowBooksGrid => ShowGrid && !ShowHostNotReadyState && !ShowLoadingState && !ShowErrorState
        && !ShowEmptyLibraryState && !ShowNoResultsState;

    public string RecycleCountText => "—";

    public bool IsCreateBookOpen
    {
        get => _isCreateBookOpen;
        private set => Set(ref _isCreateBookOpen, value);
    }

    /// <summary>Inline 新建章节 form (audit F011): real when V11R-A-1 CreateChapterAsync is available.</summary>
    public bool IsCreateChapterOpen
    {
        get => _isCreateChapterOpen;
        private set => Set(ref _isCreateChapterOpen, value);
    }

    public bool IsCreatingChapter
    {
        get => _isCreatingChapter;
        private set => Set(ref _isCreatingChapter, value);
    }

    public string NewChapterTitle
    {
        get => _newChapterTitle;
        set
        {
            if (Set(ref _newChapterTitle, value))
            {
                OnPropertyChanged(nameof(CanCreateChapter));
            }
        }
    }

    public bool CanCreateChapter => !IsCreatingChapter && !string.IsNullOrWhiteSpace(NewChapterTitle) && SelectedBook is not null;

    public string NewBookTitle
    {
        get => _newBookTitle;
        set
        {
            if (Set(ref _newBookTitle, value))
            {
                OnPropertyChanged(nameof(CanCreateBook));
            }
        }
    }

    public bool CanCreateBook => !string.IsNullOrWhiteSpace(NewBookTitle);

    public string DetailTitle => SelectedBook?.Title ?? "未选择作品";

    public string DetailOriginalTitle => SelectedBook?.OriginalTitle ?? string.Empty;

    public bool HasDetailOriginalTitle => DetailOriginalTitle.Length > 0;

    public string DetailMeta => SelectedBook is null
        ? "从左侧选择一本作品，这里显示章节账本、页数与阅读进度。"
        : $"{SelectedBook.MetaText} · {(SelectedBook.IsFavorite ? "收藏" : "未收藏")}{(SelectedBook.IsArchived ? " · 已归档" : string.Empty)}";

    public string DetailChapterCountText => _detailChapterCountText;

    public string DetailPageCountText => SelectedChapter is null
        ? "—"
        : Pages.Count.ToString(System.Globalization.CultureInfo.InvariantCulture) + " 页";

    public string DetailProgressText => _detailProgressText;

    public bool HasChapters => Chapters.Count > 0;

    public bool HasPages => Pages.Count > 0;

    public bool HasSelection => SelectedBook is not null;

    // ── Layout metrics (derived from DS tokens via ShellLayout; XAML carries no raw values) ──

    /// <summary>Search field width (DS tree-width token).</summary>
    public double SearchBoxWidth => ShellLayout.SearchBoxWidth;

    /// <summary>Sort combo width derived from the DS search width.</summary>
    public double SortBoxWidth => ShellLayout.SortBoxWidth;

    /// <summary>True below the 1280 breakpoint: the resident detail panel becomes an overlay (R-18).</summary>
    public bool IsNarrowLayout
    {
        get => _isNarrowLayout;
        private set
        {
            if (Set(ref _isNarrowLayout, value))
            {
                OnPropertyChanged(nameof(IsSideDetailVisible), nameof(IsOverlayDetailVisible));
            }
        }
    }

    public bool IsSideDetailVisible => !IsNarrowLayout;

    public bool IsOverlayDetailVisible => IsNarrowLayout;

    public double CardWidth
    {
        get => _cardWidth;
        private set => Set(ref _cardWidth, value);
    }

    public double CardHeight
    {
        get => _cardHeight;
        private set => Set(ref _cardHeight, value);
    }

    public double CardGap
    {
        get => _cardGap;
        private set
        {
            if (Set(ref _cardGap, value))
            {
                OnPropertyChanged(nameof(CardSlotWidth), nameof(CardSlotHeight));
            }
        }
    }

    public double CardSlotWidth => CardWidth + CardGap;

    public double CardSlotHeight => CardHeight + CardGap;

    public double DetailPanelWidth
    {
        get => _detailPanelWidth;
        private set => Set(ref _detailPanelWidth, value);
    }

    public int ColumnCount
    {
        get => _columnCount;
        private set => Set(ref _columnCount, value);
    }


    public string BookCountText => IsRecycleBinView
        ? "回收站"
        : $"{Books.Count} / {_allBooks.Count} 作品";

    public string ListStatusText => IsLoading
        ? "正在读取书架…"
        : HasError
            ? "读取失败"
            : $"{Books.Count} / {_allBooks.Count} 作品";

    // ── Loading ────────────────────────────────────────────────────────────────────────────

    public async Task InitializeAsync(CancellationToken cancellationToken = default)
    {
        if (_initialized)
        {
            return;
        }

        _initialized = true;
        await RefreshAsync(cancellationToken).ConfigureAwait(true);
    }

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        IsLoading = true;
        ErrorMessage = null;
        try
        {
            await _controller.RefreshBooksAsync(cancellationToken).ConfigureAwait(true);
            var snapshot = _controller.Snapshot;
            _allBooks.Clear();
            if (snapshot.State == HostViewState.Failed)
            {
                ErrorMessage = snapshot.ErrorCode is { Length: > 0 }
                    ? $"Host 启动失败（{snapshot.ErrorCode}）"
                    : "Host 启动失败：书架不可用";
            }
            else
            {
                foreach (var book in snapshot.Books)
                {
                    _allBooks.Add(new BookRowViewModel(book, OnBookSelected));
                }
            }

            var selectionBookId = _state.Selection.BookId;
            RebuildBooks();
            if (snapshot.State == HostViewState.Ready)
            {
                var restore = selectionBookId is null
                    ? null
                    : _allBooks.FirstOrDefault(book => string.Equals(book.BookId, selectionBookId, StringComparison.Ordinal));
                if (restore is not null)
                {
                    await SelectBookAsync(restore).ConfigureAwait(true);
                }
                else if (Books.Count > 0)
                {
                    // First load: land on the first visible book (and its first chapter) so the resident
                    // detail panel is never an empty shell while data exists.
                    await SelectBookAsync(Books[0]).ConfigureAwait(true);
                }
                else
                {
                    _state.ClearSelection();
                    Chapters.Clear();
                    Pages.Clear();
                    _loadedChapterId = string.Empty;
                    RaiseDetailStates();
                }
            }

            StatusMessage = snapshot.State switch
            {
                HostViewState.Ready => $"Host 就绪 · {snapshot.ModeLine}",
                HostViewState.Starting => "Host 正在启动：等待 Core sidecar",
                HostViewState.AlreadyRunning => "Host 已在运行：读取只读投影",
                _ => snapshot.StatusLine,
            };
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            ErrorMessage = "书架读取失败：" + ex.Message;
            _allBooks.Clear();
            RebuildBooks();
        }
        finally
        {
            IsLoading = false;
            OnPropertyChanged(nameof(HostNotReady));
            RaiseListStates();
        }
    }

    // ── Selection (all writes go through ShellState) ───────────────────────────────────────

    public async Task SelectBookAsync(BookRowViewModel? book)
    {
        if (book is null)
        {
            _state.SelectBook(null);
            Chapters.Clear();
            Pages.Clear();
            _loadedChapterId = string.Empty;
            RaiseDetailStates();
            return;
        }

        _state.SelectBook(book.BookId);
        await LoadChaptersAsync(book).ConfigureAwait(true);
    }

    public async Task SelectChapterAsync(ChapterRowViewModel? chapter)
    {
        if (chapter is null || SelectedBook is null)
        {
            _state.SelectChapter(null);
            Pages.Clear();
            _loadedChapterId = string.Empty;
            RaiseDetailStates();
            return;
        }

        if (string.Equals(_loadedChapterId, chapter.ChapterId, StringComparison.Ordinal) &&
            string.Equals(_state.Selection.ChapterId, chapter.ChapterId, StringComparison.Ordinal))
        {
            return;
        }

        _state.SelectChapter(chapter.ChapterId);
        foreach (var row in Chapters)
        {
            row.SetSelected(string.Equals(row.ChapterId, chapter.ChapterId, StringComparison.Ordinal));
        }

        await LoadPagesAsync(chapter).ConfigureAwait(true);
        await LoadProgressAsync().ConfigureAwait(true);
        RaiseDetailStates();
    }

    public void SelectPage(PageRowViewModel? page)
    {
        _state.SelectPage(page?.PageId);
        RefreshPageSelection();
    }

    /// <summary>Row callbacks: every row action funnels back through the single shell selection.</summary>
    private void OnBookSelected(BookRowViewModel book) => _ = SelectBookAsync(book);

    private void OnChapterSelected(ChapterRowViewModel chapter) => _ = SelectChapterAsync(chapter);

    private void OnPageSelected(PageRowViewModel page) => SelectPage(page);

    public void TogglePageSelection(PageRowViewModel page)
    {
        _state.ToggleMultiPage(page.PageId);
        RefreshPageSelection();
    }

    public void MoveObjectSelection(int delta)
    {
        if (Chapters.Count > 0 && SelectedBook is not null)
        {
            MoveChapterSelection(delta);
            return;
        }

        MoveBookSelection(delta);
    }

    public void MoveBookSelection(int delta)
    {
        if (Books.Count == 0)
        {
            return;
        }

        var current = SelectedBook is { } book ? Books.IndexOf(book) : -1;
        var next = Math.Clamp(current + delta, 0, Books.Count - 1);
        if (next < 0 || next == current)
        {
            return;
        }

        _ = SelectBookAsync(Books[next]);
    }

    public void MoveChapterSelection(int delta)
    {
        if (Chapters.Count == 0)
        {
            return;
        }

        var current = SelectedChapter is { } chapter ? Chapters.IndexOf(chapter) : -1;
        var next = Math.Clamp(current + delta, 0, Chapters.Count - 1);
        if (next == current || next < 0)
        {
            return;
        }

        _ = SelectChapterAsync(Chapters[next]);
    }

    public void MovePageSelection(int delta)
    {
        if (Pages.Count == 0)
        {
            return;
        }

        var current = SelectedPage is { } page ? Pages.IndexOf(page) : -1;
        var next = Math.Clamp(current + delta, 0, Pages.Count - 1);
        SelectPage(Pages[next]);
    }

    public async Task OpenReaderAsync()
    {
        if (SelectedBook is null || SelectedChapter is null)
        {
            _notify("阅读需要先选择作品与章节", NmStatus.Blocked);
            return;
        }

        var page = SelectedPage is { } current ? current.Index + 1 : (int?)null;
        await Reader.OpenAsync(SelectedBook.BookId, SelectedChapter.ChapterId, page).ConfigureAwait(true);
    }

    /// <summary>Deep-link / Ctrl+P page jump: opens the reader overlay at the 1-based page number.</summary>
    public async Task OpenReaderAtAsync(int pageNumber)
    {
        if (SelectedBook is null || SelectedChapter is null)
        {
            _notify("跳转到页需要先选择作品与章节", NmStatus.Blocked);
            return;
        }

        await Reader.OpenAsync(SelectedBook.BookId, SelectedChapter.ChapterId, pageNumber).ConfigureAwait(true);
    }

    // ── Import / recycle / create ─────────────────────────────────────────────────────────

    public async Task ReloadAfterImportAsync()
    {
        if (SelectedChapter is { } chapter)
        {
            await LoadPagesAsync(chapter).ConfigureAwait(true);
        }

        await RefreshBookCountsAsync().ConfigureAwait(true);
    }

    public void ShowRecycleBin()
    {
        IsRecycleBinView = true;
        _notify(
            "回收站：能力待接入（Host 未暴露 list_recycle_bin / restore / purge 方法，不能伪造列表）",
            NmStatus.Blocked);
    }

    /// <summary>Clears the Library search/filter/sort context (also resets the per-space view state).</summary>
    public void ClearFilters()
    {
        SearchText = string.Empty;
        _state.SetFilter(SpaceId.Library, null, "all");
        _state.SetSort(SpaceId.Library, null, SortUpdated);
        OnPropertyChanged(nameof(FilterKey), nameof(SortIndex));
        foreach (var chip in FilterChips)
        {
            chip.SetState(chip.Key == "all", chip.Count);
        }

        RebuildBooks();
    }

    public void CloseRecycleBin() => IsRecycleBinView = false;

    public void ShowCreateBook()
    {
        NewBookTitle = string.Empty;
        IsCreateBookOpen = true;
    }

    public async Task CreateBookAsync()
    {
        var title = NewBookTitle.Trim();
        if (title.Length == 0)
        {
            _notify("书名不能为空", NmStatus.Blocked);
            return;
        }

        var created = await _controller.TryCreateBookAsync(title).ConfigureAwait(true);
        if (!created)
        {
            _notify("新建作品被拒绝：Host 未就绪或当前只读", NmStatus.Blocked);
            return;
        }

        IsCreateBookOpen = false;
        NewBookTitle = string.Empty;
        _notify($"已新建作品《{title}》", NmStatus.Done);
        await RefreshAsync().ConfigureAwait(true);
        var createdBook = _allBooks.FirstOrDefault(book => string.Equals(book.Title, title, StringComparison.Ordinal));
        if (createdBook is not null)
        {
            await SelectBookAsync(createdBook).ConfigureAwait(true);
        }
    }

    public void ShowCreateChapter()
    {
        if (SelectedBook is null)
        {
            _notify("新建章节需要先选择一本作品", NmStatus.Blocked);
            return;
        }

        NewChapterTitle = string.Empty;
        IsCreateChapterOpen = true;
        OnPropertyChanged(nameof(CanCreateChapter));
        _notify("在右侧填写章节标题后确认：走 Core CreateChapter（V11R-A-1，minor 8）", NmStatus.Queued);
    }

    /// <summary>
    /// Real chapter creation through the new service method (V11R-A-1, audit F011). Returns null when
    /// the Host is not ready / read-only / the Core refused; the typed code is surfaced, never faked.
    /// </summary>
    public async Task CreateChapterAsync()
    {
        if (SelectedBook is not { } book)
        {
            _notify("新建章节需要先选择一本作品", NmStatus.Blocked);
            return;
        }

        var title = NewChapterTitle.Trim();
        if (title.Length == 0)
        {
            _notify("章节标题不能为空", NmStatus.Blocked);
            return;
        }

        IsCreatingChapter = true;
        OnPropertyChanged(nameof(CanCreateChapter));
        try
        {
            var created = await _controller.CreateChapterAsync(book.BookId, title).ConfigureAwait(true);
            if (created is null)
            {
                var code = _controller.Snapshot.LastError;
                _notify(
                    code is { Length: > 0 }
                        ? $"新建章节被拒绝（{code}）：Host 只读 / Core 拒绝，未写入任何数据"
                        : "新建章节被拒绝：Host 未就绪或只读，未写入任何数据",
                    NmStatus.Failed);
                return;
            }

            IsCreateChapterOpen = false;
            NewChapterTitle = string.Empty;
            _notify($"已新建章节《{created.Title}》", NmStatus.Done);
            await LoadChaptersAsync(book).ConfigureAwait(true);
            if (Chapters.FirstOrDefault(chapter =>
                    string.Equals(chapter.ChapterId, created.ChapterId, StringComparison.Ordinal)) is { } row)
            {
                await SelectChapterAsync(row).ConfigureAwait(true);
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("新建章节失败：" + ex.Message, NmStatus.Failed);
        }
        finally
        {
            IsCreatingChapter = false;
            OnPropertyChanged(nameof(CanCreateChapter));
        }
    }

    public void ShowCreateChapterEntry() => ShowCreateChapter();

    public void SetViewport(double width, double height)
    {
        // R-18: >=1600 full (4 columns) / 1280..1599 compact (3 columns) / <1280 narrow (detail overlay).
        var compact = ShellLayout.IsCompact(width);
        var narrow = ShellLayout.IsNarrow(width);
        var detailWidth = compact ? ShellLayout.CompactDetailPanelWidth : ShellLayout.DetailPanelWidth;
        var gap = ShellLayout.GridGap;
        var columns = compact ? 3 : 4;
        var content = Math.Max(0, width - (narrow ? 0 : detailWidth) - (2 * ShellLayout.PanelInset));
        var slot = columns == 0 ? 0 : content / columns;
        var cardWidth = Math.Max(0, slot - gap);

        DetailPanelWidth = detailWidth;
        CardGap = gap;
        CardWidth = Math.Floor(cardWidth);
        CardHeight = Math.Round(CardWidth * ShellLayout.CoverAspectRatio);
        ColumnCount = columns;
        IsNarrowLayout = narrow;

        OnPropertyChanged(
            nameof(CardSlotWidth),
            nameof(CardSlotHeight),
            nameof(DetailPanelWidth),
            nameof(ColumnCount),
            nameof(IsNarrowLayout),
            nameof(IsSideDetailVisible),
            nameof(IsOverlayDetailVisible),
            nameof(SearchBoxWidth),
            nameof(SortBoxWidth));
    }

    // ── Internal loaders ──────────────────────────────────────────────────────────────────

    private async Task LoadChaptersAsync(BookRowViewModel book)
    {
        IsChaptersLoading = true;
        Chapters.Clear();
        Pages.Clear();
        _loadedChapterId = string.Empty;
        try
        {
            var chapters = await _controller.ListChaptersAsync(book.BookId).ConfigureAwait(true);
            for (var index = 0; index < chapters.Count; index++)
            {
                var row = new ChapterRowViewModel(chapters[index], index, OnChapterSelected);
                row.SetSelected(string.Equals(row.ChapterId, _state.Selection.ChapterId, StringComparison.Ordinal));
                Chapters.Add(row);
            }

            _detailChapterCountText = Chapters.Count == 0 ? "0 章" : $"{Chapters.Count} 章";
            if (Chapters.Count == 0)
            {
                _state.SelectChapter(null);
                RaiseDetailStates();
                return;
            }

            var target = Chapters.FirstOrDefault(chapter =>
                    string.Equals(chapter.ChapterId, _state.Selection.ChapterId, StringComparison.Ordinal))
                ?? Chapters[0];
            await SelectChapterAsync(target).ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("章节读取失败：" + ex.Message, NmStatus.Failed);
        }
        finally
        {
            IsChaptersLoading = false;
            RaiseDetailStates();
        }
    }

    private async Task LoadPagesAsync(ChapterRowViewModel chapter)
    {
        IsPagesLoading = true;
        Pages.Clear();
        try
        {
            var pages = await _controller.ListChapterPagesAsync(chapter.ChapterId).ConfigureAwait(true);
            for (var index = 0; index < pages.Count; index++)
            {
                Pages.Add(new PageRowViewModel(pages[index], index, OnPageSelected, TogglePageSelection));
            }

            chapter.SetPageCount(pages.Count);
            _loadedChapterId = chapter.ChapterId;
            if (_state.Selection.PageId is { } selectedPage &&
                !Pages.Any(page => string.Equals(page.PageId, selectedPage, StringComparison.Ordinal)))
            {
                _state.SelectPage(null);
            }

            RefreshPageSelection();
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _notify("页读取失败：" + ex.Message, NmStatus.Failed);
        }
        finally
        {
            IsPagesLoading = false;
            RaiseDetailStates();
        }
    }

    private async Task LoadProgressAsync()
    {
        if (SelectedBook is not { } book || SelectedChapter is not { } chapter)
        {
            _detailProgressText = "—";
            OnPropertyChanged(nameof(DetailProgressText));
            return;
        }

        var data = await _controller.LoadReaderBookAsync(book.BookId, chapter.ChapterId).ConfigureAwait(true);
        if (data is null)
        {
            _detailProgressText = "进度未知（Core 未就绪或无阅读投影）";
        }
        else if (data.HasSavedProgress)
        {
            var total = Math.Max(1, data.Pages.Count);
            var page = Math.Clamp(data.InitialPageIndex + 1, 1, total);
            _detailProgressText = $"读到 第 {page} / {total} 页 · {page * 100.0 / total:0}%";
        }
        else
        {
            _detailProgressText = $"未开始阅读 · 共 {data.Pages.Count} 页";
        }

        OnPropertyChanged(nameof(DetailProgressText));
    }

    private async Task RefreshBookCountsAsync()
    {
        await _controller.RefreshBooksAsync().ConfigureAwait(true);
        var snapshot = _controller.Snapshot;
        var selectedId = _state.Selection.BookId;
        _allBooks.Clear();
        foreach (var book in snapshot.Books)
        {
            _allBooks.Add(new BookRowViewModel(book, OnBookSelected));
        }

        RebuildBooks();
        foreach (var book in _allBooks)
        {
            book.SetSelected(string.Equals(book.BookId, selectedId, StringComparison.Ordinal));
        }

        // Do NOT re-write the selection here: SelectBook would clear the chapter/page context. The
        // ShellState selection is already the truth; this pass only refreshes the row highlights.
        RaiseDetailStates();
    }

    // ── Filtering / sorting (client side over Host data) ─────────────────────────────────

    private void RebuildBooks()
    {
        var query = SearchText;
        IEnumerable<BookRowViewModel> visible = _allBooks;
        if (FilterKey == "favorite")
        {
            visible = visible.Where(book => book.IsFavorite);
        }
        else if (FilterKey == "archived")
        {
            visible = visible.Where(book => book.IsArchived);
        }

        if (!string.IsNullOrWhiteSpace(query))
        {
            visible = visible.Where(book => book.Matches(query));
        }

        visible = SortIndex switch
        {
            1 => visible.OrderBy(book => book.Title, StringComparer.OrdinalIgnoreCase),
            2 => visible.OrderByDescending(book => book.PageCount ?? 0),
            _ => visible.OrderByDescending(book => book.UpdatedAt),
        };

        Books.Clear();
        foreach (var book in visible)
        {
            book.SetSelected(string.Equals(book.BookId, _state.Selection.BookId, StringComparison.Ordinal));
            Books.Add(book);
        }

        UpdateFilterChips();
        OnPropertyChanged(nameof(BookCountText), nameof(ListStatusText));
        RaiseListStates();
    }

    private void UpdateFilterChips()
    {
        foreach (var chip in FilterChips)
        {
            var count = chip.Key switch
            {
                "favorite" => _allBooks.Count(book => book.IsFavorite),
                "archived" => _allBooks.Count(book => book.IsArchived),
                _ => _allBooks.Count,
            };
            chip.SetState(string.Equals(chip.Key, FilterKey, StringComparison.Ordinal), count);
        }
    }

    public void ToggleFilter(FilterChipItem chip)
    {
        if (chip is null)
        {
            return;
        }

        var next = string.Equals(FilterKey, chip.Key, StringComparison.Ordinal) && chip.Key != "all" ? "all" : chip.Key;
        _state.SetFilter(SpaceId.Library, null, next);
        foreach (var item in FilterChips)
        {
            item.SetState(string.Equals(item.Key, next, StringComparison.Ordinal), item.Count);
        }

        OnPropertyChanged(nameof(FilterKey));
        RebuildBooks();
    }

    private void RaiseListStates() => OnPropertyChanged(
        nameof(IsEmptyLibrary),
        nameof(HasNoResults),
        nameof(HostNotReady),
        nameof(ShowHostNotReadyState),
        nameof(ShowLoadingState),
        nameof(ShowErrorState),
        nameof(ShowEmptyLibraryState),
        nameof(ShowNoResultsState),
        nameof(ShowEmptyState),
        nameof(ShowBooksGrid),
        nameof(BookCountText),
        nameof(ListStatusText),
        nameof(HasStatus));

    private void RaiseDetailStates()
    {
        OnPropertyChanged(
            nameof(SelectedBook),
            nameof(SelectedChapter),
            nameof(SelectedPage),
            nameof(IsDetailOpen),
            nameof(HasSelection),
            nameof(HasChapters),
            nameof(HasPages),
            nameof(DetailTitle),
            nameof(DetailOriginalTitle),
            nameof(HasDetailOriginalTitle),
            nameof(DetailMeta),
            nameof(DetailChapterCountText),
            nameof(DetailPageCountText),
            nameof(DetailProgressText),
            nameof(IsMultiSelectActive),
            nameof(SelectionCount),
            nameof(SelectionSummary));
        ImportDock.NotifyChapterContextChanged();
    }

    private void RefreshPageSelection()
    {
        foreach (var page in Pages)
        {
            page.SetSelection(
                string.Equals(page.PageId, _state.Selection.PageId, StringComparison.Ordinal),
                _state.Selection.MultiPage.Contains(page.PageId, StringComparer.Ordinal));
        }

        OnPropertyChanged(nameof(SelectedPage), nameof(IsMultiSelectActive), nameof(SelectionCount), nameof(SelectionSummary), nameof(DetailPageCountText));
    }

    private void OnSelectionChanged(object? sender, EventArgs e)
    {
        foreach (var book in _allBooks)
        {
            book.SetSelected(string.Equals(book.BookId, _state.Selection.BookId, StringComparison.Ordinal));
        }

        foreach (var chapter in Chapters)
        {
            chapter.SetSelected(string.Equals(chapter.ChapterId, _state.Selection.ChapterId, StringComparison.Ordinal));
        }

        RefreshPageSelection();
        RaiseDetailStates();
    }

    private void RequestRecycleAction(string verb)
    {
        _requestConfirm(new ConfirmRequest(
            $"{verb}回收站作品",
            "注意：回收站读取与恢复/永久删除命令尚未在 IHostController 暴露（能力待接入），" +
            "此处只能确认操作意图，不会执行任何写入，也不会伪造成功。",
            $"{verb}（能力待接入）",
            IsDanger: verb.Contains("永久", StringComparison.Ordinal),
            OnConfirm: () => _notify($"{verb}：能力待接入（Host 未暴露回收站命令，未执行任何写入）", NmStatus.Blocked),
            CanConfirm: false,
            BlockedReason: "能力待接入：Host 未暴露回收站读取 / 恢复 / 永久删除方法"));
    }
}
