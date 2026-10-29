namespace NewManga.ThemeEngine;

/// <summary>One entry of the old-theme-id migration table (retirement plan §2.1).</summary>
/// <param name="LegacyId">Old persisted theme id.</param>
/// <param name="OldName">Old display name (kept for evidence/UI copy).</param>
/// <param name="Appearance">Appearance the migrated settings must use, or null to keep the configured one.</param>
/// <param name="ForceCompactDensity">True when the old pack's shelf density maps to <see cref="Density.Compact"/>.</param>
public sealed record LegacyThemeMapping(
    string LegacyId,
    string OldName,
    AppearanceMode? Appearance,
    bool ForceCompactDensity);

/// <summary>Result of migrating persisted settings away from a retired theme id.</summary>
/// <param name="Settings">The migrated settings.</param>
/// <param name="Issues">Warnings explaining every migration decision.</param>
/// <param name="Changed">True when the settings differ from the input and should be re-saved.</param>
public sealed record ThemeMigrationResult(
    ThemeSettings Settings,
    IReadOnlyList<ThemeValidationIssue> Issues,
    bool Changed);

/// <summary>
/// Old theme id → <c>newmanga-default</c> migration (V11R_THEME_RETIREMENT_PLAN §2.1). The old packs
/// (saber-purple / saber-light / midnight / sakura / emerald / mono / macos-*) are retired; their
/// configuration must land on the shipped default theme with a preserved appearance, never crash the
/// app and always record one warning per decision. Unknown ids recovered to the default theme are
/// logged as warnings too; genuinely unknown ids are only treated as unknown when no registry lookup
/// confirms them (a user-installed theme id must survive).
/// </summary>
public static class LegacyThemeMigration
{
    /// <summary>The migration table, keyed by old theme id (retirement plan §2.1).</summary>
    public static IReadOnlyDictionary<string, LegacyThemeMapping> Mappings { get; } = new Dictionary<string, LegacyThemeMapping>(StringComparer.Ordinal)
    {
        ["saber-purple"] = new("saber-purple", "Saber Purple", AppearanceMode.Dark, ForceCompactDensity: false),
        ["saber-light"] = new("saber-light", "Saber Light", AppearanceMode.Light, ForceCompactDensity: false),
        ["midnight"] = new("midnight", "Midnight", AppearanceMode.Dark, ForceCompactDensity: false),
        ["sakura"] = new("sakura", "Sakura", AppearanceMode.Light, ForceCompactDensity: false),
        ["emerald"] = new("emerald", "Emerald", AppearanceMode.Dark, ForceCompactDensity: false),
        ["mono"] = new("mono", "Mono", AppearanceMode.Dark, ForceCompactDensity: false),
        ["macos-sonoma"] = new("macos-sonoma", "macOS Sonoma", null, ForceCompactDensity: false),
        ["macos-launchpad"] = new("macos-launchpad", "macOS Launchpad", null, ForceCompactDensity: true),
        ["macos-split"] = new("macos-split", "macOS Split", null, ForceCompactDensity: false),
    };

    /// <summary>Legacy aliases for the shipped default theme id itself.</summary>
    private static readonly string[] DefaultAliases =
    [
        "newmanga-default",
        "newmanga.default",
        "default",
    ];

    /// <summary>
    /// Migrates one settings document. <paramref name="isKnownTheme"/> answers whether an id belongs to
    /// the current catalog (built-in or installed user theme); when null, unknown non-legacy ids are
    /// preserved untouched (callers that have no registry should pass null and validate later).
    /// </summary>
    public static ThemeMigrationResult Migrate(ThemeSettings settings, Func<string, bool>? isKnownTheme = null)
    {
        ArgumentNullException.ThrowIfNull(settings);

        var issues = new List<ThemeValidationIssue>(capacity: 2);
        var themeId = settings.ThemeId?.Trim() ?? string.Empty;

        if (themeId.Length == 0)
        {
            // First run / missing id: land on the shipped default and let the configured appearance stand
            // (the reader has already defaulted it to System when the file did not specify one).
            var defaults = settings with { ThemeId = ThemeDefaults.DefaultThemeId };
            return new ThemeMigrationResult(defaults, issues, Changed: !string.Equals(settings.ThemeId, defaults.ThemeId, StringComparison.Ordinal));
        }

        if (DefaultAliases.Contains(themeId, StringComparer.OrdinalIgnoreCase))
        {
            if (string.Equals(themeId, ThemeDefaults.DefaultThemeId, StringComparison.Ordinal))
            {
                return new ThemeMigrationResult(settings, issues, Changed: false);
            }

            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.SettingsLegacyThemeId,
                $"theme id '{themeId}' is an alias of '{ThemeDefaults.DefaultThemeId}'; settings were normalized",
                "themeId"));
            return new ThemeMigrationResult(
                settings with { ThemeId = ThemeDefaults.DefaultThemeId },
                issues,
                Changed: true);
        }

        if (Mappings.TryGetValue(themeId, out var mapping))
        {
            var layout = mapping.ForceCompactDensity && settings.Layout.Density == Density.Comfortable
                ? settings.Layout with { Density = Density.Compact }
                : settings.Layout;
            var migrated = settings with
            {
                ThemeId = ThemeDefaults.DefaultThemeId,
                Appearance = mapping.Appearance ?? settings.Appearance,
                Layout = layout,
            };
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.SettingsLegacyThemeId,
                $"retired theme '{mapping.OldName}' ({mapping.LegacyId}) was migrated to " +
                $"'{ThemeDefaults.DefaultThemeId}'" +
                (mapping.Appearance is { } appearance ? $" with appearance '{appearance}'" : " keeping the configured appearance") +
                (layout.Density != settings.Layout.Density ? " and compact shelf density" : string.Empty),
                "themeId"));
            return new ThemeMigrationResult(migrated, issues, Changed: true);
        }

        if (isKnownTheme is not null && !isKnownTheme(themeId))
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.SettingsUnknownThemeId,
                $"configured theme '{themeId}' is not installed; recovered to '{ThemeDefaults.DefaultThemeId}' with dark appearance",
                "themeId"));
            return new ThemeMigrationResult(
                settings with
                {
                    ThemeId = ThemeDefaults.DefaultThemeId,
                    Appearance = AppearanceMode.Dark,
                },
                issues,
                Changed: true);
        }

        return new ThemeMigrationResult(settings, issues, Changed: false);
    }
}
