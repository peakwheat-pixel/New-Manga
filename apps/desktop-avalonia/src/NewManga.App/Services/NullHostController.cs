using System.Globalization;
using NewManga.CoreClient;

namespace NewManga.App.Services;

/// <summary>
/// Inert controller used by the XAML runtime loader / visual designers. It never starts a sidecar;
/// production always constructs <see cref="HostController"/>.
/// </summary>
public sealed class NullHostController : IHostController
{
    public static NullHostController Instance { get; } = new();

    private int _createdChapters;

    private NullHostController()
    {
    }

    public HostViewSnapshot Snapshot { get; } = new(
        HostViewState.Starting,
        "设计时占位",
        "—",
        null,
        null,
        Array.Empty<BookSummary>(),
        0,
        true,
        null);

    public event EventHandler? Changed
    {
        add { }
        remove { }
    }

    public Task StartAsync(CancellationToken cancellationToken = default) => Task.CompletedTask;

    public Task RefreshBooksAsync(CancellationToken cancellationToken = default) => Task.CompletedTask;

    public Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default) =>
        Task.FromResult(false);

    /// <summary>
    /// V11R-A-1 (contract §5.1): deterministic fake for UI tests — a valid call returns an
    /// incrementing chapter (<c>null-chapter-1</c>, <c>null-chapter-2</c>, …), while a blank argument
    /// or a cancelled token returns null exactly like the production failure channel. The counter
    /// only advances on success, so assertions stay stable across failed probes. Never throws.
    /// </summary>
    public Task<ChapterSummary?> CreateChapterAsync(
        string bookId,
        string title,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId) ||
            string.IsNullOrWhiteSpace(title) ||
            cancellationToken.IsCancellationRequested)
        {
            return Task.FromResult<ChapterSummary?>(null);
        }

        var order = Interlocked.Increment(ref _createdChapters);
        var number = order.ToString(CultureInfo.InvariantCulture);
        return Task.FromResult<ChapterSummary?>(
            new ChapterSummary($"null-chapter-{number}", title, number, order));
    }

    public Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default) =>
        Task.FromResult(false);

    public Task<ReaderBookData?> LoadReaderBookAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<ReaderBookData?>(null);

    public Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(
        string bookId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<ChapterSummary>>(Array.Empty<ChapterSummary>());

    // READER-WORKBENCH-1: the designer/inert path never has a Core, so reads stay empty/null and every
    // write reports HOST_NOT_READY (the real Host is the only writer).
    public Task<IReadOnlyList<ChapterPageSummary>> ListChapterPagesAsync(
        string chapterId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<ChapterPageSummary>>(Array.Empty<ChapterPageSummary>());

    public Task<RegionPageProjection?> LoadPageRegionsAsync(
        string pageId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<RegionPageProjection?>(null);

    public Task<RegionRevisionHistory?> LoadRegionRevisionsAsync(
        string regionId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<RegionRevisionHistory?>(null);

    public Task<byte[]?> ReadPageImageAsync(
        string pageId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<byte[]?>(null);

    public Task<RegionOperationResult> SetRegionTypeAsync(
        string regionId,
        string newRegionType,
        int expectedRevision,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(RegionOperationResult.NotReady());

    public Task<RegionOperationResult> RestoreRegionRevisionAsync(
        string regionId,
        int revisionNo,
        int expectedRevision,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(RegionOperationResult.NotReady());

    public Task<PageRerenderOutcome> RerenderPageAsync(
        string pageId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(PageRerenderOutcome.NotReady());

    public Task<IReadOnlyList<CredentialTargetOption>> ListCredentialTargetsAsync(
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<CredentialTargetOption>>(Array.Empty<CredentialTargetOption>());

    public Task<CredentialOperationResult> PutCredentialAsync(
        string kind,
        string ownerId,
        string intent,
        string secret,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(CredentialOperationResult.NotReady());

    public Task<CredentialOperationResult> ClearCredentialAsync(
        string kind,
        string ownerId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(CredentialOperationResult.NotReady());

    // SETTINGS-PROFILE-UI-1: designer/inert path — no Host, so lists stay empty and mutations report
    // HOST_NOT_READY instead of pretending to succeed.
    public Task<IReadOnlyList<ProviderProfileInfo>> ListProviderProfilesAsync(
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<ProviderProfileInfo>>(Array.Empty<ProviderProfileInfo>());

    public Task<SettingsProfileResult> SaveProviderProfileAsync(
        string? profileId,
        ProviderProfileDraft draft,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(SettingsProfileResult.NotReady());

    public Task<SettingsProfileResult> DeleteProviderProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(SettingsProfileResult.NotReady());

    public Task<IReadOnlyList<NetworkProfileInfo>> ListNetworkProfilesAsync(
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<NetworkProfileInfo>>(Array.Empty<NetworkProfileInfo>());

    public Task<SettingsProfileResult> SaveNetworkProfileAsync(
        string? networkProfileId,
        NetworkProfileDraft draft,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(SettingsProfileResult.NotReady());

    public Task<SettingsProfileResult> DeleteNetworkProfileAsync(
        string networkProfileId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(SettingsProfileResult.NotReady());

    public Task<SettingsProfileResult> SetNetworkDefaultAsync(
        string? networkProfileId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(SettingsProfileResult.NotReady());

    public Task<NetworkTestInfo?> TestNetworkProfileAsync(
        string networkProfileId,
        string providerProfileId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<NetworkTestInfo?>(null);

    public Task<NetworkResolveInfo?> ResolveNetworkProfileAsync(
        string? providerProfileId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<NetworkResolveInfo?>(null);

    public Task<SettingsProfileResult> SetProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        string profileId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(SettingsProfileResult.NotReady());

    public Task<SettingsProfileResult> ClearProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(SettingsProfileResult.NotReady());

    public Task<ProviderBindingResult?> ResolveProviderBindingAsync(
        string capability,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<ProviderBindingResult?>(null);

    public Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(ReaderProgressSaveResult.NotReady());

    // IMPORT-EXPORT-UI-1: the designer/inert shell never imports or exports anything; every entry
    // reports the typed "not ready" outcome instead of pretending to succeed.
    public string ExportDirectorySuggestion => string.Empty;

    public Task<ImportOutcome> ImportFilesAsync(
        string chapterId,
        IReadOnlyList<string> paths,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default) =>
        Task.FromResult(ImportOutcome.NotReady());

    public Task<ImportOutcome> ImportFolderAsync(
        string chapterId,
        string folderPath,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default) =>
        Task.FromResult(ImportOutcome.NotReady());

    public Task<IReadOnlyList<string>> GetTranslatedPageIdsAsync(
        string chapterId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<string>>(Array.Empty<string>());

    public Task<ExportStartInfo?> StartExportAsync(
        string bookId,
        string chapterId,
        IReadOnlyList<string> orderedPageIds,
        string targetPath,
        string format = "zip",
        string? pdfContent = null,
        string? stalePolicy = null,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<ExportStartInfo?>(null);

    public Task<ExportSnapshotInfo?> GetExportSnapshotAsync(
        string exportId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<ExportSnapshotInfo?>(null);

    public Task<IReadOnlyList<ExportHistoryEntry>> GetExportHistoryAsync(
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<ExportHistoryEntry>>(Array.Empty<ExportHistoryEntry>());

    public Task<ExportSnapshotInfo?> CancelExportAsync(
        string exportId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<ExportSnapshotInfo?>(null);

    public Task<bool> RevealExportFolderAsync(
        string exportId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(false);

    public ValueTask DisposeAsync() => ValueTask.CompletedTask;

    // ---------------------------------------------------------------------------------------
    // V11R-A-2 (contract §5.2): deterministic Run fake for UI tests. A tiny in-memory run table
    // keeps a dialog/queue page drivable without a Core; no progress is fabricated (unknown counters
    // stay null, no invented targets/rows) and the transitions are the Core's frozen table.
    // ---------------------------------------------------------------------------------------

    private readonly object _runGate = new();
    private readonly Dictionary<string, NullRun> _runs = new(StringComparer.Ordinal);
    private readonly Dictionary<string, (string Payload, string RunId)> _startRunKeys = new(StringComparer.Ordinal);
    private int _runSequence;

    private sealed class NullRun
    {
        public required string RunId { get; init; }

        public required string Command { get; init; }

        public required RunStartRequest Request { get; init; }

        public string Status { get; set; } = "pending";
    }

    public Task<RunStartInfo?> StartRunAsync(RunStartRequest request, CancellationToken ct = default)
    {
        if (request is null ||
            string.IsNullOrWhiteSpace(request.Command) ||
            request.Scope is null ||
            string.IsNullOrWhiteSpace(request.IdempotencyKey) ||
            ct.IsCancellationRequested)
        {
            return Task.FromResult<RunStartInfo?>(null);
        }

        var payload = RunPayloads.StartRun(request).GetRawText();
        lock (_runGate)
        {
            if (_startRunKeys.TryGetValue(request.IdempotencyKey, out var accepted))
            {
                // Same key + same request fingerprint reuses the accepted run; a different request
                // under the same key is the Core's IDEMPOTENCY_KEY_REUSED case.
                return Task.FromResult<RunStartInfo?>(
                    string.Equals(accepted.Payload, payload, StringComparison.Ordinal)
                        ? new RunStartInfo(accepted.RunId, _runs[accepted.RunId].Status)
                        : null);
            }

            var run = new NullRun
            {
                RunId = "null-run-" + (++_runSequence).ToString(CultureInfo.InvariantCulture),
                Command = request.Command,
                Request = request,
            };
            _runs[run.RunId] = run;
            _startRunKeys[request.IdempotencyKey] = (payload, run.RunId);
            return Task.FromResult<RunStartInfo?>(new RunStartInfo(run.RunId, run.Status));
        }
    }

    public Task<RunControlInfo?> ControlRunAsync(
        string runId,
        RunControlAction action,
        string? idempotencyKey = null,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId) ||
            (action == RunControlAction.Restart && string.IsNullOrWhiteSpace(idempotencyKey)) ||
            ct.IsCancellationRequested)
        {
            return Task.FromResult<RunControlInfo?>(null);
        }

        lock (_runGate)
        {
            if (!_runs.TryGetValue(runId, out var run))
            {
                return Task.FromResult<RunControlInfo?>(null);
            }

            // Core control_run table (src/application/tasks/service.py): pause←running,
            // continue←paused, stop←pending/running/paused/blocked, restart←undisposed interrupted.
            var next = action switch
            {
                RunControlAction.Pause when run.Status == "running" => "paused",
                RunControlAction.Resume when run.Status == "paused" => "running",
                RunControlAction.Stop when run.Status is "pending" or "running" or "paused" or "blocked" => "cancelled",
                _ => null,
            };
            if (next is null)
            {
                return Task.FromResult<RunControlInfo?>(null);
            }

            run.Status = next;
            return Task.FromResult<RunControlInfo?>(new RunControlInfo(run.RunId, run.Status));
        }
    }

    public Task<RunControlInfo?> ResumeBlockedRunAsync(string runId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId) || ct.IsCancellationRequested)
        {
            return Task.FromResult<RunControlInfo?>(null);
        }

        lock (_runGate)
        {
            if (!_runs.TryGetValue(runId, out var run) || run.Status != "blocked")
            {
                return Task.FromResult<RunControlInfo?>(null);
            }

            run.Status = "running";
            return Task.FromResult<RunControlInfo?>(new RunControlInfo(run.RunId, run.Status));
        }
    }

    public Task<RunSnapshotInfo?> GetRunSnapshotAsync(string runId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId) || ct.IsCancellationRequested)
        {
            return Task.FromResult<RunSnapshotInfo?>(null);
        }

        lock (_runGate)
        {
            return Task.FromResult(
                _runs.TryGetValue(runId, out var run)
                    ? new RunSnapshotInfo(
                        run.RunId,
                        run.Command,
                        NullScopeOf(run.Request.Scope),
                        run.Status,
                        Array.Empty<RunTargetInfo>())
                    : null);
        }
    }

    public Task<TaskProjectionInfo?> GetTaskProjectionAsync(string runId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId) || ct.IsCancellationRequested)
        {
            return Task.FromResult<TaskProjectionInfo?>(null);
        }

        lock (_runGate)
        {
            if (!_runs.TryGetValue(runId, out var run))
            {
                return Task.FromResult<TaskProjectionInfo?>(null);
            }

            // Honest empty projection: the fake has no pages, so rows/tasks stay empty and the
            // counters stay null (unknown) instead of a plausible-looking zero.
            return Task.FromResult<TaskProjectionInfo?>(new TaskProjectionInfo(
                run.RunId,
                run.Status,
                null,
                null,
                null,
                null,
                Array.Empty<RunStepFlowInfo>(),
                Array.Empty<RunRowInfo>(),
                Array.Empty<RunTaskInfo>(),
                new RunCountsInfo(),
                Array.Empty<string>(),
                NullControlsFor(run.Status)));
        }
    }

    public Task<RunControlInfo?> RetryFailedTargetsAsync(
        string runId,
        string idempotencyKey,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId) ||
            string.IsNullOrWhiteSpace(idempotencyKey) ||
            ct.IsCancellationRequested)
        {
            return Task.FromResult<RunControlInfo?>(null);
        }

        lock (_runGate)
        {
            if (!_runs.TryGetValue(runId, out var run) || run.Status != "completed_with_failures")
            {
                return Task.FromResult<RunControlInfo?>(null);
            }

            var child = new NullRun
            {
                RunId = "null-run-" + (++_runSequence).ToString(CultureInfo.InvariantCulture),
                Command = run.Command,
                Request = run.Request,
            };
            _runs[child.RunId] = child;
            return Task.FromResult<RunControlInfo?>(new RunControlInfo(child.RunId, child.Status));
        }
    }

    private static RunScopeInfo NullScopeOf(IReadOnlyDictionary<string, object?> scope)
    {
        string? ReadText(string key) =>
            scope.TryGetValue(key, out var value) && value is string text ? text : null;

        IReadOnlyList<string>? pageIds = null;
        if (scope.TryGetValue("page_ids", out var ids) && ids is IEnumerable<string> items)
        {
            pageIds = items.ToList();
        }

        return new RunScopeInfo(
            ReadText("kind") ?? string.Empty,
            ReadText("book_id"),
            ReadText("chapter_id"),
            ReadText("page_id"),
            ReadText("region_id"),
            pageIds);
    }

    private static RunControlsInfo NullControlsFor(string status) => new(
        CanPause: status == "running",
        CanStop: status is "pending" or "running" or "paused" or "blocked",
        CanContinue: status == "paused",
        CanRestart: false,
        CanAbandon: false,
        CanRetryFailed: status == "completed_with_failures");
}
