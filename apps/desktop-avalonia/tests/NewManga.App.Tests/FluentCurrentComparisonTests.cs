using System;
using System.IO;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Views.Fluent;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 scope-r3 R3-004 / AC4: Current comparison behaviour. Fluent-only high-contrast and
/// motion changes must be reversible and must NOT pollute the shared resource stack that Current V2 also
/// consumes; after an in-process frontend round trip the frozen focus/elevation tokens are back to the
/// standard baseline and the Current V2 content is a non-Fluent surface.
/// </summary>
public sealed class FluentCurrentComparisonTests : IDisposable
{
    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea06-residual-current-{Guid.NewGuid():N}");

    public FluentCurrentComparisonTests() => Directory.CreateDirectory(_root);

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

    [AvaloniaFact]
    public async Task FluentHighContrastAndMotion_DoNotPolluteCurrentV2_AfterRoundTrip()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, "presentation-settings.json")));
        appearance.Reload();

        var focusBaseline = ResourceOf<Thickness>(application, "Nm.Border.Focus");
        var elevationBaseline = ResourceOf<BoxShadows>(application, "Nm.Elevation.1");
        Assert.Equal(2d, focusBaseline.Left);
        Assert.True(elevationBaseline.Count > 0);

        var window = App.CreatePresentationShell(
            AppOptions.Parse(new[] { "--presentation-host=true" }),
            NullHostController.Instance,
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            appearance,
            new ThemeHomePaths(
                SettingsFilePath: Path.Combine(_root, "theme-home", "theme-settings.json"),
                ThemesDirectory: Path.Combine(_root, "theme-home", "themes"),
                FavoritesFilePath: Path.Combine(_root, "theme-home", "theme-studio-favorites.json"),
                IsCustom: true),
            themeManager,
            application);
        var presentation = Assert.IsType<PresentationWindow>(window);
        try
        {
            presentation.Show();
            Dispatcher.UIThread.RunJobs();
            Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);

            // Fluent-only high contrast is reversible: 3px while active, frozen 2px after restore.
            Assert.True(themeManager.SetContrast(ContrastMode.High), themeManager.LastError);
            Assert.Equal(3d, ResourceOf<Thickness>(application, "Nm.Border.Focus").Left);
            Assert.Equal(0, ResourceOf<BoxShadows>(application, "Nm.Elevation.1").Count);
            Assert.True(themeManager.SetContrast(ContrastMode.Standard), themeManager.LastError);
            Assert.Equal(focusBaseline, ResourceOf<Thickness>(application, "Nm.Border.Focus"));
            Assert.Equal(elevationBaseline.Count, ResourceOf<BoxShadows>(application, "Nm.Elevation.1").Count);

            // In-process round trip to Current V2 and back leaves the shared stack at the baseline and the
            // Current surface is not a Fluent surface.
            var toCurrent = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(toCurrent.Succeeded, toCurrent.Failure);
            var currentContent = presentation.ContentHost.Current;
            Assert.NotNull(currentContent);
            Assert.IsNotType<FluentShellSurface>(currentContent);
            Assert.Equal(focusBaseline, ResourceOf<Thickness>(application, "Nm.Border.Focus"));
            Assert.Equal(elevationBaseline.Count, ResourceOf<BoxShadows>(application, "Nm.Elevation.1").Count);

            var backToFluent = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
            Assert.True(backToFluent.Succeeded, backToFluent.Failure);
            Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);
            Assert.Equal(focusBaseline, ResourceOf<Thickness>(application, "Nm.Border.Focus"));
            Assert.Equal(elevationBaseline.Count, ResourceOf<BoxShadows>(application, "Nm.Elevation.1").Count);
        }
        finally
        {
            presentation.Close();
        }
    }

    private static T ResourceOf<T>(Application application, string key)
    {
        Assert.True(application.TryGetResource(key, application.ActualThemeVariant, out var value), $"missing resource {key}");
        return Assert.IsType<T>(value);
    }
}
