using Avalonia.Controls;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.App.Views.V2.ThemeStudio;

namespace NewManga.App.Shell.V2.ThemeStudio;

/// <summary>
/// Overlay surface host for the Theme Studio (contract §6.2, THEME_STUDIO_SPEC §2). The shell pushes
/// <c>ShellSurface.ThemeStudio</c>, mounts this control and calls <see cref="OpenAsync"/>; it listens to
/// <see cref="RequestClose"/> to pop the surface. Keyboard focus/Esc ladders live in
/// <see cref="ThemeStudioView"/> so the shell key map stays the single global registry.
/// </summary>
public partial class ThemeStudioSurface : UserControl
{
    /// <summary>Creates an unbound surface (integration assigns the view model).</summary>
    public ThemeStudioSurface() => InitializeComponent();

    /// <summary>Creates the surface over a Theme Studio view model.</summary>
    public ThemeStudioSurface(ThemeStudioViewModel viewModel)
        : this()
    {
        DataContext = viewModel;
        Studio.CloseRequested += OnViewCloseRequested;
    }

    /// <summary>Raised when the surface wants to be popped by the shell.</summary>
    public event EventHandler? RequestClose;

    /// <summary>The hosted view (exposed for integration tests / focus probes).</summary>
    public ThemeStudioView StudioView => Studio;

    /// <summary>Loads the catalogue and opens the requested section.</summary>
    public Task OpenAsync(ThemeStudioSection section = ThemeStudioSection.Library) =>
        Studio.OpenAsync(section);

    /// <summary>Requests a close through the Esc ladder (dirty drafts go through the three-exit dialog).</summary>
    public void Close() => Studio.Close();

    private void OnViewCloseRequested(object? sender, EventArgs e) => RequestClose?.Invoke(this, EventArgs.Empty);
}
