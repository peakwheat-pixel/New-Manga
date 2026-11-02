using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// FEA-06-RESIDUAL-2 IN-2A: effective-property assertions for the residual component-state cells of
/// `verification/FEA-06-RESIDUAL-1/component-state-matrix.md` (current snapshot). PASS means the value
/// resolved on the attached control equals the existing design token resolved from the same resource
/// stack — never a selector string. Expected values and their anchors are frozen per group in
/// `verification/FEA-06-RESIDUAL-2/expected-tokens.md`, including actual SurfaceCard/IconButton state channels.
/// PrimaryButton(disabled) is a re-assertion: the matrix already lists it EFFECTIVE (scope-r3 R3R-004).
/// </summary>
public sealed class FluentResidual2StateEffectiveTests
{
    private static void RunJobs() => Dispatcher.UIThread.RunJobs();

    private static Color TokenColor(Application app, string key) => ThemeTestHarness.ColorOf(app, key);

    private static Color Solid(IBrush? brush) => Assert.IsAssignableFrom<ISolidColorBrush>(brush).Color;

    private static void MoveTo(Window window, Control control) =>
        window.MouseMove(
            control.TranslatePoint(new Point(control.Bounds.Width / 2, control.Bounds.Height / 2), window)
                ?? throw new InvalidOperationException("control not in the window tree"),
            RawInputModifiers.None);

    private static void Press(Window window, Control control) =>
        window.MouseDown(
            control.TranslatePoint(new Point(control.Bounds.Width / 2, control.Bounds.Height / 2), window)!.Value,
            MouseButton.Left, RawInputModifiers.None);

    private static void Release(Window window, Control control) =>
        window.MouseUp(
            control.TranslatePoint(new Point(control.Bounds.Width / 2, control.Bounds.Height / 2), window)!.Value,
            MouseButton.Left, RawInputModifiers.None);

    [AvaloniaFact]
    public void SurfaceCard_HoverSelectedDisabled_ResolveTheFrozenStateChannels()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var card = new SurfaceCard { Width = 160, Height = 72 };
        var window = new Window { Width = 480, Height = 320, Content = card };
        try
        {
            window.Show();
            RunJobs();
            void AssertDefaultTokens(string context)
            {
                Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(card.Background));
                Assert.Equal(ThemeTestHarness.ValueOf<Thickness>(app, "Nm.Border.Hairline"), card.BorderThickness);
                Assert.Equal(ThemeTestHarness.ValueOf<CornerRadius>(app, "Nm.Corner.Fluent.Md"), card.CornerRadius);
                Assert.Equal(ThemeTestHarness.ValueOf<BoxShadows>(app, "Nm.Elevation.1"), card.BoxShadow);
                _ = context;
            }

                        // default
            AssertDefaultTokens("default");
            Assert.Equal(TokenColor(app, "Nm.Color.Line.Subtle"), Solid(card.BorderBrush));
            // hover (R2-011): border channel = Line.Default
            MoveTo(window, card);
            RunJobs();
            Assert.True(card.IsPointerOver);
            Assert.Equal(TokenColor(app, "Nm.Color.Line.Default"), Solid(card.BorderBrush));
            // selected (R2-011): accent border + elevation 2
            card.Classes.Add("selected");
            RunJobs();
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(card.BorderBrush));
            Assert.Equal(ThemeTestHarness.ValueOf<BoxShadows>(app, "Nm.Elevation.2"), card.BoxShadow);
            // disabled (R2-011): opacity token
            card.IsEnabled = false;
            RunJobs();
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled"), card.Opacity);
            Assert.False(card.IsEffectivelyEnabled);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void IconButton_Checked_ResolvesTheAccentMutedStateChannel()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var button = new Button { Content = "图标", Classes = { "fluent-icon" }, Width = 40 };
        var window = new Window { Width = 160, Height = 80, Content = button };
        try
        {
            window.Show();
            RunJobs();
            button.Classes.Add("checked");
            RunJobs();
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(button.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(button.BorderBrush));
        }
        finally { window.Close(); }
    }
    [AvaloniaFact]
    public void BookCardAndBookRow_Disabled_ResolveTheDisabledOpacityToken()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var card = new BookCard { Content = "作品", Width = 160, Height = 72 };
        var row = new BookRow { Content = "作品行", Width = 240, Height = 36 };
        var window = new Window { Width = 480, Height = 320, Content = new StackPanel { Children = { card, row } } };
        try
        {
            window.Show();
            RunJobs();
            card.IsEnabled = false;
            row.IsEnabled = false;
            RunJobs();
            var disabledOpacity = ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled");
            Assert.False(card.IsEffectivelyEnabled);
            Assert.Equal(disabledOpacity, card.Opacity);
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(card.Background)); // keeps its surface
            Assert.False(row.IsEffectivelyEnabled);
            Assert.Equal(disabledOpacity, row.Opacity);
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Canvas"), Solid(row.Background));
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void PrimarySecondaryDangerButtons_Disabled_ResolveTheFrozenDisabledTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var primary = new Button { Content = "主操作", Classes = { "fluent-primary" } };
        var secondary = new Button { Content = "次操作", Classes = { "fluent-secondary" } };
        var danger = new Button { Content = "危险", Classes = { "fluent-danger" } };
        var window = new Window
        {
            Width = 480, Height = 320,
            Content = new StackPanel { Children = { primary, secondary, danger } },
        };
        try
        {
            window.Show();
            RunJobs();
            primary.IsEnabled = secondary.IsEnabled = danger.IsEnabled = false;
            RunJobs();
            var disabledOpacity = ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled");
            var disabledText = TokenColor(app, "Nm.Color.Text.Disabled");

            // PrimaryButton(disabled) is a re-assertion (matrix already EFFECTIVE, scope-r3 R3R-004).
            Assert.Equal(disabledOpacity, primary.Opacity);
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(primary.Background));
            Assert.Equal(disabledText, Solid(primary.Foreground));

            Assert.Equal(disabledOpacity, secondary.Opacity);
            Assert.Equal(disabledText, Solid(secondary.Foreground));
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(secondary.Background));

            Assert.Equal(disabledOpacity, danger.Opacity);
            Assert.Equal(disabledText, Solid(danger.Foreground));
            Assert.Equal(TokenColor(app, "Nm.Color.Status.Failed"), Solid(danger.BorderBrush)); // outline stays failed
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void IconButton_HoverResolvesAccentMuted_CheckedResolvesTheStateChannel()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var icon = new Button { Content = "★", Classes = { "fluent-icon" }, Width = 40, Height = 40 };
        var window = new Window { Width = 240, Height = 160, Content = icon };
        try
        {
            window.Show();
            RunJobs();
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(icon.Background)); // default
            MoveTo(window, icon);
            RunJobs();
            Assert.True(icon.IsPointerOver);
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(icon.Background)); // hover

            // R2-011: the checked class now has a real style channel (accent muted + accent border).
            window.MouseMove(new Point(5, 5), RawInputModifiers.None);
            RunJobs();
            icon.Classes.Add("checked");
            RunJobs();
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(icon.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(icon.BorderBrush));
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ToggleSwitch_Disabled_ResolvesTheDisabledOpacityToken()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var toggle = new ToggleSwitch { Content = "选项" };
        var window = new Window { Width = 240, Height = 160, Content = toggle };
        try
        {
            window.Show();
            RunJobs();
            toggle.IsEnabled = false;
            RunJobs();
            Assert.False(toggle.IsEffectivelyEnabled);
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled"), toggle.Opacity);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void Slider_NormalHoverDisabled_ResolveTheAccentAndOpacityTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var slider = new Slider { Minimum = 0, Maximum = 100, Value = 40, Width = 220 };
        var window = new Window { Width = 320, Height = 160, Content = slider };
        try
        {
            window.Show();
            RunJobs();
            var thumb = slider.GetVisualDescendants().OfType<Avalonia.Controls.Primitives.Thumb>().Single();
            var thumbBorder = thumb.GetVisualDescendants().OfType<Border>().Single();
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(thumb.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(thumbBorder.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(slider.Foreground)); // normal
            MoveTo(window, slider);
            RunJobs();
            Assert.True(slider.IsPointerOver);
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Hover"), Solid(slider.Foreground)); // hover
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Hover"), Solid(thumbBorder.Background));
            window.MouseMove(new Point(5, 5), RawInputModifiers.None);
            RunJobs();
            slider.IsEnabled = false;
            RunJobs();
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled"), slider.Opacity);
            Assert.Equal(TokenColor(app, "Nm.Color.Text.Disabled"), Solid(thumbBorder.Background));
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void SegmentedControl_SelectedUnselectedHoverPressed_ResolveTheSegmentTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var segmented = new SegmentedControl { Items = ["页面", "批量", "控制台"], SelectedIndex = 0, Width = 320 };
        var window = new Window { Width = 480, Height = 200, Content = segmented };
        try
        {
            window.Show();
            RunJobs();
            var items = segmented.GetVisualDescendants().OfType<Button>().ToList();
            Assert.Equal(3, items.Count);
            var selected = items[0];
            var unselected = items[1];

            // selected / unselected (Controls.Custom.axaml segmented-item styles)
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(selected.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(selected.BorderBrush));
            Assert.Equal(TokenColor(app, "Nm.Color.Text.Primary"), Solid(selected.Foreground));
            Assert.Equal(TokenColor(app, "Nm.Color.Text.Secondary"), Solid(unselected.Foreground));

            // hover on the unselected segment
            MoveTo(window, unselected);
            RunJobs();
            Assert.True(unselected.IsPointerOver);
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Overlay"), Solid(unselected.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Text.Primary"), Solid(unselected.Foreground));

            // pressed on the same segment
            Press(window, unselected);
            RunJobs();
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(unselected.Background));
            Release(window, unselected);
            RunJobs();
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void TabItem_Hover_ResolvesTextPrimaryAndRaisedTemplateBackground()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var first = new TabItem { Header = "页面", IsSelected = true };
        var second = new TabItem { Header = "批量" };
        var tabs = new TabControl { Width = 360, Height = 160, Items = { first, second } };
        var window = new Window { Width = 480, Height = 280, Content = tabs };
        try
        {
            window.Show();
            RunJobs();
            Assert.Equal(TokenColor(app, "Nm.Color.Text.Secondary"), Solid(second.Foreground)); // unselected
            MoveTo(window, second);
            RunJobs();
            Assert.True(second.IsPointerOver);
            // Themes/Controls/TabItem.axaml hover: foreground token on the item, raised token in the template.
            // Controls.Custom.axaml overrides the theme hover foreground with Accent.Hover.
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Hover"), Solid(second.Foreground));
            var layoutRoot = second.GetVisualDescendants().OfType<Border>()
                .Single(border => border.Name == "PART_LayoutRoot");
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(layoutRoot.Background));
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void SearchField_Focus_KeepsTheFrozenInputBorderTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var field = new SearchField { Width = 260 };
        var window = new Window { Width = 420, Height = 180, Content = field };
        try
        {
            window.Show();
            RunJobs();
            var box = field.GetVisualDescendants().OfType<TextBox>().Single();
            var border = box.GetVisualDescendants().OfType<Border>()
                .Single(border => border.Name == "PART_BorderElement");
            var idleBrush = Solid(border.BorderBrush);
            var idleThickness = border.BorderThickness;
            box.Focus(Avalonia.Input.NavigationMethod.Tab);
            RunJobs();
            Assert.True(box.IsFocused);
            var ring = window.GetVisualDescendants().OfType<Border>().Single(b => b.Classes.Contains("nm-focus-ring"));
            Assert.True(ring.IsVisible);
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(ring.BorderBrush));
            Assert.Equal(ThemeTestHarness.ValueOf<Thickness>(app, "Nm.Border.Focus"), ring.BorderThickness);
            // Inputs.axaml focus overrides the Fluent template emphasis back onto the frozen tokens:
            // the inner border keeps idle geometry/colour; the accent focus signal is the outside ring.
            Assert.Equal(idleBrush, Solid(border.BorderBrush));
            Assert.Equal(idleThickness, border.BorderThickness);
            Assert.Equal(TokenColor(app, "Nm.Color.Line.Default"), Solid(border.BorderBrush));
            Assert.Equal(ThemeTestHarness.ValueOf<Thickness>(app, "Nm.Border.Hairline"), border.BorderThickness);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void SettingsField_ErrorAndDisabled_ResolveTheFailedBorderAndDisabledOpacity()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var errored = new SettingsField();
        var label = new TextBlock { Text = "标签" };
        var errorInput = new TextBox();
        errored.Children.Add(label);
        errored.Children.Add(errorInput);
        Grid.SetColumn(errorInput, 1);
        errorInput.Classes.Add("invalid"); // the settings error channel (Inputs.axaml TextBox.invalid)
        var disabledInput = new TextBox { IsEnabled = false, Watermark = "不可用" };
        var disabledField = new SettingsField();
        disabledField.Children.Add(new TextBlock { Text = "禁用项" });
        disabledField.Children.Add(disabledInput);
        Grid.SetColumn(disabledInput, 1);
        var window = new Window
        {
            Width = 480, Height = 240,
            Content = new StackPanel { Children = { errored, disabledField } },
        };
        try
        {
            window.Show();
            RunJobs();
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Space.3"), errored.ColumnSpacing);
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Space.2"), errored.RowSpacing);
            var errorBorder = errorInput.GetVisualDescendants().OfType<Border>()
                .Single(border => border.Name == "PART_BorderElement");
            Assert.Equal(TokenColor(app, "Nm.Color.Status.Failed"), Solid(errorBorder.BorderBrush));
            Assert.False(disabledInput.IsEffectivelyEnabled);
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled"), disabledInput.Opacity);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void RegionBox_Hover_ResolvesTheAccentHoverBackground()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var box = new RegionBox { Width = 120, Height = 64, Child = new TextBlock { Text = "region" } };
        var window = new Window { Width = 320, Height = 200, Content = box };
        try
        {
            window.Show();
            RunJobs();
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(box.Background)); // default
            MoveTo(window, box);
            RunJobs();
            Assert.True(box.IsPointerOver);
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Hover"), Solid(box.Background)); // hover
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ContextMenu_DisabledItem_ResolvesTheDisabledOpacityToken()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var host = new Button { Content = "宿主", Width = 160, Height = 40 };
        var disabled = new MenuItem { Header = "不可用", IsEnabled = false };
        var enabled = new MenuItem { Header = "可用" };
        var menu = new ContextMenu { Items = { enabled, disabled } };
        host.ContextMenu = menu;
        var window = new Window { Width = 320, Height = 200, Content = host };
        try
        {
            window.Show();
            RunJobs();
            menu.Open(host);
            RunJobs();
            Assert.True(menu.IsOpen);
            Assert.Equal(1d, enabled.Opacity); // control: enabled item is unaffected
            Assert.False(disabled.IsEffectivelyEnabled);
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled"), disabled.Opacity);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void Tooltip_Opened_ResolvesTheOverlaySurfaceTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var tip = new ToolTip { Content = "提示文本" };
        var host = new Button { Content = "悬停我", Width = 160, Height = 40 };
        ToolTip.SetTip(host, tip);
        var window = new Window { Width = 320, Height = 200, Content = host };
        try
        {
            window.Show();
            RunJobs();
            ToolTip.SetIsOpen(host, true);
            RunJobs();
            Assert.True(ToolTip.GetIsOpen(host));
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Overlay"), Solid(tip.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Line.Default"), Solid(tip.BorderBrush));
            Assert.Equal(TokenColor(app, "Nm.Color.Text.Primary"), Solid(tip.Foreground));
            Assert.Equal(ThemeTestHarness.ValueOf<Thickness>(app, "Nm.Border.Hairline"), tip.BorderThickness);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void DerivedControls_ResolveTheirClassSelectorsToTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var chapters = new ChapterList(); var thumb = new StreamingThumb();
        var reader = new ReaderPage(); var progress = new ReaderProgressBar { Value = 60 };
        var group = new SettingsGroup(); var tabs = new TabStrip();
        var window = new Window { Width = 640, Height = 480,
            Content = new StackPanel { Children = { chapters, thumb, reader, progress, group, tabs } } };
        try
        {
            window.Show(); RunJobs();
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Space.2"), chapters.Spacing);
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(thumb.Background));
            Assert.Equal(ThemeTestHarness.ValueOf<CornerRadius>(app, "Nm.Corner.Fluent.Sm"), thumb.CornerRadius);
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Sunken"), Solid(reader.Background));
            Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(progress.Foreground));
            Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(group.Background));
            Assert.Equal(ThemeTestHarness.ValueOf<Thickness>(app, "Nm.Padding.Card"), group.Padding);
            Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Space.2"), tabs.Spacing);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ReaderProgressAndThumbStrip_ResolveRealTemplatesAndContent()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var progress = new ReaderProgressBar { Width = 260, Height = 12, Value = 60, Maximum = 100 };
        var strip = new PageThumbStrip { ItemsSource = new[] { "page-1", "page-2" } };
        var window = new Window { Width = 480, Height = 240, Content = new StackPanel { Children = { progress, strip } } };
        try
        {
            window.Show(); RunJobs();
            Assert.NotNull(progress.Template);
            Assert.Contains(progress.GetVisualDescendants().OfType<Border>(), b => b.Bounds.Width > 0);
            Assert.NotNull(strip.Template);
            Assert.Contains(strip.GetVisualDescendants().OfType<TextBlock>(), t => t.Text == "page-1");
            Assert.Contains(strip.GetVisualDescendants().OfType<StackPanel>(), p => p.Orientation == Avalonia.Layout.Orientation.Horizontal);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void AlertBanner_AllNineSeverities_ResolveTheFrozenStatusTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;
        var banners = Enum.GetValues<StatusKind>()
            .ToDictionary(kind => kind, kind => new AlertBanner
            {
                Severity = kind,
                Title = "标题",
                Message = "一句话",
                ActionText = "操作",
            });
        var panel = new StackPanel();
        foreach (var banner in banners.Values) panel.Children.Add(banner);
        var window = new Window { Width = 760, Height = 720, Content = panel };
        try
        {
            window.Show();
            RunJobs();
            // StatusGlyph colours: Controls.Status.axaml maps every StatusKind (NotStarted uses the
            // secondary text token; Locked reuses the blocked status token).
            var glyphKeys = new Dictionary<StatusKind, string>
            {
                [StatusKind.Queued] = "Nm.Color.Status.Queued",
                [StatusKind.Running] = "Nm.Color.Status.Running",
                [StatusKind.Done] = "Nm.Color.Status.Done",
                [StatusKind.Failed] = "Nm.Color.Status.Failed",
                [StatusKind.Blocked] = "Nm.Color.Status.Blocked",
                [StatusKind.Stale] = "Nm.Color.Status.Stale",
                [StatusKind.Skipped] = "Nm.Color.Status.Skipped",
                // D-14: Controls.Status.axaml (style authority) uses Text.Secondary for NotStarted,
                // StatusCatalog.ColorKey still reports Text.Disabled; track until DSH fixes the catalog.
                [StatusKind.NotStarted] = "Nm.Color.Text.Secondary",
                [StatusKind.Locked] = "Nm.Color.Status.Blocked",
            };
            // AlertBanner surfaces: Controls.Custom.axaml gives failed/blocked/stale a status-muted
            // background; every other severity keeps the default panel/line tokens (no channel —
            // the legacy `.interrupted` class is not driven by StatusCatalog).
            var mutedBackgrounds = new Dictionary<StatusKind, (string Background, string Border)>
            {
                [StatusKind.Failed] = ("Nm.Color.StatusMuted.Failed", "Nm.Color.Status.Failed"),
                [StatusKind.Blocked] = ("Nm.Color.StatusMuted.Blocked", "Nm.Color.Status.Blocked"),
                [StatusKind.Stale] = ("Nm.Color.StatusMuted.Stale", "Nm.Color.Status.Stale"),
            };
            foreach (var (kind, banner) in banners)
            {
                var glyph = banner.GetVisualDescendants().OfType<StatusGlyph>().Single();
                Assert.Equal(TokenColor(app, glyphKeys[kind]), Solid(glyph.Foreground));
                if (mutedBackgrounds.TryGetValue(kind, out var surface))
                {
                    Assert.Equal(TokenColor(app, surface.Background), Solid(banner.Background));
                    Assert.Equal(TokenColor(app, surface.Border), Solid(banner.BorderBrush));
                }
                else
                {
                    Assert.Equal(TokenColor(app, "Nm.Color.Bg.Panel"), Solid(banner.Background));
                    Assert.Equal(TokenColor(app, "Nm.Color.Line.Default"), Solid(banner.BorderBrush));
                }

                // Cross-anchor: StatusCatalog names the same colour key this assertion resolved
                // (NotStarted is the tracked D-14 exception: catalog still says Text.Disabled).
                if (kind != StatusKind.NotStarted)
                {
                    Assert.Equal(glyphKeys[kind], StatusCatalog.ColorKey(kind));
                }
            }
        }
        finally { window.Close(); }
    }
}
