using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
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
            ThemeManager.Apply(this, ThemeManager.Light);
            var controller = new HostController(options.ToHostOptions());
            var window = new MainWindow(controller, options);
            desktop.MainWindow = window;
            desktop.ShutdownMode = ShutdownMode.OnMainWindowClose;
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
