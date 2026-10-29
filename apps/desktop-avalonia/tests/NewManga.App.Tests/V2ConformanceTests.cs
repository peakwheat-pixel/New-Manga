using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using NewManga.DesignSystem;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-1 AC4 governance: static conformance of the V2 XAML against the frozen design contract —
/// no raw colour / font-size / spacing / shadow / gradient / blur values, no radius above 3px, and
/// every {DynamicResource Nm.*} key must exist in the merged Design System token set. Also emits the
///「用到的 Nm.* 键 / Classes 清单」evidence JSON for the L3 review.
/// </summary>
public sealed class V2ConformanceTests
{
    private static readonly Regex DynamicToken = new(@"\{DynamicResource\s+(Nm\.[A-Za-z0-9.]+)\s*\}", RegexOptions.Compiled);
    private static readonly Regex RawHex = new(@"#[0-9A-Fa-f]{3,8}\b", RegexOptions.Compiled);
    private static readonly Regex RawFontSize = new(@"FontSize=""\d", RegexOptions.Compiled);
    private static readonly Regex RawNumericWidth = new(@"\b(Width|Height|MinWidth|MinHeight|MaxWidth|MaxHeight)=""\d", RegexOptions.Compiled);
    private static readonly Regex ForbiddenEffect = new(@"BoxShadow|LinearGradient|RadialGradient|BlurEffect|OpacityMask|backdrop", RegexOptions.Compiled | RegexOptions.IgnoreCase);
    private static readonly Regex RawCornerRadius = new(@"CornerRadius=""([4-9]|\d\d+)", RegexOptions.Compiled);
    private static readonly Regex ClassesAttribute = new(@"Classes=""([^""]+)""", RegexOptions.Compiled);

    private static string V2Root => Path.Combine(RepoRoot(), "src", "NewManga.App");

    public static string EvidenceRoot
    {
        get
        {
            var root = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
            if (string.IsNullOrWhiteSpace(root))
            {
                root = Path.Combine(Path.GetTempPath(), "newmanga-v11r-b1-evidence");
            }

            Directory.CreateDirectory(root);
            return root;
        }
    }

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

    [Fact]
    public void V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects()
    {
        var problems = new List<string>();
        foreach (var file in V2XamlFiles())
        {
            var text = File.ReadAllText(file);
            var name = Path.GetFileName(file);
            foreach (Match match in RawHex.Matches(text))
            {
                problems.Add($"{name}: raw colour {match.Value}");
            }

            foreach (Match match in RawFontSize.Matches(text))
            {
                problems.Add($"{name}: raw font size {match.Value}");
            }

            foreach (Match match in RawNumericWidth.Matches(text))
            {
                problems.Add($"{name}: raw size {match.Value}");
            }

            foreach (Match match in ForbiddenEffect.Matches(text))
            {
                problems.Add($"{name}: forbidden effect {match.Value}");
            }

            foreach (Match match in RawCornerRadius.Matches(text))
            {
                problems.Add($"{name}: radius above 3px {match.Value}");
            }
        }

        Assert.Empty(problems);
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

        var path = Path.Combine(EvidenceRoot, "conformance", "v2-tokens-and-classes.json");
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using (var stream = File.Create(path))
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

        var json = File.ReadAllText(path);
        Assert.Contains("\"nm_tokens_used\"", json, StringComparison.Ordinal);
        Assert.Contains("Nm.Color.Bg.App", json, StringComparison.Ordinal);
        Assert.True(tokens.Count >= 40, $"expected a substantial token surface, got {tokens.Count}");
        Assert.True(new FileInfo(path).Length > 1024, "conformance evidence is too small");
    }

    [Fact]
    public void LocalFallbackTokenAndPreDsStyleFiles_AreGone()
    {
        // Lead instruction after V11R-D-1 M0: the pre-DS token dictionary / replacement styles must be
        // deleted so the Design System is the single visual source.
        Assert.False(File.Exists(Path.Combine(V2Root, "Views", "V2", "Shell", "Theme", "V2TokensFallback.axaml")));
        Assert.False(File.Exists(Path.Combine(V2Root, "Views", "V2", "Shell", "Theme", "V2FallbackStyles.axaml")));
        Assert.True(File.Exists(Path.Combine(V2Root, "Views", "V2", "Shell", "Theme", "V2LocalStyles.axaml")));
    }
}
