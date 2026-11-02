namespace NewManga.ThemeEngine;

/// <summary>
/// FEA-06-PREREQ-2 P5 (W-9/Q-32): the Theme Engine's compatibility-write seam to the appearance writer.
///
/// <para>
/// During the one-release compatibility window <see cref="ThemeSettingsStore.SaveAsync"/> keeps writing the
/// legacy <c>theme-settings.json</c> and mirrors the same settings into the canonical
/// <c>presentation-settings.json</c> through this sink. The implementation lives in the app layer
/// (backed by <c>NewManga.Appearance.AppearanceCoordinator</c>) so the engine never references the
/// appearance assembly; this interface stays Avalonia-free and engine-only.
/// </para>
/// </summary>
public interface IThemeSettingsSink
{
    /// <summary>
    /// Mirrors one settings document into the canonical appearance document. Failures propagate as
    /// exceptions; <see cref="ThemeSettingsStore.SaveAsync"/> treats its compatibility write as one unit.
    /// </summary>
    Task WriteAsync(ThemeSettings settings, CancellationToken cancellationToken = default);
}
