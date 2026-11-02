using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Data;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3 Studio · Page mode composition (SCREEN_SPECS §3):
/// FilmStrip 56⇄200 | CanvasViewport + PageSurface + RegionOverlay (+ HUDRing) | Inspector 40⇄320,
/// with the TrackStrip + pipeline band underneath (28⇄240) and the leave modal as an overlay.
/// The view is built once and keeps working off the same <see cref="StudioPageViewModel"/> instance,
/// so Page ⇄ Batch never rebuilds it (AC2).
/// </summary>
public sealed class StudioPageWorkspace : Grid
{
    private readonly StudioPageViewModel _viewModel;
    private readonly StudioFilmStrip _filmStrip;
    private readonly StudioInspectorPanel _inspector;
    private readonly StudioTrackStrip _trackStrip;
    private readonly StudioPipelineBand _pipelineBand;
    private readonly StudioLeaveModal _leaveModal;
    private readonly List<(StudioSurfaceMode Mode, Button Button)> _surfaceButtons = new();
    private StudioCanvasViewport _canvas = null!;
    private TextBlock _statusText = null!;
    private TextBlock _zoomText = null!;
    private Border _hostBanner = null!;
    private Border _errorBanner = null!;
    private Border _partialBanner = null!;
    private TextBlock _hostBannerText = null!;
    private TextBlock _errorText = null!;
    private TextBlock _partialText = null!;
    private Button _retryButton = null!;
    private Grid _emptyOverlay = null!;
    private Grid _loadingOverlay = null!;
    private TextBlock _emptyTitle = null!;
    private TextBlock _emptyDetail = null!;
    private Button _emptyAction = null!;
    private bool _responsiveApplied;

    public StudioPageWorkspace(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;
        // Path bindings in this subtree resolve against the Page view model (one page, one context).
        DataContext = viewModel;
        RowDefinitions = new RowDefinitions("*,Auto");

        // ---------------------------------------------------------------- main row
        var mainGrid = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,*,Auto") };
        _filmStrip = new StudioFilmStrip(viewModel);
        var canvasColumn = BuildCanvasColumn();
        _inspector = new StudioInspectorPanel(viewModel);

        Grid.SetColumn(_filmStrip, 0);
        Grid.SetColumn(canvasColumn, 1);
        Grid.SetColumn(_inspector, 2);
        mainGrid.Children.Add(_filmStrip);
        mainGrid.Children.Add(canvasColumn);
        mainGrid.Children.Add(_inspector);

        // ---------------------------------------------------------------- bottom bands
        var bottom = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto") };
        var trackHost = StudioUi.Box("studio-sunken-band");
        trackHost.Height = 28;
        _trackStrip = new StudioTrackStrip(viewModel);
        trackHost.Child = _trackStrip;
        _pipelineBand = new StudioPipelineBand(viewModel);
        Grid.SetRow(trackHost, 0);
        Grid.SetRow(_pipelineBand, 1);
        bottom.Children.Add(trackHost);
        bottom.Children.Add(_pipelineBand);

        Grid.SetRow(mainGrid, 0);
        Grid.SetRow(bottom, 1);
        Children.Add(mainGrid);
        Children.Add(bottom);

        // ---------------------------------------------------------------- overlays
        SizeChanged += (_, _) => ApplyResponsive();
        _leaveModal = new StudioLeaveModal(viewModel);
        Grid.SetRowSpan(_leaveModal, 2);
        Children.Add(_leaveModal);
    }

    // ---------------------------------------------------------------- exposed control tree

    public StudioFilmStrip FilmStrip => _filmStrip;

    public StudioCanvasViewport Canvas => _canvas;

    public StudioInspectorPanel Inspector => _inspector;

    public StudioTrackStrip TrackStrip => _trackStrip;

    public StudioPipelineBand PipelineBand => _pipelineBand;

    public StudioLeaveModal LeaveModal => _leaveModal;

    public IReadOnlyList<Button> SurfaceButtons => _surfaceButtons.Select(pair => pair.Button).ToList();

    public TextBlock ZoomTextBlock => _zoomText;

    public TextBlock StatusTextBlock => _statusText;

    public Border HostBanner => _hostBanner;

    public Border ErrorBanner => _errorBanner;

    public Border PartialBanner => _partialBanner;

    public Grid EmptyOverlay => _emptyOverlay;

    /// <summary>P2-6: DS Skeleton loading placeholder (static, no shimmer).</summary>
    public Grid LoadingOverlay => _loadingOverlay;

    public Button RetryButton => _retryButton;

    public Button EmptyActionButton => _emptyAction;

    public Button ZoomInButton { get; private set; } = null!;

    public Button ZoomOutButton { get; private set; } = null!;

    public Button FitButton { get; private set; } = null!;

    public Button PreviousPageButton { get; private set; } = null!;

    public Button NextPageButton { get; private set; } = null!;

    // ---------------------------------------------------------------- canvas column

    private Control BuildCanvasColumn()
    {
        var column = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto,*,Auto") };

        // toolbar (28px): surface switch + zoom + page navigation + region count
        var toolbar = StudioUi.Box("panel");
        toolbar.Height = 32;
        toolbar.Padding = new Thickness(8, 0);
        var toolbarRow = StudioUi.Row(8);
        toolbarRow.Children.Add(BuildSurfaceSwitch());
        toolbarRow.Children.Add(StudioUi.Box("studio-divider") is var divider ? WithWidth(divider, 1, 20) : new Border());

        ZoomOutButton = StudioUi.Button("−", "icon ghost", () => _viewModel.ZoomOut());
        ToolTip.SetTip(ZoomOutButton, "缩小（滚轮亦可）");
        _zoomText = new TextBlock { Classes = { "data", "muted" }, Width = 42, TextAlignment = TextAlignment.Center };
        _zoomText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.ZoomText)));
        ZoomInButton = StudioUi.Button("＋", "icon ghost", () => _viewModel.ZoomIn());
        ToolTip.SetTip(ZoomInButton, "放大（滚轮亦可）");
        FitButton = StudioUi.Button("适应", "sm", () => _viewModel.FitWindow());
        ToolTip.SetTip(FitButton, "适应窗口（适应后居中）");
        toolbarRow.Children.Add(ZoomOutButton);
        toolbarRow.Children.Add(_zoomText);
        toolbarRow.Children.Add(ZoomInButton);
        toolbarRow.Children.Add(FitButton);

        PreviousPageButton = StudioUi.Button("[", "icon ghost", () => _ = _viewModel.MovePageAsync(-1));
        ToolTip.SetTip(PreviousPageButton, "上一页（[）");
        NextPageButton = StudioUi.Button("]", "icon ghost", () => _ = _viewModel.MovePageAsync(1));
        ToolTip.SetTip(NextPageButton, "下一页（]）");
        toolbarRow.Children.Add(PreviousPageButton);
        toolbarRow.Children.Add(NextPageButton);

        var pageCounter = new TextBlock { Classes = { "data", "muted" } };
        pageCounter.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.PageCounterText)));
        toolbarRow.Children.Add(pageCounter);

        var regionChip = StudioUi.Box(StudioUi.Text("区", "meta"), "studio-chip");
        regionChip.Child = StudioUi.Text(string.Empty, "meta");
        ((TextBlock)regionChip.Child).Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.RegionCountText)));
        toolbarRow.Children.Add(regionChip);

        toolbar.Child = toolbarRow;

        // banners (in place, never toast-only)
        var banners = StudioUi.Column(4);
        banners.Margin = new Thickness(8, 4);

        _hostBannerText = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _hostBannerText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.HostBannerText)));
        _hostBanner = StudioUi.Box(_hostBannerText, "raised");
        StudioUi.TrackVisible(_hostBanner, _viewModel, () => _viewModel.HostBannerVisible);
        banners.Children.Add(_hostBanner);

        _errorText = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _errorText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.ErrorText)));
        var errorRow = StudioUi.Column(4);
        errorRow.Children.Add(_errorText);
        _retryButton = StudioUi.Button("重新读取", "sm", () => _ = _viewModel.LoadAsync());
        errorRow.Children.Add(_retryButton);
        _errorBanner = StudioUi.Box(errorRow, "studio-banner-error");
        // I1 fix: one in-place error block only — the host banner already explains a not-ready
        // host, so the error banner must not repeat it (state-error.png showed both).
        StudioUi.TrackVisible(_errorBanner, _viewModel, () => _viewModel.HasErrorText && !_viewModel.HostBannerVisible);
        banners.Children.Add(_errorBanner);

        _partialText = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _partialText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.PartialReason)));
        var partialRow = StudioUi.Row(8);
        partialRow.Children.Add(_partialText);
        var partialRetry = StudioUi.Button("重试", "sm", () => _ = _viewModel.RefreshPageAsync());
        partialRow.Children.Add(partialRetry);
        _partialBanner = StudioUi.Box(partialRow, "studio-banner-partial");
        StudioUi.TrackVisible(_partialBanner, _viewModel, () => _viewModel.HasPartialReason);
        banners.Children.Add(_partialBanner);

        // canvas viewport + empty/error overlay in the same cell
        _canvas = new StudioCanvasViewport(_viewModel);
        var canvasHost = new Grid();
        canvasHost.Children.Add(_canvas);
        BuildEmptyOverlay();
        canvasHost.Children.Add(_emptyOverlay);
        BuildLoadingOverlay();
        canvasHost.Children.Add(_loadingOverlay);

        // status line (24px): page counter · regions · selection · transient action result
        var statusBorder = StudioUi.Box("studio-sunken-band");
        statusBorder.Height = 24;
        statusBorder.Padding = new Thickness(8, 0);
        var statusRow = StudioUi.Row(12);
        var pageInfo = new TextBlock { Classes = { "data", "muted" } };
        pageInfo.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.BreadcrumbText)));
        statusRow.Children.Add(pageInfo);
        var sizeInfo = new TextBlock { Classes = { "data", "muted" } };
        sizeInfo.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.PageSizeText)));
        statusRow.Children.Add(sizeInfo);
        var selectionInfo = new TextBlock { Classes = { "meta", "muted" } };
        selectionInfo.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.SelectedRegionDetail)));
        statusRow.Children.Add(selectionInfo);
        var detailsInfo = new TextBlock { Classes = { "meta", "muted" } };
        detailsInfo.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.RegionDetailsStatus)));
        statusRow.Children.Add(detailsInfo);
        statusRow.Children.Add(new Panel { Width = 1 });
        _statusText = new TextBlock { Classes = { "meta" } };
        _statusText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioPageViewModel.StatusText)));
        statusRow.Children.Add(_statusText);
        statusBorder.Child = statusRow;

        Grid.SetRow(toolbar, 0);
        Grid.SetRow(banners, 1);
        Grid.SetRow(canvasHost, 2);
        Grid.SetRow(statusBorder, 3);
        column.Children.Add(toolbar);
        column.Children.Add(banners);
        column.Children.Add(canvasHost);
        column.Children.Add(statusBorder);

        // keyboard: the canvas column owns the Studio shortcuts and lets the shell see unhandled keys
        column.KeyDown += (_, args) => StudioKeyboard.Handle(_viewModel, this, args);
        return column;
    }

    private Control BuildSurfaceSwitch()
    {
        var segmented = StudioUi.Box("raised");
        var row = StudioUi.Row(0);
        foreach (var (mode, label) in new[]
                 {
                     (StudioSurfaceMode.Page, "页面"),
                     (StudioSurfaceMode.Final, "成品"),
                     (StudioSurfaceMode.Split, "分屏"),
                 })
        {
            var captured = mode;
            var button = StudioUi.Button(label, "studio-segment", () => _viewModel.SurfaceMode = captured);
            StudioUi.TrackClass(button, "active", _viewModel, () => _viewModel.SurfaceMode == captured);
            ToolTip.SetTip(button, mode switch
            {
                StudioSurfaceMode.Page => "页面：原图 + Region 覆盖（已接入）",
                StudioSurfaceMode.Final => "成品：成品预览读取未接入（NOT_WIRED）",
                _ => "分屏：原图 / 成品对照（成品侧 NOT_WIRED）",
            });
            _surfaceButtons.Add((mode, button));
            row.Children.Add(button);
        }

        segmented.Child = row;
        return segmented;
    }

    private void BuildEmptyOverlay()
    {
        _emptyOverlay = new Grid();
        var card = StudioUi.Box("raised");
        card.Width = 420;
        card.HorizontalAlignment = HorizontalAlignment.Center;
        card.VerticalAlignment = VerticalAlignment.Center;
        var column = StudioUi.Column(8);
        _emptyTitle = new TextBlock { Classes = { "title" } };
        _emptyDetail = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _emptyAction = StudioUi.Button("重新读取", "sm primary", () => _ = _viewModel.LoadAsync());
        column.Children.Add(_emptyTitle);
        column.Children.Add(_emptyDetail);
        column.Children.Add(_emptyAction);
        card.Child = column;
        _emptyOverlay.Children.Add(card);
        StudioUi.TrackVisible(
            _emptyOverlay,
            _viewModel,
            () => _viewModel.IsEmpty || (_viewModel.HasError && !_viewModel.HostBannerVisible));
        _viewModel.PropertyChanged += (_, _) => RefreshEmptyOverlay();
        RefreshEmptyOverlay();
    }

    /// <summary>
    /// Responsive rules (FUSION_SPEC §6): ≥1600 full layout; 1280–1599 strip fixed at 56 and inspector
    /// defaults collapsed; &lt;1280 the strip narrows to 40 and the inspector body becomes an overlay so
    /// the canvas is never squeezed to zero.
    /// </summary>
    private void ApplyResponsive()
    {
        var width = Bounds.Width;
        if (width <= 0)
        {
            return;
        }

        var compact = width < StudioMetrics.BreakpointCompact;
        _inspector.SetOverlayMode(compact);
        _filmStrip.Width = compact ? 40 : _viewModel.FilmStripWidth;
        _inspector.Width = compact ? 40 : _viewModel.InspectorWidth;

        if (_responsiveApplied)
        {
            return;
        }

        _responsiveApplied = true;
        if (width < StudioMetrics.BreakpointFull)
        {
            _viewModel.FilmStripExpanded = false;
        }

        if (width < StudioMetrics.BreakpointCompact + 120)
        {
            _viewModel.InspectorExpanded = false;
        }
    }

    private void RefreshEmptyOverlay()
    {
        if (_viewModel.HasError)
        {
            _emptyTitle!.Text = "页面读取失败";
            _emptyDetail!.Text = _viewModel.ErrorText ?? "Host 或 Core 未返回数据";
            _emptyAction!.Content = "重试";
        }
        else if (_viewModel.IsEmpty)
        {
            _emptyTitle!.Text = "本章还没有页面";
            _emptyDetail!.Text = "在 Library 空间导入页面后回到 Studio；此处不会伪造任何页面或 Region 数据。";
            _emptyAction!.Content = "重新读取";
        }
        else
        {
            _emptyTitle!.Text = string.Empty;
            _emptyDetail!.Text = string.Empty;
        }
    }

    private static Border WithWidth(Border border, double width, double height)
    {
        border.Width = width;
        border.Height = height;
        return border;
    }
    /// <summary>P2-6: loading skeleton built from the DS Skeleton control.</summary>
    private void BuildLoadingOverlay()
    {
        _loadingOverlay = new Grid { IsHitTestVisible = false };
        var column = StudioUi.Column(8);
        column.Margin = new Thickness(24);
        column.Children.Add(new NewManga.DesignSystem.Controls.Skeleton
        {
            Variant = NewManga.DesignSystem.Controls.SkeletonVariant.Panel,
            Width = 220,
            HorizontalAlignment = HorizontalAlignment.Left,
        });
        column.Children.Add(new NewManga.DesignSystem.Controls.Skeleton
        {
            Variant = NewManga.DesignSystem.Controls.SkeletonVariant.Row,
            Width = 320,
            HorizontalAlignment = HorizontalAlignment.Left,
        });
        column.Children.Add(new NewManga.DesignSystem.Controls.Skeleton
        {
            Variant = NewManga.DesignSystem.Controls.SkeletonVariant.BookCard,
            Width = 180,
            HorizontalAlignment = HorizontalAlignment.Left,
        });
        _loadingOverlay.Children.Add(column);
        StudioUi.TrackVisible(_loadingOverlay, _viewModel, () => _viewModel.IsLoading);
    }
}