using System;
using System.IO;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.Views.Fluent;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using NewManga.Presentation.Avalonia.Switching;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 slice 2c-part2: the composition root (<c>--presentation-host</c>) builds the real V2/Fluent
/// content trees and switches them inside one stable <see cref="PresentationWindow"/> (§7.1/§7.3/H2).
/// </summary>
public sealed class PresentationHostCompositionTests : IDisposable
{
    private readonly string _root;

    public PresentationHostCompositionTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-compose-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    private ThemeHomePaths ThemeHome()
    {
        var themeHome = Path.Combine(_root, "theme-home");
        Directory.CreateDirectory(themeHome);
        return new ThemeHomePaths(
            SettingsFilePath: Path.Combine(themeHome, "theme-settings.json"),
            ThemesDirectory: Path.Combine(themeHome, "themes"),
            FavoritesFilePath: Path.Combine(themeHome, "theme-studio-favorites.json"),
            IsCustom: true);
    }

    [AvaloniaFact]
    public async Task PresentationHost_ComposesRealFrontendsAndSwitchesInsideOneWindow()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, "presentation-settings.json")));
        appearance.Reload();
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null);

        var window = App.CreatePresentationShell(
            options,
            NullHostController.Instance,
            selection,
            appearance,
            ThemeHome(),
            themeManager,
            application);

        Assert.IsType<PresentationWindow>(window);
        var presentation = (PresentationWindow)window;
        try
        {
            Assert.Equal(FrontendSelector.FluentFrontendId, presentation.CurrentFrontendId);
            Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);

            var toV2 = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(toV2.Succeeded, toV2.Failure);
            Assert.IsType<AppShellV2>(presentation.ContentHost.Current);
            Assert.Equal(FrontendSelector.CurrentV2FrontendId, appearance.FrontendId);

            var toFluent = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
            Assert.True(toFluent.Succeeded, toFluent.Failure);
            Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);
            Assert.Same(window, presentation);
            Assert.False(File.Exists(Path.Combine(_root, "theme-home", "switch-journal.json")));
        }
        finally
        {
            presentation.Close();
        }
    }

    [AvaloniaFact]
    public void PresentationHostFlag_IsParsed()
    {
        Assert.True(AppOptions.Parse(new[] { "--presentation-host=true" }).PresentationHost);
        Assert.False(AppOptions.Parse(Array.Empty<string>()).PresentationHost);
        Assert.False(AppOptions.Parse(new[] { "--presentation-host=false" }).PresentationHost);
    }
}
