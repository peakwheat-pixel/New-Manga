using System.ComponentModel;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Shell;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-B-1: the new shell window content. Owns exactly one <see cref="AppShellViewModel"/> (and thus
/// one Library ViewModel) for its whole lifetime; space/mode switches only toggle visibility. Keyboard
/// input funnels through <see cref="AppShellViewModel.HandleKey"/> (single KeyMap registry, IME-safe).
/// The appearance switch goes through the merged <see cref="DesignSystemThemeManager"/> (token
/// dictionaries swap, the window is never rebuilt).
/// </summary>
public partial class AppShellV2 : UserControl
{
    private readonly AppShellViewModel _viewModel;
    private readonly DesignSystemThemeManager? _themeManager;
    private TopLevel? _topLevel;
    private bool _initializationStarted;

    /// <summary>Designer / XAML-loader ctor (inert host; never starts a sidecar).</summary>
    public AppShellV2()
        : this(NullHostController.Instance)
    {
    }

    public AppShellV2(
        IHostController controller,
        IFilePickerGateway? picker = null,
        DesignSystemThemeManager? themeManager = null)
    {
        InitializeComponent();
        KeyMap.EnsureValid();
        _viewModel = new AppShellViewModel(
            controller,
            picker ?? new AvaloniaFilePickerGateway(_ => TopLevel.GetTopLevel(this)));
        DataContext = _viewModel;
        _viewModel.RegisterWorkspace(new LibraryWorkspaceView(_viewModel.Library));
        _viewModel.RegisterWorkspace(new ConsoleWorkspaceView(_viewModel.Console));

        _themeManager = themeManager;
        if (_themeManager is null && Application.Current is { } application)
        {
            _themeManager = new DesignSystemThemeManager(application);
        }

        // Unified construction path: Initialize() is idempotent and must also run for an injected manager.
        _themeManager?.Initialize();

        ApplyTheme();
        _viewModel.PropertyChanged += OnViewModelPropertyChanged;
        SizeChanged += (_, e) => _viewModel.SetViewport(e.NewSize.Width, e.NewSize.Height);
    }

    public AppShellViewModel ViewModel => _viewModel;

    /// <summary>Completes after the first Host read; headless tests await it before asserting data.</summary>
    public Task Initialization => _viewModel.Initialization;

    /// <summary>Test/automation seam: routes a key through the same funnel the window uses.</summary>
    public bool HandleKeyForTest(Key key, KeyModifiers modifiers, bool textInputFocused = false) =>
        _viewModel.HandleKey(key, modifiers, textInputFocused);

    protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
    {
        base.OnAttachedToVisualTree(e);
        _topLevel = TopLevel.GetTopLevel(this);
        if (_topLevel is not null)
        {
            _topLevel.AddHandler(KeyDownEvent, OnPreviewKeyDown, RoutingStrategies.Tunnel);
        }

        if (!_initializationStarted)
        {
            _initializationStarted = true;
            _ = InitializeWithDeepLinkAsync();
        }
    }

    /// <summary>
    /// Evidence / integration hook: <c>NEWMANGA_V2_DEEPLINK="?space=library&amp;book=...&amp;page=3"</c>
    /// lands the shell on an exact object after the first Host read (FUSION_SPEC §3 addressing rule).
    /// Parsing is pure (<see cref="ShellDeepLink"/>) and unit-tested; an invalid value is ignored.
    /// </summary>
    public static string DeepLinkEnvironmentVariable => "NEWMANGA_V2_DEEPLINK";

    public static ShellDeepLink? DeepLinkFromEnvironment()
    {
        var raw = Environment.GetEnvironmentVariable(DeepLinkEnvironmentVariable);
        return ShellDeepLink.TryParse(raw, out var link) ? link : null;
    }

    private async Task InitializeWithDeepLinkAsync()
    {
        await _viewModel.Initialization.ConfigureAwait(true);
        if (DeepLinkFromEnvironment() is { } link)
        {
            await _viewModel.ApplyDeepLinkAsync(link).ConfigureAwait(true);
        }
    }

    protected override void OnDetachedFromVisualTree(VisualTreeAttachmentEventArgs e)
    {
        if (_topLevel is not null)
        {
            _topLevel.RemoveHandler(KeyDownEvent, OnPreviewKeyDown);
            _topLevel = null;
        }

        base.OnDetachedFromVisualTree(e);
    }

    private void OnPreviewKeyDown(object? sender, KeyEventArgs e)
    {
        var focused = _topLevel?.FocusManager?.GetFocusedElement();
        var textInputFocused = focused is TextBox;
        _viewModel.HandleKey(e, textInputFocused);
    }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(AppShellViewModel.IsDarkTheme))
        {
            ApplyTheme();
        }
    }

    private void ApplyTheme() =>
        _themeManager?.SetAppearance(
            _viewModel.IsDarkTheme ? AppearanceMode.Dark : AppearanceMode.Light);
}
