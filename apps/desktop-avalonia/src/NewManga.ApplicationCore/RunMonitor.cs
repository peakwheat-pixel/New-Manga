namespace NewManga.ApplicationCore;

public sealed record RunObservation<T>(long Sequence, RunSnapshot<T>? Snapshot, RequestResult<T> Request,
    bool IsReplay = false) where T : class;

/// <summary>
/// One application-owned monitor, one polling loop and at most one query per subscribed Run.
/// It only queries an injected port: it cannot start a Run, own Host lifetime, or schedule Core tasks.
/// Query callbacks run on worker threads; a cached replay may run synchronously during Subscribe.
/// Presentation adapters must marshal notifications to their dispatcher.
/// Snapshot values supplied by the adapter must be immutable.
/// </summary>
public sealed class RunMonitor<T> : IAsyncDisposable where T : class
{
    private readonly object _gate = new();
    private readonly Dictionary<string, Entry> _entries = new(StringComparer.Ordinal);
    private readonly HashSet<Entry> _retiring = new();
    private readonly Func<string, CancellationToken, Task<T>> _query;
    private readonly TimeSpan _interval;
    private readonly TimeSpan? _timeout;
    private readonly TimeProvider _time;
    private readonly RequestExecutor _executor;
    private long _nextObserver;
    private bool _disposed;
    private Task? _shutdown;

    public RunMonitor(Func<string, CancellationToken, Task<T>> query, TimeSpan interval,
        TimeSpan? requestTimeout = null, TimeProvider? timeProvider = null)
    {
        ArgumentNullException.ThrowIfNull(query);
        if (interval <= TimeSpan.Zero || interval.TotalMilliseconds > uint.MaxValue - 1)
            throw new ArgumentOutOfRangeException(nameof(interval));
        RequestExecutor.ValidateTimeout(requestTimeout);
        (_query, _interval, _timeout, _time) = (query, interval, requestTimeout, timeProvider ?? TimeProvider.System);
        _executor = new(_time);
    }

    public RunStateStore<T> State { get; } = new();

    public IDisposable Subscribe(string runId, Action<RunObservation<T>> callback,
        Action<Exception>? observerError = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(runId);
        ArgumentNullException.ThrowIfNull(callback);
        Entry entry;
        Observer observer;
        RunObservation<T>? replay;
        lock (_gate)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            if (!_entries.TryGetValue(runId, out entry!))
            {
                entry = new(runId);
                _entries.Add(runId, entry);
                var cached = State.GetSnapshot(runId);
                if (cached is not null)
                    entry.Latest = new(0, cached, RequestResult<T>.Success(cached.RequestId, cached.Value));
            }
            observer = new(++_nextObserver, callback, observerError);
            entry.Observers.Add(observer.Id, observer);
            replay = entry.Latest;
            entry.Loop ??= Task.Run(() => PollLoopAsync(entry));
        }
        if (replay is not null) observer.Deliver(replay with { IsReplay = true });
        return new Subscription(this, entry, observer);
    }

    /// <summary>Coalesces refreshes with the current poll; caller cancellation only stops its own wait.</summary>
    public Task<RequestResult<T>> RefreshAsync(string runId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(runId);
        Task<RequestResult<T>> pending;
        lock (_gate)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            if (!_entries.TryGetValue(runId, out var entry))
                throw new InvalidOperationException("Refresh requires an active Run subscription.");
            if (cancellationToken.IsCancellationRequested)
                return Task.FromResult(RequestResult<T>.Failure(Guid.NewGuid(), new(RequestFailureKind.Cancelled)));
            pending = GetOrStartPoll(entry);
        }
        return cancellationToken.CanBeCanceled
            ? RequestExecutor.WaitForCallerAsync(pending, cancellationToken) : pending;
    }

    /// <summary>Explicitly releases old in-memory state; active subscriptions cannot be forgotten.</summary>
    public bool ForgetRun(string runId)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(runId);
        lock (_gate)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            return !_entries.ContainsKey(runId) && State.Remove(runId);
        }
    }

    private Task<RequestResult<T>> GetOrStartPoll(Entry entry)
    {
        if (entry.Pending is null)
        {
            var completion = new TaskCompletionSource<RequestResult<T>>(TaskCreationOptions.RunContinuationsAsynchronously);
            entry.Pending = completion.Task;
            // Do not invoke an adapter or a callback while holding the monitor lock.
            _ = Task.Run(() => PollOnceAsync(entry, completion));
        }
        return entry.Pending;
    }

    private async Task PollOnceAsync(Entry entry, TaskCompletionSource<RequestResult<T>> completion)
    {
        var result = await _executor.ExecuteAsync(async token =>
            await _query(entry.RunId, token).ConfigureAwait(false)
                ?? throw new InvalidOperationException("A Run query returned no snapshot."), entry.Token, _timeout)
            .ConfigureAwait(false);
        Observer[] observers = [];
        RunObservation<T>? observation = null;
        lock (_gate)
        {
            if (!_disposed && !entry.Token.IsCancellationRequested &&
                _entries.TryGetValue(entry.RunId, out var current) && ReferenceEquals(current, entry))
            {
                var snapshot = result.IsSuccess
                    ? State.Publish(entry.RunId, result, _time.GetUtcNow()) : State.GetSnapshot(entry.RunId);
                observation = new(++entry.Sequence, snapshot, result);
                entry.Latest = observation;
                observers = entry.Observers.Values.ToArray();
            }
            entry.Pending = null;
            completion.TrySetResult(result);
        }
        if (observation is not null)
            foreach (var observer in observers) observer.Deliver(observation);
    }

    private async Task PollLoopAsync(Entry entry)
    {
        try
        {
            while (!entry.Token.IsCancellationRequested)
            {
                Task<RequestResult<T>> poll;
                lock (_gate)
                {
                    if (_disposed || entry.Token.IsCancellationRequested) return;
                    poll = GetOrStartPoll(entry);
                }
                await poll.ConfigureAwait(false);
                await Task.Delay(_interval, _time, entry.Token).ConfigureAwait(false);
            }
        }
        catch (OperationCanceledException) when (entry.Token.IsCancellationRequested) { }
    }

    private void Unsubscribe(Entry entry, Observer observer)
    {
        bool stop;
        lock (_gate)
        {
            entry.Observers.Remove(observer.Id);
            stop = entry.Observers.Count == 0;
            if (stop && _entries.TryGetValue(entry.RunId, out var current) && ReferenceEquals(entry, current))
            {
                _entries.Remove(entry.RunId);
                _retiring.Add(entry);
            }
        }
        observer.Disable();
        if (stop) _ = RetireAsync(entry);
    }

    private async Task RetireAsync(Entry entry)
    {
        await StopEntryAsync(entry).ConfigureAwait(false);
        lock (_gate) _retiring.Remove(entry);
    }

    private static Task StopEntryAsync(Entry entry)
    {
        TaskCompletionSource? completion = null;
        lock (entry.StopGate)
        {
            if (entry.Stop is null)
            {
                completion = new(TaskCreationOptions.RunContinuationsAsynchronously);
                entry.Stop = completion.Task;
            }
        }
        if (completion is not null) _ = StopCoreAsync(entry, completion);
        return entry.Stop;
    }

    private static async Task StopCoreAsync(Entry entry, TaskCompletionSource completion)
    {
        try
        {
            RequestExecutor.Cancel(entry.Cancellation);
            if (entry.Loop is not null) await entry.Loop.ConfigureAwait(false);
            if (entry.Pending is { } pending) await pending.ConfigureAwait(false);
            entry.Cancellation.Dispose();
            completion.SetResult();
        }
        catch (Exception exception) { completion.TrySetException(exception); }
    }

    public ValueTask DisposeAsync()
    {
        TaskCompletionSource? completion = null;
        Entry[] entries = [];
        Observer[] observers = [];
        lock (_gate)
        {
            if (_shutdown is null)
            {
                _disposed = true;
                entries = _entries.Values.Concat(_retiring).Distinct().ToArray();
                observers = entries.SelectMany(entry => entry.Observers.Values).ToArray();
                _entries.Clear();
                _retiring.Clear();
                completion = new(TaskCreationOptions.RunContinuationsAsynchronously);
                _shutdown = completion.Task;
            }
        }
        if (completion is not null) _ = StopAllAsync(entries, observers, completion);
        return new(_shutdown!);
    }

    private static async Task StopAllAsync(Entry[] entries, Observer[] observers, TaskCompletionSource completion)
    {
        try
        {
            foreach (var observer in observers) observer.Disable();
            await Task.WhenAll(entries.Select(StopEntryAsync)).ConfigureAwait(false);
            completion.SetResult();
        }
        catch (Exception exception) { completion.TrySetException(exception); }
    }

    private sealed class Entry
    {
        public Entry(string runId) => (RunId, Token) = (runId, Cancellation.Token);
        public string RunId { get; }
        public CancellationTokenSource Cancellation { get; } = new();
        public CancellationToken Token { get; }
        public Dictionary<long, Observer> Observers { get; } = new();
        public Task? Loop { get; set; }
        public Task<RequestResult<T>>? Pending { get; set; }
        public long Sequence { get; set; }
        public RunObservation<T>? Latest { get; set; }
        public object StopGate { get; } = new();
        public Task? Stop { get; set; }
    }

    private sealed class Observer(long id, Action<RunObservation<T>> callback, Action<Exception>? error)
    {
        private readonly object _gate = new();
        private bool _active = true;
        private bool _delivering;
        private readonly Queue<RunObservation<T>> _queue = new();
        private long _lastSequence = -1;
        public long Id { get; } = id;

        public void Deliver(RunObservation<T> observation)
        {
            lock (_gate)
            {
                if (!_active || observation.Sequence <= _lastSequence) return;
                _lastSequence = observation.Sequence;
                _queue.Enqueue(observation);
                if (_delivering) return;
                _delivering = true;
            }
            while (true)
            {
                RunObservation<T> next;
                lock (_gate)
                {
                    if (!_active || !_queue.TryDequeue(out next!))
                    {
                        _delivering = false;
                        return;
                    }
                }
                // Never hold an internal lock while invoking presentation code. An already running
                // callback may finish after unsubscribe; queued callbacks are discarded.
                try { callback(next); }
                catch (Exception exception)
                {
                    try { error?.Invoke(exception); }
                    catch (Exception) { /* An observer's diagnostics cannot interrupt other observers. */ }
                }
            }
        }

        public void Disable() { lock (_gate) { _active = false; _queue.Clear(); } }
    }

    private sealed class Subscription(RunMonitor<T> monitor, Entry entry, Observer observer) : IDisposable
    {
        private int _disposed;
        public void Dispose()
        {
            if (Interlocked.Exchange(ref _disposed, 1) == 0) monitor.Unsubscribe(entry, observer);
        }
    }
}
