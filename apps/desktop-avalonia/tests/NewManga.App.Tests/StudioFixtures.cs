using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-3 shareable fixtures: a real (if small) library chain through
/// <see cref="FakeHostController"/> so the Studio exercises the actual read path instead of a mock
/// object graph. One 3-page chapter, 3 regions with normalised geometry, revision history, and a real
/// 1×1 PNG so the page surface decodes an actual bitmap.
/// </summary>
internal static class StudioFixtures
{
    public const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

    /// <summary>
    /// Test-fixture page art: a synthetic 4-panel manga-ish page drawn with SkiaSharp so the canvas
    /// screenshot shows a real decoded bitmap with panel geometry the Region overlay must match.
    /// This is fixture art for rendering evidence only — it never enters product data.
    /// </summary>
    public static byte[] CreateComicPage(int width = 1200, int height = 1660)
    {
        using var surface = SkiaSharp.SKSurface.Create(new SkiaSharp.SKImageInfo(width, height));
        var canvas = surface.Canvas;
        canvas.Clear(new SkiaSharp.SKColor(0xF2, 0xEF, 0xE8));
        var ink = new SkiaSharp.SKPaint { Color = new SkiaSharp.SKColor(0x1A, 0x1A, 0x1A), IsAntialias = true };
        var border = new SkiaSharp.SKPaint
        {
            Color = new SkiaSharp.SKColor(0x1A, 0x1A, 0x1A),
            Style = SkiaSharp.SKPaintStyle.Stroke,
            StrokeWidth = 4,
            IsAntialias = true,
        };
        var tone = new SkiaSharp.SKPaint { Color = new SkiaSharp.SKColor(0xC9, 0xC4, 0xB8), IsAntialias = true };
        var bubble = new SkiaSharp.SKPaint
        {
            Color = new SkiaSharp.SKColor(0xFF, 0xFF, 0xFF),
            Style = SkiaSharp.SKPaintStyle.Fill,
            IsAntialias = true,
        };

        var panels = new (float X, float Y, float W, float H)[]
        {
            (60, 60, 500, 420),
            (600, 60, 540, 420),
            (60, 520, 1080, 520),
            (60, 1080, 1080, 520),
        };
        canvas.DrawRect(20, 20, width - 40, height - 40, border);
        foreach (var (x, y, w, h) in panels)
        {
            canvas.DrawRect(x, y, w, h, tone);
            canvas.DrawRect(x, y, w, h, border);
            for (var line = 0; line < 4; line++)
            {
                canvas.DrawRect(x + 40, y + 40 + line * 34, w - 140, 14, ink);
            }
        }

        // Speech bubbles sitting on the panel seams (the overlay regions cover these areas).
        canvas.DrawOval(200, 200, 130, 90, bubble);
        canvas.DrawOval(200, 200, 130, 90, border);
        canvas.DrawOval(880, 260, 150, 100, bubble);
        canvas.DrawOval(880, 260, 150, 100, border);

        using var image = surface.Snapshot();
        using var data = image.Encode(SkiaSharp.SKEncodedImageFormat.Png, 92);
        return data.ToArray();
    }
    public static FakeHostController CreateHost(HostViewSnapshot? snapshot = null)
    {
        var host = new FakeHostController(snapshot ?? FakeHostController.ReadySnapshot("夜光列车"));
        host.ChaptersByBook["book-0"] = new[]
        {
            new ChapterSummary("ch-1", "第 1 章", "1", 0),
        };
        host.ChapterPagesByChapter["ch-1"] = new[]
        {
            new ChapterPageSummary("p1", "001.jpg", 0),
            new ChapterPageSummary("p2", "002.jpg", 1),
            new ChapterPageSummary("p3", "003.jpg", 2),
        };
        host.RegionsByPage["p1"] = new RegionPageProjection(
            new[]
            {
                new RegionSummary("region-1", "speech", "skip", "user", 3,
                    new RegionGeometrySummary(0.10, 0.10, 0.40, 0.20, Array.Empty<RegionGeometryPoint>())),
                new RegionSummary("region-2", "sfx", "translate", "machine", 1,
                    new RegionGeometrySummary(0.55, 0.30, 0.20, 0.15, Array.Empty<RegionGeometryPoint>())),
                new RegionSummary("region-3", "narration", "skip", "machine", 0,
                    new RegionGeometrySummary(0.20, 0.60, 0.50, 0.25, Array.Empty<RegionGeometryPoint>())),
            },
            new RegionPageSize(1200, 1660));
        host.PageImagesByPage["p1"] = CreateComicPage();
        host.RegionsByPage["p2"] = new RegionPageProjection(
            new[]
            {
                new RegionSummary("region-p2", "speech", "skip", "machine", 2,
                    new RegionGeometrySummary(0.15, 0.20, 0.30, 0.25, Array.Empty<RegionGeometryPoint>())),
            },
            new RegionPageSize(1200, 1660));
        host.PageImagesByPage["p2"] = CreateComicPage();
        host.RevisionsByRegion["region-1"] = new RegionRevisionHistory(
            "region-1",
            3,
            new[]
            {
                new RegionRevisionSummary("r1", 1, "machine", "unreviewed", false, null, "t1", "speech", "skip", false),
                new RegionRevisionSummary("r2", 2, "user", "needs_review", false, null, "t2", "narration", "skip", false),
                new RegionRevisionSummary("r3", 3, "user", "confirmed", false, null, "t3", "speech", "skip", true),
            });
        return host;
    }

    public static (StudioWorkspaceView View, FakeHostController Host, StudioWorkspaceViewModel ViewModel) Open(
        HostViewSnapshot? snapshot = null,
        int width = 1600,
        int height = 1000)
    {
        var host = CreateHost(snapshot);
        var viewModel = new StudioWorkspaceViewModel(host);
        var view = new StudioWorkspaceView(viewModel);
        var window = new Window
        {
            Content = view,
            Width = width,
            Height = height,
        };
        window.Show();
        Pump();
        return (view, host, viewModel);
    }

    public static void Pump() => Dispatcher.UIThread.RunJobs();

    public static void PumpUntil(Func<bool> condition, int timeoutMs = 5000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (!condition() && DateTime.UtcNow < deadline)
        {
            Pump();
            Thread.Sleep(5);
        }

        Pump();
    }

    public static void Click(Button button)
    {
        button.RaiseEvent(new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
        Pump();
    }

    public static Window WindowOf(Control control) => (Window)TopLevel.GetTopLevel(control)!;
}
