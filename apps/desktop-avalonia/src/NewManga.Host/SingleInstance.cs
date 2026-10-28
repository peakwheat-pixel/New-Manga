using System.Diagnostics;

namespace NewManga.Host;

/// <summary>
/// Global single-instance mutex (<c>Global\NewManga.Host</c>, ADR-0001 D3). A second Host exits
/// instead of double-writing a shared data root. Abandoned mutexes (previous Host crashed) are
/// recovered instead of wedging the app.
/// </summary>
public sealed class SingleInstanceGuard : IDisposable
{
    public const string DefaultMutexName = @"Global\NewManga.Host";

    private readonly ISingleInstanceBackend _backend;
    private bool _disposed;

    private SingleInstanceGuard(string name, ISingleInstanceBackend backend, bool recoveredAbandoned)
    {
        Name = name;
        _backend = backend;
        RecoveredAbandoned = recoveredAbandoned;
    }

    public string Name { get; }

    /// <summary>True when the previous owner crashed without releasing (recovered, not fatal).</summary>
    public bool RecoveredAbandoned { get; }

    /// <summary>
    /// Acquires the single-instance guard. If the Global namespace is unavailable to this token
    /// (SeCreateGlobalPrivilege is not granted to standard interactive users), falls back to the
    /// per-session Local namespace — the data root is per-user anyway, so session scope is enough.
    /// </summary>
    public static bool TryAcquire(string mutexName, out SingleInstanceGuard? guard)
    {
        foreach (var candidate in MutexNames.Candidates(mutexName))
        {
            try
            {
                if (TryAcquire(candidate, out guard, static name => new NamedMutexBackend(name)))
                {
                    return true;
                }

                guard = null;
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                // this token cannot create the Global namespace object; try the next candidate
            }
        }

        guard = null;
        return false;
    }

    public static bool TryAcquire(
        string mutexName,
        out SingleInstanceGuard? guard,
        Func<string, ISingleInstanceBackend> backendFactory)
    {
        var backend = backendFactory(mutexName);
        try
        {
            if (!backend.TryAcquire(out var recovered))
            {
                backend.Dispose();
                guard = null;
                return false;
            }

            guard = new SingleInstanceGuard(mutexName, backend, recovered);
            return true;
        }
        catch
        {
            backend.Dispose();
            throw;
        }
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        try
        {
            _backend.Release();
        }
        finally
        {
            _backend.Dispose();
        }
    }
}

/// <summary>Mutex names used by the single-instance guard (ADR-0001 D3 + unprivileged fallback).</summary>
public static class MutexNames
{
    public const string GlobalDefault = @"Global\NewManga.Host";
    public const string LocalFallback = @"Local\NewManga.Host";

    public static IReadOnlyList<string> Candidates(string primaryName) =>
        string.Equals(primaryName, GlobalDefault, StringComparison.OrdinalIgnoreCase)
            ? new[] { GlobalDefault, LocalFallback }
            : new[] { primaryName };
}

public interface ISingleInstanceBackend : IDisposable
{
    bool TryAcquire(out bool recoveredAbandoned);

    void Release();
}

/// <summary>
/// Production backend. Ownership of a Win32 mutex is thread-affine, so the mutex is acquired and
/// released on a dedicated background thread. That keeps the guard safe no matter which threadpool
/// thread happens to run HostRuntime.StartAsync/DisposeAsync.
/// </summary>
public sealed class NamedMutexBackend : ISingleInstanceBackend
{
    private readonly Mutex _mutex;
    private readonly Thread _ownerThread;
    private readonly ManualResetEventSlim _attempted = new(false);
    private readonly ManualResetEventSlim _shouldRelease = new(false);
    private bool _acquired;
    private bool _recovered;
    private bool _disposed;

    public NamedMutexBackend(string name)
    {
        _mutex = new Mutex(initiallyOwned: false, name);
        _ownerThread = new Thread(OwnerLoop)
        {
            IsBackground = true,
            Name = "NewManga.Host.SingleInstance",
        };
        _ownerThread.Start();
    }

    public bool TryAcquire(out bool recoveredAbandoned)
    {
        _attempted.Wait(TimeSpan.FromSeconds(10));
        recoveredAbandoned = _recovered;
        return _acquired;
    }

    public void Release()
    {
        if (!_acquired)
        {
            return;
        }

        _shouldRelease.Set();
        _ownerThread.Join(TimeSpan.FromSeconds(5));
        _acquired = false;
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        Release();
        _mutex.Dispose();
        _attempted.Dispose();
        _shouldRelease.Dispose();
    }

    private void OwnerLoop()
    {
        try
        {
            try
            {
                _acquired = _mutex.WaitOne(0);
            }
            catch (AbandonedMutexException)
            {
                _acquired = true;
                _recovered = true;
            }
        }
        catch (Exception ex) when (ex is ObjectDisposedException or UnauthorizedAccessException or InvalidOperationException)
        {
            _acquired = false;
        }
        finally
        {
            _attempted.Set();
        }

        if (!_acquired)
        {
            return;
        }

        _shouldRelease.Wait(TimeSpan.FromMinutes(10));
        try
        {
            _mutex.ReleaseMutex();
        }
        catch (Exception ex) when (ex is ApplicationException or ObjectDisposedException)
        {
            // host is shutting down; the kernel releases on process exit
        }
    }
}

/// <summary>Legacy Tauri shell process detection (ADR-0001 D3: read-only mode while it runs).</summary>
public sealed record LegacyShellState(bool Detected, IReadOnlyList<int> ProcessIds)
{
    public static LegacyShellState NotDetected { get; } = new(false, Array.Empty<int>());
}

public interface IProcessNameProbe
{
    IReadOnlyList<int> FindProcessIds(string processName);
}

public sealed class SystemProcessNameProbe : IProcessNameProbe
{
    public const string LegacyShellProcessName = "new-manga";

    public IReadOnlyList<int> FindProcessIds(string processName)
    {
        var ids = new List<int>();
        foreach (var process in Process.GetProcessesByName(processName))
        {
            using (process)
            {
                ids.Add(process.Id);
            }
        }

        return ids;
    }
}

public sealed class LegacyShellDetector
{
    public const string LegacyShellProcessName = SystemProcessNameProbe.LegacyShellProcessName;

    private readonly IProcessNameProbe _probe;

    public LegacyShellDetector(IProcessNameProbe? probe = null)
    {
        _probe = probe ?? new SystemProcessNameProbe();
    }

    public LegacyShellState Detect()
    {
        var ids = _probe.FindProcessIds(LegacyShellProcessName);
        return ids.Count == 0 ? LegacyShellState.NotDetected : new LegacyShellState(true, ids);
    }
}
