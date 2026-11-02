using System;
using System.Collections.Generic;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-RESIDUAL-1 I-5 (design `02-motion.md` §1–§3): exhaustive, table-driven matrix over
/// `auto/full/reduce` × category switches. The resolver owns the preference/platform rules; the frozen
/// `MotionTimings` table owns the numbers. Every cell asserts either the design value or the exact
/// escalation rule (reduce ⇒ 0ms, category off ⇒ that category 0ms, auto reads the platform, read
/// failure/`Auto` ⇒ full + warning).
/// </summary>
public sealed class MotionMatrixResidualTests
{
    private static MotionResolution Resolve(
        MotionMode mode,
        MotionCategories categories,
        IMotionPreferenceSource? source = null) =>
        new MotionResolver(source).Resolve(new AppearanceSettings
        {
            MotionMode = mode,
            MotionCategories = categories,
        });

    public static IEnumerable<object[]> FullAndReduceCells()
    {
        yield return [MotionMode.Full, MotionCategories.All];
        yield return [MotionMode.Full, MotionCategories.Navigation];
        yield return [MotionMode.Full, MotionCategories.Feedback];
        yield return [MotionMode.Full, MotionCategories.Decorative];
        yield return [MotionMode.Full, MotionCategories.None];
        yield return [MotionMode.Reduce, MotionCategories.All];
        yield return [MotionMode.Reduce, MotionCategories.Feedback];
        yield return [MotionMode.Reduce, MotionCategories.None];
    }

    [Theory]
    [MemberData(nameof(FullAndReduceCells))]
    public void FullAndReduce_match_the_frozen_parameter_table(MotionMode mode, MotionCategories categories)
    {
        var settings = Resolve(mode, categories).Settings;
        var timings = MotionTimings.Resolve(settings);
        var reduce = mode == MotionMode.Reduce;
        var navigation = !reduce && categories.HasFlag(MotionCategories.Navigation);
        var feedback = categories.HasFlag(MotionCategories.Feedback) && !reduce;
        var decorative = !reduce && categories.HasFlag(MotionCategories.Decorative);

        Assert.Equal(navigation ? 240d : 0d, timings.NavigationPageMilliseconds);
        Assert.Equal(navigation ? 180d : 0d, timings.NavigationTabMilliseconds);
        Assert.Equal(navigation ? 200d : 0d, timings.NavigationOverlayInMilliseconds);
        Assert.Equal(navigation ? 160d : 0d, timings.NavigationOverlayOutMilliseconds);
        Assert.Equal(feedback ? 120d : 0d, timings.FeedbackHoverMilliseconds);
        Assert.Equal(feedback ? 90d : 0d, timings.FeedbackPressedMilliseconds);
        Assert.Equal(feedback ? 150d : 0d, timings.FeedbackBadgeMilliseconds);
        Assert.Equal(decorative, timings.DecorativeEnabled);
        Assert.Equal(reduce && categories.HasFlag(MotionCategories.Feedback), timings.FeedbackColourOnly);
        Assert.Equal(reduce, timings.Reduced);
    }

    [Fact]
    public void Auto_follows_the_platform_and_full_never_reads_it()
    {
        var platformOn = Resolve(MotionMode.Auto, MotionCategories.All, new FixedSource(MotionMode.Full));
        Assert.Empty(platformOn.Warnings);
        Assert.Equal(MotionMode.Full, platformOn.Settings.EffectiveMode);
        Assert.True(platformOn.Settings.IsEnabled(MotionCategories.Navigation));

        var platformOff = Resolve(MotionMode.Auto, MotionCategories.All, new FixedSource(MotionMode.Reduce));
        Assert.Empty(platformOff.Warnings);
        Assert.Equal(MotionMode.Reduce, platformOff.Settings.EffectiveMode);
        Assert.False(platformOff.Settings.IsEnabled(MotionCategories.Navigation));

        // Explicit full must not consult the platform (source throws if read).
        var explicitFull = Resolve(MotionMode.Full, MotionCategories.All, new ThrowingSource());
        Assert.Empty(explicitFull.Warnings);
        Assert.Equal(MotionMode.Full, explicitFull.Settings.EffectiveMode);
        Assert.True(explicitFull.Settings.IsEnabled(MotionCategories.Decorative));
    }

    [Fact]
    public void Auto_read_failure_or_null_degrades_to_full_with_a_warning()
    {
        var unavailable = Resolve(MotionMode.Auto, MotionCategories.All, new FixedSource(null));
        Assert.Single(unavailable.Warnings);
        Assert.Equal(MotionMode.Full, unavailable.Settings.EffectiveMode);
        Assert.True(unavailable.Settings.IsEnabled(MotionCategories.Navigation));

        var failed = Resolve(MotionMode.Auto, MotionCategories.All, new ThrowingSource());
        Assert.Single(failed.Warnings);
        Assert.Equal(MotionMode.Full, failed.Settings.EffectiveMode);
        Assert.True(failed.Settings.IsEnabled(MotionCategories.Feedback));
    }

    [Fact]
    public void Reduced_category_off_keeps_feedback_colour_only_when_the_category_is_on()
    {
        var reduceAll = MotionTimings.Resolve(Resolve(MotionMode.Reduce, MotionCategories.All).Settings);
        Assert.True(reduceAll.FeedbackColourOnly);
        Assert.Equal(0d, reduceAll.FeedbackHoverMilliseconds);

        var reduceFeedbackOff = MotionTimings.Resolve(
            Resolve(MotionMode.Reduce, MotionCategories.Navigation | MotionCategories.Decorative).Settings);
        Assert.False(reduceFeedbackOff.FeedbackColourOnly);
        Assert.False(reduceFeedbackOff.HasMotion);
    }

    private sealed class FixedSource(MotionMode? value) : IMotionPreferenceSource
    {
        public MotionMode? Read() => value;
    }

    private sealed class ThrowingSource : IMotionPreferenceSource
    {
        public MotionMode? Read() => throw new InvalidOperationException("platform read failed");
    }
}
