using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Markup.Xaml.MarkupExtensions;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Shell.V2;
using NewManga.Appearance;
using NewManga.DesignSystem;
using NewManga.Presentation.Avalonia.Hosting;
using NewManga.Presentation.Avalonia.Lifecycle;
using NewManga.Presentation.Avalonia.Windows;
using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.App.Views.Presentation;

/// <summary>
/// FEA-07 slice 2b: the stable native main window. It owns one visible <see cref="FrontendContentHost"/>
/// plus one hidden staging slot and keeps its own native identity (title/geometry/material) while the
/// content tree is switched between frontends. The content factory is supplied by the composition root
/// so this window has no direct dependency on either shell implementation (§7.3 / H2).
/// </summary>
public sealed class PresentationWindow : Window
{
    private readonly FrontendHostCoordinator _coordinator;
    private readonly Func<IReadOnlyList<Control>>? _allContentProvider;

    /// <summary>Creates the stable window and hosts the initial frontend content tree.</summary>
    /// <param name="allContentProvider">
    /// FEA-07 R-002: every cached content tree the composition root keeps for state preservation (the
    /// window closes only after all of them report no unsaved edits / active runs, not just the visible tree).
    /// </param>
    public PresentationWindow(
        AppOptions options,
        FrontendSelection selection,
        IHostController? hostController,
        AppearanceCoordinator appearance,
        SwitchJournal journal,
        Func<string, Control> contentFactory,
        WindowStateMemento? initialMemento = null,
        Func<IReadOnlyList<Control>>? allContentProvider = null)
    {
        ArgumentNullException.ThrowIfNull(options);
        ArgumentNullException.ThrowIfNull(selection);
        ArgumentNullException.ThrowIfNull(appearance);
        ArgumentNullException.ThrowIfNull(journal);
        ArgumentNullException.ThrowIfNull(contentFactory);

        _ = hostController; // content factory owns the Host wiring; the window never starts/disposes it
        _allContentProvider = allContentProvider;
        Title = "New Manga";
        Width = initialMemento?.Width ?? options.WindowWidth;
        Height = initialMemento?.Height ?? options.WindowHeight;
        MinWidth = ShellLayout.BreakpointNarrow;
        if (initialMemento is { } state)
        {
            Position = new PixelPoint(state.X, state.Y);
            if (state.IsMaximized)
            {
                WindowState = WindowState.Maximized;
            }
        }

        ContentHost = new FrontendContentHost();
        ContentHost.SetContent(contentFactory(selection.EffectiveFrontendId));

        // R-001: the hidden staging slot is attached to the same live visual tree as the visible slot but
        // is composited at zero opacity and never hit-testable. A replacement tree is mounted here first,
        // so the commit gate observes real layout/Loaded/frame-render signals while the previous tree
        // stays interactive (no manual Measure/Arrange, no synthetic viewport, §7.1/§15.5).
        StagingHost = new FrontendContentHost
        {
            Opacity = 0,
            IsHitTestVisible = false,
            Focusable = false,
        };
        AutomationProperties.SetAccessibilityView(StagingHost, AccessibilityView.Raw);

        var root = new Grid();
        root.Children.Add(StagingHost);
        root.Children.Add(ContentHost);
        Content = root;

        this[!BackgroundProperty] = new DynamicResourceExtension(NmKeys.Color.Bg.App);
        ApplyWindowMaterial();

        _coordinator = new FrontendHostCoordinator(
            ContentHost,
            StagingHost,
            selection.EffectiveFrontendId,
            contentFactory,
            appearance,
            journal);

        Broker = new WindowBroker();
        Broker.RegisterMain("presentation-main");
        Closing += OnClosing;
    }

    /// <summary>FEA-07 window broker: the stable main window is registered once; secondary windows are tracked.</summary>
    public WindowBroker Broker { get; }

    /// <summary>
    /// FEA-07 exit coordination (proposal §7.3): closing the stable window asks the process-level
    /// coordinator first; pending edits or active runs block the close instead of disposing the Host.
    /// </summary>
    public ExitCoordinator ExitCoordinator { get; } = new();

    /// <summary>The content slot the switch transaction replaces (exposed for headless verification).</summary>
    public FrontendContentHost ContentHost { get; }

    /// <summary>The hidden pre-commit slot: real attach/layout/Loaded/render signals come from here (R-001).</summary>
    public FrontendContentHost StagingHost { get; }

    /// <summary>The frontend id currently hosted by this stable window.</summary>
    public string CurrentFrontendId => _coordinator.CurrentFrontendId;

    /// <summary>Captures the current placement for the per-window memento (FEA-07 AC5).</summary>
    public WindowStateMemento CaptureWindowState(string? displayId = null) => new(
        Position.X,
        Position.Y,
        (int)Width,
        (int)Height,
        DisplayId: displayId,
        Scale: RenderScaling,
        IsMaximized: WindowState == WindowState.Maximized);

    private void OnClosing(object? sender, WindowClosingEventArgs args)
    {
        // R-002: aggregate the live content trees the composition root caches per frontend (the visible
        // one plus hidden staging/cached trees) before consulting the process-level coordinator; leaving a
        // dirty Fluent settings draft or a running workbench/import in a hidden tree must block the close.
        var contentBlocked = false;
        foreach (var content in EnumerateLiveContentTrees())
        {
            if (content is IPresentationExitState state && (state.HasUnsavedEdits || state.HasActiveRuns))
            {
                contentBlocked = true;
                break;
            }
        }

        var decision = ExitCoordinator.RequestExit();
        if (contentBlocked || !decision.Allowed)
        {
            args.Cancel = true;
        }
    }

    private IEnumerable<Control> EnumerateLiveContentTrees()
    {
        if (ContentHost.Current is { } visible)
        {
            yield return visible;
        }

        if (StagingHost.Current is { } staged)
        {
            yield return staged;
        }

        if (_allContentProvider?.Invoke() is not { } cached)
        {
            yield break;
        }

        foreach (var content in cached)
        {
            if (content is not null)
            {
                yield return content;
            }
        }
    }

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
