using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using NewManga.CoreClient.Diagnostics;
using NewManga.Host.Credentials;
using NewManga.CoreClient.Transport;
using NewManga.Host.Resources;

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
        _policy = DataRootPolicy.For(options.DataRoot, HostMode.ReadOnlyUntilParity);
    }

    public HostStartResult Result { get; private set; } =
        new(HostStatus.Failed, HostMode.ReadOnlyUntilParity, "HOST_NOT_STARTED", "host not started", null);

    public CoreServiceClient? CoreService { get; private set; }

    public HostBridgeClient? HostBridge { get; private set; }

    /// <summary>GRANT-ISSUER-1: host-control grant chain + whitelisted shell actions (null until ready).</summary>
    public HostGrantCoordinator? Grants { get; private set; }

    /// <summary>CREDENTIAL-PORT-1: OS-vault credential port + Core bind/clear bridge (null when unavailable).</summary>
    public HostCredentialCoordinator? Credentials { get; private set; }

    /// <summary>GRANT-ISSUER-1: the production command dispatcher, including the Host-local commands.</summary>
    public HostCommandDispatcher? Commands { get; private set; }

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
        await runtime.StartInternalAsync(cancellationToken).ConfigureAwait(false);
        return runtime;
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
    /// Creates a book through the Core — refused while the host is read-only (S1 default). Tests and
    /// the isolated demo pass an isolated data root and <c>ParityReached=true</c>.
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
    public async Task<byte[]> ReadPageImageAsync(string pageId, CancellationToken cancellationToken = default)
    {
        await _readerIoGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var core = CoreService ?? throw NotReady();
            var bridge = HostBridge ?? throw NotReady();
            var resolved = await core.ResolvePageResourceAsync(pageId, cancellationToken).ConfigureAwait(false);
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

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
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
            _log.Info($"mode={decision.Mode} reason={decision.Reason} data_root={_options.DataRoot}");

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

            // GRANT-ISSUER-1: open the HOST-ISSUER-1 host-control session and wire the dispatcher.
            // A session failure is logged and leaves grant commands typed-unavailable; it does not
            // fail the whole Host (reads and credential commands keep working).
            try
            {
                var session = await CoreService.OpenHostSessionAsync(cancellationToken).ConfigureAwait(false);
                _log.Info($"host-control session opened ({session.HostSessionId})");
                Grants = new HostGrantCoordinator(
                    CoreService, _options.DataRoot, _options.LogDirectory, _options.RequestTimeout);
                Commands = new HostCommandDispatcher(CoreService, HostBridge, HostLocalAsync);
            }
            catch (Exception ex) when (ex is CoreOperationException or SidecarException or OperationCanceledException)
            {
                _log.Warn($"host-control session unavailable: {ex.Message}");
                Commands = new HostCommandDispatcher(CoreService, HostBridge, HostLocalAsync);
            }

            Result = HostStartResult.Ready(decision.Mode);
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

    private static SidecarException NotReady() =>
        new(SidecarErrorCode.SidecarExeMissing, "host", "host is not ready; sidecars were not started");
}

public sealed record ChineseRoundTripResult(string Expected, string Received, bool ExactMatch);
