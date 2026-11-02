using Avalonia;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;

[assembly: AvaloniaTestApplication(typeof(NewManga.App.Tests.TestAppBuilder))]

namespace NewManga.App.Tests;

public static class TestAppBuilder
{
    /// <summary>
    /// THEME-MACOS-1: headless + Skia so <c>CaptureRenderedFrame()</c> produces real pixels (used by
    /// ThemeMacosTests to prove the macOS Light/Dark screenshots are rendered, not placeholders).
    /// UseHeadlessDrawing=false disables the no-op headless drawing backend; Skia then draws into the
    /// headless framebuffer exactly like the probe in the workspace task-env.
    /// </summary>
    public static AppBuilder BuildAvaloniaApp() =>
        AppBuilder.Configure<App>()
            .UseSkia()
            .UseHeadless(new AvaloniaHeadlessPlatformOptions { UseHeadlessDrawing = false });
}
