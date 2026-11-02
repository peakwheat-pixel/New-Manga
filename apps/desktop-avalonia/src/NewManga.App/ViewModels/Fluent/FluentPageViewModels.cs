using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Text.Json;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.ViewModels.Fluent;

public enum FluentPageState
{
    Loading,
    Error,
    Empty,
    Ready,
    Partial,
    ReadOnly,
    Running,
    Conflict,
}

public abstract class FluentViewModel : INotifyPropertyChanged
{
    private FluentPageState _state;
    private string _status = string.Empty;
    private string _error = string.Empty;

    public event PropertyChangedEventHandler? PropertyChanged;

    public FluentPageState State
    {
        get => _state;
        protected set => Set(ref _state, value);
    }

    public string Status
    {
        get => _status;
        protected set => Set(ref _status, value);
    }

    public string Error
    {
        get => _error;
        protected set => Set(ref _error, value);
    }

    protected bool Set<T>(ref T field, T value, [CallerMemberName] string? name = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value))
        {
            return false;
        }

        field = value;
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        return true;
    }

    protected void Changed([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

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

    public string Search
    {
        get => _search;
        set
        {
            if (Set(ref _search, value ?? string.Empty))
            {
                Changed(nameof(FilteredBooks));
                UpdateState();
            }
        }
    }

    public bool IsGrid
    {
        get => _isGrid;
        set => Set(ref _isGrid, value);
    }

    public bool FavoritesOnly
    {
        get => _favoritesOnly;
        set { if (Set(ref _favoritesOnly, value)) { Changed(nameof(FilteredBooks)); UpdateState(); } }
    }

    public bool ArchivedOnly
    {
        get => _archivedOnly;
        set { if (Set(ref _archivedOnly, value)) { Changed(nameof(FilteredBooks)); UpdateState(); } }
    }

    public void ClearFilters()
    {
        Search = string.Empty;
        FavoritesOnly = false;
        ArchivedOnly = false;
        Changed(nameof(FilteredBooks));
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
            ViewStatus = $"{Books.Count} 部作品 · {_host.Snapshot.StatusLine}";
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
            Changed(nameof(FilteredBooks));
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
        Changed(nameof(FilteredBooks));
        Changed(nameof(IsReadOnly));
        ViewStatus = _host?.Snapshot.StatusLine ?? string.Empty;
        UpdateState();
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

public sealed class WorkbenchViewModel : FluentViewModel
{
    private readonly IHostController? _host;
    private readonly string _sessionId;
    private string? _chapterId;
    private string? _pageId;
    private ChapterPageSummary? _selectedPage;
    private RegionSummary? _selectedRegion;
    private RegionPageProjection? _projection;
    private byte[]? _pageImageBytes;
    private RegionRevisionHistory? _revisions;
    private Draft? _draft;
    private DraftLease? _lease;
    private RegionCandidate? _candidate;
    private string _draftText = string.Empty;
    private string _persistedDraftText = string.Empty;
    private IReadOnlyList<Draft> _drafts = Array.Empty<Draft>();
    private bool _isBatch;
    private bool _isApplying;

    public WorkbenchViewModel(IHostController? host, string sessionId)
    {
        _host = host;
        _sessionId = sessionId;
        State = FluentPageState.Empty;
        Status = "从书架选择章节以开始编辑。";
    }

    public ObservableCollection<ChapterPageSummary> Pages { get; } = new();
    public ObservableCollection<RegionSummary> Regions { get; } = new();
    public IReadOnlyList<Draft> Drafts
    {
        get => _drafts;
        private set => Set(ref _drafts, value);
    }
    public ChapterPageSummary? SelectedPage { get => _selectedPage; private set => Set(ref _selectedPage, value); }
    public RegionSummary? SelectedRegion { get => _selectedRegion; private set => Set(ref _selectedRegion, value); }
    public RegionPageProjection? Projection { get => _projection; private set => Set(ref _projection, value); }
    public byte[]? PageImageBytes { get => _pageImageBytes; private set => Set(ref _pageImageBytes, value); }
    public Draft? CurrentDraft { get => _draft; private set => Set(ref _draft, value); }
    public string DraftText
    {
        get => _draftText;
        set
        {
            if (Set(ref _draftText, value ?? string.Empty)) Changed(nameof(HasUnsavedDraft));
        }
    }
    public bool IsBatch { get => _isBatch; set => Set(ref _isBatch, value); }
    public bool IsApplying { get => _isApplying; private set => Set(ref _isApplying, value); }
    public bool IsReadOnly => _host is null || !_host.Snapshot.WritesAllowed;
    public bool HasUnsavedDraft => CurrentDraft is not null && !string.Equals(DraftText, _persistedDraftText, StringComparison.Ordinal);
    public string ErrorCategory { get; private set; } = string.Empty;
    public IReadOnlyList<string> ErrorCodes => DraftErrorMap.Codes;

    public async Task LoadAsync(string? chapterId, CancellationToken cancellationToken = default)
    {
        _chapterId = chapterId;
        if (_host is null || string.IsNullOrWhiteSpace(chapterId))
        {
            State = FluentPageState.Empty;
            Status = "未选择章节。返回书架并选择章节。";
            return;
        }

        State = FluentPageState.Loading;
        Status = "正在读取工作台…";
        try
        {
            var pages = await _host.ListChapterPagesAsync(chapterId, cancellationToken);
            Pages.Clear();
            foreach (var page in pages.OrderBy(item => item.SortOrder))
            {
                Pages.Add(page);
            }

            if (Pages.Count == 0)
            {
                State = FluentPageState.Empty;
                Status = "本章节暂无页面。";
                return;
            }

            SelectedPage = Pages.FirstOrDefault(item => item.PageId == _pageId) ?? Pages[0];
            _pageId = SelectedPage.PageId;
            await LoadPageAsync(SelectedPage.PageId, cancellationToken);
            Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
            CurrentDraft = Drafts.FirstOrDefault(item => item.PageId == SelectedPage.PageId && item.RegionId == SelectedRegion?.RegionId);
            if (CurrentDraft is not null)
            {
                _lease = await _host.OpenDraftAsync(_sessionId, CurrentDraft.PageId, CurrentDraft.RegionId,
                    CurrentDraft.BaseRevisionId, CurrentDraft.PageBindingVersion, cancellationToken);
                DraftText = ReadDraftText(CurrentDraft.Patch);
                _persistedDraftText = DraftText;
            }

            State = IsReadOnly ? FluentPageState.ReadOnly : FluentPageState.Ready;
            Status = IsReadOnly ? _host.Snapshot.ReadOnlyReason ?? "只读模式" : "工作台已就绪";
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = FluentPageState.Error;
            Status = Error;
        }
        catch (Exception ex)
        {
            State = FluentPageState.Error;
            Error = $"读取工作台失败（{ex.GetType().Name}）。画布保留上一帧。";
            Status = Error;
        }
    }

    public async Task SelectPageAsync(string pageId, CancellationToken cancellationToken = default)
    {
        if (HasUnsavedDraft && CurrentDraft is not null && _host is not null)
        {
            await _host.GetDraftAsync(CurrentDraft.DraftId, cancellationToken);
        }

        _pageId = pageId;
        SelectedPage = Pages.FirstOrDefault(item => item.PageId == pageId);
        if (SelectedPage is not null)
        {
            await LoadPageAsync(pageId, cancellationToken);
            CurrentDraft = null;
            _lease = null;
            DraftText = string.Empty;
        }
    }

    public async Task SelectRegionAsync(RegionSummary? region, CancellationToken cancellationToken = default)
    {
        SelectedRegion = region;
        _revisions = null;
        CurrentDraft = null;
        _lease = null;
        _candidate = null;
        DraftText = string.Empty;
        if (_host is null || region is null || SelectedPage is null)
        {
            return;
        }

        _revisions = await _host.LoadRegionRevisionsAsync(region.RegionId, cancellationToken);
        Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
        CurrentDraft = Drafts.FirstOrDefault(item => item.PageId == SelectedPage.PageId && item.RegionId == region.RegionId);
        if (CurrentDraft is not null)
        {
            _lease = await _host.OpenDraftAsync(_sessionId, CurrentDraft.PageId, CurrentDraft.RegionId,
                CurrentDraft.BaseRevisionId, CurrentDraft.PageBindingVersion, cancellationToken);
            DraftText = ReadDraftText(CurrentDraft.Patch);
            _persistedDraftText = DraftText;
        }

        Changed(nameof(HasUnsavedDraft));
    }

    /// <summary>
    /// The frozen Host projection does not expose PageBindingVersion. A new draft cannot be opened
    /// safely without it, so this method fails closed instead of inventing a version.
    /// </summary>
    public async Task<bool> OpenDraftAsync(int? pageBindingVersion = null, CancellationToken cancellationToken = default)
    {
        if (_host is null || SelectedPage is null || SelectedRegion is null || IsReadOnly)
        {
            return false;
        }

        if (pageBindingVersion is null)
        {
            State = FluentPageState.ReadOnly;
            Error = "当前 Host 页面投影未提供 pageBindingVersion，无法安全开启新草稿。";
            Status = Error;
            return false;
        }

        try
        {
            _revisions ??= await _host.LoadRegionRevisionsAsync(SelectedRegion.RegionId, cancellationToken);
            var baseRevisionId = _revisions?.Revisions.FirstOrDefault(item => item.IsCurrent)?.RegionRevisionId;
            _lease = await _host.OpenDraftAsync(_sessionId, SelectedPage.PageId, SelectedRegion.RegionId,
                baseRevisionId, pageBindingVersion.Value, cancellationToken);
            if (_lease is null || !_lease.CanEdit || _lease.Token is null)
            {
                State = FluentPageState.Conflict;
                Error = "草稿当前不可编辑或 Host 未提供 EditToken。";
                Status = Error;
                return false;
            }

            CurrentDraft = _lease.Draft;
            DraftText = ReadDraftText(CurrentDraft.Patch);
            _persistedDraftText = DraftText;
            State = FluentPageState.Ready;
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            Status = Error;
            return false;
        }
    }

    public async Task<bool> SaveDraftAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null || IsReadOnly)
        {
            return false;
        }

        try
        {
            var patch = new DraftPatchRequest(new Dictionary<string, object?> { ["text"] = DraftText });
            CurrentDraft = await _host.PatchDraftAsync(CurrentDraft.DraftId, _sessionId, patch,
                cancellationToken: cancellationToken);
            Changed(nameof(HasUnsavedDraft));
            if (CurrentDraft is null)
            {
                Error = "Host 没有返回保存后的 Draft。";
                State = FluentPageState.Error;
                return false;
            }

            _persistedDraftText = DraftText;

            Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
            Status = "草稿已写入恢复日志。";
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            return false;
        }
    }

    public async Task<bool> ApplyCandidateAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null || SelectedRegion is null || _lease?.Token is null || IsReadOnly)
        {
            return false;
        }

        IsApplying = true;
        try
        {
            var patch = new DraftPatchRequest(new Dictionary<string, object?> { ["text"] = DraftText });
            _candidate = await _host.PrepareCandidateAsync(SelectedRegion.RegionId, patch, "manual",
                CurrentDraft.DraftId, CurrentDraft.BaseRevisionId, cancellationToken);
            if (_candidate is null)
            {
                Error = "Host 未准备 Candidate，应用未执行。";
                State = FluentPageState.Error;
                return false;
            }

            var freshLease = await _host.OpenDraftAsync(_sessionId, CurrentDraft.PageId, CurrentDraft.RegionId,
                CurrentDraft.BaseRevisionId, CurrentDraft.PageBindingVersion, cancellationToken);
            if (freshLease?.Token is null || !freshLease.CanEdit)
            {
                State = FluentPageState.Conflict;
                Error = "应用前 Draft token 已不可用，请重新读取状态。";
                return false;
            }

            var applied = await _host.ApplyCandidatesAsync(freshLease.Token, [_candidate.CandidateId], cancellationToken);
            if (!applied.ContainsKey(_candidate.CandidateId))
            {
                Error = "Host 没有确认 Candidate 应用；保留当前画布状态。";
                State = FluentPageState.Error;
                return false;
            }

            _lease = freshLease;
            State = FluentPageState.Ready;
            Status = "Candidate 已由 Host 确认应用。";
            await LoadPageAsync(SelectedPage?.PageId ?? string.Empty, cancellationToken);
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            return false;
        }
        finally
        {
            IsApplying = false;
        }
    }

    public async Task<bool> ReloadDraftAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null)
        {
            return false;
        }

        try
        {
            CurrentDraft = await _host.GetDraftAsync(CurrentDraft.DraftId, cancellationToken);
            if (CurrentDraft is null)
            {
                Error = "草稿不存在或当前 Host 不可用。";
                return false;
            }

            DraftText = ReadDraftText(CurrentDraft.Patch);
            _persistedDraftText = DraftText;
            Status = "草稿已重新读取。";
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            return false;
        }
    }

    public async Task DiscardDraftAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null || IsReadOnly)
        {
            return;
        }

        await _host.DiscardDraftAsync(CurrentDraft.DraftId, _sessionId, cancellationToken);
        CurrentDraft = null;
        _lease = null;
        DraftText = string.Empty;
        _persistedDraftText = string.Empty;
        Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
        State = FluentPageState.Ready;
        Status = "草稿已按请求丢弃。";
        Changed(nameof(HasUnsavedDraft));
    }

    private async Task LoadPageAsync(string pageId, CancellationToken cancellationToken)
    {
        if (_host is null || string.IsNullOrWhiteSpace(pageId))
        {
            return;
        }

        try
        {
            var projection = await _host.LoadPageRegionsAsync(pageId, cancellationToken);
            if (projection is null)
            {
                throw new InvalidOperationException("Core region projection unavailable");
            }

            var image = await _host.ReadPageImageAsync(pageId, cancellationToken);
            if (image is not null && image.Length > 0)
            {
                PageImageBytes = image;
            }

            Projection = projection;
            Regions.Clear();
            foreach (var region in projection.Regions)
            {
                Regions.Add(region);
            }

            if (SelectedRegion is null || !projection.Regions.Any(item => item.RegionId == SelectedRegion.RegionId))
            {
                SelectedRegion = Regions.FirstOrDefault();
            }
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            Status = Error;
        }
    }

    private static string ReadDraftText(JsonElement? patch)
    {
        if (patch is { ValueKind: JsonValueKind.Object } value && value.TryGetProperty("text", out var text) && text.ValueKind == JsonValueKind.String)
        {
            return text.GetString() ?? string.Empty;
        }

        return string.Empty;
    }

    private void ApplyDraftError(CoreOperationException ex)
    {
        ErrorCategory = DraftErrorMap.Category(ex.Code, ex.Category);
        Error = DraftErrorMap.Presentation(ex.Code, ErrorCategory);
        Changed(nameof(ErrorCategory));
    }
}

public static class DraftErrorMap
{
    private static readonly IReadOnlyDictionary<string, string> Categories = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["DRAFT_INVALID"] = "validation", ["DRAFT_PATCH_INVALID"] = "validation",
        ["DRAFT_CANDIDATE_INVALID"] = "validation", ["DRAFT_FLUSH_TRIGGER_INVALID"] = "validation",
        ["EDIT_TOKEN_INVALID"] = "validation", ["DRAFT_NOT_FOUND"] = "not_found",
        ["DRAFT_CANDIDATE_NOT_FOUND"] = "not_found", ["TARGET_NOT_FOUND"] = "not_found",
        ["DRAFT_READ_ONLY"] = "conflict", ["DRAFT_OWNER_CHANGED"] = "conflict",
        ["EDIT_TOKEN_EXPIRED"] = "conflict", ["EDIT_TOKEN_REUSED"] = "conflict",
        ["STALE_BASE_REVISION"] = "conflict", ["LOCK_CHANGED"] = "conflict",
        ["DRAFT_JOURNAL_UNWRITABLE"] = "unavailable", ["PAGE_SIZE_UNAVAILABLE"] = "unavailable",
        ["DRAFT_APPLY_FAILED"] = "internal", ["INTERNAL"] = "internal", ["UNKNOWN"] = "validation",
    };

    public static IReadOnlyList<string> Codes => Categories.Keys.OrderBy(value => value, StringComparer.Ordinal).ToArray();

    public static string Category(string code, string? fallback) => Categories.TryGetValue(code, out var category)
        ? category
        : fallback is "validation" or "not_found" or "conflict" or "unavailable" or "internal" ? fallback : "unknown";

    public static string Presentation(string code, string category) => category switch
    {
        "validation" => $"输入校验失败（{code}），请修正后重试。",
        "not_found" => $"目标已不存在（{code}），已保留当前工作区。",
        "conflict" => $"检测到并发或保护冲突（{code}），已停止应用，请重新读取并对照。",
        "unavailable" => $"Draft 服务暂不可用（{code}），可以重试。",
        "internal" => $"Draft 操作失败（{code}），已保留当前界面。",
        _ => $"Draft 操作被拒绝（{code}）。",
    };
}

public sealed class ReaderViewModel : FluentViewModel
{
    private readonly IHostController? _host;
    private ReaderBookData? _book;
    private int _pageIndex;
    private double _zoom = 1;
    private bool _isFullScreen;
    private bool _doublePage;
    private bool _reverseDirection;
    private string _layout = "fit-page";
    private double _scrollOffset;
    private byte[]? _pageBytes;
    private bool _isSavingProgress;
    private string? _requestedBookId;
    private string? _requestedChapterId;

    public ReaderViewModel(IHostController? host) => _host = host;

    public ReaderBookData? Book { get => _book; private set => Set(ref _book, value); }
    public int PageIndex { get => _pageIndex; private set => Set(ref _pageIndex, value); }
    public int PageCount => Book?.Pages.Count ?? 0;
    public double Zoom { get => _zoom; private set => Set(ref _zoom, Math.Clamp(value, 0.2, 5)); }
    public bool IsFullScreen { get => _isFullScreen; set => Set(ref _isFullScreen, value); }
    public bool DoublePage { get => _doublePage; set => Set(ref _doublePage, value); }
    public bool ReverseDirection { get => _reverseDirection; set => Set(ref _reverseDirection, value); }
    public string Layout { get => _layout; set => Set(ref _layout, value); }
    public byte[]? PageBytes { get => _pageBytes; private set => Set(ref _pageBytes, value); }
    public bool IsSavingProgress { get => _isSavingProgress; private set => Set(ref _isSavingProgress, value); }
    public bool IsSourceUnavailable { get; private set; }
    public string PageLabel => PageCount == 0 ? "0 / 0" : $"{PageIndex + 1} / {PageCount}";
    public double Progress => PageCount < 2 ? 0 : PageIndex * 100d / (PageCount - 1);
    public string AccessiblePageName => PageCount == 0 ? "本章节暂无页面" : $"第 {PageIndex + 1} 页，共 {PageCount} 页";

    public async Task LoadAsync(string? bookId, string? chapterId, CancellationToken cancellationToken = default)
    {
        _requestedBookId = bookId;
        _requestedChapterId = chapterId;
        if (_host is null)
        {
            State = FluentPageState.Error;
            Error = "Host 未注入，阅读器不可用。";
            return;
        }

        State = FluentPageState.Loading;
        Status = "正在读取章节…";
        try
        {
            var loaded = await _host.LoadReaderBookAsync(bookId, chapterId, cancellationToken);
            if (loaded is null || loaded.Pages.Count == 0)
            {
                Book = loaded;
                State = FluentPageState.Empty;
                Status = "本章节暂无页面。";
                PageBytes = null;
                return;
            }

            Book = loaded;
            Layout = loaded.Layout;
            PageIndex = Math.Clamp(loaded.InitialPageIndex, 0, loaded.Pages.Count - 1);
            _scrollOffset = loaded.InitialScrollOffsetY;
            await LoadCurrentPageAsync(cancellationToken);
        }
        catch (Exception ex)
        {
            State = FluentPageState.Error;
            Error = $"读取章节失败（{ex.GetType().Name}）。";
        }
    }

    public async Task<bool> NavigateAsync(int delta, CancellationToken cancellationToken = default)
    {
        if (Book is null || PageCount == 0)
        {
            return false;
        }

        var next = Math.Clamp(PageIndex + (_reverseDirection ? -delta : delta), 0, PageCount - 1);
        if (next == PageIndex)
        {
            return false;
        }

        PageIndex = next;
        Changed(nameof(PageLabel));
        Changed(nameof(Progress));
        Changed(nameof(AccessiblePageName));
        State = FluentPageState.Loading;
        var loaded = await LoadCurrentPageAsync(cancellationToken);
        if (loaded && _host is not null && Book is not null)
        {
            IsSavingProgress = true;
            State = FluentPageState.Running;
            var result = await _host.SaveReadingProgressAsync(Book.ChapterId, Book.Pages[PageIndex].PageId,
                mode: "original", scrollOffsetY: _scrollOffset, cancellationToken: cancellationToken);
            IsSavingProgress = false;
            Status = result.IsSaved ? "阅读进度已保存。" : $"阅读进度写回失败（{result.ErrorCode ?? result.Status.ToString()}），阅读不受影响。";
            State = result.IsSaved ? FluentPageState.Ready : FluentPageState.Partial;
        }

        return loaded;
    }

    public Task<bool> NextAsync(CancellationToken cancellationToken = default) => NavigateAsync(1, cancellationToken);
    public Task<bool> PreviousAsync(CancellationToken cancellationToken = default) => NavigateAsync(-1, cancellationToken);
    public void ZoomBy(double delta) => Zoom += delta;
    public void ResetZoom() => Zoom = 1;
    public void ToggleDoublePage() => DoublePage = !DoublePage;
    public void SetScrollOffset(double offset) => _scrollOffset = Math.Max(0, offset);

    public async Task RetryAsync(CancellationToken cancellationToken = default) =>
        await LoadAsync(_requestedBookId, _requestedChapterId, cancellationToken);

    private async Task<bool> LoadCurrentPageAsync(CancellationToken cancellationToken)
    {
        var page = Book?.Pages.ElementAtOrDefault(PageIndex);
        if (page?.LoadImageAsync is null)
        {
            PageBytes = null;
            State = FluentPageState.Error;
            Error = "页面源不可用，可以重试或返回书架。";
            IsSourceUnavailable = true;
            Changed(nameof(IsSourceUnavailable));
            return false;
        }

        try
        {
            var bytes = await page.LoadImageAsync(cancellationToken);
            if (bytes is null || bytes.Length == 0)
            {
                State = FluentPageState.Partial;
                Error = "页面未就绪，可以重试；其他页面仍可翻阅。";
                IsSourceUnavailable = true;
                Changed(nameof(IsSourceUnavailable));
                return false;
            }

            PageBytes = bytes;
            IsSourceUnavailable = false;
            Changed(nameof(IsSourceUnavailable));
            State = FluentPageState.Ready;
            Status = $"{Book!.BookTitle} · {Book.ChapterTitle} · {PageLabel}";
            return true;
        }
        catch (Exception ex)
        {
            State = FluentPageState.Error;
            Error = $"页面读取失败（{ex.GetType().Name}），可重试；不会自动跳过。";
            IsSourceUnavailable = true;
            Changed(nameof(IsSourceUnavailable));
            return false;
        }
    }
}

public enum SettingsGroupId
{
    Appearance,
    Providers,
    Network,
    Backup,
    About,
}

public sealed class SettingsViewModel : FluentViewModel
{
    private readonly IHostController? _host;
    private readonly AppearanceCoordinator? _appearance;
    private readonly DesignSystemThemeManager? _themeManager;
    private AppearanceSettings _draft;
    /// <summary>R-017: the canonical settings the draft was last synchronized from (frontend-switch detection).</summary>
    private AppearanceSettings _observedSettings;
    private SettingsGroupId _selectedGroup;
    private string _search = string.Empty;
    private string _notice = string.Empty;
    private bool _isSaving;
    private ProviderProfileInfo? _selectedProvider;
    private NetworkProfileInfo? _selectedNetwork;
    private BackupPackageInfo? _selectedBackup;

    public SettingsViewModel(IHostController? host, AppearanceCoordinator? appearance, DesignSystemThemeManager? themeManager)
    {
        _host = host;
        _appearance = appearance;
        _themeManager = themeManager;
        _draft = appearance?.Settings ?? AppearanceDefaults.Settings;
        _observedSettings = _draft;
        State = host is null ? FluentPageState.Error : FluentPageState.Ready;
        Status = "设置已加载。";
        if (_appearance is not null)
        {
            _appearance.Changed += OnAppearanceChanged;
        }
    }

    public ObservableCollection<ProviderProfileInfo> Providers { get; } = new();
    public ObservableCollection<NetworkProfileInfo> Networks { get; } = new();
    public ObservableCollection<BackupPackageInfo> Backups { get; } = new();
    public IReadOnlyList<CredentialTargetOption> CredentialTargets { get; private set; } = Array.Empty<CredentialTargetOption>();
    public AppearanceSettings Draft { get => _draft; private set => Set(ref _draft, value); }
    public AppearanceCoordinator? AppearanceCoordinator => _appearance;
    public SettingsGroupId SelectedGroup { get => _selectedGroup; set => Set(ref _selectedGroup, value); }
    public string Search { get => _search; set { if (Set(ref _search, value ?? string.Empty)) Changed(nameof(VisibleGroups)); } }
    public string Notice { get => _notice; private set => Set(ref _notice, value); }
    public bool IsSaving { get => _isSaving; private set => Set(ref _isSaving, value); }
    public bool IsDirty => !Equals(Draft, _appearance?.Settings ?? AppearanceDefaults.Settings);
    public bool IsReadOnly => _host is null || !_host.Snapshot.WritesAllowed || _host.Snapshot.State != HostViewState.Ready;
    public bool FluentMaterialAvailable => Draft.FrontendId == "builtin.fluent" && Draft.VisualThemeId == "builtin.fluent-dark";
    public bool IsFluentTheme => Draft.VisualThemeId == "builtin.fluent-dark";
    public ProviderProfileInfo? SelectedProvider { get => _selectedProvider; set => Set(ref _selectedProvider, value); }
    public NetworkProfileInfo? SelectedNetwork { get => _selectedNetwork; set => Set(ref _selectedNetwork, value); }
    public BackupPackageInfo? SelectedBackup { get => _selectedBackup; set => Set(ref _selectedBackup, value); }
    public IReadOnlyList<SettingsGroupId> VisibleGroups => Enum.GetValues<SettingsGroupId>()
        .Where(group => string.IsNullOrWhiteSpace(Search) || GroupLabel(group).Contains(Search, StringComparison.CurrentCultureIgnoreCase) ||
            SearchFields(group).Any(fieldName => fieldName.Contains(Search, StringComparison.CurrentCultureIgnoreCase)))
        .ToArray();
    public string Version => typeof(SettingsViewModel).Assembly.GetName().Version?.ToString() ?? "未知";
    public string License => "GPL-3.0（组件许可详见随包声明）";

    public static string GroupLabel(SettingsGroupId group) => group switch
    {
        SettingsGroupId.Appearance => "外观",
        SettingsGroupId.Providers => "Provider 与凭据",
        SettingsGroupId.Network => "网络",
        SettingsGroupId.Backup => "备份与恢复",
        SettingsGroupId.About => "关于",
        _ => group.ToString(),
    };

    private static IReadOnlyList<string> SearchFields(SettingsGroupId group) => group switch
    {
        SettingsGroupId.Appearance => ["theme.visualThemeId", "theme.frontendId", "appearance.mode", "appearance.contrast",
            "appearance.followSystemAccent", "motion.mode", "motion.categories.navigation", "motion.categories.feedback",
            "motion.categories.decorative", "corners.scale", "material.acrylicStrength", "material.micaEnabled",
            "layout.id", "layout.navigation", "layout.shelf", "layout.density", "layout.workbench", "layout.reader", "schemaVersion"],
        SettingsGroupId.Providers => ["providerId", "displayName", "endpoint", "model", "capabilities", "credential"],
        SettingsGroupId.Network => ["mode", "proxyEndpoint", "verifyTls", "allowProxyFailureDirectFallback"],
        SettingsGroupId.Backup => ["backup", "restore", "frequency", "directory"],
        SettingsGroupId.About => ["version", "license", "open source"],
        _ => Array.Empty<string>(),
    };

    public async Task LoadAsync(CancellationToken cancellationToken = default)
    {
        State = FluentPageState.Loading;
        Status = "正在读取设置…";
        try
        {
            if (_appearance is not null)
            {
                Draft = _appearance.Settings;
                _observedSettings = Draft;
            }

            if (_host is not null)
            {
                Providers.Clear();
                foreach (var item in await _host.ListProviderProfilesAsync(cancellationToken)) Providers.Add(item);
                Networks.Clear();
                foreach (var item in await _host.ListNetworkProfilesAsync(cancellationToken)) Networks.Add(item);
                Backups.Clear();
                foreach (var item in await _host.ListBackupsAsync(cancellationToken)) Backups.Add(item);
                CredentialTargets = await _host.ListCredentialTargetsAsync(cancellationToken);
                Changed(nameof(CredentialTargets));
            }

            State = IsReadOnly ? FluentPageState.ReadOnly : FluentPageState.Ready;
            Status = IsReadOnly ? _host?.Snapshot.ReadOnlyReason ?? "设置只读" : "设置已加载。";
        }
        catch (Exception ex)
        {
            State = FluentPageState.Error;
            Error = $"设置读取失败（{ex.GetType().Name}），可以重试。";
        }
    }

    public void UpdateDraft(AppearanceSettings settings)
    {
        Draft = settings;
        State = IsReadOnly ? FluentPageState.ReadOnly : FluentPageState.Ready;
        Changed(nameof(IsDirty));
    }

    public async Task<bool> SaveAppearanceAsync(CancellationToken cancellationToken = default)
    {
        if (_appearance is null)
        {
            Error = "AppearanceCoordinator 未注入。";
            State = FluentPageState.Error;
            return false;
        }

        if (IsReadOnly)
        {
            Error = "当前 Host 只读，设置保存已禁用。";
            State = FluentPageState.ReadOnly;
            return false;
        }

        if (!ValidateAppearance(out var reason))
        {
            Error = reason;
            State = FluentPageState.Error;
            return false;
        }

        IsSaving = true;
        try
        {
            await _appearance.SaveAsync(Draft, cancellationToken);
            ApplyToThemeManager(Draft);
            Notice = "外观设置已保存。";
            Status = Notice;
            Error = string.Empty;
            State = FluentPageState.Ready;
            Changed(nameof(IsDirty));
            return true;
        }
        catch (Exception ex)
        {
            Error = $"外观保存失败（{ex.GetType().Name}），输入仍保留；请重试。";
            Notice = Error;
            State = FluentPageState.Error;
            return false;
        }
        finally
        {
            IsSaving = false;
        }
    }

    public void ResetAppearance()
    {
        Draft = AppearanceDefaults.Settings with { FrontendId = Draft.FrontendId };
        Notice = "外观组已恢复为默认值；点击保存后生效。";
        Changed(nameof(IsDirty));
    }

    public async Task<bool> ToggleProviderAsync(ProviderProfileInfo profile, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var draft = new ProviderProfileDraft(profile.ProviderId, profile.DisplayName, profile.Capabilities,
            profile.Endpoint, profile.Model, profile.NetworkProfileId, !profile.Enabled);
        var result = await _host.SaveProviderProfileAsync(profile.ProfileId, draft, cancellationToken);
        Notice = result.IsSuccess ? "Provider 状态已更新。" : $"Provider 更新失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await LoadProfilesAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> SaveProviderAsync(string? profileId, ProviderProfileDraft draft, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.SaveProviderProfileAsync(profileId, draft, cancellationToken);
        Notice = result.IsSuccess ? "Provider Profile 已保存。" : $"Provider 保存失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> DeleteProviderAsync(ProviderProfileInfo profile, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.DeleteProviderProfileAsync(profile.ProfileId, cancellationToken);
        Notice = result.IsSuccess ? "Provider Profile 已删除。" : $"Provider 删除失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> SaveNetworkAsync(string? profileId, NetworkProfileDraft draft, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.SaveNetworkProfileAsync(profileId, draft, cancellationToken);
        Notice = result.IsSuccess ? "网络 Profile 已保存。" : $"网络设置失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<bool> DeleteNetworkAsync(NetworkProfileInfo profile, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.DeleteNetworkProfileAsync(profile.NetworkProfileId, cancellationToken);
        Notice = result.IsSuccess ? "网络 Profile 已删除。" : $"网络 Profile 删除失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        await ReloadProfileListsAsync(cancellationToken);
        return result.IsSuccess;
    }

    public async Task<NetworkTestInfo?> TestNetworkAsync(NetworkProfileInfo network, ProviderProfileInfo provider,
        CancellationToken cancellationToken = default)
    {
        if (_host is null) return null;
        var result = await _host.TestNetworkProfileAsync(network.NetworkProfileId, provider.ProfileId, cancellationToken);
        Notice = result?.Summary ?? "网络诊断不可用。";
        return result;
    }

    public async Task<bool> SetNetworkDefaultAsync(NetworkProfileInfo network, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var result = await _host.SetNetworkDefaultAsync(network.NetworkProfileId, cancellationToken);
        Notice = result.IsSuccess ? "默认网络 Profile 已更新。" : $"更新失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        return result.IsSuccess;
    }

    public async Task<bool> CreateBackupAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var backup = await _host.CreateBackupAsync("manual", cancellationToken);
        if (backup is null)
        {
            Notice = $"备份未创建（{_host.Snapshot.LastError ?? "HOST_NOT_READY"}）。";
            return false;
        }

        Backups.Insert(0, backup);
        SelectedBackup = backup;
        Notice = backup.Verified ? "备份已创建并校验。" : "备份已创建，Core 尚未确认校验。";
        return true;
    }

    public async Task<bool> DeleteBackupAsync(BackupPackageInfo backup, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly) return false;
        var deleted = await _host.DeleteBackupAsync(backup.BackupId, cancellationToken);
        Notice = deleted ? "备份包已删除。" : $"删除未完成（{_host.Snapshot.LastError ?? "未确认"}）。";
        if (deleted)
        {
            Backups.Remove(backup);
            SelectedBackup = null;
        }

        return deleted;
    }

    public async Task<string?> RestoreBackupAsync(BackupPackageInfo backup, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || !backup.Verified) return null;
        var rollbackBackupId = await _host.RestoreBackupAsync(backup.BackupId, cancellationToken);
        Notice = rollbackBackupId is null
            ? $"恢复未完成（{_host.Snapshot.LastError ?? "Core 未确认"}）。"
            : $"恢复已完成；恢复前回滚包：{rollbackBackupId}";
        return rollbackBackupId;
    }

    public async Task<CredentialOperationResult?> SaveCredentialAsync(
        CredentialTargetOption target, string secret, CancellationToken cancellationToken = default)
    {
        if (_host is null || IsReadOnly || string.IsNullOrEmpty(secret)) return null;
        var intent = target.CredentialState == "configured" ? "replace" : "create";
        var result = await _host.PutCredentialAsync(target.Kind, target.OwnerId, intent, secret, cancellationToken);
        Notice = result.IsSuccess ? "凭据引用已更新；明文不会回显。" : $"凭据保存失败（{result.ErrorCode ?? result.Status.ToString()}）。";
        CredentialTargets = await _host.ListCredentialTargetsAsync(cancellationToken);
        Changed(nameof(CredentialTargets));
        return result;
    }

    private async Task LoadProfilesAsync(CancellationToken cancellationToken)
    {
        if (_host is null) return;
        Providers.Clear();
        foreach (var item in await _host.ListProviderProfilesAsync(cancellationToken)) Providers.Add(item);
    }

    private async Task ReloadProfileListsAsync(CancellationToken cancellationToken)
    {
        if (_host is null) return;
        Providers.Clear();
        foreach (var item in await _host.ListProviderProfilesAsync(cancellationToken)) Providers.Add(item);
        Networks.Clear();
        foreach (var item in await _host.ListNetworkProfilesAsync(cancellationToken)) Networks.Add(item);
    }

    private bool ValidateAppearance(out string reason)
    {
        if (Draft.MaterialAcrylicStrength is < 0 or > 1)
        {
            reason = "Acrylic strength 必须在 0 到 1 之间。";
            return false;
        }

        if (Draft.FrontendId is not ("builtin.current-v2" or "builtin.fluent") ||
            Draft.VisualThemeId is not ("newmanga-default" or "builtin.fluent-dark"))
        {
            reason = "frontendId 或 visualThemeId 不在 C-02 冻结值域内。";
            return false;
        }

        reason = string.Empty;
        return true;
    }

    private void ApplyToThemeManager(AppearanceSettings settings)
    {
        if (_themeManager is null) return;
        var mode = settings.Mode switch
        {
            NewManga.Appearance.AppearanceMode.Light => NewManga.DesignSystem.Theming.AppearanceMode.Light,
            NewManga.Appearance.AppearanceMode.Dark => NewManga.DesignSystem.Theming.AppearanceMode.Dark,
            _ => NewManga.DesignSystem.Theming.AppearanceMode.System,
        };
        _themeManager.SetAppearance(mode);
        _themeManager.SetContrast(settings.Contrast == AppearanceContrast.High
            ? ContrastMode.High
            : ContrastMode.Standard);
        var motion = new MotionResolver(new WindowsMotionPreferenceSource()).Resolve(settings).Settings;
        _themeManager.SetReducedMotion(!motion.Enabled);
        _themeManager.SetDensity(settings.Layout.Density == "compact" ? DensityMode.Compact : DensityMode.Spacious);
    }

    private void OnAppearanceChanged(object? sender, EventArgs args)
    {
        if (_appearance is null) return;
        if (Dispatcher.UIThread.CheckAccess())
        {
            ApplyCoordinatorSettings();
        }
        else
        {
            // FEA-07: the coordinator may raise Changed from a pool thread after an async save; the
            // settings surface mutates controls and must always observe it on the UI thread.
            Dispatcher.UIThread.Post(ApplyCoordinatorSettings);
        }
    }

    private void ApplyCoordinatorSettings()
    {
        if (_appearance is null) return;
        var settings = _appearance.Settings;
        var previous = _observedSettings;
        if (Equals(previous, settings))
        {
            return; // no canonical change; never clobber an unapplied draft on a duplicate notification.
        }

        _observedSettings = settings;

        // FEA-07 R-017/A01: a runtime frontend switch persists only theme.frontendId. Such a
        // frontend-only canonical change must not silently discard the user's unapplied appearance draft
        // (the hidden Fluent tree keeps its state across the switch); adopt the new frontend id into the
        // draft and keep the rest. Any other external appearance change mirrors the single writer.
        Draft = Equals(previous with { FrontendId = settings.FrontendId }, settings)
            ? Draft with { FrontendId = settings.FrontendId }
            : settings;
        Changed(nameof(IsDirty));
    }
}
