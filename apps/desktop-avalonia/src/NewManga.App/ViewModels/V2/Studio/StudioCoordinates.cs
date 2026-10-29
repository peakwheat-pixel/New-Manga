using NewManga.CoreClient;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>A rectangle in one coordinate space (page pixels or rendered/zoomed pixels).</summary>
public readonly record struct StudioRect(double X, double Y, double Width, double Height)
{
    public static StudioRect Empty { get; } = new(0, 0, 0, 0);

    public double Right => X + Width;

    public double Bottom => Y + Height;

    public bool IsEmpty => Width <= 0 || Height <= 0;

    public StudioRect Scale(double factor) => new(X * factor, Y * factor, Width * factor, Height * factor);

    public StudioRect Inflate(double amount) =>
        new(X - amount, Y - amount, Math.Max(0, Width + 2 * amount), Math.Max(0, Height + 2 * amount));

    public override string ToString() =>
        $"{X:0.##},{Y:0.##} {Width:0.##}×{Height:0.##}";
}

/// <summary>
/// V11R-B-3 AC: region overlay geometry. The Core read face stores normalised (0..1) geometry
/// (<see cref="RegionGeometrySummary"/>); the canvas renders page pixels scaled by the current zoom.
/// All conversions live here so the headless tests measure exactly what the overlay uses — a region
/// box can never drift from the real page pixels (the old workbench did this inline).
/// </summary>
public static class StudioCoordinates
{
    /// <summary>AC: 86% default zoom (SCREEN_SPECS §3), deliberately not "fit window".</summary>
    public const double DefaultZoom = 0.86;

    public const double MinZoom = 0.25;

    public const double MaxZoom = 4.0;

    /// <summary>Wheel zoom factor per notch; keyboard steps use <see cref="ZoomStep"/>.</summary>
    public const double WheelZoomFactor = 1.1;

    public const double ZoomStep = 0.1;

    /// <summary>Canvas breathing room around the page (SIX_DIMENSIONS §2.2: 32–48).</summary>
    public const double FitPadding = 32;

    public static double ClampZoom(double zoom) =>
        double.IsNaN(zoom) ? DefaultZoom : Math.Clamp(zoom, MinZoom, MaxZoom);

    /// <summary>Snaps to a 0.1 grid for keyboard steps without chasing floating point noise.</summary>
    public static double SnapZoom(double zoom) =>
        ClampZoom(Math.Round(ClampZoom(zoom) * 10, MidpointRounding.AwayFromZero) / 10);

    public static double ZoomIn(double zoom) => SnapZoom(ClampZoom(zoom) + ZoomStep);

    public static double ZoomOut(double zoom) => SnapZoom(ClampZoom(zoom) - ZoomStep);

    /// <summary>Wheel notch: <paramref name="notches"/> positive = zoom in.</summary>
    public static double ApplyWheelZoom(double zoom, int notches)
    {
        var next = ClampZoom(zoom);
        var steps = Math.Abs(notches);
        for (var index = 0; index < steps; index++)
        {
            next = notches > 0 ? next * WheelZoomFactor : next / WheelZoomFactor;
        }

        return ClampZoom(next);
    }

    /// <summary>AC: 适应窗口 — the scale where the page fits the viewport minus breathing room.</summary>
    public static double FitZoom(
        double viewportWidth,
        double viewportHeight,
        double pageWidth,
        double pageHeight,
        double padding = FitPadding)
    {
        if (viewportWidth <= 0 || viewportHeight <= 0 || pageWidth <= 0 || pageHeight <= 0)
        {
            return DefaultZoom;
        }

        var availableWidth = Math.Max(1, viewportWidth - 2 * padding);
        var availableHeight = Math.Max(1, viewportHeight - 2 * padding);
        return ClampZoom(Math.Min(availableWidth / pageWidth, availableHeight / pageHeight));
    }

    /// <summary>
    /// Normalised region geometry → page-pixel rectangle. Values are clamped to the page so a
    /// malformed Core row can never paint outside the page surface; negative extents collapse to 0.
    /// Returns <see cref="StudioRect.Empty"/> when the page extent is unknown.
    /// </summary>
    public static StudioRect NormalizedToPixels(RegionGeometrySummary? geometry, RegionPageSize? pageSize)
    {
        if (geometry is null || pageSize is null || pageSize.Width <= 0 || pageSize.Height <= 0)
        {
            return StudioRect.Empty;
        }

        var x = Math.Clamp(geometry.X, 0, 1);
        var y = Math.Clamp(geometry.Y, 0, 1);
        var width = Math.Clamp(geometry.Width, 0, 1 - x);
        var height = Math.Clamp(geometry.Height, 0, 1 - y);
        return new StudioRect(
            x * pageSize.Width,
            y * pageSize.Height,
            width * pageSize.Width,
            height * pageSize.Height);
    }

    /// <summary>Inverse of <see cref="NormalizedToPixels"/> (page pixels → 0..1), clamped.</summary>
    public static StudioRect PixelsToNormalized(StudioRect pixels, RegionPageSize? pageSize)
    {
        if (pageSize is null || pageSize.Width <= 0 || pageSize.Height <= 0)
        {
            return StudioRect.Empty;
        }

        var x = Math.Clamp(pixels.X / pageSize.Width, 0, 1);
        var y = Math.Clamp(pixels.Y / pageSize.Height, 0, 1);
        var width = Math.Clamp(pixels.Width / pageSize.Width, 0, 1 - x);
        var height = Math.Clamp(pixels.Height / pageSize.Height, 0, 1 - y);
        return new StudioRect(x, y, width, height);
    }

    /// <summary>
    /// Logical content size of the page surface at <paramref name="zoom"/>. The overlay canvas uses
    /// exactly this size, so <c>RegionBox.Left == pixelRect.X * zoom</c> holds by construction.
    /// </summary>
    public static (double Width, double Height) ContentSize(RegionPageSize? pageSize, double zoom) =>
        pageSize is null || pageSize.Width <= 0 || pageSize.Height <= 0
            ? (0, 0)
            : (pageSize.Width * ClampZoom(zoom), pageSize.Height * ClampZoom(zoom));

    /// <summary>Region rectangle in rendered (zoomed) canvas pixels.</summary>
    public static StudioRect ToRendered(StudioRect pagePixels, double zoom) => pagePixels.Scale(ClampZoom(zoom));

    /// <summary>
    /// Keeps the content point under the pointer fixed while zooming (wheel zoom, AC).
    /// <paramref name="offset"/> is the content offset inside the viewport (negative = scrolled).
    /// </summary>
    public static (double X, double Y) ZoomAroundPoint(
        double offsetX,
        double offsetY,
        double pointerX,
        double pointerY,
        double oldZoom,
        double newZoom)
    {
        var from = ClampZoom(oldZoom);
        var to = ClampZoom(newZoom);
        if (Math.Abs(to - from) < 0.0001)
        {
            return (offsetX, offsetY);
        }

        var contentX = (pointerX - offsetX) / from;
        var contentY = (pointerY - offsetY) / from;
        return (pointerX - contentX * to, pointerY - contentY * to);
    }

    /// <summary>
    /// Clamps a pan offset so the page cannot be dragged out of the viewport. When the content is
    /// smaller than the viewport on one axis it is centred on that axis.
    /// </summary>
    public static (double X, double Y) ClampOffset(
        double offsetX,
        double offsetY,
        double contentWidth,
        double contentHeight,
        double viewportWidth,
        double viewportHeight)
    {
        return (
            ClampAxis(offsetX, contentWidth, viewportWidth),
            ClampAxis(offsetY, contentHeight, viewportHeight));
    }

    private static double ClampAxis(double offset, double content, double viewport)
    {
        if (content <= 0 || viewport <= 0)
        {
            return 0;
        }

        if (content <= viewport)
        {
            return (viewport - content) / 2;
        }

        return Math.Clamp(offset, viewport - content, 0);
    }

    /// <summary>Zooms to fit and centres the page (适应窗口 action).</summary>
    public static (double Zoom, double OffsetX, double OffsetY) FitAndCenter(
        double viewportWidth,
        double viewportHeight,
        RegionPageSize? pageSize,
        double padding = FitPadding)
    {
        if (pageSize is null || pageSize.Width <= 0 || pageSize.Height <= 0 ||
            viewportWidth <= 0 || viewportHeight <= 0)
        {
            return (DefaultZoom, 0, 0);
        }

        var zoom = FitZoom(viewportWidth, viewportHeight, pageSize.Width, pageSize.Height, padding);
        var (width, height) = ContentSize(pageSize, zoom);
        var (offsetX, offsetY) = ClampOffset(0, 0, width, height, viewportWidth, viewportHeight);
        return (zoom, offsetX, offsetY);
    }

    /// <summary>Percentage text for the zoom chip ("86%").</summary>
    public static string ZoomLabel(double zoom) => $"{Math.Round(ClampZoom(zoom) * 100):0}%";
}
