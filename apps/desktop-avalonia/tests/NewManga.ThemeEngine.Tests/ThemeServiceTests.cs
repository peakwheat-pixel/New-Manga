using Avalonia.Media;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Part B service contract (no Avalonia needed thanks to <see cref="IThemeLayerSink"/>): initialize /
/// migration / appearance / contrast / motion / layout / reset / apply with fallback / persistence
/// failure tolerance / preview wiring. Every failure path must recover to <c>newmanga-default</c>
/// (or the design system built-in layer) and expose <c>LastError</c> instead of throwing.
/// </summary>
public sealed class ThemeServiceTests : IDisposable
{
    private readonly TempDirectory _temp = new();
    private readonly ThemeSettingsStore _store;
    private readonly ThemeRegistry _registry;
    private readonly FakeThemeLayerSink _sink = new();
    private readonly List<EventArgs> _changes = [];

    public ThemeServiceTests()
    {
        var themeDirectory = _temp.File("themes");
        Directory.CreateDirectory(themeDirectory);
        File.WriteAllText(
            Path.Combine(themeDirectory, "ocean.nmtheme"),
            ThemeFixtures.Write(ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, "ocean", "Ocean")));

        _registry = new ThemeRegistry(themeDirectory);
        _store = new ThemeSettingsStore(_temp.File("theme-settings.json"), _registry);
    }

    public void Dispose() => _temp.Dispose();

    private ThemeService CreateService(
        IThemeRegistry? registry = null,
        IThemePersistence? persistence = null,
        IThemeLayerSink? sink = null)
    {
        var service = new ThemeService(registry ?? _registry, persistence ?? _store, sink ?? _sink);
        service.Changed += (_, args) => _changes.Add(args);
        return service;
    }

    [Fact]
    public async Task Initialize_applies_the_default_theme_and_reports_readiness()
    {
        using var service = CreateService();

        await service.InitializeAsync();

        Assert.True(service.IsInitialized);
        Assert.Equal(ThemeDefaults.Settings, service.Settings);
        Assert.Equal(ThemeDefaults.DefaultThemeId, service.Current.Id);
        Assert.Equal(ThemeDefaults.DefaultThemeId, _sink.LastAppliedThemeId);
        Assert.NotNull(_sink.LastLayer);
        Assert.Equal(ThemePaletteComposer.ThemeLayerKeyCount, _sink.LastLayer!.Count);
        Assert.Single(_changes);
        Assert.Null(service.LastError);
    }

    [Fact]
    public async Task Initialize_is_idempotent()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        var applyCount = _sink.ApplyCount;

        await service.InitializeAsync();

        Assert.Equal(applyCount, _sink.ApplyCount);
        Assert.Single(_changes);
    }

    [Fact]
    public async Task Initialize_migrates_a_legacy_theme_id_and_persists_the_migrated_settings()
    {
        File.WriteAllText(
            _temp.File("theme-settings.json"),
            """{ "schema": "newmanga.theme-settings/1", "themeId": "saber-purple" }""");
        using var service = CreateService();

        await service.InitializeAsync();

        Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
        Assert.Equal(AppearanceMode.Dark, service.Settings.Appearance);
        Assert.Equal(AppearanceMode.Dark, _sink.Appearance);
        Assert.Contains(service.LastIssues, issue => issue.Code == ThemeIssueCodes.SettingsLegacyThemeId);
        var written = ThemeSettingsJson.Read(File.ReadAllText(_temp.File("theme-settings.json"))).Settings;
        Assert.Equal(ThemeDefaults.DefaultThemeId, written.ThemeId);
        Assert.Equal(AppearanceMode.Dark, written.Appearance);
    }

    [Fact]
    public async Task Initialize_survives_a_corrupt_settings_file()
    {
        File.WriteAllText(_temp.File("theme-settings.json"), "{ not json");
        using var service = CreateService();

        await service.InitializeAsync();

        Assert.True(service.IsInitialized);
        Assert.Equal(ThemeDefaults.Settings, service.Settings);
        Assert.Contains(service.LastIssues, issue => issue.Code == ThemeIssueCodes.SettingsJsonInvalid);
        Assert.Equal(ThemeDefaults.DefaultThemeId, _sink.LastAppliedThemeId);
    }

    [Fact]
    public async Task Initialize_falls_back_to_the_builtin_layer_when_the_default_theme_cannot_be_applied()
    {
        _sink.ApplyThemeLayerResult = false;
        using var service = CreateService();

        await service.InitializeAsync();

        Assert.True(service.IsInitialized);
        Assert.Equal(1, _sink.RevertCount);
        Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
        Assert.Contains(service.LastIssues, issue => issue.Code == ThemeIssueCodes.ThemeFallbackApplied);
    }

    [Fact]
    public async Task Initialize_never_throws_when_even_the_builtin_layer_fails()
    {
        _sink.ApplyThemeLayerResult = false;
        _sink.RevertResult = false;
        using var service = CreateService();

        await service.InitializeAsync();

        Assert.True(service.IsInitialized);
        Assert.Equal(ThemeDefaults.Settings, service.Settings);
        Assert.NotNull(service.LastError);
        Assert.Contains(service.LastIssues, issue => issue.Code == ThemeIssueCodes.ThemeLayerApplyFailed);
    }

    [Fact]
    public async Task Apply_unknown_theme_recovers_to_the_default_theme()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        _changes.Clear();

        var result = await service.ApplyAsync("ghost-theme");

        Assert.True(result.Success);
        Assert.True(result.Recovered);
        Assert.Equal(ThemeDefaults.DefaultThemeId, result.AppliedThemeId);
        Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
        Assert.Equal(ThemeDefaults.DefaultThemeId, _sink.LastAppliedThemeId);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.ThemeNotFound);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.ThemeFallbackApplied);
        Assert.Single(_changes);
        Assert.Null(service.LastError);
    }

    [Fact]
    public async Task Apply_valid_user_theme_composes_its_layer_and_persists()
    {
        using var service = CreateService();
        await service.InitializeAsync();

        var result = await service.ApplyAsync("ocean");

        Assert.True(result.Success);
        Assert.False(result.Recovered);
        Assert.Equal("ocean", result.AppliedThemeId);
        Assert.Equal("ocean", service.Settings.ThemeId);
        Assert.Equal("ocean", service.Current.Id);
        Assert.Equal("ocean", _sink.LastAppliedThemeId);
        Assert.Equal(
            ExpectedColor(PaletteVariant.Dark, "Nm.Color.Bg.Canvas"),
            ColorOf(_sink.LastLayer!, "Nm.Color.Bg.Canvas"));
        var reloaded = new ThemeSettingsStore(_temp.File("theme-settings.json")).Load();
        Assert.Equal("ocean", reloaded.ThemeId);
    }

    [Fact]
    public async Task Apply_succeeds_with_contrast_warnings_that_do_not_block()
    {
        using var service = CreateService();
        await service.InitializeAsync();

        var result = await service.ApplyAsync(ThemeDefaults.DefaultThemeId);

        Assert.True(result.Success);
        Assert.False(result.Recovered);
        Assert.Contains(result.Issues, issue =>
            issue.Code == ThemeIssueCodes.ContrastStatus && issue.Severity == ThemeValidationIssue.WarningSeverity);
        Assert.DoesNotContain(result.Issues, issue => issue.IsError);
    }

    [Fact]
    public async Task Apply_falls_back_when_the_package_is_invalid()
    {
        var broken = ThemeFixtures.DefaultPackage with
        {
            Descriptor = ThemeFixtures.DefaultPackage.Descriptor with { Id = "broken", Kind = ThemeKind.User },
            Dark = ThemeFixtures.WithColor(
                ThemeFixtures.DefaultPackage.Dark,
                "Nm.Color.Bg.Panel",
                "linear-gradient(#fff,#000)"),
        };
        var stub = new StubThemeRegistry()
            .Add(ThemeFixtures.DefaultPackage)
            .Add(broken);
        using var service = CreateService(stub, new RecordingPersistence(), _sink);
        await service.InitializeAsync();

        var result = await service.ApplyAsync("broken");

        Assert.True(result.Success);
        Assert.True(result.Recovered);
        Assert.Equal(ThemeDefaults.DefaultThemeId, result.AppliedThemeId);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.ColorInvalidValue);
        Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
    }

    [Fact]
    public async Task Apply_falls_back_when_loading_the_theme_throws()
    {
        var stub = new StubThemeRegistry().Add(ThemeFixtures.DefaultPackage);
        stub.LoadOverride = id => throw new ThemePackageException(
            "boom",
            [ThemeValidationIssue.Error(ThemeIssueCodes.ThemeNotFound, "unreadable package", id)]);
        using var service = CreateService(stub, new RecordingPersistence(), _sink);
        await service.InitializeAsync();

        var result = await service.ApplyAsync(ThemeDefaults.DefaultThemeId);

        Assert.True(result.Success);
        Assert.True(result.Recovered);
        Assert.Equal(ThemeDefaults.DefaultThemeId, result.AppliedThemeId);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.ThemeNotFound);
    }

    [Fact]
    public async Task Apply_reports_failure_and_keeps_the_previous_theme_when_nothing_can_be_applied()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        var appliedBefore = service.Settings;
        _changes.Clear();
        _sink.ApplyThemeLayerResult = false;
        _sink.RevertResult = false;

        var result = await service.ApplyAsync("ocean");

        Assert.False(result.Success);
        Assert.Null(result.AppliedThemeId);
        Assert.Equal(appliedBefore, service.Settings);
        Assert.NotNull(service.LastError);
        Assert.Empty(_changes);
    }

    [Fact]
    public async Task Set_appearance_recomposes_the_palette_for_the_new_variant_and_persists()
    {
        using var service = CreateService();
        await service.InitializeAsync();

        await service.SetAppearanceAsync(AppearanceMode.Light);

        Assert.Equal(AppearanceMode.Light, _sink.Appearance);
        Assert.Equal(ThemePaletteComposer.ResolveVariant(AppearanceMode.Light, _sink.IsPlatformLight).ToString(),
            ResolveVariantOfAppliedLayer(_sink.LastLayer!));
        Assert.Equal(AppearanceMode.Light, service.Settings.Appearance);
        Assert.Equal(AppearanceMode.Light, new ThemeSettingsStore(_temp.File("theme-settings.json")).Load().Appearance);
        Assert.Equal(2, _changes.Count); // initialize + appearance
    }

    [Fact]
    public async Task Set_appearance_keeps_settings_when_the_sink_rejects_the_switch()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        _changes.Clear();
        _sink.SetAppearanceResult = false;

        await service.SetAppearanceAsync(AppearanceMode.Light);

        Assert.Equal(AppearanceMode.System, service.Settings.Appearance);
        Assert.Equal(AppearanceMode.System, _sink.Appearance);
        Assert.NotNull(service.LastError);
        Assert.Empty(_changes);
    }

    [Fact]
    public async Task Set_appearance_restores_the_previous_state_when_the_palette_swap_fails()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        _changes.Clear();
        _sink.ApplyThemeLayerResult = false;
        _sink.RevertResult = false;

        await service.SetAppearanceAsync(AppearanceMode.Light);

        Assert.Equal(AppearanceMode.System, service.Settings.Appearance);
        Assert.Equal(AppearanceMode.System, _sink.Appearance);
        Assert.NotNull(service.LastError);
        Assert.Empty(_changes);
    }

    [Fact]
    public async Task Set_contrast_delegates_and_persists()
    {
        using var service = CreateService();
        await service.InitializeAsync();

        await service.SetContrastAsync(ContrastMode.High);

        Assert.Equal(ContrastMode.High, _sink.Contrast);
        Assert.Equal(ContrastMode.High, service.Settings.Contrast);
        Assert.Equal(ContrastMode.High, new ThemeSettingsStore(_temp.File("theme-settings.json")).Load().Contrast);
    }

    [Fact]
    public async Task Set_contrast_failure_keeps_settings()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        _sink.SetContrastResult = false;

        await service.SetContrastAsync(ContrastMode.High);

        Assert.Equal(ContrastMode.Standard, service.Settings.Contrast);
        Assert.NotNull(service.LastError);
    }

    [Fact]
    public async Task Set_reduced_motion_delegates_and_persists()
    {
        using var service = CreateService();
        await service.InitializeAsync();

        await service.SetReducedMotionAsync(enabled: true);

        Assert.True(_sink.ReducedMotion);
        Assert.True(service.Settings.ReducedMotion);
        Assert.True(new ThemeSettingsStore(_temp.File("theme-settings.json")).Load().ReducedMotion);
    }

    [Fact]
    public async Task Set_reduced_motion_failure_keeps_settings()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        _sink.SetReducedMotionResult = false;

        await service.SetReducedMotionAsync(enabled: true);

        Assert.False(service.Settings.ReducedMotion);
        Assert.NotNull(service.LastError);
    }

    [Fact]
    public async Task Set_layout_persists_without_touching_the_layer_sink()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        var applyCount = _sink.ApplyCount;
        var layout = LayoutProfile.Default with
        {
            Shelf = ShelfLayout.List,
            Density = Density.Compact,
            Workbench = WorkbenchLayout.Split,
        };

        await service.SetLayoutAsync(layout);

        Assert.Equal(layout, service.Settings.Layout);
        Assert.Equal(applyCount, _sink.ApplyCount);
        Assert.Equal(layout, new ThemeSettingsStore(_temp.File("theme-settings.json")).Load().Layout);
    }

    [Fact]
    public async Task Reset_restores_every_setting_and_the_default_theme()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        await service.ApplyAsync("ocean");
        await service.SetAppearanceAsync(AppearanceMode.Light);
        await service.SetContrastAsync(ContrastMode.High);
        await service.SetReducedMotionAsync(enabled: true);
        await service.SetLayoutAsync(LayoutProfile.Default with { Shelf = ShelfLayout.Masonry });

        await service.ResetToDefaultAsync();

        Assert.Equal(ThemeDefaults.Settings, service.Settings);
        Assert.Equal(ThemeDefaults.DefaultThemeId, _sink.LastAppliedThemeId);
        Assert.Equal(AppearanceMode.System, _sink.Appearance);
        Assert.Equal(ContrastMode.Standard, _sink.Contrast);
        Assert.False(_sink.ReducedMotion);
        Assert.Equal(ThemeDefaults.Settings, new ThemeSettingsStore(_temp.File("theme-settings.json")).Load());
    }

    [Fact]
    public async Task Save_failure_is_recorded_but_the_theme_stays_applied()
    {
        var persistence = new FailingSavePersistence();
        using var service = CreateService(_registry, persistence, _sink);
        await service.InitializeAsync();

        var result = await service.ApplyAsync("ocean");

        Assert.True(result.Success);
        Assert.Equal("ocean", service.Settings.ThemeId);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.SettingsIoFailed);
        Assert.NotNull(service.LastError);
        Assert.Equal(1, persistence.SaveCount);
    }

    [Fact]
    public async Task Preview_updates_apply_live_but_only_commit_plus_apply_persists()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        var appliedThemeId = service.Settings.ThemeId;

        var session = service.PreviewEngine.Begin();
        session.Update("ocean");

        Assert.Equal("ocean", _sink.LastAppliedThemeId);
        Assert.Equal(appliedThemeId, service.Settings.ThemeId);

        session.Cancel();
        Assert.Equal(appliedThemeId, _sink.LastAppliedThemeId);
        Assert.Equal(appliedThemeId, service.Settings.ThemeId);

        var second = service.PreviewEngine.Begin();
        second.Update("ocean");
        second.Commit();
        await service.ApplyAsync("ocean");

        Assert.Equal("ocean", service.Settings.ThemeId);
        Assert.Equal("ocean", new ThemeSettingsStore(_temp.File("theme-settings.json")).Load().ThemeId);
        second.Dispose();
    }

    [Fact]
    public async Task Platform_theme_change_recomposes_the_palette_while_following_the_system()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        Assert.Equal(AppearanceMode.System, service.Settings.Appearance);
        Assert.Equal(ExpectedColor(PaletteVariant.Dark, "Nm.Color.Bg.Canvas"), ColorOf(_sink.LastLayer!, "Nm.Color.Bg.Canvas"));

        _sink.IsPlatformLight = true;
        _sink.RaisePlatformThemeChanged();

        Assert.Equal(ExpectedColor(PaletteVariant.Light, "Nm.Color.Bg.Canvas"), ColorOf(_sink.LastLayer!, "Nm.Color.Bg.Canvas"));
        Assert.Equal(AppearanceMode.System, service.Settings.Appearance);
    }

    [Fact]
    public async Task Platform_theme_change_is_ignored_for_an_explicit_appearance()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        await service.SetAppearanceAsync(AppearanceMode.Dark);
        var applyCount = _sink.ApplyCount;

        _sink.IsPlatformLight = true;
        _sink.RaisePlatformThemeChanged();

        Assert.Equal(applyCount, _sink.ApplyCount);
    }

    [Fact]
    public async Task Apply_while_a_preview_session_is_active_cancels_the_session_instead_of_throwing()
    {
        using var service = CreateService();
        await service.InitializeAsync();
        var session = service.PreviewEngine.Begin();
        session.Update("ocean");

        var result = await service.ApplyAsync(ThemeDefaults.DefaultThemeId);

        Assert.True(result.Success);
        Assert.Null(service.PreviewEngine.ActiveSession);
        Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
        session.Dispose();
    }

    [Fact]
    public async Task Dispose_detaches_from_the_preview_engine()
    {
        var service = CreateService();
        await service.InitializeAsync();
        service.Dispose();

        var applyCount = _sink.ApplyCount;
        service.PreviewEngine.Begin().Update("ocean");

        Assert.Equal(applyCount, _sink.ApplyCount);
    }

    private static string ResolveVariantOfAppliedLayer(IReadOnlyDictionary<string, object?> layer)
    {
        // Light and dark palettes differ on the canvas background; report which one was applied.
        var light = ThemePaletteComposer.Compose(ThemeFixtures.DefaultPackage, PaletteVariant.Light);
        var dark = ThemePaletteComposer.Compose(ThemeFixtures.DefaultPackage, PaletteVariant.Dark);
        var actual = ColorOf(layer, "Nm.Color.Bg.Canvas");
        if (actual == ColorOf(light, "Nm.Color.Bg.Canvas"))
        {
            return PaletteVariant.Light.ToString();
        }

        if (actual == ColorOf(dark, "Nm.Color.Bg.Canvas"))
        {
            return PaletteVariant.Dark.ToString();
        }

        return PaletteVariant.Dark.ToString();
    }

    private static Avalonia.Media.Color ExpectedColor(PaletteVariant variant, string key) =>
        ColorOf(ThemePaletteComposer.Compose(ThemeFixtures.DefaultPackage, variant), key);

    private static Avalonia.Media.Color ColorOf(IReadOnlyDictionary<string, object?> layer, string key) =>
        Assert.IsAssignableFrom<ISolidColorBrush>(layer[key]).Color;
}
