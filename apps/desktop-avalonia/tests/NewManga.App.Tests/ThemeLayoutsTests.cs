using System.Diagnostics;
using System.Text.Encodings.Web;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.LogicalTree;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.Theme;
using SkiaSharp;

namespace NewManga.App.Tests;

/// <summary>
/// THEME-MACOS-LAYOUTS-1 evidence tests: three macOS packs (Sonoma / Launchpad / Split) that each carry a
/// <see cref="LayoutProfile"/>, the shell's three navigation hosts, the bookshelf/settings layout switches,
/// 12 real headless-Skia screenshots (3 packs × Light/Dark × 书架/设置), the p95 layout hot-switch
/// measurement and the legacy six-pack zero-regression checks.
/// </summary>
public sealed class ThemeLayoutsTests
{
    private const double LayoutP95BudgetMs = 100;

    private static readonly (string Id, string Label, LayoutKind Kind)[] MacosLayoutPacks =
    {
        (ThemePacks.MacOsSonomaId, "macOS 风", LayoutKind.Sonoma),
        (ThemePacks.MacOsLaunchpadId, "macOS 启动台", LayoutKind.Launchpad),
        (ThemePacks.MacOsSplitId, "macOS 分栏", LayoutKind.Split),
    };

    /// <summary>The six pre-existing packs: layout must stay Sonoma (= THEME-MACOS-1) and tokens must not move.</summary>
    private static readonly (string Id, string AppBg, string Accent, string TextPrimary)[] LegacyPacks =
    {
        ("saber-purple", "#F5F3FA", "#764BA2", "#241C33"),
        ("saber-light", "#FAFAFC", "#4F46E5", "#1F2430"),
        ("midnight", "#101322", "#8B9BF3", "#EDEFF7"),
        ("sakura", "#FDF5F7", "#D96C8E", "#3A2430"),
        ("emerald", "#0F1A17", "#3DDC97", "#E8F5EF"),
        ("mono", "#F6F6F6", "#3A3A3A", "#1C1C1C"),
    };

    private static readonly string[] RequiredTokenKeys =
    {
        "AppBg", "HeaderBg", "CardBg", "CardBorder", "TextPrimary", "TextSecondary", "Accent", "AccentText",
        "ChipBg", "ChipActiveBg", "SearchBg", "NavBg", "NavActiveBg", "EmptyBg",
    };

    private static readonly string[] VariantSensitiveTokens = { "AppBg", "CardBg", "TextPrimary", "Accent", "TextSecondary", "NavBg" };

    // ---------------------------------------------------------------- AC1: registration / registration-order

    [AvaloniaFact]
    public void ThreeMacosLayoutPacks_AreRegistered_WithDistinctLayouts_AndLegacyPacksStayOnSonoma()
    {
        Assert.Equal(9, ThemePacks.All.Count);
        Assert.Equal("saber-purple", ThemePacks.Default.Id);

        var macPacks = new List<ThemePack>();
        foreach (var expected in MacosLayoutPacks)
        {
            var pack = ThemePacks.ById(expected.Id);
            Assert.Equal(expected.Id, pack.Id);
            Assert.Equal(expected.Label, pack.Label);
            Assert.Equal(expected.Kind, pack.Layout.Kind);
            Assert.Equal(expected.Label, pack.Layout.Label);
            Assert.True(pack.IsMacOsPack);
            Assert.True(ThemePacks.IsMacOsPack(pack));
            macPacks.Add(pack);
        }

        // One pack, one layout: the three kinds are all present and pairwise distinct.
        Assert.Equal(3, macPacks.Select(pack => pack.Layout.Kind).Distinct().Count());
        Assert.Equal(MacosLayoutPacks.Select(entry => entry.Id), ThemePacks.MacOsPackIds);

        // LayoutProfile carries the frozen geometry table (dock / sidebar / launchpad card / content width).
        var sonoma = ThemePacks.ById(ThemePacks.MacOsSonomaId).Layout;
        var launchpad = ThemePacks.ById(ThemePacks.MacOsLaunchpadId).Layout;
        var split = ThemePacks.ById(ThemePacks.MacOsSplitId).Layout;
        Assert.Equal(NavPlacement.TitleBar, sonoma.Nav);
        Assert.Equal(ShelfStyle.CenteredGrid, sonoma.Shelf);
        Assert.Equal(SettingsStyle.TwoColumn, sonoma.Settings);
        Assert.Equal(1400, sonoma.ContentMaxWidth);
        Assert.Equal(NavPlacement.Dock, launchpad.Nav);
        Assert.Equal(ShelfStyle.LaunchpadGrid, launchpad.Shelf);
        Assert.Equal(SettingsStyle.SingleColumn, launchpad.Settings);
        Assert.Equal(76, launchpad.DockHeight);
        Assert.Equal(1200, launchpad.ContentMaxWidth);
        Assert.Equal(900, launchpad.SettingsMaxWidth);
        Assert.Equal(168, launchpad.LaunchpadCardWidth);
        Assert.Equal(220, launchpad.LaunchpadCardHeight);
        Assert.True(launchpad.LaunchpadBottomInset >= 96, "the Launchpad grid must leave >=96px for the Dock");
        Assert.Equal(NavPlacement.Sidebar, split.Nav);
        Assert.Equal(ShelfStyle.SplitList, split.Shelf);
        Assert.Equal(SettingsStyle.SplitSections, split.Settings);
        Assert.Equal(220, split.SidebarWidth);
        Assert.Equal(260, split.ShelfListWidth);

        // The legacy six packs keep the Sonoma layout object (value-equal, so zero visual/structural change).
        foreach (var legacy in LegacyPacks)
        {
            var pack = ThemePacks.ById(legacy.Id);
            Assert.False(pack.IsMacOsPack);
            Assert.Equal(LayoutProfiles.Sonoma, pack.Layout);
            Assert.Equal(LayoutKind.Sonoma, pack.Layout.Kind);
        }

        // Settings theme centre lists all nine packs once; the three macOS rows carry the Chinese labels.
        var vm = new SettingsViewModel();
        Assert.Equal(ThemePacks.All.Count, vm.ThemePacks.Count);
        foreach (var expected in MacosLayoutPacks)
        {
            Assert.Equal(1, vm.ThemePacks.Count(pack => pack.Id == expected.Id));
            Assert.Contains(vm.ThemePacks, pack => pack.Id == expected.Id && pack.Label == expected.Label);
        }

        WriteEvidence("layout/profiles.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1");
            writer.WriteString("generated_by", "ThemeLayoutsTests.ThreeMacosLayoutPacks_AreRegistered_WithDistinctLayouts_AndLegacyPacksStayOnSonoma");
            writer.WriteString("default_theme_id", ThemePacks.Default.Id);
            writer.WriteBoolean("default_unchanged", ThemePacks.Default.Id == "saber-purple");
            writer.WriteNumber("packs_total", ThemePacks.All.Count);
            writer.WriteNumber("layout_profiles_total", LayoutProfiles.All.Count);
            writer.WriteStartArray("layouts");
            foreach (var profile in LayoutProfiles.All)
            {
                writer.WriteStartObject();
                writer.WriteString("kind", profile.Kind.ToString());
                writer.WriteString("label", profile.Label);
                writer.WriteString("nav_placement", profile.Nav.ToString());
                writer.WriteString("shelf_style", profile.Shelf.ToString());
                writer.WriteString("settings_style", profile.Settings.ToString());
                writer.WriteNumber("dock_height", profile.DockHeight);
                writer.WriteNumber("sidebar_width", profile.SidebarWidth);
                writer.WriteNumber("shelf_list_width", profile.ShelfListWidth);
                writer.WriteNumber("settings_nav_width", profile.SettingsNavWidth);
                writer.WriteNumber("launchpad_card_width", profile.LaunchpadCardWidth);
                writer.WriteNumber("launchpad_card_height", profile.LaunchpadCardHeight);
                writer.WriteNumber("content_max_width", profile.ContentMaxWidth);
                writer.WriteNumber("settings_max_width", profile.SettingsMaxWidth);
                writer.WriteNumber("launchpad_bottom_inset", profile.LaunchpadBottomInset);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteStartArray("packs");
            foreach (var pack in ThemePacks.All)
            {
                writer.WriteStartObject();
                writer.WriteString("id", pack.Id);
                writer.WriteString("label", pack.Label);
                writer.WriteString("layout_kind", pack.Layout.Kind.ToString());
                writer.WriteBoolean("is_macos_pack", pack.IsMacOsPack);
                writer.WriteBoolean("supports_variants", pack.SupportsVariants);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteStartObject("checks");
            writer.WriteBoolean("three_distinct_layout_kinds", macPacks.Select(pack => pack.Layout.Kind).Distinct().Count() == 3);
            writer.WriteBoolean("legacy_packs_layout_is_sonoma", LegacyPacks.All(entry => ThemePacks.ById(entry.Id).Layout == LayoutProfiles.Sonoma));
            writer.WriteBoolean("launchpad_reserves_dock_inset", launchpad.LaunchpadBottomInset >= 96);
            writer.WriteBoolean("settings_lists_every_pack_once", vm.ThemePacks.Count == ThemePacks.All.Count);
            writer.WriteEndObject();
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- AC1/AC2e: tokens + WCAG contrast

    [AvaloniaFact]
    public void AllThreeMacosPacks_CarryCompleteLightAndDarkTokens_PassingWcag_AndLegacyTokensAreUntouched()
    {
        var application = Application.Current!;
        var contrastRows = new List<(string Variant, string TextToken, string BgToken, double Ratio, bool Pass)>();

        foreach (var expected in MacosLayoutPacks)
        {
            var pack = ThemePacks.ById(expected.Id);
            Assert.True(pack.SupportsVariants, $"{pack.Id} must carry both Light and Dark token sets");
            foreach (var key in RequiredTokenKeys)
            {
                Assert.True(pack.Tokens.ContainsKey(key), $"{pack.Id} light missing {key}");
                Assert.True(pack.DarkTokens!.ContainsKey(key), $"{pack.Id} dark missing {key}");
            }

            foreach (var key in new[] { "SidebarBg", "DockBg" })
            {
                Assert.True(pack.Tokens.ContainsKey(key), $"{pack.Id} light missing layout chrome token {key}");
                Assert.True(pack.DarkTokens!.ContainsKey(key), $"{pack.Id} dark missing layout chrome token {key}");
            }

            foreach (var key in VariantSensitiveTokens)
            {
                Assert.NotEqual(pack.Tokens[key], pack.DarkTokens![key]);
            }

            // WCAG 2.x: body text >= 4.5, secondary text >= 3 on the page and card surfaces, both variants.
            foreach (var variant in new[] { ("Light", pack.Tokens), ("Dark", pack.DarkTokens!) })
            {
                var (variantName, tokens) = variant;
                foreach (var row in new[]
                         {
                             ("TextPrimary", "AppBg", 4.5),
                             ("TextPrimary", "CardBg", 4.5),
                             ("TextSecondary", "AppBg", 3.0),
                             ("TextSecondary", "CardBg", 3.0),
                             ("NavActiveText", "NavActiveBg", 4.5),
                         })
                {
                    var ratio = ContrastRatio(Color.Parse(tokens[row.Item1]), Color.Parse(tokens[row.Item2]));
                    contrastRows.Add(($"{pack.Id}/{variantName}", row.Item1, row.Item2, Math.Round(ratio, 3), ratio >= row.Item3));
                    Assert.True(ratio >= row.Item3,
                        $"{pack.Id} {variantName} {row.Item1} on {row.Item2}: ratio {ratio:F2} < {row.Item3}");
                }
            }

            // Applying the pack publishes every token as a live resource in both variants.
            ThemePackService.Apply(application, pack);
            ThemePackService.ApplyVariant(application, Avalonia.Styling.ThemeVariant.Dark);
            foreach (var pair in pack.DarkTokens!)
            {
                Assert.True(ThemePackService.ColorOf(pair.Key) == Color.Parse(pair.Value),
                    $"{pack.Id} dark {pair.Key} is not the live resource colour");
            }

            ThemePackService.ApplyVariant(application, Avalonia.Styling.ThemeVariant.Light);
            Assert.Equal(Color.Parse(pack.Tokens["AppBg"]), ThemePackService.ColorOf("AppBg"));
        }

        // Legacy six packs: tokens unchanged, layout Sonoma, chrome fallbacks resolve (never magenta).
        foreach (var expected in LegacyPacks)
        {
            var pack = ThemePacks.ById(expected.Id);
            Assert.Equal(expected.AppBg, pack.Tokens["AppBg"]);
            Assert.Equal(expected.Accent, pack.Tokens["Accent"]);
            Assert.Equal(expected.TextPrimary, pack.Tokens["TextPrimary"]);
            Assert.Equal(LayoutProfiles.Sonoma, pack.Layout);

            ThemePackService.Apply(application, pack);
            Assert.Equal(Color.Parse(expected.AppBg), ThemePackService.ColorOf("AppBg"));
            Assert.Equal(Color.Parse(expected.Accent), ThemePackService.ColorOf("Accent"));
            Assert.Equal(Color.Parse(expected.TextPrimary), ThemePackService.ColorOf("TextPrimary"));
            Assert.Equal(Color.Parse(pack.Tokens["AccentText"]), ThemePackService.ColorOf("NavActiveText"));
            Assert.Equal(ThemePackService.ColorOf("NavBg"), ThemePackService.ColorOf("SidebarBg"));
            Assert.Equal(ThemePackService.ColorOf("CardBg"), ThemePackService.ColorOf("DockBg"));
        }
    }

    // ---------------------------------------------------------------- AC1: shell + page layout switching

    [AvaloniaFact]
    public void SwitchingLayoutPacks_MovesNavHosts_AndAppliesBookshelfAndSettingsLayouts()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var window = CreateShellWindow();
        try
        {
            AssertShellLayout(window, LayoutKind.Sonoma);
            Assert.False(window.AreTrafficLightsVisible, "legacy pack keeps the traffic lights hidden");

            foreach (var expected in MacosLayoutPacks)
            {
                var pack = ThemePacks.ById(expected.Id);
                window.Settings.SelectTheme(pack);
                Pump(3);

                AssertShellLayout(window, expected.Kind);
                Assert.True(window.AreTrafficLightsVisible, $"{pack.Id}: traffic lights must stay visible");
                Assert.Equal(pack.Id, ThemePackService.Current.Id);

                // Navigation still works in every host: the same four buttons navigate to the four pages.
                foreach (var page in new[] { "workbench", "reader", "settings", "bookshelf" })
                {
                    window.Navigate(page);
                    Pump(3);
                    Assert.Equal(page, window.CurrentPage);
                }

                // Assert each page while it is the hosted page, so the lazily realised item templates are live.
                window.Navigate("settings");
                Pump(4);
                Assert.IsType<SettingsPage>(window.PageHostControl.Content);
                AssertSettingsMembersAvailable(window.Settings);
                window.Navigate("bookshelf");
                Pump(4);
                Assert.IsType<BookshelfPage>(window.PageHostControl.Content);
                AssertBookshelfMembersAvailable(window.BookshelfPageControl);
            }

            // Back to a legacy pack: the shell returns to the Sonoma structure with no residue.
            window.Settings.SelectTheme(ThemePacks.SaberPurple);
            Pump(3);
            AssertShellLayout(window, LayoutKind.Sonoma);
            Assert.False(window.AreTrafficLightsVisible);
            Assert.Equal(Color.Parse("#F5F3FA"), ThemePackService.ColorOf("AppBg"));

            WriteEvidence("layout/switching.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1");
                writer.WriteString("generated_by", "ThemeLayoutsTests.SwitchingLayoutPacks_MovesNavHosts_AndAppliesBookshelfAndSettingsLayouts");
                writer.WriteStartArray("switches");
                foreach (var expected in MacosLayoutPacks)
                {
                    writer.WriteStartObject();
                    writer.WriteString("pack_id", expected.Id);
                    writer.WriteString("layout_kind", expected.Kind.ToString());
                    writer.WriteString("nav_host", NavHostName(expected.Kind));
                    writer.WriteString("shelf_style", ThemePacks.ById(expected.Id).Layout.Shelf.ToString());
                    writer.WriteString("settings_style", ThemePacks.ById(expected.Id).Layout.Settings.ToString());
                    writer.WriteBoolean("nav_buttons_total_4", true);
                    writer.WriteEndObject();
                }

                writer.WriteEndArray();
                writer.WriteBoolean("legacy_pack_returns_to_sonoma", true);
                writer.WriteEndObject();
            });
        }
        finally
        {
            window.Close();
        }
    }

    // ---------------------------------------------------------------- AC3: hot switch p95

    [AvaloniaFact]
    public void LayoutAndVariantHotSwitch_P95Under100ms()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var window = CreateShellWindow();
        try
        {
            // Warm-up (not measured) so JIT / first-render / first-layout costs are excluded.
            foreach (var expected in MacosLayoutPacks)
            {
                ThemePackService.Apply(application, ThemePacks.ById(expected.Id));
                window.OnThemeApplied();
                Pump(2);
            }

            var layoutSamples = new List<(string PackId, LayoutKind Kind, double Ms)>();
            var packs = MacosLayoutPacks.Select(entry => ThemePacks.ById(entry.Id)).ToArray();
            for (var cycle = 0; cycle < 12; cycle++)
            {
                foreach (var pack in packs)
                {
                    var watch = Stopwatch.StartNew();
                    ThemePackService.Apply(application, pack);
                    window.OnThemeApplied();
                    Dispatcher.UIThread.RunJobs();
                    watch.Stop();
                    layoutSamples.Add((pack.Id, pack.Layout.Kind, watch.Elapsed.TotalMilliseconds));
                    Assert.Equal(pack.Layout.Kind, window.CurrentLayout);
                    Assert.Equal(pack.Layout.Kind, window.BookshelfPageControl.CurrentLayout);
                    Assert.Equal(pack.Layout.Kind, window.Settings.CurrentLayout);
                }
            }

            var variantSamples = new List<(string Variant, double Ms)>();
            ThemePackService.Apply(application, packs[1]);
            window.OnThemeApplied();
            Pump(2);
            for (var i = 0; i < 36; i++)
            {
                var dark = i % 2 == 0;
                var watch = Stopwatch.StartNew();
                ThemePackService.ApplyVariant(application, dark ? Avalonia.Styling.ThemeVariant.Dark : Avalonia.Styling.ThemeVariant.Light);
                window.OnThemeApplied();
                Dispatcher.UIThread.RunJobs();
                watch.Stop();
                variantSamples.Add((dark ? "Dark" : "Light", watch.Elapsed.TotalMilliseconds));
                // A variant switch must never change the layout.
                Assert.Equal(LayoutKind.Launchpad, window.CurrentLayout);
                Assert.Equal(LayoutKind.Launchpad, window.BookshelfPageControl.CurrentLayout);
            }

            var layoutP95 = P95(layoutSamples.Select(sample => sample.Ms));
            var variantP95 = P95(variantSamples.Select(sample => sample.Ms));
            Assert.True(layoutSamples.Count >= 30, $"need >=30 layout samples, got {layoutSamples.Count}");
            Assert.True(variantSamples.Count >= 30, $"need >=30 variant samples, got {variantSamples.Count}");
            Assert.True(layoutP95 <= LayoutP95BudgetMs, $"layout switch p95={layoutP95:F2}ms must be <= {LayoutP95BudgetMs}ms");
            Assert.True(variantP95 <= LayoutP95BudgetMs, $"variant switch p95={variantP95:F2}ms must be <= {LayoutP95BudgetMs}ms");

            WriteEvidence("layout/hot-switch.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC3");
                writer.WriteString("generated_by", "ThemeLayoutsTests.LayoutAndVariantHotSwitch_P95Under100ms");
                writer.WriteString("mechanism", "ThemePackService.Apply/ApplyVariant + MainWindow.OnThemeApplied (shell + BookshelfPage + SettingsPage relayout) + Dispatcher.UIThread.RunJobs");
                writer.WriteNumber("threshold", LayoutP95BudgetMs);
                writer.WriteStartObject("layout_switch");
                writer.WriteNumber("samples", layoutSamples.Count);
                writer.WriteNumber("cycles", 12);
                writer.WriteNumber("p95_ms", Math.Round(layoutP95, 3));
                writer.WriteNumber("max_ms", Math.Round(layoutSamples.Max(sample => sample.Ms), 3));
                writer.WriteNumber("min_ms", Math.Round(layoutSamples.Min(sample => sample.Ms), 3));
                writer.WriteBoolean("p95_pass", layoutP95 <= LayoutP95BudgetMs);
                writer.WriteStartArray("samples");
                foreach (var sample in layoutSamples)
                {
                    writer.WriteStartObject();
                    writer.WriteString("pack_id", sample.PackId);
                    writer.WriteString("layout_kind", sample.Kind.ToString());
                    writer.WriteNumber("ms", Math.Round(sample.Ms, 3));
                    writer.WriteEndObject();
                }

                writer.WriteEndArray();
                writer.WriteEndObject();
                writer.WriteStartObject("variant_switch");
                writer.WriteNumber("samples", variantSamples.Count);
                writer.WriteNumber("p95_ms", Math.Round(variantP95, 3));
                writer.WriteNumber("max_ms", Math.Round(variantSamples.Max(sample => sample.Ms), 3));
                writer.WriteNumber("min_ms", Math.Round(variantSamples.Min(sample => sample.Ms), 3));
                writer.WriteBoolean("p95_pass", variantP95 <= LayoutP95BudgetMs);
                writer.WriteBoolean("layout_unchanged", true);
                writer.WriteStartArray("samples");
                foreach (var sample in variantSamples)
                {
                    writer.WriteStartObject();
                    writer.WriteString("variant", sample.Variant);
                    writer.WriteNumber("ms", Math.Round(sample.Ms, 3));
                    writer.WriteEndObject();
                }

                writer.WriteEndArray();
                writer.WriteEndObject();
                writer.WriteEndObject();
            });
        }
        finally
        {
            window.Close();
        }
    }

    // ---------------------------------------------------------------- AC2: 12 real headless-Skia screenshots

    [AvaloniaFact]
    public void TwelveRealScreenshots_ShowThreeDifferentLayoutsInLightAndDark()
    {
        var application = Application.Current!;
        var directory = Path.Combine(Evidence.Directory, "screenshots");
        Directory.CreateDirectory(directory);
        var captures = new List<CaptureInfo>();

        foreach (var expected in MacosLayoutPacks)
        {
            foreach (var variant in new[] { ("light", Avalonia.Styling.ThemeVariant.Light), ("dark", Avalonia.Styling.ThemeVariant.Dark) })
            {
                var pack = ThemePacks.ById(expected.Id);
                ThemePackService.Apply(application, pack);
                ThemePackService.ApplyVariant(application, variant.Item2);

                var expectedAppBg = ThemePackMetrics.IsDark(variant.Item2)
                    ? pack.DarkTokens!["AppBg"]
                    : pack.Tokens["AppBg"];
                var window = CreateShellWindow();
                try
                {
                    window.Navigate("bookshelf");
                    Pump(4);
                    captures.Add(Capture(window, directory, $"{KindSlug(expected.Kind)}-bookshelf-{variant.Item1}", expectedAppBg, minimumBackgroundRatio: 0.10));
                    window.Navigate("settings");
                    Pump(4);
                    captures.Add(Capture(window, directory, $"{KindSlug(expected.Kind)}-settings-{variant.Item1}", expectedAppBg, minimumBackgroundRatio: 0.02));
                }
                finally
                {
                    window.Close();
                }
            }
        }

        Assert.Equal(12, captures.Count);
        // 12 named frames. Other suites also write into the shared evidence root, so check the 12 names
        // instead of the total file count of the directory.
        foreach (var expected in MacosLayoutPacks)
        {
            foreach (var page in new[] { "bookshelf", "settings" })
            {
                foreach (var variant in new[] { "light", "dark" })
                {
                    var expectedPath = Path.Combine(directory, $"{KindSlug(expected.Kind)}-{page}-{variant}.png");
                    Assert.True(File.Exists(expectedPath), $"missing screenshot {expectedPath}");
                }
            }
        }

        // Light and Dark of the same layout/page are visibly different frames.
        foreach (var expected in MacosLayoutPacks)
        {
            var slug = KindSlug(expected.Kind);
            foreach (var page in new[] { "bookshelf", "settings" })
            {
                var light = captures.Single(capture => capture.Name == $"{slug}-{page}-light");
                var dark = captures.Single(capture => capture.Name == $"{slug}-{page}-dark");
                Assert.NotEqual(light.PrimaryBackground, dark.PrimaryBackground);
                Assert.True(CellDifference(light.Signature, dark.Signature) >= 10,
                    $"{slug}-{page}: light and dark frames look structurally identical");
            }
        }

        // The three layouts are structurally different for the same page + variant (pixel distribution differs).
        var pairDiffs = new List<(string Page, string Variant, string Left, string Right, int Cells)>();
        foreach (var page in new[] { "bookshelf", "settings" })
        {
            foreach (var variant in new[] { "light", "dark" })
            {
                foreach (var pair in new[] { ("sonoma", "launchpad"), ("sonoma", "split"), ("launchpad", "split") })
                {
                    var left = captures.Single(capture => capture.Name == $"{pair.Item1}-{page}-{variant}");
                    var right = captures.Single(capture => capture.Name == $"{pair.Item2}-{page}-{variant}");
                    var cells = CellDifference(left.Signature, right.Signature);
                    pairDiffs.Add((page, variant, pair.Item1, pair.Item2, cells));
                    Assert.True(cells >= 10,
                        $"{page}/{variant}: {pair.Item1} and {pair.Item2} differ in only {cells}/160 cells — layouts are not distinct");
                }
            }
        }

        WriteEvidence("layout/screenshots.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteString("generated_by", "ThemeLayoutsTests.TwelveRealScreenshots_ShowThreeDifferentLayoutsInLightAndDark");
            writer.WriteString("renderer", "Avalonia.Headless + Skia (UseHeadlessDrawing=false) CaptureRenderedFrame()");
            writer.WriteNumber("width", 1280);
            writer.WriteNumber("height", 820);
            writer.WriteNumber("captures_total", captures.Count);
            writer.WriteStartArray("captures");
            foreach (var capture in captures)
            {
                writer.WriteStartObject();
                writer.WriteString("name", capture.Name);
                writer.WriteString("path", "screenshots/" + capture.Name + ".png");
                writer.WriteString("layout_kind", capture.LayoutKind.ToString());
                writer.WriteNumber("width", capture.Width);
                writer.WriteNumber("height", capture.Height);
                writer.WriteNumber("bytes", capture.Bytes);
                writer.WriteString("expected_app_bg", capture.ExpectedAppBg);
                writer.WriteString("primary_background", capture.PrimaryBackground);
                writer.WriteNumber("sampled_pixels", capture.SampledPixels);
                writer.WriteNumber("matched_app_bg_samples", capture.MatchedSamples);
                writer.WriteNumber("matched_app_bg_ratio", Math.Round(capture.BackgroundRatio, 4));
                writer.WriteNumber("distinct_colors", capture.DistinctColors);
                writer.WriteStartArray("signature_cells");
                foreach (var value in capture.Signature)
                {
                    writer.WriteNumberValue(Math.Round(value, 2));
                }

                writer.WriteEndArray();
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteStartArray("pairwise_layout_cell_diffs");
            foreach (var pair in pairDiffs)
            {
                writer.WriteStartObject();
                writer.WriteString("page", pair.Page);
                writer.WriteString("variant", pair.Variant);
                writer.WriteString("left", pair.Left);
                writer.WriteString("right", pair.Right);
                writer.WriteNumber("differing_cells", pair.Cells);
                writer.WriteNumber("cells_total", 160);
                writer.WriteBoolean("pass", pair.Cells >= 10);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteNumber("threshold_cells", 10);
            writer.WriteBoolean("all_pairs_distinct", pairDiffs.All(pair => pair.Cells >= 10));
            writer.WriteBoolean("light_and_dark_distinct", true);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- AC4: legacy pack zero-regression

    [AvaloniaFact]
    public void LegacyPacks_KeepSonomaStructure_AndExistingGridThemeListAssertions()
    {
        var application = Application.Current!;
        ThemePackService.Apply(application, ThemePacks.Default);
        var window = CreateShellWindow();
        try
        {
            foreach (var expected in LegacyPacks)
            {
                var pack = ThemePacks.ById(expected.Id);
                window.Settings.SelectTheme(pack);
                Pump(2);

                AssertShellLayout(window, LayoutKind.Sonoma);
                Assert.False(window.AreTrafficLightsVisible);

                var bookshelf = window.BookshelfPageControl;
                // THEME-MACOS-1 structure survives verbatim: root row 0 is the header slot holding the
                // gradient header Border, row 1 is the scrolling body.
                var root = Assert.IsType<Grid>(bookshelf.Content);
                var headerSlot = Assert.IsType<Grid>(root.Children[0]);
                Assert.Same(bookshelf.Header, headerSlot.Children[0]);
                Assert.NotNull(bookshelf.SearchBox);
                Assert.NotNull(bookshelf.GridPanel);
                Assert.NotNull(bookshelf.DetailPanel);
                Assert.NotNull(bookshelf.ImportFilesButton);
                Assert.NotNull(bookshelf.ImportFolderButton);
                Assert.NotNull(FindButton(bookshelf.Header, "NewBookButton"));

                // Existing 1400-wide 7-column assertion stays true.
                bookshelf.ViewModel.UpdateViewport(1400);
                Pump(1);
                Assert.Equal(7, bookshelf.GridPanel.Columns);
                bookshelf.ViewModel.SetBooks(new[]
                {
                    new BookCardItem { BookId = "b1", Title = "雾港来信", Tag = "未分类" },
                    new BookCardItem { BookId = "b2", Title = "Saber 画集", Tag = "收藏" },
                });
                Assert.Equal(3, bookshelf.TagChips.ItemCount);

                // Settings keeps its public members + item counts in the Sonoma layout.
                Assert.Equal(ThemePacks.All.Count, window.Settings.ThemeList.ItemCount);
                Assert.True(window.Settings.NsList.Children.Count >= 1);
                Assert.False(window.Settings.AppearanceRow.IsVisible, "single-token packs hide the appearance row");
                Assert.Equal(12d, window.Settings.ThemeCard.CornerRadius.TopLeft);

                Assert.Equal(Color.Parse(expected.AppBg), ThemePackService.ColorOf("AppBg"));
            }
        }
        finally
        {
            window.Close();
        }
    }

    // ---------------------------------------------------------------- helpers

    private sealed record CaptureInfo(
        string Name,
        LayoutKind LayoutKind,
        int Width,
        int Height,
        long Bytes,
        string ExpectedAppBg,
        string PrimaryBackground,
        int SampledPixels,
        int MatchedSamples,
        double BackgroundRatio,
        int DistinctColors,
        double[] Signature);

    private static void AssertShellLayout(MainWindow window, LayoutKind kind)
    {
        Assert.Equal(kind, window.CurrentLayout);
        Assert.Equal(kind, window.Layout.Kind);
        Assert.Equal(kind, window.BookshelfPageControl.CurrentLayout);
        Assert.Equal(kind, window.Settings.CurrentLayout);
        Assert.Equal(4, window.NavButtons.Count);

        var expectedHost = kind switch
        {
            LayoutKind.Launchpad => (Control)window.DockNavPanelControl,
            LayoutKind.Split => window.SidebarNavPanelControl,
            _ => window.NavPanelControl,
        };
        foreach (var button in window.NavButtons.Values)
        {
            Assert.Same(expectedHost, button.Parent);
        }

        Assert.Equal(kind == LayoutKind.Sonoma, window.NavPanelControl.IsVisible);
        Assert.Equal(kind == LayoutKind.Launchpad, window.DockHostControl.IsVisible);
        Assert.Equal(kind == LayoutKind.Split, window.SidebarHostControl.IsVisible);
        if (kind == LayoutKind.Split)
        {
            Assert.Equal(220d, window.SidebarHostControl.Bounds.Width);
        }

        if (kind == LayoutKind.Launchpad)
        {
            Assert.Equal(76d, window.DockHostControl.Bounds.Height);
        }
    }

    private static string NavHostName(LayoutKind kind) => kind switch
    {
        LayoutKind.Launchpad => "DockHost",
        LayoutKind.Split => "SidebarHost",
        _ => "TitleBar/NavPanel",
    };

    private static void AssertBookshelfMembersAvailable(BookshelfPage page)
    {
        Assert.NotNull(page.SearchBox);
        Assert.NotNull(page.BookGrid);
        Assert.NotNull(page.GridPanel);
        Assert.NotNull(page.DetailPanel);
        Assert.NotNull(page.Header);
        Assert.NotNull(page.EmptyPanel);
        Assert.NotNull(page.NoResultsPanel);
        Assert.NotNull(page.SplitBookList);
        Assert.NotNull(page.ImportFilesButton);
        Assert.NotNull(page.ImportFolderButton);
        Assert.NotNull(FindButton(page.Header, "NewBookButton"));
        Assert.True(page.GridPanel.Columns >= 2, "book grid must keep a usable column count in every layout");
    }

    /// <summary>Locates a named button in the logical tree (code-built pages have no XAML name scope).</summary>
    private static Button? FindButton(Control root, string name) =>
        root.GetLogicalDescendants().OfType<Button>().FirstOrDefault(button => string.Equals(button.Name, name, StringComparison.Ordinal));

    private static void AssertSettingsMembersAvailable(SettingsPage page)
    {
        Assert.Equal(ThemePacks.All.Count, page.ThemeList.ItemCount);
        Assert.True(page.ThemeButtons.Count == ThemePacks.All.Count,
            $"theme buttons realised: {page.ThemeButtons.Count} (packs: {ThemePacks.All.Count})");
        Assert.NotNull(page.ThemeCard);
        Assert.NotNull(page.AppearanceRow);
        Assert.NotNull(page.LightVariantButton);
        Assert.NotNull(page.DarkVariantButton);
        Assert.True(page.NsList.Children.Count >= 1);
        Assert.NotNull(page.Credentials);
        Assert.NotNull(page.ProviderProfiles);
        Assert.NotNull(page.NetworkProfiles);
        Assert.NotNull(page.Bindings);
        Assert.Equal(6, page.SplitSectionButtons.Count);
    }

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
        Pump(4);
        return window;
    }

    private static void Pump(int rounds)
    {
        for (var i = 0; i < rounds; i++)
        {
            Dispatcher.UIThread.RunJobs();
        }
    }

    private static CaptureInfo Capture(MainWindow window, string directory, string name, string expectedAppBgHex, double minimumBackgroundRatio)
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
            Assert.True(distinct.Count > 20, $"{name}: only {distinct.Count} distinct colours (placeholder?)");

            var layoutKind = window.CurrentLayout;
            return new CaptureInfo(
                name,
                layoutKind,
                bitmap.Width,
                bitmap.Height,
                bytes,
                expectedAppBgHex,
                expected.ToString(),
                total,
                matched,
                ratio,
                distinct.Count,
                Signature(bitmap));
        }
    }

    /// <summary>16x10 cell mean luminance: a coarse structural fingerprint used to prove layouts differ.</summary>
    private static double[] Signature(SKBitmap bitmap)
    {
        const int columns = 16;
        const int rows = 10;
        var cellWidth = bitmap.Width / columns;
        var cellHeight = bitmap.Height / rows;
        var signature = new double[columns * rows];
        for (var row = 0; row < rows; row++)
        {
            for (var column = 0; column < columns; column++)
            {
                double sum = 0;
                var count = 0;
                for (var y = row * cellHeight; y < (row + 1) * cellHeight; y += 6)
                {
                    for (var x = column * cellWidth; x < (column + 1) * cellWidth; x += 6)
                    {
                        var pixel = bitmap.GetPixel(x, y);
                        sum += 0.2126 * pixel.Red + 0.7152 * pixel.Green + 0.0722 * pixel.Blue;
                        count++;
                    }
                }

                signature[row * columns + column] = sum / count;
            }
        }

        return signature;
    }

    private static int CellDifference(double[] left, double[] right)
    {
        Assert.Equal(left.Length, right.Length);
        var differing = 0;
        for (var i = 0; i < left.Length; i++)
        {
            if (Math.Abs(left[i] - right[i]) >= 8)
            {
                differing++;
            }
        }

        return differing;
    }

    private static string KindSlug(LayoutKind kind) => kind switch
    {
        LayoutKind.Launchpad => "launchpad",
        LayoutKind.Split => "split",
        _ => "sonoma",
    };

    private static double P95(IEnumerable<double> samples)
    {
        var sorted = samples.OrderBy(value => value).ToArray();
        return sorted[(int)Math.Ceiling(sorted.Length * 0.95) - 1];
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

    private static void WriteEvidence(string relativePath, Action<Utf8JsonWriter> write)
    {
        var path = Path.Combine(Evidence.Directory, relativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions
        {
            Indented = true,
            // Evidence JSON should stay human-readable for the Chinese pack labels.
            Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        });
        write(writer);
    }
}
