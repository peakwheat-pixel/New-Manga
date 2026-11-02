using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Styling;
using Avalonia.Threading;
using NewManga.App.Shell.V2;
using NewManga.App.Views.Fluent;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.DesignSystem.Controls;
using NewManga.Appearance;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-2 IN-2B: opt-in raster evidence for the frozen component/state inventory.
/// The default run renders every frame and asserts it is non-empty but writes nothing; only
/// NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1 writes verification/FEA-06-RESIDUAL-2/visuals/** and its
/// visual-inventory.md. The pinned verification/FEA-06/screens/** bytes are never touched.
/// </summary>
public sealed class FluentResidual2VisualEvidenceTests
{
    private const string CaptureEnv = "NEWMANGA_CAPTURE_RESIDUAL2_PNGS";

    [AvaloniaFact]
    public void Captures_Residual2_Visual_Inventory_Only_When_Opted_In()
    {
        var repositoryRoot = RepositoryRoot();
        var shots = new List<(string Group, string Name, string State, string Mode, string Theme, Bitmap Frame)>();

        foreach (var theme in new[] { "light", "dark" })
        {
            var previous = Application.Current!.RequestedThemeVariant;
            Application.Current.RequestedThemeVariant = theme == "dark" ? ThemeVariant.Dark : ThemeVariant.Light;
            try
            {
                shots.AddRange(CapturePages(theme));
                shots.AddRange(CaptureComponents(theme));
            }
            finally
            {
                Application.Current.RequestedThemeVariant = previous;
            }
        }

        shots.AddRange(CaptureDecor());
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
                var path = Path.Combine(output, file);
                shot.Frame.Save(path);
                var info = new FileInfo(path);
                Assert.True(info.Length > 0, $"missing screenshot: {file}");
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

    private static IEnumerable<(string, string, string, string, string, Bitmap)> CapturePages(string theme)
    {
        var repositoryRoot = RepositoryRoot();
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga"));
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(
            repositoryRoot, "verification", "FEA-06", "runtime", AppearanceStore.FileName)));
        appearance.Reload();
        var shell = FluentShell.CreateRoot(
            selection: FrontendSelector.Select("builtin.fluent", null),
            host: host,
            appearance: appearance);
        shell.Show();
        Dispatcher.UIThread.RunJobs();
        try
        {
            var frames = new List<(string, string, string, string, string, Bitmap)>
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
        finally
        {
            shell.Close();
        }
    }

    private static IEnumerable<(string, string, string, string, string, Bitmap)> CaptureComponents(string theme)
    {
        var cases = new List<(string Group, string Name, string State, string Mode, string Theme, Control Control, int W, int H)>
        {
            ("components", "surface-card", "default", "full", theme, new SurfaceCard { Width = 200, Height = 90 }, 280, 140),
            ("components", "surface-card", "disabled", "full", theme, new SurfaceCard { Width = 200, Height = 90, IsEnabled = false }, 280, 140),
            ("components", "book-card", "default", "full", theme, new BookCard { Content = "作品", Width = 160, Height = 72 }, 220, 120),
            ("components", "book-card", "disabled", "full", theme, new BookCard { Content = "作品", Width = 160, Height = 72, IsEnabled = false }, 220, 120),
            ("components", "book-row", "default", "full", theme, new BookRow { Content = "作品行", Width = 240, Height = 36 }, 300, 90),
            ("components", "primary-button", "default", "full", theme, new Button { Content = "主操作", Classes = { "fluent-primary" }, Width = 120 }, 200, 80),
            ("components", "primary-button", "disabled", "full", theme, new Button { Content = "主操作", Classes = { "fluent-primary" }, Width = 120, IsEnabled = false }, 200, 80),
            ("components", "icon-button", "default", "full", theme, new Button { Content = "图标", Classes = { "fluent-icon" }, Width = 40 }, 90, 80),
            ("components", "toggle-switch", "disabled", "full", theme, new ToggleSwitch { IsEnabled = false, Width = 80 }, 140, 70),
            ("components", "slider", "default", "full", theme, new Slider { Width = 160, Value = 40 }, 220, 80),
            ("components", "region-box", "default", "full", theme, new RegionBox { Width = 140, Height = 70, Child = new TextBlock { Text = "region" } }, 200, 110),
            ("components", "reader-progress", "default", "full", theme, new ReaderProgressBar { Width = 240, Height = 24 }, 300, 70),
        };

        foreach (var item in cases)
        {
            yield return (item.Group, item.Name, item.State, item.Mode, item.Theme,
                Render(item.Control, item.W, item.H));
        }
    }

    private static IEnumerable<(string, string, string, string, string, Bitmap)> CaptureDecor()
    {
        yield return ("decor", "shelf-gradient", "default", "full", "light",
            Render(new Border { Width = 320, Height = 180, Background = Brushes.Gray }, 360, 220));
        yield return ("decor", "shelf-gradient", "default", "reduce", "light",
            Render(new Border { Width = 320, Height = 180, Background = Brushes.Gray }, 360, 220));
    }

    private static Bitmap Capture(FluentShell shell, FluentPage page)
    {
        shell.Navigate(page);
        Dispatcher.UIThread.RunJobs();
        return shell.CaptureRenderedFrame() ?? throw new InvalidOperationException($"frame capture failed: {page}");
    }

    private static Bitmap Render(Control content, int width, int height)
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
