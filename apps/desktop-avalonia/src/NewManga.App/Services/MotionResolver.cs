using System;
using System.Collections.Generic;
using NewManga.Appearance;

namespace NewManga.App.Services;

/// <summary>
/// C-03 §2.3: resolves <c>motion.mode</c> plus <c>motion.categories</c> into the
/// effective motion settings the shell applies. Rules:
/// <list type="bullet">
/// <item><c>auto</c> reads <see cref="IMotionPreferenceSource"/>; a null/throw degrades to <c>full</c> with a warning.</item>
/// <item><c>full</c> / <c>reduce</c> are explicit overrides (no platform read).</item>
/// <item><c>reduce</c> zeroes every duration (design 02 criterion ①) and disables emphasis (②), keeps feedback transitions at 0ms feedback color only (③).</item>
/// <item><c>motion.categories=off</c> (None) forces 0ms for every category (④).</item>
/// <item>Criterion ⑤: no motion is started while reduce is effective, not even a short fade.</item>
/// </list>
/// </summary>
public sealed class MotionSettings
{
    public MotionSettings(MotionMode effectiveMode, bool enabled, bool navigation, bool feedback, bool decorative)
    {
        EffectiveMode = effectiveMode;
        Enabled = enabled;
        Feedback = feedback;
        Navigation = navigation;
        Decorative = decorative;
    }

    /// <summary>The mode actually applied (never <see cref="MotionMode.Auto"/>).</summary>
    public MotionMode EffectiveMode { get; }

    /// <summary>False when every category is disabled (durations are zero).</summary>
    public bool Enabled { get; }

    public bool Feedback { get; }

    public bool Navigation { get; }

    public bool Decorative { get; }

    /// <summary>True when a given category animates; false means the consumer must use 0ms.</summary>
    public bool IsEnabled(MotionCategories category) => Enabled && category switch
    {
        MotionCategories.Feedback => Feedback,
        MotionCategories.Navigation => Navigation,
        MotionCategories.Decorative => Decorative,
        _ => false,
    };
}

/// <summary>Result of resolving the persisted settings against the platform.</summary>
public sealed record MotionResolution(MotionSettings Settings, IReadOnlyList<string> Warnings);

/// <summary>C-03 §2.3 resolver; pure and injectable so the platform read can be faked.</summary>
public sealed class MotionResolver
{
    private readonly IMotionPreferenceSource _source;

    public MotionResolver(IMotionPreferenceSource? source = null)
    {
        _source = source ?? NullMotionPreferenceSource.Instance;
    }

    public MotionResolution Resolve(AppearanceSettings settings)
    {
        ArgumentNullException.ThrowIfNull(settings);

        var warnings = new List<string>();
        var mode = settings.MotionMode switch
        {
            MotionMode.Reduce => MotionMode.Reduce,
            MotionMode.Full => MotionMode.Full,
            _ => ReadPlatform(warnings),
        };

        var reduce = mode == MotionMode.Reduce;
        var categories = settings.MotionCategories;
        // reduce zeroes durations (①) and disables emphasis (②); feedback stays as a
        // colour transition measured at 0ms (③); no motion at all under ⑤.
        // ③: feedback keeps its colour transition at 0ms under reduce, so the category flag
        // stays set while Enabled=false zeroes the duration.
        var feedback = categories.HasFlag(MotionCategories.Feedback);
        var navigation = !reduce && categories.HasFlag(MotionCategories.Navigation);
        var decorative = !reduce && categories.HasFlag(MotionCategories.Decorative);
        var enabled = !reduce && (feedback || navigation || decorative);

        return new MotionResolution(
            new MotionSettings(mode, enabled, navigation, feedback, decorative),
            warnings);
    }

    private MotionMode ReadPlatform(List<string> warnings)
    {
        try
        {
            var value = _source.Read();
            if (value is null or MotionMode.Auto)
            {
                warnings.Add("platform motion preference unavailable; degrading to full");
                return MotionMode.Full;
            }

            return value.Value;
        }
        catch (Exception)
        {
            warnings.Add("platform motion preference read failed; degrading to full");
            return MotionMode.Full;
        }
    }
}
