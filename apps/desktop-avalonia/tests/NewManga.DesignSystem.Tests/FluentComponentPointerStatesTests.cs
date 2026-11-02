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
        var danger = new Button { Content = "危险", Classes = { "fluent-danger" }, Width = 160, Height = 40 };
        var card = new Button { Content = "作品", Classes = { "fluent-book-card" }, Width = 160, Height = 48 };
        var bookRow = new Button { Content = "作品行", Classes = { "fluent-book-row" }, Width = 160, Height = 36 };
        var window = new Window
        {
            Width = 480,
            Height = 580,
            Content = new StackPanel { Spacing = 12, Children = { primary, secondary, danger, card, bookRow } },
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

        // DangerButton: hover uses the muted failed status surface (outline stays failed).
        MoveTo(window, danger);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.StatusMuted.Failed"), Solid(danger.Background));

        // BookRow: canvas → overlay (hover) → accent-muted (pressed/selected).
        Assert.Equal(TokenColor(app, "Nm.Color.Bg.Canvas"), Solid(bookRow.Background));
        MoveTo(window, bookRow);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Bg.Overlay"), Solid(bookRow.Background));
        window.MouseDown(CenterOf(window, bookRow), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(bookRow.Background));
        window.MouseUp(CenterOf(window, bookRow), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        bookRow.Classes.Add("selected");
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(bookRow.Background));

        // BookCard: raised → overlay (hover) → accent-muted (pressed) → selected keeps accent-muted surface.
        MoveTo(window, card);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Bg.Overlay"), Solid(card.Background));
        window.MouseDown(CenterOf(window, card), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(card.Background));
        window.MouseUp(CenterOf(window, card), MouseButton.Left, RawInputModifiers.None);
        Dispatcher.UIThread.RunJobs();
        card.Classes.Add("selected");
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(TokenColor(app, "Nm.Color.Accent.Muted"), Solid(card.Background));

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
