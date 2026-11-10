using Avalonia.Media;

namespace NewManga.App.Services;

/// <summary>FEA-14-SET-1 (AC1/AC2): one read-only typography projection line.</summary>
/// <param name="TokenKey">The DesignSystem token key (e.g. <c>Nm.FontFamily.Ui</c>).</param>
/// <param name="StackRaw">The theme's raw font stack.</param>
/// <param name="ResolvedFamily">The first installed family in the stack.</param>
/// <param name="Missing">Installed-unknown families walked before the resolved one.</param>
/// <param name="Scale">The typography scale for this face, when the theme exposes one.</param>
/// <param name="LineHeight">The line-height preset for this face, when exposed.</param>
/// <param name="Fallback">True when the stack degraded to its generic tail.</param>
public sealed record TypographyLine(
    string TokenKey,
    string StackRaw,
    string ResolvedFamily,
    IReadOnlyList<string> Missing,
    double? Scale,
    double? LineHeight,
    bool Fallback);

/// <summary>FEA-14-SET-1: the projection returned to the settings page (never a write).</summary>
public sealed record TypographySnapshot(
    IReadOnlyList<TypographyLine> Lines, bool Available, string? UnavailableReason);

/// <summary>FEA-14-SET-1 (AC1/AC5): the injectable, platform-free typography source.</summary>
public interface ITypographySource
{
    /// <summary>Read the current visual theme's font stacks. Must never write anything.</summary>
    TypographySnapshot Read();
}

/// <summary>
/// FEA-14-SET-1 (AC2): pure fallback resolution over the theme's font stack.
///
/// The resolver never mutates or installs anything; it only answers "which family would
/// this machine actually render, and which stack segments would silently fall through".
/// A stack whose every segment is missing reports the generic tail with
/// <paramref name="fallback"/> set, so the UI can explain the degradation instead of
/// pretending the requested family is in use.
/// </summary>
public static class TypographyResolver
{
    private static readonly string[] GenericFamilies =
    [
        "sans-serif", "serif", "monospace", "cursive", "fantasy",
        "system-ui", "ui-sans-serif", "ui-serif", "ui-monospace",
    ];

    public static TypographyLine Resolve(
        string tokenKey,
        string stackRaw,
        Func<string, bool> isInstalled,
        double? scale = null,
        double? lineHeight = null)
    {
        var segments = (stackRaw ?? string.Empty)
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Select(segment => segment.Trim('"', '\''))
            .Where(segment => segment.Length > 0)
            .ToList();
        var missing = new List<string>();
        string? resolved = null;
        foreach (var segment in segments)
        {
            if (GenericFamilies.Contains(segment, StringComparer.OrdinalIgnoreCase))
            {
                resolved = segment;
                break;
            }
            if (isInstalled(segment))
            {
                resolved = segment;
                break;
            }
            missing.Add(segment);
        }
        // DSH ruling (2026-11-10): "fallback" = the requested first family was not used,
        // i.e. at least one stack segment was missing. Landing on a generic tail is the
        // same fact, so it does not need a second flag.
        var fallback = missing.Count > 0 || resolved is null;
        return new TypographyLine(
            tokenKey,
            stackRaw ?? string.Empty,
            resolved ?? "sans-serif",
            missing,
            scale,
            lineHeight,
            fallback || resolved is null);
    }
}

/// <summary>
/// FEA-14-SET-1 (AC1/AC3/AC4): the Avalonia-backed source. It only READS the theme's
/// font-family resources and probes installed families; it never sets resources, styles
/// or settings, so opening the panel cannot write AppData or leak into global styles.
/// </summary>
public sealed class AvaloniaTypographySource : ITypographySource
{
    /// <summary>R-010: the three font-family tokens the projection must cover as a set.</summary>
    private static readonly (string TokenKey, string SizeKey, string HeightKey)[] FontTokens =
    [
        ("Nm.FontFamily.Ui", "Nm.FontSize.Md", "Nm.LineHeight.Body"),
        ("Nm.FontFamily.Data", "Nm.FontSize.Md", "Nm.LineHeight.Data"),
        ("Nm.FontFamily.Display", "Nm.FontSize.Xl", "Nm.LineHeight.Display"),
    ];

    private readonly Func<string, string?> _resourceLookup;

    public AvaloniaTypographySource(Func<string, string?>? resourceLookup = null)
    {
        _resourceLookup = resourceLookup ?? DefaultLookup;
    }

    public TypographySnapshot Read()
    {
        var lines = new List<TypographyLine>();
        var missingTokens = new List<string>();
        foreach (var (tokenKey, sizeKey, heightKey) in FontTokens)
        {
            var stack = _resourceLookup(tokenKey);
            if (string.IsNullOrWhiteSpace(stack))
            {
                missingTokens.Add(tokenKey);
                continue;
            }
            lines.Add(TypographyResolver.Resolve(
                tokenKey,
                stack,
                IsInstalled,
                scale: ReadNumber(sizeKey),
                lineHeight: ReadNumber(heightKey)));
        }

        // R-010: a partially initialised theme must not look like a complete three-row
        // projection. Missing tokens are surfaced in the reason instead of silently
        // dropping a row (the dead `missingTokens` collector from r1 is now used).
        if (missingTokens.Count > 0)
        {
            var reason = missingTokens.Count == FontTokens.Length
                ? "当前主题未初始化（缺少 Nm.FontFamily.* 资源）。"
                : $"当前主题字体 token 不完整（缺少 {string.Join("、", missingTokens)}）；请先初始化或重新应用视觉主题。";
            return new TypographySnapshot(lines, false, reason);
        }

        return new TypographySnapshot(lines, true, null);
    }

    private double? ReadNumber(string tokenKey)
    {
        var raw = _resourceLookup(tokenKey);
        if (string.IsNullOrWhiteSpace(raw)) return null;
        return double.TryParse(
            raw, System.Globalization.NumberStyles.Float,
            System.Globalization.CultureInfo.InvariantCulture, out var value)
            ? value
            : null;
    }

    private static string? DefaultLookup(string tokenKey)
    {
        if (Avalonia.Application.Current?.Resources.TryGetResource(
                tokenKey, null, out var value) != true || value is null)
        {
            return null;
        }
        return value switch
        {
            string text => text,
            FontFamily family => family.FamilyNames?.ToString() ?? family.Name,
            _ => value.ToString(),
        };
    }

    private static bool IsInstalled(string family)
    {
        if (string.IsNullOrWhiteSpace(family)) return false;
        try
        {
            return FontManager.Current.TryGetGlyphTypeface(
                new Typeface(family), out _);
        }
        catch (Exception)
        {
            return false;
        }
    }
}
