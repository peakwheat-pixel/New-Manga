namespace NewManga.ApplicationCore;

/// <summary>Captures each request's result independently, including operations that ignore cancellation.</summary>
public sealed class RequestExecutor(TimeProvider? timeProvider = null)
{
    private readonly TimeProvider _time = timeProvider ?? TimeProvider.System;

    public async Task<RequestResult<T>> ExecuteAsync<T>(
        Func<CancellationToken, Task<T>> operation,
        CancellationToken cancellationToken = default,
        TimeSpan? timeout = null)
    {
        ArgumentNullException.ThrowIfNull(operation);
        ValidateTimeout(timeout);
        var requestId = Guid.NewGuid();
        using var lifetime = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        Task<T>? pending = null;
        try
        {
            cancellationToken.ThrowIfCancellationRequested();
            pending = operation(lifetime.Token) ?? throw new InvalidOperationException("The operation returned no Task.");
            var value = await pending.WaitAsync(timeout ?? Timeout.InfiniteTimeSpan, _time, cancellationToken)
                .ConfigureAwait(false);
            return RequestResult<T>.Success(requestId, value);
        }
        catch (TimeoutException exception)
        {
            Cancel(lifetime);
            ObserveFault(pending);
            return RequestResult<T>.Failure(requestId, new(RequestFailureKind.TimedOut, Cause: exception));
        }
        catch (OperationCanceledException exception)
        {
            Cancel(lifetime);
            ObserveFault(pending);
            return RequestResult<T>.Failure(requestId, new(RequestFailureKind.Cancelled, Cause: exception));
        }
        catch (RequestRejectedException exception)
        {
            return RequestResult<T>.Failure(requestId, exception.Failure);
        }
        catch (Exception exception)
        {
            return RequestResult<T>.Failure(requestId, new(RequestFailureKind.Faulted, Cause: exception));
        }
    }

    internal static void ValidateTimeout(TimeSpan? timeout)
    {
        if (timeout is { } value && value != Timeout.InfiniteTimeSpan &&
            (value <= TimeSpan.Zero || value.TotalMilliseconds > uint.MaxValue - 1))
            throw new ArgumentOutOfRangeException(nameof(timeout));
    }

    internal static void Cancel(CancellationTokenSource source)
    {
        try { source.Cancel(); }
        catch (AggregateException) { /* A consumer's cancellation callback cannot replace the request outcome. */ }
    }

    internal static async Task<RequestResult<T>> WaitForCallerAsync<T>(
        Task<RequestResult<T>> shared, CancellationToken callerCancellation)
    {
        try { return await shared.WaitAsync(callerCancellation).ConfigureAwait(false); }
        catch (OperationCanceledException exception) when (callerCancellation.IsCancellationRequested)
        {
            return RequestResult<T>.Failure(Guid.NewGuid(), new(RequestFailureKind.Cancelled, Cause: exception));
        }
    }

    private static void ObserveFault<T>(Task<T>? task)
    {
        if (task is not null)
            _ = task.ContinueWith(completed => { _ = completed.Exception; }, CancellationToken.None,
                TaskContinuationOptions.OnlyOnFaulted | TaskContinuationOptions.ExecuteSynchronously,
                TaskScheduler.Default);
    }
}
