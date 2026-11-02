using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Avalonia.Animation;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-5: the frozen motion table (design 02 §2) is consumed by the Fluent shell —
/// navigation page transitions run at 240ms in full mode, and reduce / category-off resolve to 0ms
/// (no transition). Runtime setting changes re-apply without recreating the content tree.
/// </summary>
public sealed class FluentMotionResidualTests : IDisposable
{
    private readonly string _root = Path.Combine(Path.GetTempPath(), $"nm-fea06-residual-motion-{Guid.NewGuid():N}");

    public FluentMotionResidualTests() => Directory.CreateDirectory(_root);

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    private AppearanceCoordinator CreateAppearance() =>
        new(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));

    [AvaloniaFact]
    public void MotionTimings_Table_MatchesFrozenDesignParameters()
    {
        var settings = new MotionSettings(MotionMode.Reduce, enabled: false, navigation: false, feedback: true, decorative: false);
        var reduce = MotionTimings.Resolve(settings);
        Assert.Equal(0d, reduce.NavigationPageMilliseconds);
        Assert.Equal(0d, reduce.NavigationTabMilliseconds);
        Assert.True(reduce.FeedbackColourOnly);
        Assert.Equal(0d, reduce.FeedbackPressedMilliseconds);
        Assert.False(reduce.DecorativeEnabled);
        Assert.False(reduce.HasMotion);

        var full = MotionTimings.Resolve(new MotionSettings(
            MotionMode.Full, enabled: true, navigation: true, feedback: true, decorative: true));
        Assert.Equal(MotionTimings.NavigationPageMilliseconds, full.NavigationPageMilliseconds);
        Assert.Equal(MotionTimings.NavigationTabMilliseconds, full.NavigationTabMilliseconds);
        Assert.Equal(MotionTimings.NavigationOverlayInMilliseconds, full.NavigationOverlayInMilliseconds);
        Assert.Equal(MotionTimings.NavigationOverlayOutMilliseconds, full.NavigationOverlayOutMilliseconds);
        Assert.Equal(MotionTimings.FeedbackHoverMilliseconds, full.FeedbackHoverMilliseconds);
        Assert.True(full.HasMotion);
    }

    [AvaloniaFact]
    public async Task ShellConsumesMotionTable_AndReappliesOnSettingsChange()
    {
        using var themeManager = new DesignSystemThemeManager(Avalonia.Application.Current!);
        themeManager.Initialize();
        var appearance = CreateAppearance();
        appearance.Reload();

        var options = AppOptions.Parse(Array.Empty<string>());
        var selection = FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null);
        var surface = new FluentShellSurface(options, selection, new FakeHostController(FakeHostController.ReadySnapshot()), appearance, themeManager);
        var pageHost = surface.FindControl<ContentControl>("FluentPageHost")!;
        Assert.NotNull(pageHost);

        await appearance.SaveAsync(AppearanceDefaults.Settings with { MotionMode = MotionMode.Full, MotionCategories = MotionCategories.All });
        Dispatcher.UIThread.RunJobs();
        var transitions = pageHost.Transitions;
        Assert.NotNull(transitions);
        var transition = Assert.IsType<DoubleTransition>(transitions!.Single());
        Assert.Equal(TimeSpan.FromMilliseconds(MotionTimings.NavigationPageMilliseconds), transition.Duration);

        await appearance.SaveAsync(AppearanceDefaults.Settings with { MotionMode = MotionMode.Reduce, MotionCategories = MotionCategories.All });
        Dispatcher.UIThread.RunJobs();
        Assert.Null(pageHost.Transitions);

        await appearance.SaveAsync(AppearanceDefaults.Settings with
        {
            MotionMode = MotionMode.Full,
            MotionCategories = MotionCategories.Feedback | MotionCategories.Decorative,
        });
        Dispatcher.UIThread.RunJobs();
        Assert.Null(pageHost.Transitions);
    }
}
