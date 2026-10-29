using System.Globalization;
using NewManga.App.Services;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>Scriptable controller for headless UI tests (no sidecars, no window lifecycle).</summary>
public sealed class FakeHostController : IHostController
{
    public FakeHostController(HostViewSnapshot snapshot)
    {
        Snapshot = snapshot;
    }

    public HostViewSnapshot Snapshot { get; set; }

    public int StartCalls { get; private set; }

    public Task? StartGate { get; set; }

    public int RefreshCalls { get; private set; }

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
        return Task.CompletedTask;
    }

    public async Task RefreshBooksAsync(CancellationToken cancellationToken = default)
    {
        RefreshCalls++;
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

    public Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default)
    {
        if (ScriptedSaveResults.Count > 0)
        {
            var scripted = ScriptedSaveResults.Dequeue();
            Progress.Attempts.Add(new FakeProgressAttempt(chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta));
            return Task.FromResult(scripted);
        }

        var result = Progress.Save(ResolveBookForChapter(chapterId), chapterId, pageId, mode, scrollOffsetY, elapsedSecondsDelta);
        return Task.FromResult(result);
    }

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

    public List<string> TaskProjectionRequests { get; } = new();

    public List<(string RunId, string IdempotencyKey)> RetriedFailedRuns { get; } = new();

    public Queue<RunStartInfo?> ScriptedStartRuns { get; } = new();

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
            PublishLastError(scripted is null ? "SCRIPTED_FAILURE" : null);
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
