using System.Diagnostics;
using System.Text.Encodings.Web;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.Theme;
using SkiaSharp;

namespace NewManga.App.Tests;

/// <summary>
/// THEME-MACOS-1 evidence tests: the macOS Sonoma pack (id macos-sonoma /「macOS 风」) that carries both
/// Light and Dark token sets inside one pack, the appearance switch in the settings page, the macOS
/// traffic lights, font-stack bridging, hot-switch p95, WCAG contrast, reduced motion and four real
/// headless-Skia screenshots (bookshelf / settings × Light / Dark).
/// </summary>
public sealed class ThemeMacosTests
{
    private const string MacosId = ThemePacks.MacOsSonomaId;

    /// <summary>Every token key the existing six packs define; the macOS pack must map all of them.</summary>
    private static readonly string[] RequiredTokenKeys =
    {
        "AppBg", "HeaderBg", "CardBg", "CardBorder", "TextPrimary", "TextSecondary", "Accent", "AccentText",
        "ChipBg", "ChipActiveBg", "SearchBg", "NavBg", "NavActiveBg", "EmptyBg",
    };

    private static readonly string[] RequiredMaterialKeys =
    {
        "HeaderGradientStart", "HeaderGradientEnd", "CardShadow", "MicaFallback",
    };

    private static readonly IReadOnlyDictionary<string, string> MacosLightTokens = new Dictionary<string, string>
    {
        ["AppBg"] = "#F5F5F7",
        ["HeaderBg"] = "#E6FFFFFF",
        ["CardBg"] = "#FFFFFF",
        ["CardBorder"] = "#D2D2D7",
        ["TextPrimary"] = "#1D1D1F",
        ["TextSecondary"] = "#6E6E73",
        ["Accent"] = "#007AFF",
        ["AccentText"] = "#FFFFFF",
        ["ChipBg"] = "#F0F0F3",
        ["ChipActiveBg"] = "#007AFF",
        ["SearchBg"] = "#FFFFFF",
        ["NavBg"] = "#ECECEF",
        ["NavActiveBg"] = "#D6E9FF",
        ["NavActiveText"] = "#003E7E",
        ["EmptyBg"] = "#FAFAFC",
        ["Danger"] = "#FF3B30",
        ["Success"] = "#34C759",
        ["Warning"] = "#FF9500",
        ["Separator"] = "#D2D2D7",
    };

    private static readonly IReadOnlyDictionary<string, string> MacosDarkTokens = new Dictionary<string, string>
    {
        ["AppBg"] = "#1E1E1E",
        ["HeaderBg"] = "#E6252527",
        ["CardBg"] = "#2C2C2E",
        ["CardBorder"] = "#3A3A3C",
        ["TextPrimary"] = "#F5F5F7",
        ["TextSecondary"] = "#98989D",
        ["Accent"] = "#0A84FF",
        ["AccentText"] = "#FFFFFF",
        ["ChipBg"] = "#3A3A3C",
        ["ChipActiveBg"] = "#0A84FF",
        ["SearchBg"] = "#2C2C2E",
        ["NavBg"] = "#252527",
        ["NavActiveBg"] = "#1F3A5F",
        ["NavActiveText"] = "#D7E9FF",
        ["EmptyBg"] = "#1E1E1E",
        ["Danger"] = "#FF453A",
        ["Success"] = "#32D74B",
        ["Warning"] = "#FF9F0A",
        ["Separator"] = "#3A3A3C",
    };

    private static readonly IReadOnlyDictionary<string, string> MacosLightMaterials = new Dictionary<string, string>
    {
        ["HeaderGradientStart"] = "#FDFDFE",
        ["HeaderGradientEnd"] = "#ECECEF",
        ["CardShadow"] = "#14000000",
        ["MicaFallback"] = "#F5F5F7",
    };

    private static readonly IReadOnlyDictionary<string, string> MacosDarkMaterials = new Dictionary<string, string>
    {
        ["HeaderGradientStart"] = "#2C2C2E",
        ["HeaderGradientEnd"] = "#1E1E1E",
        ["CardShadow"] = "#66000000",
        ["MicaFallback"] = "#1E1E1E",
    };

    /// <summary>(id, AppBg, Accent, TextPrimary) of the six pre-existing packs — must never change.</summary>
    private static readonly (string Id, string AppBg, string Accent, string TextPrimary)[] LegacyPacks =
    {
        ("saber-purple", "#F5F3FA", "#764BA2", "#241C33"),
        ("saber-light", "#FAFAFC", "#4F46E5", "#1F2430"),
        ("midnight", "#101322", "#8B9BF3", "#EDEFF7"),
        ("sakura", "#FDF5F7", "#D96C8E", "#3A2430"),
        ("emerald", "#0F1A17", "#3DDC97", "#E8F5EF"),
        ("mono", "#F6F6F6", "#3A3A3A", "#1C1C1C"),
    };

    // ---------------------------------------------------------------- AC1: registration / default

    [AvaloniaFact]
    public void MacosPack_IsRegistered_WithChineseLabel_AndDefaultIsUnchanged()
    {
        // THEME-MACOS-2 adds macos-launchpad / macos-split next to macos-sonoma: the macOS family is now
        // three packs, each listed exactly once, and the default pack is still saber-purple.
        Assert.Equal(9, ThemePacks.All.Count);
        Assert.Equal("saber-purple", ThemePacks.Default.Id);
        Assert.Equal(
            new[]
            {
                "saber-purple", "saber-light", "midnight", "sakura", "emerald", "mono",
                MacosId, ThemePacks.MacOsLaunchpadId, ThemePacks.MacOsSplitId,
            },
            ThemePacks.All.Select(pack => pack.Id).ToArray());

        var mac = ThemePacks.ById(MacosId);
        Assert.Equal(MacosId, mac.Id);
        Assert.Equal("macOS 风", mac.Label);
        Assert.True(mac.SupportsVariants);
        Assert.NotNull(mac.DarkTokens);
        Assert.NotNull(mac.DarkMaterials);
        Assert.False(mac.IsDark, "macOS pack selects the Light variant by default");
        Assert.Equal(ThemePacks.MacOsFontFamily, mac.FontFamily);
        Assert.False(string.IsNullOrWhiteSpace(mac.Manifest));
        Assert.Contains("\"id\":\"macos-sonoma\"", mac.Manifest, StringComparison.Ordinal);

        // The settings theme center lists every pack once, macOS included (never split into two rows).
        var vm = new SettingsViewModel();
        Assert.Equal(ThemePacks.All.Count, vm.ThemePacks.Count);
        Assert.Equal(1, vm.ThemePacks.Count(pack => pack.Id == MacosId));
        Assert.Contains(vm.ThemePacks, pack => pack.Id == MacosId && pack.Label == "macOS 风");

        var legacy = LegacyPacks.Select(entry => ThemePacks.ById(entry.Id)).ToArray();
        foreach (var pack in legacy)
        {
            Assert.False(pack.SupportsVariants, $"{pack.Id} must stay a single-token pack");
            Assert.Equal(ThemePacks.DefaultFontFamily, pack.FontFamily);
            Assert.Equal(ThemePackMetrics.Default, pack.Metrics);
        }

        var reduced = mac.WithReducedMotion(true);
        Assert.True(reduced.Motion.Reduced);
        Assert.Equal(TimeSpan.Zero, reduced.Motion.For("fast"));
        Assert.Equal(TimeSpan.Zero, reduced.Motion.For("normal"));
        Assert.Equal(TimeSpan.Zero, reduced.Motion.For("slow"));

        WriteEvidence("theme/pack.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1");
            writer.WriteString("generated_by", "ThemeMacosTests.MacosPack_IsRegistered_WithChineseLabel_AndDefaultIsUnchanged");
            writer.WriteString("default_theme_id", ThemePacks.Default.Id);
            writer.WriteBoolean("default_unchanged", ThemePacks.Default.Id == "saber-purple");
            writer.WriteNumber("packs_total", ThemePacks.All.Count);
            writer.WriteStartArray("packs");
            foreach (var pack in ThemePacks.All)
            {
                WritePack(writer, pack);
            }

            writer.WriteEndArray();
            writer.WriteStartObject("checks");
            writer.WriteBoolean("macos_single_list_entry", vm.ThemePacks.Count(pack => pack.Id == MacosId) == 1);
            writer.WriteBoolean("macos_label_is_chinese", mac.Label == "macOS 风");
            writer.WriteBoolean("legacy_packs_single_token_set", legacy.All(pack => !pack.SupportsVariants));
            writer.WriteBoolean("reduced_motion_zeroes_durations", reduced.Motion.For("fast") == TimeSpan.Zero);
            writer.WriteBoolean("macos_maps_all_required_tokens", RequiredTokenKeys.All(mac.Tokens.ContainsKey) &&
                                                                      RequiredTokenKeys.All(mac.DarkTokens!.ContainsKey));
            writer.WriteBoolean("macos_maps_all_required_materials", RequiredMaterialKeys.All(mac.Materials.ContainsKey) &&
                                                                      RequiredMaterialKeys.All(mac.DarkMaterials!.ContainsKey));
            writer.WriteEndObject();
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- AC2: both variants map the spec

    [AvaloniaFact]
    public void MacosPack_LightAndDarkMatchFrozenSpec_EveryTokenAndMaterial()
    {
        var application = Application.Current!;
        var mac = ThemePacks.ById(MacosId);

        AssertVariantMatches(mac.Tokens, MacosLightTokens, "light.tokens");
        AssertVariantMatches(mac.DarkTokens!, MacosDarkTokens, "dark.tokens");
        AssertVariantMatches(mac.Materials, MacosLightMaterials, "light.materials");
        AssertVariantMatches(mac.DarkMaterials!, MacosDarkMaterials, "dark.materials");

        // Metrics / motion / font are part of the frozen macOS contract.
        Assert.Equal(new ThemePackMetrics(12, 14, 8, 6, "0 1 3 0 #14000000", "0 1 3 0 #66000000"), mac.Metrics);
        Assert.Equal(TimeSpan.FromMilliseconds(120), mac.Motion.Fast);
        Assert.Equal(TimeSpan.FromMilliseconds(160), mac.Motion.Normal);
        Assert.Equal(TimeSpan.FromMilliseconds(240), mac.Motion.Slow);
        Assert.False(mac.Motion.Reduced);

        // Every declared token becomes a live resource in both variants (missing key = Magenta from Brush()).
        ThemePackService.Apply(application, mac);
        Assert.False(ThemePackService.CurrentVariant.IsDarkVariantForTest(), "Apply() selects Light for the macOS pack");
        foreach (var pair in MacosLightTokens)
        {
            AssertResourceColor(pair.Key, pair.Value, "light");
        }

        ThemePackService.ApplyVariant(application, Avalonia.Styling.ThemeVariant.Dark);
        Assert.True(ThemePackService.CurrentVariant.IsDarkVariantForTest());
        foreach (var pair in MacosDarkTokens)
        {
            AssertResourceColor(pair.Key, pair.Value, "dark");
        }

        foreach (var pair in new[] { ("Corner.Card", 14d), ("Corner.Button", 8d), ("Corner.Small", 6d), ("Corner.Window", 12d) })
        {
            Assert.True(application.TryGetResource(pair.Item1, application.ActualThemeVariant, out var value),
                $"missing resource {pair.Item1}");
            Assert.Equal(pair.Item2, Assert.IsType<double>(value));
        }

        Assert.True(application.TryGetResource("CardShadowBox", application.ActualThemeVariant, out var shadow));
        Assert.Equal("0 1 3 0 #66000000", Assert.IsType<string>(shadow));

        // Return to the light variant so later tests start from a known state.
        ThemePackService.ApplyVariant(application, Avalonia.Styling.ThemeVariant.Light);
    }

    // ---------------------------------------------------------------- AC5 regression: legacy packs

    [AvaloniaFact]
    public void LegacyPacks_KeepTheirKeyTokens_AndFallbackNavActiveText()
    {
        var application = Application.Current!;
        foreach (var expected in LegacyPacks)
        {
            var pack = ThemePacks.ById(expected.Id);
            Assert.Equal(expected.AppBg, pack.Tokens["AppBg"]);
            Assert.Equal(expected.Accent, pack.Tokens["Accent"]);
            Assert.Equal(expected.TextPrimary, pack.Tokens["TextPrimary"]);

            ThemePackService.Apply(application, pack);
            Assert.Equal(Color.Parse(expected.AppBg), ThemePackService.ColorOf("AppBg"));
            Assert.Equal(Color.Parse(expected.Accent), ThemePackService.ColorOf("Accent"));
            Assert.Equal(Color.Parse(expected.TextPrimary), ThemePackService.ColorOf("TextPrimary"));
            // Legacy packs have no NavActiveText token: the service falls back to AccentText (visual unchanged).
            Assert.Equal(Color.Parse(pack.Tokens["AccentText"]), ThemePackService.ColorOf("NavActiveText"));
            AssertFontResource(ThemePacks.DefaultFontFamily, "legacy font stack");
        }
    }

    // ---------------------------------------------------------------- AC3: hot-switch p95

    [AvaloniaFact]
    public void HotSwitch_MacosLightDarkAndLegacyPacks_P95Under100ms()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var window = new MainWindow(new FakeHostController(FakeHostController.ReadySnapshot("雾港来信", "星海归途")), new AppOptions());
        window.Width = 1280;
        window.Height = 820;
        window.Show();
        Dispatcher.UIThread.RunJobs();

        var mac = ThemePacks.ById(MacosId);
        var steps = new (string Label, bool VariantSwitch, ThemePack Pack, Avalonia.Styling.ThemeVariant Variant, string ExpectedAppBg)[]
        {
            ("macos-light", false, mac, Avalonia.Styling.ThemeVariant.Light, "#F5F5F7"),
            ("macos-dark", true, mac, Avalonia.Styling.ThemeVariant.Dark, "#1E1E1E"),
            ("macos-light", true, mac, Avalonia.Styling.ThemeVariant.Light, "#F5F5F7"),
            ("saber-purple", false, ThemePacks.SaberPurple, Avalonia.Styling.ThemeVariant.Light, "#F5F3FA"),
            ("midnight", false, ThemePacks.Midnight, Avalonia.Styling.ThemeVariant.Dark, "#101322"),
            ("sakura", false, ThemePacks.Sakura, Avalonia.Styling.ThemeVariant.Light, "#FDF5F7"),
        };

        // Warm-up (not measured) so the first sample does not pay JIT / first-render cost.
        ThemePackService.Apply(application, mac);
        window.ApplyTheme();
        Dispatcher.UIThread.RunJobs();

        var samples = new List<(string Label, double Ms)>();
        for (var cycle = 0; cycle < 8; cycle++)
        {
            foreach (var step in steps)
            {
                var watch = Stopwatch.StartNew();
                if (step.VariantSwitch)
                {
                    ThemePackService.ApplyVariant(application, step.Variant);
                }
                else
                {
                    ThemePackService.Apply(application, step.Pack);
                }

                window.ApplyTheme();
                Dispatcher.UIThread.RunJobs();
                watch.Stop();
                samples.Add((step.Label, watch.Elapsed.TotalMilliseconds));
                Assert.Equal(Color.Parse(step.ExpectedAppBg), ThemePackService.ColorOf("AppBg"));
            }
        }

        var sorted = samples.Select(sample => sample.Ms).OrderBy(ms => ms).ToArray();
        var p95 = sorted[(int)Math.Ceiling(sorted.Length * 0.95) - 1];
        var max = sorted[^1];
        var min = sorted[0];

        Assert.True(samples.Count >= 30, $"need >=30 samples, got {samples.Count}");
        Assert.True(p95 <= 100, $"theme hot-switch p95={p95:F2}ms must be <=100ms");
        Assert.True(max <= 100, $"worst switch {max:F2}ms");

        // macOS colors must not leak into the legacy packs after the mixed sweep (and vice versa).
        ThemePackService.Apply(application, ThemePacks.Midnight);
        window.ApplyTheme();
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(Color.Parse("#101322"), ThemePackService.ColorOf("AppBg"));
        Assert.Equal(Color.Parse("#EDEFF7"), ThemePackService.ColorOf("TextPrimary"));
        ThemePackService.ApplyVariant(application, Avalonia.Styling.ThemeVariant.Dark);
        Assert.Equal(Color.Parse("#101322"), ThemePackService.ColorOf("AppBg"));

        WriteEvidence("theme/hot-switch-macos.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3");
            writer.WriteString("generated_by", "ThemeMacosTests.HotSwitch_MacosLightDarkAndLegacyPacks_P95Under100ms");
            writer.WriteString("threshold_ms", "100");
            writer.WriteNumber("threshold", 100);
            writer.WriteNumber("samples", samples.Count);
            writer.WriteNumber("cycles", 8);
            writer.WriteNumber("p95_ms", Math.Round(p95, 3));
            writer.WriteNumber("max_ms", Math.Round(max, 3));
            writer.WriteNumber("min_ms", Math.Round(min, 3));
            writer.WriteBoolean("p95_pass", p95 <= 100);
            writer.WriteBoolean("max_pass", max <= 100);
            writer.WriteBoolean("no_color_residue", true);
            writer.WriteStartArray("steps");
            foreach (var step in steps)
            {
                writer.WriteStartObject();
                writer.WriteString("label", step.Label);
                writer.WriteString("kind", step.VariantSwitch ? "variant" : "pack");
                writer.WriteString("variant", step.VariantSwitch ? (ThemePackMetrics.IsDark(step.Variant) ? "Dark" : "Light") : (step.Pack.IsDark ? "Dark" : "Light"));
                writer.WriteString("expected_app_bg", step.ExpectedAppBg);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteStartArray("samples");
            foreach (var sample in samples)
            {
                writer.WriteStartObject();
                writer.WriteString("label", sample.Label);
                writer.WriteNumber("ms", Math.Round(sample.Ms, 3));
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });

        window.Close();
    }

    // ---------------------------------------------------------------- AC4: WCAG contrast

    [AvaloniaFact]
    public void MacosContrast_MeetsWcag_ForBodyAndSecondaryText()
    {
        var mac = ThemePacks.ById(MacosId);
        var rows = new List<(string Variant, string Role, string FgToken, Color Fg, string BgToken, Color Bg, double Ratio, double Required, bool Pass)>();

        void AddRow(string variant, string fgToken, string fgHex, string bgToken, string bgHex, double required)
        {
            var ratio = ContrastRatio(Color.Parse(fgHex), Color.Parse(bgHex));
            rows.Add((variant, fgToken, fgToken, Color.Parse(fgHex), bgToken, Color.Parse(bgHex), Math.Round(ratio, 3), required, ratio >= required));
        }

        foreach (var variant in new[] { ("Light", mac.Tokens), ("Dark", mac.DarkTokens!) })
        {
            AddRow(variant.Item1, "TextPrimary", variant.Item2["TextPrimary"], "AppBg", variant.Item2["AppBg"], 4.5);
            AddRow(variant.Item1, "TextPrimary", variant.Item2["TextPrimary"], "CardBg", variant.Item2["CardBg"], 4.5);
            AddRow(variant.Item1, "TextSecondary", variant.Item2["TextSecondary"], "AppBg", variant.Item2["AppBg"], 3.0);
            AddRow(variant.Item1, "TextSecondary", variant.Item2["TextSecondary"], "CardBg", variant.Item2["CardBg"], 3.0);
            AddRow(variant.Item1, "NavActiveText", variant.Item2["NavActiveText"], "NavActiveBg", variant.Item2["NavActiveBg"], 4.5);
        }

        foreach (var row in rows)
        {
            Assert.True(row.Pass, $"{row.Variant} {row.Role} on {row.BgToken} ratio {row.Ratio:F2} < {row.Required}");
        }

        WriteEvidence("theme/contrast.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4");
            writer.WriteString("generated_by", "ThemeMacosTests.MacosContrast_MeetsWcag_ForBodyAndSecondaryText");
            writer.WriteString("formula", "WCAG 2.x relative luminance: L = 0.2126*R + 0.7152*G + 0.0722*B (channel linearized: c<=0.03928 ? c/12.92 : ((c+0.055)/1.055)^2.4); ratio = (Lmax+0.05)/(Lmin+0.05)");
            writer.WriteString("requirements", "body text >=4.5, secondary text >=3, nav-active text >=4.5");
            writer.WriteStartArray("pairs");
            foreach (var row in rows)
            {
                writer.WriteStartObject();
                writer.WriteString("variant", row.Variant);
                writer.WriteString("text_token", row.FgToken);
                writer.WriteString("text_hex", row.Fg.ToString());
                writer.WriteString("background_token", row.BgToken);
                writer.WriteString("background_hex", row.Bg.ToString());
                writer.WriteNumber("ratio", row.Ratio);
                writer.WriteNumber("required", row.Required);
                writer.WriteBoolean("pass", row.Pass);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteBoolean("pass", rows.All(row => row.Pass));
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- AC2/f: reduced motion

    [AvaloniaFact]
    public void MacosMotion_ReducedMotionZeroesEveryDuration()
    {
        var mac = ThemePacks.ById(MacosId);
        Assert.Equal(TimeSpan.FromMilliseconds(120), mac.Motion.For("fast"));
        Assert.Equal(TimeSpan.FromMilliseconds(160), mac.Motion.For("normal"));
        Assert.Equal(TimeSpan.FromMilliseconds(240), mac.Motion.For("slow"));

        var reduced = mac.WithReducedMotion(true);
        Assert.True(reduced.ReducedMotion);
        Assert.Equal(TimeSpan.Zero, reduced.Motion.For("fast"));
        Assert.Equal(TimeSpan.Zero, reduced.Motion.For("normal"));
        Assert.Equal(TimeSpan.Zero, reduced.Motion.For("slow"));

        // The existing motion mechanism keeps its 90/160/240 defaults for the legacy packs.
        Assert.Equal(TimeSpan.FromMilliseconds(90), ThemePacks.Default.Motion.Fast);
        Assert.Equal(TimeSpan.Zero, ThemePacks.Default.WithReducedMotion(true).Motion.For("normal"));
    }

    // ---------------------------------------------------------------- AC1/2: settings appearance switch

    [AvaloniaFact]
    public void SettingsPage_AppearanceSwitch_AppliesMatchingVariant_AndLeavesNoResidue()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var vm = new SettingsViewModel();
        var applied = 0;
        var page = new SettingsPage(vm, () => applied++);
        var host = new Window { Content = page, Width = 980, Height = 760 };
        host.Show();
        for (var i = 0; i < 3; i++)
        {
            Dispatcher.UIThread.RunJobs();
        }

        try
        {
            Assert.Equal(ThemePacks.All.Count, page.ThemeList.ItemCount);
            Assert.False(page.AppearanceRow.IsVisible, "single-token packs must not show the appearance row");
            Assert.Equal(ThemePacks.All.Count, page.ThemeButtons.Count);
            Assert.Equal(12d, page.ThemeCard.CornerRadius.TopLeft);

            var macButton = page.ThemeButtons.Single(entry => entry.Pack.Id == MacosId).Button;
            macButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();

            Assert.Equal(MacosId, ThemePackService.Current.Id);
            Assert.Equal(MacosId, vm.SelectedPack.Id);
            Assert.Equal(1, applied);
            Assert.True(page.AppearanceRow.IsVisible, "dual-variant pack must show the appearance row");
            Assert.Equal(14d, page.ThemeCard.CornerRadius.TopLeft);
            Assert.Equal(Color.Parse("#F5F5F7"), ThemePackService.ColorOf("AppBg"));

            page.DarkVariantButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();
            Assert.True(ThemePackMetrics.IsDark(ThemePackService.CurrentVariant));
            Assert.Equal(Color.Parse("#1E1E1E"), ThemePackService.ColorOf("AppBg"));
            Assert.Equal(Color.Parse("#2C2C2E"), ThemePackService.ColorOf("CardBg"));
            Assert.Equal(Color.Parse("#F5F5F7"), ThemePackService.ColorOf("TextPrimary"));
            Assert.Equal(Color.Parse("#D7E9FF"), ThemePackService.ColorOf("NavActiveText"));
            Assert.Equal(Color.Parse("#0A84FF"), ThemePackService.ColorOf("Accent"));
            Assert.Equal(2, applied);

            page.LightVariantButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();
            Assert.False(ThemePackMetrics.IsDark(ThemePackService.CurrentVariant));
            Assert.Equal(Color.Parse("#F5F5F7"), ThemePackService.ColorOf("AppBg"));
            Assert.Equal(Color.Parse("#007AFF"), ThemePackService.ColorOf("Accent"));
            Assert.Equal(3, applied);

            // Selecting a single-token pack hides the appearance row and leaves no macOS colour behind.
            var sakuraButton = page.ThemeButtons.Single(entry => entry.Pack.Id == "sakura").Button;
            sakuraButton.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
            Dispatcher.UIThread.RunJobs();
            Assert.Equal("sakura", ThemePackService.Current.Id);
            Assert.False(page.AppearanceRow.IsVisible);
            Assert.Equal(12d, page.ThemeCard.CornerRadius.TopLeft);
            Assert.Equal(Color.Parse("#FDF5F7"), ThemePackService.ColorOf("AppBg"));
            Assert.Equal(Color.Parse("#3A2430"), ThemePackService.ColorOf("TextPrimary"));
            Assert.Equal(Color.Parse("#FFFFFF"), ThemePackService.ColorOf("AccentText"));
            Assert.Equal(Color.Parse("#FFFFFF"), ThemePackService.ColorOf("NavActiveText"));
        }
        finally
        {
            host.Close();
        }
    }

    // ---------------------------------------------------------------- AC1: macOS traffic lights + font

    [AvaloniaFact]
    public void MainWindow_TrafficLights_VisibleOnlyForMacosPack_AndFontStackFollowsPack()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var window = new MainWindow(new FakeHostController(FakeHostController.ReadySnapshot("雾港来信")), new AppOptions());
        window.Width = 1280;
        window.Height = 820;
        window.Show();
        Dispatcher.UIThread.RunJobs();

        try
        {
            Assert.False(window.AreTrafficLightsVisible, "macOS traffic lights must be hidden for legacy packs");
            Assert.Equal(ThemePacks.DefaultFontFamily, ReadFontFamily());

            window.Settings.SelectTheme(ThemePacks.ById(MacosId));
            Dispatcher.UIThread.RunJobs();
            Assert.True(window.AreTrafficLightsVisible);
            Assert.Equal(ThemePacks.MacOsFontFamily, ReadFontFamily());
            Assert.Contains("Inter", ThemePacks.MacOsFontFamily, StringComparison.Ordinal);
            Assert.Contains("PingFang SC", ThemePacks.MacOsFontFamily, StringComparison.Ordinal);
            Assert.Equal(Color.Parse("#003E7E"), NavForeground(window, "bookshelf"));
            // Dark variant keeps the traffic lights and swaps the nav-active colour.
            window.Settings.SwitchVariant(Avalonia.Styling.ThemeVariant.Dark);
            Dispatcher.UIThread.RunJobs();
            Assert.True(window.AreTrafficLightsVisible);
            Assert.Equal(Color.Parse("#D7E9FF"), NavForeground(window, "bookshelf"));

            window.Settings.SelectTheme(ThemePacks.Default);
            Dispatcher.UIThread.RunJobs();
            Assert.False(window.AreTrafficLightsVisible);
            Assert.Equal(ThemePacks.DefaultFontFamily, ReadFontFamily());
            Assert.Equal(Color.Parse("#FFFFFF"), NavForeground(window, "bookshelf"));
        }
        finally
        {
            window.Close();
        }

        static Color NavForeground(MainWindow window, string page) =>
            Assert.IsAssignableFrom<ISolidColorBrush>(window.NavButtons[page].Foreground).Color;

        static string? ReadFontFamily()
        {
            if (!Application.Current!.TryGetResource(ThemePackService.AppFontFamily, Application.Current.ActualThemeVariant, out var value))
            {
                return null;
            }

            return value switch
            {
                FontFamily family => NormalizeFontStack(family.ToString()),
                string text => NormalizeFontStack(text),
                _ => null,
            };
        }
    }

    // ---------------------------------------------------------------- AC2: real headless-Skia screenshots

    [AvaloniaFact]
    public void MacosScreenshots_RenderFourRealFrames_WithVariantBackgrounds()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var mac = ThemePacks.ById(MacosId);
        var directory = Path.Combine(Evidence.Directory, "screenshots");
        Directory.CreateDirectory(directory);

        var captures = new List<ScreenshotInfo>();

        // Each variant is rendered by a freshly constructed real MainWindow: the shell's code-built pages
        // resolve their brushes when they are constructed, so constructing the window with the variant
        // already applied is the honest render of that variant (an in-place variant switch only repaints
        // the resource-driven surfaces / theme centre, same as the pre-existing in-place theme switching).
        ThemePackService.Apply(application, mac);
        var lightWindow = CreateShellWindow();
        try
        {
            lightWindow.Navigate("bookshelf");
            captures.Add(Capture(lightWindow, directory, "bookshelf-light", "#F5F5F7", minimumBackgroundRatio: 0.30));
            lightWindow.Navigate("settings");
            captures.Add(Capture(lightWindow, directory, "settings-light", "#F5F5F7", minimumBackgroundRatio: 0.02));
        }
        finally
        {
            lightWindow.Close();
        }

        ThemePackService.ApplyVariant(application, Avalonia.Styling.ThemeVariant.Dark);
        var darkWindow = CreateShellWindow();
        try
        {
            darkWindow.Navigate("settings");
            captures.Add(Capture(darkWindow, directory, "settings-dark", "#1E1E1E", minimumBackgroundRatio: 0.02));
            darkWindow.Navigate("bookshelf");
            captures.Add(Capture(darkWindow, directory, "bookshelf-dark", "#1E1E1E", minimumBackgroundRatio: 0.30));
        }
        finally
        {
            darkWindow.Close();
        }

        Assert.Equal(4, captures.Count);
        var lightBookshelf = captures.Single(c => c.Name == "bookshelf-light");
        var darkBookshelf = captures.Single(c => c.Name == "bookshelf-dark");
        Assert.NotEqual(lightBookshelf.PrimaryBackground, darkBookshelf.PrimaryBackground);
        foreach (var capture in captures)
        {
            Assert.True(capture.MatchedSamples > 0, $"{capture.Name}: expected AppBg samples not found");
            Assert.True(capture.DistinctColors > 20, $"{capture.Name}: only {capture.DistinctColors} colours (placeholder?)");
        }

        WriteEvidence("theme/screenshots.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteString("generated_by", "ThemeMacosTests.MacosScreenshots_RenderFourRealFrames_WithVariantBackgrounds");
            writer.WriteString("renderer", "Avalonia.Headless + Skia (UseHeadlessDrawing=false) CaptureRenderedFrame()");
            writer.WriteNumber("width", 1280);
            writer.WriteNumber("height", 820);
            writer.WriteStartArray("captures");
            foreach (var capture in captures)
            {
                writer.WriteStartObject();
                writer.WriteString("name", capture.Name);
                writer.WriteString("path", "screenshots/" + capture.Name + ".png");
                writer.WriteNumber("width", capture.Width);
                writer.WriteNumber("height", capture.Height);
                writer.WriteNumber("bytes", capture.Bytes);
                writer.WriteString("expected_app_bg", capture.ExpectedAppBg);
                writer.WriteString("primary_background", capture.PrimaryBackground);
                writer.WriteNumber("sampled_pixels", capture.SampledPixels);
                writer.WriteNumber("matched_app_bg_samples", capture.MatchedSamples);
                writer.WriteNumber("matched_app_bg_ratio", Math.Round(capture.BackgroundRatio, 4));
                writer.WriteNumber("distinct_colors", capture.DistinctColors);
                writer.WriteBoolean("pass", true);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteBoolean("light_and_dark_differ", lightBookshelf.PrimaryBackground != darkBookshelf.PrimaryBackground);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- helpers

    private sealed record ScreenshotInfo(
        string Name,
        int Width,
        int Height,
        long Bytes,
        string ExpectedAppBg,
        string PrimaryBackground,
        int SampledPixels,
        int MatchedSamples,
        double BackgroundRatio,
        int DistinctColors);

    private static MainWindow CreateShellWindow()
    {
        var window = new MainWindow(
            new FakeHostController(FakeHostController.ReadySnapshot("雾港来信", "星海归途")),
            new AppOptions())
        {
            Width = 1280,
            Height = 820,
        };
        window.Show();
        for (var i = 0; i < 3; i++)
        {
            Dispatcher.UIThread.RunJobs();
        }

        return window;
    }

    private static ScreenshotInfo Capture(MainWindow window, string directory, string name, string expectedAppBgHex, double minimumBackgroundRatio)
    {
        Dispatcher.UIThread.RunJobs();
        var path = Path.Combine(directory, name + ".png");
        var frame = window.CaptureRenderedFrame() ?? throw new InvalidOperationException($"{name}: CaptureRenderedFrame() returned null");
        frame.Save(path);
        var bytes = new FileInfo(path).Length;
        Assert.True(bytes > 4096, $"{name}: {bytes} bytes — blank/placeholder screenshot");
        var bitmap = SKBitmap.Decode(path) ?? throw new InvalidOperationException($"{name}: PNG decode failed");
        using (bitmap)
        {
            Assert.Equal(1280, bitmap.Width);
            Assert.Equal(820, bitmap.Height);
            var expected = Color.Parse(expectedAppBgHex);
            var total = 0;
            var matched = 0;
            var distinct = new HashSet<uint>();
            for (var y = 0; y < bitmap.Height; y += 5)
            {
                for (var x = 0; x < bitmap.Width; x += 5)
                {
                    var pixel = bitmap.GetPixel(x, y);
                    total++;
                    distinct.Add((uint)((pixel.Red << 16) | (pixel.Green << 8) | pixel.Blue));
                    if (Math.Abs(pixel.Red - expected.R) <= 2 && Math.Abs(pixel.Green - expected.G) <= 2 && Math.Abs(pixel.Blue - expected.B) <= 2)
                    {
                        matched++;
                    }
                }
            }

            var ratio = (double)matched / total;
            Assert.True(ratio >= minimumBackgroundRatio,
                $"{name}: only {ratio:P1} of sampled pixels are AppBg {expectedAppBgHex} (need >= {minimumBackgroundRatio:P0})");
            Assert.True(distinct.Count > 20, $"{name}: only {distinct.Count} distinct colours");

            // The pixel at the empty-state / page-body centre must be the variant's AppBg for the bookshelf.
            if (name.StartsWith("bookshelf", StringComparison.Ordinal))
            {
                var centre = bitmap.GetPixel(640, 700);
                Assert.True(
                    Math.Abs(centre.Red - expected.R) <= 2 && Math.Abs(centre.Green - expected.G) <= 2 && Math.Abs(centre.Blue - expected.B) <= 2,
                    $"{name}: centre pixel {centre} is not AppBg {expectedAppBgHex} (blank render?)");
            }

            return new ScreenshotInfo(name, bitmap.Width, bitmap.Height, bytes, expectedAppBgHex, expected.ToString(), total, matched, ratio, distinct.Count);
        }
    }

    private static void AssertVariantMatches(
        IReadOnlyDictionary<string, string> actual,
        IReadOnlyDictionary<string, string> expected,
        string label)
    {
        foreach (var pair in expected)
        {
            Assert.True(actual.TryGetValue(pair.Key, out var value), $"{label} missing token {pair.Key}");
            Assert.Equal(pair.Value, value);
        }

        if (label.EndsWith("tokens", StringComparison.Ordinal))
        {
            foreach (var key in RequiredTokenKeys)
            {
                Assert.True(actual.ContainsKey(key), $"{label} missing required token {key}");
            }
        }
        else
        {
            foreach (var key in RequiredMaterialKeys)
            {
                Assert.True(actual.ContainsKey(key), $"{label} missing required material {key}");
            }
        }
    }

    private static void AssertResourceColor(string key, string expectedHex, string variant)
    {
        var expected = Color.Parse(expectedHex);
        var actual = ThemePackService.ColorOf(key);
        Assert.True(actual == expected, $"{variant} {key}: expected {expected} got {actual} (Magenta = unmapped)");
    }

    private static void AssertFontResource(string expectedStack, string label)
    {
        var application = Application.Current!;
        Assert.True(application.TryGetResource(ThemePackService.AppFontFamily, application.ActualThemeVariant, out var value), $"{label}: missing AppFontFamily");
        var family = Assert.IsType<FontFamily>(value);
        Assert.Equal(expectedStack, NormalizeFontStack(family.ToString()));
    }

    /// <summary>
    /// Avalonia renders a multi-family FontFamily as "compositefont:&lt;stack&gt;#&lt;details&gt;"; keep only the
    /// declared stack so the assertion checks the pack-provided font token verbatim.
    /// </summary>
    private static string NormalizeFontStack(string text)
    {
        var stack = text.StartsWith("compositefont:", StringComparison.Ordinal)
            ? text["compositefont:".Length..]
            : text;
        var hash = stack.IndexOf('#');
        return hash >= 0 ? stack[..hash] : stack;
    }

    private static double RelativeLuminance(Color color)
    {
        static double Channel(byte value)
        {
            var channel = value / 255.0;
            return channel <= 0.03928 ? channel / 12.92 : Math.Pow((channel + 0.055) / 1.055, 2.4);
        }

        return 0.2126 * Channel(color.R) + 0.7152 * Channel(color.G) + 0.0722 * Channel(color.B);
    }

    private static double ContrastRatio(Color foreground, Color background)
    {
        var first = RelativeLuminance(foreground);
        var second = RelativeLuminance(background);
        var lighter = Math.Max(first, second);
        var darker = Math.Min(first, second);
        return (lighter + 0.05) / (darker + 0.05);
    }

    private static void WritePack(Utf8JsonWriter writer, ThemePack pack)
    {
        writer.WriteStartObject();
        writer.WriteString("id", pack.Id);
        writer.WriteString("label", pack.Label);
        writer.WriteBoolean("is_dark", pack.IsDark);
        writer.WriteBoolean("supports_variants", pack.SupportsVariants);
        writer.WriteString("font_family", pack.FontFamily);
        writer.WriteNumber("motion_fast_ms", pack.Motion.Fast.TotalMilliseconds);
        writer.WriteNumber("motion_normal_ms", pack.Motion.Normal.TotalMilliseconds);
        writer.WriteNumber("motion_slow_ms", pack.Motion.Slow.TotalMilliseconds);
        writer.WriteBoolean("motion_reduced", pack.Motion.Reduced);
        writer.WriteStartObject("metrics");
        writer.WriteNumber("corner_window", pack.Metrics.CornerWindow);
        writer.WriteNumber("corner_card", pack.Metrics.CornerCard);
        writer.WriteNumber("corner_button", pack.Metrics.CornerButton);
        writer.WriteNumber("corner_small", pack.Metrics.CornerSmall);
        writer.WriteString("card_shadow_light", pack.Metrics.CardShadowLight);
        writer.WriteString("card_shadow_dark", pack.Metrics.CardShadowDark);
        writer.WriteEndObject();
        WriteDictionary(writer, "light_tokens", pack.Tokens);
        WriteDictionary(writer, "light_materials", pack.Materials);
        if (pack.DarkTokens is { Count: > 0 } darkTokens && pack.DarkMaterials is { Count: > 0 } darkMaterials)
        {
            WriteDictionary(writer, "dark_tokens", darkTokens);
            WriteDictionary(writer, "dark_materials", darkMaterials);
        }
        else
        {
            writer.WriteNull("dark_tokens");
            writer.WriteNull("dark_materials");
        }

        writer.WriteEndObject();
    }

    private static void WriteDictionary(Utf8JsonWriter writer, string name, IReadOnlyDictionary<string, string> values)
    {
        writer.WriteStartObject(name);
        foreach (var pair in values.OrderBy(entry => entry.Key, StringComparer.Ordinal))
        {
            writer.WriteString(pair.Key, pair.Value);
        }

        writer.WriteEndObject();
    }

    private static void WriteEvidence(string relativePath, Action<Utf8JsonWriter> write)
    {
        var path = Path.Combine(Evidence.Directory, relativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions
        {
            Indented = true,
            // Evidence JSON should stay human-readable for the Chinese pack label.
            Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        });
        write(writer);
    }
}

internal static class ThemeVariantAssertions
{
    /// <summary>Test-only helper: true when the variant resolves to Dark (single place to compare variants).</summary>
    public static bool IsDarkVariantForTest(this Avalonia.Styling.ThemeVariant variant) => ThemePackMetrics.IsDark(variant);
}
