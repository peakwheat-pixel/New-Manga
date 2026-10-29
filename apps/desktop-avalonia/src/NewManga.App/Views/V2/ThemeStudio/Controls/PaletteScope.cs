using Avalonia;
using Avalonia.Controls;
using NewManga.App.ViewModels.V2.ThemeStudio;

namespace NewManga.App.Views.V2.ThemeStudio.Controls;

/// <summary>
/// Installs a scoped <c>Nm.*</c> token layer on a subtree (THEME_STUDIO_SPEC AC9).
///
/// <para>
/// Every <c>{DynamicResource Nm.*}</c> inside this scope resolves the candidate theme while the rest of
/// the window keeps the application palette: preview and cancel never mutate application resources, so the
/// main canvas pixels and unsaved edits cannot be disturbed by a theme preview. It is the only mechanism
/// the Theme Studio uses to render a theme.
/// </para>
/// </summary>
public sealed class PaletteScope : ContentControl
{
    /// <summary>The palette to install; null keeps the ambient application palette.</summary>
    public static readonly StyledProperty<ThemeStudioPalette?> PaletteProperty =
        AvaloniaProperty.Register<PaletteScope, ThemeStudioPalette?>(nameof(Palette));

    /// <summary>Creates an empty scope.</summary>
    public PaletteScope() => ClipToBounds = false;

    /// <summary>The active scoped palette.</summary>
    public ThemeStudioPalette? Palette
    {
        get => GetValue(PaletteProperty);
        set => SetValue(PaletteProperty, value);
    }

    /// <summary>Resource keys currently installed (test seam: proves the scope is really mounted).</summary>
    public IReadOnlyList<string> InstalledKeys =>
        Resources.MergedDictionaries.Count == 0 || Resources.MergedDictionaries[0] is not ResourceDictionary dictionary
            ? Array.Empty<string>()
            : dictionary.Keys.OfType<string>().ToArray();

    /// <inheritdoc />
    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == PaletteProperty)
        {
            ApplyPalette();
        }
    }

    private void ApplyPalette()
    {
        Resources.MergedDictionaries.Clear();
        var palette = Palette;
        if (palette is null)
        {
            return;
        }

        if (palette.Tokens is ResourceDictionary dictionary)
        {
            Resources.MergedDictionaries.Add(dictionary);
        }
    }
}
