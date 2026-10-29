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
}
