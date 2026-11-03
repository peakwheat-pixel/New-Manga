using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Sources;

/// <summary>Host authority for source-read issuance, capability gating and revoke ACK.</summary>
public sealed class SourceReadCoordinator(CoreServiceClient core, SourceAccessRegistry registry, Func<bool> enabled)
{
    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly Dictionary<string, List<string>> _grants = new();
    public SourceAccessRegistry Registry { get; } = registry;
    public bool ReferencedImportEnabled => enabled();

    private async Task RequireCapability(CancellationToken token)
    {
        var ping = await core.PingAsync(token).ConfigureAwait(false);
        if (!ping.Capabilities.Contains("source.read/1")) throw new SourceAccessException("CORE_CAPABILITY_MISSING");
    }

    public async Task<string> IssueAsync(string registryId, int generation, string sourcePath, string sourceKind,
        string sourceId, string version, JsonElement rendition, long maxBytes = 268435456,
        long maxDecodeBytes = 268435456, int maxEntries = 10000, CancellationToken cancellationToken = default)
    {
        await _gate.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            await RequireCapability(cancellationToken).ConfigureAwait(false);
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
            var expiry = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0 + 300;
            var payload = new JsonObject
            {
                ["grant_id"] = id, ["session_id"] = session.HostSessionId, ["operation"] = "source-read",
                ["scope_class"] = "user-source", ["registry_id"] = registryId, ["generation"] = generation,
                ["expires_at"] = expiry,
                ["budget"] = new JsonObject { ["max_bytes"] = maxBytes, ["max_decode_bytes"] = maxDecodeBytes, ["max_entries"] = maxEntries },
                ["scope"] = new JsonObject { ["source_id"] = sourceId, ["version"] = version,
                    ["rendition"] = JsonNode.Parse(rendition.GetRawText()), ["entries"] = entries }
            };
            var signed = payload.DeepClone().AsObject();
            signed["expires_at"] = expiry.ToString("F6", CultureInfo.InvariantCulture);
            var signature = HMACSHA256.HashData(session.SigningKey, Encoding.UTF8.GetBytes(Canonical(signed)));
            payload["signing_key"] = Base64Url(session.SigningKey);
            payload["signature"] = Base64Url(signature);
            using var document = JsonDocument.Parse(payload.ToJsonString());
            var result = await core.SendHostControlAsync("RegisterSourceReadGrant", writer =>
            {
                foreach (var property in document.RootElement.EnumerateObject()) property.WriteTo(writer);
            }, cancellationToken).ConfigureAwait(false);
            if (result.Result is not { } ack || !ack.TryGetProperty("registered", out var registered) || registered.ValueKind != JsonValueKind.True)
                throw new SourceAccessException("SOURCE_ACCESS_DENIED");
            if (!_grants.TryGetValue(registryId, out var list)) _grants[registryId] = list = [];
            list.Add(id);
            return id;
        }
        finally { _gate.Release(); }
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
                    var revoked = Registry.Revoke(args.GetProperty("registry_id").GetString()!);
                    var grantIds = _grants.GetValueOrDefault(revoked.RegistryId) ?? [];
                    var ack = await core.SendHostControlAsync("RevokeSourceReadGrant", writer =>
                    {
                        writer.WriteString("registry_id", revoked.RegistryId); writer.WriteNumber("generation", revoked.Generation);
                        writer.WritePropertyName("grant_ids"); JsonSerializer.Serialize(writer, grantIds);
                    }, token).ConfigureAwait(false);
                    if (ack.Result is not { } value || !value.TryGetProperty("revoked", out var yes) || yes.ValueKind != JsonValueKind.True)
                        throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
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
    private static string Canonical(JsonNode? node) => node switch
    {
        JsonObject obj => "{" + string.Join(",", obj.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => JsonSerializer.Serialize(p.Key) + ":" + Canonical(p.Value))) + "}",
        JsonArray array => "[" + string.Join(",", array.Select(Canonical)) + "]",
        null => "null",
        _ => node.ToJsonString(new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping })
    };
}
