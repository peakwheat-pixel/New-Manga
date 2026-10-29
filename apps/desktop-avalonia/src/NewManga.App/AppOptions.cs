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
    /// V11R-C-3 compatibility hook: accepts a retired theme id via <c>--theme</c>/<c>--theme-id</c> and
    /// maps it through <c>LegacyThemeMigration</c> to the shipped default (newmanga-default). It no longer
    /// selects an old theme pack; null keeps the normal design-system default and appearance handling.
    /// </summary>
    public string? StartupThemeId { get; private set; }

    /// <summary>
    /// V11R-INT-1: which shell hosts the product. <c>v2</c> is the new Avalonia shell
    /// (AppShellV2: three spaces + Studio dual mode + Theme Studio); <c>legacy</c> keeps the
    /// pre-redesign code-built shell as a one-release rollback path (<c>--shell=legacy</c>).
    /// Default flipped to <c>v2</c> for V11R-INT-1 (L3 gate); <c>--shell=legacy</c> remains the one-release rollback.
    /// </summary>
    public string Shell { get; private set; } = DefaultShellId;

    /// <summary>INT-1 rollout constant: keep <c>legacy</c> until the new shell passes L3, then flip.</summary>
    public const string DefaultShellId = "v2";

    /// <summary>True when the new Avalonia shell should host the product.</summary>
    public bool UseV2Shell => string.Equals(Shell, "v2", StringComparison.OrdinalIgnoreCase);

    /// <summary>THEME-MACOS-2 evidence hook: <c>light</c> / <c>dark</c> for the startup theme variant.</summary>
    public string? StartupVariant { get; private set; }

    /// <summary>THEME-MACOS-2 evidence hook: page to open after start (<c>bookshelf</c> / <c>settings</c> / <c>workbench</c> / <c>reader</c>).</summary>
    public string? StartupPage { get; private set; }

    /// <summary>Options that carry a value (both <c>--key=value</c> and <c>--key value</c> are accepted).</summary>
    private static readonly HashSet<string> ValueKeys = new(StringComparer.Ordinal)
    {
        "data-root", "log-dir", "sidecar-dir", "mutex-name",
        "theme", "theme-id", "shell", "variant", "page",
        "exit-after", "width", "height",
    };

    /// <summary>Flags that may be written bare (<c>--parity</c> == <c>--parity=true</c>).</summary>
    private static readonly HashSet<string> BooleanSwitchKeys = new(StringComparer.Ordinal)
    {
        "parity", "demo-write", "auto-roundtrip", "smoke",
    };

    /// <summary>Flags whose value is optional (<c>--legacy-shell-check</c> == on; <c>=off</c> disables).</summary>
    private static readonly HashSet<string> OptionalValueKeys = new(StringComparer.Ordinal)
    {
        "legacy-shell-check",
    };

    public static AppOptions Parse(string[] args)
    {
        var options = new AppOptions();
        for (var index = 0; index < args.Length; index++)
        {
            var raw = args[index];
            if (!raw.StartsWith("--", StringComparison.Ordinal))
            {
                options.InvalidReason =
                    $"unexpected positional argument '{raw}'; options must be --key=value or --key value";
                return options;
            }

            var body = raw[2..];
            if (body.Length == 0)
            {
                options.InvalidReason = "empty option '--'; options must be --key=value or --key value";
                return options;
            }

            var separator = body.IndexOf('=');
            var key = (separator < 0 ? body : body[..separator]).ToLowerInvariant();
            string? value = separator < 0 ? null : body[(separator + 1)..];

            // An explicitly empty value (--log-dir=) is never valid: it used to reach
            // Program.WriteFatal with an empty path and crash there instead of reporting the real error.
            if (value is { Length: 0 })
            {
                options.InvalidReason = $"--{key} requires a non-empty value";
                return options;
            }

            if (value is null)
            {
                if (BooleanSwitchKeys.Contains(key))
                {
                    value = "true";
                }
                else if (OptionalValueKeys.Contains(key))
                {
                    value = "on";
                }
                else if (ValueKeys.Contains(key))
                {
                    // Space-separated form: consume the next token unless it is another option.
                    if (index + 1 < args.Length &&
                        !args[index + 1].StartsWith("--", StringComparison.Ordinal))
                    {
                        index++;
                        value = args[index];
                    }
                    else
                    {
                        options.InvalidReason =
                            $"--{key} requires a value (use --{key}=<value> or --{key} <value>)";
                        return options;
                    }
                }
                else
                {
                    options.InvalidReason = $"unknown option '--{key}'";
                    return options;
                }
            }
            else if (!ValueKeys.Contains(key) && !BooleanSwitchKeys.Contains(key) &&
                     !OptionalValueKeys.Contains(key))
            {
                options.InvalidReason = $"unknown option '--{key}'";
                return options;
            }

            if (!TryApply(options, key, value))
            {
                return options;
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

    /// <summary>Applies one validated option; returns false with <see cref="InvalidReason"/> when invalid.</summary>
    private static bool TryApply(AppOptions options, string key, string value)
    {
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
            case "theme-id":
                options.StartupThemeId = value;
                break;
            case "shell":
                if (!value.Equals("v2", StringComparison.OrdinalIgnoreCase) &&
                    !value.Equals("legacy", StringComparison.OrdinalIgnoreCase))
                {
                    options.InvalidReason = $"--shell must be 'v2' or 'legacy' (got '{value}')";
                    return false;
                }

                options.Shell = value.Equals("v2", StringComparison.OrdinalIgnoreCase) ? "v2" : "legacy";
                break;
            case "variant":
                options.StartupVariant = value;
                break;
            case "page":
                options.StartupPage = value;
                break;
            case "exit-after":
                if (!TryParseNonNegativeInt(value, out var exitAfter))
                {
                    options.InvalidReason = $"--exit-after requires a non-negative integer (got '{value}')";
                    return false;
                }

                options.ExitAfterMs = exitAfter;
                break;
            case "smoke":
                options.ExitAfterMs ??= 1500;
                break;
            case "width":
                if (!TryParsePositiveInt(value, out var width))
                {
                    options.InvalidReason = $"--width requires a positive integer (got '{value}')";
                    return false;
                }

                options.WindowWidth = width;
                break;
            case "height":
                if (!TryParsePositiveInt(value, out var height))
                {
                    options.InvalidReason = $"--height requires a positive integer (got '{value}')";
                    return false;
                }

                options.WindowHeight = height;
                break;
            default:
                options.InvalidReason = $"unknown option '--{key}'";
                return false;
        }

        return true;
    }

    private static bool TryParseNonNegativeInt(string value, out int parsed) =>
        int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out parsed) && parsed >= 0;

    private static bool TryParsePositiveInt(string value, out int parsed) =>
        int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out parsed) && parsed > 0;

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
