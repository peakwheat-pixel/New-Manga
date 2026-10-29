using Avalonia;
using Avalonia.Controls;
using Avalonia.Styling;
using NewManga.DesignSystem.Theming;
using DsAppearanceMode = NewManga.DesignSystem.Theming.AppearanceMode;
using DsContrastMode = NewManga.DesignSystem.Theming.ContrastMode;

namespace NewManga.ThemeEngine;

/// <summary>
/// The real Part B adapter: connects <see cref="ThemeService"/> to the running Avalonia application and
/// the design system's <see cref="DesignSystemThemeManager"/> seam. It is the only Theme Engine type
/// that touches Avalonia resources, and it only forwards:
/// <list type="bullet">
///   <item><c>ApplyThemeLayer</c> — converts the composed <see cref="ThemePaletteComposer"/> layer to a
///   <see cref="ResourceDictionary"/> and hands it to the DS 59-key whitelist seam (failure keeps the
///   previous layer; <see cref="LastError"/> is surfaced);</item>
///   <item><c>RevertToBuiltInLayer</c> — DS <c>RevertPalette()</c>;</item>
///   <item>appearance/contrast/reduced-motion — existing DS manager methods;</item>
///   <item><c>PlatformThemeChanged</c> — re-raised from <see cref="Application.ActualThemeVariantChanged"/>
///   so the service can recompose the current theme for a system light/dark flip.</item>
/// </list>
/// Swapping dictionaries never recreates the visual tree: window instances and canvas content stay
/// untouched (contract §4 behavior 1).
/// </summary>
public sealed class DesignSystemThemeLayerSink : IThemeLayerSink, IDisposable
{
    private readonly Application _application;
    private readonly DesignSystemThemeManager _manager;
    private string? _lastError;
    private bool _disposed;

    /// <summary>Creates the adapter over one application and its initialized design-system manager.</summary>
    public DesignSystemThemeLayerSink(Application application, DesignSystemThemeManager manager)
    {
        _application = application ?? throw new ArgumentNullException(nameof(application));
        _manager = manager ?? throw new ArgumentNullException(nameof(manager));
        _application.ActualThemeVariantChanged += OnActualThemeVariantChanged;
    }

    /// <inheritdoc />
    public bool IsPlatformLight => _application.ActualThemeVariant == ThemeVariant.Light;

    /// <inheritdoc />
    public event EventHandler? PlatformThemeChanged;

    /// <inheritdoc />
    public string? LastError => _lastError ?? _manager.LastError;

    /// <inheritdoc />
    public bool ApplyThemeLayer(IReadOnlyDictionary<string, object?> layer, string themeId)
    {
        ArgumentNullException.ThrowIfNull(layer);
        ObjectDisposedException.ThrowIf(_disposed, this);

        try
        {
            var dictionary = new ResourceDictionary();
            foreach (var (key, value) in layer)
            {
                if (value is null)
                {
                    _lastError = $"theme layer '{themeId}' contains a null value for '{key}'";
                    return false;
                }

                dictionary[key] = value;
            }

            var applied = _manager.ApplyThemeLayer(dictionary, themeId);
            _lastError = applied ? null : _manager.LastError;
            return applied;
        }
        catch (Exception exception) when (exception is ArgumentException or InvalidOperationException or NotSupportedException)
        {
            _lastError = $"theme layer '{themeId}' could not be applied: {exception.Message}";
            return false;
        }
    }

    /// <inheritdoc />
    public bool RevertToBuiltInLayer()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        try
        {
            var reverted = _manager.RevertPalette();
            _lastError = reverted ? null : _manager.LastError;
            return reverted;
        }
        catch (Exception exception) when (exception is InvalidOperationException or NotSupportedException)
        {
            _lastError = $"built-in theme layer could not be restored: {exception.Message}";
            return false;
        }
    }

    /// <inheritdoc />
    public bool SetAppearance(AppearanceMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return Guard(() => _manager.SetAppearance(Map(mode)), "appearance");
    }

    /// <inheritdoc />
    public bool SetContrast(ContrastMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return Guard(() => _manager.SetContrast(Map(mode)), "contrast");
    }

    /// <inheritdoc />
    public bool SetReducedMotion(bool enabled)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return Guard(() => _manager.SetReducedMotion(enabled), "reduced-motion");
    }

    /// <summary>Detaches from the application theme event; the applied resources stay as they are.</summary>
    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _application.ActualThemeVariantChanged -= OnActualThemeVariantChanged;
        _disposed = true;
    }

    private void OnActualThemeVariantChanged(object? sender, EventArgs args)
    {
        if (_disposed)
        {
            return;
        }

        PlatformThemeChanged?.Invoke(this, EventArgs.Empty);
    }

    private bool Guard(Func<bool> operation, string label)
    {
        try
        {
            var ok = operation();
            _lastError = ok ? null : _manager.LastError ?? $"{label} could not be applied";
            return ok;
        }
        catch (Exception exception) when (exception is InvalidOperationException or NotSupportedException)
        {
            _lastError = $"{label} could not be applied: {exception.Message}";
            return false;
        }
    }

    private static DsAppearanceMode Map(AppearanceMode mode) => mode switch
    {
        AppearanceMode.Light => DsAppearanceMode.Light,
        AppearanceMode.Dark => DsAppearanceMode.Dark,
        _ => DsAppearanceMode.System,
    };

    private static DsContrastMode Map(ContrastMode mode) =>
        mode == ContrastMode.High ? DsContrastMode.High : DsContrastMode.Standard;
}
