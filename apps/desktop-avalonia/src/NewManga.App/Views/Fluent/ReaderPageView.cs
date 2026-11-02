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
using NewManga.App.Controls;
using NewManga.App.ViewModels.Fluent;
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
    private readonly StackPanel _root;
    private readonly StackPanel _topBar;
    private readonly StackPanel _bottomBar;
    private readonly DsReaderPage _pageSurface;
    private readonly Image _pageImage;
    private readonly Border _messageHost;
    private readonly Border _sourceWarningHost;
    private readonly Border _sideRailHost;
    private readonly Button _sideRailRestore;
    private readonly PageThumbStrip _thumbStrip;
    private readonly ReaderProgressBar _progress;
    private readonly DispatcherTimer _autoHideTimer;
    private byte[]? _imageBytes;
    private Bitmap? _bitmap;

    public ReaderPageView(ReaderViewModel viewModel, Action back, Action<bool> setFullScreen)
    {
        _viewModel = viewModel;
        _back = back;
        _setFullScreen = setFullScreen;
        Focusable = true;
        _pageImage = new Image { Stretch = Stretch.Uniform, HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center };
        _pageSurface = new DsReaderPage { Child = _pageImage, Classes = { "fluent-reader-page" } };
        _pageSurface.Focusable = true;
        AutomationProperties.SetName(_pageSurface, "当前漫画页面");
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
        _root = FluentUi.Stack("fluent-page-layout");
        _root.Children.Add(_topBar);
        _root.Children.Add(_sourceWarningHost);
        _root.Children.Add(BuildReadingArea());
        _root.Children.Add(_bottomBar);
        Content = _root;
        _autoHideTimer = new DispatcherTimer { Interval = ToolBarAutoHideInterval };
        _autoHideTimer.Tick += (_, _) => _viewModel.HideToolBarsAfterIdle();
        _viewModel.PropertyChanged += OnViewModelPropertyChanged;
        KeyDown += OnKeyDown;
        _pageSurface.DoubleTapped += (_, _) => _viewModel.ToggleDoublePage();
        _pageSurface.PointerPressed += (_, args) => HandleReadingAreaTap(args.GetPosition(_pageSurface));
        _pageSurface.PointerWheelChanged += (_, args) =>
        {
            _ = args.Delta.Y >= 0 ? _viewModel.PreviousAsync() : _viewModel.NextAsync();
            args.Handled = true;
        };
        AddHandler(InputElement.PointerMovedEvent, (_, _) => WakeToolBars(), RoutingStrategies.Tunnel);
        AttachedToVisualTree += (_, _) => { if (_viewModel.AreToolBarsVisible) _autoHideTimer.Start(); };
        DetachedFromVisualTree += (_, _) => _autoHideTimer.Stop();
        ApplyToolBarsMotionMode();
        ApplyToolBarsVisibility();
        ApplySideRailVisibility();
        Render();
    }

    public ReaderViewModel ViewModel => _viewModel;
    public Image PageImage => _pageImage;
    public DsReaderPage PageSurface => _pageSurface;
    public Border SideRail => _sideRailHost;
    public StackPanel TopBar => _topBar;
    public StackPanel BottomBar => _bottomBar;
    public TimeSpan AutoHideTimerInterval => _autoHideTimer.Interval;

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
        Render();
    }

    private void WakeToolBars()
    {
        _viewModel.PokeToolBars();
        // impl-r1 R1-003: every interaction restarts the 2s idle deadline, even while the bars are
        // already visible (PokeToolBars is idempotent for the bool, so the old code never restarted the
        // timer and the bars could hide mid-interaction).
        if (_viewModel.AreToolBarsVisible && TopLevel.GetTopLevel(this) is not null)
        {
            _autoHideTimer.Stop();
            _autoHideTimer.Start();
        }
    }

    private void ApplyToolBarsVisibility()
    {
        _topBar.IsVisible = _viewModel.AreToolBarsVisible;
        _bottomBar.IsVisible = _viewModel.AreToolBarsVisible;
        if (_viewModel.AreToolBarsVisible)
        {
            _autoHideTimer.Start();
        }
        else
        {
            _autoHideTimer.Stop();
        }
    }

    private void ApplySideRailVisibility()
    {
        _sideRailHost.IsVisible = _viewModel.IsSideRailVisible;
        _sideRailRestore.IsVisible = !_viewModel.IsSideRailVisible;
    }

    private void ApplyToolBarsMotionMode()
    {
        // I-10：full/auto 下条带 160ms 淡出过渡（02-motion §2.1 浮层退出参数）；reduce 下直接切换（07:23）。
        if (_viewModel.AreToolBarsReducedMotion)
        {
            _topBar.Transitions = null;
            _bottomBar.Transitions = null;
            return;
        }

        var fade = new Transitions { new DoubleTransition { Property = OpacityProperty, Duration = ToolBarFadeDuration } };
        _topBar.Transitions = fade;
        _bottomBar.Transitions = new Transitions { new DoubleTransition { Property = OpacityProperty, Duration = ToolBarFadeDuration } };
    }

    private void Render()
    {
        var book = _viewModel.Book;
        var title = _topBar.Children.OfType<TextBlock>().FirstOrDefault(block => block.Classes.Contains("fluent-reader-title"));
        if (title is not null) title.Text = book is null ? "阅读器" : $"{book.BookTitle} · {book.ChapterTitle} · {_viewModel.PageLabel}";

        if (_viewModel.PageBytes is { Length: > 0 } bytes)
        {
            if (_imageBytes is null || !_imageBytes.AsSpan().SequenceEqual(bytes))
            {
                _bitmap?.Dispose();
                _imageBytes = bytes;
                using var stream = new MemoryStream(bytes, writable: false);
                _bitmap = new Bitmap(stream);
                _pageImage.Source = _bitmap;
            }

            _pageImage.RenderTransform = new ScaleTransform(_viewModel.Zoom, _viewModel.Zoom);
            _pageSurface.IsVisible = true;
        }
        else
        {
            _pageSurface.IsVisible = false;
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
