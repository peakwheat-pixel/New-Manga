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
/// D-1 I2 P1-1 regression: startup must be verified against the REAL App.axaml resource stack, not a
/// synthetic harness stack. The product stack currently registers Global tokens, the dark palette and
/// the control themes as separate providers; the manager must replace only the palette and keep every
/// global token (spacing/fonts/Scrim/motion) resolvable after appearance switches and overlays.
/// The second test also covers the historical aggregate-provider shape (Global+palette in one
/// dictionary) so RemovePaletteProviders can never drop global tokens again.
/// </summary>
public sealed class RealAppResourceStackTests
{
    private static readonly string[] GlobalProbeKeys =
    [
        NmKeys.Space.S3,
        NmKeys.FontSize.Md,
        NmKeys.Color.Scrim,
        NmKeys.Motion.Duration.Slow,
    ];

    [AvaloniaFact]
    public void Real_App_startup_stack_keeps_global_tokens_through_appearance_and_overlays()
    {
        using var manager = InitializeFromRealAppStack();

        AssertGlobalTokensResolve("after real-App initialize", expectLight: false, expectedSlowMs: 220);
        Assert.Equal(DesignSystemThemeManager.BuiltinDarkPaletteId, manager.AppliedPaletteId);

        Assert.True(manager.SetAppearance(AppearanceMode.Light), manager.LastError);
        AssertGlobalTokensResolve("after switch to light", expectLight: true, expectedSlowMs: 220);
        Assert.Equal(DesignSystemThemeManager.BuiltinLightPaletteId, manager.AppliedPaletteId);

        Assert.True(manager.SetContrast(ContrastMode.High), manager.LastError);
        AssertGlobalTokensResolve("after high contrast", expectLight: true, expectedSlowMs: 220);

        Assert.True(manager.SetDensity(DensityMode.Compact), manager.LastError);
        AssertGlobalTokensResolve("after compact density", expectLight: true, expectedSlowMs: 220);

        Assert.True(manager.SetReducedMotion(true), manager.LastError);
        AssertGlobalTokensResolve("after reduced motion", expectLight: true, expectedSlowMs: 0);

        Assert.True(manager.SetAppearance(AppearanceMode.Dark), manager.LastError);
        AssertGlobalTokensResolve("after switch back to dark", expectLight: false, expectedSlowMs: 0);

        manager.ResetToDefaults();
    }

    [AvaloniaFact]
    public void Aggregate_global_and_palette_provider_is_never_removed_by_palette_swap()
    {
        var application = Application.Current!;
        application.Resources.MergedDictionaries.Clear();
        application.Resources.MergedDictionaries.Add(
            (ResourceDictionary)AvaloniaXamlLoader.Load(
                new Uri("avares://NewManga.DesignSystem/Themes/NewMangaTheme.axaml")));
        application.Resources.MergedDictionaries.Add(ThemeTestHarness.LoadControlThemes());

        var manager = new DesignSystemThemeManager(application);
        try
        {
            Assert.True(manager.Initialize(AppearanceMode.Dark), manager.LastError);
            AssertGlobalTokensResolve("aggregate provider startup", expectLight: false, expectedSlowMs: 220);

            Assert.True(manager.SetAppearance(AppearanceMode.Light), manager.LastError);
            AssertGlobalTokensResolve("aggregate provider after light switch", expectLight: true, expectedSlowMs: 220);

            Assert.True(manager.SetAppearance(AppearanceMode.Dark), manager.LastError);
            AssertGlobalTokensResolve("aggregate provider after dark switch", expectLight: false, expectedSlowMs: 220);
        }
        finally
        {
            manager.Dispose();
        }
    }

    private static DesignSystemThemeManager InitializeFromRealAppStack()
    {
        // Read the REAL App.axaml manifest from the product project and load every resource provider it
        // registers, in file order. This mirrors startup exactly while keeping each dictionary freshly
        // parented to the test Application (a production provider cannot be re-parented).
        var appXamlPath = Path.Combine(
            TestPaths.RepositoryRoot, "apps", "desktop-avalonia", "src", "NewManga.App", "App.axaml");
        var appXaml = File.ReadAllText(appXamlPath);
        var resources = applicationResourceUris(appXaml);

        Assert.True(resources.Count >= 3, "App.axaml must register the Global tokens, palette and control themes separately");

        var application = Application.Current!;
        application.Resources.MergedDictionaries.Clear();
        foreach (var uri in resources)
        {
            var dictionary = (ResourceDictionary)AvaloniaXamlLoader.Load(new Uri(uri));
            application.Resources.MergedDictionaries.Add(dictionary);
        }

        var manager = new DesignSystemThemeManager(application);
        Assert.True(manager.Initialize(AppearanceMode.Dark), manager.LastError);
        return manager;

        static List<string> applicationResourceUris(string xaml)
        {
            var uris = new List<string>();
            foreach (System.Text.RegularExpressions.Match match in System.Text.RegularExpressions.Regex.Matches(
                         xaml, "ResourceInclude\\s+Source=\"(avares://[^\"]+)\"", System.Text.RegularExpressions.RegexOptions.CultureInvariant))
            {
                uris.Add(match.Groups[1].Value);
            }

            return uris;
        }
    }

    private static void AssertGlobalTokensResolve(string stage, bool expectLight, int expectedSlowMs)
    {
        var application = Application.Current!;

        Assert.Equal(8d, ThemeTestHarness.ValueOf<double>(application, NmKeys.Space.S3));
        Assert.Equal(13d, ThemeTestHarness.ValueOf<double>(application, NmKeys.FontSize.Md));
        Assert.NotNull(ThemeTestHarness.ValueOf<SolidColorBrush>(application, NmKeys.Color.Scrim));
        Assert.Equal(
            TimeSpan.FromMilliseconds(expectedSlowMs),
            ThemeTestHarness.ValueOf<TimeSpan>(application, NmKeys.Motion.Duration.Slow));

        var expectedCanvas = expectLight
            ? ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas, ThemeVariant.Light)
            : ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas, ThemeVariant.Dark);
        Assert.Equal(expectedCanvas, ThemeTestHarness.ColorOf(application, NmKeys.Color.Bg.Canvas));
        Assert.True(
            application.TryFindResource(NmKeys.Color.Bg.Canvas, out _),
            $"{stage}: canvas palette key must resolve");
    }
}


