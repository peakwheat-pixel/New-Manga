using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-4 hover/pressed cells. The headless platform can synthesise pointer input, so these
/// cells are asserted through the REAL effective property change (`Background` follows the frozen hover /
/// pressed tokens), not through selector strings. This upgrades the previously NOT_RUN hover/pressed rows.
/// </summary>
public sealed class FluentComponentPointerStatesTests
{
    [AvaloniaFact]
    public void PrimaryButton_HoverAndPressed_ResolveTheFrozenAccentTokens()
    {
        using var manager = ThemeTestHarness.CreateInitialized();
        var app = Application.Current!;

        var primary = new Button { Content = "主操作", Classes = { "fluent-primary" }, Width = 160, Height = 40 };
        var secondary = new Button { Content = "次操作", Classes = { "fluent-secondary" }, Width = 160, Height = 40 };
        var window = new Window
        {
            Width = 480,
            Height = 320,
            Content = new StackPanel { Spacing = 12, Children = { primary, secondary } },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        // Primary: default accent → hover accent-hover → pressed returns accent-base (frozen design values).
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(primary.Background));
        MoveTo(window, primary);
        Dispatcher.UIThread.RunJobs();
        Assert.True(primary.IsPointerOver);
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Hover"), Solid(primary.Background));

        window.MouseDown(CenterOf(window, primary), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(primary.Background));
        window.MouseUp(CenterOf(window, primary), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Hover"), Solid(primary.Background));

        // Move away: hover clears and the default token returns.
        MoveAway(window);
        Dispatcher.UIThread.RunJobs();
        Assert.False(primary.IsPointerOver);
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Base"), Solid(primary.Background));

        // Secondary: hover overlay → pressed accent-muted (distinct from its raised default).
        Assert.Equal(TokenColor(app, "Nm.Color.Bg.Raised"), Solid(secondary.Background));
        MoveTo(window, secondary);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Bg.Overlay"), Solid(secondary.Background));
        window.MouseDown(CenterOf(window, secondary), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(secondary.Background));
        window.MouseUp(CenterOf(window, secondary), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Bg.Overlay"), Solid(secondary.Background));

        window.Close();
    }

    private static Point CenterOf(Window window, Control control) =>
        control.TranslatePoint(new Point(control.Bounds.Width / 2, control.Bounds.Height / 2), window)
        ?? throw new InvalidOperationException("control is not in the window visual tree");

    private static void MoveTo(Window window, Control control) =>
        window.MouseMove(CenterOf(window, control), RawInputModifiers.None);

    private static void MoveAway(Window window) =>
        window.MouseMove(new Point(window.Bounds.Width - 10, window.Bounds.Height - 10), RawInputModifiers.None);

    private static Color TokenColor(Application app, string key) =>
        Assert.IsType<SolidColorBrush>(app.TryGetResource(key, app.ActualThemeVariant, out var value) ? value : null).Color;

    private static Color Solid(IBrush? brush) => Assert.IsAssignableFrom<ISolidColorBrush>(brush).Color;
}
