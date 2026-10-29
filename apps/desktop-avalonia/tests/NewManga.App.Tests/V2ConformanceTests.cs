using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using NewManga.DesignSystem;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-1 AC4 governance: static conformance of the V2 UI against the frozen design contract —
/// no raw colour / font-size / spacing / shadow / gradient / blur values, no radius above 3px, every
/// {DynamicResource Nm.*} key present in the merged Design System, AND (review item 4) the same ban on
/// raw design values in the C# ViewModel layer (ShellLayout is the single token-resolution module and
/// is the only allowlisted file). Also emits the token/class inventory used by the L3 review.
/// </summary>
public sealed class V2ConformanceTests
{
    private static readonly Regex DynamicToken = new(@"\{DynamicResource\s+(Nm\.[A-Za-z0-9.]+)\s*\}", RegexOptions.Compiled);
    private static readonly Regex RawHex = new(@"#[0-9A-Fa-f]{3,8}\b", RegexOptions.Compiled);
    private static readonly Regex RawFontSize = new(@"FontSize=""\d", RegexOptions.Compiled);
    private static readonly Regex RawNumericSize = new(@"\b(Width|Height|MinWidth|MinHeight|MaxWidth|MaxHeight)=""\d", RegexOptions.Compiled);
    private static readonly Regex RawThickness = new(@"\b(Margin|Padding|Spacing|BorderThickness)=""[0-9]", RegexOptions.Compiled);
    private static readonly Regex RawOpacity = new(@"Opacity=""[0-9]", RegexOptions.Compiled);
    private static readonly Regex RawFourCorner = new(@"CornerRadius=""\d+\s*,", RegexOptions.Compiled);
    private static readonly Regex ForbiddenEffect = new(@"BoxShadow|LinearGradient|RadialGradient|BlurEffect|OpacityMask|backdrop", RegexOptions.Compiled | RegexOptions.IgnoreCase);
    private static readonly Regex RawCornerRadius = new(@"CornerRadius=""([4-9]|\d\d+)", RegexOptions.Compiled);
    private static readonly Regex ClassesAttribute = new(@"Classes=""([^""]+)""", RegexOptions.Compiled);

    private static readonly Regex CSharpRawThickness = new(
        @"\b(Margin|Padding|Spacing|BorderThickness)\s*=\s*(new\s+Thickness\(\s*)?\d",
        RegexOptions.Compiled);
    private static readonly Regex CSharpRawCorner = new(
        @"\bCornerRadius\s*=\s*(new\s+CornerRadius\(\s*)?\d",
        RegexOptions.Compiled);
    private static readonly Regex CSharpRawFontSize = new(@"\bFontSize\s*=\s*\d", RegexOptions.Compiled);
    private static readonly Regex CSharpRawOpacity = new(@"\bOpacity\s*=\s*0?\.\d", RegexOptions.Compiled);
    private static readonly Regex CSharpBrushLiteral = new(@"\bBrushes\.|new\s+SolidColorBrush\(|Color\.FromRgb|Color\.Parse\(", RegexOptions.Compiled);
    private static readonly Regex CSharpLayoutLiteral = new(
        @"\b(Width|Height|MinWidth|MinHeight|MaxWidth|MaxHeight|FontSize)\s*=>\s*\d",
        RegexOptions.Compiled);
    private static readonly Regex CSharpOldBreakpoint = new(@"(>=|<)\s*(1400|1200)\b", RegexOptions.Compiled);

    private static string V2Root => Path.Combine(RepoRoot(), "src", "NewManga.App");

    /// <summary>Single token-resolution module: token lookups + frozen breakpoints/ratios only.</summary>
    private static readonly string[] CSharpAllowlist = { "Shell/V2/ShellLayout.cs" };

    private static string RepoRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "NewManga.sln")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException("apps/desktop-avalonia/NewManga.sln not found above the test binaries");
    }

    private static IReadOnlyList<string> V2XamlFiles()
    {
        var directories = new[]
        {
            Path.Combine(V2Root, "Views", "V2"),
            Path.Combine(V2Root, "Shell", "V2"),
        };
        return directories
            .Where(Directory.Exists)
            .SelectMany(directory => Directory.EnumerateFiles(directory, "*.axaml", SearchOption.AllDirectories))
            .OrderBy(path => path, StringComparer.Ordinal)
            .ToList();
    }

    /// <summary>
    /// C# owned by this task (Shell/Library/Console). Other V2 code (Studio, Theme Studio) belongs to its
    /// own Owner review and is excluded here; legacy Views are outside the new contract scan entirely.
    /// </summary>
    private static readonly string[] OwnedCSharpDirectories =
    {
        "Shell/V2",
        "ViewModels/V2/Shell",
        "ViewModels/V2/Library",
        "ViewModels/V2/Console",
        "Views/V2/Shell",
        "Views/V2/Library",
        "Views/V2/Console",
    };

    private static IReadOnlyList<string> AppCSharpFiles()
    {
        return OwnedCSharpDirectories
            .Select(directory => Path.Combine(V2Root, directory.Replace('/', Path.DirectorySeparatorChar)))
            .Where(Directory.Exists)
            .SelectMany(directory => Directory.EnumerateFiles(directory, "*.cs", SearchOption.AllDirectories))
            .Where(path => !path.Contains($"{Path.DirectorySeparatorChar}Studio{Path.DirectorySeparatorChar}", StringComparison.Ordinal))
            .OrderBy(path => path, StringComparer.Ordinal)
            .Where(path => !CSharpAllowlist.Any(allowed =>
                Path.GetRelativePath(V2Root, path).Replace('\\', '/').EndsWith(allowed, StringComparison.Ordinal)))
            .ToList();
    }

    [Fact]
    public void V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects()
    {
        var problems = new List<string>();
        foreach (var file in V2XamlFiles())
        {
            var text = File.ReadAllText(file);
            var name = Path.GetFileName(file);
            foreach (var (regex, label) in new[]
                     {
                         (RawHex, "raw colour"),
                         (RawFontSize, "raw font size"),
                         (RawNumericSize, "raw size"),
                         (RawThickness, "raw padding/margin/spacing/thickness"),
                         (RawOpacity, "raw opacity"),
                         (RawFourCorner, "four-value raw corner radius"),
                         (ForbiddenEffect, "forbidden effect"),
                         (RawCornerRadius, "radius above 3px"),
                     })
            {
                foreach (Match match in regex.Matches(text))
                {
                    problems.Add($"{name}: {label} {match.Value}");
                }
            }
        }

        Assert.Empty(problems);
    }

    [Fact]
    public void AppCSharp_OutsideShellLayout_HasNoRawDesignValues()
    {
        var problems = new List<string>();
        foreach (var file in AppCSharpFiles())
        {
            var text = File.ReadAllText(file);
            var name = Path.GetRelativePath(V2Root, file).Replace('\\', '/');
            foreach (Match match in CSharpRawThickness.Matches(text))
            {
                problems.Add($"{name}: raw padding/margin/spacing/thickness {match.Value}");
            }

            foreach (Match match in CSharpRawCorner.Matches(text))
            {
                problems.Add($"{name}: raw corner radius {match.Value}");
            }

            foreach (Match match in CSharpRawFontSize.Matches(text))
            {
                problems.Add($"{name}: raw font size {match.Value}");
            }

            foreach (Match match in CSharpRawOpacity.Matches(text))
            {
                problems.Add($"{name}: raw opacity {match.Value}");
            }

            foreach (Match match in CSharpBrushLiteral.Matches(text))
            {
                problems.Add($"{name}: literal brush/colour {match.Value}");
            }

            foreach (Match match in CSharpLayoutLiteral.Matches(text))
            {
                problems.Add($"{name}: raw layout literal {match.Value}");
            }
        }

        Assert.Empty(problems);
    }

    [Fact]
    public void ResponsiveBreakpoints_UseTheFrozenR18Values_AndNoLegacyThresholds()
    {
        Assert.Equal(1600, NewManga.App.Shell.V2.ShellLayout.BreakpointFull);
        Assert.Equal(1280, NewManga.App.Shell.V2.ShellLayout.BreakpointCompact);
        Assert.Equal(1024, NewManga.App.Shell.V2.ShellLayout.BreakpointNarrow);

        var offenders = new List<string>();
        foreach (var file in AppCSharpFiles().Concat(V2XamlFiles()))
        {
            var text = File.ReadAllText(file);
            if (CSharpOldBreakpoint.IsMatch(text))
            {
                offenders.Add(Path.GetRelativePath(V2Root, file).Replace('\\', '/'));
            }
        }

        Assert.Empty(offenders);
    }

    [Fact]
    public void EveryReferencedNmToken_ExistsInTheMergedDesignSystem()
    {
        var published = new HashSet<string>(NmKeys.All, StringComparer.Ordinal);
        var missing = new List<string>();
        var used = new SortedSet<string>(StringComparer.Ordinal);
        foreach (var file in V2XamlFiles())
        {
            foreach (Match match in DynamicToken.Matches(File.ReadAllText(file)))
            {
                var key = match.Groups[1].Value;
                used.Add(key);
                if (!published.Contains(key))
                {
                    missing.Add($"{Path.GetFileName(file)} → {key}");
                }
            }
        }

        Assert.Empty(missing);
        Assert.NotEmpty(used);
    }

    [Fact]
    public void Evidence_RecordsUsedTokensClassesAndStyleSources()
    {
        var tokens = new SortedSet<string>(StringComparer.Ordinal);
        var classes = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var files = V2XamlFiles();
        foreach (var file in files)
        {
            var text = File.ReadAllText(file);
            foreach (Match match in DynamicToken.Matches(text))
            {
                tokens.Add(match.Groups[1].Value);
            }

            foreach (Match match in ClassesAttribute.Matches(text))
            {
                foreach (var token in match.Groups[1].Value.Split(' ', StringSplitOptions.RemoveEmptyEntries))
                {
                    if (token.Contains('{', StringComparison.Ordinal))
                    {
                        continue;
                    }

                    classes[token] = classes.TryGetValue(token, out var count) ? count + 1 : 1;
                }
            }
        }

        var json = BuildInventoryJson(files, tokens, classes);
        var relative = Path.Combine("conformance", "v2-tokens-and-classes.json");
        var bytes = EvidenceFiles.WriteText("V11R-B-1", relative, json, nameof(Evidence_RecordsUsedTokensClassesAndStyleSources));
        Assert.NotNull(bytes);
        Assert.True(bytes > 1024, $"conformance evidence is too small: {bytes}");

        var tempPath = EvidenceFiles.TempPath("V11R-B-1", relative);
        Assert.True(File.Exists(tempPath), $"conformance evidence not written to {tempPath}");
        var written = File.ReadAllText(tempPath);
        Assert.Contains("\"nm_tokens_used\"", written, StringComparison.Ordinal);
        Assert.Contains("Nm.Color.Bg.App", written, StringComparison.Ordinal);
        Assert.True(tokens.Count >= 40, $"expected a substantial token surface, got {tokens.Count}");
    }

    [Fact]
    public void LocalFallbackTokenAndPreDsStyleFiles_AreGone()
    {
        Assert.False(File.Exists(Path.Combine(V2Root, "Views", "V2", "Shell", "Theme", "V2TokensFallback.axaml")));
        Assert.False(File.Exists(Path.Combine(V2Root, "Views", "V2", "Shell", "Theme", "V2FallbackStyles.axaml")));
        Assert.True(File.Exists(Path.Combine(V2Root, "Views", "V2", "Shell", "Theme", "V2LocalStyles.axaml")));
    }

    private static string BuildInventoryJson(
        IReadOnlyList<string> files,
        SortedSet<string> tokens,
        SortedDictionary<string, int> classes)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true }))
        {
            writer.WriteStartObject();
            writer.WriteString("generated_by", "V2ConformanceTests.Evidence_RecordsUsedTokensClassesAndStyleSources");
            writer.WriteString("design_system", "NewManga.DesignSystem (V11R-D-1 M0, merged)");
            writer.WriteBoolean("local_fallback_tokens_removed", true);
            writer.WriteStartArray("xaml_files");
            foreach (var file in files)
            {
                writer.WriteStringValue(Path.GetRelativePath(V2Root, file).Replace('\\', '/'));
            }

            writer.WriteEndArray();
            writer.WriteStartArray("nm_tokens_used");
            foreach (var token in tokens)
            {
                writer.WriteStringValue(token);
            }

            writer.WriteEndArray();
            writer.WriteStartObject("classes_used");
            foreach (var pair in classes)
            {
                writer.WriteNumber(pair.Key, pair.Value);
            }

            writer.WriteEndObject();
            writer.WriteEndObject();
        }

        return Encoding.UTF8.GetString(stream.ToArray());
    }
}
