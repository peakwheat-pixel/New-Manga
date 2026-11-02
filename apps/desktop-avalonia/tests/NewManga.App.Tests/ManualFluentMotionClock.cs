using System;
using System.Collections.Generic;
using Avalonia.Controls;
using NewManga.App.Views.Fluent;

namespace NewManga.App.Tests;

/// <summary>Advances the production interpolator, without sleeps, dispatcher timers or test-only completion.</summary>
internal sealed class ManualFluentMotionClock : IFluentMotionClock
{
    private readonly Queue<Action> _frames = new();
    public TimeSpan Now { get; private set; }
    public int PendingFrames => _frames.Count;
    public void RequestFrame(Control target, Action callback) => _frames.Enqueue(callback);

    public void Advance(double milliseconds)
    {
        Now += TimeSpan.FromMilliseconds(milliseconds);
        var count = _frames.Count;
        for (var i = 0; i < count; i++) _frames.Dequeue()();
    }
}
