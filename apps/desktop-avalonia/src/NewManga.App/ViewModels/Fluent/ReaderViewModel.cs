using NewManga.App.Services;

namespace NewManga.App.ViewModels.Fluent;

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
