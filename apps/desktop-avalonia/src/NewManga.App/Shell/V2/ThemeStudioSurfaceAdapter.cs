using System.Diagnostics;
using Avalonia.Controls;
using Avalonia.Threading;
using NewManga.App.Shell.V2.ThemeStudio;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.App.Views.V2.ThemeStudio;

namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-INT-1: binds the Theme Studio overlay (V11R-C-2) into the shell's surface stack.
/// The shell only knows <see cref="ISurfaceWorkspace"/>; this adapter owns the production
/// <see cref="ThemeStudioViewModel"/> (real <c>IThemeService</c> from the theme engine) and
/// forwards the surface lifecycle without touching <c>AppShellV2</c> internals.
/// </summary>
public sealed class ThemeStudioSurfaceAdapter : ISurfaceWorkspace
{
    private readonly ThemeStudioViewModel _viewModel;
    private readonly Action? _requestClose;
    private ThemeStudioSurface? _surface;

    public ThemeStudioSurfaceAdapter(ThemeStudioViewModel viewModel, Action? requestClose = null)
    {
        _viewModel = viewModel ?? throw new ArgumentNullException(nameof(viewModel));
        _requestClose = requestClose;
    }

    public ShellSurface Surface => ShellSurface.ThemeStudio;

    public string DisplayName => "主题中心";

    public ThemeStudioViewModel ViewModel => _viewModel;

    public Control CreateContent()
    {
        if (_surface is null)
        {
            _surface = new ThemeStudioSurface(_viewModel);
            _surface.RequestClose += (_, _) => _requestClose?.Invoke();
        }

        return _surface;
    }

    public void OnActivated(ShellState state)
    {
        if (_surface is null)
        {
            return;
        }

        // The section catalogue loads asynchronously; failures surface inside the studio's own
        // error banner instead of crashing the shell.
        Dispatcher.UIThread.Post(async () =>
        {
            try
            {
                await _surface.OpenAsync();
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException or TimeoutException)
            {
                Trace.TraceWarning($"Theme Studio open failed: {ex.GetType().Name}");
            }
        });
    }

    public void OnDeactivated(ShellState state) => _surface?.Close();
}
