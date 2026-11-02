using System.Runtime.CompilerServices;
using Avalonia;
using Avalonia.Animation.Easings;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Media;

namespace NewManga.App.Views.Fluent;

/// <summary>Render-only feedback: layout, semantic visibility and command handling are unchanged.</summary>
internal static class FluentFeedbackMotion
{
    private static readonly ConditionalWeakTable<Control, Feedback> Items = new();

    public static void Configure(Control control, double duration, IFluentMotionClock clock, bool badge = false) =>
        Items.GetValue(control, target => new Feedback(target, badge)).Configure(duration, clock);

    private sealed class Feedback
    {
        private readonly Control _control;
        private readonly bool _badge;
        private readonly ScaleTransform _scale = new(1, 1);
        private readonly FluentFrameAnimation _animation;
        private readonly SplineEasing _easing = new(0.4, 0, 0.2, 1);
        private IFluentMotionClock _clock = FluentRenderClock.Instance;
        private double _duration;

        public Feedback(Control control, bool badge)
        {
            _control = control;
            _badge = badge;
            _animation = new FluentFrameAnimation(control);
            control.RenderTransformOrigin = RelativePoint.Center;
            control.RenderTransform = _scale;
            control.PropertyChanged += OnPropertyChanged;
        }

        public void Configure(double duration, IFluentMotionClock clock)
        {
            if (_duration == duration && ReferenceEquals(_clock, clock)) return;
            _duration = duration;
            _clock = clock;
            _animation.Cancel();
            SetScale(duration > 0 && _control is Button { IsPressed: true } ? 0.98 : 1);
            if (_badge) _control.Opacity = 1;
        }

        private void OnPropertyChanged(object? sender, AvaloniaPropertyChangedEventArgs args)
        {
            if (_badge && args.Property == Visual.IsVisibleProperty)
            {
                if (_control.IsVisible)
                {
                    _animation.Run(_clock, _duration, progress =>
                    {
                        var eased = _easing.Ease(progress);
                        _control.Opacity = eased;
                        SetScale(0.9 + 0.1 * eased);
                    });
                }
                else
                {
                    _animation.Finish();
                }
            }
            else if (!_badge && _control is Button button &&
                     (args.Property == Button.IsPressedProperty || args.Property == InputElement.IsEffectivelyEnabledProperty))
            {
                var from = _scale.ScaleX;
                var to = _duration > 0 && button.IsPressed && button.IsEffectivelyEnabled ? 0.98 : 1;
                _animation.Run(_clock, _duration, progress => SetScale(from + (to - from) * _easing.Ease(progress)));
            }
        }

        private void SetScale(double value) => _scale.ScaleX = _scale.ScaleY = value;
    }
}
