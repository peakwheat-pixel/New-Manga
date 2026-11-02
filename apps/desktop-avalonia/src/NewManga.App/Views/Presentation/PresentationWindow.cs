using System;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml.MarkupExtensions;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Shell.V2;
using NewManga.Appearance;
using NewManga.DesignSystem;
using NewManga.Presentation.Avalonia.Hosting;
using NewManga.Presentation.Avalonia.Windows;
using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.App.Views.Presentation;

/// <summary>
/// FEA-07 slice 2b: the stable native main window. It owns one <see cref="FrontendContentHost"/> and
/// keeps its own native identity (title/geometry/material) while the content tree is switched between
/// frontends. The content factory is supplied by the composition root so this window has no direct
/// dependency on either shell implementation (§7.3 / H2).
/// </summary>
public sealed class PresentationWindow : Window
{
    private readonly FrontendHostCoordinator _coordinator;

    /// <summary>Creates the stable window and hosts the initial frontend content tree.</summary>
    public PresentationWindow(
        AppOptions options,
        FrontendSelection selection,
        IHostController? hostController,
        AppearanceCoordinator appearance,
        SwitchJournal journal,
        Func<string, Control> contentFactory,
        WindowStateMemento? initialMemento = null)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(selection);
        ArgumentNullException.ThrowIfNull(appearance);
        ArgumentNullException.ThrowIfNull(journal);
        ArgumentNullException.ThrowIfNull(contentFactory);

        _ = hostController; // content factory owns the Host wiring; the window never starts/disposes it
        Title = "New Manga";
        Width = initialMemento?.Width ?? options.WindowWidth;
        Height = initialMemento?.Height ?? options.WindowHeight;
        MinWidth = ShellLayout.BreakpointNarrow;
        if (initialMemento is { } state)
        {
            Position = new PixelPoint(state.X, state.Y);
        }

        ContentHost = new FrontendContentHost();
        ContentHost.SetContent(contentFactory(selection.EffectiveFrontendId));
        Content = ContentHost;
        this[!BackgroundProperty] = new DynamicResourceExtension(NmKeys.Color.Bg.App);
        ApplyWindowMaterial();

        _coordinator = new FrontendHostCoordinator(
            ContentHost,
            selection.EffectiveFrontendId,
            contentFactory,
            appearance,
            journal);

        Broker = new WindowBroker();
        Broker.RegisterMain("presentation-main");
    }

    /// <summary>FEA-07 window broker: the stable main window is registered once; secondary windows are tracked.</summary>
    public WindowBroker Broker { get; }

    /// <summary>The content slot the switch transaction replaces (exposed for headless verification).</summary>
    public FrontendContentHost ContentHost { get; }

    /// <summary>The frontend id currently hosted by this stable window.</summary>
    public string CurrentFrontendId => _coordinator.CurrentFrontendId;

    /// <summary>Captures the current placement for the per-window memento (FEA-07 AC5).</summary>
    public WindowStateMemento CaptureWindowState() => new(
        Position.X,
        Position.Y,
        (int)Width,
        (int)Height,
        DisplayId: null,
        Scale: RenderScaling,
        IsMaximized: WindowState == WindowState.Maximized);

    /// <summary>Switches the hosted content tree; the window identity is preserved and failures roll back.</summary>
    public Task<SwitchResult> SwitchFrontendAsync(string frontendId, CancellationToken cancellationToken = default) =>
        _coordinator.SwitchAsync(frontendId, cancellationToken);

    private void ApplyWindowMaterial()
    {
        var material = WindowMaterial.ForCurrentOs();
        TransparencyLevelHint = material.Hints switch
        {
            var hints when hints.Contains("Mica") => new[] { WindowTransparencyLevel.Mica },
            var hints when hints.Contains("Blur") => new[] { WindowTransparencyLevel.Blur },
            _ => new[] { WindowTransparencyLevel.None },
        };
    }
}
