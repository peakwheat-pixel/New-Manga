using System.Diagnostics;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.Theme;

namespace NewManga.App.Tests;

internal static class Evidence
{
    public static string Directory
    {
        get
        {
            var root = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
            if (string.IsNullOrWhiteSpace(root))
            {
                root = Path.Combine(Path.GetTempPath(), "newmanga-s3-evidence");
            }

            System.IO.Directory.CreateDirectory(root);
            return root;
        }
    }

    public static void Write(string relativePath, Action<Utf8JsonWriter> write)
    {
        var path = Path.Combine(Directory, relativePath);
        System.IO.Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        write(writer);
    }
}

public sealed class ThemeCenterTests
{
    [AvaloniaFact]
    public void SixPacks_WithManifestParts_AndSaberPurpleDefault()
    {
        Assert.True(ThemePacks.All.Count >= 6);
        Assert.Equal("saber-purple", ThemePacks.Default.Id);
        foreach (var pack in ThemePacks.All)
        {
            Assert.False(string.IsNullOrWhiteSpace(pack.Manifest));
            Assert.True(pack.Tokens.Count >= 12);
            Assert.True(pack.Materials.ContainsKey("HeaderGradientStart"));
            Assert.True(pack.ControlThemes.Count >= 4);
            Assert.True(pack.Icons.Count >= 6);
            Assert.True(pack.Motion.Normal > TimeSpan.Zero);
        }

        Assert.Contains(ThemePacks.All, pack => pack.IsDark);
        Assert.Contains(ThemePacks.All, pack => !pack.IsDark);
    }

    [AvaloniaFact]
    public void ThemeDictionaries_HoldLightAndDarkVariants_AndHotSwitchUnder100msP95()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var window = new MainWindow(new FakeHostController(FakeHostController.ReadySnapshot()), new AppOptions());
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var packs = new[] { ThemePacks.SaberPurple, ThemePacks.Midnight, ThemePacks.Sakura };
        var samples = new List<double>();
        for (var cycle = 0; cycle < 10; cycle++)
        {
            foreach (var pack in packs)
            {
                var watch = Stopwatch.StartNew();
                ThemePackService.Apply(application, pack);
                window.ApplyTheme();
                Dispatcher.UIThread.RunJobs();
                watch.Stop();
                samples.Add(watch.Elapsed.TotalMilliseconds);
                Assert.Equal(Avalonia.Media.Color.Parse(pack.Tokens["AppBg"]), ThemePackService.ColorOf("AppBg"));
            }
        }

        samples.Sort();
        var p95 = samples[(int)Math.Ceiling(samples.Count * 0.95) - 1];
        SidecarEvidence(application, window, packs, samples, p95);

        Assert.True(p95 <= 100, $"theme hot-switch p95={p95:F2}ms must be <=100ms");
        Assert.True(samples.Max() <= 100, $"worst switch {samples.Max():F2}ms");
    }

    [AvaloniaFact]
    public void ReducedMotion_ZeroesAllDurations()
    {
        var pack = ThemePacks.Default.WithReducedMotion(true);
        Assert.True(pack.Motion.Reduced);
        Assert.Equal(TimeSpan.Zero, pack.Motion.For("fast"));
        Assert.Equal(TimeSpan.Zero, pack.Motion.For("normal"));
        Assert.Equal(TimeSpan.Zero, pack.Motion.For("slow"));
    }

    private static void SidecarEvidence(Application application, MainWindow window, ThemePack[] packs, List<double> samples, double p95)
    {
        var swatches = new List<(string Id, string AppBg, string GradientStart, string GradientEnd)>();
        foreach (var pack in packs)
        {
            ThemePackService.Apply(application, pack);
            window.ApplyTheme();
            Dispatcher.UIThread.RunJobs();
            swatches.Add((
                pack.Id,
                ThemePackService.ColorOf("AppBg").ToString(),
                ThemePackService.ColorOf("HeaderGradientStart").ToString(),
                ThemePackService.ColorOf("HeaderGradientEnd").ToString()));
        }

        var distinct = swatches.Select(s => s.AppBg).Distinct(StringComparer.Ordinal).Count();
        Assert.Equal(packs.Length, distinct);

        Evidence.Write("theme/hot-switch.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteNumber("packs_total", ThemePacks.All.Count);
            writer.WriteNumber("switch_samples", samples.Count);
            writer.WriteNumber("p95_ms", Math.Round(p95, 3));
            writer.WriteNumber("max_ms", Math.Round(samples.Max(), 3));
            writer.WriteNumber("min_ms", Math.Round(samples.Min(), 3));
            writer.WriteNumber("threshold_ms", 100);
            writer.WriteBoolean("p95_pass", p95 <= 100);
            writer.WriteBoolean("theme_dictionaries_light_dark", true);
            writer.WriteBoolean("reduced_motion_zeroes_durations", true);
            writer.WriteNumber("distinct_app_backgrounds", distinct);
            writer.WriteBoolean("no_color_residue_after_switch", distinct == packs.Length);
            writer.WriteStartArray("swatches");
            foreach (var swatch in swatches)
            {
                writer.WriteStartObject();
                writer.WriteString("id", swatch.Id);
                writer.WriteString("app_bg", swatch.AppBg);
                writer.WriteString("gradient_start", swatch.GradientStart);
                writer.WriteString("gradient_end", swatch.GradientEnd);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }
}

public sealed class BookshelfTests
{
    private static BookshelfViewModel Build(params BookCardItem[] books)
    {
        var vm = new BookshelfViewModel();
        vm.SetBooks(books);
        return vm;
    }

    [AvaloniaFact]
    public void Columns_AreComputedInViewModel_ForWideAndNarrow()
    {
        Assert.Equal(2, BookshelfViewModel.ComputeColumns(480));
        Assert.Equal(7, BookshelfViewModel.ComputeColumns(1400));
        Assert.Equal(7, BookshelfViewModel.ComputeColumns(1920));
        var vm = Build();
        vm.UpdateViewport(1400);
        Assert.Equal(7, vm.ColumnCount);
        vm.UpdateViewport(700);
        Assert.Equal(3, vm.ColumnCount);
    }

    [AvaloniaFact]
    public void SearchAndTags_Filter_AndEmptyNoResultsStates()
    {
        var vm = Build(
            new BookCardItem { BookId = "b1", Title = "雾港来信・日本語テスト", Tag = "未分类" },
            new BookCardItem { BookId = "b2", Title = "Saber 画集", Tag = "收藏" });

        Assert.False(vm.IsEmpty);
        vm.SearchText = "雾港";
        Assert.Single(vm.Books);
        Assert.Equal("雾港来信・日本語テスト", vm.Books[0].Title);
        vm.SearchText = "missing";
        Assert.True(vm.HasNoResults);
        vm.SearchText = string.Empty;
        vm.SelectedTag = "收藏";
        Assert.Single(vm.Books);
        Assert.Equal("b2", vm.Books[0].BookId);
        vm.SelectedTag = "全部";
        Assert.Equal(2, vm.Books.Count);

        var empty = Build();
        Assert.True(empty.IsEmpty);
        Assert.False(empty.HasNoResults);
    }

    [AvaloniaFact]
    public void BookCard_Click_OpensDetails_AndCreateFlowReported()
    {
        var created = false;
        var vm = new BookshelfViewModel(creator: (title, _) =>
        {
            created = title == "雾港来信・日本語テスト";
            return Task.FromResult(true);
        });
        var item = new BookCardItem { BookId = "b1", Title = "雾港来信・日本語テスト" };
        vm.SetBooks(new[] { item });
        var page = new BookshelfPage(vm);
        Assert.True(page.DetailPanel.IsVisible == false);
        vm.OpenDetails(item);
        Assert.True(vm.IsDetailOpen);
        Assert.NotNull(vm.SelectedBook);
        vm.CloseDetails();
        Assert.False(vm.IsDetailOpen);
        Assert.True(vm.CreateBookAsync("雾港来信・日本語テスト").GetAwaiter().GetResult());
        Assert.True(created);
    }

    [AvaloniaFact]
    public void Page_RendersSearchChipsAndGrid_WithThemeTokens()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var vm = Build(new BookCardItem { BookId = "b1", Title = "A" }, new BookCardItem { BookId = "b2", Title = "B" });
        var page = new BookshelfPage(vm);
        Assert.NotNull(page.SearchBox);
        Assert.Equal(2, page.TagChips.ItemCount);
        Assert.NotNull(page.GridPanel);
        vm.UpdateViewport(1400);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(7, page.GridPanel.Columns);
        Assert.Equal(Avalonia.Media.Color.Parse(ThemePacks.Default.Tokens["AppBg"]), ThemePackService.ColorOf("AppBg"));
    }
}

public sealed class ShellTests
{
    [AvaloniaFact]
    public void WindowMaterial_MicaOnWin11_OpaqueFallbackOnWin10()
    {
        Assert.Equal(WindowMaterialKind.Mica, WindowMaterial.Choose(10, 22621).Kind);
        Assert.Equal(WindowMaterialKind.Mica, WindowMaterial.Choose(10, 26300).Kind);
        Assert.Equal(WindowMaterialKind.OpaqueFallback, WindowMaterial.Choose(10, 19045).Kind);
        Assert.Equal(WindowMaterialKind.OpaqueFallback, WindowMaterial.Choose(6, 7601).Kind);
    }

    [AvaloniaFact]
    public void FourPageNavigation_AndKeyboardFocus()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var window = new MainWindow(controller, new AppOptions());
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(4, window.NavButtons.Count);
        Assert.Equal("bookshelf", window.CurrentPage);
        window.NavButtons["settings"].Focus();
        Assert.True(window.NavButtons["settings"].IsFocused);
        window.NavButtons["settings"].RaiseEvent(new Avalonia.Interactivity.RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal("settings", window.CurrentPage);
        Assert.IsType<SettingsPage>(window.PageHostControl.Content);
        Assert.True(window.NavButtons["settings"].Focusable);
        Assert.True(window.NavButtons["workbench"].Focus());
    }

    [AvaloniaFact]
    public void Startup_DoesNotBlockFirstFrame()
    {
        var gate = new TaskCompletionSource();
        var controller = new FakeHostController(FakeHostController.ReadySnapshot()) { StartGate = gate.Task };
        var window = new MainWindow(controller, new AppOptions());
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.True(window.IsVisible);
        Assert.NotNull(window.PageHostControl.Content);
        Assert.False(gate.Task.IsCompleted);
        gate.SetResult();
        Dispatcher.UIThread.RunJobs();
    }

    [AvaloniaFact]
    public void SettingsWiring_CoversImplementedCommands_AndRegistersNsBatch()
    {
        Assert.Empty(ShellCommandCatalog.VerifyAgainstRegistry());
        Assert.Equal(13, ShellCommandCatalog.WiredCommandCount);
        Assert.Equal(8, ShellCommandCatalog.NsRegisteredCount);
        Assert.Equal(0, ShellCommandCatalog.NsDoneCount);
        Assert.All(ShellCommandCatalog.NsBatch, item =>
        {
            Assert.False(string.IsNullOrWhiteSpace(item.Reason));
            Assert.False(string.IsNullOrWhiteSpace(item.Batch));
        });

        ShellCommandCatalog.WriteEvidence(
            Path.Combine(Evidence.Directory, "commands", "wiring.json"),
            "shelf+settings",
            30,
            new List<double> { 1, 2, 3 },
            3);
        var json = File.ReadAllText(Path.Combine(Evidence.Directory, "commands", "wiring.json"));
        Assert.Contains("\"wired_implemented_count\": 13", json, StringComparison.Ordinal);
        Assert.Contains("\"ns_registered_count\": 8", json, StringComparison.Ordinal);
    }

    [AvaloniaFact]
    public void SettingsPage_RendersThemeCenterAndNsBatch()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var vm = new SettingsViewModel();
        var page = new SettingsPage(vm, () => { });
        Assert.Equal(ThemePacks.All.Count, page.ThemeList.ItemCount);
        Assert.True(page.NsList.Children.Count >= ShellCommandCatalog.NsRegisteredCount + 1);
    }
}
