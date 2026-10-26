using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using NewManga.App.Services;
using NewManga.App.Views;
using NewManga.Theme;

namespace NewManga.App.Tests;

public sealed class MainWindowTests
{
    [AvaloniaFact]
    public void ReadySnapshot_RendersStatusBooksAndWireStats()
    {
        var controller = new FakeHostController(
            FakeHostController.ReadySnapshot("雾港来信 · 第 1 卷", "星屑のセイバー"));
        var window = new MainWindow(controller, new AppOptions());

        var status = window.FindControl<TextBlock>("StatusText");
        Assert.NotNull(status);
        Assert.Contains("就绪", status!.Text!, StringComparison.Ordinal);

        var books = window.FindControl<ListBox>("BooksList");
        Assert.NotNull(books);
        Assert.NotNull(books!.ItemsSource);
        Assert.Equal(2, books.ItemsSource!.Cast<object>().Count());

        var wire = window.FindControl<TextBlock>("WireText");
        Assert.NotNull(wire);
        Assert.Contains("ASCII-only=True", wire!.Text!, StringComparison.Ordinal);

        var errorCode = window.FindControl<TextBlock>("ErrorCodeText");
        Assert.Equal("无错误", errorCode!.Text);
    }

    [AvaloniaFact]
    public void FailureSnapshot_ShowsTypedCode_NotAnException()
    {
        var controller = new FakeHostController(FakeHostController.FailureSnapshot());
        var window = new MainWindow(controller, new AppOptions());

        var errorCode = window.FindControl<TextBlock>("ErrorCodeText");
        Assert.NotNull(errorCode);
        Assert.Contains("SIDECAR_EXE_MISSING", errorCode!.Text!, StringComparison.Ordinal);

        var errorMessage = window.FindControl<TextBlock>("ErrorMessageText");
        Assert.Contains("核心服务", errorMessage!.Text!, StringComparison.Ordinal);
    }

    [AvaloniaFact]
    public void ChineseRoundTripButton_UsesAc3Vector()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var window = new MainWindow(controller, new AppOptions());
        var roundTrip = window.FindControl<Button>("RoundTripButton");
        Assert.NotNull(roundTrip);

        window.Controller.TryChineseRoundTripAsync(MainWindow.ChineseVector).GetAwaiter().GetResult();

        Assert.Equal("\u96fe\u6e2f\u6765\u4fe1\u30fb\u65e5\u672c\u8a9e\u30c6\u30b9\u30c8", controller.LastRoundTripTitle);
    }

    [AvaloniaFact]
    public void ThemeSwitch_ReplacesPaletteWithoutRestart()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var window = new MainWindow(controller, new AppOptions());
        var application = Application.Current!;

        ThemeManager.Apply(application, ThemeManager.Dark);
        Assert.True(application.TryGetResource(ThemeManager.AppBackground, application.ActualThemeVariant, out var darkValue));
        Assert.Equal(Color.Parse("#12161C"), ((SolidColorBrush)darkValue!).Color);

        ThemeManager.Apply(application, ThemeManager.SaberPurple);
        Assert.True(application.TryGetResource(ThemeManager.AppBackground, application.ActualThemeVariant, out var saberValue));
        Assert.Equal(Color.Parse("#1A0F26"), ((SolidColorBrush)saberValue!).Color);

        Assert.NotNull(window);
    }
}
