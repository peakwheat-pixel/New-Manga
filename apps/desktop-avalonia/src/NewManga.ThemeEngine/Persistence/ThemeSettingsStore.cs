using System.Text;

namespace NewManga.ThemeEngine;

/// <summary>
/// File-backed <see cref="IThemePersistence"/> (contract §4): reads/writes
/// <c>%APPDATA%/NewManga/theme-settings.json</c>, migrates retired theme ids, and never lets a corrupt
/// file block startup (behavior 2/3). Loading always returns usable settings; every recovery is
/// recorded in <see cref="LastLoadIssues"/> for the Theme Studio / diagnostics surface.
/// </summary>
public sealed class ThemeSettingsStore : IThemePersistence
{
    /// <summary>Maximum accepted settings document size (256 KiB; the real document is under 1 KiB).</summary>
    public const int MaxDocumentBytes = 256 * 1024;

    private readonly object _gate = new();
    private readonly string _settingsFilePath;
    private readonly IThemeRegistry? _registry;

    private IReadOnlyList<ThemeValidationIssue> _lastLoadIssues = [];
    private bool _needsSave;

    /// <summary>
    /// Creates a store. <paramref name="settingsFilePath"/> defaults to
    /// <see cref="DefaultSettingsFilePath"/>; <paramref name="registry"/> (optional) lets the loader
    /// distinguish installed user theme ids from unknown ids (refresh it before <see cref="Load"/>).
    /// </summary>
    public ThemeSettingsStore(string? settingsFilePath = null, IThemeRegistry? registry = null)
    {
        _settingsFilePath = string.IsNullOrWhiteSpace(settingsFilePath)
            ? DefaultSettingsFilePath
            : Path.GetFullPath(settingsFilePath);
        _registry = registry;
    }

    /// <summary>Absolute path of the settings document this store owns.</summary>
    public string SettingsFilePath => _settingsFilePath;

    /// <summary>Findings from the most recent <see cref="Load"/> (migration decisions, recovery warnings).</summary>
    public IReadOnlyList<ThemeValidationIssue> LastLoadIssues
    {
        get
        {
            lock (_gate)
            {
                return _lastLoadIssues;
            }
        }
    }

    /// <summary>True when the last load migrated/recovered settings that should be persisted again.</summary>
    public bool NeedsSave
    {
        get
        {
            lock (_gate)
            {
                return _needsSave;
            }
        }
    }

    /// <summary>Roaming application-data directory owned by New Manga.</summary>
    public static string DefaultDirectory { get; } = ResolveDefaultDirectory();

    /// <summary>Default settings document path (<c>%APPDATA%/NewManga/theme-settings.json</c>).</summary>
    public static string DefaultSettingsFilePath => Path.Combine(DefaultDirectory, ThemeDefaults.SettingsFileName);

    /// <summary>Reads settings; never throws for missing/corrupt/unreadable files.</summary>
    public ThemeSettings Load()
    {
        lock (_gate)
        {
            if (!File.Exists(_settingsFilePath))
            {
                _lastLoadIssues = [];
                _needsSave = false;
                return ThemeDefaults.Settings;
            }

            string json;
            try
            {
                var info = new FileInfo(_settingsFilePath);
                if (info.Length > MaxDocumentBytes)
                {
                    _lastLoadIssues =
                    [
                        ThemeValidationIssue.Warning(
                            ThemeIssueCodes.SettingsIoFailed,
                            $"settings file is {info.Length} bytes, above the {MaxDocumentBytes} byte limit; " +
                            "shipped defaults are used",
                            _settingsFilePath),
                    ];
                    _needsSave = false;
                    return ThemeDefaults.Settings;
                }

                json = File.ReadAllText(_settingsFilePath, Encoding.UTF8);
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
            {
                _lastLoadIssues =
                [
                    ThemeValidationIssue.Warning(
                        ThemeIssueCodes.SettingsIoFailed,
                        $"settings file could not be read ({exception.Message}); shipped defaults are used",
                        _settingsFilePath),
                ];
                _needsSave = false;
                return ThemeDefaults.Settings;
            }

            var read = ThemeSettingsJson.Read(json);
            var known = _registry is null
                ? (Func<string, bool>?)null
                : id => _registry.Find(id) is not null;
            var migrated = LegacyThemeMigration.Migrate(read.Settings, known);

            var issues = new List<ThemeValidationIssue>(read.Issues.Count + migrated.Issues.Count);
            issues.AddRange(read.Issues);
            issues.AddRange(migrated.Issues);

            _lastLoadIssues = issues;
            _needsSave = migrated.Changed;
            return migrated.Settings;
        }
    }

    /// <summary>Atomically persists settings (temporary file + replace).</summary>
    public async Task SaveAsync(ThemeSettings settings)
    {
        ArgumentNullException.ThrowIfNull(settings);

        var json = ThemeSettingsJson.Write(settings);
        var directory = Path.GetDirectoryName(_settingsFilePath);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var tempPath = _settingsFilePath + ".tmp";
        try
        {
            await File.WriteAllTextAsync(tempPath, json, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false))
                .ConfigureAwait(false);
            File.Move(tempPath, _settingsFilePath, overwrite: true);
        }
        catch
        {
            TryDelete(tempPath);
            throw;
        }
    }

    private static void TryDelete(string path)
    {
        try
        {
            if (File.Exists(path))
            {
                File.Delete(path);
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            // The temporary file is harmless; the real save failure is already propagating.
        }
    }

    private static string ResolveDefaultDirectory()
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        if (string.IsNullOrWhiteSpace(appData))
        {
            appData = AppContext.BaseDirectory;
        }

        return Path.Combine(appData, "NewManga");
    }
}
