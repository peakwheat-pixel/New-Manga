using System.Diagnostics;
using System.IO;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Avalonia.Styling;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.App.Views;
using NewManga.App.Views.Fluent;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using NewManga.Presentation.Avalonia.Switching;
using NewManga.Presentation.Avalonia.Windows;
using DsAppearanceMode = NewManga.DesignSystem.Theming.AppearanceMode;

namespace NewManga.App;

public partial class App : Application
{
    /// <summary>
    /// V11R-D-1: owns the application-wide design-system resource stack. Created in
    /// <see cref="OnFrameworkInitializationCompleted"/> before the shell so every control resolves
    /// <c>Nm.*</c> tokens on first layout; later theme switches only swap resource dictionaries.
    /// </summary>
    private DesignSystemThemeManager? _designSystemTheme;

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
        // V11R-A11Y-1: readable automation names for V2 buttons whose Content is a control tree.
        Shell.V2.V2AccessibleNames.Register();
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            var options = AppOptionsStore.Current;
            StartupDiagnostics.Install(options.ToHostOptions().LogDirectory); // FEA-07 AC4: <log-dir>/startup.log sink

            // V11R-C-3: the old theme-pack startup hook is retired. `--theme` stays as a compatibility
            // argument: LegacyStartupTheme maps it through the ThemeEngine migration table and carries the
            // retired pack's appearance/density into the DesignSystem manager below.
            var startupTheme = LegacyStartupTheme.Resolve(options.StartupThemeId, options.StartupVariant);

            // V11R-D-1: normalize the design-system resource stack (palette + overlays) after the
            // legacy theme pack has been applied. Explicit --variant wins; otherwise the retired
            // pack's appearance (carried through the ThemeEngine migration table) applies; only an
            // absent choice falls back to the design-system default (dark).
            var startupAppearance = StartupAppearance(options) ?? startupTheme.Appearance;
            _designSystemTheme = new DesignSystemThemeManager(this);
            _designSystemTheme.Initialize(startupAppearance);
            if (startupTheme.Density is { } startupDensity &&
                !_designSystemTheme.SetDensity(startupDensity))
            {
                Trace.TraceWarning($"legacy --theme density could not be applied: {_designSystemTheme.LastError}");
            }

            // FEA-06-PREREQ-2 P1/P2/P5: read the persisted appearance document once, resolve the
            // frontend (--frontend > persisted theme.frontendId > fail-safe builtin.current-v2) and hand
            // the single writer to the composition root. The shell choice is recorded for diagnostics.
            var themeHome = ThemeHome.Resolve(options);
            var presentationPath = Path.Combine(
                Path.GetDirectoryName(Path.GetFullPath(themeHome.SettingsFilePath)) ?? ".",
                AppearanceStore.FileName);
            var appearance = new AppearanceCoordinator(new AppearanceStore(
                presentationPath,
                legacyPath: themeHome.SettingsFilePath));
            appearance.Reload();
            // R-003: a crash between persisting the target frontend and committing the journal is rolled
            // back to the last committed frontend before the startup decision is made.
            RecoverInterruptedSwitch(themeHome, appearance);
            var startupPlan = SafeStartupPlanner.Plan(options, appearance.Settings, appearance.Warnings);
            StartupDiagnostics.Report(startupPlan); // FEA-07 AC4: diagnosable safe-startup decision (Trace → startup.log)
            foreach (var diagnostic in startupPlan.Diagnostics)
            {
                Trace.TraceInformation("startup: " + diagnostic);
            }

            if (startupPlan.IsFallback)
            {
                Trace.TraceWarning("startup fell back to the Current V2 shell: " + startupPlan.EffectiveFrontendId);
            }

            // R-004: the planner is the single decision source; its selection object is what starts.
            var selection = startupPlan.Selection;

            var controller = new HostController(options.ToHostOptions());
            var window = CreateShell(options, controller, selection, appearance, themeHome, _designSystemTheme, this);

            desktop.MainWindow = window;
            desktop.ShutdownMode = ShutdownMode.OnMainWindowClose;

            if (!options.UseV2Shell && (!string.IsNullOrWhiteSpace(options.StartupThemeId) || !string.IsNullOrWhiteSpace(options.StartupVariant)))
            {
                (window as MainWindow)?.ApplyTheme();
            }

            if (!string.IsNullOrWhiteSpace(options.StartupPage))
            {
                NavigateStartupPage(window, options);
            }

            if (options.ExitAfterMs is { } exitAfter)
            {
                var timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(exitAfter) };
                timer.Tick += (_, _) =>
                {
                    timer.Stop();
                    window.Close();
                };
                timer.Start();
            }
        }

        base.OnFrameworkInitializationCompleted();
    }

    /// <summary>
    /// FEA-06-PREREQ-2 P2/AC2: the composition root's shell decision. <c>--shell=legacy</c> stays the
    /// one-release operator rollback and wins over everything; otherwise the frontend selector
    /// (<paramref name="selection"/>, W-2b precedence) chooses between the Fluent shell and the Current V2
    /// shell. The V2 path is unchanged apart from receiving the appearance writer and the resolved theme
    /// home explicitly.
    /// </summary>
    internal static Window CreateShell(
        AppOptions options,
        IHostController controller,
        FrontendSelection selection,
        AppearanceCoordinator appearance,
        ThemeHomePaths themeHome,
        DesignSystemThemeManager themeManager,
        Application application)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(controller);
        ArgumentNullException.ThrowIfNull(selection);
        ArgumentNullException.ThrowIfNull(appearance);
        ArgumentNullException.ThrowIfNull(themeHome);
        ArgumentNullException.ThrowIfNull(themeManager);
        ArgumentNullException.ThrowIfNull(application);

        if (!options.UseV2Shell)
        {
            return CreateLegacyShell(controller, options, themeManager);
        }

        if (options.PresentationHost)
        {
            // FEA-07: one stable native window with the real V2/Fluent content factory (opt-in).
            return CreatePresentationShell(options, controller, selection, appearance, themeHome, themeManager, application);
        }

        return selection.IsFluent
            ? FluentShell.CreateRoot(options, selection, controller, appearance, themeManager)
            : CreateV2Shell(application, controller, options, themeManager, appearance, themeHome);
    }

    /// <summary>
    /// V11R-INT-1: the new Avalonia shell (three spaces + Studio dual mode + Theme Studio surface).
    /// Theme Studio is bound to the real theme engine and shares the application's single
    /// <see cref="DesignSystemThemeManager"/> (two managers would fight over the same resource layer).
    /// </summary>
    private static Window CreateV2Shell(
        Application application,
        IHostController controller,
        AppOptions options,
        DesignSystemThemeManager themeManager,
        AppearanceCoordinator appearance,
        ThemeHomePaths themeHome)
    {
        var root = AppShellV2.CreateRoot(controller, options, picker: null, themeManager: themeManager);
        if (root.Content is not AppShellV2 shell)
        {
            return root;
        }

        WireThemeStudio(shell, application, themeManager, appearance, themeHome, options);
        WireImmersiveReader(shell, root);

        return root;
    }

    /// <summary>FEA-07: creates a bare V2 content tree (no host window) for the stable presentation window.</summary>
    internal static AppShellV2 CreateV2Content(
        Application application,
        IHostController controller,
        AppOptions options,
        DesignSystemThemeManager themeManager,
        AppearanceCoordinator appearance,
        ThemeHomePaths themeHome)
    {
        var shell = new AppShellV2(controller, picker: null, themeManager: themeManager);
        WireThemeStudio(shell, application, themeManager, appearance, themeHome, options);
        return shell;
    }

    /// <summary>FEA-07: stable presentation window driving the real V2/Fluent content factory.</summary>
    internal static Window CreatePresentationShell(
        AppOptions options,
        IHostController controller,
        FrontendSelection selection,
        AppearanceCoordinator appearance,
        ThemeHomePaths themeHome,
        DesignSystemThemeManager themeManager,
        Application application)
    {
        var directory = Path.GetDirectoryName(themeHome.SettingsFilePath)
            ?? throw new InvalidOperationException("theme home has no directory");
        var journal = new SwitchJournal(Path.Combine(directory, "switch-journal.json"));



        // R-001/R-010: retain one content tree per frontend so switching back preserves page/session
        // state instead of rebuilding a fresh Fluent/V2 tree (and its subscriptions) every time.
        var contentCache = new Dictionary<string, Control>(StringComparer.Ordinal);
        Control ContentFactory(string frontendId)
        {
            var key = string.Equals(frontendId, FrontendSelector.FluentFrontendId, StringComparison.Ordinal)
                ? FrontendSelector.FluentFrontendId
                : FrontendSelector.CurrentV2FrontendId;
            if (contentCache.TryGetValue(key, out var cached))
            {
                return cached;
            }

            Control content = key == FrontendSelector.FluentFrontendId
                ? new FluentShellSurface(
                    options,
                    FrontendSelector.Select(key, persistedFrontendId: null),
                    controller,
                    appearance,
                    themeManager)
                : CreateV2Content(application, controller, options, themeManager, appearance, themeHome);
            contentCache[key] = content;
            return content;
        }

        var stateStore = new WindowStateMementoStore(Path.Combine(directory, "window-state.json"));
        var initialMemento = stateStore.TryLoad(out _);
        // R-002: every cached content tree (including the hidden one kept for state preservation) must
        // report its live exit state, so leaving a dirty Fluent settings draft or a running workbench
        // cannot be closed silently from the other frontend.
        var window = new PresentationWindow(
            options,
            selection,
            controller,
            appearance,
            journal,
            ContentFactory,
            initialMemento,
            allContentProvider: () => contentCache.Values.ToArray());

        // R-005: clamp the restored placement into the current displays (never restore off-screen).
        if (initialMemento is { } restored)
        {
            ApplyTopologySafePlacement(window, restored);
        }

        window.Closing += (_, args) =>
        {
            if (args.Cancel)
            {
                return; // ExitCoordinator blocked the close; do not persist a cancelled placement.
            }

            try
            {
                stateStore.Save(window.CaptureWindowState(CurrentDisplayId(window)));
            }
            catch (IOException)
            {
                // Placement persistence is best-effort and never blocks closing the window.
            }
        };

        return window;
    }

    /// <summary>R-005: enumerates the current displays for the topology-safe memento restore.</summary>
    private static IReadOnlyList<DisplayInfo> CurrentDisplays(PresentationWindow window)
    {
        try
        {
            return window.Screens.All
                .Select((screen, index) => new DisplayInfo(
                    screen.DisplayName ?? $"screen-{index}",
                    screen.WorkingArea.X,
                    screen.WorkingArea.Y,
                    screen.WorkingArea.Width,
                    screen.WorkingArea.Height,
                    screen.Scaling,
                    screen.IsPrimary))
                .ToArray();
        }
        catch (InvalidOperationException)
        {
            return Array.Empty<DisplayInfo>();
        }
    }

    private static void ApplyTopologySafePlacement(PresentationWindow window, WindowStateMemento memento)
    {
        var displays = CurrentDisplays(window);
        if (displays.Count == 0)
        {
            return;
        }

        var safe = DisplayTopologyPlanner.Clamp(memento, displays);
        window.Width = safe.Width;
        window.Height = safe.Height;
        window.Position = new PixelPoint(safe.X, safe.Y);
    }

    private static string? CurrentDisplayId(PresentationWindow window)
    {
        try
        {
            return window.Screens.ScreenFromWindow(window)?.DisplayName;
        }
        catch (InvalidOperationException)
        {
            return null;
        }
    }

    /// <summary>
    /// R-003: recovers a crash between persisting the switch target and committing the switch journal.
    /// When the persisted document already points at the interrupted target, the last committed frontend
    /// recorded in the journal is restored before the startup decision is made; the journal is then
    /// deterministically rolled back. Never resumes a partially switched UI.
    /// </summary>
    internal static void RecoverInterruptedSwitch(ThemeHomePaths themeHome, AppearanceCoordinator appearance)
    {
        ArgumentNullException.ThrowIfNull(themeHome);
        ArgumentNullException.ThrowIfNull(appearance);
        var directory = Path.GetDirectoryName(themeHome.SettingsFilePath);
        if (string.IsNullOrWhiteSpace(directory))
        {
            return;
        }

        var journal = new SwitchJournal(Path.Combine(directory, "switch-journal.json"));
        var switchCoordinator = new FrontendSwitchCoordinator(journal);
        if (!switchCoordinator.TryRecoverInterrupted(out var interrupted) || interrupted is null)
        {
            return;
        }

        var restored = interrupted.PreviousFrontendId;
        var crashWindowPersistedTarget = string.Equals(appearance.FrontendId, interrupted.TargetFrontendId, StringComparison.Ordinal);
        if (crashWindowPersistedTarget && !string.IsNullOrWhiteSpace(restored))
        {
            try
            {
                appearance.SaveAsync(appearance.Settings with { FrontendId = restored }, CancellationToken.None)
                    .GetAwaiter()
                    .GetResult();
            }
            catch (Exception ex) when (ex is IOException or InvalidOperationException)
            {
                Trace.TraceWarning($"startup recovery: could not restore '{restored}': {ex.GetType().Name}");
            }
        }

        var recovery = $"startup recovery: interrupted switch to '{interrupted.TargetFrontendId}' at {interrupted.Stage}; previous='{restored ?? "<unknown>"}'";
        journal.Rollback(recovery);
        Trace.TraceWarning(recovery);
    }
    /// <summary>FEA-06-PREREQ-2 P5: Theme Studio production wiring (never blocks the shell on failure).</summary>
    private static void WireThemeStudio(
        AppShellV2 shell,
        Application application,
        DesignSystemThemeManager themeManager,
        AppearanceCoordinator appearance,
        ThemeHomePaths themeHome,
        AppOptions options)
    {
        try
        {
            // FEA-06-PREREQ-2 P5 (W-9/Q-32): the Theme Engine's compatibility write mirrors into the
            // canonical presentation-settings.json through this app-side sink; the coordinator stays the
            // single writer of that document.
            var service = ThemeEngineThemeStudioService.CreateProduction(
                application,
                themeManager,
                themeDirectory: themeHome.ThemesDirectory,
                settingsFilePath: themeHome.SettingsFilePath,
                favoritesFilePath: themeHome.FavoritesFilePath,
                presentationSink: new AppearanceThemeSettingsSink(appearance));
            var viewModel = new ThemeStudioViewModel(service);
            var adapter = new ThemeStudioSurfaceAdapter(viewModel, () => shell.ViewModel.CloseThemeStudioCommand.Execute(null));
            shell.ViewModel.RegisterSurfaceWorkspace(adapter);

            // R-002: the stable window's exit gate aggregates hidden content trees; the V2 shell reports
            // the production Theme Studio draft through this seam (the studio commits apply immediately,
            // so an unapplied draft is the only V2 edit buffer that can be lost on close).
            shell.ThemeStudioDraftProvider = () => viewModel.HasDraft;

            // Persisted theme settings are applied asynchronously; the shell is already usable and
            // the surface shows its own error banner if initialization fails.
            Dispatcher.UIThread.Post(async () =>
            {
                try
                {
                    await service.InitializeAsync();

                    // V11R-INT-2: the Theme Studio service applies persisted settings after the shell
                    // has adopted the startup appearance. An explicit --variant must win over the
                    // persisted default, and the shell label must mirror the real palette.
                    if (StartupAppearance(options) is { } requested)
                    {
                        themeManager.SetAppearance(requested);
                    }

                    shell.ViewModel.AdoptAppearance(themeManager.Appearance == DsAppearanceMode.Dark);
                }
                catch (Exception ex) when (ex is InvalidOperationException or IOException or TimeoutException)
                {
                    Trace.TraceWarning($"Theme service init failed: {ex.GetType().Name}");
                }
            });
        }
        catch (Exception ex) when (ex is InvalidOperationException or IOException or ArgumentException)
        {
            // Theme Studio is optional at startup: never block the product shell on it.
            Trace.TraceWarning($"Theme Studio wiring failed: {ex.GetType().Name}");
        }
    }
    /// <summary>Explicit startup appearance from <c>--variant</c> (null = persisted/default wins).</summary>
    private static DsAppearanceMode? StartupAppearance(AppOptions options) =>
        string.IsNullOrWhiteSpace(options.StartupVariant)
            ? null
            : string.Equals(options.StartupVariant, "dark", StringComparison.OrdinalIgnoreCase)
                ? DsAppearanceMode.Dark
                : DsAppearanceMode.Light;

    private static Window CreateLegacyShell(
        IHostController controller,
        AppOptions options,
        DesignSystemThemeManager themeManager) =>
        new MainWindow(controller, options, themeManager: themeManager);

    /// <summary>
    /// Maps the existing <c>--page</c> evidence hook onto all shells. Legacy keeps its page names; v2 maps
    /// the four product surfaces onto the three spaces (reader is an overlay inside Library); the Fluent
    /// skeleton maps them onto its four navigation entries.
    /// </summary>
    private static void NavigateStartupPage(Window window, AppOptions options)
    {
        var page = options.StartupPage!;
        if (window is MainWindow legacy)
        {
            legacy.Navigate(page);
            return;
        }

        if (window is FluentShell fluent)
        {
            fluent.Navigate(page);
            return;
        }

        if (window is PresentationWindow presentation)
        {
            // FEA-07: map the startup page onto whichever content tree the stable window hosts.
            if (presentation.ContentHost.Current is FluentShellSurface fluentSurface)
            {
                fluentSurface.Navigate(page);
                return;
            }

            if (presentation.ContentHost.Current is AppShellV2 presentationShell &&
                SpaceForStartupPage(page) is { } presentationSpace)
            {
                presentationShell.ViewModel.SwitchSpace(presentationSpace);
            }

            return;
        }

        if (window.Content is not AppShellV2 shell)
        {
            return;
        }

        if (SpaceForStartupPage(page) is { } target)
        {
            shell.ViewModel.SwitchSpace(target);
        }
    }

    private static SpaceId? SpaceForStartupPage(string page) =>
        page.ToLowerInvariant() switch
        {
            "bookshelf" or "library" or "reader" => SpaceId.Library,
            "workbench" or "studio" => SpaceId.Studio,
            "settings" or "console" => SpaceId.Console,
            _ => (SpaceId?)null,
        };

    /// <summary>
    /// FEA-07-V2-F11-1: owns the single immersive reader window for the V2 shell. F11 opens it
    /// borderless/fullscreen; F11 or Esc inside closes it and the shell page stays where the user left it.
    /// </summary>
    private static void WireImmersiveReader(AppShellV2 shell, Window host)
    {
        ImmersiveReaderWindow? open = null;
        shell.ViewModel.ImmersiveReaderRequested += (_, _) =>
        {
            if (open is { IsVisible: true })
            {
                open.Close();
                return;
            }

            var window = new ImmersiveReaderWindow(shell.ViewModel.Library.Reader);
            open = window;
            window.Closed += (_, _) =>
            {
                if (ReferenceEquals(open, window))
                {
                    open = null;
                }
            };
            window.Show(host);
        };
    }

}
