using Avalonia;
using Avalonia.Animation.Easings;
using Avalonia.Controls;

namespace NewManga.App.Views.Fluent;

/// <summary>Logical close is immediate; the visual remains until its finite opacity exit completes.</summary>
internal sealed class FluentVisibilityMotion
{
    private readonly Control _target;
    private readonly FluentFrameAnimation _animation;
    private IFluentMotionClock _clock = FluentRenderClock.Instance;
    private double _enter;
    private double _exit;
    private bool _shown;

    public FluentVisibilityMotion(Control target, StyledProperty<bool>? openProperty = null)
    {
        _target = target;
        _shown = target.IsVisible;
        _animation = new FluentFrameAnimation(target);
        if (openProperty is not null)
            target.PropertyChanged += (_, e) =>
            {
                if (e.Property == openProperty) SetVisible(target.GetValue(openProperty));
            };
    }

    public void Configure(double enter, double exit, IFluentMotionClock clock)
    {
        _clock = clock;
        _enter = enter;
        _exit = exit;
        if ((_shown ? enter : exit) == 0) _animation.Finish();
    }

    public void SetVisible(bool shown)
    {
        if (_shown == shown)
        {
            // IsOpen's native handler can set IsVisible during an in-flight exit.
            if (shown) _target.IsVisible = true;
            return;
        }
        _shown = shown;
        _animation.Cancel();
        _target.Transitions = null;
        // Native IsOpen may already have made the target visible. New entrances always start at 0.
        var from = shown ? 0 : _target.Opacity;
        _target.IsVisible = true;
        _target.IsHitTestVisible = shown;
        var to = shown ? 1d : 0d;
        var easing = shown ? new SplineEasing(0.2, 0, 0, 1) : new SplineEasing(0.4, 0, 1, 1);
        _animation.Run(_clock, shown ? _enter : _exit,
            p => _target.Opacity = from + (to - from) * easing.Ease(p),
            () => _target.IsVisible = _shown);
    }
}
