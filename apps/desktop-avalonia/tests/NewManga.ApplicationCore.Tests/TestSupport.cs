using System.Threading.Channels;

namespace NewManga.ApplicationCore.Tests;

internal sealed record TestRun(string Status);

internal static class TestSupport
{
    public static TaskCompletionSource<T> Completion<T>() => new(TaskCreationOptions.RunContinuationsAsynchronously);
    public static async Task<T> Within<T>(this Task<T> task) => await task.WaitAsync(TimeSpan.FromSeconds(10));
    public static async Task Within(this Task task) => await task.WaitAsync(TimeSpan.FromSeconds(10));
    public static async Task Eventually(Func<bool> condition)
    {
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        while (!condition()) await Task.Delay(1, timeout.Token);
    }
    public static Channel<RunObservation<TestRun>> Observations() => Channel.CreateUnbounded<RunObservation<TestRun>>();
    public static Task<RunObservation<TestRun>> Next(this Channel<RunObservation<TestRun>> channel) =>
        channel.Reader.ReadAsync().AsTask().Within();
}

// Virtual time drives both Task.Delay and Task.WaitAsync without real polling intervals/timeouts.
internal sealed class ManualTimeProvider : TimeProvider
{
    private readonly object _gate = new();
    private readonly HashSet<ManualTimer> _timers = new();
    private DateTimeOffset _now = DateTimeOffset.UnixEpoch;
    public override long TimestampFrequency => TimeSpan.TicksPerSecond;
    public override DateTimeOffset GetUtcNow() { lock (_gate) return _now; }
    public override long GetTimestamp() => GetUtcNow().Ticks;
    public int ActiveTimerCount { get { lock (_gate) return _timers.Count(timer => timer.Due is not null); } }
    public override ITimer CreateTimer(TimerCallback callback, object? state, TimeSpan dueTime, TimeSpan period)
    {
        var timer = new ManualTimer(this, callback, state);
        timer.Change(dueTime, period);
        return timer;
    }
    public void Advance(TimeSpan elapsed)
    {
        if (elapsed < TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(elapsed));
        List<ManualTimer> due;
        lock (_gate)
        {
            _now += elapsed;
            due = _timers.Where(timer => timer.Due <= _now).ToList();
            foreach (var timer in due)
                timer.Due = timer.Period > TimeSpan.Zero ? _now + timer.Period : null;
        }
        foreach (var timer in due) timer.Fire();
    }
    private sealed class ManualTimer(ManualTimeProvider owner, TimerCallback callback, object? state) : ITimer
    {
        private bool _disposed;
        public DateTimeOffset? Due { get; set; }
        public TimeSpan Period { get; private set; }
        public bool Change(TimeSpan dueTime, TimeSpan period)
        {
            lock (owner._gate)
            {
                if (_disposed) return false;
                Period = period;
                Due = dueTime == Timeout.InfiniteTimeSpan ? null : owner._now + dueTime;
                owner._timers.Add(this);
                return true;
            }
        }
        public void Fire()
        {
            lock (owner._gate) { if (_disposed) return; }
            callback(state);
        }
        public void Dispose() { lock (owner._gate) { _disposed = true; owner._timers.Remove(this); } }
        public ValueTask DisposeAsync() { Dispose(); return ValueTask.CompletedTask; }
    }
}
