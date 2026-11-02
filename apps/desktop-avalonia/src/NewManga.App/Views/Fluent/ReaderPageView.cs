using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Automation;
using NewManga.App.Controls;
using NewManga.App.ViewModels.Fluent;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;
using DsReaderPage = NewManga.DesignSystem.Controls.ReaderPage;

namespace NewManga.App.Views.Fluent;

/// <summary>Fluent Reader overlay. Page ids and progress stay Host-owned.</summary>
public sealed class ReaderPageView : UserControl
{
    private readonly ReaderViewModel _viewModel;
    private readonly Action _back;
    private readonly Action<bool> _setFullScreen;
    private readonly StackPanel _root;
    private readonly DsReaderPage _pageSurface;
    private readonly Image _pageImage;
    private readonly Border _messageHost;
    private readonly PageThumbStrip _thumbStrip;
    private readonly ReaderProgressBar _progress;
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
        _thumbStrip = new PageThumbStrip();
        _progress = new ReaderProgressBar { Minimum = 0, Maximum = 100 };
        _root = FluentUi.Stack("fluent-page-layout");
        _root.Children.Add(BuildTopBar());
        _root.Children.Add(BuildReadingArea());
        _root.Children.Add(BuildBottomBar());
        Content = _root;
        _viewModel.PropertyChanged += (_, _) => Render();
        KeyDown += OnKeyDown;
        _pageSurface.DoubleTapped += (_, _) => _viewModel.ToggleDoublePage();
        _pageSurface.PointerWheelChanged += (_, args) =>
        {
            _ = args.Delta.Y >= 0 ? _viewModel.PreviousAsync() : _viewModel.NextAsync();
            args.Handled = true;
        };
        Render();
    }

    public ReaderViewModel ViewModel => _viewModel;
    public Image PageImage => _pageImage;

    public async Task LoadAsync(string? bookId, string? chapterId, CancellationToken cancellationToken = default)
    {
        await _viewModel.LoadAsync(bookId, chapterId, cancellationToken);
        Focus();
    }

    private Control BuildTopBar()
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
        return grid;
    }

    private Control BuildBottomBar()
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

    private void Render()
    {
        var book = _viewModel.Book;
        var title = _root.Children.OfType<StackPanel>().First().Children.OfType<TextBlock>().FirstOrDefault(block => block.Classes.Contains("fluent-reader-title"));
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

        _thumbStrip.ItemsSource = book is null ? Array.Empty<int>() : Enumerable.Range(0, book.Pages.Count).ToArray();
        _thumbStrip.ItemTemplate = new Avalonia.Controls.Templates.FuncDataTemplate<int>((index, nameScope) =>
        {
            var button = FluentUi.Button($"{index + 1}", "fluent-secondary", () => _ = JumpToPageAsync(index),
                $"跳转到第 {index + 1} 页");
            button.Classes.Set("selected", index == _viewModel.PageIndex);
            return button;
        });
        var status = _root.Children.OfType<StackPanel>().Skip(1).FirstOrDefault();
        if (status is not null)
        {
            var pageText = status.Children.OfType<TextBlock>().FirstOrDefault();
            if (pageText is not null) pageText.Text = _viewModel.IsSavingProgress ? "进度写回中…" : _viewModel.Status;
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
