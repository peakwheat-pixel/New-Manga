using System.IO;
using Avalonia;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using NewManga.ThemeEngine;
using Xunit;
using ThemeAppearanceMode = NewManga.ThemeEngine.AppearanceMode;
using ThemeContrastMode = NewManga.ThemeEngine.ContrastMode;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-PREREQ-2 P5/AC5 (W-9/Q-32): the app-side <see cref="IThemeSettingsSink"/> adapter maps the Theme
/// Engine's settings into the canonical appearance document (through the sole writer
/// <see cref="AppearanceCoordinator"/>), and the production Theme Studio construction path actually
/// receives/invokes that sink (the R2-P1-1 injection-point requirement).
/// </summary>
public sealed class AppearanceThemeSettingsSinkTests
{
    [Fact]
    public async Task Sink_MapsEveryThemeSettingsFieldIntoTheCanonicalDocument()
    {
        using var temp = new TempRoot();
        var path = Path.Combine(temp.Path, AppearanceStore.FileName);
        var coordinator = new AppearanceCoordinator(new AppearanceStore(path, Path.Combine(temp.Path, "theme-settings.json")));
        coordinator.Reload();
        var sink = new AppearanceThemeSettingsSink(coordinator);
        var settings = new ThemeSettings(
            "builtin.fluent-dark",
            ThemeAppearanceMode.Dark,
            ThemeContrastMode.High,
            new LayoutProfile("default", LayoutNavigation.Sidebar, ShelfLayout.List, Density.Compact, WorkbenchLayout.Split, ReaderLayout.FitWidth),
            ReducedMotion: true,
            FollowSystemAccent: true);

        await sink.WriteAsync(settings);

        var written = new AppearanceCoordinator(new AppearanceStore(path)).Reload();
        Assert.Equal("builtin.fluent-dark", written.VisualThemeId);
        Assert.Equal(NewManga.Appearance.AppearanceMode.Dark, written.Mode);
        Assert.Equal(AppearanceContrast.High, written.Contrast);
        Assert.True(written.FollowSystemAccent);
        Assert.Equal(MotionMode.Reduce, written.MotionMode);
        Assert.Equal("sidebar", written.Layout.Navigation);
        Assert.Equal("list", written.Layout.Shelf);
        Assert.Equal("compact", written.Layout.Density);
        Assert.Equal("split", written.Layout.Workbench);
        Assert.Equal("fit-width", written.Layout.Reader);
    }

    [Fact]
    public async Task Sink_PreservesTheLegacyMotionOnOffSemantics()
    {
        using var temp = new TempRoot();
        var coordinator = new AppearanceCoordinator(new AppearanceStore(Path.Combine(temp.Path, AppearanceStore.FileName)));
        coordinator.Reload();
        var sink = new AppearanceThemeSettingsSink(coordinator);

        await sink.WriteAsync(ThemeDefaults.Settings with { ReducedMotion = false });
        Assert.Equal(MotionMode.Full, coordinator.Settings.MotionMode);

        await sink.WriteAsync(ThemeDefaults.Settings with { ReducedMotion = true });
        Assert.Equal(MotionMode.Reduce, coordinator.Settings.MotionMode);
    }

    [Fact]
    public async Task Sink_DoesNotWriteTheLegacyThemeSettingsDocument()
    {
        using var temp = new TempRoot();
        var legacyPath = Path.Combine(temp.Path, "theme-settings.json");
        var coordinator = new AppearanceCoordinator(new AppearanceStore(
            Path.Combine(temp.Path, AppearanceStore.FileName),
            legacyPath));
        coordinator.Reload();

        await new AppearanceThemeSettingsSink(coordinator).WriteAsync(ThemeDefaults.Settings);

        Assert.True(File.Exists(Path.Combine(temp.Path, AppearanceStore.FileName)));
        Assert.False(File.Exists(legacyPath));
    }

    [AvaloniaFact]
    public async Task ProductionThemeStudio_IsWiredWithTheCompatibilitySink()
    {
        var application = Application.Current!;
        using var manager = new DesignSystemThemeManager(application);
        Assert.True(manager.Initialize(NewManga.DesignSystem.Theming.AppearanceMode.Dark), manager.LastError);
        using var temp = new TempRoot();
        var sink = new RecordingSink();
        var service = ThemeEngineThemeStudioService.CreateProduction(
            application,
            manager,
            themeDirectory: Path.Combine(temp.Path, "themes"),
            settingsFilePath: Path.Combine(temp.Path, "theme-settings.json"),
            favoritesFilePath: Path.Combine(temp.Path, "favorites.json"),
            presentationSink: sink);

        await service.InitializeAsync();
        sink.Writes.Clear();
        await service.ThemeService.SetAppearanceAsync(ThemeAppearanceMode.Light);

        var write = Assert.Single(sink.Writes);
        Assert.Equal(ThemeAppearanceMode.Light, write.Appearance);
        Assert.True(File.Exists(Path.Combine(temp.Path, "theme-settings.json")));
    }

    private sealed class RecordingSink : IThemeSettingsSink
    {
        public List<ThemeSettings> Writes { get; } = [];

        public Task WriteAsync(ThemeSettings settings, CancellationToken cancellationToken = default)
        {
            Writes.Add(settings);
            return Task.CompletedTask;
        }
    }

    private sealed class TempRoot : IDisposable
    {
        public TempRoot()
        {
            Path = System.IO.Path.Combine(
                System.IO.Path.GetTempPath(),
                "nm-appearance-sink-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Path);
        }

        public string Path { get; }

        public void Dispose()
        {
            if (Directory.Exists(Path))
            {
                Directory.Delete(Path, recursive: true);
            }
        }
    }
}
