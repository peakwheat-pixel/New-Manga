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
        var response = CoreProtocol.Parse(frame.ResponseLine);
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

    private static string? ReadString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static bool ReadBool(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.True;

    private static int ReadInt(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Number
            ? value.GetInt32()
            : 0;
}
