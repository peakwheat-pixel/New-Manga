// Minimal Avalonia 11 app used only to measure publish size / startup.
// Not product code; lives under verification/DISPLAY-PERF-DECISION-1/ui-stack/_spike.
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Media;
using Avalonia.Themes.Fluent;

namespace avalonia_size;

public sealed class App : Application
{
    public override void Initialize()
    {
        Styles.Add(new FluentTheme());
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new Window
            {
                Title = "avalonia-size spike",
                Width = 800,
                Height = 600,
                TransparencyLevelHint = new[] { WindowTransparencyLevel.Mica },
                Background = Brushes.Transparent,
                Content = new TextBlock
                {
                    Text = "spike",
                    FontSize = 20,
                    Margin = new Thickness(24),
                },
            };
            desktop.MainWindow.Opened += (_, _) =>
            {
                System.Console.WriteLine("OPENED");
            };
        }

        base.OnFrameworkInitializationCompleted();
    }
}

public static class Program
{
    [System.STAThread]
    public static void Main(string[] args) =>
        AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .LogToTrace()
            .StartWithClassicDesktopLifetime(args);
}
