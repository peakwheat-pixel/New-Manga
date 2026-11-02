using System.Text.RegularExpressions;
using Avalonia;
using Avalonia.Headless.XUnit;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Tests;

/// <summary>Guards Fluent style DynamicResource keys against the real Avalonia application resources.</summary>
public sealed class FluentTokenResourceTests
{
    [AvaloniaFact]
    public void Fluent_styles_and_resources_reference_only_resolvable_Nm_tokens()
    {
        var application = Application.Current!;
        using var theme = new DesignSystemThemeManager(application);
        Assert.True(theme.Initialize(AppearanceMode.Dark), theme.LastError);

        var repositoryRoot = FindRepositoryRoot();
        var searchRoots = new[]
        {
            Path.Combine(repositoryRoot, "apps", "desktop-avalonia", "src", "NewManga.DesignSystem", "Styles"),
            Path.Combine(repositoryRoot, "apps", "desktop-avalonia", "src", "NewManga.App", "Styles"),
            Path.Combine(repositoryRoot, "apps", "desktop-avalonia", "src", "NewManga.App", "Views", "Fluent"),
        };
        var references = searchRoots
            .Where(Directory.Exists)
            .SelectMany(root => Directory.EnumerateFiles(root, "*.axaml", SearchOption.AllDirectories))
            .SelectMany(file => Regex.Matches(File.ReadAllText(file), @"\{DynamicResource\s+(?<key>Nm\.[^,\s}]+)")
                .Select(match => (Key: match.Groups["key"].Value, File: file)))
            .DistinctBy(reference => reference.Key)
            .ToArray();

        Assert.NotEmpty(references);
        var unresolved = references
            .Where(reference => !application.TryGetResource(reference.Key, null, out _))
            .Select(reference => $"{reference.Key} ({Path.GetRelativePath(repositoryRoot, reference.File)})")
            .ToArray();

        Assert.True(unresolved.Length == 0,
            "Unresolvable Fluent DynamicResource keys: " + string.Join(", ", unresolved));
    }

    private static string FindRepositoryRoot()
    {
        var cursor = new DirectoryInfo(AppContext.BaseDirectory);
        while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc", "tasks", "FEA-06.md")))
        {
            cursor = cursor.Parent;
        }

        return cursor?.FullName ?? throw new DirectoryNotFoundException("could not locate the New Manga repository root");
    }
}
