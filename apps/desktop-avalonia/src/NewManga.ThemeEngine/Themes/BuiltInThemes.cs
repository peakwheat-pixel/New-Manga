using System.Reflection;

namespace NewManga.ThemeEngine;

/// <summary>
/// The packages embedded in this assembly. Built-in themes are trusted input: they are generated at
/// build time from the frozen token document and never validated at runtime, but a missing/corrupt
/// resource must not crash startup (contract §4 behavior 2), so loading is lazy and failure is exposed
/// as data instead of an exception until something actually needs the package.
/// </summary>
public static class BuiltInThemes
{
    /// <summary>Manifest resource name of the shipped default theme.</summary>
    public const string DefaultThemeResourceName =
        "NewManga.ThemeEngine.Themes.newmanga-default.nmtheme";

    private static readonly Lazy<ThemeReadResult> DefaultResult = new(
        LoadDefaultPackage,
        LazyThreadSafetyMode.ExecutionAndPublication);

    /// <summary>True when the embedded default package loaded successfully.</summary>
    public static bool IsDefaultAvailable => DefaultResult.Value.Package is not null;

    /// <summary>Findings produced while loading the embedded default package (empty on success).</summary>
    public static IReadOnlyList<ThemeValidationIssue> DefaultLoadIssues => DefaultResult.Value.Issues;

    /// <summary>The shipped default package.</summary>
    public static ThemePackage Default =>
        DefaultResult.Value.Package ??
        throw new ThemePackageException(
            $"embedded default theme '{DefaultThemeResourceName}' is unavailable",
            DefaultResult.Value.Issues);

    /// <summary>Every built-in package. V1 ships exactly one theme by explicit product decision.</summary>
    public static IReadOnlyList<ThemePackage> All =>
        IsDefaultAvailable ? [Default] : [];

    /// <summary>Reads a package from an assembly manifest resource, returning findings instead of throwing.</summary>
    public static ThemeReadResult LoadFromResource(Assembly assembly, string resourceName)
    {
        ArgumentNullException.ThrowIfNull(assembly);
        ArgumentException.ThrowIfNullOrWhiteSpace(resourceName);

        using var stream = assembly.GetManifestResourceStream(resourceName);
        if (stream is null)
        {
            return new ThemeReadResult(
                null,
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.FieldMissing,
                    $"embedded theme resource '{resourceName}' was not found in assembly '{assembly.GetName().Name}'")]);
        }

        if (stream.Length > ThemePackageJson.MaxDocumentBytes)
        {
            return new ThemeReadResult(
                null,
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.InstallTooLarge,
                    $"embedded theme resource '{resourceName}' exceeds the {ThemePackageJson.MaxDocumentBytes} byte limit")]);
        }

        using var reader = new StreamReader(stream, System.Text.Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
        return ThemePackageJson.Read(reader.ReadToEnd());
    }

    private static ThemeReadResult LoadDefaultPackage()
    {
        try
        {
            return LoadFromResource(typeof(BuiltInThemes).Assembly, DefaultThemeResourceName);
        }
        catch (Exception exception) when (exception is IOException or InvalidOperationException or NotSupportedException)
        {
            return new ThemeReadResult(
                null,
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.RegistryFileUnreadable,
                    $"embedded default theme could not be read: {exception.Message}")]);
        }
    }
}
