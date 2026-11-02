using Avalonia.Controls;
using NewManga.App.ViewModels.V2.ThemeStudio;

namespace NewManga.App.Views.V2.ThemeStudio.Preview;

/// <summary>
/// Seam for V11R-INT-1 (approved by the Lead): lets the integration layer swap the built-in preview
/// control trees for the production space views once they can be hosted without their workspace
/// ViewModels (they currently require <c>IHostController</c> + shell state).
///
/// <para>
/// The default implementation is the studio's own real control trees
/// (<see cref="ShelfPreviewView"/> / <see cref="WorkbenchPreviewView"/> / <see cref="ReaderPreviewView"/>),
/// which already render the candidate theme through the scoped palette. A provider returning null for a
/// mode keeps that default.
/// </para>
/// </summary>
public interface IPreviewSurfaceProvider
{
    /// <summary>Creates the control tree for one preview mode, or null to keep the studio's default.</summary>
    Control? CreateSurface(ThemeStudioPreviewMode mode);
}
