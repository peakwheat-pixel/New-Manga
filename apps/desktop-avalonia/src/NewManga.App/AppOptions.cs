using System.Globalization;
using NewManga.Host;

namespace NewManga.App;

/// <summary>
/// Command-line options for the new shell. S1 intentionally defaults to the shared production data
/// root in read-only mode; writes are only possible with an explicit isolated data root
/// (<c>--data-root</c>) plus <c>--demo-write</c>, which is what the AC3 demo/evidence run uses.
/// </summary>
public sealed class AppOptions
{
    public string? DataRoot { get; private set; }

    public string? LogDirectory { get; private set; }

    public string? SidecarDirectory { get; private set; }

    public string MutexName { get; private set; } = SingleInstanceGuard.DefaultMutexName;

    public bool ParityReached { get; private set; }

    public bool DemoWrite { get; private set; }

    public bool DetectLegacyShell { get; private set; } = true;

    /// <summary>Demo/evidence: click the AC3 Chinese vector automatically after host start.</summary>
    public bool AutoRoundTrip { get; private set; }

    public int? ExitAfterMs { get; private set; }

    public string? InvalidReason { get; private set; }

    public int WindowWidth { get; private set; } = 1100;

    public int WindowHeight { get; private set; } = 760;

    /// <summary>
    /// THEME-MACOS-2 evidence hook: start the real shell on a given ThemePack id
    /// (e.g. <c>macos-sonoma</c>), so real-machine screenshots of one variant are reproducible without
    /// pointer automation. Null keeps the normal default theme (saber-purple).
    /// </summary>
    public string? StartupThemeId { get; private set; }

    /// <summary>THEME-MACOS-2 evidence hook: <c>light</c> / <c>dark</c> for the startup theme variant.</summary>
    public string? StartupVariant { get; private set; }

    /// <summary>THEME-MACOS-2 evidence hook: page to open after start (<c>bookshelf</c> / <c>settings</c> / <c>workbench</c> / <c>reader</c>).</summary>
    public string? StartupPage { get; private set; }

    public static AppOptions Parse(string[] args)
    {
        var options = new AppOptions();
        foreach (var raw in args)
        {
            if (!raw.StartsWith("--", StringComparison.Ordinal))
            {
                continue;
            }

            var body = raw[2..];
            var separator = body.IndexOf('=');
            var key = (separator < 0 ? body : body[..separator]).ToLowerInvariant();
            var value = separator < 0 ? "true" : body[(separator + 1)..];
            switch (key)
            {
                case "data-root":
                    options.DataRoot = value;
                    break;
                case "log-dir":
                    options.LogDirectory = value;
                    break;
                case "sidecar-dir":
                    options.SidecarDirectory = value;
                    break;
                case "mutex-name":
                    options.MutexName = value;
                    break;
                case "parity":
                    options.ParityReached = !value.Equals("false", StringComparison.OrdinalIgnoreCase);
                    break;
                case "demo-write":
                    options.DemoWrite = !value.Equals("false", StringComparison.OrdinalIgnoreCase);
                    break;
                case "auto-roundtrip":
                    options.AutoRoundTrip = !value.Equals("false", StringComparison.OrdinalIgnoreCase);
                    break;
                case "legacy-shell-check":
                    options.DetectLegacyShell = !value.Equals("off", StringComparison.OrdinalIgnoreCase);
                    break;
                case "theme":
                    options.StartupThemeId = value;
                    break;
                case "variant":
                    options.StartupVariant = value;
                    break;
                case "page":
                    options.StartupPage = value;
                    break;
                case "exit-after":
                    options.ExitAfterMs = int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed)
                        ? parsed
                        : 2000;
                    break;
                case "smoke":
                    options.ExitAfterMs ??= 1500;
                    break;
                case "width":
                    options.WindowWidth = int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var width) ? width : 1100;
                    break;
                case "height":
                    options.WindowHeight = int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var height) ? height : 760;
                    break;
            }
        }

        if (options.DemoWrite)
        {
            if (string.IsNullOrWhiteSpace(options.DataRoot))
            {
                options.InvalidReason = "--demo-write requires an explicit isolated --data-root (production data stays read-only in S1)";
                return options;
            }

            options.ParityReached = true;
        }

        return options;
    }

    public HostOptions ToHostOptions()
    {
        var dataRoot = DataRoot ?? Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "com.newmanga.desktop");
        var logDirectory = LogDirectory ?? Path.Combine(dataRoot, "logs");
        return new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = logDirectory,
            SidecarDirectoryOverride = SidecarDirectory,
            MutexName = MutexName,
            ParityReached = ParityReached,
            DetectLegacyShell = DetectLegacyShell,
        };
    }
}

public static class AppOptionsStore
{
    public static AppOptions Current { get; set; } = new();
}
