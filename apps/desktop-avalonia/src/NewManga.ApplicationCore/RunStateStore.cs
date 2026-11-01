using System.Collections.ObjectModel;

namespace NewManga.ApplicationCore;

/// <summary>A successful, authoritative snapshot supplied by an adapter; no progress is derived here.</summary>
public sealed record RunSnapshot<T>(string RunId, long Version, Guid RequestId, T Value, DateTimeOffset ObservedAt)
    where T : class;

/// <summary>Application-owned in-memory state. Failed requests never replace a successful snapshot.</summary>
public sealed class RunStateStore<T> where T : class
{
    private readonly object _gate = new();
    private readonly Dictionary<string, RunSnapshot<T>> _snapshots = new(StringComparer.Ordinal);

    public RunSnapshot<T>? GetSnapshot(string runId)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(runId);
        lock (_gate) return _snapshots.GetValueOrDefault(runId);
    }

    public IReadOnlyDictionary<string, RunSnapshot<T>> GetSnapshots()
    {
        lock (_gate) return new ReadOnlyDictionary<string, RunSnapshot<T>>(
            new Dictionary<string, RunSnapshot<T>>(_snapshots, StringComparer.Ordinal));
    }

    internal RunSnapshot<T> Publish(string runId, RequestResult<T> result, DateTimeOffset observedAt)
    {
        lock (_gate)
        {
            var version = (_snapshots.GetValueOrDefault(runId)?.Version ?? 0) + 1;
            var snapshot = new RunSnapshot<T>(runId, version, result.RequestId, result.Value!, observedAt);
            _snapshots[runId] = snapshot;
            return snapshot;
        }
    }

    internal bool Remove(string runId)
    {
        lock (_gate) return _snapshots.Remove(runId);
    }
}
