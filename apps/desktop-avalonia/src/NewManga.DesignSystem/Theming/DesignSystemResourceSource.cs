using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Styling;

namespace NewManga.DesignSystem.Theming;

/// <summary>Which palette the design system should show (contract §4 <c>AppearanceMode</c>).</summary>
public enum AppearanceMode
{
    /// <summary>Follow the platform theme.</summary>
    System,

    Light,

    Dark,
}

/// <summary>Standard or WCAG-boosted contrast (contract §4 <c>ContrastMode</c>).</summary>
public enum ContrastMode
{
    Standard,

    High,
}

/// <summary>Comfortable/Compact/Spacious density (contract §4 <c>Density</c>).</summary>
public enum DensityMode
{
    Comfortable,

    Compact,

    Spacious,
}

/// <summary>
/// Where the design system loads its resource dictionaries from. The interface exists so the Theme
/// Engine (V11R-C-1) and tests can substitute user-theme or deliberately broken sources and prove the
/// fallback path never throws (AC9).
/// </summary>
public interface IDesignSystemResourceSource
{
    /// <summary>Theme-invariant tokens (<c>Tokens.Global.axaml</c>).</summary>
    Uri GlobalTokens { get; }

    Uri DarkPalette { get; }

    Uri LightPalette { get; }

    /// <summary>Complete high-contrast palette, itself theme scoped (dark/light).</summary>
    Uri HighContrastPalette { get; }

    Uri CompactDensity { get; }

    Uri SpaciousDensity { get; }

    Uri ReducedMotion { get; }
}

/// <summary>Default source: dictionaries compiled into the design-system assembly.</summary>
public sealed class DesignSystemResourceSource : IDesignSystemResourceSource
{
    /// <summary>Shared stateless instance.</summary>
    public static DesignSystemResourceSource Default { get; } = new();

    private const string Root = "avares://NewManga.DesignSystem/Themes/";

    public Uri GlobalTokens { get; } = new(Root + "Tokens.Global.axaml");

    public Uri DarkPalette { get; } = new(Root + "Tokens.Dark.axaml");

    public Uri LightPalette { get; } = new(Root + "Tokens.Light.axaml");

    public Uri HighContrastPalette { get; } = new(Root + "Tokens.HighContrast.axaml");

    public Uri CompactDensity { get; } = new(Root + "Density.Compact.axaml");

    public Uri SpaciousDensity { get; } = new(Root + "Density.Spacious.axaml");

    public Uri ReducedMotion { get; } = new(Root + "Motion.Reduced.axaml");
}
