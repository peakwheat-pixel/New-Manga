using System.Globalization;
using System.Text.RegularExpressions;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Tokens;

namespace NewManga.ThemeEngine;

/// <summary>
/// Validates a theme package against the frozen contract (V11R_AVALONIA_CONTRACT §4) and the frozen
/// design rules (DESIGN_SYSTEM §1/§2/§3). The validator is fail-closed: any <c>error</c> finding makes
/// the package invalid, which blocks installation/import. Unknown fields are warnings, never errors,
/// except declarations of a forbidden visual effect (shadow/gradient/blur/mica/acrylic), which the
/// package reader already turns into errors.
/// <para>
/// Contrast policy (DESIGN_SYSTEM §2.3): text primary ≥7:1 and secondary ≥4.5:1 are measured against the
/// two surfaces the spec names for body text (<c>Bg.Panel</c> / <c>Bg.Canvas</c>) and are errors.
/// Status/accent colors are measured against <c>Bg.Panel</c> — the surface status components live on —
/// and are errors. The same status hues measured against <c>Bg.Raised</c>/<c>Bg.Canvas</c> are reported
/// as warnings only: those are secondary/edge surfaces, and the frozen R-09 baseline deliberately only
/// guarantees the panel floor (Lead ruling on V11R-C-1; see verification/V11R-C-1/DEVIATIONS.md).
/// </para>
/// </summary>
public sealed class ThemeValidator : IThemeValidator
{
    /// <summary>Shared stateless instance.</summary>
    public static ThemeValidator Default { get; } = new();

    private const double PrimaryTextFloor = 7.0;
    private const double SecondaryTextFloor = 4.5;
    private const double StatusFloor = 4.5;
    private const double AccentOnFloor = 4.5;
    private const double FocusAccentFloor = 3.0;
    private const int MaxTags = 16;
    private const int MaxTagLength = 32;
    private const double MinFontScale = 0.8;
    private const double MaxFontScale = 1.3;

    private static readonly Regex IdPattern = new(
        "^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$",
        RegexOptions.CultureInvariant | RegexOptions.Compiled);

    private static readonly Regex VersionPattern = new(
        "^\\d+\\.\\d+\\.\\d+(?:[-+][0-9A-Za-z.-]+)?$",
        RegexOptions.CultureInvariant | RegexOptions.Compiled);

    private static readonly string[] StatusKeys =
    [
        NmKeys.Color.Status.Queued,
        NmKeys.Color.Status.Running,
        NmKeys.Color.Status.Done,
        NmKeys.Color.Status.Failed,
        NmKeys.Color.Status.Blocked,
        NmKeys.Color.Status.Stale,
        NmKeys.Color.Status.Skipped,
    ];

    /// <summary>Validates one package; never throws for invalid content.</summary>
    public ThemeValidationResult Validate(ThemePackage package)
    {
        ArgumentNullException.ThrowIfNull(package);

        var issues = new List<ThemeValidationIssue>(capacity: 64);

        // Reader diagnostics (unknown fields, forbidden declarations, duplicate fields) are part of the
        // package's validity: a package that declares a gradient/shadow field must not import.
        issues.AddRange(package.Metadata.LoadWarnings);

        ValidateSchema(package, issues);
        ValidateDescriptor(package.Descriptor, issues);
        ValidateTokenSet(package.Light, PaletteVariant.Light, issues);
        ValidateTokenSet(package.Dark, PaletteVariant.Dark, issues);

        return ThemeValidationResult.From(Deduplicate(issues));
    }

    private static void ValidateSchema(ThemePackage package, List<ThemeValidationIssue> issues)
    {
        if (!string.Equals(package.Schema, ThemeDefaults.Schema, StringComparison.Ordinal))
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.SchemaUnsupported,
                $"package schema '{package.Schema}' is not supported; expected '{ThemeDefaults.Schema}'",
                "schema"));
        }

        if (!string.Equals(package.Metadata.EngineVersion, ThemeDefaults.EngineVersion, StringComparison.Ordinal))
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.EngineVersionMismatch,
                $"metadata.engineVersion '{package.Metadata.EngineVersion}' does not match engine version " +
                $"'{ThemeDefaults.EngineVersion}'; the package is read with the v1 schema",
                "metadata.engineVersion"));
        }
    }

    private static void ValidateDescriptor(ThemeDescriptor descriptor, List<ThemeValidationIssue> issues)
    {
        if (string.IsNullOrWhiteSpace(descriptor.Id) || !IdPattern.IsMatch(descriptor.Id))
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.DescriptorIdInvalid,
                $"theme id '{descriptor.Id}' must be 1–64 chars of lowercase a-z, 0-9 and '-', starting/ending alphanumeric",
                "descriptor.id"));
        }

        if (string.IsNullOrWhiteSpace(descriptor.Name) || descriptor.Name.Length > 80)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.DescriptorNameInvalid,
                "theme name must be 1–80 visible characters",
                "descriptor.name"));
        }

        if (!VersionPattern.IsMatch(descriptor.Version ?? string.Empty))
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.DescriptorVersionNonSemver,
                $"theme version '{descriptor.Version}' is not semver-shaped (e.g. 1.0.0)",
                "descriptor.version"));
        }

        if (!descriptor.SupportsLight && !descriptor.SupportsDark)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.DescriptorAppearanceUnsupported,
                "theme must support at least one appearance (light or dark)",
                "descriptor"));
        }

        var tags = descriptor.Tags ?? [];
        if (tags.Count > MaxTags)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.DescriptorTagsInvalid,
                $"theme may declare at most {MaxTags} tags, found {tags.Count}",
                "descriptor.tags"));
        }

        var seen = new HashSet<string>(StringComparer.Ordinal);
        for (var index = 0; index < tags.Count; index++)
        {
            var tag = tags[index];
            if (string.IsNullOrWhiteSpace(tag) || tag.Length > MaxTagLength || !seen.Add(tag))
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.DescriptorTagsInvalid,
                    $"tag '{tag}' must be unique, non-empty and at most {MaxTagLength} chars",
                    $"descriptor.tags[{index}]"));
            }
        }
    }

    private static void ValidateTokenSet(
        ThemeTokenSet tokens,
        PaletteVariant variant,
        List<ThemeValidationIssue> issues)
    {
        var scope = variant == PaletteVariant.Light ? "light" : "dark";
        ValidateColors(tokens, scope, issues);
        ValidateCorners(tokens.Corners, scope, issues);
        ValidateTypography(tokens.Typography, scope, issues);
        ValidateMotion(tokens.Motion, scope, issues);
        ValidateContrast(tokens, variant, scope, issues);
    }

    private static void ValidateColors(ThemeTokenSet tokens, string scope, List<ThemeValidationIssue> issues)
    {
        foreach (var required in ThemeTokenKeys.Colors)
        {
            if (!tokens.Colors.ContainsKey(required))
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.ColorMissingKey,
                    $"required color token '{required}' is missing",
                    $"{scope}.colors.{required}"));
                continue;
            }

            if (!ThemeContrast.TryParse(tokens.Colors[required], out _))
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.ColorInvalidValue,
                    $"color '{required}' has unsupported value '{tokens.Colors[required]}'",
                    $"{scope}.colors.{required}"));
            }
        }

        foreach (var pair in tokens.Colors)
        {
            if (ThemeTokenKeys.Colors.Contains(pair.Key, StringComparer.Ordinal))
            {
                continue;
            }

            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.ColorUnknownKey,
                $"unknown color token '{pair.Key}' is ignored (contract §2.2 defines {ThemeTokenKeys.Colors.Count} keys)",
                $"{scope}.colors.{pair.Key}"));
        }
    }

    private static void ValidateCorners(ThemeCorners corners, string scope, List<ThemeValidationIssue> issues)
    {
        ValidateCorner(corners.None, "none", scope, issues);
        ValidateCorner(corners.Sm, "sm", scope, issues);
        ValidateCorner(corners.Md, "md", scope, issues);
    }

    private static void ValidateCorner(double value, string name, string scope, List<ThemeValidationIssue> issues)
    {
        if (double.IsNaN(value) || value < 0 || value > ThemeCorners.MaxRadius)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.CornerOutOfRange,
                $"corner '{name}' is {TokenValues.FormatDouble(value)}; only 0–{ThemeCorners.MaxRadius}px is allowed " +
                "(DESIGN_SYSTEM §1 rule 4)",
                $"{scope}.corners.{name}"));
        }
    }

    private static void ValidateTypography(ThemeTypography typography, string scope, List<ThemeValidationIssue> issues)
    {
        ValidateFontFamily(typography.Ui, "ui", scope, issues);
        ValidateFontFamily(typography.Data, "data", scope, issues);
        ValidateFontFamily(typography.Display, "display", scope, issues);

        if (double.IsNaN(typography.Scale) || typography.Scale < MinFontScale || typography.Scale > MaxFontScale)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.FontScaleOutOfRange,
                $"font scale {TokenValues.FormatDouble(typography.Scale)} is outside {MinFontScale}–{MaxFontScale}",
                $"{scope}.font.scale"));
        }
    }

    private static void ValidateFontFamily(string raw, string name, string scope, List<ThemeValidationIssue> issues)
    {
        var path = $"{scope}.font.family.{name}";
        if (string.IsNullOrWhiteSpace(raw))
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.FontFamilyInvalid,
                $"font family '{name}' must not be empty",
                path));
            return;
        }

        // Themes declare system font stacks only; bundling/embedding fonts is forbidden by the
        // design-system rule "商业/系统字体不得随包" (DESIGN_SYSTEM §3), so a path-looking family is an error.
        if (raw.Contains('\\') || raw.Contains('/') || raw.Contains(".ttf", StringComparison.OrdinalIgnoreCase) ||
            raw.Contains(".otf", StringComparison.OrdinalIgnoreCase) ||
            raw.Contains(".woff", StringComparison.OrdinalIgnoreCase))
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.FontFamilyInvalid,
                $"font family '{raw}' looks like a bundled font path; only system font stacks are allowed",
                path));
            return;
        }

        try
        {
            _ = TokenValues.ParseFontFamily(raw);
        }
        catch (FormatException exception)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.FontFamilyInvalid,
                $"font family '{raw}' is unusable: {exception.Message}",
                path));
        }
    }

    private static void ValidateMotion(ThemeMotion motion, string scope, List<ThemeValidationIssue> issues)
    {
        if (motion.FastMs < 0 || motion.NormalMs < 0 || motion.SlowMs < 0 ||
            motion.FastMs > ThemeMotion.MaxDurationMs ||
            motion.NormalMs > ThemeMotion.MaxDurationMs ||
            motion.SlowMs > ThemeMotion.MaxDurationMs)
        {
            issues.Add(ThemeValidationIssue.Error(
                ThemeIssueCodes.MotionDurationOutOfRange,
                $"motion durations must stay within 0–{ThemeMotion.MaxDurationMs}ms",
                $"{scope}.motion"));
            return;
        }

        // R-15: the three theme-owned tiers must be ordered fast <= normal <= slow.
        if (motion.FastMs > motion.NormalMs || motion.NormalMs > motion.SlowMs)
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.MotionDurationOrder,
                $"motion tiers are not ordered fast <= normal <= slow ({motion.FastMs}ms/{motion.NormalMs}ms/{motion.SlowMs}ms)",
                $"{scope}.motion"));
        }
    }

    private static void ValidateContrast(
        ThemeTokenSet tokens,
        PaletteVariant variant,
        string scope,
        List<ThemeValidationIssue> issues)
    {
        CheckTextContrast(tokens, scope, issues, NmKeys.Color.Text.Primary, PrimaryTextFloor, ThemeIssueCodes.ContrastTextPrimary, "primary text", isError: true);
        CheckTextContrast(tokens, scope, issues, NmKeys.Color.Text.Secondary, SecondaryTextFloor, ThemeIssueCodes.ContrastTextSecondary, "secondary text", isError: true);

        foreach (var statusKey in StatusKeys)
        {
            CheckStatusPanelContrast(tokens, scope, issues, statusKey);
        }

        // Secondary/edge surfaces: aggregate into one warning per surface so a shipped theme does not
        // drown the Theme Studio result list; the panel floor above is the normative gate.
        ReportStatusEdgeSurface(tokens, scope, issues, NmKeys.Color.Bg.Canvas);
        ReportStatusEdgeSurface(tokens, scope, issues, NmKeys.Color.Bg.Raised);

        if (TryColor(tokens, NmKeys.Color.Accent.On, out var accentOn) &&
            TryColor(tokens, NmKeys.Color.Accent.Base, out var accentBase))
        {
            var ratio = ThemeContrast.Ratio(accentOn, accentBase);
            if (ratio < AccentOnFloor)
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.ContrastAccentOn,
                    $"accent.on {accentOn} on accent.base {accentBase} is {FormatRatio(ratio)}:1; need >= {AccentOnFloor}:1",
                    $"{scope}.colors.{NmKeys.Color.Accent.On}"));
            }
        }

        if (TryColor(tokens, NmKeys.Color.Accent.Base, out var focusAccent) &&
            TryColor(tokens, NmKeys.Color.Bg.Panel, out var panel))
        {
            var ratio = ThemeContrast.Ratio(focusAccent, panel);
            if (ratio < FocusAccentFloor)
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.ContrastAccentFocus,
                    $"focus accent {focusAccent} on bg.panel {panel} is {FormatRatio(ratio)}:1; need >= {FocusAccentFloor}:1",
                    $"{scope}.colors.{NmKeys.Color.Accent.Base}"));
            }
        }
    }

    private static void CheckTextContrast(
        ThemeTokenSet tokens,
        string scope,
        List<ThemeValidationIssue> issues,
        string foregroundKey,
        double floor,
        string code,
        string label,
        bool isError)
    {
        if (!TryColor(tokens, foregroundKey, out var foreground))
        {
            return;
        }

        foreach (var backgroundKey in new[] { NmKeys.Color.Bg.Panel, NmKeys.Color.Bg.Canvas })
        {
            if (!TryColor(tokens, backgroundKey, out var background))
            {
                continue;
            }

            var ratio = ThemeContrast.Ratio(foreground, background);
            if (ratio >= floor)
            {
                continue;
            }

            var message =
                $"{label} {foreground} on {backgroundKey} {background} is {FormatRatio(ratio)}:1; need >= {floor}:1 " +
                "(DESIGN_SYSTEM §2.3)";
            issues.Add(isError
                ? ThemeValidationIssue.Error(code, message, $"{scope}.colors.{foregroundKey}")
                : ThemeValidationIssue.Warning(code, message, $"{scope}.colors.{foregroundKey}"));
        }
    }

    /// <summary>Status hues are normative on <c>bg.panel</c> (the surface status components live on).</summary>
    private static void CheckStatusPanelContrast(
        ThemeTokenSet tokens,
        string scope,
        List<ThemeValidationIssue> issues,
        string foregroundKey)
    {
        if (!TryColor(tokens, foregroundKey, out var foreground) ||
            !TryColor(tokens, NmKeys.Color.Bg.Panel, out var panel))
        {
            return;
        }

        var ratio = ThemeContrast.Ratio(foreground, panel);
        if (ratio >= StatusFloor)
        {
            return;
        }

        issues.Add(ThemeValidationIssue.Error(
            ThemeIssueCodes.ContrastStatus,
            $"status {foreground} on bg.panel {panel} is {FormatRatio(ratio)}:1; need >= {StatusFloor}:1 " +
            "(DESIGN_SYSTEM §2.3)",
            $"{scope}.colors.{foregroundKey}"));
    }

    /// <summary>
    /// Warns once per non-normative surface when status hues stay under the floor there. The frozen
    /// token baseline only guarantees the panel floor (R-09), so canvas/raised stay warnings.
    /// </summary>
    private static void ReportStatusEdgeSurface(
        ThemeTokenSet tokens,
        string scope,
        List<ThemeValidationIssue> issues,
        string backgroundKey)
    {
        if (!TryColor(tokens, backgroundKey, out var background))
        {
            return;
        }

        var failing = new List<string>(StatusKeys.Length);
        var minimum = double.MaxValue;
        foreach (var statusKey in StatusKeys)
        {
            if (!TryColor(tokens, statusKey, out var foreground))
            {
                continue;
            }

            var ratio = ThemeContrast.Ratio(foreground, background);
            if (ratio < StatusFloor)
            {
                failing.Add(statusKey[(statusKey.LastIndexOf('.') + 1)..]);
                minimum = Math.Min(minimum, ratio);
            }
        }

        if (failing.Count == 0)
        {
            return;
        }

        issues.Add(ThemeValidationIssue.Warning(
            ThemeIssueCodes.ContrastStatus,
            $"{failing.Count} status hue(s) ({string.Join(", ", failing)}) stay below {StatusFloor}:1 on " +
            $"{backgroundKey} {background} (minimum {FormatRatio(minimum)}:1); panel is the normative surface",
            $"{scope}.colors.{backgroundKey}"));
    }

    private static bool TryColor(ThemeTokenSet tokens, string key, out string raw)
    {
        if (tokens.Colors.TryGetValue(key, out var value) && ThemeContrast.TryParse(value, out _))
        {
            raw = value;
            return true;
        }

        raw = string.Empty;
        return false;
    }

    private static string FormatRatio(double ratio) => ratio.ToString("F2", CultureInfo.InvariantCulture);

    private static IReadOnlyList<ThemeValidationIssue> Deduplicate(List<ThemeValidationIssue> issues)
    {
        var seen = new HashSet<string>(StringComparer.Ordinal);
        var unique = new List<ThemeValidationIssue>(issues.Count);
        foreach (var issue in issues)
        {
            var key = issue.Code + "\u001f" + (issue.Path ?? string.Empty) + "\u001f" + issue.Message;
            if (seen.Add(key))
            {
                unique.Add(issue);
            }
        }

        return unique;
    }
}
