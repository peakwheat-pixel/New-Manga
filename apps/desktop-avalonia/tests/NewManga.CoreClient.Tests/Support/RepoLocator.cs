using System.Text.Json;

namespace NewManga.CoreClient.Tests.Support;

/// <summary>Locates the repository root from the test binaries and reads committed parity evidence.</summary>
public static class RepoLocator
{
    public static string Root { get; } = FindRoot();

    public static JsonDocument ReadJson(string relativePath) =>
        JsonDocument.Parse(File.ReadAllText(Path.Combine(Root, relativePath)));

    public static JsonElement ReadElement(string relativePath)
    {
        using var document = ReadJson(relativePath);
        return document.RootElement.Clone();
    }

    private static string FindRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (Directory.Exists(Path.Combine(directory.FullName, "apps", "desktop-avalonia")) &&
                File.Exists(Path.Combine(directory.FullName, "AGENTS.md")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException("repository root not found from " + AppContext.BaseDirectory);
    }
}
