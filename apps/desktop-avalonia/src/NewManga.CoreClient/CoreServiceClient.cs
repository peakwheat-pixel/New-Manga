using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
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
    private readonly SidecarProcess _process;
    private readonly CoreServiceOptions _options;
    private int _requestCounter;
    private bool _disposed;

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
