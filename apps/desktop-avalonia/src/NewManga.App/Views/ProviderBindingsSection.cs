using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.App.Views.Legacy;

namespace NewManga.App.Views;

/// <summary>
/// SETTINGS-PROFILE-UI-1 AC3 + READER-SELECTOR-UI-1: provider-binding slot
/// (global/book/chapter + capability → provider profile) via
/// <c>settings_provider_bindings_set/clear/resolve</c>.
///
/// READER-SELECTOR-UI-1 replaces the hand-typed book/chapter ids with real readers:
///  - scope=book/chapter shows a book selector fed by <c>library_list_books</c> (book title);
///  - selecting a book loads its chapters via <c>list_chapters</c> (chapter title);
///  - switching the scope kind resets both selections;
///  - while the required selection is missing the bind action is disabled and a hint explains why;
///  - an empty library / chapterless book shows an explicit empty state instead of a broken form.
/// </summary>
public sealed class ProviderBindingsSection : UserControl
{
    private readonly Func<CancellationToken, Task<IReadOnlyList<ProviderProfileInfo>>> _listProviders;
    private readonly Func<CancellationToken, Task<IReadOnlyList<BookSummary>>> _listBooks;
    private readonly Func<string, CancellationToken, Task<IReadOnlyList<ChapterSummary>>> _listChapters;
    private readonly Func<ProfileBindingScope, string, string, CancellationToken, Task<SettingsProfileResult>> _set;
    private readonly Func<ProfileBindingScope, string, CancellationToken, Task<SettingsProfileResult>> _clear;
    private readonly Func<string, CancellationToken, Task<ProviderBindingResult?>> _resolve;
    private readonly ComboBox _scopeKind = new() { Name = "BindingScopeKind", MinWidth = 130 };
    private readonly ComboBox _bookSelector = new() { Name = "BindingBookSelector", MinWidth = 320 };
    private readonly ComboBox _chapterSelector = new() { Name = "BindingChapterSelector", MinWidth = 320 };
    private readonly TextBlock _selectorStatus;
    private readonly ComboBox _capability = new() { Name = "BindingCapability", MinWidth = 140 };
    private readonly ComboBox _profile = new() { Name = "BindingProfile", MinWidth = 240 };
    private readonly TextBlock _status;
    private readonly TextBlock _resolveResult;
    private readonly Button _setButton;
    private readonly Button _clearButton;
    private readonly Button _resolveButton;
    private readonly Button _refreshButton;
    private IReadOnlyList<ProviderProfileInfo> _providers = Array.Empty<ProviderProfileInfo>();
    private IReadOnlyList<BookSummary> _books = Array.Empty<BookSummary>();
    private IReadOnlyList<ChapterSummary> _chapters = Array.Empty<ChapterSummary>();

    public ProviderBindingsSection(
        Func<CancellationToken, Task<IReadOnlyList<ProviderProfileInfo>>> listProviders,
        Func<CancellationToken, Task<IReadOnlyList<BookSummary>>> listBooks,
        Func<string, CancellationToken, Task<IReadOnlyList<ChapterSummary>>> listChapters,
        Func<ProfileBindingScope, string, string, CancellationToken, Task<SettingsProfileResult>> set,
        Func<ProfileBindingScope, string, CancellationToken, Task<SettingsProfileResult>> clear,
        Func<string, CancellationToken, Task<ProviderBindingResult?>> resolve)
    {
        _listProviders = listProviders;
        _listBooks = listBooks;
        _listChapters = listChapters;
        _set = set;
        _clear = clear;
        _resolve = resolve;
        Name = "ProviderBindingsSection";

        _status = Ui.Text(string.Empty, 11, "TextSecondary");
        _status.Name = "BindingStatus";
        _selectorStatus = Ui.Text(string.Empty, 11, "TextSecondary");
        _selectorStatus.Name = "BindingSelectorStatus";
        _resolveResult = Ui.Text("解析结果：尚未执行 resolve。", 11, "TextSecondary");
        _resolveResult.Name = "BindingResolveResult";
        _scopeKind.ItemsSource = ProfileBindingScope.Kinds.ToList();
        _scopeKind.SelectedIndex = 0;
        _scopeKind.SelectionChanged += (_, _) => LastOperation = OnScopeChangedAsync();
        _bookSelector.SelectionChanged += (_, _) => LastOperation = OnBookChangedAsync();
        _capability.ItemsSource = SettingsCapabilities.All.ToList();
        _capability.SelectedIndex = 0;
        _setButton = ProfileUi.Action("绑定", () => LastOperation = SetAsync(), primary: true);
        _setButton.Name = "BindingSet";
        _clearButton = ProfileUi.Action("清除绑定", () => LastOperation = ClearAsync());
        _clearButton.Name = "BindingClear";
        _resolveButton = ProfileUi.Action("解析当前绑定", () => LastOperation = ResolveAsync());
        _resolveButton.Name = "BindingResolve";
        _refreshButton = ProfileUi.Action("刷新列表", () => LastOperation = RefreshAsync());
        _refreshButton.Name = "BindingRefresh";

        var body = new StackPanel { Spacing = 8 };
        body.Children.Add(Ui.Text("Provider 绑定（slot）", 13, "TextPrimary", bold: true));
        body.Children.Add(Ui.Text(
            "把某个 provider profile 绑定到 (scope, capability) 槽位；运行链会按槽位解析 provider。book/chapter 范围用真实书库选择器。",
            11,
            "TextSecondary"));
        body.Children.Add(ProfileUi.Label("Scope 类型（global / book / chapter）"));
        body.Children.Add(_scopeKind);
        body.Children.Add(ProfileUi.Label("书籍（book，来自 library_list_books）"));
        body.Children.Add(_bookSelector);
        body.Children.Add(ProfileUi.Label("章节（chapter，选书后来自 list_chapters）"));
        body.Children.Add(_chapterSelector);
        body.Children.Add(_selectorStatus);
        body.Children.Add(ProfileUi.Label("能力（capability）"));
        body.Children.Add(_capability);
        body.Children.Add(ProfileUi.Label("Provider profile"));
        body.Children.Add(_profile);
        body.Children.Add(ProfileUi.Row(_setButton, _clearButton, _resolveButton, _refreshButton));
        body.Children.Add(_status);
        body.Children.Add(_resolveResult);
        Content = body;
        _bookSelector.IsVisible = false;
        _chapterSelector.IsVisible = false;
        UpdateButtons();
    }

    public ComboBox ScopeKindInput => _scopeKind;

    public ComboBox BookSelector => _bookSelector;

    public ComboBox ChapterSelector => _chapterSelector;

    public TextBlock SelectorStatusText => _selectorStatus;

    public ComboBox CapabilityInput => _capability;

    public ComboBox ProfileInput => _profile;

    /// <summary>Alias used by the settings wiring/tests (provider picker).</summary>
    public ComboBox ProviderInput => _profile;

    public TextBlock StatusText => _status;

    public TextBlock ResolveResultText => _resolveResult;

    public Button SetButton => _setButton;

    public Button ClearButton => _clearButton;

    public Button ResolveButton => _resolveButton;

    public IReadOnlyList<ProviderProfileInfo> Providers => _providers;

    public IReadOnlyList<BookSummary> Books => _books;

    public IReadOnlyList<ChapterSummary> Chapters => _chapters;

    public Task LastOperation { get; private set; } = Task.CompletedTask;

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _providers = await _listProviders(cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            _providers = Array.Empty<ProviderProfileInfo>();
        }

        _profile.ItemsSource = _providers.Select(provider => provider.DisplayText).ToList();
        _profile.SelectedIndex = _providers.Count > 0 ? 0 : -1;

        var kind = CurrentKind();
        if (kind is ProfileBindingScope.Book or ProfileBindingScope.Chapter)
        {
            await LoadBooksAsync(cancellationToken);
        }

        UpdateButtons();
    }

    public ProfileBindingScope CurrentScope()
    {
        var kind = CurrentKind();
        return kind switch
        {
            ProfileBindingScope.Book => new ProfileBindingScope(ProfileBindingScope.Book, BookId: SelectedBookId()),
            ProfileBindingScope.Chapter => new ProfileBindingScope(
                ProfileBindingScope.Chapter,
                ChapterId: SelectedChapterId()),
            _ => new ProfileBindingScope(ProfileBindingScope.Global),
        };
    }

    private string CurrentKind() => _scopeKind.SelectedItem as string ?? ProfileBindingScope.Global;

    private string? SelectedBookId() =>
        _bookSelector.SelectedIndex >= 0 && _bookSelector.SelectedIndex < _books.Count
            ? _books[_bookSelector.SelectedIndex].BookId
            : null;

    private string? SelectedChapterId() =>
        _chapterSelector.SelectedIndex >= 0 && _chapterSelector.SelectedIndex < _chapters.Count
            ? _chapters[_chapterSelector.SelectedIndex].ChapterId
            : null;

    private async Task OnScopeChangedAsync()
    {
        ResetSelections();
        var kind = CurrentKind();
        _bookSelector.IsVisible = kind is ProfileBindingScope.Book or ProfileBindingScope.Chapter;
        _chapterSelector.IsVisible = kind == ProfileBindingScope.Chapter;
        if (kind == ProfileBindingScope.Global)
        {
            _selectorStatus.Text = string.Empty;
            UpdateButtons();
            return;
        }

        await LoadBooksAsync(CancellationToken.None);
        UpdateButtons();
    }

    private async Task OnBookChangedAsync()
    {
        if (CurrentKind() != ProfileBindingScope.Chapter)
        {
            UpdateButtons();
            return;
        }

        await LoadChaptersAsync(CancellationToken.None);
        UpdateButtons();
    }

    private async Task LoadBooksAsync(CancellationToken cancellationToken)
    {
        try
        {
            _books = await _listBooks(cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            _books = Array.Empty<BookSummary>();
        }

        _bookSelector.ItemsSource = _books
            .Select(book => string.IsNullOrWhiteSpace(book.Title) ? book.BookId : book.Title)
            .ToList();
        _bookSelector.SelectedIndex = -1;
        _chapterSelector.ItemsSource = null;
        _chapters = Array.Empty<ChapterSummary>();
        _selectorStatus.Text = _books.Count == 0
            ? "书库为空：请先在书架导入或创建书籍，然后再选择 book/chapter 范围。"
            : "请选择书籍；章节列表会在选书后自动加载。";
    }

    private async Task LoadChaptersAsync(CancellationToken cancellationToken)
    {
        var bookId = SelectedBookId();
        _chapters = Array.Empty<ChapterSummary>();
        _chapterSelector.ItemsSource = null;
        _chapterSelector.SelectedIndex = -1;
        if (bookId is null)
        {
            _selectorStatus.Text = _books.Count == 0
                ? "书库为空：请先在书架导入或创建书籍，然后再选择 book/chapter 范围。"
                : "请选择书籍；章节列表会在选书后自动加载。";
            return;
        }

        try
        {
            _chapters = await _listChapters(bookId, cancellationToken);
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or IOException or OperationCanceledException)
        {
            _chapters = Array.Empty<ChapterSummary>();
        }

        _chapterSelector.ItemsSource = _chapters
            .Select(chapter => string.IsNullOrWhiteSpace(chapter.Title) ? chapter.ChapterId : chapter.Title)
            .ToList();
        _chapterSelector.SelectedIndex = _chapters.Count > 0 ? 0 : -1;
        _selectorStatus.Text = _chapters.Count == 0
            ? "该书籍没有章节：请先在书架/阅读器中为它创建或导入章节。"
            : $"已加载 {_chapters.Count} 个章节；请选择要绑定的章节。";
    }

    private void ResetSelections()
    {
        _bookSelector.SelectedIndex = -1;
        _bookSelector.ItemsSource = null;
        _chapterSelector.SelectedIndex = -1;
        _chapterSelector.ItemsSource = null;
        _books = Array.Empty<BookSummary>();
        _chapters = Array.Empty<ChapterSummary>();
    }

    private void UpdateButtons()
    {
        var kind = CurrentKind();
        var hasProvider = SelectedProfileId() is not null;
        var selectionReady = kind switch
        {
            ProfileBindingScope.Book => SelectedBookId() is not null,
            ProfileBindingScope.Chapter => SelectedChapterId() is not null,
            _ => true,
        };
        _setButton.IsEnabled = hasProvider && selectionReady;
        if (kind != ProfileBindingScope.Global && !selectionReady && (_selectorStatus.Text ?? string.Empty).Length == 0)
        {
            _selectorStatus.Text = "请先选择书籍/章节后再提交绑定。";
        }
    }

    private string? SelectedProfileId() =>
        _profile.SelectedIndex >= 0 && _profile.SelectedIndex < _providers.Count
            ? _providers[_profile.SelectedIndex].ProfileId
            : null;

    private async Task SetAsync()
    {
        var profileId = SelectedProfileId();
        if (profileId is null)
        {
            SetStatus("参数无效（INVALID_ARGUMENTS）：请先选择 provider profile（Host 未就绪时列表为空）。", error: true);
            return;
        }

        var kind = CurrentKind();
        if (kind == ProfileBindingScope.Book && SelectedBookId() is null)
        {
            SetStatus("请先选择书籍：book 范围的绑定必须指定书籍。", error: true);
            _selectorStatus.Text = _books.Count == 0
                ? "书库为空：请先在书架导入或创建书籍。"
                : "请选择书籍后再提交绑定。";
            UpdateButtons();
            return;
        }

        if (kind == ProfileBindingScope.Chapter && SelectedChapterId() is null)
        {
            SetStatus("请先选择书籍与章节：chapter 范围的绑定必须指定章节。", error: true);
            _selectorStatus.Text = _chapters.Count == 0 && SelectedBookId() is not null
                ? "该书籍没有章节：请先在书架/阅读器中创建或导入章节。"
                : "请选择书籍与章节后再提交绑定。";
            UpdateButtons();
            return;
        }

        var scope = CurrentScope();
        var result = await _set(scope, _capability.SelectedItem as string ?? SettingsCapabilities.Ocr, profileId, CancellationToken.None);
        SetStatus(ProfileUi.Describe(result), error: !result.IsSuccess);
    }

    private async Task ClearAsync()
    {
        var scope = CurrentScope();
        if (scope.Kind == ProfileBindingScope.Book && scope.BookId is null)
        {
            SetStatus("请先选择书籍：清除 book 范围的绑定必须指定书籍。", error: true);
            return;
        }

        if (scope.Kind == ProfileBindingScope.Chapter && scope.ChapterId is null)
        {
            SetStatus("请先选择书籍与章节：清除 chapter 范围的绑定必须指定章节。", error: true);
            return;
        }

        var result = await _clear(scope, _capability.SelectedItem as string ?? SettingsCapabilities.Ocr, CancellationToken.None);
        SetStatus(ProfileUi.Describe(result), error: !result.IsSuccess);
    }

    private async Task ResolveAsync()
    {
        var info = await _resolve(_capability.SelectedItem as string ?? SettingsCapabilities.Ocr, CancellationToken.None);
        _resolveResult.Text = info is null
            ? "解析结果：不可用（Host/Core 未就绪或该 capability 无绑定）。"
            : $"解析结果：profile_id={info.ProfileId ?? "(none)"} · source={info.Source ?? "(none)"}";
    }

    private void SetStatus(string message, bool error = false)
    {
        _status.Text = message;
        _status.Foreground = LegacyChrome.Brush(error ? "TextPrimary" : "TextSecondary");
    }
}

