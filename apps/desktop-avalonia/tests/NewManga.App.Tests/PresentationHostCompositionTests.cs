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
using NewManga.Presentation.Avalonia.Windows;
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

    private AppearanceCoordinator Appearance()
    {
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, "presentation-settings.json")));
        appearance.Reload();
        return appearance;
    }

    [AvaloniaFact]
    public async Task PresentationHost_ComposesRealFrontendsAndSwitchesInsideOneWindow()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = Appearance();
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
            presentation.Show();
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


    [AvaloniaFact]
    public async Task InterruptedSwitchFromPreviousRun_IsRolledBackAtStartup()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = Appearance();
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var themeHome = ThemeHome();
        var journal = new SwitchJournal(Path.Combine(themeHome.ThemesDirectory, "..", "switch-journal.json"));
        journal.Begin(FrontendSelector.FluentFrontendId);
        journal.Advance(SwitchStage.Rendered);
        Assert.True(journal.HasInterruptedSwitch(out _));

        // The App startup path runs the journal recovery before the shell decision.
        App.RecoverInterruptedSwitch(themeHome, appearance);

        var selection = FrontendSelector.Select(FrontendSelector.CurrentV2FrontendId, persistedFrontendId: null);
        var window = App.CreatePresentationShell(options, NullHostController.Instance, selection, appearance, themeHome, themeManager, application);
        try
        {
            var presentation = Assert.IsType<PresentationWindow>(window);
            Assert.IsType<AppShellV2>(presentation.ContentHost.Current);
            Assert.True(journal.TryRead(out var entry, out _));
            Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
            Assert.Contains("startup recovery", entry.Failure);
        }
        finally
        {
            window.Close();
        }
    }


    /// <summary>
    /// R-001: real content trees are cached per frontend; 50 round trips keep one stable window and one
    /// tree per frontend with the testable session/draft state intact (Fluent page + unsaved settings
    /// draft, V2 current space + session memento values).
    /// </summary>
    [AvaloniaFact]
    public async Task RealContentRoundTrips_KeepOneStableWindowAndTheirState()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = Appearance();
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.CurrentV2FrontendId, persistedFrontendId: null);
        var window = App.CreatePresentationShell(options, NullHostController.Instance, selection, appearance, ThemeHome(), themeManager, application);
        var presentation = Assert.IsType<PresentationWindow>(window);
        try
        {
            presentation.Show();
            FluentShellSurface? fluentContent = null;
            AppShellV2? v2Content = null;
            AppearanceSettings? fluentDraft = null;
            const string consoleIntent = "run-intent-marker";
            const string readerBook = "book-marker";
            for (var i = 0; i < 50; i++)
            {
                var fluent = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
                Assert.True(fluent.Succeeded, fluent.Failure);
                var fluentTree = Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);
                if (fluentContent is null)
                {
                    fluentContent = fluentTree;
                    fluentTree.Navigate(FluentPage.Workbench);
                    // An unapplied settings draft is real user state that a frontend switch must preserve.
                    fluentDraft = fluentTree.SettingsViewModel.Draft with
                    {
                        MotionMode = fluentTree.SettingsViewModel.Draft.MotionMode == MotionMode.Auto
                            ? MotionMode.Reduce
                            : MotionMode.Auto,
                    };
                    fluentTree.SettingsViewModel.UpdateDraft(fluentDraft);
                    Assert.True(fluentTree.SettingsViewModel.IsDirty);
                }
                else
                {
                    Assert.Same(fluentContent, fluentTree);
                    Assert.Equal(FluentPage.Workbench, fluentTree.CurrentPage);
                    Assert.True(fluentTree.SettingsViewModel.IsDirty);
                    Assert.Equal(fluentDraft, fluentTree.SettingsViewModel.Draft);
                }

                var v2 = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
                Assert.True(v2.Succeeded, v2.Failure);
                var v2Tree = Assert.IsType<AppShellV2>(presentation.ContentHost.Current);
                if (v2Content is null)
                {
                    v2Content = v2Tree;
                    v2Tree.ViewModel.SwitchSpace(SpaceId.Studio);
                    v2Tree.ViewModel.Current.Session.Console.RunIdInput = consoleIntent;
                    v2Tree.ViewModel.Current.Session.Reader.BookId = readerBook;
                }
                else
                {
                    Assert.Same(v2Content, v2Tree);
                    Assert.Equal(SpaceId.Studio, v2Tree.ViewModel.Current.Session.Shell.CurrentSpace);
                    Assert.Equal(consoleIntent, v2Tree.ViewModel.Current.Session.Console.RunIdInput);
                    Assert.Equal(readerBook, v2Tree.ViewModel.Current.Session.Reader.BookId);
                }
                Assert.Same(window, presentation);
            }

            Assert.False(File.Exists(Path.Combine(_root, "theme-home", "switch-journal.json")));
        }
        finally
        {
            presentation.Close();
        }
    }

    /// <summary>
    /// R-002: after a production content-tree switch the hidden (cached) Fluent tree still blocks the
    /// close while it holds an unsaved settings draft, and the V2 shell reports the production Theme
    /// Studio draft through its wired provider.
    /// </summary>
    [AvaloniaFact]
    public async Task HiddenProductionContentTreeAndThemeStudioDraft_BlockCloseAfterSwitch()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = Appearance();
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null);
        var window = App.CreatePresentationShell(options, NullHostController.Instance, selection, appearance, ThemeHome(), themeManager, application);
        var presentation = Assert.IsType<PresentationWindow>(window);
        var cancelled = false;
        presentation.Closing += (_, args) => cancelled |= args.Cancel;
        try
        {
            presentation.Show();
            var fluent = Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);
            var dirtyDraft = fluent.SettingsViewModel.Draft with
            {
                MotionMode = fluent.SettingsViewModel.Draft.MotionMode == MotionMode.Auto
                    ? MotionMode.Reduce
                    : MotionMode.Auto,
            };
            fluent.SettingsViewModel.UpdateDraft(dirtyDraft);
            Assert.True(fluent.SettingsViewModel.IsDirty);

            var toV2 = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(toV2.Succeeded, toV2.Failure);
            var v2 = Assert.IsType<AppShellV2>(presentation.ContentHost.Current);

            // R-001: the dirty draft survived the switch into the hidden Fluent tree.
            Assert.True(fluent.SettingsViewModel.IsDirty);

            // R-002: the close is blocked by the hidden cached tree, not just the visible V2 tree.
            cancelled = false;
            presentation.Close();
            Assert.True(cancelled, "a hidden cached Fluent tree with an unsaved settings draft must block the close");

            // R-002: the V2 shell reports the production Theme Studio draft (wired by the composition root);
            // simulate an unapplied studio draft and verify it blocks the close as well.
            Assert.NotNull(v2.ThemeStudioDraftProvider);
            v2.ThemeStudioDraftProvider = () => true;
            cancelled = false;
            presentation.Close();
            Assert.True(cancelled, "an unapplied Theme Studio draft in the V2 shell must block the close");

            // Resolve both states: the close is allowed again.
            v2.ThemeStudioDraftProvider = () => false;
            fluent.SettingsViewModel.UpdateDraft(appearance.Settings);
            Assert.False(fluent.SettingsViewModel.IsDirty);
            cancelled = false;
            presentation.Close();
            Assert.False(cancelled);
        }
        finally
        {
            presentation.Close();
        }
    }
}
