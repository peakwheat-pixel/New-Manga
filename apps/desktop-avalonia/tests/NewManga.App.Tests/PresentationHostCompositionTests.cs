using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.App.Views.Fluent;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using NewManga.Presentation.Avalonia.Switching;
using NewManga.Presentation.Avalonia.Windows;
using NewManga.ThemeEngine;
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

            // The memento is process-wide for the (shared) NullHostController instance: restore the default
            // session values so later tests are not order-dependent on this state-preservation check.
            if (v2Content is not null)
            {
                v2Content.ViewModel.SwitchSpace(SpaceId.Library);
                v2Content.ViewModel.Current.Session.Console.RunIdInput = string.Empty;
                v2Content.ViewModel.Current.Session.Reader.BookId = null;
            }
        }
        finally
        {
            presentation.Close();
        }
    }

    /// <summary>
    /// R-002: after a production content-tree switch the hidden (cached) Fluent tree still blocks the
    /// close while it holds an unsaved settings draft.
    /// </summary>
    [AvaloniaFact]
    public async Task HiddenProductionContentTree_BlocksCloseAfterSwitch()
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

            // R-001: the dirty draft survived the switch into the hidden Fluent tree.
            Assert.True(fluent.SettingsViewModel.IsDirty);

            // R-002: the close is blocked by the hidden cached tree, not just the visible V2 tree.
            cancelled = false;
            presentation.Close();
            Assert.True(cancelled, "a hidden cached Fluent tree with an unsaved settings draft must block the close");

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

    /// <summary>
    /// R-002 (r4): the production Theme Studio draft really feeds the V2 exit gate. The provider is never
    /// overridden: a real unapplied draft is created through the registered Theme Studio view model and
    /// must flip <c>AppShellV2.HasUnsavedEdits</c> / block the close on its own. A last reverse check
    /// removes the provider and proves the previous block came from it.
    /// </summary>
    [AvaloniaFact]
    public async Task ThemeStudioUnappliedDraft_BlocksCloseThroughProductionProvider()
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
            var toV2 = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(toV2.Succeeded, toV2.Failure);
            var v2 = Assert.IsType<AppShellV2>(presentation.ContentHost.Current);

            var adapter = Assert.IsType<ThemeStudioSurfaceAdapter>(
                v2.ViewModel.State.GetSurfaceWorkspace(ShellSurface.ThemeStudio));
            var studio = adapter.ViewModel;
            var service = Assert.IsType<ThemeEngineThemeStudioService>(studio.Service);
            await WaitUntilAsync(() => service.IsInitialized);

            // Clean baseline: no draft, no exit blocker.
            Assert.False(studio.HasDraft);
            Assert.False(v2.HasUnsavedEdits);

            // A real unapplied draft through the production editor (no provider override anywhere).
            studio.Editor.SelectMaterial(ThemeMaterial.None);
            if (!studio.HasDraft)
            {
                studio.Editor.SelectMaterial(ThemeMaterial.Solid);
            }

            Assert.True(studio.HasDraft, "the production Theme Studio editor did not create an unapplied draft");
            Assert.True(v2.HasUnsavedEdits, "the V2 shell must report the real Theme Studio draft");

            cancelled = false;
            presentation.Close();
            Assert.True(cancelled, "an unapplied Theme Studio draft must block the close through the wired provider");

            // Discarding the draft through the real service unblocks the same gate.
            await service.CancelPreviewAsync();
            studio.NotifyDraftChanged();
            Assert.False(studio.HasDraft);
            Assert.False(v2.HasUnsavedEdits);

            // Create a fresh draft and verify the block is really produced by the provider seam: removing
            // it (simulated regression) both hides the draft state and lets the close through.
            studio.Editor.SelectMaterial(ThemeMaterial.None);
            if (!studio.HasDraft)
            {
                studio.Editor.SelectMaterial(ThemeMaterial.Solid);
            }

            Assert.True(studio.HasDraft);
            cancelled = false;
            presentation.Close();
            Assert.True(cancelled);

            v2.ThemeStudioDraftProvider = null;
            Assert.False(v2.HasUnsavedEdits);
            cancelled = false;
            presentation.Close();
            Assert.False(cancelled, "without the provider the draft no longer blocks the close (reverse validation)");
        }
        finally
        {
            presentation.Close();
        }
    }

    /// <summary>
    /// R-020 (r5): the stable window owns the native window state. Fluent full-screen requests (button / F /
    /// Esc) must drive <see cref="WindowState"/> through the production composition root, only for the
    /// visible tree, and switching frontends must restore a normal window.
    /// </summary>
    [AvaloniaFact]
    public async Task FluentFullScreenRequests_DriveTheStableWindowState()
    {
        var application = Application.Current!;
        using var themeManager = new DesignSystemThemeManager(application);
        themeManager.Initialize();
        var appearance = Appearance();
        var options = AppOptions.Parse(new[] { "--presentation-host=true" });
        var selection = FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null);
        var window = App.CreatePresentationShell(options, NullHostController.Instance, selection, appearance, ThemeHome(), themeManager, application);
        var presentation = Assert.IsType<PresentationWindow>(window);
        try
        {
            presentation.Show();
            var fluent = Assert.IsType<FluentShellSurface>(presentation.ContentHost.Current);
            fluent.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();

            var fullScreenButton = fluent.GetVisualDescendants().OfType<Button>()
                .FirstOrDefault(button => string.Equals(button.Content as string, "全屏", StringComparison.Ordinal));
            var reader = fluent.GetVisualDescendants().OfType<ReaderPageView>().FirstOrDefault();
            Assert.NotNull(fullScreenButton);
            Assert.NotNull(reader);

            // Button path: the visible Fluent reader asks the stable window for full screen and back.
            fullScreenButton!.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();
            Assert.True(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.FullScreen, presentation.WindowState);
            fullScreenButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();
            Assert.False(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.Normal, presentation.WindowState);

            // F path: the reader key funnel toggles the native window state.
            Assert.True(reader!.Focus());
            Dispatcher.UIThread.RunJobs();
            window.KeyPressQwerty(PhysicalKey.F, RawInputModifiers.None);
            Dispatcher.UIThread.RunJobs();
            Assert.True(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.FullScreen, presentation.WindowState);
            window.KeyPressQwerty(PhysicalKey.F, RawInputModifiers.None);
            Dispatcher.UIThread.RunJobs();
            Assert.False(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.Normal, presentation.WindowState);

            // Esc path: the Fluent surface closes the reader (SurfaceBack binding, FEA-06) and the stable
            // window must leave full screen instead of leaving the user stuck in a full-screen library.
            window.KeyPressQwerty(PhysicalKey.F, RawInputModifiers.None);
            Dispatcher.UIThread.RunJobs();
            Assert.Equal(WindowState.FullScreen, presentation.WindowState);
            Assert.True(reader.Focus());
            window.KeyPressQwerty(PhysicalKey.Escape, RawInputModifiers.None);
            Dispatcher.UIThread.RunJobs();
            Assert.NotEqual(FluentPage.Reader, fluent.CurrentPage);
            Assert.False(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.Normal, presentation.WindowState);

            // Switching frontends restores a normal window, and the hidden cached Fluent tree can no longer
            // drive the window chrome.
            fluent.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();
            fullScreenButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();
            Assert.Equal(WindowState.FullScreen, presentation.WindowState);

            var toV2 = await presentation.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(toV2.Succeeded, toV2.Failure);
            Assert.Equal(WindowState.Normal, presentation.WindowState);
            Assert.False(fluent.ReaderViewModel.IsFullScreen);
            fluent.FullScreenRequested?.Invoke(true);
            Dispatcher.UIThread.RunJobs();
            Assert.Equal(WindowState.Normal, presentation.WindowState);

            // Switching back re-wires the same cached surface: the key funnel drives the window again.
            var backToFluent = await presentation.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
            Assert.True(backToFluent.Succeeded, backToFluent.Failure);
            fluent.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();
            var readerAgain = fluent.GetVisualDescendants().OfType<ReaderPageView>().First();
            Assert.True(readerAgain.Focus());
            Dispatcher.UIThread.RunJobs();
            window.KeyPressQwerty(PhysicalKey.F, RawInputModifiers.None);
            Dispatcher.UIThread.RunJobs();
            Assert.True(fluent.ReaderViewModel.IsFullScreen);
            Assert.Equal(WindowState.FullScreen, presentation.WindowState);
        }
        finally
        {
            presentation.Close();
        }
    }

    private static async Task WaitUntilAsync(Func<bool> condition, int timeoutMs = 10000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (!condition() && DateTime.UtcNow < deadline)
        {
            Dispatcher.UIThread.RunJobs();
            await Task.Delay(10);
        }
    }
}
