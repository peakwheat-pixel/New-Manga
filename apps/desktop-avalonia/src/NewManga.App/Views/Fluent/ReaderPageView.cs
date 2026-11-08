using Avalonia;
using Avalonia.Animation;
using Avalonia.Controls;
using Avalonia.Markup.Xaml.MarkupExtensions;
using Avalonia.Controls.Primitives;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Automation;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Controls;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;
using DsReaderPage = NewManga.DesignSystem.Controls.ReaderPage;

namespace NewManga.App.Views.Fluent;

/// <summary>Fluent Reader overlay. Page ids and progress stay Host-owned.</summary>
public sealed class ReaderPageView : UserControl
{
    /// <summary>I-10：无操作后顶部/底部条隐藏的空闲窗口（设计 07:23「2s 淡出」）。</summary>
    public static readonly TimeSpan ToolBarAutoHideInterval = TimeSpan.FromSeconds(2);

    /// <summary>
    /// I-10：顶部/底部条的淡出过渡时长。取 02-motion §2.1「浮层退出 160ms ease-in」冻结参数；
    /// reduce 下不挂该过渡（07:23「直接切换」）。
    /// </summary>
    public static readonly TimeSpan ToolBarFadeDuration = TimeSpan.FromMilliseconds(160);

    private readonly ReaderViewModel _viewModel;
    private readonly Action _back;
    private readonly Action<bool> _setFullScreen;
    private readonly Grid _root;
    private readonly StackPanel _topBar;
    private readonly StackPanel _bottomBar;
    private readonly DsReaderPage _pageSurface;
    private readonly Image _pageImage;
    private readonly Image _pageImageSecondary;
    private readonly StackPanel _pagedPanel;
    private readonly ScrollViewer _webtoonScroll;
    private readonly StackPanel _webtoonPanel;
    private readonly Image _webtoonImagePrimary;
    private readonly Image _webtoonImageSecondary;
    private readonly Border _messageHost;
    private readonly Border _sourceWarningHost;
    private readonly Border _sideRailHost;
    private readonly Button _sideRailRestore;
    private readonly PageThumbStrip _thumbStrip;
    private readonly ReaderProgressBar _progress;
    private readonly DispatcherTimer _autoHideTimer;
    // 字段初始化器必须在任何 lambda 捕获之前完成（_webtoonScroll.ScrollChanged 会用到这里）。
    private readonly DispatcherTimer _scrollProgressTimer = new() { Interval = TimeSpan.FromMilliseconds(600) };
    private readonly FluentVisibilityMotion _topMotion;
    private readonly FluentVisibilityMotion _bottomMotion;
    private IFluentMotionClock _motionClock = FluentRenderClock.Instance;
    private double _decorativePageTurnMs;
    private Action? _cancelPageTurnDecor;
    private TimeSpan? _idleDeadline;
    internal TimeSpan? IdleDeadline => _idleDeadline;
    internal bool IdleTimerEnabled => _autoHideTimer.IsEnabled;
    private byte[]? _imageBytes;
    private Bitmap? _bitmap;
    private byte[]? _imageBytesSecondary;
    private Bitmap? _bitmapSecondary;

    public ReaderPageView(ReaderViewModel viewModel, Action back, Action<bool> setFullScreen)
    {
        _viewModel = viewModel;
        _back = back;
        _setFullScreen = setFullScreen;
        Focusable = true;
        // AC-5 A3：ReaderPageView 自身是 Tab 落点（Focusable=true），必须有语义名而不是类型名。
        AutomationProperties.SetName(this, "阅读器");
        _pageImage = new Image { Stretch = Stretch.Uniform, HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center };
        // AC-3（格 2）：双页模式的第二页（仅双页模式下可见；单页模式不显示、不加载）。
        _pageImageSecondary = new Image { Stretch = Stretch.Uniform, IsVisible = false,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center };
        AutomationProperties.SetName(_pageImageSecondary, "后一页");
        _pagedPanel = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
        };
        _pagedPanel.Children.Add(_pageImage);
        _pagedPanel.Children.Add(_pageImageSecondary);
        _pageSurface = new DsReaderPage { Child = _pagedPanel, Classes = { "fluent-reader-page" } };
        _pageSurface.Focusable = true;
        AutomationProperties.SetName(_pageSurface, "当前漫画页面");
        // AC-3：webtoon 连续页滚动面（Layout=webtoon_vertical / IsWebtoon）；
        // 滚动偏移写回 SaveReadingProgressAsync 的 scrollOffsetY（逻辑页像素）。
        _webtoonImagePrimary = new Image { Stretch = Stretch.Uniform, HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center };
        _webtoonImageSecondary = new Image { Stretch = Stretch.Uniform, HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center };
        AutomationProperties.SetName(_webtoonImagePrimary, "连续滚动当前页");
        AutomationProperties.SetName(_webtoonImageSecondary, "连续滚动后一页");
        _webtoonPanel = new StackPanel { Orientation = Orientation.Vertical };
        _webtoonPanel.Children.Add(_webtoonImagePrimary);
        _webtoonPanel.Children.Add(_webtoonImageSecondary);
        _webtoonScroll = new ScrollViewer
        {
            Content = _webtoonPanel,
            IsVisible = false,
            HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
        };
        AutomationProperties.SetName(_webtoonScroll, "连续页滚动区");
        _webtoonScroll.ScrollChanged += (_, _) =>
        {
            if (!_viewModel.IsWebtoon)
            {
                return;
            }

            // AC-3：只把真实用户滚动写回进度（布局 clamp 造成的 0 偏移同样合法，不伪造）。
            _viewModel.SetScrollOffset(_webtoonScroll.Offset.Y);
            // 停止滚动 600ms 后写回（同一保存路径；不新增 Host 端口）。
            _scrollProgressTimer.Stop();
            _scrollProgressTimer.Start();
        };
        _messageHost = new Border { IsVisible = false };
        _sourceWarningHost = new Border { IsVisible = false };
        _sideRailHost = BuildSideRail();
        _sideRailRestore = FluentUi.Button("显示浮动工具条", "fluent-secondary", () => _viewModel.ToggleSideRail(), "显示浮动工具条");
        _sideRailRestore.VerticalAlignment = VerticalAlignment.Center;
        _sideRailRestore.HorizontalAlignment = HorizontalAlignment.Right;
        _sideRailRestore.IsVisible = false;
        _thumbStrip = new PageThumbStrip();
        _progress = new ReaderProgressBar { Minimum = 0, Maximum = 100 };
        _topBar = BuildTopBar();
        _bottomBar = BuildBottomBar();
        // A vertical StackPanel measures the image at infinite height: fit-page then overflows the
        // viewport and puts both the progress bar and bottom-edge particles off screen.
        _root = new Grid { RowDefinitions = new RowDefinitions("Auto,Auto,*,Auto") };
        _root[!Grid.RowSpacingProperty] = new DynamicResourceExtension("Nm.Space.3");
        var readingArea = BuildReadingArea();
        _root.Children.Add(_topBar);
        _root.Children.Add(_sourceWarningHost); Grid.SetRow(_sourceWarningHost, 1);
        _root.Children.Add(readingArea); Grid.SetRow(readingArea, 2);
        _root.Children.Add(_bottomBar); Grid.SetRow(_bottomBar, 3);
        Content = _root;
        _topMotion = new FluentVisibilityMotion(_topBar);
        _bottomMotion = new FluentVisibilityMotion(_bottomBar);
        _autoHideTimer = new DispatcherTimer { Interval = ToolBarAutoHideInterval };
        _autoHideTimer.Tick += (_, _) => CheckIdleDeadline();
        // AC-3：滚动模式下停止滚动 600ms 后写回进度（scrollOffsetY=当前滚动偏移）。
        _scrollProgressTimer.Tick += (_, _) =>
        {
            _scrollProgressTimer.Stop();
            _ = SaveScrollProgressAsync();
        };
        _viewModel.PropertyChanged += OnViewModelPropertyChanged;
        KeyDown += OnKeyDown;
        _pageSurface.DoubleTapped += (_, _) => _viewModel.ToggleDoublePage();
        _pageSurface.PointerWheelChanged += (_, args) =>
        {
            _ = args.Delta.Y >= 0 ? _viewModel.PreviousAsync() : _viewModel.NextAsync();
            args.Handled = true;
        };
        AddHandler(PointerMovedEvent, (_, _) => NotifyInteraction(), RoutingStrategies.Tunnel, handledEventsToo: true);
        AddHandler(PointerPressedEvent, OnPointerPressed, RoutingStrategies.Tunnel, handledEventsToo: true);
        // Releasing a center tap resets time but must not undo its visibility toggle.
        AddHandler(PointerReleasedEvent, (_, _) => NotifyInteraction(reveal: false), RoutingStrategies.Tunnel, handledEventsToo: true);
        AddHandler(PointerWheelChangedEvent, (_, _) => NotifyInteraction(), RoutingStrategies.Tunnel, handledEventsToo: true);
        AddHandler(KeyDownEvent, (_, _) => NotifyInteraction(), RoutingStrategies.Tunnel, handledEventsToo: true);
        AttachedToVisualTree += (_, _) => ResetIdleDeadline();
        DetachedFromVisualTree += (_, _) =>
        {
            _autoHideTimer.Stop(); _idleDeadline = null;
            _scrollProgressTimer.Stop();
            _cancelPageTurnDecor?.Invoke(); _cancelPageTurnDecor = null;
        };
        ApplyToolBarsMotionMode();
        ApplyToolBarsVisibility();
        ApplySideRailVisibility();
        Render();
    }

    public ReaderViewModel ViewModel => _viewModel;
    public Image PageImage => _pageImage;
    public Image PageImageSecondary => _pageImageSecondary;
    public DsReaderPage PageSurface => _pageSurface;
    /// <summary>AC-3：webtoon 连续页滚动面（滚动偏移 → SaveReadingProgressAsync 的 scrollOffsetY）。</summary>
    public ScrollViewer WebtoonScroll => _webtoonScroll;
    public StackPanel WebtoonPanel => _webtoonPanel;
    /// <summary>R3-002 证据入口：webtoon 第二页 Image（末页/单页/失败时必须无 Source 且不可见）。</summary>
    public Image WebtoonSecondaryImage => _webtoonImageSecondary;
    public Image WebtoonPrimaryImage => _webtoonImagePrimary;
    public Border SideRail => _sideRailHost;
    public StackPanel TopBar => _topBar;
    public StackPanel BottomBar => _bottomBar;
    public TimeSpan AutoHideTimerInterval => _autoHideTimer.Interval;
    /// <summary>AC-3 证据：滚动进度写回的去抖窗口（停止滚动后 600ms 保存）。</summary>
    public TimeSpan ScrollProgressSaveDelay => _scrollProgressTimer.Interval;

    /// <summary>AC-3：立即冲刷滚动进度（测试/离开页面时用同一保存路径，不另建实现）。</summary>
    internal Task<bool> FlushScrollProgressAsync()
    {
        _scrollProgressTimer.Stop();
        return SaveScrollProgressAsync();
    }

    private Task<bool> SaveScrollProgressAsync() => _viewModel.SaveScrollProgressAsync();

    public async Task LoadAsync(string? bookId, string? chapterId, CancellationToken cancellationToken = default)
    {
        await _viewModel.LoadAsync(bookId, chapterId, cancellationToken);
        Focus();
        WakeToolBars();
    }

    /// <summary>I-10：由 PointerPressed 驱动的点击判定；命中页面中部（垂直 25%–75%）时切换工具条显隐。</summary>
    public bool HandleReadingAreaTap(Point relative)
    {
        var height = _pageSurface.Bounds.Height;
        if (height <= 0)
        {
            return false; // no layout yet; a tap cannot be judged against the center band.
        }

        var ratio = relative.Y / height;
        if (ratio is < 0.25 or > 0.75)
        {
            return false;
        }

        _viewModel.ToggleToolBars();
        return true;
    }

    private void OnPointerPressed(object? sender, PointerPressedEventArgs args)
    {
        // Decide the center toggle before any wake-up can change the pre-press visibility.
        // Image descendants count as page hits; overlaid controls retain ordinary wake-up behavior.
        var centerTap = args.Source is Visual source &&
            (ReferenceEquals(source, _pageSurface) || source.GetVisualAncestors().Contains(_pageSurface)) &&
            HandleReadingAreaTap(args.GetPosition(_pageSurface));
        NotifyInteraction(reveal: !centerTap);
    }

    private StackPanel BuildTopBar()
    {
        var bar = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        bar.Classes.Add("fluent-reader-bar");
        bar.Children.Add(FluentUi.Button("返回", "fluent-secondary", _back, "返回书架"));
        bar.Children.Add(FluentUi.Text(string.Empty, "fluent-reader-title"));
        bar.Children.Add(FluentUi.Button("单页 / 双页", "fluent-secondary", _viewModel.ToggleDoublePage, "切换单页或双页"));
        bar.Children.Add(FluentUi.Button("反向翻页", "fluent-secondary", () => _viewModel.ReverseDirection = !_viewModel.ReverseDirection, "切换阅读方向"));
        bar.Children.Add(FluentUi.Button("全屏", "fluent-icon", ToggleFullScreen, "切换全屏阅读"));
        return bar;
    }

    private Control BuildReadingArea()
    {
        var grid = new Grid();
        grid.Children.Add(_pageSurface);
        grid.Children.Add(_webtoonScroll);
        grid.Children.Add(_messageHost);
        grid.Children.Add(_sideRailHost);
        grid.Children.Add(_sideRailRestore);
        return grid;
    }

    /// <summary>
    /// I-10：右侧浮动工具条（07:24 缩放/方向/全屏，Elevation.2 + Fluent.Md）；常显、可显式隐藏（07:62），
    /// 不参与 2s 自动隐藏；隐藏后右缘保留恢复入口。
    /// </summary>
    private Border BuildSideRail()
    {
        var rail = FluentUi.Stack("fluent-reader-siderail", Orientation.Vertical);
        rail.Children.Add(FluentUi.Button("放大", "fluent-icon", () => _viewModel.ZoomBy(0.1), "放大页面"));
        rail.Children.Add(FluentUi.Button("缩小", "fluent-icon", () => _viewModel.ZoomBy(-0.1), "缩小页面"));
        rail.Children.Add(FluentUi.Button("适合页面", "fluent-icon", _viewModel.ResetZoom, "重置缩放"));
        rail.Children.Add(FluentUi.Button("反向翻页", "fluent-icon", () => _viewModel.ReverseDirection = !_viewModel.ReverseDirection, "切换阅读方向"));
        rail.Children.Add(FluentUi.Button("全屏", "fluent-icon", ToggleFullScreen, "切换全屏阅读"));
        rail.Children.Add(FluentUi.Button("隐藏浮动工具条", "fluent-secondary", () => _viewModel.ToggleSideRail(), "隐藏浮动工具条"));
        var host = new Border { Child = rail, VerticalAlignment = VerticalAlignment.Center };
        host[!Border.CornerRadiusProperty] = new DynamicResourceExtension("Nm.Corner.Fluent.Md");
        host[!Border.BoxShadowProperty] = new DynamicResourceExtension("Nm.Elevation.2");
        // impl-r1 R1-007 / design 03 §4: the floating rail must keep a hairline border so high contrast
        // (which zeroes Elevation) still renders the required 1px border instead of a borderless surface.
        host[!Border.BorderThicknessProperty] = new DynamicResourceExtension("Nm.Border.Hairline");
        host[!Border.BorderBrushProperty] = new DynamicResourceExtension("Nm.Color.Line.Subtle");
        return host;
    }

    private StackPanel BuildBottomBar()
    {
        var bottom = FluentUi.Stack("fluent-page-layout");
        var actions = FluentUi.Stack("fluent-page-toolbar", Orientation.Horizontal);
        actions.Classes.Add("fluent-reader-bar");
        actions.Children.Add(FluentUi.Button("上一页", "fluent-secondary", () => _ = _viewModel.PreviousAsync(), "上一页"));
        actions.Children.Add(_progress);
        actions.Children.Add(FluentUi.Text(string.Empty, "fluent-status-text"));
        actions.Children.Add(FluentUi.Button("下一页", "fluent-primary", () => _ = _viewModel.NextAsync(), "下一页"));
        actions.Children.Add(FluentUi.Button("缩小", "fluent-icon", () => _viewModel.ZoomBy(-0.1), "缩小页面"));
        actions.Children.Add(FluentUi.Button("放大", "fluent-icon", () => _viewModel.ZoomBy(0.1), "放大页面"));
        actions.Children.Add(FluentUi.Button("适合页面", "fluent-secondary", _viewModel.ResetZoom, "重置缩放"));
        bottom.Children.Add(actions);
        bottom.Children.Add(_thumbStrip);
        return bottom;
    }

    private void OnViewModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs args)
    {
        if (args.PropertyName is nameof(ReaderViewModel.AreToolBarsVisible)) ApplyToolBarsVisibility();
        if (args.PropertyName is nameof(ReaderViewModel.IsSideRailVisible)) ApplySideRailVisibility();
        if (args.PropertyName is nameof(ReaderViewModel.AreToolBarsReducedMotion)) ApplyToolBarsMotionMode();
        if (args.PropertyName is nameof(ReaderViewModel.IsFullScreen)) WakeToolBars();
        // IN-1.2（02 §2.3）：任何翻页路径都会推进 PageIndex，翻页粒子统一由此触发一次。
        if (args.PropertyName is nameof(ReaderViewModel.PageIndex)) PlayPageTurnDecor();
        Render();
    }

    /// <summary>
    /// IN-1.2：翻页装饰粒子（400ms，一次）。reduce / auto(系统关) / category=off 下完全不创建粒子层
    /// （02 §3 判据①）；启用时粒子层在页面前景边缘稀疏可见，不拦截命中，像素断言限制覆盖面积。
    /// </summary>
    private void PlayPageTurnDecor()
    {
        _cancelPageTurnDecor?.Invoke();
        _cancelPageTurnDecor = null;
        if (_decorativePageTurnMs <= 0) return;
        if (_pageSurface.Parent is Grid area) _cancelPageTurnDecor = FluentPageTurnDecor.Play(_motionClock, _decorativePageTurnMs, area);
    }

    /// <summary>IN-1.2 证据入口：阅读区是否当前存在粒子层（reduce 下恒为 null）。</summary>
    internal Border? DecorativeParticleLayer =>
        (_pageSurface.Parent as Grid)?.Children.OfType<Border>()
            .FirstOrDefault(border => border.Classes.Contains("fluent-decorative-particles"));

    private void WakeToolBars()
    {
        NotifyInteraction();
    }

    internal void NotifyInteraction(bool reveal = true)
    {
        if (reveal) _viewModel.PokeToolBars();
        ResetIdleDeadline();
    }

    private void ResetIdleDeadline()
    {
        if (_viewModel.AreToolBarsVisible && TopLevel.GetTopLevel(this) is not null)
        {
            _idleDeadline = _motionClock.Now + ToolBarAutoHideInterval;
            _autoHideTimer.Stop();
            _autoHideTimer.Start();
        }
    }

    internal void CheckIdleDeadline()
    {
        if (_idleDeadline is { } deadline && _motionClock.Now >= deadline && TopLevel.GetTopLevel(this) is not null)
            _viewModel.HideToolBarsAfterIdle();
    }

    private void ApplyToolBarsVisibility()
    {
        _topMotion.SetVisible(_viewModel.AreToolBarsVisible);
        _bottomMotion.SetVisible(_viewModel.AreToolBarsVisible);
        if (_viewModel.AreToolBarsVisible)
        {
            ResetIdleDeadline();
        }
        else
        {
            _autoHideTimer.Stop();
            _idleDeadline = null;
        }
    }

    private void ApplySideRailVisibility()
    {
        _sideRailHost.IsVisible = _viewModel.IsSideRailVisible;
        _sideRailRestore.IsVisible = !_viewModel.IsSideRailVisible;
    }

    private void ApplyToolBarsMotionMode()
    {
        var duration = _viewModel.AreToolBarsReducedMotion ? 0 : ToolBarFadeDuration.TotalMilliseconds;
        _topMotion.Configure(0, duration, _motionClock);
        _bottomMotion.Configure(0, duration, _motionClock);
    }

    internal void ConfigureMotion(MotionTimingProfile timings, IFluentMotionClock clock)
    {
        _motionClock = clock;
        _decorativePageTurnMs = timings.DecorativePageTurnMilliseconds;
        if (_decorativePageTurnMs <= 0)
        {
            _cancelPageTurnDecor?.Invoke();
            _cancelPageTurnDecor = null;
        }
        _topMotion.Configure(0, timings.NavigationOverlayOutMilliseconds, clock);
        _bottomMotion.Configure(0, timings.NavigationOverlayOutMilliseconds, clock);
        ResetIdleDeadline();
    }

    private void Render()
    {
        var book = _viewModel.Book;
        var title = _topBar.Children.OfType<TextBlock>().FirstOrDefault(block => block.Classes.Contains("fluent-reader-title"));
        if (title is not null) title.Text = book is null ? "阅读器" : $"{book.BookTitle} · {book.ChapterTitle} · {_viewModel.PageLabel}";

        // AC-3（格 2）：双页 / webtoon 连续页都加载 Pages[i] + Pages[i+1]；单页只显示当前页。
        if (_viewModel.PageBytes is { Length: > 0 } bytes)
        {
            ApplyImageBytes(_pageImage, bytes, ref _imageBytes, ref _bitmap);
            var secondary = _viewModel.PageBytesSecondary;
            if (secondary is { Length: > 0 })
            {
                ApplyImageBytes(_pageImageSecondary, secondary, ref _imageBytesSecondary, ref _bitmapSecondary);
            }
            else
            {
                // R3-002：末页 / 单页章节 / 第二页读取失败时，第二页必须**彻底**清空
                // （bitmap/bytes/size/可见性），否则 webtoon 分支会用残留 bitmap 继续显示上一页。
                ClearSecondaryImage();
            }

            _pageImage.RenderTransform = new ScaleTransform(_viewModel.Zoom, _viewModel.Zoom);
            _pageImageSecondary.RenderTransform = new ScaleTransform(_viewModel.Zoom, _viewModel.Zoom);
            var webtoon = _viewModel.IsWebtoon;
            _pageSurface.IsVisible = !webtoon;
            _pageImageSecondary.IsVisible = !webtoon && _viewModel.DoublePage && _pageImageSecondary.Source is not null;

            // webtoon 连续页：当前页 + 后继页纵向堆叠（L-R3-1：本卡口径仅两页连续；全章长滚动/
            // 窗口化加载 re-home FEA-06-RESIDUAL-5）。逻辑像素尺寸来自 Host 投影，保证真实滚动范围。
            _webtoonScroll.IsVisible = webtoon;
            _webtoonImagePrimary.Source = _bitmap;
            _webtoonImageSecondary.Source = _bitmapSecondary;
            _webtoonImageSecondary.IsVisible = _bitmapSecondary is not null;
            if (webtoon)
            {
                ApplyWebtoonLogicalSizes();
            }
        }
        else
        {
            _pageSurface.IsVisible = false;
            _webtoonScroll.IsVisible = false;
            ClearSecondaryImage();
        }

        _progress.Value = _viewModel.Progress;
        AutomationProperties.SetName(_progress, $"阅读进度 {_viewModel.Progress:0}%");
        _messageHost.IsVisible = _viewModel.State is FluentPageState.Empty or FluentPageState.Error or FluentPageState.Partial;
        if (_viewModel.State == FluentPageState.Empty)
        {
            _messageHost.Child = FluentUi.Empty("本章节暂无页面", "返回书架选择其他章节。", "返回", _back);
        }
        else if (_viewModel.State == FluentPageState.Error)
        {
            _messageHost.Child = FluentUi.Banner(StatusKind.Failed, "页面读取失败", _viewModel.Error,
                "重试", () => _ = _viewModel.RetryAsync());
        }
        else if (_viewModel.State == FluentPageState.Partial)
        {
            _messageHost.Child = FluentUi.Banner(StatusKind.Blocked, "页面未就绪", _viewModel.Error,
                "重试", () => _ = _viewModel.RetryAsync());
        }

        // I-14：源不可用只读警示本体（07:46「顶部警示条 + 缺页占位」）；恢复动作归 B-3，仅给禁用占位入口。
        _sourceWarningHost.IsVisible = _viewModel.IsSourceUnavailable;
        if (_viewModel.IsSourceUnavailable)
        {
            var warning = FluentUi.Stack("fluent-page-layout");
            warning.Children.Add(FluentUi.Banner(StatusKind.Locked, "源文件不可用",
                "当前页引用的原文件不可用或未就绪；页面按只读方式展示，进度不会写入不可用页。", null, null));
            var recover = FluentUi.Button("恢复源文件", "fluent-secondary", null, "恢复源文件");
            recover.IsEnabled = false;
            ToolTip.SetTip(recover, "恢复动作待阅读器数据端口接入（B-3）；当前只展示警示。");
            warning.Children.Add(recover);
            _sourceWarningHost.Child = warning;
        }

        _thumbStrip.ItemsSource = book is null ? Array.Empty<int>() : Enumerable.Range(0, book.Pages.Count).ToArray();
        _thumbStrip.ItemTemplate = new Avalonia.Controls.Templates.FuncDataTemplate<int>((index, nameScope) =>
        {
            var button = FluentUi.Button($"{index + 1}", "fluent-secondary", () => _ = JumpToPageAsync(index),
                $"跳转到第 {index + 1} 页");
            button.Classes.Set("selected", index == _viewModel.PageIndex);
            return button;
        });
        var status = _bottomBar.Children.OfType<StackPanel>().FirstOrDefault()?.Children.OfType<TextBlock>().FirstOrDefault();
        if (status is not null)
        {
            status.Text = _viewModel.IsSavingProgress ? "进度写回中…" : _viewModel.Status;
        }
    }

    private static void ApplyImageBytes(Image target, byte[] bytes, ref byte[]? cached, ref Bitmap? bitmap)
    {
        if (cached is not null && cached.AsSpan().SequenceEqual(bytes))
        {
            target.Source = bitmap;
            return;
        }

        bitmap?.Dispose();
        cached = bytes;
        using var stream = new MemoryStream(bytes, writable: false);
        bitmap = new Bitmap(stream);
        target.Source = bitmap;
    }

    /// <summary>
    /// R3-002（AC-3）：把第二页的所有状态彻底清空——双页 Image、webtoon 第二页 Image、
    /// 缓存的字节/bitmap 与逻辑尺寸。缺失分支只清 Source 会让 webtoon 继续渲染上一页的残留 bitmap。
    /// </summary>
    private void ClearSecondaryImage()
    {
        _pageImageSecondary.Source = null;
        _pageImageSecondary.IsVisible = false;
        _webtoonImageSecondary.Source = null;
        _webtoonImageSecondary.IsVisible = false;
        _webtoonImageSecondary.Width = double.NaN;
        _webtoonImageSecondary.Height = double.NaN;
        _bitmapSecondary?.Dispose();
        _bitmapSecondary = null;
        _imageBytesSecondary = null;
    }

    private void ApplyWebtoonLogicalSizes()
    {
        var pages = _viewModel.Book?.Pages;
        if (pages is null)
        {
            return;
        }

        var index = _viewModel.PageIndex;
        SizeImage(_webtoonImagePrimary, pages.ElementAtOrDefault(index));
        SizeImage(_webtoonImageSecondary,
            _viewModel.PageBytesSecondary is { Length: > 0 } ? pages.ElementAtOrDefault(index + 1) : null);

        static void SizeImage(Image image, ReaderPageData? page)
        {
            if (page is null)
            {
                return;
            }

            image.Width = page.WidthPx > 0 ? page.WidthPx : 320;
            image.Height = page.HeightPx > 0 ? page.HeightPx : 480;
        }
    }

    private async Task JumpToPageAsync(int index)
    {
        var delta = index - _viewModel.PageIndex;
        if (delta != 0) await _viewModel.NavigateAsync(delta);
    }

    private void ToggleFullScreen()
    {
        _viewModel.IsFullScreen = !_viewModel.IsFullScreen;
        _setFullScreen(_viewModel.IsFullScreen);
    }

    private void OnKeyDown(object? sender, KeyEventArgs args)
    {
        WakeToolBars();
        if (args.Key is Key.Left or Key.PageUp)
        {
            _ = _viewModel.PreviousAsync();
            args.Handled = true;
        }
        else if (args.Key is Key.Right or Key.PageDown)
        {
            _ = _viewModel.NextAsync();
            args.Handled = true;
        }
        else if (args.Key == Key.Add || args.Key == Key.OemPlus)
        {
            _viewModel.ZoomBy(0.1);
            args.Handled = true;
        }
        else if (args.Key == Key.Subtract || args.Key == Key.OemMinus)
        {
            _viewModel.ZoomBy(-0.1);
            args.Handled = true;
        }
        else if (args.Key == Key.D0)
        {
            _viewModel.ResetZoom();
            args.Handled = true;
        }
        else if (args.Key == Key.F)
        {
            ToggleFullScreen();
            args.Handled = true;
        }
        else if (args.Key == Key.Escape && _viewModel.IsFullScreen)
        {
            _viewModel.IsFullScreen = false;
            _setFullScreen(false);
            args.Handled = true;
        }
    }
}
