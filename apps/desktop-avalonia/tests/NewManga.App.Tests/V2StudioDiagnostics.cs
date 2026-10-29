using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.VisualTree;
using SkiaSharp;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Tests;

/// <summary>Temporary development diagnostics (removed before the V11R-B-3 handoff).</summary>
public sealed class V2StudioDiagnostics
{
    [AvaloniaFact]
    public async Task Dump()
    {
        var (view, host, vm) = StudioFixtures.Open();
        Assert.True(await view.LoadAndRenderAsync("book-0", "ch-1"));
        StudioFixtures.Pump();
        var window = StudioFixtures.WindowOf(view);
        var canvas = view.PageWorkspace.Canvas;
        var overlay = canvas.RegionOverlay;
        var boxes = overlay.Boxes.Select(box => new
        {
            id = box.Item.RegionId,
            bounds = box.Bounds.ToString(),
            border = (box.BorderBrush as ISolidColorBrush)?.Color.ToString() ?? "null",
            thickness = box.BorderThickness.ToString(),
            classes = string.Join(",", box.Classes),
            visible = box.IsVisible,
            parentIsOverlay = box.Parent == overlay,
        }).ToList();

        var tree = new List<string>();
        void Walk(Visual visual, int depth)
        {
            if (depth > 6)
            {
                return;
            }

            var type = visual.GetType().Name;
            var bounds = visual.Bounds.ToString();
            var background = visual is Border border ? (border.Background as ISolidColorBrush)?.Color.ToString() ?? "null" : "-";
            var borderBrush = visual is Border b2 ? (b2.BorderBrush as ISolidColorBrush)?.Color.ToString() ?? "null" : "-";
            tree.Add($"{new string(' ', depth * 2)}{type} [{bounds}] bg={background} border={borderBrush} classes={string.Join(',', ((Control)visual).Classes)}");
            foreach (var child in visual.GetVisualChildren())
            {
                Walk(child, depth + 1);
            }
        }
        Walk(canvas, 0);

        var frame = window.CaptureRenderedFrame()!;
        var framePath = StudioEvidence.File("V11R-B-3", "artifacts/diagnostics.png");
        frame.Save(framePath);
        var pixels = new List<string>();
        using (var decoded = SKBitmap.Decode(framePath))
        {
            foreach (var (x, y) in new[] { (100, 100), (700, 500), (1400, 500), (1580, 500), (700, 950) })
            {
                pixels.Add($"({x},{y})={decoded.GetPixel(x, y)}");
            }
        }

        // Crops for close inspection (toolbar + bottom band).
        using (var decoded = SKBitmap.Decode(framePath))
        {
            using var top = new SKBitmap(1200, 120);
            decoded.ExtractSubset(top, new SKRectI(0, 0, 1200, 120));
            using var topImage = SKImage.FromBitmap(top);
            using var topData = topImage.Encode(SKEncodedImageFormat.Png, 95);
            System.IO.File.WriteAllBytes(StudioEvidence.File("V11R-B-3", "artifacts/crop-top.png"), topData.ToArray());

            using var bottom = new SKBitmap(1200, 120);
            decoded.ExtractSubset(bottom, new SKRectI(0, 880, 1200, 1000));
            using var bottomImage = SKImage.FromBitmap(bottom);
            using var bottomData = bottomImage.Encode(SKEncodedImageFormat.Png, 95);
            System.IO.File.WriteAllBytes(StudioEvidence.File("V11R-B-3", "artifacts/crop-bottom.png"), bottomData.ToArray());
        }

        var widgets = new
        {
            zoomText = new { bounds = view.PageWorkspace.ZoomTextBlock.Bounds.ToString(), text = view.PageWorkspace.ZoomTextBlock.Text },
            statusText = new { bounds = view.PageWorkspace.StatusTextBlock.Bounds.ToString(), text = view.PageWorkspace.StatusTextBlock.Text },
            pipelineHeader = new { bounds = view.PageWorkspace.PipelineBand.HeaderText.Bounds.ToString(), text = view.PageWorkspace.PipelineBand.HeaderText.Text, visible = view.PageWorkspace.PipelineBand.HeaderText.IsVisible },
            pipelineToggle = new { bounds = view.PageWorkspace.PipelineBand.ToggleButton.Bounds.ToString(), content = view.PageWorkspace.PipelineBand.ToggleButton.Content?.ToString(), visible = view.PageWorkspace.PipelineBand.ToggleButton.IsVisible },
            pipelineBand = new { bounds = view.PageWorkspace.PipelineBand.Bounds.ToString() },
            trackStrip = new { bounds = view.PageWorkspace.TrackStrip.Bounds.ToString() },
            inspector = new { bounds = view.PageWorkspace.Inspector.Bounds.ToString(), rail = view.PageWorkspace.Inspector.Rail.Bounds.ToString() },
        };

        var payload = new
        {
            fallbackInjected = StudioFallbackTokens.WasInjected,
            pixels,
            widgets,
            tree,
            window = new { width = window.Width, height = window.Height },
            viewport = canvas.Bounds.ToString(),
            viewportSize = canvas.ViewportSize.ToString(),
            content = canvas.RenderedContentSize.ToString(),
            pageFrame = canvas.PageFrame.Bounds.ToString(),
            pageFrameBorder = (canvas.PageFrame.BorderBrush as ISolidColorBrush)?.Color.ToString() ?? "null",
            imageSource = canvas.PageImage.Source is Bitmap bitmap ? $"{bitmap.PixelSize}" : "null",
            offsetX = vm.Page.OffsetX,
            offsetY = vm.Page.OffsetY,
            zoom = vm.Page.Zoom,
            selected = vm.Page.SelectedRegion?.RegionId,
            hudVisible = vm.Page.HudVisible,
            boxes,
            tracks = view.PageWorkspace.TrackStrip.Tracks.Select(track => new { track.Key, track.Glyph, track.Detail }),
            notWired = vm.Page.BuildNotWiredInventory(),
        };

        StudioEvidence.Write("V11R-B-3", "artifacts/diagnostics.json", writer =>
        {
            JsonSerializer.Serialize(writer, payload, new JsonSerializerOptions { WriteIndented = true });
        });

           }
}
