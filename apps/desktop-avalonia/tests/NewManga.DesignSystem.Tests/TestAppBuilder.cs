using Avalonia;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;

[assembly: AvaloniaTestApplication(typeof(NewManga.DesignSystem.Tests.TestAppBuilder))]

namespace NewManga.DesignSystem.Tests;

/// <summary>
/// Headless application used by every design-system test. Skia drawing is enabled so tests can
/// capture real pixels (theme screenshots / accent rendering) instead of the no-op headless backend.
/// </summary>
public static class TestAppBuilder
{
    public static AppBuilder BuildAvaloniaApp() =>
        AppBuilder.Configure<DesignSystemTestApp>()
            .UseSkia()
            .UseHeadless(new AvaloniaHeadlessPlatformOptions { UseHeadlessDrawing = false });
}
