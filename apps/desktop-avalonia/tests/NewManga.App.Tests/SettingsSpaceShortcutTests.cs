using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2;
using NewManga.App.ViewModels.V2.Shell;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// GATE3-SETTINGS-SHORTCUT-1: the last ⚠️ cell of the condition-3 matrix (settings page / shortcuts).
///
/// Why this exists: the shell routes keys as "workspace first refusal, then the shell KeyMap"
/// (AppShellViewModel.HandleKey). A workspace adapter that returned true for every key would swallow
/// global shortcuts while the user is on that space. The Console space (where Settings lives) returns
/// false from TryHandleKey, so global shortcuts are expected to keep working there -- but nothing
/// asserted it until now; the matrix only had "settings is not a Space entry", which is a different
/// claim.
///
/// This test pins the user-visible behaviour: from the Console/settings space, Ctrl+K must still open
/// the command palette, and Ctrl+D2 must still switch back to the workbench.
/// </summary>
public sealed class SettingsSpaceShortcutTests
{
    private static (Window Window, AppShellV2 Shell) Create()
    {
        TestTheme.ResetToDefaults();
        var shell = new AppShellV2(V2Fixture.Create());
        var window = new Window
        {
            Width = 1600,
            Height = 1000,
            Content = shell,
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        return (window, shell);
    }

    [AvaloniaFact]
    public async Task ConsoleSpace_DoesNotSwallowGlobalShortcuts()
    {
        var (window, shell) = Create();
        try
        {
            await shell.Initialization;
            Dispatcher.UIThread.RunJobs();

            // 1. Enter the Console space (that is where Settings lives).
            Assert.True(
                shell.HandleKeyForTest(Key.D3, KeyModifiers.Control),
                "Ctrl+D3 was not handled; cannot establish the Console space");
            Dispatcher.UIThread.RunJobs();
            Assert.Equal(SpaceId.Console, shell.ViewModel.State.CurrentSpace);

            // 2. A global shortcut must still be honoured FROM the settings space.
            Assert.True(
                shell.HandleKeyForTest(Key.K, KeyModifiers.Control),
                "Ctrl+K was swallowed while the Console/settings space was active");
            Assert.True(shell.ViewModel.IsPaletteOpen, "Ctrl+K did not open the command palette from Settings");

            // 3. Close it again so the next assertion is not short-circuited by the overlay.
            Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
            Dispatcher.UIThread.RunJobs();
            Assert.False(shell.ViewModel.IsPaletteOpen);

            // 4. Leaving the space must also still work.
            Assert.True(
                shell.HandleKeyForTest(Key.D2, KeyModifiers.Control),
                "Ctrl+D2 was swallowed while the Console/settings space was active");
            Dispatcher.UIThread.RunJobs();
            Assert.Equal(SpaceId.Studio, shell.ViewModel.State.CurrentSpace);
        }
        finally
        {
            window.Close();
        }
    }
}
