namespace NewManga.ThemeEngine;

/// <summary>
/// Boundary between <see cref="ThemeService"/> and the running application surface (Avalonia resources
/// + DesignSystem theme manager). The service owns theme semantics (which theme, which appearance,
/// persistence, fallback); the sink owns the irreversible part — swapping dictionaries on a live
/// application without rebuilding the window (contract §4 behavior 1).
/// <para>
/// Part B adapter (once the design system exposes <c>ApplyThemeLayer(ResourceDictionary, string)</c>):
/// convert the composed <c>Nm.*</c> layer to a <c>ResourceDictionary</c>, call the seam, and delegate
/// appearance/contrast/reduced-motion to the existing <c>DesignSystemThemeManager</c> methods — a few
/// lines. The interface stays Avalonia-free so the service is unit-testable without an
/// <c>Application</c> instance.
/// </para>
/// </summary>
public interface IThemeLayerSink
{
    /// <summary>True when the platform currently reports a light theme (used to resolve <see cref="AppearanceMode.System"/>).</summary>
    bool IsPlatformLight { get; }

    /// <summary>
    /// Applies the composed theme layer (<see cref="ThemePaletteComposer"/> output) to the application.
    /// Must replace only the theme layer and keep layout/density/high-contrast semantics; returns false
    /// and leaves the previous layer intact on failure.
    /// </summary>
    bool ApplyThemeLayer(IReadOnlyDictionary<string, object?> layer, string themeId);

    /// <summary>Restores the design system's shipped built-in layer (final fallback, uninstall, reset).</summary>
    bool RevertToBuiltInLayer();

    /// <summary>Switches light/dark/system appearance; false on failure (previous appearance kept).</summary>
    bool SetAppearance(AppearanceMode mode);

    /// <summary>Switches standard/high contrast; false on failure.</summary>
    bool SetContrast(ContrastMode mode);

    /// <summary>Turns reduced motion on/off; false on failure.</summary>
    bool SetReducedMotion(bool enabled);

    /// <summary>Last sink-level error, or null. The service surfaces it through its own <c>LastError</c>.</summary>
    string? LastError { get; }

    /// <summary>
    /// Raised when the platform light/dark state changes while <see cref="AppearanceMode.System"/> is
    /// active. The service then recomposes the current theme for the new variant (contract §4 behavior 4).
    /// </summary>
    event EventHandler? PlatformThemeChanged;
}
