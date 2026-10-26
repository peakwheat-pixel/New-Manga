using System.Diagnostics;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.ViewModels;
using NewManga.Theme;

namespace NewManga.App.Views;

/// <summary>AC1 workbench: fixed 300/mid/230 columns, zoom 50-200%, tile canvas, region/bubble editing.</summary>
public sealed class WorkbenchPage : UserControl
{
    public WorkbenchPage(WorkbenchViewModel viewModel)
    {
        ViewModel = viewModel;
        Name = "WorkbenchPage";
        var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("300,*,230") };
        grid.Children.Add(BuildLeft());
        grid.Children.Add(BuildCenter());
        grid.Children.Add(BuildRight());
        Content = grid;
        ApplyTheme();
    }

    public WorkbenchViewModel ViewModel { get; }

    public ITileSource? TileSource { get; private set; }

    public void BindTileSource(ITileSource? source) => TileSource = source;

    public Grid Root => (Grid)Content!;

    public Slider ZoomSlider { get; private set; } = null!;

    public TextBlock ZoomLabel { get; private set; } = null!;

    public Canvas RegionLayer { get; private set; } = null!;

    public Border CanvasHost { get; private set; } = null!;

    public ListBox RegionList { get; private set; } = null!;

    public TextBox BubbleText { get; private set; } = null!;

    public ComboBox BubbleOrientation { get; private set; } = null!;

    public ItemsControl ThumbnailList { get; private set; } = null!;

    public double LeftColumnWidth => Root.ColumnDefinitions[0].Width.Value;

    public double RightColumnWidth => Root.ColumnDefinitions[2].Width.Value;

    public void ApplyTheme()
    {
        Background = ThemePackService.Brush("AppBg");
    }

    private Control BuildLeft()
    {
        var panel = new StackPanel { Spacing = 10, Margin = new Thickness(16) };
        panel.Children.Add(Ui.Text("翻译设置", 15, "TextPrimary", bold: true));
        panel.Children.Add(Ui.Text("动作栈按色族分组（S4 骨架）", 11, "TextSecondary"));
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
            }
        };
        var zoomBox = new StackPanel { Spacing = 6 };
        zoomBox.Children.Add(Ui.Text("缩放 50–200%", 11, "TextSecondary"));
        zoomBox.Children.Add(ZoomSlider);
        panel.Children.Add(zoomBox);
        zoomRow.Children.Add(Ui.Text("画布缩放", 12, "TextSecondary"));
        zoomRow.Children.Add(ZoomLabel);
        panel.Children.Add(zoomRow);

        panel.Children.Add(Ui.Text("区域 (Region)", 13, "TextPrimary", bold: true));
        RegionList = new ListBox { ItemsSource = ViewModel.Regions, Height = 160 };
        RegionList.SelectionChanged += (_, _) => ViewModel.SelectedRegion = RegionList.SelectedItem as RegionItem;
        panel.Children.Add(RegionList);
        var addRegion = Ui.Action("添加区域", () =>
        {
            ViewModel.AddRegion(40, 40, 240, 160);
        }, primary: true);
        addRegion.Name = "AddRegionButton";
        panel.Children.Add(addRegion);
        var deleteRegion = Ui.Action("删除选中区域", () => ViewModel.DeleteSelectedRegion());
        panel.Children.Add(deleteRegion);
        return new Border { Background = ThemePackService.Brush("CardBg"), Child = new ScrollViewer { Content = panel } };
    }

    private Control BuildCenter()
    {
        var dock = new DockPanel();
        var toolbar = new StackPanel
        {
            Orientation = Avalonia.Layout.Orientation.Horizontal,
            Spacing = 10,
            Margin = new Thickness(12, 8),
            Background = ThemePackService.Brush("NavBg"),
        };
        toolbar.Children.Add(Ui.Text("Canvas · tile 渲染 BitmapInterpolationMode=None", 11, "TextSecondary"));
        toolbar.Children.Add(ZoomLabel = Ui.Text(ViewModel.ZoomLabel, 12, "TextPrimary", bold: true));
        DockPanel.SetDock(toolbar, Dock.Top);
        dock.Children.Add(toolbar);

        RegionLayer = new Canvas();
        var preview = new Border
        {
            Width = 720,
            Height = 520,
            Background = new SolidColorBrush(Color.Parse("#1E222B")),
            Child = new TextBlock
            {
                Text = "Region canvas（Core tile 预览占位）",
                Foreground = ThemePackService.Brush("TextSecondary"),
                FontSize = 12,
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
            },
        };
        Canvas.SetLeft(preview, 40);
        Canvas.SetTop(preview, 30);
        RegionLayer.Children.Add(preview);
        CanvasHost = new Border
        {
            Background = ThemePackService.Brush("ReaderBackground"),
            Child = new ScrollViewer { Content = RegionLayer, HorizontalScrollBarVisibility = ScrollBarVisibility.Auto },
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
                Background = ThemePackService.Brush("ChipBg"),
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
        return new Border { Background = ThemePackService.Brush("CardBg"), Child = new ScrollViewer { Content = panel } };
    }
}

/// <summary>AC2/AC3/AC4 reader page: fit/1:1/fit-width + virtualized webtoon, no interpolation.</summary>
public sealed class ReaderPage : UserControl
{
    private readonly IReadOnlyList<string> _pages;
    private readonly string? _tileDirectory;
    private readonly List<string> _tileFiles = new();
    private readonly Dictionary<int, Bitmap> _tileCache = new();
    private readonly Image _pageImage;
    private readonly ScrollViewer _webtoonScroll;
    private readonly ItemsControl _webtoonItems;
    private readonly TextBlock _hud;
    private readonly Border _root;
    private Bitmap? _currentBitmap;
    private ITileSource? _tileSource;

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
            Text = "沉浸阅读 · Esc 退出 · F 切换 fit · H 隐藏 UI",
            FontSize = 12,
            Foreground = Brushes.White,
            Margin = new Thickness(16, 10),
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
        };
        Hud = _hud;

        _root = new Border { Background = Brushes.Black, Child = new Grid { RowDefinitions = new RowDefinitions("Auto,*") , Children = { _hud, BuildSurface() } } };
        var grid = (Grid)_root.Child!;
        Grid.SetRow(grid.Children[1], 1);
        grid.Children.Add(_webtoonScroll);
        Grid.SetRow(_webtoonScroll, 1);
        Content = _root;

        PointerPressed += OnPointerPressed;
        PointerWheelChanged += OnWheel;
    }

    public ReaderViewModel ViewModel { get; }

    public Image PageImage { get; }

    public ScrollViewer WebtoonScroll { get; }

    public TextBlock Hud { get; }

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

    /// <summary>Loads one page image and applies the current fit mode; returns the measured frame cost.</summary>
    public PageTurnSample ShowPage(int index)
    {
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
        var size = _currentBitmap is null
            ? (ViewModel.ViewportWidth - 2 * ReaderViewModel.PagePadding, ViewModel.ViewportHeight - 2 * ReaderViewModel.PagePadding, 1.0)
            : ViewModel.DisplaySize(_currentBitmap.PixelSize.Width, _currentBitmap.PixelSize.Height);
        _pageImage.Stretch = ViewModel.FitMode == ReaderFitMode.OneToOne ? Stretch.None : Stretch.Uniform;
        _pageImage.Width = size.Item1;
        _pageImage.Height = size.Item2;
        _pageImage.Measure(new Size(ViewModel.ViewportWidth, ViewModel.ViewportHeight));
        _pageImage.Arrange(new Rect(0, 0, size.Item1, size.Item2));
        Dispatcher.UIThread.RunJobs();
        var total = watch.Elapsed.TotalMilliseconds;
        var sample = new PageTurnSample(index, total, decode, total - decode - layoutStart);
        ViewModel.RecordPageTurn(index, sample.TotalMs, sample.DecodeMs, sample.LayoutMs);
        ViewModel.SetPageCount(_pages.Count, index);
        return sample;
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
            PrepareWebtoon();
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
        var position = e.GetPosition(this);
        if (position.X < Bounds.Width * 0.25)
        {
            ViewModel.PreviousPage();
        }
        else if (position.X > Bounds.Width * 0.75)
        {
            ViewModel.NextPage();
        }
    }

    private void OnWheel(object? sender, PointerWheelEventArgs e)
    {
        if (e.Delta.Y > 0)
        {
            ViewModel.PreviousPage();
        }
        else if (e.Delta.Y < 0)
        {
            ViewModel.NextPage();
        }

        e.Handled = true;
    }
}

/// <summary>AC2 immersive reader window: borderless black chrome, Esc exits, H hides HUD, F cycles fit.</summary>
public sealed class ReaderWindow : Window
{
    public ReaderWindow(ReaderViewModel viewModel, IReadOnlyList<string> pages, string? tileDirectory = null)
    {
        Title = "阅读器";
        SystemDecorations = SystemDecorations.None;
        WindowState = WindowState.FullScreen;
        Background = Brushes.Black;
        Page = new ReaderPage(viewModel, pages, tileDirectory);
        Content = Page;
        KeyDown += OnKeyDown;
        Opened += (_, _) => Page.ShowPage(viewModel.CurrentPageIndex);
    }

    public ReaderPage Page { get; }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        switch (e.Key)
        {
            case Key.Escape:
                Close();
                break;
            case Key.H:
                Page.SetHudVisible(!Page.ViewModel.HudVisible);
                break;
            case Key.F:
                Page.CycleFitMode();
                break;
            case Key.Right:
            case Key.Down:
                Page.ViewModel.NextPage();
                break;
            case Key.Left:
            case Key.Up:
                Page.ViewModel.PreviousPage();
                break;
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
