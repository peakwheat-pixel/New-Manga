using NewManga.App.Services;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-14-SET-1 (AC2): the pure fallback-resolution matrix; and (AC1) the projection
/// shape with an injected source. No Avalonia <c>Application</c> is required.
/// </summary>
public sealed class TypographyResolverTests
{
    private static Func<string, bool> Installed(params string[] families) => family =>
        families.Contains(family, StringComparer.OrdinalIgnoreCase);

    [Fact]
    public void ResolvesTheFirstInstalledFamilyAndListsTheMissingOnes()
    {
        var line = TypographyResolver.Resolve(
            "Nm.FontFamily.Ui",
            "\"Missing A\", Installed B, sans-serif",
            Installed("Installed B"));

        Assert.Equal("Installed B", line.ResolvedFamily);
        Assert.Equal(["Missing A"], line.Missing);
        // DSH 裁决：fallback = 请求的首族未被使用（至少一段缺失）。
        Assert.True(line.Fallback);
        Assert.Equal("\"Missing A\", Installed B, sans-serif", line.StackRaw);
    }

    [Fact]
    public void FallsBackToTheGenericTailWhenEveryFamilyIsMissing()
    {
        var line = TypographyResolver.Resolve(
            "Nm.FontFamily.Data",
            "Missing A, Missing B, serif",
            Installed());

        Assert.Equal("serif", line.ResolvedFamily);
        Assert.Equal(["Missing A", "Missing B"], line.Missing);
        Assert.True(line.Fallback);
    }

    [Fact]
    public void AnEmptyStackIsUnavailableRatherThanFabricated()
    {
        var line = TypographyResolver.Resolve("Nm.FontFamily.Display", "  ", Installed());

        Assert.Equal("sans-serif", line.ResolvedFamily);
        Assert.Empty(line.Missing);
        Assert.True(line.Fallback);
    }

    [Fact]
    public void ScaleAndLineHeightAreCarriedThroughUntouched()
    {
        var line = TypographyResolver.Resolve(
            "Nm.FontFamily.Ui", "Installed B", Installed("Installed B"), scale: 1.25, lineHeight: 1.6);

        Assert.Equal(1.25, line.Scale);
        Assert.Equal(1.6, line.LineHeight);
    }

    [Fact]
    public void ProjectionRendersThreeLinesFromTheInjectedSource()
    {
        var snapshot = new TypographySnapshot(
            [
                TypographyResolver.Resolve("Nm.FontFamily.Ui", "Installed B", Installed("Installed B")),
                TypographyResolver.Resolve("Nm.FontFamily.Data", "Installed B", Installed("Installed B")),
                TypographyResolver.Resolve("Nm.FontFamily.Display", "Installed B", Installed("Installed B")),
            ],
            Available: true,
            UnavailableReason: null);

        Assert.True(snapshot.Available);
        Assert.Equal(3, snapshot.Lines.Count);
        Assert.All(snapshot.Lines, line => Assert.Equal("Installed B", line.ResolvedFamily));
    }

    [Fact]
    public void AnUnavailableThemeIsAStablePlaceholderNotACrash()
    {
        var snapshot = new TypographySnapshot(
            Array.Empty<TypographyLine>(), false, "当前主题未初始化（缺少 Nm.FontFamily.* 资源）。");

        Assert.False(snapshot.Available);
        Assert.Empty(snapshot.Lines);
        Assert.False(string.IsNullOrWhiteSpace(snapshot.UnavailableReason));
    }
}
