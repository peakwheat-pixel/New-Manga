using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.ViewModels.V2.Shell;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07-V2-F11-1: the default V2 shell gains a keyboard-only immersive entry — bare F11 opens a
/// borderless fullscreen reader window, Esc/F11 closes it, and the shell page is left untouched.
/// </summary>
public sealed class V2ImmersiveReaderTests
{
    private static FakeHostController Controller() =>
        new(FakeHostController.ReadySnapshot("BITMAP-BOOK"));

    [AvaloniaFact]
    public void ImmersiveWindow_IsBorderlessFullscreen_AndClosesOnEscOrF11()
    {
        var reader = new ReaderOverlayViewModel(Controller(), (_, _) => { });
        var window = new ImmersiveReaderWindow(reader);

        Assert.Equal("阅读器", window.Title);
        Assert.Equal(SystemDecorations.None, window.SystemDecorations);
        Assert.Equal(WindowState.FullScreen, window.WindowState);

        Assert.True(window.TryHandleKey(Key.Escape));
        Assert.Equal(1, window.EscapeCount);
        Assert.False(window.IsVisible);

        var second = new ImmersiveReaderWindow(reader);
        Assert.True(second.TryHandleKey(Key.F11));
        Assert.Equal(1, second.F11Count);
    }

    [AvaloniaFact]
    public void V2Shell_BareF11_RaisesImmersiveRequest_AndIgnoresModifiersOrTextFocus()
    {
        var shell = new AppShellViewModel(Controller(), picker: null);
        var raised = 0;
        shell.ImmersiveReaderRequested += (_, _) => raised++;

        Assert.True(shell.HandleKey(Key.F11, KeyModifiers.None, isTextInputFocused: false));
        Assert.Equal(1, raised);

        Assert.False(shell.HandleKey(Key.F11, KeyModifiers.Control, isTextInputFocused: false));
        Assert.False(shell.HandleKey(Key.F11, KeyModifiers.None, isTextInputFocused: true));
        Assert.False(shell.HandleKey(Key.F11, KeyModifiers.Alt, isTextInputFocused: false));
        Assert.Equal(1, raised);
    }

    [AvaloniaFact]
    public void KeyMap_DeclaresTheF11ImmersiveGesture()
    {
        var command = KeyMap.Default.Definitions.Single(d => d.Id == ShellCommandIds.LibraryImmersiveReader);
        Assert.Contains(command.Gestures, g => g.Matches(Key.F11, KeyModifiers.None));
        Assert.Empty(KeyMap.Default.Conflicts);
    }
}
