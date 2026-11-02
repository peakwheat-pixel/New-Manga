using System.Diagnostics;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.ViewModels;
using NewManga.CoreClient;
using NewManga.App.Views.Legacy;

namespace NewManga.App.Views;

/// <summary>
/// READER-WORKBENCH-1: single-page workbench over the real Core data. Book → chapter → page
/// navigation uses the Host read face; the page image comes through the resource channel
/// (<c>ReadPageImageAsync</c>); the region overlay projects the Core <c>list_regions</c> normalized
/// geometry through the returned <c>page_size</c>; retype / revision restore / manual rerender go
/// through the Host write face and are gated by <c>Policy.WritesAllowed</c> (typed read-only state in
/// the UI). The 300/mid/230 column contract, 50–200% zoom and no-interpolation page image are kept.
/// </summary>
public sealed class WorkbenchPage : UserControl
{
    /// <summary>The frozen Core RegionType six-value closed set (domain.regions.entities.RegionType).</summary>
    public static IReadOnlyList<string> RegionTypeValues { get; } = new[]
    {
        "speech",
        "narration",
        "sfx",
        "title",
        "note",
        "other",
    };

    private readonly IHostController? _controller;
    private readonly IFilePickerGateway? _picker;
    private ImportPanel? _importPanel;
    private readonly Image _pageImage;
    private readonly Border _placeholder;
    private readonly Canvas _regionOverlay;
    private readonly ComboBox _bookSelector;
    private readonly ComboBox _chapterSelector;
    private readonly ComboBox _pageSelector;
    private readonly ComboBox _regionTypeSelector;
    private readonly SemaphoreSlim _loadGate = new(1, 1);

    private IReadOnlyList<ChapterSummary> _chapters = Array.Empty<ChapterSummary>();
    private IReadOnlyList<ChapterPageSummary> _pages = Array.Empty<ChapterPageSummary>();
    private RegionPageProjection? _pageProjection;
    private Bitmap? _pageBitmap;
    private bool _suppressNavigation;
    private bool _syncingSelection;

    public WorkbenchPage(
        WorkbenchViewModel viewModel,
        IHostController? controller = null,
        IFilePickerGateway? picker = null)
    {
        ViewModel = viewModel;
        _controller = controller;
        _picker = picker;
        Name = "WorkbenchPage";

        _pageImage = new Image { Stretch = Stretch.Fill, IsVisible = false };
        RenderOptions.SetBitmapInterpolationMode(_pageImage, BitmapInterpolationMode.None);
        Canvas.SetLeft(_pageImage, 0);
        Canvas.SetTop(_pageImage, 0);
        PageImageControl = _pageImage;

        _placeholder = new Border
        {
            Width = 720,
            Height = 520,
            Background = new SolidColorBrush(Color.Parse("#1E222B")),
            Child = new TextBlock
            {
                Text = "单页画布（选择书 / 章 / 页后显示真实页图与 Core region 覆盖）",
                Foreground = LegacyChrome.Brush("TextSecondary"),
                FontSize = 12,
                TextWrapping = TextWrapping.Wrap,
                TextAlignment = TextAlignment.Center,
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
            },
        };
        Canvas.SetLeft(_placeholder, 40);
        Canvas.SetTop(_placeholder, 30);

        // One coordinate space: the page image, the skeleton placeholder and the region overlay all
        // live on RegionLayer (the existing name the S4/S5 tests assert on).
        _regionOverlay = new Canvas();
        RegionLayer = new Canvas();
        RegionLayer.Children.Add(_pageImage);
        RegionLayer.Children.Add(_placeholder);
        RegionLayer.Children.Add(_regionOverlay);

        _bookSelector = new ComboBox
        {
            Name = "WorkbenchBookSelector",
            MinWidth = 220,
            FontSize = 12,
        };
        _bookSelector.SelectionChanged += OnBookSelectionChanged;
        _chapterSelector = new ComboBox
        {
            Name = "WorkbenchChapterSelector",
            MinWidth = 220,
            FontSize = 12,
        };
        _chapterSelector.SelectionChanged += OnChapterSelectionChanged;
        _pageSelector = new ComboBox
        {
            Name = "WorkbenchPageSelector",
            MinWidth = 220,
            FontSize = 12,
        };
        _pageSelector.SelectionChanged += OnPageSelectionChanged;
        _regionTypeSelector = new ComboBox
        {
            Name = "RegionTypeSelector",
            ItemsSource = RegionTypeValues,
            SelectedIndex = 0,
            MinWidth = 220,
            FontSize = 12,
        };
        RegionTypeSelector = _regionTypeSelector;

        ReadOnlyBanner = new TextBlock
        {
            Name = "WorkbenchReadOnlyBanner",
            FontSize = 11,
            Foreground = LegacyChrome.Brush("TextSecondary"),
            TextWrapping = TextWrapping.Wrap,
            IsVisible = false,
        };
        StatusText = new TextBlock
        {
            Name = "WorkbenchStatusText",
            FontSize = 11,
            Foreground = LegacyChrome.Brush("TextSecondary"),
            TextWrapping = TextWrapping.Wrap,
        };
        SelectionDetail = new TextBlock
        {
            Name = "WorkbenchSelectionDetail",
            FontSize = 11,
            Foreground = LegacyChrome.Brush("TextSecondary"),
            TextWrapping = TextWrapping.Wrap,
        };

        var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("300,*,230") };
        // READER-WORKBENCH-1: the S4 skeleton added all three columns without Grid.SetColumn, so the
        // right panel painted over the left one. The three column contract is now explicit.
        var left = BuildLeft();
        Grid.SetColumn(left, 0);
        grid.Children.Add(left);
        var center = BuildCenter();
        Grid.SetColumn(center, 1);
        grid.Children.Add(center);
        var right = BuildRight();
        Grid.SetColumn(right, 2);
        grid.Children.Add(right);
        if (_controller is not null)
        {
            // IMPORT-EXPORT-UI-1 AC1: the workbench exposes the same import entries as the shelf.
            _importPanel = new ImportPanel(_controller) { IsVisible = false };
            Grid.SetColumnSpan(_importPanel, 3);
            _importPanel.ImportCompleted += (_, _) => LastImportOperation = RefreshAfterImportAsync();
            grid.Children.Add(_importPanel);
            _controller.Changed += OnControllerChanged;
        }

        Content = grid;
        ViewModel.PropertyChanged += OnViewModelPropertyChanged;
        ApplyTheme();
        ApplyReadOnlyState();
        StatusText.Text = _controller is null
            ? "未连接 Host：画布为占位预览，region 数据不可用"
            : "选择书 / 章 / 页后加载真实页图与 Core region";
    }

    public WorkbenchViewModel ViewModel { get; }

    /// <summary>IMPORT-EXPORT-UI-1 AC1: workbench import entries.</summary>
    public Button ImportFilesButton { get; private set; } = null!;

    public Button ImportFolderButton { get; private set; } = null!;

    public ImportPanel? ImportPanelControl => _importPanel;

    public Task LastImportOperation { get; private set; } = Task.CompletedTask;

    public ITileSource? TileSource { get; private set; }

    public void BindTileSource(ITileSource? source) => TileSource = source;

    public Grid Root => (Grid)Content!;

    public Slider ZoomSlider { get; private set; } = null!;

    public TextBlock ZoomLabel { get; private set; } = null!;

    /// <summary>READER-WORKBENCH-1: canvas that holds the page image + the region overlay boxes.</summary>
    public Canvas RegionLayer { get; }

    public Border CanvasHost { get; private set; } = null!;

    public ListBox RegionList { get; private set; } = null!;

    public TextBox BubbleText { get; private set; } = null!;

    public ComboBox BubbleOrientation { get; private set; } = null!;

    public ItemsControl ThumbnailList { get; private set; } = null!;

    /// <summary>AC1: book selector fed from the Host book snapshot.</summary>
    public ComboBox BookSelector => _bookSelector;

    /// <summary>AC1: chapter selector fed from <c>list_chapters</c>.</summary>
    public ComboBox ChapterSelector => _chapterSelector;

    /// <summary>AC1: page selector fed from <c>list_chapter_pages</c>.</summary>
    public ComboBox PageSelector => _pageSelector;

    /// <summary>AC2: region type picker (frozen RegionType closed set).</summary>
    public ComboBox RegionTypeSelector { get; }

    /// <summary>AC2: 「应用类型」 entry.</summary>
    public Button ApplyRegionTypeButton { get; private set; } = null!;

    /// <summary>AC2: 「撤销到上一 revision」 entry.</summary>
    public Button UndoRegionRevisionButton { get; private set; } = null!;

    /// <summary>AC2: 「重渲染本页」 entry.</summary>
    public Button RerenderPageButton { get; private set; } = null!;

    /// <summary>AC3: read-only reason banner (visible + reason text when writes are gated).</summary>
    public TextBlock ReadOnlyBanner { get; }

    /// <summary>Status line of the last load/write (evidence + tests).</summary>
    public TextBlock StatusText { get; }

    /// <summary>Selected region detail ("id · type · origin · sfx · revision").</summary>
    public TextBlock SelectionDetail { get; }

    /// <summary>AC1: the decoded page image control.</summary>
    public Image PageImageControl { get; }

    public double LeftColumnWidth => Root.ColumnDefinitions[0].Width.Value;

    public double RightColumnWidth => Root.ColumnDefinitions[2].Width.Value;

    /// <summary>AC1: book currently loaded (null = nothing loaded yet).</summary>
    public string? LoadedBookId { get; private set; }

    /// <summary>AC1: chapter currently loaded (null = nothing loaded yet).</summary>
    public string? LoadedChapterId { get; private set; }

    /// <summary>AC1: page currently loaded (null = nothing loaded yet).</summary>
    public string? LoadedPageId { get; private set; }

    /// <summary>AC1: last <c>list_regions</c> projection (regions + page pixel extent).</summary>
    public RegionPageProjection? PageProjection => _pageProjection;

    /// <summary>AC2: last typed retype/restore outcome (tests + evidence).</summary>
    public RegionOperationResult? LastWriteResult { get; private set; }

    /// <summary>AC2: last typed rerender outcome (tests + evidence).</summary>
    public PageRerenderOutcome? LastRerenderOutcome { get; private set; }

    /// <summary>AC2: last async write triggered by the UI buttons (tests/evidence await this).</summary>
    public Task LastWriteOperation { get; private set; } = Task.CompletedTask;

    /// <summary>AC2: last async rerender triggered by the UI button.</summary>
    public Task LastRerenderOperation { get; private set; } = Task.CompletedTask;

    /// <summary>AC3: true only when the Host is ready, writable and a region is selected.</summary>
    public bool WriteControlsEnabled => ApplyRegionTypeButton.IsEnabled;

    /// <summary>AC3: the reason shown while the write controls are disabled (empty = writable).</summary>
    public string ReadOnlyReasonText
    {
        get
        {
            if (_controller is null)
            {
                return "未连接 Host：工作台只显示占位画布";
            }

            var snapshot = _controller.Snapshot;
            if (snapshot.State != HostViewState.Ready)
            {
                return "Host 未就绪：页图与 region 读取暂不可用";
            }

            return snapshot.WritesAllowed
                ? string.Empty
                : "只读模式（Host 未达 S2 parity）：改类型 / 撤销 / 重渲染已禁用；region 读取仍可用";
        }
    }

    public void ApplyTheme()
    {
        Background = LegacyChrome.Brush("AppBg");
    }

    /// <summary>
    /// AC1: loads the default real book/chapter/page chain once the Host is ready (idempotent — a
    /// second call after a successful load is a no-op). Never throws: failures surface as status text.
    /// </summary>
    public async Task<bool> EnsureLoadedAsync(CancellationToken cancellationToken = default)
    {
        if (_controller is null)
        {
            return false;
        }

        await _loadGate.WaitAsync(cancellationToken).ConfigureAwait(true);
        try
        {
            ApplyReadOnlyState();
            if (_controller.Snapshot.State != HostViewState.Ready)
            {
                return false;
            }

            if (LoadedPageId is not null)
            {
                return true;
            }

            try
            {
                await _controller.RefreshBooksAsync(cancellationToken).ConfigureAwait(true);
                var books = _controller.Snapshot.Books;
                PopulateBooks(books);
                var book = books.FirstOrDefault(candidate => (candidate.PageCount ?? 0) > 0) ?? books.FirstOrDefault();
                if (book is null)
                {
                    StatusText.Text = "书架为空：没有可加载的书";
                    return false;
                }

                return await LoadBookAsync(book.BookId, cancellationToken).ConfigureAwait(true);
            }
            catch (Exception ex) when (ex is IOException or InvalidOperationException or TimeoutException or OperationCanceledException)
            {
                StatusText.Text = "加载书库失败：" + ex.Message;
                return false;
            }
        }
        finally
        {
            _loadGate.Release();
        }
    }

    /// <summary>AC1: loads one book, its chapter list and the first chapter's first page.</summary>
    public async Task<bool> LoadBookAsync(string bookId, CancellationToken cancellationToken = default)
    {
        if (_controller is null || string.IsNullOrWhiteSpace(bookId))
        {
            return false;
        }

        LoadedBookId = bookId;
        LoadedChapterId = null;
        LoadedPageId = null;
        _chapters = await _controller.ListChaptersAsync(bookId, cancellationToken).ConfigureAwait(true);
        var choices = _chapters.Select(chapter => new ChapterChoice(chapter.ChapterId, FormatChapterLabel(chapter))).ToList();
        _suppressNavigation = true;
        try
        {
            _chapterSelector.ItemsSource = choices;
            _chapterSelector.SelectedItem = choices.FirstOrDefault();
        }
        finally
        {
            _suppressNavigation = false;
        }

        var first = _chapters.FirstOrDefault();
        if (first is null)
        {
            _pages = Array.Empty<ChapterPageSummary>();
            _pageSelector.ItemsSource = Array.Empty<PageChoice>();
            StatusText.Text = "该书没有章节";
            ClearPage();
            return false;
        }

        return await LoadChapterAsync(bookId, first.ChapterId, cancellationToken).ConfigureAwait(true);
    }

    /// <summary>AC1: loads one chapter's ordered page list (list_chapter_pages) and its first page.</summary>
    public async Task<bool> LoadChapterAsync(
        string bookId,
        string chapterId,
        CancellationToken cancellationToken = default)
    {
        if (_controller is null || string.IsNullOrWhiteSpace(chapterId))
        {
            return false;
        }

        LoadedBookId = string.IsNullOrWhiteSpace(bookId) ? LoadedBookId : bookId;
        LoadedChapterId = chapterId;
        LoadedPageId = null;
        _pages = (await _controller.ListChapterPagesAsync(chapterId, cancellationToken).ConfigureAwait(true))
            .OrderBy(page => page.SortOrder)
            .ToList();
        var choices = _pages.Select((page, index) => new PageChoice(page.PageId, $"{index + 1} · {page.SourceFilename}")).ToList();
        _suppressNavigation = true;
        try
        {
            _pageSelector.ItemsSource = choices;
            _pageSelector.SelectedItem = choices.FirstOrDefault();
        }
        finally
        {
            _suppressNavigation = false;
        }

        ViewModel.LoadThumbnails(choices.Select(choice => choice.Label));

        if (choices.Count == 0)
        {
            StatusText.Text = "该章没有页";
            ClearPage();
            return false;
        }

        return await LoadPageAsync(choices[0].PageId, cancellationToken).ConfigureAwait(true);
    }

    /// <summary>
    /// AC1/AC2: loads one page — image bytes through the Host resource channel, then the Core
    /// <c>list_regions</c> projection; the region list and the canvas overlay are rebuilt from the
    /// real rows. Also used to refresh after a successful write.
    /// </summary>
    public async Task<bool> LoadPageAsync(string pageId, CancellationToken cancellationToken = default)
    {
        if (_controller is null || string.IsNullOrWhiteSpace(pageId))
        {
            return false;
        }

        LoadedPageId = pageId;
        StatusText.Text = "加载页图与 region…";
        byte[]? bytes = null;
        try
        {
            bytes = await _controller.ReadPageImageAsync(pageId, cancellationToken).ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is IOException or InvalidOperationException or TimeoutException or OperationCanceledException)
        {
            bytes = null;
        }

        SetPageBitmap(DecodePageImage(bytes));
        try
        {
            _pageProjection = await _controller.LoadPageRegionsAsync(pageId, cancellationToken).ConfigureAwait(true);
        }
        catch (Exception ex) when (ex is IOException or InvalidOperationException or TimeoutException or OperationCanceledException)
        {
            _pageProjection = null;
        }

        ApplyProjection(_pageProjection);
        RefreshCanvas();
        UpdateSelectionUi();
        if (_pageProjection is { } projection)
        {
            StatusText.Text = $"已加载 {projection.Regions.Count} 个 region"
                              + (projection.PageSize is { } size ? $" · 页 {size.Width}×{size.Height}" : " · 无 page_size")
                              + (_pageBitmap is null ? " · 页图不可用" : string.Empty);
        }
        else
        {
            StatusText.Text = _pageBitmap is null
                ? "页图与 region 加载失败（Host 读面不可用）"
                : "region 加载失败（Host 读面不可用）";
        }

        return _pageProjection is not null || _pageBitmap is not null;
    }

    /// <summary>
    /// AC2: applies the selected region type through <c>set_region_type</c> with the revision the UI
    /// actually read. On success the region list, revision and page are reloaded (real refresh).
    /// </summary>
    public async Task<RegionOperationResult> ApplySelectedRegionTypeAsync(CancellationToken cancellationToken = default)
    {
        var region = ViewModel.SelectedRegion;
        var type = _regionTypeSelector.SelectedItem as string;
        if (region is null || string.IsNullOrEmpty(type))
        {
            LastWriteResult = RegionOperationResult.Failed("INVALID_REQUEST", "请先选择一个区域和类型");
            StatusText.Text = LastWriteResult.Message!;
            return LastWriteResult;
        }

        if (WriteGate() is { } gate)
        {
            LastWriteResult = gate;
            StatusText.Text = ReadOnlyReasonText;
            return LastWriteResult;
        }

        LastWriteResult = await _controller!
            .SetRegionTypeAsync(region.Id, type, region.RevisionNo, cancellationToken)
            .ConfigureAwait(true);
        if (LastWriteResult.IsSuccess)
        {
            await RefreshAfterWriteAsync(region.Id, cancellationToken).ConfigureAwait(true);
        }

        StatusText.Text = LastWriteResult.IsSuccess
            ? LastWriteResult.Message!
            : DescribeFailure(LastWriteResult.Status, LastWriteResult.ErrorCode, LastWriteResult.Message);
        return LastWriteResult;
    }

    /// <summary>
    /// AC2: restores the revision immediately before the current one (<c>list_region_revisions</c>
    /// first, then <c>restore_region_revision</c> with the current revision as the guard).
    /// </summary>
    public async Task<RegionOperationResult> UndoSelectedRegionRevisionAsync(CancellationToken cancellationToken = default)
    {
        var region = ViewModel.SelectedRegion;
        if (region is null)
        {
            LastWriteResult = RegionOperationResult.Failed("INVALID_REQUEST", "请先选择一个区域");
            StatusText.Text = LastWriteResult.Message!;
            return LastWriteResult;
        }

        if (WriteGate() is { } gate)
        {
            LastWriteResult = gate;
            StatusText.Text = ReadOnlyReasonText;
            return LastWriteResult;
        }

        var history = await _controller!
            .LoadRegionRevisionsAsync(region.Id, cancellationToken)
            .ConfigureAwait(true);
        if (history is null)
        {
            LastWriteResult = RegionOperationResult.Failed("REVISION_HISTORY_UNAVAILABLE", "读取 region revision 历史失败");
            StatusText.Text = LastWriteResult.Message!;
            return LastWriteResult;
        }

        var current = history.CurrentRevisionNo;
        var previous = history.Revisions
            .Where(revision => revision.RevisionNo < current)
            .OrderByDescending(revision => revision.RevisionNo)
            .FirstOrDefault();
        if (previous is null)
        {
            LastWriteResult = RegionOperationResult.Failed("NO_PREVIOUS_REVISION", "没有更早的 revision 可撤销");
            StatusText.Text = LastWriteResult.Message!;
            return LastWriteResult;
        }

        LastWriteResult = await _controller!
            .RestoreRegionRevisionAsync(region.Id, previous.RevisionNo, current, cancellationToken)
            .ConfigureAwait(true);
        if (LastWriteResult.IsSuccess)
        {
            await RefreshAfterWriteAsync(region.Id, cancellationToken).ConfigureAwait(true);
        }

        StatusText.Text = LastWriteResult.IsSuccess
            ? LastWriteResult.Message!
            : DescribeFailure(LastWriteResult.Status, LastWriteResult.ErrorCode, LastWriteResult.Message);
        return LastWriteResult;
    }

    /// <summary>AC2: manual page rerender; on success the page image and regions are reloaded.</summary>
    public async Task<PageRerenderOutcome> RerenderCurrentPageAsync(CancellationToken cancellationToken = default)
    {
        if (LoadedPageId is not { } pageId)
        {
            LastRerenderOutcome = PageRerenderOutcome.Failed("INVALID_REQUEST", "尚未加载页面");
            StatusText.Text = LastRerenderOutcome.Message!;
            return LastRerenderOutcome;
        }

        if (_controller is null || _controller.Snapshot.State != HostViewState.Ready)
        {
            LastRerenderOutcome = PageRerenderOutcome.NotReady();
            StatusText.Text = ReadOnlyReasonText;
            return LastRerenderOutcome;
        }

        if (!_controller.Snapshot.WritesAllowed)
        {
            LastRerenderOutcome = PageRerenderOutcome.ReadOnly();
            StatusText.Text = ReadOnlyReasonText;
            return LastRerenderOutcome;
        }

        LastRerenderOutcome = await _controller!
            .RerenderPageAsync(pageId, cancellationToken)
            .ConfigureAwait(true);
        if (LastRerenderOutcome.IsSuccess)
        {
            await LoadPageAsync(pageId, cancellationToken).ConfigureAwait(true);
        }

        StatusText.Text = LastRerenderOutcome.IsSuccess
            ? LastRerenderOutcome.Message!
            : DescribeFailure(LastRerenderOutcome.Status, LastRerenderOutcome.ErrorCode, LastRerenderOutcome.Message);
        return LastRerenderOutcome;
    }

    /// <summary>
    /// AC1: canvas → list selection (the overlay box click path). The ViewModel is the single source
    /// of truth; the list box selection is synced back without re-entering the change handler.
    /// </summary>
    public void SelectRegionFromCanvas(RegionItem region)
    {
        ViewModel.SelectedRegion = region;
        SyncRegionListSelection();
        UpdateSelectionUi();
    }

    /// <summary>AC3: refreshes the banner + write-control enablement from the Host snapshot.</summary>
    public void ApplyReadOnlyState()
    {
        var reason = ReadOnlyReasonText;
        ReadOnlyBanner.Text = reason;
        ReadOnlyBanner.IsVisible = !string.IsNullOrEmpty(reason);
        UpdateWriteControlsEnabled();
    }

    /// <summary>AC3: typed write gate — NotReady before Ready, ReadOnly before parity; null = writable.</summary>
    private RegionOperationResult? WriteGate()
    {
        if (_controller is null || _controller.Snapshot.State != HostViewState.Ready)
        {
            return RegionOperationResult.NotReady();
        }

        return _controller.Snapshot.WritesAllowed ? null : RegionOperationResult.ReadOnly();
    }

    private Control BuildLeft()
    {
        var panel = new StackPanel { Spacing = 10, Margin = new Thickness(16) };
        panel.Children.Add(Ui.Text("区域工作台", 15, "TextPrimary", bold: true));
        panel.Children.Add(Ui.Text("真实 Core region · 读面可用，写面受 parity 只读门约束", 11, "TextSecondary"));
        var zoomRow = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        ZoomLabel = Ui.Text(ViewModel.ZoomLabel, 12, "TextPrimary", bold: true);
        Grid.SetColumn(ZoomLabel, 1);
        ZoomSlider = new Slider
        {
            Minimum = WorkbenchViewModel.MinZoomPercent,
            Maximum = WorkbenchViewModel.MaxZoomPercent,
            TickFrequency = WorkbenchViewModel.ZoomStep,
            Value = ViewModel.ZoomPercent,
            Width = 180,
        };
        ZoomSlider.PropertyChanged += (_, args) =>
        {
            if (args.Property == Slider.ValueProperty)
            {
                ViewModel.ZoomPercent = ZoomSlider.Value;
                ZoomLabel.Text = ViewModel.ZoomLabel;
                RefreshCanvas();
            }
        };
        var zoomBox = new StackPanel { Spacing = 6 };
        zoomBox.Children.Add(Ui.Text("缩放 50–200%", 11, "TextSecondary"));
        zoomBox.Children.Add(ZoomSlider);
        panel.Children.Add(zoomBox);
        zoomRow.Children.Add(Ui.Text("画布缩放", 12, "TextSecondary"));
        zoomRow.Children.Add(ZoomLabel);
        panel.Children.Add(zoomRow);

        panel.Children.Add(Ui.Text("内容 (book → chapter → page)", 13, "TextPrimary", bold: true));
        panel.Children.Add(_bookSelector);
        panel.Children.Add(_chapterSelector);
        panel.Children.Add(_pageSelector);

        panel.Children.Add(ReadOnlyBanner);
        panel.Children.Add(StatusText);
        panel.Children.Add(SelectionDetail);

        panel.Children.Add(Ui.Text("区域 (Region)", 13, "TextPrimary", bold: true));
        RegionList = new ListBox { ItemsSource = ViewModel.Regions, Height = 140 };
        RegionList.SelectionChanged += OnRegionListSelectionChanged;
        panel.Children.Add(RegionList);

        panel.Children.Add(Ui.Text("改标 / 撤销 / 重渲染", 13, "TextPrimary", bold: true));
        panel.Children.Add(RegionTypeSelector);
        ApplyRegionTypeButton = Ui.Action(
            "应用类型",
            () => LastWriteOperation = ApplySelectedRegionTypeAsync(),
            primary: true);
        ApplyRegionTypeButton.Name = "ApplyRegionTypeButton";
        UndoRegionRevisionButton = Ui.Action(
            "撤销到上一 revision",
            () => LastWriteOperation = UndoSelectedRegionRevisionAsync());
        UndoRegionRevisionButton.Name = "UndoRegionRevisionButton";
        RerenderPageButton = Ui.Action(
            "重渲染本页",
            () => LastRerenderOperation = RerenderCurrentPageAsync());
        RerenderPageButton.Name = "RerenderPageButton";
        panel.Children.Add(ApplyRegionTypeButton);
        panel.Children.Add(UndoRegionRevisionButton);
        panel.Children.Add(RerenderPageButton);

        panel.Children.Add(Ui.Text("导入", 13, "TextPrimary", bold: true));
        var importRow = new StackPanel { Orientation = Avalonia.Layout.Orientation.Horizontal, Spacing = 6 };
        ImportFilesButton = Ui.Action("导入文件", () => LastImportOperation = BeginImportAsync(ImportSourceKind.Files));
        ImportFilesButton.Name = "WorkbenchImportFilesButton";
        ImportFolderButton = Ui.Action("导入文件夹", () => LastImportOperation = BeginImportAsync(ImportSourceKind.Folder));
        ImportFolderButton.Name = "WorkbenchImportFolderButton";
        importRow.Children.Add(ImportFilesButton);
        importRow.Children.Add(ImportFolderButton);
        panel.Children.Add(importRow);
        return new Border { Background = LegacyChrome.Brush("CardBg"), Child = new ScrollViewer { Content = panel } };
    }

    private Control BuildCenter()
    {
        var dock = new DockPanel();
        var toolbar = new StackPanel
        {
            Orientation = Avalonia.Layout.Orientation.Horizontal,
            Spacing = 10,
            Margin = new Thickness(12, 8),
            Background = LegacyChrome.Brush("NavBg"),
        };
        toolbar.Children.Add(Ui.Text("Canvas · 单页真实页图 + Core region 覆盖（无插值）", 11, "TextSecondary"));
        DockPanel.SetDock(toolbar, Dock.Top);
        dock.Children.Add(toolbar);

        CanvasHost = new Border
        {
            Background = LegacyChrome.Brush("ReaderBackground"),
            Child = new ScrollViewer
            {
                Content = RegionLayer,
                HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
            },
        };
        dock.Children.Add(CanvasHost);
        return dock;
    }

    private Control BuildRight()
    {
        var panel = new StackPanel { Spacing = 10, Margin = new Thickness(12) };
        panel.Children.Add(Ui.Text("缩略图", 13, "TextPrimary", bold: true));
        ThumbnailList = new ItemsControl { ItemsSource = ViewModel.Thumbnails, Height = 200 };
        ThumbnailList.ItemTemplate = new Avalonia.Controls.Templates.FuncDataTemplate<string>((label, _) =>
            new Border
            {
                Padding = new Thickness(6),
                Margin = new Thickness(0, 0, 0, 4),
                CornerRadius = new CornerRadius(6),
                Background = LegacyChrome.Brush("ChipBg"),
                Child = Ui.Text(label, 11, "TextSecondary"),
            });
        panel.Children.Add(ThumbnailList);
        panel.Children.Add(Ui.Text("气泡检查器", 13, "TextPrimary", bold: true));
        BubbleText = new TextBox { Text = ViewModel.SelectedBubble?.Text ?? string.Empty, Watermark = "气泡文本" };
        BubbleOrientation = new ComboBox
        {
            ItemsSource = new[] { "horizontal", "vertical" },
            SelectedIndex = 0,
        };
        var addBubble = Ui.Action("添加气泡", () => ViewModel.AddBubble(10, 10), primary: true);
        addBubble.Name = "AddBubbleButton";
        var apply = Ui.Action("应用到选中", () => ViewModel.UpdateBubble(BubbleText.Text, BubbleOrientation.SelectedItem as string));
        panel.Children.Add(BubbleText);
        panel.Children.Add(BubbleOrientation);
        panel.Children.Add(addBubble);
        panel.Children.Add(apply);
        return new Border { Background = LegacyChrome.Brush("CardBg"), Child = new ScrollViewer { Content = panel } };
    }

    // ------------------------------------------------------------------
    // AC1: book/chapter/page navigation
    // ------------------------------------------------------------------

    private void PopulateBooks(IReadOnlyList<BookSummary> books)
    {
        var choices = books.Select(book => new BookChoice(book.BookId, string.IsNullOrWhiteSpace(book.Title) ? book.BookId : book.Title)).ToList();
        _suppressNavigation = true;
        try
        {
            _bookSelector.ItemsSource = choices;
            _bookSelector.SelectedItem = choices.FirstOrDefault();
        }
        finally
        {
            _suppressNavigation = false;
        }
    }

    private void OnBookSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (_suppressNavigation || _bookSelector.SelectedItem is not BookChoice choice)
        {
            return;
        }

        if (string.Equals(choice.BookId, LoadedBookId, StringComparison.Ordinal))
        {
            return;
        }

        _ = LoadBookAsync(choice.BookId);
    }

    private void OnChapterSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (_suppressNavigation || _chapterSelector.SelectedItem is not ChapterChoice choice)
        {
            return;
        }

        if (string.Equals(choice.ChapterId, LoadedChapterId, StringComparison.Ordinal))
        {
            return;
        }

        _ = LoadChapterAsync(LoadedBookId ?? string.Empty, choice.ChapterId);
    }

    private void OnPageSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (_suppressNavigation || _pageSelector.SelectedItem is not PageChoice choice)
        {
            return;
        }

        if (string.Equals(choice.PageId, LoadedPageId, StringComparison.Ordinal))
        {
            return;
        }

        _ = LoadPageAsync(choice.PageId);
    }

    // ------------------------------------------------------------------
    // AC1/AC2: region list, canvas overlay and selection synchronization
    // ------------------------------------------------------------------

    private void ApplyProjection(RegionPageProjection? projection)
    {
        var items = new List<RegionItem>();
        if (projection is not null)
        {
            foreach (var row in projection.Regions)
            {
                var x = 0d;
                var y = 0d;
                var width = 0d;
                var height = 0d;
                if (row.Geometry is { } geometry && projection.PageSize is { Width: > 0, Height: > 0 } pageSize)
                {
                    var rect = geometry.ToPagePixels(pageSize);
                    x = rect.X;
                    y = rect.Y;
                    width = rect.Width;
                    height = rect.Height;
                }

                items.Add(new RegionItem
                {
                    Id = row.RegionId,
                    Kind = row.RegionType,
                    Origin = row.Origin,
                    RevisionNo = row.RevisionNo,
                    SfxPolicy = row.SfxPolicy,
                    X = x,
                    Y = y,
                    Width = width,
                    Height = height,
                });
            }
        }

        ViewModel.ReplaceRegions(items);
    }

    private void RefreshCanvas()
    {
        var scale = ViewModel.DisplayScale;
        var pageSize = EffectivePageSize();
        if (_pageBitmap is not null && pageSize is { Width: > 0, Height: > 0 } bitmapSize)
        {
            _pageImage.Source = _pageBitmap;
            _pageImage.Width = bitmapSize.Width * scale;
            _pageImage.Height = bitmapSize.Height * scale;
            _pageImage.IsVisible = true;
        }
        else
        {
            _pageImage.Source = null;
            _pageImage.IsVisible = false;
        }

        _placeholder.IsVisible = _pageBitmap is null && pageSize is null;
        if (pageSize is { Width: > 0, Height: > 0 } extent)
        {
            _regionOverlay.Width = extent.Width * scale;
            _regionOverlay.Height = extent.Height * scale;
        }
        else
        {
            _regionOverlay.Width = 0;
            _regionOverlay.Height = 0;
        }

        RefreshRegionOverlay();
    }

    private RegionPageSize? EffectivePageSize()
    {
        if (_pageProjection?.PageSize is { Width: > 0, Height: > 0 } projectionSize)
        {
            return projectionSize;
        }

        if (_pageBitmap is { } bitmap)
        {
            return new RegionPageSize(bitmap.PixelSize.Width, bitmap.PixelSize.Height);
        }

        return null;
    }

    private void RefreshRegionOverlay()
    {
        _regionOverlay.Children.Clear();
        var scale = ViewModel.DisplayScale;
        foreach (var region in ViewModel.Regions)
        {
            if (region.Width <= 0 || region.Height <= 0)
            {
                continue;
            }

            var selected = ReferenceEquals(region, ViewModel.SelectedRegion);
            var box = new Border
            {
                Width = region.Width * scale,
                Height = region.Height * scale,
                Background = new SolidColorBrush(Color.Parse(selected ? "#33FFC857" : "#2234C1F0")),
                BorderBrush = new SolidColorBrush(Color.Parse(selected ? "#FFFFC857" : "#FF34C1F0")),
                BorderThickness = new Thickness(selected ? 3 : 1.5),
                CornerRadius = new CornerRadius(3),
                Cursor = new Cursor(StandardCursorType.Hand),
                Tag = region,
            };
            ToolTip.SetTip(box, region.Label);
            Canvas.SetLeft(box, region.X * scale);
            Canvas.SetTop(box, region.Y * scale);
            box.PointerPressed += (_, _) => SelectRegionFromCanvas(region);
            _regionOverlay.Children.Add(box);
        }
    }

    private void OnRegionListSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (_syncingSelection)
        {
            return;
        }

        if (RegionList.SelectedItem is RegionItem region && !ReferenceEquals(region, ViewModel.SelectedRegion))
        {
            ViewModel.SelectedRegion = region;
            UpdateSelectionUi();
        }
    }

    private void SyncRegionListSelection()
    {
        _syncingSelection = true;
        try
        {
            RegionList.SelectedItem = ViewModel.SelectedRegion;
        }
        finally
        {
            _syncingSelection = false;
        }
    }

    private void UpdateSelectionUi()
    {
        SelectionDetail.Text = ViewModel.SelectedRegionDetail;
        var selected = ViewModel.SelectedRegion;
        if (selected is not null && RegionTypeValues.Contains(selected.Kind))
        {
            _regionTypeSelector.SelectedItem = selected.Kind;
        }

        RefreshRegionOverlay();
        UpdateWriteControlsEnabled();
    }

    private void OnViewModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        if (string.IsNullOrEmpty(e.PropertyName) ||
            e.PropertyName is nameof(WorkbenchViewModel.SelectedRegion))
        {
            SyncRegionListSelection();
            UpdateSelectionUi();
        }
    }

    private void OnControllerChanged(object? sender, EventArgs e)
    {
        if (Dispatcher.UIThread.CheckAccess())
        {
            ApplyReadOnlyState();
        }
        else
        {
            Dispatcher.UIThread.Post(ApplyReadOnlyState);
        }
    }

    /// <summary>AC3: write controls require a ready, writable Host plus a loaded target.</summary>
    private void UpdateWriteControlsEnabled()
    {
        var snapshot = _controller?.Snapshot;
        var writable = _controller is not null &&
                       snapshot is { State: HostViewState.Ready, WritesAllowed: true };
        var hasRegion = ViewModel.SelectedRegion is not null;
        _regionTypeSelector.IsEnabled = writable && hasRegion;
        ApplyRegionTypeButton.IsEnabled = writable && hasRegion;
        UndoRegionRevisionButton.IsEnabled = writable && hasRegion;
        RerenderPageButton.IsEnabled = writable && LoadedPageId is not null;
    }

    private async Task RefreshAfterWriteAsync(string regionId, CancellationToken cancellationToken)
    {
        if (LoadedPageId is { } pageId)
        {
            await LoadPageAsync(pageId, cancellationToken).ConfigureAwait(true);
        }

        if (ViewModel.SelectRegionById(regionId))
        {
            SyncRegionListSelection();
            UpdateSelectionUi();
        }
    }

    private static string DescribeFailure(RegionOperationStatus status, string? errorCode, string? message)
    {
        var detail = message ?? errorCode ?? status.ToString();
        return status switch
        {
            RegionOperationStatus.ReadOnly => "只读模式：" + detail,
            RegionOperationStatus.NotReady => "Host 未就绪：" + detail,
            _ => "操作失败：" + detail,
        };
    }

    private void ClearPage()
    {
        LoadedPageId = null;
        _pageProjection = null;
        SetPageBitmap(null);
        ViewModel.ReplaceRegions(Array.Empty<RegionItem>());
        RefreshCanvas();
        UpdateSelectionUi();
    }

    private void SetPageBitmap(Bitmap? bitmap)
    {
        _pageImage.Source = null;
        _pageBitmap?.Dispose();
        _pageBitmap = bitmap;
        if (bitmap is not null)
        {
            _pageImage.Source = bitmap;
        }
    }

    private static Bitmap? DecodePageImage(byte[]? bytes)
    {
        if (bytes is not { Length: > 0 })
        {
            return null;
        }

        try
        {
            using var stream = new MemoryStream(bytes);
            return new Bitmap(stream);
        }
        catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or NotSupportedException)
        {
            return null;
        }
    }

    private async Task BeginImportAsync(ImportSourceKind kind)
    {
        if (_importPanel is null || _picker is null)
        {
            return;
        }

        try
        {
            IReadOnlyList<string> paths = kind == ImportSourceKind.Folder
                ? (await _picker.PickFolderAsync() is { } folder ? new[] { folder } : Array.Empty<string>())
                : await _picker.PickFilesAsync();
            if (paths.Count == 0)
            {
                return;
            }

            await _importPanel.OpenAsync(kind, paths);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
        }
    }

    private async Task RefreshAfterImportAsync()
    {
        if (_controller is not null)
        {
            await _controller.RefreshBooksAsync();
        }
    }

    // ------------------------------------------------------------------
    // chapter picker choice types (kept from the S4 skeleton naming)
    // ------------------------------------------------------------------

    /// <summary>One entry of the chapter picker.</summary>
    public sealed record ChapterChoice(string ChapterId, string Label)
    {
        public override string ToString() => Label;
    }

    /// <summary>AC1: one entry of the workbench page picker.</summary>
    public sealed record PageChoice(string PageId, string Label)
    {
        public override string ToString() => Label;
    }

    /// <summary>AC1: one entry of the workbench book picker.</summary>
    public sealed record BookChoice(string BookId, string Label)
    {
        public override string ToString() => Label;
    }

    private static string FormatChapterLabel(ChapterSummary chapter)
    {
        if (!string.IsNullOrWhiteSpace(chapter.Title))
        {
            // Fixture/Core titles often already read "第 1 章"; avoid a doubled prefix.
            var titleHasNumber = chapter.Title.StartsWith("第", StringComparison.Ordinal);
            return titleHasNumber || string.IsNullOrWhiteSpace(chapter.ChapterNumber)
                ? chapter.Title
                : $"第 {chapter.ChapterNumber} 章 · {chapter.Title}";
        }

        return string.IsNullOrWhiteSpace(chapter.ChapterNumber)
            ? $"第 {chapter.SortOrder} 章"
            : $"第 {chapter.ChapterNumber} 章";
    }
}


/// <summary>
/// AC2/AC3/AC4 reader page: fit/1:1/fit-width + virtualized webtoon, no interpolation.
/// READER-LIBRARY-WIRE-1 AC1: renders a real library book (pages come from the Host resource
/// channel, lazily); the fixture path stays available as the fallback source.
/// </summary>
public sealed class ReaderPage : UserControl
{
    private readonly IReadOnlyList<string> _pages;
    private readonly string? _tileDirectory;
    private readonly List<string> _tileFiles = new();
    private readonly Dictionary<int, Bitmap> _tileCache = new();
    private readonly Dictionary<int, TaskCompletionSource<int>> _pageWaiters = new();
    private readonly HashSet<int> _renderedPages = new();
    private readonly SemaphoreSlim _libraryLoadGate = new(1, 1);
    private readonly Image _pageImage;
    private readonly ScrollViewer _webtoonScroll;
    private readonly ItemsControl _webtoonItems;
    private readonly TextBlock _hud;
    private readonly TextBlock _libraryTitle;
    private readonly TextBlock _emptyState;
    private readonly Button _immersiveButton;
    private readonly Button _exportButton;
    private readonly Border _root;
    private IHostController? _exportController;
    private IFilePickerGateway? _exportPicker;
    private ExportPanel? _exportPanel;
    private Grid? _pageGrid;
    private Bitmap? _currentBitmap;
    private ITileSource? _tileSource;
    private ReaderBookData? _libraryBook;

    // READER-PROGRESS-1: reading clock accumulates only time not yet accepted by the Core
    // (reset after every successful save), so elapsed_seconds_delta is never replayed.
    private readonly Stopwatch _readingClock = Stopwatch.StartNew();
    private readonly SemaphoreSlim _saveGate = new(1, 1);
    private readonly List<Image> _webtoonImages = new();
    private readonly List<double> _webtoonPageHeights = new();
    private ProgressPayload? _pendingPayload;
    private Task _saveLoopTask = Task.CompletedTask;
    private int _saveLoopRunning;
    private string? _lastSavedPageId;
    private double _lastSavedScrollOffsetY;
    private double _lastScrollSaveAtMs;

    // Headless tests have no real scroll extent, so the webtoon offset can be injected.
    private double? _webtoonScrollOverride;

    // READER-PROGRESS-1: a programmatic restore (resume page/offset) fires ScrollChanged events with
    // half-laid-out geometry. Only user-driven navigation may persist, otherwise reopening a webtoon
    // book would immediately overwrite the very position it just restored.
    private bool _webtoonRestoreInProgress;
    private bool _userInteractionSeen;

    // CHAPTER-SELECTOR-1: chapter list of the loaded book + current chapter context.
    private readonly ComboBox _chapterSelector;
    private readonly TextBlock _bookContext;
    private readonly Button _previousChapter;
    private readonly Button _nextChapter;
    private bool _suppressChapterChange;
    private IReadOnlyList<ChapterSummary> _chapters = Array.Empty<ChapterSummary>();
    private string? _loadedChapterId;

    public ReaderPage(ReaderViewModel viewModel, IReadOnlyList<string> pages, string? tileDirectory = null)
    {
        ViewModel = viewModel;
        _pages = pages;
        _tileDirectory = tileDirectory;
        if (Directory.Exists(tileDirectory))
        {
            _tileFiles.AddRange(Directory.GetFiles(tileDirectory, "tile_*.jpg").OrderBy(path => path, StringComparer.Ordinal));
        }

        Name = "ReaderPage";
        _pageImage = new Image { Stretch = Stretch.None, HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center };
        RenderOptions.SetBitmapInterpolationMode(_pageImage, BitmapInterpolationMode.None);
        PageImage = _pageImage;

        _webtoonItems = new ItemsControl
        {
            ItemsPanel = new Avalonia.Controls.Templates.FuncTemplate<Panel?>(() => new VirtualizingStackPanel()),
        };
        _webtoonScroll = new ScrollViewer
        {
            Content = _webtoonItems,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
            IsVisible = false,
        };
        WebtoonScroll = _webtoonScroll;

        _hud = new TextBlock
        {
            Text = "Esc 退出 · F fit · H 隐藏 UI",
            FontSize = 12,
            Foreground = Brushes.White,
            Margin = new Thickness(16, 10),
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
        };
        Hud = _hud;

        _libraryTitle = new TextBlock
        {
            Text = "fixture 回退（无库中书）",
            FontSize = 12,
            Foreground = Brushes.White,
            Margin = new Thickness(8, 10),
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        LibraryTitle = _libraryTitle;

        _emptyState = new TextBlock
        {
            Text = string.Empty,
            FontSize = 13,
            Foreground = Brushes.White,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
            TextAlignment = TextAlignment.Center,
            IsVisible = false,
        };
        EmptyState = _emptyState;

        // CHAPTER-SELECTOR-1 AC1: current book/chapter context + chapter picker (hidden for one chapter).
        _bookContext = new TextBlock
        {
            Text = string.Empty,
            Name = "ReaderBookContext",
            FontSize = 12,
            Foreground = Brushes.White,
            Opacity = 0.85,
            Margin = new Thickness(8, 10),
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        BookContext = _bookContext;

        _chapterSelector = new ComboBox
        {
            Name = "ChapterSelector",
            FontSize = 12,
            MinWidth = 200,
            IsVisible = false,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        _chapterSelector.SelectionChanged += OnChapterSelectionChanged;
        ChapterSelector = _chapterSelector;

        // CHAPTER-SELECTOR-1: previous/next chapter buttons (fast navigation without the popup).
        _previousChapter = new Button
        {
            Content = "上一章",
            Name = "PreviousChapter",
            FontSize = 12,
            Padding = new Thickness(8, 4),
            CornerRadius = new CornerRadius(8),
            IsVisible = false,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        _previousChapter.Click += (_, _) => SelectAdjacentChapter(-1);
        PreviousChapterButton = _previousChapter;
        _nextChapter = new Button
        {
            Content = "下一章",
            Name = "NextChapter",
            FontSize = 12,
            Padding = new Thickness(8, 4),
            CornerRadius = new CornerRadius(8),
            IsVisible = false,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        _nextChapter.Click += (_, _) => SelectAdjacentChapter(1);
        NextChapterButton = _nextChapter;
        StyleToolbarButton(_previousChapter);
        StyleToolbarButton(_nextChapter);

        _immersiveButton = new Button
        {
            Content = "沉浸模式 (Esc/H/F)",
            Name = "ImmersiveButton",
            FontSize = 12,
            Padding = new Thickness(10, 4),
            CornerRadius = new CornerRadius(8),
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        _immersiveButton.Click += (_, _) => RequestImmersive();
        StyleToolbarButton(_immersiveButton);
        ImmersiveButton = _immersiveButton;

        // IMPORT-EXPORT-UI-1 AC2: export entry for the currently loaded book/chapter (hidden until
        // a controller is wired AND a real library book is open).
        _exportButton = new Button
        {
            Content = "导出",
            Name = "ExportButton",
            FontSize = 12,
            Padding = new Thickness(10, 4),
            CornerRadius = new CornerRadius(8),
            IsVisible = false,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        _exportButton.Click += (_, _) => LastExportOperation = OpenExportAsync();
        StyleToolbarButton(_exportButton);

        var toolbar = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("Auto,*,Auto,Auto,Auto,Auto,Auto"),
            Margin = new Thickness(0, 6, 12, 6),
        };
        _hud.Margin = new Thickness(16, 0);
        _libraryTitle.Margin = new Thickness(0);
        _libraryTitle.TextTrimming = TextTrimming.CharacterEllipsis;
        _bookContext.Margin = new Thickness(0);
        _bookContext.TextTrimming = TextTrimming.CharacterEllipsis;
        var contextPanel = new StackPanel
        {
            Spacing = 1,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
            Children = { _libraryTitle, _bookContext },
        };
        toolbar.Children.Add(_hud);
        toolbar.Children.Add(contextPanel);
        toolbar.Children.Add(_previousChapter);
        toolbar.Children.Add(_chapterSelector);
        toolbar.Children.Add(_nextChapter);
        toolbar.Children.Add(_immersiveButton);
        toolbar.Children.Add(_exportButton);
        Grid.SetColumn(contextPanel, 1);
        Grid.SetColumn(_previousChapter, 2);
        Grid.SetColumn(_chapterSelector, 3);
        Grid.SetColumn(_nextChapter, 4);
        Grid.SetColumn(_immersiveButton, 5);
        Grid.SetColumn(_exportButton, 6);
        _previousChapter.Margin = new Thickness(6, 0);
        _chapterSelector.Margin = new Thickness(6, 0);
        _nextChapter.Margin = new Thickness(6, 0);
        _immersiveButton.Margin = new Thickness(6, 0);
        _exportButton.Margin = new Thickness(6, 0);
        var surface = BuildSurface();
        var grid = new Grid
        {
            RowDefinitions = new RowDefinitions("Auto,*"),
            Children = { toolbar, surface, _webtoonScroll, _emptyState },
        };
        Grid.SetRow(surface, 1);
        Grid.SetRow(_webtoonScroll, 1);
        Grid.SetRow(_emptyState, 1);
        _pageGrid = grid;
        _root = new Border { Background = Brushes.Black, Child = grid };
        Content = _root;

        PointerPressed += OnPointerPressed;
        PointerWheelChanged += OnWheel;
        _webtoonScroll.ScrollChanged += OnWebtoonScrollChanged;
    }

    public ReaderViewModel ViewModel { get; }

    public Image PageImage { get; }

    public ScrollViewer WebtoonScroll { get; }

    public TextBlock Hud { get; }

    public TextBlock LibraryTitle { get; }

    public TextBlock EmptyState { get; }

    public Button ImmersiveButton { get; }

    /// <summary>IMPORT-EXPORT-UI-1 AC2: reader export entry (enabled once a book + controller exist).</summary>
    public Button ExportButton => _exportButton;

    public ExportPanel? ExportPanelControl => _exportPanel;

    public Task LastExportOperation { get; private set; } = Task.CompletedTask;

    /// <summary>CHAPTER-SELECTOR-1 AC1: chapter picker in the reader toolbar (hidden for 1 chapter).</summary>
    public ComboBox ChapterSelector { get; }

    /// <summary>CHAPTER-SELECTOR-1 AC1: jump to the previous chapter (hidden for 1 chapter).</summary>
    public Button PreviousChapterButton { get; }

    /// <summary>CHAPTER-SELECTOR-1 AC1: jump to the next chapter (hidden for 1 chapter).</summary>
    public Button NextChapterButton { get; }

    /// <summary>CHAPTER-SELECTOR-1 AC1: "书：… · 章：…" context label.</summary>
    public TextBlock BookContext { get; }

    /// <summary>CHAPTER-SELECTOR-1: chapters of the currently loaded book (empty = unknown/fixture).</summary>
    public IReadOnlyList<ChapterSummary> Chapters => _chapters;

    /// <summary>CHAPTER-SELECTOR-1: chapter id currently rendered (null = fixture/empty).</summary>
    public string? CurrentChapterId => _loadedChapterId;

    /// <summary>CHAPTER-SELECTOR-1: chapter id selected in the picker.</summary>
    public string? SelectedChapterId => (_chapterSelector.SelectedItem as ChapterChoice)?.ChapterId;

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC1: the user picked another chapter; the window re-loads that chapter
    /// (flush current progress → projection resume → render).
    /// </summary>
    public event EventHandler<string>? ChapterSelectionRequested;

    /// <summary>READER-LIBRARY-WIRE-1 AC2: raised by the toolbar button / double-click.</summary>
    public event EventHandler? ImmersiveRequested;

    /// <summary>Real library book currently rendered (null = fixture fallback).</summary>
    public ReaderBookData? LibraryBook => _libraryBook;

    /// <summary>READER-PROGRESS-1: progress persistence seam (null = fixture fallback / not wired).</summary>
    public IReaderProgressSink? ProgressSink { get; set; }

    /// <summary>READER-PROGRESS-1: number of save attempts issued by this page (tests/evidence).</summary>
    public int ProgressSaveAttempts { get; private set; }

    /// <summary>READER-PROGRESS-1: last typed save result (null = nothing was attempted yet).</summary>
    public ReaderProgressSaveResult? LastProgressResult { get; private set; }

    /// <summary>READER-PROGRESS-1: page id of the last successfully persisted position.</summary>
    public string? LastSavedPageId => _lastSavedPageId;

    /// <summary>READER-PROGRESS-1: last successful webtoon offset in logical page pixels.</summary>
    public double LastSavedScrollOffsetY => _lastSavedScrollOffsetY;

    /// <summary>READER-PROGRESS-1: diagnostic summary of the last save payload (evidence/tests).</summary>
    public string? LastProgressPayloadSummary { get; private set; }

    /// <summary>READER-PROGRESS-1: raised after the Core accepted a progress write.</summary>
    public event EventHandler? ProgressSaved;

    public IReadOnlyList<string> TileFiles => _tileFiles;

    public int CachedTileCount => _tileCache.Count;

    public int TileCount => _tileFiles.Count;

    public ITileSource? TileSource => _tileSource;

    public int BoundTileCount => _tileSource?.TileCount ?? _tileFiles.Count;

    public void BindTileSource(ITileSource? source) => _tileSource = source;

    public BitmapInterpolationMode InterpolationMode => RenderOptions.GetBitmapInterpolationMode(_pageImage);

    public void SetViewport(double width, double height, double dpr = 1.0)
    {
        ViewModel.SetViewport(width, height, dpr);
        _pageImage.MaxWidth = width - 2 * ReaderViewModel.PagePadding;
        _pageImage.MaxHeight = height - 2 * ReaderViewModel.PagePadding;
    }

    /// <summary>READER-LIBRARY-WIRE-1 AC1: render a real book from Host/CoreClient data.</summary>
    public void LoadLibrary(ReaderBookData book)
    {
        if (_exportController is not null)
        {
            _exportButton.IsVisible = true;
        }

        _libraryBook = book;
        _renderedPages.Clear();
        _emptyState.IsVisible = false;
        _libraryTitle.Text = book.Summary;
        _loadedChapterId = book.ChapterId;
        SetBookContext(book.BookTitle, book.ChapterTitle);
        _lastSavedPageId = null;
        _lastSavedScrollOffsetY = 0;
        LastProgressResult = null;
        ProgressSaveAttempts = 0;
        _userInteractionSeen = false;
        _readingClock.Restart();

        var initialIndex = Math.Clamp(book.InitialPageIndex, 0, Math.Max(0, book.Pages.Count - 1));
        ViewModel.SetPageCount(book.Pages.Count, initialIndex);
        if (book.IsWebtoon)
        {
            PrepareLibraryWebtoon();
        }
        else
        {
            _webtoonRestoreInProgress = false;
            _webtoonScroll.IsVisible = false;
            _pageImage.IsVisible = true;
            ShowPage(initialIndex);
        }

        SyncChapterSelection();
    }

    /// <summary>READER-LIBRARY-WIRE-1 AC1 empty state (fixture fallback keeps rendering behind it).</summary>
    public void SetLibraryEmpty(string message)
    {
        _exportButton.IsVisible = false;

        _libraryBook = null;
        _emptyState.Text = message;
        _emptyState.IsVisible = true;
        _libraryTitle.Text = "fixture 回退";
        SetBookContext(null, null);
        LoadChapters(Array.Empty<ChapterSummary>());
        _readingClock.Restart();
    }

    // ------------------------------------------------------------------
    // CHAPTER-SELECTOR-1: book/chapter context + chapter list
    // ------------------------------------------------------------------

    /// <summary>CHAPTER-SELECTOR-1 AC1: current book/chapter line ("书：… · 章：…").</summary>
    public void SetBookContext(string? bookTitle, string? chapterTitle)
    {
        var book = string.IsNullOrWhiteSpace(bookTitle) ? "—" : bookTitle.Trim();
        var chapter = string.IsNullOrWhiteSpace(chapterTitle) ? "—" : chapterTitle.Trim();
        _bookContext.Text = $"书：{book} · 章：{chapter}";
    }

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC1: populate the chapter picker. A single chapter hides the selector, so
    /// single-chapter books keep the old toolbar; an empty list also hides it (fixture/unknown).
    /// </summary>
    public void LoadChapters(IReadOnlyList<ChapterSummary> chapters, string? currentChapterId = null)
    {
        _chapters = chapters ?? Array.Empty<ChapterSummary>();
        var choices = _chapters.Select(chapter => new ChapterChoice(chapter.ChapterId, FormatChapterLabel(chapter))).ToList();
        _suppressChapterChange = true;
        try
        {
            _chapterSelector.ItemsSource = choices;
            var target = string.IsNullOrEmpty(currentChapterId)
                ? choices.FirstOrDefault()
                : choices.FirstOrDefault(choice => string.Equals(choice.ChapterId, currentChapterId, StringComparison.Ordinal))
                  ?? choices.FirstOrDefault();
            _chapterSelector.SelectedItem = target;
            _chapterSelector.IsVisible = choices.Count > 1;
        }
        finally
        {
            _suppressChapterChange = false;
        }

        if (!string.IsNullOrEmpty(currentChapterId))
        {
            _loadedChapterId = currentChapterId;
        }

        UpdateChapterNavigation();
    }

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC1: switch to the previous (-1) / next (+1) chapter. Used by the two
    /// toolbar buttons and exposed for tests; the window reloads the chapter through the same
    /// <see cref="ChapterSelectionRequested"/> path as the picker.
    /// </summary>
    public bool SelectAdjacentChapter(int delta)
    {
        if (_chapters.Count < 2 || _loadedChapterId is null)
        {
            return false;
        }

        var index = IndexOfChapter(_loadedChapterId);
        var target = index + delta;
        if (index < 0 || target < 0 || target >= _chapters.Count)
        {
            return false;
        }

        var chapterId = _chapters[target].ChapterId;
        if (string.Equals(chapterId, _loadedChapterId, StringComparison.Ordinal))
        {
            return false;
        }

        ChapterSelectionRequested?.Invoke(this, chapterId);
        return true;
    }

    /// <summary>CHAPTER-SELECTOR-1: index of the loaded chapter inside the current list (-1 = unknown).</summary>
    public int CurrentChapterIndex => IndexOfChapter(_loadedChapterId);

    private int IndexOfChapter(string? chapterId)
    {
        if (string.IsNullOrEmpty(chapterId))
        {
            return -1;
        }

        for (var index = 0; index < _chapters.Count; index++)
        {
            if (string.Equals(_chapters[index].ChapterId, chapterId, StringComparison.Ordinal))
            {
                return index;
            }
        }

        return -1;
    }

    private void UpdateChapterNavigation()
    {
        var multiple = _chapters.Count > 1 && _loadedChapterId is not null;
        var index = IndexOfChapter(_loadedChapterId);
        _previousChapter.IsVisible = multiple;
        _nextChapter.IsVisible = multiple;
        _previousChapter.IsEnabled = multiple && index > 0;
        _nextChapter.IsEnabled = multiple && index >= 0 && index < _chapters.Count - 1;
    }

    /// <summary>CHAPTER-SELECTOR-1: immersive chrome keeps the context but hides the picker.</summary>
    public void HideChapterSelector() => _chapterSelector.IsVisible = false;

    private void SyncChapterSelection()
    {
        if (_chapters.Count == 0 || _loadedChapterId is null)
        {
            return;
        }

        var match = _chapters.FirstOrDefault(chapter =>
            string.Equals(chapter.ChapterId, _loadedChapterId, StringComparison.Ordinal));
        if (match is null)
        {
            return;
        }

        _suppressChapterChange = true;
        try
        {
            _chapterSelector.SelectedItem = _chapterSelector.ItemsSource?
                .OfType<ChapterChoice>()
                .FirstOrDefault(choice => string.Equals(choice.ChapterId, match.ChapterId, StringComparison.Ordinal));
        }
        finally
        {
            _suppressChapterChange = false;
        }

        UpdateChapterNavigation();
    }

    private void OnChapterSelectionChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (_suppressChapterChange || _chapterSelector.SelectedItem is not ChapterChoice choice)
        {
            return;
        }

        if (string.Equals(choice.ChapterId, _loadedChapterId, StringComparison.Ordinal))
        {
            return;
        }

        ChapterSelectionRequested?.Invoke(this, choice.ChapterId);
    }

    private static string FormatChapterLabel(ChapterSummary chapter)
    {
        if (!string.IsNullOrWhiteSpace(chapter.Title))
        {
            // Fixture/Core titles often already read "第 1 章"; avoid a doubled prefix.
            var titleHasNumber = chapter.Title.StartsWith("第", StringComparison.Ordinal);
            return titleHasNumber || string.IsNullOrWhiteSpace(chapter.ChapterNumber)
                ? chapter.Title
                : $"第 {chapter.ChapterNumber} 章 · {chapter.Title}";
        }

        return string.IsNullOrWhiteSpace(chapter.ChapterNumber)
            ? $"第 {chapter.SortOrder} 章"
            : $"第 {chapter.ChapterNumber} 章";
    }

    /// <summary>CHAPTER-SELECTOR-1: one entry of the chapter picker.</summary>
    public sealed record ChapterChoice(string ChapterId, string Label)
    {
        public override string ToString() => Label;
    }

    // ------------------------------------------------------------------
    // READER-PROGRESS-1: navigation + progress persistence
    // ------------------------------------------------------------------

    /// <summary>
    /// Applies one page index (clamped) to the canvas and the view model. Kept synchronous so a
    /// turn is observable immediately; the image decodes asynchronously in the background.
    /// </summary>
    public int GoToPage(int index)
    {
        var book = _libraryBook;
        if (book is null)
        {
            var clampedFixture = Math.Clamp(index, 0, Math.Max(0, _pages.Count - 1));
            ShowPage(clampedFixture);
            return clampedFixture;
        }

        var clamped = Math.Clamp(index, 0, Math.Max(0, book.Pages.Count - 1));
        ViewModel.SetPageCount(book.Pages.Count, clamped);
        if (book.IsWebtoon)
        {
            ScrollWebtoonToPage(clamped);
        }
        else
        {
            _ = ShowLibraryPageAsync(clamped);
        }

        return clamped;
    }

    /// <summary>Applies a turn and awaits its progress save (headless-testable unit of "turn a page").</summary>
    public async Task<int> GoToPageAsync(int index)
    {
        _userInteractionSeen = true;
        var applied = GoToPage(index);
        await SaveProgressAsync().ConfigureAwait(true);
        return applied;
    }

    /// <summary>Turns one page forward/backward (mouse zones, wheel, arrow keys).</summary>
    public Task<int> TurnPageAsync(int delta) => GoToPageAsync(ViewModel.CurrentPageIndex + delta);

    /// <summary>
    /// Queues a save of the current position and drains the single-flight queue. Every call returns
    /// a typed result; a Core/transport failure is recorded and never thrown into the UI.
    /// </summary>
    public async Task<ReaderProgressSaveResult?> SaveProgressAsync()
    {
        QueueProgressSave();
        for (var attempt = 0; attempt < 200; attempt++)
        {
            var loop = _saveLoopTask;
            if (!loop.IsCompleted)
            {
                await loop.ConfigureAwait(true);
                continue;
            }

            if (Volatile.Read(ref _saveLoopRunning) == 0 && _pendingPayload is null)
            {
                break;
            }

            await Task.Yield();
        }

        return LastProgressResult;
    }

    /// <summary>Flushes the current position before leaving the page / closing a window.</summary>
    public Task<ReaderProgressSaveResult?> FlushProgressAsync() => SaveProgressAsync();

    /// <summary>READER-PROGRESS-1: true when the last save was accepted by the Core.</summary>
    public bool HasPersistedProgress => LastProgressResult is { IsSaved: true };

    private void QueueProgressSave()
    {
        if (BuildProgressPayload() is not { } payload)
        {
            return;
        }

        _pendingPayload = payload;
        if (Interlocked.CompareExchange(ref _saveLoopRunning, 1, 0) == 0)
        {
            _saveLoopTask = RunSaveLoopAsync();
        }
    }

    private async Task RunSaveLoopAsync()
    {
        try
        {
            while (true)
            {
                var payload = _pendingPayload;
                _pendingPayload = null;
                if (payload is null)
                {
                    break;
                }

                await SavePayloadAsync(payload).ConfigureAwait(true);
            }
        }
        finally
        {
            Interlocked.Exchange(ref _saveLoopRunning, 0);
            if (_pendingPayload is not null && Interlocked.CompareExchange(ref _saveLoopRunning, 1, 0) == 0)
            {
                _saveLoopTask = RunSaveLoopAsync();
            }
        }
    }

    private async Task<ReaderProgressSaveResult?> SavePayloadAsync(ProgressPayload payload)
    {
        var sink = ProgressSink;
        if (sink is null)
        {
            return null;
        }

        await _saveGate.WaitAsync().ConfigureAwait(true);
        try
        {
            // READER-PROGRESS-1: accumulate elapsed *at send time*. Two queued payloads for the same
            // position (turn + scroll coalescing) must not each carry the whole interval, otherwise
            // the Core would add the same accepted seconds twice.
            var elapsed = _readingClock.Elapsed.TotalSeconds;
            var offset = payload.ScrollOffsetY ?? 0;
            if (string.Equals(payload.PageId, _lastSavedPageId, StringComparison.Ordinal) &&
                Math.Abs(offset - _lastSavedScrollOffsetY) < 0.5 &&
                elapsed < 0.05)
            {
                // Duplicate of the accepted position: nothing new to persist.
                return LastProgressResult;
            }

            ProgressSaveAttempts++;
            LastProgressPayloadSummary = payload.Describe(elapsed);
            var result = await sink
                .SaveReadingProgressAsync(
                    payload.ChapterId,
                    payload.PageId,
                    payload.Mode,
                    payload.ScrollOffsetY,
                    elapsed)
                .ConfigureAwait(true);
            LastProgressResult = result;
            if (result.IsSaved)
            {
                _lastSavedPageId = payload.PageId;
                _lastSavedScrollOffsetY = offset;
                _readingClock.Restart();
                ProgressSaved?.Invoke(this, EventArgs.Empty);
            }

            return result;
        }
        catch (Exception ex) when (ex is IOException or InvalidOperationException or OperationCanceledException or TimeoutException)
        {
            LastProgressResult = ReaderProgressSaveResult.Failed("READER_PROGRESS_UNAVAILABLE");
            return LastProgressResult;
        }
        finally
        {
            _saveGate.Release();
        }
    }

    private ProgressPayload? BuildProgressPayload()
    {
        var book = _libraryBook;
        if (book is null || ProgressSink is null || book.Pages.Count == 0)
        {
            return null;
        }

        var index = Math.Clamp(ViewModel.CurrentPageIndex, 0, book.Pages.Count - 1);
        var page = book.Pages[index];
        double? offset = book.IsWebtoon ? CurrentWebtoonOffsetPixels(index) : null;
        return new ProgressPayload(book.ChapterId, page.PageId, "original", offset);
    }

    /// <summary>READER-PROGRESS-1: webtoon offset in the current page's original pixel coordinates.</summary>
    private double? CurrentWebtoonOffsetPixels(int pageIndex)
    {
        var book = _libraryBook;
        if (book is null || pageIndex < 0 || pageIndex >= book.Pages.Count)
        {
            return null;
        }

        if (_webtoonPageHeights.Count != book.Pages.Count || ViewModel.ViewportWidth <= 0)
        {
            return Math.Max(0, _lastSavedScrollOffsetY);
        }

        var scroll = WebtoonScrollY;
        var top = 0d;
        for (var index = 0; index < _webtoonPageHeights.Count; index++)
        {
            var height = _webtoonPageHeights[index];
            if (index == pageIndex)
            {
                var displayed = Math.Max(1, height);
                var local = Math.Clamp(scroll - top, 0, displayed);
                var pageHeight = Math.Max(1, book.Pages[index].HeightPx);
                return Math.Clamp(local / displayed * pageHeight, 0, pageHeight);
            }

            top += height;
        }

        return 0;
    }

    private void ScrollWebtoonToPage(int pageIndex)
    {
        if (_webtoonPageHeights.Count == 0)
        {
            return;
        }

        var offset = 0d;
        for (var index = 0; index < Math.Min(pageIndex, _webtoonPageHeights.Count); index++)
        {
            offset += _webtoonPageHeights[index];
        }

        _webtoonScroll.Offset = new Vector(_webtoonScroll.Offset.X, offset);
    }

    private void OnWebtoonScrollChanged(object? sender, ScrollChangedEventArgs e) => UpdateWebtoonPosition();

    private void UpdateWebtoonPosition()
    {
        var book = _libraryBook;
        if (book is null || !book.IsWebtoon || book.Pages.Count == 0 || _webtoonPageHeights.Count != book.Pages.Count)
        {
            return;
        }

        // READER-PROGRESS-1: a programmatic restore (resume) must not be treated as a position edit.
        // ScrollChanged fires while the stack is still being laid out, so persisting those frames
        // would immediately overwrite the saved page this open just restored.
        if (_webtoonRestoreInProgress || !_userInteractionSeen)
        {
            return;
        }

        var scroll = WebtoonScrollY;
        var top = 0d;
        var index = book.Pages.Count - 1;
        for (var candidate = 0; candidate < _webtoonPageHeights.Count; candidate++)
        {
            if (scroll < top + Math.Max(1, _webtoonPageHeights[candidate]))
            {
                index = candidate;
                break;
            }

            top += _webtoonPageHeights[candidate];
        }

        var previous = ViewModel.CurrentPageIndex;
        ViewModel.SetPageCount(book.Pages.Count, index);

        // Scroll events are frequent: throttle persisted writes, and only when the position moved.
        var now = _readingClock.Elapsed.TotalMilliseconds;
        if (previous != ViewModel.CurrentPageIndex || now - _lastScrollSaveAtMs > 1000)
        {
            _lastScrollSaveAtMs = now;
            QueueProgressSave();
        }
    }

    /// <summary>READER-PROGRESS-1: restore finished; user-driven scroll may persist from now on.</summary>
    private void CompleteWebtoonRestore()
    {
        _webtoonRestoreInProgress = false;
        _lastScrollSaveAtMs = _readingClock.Elapsed.TotalMilliseconds;
    }

    /// <summary>
    /// READER-PROGRESS-1 test seam: apply a webtoon scroll offset (display pixels) without a
    /// pointer device, then expose the mapped page/offset to assertions.
    /// </summary>
    public int ApplyWebtoonScrollForTest(double offsetPixels)
    {
        _webtoonRestoreInProgress = false;
        _userInteractionSeen = true;
        _webtoonScrollOverride = Math.Max(0, offsetPixels);
        _webtoonScroll.Offset = new Vector(0, Math.Max(0, offsetPixels));
        UpdateWebtoonPosition();
        return ViewModel.CurrentPageIndex;
    }

    /// <summary>READER-PROGRESS-1: current webtoon scroll position in display pixels.</summary>
    private double WebtoonScrollY => _webtoonScrollOverride ?? _webtoonScroll.Offset.Y;

    /// <summary>READER-LIBRARY-WIRE-1 AC2: request the immersive window (button / double-click).</summary>
    /// <summary>
    /// IMPORT-EXPORT-UI-1 AC2: wire the export entry (MainWindow does this once at construction).
    /// Nothing changes for the fixture reader: without a controller the button stays hidden.
    /// </summary>
    public void SetExportController(IHostController controller, IFilePickerGateway? picker = null)
    {
        _exportController = controller;
        _exportPicker = picker;
        _exportPanel = new ExportPanel(controller) { IsVisible = false };
        var pageGrid = _pageGrid;
        if (pageGrid is not null)
        {
            var host = new Grid();
            _root.Child = null;
            host.Children.Add(pageGrid);
            host.Children.Add(_exportPanel);
            _root.Child = host;
        }

        _exportButton.IsVisible = _libraryBook is not null;
    }

    private async Task OpenExportAsync()
    {
        if (_exportPanel is null || _exportController is null)
        {
            return;
        }

        if (_libraryBook is not { } book)
        {
            return;
        }

        _exportPanel.IsVisible = true;
        await _exportPanel.PrepareAsync(book.BookId, book.BookTitle, book.ChapterId, book.ChapterTitle);
    }

    public void RequestImmersive() => ImmersiveRequested?.Invoke(this, EventArgs.Empty);

    /// <summary>Waits until a library page has decoded and been applied (tests/evidence).</summary>
    public Task<int> WaitForPageAsync(int index)
    {
        if (_renderedPages.Contains(index))
        {
            return Task.FromResult(index);
        }

        if (!_pageWaiters.TryGetValue(index, out var waiter))
        {
            waiter = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);
            _pageWaiters[index] = waiter;
        }

        return waiter.Task;
    }

    /// <summary>Loads one page image and applies the current fit mode; returns the measured frame cost.</summary>
    public PageTurnSample ShowPage(int index)
    {
        if (_libraryBook is not null)
        {
            var clamped = Math.Clamp(index, 0, _libraryBook.Pages.Count - 1);
            ViewModel.SetPageCount(_libraryBook.Pages.Count, clamped);
            _ = ShowLibraryPageAsync(clamped);
            return new PageTurnSample(clamped, 0, 0, 0);
        }

        var watch = Stopwatch.StartNew();
        var decodeStart = watch.Elapsed.TotalMilliseconds;
        _currentBitmap?.Dispose();
        _currentBitmap = null;
        if (index >= 0 && index < _pages.Count && File.Exists(_pages[index]))
        {
            _currentBitmap = new Bitmap(_pages[index]);
        }

        _pageImage.Source = _currentBitmap;
        var decode = watch.Elapsed.TotalMilliseconds - decodeStart;
        var layoutStart = watch.Elapsed.TotalMilliseconds;
        ApplyPageLayout(_currentBitmap);
        Dispatcher.UIThread.RunJobs();
        var total = watch.Elapsed.TotalMilliseconds;
        var sample = new PageTurnSample(index, total, decode, total - decode - layoutStart);
        ViewModel.RecordPageTurn(index, sample.TotalMs, sample.DecodeMs, sample.LayoutMs);
        ViewModel.SetPageCount(_pages.Count, index);
        return sample;
    }

    private async Task ShowLibraryPageAsync(int index)
    {
        var book = _libraryBook;
        if (book is null || index < 0 || index >= book.Pages.Count)
        {
            return;
        }

        var watch = Stopwatch.StartNew();
        byte[]? bytes = null;
        try
        {
            if (book.Pages[index].LoadImageAsync is { } loader)
            {
                await _libraryLoadGate.WaitAsync(CancellationToken.None).ConfigureAwait(true);
                try
                {
                    bytes = await loader(CancellationToken.None).ConfigureAwait(true);
                }
                finally
                {
                    _libraryLoadGate.Release();
                }
            }
        }
        catch (Exception ex) when (ex is IOException or InvalidOperationException or UnauthorizedAccessException)
        {
            bytes = null;
        }

        Bitmap? bitmap = null;
        if (bytes is { Length: > 0 })
        {
            try
            {
                using var stream = new MemoryStream(bytes);
                bitmap = new Bitmap(stream);
            }
            catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or NotSupportedException)
            {
                bitmap = null;
            }
        }

        await Dispatcher.UIThread.InvokeAsync(() =>
        {
            _currentBitmap?.Dispose();
            _currentBitmap = bitmap;
            _pageImage.Source = bitmap;
            ApplyPageLayout(bitmap);
            _renderedPages.Add(index);
            ViewModel.RecordPageTurn(index, watch.Elapsed.TotalMilliseconds, 0, 0);
            if (_pageWaiters.Remove(index, out var waiter))
            {
                waiter.TrySetResult(index);
            }
        });
    }

    private void ApplyPageLayout(Bitmap? bitmap)
    {
        var size = bitmap is null
            ? (ViewModel.ViewportWidth - 2 * ReaderViewModel.PagePadding, ViewModel.ViewportHeight - 2 * ReaderViewModel.PagePadding, 1.0)
            : ViewModel.DisplaySize(bitmap.PixelSize.Width, bitmap.PixelSize.Height);
        _pageImage.Stretch = ViewModel.FitMode == ReaderFitMode.OneToOne ? Stretch.None : Stretch.Uniform;
        _pageImage.Width = size.Item1;
        _pageImage.Height = size.Item2;
        _pageImage.Measure(new Size(ViewModel.ViewportWidth, ViewModel.ViewportHeight));
        _pageImage.Arrange(new Rect(0, 0, size.Item1, size.Item2));
    }

    public void PrepareWebtoon()
    {
        ViewModel.SetFitMode(ReaderFitMode.Webtoon);
        _pageImage.IsVisible = false;
        _webtoonScroll.IsVisible = true;
        ViewModel.ScrollWebtoon(0, out _);
        var items = new List<Control>();
        var cacheLimit = Math.Max(3, ViewModel.CachedTileCount);
        var totalTiles = _tileSource?.TileCount ?? _tileFiles.Count;
        for (var index = 0; index < totalTiles; index++)
        {
            Bitmap? bitmap = null;
            if (index < cacheLimit)
            {
                bitmap = LoadTileBitmap(index);
            }

            var image = new Image
            {
                Source = bitmap,
                Stretch = Stretch.Fill,
                Height = Math.Max(1, ViewModel.ViewportWidth * (ReaderViewModel.WebtoonTileHeight / ReaderViewModel.WebtoonStripWidth)),
            };
            RenderOptions.SetBitmapInterpolationMode(image, BitmapInterpolationMode.None);
            items.Add(image);
        }

        _webtoonItems.ItemsSource = items;
        _webtoonItems.Measure(new Size(ViewModel.ViewportWidth, ViewModel.ViewportHeight));
        _webtoonItems.Arrange(new Rect(0, 0, ViewModel.ViewportWidth, ViewModel.ViewportHeight));
    }

    /// <summary>READER-LIBRARY-WIRE-1 AC4: real webtoon book rendered as one vertical page stack.</summary>
    public void PrepareLibraryWebtoon()
    {
        _webtoonRestoreInProgress = true;
        _ = PrepareLibraryWebtoonAsync();
    }

    private async Task PrepareLibraryWebtoonAsync()
    {
        _webtoonRestoreInProgress = true;
        var book = _libraryBook;
        if (book is null)
        {
            PrepareWebtoon();
            return;
        }

        ViewModel.SetFitMode(ReaderFitMode.Webtoon);
        _pageImage.IsVisible = false;
        _webtoonScroll.IsVisible = true;
        _webtoonImages.Clear();
        _webtoonPageHeights.Clear();
        var images = new List<Image>();
        for (var index = 0; index < book.Pages.Count; index++)
        {
            var height = LibraryPageHeight(book.Pages[index]);
            var image = new Image
            {
                Name = $"WebtoonPage_{index}",
                Stretch = Stretch.Fill,
                Height = height,
            };
            RenderOptions.SetBitmapInterpolationMode(_pageImage, BitmapInterpolationMode.None);
            RenderOptions.SetBitmapInterpolationMode(image, BitmapInterpolationMode.None);
            images.Add(image);
            _webtoonImages.Add(image);
            _webtoonPageHeights.Add(height);
        }

        _webtoonItems.ItemsSource = images;
        _webtoonItems.Measure(new Size(ViewModel.ViewportWidth, ViewModel.ViewportHeight));
        _webtoonItems.Arrange(new Rect(0, 0, ViewModel.ViewportWidth, ViewModel.ViewportHeight));

        // READER-PROGRESS-1 AC1: restore the persisted webtoon position (page + in-page offset).
        var initialPage = Math.Clamp(book.InitialPageIndex, 0, Math.Max(0, book.Pages.Count - 1));
        ViewModel.SetPageCount(book.Pages.Count, initialPage);
        ScrollWebtoonToPage(initialPage);
        if (book.InitialScrollOffsetY > 0)
        {
            var pageHeight = Math.Max(1, _webtoonPageHeights[initialPage]);
            var localPixels = Math.Clamp(
                book.InitialScrollOffsetY / Math.Max(1, book.Pages[initialPage].HeightPx) * pageHeight,
                0,
                pageHeight - 1);
            _webtoonScroll.Offset = new Vector(0, _webtoonScroll.Offset.Y + localPixels);
        }

        // The resource pipe is request/response: load page images one at a time.
        for (var index = 0; index < book.Pages.Count; index++)
        {
            await LoadWebtoonPageAsync(images[index], index).ConfigureAwait(true);
        }

        CompleteWebtoonRestore();
    }

    private double LibraryPageHeight(ReaderPageData page)
    {
        var aspect = page.WidthPx > 0 ? (double)page.HeightPx / page.WidthPx : 1.0;
        return Math.Max(1, Math.Max(1, ViewModel.ViewportWidth) * aspect);
    }

    private async Task LoadWebtoonPageAsync(Image image, int index)
    {
        var book = _libraryBook;
        if (book is null || index < 0 || index >= book.Pages.Count)
        {
            return;
        }

        byte[]? bytes = null;
        try
        {
            if (book.Pages[index].LoadImageAsync is { } loader)
            {
                await _libraryLoadGate.WaitAsync(CancellationToken.None).ConfigureAwait(true);
                try
                {
                    bytes = await loader(CancellationToken.None).ConfigureAwait(true);
                }
                finally
                {
                    _libraryLoadGate.Release();
                }
            }
        }
        catch (Exception ex) when (ex is IOException or InvalidOperationException or UnauthorizedAccessException)
        {
            bytes = null;
        }

        if (bytes is not { Length: > 0 })
        {
            return;
        }

        Bitmap? bitmap;
        try
        {
            using var stream = new MemoryStream(bytes);
            bitmap = new Bitmap(stream);
        }
        catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or NotSupportedException)
        {
            bitmap = null;
        }

        await Dispatcher.UIThread.InvokeAsync(() =>
        {
            image.Source = bitmap;
            _renderedPages.Add(index);
            if (_pageWaiters.Remove(index, out var waiter))
            {
                waiter.TrySetResult(index);
            }
        });
    }

    private Bitmap? LoadTileBitmap(int index)
    {
        if (_tileSource is not null)
        {
            var bytes = _tileSource.ReadTile(index);
            if (bytes is null)
            {
                return null;
            }

            try
            {
                return new Bitmap(new MemoryStream(bytes));
            }
            catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or NotSupportedException)
            {
                return null;
            }
        }

        return GetTile(index);
    }

    public Bitmap? GetTile(int index)
    {
        if (_tileCache.TryGetValue(index, out var cached))
        {
            return cached;
        }

        if (index < 0 || index >= _tileFiles.Count)
        {
            return null;
        }

        var bitmap = new Bitmap(_tileFiles[index]);
        _tileCache[index] = bitmap;
        return bitmap;
    }

    public void SetHudVisible(bool visible)
    {
        ViewModel.HudVisible = visible;
        _hud.IsVisible = visible;
        _immersiveButton.IsVisible = visible;
        _libraryTitle.IsVisible = visible;
    }

    public void CycleFitMode()
    {
        var next = ViewModel.FitMode switch
        {
            ReaderFitMode.FitPage => ReaderFitMode.FitWidth,
            ReaderFitMode.FitWidth => ReaderFitMode.OneToOne,
            ReaderFitMode.OneToOne => ReaderFitMode.Webtoon,
            _ => ReaderFitMode.FitPage,
        };
        ViewModel.SetFitMode(next);
        if (next == ReaderFitMode.Webtoon)
        {
            if (_libraryBook is { IsWebtoon: true })
            {
                PrepareLibraryWebtoon();
            }
            else
            {
                PrepareWebtoon();
            }
        }
        else
        {
            _webtoonScroll.IsVisible = false;
            _pageImage.IsVisible = true;
        }
    }

    private Control BuildSurface()
    {
        var stack = new StackPanel
        {
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            Children = { _pageImage },
        };
        return stack;
    }

    private void OnPointerPressed(object? sender, PointerPressedEventArgs e)
    {
        // CHAPTER-SELECTOR-1: only presses on the reading surface (page image / webtoon stack) may
        // turn pages or toggle immersive; clicks on the toolbar (chapter picker), buttons or the
        // scrollbar must never page-turn.
        if (!IsReadingSurfaceSource(e.Source))
        {
            return;
        }

        if (e.ClickCount >= 2)
        {
            RequestImmersive();
            e.Handled = true;
            return;
        }

        _userInteractionSeen = true;
        var position = e.GetPosition(this);
        if (position.X < Bounds.Width * 0.25)
        {
            _ = TurnPageAsync(-1);
        }
        else if (position.X > Bounds.Width * 0.75)
        {
            _ = TurnPageAsync(1);
        }
    }

    /// <summary>CHAPTER-SELECTOR-1: true when the press originated on the reading surface.</summary>
    private bool IsReadingSurfaceSource(object? source)
    {
        if (source is not Visual visual)
        {
            return false;
        }

        // Scrollbar drags/thumbs live inside the webtoon scroll viewer but are not page turns.
        if (visual is ScrollBar || visual.FindAncestorOfType<ScrollBar>() is not null)
        {
            return false;
        }

        for (Visual? current = visual; current is not null; current = current.GetVisualParent())
        {
            if (ReferenceEquals(current, _webtoonScroll) || ReferenceEquals(current, _pageImage))
            {
                return true;
            }
        }

        return false;
    }

    /// <summary>CHAPTER-SELECTOR-1: make toolbar buttons readable on the black reader chrome.</summary>
    private static void StyleToolbarButton(Button button)
    {
        button.Background = LegacyChrome.Brush("CardBg");
        button.Foreground = LegacyChrome.Brush("TextPrimary");
        button.BorderBrush = LegacyChrome.Brush("CardBorder");
        button.BorderThickness = new Thickness(1);
    }

    /// <summary>CHAPTER-SELECTOR-1 test seam: would a press from this source page-turn?</summary>
    public bool IsPageTurnSourceForTest(object? source) => IsReadingSurfaceSource(source);

    private void OnWheel(object? sender, PointerWheelEventArgs e)
    {
        _userInteractionSeen = true;
        if (e.Delta.Y > 0)
        {
            _ = TurnPageAsync(-1);
        }
        else if (e.Delta.Y < 0)
        {
            _ = TurnPageAsync(1);
        }

        e.Handled = true;
    }

    /// <summary>READER-PROGRESS-1: one immutable progress write (captured on the UI thread).</summary>
    private sealed record ProgressPayload(
        string ChapterId,
        string PageId,
        string Mode,
        double? ScrollOffsetY)
    {
        public string Describe(double elapsedSeconds) =>
            $"chapter={ChapterId} page={PageId} mode={Mode} " +
            $"offset={(ScrollOffsetY is { } offset ? offset.ToString("F1") : "omitted")} " +
            $"elapsed={elapsedSeconds:F3}s";
    }
}

/// <summary>
/// AC2 immersive reader window: borderless black chrome, Esc/F11 exits, H hides HUD, F cycles fit,
/// arrow keys page. READER-LIBRARY-WIRE-1 AC2: created from the reader page (button/double-click)
/// for both a real library book and the fixture fallback. F11-HOTKEY-1: also opened/closed by the
/// application-level F11 hotkey.
/// </summary>
public sealed class ReaderWindow : Window
{
    public ReaderWindow(ReaderViewModel viewModel, IReadOnlyList<string> pages, string? tileDirectory = null)
        : this(viewModel, new ReaderPage(viewModel, pages, tileDirectory))
    {
    }

    public ReaderWindow(ReaderViewModel viewModel, ReaderBookData book, IReaderProgressSink? progressSink = null)
        : this(viewModel, CreateLibraryPage(viewModel, book, progressSink))
    {
    }

    public ReaderWindow(ReaderViewModel viewModel, ReaderPage page)
    {
        var effectivePage = page;
        if (effectivePage.LibraryBook is null && effectivePage.PageImage.Source is null && effectivePage.ViewModel.PageCount <= 1)
        {
            // No fixture and no library book: keep the window usable but empty.
        }

        Title = "阅读器";
        SystemDecorations = SystemDecorations.None;
        WindowState = WindowState.FullScreen;
        Background = Brushes.Black;
        Page = effectivePage;
        Content = effectivePage;
        KeyDown += OnKeyDown;

        // READER-PROGRESS-1 AC1: closing the immersive window is one of the save triggers.
        Closed += (_, _) => _ = effectivePage.FlushProgressAsync();
        Opened += (_, _) =>
        {
            if (effectivePage.LibraryBook is { IsWebtoon: true })
            {
                effectivePage.PrepareLibraryWebtoon();
            }
            else
            {
                effectivePage.GoToPage(viewModel.CurrentPageIndex);
            }
        };
    }

    public ReaderPage Page { get; }

    /// <summary>Number of Esc presses that requested a close (headless-testable).</summary>
    public int EscapeCount { get; private set; }

    /// <summary>F11-HOTKEY-1: number of F11 presses that closed the immersive session.</summary>
    public int F11Count { get; private set; }

    /// <summary>Handles one keystroke; returns true when the key was consumed.</summary>
    public bool TryHandleKey(Key key)
    {
        switch (key)
        {
            case Key.Escape:
                EscapeCount++;
                _ = Page.FlushProgressAsync();
                Close();
                return true;
            case Key.F11:
                // F11-HOTKEY-1: inside the immersive window F11 is the toggle-off half of the
                // application hotkey (the window is already fullscreen); closing returns to the
                // main window page (restored by MainWindow when F11 started elsewhere).
                F11Count++;
                _ = Page.FlushProgressAsync();
                Close();
                return true;
            case Key.H:
                Page.SetHudVisible(!Page.ViewModel.HudVisible);
                return true;
            case Key.F:
                Page.CycleFitMode();
                return true;
            case Key.Right:
            case Key.Down:
                _ = Page.TurnPageAsync(1);
                return true;
            case Key.Left:
            case Key.Up:
                _ = Page.TurnPageAsync(-1);
                return true;
            default:
                return false;
        }
    }

    private static ReaderPage CreateLibraryPage(
        ReaderViewModel viewModel,
        ReaderBookData book,
        IReaderProgressSink? progressSink)
    {
        var page = new ReaderPage(viewModel, Array.Empty<string>()) { ProgressSink = progressSink };
        page.LoadLibrary(book);
        return page;
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        if (TryHandleKey(e.Key))
        {
            e.Handled = true;
        }
    }
}

internal static class ReaderFixtureLocator
{
    public static string? Root
    {
        get
        {
            var configured = Environment.GetEnvironmentVariable("NEWMANGA_S4_FIXTURES");
            if (!string.IsNullOrWhiteSpace(configured) && Directory.Exists(configured))
            {
                return configured;
            }

            var fallback = @"G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1/fixtures";
            return Directory.Exists(fallback) ? fallback : null;
        }
    }

    public static IReadOnlyList<string> TypographyPaths() => new[]
    {
        Path.Combine(Root ?? string.Empty, "typography", "vertical-1200x1800.png"),
        Path.Combine(Root ?? string.Empty, "typography", "horizontal-1800x1200.png"),
    };

    public static string? TileDirectory => Root is null ? null : @"G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/spike/avalonia/fixtures/strip-4000x60000/tiles";
}

