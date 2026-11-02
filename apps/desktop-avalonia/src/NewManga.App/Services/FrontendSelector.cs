using System;
using System.Diagnostics;

namespace NewManga.App.Services;

/// <summary>Which product shell the composition root starts (FEA-06-PREREQ-2 W-1).</summary>
public enum FrontendKind
{
    /// <summary>The Current V2 shell (<c>builtin.current-v2</c>) — the fail-safe default.</summary>
    AvaloniaV2,

    /// <summary>The Fluent shell (<c>builtin.fluent</c>, FEA-06 implements the four pages).</summary>
    Fluent,
}

/// <summary>Where the effective <c>theme.frontendId</c> came from (W-2b precedence chain).</summary>
public enum FrontendSource
{
    /// <summary>Explicit <c>--frontend</c> command-line override (highest priority).</summary>
    CommandLine,

    /// <summary>Persisted <c>theme.frontendId</c> from <c>presentation-settings.json</c>.</summary>
    AppearanceSettings,

    /// <summary>Neither source supplied a value: the shipped fail-safe default applies.</summary>
    Default,
}

/// <summary>
/// The decision produced by <see cref="FrontendSelector"/>. <see cref="Diagnostic"/> is always set so a
/// startup log can record why a shell was chosen (AC1 "记录"); <see cref="IsFallback"/> is true when an
/// explicit but unrecognized id was replaced by the fail-safe V2 shell.
/// </summary>
/// <param name="Kind">Shell to start.</param>
/// <param name="EffectiveFrontendId">The frontend id the decision is based on (<c>builtin.current-v2</c> after a fallback).</param>
/// <param name="Source">Which input won the precedence chain.</param>
/// <param name="IsFallback">True when an unknown id was rejected and V2 started instead.</param>
/// <param name="Diagnostic">Human-readable decision record (also emitted as a trace warning on fallback).</param>
public sealed record FrontendSelection(
    FrontendKind Kind,
    string EffectiveFrontendId,
    FrontendSource Source,
    bool IsFallback,
    string Diagnostic)
{
    /// <summary>True when the Fluent shell must host the product.</summary>
    public bool IsFluent => Kind == FrontendKind.Fluent;
}

/// <summary>
/// FEA-06-PREREQ-2 AC1 (W-1 / W-2b): resolves the frontend id to the shell to start.
/// <para>
/// Decision table (ids are the frozen <c>newmanga.frontend/1</c> vocabulary, compared ordinally):
/// <list type="bullet">
///   <item><c>builtin.current-v2</c> → the Current V2 shell;</item>
///   <item><c>builtin.fluent</c> → the Fluent shell;</item>
///   <item>anything else (missing/unknown, including the visual-theme id <c>builtin.fluent-dark</c> mistaken
///   for a frontend id) → V2 + a recorded diagnostic (fail-safe, W-1).</item>
/// </list>
/// <c>builtin.fluent-dark</c> is a <b>visual theme</b> id (<c>theme.visualThemeId</c>); it never participates
/// in frontend selection.
/// </para>
/// </summary>
public static class FrontendSelector
{
    /// <summary>Frozen frontend id of the Current V2 shell (default, fail-safe).</summary>
    public const string CurrentV2FrontendId = "builtin.current-v2";

    /// <summary>Frozen frontend id of the Fluent shell.</summary>
    public const string FluentFrontendId = "builtin.fluent";

    /// <summary>Visual theme id of the Fluent dark package (never a frontend id).</summary>
    public const string FluentDarkVisualThemeId = "builtin.fluent-dark";

    private const string DefaultDiagnostic =
        "theme.frontendId is absent; fail-safe frontend 'builtin.current-v2' (Current V2) selected";

    /// <summary>
    /// Resolves the frontend. <paramref name="commandLineFrontendId"/> is an explicit <c>--frontend</c>
    /// value (highest priority); <paramref name="persistedFrontendId"/> is the persisted
    /// <c>theme.frontendId</c>. Never throws.
    /// </summary>
    public static FrontendSelection Select(string? commandLineFrontendId, string? persistedFrontendId)
    {
        var (candidate, source) = ResolveCandidate(commandLineFrontendId, persistedFrontendId);

        if (candidate is null)
        {
            return new FrontendSelection(
                FrontendKind.AvaloniaV2,
                CurrentV2FrontendId,
                FrontendSource.Default,
                IsFallback: false,
                DefaultDiagnostic);
        }

        if (string.Equals(candidate, FluentFrontendId, StringComparison.Ordinal))
        {
            return new FrontendSelection(
                FrontendKind.Fluent,
                FluentFrontendId,
                source,
                IsFallback: false,
                $"theme.frontendId '{FluentFrontendId}' ({Describe(source)}) selects the Fluent shell");
        }

        if (string.Equals(candidate, CurrentV2FrontendId, StringComparison.Ordinal))
        {
            return new FrontendSelection(
                FrontendKind.AvaloniaV2,
                CurrentV2FrontendId,
                source,
                IsFallback: false,
                $"theme.frontendId '{CurrentV2FrontendId}' ({Describe(source)}) selects the Current V2 shell");
        }

        var reason = string.Equals(candidate, FluentDarkVisualThemeId, StringComparison.Ordinal)
            ? $"'{FluentDarkVisualThemeId}' is a visual theme id (theme.visualThemeId), not a frontend id"
            : $"unknown frontend id '{candidate}'";
        var diagnostic =
            $"{reason}; {Describe(source)} supplied it and the fail-safe frontend '{CurrentV2FrontendId}' " +
            "(Current V2) was selected instead";
        Trace.TraceWarning("FrontendSelector: " + diagnostic);

        return new FrontendSelection(
            FrontendKind.AvaloniaV2,
            CurrentV2FrontendId,
            source,
            IsFallback: true,
            diagnostic);
    }

    private static (string? Candidate, FrontendSource Source) ResolveCandidate(
        string? commandLineFrontendId,
        string? persistedFrontendId)
    {
        if (!string.IsNullOrWhiteSpace(commandLineFrontendId))
        {
            return (commandLineFrontendId.Trim(), FrontendSource.CommandLine);
        }

        if (!string.IsNullOrWhiteSpace(persistedFrontendId))
        {
            return (persistedFrontendId.Trim(), FrontendSource.AppearanceSettings);
        }

        return (null, FrontendSource.Default);
    }

    private static string Describe(FrontendSource source) => source switch
    {
        FrontendSource.CommandLine => "--frontend override",
        FrontendSource.AppearanceSettings => "persisted appearance settings",
        _ => "default",
    };
}
