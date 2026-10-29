using NewManga.DesignSystem;

namespace NewManga.ThemeEngine;

/// <summary>
/// The resource-key sets the Theme Engine is allowed to publish (contract §2.2). Derived from the
/// design system's generated <see cref="NmKeys"/> so a theme can never invent a key outside the frozen
/// token vocabulary (DESIGN_SYSTEM §0: one token truth).
/// </summary>
public static class ThemeTokenKeys
{
    /// <summary>Prefix every theme-engine resource key starts with.</summary>
    public const string Prefix = "Nm.";

    /// <summary>Prefix of the color layer a theme package owns.</summary>
    public const string ColorPrefix = "Nm.Color.";

    /// <summary>
    /// The 35 color keys every theme token set must define (background 6, line 4, text 5, accent 6,
    /// status 7, status-muted 7), in ordinal order.
    /// </summary>
    public static IReadOnlyList<string> Colors { get; } = NmKeys.All
        .Where(static key => key.StartsWith(ColorPrefix, StringComparison.Ordinal))
        .OrderBy(static key => key, StringComparer.Ordinal)
        .ToArray();

    /// <summary>Every resource key the design system publishes, as a set for palette conformance tests.</summary>
    public static IReadOnlySet<string> Published { get; } =
        new HashSet<string>(NmKeys.All, StringComparer.Ordinal);
}
