using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Animation;
using Avalonia.Animation.Easings;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Tests;

public sealed class FluentR2ReworkTests
{
    private static void Motion(FluentShellSurface surface, MotionMode mode = MotionMode.Full,
        MotionCategories categories = MotionCategories.All) =>
        typeof(FluentShellSurface).GetMethod("ApplyMotion", BindingFlags.Instance | BindingFlags.NonPublic)!
            .Invoke(surface, [AppearanceDefaults.Settings with { MotionMode = mode, MotionCategories = categories }]);

    private static T Field<T>(object owner, string name) => (T)owner.GetType()
        .GetField(name, BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(owner)!;

    private static Button Named(Control root, string name) => root.GetVisualDescendants().OfType<Button>()
        .Single(b => AutomationProperties.GetName(b) == name);

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static (Window Window, FluentShellSurface Surface, ManualFluentMotionClock Clock) Create(AppearanceCoordinator? appearance = null, FakeHostController? host = null)
    {
        var clock = new ManualFluentMotionClock();
        var surface = new FluentShellSurface(host: host ?? new FakeHostController(FakeHostController.ReadySnapshot()), appearance: appearance)
            { MotionClock = clock };
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        Motion(surface);
        return (window, surface, clock);
    }

    [AvaloniaFact]
    public void R2001_Reader_FadesBothBars_At80_159_160ms_AndCancelsOldExitOnWake()
    {
        var (window, surface, clock) = Create();
        try
        {
            surface.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();
            surface.ReaderViewModel.HideToolBarsAfterIdle();
            foreach (var bar in new[] { surface.ReaderView.TopBar, surface.ReaderView.BottomBar })
            {
                Assert.True(bar.IsVisible);
                Assert.Equal(1, bar.Opacity);
                Assert.False(bar.IsHitTestVisible);
            }
            clock.Advance(80);
            foreach (var bar in new[] { surface.ReaderView.TopBar, surface.ReaderView.BottomBar })
                Assert.Equal(1 - new SplineEasing(.4, 0, 1, 1).Ease(.5), bar.Opacity, 6);
            clock.Advance(79);
            Assert.True(surface.ReaderView.TopBar.IsVisible);
            Assert.InRange(surface.ReaderView.TopBar.Opacity, .000001, .999999);
            clock.Advance(1);
            Assert.False(surface.ReaderView.TopBar.IsVisible);
            Assert.False(surface.ReaderView.BottomBar.IsVisible);
            Assert.Equal(0, surface.ReaderView.BottomBar.Opacity);
            surface.ReaderView.NotifyInteraction();
            Assert.Equal(1, surface.ReaderView.TopBar.Opacity);
            surface.ReaderViewModel.HideToolBarsAfterIdle();
            clock.Advance(80);
            surface.ReaderView.NotifyInteraction();
            clock.Advance(200);
            Assert.True(surface.ReaderView.TopBar.IsVisible);
            Assert.Equal(1, surface.ReaderView.TopBar.Opacity);
            Assert.True(surface.ReaderView.SideRail.IsVisible);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionMode.Reduce, MotionCategories.All)]
    [InlineData(MotionMode.Full, MotionCategories.Feedback)]
    public void R2001_NavigationOff_ReaderAndPageOverlaysFinishImmediately(MotionMode mode, MotionCategories categories)
    {
        var (window, surface, clock) = Create();
        try
        {
            surface.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();
            surface.ReaderViewModel.HideToolBarsAfterIdle();
            clock.Advance(80);
            Motion(surface, mode, categories);
            Assert.True(surface.ReaderViewModel.AreToolBarsReducedMotion);
            Assert.Null(surface.ReaderView.TopBar.Transitions);
            Assert.False(surface.ReaderView.TopBar.IsVisible);
            Assert.Equal(0, surface.ReaderView.TopBar.Opacity);
            surface.ReaderView.NotifyInteraction();
            Assert.Equal(1, surface.ReaderView.TopBar.Opacity);
            surface.ReaderViewModel.HideToolBarsAfterIdle();
            Assert.False(surface.ReaderView.BottomBar.IsVisible);
            surface.Navigate(FluentPage.Library);
            Dispatcher.UIThread.RunJobs();
            surface.ShelfView.ShowNewBookDialog();
            var dialog = Field<FluentDialog>(surface.ShelfView, "_dialog");
            Assert.True(dialog.IsVisible);
            Assert.Equal(1, dialog.Opacity);
            Click(Named(dialog, "取消"));
            Assert.False(dialog.IsVisible);
            Assert.Equal(0, dialog.Opacity);
            surface.ShelfView.OpenRecycleDrawer();
            var drawer = Field<Drawer>(surface.ShelfView, "_recycleDrawer");
            Assert.Equal(1, drawer.Opacity);
            drawer.IsOpen = false;
            Assert.False(drawer.IsVisible);
            surface.Navigate(FluentPage.Settings);
            Dispatcher.UIThread.RunJobs();
            surface.SettingsViewModel.UpdateDraft(surface.SettingsViewModel.Draft with { MaterialAcrylicStrength = .123 });
            surface.Navigate(FluentPage.Library);
            var leave = Field<FluentDialog>(surface.SettingsView, "_leaveDialog");
            Assert.True(leave.IsVisible);
            Assert.Equal(1, leave.Opacity);
            surface.SettingsView.CancelLeave();
            Assert.False(leave.IsVisible);
            surface.SettingsViewModel.UpdateDraft(AppearanceDefaults.Settings);
            surface.SettingsViewModel.SelectedGroup = SettingsGroupId.Providers;
            Dispatcher.UIThread.RunJobs();
            Click(Named(surface.SettingsView, "添加 Provider Profile"));
            var confirmation = Field<FluentDialog>(surface.SettingsView, "_confirmation");
            Assert.Equal(1, confirmation.Opacity);
            surface.SettingsView.CancelConfirmation();
            Assert.False(confirmation.IsVisible);
            clock.Advance(500);
            Assert.False(dialog.IsVisible);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(0)] // settings leave
    [InlineData(1)] // settings provider confirmation
    [InlineData(2)] // shelf dialog
    [InlineData(3)] // shelf drawer
    public void R2001_ActualPageOverlays_Enter200_Exit160_WithFrozenCurves(int kind)
    {
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(Path.GetTempPath(), "nm-r2-" + Guid.NewGuid(), "appearance.json")));
        var (window, surface, clock) = Create(appearance);
        try
        {
            Control overlay;
            Border? scrim;
            Action close;
            if (kind <= 1)
            {
                surface.Navigate(FluentPage.Settings);
                Dispatcher.UIThread.RunJobs();
                if (kind == 0)
                {
                    surface.SettingsViewModel.UpdateDraft(surface.SettingsViewModel.Draft with { MaterialAcrylicStrength = .123 });
                    surface.Navigate(FluentPage.Library);
                    overlay = Field<FluentDialog>(surface.SettingsView, "_leaveDialog");
                    close = surface.SettingsView.CancelLeave;
                }
                else
                {
                    surface.SettingsViewModel.SelectedGroup = SettingsGroupId.Providers;
                    Dispatcher.UIThread.RunJobs();
                    Click(Named(surface.SettingsView, "添加 Provider Profile"));
                    overlay = Field<FluentDialog>(surface.SettingsView, "_confirmation");
                    close = surface.SettingsView.CancelConfirmation;
                }
                scrim = Field<Border>(surface.SettingsView, "_scrim");
            }
            else if (kind == 2)
            {
                surface.ShelfView.ShowNewBookDialog();
                overlay = Field<FluentDialog>(surface.ShelfView, "_dialog");
                scrim = Field<Border>(surface.ShelfView, "_dialogScrim");
                close = () => Click(Named(overlay, "取消"));
            }
            else
            {
                surface.ShelfView.OpenRecycleDrawer();
                var drawer = Field<Drawer>(surface.ShelfView, "_recycleDrawer");
                overlay = drawer;
                scrim = null;
                close = () => drawer.IsOpen = false;
            }
            Assert.True(overlay.IsVisible);
            Assert.Equal(0, overlay.Opacity);
            clock.Advance(100);
            Assert.Equal(new SplineEasing(.2, 0, 0, 1).Ease(.5), overlay.Opacity, 6);
            if (scrim is not null) Assert.InRange(scrim.Opacity, .000001, .999999);
            clock.Advance(60);
            if (scrim is not null) Assert.Equal(1, scrim.Opacity);
            clock.Advance(39);
            Assert.True(overlay.Opacity < 1);
            clock.Advance(1);
            Assert.Equal(1, overlay.Opacity);
            close();
            Assert.True(overlay.IsVisible);
            Assert.False(overlay.IsHitTestVisible);
            clock.Advance(80);
            Assert.Equal(1 - new SplineEasing(.4, 0, 1, 1).Ease(.5), overlay.Opacity, 6);
            clock.Advance(79);
            Assert.True(overlay.IsVisible);
            clock.Advance(1);
            Assert.False(overlay.IsVisible);
            Assert.Equal(0, overlay.Opacity);
            if (scrim is not null) Assert.False(scrim.IsVisible);
        }
        finally { window.Close(); }
    }

    private static void Pump(int milliseconds)
    {
        var watch = Stopwatch.StartNew();
        do
        {
            AvaloniaHeadlessPlatform.ForceRenderTimerTick();
            Dispatcher.UIThread.RunJobs();
            Thread.Sleep(2);
        } while (watch.ElapsedMilliseconds < milliseconds);
    }

    private static Color Background(Button button) => Assert.IsAssignableFrom<ISolidColorBrush>(button.Background).Color;

    internal static void Hover(Window window, Button button, bool animated)
    {
        if (animated) Assert.NotNull(button.Transitions);
        else Assert.Null(button.Transitions);
        var clock = new HoverClock();
        // Avalonia's transition clock is internal; replace only its pulse source, retaining the real
        // BrushTransition interpolator and native pointer/style change under test.
        typeof(Animatable).GetProperty("Clock", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(button, clock.Value);
        window.MouseMove(new Point(1278, 898), RawInputModifiers.None);
        clock.Advance(0);
        clock.Advance(120);
        var from = Background(button);
        var point = button.TranslatePoint(new Point(8, button.Bounds.Height / 2), window)!.Value;
        window.MouseMove(point, RawInputModifiers.None);
        Assert.True(button.IsPointerOver, $"button={button.Content}; bounds={button.Bounds}; point={point}; hit={window.InputHitTest(point)}; visible={button.IsEffectivelyVisible}; enabled={button.IsEffectivelyEnabled}");
        Dispatcher.UIThread.RunJobs();
        clock.Advance(0);
        clock.Advance(30);
        var middle = Background(button);
        clock.Advance(89);
        if (animated) Assert.NotEqual(Background(button), from);
        clock.Advance(1);
        var to = Background(button);
        Assert.NotEqual(from, to); // actual hover colour, not the mere presence of a transition
        if (animated)
        {
            Assert.NotEqual(from, middle);
            Assert.NotEqual(to, middle);
            var transition = Assert.Single(button.Transitions!.OfType<BrushTransition>());
            Assert.InRange(Math.Abs(new SplineEasing(.4, 0, .2, 1).Ease(.5) - Assert.IsType<SplineEasing>(transition.Easing).Ease(.5)), 0, .0001);
            var eased = new SplineEasing(.4, 0, .2, 1).Ease(.25);
            Assert.InRange(Math.Abs(middle.R - (from.R + (to.R - from.R) * eased)), 0, 1);
            Assert.InRange(Math.Abs(middle.G - (from.G + (to.G - from.G) * eased)), 0, 1);
            Assert.InRange(Math.Abs(middle.B - (from.B + (to.B - from.B) * eased)), 0, 1);
        }
        else Assert.Equal(to, middle);
    }

    private sealed class HoverClock
    {
        private static readonly Type ClockType = typeof(Animatable).Assembly.GetType("Avalonia.Animation.ClockBase")!;
        public object Value { get; } = Activator.CreateInstance(ClockType, nonPublic: true)!;
        private TimeSpan _now;
        public void Advance(double milliseconds)
        {
            _now += TimeSpan.FromMilliseconds(milliseconds);
            ClockType.GetMethod("Pulse", BindingFlags.Instance | BindingFlags.NonPublic)!.Invoke(Value, [_now]);
        }
    }

    [AvaloniaFact]
    public void R2002_RebuildHover_CategorySwitch_RebuildAndPress_KeepColourAndScaleInSync()
    {
        using var theme = new DesignSystemThemeManager(Application.Current!);
        Assert.True(theme.Initialize(), theme.LastError);
        var (window, surface, clock) = Create();
        try
        {
            surface.Navigate(FluentPage.Settings);
            surface.SettingsViewModel.SelectedGroup = SettingsGroupId.Providers;
            Dispatcher.UIThread.RunJobs();
            var provider = Named(surface.SettingsView, "添加 Provider Profile");
            Hover(window, provider, animated: true);
            provider.Focus();
            window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            clock.Advance(45);
            Assert.InRange(Assert.IsType<ScaleTransform>(provider.RenderTransform).ScaleX, .980001, .999999);
            Motion(surface, MotionMode.Full, MotionCategories.Navigation);
            Assert.Null(provider.Transitions);
            Assert.Equal(1, Assert.IsType<ScaleTransform>(provider.RenderTransform).ScaleX);
            surface.SettingsView.Focusable = true;
            surface.SettingsView.Focus();
            window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
            surface.SettingsView.CancelConfirmation();
            clock.Advance(160);
            surface.SettingsViewModel.SelectedGroup = SettingsGroupId.Backup;
            Dispatcher.UIThread.RunJobs();
            var backup = Named(surface.SettingsView, "创建手动备份");
            Hover(window, backup, animated: false);
            backup.Focus();
            window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            clock.Advance(90);
            Assert.Equal(1, Assert.IsType<ScaleTransform>(backup.RenderTransform).ScaleX);
            surface.SettingsView.Focusable = true;
            surface.SettingsView.Focus();
            window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
            surface.Navigate(FluentPage.Library); // cached settings tree receives the new configuration
            Motion(surface);
            surface.SettingsViewModel.SelectedGroup = SettingsGroupId.Providers;
            surface.Navigate(FluentPage.Settings);
            Dispatcher.UIThread.RunJobs();
            var rebuilt = Named(surface.SettingsView, "添加 Provider Profile");
            Assert.NotSame(provider, rebuilt);
            Hover(window, rebuilt, animated: true);
            rebuilt.Focus();
            window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            clock.Advance(90);
            Assert.Equal(.98, Assert.IsType<ScaleTransform>(rebuilt.RenderTransform).ScaleX);
            surface.SettingsView.Focusable = true;
            surface.SettingsView.Focus();
            window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(0)] // press without movement
    [InlineData(1)] // release without movement
    [InlineData(2)] // wheel
    [InlineData(3)] // key consumed by shell tunnel handler (Ctrl+K)
    public void R2003_RealInput_ResetsTwoSecondDeadline_AndDetachStopsTimer(int input)
    {
        var (window, surface, clock) = Create();
        try
        {
            surface.Navigate(FluentPage.Reader);
            Dispatcher.UIThread.RunJobs();
            var reader = surface.ReaderView;
            var button = Named(reader, "切换单页或双页");
            var point = button.TranslatePoint(new Point(4, 4), window)!.Value;
            window.MouseMove(point, RawInputModifiers.None);
            if (input == 1) window.MouseDown(point, MouseButton.Left, RawInputModifiers.None);
            button.Focus();
            clock.Advance(1500);
            switch (input)
            {
                case 0: window.MouseDown(point, MouseButton.Left, RawInputModifiers.None); Assert.True(button.IsPressed); break;
                case 1: window.MouseUp(point, MouseButton.Left, RawInputModifiers.None); Assert.True(surface.ReaderViewModel.DoublePage); break;
                case 2: window.MouseWheel(point, new Vector(0, -1), RawInputModifiers.None); break;
                case 3:
                    window.KeyPressQwerty(PhysicalKey.K, RawInputModifiers.Control);
                    window.KeyReleaseQwerty(PhysicalKey.K, RawInputModifiers.Control);
                    Assert.True(surface.FindControl<Border>("FluentModalHost")!.IsVisible);
                    break;
            }
            Assert.Equal(TimeSpan.FromMilliseconds(3500), reader.IdleDeadline);
            clock.Advance(500);
            reader.CheckIdleDeadline();
            Assert.True(surface.ReaderViewModel.AreToolBarsVisible);
            clock.Advance(1499);
            reader.CheckIdleDeadline();
            Assert.True(surface.ReaderViewModel.AreToolBarsVisible);
            clock.Advance(1);
            reader.CheckIdleDeadline();
            Assert.False(surface.ReaderViewModel.AreToolBarsVisible);
            clock.Advance(160);
            Assert.False(reader.TopBar.IsVisible);
            reader.NotifyInteraction();
            Assert.True(reader.IdleTimerEnabled);
            window.Content = null;
            Assert.False(reader.IdleTimerEnabled);
            Assert.Null(reader.IdleDeadline);
            clock.Advance(3000);
            reader.CheckIdleDeadline();
            Assert.True(surface.ReaderViewModel.AreToolBarsVisible);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public async Task R2003_RealCenterPressAndRelease_KeepTapToggleHidden()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        var png = Convert.FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==");
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData("book-1", "Sample", "chapter-key", "Chapter", "fit-page",
            [new ReaderPageData("page-1", 0, 1, 1, _ => Task.FromResult<byte[]?>(png))]);
        var (window, surface, clock) = Create(host: host);
        try
        {
            surface.Navigate(FluentPage.Reader);
            await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            surface.ReaderViewModel.ToggleSideRail();
            var page = surface.ReaderView.PageSurface;
            page.Height = 400;
            Dispatcher.UIThread.RunJobs();
            window.UpdateLayout();
            Pump(300); // settle the page-host entrance before checking native hit-testing
            var point = page.TranslatePoint(new Point(page.Bounds.Width / 2, page.Bounds.Height / 2), window)!.Value;
            window.MouseMove(point, RawInputModifiers.None);
            Assert.True(window.InputHitTest(point) is Visual hit && (ReferenceEquals(hit, page) || hit.GetVisualAncestors().Contains(page)),
                $"bounds={page.Bounds}; point={point}; hit={window.InputHitTest(point)}");
            window.MouseDown(point, MouseButton.Left, RawInputModifiers.None);
            Assert.False(surface.ReaderViewModel.AreToolBarsVisible);
            window.MouseUp(point, MouseButton.Left, RawInputModifiers.None);
            Assert.False(surface.ReaderViewModel.AreToolBarsVisible);
            Assert.Null(surface.ReaderView.IdleDeadline);
            clock.Advance(160);
            Assert.False(surface.ReaderView.TopBar.IsVisible);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionMode.Full, MotionCategories.All)]
    [InlineData(MotionMode.Reduce, MotionCategories.All)]
    [InlineData(MotionMode.Full, MotionCategories.Feedback)]
    public async Task R3001_SamePointCenterClicks_ToggleFromPrePressState_ReleaseOnlyExtendsDeadline(
        MotionMode mode, MotionCategories categories)
    {
        var (window, surface, clock, point) = await CreateLoadedReader(mode, categories);
        try
        {
            var reader = surface.ReaderView;
            var vm = surface.ReaderViewModel;
            var instant = mode == MotionMode.Reduce || !categories.HasFlag(MotionCategories.Navigation);
            var changes = 0;
            vm.PropertyChanged += (_, args) => { if (args.PropertyName == nameof(vm.AreToolBarsVisible)) changes++; };
            Assert.True(vm.AreToolBarsVisible);
            var initialDeadline = reader.IdleDeadline!.Value;
            clock.Advance(1999);
            reader.CheckIdleDeadline();
            Assert.True(vm.AreToolBarsVisible);
            clock.Advance(1);
            Assert.Equal(initialDeadline, clock.Now);
            reader.CheckIdleDeadline(); // Start hidden through the actual idle path, never Poke.
            Assert.False(vm.AreToolBarsVisible);
            AssertHidden();
            Assert.Equal(1, changes);

            // One MouseMove above, then all presses/releases use exactly the same window coordinate.
            for (var click = 1; click <= 3; click++)
            {
                var expected = click != 2;
                AssertPageHit();
                var beforeChanges = changes;
                window.MouseDown(point, MouseButton.Left, RawInputModifiers.None);
                Assert.Equal(expected, vm.AreToolBarsVisible);
                Assert.Equal(beforeChanges + 1, changes); // Exactly one visibility change per press.
                if (expected)
                {
                    Assert.Equal(clock.Now + TimeSpan.FromSeconds(2), reader.IdleDeadline);
                    foreach (var bar in new[] { reader.TopBar, reader.BottomBar })
                    {
                        Assert.True(bar.IsVisible);
                        Assert.Equal(1, bar.Opacity);
                        Assert.True(bar.IsHitTestVisible);
                    }
                }
                else if (instant)
                {
                    // Check at MouseDown, before advancing even one animation frame.
                    Assert.False(reader.TopBar.IsVisible);
                    Assert.False(reader.BottomBar.IsVisible);
                    Assert.Equal(0, reader.TopBar.Opacity);
                    Assert.Equal(0, reader.BottomBar.Opacity);
                }
                clock.Advance(400); // Release must renew from release time, without toggling again.
                window.MouseUp(point, MouseButton.Left, RawInputModifiers.None);
                Assert.Equal(expected, vm.AreToolBarsVisible);
                Assert.Equal(beforeChanges + 1, changes);
                if (expected)
                    Assert.Equal(clock.Now + TimeSpan.FromSeconds(2), reader.IdleDeadline);
                else
                {
                    Assert.Null(reader.IdleDeadline);
                    Assert.False(reader.IdleTimerEnabled);
                    AssertHidden();
                }
            }

            // The last interaction is MouseUp, 400ms after MouseDown.
            var lastRelease = clock.Now;
            Assert.Equal(lastRelease + TimeSpan.FromSeconds(2), reader.IdleDeadline);
            clock.Advance(1600); // Old press deadline must not hide the bars.
            reader.CheckIdleDeadline();
            Assert.True(vm.AreToolBarsVisible);
            clock.Advance(399);
            reader.CheckIdleDeadline();
            Assert.True(vm.AreToolBarsVisible);
            clock.Advance(1);
            reader.CheckIdleDeadline();
            Assert.False(vm.AreToolBarsVisible);
            AssertHidden();

            AssertPageHit();
            window.MouseDown(point, MouseButton.Left, RawInputModifiers.None);
            window.MouseUp(point, MouseButton.Left, RawInputModifiers.None);
            Assert.True(vm.AreToolBarsVisible);
            Assert.True(reader.IdleTimerEnabled);
            window.Content = null;
            Assert.False(reader.IdleTimerEnabled);
            Assert.Null(reader.IdleDeadline);
            clock.Advance(3000);
            reader.CheckIdleDeadline();
            Assert.True(vm.AreToolBarsVisible);
            Assert.Equal(1, reader.TopBar.Opacity);

            void AssertPageHit()
            {
                window.UpdateLayout();
                Pump(20);
                var page = reader.PageSurface;
                Assert.True(window.InputHitTest(point) is Visual hit &&
                    (ReferenceEquals(hit, page) || hit.GetVisualAncestors().Contains(page)));
                var local = page.TranslatePoint(new Point(), window)!.Value;
                Assert.InRange((point.Y - local.Y) / page.Bounds.Height, .25, .75);
            }

            void AssertHidden()
            {
                foreach (var bar in new[] { reader.TopBar, reader.BottomBar })
                {
                    Assert.False(bar.IsHitTestVisible);
                    if (instant)
                    {
                        Assert.False(bar.IsVisible);
                        Assert.Equal(0, bar.Opacity);
                    }
                }
                clock.Advance(160);
                Assert.False(reader.TopBar.IsVisible);
                Assert.False(reader.BottomBar.IsVisible);
                Assert.Equal(0, reader.TopBar.Opacity);
                Assert.Equal(0, reader.BottomBar.Opacity);
            }
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionMode.Full, MotionCategories.All, 0)]
    [InlineData(MotionMode.Full, MotionCategories.All, 1)]
    [InlineData(MotionMode.Full, MotionCategories.All, 2)]
    [InlineData(MotionMode.Reduce, MotionCategories.All, 0)]
    [InlineData(MotionMode.Reduce, MotionCategories.All, 1)]
    [InlineData(MotionMode.Reduce, MotionCategories.All, 2)]
    [InlineData(MotionMode.Full, MotionCategories.Feedback, 0)]
    [InlineData(MotionMode.Full, MotionCategories.Feedback, 1)]
    [InlineData(MotionMode.Full, MotionCategories.Feedback, 2)]
    public async Task R3001_OtherControlPress_Wheel_AndShellHandledKey_WakeHiddenBarsAndRenewDeadline(
        MotionMode mode, MotionCategories categories, int input)
    {
        var (window, surface, clock, pagePoint) = await CreateLoadedReader(mode, categories);
        try
        {
            var reader = surface.ReaderView;
            var vm = surface.ReaderViewModel;
            Assert.False(vm.IsSideRailVisible);
            window.UpdateLayout();
            var restore = Named(reader, "显示浮动工具条");
            var point = input == 0 ? restore.TranslatePoint(new Point(restore.Bounds.Width / 2, restore.Bounds.Height / 2), window)!.Value : pagePoint;
            window.MouseMove(point, RawInputModifiers.None);
            reader.PageSurface.Focus();
            clock.Advance(2000);
            reader.CheckIdleDeadline();
            clock.Advance(160);
            Assert.False(vm.AreToolBarsVisible);
            Assert.False(reader.TopBar.IsVisible);
            Assert.Null(reader.IdleDeadline);
            window.UpdateLayout();
            Pump(20); // Publish the new layout to headless hit-testing before selecting the target.
            // Bars leaving the StackPanel shift the restore control; retarget without a waking MouseMove.
            if (input == 0) point = restore.TranslatePoint(new Point(restore.Bounds.Width / 2, restore.Bounds.Height / 2), window)!.Value;
            var target = input == 0 ? (Control)restore : reader.PageSurface;
            Assert.True(window.InputHitTest(point) is Visual hit &&
                (ReferenceEquals(hit, target) || hit.GetVisualAncestors().Contains(target)), $"target={target}; bounds={target.Bounds}; point={point}; hit={window.InputHitTest(point)}");

            switch (input)
            {
                case 0:
                    window.MouseDown(point, MouseButton.Left, RawInputModifiers.None);
                    Assert.True(restore.IsPressed);
                    break;
                case 1:
                    window.MouseWheel(point, new Vector(0, -1), RawInputModifiers.None);
                    break;
                case 2:
                    window.KeyPressQwerty(PhysicalKey.K, RawInputModifiers.Control);
                    window.KeyReleaseQwerty(PhysicalKey.K, RawInputModifiers.Control);
                    Assert.True(surface.FindControl<Border>("FluentModalHost")!.IsVisible);
                    break;
            }
            Assert.True(vm.AreToolBarsVisible);
            Assert.True(reader.TopBar.IsVisible);
            Assert.True(reader.BottomBar.IsVisible);
            Assert.Equal(1, reader.TopBar.Opacity);
            Assert.Equal(clock.Now + TimeSpan.FromSeconds(2), reader.IdleDeadline);
            if (input == 0)
            {
                Assert.False(vm.IsSideRailVisible);
                clock.Advance(400);
                window.UpdateLayout();
                Pump(20);
                point = restore.TranslatePoint(new Point(restore.Bounds.Width / 2, restore.Bounds.Height / 2), window)!.Value;
                window.MouseUp(point, MouseButton.Left, RawInputModifiers.None);
                Assert.True(vm.IsSideRailVisible); // The other control still receives its click.
                Assert.True(vm.AreToolBarsVisible);
                Assert.Equal(clock.Now + TimeSpan.FromSeconds(2), reader.IdleDeadline);
            }
            clock.Advance(1999);
            reader.CheckIdleDeadline();
            Assert.True(vm.AreToolBarsVisible);
            clock.Advance(1);
            reader.CheckIdleDeadline();
            Assert.False(vm.AreToolBarsVisible);
        }
        finally { window.Close(); }
    }

    private static async Task<(Window Window, FluentShellSurface Surface, ManualFluentMotionClock Clock, Point Point)>
        CreateLoadedReader(MotionMode mode, MotionCategories categories)
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        var png = Convert.FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==");
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData("book-1", "Sample", "chapter-key", "Chapter", "fit-page",
            [new ReaderPageData("page-1", 0, 1, 1, _ => Task.FromResult<byte[]?>(png))]);
        var (window, surface, clock) = Create(host: host);
        try
        {
            Motion(surface, mode, categories);
            surface.Navigate(FluentPage.Reader);
            await surface.ReaderView.LoadAsync("book-1", "chapter-key");
            surface.ReaderViewModel.IsSideRailVisible = false;
            var page = surface.ReaderView.PageSurface;
            page.Height = 400;
            Dispatcher.UIThread.RunJobs();
            window.UpdateLayout();
            Pump(300);
            var point = page.TranslatePoint(new Point(page.Bounds.Width / 2, page.Bounds.Height / 2), window)!.Value;
            window.MouseMove(point, RawInputModifiers.None);
            return (window, surface, clock, point);
        }
        catch { window.Close(); throw; }
    }

    [AvaloniaTheory]
    [InlineData(false)]
    [InlineData(true)]
    public void R2004_BackgroundEvent_DetachAndOptionalReattach_InvalidateQueuedCallback(bool reattach)
    {
        var root = Path.Combine(Path.GetTempPath(), "nm-r2-" + Guid.NewGuid());
        var appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(root, "appearance.json")));
        var (window, surface, _) = Create(appearance);
        try
        {
            var pageHost = surface.FindControl<ContentControl>("FluentPageHost")!;
            // Exercise the real Changed event after a write into this test's isolated temporary root.
            var worker = new Thread(() => appearance.SaveAsync(appearance.Settings with { MotionMode = MotionMode.Full })
                .GetAwaiter().GetResult());
            worker.Start(); worker.Join();
            window.Content = null;
            if (reattach)
            {
                window.Content = surface;
                // Reattach applies current auto settings. Assert effective timing as well as identity.
                var expected = MotionTimings.Resolve(new MotionResolver(new WindowsMotionPreferenceSource()).Resolve(appearance.Settings).Settings);
                Assert.Equal(expected.NavigationPageMilliseconds > 0, pageHost.Transitions is not null);
            }
            var beforePump = pageHost.Transitions;
            Dispatcher.UIThread.RunJobs();
            Assert.Same(beforePump, pageHost.Transitions);
            var subscribers = (Delegate?)typeof(AppearanceCoordinator).GetField("Changed", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(appearance);
            var motionSubscribers = subscribers?.GetInvocationList().Count(d => ReferenceEquals(d.Target, surface) && d.Method.Name == "OnAppearanceChangedForMotion") ?? 0;
            Assert.Equal(reattach ? 1 : 0, motionSubscribers);
            window.Content = null;
            window.Content = surface;
            window.Content = null;
            window.Content = surface;
            subscribers = (Delegate?)typeof(AppearanceCoordinator).GetField("Changed", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(appearance);
            Assert.Single(subscribers!.GetInvocationList(), d => ReferenceEquals(d.Target, surface) && d.Method.Name == "OnAppearanceChangedForMotion");
        }
        finally { window.Close(); if (Directory.Exists(root)) Directory.Delete(root, recursive: true); }
    }

    [AvaloniaFact]
    public void R2006_FluentFocusOffset_IsInheritedToken_AndCurrentKeepsZeroGap()
    {
        var (window, surface, _) = Create();
        try
        {
            var button = surface.FindControl<Button>("NavLibrary")!;
            Assert.Equal(1, FocusRing.GetOffset(button));
            var current = new TextBox();
            window.Content = current;
            Assert.Equal(0, FocusRing.GetOffset(current));
            window.Content = surface;
            Assert.Equal(1, FocusRing.GetOffset(button));
        }
        finally { window.Close(); }
    }
}
