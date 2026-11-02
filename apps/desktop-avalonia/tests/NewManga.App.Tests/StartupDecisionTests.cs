using System;
using System.IO;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Switching;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 R-003/R-004: the startup decision is the planner's single source, and a crash between
/// persisting the switch target and committing the journal is rolled back to the last committed
/// frontend before the shell starts.
/// </summary>
public sealed class StartupDecisionTests : IDisposable
{
    private readonly string _root;

    public StartupDecisionTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-startup-decision-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    private ThemeHomePaths ThemeHome()
    {
        Directory.CreateDirectory(_root);
        return new ThemeHomePaths(
            SettingsFilePath: Path.Combine(_root, "theme-settings.json"),
            ThemesDirectory: Path.Combine(_root, "themes"),
            FavoritesFilePath: Path.Combine(_root, "theme-studio-favorites.json"),
            IsCustom: true);
    }

    private AppearanceCoordinator Appearance() =>
        new(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));

    private SwitchJournal Journal() => new(Path.Combine(_root, "switch-journal.json"));

    [Fact]
    public async Task InterruptedSwitchAfterTargetPersisted_RestoresLastCommittedFrontend()
    {
        var appearance = Appearance();
        appearance.Reload();
        await appearance.SaveAsync(AppearanceDefaults.Settings with { FrontendId = FrontendSelector.FluentFrontendId });
        var journal = Journal();
        journal.Begin(FrontendSelector.FluentFrontendId, previousFrontendId: FrontendSelector.CurrentV2FrontendId);
        journal.Advance(SwitchStage.Rendered);

        App.RecoverInterruptedSwitch(ThemeHome(), appearance);

        Assert.Equal(FrontendSelector.CurrentV2FrontendId, appearance.FrontendId);
        Assert.True(journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        Assert.Contains("startup recovery", entry.Failure);
        Assert.Contains(FrontendSelector.CurrentV2FrontendId, entry.Failure);
    }

    [Fact]
    public async Task InterruptedSwitchBeforeTargetPersisted_KeepsPersistedFrontend()
    {
        var appearance = Appearance();
        appearance.Reload();
        await appearance.SaveAsync(AppearanceDefaults.Settings with { FrontendId = FrontendSelector.CurrentV2FrontendId });
        var journal = Journal();
        journal.Begin(FrontendSelector.FluentFrontendId, previousFrontendId: FrontendSelector.CurrentV2FrontendId);
        journal.Advance(SwitchStage.Building);

        App.RecoverInterruptedSwitch(ThemeHome(), appearance);

        Assert.Equal(FrontendSelector.CurrentV2FrontendId, appearance.FrontendId);
        Assert.True(journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
    }

    [Fact]
    public void StartupPlan_SelectionMatchesEffectiveFrontend()
    {
        var options = AppOptions.Parse(Array.Empty<string>());
        var fallbackPlan = SafeStartupPlanner.Plan(
            options,
            AppearanceDefaults.Settings,
            new[] { "unknown theme.visualThemeId 'nope'; falling back" });
        Assert.True(fallbackPlan.IsFallback);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, fallbackPlan.Selection.EffectiveFrontendId);
        Assert.Equal(fallbackPlan.EffectiveFrontendId, fallbackPlan.Selection.EffectiveFrontendId);

        var fluentPlan = SafeStartupPlanner.Plan(
            options,
            AppearanceDefaults.Settings with { FrontendId = FrontendSelector.FluentFrontendId },
            Array.Empty<string>());
        Assert.False(fluentPlan.IsFallback);
        Assert.Equal(FrontendSelector.FluentFrontendId, fluentPlan.Selection.EffectiveFrontendId);
    }
}
