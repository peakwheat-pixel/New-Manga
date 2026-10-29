using System.Runtime.InteropServices;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Platform;
using Avalonia.Threading;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Theming;
using NewManga.ThemeEngine;
using SkiaSharp;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Part B adapter acceptance against a real headless Avalonia application: the composed 59-key theme
/// layer reaches <see cref="Application.Resources"/> through the design-system seam, only the theme
/// layer changes (layout/density stay), failures keep the previous state, and switching themes neither
/// recreates the window nor changes canvas pixels (contract §4 behavior 1).
/// </summary>
public sealed class DesignSystemThemeLayerSinkTests : IDisposable
{
    private readonly TempDirectory _temp = new();

    public void Dispose() => _temp.Dispose();

    [AvaloniaFact]
    public void Sink_applies_the_composed_layer_and_reports_the_theme_layer_id()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var layer = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);

        var applied = sink.ApplyThemeLayer(layer, ThemeDefaults.DefaultThemeId);

        Assert.True(applied, sink.LastError);
        Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedThemeLayerId);
        var application = ThemeTestHarness.Application;
        Assert.Equal(Color.Parse("#FF0F1012"), ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));
        Assert.Equal(13d, ThemeTestHarness.ValueOf<double>(application, NmKeys.FontSize.Md));
        Assert.Equal(18.85, ThemeTestHarness.ValueOf<double>(application, NmKeys.LineHeight.Body), precision: 2);
        Assert.Equal(new CornerRadius(3), ThemeTestHarness.ValueOf<CornerRadius>(application, NmKeys.Corner.Md));
        Assert.Equal(
            TimeSpan.FromMilliseconds(ThemeMotion.DefaultSlowMs),
            ThemeTestHarness.ValueOf<TimeSpan>(application, NmKeys.Motion.Duration.Slow));
    }

    [AvaloniaFact]
    public void Sink_keeps_layout_density_and_spacing_resources_untouched()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var application = ThemeTestHarness.Application;
        var space = ThemeTestHarness.ValueOf<double>(application, NmKeys.Space.S3);
        var controlHeight = ThemeTestHarness.ValueOf<double>(application, NmKeys.Size.ControlHeight);
        var panelPadding = ThemeTestHarness.ValueOf<Thickness>(application, NmKeys.Padding.Panel);

        var layer = ThemePaletteComposer.Compose(
            ThemeTestHarness.UserPackage("ocean", "#102030", "#FFEFE0"),
            PaletteVariant.Dark);
        Assert.True(sink.ApplyThemeLayer(layer, "ocean"), sink.LastError);

        Assert.Equal(space, ThemeTestHarness.ValueOf<double>(application, NmKeys.Space.S3));
        Assert.Equal(controlHeight, ThemeTestHarness.ValueOf<double>(application, NmKeys.Size.ControlHeight));
        Assert.Equal(panelPadding, ThemeTestHarness.ValueOf<Thickness>(application, NmKeys.Padding.Panel));
        Assert.Equal(Color.Parse("#FF102030"), ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));
    }

    [AvaloniaFact]
    public void Sink_rejects_an_incomplete_layer_and_keeps_the_previous_state()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var application = ThemeTestHarness.Application;
        var complete = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);
        Assert.True(sink.ApplyThemeLayer(complete, ThemeDefaults.DefaultThemeId), sink.LastError);
        var canvasBefore = ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas);

        var incomplete = new Dictionary<string, object?>(complete, StringComparer.Ordinal);
        incomplete.Remove(NmKeys.Color.Status.Failed);
        var applied = sink.ApplyThemeLayer(incomplete, "broken");

        Assert.False(applied);
        Assert.NotNull(sink.LastError);
        Assert.Equal(canvasBefore, ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));
        Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedThemeLayerId);
    }

    [AvaloniaFact]
    public void Sink_rejects_wrong_value_types_without_mutating_state()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var complete = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);
        var invalid = new Dictionary<string, object?>(complete, StringComparer.Ordinal)
        {
            [NmKeys.FontFamily.Ui] = "not a font family",
        };

        Assert.False(sink.ApplyThemeLayer(invalid, "invalid-types"));
        Assert.NotNull(sink.LastError);
        Assert.Null(manager.AppliedThemeLayerId);
    }

    [AvaloniaFact]
    public void Sink_reports_ignored_non_whitelisted_keys_but_still_applies()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var application = ThemeTestHarness.Application;
        var layer = ThemePaletteComposer.Compose(ThemeTestHarness.DefaultPackage, PaletteVariant.Dark);
        var withLayoutOverride = new Dictionary<string, object?>(layer, StringComparer.Ordinal)
        {
            [NmKeys.Space.S3] = 99d,
        };

        Assert.True(sink.ApplyThemeLayer(withLayoutOverride, "override-attempt"), sink.LastError);

        Assert.Contains("outside the R-15 59-key whitelist", string.Join(" | ", manager.ThemeLayerIssues), StringComparison.Ordinal);
        Assert.Equal(8d, ThemeTestHarness.ValueOf<double>(application, NmKeys.Space.S3));
    }

    [AvaloniaFact]
    public void Sink_revert_restores_the_builtin_palette()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var application = ThemeTestHarness.Application;
        var layer = ThemePaletteComposer.Compose(
            ThemeTestHarness.UserPackage("ocean", "#102030", "#FFEFE0"),
            PaletteVariant.Dark);
        Assert.True(sink.ApplyThemeLayer(layer, "ocean"), sink.LastError);
        Assert.Equal(Color.Parse("#FF102030"), ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));

        Assert.True(sink.RevertToBuiltInLayer(), sink.LastError);

        Assert.Equal(Color.Parse("#FF0F1012"), ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));
        Assert.Equal(DesignSystemThemeManager.BuiltinDarkPaletteId, manager.AppliedPaletteId);
        Assert.Null(manager.AppliedThemeLayerId);
    }

    [AvaloniaFact]
    public async Task Service_initializes_and_applies_the_default_theme_through_the_real_sink()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var registry = CreateRegistry();
        var persistence = new RecordingPersistence
        {
            LoadResult = ThemeDefaults.Settings with { Appearance = AppearanceMode.Dark },
        };
        using var service = new ThemeService(registry, persistence, sink);

        await service.InitializeAsync();

        Assert.True(service.IsInitialized);
        Assert.Null(service.LastError);
        Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedThemeLayerId);
        Assert.Equal(Color.Parse("#FF0F1012"), ThemeTestHarness.ColorOf(ThemeTestHarness.Application, NmKeys.Color.Bg.Canvas));
        // No migration/recovery happened, so initialization must not rewrite the settings file.
        Assert.Equal(0, persistence.SaveCount);
        Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
    }

    [AvaloniaFact]
    public async Task Service_apply_user_theme_updates_real_resources_and_persists()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var registry = CreateRegistry();
        var persistence = new RecordingPersistence
        {
            LoadResult = ThemeDefaults.Settings with { Appearance = AppearanceMode.Dark },
        };
        using var service = new ThemeService(registry, persistence, sink);
        await service.InitializeAsync();

        var result = await service.ApplyAsync("ocean");

        Assert.True(result.Success, string.Join(", ", result.Issues.Select(issue => issue.Message)));
        Assert.False(result.Recovered);
        Assert.Equal("ocean", manager.AppliedThemeLayerId);
        Assert.Equal(Color.Parse("#FF102030"), ThemeTestHarness.ColorOf(ThemeTestHarness.Application, NmKeys.Color.Bg.Canvas));
        Assert.Equal("ocean", persistence.LastSaved?.ThemeId);
    }

    [AvaloniaFact]
    public async Task Service_set_appearance_recomposes_light_resources()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var registry = CreateRegistry();
        var persistence = new RecordingPersistence
        {
            LoadResult = ThemeDefaults.Settings with { Appearance = AppearanceMode.Dark },
        };
        using var service = new ThemeService(registry, persistence, sink);
        await service.InitializeAsync();

        await service.SetAppearanceAsync(AppearanceMode.Light);

        Assert.Equal(AppearanceMode.Light, service.Settings.Appearance);
        Assert.Equal(Color.Parse("#FFF4F3F0"), ThemeTestHarness.ColorOf(ThemeTestHarness.Application, NmKeys.Color.Bg.Canvas));
        Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedThemeLayerId);
        Assert.Equal(AppearanceMode.Light, persistence.LastSaved?.Appearance);
    }

    [AvaloniaFact]
    public async Task Theme_switch_keeps_the_window_instance_and_canvas_pixels()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var registry = CreateRegistry();
        var persistence = new RecordingPersistence
        {
            LoadResult = ThemeDefaults.Settings with { Appearance = AppearanceMode.Dark },
        };
        using var service = new ThemeService(registry, persistence, sink);
        await service.InitializeAsync();

        var bitmap = CreateSolidBitmap(32, 32, Colors.Magenta);
        var image = new Image
        {
            Source = bitmap,
            Width = 32,
            Height = 32,
            Stretch = Stretch.None,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Top,
        };
        var content = new StackPanel { Children = { image } };
        var window = new Window { Width = 160, Height = 120, Content = content };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var before = Capture(window);
        var result = await service.ApplyAsync("ocean");
        Dispatcher.UIThread.RunJobs();
        var after = Capture(window);

        Assert.True(result.Success);
        // The window and its content instance survive the theme switch (no visual-tree rebuild).
        Assert.True(window.IsVisible);
        Assert.Same(content, window.Content);
        // The comic canvas bitmap pixels are untouched by the theme switch.
        Assert.Equal(0, CountDifferentPixels(before, after, new SKRectI(0, 0, 32, 32)));
        // The theme really did reach the application resources.
        Assert.Equal(Color.Parse("#FF102030"), ThemeTestHarness.ColorOf(ThemeTestHarness.Application, NmKeys.Color.Bg.Canvas));
        window.Close();
    }

    [AvaloniaFact]
    public async Task Repeated_theme_switches_do_not_duplicate_resource_providers()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        using var sink = new DesignSystemThemeLayerSink(ThemeTestHarness.Application, manager);
        var registry = CreateRegistry();
        var persistence = new RecordingPersistence
        {
            LoadResult = ThemeDefaults.Settings with { Appearance = AppearanceMode.Dark },
        };
        using var service = new ThemeService(registry, persistence, sink);
        await service.InitializeAsync();
        var providersAfterInit = ThemeTestHarness.Application.Resources.MergedDictionaries.Count;

        for (var index = 0; index < 5; index++)
        {
            await service.ApplyAsync(index % 2 == 0 ? "ocean" : ThemeDefaults.DefaultThemeId);
        }

        Assert.Equal(providersAfterInit, ThemeTestHarness.Application.Resources.MergedDictionaries.Count);
        // The loop ends on the odd iteration (index 4 -> ocean).
        Assert.Equal("ocean", manager.AppliedThemeLayerId);
    }

    private ThemeRegistry CreateRegistry()
    {
        var directory = _temp.File("themes");
        Directory.CreateDirectory(directory);
        File.WriteAllText(
            Path.Combine(directory, "ocean.nmtheme"),
            ThemeFixtures.Write(ThemeTestHarness.UserPackage("ocean", "#102030", "#FFEFE0", "Ocean")));
        return new ThemeRegistry(directory);
    }

    private static WriteableBitmap Capture(Window window) =>
        window.CaptureRenderedFrame() ?? throw new InvalidOperationException("CaptureRenderedFrame returned null");

    private static WriteableBitmap CreateSolidBitmap(int width, int height, Color color)
    {
        var bitmap = new WriteableBitmap(
            new PixelSize(width, height),
            new Vector(96, 96),
            PixelFormat.Bgra8888,
            AlphaFormat.Premul);
        using var frame = bitmap.Lock();
        var pixels = new byte[frame.RowBytes * height];
        for (var offset = 0; offset < pixels.Length; offset += 4)
        {
            pixels[offset + 0] = color.B;
            pixels[offset + 1] = color.G;
            pixels[offset + 2] = color.R;
            pixels[offset + 3] = color.A;
        }

        Marshal.Copy(pixels, 0, frame.Address, pixels.Length);
        return bitmap;
    }

    private static int CountDifferentPixels(WriteableBitmap left, WriteableBitmap right, SKRectI region)
    {
        using var leftBitmap = Decode(left);
        using var rightBitmap = Decode(right);
        var different = 0;
        for (var y = region.Top; y < region.Bottom; y++)
        {
            for (var x = region.Left; x < region.Right; x++)
            {
                if (leftBitmap.GetPixel(x, y) != rightBitmap.GetPixel(x, y))
                {
                    different++;
                }
            }
        }

        return different;
    }

    private static SKBitmap Decode(WriteableBitmap frame)
    {
        using var stream = new MemoryStream();
        frame.Save(stream);
        return SKBitmap.Decode(stream.ToArray()) ?? throw new InvalidOperationException("PNG decode failed");
    }
}
