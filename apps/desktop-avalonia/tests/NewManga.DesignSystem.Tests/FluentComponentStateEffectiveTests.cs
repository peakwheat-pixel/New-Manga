using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-4: effective-property assertions for the Fluent component state matrix
/// (`10-component-inventory.md` §1/§3). Values are resolved from the real application resources after
/// attaching the control, not inferred from selector strings. Hover/pressed visual cells stay NOT_RUN in
/// the task evidence because headless pseudo-class rendering cannot be asserted reliably.
/// </summary>
public sealed class FluentComponentStateEffectiveTests
{
    [AvaloniaFact]
    public void Fluent_components_resolve_frozen_tokens_for_default_and_disabled_states()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var primary = new Button { Content = "主操作", Classes = { "fluent-primary" } };
        var danger = new Button { Content = "危险", Classes = { "fluent-danger" } };
        var disabled = new Button { Content = "禁用", Classes = { "fluent-primary" }, IsEnabled = false };
        var card = new Border { Classes = { "fluent-surface-card" }, Width = 100, Height = 40 };
        var dialog = new Border { Classes = { "fluent-dialog" }, Width = 120, Height = 60 };
        var window = new Window
        {
            Width = 480,
            Height = 360,
            Content = new StackPanel { Spacing = 8, Children = { primary, danger, disabled, card, dialog } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        // PrimaryButton: normal state = accent background/on-accent foreground + frozen geometry tokens.
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(primary.Background));
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.On"), Solid(primary.Foreground));
        Assert.Equal(ThemeTestHarness.ValueOf<CornerRadius>(app, "Nm.Corner.Fluent.Sm"), primary.CornerRadius);
        Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Size.ControlHeight"), primary.MinHeight);

        // DangerButton: outline uses the failed status colour on both foreground and border.
        Assert.Equal(TokenColor(app, "Nm.Color.Status.Failed"), Solid(danger.Foreground));
        Assert.Equal(TokenColor(app, "Nm.Color.Status.Failed"), Solid(danger.BorderBrush));
        Assert.Equal(ThemeTestHarness.ValueOf<Thickness>(app, "Nm.Border.Hairline"), danger.BorderThickness);

        // Disabled state: opacity token applies and the control reports itself as not effectively enabled.
        Assert.False(disabled.IsEffectivelyEnabled);
        Assert.Equal(ThemeTestHarness.ValueOf<double>(app, "Nm.Opacity.Disabled"), disabled.Opacity);

        // SurfaceCard / Dialog consume elevation + corner tokens.
        Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(card.Background));
        Assert.Equal(ThemeTestHarness.ValueOf<Thickness>(app, "Nm.Border.Hairline"), card.BorderThickness);
        Assert.True(card.BoxShadow.Count > 0);
        Assert.Equal(ThemeTestHarness.ValueOf<CornerRadius>(app, "Nm.Corner.Fluent.Md"), card.CornerRadius);
        Assert.True(dialog.BoxShadow.Count > 0);
        Assert.Equal(ThemeTestHarness.ValueOf<CornerRadius>(app, "Nm.Corner.Fluent.Lg"), dialog.CornerRadius);
        Assert.Equal(ThemeTestHarness.ValueOf<int>(app, "Nm.ZIndex.Modal"), dialog.GetValue(Panel.ZIndexProperty));

        window.Close();
    }

    private static Color TokenColor(Application app, string key) =>
        Assert.IsType<SolidColorBrush>(app.TryGetResource(key, app.ActualThemeVariant, out var value) ? value : null).Color;

    private static Color Solid(IBrush? brush) => Assert.IsAssignableFrom<ISolidColorBrush>(brush).Color;
}
