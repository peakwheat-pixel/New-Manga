using System.Runtime.InteropServices;
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

    /// <summary>
    /// Best-effort startup-failure log. V11R-A-8: this must NEVER throw — an empty/too-long/read-only
    /// log path used to escape as an unhandled ArgumentException and mask the original startup error
    /// (exit -532462766 with no diagnostic). Invalid paths now degrade to stderr.
    /// </summary>
    internal static void WriteFatal(AppOptions options, string name, string detail)
    {
        try
        {
            var hostOptions = options.ToHostOptions();
            var logDirectory = hostOptions.LogDirectory;
            if (string.IsNullOrWhiteSpace(logDirectory))
            {
                WriteStderr(name, detail, "log directory is empty");
                return;
            }

            Directory.CreateDirectory(logDirectory);
            File.WriteAllText(Path.Combine(logDirectory, name + ".log"), detail);
        }
        catch (Exception logError)
        {
            // Nothing else to do in a windowless startup failure; never crash while trying to log.
            WriteStderr(name, detail, logError.GetType().Name + ": " + logError.Message);
        }
    }

    private static void WriteStderr(string name, string detail, string logFailure)
    {
        try
        {
            Console.Error.WriteLine($"[{name}] {detail}");
            Console.Error.WriteLine($"log unavailable: {logFailure}");
        }
        catch
        {
            // stderr itself can be unavailable in a windowless host; nothing left to report to.
        }
    }
internal static class DpiAwareness
{
    private const int PerMonitorAwareV2 = -4;

    [DllImport("user32.dll")]
    private static extern bool SetProcessDpiAwarenessContext(IntPtr value);

    public static void EnablePerMonitorV2()
    {
        try
        {
            // Manifest already declares PerMonitorV2; this also covers hosts that ignore it.
            _ = SetProcessDpiAwarenessContext(new IntPtr(PerMonitorAwareV2));
        }
        catch (Exception ex) when (ex is DllNotFoundException or EntryPointNotFoundException)
        {
            // pre-Windows 10 1703: manifest <dpiAware>true/pm</dpiAware> still applies
        }
    }
}
}
