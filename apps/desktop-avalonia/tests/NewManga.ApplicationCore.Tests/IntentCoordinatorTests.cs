using static NewManga.ApplicationCore.Tests.TestSupport;

namespace NewManga.ApplicationCore.Tests;

public sealed class IntentCoordinatorTests
{
    [Fact]
    public async Task Concurrent_retries_of_pending_intent_share_one_start_task_and_result()
    {
        await using var coordinator = new IntentCoordinator<TestRun>();
        var calls = 0;
        var release = Completion<TestRun>();
        var pending = Enumerable.Range(0, 64).AsParallel().Select(_ => coordinator.ExecuteAsync("intent-a", (key, _) =>
        {
            Assert.Equal("intent-a", key);
            Interlocked.Increment(ref calls);
            return release.Task;
        })).ToArray();
        Assert.Equal(1, calls);
        Assert.All(pending, task => Assert.Same(pending[0], task));
        var value = new TestRun("running");
        release.SetResult(value);
        var results = await Task.WhenAll(pending).Within();
        Assert.All(results, result => Assert.Same(results[0], result));
        Assert.Same(value, results[0].Value);

        var next = await coordinator.ExecuteAsync("new-intent", (_, _) =>
        {
            Interlocked.Increment(ref calls);
            return Task.FromResult(new TestRun("next"));
        });
        Assert.True(next.IsSuccess);
        Assert.Equal(2, calls);
        Assert.NotEqual(results[0].RequestId, next.RequestId);
    }

    [Fact]
    public async Task Completed_flight_is_released_but_original_key_is_forwarded_for_durable_idempotency()
    {
        await using var coordinator = new IntentCoordinator<int>();
        var keys = new List<string>();
        Task<int> Adapter(string key, CancellationToken token) { keys.Add(key); return Task.FromResult(7); }
        var first = await coordinator.ExecuteAsync("original-key", Adapter);
        var second = await coordinator.ExecuteAsync("original-key", Adapter);
        Assert.Equal(new[] { "original-key", "original-key" }, keys);
        Assert.NotEqual(first.RequestId, second.RequestId);
    }

    [Fact]
    public async Task Cancelling_one_waiter_does_not_cancel_shared_start_or_other_waiter()
    {
        await using var coordinator = new IntentCoordinator<int>();
        using var cancellation = new CancellationTokenSource();
        var release = Completion<int>();
        CancellationToken adapterToken = default;
        var owner = coordinator.ExecuteAsync("same", (_, token) => { adapterToken = token; return release.Task; });
        var waiter = coordinator.ExecuteAsync("same", (_, _) => throw new InvalidOperationException("duplicate start"), cancellation.Token);
        cancellation.Cancel();
        Assert.Equal(RequestFailureKind.Cancelled, (await waiter.Within()).Error!.Kind);
        Assert.False(adapterToken.IsCancellationRequested);
        release.SetResult(42);
        Assert.Equal(42, (await owner.Within()).Value);
    }

    [Fact]
    public async Task Different_intents_have_independent_failures_and_pre_cancelled_intent_never_starts()
    {
        await using var coordinator = new IntentCoordinator<int>();
        var rejected = coordinator.ExecuteAsync("bad", (_, _) => Task.FromException<int>(new InvalidOperationException("bad")));
        var good = coordinator.ExecuteAsync("good", (_, _) => Task.FromResult(2));
        var cancelled = coordinator.ExecuteAsync("cancelled", (_, _) => throw new InvalidOperationException("must not call"), new CancellationToken(true));
        Assert.Equal(RequestFailureKind.Faulted, (await rejected).Error!.Kind);
        Assert.Equal(2, (await good).Value);
        Assert.Equal(RequestFailureKind.Cancelled, (await cancelled).Error!.Kind);
    }

    [Fact]
    public async Task Shared_timeout_releases_flight_and_late_reply_does_not_complete_next_intent()
    {
        var time = new ManualTimeProvider();
        await using var coordinator = new IntentCoordinator<int>(new RequestExecutor(time), TimeSpan.FromSeconds(5));
        var late = Completion<int>();
        var first = coordinator.ExecuteAsync("intent", (_, _) => late.Task);
        var retry = coordinator.ExecuteAsync("intent", (_, _) => throw new InvalidOperationException("duplicate"));
        time.Advance(TimeSpan.FromSeconds(5));
        var timeout = await first.Within();
        Assert.Same(timeout, await retry.Within());
        Assert.Equal(RequestFailureKind.TimedOut, timeout.Error!.Kind);
        var next = await coordinator.ExecuteAsync("intent", (_, _) => Task.FromResult(99));
        late.SetResult(1);
        Assert.Equal(99, next.Value);
        Assert.True(next.IsSuccess);
    }

    [Fact]
    public async Task Disposal_cancels_pending_flights_without_waiting_for_uncooperative_adapter()
    {
        var coordinator = new IntentCoordinator<int>();
        var late = Completion<int>();
        var pending = coordinator.ExecuteAsync("pending", (_, _) => late.Task);
        await Task.WhenAll(coordinator.DisposeAsync().AsTask(), coordinator.DisposeAsync().AsTask()).Within();
        Assert.Equal(RequestFailureKind.Cancelled, (await pending).Error!.Kind);
        await Assert.ThrowsAsync<ObjectDisposedException>(() => coordinator.ExecuteAsync("next", (_, _) => Task.FromResult(1)));
        late.SetResult(42);
    }
}
