using System.ComponentModel;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml.MarkupExtensions;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.Shell;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.DesignSystem;
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
        StudioWorkspace = new StudioWorkspaceAdapter(
            new StudioWorkspaceView(new StudioWorkspaceViewModel(
                controller,
                new StudioSelection(_viewModel.State))));
        _viewModel.RegisterWorkspace(StudioWorkspace);

        _themeManager = themeManager;
        if (_themeManager is null && Application.Current is { } application)
        {
            _themeManager = new DesignSystemThemeManager(application);
        }

        // Unified construction path: Initialize() is idempotent and must also run for an injected manager.
        _themeManager?.Initialize();

        // V11R-INT-2: adopt the appearance the DS manager already applied (--variant / persisted
        // choice) instead of forcing the ViewModel default back over it. Only the user toggle and
        // explicit SetAppearance calls change it afterwards.
        if (_themeManager is not null)
        {
            _viewModel.AdoptAppearance(_themeManager.Appearance == AppearanceMode.Dark);
        }

        _viewModel.PropertyChanged += OnViewModelPropertyChanged;
        SizeChanged += (_, e) => _viewModel.SetViewport(e.NewSize.Width, e.NewSize.Height);
    }

    public AppShellViewModel ViewModel => _viewModel;

    /// <summary>INT-0: the Studio workspace adapter registered by the built-in shell.</summary>
    public StudioWorkspaceAdapter StudioWorkspace { get; }

    /// <summary>Completes after the first Host read; headless tests await it before asserting data.</summary>
    public Task Initialization => _viewModel.Initialization;

    /// <summary>INT-1 integration seam: register an extra top-level workspace (e.g. settings).</summary>
    public bool RegisterWorkspace(IWorkspaceView workspace) => _viewModel.RegisterWorkspace(workspace);

    /// <summary>INT-1/C-2 integration seam: register the Theme Studio surface implementation.</summary>
    public bool RegisterSurfaceWorkspace(ISurfaceWorkspace workspace) =>
        _viewModel.RegisterSurfaceWorkspace(workspace);

    /// <summary>
    /// V11R-INT-0: the shell's standalone window factory. MainWindow is not involved; INT-1 is expected to
    /// switch the default entry point to this factory. Options only supply window geometry (AppOptions is
    /// parse-only, so a caller can pass <see cref="AppOptions.Parse"/> of its real arguments).
    /// </summary>
    public static Window CreateRoot(
        IHostController controller,
        AppOptions? options = null,
        IFilePickerGateway? picker = null,
        DesignSystemThemeManager? themeManager = null)
    {
        var shell = new AppShellV2(controller, picker, themeManager);
        var window = new Window
        {
            Title = "New Manga",
            Width = options?.WindowWidth ?? 1100,
            Height = options?.WindowHeight ?? 760,
            MinWidth = ShellLayout.BreakpointNarrow,
            Content = shell,
        };
        window[!Window.BackgroundProperty] = new DynamicResourceExtension(NmKeys.Color.Bg.App);
        // C-3-I1: the v2 shell applies the same window-material policy as the legacy shell (Mica on
        // Win11, opaque fallback elsewhere) so the R4 material assertion is not legacy-only.
        var material = WindowMaterial.ForCurrentOs();
        window.TransparencyLevelHint = material.Hints
            .Select(hint => hint switch
            {
                "Mica" => WindowTransparencyLevel.Mica,
                "Blur" => WindowTransparencyLevel.Blur,
                _ => WindowTransparencyLevel.None,
            })
            .ToArray();
        return window;
    }

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
