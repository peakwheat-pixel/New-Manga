using NewManga.CoreClient;

namespace NewManga.App.Services;

public enum HostViewState
{
    Starting,
    Ready,
    AlreadyRunning,
    Failed,
}

/// <summary>UI-facing host state. Deliberately free of OS paths: only typed codes + friendly text.</summary>
public sealed record HostViewSnapshot(
    HostViewState State,
    string StatusLine,
    string ModeLine,
    string? ErrorCode,
    string? ErrorMessage,
    IReadOnlyList<BookSummary> Books,
    int WireFrameCount,
    bool AllRequestsAsciiOnly,
    string? LastChineseRoundTrip)
{
    /// <summary>
    /// READER-WORKBENCH-1 AC3: <see cref="NewManga.Host.DataRootPolicy.WritesAllowed"/> at the last
    /// host transition. The workbench disables its write controls when this is false; headless fakes
    /// default to true so existing UI suites keep exercising the writable path.
    /// </summary>
    public bool WritesAllowed { get; init; } = true;

/// <summary>
/// V11R-A-1: typed code of the last refused Host-controller request (<c>INVALID_REQUEST</c> /
/// <c>TARGET_NOT_FOUND</c> / <c>HOST_READ_ONLY</c> / <c>CANCELLED</c> / <c>IDEMPOTENCY_KEY_REUSED</c> /
/// <c>INVALID_RUN_TRANSITION</c> …); null after the last successful write. V11R-A-2 publishes Run
/// read refusals (for example <c>TARGET_NOT_FOUND</c>) on the same field. Deliberately a code only —
/// never a message, an OS path or a credential — so the channel is safe to render and to log.
/// </summary>
public string? LastError { get; init; }
}

/// <summary>READER-PROGRESS-1: typed outcome of one progress save (never throws into the UI).</summary>
public enum ReaderProgressSaveStatus
{
    /// <summary>Core committed the row (ReadingProgressSnapshot returned).</summary>
    Saved,

    /// <summary>No Core: host is starting / failed / already running.</summary>
    NotReady,

    /// <summary>Host is read-only until parity; nothing was sent to the Core.</summary>
    ReadOnly,

    /// <summary>Core or transport rejected the save; <see cref="ReaderProgressSaveResult.ErrorCode"/> is typed.</summary>
    Failed,
}

/// <summary>READER-PROGRESS-1: result of one <see cref="IReaderProgressSink"/> call.</summary>
public sealed record ReaderProgressSaveResult(
    ReaderProgressSaveStatus Status,
    string? ErrorCode = null,
    double ProgressPercent = 0,
    string? LastPageId = null)
{
    public bool IsSaved => Status == ReaderProgressSaveStatus.Saved;

    public static ReaderProgressSaveResult Saved(double progressPercent, string? lastPageId) =>
        new(ReaderProgressSaveStatus.Saved, null, progressPercent, lastPageId);

    public static ReaderProgressSaveResult NotReady() =>
        new(ReaderProgressSaveStatus.NotReady, "HOST_NOT_READY");

    public static ReaderProgressSaveResult ReadOnly() =>
        new(ReaderProgressSaveStatus.ReadOnly, "HOST_READ_ONLY");

    public static ReaderProgressSaveResult Failed(string code) =>
        new(ReaderProgressSaveStatus.Failed, code);
}

/// <summary>
/// READER-PROGRESS-1: the reader page only needs this one seam to persist its position. The window
/// injects the controller; tests inject a scripted fake. Implementations must never throw — failures
/// come back as <see cref="ReaderProgressSaveResult"/> so a broken save never blocks the UI.
/// </summary>
public interface IReaderProgressSink
{
    Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default);
}

/// <summary>Test seam: the window talks to this, production implementation wraps HostRuntime.</summary>
public interface IHostController : IReaderProgressSink, IRunController, IAsyncDisposable
{
    HostViewSnapshot Snapshot { get; }

    event EventHandler? Changed;

    Task StartAsync(CancellationToken cancellationToken = default);

    Task RefreshBooksAsync(CancellationToken cancellationToken = default);

    /// <summary>Creates the fixed AC3 Chinese vector; false when the host is read-only.</summary>
    Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default);

    Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default);

    /// <summary>
    /// V11R-A-1 (audit P-01, contract §5.1): creates one chapter through the Core
    /// <c>CreateChapter</c> command (protocol minor 8). Returns the new chapter, or null when the
    /// Host is not ready / read-only / the Core refused the request; refusals are recorded as a
    /// typed code on <see cref="HostViewSnapshot.LastError"/> and never throw into the UI.
    /// The Core stays the semantic authority for the title rules (blank titles are rejected by the
    /// Core, duplicate titles are allowed by design); only an empty <paramref name="bookId"/> is
    /// rejected locally before any wire frame is sent.
    /// </summary>
    Task<ChapterSummary?> CreateChapterAsync(
        string bookId,
        string title,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// READER-LIBRARY-WIRE-1 AC1: real reader payload (ListBooks → list_chapters → GetReaderProjection)
    /// for the reader page. Null when the Host is not ready, the library is empty, or the read fails;
    /// the reader then keeps its fixture fallback.
    /// READER-PROGRESS-1: the projection asks for <c>start_position="resume"</c>, so the returned book
    /// carries <see cref="ReaderBookData.InitialPageIndex"/> for the last read page.
    /// CHAPTER-SELECTOR-1: <paramref name="bookId"/>/<paramref name="chapterId"/> select the exact
    /// book and chapter; null keeps the previous defaults (first readable book / its first chapter).
    /// </summary>
    Task<ReaderBookData?> LoadReaderBookAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC1: chapter list of one book (<c>list_chapters</c>) for the reader's chapter
    /// selector. Read-only; returns an empty list when the Host is not ready or the read fails.
    /// </summary>
    Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(
        string bookId,
        CancellationToken cancellationToken = default);

    // ---------------------------------------------------------------------------------------
    // READER-WORKBENCH-1: single-page workbench region data. Reads never throw into the UI (empty /
    // null on an unavailable Host); writes return typed outcomes. Every write carries the revision
    // the UI actually read (optimistic guard); the Host never guesses revision numbers or ids.
    // ---------------------------------------------------------------------------------------

    /// <summary>AC1: ordered pages of one chapter (<c>list_chapter_pages</c>); empty when unavailable.</summary>
    Task<IReadOnlyList<ChapterPageSummary>> ListChapterPagesAsync(
        string chapterId,
        CancellationToken cancellationToken = default);

    /// <summary>AC1: live regions + page pixel extent (<c>list_regions</c>); null when unavailable.</summary>
    Task<RegionPageProjection?> LoadPageRegionsAsync(
        string pageId,
        CancellationToken cancellationToken = default);

    /// <summary>AC1: region revision history (<c>list_region_revisions</c>); null when unavailable.</summary>
    Task<RegionRevisionHistory?> LoadRegionRevisionsAsync(
        string regionId,
        CancellationToken cancellationToken = default);

    /// <summary>AC1: page image bytes through the Host resource channel; null when unavailable.</summary>
    Task<byte[]?> ReadPageImageAsync(
        string pageId,
        CancellationToken cancellationToken = default);

    /// <summary>AC2: retype one region (<c>set_region_type</c>) with the read revision as the guard.</summary>
    Task<RegionOperationResult> SetRegionTypeAsync(
        string regionId,
        string newRegionType,
        int expectedRevision,
        CancellationToken cancellationToken = default);

    /// <summary>AC2: restore one revision into a new revision (<c>restore_region_revision</c>).</summary>
    Task<RegionOperationResult> RestoreRegionRevisionAsync(
        string regionId,
        int revisionNo,
        int expectedRevision,
        CancellationToken cancellationToken = default);

    /// <summary>AC2: manual page rerender (<c>rerender_page</c>) with typed outcome.</summary>
    Task<PageRerenderOutcome> RerenderPageAsync(
        string pageId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// CREDENTIAL-UI-1 AC1/AC2: credential-capable targets (provider profiles + proxy network
    /// profiles) with the Core-reported <c>credential_state</c> (configured|missing). Never returns a
    /// secret; an empty list means no profiles or the Host is not ready.
    /// </summary>
    Task<IReadOnlyList<CredentialTargetOption>> ListCredentialTargetsAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// CREDENTIAL-UI-1 AC1: stores one credential through the <c>credential_put</c> Host command
    /// (two-phase vault + Core ref). <paramref name="intent"/> is <c>create</c> or <c>replace</c>;
    /// implementations return typed outcomes and never throw into the UI.
    /// </summary>
    Task<CredentialOperationResult> PutCredentialAsync(
        string kind,
        string ownerId,
        string intent,
        string secret,
        CancellationToken cancellationToken = default);

    /// <summary>CREDENTIAL-UI-1 AC1: clears one credential through <c>credential_clear</c>.</summary>
    Task<CredentialOperationResult> ClearCredentialAsync(
        string kind,
        string ownerId,
        CancellationToken cancellationToken = default);

    // -------------------------------------------------------------------------------------
    // SETTINGS-PROFILE-UI-1: P15 provider / network profile management + binding slots.
    // Every method returns typed outcomes (never throws into the UI); list methods degrade to an
    // empty list when the Host is not ready. None of these records carries a credential secret.
    // -------------------------------------------------------------------------------------

    Task<IReadOnlyList<ProviderProfileInfo>> ListProviderProfilesAsync(
        CancellationToken cancellationToken = default);

    /// <summary>Creates (<paramref name="profileId"/> null) or updates one provider profile.</summary>
    Task<SettingsProfileResult> SaveProviderProfileAsync(
        string? profileId,
        ProviderProfileDraft draft,
        CancellationToken cancellationToken = default);

    Task<SettingsProfileResult> DeleteProviderProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default);

    Task<IReadOnlyList<NetworkProfileInfo>> ListNetworkProfilesAsync(
        CancellationToken cancellationToken = default);

    /// <summary>Creates (<paramref name="networkProfileId"/> null) or updates one network profile.</summary>
    Task<SettingsProfileResult> SaveNetworkProfileAsync(
        string? networkProfileId,
        NetworkProfileDraft draft,
        CancellationToken cancellationToken = default);

    Task<SettingsProfileResult> DeleteNetworkProfileAsync(
        string networkProfileId,
        CancellationToken cancellationToken = default);

    /// <summary>Sets (<paramref name="networkProfileId"/> non-null) or clears the global network default.</summary>
    Task<SettingsProfileResult> SetNetworkDefaultAsync(
        string? networkProfileId,
        CancellationToken cancellationToken = default);

    /// <summary>Runs the real Core network diagnostic; null when unavailable (never fabricated).</summary>
    Task<NetworkTestInfo?> TestNetworkProfileAsync(
        string networkProfileId,
        string providerProfileId,
        CancellationToken cancellationToken = default);

    Task<NetworkResolveInfo?> ResolveNetworkProfileAsync(
        string? providerProfileId,
        CancellationToken cancellationToken = default);

    Task<SettingsProfileResult> SetProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        string profileId,
        CancellationToken cancellationToken = default);

    Task<SettingsProfileResult> ClearProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        CancellationToken cancellationToken = default);

    Task<ProviderBindingResult?> ResolveProviderBindingAsync(
        string capability,
        CancellationToken cancellationToken = default);

    // ---------------------------------------------------------------------------------------
    // IMPORT-EXPORT-UI-1: user-visible import/export entries. Import goes through the Host grant
    // chain (HostIssuer mints the source grant; the UI never signs anything), export through the
    // Host grant + StartExport chain verified by EXPORT-E2E-CLOSE-1.
    // ---------------------------------------------------------------------------------------

    /// <summary>Host-owned exports directory (the only accepted export destination root).</summary>
    string ExportDirectorySuggestion { get; }

    /// <summary>「导入文件」→ <c>library_import_file</c>（Host grant chain）；typed outcome only.</summary>
    Task<ImportOutcome> ImportFilesAsync(
        string chapterId,
        IReadOnlyList<string> paths,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default);

    /// <summary>「导入文件夹」→ <c>library_import_folder</c>（Host grant chain）；typed outcome only.</summary>
    Task<ImportOutcome> ImportFolderAsync(
        string chapterId,
        string folderPath,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default);

    /// <summary>Pages of one chapter that carry a translated revision (the only exportable input).</summary>
    Task<IReadOnlyList<string>> GetTranslatedPageIdsAsync(
        string chapterId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// StartExport through the Host grant chain; null when the StartExport request was refused.
    /// PDF-EXPORT-UI-1: <paramref name="format"/> is <c>zip</c> or <c>pdf</c>; for PDF
    /// <paramref name="pdfContent"/> selects <c>image_only</c> / <c>searchable_dual_layer</c>
    /// (the Host contract already validates exactly that pair).
    /// </summary>
    Task<ExportStartInfo?> StartExportAsync(
        string bookId,
        string chapterId,
        IReadOnlyList<string> orderedPageIds,
        string targetPath,
        string format = "zip",
        string? pdfContent = null,
        CancellationToken cancellationToken = default);

    Task<ExportSnapshotInfo?> GetExportSnapshotAsync(
        string exportId,
        CancellationToken cancellationToken = default);

    Task<IReadOnlyList<ExportHistoryEntry>> GetExportHistoryAsync(
        CancellationToken cancellationToken = default);

    Task<ExportSnapshotInfo?> CancelExportAsync(
        string exportId,
        CancellationToken cancellationToken = default);

    /// <summary>「打开导出目录」shell action; true only when the Host actually opened it.</summary>
    Task<bool> RevealExportFolderAsync(
        string exportId,
        CancellationToken cancellationToken = default);
}
