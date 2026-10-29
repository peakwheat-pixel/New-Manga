using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Avalonia.Styling;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Views;
using NewManga.DesignSystem.Theming;
using NewManga.Theme;

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
            ThemePackService.ApplyDefault(this);

            // THEME-MACOS-2 evidence hook: deterministic real-machine startup state for screenshots.
            // Applied BEFORE the shell is constructed so code-built page surfaces resolve the requested
            // variant; defaults are untouched when the options are absent.
            if (!string.IsNullOrWhiteSpace(options.StartupThemeId))
            {
                ThemePackService.Apply(this, ThemePacks.ById(options.StartupThemeId));
            }

            if (!string.IsNullOrWhiteSpace(options.StartupVariant))
            {
                ThemePackService.ApplyVariant(
                    this,
                    string.Equals(options.StartupVariant, "dark", StringComparison.OrdinalIgnoreCase)
                        ? ThemeVariant.Dark
                        : ThemeVariant.Light);
            }

            // V11R-D-1: normalize the design-system resource stack (palette + overlays) after the
            // legacy theme pack has been applied. The startup appearance (--variant / persisted choice)
            // is passed in so initialization never silently overrides a known user preference; only an
            // absent choice falls back to the design-system default (dark).
            var startupAppearance = string.IsNullOrWhiteSpace(options.StartupVariant)
                ? (AppearanceMode?)null
                : string.Equals(options.StartupVariant, "dark", StringComparison.OrdinalIgnoreCase)
                    ? AppearanceMode.Dark
                    : AppearanceMode.Light;
            _designSystemTheme = new DesignSystemThemeManager(this);
            _designSystemTheme.Initialize(startupAppearance);

            var controller = new HostController(options.ToHostOptions());
            var window = new MainWindow(controller, options);
            desktop.MainWindow = window;
            desktop.ShutdownMode = ShutdownMode.OnMainWindowClose;

            if (!string.IsNullOrWhiteSpace(options.StartupThemeId) || !string.IsNullOrWhiteSpace(options.StartupVariant))
            {
                window.ApplyTheme();
            }

            if (!string.IsNullOrWhiteSpace(options.StartupPage))
            {
                window.Navigate(options.StartupPage);
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
}
