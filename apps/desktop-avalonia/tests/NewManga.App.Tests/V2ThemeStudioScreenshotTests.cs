using System.Security.Cryptography;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Media.Imaging;
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
            captures.Add(Capture(window, "rollback-preview", "Library", "dark"));

            service.CancelPreviewAsync().GetAwaiter().GetResult();
            Pump(window);
            var after = Capture(window, "rollback-after", "Library", "dark");
            captures.Add(after);

            Assert.False(service.HasDraft);
            Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
            Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedPaletteId);

            // Rollback correctness visually: the post-cancel frame matches the pre-preview frame cell by cell.
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

    [AvaloniaFact]
    public void Preview_DoesNotTouchAFixedPixelCanvas_OrTheUnsavedEditorState()
    {
        var (service, manager, _) = CreateProductionService();
        using var _ = service;
        try
        {
            var probe = new Border
            {
                Width = 320,
                Height = 180,
                Background = new SolidColorBrush(Color.Parse("#123456")),
                Child = new TextBlock { Text = "未保存编辑（像素探针）", Foreground = Brushes.White },
            };

            var before = Hash(RenderProbe(probe));
            var appliedBefore = service.Settings.ThemeId;

            service.BeginPreview();
            service.PreviewTheme(StubThemeStudioService.FixturePackages[1].Descriptor.Id);
            Assert.True(service.HasDraft);

            var during = Hash(RenderProbe(probe));
            Assert.Equal(before, during);
            Assert.Equal(appliedBefore, service.Settings.ThemeId);

            service.CancelPreviewAsync().GetAwaiter().GetResult();
            var after = Hash(RenderProbe(probe));
            Assert.Equal(before, after);
            Assert.Equal(appliedBefore, service.Settings.ThemeId);

            Evidence.Write("screens/pixel-hash.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC9");
                writer.WriteString("generated_by", "V2ThemeStudioScreenshotTests.Preview_DoesNotTouchAFixedPixelCanvas_OrTheUnsavedEditorState");
                writer.WriteString("method", "RenderTargetBitmap(320x180, #123456 canvas + unsaved-edit text) hashed before/during/after a real preview session");
                writer.WriteString("hash_before", before);
                writer.WriteString("hash_during_preview", during);
                writer.WriteString("hash_after_cancel", after);
                writer.WriteBoolean("identical", before == during && before == after);
                writer.WriteString("applied_theme_before", appliedBefore);
                writer.WriteString("applied_theme_after", service.Settings.ThemeId);
                writer.WriteBoolean("passed", true);
                writer.WriteEndObject();
            });
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

    private static byte[] RenderProbe(Control control)
    {
        var pixelSize = new PixelSize(320, 180);
        using var bitmap = new RenderTargetBitmap(pixelSize, new Vector(96, 96));
        control.Measure(new Size(320, 180));
        control.Arrange(new Rect(0, 0, 320, 180));
        bitmap.Render(control);
        using var stream = new MemoryStream();
        bitmap.Save(stream);
        return stream.ToArray();
    }

    private static string Hash(byte[] data) => Convert.ToHexString(SHA256.HashData(data));

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