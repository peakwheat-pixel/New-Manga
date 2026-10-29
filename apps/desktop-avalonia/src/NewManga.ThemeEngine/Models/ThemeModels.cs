namespace NewManga.ThemeEngine;

/// <summary>Where a theme package came from (contract §4 <c>ThemeKind</c>).</summary>
public enum ThemeKind
{
    /// <summary>Shipped with the application as an embedded resource; cannot be uninstalled or overridden.</summary>
    BuiltIn,

    /// <summary>Installed by the user under <c>%APPDATA%/NewManga/themes</c>.</summary>
    User,
}

/// <summary>Requested light/dark appearance (contract §4 <c>AppearanceMode</c>).</summary>
public enum AppearanceMode
{
    /// <summary>Follow the platform theme (listens to <c>ActualThemeVariantChanged</c>).</summary>
    System,

    Light,

    Dark,
}

/// <summary>Standard or WCAG-boosted contrast (contract §4 <c>ContrastMode</c>).</summary>
public enum ContrastMode
{
    Standard,

    High,
}

/// <summary>Which of the two token sets a palette resolution reads (contract §4 <c>ThemeTokenSet</c> variant selector).</summary>
public enum PaletteVariant
{
    Light,

    Dark,
}

/// <summary>Navigation placement (contract §4 <c>LayoutNavigation</c>). V1 implements <see cref="TopBand"/> only.</summary>
public enum LayoutNavigation
{
    TopBand,

    Sidebar,

    Dock,
}

/// <summary>Shelf presentation (contract §4 <c>ShelfLayout</c>).</summary>
public enum ShelfLayout
{
    Grid,

    List,

    Masonry,
}

/// <summary>Density preset (contract §4 <c>Density</c>).</summary>
public enum Density
{
    Comfortable,

    Compact,

    Spacious,
}

/// <summary>Workbench arrangement (contract §4 <c>WorkbenchLayout</c>).</summary>
public enum WorkbenchLayout
{
    Stacked,

    Split,
}

/// <summary>Reader presentation (contract §4 <c>ReaderLayout</c>).</summary>
public enum ReaderLayout
{
    FitPage,

    FitWidth,

    DoublePage,

    Webtoon,
}

/// <summary>Background material a theme may declare (THEME_STUDIO_SPEC §3.4: Solid / None only in V1).</summary>
public enum ThemeMaterial
{
    Solid,

    None,
}

/// <summary>Elevation expression a theme may declare (THEME_STUDIO_SPEC §3.4: none / raised only).</summary>
public enum ThemeElevation
{
    None,

    Raised,
}

/// <summary>Line-height preset selected by a theme's typography (THEME_STUDIO_SPEC §3.4).</summary>
public enum LineHeightPreset
{
    Tight,

    Normal,

    Loose,
}

/// <summary>
/// One absolute line-height tier the design system publishes (<c>Nm.LineHeight.*</c>).
/// Avalonia's <c>TextBlock.LineHeight</c> is absolute pixels, so the theme engine derives the tier
/// from a font-size token and the DESIGN_SYSTEM §3 per-tier ratio instead of a bare multiplier.
/// </summary>
/// <param name="ResourceKey"><c>Nm.LineHeight.*</c> key.</param>
/// <param name="FontSizeKey"><c>Nm.FontSize.*</c> key the tier scales with.</param>
/// <param name="DesignMultiplier">DESIGN_SYSTEM §3 line-height ratio for the tier at scale 1.0.</param>
public sealed record LineHeightTier(string ResourceKey, string FontSizeKey, double DesignMultiplier);

/// <summary>Theme identity and capabilities (contract §4 <c>ThemeDescriptor</c>).</summary>
/// <param name="Id">Stable lowercase slug, e.g. <c>newmanga-default</c>.</param>
/// <param name="Name">Human-readable display name.</param>
/// <param name="Version">Author version string (semver recommended).</param>
/// <param name="Author">Optional author.</param>
/// <param name="Description">Optional one-line description.</param>
/// <param name="Kind">Built-in or user-installed.</param>
/// <param name="Tags">Search/category tags.</param>
/// <param name="SupportsLight">Whether the package's light token set is an intended appearance.</param>
/// <param name="SupportsDark">Whether the package's dark token set is an intended appearance.</param>
/// <param name="PreviewHint">Optional UI hint (e.g. which surface to preview first).</param>
public sealed record ThemeDescriptor(
    string Id,
    string Name,
    string Version,
    string? Author,
    string? Description,
    ThemeKind Kind,
    IReadOnlyList<string> Tags,
    bool SupportsLight,
    bool SupportsDark,
    string? PreviewHint)
{
    /// <summary>
    /// Structural equality: the positional record would otherwise compare <see cref="Tags"/> by
    /// reference, which makes two identical descriptors unequal after a JSON round-trip.
    /// </summary>
    public bool Equals(ThemeDescriptor? other) =>
        other is not null &&
        string.Equals(Id, other.Id, StringComparison.Ordinal) &&
        string.Equals(Name, other.Name, StringComparison.Ordinal) &&
        string.Equals(Version, other.Version, StringComparison.Ordinal) &&
        string.Equals(Author, other.Author, StringComparison.Ordinal) &&
        string.Equals(Description, other.Description, StringComparison.Ordinal) &&
        Kind == other.Kind &&
        ThemeEquality.SequenceEquals(Tags, other.Tags) &&
        SupportsLight == other.SupportsLight &&
        SupportsDark == other.SupportsDark &&
        string.Equals(PreviewHint, other.PreviewHint, StringComparison.Ordinal);

    /// <inheritdoc />
    public override int GetHashCode() =>
        HashCode.Combine(
            Id,
            Name,
            Version,
            Author,
            Description,
            Kind,
            ThemeEquality.SequenceHashCode(Tags),
            HashCode.Combine(SupportsLight, SupportsDark, PreviewHint));
}

/// <summary>Font personality of a theme token set: families, size scale and line-height preset.</summary>
/// <param name="Ui">CSS-style font stack for UI text.</param>
/// <param name="Data">CSS-style font stack for data/monospace text.</param>
/// <param name="Display">CSS-style font stack for display headings.</param>
/// <param name="Scale">Font-size scale in [0.8, 1.3] (THEME_STUDIO_SPEC §3.4: 80–130%).</param>
/// <param name="LineHeight">Selected line-height preset.</param>
public sealed record ThemeTypography(
    string Ui,
    string Data,
    string Display,
    double Scale,
    LineHeightPreset LineHeight)
{
    /// <summary>Scale factor of the shipped default theme.</summary>
    public const double DefaultScale = 1.0;
}

/// <summary>Corner radius personality (DESIGN_SYSTEM §1 rule 4: only values up to 3px are legal).</summary>
/// <param name="None">0px corner token value.</param>
/// <param name="Sm">Small corner value (default 2px).</param>
/// <param name="Md">Medium corner value (default 3px).</param>
public sealed record ThemeCorners(double None, double Sm, double Md)
{
    /// <summary>Hard upper bound for any corner token (DESIGN_SYSTEM §1 rule 4).</summary>
    public const double MaxRadius = 3.0;
}

/// <summary>Motion personality: UI durations owned by the theme (DESIGN_SYSTEM §7, R-10: 140ms baseline).</summary>
/// <param name="FastMs">Fast duration in milliseconds (frozen baseline: 90ms).</param>
/// <param name="NormalMs">Normal duration in milliseconds (frozen baseline: 140ms).</param>
public sealed record ThemeMotion(int FastMs, int NormalMs)
{
    /// <summary>Upper bound accepted from a theme package, in milliseconds.</summary>
    public const int MaxDurationMs = 1000;
}

/// <summary>
/// One appearance variant of a theme: everything a package may define for light or dark
/// (contract §4: a theme defines <em>personality</em> — colors, fonts, corners, material, elevation,
/// motion — and must not define layout or navigation).
/// </summary>
/// <param name="Colors">Complete <c>Nm.Color.*</c> map (35 keys, contract §2.2) of raw CSS color values.</param>
/// <param name="Typography">Font personality.</param>
/// <param name="Corners">Corner radius personality.</param>
/// <param name="Material">Background material.</param>
/// <param name="Elevation">Elevation expression.</param>
/// <param name="Motion">Motion personality.</param>
public sealed record ThemeTokenSet(
    IReadOnlyDictionary<string, string> Colors,
    ThemeTypography Typography,
    ThemeCorners Corners,
    ThemeMaterial Material,
    ThemeElevation Elevation,
    ThemeMotion Motion)
{
    /// <summary>Immutable empty color map (used by malformed/partial packages).</summary>
    public static IReadOnlyDictionary<string, string> EmptyColors { get; } =
        new System.Collections.ObjectModel.ReadOnlyDictionary<string, string>(
            new Dictionary<string, string>(StringComparer.Ordinal));

    /// <summary>
    /// Structural equality: the positional record would otherwise compare <see cref="Colors"/> by
    /// reference, which makes two identical token sets unequal after a JSON round-trip.
    /// </summary>
    public bool Equals(ThemeTokenSet? other) =>
        other is not null &&
        ThemeEquality.DictionaryEquals(Colors, other.Colors) &&
        Typography == other.Typography &&
        Corners == other.Corners &&
        Material == other.Material &&
        Elevation == other.Elevation &&
        Motion == other.Motion;

    /// <inheritdoc />
    public override int GetHashCode() =>
        HashCode.Combine(
            ThemeEquality.DictionaryHashCode(Colors),
            Typography,
            Corners,
            Material,
            Elevation,
            Motion);
}

/// <summary>
/// Package metadata. Free-form provenance plus read-side diagnostics; diagnostics are never serialized
/// and never part of value equality.
/// </summary>
public sealed record ThemeMetadata
{
    /// <summary>Theme-engine schema generation the package targets (always <c>"1"</c> for <c>newmanga.theme/1</c>).</summary>
    public string EngineVersion { get; init; } = ThemeDefaults.EngineVersion;

    /// <summary>Optional generator identifier, e.g. <c>newmanga-theme-gen/1</c>.</summary>
    public string? Generator { get; init; }

    /// <summary>Additional, ordered author metadata (unknown fields are reported but preserved here only by the engine).</summary>
    public IReadOnlyDictionary<string, string> Extra { get; init; } = EmptyExtra;

    /// <summary>
    /// Diagnostics produced while reading the package (unknown fields, duplicate fields, ...). The
    /// validator folds them into its result so import UI can show warnings without failing the load.
    /// </summary>
    public IReadOnlyList<ThemeValidationIssue> LoadWarnings { get; init; } = [];

    /// <summary>Immutable empty extra map.</summary>
    public static IReadOnlyDictionary<string, string> EmptyExtra { get; } =
        new System.Collections.ObjectModel.ReadOnlyDictionary<string, string>(
            new Dictionary<string, string>(StringComparer.Ordinal));

    /// <summary>Structural equality over the serialized fields only (diagnostics excluded).</summary>
    public bool Equals(ThemeMetadata? other) =>
        other is not null &&
        string.Equals(EngineVersion, other.EngineVersion, StringComparison.Ordinal) &&
        string.Equals(Generator, other.Generator, StringComparison.Ordinal) &&
        ThemeEquality.DictionaryEquals(Extra, other.Extra);

    /// <inheritdoc />
    public override int GetHashCode() =>
        HashCode.Combine(EngineVersion, Generator, ThemeEquality.DictionaryHashCode(Extra));
}

/// <summary>
/// A theme package (contract §4 <c>ThemePackage</c>): schema id, descriptor, one token set per
/// appearance and metadata. Immutable and safe to hand to any consumer.
/// </summary>
public sealed record ThemePackage(
    string Schema,
    ThemeDescriptor Descriptor,
    ThemeTokenSet Light,
    ThemeTokenSet Dark,
    ThemeMetadata Metadata);

/// <summary>
/// Layout is independent of the theme and persisted separately (contract §4 <c>LayoutProfile</c>);
/// V1 implements <see cref="LayoutNavigation.TopBand"/> only and keeps the other enum values reserved.
/// </summary>
public sealed record LayoutProfile(
    string Id,
    LayoutNavigation Navigation,
    ShelfLayout Shelf,
    Density Density,
    WorkbenchLayout Workbench,
    ReaderLayout Reader)
{
    /// <summary>Factory default: TopBand navigation, grid shelf, comfortable density, stacked workbench, fit-page reader.</summary>
    public static LayoutProfile Default { get; } = new(
        "default",
        LayoutNavigation.TopBand,
        ShelfLayout.Grid,
        Density.Comfortable,
        WorkbenchLayout.Stacked,
        ReaderLayout.FitPage);
}

/// <summary>Persisted theme/layout settings (contract §4 <c>ThemeSettings</c>).</summary>
public sealed record ThemeSettings(
    string ThemeId,
    AppearanceMode Appearance,
    ContrastMode Contrast,
    LayoutProfile Layout,
    bool ReducedMotion,
    bool FollowSystemAccent);

/// <summary>One validation finding. <see cref="Severity"/> is the contract's string channel: <c>error</c> or <c>warning</c>.</summary>
public sealed record ThemeValidationIssue(string Code, string Severity, string Message, string? Path)
{
    /// <summary>Severity value for findings that make a package invalid.</summary>
    public const string ErrorSeverity = "error";

    /// <summary>Severity value for tolerated findings (import is still allowed).</summary>
    public const string WarningSeverity = "warning";

    /// <summary>True when this finding invalidates a package.</summary>
    public bool IsError => string.Equals(Severity, ErrorSeverity, StringComparison.Ordinal);

    /// <summary>Creates an error finding.</summary>
    public static ThemeValidationIssue Error(string code, string message, string? path = null) =>
        new(code, ErrorSeverity, message, path);

    /// <summary>Creates a warning finding.</summary>
    public static ThemeValidationIssue Warning(string code, string message, string? path = null) =>
        new(code, WarningSeverity, message, path);
}

/// <summary>Validation outcome (contract §4 <c>ThemeValidationResult</c>).</summary>
public sealed record ThemeValidationResult(bool IsValid, IReadOnlyList<ThemeValidationIssue> Issues)
{
    /// <summary>Valid with no findings.</summary>
    public static ThemeValidationResult Ok { get; } = new(true, []);

    /// <summary>Builds a result whose <see cref="IsValid"/> is true only when no finding is an error.</summary>
    public static ThemeValidationResult From(IEnumerable<ThemeValidationIssue> issues)
    {
        ArgumentNullException.ThrowIfNull(issues);
        var list = issues as IReadOnlyList<ThemeValidationIssue> ?? issues.ToArray();
        var valid = true;
        foreach (var issue in list)
        {
            if (issue.IsError)
            {
                valid = false;
                break;
            }
        }

        return new ThemeValidationResult(valid, list);
    }

    /// <summary>All error findings, in order.</summary>
    public IReadOnlyList<ThemeValidationIssue> Errors =>
        Issues.Where(static issue => issue.IsError).ToArray();

    /// <summary>All warning findings, in order.</summary>
    public IReadOnlyList<ThemeValidationIssue> Warnings =>
        Issues.Where(static issue => !issue.IsError).ToArray();
}

/// <summary>Outcome of applying a theme (contract §4 <c>ThemeApplyResult</c>).</summary>
public sealed record ThemeApplyResult(
    bool Success,
    string? AppliedThemeId,
    IReadOnlyList<ThemeValidationIssue> Issues,
    bool Recovered)
{
    /// <summary>Theme applied as requested.</summary>
    public static ThemeApplyResult Applied(string themeId) => new(true, themeId, [], false);

    /// <summary>Theme applied but a fallback was needed (e.g. unknown id resolved to the default theme).</summary>
    public static ThemeApplyResult RecoveredWith(string themeId, IEnumerable<ThemeValidationIssue> issues) =>
        new(true, themeId, issues as IReadOnlyList<ThemeValidationIssue> ?? issues.ToArray(), true);

    /// <summary>Nothing was applied; the caller keeps the previous state.</summary>
    public static ThemeApplyResult Failed(IEnumerable<ThemeValidationIssue> issues) =>
        new(false, null, issues as IReadOnlyList<ThemeValidationIssue> ?? issues.ToArray(), false);
}

/// <summary>Well-known contract constants shared by every Theme Engine subsystem.</summary>
public static class ThemeDefaults
{
    /// <summary>Frozen theme-package schema id (contract §4: <c>newmanga.theme/1</c>).</summary>
    public const string Schema = "newmanga.theme/1";

    /// <summary>Schema id of the persisted settings file.</summary>
    public const string SettingsSchema = "newmanga.theme-settings/1";

    /// <summary>
    /// Shipped default theme id. The contract's fallback text ("NewManga.Default") and the retirement
    /// plan's <c>newmanga-default</c> refer to this one theme; the id is the retirement-plan spelling.
    /// </summary>
    public const string DefaultThemeId = "newmanga-default";

    /// <summary>Schema generation stored in <see cref="ThemeMetadata.EngineVersion"/>.</summary>
    public const string EngineVersion = "1";

    /// <summary>Folder name under the roaming application-data directory that owns theme files.</summary>
    public const string ThemeDirectoryName = "themes";

    /// <summary>File name of the persisted settings document.</summary>
    public const string SettingsFileName = "theme-settings.json";

    /// <summary>Extension used when the engine writes a theme package (input may also be <c>.json</c>).</summary>
    public const string ThemeFileExtension = ".nmtheme";

    /// <summary>Alternative extension accepted on import/scan.</summary>
    public const string ThemeJsonExtension = ".json";

    /// <summary>Shipped settings: default theme, system appearance, standard contrast, default layout.</summary>
    public static ThemeSettings Settings { get; } = new(
        DefaultThemeId,
        AppearanceMode.System,
        ContrastMode.Standard,
        LayoutProfile.Default,
        ReducedMotion: false,
        FollowSystemAccent: false);
}
