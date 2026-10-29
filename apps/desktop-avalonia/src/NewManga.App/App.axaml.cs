using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Avalonia.Styling;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Views;
using NewManga.Theme;

namespace NewManga.App;

public partial class App : Application
{
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
