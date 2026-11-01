namespace NewManga.ApplicationCore;

/// <summary>
/// Shares in-flight work for an intent key. This is not durable idempotency: the adapter must forward
/// the original key to Core. Completed flights are released; distinct new intentions use new keys.
/// Cancelling a caller only cancels that caller's wait, never another caller's shared operation.
/// </summary>
public sealed class IntentCoordinator<T> : IAsyncDisposable
{
    private readonly object _gate = new();
    private readonly Dictionary<string, TaskCompletionSource<RequestResult<T>>> _flights = new(StringComparer.Ordinal);
    private readonly CancellationTokenSource _lifetime = new();
    private readonly CancellationToken _token;
    private readonly RequestExecutor _executor;
    private readonly TimeSpan? _timeout;
    private Task? _shutdown;
    private bool _disposed;

    public IntentCoordinator(RequestExecutor? executor = null, TimeSpan? timeout = null)
    {
        RequestExecutor.ValidateTimeout(timeout);
        _executor = executor ?? new();
        _timeout = timeout;
        _token = _lifetime.Token;
    }

    public Task<RequestResult<T>> ExecuteAsync(string intentKey,
        Func<string, CancellationToken, Task<T>> operation, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(intentKey);
        ArgumentNullException.ThrowIfNull(operation);
        TaskCompletionSource<RequestResult<T>> flight;
        bool start;
        lock (_gate)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            if (cancellationToken.IsCancellationRequested)
                return Task.FromResult(RequestResult<T>.Failure(Guid.NewGuid(), new(RequestFailureKind.Cancelled)));
            start = !_flights.TryGetValue(intentKey, out flight!);
            if (start)
            {
                flight = new(TaskCreationOptions.RunContinuationsAsynchronously);
                _flights.Add(intentKey, flight);
            }
        }
        if (start) _ = ExecuteFlightAsync(intentKey, operation, flight);
        return cancellationToken.CanBeCanceled
            ? RequestExecutor.WaitForCallerAsync(flight.Task, cancellationToken) : flight.Task;
    }

    private async Task ExecuteFlightAsync(string key, Func<string, CancellationToken, Task<T>> operation,
        TaskCompletionSource<RequestResult<T>> flight)
    {
        var result = await _executor.ExecuteAsync(ct => operation(key, ct), _token, _timeout)
            .ConfigureAwait(false);
        lock (_gate)
        {
            flight.TrySetResult(result);
            _flights.Remove(key);
        }
    }

    public ValueTask DisposeAsync()
    {
        TaskCompletionSource? completion = null;
        Task[] pending = [];
        lock (_gate)
        {
            if (_shutdown is null)
            {
                _disposed = true;
                pending = _flights.Values.Select(flight => (Task)flight.Task).ToArray();
                completion = new(TaskCreationOptions.RunContinuationsAsynchronously);
                _shutdown = completion.Task;
            }
        }
        if (completion is not null) _ = StopAsync(pending, completion);
        return new(_shutdown!);
    }

    private async Task StopAsync(Task[] pending, TaskCompletionSource completion)
    {
        RequestExecutor.Cancel(_lifetime);
        await Task.WhenAll(pending).ConfigureAwait(false);
        _lifetime.Dispose();
        completion.SetResult();
    }
}
