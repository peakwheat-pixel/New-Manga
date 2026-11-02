using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace NewManga.Appearance;

/// <summary>
/// C-03 §2.1: the appearance coordinator — the <b>single writer</b> of the persisted appearance
/// document (<c>presentation-settings.json</c>). It owns reading, validating, writing and broadcasting
/// the settings; applying the theme / motion to the visual tree is the shell's job (FEA-06), so this
/// type deliberately never touches resources — it is the seam between the writer
/// (<see cref="AppearanceStore"/>) and the shell.
/// </summary>
/// <remarks>
/// FEA-06-PREREQ-2 P5 / W-10 resolves the PREREQ-1 deviation D-1: the coordinator now lives in
/// <c>NewManga.Appearance</c> (C-03 §2.1) and owns <see cref="SaveAsync"/>, so the app layer only calls
/// into this class and the Theme Engine never writes the new document (its compatibility write goes
/// through an app-provided <c>IThemeSettingsSink</c> adapter).
/// </remarks>
public sealed class AppearanceCoordinator
{
    private readonly AppearanceStore _store;

    public AppearanceCoordinator(AppearanceStore store)
    {
        ArgumentNullException.ThrowIfNull(store);
        _store = store;
    }

    /// <summary>Raised after <see cref="Reload"/> produced a different settings object.</summary>
    public event EventHandler? Changed;

    /// <summary>The current settings (shipped defaults until the first load).</summary>
    public AppearanceSettings Settings { get; private set; } = AppearanceDefaults.Settings;

    /// <summary>Warnings produced by the last load (never blocks startup).</summary>
    public IReadOnlyList<string> Warnings { get; private set; } = Array.Empty<string>();

    /// <summary>The <c>theme.frontendId</c> the shell must start (fail-safe default).</summary>
    public string FrontendId => Settings.FrontendId;

    /// <summary>
    /// Reads the document, falls back field-by-field on a broken file and raises
    /// <see cref="Changed"/> only when the resulting settings differ.
    /// </summary>
    public AppearanceSettings Reload()
    {
        var read = _store.Read();
        var next = read.Settings;
        var changed = !Equals(next, Settings);
        Settings = next;
        Warnings = read.Warnings;
        if (changed)
        {
            Changed?.Invoke(this, EventArgs.Empty);
        }

        return next;
    }

    /// <summary>
    /// Persists the document atomically (temp + replace) and updates <see cref="Settings"/> before
    /// raising <see cref="Changed"/>. This is the only production write path of
    /// <c>presentation-settings.json</c> (C-03 §2.1 唯一写者).
    /// </summary>
    public async Task SaveAsync(AppearanceSettings settings, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(settings);

        await _store.WriteAsync(settings, cancellationToken).ConfigureAwait(false);

        var changed = !Equals(Settings, settings);
        Settings = settings;
        if (changed)
        {
            Changed?.Invoke(this, EventArgs.Empty);
        }
    }
}
