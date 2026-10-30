using NewManga.App;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.ThemeEngine;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-E2E-1 (FOLLOW-UP-E2E-1): <c>--theme-home</c> moves the whole theme subsystem (settings, user
/// themes, favorites) to one directory, while the default run keeps the shipped
/// <c>%APPDATA%/NewManga</c> location untouched.
/// </summary>
public sealed class ThemeHomeTests : IDisposable
{
    private readonly string _root;

    public ThemeHomeTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-e2e1-themehome-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        try { Directory.Delete(_root, recursive: true); } catch { /* best effort temp cleanup */ }
    }

    [Fact]
    public void NoOverride_KeepsShippedRoamingPaths()
    {
        var paths = ThemeHome.Resolve((string?)null);

        Assert.False(paths.IsCustom);
        Assert.Equal(ThemeSettingsStore.DefaultSettingsFilePath, paths.SettingsFilePath);
        Assert.Equal(ThemeRegistry.DefaultUserThemeDirectory, paths.ThemesDirectory);
        Assert.Equal(
            Path.Combine(ThemeSettingsStore.DefaultDirectory, ThemeHome.FavoritesFileName),
            paths.FavoritesFilePath);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("\t")]
    public void BlankOverride_KeepsShippedPaths(string themeHome)
    {
        var paths = ThemeHome.Resolve(themeHome);

        Assert.False(paths.IsCustom);
        Assert.Equal(ThemeSettingsStore.DefaultSettingsFilePath, paths.SettingsFilePath);
    }

    [Fact]
    public void EqualsAndSpaceForms_ResolveIdentically()
    {
        var home = Path.Combine(_root, "theme home with spaces");
        var equalsForm = AppOptions.Parse([$"--theme-home={home}"]);
        var spaceForm = AppOptions.Parse(["--theme-home", home]);

        Assert.Null(equalsForm.InvalidReason);
        Assert.Null(spaceForm.InvalidReason);
        Assert.Equal(ThemeHome.Resolve(equalsForm), ThemeHome.Resolve(spaceForm));
        Assert.True(ThemeHome.Resolve(equalsForm).IsCustom);
    }

    [Fact]
    public void CustomRoot_WithSpaces_MapsAllThreePaths()
    {
        var home = Path.Combine(_root, "theme home with spaces");
        var options = AppOptions.Parse(["--theme-home", home]);
        var paths = ThemeHome.Resolve(options);

        Assert.True(paths.IsCustom);
        Assert.Equal(Path.Combine(home, "theme-settings.json"), paths.SettingsFilePath);
        Assert.Equal(Path.Combine(home, "themes"), paths.ThemesDirectory);
        Assert.Equal(Path.Combine(home, "theme-studio-favorites.json"), paths.FavoritesFilePath);
    }

    [Fact]
    public void RelativeOverride_IsResolvedToAnAbsoluteRoot()
    {
        var paths = ThemeHome.Resolve("relative-theme-home");

        Assert.True(paths.IsCustom);
        Assert.True(Path.IsPathFullyQualified(paths.SettingsFilePath));
        Assert.EndsWith("theme-settings.json", paths.SettingsFilePath, StringComparison.Ordinal);
    }

    [Fact]
    public void EmptyValue_IsRejectedByTheParser()
    {
        var options = AppOptions.Parse(["--theme-home="]);

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--theme-home", options.InvalidReason, StringComparison.Ordinal);
        Assert.Contains("non-empty", options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public void WhitespaceValue_IsRejectedByTheParser()
    {
        var options = AppOptions.Parse(["--theme-home", "   "]);

        Assert.NotNull(options.InvalidReason);
        Assert.Contains("--theme-home", options.InvalidReason, StringComparison.Ordinal);
    }

    [Fact]
    public async Task SettingsStore_WritesOnlyTheCustomThemeHome_DefaultPathUntouched()
    {
        var home = Path.Combine(_root, "isolated");
        var paths = ThemeHome.Resolve(AppOptions.Parse([$"--theme-home={home}"]));

        var defaultSettings = new FileInfo(ThemeSettingsStore.DefaultSettingsFilePath);
        var defaultExistedBefore = defaultSettings.Exists;
        var defaultWriteBefore = defaultSettings.Exists ? defaultSettings.LastWriteTimeUtc : (DateTime?)null;

        var registry = new ThemeRegistry(paths.ThemesDirectory);
        Assert.Equal(paths.ThemesDirectory, registry.UserThemeDirectory);

        var store = new ThemeSettingsStore(paths.SettingsFilePath, registry);
        Assert.Equal(Path.GetFullPath(paths.SettingsFilePath), store.SettingsFilePath);

        var light = new ThemeSettings(
            ThemeDefaults.DefaultThemeId,
            AppearanceMode.Light,
            ContrastMode.Standard,
            LayoutProfile.Default,
            ReducedMotion: false,
            FollowSystemAccent: false);
        await store.SaveAsync(light);

        Assert.True(File.Exists(paths.SettingsFilePath), $"expected settings at {paths.SettingsFilePath}");
        var written = ThemeSettingsJson.Read(File.ReadAllText(paths.SettingsFilePath));
        Assert.Equal(AppearanceMode.Light, written.Settings.Appearance);
        Assert.Equal(light, store.Load());

        // The real user settings document must not be created or modified by this test.
        var defaultSettingsAfter = new FileInfo(ThemeSettingsStore.DefaultSettingsFilePath);
        Assert.Equal(defaultExistedBefore, defaultSettingsAfter.Exists);
        if (defaultExistedBefore)
        {
            Assert.Equal(defaultWriteBefore, defaultSettingsAfter.LastWriteTimeUtc);
        }
    }

    [Fact]
    public void FavoritesStore_WritesOnlyTheCustomThemeHome()
    {
        var home = Path.Combine(_root, "isolated-favorites");
        var paths = ThemeHome.Resolve(AppOptions.Parse(["--theme-home", home]));
        Directory.CreateDirectory(home);

        var defaultFavorites = Path.Combine(ThemeSettingsStore.DefaultDirectory, ThemeHome.FavoritesFileName);
        var defaultExistedBefore = File.Exists(defaultFavorites);
        var defaultWriteBefore = defaultExistedBefore ? File.GetLastWriteTimeUtc(defaultFavorites) : (DateTime?)null;

        var store = new ThemeStudioFavoritesStore(paths.FavoritesFilePath);
        Assert.Equal(Path.GetFullPath(paths.FavoritesFilePath), store.FilePath);
        Assert.True(store.Save(new HashSet<string>(StringComparer.Ordinal) { ThemeDefaults.DefaultThemeId }));

        Assert.True(File.Exists(paths.FavoritesFilePath));
        Assert.Contains(ThemeDefaults.DefaultThemeId, store.Load());
        Assert.Equal(defaultExistedBefore, File.Exists(defaultFavorites));
        if (defaultExistedBefore)
        {
            Assert.Equal(defaultWriteBefore, File.GetLastWriteTimeUtc(defaultFavorites));
        }
    }
}

