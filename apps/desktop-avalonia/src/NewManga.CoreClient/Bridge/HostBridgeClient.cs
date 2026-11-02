using System.Text.Json;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Transport;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Bridge;

public sealed record IssuedRef(string GrantId, long Size);

public sealed record BridgeGrant(
    string ScopeClass,
    string ResourceId,
    string RevisionFingerprint,
    string RelPath,
    long Size,
    string Sha256,
    long VolumeSerial,
    long FileIndex);

/// <summary>Typed control-plane error from the resource channel (code passthrough, RC2 hardening).</summary>
public sealed class BridgeException : Exception
{
    public BridgeException(string code, string? detail = null)
        : base($"[{code}] {detail ?? "resource channel error"}")
    {
        Code = code;
    }

    public string Code { get; }

    public string UserMessage => Code switch
    {
        "RESOURCE_NOT_CATALOGED" => "资源未在 Core 目录中登记（RESOURCE_NOT_CATALOGED）。",
        "REF_REVOKED" => "资源授权已撤销（REF_REVOKED）。",
        "REF_MALFORMED" => "资源通道请求格式非法（REF_MALFORMED）。",
        _ => $"资源通道错误（{Code}）。",
    };
}

public sealed class HostBridgeOptions
{
    public required string ExecutablePath { get; init; }

    /// <summary>M2RC1_DERIVED_ROOT (servable derived scope root).</summary>
    public required string DerivedRoot { get; init; }

    /// <summary>M2RC1_MANAGED_ROOT (servable managed scope root).</summary>
    public required string ManagedRoot { get; init; }

    /// <summary>M2RC2_CATALOG_DB (Core/SQLite catalog authority).</summary>
    public required string CatalogDbPath { get; init; }

    public required string StderrLogPath { get; init; }

    public string? WireLogPath { get; init; }

    public TimeSpan StartupTimeout { get; init; } = TimeSpan.FromSeconds(30);

    public TimeSpan RequestTimeout { get; init; } = TimeSpan.FromSeconds(30);
}

/// <summary>
/// wire-v1 control plane to <c>host_bridge.exe</c>: <c>ping</c>, <c>issue</c>, <c>resolve</c>,
/// <c>revoke</c>, <c>revoke_resource</c>, <c>shutdown</c>. The host never names a path — only a
/// catalog resource id — and the returned grant carries the issue-time facts for handle-verified
/// reads (ADR-0002 resource-channel contract).
/// </summary>
public sealed class HostBridgeClient : IAsyncDisposable
{
    private readonly SidecarProcess _process;
    private readonly HostBridgeOptions _options;
    private int _requestCounter;
    private bool _disposed;

    private HostBridgeClient(SidecarProcess process, HostBridgeOptions options)
    {
        _process = process;
        _options = options;
    }

    public WireLog Wire => _process.Log;

    public string StderrTail => _process.StderrTail;

    public static async Task<HostBridgeClient> StartAsync(
        HostBridgeOptions options,
        CancellationToken cancellationToken = default)
    {
        var spec = new SidecarSpec
        {
            Name = SidecarSpec.HostBridgeName,
            ExecutablePath = options.ExecutablePath,
            Environment = new Dictionary<string, string>(StringComparer.Ordinal)
            {
                ["M2RC1_DERIVED_ROOT"] = options.DerivedRoot,
                ["M2RC1_MANAGED_ROOT"] = options.ManagedRoot,
                ["M2RC2_CATALOG_DB"] = options.CatalogDbPath,
            },
            StderrLogPath = options.StderrLogPath,
            WireLogPath = options.WireLogPath,
            StartupTimeout = options.StartupTimeout,
            RequestTimeout = options.RequestTimeout,
        };

        var process = await SidecarProcess.StartAsync(spec, cancellationToken).ConfigureAwait(false);
        var client = new HostBridgeClient(process, options);
        try
        {
            var pong = await client.PingAsync(options.StartupTimeout, cancellationToken).ConfigureAwait(false);
            if (!pong)
            {
                throw new SidecarException(
                    SidecarErrorCode.ProtocolMismatch,
                    SidecarSpec.HostBridgeName,
                    "host_bridge ping did not return pong=true",
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
                    SidecarSpec.HostBridgeName,
                    $"host_bridge ping startup timeout: {ex.Message}",
                    options.StderrLogPath,
                    ex);
            }

            if (ex.Code is SidecarErrorCode.ProcessExited or SidecarErrorCode.MalformedResponse)
            {
                throw new SidecarException(
                    SidecarErrorCode.HandshakeFailed,
                    SidecarSpec.HostBridgeName,
                    $"host_bridge ping handshake failed: {ex.Message}",
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

    public async Task<bool> PingAsync(CancellationToken cancellationToken = default) =>
        await PingAsync(_options.RequestTimeout, cancellationToken).ConfigureAwait(false);

    private async Task<bool> PingAsync(TimeSpan timeout, CancellationToken cancellationToken)
    {
        var result = await SendAsync("ping", WireJson.EmptyObject, timeout, cancellationToken).ConfigureAwait(false);
        return result.TryGetProperty("pong", out var pong) && pong.ValueKind == JsonValueKind.True;
    }

    public async Task<IssuedRef> IssueAsync(string resourceId, string revisionFingerprint, CancellationToken cancellationToken = default)
    {
        var result = await SendAsync(
                "issue",
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("resource_id", resourceId);
                    writer.WriteString("revision_fingerprint", revisionFingerprint);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return new IssuedRef(ReadString(result, "id") ?? string.Empty, ReadLong(result, "size"));
    }

    public async Task<BridgeGrant> ResolveAsync(string grantId, CancellationToken cancellationToken = default)
    {
        var result = await SendAsync(
                "resolve",
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("id", grantId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return new BridgeGrant(
            ReadString(result, "scope_class") ?? string.Empty,
            ReadString(result, "resource_id") ?? string.Empty,
            ReadString(result, "revision_fingerprint") ?? string.Empty,
            ReadString(result, "rel_path") ?? string.Empty,
            ReadLong(result, "size"),
            ReadString(result, "sha256") ?? string.Empty,
            ReadLong(result, "volume_serial"),
            ReadLong(result, "file_index"));
    }

    public async Task RevokeAsync(string grantId, CancellationToken cancellationToken = default)
    {
        var result = await SendAsync(
                "revoke",
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("id", grantId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        if (!result.TryGetProperty("revoked", out var revoked) || revoked.ValueKind != JsonValueKind.True)
        {
            throw new BridgeException("REF_MALFORMED", "revoke did not return revoked=true");
        }
    }

    public async Task<long> RevokeResourceAsync(string resourceId, CancellationToken cancellationToken = default)
    {
        var result = await SendAsync(
                "revoke_resource",
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("resource_id", resourceId);
                    writer.WriteEndObject();
                },
                _options.RequestTimeout,
                cancellationToken)
            .ConfigureAwait(false);
        return ReadLong(result, "revoked_count");
    }

    public async Task ShutdownAsync(CancellationToken cancellationToken = default)
    {
        if (_disposed)
        {
            return;
        }

        try
        {
            await SendAsync("shutdown", WireJson.EmptyObject, TimeSpan.FromSeconds(5), cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is SidecarException or BridgeException or OperationCanceledException)
        {
            // best effort; dispose kills the bridge if it hangs
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

    /// <summary>Raw wire hook (evidence/negative): sends a line verbatim and parses the reply.</summary>
    public async Task<JsonElement> SendRawAsync(string rawJsonLine, CancellationToken cancellationToken = default)
    {
        var frame = await _process.ExchangeAsync(rawJsonLine, escapeNonAscii: false, _options.RequestTimeout, cancellationToken)
            .ConfigureAwait(false);
        return ParseResponse("raw", frame.ResponseLine);
    }

    private async Task<JsonElement> SendAsync(
        string method,
        Action<Utf8JsonWriter> paramsWriter,
        TimeSpan timeout,
        CancellationToken cancellationToken)
    {
        var requestId = NextRequestId();
        var line = WireJson.Write(writer =>
        {
            writer.WriteStartObject();
            writer.WriteNumber("id", requestId);
            writer.WriteString("method", method);
            writer.WritePropertyName("params");
            paramsWriter(writer);
            writer.WriteEndObject();
        });

        var frame = await _process.ExchangeAsync(line, escapeNonAscii: true, timeout, cancellationToken).ConfigureAwait(false);
        return ParseResponse(method, frame.ResponseLine);
    }

    private int NextRequestId() => Interlocked.Increment(ref _requestCounter);

    private static JsonElement ParseResponse(string method, string line)
    {
        JsonDocument document;
        try
        {
            document = JsonDocument.Parse(line);
        }
        catch (JsonException ex)
        {
            throw new SidecarException(SidecarErrorCode.MalformedResponse, SidecarSpec.HostBridgeName, $"{method}: invalid JSON", null, ex);
        }

        using (document)
        {
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
            {
                throw new SidecarException(SidecarErrorCode.MalformedResponse, SidecarSpec.HostBridgeName, $"{method}: response root is not an object");
            }

            if (root.TryGetProperty("error", out var error) && error.ValueKind == JsonValueKind.Object)
            {
                var code = ReadString(error, "code") ?? "REF_MALFORMED";
                throw new BridgeException(code, $"{method} failed");
            }

            if (root.TryGetProperty("result", out var result))
            {
                return result.Clone();
            }

            throw new BridgeException("REF_MALFORMED", $"{method}: response has neither result nor error");
        }
    }

    private static string? ReadString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static long ReadLong(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out var parsed)
            ? parsed
            : 0;
}
