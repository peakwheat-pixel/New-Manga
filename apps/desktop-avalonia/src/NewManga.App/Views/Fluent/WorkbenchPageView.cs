using Avalonia.Controls;
using Avalonia.Automation;
using Avalonia.Controls.Primitives;
using Avalonia.Layout;
using Avalonia.Media.Imaging;
using NewManga.App.Controls;
using NewManga.App.ViewModels.Fluent;
using NewManga.CoreClient;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;
using FluentTabStrip = NewManga.DesignSystem.Controls.TabStrip;

namespace NewManga.App.Views.Fluent;

public enum WorkbenchViewTab
{
    Page,
    Batch,
    Console,
}

/// <summary>Fluent Workbench page backed exclusively by Host projections and the seven Draft ports.</summary>
public sealed class WorkbenchPageView : UserControl
{
    private readonly WorkbenchViewModel _viewModel;
    private readonly Action _backToShelf;
    private readonly StackPanel _root;
    private readonly FluentTabStrip _tabStrip;
    private readonly ContentControl _mainHost;
    private readonly Control _pageLayout;
    private readonly StackPanel _pageStrip;
    private readonly Canvas _canvas;
    private readonly StackPanel _regionList;
    private readonly StackPanel _inspector;
    private readonly Border _statusHost;
    private readonly Border _loadingHost;
    private readonly Border _dialogScrim;
    private readonly FluentDialog _leaveDialog;
    private string? _pendingPageId;
    private TextBox? _draftInput;
    private WorkbenchViewTab _activeTab;

    public WorkbenchPageView(WorkbenchViewModel viewModel, Action backToShelf)
    {
        _viewModel = viewModel;
        _backToShelf = backToShelf;
        _root = FluentUi.Stack("fluent-page-layout");
        _tabStrip = new FluentTabStrip();
        AutomationProperties.SetName(_tabStrip, "工作台视图");
        _mainHost = new ContentControl();
        _pageStrip = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        _canvas = new Canvas { Classes = { "fluent-canvas" }, ClipToBounds = true };
        _regionList = FluentUi.Stack("fluent-chapter-list");
        _inspector = FluentUi.Stack("fluent-page-layout");
        _statusHost = new Border { IsVisible = false };
        _loadingHost = new Border { IsVisible = false };
        _leaveDialog = new FluentDialog { IsOpen = false };
        _dialogScrim = new Border { Classes = { "fluent-modal-scrim" }, IsVisible = false };
        _pageLayout = BuildPageLayout();
        _root.Children.Add(BuildToolbar());
        _root.Children.Add(BuildTabs());
        _root.Children.Add(_statusHost);
        _root.Children.Add(_loadingHost);
        _root.Children.Add(BuildMainLayout());
        _root.Children.Add(BuildLeaveOverlay());
        Content = _root;
        _viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName == nameof(WorkbenchViewModel.IsBatch) && _activeTab != WorkbenchViewTab.Console)
            {
                _activeTab = _viewModel.IsBatch ? WorkbenchViewTab.Batch : WorkbenchViewTab.Page;
            }
            if (args.PropertyName != nameof(WorkbenchViewModel.DraftText)) Render();
        };
        _canvas.SizeChanged += (_, _) => RenderRegions();
        Render();
    }

    public WorkbenchViewModel ViewModel => _viewModel;
    public Canvas RegionCanvas => _canvas;
    public FluentTabStrip ViewTabs => _tabStrip;
    public WorkbenchViewTab ActiveTab => _activeTab;
    public Control? CurrentViewContent => _mainHost.Content as Control;
    public event Action<WorkbenchViewTab>? TabChanged;

    public void SelectConsoleTab() => SelectTab(WorkbenchViewTab.Console);

    public void SelectPageTab() => SelectTab(WorkbenchViewTab.Page);

    public void SelectTab(WorkbenchViewTab tab)
    {
        _activeTab = tab;
        _viewModel.IsBatch = tab == WorkbenchViewTab.Batch;
        TabChanged?.Invoke(tab);
        Render();
    }

    public bool MovePage(int direction)
    {
        if (direction == 0 || _viewModel.SelectedPage is not { } selected) return false;
        var pages = _viewModel.Pages.ToList();
        var currentIndex = pages.FindIndex(page => page.PageId == selected.PageId);
        if (currentIndex < 0) return false;
        var targetIndex = Math.Clamp(currentIndex + Math.Sign(direction), 0, pages.Count - 1);
        if (targetIndex == currentIndex) return false;
        RequestPage(pages[targetIndex].PageId);
        return true;
    }

    private Control BuildToolbar()
    {
        var toolbar = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        toolbar.Children.Add(FluentUi.Text("工作台", "fluent-page-title"));
        toolbar.Children.Add(FluentUi.Button("返回书架", "fluent-secondary", _backToShelf, "返回书架"));
        toolbar.Children.Add(FluentUi.Button("刷新", "fluent-icon", () => _ = _viewModel.LoadAsync(_viewModel.SelectedPage is null ? null : GetChapterId()), "刷新工作台"));
        return toolbar;
    }

    private Control BuildTabs()
    {
        AddTab("页面", WorkbenchViewTab.Page);
        AddTab("批量", WorkbenchViewTab.Batch);
        AddTab("控制台", WorkbenchViewTab.Console);
        return _tabStrip;

        void AddTab(string label, WorkbenchViewTab tab)
        {
            var button = FluentUi.Button(label, "fluent-secondary", () => SelectTab(tab), $"切换到{label}视图");
            button.Classes.Set("selected", tab == _activeTab);
            _tabStrip.Children.Add(button);
        }
    }

    private Control BuildMainLayout()
    {
        return _mainHost;
    }

    private Control BuildPageLayout()
    {
        var main = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,*,Auto") };

        var leftCard = new SurfaceCard { Classes = { "fluent-detail-pane" } };
        var left = FluentUi.Stack("fluent-page-layout");
        left.Children.Add(FluentUi.Text("FilmStrip", "fluent-status-text"));
        left.Children.Add(_pageStrip);
        left.Children.Add(FluentUi.Text("Regions", "fluent-status-text"));
        left.Children.Add(_regionList);
        leftCard.Child = left;
        leftCard.Classes.Add("fluent-filmstrip-pane");
        main.Children.Add(leftCard);

        var center = FluentUi.Stack("fluent-page-layout");
        var runBar = new RunProjectionBar
        {
            Child = FluentUi.Text("Run 投影：当前没有活动任务投影。", "fluent-status-text"),
        };
        center.Children.Add(runBar);
        var canvasSurface = new SurfaceCard
        {
            Child = new ScrollViewer
            {
                Content = _canvas,
                HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
            },
        };
        canvasSurface.Classes.Add("fluent-workbench-surface");
        center.Children.Add(canvasSurface);
        Grid.SetColumn(center, 1);
        main.Children.Add(center);

        var inspector = new SurfaceCard { Child = _inspector };
        inspector.Classes.Add("fluent-inspector-pane");
        Grid.SetColumn(inspector, 2);
        main.Children.Add(inspector);
        return main;
    }

    private Control BuildBatchLayout()
    {
        var content = FluentUi.Stack("fluent-page-layout");
        content.Children.Add(FluentUi.Text("批量处理", "fluent-page-title"));
        content.Children.Add(FluentUi.Text("当前没有可显示的批量状态。", "fluent-status-text"));
        return new BatchMatrix { Content = content };
    }

    private Control BuildConsoleLayout()
    {
        var content = FluentUi.Stack("fluent-page-layout");
        content.Children.Add(FluentUi.Text("Run 控制台", "fluent-page-title"));
        content.Children.Add(new RunProjectionBar
        {
            Child = FluentUi.Text("当前没有运行中的任务", "fluent-status-text"),
        });
        content.Children.Add(FluentUi.Text("Run 状态与错误由 Host 投影提供；当前端口尚未接入。", "fluent-subtle-text"));
        if (_viewModel.State == FluentPageState.Error && !string.IsNullOrWhiteSpace(_viewModel.Error))
        {
            content.Children.Add(FluentUi.Button("查看工作台错误", "fluent-secondary",
                () => SelectTab(WorkbenchViewTab.Page), "切换到工作台页面查看错误"));
        }
        return content;
    }

    private Control BuildLeaveOverlay()
    {
        var overlay = new Grid { RowDefinitions = new RowDefinitions("*,Auto,*") };
        overlay.Children.Add(_dialogScrim);
        Grid.SetRowSpan(_dialogScrim, 3);
        var panel = FluentUi.Stack("fluent-page-layout");
        panel.Children.Add(FluentUi.Text("未决草稿", "fluent-page-title"));
        panel.Children.Add(FluentUi.Text("切换页面前，请选择保存、丢弃或取消。失败时会留在当前页面。"));
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Children.Add(FluentUi.Button("保存", "fluent-primary", () => _ = SaveThenNavigateAsync(), "保存草稿后切换"));
        actions.Children.Add(FluentUi.Button("丢弃", "fluent-danger", () => _ = DiscardThenNavigateAsync(), "丢弃草稿后切换"));
        actions.Children.Add(FluentUi.Button("取消", "fluent-secondary", CloseLeaveDialog, "取消切换"));
        panel.Children.Add(actions);
        _leaveDialog.Child = panel;
        overlay.Children.Add(_leaveDialog);
        Grid.SetRow(_leaveDialog, 1);
        return overlay;
    }

    private void Render()
    {
        for (var index = 0; index < _tabStrip.Children.Count; index++)
        {
            _tabStrip.Children[index].Classes.Set("selected", index == (int)_activeTab);
        }
        _mainHost.Content = _activeTab switch
        {
            WorkbenchViewTab.Batch => BuildBatchLayout(),
            WorkbenchViewTab.Console => BuildConsoleLayout(),
            _ => _pageLayout,
        };

        _pageStrip.Children.Clear();
        foreach (var page in _viewModel.Pages)
        {
            var button = FluentUi.Button($"第 {page.SortOrder + 1} 页", "fluent-secondary",
                () => RequestPage(page.PageId), $"打开第 {page.SortOrder + 1} 页");
            button.Classes.Set("selected", _viewModel.SelectedPage?.PageId == page.PageId);
            _pageStrip.Children.Add(button);
        }

        _regionList.Children.Clear();
        foreach (var region in _viewModel.Regions)
        {
            var button = FluentUi.Button($"{region.RegionType} · 修订 {region.RevisionNo}", "fluent-book-row",
                () => _ = _viewModel.SelectRegionAsync(region), $"选择区域 {region.RegionId}");
            button.Classes.Set("selected", _viewModel.SelectedRegion?.RegionId == region.RegionId);
            _regionList.Children.Add(button);
        }

        _statusHost.IsVisible = _viewModel.State is FluentPageState.Error or FluentPageState.Conflict or FluentPageState.ReadOnly or FluentPageState.Partial;
        if (_viewModel.State == FluentPageState.Error)
        {
            _statusHost.Child = FluentUi.Banner(StatusKind.Failed, "工作台错误", _viewModel.Error,
                "重试", () => _ = _viewModel.LoadAsync(GetChapterId()));
        }
        else if (_viewModel.State == FluentPageState.Conflict)
        {
            _statusHost.Child = FluentUi.Banner(StatusKind.Stale, "并发冲突", _viewModel.Error,
                "重读草稿", () => _ = _viewModel.ReloadDraftAsync());
        }
        else if (_viewModel.State == FluentPageState.ReadOnly)
        {
            _statusHost.Child = FluentUi.Banner(StatusKind.Locked, "只读模式", _viewModel.Error,
                null, null);
        }
        else if (_viewModel.State == FluentPageState.Partial)
        {
            _statusHost.Child = FluentUi.Banner(StatusKind.Blocked, "部分可用", _viewModel.Error,
                null, null);
        }

        _loadingHost.IsVisible = _viewModel.State == FluentPageState.Loading;
        if (_viewModel.State == FluentPageState.Loading)
        {
            var loading = FluentUi.Stack("fluent-page-layout");
            loading.Children.Add(new Skeleton { Variant = SkeletonVariant.Panel });
            loading.Children.Add(FluentUi.Text("读取中…", "fluent-status-text"));
            _loadingHost.Child = FluentUi.Card(loading);
        }
        else
        {
            _loadingHost.Child = null;
        }

        _inspector.Children.Clear();
        _inspector.Children.Add(FluentUi.Text("检查器", "fluent-page-title"));
        if (_viewModel.SelectedRegion is null)
        {
            _inspector.Children.Add(FluentUi.Empty("未选择区域", "在画布或列表中选择一个 Region。", null, null));
        }
        else
        {
            _inspector.Children.Add(FluentUi.Text($"区域类型：{_viewModel.SelectedRegion.RegionType}", "fluent-status-text"));
            _inspector.Children.Add(FluentUi.Text($"修订：{_viewModel.SelectedRegion.RevisionNo} · 来源：{_viewModel.SelectedRegion.Origin}", "fluent-subtle-text"));
            _inspector.Children.Add(FluentUi.Text("译文草稿", "fluent-status-text"));
            _draftInput = FluentUi.Input("译文草稿", "输入译文文本", _viewModel.DraftText);
            _draftInput.TextChanged += (_, _) => _viewModel.DraftText = _draftInput.Text ?? string.Empty;
            _draftInput.IsEnabled = !_viewModel.IsReadOnly && _viewModel.CurrentDraft is not null;
            if (_viewModel.CurrentDraft is null)
            {
                ToolTip.SetTip(_draftInput, "新建 Draft 需要 pageBindingVersion；当前 Host 页面投影未提供此字段，操作已 fail-closed。");
            }

            _inspector.Children.Add(_draftInput);
            _inspector.Children.Add(FluentUi.Button("开启草稿", "fluent-secondary",
                () => _ = _viewModel.OpenDraftAsync(), "开启草稿"));
            _inspector.Children.Add(FluentUi.Button("写入恢复日志", "fluent-primary",
                () => _ = SaveDraftAsync(), "保存草稿"));
            _inspector.Children.Add(FluentUi.Button("准备并应用 Candidate", "fluent-secondary",
                () => _ = _viewModel.ApplyCandidateAsync(), "准备并应用 Candidate"));
            _inspector.Children.Add(FluentUi.Button("丢弃草稿", "fluent-danger",
                () => _ = _viewModel.DiscardDraftAsync(), "丢弃草稿"));
            _inspector.Children.Add(FluentUi.Text($"Draft Error Category：{_viewModel.ErrorCategory}", "fluent-subtle-text"));
            _inspector.Children.Add(FluentUi.Text($"错误码映射：{string.Join(" · ", _viewModel.ErrorCodes)}", "fluent-subtle-text"));
            if (_viewModel.IsReadOnly)
            {
                foreach (var button in _inspector.Children.OfType<Button>()) button.IsEnabled = false;
            }
        }

        RenderRegions();
    }

    private void RenderRegions()
    {
        _canvas.Children.Clear();
        if (_viewModel.PageImageBytes is { Length: > 0 } bytes && _viewModel.Projection?.PageSize is { } pageSize)
        {
            try
            {
                using var stream = new MemoryStream(bytes, writable: false);
                var bitmap = new Bitmap(stream);
                _canvas.Width = pageSize.Width;
                _canvas.Height = pageSize.Height;
                var image = new Image { Source = bitmap, Width = pageSize.Width, Height = pageSize.Height, Stretch = Avalonia.Media.Stretch.Fill };
                _canvas.Children.Add(image);
                foreach (var region in _viewModel.Regions)
                {
                    if (region.Geometry is not { } geometry) continue;
                    var box = new RegionBox
                    {
                        Tag = region,
                        Width = geometry.Width * pageSize.Width,
                        Height = geometry.Height * pageSize.Height,
                        Child = FluentUi.Text($"{region.RegionType} · {region.RevisionNo}", "fluent-subtle-text"),
                        IsHitTestVisible = true,
                    };
                    box.Classes.Set("selected", _viewModel.SelectedRegion?.RegionId == region.RegionId);
                    box.PointerPressed += (_, _) => _ = _viewModel.SelectRegionAsync(region);
                    Canvas.SetLeft(box, geometry.X * pageSize.Width);
                    Canvas.SetTop(box, geometry.Y * pageSize.Height);
                    _canvas.Children.Add(box);
                }
            }
            catch (Exception ex)
            {
                _canvas.Children.Clear();
                _canvas.Children.Add(FluentUi.Text($"页面预览暂不可用（{ex.GetType().Name}）", "fluent-status-text"));
            }
        }
        else if (_viewModel.State == FluentPageState.Empty)
        {
            _canvas.Children.Add(FluentUi.Empty("未选章节", "从书架选择章节以读取页面。", "返回书架", _backToShelf));
        }
    }

    private string? GetChapterId() => _viewModel.SelectedPage is null ? null : _chapterId;

    private string? _chapterId;

    public async Task LoadAsync(string? chapterId, CancellationToken cancellationToken = default)
    {
        _chapterId = chapterId;
        await _viewModel.LoadAsync(chapterId, cancellationToken);
    }

    private void RequestPage(string pageId)
    {
        if (_viewModel.HasUnsavedDraft)
        {
            _pendingPageId = pageId;
            _leaveDialog.IsOpen = true;
            _dialogScrim.IsVisible = true;
            return;
        }

        _ = _viewModel.SelectPageAsync(pageId);
    }

    private async Task SaveDraftAsync()
    {
        if (_draftInput is not null) _viewModel.DraftText = _draftInput.Text ?? string.Empty;
        await _viewModel.SaveDraftAsync();
    }

    private async Task SaveThenNavigateAsync()
    {
        if (await _viewModel.SaveDraftAsync()) await NavigatePendingPageAsync();
    }

    private async Task DiscardThenNavigateAsync()
    {
        await _viewModel.DiscardDraftAsync();
        await NavigatePendingPageAsync();
    }

    private async Task NavigatePendingPageAsync()
    {
        CloseLeaveDialog();
        if (_pendingPageId is { } pageId)
        {
            _pendingPageId = null;
            await _viewModel.SelectPageAsync(pageId);
        }
    }

    private void CloseLeaveDialog()
    {
        _leaveDialog.IsOpen = false;
        _dialogScrim.IsVisible = false;
        _pendingPageId = null;
    }
}
