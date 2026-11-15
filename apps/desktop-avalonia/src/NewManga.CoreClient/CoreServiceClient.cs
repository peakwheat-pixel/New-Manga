using System.Security.Cryptography;
using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Issuer;
using NewManga.CoreClient.Transport;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient;

public sealed record CorePing(
    bool Ready,
    int ProtocolMajor,
    int ProtocolMinor,
    string? Status,
    IReadOnlyList<string> Capabilities);

public sealed record BookSummary(
    string BookId,
    string Title,
    string OriginalTitle,
    bool IsFavorite,
    bool IsArchived,
    int? PageCount,
    string CreatedAt,
    string UpdatedAt);

/// <summary>One chapter row from the Core <c>list_chapters</c> read face.</summary>
/// <summary>
/// M2-PAGE-NAV-PROJECTION-1 chapter navigation row. M2-C1 rev 2.16 (MAINT-2-C1-BATCH-1
/// AC4/AC5) widened the frozen four-key <c>list_chapters</c> result with two OPTIONAL
/// read-only fields: <paramref name="Kind"/> (<c>paged</c>/<c>webtoon</c>) and
/// <paramref name="CustomRank"/> (null when unset). Both are optional so every existing
/// construction site keeps working; the four original fields are unchanged.
/// <see cref="CustomRank"/> is <see cref="long"/> because the Core column is a 64-bit
/// integer (see MAX_SQLITE_INTEGER in the library service) and an int would truncate.
/// </summary>
public sealed record ChapterSummary(
    string ChapterId,
    string Title,
    string ChapterNumber,
    int SortOrder,
    string? Kind = null,
    long? CustomRank = null)
{
    /// <summary>
    /// M2-C1 rev 2.16: parse one <c>list_chapters</c> row. The four frozen keys are required
    /// (a missing/mistyped one throws <see cref="FormatException"/> -- the row is malformed),
    /// while <c>kind</c>/<c>custom_rank</c> are OPTIONAL: an absent field, an explicit null and
    /// an older four-key Core all read as null. Kept as a static entry point (same convention as
    /// <c>RegionTextDetail.Parse</c>) so the widening is testable without a live sidecar.
    /// </summary>
    public static ChapterSummary Parse(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            throw new FormatException("chapter row must be an object");
        }

        var sortOrder = element.TryGetProperty("sort_order", out var sort)
            && sort.ValueKind == JsonValueKind.Number
            && sort.TryGetInt32(out var order)
            ? order
            : throw new FormatException("missing integer field 'sort_order'");

        var customRank = element.TryGetProperty("custom_rank", out var rank)
            && rank.ValueKind == JsonValueKind.Number
            && rank.TryGetInt64(out var value)
            ? (long?)value
            : null;

        return new ChapterSummary(
            RequiredString(element, "chapter_id"),
            RequiredString(element, "title"),
            RequiredString(element, "chapter_number"),
            sortOrder,
            element.TryGetProperty("kind", out var kind) && kind.ValueKind == JsonValueKind.String
                ? kind.GetString()
                : null,
            customRank);
    }

    private static string RequiredString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString() ?? string.Empty
            : throw new FormatException($"missing string field '{property}'");
}

/// <summary>FEA-14-EDIT-1 (PREQ EDIT P16): relative page point of a marker (0..1).</summary>
public sealed record IssueMarkerPosition(double X, double Y);

/// <summary>
/// FEA-14-EDIT-1 (PREQ EDIT P16): one editing issue marker. <see cref="Position"/>
/// is null for whole-page markers; <see cref="Note"/>/<see cref="ResolvedAt"/>
/// are null until set.
/// </summary>
public sealed record IssueMarkerInfo(
    string MarkerId,
    string ChapterId,
    string PageId,
    string Kind,
    string? Note,
    string State,
    string CreatedAt,
    IssueMarkerPosition? Position = null,
    string? ResolvedAt = null);

/// <summary>FEA-14-AI-1 (PREQ AI P21): one prompt template row (builtin or user).</summary>
public sealed record PromptTemplateInfo(string TemplateId, string Name, int Version, bool Builtin);

/// <summary>FEA-14-AI-1 (PREQ AI P23): outcome of a template delete.</summary>
public sealed record PromptTemplateDeleteResult(bool Deleted);

/// <summary>FEA-14-AI-1 (PREQ AI P25): one durable pointer at a template.</summary>
public sealed record PromptTemplateReference(string Kind, string OwnerId, string Label);

/// <summary>
/// REALUSE-DATA-SAFETY-1 AC2: one <c>.nmbak</c> package row from <c>backup.list</c> /
/// <c>backup.create</c>. <see cref="Verified"/> is the Core's read-back verdict, never optimism.
/// </summary>
public sealed record BackupPackageInfo(
    string BackupId,
    string BackupType,
    string CreatedAt,
    long SizeBytes,
    int SchemaVersion,
    bool Verified,
    // FEA-13-ID-3 (C-01b SC-18): the library identity the package belongs to.
    // Null means "unknown" (a legacy package created before the primitive);
    // it must never be read as a mismatch.
    string? DatabaseId = null);

/// <summary>
/// REALUSE-DATA-SAFETY-4 AC1: one removable cache target from <c>cleanup.preview</c>. Only a
/// relative path and a byte size — the Core never sends an OS path here.
/// </summary>
public sealed record CleanupTargetInfo(string RelativePath, long SizeBytes);

/// <summary>
/// REALUSE-DATA-SAFETY-4 AC1: <c>cleanup.preview</c> projection
/// (<c>CleanupPreview.to_dict()</c> + <c>pending_cleanups</c>). Reading never deletes anything.
/// </summary>
public sealed record CleanupPreviewInfo(
    IReadOnlyList<CleanupTargetInfo> Targets,
    long TotalBytes,
    int PendingCleanups);

/// <summary>
/// REALUSE-DATA-SAFETY-4 AC1: <c>cleanup.run</c> projection. Counts are the Core's own; failures
/// keep their fixed path-free reason so a partial cleanup is never reported as success.
/// </summary>
public sealed record CleanupOutcomeInfo(
    int Removed,
    int Failed,
    int Skipped,
    IReadOnlyList<string> FailedPaths);

/// <summary>
/// REALUSE-DATA-SAFETY-4 AC1: one row of <c>plugins.list</c>. A rejected plugin keeps its
/// <paramref name="Reason"/>; the UI must not present it as merely "off".
/// </summary>
public sealed record PluginInfo(
    string PluginId,
    string Status,
    bool Enabled,
    string Name,
    string Version,
    string Description,
    IReadOnlyList<string> Hooks,
    IReadOnlyList<string> Permissions,
    string? Reason);

/// <summary>
/// REALUSE-DATA-SAFETY-4 AC1: <c>plugins.list</c> projection. The plugin root is deliberately not
/// part of it (the Core never projects an absolute OS path over IPC).
/// </summary>
public sealed record PluginListInfo(bool GlobalEnabled, IReadOnlyList<PluginInfo> Plugins);

/// <summary>One page row from <c>GetReaderProjection</c> (src/infrastructure/sqlite/library.py list_pages).</summary>
public sealed record ReaderPageSummary(
    string PageId,
    int Order,
    int WidthPx,
    int HeightPx,
    string? OriginalResourceId,
    string? OriginalRevisionId,
    string? Sha256);

/// <summary>Reader projection result: layout + ordered pages for one chapter.</summary>
public sealed record ReaderProjection(
    string BookId,
    string ChapterId,
    string Mode,
    string Layout,
    IReadOnlyList<ReaderPageSummary> Pages)
{
    /// <summary>
    /// READER-PROGRESS-1: <c>initial_position.page_id</c>. With <c>start_position="resume"</c> the
    /// Core echoes the persisted page for (book, chapter, mode); it falls back to the first page when
    /// nothing was saved or the saved page left the chapter (page list shrank/reordered).
    /// </summary>
    public string? InitialPageId { get; init; }

    /// <summary>READER-PROGRESS-1: <c>initial_position.scroll_offset_y</c> (webtoon logical page pixels).</summary>
    public double InitialScrollOffsetY { get; init; }

    /// <summary>READER-PROGRESS-1: progress row echoed by the projection (null = never read).</summary>
    public ReadingProgressSnapshot? SavedProgress { get; init; }
}

/// <summary>READER-PROGRESS-1: committed reading-progress row (contract M2-C1 §6.3).</summary>
public sealed record ReadingProgressSnapshot(
    string BookId,
    string ChapterId,
    string Mode,
    string? LastPageId,
    double ScrollOffsetY,
    double ProgressPercent,
    string? LastReadAt,
    double TotalReadSeconds);

/// <summary>
/// One navigation row from the Core <c>list_chapter_pages</c> read face
/// (M2-PAGE-NAV-PROJECTION-1, contract M2-C1 rev 1.8 §5): page id, source filename and the
/// user sort order only — the page image itself is fetched through the resource channel.
/// </summary>
public sealed record ChapterPageSummary(string PageId, string SourceFilename, int SortOrder);

/// <summary>
/// Normalized (0..1) region geometry from <c>list_regions</c> (M2-WORKBENCH-REACT-1 additive
/// widening, contract rev 1.5): <c>bbox</c> is the display rectangle and <c>polygon</c> keeps the
/// stored ring shape (empty for rectangles created from two corners).
/// </summary>
public sealed record RegionGeometrySummary(
    double X,
    double Y,
    double Width,
    double Height,
    IReadOnlyList<RegionGeometryPoint> Polygon)
{
    /// <summary>Page-pixel rectangle for one Core page extent (normalized × page_size).</summary>
    public RegionPixelRect ToPagePixels(RegionPageSize pageSize) => new(
        X * pageSize.Width,
        Y * pageSize.Height,
        Width * pageSize.Width,
        Height * pageSize.Height);
}

/// <summary>One normalized polygon vertex (0..1 on each axis).</summary>
public sealed record RegionGeometryPoint(double X, double Y);

/// <summary>Page-pixel rectangle projected from normalized region geometry.</summary>
public sealed record RegionPixelRect(double X, double Y, double Width, double Height);

/// <summary>Pixel extent of one Core page row (<c>list_regions.page_size</c>).</summary>
public sealed record RegionPageSize(int Width, int Height);

/// <summary>
/// One region row of the <c>list_regions</c> read face (contract rev 1.4 §5.4, geometry added
/// additively by rev 1.5). <see cref="Geometry"/> is null when the Core has no page extent for the
/// page (unknown/hidden page: rows stay addressable, overlay math is unavailable).
/// </summary>
public sealed record RegionSummary(
    string RegionId,
    string RegionType,
    string SfxPolicy,
    string Origin,
    int RevisionNo,
    RegionGeometrySummary? Geometry);

/// <summary>Result of <c>list_regions</c>: live region summaries + the page pixel extent.</summary>
public sealed record RegionPageProjection(
    IReadOnlyList<RegionSummary> Regions,
    RegionPageSize? PageSize);

/// <summary>One row of the <c>list_region_revisions</c> frozen revision history face (RC-4).</summary>
public sealed record RegionRevisionSummary(
    string RegionRevisionId,
    int RevisionNo,
    string Origin,
    string ReviewState,
    bool IsPinned,
    string? RestoredFromRevisionId,
    string? CreatedAt,
    string RegionType,
    string SfxPolicy,
    bool IsCurrent);

/// <summary>Result of <c>list_region_revisions</c> for one region.</summary>
public sealed record RegionRevisionHistory(
    string RegionId,
    int CurrentRevisionNo,
    IReadOnlyList<RegionRevisionSummary> Revisions);

/// <summary>Post-write effective state echoed by <c>set_region_type</c> / <c>restore_region_revision</c>.</summary>
public sealed record RegionWriteSnapshot(
    string RegionId,
    int RevisionNo,
    string RegionType,
    string SfxPolicy);

/// <summary>One region row of a <c>rerender_page</c> report.</summary>
public sealed record RerenderRegionReport(
    string RegionId,
    string Status,
    string? SkipReason,
    bool FontSubstituted);

/// <summary>Result of <c>rerender_page</c>: published translated artifact revision + preview state.</summary>
public sealed record PageRerenderResult(
    string PageId,
    string ArtifactId,
    int RevisionNo,
    IReadOnlyList<RerenderRegionReport> Reports,
    string? PreviewResourceId,
    string? PreviewError);

/// <summary>Catalog key returned by <c>resolve_page_resource</c> (idempotent per page).</summary>
public sealed record ResolvedPageResource(string ResourceId, string Revision);

public sealed class CoreServiceOptions
{
    public required string ExecutablePath { get; init; }

    /// <summary>NEWMANGA_DATA_ROOT for the Core (isolated for tests/S1 read-only runs).</summary>
    public required string DataRoot { get; init; }

    /// <summary>M2RC1_DERIVED_ROOT for the Core preview namespace.</summary>
    public required string DerivedRoot { get; init; }

    /// <summary>M2RC2_CATALOG_DB for the Core catalog.</summary>
    public required string CatalogDbPath { get; init; }

    public string? ManagedRoot { get; init; }

    public bool ReferencedImportEnabled { get; init; } = true;

    public required string StderrLogPath { get; init; }

    public string? WireLogPath { get; init; }

    /// <summary>Optional extra argv for test doubles / diagnostics (production passes none).</summary>
    public IReadOnlyList<string> AdditionalArguments { get; init; } = Array.Empty<string>();

    public TimeSpan StartupTimeout { get; init; } = TimeSpan.FromSeconds(30);

    public TimeSpan RequestTimeout { get; init; } = TimeSpan.FromSeconds(30);
}

/// <summary>
/// protocol-2.3 application channel to <c>core_service.exe</c>: <c>core.ping</c>, <c>ListBooks</c>,
/// <c>CreateBook</c> plus raw-line access for the cp936 negative test. Every request is ASCII-escaped
/// on the wire; every frame is captured in <see cref="Wire"/>.
/// </summary>
public sealed class CoreServiceClient : IAsyncDisposable
{
    private readonly object _preparedGate = new();
    private readonly Dictionary<string, JsonElement> _preparedRuns = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _preparedAttempts = new(StringComparer.Ordinal);

    /// <summary>Host-only temporary candidates. UI receives only the safe preview record.</summary>
    public async Task<PreparedRunPreview> PrepareRunAsync(JsonElement request, CancellationToken ct = default)
    {
        var response = await SendAsync("PrepareRun", 12, writer => request.WriteTo(writer),
            _options.RequestTimeout, ct).ConfigureAwait(false);
        var candidate = response.Result!.Value.Clone();
        var id = candidate.GetProperty("preparedRunId").GetString()!;
        lock (_preparedGate)
        {
            foreach (var expired in _preparedRuns.Where(pair =>
                pair.Value.GetProperty("expiresAt").GetDateTimeOffset() <= DateTimeOffset.UtcNow &&
                !_preparedAttempts.ContainsValue(pair.Key)).Select(pair => pair.Key).ToArray())
                _preparedRuns.Remove(expired);
            _preparedRuns[id] = candidate;
        }
        return new(id, candidate.GetProperty("snapshotDigest").GetString()!,
            candidate.GetProperty("generation").GetInt32(), candidate.GetProperty("expiresAt").GetDateTimeOffset(),
            candidate.GetProperty("displaySummary").Clone(), candidate.GetProperty("redactedPayloadPreview").Clone());
    }

    public async Task<JsonElement> AcceptRunAsync(string preparedRunId, int generation, string idempotencyKey,
        CancellationToken ct = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(idempotencyKey);
        JsonElement candidate;
        lock (_preparedGate)
        {
            if (!_preparedRuns.TryGetValue(preparedRunId, out candidate) ||
                candidate.GetProperty("generation").GetInt32() != generation)
                throw new CoreOperationException("RUN_STALE_PREVIEW", "conflict", false, "Run preview is stale", null);
            // An attempted key may have committed before an ACK was lost. Replay reaches durable Core truth.
            if (!_preparedAttempts.ContainsKey(idempotencyKey) &&
                candidate.GetProperty("expiresAt").GetDateTimeOffset() <= DateTimeOffset.UtcNow)
                throw new CoreOperationException("RUN_PREVIEW_EXPIRED", "conflict", false, "Run preview expired", null);
            _preparedAttempts.TryAdd(idempotencyKey, preparedRunId);
        }
        var response = await SendAsync("AcceptRun", 12, writer =>
        {
            writer.WriteStartObject();
            writer.WritePropertyName("prepared_run");
            candidate.WriteTo(writer);
            writer.WriteString("idempotency_key", idempotencyKey);
            writer.WriteEndObject();
        }, _options.RequestTimeout, ct).ConfigureAwait(false);
        return response.Result!.Value.Clone();
    }
    /// <summary>M2-PAGE-NAV-PROJECTION-1: <c>list_chapter_pages</c> was introduced at protocol minor 6.</summary>
    private const int ChapterPagesMinor = 6;

    private readonly SidecarProcess _process;
    private readonly CoreServiceOptions _options;
    private int _requestCounter;
    private bool _disposed;
    private readonly SemaphoreSlim _sessionGate = new(1, 1);

    /// <summary>
    /// CORE-PIPE-EXCLUSIVE-1 / E-6: core_service speaks a strictly request/response protocol on ONE
    /// stdin/stdout pipe and <see cref="Transport.SidecarProcess"/> holds a single StreamReader over it.
    /// Two concurrent callers therefore both corrupt each other's responses and trip
    /// "The stream is currently in use by a previous operation on the stream".
    ///
    /// Every command -- app channel, host-control channel, gate-inside or gate-outside -- must hold this
    /// gate for the WHOLE request/response cycle, including the event-frame skipping loop, because that
    /// loop reads the same shared stream.
    /// </summary>
    // E-7 #1: exclusivity now comes from the transport (SidecarProcess.AcquireExchangeLeaseAsync),
    // so the client no longer keeps its own second gate.

    /// <summary>GRANT-ISSUER-1: the host-control session opened at startup (null until opened).</summary>
    public HostSessionInfo? HostSession { get; private set; }

    private CoreServiceClient(SidecarProcess process, CoreServiceOptions options)
    {
        _process = process;
        _options = options;
    }

    public WireLog Wire => _process.Log;

    public string StderrTail => _process.StderrTail;

    public string? StderrLogPath => _options.StderrLogPath;

    public static async Task<CoreServiceClient> StartAsync(
        CoreServiceOptions options,
        CancellationToken cancellationToken = default)
    {
        var spec = new SidecarSpec
        {
            Name = SidecarSpec.CoreServiceName,
            ExecutablePath = options.ExecutablePath,
            Environment = BuildEnvironment(options),
            StderrLogPath = options.StderrLogPath,
            WireLogPath = options.WireLogPath,
            AdditionalArguments = options.AdditionalArguments,
            StartupTimeout = options.StartupTimeout,
            RequestTimeout = options.RequestTimeout,
        };

        var process = await SidecarProcess.StartAsync(spec, cancellationToken).ConfigureAwait(false);
        var client = new CoreServiceClient(process, options);
        try
        {
            var ping = await client.PingAsync(options.StartupTimeout, cancellationToken).ConfigureAwait(false);
            if (!ping.Ready || ping.ProtocolMajor != CoreProtocol.Major)
            {
                throw new SidecarException(
                    SidecarErrorCode.ProtocolMismatch,
                    SidecarSpec.CoreServiceName,
                    $"unexpected core.ping result: status={ping.Status}, protocol={ping.ProtocolMajor}.{ping.ProtocolMinor}",
                    options.StderrLogPath);
            }
        }
        catch (SidecarException ex)
        {
            await client.DisposeAsync().ConfigureAwait(false);
            if (ex.Code == SidecarErrorCode.RequestTimeout)
            {
                throw new SidecarException(
                    SidecarErrorCode.StartupTimeout,
                    SidecarSpec.CoreServiceName,
                    $"core.ping startup timeout: {ex.Message}",
                    options.StderrLogPath,
                    ex);
            }

            if (ex.Code is SidecarErrorCode.ProcessExited or SidecarErrorCode.MalformedResponse)
            {
                throw new SidecarException(
                    SidecarErrorCode.HandshakeFailed,
                    SidecarSpec.CoreServiceName,
                    $"core.ping handshake failed: {ex.Message}",
                    options.StderrLogPath,
                    ex);
            }

            throw;
        }
        catch
        {
            await client.DisposeAsync().ConfigureAwait(false);
            throw;
        }

        return client;
    }

    private static IReadOnlyDictionary<string, string> BuildEnvironment(CoreServiceOptions options)
    {
        var environment = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["NEWMANGA_DATA_ROOT"] = options.DataRoot,
            ["NEWMANGA_REFERENCED_IMPORT_ENABLED"] = options.ReferencedImportEnabled ? "true" : "false",
            ["M2RC1_DERIVED_ROOT"] = options.DerivedRoot,
            ["M2RC2_CATALOG_DB"] = options.CatalogDbPath,
        };
        if (!string.IsNullOrWhiteSpace(options.ManagedRoot))
        {
            environment["M2RC1_MANAGED_ROOT"] = options.ManagedRoot!;
        }

        return environment;
    }

    public async Task<CorePing> PingAsync(CancellationToken cancellationToken = default) =>
        await PingAsync(_options.RequestTimeout, cancellationToken).ConfigureAwait(false);

    private async Task<CorePing> PingAsync(TimeSpan timeout, CancellationToken cancellationToken)
    {
        var response = await SendAsync("core.ping", CoreProtocol.DefaultMinor, WireJson.EmptyObject, timeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "core.ping");
        var status = ReadString(result, "status");
        var ready = string.Equals(status, "ready", StringComparison.Ordinal);
        var major = 0;
        var minor = 0;
        if (result.TryGetProperty("protocol_version", out var version))
        {
            major = ReadInt(version, "major");
            minor = ReadInt(version, "minor");
        }

        var capabilities = new List<string>();
        if (result.TryGetProperty("capabilities", out var caps) && caps.ValueKind == JsonValueKind.Array)
        {
            foreach (var cap in caps.EnumerateArray())
            {
                if (cap.ValueKind == JsonValueKind.String && cap.GetString() is { } value)
                {
                    capabilities.Add(value);
                }
            }
        }

        return new CorePing(ready, major, minor, status, capabilities);
    }

    /// <summary>
    /// FEA-12-CORE / M2-C1 §5.13/§5.14: fail-closed capability probe. A Host that is about to
    /// dispatch a capability-gated command calls this BEFORE the command frame is built; a Core
    /// that does not advertise every required capability -- or a probe that cannot produce the
    /// capability list at all -- yields the frozen contract verdict <c>CORE_CAPABILITY_MISSING</c>
    /// (<c>protocol</c> / <c>retryable=false</c>). Sending the command itself and inspecting
    /// <c>UNKNOWN_COMMAND</c> is NOT a legal probe channel (M2-C1 §5.13/§5.14).
    /// </summary>
    public async Task RequireCapabilitiesAsync(
        IReadOnlyCollection<string> required,
        CancellationToken cancellationToken = default)
    {
        CorePing ping;
        try
        {
            ping = await PingAsync(cancellationToken).ConfigureAwait(false);
        }
        catch (Exception error) when (error is CoreOperationException or SidecarException)
        {
            // A probe that cannot report capabilities is treated exactly like a missing
            // capability: fail closed, never "assume supported".
            throw new CoreOperationException(
                "CORE_CAPABILITY_MISSING", "protocol", false, "capability probe failed", null);
        }

        if (required.Count == 0)
        {
            return;
        }

        var advertised = new HashSet<string>(ping.Capabilities, StringComparer.Ordinal);
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

    /// <summary>
    /// GRANT-ISSUER-1: opens the HOST-ISSUER-1 host-control session. The credential is a
    /// 32-byte random token (base64url), the signing key is a separate 32-byte random key used by
    /// <see cref="HostIssuer"/>; the Core echoes its own session id, which every later host-control
    /// envelope must carry.
    /// </summary>
    public async Task<HostSessionInfo> OpenHostSessionAsync(CancellationToken cancellationToken = default)
    {
        await _sessionGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (HostSession is not null)
            {
                return HostSession;
            }

            var credential = HostIssuer.Base64Url(RandomNumberGenerator.GetBytes(32));
            var hostSessionId = "host_" + HostIssuer.NewToken();
            var response = await SendHostControlAsync(
                    "OpenHostSession",
                    writer =>
                    {
                        writer.WriteString("host_session_id", hostSessionId);
                        writer.WriteString("host_session_credential", credential);
                    },
                    _options.RequestTimeout,
                    session: null,
                    cancellationToken)
                .ConfigureAwait(false);
            var result = RequireResult(response, "OpenHostSession");
            var coreSessionId = ReadString(result, "core_session_id");
            if (string.IsNullOrEmpty(coreSessionId))
            {
                throw new SidecarException(
                    SidecarErrorCode.MalformedResponse,
                    SidecarSpec.CoreServiceName,
                    "OpenHostSession response has no core_session_id",
                    _options.StderrLogPath);
            }

            HostSession = new HostSessionInfo(
                hostSessionId, credential, coreSessionId, HostIssuer.NewSigningKey());
            return HostSession;
        }
        finally
        {
            _sessionGate.Release();
        }
    }

    /// <summary>
    /// Sends one HOST-ISSUER-1 host-control envelope (channel=host-control). Application-channel
    /// commands keep using <see cref="SendAsync"/>; this surface is only for grant/session control,
    /// exactly the set the frozen Core accepts on that channel.
    /// </summary>
    public async Task<CoreResponse> SendHostControlAsync(
        string command,
        Action<Utf8JsonWriter> payload,
        CancellationToken cancellationToken = default) =>
        await SendHostControlAsync(command, payload, _options.RequestTimeout, HostSession, cancellationToken)
            .ConfigureAwait(false);

    public async Task<CoreResponse> SendHostControlAsync(
        string command,
        Action<Utf8JsonWriter> payload,
        TimeSpan timeout,
        HostSessionInfo? session,
        CancellationToken cancellationToken = default)
    {
        var requestId = $"hostctl-{Interlocked.Increment(ref _requestCounter)}";
        var line = WireJson.Write(writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("protocol", CoreProtocol.ProtocolName);
            writer.WritePropertyName("version");
            writer.WriteStartObject();
            writer.WriteNumber("major", CoreProtocol.Major);
            writer.WriteNumber("minor", CoreProtocol.DefaultMinor);
            writer.WriteEndObject();
            writer.WriteString("request_id", requestId);
            writer.WriteString("channel", "host-control");
            writer.WriteString("command", command);
            if (session is not null)
            {
                writer.WriteString("core_session_id", session.CoreSessionId);
                writer.WriteString("host_session_id", session.HostSessionId);
                writer.WriteString("host_session_credential", session.Credential);
            }

            writer.WritePropertyName("payload");
            writer.WriteStartObject();
            payload(writer);
            writer.WriteEndObject();
            writer.WriteEndObject();
        });

        // CORE-PIPE-EXCLUSIVE-1: same exclusive gate as the app channel -- one shared pipe.
        var lease = await _process.AcquireExchangeLeaseAsync(cancellationToken).ConfigureAwait(false);
        try
        {
        var frame = await _process
            .ExchangeAsync(line, escapeNonAscii: true, timeout, cancellationToken)
            .ConfigureAwait(false);
        var response = await ReadResponseForRequestAsync(
                frame.ResponseLine,
                requestId,
                ct => _process.ReadNextResponseLineAsync(timeout, ct),
                _process.Poison,
                ResyncMaxDrainFrames,
                _options.StderrLogPath,
                cancellationToken)
            .ConfigureAwait(false);
        if (response.Error is { } error)
        {
            throw new CoreOperationException(
                error.Code, error.Category, error.Retryable, error.Message, response.RequestId ?? requestId);
        }

        return response;
        }
        finally
        {
            lease.Dispose();
        }
    }

    public async Task<IReadOnlyList<BookSummary>> ListBooksAsync(CancellationToken cancellationToken = default)
    {
        var response = await SendAsync("ListBooks", CoreProtocol.DefaultMinor, WireJson.EmptyObject, _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ListBooks");
        if (result.ValueKind != JsonValueKind.Array)
        {
            throw Malformed("ListBooks result is not an array");
        }

        var books = new List<BookSummary>();
        foreach (var item in result.EnumerateArray())
        {
            books.Add(ParseBook(item));
        }

        return books;
    }

    // ---------------------------------------------------------------------------------------------
    // REALUSE-DATA-SAFETY-1 AC2: the .nmbak package face (backup.list/create/delete/restore).
    // These are ordinary application commands (never HostControl); every failure is the Core's
    // typed code, so the UI can show it instead of inventing success.
    // ---------------------------------------------------------------------------------------------

    public async Task<IReadOnlyList<BackupPackageInfo>> ListBackupsAsync(
        CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "backup.list",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "backup.list");
        if (result.ValueKind != JsonValueKind.Array)
        {
            throw Malformed("backup.list result is not an array");
        }

        var packages = new List<BackupPackageInfo>();
        foreach (var item in result.EnumerateArray())
        {
            packages.Add(ParseBackupPackage(item));
        }

        return packages;
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-4 AC1 (review r1 M5): retry the removals the Core persisted as failed
    /// (<c>cleanup.retry_pending</c>). Settled entries leave the ledger; repeated failures stay pending.
    /// </summary>
    public async Task<CleanupOutcomeInfo> RetryPendingCleanupsAsync(CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "cleanup.retry_pending",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "cleanup.retry_pending");
        if (result.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("cleanup.retry_pending result is not an object");
        }

        return ParseCleanupOutcome(result);
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: plugin inventory (<c>plugins.list</c>). Read-only.</summary>
    public async Task<PluginListInfo> ListPluginsAsync(CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "plugins.list",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "plugins.list");
        if (result.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("plugins.list result is not an object");
        }

        var plugins = new List<PluginInfo>();
        if (result.TryGetProperty("plugins", out var pluginsElement) && pluginsElement.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in pluginsElement.EnumerateArray())
            {
                plugins.Add(new PluginInfo(
                    ReadPluginString(item, "plugin_id"),
                    ReadPluginString(item, "status"),
                    item.TryGetProperty("enabled", out var enabled) && enabled.ValueKind == JsonValueKind.True,
                    ReadPluginString(item, "name"),
                    ReadPluginString(item, "version"),
                    ReadPluginString(item, "description"),
                    ReadPluginStringArray(item, "hooks"),
                    ReadPluginStringArray(item, "permissions"),
                    item.TryGetProperty("reason", out var reason) && reason.ValueKind == JsonValueKind.String
                        ? reason.GetString()
                        : null));
            }
        }

        return new PluginListInfo(
            result.TryGetProperty("global_enabled", out var global) && global.ValueKind == JsonValueKind.True,
            plugins);
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-4 AC1: the global plugin master switch (<c>plugins.set_enabled</c>).
    /// Returns the Core-confirmed new state, or null when the response was not a projection —
    /// <c>false</c> is a valid ANSWER ("now off"), not a failure signal (review r1 M1).
    /// </summary>
    public async Task<bool?> SetPluginsGlobalEnabledAsync(bool enabled, CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "plugins.set_enabled",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteBoolean("enabled", enabled);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "plugins.set_enabled");
        if (result.ValueKind != JsonValueKind.Object
            || !result.TryGetProperty("global_enabled", out var global)
            || (global.ValueKind != JsonValueKind.True && global.ValueKind != JsonValueKind.False))
        {
            return null;
        }

        return global.ValueKind == JsonValueKind.True;
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-4 AC1: one plugin's switch (<c>plugins.set_plugin_enabled</c>). Returns the
    /// confirmed new state, or null when the Core refused (unknown / rejected plugin).
    /// </summary>
    public async Task<bool?> SetPluginEnabledAsync(
        string pluginId,
        bool enabled,
        CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "plugins.set_plugin_enabled",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("plugin_id", pluginId);
                    writer.WriteBoolean("enabled", enabled);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "plugins.set_plugin_enabled");
        if (result.ValueKind != JsonValueKind.Object
            || !result.TryGetProperty("enabled", out var value)
            || (value.ValueKind != JsonValueKind.True && value.ValueKind != JsonValueKind.False))
        {
            return null;
        }

        return value.ValueKind == JsonValueKind.True;
    }

    private static string ReadPluginString(JsonElement element, string name) =>
        element.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString() ?? string.Empty
            : string.Empty;

    private static IReadOnlyList<string> ReadPluginStringArray(JsonElement element, string name)
    {
        if (!element.TryGetProperty(name, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            return Array.Empty<string>();
        }

        var items = new List<string>();
        foreach (var item in value.EnumerateArray())
        {
            if (item.ValueKind == JsonValueKind.String && item.GetString() is { Length: > 0 } text)
            {
                items.Add(text);
            }
        }

        return items;
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-4 AC1: read-only pre-flight over the removable cache population
    /// (<c>cleanup.preview</c>). The preview lists exactly the targets the run face re-checks, so
    /// "preview says N" and "run touches at most N" cannot disagree.
    /// </summary>
    public async Task<CleanupPreviewInfo> GetCleanupPreviewAsync(CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "cleanup.preview",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "cleanup.preview");
        if (result.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("cleanup.preview result is not an object");
        }

        var targets = new List<CleanupTargetInfo>();
        if (result.TryGetProperty("targets", out var targetsElement) && targetsElement.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in targetsElement.EnumerateArray())
            {
                targets.Add(new CleanupTargetInfo(
                    item.TryGetProperty("relative_path", out var path) ? path.GetString() ?? string.Empty : string.Empty,
                    item.TryGetProperty("size_bytes", out var size) && size.TryGetInt64(out var bytes) ? bytes : 0));
            }
        }

        return new CleanupPreviewInfo(
            targets,
            result.TryGetProperty("total_bytes", out var total) && total.TryGetInt64(out var totalBytes) ? totalBytes : 0,
            result.TryGetProperty("pending_cleanups", out var pending) && pending.TryGetInt32(out var pendingCount) ? pendingCount : 0);
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-4 AC1: remove every safe cache target (<c>cleanup.run</c>). Idempotent;
    /// failed removals stay persisted in the Core's pending ledger for the retry face.
    /// </summary>
    public async Task<CleanupOutcomeInfo> RunCleanupAsync(CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "cleanup.run",
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "cleanup.run");
        if (result.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("cleanup.run result is not an object");
        }

        return ParseCleanupOutcome(result);
    }

    private static CleanupOutcomeInfo ParseCleanupOutcome(JsonElement result)
    {
        var failedPaths = new List<string>();
        if (result.TryGetProperty("items", out var items) && items.ValueKind == JsonValueKind.Object)
        {
            foreach (var item in items.EnumerateObject())
            {
                if (item.Value.ValueKind == JsonValueKind.Object
                    && item.Value.TryGetProperty("status", out var status)
                    && string.Equals(status.GetString(), "failed", StringComparison.Ordinal))
                {
                    failedPaths.Add(item.Name);
                }
            }
        }

        return new CleanupOutcomeInfo(
            result.TryGetProperty("removed", out var removed) && removed.TryGetInt32(out var removedCount) ? removedCount : 0,
            result.TryGetProperty("failed", out var failed) && failed.TryGetInt32(out var failedCount) ? failedCount : 0,
            result.TryGetProperty("skipped", out var skipped) && skipped.TryGetInt32(out var skippedCount) ? skippedCount : 0,
            failedPaths);
    }

    public async Task<BackupPackageInfo> CreateBackupAsync(
        string backupType = "manual",
        CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "backup.create",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("backup_type", backupType);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return ParseBackupPackage(RequireResult(response, "backup.create"));
    }

    public async Task DeleteBackupAsync(string backupId, CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "backup.delete",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("backup_id", backupId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        RequireResult(response, "backup.delete");
    }

    /// <summary>
    /// Overwrite restore. The Core writes its own <c>pre_restore</c> rollback package first and refuses
    /// anything but an explicit <c>confirm_restore: true</c>; the returned id names that rollback point.
    /// </summary>
    public async Task<string> RestoreBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "backup.restore",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("backup_id", backupId);
                    writer.WriteBoolean("confirm_restore", true);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "backup.restore");
        return result.ValueKind == JsonValueKind.Object
               && result.TryGetProperty("pre_restore_backup_id", out var rollback)
            ? rollback.GetString() ?? string.Empty
            : string.Empty;
    }

    public async Task<BookSummary> CreateBookAsync(string title, CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "CreateBook",
                CoreProtocol.CreateMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("title", title);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "CreateBook");
        return ParseBook(result);
    }

    /// <summary>Chapter navigation read face (protocol 2.3 <c>list_chapters</c>).</summary>
    public async Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(string bookId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }

        var response = await SendAsync(
                "list_chapters",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "list_chapters");
        var chapters = new List<ChapterSummary>();
        if (result.TryGetProperty("chapters", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object)
                {
                    throw Malformed("list_chapters entry is not an object");
                }

                chapters.Add(ChapterSummary.Parse(item));
            }
        }

        return chapters;
    }

    /// <summary>
    /// M2-PAGE-NAV-PROJECTION-1 page navigation read face (<c>list_chapter_pages</c>, contract
    /// M2-C1 rev 1.8 §5): committed pages of one chapter in the user's current sort order.
    /// The command was introduced at protocol minor 6; the frozen 2.3 sidecar accepts it (evidence:
    /// verification/REGION-WORKBENCH-1/logs/wire-probe.json), so the request carries 6 while the
    /// registry's proven dispatcher binding keeps its own minor.
    /// </summary>
    public async Task<IReadOnlyList<ChapterPageSummary>> ListChapterPagesAsync(
        string chapterId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            throw new ArgumentException("chapter_id is required", nameof(chapterId));
        }

        var response = await SendAsync(
                "list_chapter_pages",
                ChapterPagesMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("chapter_id", chapterId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "list_chapter_pages");
        var pages = new List<ChapterPageSummary>();
        if (result.TryGetProperty("pages", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object)
                {
                    throw Malformed("list_chapter_pages entry is not an object");
                }

                pages.Add(new ChapterPageSummary(
                    ReadString(item, "page_id") ?? string.Empty,
                    ReadString(item, "source_filename") ?? string.Empty,
                    ReadInt(item, "sort_order")));
            }
        }

        return pages;
    }

    /// <summary>
    /// Region read face (<c>list_regions</c>, contract rev 1.4 §5.4 + rev 1.5 additive widening):
    /// live region summaries in reading order plus the page pixel extent the overlay math needs.
    /// </summary>
    public async Task<RegionPageProjection> ListRegionsAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(pageId))
        {
            throw new ArgumentException("page_id is required", nameof(pageId));
        }

        var response = await SendAsync(
                "list_regions",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", pageId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "list_regions");

        RegionPageSize? pageSize = null;
        if (result.TryGetProperty("page_size", out var size) && size.ValueKind == JsonValueKind.Object)
        {
            pageSize = new RegionPageSize(ReadInt(size, "width"), ReadInt(size, "height"));
        }

        var regions = new List<RegionSummary>();
        if (result.TryGetProperty("regions", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object)
                {
                    throw Malformed("list_regions entry is not an object");
                }

                regions.Add(new RegionSummary(
                    ReadString(item, "region_id") ?? string.Empty,
                    ReadString(item, "region_type") ?? string.Empty,
                    ReadString(item, "sfx_policy") ?? string.Empty,
                    ReadString(item, "origin") ?? string.Empty,
                    ReadInt(item, "revision_no"),
                    ParseRegionGeometry(item)));
            }
        }

        return new RegionPageProjection(regions, pageSize);
    }

    /// <summary>
    /// FEA-06-RESIDUAL-4B (C-07 UNFREEZE v1.9 / RO-1 plan row <c>#80</c>): the page-scoped Region
    /// TEXT read projection (<c>list_page_region_texts</c>, Region family minor 3, V11R-F0-2).
    /// ONE page load returns every live region's four-level text / lock / review / pin / geometry
    /// projection, so the workbench compare panel needs no per-region N+1.
    /// The command accepts ONLY <c>page_id</c> plus an optional strict <c>region_ids</c> filter. It
    /// has no <c>expected_revision</c> (that field belongs to the write commands), so a revision
    /// guard cannot be sent by construction -- see <see cref="ListPageRegionTextsCommand"/>.
    /// </summary>
    public async Task<RegionPageTextProjection> ListPageRegionTextsAsync(
        string pageId,
        IReadOnlyList<string>? regionIds = null,
        CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                ListPageRegionTextsCommand,
                ListPageRegionTextsMinor,
                writer => WriteListPageRegionTextsPayload(pageId, regionIds, writer),
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return RegionPageTextProjection.Parse(RequireResult(response, ListPageRegionTextsCommand));
    }

    /// <summary>FEA-06-RESIDUAL-4B (AC6): the frozen wire command of the page-scoped Region text read.</summary>
    internal const string ListPageRegionTextsCommand = "list_page_region_texts";

    /// <summary>
    /// FEA-06-RESIDUAL-4B (AC6): the Region command-family minor. It stays the shared default-3
    /// protocol minor, and the registry descriptor for the same command carries the same value; the
    /// CoreClient tests cross-check both, so a drift fails a test instead of silently changing wire.
    /// </summary>
    internal static int ListPageRegionTextsMinor => CoreProtocol.DefaultMinor;

    /// <summary>
    /// FEA-06-RESIDUAL-4B (AC6): the ONE place that decides this command's payload shape. Internal
    /// (not private) so the CoreClient test project can assert the exact keys without a live
    /// sidecar -- the same testability convention as <c>HostCommandDispatcher.WriteCorePayload</c>.
    /// Validation runs inside the writer, which <see cref="CoreProtocol.BuildRequest"/> invokes
    /// before the frame is sent, so a rejected argument never reaches the wire.
    /// </summary>
    internal static void WriteListPageRegionTextsPayload(
        string pageId,
        IReadOnlyList<string>? regionIds,
        Utf8JsonWriter writer)
    {
        if (string.IsNullOrWhiteSpace(pageId))
        {
            throw new ArgumentException("page_id is required", nameof(pageId));
        }

        var filter = NormalizeRegionIdFilter(regionIds, nameof(regionIds));
        writer.WriteStartObject();
        writer.WriteString("page_id", pageId);
        if (filter is not null)
        {
            writer.WriteStartArray("region_ids");
            foreach (var regionId in filter)
            {
                writer.WriteStringValue(regionId);
            }

            writer.WriteEndArray();
        }

        writer.WriteEndObject();
    }

    /// <summary>
    /// FEA-06-RESIDUAL-4B (AC6): mirrors the dispatcher's boundary rule for the same optional
    /// filter (non-empty, distinct). An empty list means "no filter", so the property is omitted
    /// instead of sending the empty array the Core refuses.
    /// </summary>
    private static IReadOnlyList<string>? NormalizeRegionIdFilter(
        IReadOnlyList<string>? regionIds,
        string parameterName)
    {
        if (regionIds is null || regionIds.Count == 0)
        {
            return null;
        }

        var seen = new HashSet<string>(StringComparer.Ordinal);
        var filter = new List<string>(regionIds.Count);
        foreach (var regionId in regionIds)
        {
            if (string.IsNullOrWhiteSpace(regionId))
            {
                throw new ArgumentException("region_ids entries must be non-empty", parameterName);
            }

            if (!seen.Add(regionId))
            {
                throw new ArgumentException($"region_ids contains a duplicate id: {regionId}", parameterName);
            }

            filter.Add(regionId);
        }

        return filter;
    }

    /// <summary>Region revision history read face (<c>list_region_revisions</c>, RC-4).</summary>
    public async Task<RegionRevisionHistory> ListRegionRevisionsAsync(
        string regionId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(regionId))
        {
            throw new ArgumentException("region_id is required", nameof(regionId));
        }

        var response = await SendAsync(
                "list_region_revisions",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("region_id", regionId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "list_region_revisions");

        var revisions = new List<RegionRevisionSummary>();
        if (result.TryGetProperty("revisions", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object)
                {
                    throw Malformed("list_region_revisions entry is not an object");
                }

                revisions.Add(new RegionRevisionSummary(
                    ReadString(item, "region_revision_id") ?? string.Empty,
                    ReadInt(item, "revision_no"),
                    ReadString(item, "origin") ?? string.Empty,
                    ReadString(item, "review_state") ?? string.Empty,
                    ReadBool(item, "is_pinned"),
                    ReadString(item, "restored_from_revision_id"),
                    ReadString(item, "created_at"),
                    ReadString(item, "region_type") ?? string.Empty,
                    ReadString(item, "sfx_policy") ?? string.Empty,
                    ReadBool(item, "is_current")));
            }
        }

        return new RegionRevisionHistory(
            ReadString(result, "region_id") ?? regionId,
            ReadInt(result, "current_revision_no"),
            revisions);
    }

    /// <summary>
    /// Region retype write face (<c>set_region_type</c>). <paramref name="expectedRevision"/> is the
    /// optimistic guard: it must be the revision the caller read, never a guessed value. The Core
    /// answers INPUT_REVISION_CHANGED when it no longer matches.
    /// </summary>
    public async Task<RegionWriteSnapshot> SetRegionTypeAsync(
        string regionId,
        string newRegionType,
        int? expectedRevision = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(regionId))
        {
            throw new ArgumentException("region_id is required", nameof(regionId));
        }

        if (string.IsNullOrWhiteSpace(newRegionType))
        {
            throw new ArgumentException("new_region_type is required", nameof(newRegionType));
        }

        var response = await SendAsync(
                "set_region_type",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("region_id", regionId);
                    writer.WriteString("new_region_type", newRegionType);
                    if (expectedRevision is { } expected)
                    {
                        writer.WriteNumber("expected_revision", expected);
                    }

                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return ParseRegionWriteSnapshot(RequireResult(response, "set_region_type"), regionId);
    }

    /// <summary>
    /// Restores one region revision into a NEW revision (<c>restore_region_revision</c>). Both
    /// integers are required by the frozen Core: the source revision and the current revision the
    /// optimistic guard must match.
    /// </summary>
    public async Task<RegionWriteSnapshot> RestoreRegionRevisionAsync(
        string regionId,
        int revisionNo,
        int expectedRevision,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(regionId))
        {
            throw new ArgumentException("region_id is required", nameof(regionId));
        }

        if (revisionNo <= 0 || expectedRevision <= 0)
        {
            throw new ArgumentException("revision_no and expected_revision must be positive", nameof(revisionNo));
        }

        var response = await SendAsync(
                "restore_region_revision",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("region_id", regionId);
                    writer.WriteNumber("revision_no", revisionNo);
                    writer.WriteNumber("expected_revision", expectedRevision);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return ParseRegionWriteSnapshot(RequireResult(response, "restore_region_revision"), regionId);
    }

    /// <summary>
    /// Manual page rerender (<c>rerender_page</c>): applies the current global typeset settings and
    /// commits a translated artifact revision; the optional preview publication is projected as
    /// <see cref="PageRerenderResult.PreviewResourceId"/> / <see cref="PageRerenderResult.PreviewError"/>.
    /// </summary>
    public async Task<PageRerenderResult> RerenderPageAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(pageId))
        {
            throw new ArgumentException("page_id is required", nameof(pageId));
        }

        var response = await SendAsync(
                "rerender_page",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", pageId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "rerender_page");
        var reports = new List<RerenderRegionReport>();
        if (result.TryGetProperty("reports", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object)
                {
                    throw Malformed("rerender_page report entry is not an object");
                }

                reports.Add(new RerenderRegionReport(
                    ReadString(item, "region_id") ?? string.Empty,
                    ReadString(item, "status") ?? string.Empty,
                    ReadString(item, "skip_reason"),
                    ReadBool(item, "font_substituted")));
            }
        }

        string? previewResourceId = null;
        if (result.TryGetProperty("preview", out var preview) && preview.ValueKind == JsonValueKind.Object)
        {
            previewResourceId = ReadString(preview, "resource_id");
        }

        return new PageRerenderResult(
            ReadString(result, "page_id") ?? pageId,
            ReadString(result, "artifact_id") ?? string.Empty,
            ReadInt(result, "revision_no"),
            reports,
            previewResourceId,
            ReadString(result, "preview_error"));
    }

    /// <summary>FEA-14-READ-1 (PREQ P9): per-book reading preferences.</summary>
    public async Task<ReadingPreferencesInfo?> GetReadingPreferencesAsync(
        string bookId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }
        var response = await SendAsync(
                "GetReadingPreferences", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteString("book_id", bookId); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "GetReadingPreferences");
        return new ReadingPreferencesInfo(
            ReadString(result, "book_id") ?? bookId,
            ReadString(result, "mode") ?? "original",
            ReadString(result, "direction") ?? "ltr",
            result.TryGetProperty("zoom", out var zoom) && zoom.ValueKind == JsonValueKind.Number ? zoom.GetDouble() : 1.0,
            result.TryGetProperty("double_page", out var doublePage) && doublePage.ValueKind == JsonValueKind.True,
            ReadString(result, "layout") ?? "single",
            ReadString(result, "updated_at") ?? string.Empty,
            result.TryGetProperty("is_default", out var isDefault) && isDefault.ValueKind == JsonValueKind.True);
    }

    /// <summary>FEA-14-READ-1 (PREQ P10): persist one book's reading preferences.</summary>
    public async Task<bool> SaveReadingPreferencesAsync(
        string bookId, ReadingPreferencesPatch patch, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }
        ArgumentNullException.ThrowIfNull(patch);
        var response = await SendAsync(
                "SaveReadingPreferences", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteStartObject("prefs");
                    if (patch.Mode is not null) writer.WriteString("mode", patch.Mode);
                    if (patch.Direction is not null) writer.WriteString("direction", patch.Direction);
                    if (patch.Zoom is not null) writer.WriteNumber("zoom", patch.Zoom.Value);
                    if (patch.DoublePage is not null) writer.WriteBoolean("double_page", patch.DoublePage.Value);
                    if (patch.Layout is not null) writer.WriteString("layout", patch.Layout);
                    writer.WriteEndObject();
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "SaveReadingPreferences");
        return result.TryGetProperty("saved", out var saved) && saved.ValueKind == JsonValueKind.True;
    }

    /// <summary>FEA-14-READ-1 (PREQ P11): list one book's bookmarks.</summary>
    public async Task<IReadOnlyList<BookmarkInfo>> ListBookmarksAsync(
        string bookId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }
        var response = await SendAsync(
                "ListBookmarks", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteString("book_id", bookId); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ListBookmarks");
        var bookmarks = new List<BookmarkInfo>();
        if (result.TryGetProperty("bookmarks", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object) continue;
                bookmarks.Add(new BookmarkInfo(
                    ReadString(item, "bookmark_id") ?? string.Empty,
                    ReadString(item, "book_id") ?? string.Empty,
                    ReadString(item, "chapter_id") ?? string.Empty,
                    ReadString(item, "page_id") ?? string.Empty,
                    ReadString(item, "side"),
                    ReadString(item, "note"),
                    ReadString(item, "created_at") ?? string.Empty));
            }
        }
        return bookmarks;
    }

    /// <summary>FEA-14-READ-1 (PREQ P12): create one bookmark.</summary>
    public async Task<string?> CreateBookmarkAsync(
        string bookId, string chapterId, string pageId, string? side = null, string? note = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(chapterId) || string.IsNullOrWhiteSpace(pageId))
        {
            throw new ArgumentException("book_id, chapter_id and page_id are required", nameof(bookId));
        }
        var response = await SendAsync(
                "CreateBookmark", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteString("chapter_id", chapterId);
                    writer.WriteString("page_id", pageId);
                    if (side is not null) writer.WriteString("side", side);
                    if (note is not null) writer.WriteString("note", note);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "CreateBookmark");
        return ReadString(result, "bookmark_id");
    }

    /// <summary>FEA-14-READ-1 (PREQ P13): delete one bookmark.</summary>
    public async Task<bool> DeleteBookmarkAsync(string bookmarkId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookmarkId))
        {
            throw new ArgumentException("bookmark_id is required", nameof(bookmarkId));
        }
        var response = await SendAsync(
                "DeleteBookmark", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteString("bookmark_id", bookmarkId); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "DeleteBookmark");
        return result.TryGetProperty("deleted", out var deleted) && deleted.ValueKind == JsonValueKind.True;
    }

    /// <summary>FEA-14-READ-1 (PREQ P14): whole-book reading progress.</summary>
    public async Task<BookReadingProgressInfo?> GetBookReadingProgressAsync(
        string bookId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }
        var response = await SendAsync(
                "GetBookReadingProgress", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteString("book_id", bookId); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "GetBookReadingProgress");
        return new BookReadingProgressInfo(
            ReadInt(result, "read_pages"),
            ReadInt(result, "total_pages"),
            result.TryGetProperty("percent", out var percent) && percent.ValueKind == JsonValueKind.Number ? percent.GetDouble() : 0.0,
            result.TryGetProperty("finished", out var finished) && finished.ValueKind == JsonValueKind.True);
    }

    /// <summary>FEA-14-READ-1 (PREQ P15): reset one book's reading progress (explicit confirm).</summary>
    public async Task<int> ResetReadingProgressAsync(
        string bookId, bool confirm = false, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }
        var response = await SendAsync(
                "ResetReadingProgress", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteBoolean("confirm", confirm);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ResetReadingProgress");
        return ReadInt(result, "reset");
    }
    /// <summary>FEA-14-FONT-1 (PREQ FONT P1): list user-imported font assets.</summary>
    public async Task<IReadOnlyList<FontAssetInfo>> ListFontAssetsAsync(CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "ListFontAssets", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ListFontAssets");
        var assets = new List<FontAssetInfo>();
        if (result.TryGetProperty("assets", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object) continue;
                assets.Add(new FontAssetInfo(
                    ReadString(item, "asset_id") ?? string.Empty,
                    ReadString(item, "family") ?? string.Empty,
                    ReadString(item, "subfamily") ?? string.Empty,
                    ReadString(item, "format") ?? string.Empty,
                    ReadString(item, "sha256") ?? string.Empty,
                    ReadInt(item, "size_bytes"),
                    ReadString(item, "state") ?? string.Empty));
            }
        }
        return assets;
    }

    /// <summary>FEA-14-FONT-1 (PREQ FONT P2): import one font file (copy + SHA-256).</summary>
    public async Task<FontAssetInfo?> ImportFontAssetAsync(
        string sourcePath, string? licenseNote = null, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(sourcePath))
        {
            throw new ArgumentException("source_path is required", nameof(sourcePath));
        }
        var response = await SendAsync(
                "ImportFontAsset", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("source_path", sourcePath);
                    if (licenseNote is not null) writer.WriteString("license_note", licenseNote);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ImportFontAsset");
        return new FontAssetInfo(
            ReadString(result, "asset_id") ?? string.Empty,
            ReadString(result, "family") ?? string.Empty,
            ReadString(result, "subfamily") ?? string.Empty, string.Empty, string.Empty, 0, "active");
    }

    /// <summary>FEA-14-FONT-1 (PREQ FONT P3): soft-delete one font asset.</summary>
    public async Task<bool> DeleteFontAssetAsync(string assetId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(assetId))
        {
            throw new ArgumentException("asset_id is required", nameof(assetId));
        }
        var response = await SendAsync(
                "DeleteFontAsset", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteString("asset_id", assetId); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "DeleteFontAsset");
        return result.TryGetProperty("deleted", out var deleted) && deleted.ValueKind == JsonValueKind.True;
    }

    /// <summary>FEA-14-FONT-1 (PREQ FONT P4): rescan the managed fonts directory.</summary>
    public async Task<FontRefreshInfo> RefreshFontAssetsAsync(CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "RefreshFontAssets", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "RefreshFontAssets");
        var failed = new List<FontRefreshFailure>();
        if (result.TryGetProperty("failed", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object) continue;
                failed.Add(new FontRefreshFailure(
                    ReadString(item, "path") ?? string.Empty,
                    ReadString(item, "code") ?? string.Empty));
            }
        }
        return new FontRefreshInfo(ReadInt(result, "available"), failed);
    }

    /// <summary>FEA-14-LIB-1 (PREQ LIB P5): patch book display metadata.</summary>
    public async Task<bool> UpdateBookMetadataAsync(
        string bookId, IReadOnlyDictionary<string, object?> patch, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId) || patch.Count == 0)
        {
            throw new ArgumentException("book_id and a non-empty patch are required", nameof(bookId));
        }
        // P3 (r2): the Host port must be able to express P5's tags list, so the
        // patch carries object values: strings (text fields) or tag-id arrays.
        foreach (var pair in patch)
        {
            if (pair.Value is not null and not string and not IReadOnlyList<string>)
            {
                throw new ArgumentException(
                    $"unsupported book metadata value for '{pair.Key}'", nameof(patch));
            }
        }
        var response = await SendAsync(
                "UpdateBookMetadata", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteStartObject("patch");
                    foreach (var pair in patch)
                    {
                        switch (pair.Value)
                        {
                            case null:
                                writer.WriteNull(pair.Key);
                                break;
                            case string text:
                                writer.WriteString(pair.Key, text);
                                break;
                            case IReadOnlyList<string> tagIds:
                                writer.WriteStartArray(pair.Key);
                                foreach (var tagId in tagIds) writer.WriteStringValue(tagId);
                                writer.WriteEndArray();
                                break;
                            default:
                                throw new ArgumentException(
                                    $"unsupported book metadata value for '{pair.Key}'", nameof(patch));
                        }
                    }
                    writer.WriteEndObject();
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "UpdateBookMetadata");
        return result.TryGetProperty("updated", out var updated) && updated.ValueKind == JsonValueKind.True;
    }

    /// <summary>FEA-14-LIB-1 (PREQ LIB P6): reorder a book's chapters.</summary>
    public async Task<bool> ReorderChaptersAsync(
        string bookId, IReadOnlyList<string> orderedChapterIds, CancellationToken cancellationToken = default)
    {
        // R-13/P3 (r2): an empty list is the empty-book no-op; only the book id is required.
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }
        var response = await SendAsync(
                "ReorderChapters", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteStartArray("ordered_ids");
                    foreach (var id in orderedChapterIds) writer.WriteStringValue(id);
                    writer.WriteEndArray();
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ReorderChapters");
        return result.TryGetProperty("updated", out var updated) && updated.ValueKind == JsonValueKind.True;
    }

    /// <summary>FEA-14-LIB-1 (PREQ LIB P7): patch chapter metadata.</summary>
    public async Task<bool> UpdateChapterMetadataAsync(
        string chapterId, IReadOnlyDictionary<string, object?> patch, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId) || patch.Count == 0)
        {
            throw new ArgumentException("chapter_id and a non-empty patch are required", nameof(chapterId));
        }
        var response = await SendAsync(
                "UpdateChapterMetadata", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("chapter_id", chapterId);
                    writer.WriteStartObject("patch");
                    foreach (var pair in patch)
                    {
                        switch (pair.Value)
                        {
                            case null: writer.WriteNull(pair.Key); break;
                            case int intValue: writer.WriteNumber(pair.Key, intValue); break;
                            default: writer.WriteString(pair.Key, pair.Value.ToString()); break;
                        }
                    }
                    writer.WriteEndObject();
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "UpdateChapterMetadata");
        return result.TryGetProperty("updated", out var updated) && updated.ValueKind == JsonValueKind.True;
    }

    /// <summary>FEA-14-LIB-1 (PREQ LIB P8): create a chapter with metadata.</summary>
    public async Task<ChapterSummary?> CreateChapterWithMetadataAsync(
        string bookId, string title, string? kind = null, string? number = null, int? importOrder = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(title))
        {
            throw new ArgumentException("book_id and title are required", nameof(bookId));
        }
        var response = await SendAsync(
                "CreateChapterWithMetadata", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteString("title", title);
                    if (kind is not null) writer.WriteString("kind", kind);
                    if (number is not null) writer.WriteString("number", number);
                    if (importOrder is not null) writer.WriteNumber("import_order", importOrder.Value);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "CreateChapterWithMetadata");
        // R-03: P8 returns sort_order (the appended position) -- never import_order,
        // which is not part of the P8 response.
        return new ChapterSummary(
            ReadString(result, "chapter_id") ?? string.Empty,
            ReadString(result, "title") ?? string.Empty,
            ReadString(result, "number") ?? string.Empty,
            ReadInt(result, "sort_order"));
    }

    /// <summary>FEA-14-EDIT-1 (PREQ EDIT P16): list a book's issue markers (default state=open).</summary>
    public async Task<IReadOnlyList<IssueMarkerInfo>> ListIssueMarkersAsync(
        string bookId, string? state = null, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            throw new ArgumentException("book_id is required", nameof(bookId));
        }
        var response = await SendAsync(
                "ListIssueMarkers", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    if (state is not null) writer.WriteString("state", state);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ListIssueMarkers");
        var markers = new List<IssueMarkerInfo>();
        if (result.TryGetProperty("markers", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object) continue;
                markers.Add(new IssueMarkerInfo(
                    ReadString(item, "marker_id") ?? string.Empty,
                    ReadString(item, "chapter_id") ?? string.Empty,
                    ReadString(item, "page_id") ?? string.Empty,
                    ReadString(item, "kind") ?? string.Empty,
                    ReadString(item, "note"),
                    ReadString(item, "state") ?? string.Empty,
                    ReadString(item, "created_at") ?? string.Empty,
                    ReadIssueMarkerPosition(item),
                    ReadString(item, "resolved_at")));
            }
        }
        return markers;
    }

    /// <summary>FEA-14-EDIT-1 (PREQ EDIT P17): create a marker; returns its id.</summary>
    public async Task<string?> CreateIssueMarkerAsync(
        string bookId, string chapterId, string pageId, string kind,
        string? note = null, IssueMarkerPosition? position = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(chapterId)
            || string.IsNullOrWhiteSpace(pageId) || string.IsNullOrWhiteSpace(kind))
        {
            throw new ArgumentException("book_id, chapter_id, page_id and kind are required", nameof(bookId));
        }
        var response = await SendAsync(
                "CreateIssueMarker", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("book_id", bookId);
                    writer.WriteString("chapter_id", chapterId);
                    writer.WriteString("page_id", pageId);
                    writer.WriteString("kind", kind);
                    if (note is not null) writer.WriteString("note", note);
                    if (position is not null)
                    {
                        writer.WriteStartObject("position");
                        writer.WriteNumber("x", position.X);
                        writer.WriteNumber("y", position.Y);
                        writer.WriteEndObject();
                    }
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "CreateIssueMarker");
        return ReadString(result, "marker_id");
    }

    /// <summary>FEA-14-EDIT-1 (PREQ EDIT P18): resolve a marker.</summary>
    public async Task<bool> ResolveIssueMarkerAsync(string markerId, CancellationToken cancellationToken = default)
        => await SendIssueMarkerStateAsync("ResolveIssueMarker", "resolved", markerId, cancellationToken).ConfigureAwait(false);

    /// <summary>FEA-14-EDIT-1 (PREQ EDIT P19): reopen a marker.</summary>
    public async Task<bool> ReopenIssueMarkerAsync(string markerId, CancellationToken cancellationToken = default)
        => await SendIssueMarkerStateAsync("ReopenIssueMarker", "reopened", markerId, cancellationToken).ConfigureAwait(false);

    /// <summary>FEA-14-EDIT-1 (PREQ EDIT P20): delete a marker (marker row only).</summary>
    public async Task<bool> DeleteIssueMarkerAsync(string markerId, CancellationToken cancellationToken = default)
        => await SendIssueMarkerStateAsync("DeleteIssueMarker", "deleted", markerId, cancellationToken).ConfigureAwait(false);

    private async Task<bool> SendIssueMarkerStateAsync(
        string command, string trueProperty, string markerId, CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(markerId))
        {
            throw new ArgumentException("marker_id is required", nameof(markerId));
        }
        var response = await SendAsync(
                command, CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("marker_id", markerId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, command);
        return ReadBool(result, trueProperty);
    }

    private static IssueMarkerPosition? ReadIssueMarkerPosition(JsonElement item)
    {
        if (!item.TryGetProperty("position", out var position) || position.ValueKind != JsonValueKind.Object)
        {
            return null;
        }
        return new IssueMarkerPosition(ReadDouble(position, "x"), ReadDouble(position, "y"));
    }

    /// <summary>FEA-14-AI-1 (PREQ AI P21): list builtin + user prompt templates.</summary>
    public async Task<IReadOnlyList<PromptTemplateInfo>> ListPromptTemplatesAsync(
        CancellationToken cancellationToken = default)
    {
        var response = await SendAsync(
                "ListPromptTemplates", CoreProtocol.DefaultMinor,
                writer => { writer.WriteStartObject(); writer.WriteEndObject(); },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "ListPromptTemplates");
        var templates = new List<PromptTemplateInfo>();
        if (result.TryGetProperty("templates", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object) continue;
                templates.Add(new PromptTemplateInfo(
                    ReadString(item, "template_id") ?? string.Empty,
                    ReadString(item, "name") ?? string.Empty,
                    ReadInt(item, "version"),
                    ReadBool(item, "builtin")));
            }
        }
        return templates;
    }

    /// <summary>FEA-14-AI-1 (PREQ AI P22): create/update a user template.</summary>
    public async Task<PromptTemplateInfo?> SavePromptTemplateAsync(
        string name, string body, string? templateId = null, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(name) || string.IsNullOrWhiteSpace(body))
        {
            throw new ArgumentException("name and body are required", nameof(name));
        }
        var response = await SendAsync(
                "SavePromptTemplate", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    if (templateId is not null) writer.WriteString("template_id", templateId);
                    writer.WriteString("name", name);
                    writer.WriteString("body", body);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "SavePromptTemplate");
        var savedId = ReadString(result, "template_id");
        if (savedId is null) return null;
        return new PromptTemplateInfo(savedId, name, ReadInt(result, "version"), false);
    }

    /// <summary>FEA-14-AI-1 (PREQ AI P23): delete a user template with a mandatory replacement.</summary>
    public async Task<PromptTemplateDeleteResult> DeletePromptTemplateAsync(
        string templateId, string replacementId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(templateId) || string.IsNullOrWhiteSpace(replacementId))
        {
            throw new ArgumentException("template_id and replacement_id are required", nameof(templateId));
        }
        var response = await SendAsync(
                "DeletePromptTemplate", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("template_id", templateId);
                    writer.WriteString("replacement_id", replacementId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "DeletePromptTemplate");
        return new PromptTemplateDeleteResult(ReadBool(result, "deleted"));
    }

    /// <summary>FEA-14-AI-1 (PREQ AI P24): copy a builtin into an editable template.</summary>
    public async Task<PromptTemplateInfo?> CopyBuiltinPromptTemplateAsync(
        string builtinId, string? name = null, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(builtinId))
        {
            throw new ArgumentException("builtin_id is required", nameof(builtinId));
        }
        var response = await SendAsync(
                "CopyBuiltinPromptTemplate", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("builtin_id", builtinId);
                    if (name is not null) writer.WriteString("name", name);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "CopyBuiltinPromptTemplate");
        var copiedId = ReadString(result, "template_id");
        if (copiedId is null) return null;
        // P24's wire response only carries template_id; refresh through P21 for the
        // Core-assigned name (a null name defaults to "<builtin> (copy)" in Core).
        return new PromptTemplateInfo(copiedId, name ?? string.Empty, 1, false);
    }

    /// <summary>FEA-14-AI-1 (PREQ AI P25): references that block/precede a delete.</summary>
    public async Task<IReadOnlyList<PromptTemplateReference>> GetPromptTemplateReferencesAsync(
        string templateId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(templateId))
        {
            throw new ArgumentException("template_id is required", nameof(templateId));
        }
        var response = await SendAsync(
                "GetPromptTemplateReferences", CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("template_id", templateId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "GetPromptTemplateReferences");
        var references = new List<PromptTemplateReference>();
        if (result.TryGetProperty("references", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object) continue;
                references.Add(new PromptTemplateReference(
                    ReadString(item, "kind") ?? string.Empty,
                    ReadString(item, "owner_id") ?? string.Empty,
                    ReadString(item, "label") ?? string.Empty));
            }
        }
        return references;
    }

    /// <summary>Reader projection read face (<c>GetReaderProjection</c>, mode=original, start=beginning).</summary>
    public async Task<ReaderProjection> GetReaderProjectionAsync(
        string chapterId,
        string mode = "original",
        string startPosition = ReaderStartPosition.Resume,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            throw new ArgumentException("chapter_id is required", nameof(chapterId));
        }

        if (startPosition is not (ReaderStartPosition.Resume or ReaderStartPosition.Beginning))
        {
            throw new ArgumentException($"unknown start_position: {startPosition}", nameof(startPosition));
        }

        var response = await SendAsync(
                "GetReaderProjection",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("chapter_id", chapterId);
                    writer.WriteString("mode", mode);
                    writer.WriteString("start_position", startPosition);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "GetReaderProjection");
        var pages = new List<ReaderPageSummary>();
        if (result.TryGetProperty("pages", out var array) && array.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in array.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object)
                {
                    throw Malformed("GetReaderProjection page entry is not an object");
                }

                string? resourceId = null;
                string? revisionId = null;
                string? sha256 = null;
                if (item.TryGetProperty("original", out var original) && original.ValueKind == JsonValueKind.Object)
                {
                    sha256 = ReadString(original, "sha256");
                    if (original.TryGetProperty("resource_ref", out var resourceRef) && resourceRef.ValueKind == JsonValueKind.Object)
                    {
                        resourceId = ReadString(resourceRef, "resource_id");
                        revisionId = ReadString(resourceRef, "revision");
                    }
                }

                pages.Add(new ReaderPageSummary(
                    ReadString(item, "page_id") ?? string.Empty,
                    ReadInt(item, "order"),
                    ReadInt(item, "width_px"),
                    ReadInt(item, "height_px"),
                    resourceId,
                    revisionId,
                    sha256));
            }
        }

        var initialPageId = (string?)null;
        var initialOffsetY = 0d;
        if (result.TryGetProperty("initial_position", out var initial) && initial.ValueKind == JsonValueKind.Object)
        {
            initialPageId = ReadString(initial, "page_id");
            initialOffsetY = ReadDouble(initial, "scroll_offset_y");
        }

        ReadingProgressSnapshot? saved = null;
        if (result.TryGetProperty("saved_progress", out var savedElement) && savedElement.ValueKind == JsonValueKind.Object)
        {
            saved = ParseProgressSnapshot(savedElement);
        }

        return new ReaderProjection(
            ReadString(result, "book_id") ?? string.Empty,
            ReadString(result, "chapter_id") ?? chapterId,
            ReadString(result, "mode") ?? mode,
            ReadString(result, "layout") ?? string.Empty,
            pages)
        {
            InitialPageId = initialPageId,
            InitialScrollOffsetY = initialOffsetY,
            SavedProgress = saved,
        };
    }

    /// <summary>
    /// READER-PROGRESS-1: persists one progress coordinate via the frozen Core command
    /// <c>SaveReadingProgress</c> (contract M2-C1 §5). Optional fields follow the old shell
    /// discipline: MISSING = NOT SENT (no <c>elapsed_seconds_delta</c> replay for accepted
    /// intervals; the caller only sends the delta accumulated since its previous success).
    /// </summary>
    public async Task<ReadingProgressSnapshot> SaveReadingProgressAsync(
        string chapterId,
        string mode,
        string pageId,
        double? scrollOffsetY = null,
        double? elapsedSecondsDelta = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            throw new ArgumentException("chapter_id is required", nameof(chapterId));
        }

        if (string.IsNullOrWhiteSpace(pageId))
        {
            throw new ArgumentException("page_id is required", nameof(pageId));
        }

        if (mode is not ("original" or "translated"))
        {
            throw new ArgumentException($"unknown reading mode: {mode}", nameof(mode));
        }

        var response = await SendAsync(
                "SaveReadingProgress",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("chapter_id", chapterId);
                    writer.WriteString("mode", mode);
                    writer.WriteString("page_id", pageId);
                    if (scrollOffsetY is { } offset && double.IsFinite(offset) && offset >= 0)
                    {
                        writer.WriteNumber("scroll_offset_y", offset);
                    }

                    // M2-C1 §5: elapsed_seconds_delta is the non-negative time accumulated by the
                    // caller since its previous successful save; omit it when there is nothing new.
                    if (elapsedSecondsDelta is { } elapsed && double.IsFinite(elapsed) && elapsed > 0)
                    {
                        writer.WriteNumber("elapsed_seconds_delta", elapsed);
                    }

                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "SaveReadingProgress");
        if (result.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("SaveReadingProgress result is not an object");
        }

        return ParseProgressSnapshot(result);
    }

    /// <summary>Publishes/looks up the page-original catalog key used by the Host resource channel.</summary>
    public async Task<ResolvedPageResource> ResolvePageResourceAsync(string pageId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(pageId))
        {
            throw new ArgumentException("page_id is required", nameof(pageId));
        }

        var response = await SendAsync(
                "resolve_page_resource",
                CoreProtocol.DefaultMinor,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", pageId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, "resolve_page_resource");
        return new ResolvedPageResource(
            ReadString(result, "resource_id") ?? string.Empty,
            ReadString(result, "revision") ?? "original");
    }

    /// <summary>Raw escaping test hook (AC3 negative): sends the line verbatim, never throws on Core errors.</summary>
    public async Task<CoreResponse> SendRawAsync(string rawJsonLine, CancellationToken cancellationToken = default)
    {
        // PIPE-EXCLUSIVE-TRANSPORT-1 / E-7 (window 2): this hook used to bypass the client gate entirely,
        // so a raw frame could race every normal command on the same stdin/stdout pair. The raw line
        // carries its own request_id (if any), so we do not validate the id here -- but the pipe must
        // still be exclusive. E-7 #1: exclusivity comes from the transport lease for every caller now.
        var lease = await _process.AcquireExchangeLeaseAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var frame = await _process
                .ExchangeAsync(rawJsonLine, escapeNonAscii: false, _options.RequestTimeout, cancellationToken)
                .ConfigureAwait(false);
            return CoreProtocol.Parse(frame.ResponseLine);
        }
        finally
        {
            lease.Dispose();
        }
    }
    /// <summary>
    /// E-7 / R-002: how many extra response frames may be discarded while looking for the response that
    /// belongs to <paramref name="requestId"/>. Deliberately the same bound as the event-frame skip loop,
    /// so there is one number to reason about rather than two.
    /// </summary>
    internal const int ResyncMaxDrainFrames = 16;

    /// <summary>
    /// E-7 / R-002: turns the first response line into the response for <paramref name="requestId"/>,
    /// discarding event frames and — the R-002 fix — any response that carries a DIFFERENT request id.
    ///
    /// <para>Before this, a mismatched id threw immediately and left the real response on the wire, so the
    /// next command read its predecessor's answer: a permanent off-by-one until the sidecar restarted.</para>
    ///
    /// <para>Bounded on purpose: after <paramref name="maxDrainFrames"/> discarded frames the pipe is
    /// considered unresynchronisable, the channel is poisoned and the caller fails closed — better than
    /// silently handing every subsequent command the wrong payload.</para>
    /// </summary>
    internal static async Task<CoreResponse> ReadResponseForRequestAsync(
        string firstLine,
        string requestId,
        Func<CancellationToken, Task<string>> readNextLine,
        Action poisonChannel,
        int maxDrainFrames,
        string? stderrLogPath,
        CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(readNextLine);
        ArgumentNullException.ThrowIfNull(poisonChannel);

        var line = firstLine;
        for (var frames = 0; ; frames++)
        {
            var response = CoreProtocol.Parse(line);

            // An EVENT frame is a single-direction notification: it carries no request id and must never be
            // mistaken for "a response without an id that therefore belongs to us" (the first version of
            // this helper did exactly that, and R002ResyncTests caught it).
            if (!CoreProtocol.IsEventFrame(line) && BelongsToRequest(response, requestId))
            {
                return response;
            }

            if (frames >= maxDrainFrames)
            {
                poisonChannel();
                throw new SidecarException(
                    SidecarErrorCode.MalformedResponse,
                    SidecarSpec.CoreServiceName,
                    $"response request_id could not be resynchronised to '{requestId}' within "
                    + $"{maxDrainFrames} response frames; the core pipe is out of step, channel poisoned",
                    stderrLogPath);
            }

            line = await readNextLine(cancellationToken).ConfigureAwait(false);
        }
    }

    /// <summary>
    /// A response belongs to the request only when it carries that exact request id.
    ///
    /// <para><b>E-7 #2 — fail-closed (Codex ruling 2026-11-16).</b> This used to treat "no request_id"
    /// as belonging to the request (fail-open). The ruling rejected that for the production path: holding
    /// the exchange lease only proves the pipe is used serially, it does NOT prove the response belongs to
    /// this command — a damaged response, a duplicate frame, or a resync that stopped early all still land
    /// in the caller's hands under fail-open. Event frames are already excluded upstream by
    /// <c>CoreProtocol.IsEventFrame</c>, so they do not need the leniency either.</para>
    ///
    /// <para><c>SendRawAsync</c> deliberately does NOT go through this method: it is the raw-wire
    /// observation hook and keeps "return whatever came back" semantics (ruling: no new opt-out switch).</para>
    ///
    /// <para>Consequence accepted by the ruling: a response that genuinely lacks an id (the frozen core
    /// emits <c>request_id: null</c> for requests that did not supply one) is now treated as a mismatched
    /// frame — it is discarded by the bounded resync and, if no matching frame arrives within the budget,
    /// the channel is poisoned instead of silently handing over an unverifiable payload.</para>
    /// </summary>
    private static bool BelongsToRequest(CoreResponse response, string requestId) =>
        response.RequestId is { } actual && string.Equals(actual, requestId, StringComparison.Ordinal);

    internal static void EnsureResponseBelongsToRequest(
        CoreResponse response, string requestId, string? stderrLogPath)
    {
        if (response.RequestId is { } actual && !string.Equals(actual, requestId, StringComparison.Ordinal))
        {
            throw new SidecarException(
                SidecarErrorCode.MalformedResponse,
                SidecarSpec.CoreServiceName,
                $"response request_id '{actual}' does not match request '{requestId}': "
                + "the core pipe returned another command's response",
                stderrLogPath);
        }
    }

    public async Task<CoreResponse> SendAsync(
        string command,
        int minor,
        Action<Utf8JsonWriter> payload,
        TimeSpan timeout,
        CancellationToken cancellationToken = default)
    {
        var requestId = $"req-{Interlocked.Increment(ref _requestCounter)}";
        var line = CoreProtocol.BuildRequest(requestId, command, minor, payload);

        // CORE-PIPE-EXCLUSIVE-1: hold the pipe for the entire cycle (write + read + event-frame skipping).
        var lease = await _process.AcquireExchangeLeaseAsync(cancellationToken).ConfigureAwait(false);
        try
        {
        var frame = await _process.ExchangeAsync(line, escapeNonAscii: true, timeout, cancellationToken).ConfigureAwait(false);

        // READER-PROGRESS-1: core_service pushes event frames (ReadingProgressChanged …) on the same
        // stdout pipe *before* the command response. E-7 / R-002 additionally requires resynchronising
        // when a response carries a DIFFERENT request id (otherwise the real response stays on the wire
        // and the next command reads it — a permanent off-by-one). Both are handled inside the helper.
        var response = await ReadResponseForRequestAsync(
                frame.ResponseLine,
                requestId,
                ct => _process.ReadNextResponseLineAsync(timeout, ct),
                _process.Poison,
                ResyncMaxDrainFrames,
                _options.StderrLogPath,
                cancellationToken)
            .ConfigureAwait(false);
        if (response.Error is { } error)
        {
            throw new CoreOperationException(error.Code, error.Category, error.Retryable, error.Message, response.RequestId ?? requestId);
        }

        return response;
        }
        finally
        {
            lease.Dispose();
        }
    }

    /// <summary>
    /// FEA-11-SCAN-2 (C-17 v1.1 / B1): the read-only cold-start scan-target enumeration command
    /// (<c>source_list_scan_targets</c>, application channel, closed empty request object). It is
    /// Host-internal: deliberately NOT registered on the Host command dispatcher / C-07 and it has
    /// no UI face; the Host calls it directly before the first periodic scan tick.
    /// </summary>
    public const string SourceListScanTargetsCommand = "source_list_scan_targets";

    /// <summary>FEA-11-SCAN-2 (C-17 v1.1): the additive capability that gates the enumeration command.</summary>
    public const string SourceEnumerateCapability = "source.sync.enumerate/1";

    /// <summary>
    /// FEA-11-SCAN-2 (B1 / AC-S2-1): enumerates the Core's authoritative scan targets. Capability is
    /// probed first (C-17 §5 / M2-C1 §5.13 fail-closed rule: never probe by dispatching the command and
    /// interpreting <c>UNKNOWN_COMMAND</c>); a missing capability surfaces as typed
    /// <c>CORE_CAPABILITY_MISSING</c> from <see cref="RequireCapabilitiesAsync"/>.
    /// </summary>
    public async Task<JsonElement> ListSourceScanTargetsAsync(CancellationToken cancellationToken = default)
    {
        await RequireCapabilitiesAsync(new[] { SourceEnumerateCapability }, cancellationToken)
            .ConfigureAwait(false);
        var response = await SendAsync(
                SourceListScanTargetsCommand,
                CoreProtocol.DefaultMinor,
                WireJson.EmptyObject,
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return RequireResult(response, SourceListScanTargetsCommand);
    }

    /// <summary>
    /// FEA-11-HOST-AUTH-3 (C-17 v1.2 §5.1): the read-only plan materialization projection
    /// (<c>source_get_sync_plan_materialized</c>, host-control, closed shape). Host-internal:
    /// deliberately NOT registered on the Host command dispatcher / C-07 and it has no UI face.
    /// Zero writes; the returned data is NOT an authorization -- the caller still mints a fresh
    /// grant through the existing C-16 validation path.
    /// </summary>
    public const string SourceGetSyncPlanMaterializedCommand = "GetSourceSyncPlanMaterialized";

    /// <summary>FEA-11-HOST-AUTH-3: the additive capability gating the projection.</summary>
    public const string SourcePlanMaterializationCapability = "source.sync.plan-materialization/1";

    /// <summary>One projected plan target entry (Core-authoritative locator/ordinal).</summary>
    public sealed record SourcePlanMaterializedEntry(
        string EntryId,
        string Locator,
        int Ordinal,
        string ContentDigestKind,
        string? ContentDigest);

    /// <summary>The projected plan subset the recovery path re-mints grants from.</summary>
    public sealed record SourceSyncPlanMaterialization(
        string Format,
        string PlanId,
        string PlanDigest,
        string Kind,
        string SourceId,
        string? VersionId,
        string? ContentDigest,
        IReadOnlyList<SourcePlanMaterializedEntry> Entries,
        string ReferenceSetDigest,
        string State,
        string ExpiresAt);

    /// <summary>
    /// FEA-11-HOST-AUTH-3: read back the persisted plan subset (C-17 v1.2). Capability is probed
    /// first (never by dispatching the command and interpreting UNKNOWN_COMMAND).
    /// </summary>
    public async Task<SourceSyncPlanMaterialization> GetSourceSyncPlanMaterializedAsync(
        string planId,
        string planDigest,
        CancellationToken cancellationToken = default)
    {
        await RequireCapabilitiesAsync(new[] { SourcePlanMaterializationCapability }, cancellationToken)
            .ConfigureAwait(false);
        var response = await SendHostControlAsync(
                SourceGetSyncPlanMaterializedCommand,
                writer =>
                {
                    writer.WriteString("plan_id", planId);
                    writer.WriteString("plan_digest", planDigest);
                },
                _options.RequestTimeout,
                HostSession,
                cancellationToken)
            .ConfigureAwait(false);
        var result = RequireResult(response, SourceGetSyncPlanMaterializedCommand);
        if (result.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("materialization result is not an object");
        }

        // R-r1-11: a required field that is missing/wrong-typed is a malformed response,
        // never a silent empty string / zero.
        string RequireText(string name)
        {
            var value = ReadString(result, name);
            if (string.IsNullOrWhiteSpace(value))
            {
                throw Malformed($"materialization result is missing {name}");
            }
            return value;
        }

        if (!result.TryGetProperty("entries", out var entriesJson)
            || entriesJson.ValueKind != JsonValueKind.Array)
        {
            throw Malformed("materialization result is missing entries");
        }
        var entries = new List<SourcePlanMaterializedEntry>();
        foreach (var item in entriesJson.EnumerateArray())
        {
            var entryId = ReadString(item, "entry_id");
            var locator = ReadString(item, "locator");
            var kind = ReadString(item, "content_digest_kind");
            var ordinal = item.TryGetProperty("ordinal", out var ordinalJson)
                && ordinalJson.ValueKind == JsonValueKind.Number
                    ? ordinalJson.GetInt32()
                    : (int?)null;
            if (string.IsNullOrWhiteSpace(entryId) || string.IsNullOrWhiteSpace(locator)
                || string.IsNullOrWhiteSpace(kind) || ordinal is null)
            {
                throw Malformed("materialization entry is malformed");
            }
            entries.Add(new SourcePlanMaterializedEntry(
                entryId, locator, ordinal.Value, kind, ReadString(item, "content_digest")));
        }

        return new SourceSyncPlanMaterialization(
            RequireText("format"),
            RequireText("plan_id"),
            RequireText("plan_digest"),
            RequireText("kind"),
            RequireText("source_id"),
            ReadString(result, "version_id"),
            ReadString(result, "content_digest"),
            entries,
            RequireText("reference_set_digest"),
            RequireText("state"),
            RequireText("expires_at"));
    }

    public async Task ShutdownAsync(CancellationToken cancellationToken = default)
    {
        if (_disposed)
        {
            return;
        }

        try
        {
            await SendAsync("core.shutdown", CoreProtocol.DefaultMinor, WireJson.EmptyObject, TimeSpan.FromSeconds(5), cancellationToken)
                .ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is SidecarException or CoreOperationException or OperationCanceledException)
        {
            // shutdown is best effort; DisposeAsync kills a hung core
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        // Await pipe/process release before another Core opens this DataRoot's scheduler lease.
        await _process.StopAsync().ConfigureAwait(false);
        await _process.DisposeAsync().ConfigureAwait(false);
    }

    private static JsonElement RequireResult(CoreResponse response, string command)
    {
        if (response.Result is { } result)
        {
            return result;
        }

        throw new CoreOperationException("INVALID_RESPONSE", "internal", false, $"{command} returned no result", response.RequestId);
    }

    private static BackupPackageInfo ParseBackupPackage(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("backup package entry is not an object");
        }

        return new BackupPackageInfo(
            ReadString(element, "backup_id") ?? string.Empty,
            ReadString(element, "backup_type") ?? "unknown",
            ReadString(element, "created_at") ?? string.Empty,
            element.TryGetProperty("size_bytes", out var size) && size.ValueKind == JsonValueKind.Number
                ? size.GetInt64()
                : 0,
            element.TryGetProperty("schema_version", out var schema) && schema.ValueKind == JsonValueKind.Number
                ? schema.GetInt32()
                : 0,
            ReadBool(element, "verified"),
            ReadString(element, "database_id"));
    }

    private static BookSummary ParseBook(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            throw Malformed("book entry is not an object");
        }

        return new BookSummary(
            ReadString(element, "book_id") ?? string.Empty,
            ReadString(element, "title") ?? string.Empty,
            ReadString(element, "original_title") ?? string.Empty,
            ReadBool(element, "is_favorite"),
            ReadBool(element, "is_archived"),
            element.TryGetProperty("page_count", out var pages) && pages.ValueKind == JsonValueKind.Number
                ? pages.GetInt32()
                : null,
            ReadString(element, "created_at") ?? string.Empty,
            ReadString(element, "updated_at") ?? string.Empty);
    }

    private static SidecarException Malformed(string detail) =>
        new(SidecarErrorCode.MalformedResponse, SidecarSpec.CoreServiceName, detail);

    /// <summary>
    /// Parses the optional <c>geometry</c> row field (contract rev 1.5): <c>bbox</c> = [x, y, w, h]
    /// normalized and <c>polygon</c> = [[x, y], ...]. A row without geometry (page with no extent)
    /// yields null instead of a fabricated rectangle.
    /// </summary>
    private static RegionGeometrySummary? ParseRegionGeometry(JsonElement row)
    {
        if (!row.TryGetProperty("geometry", out var geometry) || geometry.ValueKind != JsonValueKind.Object)
        {
            return null;
        }

        if (!geometry.TryGetProperty("bbox", out var bbox) ||
            bbox.ValueKind != JsonValueKind.Array ||
            bbox.GetArrayLength() < 4)
        {
            throw Malformed("list_regions geometry.bbox is not a 4-element array");
        }

        var values = new double[4];
        var index = 0;
        foreach (var value in bbox.EnumerateArray())
        {
            if (index >= values.Length || value.ValueKind != JsonValueKind.Number)
            {
                throw Malformed("list_regions geometry.bbox has a non-numeric value");
            }

            values[index++] = value.GetDouble();
        }

        var polygon = new List<RegionGeometryPoint>();
        if (geometry.TryGetProperty("polygon", out var ring) && ring.ValueKind == JsonValueKind.Array)
        {
            foreach (var point in ring.EnumerateArray())
            {
                if (point.ValueKind != JsonValueKind.Array || point.GetArrayLength() < 2)
                {
                    throw Malformed("list_regions geometry.polygon point is not a 2-element array");
                }

                var x = point[0];
                var y = point[1];
                if (x.ValueKind != JsonValueKind.Number || y.ValueKind != JsonValueKind.Number)
                {
                    throw Malformed("list_regions geometry.polygon point has a non-numeric value");
                }

                polygon.Add(new RegionGeometryPoint(x.GetDouble(), y.GetDouble()));
            }
        }

        return new RegionGeometrySummary(values[0], values[1], values[2], values[3], polygon);
    }

    /// <summary>Parses the post-write effective state (<c>set_region_type</c> / <c>restore_region_revision</c>).</summary>
    private static RegionWriteSnapshot ParseRegionWriteSnapshot(JsonElement result, string fallbackRegionId) => new(
        ReadString(result, "region_id") ?? fallbackRegionId,
        ReadInt(result, "revision_no"),
        ReadString(result, "region_type") ?? string.Empty,
        ReadString(result, "sfx_policy") ?? string.Empty);

    /// <summary>READER-PROGRESS-1: parses the committed <c>ReadingProgressSnapshot</c> (contract §6.3).</summary>
    private static ReadingProgressSnapshot ParseProgressSnapshot(JsonElement element) => new(
        ReadString(element, "book_id") ?? string.Empty,
        ReadString(element, "chapter_id") ?? string.Empty,
        ReadString(element, "mode") ?? "original",
        ReadString(element, "last_page_id"),
        ReadDouble(element, "scroll_offset_y"),
        ReadDouble(element, "progress_percent"),
        ReadString(element, "last_read_at"),
        ReadDouble(element, "total_read_seconds"));

    private static string? ReadString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static double ReadDouble(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Number
            ? value.GetDouble()
            : 0d;

    private static bool ReadBool(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.True;

    private static int ReadInt(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Number
            ? value.GetInt32()
            : 0;
}

/// <summary>Safe UI projection: full target/settings/provider snapshots stay within Host/Core.</summary>
public sealed record PreparedRunPreview(string PreparedRunId, string SnapshotDigest, int Generation,
    DateTimeOffset ExpiresAt, JsonElement DisplaySummary, JsonElement RedactedPayloadPreview);

/// <summary>Frozen <c>GetReaderProjection.start_position</c> values (contract M2-C1 §5).</summary>
public static class ReaderStartPosition
{
    /// <summary>Restores the persisted (book, chapter, mode) page; never mutates saved progress.</summary>
    public const string Resume = "resume";

    /// <summary>Starts at the first page / offset 0 without touching saved progress.</summary>
    public const string Beginning = "beginning";
}

/// <summary>
/// FEA-12-PREREQ-1 / M2-C1 rev 2.13: the delete-preview + trash wire contract constants.
/// These are REGISTRATION-ONLY values: the frozen Core runtime does not implement the commands
/// yet. <c>PermanentlyDeleteBook</c>/<c>PermanentlyDeleteBooks</c> keep their per-command wire
/// minor 10 (the <c>inventory_digest</c> fields are additive). The runtime capability probe
/// (<c>core.ping</c> missing -&gt; <c>CORE_CAPABILITY_MISSING</c>) belongs to FEA-12-CORE.
/// </summary>
public static class DeleteTrashWireTargets
{
    /// <summary>C-04b `:47`: <c>PreviewPermanentDeleteBooks</c> target wire minor.</summary>
    public const int PreviewPermanentDeleteBooksMinor = 11;

    /// <summary>C-09 SC-B06: the trash command family target wire minor (independent family).</summary>
    public const int TrashCommandsMinor = 13;

    /// <summary>C-04b §2.4 / M2-C1 rev 2.13 capability of the read-only delete preview.</summary>
    public const string DeletePreviewCapability = "library.delete.preview/1";

    /// <summary>C-09 SC-B06 capability of the trash read face (<c>ListTrash</c>).</summary>
    public const string TrashReadCapability = "library.trash.read/1";

    /// <summary>C-09 SC-B06 capability of the trash write face (<c>MoveToTrash</c>/<c>RestoreFromTrash</c>/<c>PurgeTrash</c>).</summary>
    public const string TrashWriteCapability = "library.trash.write/1";
}

/// <summary>FEA-14-READ-1: per-book reading preferences (PREQ P9/P10).</summary>
public sealed record ReadingPreferencesInfo(
    string BookId, string Mode, string Direction, double Zoom,
    bool DoublePage, string Layout, string UpdatedAt, bool IsDefault);

/// <summary>FEA-14-READ-1: partial preferences patch (only non-null fields are sent).</summary>
public sealed record ReadingPreferencesPatch(
    string? Mode = null, string? Direction = null, double? Zoom = null,
    bool? DoublePage = null, string? Layout = null);

/// <summary>FEA-14-READ-1: one bookmark (PREQ P11/P12).</summary>
public sealed record BookmarkInfo(
    string BookmarkId, string BookId, string ChapterId, string PageId,
    string? Side, string? Note, string CreatedAt);

/// <summary>FEA-14-READ-1: whole-book reading progress (PREQ P14).</summary>
public sealed record BookReadingProgressInfo(int ReadPages, int TotalPages, double Percent, bool Finished);

/// <summary>FEA-14-FONT-1: one user-imported font asset.</summary>
public sealed record FontAssetInfo(
    string AssetId, string Family, string Subfamily, string Format,
    string Sha256, int SizeBytes, string State);

/// <summary>FEA-14-FONT-1: one failed entry of a fonts refresh.</summary>
public sealed record FontRefreshFailure(string Path, string Code);

/// <summary>FEA-14-FONT-1: result of a fonts refresh.</summary>
public sealed record FontRefreshInfo(int Available, IReadOnlyList<FontRefreshFailure> Failed);
