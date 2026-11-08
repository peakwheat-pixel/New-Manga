using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.CoreClient;

namespace NewManga.App.ViewModels.Fluent;

public sealed class ShelfViewModel : FluentViewModel
{
    private readonly IHostController? _host;
    private string _search = string.Empty;
    private bool _isGrid = true;
    private bool _favoritesOnly;
    private bool _archivedOnly;
    private BookSummary? _selectedBook;
    private ChapterSummary? _selectedChapter;
    private bool _isImporting;
    private string _viewStatus = string.Empty;
    private bool _isDetailPaneCollapsed;
    private double _listScrollOffset;
    private IReadOnlyList<ChapterPageSummary> _previewPages = Array.Empty<ChapterPageSummary>();

    public ShelfViewModel(IHostController? host)
    {
        _host = host;
        State = host?.Snapshot.State == HostViewState.Ready ? FluentPageState.Ready : FluentPageState.Loading;
        _viewStatus = host?.Snapshot.StatusLine ?? "正在连接 Host…";
        if (_host is not null)
        {
            _host.Changed += OnHostChanged;
        }
    }

    public IReadOnlyList<BookSummary> Books => _host?.Snapshot.Books ?? Array.Empty<BookSummary>();

    public IEnumerable<BookSummary> FilteredBooks => Books.Where(book =>
        (string.IsNullOrWhiteSpace(Search) || book.Title.Contains(Search, StringComparison.CurrentCultureIgnoreCase)) &&
        (!_favoritesOnly || book.IsFavorite) && (!_archivedOnly || book.IsArchived));

    public ObservableCollection<ChapterSummary> Chapters { get; } = new();
    public IReadOnlyList<ChapterPageSummary> PreviewPages
    {
        get => _previewPages;
        private set => Set(ref _previewPages, value);
    }

    // ------------------------------------------------------------------------------------------
    // AC-4（格 4）：书架满态统计 = 既有投影的自洽聚合（零新增命令）；PageCount 为 null 不计入。
    // ------------------------------------------------------------------------------------------

    /// <summary>AC-4：筛选后作品的 <c>ΣPageCount</c>（<c>PageCount==null</c> 不计入）。</summary>
    public int FilteredPageCountTotal =>
        FilteredBooks.Sum(book => book.PageCount ?? 0);

    /// <summary>AC-4：筛选后作品是否存在真实 PageCount（全为 null =「—」，不显示 0 冒充统计）。</summary>
    public bool HasPageCountData => FilteredBooks.Any(book => book.PageCount is not null);

    /// <summary>AC-4：<c>ΣPageCount</c> 文案；缺失显示「—」而非 0。</summary>
    public string PageCountTotalText => HasPageCountData ? FilteredPageCountTotal.ToString() : "—";

    /// <summary>
    /// AC-4：状态条 = <c>"{FilteredBooks.Count} / {Books.Count} 部作品"</c> + <c>ΣPageCount</c>。
    /// 只聚合既有 <c>BookSummary.PageCount</c>（Core 真算）与 <c>Books.Count</c>，不新增命令。
    /// </summary>
    public string StatsLine => $"{FilteredBooks.Count()} / {Books.Count} 部作品 · 总页数 {PageCountTotalText}";

    public string Search
    {
        get => _search;
        set
        {
            if (Set(ref _search, value ?? string.Empty))
            {
                NotifyFilterChanged();
                UpdateState();
            }
        }
    }

    public bool IsGrid
    {
        get => _isGrid;
        set => Set(ref _isGrid, value);
    }

    /// <summary>I-1/I-2：详情栏折叠状态；同一运行期 UI memento，不落盘（页面往返/frontend 切换后保留）。</summary>
    public bool IsDetailPaneCollapsed
    {
        get => _isDetailPaneCollapsed;
        set => Set(ref _isDetailPaneCollapsed, value);
    }

    /// <summary>I-1：书架列表滚动偏移；同一运行期 UI memento，不落盘。</summary>
    public double ListScrollOffset
    {
        get => _listScrollOffset;
        set => Set(ref _listScrollOffset, value);
    }

    public bool FavoritesOnly
    {
        get => _favoritesOnly;
        set { if (Set(ref _favoritesOnly, value)) { NotifyFilterChanged(); UpdateState(); } }
    }

    public bool ArchivedOnly
    {
        get => _archivedOnly;
        set { if (Set(ref _archivedOnly, value)) { NotifyFilterChanged(); UpdateState(); } }
    }

    public void ClearFilters()
    {
        Search = string.Empty;
        FavoritesOnly = false;
        ArchivedOnly = false;
        NotifyFilterChanged();
        UpdateState();
    }

    public BookSummary? SelectedBook
    {
        get => _selectedBook;
        private set => Set(ref _selectedBook, value);
    }

    public ChapterSummary? SelectedChapter
    {
        get => _selectedChapter;
        private set => Set(ref _selectedChapter, value);
    }

    public IReadOnlyList<BookSummary> SelectedBooks { get; private set; } = Array.Empty<BookSummary>();

    public bool IsImporting
    {
        get => _isImporting;
        private set
        {
            if (Set(ref _isImporting, value))
            {
                if (value) State = FluentPageState.Running;
                else UpdateState();
                Changed(nameof(IsReadOnly));
            }
        }
    }

    public bool IsReadOnly => _host is null || !_host.Snapshot.WritesAllowed || _host.Snapshot.State != HostViewState.Ready;

    public string ViewStatus
    {
        get => _viewStatus;
        private set => Set(ref _viewStatus, value);
    }

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null)
        {
            State = FluentPageState.Error;
            Error = "Host 未注入，书架暂不可用。";
            return;
        }

        State = FluentPageState.Loading;
        ViewStatus = "正在读取书架…";
        try
        {
            await _host.RefreshBooksAsync(cancellationToken);
            UpdateState();
            NotifyFilterChanged();
            // AC-4：部作品/ΣPageCount 聚合由状态条 StatsLine 呈现，这里只保留 Host 状态行，避免重复计数。
            ViewStatus = _host.Snapshot.StatusLine;
        }
        catch (Exception ex)
        {
            State = FluentPageState.Error;
            Error = $"读取书架失败（{_host.Snapshot.ErrorCode ?? ex.GetType().Name}）。";
        }
    }

    public async Task SelectBookAsync(BookSummary book, CancellationToken cancellationToken = default)
    {
        SelectedBook = book;
        SelectedChapter = null;
        Chapters.Clear();
        Changed(nameof(SelectedBooks));
        if (_host is null)
        {
            return;
        }

        var chapters = await _host.ListChaptersAsync(book.BookId, cancellationToken);
        foreach (var chapter in chapters.OrderBy(item => item.SortOrder))
        {
            Chapters.Add(chapter);
        }

        SelectedChapter = Chapters.FirstOrDefault();
        if (SelectedChapter is not null)
        {
            PreviewPages = await _host.ListChapterPagesAsync(SelectedChapter.ChapterId, cancellationToken);
        }
        ViewStatus = chapters.Count == 0 ? "这部作品还没有章节。" : $"{book.Title} · {chapters.Count} 个章节";
    }

    public void ToggleSelection(BookSummary book)
    {
        var selected = SelectedBooks.ToList();
        if (selected.Any(item => item.BookId == book.BookId))
        {
            selected.RemoveAll(item => item.BookId == book.BookId);
        }
        else
        {
            selected.Add(book);
        }

        SelectedBooks = selected;
        Changed(nameof(SelectedBooks));
    }

    public void ClearSelection()
    {
        SelectedBooks = Array.Empty<BookSummary>();
        Changed(nameof(SelectedBooks));
    }

    public async Task MoveSelection(int direction, CancellationToken cancellationToken = default)
    {
        var books = FilteredBooks.ToArray();
        if (books.Length == 0) return;
        var current = SelectedBook is null ? -1 : Array.FindIndex(books, item => item.BookId == SelectedBook.BookId);
        var next = Math.Clamp(current + direction, 0, books.Length - 1);
        await SelectBookAsync(books[next], cancellationToken);
    }

    public async Task MoveChapter(int direction, CancellationToken cancellationToken = default)
    {
        if (Chapters.Count == 0) return;
        var current = SelectedChapter is null ? -1 : Chapters.IndexOf(SelectedChapter);
        var next = Math.Clamp(current + direction, 0, Chapters.Count - 1);
        await SelectChapterAsync(Chapters[next], cancellationToken);
    }

    public void SelectChapter(ChapterSummary? chapter)
    {
        SelectedChapter = chapter;
        if (chapter is not null)
        {
            ViewStatus = $"已选择：{SelectedBook?.Title} · {chapter.Title}";
        }
    }

    public async Task SelectChapterAsync(ChapterSummary? chapter, CancellationToken cancellationToken = default)
    {
        SelectChapter(chapter);
        PreviewPages = _host is null || chapter is null
            ? Array.Empty<ChapterPageSummary>()
            : await _host.ListChapterPagesAsync(chapter.ChapterId, cancellationToken);
    }

    public async Task<bool> CreateBookAsync(string title, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || string.IsNullOrWhiteSpace(title))
        {
            return false;
        }

        var created = await _host.TryCreateBookAsync(title.Trim(), cancellationToken);
        if (!created)
        {
            Error = $"创建作品失败（{_host.Snapshot.LastError ?? "HOST_NOT_READY"}）。";
            State = FluentPageState.Error;
            return false;
        }

        await RefreshAsync(cancellationToken);
        var book = Books.FirstOrDefault(item => string.Equals(item.Title, title.Trim(), StringComparison.Ordinal));
        if (book is not null)
        {
            await SelectBookAsync(book, cancellationToken);
        }

        return book is not null;
    }

    public async Task<bool> CreateChapterAsync(string title, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || SelectedBook is null || string.IsNullOrWhiteSpace(title))
        {
            return false;
        }

        var chapter = await _host.CreateChapterAsync(SelectedBook.BookId, title.Trim(), cancellationToken);
        if (chapter is null)
        {
            Error = $"创建章节失败（{_host.Snapshot.LastError ?? "HOST_NOT_READY"}）。";
            State = FluentPageState.Error;
            return false;
        }

        await SelectBookAsync(SelectedBook, cancellationToken);
        SelectChapter(Chapters.FirstOrDefault(item => item.ChapterId == chapter.ChapterId));
        return true;
    }

    public async Task<ImportOutcome> ImportFilesAsync(IReadOnlyList<string> paths, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || SelectedChapter is null)
        {
            return ImportOutcome.NotReady();
        }

        IsImporting = true;
        ViewStatus = "正在导入文件…";
        try
        {
            var result = await _host.ImportFilesAsync(SelectedChapter.ChapterId, paths, cancellationToken: cancellationToken);
            ViewStatus = ImportExportFormatting.ImportStatus(result);
            if (result.Ok)
            {
                await _host.RefreshBooksAsync(cancellationToken);
                Changed(nameof(Books));
                UpdateState();
            }

            return result;
        }
        finally
        {
            IsImporting = false;
            NotifyFilterChanged();
        }
    }

    public async Task<ImportOutcome> ImportFolderAsync(string folder, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || SelectedChapter is null)
        {
            return ImportOutcome.NotReady();
        }

        IsImporting = true;
        ViewStatus = "正在扫描并导入文件夹…";
        try
        {
            var result = await _host.ImportFolderAsync(SelectedChapter.ChapterId, folder, cancellationToken: cancellationToken);
            ViewStatus = ImportExportFormatting.ImportStatus(result);
            if (result.Ok)
            {
                await _host.RefreshBooksAsync(cancellationToken);
                Changed(nameof(Books));
                UpdateState();
            }

            return result;
        }
        finally
        {
            IsImporting = false;
        }
    }

    private void OnHostChanged(object? sender, EventArgs args)
    {
        Changed(nameof(Books));
        NotifyFilterChanged();
        Changed(nameof(IsReadOnly));
        ViewStatus = _host?.Snapshot.StatusLine ?? string.Empty;
        UpdateState();
    }

    /// <summary>AC-4：筛选/数据面变化时同时刷新列表与状态条聚合（同一自洽投影）。</summary>
    private void NotifyFilterChanged()
    {
        Changed(nameof(FilteredBooks));
        Changed(nameof(FilteredPageCountTotal));
        Changed(nameof(HasPageCountData));
        Changed(nameof(PageCountTotalText));
        Changed(nameof(StatsLine));
    }

    private void UpdateState()
    {
        if (_host?.Snapshot.State == HostViewState.Failed)
        {
            State = FluentPageState.Error;
            Error = _host.Snapshot.ErrorMessage ?? "读取书架失败。";
        }
        else if (IsImporting)
        {
            State = FluentPageState.Running;
        }
        else if (_host is null || _host.Snapshot.State is HostViewState.Starting or HostViewState.AlreadyRunning)
        {
            State = FluentPageState.Loading;
        }
        else if (Books.Count == 0)
        {
            State = FluentPageState.Empty;
        }
        else if (!string.IsNullOrWhiteSpace(Search) && !FilteredBooks.Any())
        {
            State = FluentPageState.Partial;
        }
        else if (IsReadOnly)
        {
            State = FluentPageState.ReadOnly;
        }
        else
        {
            State = FluentPageState.Ready;
        }
    }
}
