using System.Security.Cryptography;
using System.Text.Json;
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
public sealed record ChapterSummary(string ChapterId, string Title, string ChapterNumber, int SortOrder);

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
    /// <summary>M2-PAGE-NAV-PROJECTION-1: <c>list_chapter_pages</c> was introduced at protocol minor 6.</summary>
    private const int ChapterPagesMinor = 6;

    private readonly SidecarProcess _process;
    private readonly CoreServiceOptions _options;
    private int _requestCounter;
    private bool _disposed;
    private readonly SemaphoreSlim _sessionGate = new(1, 1);

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

        var frame = await _process
            .ExchangeAsync(line, escapeNonAscii: true, timeout, cancellationToken)
            .ConfigureAwait(false);
        var responseLine = frame.ResponseLine;
        for (var skipped = 0; skipped < 16 && CoreProtocol.IsEventFrame(responseLine); skipped++)
        {
            responseLine = await _process
                .ReadNextResponseLineAsync(timeout, cancellationToken)
                .ConfigureAwait(false);
        }

        var response = CoreProtocol.Parse(responseLine);
        if (response.Error is { } error)
        {
            throw new CoreOperationException(
                error.Code, error.Category, error.Retryable, error.Message, response.RequestId ?? requestId);
        }

        return response;
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

                chapters.Add(new ChapterSummary(
                    ReadString(item, "chapter_id") ?? string.Empty,
                    ReadString(item, "title") ?? string.Empty,
                    ReadString(item, "chapter_number") ?? string.Empty,
                    ReadInt(item, "sort_order")));
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
        var frame = await _process
            .ExchangeAsync(rawJsonLine, escapeNonAscii: false, _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        return CoreProtocol.Parse(frame.ResponseLine);
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
        var frame = await _process.ExchangeAsync(line, escapeNonAscii: true, timeout, cancellationToken).ConfigureAwait(false);

        // READER-PROGRESS-1: core_service pushes event frames (ReadingProgressChanged …) on the same
        // stdout pipe *before* the command response. Skip them until the response envelope arrives
        // (bounded so a broken sidecar still fails fast instead of hanging).
        var responseLine = frame.ResponseLine;
        for (var skipped = 0; skipped < 16 && CoreProtocol.IsEventFrame(responseLine); skipped++)
        {
            responseLine = await _process
                .ReadNextResponseLineAsync(timeout, cancellationToken)
                .ConfigureAwait(false);
        }

        var response = CoreProtocol.Parse(responseLine);
        if (response.Error is { } error)
        {
            throw new CoreOperationException(error.Code, error.Category, error.Retryable, error.Message, response.RequestId ?? requestId);
        }

        return response;
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

/// <summary>Frozen <c>GetReaderProjection.start_position</c> values (contract M2-C1 §5).</summary>
public static class ReaderStartPosition
{
    /// <summary>Restores the persisted (book, chapter, mode) page; never mutates saved progress.</summary>
    public const string Resume = "resume";

    /// <summary>Starts at the first page / offset 0 without touching saved progress.</summary>
    public const string Beginning = "beginning";
}
