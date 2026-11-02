using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 R-017: the Fluent settings surface mirrors the single appearance writer, except for a
/// frontend-only canonical change (a runtime frontend switch), which must preserve the user's unapplied
/// draft (A01 no-data-loss) instead of silently discarding it.
/// </summary>
public sealed class SettingsDraftSyncTests : IDisposable
{
    private readonly string _root;
    private readonly AppearanceCoordinator _appearance;

    public SettingsDraftSyncTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-draft-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
        _appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        _appearance.Reload();
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

    private SettingsViewModel CreateSettings() => new(host: null, _appearance, themeManager: null);

    private static void PumpUntil(Func<bool> condition, int timeoutMs = 5000)
    {
        var deadline = DateTime.UtcNow.AddMilliseconds(timeoutMs);
        while (!condition() && DateTime.UtcNow < deadline)
        {
            Dispatcher.UIThread.RunJobs();
            Thread.Sleep(5);
        }

        Dispatcher.UIThread.RunJobs();
    }

    private async Task SaveAndSettleAsync(AppearanceSettings next, Func<bool> settled)
    {
        await _appearance.SaveAsync(next);
        PumpUntil(settled);
        Assert.True(settled(), "the settings surface did not observe the canonical appearance change");
    }

    private static AppearanceSettings DirtyDraft(AppearanceSettings current) =>
        current with { MotionMode = MotionMode.Reduce };

    [AvaloniaFact]
    public async Task ExternalAppearanceChange_WhenClean_MirrorsCanonicalSettings()
    {
        var settings = CreateSettings();
        var dark = _appearance.Settings with { Mode = AppearanceMode.Dark };

        await SaveAndSettleAsync(dark, () => settings.Draft.Mode == AppearanceMode.Dark);

        Assert.Equal(dark, settings.Draft);
        Assert.False(settings.IsDirty);
    }

    /// <summary>R-017 regression: a real external change must win over (and clear) a dirty draft.</summary>
    [AvaloniaFact]
    public async Task ExternalAppearanceChange_WhenDirty_MirrorsCanonicalAndClearsTheDraft()
    {
        var settings = CreateSettings();
        settings.UpdateDraft(DirtyDraft(settings.Draft));
        Assert.True(settings.IsDirty);

        var dark = _appearance.Settings with { Mode = AppearanceMode.Dark };
        await SaveAndSettleAsync(dark, () => settings.Draft.Mode == AppearanceMode.Dark);

        Assert.Equal(dark, settings.Draft);
        Assert.False(settings.IsDirty);
    }

    [AvaloniaFact]
    public async Task FrontendOnlyChange_WhenClean_AdoptsFrontendIdAndStaysClean()
    {
        var settings = CreateSettings();
        var toFluent = _appearance.Settings with { FrontendId = FrontendSelector.FluentFrontendId };

        await SaveAndSettleAsync(toFluent, () => settings.Draft.FrontendId == FrontendSelector.FluentFrontendId);

        Assert.Equal(toFluent, settings.Draft);
        Assert.False(settings.IsDirty);
    }

    /// <summary>A01: the runtime frontend switch only changes theme.frontendId; the unapplied draft survives.</summary>
    [AvaloniaFact]
    public async Task FrontendOnlyChange_WhenDirty_PreservesTheUnappliedDraft()
    {
        var settings = CreateSettings();
        var draft = DirtyDraft(settings.Draft);
        settings.UpdateDraft(draft);
        Assert.True(settings.IsDirty);

        var toFluent = _appearance.Settings with { FrontendId = FrontendSelector.FluentFrontendId };
        await SaveAndSettleAsync(toFluent, () => settings.Draft.FrontendId == FrontendSelector.FluentFrontendId);

        Assert.Equal(draft with { FrontendId = FrontendSelector.FluentFrontendId }, settings.Draft);
        Assert.True(settings.IsDirty);
    }

    [AvaloniaFact]
    public async Task DuplicateCanonicalNotification_DoesNotClobberADirtyDraft()
    {
        var settings = CreateSettings();
        var draft = DirtyDraft(settings.Draft);
        settings.UpdateDraft(draft);

        await _appearance.SaveAsync(_appearance.Settings); // unchanged document -> no Changed event
        PumpUntil(() => false, timeoutMs: 50);

        Assert.Equal(draft, settings.Draft);
        Assert.True(settings.IsDirty);
    }

    /// <summary>
    /// R-017 commit/rollback regression: the switch transaction persists the frontend id twice (commit
    /// target, rollback previous); both are frontend-only changes and must keep the dirty draft.
    /// </summary>
    [AvaloniaFact]
    public async Task SwitchCommitThenRollback_KeepsTheDirtyDraftAndRestoresTheFrontendId()
    {
        var settings = CreateSettings();
        var draft = DirtyDraft(settings.Draft);
        settings.UpdateDraft(draft);
        var original = _appearance.Settings;

        await SaveAndSettleAsync(
            original with { FrontendId = FrontendSelector.FluentFrontendId },
            () => settings.Draft.FrontendId == FrontendSelector.FluentFrontendId);
        Assert.True(settings.IsDirty);
        Assert.Equal(draft with { FrontendId = FrontendSelector.FluentFrontendId }, settings.Draft);

        await SaveAndSettleAsync(original, () => settings.Draft.FrontendId == original.FrontendId);
        Assert.True(settings.IsDirty);
        Assert.Equal(draft with { FrontendId = original.FrontendId }, settings.Draft);
    }

    /// <summary>A frontend merge must not swallow the next real external change.</summary>
    [AvaloniaFact]
    public async Task FrontendMergeThenRealChange_MirrorsTheRealChange()
    {
        var settings = CreateSettings();
        settings.UpdateDraft(DirtyDraft(settings.Draft));

        await SaveAndSettleAsync(
            _appearance.Settings with { FrontendId = FrontendSelector.FluentFrontendId },
            () => settings.Draft.FrontendId == FrontendSelector.FluentFrontendId);
        Assert.True(settings.IsDirty);

        var highContrast = _appearance.Settings with { Contrast = AppearanceContrast.High };
        await SaveAndSettleAsync(highContrast, () => settings.Draft.Contrast == AppearanceContrast.High);

        Assert.Equal(highContrast, settings.Draft);
        Assert.False(settings.IsDirty);
    }
}
