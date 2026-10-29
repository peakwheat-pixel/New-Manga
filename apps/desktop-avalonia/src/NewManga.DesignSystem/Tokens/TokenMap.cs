namespace NewManga.DesignSystem.Tokens;

/// <summary>Value family a token is serialized as inside the Avalonia resource dictionaries.</summary>
public enum TokenValueKind
{
    Brush,
    FontFamily,
    Double,
    EmRatio,
    FontWeight,
    CornerRadius,
    Thickness,
    TimeSpan,
    Boolean,
    String,
    Int32,
}

/// <summary>One frozen DTCG token mapped to exactly one Avalonia resource key (contract §2).</summary>
public sealed record TokenBinding(string TokenPath, string ResourceKey, TokenValueKind Kind);

/// <summary>
/// A resource key the design system must publish although the frozen <c>tokens.json</c> only implies
/// it (padding aggregates, control heights, absolute line heights). Every entry documents its
/// derivation so the extension stays auditable against the frozen baseline.
/// </summary>
public sealed record DerivedToken(string ResourceKey, TokenValueKind Kind, string RawValue, string Derivation);

/// <summary>
/// Curated high-contrast value for one color key. <c>tokens.json</c> defines no contrast mode; the
/// design-system extension raises every text/line/accent/status pair above the WCAG thresholds of
/// DESIGN_SYSTEM §2.3 while keeping the five-level background ladder unchanged.
/// </summary>
public sealed record HighContrastColor(string ResourceKey, string DarkRawValue, string LightRawValue);

/// <summary>Density override for one size/padding key (contract §4 <c>Density</c> is a layout concern, not a token set).</summary>
public sealed record DensityToken(string ResourceKey, TokenValueKind Kind, string CompactRawValue, string SpaciousRawValue);

/// <summary>
/// The one authoritative mapping from frozen token paths to <c>Nm.*</c> resource keys
/// (contract §2.1: <c>{group}.{path}</c> -> <c>Nm.{Group}.{Path}</c>, PascalCase per segment).
/// </summary>
public static class TokenMap
{
    /// <summary>Resource-key prefix owned by the design system.</summary>
    public const string Prefix = "Nm.";

    /// <summary>DTCG scope prefix for the dark palette.</summary>
    public const string DarkScope = "color.dark.";

    /// <summary>DTCG scope prefix for the light palette.</summary>
    public const string LightScope = "color.light.";

    private static readonly (string TokenPath, string ResourceKey, TokenValueKind Kind)[] GlobalTable =
    [
        // Typography families / scale (DESIGN_SYSTEM §3).
        ("font.family.ui", "Nm.FontFamily.Ui", TokenValueKind.FontFamily),
        ("font.family.data", "Nm.FontFamily.Data", TokenValueKind.FontFamily),
        ("font.family.display", "Nm.FontFamily.Display", TokenValueKind.FontFamily),
        ("font.size.xs", "Nm.FontSize.Xs", TokenValueKind.Double),
        ("font.size.sm", "Nm.FontSize.Sm", TokenValueKind.Double),
        ("font.size.md", "Nm.FontSize.Md", TokenValueKind.Double),
        ("font.size.lg", "Nm.FontSize.Lg", TokenValueKind.Double),
        ("font.size.xl", "Nm.FontSize.Xl", TokenValueKind.Double),
        ("font.size.2xl", "Nm.FontSize.Xxl", TokenValueKind.Double),
        ("font.weight.regular", "Nm.FontWeight.Regular", TokenValueKind.FontWeight),
        ("font.weight.medium", "Nm.FontWeight.Medium", TokenValueKind.FontWeight),
        ("font.weight.semibold", "Nm.FontWeight.SemiBold", TokenValueKind.FontWeight),
        ("font.lineHeight.tight", "Nm.LineHeight.Tight", TokenValueKind.Double),
        ("font.lineHeight.normal", "Nm.LineHeight.Normal", TokenValueKind.Double),
        ("font.lineHeight.loose", "Nm.LineHeight.Loose", TokenValueKind.Double),
        ("font.tracking.normal", "Nm.FontTracking.Normal", TokenValueKind.EmRatio),
        ("font.tracking.caps", "Nm.FontTracking.Caps", TokenValueKind.EmRatio),
        ("font.tracking.data", "Nm.FontTracking.Data", TokenValueKind.EmRatio),

        // Spacing scale (DESIGN_SYSTEM §4).
        ("space.0", "Nm.Space.0", TokenValueKind.Double),
        ("space.1", "Nm.Space.1", TokenValueKind.Double),
        ("space.2", "Nm.Space.2", TokenValueKind.Double),
        ("space.3", "Nm.Space.3", TokenValueKind.Double),
        ("space.4", "Nm.Space.4", TokenValueKind.Double),
        ("space.5", "Nm.Space.5", TokenValueKind.Double),
        ("space.6", "Nm.Space.6", TokenValueKind.Double),
        ("space.7", "Nm.Space.7", TokenValueKind.Double),
        ("space.8", "Nm.Space.8", TokenValueKind.Double),

        // Radius / borders (DESIGN_SYSTEM §1 rule 4 + §8 focus ring).
        ("radius.none", "Nm.Corner.None", TokenValueKind.CornerRadius),
        ("radius.sm", "Nm.Corner.Sm", TokenValueKind.CornerRadius),
        ("radius.md", "Nm.Corner.Md", TokenValueKind.CornerRadius),
        ("border.hairline", "Nm.Border.Hairline", TokenValueKind.Thickness),
        ("border.focus", "Nm.Border.Focus", TokenValueKind.Thickness),

        // Named layout sizes (contract §2.2).
        ("size.hTop", "Nm.Size.TopBand", TokenValueKind.Double),
        ("size.hSub", "Nm.Size.SubBand", TokenValueKind.Double),
        ("size.wFilm", "Nm.Size.FilmStripCollapsed", TokenValueKind.Double),
        ("size.wFilmOpen", "Nm.Size.FilmStripExpanded", TokenValueKind.Double),
        ("size.wInsp", "Nm.Size.InspectorCollapsed", TokenValueKind.Double),
        ("size.wInspOpen", "Nm.Size.InspectorExpanded", TokenValueKind.Double),
        ("size.wDrawer", "Nm.Size.Drawer", TokenValueKind.Double),
        ("size.wTree", "Nm.Size.TreeWidth", TokenValueKind.Double),
        ("size.hBand", "Nm.Size.StatusBandPage", TokenValueKind.Double),
        ("size.hBandOpen", "Nm.Size.StatusBandExpanded", TokenValueKind.Double),
        ("size.hRunStrip", "Nm.Size.StatusBandBatch", TokenValueKind.Double),
        ("size.icon", "Nm.Icon.Size", TokenValueKind.Double),
        ("size.iconLg", "Nm.Icon.SizeLarge", TokenValueKind.Double),
        ("size.hudSlot", "Nm.Size.HudSlot", TokenValueKind.Double),

        // Row heights (DESIGN_SYSTEM §4 two densities).
        ("row.matrix", "Nm.Size.RowBatch", TokenValueKind.Double),
        ("row.dense", "Nm.Size.RowDense", TokenValueKind.Double),
        ("row.normal", "Nm.Size.RowNormal", TokenValueKind.Double),
        ("row.comfy", "Nm.Size.RowPage", TokenValueKind.Double),
        ("row.page", "Nm.Size.RowPageTall", TokenValueKind.Double),

        // Motion (DESIGN_SYSTEM §7, contract §2.2).
        ("motion.duration.instant", "Nm.Motion.Duration.Instant", TokenValueKind.TimeSpan),
        ("motion.duration.fast", "Nm.Motion.Duration.Fast", TokenValueKind.TimeSpan),
        ("motion.duration.normal", "Nm.Motion.Duration.Normal", TokenValueKind.TimeSpan),
        ("motion.easing.standard", "Nm.Motion.Easing.Standard", TokenValueKind.String),

        // Status symbols: the single source of the "symbol" channel (DESIGN_SYSTEM §2.2).
        ("stateSymbols.queued", "Nm.State.Symbol.Queued", TokenValueKind.String),
        ("stateSymbols.running", "Nm.State.Symbol.Running", TokenValueKind.String),
        ("stateSymbols.done", "Nm.State.Symbol.Done", TokenValueKind.String),
        ("stateSymbols.failed", "Nm.State.Symbol.Failed", TokenValueKind.String),
        ("stateSymbols.blocked", "Nm.State.Symbol.Blocked", TokenValueKind.String),
        ("stateSymbols.stale", "Nm.State.Symbol.Stale", TokenValueKind.String),
        ("stateSymbols.skipped", "Nm.State.Symbol.Skipped", TokenValueKind.String),
        ("stateSymbols.notStarted", "Nm.State.Symbol.NotStarted", TokenValueKind.String),
        ("stateSymbols.locked", "Nm.State.Symbol.Locked", TokenValueKind.String),

        // Layering (contract §2.2 z-index group).
        ("zIndex.base", "Nm.ZIndex.Base", TokenValueKind.Int32),
        ("zIndex.sticky", "Nm.ZIndex.Sticky", TokenValueKind.Int32),
        ("zIndex.panel", "Nm.ZIndex.Panel", TokenValueKind.Int32),
        ("zIndex.drawer", "Nm.ZIndex.Drawer", TokenValueKind.Int32),
        ("zIndex.overlay", "Nm.ZIndex.Overlay", TokenValueKind.Int32),
        ("zIndex.modal", "Nm.ZIndex.Modal", TokenValueKind.Int32),
        ("zIndex.palette", "Nm.ZIndex.Palette", TokenValueKind.Int32),
    ];

    /// <summary>All 71 global (theme-invariant) token bindings from the frozen baseline.</summary>
    public static IReadOnlyList<TokenBinding> GlobalBindings { get; } = GlobalTable
        .Select(static entry => new TokenBinding(entry.TokenPath, entry.ResourceKey, entry.Kind))
        .ToArray();

    /// <summary>
    /// Tokens the contract requires as resources but the frozen file only implies. Every value is
    /// derived from a frozen token (or a frozen design-system rule) and says which.
    /// </summary>
    public static IReadOnlyList<DerivedToken> DerivedGlobals { get; } =
    [
        new("Nm.Size.ControlHeight", TokenValueKind.Double, "28",
            "contract §2.2: control height; equal to row.comfy (28px) so controls align with Page-mode rows"),
        new("Nm.Size.ControlHeightSm", TokenValueKind.Double, "24",
            "contract §2.2: compact control height; equal to row.dense (24px)"),
        new("Nm.Padding.Panel", TokenValueKind.Thickness, "12",
            "contract §2.2: panel padding = space.4"),
        new("Nm.Padding.Card", TokenValueKind.Thickness, "12",
            "contract §2.2: card padding = space.4"),
        new("Nm.Padding.Control", TokenValueKind.Thickness, "12,8,12,8",
            "contract §2.2 + DESIGN_SYSTEM §4: control padding 8px vertical / 12px horizontal (space.3/space.4), stored as Avalonia left,top,right,bottom"),
        new("Nm.Padding.ControlSm", TokenValueKind.Thickness, "8,6,8,6",
            "contract §2.2: small control padding 6px vertical / 8px horizontal; stored as Avalonia left,top,right,bottom"),
        new("Nm.Padding.Cell", TokenValueKind.Thickness, "8",
            "contract §2.2 + DESIGN_SYSTEM §4: cell horizontal padding = space.3 (row height governs vertical rhythm)"),
        new("Nm.Padding.Section", TokenValueKind.Thickness, "16",
            "contract §2.2: section padding = space.5"),
        new("Nm.Padding.Icon", TokenValueKind.Thickness, "4",
            "contract §3.1 icon buttons: square padding = space.2"),
        new("Nm.Padding.IconSm", TokenValueKind.Thickness, "2",
            "contract §3.1 small icon buttons: square padding = space.1"),
        new("Nm.Padding.Tight", TokenValueKind.Thickness, "2",
            "tight inset for compound controls (segmented track) = space.1"),
        new("Nm.Padding.Snug", TokenValueKind.Thickness, "4",
            "snug inset for dense compound rows = space.2"),
        new("Nm.Icon.Stroke", TokenValueKind.Double, "1.25",
            "contract §2.2 + DESIGN_SYSTEM §5: icon stroke width 1.25px"),
        new("Nm.Icon.SizeSmall", TokenValueKind.Double, "16",
            "DESIGN_SYSTEM §5: dense-area icon size 16px"),
        // R-15 extension: a slow exit/reveal duration (220ms) in addition to fast/normal.
        new("Nm.Motion.Duration.Slow", TokenValueKind.TimeSpan, "220ms",
            "R-15 extension: slow duration for 200-260ms reveal/exit transitions"),        new("Nm.Motion.Enabled", TokenValueKind.Boolean, "true",
            "contract §2.2: motion toggle; reduced-motion overlay flips it to false and zeroes durations"),
        // R-14: Nm.LineHeight.Body/Label/Meta/Data are semantic aliases and MUST equal one of the
        // frozen multipliers (Tight 1.25 / Normal 1.45 / Loose 1.6); the generator asserts that rule.
        new("Nm.LineHeight.Display", TokenValueKind.Double, "1.25",
            "R-14 semantic alias: Display uses the frozen Tight multiplier (1.25)"),
        new("Nm.LineHeight.Title", TokenValueKind.Double, "1.25",
            "R-14 semantic alias: Title uses the frozen Tight multiplier (1.25)"),
        new("Nm.LineHeight.Body", TokenValueKind.Double, "1.45",
            "R-14 semantic alias: Body uses the frozen Normal multiplier (1.45)"),
        new("Nm.LineHeight.Label", TokenValueKind.Double, "1.25",
            "R-14 semantic alias: Label uses the frozen Tight multiplier (1.25)"),
        new("Nm.LineHeight.Meta", TokenValueKind.Double, "1.25",
            "R-14 semantic alias: Meta uses the frozen Tight multiplier (1.25)"),
        new("Nm.LineHeight.Data", TokenValueKind.Double, "1.25",
            "R-14 semantic alias: Data uses the frozen Tight multiplier (1.25)"),
        // Avalonia TextBlock.LineHeight is an absolute pixel height, not a multiplier, so the styles
        // consume these derived absolute boxes (font size x the R-14 alias multiplier above).
        new("Nm.TextLineBox.Display", TokenValueKind.Double, "30",
            "DESIGN_SYSTEM §3: 24px font x 1.25 absolute line box for Avalonia TextBlock.LineHeight"),
        new("Nm.TextLineBox.Title", TokenValueKind.Double, "22.5",
            "DESIGN_SYSTEM §3: 18px font x 1.25"),
        new("Nm.TextLineBox.Body", TokenValueKind.Double, "18.85",
            "DESIGN_SYSTEM §3: 13px font x 1.45"),
        new("Nm.TextLineBox.Label", TokenValueKind.Double, "15",
            "DESIGN_SYSTEM §3: 12px font x 1.25 (R-14 alias multiplier)"),
        new("Nm.TextLineBox.Meta", TokenValueKind.Double, "13.75",
            "DESIGN_SYSTEM §3: 11px font x 1.25 (R-14 alias multiplier)"),
        new("Nm.TextLineBox.Data", TokenValueKind.Double, "15",
            "DESIGN_SYSTEM §3: 12px mono font x 1.25 (R-14 alias multiplier)"),
        new("Nm.Size.Marker", TokenValueKind.Double, "16",
            "DESIGN_SYSTEM §6.1 Checkbox/Radio: 16px marker box (hit area stays Nm.Size.ControlHeight)"),
        new("Nm.Size.MarkerCore", TokenValueKind.Double, "8",
            "DESIGN_SYSTEM §6.1 Radio: 8px selected core inside the marker box"),
        new("Nm.Size.ScrollBar", TokenValueKind.Double, "8",
            "DESIGN_SYSTEM §6.1: scrollbar thickness 8px"),
        new("Nm.Opacity.Disabled", TokenValueKind.Double, "0.4",
            "DESIGN_SYSTEM §6.4: disabled HUD actions are 40% opaque"),
        new("Nm.Color.Scrim", TokenValueKind.Brush, "rgba(0,0,0,0.55)",
            "DESIGN_SYSTEM §6.2 Modal: overlay scrim; the frozen baseline defines Modal but no scrim color, so a neutral 55% black scrim is derived (abandoning the layer behind, never decorative)"),
    ];

    /// <summary>
    /// High-contrast overrides per palette. Backgrounds keep the frozen five-level ladder; every
    /// foreground is re-curated so text >= 7:1, status/focus >= 4.5:1 (DESIGN_SYSTEM §2.3).
    /// </summary>
    public static IReadOnlyList<HighContrastColor> HighContrast { get; } =
    [
        new("Nm.Color.Text.Primary", "#FFFFFF", "#000000"),
        new("Nm.Color.Text.Secondary", "#DDE0E4", "#202326"),
        new("Nm.Color.Text.Tertiary", "#C3C8CE", "#3C4045"),
        new("Nm.Color.Text.Disabled", "#9AA0A8", "#5F6368"),
        new("Nm.Color.Text.Inverse", "#0F1012", "#FFFFFF"),

        new("Nm.Color.Line.Subtle", "#3A3F46", "#C9CCCF"),
        new("Nm.Color.Line.Default", "#4E555E", "#A9ADB2"),
        new("Nm.Color.Line.Strong", "#6E7681", "#7D8288"),
        new("Nm.Color.Line.Grid", "#2E3339", "#DCDEE0"),

        new("Nm.Color.Accent.Base", "#FFC46B", "#7A4E00"),
        new("Nm.Color.Accent.Hover", "#FFD08A", "#5F3C00"),
        new("Nm.Color.Accent.Active", "#E8A84E", "#4A2F00"),
        new("Nm.Color.Accent.Muted", "rgba(255,196,107,0.24)", "rgba(122,78,0,0.18)"),
        new("Nm.Color.Accent.On", "#17181A", "#FFFFFF"),
        new("Nm.Color.Accent.Ring", "rgba(255,196,107,0.85)", "rgba(122,78,0,0.70)"),

        new("Nm.Color.Status.Queued", "#C6CCD3", "#4E5257"),
        new("Nm.Color.Status.Running", "#8CC4E8", "#1F4F6E"),
        new("Nm.Color.Status.Done", "#8FD49F", "#1E4A2E"),
        new("Nm.Color.Status.Failed", "#F08A74", "#7A1F0F"),
        new("Nm.Color.Status.Blocked", "#F0BE6B", "#5E4400"),
        new("Nm.Color.Status.Stale", "#C6B4E0", "#4A3D63"),
        new("Nm.Color.Status.Skipped", "#A8AEB5", "#5C6166"),

        new("Nm.Color.StatusMuted.Queued", "rgba(198,204,211,0.22)", "rgba(78,82,87,0.16)"),
        new("Nm.Color.StatusMuted.Running", "rgba(140,196,232,0.22)", "rgba(31,79,110,0.16)"),
        new("Nm.Color.StatusMuted.Done", "rgba(143,212,159,0.22)", "rgba(30,74,46,0.16)"),
        new("Nm.Color.StatusMuted.Failed", "rgba(240,138,116,0.24)", "rgba(122,31,15,0.16)"),
        new("Nm.Color.StatusMuted.Blocked", "rgba(240,190,107,0.22)", "rgba(94,68,0,0.16)"),
        new("Nm.Color.StatusMuted.Stale", "rgba(198,180,224,0.22)", "rgba(74,61,99,0.16)"),
        new("Nm.Color.StatusMuted.Skipped", "rgba(168,174,181,0.20)", "rgba(92,97,102,0.16)"),
    ];

    /// <summary>
    /// Density overrides: the token set stays singular; Compact/Spacious only re-scale control,
    /// row and padding tokens (Comfortable is the frozen baseline itself). Derived extension, see
    /// verification/V11R-D-1/DEVIATIONS.md.
    /// </summary>
    public static IReadOnlyList<DensityToken> Density { get; } =
    [
        new("Nm.Size.TopBand", TokenValueKind.Double, "32", "40"),
        new("Nm.Size.ControlHeight", TokenValueKind.Double, "24", "32"),
        new("Nm.Size.ControlHeightSm", TokenValueKind.Double, "22", "28"),
        new("Nm.Size.RowPage", TokenValueKind.Double, "24", "32"),
        new("Nm.Size.RowBatch", TokenValueKind.Double, "20", "24"),
        new("Nm.Size.RowNormal", TokenValueKind.Double, "22", "30"),
        new("Nm.Padding.Panel", TokenValueKind.Thickness, "8", "16"),
        new("Nm.Padding.Card", TokenValueKind.Thickness, "8", "16"),
        new("Nm.Padding.Control", TokenValueKind.Thickness, "10,6,10,6", "16,10,16,10"),
        new("Nm.Padding.ControlSm", TokenValueKind.Thickness, "6,4,6,4", "10,8,10,8"),
        new("Nm.Padding.Cell", TokenValueKind.Thickness, "6", "10"),
        new("Nm.Padding.Section", TokenValueKind.Thickness, "12", "24"),
    ];

    /// <summary>Resource keys of the whole frozen dark/light color set, in ordinal order.</summary>
    public static IReadOnlyList<string> ThemeColorKeys(IEnumerable<TokenEntry> entries) => entries
        .Where(static entry => entry.Path.StartsWith(DarkScope, StringComparison.Ordinal))
        .Select(static entry => ColorResourceKey(entry.Path))
        .OrderBy(static key => key, StringComparer.Ordinal)
        .ToArray();

    /// <summary>Maps a <c>color.dark.*</c> or <c>color.light.*</c> token path to its <c>Nm.Color.*</c> key.</summary>
    public static string ColorResourceKey(string tokenPath)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(tokenPath);

        var scopeLength = tokenPath.StartsWith(DarkScope, StringComparison.Ordinal) ? DarkScope.Length
            : tokenPath.StartsWith(LightScope, StringComparison.Ordinal) ? LightScope.Length
            : throw new ArgumentException($"'{tokenPath}' is not inside a color theme scope", nameof(tokenPath));

        var segments = tokenPath[scopeLength..].Split('.');
        return Prefix + "Color." + string.Join('.', segments.Select(PascalCaseSegment));
    }

    /// <summary>PascalCases one DTCG path segment (<c>bg</c> -> <c>Bg</c>, <c>2xl</c> -> <c>2Xl</c>).</summary>
    public static string PascalCaseSegment(string segment)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(segment);
        if (segment.Length == 0)
        {
            return segment;
        }

        var characters = segment.ToCharArray();
        var upperNext = true;
        for (var index = 0; index < characters.Length; index++)
        {
            var character = characters[index];
            if (upperNext && char.IsLetter(character))
            {
                characters[index] = char.ToUpperInvariant(character);
                upperNext = false;
            }
            else if (char.IsDigit(character))
            {
                upperNext = true;
            }
            else
            {
                upperNext = false;
            }
        }

        return new string(characters);
    }
}


