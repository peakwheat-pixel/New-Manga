using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Sources;

/// <summary>One Host-known source to mint a Run-scoped read grant for
/// (FEA-11-RUN-GRANT-1 / C-16 v1.3 §2.4). The absolute path is Host-only and
/// never crosses the wire.</summary>
public sealed record RunSourceScope(
    string RegistryId,
    int Generation,
    string Path,
    string Kind,
    string SourceId,
    string Version)
{
    public override string ToString() => "RunSourceScope(" + SourceId + ")";
}

/// <summary>Host authority for source-read issuance, capability gating and revoke ACK.</summary>
public sealed class SourceReadCoordinator(
    CoreServiceClient core,
    SourceAccessRegistry registry,
    Func<bool> enabled,
    Func<double>? clock = null)
{
    /// <summary>C-16 v1.3 §0: the Run pre-dispatch authorization capability.</summary>
    public const string RunAuthorizationCapability = "source.read.run/1";

    /// <summary>Frozen §2.4 request bound: 1..64 grant ids per authorization.</summary>
    public const int MaxRunGrants = 64;

    /// <summary>R-8/L-G7: the ledger never tracks more than this many payloads.</summary>
    public const int MaxTrackedPayloads = 256;

    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly Dictionary<string, List<string>> _grants = new();
    //: C-16 v1.1 fresh-grant protocol: issued payloads are kept only in memory so
    //: a resolve-time Secret-G can clone the exact four-dimension scope without
    //: ever querying page bindings (the Host has no DB access).
    private readonly Dictionary<string, JsonObject> _payloads = new();
    private readonly Dictionary<string, (string RegistryId, int Generation, string GrantId)> _secretGrants = new();
    //: FEA-11-RUN-GRANT-1 (R-8/L-G7): the bounded ledger. ``_expiries`` drives
    //: the expiry/terminal prune; ``_boundRunGrants`` marks Run grants whose
    //: binding was acknowledged (their payloads stop being Secret-G templates).
    private readonly Dictionary<string, double> _expiries = new();
    private readonly HashSet<string> _boundRunGrants = new();
    private readonly object _ledger = new();
    private readonly Func<double> _clock = clock
        ?? (() => DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0);
    private bool? _runCapability;
    public SourceAccessRegistry Registry { get; } = registry;
    public bool ReferencedImportEnabled => enabled();

    /// <summary>R-8 probe: how many grant payloads the ledger currently keeps.</summary>
    public int TrackedPayloadCount
    {
        get { lock (_ledger) return _payloads.Count; }
    }

    /// <summary>R-8 probe: how many id-only grants the ledger currently keeps.</summary>
    public int TrackedGrantCount
    {
        get { lock (_ledger) return _grants.Values.Sum(list => list.Count); }
    }

    /// <summary>Live import-time grant ids (templates for fresh Secret-G clones).</summary>
    public IReadOnlyList<string> IssuedGrantIds
    {
        get { lock (_ledger) return _payloads.Keys.ToArray(); }
    }

    /// <summary>True when the running Core advertises source.resolve-secret/1.</summary>
    public async Task<bool> SupportsResolveSecretAsync(CancellationToken token)
    {
        var ping = await core.PingAsync(token).ConfigureAwait(false);
        return ping.Capabilities.Contains("source.resolve-secret/1");
    }

    /// <summary>
    /// FEA-11-RUN-GRANT-1 (C-16 v1.3 §0): the Run pre-dispatch authorization
    /// capability. Probed with ``core.ping`` only (never by dispatching the
    /// command); the verdict is cached because a running Core never changes it.
    /// </summary>
    public async Task<bool> SupportsRunAuthorizationAsync(CancellationToken token)
    {
        if (_runCapability is { } cached) return cached;
        var ping = await core.PingAsync(token).ConfigureAwait(false);
        var supported = ping.Capabilities.Contains(RunAuthorizationCapability);
        _runCapability = supported;
        return supported;
    }

    private async Task RequireCapability(CancellationToken token)
    {
        var ping = await core.PingAsync(token).ConfigureAwait(false);
        if (!ping.Capabilities.Contains("source.read/1")) throw new SourceAccessException("CORE_CAPABILITY_MISSING");
    }

    /// <summary>
    /// FEA-11-RUN-GRANT-1 (C-16 v1.3 §2.4): mint one source-read grant per
    /// Host-known Run source, then let the Core bind them to the Run target
    /// page bindings (``AuthorizeSourceReadForRun``). A Core typed refusal
    /// propagates as <see cref="CoreOperationException"/> so the caller can
    /// return that exact code and NOT dispatch the Run command (R-5).
    /// Returns the Core-reported ``bound_pages``.
    /// </summary>
    public async Task<int> AuthorizeRunAsync(
        IReadOnlyList<RunSourceScope> sources,
        string command,
        JsonElement scope,
        CancellationToken cancellationToken = default)
    {
        await _gate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            await RequireCapability(cancellationToken).ConfigureAwait(false);
            if (!await SupportsRunAuthorizationAsync(cancellationToken).ConfigureAwait(false))
                throw new SourceAccessException("CORE_CAPABILITY_MISSING");
            if (sources.Count == 0) throw new SourceAccessException("INVALID_REQUEST");
            if (sources.Count > MaxRunGrants) throw new SourceAccessException("SOURCE_BUDGET_EXCEEDED");
            var grantIds = new List<string>(sources.Count);
            foreach (var source in sources)
            {
                var rendition = RenditionFor(source.Kind);
                grantIds.Add(await IssueLockedAsync(
                    source.RegistryId, source.Generation, source.Path, source.Kind,
                    source.SourceId, source.Version, rendition,
                    cancellationToken: cancellationToken).ConfigureAwait(false));
            }
            var response = await core.SendHostControlAsync("AuthorizeSourceReadForRun", writer =>
            {
                writer.WritePropertyName("grant_ids");
                writer.WriteStartArray();
                foreach (var grantId in grantIds) writer.WriteStringValue(grantId);
                writer.WriteEndArray();
                writer.WriteString("command", command);
                writer.WritePropertyName("scope");
                scope.WriteTo(writer);
            }, cancellationToken).ConfigureAwait(false);
            if (response.Result is not { ValueKind: JsonValueKind.Object } result
                || !result.TryGetProperty("bound_pages", out var bound)
                || bound.ValueKind != JsonValueKind.Number
                || !bound.TryGetInt32(out var boundPages))
            {
                throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
            }
            lock (_ledger)
            {
                foreach (var grantId in grantIds) _boundRunGrants.Add(grantId);
            }
            PruneExpired();
            return boundPages;
        }
        finally { _gate.Release(); }
    }

    /// <summary>
    /// R-8/L-G7: record one tracked grant id/expiry. Every issuance path calls
    /// it; it also enforces the bounded ledger. Exposed as the accounting
    /// contract (the unit tests pin the upper bound and the expiry prune).
    /// </summary>
    public void Track(string grantId, string registryId, double expiresAt)
    {
        if (string.IsNullOrWhiteSpace(grantId) || string.IsNullOrWhiteSpace(registryId)) return;
        lock (_ledger)
        {
            _expiries[grantId] = expiresAt;
            if (!_grants.TryGetValue(registryId, out var list)) _grants[registryId] = list = [];
            if (!list.Contains(grantId, StringComparer.Ordinal)) list.Add(grantId);
        }
        PruneExpired();
    }

    /// <summary>
    /// R-8/L-G7: drop expired payloads/grants and enforce the hard upper bound.
    /// Called after every issuance/authorization so the ledger can never grow
    /// with the number of Runs. Safe to call from tests (own lock only).
    /// </summary>
    public int PruneExpired()
    {
        var now = _clock();
        lock (_ledger)
        {
            var expired = _expiries
                .Where(pair => pair.Value <= now)
                .Select(pair => pair.Key)
                .ToArray();
            foreach (var grantId in expired) ForgetLocked(grantId);
            if (_expiries.Count > MaxTrackedPayloads)
            {
                var oldest = _expiries
                    .OrderBy(pair => pair.Value)
                    .Select(pair => pair.Key)
                    .Take(_expiries.Count - MaxTrackedPayloads)
                    .ToArray();
                foreach (var grantId in oldest) ForgetLocked(grantId);
            }
            foreach (var registryId in _grants
                         .Where(pair => pair.Value.Count == 0)
                         .Select(pair => pair.Key)
                         .ToArray())
            {
                _grants.Remove(registryId);
            }
            return expired.Length;
        }
    }

    private void ForgetLocked(string grantId)
    {
        _payloads.Remove(grantId);
        _expiries.Remove(grantId);
        _secretGrants.Remove(grantId);
        _boundRunGrants.Remove(grantId);
        foreach (var list in _grants.Values) list.Remove(grantId);
    }

    public async Task<string> IssueAsync(string registryId, int generation, string sourcePath, string sourceKind,
        string sourceId, string version, JsonElement rendition, long maxBytes = 268435456,
        long maxDecodeBytes = 268435456, int maxEntries = 10000,
        string? secretToken = null, string? secretPath = null, double? secretExpiresAt = null,
        CancellationToken cancellationToken = default)
    {
        await _gate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            await RequireCapability(cancellationToken).ConfigureAwait(false);
            return await IssueLockedAsync(
                registryId, generation, sourcePath, sourceKind, sourceId, version,
                rendition, maxBytes, maxDecodeBytes, maxEntries,
                secretToken, secretPath, secretExpiresAt, cancellationToken)
                .ConfigureAwait(false);
        }
        finally { _gate.Release(); }
    }

    /// <summary>Issuance body: the caller owns ``_gate`` and the capability probe.</summary>
    private async Task<string> IssueLockedAsync(string registryId, int generation, string sourcePath, string sourceKind,
        string sourceId, string version, JsonElement rendition, long maxBytes = 268435456,
        long maxDecodeBytes = 268435456, int maxEntries = 10000,
        string? secretToken = null, string? secretPath = null, double? secretExpiresAt = null,
        CancellationToken cancellationToken = default)
    {
            var session = core.HostSession ?? throw new SourceAccessException("SOURCE_ACCESS_DENIED");
            if (sourceKind is not ("image" or "folder" or "zip" or "cbz" or "pdf")
                || maxBytes <= 0 || maxDecodeBytes <= 0 || maxEntries <= 0 || maxEntries > 10000)
                throw new SourceAccessException("INVALID_REQUEST");
            var path = SourceSecurity.Normalize(sourcePath);
            Registry.Authorize(registryId, generation, [path]);
            var paths = sourceKind == "folder" ? EnumerateFolder(path, maxEntries).OrderBy(NaturalKey, StringComparer.Ordinal).ThenBy(p => p, StringComparer.Ordinal).ToArray() : new[] { path };
            if (paths.Length == 0 || paths.Length > maxEntries) throw new SourceAccessException("SOURCE_BUDGET_EXCEEDED");
            Registry.Authorize(registryId, generation, paths);
            var entries = new JsonArray();
            var ordinal = 0;
            foreach (var member in paths)
            {
                SourceSecurity.RejectReparseAncestors(member);
                using var stream = new FileStream(member, FileMode.Open, FileAccess.Read, FileShare.Read);
                var before = SourceSecurity.Identity(stream.SafeFileHandle);
                if (before.Size > maxBytes) throw new SourceAccessException("SOURCE_BUDGET_EXCEEDED");
                var digest = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
                if (SourceSecurity.Identity(stream.SafeFileHandle) != before) throw new SourceAccessException("FILE_IDENTITY_CHANGED");
                entries.Add(new JsonObject
                {
                    ["entry_key"] = "entry-" + ordinal, ["entry_id"] = null,
                    ["locator"] = sourceKind == "folder" ? Path.GetRelativePath(path, member).Replace('\\', '/') : Path.GetFileName(member),
                    ["ordinal"] = ordinal++, ["path"] = member,
                    ["facts"] = new JsonObject { ["volume_serial"] = before.Volume, ["file_id"] = before.Id,
                        ["size"] = before.Size, ["sha256"] = digest }
                });
            }
            // Re-check root identities/generation and durable last-use after collection.
            Registry.Authorize(registryId, generation, paths);
            var id = "source-" + Guid.NewGuid().ToString("N");
            var expiry = _clock() + 300;
            var payload = new JsonObject
            {
                ["grant_id"] = id, ["session_id"] = session.HostSessionId, ["operation"] = "source-read",
                ["scope_class"] = "user-source", ["registry_id"] = registryId, ["generation"] = generation,
                ["expires_at"] = expiry,
                ["budget"] = new JsonObject { ["max_bytes"] = maxBytes, ["max_decode_bytes"] = maxDecodeBytes, ["max_entries"] = maxEntries },
                ["scope"] = new JsonObject { ["source_id"] = sourceId, ["version"] = version,
                    ["rendition"] = JsonNode.Parse(rendition.GetRawText()), ["entries"] = entries }
            };
            if (secretToken is not null && secretPath is not null)
            {
                if (secretExpiresAt is null || secretExpiresAt.Value <= expiry)
                {
                    payload["secret_ref"] = new JsonObject
                    {
                        ["token"] = secretToken, ["path"] = secretPath,
                        ["expires_at"] = secretExpiresAt ?? expiry,
                    };
                }
                else
                {
                    throw new SourceAccessException("INVALID_REQUEST");
                }
            }
            var signed = payload.DeepClone().AsObject();
            signed["expires_at"] = expiry.ToString("F6", CultureInfo.InvariantCulture);
            var signature = HMACSHA256.HashData(session.SigningKey, Encoding.UTF8.GetBytes(Canonical(signed)));
            payload["signing_key"] = Base64Url(session.SigningKey);
            payload["signature"] = Base64Url(signature);
            await RegisterPayloadAsync(payload, cancellationToken).ConfigureAwait(false);
            lock (_ledger) { _payloads[id] = payload.DeepClone().AsObject(); }
            Track(id, registryId, expiry);
            return id;
    }

    /// <summary>
    /// C-16 v1.1 §3.1: revoke the previous Secret-G, then clone every live
    /// import grant's scope with a fresh grant id/expiry plus <c>secret_ref</c>.
    /// The caller creates the DPAPI token file first; capability must be checked
    /// by the caller before creating it. Returns the registered secret grant ids.
    /// </summary>
    public async Task<IReadOnlyList<string>> IssueSecretGrantsAsync(
        IReadOnlyCollection<string> templateGrantIds, string token, string secretPath,
        double expiresAt, CancellationToken cancellationToken = default)
    {
        if (templateGrantIds.Count == 0) return Array.Empty<string>();
        if (!await SupportsResolveSecretAsync(cancellationToken).ConfigureAwait(false))
            throw new SourceAccessException("CORE_CAPABILITY_MISSING");
        await _gate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            var session = core.HostSession ?? throw new SourceAccessException("SOURCE_ACCESS_DENIED");
            await RevokeSecretGrantsLockedAsync(cancellationToken).ConfigureAwait(false);
            var issued = new List<string>();
            foreach (var templateId in templateGrantIds)
            {
                JsonObject template;
                lock (_ledger)
                {
                    if (!_payloads.TryGetValue(templateId, out var found)) continue;
                    template = found.DeepClone().AsObject();
                }
                var grantId = "source-" + Guid.NewGuid().ToString("N");
                template["grant_id"] = grantId;
                template["session_id"] = session.HostSessionId;
                template["expires_at"] = expiresAt;
                template.Remove("signing_key");
                template.Remove("signature");
                template["secret_ref"] = new JsonObject
                {
                    ["token"] = token, ["path"] = secretPath, ["expires_at"] = expiresAt,
                };
                var signed = template.DeepClone().AsObject();
                signed["expires_at"] = expiresAt.ToString("F6", CultureInfo.InvariantCulture);
                var signature = HMACSHA256.HashData(session.SigningKey, Encoding.UTF8.GetBytes(Canonical(signed)));
                template["signing_key"] = Base64Url(session.SigningKey);
                template["signature"] = Base64Url(signature);
                await RegisterPayloadAsync(template, cancellationToken).ConfigureAwait(false);
                issued.Add(grantId);
                var registryId = template["registry_id"]!.GetValue<string>();
                var generation = template["generation"]!.GetValue<int>();
                lock (_ledger) _secretGrants[grantId] = (registryId, generation, grantId);
                Track(grantId, registryId, expiresAt);
            }
            PruneExpired();
            return issued;
        }
        catch
        {
            try { await RevokeSecretGrantsLockedAsync(CancellationToken.None).ConfigureAwait(false); }
            catch { /* best effort cleanup */ }
            throw;
        }
        finally { _gate.Release(); }
    }

    /// <summary>Revoke every currently tracked Secret-G (resolve teardown).</summary>
    public async Task RevokeSecretGrantsAsync(CancellationToken cancellationToken = default)
    {
        await _gate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try { await RevokeSecretGrantsLockedAsync(cancellationToken).ConfigureAwait(false); }
        finally { _gate.Release(); }
    }

    private async Task RevokeSecretGrantsLockedAsync(CancellationToken token)
    {
        KeyValuePair<string, (string RegistryId, int Generation, string GrantId)>[] snapshot;
        lock (_ledger)
        {
            if (_secretGrants.Count == 0) return;
            snapshot = _secretGrants.ToArray();
            foreach (var item in snapshot) ForgetLocked(item.Key);
        }
        foreach (var group in snapshot.GroupBy(item => (item.Value.RegistryId, item.Value.Generation)))
        {
            var ids = group.Select(item => item.Key).ToArray();
            var ack = await core.SendHostControlAsync("RevokeSourceReadGrant", writer =>
            {
                writer.WriteString("registry_id", group.Key.RegistryId);
                writer.WriteNumber("generation", group.Key.Generation);
                writer.WritePropertyName("grant_ids");
                JsonSerializer.Serialize(writer, ids);
            }, token).ConfigureAwait(false);
            if (ack.Result is null) throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        }
    }

    private async Task RegisterPayloadAsync(JsonObject payload, CancellationToken token)
    {
        using var document = JsonDocument.Parse(payload.ToJsonString());
        var result = await core.SendHostControlAsync("RegisterSourceReadGrant", writer =>
        {
            foreach (var property in document.RootElement.EnumerateObject()) property.WriteTo(writer);
        }, token).ConfigureAwait(false);
        if (result.Result is not { } ack || !ack.TryGetProperty("registered", out var registered)
            || registered.ValueKind != JsonValueKind.True)
            throw new SourceAccessException("SOURCE_ACCESS_DENIED");
    }

    public async Task<JsonElement> InvokeAsync(string name, JsonElement args, CancellationToken token)
    {
        await _gate.WaitAsync(token).ConfigureAwait(false);
        try
        {
            await RequireCapability(token).ConfigureAwait(false);
            object result;
            switch (name)
            {
                case "source_register_root":
                    var entry = Registry.Register(args.GetProperty("locator").GetString()!, args.GetProperty("roots").EnumerateArray().Select(v => v.GetString()!).ToArray());
                    result = new { registry_id = entry.RegistryId, generation = entry.Generation }; break;
                case "source_list_roots":
                    result = new { entries = Registry.List().Select(e => new { registry_id = e.RegistryId, locator = e.Locator,
                        roots = e.Roots.Select(r => r.Root), generation = e.Generation, created_at = e.CreatedAt,
                        last_used_at = e.LastUsedAt, revoked = e.RevokedAt is not null }) }; break;
                case "source_reset_registry":
                    result = new { reset = true, quarantine_path = Registry.Reset(args.GetProperty("confirm").GetBoolean()) }; break;
                case "source_revoke_root":
                    string[] revokedGrantIds;
                    var revoked = Registry.Revoke(args.GetProperty("registry_id").GetString()!);
                    revokedGrantIds = (_grants.GetValueOrDefault(revoked.RegistryId) ?? []).ToArray();
                    var ack = await core.SendHostControlAsync("RevokeSourceReadGrant", writer =>
                    {
                        writer.WriteString("registry_id", revoked.RegistryId); writer.WriteNumber("generation", revoked.Generation);
                        writer.WritePropertyName("grant_ids"); JsonSerializer.Serialize(writer, revokedGrantIds);
                    }, token).ConfigureAwait(false);
                    if (ack.Result is not { } value || !value.TryGetProperty("revoked", out var yes) || yes.ValueKind != JsonValueKind.True)
                        throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
                    // R-8/L-G7: a revoked root drops its ledger entries immediately.
                    lock (_ledger)
                    {
                        foreach (var grantId in revokedGrantIds) ForgetLocked(grantId);
                    }
                    PruneExpired();
                    result = new { revoked = true, generation = revoked.Generation }; break;
                default:
                    if (name is "plan_import_references" or "start_import_references" && !ReferencedImportEnabled)
                        throw new SourceAccessException("SOURCE_ACCESS_DENIED");
                    var command = name switch { "plan_import_references" => "PlanImportReferences", "start_import_references" => "StartImportReferences",
                        "get_import_receipt" => "GetImportReceipt", "cancel_import" => "CancelImport", _ => throw new SourceAccessException("INVALID_REQUEST") };
                    var response = await core.SendAsync(command, 3, args.WriteTo, TimeSpan.FromSeconds(30), token).ConfigureAwait(false);
                    return response.Result ?? throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
            }
            return JsonSerializer.SerializeToElement(result);
        }
        catch (Exception error) when (error is JsonException or KeyNotFoundException or InvalidOperationException or ArgumentException)
        { throw new SourceAccessException("INVALID_REQUEST"); }
        finally { _gate.Release(); }
    }

    private static IEnumerable<string> EnumerateFolder(string root, int maxEntries)
    {
        var pending = new Stack<string>(); pending.Push(root); var count = 0;
        while (pending.TryPop(out var directory))
        foreach (var path in Directory.EnumerateFileSystemEntries(directory).Order(StringComparer.Ordinal))
        {
            SourceSecurity.RejectReparseAncestors(path);
            var flags = File.GetAttributes(path);
            if ((flags & (FileAttributes.Hidden | FileAttributes.System)) != 0) continue;
            if ((flags & FileAttributes.Directory) != 0) pending.Push(path);
            else
            {
                if (++count > maxEntries) throw new SourceAccessException("SOURCE_BUDGET_EXCEEDED");
                yield return path;
            }
        }
    }
    private static string NaturalKey(string path) => string.Concat(
        System.Text.RegularExpressions.Regex.Split(path, "([0-9]+)").Select((part, index) =>
            index % 2 == 1 ? "\u0001N" + System.Numerics.BigInteger.Parse(part, CultureInfo.InvariantCulture).ToString("D20", CultureInfo.InvariantCulture)
                : part.Length > 0 ? "\u0002S" + part.ToLowerInvariant() : string.Empty));

    private static string Base64Url(byte[] bytes) => Convert.ToBase64String(bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_');

    /// <summary>The frozen rendition dimension for a Run grant (the decoder is
    /// the source kind; scale/params are fixed — the Run authorization never
    /// compares the rendition, it only needs the frozen closed shape).</summary>
    private static JsonElement RenditionFor(string kind)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            writer.WriteStartObject();
            writer.WriteString("decoder", kind);
            writer.WriteNumber("scale", 1.0);
            writer.WriteString("params_digest", RunRenditionParamsDigest);
            writer.WriteEndObject();
        }
        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }

    /// <summary>Fixed params digest for Run-scoped grants (frozen shape, not a codec choice).</summary>
    private const string RunRenditionParamsDigest =
        "0000000000000000000000000000000000000000000000000000000000000000";

    private static string Canonical(JsonNode? node) => node switch
    {
        JsonObject obj => "{" + string.Join(",", obj.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => JsonSerializer.Serialize(p.Key) + ":" + Canonical(p.Value))) + "}",
        JsonArray array => "[" + string.Join(",", array.Select(Canonical)) + "]",
        null => "null",
        _ => node.ToJsonString(new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping })
    };
}
