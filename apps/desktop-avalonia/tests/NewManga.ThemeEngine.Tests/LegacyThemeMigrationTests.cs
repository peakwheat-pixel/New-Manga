using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Retirement-plan §2.1 migration (9 retired ids + unknown + empty), legacy settings recovery and the
/// persistence round-trip. Persistence must never throw for a corrupt file and must not block startup.
/// </summary>
public sealed class LegacyThemeMigrationTests
{
    private static ThemeSettings Settings(
        string themeId,
        AppearanceMode appearance = AppearanceMode.System,
        Density density = Density.Comfortable) =>
        ThemeDefaults.Settings with
        {
            ThemeId = themeId,
            Appearance = appearance,
            Layout = LayoutProfile.Default with { Density = density },
        };

    [Theory]
    [InlineData("saber-purple", AppearanceMode.Dark)]
    [InlineData("saber-light", AppearanceMode.Light)]
    [InlineData("midnight", AppearanceMode.Dark)]
    [InlineData("sakura", AppearanceMode.Light)]
    [InlineData("emerald", AppearanceMode.Dark)]
    [InlineData("mono", AppearanceMode.Dark)]
    public void Preset_theme_ids_map_to_the_default_theme_and_the_planned_appearance(
        string legacyId,
        AppearanceMode expectedAppearance)
    {
        var result = LegacyThemeMigration.Migrate(Settings(legacyId, AppearanceMode.System));

        Assert.Equal(ThemeDefaults.DefaultThemeId, result.Settings.ThemeId);
        Assert.Equal(expectedAppearance, result.Settings.Appearance);
        Assert.True(result.Changed);
        Assert.Contains(result.Issues, issue =>
            issue.Code == ThemeIssueCodes.SettingsLegacyThemeId && issue.Severity == "warning");
    }

    [Theory]
    [InlineData("macos-sonoma")]
    [InlineData("macos-split")]
    public void Macos_layout_packs_keep_the_configured_appearance(string legacyId)
    {
        var result = LegacyThemeMigration.Migrate(Settings(legacyId, AppearanceMode.Light));

        Assert.Equal(ThemeDefaults.DefaultThemeId, result.Settings.ThemeId);
        Assert.Equal(AppearanceMode.Light, result.Settings.Appearance);
        Assert.Equal(Density.Comfortable, result.Settings.Layout.Density);
        Assert.True(result.Changed);
    }

    [Fact]
    public void Macos_launchpad_keeps_the_appearance_and_maps_the_shelf_density_to_compact()
    {
        var result = LegacyThemeMigration.Migrate(Settings("macos-launchpad", AppearanceMode.Dark));

        Assert.Equal(ThemeDefaults.DefaultThemeId, result.Settings.ThemeId);
        Assert.Equal(AppearanceMode.Dark, result.Settings.Appearance);
        Assert.Equal(Density.Compact, result.Settings.Layout.Density);
        Assert.True(result.Changed);
    }

    [Fact]
    public void Macos_launchpad_does_not_override_an_explicit_user_density()
    {
        var result = LegacyThemeMigration.Migrate(
            Settings("macos-launchpad", AppearanceMode.Dark, Density.Spacious));

        Assert.Equal(Density.Spacious, result.Settings.Layout.Density);
    }

    [Fact]
    public void Unknown_theme_id_recovers_to_the_default_theme_with_dark_appearance()
    {
        var result = LegacyThemeMigration.Migrate(Settings("no-such-theme"), isKnownTheme: _ => false);

        Assert.Equal(ThemeDefaults.DefaultThemeId, result.Settings.ThemeId);
        Assert.Equal(AppearanceMode.Dark, result.Settings.Appearance);
        Assert.True(result.Changed);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.SettingsUnknownThemeId);
    }

    [Fact]
    public void Installed_user_theme_id_is_preserved()
    {
        var result = LegacyThemeMigration.Migrate(Settings("ocean"), isKnownTheme: id => id == "ocean");

        Assert.Equal("ocean", result.Settings.ThemeId);
        Assert.False(result.Changed);
        Assert.Empty(result.Issues);
    }

    [Fact]
    public void Empty_theme_id_lands_on_the_default_theme_without_a_warning()
    {
        var result = LegacyThemeMigration.Migrate(Settings(string.Empty, AppearanceMode.Light));

        Assert.Equal(ThemeDefaults.DefaultThemeId, result.Settings.ThemeId);
        Assert.Equal(AppearanceMode.Light, result.Settings.Appearance);
        Assert.True(result.Changed);
        Assert.Empty(result.Issues);
    }

    [Fact]
    public void Legacy_default_alias_is_normalized_to_the_shipped_id()
    {
        var result = LegacyThemeMigration.Migrate(Settings("NewManga.Default"));

        Assert.Equal(ThemeDefaults.DefaultThemeId, result.Settings.ThemeId);
        Assert.True(result.Changed);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.SettingsLegacyThemeId);
    }

    [Fact]
    public async Task Settings_round_trip_through_the_store()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        var store = new ThemeSettingsStore(path);
        var settings = new ThemeSettings(
            ThemeDefaults.DefaultThemeId,
            AppearanceMode.Dark,
            ContrastMode.High,
            LayoutProfile.Default with { Shelf = ShelfLayout.List, Density = Density.Compact },
            ReducedMotion: true,
            FollowSystemAccent: true);

        await store.SaveAsync(settings);
        var loaded = store.Load();

        Assert.Equal(settings, loaded);
        Assert.Empty(store.LastLoadIssues);
        Assert.False(store.NeedsSave);
    }

    [Fact]
    public void Missing_settings_file_returns_shipped_defaults_without_issues()
    {
        using var temp = new TempDirectory();
        var store = new ThemeSettingsStore(temp.File("theme-settings.json"));

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.Settings, loaded);
        Assert.Empty(store.LastLoadIssues);
        Assert.False(store.NeedsSave);
    }

    [Fact]
    public void Corrupt_settings_file_falls_back_to_defaults_without_throwing()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, "{ this is not json");
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.Settings, loaded);
        Assert.Contains(store.LastLoadIssues, issue => issue.Code == ThemeIssueCodes.SettingsJsonInvalid);
    }

    [Fact]
    public void Legacy_theme_key_and_variant_alias_are_read_and_migrated()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, """
            {
              "theme": "sakura",
              "variant": "dark"
            }
            """);
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        Assert.Equal(AppearanceMode.Light, loaded.Appearance);
        Assert.True(store.NeedsSave);
        Assert.Contains(store.LastLoadIssues, issue => issue.Code == ThemeIssueCodes.SettingsLegacyThemeId);
    }

    [Fact]
    public void Unknown_theme_id_is_recovered_when_a_registry_is_available()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.File("themes"));
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, """{ "themeId": "ghost-theme" }""");
        var store = new ThemeSettingsStore(path, registry);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        Assert.Equal(AppearanceMode.Dark, loaded.Appearance);
        Assert.Contains(store.LastLoadIssues, issue => issue.Code == ThemeIssueCodes.SettingsUnknownThemeId);
    }

    [Fact]
    public void Invalid_setting_values_fall_back_field_by_field_with_warnings()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, """
            {
              "schema": "newmanga.theme-settings/1",
              "themeId": "newmanga-default",
              "appearance": 42,
              "contrast": "ultra",
              "layout": { "density": "giant" },
              "reducedMotion": "yes"
            }
            """);
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        Assert.Equal(AppearanceMode.System, loaded.Appearance);
        Assert.Equal(ContrastMode.Standard, loaded.Contrast);
        Assert.Equal(Density.Comfortable, loaded.Layout.Density);
        Assert.False(loaded.ReducedMotion);
        Assert.Contains(store.LastLoadIssues, issue => issue.Code == ThemeIssueCodes.SettingsInvalidValue);
    }
}
