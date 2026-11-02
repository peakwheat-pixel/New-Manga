using System;
using System.Collections.Generic;
using NewManga.Appearance;

namespace NewManga.App.Services;

/// <summary>FEA-07 AC4: which shell the composition root starts (after all safe-startup fallbacks).</summary>
public enum StartupShellKind
{
    /// <summary><c>--shell=legacy</c> operator rollback (one release).</summary>
    Legacy = 0,

    /// <summary>The default per-frontend path (Fluent shell or Current V2).</summary>
    Default = 1,

    /// <summary>The stable presentation window with runtime frontend switching (opt-in).</summary>
    PresentationHost = 2,
}

/// <summary>The safe-startup decision: effective frontend, shell kind and human-readable diagnostics.</summary>
public sealed record StartupPlan(
    string RequestedFrontendId,
    string EffectiveFrontendId,
    bool IsFallback,
    StartupShellKind ShellKind,
    IReadOnlyList<string> Diagnostics);

/// <summary>
/// FEA-07 AC4/AC7: decides the startup shell and effective frontend under the fail-safe policy:
/// bad/unknown frontend or a bad appearance document never blocks startup — the selector keeps its
/// frozen Current V2 fallback and the appearance loader keeps its field-by-field fallback; both are
/// surfaced as diagnostics. <c>--shell=legacy</c> still wins over everything.
/// </summary>
public static class SafeStartupPlanner
{
    public static StartupPlan Plan(
        AppOptions options,
        AppearanceSettings settings,
        IReadOnlyList<string> appearanceWarnings)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(settings);
        ArgumentNullException.ThrowIfNull(appearanceWarnings);

        var selection = FrontendSelector.Select(options.FrontendId, settings.FrontendId);
        var diagnostics = new List<string>();
        if (!string.IsNullOrWhiteSpace(selection.Diagnostic))
        {
            diagnostics.Add(selection.Diagnostic);
        }

        if (selection.IsFallback)
        {
            var requested = options.FrontendId ?? settings.FrontendId;
            diagnostics.Add(
                $"frontend fallback: requested '{requested}' is not a frontend id; starting '{selection.EffectiveFrontendId}' (fail-safe)");
        }

        foreach (var warning in appearanceWarnings)
        {
            if (!string.IsNullOrWhiteSpace(warning))
            {
                diagnostics.Add("appearance: " + warning);
            }
        }

        var shellKind = !options.UseV2Shell
            ? StartupShellKind.Legacy
            : options.PresentationHost
                ? StartupShellKind.PresentationHost
                : StartupShellKind.Default;

        return new StartupPlan(
            RequestedFrontendId: options.FrontendId ?? settings.FrontendId,
            EffectiveFrontendId: selection.EffectiveFrontendId,
            IsFallback: selection.IsFallback,
            ShellKind: shellKind,
            Diagnostics: diagnostics);
    }
}
