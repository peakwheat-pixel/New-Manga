using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace NewManga.Appearance;

/// <summary>
/// C-03 §2.1: the appearance writer. Order discipline: the legacy settings file is
/// read once, never modified; the new document is written atomically (temp + replace)
/// so a crash cannot leave a half-written file. Corrupt files fall back to defaults
/// with warnings and never block startup.
/// </summary>
public sealed class AppearanceStore
{
    private readonly string _path;
    private readonly string? _legacyPath;

    public AppearanceStore(string path, string? legacyPath = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        _path = path;
        _legacyPath = legacyPath ?? Path.Combine(
            Path.GetDirectoryName(Path.GetFullPath(path)) ?? ".",
            "theme-settings.json");
    }

    /// <summary>The legacy document read before the first write (null until then).</summary>
    public string? LegacyDocument { get; private set; }

    /// <summary>Reads the document; a missing file yields defaults.</summary>
    public AppearanceReadResult Read()
    {
        if (!File.Exists(_path))
        {
            // C-03 §2.2: the first run must migrate the legacy theme-settings.json instead
            // of silently falling back to defaults.
            if (_legacyPath is not null && File.Exists(_legacyPath))
            {
                var legacy = File.ReadAllText(_legacyPath);
                LegacyDocument ??= legacy;
                var migrated = AppearanceJson.Read(legacy);
                var warnings = new List<string>(migrated.Warnings)
                {
                    "legacy theme-settings.json migrated into presentation-settings.json",
                };
                return new AppearanceReadResult(migrated.Settings, warnings) { DocumentParsed = true };
            }

            return new AppearanceReadResult(AppearanceDefaults.Settings, Array.Empty<string>())
            {
                DocumentParsed = false,
            };
        }

        var text = File.ReadAllText(_path);
        LegacyDocument ??= text;
        return AppearanceJson.Read(text);
    }

    /// <summary>Writes atomically (same-directory temp file + replace).</summary>
    public async Task WriteAsync(AppearanceSettings settings, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(settings);

        var directory = Path.GetDirectoryName(Path.GetFullPath(_path));
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var json = AppearanceJson.Write(settings);
        var temporary = _path + ".tmp";
        await File.WriteAllTextAsync(temporary, json, cancellationToken).ConfigureAwait(false);
        File.Move(temporary, _path, overwrite: true);
    }
}
