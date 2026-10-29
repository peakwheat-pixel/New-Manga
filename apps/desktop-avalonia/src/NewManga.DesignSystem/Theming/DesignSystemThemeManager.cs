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
/// Failures to load a dictionary are reported through <see cref="LastError"/> and leave the previous
/// state intact (AC9).
///
/// <para>
/// Boundary with the Theme Engine (V11R-C-1): the design system owns tokens, styles, controls and the
/// mechanism that applies a dictionary to the running application; the theme engine owns theme
/// semantics (packages, registry, persistence, preview). The engine feeds a complete palette in through
/// <see cref="ApplyPalette"/> and can restore the shipped palette with <see cref="RevertPalette"/>.
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

    /// <summary>Every color key a complete palette must define (contract §2.2 color groups).</summary>
    public static IReadOnlyList<string> PaletteColorKeys { get; } = NmKeys.All
        .Where(static key => key.StartsWith("Nm.Color.", StringComparison.Ordinal))
        .ToArray();

    private readonly Application _application;
    private readonly IDesignSystemResourceSource _resources;

    private ResourceDictionary? _palette;
    private bool _paletteIsLight;
    private bool _paletteIsBuiltin = true;
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

    /// <summary>Last resource-load failure, if any. Never thrown at the caller (AC9).</summary>
    public string? LastError
    {
        get => _lastError;
        private set => _lastError = value;
    }

    public bool IsInitialized { get; private set; }

    /// <summary>
    /// Id of the palette currently applied: <see cref="BuiltinDarkPaletteId"/> /
    /// <see cref="BuiltinLightPaletteId"/> for the shipped appearance palettes, otherwise the id the
    /// Theme Engine supplied through <see cref="ApplyPalette"/>.
    /// </summary>
    public string? AppliedPaletteId { get; private set; }

    /// <summary>
    /// Ensures the token dictionaries exist, then applies the current settings. Safe to call twice;
    /// the second call re-normalizes a foreign palette provider (e.g. the aggregate theme include).
    /// </summary>
    public bool Initialize()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (!_listening)
        {
            _application.ActualThemeVariantChanged += OnActualThemeVariantChanged;
            _listening = true;
        }

        var ok = ApplyRequestedVariant();
        ok &= SetContrast(Contrast);
        ok &= SetDensity(Density);
        ok &= SetReducedMotion(ReducedMotion);
        IsInitialized = true;
        return ok;
    }

    /// <summary>Switches palette; <see cref="AppearanceMode.System"/> follows the platform variant.</summary>
    public bool SetAppearance(AppearanceMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        Appearance = mode;
        return ApplyRequestedVariant();
    }

    /// <summary>
    /// Palette seam for the Theme Engine (V11R-C-1): replaces only the color layer
    /// (<c>Nm.Color.*</c>) and preserves the theme-invariant tokens and the density/motion/contrast
    /// overlay semantics. The palette must define every key in <see cref="PaletteColorKeys"/>; a
    /// palette with missing keys or non-brush values is rejected without touching the current state
    /// (no half-applied palette).
    /// </summary>
    /// <param name="palette">Complete, flat (or theme-scoped) palette dictionary for the active appearance.</param>
    /// <param name="paletteId">Stable palette id reported back through <see cref="AppliedPaletteId"/>.</param>
    /// <returns>True when the palette was applied; false when validation/merge failed.</returns>
    public bool ApplyPalette(ResourceDictionary palette, string paletteId)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ArgumentNullException.ThrowIfNull(palette);
        if (string.IsNullOrWhiteSpace(paletteId))
        {
            LastError = "palette id must not be empty";
            return false;
        }

        var invalidKeys = new List<string>();
        foreach (var key in PaletteColorKeys)
        {
            if (!TryResolvePaletteValue(palette, key, out var value) || value is not IBrush)
            {
                invalidKeys.Add(key);
            }
        }

        if (invalidKeys.Count > 0)
        {
            LastError =
                $"palette '{paletteId}' is not a complete color layer: {invalidKeys.Count} key(s) missing or not a brush " +
                $"({string.Join(", ", invalidKeys.Take(5))}{(invalidKeys.Count > 5 ? ", ..." : string.Empty)})";
            return false;
        }

        SwapPalette(palette, IsLightConfigured(), paletteId, isBuiltin: false);
        return true;
    }

    /// <summary>Restores the shipped built-in palette for the current appearance (cancel/uninstall path).</summary>
    public bool RevertPalette()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return ApplyPaletteForActualVariant(forceBuiltin: true);
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
        return ApplyRequestedVariant();
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

        ApplyPaletteForActualVariant();
    }

    private bool ApplyRequestedVariant()
    {
        _application.RequestedThemeVariant = Appearance switch
        {
            AppearanceMode.Light => ThemeVariant.Light,
            AppearanceMode.Dark => ThemeVariant.Dark,
            _ => ThemeVariant.Default,
        };

        return ApplyPaletteForActualVariant();
    }

    private bool ApplyPaletteForActualVariant(bool forceBuiltin = false)
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

        SwapPalette(palette!, isLight, BuiltinPaletteId(isLight), isBuiltin: true);
        return true;
    }

    /// <summary>
    /// Swaps only the palette layer. The theme-invariant tokens are re-ensured and the overlays are
    /// re-ordered afterwards so density/motion/high-contrast semantics keep their precedence.
    /// </summary>
    private void SwapPalette(ResourceDictionary palette, bool isLight, string paletteId, bool isBuiltin)
    {
        RemovePaletteProviders();
        EnsureGlobalTokens();
        _application.Resources.MergedDictionaries.Add(palette);
        _palette = palette;
        _paletteIsLight = isLight;
        _paletteIsBuiltin = isBuiltin;
        AppliedPaletteId = paletteId;
        ReorderOverlays();
    }

    private bool IsLightConfigured() => Appearance switch
    {
        AppearanceMode.Light => true,
        AppearanceMode.Dark => false,
        _ => _application.ActualThemeVariant == ThemeVariant.Light,
    };

    private static string BuiltinPaletteId(bool isLight) =>
        isLight ? BuiltinLightPaletteId : BuiltinDarkPaletteId;

    /// <summary>Resolves a palette value for validation, tolerating flat and theme-scoped palettes.</summary>
    private bool TryResolvePaletteValue(ResourceDictionary palette, string key, out object? value)
    {
        if (palette.TryGetResource(key, ThemeVariant.Default, out value))
        {
            return true;
        }

        if (palette.TryGetResource(key, _application.ActualThemeVariant, out value))
        {
            return true;
        }

        return palette.TryGetResource(key, ThemeVariant.Dark, out value) ||
               palette.TryGetResource(key, ThemeVariant.Light, out value);
    }

    private void RemovePaletteProviders()
    {
        foreach (var provider in _application.Resources.MergedDictionaries.ToArray())
        {
            if (ProviderHasKey(provider, PaletteProbeKey))
            {
                _application.Resources.MergedDictionaries.Remove(provider);
            }
        }

        _palette = null;
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
    /// Keeps the precedence deterministic: palette first, then contrast, density and motion overlays,
    /// so an appearance switch can never re-order a high-contrast palette underneath the base palette.
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
