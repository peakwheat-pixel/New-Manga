using System;
using System.Collections.Generic;
using NewManga.Appearance;

namespace NewManga.App.Services;

/// <summary>
/// C-03 §2.5 / FEA-06-PREREQ-1 AC2: the appearance coordinator. It owns reading,
/// validating and broadcasting the persisted appearance settings. Applying the
/// theme / motion to the visual tree is the shell's job (FEA-06-PREREQ-2), so this
/// type deliberately never touches resources — it is the seam between the writer
/// (<see cref="AppearanceStore"/>) and the shell.
/// </summary>
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
}
