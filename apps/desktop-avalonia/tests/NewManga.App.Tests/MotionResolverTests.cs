using System;
using System.Collections.Generic;
using NewManga.App.Services;
using NewManga.Appearance;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// C-03 §2.3 / FEA-06-PREREQ-1 AC4: motion resolution, platform degradation and the
/// design-02 criterion map (①–⑤).
/// </summary>
public sealed class MotionResolverTests
{
    private sealed class FixedSource : IMotionPreferenceSource
    {
        private readonly MotionMode? _value;

        public FixedSource(MotionMode? value) => _value = value;

        public MotionMode? Read() => _value;
    }

    private sealed class ThrowingSource : IMotionPreferenceSource
    {
        public MotionMode? Read() => throw new InvalidOperationException("platform failure");
    }

    private static MotionResolution Resolve(MotionMode mode, MotionCategories categories, IMotionPreferenceSource? source = null) =>
        new MotionResolver(source).Resolve(new AppearanceSettings
        {
            MotionMode = mode,
            MotionCategories = categories,
        });

    [Fact]
    public void Auto_UsesThePlatformSource()
    {
        var result = Resolve(MotionMode.Auto, MotionCategories.All, new FixedSource(MotionMode.Reduce));

        Assert.Equal(MotionMode.Reduce, result.Settings.EffectiveMode);
        Assert.Empty(result.Warnings);
        Assert.True(result.Settings.Feedback); // ③ the category flag stays; Enabled=false zeroes it
        Assert.False(result.Settings.IsEnabled(MotionCategories.Navigation));
        Assert.False(result.Settings.IsEnabled(MotionCategories.Decorative));
    }

    [Fact]
    public void Auto_WithUnavailableSource_DegradesToFull_WithWarning()
    {
        var result = Resolve(MotionMode.Auto, MotionCategories.All, new FixedSource(null));

        Assert.Equal(MotionMode.Full, result.Settings.EffectiveMode);
        Assert.NotEmpty(result.Warnings);
        Assert.True(result.Settings.Enabled);
    }

    [Fact]
    public void Auto_WithThrowingSource_DegradesToFull_WithWarning()
    {
        var result = Resolve(MotionMode.Auto, MotionCategories.All, new ThrowingSource());

        Assert.Equal(MotionMode.Full, result.Settings.EffectiveMode);
        Assert.NotEmpty(result.Warnings);
    }

    [Fact]
    public void ExplicitFull_DoesNotReadThePlatform()
    {
        var result = Resolve(MotionMode.Full, MotionCategories.All, new ThrowingSource());

        Assert.Equal(MotionMode.Full, result.Settings.EffectiveMode);
        Assert.Empty(result.Warnings);
        Assert.True(result.Settings.IsEnabled(MotionCategories.Decorative));
    }

    [Fact]
    public void Reduce_ZeroesEveryDuration_AndDisablesAllCategories()
    {
        var result = Resolve(MotionMode.Reduce, MotionCategories.All, new FixedSource(MotionMode.Full));

        Assert.Equal(MotionMode.Reduce, result.Settings.EffectiveMode);
        Assert.False(result.Settings.Enabled); // ① 0ms everywhere, ⑤ no motion started
        Assert.False(result.Settings.IsEnabled(MotionCategories.Feedback));
        Assert.False(result.Settings.IsEnabled(MotionCategories.Navigation));
        Assert.False(result.Settings.IsEnabled(MotionCategories.Decorative));
    }

    [Fact]
    public void CategoriesOff_DisablesEveryCategory_UnderFull()
    {
        var result = Resolve(MotionMode.Full, MotionCategories.None);

        Assert.False(result.Settings.Enabled); // ④ categories=off → 0ms for all three
        Assert.False(result.Settings.Feedback);
        Assert.False(result.Settings.Navigation);
        Assert.False(result.Settings.Decorative);
    }

    [Fact]
    public void OnlyFeedbackCategory_KeepsFeedbackEnabled()
    {
        var result = Resolve(MotionMode.Full, MotionCategories.Feedback);

        Assert.True(result.Settings.Feedback);
        Assert.False(result.Settings.Navigation);
        Assert.False(result.Settings.Decorative);
        Assert.True(result.Settings.IsEnabled(MotionCategories.Feedback));
    }
}
