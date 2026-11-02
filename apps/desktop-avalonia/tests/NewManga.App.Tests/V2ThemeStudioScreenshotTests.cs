using System.Security.Cryptography;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Markup.Xaml.MarkupExtensions;
using Avalonia.Platform;
using NewManga.DesignSystem;
using System.Runtime.InteropServices;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.App.Views.V2.ThemeStudio;
using DesignSystemThemeManager = NewManga.DesignSystem.Theming.DesignSystemThemeManager;
using NewManga.ThemeEngine;
using SkiaSharp;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-C-2 headless visual evidence (THEME_STUDIO_SPEC AC12): real Skia-rendered frames of all seven
/// sections in dark and light, high-contrast key frames, the import-failure state, the editor dirty
/// state, the responsive 1280/1024 grid, and a cancel-rollback before/after pair.
///
/// <para>
/// The studio runs over the real engine service with the real <see cref="DesignSystemThemeLayerSink"/>, so
/// the frames show the actual application palette being swapped — not a mock. The only test double is the
/// user theme directory (temporary).
/// </para>
/// </summary>
public sealed class V2ThemeStudioScreenshotTests : IDisposable
{
    private const int Width = 1600;
    private const int Height = 1000;

    private readonly string _root = Path.Combine(
        Path.GetTempPath(),
        "nm-theme-studio-shots",
        Guid.NewGuid().ToString("N")[..10]);

    public V2ThemeStudioScreenshotTests() => Directory.CreateDirectory(_root);

    public void Dispose()
    {
        try
        {
            if (Directory.Exists(_root))
            {
                Directory.Delete(_root, recursive: true);
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            // best effort
        }
    }

    [AvaloniaFact]
    public void SevenSectionsInDarkAndLight_PlusHighContrastAndFailureStates_AreRealRenderedFrames()
    {
        var (service, manager, _) = CreateProductionService();
        using var _ = service;
        var captures = new List<CaptureInfo>();

        try
        {
            service.SetAppearanceAsync(AppearanceMode.Dark).GetAwaiter().GetResult();
            service.SetContrastAsync(ContrastMode.Standard).GetAwaiter().GetResult();

            var window = CreateWindow(service);
            var viewModel = (ThemeStudioViewModel)((Control)window.Content!).DataContext!;

            // ---- 7 sections × dark
            foreach (var section in ThemeStudioLabels.AllSections)
            {
                viewModel.SelectSection(section);
                Pump(window);
                captures.Add(Capture(window, $"studio-{Slug(section)}-dark", section.ToString(), "dark"));
            }

            // ---- import failure state (invalid package is blocked with per-item issues)
            viewModel.SelectSection(ThemeStudioSection.ImportExport);
            viewModel.ImportExport.InputJson = ThemePackageJson.Write(StubThemeStudioService.CreateIllegalFixture());
            viewModel.ImportExport.ValidateAsync().GetAwaiter().GetResult();
            Pump(window);
            Assert.False(viewModel.ImportExport.CanImport);
            Assert.True(viewModel.ImportExport.Issues.Count > 0);
            captures.Add(Capture(window, "import-failure-dark", "ImportExport", "dark", assertIssues: true));

            // ---- editor dirty state: live edit, scoped palette, unsaved marker
            viewModel.SelectSection(ThemeStudioSection.Editor);
            viewModel.Editor.SelectVariant(PaletteVariant.Dark);
            var firstRow = viewModel.Editor.ColorGroups[0].Rows[0];
            firstRow.HexValue = "#0A0C10";
            Pump(window);
            Assert.True(viewModel.HasDraft);
            captures.Add(Capture(window, "editor-dirty-dark", "Editor", "dark"));

            // ---- 7 sections × light
            viewModel.CancelAsync().GetAwaiter().GetResult();
            service.SetAppearanceAsync(AppearanceMode.Light).GetAwaiter().GetResult();
            foreach (var section in ThemeStudioLabels.AllSections)
            {
                viewModel.SelectSection(section);
                Pump(window);
                captures.Add(Capture(window, $"studio-{Slug(section)}-light", section.ToString(), "light"));
            }

            // ---- high contrast key frames
            service.SetContrastAsync(ContrastMode.High).GetAwaiter().GetResult();
            foreach (var section in new[] { ThemeStudioSection.Library, ThemeStudioSection.Preview, ThemeStudioSection.Editor })
            {
                viewModel.SelectSection(section);
                Pump(window);
                captures.Add(Capture(window, $"studio-{Slug(section)}-highcontrast", section.ToString(), "high-contrast"));
            }

            service.SetContrastAsync(ContrastMode.Standard).GetAwaiter().GetResult();
            service.SetAppearanceAsync(AppearanceMode.Dark).GetAwaiter().GetResult();
            Pump(window);

            // ---- cancel rollback pair (real application palette): identical frames after rollback
            viewModel.SelectSection(ThemeStudioSection.Library);
            Pump(window);
            var before = Capture(window, "rollback-before", "Library", "dark");
            captures.Add(before);

            service.BeginPreview();
            service.PreviewTheme(StubThemeStudioService.FixturePackages[0].Descriptor.Id);
            Pump(window);
            var previewFrame = Capture(window, "rollback-preview", "Library", "dark");
            captures.Add(previewFrame);

            service.CancelPreviewAsync().GetAwaiter().GetResult();
            Pump(window);
            var after = Capture(window, "rollback-after", "Library", "dark");
            captures.Add(after);

            Assert.False(service.HasDraft);
            Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
            Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedPaletteId);

            // Rollback correctness visually: the post-cancel frame matches the pre-preview frame cell by cell.
            // Review C2-P2-2 (P3 follow-up): the preview frame has to actually differ, otherwise "preview then
            // cancel restored the pixels" would only prove that nothing ever happened.
            var previewDiff = CellDifference(before.Signature, previewFrame.Signature);
            Assert.True(
                previewDiff >= 5,
                $"rollback-preview differs from rollback-before in only {previewDiff}/160 cells (preview was a no-op)");

            var cellDiff = CellDifference(before.Signature, after.Signature);
            Assert.True(
                cellDiff <= 3,
                $"rollback frames differ in {cellDiff}/160 cells (expected the applied theme to be restored)");

            // ---- responsive breakpoints: 1280 (3 columns) and 1024 (2 columns)
            foreach (var (width, columns) in new[] { (1280, 3), (1024, 2) })
            {
                window.Width = width;
                window.Height = Height;
                Pump(window);
                Pump(window);
                Assert.Equal(columns, viewModel.Library.ColumnCount);
                captures.Add(Capture(window, $"library-{width}", "Library", "dark", expectedWidth: width));
            }

            window.Close();

            // ---- assertions over every frame
            Assert.Equal(24, captures.Count);
            foreach (var capture in captures)
            {
                Assert.True(capture.Bytes > 4096, $"{capture.Name}: only {capture.Bytes} bytes (placeholder?)");
                Assert.True(capture.DistinctColors > 20, $"{capture.Name}: only {capture.DistinctColors} colours");
                Assert.True(capture.Width > 0 && capture.Height > 0, $"{capture.Name}: empty frame");
            }

            var darkLibrary = captures.Single(capture => capture.Name == "studio-library-dark");
            var lightLibrary = captures.Single(capture => capture.Name == "studio-library-light");
            Assert.NotEqual(darkLibrary.PrimaryBackground, lightLibrary.PrimaryBackground);
            Assert.True(CellDifference(darkLibrary.Signature, lightLibrary.Signature) >= 20);

            var highContrast = captures.Single(capture => capture.Name == "studio-library-highcontrast");
            // High contrast keeps the surface ladder (so the dominant background may equal the normal
            // palette) and strengthens strokes/text: the rendered frame still has to differ.
            Assert.NotEqual(lightLibrary.Sha256, highContrast.Sha256);
            Assert.True(CellDifference(lightLibrary.Signature, highContrast.Signature) >= 2);

            // Every section frame is structurally distinct (7 sections actually differ).
            for (var index = 0; index < ThemeStudioLabels.AllSections.Count - 1; index++)
            {
                var left = captures.Single(capture =>
                    capture.Name == $"studio-{Slug(ThemeStudioLabels.AllSections[index])}-dark");
                var right = captures.Single(capture =>
                    capture.Name == $"studio-{Slug(ThemeStudioLabels.AllSections[index + 1])}-dark");
                Assert.True(
                    CellDifference(left.Signature, right.Signature) >= 5,
                    $"{left.Name} and {right.Name} look structurally identical");
            }

            WriteEvidence(captures, service, manager);
        }
        finally
        {
            manager.RevertPalette();
        }
    }

    /// <summary>
    /// AC9 evidence, honest by construction (review C2-P2-2): the probe lives in the <b>real window</b> next to
    /// the Studio surface and is mixed:
    /// <list type="bullet">
    ///   <item>a Border whose background is a <c>{DynamicResource Nm.Color.Accent.Base}</c> binding — it must
    ///   change when the appearance or the previewed theme changes (positive control, fails the test otherwise);</item>
    ///   <item>a <see cref="WriteableBitmap"/> rendered as a document page — its pixels must not move by a single
    ///   byte while the app-wide theme layer is swapped (the "canvas" half of AC9).</item>
    /// </list>
    /// Every value written to <c>pixel-hash.json</c> is derived from those comparisons, never assumed.
    /// </summary>
    [AvaloniaFact]
    public void Preview_ChangesDynamicResourceProbe_ButLeavesCanvasPixelsUntouched_AndCancelRestores()
    {
        var (service, manager, _) = CreateProductionService();
        using var _ = service;
        try
        {
            service.SetAppearanceAsync(AppearanceMode.Dark).GetAwaiter().GetResult();

            var accentPackage = BuildAccentProbePackage();
            var validation = service.ValidatePackage(accentPackage);
            Assert.True(
                validation.IsValid,
                string.Join(" | ", validation.Issues.Select(issue => issue.Message)));

            var import = service.ImportAsync(
                    ThemePackageJson.Write(accentPackage),
                    accentPackage.Descriptor.Id + ".nmtheme")
                .GetAwaiter().GetResult();
            Assert.True(import.Success, import.Message);

            var probeWindow = CreateProbeWindow(service);
            var window = probeWindow.Window;
            try
            {
                var baseline = CaptureProbe(window, probeWindow.AccentRect, probeWindow.CanvasRect, "baseline");
                Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedPaletteId);

                // Positive control 1: switching appearance must repaint the DynamicResource probe.
                service.SetAppearanceAsync(AppearanceMode.Light).GetAwaiter().GetResult();
                var light = CaptureProbe(window, probeWindow.AccentRect, probeWindow.CanvasRect, "appearance-light");
                Assert.NotEqual(baseline.AccentHash, light.AccentHash);
                Assert.Equal(baseline.CanvasHash, light.CanvasHash);

                service.SetAppearanceAsync(AppearanceMode.Dark).GetAwaiter().GetResult();
                var darkRestored = CaptureProbe(window, probeWindow.AccentRect, probeWindow.CanvasRect, "appearance-dark");
                Assert.Equal(baseline.AccentHash, darkRestored.AccentHash);

                // Positive control 2: the previewed theme carries a different accent, so the probe must react.
                service.BeginPreview();
                service.PreviewTheme(accentPackage.Descriptor.Id);
                Assert.Equal(accentPackage.Descriptor.Id, manager.AppliedPaletteId);
                var preview = CaptureProbe(window, probeWindow.AccentRect, probeWindow.CanvasRect, "preview");
                Assert.NotEqual(baseline.AccentHash, preview.AccentHash);
                Assert.True(
                    CellDifference(baseline.Signature, preview.Signature) >= 5,
                    "the preview did not change any window pixels: the probe would be tautological");
                Assert.Equal(baseline.CanvasHash, preview.CanvasHash);

                // Cancel must restore both the app-wide palette and the probe pixels, and keep the canvas stable.
                service.CancelPreviewAsync().GetAwaiter().GetResult();
                Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedPaletteId);
                var afterCancel = CaptureProbe(window, probeWindow.AccentRect, probeWindow.CanvasRect, "after-cancel");
                Assert.Equal(baseline.AccentHash, afterCancel.AccentHash);
                Assert.Equal(baseline.CanvasHash, afterCancel.CanvasHash);
                var fullFrameDifference = CellDifference(baseline.Signature, afterCancel.Signature);
                Assert.True(fullFrameDifference <= 3, $"post-cancel window differs in {fullFrameDifference}/160 cells");

                var checks = new (string Key, bool Ok)[]
                {
                    ("dynamic_resource_probe_reacts_to_appearance", baseline.AccentHash != light.AccentHash),
                    ("canvas_region_stable_through_appearance", baseline.CanvasHash == light.CanvasHash),
                    ("appearance_dark_restores_probe", baseline.AccentHash == darkRestored.AccentHash),
                    ("dynamic_resource_probe_reacts_to_theme_preview", baseline.AccentHash != preview.AccentHash),
                    ("full_frame_changed_by_preview", CellDifference(baseline.Signature, preview.Signature) >= 5),
                    ("canvas_region_stable_through_preview", baseline.CanvasHash == preview.CanvasHash),
                    ("cancel_restores_probe_pixels", baseline.AccentHash == afterCancel.AccentHash),
                    ("cancel_restores_canvas_pixels", baseline.CanvasHash == afterCancel.CanvasHash),
                    ("cancel_restores_full_frame", fullFrameDifference <= 3),
                };
                var passed = checks.All(check => check.Ok);
                Assert.True(
                    passed,
                    "probe checks failed: " + string.Join(", ", checks.Where(check => !check.Ok).Select(check => check.Key)));

                Evidence.Write("screens/pixel-hash.json", writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("ac", "AC9");
                    writer.WriteString(
                        "generated_by",
                        "V2ThemeStudioScreenshotTests.Preview_ChangesDynamicResourceProbe_ButLeavesCanvasPixelsUntouched_AndCancelRestores");
                    writer.WriteString(
                        "method",
                        "real window (Studio surface + mixed probe strip): accent Border bound with {DynamicResource Nm.Color.Accent.Base} + WriteableBitmap document canvas; frames captured with Window.CaptureRenderedFrame and region-hashed");
                    writer.WriteString("service", "ThemeEngineThemeStudioService.CreateProduction (real ThemeService + DesignSystemThemeLayerSink)");
                    writer.WriteNumber("window_width", (int)window.Width);
                    writer.WriteNumber("window_height", (int)window.Height);
                    writer.WriteStartObject("regions");
                    WriteRect(writer, "accent_probe", probeWindow.AccentRect);
                    WriteRect(writer, "document_canvas", probeWindow.CanvasRect);
                    writer.WriteEndObject();

                    writer.WriteStartObject("applied_palette");
                    writer.WriteString("baseline", ThemeDefaults.DefaultThemeId);
                    writer.WriteString("preview", accentPackage.Descriptor.Id);
                    writer.WriteString("after_cancel", ThemeDefaults.DefaultThemeId);
                    writer.WriteEndObject();

                    writer.WriteStartArray("steps");
                    WriteStep(writer, baseline);
                    WriteStep(writer, light);
                    WriteStep(writer, darkRestored);
                    WriteStep(writer, preview);
                    WriteStep(writer, afterCancel);
                    writer.WriteEndArray();

                    writer.WriteStartObject("checks");
                    foreach (var check in checks)
                    {
                        writer.WriteBoolean(check.Key, check.Ok);
                    }

                    writer.WriteNumber("full_frame_cell_difference_after_cancel", fullFrameDifference);
                    writer.WriteEndObject();
                    writer.WriteBoolean("passed", passed);
                    writer.WriteEndObject();
                });
            }
            finally
            {
                window.Close();
            }
        }
        finally
        {
            manager.RevertPalette();
        }
    }

    // ---------------------------------------------------------------- helpers

    private sealed record CaptureInfo(
        string Name,
        string Path,
        int Width,
        int Height,
        long Bytes,
        string Sha256,
        int DistinctColors,
        string PrimaryBackground,
        int[] Signature,
        string Section,
        string Variant);

    private (ThemeEngineThemeStudioService Service, DesignSystemThemeManager Manager, Application Application) CreateProductionService()
    {
        var themeDirectory = Path.Combine(_root, "themes");
        Directory.CreateDirectory(themeDirectory);
        foreach (var fixture in StubThemeStudioService.FixturePackages)
        {
            File.WriteAllText(
                Path.Combine(themeDirectory, fixture.Descriptor.Id + ThemeDefaults.ThemeFileExtension),
                ThemePackageJson.Write(fixture));
        }

        var application = Application.Current ?? throw new InvalidOperationException("headless Avalonia application is required");
        var manager = new DesignSystemThemeManager(application);
        manager.Initialize();
        var service = ThemeEngineThemeStudioService.CreateProduction(
            application,
            manager,
            themeDirectory,
            Path.Combine(_root, "theme-settings.json"),
            Path.Combine(_root, "favorites.json"));
        service.InitializeAsync().GetAwaiter().GetResult();
        return (service, manager, application);
    }

    private static Window CreateWindow(ThemeEngineThemeStudioService service)
    {
        var viewModel = new ThemeStudioViewModel(service);
        viewModel.OpenAsync(ThemeStudioSection.Library).GetAwaiter().GetResult();
        var view = new ThemeStudioView(viewModel);
        var window = new Window
        {
            Width = Width,
            Height = Height,
            Content = view,
        };
        window.Show();
        Pump(window);
        Pump(window);
        return window;
    }

    /// <summary>Extra pump for bindings/layout that are scheduled after a VM transition.</summary>
    private static void Pump(Window window)
    {
        for (var i = 0; i < 4; i++)
        {
            Dispatcher.UIThread.RunJobs();
            window.UpdateLayout();
        }
    }

    private CaptureInfo Capture(
        Window window,
        string name,
        string section,
        string variant,
        int expectedWidth = Width,
        bool assertIssues = false)
    {
        Pump(window);
        var directory = Path.Combine(Evidence.Directory, "screens");
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, name + ".png");
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException($"{name}: CaptureRenderedFrame returned null");
        frame.Save(path);
        var bytes = new FileInfo(path).Length;

        using var bitmap = SKBitmap.Decode(path) ?? throw new InvalidOperationException($"{name}: PNG decode failed");
        var distinct = new HashSet<uint>();
        var counts = new Dictionary<uint, int>();
        var signature = new int[160];
        for (var y = 0; y < bitmap.Height; y += 5)
        {
            for (var x = 0; x < bitmap.Width; x += 5)
            {
                var pixel = bitmap.GetPixel(x, y);
                var color = (uint)((pixel.Red << 16) | (pixel.Green << 8) | pixel.Blue);
                distinct.Add(color);
                counts[color] = counts.TryGetValue(color, out var count) ? count + 1 : 1;

                var cellX = Math.Min(15, x * 16 / Math.Max(1, bitmap.Width));
                var cellY = Math.Min(9, y * 10 / Math.Max(1, bitmap.Height));
                signature[cellY * 16 + cellX] += (int)(color & 0x7F);
            }
        }

        var primary = counts.OrderByDescending(pair => pair.Value).First().Key;
        var sha = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
        Assert.True(bitmap.Width >= expectedWidth - 1 && bitmap.Width <= expectedWidth + 1, $"{name}: width {bitmap.Width} != {expectedWidth}");
        if (assertIssues)
        {
            Assert.True(File.Exists(path));
        }

        return new CaptureInfo(
            name,
            path,
            bitmap.Width,
            bitmap.Height,
            bytes,
            sha,
            distinct.Count,
            $"#{primary:X6}",
            signature,
            section,
            variant);
    }

    private static int CellDifference(int[] left, int[] right)
    {
        var different = 0;
        for (var i = 0; i < left.Length; i++)
        {
            if (Math.Abs(left[i] - right[i]) > 40)
            {
                different++;
            }
        }

        return different;
    }

    private sealed record ProbeWindow(Window Window, PixelRect AccentRect, PixelRect CanvasRect);

    private sealed record ProbeHashes(
        string Name,
        string FullHash,
        string AccentHash,
        string CanvasHash,
        int[] Signature);

    /// <summary>
    /// Builds the real probe window: the Studio surface on the left (so the app-wide layer swap has real UI to
    /// repaint) and, on the right, an accent Border bound through <c>DynamicResource</c> plus a WriteableBitmap
    /// document page. Geometry here is test-harness only (not product UI, not scanned by conformance).
    /// </summary>
    private static ProbeWindow CreateProbeWindow(ThemeEngineThemeStudioService service)
    {
        var viewModel = new ThemeStudioViewModel(service);
        viewModel.OpenAsync(ThemeStudioSection.Library).GetAwaiter().GetResult();
        var studioView = new ThemeStudioView(viewModel);

        var accentProbe = new Border { Width = 180, Height = 90 };
        accentProbe.Bind(Border.BackgroundProperty, new DynamicResourceExtension("Nm.Color.Accent.Base"));

        var canvas = new Image { Width = 180, Height = 90, Source = CreateDocumentBitmap(180, 90) };

        var strip = new StackPanel
        {
            Spacing = 6,
            Margin = new Thickness(8),
            Children =
            {
                new TextBlock { Text = "主题敏感探针（DynamicResource）" },
                accentProbe,
                new TextBlock { Text = "文档画布（页面位图）" },
                canvas,
            },
        };

        var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        grid.Children.Add(studioView);
        Grid.SetColumn(strip, 1);
        grid.Children.Add(strip);

        var window = new Window
        {
            Width = 1820,
            Height = 1000,
            Content = grid,
        };
        window.Show();
        Pump(window);
        Pump(window);

        return new ProbeWindow(window, ToPixelRect(accentProbe, window), ToPixelRect(canvas, window));
    }

    private static PixelRect ToPixelRect(Control control, Window window)
    {
        var scale = window.RenderScaling;
        var topLeft = control.TranslatePoint(new Point(0, 0), window) ?? new Point(0, 0);
        return new PixelRect(
            (int)Math.Round(topLeft.X * scale),
            (int)Math.Round(topLeft.Y * scale),
            (int)Math.Round(control.Bounds.Width * scale),
            (int)Math.Round(control.Bounds.Height * scale));
    }

    private static ProbeHashes CaptureProbe(
        Window window,
        PixelRect accentRect,
        PixelRect canvasRect,
        string name)
    {
        Pump(window);
        var directory = Path.Combine(Evidence.Directory, "screens");
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, "probe-" + name + ".png");
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException($"{name}: CaptureRenderedFrame returned null");
        frame.Save(path);

        using var bitmap = SKBitmap.Decode(path) ?? throw new InvalidOperationException($"{name}: PNG decode failed");
        var accentHash = HashPixels(bitmap, accentRect);
        var canvasHash = HashPixels(bitmap, canvasRect);
        var fullHash = HashPixels(bitmap, new PixelRect(0, 0, bitmap.Width, bitmap.Height));

        var signature = new int[160];
        for (var y = 0; y < bitmap.Height; y += 5)
        {
            for (var x = 0; x < bitmap.Width; x += 5)
            {
                var pixel = bitmap.GetPixel(x, y);
                var cellX = Math.Min(15, x * 16 / Math.Max(1, bitmap.Width));
                var cellY = Math.Min(9, y * 10 / Math.Max(1, bitmap.Height));
                signature[cellY * 16 + cellX] += (int)(((uint)pixel.Red << 16 | (uint)pixel.Green << 8 | pixel.Blue) & 0x7F);
            }
        }

        return new ProbeHashes(name, fullHash, accentHash, canvasHash, signature);
    }

    private static string HashPixels(SKBitmap bitmap, PixelRect rect)
    {
        var left = Math.Max(0, rect.X);
        var top = Math.Max(0, rect.Y);
        var width = Math.Min(rect.Width, bitmap.Width - left);
        var height = Math.Min(rect.Height, bitmap.Height - top);
        if (width <= 0 || height <= 0)
        {
            throw new InvalidOperationException($"probe region {rect} is outside the frame ({bitmap.Width}x{bitmap.Height})");
        }

        var bytes = new byte[width * height * 4];
        var index = 0;
        for (var y = 0; y < height; y++)
        {
            for (var x = 0; x < width; x++)
            {
                var pixel = bitmap.GetPixel(left + x, top + y);
                bytes[index++] = pixel.Blue;
                bytes[index++] = pixel.Green;
                bytes[index++] = pixel.Red;
                bytes[index++] = pixel.Alpha;
            }
        }

        return Convert.ToHexString(SHA256.HashData(bytes));
    }

    private static void WriteRect(Utf8JsonWriter writer, string name, PixelRect rect)
    {
        writer.WriteStartObject(name);
        writer.WriteNumber("x", rect.X);
        writer.WriteNumber("y", rect.Y);
        writer.WriteNumber("width", rect.Width);
        writer.WriteNumber("height", rect.Height);
        writer.WriteEndObject();
    }

    private static void WriteStep(Utf8JsonWriter writer, ProbeHashes step)
    {
        writer.WriteStartObject();
        writer.WriteString("name", step.Name);
        writer.WriteString("full_frame_sha256", step.FullHash);
        writer.WriteString("accent_probe_sha256", step.AccentHash);
        writer.WriteString("document_canvas_sha256", step.CanvasHash);
        writer.WriteStartArray("signature_cells");
        foreach (var value in step.Signature)
        {
            writer.WriteNumberValue(value);
        }

        writer.WriteEndArray();
        writer.WriteEndObject();
    }

    /// <summary>A fixed document page (white paper, black text bars, one accent block) as a real bitmap source.</summary>
    private static WriteableBitmap CreateDocumentBitmap(int width, int height)
    {
        var bitmap = new WriteableBitmap(new PixelSize(width, height), new Vector(96, 96), PixelFormat.Bgra8888, AlphaFormat.Premul);
        var bytes = new byte[width * height * 4];
        for (var i = 0; i < bytes.Length; i += 4)
        {
            bytes[i] = 0xFF;
            bytes[i + 1] = 0xFF;
            bytes[i + 2] = 0xFF;
            bytes[i + 3] = 0xFF;
        }

        void Fill(int x0, int y0, int w, int h, byte b, byte g, byte r)
        {
            for (var y = y0; y < Math.Min(height, y0 + h); y++)
            {
                for (var x = x0; x < Math.Min(width, x0 + w); x++)
                {
                    var index = ((y * width) + x) * 4;
                    bytes[index] = b;
                    bytes[index + 1] = g;
                    bytes[index + 2] = r;
                }
            }
        }

        // page margin + text bars (document content: theme-independent by definition)
        for (var line = 0; line < 7; line++)
        {
            var w = line % 3 == 2 ? width - 60 : width - 30;
            Fill(15, 12 + (line * 11), w, 5, 0x30, 0x30, 0x30);
        }

        Fill(15, height - 35, width - 30, 20, 0xA0, 0x50, 0x20); // ink-coloured figure block
        using var buffer = bitmap.Lock();
        Marshal.Copy(bytes, 0, buffer.Address, bytes.Length);
        return bitmap;
    }

    /// <summary>
    /// The previewed probe theme: the built-in default with a different accent in both variants. Kept close to the
    /// default luminance so the engine validator still accepts every contrast floor (asserted by the caller).
    /// </summary>
    private static ThemePackage BuildAccentProbePackage()
    {
        var baseline = BuiltInThemes.Default;
        return baseline with
        {
            Descriptor = baseline.Descriptor with
            {
                Id = "c2-accent-probe",
                Name = "C2 强调色探针",
                Kind = ThemeKind.User,
                Author = "C2 evidence",
            },
            Dark = WithAccent(baseline.Dark, "#7FA9F5"),
            Light = WithAccent(baseline.Light, "#2F6FD0"),
        };
    }

    private static ThemeTokenSet WithAccent(ThemeTokenSet tokens, string accent)
    {
        var colors = new Dictionary<string, string>(tokens.Colors, StringComparer.Ordinal)
        {
            [NmKeys.Color.Accent.Base] = accent,
        };
        return tokens with { Colors = colors };
    }

    private static string Slug(ThemeStudioSection section) => section switch
    {
        ThemeStudioSection.Library => "library",
        ThemeStudioSection.Preview => "preview",
        ThemeStudioSection.MyThemes => "mythemes",
        ThemeStudioSection.Editor => "editor",
        ThemeStudioSection.Appearance => "appearance",
        ThemeStudioSection.ImportExport => "importexport",
        _ => "reset",
    };

    private static void WriteEvidence(
        IReadOnlyList<CaptureInfo> captures,
        ThemeEngineThemeStudioService service,
        DesignSystemThemeManager manager)
    {
        Evidence.Write("screens/screens.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC12");
            writer.WriteString("generated_by", "V2ThemeStudioScreenshotTests.SevenSectionsInDarkAndLight_PlusHighContrastAndFailureStates_AreRealRenderedFrames");
            writer.WriteString("renderer", "Avalonia.Headless + Skia (UseHeadlessDrawing=false) Window.CaptureRenderedFrame()");
            writer.WriteString("service", "ThemeEngineThemeStudioService.CreateProduction (real ThemeService + DesignSystemThemeLayerSink)");
            writer.WriteString("applied_palette_id", manager.AppliedPaletteId ?? string.Empty);
            writer.WriteString("applied_theme", service.CurrentTheme.Id);
            writer.WriteString("applied_appearance", service.Settings.Appearance.ToString());
            writer.WriteNumber("width", Width);
            writer.WriteNumber("height", Height);
            writer.WriteNumber("captures_total", captures.Count);
            writer.WriteStartObject("rollback");
            writer.WriteNumber(
                "preview_vs_before_cell_difference",
                CellDifference(
                    captures.Single(capture => capture.Name == "rollback-before").Signature,
                    captures.Single(capture => capture.Name == "rollback-preview").Signature));
            writer.WriteNumber(
                "after_vs_before_cell_difference",
                CellDifference(
                    captures.Single(capture => capture.Name == "rollback-before").Signature,
                    captures.Single(capture => capture.Name == "rollback-after").Signature));
            writer.WriteEndObject();
            writer.WriteStartArray("captures");
            foreach (var capture in captures)
            {
                writer.WriteStartObject();
                writer.WriteString("name", capture.Name);
                writer.WriteString("path", "screens/" + capture.Name + ".png");
                writer.WriteString("section", capture.Section);
                writer.WriteString("variant", capture.Variant);
                writer.WriteNumber("width", capture.Width);
                writer.WriteNumber("height", capture.Height);
                writer.WriteNumber("bytes", capture.Bytes);
                writer.WriteString("sha256", capture.Sha256);
                writer.WriteNumber("distinct_colors", capture.DistinctColors);
                writer.WriteString("primary_background", capture.PrimaryBackground);
                writer.WriteStartArray("signature_cells");
                foreach (var value in capture.Signature)
                {
                    writer.WriteNumberValue(value);
                }

                writer.WriteEndArray();
                writer.WriteBoolean("pass", true);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }
}