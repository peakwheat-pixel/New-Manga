using System.Security.Cryptography;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Styling;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// C-3-I1: the legacy shell's appearance switch must move the DesignSystem palette, not only the
/// Avalonia theme variant. Both the top-bar cycle and the settings-page light/dark row are covered,
/// asserting the resolved token value and a real rendered-frame hash change.
/// </summary>
public sealed class LegacyAppearanceSyncTests
{
    [AvaloniaFact]
    public void Cycle_theme_switches_both_the_variant_and_the_palette()
    {
        using var manager = CreateManager();
        var window = CreateWindow(manager);
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var darkHash = ScreenshotHash(window);
        var darkBg = ColorOf(NmKeys.Color.Bg.App, ThemeVariant.Dark);
        Assert.Equal(darkBg, ResolvedColor(NmKeys.Color.Bg.App));

        window.CycleTheme();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(AppearanceMode.Light, manager.Appearance);
        Assert.Equal(ThemeVariant.Light, Application.Current!.RequestedThemeVariant);
        var lightBg = ColorOf(NmKeys.Color.Bg.App, ThemeVariant.Light);
        Assert.Equal(lightBg, ResolvedColor(NmKeys.Color.Bg.App));
        Assert.NotEqual(darkHash, ScreenshotHash(window));

        window.Close();
    }

    [AvaloniaFact]
    public void Settings_appearance_row_switches_both_the_variant_and_the_palette()
    {
        using var manager = CreateManager();
        var window = CreateWindow(manager);
        window.Show();
        Dispatcher.UIThread.RunJobs();
        var darkHash = ScreenshotHash(window);

        window.Settings.SwitchVariant(ThemeVariant.Light);
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(AppearanceMode.Light, manager.Appearance);
        Assert.Equal(ColorOf(NmKeys.Color.Bg.App, ThemeVariant.Light), ResolvedColor(NmKeys.Color.Bg.App));
        Assert.NotEqual(darkHash, ScreenshotHash(window));

        window.Settings.SwitchVariant(ThemeVariant.Dark);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(AppearanceMode.Dark, manager.Appearance);
        Assert.Equal(ColorOf(NmKeys.Color.Bg.App, ThemeVariant.Dark), ResolvedColor(NmKeys.Color.Bg.App));

        window.Close();
    }

    private static DesignSystemThemeManager CreateManager()
    {
        var manager = new DesignSystemThemeManager(Application.Current!);
        Assert.True(manager.Initialize(AppearanceMode.Dark), manager.LastError);
        return manager;
    }

    private static MainWindow CreateWindow(DesignSystemThemeManager manager)
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        return new MainWindow(controller, new AppOptions(), themeManager: manager);
    }

    private static Color ResolvedColor(string key)
    {
        Assert.True(Application.Current!.TryGetResource(key, null, out var value), $"{key} is not loaded");
        return value switch
        {
            ISolidColorBrush brush => brush.Color,
            Color color => color,
            _ => throw new InvalidOperationException($"{key} resolved to {value?.GetType().Name ?? "null"}"),
        };
    }

    private static Color ColorOf(string key, ThemeVariant variant)
    {
        Assert.True(Application.Current!.TryGetResource(key, variant, out var value), $"{key} has no {variant} value");
        return value switch
        {
            ISolidColorBrush brush => brush.Color,
            Color color => color,
            _ => throw new InvalidOperationException($"{key} resolved to {value?.GetType().Name ?? "null"}"),
        };
    }

    private static string ScreenshotHash(Window window)
    {
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException("frame capture failed");
        using var stream = new MemoryStream();
        frame.Save(stream);
        return Convert.ToHexString(SHA256.HashData(stream.ToArray()));
    }
}

