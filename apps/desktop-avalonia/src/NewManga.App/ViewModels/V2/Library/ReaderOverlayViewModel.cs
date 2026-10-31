using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.Library;

public enum ReaderLayoutMode
{
    Paged,
    Webtoon,
}

public enum ReaderDirection
{
    Rtl,
    Ltr,
}

/// <summary>
/// REALUSE-DATA-SAFETY-6 AC1 (audit MA-09): one committed reader save, published to the Library so
/// the shelf detail can mirror the position the Core just accepted. <see cref="PageNumber"/> is
/// 1-based and names the page that was saved, <see cref="PageCount"/> the reader's page count for
/// the same chapter -- together they are exactly the dual-modality progress the reader shows.
/// <see cref="IsClosing"/> tells the Library the overlay is going away, i.e. the shelf becomes
/// visible and should re-read the authoritative Core projection instead of only mirroring.
/// </summary>
public readonly record struct ReaderProgressSavedEvent(
    string BookId,
    string ChapterId,
    int PageNumber,
    int PageCount,
    bool IsClosing,
    ReaderProgressSaveResult Result);

/// <summary>
/// V11R-B-1: the Library reading overlay (screen spec §2 / FUSION_SPEC §2.1: reading is a Library
/// overlay, not a separate space). Supports paged RTL/LTR and webtoon vertical layouts, shows the
/// dual-modality progress (page number + percentage), saves progress through the real
/// <see cref="IHostController.SaveReadingProgressAsync"/> seam and never crashes on a missing Core.
/// REALUSE-DATA-SAFETY-6 AC1: a committed save is published through
/// <c>progressSaved</c> so the shelf cannot keep showing a stale position (MA-09).
/// </summary>
public sealed class ReaderOverlayViewModel : ObservableObject
{
    private readonly IHostController _controller;
    private readonly Action<string, NmStatus> _notify;
    private readonly Func<ReaderProgressSavedEvent, Task>? _progressSaved;
    private ReaderBookData? _book;
    private int _pageIndex;
    private ReaderLayoutMode _layout = ReaderLayoutMode.Paged;
    private ReaderDirection _direction = ReaderDirection.Rtl;
    private bool _isOpen;
    private bool _isLoading;
    private string? _errorMessage;
    private double _webtoonPercent;
    private string _saveStatusText = "进度：未保存";
    private bool _isSaving;

    public ReaderOverlayViewModel(
        IHostController controller,
        Action<string, NmStatus> notify,
        Func<ReaderProgressSavedEvent, Task>? progressSaved = null)
    {
        _controller = controller;
        _notify = notify;
        _progressSaved = progressSaved;
        Pages = new ObservableCollection<ReaderPageItem>();
        CloseCommand = new RelayCommand(() => _ = CloseAsync());
        NextPageCommand = new RelayCommand(() => _ = NextAsync());
        PreviousPageCommand = new RelayCommand(() => _ = PreviousAsync());
        ToggleLayoutCommand = new RelayCommand(() => _ = ToggleLayoutAsync());
        ToggleDirectionCommand = new RelayCommand(() => _ = ToggleDirectionAsync());
        RetryCommand = new RelayCommand(() => _ = OpenAsync(BookId, ChapterId));
    }

    public ObservableCollection<ReaderPageItem> Pages { get; }

    public RelayCommand CloseCommand { get; }

    public RelayCommand NextPageCommand { get; }

    public RelayCommand PreviousPageCommand { get; }

    public RelayCommand ToggleLayoutCommand { get; }

    public RelayCommand ToggleDirectionCommand { get; }

    public RelayCommand RetryCommand { get; }

    public bool IsOpen
    {
        get => _isOpen;
        private set => Set(ref _isOpen, value);
    }

    public bool IsLoading
    {
        get => _isLoading;
        private set => Set(ref _isLoading, value);
    }

    public string? ErrorMessage
    {
        get => _errorMessage;
        private set
        {
            if (Set(ref _errorMessage, value))
            {
                OnPropertyChanged(nameof(HasError));
            }
        }
    }

    public bool HasError => !string.IsNullOrWhiteSpace(ErrorMessage);

    public ReaderBookData? Book => _book;

    public string? BookId => _book?.BookId;

    public string? ChapterId => _book?.ChapterId;

    public bool HasBook => _book is not null && Pages.Count > 0;

    public string Title => _book is null ? "阅读" : _book.BookTitle;

    public string Subtitle => _book is null ? string.Empty : _book.ChapterTitle;

    public int PageCount => Pages.Count;

    public int PageIndex
    {
        get => _pageIndex;
        private set
        {
            if (Set(ref _pageIndex, value))
            {
                OnPropertyChanged(
                    nameof(CurrentPage),
                    nameof(CurrentPageHasImage),
                    nameof(CurrentPageLabel),
                    nameof(PageLabel),
                    nameof(ProgressPercent),
                    nameof(ProgressText));
            }
        }
    }

    public ReaderPageItem? CurrentPage => PageIndex >= 0 && PageIndex < Pages.Count ? Pages[PageIndex] : null;

    public string PageLabel => Pages.Count == 0 ? "—" : $"第 {PageIndex + 1} / {Pages.Count} 页";

    /// <summary>Paged view state: true when the current page image really loaded through the Host channel.</summary>
    public bool CurrentPageHasImage => CurrentPage?.HasImage == true;

    public string CurrentPageLabel => CurrentPage?.Label ?? "—";

    public ReaderLayoutMode Layout
    {
        get => _layout;
        private set
        {
            if (Set(ref _layout, value))
            {
                OnPropertyChanged(nameof(IsWebtoon), nameof(IsPaged), nameof(LayoutLabel));
            }
        }
    }

    public bool IsWebtoon => Layout == ReaderLayoutMode.Webtoon;

    public bool IsPaged => Layout == ReaderLayoutMode.Paged;

    public string LayoutLabel => IsWebtoon ? "Webtoon 纵向" : "分页";

    public ReaderDirection Direction
    {
        get => _direction;
        private set
        {
            if (Set(ref _direction, value))
            {
                OnPropertyChanged(nameof(DirectionLabel));
            }
        }
    }

    public string DirectionLabel => Direction == ReaderDirection.Rtl ? "RTL" : "LTR";

    public double ProgressPercent => Pages.Count == 0
        ? 0
        : IsWebtoon
            ? Math.Clamp(_webtoonPercent * 100, 0, 100)
            : Math.Clamp((PageIndex + 1) * 100.0 / Pages.Count, 0, 100);

    /// <summary>Dual-modality progress: page number AND percentage are always both visible.</summary>
    public string ProgressText => Pages.Count == 0
        ? "—"
        : $"{PageLabel} · {ProgressPercent:0}%";

    public string SaveStatusText
    {
        get => _saveStatusText;
        private set => Set(ref _saveStatusText, value);
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-6 AC1: typed outcome of the last save attempt (null before the first
    /// one). Honest evidence for the shelf-consistency tests: only <c>Saved</c> may refresh the
    /// shelf, so the reader keeps the raw result instead of only its display text.
    /// </summary>
    public ReaderProgressSaveResult? LastSaveResult { get; private set; }

    /// <summary>Opens the overlay at the resume position returned by the Host. Never throws.</summary>
    public async Task<bool> OpenAsync(string? bookId = null, string? chapterId = null, int? startPage = null)
    {
        if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(chapterId))
        {
            _notify("请先在资料柜选择作品与章节，再打开阅读浮层", NmStatus.Blocked);
            return false;
        }

        IsOpen = true;
        IsLoading = true;
        ErrorMessage = null;
        SaveStatusText = "进度：未保存";
        ReleaseImages();
        Pages.Clear();
        _book = null;
        try
        {
            var data = await _controller.LoadReaderBookAsync(bookId, chapterId).ConfigureAwait(true);
            if (data is null)
            {
                ErrorMessage = "阅读投影不可用：Host 未就绪或该章节没有页面。";
                return false;
            }

            _book = data;
            for (var index = 0; index < data.Pages.Count; index++)
            {
                Pages.Add(new ReaderPageItem(data.Pages[index], index));
            }

            var initial = startPage is { } page
                ? Math.Clamp(page - 1, 0, Math.Max(0, Pages.Count - 1))
                : Math.Clamp(data.InitialPageIndex, 0, Math.Max(0, Pages.Count - 1));
            PageIndex = initial;
            _webtoonPercent = 0;
            Layout = data.IsWebtoon ? ReaderLayoutMode.Webtoon : ReaderLayoutMode.Paged;
            OnPropertyChanged(nameof(Title), nameof(Subtitle), nameof(HasBook), nameof(PageCount), nameof(PageLabel), nameof(ProgressPercent), nameof(ProgressText), nameof(CurrentPage));
            if (Pages.Count == 0)
            {
                ErrorMessage = "该章节没有可阅读的页面。";
                return false;
            }

            await LoadCurrentImageAsync().ConfigureAwait(true);
            SaveStatusText = data.HasSavedProgress
                ? $"进度：续读到第 {initial + 1} 页（Core 已保存）"
                : "进度：开始阅读（Core 尚无进度行）";
            return true;
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            ErrorMessage = "阅读投影读取失败：" + ex.Message;
            return false;
        }
        finally
        {
            IsLoading = false;
        }
    }

    public async Task CloseAsync()
    {
        // MA-09: the closing save is the last one the reader performs, and the shelf becomes visible
        // right after it, so the Library re-reads the authoritative projection on this pass.
        await SaveProgressAsync(isClosing: true).ConfigureAwait(true);
        IsOpen = false;
        ReleaseImages();
        _book = null;
        Pages.Clear();
        PageIndex = 0;
        OnPropertyChanged(nameof(Title), nameof(Subtitle), nameof(HasBook), nameof(PageCount), nameof(PageLabel), nameof(ProgressText));
    }

    public Task NextAsync() => GoToAsync(PageIndex + 1);

    public Task PreviousAsync() => GoToAsync(PageIndex - 1);

    public async Task GoToAsync(int index)
    {
        if (Pages.Count == 0)
        {
            return;
        }

        var clamped = Math.Clamp(index, 0, Pages.Count - 1);
        if (clamped == PageIndex)
        {
            return;
        }

        PageIndex = clamped;
        _webtoonPercent = Pages.Count <= 1 ? 0 : (double)clamped / (Pages.Count - 1);
        OnPropertyChanged(nameof(ProgressPercent), nameof(ProgressText));
        await LoadCurrentImageAsync().ConfigureAwait(true);
        await SaveProgressAsync().ConfigureAwait(true);
    }

    public async Task ToggleLayoutAsync()
    {
        Layout = IsWebtoon ? ReaderLayoutMode.Paged : ReaderLayoutMode.Webtoon;
        if (IsWebtoon)
        {
            await LoadAllImagesAsync().ConfigureAwait(true);
        }
        else
        {
            await LoadCurrentImageAsync().ConfigureAwait(true);
        }
    }

    public Task ToggleDirectionAsync()
    {
        Direction = Direction == ReaderDirection.Rtl ? ReaderDirection.Ltr : ReaderDirection.Rtl;
        return Task.CompletedTask;
    }

    /// <summary>Webtoon progress from the viewport scroll (0..1). Page number is derived for the save.</summary>
    public void UpdateWebtoonProgress(double percent)
    {
        _webtoonPercent = Math.Clamp(percent, 0, 1);
        var derived = Pages.Count <= 1 ? 0 : (int)Math.Round(_webtoonPercent * (Pages.Count - 1));
        if (derived != PageIndex)
        {
            _pageIndex = derived;
            OnPropertyChanged(nameof(PageIndex), nameof(CurrentPage), nameof(PageLabel));
        }

        OnPropertyChanged(nameof(ProgressPercent), nameof(ProgressText));
    }

    public async Task SaveProgressAsync(bool isClosing = false)
    {
        if (_book is null || Pages.Count == 0 || _isSaving)
        {
            return;
        }

        _isSaving = true;
        try
        {
            var page = CurrentPage ?? Pages[0];
            var result = await _controller.SaveReadingProgressAsync(
                _book.ChapterId,
                page.PageId,
                "original",
                scrollOffsetY: null).ConfigureAwait(true);
            LastSaveResult = result;
            SaveStatusText = result.Status switch
            {
                ReaderProgressSaveStatus.Saved => "进度：已保存到 Core",
                ReaderProgressSaveStatus.NotReady => "进度：未保存（Host 未就绪）",
                ReaderProgressSaveStatus.ReadOnly => "进度：未保存（Host 只读）",
                ReaderProgressSaveStatus.Failed => $"进度：保存失败（{result.ErrorCode}）",
                _ => "进度：未保存",
            };
            OnPropertyChanged(nameof(SaveStatusText));

            // MA-09 (REALUSE-DATA-SAFETY-6 AC1): publish the committed position so the shelf detail
            // refreshes in the same user action. Only a real commit is mirrored -- a typed refusal
            // (NotReady / ReadOnly / Failed) changes nothing in the Core, so nothing may change on
            // the shelf either.
            if (result.IsSaved && _progressSaved is not null)
            {
                await _progressSaved(new ReaderProgressSavedEvent(
                    _book.BookId,
                    _book.ChapterId,
                    page.Index + 1,
                    Pages.Count,
                    isClosing,
                    result)).ConfigureAwait(true);
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            SaveStatusText = "进度：保存失败（Host 不可用）";
        }
        finally
        {
            _isSaving = false;
        }
    }

    private async Task LoadCurrentImageAsync()
    {
        if (CurrentPage is { } page)
        {
            await page.LoadAsync().ConfigureAwait(true);
            OnPropertyChanged(nameof(CurrentPageHasImage));
        }
    }

    private async Task LoadAllImagesAsync()
    {
        foreach (var page in Pages)
        {
            await page.LoadAsync().ConfigureAwait(true);
        }
    }

    private void ReleaseImages()
    {
        foreach (var page in Pages)
        {
            page.Image?.Dispose();
        }
    }
}
