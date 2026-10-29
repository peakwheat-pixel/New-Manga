using NewManga.App.Services;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// C-3-I1: the retired <c>--theme</c> argument keeps its visual intent through the migration table
/// (appearance and compact density), while an explicit <c>--variant</c> always wins.
/// </summary>
public sealed class LegacyStartupThemeTests
{
    [Fact]
    public void Saber_light_maps_to_the_light_appearance()
    {
        var resolved = LegacyStartupTheme.Resolve("saber-light", null);
        Assert.Equal(AppearanceMode.Light, resolved.Appearance);
        Assert.Null(resolved.Density);
    }

    [Fact]
    public void Dark_pack_maps_to_the_dark_appearance()
    {
        var resolved = LegacyStartupTheme.Resolve("saber-purple", null);
        Assert.Equal(AppearanceMode.Dark, resolved.Appearance);
    }

    [Fact]
    public void Explicit_variant_wins_over_the_theme_appearance()
    {
        var resolved = LegacyStartupTheme.Resolve("saber-light", "dark");
        Assert.Equal(AppearanceMode.Dark, resolved.Appearance);
    }

    [Fact]
    public void Launchpad_pack_keeps_its_compact_density()
    {
        var resolved = LegacyStartupTheme.Resolve("macos-launchpad", null);
        Assert.Null(resolved.Appearance);
        Assert.Equal(DensityMode.Compact, resolved.Density);
    }

    [Fact]
    public void Default_id_keeps_the_requested_appearance_and_unknown_recovers_dark()
    {
        Assert.Null(LegacyStartupTheme.Resolve("newmanga-default", null).Appearance);
        Assert.Null(LegacyStartupTheme.Resolve(null, null).Appearance);
        // LegacyThemeMigration treats an unknown installed theme as a dark recovery (warning, not crash).
        Assert.Equal(AppearanceMode.Dark, LegacyStartupTheme.Resolve("unknown-theme", null).Appearance);
    }
}

