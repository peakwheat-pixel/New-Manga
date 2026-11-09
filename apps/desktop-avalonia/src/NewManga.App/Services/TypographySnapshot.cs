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
        var fallback = resolved is not null
            && GenericFamilies.Contains(resolved, StringComparer.OrdinalIgnoreCase)
            && segments.Count > 0
            && missing.Count == segments.Count - 1;
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
    private readonly Func<string, string?> _resourceLookup;

    public AvaloniaTypographySource(Func<string, string?>? resourceLookup = null)
    {
        _resourceLookup = resourceLookup ?? DefaultLookup;
    }

    public TypographySnapshot Read()
    {
        var lines = new List<TypographyLine>();
        var missingTokens = new List<string>();
        foreach (var tokenKey in new[] { "Nm.FontFamily.Ui", "Nm.FontFamily.Data", "Nm.FontFamily.Display" })
        {
            var stack = _resourceLookup(tokenKey);
            if (string.IsNullOrWhiteSpace(stack))
            {
                missingTokens.Add(tokenKey);
                continue;
            }
            lines.Add(TypographyResolver.Resolve(tokenKey, stack, IsInstalled));
        }
        if (lines.Count == 0)
        {
            return new TypographySnapshot(
                Array.Empty<TypographyLine>(),
                false,
                "当前主题未初始化（缺少 Nm.FontFamily.* 资源）。");
        }
        return new TypographySnapshot(lines, true, null);
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
            FontFamily family => family.Name,
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
