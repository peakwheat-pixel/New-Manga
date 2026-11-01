using static NewManga.ApplicationCore.Tests.TestSupport;

namespace NewManga.ApplicationCore.Tests;

public sealed class RequestExecutorTests
{
    [Fact]
    public void Assembly_has_no_presentation_transport_or_storage_dependency()
    {
        var references = typeof(RequestExecutor).Assembly.GetReferencedAssemblies();
        Assert.All(references, reference => Assert.StartsWith("System", reference.Name));
    }

    [Fact]
    public async Task Concurrent_fault_is_request_local_and_does_not_replace_success()
    {
        var executor = new RequestExecutor();
        var failure = new InvalidOperationException("request A only");
        var a = executor.ExecuteAsync<int>(_ => Task.FromException<int>(failure));
        var b = executor.ExecuteAsync(_ => Task.FromResult(42));
        var results = await Task.WhenAll(a, b).Within();
        Assert.Equal(RequestFailureKind.Faulted, results[0].Error!.Kind);
        Assert.Same(failure, results[0].Error!.Cause);
        Assert.True(results[1].IsSuccess);
        Assert.Equal(42, results[1].Value);
        Assert.NotEqual(results[0].RequestId, results[1].RequestId);
    }

    [Fact]
    public async Task Adapter_rejection_keeps_source_code_and_failure_identity_without_mapping()
    {
        var failure = new RequestFailure(RequestFailureKind.Rejected, "arbitrary.core.code", "detail");
        var result = await new RequestExecutor().ExecuteAsync<int>(_ => throw new RequestRejectedException(failure));
        Assert.Same(failure, result.Error);
        Assert.Equal("arbitrary.core.code", result.Error!.SourceCode);
    }

    [Fact]
    public async Task Precancelled_request_does_not_invoke_adapter()
    {
        var called = false;
        var result = await new RequestExecutor().ExecuteAsync(_ =>
        {
            called = true;
            return Task.FromResult(1);
        }, new CancellationToken(true));
        Assert.False(called);
        Assert.Equal(RequestFailureKind.Cancelled, result.Error!.Kind);
    }

    [Fact]
    public async Task Cancellation_finishes_even_if_adapter_ignores_token_and_late_fault_is_isolated()
    {
        var late = Completion<int>();
        using var cancellation = new CancellationTokenSource();
        var executor = new RequestExecutor();
        var pending = executor.ExecuteAsync(_ => late.Task, cancellation.Token);
        cancellation.Cancel();
        Assert.Equal(RequestFailureKind.Cancelled, (await pending.Within()).Error!.Kind);
        late.SetException(new InvalidOperationException("late adapter failure"));
        Assert.Equal(9, (await executor.ExecuteAsync(_ => Task.FromResult(9))).Value);
    }

    [Fact]
    public async Task Timeout_uses_injected_clock_and_cancels_only_its_operation()
    {
        var time = new ManualTimeProvider();
        var executor = new RequestExecutor(time);
        var late = Completion<int>();
        var cancelled = Completion<bool>();
        var pending = executor.ExecuteAsync(token =>
        {
            token.Register(() => cancelled.TrySetResult(true));
            return late.Task;
        }, timeout: TimeSpan.FromSeconds(5));
        time.Advance(TimeSpan.FromSeconds(5));
        Assert.Equal(RequestFailureKind.TimedOut, (await pending.Within()).Error!.Kind);
        Assert.True(await cancelled.Task.Within());
        late.SetResult(100);
        Assert.Equal(10, (await executor.ExecuteAsync(_ => Task.FromResult(10))).Value);
    }

    [Theory]
    [InlineData(RequestFailureKind.Faulted)]
    [InlineData(RequestFailureKind.Cancelled)]
    [InlineData(RequestFailureKind.TimedOut)]
    public async Task Concurrent_success_retains_its_result_when_another_request_fails(RequestFailureKind kind)
    {
        var clock = new ManualTimeProvider();
        var executor = new RequestExecutor(clock);
        using var cancellation = new CancellationTokenSource();
        var badReply = Completion<int>();
        var goodReply = Completion<int>();
        var bad = executor.ExecuteAsync(_ => badReply.Task, cancellation.Token, TimeSpan.FromSeconds(5));
        var good = executor.ExecuteAsync(_ => goodReply.Task);
        if (kind == RequestFailureKind.Faulted) badReply.SetException(new InvalidOperationException("bad"));
        else if (kind == RequestFailureKind.Cancelled) cancellation.Cancel();
        else clock.Advance(TimeSpan.FromSeconds(5));
        Assert.Equal(kind, (await bad.Within()).Error!.Kind);
        Assert.False(good.IsCompleted);
        goodReply.SetResult(123);
        var success = await good.Within();
        Assert.True(success.IsSuccess);
        Assert.Null(success.Error);
        Assert.Equal(123, success.Value);
        badReply.TrySetResult(0);
        Assert.Equal(123, success.Value);
    }
}
