using NewManga.DesignSystem;
using NewManga.DesignSystem.Theming;

namespace NewManga.ThemeEngine;

/// <summary>
/// The resource-key sets the Theme Engine is allowed to publish (contract §2.2 / §4.1, R-15/R-21).
/// The design system is the single authority: the required palette set comes from
/// <see cref="DesignSystemThemeManager.PaletteColorKeys"/> and the 59-key theme-layer whitelist from
/// <see cref="DesignSystemThemeManager.ThemeLayerRequiredKeys"/>. Theme-invariant derived colors
/// (<c>Nm.Color.Scrim</c>, the Modal scrim) live in the global token dictionary, are excluded from every
/// appearance palette and therefore never belong to a theme package.
/// </summary>
public static class ThemeTokenKeys
{
    /// <summary>Prefix every theme-engine resource key starts with.</summary>
    public const string Prefix = "Nm.";

    /// <summary>Prefix of the color layer a theme package owns.</summary>
    public const string ColorPrefix = "Nm.Color.";

    /// <summary>
    /// The 35 palette color keys a theme token set must define (background 6, line 4, text 5, accent 6,
    /// status 7, status-muted 7). Authoritative source: DS <c>PaletteColorKeys</c>, which excludes
    /// theme-invariant derived colors such as <c>Nm.Color.Scrim</c>.
    /// </summary>
    public static IReadOnlyList<string> Colors { get; } = DesignSystemThemeManager.PaletteColorKeys;

    /// <summary>
    /// Theme-invariant derived colors: published by the design system's global token dictionary
    /// (alongside <c>Nm.Space.*</c>), never part of an appearance palette and never validated as a
    /// theme-package requirement (R-21).
    /// </summary>
    public static IReadOnlyList<string> ThemeInvariantColorKeys { get; } = [NmKeys.Color.Scrim];

    /// <summary>Motion-duration keys owned by a theme (R-15: fast/normal/slow; instant is theme-invariant).</summary>
    public static IReadOnlyList<string> MotionDurations { get; } =
    [
        NmKeys.Motion.Duration.Fast,
        NmKeys.Motion.Duration.Normal,
        NmKeys.Motion.Duration.Slow,
    ];

    /// <summary>
    /// The exact 59 keys a theme layer must define (R-15): 35 colors + 3 font families + 6 font sizes
    /// + 9 line heights + 3 corner radii + 3 motion durations. Authoritative source: DS
    /// <c>ThemeLayerRequiredKeys</c> — the palette composer output and the seam whitelist must agree.
    /// </summary>
    public static IReadOnlyList<string> ThemeLayer { get; } = DesignSystemThemeManager.ThemeLayerRequiredKeys;

    /// <summary>Every resource key the design system publishes, as a set for conformance tests.</summary>
    public static IReadOnlySet<string> Published { get; } =
        new HashSet<string>(NmKeys.All, StringComparer.Ordinal);

    /// <summary>True when the key is part of the 59-key theme layer whitelist.</summary>
    public static bool IsThemeLayerKey(string key) => ThemeLayer.Contains(key, StringComparer.Ordinal);
}
