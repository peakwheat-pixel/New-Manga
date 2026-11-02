using Avalonia.Controls;

namespace NewManga.Presentation.Avalonia.Hosting;

/// <summary>
/// FEA-07 stable-window content slot: the native main window keeps its identity while the frontend
/// content tree is replaced. Only the hosting app decides which control is shown; the host itself has
/// no knowledge of Frontends (§7.1 / §15.5).
/// </summary>
public sealed class FrontendContentHost : UserControl
{
    private readonly ContentControl _slot = new();

    public FrontendContentHost()
    {
        Content = _slot;
    }

    /// <summary>The currently displayed frontend content tree.</summary>
    public Control? Current => _slot.Content as Control;

    /// <summary>Replaces the live content tree; the previous tree is detached. Callers must swap only on the UI thread.</summary>
    public void SetContent(Control content)
    {
        ArgumentNullException.ThrowIfNull(content);
        _slot.Content = content;
    }

    /// <summary>Detaches the current content tree without displaying a replacement.</summary>
    public void Clear()
    {
        _slot.Content = null;
    }
}
