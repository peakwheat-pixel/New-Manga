namespace NewManga.App.Services;

/// <summary>
/// V11R-E2E-1: the three persistence paths the theme subsystem owns, resolved once at startup.
/// </summary>
/// <param name="SettingsFilePath">Absolute path of <c>theme-settings.json</c>.</param>
/// <param name="ThemesDirectory">Absolute path of the user theme directory (<c>themes</c>).</param>
/// <param name="FavoritesFilePath">Absolute path of <c>theme-studio-favorites.json</c>.</param>
/// <param name="IsCustom">True when <c>--theme-home</c> overrode the roaming app-data location.</param>
public sealed record ThemeHomePaths(
    string SettingsFilePath,
    string ThemesDirectory,
    string FavoritesFilePath,
    bool IsCustom);

/// <summary>
/// V11R-E2E-1 (FOLLOW-UP-E2E-1): resolves the theme subsystem's persistence root.
///
/// Without <c>--theme-home</c> the shipped behavior is unchanged: everything lives under
/// <c>%APPDATA%/NewManga</c> (see <see cref="NewManga.ThemeEngine.ThemeSettingsStore.DefaultDirectory"/>).
/// With <c>--theme-home &lt;dir&gt;</c> (or <c>--theme-home=&lt;dir&gt;</c>) the whole subsystem moves to
/// that directory so E2E / multi-instance / portable runs never touch the real user data:
/// <list type="bullet">
/// <item><c>&lt;dir&gt;/theme-settings.json</c></item>
/// <item><c>&lt;dir&gt;/themes</c></item>
/// <item><c>&lt;dir&gt;/theme-studio-favorites.json</c></item>
/// </list>
/// This resolver is pure (no Avalonia dependency) so it is unit-testable and has a single call site in
/// <c>App.CreateV2Shell</c>, which passes the three paths to
/// <c>ThemeEngineThemeStudioService.CreateProduction</c>.
/// </summary>
public static class ThemeHome
{
    /// <summary>File name of the persisted settings document (contract §4).</summary>
    public const string SettingsFileName = "theme-settings.json";

    /// <summary>Directory name scanned for user theme packages (contract §4/§5).</summary>
    public const string ThemesDirectoryName = "themes";

    /// <summary>File name of the Theme Studio favorites document.</summary>
    public const string FavoritesFileName = "theme-studio-favorites.json";

    /// <summary>Shipped roaming location (<c>%APPDATA%/NewManga</c>), used when no override is given.</summary>
    public static string DefaultDirectory => NewManga.ThemeEngine.ThemeSettingsStore.DefaultDirectory;

    /// <summary>The paths used when no <c>--theme-home</c> override is present (identical to shipped behavior).</summary>
    public static ThemeHomePaths Default { get; } = Build(DefaultDirectory, isCustom: false);

    /// <summary>Resolves the paths from parsed CLI options.</summary>
    public static ThemeHomePaths Resolve(AppOptions options)
    {
        ArgumentNullException.ThrowIfNull(options);
        return Resolve(options.ThemeHome);
    }

    /// <summary>
    /// Resolves the paths from a raw <c>--theme-home</c> value. Null/blank keeps the default (the CLI
    /// parser already rejects blank values with <c>InvalidReason</c> + exit 2; this guard keeps the
    /// resolver total for tests and future callers).
    /// </summary>
    public static ThemeHomePaths Resolve(string? themeHome)
    {
        if (string.IsNullOrWhiteSpace(themeHome))
        {
            return Default;
        }

        var root = Path.GetFullPath(themeHome.Trim());
        return Build(root, isCustom: true);
    }

    private static ThemeHomePaths Build(string root, bool isCustom) => new(
        Path.Combine(root, SettingsFileName),
        Path.Combine(root, ThemesDirectoryName),
        Path.Combine(root, FavoritesFileName),
        isCustom);
}
