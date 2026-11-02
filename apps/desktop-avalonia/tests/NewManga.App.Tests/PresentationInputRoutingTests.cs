using System;
using System.IO;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.Views.Fluent;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using NewManga.Presentation.Avalonia.Hosting;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 R-019: a frontend mounted in the hidden staging slot must not consume application shortcuts
/// or focus that belong to the visible UI; input activation follows the commit, not the staging mount.
/// </summary>
public sealed class PresentationInputRoutingTests
{
    private static Window CreateWindow(Control stagingContent, Button visibleButton, out FrontendContentHost staging)
    {
        staging = new FrontendContentHost { Opacity = 0, IsHitTestVisible = false };
        staging.SetContent(stagingContent);
        var root = new Grid();
        root.Children.Add(staging);
        root.Children.Add(visibleButton);
        return new Window { Width = 900, Height = 600, Content = root };
    }

    [AvaloniaFact]
    public void StagedV2_DoesNotConsumeKeys_UntilCommittedAsActive()
    {
        using var themeManager = new DesignSystemThemeManager(Application.Current!);
        themeManager.Initialize();
        var shell = new AppShellV2(NullHostController.Instance, themeManager: themeManager);
        shell.IsInputActive = false;
        // Deterministic key scope: V2 shells created with the shared NullHostController instance share the
        // process-wide CurrentFrontend session memento, so an earlier test may have left another space active.
        shell.ViewModel.SwitchSpace(NewManga.App.Shell.V2.SpaceId.Library);

        var visibleKeys = 0;
        var visibleButton = new Button { Content = "visible" };
        visibleButton.AddHandler(InputElement.KeyDownEvent, (_, _) => visibleKeys++, RoutingStrategies.Bubble);

        var window = CreateWindow(shell, visibleButton, out _);
        try
        {
            window.Show();
            window.Activate();
            Pump();
            Assert.True(visibleButton.Focus(), "the visible button must take focus");
            Pump();

            // Parked staging tree: the visible UI keeps the shortcut routing and the hidden V2 stays inert.
            window.KeyPressQwerty(PhysicalKey.K, RawInputModifiers.Control);
            PumpUntil(() => visibleKeys == 1);
            Assert.Equal(1, visibleKeys);
            Assert.False(shell.ViewModel.IsPaletteOpen, "a staged, inactive V2 must not consume Ctrl+K");

            // Commit turns input on: the same shortcut now reaches the V2 command palette.
            shell.IsInputActive = true;
            window.KeyPressQwerty(PhysicalKey.K, RawInputModifiers.Control);
            PumpUntil(() => shell.ViewModel.IsPaletteOpen);
            Assert.True(shell.ViewModel.IsPaletteOpen, "the committed V2 must own the shortcut");

            // Rolling the activation back again restores exclusive routing to the visible UI.
            shell.IsInputActive = false;
            Assert.True(visibleButton.Focus());
            Pump();
            window.KeyPressQwerty(PhysicalKey.K, RawInputModifiers.Control);
            PumpUntil(() => visibleKeys == 2);
            Assert.Equal(2, visibleKeys);
        }
        finally
        {
            window.Close();
        }
    }

    private static void Pump()
    {
        for (var i = 0; i < 3; i++)
        {
            Dispatcher.UIThread.RunJobs();
            System.Threading.Thread.Sleep(10);
        }
    }

    private static void PumpUntil(Func<bool> condition, int timeoutMs = 2000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (!condition() && DateTime.UtcNow < deadline)
        {
            Dispatcher.UIThread.RunJobs();
            System.Threading.Thread.Sleep(10);
        }

        Dispatcher.UIThread.RunJobs();
    }

    /// <summary>
    /// R-019 through the production switch transaction: the committed tree is input-active and the staging
    /// slot is empty; the staged (pre-commit) tree was parked by the coordinator (see
    /// FrontendHostCoordinatorTests.InputActivation_* for the exact mount/commit activation sequence).
    /// </summary>
    [AvaloniaFact]
    public async Task ProductionSwitch_LeavesOnlyTheCommittedTreeInputActive()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var root = Path.Combine(Path.GetTempPath(), $"nm-fea07-input-{Guid.NewGuid():N}");
        Directory.CreateDirectory(root);
        try
        {
            var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(root, "settings.json")));
            appearance.Reload();
            var themeHome = new ThemeHomePaths(
                SettingsFilePath: Path.Combine(root, "theme-settings.json"),
                ThemesDirectory: Path.Combine(root, "themes"),
                FavoritesFilePath: Path.Combine(root, "theme-favorites.json"),
                IsCustom: true);
            var window = App.CreatePresentationShell(
                AppOptions.Parse(new[] { "--presentation-host=true" }),
                NullHostController.Instance,
                FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
                appearance,
                themeHome,
                themeManager,
                application);
            var presentation = Assert.IsType<PresentationWindow>(window);
            try
            {
                presentation.Show();
                Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);

                var result = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
                Assert.True(result.Succeeded, result.Failure);
                var v2 = Assert.IsType<AppShellV2>(presentation.ContentHost.Current);
                Assert.True(v2.IsInputActive, "the committed V2 must be input-active");
                Assert.Null(presentation.StagingHost.Current);
            }
            finally
            {
                presentation.Close();
            }
        }
        finally
        {
            try
            {
                Directory.Delete(root, recursive: true);
            }
            catch (IOException)
            {
                // best-effort cleanup
            }
        }
    }
}
