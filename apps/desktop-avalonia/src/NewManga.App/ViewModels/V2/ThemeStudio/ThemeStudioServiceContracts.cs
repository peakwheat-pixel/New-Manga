using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// The Theme Studio's UI facade (THEME_STUDIO_SPEC §4). The surface only talks to this interface, so the
/// production implementation over the real <see cref="IThemeService"/> and the deterministic sandbox used
/// by tests are interchangeable, and the "STUB / 未持久化" labels are driven by
/// <see cref="Capabilities"/> rather than by hard-coded copy.
/// </summary>
public interface IThemeStudioService : IDisposable
{
    /// <summary>What this instance can actually do (drives honest apply labels).</summary>
    ThemeStudioCapabilities Capabilities { get; }

    /// <summary>The applied (committed) settings.</summary>
    ThemeSettings Settings { get; }

    /// <summary>Descriptor of the applied theme.</summary>
    ThemeDescriptor CurrentTheme { get; }

    /// <summary>The applied package (never null once <see cref="InitializeAsync"/> succeeded).</summary>
    ThemePackage AppliedPackage { get; }

    /// <summary>Every installed theme, ordinal by id.</summary>
    IReadOnlyList<ThemePackage> Themes { get; }

    /// <summary>Legacy/unknown-id migration decisions disclosed by the engine (retirement plan §2.1).</summary>
    IReadOnlyList<ThemeStudioMigrationNotice> MigrationNotices { get; }

    /// <summary>Catalog-level findings (quarantined theme files, built-in load problems).</summary>
    ThemeStudioValidationReport StartupIssues { get; }

    /// <summary>Findings from the last initialize/apply/change (fallback explanations).</summary>
    IReadOnlyList<ThemeStudioIssue> LastIssues { get; }

    /// <summary>Raised after any applied-state or catalog change.</summary>
    event EventHandler? Changed;

    /// <summary>Loads settings + catalog and applies the persisted theme. Never throws on corrupt input.</summary>
    Task InitializeAsync(CancellationToken ct = default);

    /// <summary>
    /// The package being previewed/edited, or null when nothing is pending. It is the preview session's
    /// theme for an installed selection, or an in-memory package for unsaved editor changes.
    /// </summary>
    ThemePackage? DraftPackage { get; }

    /// <summary>
    /// True when <see cref="DraftPackage"/> is an in-memory (not installed) package, i.e. the editor holds
    /// token edits. The surface then renders the draft through a scoped palette instead of the engine's
    /// application-wide preview session (which only accepts installed theme ids).
    /// </summary>
    bool IsDraftPackageScoped { get; }

    /// <summary>True when the draft differs from the applied state (THEME_STUDIO_SPEC §4 HasDraft).</summary>
    bool HasDraft { get; }

    /// <summary>Opens the preview session (idempotent; a second call rolls the previous session back).</summary>
    void BeginPreview();

    /// <summary>Previews an installed theme id through the real <c>IThemePreviewEngine</c> session.</summary>
    void PreviewTheme(string themeId);

    /// <summary>Previews an edited, not-yet-installed package (live editor changes).</summary>
    void PreviewDocument(ThemePackage package);

    /// <summary>Discards the draft and rolls the preview session back to the applied state.</summary>
    Task CancelPreviewAsync(CancellationToken ct = default);

    /// <summary>
    /// Commits the draft: "应用" = commit + persist. Token edits are saved as a user theme first so the
    /// applied personality survives a restart; the result records whether it was durable.
    /// </summary>
    Task<ThemeStudioApplyResult> ApplyAsync(CancellationToken ct = default);

    /// <summary>Switches appearance immediately (settings are not theme packages; §3.5).</summary>
    Task SetAppearanceAsync(AppearanceMode mode, CancellationToken ct = default);

    /// <summary>Switches standard/high contrast immediately.</summary>
    Task SetContrastAsync(ContrastMode mode, CancellationToken ct = default);

    /// <summary>Switches density immediately.</summary>
    Task SetDensityAsync(Density density, CancellationToken ct = default);

    /// <summary>Toggles reduced motion immediately (system preference may pre-empt it).</summary>
    Task SetReducedMotionAsync(bool enabled, CancellationToken ct = default);

    /// <summary>Toggles the system-accent baseline immediately.</summary>
    Task SetFollowSystemAccentAsync(bool enabled, CancellationToken ct = default);

    /// <summary>Composes a scoped token layer for one package + appearance request (preview/audit use).</summary>
    ThemeStudioPalette ComposePalette(ThemePackage package, ThemeStudioPaletteRequest request);

    /// <summary>Composes a scoped token layer for an installed theme id.</summary>
    ThemeStudioPalette ComposePalette(string themeId, ThemeStudioPaletteRequest request);

    /// <summary>The applied state's scoped palette (surface chrome scope).</summary>
    ThemeStudioPalette GetAppliedPalette();

    /// <summary>The uninstalled draft's scoped palette, or null when the engine session already previews it.</summary>
    ThemeStudioPalette? GetDraftPalette();

    /// <summary>Live WCAG audit for one variant of a package.</summary>
    ThemeStudioContrastReport Audit(ThemePackage package, PaletteVariant variant);

    /// <summary>Validates an in-memory package (live editor feedback, no side effects).</summary>
    ThemeStudioValidationReport ValidatePackage(ThemePackage package);

    /// <summary>Finds an installed package.</summary>
    ThemePackage? FindPackage(string themeId);

    /// <summary>Parses + validates a theme package document without installing it (import preview).</summary>
    ThemeStudioValidationReport ValidateJson(string json, string? sourceName = null);

    /// <summary>Validates then installs a theme package document.</summary>
    Task<ThemeStudioOperationResult> ImportAsync(
        string json,
        string sourceName,
        bool overwrite = false,
        CancellationToken ct = default);

    /// <summary>Reads a dropped/selected <c>.nmtheme</c>/<c>.json</c> file and imports it.</summary>
    Task<ThemeStudioOperationResult> ImportFileAsync(
        string path,
        bool overwrite = false,
        CancellationToken ct = default);

    /// <summary>Exports an installed theme as <c>.nmtheme</c> JSON text.</summary>
    Task<string?> ExportAsync(string themeId, CancellationToken ct = default);

    /// <summary>Deletes a user theme (built-ins are protected).</summary>
    Task<ThemeStudioOperationResult> DeleteAsync(string themeId, CancellationToken ct = default);

    /// <summary>Duplicates a theme into a new user theme (copy).</summary>
    Task<ThemeStudioOperationResult> DuplicateAsync(string themeId, string newName, CancellationToken ct = default);

    /// <summary>Persists the current draft as a user theme ("从当前主题另存为").</summary>
    Task<ThemeStudioOperationResult> SaveDraftAsUserThemeAsync(
        string name,
        string? author,
        IReadOnlyList<string> tags,
        CancellationToken ct = default);

    /// <summary>True when the theme is favorited.</summary>
    bool IsFavorite(string themeId);

    /// <summary>Toggles the favorite flag (UI-owned persistence, see <see cref="ThemeStudioFavoritesStore"/>).</summary>
    Task<ThemeStudioOperationResult> ToggleFavoriteAsync(string themeId, CancellationToken ct = default);

    /// <summary>Restores factory theme/appearance/density/layout; optionally deletes user theme files.</summary>
    Task<ThemeStudioOperationResult> ResetToDefaultAsync(bool clearUserThemes, CancellationToken ct = default);
}

/// <summary>
/// File-picker seam. The surface never opens an OS dialog itself: storage policy belongs to the
/// integration layer (V11R-INT-1 passes the real <c>StorageProvider</c> implementation).
/// </summary>
public interface IThemeStudioFileGateway
{
    /// <summary>False when no picker is wired; the UI then offers drag-and-drop + paste instead.</summary>
    bool IsAvailable { get; }

    /// <summary>Picks a theme package to import.</summary>
    Task<string?> PickPackagePathAsync(CancellationToken ct = default);

    /// <summary>Picks the destination file for an export.</summary>
    Task<string?> PickExportPathAsync(string suggestedFileName, CancellationToken ct = default);

    /// <summary>Writes the export payload to the picked path.</summary>
    Task<bool> WriteTextAsync(string path, string text, CancellationToken ct = default);
}

/// <summary>No-picker implementation used until the integration task wires the real storage provider.</summary>
public sealed class NullThemeStudioFileGateway : IThemeStudioFileGateway
{
    /// <summary>Shared stateless instance.</summary>
    public static NullThemeStudioFileGateway Instance { get; } = new();

    /// <inheritdoc />
    public bool IsAvailable => false;

    /// <inheritdoc />
    public Task<string?> PickPackagePathAsync(CancellationToken ct = default) => Task.FromResult<string?>(null);

    /// <inheritdoc />
    public Task<string?> PickExportPathAsync(string suggestedFileName, CancellationToken ct = default) =>
        Task.FromResult<string?>(null);

    /// <inheritdoc />
    public Task<bool> WriteTextAsync(string path, string text, CancellationToken ct = default) =>
        Task.FromResult(false);
}

/// <summary>
/// Favorites are Theme Studio UI state (not theme-engine data): they live in their own document next to
/// the engine's settings file instead of polluting the theme package schema.
/// </summary>
public sealed class ThemeStudioFavoritesStore
{
    /// <summary>Schema id of the favorites document.</summary>
    public const string Schema = "newmanga.theme-studio-favorites/1";

    /// <summary>Maximum accepted document size.</summary>
    public const int MaxDocumentBytes = 64 * 1024;

    private readonly string _path;

    /// <summary>Creates a store; <paramref name="path"/> defaults next to the engine settings document.</summary>
    public ThemeStudioFavoritesStore(string? path = null)
    {
        _path = string.IsNullOrWhiteSpace(path)
            ? Path.Combine(ThemeSettingsStore.DefaultDirectory, "theme-studio-favorites.json")
            : Path.GetFullPath(path);
    }

    /// <summary>Absolute path of the favorites document.</summary>
    public string FilePath => _path;

    /// <summary>Reads the favorites; a missing/corrupt document yields an empty set (never throws).</summary>
    public IReadOnlySet<string> Load()
    {
        if (!File.Exists(_path))
        {
            return new HashSet<string>(StringComparer.Ordinal);
        }

        try
        {
            var info = new FileInfo(_path);
            if (info.Length > MaxDocumentBytes)
            {
                return new HashSet<string>(StringComparer.Ordinal);
            }

            using var document = System.Text.Json.JsonDocument.Parse(File.ReadAllText(_path));
            var root = document.RootElement;
            if (root.ValueKind != System.Text.Json.JsonValueKind.Object ||
                !root.TryGetProperty("ids", out var ids) ||
                ids.ValueKind != System.Text.Json.JsonValueKind.Array)
            {
                return new HashSet<string>(StringComparer.Ordinal);
            }

            var result = new HashSet<string>(StringComparer.Ordinal);
            foreach (var id in ids.EnumerateArray())
            {
                if (id.ValueKind == System.Text.Json.JsonValueKind.String && id.GetString() is { Length: > 0 } value)
                {
                    result.Add(value);
                }
            }

            return result;
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or System.Text.Json.JsonException or NotSupportedException)
        {
            return new HashSet<string>(StringComparer.Ordinal);
        }
    }

    /// <summary>Persists the favorites atomically; failures are reported as false (never thrown).</summary>
    public bool Save(IReadOnlySet<string> ids)
    {
        ArgumentNullException.ThrowIfNull(ids);
        var directory = Path.GetDirectoryName(_path);
        var tempPath = _path + ".tmp";
        try
        {
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            using (var stream = File.Create(tempPath))
            using (var writer = new System.Text.Json.Utf8JsonWriter(stream, new System.Text.Json.JsonWriterOptions { Indented = true }))
            {
                writer.WriteStartObject();
                writer.WriteString("schema", Schema);
                writer.WriteStartArray("ids");
                foreach (var id in ids.OrderBy(static value => value, StringComparer.Ordinal))
                {
                    writer.WriteStringValue(id);
                }

                writer.WriteEndArray();
                writer.WriteEndObject();
            }

            File.Move(tempPath, _path, overwrite: true);
            return true;
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
        {
            try
            {
                if (File.Exists(tempPath))
                {
                    File.Delete(tempPath);
                }
            }
            catch (Exception cleanup) when (cleanup is IOException or UnauthorizedAccessException)
            {
                // best effort
            }

            return false;
        }
    }
}
