using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Shell.V2;
using NewManga.App.Views.Fluent;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Controls;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-2 IN-2B: opt-in raster evidence for the frozen component/state inventory.
/// The default run renders every frame and asserts it is non-empty but writes nothing; only
/// NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1 writes verification/FEA-06-RESIDUAL-2/visuals/** and its
/// visual-inventory.md. Light/dark are applied through AppearanceCoordinator (the product token
/// path), not by flipping RequestedThemeVariant. Pinned verification/FEA-06/screens/** is never touched.
/// </summary>
public sealed class FluentResidual2VisualEvidenceTests
{
    private const string CaptureEnv = "NEWMANGA_CAPTURE_RESIDUAL2_PNGS";

    [AvaloniaFact]
    public async Task Captures_Residual2_Visual_Inventory_Only_When_Opted_In()
    {
        var repositoryRoot = RepositoryRoot();
        var shots = new List<(string Group, string Name, string State, string Mode, string Theme, Avalonia.Media.Imaging.Bitmap Frame)>();

        foreach (var theme in new[] { "light", "dark" })
        {
            var tempRoot = Path.Combine(Path.GetTempPath(), "residual2-visual-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(tempRoot);
            var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(tempRoot, AppearanceStore.FileName)));
            appearance.Reload();
            await appearance.SaveAsync(AppearanceDefaults.Settings with
            {
                Mode = theme == "dark" ? AppearanceMode.Dark : AppearanceMode.Light,
                MotionMode = MotionMode.Full,
                MotionCategories = MotionCategories.All,
            });

            var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga"));
            var shell = FluentShell.CreateRoot(
                selection: FrontendSelector.Select("builtin.fluent", null),
                host: host,
                appearance: appearance);
            shell.Show();
            Dispatcher.UIThread.RunJobs();
            try
            {
                shots.AddRange(CapturePages(shell, theme));
                shots.AddRange(CaptureComponents(theme));
            }
            finally
            {
                shell.Close();
                Dispatcher.UIThread.RunJobs();
                try { Directory.Delete(tempRoot, recursive: true); } catch (IOException) { }
            }
        }

        Assert.All(shots, shot => Assert.True(
            shot.Frame.PixelSize.Width > 0 && shot.Frame.PixelSize.Height > 0,
            $"empty rendered frame: {shot.Name}/{shot.State}/{shot.Mode}/{shot.Theme}"));

        var captureEnabled = string.Equals(
            Environment.GetEnvironmentVariable(CaptureEnv), "1", StringComparison.OrdinalIgnoreCase);
        if (captureEnabled)
        {
            var output = Path.Combine(repositoryRoot, "verification", "FEA-06-RESIDUAL-2", "visuals");
            Directory.CreateDirectory(output);
            Assert.DoesNotContain(
                Path.Combine("verification", "FEA-06", "screens"), output, StringComparison.OrdinalIgnoreCase);

            var rows = new List<string>
            {
                "| file | group | component/page | state | mode | viewport | theme | frame | command | EXIT | signed_by | signed_at |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|",
            };
            foreach (var shot in shots)
            {
                var file = $"{shot.Group}--{shot.Name}--{shot.State}--{shot.Mode}--{shot.Theme}.png";
                shot.Frame.Save(Path.Combine(output, file));
                Assert.True(new FileInfo(Path.Combine(output, file)).Length > 0, $"missing screenshot: {file}");
                var size = shot.Frame.PixelSize;
                rows.Add($"| `{file}` | {shot.Group} | {shot.Name} | {shot.State} | {shot.Mode} | {size.Width}x{size.Height} | {shot.Theme} | mid | `dotnet test --filter FullyQualifiedName~FluentResidual2VisualEvidenceTests` | 0 | (待独立 Reviewer) | — |");
            }

            File.WriteAllText(Path.Combine(output, "visual-inventory.md"), string.Join(Environment.NewLine, rows));
        }

        foreach (var shot in shots)
        {
            shot.Frame.Dispose();
        }
    }

    private static IEnumerable<(string, string, string, string, string, Avalonia.Media.Imaging.Bitmap)> CapturePages(FluentShell shell, string theme)
    {
        var frames = new List<(string, string, string, string, string, Avalonia.Media.Imaging.Bitmap)>
        {
            ("pages", "shelf", "default", "full", theme, Capture(shell, FluentPage.Library)),
            ("pages", "workbench", "default", "full", theme, Capture(shell, FluentPage.Workbench)),
        };
        shell.ReaderViewModel.LoadAsync("book-0", "chapter-0").GetAwaiter().GetResult();
        frames.Add(("pages", "reader", "default", "full", theme, Capture(shell, FluentPage.Reader)));
        shell.SettingsViewModel.LoadAsync().GetAwaiter().GetResult();
        frames.Add(("pages", "settings", "default", "full", theme, Capture(shell, FluentPage.Settings)));
        return frames;
    }

    private static IEnumerable<(string, string, string, string, string, Avalonia.Media.Imaging.Bitmap)> CaptureComponents(string theme)
    {
        var cases = new List<(string Name, string State, Control Control, int W, int H)>
        {
            ("surface-card", "default", new SurfaceCard { Width = 200, Height = 90 }, 280, 140),
            ("surface-card", "disabled", new SurfaceCard { Width = 200, Height = 90, IsEnabled = false }, 280, 140),
            ("book-card", "default", new BookCard { Content = "作品", Width = 160, Height = 72 }, 220, 120),
            ("book-card", "disabled", new BookCard { Content = "作品", Width = 160, Height = 72, IsEnabled = false }, 220, 120),
            ("book-row", "default", new BookRow { Content = "作品行", Width = 240, Height = 36 }, 300, 90),
            ("book-row", "disabled", new BookRow { Content = "作品行", Width = 240, Height = 36, IsEnabled = false }, 300, 90),
            ("primary-button", "default", new Button { Content = "主操作", Classes = { "fluent-primary" }, Width = 120 }, 200, 80),
            ("primary-button", "disabled", new Button { Content = "主操作", Classes = { "fluent-primary" }, Width = 120, IsEnabled = false }, 200, 80),
            ("secondary-button", "default", new Button { Content = "次操作", Classes = { "fluent-secondary" }, Width = 120 }, 200, 80),
            ("danger-button", "default", new Button { Content = "危险", Classes = { "fluent-danger" }, Width = 120 }, 200, 80),
            ("icon-button", "default", new Button { Content = "图标", Width = 40 }, 90, 80),
            ("toggle-switch", "disabled", new ToggleSwitch { IsEnabled = false, Width = 80 }, 140, 70),
            ("slider", "default", new Slider { Width = 160, Value = 40 }, 220, 80),
            ("slider", "disabled", new Slider { Width = 160, Value = 40, IsEnabled = false }, 220, 80),
            ("region-box", "default", new RegionBox { Width = 140, Height = 70, Child = new TextBlock { Text = "region" } }, 200, 110),
            ("reader-progress", "default", new ReaderProgressBar { Width = 240, Height = 24 }, 300, 70),
            ("chapter-list", "default", new ChapterList { Width = 220, Children = { new TextBlock { Text = "第 1 章" } } }, 280, 120),
            ("page-thumb-strip", "default", new PageThumbStrip { Width = 240, Height = 60 }, 300, 120),
            ("empty-state", "default", new EmptyState { Width = 240, Height = 120 }, 300, 180),
        };

        foreach (var item in cases)
        {
            yield return ("components", item.Name, item.State, "full", theme, Render(item.Control, item.W, item.H));
        }
    }

    private static Avalonia.Media.Imaging.Bitmap Capture(FluentShell shell, FluentPage page)
    {
        shell.Navigate(page);
        Dispatcher.UIThread.RunJobs();
        return shell.CaptureRenderedFrame() ?? throw new InvalidOperationException($"frame capture failed: {page}");
    }

    private static Avalonia.Media.Imaging.Bitmap Render(Control content, int width, int height)
    {
        var window = new Window { Width = width, Height = height, Content = content };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        try
        {
            return window.CaptureRenderedFrame() ?? throw new InvalidOperationException("frame capture failed");
        }
        finally
        {
            window.Close();
        }
    }

    private static string RepositoryRoot()
    {
        var cursor = new DirectoryInfo(AppContext.BaseDirectory);
        while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc", "tasks", "FEA-06-RESIDUAL-2.md")))
        {
            cursor = cursor.Parent;
        }

        return cursor?.FullName ?? throw new DirectoryNotFoundException("repository root not found");
    }
}
