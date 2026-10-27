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

    public string? LastRoundTripTitle { get; private set; }

    public event EventHandler? Changed;

    public Task StartAsync(CancellationToken cancellationToken = default)
    {
        StartCalls++;
        return Task.CompletedTask;
    }

    public Task RefreshBooksAsync(CancellationToken cancellationToken = default)
    {
        RefreshCalls++;
        return Task.CompletedTask;
    }

    public bool CreateBookResult { get; set; } = true;

    public Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default) => Task.FromResult(CreateBookResult);

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

    public List<(string BookId, string ChapterId, IReadOnlyList<string> PageIds, string TargetPath)> StartExportCalls { get; } = new();

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
        CancellationToken cancellationToken = default)
    {
        StartExportCalls.Add((bookId, chapterId, orderedPageIds, targetPath));
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
