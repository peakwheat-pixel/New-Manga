using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3 <c>CanvasViewport</c> + <c>PageSurface</c>: 86% default zoom, wheel zoom anchored at the
/// pointer, drag pan, fit window, and the 页面 / 成品 / 分屏 surface switch. The page image is the real
/// Host resource-channel bytes (<c>ReadPageImageAsync</c>); 成品/分屏 need the rendered-page read that
/// is not on the frozen face yet, so they render an explicit NOT_WIRED placeholder instead of a fake.
/// </summary>
public sealed class StudioCanvasViewport : Border
{
    private readonly StudioPageViewModel _viewModel;
    private readonly Canvas _host;
    private readonly Canvas _content;
    private readonly Border _pageFrame;
    private readonly Grid _surfaceGrid;
    private readonly Border _imageHost;
    private readonly Image _image;
    private readonly Border _placeholderHost;
    private readonly TextBlock _placeholderText;
    private readonly Border _finalHost;
    private readonly TextBlock _finalText;
    private readonly Border _splitDivider;
    private readonly StudioRegionOverlay _overlay;
    private readonly StudioHudRingControl _hud;
    private Bitmap? _bitmap;
    private bool _panning;
    private Point _lastPointer;

    public StudioCanvasViewport(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;
        Classes.Add("studio-viewport");
        ClipToBounds = true;

        _image = new Image
        {
            Stretch = Stretch.Fill,
            HorizontalAlignment = HorizontalAlignment.Stretch,
            VerticalAlignment = VerticalAlignment.Stretch,
        };
        RenderOptions.SetBitmapInterpolationMode(_image, BitmapInterpolationMode.HighQuality);

        _placeholderText = StudioUi.Text("正在读取页面图…", "nm-meta");
        _placeholderHost = StudioUi.Box("studio-sunken");
        _placeholderHost.Child = new Border
        {
            Child = _placeholderText,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
        };

        _imageHost = new Border { Child = _image, ClipToBounds = true };

        _finalText = StudioUi.Text(
            "成品预览 · 能力待接入\n渲染结果读取命令未接入（F0-1）", "nm-meta", "nm-center", "nm-wrap");
        _finalHost = StudioUi.Box("studio-sunken");
        _finalHost.Child = new Border
        {
            Child = _finalText,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
        };
        _finalHost.IsVisible = false;

        _splitDivider = StudioUi.Box("studio-divider");
        _splitDivider.Width = 1; // 1px hairline is the only allowed raw size (contract §2.2 exception)
        _splitDivider.HorizontalAlignment = HorizontalAlignment.Left;
        _splitDivider.IsVisible = false;

        _surfaceGrid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,*") };
        Grid.SetColumnSpan(_imageHost, 2);
        _surfaceGrid.Children.Add(_imageHost);
        _surfaceGrid.Children.Add(_finalHost);
        _surfaceGrid.Children.Add(_splitDivider);

        _pageFrame = StudioUi.Box("studio-page-shadowless");
        _pageFrame.ClipToBounds = true;
        _pageFrame.Child = _surfaceGrid;

        _overlay = new StudioRegionOverlay(viewModel);
        _hud = new StudioHudRingControl(viewModel);

        _content = new Canvas();
        _content.Children.Add(_pageFrame);
        _content.Children.Add(_overlay);
        _content.Children.Add(_hud);

        _host = new Canvas { ClipToBounds = true };
        _host.Children.Add(_content);
        Child = _host;

        PointerWheelChanged += OnWheel;
        PointerPressed += OnPointerPressed;
        PointerMoved += OnPointerMoved;
        PointerReleased += OnPointerReleased;
        SizeChanged += (_, _) => UpdateViewport();

        viewModel.CanvasInvalidated += (_, _) => UpdateLayoutState();
        viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioPageViewModel.PageImageBytes) or nameof(StudioPageViewModel.HasPageImage))
            {
                UpdateImage();
            }

            UpdateLayoutState();
        };

        UpdateImage();
        UpdateLayoutState();
    }

    public StudioRegionOverlay RegionOverlay => _overlay;

    public StudioHudRingControl Hud => _hud;

    public Image PageImage => _image;

    public Border FinalPlaceholder => _finalHost;

    public TextBlock PlaceholderText => _placeholderText;

    public Border PageFrame => _pageFrame;

    /// <summary>Current viewport size in device-independent pixels (tests assert the fit math).</summary>
    public Size ViewportSize => Bounds.Size;

    public Size RenderedContentSize => new(_viewModel.ContentWidth, _viewModel.ContentHeight);

    private void UpdateViewport()
    {
        _viewModel.SetViewportSize(Bounds.Width, Bounds.Height);
        UpdateLayoutState();
    }

    private void UpdateImage()
    {
        var bytes = _viewModel.PageImageBytes;
        if (bytes is null || bytes.Length == 0)
        {
            _bitmap?.Dispose();
            _bitmap = null;
            _image.Source = null;
            UpdatePlaceholder();
            return;
        }

        try
        {
            using var stream = new MemoryStream(bytes);
            var next = new Bitmap(stream);
            _bitmap?.Dispose();
            _bitmap = next;
            _image.Source = _bitmap;
        }
        catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or NotSupportedException)
        {
            _image.Source = null;
        }

        UpdatePlaceholder();
    }

    private void UpdatePlaceholder()
    {
        var missing = !_viewModel.HasPageImage;
        _placeholderHost.IsVisible = missing;
        _placeholderText.Text = _viewModel.PageImageNote;
        _imageHost.IsVisible = _viewModel.HasPageImage;
        ApplySurfaceMode();
    }

    /// <summary>页面 = image + overlay; 成品 = NOT_WIRED placeholder; 分屏 = image left / placeholder right.</summary>
    private void ApplySurfaceMode()
    {
        var mode = _viewModel.SurfaceMode;
        var hasImage = _viewModel.HasPageImage;
        switch (mode)
        {
            case StudioSurfaceMode.Page:
                Grid.SetColumnSpan(_imageHost, 2);
                Grid.SetColumn(_imageHost, 0);
                _imageHost.IsVisible = hasImage;
                _finalHost.IsVisible = false;
                _splitDivider.IsVisible = false;
                break;
            case StudioSurfaceMode.Final:
                _imageHost.IsVisible = false;
                Grid.SetColumnSpan(_finalHost, 2);
                Grid.SetColumn(_finalHost, 0);
                _finalHost.IsVisible = true;
                _splitDivider.IsVisible = false;
                break;
            case StudioSurfaceMode.Split:
                Grid.SetColumnSpan(_imageHost, 1);
                Grid.SetColumn(_imageHost, 0);
                _imageHost.IsVisible = hasImage;
                Grid.SetColumnSpan(_finalHost, 1);
                Grid.SetColumn(_finalHost, 1);
                _finalHost.IsVisible = true;
                _splitDivider.IsVisible = true;
                break;
        }

        _overlay.IsVisible = mode == StudioSurfaceMode.Page;
        _hud.IsVisible = mode == StudioSurfaceMode.Page && _viewModel.HudVisible;
    }

    /// <summary>Repositions the page surface, overlay and HUD for the current zoom/pan (single place).</summary>
    public void UpdateLayoutState()
    {
        var zoom = _viewModel.Zoom;
        var width = _viewModel.ContentWidth;
        var height = _viewModel.ContentHeight;

        _content.Width = width;
        _content.Height = height;
        Canvas.SetLeft(_content, _viewModel.OffsetX);
        Canvas.SetTop(_content, _viewModel.OffsetY);

        _pageFrame.Width = width;
        _pageFrame.Height = height;
        _placeholderHost.Width = width;
        _placeholderHost.Height = height;
        _placeholderHost.IsVisible = !_viewModel.HasPageImage;

        // Placeholder sits above the frame when the image is missing (page-sized, no layout jump).
        Canvas.SetLeft(_placeholderHost, 0);
        Canvas.SetTop(_placeholderHost, 0);
        if (!_content.Children.Contains(_placeholderHost))
        {
            _content.Children.Insert(0, _placeholderHost);
        }

        _overlay.Width = width;
        _overlay.Height = height;
        Canvas.SetLeft(_overlay, 0);
        Canvas.SetTop(_overlay, 0);
        _overlay.Relayout();

        _hud.Width = width;
        _hud.Height = height;
        Canvas.SetLeft(_hud, 0);
        Canvas.SetTop(_hud, 0);
        _hud.UpdateLayoutState();

        // Improve resampling: exact 1:1 or upscaled pages must not be blurred.
        RenderOptions.SetBitmapInterpolationMode(
            _image,
            zoom >= 1 ? BitmapInterpolationMode.None : BitmapInterpolationMode.HighQuality);

        UpdatePlaceholder();
    }

    private void OnWheel(object? sender, PointerWheelEventArgs args)
    {
        var point = args.GetPosition(this);
        var notches = args.Delta.Y > 0 ? 1 : args.Delta.Y < 0 ? -1 : 0;
        if (notches == 0)
        {
            args.Handled = true;
            return;
        }

        _viewModel.HandleWheel(notches, point.X, point.Y);
        args.Handled = true;
    }

    private void OnPointerPressed(object? sender, PointerPressedEventArgs args)
    {
        var point = args.GetCurrentPoint(this);
        if (!point.Properties.IsLeftButtonPressed)
        {
            return;
        }

        _panning = true;
        _lastPointer = point.Position;
        args.Pointer.Capture(this);
        args.Handled = true;
    }

    private void OnPointerMoved(object? sender, PointerEventArgs args)
    {
        if (!_panning)
        {
            return;
        }

        var position = args.GetPosition(this);
        _viewModel.PanBy(position.X - _lastPointer.X, position.Y - _lastPointer.Y);
        _lastPointer = position;
        args.Handled = true;
    }

    private void OnPointerReleased(object? sender, PointerReleasedEventArgs args)
    {
        if (!_panning)
        {
            return;
        }

        _panning = false;
        args.Pointer.Capture(null);
        args.Handled = true;
    }
}
