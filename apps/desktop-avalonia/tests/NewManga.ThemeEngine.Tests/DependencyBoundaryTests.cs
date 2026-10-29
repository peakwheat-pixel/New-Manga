using System.Reflection;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Dependency-boundary evidence for the V11R-C-3 retirement gate: the new engine must have zero
/// compile/runtime dependency on the retired <c>NewManga.Theme</c> (<c>ThemePack</c>) assembly and may
/// only depend downward on the design system — never on App/Host/CoreClient.
/// </summary>
public sealed class DependencyBoundaryTests
{
    private static readonly Assembly EngineAssembly = typeof(ThemeService).Assembly;

    /// <summary>Retired public symbols the C-3 gate requires to be gone from production code.</summary>
    private static readonly string[] RetiredSymbols =
    [
        "ThemePack",
        "ThemePacks",
        "ThemePackService",
        "ThemePackMetrics",
        "MotionProfile",
        "LayoutKind",
        "NavPlacement",
        "ShelfStyle",
        "SettingsStyle",
    ];

    [Fact]
    public void Engine_does_not_reference_the_retired_theme_pack_assembly()
    {
        var references = EngineAssembly.GetReferencedAssemblies()
            .Select(assembly => assembly.Name ?? string.Empty)
            .ToArray();

        Assert.DoesNotContain("NewManga.Theme", references);
        Assert.DoesNotContain(
            references,
            name => name.StartsWith("NewManga.Theme", StringComparison.Ordinal) &&
                    !string.Equals(name, "NewManga.ThemeEngine", StringComparison.Ordinal));
    }

    [Fact]
    public void Engine_only_depends_downward_on_the_design_system()
    {
        var references = EngineAssembly.GetReferencedAssemblies()
            .Select(assembly => assembly.Name ?? string.Empty)
            .ToArray();

        foreach (var forbidden in new[] { "NewManga.App", "NewManga.Host", "NewManga.CoreClient", "NewManga.Theme" })
        {
            Assert.DoesNotContain(forbidden, references);
        }

        Assert.Contains("NewManga.DesignSystem", references);
    }

    [Fact]
    public void Retired_theme_pack_symbols_are_absent_from_the_engine_surface()
    {
        var members = EngineAssembly.GetTypes()
            .SelectMany(type => type.GetMembers(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
            .Select(member => member.Name)
            .ToHashSet(StringComparer.Ordinal);

        foreach (var retired in RetiredSymbols)
        {
            Assert.DoesNotContain(retired, members);
        }

        var typeNames = EngineAssembly.GetTypes().Select(type => type.Name).ToHashSet(StringComparer.Ordinal);
        Assert.DoesNotContain("ThemePack", typeNames);
        Assert.DoesNotContain("ThemePackService", typeNames);

        // The new contract type LayoutProfile is expected (it replaces the retired LayoutKind/NavPlacement
        // pair); this guards that the retired enum itself never resurfaced.
        Assert.Contains("LayoutProfile", typeNames);
    }
}
