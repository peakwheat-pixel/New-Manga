using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Styling;
using Avalonia.Threading;
using NewManga.DesignSystem.Theming;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// AC7/AC9: theme, contrast, density and motion switches are dictionary swaps on a live application —
/// the same visual tree updates in place and a broken dictionary source degrades without throwing.
/// </summary>
public sealed class ThemeManagerTests
{
    [AvaloniaFact]
    public void Initialize_publishes_palette_and_global_tokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var app = Application.Current!;
        Assert.Equal(Color.Parse("#FF0F1012"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));
        Assert.Equal(Color.Parse("#FFE9EAEC"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary));
        Assert.Equal(8d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Space.S3));
        Assert.Equal(12d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Space.S4));
        Assert.Equal(28d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.ControlHeight));
        Assert.True(manager.IsInitialized);
        Assert.Null(manager.LastError);
    }

    [AvaloniaFact]
    public void Appearance_switch_updates_a_live_visual_tree_without_rebuilding_it()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var border = new Border { Classes = { "card" } };
        var text = new TextBlock { Text = "probe" };
        border.Child = text;
        var window = new Window { Width = 320, Height = 200, Content = border };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var darkPanel = BrushesOf(border.Background, "card background");
        var darkText = BrushesOf(text.Foreground, "body text");
        Assert.Equal(Color.Parse("#FF1A1C1F"), darkPanel);
        Assert.Equal(Color.Parse("#FFE9EAEC"), darkText);

        Assert.True(manager.SetAppearance(AppearanceMode.Light), manager.LastError);
        Dispatcher.UIThread.RunJobs();

        var lightPanel = BrushesOf(border.Background, "card background after switch");
        var lightText = BrushesOf(text.Foreground, "body text after switch");
        Assert.Equal(Color.Parse("#FFFFFFFF"), lightPanel);
        Assert.Equal(Color.Parse("#FF1C1E21"), lightText);

        // Same instances: the switch replaced resources, not the visual tree.
        Assert.Same(border, window.Content);
        Assert.True(window.IsVisible);
        Assert.Equal(AppearanceMode.Light, manager.Appearance);

        window.Close();
    }

    [AvaloniaFact]
    public void High_contrast_overlay_wins_and_survives_an_appearance_switch()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        Assert.True(manager.SetContrast(ContrastMode.High), manager.LastError);
        Assert.Equal(Color.Parse("#FFFFFFFF"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary));

        Assert.True(manager.SetAppearance(AppearanceMode.Light), manager.LastError);
        Assert.Equal(Color.Parse("#FF000000"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary));
        Assert.Equal(Color.Parse("#FFF4F3F0"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));

        Assert.True(manager.SetContrast(ContrastMode.Standard), manager.LastError);
        Assert.Equal(Color.Parse("#FF1C1E21"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary));
    }

    [AvaloniaFact]
    public void Density_switch_replaces_the_scale_overlay()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        Assert.True(manager.SetDensity(DensityMode.Compact), manager.LastError);
        Assert.Equal(24d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.ControlHeight));
        Assert.Equal(new Thickness(10, 6, 10, 6), ThemeTestHarness.ValueOf<Thickness>(app, NmKeys.Padding.Control));

        Assert.True(manager.SetDensity(DensityMode.Spacious), manager.LastError);
        Assert.Equal(32d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.ControlHeight));

        Assert.True(manager.SetDensity(DensityMode.Comfortable), manager.LastError);
        Assert.Equal(28d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.ControlHeight));
    }

    [AvaloniaFact]
    public void Reduced_motion_zeroes_durations_and_flips_the_motion_toggle()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        Assert.Equal(TimeSpan.FromMilliseconds(90), ThemeTestHarness.ValueOf<TimeSpan>(app, NmKeys.Motion.Duration.Fast));
        Assert.True(ThemeTestHarness.ValueOf<bool>(app, NmKeys.Motion.Enabled));

        Assert.True(manager.SetReducedMotion(true), manager.LastError);
        Assert.Equal(TimeSpan.Zero, ThemeTestHarness.ValueOf<TimeSpan>(app, NmKeys.Motion.Duration.Fast));
        Assert.Equal(TimeSpan.Zero, ThemeTestHarness.ValueOf<TimeSpan>(app, NmKeys.Motion.Duration.Normal));
        Assert.False(ThemeTestHarness.ValueOf<bool>(app, NmKeys.Motion.Enabled));
        Assert.True(manager.ReducedMotion);

        Assert.True(manager.SetReducedMotion(false), manager.LastError);
        Assert.Equal(TimeSpan.FromMilliseconds(90), ThemeTestHarness.ValueOf<TimeSpan>(app, NmKeys.Motion.Duration.Fast));
    }

    [AvaloniaFact]
    public void Broken_dictionary_source_degrades_without_throwing()
    {
        var app = Application.Current!;
        app.Resources.MergedDictionaries.Clear();
        var broken = new BrokenResourceSource();
        using var manager = new DesignSystemThemeManager(app, broken);

        // Every dictionary fails to load: no exception, false result, recorded error.
        Assert.False(manager.Initialize());
        Assert.NotNull(manager.LastError);

        // The caller can still recover: a healthy manager re-normalizes the same application.
        using var healthy = ThemeTestHarness.CreateInitialized();
        Assert.Equal(Color.Parse("#FF0F1012"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));
    }

    [AvaloniaFact]
    public void Apply_palette_replaces_only_the_color_layer_and_revert_restores_builtin()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        Assert.Equal(DesignSystemThemeManager.BuiltinDarkPaletteId, manager.AppliedPaletteId);

        var globalBefore = ThemeTestHarness.ValueOf<double>(app, NmKeys.Space.S3);
        var custom = CompletePalette(palette =>
        {
            palette[NmKeys.Color.Bg.Canvas] = new SolidColorBrush(Color.Parse("#FF112233"));
            palette[NmKeys.Color.Bg.Panel] = new SolidColorBrush(Color.Parse("#FF223344"));
        });

        Assert.True(manager.ApplyPalette(custom, "user.ocean"), manager.LastError);
        Assert.Equal("user.ocean", manager.AppliedPaletteId);
        Assert.Equal(Color.Parse("#FF112233"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));
        Assert.Equal(Color.Parse("#FF223344"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Panel));
        // Global (size/spacing/typography) semantics are untouched by a palette swap.
        Assert.Equal(globalBefore, ThemeTestHarness.ValueOf<double>(app, NmKeys.Space.S3));
        Assert.Equal(28d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.ControlHeight));

        Assert.True(manager.RevertPalette(), manager.LastError);
        Assert.Equal(DesignSystemThemeManager.BuiltinDarkPaletteId, manager.AppliedPaletteId);
        Assert.Equal(Color.Parse("#FF0F1012"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));
    }

    [AvaloniaFact]
    public void Apply_palette_refreshes_a_live_visual_tree()
    {
        using var manager = ThemeTestHarness.CreateInitialized();

        var border = new Border { Classes = { "card" } };
        var window = new Window { Width = 320, Height = 200, Content = border };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(Color.Parse("#FF1A1C1F"), ((SolidColorBrush)border.Background!).Color);

        var custom = CompletePalette(palette =>
            palette[NmKeys.Color.Bg.Panel] = new SolidColorBrush(Color.Parse("#FF445566")));
        Assert.True(manager.ApplyPalette(custom, "user.refresh"), manager.LastError);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(Color.Parse("#FF445566"), ((SolidColorBrush)border.Background!).Color);

        Assert.True(manager.RevertPalette(), manager.LastError);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(Color.Parse("#FF1A1C1F"), ((SolidColorBrush)border.Background!).Color);
        Assert.True(window.IsVisible);

        window.Close();
    }

    [AvaloniaFact]
    public void Apply_palette_with_missing_keys_is_rejected_without_changing_state()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var canvasBefore = ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas);
        var idBefore = manager.AppliedPaletteId;

        var incomplete = CompletePalette(palette => palette.Remove(NmKeys.Color.Status.Failed));

        Assert.False(manager.ApplyPalette(incomplete, "user.broken"));
        Assert.NotNull(manager.LastError);
        Assert.Contains("not a complete color layer", manager.LastError, StringComparison.Ordinal);
        Assert.Equal(canvasBefore, ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));
        Assert.Equal(idBefore, manager.AppliedPaletteId);
    }

    [AvaloniaFact]
    public void Apply_palette_with_non_brush_values_is_rejected()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var textBefore = ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary);

        var invalid = CompletePalette(palette => palette[NmKeys.Color.Text.Primary] = "not-a-brush");

        Assert.False(manager.ApplyPalette(invalid, "user.invalid-types"));
        Assert.NotNull(manager.LastError);
        Assert.Equal(textBefore, ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary));
    }

    [AvaloniaFact]
    public void Appearance_switch_after_a_custom_palette_returns_to_the_builtin_palette()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var custom = CompletePalette(palette =>
            palette[NmKeys.Color.Bg.Canvas] = new SolidColorBrush(Color.Parse("#FF010203")));
        Assert.True(manager.ApplyPalette(custom, "user.temporary"), manager.LastError);

        Assert.True(manager.SetAppearance(AppearanceMode.Light), manager.LastError);
        Assert.Equal(DesignSystemThemeManager.BuiltinLightPaletteId, manager.AppliedPaletteId);
        Assert.Equal(Color.Parse("#FFF4F3F0"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));
    }

    [AvaloniaFact]
    public void Reset_to_defaults_restores_the_shipped_stack()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        Assert.True(manager.SetAppearance(AppearanceMode.Light));
        Assert.True(manager.SetContrast(ContrastMode.High));
        Assert.True(manager.SetDensity(DensityMode.Compact));
        Assert.True(manager.SetReducedMotion(true));

        Assert.True(manager.ResetToDefaults(), manager.LastError);

        Assert.Equal(Color.Parse("#FF0F1012"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Bg.Canvas));
        Assert.Equal(Color.Parse("#FFE9EAEC"), ThemeTestHarness.ColorOf(app, NmKeys.Color.Text.Primary));
        Assert.Equal(28d, ThemeTestHarness.ValueOf<double>(app, NmKeys.Size.ControlHeight));
        Assert.True(ThemeTestHarness.ValueOf<bool>(app, NmKeys.Motion.Enabled));
        Assert.Equal(AppearanceMode.Dark, manager.Appearance);
        Assert.Equal(ContrastMode.Standard, manager.Contrast);
        Assert.Equal(DensityMode.Comfortable, manager.Density);
        Assert.False(manager.ReducedMotion);
    }

    private static Color BrushesOf(IBrush? brush, string label) =>
        brush is SolidColorBrush solid
            ? solid.Color
            : throw new InvalidOperationException($"{label} is not a solid color brush");

    /// <summary>Copies the shipped dark palette into a fresh dictionary, then applies an optional mutation.</summary>
    private static ResourceDictionary CompletePalette(Action<ResourceDictionary>? mutate = null)
    {
        var source = (ResourceDictionary)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Themes/Tokens.Dark.axaml"));
        var palette = new ResourceDictionary();
        foreach (var key in DesignSystemThemeManager.PaletteColorKeys)
        {
            Assert.True(source.TryGetResource(key, ThemeVariant.Default, out var value), $"builtin palette lacks {key}");
            palette[key] = value;
        }

        mutate?.Invoke(palette);
        return palette;
    }

    private sealed class BrokenResourceSource : IDesignSystemResourceSource
    {
        private static readonly Uri Missing = new("avares://NewManga.DesignSystem/Themes/DoesNotExist.axaml");

        public Uri GlobalTokens => Missing;

        public Uri DarkPalette => Missing;

        public Uri LightPalette => Missing;

        public Uri HighContrastPalette => Missing;

        public Uri CompactDensity => Missing;

        public Uri SpaciousDensity => Missing;

        public Uri ReducedMotion => Missing;
    }
}

/// <summary>Shared helpers that isolate each test from resources merged by the previous test.</summary>
internal static class ThemeTestHarness
{
    public static DesignSystemThemeManager CreateInitialized()
    {
        var application = Application.Current
            ?? throw new InvalidOperationException("no Avalonia application is running");

        // Tests share one Application instance; start from a clean resource stack so every test sees
        // the same deterministic state the product gets on a fresh launch (the product merges the
        // control-theme dictionary in App.axaml, so the harness restores it here).
        application.Resources.MergedDictionaries.Clear();
        application.Resources.MergedDictionaries.Add(LoadControlThemes());

        var manager = new DesignSystemThemeManager(application);
        Assert.True(manager.Initialize(), manager.LastError);
        return manager;
    }

    private static ResourceDictionary LoadControlThemes() =>
        (ResourceDictionary)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Themes/Controls.axaml"));

    public static Color ColorOf(Application application, string key, ThemeVariant? theme = null)
    {
        Assert.True(
            application.TryGetResource(key, theme ?? application.ActualThemeVariant, out var value),
            $"application resource '{key}' is missing");
        return value is SolidColorBrush brush
            ? brush.Color
            : throw new InvalidOperationException($"application resource '{key}' is not a solid color brush");
    }

    public static T ValueOf<T>(Application application, string key, ThemeVariant? theme = null)
    {
        Assert.True(
            application.TryGetResource(key, theme ?? application.ActualThemeVariant, out var value),
            $"application resource '{key}' is missing");
        return Assert.IsType<T>(value);
    }
}
