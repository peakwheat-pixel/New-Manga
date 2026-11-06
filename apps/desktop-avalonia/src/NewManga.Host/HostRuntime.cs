using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.CoreClient.Diagnostics;
using NewManga.Host.Credentials;
using NewManga.CoreClient.Transport;
using NewManga.Host.Resources;
using NewManga.Host.Sources;
using System.Text;
using ScanStatus = NewManga.Host.Sources.SourceScanStatus;

namespace NewManga.Host;

/// <summary>
/// Host lifecycle: single instance → legacy coexistence → read-only policy → first-run backup →
/// sidecar discovery → both sidecars (core_service protocol 2.3 + host_bridge wire v1). Every
/// failure becomes a typed <see cref="HostStartResult"/> (never a crash), with stderr logs on disk.
/// </summary>
public sealed class HostRuntime : IAsyncDisposable
{
    private readonly HostOptions _options;
    private readonly HostLog _log;
    private SingleInstanceGuard? _guard;
    private DataRootPolicy? _policy;
    private bool _disposed;

    // FEA-11-RUN-GRANT-2A (card S-2/S-4): the in-memory cache of Core-authoritative source identities
    // (source_id → version_id + entries[]), learned ONLY from unchanged ScanSourceSync responses. The
    // Run minting path reads its version from here and never falls back to the old constant "1" (L-G15).
    private readonly SourceIdentityCache _sourceIdentities;

    // The host_bridge/core_service pipes are request/response only: page reads are serialized.
    private readonly SemaphoreSlim _readerIoGate = new(1, 1);

    private HostRuntime(HostOptions options, HostLog log)
    {
        _options = options;
        _log = log;
        // FEA-11-RUN-GRANT-2A (S-4): bounded identity cache driven by the same clock seam as the scan
        // slice; it is created before both producers (scan executor) and consumers (Run authorizer).
        _sourceIdentities = SourceIdentityCache.FromTimeProvider(options.SourceScanTimeProvider);
        // V11R-A-5: conservative pre-start gate (closed until StartInternalAsync decides). The real
        // policy is derived from CoexistenceRules (legacy shell / explicit --parity=false).
        _policy = DataRootPolicy.For(options.DataRoot, HostMode.ReadOnlyUntilParity);
    }

    /// <summary>V11R-A-6: last startup contract self check result (NotRun until the host starts).</summary>
    public StartupSelfCheckResult SelfCheck { get; private set; } = StartupSelfCheckResult.NotRun;

    public HostStartResult Result { get; private set; } =
        new(HostStatus.Failed, HostMode.ReadOnlyUntilParity, "HOST_NOT_STARTED", "host not started", null);

    public CoreServiceClient? CoreService { get; private set; }

    /// <summary>
    /// FEA-11-RUN-GRANT-1: the bounded prepared-Run slice ledger (prepared id
    /// -> the frozen ``{command, scope}`` pair the Run will accept). The Core
    /// client owns the preparedRun object itself; AcceptRun only has the id, so
    /// the Host remembers the two frozen fields here to run the Run
    /// pre-authorization (R-4/R1-02③). Extracted as a standalone class so the
    /// AcceptRun lookup/expiry behaviour is unit-testable without sidecars.
    /// </summary>
    private readonly PreparedRunSlices _preparedSlices = new();

    /// <summary>The production Run pre-dispatch authorization orchestration
    /// (R-4/R-6/R-7/R1-01/R1-04). Null until the source-read stack exists.</summary>
    private RunSourceAuthorizer? _runAuthorizer;

    public async Task<PreparedRunPreview> PrepareRunAsync(System.Text.Json.JsonElement request,
        CancellationToken ct = default)
    {
        var core = CoreService ?? throw new InvalidOperationException("Core unavailable");
        var preview = await core.PrepareRunAsync(request, ct).ConfigureAwait(false);
        _preparedSlices.Remember(preview.PreparedRunId, request, preview.ExpiresAt);
        return preview;
    }

    public async Task<System.Text.Json.JsonElement> AcceptRunAsync(string preparedRunId, int generation,
        string idempotencyKey, CancellationToken ct = default)
    {
        if (!Policy.WritesAllowed) throw new InvalidOperationException("Host is read-only");
        // FEA-11-RUN-GRANT-1 (R-4/R1-02③/R2-03): AcceptRun triggers step
        // execution, so the Run's source reads are authorized first from the
        // frozen command/scope pair captured by PrepareRun. A missing/expired
        // slice is typed RUN_STALE_PREVIEW (R1-11: this API now requires the
        // same-process PrepareRunAsync; documented in the Handoff limitations).
        await AuthorizePreparedRunForAcceptAsync(
            _preparedSlices, _runAuthorizer, preparedRunId, ct).ConfigureAwait(false);
        return await (CoreService ?? throw new InvalidOperationException("Core unavailable"))
            .AcceptRunAsync(preparedRunId, generation, idempotencyKey, ct).ConfigureAwait(false);
    }

    /// <summary>
    /// Review r2 R2-03: the exact AcceptRun source-authorization wiring as a
    /// testable seam (the production ``AcceptRunAsync`` above delegates here).
    /// Takes the frozen ``{command, scope}`` from the prepared-slice ledger
    /// (missing/expired -&gt; typed ``RUN_STALE_PREVIEW``) and runs the same
    /// best-effort authorizer the dispatcher hook uses.
    /// </summary>
    public static async Task AuthorizePreparedRunForAcceptAsync(
        PreparedRunSlices slices,
        RunSourceAuthorizer? authorizer,
        string preparedRunId,
        CancellationToken token)
    {
        ArgumentNullException.ThrowIfNull(slices);
        var slice = slices.Take(preparedRunId);
        if (authorizer is not null)
        {
            await authorizer.AuthorizePreparedRunAsync(slice.Command, slice.Scope, token)
                .ConfigureAwait(false);
        }
    }

    public HostBridgeClient? HostBridge { get; private set; }

    /// <summary>GRANT-ISSUER-1: host-control grant chain + whitelisted shell actions (null until ready).</summary>
    public HostGrantCoordinator? Grants { get; private set; }
    public SourceAccessRegistry? Registry { get; private set; }

    public SourceReadCoordinator? Sources { get; private set; }

    /// <summary>FEA-11 (C-17 §5.2): the Host durable operation journal and
    /// acknowledgement coordinator (null when the source registry is off).</summary>
    public SourceOperationCoordinator? Operations { get; private set; }

    /// <summary>CREDENTIAL-PORT-1: OS-vault credential port + Core bind/clear bridge (null when unavailable).</summary>
    public HostCredentialCoordinator? Credentials { get; private set; }

    /// <summary>GRANT-ISSUER-1: the production command dispatcher, including the Host-local commands.</summary>
    public HostCommandDispatcher? Commands { get; private set; }

    /// <summary>
    /// FEA-11-SCAN-1 (I-1/I-7): the Host-side read-only periodic source scan scheduler. Created only
    /// after the Host is ready; null when referenced import is disabled or the Host never became
    /// ready. It is the ONLY producer of <see cref="SourceScanStatus"/> and never writes Core state.
    /// </summary>
    public SourceScanScheduler? ScanScheduler { get; private set; }

    /// <summary>
    /// FEA-11-RUN-GRANT-2A (S-3): the production scan executor, kept so the Run path can perform at
    /// most ONE bounded on-demand <c>ScanSourceSync</c> per cold source (never a retry loop). Null until
    /// the scan slice starts and again after it stops.
    /// </summary>
    private HostSourceScanExecutor? _scanExecutor;

    /// <summary>
    /// FEA-11-WATCH-1 (AC-W1): the Host-only read-only directory watcher. Armed after Ready over the
    /// scheduler's registered targets only; disarmed (zero future hints) before the scheduler stops.
    /// Null when watchers are disabled or the Host never became ready.
    /// </summary>
    public SourceWatcher? Watcher { get; private set; }

    /// <summary>
    /// FEA-11-SCAN-1 (I-6 / AC-S5): the closed in-process scan status snapshot — the slice's only
    /// observable surface (no wire command, no DB row, no file). Contains typed source ids, result
    /// enums, counts and stable codes only; never absolute paths, grants, sessions or exception text.
    /// </summary>
    public ScanStatus SourceScanStatus =>
        ScanScheduler?.Snapshot() ?? ScanStatus.Disabled(ResolvedSourceScanIntervalSeconds());

    /// <summary>
    /// FEA-11-SCAN-1 (I-2 / AC-S2): registers a source of a completed referenced import as a periodic
    /// scan target. In-memory only (L-A/L-C); re-registering the same <paramref name="sourceId"/>
    /// overwrites it so the target set never grows on repeated imports. Returns false when the Host
    /// is not accepting targets (not ready / referenced import disabled / invalid identity).
    /// </summary>
    public bool RegisterSourceScanTarget(
        string sourceId,
        string path,
        IReadOnlyList<string> projectIds,
        string version = "1")
    {
        var scheduler = ScanScheduler;
        if (scheduler is null || !_options.ReferencedImportEnabled
            || string.IsNullOrWhiteSpace(sourceId) || string.IsNullOrWhiteSpace(path)
            || projectIds.Count == 0)
        {
            return false;
        }

        return scheduler.RegisterTarget(new SourceScanTarget(sourceId, path, projectIds, version));
    }

    /// <summary>
    /// FEA-11-SCAN-2 (B1 / AC-S2-2 / S-2): App-triggered scan-target refresh. Only a completed
    /// referenced import calls this — the App never computes authoritative target ids; the Host
    /// enumerates the Core's read-only targets and re-verifies its own persistent registry. The
    /// refresh runs in the background (never blocks the caller or Host start). Returns false when
    /// the scan slice is not active on this Host.
    /// </summary>
    public bool RequestSourceScanRefresh()
    {
        var scheduler = ScanScheduler;
        if (scheduler is null || !_options.SourceScanColdStartEnumeration)
        {
            return false;
        }

        _ = RefreshSourceScanTargetsAsync(scheduler);
        return true;
    }

    private async Task RefreshSourceScanTargetsAsync(SourceScanScheduler scheduler)
    {
        try
        {
            await scheduler.RefreshTargetsAsync(CancellationToken.None).ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            // Enumeration is observability-only for the Host start path; the typed verdict is already
            // on SourceScanStatus. Never let a refresh fault escape as an unobserved task exception.
            _log.Warn("source scan refresh failed: " + error.GetType().Name);
        }
    }

    public HostLog Log => _log;

    public HostOptions Options => _options;

    public DataRootPolicy Policy => _policy!;

    public HostMode Mode => _policy?.Mode ?? HostMode.ReadOnlyUntilParity;

    public LegacyShellState LegacyShell { get; private set; } = LegacyShellState.NotDetected;

    public FirstRunBackupResult? Backup { get; private set; }

    public string WireEvidenceDirectory => Path.Combine(_options.LogDirectory, "wire");

    public static async Task<HostRuntime> StartAsync(HostOptions options, CancellationToken cancellationToken = default)
    {
        var runtime = new HostRuntime(options, new HostLog(options.LogDirectory));
        try
        {
            await runtime.StartInternalAsync(cancellationToken).ConfigureAwait(false);
            return runtime;
        }
        catch
        {
            // REALUSE-DATA-SAFETY-2 review r1 M1: an escaping failure would drop a runtime that
            // already owns the Win32 single-instance mutex, so the next start would report
            // AlreadyRunning forever. The normal failure paths return a Failed result instead of
            // throwing, but release the mutex here for the ones that do escape.
            try
            {
                await runtime.DisposeAsync().ConfigureAwait(false);
            }
            catch (Exception disposeFailure) when (
                disposeFailure is ObjectDisposedException or IOException or InvalidOperationException)
            {
                // Keep the original failure; only the exception type is recorded.
                System.Diagnostics.Debug.WriteLine(
                    $"failed runtime cleanup failed: {disposeFailure.GetType().Name}");
            }

            throw;
        }
    }

    public async Task<IReadOnlyList<BookSummary>> ListBooksAsync(CancellationToken cancellationToken = default)
    {
        var core = CoreService ?? throw NotReady();
        return await core.ListBooksAsync(cancellationToken).ConfigureAwait(false);
    }

    /// <summary>GRANT-ISSUER-1: creates a chapter (CreateChapter, protocol minor 8) for imports.</summary>
    public async Task<ChapterSummary> CreateChapterAsync(
        string bookId,
        string title,
        CancellationToken cancellationToken = default)
    {
        if (!Policy.WritesAllowed)
        {
            throw new ReadOnlyHostException($"host is read-only ({Policy.Reason}); writes to production data are disabled until S2 parity");
        }

        var core = CoreService ?? throw NotReady();
        var response = await core.SendAsync(
                "CreateChapter",
                CoreProtocol.CreateMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteString("title", title);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = response.Result ?? throw new SidecarException(
            SidecarErrorCode.MalformedResponse,
            SidecarSpec.CoreServiceName,
            "CreateChapter returned no result",
            _log.CoreServiceStderrPath);
        return new ChapterSummary(
            result.GetProperty("chapter_id").GetString() ?? string.Empty,
            result.GetProperty("title").GetString() ?? string.Empty,
            result.GetProperty("chapter_number").GetString() ?? string.Empty,
            result.GetProperty("sort_order").GetInt32());
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-1 AC2: the .nmbak package face through the Core. Listing is a read;
    /// create/delete/restore are writes and therefore obey the same read-only policy as every other
    /// write path (a read-only Host must never mutate the backups directory behind the UI's back).
    /// </summary>
    public async Task<IReadOnlyList<BackupPackageInfo>> ListBackupsAsync(
        CancellationToken cancellationToken = default)
    {
        var core = CoreService ?? throw NotReady();
        return await core.ListBackupsAsync(cancellationToken).ConfigureAwait(false);
    }

    public async Task<BackupPackageInfo> CreateBackupAsync(
        string backupType = "manual",
        CancellationToken cancellationToken = default)
    {
        RequireWritesAllowed();
        var core = CoreService ?? throw NotReady();
        return await core.CreateBackupAsync(backupType, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: retry persisted failed removals (a write).</summary>
    public async Task<CleanupOutcomeInfo> RetryPendingCleanupsAsync(CancellationToken cancellationToken = default)
    {
        RequireWritesAllowed();
        var core = CoreService ?? throw NotReady();
        return await core.RetryPendingCleanupsAsync(cancellationToken).ConfigureAwait(false);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: plugin inventory (plugins.list), read-only.</summary>
    public async Task<PluginListInfo> ListPluginsAsync(CancellationToken cancellationToken = default)
    {
        var core = CoreService ?? throw NotReady();
        return await core.ListPluginsAsync(cancellationToken).ConfigureAwait(false);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: the global plugin master switch (a write).</summary>
    public async Task<bool?> SetPluginsGlobalEnabledAsync(bool enabled, CancellationToken cancellationToken = default)
    {
        RequireWritesAllowed();
        var core = CoreService ?? throw NotReady();
        return await core.SetPluginsGlobalEnabledAsync(enabled, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: one plugin's switch (a write).</summary>
    public async Task<bool?> SetPluginEnabledAsync(
        string pluginId,
        bool enabled,
        CancellationToken cancellationToken = default)
    {
        RequireWritesAllowed();
        var core = CoreService ?? throw NotReady();
        return await core.SetPluginEnabledAsync(pluginId, enabled, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: read-only cache pre-flight (cleanup.preview).</summary>
    public async Task<CleanupPreviewInfo> GetCleanupPreviewAsync(CancellationToken cancellationToken = default)
    {
        var core = CoreService ?? throw NotReady();
        return await core.GetCleanupPreviewAsync(cancellationToken).ConfigureAwait(false);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: remove the safe cache population (cleanup.run).</summary>
    public async Task<CleanupOutcomeInfo> RunCleanupAsync(CancellationToken cancellationToken = default)
    {
        RequireWritesAllowed();
        var core = CoreService ?? throw NotReady();
        return await core.RunCleanupAsync(cancellationToken).ConfigureAwait(false);
    }

    public async Task DeleteBackupAsync(string backupId, CancellationToken cancellationToken = default)
    {
        RequireWritesAllowed();
        var core = CoreService ?? throw NotReady();
        await core.DeleteBackupAsync(backupId, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>Restore is the most destructive write: policy check first, then the Core's own rollback gate.</summary>
    public async Task<string> RestoreBackupAsync(string backupId, CancellationToken cancellationToken = default)
    {
        RequireWritesAllowed();
        var core = CoreService ?? throw NotReady();
        return await core.RestoreBackupAsync(backupId, cancellationToken).ConfigureAwait(false);
    }

    private void RequireWritesAllowed()
    {
        if (!Policy.WritesAllowed)
        {
            throw new ReadOnlyHostException($"host is read-only ({Policy.Reason}); writes to production data are disabled until S2 parity");
        }
    }

    /// <summary>
    /// Creates a book through the Core — refused while the host is read-only (legacy Tauri shell
    /// detected, explicit <c>--parity=false</c>, or the host is not ready). V11R-A-5: the shipped
    /// product is writable by default; tests use an isolated data root.
    /// </summary>
    public async Task<BookSummary> CreateBookAsync(string title, CancellationToken cancellationToken = default)
    {
        if (!Policy.WritesAllowed)
        {
            throw new ReadOnlyHostException($"host is read-only ({Policy.Reason}); writes to production data are disabled until S2 parity");
        }

        var core = CoreService ?? throw NotReady();
        return await core.CreateBookAsync(title, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>
    /// AC3 end-to-end vector: create the fixed Chinese title then list it back and require exact
    /// string equality (any mojibake fails here). Only valid on an isolated writable data root.
    /// </summary>
    public async Task<ChineseRoundTripResult> RoundTripChineseTitleAsync(
        string title,
        CancellationToken cancellationToken = default)
    {
        var created = await CreateBookAsync(title, cancellationToken).ConfigureAwait(false);
        var books = await ListBooksAsync(cancellationToken).ConfigureAwait(false);
        var found = false;
        foreach (var book in books)
        {
            if (string.Equals(book.Title, title, StringComparison.Ordinal))
            {
                found = true;
                break;
            }
        }

        return new ChineseRoundTripResult(title, created.Title, found);
    }

    /// <summary>
    /// READER-LIBRARY-WIRE-1: chapter navigation for the reader page (read-only).
    /// CHAPTER-SELECTOR-1: serialized on the reader I/O gate — the core_service pipe is strictly
    /// request/response, so a chapter list must not cross a concurrent page/projection read.
    /// </summary>
    public async Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(string bookId, CancellationToken cancellationToken = default)
    {
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core.ListChaptersAsync(bookId, cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-LIBRARY-WIRE-1: ordered reader projection (pages + layout) for one chapter.
    /// READER-PROGRESS-1: <paramref name="startPosition"/> defaults to <c>resume</c> so the Core echoes
    /// the persisted page (book, chapter, mode) and never mutates it on read.
    /// CHAPTER-SELECTOR-1: serialized on the same reader I/O gate as page reads.
    /// </summary>
    public async Task<ReaderProjection> GetReaderProjectionAsync(
        string chapterId,
        string startPosition = ReaderStartPosition.Resume,
        CancellationToken cancellationToken = default)
    {
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core
                .GetReaderProjectionAsync(chapterId, startPosition: startPosition, cancellationToken: cancellationToken)
                .ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-WORKBENCH-1 AC1: ordered page navigation for one chapter (<c>list_chapter_pages</c>,
    /// protocol minor 6). Read-only; shares the reader I/O gate so a page list never crosses a
    /// concurrent projection/page-image response on the strictly request/response core pipe.
    /// </summary>
    public async Task<IReadOnlyList<ChapterPageSummary>> ListChapterPagesAsync(
        string chapterId,
        CancellationToken cancellationToken = default)
    {
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core.ListChapterPagesAsync(chapterId, cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-WORKBENCH-1 AC1: live regions of one page + the page pixel extent the workbench
    /// overlay projects normalized geometry through (<c>list_regions</c>). Read-only; same gate.
    /// </summary>
    public async Task<RegionPageProjection> ListRegionsAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core.ListRegionsAsync(pageId, cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-WORKBENCH-1 AC1: frozen region revision history (<c>list_region_revisions</c>).
    /// Read-only; same gate.
    /// </summary>
    public async Task<RegionRevisionHistory> ListRegionRevisionsAsync(
        string regionId,
        CancellationToken cancellationToken = default)
    {
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core.ListRegionRevisionsAsync(regionId, cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-WORKBENCH-1 AC2/AC3: retype one region (<c>set_region_type</c>). It is a write, so the
    /// read-only-until-parity policy refuses it with a typed <see cref="ReadOnlyHostException"/>
    /// BEFORE any gate is taken or any frame is written to the Core. The caller must pass the
    /// revision it actually read as <paramref name="expectedRevision"/>; concurrent writes surface
    /// as the Core's typed INPUT_REVISION_CHANGED and are never guessed away here.
    /// </summary>
    public async Task<RegionWriteSnapshot> SetRegionTypeAsync(
        string regionId,
        string newRegionType,
        int? expectedRevision = null,
        CancellationToken cancellationToken = default)
    {
        RequireWrites($"region retype ({regionId})");
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core
                .SetRegionTypeAsync(regionId, newRegionType, expectedRevision, cancellationToken)
                .ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-WORKBENCH-1 AC2/AC3: restore one region revision into a NEW revision
    /// (<c>restore_region_revision</c>). Read-only policy refuses before any Core frame; the
    /// optimistic guard is the caller's read revision, never a guessed one.
    /// </summary>
    public async Task<RegionWriteSnapshot> RestoreRegionRevisionAsync(
        string regionId,
        int revisionNo,
        int expectedRevision,
        CancellationToken cancellationToken = default)
    {
        RequireWrites($"region revision restore ({regionId})");
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core
                .RestoreRegionRevisionAsync(regionId, revisionNo, expectedRevision, cancellationToken)
                .ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-WORKBENCH-1 AC2/AC3: manual page rerender (<c>rerender_page</c>). Read-only policy
    /// refuses before any Core frame; the same reader I/O gate serializes the write with page reads.
    /// </summary>
    public async Task<PageRerenderResult> RerenderPageAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        RequireWrites($"page rerender ({pageId})");
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core.RerenderPageAsync(pageId, cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    private void RequireWrites(string what)
    {
        if (!Policy.WritesAllowed)
        {
            throw new ReadOnlyHostException(
                $"host is read-only ({Policy.Reason}); {what} is disabled until S2 parity");
        }
    }

    /// <summary>
    /// READER-PROGRESS-1: persists reading progress through the frozen Core command
    /// (<c>SaveReadingProgress</c>). It is a write, so the read-only-until-parity policy refuses it
    /// with a typed <see cref="ReadOnlyHostException"/> and no request reaches the Core. The
    /// core_service pipe is strictly request/response, so this shares the reader I/O gate with page
    /// reads (concurrent frames would cross responses).
    /// </summary>
    public async Task<ReadingProgressSnapshot> SaveReadingProgressAsync(
        string chapterId,
        string mode,
        string pageId,
        double? scrollOffsetY = null,
        double? elapsedSecondsDelta = null,
        CancellationToken cancellationToken = default)
    {
        if (!Policy.WritesAllowed)
        {
            throw new ReadOnlyHostException(
                $"host is read-only ({Policy.Reason}); reading progress is not persisted until parity");
        }

        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            return await core
                .SaveReadingProgressAsync(
                    chapterId,
                    mode,
                    pageId,
                    scrollOffsetY,
                    elapsedSecondsDelta,
                    cancellationToken)
                .ConfigureAwait(false);
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// READER-LIBRARY-WIRE-1: page image bytes through the existing resource channel —
    /// Core resolve_page_resource → host_bridge issue/resolve grant → Host tile channel
    /// (handle-verified, digest-checked whole-file read). No path or digest leaves the Host.
    /// The resource pipe is strictly request/response, so the whole sequence is serialized.
    /// </summary>
    public async Task<byte[]> ReadPageImageAsync(string pageId, CancellationToken cancellationToken = default, string? password = null)
    {
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            var bridge = HostBridge ?? throw NotReady();
            var resolved = await ResolvePageResourceWithSecretAsync(core, pageId, password, cancellationToken)
                .ConfigureAwait(false);
            var issued = await bridge.IssueAsync(resolved.ResourceId, resolved.Revision, cancellationToken).ConfigureAwait(false);
            try
            {
                var grant = await bridge.ResolveAsync(issued.GrantId, cancellationToken).ConfigureAwait(false);
                var root = grant.ScopeClass switch
                {
                    "derived-read-only" => Path.Combine(_options.DataRoot, "derived"),
                    "managed-read-only" => _options.ManagedRoot ?? Path.Combine(_options.DataRoot, "managed"),
                    _ => throw new BridgeException("SCOPE_NOT_SERVABLE", grant.ScopeClass),
                };
                if (grant.Size <= 0 || grant.Size > int.MaxValue)
                {
                    throw new BridgeException("REF_MALFORMED", $"grant size out of range: {grant.Size}");
                }

                var absolutePath = Path.Combine(root, grant.RelPath);
                var channel = new TileChannel();
                var request = new TileGrantRequest(
                    resolved.ResourceId,
                    resolved.Revision,
                    absolutePath,
                    root,
                    grant.Size,
                    new[] { new TileDescriptor(0, 0, (int)grant.Size, grant.Sha256) });
                var handle = channel.Issue(request).Handle;
                try
                {
                    return channel.ReadTile(handle, 0).Bytes;
                }
                finally
                {
                    channel.Revoke(handle);
                }
            }
            finally
            {
                try
                {
                    await bridge.RevokeAsync(issued.GrantId, cancellationToken).ConfigureAwait(false);
                }
                catch (Exception ex) when (ex is BridgeException or SidecarException or OperationCanceledException)
                {
                    // best effort: the grant expires on its own; the read already returned or threw
                }
            }
        }
        finally
        {
            _readerIoGate.Release();
        }
    }

    /// <summary>
    /// C-16 v1.1 §3.1 Host fresh-grant protocol: on a typed
    /// SOURCE_PASSWORD_REQUIRED (and only when the caller supplied a password)
    /// check the capability BEFORE creating any secret file, write one DPAPI
    /// token, clone every live grant scope as a fresh Secret-G, retry the
    /// resolve exactly once, then always revoke the clones and delete any
    /// unconsumed token. A missing capability or absent password stays typed.
    /// </summary>
    private async Task<ResolvedPageResource> ResolvePageResourceWithSecretAsync(
        CoreServiceClient core, string pageId, string? password, CancellationToken cancellationToken)
    {
        try
        {
            return await core.ResolvePageResourceAsync(pageId, cancellationToken).ConfigureAwait(false);
        }
        catch (CoreOperationException error) when (
            error.Code == "SOURCE_PASSWORD_REQUIRED" && password is not null)
        {
            var sources = Sources ?? throw new CoreOperationException(
                "CORE_CAPABILITY_MISSING", "protocol", false, "source registry unavailable", null);
            if (!await sources.SupportsResolveSecretAsync(cancellationToken).ConfigureAwait(false))
                throw new CoreOperationException(
                    "CORE_CAPABILITY_MISSING", "protocol", false,
                    "core does not advertise source.resolve-secret/1", null);
            var (token, secretPath) = SourceSecretStore.WritePassword(
                _options.DataRoot, Encoding.UTF8.GetBytes(password));
            var expiresAt = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0 + 60;
            try
            {
                await sources.IssueSecretGrantsAsync(
                    sources.IssuedGrantIds, token, secretPath, expiresAt, cancellationToken)
                    .ConfigureAwait(false);
                return await core.ResolvePageResourceAsync(pageId, cancellationToken)
                    .ConfigureAwait(false);
            }
            finally
            {
                try { await sources.RevokeSecretGrantsAsync(CancellationToken.None).ConfigureAwait(false); }
                catch { /* best effort: grants expire on their own */ }
                SourceSecretStore.DeleteIfPresent(secretPath);
            }
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        StopSourceWatcher();
        await StopSourceScanSchedulerAsync().ConfigureAwait(false);
        if (HostBridge is not null)
        {
            await HostBridge.DisposeAsync().ConfigureAwait(false);
            HostBridge = null;
        }

        if (CoreService is not null)
        {
            await CoreService.DisposeAsync().ConfigureAwait(false);
            CoreService = null;
        }

        _guard?.Dispose();
        _guard = null;
        _log.Dispose();
    }

    private async Task StartInternalAsync(CancellationToken cancellationToken)
    {
        try
        {
            if (!SingleInstanceGuard.TryAcquire(_options.MutexName, out var guard))
            {
                _log.Warn("single-instance mutex already owned; exiting without spawning sidecars");
                Result = HostStartResult.AlreadyRunning();
                return;
            }

            _guard = guard!;
            _log.Info($"single-instance acquired: {guard!.Name} (abandoned_recovered={guard.RecoveredAbandoned})");
            if (guard!.RecoveredAbandoned)
            {
                _log.Warn("recovered abandoned single-instance mutex from a previous host");
            }

            LegacyShell = _options.DetectLegacyShell
                ? new LegacyShellDetector(_options.ProcessProbe).Detect()
                : LegacyShellState.NotDetected;
            if (LegacyShell.Detected)
            {
                _log.Warn($"legacy shell detected (pid {string.Join(',', LegacyShell.ProcessIds)}); entering read-only mode");
            }

            var decision = CoexistenceRules.Decide(LegacyShell.Detected, _options.ParityReached);
            _policy = DataRootPolicy.For(_options.DataRoot, decision.Mode);
            _log.Info($"mode={decision.Mode} reason={decision.Reason}");

            if (_options.FirstRunBackupEnabled)
            {
                Backup = FirstRunBackup.EnsureBackup(_options.DataRoot, Path.Combine(_options.DataRoot, "backups"));
                _log.Info(Backup.Created
                    ? $"first-run backup created: {Backup.FileName}"
                    : $"first-run backup skipped: {Backup.SkippedReason}");
            }

            SidecarBundle bundle;
            try
            {
                bundle = SidecarLocator.Locate(_options.SidecarDirectoryOverride);
            }
            catch (SidecarException ex)
            {
                Fail(ex);
                return;
            }

            var managedRoot = _options.ManagedRoot ?? Path.Combine(_options.DataRoot, "managed");
            var derivedRoot = Path.Combine(_options.DataRoot, "derived");
            var catalogDb = Path.Combine(_options.DataRoot, "catalog", "catalog.sqlite");
            Directory.CreateDirectory(derivedRoot);
            Directory.CreateDirectory(managedRoot);
            Directory.CreateDirectory(Path.GetDirectoryName(catalogDb)!);
            if (_options.EnableWireEvidence)
            {
                Directory.CreateDirectory(WireEvidenceDirectory);
            }

            var coreWire = _options.EnableWireEvidence ? Path.Combine(WireEvidenceDirectory, "core-service.ndjson") : null;
            CoreService = await CoreServiceClient.StartAsync(
                new CoreServiceOptions
                {
                    ExecutablePath = bundle.CoreServicePath,
                    DataRoot = _options.DataRoot,
                    DerivedRoot = derivedRoot,
                    CatalogDbPath = catalogDb,
                    ManagedRoot = managedRoot,
                    ReferencedImportEnabled = _options.ReferencedImportEnabled,
                    StderrLogPath = _log.CoreServiceStderrPath,
                    WireLogPath = coreWire,
                    StartupTimeout = _options.StartupTimeout,
                    RequestTimeout = _options.RequestTimeout,
                },
                cancellationToken).ConfigureAwait(false);
            _log.Info($"core_service ready ({CoreService.Wire.Count} wire frames)");

            var bridgeWire = _options.EnableWireEvidence ? Path.Combine(WireEvidenceDirectory, "host-bridge.ndjson") : null;
            HostBridge = await HostBridgeClient.StartAsync(
                new HostBridgeOptions
                {
                    ExecutablePath = bundle.HostBridgePath,
                    DerivedRoot = derivedRoot,
                    ManagedRoot = managedRoot,
                    CatalogDbPath = catalogDb,
                    StderrLogPath = _log.HostBridgeStderrPath,
                    WireLogPath = bridgeWire,
                    StartupTimeout = _options.StartupTimeout,
                    RequestTimeout = _options.RequestTimeout,
                },
                cancellationToken).ConfigureAwait(false);
            _log.Info($"host_bridge ready ({HostBridge.Wire.Count} wire frames)");

            // CREDENTIAL-PORT-1: the credential port does not depend on the host-control session;
            // construct it first so put/clear stay available even if grant issuance is down.
            try
            {
                var credentialStore = new WindowsCredentialStore();
                Credentials = new HostCredentialCoordinator(
                    new CoreCredentialBridge(CoreService, _options.RequestTimeout),
                    credentialStore,
                    _options.LogDirectory);
                _log.Info("credential port ready (Windows Credential Manager)");
            }
            catch (Exception ex) when (ex is DllNotFoundException or PlatformNotSupportedException or EntryPointNotFoundException)
            {
                _log.Warn($"credential port unavailable: {ex.Message}");
            }

            async Task<HostCommandResult> HostLocalAsync(
                string name,
                System.Text.Json.JsonElement payload,
                CancellationToken token)
            {
                if (HostCommandRegistry.SourceCommandNames.Contains(name))
                {
                    if (name is not ("source_list_roots" or "get_import_receipt")) RequireWritesAllowed();
                    var sources = Sources ?? throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
                    return new HostCommandResult(name, HostCommandStatus.Implemented, HostCommandChannel.HostLocal,
                        await sources.InvokeAsync(name, payload, token).ConfigureAwait(false));
                }
                if (name == "source_get_sync_capabilities")
                {
                    var items = await RunCapabilityProbeAsync().ConfigureAwait(false);
                    return new HostCommandResult(
                        name, HostCommandStatus.Implemented,
                        HostCommandChannel.HostLocal,
                        System.Text.Json.JsonSerializer.SerializeToElement(new { items }));
                }
                if (name is HostCredentialCoordinator.PutCommand or HostCredentialCoordinator.ClearCommand)
                {
                    var credentials = Credentials
                        ?? throw new CredentialPortException(
                            "CREDENTIAL_STORE_UNAVAILABLE",
                            "the Host credential port is unavailable on this machine");
                    return await credentials.HandleCommandAsync(name, payload, token).ConfigureAwait(false);
                }

                var grants = Grants
                    ?? throw new HostCommandNotSupportedException(HostCommandRegistry.Get(name));
                return await grants.HandleCommandAsync(name, payload, token).ConfigureAwait(false);
            }

            // FEA-11 (C-17 §5.2): journal-wrap the operation-kind writes. The
            // Host journals *before* the Core call and records the commit after
            // it; ACK/recovery/failure stay on the operation face.
            async Task<(string OperationId, System.Text.Json.JsonElement Result)> SourceOperationJournalAsync(
                string name, System.Text.Json.JsonElement payload,
                Func<System.Text.Json.JsonElement, CancellationToken, Task<NewManga.CoreClient.Wire.CoreResponse>> call,
                CancellationToken token)
            {
                var operations = Operations ?? throw new CoreOperationException(
                    "CORE_UNAVAILABLE", "unavailable", false, "source operation journal unavailable", null);
                var registry = Registry ?? throw new CoreOperationException(
                    "SOURCE_REGISTRY_UNAVAILABLE", "protocol", false,
                    "source registry unavailable", null);
                var orchestrator = new NewManga.Host.Sources.HostOperationOrchestrator(
                    operations,
                    registry,
                    SourceSyncCapabilityAsync,
                    async (operationId, cancellationToken) =>
                    {
                        var lookup = await CoreService.SendAsync(
                                "source_get_operation", 3,
                                writer =>
                                {
                                    writer.WriteStartObject();
                                    writer.WriteString("operation_id", operationId);
                                    writer.WriteEndObject();
                                },
                                _options.RequestTimeout, cancellationToken)
                            .ConfigureAwait(false);
                        return lookup.Result ?? default;
                    });
                return await orchestrator.ApplyAsync(name, payload, call, token)
                    .ConfigureAwait(false);
            }

            async Task SourceSyncCapabilityAsync(
                string name, CancellationToken token)
            {
                var ping = await CoreService.SendAsync(
                        "core.ping", 3,
                        writer => writer.WriteStartObject(),
                        _options.RequestTimeout, token)
                    .ConfigureAwait(false);
                var advertised = new HashSet<string>(StringComparer.Ordinal);
                if (ping.Result?.ValueKind == System.Text.Json.JsonValueKind.Object
                    && ping.Result.Value.TryGetProperty("capabilities", out var caps)
                    && caps.ValueKind == System.Text.Json.JsonValueKind.Array)
                {
                    foreach (var capability in caps.EnumerateArray())
                    {
                        if (capability.ValueKind == System.Text.Json.JsonValueKind.String
                            && capability.GetString() is { } value)
                        {
                            advertised.Add(value);
                        }
                    }
                }
                // r5: the delegate receives the HOST command name; every sync
                // write kind maps to its own capability, plus the read floor.
                var required = new List<string>
                {
                    "source.read/1",
                    "source.sync.plan/1", "source.sync.apply/1",
                    "source.sync.operation/1",
                };
                required.Add(name switch
                {
                    "source_scan_sync" => "source.sync.scan/1",
                    "source_relink" => "source.sync.relink/1",
                    "source_repoint" => "source.sync.repoint/1",
                    "source_resync" => "source.sync.resync/1",
                    _ => "source.sync.apply/1",
                });
                foreach (var capability in required)
                {
                    if (!advertised.Contains(capability))
                    {
                        throw new CoreOperationException(
                            "CORE_CAPABILITY_MISSING", "protocol", false,
                            "the Core does not advertise " + capability, null);
                    }
                }
            }


            // FEA-12-CORE / M2-C1 §5.13/§5.14 (R-002 option (b)): the delete/trash capability probe.
            // It runs BEFORE dispatch -- the dispatcher invokes the injected gate outside its error
            // projection try-block -- so a missing capability is thrown HERE (Host layer) and keeps
            // the frozen protocol/false taxonomy instead of being degraded to category=unknown by
            // ProjectDeleteTrashError. The probe is core.ping only: a command is never used as a
            // capability probe (UNKNOWN_COMMAND probing is forbidden).
            async Task DeleteTrashCapabilityAsync(string name, CancellationToken token)
            {
                await CoreService.RequireCapabilitiesAsync(
                        HostCommandRegistry.RequiredCapabilities(name), token)
                    .ConfigureAwait(false);
            }


            async Task<object[]> RunCapabilityProbeAsync()
            {
                var advertised = new HashSet<string>(StringComparer.Ordinal);
                try
                {
                    var ping = await CoreService.SendAsync(
                            "core.ping", 3,
                            writer => writer.WriteStartObject(),
                            _options.RequestTimeout, CancellationToken.None)
                        .ConfigureAwait(false);
                    if (ping.Result?.ValueKind == System.Text.Json.JsonValueKind.Object
                        && ping.Result.Value.TryGetProperty("capabilities", out var caps)
                        && caps.ValueKind == System.Text.Json.JsonValueKind.Array)
                    {
                        foreach (var capability in caps.EnumerateArray())
                        {
                            if (capability.ValueKind == System.Text.Json.JsonValueKind.String
                                && capability.GetString() is { } value)
                            {
                                advertised.Add(value);
                            }
                        }
                    }
                }
                catch (CoreOperationException)
                {
                    // Core unavailable: every sync capability reports unavailable.
                }
                var tokens = new (string Name, string Probe)[]
                {
                    ("scan", "source.sync.scan/1"),
                    ("plan", "source.sync.plan/1"),
                    ("apply", "source.sync.apply/1"),
                    ("relink", "source.sync.relink/1"),
                    ("repoint", "source.sync.repoint/1"),
                    ("resync", "source.sync.resync/1"),
                    ("operation", "source.sync.operation/1"),
                };
                return tokens.Select(token => (object)new Dictionary<string, object?>
                {
                    ["name"] = token.Name,
                    ["available"] = advertised.Contains(token.Probe)
                        && advertised.Contains("source.read/1"),
                    ["reason"] = advertised.Contains(token.Probe)
                        ? null
                        : "capability_missing",
                }).ToArray();
            }

            // FEA-11 (C-17 §3.2/§3.3): ACK/recovery/failure are Host-coordinated
            // through the durable journal; the Core call stays inside the
            // coordinator so a failed call never regresses the journal state.
            async Task<System.Text.Json.JsonElement> SourceOperationCompletionAsync(
                string name, System.Text.Json.JsonElement payload,
                CancellationToken token)
            {
                var operations = Operations ?? throw new CoreOperationException(
                    "CORE_UNAVAILABLE", "unavailable", false, "source operation journal unavailable", null);
                var operationId = payload.ValueKind == System.Text.Json.JsonValueKind.Object
                    && payload.TryGetProperty("operation_id", out var id)
                    && id.ValueKind == System.Text.Json.JsonValueKind.String
                        ? id.GetString()
                        : null;
                if (string.IsNullOrWhiteSpace(operationId))
                {
                    throw new CoreOperationException(
                        "INVALID_REQUEST", "validation", false, "operation id is required", null);
                }
                switch (name)
                {
                    case "source_acknowledge_operation":
                    {
                        var entry = await operations.AcknowledgeAsync(operationId!, token)
                            .ConfigureAwait(false);
                        return System.Text.Json.JsonSerializer.SerializeToElement(entry);
                    }
                    case "source_complete_operation_recovery":
                    {
                        var entry = await operations.RecoverAsync(operationId!, token)
                            .ConfigureAwait(false);
                        return System.Text.Json.JsonSerializer.SerializeToElement(entry);
                    }
                    default:
                    {
                        // r3 P1-03: validate first, forward the exact frozen
                        // fields, and only then record the Host-side failure.
                        var journaled = operations.Get(operationId!);
                        if (journaled is null)
                        {
                            throw new CoreOperationException(
                                "SOURCE_OPERATION_NOT_FOUND", "conflict", false,
                                "unknown operation", null);
                        }
                        var code = payload.ValueKind == System.Text.Json.JsonValueKind.Object
                            && payload.TryGetProperty("code", out var codeValue)
                            && codeValue.ValueKind == System.Text.Json.JsonValueKind.String
                                ? codeValue.GetString()
                                : null;
                        if (string.IsNullOrWhiteSpace(code)
                            || !HostErrorCodes.IsKnown(code))
                        {
                            throw new CoreOperationException(
                                "INVALID_REQUEST", "validation", false,
                                "failure code is required and must be a C-17 §8 code", null);
                        }
                        try
                        {
                            await CoreService.SendHostControlAsync(
                                    "RecordSourceOperationFailure",
                                    writer =>
                                    {
                                        writer.WriteStartObject();
                                        writer.WriteString("operation_id", journaled.OperationId);
                                        writer.WriteString("request_digest", journaled.RequestDigest);
                                        writer.WriteString("code", code);
                                        writer.WriteEndObject();
                                    },
                                    _options.RequestTimeout, CoreService.HostSession, token)
                                .ConfigureAwait(false);
                        }
                        catch (CoreOperationException error)
                            when (error.Code == "SOURCE_OPERATION_NOT_FOUND"
                                  || error.Code == "SOURCE_SYNC_STATE_CONFLICT")
                        {
                            // The Core row may already be terminal/gone; the
                            // Host journal still records the failure.
                        }
                        var failedEntry = operations.MarkFailed(
                            operationId!, code, retryable: HostErrorCodes.RetryableOf(code));
                        return System.Text.Json.JsonSerializer.SerializeToElement(failedEntry);
                    }
                }
            }

            // GRANT-ISSUER-1: open the HOST-ISSUER-1 host-control session and wire the dispatcher.
            // A session failure is logged and leaves grant commands typed-unavailable; it does not
            // fail the whole Host (reads and credential commands keep working).
            try
            {
                var session = await CoreService.OpenHostSessionAsync(cancellationToken).ConfigureAwait(false);
                _log.Info($"host-control session opened ({session.HostSessionId})");
                Grants = new HostGrantCoordinator(
                    CoreService, _options.DataRoot, _options.LogDirectory, _options.RequestTimeout);
                try
                {
                    Registry = new SourceAccessRegistry(_options.DataRoot);
                Sources = new SourceReadCoordinator(CoreService, Registry,
                        () => _options.ReferencedImportEnabled);
                    Operations = new SourceOperationCoordinator(
                        CoreService, _options.DataRoot, () => _options.ReferencedImportEnabled);
                }
                catch (Exception error) when (error is SourceAccessException or IOException or UnauthorizedAccessException)
                { _log.Warn("source registry unavailable"); }
                // FEA-11-RUN-GRANT-1 (R1-01): the best-effort Run pre-authorization
                // orchestration over the source-read stack above. Null when the
                // stack is off/absent -> the hook is a no-op (old behaviour).
                _runAuthorizer = CreateRunSourceAuthorizer();
                Commands = new HostCommandDispatcher(
                    CoreService, HostBridge, HostLocalAsync, SourceOperationJournalAsync,
                    SourceOperationCompletionAsync,
                    // FEA-12-CORE / M2-C1 §5.13/§5.14: the single capability gate covers both
                    // families -- the FEA-12 delete/trash probe and the unchanged FEA-11 source-sync
                    // gate. Both run BEFORE dispatch; a probe verdict is never routed through the
                    // delete/run error projections (R-002 option (b)).
                    async (name, token) =>
                    {
                        if (HostCommandRegistry.RequiredCapabilities(name).Count > 0)
                        {
                            await DeleteTrashCapabilityAsync(name, token).ConfigureAwait(false);
                            return;
                        }

                        await SourceSyncCapabilityAsync(name, token).ConfigureAwait(false);
                    },
                    // FEA-11-RUN-GRANT-1 (C-16 v1.3 §2.4): the Run pre-dispatch
                    // source-read authorization hook (mint -> bind -> dispatch).
                    RunAuthorizeAsync);
            }
            catch (Exception ex) when (ex is CoreOperationException or SidecarException or OperationCanceledException)
            {
                _log.Warn($"host-control session unavailable: {ex.Message}");
                // No host session: the dispatcher still probes delete/trash capabilities through its
                // own CoreServiceClient probe (never dispatches a capability-gated command unprobed).
                Commands = new HostCommandDispatcher(CoreService, HostBridge, HostLocalAsync);
            }

            // V11R-A-6: contract self check after the Core handshake. A mismatch closes the write
            // gate (read-only host, typed error) instead of failing the first user write; partial
            // coverage is a visible Degraded status, never a silent pass.
            SelfCheck = await StartupSelfCheck.RunAsync(_options, CoreService, cancellationToken).ConfigureAwait(false);
            _log.Info($"self-check status={SelfCheck.Status} code={SelfCheck.ErrorCode ?? "-"} detail={SelfCheck.Detail}");
            if (SelfCheck.WritesBlocked)
            {
                _policy = DataRootPolicy.For(_options.DataRoot, HostMode.ReadOnlySelfCheckFailed);
                _log.Warn($"self-check blocked writes: {SelfCheck.ErrorCode} {SelfCheck.Reason}");
                Result = new HostStartResult(
                    HostStatus.Ready,
                    _policy.Mode,
                    SelfCheck.ErrorCode,
                    SelfCheck.Reason,
                    null);
            }
            else
            {
                Result = HostStartResult.Ready(decision.Mode);
            }

            // FEA-11-SCAN-1/2 (I-7 / B1): start the read-only periodic scan only after the Host is
            // ready (host-control session + Sources resolved + Result.IsReady). From FEA-11-SCAN-2 on,
            // a background read-only enumeration of the Core's authoritative scan targets runs after
            // Ready (never blocking the start path); the first periodic tick still happens after one
            // interval, over the merged/verified target set.
            StartSourceScanScheduler();
        }
        catch (SidecarException ex)
        {
            Fail(ex);
        }
        catch (BridgeException ex)
        {
            _log.Error(ex.Code, ex.Message);
            Result = new HostStartResult(HostStatus.Failed, _policy?.Mode ?? HostMode.ReadOnlyUntilParity, ex.Code, ex.UserMessage, null);
            await StopSidecarsAsync().ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or OperationCanceledException)
        {
            _log.Error("HOST_START_IO", ex.Message);
            Result = new HostStartResult(
                HostStatus.Failed,
                _policy?.Mode ?? HostMode.ReadOnlyUntilParity,
                "HOST_START_IO",
                "Host 启动时发生 I/O 错误，详见 host.log。",
                null);
            await StopSidecarsAsync().ConfigureAwait(false);
        }
    }

    private void Fail(SidecarException error)
    {
        _log.Error(error);
        Result = HostStartResult.Failed(new SidecarErrorLike(error.Code.ToString(), error.UserMessage, error.StderrLogPath));
    }

    private async Task StopSidecarsAsync()
    {
        // FEA-11-WATCH-1 (AC-W1): disarmed first so it cannot produce hints after the scheduler stops;
        // then stop and join the scan loop BEFORE the Core/host-control session goes away (SCAN-1 I-7:
        // the scheduler never reopens a session itself).
        StopSourceWatcher();
        await StopSourceScanSchedulerAsync().ConfigureAwait(false);
        if (HostBridge is not null)
        {
            await HostBridge.DisposeAsync().ConfigureAwait(false);
            HostBridge = null;
        }

        if (CoreService is not null)
        {
            await CoreService.DisposeAsync().ConfigureAwait(false);
            CoreService = null;
        }
    }

    /// <summary>
    /// FEA-11-SCAN-1 (I-1/I-7 / AC-S1): resolves the interval from the option + environment override
    /// (illegal values fall back to 900s with a WARN — never a startup failure), builds the
    /// production executor and starts the single loop.
    /// </summary>
    private void StartSourceScanScheduler()
    {
        if (ScanScheduler is not null || Result.Status != HostStatus.Ready
            || !_options.ReferencedImportEnabled || !_options.SourceScanEnabled
            || Sources is not { } sources || CoreService is not { } core)
        {
            return;
        }

        var environment = Environment.GetEnvironmentVariable(SourceScanScheduler.IntervalEnvironmentVariable);
        var interval = SourceScanScheduler.ResolveIntervalSeconds(
            _options.SourceScanIntervalSeconds, environment, out var usedFallback);
        if (usedFallback)
        {
            _log.Warn(
                $"source scan: invalid {SourceScanScheduler.IntervalEnvironmentVariable}; falling back to "
                + SourceScanScheduler.DefaultIntervalSeconds + "s");
        }

        var scanOptions = new SourceScanOptions
        {
            Enabled = true,
            IntervalSeconds = interval,
            MaxTargetsPerTick = _options.SourceScanMaxTargetsPerTick,
            MaxBytesPerSource = _options.SourceScanMaxBytesPerSource,
            MaxEntriesPerSource = _options.SourceScanMaxEntriesPerSource,
        };
        var executor = new HostSourceScanExecutor(
            core, sources, scanOptions, _options.SourceScanTimeProvider, _sourceIdentities);
        _scanExecutor = executor;
        // FEA-11-SCAN-2 (B1): the cold-start enumerator reads the Core's authoritative scan targets
        // and re-verifies the Host's persistent registry; null keeps the SCAN-1 snapshot-only mode
        // (no enumeration command is ever sent).
        ISourceScanTargetEnumerator? enumerator = _options.SourceScanColdStartEnumeration
            && sources.Registry is { } registry
                ? new HostSourceScanTargetEnumerator(core, registry)
                : null;
        ScanScheduler = new SourceScanScheduler(
            scanOptions,
            executor,
            _options.SourceScanTimeProvider,
            infoLog: _log.Info,
            warnLog: _log.Warn,
            errorLog: _log.Error,
            enumerator: enumerator);
        ScanScheduler.Start();
        _log.Info(
            "source scan scheduler started interval=" + interval
            + "s max_targets=" + scanOptions.MaxTargetsPerTick
            + " max_bytes=" + scanOptions.MaxBytesPerSource
            + " cold_start_enumeration=" + (enumerator is not null));
        // FEA-11-WATCH-1 (AC-W1): arm the watcher AFTER the scheduler exists and BEFORE the cold-start
        // enumeration so the merge callback re-arms new targets; arming is read-only and never blocks.
        if (_options.SourceWatchEnabled && sources.Registry is { } watchRegistry)
        {
            var watchOptions = new SourceWatchOptions
            {
                Enabled = true,
                MaxWatches = _options.SourceWatchMaxWatches,
                InternalBufferBytes = _options.SourceWatchInternalBufferBytes,
                DebounceMilliseconds = _options.SourceWatchDebounceMilliseconds,
            };
            Watcher = new SourceWatcher(
                ScanScheduler,
                watchRegistry,
                watchOptions,
                _options.SourceScanTimeProvider,
                infoLog: _log.Info,
                warnLog: _log.Warn);
            Watcher.Start();
            _log.Info("source watcher armed enabled=true max_watches=" + watchOptions.MaxWatches
                + " debounce_ms=" + watchOptions.DebounceMilliseconds);
        }
        else
        {
            _log.Info("source watcher disabled");
        }

        if (enumerator is not null)
        {
            // AC-S2-1: enumerate in the background after Ready — never block startup and never retry
            // in a storm; a missing capability is a typed snapshot state until an explicit refresh.
            _ = RefreshSourceScanTargetsAsync(ScanScheduler);
        }
    }

    /// <summary>FEA-11-WATCH-1: idempotent, synchronous disarm before the scheduler/Core go away.</summary>
    private void StopSourceWatcher()
    {
        var watcher = Watcher;
        Watcher = null;
        if (watcher is null)
        {
            return;
        }

        try
        {
            watcher.Dispose();
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            _log.Warn("source watcher stop failed: " + error.GetType().Name);
        }
    }

    /// <summary>FEA-11-SCAN-1: stops and joins the scan loop; idempotent and safe before/after stop.</summary>
    private async Task StopSourceScanSchedulerAsync()
    {
        var scheduler = ScanScheduler;
        ScanScheduler = null;
        // FEA-11-RUN-GRANT-2A: no on-demand scan may run once the scheduler is gone.
        _scanExecutor = null;
        if (scheduler is null)
        {
            return;
        }

        try
        {
            await scheduler.DisposeAsync().ConfigureAwait(false);
        }
        catch (Exception error) when (error is ObjectDisposedException or InvalidOperationException)
        {
            _log.Warn("source scan scheduler stop failed: " + error.GetType().Name);
        }
    }

    /// <summary>The guarded option value used when no scheduler exists (env override not yet applied).</summary>
    private int ResolvedSourceScanIntervalSeconds()
    {
        var configured = _options.SourceScanIntervalSeconds;
        return configured is >= SourceScanScheduler.MinimumIntervalSeconds
            and <= SourceScanScheduler.MaximumIntervalSeconds
            ? configured
            : SourceScanScheduler.DefaultIntervalSeconds;
    }

    private static SidecarException NotReady() =>
        new(SidecarErrorCode.SidecarExeMissing, "host", "host is not ready; sidecars were not started");

    // ------------------------------------------------------------------
    // FEA-11-RUN-GRANT-1 (C-16 v1.3 §2.4): Run pre-dispatch source-read
    // authorization. R1-01/R1-04 (Review r1): Host-side pre-authorization
    // failures (capability probe, mint I/O, unusable registry, unresolvable
    // known sources) are BEST-EFFORT SKIPS — they must never block a Run the
    // Core could accept. Only a Core typed refusal of the Run target pages
    // propagates (R-5) and prevents the dispatch. The orchestration lives in
    // the standalone ``RunSourceAuthorizer`` so it is unit-testable without
    // sidecars; this class only wires the production dependencies.
    // ------------------------------------------------------------------

    /// <summary>The dispatcher hook for the Run commands that trigger step
    /// execution (R-4). Never throws for Host-side failures (R1-01).</summary>
    private Task RunAuthorizeAsync(
        string name, System.Text.Json.JsonElement payload, CancellationToken token) =>
        _runAuthorizer is { } authorizer
            ? authorizer.AuthorizeForCommandAsync(name, payload, token)
            : Task.CompletedTask;

    /// <summary>R1-02③/R1-07: the Core read used to resolve a Run's frozen
    /// ``{command, scope}`` for control/resume/retry. Its failure is handled by
    /// the caller as a best-effort skip (R1-01).</summary>
    private async Task<(string Command, System.Text.Json.JsonElement Scope)> ResolveRunSliceAsync(
        string runId, CancellationToken token)
    {
        var core = CoreService ?? throw new CoreOperationException(
            "CORE_UNAVAILABLE", "unavailable", false, "Core unavailable", null);
        var response = await core.SendAsync(
                "GetRunSnapshot", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("run_id", runId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, token)
            .ConfigureAwait(false);
        var snapshot = response.Result
                       ?? throw new CoreOperationException(
                           "RUN_SNAPSHOT_INCOMPLETE", "unavailable", true,
                           "Run snapshot is incomplete", null);
        var command = RunCommandPolicy.ReadString(snapshot, "command");
        var scope = snapshot.ValueKind == System.Text.Json.JsonValueKind.Object
                    && snapshot.TryGetProperty("scope", out var rawScope)
            ? rawScope.Clone()
            : default;
        if (command is null
            || scope.ValueKind != System.Text.Json.JsonValueKind.Object)
        {
            throw new CoreOperationException(
                "RUN_SNAPSHOT_INCOMPLETE", "unavailable", true,
                "Run snapshot is incomplete", null);
        }
        return (command, scope);
    }

    /// <summary>Wire the production Run pre-authorization orchestrator. Null
    /// when the source-read stack is off/absent (old behaviour, R-6).</summary>
    private RunSourceAuthorizer? CreateRunSourceAuthorizer()
    {
        var coordinator = Sources;
        var registry = Registry;
        if (coordinator is null || registry is null || !_options.ReferencedImportEnabled)
        {
            return null;
        }
        return new RunSourceAuthorizer(
            enabled: true,
            knownTargets: () => ScanScheduler?.TargetSnapshot() ?? Array.Empty<SourceScanTarget>(),
            registryEntries: registry.List,
            capabilityProbe: coordinator.SupportsRunAuthorizationAsync,
            authorize: coordinator.AuthorizeRunAsync,
            resolveRunSlice: ResolveRunSliceAsync,
            info: message => _log.Info(message),
            warn: message => _log.Warn(message),
            // FEA-11-RUN-GRANT-2A (S-2/S-3): the Run minting version comes from this cache (never the
            // constant "1"); a cold source gets ONE bounded on-demand scan and is skipped on failure.
            identities: _sourceIdentities,
            onDemandScan: ScanSourceOnDemandAsync);
    }

    /// <summary>
    /// FEA-11-RUN-GRANT-2A (card S-3): the single bounded on-demand <c>ScanSourceSync</c> primitive used
    /// only when the identity cache has no live entry for a source. It performs exactly one scan attempt
    /// (cancellation/timeout and the per-slice budget live in <see cref="RunSourceAuthorizer"/>), records
    /// the identity through the production executor path and never throws: failure is a best-effort skip
    /// that must not block a managed-only Run. Null executor (scan slice off) is a silent skip.
    /// </summary>
    private async Task ScanSourceOnDemandAsync(SourceScanTarget target, CancellationToken token)
    {
        var executor = _scanExecutor;
        if (executor is null)
        {
            return;
        }

        try
        {
            await executor.ScanAsync(target, token).ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
            throw; // the authorizer classifies its own timeout vs. the caller's cancellation
        }
        catch (Exception error) when (error is not OutOfMemoryException)
        {
            // Counts/typed code only (never a path): L-G8/§7 redaction.
            _log.Warn("run source-read on-demand scan failed code=" + error.GetType().Name);
        }
    }
}


/// <summary>FEA-11-RUN-GRANT-1 (R1-02③ / R1-11): bounded prepared-Run
/// ``{command, scope}`` ledger. The Core client owns the preparedRun object;
/// AcceptRun only has the id, so the Host must have captured the two frozen
/// fields in the same process (a missing/expired slice is typed
/// ``RUN_STALE_PREVIEW``). Standalone so the behaviour is unit-testable.</summary>
public sealed class PreparedRunSlices
{
    /// <summary>Host-side bound; the ledger never grows with the Run count.</summary>
    public const int MaxEntries = 32;

    private readonly Dictionary<string, System.Text.Json.JsonElement> _slices = new();
    private readonly Dictionary<string, DateTimeOffset> _expiry = new();
    private readonly object _lock = new();
    private readonly Func<DateTimeOffset> _clock;

    public PreparedRunSlices(Func<DateTimeOffset>? clock = null) =>
        _clock = clock ?? (() => DateTimeOffset.UtcNow);

    public int Count
    {
        get { lock (_lock) return _slices.Count; }
    }

    /// <summary>Record the frozen ``{command, scope}`` pair of one prepared Run.
    /// Returns false (no record) when the request does not carry them.</summary>
    public bool Remember(
        string preparedRunId,
        System.Text.Json.JsonElement request,
        DateTimeOffset expiresAt)
    {
        if (string.IsNullOrWhiteSpace(preparedRunId)
            || request.ValueKind != System.Text.Json.JsonValueKind.Object
            || !request.TryGetProperty("command", out var command)
            || command.ValueKind != System.Text.Json.JsonValueKind.String
            || !request.TryGetProperty("scope", out var scope)
            || scope.ValueKind != System.Text.Json.JsonValueKind.Object)
        {
            return false;
        }
        lock (_lock)
        {
            var now = _clock();
            foreach (var expired in _expiry
                         .Where(pair => pair.Value <= now)
                         .Select(pair => pair.Key)
                         .ToArray())
            {
                _slices.Remove(expired);
                _expiry.Remove(expired);
            }
            if (_slices.Count >= MaxEntries)
            {
                var oldest = _expiry
                    .OrderBy(pair => pair.Value)
                    .Select(pair => pair.Key)
                    .FirstOrDefault();
                if (oldest is not null)
                {
                    _slices.Remove(oldest);
                    _expiry.Remove(oldest);
                }
            }
            _slices[preparedRunId] = System.Text.Json.JsonSerializer.SerializeToElement(
                new { command = command.GetString(), scope = scope.Clone() });
            _expiry[preparedRunId] = expiresAt;
            return true;
        }
    }

    /// <summary>Look up a live slice without throwing.</summary>
    public bool TryTake(
        string preparedRunId,
        out string command,
        out System.Text.Json.JsonElement scope)
    {
        command = string.Empty;
        scope = default;
        System.Text.Json.JsonElement slice;
        lock (_lock)
        {
            if (!_slices.TryGetValue(preparedRunId, out slice))
            {
                return false;
            }
            if (_expiry.TryGetValue(preparedRunId, out var expiresAt)
                && expiresAt <= _clock())
            {
                _slices.Remove(preparedRunId);
                _expiry.Remove(preparedRunId);
                return false;
            }
        }
        var name = slice.TryGetProperty("command", out var commandValue)
                   && commandValue.ValueKind == System.Text.Json.JsonValueKind.String
            ? commandValue.GetString()
            : null;
        if (name is null || !slice.TryGetProperty("scope", out var scopeValue))
        {
            return false;
        }
        command = name;
        scope = scopeValue.Clone();
        return true;
    }

    /// <summary>The frozen AcceptRun lookup: a missing/expired slice is typed
    /// ``RUN_STALE_PREVIEW`` (preserves the pre-rework behaviour, R1-11).</summary>
    public (string Command, System.Text.Json.JsonElement Scope) Take(string preparedRunId)
    {
        if (TryTake(preparedRunId, out var command, out var scope))
        {
            return (command, scope);
        }
        throw new CoreOperationException(
            "RUN_STALE_PREVIEW", "conflict", false, "Run preview is stale", null);
    }
}

/// <summary>FEA-11-RUN-GRANT-1 (R-4/R1-02①/R1-02③): pure Run command policy.
/// Only the Run commands that trigger step execution are pre-authorized;
/// read-only commands and non-executing control actions (pause/stop/abandon)
/// never touch the source-read face.</summary>
public static class RunCommandPolicy
{
    public static bool TriggersStepExecution(
        string commandName, System.Text.Json.JsonElement payload) => commandName switch
    {
        "library_start_run" => true,
        "library_control_run" => ReadString(payload, "action") is "continue" or "restart",
        "library_resume_blocked_run" or "library_retry_failed_targets" => true,
        _ => false,
    };

    internal static string? ReadString(
        System.Text.Json.JsonElement element, string name) =>
        element.ValueKind == System.Text.Json.JsonValueKind.Object
        && element.TryGetProperty(name, out var value)
        && value.ValueKind == System.Text.Json.JsonValueKind.String
            ? value.GetString()
            : null;
}

/// <summary>FEA-11-RUN-GRANT-2A (S-2/S-4): the pure Host-known source-range resolution plus the cold
/// sources that still need their Core-authoritative identity (version) before they can be minted.
/// <see cref="Unresolved"/> counts sources that cannot be resolved at all (registry/path/safety);
/// <see cref="ColdSources"/> counts sources whose identity cache entry is missing or expired — they are
/// SKIPPED, never minted with a placeholder version.</summary>
public sealed record RunSourceRangeResolution(
    IReadOnlyList<RunSourceScope> Targets,
    int Unresolved,
    IReadOnlyList<SourceScanTarget> ColdSources);

/// <summary>FEA-11-RUN-GRANT-1 (R-7/R1-02④/R1-04) + FEA-11-RUN-GRANT-2A (S-2/S-5): pure Host-known
/// source-range resolution. Prefer the Run's project when the scope names a book, else every known
/// source. Sources that cannot be resolved (registry entry missing, unsafe path) are counted and
/// SKIPPED — the Core stays the fail-closed authority for the target pages (no silent allow, no Host
/// side block). From 2A on the minting version is the Core-authoritative
/// <c>ScanSourceSync</c> version held by <see cref="SourceIdentityCache"/>; a source without a live
/// identity is returned as COLD and is never minted with the old constant "1" (L-G15).</summary>
public static class RunSourceRange
{
    public static RunSourceRangeResolution Resolve(
        IReadOnlyList<SourceScanTarget> known,
        System.Text.Json.JsonElement scope,
        IReadOnlyList<SourceAuthorization> registryEntries,
        SourceIdentityCache identities)
    {
        ArgumentNullException.ThrowIfNull(identities);
        if (known.Count == 0)
        {
            return new RunSourceRangeResolution(
                Array.Empty<RunSourceScope>(), 0, Array.Empty<SourceScanTarget>());
        }
        IReadOnlyList<SourceScanTarget> filtered = known;
        var kind = RunCommandPolicy.ReadString(scope, "kind");
        var project = RunCommandPolicy.ReadString(scope, "book_id");
        if (kind == "book" && project is not null)
        {
            filtered = known
                .Where(target => target.ProjectIds.Contains(project, StringComparer.Ordinal))
                .ToArray();
        }
        if (filtered.Count == 0)
        {
            return new RunSourceRangeResolution(
                Array.Empty<RunSourceScope>(), 0, Array.Empty<SourceScanTarget>());
        }
        var scopes = new List<RunSourceScope>(filtered.Count);
        var cold = new List<SourceScanTarget>();
        var unresolved = 0;
        foreach (var target in filtered)
        {
            if (scopes.Count + cold.Count >= SourceReadCoordinator.MaxRunGrants)
            {
                unresolved++;
                continue;
            }
            string normalized;
            try
            {
                normalized = SourceSecurity.Normalize(target.Path);
            }
            catch (SourceAccessException)
            {
                unresolved++;
                continue;
            }
            var entry = HostSourceScanExecutor.ResolveRegistryEntry(registryEntries, target.Path);
            if (entry is null)
            {
                unresolved++;
                continue;
            }
            // S-2/S-5: the version MUST come from the Core-authoritative scan response. The scan target
            // only carries the pre-2A placeholder (production default "1"); it is never used here.
            if (!identities.TryGet(target.SourceId, out var identity)
                || string.IsNullOrWhiteSpace(identity.VersionId))
            {
                cold.Add(target);
                continue;
            }
            var sourceKind = KindOfSource(target, normalized);
            scopes.Add(new RunSourceScope(
                entry.RegistryId, entry.Generation, normalized, sourceKind,
                target.SourceId, identity.VersionId,
                // FEA-11-RUN-GRANT-2 (2B, C-16 v1.4 §2): a container source also carries the
                // Core-authoritative member identities (locator/ordinal) from that same scan response;
                // the Host passes them VERBATIM (never inferred, never renumbered). ``image`` keeps the
                // single-entry shape and ``folder`` its per-member enumeration, so both keep null here.
                sourceKind is "zip" or "cbz" or "pdf" && identity.Entries.Count > 0
                    ? identity.Entries
                    : null));
        }
        return new RunSourceRangeResolution(scopes, unresolved, cold);
    }

    public static string KindOf(string path) => Path.GetExtension(path).ToLowerInvariant() switch
    {
        ".zip" => "zip",
        ".cbz" => "cbz",
        ".pdf" => "pdf",
        _ => "image",
    };

    /// <summary>
    /// Review r2 R2-01: the kind of ONE Host scan target. The cold-start
    /// enumeration carries the Core-recorded ``SourceKind`` (authoritative);
    /// when it is absent the filesystem decides — a DIRECTORY is a ``folder``
    /// source. The old extension-only guess classified every folder as
    /// ``image``, so the mint opened the directory as a file and the whole
    /// source was skipped (folder Run pre-authorization was never usable).
    /// </summary>
    public static string KindOfSource(SourceScanTarget target, string normalizedPath)
    {
        var declared = target.SourceKind;
        if (declared is "image" or "folder" or "zip" or "cbz" or "pdf")
        {
            return declared;
        }
        return Directory.Exists(normalizedPath) ? "folder" : KindOf(normalizedPath);
    }
}

/// <summary>FEA-11-RUN-GRANT-1 (R1-01/R1-04): the Run pre-dispatch authorization
/// orchestration. Best-effort by contract:
///
/// * capability missing / probe error / no known source / registry unusable /
///   every mint failed -&gt; skip and let the dispatch proceed unchanged;
/// * a Core typed refusal of the request (``CoreOperationException``) -&gt;
///   propagate so the Run command is NOT dispatched and the typed code is
///   returned unchanged (R-5). No new Run-face code is invented.
/// </summary>
public sealed class RunSourceAuthorizer
{
    /// <summary>
    /// FEA-11-RUN-GRANT-2A (card S-3, AC-G3): explicit budget — one Run slice performs at most this
    /// many on-demand <c>ScanSourceSync</c> fills for COLD sources. The remaining cold sources are
    /// skipped (best-effort) and the Core stays the fail-closed authority for their pages.
    /// </summary>
    public const int MaxOnDemandScansPerSlice = 8;

    /// <summary>FEA-11-RUN-GRANT-2A (card S-3): explicit per-source on-demand scan timeout.</summary>
    public static readonly TimeSpan OnDemandScanTimeout = TimeSpan.FromSeconds(30);

    private readonly bool _enabled;
    private readonly Func<IReadOnlyList<SourceScanTarget>> _knownTargets;
    private readonly Func<IReadOnlyList<SourceAuthorization>> _registryEntries;
    private readonly Func<CancellationToken, Task<bool>> _capabilityProbe;
    private readonly Func<
        IReadOnlyList<RunSourceScope>, string, System.Text.Json.JsonElement,
        CancellationToken, Task<RunAuthorizationResult>> _authorize;
    private readonly Func<
        string, CancellationToken,
        Task<(string Command, System.Text.Json.JsonElement Scope)>> _resolveRunSlice;
    private readonly Action<string> _info;
    private readonly Action<string> _warn;
    private readonly SourceIdentityCache _identities;
    private readonly Func<SourceScanTarget, CancellationToken, Task>? _onDemandScan;
    // S-3: serializes the bounded cold-cache fills so concurrent Run commands cannot scan the same
    // source twice (the second slice finds the cache warm) and the on-demand budget stays explicit.
    private readonly SemaphoreSlim _onDemandGate = new(1, 1);

    public RunSourceAuthorizer(
        bool enabled,
        Func<IReadOnlyList<SourceScanTarget>> knownTargets,
        Func<IReadOnlyList<SourceAuthorization>> registryEntries,
        Func<CancellationToken, Task<bool>> capabilityProbe,
        Func<
            IReadOnlyList<RunSourceScope>, string, System.Text.Json.JsonElement,
            CancellationToken, Task<RunAuthorizationResult>> authorize,
        Func<
            string, CancellationToken,
            Task<(string Command, System.Text.Json.JsonElement Scope)>> resolveRunSlice,
        Action<string> info,
        Action<string> warn,
        SourceIdentityCache identities,
        Func<SourceScanTarget, CancellationToken, Task>? onDemandScan = null)
    {
        _enabled = enabled;
        _knownTargets = knownTargets;
        _registryEntries = registryEntries;
        _capabilityProbe = capabilityProbe;
        _authorize = authorize;
        _resolveRunSlice = resolveRunSlice;
        _info = info;
        _warn = warn;
        _identities = identities ?? throw new ArgumentNullException(nameof(identities));
        _onDemandScan = onDemandScan;
    }

    public bool Enabled => _enabled;

    /// <summary>The dispatcher hook (R-4). Best-effort: it never throws for
    /// Host-side failures; only a Core typed page refusal propagates (R-5).</summary>
    public async Task AuthorizeForCommandAsync(
        string commandName,
        System.Text.Json.JsonElement payload,
        CancellationToken token)
    {
        if (!_enabled || !RunCommandPolicy.TriggersStepExecution(commandName, payload))
        {
            return; // read-only command or a non-executing control action
        }
        if (!await ProbeAsync(token).ConfigureAwait(false))
        {
            return; // R-6: no source.read.run/1 (or probe failed) -> old behaviour
        }
        if (commandName == "library_start_run")
        {
            var command = RunCommandPolicy.ReadString(payload, "command");
            var scope = ExtractScope(payload);
            if (command is null
                || scope.ValueKind != System.Text.Json.JsonValueKind.Object)
            {
                // The Core dispatch will produce the authoritative
                // INVALID_REQUEST; the pre-authorization stays out of the way.
                _warn("run source-read authorization skipped code=INVALID_REQUEST");
                return;
            }
            await AuthorizeSliceAsync(command, scope, token).ConfigureAwait(false);
            return;
        }
        var runId = RunCommandPolicy.ReadString(payload, "run_id");
        if (string.IsNullOrWhiteSpace(runId))
        {
            _warn("run source-read authorization skipped code=INVALID_REQUEST");
            return;
        }
        (string Command, System.Text.Json.JsonElement Scope) slice;
        try
        {
            slice = await _resolveRunSlice(runId!, token).ConfigureAwait(false);
        }
        catch (Exception error) when (error is not OperationCanceledException)
        {
            // R1-01: a snapshot lookup failure is not a target-page refusal; the
            // Run dispatch keeps its own typed error.
            _warn("run source-read authorization skipped run_id code=" + CodeOf(error));
            return;
        }
        await AuthorizeSliceAsync(slice.Command, slice.Scope, token).ConfigureAwait(false);
    }

    /// <summary>R1-02③: the AcceptRun seam (the frozen prepared slice already
    /// supplied command/scope; authorization is the same best-effort slice).</summary>
    public Task AuthorizePreparedRunAsync(
        string command,
        System.Text.Json.JsonElement scope,
        CancellationToken token) =>
        _enabled
            ? AuthorizeSliceAsync(command, scope, token)
            : Task.CompletedTask;

    /// <summary>Best-effort mint+bind for one Run slice.</summary>
    public async Task AuthorizeSliceAsync(
        string command,
        System.Text.Json.JsonElement scope,
        CancellationToken token)
    {
        if (!_enabled || !await ProbeAsync(token).ConfigureAwait(false))
        {
            return;
        }
        IReadOnlyList<SourceScanTarget> known;
        IReadOnlyList<SourceAuthorization> entries;
        try
        {
            known = _knownTargets();
            entries = _registryEntries();
        }
        catch (Exception error) when (error is not OperationCanceledException)
        {
            _warn("run source-read authorization skipped registry code=" + CodeOf(error));
            return;
        }
        var resolution = await ResolveWithColdCacheAsync(known, entries, scope, token)
            .ConfigureAwait(false);
        if (resolution.Resolution.Unresolved > 0)
        {
            // Counts only (never a path / source id): L-G12 boundary evidence.
            _warn($"run source-read authorization unresolved_sources={resolution.Resolution.Unresolved}");
        }
        if (resolution.ColdSources > 0)
        {
            // AC-G3: a cold source without a Core-proven version is SKIPPED, never minted with a
            // placeholder; the Run continues (best-effort) and the Core owns the fail-closed verdict.
            _warn($"run source-read authorization cold_sources={resolution.ColdSources}"
                  + $" on_demand_attempts={resolution.OnDemandAttempts}");
        }
        var targets = resolution.Resolution.Targets;
        if (targets.Count == 0)
        {
            return; // no Host-known source can hold this Run's referenced pages
        }
        try
        {
            var result = await _authorize(targets, command, scope, token)
                .ConfigureAwait(false);
            if (result.Skipped)
            {
                _warn("run source-read authorization skipped all_sources"
                      + " mint=" + result.SkippedSources);
                return;
            }
            // L-G8: the mint cost is a source-size bound; only counts are logged.
            _info($"run source-read authorization sources={targets.Count}"
                  + $" minted={result.MintedGrants} bound_pages={result.BoundPages}"
                  + $" skipped={result.SkippedSources}");
        }
        catch (CoreOperationException)
        {
            // R-5: the Core refused the target pages (typed) -> block the
            // dispatch and return that exact code unchanged.
            throw;
        }
        catch (Exception error) when (error is not OperationCanceledException)
        {
            // R1-01: any other pre-authorization failure is a best-effort skip.
            _warn("run source-read authorization skipped code=" + CodeOf(error));
        }
    }

    /// <summary>FEA-11-RUN-GRANT-2A (S-3): resolve the range, fill cold sources with at most ONE
    /// bounded on-demand scan each (explicit budget + timeout), then resolve again. Failures, timeouts
    /// and exhausted budgets are skips: the method never throws for Host-side reasons.</summary>
    private async Task<ColdCacheResolution> ResolveWithColdCacheAsync(
        IReadOnlyList<SourceScanTarget> known,
        IReadOnlyList<SourceAuthorization> entries,
        System.Text.Json.JsonElement scope,
        CancellationToken token)
    {
        var resolution = RunSourceRange.Resolve(known, scope, entries, _identities);
        if (resolution.ColdSources.Count == 0 || _onDemandScan is null)
        {
            return new ColdCacheResolution(resolution, resolution.ColdSources.Count, 0);
        }
        var budget = Math.Min(resolution.ColdSources.Count, MaxOnDemandScansPerSlice);
        if (resolution.ColdSources.Count > budget)
        {
            _warn($"run source-read authorization on_demand_budget_exhausted={resolution.ColdSources.Count - budget}");
        }
        var attempts = 0;
        await _onDemandGate.WaitAsync(token).ConfigureAwait(false);
        try
        {
            foreach (var cold in resolution.ColdSources.Take(budget))
            {
                if (_identities.TryGet(cold.SourceId, out _))
                {
                    continue; // already filled (a concurrent slice or the periodic tick won)
                }
                attempts++;
                using var timeout = CancellationTokenSource.CreateLinkedTokenSource(token);
                timeout.CancelAfter(OnDemandScanTimeout);
                try
                {
                    await _onDemandScan(cold, timeout.Token).ConfigureAwait(false);
                }
                catch (OperationCanceledException) when (!token.IsCancellationRequested)
                {
                    _warn("run source-read authorization on_demand_scan timed out");
                }
                catch (Exception error) when (error is not OperationCanceledException)
                {
                    _warn("run source-read authorization on_demand_scan skipped code=" + CodeOf(error));
                }
            }
        }
        finally
        {
            _onDemandGate.Release();
        }
        var refreshed = RunSourceRange.Resolve(known, scope, entries, _identities);
        return new ColdCacheResolution(refreshed, refreshed.ColdSources.Count, attempts);
    }

    private sealed record ColdCacheResolution(
        RunSourceRangeResolution Resolution, int ColdSources, int OnDemandAttempts);

    public static System.Text.Json.JsonElement ExtractScope(
        System.Text.Json.JsonElement payload) =>
        payload.ValueKind == System.Text.Json.JsonValueKind.Object
        && payload.TryGetProperty("scope", out var scope)
            ? scope.Clone()
            : default;

    private async Task<bool> ProbeAsync(CancellationToken token)
    {
        try
        {
            return await _capabilityProbe(token).ConfigureAwait(false);
        }
        catch (Exception error) when (error is not OperationCanceledException)
        {
            _warn("run source-read authorization skipped probe code=" + CodeOf(error));
            return false;
        }
    }

    private static string CodeOf(Exception error) => error switch
    {
        CoreOperationException core => core.Code,
        SourceAccessException source => source.Code,
        _ => error.GetType().Name,
    };
}

public sealed record ChineseRoundTripResult(string Expected, string Received, bool ExactMatch);

