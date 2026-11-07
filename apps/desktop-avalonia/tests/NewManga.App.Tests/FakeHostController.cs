using System.Globalization;
using System.Text.Json;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Library;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// Scriptable controller for headless UI tests (no sidecars, no window lifecycle).
/// FEA-09-UI-1: also implements <see cref="ISourceImportController"/> (the scriptable
/// referenced-import face) — that face is deliberately OUTSIDE the frozen C-07
/// <see cref="IHostController"/> inventory; see Services/SourceImportModels.cs.
/// FEA-12-UI: also implements <see cref="ITrashController"/> (the separate recycle-bin face), so
/// headless tests can script list/preview/delete frames and assert the exact frame log.
/// </summary>
public sealed class FakeHostController : IHostController, ISourceImportController, ITrashController
{
    public FakeHostController(HostViewSnapshot snapshot)
    {
        Snapshot = snapshot;
    }

    public HostViewSnapshot Snapshot { get; set; }

    public int StartCalls { get; private set; }

    /// <summary>V11R-INT-2 ordering evidence: "start" must precede the first "refresh".</summary>
    public List<string> LifecycleLog { get; } = new();

    /// <inheritdoc />
    public int StartRequests => StartCalls;

    /// <summary>V11R-INT-2 failure path: when set, StartAsync throws this typed exception once.</summary>
    public Exception? StartException { get; set; }

    public Task? StartGate { get; set; }

    public int RefreshCalls { get; private set; }

    /// <summary>V11R-INT-2 error-state test: when set, the next RefreshBooksAsync throws this typed error.</summary>
    public Exception? RefreshException { get; set; }

    /// <summary>V11R-INT-0 loading-skeleton tests: refresh waits on this gate before completing.</summary>
    public Task? SnapshotGate { get; set; }

    /// <summary>Signals that the gated refresh actually started (test can await it deterministically).</summary>
    public TaskCompletionSource<bool> SnapshotGateStarted { get; } =
        new(TaskCreationOptions.RunContinuationsAsynchronously);

    public string? LastRoundTripTitle { get; private set; }

    public event EventHandler? Changed;

    public Task StartAsync(CancellationToken cancellationToken = default)
    {
        StartCalls++;
        LifecycleLog.Add("start");
        if (StartException is { } failure)
        {
            StartException = null;
            throw failure;
        }

        return Task.CompletedTask;
    }

    public async Task RefreshBooksAsync(CancellationToken cancellationToken = default)
    {
        RefreshCalls++;
        LifecycleLog.Add("refresh");
        if (RefreshException is { } failure)
        {
            RefreshException = null;
            throw failure;
        }

        if (SnapshotGate is { } gate)
        {
            SnapshotGateStarted.TrySetResult(true);
            await gate.ConfigureAwait(false);
        }
    }

    public bool CreateBookResult { get; set; } = true;

    public Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default) => Task.FromResult(CreateBookResult);

    /// <summary>V11R-A-1: every (bookId, title) the UI asked to create, in call order.</summary>
    public List<(string BookId, string Title)> CreateChapterRequests { get; } = new();

    /// <summary>V11R-A-1: scripted results consumed in order (null scripts a refusal).</summary>
    public Queue<ChapterSummary?> ScriptedCreateChapters { get; } = new();

    public int CreateChapterCalls { get; private set; }

    /// <summary>
    /// V11R-A-1: scripted chapter creation for UI tests. Mirrors the production failure channel —
    /// blank arguments and a cancelled token return null with a typed <c>LastError</c> — and returns
    /// deterministic incrementing chapters otherwise, so a create-chapter dialog can be driven
    /// headlessly. Never throws.
    /// </summary>
    public Task<ChapterSummary?> CreateChapterAsync(
        string bookId,
        string title,
        CancellationToken cancellationToken = default)
    {
        CreateChapterCalls++;
        CreateChapterRequests.Add((bookId, title));

        if (ScriptedCreateChapters.Count > 0)
        {
            var scripted = ScriptedCreateChapters.Dequeue();
            PublishLastError(scripted is null ? "SCRIPTED_FAILURE" : null);
            return Task.FromResult(scripted);
        }

        if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(title))
        {
            PublishLastError("INVALID_REQUEST");
            return Task.FromResult<ChapterSummary?>(null);
        }

        if (cancellationToken.IsCancellationRequested)
        {
            PublishLastError("CANCELLED");
            return Task.FromResult<ChapterSummary?>(null);
        }

        var order = CreateChapterRequests.Count;
        var number = order.ToString(CultureInfo.InvariantCulture);
        PublishLastError(null);
        return Task.FromResult<ChapterSummary?>(
            new ChapterSummary($"fake-chapter-{number}", title, number, order));
    }

    private void PublishLastError(string? code)
    {
        Snapshot = Snapshot with { LastError = code };
        Changed?.Invoke(this, EventArgs.Empty);
    }

    public Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default)
    {
        LastRoundTripTitle = title;
        Snapshot = Snapshot with
        {
            LastChineseRoundTrip = Snapshot.State == HostViewState.Ready
                ? $"往返一致：{title}"
                : "只读模式：S2 parity 前禁止写生产数据",
        };
        Changed?.Invoke(this, EventArgs.Empty);
        return Task.FromResult(Snapshot.State == HostViewState.Ready);
    }

    /// <summary>READER-LIBRARY-WIRE-1: scripted reader payload (null = empty library).</summary>
    public ReaderBookData? ReaderBook { get; set; }

    public bool ReaderLoadCalled { get; private set; }

    /// <summary>
    /// REALUSE-DATA-SAFETY-6 AC1: number of reader projection reads. A progress refresh must be a
    /// real Host read, not only a re-render of a cached value, so tests assert this counter moves.
    /// </summary>
    public int ReaderLoadCount { get; private set; }

    /// <summary>READER-PROGRESS-1: last (bookId, chapterId) requested from the reader seam.</summary>
    public (string? BookId, string? ChapterId) LastReaderRequest { get; private set; }

    /// <summary>READER-PROGRESS-1: in-memory Core stand-in for per (book, chapter, mode) progress.</summary>
    public FakeProgressStore Progress { get; } = new();

    /// <summary>READER-PROGRESS-1: overrides the next save results (queue, consumed in order).</summary>
    public Queue<ReaderProgressSaveResult> ScriptedSaveResults { get; } = new();

    /// <summary>CHAPTER-SELECTOR-1: scripted books by book id (multi-book entry).</summary>
    public Dictionary<string, ReaderBookData> ReaderBooksByBookId { get; } = new(StringComparer.Ordinal);

    /// <summary>CHAPTER-SELECTOR-1: scripted books by chapter id (chapter switching).</summary>
    public Dictionary<string, ReaderBookData> ReaderBooksByChapterId { get; } = new(StringComparer.Ordinal);

    /// <summary>CHAPTER-SELECTOR-1: scripted chapter lists per book (falls back to one chapter).</summary>
    public Dictionary<string, IReadOnlyList<ChapterSummary>> ChaptersByBook { get; } = new(StringComparer.Ordinal);

    /// <summary>CHAPTER-SELECTOR-1: number of ListChaptersAsync calls (tests/evidence).</summary>
    public int ChapterListCalls { get; private set; }

    public Task<ReaderBookData?> LoadReaderBookAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default)
    {
        ReaderLoadCalled = true;
        ReaderLoadCount++;
        LastReaderRequest = (bookId, chapterId);

        // CHAPTER-SELECTOR-1: an exact chapter wins, then an exact book, then the legacy single book.
        ReaderBookData? book = null;
        if (!string.IsNullOrWhiteSpace(chapterId) && ReaderBooksByChapterId.TryGetValue(chapterId, out var chapterBook))
        {
            book = chapterBook;
        }
        else if (!string.IsNullOrWhiteSpace(bookId) && ReaderBooksByBookId.TryGetValue(bookId, out var idBook))
        {
            book = idBook;
        }

        book ??= ReaderBook;
        if (book is null)
        {
            return Task.FromResult<ReaderBookData?>(null);
        }

        if (!string.IsNullOrWhiteSpace(bookId) && !string.Equals(book.BookId, bookId, StringComparison.Ordinal))
        {
            book = book with { BookId = bookId };
        }

        if (!string.IsNullOrWhiteSpace(chapterId) && !string.Equals(book.ChapterId, chapterId, StringComparison.Ordinal))
        {
            book = book with { ChapterId = chapterId };
        }

        // Mimic the Core: resume maps the persisted page id back onto this page list.
        var saved = Progress.TryGet(book.ChapterId, "original");
        if (saved is null)
        {
            return Task.FromResult<ReaderBookData?>(book with { InitialPageIndex = 0, InitialScrollOffsetY = 0, SavedPageId = null });
        }

        var index = -1;
        for (var candidate = 0; candidate < book.Pages.Count; candidate++)
        {
            if (string.Equals(book.Pages[candidate].PageId, saved.PageId, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        // Core semantics on a shrunken/reordered chapter: unknown saved page → start from page 1.
        var initialIndex = index < 0 ? 0 : Math.Clamp(index, 0, Math.Max(0, book.Pages.Count - 1));
        return Task.FromResult<ReaderBookData?>(book with
        {
            InitialPageIndex = initialIndex,
            InitialScrollOffsetY = saved.ScrollOffsetY,
            SavedPageId = index < 0 ? null : saved.PageId,
        });
    }

    /// <summary>CHAPTER-SELECTOR-1: read-only chapter list (scripted, else one chapter from the book).</summary>
    public Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(
        string bookId,
        CancellationToken cancellationToken = default)
    {
        ChapterListCalls++;
        if (ChaptersByBook.TryGetValue(bookId, out var chapters))
        {
            return Task.FromResult(chapters);
        }

        if (ReaderBooksByBookId.TryGetValue(bookId, out var book))
        {
            return Task.FromResult<IReadOnlyList<ChapterSummary>>(new[]
            {
                new ChapterSummary(book.ChapterId, book.ChapterTitle, "1", 0),
            });
        }

        return Task.FromResult<IReadOnlyList<ChapterSummary>>(Array.Empty<ChapterSummary>());
    }

    public async Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default)
    {
        ProgressSaveCalls++;

        // REALUSE-DATA-SAFETY-7 R-001: lets a test hold a save inside the Host await so the reader
        // can be closed while the call is still pending (the concurrency window that used to NRE).
        if (SaveGate is { } gate)
        {
            SaveGate = null;
            SaveGateStarted.TrySetResult(true);
            await gate.ConfigureAwait(false);
        }

        if (ScriptedSaveResults.Count > 0)
        {
            var scripted = ScriptedSaveResults.Dequeue();
            Progress.Attempts.Add(new FakeProgressAttempt(chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta));
            return scripted;
        }

        return Progress.Save(ResolveBookForChapter(chapterId), chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta);
    }

    /// <summary>R-001: when set, the next save awaits this gate before returning a result.</summary>
    public Task? SaveGate { get; set; }

    /// <summary>R-001: signals that the gated save actually entered the Host await.</summary>
    public TaskCompletionSource<bool> SaveGateStarted { get; } =
        new(TaskCreationOptions.RunContinuationsAsynchronously);

    /// <summary>R-001: number of progress saves that reached the controller.</summary>
    public int ProgressSaveCalls { get; private set; }

    // -------------------------------------------------------------------------------------
    // CREDENTIAL-UI-1: scripted credential port. Records the exact command arguments the UI
    // would send (kind/owner/intent/secret) so headless tests can assert them; it never persists
    // the secret beyond the recorded call, mirroring the real Host (vault + opaque Core ref).
    // -------------------------------------------------------------------------------------

    /// <summary>Targets shown by the settings credential block (state configured|missing).</summary>
    public List<CredentialTargetOption> CredentialTargets { get; } = new();

    /// <summary>Every <c>credential_put</c> the UI issued, in order (kind, owner, intent, secret).</summary>
    public List<(string Kind, string OwnerId, string Intent, string Secret)> PutCredentialCalls { get; } = new();

    /// <summary>Every <c>credential_clear</c> the UI issued (kind, owner).</summary>
    public List<(string Kind, string OwnerId)> ClearCredentialCalls { get; } = new();

    /// <summary>Scripted results consumed by put calls; default = configured (state updated).</summary>
    public Queue<CredentialOperationResult> ScriptedPutResults { get; } = new();

    /// <summary>Scripted results consumed by clear calls; default = cleared (state updated).</summary>
    public Queue<CredentialOperationResult> ScriptedClearResults { get; } = new();

    public int CredentialListCalls { get; private set; }

    public Task<IReadOnlyList<CredentialTargetOption>> ListCredentialTargetsAsync(
        CancellationToken cancellationToken = default)
    {
        CredentialListCalls++;
        return Task.FromResult<IReadOnlyList<CredentialTargetOption>>(CredentialTargets.ToList());
    }

    public Task<CredentialOperationResult> PutCredentialAsync(
        string kind,
        string ownerId,
        string intent,
        string secret,
        CancellationToken cancellationToken = default)
    {
        PutCredentialCalls.Add((kind, ownerId, intent, secret));
        var result = ScriptedPutResults.Count > 0
            ? ScriptedPutResults.Dequeue()
            : CredentialOperationResult.Configured();
        if (result.Status == CredentialOperationStatus.Configured)
        {
            UpdateCredentialState(kind, ownerId, "configured");
        }

        return Task.FromResult(result);
    }

    public Task<CredentialOperationResult> ClearCredentialAsync(
        string kind,
        string ownerId,
        CancellationToken cancellationToken = default)
    {
        ClearCredentialCalls.Add((kind, ownerId));
        var result = ScriptedClearResults.Count > 0
            ? ScriptedClearResults.Dequeue()
            : CredentialOperationResult.Cleared();
        if (result.Status == CredentialOperationStatus.Cleared)
        {
            UpdateCredentialState(kind, ownerId, "missing");
        }

        return Task.FromResult(result);
    }

    private void UpdateCredentialState(string kind, string ownerId, string state)
    {
        for (var index = 0; index < CredentialTargets.Count; index++)
        {
            var target = CredentialTargets[index];
            if (string.Equals(target.Kind, kind, StringComparison.Ordinal) &&
                string.Equals(target.OwnerId, ownerId, StringComparison.Ordinal))
            {
                CredentialTargets[index] = target with { CredentialState = state };
            }
        }
    }

    // -------------------------------------------------------------------------------------
    // SETTINGS-PROFILE-UI-1: scripted P15 profile port. Records the exact call arguments the UI
    // sends; default mutations succeed and update the visible lists (unless a scripted result says
    // otherwise). Test/resolve default to null = "unavailable, never fabricated".
    // -------------------------------------------------------------------------------------

    public List<ProviderProfileInfo> ProviderProfiles { get; } = new();

    public List<NetworkProfileInfo> NetworkProfiles { get; } = new();

    public List<(string? ProfileId, ProviderProfileDraft Draft)> ProviderSaves { get; } = new();

    public List<(string? NetworkProfileId, NetworkProfileDraft Draft)> NetworkSaves { get; } = new();

    public List<string> ProviderDeletes { get; } = new();

    public List<string> NetworkDeletes { get; } = new();

    public List<string?> NetworkDefaults { get; } = new();

    public List<(string NetworkProfileId, string ProviderProfileId)> NetworkTests { get; } = new();

    public List<string?> NetworkResolves { get; } = new();

    public List<(ProfileBindingScope Scope, string Capability, string ProfileId)> BindingSets { get; } = new();

    public List<(ProfileBindingScope Scope, string Capability)> BindingClears { get; } = new();

    public Queue<SettingsProfileResult> ScriptedProviderSaveResults { get; } = new();

    public Queue<SettingsProfileResult> ScriptedNetworkSaveResults { get; } = new();

    public Queue<SettingsProfileResult> ScriptedDeleteResults { get; } = new();

    public Queue<SettingsProfileResult> ScriptedDefaultResults { get; } = new();

    public Queue<NetworkTestInfo?> ScriptedNetworkTestResults { get; } = new();

    public Queue<NetworkResolveInfo?> ScriptedNetworkResolveResults { get; } = new();

    public Queue<SettingsProfileResult> ScriptedBindingResults { get; } = new();

    public Queue<ProviderBindingResult?> ScriptedBindingResolveResults { get; } = new();

    public int ProviderProfileListCalls { get; private set; }

    public int NetworkProfileListCalls { get; private set; }

    public Task<IReadOnlyList<ProviderProfileInfo>> ListProviderProfilesAsync(
        CancellationToken cancellationToken = default)
    {
        ProviderProfileListCalls++;
        return Task.FromResult<IReadOnlyList<ProviderProfileInfo>>(ProviderProfiles.ToList());
    }

    public Task<SettingsProfileResult> SaveProviderProfileAsync(
        string? profileId,
        ProviderProfileDraft draft,
        CancellationToken cancellationToken = default)
    {
        ProviderSaves.Add((profileId, draft));
        var result = ScriptedProviderSaveResults.Count > 0
            ? ScriptedProviderSaveResults.Dequeue()
            : SettingsProfileResult.Success(profileId is null ? "provider profile 已创建" : "provider profile 已更新");
        if (result.IsSuccess)
        {
            var id = profileId ?? "provider-" + (ProviderProfiles.Count + 1);
            var entry = new ProviderProfileInfo(
                id,
                draft.ProviderId,
                draft.DisplayName,
                draft.Capabilities,
                draft.Endpoint,
                draft.Model,
                draft.NetworkProfileId,
                draft.Enabled,
                "missing");
            var index = ProviderProfiles.FindIndex(item => string.Equals(item.ProfileId, id, StringComparison.Ordinal));
            if (index >= 0)
            {
                ProviderProfiles[index] = entry;
            }
            else
            {
                ProviderProfiles.Add(entry);
            }
        }

        return Task.FromResult(result);
    }

    public Task<SettingsProfileResult> DeleteProviderProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        ProviderDeletes.Add(profileId);
        var result = ScriptedDeleteResults.Count > 0
            ? ScriptedDeleteResults.Dequeue()
            : SettingsProfileResult.Success("provider profile 已删除");
        if (result.IsSuccess)
        {
            ProviderProfiles.RemoveAll(item => string.Equals(item.ProfileId, profileId, StringComparison.Ordinal));
        }

        return Task.FromResult(result);
    }

    public Task<IReadOnlyList<NetworkProfileInfo>> ListNetworkProfilesAsync(
        CancellationToken cancellationToken = default)
    {
        NetworkProfileListCalls++;
        return Task.FromResult<IReadOnlyList<NetworkProfileInfo>>(NetworkProfiles.ToList());
    }

    public Task<SettingsProfileResult> SaveNetworkProfileAsync(
        string? networkProfileId,
        NetworkProfileDraft draft,
        CancellationToken cancellationToken = default)
    {
        NetworkSaves.Add((networkProfileId, draft));
        var result = ScriptedNetworkSaveResults.Count > 0
            ? ScriptedNetworkSaveResults.Dequeue()
            : SettingsProfileResult.Success(networkProfileId is null ? "network profile 已创建" : "network profile 已更新");
        if (result.IsSuccess)
        {
            var id = networkProfileId ?? "network-" + (NetworkProfiles.Count + 1);
            var entry = new NetworkProfileInfo(
                id,
                draft.DisplayName,
                draft.Mode,
                draft.ProxyEndpoint,
                draft.VerifyTls,
                draft.VerifyTls ? "enabled" : "disabled_confirmed",
                draft.AllowProxyFailureDirectFallback,
                "missing");
            var index = NetworkProfiles.FindIndex(item => string.Equals(item.NetworkProfileId, id, StringComparison.Ordinal));
            if (index >= 0)
            {
                NetworkProfiles[index] = entry;
            }
            else
            {
                NetworkProfiles.Add(entry);
            }
        }

        return Task.FromResult(result);
    }

    public Task<SettingsProfileResult> DeleteNetworkProfileAsync(
        string networkProfileId,
        CancellationToken cancellationToken = default)
    {
        NetworkDeletes.Add(networkProfileId);
        var result = ScriptedDeleteResults.Count > 0
            ? ScriptedDeleteResults.Dequeue()
            : SettingsProfileResult.Success("network profile 已删除");
        if (result.IsSuccess)
        {
            NetworkProfiles.RemoveAll(item => string.Equals(item.NetworkProfileId, networkProfileId, StringComparison.Ordinal));
        }

        return Task.FromResult(result);
    }

    public Task<SettingsProfileResult> SetNetworkDefaultAsync(
        string? networkProfileId,
        CancellationToken cancellationToken = default)
    {
        NetworkDefaults.Add(networkProfileId);
        var result = ScriptedDefaultResults.Count > 0
            ? ScriptedDefaultResults.Dequeue()
            : SettingsProfileResult.Success(networkProfileId is null ? "默认 network profile 已清除" : "默认 network profile 已设置");
        return Task.FromResult(result);
    }

    public Task<NetworkTestInfo?> TestNetworkProfileAsync(
        string networkProfileId,
        string providerProfileId,
        CancellationToken cancellationToken = default)
    {
        NetworkTests.Add((networkProfileId, providerProfileId));
        var result = ScriptedNetworkTestResults.Count > 0
            ? ScriptedNetworkTestResults.Dequeue()
            : null;
        return Task.FromResult(result);
    }

    public Task<NetworkResolveInfo?> ResolveNetworkProfileAsync(
        string? providerProfileId,
        CancellationToken cancellationToken = default)
    {
        NetworkResolves.Add(providerProfileId);
        var result = ScriptedNetworkResolveResults.Count > 0
            ? ScriptedNetworkResolveResults.Dequeue()
            : null;
        return Task.FromResult(result);
    }

    public Task<SettingsProfileResult> SetProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        string profileId,
        CancellationToken cancellationToken = default)
    {
        BindingSets.Add((scope, capability, profileId));
        var result = ScriptedBindingResults.Count > 0
            ? ScriptedBindingResults.Dequeue()
            : SettingsProfileResult.Success($"绑定已保存：{capability} → {profileId}");
        return Task.FromResult(result);
    }

    public Task<SettingsProfileResult> ClearProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        CancellationToken cancellationToken = default)
    {
        BindingClears.Add((scope, capability));
        var result = ScriptedBindingResults.Count > 0
            ? ScriptedBindingResults.Dequeue()
            : SettingsProfileResult.Success($"绑定已清除：{capability}");
        return Task.FromResult(result);
    }

    public Task<ProviderBindingResult?> ResolveProviderBindingAsync(
        string capability,
        CancellationToken cancellationToken = default)
    {
        var result = ScriptedBindingResolveResults.Count > 0
            ? ScriptedBindingResolveResults.Dequeue()
            : null;
        return Task.FromResult(result);
    }

    // ---------------------------------------------------------------------------------------
    // IMPORT-EXPORT-UI-1: recorded import/export traffic + scripted job state (headless tests never
    // touch a real Core, never write real files: the target path is only recorded).
    // ---------------------------------------------------------------------------------------

    public string ExportDirectorySuggestionValue { get; set; } = string.Empty;

    public string ExportDirectorySuggestion => ExportDirectorySuggestionValue;

    public List<(string ChapterId, IReadOnlyList<string> Paths, string DuplicatePolicy)> ImportFileCalls { get; } = new();

    public List<(string ChapterId, string FolderPath, string DuplicatePolicy)> ImportFolderCalls { get; } = new();

    public Queue<ImportOutcome> ScriptedImportResults { get; } = new();

    public Dictionary<string, IReadOnlyList<string>> TranslatedPagesByChapter { get; } = new(StringComparer.Ordinal);

    public int TranslatedPageCalls { get; private set; }

    /// <summary>V11R-A-7: stale policy the UI asked for (null = the controller's default abort).</summary>
    public List<(string BookId, string ChapterId, IReadOnlyList<string> PageIds, string TargetPath, string Format, string? PdfContent, string? StalePolicy)> StartExportCalls { get; } = new();

    public Queue<ExportStartInfo?> ScriptedStartResults { get; } = new();

    public Queue<ExportSnapshotInfo?> ScriptedSnapshots { get; } = new();

    public ExportSnapshotInfo? LastSnapshotResult { get; private set; }

    public List<string> SnapshotCalls { get; } = new();

    public List<string> CancelCalls { get; } = new();

    public List<string> RevealCalls { get; } = new();

    public List<ExportHistoryEntry> ExportHistory { get; set; } = new();

    public bool RevealResult { get; set; } = true;

    public Task<ImportOutcome> ImportFilesAsync(
        string chapterId,
        IReadOnlyList<string> paths,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default)
    {
        ImportFileCalls.Add((chapterId, paths, duplicatePolicy));
        return Task.FromResult(ScriptedImportResults.Count > 0
            ? ScriptedImportResults.Dequeue()
            : ImportOutcome.Success(paths.Count, 0));
    }

    public Task<ImportOutcome> ImportFolderAsync(
        string chapterId,
        string folderPath,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default)
    {
        ImportFolderCalls.Add((chapterId, folderPath, duplicatePolicy));
        return Task.FromResult(ScriptedImportResults.Count > 0
            ? ScriptedImportResults.Dequeue()
            : ImportOutcome.Success(1, 0));
    }

    // FEA-09-UI-1: scriptable referenced-import face (VM state-machine tests only — the real
    // IPC evidence lives in NewManga.Host.Tests under NEWMANGA_FEA09_IPC=1).
    public List<(string ChapterId, IReadOnlyList<ReferenceImportSource> Sources, string Policy)> ReferencePlanCalls { get; } = new();

    public Queue<SourcePlanPreview?> ScriptedReferencePlans { get; } = new();

    public Queue<SourceImportStartResult> ScriptedReferenceStarts { get; } = new();

    public Func<Task<SourceImportReceipt?>>? ReferenceReceiptOverride { get; set; }

    public Queue<SourceImportReceipt?> ScriptedReferenceReceipts { get; } = new();

    public List<string> ReferenceCancelCalls { get; } = new();

    public Queue<SourceImportCancelResult> ScriptedReferenceCancels { get; } = new();

    public string? LastStartPassword { get; private set; }

    public int ReferenceStartCalls { get; private set; }

    public Task<SourcePlanPreview?> PlanReferencedImportAsync(
        string chapterId,
        IReadOnlyList<ReferenceImportSource> sources,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default)
    {
        ReferencePlanCalls.Add((chapterId, sources, duplicatePolicy));
        return Task.FromResult(ScriptedReferencePlans.Count > 0
            ? ScriptedReferencePlans.Dequeue()
            : null);
    }

    public Task<SourceImportStartResult> StartReferencedImportAsync(
        SourcePlanPreview plan,
        string? password,
        CancellationToken cancellationToken = default)
    {
        ReferenceStartCalls++;
        LastStartPassword = password;
        return Task.FromResult(ScriptedReferenceStarts.Count > 0
            ? ScriptedReferenceStarts.Dequeue()
            : SourceImportStartResult.Accepted("op-fake-" + ReferenceStartCalls));
    }

    public Task<SourceImportReceipt?> GetReferencedImportReceiptAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        if (ReferenceReceiptOverride is { } receipt) return receipt();
        return Task.FromResult(ScriptedReferenceReceipts.Count > 0
            ? ScriptedReferenceReceipts.Dequeue()
            : null);
    }

    public Task<SourceImportCancelResult> CancelReferencedImportAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        ReferenceCancelCalls.Add(operationId);
        return Task.FromResult(ScriptedReferenceCancels.Count > 0
            ? ScriptedReferenceCancels.Dequeue()
            : new SourceImportCancelResult(true, true, "running", null));
    }

    /// <summary>
    /// FEA-11-SCAN-2 (B1 / AC-S2-2 / S-2): how many times the dock asked the Host to refresh its scan
    /// targets. The App passes NO target ids anymore — the Core enumeration is the sole authority.
    /// </summary>
    public int SourceScanRefreshRequests { get; private set; }

    public void RequestSourceScanRefresh() => SourceScanRefreshRequests++;

    // FEA-11-L-S1-B-RECOVERY-REAUTH-1 (B1): scriptable explicit recovery face. The counters are the
    // AC-LSB-1 evidence at the port boundary: a preview failure alone must leave every one of them
    // at 0 (no automatic re-authorization / reset), and only an explicit user command may move them.
    public int SourceRecoveryDiagnoseCalls { get; private set; }

    public Queue<SourceRecoveryDiagnosis> ScriptedRecoveryDiagnoses { get; } = new();

    public Func<SourceRecoveryDiagnosis>? RecoveryDiagnosisOverride { get; set; }

    public int SourceReauthorizeCalls { get; private set; }

    public Queue<SourceRecoveryResult> ScriptedReauthorizeResults { get; } = new();

    public int SourceResetCalls { get; private set; }

    /// <summary>Every confirm bit the view model actually passed to the reset action.</summary>
    public List<bool> SourceResetConfirms { get; } = new();

    public Queue<SourceRecoveryResult> ScriptedResetResults { get; } = new();

    public Task<SourceRecoveryDiagnosis> DiagnoseSourceRecoveryAsync(
        CancellationToken cancellationToken = default)
    {
        SourceRecoveryDiagnoseCalls++;
        if (RecoveryDiagnosisOverride is { } diagnose) return Task.FromResult(diagnose());
        return Task.FromResult(ScriptedRecoveryDiagnoses.Count > 0
            ? ScriptedRecoveryDiagnoses.Dequeue()
            : SourceRecoveryDiagnosis.NotApplicable(null));
    }

    public Task<SourceRecoveryResult> ReauthorizeSourceAsync(
        CancellationToken cancellationToken = default)
    {
        SourceReauthorizeCalls++;
        return Task.FromResult(ScriptedReauthorizeResults.Count > 0
            ? ScriptedReauthorizeResults.Dequeue()
            : SourceRecoveryResult.Failed("HOST_NOT_READY", SourceRecoveryText.NotReady()));
    }

    public Task<SourceRecoveryResult> ResetSourceRegistryAsync(
        bool confirm,
        CancellationToken cancellationToken = default)
    {
        SourceResetCalls++;
        SourceResetConfirms.Add(confirm);
        return Task.FromResult(ScriptedResetResults.Count > 0
            ? ScriptedResetResults.Dequeue()
            : SourceRecoveryResult.Failed("HOST_NOT_READY", SourceRecoveryText.NotReady()));
    }

    public Task<IReadOnlyList<string>> GetTranslatedPageIdsAsync(
        string chapterId,
        CancellationToken cancellationToken = default)
    {
        TranslatedPageCalls++;
        return Task.FromResult(
            TranslatedPagesByChapter.TryGetValue(chapterId, out var pages)
                ? pages
                : (IReadOnlyList<string>)Array.Empty<string>());
    }

    public Task<ExportStartInfo?> StartExportAsync(
        string bookId,
        string chapterId,
        IReadOnlyList<string> orderedPageIds,
        string targetPath,
        string format = "zip",
        string? pdfContent = null,
        string? stalePolicy = null,
        CancellationToken cancellationToken = default)
    {
        StartExportCalls.Add((bookId, chapterId, orderedPageIds, targetPath, format, pdfContent, stalePolicy));
        if (ScriptedStartResults.Count > 0)
        {
            return Task.FromResult(ScriptedStartResults.Dequeue());
        }

        return Task.FromResult<ExportStartInfo?>(
            ExportStartInfo.FromState($"exp-fake-{StartExportCalls.Count}", "pending", orderedPageIds.Count));
    }

    public Task<ExportSnapshotInfo?> GetExportSnapshotAsync(
        string exportId,
        CancellationToken cancellationToken = default)
    {
        SnapshotCalls.Add(exportId);
        if (ScriptedSnapshots.Count > 0)
        {
            LastSnapshotResult = ScriptedSnapshots.Dequeue();
        }

        return Task.FromResult(LastSnapshotResult);
    }

    public Task<IReadOnlyList<ExportHistoryEntry>> GetExportHistoryAsync(
        CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<ExportHistoryEntry>>(ExportHistory.ToList());

    public Task<ExportSnapshotInfo?> CancelExportAsync(
        string exportId,
        CancellationToken cancellationToken = default)
    {
        CancelCalls.Add(exportId);
        var cancelled = ExportSnapshotInfo.FromState(exportId, ExportJobState.Cancelled);
        LastSnapshotResult = cancelled;
        return Task.FromResult<ExportSnapshotInfo?>(cancelled);
    }

    public Task<bool> RevealExportFolderAsync(
        string exportId,
        CancellationToken cancellationToken = default)
    {
        RevealCalls.Add(exportId);
        return Task.FromResult(RevealResult);
    }

    // ---------------------------------------------------------------------------------------
    // READER-WORKBENCH-1: scripted single-page region data. Reads are dictionary lookups; writes
    // mimic the Core's optimistic-commit semantics in memory (new revision on every successful
    // write, restored revision appended as a NEW revision) so UI refresh assertions are real.
    // ---------------------------------------------------------------------------------------

    public Dictionary<string, IReadOnlyList<ChapterPageSummary>> ChapterPagesByChapter { get; } = new(StringComparer.Ordinal);

    public Dictionary<string, RegionPageProjection> RegionsByPage { get; } = new(StringComparer.Ordinal);

    public Dictionary<string, RegionRevisionHistory> RevisionsByRegion { get; } = new(StringComparer.Ordinal);

    public Dictionary<string, byte[]> PageImagesByPage { get; } = new(StringComparer.Ordinal);

    public List<string> ChapterPageCalls { get; } = new();

    public List<string> RegionListCalls { get; } = new();

    public List<string> RevisionListCalls { get; } = new();

    public List<string> PageImageCalls { get; } = new();

    public List<(string RegionId, string NewType, int ExpectedRevision)> SetRegionTypeCalls { get; } = new();

    public List<(string RegionId, int RevisionNo, int ExpectedRevision)> RestoreRegionCalls { get; } = new();

    public List<string> RerenderCalls { get; } = new();

    public Queue<RegionOperationResult> ScriptedSetTypeResults { get; } = new();

    public Queue<RegionOperationResult> ScriptedRestoreResults { get; } = new();

    public Queue<PageRerenderOutcome> ScriptedRerenderResults { get; } = new();

    public Task<IReadOnlyList<ChapterPageSummary>> ListChapterPagesAsync(
        string chapterId,
        CancellationToken cancellationToken = default)
    {
        ChapterPageCalls.Add(chapterId);
        return Task.FromResult(
            ChapterPagesByChapter.TryGetValue(chapterId, out var pages)
                ? pages
                : (IReadOnlyList<ChapterPageSummary>)Array.Empty<ChapterPageSummary>());
    }

    public Task<RegionPageProjection?> LoadPageRegionsAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        RegionListCalls.Add(pageId);
        return Task.FromResult<RegionPageProjection?>(
            RegionsByPage.TryGetValue(pageId, out var projection) ? projection : null);
    }

    public Task<RegionRevisionHistory?> LoadRegionRevisionsAsync(
        string regionId,
        CancellationToken cancellationToken = default)
    {
        RevisionListCalls.Add(regionId);
        return Task.FromResult<RegionRevisionHistory?>(
            RevisionsByRegion.TryGetValue(regionId, out var history) ? history : null);
    }

    public Task<byte[]?> ReadPageImageAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        PageImageCalls.Add(pageId);
        return Task.FromResult<byte[]?>(
            PageImagesByPage.TryGetValue(pageId, out var bytes) ? bytes : null);
    }

    public Task<RegionOperationResult> SetRegionTypeAsync(
        string regionId,
        string newRegionType,
        int expectedRevision,
        CancellationToken cancellationToken = default)
    {
        if (Snapshot.State != HostViewState.Ready)
        {
            return Task.FromResult(RegionOperationResult.NotReady());
        }

        if (!Snapshot.WritesAllowed)
        {
            return Task.FromResult(RegionOperationResult.ReadOnly());
        }

        SetRegionTypeCalls.Add((regionId, newRegionType, expectedRevision));
        if (ScriptedSetTypeResults.Count > 0)
        {
            return Task.FromResult(ScriptedSetTypeResults.Dequeue());
        }

        var row = FindRegion(regionId);
        if (row is null)
        {
            return Task.FromResult(RegionOperationResult.Failed("TARGET_NOT_FOUND"));
        }

        if (expectedRevision > 0 && row.RevisionNo != expectedRevision)
        {
            return Task.FromResult(RegionOperationResult.Failed("INPUT_REVISION_CHANGED"));
        }

        var revision = row.RevisionNo + 1;
        WriteRegion(regionId, row with { RegionType = newRegionType, RevisionNo = revision });
        AppendRevision(regionId, revision, newRegionType, row.SfxPolicy);
        return Task.FromResult(RegionOperationResult.Success(
            new RegionWriteSnapshot(regionId, revision, newRegionType, row.SfxPolicy),
            $"类型已更新为 {newRegionType}（revision {revision}）"));
    }

    public Task<RegionOperationResult> RestoreRegionRevisionAsync(
        string regionId,
        int revisionNo,
        int expectedRevision,
        CancellationToken cancellationToken = default)
    {
        if (Snapshot.State != HostViewState.Ready)
        {
            return Task.FromResult(RegionOperationResult.NotReady());
        }

        if (!Snapshot.WritesAllowed)
        {
            return Task.FromResult(RegionOperationResult.ReadOnly());
        }

        RestoreRegionCalls.Add((regionId, revisionNo, expectedRevision));
        if (ScriptedRestoreResults.Count > 0)
        {
            return Task.FromResult(ScriptedRestoreResults.Dequeue());
        }

        var row = FindRegion(regionId);
        if (row is null)
        {
            return Task.FromResult(RegionOperationResult.Failed("TARGET_NOT_FOUND"));
        }

        if (row.RevisionNo != expectedRevision)
        {
            return Task.FromResult(RegionOperationResult.Failed("INPUT_REVISION_CHANGED"));
        }

        var source = RevisionsByRegion.TryGetValue(regionId, out var history)
            ? history.Revisions.FirstOrDefault(revision => revision.RevisionNo == revisionNo)
            : null;
        if (source is null)
        {
            return Task.FromResult(RegionOperationResult.Failed("TARGET_NOT_FOUND"));
        }

        var revision = row.RevisionNo + 1;
        WriteRegion(regionId, row with { RegionType = source.RegionType, RevisionNo = revision });
        AppendRevision(regionId, revision, source.RegionType, source.SfxPolicy);
        return Task.FromResult(RegionOperationResult.Success(
            new RegionWriteSnapshot(regionId, revision, source.RegionType, source.SfxPolicy),
            $"已恢复 revision {revisionNo} → revision {revision}（{source.RegionType}）"));
    }

    public Task<PageRerenderOutcome> RerenderPageAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        if (Snapshot.State != HostViewState.Ready)
        {
            return Task.FromResult(PageRerenderOutcome.NotReady());
        }

        if (!Snapshot.WritesAllowed)
        {
            return Task.FromResult(PageRerenderOutcome.ReadOnly());
        }

        RerenderCalls.Add(pageId);
        if (ScriptedRerenderResults.Count > 0)
        {
            return Task.FromResult(ScriptedRerenderResults.Dequeue());
        }

        var reports = RegionsByPage.TryGetValue(pageId, out var projection)
            ? projection.Regions
                .Select(region => new RerenderRegionReport(region.RegionId, "rendered", null, false))
                .ToList()
            : new List<RerenderRegionReport>();
        var result = new PageRerenderResult(pageId, "artifact-fake", 1, reports, "preview-fake", null);
        return Task.FromResult(PageRerenderOutcome.Success(
            result,
            $"已重渲染 revision 1（{reports.Count} 区域，预览已发布）"));
    }

    private RegionSummary? FindRegion(string regionId)
    {
        foreach (var projection in RegionsByPage.Values)
        {
            var row = projection.Regions.FirstOrDefault(region =>
                string.Equals(region.RegionId, regionId, StringComparison.Ordinal));
            if (row is not null)
            {
                return row;
            }
        }

        return null;
    }

    private void WriteRegion(string regionId, RegionSummary updated)
    {
        foreach (var entry in RegionsByPage.ToList())
        {
            var index = entry.Value.Regions.ToList().FindIndex(region =>
                string.Equals(region.RegionId, regionId, StringComparison.Ordinal));
            if (index < 0)
            {
                continue;
            }

            var rows = entry.Value.Regions.ToList();
            rows[index] = updated;
            RegionsByPage[entry.Key] = entry.Value with { Regions = rows };
            return;
        }
    }

    private void AppendRevision(string regionId, int revisionNo, string regionType, string sfxPolicy)
    {
        if (!RevisionsByRegion.TryGetValue(regionId, out var history))
        {
            history = new RegionRevisionHistory(regionId, 0, Array.Empty<RegionRevisionSummary>());
        }

        var rows = history.Revisions
            .Select(revision => revision with { IsCurrent = false })
            .ToList();
        rows.Add(new RegionRevisionSummary(
            "rev-" + revisionNo,
            revisionNo,
            "restored",
            "unreviewed",
            false,
            null,
            "2026-10-28T00:00:00Z",
            regionType,
            sfxPolicy,
            true));
        RevisionsByRegion[regionId] = new RegionRevisionHistory(regionId, revisionNo, rows);
    }

    public ValueTask DisposeAsync() => ValueTask.CompletedTask;

    /// <summary>CHAPTER-SELECTOR-1: resolve the scripted book that owns a chapter id.</summary>
    private ReaderBookData? ResolveBookForChapter(string chapterId)
    {
        if (ReaderBooksByChapterId.TryGetValue(chapterId, out var exact))
        {
            return exact;
        }

        foreach (var book in ReaderBooksByBookId.Values)
        {
            if (string.Equals(book.ChapterId, chapterId, StringComparison.Ordinal))
            {
                return book;
            }
        }

        return ReaderBook is { } fallback && string.Equals(fallback.ChapterId, chapterId, StringComparison.Ordinal)
            ? fallback
            : null;
    }

    // ---------------------------------------------------------------------------------------
    // V11R-A-2 (contract §5.2): scripted Run seam. Records every request, lets a test queue typed
    // results, and otherwise behaves like the deterministic fake (in-memory runs, honest empty
    // projections, local R-08 key rules). Never throws into the UI.
    // ---------------------------------------------------------------------------------------

    public List<RunStartRequest> StartRunRequests { get; } = new();

    public List<(string RunId, RunControlAction Action, string? IdempotencyKey)> ControlRunRequests { get; } = new();

    public List<string> RunSnapshotRequests { get; } = new();

    public Task? RunSnapshotGate { get; set; }

    public TaskCompletionSource<bool> RunSnapshotGateStarted { get; } =
        new(TaskCreationOptions.RunContinuationsAsynchronously);

    public List<string> TaskProjectionRequests { get; } = new();

    public List<(string RunId, string IdempotencyKey)> RetriedFailedRuns { get; } = new();

    public Queue<RunStartInfo?> ScriptedStartRuns { get; } = new();

    /// <summary>
    /// REALUSE-DATA-SAFETY-2 AC1: typed code published when a scripted start returns null
    /// (default <c>SCRIPTED_FAILURE</c>), so a test can reproduce a real Core refusal such as
    /// <c>PROVIDER_NOT_CONFIGURED</c>.
    /// </summary>
    public string? ScriptedStartRunErrorCode { get; set; }

    public Queue<RunControlInfo?> ScriptedControlRuns { get; } = new();

    public Queue<RunSnapshotInfo?> ScriptedRunSnapshots { get; } = new();

    public Queue<TaskProjectionInfo?> ScriptedTaskProjections { get; } = new();

    private readonly Dictionary<string, RunStartInfo> _fakeRuns = new(StringComparer.Ordinal);
    private readonly Dictionary<string, RunStartRequest> _fakeRunRequests = new(StringComparer.Ordinal);
    private int _fakeRunSequence;

    public Task<RunStartInfo?> StartRunAsync(RunStartRequest request, CancellationToken ct = default)
    {
        StartRunRequests.Add(request);

        if (request is null ||
            string.IsNullOrWhiteSpace(request.Command) ||
            request.Scope is null ||
            string.IsNullOrWhiteSpace(request.IdempotencyKey))
        {
            PublishLastError("INVALID_REQUEST");
            return Task.FromResult<RunStartInfo?>(null);
        }

        if (ct.IsCancellationRequested)
        {
            PublishLastError("CANCELLED");
            return Task.FromResult<RunStartInfo?>(null);
        }

        if (ScriptedStartRuns.Count > 0)
        {
            var scripted = ScriptedStartRuns.Dequeue();
            PublishLastError(scripted is null
                ? ScriptedStartRunErrorCode ?? "SCRIPTED_FAILURE"
                : null);
            return Task.FromResult(scripted);
        }

        var info = new RunStartInfo($"fake-run-{++_fakeRunSequence}", "pending");
        _fakeRuns[info.RunId] = info;
        _fakeRunRequests[info.RunId] = request;
        PublishLastError(null);
        return Task.FromResult<RunStartInfo?>(info);
    }

    public Task<RunControlInfo?> ControlRunAsync(
        string runId,
        RunControlAction action,
        string? idempotencyKey = null,
        CancellationToken ct = default)
    {
        ControlRunRequests.Add((runId, action, idempotencyKey));

        if (string.IsNullOrWhiteSpace(runId) ||
            (action == RunControlAction.Restart && string.IsNullOrWhiteSpace(idempotencyKey)))
        {
            PublishLastError("INVALID_REQUEST");
            return Task.FromResult<RunControlInfo?>(null);
        }

        if (ct.IsCancellationRequested)
        {
            PublishLastError("CANCELLED");
            return Task.FromResult<RunControlInfo?>(null);
        }

        if (ScriptedControlRuns.Count > 0)
        {
            var scripted = ScriptedControlRuns.Dequeue();
            PublishLastError(scripted is null ? "SCRIPTED_FAILURE" : null);
            return Task.FromResult(scripted);
        }

        lock (_fakeRuns)
        {
            if (!_fakeRuns.TryGetValue(runId, out var run))
            {
                PublishLastError("TARGET_NOT_FOUND");
                return Task.FromResult<RunControlInfo?>(null);
            }

            var next = action switch
            {
                RunControlAction.Pause when run.Status == "running" => "paused",
                RunControlAction.Resume when run.Status == "paused" => "running",
                RunControlAction.Stop when run.Status is "pending" or "running" or "paused" => "cancelled",
                _ => null,
            };
            if (next is null)
            {
                PublishLastError("INVALID_RUN_TRANSITION");
                return Task.FromResult<RunControlInfo?>(null);
            }

            var updated = run with { Status = next };
            _fakeRuns[runId] = updated;
            PublishLastError(null);
            return Task.FromResult<RunControlInfo?>(new RunControlInfo(runId, next));
        }
    }

    public Task<RunControlInfo?> ResumeBlockedRunAsync(string runId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId) || ct.IsCancellationRequested)
        {
            PublishLastError(ct.IsCancellationRequested ? "CANCELLED" : "INVALID_REQUEST");
            return Task.FromResult<RunControlInfo?>(null);
        }

        if (ScriptedControlRuns.Count > 0)
        {
            var scripted = ScriptedControlRuns.Dequeue();
            PublishLastError(scripted is null ? "SCRIPTED_FAILURE" : null);
            return Task.FromResult(scripted);
        }

        PublishLastError("INVALID_RUN_TRANSITION");
        return Task.FromResult<RunControlInfo?>(null);
    }

    public Task<RunSnapshotInfo?> GetRunSnapshotAsync(string runId, CancellationToken ct = default)
    {
        RunSnapshotRequests.Add(runId);
        if (RunSnapshotGate is { } gate)
        {
            return GetRunSnapshotAfterGateAsync(runId, ct, gate);
        }

        return GetRunSnapshotCore(runId, ct);
    }

    private async Task<RunSnapshotInfo?> GetRunSnapshotAfterGateAsync(
        string runId, CancellationToken cancellationToken, Task gate)
    {
        RunSnapshotGateStarted.TrySetResult(true);
        await gate.WaitAsync(cancellationToken).ConfigureAwait(false);
        return await GetRunSnapshotCore(runId, cancellationToken).ConfigureAwait(false);
    }

    private Task<RunSnapshotInfo?> GetRunSnapshotCore(string runId, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(runId) || ct.IsCancellationRequested)
        {
            PublishLastError(ct.IsCancellationRequested ? "CANCELLED" : "INVALID_REQUEST");
            return Task.FromResult<RunSnapshotInfo?>(null);
        }

        if (ScriptedRunSnapshots.Count > 0)
        {
            var scripted = ScriptedRunSnapshots.Dequeue();
            PublishLastError(scripted is null ? "SCRIPTED_FAILURE" : null);
            return Task.FromResult(scripted);
        }

        lock (_fakeRuns)
        {
            if (!_fakeRuns.TryGetValue(runId, out var run))
            {
                PublishLastError("TARGET_NOT_FOUND");
                return Task.FromResult<RunSnapshotInfo?>(null);
            }

            return Task.FromResult<RunSnapshotInfo?>(new RunSnapshotInfo(
                runId,
                _fakeRunRequests[runId].Command,
                new RunScopeInfo("chapter"),
                run.Status,
                Array.Empty<RunTargetInfo>()));
        }
    }

    public Task<TaskProjectionInfo?> GetTaskProjectionAsync(string runId, CancellationToken ct = default)
    {
        TaskProjectionRequests.Add(runId);

        if (string.IsNullOrWhiteSpace(runId) || ct.IsCancellationRequested)
        {
            PublishLastError(ct.IsCancellationRequested ? "CANCELLED" : "INVALID_REQUEST");
            return Task.FromResult<TaskProjectionInfo?>(null);
        }

        if (ScriptedTaskProjections.Count > 0)
        {
            var scripted = ScriptedTaskProjections.Dequeue();
            PublishLastError(scripted is null ? "SCRIPTED_FAILURE" : null);
            return Task.FromResult(scripted);
        }

        lock (_fakeRuns)
        {
            if (!_fakeRuns.TryGetValue(runId, out var run))
            {
                PublishLastError("TARGET_NOT_FOUND");
                return Task.FromResult<TaskProjectionInfo?>(null);
            }

            return Task.FromResult<TaskProjectionInfo?>(new TaskProjectionInfo(
                runId,
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
                new RunControlsInfo(false, false, false, false, false, false)));
        }
    }

    public Task<RunControlInfo?> RetryFailedTargetsAsync(
        string runId,
        string idempotencyKey,
        CancellationToken ct = default)
    {
        RetriedFailedRuns.Add((runId, idempotencyKey));

        if (string.IsNullOrWhiteSpace(runId) || string.IsNullOrWhiteSpace(idempotencyKey))
        {
            PublishLastError("INVALID_REQUEST");
            return Task.FromResult<RunControlInfo?>(null);
        }

        if (ct.IsCancellationRequested)
        {
            PublishLastError("CANCELLED");
            return Task.FromResult<RunControlInfo?>(null);
        }

        if (ScriptedControlRuns.Count > 0)
        {
            var scripted = ScriptedControlRuns.Dequeue();
            PublishLastError(scripted is null ? "SCRIPTED_FAILURE" : null);
            return Task.FromResult(scripted);
        }

        PublishLastError("INVALID_RUN_TRANSITION");
        return Task.FromResult<RunControlInfo?>(null);
    }

    public static HostViewSnapshot ReadySnapshot(params string[] titles)
    {
        var books = new List<BookSummary>();
        for (var i = 0; i < titles.Length; i++)
        {
            books.Add(new BookSummary(
                $"book-{i}",
                titles[i],
                string.Empty,
                false,
                false,
                null,
                "2026-10-27T00:00:00Z",
                "2026-10-27T00:00:00Z"));
        }

        return new HostViewSnapshot(
            HostViewState.Ready,
            "Host 就绪 · core_service protocol 2.3 + host_bridge wire v1",
            "只读（S2 parity 前） · sidecars ready",
            null,
            null,
            books,
            4,
            true,
            null);
    }

    /// <summary>READER-WORKBENCH-1 AC3: a ready Host whose data-root policy is still read-only.</summary>
    public static HostViewSnapshot ReadOnlySnapshot(params string[] titles) =>
        ReadySnapshot(titles) with
        {
            ModeLine = "只读（S2 parity 前） · sidecars ready",
            WritesAllowed = false,
        };

    public static HostViewSnapshot FailureSnapshot() => new(
        HostViewState.Failed,
        "Host 启动失败",
        "只读（S2 parity 前） · no sidecars",
        "SIDECAR_EXE_MISSING",
        "核心服务程序缺失（core_service.exe）。",
        Array.Empty<BookSummary>(),
        0,
        true,
        null);

    // ---------------------------------------------------------------------------------------
    // REALUSE-DATA-SAFETY-1 AC2: scriptable backup face for Console headless tests.
    // ---------------------------------------------------------------------------------------

    public List<BackupPackageInfo> Backups { get; } = new();

    public List<string> BackupCalls { get; } = new();

    /// <summary>When set, every backup write reports this failure and performs nothing.</summary>
    public string? BackupFailureCode { get; set; }

    public Func<BackupPackageInfo>? BackupFactory { get; set; }

    public string? LastBackupError { get; private set; }

    public Task<IReadOnlyList<BackupPackageInfo>> ListBackupsAsync(
        CancellationToken cancellationToken = default)
    {
        BackupCalls.Add("list");
        return Task.FromResult<IReadOnlyList<BackupPackageInfo>>(Backups.ToList());
    }

    public Task<BackupPackageInfo?> CreateBackupAsync(
        string backupType = "manual",
        CancellationToken cancellationToken = default)
    {
        BackupCalls.Add("create");
        if (BackupFailureCode is { } code)
        {
            LastBackupError = code;
            return Task.FromResult<BackupPackageInfo?>(null);
        }

        var created = BackupFactory?.Invoke() ?? new BackupPackageInfo(
            Guid.NewGuid().ToString("N"), backupType, DateTimeOffset.UtcNow.ToString("o"), 1024, 6, true);
        Backups.Add(created);
        return Task.FromResult<BackupPackageInfo?>(created);
    }

    public Task<bool> DeleteBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        BackupCalls.Add("delete:" + backupId);
        if (BackupFailureCode is { } code)
        {
            LastBackupError = code;
            return Task.FromResult(false);
        }

        Backups.RemoveAll(item => string.Equals(item.BackupId, backupId, StringComparison.Ordinal));
        return Task.FromResult(true);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: scriptable plugin face.</summary>
    public PluginListInfo PluginList { get; set; } = new(
        true,
        new[]
        {
            new PluginInfo("sample.plugin", "enabled", true, "示例插件", "1.0.0", "测试夹具插件",
                new[] { "before_translate" }, new[] { "read:pages" }, null),
        });

    public int PluginListCalls { get; private set; }

    public int PluginGlobalToggleCalls { get; private set; }

    public int PluginToggleCalls { get; private set; }

    public bool PluginWriteRefused { get; set; }

    public Task<PluginListInfo> ListPluginsAsync(CancellationToken cancellationToken = default)
    {
        PluginListCalls++;
        return Task.FromResult(PluginList);
    }

    public Task<bool?> SetPluginsGlobalEnabledAsync(bool enabled, CancellationToken cancellationToken = default)
    {
        PluginGlobalToggleCalls++;
        if (PluginWriteRefused)
        {
            PublishLastError("HOST_READ_ONLY");
            return Task.FromResult<bool?>(null);
        }

        PluginList = PluginList with { GlobalEnabled = enabled };
        return Task.FromResult<bool?>(enabled);
    }

    public Task<bool?> SetPluginEnabledAsync(string pluginId, bool enabled, CancellationToken cancellationToken = default)
    {
        PluginToggleCalls++;
        if (PluginWriteRefused)
        {
            PublishLastError("HOST_READ_ONLY");
            return Task.FromResult<bool?>(null);
        }

        PluginList = PluginList with
        {
            Plugins = PluginList.Plugins
                .Select(plugin => plugin.PluginId == pluginId
                    ? plugin with { Enabled = enabled, Status = enabled ? "enabled" : "disabled" }
                    : plugin)
                .ToArray(),
        };
        return Task.FromResult<bool?>(enabled);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: scriptable cleanup face (preview/run counters + outcome).</summary>
    public CleanupPreviewInfo CleanupPreview { get; set; } =
        new(new[] { new CleanupTargetInfo("cache/tiles/abc.webp", 2048) }, 2048, 0);

    public int CleanupPreviewCalls { get; private set; }

    public int CleanupRunCalls { get; private set; }

    /// <summary>When set, the next RunCleanupAsync returns null (Host refused: read-only / error).</summary>
    public bool CleanupRunRefused { get; set; }

    public CleanupOutcomeInfo CleanupOutcome { get; set; } =
        new(1, 0, 0, Array.Empty<string>());

    public int CleanupRetryCalls { get; private set; }

    public CleanupOutcomeInfo CleanupRetryOutcome { get; set; } = new(1, 0, 0, Array.Empty<string>());

    public Task<CleanupOutcomeInfo?> RetryPendingCleanupsAsync(CancellationToken cancellationToken = default)
    {
        CleanupRetryCalls++;
        return Task.FromResult<CleanupOutcomeInfo?>(CleanupRetryOutcome);
    }

    public Task<CleanupPreviewInfo> GetCleanupPreviewAsync(CancellationToken cancellationToken = default)
    {
        CleanupPreviewCalls++;
        return Task.FromResult(CleanupPreview);
    }

    public Task<CleanupOutcomeInfo?> RunCleanupAsync(CancellationToken cancellationToken = default)
    {
        CleanupRunCalls++;
        return Task.FromResult(CleanupRunRefused ? null : (CleanupOutcomeInfo?)CleanupOutcome);
    }

    public Task<string?> RestoreBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        BackupCalls.Add("restore:" + backupId);
        if (BackupFailureCode is { } code)
        {
            LastBackupError = code;
            return Task.FromResult<string?>(null);
        }

        return Task.FromResult<string?>("pre-" + backupId);
    }
    // FEA-05-PORT-1: Draft surface (default: unavailable in the fake host).
    // FEA-06-RESIDUAL-1: scriptable draft surface for dirty-draft UI tests; defaults keep the
    // previous behavior (no leases, empty session draft list).
    /// <summary>Draft leases keyed by "{pageId}|{regionId}"; default empty.</summary>
    public Dictionary<string, DraftLease?> DraftLeasesByPageRegion { get; } = new(StringComparer.Ordinal);

    /// <summary>Drafts returned by ListDraftsAsync for every session; default empty.</summary>
    public IReadOnlyList<Draft> ScriptedDrafts { get; set; } = Array.Empty<Draft>();

    public Task<DraftLease?> OpenDraftAsync(string sessionId, string pageId, string? regionId,
        string? baseRevisionId, int pageBindingVersion, CancellationToken cancellationToken = default) =>
        Task.FromResult(DraftLeasesByPageRegion.TryGetValue(pageId + "|" + regionId, out var lease) ? lease : null);

    public Task<Draft?> PatchDraftAsync(string draftId, string sessionId, DraftPatchRequest patch,
        int? undoCursor = null, CancellationToken cancellationToken = default) =>
        Task.FromResult<Draft?>(null);

    public Task<RegionCandidate?> PrepareCandidateAsync(string regionId, DraftPatchRequest patch,
        string origin, string? draftId = null, string? baseRevisionId = null,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<RegionCandidate?>(null);

    public Task<IReadOnlyDictionary<string, string>> ApplyCandidatesAsync(EditToken token,
        IReadOnlyList<string> candidateIds, CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyDictionary<string, string>>(new Dictionary<string, string>());

    public Task<Draft?> GetDraftAsync(string draftId, CancellationToken cancellationToken = default) =>
        Task.FromResult<Draft?>(null);

    public Task<IReadOnlyList<Draft>> ListDraftsAsync(string sessionId,
        CancellationToken cancellationToken = default) =>
        Task.FromResult(ScriptedDrafts);

    public Task DiscardDraftAsync(string draftId, string sessionId,
        CancellationToken cancellationToken = default) => Task.CompletedTask;

    // ── FEA-12-UI: scriptable trash face (separate from the frozen IHostController) ──────────

    /// <summary>Capability probe result (<c>core_ping</c>); default = all three capabilities present.</summary>
    public TrashCapabilityState TrashCapabilities { get; set; } = new(true, true, true, true, null, null);

    /// <summary>Every "frame" the UI asked the controller for, in order (method→command proxy).</summary>
    public List<string> TrashFrames { get; } = new();

    /// <summary>Payloads of the write/preview frames, in order (assert closed shapes + digest binding).</summary>
    public List<JsonElement> TrashFramePayloads { get; } = new();

    public List<string?> TrashListCursors { get; } = new();

    public Queue<TrashListResult> ScriptedTrashPages { get; } = new();

    public Queue<TrashPreviewResult> ScriptedTrashPreviews { get; } = new();

    /// <summary>r2 P2-2b: optional projection factory (e.g. HostController.ProjectPreviewResponse over
    /// an old-Core JSON shape) so the adapter fail-closed path is testable through the VM.</summary>
    public Func<IReadOnlyList<string>, TrashPreviewResult>? TrashPreviewFactory { get; set; }

    public Queue<TrashDeleteResult> ScriptedTrashDeletes { get; } = new();

    public Queue<TrashWriteResult> ScriptedMoves { get; } = new();

    public Queue<TrashWriteResult> ScriptedRestores { get; } = new();

    /// <summary>Default list page returned when no scripted page is queued.</summary>
    public IReadOnlyList<TrashEntry> DefaultTrashEntries { get; set; } = Array.Empty<TrashEntry>();

    public string? DefaultTrashCursor { get; set; }

    /// <summary>AC1 late-response isolation: when set, ListTrashAsync awaits it before returning.</summary>
    public Task? TrashListGate { get; set; }

    public TaskCompletionSource<bool> TrashListGateStarted { get; } =
        new(TaskCreationOptions.RunContinuationsAsynchronously);

    public int TrashProbeGolden { get; private set; }

    public Task<TrashCapabilityState> ProbeTrashCapabilitiesAsync(CancellationToken cancellationToken = default)
    {
        TrashFrames.Add(TrashWireCommands.CapabilityProbe);
        TrashProbeGolden++;
        return Task.FromResult(TrashCapabilities);
    }

    public async Task<TrashListResult> ListTrashAsync(string? cursor = null, CancellationToken cancellationToken = default)
    {
        TrashFrames.Add(TrashWireCommands.ListTrash);
        TrashListCursors.Add(cursor);
        if (TrashListGate is { } gate)
        {
            TrashListGateStarted.TrySetResult(true);
            await gate.ConfigureAwait(false);
        }

        if (ScriptedTrashPages.Count > 0)
        {
            return ScriptedTrashPages.Dequeue();
        }

        return new TrashListResult(true, null, null, DefaultTrashEntries, DefaultTrashCursor);
    }

    public Task<TrashWriteResult> MoveToTrashAsync(
        IReadOnlyList<string> bookIds,
        string idempotencyKey,
        CancellationToken cancellationToken = default)
    {
        TrashFrames.Add(TrashWireCommands.MoveToTrash);
        TrashFramePayloads.Add(TrashPayloads.MoveOrRestore(bookIds, idempotencyKey));
        var result = ScriptedMoves.Count > 0
            ? ScriptedMoves.Dequeue()
            : new TrashWriteResult(true, null, null, bookIds.ToArray(), Array.Empty<TrashItemIssue>());

        // r2 P3-9 (AC2): a successful soft delete really removes the book from the shelf snapshot,
        // so "书架不再含该书" is assertable instead of only Selection.HasBook=false.
        if (result.SucceededIds.Count > 0)
        {
            var removed = new HashSet<string>(result.SucceededIds, StringComparer.Ordinal);
            Snapshot = Snapshot with
            {
                Books = Snapshot.Books.Where(book => !removed.Contains(book.BookId)).ToArray(),
            };
        }

        return Task.FromResult(result);
    }

    public Task<TrashWriteResult> RestoreFromTrashAsync(
        IReadOnlyList<string> bookIds,
        string idempotencyKey,
        CancellationToken cancellationToken = default)
    {
        TrashFrames.Add(TrashWireCommands.RestoreFromTrash);
        TrashFramePayloads.Add(TrashPayloads.MoveOrRestore(bookIds, idempotencyKey));
        if (ScriptedRestores.Count > 0)
        {
            return Task.FromResult(ScriptedRestores.Dequeue());
        }

        return Task.FromResult(new TrashWriteResult(true, null, null, bookIds.ToArray(), Array.Empty<TrashItemIssue>()));
    }

    public Task<TrashPreviewResult> PreviewPermanentDeleteAsync(
        IReadOnlyList<string> bookIds,
        CancellationToken cancellationToken = default)
    {
        TrashFrames.Add(TrashWireCommands.PreviewPermanentDelete);
        TrashFramePayloads.Add(TrashPayloads.Preview(bookIds));
        if (TrashPreviewFactory is { } factory)
        {
            return Task.FromResult(factory(bookIds));
        }

        if (ScriptedTrashPreviews.Count > 0)
        {
            return Task.FromResult(ScriptedTrashPreviews.Dequeue());
        }

        return Task.FromResult(DefaultPreview(bookIds[0]));
    }

    public Task<TrashDeleteResult> DeletePermanentlyAsync(
        string bookId,
        string inventoryDigest,
        CancellationToken cancellationToken = default)
    {
        TrashFrames.Add(TrashWireCommands.DeletePermanently);
        TrashFramePayloads.Add(TrashPayloads.DeletePermanently(bookId, inventoryDigest));
        if (ScriptedTrashDeletes.Count > 0)
        {
            return Task.FromResult(ScriptedTrashDeletes.Dequeue());
        }

        return Task.FromResult(new TrashDeleteResult(TrashDeleteOutcome.Deleted, null, null));
    }

    /// <summary>Fixture-shaped PD-01 disclosure with KNOWN (empty) current sets and no blockers.</summary>
    public static TrashPreviewResult DefaultPreview(string bookId) =>
        new(true, null, null, "sha256:" + new string('a', 64),
            new[]
            {
                new TrashPreviewItem(
                    bookId,
                    "夜光列车",
                    new TrashProtection(
                        2,
                        "rev-current-1",
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        new[] { "rev-pinned-1" },
                        Array.Empty<string>(),
                        1,
                        3),
                    new TrashContentSummary(2, 12, 3, 4, 2048),
                    new[] { new TrashSharedFileRef("file-1", 1) }),
            },
            new Dictionary<string, string>(StringComparer.Ordinal) { [bookId] = "sha256:" + new string('d', 64) });

    /// <summary>Old-Core fixture: the rev 2.14 current arrays are unknown (absent/null) → fail-closed.</summary>
    public static TrashPreviewResult OldCorePreview(string bookId) =>
        new(true, null, null, "sha256:" + new string('b', 64),
            new[]
            {
                new TrashPreviewItem(
                    bookId,
                    "旧 Core 作品",
                    new TrashProtection(
                        0,
                        null,
                        null,
                        null,
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        0,
                        0),
                    new TrashContentSummary(1, 1, 0, 0, 0),
                    Array.Empty<TrashSharedFileRef>()),
            },
            new Dictionary<string, string>(StringComparer.Ordinal) { [bookId] = "sha256:" + new string('e', 64) });

    /// <summary>Busy fixture: a non-terminal run/task is disclosed (BOOK_BUSY pre-block).</summary>
    public static TrashPreviewResult BusyPreview(string bookId) =>
        new(true, null, null, "sha256:" + new string('c', 64),
            new[]
            {
                new TrashPreviewItem(
                    bookId,
                    "忙作品",
                    new TrashProtection(
                        0,
                        null,
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        Array.Empty<string>(),
                        new[] { "run-active-1" },
                        0,
                        0),
                    new TrashContentSummary(1, 2, 0, 0, 0),
                    Array.Empty<TrashSharedFileRef>()),
            },
            new Dictionary<string, string>(StringComparer.Ordinal) { [bookId] = "sha256:" + new string('f', 64) });

}

/// <summary>READER-PROGRESS-1: one scripted save call recorded by <see cref="FakeProgressStore"/>.</summary>
public sealed record FakeProgressAttempt(
    string ChapterId,
    string PageId,
    string Mode,
    double? ScrollOffsetY,
    double ElapsedSecondsDelta);

/// <summary>READER-PROGRESS-1: one persisted position (Core <c>reading_progress</c> row stand-in).</summary>
public sealed record FakeProgressEntry(string PageId, double ScrollOffsetY, double ProgressPercent);

/// <summary>
/// READER-PROGRESS-1: in-memory Core stand-in. It keys progress by (chapter, mode) exactly like
/// <c>reading_progress</c> does by (book, chapter, mode), validates the page belongs to the book, and
/// keeps the accepted elapsed time so tests can assert "no resend after success".
/// </summary>
public sealed class FakeProgressStore
{
    private readonly Dictionary<string, FakeProgressEntry> _entries = new(StringComparer.Ordinal);

    public List<FakeProgressAttempt> Attempts { get; } = new();

    public int SaveCount => Attempts.Count;

    public double TotalReadSeconds { get; private set; }

    public IReadOnlyDictionary<string, FakeProgressEntry> Entries => _entries;

    public FakeProgressEntry? TryGet(string chapterId, string mode = "original") =>
        _entries.TryGetValue(Key(chapterId, mode), out var entry) ? entry : null;

    public ReaderProgressSaveResult Save(
        ReaderBookData? book,
        string chapterId,
        string pageId,
        string mode,
        double? scrollOffsetY,
        double elapsedSecondsDelta)
    {
        Attempts.Add(new FakeProgressAttempt(chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta));
        if (book is null || !string.Equals(book.ChapterId, chapterId, StringComparison.Ordinal))
        {
            return ReaderProgressSaveResult.Failed("TARGET_NOT_FOUND");
        }

        var index = -1;
        for (var candidate = 0; candidate < book.Pages.Count; candidate++)
        {
            if (string.Equals(book.Pages[candidate].PageId, pageId, StringComparison.Ordinal))
            {
                index = candidate;
                break;
            }
        }

        if (index < 0)
        {
            return ReaderProgressSaveResult.Failed("TARGET_NOT_FOUND");
        }

        var percent = Math.Round((index + 1) / (double)Math.Max(1, book.Pages.Count) * 100.0, 2);
        var offset = Math.Max(0, scrollOffsetY ?? 0);
        TotalReadSeconds += Math.Max(0, elapsedSecondsDelta);
        _entries[Key(chapterId, mode)] = new FakeProgressEntry(pageId, offset, percent);
        return ReaderProgressSaveResult.Saved(percent, pageId);
    }

    private static string Key(string chapterId, string mode) => chapterId + "|" + mode;
}

/// <summary>
/// FEA-11-SCAN-2 (B1 / AC-S2-2 / S-2): VM-level proof that ONLY a completed referenced import asks
/// the Host to refresh its scan targets (exactly once) and that the App contributes NO target
/// identity of its own — the Core enumeration is the sole target authority. Failed/cancelled
/// receipts ask for no refresh, and a library selection switch during the import cannot add or
/// re-label a refresh request.
/// </summary>
public sealed class Fea11ScanRefreshVmTests
{
    private static ImportDockViewModel Create(FakeHostController host) =>
        new(
            host,
            picker: null,
            notify: (_, _) => { },
            chapterId: () => "ch-1",
            chapterTitle: () => "第 1 章",
            afterImport: () => Task.CompletedTask,
            requestCreateChapter: () => { },
            referencePollDelay: () => Task.CompletedTask);

    private static SourcePlanPreview Plan() => new(
        "ch-1",
        "skip",
        "plan-1",
        "digest-1",
        new[] { "grant-1" },
        new[] { new SourcePlanItemView(0, "page.png", "image", "ok", 1, null, false) },
        new SourcePlanTotals(1, 0, 0, 0));

    private static SourceImportReceipt Receipt(SourceImportOperationState state) => new(
        "op-1",
        "ch-1",
        state,
        false,
        state == SourceImportOperationState.Completed ? 1 : 0,
        new[]
        {
            new SourceImportReceiptItem(
                0,
                "page.png",
                "image",
                state == SourceImportOperationState.Failed ? "failed" : "imported",
                state == SourceImportOperationState.Failed ? "SOURCE_PASSWORD_INVALID" : null,
                1,
                0,
                new SourceImportCounts(ImportedPages: 1)),
        },
        new SourceImportCounts(ImportedPages: 1));

    private static async Task RunAsync(
        FakeHostController host, ImportDockViewModel viewModel, SourceImportOperationState state)
    {
        host.ScriptedReferencePlans.Enqueue(Plan());
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-1"));
        host.ScriptedReferenceReceipts.Enqueue(Receipt(state));
        await viewModel.PlanReferenceImportAsync(
            new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });
        await viewModel.ConfirmReferenceImportAsync();
    }

    [Fact]
    public async Task CompletedReceipt_RequestsExactlyOneRefresh()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        var viewModel = Create(host);

        await RunAsync(host, viewModel, SourceImportOperationState.Completed);

        Assert.Equal(1, host.SourceScanRefreshRequests);
    }

    [Theory]
    [InlineData(SourceImportOperationState.Failed)]
    [InlineData(SourceImportOperationState.Cancelled)]
    public async Task NonCompletedReceipt_RequestsNoRefresh(SourceImportOperationState state)
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        var viewModel = Create(host);

        await RunAsync(host, viewModel, state);

        Assert.Equal(0, host.SourceScanRefreshRequests);
    }

    [Fact]
    public async Task RefreshRequest_CarriesNoAppComputedTargetIdentity()
    {
        // S-2 discriminator (VM seam): the only App -> Host scan interface takes no id/path argument,
        // so a completed import can never smuggle a StableSourceId/folder registry_id into the Host.
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        var viewModel = Create(host);
        await RunAsync(host, viewModel, SourceImportOperationState.Completed);

        Assert.Equal(1, host.SourceScanRefreshRequests);
        var method = typeof(ISourceImportController).GetMethod(nameof(ISourceImportController.RequestSourceScanRefresh));
        Assert.NotNull(method);
        Assert.Empty(method!.GetParameters());
    }

    [Fact]
    public async Task ConfirmInFlight_CompletesOnce_ThenExactlyOneRefresh()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot());
        var viewModel = Create(host);
        var receiptGate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        host.ReferenceReceiptOverride = async () =>
        {
            await receiptGate.Task;
            return Receipt(SourceImportOperationState.Completed);
        };
        host.ScriptedReferencePlans.Enqueue(Plan());
        host.ScriptedReferenceStarts.Enqueue(SourceImportStartResult.Accepted("op-1"));

        await viewModel.PlanReferenceImportAsync(
            new[] { new ReferenceImportSource(@"C:\manga\page.png", IsFolder: false) });
        var confirm = viewModel.ConfirmReferenceImportAsync();
        // No book/selection state feeds the refresh request anymore (S-2): completing the import
        // triggers exactly one refresh regardless of any selection change while it is in flight.
        receiptGate.TrySetResult(true);
        await confirm;

        Assert.Equal(1, host.SourceScanRefreshRequests);
    }
}