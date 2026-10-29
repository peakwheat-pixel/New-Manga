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
/// <see cref="ApplyThemeLayer"/> (contract §4.1 / R-15: 59 whitelisted keys — 35 colors, 3 font
/// families, 6 font sizes, 9 line heights, 3 corner radii, 3 motion durations) or just the color subset
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

    /// <summary>Keys a theme layer may define; anything outside this whitelist is ignored and recorded.</summary>
    public static IReadOnlyList<string> ThemeLayerAllowedKeys => ThemeLayerRequiredKeys;

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
    /// Safe to call twice; the second call re-normalizes a foreign palette provider.
    /// </summary>
    public bool Initialize(AppearanceMode? appearance = null)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (!_listening)
        {
            _application.ActualThemeVariantChanged += OnActualThemeVariantChanged;
            _listening = true;
        }

        if (appearance is not null)
        {
            Appearance = appearance.Value;
        }

        var ok = ApplyRequestedVariant(forceBuiltin: true);
        ok &= SetContrast(Contrast);
        ok &= SetDensity(Density);
        ok &= SetReducedMotion(ReducedMotion);
        IsInitialized = true;
        return ok;
    }

    /// <summary>Switches appearance; the shipped palette for that appearance becomes active (a custom theme layer is dropped).</summary>
    public bool SetAppearance(AppearanceMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        Appearance = mode;
        return ApplyRequestedVariant(forceBuiltin: true);
    }

    /// <summary>
    /// Theme Engine seam (contract §4.1 / R-15): replaces the themeable layer with a whitelisted set of
    /// 59 keys (35 colors + 3 font families + 6 font sizes + 9 line heights + 3 corner radii + 3 motion
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
        return ApplyRequestedVariant(forceBuiltin: true);
    }

    /// <summary>Adds/removes the complete high-contrast palette overlay.</summary>
    public bool SetContrast(ContrastMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        Contrast = mode;
        if (mode == ContrastMode.Standard)
        {
            RemoveOverlay(ref _contrastOverlay);
            return true;
        }

        if (!TryLoadAndRecord(_resources.HighContrastPalette, out var dictionary))
        {
            return false;
        }

        ReplaceOverlay(ref _contrastOverlay, dictionary);
        return true;
    }

    /// <summary>Adds/removes the compact or spacious density overlay.</summary>
    public bool SetDensity(DensityMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        Density = mode;
        if (mode == DensityMode.Comfortable)
        {
            RemoveOverlay(ref _densityOverlay);
            return true;
        }

        var source = mode == DensityMode.Compact ? _resources.CompactDensity : _resources.SpaciousDensity;
        if (!TryLoadAndRecord(source, out var dictionary))
        {
            return false;
        }

        ReplaceOverlay(ref _densityOverlay, dictionary);
        return true;
    }

    /// <summary>Adds/removes the reduced-motion overlay (zeroes every duration, disables motion).</summary>
    public bool SetReducedMotion(bool enabled)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ReducedMotion = enabled;
        if (!enabled)
        {
            RemoveOverlay(ref _motionOverlay);
            return true;
        }

        if (!TryLoadAndRecord(_resources.ReducedMotion, out var dictionary))
        {
            return false;
        }

        ReplaceOverlay(ref _motionOverlay, dictionary);
        return true;
    }

    /// <summary>Restores the shipped defaults without touching any other application resource.</summary>
    public bool ResetToDefaults()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        RemoveOverlay(ref _contrastOverlay);
        RemoveOverlay(ref _densityOverlay);
        RemoveOverlay(ref _motionOverlay);
        Appearance = AppearanceMode.Dark;
        Contrast = ContrastMode.Standard;
        Density = DensityMode.Comfortable;
        ReducedMotion = false;
        return ApplyRequestedVariant(forceBuiltin: true);
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

    private bool ApplyThemeLayerCore(
        ResourceDictionary layer,
        string themeId,
        IReadOnlyList<string> inheritedIssues)
    {
        var issues = new List<string>(inheritedIssues);
        var filtered = new ResourceDictionary();
        foreach (var (key, value) in ReadEntries(layer))
        {
            if (ThemeLayerAllowedKeys.Contains(key, StringComparer.Ordinal))
            {
                filtered[key] = value;
            }
            else
            {
                issues.Add($"ignored key '{key}' from theme layer '{themeId}': outside the R-15 59-key whitelist");
            }
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
        return true;
    }

    private bool TryResolveApplicationValue(string key, out object? value)
    {
        foreach (var provider in _application.Resources.MergedDictionaries)
        {
            if (provider.TryGetResource(key, ThemeVariant.Default, out value) ||
                provider.TryGetResource(key, _application.ActualThemeVariant, out value))
            {
                return true;
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

    private bool ApplyRequestedVariant(bool forceBuiltin)
    {
        _application.RequestedThemeVariant = Appearance switch
        {
            AppearanceMode.Light => ThemeVariant.Light,
            AppearanceMode.Dark => ThemeVariant.Dark,
            _ => ThemeVariant.Default,
        };

        return ApplyPaletteForActualVariant(forceBuiltin);
    }

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
        ReorderOverlays();
    }

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

    private void ReplaceOverlay(ref ResourceDictionary? slot, ResourceDictionary? dictionary)
    {
        RemoveOverlay(ref slot);
        if (dictionary is null)
        {
            return;
        }

        _application.Resources.MergedDictionaries.Add(dictionary);
        slot = dictionary;
        ReorderOverlays();
    }

    private void RemoveOverlay(ref ResourceDictionary? slot)
    {
        if (slot is not null)
        {
            _application.Resources.MergedDictionaries.Remove(slot);
            slot = null;
        }
    }

    /// <summary>
    /// Keeps the precedence deterministic: palette/theme layer first, then contrast, density and motion
    /// overlays, so an appearance switch can never re-order a high-contrast palette underneath the base
    /// palette and a density overlay always wins over the theme layer.
    /// </summary>
    private void ReorderOverlays()
    {
        var ordered = new List<ResourceDictionary>(3);
        if (_contrastOverlay is not null)
        {
            ordered.Add(_contrastOverlay);
        }

        if (_densityOverlay is not null)
        {
            ordered.Add(_densityOverlay);
        }

        if (_motionOverlay is not null)
        {
            ordered.Add(_motionOverlay);
        }

        if (ordered.Count == 0)
        {
            return;
        }

        if (_palette is not null)
        {
            var index = _application.Resources.MergedDictionaries.IndexOf(_palette);
            if (index > 0)
            {
                _application.Resources.MergedDictionaries.Remove(_palette);
                _application.Resources.MergedDictionaries.Insert(0, _palette);
            }
        }

        foreach (var overlay in ordered)
        {
            _application.Resources.MergedDictionaries.Remove(overlay);
        }

        foreach (var overlay in ordered)
        {
            _application.Resources.MergedDictionaries.Add(overlay);
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
