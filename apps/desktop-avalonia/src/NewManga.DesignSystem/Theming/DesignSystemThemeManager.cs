using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Styling;

namespace NewManga.DesignSystem.Theming;

/// <summary>
/// Applies the design system to a running Avalonia application by swapping resource dictionaries in
/// <see cref="Application.Resources"/> — never by recreating the visual tree (AC7). Appearance swaps
/// the palette dictionary, contrast/density/reduced-motion append or remove overlay dictionaries.
/// Failures to load or validate a dictionary are reported through <see cref="LastError"/> and leave the
/// previous state intact: the manager builds and validates the replacement layer first and only then
/// performs an atomic swap (AC9).
///
/// <para>
/// Boundary with the Theme Engine (V11R-C-1 Part B): the design system owns tokens, styles, controls
/// and the mechanism that applies a dictionary to the running application; the theme engine owns theme
/// semantics (packages, registry, persistence, preview). The engine feeds a theme layer through
/// <see cref="ApplyThemeLayer"/> (contract §4.1 / R-15: 59 required keys — 35 colors, 3 font
/// families, 6 font sizes, 9 line heights, 3 corner radii, 3 motion durations; the six absolute
/// <c>Nm.TextLineBox.*</c> keys are optional and derived from the layer's own sizes/multipliers when
/// omitted) or just the color subset
/// through <see cref="ApplyPalette"/>, and restores the shipped look with <see cref="RevertPalette"/>.
/// </para>
/// </summary>
public sealed class DesignSystemThemeManager : IDisposable
{
    /// <summary>Key probed to detect a palette provider in <see cref="Application.Resources"/>.</summary>
    public const string PaletteProbeKey = "Nm.Color.Bg.Canvas";

    /// <summary>Key probed to detect the theme-invariant token dictionary.</summary>
    public const string GlobalProbeKey = "Nm.Space.3";

    /// <summary>Palette id reported while the shipped dark appearance palette is applied.</summary>
    public const string BuiltinDarkPaletteId = "builtin.dark";

    /// <summary>Palette id reported while the shipped light appearance palette is applied.</summary>
    public const string BuiltinLightPaletteId = "builtin.light";

    /// <summary>Font-family keys a theme layer carries (R-15).</summary>
    public static IReadOnlyList<string> ThemeLayerFontKeys { get; } =
    [
        NmKeys.FontFamily.Ui,
        NmKeys.FontFamily.Data,
        NmKeys.FontFamily.Display,
    ];

    /// <summary>Font-size keys a theme layer carries (R-15).</summary>
    public static IReadOnlyList<string> ThemeLayerFontSizeKeys { get; } =
    [
        NmKeys.FontSize.Xs,
        NmKeys.FontSize.Sm,
        NmKeys.FontSize.Md,
        NmKeys.FontSize.Lg,
        NmKeys.FontSize.Xl,
        NmKeys.FontSize.Xxl,
    ];

    /// <summary>Line-height keys a theme layer carries (R-15: 3 multipliers + 6 semantic aliases).</summary>
    public static IReadOnlyList<string> ThemeLayerLineHeightKeys { get; } =
    [
        NmKeys.LineHeight.Tight,
        NmKeys.LineHeight.Normal,
        NmKeys.LineHeight.Loose,
        NmKeys.LineHeight.Display,
        NmKeys.LineHeight.Title,
        NmKeys.LineHeight.Body,
        NmKeys.LineHeight.Label,
        NmKeys.LineHeight.Meta,
        NmKeys.LineHeight.Data,
    ];

    /// <summary>Absolute line-box keys the text styles consume (Avalonia LineHeight is px, not a multiplier).</summary>
    public static IReadOnlyList<string> ThemeLayerLineBoxKeys { get; } =
    [
        NmKeys.TextLineBox.Display,
        NmKeys.TextLineBox.Title,
        NmKeys.TextLineBox.Body,
        NmKeys.TextLineBox.Label,
        NmKeys.TextLineBox.Meta,
        NmKeys.TextLineBox.Data,
    ];

    /// <summary>Corner-radius keys a theme layer carries (R-15).</summary>
    public static IReadOnlyList<string> ThemeLayerCornerKeys { get; } =
    [
        NmKeys.Corner.None,
        NmKeys.Corner.Sm,
        NmKeys.Corner.Md,
    ];

    /// <summary>Motion-duration keys a theme layer carries (R-15: fast/normal/slow).</summary>
    public static IReadOnlyList<string> ThemeLayerMotionKeys { get; } =
    [
        NmKeys.Motion.Duration.Fast,
        NmKeys.Motion.Duration.Normal,
        NmKeys.Motion.Duration.Slow,
    ];

    /// <summary>
    /// Every color key a complete palette must define (contract §2.2 color groups). Theme-invariant
    /// derived colors (e.g. <c>Nm.Color.Scrim</c>, which lives in the global token dictionary and is not
    /// part of any appearance palette) are excluded: a palette layer never carries them.
    /// </summary>
    public static IReadOnlyList<string> PaletteColorKeys { get; } = NmKeys.All
        .Where(static key =>
            key.StartsWith("Nm.Color.", StringComparison.Ordinal) &&
            !string.Equals(key, NmKeys.Color.Scrim, StringComparison.Ordinal))
        .ToArray();

    /// <summary>All 59 keys a theme layer must define (contract §4.1 / R-15).</summary>
    public static IReadOnlyList<string> ThemeLayerRequiredKeys { get; } =
        PaletteColorKeys
            .Concat(ThemeLayerFontKeys)
            .Concat(ThemeLayerFontSizeKeys)
            .Concat(ThemeLayerLineHeightKeys)
            .Concat(ThemeLayerCornerKeys)
            .Concat(ThemeLayerMotionKeys)
            .ToArray();

    /// <summary>
    /// Keys a theme layer may define: the 59 required keys plus the six absolute line boxes. The line
    /// boxes may be supplied explicitly; when omitted the manager derives them from the layer's own font
    /// sizes and line-height multipliers so text styles always read consistent values. Anything else is
    /// ignored and recorded.
    /// </summary>
    public static IReadOnlyList<string> ThemeLayerAllowedKeys { get; } =
        ThemeLayerRequiredKeys.Concat(ThemeLayerLineBoxKeys).ToArray();

    private readonly Application _application;
    private readonly IDesignSystemResourceSource _resources;

    private ResourceDictionary? _palette;
    private bool _paletteIsLight;
    private bool _paletteIsBuiltin = true;
    private string? _themeLayerId;
    private ResourceDictionary? _contrastOverlay;
    private ResourceDictionary? _densityOverlay;
    private ResourceDictionary? _motionOverlay;
    private bool _listening;
    private bool _disposed;
    private string? _lastError;

    /// <summary>Creates a manager bound to one application instance.</summary>
    public DesignSystemThemeManager(Application application, IDesignSystemResourceSource? resources = null)
    {
        _application = application ?? throw new ArgumentNullException(nameof(application));
        _resources = resources ?? DesignSystemResourceSource.Default;
    }

    /// <summary>Requested appearance (defaults to the frozen A+C baseline: dark).</summary>
    public AppearanceMode Appearance { get; private set; } = AppearanceMode.Dark;

    public ContrastMode Contrast { get; private set; } = ContrastMode.Standard;

    public DensityMode Density { get; private set; } = DensityMode.Comfortable;

    public bool ReducedMotion { get; private set; }

    /// <summary>Last resource-load/validation failure, if any. Never thrown at the caller (AC9).</summary>
    public string? LastError
    {
        get => _lastError;
        private set => _lastError = value;
    }

    /// <summary>
    /// Non-fatal issues recorded by the last theme-layer application: keys outside the R-15 whitelist
    /// are ignored (never applied) and reported here for the Theme Studio diagnostics surface.
    /// </summary>
    public IReadOnlyList<string> ThemeLayerIssues { get; private set; } = [];

    public bool IsInitialized { get; private set; }

    /// <summary>
    /// Id of the palette currently applied: <see cref="BuiltinDarkPaletteId"/> /
    /// <see cref="BuiltinLightPaletteId"/> for the shipped appearance palettes, otherwise the id the
    /// Theme Engine supplied through <see cref="ApplyThemeLayer"/> / <see cref="ApplyPalette"/>.
    /// </summary>
    public string? AppliedPaletteId { get; private set; }

    /// <summary>Id of the applied theme layer, or null when the shipped layers are active.</summary>
    public string? AppliedThemeLayerId => _themeLayerId;

    /// <summary>
    /// Ensures the token dictionaries exist, then applies the current settings. An optional
    /// <paramref name="appearance"/> lets the host pass the persisted/user startup choice; when omitted
    /// the frozen default (dark) is used, so initialization never silently overrides a known choice.
    /// All dictionaries are loaded before any state is committed: a failure leaves the manager and the
    /// application resource stack untouched.
    /// </summary>
    public bool Initialize(AppearanceMode? appearance = null)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        var mode = appearance ?? Appearance;
        if (!TryLoadPaletteFor(mode, out var palette, out var isLight))
        {
            return false;
        }

        var needsGlobalTokens = !AnyProviderHasKey(GlobalProbeKey);
        ResourceDictionary? globalTokens = null;
        if (needsGlobalTokens && !TryLoadAndRecord(_resources.GlobalTokens, out globalTokens))
        {
            return false;
        }

        ResourceDictionary? contrast = null;
        ResourceDictionary? density = null;
        ResourceDictionary? motion = null;
        if (Contrast != ContrastMode.Standard &&
            !TryLoadAndRecord(_resources.HighContrastPalette, out contrast))
        {
            return false;
        }

        if (Density != DensityMode.Comfortable &&
            !TryLoadAndRecord(DensitySource(Density), out density))
        {
            return false;
        }

        if (ReducedMotion && !TryLoadAndRecord(_resources.ReducedMotion, out motion))
        {
            return false;
        }

        // ---- Commit (no failure can happen past this point) --------------------------------
        if (!_listening)
        {
            _application.ActualThemeVariantChanged += OnActualThemeVariantChanged;
            _listening = true;
        }

        _application.RequestedThemeVariant = VariantFor(mode);
        Appearance = mode;
        if (needsGlobalTokens && globalTokens is not null)
        {
            _application.Resources.MergedDictionaries.Add(globalTokens);
        }

        SwapPalette(palette!, isLight, BuiltinPaletteId(isLight), isBuiltin: true, themeLayerId: null);
        CommitOverlay(ref _contrastOverlay, contrast);
        CommitOverlay(ref _densityOverlay, density);
        CommitOverlay(ref _motionOverlay, motion);
        ReorderResourceStack();
        ThemeLayerIssues = [];
        LastError = null;
        IsInitialized = true;
        return true;
    }

    /// <summary>
    /// Switches appearance; the shipped palette for that appearance becomes active (a custom theme layer
    /// is dropped). The target palette is loaded and validated before the request/state is changed, so a
    /// failed switch keeps the previous appearance and resources intact.
    /// </summary>
    public bool SetAppearance(AppearanceMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (!TryLoadPaletteFor(mode, out var palette, out var isLight))
        {
            return false;
        }

        if (!EnsureGlobalTokens())
        {
            return false;
        }

        _application.RequestedThemeVariant = VariantFor(mode);
        Appearance = mode;
        SwapPalette(palette!, isLight, BuiltinPaletteId(isLight), isBuiltin: true, themeLayerId: null);
        ThemeLayerIssues = [];
        LastError = null;
        return true;
    }

    /// <summary>
    /// Theme Engine seam (contract §4.1 / R-15): replaces the themeable layer with a whitelisted set of
    /// 59 required keys (35 colors + 3 font families + 6 font sizes + 9 line heights + 3 corner radii + 3 motion
    /// durations). Keys outside the whitelist are ignored and reported in
    /// <see cref="ThemeLayerIssues"/>; material/elevation keys are not part of the frozen whitelist.
    /// The previous state is kept if the layer is incomplete or a value has the wrong type.
    /// </summary>
    public bool ApplyThemeLayer(ResourceDictionary layer, string themeId)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ArgumentNullException.ThrowIfNull(layer);
        return ApplyThemeLayerCore(layer, RequireId(themeId), []);
    }

    /// <summary>
    /// Color-only convenience over <see cref="ApplyThemeLayer"/>: the theme engine migrates the 35
    /// color keys and the remaining 24 non-color keys are inherited from the currently loaded theme
    /// tokens, so a palette swap never accidentally resets typography/motion/corners.
    /// </summary>
    public bool ApplyPalette(ResourceDictionary palette, string paletteId)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ArgumentNullException.ThrowIfNull(palette);

        var id = RequireId(paletteId);
        var issues = new List<string>();
        var complete = new ResourceDictionary();
        var entries = ReadEntries(palette);
        foreach (var (key, value) in entries)
        {
            if (PaletteColorKeys.Contains(key, StringComparer.Ordinal))
            {
                complete[key] = value;
            }
            else
            {
                issues.Add($"ignored key '{key}' from palette '{id}': ApplyPalette only accepts the 35 color keys");
            }
        }

        var missingColors = PaletteColorKeys
            .Where(key => !entries.Any(entry => string.Equals(entry.Key, key, StringComparison.Ordinal)))
            .Take(10)
            .ToArray();
        if (missingColors.Length > 0)
        {
            LastError = $"palette '{id}' is missing {missingColors.Length} color key(s): {string.Join(", ", missingColors)}";
            return false;
        }

        foreach (var key in ThemeLayerRequiredKeys.Where(key => !PaletteColorKeys.Contains(key, StringComparer.Ordinal)))
        {
            if (!TryResolveApplicationValue(key, out var value))
            {
                LastError =
                    $"palette '{id}' cannot inherit theme-layer key '{key}': load the design-system tokens first";
                return false;
            }

            complete[key] = value!;
        }

        return ApplyThemeLayerCore(complete, id, issues);
    }

    /// <summary>Restores the shipped built-in palette (and drops any theme layer) for the current appearance.</summary>
    public bool RevertPalette()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return SetAppearance(Appearance);
    }

    /// <summary>Adds/removes the complete high-contrast palette overlay.</summary>
    public bool SetContrast(ContrastMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (mode == ContrastMode.Standard)
        {
            CommitOverlay(ref _contrastOverlay, null);
            Contrast = mode;
            LastError = null;
            return true;
        }

        // Load before mutating: a broken overlay must not change Contrast or the stack.
        if (!TryLoadAndRecord(_resources.HighContrastPalette, out var dictionary))
        {
            return false;
        }

        CommitOverlay(ref _contrastOverlay, dictionary);
        Contrast = mode;
        LastError = null;
        return true;
    }

    /// <summary>Adds/removes the compact or spacious density overlay.</summary>
    public bool SetDensity(DensityMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (mode == DensityMode.Comfortable)
        {
            CommitOverlay(ref _densityOverlay, null);
            Density = mode;
            LastError = null;
            return true;
        }

        if (!TryLoadAndRecord(DensitySource(mode), out var dictionary))
        {
            return false;
        }

        CommitOverlay(ref _densityOverlay, dictionary);
        Density = mode;
        LastError = null;
        return true;
    }

    /// <summary>Adds/removes the reduced-motion overlay (zeroes every duration, disables motion).</summary>
    public bool SetReducedMotion(bool enabled)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (!enabled)
        {
            CommitOverlay(ref _motionOverlay, null);
            ReducedMotion = false;
            LastError = null;
            return true;
        }

        if (!TryLoadAndRecord(_resources.ReducedMotion, out var dictionary))
        {
            return false;
        }

        CommitOverlay(ref _motionOverlay, dictionary);
        ReducedMotion = true;
        LastError = null;
        return true;
    }

    /// <summary>Restores the shipped defaults without touching any other application resource.</summary>
    public bool ResetToDefaults()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (!TryLoadPaletteFor(AppearanceMode.Dark, out var palette, out var isLight))
        {
            return false;
        }

        if (!EnsureGlobalTokens())
        {
            return false;
        }

        CommitOverlay(ref _contrastOverlay, null);
        CommitOverlay(ref _densityOverlay, null);
        CommitOverlay(ref _motionOverlay, null);
        _application.RequestedThemeVariant = ThemeVariant.Dark;
        Appearance = AppearanceMode.Dark;
        Contrast = ContrastMode.Standard;
        Density = DensityMode.Comfortable;
        ReducedMotion = false;
        SwapPalette(palette!, isLight, BuiltinPaletteId(isLight), isBuiltin: true, themeLayerId: null);
        ThemeLayerIssues = [];
        LastError = null;
        return true;
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        if (_listening)
        {
            _application.ActualThemeVariantChanged -= OnActualThemeVariantChanged;
            _listening = false;
        }

        _disposed = true;
    }

    /// <summary>
    /// Loads one compiled resource dictionary; returns false instead of throwing when the dictionary
    /// is missing or malformed (AC9 fallback contract).
    /// </summary>
    public static bool TryLoad(Uri uri, out ResourceDictionary? dictionary)
    {
        ArgumentNullException.ThrowIfNull(uri);
        try
        {
            dictionary = AvaloniaXamlLoader.Load(uri) as ResourceDictionary;
            return dictionary is not null;
        }
        catch (Exception)
        {
            dictionary = null;
            return false;
        }
    }

    private static string RequireId(string id) =>
        string.IsNullOrWhiteSpace(id) ? "unnamed" : id;

    /// <summary>
    /// Derivation table for the absolute line boxes the text styles consume. The theme layer carries the
    /// multipliers (R-15 line-height group); the manager multiplies them by the layer's own font sizes so
    /// styles never read a stale absolute value after a theme switch (I2/P2-①).
    /// </summary>
    private static readonly (string LineBoxKey, string FontSizeKey, string LineHeightKey)[] LineBoxDerivations =
    [
        (NmKeys.TextLineBox.Display, NmKeys.FontSize.Xxl, NmKeys.LineHeight.Display),
        (NmKeys.TextLineBox.Title, NmKeys.FontSize.Xl, NmKeys.LineHeight.Title),
        (NmKeys.TextLineBox.Body, NmKeys.FontSize.Md, NmKeys.LineHeight.Body),
        (NmKeys.TextLineBox.Label, NmKeys.FontSize.Sm, NmKeys.LineHeight.Label),
        (NmKeys.TextLineBox.Meta, NmKeys.FontSize.Xs, NmKeys.LineHeight.Meta),
        (NmKeys.TextLineBox.Data, NmKeys.FontSize.Sm, NmKeys.LineHeight.Data),
    ];

    private bool ApplyThemeLayerCore(
        ResourceDictionary layer,
        string themeId,
        IReadOnlyList<string> inheritedIssues)
    {
        var issues = new List<string>(inheritedIssues);
        var entries = new Dictionary<string, object?>(StringComparer.Ordinal);
        foreach (var (key, value) in ReadEntries(layer))
        {
            if (ThemeLayerAllowedKeys.Contains(key, StringComparer.Ordinal))
            {
                entries[key] = value;
            }
            else
            {
                issues.Add(
                    $"ignored key '{key}' from theme layer '{themeId}': outside the R-15 59-key whitelist " +
                    "or the six absolute line-box keys");
            }
        }

        if (!TryDeriveLineBoxes(entries, themeId, out var lineBoxError))
        {
            LastError = lineBoxError;
            return false;
        }

        var filtered = new ResourceDictionary();
        foreach (var (key, value) in entries)
        {
            filtered[key] = value;
        }

        if (!ValidateValues(filtered, themeId, ThemeLayerRequiredKeys, out var error))
        {
            LastError = error;
            return false;
        }

        // Ensure the theme-invariant tokens exist before any provider is touched (atomic swap).
        if (!EnsureGlobalTokens())
        {
            return false;
        }

        SwapPalette(filtered, IsLightConfigured(), themeId, isBuiltin: false, themeLayerId: themeId);
        ThemeLayerIssues = issues;
        LastError = null;
        return true;
    }

    /// <summary>Contract floor for the <c>Nm.LineHeight.*</c> aliases (multipliers, never pixels).</summary>
    private const double MinLineHeightMultiplier = 1.0;

    /// <summary>Upper bound of the frozen multiplier range; larger values mean pixels leaked into an alias.</summary>
    private const double MaxLineHeightMultiplier = 2.5;

    /// <summary>
    /// Fills in any missing absolute line box from the layer's font size and multiplier. Explicit line
    /// boxes are validated instead of silently overwritten.
    /// </summary>
    private static bool TryDeriveLineBoxes(
        IDictionary<string, object?> entries,
        string themeId,
        out string? error)
    {
        // C-2-I1 guard: a layer that carries absolute pixels (e.g. 16.2) in the alias keys would be
        // multiplied by the font size again below and inflate every line box. Reject it instead of
        // silently applying a broken layer; the manager keeps the previous palette.
        foreach (var key in ThemeLayerLineHeightKeys)
        {
            if (!entries.TryGetValue(key, out var value))
            {
                continue;
            }

            if (value is not double multiplier)
            {
                error = $"theme layer '{themeId}': '{key}' must be a double";
                return false;
            }

            if (multiplier is < MinLineHeightMultiplier or > MaxLineHeightMultiplier)
            {
                error =
                    $"theme layer '{themeId}': '{key}' is {multiplier}; line-height aliases must stay within " +
                    $"[{MinLineHeightMultiplier}, {MaxLineHeightMultiplier}] (absolute pixels belong in Nm.TextLineBox.*)";
                return false;
            }
        }

        foreach (var (lineBoxKey, fontSizeKey, lineHeightKey) in LineBoxDerivations)
        {
            if (entries.TryGetValue(lineBoxKey, out var supplied))
            {
                if (supplied is not double)
                {
                    error = $"theme layer '{themeId}': '{lineBoxKey}' must be a double";
                    return false;
                }

                continue;
            }

            if (!entries.TryGetValue(fontSizeKey, out var sizeValue) ||
                sizeValue is not double size ||
                !entries.TryGetValue(lineHeightKey, out var lineHeightValue) ||
                lineHeightValue is not double lineHeight)
            {
                error =
                    $"theme layer '{themeId}': cannot derive '{lineBoxKey}' because " +
                    $"'{fontSizeKey}' or '{lineHeightKey}' is missing";
                return false;
            }

            entries[lineBoxKey] = size * lineHeight;
        }

        error = null;
        return true;
    }

    private bool ValidateValues(
        ResourceDictionary dictionary,
        string id,
        IReadOnlyList<string> requiredKeys,
        out string? error)
    {
        var invalid = new List<string>();
        var entries = ReadEntries(dictionary).ToDictionary(static entry => entry.Key, static entry => entry.Value, StringComparer.Ordinal);
        foreach (var key in requiredKeys)
        {
            if (!entries.TryGetValue(key, out var value) || !HasExpectedType(key, value))
            {
                invalid.Add(key);
            }
        }

        if (invalid.Count > 0)
        {
            error =
                $"'{id}' is not a complete theme layer: {invalid.Count} key(s) missing or with the wrong value type " +
                $"({string.Join(", ", invalid.Take(5))}{(invalid.Count > 5 ? ", ..." : string.Empty)})";
            return false;
        }

        error = null;
        return true;
    }

    private static bool HasExpectedType(string key, object? value) => value switch
    {
        null => false,
        _ when key.StartsWith("Nm.Color.", StringComparison.Ordinal) => value is IBrush,
        _ when key.StartsWith("Nm.FontFamily.", StringComparison.Ordinal) => value is FontFamily,
        _ when key.StartsWith("Nm.FontSize.", StringComparison.Ordinal) => value is double,
        _ when key.StartsWith("Nm.LineHeight.", StringComparison.Ordinal) => value is double,
        _ when key.StartsWith("Nm.TextLineBox.", StringComparison.Ordinal) => value is double,
        _ when key.StartsWith("Nm.Corner.", StringComparison.Ordinal) => value is CornerRadius,
        _ when key.StartsWith("Nm.Motion.Duration.", StringComparison.Ordinal) => value is TimeSpan,
        _ => false,
    };

    private static IReadOnlyList<(string Key, object? Value)> ReadEntries(ResourceDictionary dictionary)
    {
        var entries = new List<(string Key, object? Value)>();
        if (dictionary is IDictionary<object, object> map)
        {
            foreach (var pair in map)
            {
                if (pair.Key is string key)
                {
                    entries.Add((key, pair.Value));
                }
            }

            return entries;
        }

        foreach (var key in dictionary.Keys.OfType<string>())
        {
            entries.Add((key, null));
        }

        return entries;
    }

    private bool EnsureGlobalTokens()
    {
        if (AnyProviderHasKey(GlobalProbeKey))
        {
            return true;
        }

        if (!TryLoadAndRecord(_resources.GlobalTokens, out var global))
        {
            return false;
        }

        _application.Resources.MergedDictionaries.Add(global!);
        ReorderResourceStack();
        return true;
    }

    /// <summary>
    /// Resolves a value from the <em>effective</em> resource stack (last provider wins), not from the
    /// first provider that happens to contain the key. Palette-only application must preserve the active
    /// theme layer's typography instead of re-reading the base global dictionary (I2/P2-③).
    /// </summary>
    private bool TryResolveApplicationValue(string key, out object? value)
    {
        var providers = _application.Resources.MergedDictionaries;
        for (var index = providers.Count - 1; index >= 0; index--)
        {
            var provider = providers[index];
            if (provider.TryGetResource(key, ThemeVariant.Default, out value) ||
                provider.TryGetResource(key, _application.ActualThemeVariant, out value))
            {
                if (value is not null)
                {
                    return true;
                }
            }
        }

        value = null;
        return false;
    }

    /// <summary>Loads and records <see cref="LastError"/> on failure while keeping the previous state.</summary>
    private bool TryLoadAndRecord(Uri uri, out ResourceDictionary? dictionary)
    {
        if (TryLoad(uri, out dictionary))
        {
            return true;
        }

        LastError = $"failed to load design-system resource dictionary '{uri}'";
        return false;
    }

    private void OnActualThemeVariantChanged(object? sender, EventArgs e)
    {
        if (_disposed || Appearance != AppearanceMode.System)
        {
            return;
        }

        ApplyPaletteForActualVariant(forceBuiltin: false);
    }

    private static ThemeVariant VariantFor(AppearanceMode mode) => mode switch
    {
        AppearanceMode.Light => ThemeVariant.Light,
        AppearanceMode.Dark => ThemeVariant.Dark,
        _ => ThemeVariant.Default,
    };

    private bool TryLoadPaletteFor(AppearanceMode mode, out ResourceDictionary? palette, out bool isLight)
    {
        isLight = mode switch
        {
            AppearanceMode.Light => true,
            AppearanceMode.Dark => false,
            _ => _application.ActualThemeVariant == ThemeVariant.Light,
        };

        return TryLoadAndRecord(isLight ? _resources.LightPalette : _resources.DarkPalette, out palette);
    }

    private Uri DensitySource(DensityMode mode) =>
        mode == DensityMode.Compact ? _resources.CompactDensity : _resources.SpaciousDensity;

    private bool ApplyPaletteForActualVariant(bool forceBuiltin)
    {
        var isLight = IsLightConfigured();
        if (!forceBuiltin && _palette is not null && _paletteIsBuiltin && _paletteIsLight == isLight)
        {
            AppliedPaletteId = BuiltinPaletteId(isLight);
            return true;
        }

        var source = isLight ? _resources.LightPalette : _resources.DarkPalette;
        if (!TryLoadAndRecord(source, out var palette))
        {
            return false;
        }

        // Load the theme-invariant tokens before touching the palette provider (atomic swap).
        if (!EnsureGlobalTokens())
        {
            return false;
        }

        SwapPalette(palette!, isLight, BuiltinPaletteId(isLight), isBuiltin: true, themeLayerId: null);
        ThemeLayerIssues = [];
        LastError = null;
        return true;
    }

    /// <summary>
    /// Atomic swap: the replacement layer has already been loaded, filtered and validated, and the
    /// theme-invariant tokens are ensured by the caller <em>before</em> any provider is removed. A
    /// failed global load therefore aborts the swap and leaves the previous layer untouched.
    /// </summary>
    private void SwapPalette(
        ResourceDictionary palette,
        bool isLight,
        string paletteId,
        bool isBuiltin,
        string? themeLayerId)
    {
        RemovePaletteProviders();
        _application.Resources.MergedDictionaries.Add(palette);
        _palette = palette;
        _paletteIsLight = isLight;
        _paletteIsBuiltin = isBuiltin;
        _themeLayerId = themeLayerId;
        AppliedPaletteId = paletteId;
        ReorderResourceStack();
    }

    /// <summary>
    /// Removes the previous dedicated palette/theme-layer provider only. Providers that also carry the
    /// theme-invariant tokens (the App.axaml aggregate dictionary) are never removed: doing so used to
    /// drop spacing/font/Scrim tokens after an appearance switch (I2/P1-1). Global tokens stay in front
    /// of the palette, so the freshly added palette still wins for every color key.
    /// </summary>
    private void RemovePaletteProviders()
    {
        foreach (var provider in _application.Resources.MergedDictionaries.ToArray())
        {
            // Overlays (high contrast, density, reduced motion) are tracked separately and must survive
            // an appearance/theme-layer switch; only the current palette/theme layer is replaced.
            if (ReferenceEquals(provider, _contrastOverlay) ||
                ReferenceEquals(provider, _densityOverlay) ||
                ReferenceEquals(provider, _motionOverlay))
            {
                continue;
            }

            if (ProviderHasKey(provider, GlobalProbeKey))
            {
                continue;
            }

            if (ProviderHasKey(provider, PaletteProbeKey))
            {
                _application.Resources.MergedDictionaries.Remove(provider);
            }
        }

        _palette = null;
    }

    private bool IsLightConfigured() => Appearance switch
    {
        AppearanceMode.Light => true,
        AppearanceMode.Dark => false,
        _ => _application.ActualThemeVariant == ThemeVariant.Light,
    };

    private static string BuiltinPaletteId(bool isLight) =>
        isLight ? BuiltinLightPaletteId : BuiltinDarkPaletteId;

    private void CommitOverlay(ref ResourceDictionary? slot, ResourceDictionary? dictionary)
    {
        if (slot is not null)
        {
            _application.Resources.MergedDictionaries.Remove(slot);
        }

        slot = dictionary;
        if (dictionary is not null)
        {
            _application.Resources.MergedDictionaries.Add(dictionary);
        }

        ReorderResourceStack();
    }

    /// <summary>
    /// Deterministic precedence for every token lookup (<em>last provider wins</em>):
    /// foreign dictionaries → global/aggregate token dictionaries → palette/theme layer → contrast →
    /// density → reduced-motion overlays. This guarantees a theme layer's fonts/sizes are not shadowed by
    /// an independent Global provider and that every overlay stays on top (I2/P2-②).
    /// </summary>
    private void ReorderResourceStack()
    {
        var providers = _application.Resources.MergedDictionaries.ToList();

        bool IsOverlay(IResourceProvider provider) =>
            ReferenceEquals(provider, _contrastOverlay) ||
            ReferenceEquals(provider, _densityOverlay) ||
            ReferenceEquals(provider, _motionOverlay);

        bool IsGlobal(IResourceProvider provider) =>
            !IsOverlay(provider) && ProviderHasKey(provider, GlobalProbeKey);

        bool IsPalette(IResourceProvider provider) =>
            !IsOverlay(provider) && !IsGlobal(provider) && ProviderHasKey(provider, PaletteProbeKey);

        var foreign = providers.Where(provider => !IsOverlay(provider) && !IsGlobal(provider) && !IsPalette(provider)).ToList();
        var globals = providers.Where(IsGlobal).ToList();
        var palette = _palette is not null && providers.Contains(_palette) && !globals.Contains(_palette)
            ? new List<IResourceProvider> { _palette }
            : [];
        // A stale palette provider that is no longer tracked must still sit after global tokens so an
        // old provider can never shadow the fresh one. It is removed on the next palette swap.
        var stalePalettes = providers
            .Where(provider => IsPalette(provider) && !ReferenceEquals(provider, _palette))
            .ToList();
        var overlays = new List<IResourceProvider>(3);
        if (_contrastOverlay is not null)
        {
            overlays.Add(_contrastOverlay);
        }

        if (_densityOverlay is not null)
        {
            overlays.Add(_densityOverlay);
        }

        if (_motionOverlay is not null)
        {
            overlays.Add(_motionOverlay);
        }

        var ordered = foreign
            .Concat(globals)
            .Concat(palette)
            .Concat(stalePalettes)
            .Concat(overlays)
            .ToList();

        if (ordered.Count != providers.Count)
        {
            ordered.AddRange(providers.Where(provider => !ordered.Contains(provider)));
        }

        if (ordered.SequenceEqual(providers))
        {
            return;
        }

        _application.Resources.MergedDictionaries.Clear();
        foreach (var provider in ordered)
        {
            _application.Resources.MergedDictionaries.Add(provider);
        }
    }

    private bool AnyProviderHasKey(string key)
    {
        foreach (var provider in _application.Resources.MergedDictionaries)
        {
            if (ProviderHasKey(provider, key))
            {
                return true;
            }
        }

        return false;
    }

    private static bool ProviderHasKey(IResourceProvider provider, string key) =>
        provider.TryGetResource(key, ThemeVariant.Default, out _);
}


