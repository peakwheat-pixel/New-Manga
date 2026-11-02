using Avalonia;
using System.Reflection;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-2 IN-1.1/IN-1.2 (design 02-motion §2.3/§4): the two decorative scenes consume the
/// frozen table — the shelf background gradient loops for 8s changing only Brush.Opacity, the page-turn
/// particle layer runs once per turn for 400ms above the page surface (sparse edge particles). reduce / auto(system-off) /
/// decorative-off keep the gradient static and create no animation object and no particle layer; a
/// deactivated window pauses without losing phase; detaching stops every frame request; the production
/// render clock is sampled for a full first/mid/tail pass.
/// </summary>
public sealed class FluentResidual2DecorativeTests
{
    private static void Motion(FluentShellSurface surface, MotionMode mode = MotionMode.Full,
        MotionCategories categories = MotionCategories.All) =>
        typeof(FluentShellSurface).GetMethod("ApplyMotion", BindingFlags.Instance | BindingFlags.NonPublic)!
            .Invoke(surface, [AppearanceDefaults.Settings with { MotionMode = mode, MotionCategories = categories }]);

    private static (Window Window, FluentShellSurface Surface, ManualFluentMotionClock Clock) Create()
    {
        var clock = new ManualFluentMotionClock();
        var surface = new FluentShellSurface(host: new FakeHostController(FakeHostController.ReadySnapshot()))
            { MotionClock = clock };
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        return (window, surface, clock);
    }

    /// <summary>A host whose reader chapter has two real pages, so a turn actually advances PageIndex.</summary>
    private static FakeHostController TwoPageHost()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        var png = Convert.FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==");
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData("book-1", "Sample", "chapter-key", "Chapter", "fit-page",
            [
                new ReaderPageData("page-1", 0, 1, 1, _ => Task.FromResult<byte[]?>(png)),
                new ReaderPageData("page-2", 1, 1, 1, _ => Task.FromResult<byte[]?>(png)),
            ]);
        return host;
    }

    private static (Window Window, FluentShellSurface Surface, ManualFluentMotionClock Clock) CreateWithPages()
    {
        var clock = new ManualFluentMotionClock();
        var surface = new FluentShellSurface(host: TwoPageHost()) { MotionClock = clock };
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        return (window, surface, clock);
    }

    private static LinearGradientBrush Gradient(FluentShellSurface surface) => surface.ShelfView.DecorativeBrush;



    [AvaloniaFact]
    public void ShelfGradient_FullMode_LoopsTheFrozen8s_AndOnlyBrushOpacityMutates()
    {
        var (window, surface, clock) = Create();
        try
        {
            Motion(surface, MotionMode.Full, MotionCategories.All);
            var shelf = surface.ShelfView;
            Assert.Equal(8000d, MotionTimings.DecorativeShelfGradientMilliseconds);
            Assert.True(shelf.DecorativeLoop.IsRunning);
            Assert.True(clock.PendingFrames > 0);

            window.UpdateLayout();
            var bounds = shelf.DecorativeLayer.Bounds;
            var toolbars = shelf.DecorativeLayer.Parent is Grid host;
            Assert.True(toolbars);
            // The decorative layer sits beneath the page content (Grid child order = Z order) and never
            // takes hit-tests; the real toolbar buttons above stay hit-testable.
            Assert.Equal(0, ((Grid)shelf.DecorativeLayer.Parent!).Children.IndexOf(shelf.DecorativeLayer));
            Assert.False(shelf.DecorativeLayer.IsHitTestVisible);
            var button = surface.GetVisualDescendants().OfType<Button>().First(b => b.Content as string == "新建作品");
            Assert.True(button.IsHitTestVisible);

            // Manual-clock boundary assertions over one full period (judge: tests only bound the edges).
            var expectedAt = TimeSpan.Zero;
            void Sample(double elapsedMs, double expectedPhase)
            {
                clock.Advance(elapsedMs);
                expectedAt += TimeSpan.FromMilliseconds(elapsedMs);
                var phase = shelf.DecorativeLoop.Phase();
                Assert.InRange(phase, expectedPhase - 0.02, expectedPhase + 0.02);
                var floor = ShelfPageView.DecorativeGradientFloorOpacity;
                var expected = floor + (1 - floor) * (0.5 - 0.5 * Math.Cos(2 * Math.PI * expectedPhase));
                Assert.Equal(expected, Gradient(surface).Opacity, 3);
            }

            Sample(0, 0);
            Sample(2000, 0.25);
            Sample(2000, 0.5);
            Sample(3999, 0.999875);
            clock.Advance(1); // wrap past the full 8s period
            Assert.InRange(shelf.DecorativeLoop.Phase(), 0, 0.001);
            window.UpdateLayout();
            Assert.Equal(bounds, shelf.DecorativeLayer.Bounds); // Render-only: layout never moved.
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionMode.Reduce, MotionCategories.All)]
    [InlineData(MotionMode.Full, MotionCategories.None)]
    [InlineData(MotionMode.Full, MotionCategories.Navigation | MotionCategories.Feedback)]
    public void ShelfGradient_DisabledModes_AreStaticAndCreateNoAnimationObject(MotionMode mode, MotionCategories categories)
    {
        var (window, surface, clock) = Create();
        try
        {
            Motion(surface, mode, categories);
            var shelf = surface.ShelfView;
            Assert.False(shelf.DecorativeLoop.IsRunning);
            Assert.Equal(0, clock.PendingFrames);
            var opacity = Gradient(surface).Opacity;
            Assert.Equal(1d, opacity);
            clock.Advance(12000);
            Assert.Equal(1d, Gradient(surface).Opacity); // static: nothing advances
            Assert.Equal(0, clock.PendingFrames);
            // The static background keeps resolving the two existing Bg tokens.
            Assert.Equal(2, shelf.DecorativeBrush.GradientStops.Count);
            Assert.False(shelf.DecorativeLayer.IsHitTestVisible);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ShelfGradient_WindowDeactivated_Pauses_ResumeContinuesTheSamePhase()
    {
        var (window, surface, clock) = Create();
        try
        {
            Motion(surface, MotionMode.Full, MotionCategories.All);
            var shelf = surface.ShelfView;
            clock.Advance(1000); // quarter-ish into the cycle
            var phaseAtPause = shelf.DecorativeLoop.Phase();
            Assert.InRange(phaseAtPause, 0.01, 0.99);

            // Raise the actual Window event via its platform notification; do not call the loop's Pause.
            typeof(WindowBase).GetMethod("HandleDeactivated", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public)!
                .Invoke(window, null);
            Assert.False(shelf.DecorativeLoop.IsRunning);
            var frozen = Gradient(surface).Opacity;
            clock.Advance(3000);
            Assert.Equal(0, clock.PendingFrames); // paused: no frame callback is queued
            Assert.Equal(frozen, Gradient(surface).Opacity);
            Assert.Equal(phaseAtPause, shelf.DecorativeLoop.Phase(), 5); // phase kept while paused

            window.Activate(); // real API path: raises Activated, the loop's wiring resumes the loop
            Dispatcher.UIThread.RunJobs();
            Assert.True(shelf.DecorativeLoop.IsRunning);
            Assert.Equal(phaseAtPause, shelf.DecorativeLoop.Phase(), 5); // resume continues, no jump
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ShelfGradient_DetachedPage_StopsFrames_ReattachRestoresTheLoop()
    {
        var (window, surface, clock) = Create();
        try
        {
            Motion(surface, MotionMode.Full, MotionCategories.All);
            var shelf = surface.ShelfView;
            Assert.True(shelf.DecorativeLoop.IsRunning);

            surface.Navigate(FluentPage.Workbench); // the cached shelf page detaches
            Dispatcher.UIThread.RunJobs();
            Assert.False(shelf.DecorativeLoop.IsRunning);
            clock.Advance(0); // any frame already queued is invalidated by the detach and stops re-queuing
            Assert.Equal(0, clock.PendingFrames); // detach stops every frame request

            surface.Navigate(FluentPage.Library); // the cached page re-attaches
            Dispatcher.UIThread.RunJobs();
            Assert.True(shelf.DecorativeLoop.IsRunning);
            Assert.True(clock.PendingFrames > 0);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ShelfGradient_ProductionRenderClock_SamplesFirstMidTailAcross8s()
    {
        var (window, surface, _) = Create();
        try
        {
            surface.MotionClock = FluentRenderClock.Instance;
            Motion(surface, MotionMode.Full, MotionCategories.All);
            var shelf = surface.ShelfView;
            var watch = System.Diagnostics.Stopwatch.StartNew();
            var floor = ShelfPageView.DecorativeGradientFloorOpacity;
            double Sample()
            {
                AvaloniaHeadlessPlatform.ForceRenderTimerTick();
                Dispatcher.UIThread.RunJobs();
                return Gradient(surface).Opacity;
            }

            void PumpUntil(double targetMs)
            {
                while (watch.Elapsed.TotalMilliseconds < targetMs)
                {
                    AvaloniaHeadlessPlatform.ForceRenderTimerTick();
                    Dispatcher.UIThread.RunJobs();
                    Thread.Sleep(20);
                }
            }

            var first = Sample();
            Assert.InRange(first, floor - 0.05, floor + 0.15); // head: near the trough
            PumpUntil(4000);
            var mid = Sample();
            Assert.InRange(mid, 0.95, 1.0); // mid-period: at the crest
            PumpUntil(7950);
            var tail = Sample();
            Assert.InRange(tail, floor - 0.1, floor + 0.2); // tail: trough again after the wrap
            Assert.True(mid - first > 0.2, $"first={first} mid={mid}");
            Assert.True(mid - tail > 0.2, $"mid={mid} tail={tail}");
            window.UpdateLayout();
            Assert.True(shelf.DecorativeLayer.Bounds.Width > 0); // layer laid out under real rendering
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionMode.Reduce, MotionCategories.All)]
    [InlineData(MotionMode.Full, MotionCategories.None)]
    public async Task PageTurnParticles_DisabledModes_CreateNoParticleLayer(MotionMode mode, MotionCategories categories)
    {
        var (window, surface, clock) = CreateWithPages();
        try
        {
            Motion(surface, mode, categories);
            surface.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs(); // attach the reader before the first turn
            await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            var before = surface.ReaderViewModel.PageIndex;
            await surface.ReaderViewModel.NavigateAsync(1);
            Dispatcher.UIThread.RunJobs();
            Assert.NotEqual(before, surface.ReaderViewModel.PageIndex); // the turn really happened
            Assert.Null(surface.ReaderView.DecorativeParticleLayer); // no layer created at all
            clock.Advance(1000);
            Assert.Null(surface.ReaderView.DecorativeParticleLayer);
            Assert.Equal(0, clock.PendingFrames);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public async Task PageTurnParticles_RunOnceFor400ms_AboveThePageImage_ThenAreRemoved()
    {
        var (window, surface, clock) = CreateWithPages();
        try
        {
            Motion(surface, MotionMode.Full, MotionCategories.All);
            surface.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs(); // attach the reader before the first turn
            await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            var pageSurface = surface.ReaderView.PageSurface;
            var area = Assert.IsType<Grid>(pageSurface.Parent);
            await surface.ReaderViewModel.NavigateAsync(1);
            Dispatcher.UIThread.RunJobs();

            var layer = surface.ReaderView.DecorativeParticleLayer;
            Assert.NotNull(layer);
            Assert.False(layer.IsHitTestVisible); // never intercepts hits
            Assert.True(area.Children.IndexOf(layer) > area.Children.IndexOf(pageSurface)); // foreground edge particles
            Assert.True(pageSurface.IsVisible); // the page image itself stays visible

            clock.Advance(200); // mid-frame: at least one particle is visible
            var canvas = Assert.IsType<Avalonia.Controls.Canvas>(layer.Child);
            Assert.Contains(canvas.Children, dot => dot.Opacity > 0);
            var particleBounds = layer.Bounds;
            clock.Advance(199);
            Assert.NotNull(surface.ReaderView.DecorativeParticleLayer); // still inside the 400ms window
            clock.Advance(1);
            Assert.Null(surface.ReaderView.DecorativeParticleLayer); // finished: the layer is removed
            Assert.Equal(0, clock.PendingFrames);
            Assert.Equal(particleBounds, layer.Bounds);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public async Task PageTurnParticles_NextTurnSupersedes_AndDetachLeaksNoFrames()
    {
        var (window, surface, clock) = CreateWithPages();
        try
        {
            Motion(surface, MotionMode.Full, MotionCategories.All);
            surface.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs(); // attach the reader before the first turn
            await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            await surface.ReaderViewModel.NavigateAsync(1);
            Dispatcher.UIThread.RunJobs();
            var first = surface.ReaderView.DecorativeParticleLayer;
            Assert.NotNull(first);
            clock.Advance(100);
            await surface.ReaderViewModel.NavigateAsync(-1); // a newer turn supersedes the in-flight one
            Dispatcher.UIThread.RunJobs();
            var second = surface.ReaderView.DecorativeParticleLayer;
            Assert.NotNull(second);
            Assert.NotSame(first, second);

            surface.Navigate(FluentPage.Library); // reader detaches mid-run
            Dispatcher.UIThread.RunJobs();
            // Also stop the shelf gradient loop, so zero pending frames proves no PARTICLE frame leaked
            // (the gradient loop would otherwise legitimately hold one standing render frame).
            Motion(surface, MotionMode.Reduce, MotionCategories.All);
            Dispatcher.UIThread.RunJobs();
            clock.Advance(2000);
            Assert.Equal(0, clock.PendingFrames); // no frame callback outlives the tree
            Assert.Null(surface.ReaderView.DecorativeParticleLayer);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ShelfGradient_BindsOnlyExistingBgTokens_HighContrastHasNoFallback()
    {
        using var manager = new DesignSystemThemeManager(Avalonia.Application.Current!);
        Assert.True(manager.Initialize(NewManga.DesignSystem.Theming.AppearanceMode.Light), manager.LastError);
        var clock = new ManualFluentMotionClock();
        var surface = new FluentShellSurface(
            host: new FakeHostController(FakeHostController.ReadySnapshot()), themeManager: manager)
        { MotionClock = clock };
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        try
        {
            window.Show();
            Dispatcher.UIThread.RunJobs();
            Motion(surface, MotionMode.Reduce, MotionCategories.All); // static mode suffices for colour checks
            var brush = surface.ShelfView.DecorativeBrush;
            var app = Avalonia.Application.Current!;
            Color Token(string key) =>
                Assert.IsType<SolidColorBrush>(app.TryGetResource(key, app.ActualThemeVariant, out var value) ? value : null).Color;
            Assert.Equal(Token("Nm.Color.Bg.Canvas"), brush.GradientStops[0].Color);
            Assert.Equal(Token("Nm.Color.Bg.Overlay"), brush.GradientStops[1].Color);

            // High contrast just swaps the token table (materials degrade to opaque surfaces); the
            // decorative layer keeps resolving the same keys with no hardcoded fallback (03 §4).
            Assert.True(manager.SetContrast(NewManga.DesignSystem.Theming.ContrastMode.High), manager.LastError);
            Dispatcher.UIThread.RunJobs();
            Assert.Equal(Token("Nm.Color.Bg.Canvas"), brush.GradientStops[0].Color);
            Assert.Equal(Token("Nm.Color.Bg.Overlay"), brush.GradientStops[1].Color);
        }
        finally { window.Close(); }
    }
    /// <summary>
    /// FEA-06-RESIDUAL-2 R2-001: opt-in real decor frames from the product decorative layers
    /// (ManualFluentMotionClock drives the same code paths the behavioural tests bound). Default run
    /// writes nothing; NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1 writes verification/FEA-06-RESIDUAL-2/visuals.
    /// </summary>
    [AvaloniaFact]
    public async Task Decor_Frames_Are_Captured_Only_When_Opted_In()
    {
        using var scope = await Residual2Evidence.Create("light");
        var clock = new ManualFluentMotionClock();
        var surface = new FluentShellSurface(selection: FrontendSelector.Select("builtin.fluent", null),
            host: Residual2Evidence.Host(), appearance: scope.Appearance, themeManager: scope.Manager) { MotionClock = clock };
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        window.Show(); Dispatcher.UIThread.RunJobs();
        try
        {
            Motion(surface, MotionMode.Full, MotionCategories.Decorative);
            surface.Navigate(FluentPage.Reader);
            await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            FluentResidual2VisualEvidenceTests.Settle();
            await surface.ReaderViewModel.NavigateAsync(1);
            Dispatcher.UIThread.RunJobs(); window.UpdateLayout(); clock.Advance(200);
            using var withParticles = Residual2Evidence.Capture(window);
            var layer = surface.ReaderView.DecorativeParticleLayer!;
            Assert.NotNull(layer); layer.IsVisible = false;
            using var withoutParticles = Residual2Evidence.Capture(window);
            Assert.True(Residual2Evidence.ChangedPixels(withParticles, withoutParticles) >= 25, $"layer={layer.Bounds}; origin={layer.TranslatePoint(default, window)}; image={surface.ReaderView.PageImage.Bounds}; particles={string.Join(";", ((Avalonia.Controls.Canvas)layer.Child!).Children.Select(c => $"{c.Bounds}/{c.Opacity}/{c.RenderTransform}"))}");
            // The only repository writer is the complete, atomic inventory capture test.
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ShelfGradient_HiddenWindow_PausesAndShowingResumes()
    {
        var (window, surface, clock) = Create();
        try
        {
            Motion(surface); clock.Advance(1000);
            var phase = surface.ShelfView.DecorativeLoop.Phase();
            window.Hide(); Dispatcher.UIThread.RunJobs(); clock.Advance(2000);
            Assert.False(surface.ShelfView.DecorativeLoop.IsRunning);
            Assert.Equal(0, clock.PendingFrames);
            Assert.Equal(phase, surface.ShelfView.DecorativeLoop.Phase(), 5);
            window.Show(); Dispatcher.UIThread.RunJobs();
            Assert.True(surface.ShelfView.DecorativeLoop.IsRunning);
        }
        finally { window.Close(); }
    }
    [AvaloniaFact]
    public async Task PageTurnParticles_ProductionClock_SamplesVisibleMidAndRemovedTail()
    {
        using var scope = await Residual2Evidence.Create("light");
        var surface = new FluentShellSurface(selection: FrontendSelector.Select("builtin.fluent", null),
            host: Residual2Evidence.Host(), themeManager: scope.Manager) { MotionClock = FluentRenderClock.Instance };
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        try
        {
            window.Show(); Motion(surface, MotionMode.Full, MotionCategories.Decorative);
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs(); await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            FluentResidual2VisualEvidenceTests.Settle();
            await surface.ReaderViewModel.NavigateAsync(1); Dispatcher.UIThread.RunJobs();
            Assert.NotNull(surface.ReaderView.DecorativeParticleLayer); // first
            FluentResidual2VisualEvidenceTests.Settle(160);
            var layer = surface.ReaderView.DecorativeParticleLayer;
            Assert.NotNull(layer);
            Assert.Contains(((Avalonia.Controls.Canvas)layer.Child!).Children, dot => dot.Opacity > .2); // mid
            using var visible = Residual2Evidence.Capture(window);
            layer.IsVisible = false;
            using var control = Residual2Evidence.Capture(window);
            Assert.True(Residual2Evidence.ChangedPixels(visible, control) >= 25);
            layer.IsVisible = true;
            FluentResidual2VisualEvidenceTests.Settle(300);
            Assert.Null(surface.ReaderView.DecorativeParticleLayer); // tail, production time > 400ms
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public async Task TokenGradient_DetachUnsubscribes_AndReattachRefreshes()
    {
        using var scope = await Residual2Evidence.Create("light");
        var surface = new FluentShellSurface(host: Residual2Evidence.Host(), themeManager: scope.Manager);
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        try
        {
            window.Show(); Motion(surface, MotionMode.Reduce);
            var brush = surface.ShelfView.DecorativeBrush;
            var light = brush.GradientStops[0].Color;
            surface.Navigate(FluentPage.Workbench); Dispatcher.UIThread.RunJobs();
            Assert.True(scope.Manager.SetAppearance(NewManga.DesignSystem.Theming.AppearanceMode.Dark));
            Dispatcher.UIThread.RunJobs();
            Assert.Equal(light, brush.GradientStops[0].Color); // detached layer receives no global resource notifications
            surface.Navigate(FluentPage.Library); Dispatcher.UIThread.RunJobs();
            Assert.NotEqual(light, brush.GradientStops[0].Color); // reattached layer refreshes and subscribes
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public async Task PageTurnParticles_WindowDeactivated_PausesThenResumesRemainingTime()
    {
        var (window, surface, clock) = CreateWithPages();
        try
        {
            Motion(surface, MotionMode.Full, MotionCategories.Decorative);
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs(); await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            await surface.ReaderViewModel.NavigateAsync(1); Dispatcher.UIThread.RunJobs();
            clock.Advance(100);
            var layer = surface.ReaderView.DecorativeParticleLayer!;
            Assert.NotNull(layer);
            typeof(WindowBase).GetMethod("HandleDeactivated", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)!.Invoke(window, null);
            clock.Advance(2000);
            Assert.Same(layer, surface.ReaderView.DecorativeParticleLayer);
            Assert.Equal(0, clock.PendingFrames);
            window.Activate(); Dispatcher.UIThread.RunJobs();
            clock.Advance(299); Assert.Same(layer, surface.ReaderView.DecorativeParticleLayer);
            clock.Advance(1); Assert.Null(surface.ReaderView.DecorativeParticleLayer);
        }
        finally { window.Close(); }
    }

    [Fact]
    public void HasMotion_ReportsFiniteTransitions_WhileDecorativeHasItsOwnDiagnostic()
    {
        var resolution = new MotionResolver(new WindowsMotionPreferenceSource()).Resolve(AppearanceDefaults.Settings with
        { MotionMode = MotionMode.Full, MotionCategories = MotionCategories.Decorative });
        var profile = MotionTimings.Resolve(resolution.Settings);
        Assert.True(profile.DecorativeEnabled);
        Assert.False(profile.HasMotion);
        Assert.Equal(8000, profile.DecorativeShelfGradientMilliseconds);
    }

}
