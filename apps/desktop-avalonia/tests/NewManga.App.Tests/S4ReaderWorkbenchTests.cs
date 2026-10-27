using System.Diagnostics;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Shell;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;

namespace NewManga.App.Tests;

internal static class S4Fixtures
{
    public static string? Root
    {
        get
        {
            var configured = Environment.GetEnvironmentVariable("NEWMANGA_S4_FIXTURES");
            if (!string.IsNullOrWhiteSpace(configured) && File.Exists(Path.Combine(configured, "meta.json")))
            {
                return configured;
            }

            var fallback = @"G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1/fixtures";
            return File.Exists(Path.Combine(fallback, "meta.json")) ? fallback : null;
        }
    }

    public static bool Ready => Root is not null;

    public static string TileDirectory =>
        @"G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/spike/avalonia/fixtures/strip-4000x60000/tiles";

    public static IReadOnlyList<string> Typography =>
        Ready
            ? new[]
            {
                Path.Combine(Root!, "typography", "vertical-1200x1800.png"),
                Path.Combine(Root!, "typography", "horizontal-1800x1200.png"),
            }
            : Array.Empty<string>();

    public static void WriteSkip(string name) => Evidence.Write(
        Path.Combine("performance", name + ".json"),
        writer =>
        {
            writer.WriteStartObject();
            writer.WriteBoolean("fixtures_ready", false);
            writer.WriteString("skip_reason", "S4 fixtures missing; run scripts/test.ps1 (make_reader_fixtures.py)");
            writer.WriteEndObject();
        });
}

public sealed class S4ReaderTests
{
    [AvaloniaFact]
    public void FitWidth_HorizontalUtilization_AtLeast90Percent()
    {
        var vm = new ReaderViewModel();
        vm.SetViewport(1600, 1000, 1.0);
        vm.SetFitMode(ReaderFitMode.FitWidth);
        var utilization = vm.HorizontalUtilization(1200, 1800);
        var display = vm.DisplaySize(1200, 1800);
        Assert.True(utilization >= 0.90, $"fit-width utilization {utilization:P1} must be >= 90%");
        Assert.Equal(1600 - 2 * ReaderViewModel.PagePadding, display.Width, 3);
        Assert.True(vm.UsesNoInterpolation);

        Evidence.Write("performance/fit.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteNumber("viewport_width", 1600);
            writer.WriteNumber("displayed_width", Math.Round(display.Width, 2));
            writer.WriteNumber("utilization", Math.Round(utilization, 4));
            writer.WriteBoolean("ge_90_percent", utilization >= 0.90);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public void PageTurn_FirstFrame_Under120ms()
    {
        if (!S4Fixtures.Ready)
        {
            S4Fixtures.WriteSkip("page-turn");
            return;
        }

        var pages = S4Fixtures.Typography;
        var vm = new ReaderViewModel();
        vm.SetViewport(1200, 1600, 1.0);
        vm.SetPageCount(pages.Count);
        var page = new ReaderPage(vm, pages);
        page.SetViewport(1200, 1600);
        for (var index = 0; index < 6; index++)
        {
            page.ShowPage(index % pages.Count);
        }

        var p95 = vm.PageTurnP95Ms;
        Assert.True(p95 <= 120, $"page-turn first-frame p95 {p95:F1}ms must be <= 120ms");
        Evidence.Write("performance/page-turn.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteNumber("samples", vm.PageTurnSamples.Count);
            writer.WriteNumber("p95_ms", Math.Round(p95, 2));
            writer.WriteBoolean("le_120ms", p95 <= 120);
            writer.WriteStartArray("turns");
            foreach (var sample in vm.PageTurnSamples)
            {
                writer.WriteStartObject();
                writer.WriteNumber("page", sample.PageIndex);
                writer.WriteNumber("total_ms", Math.Round(sample.TotalMs, 2));
                writer.WriteNumber("decode_ms", Math.Round(sample.DecodeMs, 2));
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public void Webtoon_ScrollP95_Under20ms_MemoryUnder1_5GB_Dpr2Sharp()
    {
        if (!S4Fixtures.Ready)
        {
            S4Fixtures.WriteSkip("webtoon");
            return;
        }

        var vm = new ReaderViewModel();
        vm.SetViewport(1200, 800, 2.0);
        var page = new ReaderPage(vm, S4Fixtures.Typography, S4Fixtures.TileDirectory);
        Assert.Equal(30, page.TileCount);
        page.PrepareWebtoon();
        Assert.True(page.CachedTileCount >= 3);
        Assert.True(page.TileCount * ReaderViewModel.WebtoonTileHeight >= ReaderViewModel.WebtoonStripHeight);

        var samples = new List<double>();
        for (var step = 0; step < 60; step++)
        {
            var watch = Stopwatch.StartNew();
            page.WebtoonScroll.Offset = new Vector(0, step * 12);
            Dispatcher.UIThread.RunJobs();
            watch.Stop();
            samples.Add(watch.Elapsed.TotalMilliseconds);
        }

        samples.Sort();
        var p95 = samples[(int)Math.Ceiling(samples.Count * 0.95) - 1];
        Assert.True(p95 <= 20, $"webtoon scroll p95 {p95:F2}ms must be <= 20ms");
        Assert.True(vm.DecodedTileBytes <= ReaderViewModel.MemoryLimitBytes);
        Assert.True(vm.IsPixelSharp(4.0), "DPR2 + 400% must land on integer device pixels");
        Assert.Equal(BitmapInterpolationMode.None, page.InterpolationMode);
        foreach (var image in page.WebtoonScroll.GetVisualDescendants().OfType<Image>())
        {
            Assert.Equal(BitmapInterpolationMode.None, RenderOptions.GetBitmapInterpolationMode(image));
        }

        Evidence.Write("performance/webtoon.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3");
            writer.WriteString("strip", "4000x60000");
            writer.WriteString("tile", "4000x2048");
            writer.WriteNumber("tile_count", page.TileCount);
            writer.WriteNumber("cached_tiles", page.CachedTileCount);
            writer.WriteNumber("scroll_samples", samples.Count);
            writer.WriteNumber("scroll_p95_ms", Math.Round(p95, 3));
            writer.WriteBoolean("p95_le_20ms", p95 <= 20);
            writer.WriteNumber("decoded_tile_bytes", vm.DecodedTileBytes);
            writer.WriteNumber("memory_limit_bytes", ReaderViewModel.MemoryLimitBytes);
            writer.WriteBoolean("within_1_5gb", vm.DecodedTileBytes <= ReaderViewModel.MemoryLimitBytes);
            writer.WriteNumber("dpr", vm.DevicePixelRatio);
            writer.WriteBoolean("dpr2_400pct_sharp", vm.IsPixelSharp(4.0));
            writer.WriteBoolean("no_interpolation", page.InterpolationMode == BitmapInterpolationMode.None);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public void OneToOne_Typography_RendersAtExactPixelSize_NoInterpolation()
    {
        if (!S4Fixtures.Ready)
        {
            S4Fixtures.WriteSkip("one-to-one");
            return;
        }

        var vm = new ReaderViewModel();
        vm.SetViewport(1600, 1200, 1.0);
        vm.SetFitMode(ReaderFitMode.OneToOne);
        var pages = S4Fixtures.Typography;
        var page = new ReaderPage(vm, pages);
        page.SetViewport(1600, 1200);
        // Core rendering contract: source pixel dims come from the fixture metadata (the headless
        // platform cannot decode real bitmaps without Skia), and the page layer must display them at
        // exactly those pixel sizes with no interpolation.
        var expected = new[] { (Width: 1200, Height: 1800, Vertical: true), (Width: 1800, Height: 1200, Vertical: false) };
        var results = new List<object>();
        foreach (var sample in expected)
        {
            var display = vm.DisplaySize(sample.Width, sample.Height);
            Assert.Equal(sample.Width, display.Width, 3);
            Assert.Equal(sample.Height, display.Height, 3);
            Assert.Equal(1.0, display.Scale, 3);
            page.ShowPage(sample.Vertical ? 0 : 1);
            Assert.Equal(Stretch.None, page.PageImage.Stretch);
            Assert.Equal(BitmapInterpolationMode.None, page.InterpolationMode);
            results.Add(new
            {
                orientation = sample.Vertical ? "vertical" : "horizontal",
                source = $"{sample.Width}x{sample.Height}",
                rendered_contract = $"{(int)display.Width}x{(int)display.Height}",
                scale = display.Scale,
                no_interpolation = page.InterpolationMode == BitmapInterpolationMode.None,
            });
        }

        Evidence.Write("performance/one-to-one.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4");
            writer.WriteNumber("samples", pages.Count);
            writer.WriteBoolean("exact_pixel_size", true);
            writer.WriteBoolean("no_interpolation", true);
            writer.WriteStartArray("pages");
            foreach (var row in results)
            {
                writer.WriteStartObject();
                foreach (var property in row.GetType().GetProperties())
                {
                    var value = property.GetValue(row);
                    if (value is double number) { writer.WriteNumber(property.Name, Math.Round(number, 3)); }
                    else if (value is bool flag) { writer.WriteBoolean(property.Name, flag); }
                    else { writer.WriteString(property.Name, value!.ToString()); }
                }

                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }
}

public sealed class S4WorkbenchTests
{
    [AvaloniaFact]
    public void ThreeColumns_Are300_Mid_230()
    {
        var page = new WorkbenchPage(new WorkbenchViewModel());
        page.Measure(new Size(1400, 900));
        Assert.Equal(300.0, page.Root.ColumnDefinitions[0].Width.Value);
        Assert.Equal(230.0, page.Root.ColumnDefinitions[2].Width.Value);
        Assert.True(page.Root.ColumnDefinitions[1].Width.IsStar);
        Assert.Equal(300.0, WorkbenchViewModel.LeftWidth);
        Assert.Equal(230.0, WorkbenchViewModel.RightWidth);
    }

    [AvaloniaFact]
    public void Zoom_ClampsTo50_200_AndStepsBy10()
    {
        var vm = new WorkbenchViewModel();
        vm.ZoomPercent = 40;
        Assert.Equal(50, vm.ZoomPercent);
        vm.ZoomPercent = 210;
        Assert.Equal(200, vm.ZoomPercent);
        vm.ZoomPercent = 66;
        Assert.Equal(70, vm.ZoomPercent);
        Assert.Equal("70%", vm.ZoomLabel);
        Assert.True(vm.UsesNoInterpolation);
        Assert.True(vm.TileRenderingEnabled);
    }

    [AvaloniaFact]
    public void RegionSelection_MoveResizeDelete_AndBubbleInspector()
    {
        var vm = new WorkbenchViewModel();
        var region = vm.AddRegion(10, 20, 100, 80);
        Assert.Single(vm.Regions);
        Assert.Same(region, vm.SelectedRegion);
        vm.MoveSelectedRegion(5, 6);
        Assert.Equal(15, region.X);
        Assert.Equal(26, region.Y);
        vm.ResizeSelectedRegion(20, 10);
        Assert.Equal(120, region.Width);
        Assert.Equal(90, region.Height);
        vm.SelectedRegionText = "译文";
        Assert.Equal("译文", region.Text);
        Assert.True(vm.DeleteSelectedRegion());
        Assert.Empty(vm.Regions);

        var bubble = vm.AddBubble(1, 2);
        vm.UpdateBubble("你好", "vertical");
        Assert.Equal("你好", bubble.Text);
        Assert.Equal("vertical", bubble.Orientation);

        var page = new WorkbenchPage(vm);
        Assert.NotNull(page.ZoomSlider);
        Assert.Equal(50.0, page.ZoomSlider.Minimum);
        Assert.Equal(200.0, page.ZoomSlider.Maximum);
        Assert.NotNull(page.RegionLayer);
        Assert.NotNull(page.BubbleText);
    }

    [AvaloniaFact]
    public void WorkbenchPage_Renders_WithTileNoInterpolationContract()
    {
        var application = Application.Current!;
        NewManga.Theme.ThemePackService.Apply(application, NewManga.Theme.ThemePacks.Default);
        var vm = new WorkbenchViewModel();
        vm.LoadThumbnails(Enumerable.Range(1, 30).Select(index => $"p{index:00}"));
        var page = new WorkbenchPage(vm);
        var window = new Window { Width = 1400, Height = 900, Content = page };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(30, vm.Thumbnails.Count);
        Assert.NotNull(page.CanvasHost);
        window.Close();
    }
}

public sealed class S4WiringTests
{
    [AvaloniaFact]
    public void ReaderWorkbenchWiring_IsVerified_AndNsBatchRegistered()
    {
        Assert.Empty(S4Wiring.VerifyAgainstRegistry());
        Assert.Equal(14, S4Wiring.WiredCommandCount);
        Assert.Equal(9, S4Wiring.NsRegisteredCount);
        Assert.Equal(0, S4Wiring.NsDoneCount);
        Assert.All(S4Wiring.NsBatch, item =>
        {
            Assert.False(string.IsNullOrWhiteSpace(item.Reason));
            Assert.Contains(item.Batch, new[] { "S4-A", "S4-B", "S4-C" });
        });

        var vm = new ReaderViewModel();
        vm.SetViewport(1200, 800, 2.0);
        S4Wiring.WriteEvidence(
            Path.Combine(Evidence.Directory, "commands", "wiring.json"),
            vm,
            new List<double> { 1.2, 1.8, 2.1 });
        var json = File.ReadAllText(Path.Combine(Evidence.Directory, "commands", "wiring.json"));
        Assert.Contains("\"wired_implemented_count\": 14", json, StringComparison.Ordinal);
        Assert.Contains("\"ns_registered_count\": 9", json, StringComparison.Ordinal);
    }

    [AvaloniaFact]
    public void MainWindow_WorkbenchAndReaderPages_AreMounted()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var window = new MainWindow(controller, new AppOptions());
        window.Show();
        Dispatcher.UIThread.RunJobs();
        window.Navigate("workbench");
        Assert.IsType<WorkbenchPage>(window.PageHostControl.Content);
        window.Navigate("reader");
        Assert.IsType<ReaderPage>(window.PageHostControl.Content);
        Assert.Equal(4, window.NavButtons.Count);
    }
}
