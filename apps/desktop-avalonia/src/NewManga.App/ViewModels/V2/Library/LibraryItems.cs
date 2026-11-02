using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.CoreClient;

namespace NewManga.App.ViewModels.V2.Library;

/// <summary>One book cover row of the Library PageGrid (real <see cref="BookSummary"/>, no fake status).</summary>
public sealed class BookRowViewModel : ObservableObject
{
    private bool _isSelected;

    public BookRowViewModel(BookSummary book, Action<BookRowViewModel> onSelect)
    {
        BookId = book.BookId;
        Title = string.IsNullOrWhiteSpace(book.Title) ? "（未命名）" : book.Title;
        OriginalTitle = book.OriginalTitle ?? string.Empty;
        IsFavorite = book.IsFavorite;
        IsArchived = book.IsArchived;
        PageCount = book.PageCount;
        UpdatedAt = ParseTimestamp(book.UpdatedAt);
        CreatedAt = ParseTimestamp(book.CreatedAt);
        SelectCommand = new RelayCommand(() => onSelect(this));
    }

    public RelayCommand SelectCommand { get; }

    public string BookId { get; }

    public string Title { get; }

    public string AutomationName => $"打开作品：{Title}";

    public string OriginalTitle { get; }

    public bool IsFavorite { get; }

    public bool IsArchived { get; }

    public int? PageCount { get; }

    public DateTimeOffset UpdatedAt { get; }

    public DateTimeOffset CreatedAt { get; }

    public string Glyph
    {
        get
        {
            if (string.IsNullOrEmpty(Title))
            {
                return "书";
            }

            var element = System.Globalization.StringInfo.GetNextTextElement(Title);
            return string.IsNullOrEmpty(element) ? "书" : element;
        }
    }

    public string MetaText => PageCount is { } pages ? $"{pages} 页" : "页数未知";

    public string BadgeText => IsArchived ? "已归档" : IsFavorite ? "收藏" : string.Empty;

    public bool HasBadge => BadgeText.Length > 0;

    public bool IsSelected
    {
        get => _isSelected;
        private set => Set(ref _isSelected, value);
    }

    public bool Matches(string query) =>
        PinyinIndex.Matches(Title, query) || PinyinIndex.Matches(OriginalTitle, query);

    public void SetSelected(bool selected) => IsSelected = selected;

    private static DateTimeOffset ParseTimestamp(string? value) =>
        DateTimeOffset.TryParse(
            value,
            System.Globalization.CultureInfo.InvariantCulture,
            System.Globalization.DateTimeStyles.AssumeUniversal,
            out var parsed)
            ? parsed
            : DateTimeOffset.MinValue;
}

/// <summary>One row of the chapter ledger (chapter ids are real; page count is loaded on demand).</summary>
public sealed class ChapterRowViewModel : ObservableObject
{
    private bool _isSelected;
    private string _pageCountText = "—";
    private bool _isPageCountKnown;

    public ChapterRowViewModel(ChapterSummary chapter, int index, Action<ChapterRowViewModel> onSelect)
    {
        ChapterId = chapter.ChapterId;
        Title = string.IsNullOrWhiteSpace(chapter.Title) ? $"第 {index + 1} 章" : chapter.Title;
        Number = chapter.ChapterNumber ?? string.Empty;
        SortOrder = chapter.SortOrder;
        Index = index;
        SelectCommand = new RelayCommand(() => onSelect(this));
    }

    public RelayCommand SelectCommand { get; }

    public string ChapterId { get; }

    public string Title { get; }

    public string AutomationName => $"打开章节：{Title}";

    public string Number { get; }

    public int SortOrder { get; }

    public int Index { get; }

    public string IndexText => (Index + 1).ToString("00");

    public string MetaText => string.IsNullOrWhiteSpace(Number) ? "章" : $"第 {Number} 章";

    public string PageCountText
    {
        get => _pageCountText;
        private set => Set(ref _pageCountText, value);
    }

    public bool IsPageCountKnown
    {
        get => _isPageCountKnown;
        private set => Set(ref _isPageCountKnown, value);
    }

    public bool IsSelected
    {
        get => _isSelected;
        private set => Set(ref _isSelected, value);
    }

    public void SetSelected(bool selected) => IsSelected = selected;

    public void SetPageCount(int? count)
    {
        IsPageCountKnown = count is not null;
        PageCountText = count is { } pages ? $"{pages} 页" : "—";
    }
}

/// <summary>One page row of the selected chapter (real <see cref="ChapterPageSummary"/>).</summary>
public sealed class PageRowViewModel : ObservableObject
{
    private bool _isSelected;
    private bool _isMultiSelected;

    public PageRowViewModel(
        ChapterPageSummary page,
        int index,
        Action<PageRowViewModel> onSelect,
        Action<PageRowViewModel> onToggleMulti)
    {
        PageId = page.PageId;
        Index = index;
        FileName = string.IsNullOrWhiteSpace(page.SourceFilename) ? string.Empty : page.SourceFilename;
        SortOrder = page.SortOrder;
        SelectCommand = new RelayCommand(() => onSelect(this));
        ToggleMultiCommand = new RelayCommand(() => onToggleMulti(this));
    }

    public RelayCommand SelectCommand { get; }

    public RelayCommand ToggleMultiCommand { get; }

    public string PageId { get; }

    public int Index { get; }

    public string FileName { get; }

    public int SortOrder { get; }

    public string Label => (Index + 1).ToString("000");

    public string FileNameText => FileName.Length == 0 ? "页 " + Label : FileName;

    public bool IsSelected
    {
        get => _isSelected;
        private set => Set(ref _isSelected, value);
    }

    public bool IsMultiSelected
    {
        get => _isMultiSelected;
        private set => Set(ref _isMultiSelected, value);
    }

    public void SetSelection(bool selected, bool multiSelected)
    {
        IsSelected = selected;
        IsMultiSelected = multiSelected;
    }
}

/// <summary>Filter chip state (全部 / 收藏 / 已归档) driven by real BookSummary flags.</summary>
public sealed class FilterChipItem : ObservableObject
{
    private bool _isOn;
    private int? _count;

    public FilterChipItem(string key, string label, Action<FilterChipItem> onToggle)
    {
        Key = key;
        Label = label;
        ToggleCommand = new RelayCommand(() => onToggle(this));
    }

    public RelayCommand ToggleCommand { get; }

    public string Key { get; }

    public string Label { get; }

    public bool IsOn
    {
        get => _isOn;
        private set => Set(ref _isOn, value);
    }

    public int? Count
    {
        get => _count;
        private set
        {
            if (Set(ref _count, value))
            {
                OnPropertyChanged(nameof(CountText), nameof(DisplayText));
            }
        }
    }

    public string CountText => Count is { } count
        ? count.ToString(System.Globalization.CultureInfo.InvariantCulture)
        : string.Empty;

    public string DisplayText => Count is null ? Label : $"{Label} {Count}";

    public void SetState(bool isOn, int? count)
    {
        IsOn = isOn;
        Count = count;
    }
}

/// <summary>Sort option shown in the Library sort ComboBox.</summary>
public sealed record LibrarySortOption(string Key, string Label);

/// <summary>One row of the import dock: per-file status (queued/importing/imported/skipped/failed).</summary>
public sealed class ImportRowViewModel : ObservableObject
{
    private ImportRowState _state = ImportRowState.Pending;
    private string _message = "待导入";

    public ImportRowViewModel(string path, bool isFolder)
    {
        Path = path;
        IsFolder = isFolder;
        DisplayName = SafeName(path);
    }

    /// <summary>The user-picked path. Never rendered by the UI (privacy: no OS paths on screen).</summary>
    public string Path { get; }

    public bool IsFolder { get; }

    public string DisplayName { get; }

    public ImportRowState State
    {
        get => _state;
        internal set
        {
            if (Set(ref _state, value))
            {
                OnPropertyChanged(nameof(Status), nameof(Symbol), nameof(StatusLabel), nameof(CanRetry), nameof(IsTerminal));
            }
        }
    }

    public string Message
    {
        get => _message;
        internal set => Set(ref _message, value);
    }

    public NmStatus Status => State switch
    {
        ImportRowState.Pending => NmStatus.Queued,
        ImportRowState.Importing => NmStatus.Running,
        ImportRowState.Imported => NmStatus.Done,
        ImportRowState.Skipped => NmStatus.Skipped,
        ImportRowState.SkippedByUser => NmStatus.Skipped,
        ImportRowState.Failed => NmStatus.Failed,
        _ => NmStatus.NotStarted,
    };

    public string Symbol => NmStatusInfo.Symbol(Status);

    public string StatusLabel => NmStatusInfo.Label(Status);

    public bool CanRetry => State == ImportRowState.Failed;

    public bool IsTerminal => State is ImportRowState.Imported or ImportRowState.Skipped
        or ImportRowState.SkippedByUser or ImportRowState.Failed;

    public void ResetForRetry()
    {
        State = ImportRowState.Pending;
        Message = "待重试";
    }

    private static string SafeName(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            return "（未知文件）";
        }

        var trimmed = path.TrimEnd('/', '\\');
        var separator = trimmed.LastIndexOfAny(new[] { '/', '\\' });
        var name = separator >= 0 ? trimmed[(separator + 1)..] : trimmed;
        return string.IsNullOrWhiteSpace(name) ? "（未知文件）" : name;
    }
}

public enum ImportRowState
{
    Pending,
    Importing,
    Imported,
    Skipped,
    SkippedByUser,
    Failed,
}

/// <summary>One page of the reader overlay; the bitmap is loaded through the Host resource channel.</summary>
public sealed class ReaderPageItem : ObservableObject
{
    private Avalonia.Media.Imaging.Bitmap? _image;
    private bool _isLoaded;

    public ReaderPageItem(ReaderPageData page, int index)
    {
        PageId = page.PageId;
        Index = index;
        WidthPx = page.WidthPx;
        HeightPx = page.HeightPx;
        LoadImageAsync = page.LoadImageAsync;
    }

    public string PageId { get; }

    public int Index { get; }

    public int WidthPx { get; }

    public int HeightPx { get; }

    public Func<CancellationToken, Task<byte[]?>>? LoadImageAsync { get; }

    public string Label => (Index + 1).ToString("000");

    public string MetaText => $"{WidthPx}×{HeightPx}";

    public Avalonia.Media.Imaging.Bitmap? Image
    {
        get => _image;
        private set
        {
            if (Set(ref _image, value))
            {
                OnPropertyChanged(nameof(HasImage));
            }
        }
    }

    public bool IsLoaded
    {
        get => _isLoaded;
        private set => Set(ref _isLoaded, value);
    }

    public bool HasImage => Image is not null;

    public async Task LoadAsync(CancellationToken cancellationToken = default)
    {
        if (IsLoaded || LoadImageAsync is null)
        {
            IsLoaded = true;
            return;
        }

        IsLoaded = true;
        try
        {
            var bytes = await LoadImageAsync(cancellationToken).ConfigureAwait(true);
            if (bytes is { Length: > 0 })
            {
                using var stream = new MemoryStream(bytes);
                Image = new Avalonia.Media.Imaging.Bitmap(stream);
            }
        }
        catch (ArgumentException)
        {
            // Corrupt/unsupported page bytes: keep the placeholder, never crash the reader.
            Image = null;
        }
    }
}
