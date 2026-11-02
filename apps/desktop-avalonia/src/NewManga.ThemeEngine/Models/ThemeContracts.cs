namespace NewManga.ThemeEngine;

/// <summary>
/// Frozen Theme Engine public surface (V11R_AVALONIA_CONTRACT §4). The App consumes the engine only
/// through these interfaces; implementations live in this assembly and concrete classes may expose
/// additional diagnostics on top of the interface members.
/// </summary>
public interface IThemeService
{
    /// <summary>Descriptor of the currently applied theme.</summary>
    ThemeDescriptor Current { get; }

    /// <summary>Currently applied and persisted settings.</summary>
    ThemeSettings Settings { get; }

    /// <summary>Raised after a theme, appearance, contrast, layout or motion change was applied.</summary>
    event EventHandler? Changed;

    /// <summary>Loads persisted settings, resolves the theme and applies the initial palette.</summary>
    Task InitializeAsync(CancellationToken ct = default);

    /// <summary>Applies a theme by id; unknown/invalid themes fall back to the default theme.</summary>
    Task<ThemeApplyResult> ApplyAsync(string themeId, CancellationToken ct = default);

    /// <summary>Switches light/dark/system appearance.</summary>
    Task SetAppearanceAsync(AppearanceMode mode);

    /// <summary>Switches standard/high contrast.</summary>
    Task SetContrastAsync(ContrastMode mode);

    /// <summary>Persists and applies a layout profile.</summary>
    Task SetLayoutAsync(LayoutProfile layout);

    /// <summary>Turns all motion on/off.</summary>
    Task SetReducedMotionAsync(bool enabled);

    /// <summary>Resets theme, appearance, contrast, layout and motion to the shipped defaults.</summary>
    Task ResetToDefaultAsync();
}

/// <summary>Theme catalog (contract §4 <c>IThemeRegistry</c>): built-in packages plus the user theme directory.</summary>
public interface IThemeRegistry
{
    /// <summary>Every known theme, built-ins first, then user themes ordered by id.</summary>
    IReadOnlyList<ThemeDescriptor> All { get; }

    /// <summary>Finds a descriptor by id (ordinal); null when unknown.</summary>
    ThemeDescriptor? Find(string id);

    /// <summary>Loads and deserializes a package by id.</summary>
    ThemePackage Load(string id);

    /// <summary>Rescans the user theme directory and rebuilds the catalog.</summary>
    Task RefreshAsync(CancellationToken ct = default);

    /// <summary>Validates and installs a theme package stream; returns the validation result.</summary>
    Task<ThemeValidationResult> InstallAsync(Stream packageJson, CancellationToken ct = default);

    /// <summary>Deletes a user theme; returns false for unknown or built-in ids.</summary>
    Task<bool> UninstallAsync(string id);

    /// <summary>Serializes a theme (built-in or user) to the canonical package document.</summary>
    Task<string> ExportAsync(string id);
}

/// <summary>One preview session (contract §4 <c>IThemePreviewSession</c>).</summary>
public interface IThemePreviewSession : IDisposable
{
    /// <summary>Points the preview at another theme; the applied settings stay untouched until <see cref="Commit"/>.</summary>
    void Update(string themeId);

    /// <summary>Persists the previewed theme as the applied theme.</summary>
    void Commit();

    /// <summary>Rolls the session back to the settings captured by <c>Begin()</c>.</summary>
    void Cancel();
}

/// <summary>Preview session factory (contract §4 <c>IThemePreviewEngine</c>).</summary>
public interface IThemePreviewEngine
{
    /// <summary>Starts a session, capturing the current settings as the rollback baseline.</summary>
    IThemePreviewSession Begin();
}

/// <summary>Theme package validator (contract §4 <c>IThemeValidator</c>).</summary>
public interface IThemeValidator
{
    /// <summary>Validates one package against the schema, DESIGN_SYSTEM constraints and WCAG floors.</summary>
    ThemeValidationResult Validate(ThemePackage package);
}

/// <summary>Theme settings persistence with legacy-id migration (contract §4 <c>IThemePersistence</c>).</summary>
public interface IThemePersistence
{
    /// <summary>
    /// Reads settings; never throws on corrupt/missing files (falls back to defaults and records the
    /// findings on the concrete store). Legacy/unknown theme ids are migrated per the retirement plan.
    /// </summary>
    ThemeSettings Load();

    /// <summary>Atomically persists settings.</summary>
    Task SaveAsync(ThemeSettings settings);
}

/// <summary>Raised when a theme package cannot be read, found or validated.</summary>
public class ThemeException : Exception
{
    /// <summary>Creates an exception with structured findings.</summary>
    public ThemeException(string message, IReadOnlyList<ThemeValidationIssue>? issues = null, Exception? inner = null)
        : base(message, inner)
    {
        Issues = issues ?? [];
    }

    /// <summary>Structured findings explaining the failure.</summary>
    public IReadOnlyList<ThemeValidationIssue> Issues { get; }
}

/// <summary>Raised when a theme id is unknown or its package document is invalid.</summary>
public sealed class ThemePackageException : ThemeException
{
    /// <summary>Creates a package exception.</summary>
    public ThemePackageException(string message, IReadOnlyList<ThemeValidationIssue>? issues = null, Exception? inner = null)
        : base(message, issues, inner)
    {
    }

    /// <summary>Finding code used when a requested theme id is not in the catalog.</summary>
    public const string NotFoundCode = "theme.not-found";
}

/// <summary>Raised when a preview session is used outside its lifecycle contract.</summary>
public sealed class ThemePreviewException : ThemeException
{
    /// <summary>Creates a preview exception.</summary>
    public ThemePreviewException(string message, IReadOnlyList<ThemeValidationIssue>? issues = null)
        : base(message, issues)
    {
    }
}

/// <summary>Shared structural-equality helpers for records that carry collections.</summary>
internal static class ThemeEquality
{
    /// <summary>Ordinal sequence equality treating null as empty.</summary>
    internal static bool SequenceEquals(IReadOnlyList<string>? left, IReadOnlyList<string>? right)
    {
        if (ReferenceEquals(left, right))
        {
            return true;
        }

        var first = left ?? [];
        var second = right ?? [];
        if (first.Count != second.Count)
        {
            return false;
        }

        for (var index = 0; index < first.Count; index++)
        {
            if (!string.Equals(first[index], second[index], StringComparison.Ordinal))
            {
                return false;
            }
        }

        return true;
    }

    /// <summary>Order-independent hash of an ordinal string sequence.</summary>
    internal static int SequenceHashCode(IReadOnlyList<string>? values)
    {
        if (values is null)
        {
            return 0;
        }

        var hash = 17;
        foreach (var value in values)
        {
            hash = unchecked((hash * 31) + StringComparer.Ordinal.GetHashCode(value));
        }

        return hash;
    }

    /// <summary>Ordinal dictionary equality treating null as empty.</summary>
    internal static bool DictionaryEquals(
        IReadOnlyDictionary<string, string>? left,
        IReadOnlyDictionary<string, string>? right)
    {
        if (ReferenceEquals(left, right))
        {
            return true;
        }

        var first = left ?? ThemeTokenSet.EmptyColors;
        var second = right ?? ThemeTokenSet.EmptyColors;
        if (first.Count != second.Count)
        {
            return false;
        }

        foreach (var pair in first)
        {
            if (!second.TryGetValue(pair.Key, out var value) ||
                !string.Equals(pair.Value, value, StringComparison.Ordinal))
            {
                return false;
            }
        }

        return true;
    }

    /// <summary>Order-independent hash of an ordinal string dictionary.</summary>
    internal static int DictionaryHashCode(IReadOnlyDictionary<string, string>? values)
    {
        if (values is null)
        {
            return 0;
        }

        var hash = 17;
        foreach (var pair in values)
        {
            hash = unchecked(hash + (StringComparer.Ordinal.GetHashCode(pair.Key) * 31) +
                             StringComparer.Ordinal.GetHashCode(pair.Value));
        }

        return hash;
    }
}
