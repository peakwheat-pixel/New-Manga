using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using NewManga.CoreClient;
using NewManga.Theme;

namespace NewManga.App.ViewModels;

public sealed class BookCardItem
{
    public required string BookId { get; init; }

    public required string Title { get; init; }

    public string OriginalTitle { get; init; } = string.Empty;

    public bool IsFavorite { get; init; }

    public int? PageCount { get; init; }

    public string Tag { get; init; } = "未分类";

    public string Meta => PageCount is { } pages ? $"{pages} 页" : "页数未知";

    public string Glyph => string.IsNullOrEmpty(Title) ? "书" : Title[..1];
}

/// <summary>AC3 bookshelf VM. Grid columns are computed here (Avalonia has no auto-fill).</summary>
public sealed class BookshelfViewModel : INotifyPropertyChanged
{
    public const double CardWidth = 170;
    public const double CardGap = 16;
    public const double MaxContentWidth = 1400;

    private readonly Func<CancellationToken, Task<IReadOnlyList<BookCardItem>>>? _loader;
    private readonly Func<string, CancellationToken, Task<bool>>? _creator;
    private readonly List<BookCardItem> _all = new();
    private string _searchText = string.Empty;
    private string _selectedTag = "全部";
    private int _columnCount = 4;
    private bool _isLoading;
    private BookCardItem? _selectedBook;
    private string? _statusMessage;

    public BookshelfViewModel(
        Func<CancellationToken, Task<IReadOnlyList<BookCardItem>>>? loader = null,
        Func<string, CancellationToken, Task<bool>>? creator = null)
    {
        _loader = loader;
        _creator = creator;
    }

    public event PropertyChangedEventHandler? PropertyChanged;

    public event EventHandler? BooksChanged;

    public ObservableCollection<BookCardItem> Books { get; } = new();

    public ObservableCollection<string> Tags { get; } = new() { "全部" };

    public string SearchText
    {
        get => _searchText;
        set
        {
            if (Set(ref _searchText, value))
            {
                RebuildVisible();
            }
        }
    }

    public string SelectedTag
    {
        get => _selectedTag;
        set
        {
            if (Set(ref _selectedTag, value))
            {
                RebuildVisible();
            }
        }
    }

    public int ColumnCount
    {
        get => _columnCount;
        private set => Set(ref _columnCount, value);
    }

    public bool IsLoading
    {
        get => _isLoading;
        private set => Set(ref _isLoading, value);
    }

    public BookCardItem? SelectedBook
    {
        get => _selectedBook;
        private set
        {
            if (Set(ref _selectedBook, value))
            {
                OnPropertyChanged(nameof(IsDetailOpen));
            }
        }
    }

    public bool IsDetailOpen => SelectedBook is not null;

    public string? StatusMessage
    {
        get => _statusMessage;
        private set => Set(ref _statusMessage, value);
    }

    public bool IsEmpty => Books.Count == 0 && string.IsNullOrWhiteSpace(SearchText) && SelectedTag == "全部";

    public bool HasNoResults => Books.Count == 0 && !IsEmpty;

    public string EmptyTitle => "书架还是空的";

    public string EmptyHint => "新建一本书，或告诉 Host 导入一个文件；数据只经 Core 访问。";

    public string NoResultsTitle => "没有匹配的书";

    public string NoResultsHint => "换个关键词，或切回「全部」标签。";

    public static int ComputeColumns(double availableWidth)
    {
        var content = Math.Max(0, Math.Min(availableWidth, MaxContentWidth) - 2 * 24);
        var columns = (int)Math.Floor((content + CardGap) / (CardWidth + CardGap));
        return Math.Clamp(columns, 2, 8);
    }

    public void UpdateViewport(double availableWidth) => ColumnCount = ComputeColumns(availableWidth);

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        if (_loader is null)
        {
            RebuildVisible();
            return;
        }

        IsLoading = true;
        try
        {
            var items = await _loader(cancellationToken).ConfigureAwait(true);
            _all.Clear();
            _all.AddRange(items);

            var tags = new SortedSet<string>(StringComparer.Ordinal) { "全部" };
            foreach (var item in _all)
            {
                tags.Add(item.Tag);
            }

            Tags.Clear();
            foreach (var tag in tags)
            {
                Tags.Add(tag);
            }

            if (SelectedTag != "全部" && !tags.Contains(SelectedTag))
            {
                SelectedTag = "全部";
            }

            RebuildVisible();
            StatusMessage = _all.Count == 0 ? "Core 返回空书架（隔离数据根或尚未导入）" : $"已加载 {_all.Count} 本（经 command dispatcher）";
        }
        catch (Exception ex) when (ex is NewManga.CoreClient.Commands.HostCommandNotSupportedException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            _all.Clear();
            RebuildVisible();
            StatusMessage = ex is NewManga.CoreClient.Commands.HostCommandNotSupportedException typed
                ? $"命令未迁移：{typed.Code}"
                : "Core 通道不可用（只读骨架仍可浏览）";
        }
        finally
        {
            IsLoading = false;
        }
    }

    public void SetBooks(IEnumerable<BookCardItem> items)
    {
        _all.Clear();
        _all.AddRange(items);
        Tags.Clear();
        var tags = new SortedSet<string>(StringComparer.Ordinal) { "全部" };
        foreach (var item in _all)
        {
            tags.Add(item.Tag);
        }

        foreach (var tag in tags)
        {
            Tags.Add(tag);
        }

        SelectedTag = "全部";
        RebuildVisible();
    }

    public void OpenDetails(BookCardItem? item) => SelectedBook = item;

    public void CloseDetails() => SelectedBook = null;

    public async Task<bool> CreateBookAsync(string title, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(title))
        {
            StatusMessage = "书名不能为空";
            return false;
        }

        if (_creator is null)
        {
            StatusMessage = "只读模式：新建书需要 Core 写权限（S2 只读策略）";
            return false;
        }

        var created = await _creator(title.Trim(), cancellationToken).ConfigureAwait(true);
        StatusMessage = created ? $"已新建《{title.Trim()}》" : "新建被拒绝（Host 只读或 Core 未就绪）";
        if (created)
        {
            await RefreshAsync(cancellationToken).ConfigureAwait(true);
        }

        return created;
    }

    public IReadOnlyList<string> VisibleTitles()
    {
        var query = SearchText.Trim();
        var visible = new List<string>();
        foreach (var book in _all)
        {
            if (SelectedTag != "全部" && !string.Equals(book.Tag, SelectedTag, StringComparison.Ordinal))
            {
                continue;
            }

            if (query.Length > 0 &&
                book.Title.IndexOf(query, StringComparison.OrdinalIgnoreCase) < 0 &&
                book.OriginalTitle.IndexOf(query, StringComparison.OrdinalIgnoreCase) < 0)
            {
                continue;
            }

            visible.Add(book.Title);
        }

        return visible;
    }

    private void RebuildVisible()
    {
        var visible = VisibleTitles();
        Books.Clear();
        foreach (var book in _all)
        {
            if (visible.Contains(book.Title, StringComparer.Ordinal))
            {
                Books.Add(book);
            }
        }

        OnPropertyChanged(nameof(IsEmpty));
        OnPropertyChanged(nameof(HasNoResults));
        BooksChanged?.Invoke(this, EventArgs.Empty);
    }

    private bool Set<T>(ref T field, T value, [CallerMemberName] string? property = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value))
        {
            return false;
        }

        field = value;
        OnPropertyChanged(property);
        return true;
    }

    private void OnPropertyChanged(string? name) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}

/// <summary>AC4 settings skeleton: theme center + wired command ledger + NS batch.</summary>
public sealed class SettingsViewModel
{
    public IReadOnlyList<ThemePack> ThemePacks { get; } = NewManga.Theme.ThemePacks.All;

    public ThemePack SelectedPack { get; set; } = ThemePackService.Current;

    public string WiredSummary =>
        $"已接线命令 {Shell.ShellCommandCatalog.WiredCommandCount} 条 · S2 NOT_SUPPORTED 批登记 {Shell.ShellCommandCatalog.NsRegisteredCount} 条" +
        $"（完成 {Shell.ShellCommandCatalog.NsDoneCount}/{Shell.ShellCommandCatalog.NsRegisteredCount}）";

    public IReadOnlyList<Shell.ShellCommandCatalog.NsBatchItem> NsBatch => Shell.ShellCommandCatalog.NsBatch;

    public string SettingsJson { get; private set; } = "（尚未读取 settings.get）";

    public void UpdateSettingsJson(System.Text.Json.JsonElement value) => SettingsJson = value.GetRawText();


}
