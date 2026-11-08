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
    private byte[]? _pageBytesSecondary;
    private string? _secondaryPageId;
    private bool _isSavingProgress;
    private bool _areToolBarsVisible = true;
    private bool _isSideRailVisible = true;
    private bool _areToolBarsReducedMotion;
    private string? _requestedBookId;
    private string? _requestedChapterId;

    public ReaderViewModel(IHostController? host) => _host = host;

    /// <summary>I-10：顶部/底部条当前可见状态；2s 空闲后隐藏，交互唤醒（07:23）。</summary>
    public bool AreToolBarsVisible
    {
        get => _areToolBarsVisible;
        private set => Set(ref _areToolBarsVisible, value);
    }

    /// <summary>I-10：右侧浮动工具条常显、可显式隐藏（07:62）；不参与 2s 自动隐藏。</summary>
    public bool IsSideRailVisible
    {
        get => _isSideRailVisible;
        set => Set(ref _isSideRailVisible, value);
    }

    /// <summary>I-10：reduce 下工具条直接切换、无淡出过渡（07:23）；由 shell 在 motion 解析后同步。</summary>
    public bool AreToolBarsReducedMotion
    {
        get => _areToolBarsReducedMotion;
        set => Set(ref _areToolBarsReducedMotion, value);
    }

    /// <summary>I-10：任意指针/键盘交互让顶部/底部条重新可见（视图会重启 2s 空闲计时器）。</summary>
    public void PokeToolBars() => AreToolBarsVisible = true;

    /// <summary>I-10：点击页面中部切换顶部/底部条显隐（07:23）。</summary>
    public void ToggleToolBars() => AreToolBarsVisible = !AreToolBarsVisible;

    /// <summary>I-10：2s 空闲窗口到期（由视图的 DispatcherTimer 驱动）；reduce 下同样隐藏、只是切换方式不同。</summary>
    public void HideToolBarsAfterIdle() => AreToolBarsVisible = false;

    /// <summary>I-10：切换右侧浮动工具条显隐（常显语义下的显式隐藏入口）。</summary>
    public void ToggleSideRail() => IsSideRailVisible = !IsSideRailVisible;

    public ReaderBookData? Book { get => _book; private set => Set(ref _book, value); }
    public int PageIndex { get => _pageIndex; private set => Set(ref _pageIndex, value); }
    public int PageCount => Book?.Pages.Count ?? 0;
    public double Zoom { get => _zoom; private set => Set(ref _zoom, Math.Clamp(value, 0.2, 5)); }
    public bool IsFullScreen { get => _isFullScreen; set => Set(ref _isFullScreen, value); }
    public bool DoublePage { get => _doublePage; set => Set(ref _doublePage, value); }
    public bool ReverseDirection { get => _reverseDirection; set => Set(ref _reverseDirection, value); }
    public string Layout { get => _layout; set => Set(ref _layout, value); }
    public byte[]? PageBytes { get => _pageBytes; private set => Set(ref _pageBytes, value); }

    /// <summary>
    /// AC-3（格 2）：双页 / 滚动模式下相邻页 <c>Pages[i+1]</c> 的字节；单页模式恒为 null。
    /// </summary>
    public byte[]? PageBytesSecondary { get => _pageBytesSecondary; private set => Set(ref _pageBytesSecondary, value); }

    /// <summary>AC-3：当前页 pageId（Host 投影值；无书时 null）。</summary>
    public string? PageId => Book?.Pages.ElementAtOrDefault(PageIndex)?.PageId;

    /// <summary>AC-3：相邻页 pageId；单页 / 末页为 null（不得复用当前页 bytes 充数）。</summary>
    public string? SecondaryPageId
    {
        get => _secondaryPageId;
        private set => Set(ref _secondaryPageId, value);
    }

    /// <summary>AC-3：是否滚动（webtoon）模式——<c>IsWebtoon</c> 或 <c>Layout=webtoon_vertical</c>。</summary>
    public bool IsWebtoon => Book?.IsWebtoon == true ||
        Layout.Contains("webtoon", StringComparison.OrdinalIgnoreCase);

    /// <summary>AC-3：滚动模式最近一次记录的 <c>scrollOffsetY</c>（webtoon 逻辑页像素）。</summary>
    public double ScrollOffsetY => _scrollOffset;

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
                PageBytesSecondary = null;
                SecondaryPageId = null;
                return;
            }

            Book = loaded;
            Layout = loaded.Layout;
            PageIndex = Math.Clamp(loaded.InitialPageIndex, 0, loaded.Pages.Count - 1);
            _scrollOffset = loaded.InitialScrollOffsetY;
            await LoadCurrentPageAsync(cancellationToken);
            // AC-3：Layout / IsWebtoon / DoublePage 任一变化都会改变「第二页」的存在性，
            // 让视图（滚动区）在加载完成后重新求值一次。
            Changed(nameof(IsWebtoon));
            Changed(nameof(PageId));
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

    /// <summary>
    /// AC-3（格 2）：切换双页模式。开启时补载 Pages[i+1]（每页恰 1 次 LoadImageAsync）；
    /// 关闭时清空第二页，确保单页模式不残留第二页字节。
    /// </summary>
    public void ToggleDoublePage()
    {
        DoublePage = !DoublePage;
        if (!DoublePage)
        {
            PageBytesSecondary = null;
            SecondaryPageId = null;
            return;
        }

        _ = LoadSecondaryPageAsync(CancellationToken.None);
    }

    public void SetScrollOffset(double offset) => _scrollOffset = Math.Max(0, offset);

    /// <summary>
    /// AC-3：把当前滚动偏移写回 Host 进度（webtoon 逻辑页像素）。这是既有
    /// <see cref="IReaderProgressSink.SaveReadingProgressAsync"/> 端口，不新增命令。
    /// </summary>
    public async Task<bool> SaveScrollProgressAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || Book is null || PageCount == 0)
        {
            return false;
        }

        var page = Book.Pages[PageIndex];
        IsSavingProgress = true;
        try
        {
            var result = await _host.SaveReadingProgressAsync(Book.ChapterId, page.PageId,
                mode: "original", scrollOffsetY: _scrollOffset, cancellationToken: cancellationToken);
            Status = result.IsSaved
                ? "阅读进度已保存。"
                : $"阅读进度写回失败（{result.ErrorCode ?? result.Status.ToString()}），阅读不受影响。";
            return result.IsSaved;
        }
        catch (Exception exception)
        {
            Status = $"阅读进度写回失败（{exception.GetType().Name}），阅读不受影响。";
            return false;
        }
        finally
        {
            IsSavingProgress = false;
        }
    }

    public async Task RetryAsync(CancellationToken cancellationToken = default) =>
        await LoadAsync(_requestedBookId, _requestedChapterId, cancellationToken);

    /// <summary>
    /// AC-3（格 2）：加载当前页，并在双页 / 滚动（webtoon）模式下额外加载 <c>Pages[i+1]</c>。
    /// 每页恰各 1 次 <c>LoadImageAsync</c>，pageId 不同；末页只有 1 次（不复用当前页 bytes 充数）。
    /// 单页模式仍只加载当前页（不回归）。
    /// </summary>
    private async Task<bool> LoadCurrentPageAsync(CancellationToken cancellationToken)
    {
        var page = Book?.Pages.ElementAtOrDefault(PageIndex);
        if (page?.LoadImageAsync is null)
        {
            PageBytes = null;
            PageBytesSecondary = null;
            SecondaryPageId = null;
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
            await LoadSecondaryPageAsync(cancellationToken);
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

    /// <summary>
    /// AC-3：双页 / webtoon 连续页的第二页。第二页失败不覆盖当前页的可用状态（只隐藏第二页，
    /// 诚实告知「相邻页不可用」），不会影响单页阅读与进度写回。
    /// </summary>
    private async Task LoadSecondaryPageAsync(CancellationToken cancellationToken)
    {
        var nextIndex = (DoublePage || IsWebtoon) && PageIndex + 1 < PageCount ? PageIndex + 1 : (int?)null;
        var next = nextIndex is { } index ? Book?.Pages.ElementAtOrDefault(index) : null;
        var loader = next?.LoadImageAsync;
        if (loader is null || next is null)
        {
            PageBytesSecondary = null;
            SecondaryPageId = null;
            return;
        }

        try
        {
            var bytes = await loader(cancellationToken);
            if (bytes is null || bytes.Length == 0)
            {
                PageBytesSecondary = null;
                SecondaryPageId = null;
                return;
            }

            PageBytesSecondary = bytes;
            SecondaryPageId = next.PageId;
        }
        catch (Exception)
        {
            // 第二页读取失败：保持单页可读，不把整页降级为错误（失败不会自动跳过当前页）。
            PageBytesSecondary = null;
            SecondaryPageId = null;
        }
    }
}
