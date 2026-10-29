using System.Security.Cryptography;

namespace NewManga.ThemeEngine.Tests;

/// <summary>Repository layout helpers for tests that must see the frozen token source and generated artifacts.</summary>
internal static class TestPaths
{
    /// <summary>Worktree root (the directory containing <c>doc/</c> and <c>apps/</c>).</summary>
    public static string RepositoryRoot { get; } = FindRepositoryRoot();

    /// <summary>Theme-engine project directory (generated artifacts live here).</summary>
    public static string ThemeEngineProject { get; } = Path.Combine(
        RepositoryRoot, "apps", "desktop-avalonia", "src", "NewManga.ThemeEngine");

    /// <summary>Path of the frozen token source in the repository.</summary>
    public static string TokensJson { get; } =
        Path.Combine(RepositoryRoot, "doc", "design", "redesign-v1", "40-fusion", "tokens.json");

    /// <summary>Fixture copy of the frozen token source (copied next to the test binaries).</summary>
    public static string TokensFixture { get; } =
        Path.Combine(AppContext.BaseDirectory, "Fixtures", "tokens.json");

    /// <summary>Committed, generated default theme package.</summary>
    public static string DefaultThemeFile { get; } =
        Path.Combine(ThemeEngineProject, "Themes", "newmanga-default.nmtheme");

    /// <summary>Committed, generated typography baseline source file.</summary>
    public static string BaselineSourceFile { get; } =
        Path.Combine(ThemeEngineProject, "Generated", "ThemeTokenBaseline.g.cs");

    private static string FindRepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "doc", "design", "redesign-v1", "40-fusion", "tokens.json")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException(
            $"could not locate repository root above '{AppContext.BaseDirectory}'");
    }
}

/// <summary>Theme package fixtures shared by the engine tests.</summary>
internal static class ThemeFixtures
{
    /// <summary>The frozen token document, read from the copied fixture.</summary>
    public static string TokensJson { get; } = File.ReadAllText(TestPaths.TokensFixture);

    /// <summary>The shipped default package, regenerated in-memory from the frozen tokens.</summary>
    public static ThemePackage DefaultPackage { get; } = BuiltInThemeGenerator.GenerateDefaultTheme(TokensJson);

    /// <summary>Returns a copy of <paramref name="package"/> with a different descriptor id/name and user kind.</summary>
    public static ThemePackage AsUser(ThemePackage package, string id, string? name = null) =>
        package with
        {
            Descriptor = package.Descriptor with
            {
                Id = id,
                Name = name ?? id,
                Kind = ThemeKind.User,
                Author = "Tests",
                Tags = ["test"],
            },
        };

    /// <summary>Returns a token set with one color value replaced.</summary>
    public static ThemeTokenSet WithColor(ThemeTokenSet set, string key, string value)
    {
        var colors = new Dictionary<string, string>(set.Colors, StringComparer.Ordinal)
        {
            [key] = value,
        };
        return set with { Colors = colors };
    }

    /// <summary>Returns a token set with the given typography.</summary>
    public static ThemeTokenSet WithTypography(ThemeTokenSet set, ThemeTypography typography) =>
        set with { Typography = typography };

    /// <summary>Returns a token set with the given corners.</summary>
    public static ThemeTokenSet WithCorners(ThemeTokenSet set, ThemeCorners corners) => set with { Corners = corners };

    /// <summary>Returns a token set with the given motion.</summary>
    public static ThemeTokenSet WithMotion(ThemeTokenSet set, ThemeMotion motion) => set with { Motion = motion };

    /// <summary>Serializes a package for install/scan tests.</summary>
    public static string Write(ThemePackage package) => ThemePackageJson.Write(package);

    /// <summary>Streams a package document for <c>InstallAsync</c>.</summary>
    public static MemoryStream Stream(ThemePackage package) =>
        new(System.Text.Encoding.UTF8.GetBytes(Write(package)));

    /// <summary>Streams raw text for <c>InstallAsync</c>.</summary>
    public static MemoryStream Stream(string json) => new(System.Text.Encoding.UTF8.GetBytes(json));

    /// <summary>Visits every token-set variant (light/dark) for parameterized assertions.</summary>
    public static IEnumerable<object[]> Variants()
    {
        yield return [PaletteVariant.Light];
        yield return [PaletteVariant.Dark];
    }
}

/// <summary>Temporary directory that deletes itself on dispose.</summary>
internal sealed class TempDirectory : IDisposable
{
    public TempDirectory(string prefix = "nm-theme-test-")
    {
        Path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), prefix + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path);
    }

    public string Path { get; }

    public string File(string name) => System.IO.Path.Combine(Path, name);

    public void Dispose()
    {
        try
        {
            if (Directory.Exists(Path))
            {
                Directory.Delete(Path, recursive: true);
            }
        }
        catch (IOException)
        {
            // best effort cleanup for a temp directory
        }
        catch (UnauthorizedAccessException)
        {
            // best effort cleanup for a temp directory
        }
    }
}

/// <summary>SHA-256 helpers for generator reproducibility assertions.</summary>
internal static class Hashing
{
    public static string Sha256(string text) =>
        Convert.ToHexString(SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
}
