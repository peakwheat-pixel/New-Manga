using NewManga.DesignSystem.Theming;
using NewManga.ThemeEngine;
using DesignSystemAppearance = NewManga.DesignSystem.Theming.AppearanceMode;
using DesignSystemDensity = NewManga.DesignSystem.Theming.DensityMode;

namespace NewManga.App.Services;

/// <summary>
/// C-3-I1: startup compatibility for the retired <c>--theme</c> argument. The migration table already
/// maps every retired pack id to <c>newmanga-default</c>; this helper also carries the appearance and
/// density that the old pack implied (e.g. <c>saber-light</c>) into the DesignSystem manager, so the
/// legacy argument no longer silently loses its visual intent. An explicit <c>--variant</c> always wins.
/// </summary>
public sealed record LegacyStartupTheme(DesignSystemAppearance? Appearance, DesignSystemDensity? Density)
{
    public static LegacyStartupTheme Resolve(string? themeId, string? variant)
    {
        var appearance = ParseVariant(variant);
        DesignSystemDensity? density = null;

        if (!string.IsNullOrWhiteSpace(themeId))
        {
            var legacySettings = new ThemeSettings(
                themeId!,
                ThemeEngine.AppearanceMode.System,
                NewManga.ThemeEngine.ContrastMode.Standard,
                LayoutProfile.Default,
                ReducedMotion: false,
                FollowSystemAccent: false);
            var migrated = LegacyThemeMigration.Migrate(legacySettings, _ => false);
            System.Diagnostics.Trace.TraceInformation(
                $"--theme={themeId} mapped to {migrated.Settings.ThemeId} " +
                $"(appearance={migrated.Settings.Appearance}, density={migrated.Settings.Layout.Density})");

            appearance ??= migrated.Settings.Appearance switch
            {
                ThemeEngine.AppearanceMode.Dark => DesignSystemAppearance.Dark,
                ThemeEngine.AppearanceMode.Light => DesignSystemAppearance.Light,
                _ => null,
            };
            density = migrated.Settings.Layout.Density switch
            {
                ThemeEngine.Density.Compact => DesignSystemDensity.Compact,
                ThemeEngine.Density.Spacious => DesignSystemDensity.Spacious,
                _ => null,
            };
        }

        return new LegacyStartupTheme(appearance, density);
    }

    private static DesignSystemAppearance? ParseVariant(string? variant) =>
        string.IsNullOrWhiteSpace(variant)
            ? null
            : string.Equals(variant, "dark", StringComparison.OrdinalIgnoreCase)
                ? DesignSystemAppearance.Dark
                : DesignSystemAppearance.Light;
}


