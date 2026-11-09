using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.Views.V2.Library;

namespace NewManga.App.Shell.V2;

/// <summary>
/// FEA-07-V2-F11-1: borderless fullscreen reader host for the default V2 shell. The shell view model
/// only raises <c>ImmersiveReaderRequested</c>; the composition root creates this window (mirroring the
/// legacy <c>ReaderWindow</c> behaviour: no decorations, black background, Esc/F11 closes and the shell
/// page the user came from stays untouched).
/// </summary>
public sealed class ImmersiveReaderWindow : Window
{
    public ImmersiveReaderWindow(ReaderOverlayViewModel reader)
    {
        ArgumentNullException.ThrowIfNull(reader);
        Title = "阅读器";
        SystemDecorations = SystemDecorations.None;
        WindowState = WindowState.FullScreen;
        Background = Brushes.Black;
        Content = new ReaderOverlay { DataContext = reader };
        KeyDown += (_, e) =>
        {
            if (TryHandleKey(e.Key))
            {
                e.Handled = true;
            }
        };
    }

    /// <summary>Esc presses that closed the immersive session (headless-testable).</summary>
    public int EscapeCount { get; private set; }

    /// <summary>F11 presses that closed the immersive session (toggle-off half, like legacy).</summary>
    public int F11Count { get; private set; }

    /// <summary>Handles one keystroke; returns true when the key was consumed.</summary>
    public bool TryHandleKey(Key key)
    {
        switch (key)
        {
            case Key.Escape:
                EscapeCount++;
                Close();
                return true;
            case Key.F11:
                F11Count++;
                Close();
                return true;
            default:
                return false;
        }
    }
}
