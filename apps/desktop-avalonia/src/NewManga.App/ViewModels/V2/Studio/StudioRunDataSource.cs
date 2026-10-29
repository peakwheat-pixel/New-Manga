namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// One stage aggregate from a run projection. <see cref="RawState"/> keeps the exact Core string
/// (<c>waiting/processing/completed/failed/skipped/blocked</c>) so the UI never loses the source
/// vocabulary; <see cref="State"/> is the mapped product state (null when the Core sent an unknown
/// value — the view then renders "no projection" rather than a guessed state).
/// </summary>
public sealed record StudioRunStageState(
    string CoreStepType,
    string Label,
    string RawState,
    StudioStateKind? State);

/// <summary>One page row of the run projection (Batch matrix row).</summary>
public sealed record StudioRunPageRow(
    string PageId,
    int PageOrder,
    string? Filename,
    string RawStatus,
    StudioStateKind? State,
    bool IsLocked,
    bool IsPipelineCurrent,
    string? ErrorCode);

/// <summary>
/// Studio-facing projection of one pipeline run. Deliberately a Studio-local DTO: the frozen
/// <c>IRunController.TaskProjectionInfo</c> (V11R-A-2) is not merged yet, and the Studio must be able
/// to render NOT_WIRED without referencing an unfinished contract type.
/// </summary>
public sealed record StudioRunProjection(
    string RunId,
    string RunStatus,
    string Title,
    double Progress,
    string? CurrentPageId,
    string? CurrentStepType,
    IReadOnlyList<StudioRunStageState> Stages,
    IReadOnlyList<StudioRunPageRow> Rows,
    int TotalPageCount,
    int CompletedPageCount,
    int FailedPageCount,
    int SkippedPageCount,
    int BlockedPageCount,
    int WaitingPageCount,
    int ProcessingPageCount)
{
    /// <summary>True when the projection has enough information to render the matrix honestly.</summary>
    public bool HasRows => Rows.Count > 0;

    /// <summary>Stages as a lookup for the Page pipeline band (Core step type → state).</summary>
    public StudioStateKind? StateForStage(StudioStage stage) =>
        stage.CoreStepType is null
            ? null
            : Stages.FirstOrDefault(item =>
                    string.Equals(item.CoreStepType, stage.CoreStepType, StringComparison.OrdinalIgnoreCase))
                ?.State;
}

/// <summary>
/// V11R-B-4 seam (defined in B-3 so the Page pipeline band can already be honest about it): the UI
/// reads run/task state only through this interface. When V11R-A-2 merges, <c>RunControllerRunDataSource</c>
/// wraps <c>IRunController.GetTaskProjectionAsync</c>; no view or view-model changes.
/// </summary>
public interface IRunDataSource
{
    /// <summary>False in this build: <c>IRunController</c> has not merged yet.</summary>
    bool IsWired { get; }

    /// <summary>Latest projection for the chapter/runs scope; null when unavailable (never invented).</summary>
    Task<StudioRunProjection?> GetProjectionAsync(
        string? chapterId,
        CancellationToken cancellationToken = default);
}

/// <summary>
/// Degradation source of this build: every call returns null, the Page pipeline band renders
/// "投影未接入 / NOT_WIRED", the Batch mode renders its NOT_WIRED empty state. It is impossible for
/// the UI to show fabricated progress because there is no fabricated data anywhere.
/// </summary>
public sealed class NotWiredRunDataSource : IRunDataSource
{
    public static NotWiredRunDataSource Instance { get; } = new();

    public bool IsWired => false;

    public int CallCount { get; private set; }

    public Task<StudioRunProjection?> GetProjectionAsync(
        string? chapterId,
        CancellationToken cancellationToken = default)
    {
        CallCount++;
        return Task.FromResult<StudioRunProjection?>(null);
    }
}

/// <summary>
/// Maps a projection onto the ten canonical band stages. A stage that the projection does not carry
/// (e.g. <c>save</c>) stays null; a stage missing from this particular command's step flow also stays
/// null (: there is no evidence either way).
/// </summary>
public static class StudioRunStageMapper
{
    public static IReadOnlyList<(StudioStage Stage, StudioStateKind? State)> MapBandStages(
        StudioRunProjection? projection)
    {
        var result = new List<(StudioStage, StudioStateKind?)>(StudioStages.Count);
        foreach (var stage in StudioStages.Canonical)
        {
            result.Add((stage, projection?.StateForStage(stage)));
        }

        return result;
    }
}
