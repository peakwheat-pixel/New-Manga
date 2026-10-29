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
using NewManga.DesignSystem.Theming;

namespace NewManga.App;

public partial class App : Application
{
    /// <summary>
    /// V11R-D-1: owns the application-wide design-system resource stack. Created in
    /// <see cref="OnFrameworkInitializationCompleted"/> before the shell so every control resolves
    /// <c>Nm.*</c> tokens on first layout; later theme switches only swap resource dictionaries.
    /// </summary>
    private DesignSystemThemeManager? _designSystemTheme;

    public override void Initialize() => AvaloniaXamlLoader.Load(this);

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            var options = AppOptionsStore.Current;

            // V11R-C-3: the old theme-pack startup hook is retired. `--theme` stays as a compatibility
            // argument: LegacyStartupTheme maps it through the ThemeEngine migration table and carries the
            // retired pack's appearance/density into the DesignSystem manager below.
            var startupTheme = LegacyStartupTheme.Resolve(options.StartupThemeId, options.StartupVariant);

            // V11R-D-1: normalize the design-system resource stack (palette + overlays) after the
            // legacy theme pack has been applied. The startup appearance (--variant / --theme / persisted
            // choice) is passed in so initialization never silently overrides a known user preference;
            // only an absent choice falls back to the design-system default (dark).
            var startupAppearance = startupTheme.Appearance;
            _designSystemTheme = new DesignSystemThemeManager(this);
            _designSystemTheme.Initialize(startupAppearance);
            if (startupTheme.Density is { } startupDensity &&
                !_designSystemTheme.SetDensity(startupDensity))
            {
                System.Diagnostics.Trace.TraceWarning(
                    $"legacy --theme density could not be applied: {_designSystemTheme.LastError}");
            }

            var controller = new HostController(options.ToHostOptions());
            var window = options.UseV2Shell
                ? CreateV2Shell(controller, options)
                : CreateLegacyShell(controller, options);

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
    /// V11R-INT-1: the new Avalonia shell (three spaces + Studio dual mode + Theme Studio surface).
    /// Theme Studio is bound to the real theme engine and shares the application's single
    /// <see cref="DesignSystemThemeManager"/> (two managers would fight over the same resource layer).
    /// </summary>
    private Window CreateV2Shell(HostController controller, AppOptions options)
    {
        var root = AppShellV2.CreateRoot(controller, options, picker: null, themeManager: _designSystemTheme);
        if (root.Content is not AppShellV2 shell || _designSystemTheme is null)
        {
            return root;
        }

        try
        {
            var service = ThemeEngineThemeStudioService.CreateProduction(this, _designSystemTheme);
            var viewModel = new ThemeStudioViewModel(service);
            var adapter = new ThemeStudioSurfaceAdapter(viewModel, () => shell.ViewModel.CloseThemeStudioCommand.Execute(null));
            shell.ViewModel.RegisterSurfaceWorkspace(adapter);

            // Persisted theme settings are applied asynchronously; the shell is already usable and
            // the surface shows its own error banner if initialization fails.
            Dispatcher.UIThread.Post(async () =>
            {
                try
                {
                    await service.InitializeAsync();
                }
                catch (Exception ex) when (ex is InvalidOperationException or IOException or TimeoutException)
                {
                    System.Diagnostics.Trace.TraceWarning($"Theme service init failed: {ex.GetType().Name}");
                }
            });
        }
        catch (Exception ex) when (ex is InvalidOperationException or IOException or ArgumentException)
        {
            // Theme Studio is optional at startup: never block the product shell on it.
            System.Diagnostics.Trace.TraceWarning($"Theme Studio wiring failed: {ex.GetType().Name}");
        }

        return root;
    }

    private Window CreateLegacyShell(HostController controller, AppOptions options) =>
        new MainWindow(controller, options, themeManager: _designSystemTheme);

    /// <summary>
    /// Maps the existing <c>--page</c> evidence hook onto both shells. Legacy keeps its page names;
    /// v2 maps the four product surfaces onto the three spaces (reader is an overlay inside Library).
    /// </summary>
    private static void NavigateStartupPage(Window window, AppOptions options)
    {
        var page = options.StartupPage!;
        if (window is MainWindow legacy)
        {
            legacy.Navigate(page);
            return;
        }

        if (window.Content is not AppShellV2 shell)
        {
            return;
        }

        var space = page.ToLowerInvariant() switch
        {
            "bookshelf" or "library" or "reader" => SpaceId.Library,
            "workbench" or "studio" => SpaceId.Studio,
            "settings" or "console" => SpaceId.Console,
            _ => (SpaceId?)null,
        };

        if (space is { } target)
        {
            shell.ViewModel.SwitchSpace(target);
        }
    }
}


