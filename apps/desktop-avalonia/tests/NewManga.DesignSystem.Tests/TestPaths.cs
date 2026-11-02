using System.Text.Json;
using Xunit;

[assembly: CollectionBehavior(DisableTestParallelization = true)]

namespace NewManga.DesignSystem.Tests;

/// <summary>Repository layout helpers for tests that must see the frozen token source and the project files.</summary>
internal static class TestPaths
{
    /// <summary>Worktree root (the directory containing <c>doc/</c> and <c>apps/</c>).</summary>
    public static string RepositoryRoot { get; } = FindRepositoryRoot();

    /// <summary>Path of the design-system project directory (generated artifacts live here).</summary>
    public static string DesignSystemProject { get; } =
        Path.Combine(RepositoryRoot, "apps", "desktop-avalonia", "src", "NewManga.DesignSystem");

    /// <summary>Path of the frozen token source in the repository.</summary>
    public static string TokensJson { get; } =
        Path.Combine(RepositoryRoot, "doc", "design", "redesign-v1", "40-fusion", "tokens.json");

    /// <summary>Fixture copy of the frozen token source (copied next to the test binaries).</summary>
    public static string TokensFixture { get; } =
        Path.Combine(AppContext.BaseDirectory, "Fixtures", "tokens.json");

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
