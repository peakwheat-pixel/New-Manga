using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Styling;
using Avalonia.Themes.Fluent;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Theming;

[assembly: AvaloniaTestApplication(typeof(NewManga.ThemeEngine.Tests.ThemeEngineTestAppBuilder))]
[assembly: CollectionBehavior(DisableTestParallelization = true)]

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Minimal headless application for the Theme Engine adapter tests. It composes the same style stack as
/// the product (Fluent base theme + design-system styles) and nothing else: the tests exercise the real
/// <see cref="DesignSystemThemeManager"/> plus <see cref="DesignSystemThemeLayerSink"/>, not the shell.
/// </summary>
public sealed class ThemeEngineTestApplication : Application
{
    public override void Initialize()
    {
        Styles.Add(new FluentTheme());
        Styles.Add((Styles)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Styles/NewMangaStyles.axaml")));
    }
}

/// <summary>Headless Avalonia test application builder (Skia drawing enabled for real pixel frames).</summary>
public static class ThemeEngineTestAppBuilder
{
    public static AppBuilder BuildAvaloniaApp() =>
        AppBuilder.Configure<ThemeEngineTestApplication>()
            .UseSkia()
            .UseHeadless(new AvaloniaHeadlessPlatformOptions { UseHeadlessDrawing = false });
}

/// <summary>Shared headless helpers for the adapter tests (mirrors the design-system test harness).</summary>
internal static class ThemeTestHarness
{
    /// <summary>Resets the application resource stack and returns an initialized design-system manager.</summary>
    public static DesignSystemThemeManager CreateInitialized()
    {
        var application = Application.Current
            ?? throw new InvalidOperationException("no Avalonia application is running");

        application.Resources.MergedDictionaries.Clear();
        application.Resources.MergedDictionaries.Add(LoadControlThemes());

        var manager = new DesignSystemThemeManager(application);
        Assert.True(manager.Initialize(), manager.LastError);
        return manager;
    }

    public static Application Application =>
        Application.Current ?? throw new InvalidOperationException("no Avalonia application is running");

    public static ResourceDictionary LoadControlThemes() =>
        (ResourceDictionary)AvaloniaXamlLoader.Load(
            new Uri("avares://NewManga.DesignSystem/Themes/Controls.axaml"));

    public static Color ColorOf(Application application, string key)
    {
        Assert.True(
            application.TryGetResource(key, application.ActualThemeVariant, out var value),
            $"application resource '{key}' is missing");
        return value is ISolidColorBrush brush
            ? brush.Color
            : throw new InvalidOperationException($"application resource '{key}' is not a color brush");
    }

    public static T ValueOf<T>(Application application, string key)
    {
        Assert.True(
            application.TryGetResource(key, application.ActualThemeVariant, out var value),
            $"application resource '{key}' is missing");
        return Assert.IsType<T>(value);
    }

    public static ThemePackage DefaultPackage => ThemeFixtures.DefaultPackage;

    public static ThemePackage UserPackage(
        string id,
        string darkCanvasColor,
        string lightCanvasColor,
        string? name = null) =>
        ThemeFixtures.AsUser(
            ThemeFixtures.DefaultPackage with
            {
                Dark = ThemeFixtures.WithColor(ThemeFixtures.DefaultPackage.Dark, NmKeys.Color.Bg.Canvas, darkCanvasColor),
                Light = ThemeFixtures.WithColor(ThemeFixtures.DefaultPackage.Light, NmKeys.Color.Bg.Canvas, lightCanvasColor),
            },
            id,
            name);
}
