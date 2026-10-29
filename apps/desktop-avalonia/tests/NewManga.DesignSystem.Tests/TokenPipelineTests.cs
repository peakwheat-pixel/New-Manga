using NewManga.DesignSystem.Tokens;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC1: the token pipeline is a reproducible generator over the frozen DTCG baseline, and every frozen
/// leaf token is mapped to exactly one published <c>Nm.*</c> key.
/// </summary>
public sealed class TokenPipelineTests
{
    [Fact]
    public void Generated_artifacts_match_the_frozen_token_source()
    {
        var result = TokenGenerator.Generate(File.ReadAllText(TestPaths.TokensFixture));

        Assert.True(
            TokenGenerator.IsUpToDate(result, TestPaths.DesignSystemProject, out var mismatches),
            "generated artifacts are stale - run the token generator. Mismatches: " +
            string.Join("; ", mismatches));
    }

    [Fact]
    public void Generation_is_deterministic_in_process()
    {
        var tokensJson = File.ReadAllText(TestPaths.TokensFixture);

        var first = TokenGenerator.Generate(tokensJson);
        var second = TokenGenerator.Generate(tokensJson);

        Assert.Equal(
            first.Files.Select(static file => file.RelativePath),
            second.Files.Select(static file => file.RelativePath));
        foreach (var (left, right) in first.Files.Zip(second.Files))
        {
            Assert.Equal(left.Content, right.Content);
        }
    }

    [Fact]
    public void Every_frozen_token_is_mapped_exactly_once()
    {
        var entries = TokenDocument.Parse(File.ReadAllText(TestPaths.TokensFixture));

        var dark = entries.Where(static entry => entry.Path.StartsWith(TokenMap.DarkScope, StringComparison.Ordinal)).ToArray();
        var light = entries.Where(static entry => entry.Path.StartsWith(TokenMap.LightScope, StringComparison.Ordinal)).ToArray();
        var globals = entries
            .Where(static entry =>
                !entry.Path.StartsWith(TokenMap.DarkScope, StringComparison.Ordinal) &&
                !entry.Path.StartsWith(TokenMap.LightScope, StringComparison.Ordinal))
            .ToArray();

        Assert.Equal(35, dark.Length);
        Assert.Equal(35, light.Length);
        Assert.Equal(71, globals.Length);
        Assert.Equal(141, entries.Count);

        var globalBindings = TokenMap.GlobalBindings.ToDictionary(static binding => binding.TokenPath, StringComparer.Ordinal);
        Assert.Equal(71, globalBindings.Count);
        Assert.All(globals, entry => Assert.True(
            globalBindings.ContainsKey(entry.Path),
            $"global token '{entry.Path}' has no resource-key mapping"));

        var darkKeys = dark.Select(static entry => TokenMap.ColorResourceKey(entry.Path)).ToArray();
        var lightKeys = light.Select(static entry => TokenMap.ColorResourceKey(entry.Path)).ToArray();
        Assert.Equal(35, darkKeys.Distinct(StringComparer.Ordinal).Count());
        Assert.Equal(darkKeys.OrderBy(static key => key, StringComparer.Ordinal), lightKeys.OrderBy(static key => key, StringComparer.Ordinal));
    }

    [Fact]
    public void Resource_keys_follow_the_contract_naming_rule()
    {
        var result = TokenGenerator.Generate(File.ReadAllText(TestPaths.TokensFixture));
        var keys = result.Rows.Select(static row => row.ResourceKey).Distinct(StringComparer.Ordinal).ToArray();

        Assert.NotEmpty(keys);
        foreach (var key in keys)
        {
            Assert.StartsWith("Nm.", key, StringComparison.Ordinal);
            foreach (var segment in key.Split('.'))
            {
                Assert.False(string.IsNullOrWhiteSpace(segment), $"'{key}' has an empty segment");
                Assert.True(
                    char.IsUpper(segment[0]) || char.IsDigit(segment[0]),
                    $"'{key}' segment '{segment}' must be PascalCase");
            }
        }
    }

    [Fact]
    public void Every_published_key_has_a_csharp_constant()
    {
        var result = TokenGenerator.Generate(File.ReadAllText(TestPaths.TokensFixture));
        var published = result.Rows.Select(static row => row.ResourceKey).ToHashSet(StringComparer.Ordinal);

        Assert.NotEmpty(NmKeys.All);
        Assert.Equal(published.OrderBy(static key => key, StringComparer.Ordinal), NmKeys.All.OrderBy(static key => key, StringComparer.Ordinal));
        Assert.All(NmKeys.All, key => Assert.Contains(key, published));
        Assert.All(published, key => Assert.Contains(key, NmKeys.All));
    }
}
