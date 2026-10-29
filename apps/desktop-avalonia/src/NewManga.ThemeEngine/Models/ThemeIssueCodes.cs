namespace NewManga.ThemeEngine;

/// <summary>
/// Stable finding codes emitted by the Theme Engine. UI/apart from localized display strings, codes
/// are the contract between the engine and Theme Studio (THEME_STUDIO_SPEC §3.6 "级别 + 路径 + 说明").
/// </summary>
public static class ThemeIssueCodes
{
    // ---- Schema reading (ThemePackageJson) -----------------------------------------------------
    /// <summary>Document is not valid JSON.</summary>
    public const string JsonInvalid = "package.json-invalid";

    /// <summary>JSON root is not an object.</summary>
    public const string RootNotObject = "package.root-not-object";

    /// <summary>A required field is missing.</summary>
    public const string FieldMissing = "package.field-missing";

    /// <summary>A field has an unexpected JSON type.</summary>
    public const string FieldType = "package.field-type";

    /// <summary>An unknown (tolerated) field was found; import is still allowed.</summary>
    public const string UnknownField = "package.unknown-field";

    /// <summary>A field declares a visual effect the design system forbids (shadow/gradient/blur/mica...).</summary>
    public const string ForbiddenDeclaration = "package.forbidden-declaration";

    /// <summary>The same field appears more than once.</summary>
    public const string DuplicateField = "package.duplicate-field";

    /// <summary>The package targets another schema generation.</summary>
    public const string SchemaUnsupported = "package.schema-unsupported";

    /// <summary>An enum value is not part of the schema.</summary>
    public const string EnumInvalid = "package.enum-invalid";

    /// <summary>The package metadata targets another engine version (warning).</summary>
    public const string EngineVersionMismatch = "metadata.engine-version";

    // ---- Descriptor ----------------------------------------------------------------------------
    /// <summary>Descriptor id does not match the slug requirement.</summary>
    public const string DescriptorIdInvalid = "descriptor.id-invalid";

    /// <summary>Descriptor name is missing/too long.</summary>
    public const string DescriptorNameInvalid = "descriptor.name-invalid";

    /// <summary>Descriptor version is not semver-shaped (warning).</summary>
    public const string DescriptorVersionNonSemver = "descriptor.version-nonsemver";

    /// <summary>A theme declares support for no appearance.</summary>
    public const string DescriptorAppearanceUnsupported = "descriptor.appearance-unsupported";

    /// <summary>Tags are invalid (too many / too long / duplicates).</summary>
    public const string DescriptorTagsInvalid = "descriptor.tags-invalid";

    // ---- Token set -----------------------------------------------------------------------------
    /// <summary>A required color key is missing.</summary>
    public const string ColorMissingKey = "colors.missing-key";

    /// <summary>A color key outside the contract set is present (warning).</summary>
    public const string ColorUnknownKey = "colors.unknown-key";

    /// <summary>A color value cannot be parsed as a CSS color.</summary>
    public const string ColorInvalidValue = "colors.invalid-value";

    /// <summary>A corner radius is negative or larger than the 3px hard limit.</summary>
    public const string CornerOutOfRange = "corners.radius-out-of-range";

    /// <summary>A font family declaration is not a plain family stack (e.g. a bundled font path).</summary>
    public const string FontFamilyInvalid = "typography.font-family-invalid";

    /// <summary>The font-size scale leaves the 80–130% range.</summary>
    public const string FontScaleOutOfRange = "typography.font-scale-out-of-range";

    /// <summary>A motion duration is negative or absurdly large.</summary>
    public const string MotionDurationOutOfRange = "motion.duration-out-of-range";

    /// <summary>Fast motion is slower than normal motion (warning).</summary>
    public const string MotionDurationOrder = "motion.duration-order";

    // ---- Contrast (WCAG 2.1, DESIGN_SYSTEM §2.3) ----------------------------------------------
    /// <summary>Primary text is below 7:1 against canvas/panel.</summary>
    public const string ContrastTextPrimary = "contrast.text-primary";

    /// <summary>Secondary text is below 4.5:1 against canvas/panel.</summary>
    public const string ContrastTextSecondary = "contrast.text-secondary";

    /// <summary>A status hue is below 4.5:1 against the panel.</summary>
    public const string ContrastStatus = "contrast.status";

    /// <summary>The accent "on" color is below 4.5:1 against the accent fill.</summary>
    public const string ContrastAccentOn = "contrast.accent-on";

    /// <summary>The focus-ring accent is below 3:1 against the panel.</summary>
    public const string ContrastAccentFocus = "contrast.accent-focus";

    // ---- Registry / install --------------------------------------------------------------------
    /// <summary>The theme id is not in the catalog.</summary>
    public const string ThemeNotFound = "theme.not-found";

    /// <summary>An installed theme may not use a built-in id.</summary>
    public const string RegistryIdReserved = "registry.id-reserved";

    /// <summary>Two user theme files declare the same id (warning; first file wins).</summary>
    public const string RegistryDuplicateId = "registry.duplicate-id";

    /// <summary>A user theme file could not be read (warning; file skipped).</summary>
    public const string RegistryFileUnreadable = "registry.file-unreadable";

    /// <summary>A user theme file parsed but failed validation (warning; file skipped).</summary>
    public const string RegistryFileInvalid = "registry.file-invalid";

    /// <summary>A registry operation failed at the filesystem level.</summary>
    public const string RegistryIoFailed = "registry.io-failed";

    /// <summary>The uploaded package document exceeds the size limit.</summary>
    public const string InstallTooLarge = "install.package-too-large";

    /// <summary>The uploaded package kind was normalized to <c>user</c> (warning).</summary>
    public const string InstallKindNormalized = "install.kind-normalized";

    // ---- Persistence / migration ---------------------------------------------------------------
    /// <summary>The settings document is corrupt (warning; defaults are used).</summary>
    public const string SettingsJsonInvalid = "settings.json-invalid";

    /// <summary>The settings document targets another schema generation (warning).</summary>
    public const string SettingsSchemaUnsupported = "settings.schema-unsupported";

    /// <summary>The settings document contains an invalid value (warning; that field falls back).</summary>
    public const string SettingsInvalidValue = "settings.invalid-value";

    /// <summary>A legacy theme id was migrated to the default theme (warning).</summary>
    public const string SettingsLegacyThemeId = "settings.legacy-theme-id";

    /// <summary>The settings pointed at an unknown theme and were recovered to the default (warning).</summary>
    public const string SettingsUnknownThemeId = "settings.unknown-theme-id";

    /// <summary>The settings file could not be read/written (warning; defaults/previous state kept).</summary>
    public const string SettingsIoFailed = "settings.io-failed";

    // ---- Preview -------------------------------------------------------------------------------
    /// <summary>The preview session switched to an unknown theme id.</summary>
    public const string PreviewThemeUnknown = "preview.theme-unknown";
}
