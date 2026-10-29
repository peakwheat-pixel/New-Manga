using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.ViewModels.V2.ThemeStudio;
using NewManga.App.Views.V2.ThemeStudio.Preview;

namespace NewManga.App.Views.V2.ThemeStudio;

/// <summary>
/// The Theme Studio surface (THEME_STUDIO_SPEC §2/§5). Code-behind only wires the things XAML cannot:
/// keyboard routing (Esc ladder / Ctrl+F / Ctrl+Enter / arrow section navigation), focus entry into the
/// modal dialog, and the focus-search request. All state lives in <see cref="ThemeStudioViewModel"/>.
/// </summary>
public partial class ThemeStudioView : UserControl
{
    private ThemeStudioViewModel? _viewModel;

    public ThemeStudioView()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => AttachViewModel();
        AddHandler(KeyDownEvent, OnTunnelKeyDown, RoutingStrategies.Tunnel, handledEventsToo: true);
        AddHandler(KeyDownEvent, OnKeyDown, RoutingStrategies.Bubble);
    }

    /// <summary>Raised when the surface should be popped by the shell (Esc / 返回 / 应用后退出).</summary>
    public event EventHandler? CloseRequested;

    /// <summary>The surface view model (null until an integration layer assigns one).</summary>
    public ThemeStudioViewModel? ViewModel => _viewModel;

    /// <summary>
    /// Optional production-surface provider for the three preview views (V11R-INT-1 seam). When unset the
    /// studio renders its own real control trees with example content.
    /// </summary>
    public IPreviewSurfaceProvider? PreviewSurfaceProvider { get; set; }

    /// <summary>Creates the view over a view model (integration entry point).</summary>
    public ThemeStudioView(ThemeStudioViewModel viewModel)
        : this()
    {
        DataContext = viewModel;
        AttachViewModel();
    }

    /// <summary>Opens the surface on a section and focuses the rail.</summary>
    public async Task OpenAsync(ThemeStudioSection section = ThemeStudioSection.Library)
    {
        if (_viewModel is null)
        {
            return;
        }

        await _viewModel.OpenAsync(section).ConfigureAwait(true);
        Focus();
        NavRail.Focus();
    }

    /// <summary>Requests a close through the normal Esc ladder (dirty drafts go through the dialog).</summary>
    public void Close() => _viewModel?.Close();

    private void AttachViewModel()
    {
        if (_viewModel is not null)
        {
            _viewModel.PropertyChanged -= OnViewModelPropertyChanged;
            _viewModel.RequestClose -= OnRequestClose;
            _viewModel.FocusSearchRequested -= OnFocusSearchRequested;
        }

        _viewModel = DataContext as ThemeStudioViewModel;
        if (_viewModel is null)
        {
            return;
        }

        _viewModel.PropertyChanged += OnViewModelPropertyChanged;
        _viewModel.RequestClose += OnRequestClose;
        _viewModel.FocusSearchRequested += OnFocusSearchRequested;
        PreviewSection.ApplySurfaceProvider(PreviewSurfaceProvider);
    }

    private void OnRequestClose(object? sender, EventArgs e) => CloseRequested?.Invoke(this, EventArgs.Empty);

    private void OnFocusSearchRequested(object? sender, EventArgs e) =>
        Dispatcher.UIThread.Post(() => LibrarySection.FocusSearch(), DispatcherPriority.Input);

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName != nameof(ThemeStudioViewModel.Dialog))
        {
            return;
        }

        if (_viewModel?.Dialog.IsOpen != true)
        {
            Focus();
            return;
        }

        // Modal focus trap: enter the dialog, default focus lands on its first action (取消 is first).
        Dispatcher.UIThread.Post(
            () =>
            {
                DialogCard.UpdateLayout();
                var first = DialogCard.GetVisualDescendants().OfType<Button>().FirstOrDefault();
                first?.Focus();
            },
            DispatcherPriority.Input);
    }

    private void OnTunnelKeyDown(object? sender, KeyEventArgs e)
    {
        if (_viewModel is null || e.Key != Key.Escape || e.Handled)
        {
            return;
        }

        // Esc must work even while a TextBox owns focus, so it is handled in the tunnel phase.
        e.Handled = _viewModel.HandleEscape();
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        if (_viewModel is null || e.Handled)
        {
            return;
        }

        var modifiers = e.KeyModifiers;
        if (modifiers == KeyModifiers.Control && e.Key == Key.F)
        {
            _viewModel.FocusSearch();
            e.Handled = true;
            return;
        }

        if (modifiers == KeyModifiers.Control && e.Key == Key.Enter)
        {
            _ = _viewModel.ApplyDraftAsync();
            e.Handled = true;
            return;
        }

        if (e.KeyModifiers != KeyModifiers.None)
        {
            return;
        }

        switch (e.Key)
        {
            case Key.Down:
            case Key.Right:
                _viewModel.SelectNextSection(1);
                e.Handled = true;
                break;
            case Key.Up:
            case Key.Left:
                _viewModel.SelectNextSection(-1);
                e.Handled = true;
                break;
        }
    }
}
