using Avalonia;

namespace NewManga.App;

public static class Program
{
    [STAThread]
    public static int Main(string[] args)
    {
        var options = AppOptions.Parse(args);
        AppOptionsStore.Current = options;
        if (options.InvalidReason is not null)
        {
            WriteFatal(options, "invalid-arguments", options.InvalidReason);
            return 2;
        }

        try
        {
            BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
            return 0;
        }
        catch (Exception ex)
        {
            WriteFatal(options, "fatal", ex.ToString());
            return 1;
        }
    }

    public static AppBuilder BuildAvaloniaApp() =>
        AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .LogToTrace();

    private static void WriteFatal(AppOptions options, string name, string detail)
    {
        try
        {
            var hostOptions = options.ToHostOptions();
            Directory.CreateDirectory(hostOptions.LogDirectory);
            File.WriteAllText(Path.Combine(hostOptions.LogDirectory, name + ".log"), detail);
        }
        catch (Exception logError) when (logError is IOException or UnauthorizedAccessException)
        {
            // nothing else to do in a windowless startup failure
        }
    }
}
