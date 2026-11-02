using Avalonia;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Tests;

/// <summary>
/// R-19 test isolation: the DesignSystem theme manager mutates global <see cref="Application"/> resources,
/// so headless tests that switch appearance must not leak that state into later tests. Every window-based
/// test starts from the DS defaults.
/// </summary>
public static class TestTheme
{
    public static void ResetToDefaults()
    {
        if (Application.Current is not { } application)
        {
            return;
        }

        using var manager = new DesignSystemThemeManager(application);
        manager.Initialize();
        manager.ResetToDefaults();
    }
}
