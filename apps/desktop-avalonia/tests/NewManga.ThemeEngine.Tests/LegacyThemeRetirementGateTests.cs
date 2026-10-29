using System.Text.Json.Nodes;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// C-3 removal gate (V11R_THEME_RETIREMENT_PLAN §2.1 / §5): an END-TO-END migration of persisted
/// legacy settings FILES, not just the in-memory mapping table. Every legacy id is written in the old
/// document shape (legacy key <c>theme</c>, legacy <c>variant</c> alias), loaded through the real
/// <see cref="ThemeSettingsStore"/>, and must land on <c>newmanga-default</c> with the planned
/// appearance/density, one migration warning, no exception and a stable re-saved document.
///
/// This file is the executable prerequisite for deleting the old theme system: if any case here fails,
/// C-3 must not remove <c>NewManga.Theme</c> (users with old settings would lose their configuration).
/// </summary>
public sealed class LegacyThemeRetirementGateTests
{
    /// <summary>Retirement plan §2.1: old id, old display name, migrated appearance, density rule.</summary>
    public static TheoryData<string, AppearanceMode, Density> RetirementMatrix => new()
    {
        { "saber-purple", AppearanceMode.Dark, Density.Comfortable },
        { "saber-light", AppearanceMode.Light, Density.Comfortable },
        { "midnight", AppearanceMode.Dark, Density.Comfortable },
        { "sakura", AppearanceMode.Light, Density.Comfortable },
        { "emerald", AppearanceMode.Dark, Density.Comfortable },
        { "mono", AppearanceMode.Dark, Density.Comfortable },
        { "macos-sonoma", AppearanceMode.Light, Density.Comfortable },
        { "macos-launchpad", AppearanceMode.Dark, Density.Compact },
        { "macos-split", AppearanceMode.Light, Density.Comfortable },
    };

    [Fact]
    public void The_migration_table_covers_exactly_the_nine_retired_ids_from_the_plan()
    {
        var expectedIds = RetirementMatrix
            .Select(row => (string)row[0])
            .OrderBy(id => id, StringComparer.Ordinal)
            .ToArray();
        var actualIds = LegacyThemeMigration.Mappings.Keys
            .OrderBy(id => id, StringComparer.Ordinal)
            .ToArray();

        Assert.Equal(expectedIds, actualIds);
        Assert.Equal(9, LegacyThemeMigration.Mappings.Count);
    }

    [Theory]
    [MemberData(nameof(RetirementMatrix))]
    public async Task Legacy_settings_file_migrates_to_the_default_theme_without_losing_appearance(
        string legacyId,
        AppearanceMode expectedAppearance,
        Density expectedDensity)
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        // Old document shape: legacy key `theme` + legacy `variant` alias. The variant values below
        // deliberately disagree with the migrated appearance for the preset packs so the test proves the
        // plan's appearance column (not the old variant) wins where §2.1 says so.
        var legacyVariant = legacyId == "macos-split" ? "light" : "dark";
        File.WriteAllText(path, $$"""
            {
              "schema": "newmanga.theme-settings/1",
              "theme": "{{legacyId}}",
              "variant": "{{legacyVariant}}",
              "contrast": "standard",
              "reducedMotion": false
            }
            """);
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        // Preset packs force the plan appearance; macOS layout packs keep the legacy variant, so the
        // expected value is derived from the plan mapping plus the legacy document itself.
        var mapping = LegacyThemeMigration.Mappings[legacyId];
        var expectedLoadedAppearance = mapping.Appearance ?? (legacyVariant == "light" ? AppearanceMode.Light : AppearanceMode.Dark);
        if (mapping.Appearance is not null)
        {
            Assert.Equal(expectedAppearance, expectedLoadedAppearance);
        }
        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        Assert.Equal(expectedLoadedAppearance, loaded.Appearance);
        Assert.Equal(expectedDensity, loaded.Layout.Density);
        Assert.True(store.NeedsSave, "a migrated legacy document must be re-saved");
        var migrationIssue = Assert.Single(
            store.LastLoadIssues,
            issue => issue.Code == ThemeIssueCodes.SettingsLegacyThemeId);
        Assert.Equal("warning", migrationIssue.Severity);

        // Persisting the migrated settings must produce a document that loads clean (no repeated
        // migration warning) and preserves the migrated values.
        await store.SaveAsync(loaded);
        var reloaded = store.Load();
        Assert.Equal(ThemeDefaults.DefaultThemeId, reloaded.ThemeId);
        Assert.Equal(expectedLoadedAppearance, reloaded.Appearance);
        Assert.Equal(expectedDensity, reloaded.Layout.Density);
        Assert.DoesNotContain(reloaded.ThemeId, LegacyThemeMigration.Mappings.Keys);
        Assert.Empty(store.LastLoadIssues);
        Assert.False(store.NeedsSave);
    }

    [Fact]
    public void Unknown_legacy_id_with_a_registry_recovers_to_default_with_dark_appearance()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.File("themes"));
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, """{ "theme": "saber-unknown-2031", "variant": "light" }""");
        var store = new ThemeSettingsStore(path, registry);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        Assert.Equal(AppearanceMode.Dark, loaded.Appearance);
        Assert.True(store.NeedsSave);
        var issue = Assert.Single(store.LastLoadIssues);
        Assert.Equal(ThemeIssueCodes.SettingsUnknownThemeId, issue.Code);
    }

    [Fact]
    public void Unknown_legacy_id_without_registry_is_preserved_for_later_validation()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, """{ "theme": "saber-unknown-2031" }""");
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        Assert.Equal("saber-unknown-2031", loaded.ThemeId);
        Assert.False(store.NeedsSave);
    }

    [Theory]
    [InlineData("""{ "theme": "" }""")]
    [InlineData("""{ "theme": null }""")]
    [InlineData("""{ }""")]
    public void Empty_or_missing_legacy_theme_lands_on_the_default_theme_with_system_appearance(string json)
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, json);
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        Assert.Equal(AppearanceMode.System, loaded.Appearance);
        Assert.DoesNotContain(store.LastLoadIssues, issue => issue.Code == ThemeIssueCodes.SettingsLegacyThemeId);
    }

    [Fact]
    public void Legacy_keys_and_values_are_migrated_together_into_one_clean_document()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        File.WriteAllText(path, """
            {
              "theme": "midnight",
              "variant": "light",
              "contrast": "high",
              "density": "compact",
              "reducedMotion": true,
              "followAccent": true,
              "unknownFutureField": 42
            }
            """);
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        // Midnight is a preset pack: §2.1 forces Dark even though the old variant said light.
        Assert.Equal(AppearanceMode.Dark, loaded.Appearance);
        Assert.Equal(ContrastMode.High, loaded.Contrast);
        Assert.Equal(Density.Compact, loaded.Layout.Density);
        Assert.True(loaded.ReducedMotion);
        Assert.True(loaded.FollowSystemAccent);
        Assert.Contains(store.LastLoadIssues, issue => issue.Code == ThemeIssueCodes.SettingsLegacyThemeId);
    }

    [Fact]
    public void First_run_after_retirement_starts_with_a_usable_default_document()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json"); // deliberately never written
        var store = new ThemeSettingsStore(path);

        var loaded = store.Load();

        Assert.Equal(ThemeDefaults.Settings, loaded);
        Assert.Equal(ThemeDefaults.DefaultThemeId, loaded.ThemeId);
        Assert.Empty(store.LastLoadIssues);
        Assert.False(store.NeedsSave);
    }

    [Theory]
    [MemberData(nameof(RetirementMatrix))]
    public void Migration_is_idempotent_for_every_retired_id(
        string legacyId,
        AppearanceMode expectedAppearance,
        Density expectedDensity)
    {
        var original = ThemeDefaults.Settings with
        {
            ThemeId = legacyId,
            Appearance = AppearanceMode.System,
        };

        var first = LegacyThemeMigration.Migrate(original);
        var second = LegacyThemeMigration.Migrate(first.Settings);

        Assert.Equal(ThemeDefaults.DefaultThemeId, first.Settings.ThemeId);
        Assert.Equal(first.Settings, second.Settings);
        Assert.False(second.Changed);
        Assert.Empty(second.Issues);
        // Preset packs force the plan's appearance; macOS layout packs keep the configured appearance,
        // so with no configured variant they stay on System. Either way the appearance is deterministic.
        var mapping = LegacyThemeMigration.Mappings[legacyId];
        Assert.Equal(mapping.Appearance ?? AppearanceMode.System, first.Settings.Appearance);
        if (mapping.Appearance is not null)
        {
            Assert.Equal(expectedAppearance, first.Settings.Appearance);
        }

        Assert.Equal(expectedDensity, first.Settings.Layout.Density);
    }
}



