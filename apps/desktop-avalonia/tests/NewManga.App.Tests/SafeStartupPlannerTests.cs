using NewManga.App.Services;
using NewManga.Appearance;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC4/AC7: the safe-startup decision keeps the frozen fail-safe policy (unknown frontend or a
/// broken appearance document never blocks startup) and surfaces every fallback as diagnostics.
/// </summary>
public sealed class SafeStartupPlannerTests
{
    private static StartupPlan Plan(string[] args, AppearanceSettings? settings = null, string[]? warnings = null) =>
        SafeStartupPlanner.Plan(
            AppOptions.Parse(args),
            settings ?? AppearanceDefaults.Settings,
            warnings ?? Array.Empty<string>());

    [Fact]
    public void DefaultArgs_StartCurrentV2()
    {
        var plan = Plan(Array.Empty<string>());

        Assert.Equal(StartupShellKind.Default, plan.ShellKind);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);
        Assert.False(plan.IsFallback);
        Assert.NotEmpty(plan.Diagnostics);
    }

    [Fact]
    public void CliFluent_WinsOverPersisted()
    {
        var plan = Plan(new[] { "--frontend=builtin.fluent" });

        Assert.Equal(StartupShellKind.Default, plan.ShellKind);
        Assert.Equal(FrontendSelector.FluentFrontendId, plan.EffectiveFrontendId);
        Assert.False(plan.IsFallback);
    }

    [Fact]
    public void PersistedFluent_UsedWhenNoCliFrontend()
    {
        var plan = Plan(
            Array.Empty<string>(),
            AppearanceDefaults.Settings with { FrontendId = FrontendSelector.FluentFrontendId });

        Assert.Equal(FrontendSelector.FluentFrontendId, plan.EffectiveFrontendId);
        Assert.False(plan.IsFallback);
    }

    [Fact]
    public void UnknownCliFrontend_FallsBackToCurrentV2()
    {
        var plan = Plan(new[] { "--frontend=builtin.not-a-frontend" });

        Assert.True(plan.IsFallback);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);
        Assert.Contains(plan.Diagnostics, d => d.Contains("builtin.not-a-frontend", StringComparison.Ordinal));
    }

    [Fact]
    public void VisualThemeId_FallsBackToCurrentV2()
    {
        var plan = Plan(new[] { "--frontend=builtin.fluent-dark" });

        Assert.True(plan.IsFallback);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);
    }

    [Fact]
    public void LegacyShell_WinsOverFrontendAndPresentationHost()
    {
        var plan = Plan(new[] { "--shell=legacy", "--frontend=builtin.fluent", "--presentation-host=true" });

        Assert.Equal(StartupShellKind.Legacy, plan.ShellKind);
    }

    [Fact]
    public void PresentationHost_IsElectedForTheStableWindow()
    {
        var plan = Plan(new[] { "--presentation-host=true" });

        Assert.Equal(StartupShellKind.PresentationHost, plan.ShellKind);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);
    }

    [Fact]
    public void AppearanceWarnings_AreSurfacedAsDiagnostics()
    {
        var plan = Plan(
            Array.Empty<string>(),
            warnings: new[] { "unknown theme.frontendId 'x'; falling back to 'builtin.current-v2'" });

        Assert.Contains(plan.Diagnostics, d => d.Contains("appearance:", StringComparison.Ordinal));
    }


    [Fact]
    public void AppearanceFallback_ForcesCurrentV2EvenWhenPersistedFrontendIsFluent()
    {
        var plan = Plan(
            Array.Empty<string>(),
            AppearanceDefaults.Settings with { FrontendId = FrontendSelector.FluentFrontendId },
            new[] { "unknown theme.visualThemeId 'nope'; falling back to 'newmanga-default'" });

        Assert.True(plan.IsFallback);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);
        Assert.Contains(plan.Diagnostics, d => d.Contains("appearance:", StringComparison.Ordinal));
    }

    [Fact]
    public void AppearanceFallback_AlsoWinsOverExplicitCliFrontend()
    {
        var plan = Plan(
            new[] { "--frontend=builtin.fluent" },
            AppearanceDefaults.Settings,
            new[] { "unknown scale '9.9'; falling back to the shipped scale" });

        Assert.True(plan.IsFallback);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);
    }
}