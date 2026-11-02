using System;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Text.Json;
using System.Threading.Tasks;
using Avalonia;
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
using NewManga.CoreClient;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Tests;

public sealed class FluentAnimationCompletionTests
{
    // FEA-06-RESIDUAL-2: decorative loops own their own frame source; these completion tests cover
    // navigation/feedback only so pending-frame assertions stay about the animation they exercise.
    private static void Motion(FluentShellSurface surface, MotionMode mode = MotionMode.Full,
        MotionCategories categories = MotionCategories.Navigation | MotionCategories.Feedback) =>
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
        Motion(surface);
        return (window, surface, clock);
    }

    private static Button Trigger(FluentShellSurface surface) => surface.FindControl<Button>("CommandPaletteButton")!;

    private static Border Open(FluentShellSurface surface)
    {
        Trigger(surface).Focus();
        Trigger(surface).RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
        Dispatcher.UIThread.RunJobs();
        var host = surface.FindControl<Border>("FluentModalHost")!;
        Assert.True(host.IsVisible);
        return host;
    }

    private static ScaleTransform Scale(Control control) => Assert.IsType<ScaleTransform>(control.RenderTransform);

    [AvaloniaFact]
    public void OverlayExit_KeepsHostUntil160ms_UsesEaseIn_AndReturnsFocusImmediately()
    {
        var (window, surface, clock) = Create();
        try
        {
            var host = Open(surface);
            var scrim = Assert.IsType<Border>(host.Child);
            // Settle entrance so this assertion measures exit independently of Avalonia transitions.
            scrim.Transitions = null;
            scrim.Opacity = 1;
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            Assert.True(Trigger(surface).IsFocused);
            Assert.True(host.IsVisible);
            Assert.False(host.IsHitTestVisible);
            Assert.Equal(1, scrim.Opacity);
            clock.Advance(80);
            Assert.Equal(1 - new SplineEasing(0.4, 0, 1, 1).Ease(0.5), scrim.Opacity, 6);
            clock.Advance(79);
            Assert.True(host.IsVisible);
            Assert.True(scrim.Opacity > 0);
            clock.Advance(1);
            Assert.Equal(0, scrim.Opacity);
            Assert.False(host.IsVisible);
            Assert.Null(host.Child);
            Assert.Equal(0, clock.PendingFrames);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionMode.Reduce, MotionCategories.All)]
    [InlineData(MotionMode.Full, MotionCategories.None)]
    public void DisabledMotion_ExitPressedAndBadge_AreInstant(MotionMode mode, MotionCategories categories)
    {
        var (window, surface, clock) = Create();
        try
        {
            Motion(surface, mode, categories);
            var button = surface.FindControl<Button>("NavLibrary")!;
            button.Focus();
            window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            Assert.True(button.IsPressed);
            Assert.Equal(1, Scale(button).ScaleX);
            window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
            surface.Navigate(FluentPage.Settings);
            Dispatcher.UIThread.RunJobs();
            surface.SettingsViewModel.UpdateDraft(surface.SettingsViewModel.Draft with { MaterialAcrylicStrength = 0.123 });
            var badge = surface.SettingsView.GetVisualDescendants().OfType<Control>()
                .Single(c => c.Classes.Contains("fluent-feedback-badge"));
            Assert.True(badge.IsVisible);
            Assert.Equal(1, badge.Opacity);
            Assert.Equal(1, Scale(badge).ScaleX);
            var host = Open(surface);
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            Assert.False(host.IsVisible);
            Assert.True(Trigger(surface).IsFocused);
            Assert.Equal(0, clock.PendingFrames);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(true)]
    [InlineData(false)]
    public void Pressed_RealInput_InterpolatesTo098At90ms_ThenReturnsToOne(bool keyboard)
    {
        var (window, surface, clock) = Create();
        try
        {
            var button = surface.FindControl<Button>("NavLibrary")!;
            var bounds = button.Bounds;
            button.Focus();
            var point = button.TranslatePoint(new Point(3, 3), window)!.Value;
            if (keyboard) window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            else window.MouseDown(point, MouseButton.Left, RawInputModifiers.None);
            Assert.True(button.IsPressed);
            Assert.Equal(1, Scale(button).ScaleX);
            clock.Advance(45);
            Assert.InRange(Scale(button).ScaleX, 0.980001, 0.999999);
            Assert.Equal(bounds, button.Bounds);
            clock.Advance(44);
            Assert.True(Scale(button).ScaleX > 0.98);
            clock.Advance(1);
            Assert.Equal(0.98, Scale(button).ScaleX);
            Assert.Equal(0.98, Scale(button).ScaleY);
            if (keyboard) window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
            else window.MouseUp(point, MouseButton.Left, RawInputModifiers.None);
            Assert.False(button.IsPressed);
            clock.Advance(90);
            Assert.Equal(1, Scale(button).ScaleX);
            Assert.Equal(0, clock.PendingFrames);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(true)]
    [InlineData(false)]
    public void Badge_AppearsWithOpacityAndScale_ForExactly150ms(bool settings)
    {
        var (window, surface, clock) = Create();
        try
        {
            surface.Navigate(settings ? FluentPage.Settings : FluentPage.Workbench);
            Dispatcher.UIThread.RunJobs();
            var badge = settings
                ? surface.SettingsView.GetVisualDescendants().OfType<Control>()
                    .Single(c => c.Classes.Contains("fluent-feedback-badge"))
                : surface.WorkbenchView.DirtyDot;
            if (settings)
                surface.SettingsViewModel.UpdateDraft(surface.SettingsViewModel.Draft with { MaterialAcrylicStrength = 0.123 });
            else
                badge.IsVisible = true;
            Assert.True(badge.IsVisible);
            Assert.Equal(0, badge.Opacity);
            Assert.Equal(0.9, Scale(badge).ScaleX);
            window.UpdateLayout();
            var bounds = badge.Bounds;
            clock.Advance(75);
            Assert.InRange(badge.Opacity, 0.000001, 0.999999);
            Assert.InRange(Scale(badge).ScaleX, 0.900001, 0.999999);
            window.UpdateLayout();
            Assert.Equal(bounds, badge.Bounds); // Render-only changes never animate layout.
            clock.Advance(74);
            Assert.True(badge.Opacity < 1);
            Assert.True(Scale(badge).ScaleX < 1);
            clock.Advance(1);
            Assert.Equal(1, badge.Opacity);
            Assert.Equal(1, Scale(badge).ScaleX);
            badge.IsVisible = false;
            badge.IsVisible = true;
            Assert.Equal(0, badge.Opacity); // Reappearance restarts, rather than a one-time setup effect.
            clock.Advance(150);
            Assert.Equal(1, badge.Opacity);
            Assert.Equal(0, clock.PendingFrames);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public async Task WorkbenchDraftEdit_BadgeSurvivesRender_AndNewButtonsReceivePressedMotion()
    {
        using var theme = new DesignSystemThemeManager(Application.Current!);
        Assert.True(theme.Initialize(NewManga.DesignSystem.Theming.AppearanceMode.Light), theme.LastError);
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        host.ChapterPagesByChapter["chapter-key"] = [new ChapterPageSummary("page-1", "one.png", 0)];
        host.RegionsByPage["page-1"] = new RegionPageProjection(
            [new RegionSummary("region-1", "speech", "skip", "detect", 1,
                new RegionGeometrySummary(0.1, 0.1, 0.3, 0.2, []))], new RegionPageSize(100, 100));
        host.RevisionsByRegion["region-1"] = new RegionRevisionHistory("region-1", 1,
            [new RegionRevisionSummary("rev-1", 1, "detect", "reviewed", false,
                null, "2026-11-02T00:00:00Z", "speech", "skip", true)]);
        var draft = new Draft("draft-1", "session-1", "page-1", "region-1", "rev-1", 1, 1,
            JsonSerializer.SerializeToElement(new { text = "draft text" }), null, "2026-11-02T00:00:00Z", "open");
        host.ScriptedDrafts = [draft];
        host.DraftLeasesByPageRegion["page-1|region-1"] = new DraftLease(draft, true,
            new EditToken("token-1", "draft-1", 1, "session-1", "2026-11-02T00:00:00Z", "2026-11-03T00:00:00Z"));
        var clock = new ManualFluentMotionClock();
        var surface = new FluentShellSurface(host: host) { MotionClock = clock };
        var window = new Window { Width = 1280, Height = 900, Content = surface };
        try
        {
            window.Show();
            Motion(surface);
            surface.Navigate(FluentPage.Workbench);
            await surface.WorkbenchView.LoadAsync("chapter-key");
            Dispatcher.UIThread.RunJobs();
            var badge = surface.WorkbenchView.DirtyDot;
            surface.WorkbenchViewModel.DraftText = "changed";
            Dispatcher.UIThread.RunJobs();
            Assert.True(badge.IsVisible);
            Assert.Equal(0, badge.Opacity);
            clock.Advance(75);
            Assert.InRange(badge.Opacity, 0.000001, 0.999999);
            // Another dirty edit rerenders the inspector; the same badge must finish its original run.
            surface.WorkbenchViewModel.DraftText = "changed again";
            clock.Advance(74);
            Assert.True(badge.Opacity < 1);
            clock.Advance(1);
            Assert.Equal(1, badge.Opacity);
            Assert.Equal(1, Scale(badge).ScaleX);

            var button = surface.WorkbenchView.GetVisualDescendants().OfType<Button>()
                .Single(b => AutomationProperties.GetName(b) == "开启草稿");
            FluentR2ReworkTests.Hover(window, button, animated: true);
            button.Focus();
            window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            Assert.True(button.IsPressed);
            clock.Advance(89);
            Assert.True(Scale(button).ScaleX > 0.98);
            clock.Advance(1);
            Assert.Equal(0.98, Scale(button).ScaleX);
            Motion(surface, MotionMode.Reduce);
            Assert.Equal(1, Scale(button).ScaleX);
            // Release without invoking the command under test: focus moves before the key is released.
            surface.WorkbenchView.Focusable = true;
            surface.WorkbenchView.Focus();
            window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
            surface.WorkbenchViewModel.DraftText = "rebuild with feedback disabled";
            Dispatcher.UIThread.RunJobs();
            var reducedButton = surface.WorkbenchView.GetVisualDescendants().OfType<Button>()
                .Single(b => AutomationProperties.GetName(b) == "开启草稿");
            Assert.NotSame(button, reducedButton);
            FluentR2ReworkTests.Hover(window, reducedButton, animated: false);
            Motion(surface);
            surface.WorkbenchViewModel.DraftText = "rebuild with feedback restored";
            Dispatcher.UIThread.RunJobs();
            var restoredButton = surface.WorkbenchView.GetVisualDescendants().OfType<Button>()
                .Single(b => AutomationProperties.GetName(b) == "开启草稿");
            Assert.NotSame(reducedButton, restoredButton);
            FluentR2ReworkTests.Hover(window, restoredButton, animated: true);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionMode.Reduce, MotionCategories.All)]
    [InlineData(MotionMode.Full, MotionCategories.None)]
    public void RuntimeReduce_CompletesExitAndFeedback_AndIgnoresQueuedFrames(MotionMode mode, MotionCategories categories)
    {
        var (window, surface, clock) = Create();
        try
        {
            var host = Open(surface);
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            clock.Advance(50);
            Assert.True(host.IsVisible);
            Motion(surface, mode, categories);
            Assert.False(host.IsVisible);
            var button = surface.FindControl<Button>("NavLibrary")!;
            Motion(surface);
            button.Focus();
            window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            surface.WorkbenchView.DirtyDot.IsVisible = true;
            clock.Advance(45);
            Assert.True(Scale(button).ScaleX < 1);
            Motion(surface, mode, categories);
            Assert.Equal(1, Scale(button).ScaleX);
            Assert.Equal(1, surface.WorkbenchView.DirtyDot.Opacity);
            window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
            clock.Advance(500);
            Assert.Equal(1, Scale(button).ScaleX);
            Assert.False(host.IsVisible);
            Assert.Equal(0, clock.PendingFrames);
        }
        finally { window.Close(); }
    }

    [AvaloniaTheory]
    [InlineData(MotionCategories.Navigation, true, false)]
    [InlineData(MotionCategories.Feedback, false, true)]
    public void CategorySwitches_GateNavigationAndFeedbackIndependently(MotionCategories categories, bool navigation, bool feedback)
    {
        var (window, surface, clock) = Create();
        try
        {
            Motion(surface, MotionMode.Full, categories);
            surface.Navigate(FluentPage.Workbench);
            Dispatcher.UIThread.RunJobs();
            var badge = surface.WorkbenchView.DirtyDot;
            badge.IsVisible = true;
            Assert.Equal(feedback ? 0 : 1, badge.Opacity);
            Assert.Equal(feedback ? 0.9 : 1, Scale(badge).ScaleX);
            var button = surface.FindControl<Button>("NavWorkbench")!;
            button.Focus();
            window.KeyPressQwerty(PhysicalKey.Space, RawInputModifiers.None);
            clock.Advance(90);
            Assert.Equal(feedback ? 0.98 : 1, Scale(button).ScaleX);
            window.KeyReleaseQwerty(PhysicalKey.Space, RawInputModifiers.None);
            clock.Advance(90);
            Assert.Equal(1, badge.Opacity);
            var host = Open(surface);
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            Assert.Equal(navigation, host.IsVisible);
            Assert.True(Trigger(surface).IsFocused);
            clock.Advance(159);
            Assert.Equal(navigation, host.IsVisible);
            clock.Advance(1);
            Assert.False(host.IsVisible);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void DetachedCachedPage_FinishesBadge_AndQueuedFramesStop()
    {
        var (window, surface, clock) = Create();
        try
        {
            surface.Navigate(FluentPage.Workbench);
            Dispatcher.UIThread.RunJobs();
            var badge = surface.WorkbenchView.DirtyDot;
            badge.IsVisible = true;
            clock.Advance(50);
            Assert.InRange(badge.Opacity, 0.000001, 0.999999);
            surface.Navigate(FluentPage.Library);
            Assert.Equal(1, badge.Opacity);
            Assert.Equal(1, Scale(badge).ScaleX);
            clock.Advance(500);
            Assert.Equal(0, clock.PendingFrames);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ReopenDuringExit_OldCompletionCannotHideNewOverlay()
    {
        var (window, surface, clock) = Create();
        try
        {
            var host = Open(surface);
            var old = host.Child;
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            clock.Advance(80);
            Open(surface);
            Assert.NotSame(old, host.Child);
            clock.Advance(160);
            Assert.True(host.IsVisible);
            Assert.True(host.IsHitTestVisible);
            Assert.IsType<TextBox>(window.FocusManager!.GetFocusedElement());
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ExitingOverlay_DoesNotDelaySecondEscapeReaderBack()
    {
        var (window, surface, clock) = Create();
        try
        {
            surface.Navigate(FluentPage.Reader);
            var host = Open(surface);
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            Assert.Equal(FluentPage.Reader, surface.CurrentPage);
            Assert.True(host.IsVisible);
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            Assert.Equal(FluentPage.Library, surface.CurrentPage);
            clock.Advance(160);
            Assert.False(host.IsVisible);
        }
        finally { window.Close(); }
    }

    [AvaloniaFact]
    public void ProductionRenderClock_ForceRenderTicks_ActuallyCompletesExitAfter160ms()
    {
        var (window, surface, _) = Create();
        try
        {
            surface.MotionClock = FluentRenderClock.Instance;
            var host = Open(surface);
            var scrim = Assert.IsType<Border>(host.Child);
            scrim.Transitions = null;
            scrim.Opacity = 1;
            var watch = Stopwatch.StartNew();
            long? hiddenAt = null;
            host.PropertyChanged += (_, e) =>
            {
                if (e.Property == Visual.IsVisibleProperty && !host.IsVisible) hiddenAt = watch.ElapsedMilliseconds;
            };
            surface.HandleKeyForTest(Key.Escape, KeyModifiers.None);
            Assert.True(Trigger(surface).IsFocused);
            Assert.True(host.IsVisible);
            while (host.IsVisible && watch.ElapsedMilliseconds < 3000)
            {
                AvaloniaHeadlessPlatform.ForceRenderTimerTick();
                Dispatcher.UIThread.RunJobs();
                Thread.Sleep(5);
            }
            Assert.False(host.IsVisible);
            Assert.NotNull(hiddenAt);
            Assert.True(hiddenAt >= 160, $"host hidden at {hiddenAt}ms");
            Assert.Equal(0, scrim.Opacity);
        }
        finally { window.Close(); }
    }
}
