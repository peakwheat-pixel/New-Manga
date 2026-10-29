using System.Collections.ObjectModel;
using Avalonia;
using Avalonia.Media;
using Avalonia.Media.Immutable;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Tokens;

namespace NewManga.ThemeEngine;

/// <summary>
/// Resolves a <see cref="ThemePackage"/> into the flat <c>Nm.*</c> resource dictionary the design system
/// applies at runtime (contract §2.2/§4). The composed layer is the theme's whole personality:
/// <list type="bullet">
///   <item>colors — the 35 <c>Nm.Color.*</c> keys of the selected variant,</item>
///   <item>typography — 3 font families, 6 font sizes (scaled), 3 line-height multipliers and the 6
///   absolute line-height tiers derived from DESIGN_SYSTEM §3,</item>
///   <item>corners — <c>Nm.Corner.None/Sm/Md</c> (≤3px, validated before composition),</item>
///   <item>motion — <c>Nm.Motion.Duration.Fast/Normal/Slow</c> (R-15; <c>Instant</c> is a theme-invariant
///   global token and stays with the design system).</item>
/// </list>
/// Layout, density, spacing and sizes are deliberately absent: they are not theme personality
/// (contract §4, DESIGN_SYSTEM §1 token-compilation rule). Material/elevation are validated theme
/// declarations but have no <c>Nm.*</c> resource key in the frozen token vocabulary, so they are not
/// published here — the engine must never invent a second token truth.
/// </summary>
public static class ThemePaletteComposer
{
    /// <summary>Number of keys a composed theme layer contains (R-15: 35 colors + 3 families + 6 sizes + 3 multipliers + 6 absolute line heights + 3 corners + 3 motion).</summary>
    public const int ThemeLayerKeyCount = 59;

    /// <summary>Number of color keys (<see cref="ThemeTokenKeys.Colors"/>).</summary>
    public const int ColorLayerKeyCount = 35;

    /// <summary>Resolves <see cref="AppearanceMode.System"/> against the platform's current light/dark state.</summary>
    public static PaletteVariant ResolveVariant(AppearanceMode appearance, bool platformIsLight) => appearance switch
    {
        AppearanceMode.Light => PaletteVariant.Light,
        AppearanceMode.Dark => PaletteVariant.Dark,
        _ => platformIsLight ? PaletteVariant.Light : PaletteVariant.Dark,
    };

    /// <summary>Composes the whole theme layer for one variant.</summary>
    public static IReadOnlyDictionary<string, object?> Compose(ThemePackage package, PaletteVariant variant)
    {
        ArgumentNullException.ThrowIfNull(package);

        var tokens = TokenSet(package, variant);
        var layer = new SortedDictionary<string, object?>(StringComparer.Ordinal);

        AddColors(layer, tokens, variant);
        AddTypography(layer, tokens, variant);
        AddCorners(layer, tokens, variant);
        AddMotion(layer, tokens, variant);

        if (layer.Count != ThemeLayerKeyCount)
        {
            throw new ThemePackageException(
                $"composed theme layer has {layer.Count} keys, expected {ThemeLayerKeyCount}",
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.FieldMissing,
                    $"composed theme layer is incomplete ({layer.Count}/{ThemeLayerKeyCount} keys)")]);
        }

        return new ReadOnlyDictionary<string, object?>(layer);
    }

    /// <summary>Composes only the <c>Nm.Color.*</c> subset (35 keys) for preview snapshots and palette probes.</summary>
    public static IReadOnlyDictionary<string, object?> ComposeColorLayer(ThemePackage package, PaletteVariant variant)
    {
        ArgumentNullException.ThrowIfNull(package);

        var layer = new SortedDictionary<string, object?>(StringComparer.Ordinal);
        AddColors(layer, TokenSet(package, variant), variant);
        if (layer.Count != ColorLayerKeyCount)
        {
            throw new ThemePackageException(
                $"composed color layer has {layer.Count} keys, expected {ColorLayerKeyCount}",
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.ColorMissingKey,
                    $"composed color layer is incomplete ({layer.Count}/{ColorLayerKeyCount} keys)")]);
        }

        return new ReadOnlyDictionary<string, object?>(layer);
    }

    private static ThemeTokenSet TokenSet(ThemePackage package, PaletteVariant variant) =>
        variant == PaletteVariant.Light ? package.Light : package.Dark;

    private static void AddColors(
        IDictionary<string, object?> layer,
        ThemeTokenSet tokens,
        PaletteVariant variant)
    {
        foreach (var key in ThemeTokenKeys.Colors)
        {
            if (!tokens.Colors.TryGetValue(key, out var raw))
            {
                throw new ThemePackageException(
                    $"theme '{variant}' tokens are missing color '{key}'",
                    [ThemeValidationIssue.Error(ThemeIssueCodes.ColorMissingKey, "required color key is missing", key)]);
            }

            if (!ThemeContrast.TryParse(raw, out var color))
            {
                throw new ThemePackageException(
                    $"theme '{variant}' color '{key}' has unsupported value '{raw}'",
                    [ThemeValidationIssue.Error(ThemeIssueCodes.ColorInvalidValue, "unsupported color value", key)]);
            }

            layer[key] = new ImmutableSolidColorBrush(color);
        }
    }

    private static void AddTypography(
        IDictionary<string, object?> layer,
        ThemeTokenSet tokens,
        PaletteVariant variant)
    {
        layer[NmKeys.FontFamily.Ui] = ParseFontFamily(tokens.Typography.Ui, "typography.ui", variant);
        layer[NmKeys.FontFamily.Data] = ParseFontFamily(tokens.Typography.Data, "typography.data", variant);
        layer[NmKeys.FontFamily.Display] = ParseFontFamily(tokens.Typography.Display, "typography.display", variant);

        var scale = tokens.Typography.Scale;
        foreach (var (fontSizeKey, baseSize) in ThemeTokenBaseline.FontSizes)
        {
            layer[fontSizeKey] = Round(baseSize * scale);
        }

        foreach (var (multiplierKey, multiplierValue) in ThemeTokenBaseline.LineHeightMultipliers)
        {
            layer[multiplierKey] = multiplierValue;
        }

        var anchor = ThemeTokenBaseline.LineHeightMultipliers[NmKeys.LineHeight.Normal];
        var preset = PresetMultiplier(tokens.Typography.LineHeight);
        var presetRatio = preset / anchor;
        foreach (var tier in ThemeTokenBaseline.LineHeightTiers)
        {
            var baseSize = ThemeTokenBaseline.FontSizes[tier.FontSizeKey];
            layer[tier.ResourceKey] = Round(baseSize * scale * tier.DesignMultiplier * presetRatio);
        }
    }

    private static void AddCorners(
        IDictionary<string, object?> layer,
        ThemeTokenSet tokens,
        PaletteVariant variant)
    {
        layer[NmKeys.Corner.None] = new CornerRadius(RequireCorner(tokens.Corners.None, "none", variant));
        layer[NmKeys.Corner.Sm] = new CornerRadius(RequireCorner(tokens.Corners.Sm, "sm", variant));
        layer[NmKeys.Corner.Md] = new CornerRadius(RequireCorner(tokens.Corners.Md, "md", variant));
    }

    private static double RequireCorner(double value, string name, PaletteVariant variant)
    {
        if (double.IsNaN(value) || value < 0 || value > ThemeCorners.MaxRadius)
        {
            throw new ThemePackageException(
                $"theme '{variant}' corner '{name}' is {TokenValues.FormatDouble(value)}; only 0–{ThemeCorners.MaxRadius}px is allowed",
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.CornerOutOfRange,
                    "corner radius must stay within 0–3px (DESIGN_SYSTEM §1 rule 4)",
                    $"corners.{name}")]);
        }

        return value;
    }

    private static void AddMotion(
        IDictionary<string, object?> layer,
        ThemeTokenSet tokens,
        PaletteVariant variant)
    {
        if (tokens.Motion.FastMs < 0 || tokens.Motion.FastMs > ThemeMotion.MaxDurationMs ||
            tokens.Motion.NormalMs < 0 || tokens.Motion.NormalMs > ThemeMotion.MaxDurationMs ||
            tokens.Motion.SlowMs < 0 || tokens.Motion.SlowMs > ThemeMotion.MaxDurationMs)
        {
            throw new ThemePackageException(
                $"theme '{variant}' motion durations are out of range",
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.MotionDurationOutOfRange,
                    $"motion durations must stay within 0–{ThemeMotion.MaxDurationMs}ms")]);
        }

        layer[NmKeys.Motion.Duration.Fast] = TimeSpan.FromMilliseconds(tokens.Motion.FastMs);
        layer[NmKeys.Motion.Duration.Normal] = TimeSpan.FromMilliseconds(tokens.Motion.NormalMs);
        layer[NmKeys.Motion.Duration.Slow] = TimeSpan.FromMilliseconds(tokens.Motion.SlowMs);
    }

    private static FontFamily ParseFontFamily(string raw, string path, PaletteVariant variant)
    {
        try
        {
            return new FontFamily(TokenValues.ParseFontFamily(raw));
        }
        catch (FormatException exception)
        {
            throw new ThemePackageException(
                $"theme '{variant}' {path} font family is invalid: {exception.Message}",
                [ThemeValidationIssue.Error(
                    ThemeIssueCodes.FontFamilyInvalid,
                    $"unsupported font family '{raw}'",
                    path)]);
        }
    }

    private static double PresetMultiplier(LineHeightPreset preset) => preset switch
    {
        LineHeightPreset.Tight => ThemeTokenBaseline.LineHeightMultipliers[NmKeys.LineHeight.Tight],
        LineHeightPreset.Loose => ThemeTokenBaseline.LineHeightMultipliers[NmKeys.LineHeight.Loose],
        _ => ThemeTokenBaseline.LineHeightMultipliers[NmKeys.LineHeight.Normal],
    };

    private static double Round(double value) => Math.Round(value, 2, MidpointRounding.AwayFromZero);
}
