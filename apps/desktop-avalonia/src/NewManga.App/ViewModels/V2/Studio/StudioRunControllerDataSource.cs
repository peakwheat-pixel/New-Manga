using NewManga.App.Services;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// V11R-B-4: the real adapter from the merged <see cref="IRunController"/> (V11R-A-2) to the Studio's
/// own <see cref="IRunDataSource"/> seam. Only the projection read face is used: the matrix state always
/// comes from <c>GetTaskProjection</c>, never from a local guess (SCREEN_SPECS §4).
/// </summary>
public sealed class RunControllerRunDataSource : IRunDataSource
{
    private readonly IRunController _controller;
    private readonly Func<string?> _runIdProvider;

    public RunControllerRunDataSource(IRunController controller, Func<string?> runIdProvider)
    {
        _controller = controller;
        _runIdProvider = runIdProvider;
    }

    public bool IsWired => true;

    /// <summary>Number of projection reads issued (evidence: polling actually polls).</summary>
    public int ReadCount { get; private set; }

    public async Task<StudioRunProjection?> GetProjectionAsync(
        string? chapterId,
        CancellationToken cancellationToken = default)
    {
        var runId = _runIdProvider();
        if (string.IsNullOrWhiteSpace(runId))
        {
            return null;
        }

        ReadCount++;
        var projection = await _controller.GetTaskProjectionAsync(runId, cancellationToken).ConfigureAwait(true);
        return projection is null ? null : Map(projection);
    }

    /// <summary>
    /// Maps the frozen <c>TaskProjectionInfo</c>. Stage columns are taken verbatim from
    /// <c>step_flow</c> (dynamic — never a hard-coded ten); unknown Core states map to null so the cell
    /// renders "no projection" instead of an invented state.
    /// </summary>
    public static StudioRunProjection Map(TaskProjectionInfo info)
    {
        var stages = info.StepFlow
            .Where(step => !string.IsNullOrWhiteSpace(step.Type))
            .Select(step => new StudioRunStageState(
                step.Type,
                string.IsNullOrWhiteSpace(step.Label) ? step.Type : step.Label,
                step.State,
                StudioStates.FromProjectionStatus(step.State)))
            .ToList();

        var stepsByPage = info.Tasks
            .GroupBy(task => task.PageId, StringComparer.Ordinal)
            .ToDictionary(
                group => group.Key,
                group => (IReadOnlyList<StudioRunStepState>)group
                    .SelectMany(task => task.Steps)
                    .Where(step => !string.IsNullOrWhiteSpace(step.StepType))
                    .Select(step => new StudioRunStepState(
                        step.StepType,
                        step.Status,
                        StudioStates.FromProjectionStatus(step.Status),
                        step.ErrorCode))
                    .ToList(),
                StringComparer.Ordinal);

        var rows = info.Rows
            .Select(row => new StudioRunPageRow(
                row.PageId,
                row.PageOrder ?? 0,
                string.IsNullOrWhiteSpace(row.Filename) ? null : row.Filename,
                row.Status,
                StudioStates.FromProjectionStatus(row.Status),
                row.IsLocked,
                row.IsPipelineCurrent,
                row.ErrorCode,
                stepsByPage.TryGetValue(row.PageId, out var steps) ? steps : Array.Empty<StudioRunStepState>()))
            .OrderBy(row => row.PageOrder)
            .ThenBy(row => row.PageId, StringComparer.Ordinal)
            .ToList();

        var counts = info.Counts;
        var total = counts.Total ?? rows.Count;
        return new StudioRunProjection(
            info.RunId,
            info.RunStatus,
            string.IsNullOrWhiteSpace(info.RunTitle) ? info.RunId : info.RunTitle,
            Math.Clamp(info.OverallProgress ?? 0, 0, 1),
            info.CurrentPageId,
            info.CurrentStepType,
            stages,
            rows,
            total,
            counts.Completed ?? rows.Count(row => row.State == StudioStateKind.Done),
            counts.Failed ?? rows.Count(row => row.State == StudioStateKind.Failed),
            counts.Skipped ?? rows.Count(row => row.State == StudioStateKind.Skipped),
            counts.Blocked ?? rows.Count(row => row.State == StudioStateKind.Blocked),
            counts.Waiting ?? rows.Count(row => row.State == StudioStateKind.Queued),
            counts.Processing ?? rows.Count(row => row.State == StudioStateKind.Running))
        {
            Controls = new StudioRunControls(
                info.Controls.CanPause,
                info.Controls.CanStop,
                info.Controls.CanContinue,
                info.Controls.CanRestart,
                info.Controls.CanAbandon,
                info.Controls.CanRetryFailed),
            BlockedReasons = info.BlockedReasons.ToList(),
        };
    }
}

/// <summary>Control availability exactly as the Core projected it (never re-derived in the UI).</summary>
public sealed record StudioRunControls(
    bool CanPause,
    bool CanStop,
    bool CanContinue,
    bool CanRestart,
    bool CanAbandon,
    bool CanRetryFailed);
