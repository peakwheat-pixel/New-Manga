using Avalonia;
using Avalonia.Controls;
using Avalonia.Automation;
using Avalonia.Controls.Primitives;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Platform.Storage;
using Avalonia.VisualTree;
using NewManga.App.Controls;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.CoreClient;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;

namespace NewManga.App.Views.Fluent;

/// <summary>Fluent Shelf page. Its state and data projections live in <see cref="ShelfViewModel"/>.</summary>
public sealed class ShelfPageView : UserControl
{
    /// <summary>I-2：详情栏展开时的默认/最小/最大宽度（设计 05 §1 详情栏 320；范围为实现约束）。</summary>
    public const double DetailPaneWidth = 320;
    public const double DetailPaneMinWidth = 240;
    public const double DetailPaneMaxWidth = 480;

    private readonly ShelfViewModel _viewModel;
    private readonly IFilePickerGateway? _filePicker;
    private readonly Action<BookSummary, ChapterSummary> _openReader;
    private readonly Action<BookSummary, ChapterSummary> _openWorkbench;
    private readonly Action? _openConsole;
    private readonly StackPanel _root;
    private readonly WrapPanel _gridHost;
    private readonly StackPanel _listHost;
    private readonly ScrollViewer _listScroll;
    private readonly ChapterList _chapterHost;
    private readonly StackPanel _pageThumbHost;
    private readonly Border _details;
    private readonly Border _stateHost;
    private readonly TextBlock _status;
    private readonly Button _detailToggle;
    private readonly Drawer _recycleDrawer;
    private readonly FluentDialog _dialog;
    private readonly Border _dialogScrim;
    private readonly FluentVisibilityMotion _scrimMotion;
    private readonly FluentVisibilityMotion[] _overlayMotions;
    private readonly TextBox _dialogInput;
    private readonly StackPanel _dialogBody;
    private readonly Button _dialogConfirm;
    private readonly SegmentedControl _viewModeControl;
    private IReadOnlyList<string> _pendingDropFiles = Array.Empty<string>();
    private string? _pendingDropFolder;
    private Button _importFilesButton = null!;
    private Button _importFolderButton = null!;
    private Button _newBookButton = null!;
    private Button _newChapterButton = null!;
    private string _dialogAction = "book";

    public ShelfPageView(
        ShelfViewModel viewModel,
        IFilePickerGateway? filePicker,
        Action<BookSummary, ChapterSummary> openReader,
        Action<BookSummary, ChapterSummary> openWorkbench,
        Action? openConsole = null)
    {
        _viewModel = viewModel;
        _filePicker = filePicker;
        _openReader = openReader;
        _openWorkbench = openWorkbench;
        _openConsole = openConsole;
        _gridHost = new WrapPanel { Orientation = Orientation.Horizontal };
        _listHost = new StackPanel { Orientation = Orientation.Vertical, Classes = { "fluent-chapter-list" } };
        _chapterHost = new ChapterList();
        _viewModeControl = new SegmentedControl
        {
            Items = ["网格", "列表"],
            SelectedIndex = viewModel.IsGrid ? 0 : 1,
        };
        AutomationProperties.SetName(_viewModeControl, "书架视图模式");
        _viewModeControl.SelectionChanged += (_, selectedIndex) => _viewModel.IsGrid = selectedIndex == 0;
        _pageThumbHost = new StackPanel { Orientation = Orientation.Horizontal, Classes = { "fluent-page-toolbar" } };
        _status = FluentUi.Text(string.Empty, "fluent-status-text");
        _stateHost = new Border { IsVisible = false };
        _details = new Border
        {
            Classes = { "fluent-detail-pane" },
            IsVisible = false,
            Width = DetailPaneWidth,
            MinWidth = DetailPaneMinWidth,
            MaxWidth = DetailPaneMaxWidth,
        };
        _listScroll = new ScrollViewer
        {
            HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
        };
        // I-1：列表滚动偏移属同一运行期 UI memento（不落盘），页面往返/重建后恢复。
        // 只把「用户滚动」（extent 不变、仅 offset 变化）记入 memento：Render 重建内容或布局
        // clamp 引起的 offset 变化（ExtentDelta≠0）不代表用户位置，不能回写覆盖 memento。
        _listScroll.ScrollChanged += (_, args) =>
        {
            if (_listScroll.IsArrangeValid && args.ExtentDelta.Y == 0)
            {
                _viewModel.ListScrollOffset = _listScroll.Offset.Y;
            }
        };
        _detailToggle = FluentUi.Button("折叠详情栏", "fluent-secondary", () => _viewModel.IsDetailPaneCollapsed = !_viewModel.IsDetailPaneCollapsed, "折叠或展开详情栏");
        _recycleDrawer = new Drawer { IsOpen = false, Header = "回收站", Classes = { "fluent-drawer" } };
        _recycleDrawer.Content = FluentUi.Stack("fluent-page-layout");
        ((StackPanel)_recycleDrawer.Content).Children.Add(FluentUi.Text(
            "回收站入口已保留。当前 IHostController 未发布回收站读写端口，因此这里不显示虚构记录，也不会执行删除。"));

        _dialogInput = FluentUi.Input("名称", "输入作品或章节名称");
        _dialog = new FluentDialog { IsOpen = false };
        _dialogScrim = new Border { Classes = { "fluent-modal-scrim" }, IsVisible = false };
        _scrimMotion = new FluentVisibilityMotion(_dialogScrim);
        _overlayMotions = [new(_dialog, FluentDialog.IsOpenProperty), new(_recycleDrawer, Drawer.IsOpenProperty)];
        _dialogBody = FluentUi.Stack("fluent-page-layout");
        _dialogConfirm = FluentUi.Button("确认", "fluent-primary", () => _ = SubmitNameAsync(), "确认操作");

        _root = FluentUi.Stack("fluent-page-layout");
        _root.Children.Add(BuildToolbar());
        _root.Children.Add(_stateHost);
        _root.Children.Add(BuildBody());
        _root.Children.Add(_status);
        Content = BuildOverlays(_root);

        _viewModel.PropertyChanged += (_, _) => Render();
        DragDrop.SetAllowDrop(_root, true);
        _root.AddHandler(DragDrop.DragOverEvent, OnDragOver);
        _root.AddHandler(DragDrop.DropEvent, OnDrop);
        Render();
        _ = _viewModel.RefreshAsync();
    }

    public ShelfViewModel ViewModel => _viewModel;
    public SegmentedControl ViewModeControl => _viewModeControl;
    public ChapterList ChapterDetails => _chapterHost;
    public Border DetailPane => _details;
    public Button DetailPaneToggle => _detailToggle;
    public ScrollViewer ListScroll => _listScroll;

    public void ShowNewBookDialog() => ShowNameDialog("book");

    public void ShowNewChapterDialog() => ShowNameDialog("chapter");

    public void OpenRecycleDrawer() => _recycleDrawer.IsOpen = true;

    internal void ConfigureMotion(MotionTimingProfile timings, IFluentMotionClock clock)
    {
        _scrimMotion.Configure(timings.NavigationOverlayInMilliseconds > 0 ? timings.NavigationOverlayOutMilliseconds : 0,
            timings.NavigationOverlayOutMilliseconds, clock);
        foreach (var motion in _overlayMotions)
            motion.Configure(timings.NavigationOverlayInMilliseconds, timings.NavigationOverlayOutMilliseconds, clock);
    }

    public Task ImportFilesAsync() => PickAndImportFilesAsync();

    public Task ImportFolderAsync() => PickAndImportFolderAsync();

    public void OpenSelectedReader() => OpenReader();

    public void OpenSelectedWorkbench() => OpenWorkbench();

    public Control? BookButton(string bookId) =>
        (Control?)_gridHost.Children.OfType<BookCard>().FirstOrDefault(button => button.Tag is BookSummary item && item.BookId == bookId)
        ?? _listHost.Children.OfType<BookRow>().FirstOrDefault(button => button.Tag is BookSummary item && item.BookId == bookId);

    private Control BuildToolbar()
    {
        var toolbar = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        toolbar.Children.Add(FluentUi.Text("书架", "fluent-page-title"));
        var search = FluentUi.Search("搜索书架", "搜索作品");
        search.PropertyChanged += (_, args) =>
        {
            if (args.Property == SearchField.TextProperty) _viewModel.Search = search.Text ?? string.Empty;
        };
        toolbar.Children.Add(search);
        toolbar.Children.Add(_viewModeControl);
        toolbar.Children.Add(FluentUi.Button("收藏", "fluent-secondary", () => _viewModel.FavoritesOnly = !_viewModel.FavoritesOnly, "筛选收藏作品"));
        toolbar.Children.Add(FluentUi.Button("已归档", "fluent-secondary", () => _viewModel.ArchivedOnly = !_viewModel.ArchivedOnly, "筛选已归档作品"));
        toolbar.Children.Add(FluentUi.Button("新建作品", "fluent-primary", () => ShowNameDialog("book"), "新建作品"));
        _newBookButton = (Button)toolbar.Children[^1];
        _newChapterButton = FluentUi.Button("新建章节", "fluent-secondary", () => ShowNameDialog("chapter"), "新建章节");
        toolbar.Children.Add(_newChapterButton);
        _importFilesButton = FluentUi.IconButton(NmIconKind.Import, "导入文件", () => _ = PickAndImportFilesAsync(), "fluent-primary");
        toolbar.Children.Add(_importFilesButton);
        _importFolderButton = FluentUi.Button("导入文件夹", "fluent-secondary", () => _ = PickAndImportFolderAsync(), "导入文件夹");
        toolbar.Children.Add(_importFolderButton);
        toolbar.Children.Add(FluentUi.Button("回收站", "fluent-secondary", () => _recycleDrawer.IsOpen = true, "打开回收站"));
        toolbar.Children.Add(FluentUi.Button("刷新", "fluent-icon", () => _ = _viewModel.RefreshAsync(), "刷新书架"));
        // I-2：详情栏折叠/展开入口（Enter/Space 激活；折叠后按钮仍在工具栏保持可达）。
        toolbar.Children.Add(_detailToggle);
        return toolbar;
    }

    private Control BuildBody()
    {
        var body = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        _listScroll.Content = _gridHost;
        _listHost.IsVisible = false;
        var lists = FluentUi.Stack("fluent-page-layout");
        lists.Children.Add(_listScroll);
        lists.Children.Add(_listHost);
        body.Children.Add(lists);

        var detailStack = FluentUi.Stack("fluent-page-layout");
        detailStack.Children.Add(FluentUi.Text("作品详情", "fluent-page-title"));
        detailStack.Children.Add(FluentUi.Text("章节", "fluent-status-text"));
        detailStack.Children.Add(_chapterHost);
        detailStack.Children.Add(FluentUi.Text("页面", "fluent-status-text"));
        detailStack.Children.Add(_pageThumbHost);
        detailStack.Children.Add(FluentUi.Button("打开工作台", "fluent-primary", OpenWorkbench, "在工作台中打开所选章节"));
        detailStack.Children.Add(FluentUi.Button("开始阅读", "fluent-secondary", OpenReader, "阅读所选章节"));
        _details.Child = detailStack;
        Grid.SetColumn(_details, 1);
        body.Children.Add(_details);
        return body;
    }

    private Control BuildOverlays(Control content)
    {
        var overlay = new Grid();
        overlay.Children.Add(content);

        _dialogScrim.PointerPressed += (_, _) => CloseDialog();
        _dialogBody.Children.Add(FluentUi.Text("名称", "fluent-page-title"));
        _dialogBody.Children.Add(_dialogInput);
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("取消", "fluent-secondary", CloseDialog, "取消"));
        actions.Children.Add(_dialogConfirm);
        _dialogBody.Children.Add(actions);
        _dialog.Child = _dialogBody;
        var dialogLayer = new Grid { RowDefinitions = new RowDefinitions("*,Auto,*") };
        dialogLayer.Children.Add(_dialogScrim);
        Grid.SetRowSpan(_dialogScrim, 3);
        dialogLayer.Children.Add(_dialog);
        Grid.SetRow(_dialog, 1);
        overlay.Children.Add(dialogLayer);

        var drawerLayer = new Grid { IsHitTestVisible = true };
        drawerLayer.Children.Add(_recycleDrawer);
        Grid.SetColumn(_recycleDrawer, 1);
        overlay.Children.Add(drawerLayer);
        return overlay;
    }

    private void Render()
    {
        _gridHost.Children.Clear();
        _listHost.Children.Clear();
        _chapterHost.Children.Clear();
        _pageThumbHost.Children.Clear();

        if (_viewModel.State == FluentPageState.Loading && _viewModel.Books.Count == 0)
        {
            var loading = FluentUi.Stack("fluent-page-layout");
            loading.Children.Add(FluentUi.Text("正在读取书架…", "fluent-page-title"));
            foreach (var _ in Enumerable.Range(0, 6)) loading.Children.Add(FluentUi.LoadingCard());
            _stateHost.Child = FluentUi.Card(loading);
            _stateHost.IsVisible = true;
        }
        else if (_viewModel.State == FluentPageState.Error)
        {
            // I-12：错误卡保留「重试」并补「打开控制台」入口（设计 05 §3 错误行）；无 shell 回调时入口不渲染。
            var errorCard = FluentUi.Stack("fluent-page-layout");
            errorCard.Children.Add(FluentUi.Banner(StatusKind.Failed, "书架读取失败", _viewModel.Error,
                "重试", () => _ = _viewModel.RefreshAsync()));
            if (_openConsole is not null)
            {
                errorCard.Children.Add(FluentUi.Button("打开控制台", "fluent-secondary", _openConsole, "打开控制台"));
            }

            _stateHost.Child = FluentUi.Card(errorCard);
            _stateHost.IsVisible = true;
        }
        else if (_viewModel.State == FluentPageState.ReadOnly)
        {
            _stateHost.Child = FluentUi.Banner(StatusKind.Locked, "当前为只读模式",
                _viewModel.ViewStatus, null, null);
            _stateHost.IsVisible = true;
        }
        else if (_viewModel.State == FluentPageState.Running)
        {
            var running = FluentUi.Stack("fluent-page-layout");
            running.Children.Add(FluentUi.Text("正在扫描或导入…", "fluent-status-text"));
            running.Children.Add(new ProgressBar { IsIndeterminate = true, Classes = { "fluent-progress" } });
            _stateHost.Child = FluentUi.Card(running);
            _stateHost.IsVisible = true;
        }
        else if (_viewModel.Books.Count == 0)
        {
            _stateHost.Child = FluentUi.Card(FluentUi.Empty(
                "还没有作品",
                "创建作品和章节后，可以通过 Host 导入文件或文件夹。",
                "新建作品",
                () => ShowNameDialog("book")));
            _stateHost.IsVisible = true;
        }
        else if (!_viewModel.FilteredBooks.Any())
        {
            _stateHost.Child = FluentUi.Card(FluentUi.Empty(
                "没有匹配的作品",
                "当前筛选条件已保留。",
                "清除筛选",
                _viewModel.ClearFilters));
            _stateHost.IsVisible = true;
        }
        else
        {
            _stateHost.Child = null;
            _stateHost.IsVisible = false;
        }

        foreach (var book in _viewModel.FilteredBooks)
        {
            _gridHost.Children.Add(BuildBookCard(book));
            _listHost.Children.Add(BuildBookRow(book));
        }

        _gridHost.IsVisible = _viewModel.IsGrid;
        _listHost.IsVisible = !_viewModel.IsGrid;
        _viewModeControl.SelectedIndex = _viewModel.IsGrid ? 0 : 1;
        // I-2：详情栏在「已选作品且未折叠」时可见；折叠后 Auto 列宽为 0，列表占满主区。
        _details.IsVisible = !_viewModel.IsDetailPaneCollapsed && _viewModel.SelectedBook is not null;
        _detailToggle.Content = _viewModel.IsDetailPaneCollapsed ? "展开详情栏" : "折叠详情栏";
        AutomationProperties.SetName(_detailToggle, _detailToggle.Content?.ToString() ?? "折叠或展开详情栏");
        if (_viewModel.SelectedBook is not null)
        {
            _chapterHost.Children.Add(FluentUi.Text(_viewModel.SelectedBook.Title, "fluent-status-text"));
            foreach (var chapter in _viewModel.Chapters)
            {
                var button = FluentUi.Button(chapter.Title, "fluent-book-row",
                    () => _ = _viewModel.SelectChapterAsync(chapter), chapter.Title);
                button.Classes.Set("selected", _viewModel.SelectedChapter?.ChapterId == chapter.ChapterId);
                _chapterHost.Children.Add(button);
            }

            foreach (var page in _viewModel.PreviewPages)
            {
                var thumb = new StreamingThumb { Child = FluentUi.Text($"第 {page.SortOrder + 1} 页", "fluent-subtle-text") };
                Avalonia.Automation.AutomationProperties.SetName(thumb, $"第 {page.SortOrder + 1} 页");
                _pageThumbHost.Children.Add(thumb);
            }
        }

        _newBookButton.IsEnabled = !_viewModel.IsReadOnly;
        _newChapterButton.IsEnabled = !_viewModel.IsReadOnly && _viewModel.SelectedBook is not null;
        _importFilesButton.IsEnabled = !_viewModel.IsReadOnly && _viewModel.SelectedChapter is not null;
        _importFolderButton.IsEnabled = !_viewModel.IsReadOnly && _viewModel.SelectedChapter is not null;

        _status.Text = _viewModel.IsReadOnly
            ? $"只读 · {_viewModel.ViewStatus}"
            : _viewModel.ViewStatus;
        _status.Classes.Set("failed", _viewModel.State == FluentPageState.Error);

        // I-1：Render 重建列表内容会重置滚动，这里从 UI memento 恢复列表滚动偏移。
        if (_listScroll.Offset.Y != _viewModel.ListScrollOffset)
        {
            _listScroll.Offset = new Vector(0, _viewModel.ListScrollOffset);
        }
    }

    private BookCard BuildBookCard(BookSummary book)
    {
        var card = new BookCard
        {
            Tag = book,
            Content = BookSummaryView(book),
            Classes = { "selected" },
        };
        card.Classes.Set("selected", _viewModel.SelectedBook?.BookId == book.BookId);
        card.Click += async (_, _) => await _viewModel.SelectBookAsync(book);
        card.ContextMenu = BuildContextMenu(book);
        AutomationProperties.SetName(card, $"{book.Title} · {book.PageCount ?? 0} 页");
        card.PointerPressed += (_, args) =>
        {
            if (args.KeyModifiers.HasFlag(KeyModifiers.Control))
            {
                _viewModel.ToggleSelection(book);
                card.Classes.Set("selected", _viewModel.SelectedBooks.Any(item => item.BookId == book.BookId));
            }
        };
        return card;
    }

    private BookRow BuildBookRow(BookSummary book)
    {
        var row = new BookRow { Tag = book, Content = BookSummaryView(book) };
        row.Classes.Set("selected", _viewModel.SelectedBook?.BookId == book.BookId);
        row.Click += async (_, _) => await _viewModel.SelectBookAsync(book);
        row.ContextMenu = BuildContextMenu(book);
        AutomationProperties.SetName(row, $"{book.Title} · {book.PageCount ?? 0} 页");
        return row;
    }

    private static Control BookSummaryView(BookSummary book)
    {
        var stack = FluentUi.Stack("fluent-page-layout");
        stack.Children.Add(new NmIcon { Kind = NmIconKind.Library, Classes = { "large" } });
        stack.Children.Add(FluentUi.Text(book.Title, "fluent-page-title"));
        stack.Children.Add(FluentUi.Text($"{book.PageCount ?? 0} 页{(book.IsFavorite ? " · 收藏" : string.Empty)}{(book.IsArchived ? " · 已归档" : string.Empty)}",
            "fluent-subtle-text"));
        return stack;
    }

    private ContextMenu BuildContextMenu(BookSummary book)
    {
        var delete = new MenuItem { Header = "移入回收站", IsEnabled = false };
        ToolTip.SetTip(delete, "当前 IHostController 未发布回收站写端口。");
        var open = new MenuItem { Header = "打开作品" };
        open.Click += async (_, _) => await _viewModel.SelectBookAsync(book);
        var import = new MenuItem { Header = "导入到所选章节", IsEnabled = !_viewModel.IsReadOnly && _viewModel.SelectedChapter is not null };
        import.Click += async (_, _) =>
        {
            await _viewModel.SelectBookAsync(book);
            if (_viewModel.SelectedChapter is not null) await PickAndImportFilesAsync();
        };
        var multi = new MenuItem { Header = "切换多选" };
        multi.Click += (_, _) => _viewModel.ToggleSelection(book);
        return new ContextMenu { Items = { open, import, multi, delete } };
    }

    private void ShowNameDialog(string action)
    {
        _dialogAction = action;
        _pendingDropFiles = Array.Empty<string>();
        _pendingDropFolder = null;
        _dialogConfirm.Content = "确认创建";
        AutomationProperties.SetName(_dialogConfirm, "确认创建");
        _dialogInput.IsVisible = true;
        _dialogBody.Children.Clear();
        _dialogBody.Children.Add(FluentUi.Text(action == "book" ? "新建作品" : "新建章节", "fluent-page-title"));
        _dialogBody.Children.Add(_dialogInput);
        AddDialogActions("取消");
        _dialogInput.Text = string.Empty;
        _dialog.IsOpen = true;
        _scrimMotion.SetVisible(true);
        _dialogInput.Focus();
    }

    private void CloseDialog()
    {
        _dialog.IsOpen = false;
        _scrimMotion.SetVisible(false);
    }

    private async Task SubmitNameAsync()
    {
        var title = _dialogInput.Text ?? string.Empty;
        CloseDialog();
        if (_dialogAction == "book") await _viewModel.CreateBookAsync(title);
        else if (_dialogAction == "chapter") await _viewModel.CreateChapterAsync(title);
        else if (_dialogAction == "drop-files" && _pendingDropFiles.Count > 0) await _viewModel.ImportFilesAsync(_pendingDropFiles);
        else if (_dialogAction == "drop-folder" && !string.IsNullOrWhiteSpace(_pendingDropFolder)) await _viewModel.ImportFolderAsync(_pendingDropFolder);
        _pendingDropFiles = Array.Empty<string>();
        _pendingDropFolder = null;
    }

    private async Task PickAndImportFilesAsync()
    {
        if (_filePicker is null) return;
        var paths = await _filePicker.PickFilesAsync();
        if (paths.Count > 0) await _viewModel.ImportFilesAsync(paths);
    }

    private async Task PickAndImportFolderAsync()
    {
        if (_filePicker is null) return;
        var folder = await _filePicker.PickFolderAsync();
        if (!string.IsNullOrWhiteSpace(folder)) await _viewModel.ImportFolderAsync(folder);
    }

    private void OnDragOver(object? sender, DragEventArgs args)
    {
        var canDrop = args.DataTransfer.Contains(DataFormat.File) && !_viewModel.IsReadOnly;
        args.DragEffects = canDrop ? DragDropEffects.Copy : DragDropEffects.None;
        args.Handled = true;
    }

    private void OnDrop(object? sender, DragEventArgs args)
    {
        args.Handled = true;
        if (_viewModel.IsReadOnly || args.DataTransfer.TryGetFiles() is not { } items) return;
        var paths = new List<string>();
        string? folder = null;
        foreach (IStorageItem item in items)
        {
            if (item.Path is not { IsFile: true } uri) continue;
            if (item is IStorageFolder) folder = uri.LocalPath;
            else paths.Add(uri.LocalPath);
        }

        if (_viewModel.SelectedChapter is null)
        {
            _status.Text = "请先选择目标章节，再拖入文件或文件夹。";
            return;
        }
        if (paths.Count == 0 && folder is null) return;
        _pendingDropFiles = paths;
        _pendingDropFolder = folder;
        _dialogAction = paths.Count > 0 ? "drop-files" : "drop-folder";
        _dialogInput.IsVisible = false;
        _dialogConfirm.Content = paths.Count > 0 ? "确认导入" : "确认扫描并导入";
        AutomationProperties.SetName(_dialogConfirm, _dialogConfirm.Content?.ToString() ?? "确认导入");
        _dialogBody.Children.Clear();
        _dialogBody.Children.Add(FluentUi.Text("导入确认", "fluent-page-title"));
        _dialogBody.Children.Add(FluentUi.Text(
            paths.Count > 0
                ? $"将把 {paths.Count} 个文件导入到「{_viewModel.SelectedChapter.Title}」。"
                : $"将扫描文件夹并导入到「{_viewModel.SelectedChapter.Title}」。",
            "fluent-status-text"));
        AddDialogActions("取消导入");
        _dialog.IsOpen = true;
        _scrimMotion.SetVisible(true);
    }

    private void AddDialogActions(string cancelName)
    {
        // The cached confirm button still belongs to the previous (now detached) actions panel.
        if (_dialogConfirm.Parent is Panel previous) previous.Children.Remove(_dialogConfirm);
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("取消", "fluent-secondary", CloseDialog, cancelName));
        actions.Children.Add(_dialogConfirm);
        _dialogBody.Children.Add(actions);
    }

    private void OpenWorkbench()
    {
        if (_viewModel.SelectedBook is { } book && _viewModel.SelectedChapter is { } chapter)
        {
            _openWorkbench(book, chapter);
        }
    }

    private void OpenReader()
    {
        if (_viewModel.SelectedBook is { } book && _viewModel.SelectedChapter is { } chapter)
        {
            _openReader(book, chapter);
        }
    }
}
