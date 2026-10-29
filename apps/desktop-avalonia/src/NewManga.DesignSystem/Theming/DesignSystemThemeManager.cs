using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Styling;

namespace NewManga.DesignSystem.Theming;

/// <summary>
/// Applies the design system to a running Avalonia application by swapping resource dictionaries in
/// <see cref="Application.Resources"/> — never by recreating the visual tree (AC7). Appearance swaps
/// the palette dictionary, contrast/density/reduced-motion append or remove overlay dictionaries.
/// Failures to load a dictionary are reported through <see cref="LastError"/> and leave the previous
/// state intact (AC9).
/// </summary>
public sealed class DesignSystemThemeManager : IDisposable
{
    /// <summary>Key probed to detect a palette provider in <see cref="Application.Resources"/>.</summary>
    public const string PaletteProbeKey = "Nm.Color.Bg.Canvas";

    /// <summary>Key probed to detect the theme-invariant token dictionary.</summary>
    public const string GlobalProbeKey = "Nm.Space.3";

    private readonly Application _application;
    private readonly IDesignSystemResourceSource _resources;

    private ResourceDictionary? _palette;
    private bool _paletteIsLight;
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

    private bool ApplyPaletteForActualVariant()
    {
        var isLight = Appearance switch
        {
            AppearanceMode.Light => true,
            AppearanceMode.Dark => false,
            _ => _application.ActualThemeVariant == ThemeVariant.Light,
        };

        var source = isLight ? _resources.LightPalette : _resources.DarkPalette;
        if (!TryLoadAndRecord(source, out var palette))
        {
            return false;
        }

        if (_palette is not null && _paletteIsLight == isLight)
        {
            return true;
        }

        // Replace whatever currently provides the palette (a plain palette include, or the aggregate
        // NewMangaTheme include). The theme-invariant tokens are re-ensured afterwards so removing an
        // aggregate include cannot leave the application without tokens.
        RemovePaletteProviders();
        if (!EnsureGlobalTokens())
        {
            return false;
        }

        _application.Resources.MergedDictionaries.Add(palette!);
        _palette = palette;
        _paletteIsLight = isLight;
        ReorderOverlays();
        return true;
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
