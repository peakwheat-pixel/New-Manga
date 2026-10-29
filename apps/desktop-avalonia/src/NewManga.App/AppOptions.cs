using System.Globalization;
using NewManga.Host;

namespace NewManga.App;

/// <summary>
/// Command-line options for the new shell.
///
/// V11R-A-5 (P0 write policy): the shipped GUI is writable by default — the previous
/// "read-only until S2 parity" default made import / create book / create chapter / Run fail for every
/// release user (the installer shortcut passes no arguments). Writes are now gated by real
/// preconditions instead: the legacy Tauri shell being detected keeps the host read-only, and
/// <c>--parity=false</c> is the explicit operator/test downgrade. <c>--demo-write</c> stays as a
/// compatibility flag for the isolated AC3 demo (it still requires an explicit <c>--data-root</c>).
/// </summary>
public sealed class AppOptions
{
    public string? DataRoot { get; private set; }

    public string? LogDirectory { get; private set; }

    public string? SidecarDirectory { get; private set; }

    public string MutexName { get; private set; } = SingleInstanceGuard.DefaultMutexName;

    /// <summary>
    /// V11R-A-5: true by default (production write policy). <c>--parity=false</c> forces the
    /// migration-era read-only mode for diagnostics/tests; legacy-shell coexistence still overrides.
    /// </summary>
    public bool ParityReached { get; private set; } = true;

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

    /// <summary>
    /// V11R-INT-1: which shell hosts the product. <c>v2</c> is the new Avalonia shell
    /// (AppShellV2: three spaces + Studio dual mode + Theme Studio); <c>legacy</c> keeps the
    /// pre-redesign code-built shell as a one-release rollback path (<c>--shell=legacy</c>).
    /// Default is flipped to <c>v2</c> only after the INT-1 L3 gate passes.
    /// </summary>
    public string Shell { get; private set; } = DefaultShellId;

    /// <summary>INT-1 rollout constant: keep <c>legacy</c> until the new shell passes L3, then flip.</summary>
    public const string DefaultShellId = "legacy";

    /// <summary>True when the new Avalonia shell should host the product.</summary>
    public bool UseV2Shell => string.Equals(Shell, "v2", StringComparison.OrdinalIgnoreCase);

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
                    break;                case "theme":
                case "theme-id":
                    options.StartupThemeId = value;
                    break;
                case "shell":
                    options.Shell = value.Equals("v2", StringComparison.OrdinalIgnoreCase) ? "v2" : "legacy";
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
