using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC7 / W-6: mechanical project-reference direction check. App → Presentation is allowed; the
/// product lower layers (Host/Core/ApplicationCore) must never reference the presentation/UI layers,
/// and the whole desktop solution keeps the frozen net9.0 TFM.
/// </summary>
public sealed class ArchitectureDependencyTests
{
    private static readonly string[] LowerLayers =
    [
        "NewManga.Host",
        "NewManga.CoreClient",
        "NewManga.ApplicationCore",
    ];

    private static readonly string[] ForbiddenTargets =
    [
        "NewManga.Presentation.Avalonia",
        "NewManga.App",
        "NewManga.DesignSystem",
    ];

    [Fact]
    public void App_ConsumesThePresentationModule()
    {
        var app = Load("NewManga.App");
        Assert.Contains(app.References, reference => reference.EndsWith("NewManga.Presentation.Avalonia.csproj", StringComparison.Ordinal));
    }

    [Fact]
    public void LowerLayers_NeverReferencePresentationOrUi()
    {
        foreach (var lower in LowerLayers)
        {
            var project = Load(lower);
            foreach (var forbidden in ForbiddenTargets)
            {
                Assert.DoesNotContain(
                    project.References,
                    reference => reference.EndsWith(forbidden + ".csproj", StringComparison.Ordinal));
            }
        }
    }

    [Fact]
    public void DesktopProjects_KeepTheFrozenTargetFramework()
    {
        var projects = Directory
            .EnumerateFiles(Path.Combine(DesktopRoot(), "src"), "*.csproj", SearchOption.AllDirectories)
            .Where(path => !path.Contains($"{Path.DirectorySeparatorChar}tools{Path.DirectorySeparatorChar}", StringComparison.Ordinal));
        foreach (var project in projects)
        {
            var document = XDocument.Load(project);
            var targetFramework = document.Descendants("TargetFramework").FirstOrDefault()?.Value;
            if (targetFramework is null)
            {
                continue; // inherited from Directory.Build.props (net9.0)
            }

            Assert.Equal("net9.0", targetFramework.Trim());
        }
    }

    private static (string Name, IReadOnlyList<string> References) Load(string projectName)
    {
        var path = Directory
            .EnumerateFiles(Path.Combine(DesktopRoot(), "src"), projectName + ".csproj", SearchOption.AllDirectories)
            .Single();
        var document = XDocument.Load(path);
        var references = document
            .Descendants("ProjectReference")
            .Select(element => element.Attribute("Include")?.Value ?? string.Empty)
            .Where(value => value.Length > 0)
            .ToArray();
        return (projectName, references);
    }

    private static string DesktopRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var candidate = Path.Combine(directory.FullName, "apps", "desktop-avalonia");
            if (Directory.Exists(Path.Combine(candidate, "src")))
            {
                return candidate;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException("desktop root not found from " + AppContext.BaseDirectory);
    }
}
