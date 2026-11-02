using NewManga.App;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-8: the CLI parser accepts both <c>--key=value</c> and <c>--key value</c>, rejects unknown
/// options / bare value options / bad numeric values with a readable <see cref="AppOptions.InvalidReason"/>
/// (Program.Main maps that to exit code 2), and never silently mis-parses a quoted path with spaces.
/// </summary>
public sealed class AppOptionsCliRobustnessTests
{
    [Fact]
    public void EqualsForm_And_SpaceForm_AreEquivalent()
    {
        var equalsForm = AppOptions.Parse(new[]
        {
            @"--data-root=C:\tmp\nm data", "--log-dir=C:\\tmp\\nm logs",
            @"--sidecar-dir=C:\tmp\nm sidecar", "--width=1280", "--height=800",
            "--variant=dark", "--shell=legacy",
        });
        var spaceForm = AppOptions.Parse(new[]
        {
            "--data-root", @"C:\tmp\nm data", "--log-dir", @"C:\tmp\nm logs",
            "--sidecar-dir", @"C:\tmp\nm sidecar", "--width", "1280", "--height", "800",
            "--variant", "dark", "--shell", "legacy",
        });

        foreach (var options in new[] { equalsForm, spaceForm })
        {
            Assert.Null(options.InvalidReason);
            Assert.Equal(@"C:\tmp\nm data", options.DataRoot);
            Assert.Equal(@"C:\tmp\nm logs", options.LogDirectory);
            Assert.Equal(@"C:\tmp\nm sidecar", options.SidecarDirectory);
            Assert.Equal(1280, options.WindowWidth);
            Assert.Equal(800, options.WindowHeight);
            Assert.Equal("dark", options.StartupVariant);
            Assert.Equal("legacy", options.Shell);
            Assert.False(options.UseV2Shell);
        }
    }

    [Fact]
    public void BareValueOption_IsRejected_WithReadableReason()
    {
        var options = AppOptions.Parse(new[] { "--data-root" });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--data-root", options.InvalidReason, StringComparison.Ordinal);
        Assert.Contains("requires a value", options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public void ValueOption_FollowedByAnotherOption_IsRejected()
    {
        var options = AppOptions.Parse(new[] { "--sidecar-dir", "--width=100" });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--sidecar-dir", options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public void UnknownOption_IsRejected()
    {
        Assert.NotNull(AppOptions.Parse(new[] { "--bogus=1" }).InvalidReason);
        Assert.NotNull(AppOptions.Parse(new[] { "--bogus", "value" }).InvalidReason);
    }

    [Fact]
    public void UnknownPositionalToken_IsRejected()
    {
        var options = AppOptions.Parse(new[] { @"C:\tmp\stray" });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("unexpected positional argument", options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public void EmptyValue_IsRejected_ForEveryKey()
    {
        foreach (var raw in new[] { "--log-dir=", "--data-root=", "--sidecar-dir=", "--width=" })
        {
            var options = AppOptions.Parse(new[] { raw });
            Assert.NotNull(options.InvalidReason);
            Assert.Contains("non-empty", options.InvalidReason, StringComparison.Ordinal);
        }
    }

    [Theory]
    [InlineData("--width=abc")]
    [InlineData("--height=-5")]
    [InlineData("--height=0")]
    [InlineData("--exit-after=abc")]
    [InlineData("--exit-after=-1")]
    public void InvalidNumericValue_IsRejected(string raw)
    {
        var options = AppOptions.Parse(new[] { raw });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains(raw[..raw.IndexOf('=')], options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public void InvalidShellValue_IsRejected()
    {
        var options = AppOptions.Parse(new[] { "--shell=v1" });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--shell", options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public void BooleanSwitches_StillWorkBare()
    {
        var parity = AppOptions.Parse(new[] { "--parity" });
        Assert.Null(parity.InvalidReason);
        Assert.True(parity.ParityReached);

        var smoke = AppOptions.Parse(new[] { "--smoke" });
        Assert.Null(smoke.InvalidReason);
        Assert.Equal(1500, smoke.ExitAfterMs);

        var legacyCheck = AppOptions.Parse(new[] { "--legacy-shell-check" });
        Assert.Null(legacyCheck.InvalidReason);
        Assert.True(legacyCheck.DetectLegacyShell);
    }

    [Fact]
    public void DemoWrite_StillRequiresAnExplicitDataRoot()
    {
        var options = AppOptions.Parse(new[] { "--demo-write" });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--data-root", options.InvalidReason, StringComparison.Ordinal);
    }

    // ── REALUSE-DATA-SAFETY-5 AC1 (audit MA-14): --page / --variant must be validated ─────────

    [Theory]
    [InlineData("bookshelf")]
    [InlineData("library")]
    [InlineData("reader")]
    [InlineData("workbench")]
    [InlineData("studio")]
    [InlineData("settings")]
    [InlineData("console")]
    public void Parse_AcceptsEveryPageTheShellCanNavigateTo(string page)
    {
        var options = AppOptions.Parse(new[] { "--page", page });

        Assert.Null(options.InvalidReason);
        Assert.Equal(page, options.StartupPage);
    }

    [Theory]
    [InlineData("nonsense")]
    [InlineData("bogshelf")]
    [InlineData("Reader ")]
    public void Parse_RejectsAnUnknownPage_InsteadOfSilentlyIgnoringIt(string page)
    {
        var options = AppOptions.Parse(new[] { "--page", page });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--page", options.InvalidReason, StringComparison.Ordinal);
    }

    [Theory]
    [InlineData("light")]
    [InlineData("dark")]
    [InlineData("DARK")]
    public void Parse_AcceptsTheTwoVariantsTheShellConsumes(string variant)
    {
        var options = AppOptions.Parse(new[] { "--variant", variant });

        Assert.Null(options.InvalidReason);
        Assert.NotNull(options.StartupVariant);
    }

    [Fact]
    public void Parse_RejectsAnUnknownVariant()
    {
        var options = AppOptions.Parse(new[] { "--variant", "blue" });

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--variant", options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public void Frontend_Option_IsParsedBothWays()
    {
        var equalsForm = AppOptions.Parse(new[] { "--frontend=builtin.fluent" });
        Assert.Null(equalsForm.InvalidReason);
        Assert.Equal("builtin.fluent", equalsForm.FrontendId);

        var spaceForm = AppOptions.Parse(new[] { "--frontend", "builtin.current-v2" });
        Assert.Equal("builtin.current-v2", spaceForm.FrontendId);

        var empty = AppOptions.Parse(new[] { "--frontend=" });
        Assert.NotNull(empty.InvalidReason);
    }
}
