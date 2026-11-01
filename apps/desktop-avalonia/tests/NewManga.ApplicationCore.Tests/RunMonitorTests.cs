using static NewManga.ApplicationCore.Tests.TestSupport;

namespace NewManga.ApplicationCore.Tests;

public sealed class RunMonitorTests
{
    private static readonly TimeSpan Interval = TimeSpan.FromSeconds(30);

    [Fact]
    public async Task Many_observers_share_one_query_and_the_same_snapshot_then_one_next_tick()
    {
        var clock = new ManualTimeProvider();
        var release = Completion<TestRun>();
        var calls = 0;
        await using var monitor = new RunMonitor<TestRun>((_, _) =>
        {
            Interlocked.Increment(ref calls);
            return release.Task;
        }, Interval, timeProvider: clock);
        var channels = Enumerable.Range(0, 32).Select(_ => Observations()).ToArray();
        var subscriptions = channels.Select(channel => monitor.Subscribe("run-a", value => channel.Writer.TryWrite(value))).ToArray();
        try
        {
            await Eventually(() => Volatile.Read(ref calls) == 1);
            var refreshes = Enumerable.Range(0, 32).Select(_ => monitor.RefreshAsync("run-a")).ToArray();
            Assert.All(refreshes, task => Assert.Same(refreshes[0], task));
            var value = new TestRun("running");
            release.SetResult(value);
            var observations = await Task.WhenAll(channels.Select(channel => channel.Next()));
            var result = await refreshes[0].Within();
            Assert.All(observations, observation => Assert.Same(observations[0], observation));
            Assert.Same(value, observations[0].Snapshot!.Value);
            Assert.Same(result, observations[0].Request);
            Assert.Same(observations[0].Snapshot, monitor.State.GetSnapshot("run-a"));
            Assert.Equal(1, calls);
            await Eventually(() => clock.ActiveTimerCount == 1);
            clock.Advance(Interval);
            var second = await Task.WhenAll(channels.Select(channel => channel.Next()));
            Assert.Equal(2, calls);
            Assert.All(second, observation => Assert.Same(second[0].Snapshot, observation.Snapshot));
            Assert.Equal(2, second[0].Snapshot!.Version);
        }
        finally { foreach (var subscription in subscriptions) subscription.Dispose(); }
    }

    [Fact]
    public async Task Failure_keeps_last_success_and_does_not_contaminate_another_run()
    {
        var clock = new ManualTimeProvider();
        var aCalls = 0;
        var rejection = new RequestFailure(RequestFailureKind.Rejected, "source.code", "only A failed");
        await using var monitor = new RunMonitor<TestRun>((id, _) =>
            id == "a" && Interlocked.Increment(ref aCalls) > 1
                ? Task.FromException<TestRun>(new RequestRejectedException(rejection))
                : Task.FromResult(new TestRun(id)), Interval, timeProvider: clock);
        var a = Observations();
        var b = Observations();
        using var aSubscription = monitor.Subscribe("a", value => a.Writer.TryWrite(value));
        using var bSubscription = monitor.Subscribe("b", value => b.Writer.TryWrite(value));
        var initialA = await a.Next();
        var initialB = await b.Next();
        await Eventually(() => clock.ActiveTimerCount == 2);
        var result = await monitor.RefreshAsync("a").Within();
        var failed = await a.Next();
        Assert.Same(rejection, result.Error);
        Assert.Same(initialA.Snapshot, failed.Snapshot);
        Assert.Same(initialA.Snapshot, monitor.State.GetSnapshot("a"));
        Assert.Same(initialB.Snapshot, monitor.State.GetSnapshot("b"));
        Assert.False(b.Reader.TryRead(out _));
        var copy = monitor.State.GetSnapshots();
        Assert.Equal(2, copy.Count);
        Assert.Throws<NotSupportedException>(() => ((IDictionary<string, RunSnapshot<TestRun>>)copy).Clear());
    }

    [Theory]
    [InlineData(true)]
    [InlineData(false)]
    public async Task Timeout_or_cancellation_does_not_replace_a_successful_snapshot(bool timeout)
    {
        var clock = new ManualTimeProvider();
        var late = Completion<TestRun>();
        var calls = 0;
        await using var monitor = new RunMonitor<TestRun>((_, _) =>
            Interlocked.Increment(ref calls) == 1 ? Task.FromResult(new TestRun("first")) : late.Task,
            Interval, requestTimeout: TimeSpan.FromSeconds(5), timeProvider: clock);
        var channel = Observations();
        using var subscription = monitor.Subscribe("a", value => channel.Writer.TryWrite(value));
        var initial = await channel.Next();
        await Eventually(() => clock.ActiveTimerCount == 1);
        using var cancellation = new CancellationTokenSource();
        var refresh = monitor.RefreshAsync("a", cancellation.Token);
        await Eventually(() => Volatile.Read(ref calls) == 2 && clock.ActiveTimerCount == 2);
        if (timeout) clock.Advance(TimeSpan.FromSeconds(5));
        else cancellation.Cancel();
        var result = await refresh.Within();
        Assert.Equal(timeout ? RequestFailureKind.TimedOut : RequestFailureKind.Cancelled, result.Error!.Kind);
        Assert.Same(initial.Snapshot, monitor.State.GetSnapshot("a"));
        if (timeout)
        {
            var failed = await channel.Next();
            Assert.Same(initial.Snapshot, failed.Snapshot);
            late.SetResult(new TestRun("too late"));
            Assert.Same(initial.Snapshot, monitor.State.GetSnapshot("a"));
        }
        else
        {
            // Only this waiter was cancelled. The shared query can still publish its valid result.
            late.SetResult(new TestRun("completed"));
            Assert.Equal("completed", (await channel.Next()).Snapshot!.Value.Status);
        }
    }

    [Fact]
    public async Task Last_unsubscribe_cancels_query_but_another_observer_keeps_it_alive()
    {
        var started = Completion<CancellationToken>();
        var cancelled = Completion<bool>();
        await using var monitor = new RunMonitor<TestRun>((_, token) =>
        {
            token.Register(() => cancelled.TrySetResult(true));
            started.TrySetResult(token);
            return Completion<TestRun>().Task;
        }, Interval);
        var first = monitor.Subscribe("a", _ => { });
        var second = monitor.Subscribe("a", _ => { });
        var adapterToken = await started.Task.Within();
        first.Dispose();
        Assert.False(adapterToken.IsCancellationRequested);
        second.Dispose();
        Assert.True(await cancelled.Task.Within());
        second.Dispose();
        await Assert.ThrowsAsync<InvalidOperationException>(() => monitor.RefreshAsync("a"));
    }

    [Fact]
    public async Task Replay_is_cached_without_extra_query_and_active_cache_cannot_be_forgotten()
    {
        var clock = new ManualTimeProvider();
        var calls = 0;
        await using var monitor = new RunMonitor<TestRun>((_, _) =>
        {
            Interlocked.Increment(ref calls);
            return Task.FromResult(new TestRun("first"));
        }, Interval, timeProvider: clock);
        var first = Observations();
        var subscription = monitor.Subscribe("a", value => first.Writer.TryWrite(value));
        var snapshot = (await first.Next()).Snapshot;
        var second = Observations();
        using var other = monitor.Subscribe("a", value => second.Writer.TryWrite(value));
        var replay = await second.Next();
        Assert.True(replay.IsReplay);
        Assert.Same(snapshot, replay.Snapshot);
        Assert.Equal(1, calls);
        Assert.False(monitor.ForgetRun("a"));
        subscription.Dispose();
        other.Dispose();
        Assert.True(monitor.ForgetRun("a"));
        Assert.Null(monitor.State.GetSnapshot("a"));
        Assert.False(monitor.ForgetRun("a"));
    }

    [Fact]
    public async Task Old_generation_cannot_overwrite_resubscribed_run_after_late_reply()
    {
        var oldReply = Completion<TestRun>();
        var oldStarted = Completion<bool>();
        var calls = 0;
        await using var monitor = new RunMonitor<TestRun>((_, _) =>
        {
            if (Interlocked.Increment(ref calls) != 1) return Task.FromResult(new TestRun("new"));
            oldStarted.SetResult(true);
            return oldReply.Task;
        }, Interval);
        var oldChannel = Observations();
        var oldSubscription = monitor.Subscribe("a", value => oldChannel.Writer.TryWrite(value));
        await oldStarted.Task.Within();
        oldSubscription.Dispose();
        var newChannel = Observations();
        using var newSubscription = monitor.Subscribe("a", value => newChannel.Writer.TryWrite(value));
        var current = await newChannel.Next();
        oldReply.SetResult(new TestRun("old"));
        await monitor.DisposeAsync().AsTask().Within();
        Assert.Equal("new", current.Snapshot!.Value.Status);
        Assert.Same(current.Snapshot, monitor.State.GetSnapshot("a"));
        Assert.False(oldChannel.Reader.TryRead(out _));
        Assert.False(newChannel.Reader.TryRead(out _));
    }

    [Fact]
    public async Task Observer_exceptions_do_not_break_other_observers_or_future_polls()
    {
        var clock = new ManualTimeProvider();
        var release = Completion<TestRun>();
        var errors = Completion<Exception>();
        var expected = new InvalidOperationException("observer only");
        await using var monitor = new RunMonitor<TestRun>((_, _) => release.Task, Interval, timeProvider: clock);
        using var broken = monitor.Subscribe("a", _ => throw expected, error =>
        {
            errors.TrySetResult(error);
            throw new InvalidOperationException("error observer also fails");
        });
        var channel = Observations();
        using var healthy = monitor.Subscribe("a", value => channel.Writer.TryWrite(value));
        release.SetResult(new TestRun("success"));
        Assert.Same(expected, await errors.Task.Within());
        Assert.True((await channel.Next()).Request.IsSuccess);
        await Eventually(() => clock.ActiveTimerCount == 1);
        clock.Advance(Interval);
        Assert.Equal(2, (await channel.Next()).Snapshot!.Version);
    }

    [Fact]
    public async Task Callback_can_unsubscribe_itself_and_subscribe_another_run_without_deadlock()
    {
        var release = Completion<TestRun>();
        var finished = Completion<bool>();
        await using var monitor = new RunMonitor<TestRun>((_, _) => release.Task, Interval);
        IDisposable? subscription = null;
        subscription = monitor.Subscribe("a", _ =>
        {
            subscription!.Dispose();
            using var other = monitor.Subscribe("b", _ => { });
            finished.TrySetResult(true);
        });
        release.SetResult(new TestRun("success"));
        Assert.True(await finished.Task.Within());
    }

    [Fact]
    public async Task Disposal_stops_queries_and_rejects_new_work_without_clearing_last_success()
    {
        var clock = new ManualTimeProvider();
        var calls = 0;
        var monitor = new RunMonitor<TestRun>((_, _) =>
        {
            Interlocked.Increment(ref calls);
            return Task.FromResult(new TestRun("success"));
        }, Interval, timeProvider: clock);
        Assert.Equal(0, calls); // Construction never starts a scheduler or queries anything.
        var channel = Observations();
        using var subscription = monitor.Subscribe("a", value => channel.Writer.TryWrite(value));
        var snapshot = (await channel.Next()).Snapshot;
        await Task.WhenAll(monitor.DisposeAsync().AsTask(), monitor.DisposeAsync().AsTask()).Within();
        clock.Advance(Interval + Interval);
        Assert.Equal(1, calls);
        Assert.Same(snapshot, monitor.State.GetSnapshot("a"));
        Assert.Throws<ObjectDisposedException>(() => monitor.Subscribe("a", _ => { }));
        await Assert.ThrowsAsync<ObjectDisposedException>(() => monitor.RefreshAsync("a"));
    }
}
