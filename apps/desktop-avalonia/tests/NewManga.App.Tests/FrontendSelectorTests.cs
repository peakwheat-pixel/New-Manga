using NewManga.App.Services;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-PREREQ-2 AC1 (W-1/W-2b): the frontend decision table. The CLI <c>--frontend</c> wins over the
/// persisted <c>theme.frontendId</c>; an absent/unknown id falls back to the Current V2 shell and the
/// decision is recorded. <c>builtin.fluent-dark</c> is a visual theme id and must never select a shell.
/// </summary>
public sealed class FrontendSelectorTests
{
    [Fact]
    public void CliFluent_WinsOverPersistedV2()
    {
        var selection = FrontendSelector.Select("builtin.fluent", "builtin.current-v2");

        Assert.Equal(FrontendKind.Fluent, selection.Kind);
        Assert.True(selection.IsFluent);
        Assert.Equal(FrontendSource.CommandLine, selection.Source);
        Assert.Equal("builtin.fluent", selection.EffectiveFrontendId);
        Assert.False(selection.IsFallback);
        Assert.NotEmpty(selection.Diagnostic);
    }

    [Fact]
    public void CliV2_WinsOverPersistedFluent()
    {
        var selection = FrontendSelector.Select("builtin.current-v2", "builtin.fluent");

        Assert.Equal(FrontendKind.AvaloniaV2, selection.Kind);
        Assert.Equal(FrontendSource.CommandLine, selection.Source);
        Assert.Equal("builtin.current-v2", selection.EffectiveFrontendId);
        Assert.False(selection.IsFallback);
    }

    [Fact]
    public void PersistedFluent_IsUsedWhenTheCliDoesNotOverride()
    {
        var selection = FrontendSelector.Select(null, "builtin.fluent");

        Assert.Equal(FrontendKind.Fluent, selection.Kind);
        Assert.Equal(FrontendSource.AppearanceSettings, selection.Source);
        Assert.False(selection.IsFallback);
    }

    [Fact]
    public void NoInputAtAll_FallsBackToV2_WithARecordedDefaultDecision()
    {
        var selection = FrontendSelector.Select(null, null);

        Assert.Equal(FrontendKind.AvaloniaV2, selection.Kind);
        Assert.Equal(FrontendSource.Default, selection.Source);
        Assert.Equal("builtin.current-v2", selection.EffectiveFrontendId);
        Assert.False(selection.IsFallback);
        Assert.Contains("builtin.current-v2", selection.Diagnostic, StringComparison.Ordinal);
    }

    [Fact]
    public void BlankInputs_AreTreatedAsAbsent()
    {
        var selection = FrontendSelector.Select("   ", null);

        Assert.Equal(FrontendSource.Default, selection.Source);
        Assert.Equal(FrontendKind.AvaloniaV2, selection.Kind);
    }

    [Fact]
    public void UnknownFrontend_FromCli_IsRejectedWithAFailSafeWarning()
    {
        var selection = FrontendSelector.Select("builtin.arcade", null);

        Assert.Equal(FrontendKind.AvaloniaV2, selection.Kind);
        Assert.True(selection.IsFallback);
        Assert.Equal(FrontendSource.CommandLine, selection.Source);
        Assert.Equal("builtin.current-v2", selection.EffectiveFrontendId);
        Assert.Contains("builtin.arcade", selection.Diagnostic, StringComparison.Ordinal);
        Assert.Contains("fail-safe", selection.Diagnostic, StringComparison.Ordinal);
    }

    [Fact]
    public void UnknownFrontend_FromPersistedSettings_IsRejectedWithAFailSafeWarning()
    {
        var selection = FrontendSelector.Select(null, "not-a-frontend");

        Assert.Equal(FrontendKind.AvaloniaV2, selection.Kind);
        Assert.True(selection.IsFallback);
        Assert.Equal(FrontendSource.AppearanceSettings, selection.Source);
        Assert.Contains("not-a-frontend", selection.Diagnostic, StringComparison.Ordinal);
    }

    [Theory]
    [InlineData("builtin.fluent-dark")]
    [InlineData("Builtin.Fluent")]
    [InlineData("builtin_fluent")]
    public void FluentDarkOrWrongCasing_NeverSelectsTheFluentShell(string value)
    {
        var selection = FrontendSelector.Select(value, null);

        Assert.Equal(FrontendKind.AvaloniaV2, selection.Kind);
        Assert.True(selection.IsFallback);
        Assert.Equal("builtin.current-v2", selection.EffectiveFrontendId);
    }

    [Fact]
    public void SurroundingWhitespace_IsTrimmedBeforeTheFrozenIdLookup()
    {
        var selection = FrontendSelector.Select(" builtin.fluent ", null);

        Assert.Equal(FrontendKind.Fluent, selection.Kind);
        Assert.False(selection.IsFallback);
    }

    [Fact]
    public void FluentDarkAsFrontendId_IsNamedAsAVisualThemeIdMistake()
    {
        var selection = FrontendSelector.Select("builtin.fluent-dark", null);

        Assert.True(selection.IsFallback);
        Assert.Contains("visualThemeId", selection.Diagnostic, StringComparison.Ordinal);
        Assert.Contains("builtin.fluent-dark", selection.Diagnostic, StringComparison.Ordinal);
    }

    [Fact]
    public void SelectedIdIsAlwaysOneOfTheFrozenFrontendIds()
    {
        var inputs = new[]
        {
            "builtin.fluent",
            "builtin.current-v2",
            "builtin.fluent-dark",
            "unknown",
            null,
        };

        foreach (var input in inputs)
        {
            var selection = FrontendSelector.Select(input, null);
            Assert.True(
                selection.EffectiveFrontendId is "builtin.current-v2" or "builtin.fluent",
                $"unexpected effective id '{selection.EffectiveFrontendId}' for input '{input}'");
        }
    }
}
