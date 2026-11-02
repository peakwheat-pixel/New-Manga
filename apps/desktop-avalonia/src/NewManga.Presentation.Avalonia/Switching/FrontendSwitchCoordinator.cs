using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.Presentation.Avalonia.Switching;

/// <summary>A frontend switch request (FEA-07 / proposal §7.1).</summary>
public sealed record SwitchRequest(string TargetFrontendId, string PreviousFrontendId);

/// <summary>The composition-root supplied steps of one switch (content tree hosting belongs to the app).</summary>
public sealed class SwitchCallbacks
{
    public required Func<CancellationToken, Task> ValidateAsync { get; init; }

    public required Func<CancellationToken, Task> BuildTreeAsync { get; init; }

    public required Func<CancellationToken, Task> CommitAsync { get; init; }

    public required Func<CancellationToken, Task> RollbackAsync { get; init; }

    /// <summary>Real layout gate: the replacement tree completed layout with valid geometry.</summary>
    public Func<CancellationToken, Task>? LayoutAsync { get; init; }

    /// <summary>Real loaded gate: Loaded callbacks completed after the tree entered a visual tree.</summary>
    public Func<CancellationToken, Task>? LoadedAsync { get; init; }

    /// <summary>Real rendered gate: at least one frame can be rendered before the swap is committed.</summary>
    public Func<CancellationToken, Task>? RenderedAsync { get; init; }

    /// <summary>Optional stage observer for diagnostics/evidence.</summary>
    public Action<SwitchStage>? OnStage { get; init; }
}

/// <summary>The outcome of one switch attempt; a failed switch is always rolled back.</summary>
public sealed record SwitchResult(
    bool Succeeded,
    SwitchStage FinalStage,
    string? Failure,
    bool RolledBack);

/// <summary>
/// FEA-07 switch transaction: validate → build replacement tree → layout → loaded → rendered → commit,
/// with a durable journal and a rollback to the previous UI on any failure (§7.1/§15.5). The actual UI
/// callbacks are supplied by the app composition root so this module stays UI-toolkit-light and testable.
/// </summary>
public sealed class FrontendSwitchCoordinator
{
    private readonly SwitchJournal _journal;
    private readonly Func<SwitchStage, Exception?>? _faultInjector;
    private readonly Action? _beforeJournalCommit;
    private readonly SemaphoreSlim _gate = new(1, 1);

    public FrontendSwitchCoordinator(
        SwitchJournal journal,
        Func<SwitchStage, Exception?>? faultInjector = null,
        Action? beforeJournalCommit = null)
    {
        _journal = journal ?? throw new ArgumentNullException(nameof(journal));
        _faultInjector = faultInjector;
        _beforeJournalCommit = beforeJournalCommit;
    }

    /// <summary>True when the previous run left an in-flight switch that must be rolled back at startup.</summary>
    public bool TryRecoverInterrupted(out SwitchJournalEntry? entry) => _journal.HasInterruptedSwitch(out entry);

    /// <summary>
    /// Runs one switch attempt. The journal is started before any UI work and rolled back on failure;
    /// concurrent attempts are serialized (a second switch waits instead of interleaving content trees).
    /// </summary>
    public async Task<SwitchResult> SwitchAsync(
        SwitchRequest request,
        SwitchCallbacks callbacks,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        ArgumentNullException.ThrowIfNull(callbacks);
        ArgumentException.ThrowIfNullOrWhiteSpace(request.TargetFrontendId);

        await _gate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var stages = new (SwitchStage Stage, Func<CancellationToken, Task> Step)[]
            {
                (SwitchStage.Preparing, callbacks.ValidateAsync),
                (SwitchStage.Building, callbacks.BuildTreeAsync),
                (SwitchStage.Layout, callbacks.LayoutAsync ?? NoOpAsync),
                (SwitchStage.Loaded, callbacks.LoadedAsync ?? NoOpAsync),
                (SwitchStage.Rendered, callbacks.RenderedAsync ?? NoOpAsync),
                (SwitchStage.Committed, callbacks.CommitAsync),
            };

            _journal.Begin(request.TargetFrontendId, request.PreviousFrontendId);

            var current = SwitchStage.Preparing;
            try
            {
                foreach (var (stage, step) in stages)
                {
                    current = stage;
                    if (Fault(stage) is { } injected)
                    {
                        throw injected;
                    }

                    cancellationToken.ThrowIfCancellationRequested();
                    await step(cancellationToken).ConfigureAwait(false);
                    if (stage is not (SwitchStage.Preparing or SwitchStage.Committed))
                    {
                        _journal.Advance(stage);
                    }

                    callbacks.OnStage?.Invoke(stage);
                }

                _beforeJournalCommit?.Invoke();
                _journal.Commit();
                return new SwitchResult(Succeeded: true, SwitchStage.Committed, Failure: null, RolledBack: false);
            }
            catch (Exception ex) when (ex is not OperationCanceledException || !cancellationToken.IsCancellationRequested)
            {
                var failure = $"{current}: {ex.GetType().Name}: {ex.Message}";
                // R-015: the app-side compensation must run even if the journal rollback write fails.
                var journalRolledBack = true;
                try
                {
                    _journal.Rollback(failure);
                }
                catch (Exception journalError) when (journalError is IOException or InvalidOperationException or UnauthorizedAccessException)
                {
                    journalRolledBack = false;
                }

                var rolledBack = await TryRollbackAsync(callbacks, cancellationToken).ConfigureAwait(false) && journalRolledBack;
                callbacks.OnStage?.Invoke(SwitchStage.RolledBack);
                return new SwitchResult(Succeeded: false, current, failure, rolledBack);
            }
            catch (OperationCanceledException)
            {
                try
                {
                    _journal.Rollback("cancelled");
                }
                catch (Exception journalError) when (journalError is IOException or InvalidOperationException or UnauthorizedAccessException)
                {
                    // best-effort: cancellation still rolls the UI back below
                }
                await TryRollbackAsync(callbacks, CancellationToken.None).ConfigureAwait(false);
                callbacks.OnStage?.Invoke(SwitchStage.RolledBack);
                throw;
            }
        }
        finally
        {
            _gate.Release();
        }
    }

    private Exception? Fault(SwitchStage stage)
    {
        if (_faultInjector is null)
        {
            return null;
        }

        return _faultInjector(stage);
    }

    private static async Task<bool> TryRollbackAsync(SwitchCallbacks callbacks, CancellationToken cancellationToken)
    {
        try
        {
            await callbacks.RollbackAsync(cancellationToken).ConfigureAwait(false);
            return true;
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return false;
        }
    }

    private static Task NoOpAsync(CancellationToken cancellationToken) => Task.CompletedTask;
}
