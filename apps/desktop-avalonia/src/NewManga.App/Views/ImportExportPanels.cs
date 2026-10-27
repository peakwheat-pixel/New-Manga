using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.Theme;

namespace NewManga.App.Views;

/// <summary>
/// IMPORT-EXPORT-UI-1 AC1: the modal import flow (files/folder → destination book/chapter → grant-chain
/// import → progress/result → shelf refresh). The panel never fabricates a result: it renders the Host's
/// typed outcome, and only reaches "已导入" when the Host reported imported files.
/// </summary>
public sealed class ImportPanel : Border
{
    private readonly IHostController _controller;
    private readonly ComboBox _bookSelector = new() { Name = "ImportBookSelector", MinWidth = 260, FontSize = 12 };
    private readonly ComboBox _chapterSelector = new() { Name = "ImportChapterSelector", MinWidth = 260, FontSize = 12 };
    private readonly ComboBox _policySelector = new() { Name = "ImportPolicySelector", MinWidth = 160, FontSize = 12 };
    private readonly TextBlock _status;
    private readonly TextBlock _selection;
    private readonly ProgressBar _progress;
    private readonly Button _start;
    private readonly Button _close;
    private readonly TextBlock _title;
    private ImportSourceKind _kind = ImportSourceKind.Files;
    private IReadOnlyList<string> _paths = Array.Empty<string>();
    private IReadOnlyList<ChapterSummary> _chapters = Array.Empty<ChapterSummary>();
    private bool _busy;

    public ImportPanel(IHostController controller)
    {
        _controller = controller;
        Name = "ImportPanel";
        HorizontalAlignment = HorizontalAlignment.Center;
        VerticalAlignment = VerticalAlignment.Center;
        Width = 620;
        Padding = new Thickness(22);
        CornerRadius = new CornerRadius(14);
        Background = ThemePackService.Brush("CardBg");
        BorderBrush = ThemePackService.Brush("CardBorder");
        BorderThickness = new Thickness(1);
        IsVisible = false;

        _status = Ui.Text("选择目标书/章后开始导入", 12, "TextSecondary");
        _status.Name = "ImportStatus";
        _selection = Ui.Text(string.Empty, 11, "TextSecondary");
        _selection.Name = "ImportSelection";
        _selection.TextWrapping = TextWrapping.Wrap;
        _progress = new ProgressBar
        {
            Name = "ImportProgress",
            IsIndeterminate = true,
            IsVisible = false,
            Height = 5,
            CornerRadius = new CornerRadius(3),
        };
        _title = Ui.Text("导入到书库", 17, "TextPrimary", bold: true);
        _start = Ui.Action("开始导入", () => LastOperation = StartAsync(), primary: true);
        _start.Name = "ImportStartButton";
        _close = Ui.Action("关闭", Close);
        _close.Name = "ImportCloseButton";

        var bookRow = new Grid { ColumnDefinitions = new ColumnDefinitions("90,*"), Margin = new Thickness(0, 6, 0, 0) };
        bookRow.Children.Add(Ui.Text("目标书", 12, "TextSecondary"));
        Grid.SetColumn(_bookSelector, 1);
        bookRow.Children.Add(_bookSelector);
        var chapterRow = new Grid { ColumnDefinitions = new ColumnDefinitions("90,*"), Margin = new Thickness(0, 6, 0, 0) };
        chapterRow.Children.Add(Ui.Text("目标章", 12, "TextSecondary"));
        Grid.SetColumn(_chapterSelector, 1);
        chapterRow.Children.Add(_chapterSelector);
        var policyRow = new Grid { ColumnDefinitions = new ColumnDefinitions("90,*"), Margin = new Thickness(0, 6, 0, 0) };
        policyRow.Children.Add(Ui.Text("重复文件", 12, "TextSecondary"));
        Grid.SetColumn(_policySelector, 1);
        policyRow.Children.Add(_policySelector);

        var buttons = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, Margin = new Thickness(0, 10, 0, 0) };
        buttons.Children.Add(_start);
        buttons.Children.Add(_close);

        var body = new StackPanel { Spacing = 2 };
        body.Children.Add(_title);
        body.Children.Add(Ui.Text("通过系统文件选择器选择源文件；导入由 Host 签发 grant 后交给 Core。", 11, "TextSecondary"));
        body.Children.Add(bookRow);
        body.Children.Add(chapterRow);
        body.Children.Add(policyRow);
        body.Children.Add(new Border { Height = 6 });
        body.Children.Add(_selection);
        body.Children.Add(_status);
        body.Children.Add(new Border { Height = 4 });
        body.Children.Add(_progress);
        body.Children.Add(buttons);
        Child = body;

        _policySelector.ItemsSource = new[] { new PolicyChoice("skip", "跳过重复"), new PolicyChoice("import_as_new", "全部导入为新页") };
        _policySelector.SelectedIndex = 0;
        _bookSelector.SelectionChanged += (_, _) => LastOperation = LoadChaptersAsync();
    }

    public ComboBox BookSelector => _bookSelector;

    public ComboBox ChapterSelector => _chapterSelector;

    public ComboBox PolicySelector => _policySelector;

    public Button StartButton => _start;

    public Button CloseButton => _close;

    public ProgressBar ProgressBar => _progress;

    public TextBlock StatusText => _status;

    public ImportSourceKind Kind => _kind;

    public IReadOnlyList<string> SelectedPaths => _paths;

    /// <summary>Last asynchronous flow (tests await this instead of sleeping).</summary>
    public Task LastOperation { get; private set; } = Task.CompletedTask;

    /// <summary>Raised only after a Host-imported (non-zero or genuinely empty-success) outcome.</summary>
    public event EventHandler<ImportOutcome>? ImportCompleted;

    /// <summary>AC1: open with the paths the picker already returned (files or a folder).</summary>
    public async Task OpenAsync(ImportSourceKind kind, IReadOnlyList<string> paths)
    {
        _kind = kind;
        _paths = paths;
        _title.Text = kind == ImportSourceKind.Folder ? "导入文件夹到书库" : "导入文件到书库";
        _selection.Text = paths.Count == 0
            ? "未选择任何内容"
            : kind == ImportSourceKind.Folder
                ? $"源文件夹：{paths[0]}"
                : $"已选择 {paths.Count} 个文件：{string.Join("、", paths.Take(3).Select(Path.GetFileName))}"
                  + (paths.Count > 3 ? " …" : string.Empty);
        _status.Text = "正在读取书库…";
        IsVisible = true;
        await LoadBooksAsync();
        if (_bookSelector.SelectedItem is null)
        {
            _status.Text = "书架为空：先新建一本书，或检查 Host 是否就绪";
            _start.IsEnabled = false;
        }
        else
        {
            await LoadChaptersAsync();
            _start.IsEnabled = paths.Count > 0;
            _status.Text = paths.Count == 0
                ? "未选择文件：请关闭后重新选择"
                : "已选择源内容：确认目标书/章后点击「开始导入」";
        }
    }

    public void Close()
    {
        IsVisible = false;
        _busy = false;
        _progress.IsVisible = false;
        _start.IsEnabled = true;
    }

    private async Task LoadBooksAsync()
    {
        var books = _controller.Snapshot.Books;
        _bookSelector.ItemsSource = books.Select(book => new BookChoice(book)).ToList();
        _bookSelector.SelectedIndex = books.Count > 0 ? 0 : -1;
        if (books.Count == 0)
        {
            _chapterSelector.ItemsSource = null;
        }
    }

    private async Task LoadChaptersAsync()
    {
        if (_bookSelector.SelectedItem is not BookChoice book)
        {
            return;
        }

        _chapterSelector.ItemsSource = null;
        _status.Text = "正在读取章节…";
        _chapters = await _controller.ListChaptersAsync(book.Book.BookId);
        _chapterSelector.ItemsSource = _chapters.Select(chapter => new ChapterChoice(chapter)).ToList();
        _chapterSelector.SelectedIndex = _chapters.Count > 0 ? 0 : -1;
        _status.Text = _chapters.Count == 0
            ? "该书没有章节：请先在书里创建章节"
            : "选择目标章节后点击「开始导入」";
    }

    public async Task StartAsync()
    {
        if (_busy)
        {
            return;
        }

        if (_bookSelector.SelectedItem is not BookChoice)
        {
            _status.Text = "请选择目标书";
            return;
        }

        if (_chapterSelector.SelectedItem is not ChapterChoice chapter)
        {
            _status.Text = "请选择目标章节";
            return;
        }

        if (_paths.Count == 0)
        {
            _status.Text = "没有选择文件：请关闭后重新选择";
            return;
        }

        var policy = (_policySelector.SelectedItem as PolicyChoice)?.WireValue ?? "skip";
        _busy = true;
        _start.IsEnabled = false;
        _progress.IsVisible = true;
        _progress.IsIndeterminate = true;
        _status.Text = _kind == ImportSourceKind.Folder ? "正在导入文件夹…" : "正在导入文件…";
        try
        {
            var outcome = _kind == ImportSourceKind.Folder
                ? await _controller.ImportFolderAsync(chapter.Chapter.ChapterId, _paths[0], policy)
                : await _controller.ImportFilesAsync(chapter.Chapter.ChapterId, _paths, policy);
            _progress.IsVisible = false;
            _status.Text = ImportExportFormatting.ImportStatus(outcome);
            if (outcome.Ok)
            {
                ImportCompleted?.Invoke(this, outcome);
            }
        }
        finally
        {
            _busy = false;
            _start.IsEnabled = true;
        }
    }

    private sealed record BookChoice(BookSummary Book)
    {
        public override string ToString() => Book.Title;
    }

    private sealed record ChapterChoice(ChapterSummary Chapter)
    {
        public override string ToString() =>
            string.IsNullOrWhiteSpace(Chapter.Title) ? $"第 {Chapter.SortOrder + 1} 章" : Chapter.Title;
    }

    private sealed record PolicyChoice(string WireValue, string Label)
    {
        public override string ToString() => Label;
    }
}

/// <summary>
/// IMPORT-EXPORT-UI-1 AC2: reader export flow. Start → Host grant chain StartExport, then the panel
/// polls GetExportSnapshot (the only progress source), lists GetExportHistory, offers CancelExport
/// while the job is active, and RevealExportFolder only after a completed record exists.
/// Every rendered state comes from the controller; nothing is fabricated.
/// </summary>
public sealed class ExportPanel : Border
{
    private readonly IHostController _controller;
    private readonly TextBlock _context;
    private readonly TextBlock _status;
    private readonly ProgressBar _progress;
    private readonly Button _start;
    private readonly Button _cancel;
    private readonly Button _reveal;
    private readonly Button _close;
    private readonly ItemsControl _history;
    private string? _bookId;
    private string? _chapterId;
    private string _bookTitle = string.Empty;
    private string _chapterTitle = string.Empty;
    private IReadOnlyList<string> _translated = Array.Empty<string>();
    private string? _exportId;
    private ExportSnapshotInfo? _last;
    private DispatcherTimer? _timer;
    private bool _busy;
    private int _pollCount;

    public ExportPanel(IHostController controller)
    {
        _controller = controller;
        Name = "ExportPanel";
        HorizontalAlignment = HorizontalAlignment.Center;
        VerticalAlignment = VerticalAlignment.Center;
        Width = 700;
        Padding = new Thickness(22);
        CornerRadius = new CornerRadius(14);
        Background = ThemePackService.Brush("CardBg");
        BorderBrush = ThemePackService.Brush("CardBorder");
        BorderThickness = new Thickness(1);
        IsVisible = false;

        _context = Ui.Text(string.Empty, 12, "TextPrimary", bold: true);
        _context.Name = "ExportContext";
        _status = Ui.Text("准备就绪", 12, "TextSecondary");
        _status.Name = "ExportStatus";
        _status.TextWrapping = TextWrapping.Wrap;
        _progress = new ProgressBar
        {
            Name = "ExportProgress",
            Minimum = 0,
            Maximum = 100,
            Height = 6,
            CornerRadius = new CornerRadius(3),
            IsVisible = false,
        };
        _start = Ui.Action("开始导出", () => LastOperation = StartAsync(), primary: true);
        _start.Name = "ExportStartButton";
        _cancel = Ui.Action("取消导出", () => LastOperation = CancelAsync());
        _cancel.Name = "ExportCancelButton";
        _cancel.IsEnabled = false;
        _reveal = Ui.Action("打开导出目录", () => LastOperation = RevealAsync());
        _reveal.Name = "ExportRevealButton";
        _reveal.IsEnabled = false;
        _close = Ui.Action("关闭", Close);
        _close.Name = "ExportCloseButton";
        _history = new ItemsControl { Name = "ExportHistory", MaxHeight = 120 };
        _history.ItemTemplate = new Avalonia.Controls.Templates.FuncDataTemplate<string>((line, _) =>
            Ui.Text(line, 11, "TextSecondary"));

        var buttons = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, Margin = new Thickness(0, 10, 0, 0) };
        buttons.Children.Add(_start);
        buttons.Children.Add(_cancel);
        buttons.Children.Add(_reveal);
        buttons.Children.Add(_close);

        var body = new StackPanel { Spacing = 6 };
        body.Children.Add(Ui.Text("导出当前书（ZIP 图片包）", 17, "TextPrimary", bold: true));
        body.Children.Add(_context);
        body.Children.Add(Ui.Text("导出由 Host 签发目标 grant，产物写入 Host 数据根 exports/；下方进度来自 GetExportSnapshot。", 11, "TextSecondary"));
        body.Children.Add(_status);
        body.Children.Add(_progress);
        body.Children.Add(new Border { Height = 4 });
        body.Children.Add(Ui.Text("最近导出", 12, "TextPrimary", bold: true));
        body.Children.Add(_history);
        body.Children.Add(buttons);
        Child = body;
    }

    public Button StartButton => _start;

    public Button CancelButton => _cancel;

    public Button RevealButton => _reveal;

    public Button CloseButton => _close;

    public ProgressBar ProgressBar => _progress;

    public TextBlock StatusText => _status;

    public ItemsControl HistoryList => _history;

    public string? ActiveExportId => _exportId;

    public ExportSnapshotInfo? LastSnapshot => _last;

    public IReadOnlyList<string> TranslatedPageIds => _translated;

    /// <summary>Tests disable the internal timer and drive <see cref="TickAsync"/> deterministically.</summary>
    public bool AutoPoll { get; set; } = true;

    public Task LastOperation { get; private set; } = Task.CompletedTask;

    public string SuggestedTargetPath()
    {
        var directory = _controller.ExportDirectorySuggestion;
        if (string.IsNullOrWhiteSpace(directory))
        {
            return string.Empty;
        }

        return Path.Combine(directory, ImportExportFormatting.DefaultExportFileName(_bookTitle, _chapterTitle));
    }

    /// <summary>AC2: load the reader context (book/chapter + its translated pages + history).</summary>
    public async Task PrepareAsync(string bookId, string bookTitle, string chapterId, string chapterTitle)
    {
        _bookId = bookId;
        _bookTitle = string.IsNullOrWhiteSpace(bookTitle) ? "未命名" : bookTitle;
        _chapterId = chapterId;
        _chapterTitle = string.IsNullOrWhiteSpace(chapterTitle) ? "第 1 章" : chapterTitle;
        _exportId = null;
        _last = null;
        _pollCount = 0;
        IsVisible = true;
        _reveal.IsEnabled = false;
        _cancel.IsEnabled = false;
        _progress.IsVisible = false;
        _start.IsEnabled = false;
        _context.Text = $"{_bookTitle} · {_chapterTitle}";
        _status.Text = "正在读取可导出的翻译页…";
        _translated = await _controller.GetTranslatedPageIdsAsync(chapterId);
        await RefreshHistoryAsync();
        if (string.IsNullOrWhiteSpace(_controller.ExportDirectorySuggestion))
        {
            _status.Text = "导出不可用：Host 未就绪或没有数据根";
            return;
        }

        if (_translated.Count == 0)
        {
            _status.Text = "没有可导出的翻译页：请先对该章运行翻译，再回到这里导出";
            _context.Text = $"{_bookTitle} · {_chapterTitle} · 0 页可导出";
            return;
        }

        _context.Text = $"{_bookTitle} · {_chapterTitle} · {_translated.Count} 页可导出";
        _status.Text = $"可导出 {_translated.Count} 页已翻译内容：点击「开始导出」";
        _start.IsEnabled = true;
    }

    public async Task RefreshHistoryAsync()
    {
        var history = await _controller.GetExportHistoryAsync();
        _history.ItemsSource = history
            .Take(5)
            .Select(ImportExportFormatting.HistoryLine)
            .ToList();
    }

    public async Task StartAsync()
    {
        if (_busy || _bookId is null || _chapterId is null)
        {
            return;
        }

        if (_translated.Count == 0)
        {
            _status.Text = "没有可导出的翻译页：请先翻译该章";
            return;
        }

        var target = SuggestedTargetPath();
        if (string.IsNullOrWhiteSpace(target))
        {
            _status.Text = "导出不可用：Host 未就绪或没有数据根";
            return;
        }

        _busy = true;
        _start.IsEnabled = false;
        _status.Text = "正在请求 Host 导出（签发目标 grant）…";
        _progress.IsIndeterminate = true;
        _progress.Value = 0;
        _progress.IsVisible = true;
        try
        {
            var started = await _controller.StartExportAsync(_bookId, _chapterId, _translated, target);
            if (started is null || string.IsNullOrWhiteSpace(started.ExportId))
            {
                _progress.IsVisible = false;
                _status.Text = "导出被拒绝：目标/输入不可用（EXPORT_PATH_UNAVAILABLE / EXPORT_INPUT_UNAVAILABLE），详见 Host 日志";
                return;
            }

            _exportId = started.ExportId;
            _last = ExportSnapshotInfo.FromState(started.ExportId, started.State, 0, started.PageCount);
            UpdateFromSnapshot(_last);
            await TickAsync();
            StartTimer();
        }
        finally
        {
            _busy = false;
            _start.IsEnabled = _exportId is null;
        }
    }

    /// <summary>One snapshot poll; the timer calls this, tests call it explicitly.</summary>
    public async Task TickAsync()
    {
        if (_exportId is null)
        {
            return;
        }

        var snapshot = await _controller.GetExportSnapshotAsync(_exportId);
        if (snapshot is null)
        {
            StopTimer();
            _status.Text = "读取导出进度失败（Host 未就绪）；已停止轮询";
            return;
        }

        _last = snapshot;
        UpdateFromSnapshot(snapshot);
        _pollCount++;
        if (snapshot.IsTerminal)
        {
            StopTimer();
            _reveal.IsEnabled = snapshot.State == ExportJobState.Completed;
            _cancel.IsEnabled = false;
            _start.IsEnabled = snapshot.State != ExportJobState.Completed;
            await RefreshHistoryAsync();
        }
        else if (_pollCount >= 200)
        {
            StopTimer();
            _status.Text = ImportExportFormatting.SnapshotStatus(snapshot) + "（轮询超时，可稍后在历史中确认）";
        }
    }

    public async Task CancelAsync()
    {
        if (_exportId is null)
        {
            return;
        }

        var snapshot = await _controller.CancelExportAsync(_exportId);
        if (snapshot is null)
        {
            _status.Text = "取消请求失败（Host 未就绪）";
            return;
        }

        _last = snapshot;
        UpdateFromSnapshot(snapshot);
        if (snapshot.IsTerminal)
        {
            StopTimer();
            _cancel.IsEnabled = false;
            _reveal.IsEnabled = false;
            await RefreshHistoryAsync();
        }
    }

    public async Task RevealAsync()
    {
        if (_exportId is null || _last?.State != ExportJobState.Completed)
        {
            _status.Text = "没有已完成的导出记录可打开";
            return;
        }

        var opened = await _controller.RevealExportFolderAsync(_exportId);
        _status.Text = opened ? "已打开导出目录" : "打开导出目录失败（EXPORT_PATH_UNAVAILABLE / EXPORT_NOT_FOUND）";
    }

    public void Close()
    {
        StopTimer();
        IsVisible = false;
    }

    private void UpdateFromSnapshot(ExportSnapshotInfo snapshot)
    {
        _status.Text = ImportExportFormatting.SnapshotStatus(snapshot);
        _progress.IsVisible = snapshot.IsActive;
        if (snapshot.IsActive)
        {
            _progress.IsIndeterminate = snapshot.TotalPages <= 0;
            if (!_progress.IsIndeterminate)
            {
                _progress.Value = snapshot.ProgressPercent;
            }
        }

        _cancel.IsEnabled = snapshot.IsActive;
    }

    private void StartTimer()
    {
        if (!AutoPoll)
        {
            return;
        }

        StopTimer();
        _timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(300) };
        _timer.Tick += (_, _) => LastOperation = TickAsync();
        _timer.Start();
    }

    private void StopTimer()
    {
        if (_timer is not null)
        {
            _timer.Stop();
            _timer = null;
        }
    }
}
