namespace NewManga.Presentation.Avalonia.Lifecycle;

/// <summary>Result of an exit request; <see cref="Allowed"/> false carries a user-facing reason.</summary>
public sealed record ExitDecision(bool Allowed, string? Reason);

/// <summary>
/// FEA-07 process-level exit coordination (proposal §7.3): any UI's window close must ask this
/// coordinator instead of disposing the Host; the coordinator blocks exit while unsaved edits or runs
/// are pending. It never touches Host lifecycle itself.
/// </summary>
public sealed class ExitCoordinator
{
    private readonly HashSet<string> _pendingEdits = new(StringComparer.Ordinal);
    private readonly HashSet<string> _activeRuns = new(StringComparer.Ordinal);
    private readonly object _sync = new();

    /// <summary>Registers a pending (unsaved) edit; returns a token to complete it later.</summary>
    public string RegisterPendingEdit(string id)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
        lock (_sync)
        {
            if (!_pendingEdits.Add(id))
            {
                throw new InvalidOperationException($"pending edit '{id}' is already registered");
            }

            return id;
        }
    }

    /// <summary>Completes (saves/discards) a pending edit.</summary>
    public bool CompletePendingEdit(string id)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
        lock (_sync)
        {
            return _pendingEdits.Remove(id);
        }
    }

    /// <summary>Registers an active run; returns a token to complete it later.</summary>
    public string RegisterActiveRun(string id)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
        lock (_sync)
        {
            if (!_activeRuns.Add(id))
            {
                throw new InvalidOperationException($"active run '{id}' is already registered");
            }

            return id;
        }
    }

    /// <summary>Completes a run (finished/failed/cancelled).</summary>
    public bool CompleteActiveRun(string id)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
        lock (_sync)
        {
            return _activeRuns.Remove(id);
        }
    }

    /// <summary>Evaluates whether the process may exit now; does not perform the exit.</summary>
    public ExitDecision RequestExit()
    {
        lock (_sync)
        {
            if (_pendingEdits.Count > 0)
            {
                return new ExitDecision(false, $"unsaved edits: {_pendingEdits.Count}");
            }

            if (_activeRuns.Count > 0)
            {
                return new ExitDecision(false, $"active runs: {_activeRuns.Count}");
            }

            return new ExitDecision(true, null);
        }
    }
}
