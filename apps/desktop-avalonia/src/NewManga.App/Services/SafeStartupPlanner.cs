using System;
using System.Collections.Generic;
using System.Linq;
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
    IReadOnlyList<string> Diagnostics,
    FrontendSelection Selection);

/// <summary>
/// FEA-07 AC4/AC7: decides the startup shell and effective frontend under the fail-safe policy. The
/// planner is the composition root's single decision source: an unknown frontend OR any appearance
/// document fallback (unknown visual theme / scale / bad package, surfaced as load warnings) forces the
/// frozen Current V2 fail-safe instead of starting a half-broken Fluent shell. <c>--shell=legacy</c>
/// still wins over everything.
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

        var appearanceFallbacks = appearanceWarnings
            .Where(warning => !string.IsNullOrWhiteSpace(warning))
            .ToArray();
        foreach (var warning in appearanceFallbacks)
        {
            diagnostics.Add("appearance: " + warning);
        }

        var isFallback = selection.IsFallback || appearanceFallbacks.Length > 0;
        if (isFallback)
        {
            var requested = options.FrontendId ?? selection.EffectiveFrontendId;
            var reason = appearanceFallbacks.Length > 0
                ? "appearance document fell back field-by-field"
                : "requested frontend is not a frontend id";
            diagnostics.Add(
                $"startup fallback: {reason}; starting '{FrontendSelector.CurrentV2FrontendId}' (fail-safe)");
        }

        var shellKind = !options.UseV2Shell
            ? StartupShellKind.Legacy
            : options.PresentationHost
                ? StartupShellKind.PresentationHost
                : StartupShellKind.Default;

        var effectiveSelection = isFallback
            ? FrontendSelector.Select(FrontendSelector.CurrentV2FrontendId, persistedFrontendId: null)
            : selection;
        return new StartupPlan(
            RequestedFrontendId: options.FrontendId ?? settings.FrontendId,
            EffectiveFrontendId: effectiveSelection.EffectiveFrontendId,
            IsFallback: isFallback,
            ShellKind: shellKind,
            Diagnostics: diagnostics,
            Selection: effectiveSelection);
    }
}
