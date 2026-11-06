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

    // The host_bridge/core_service pipes are request/response only: page reads are serialized.
    private readonly SemaphoreSlim _readerIoGate = new(1, 1);

    private HostRuntime(HostOptions options, HostLog log)
    {
        _options = options;
        _log = log;
        // V11R-A-5: conservative pre-start gate (closed until StartInternalAsync decides). The real
        // policy is derived from CoexistenceRules (legacy shell / explicit --parity=false).
        _policy = DataRootPolicy.For(options.DataRoot, HostMode.ReadOnlyUntilParity);
    }

    /// <summary>V11R-A-6: last startup contract self check result (NotRun until the host starts).</summary>
    public StartupSelfCheckResult SelfCheck { get; private set; } = StartupSelfCheckResult.NotRun;

    public HostStartResult Result { get; private set; } =
        new(HostStatus.Failed, HostMode.ReadOnlyUntilParity, "HOST_NOT_STARTED", "host not started", null);

    public CoreServiceClient? CoreService { get; private set; }

    public Task<PreparedRunPreview> PrepareRunAsync(System.Text.Json.JsonElement request,
        CancellationToken ct = default) => (CoreService ?? throw new InvalidOperationException("Core unavailable"))
        .PrepareRunAsync(request, ct);

    public Task<System.Text.Json.JsonElement> AcceptRunAsync(string preparedRunId, int generation,
        string idempotencyKey, CancellationToken ct = default)
    {
        if (!Policy.WritesAllowed) throw new InvalidOperationException("Host is read-only");
        return (CoreService ?? throw new InvalidOperationException("Core unavailable"))
            .AcceptRunAsync(preparedRunId, generation, idempotencyKey, ct);
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
                    });
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

            // FEA-11-SCAN-1 (I-7): start the read-only periodic scan only after the Host is ready
            // (host-control session + Sources resolved + Result.IsReady). Cold start enumerates no
            // sources (L-A): the first tick happens after one interval and only over App-registered
            // targets.
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
        // FEA-11-SCAN-1 (I-7): stop and join the scan loop BEFORE the Core/host-control session goes
        // away; the scheduler never reopens a session itself.
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
        var executor = new HostSourceScanExecutor(core, sources, scanOptions, _options.SourceScanTimeProvider);
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
        if (enumerator is not null)
        {
            // AC-S2-1: enumerate in the background after Ready — never block startup and never retry
            // in a storm; a missing capability is a typed snapshot state until an explicit refresh.
            _ = RefreshSourceScanTargetsAsync(ScanScheduler);
        }
    }

    /// <summary>FEA-11-SCAN-1: stops and joins the scan loop; idempotent and safe before/after stop.</summary>
    private async Task StopSourceScanSchedulerAsync()
    {
        var scheduler = ScanScheduler;
        ScanScheduler = null;
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
}

public sealed record ChineseRoundTripResult(string Expected, string Received, bool ExactMatch);

