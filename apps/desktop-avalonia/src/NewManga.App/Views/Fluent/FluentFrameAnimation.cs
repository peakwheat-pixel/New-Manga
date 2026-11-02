using System.Diagnostics;
using Avalonia.Controls;
using Avalonia.VisualTree;

namespace NewManga.App.Views.Fluent;

/// <summary>Only the frame source is replaceable in tests; interpolation and completion stay production code.</summary>
internal interface IFluentMotionClock
{
    TimeSpan Now { get; }
    void RequestFrame(Control target, Action callback);
}

internal sealed class FluentRenderClock : IFluentMotionClock
{
    public static FluentRenderClock Instance { get; } = new();
    public TimeSpan Now => TimeSpan.FromSeconds((double)Stopwatch.GetTimestamp() / Stopwatch.Frequency);

    public void RequestFrame(Control target, Action callback) =>
        TopLevel.GetTopLevel(target)?.RequestAnimationFrame(_ => callback());
}

/// <summary>A finite render-frame animation, with no dispatcher timer or background work.</summary>
internal sealed class FluentFrameAnimation
{
    private readonly Control _target;
    private Action<double>? _update;
    private Action? _completed;
    private int _generation;

    public FluentFrameAnimation(Control target)
    {
        _target = target;
        // A cached page must not retain a partially faded/scaled visual when reattached.
        target.DetachedFromVisualTree += (_, _) => Finish();
    }

    public void Run(IFluentMotionClock clock, double milliseconds, Action<double> update, Action? completed = null)
    {
        Cancel();
        _update = update;
        _completed = completed;
        if (milliseconds <= 0 || !_target.IsAttachedToVisualTree())
        {
            Finish();
            return;
        }

        var generation = _generation;
        var start = clock.Now;
        update(0);
        void Tick()
        {
            if (generation != _generation) return;
            var progress = Math.Clamp((clock.Now - start).TotalMilliseconds / milliseconds, 0, 1);
            if (progress >= 1)
            {
                Finish();
                return;
            }

            _update?.Invoke(progress);
            clock.RequestFrame(_target, Tick);
        }

        clock.RequestFrame(_target, Tick);
    }

    public void Cancel()
    {
        ++_generation;
        _update = null;
        _completed = null;
    }

    public void Finish()
    {
        var update = _update;
        var completed = _completed;
        Cancel();
        update?.Invoke(1);
        completed?.Invoke();
    }
}
