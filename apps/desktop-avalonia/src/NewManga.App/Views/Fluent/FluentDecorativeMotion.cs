using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Controls.Shapes;
using Avalonia.Markup.Xaml.MarkupExtensions;
using Avalonia.VisualTree;
using NewManga.App.Controls;

namespace NewManga.App.Views.Fluent;

/// <summary>
/// FEA-06-RESIDUAL-2 IN-1.1: an endless decorative loop driven purely by render frames — no dispatcher
/// timers and no background work. A deactivated or hidden window pauses the loop (02-motion §4) while
/// keeping its phase, so reactivation continues instead of jumping; detaching the target stops every
/// frame request (no leaked callbacks). A period of 0 keeps the decorative visual static and creates
/// no running animation at all (design §3 判据①).
/// </summary>
internal sealed class FluentDecorativeLoop
{
    private readonly Control _target;
    private IFluentMotionClock? _clock;
    private Action<double>? _update;
    private double _periodMs;
    private int _generation;
    private bool _running;
    private TimeSpan _anchor;
    private double _phaseAtPause;
    private Window? _window;

    public FluentDecorativeLoop(Control target)
    {
        _target = target;
        target.AttachedToVisualTree += OnTargetAttached;
        target.DetachedFromVisualTree += OnTargetDetached;
    }

    /// <summary>True while frame requests for the loop are live (false = static, no animation object).</summary>
    public bool IsRunning => _running;

    /// <summary>
    /// Configures the loop. <paramref name="periodMs"/> &lt;= 0 stops it and leaves the decorative visual
    /// fully static; a positive period (re)starts it from phase 0 — or, after attach, from the paused phase.
    /// </summary>
    public void Configure(IFluentMotionClock? clock, double periodMs, Action<double>? update)
    {
        _clock = clock;
        _periodMs = periodMs > 0 ? periodMs : 0d;
        _update = _periodMs > 0 ? update : null;
        if (_clock is null || _periodMs <= 0 || _update is null)
        {
            StopRunning();
            return;
        }

        Run(_target.IsAttachedToVisualTree() ? _phaseAtPause : 0d);
    }

    /// <summary>Pauses the loop at its current phase; in-flight frame callbacks are invalidated.</summary>
    public void Pause()
    {
        if (!_running)
        {
            return;
        }

        _phaseAtPause = Phase();
        StopRunning();
    }

    /// <summary>Resumes from the paused phase. No-op when static, already running, or not configured.</summary>
    public void Resume()
    {
        if (_running || _clock is null || _update is null || _periodMs <= 0)
        {
            return;
        }

        Run(_phaseAtPause);
    }

    /// <summary>Current loop phase in [0,1); the paused phase while not running.</summary>
    public double Phase()
    {
        if (!_running || _clock is null || _periodMs <= 0)
        {
            return _phaseAtPause;
        }

        var elapsed = (_clock.Now - _anchor).TotalMilliseconds % _periodMs;
        if (elapsed < 0) elapsed += _periodMs;
        return elapsed / _periodMs;
    }

    private void Run(double fromPhase)
    {
        StopRunning();
        if (!_target.IsAttachedToVisualTree() || _window?.IsVisible == false)
        {
            // The attach handler restarts the configured loop when the cached page returns to the tree.
            _phaseAtPause = fromPhase;
            return;
        }

        _running = true;
        _anchor = _clock!.Now - TimeSpan.FromMilliseconds(fromPhase * _periodMs);
        var generation = ++_generation;
        _update!(fromPhase);
        void Tick()
        {
            if (!_running || generation != _generation)
            {
                return;
            }

            _update!(Phase());
            _clock!.RequestFrame(_target, Tick);
        }

        _clock.RequestFrame(_target, Tick);
    }

    private void StopRunning()
    {
        _running = false;
        ++_generation;
    }

    private void OnTargetAttached(object? sender, VisualTreeAttachmentEventArgs e)
    {
        if (!ReferenceEquals(TopLevel.GetTopLevel(_target) as Window, _window))
        {
            DetachWindow();
            _window = TopLevel.GetTopLevel(_target) as Window;
            if (_window is not null)
            {
                // 02-motion §4: long decorative loops pause while the window is deactivated/hidden and
                // continue from the same phase on activation.
                _window.Activated += OnWindowActivated;
                _window.Deactivated += OnWindowDeactivated;
                _window.PropertyChanged += OnWindowPropertyChanged;
            }
        }

        Resume();
    }

    private void OnTargetDetached(object? sender, VisualTreeAttachmentEventArgs e)
    {
        if (_running)
        {
            _phaseAtPause = Phase();
        }

        // Stop-frame on detach: no frame callback outlives the visual tree it was animating.
        StopRunning();
        DetachWindow();
    }

    private void OnWindowActivated(object? sender, EventArgs e) => Resume();

    private void OnWindowPropertyChanged(object? sender, AvaloniaPropertyChangedEventArgs e)
    {
        if (e.Property == Visual.IsVisibleProperty)
        {
            if (_window?.IsVisible == true) Resume();
            else Pause();
        }
    }

    private void OnWindowDeactivated(object? sender, EventArgs e) => Pause();

    private void DetachWindow()
    {
        if (_window is null)
        {
            return;
        }

        _window.Activated -= OnWindowActivated;
        _window.Deactivated -= OnWindowDeactivated;
        _window.PropertyChanged -= OnWindowPropertyChanged;
        _window = null;
    }
}

/// <summary>
/// FEA-06-RESIDUAL-2 IN-1.2: the 400ms page-turn particle effect. One layer is created per turn,
/// painted above the page surface as sparse, non-interactive edge particles, driven by <see cref="FluentFrameAnimation"/>,
/// and removed from the tree when the finite run completes or the layer detaches.
/// </summary>
internal static class FluentPageTurnDecor
{
    /// <summary>Plays one page-turn particle run in <paramref name="area"/>; no-op when disabled.</summary>
    public static void Play(IFluentMotionClock clock, double milliseconds, Grid area)
    {
        if (milliseconds <= 0)
        {
            return; // IN-1.2: reduce / auto(system-off) / category-off creates no particle layer.
        }

        if (!area.IsAttachedToVisualTree())
        {
            // Decorations belong to the visible reader; a cached/detached page never spawns them
            // (its finite animation would finish immediately and leak nothing).
            return;
        }

        // A newer turn supersedes an in-flight one instead of stacking layers. The old layer's
        // detach-triggered completion must not remove itself again while this collection edit runs,
        // so detach-time cleanup is deferred to the dispatcher (see below).
        for (var i = area.Children.Count - 1; i >= 0; i--)
        {
            if (area.Children[i] is Border border && border.Classes.Contains("fluent-decorative-particles"))
            {
                area.Children.RemoveAt(i);
            }
        }

        var layer = CreateLayer();
        area.Children.Add(layer); // foreground: the opaque page surface must not hide the particles.
        var detached = false;
        var window = TopLevel.GetTopLevel(area) as Window;
        var animation = new FluentFrameAnimation(layer);
        var progressAtPause = 0d;
        var startProgress = 0d;
        var startedAt = clock.Now;
        var running = false;
        void Unsubscribe()
        {
            if (window is null) return;
            window.Activated -= OnActivated;
            window.Deactivated -= OnDeactivated;
            window.PropertyChanged -= OnWindowChanged;
        }
        layer.DetachedFromVisualTree += (_, _) => { detached = true; Unsubscribe(); };
        void RemoveFromHost()
        {
            if (detached)
            {
                // Detaching (page navigated away or layer superseded): removing synchronously here
                // would re-enter the visual-tree change that raised this completion.
                Avalonia.Threading.Dispatcher.UIThread.Post(() =>
                {
                    if (layer.Parent is Panel panel)
                    {
                        panel.Children.Remove(layer);
                    }
                });
                return;
            }

            if (layer.Parent is Panel host)
            {
                host.Children.Remove(layer);
            }
        }

        void Resume()
        {
            if (running || detached || window?.IsVisible == false) return;
            running = true;
            startProgress = progressAtPause;
            startedAt = clock.Now;
            animation.Run(clock, milliseconds * (1 - startProgress),
                progress => Update(layer, startProgress + (1 - startProgress) * progress),
                () => { running = false; Unsubscribe(); RemoveFromHost(); });
        }
        void Pause()
        {
            if (!running) return;
            progressAtPause = Math.Clamp(startProgress + (clock.Now - startedAt).TotalMilliseconds / milliseconds, 0, 1);
            animation.Cancel(); running = false;
        }
        void OnActivated(object? sender, EventArgs args) => Resume();
        void OnDeactivated(object? sender, EventArgs args) => Pause();
        void OnWindowChanged(object? sender, AvaloniaPropertyChangedEventArgs args)
        {
            if (args.Property != Visual.IsVisibleProperty) return;
            if (window?.IsVisible == true) Resume(); else Pause();
        }
        if (window is not null)
        {
            window.Activated += OnActivated;
            window.Deactivated += OnDeactivated;
            window.PropertyChanged += OnWindowChanged;
        }
        Resume();
    }

    private sealed record Particle(double X, double Bottom, double Size, double Delay, double Rise, double Drift);
    private static readonly Particle[] Particles =
    [
        new(.08, 26, 5, 0, 30, -6), new(.20, 14, 4, .045, 24, 8),
        new(.33, 34, 6, .09, 36, -10), new(.46, 18, 4, .135, 26, 6),
        new(.58, 30, 5, .18, 32, -8), new(.71, 12, 4, .225, 22, 10),
        new(.84, 28, 6, .27, 34, -6), new(.94, 20, 4, .30, 28, 8),
    ];

    private static Border CreateLayer()
    {
        var canvas = new Canvas();
        foreach (var spec in Particles)
        {
            var dot = new Ellipse { Width = spec.Size, Height = spec.Size, Opacity = 0,
                Tag = spec, RenderTransform = new TranslateTransform() };
            dot[!Shape.FillProperty] = new DynamicResourceExtension("Nm.Color.Accent.Base");
            canvas.Children.Add(dot);
        }
        // Layout positions are stable throughout a run. Resizing is the only reason to reposition.
        canvas.SizeChanged += (_, _) =>
        {
            foreach (var dot in canvas.Children.OfType<Ellipse>())
            {
                var spec = (Particle)dot.Tag!;
                Canvas.SetLeft(dot, spec.X * canvas.Bounds.Width);
                Canvas.SetTop(dot, Math.Max(0, canvas.Bounds.Height - spec.Bottom));
            }
        };
        return new Border { Child = canvas, IsHitTestVisible = false,
            Classes = { "fluent-decorative", "fluent-decorative-particles" } };
    }

    private static void Update(Border layer, double progress)
    {
        foreach (var dot in ((Canvas)layer.Child!).Children.OfType<Ellipse>())
        {
            var spec = (Particle)dot.Tag!;
            var local = Math.Clamp((progress - spec.Delay) / (1 - spec.Delay), 0, 1);
            dot.Opacity = .75 * Math.Sin(Math.PI * local);
            var transform = (TranslateTransform)dot.RenderTransform!;
            transform.X = spec.Drift * local;
            transform.Y = -spec.Rise * local;
        }
    }

}

/// <summary>
/// IN-1.1: gradient stops are plain freezables outside the visual tree, so a DynamicResource binding on
/// them never resolves. This helper keeps the two stops equal to the existing Bg tokens by resolving
/// them from the layer's own resource scope and re-resolving whenever that scope changes (theme or
/// high-contrast swap) — the decorative layer therefore never invents a colour of its own.
/// </summary>
internal static class FluentTokenGradient
{
    public static void Bind(Border layer, LinearGradientBrush brush, string fromKey, string toKey)
    {
        void Refresh()
        {
            // The design tokens live in the application dictionaries (DesignSystemThemeManager swaps
            // them there), so resolve from the application scope — the layer itself owns no resources.
            var app = Application.Current;
            if (app is null)
            {
                return;
            }

            var variant = layer.ActualThemeVariant;
            if (app.TryGetResource(fromKey, variant, out var from) && from is ISolidColorBrush fromBrush)
            {
                brush.GradientStops[0].Color = fromBrush.Color;
            }

            if (app.TryGetResource(toKey, variant, out var to) && to is ISolidColorBrush toBrush)
            {
                brush.GradientStops[^1].Color = toBrush.Color;
            }
        }

        Application? subscribed = null;
        void OnResourcesChanged(object? sender, Avalonia.Controls.ResourcesChangedEventArgs e) => Refresh();
        void Subscribe()
        {
            if (subscribed is null && Application.Current is { } application)
            {
                subscribed = application;
                subscribed.ResourcesChanged += OnResourcesChanged;
            }
            Refresh();
        }
        layer.AttachedToVisualTree += (_, _) => Subscribe();
        layer.DetachedFromVisualTree += (_, _) =>
        {
            if (subscribed is not null) subscribed.ResourcesChanged -= OnResourcesChanged;
            subscribed = null;
        };
        if (layer.IsAttachedToVisualTree()) Subscribe();
        else Refresh();
    }
}
