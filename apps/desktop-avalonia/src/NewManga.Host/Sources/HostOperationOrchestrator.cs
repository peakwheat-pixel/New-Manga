using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;

namespace NewManga.Host.Sources;

/// <summary>
/// FEA-11-HOST-AUTH-1 (C-17 §3.2/§5.2): the Host-side operation orchestrator.
///
/// Order is normative: mint the HostAuthorization → Registry durable
/// authorization → journal Begin/Authorize → Core call → MarkCommitted. The
/// caller cannot inject operation_id/authorization; it only supplies the
/// frozen plan digest and the registry authorizations.
/// </summary>
public sealed class HostOperationOrchestrator
{
    private readonly SourceOperationCoordinator _operations;
    private readonly SourceAccessRegistry _registry;
    private readonly Func<string, CancellationToken, Task> _capability;
    private readonly Func<string, CancellationToken, Task<JsonElement>> _lookup;

    public HostOperationOrchestrator(
        SourceOperationCoordinator operations,
        SourceAccessRegistry registry,
        Func<string, CancellationToken, Task> capability,
        Func<string, CancellationToken, Task<JsonElement>> lookup)
    {
        _operations = operations;
        _registry = registry;
        _capability = capability;
        _lookup = lookup;
    }

    public async Task<(string OperationId, JsonElement Result)> ApplyAsync(
        string hostCommandName,
        JsonElement payload,
        Func<JsonElement, CancellationToken, Task<CoreResponse>> call,
        CancellationToken token)
    {
        await _capability(hostCommandName, token).ConfigureAwait(false);
        string? StringField(JsonElement element, string key) =>
            element.ValueKind == JsonValueKind.Object
            && element.TryGetProperty(key, out var value)
            && value.ValueKind == JsonValueKind.String
                ? value.GetString() : null;

        var planId = StringField(payload, "plan_id") ?? string.Empty;
        var planDigest = StringField(payload, "plan_digest") ?? new string('0', 64);
        var kind = hostCommandName switch
        {
            "source_relink" => "relink",
            "source_repoint" => "repoint",
            _ => "resync",
        };
        var grantIds = new List<string>();
        if (payload.ValueKind == JsonValueKind.Object
            && payload.TryGetProperty("grant_ids", out var grantArray)
            && grantArray.ValueKind == JsonValueKind.Array)
        {
            foreach (var grant in grantArray.EnumerateArray())
            {
                if (grant.ValueKind == JsonValueKind.String
                    && grant.GetString() is { Length: > 0 } grantId)
                {
                    grantIds.Add(grantId);
                }
            }
        }

        var registryAuthorizations = new List<Dictionary<string, object?>>();
        if (payload.ValueKind == JsonValueKind.Object
            && payload.TryGetProperty("authorization", out var incoming)
            && incoming.ValueKind == JsonValueKind.Object
            && incoming.TryGetProperty("authorizations", out var incomingAuthorizations)
            && incomingAuthorizations.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in incomingAuthorizations.EnumerateArray())
            {
                var registryId = StringField(item, "registry_id");
                var identityDigest = StringField(item, "identity_digest");
                var generation = item.ValueKind == JsonValueKind.Object
                    && item.TryGetProperty("generation", out var generationValue)
                    && generationValue.ValueKind == JsonValueKind.Number
                        ? generationValue.GetInt32() : 0;
                if (string.IsNullOrWhiteSpace(registryId)
                    || string.IsNullOrWhiteSpace(identityDigest) || generation < 1)
                {
                    throw new CoreOperationException(
                        "INVALID_REQUEST", "validation", false,
                        "apply request carries a malformed authorizations entry", null);
                }
                registryAuthorizations.Add(new Dictionary<string, object?>
                {
                    ["registry_id"] = registryId,
                    ["generation"] = generation,
                    ["identity_digest"] = identityDigest,
                });
            }
        }
        if (registryAuthorizations.Count == 0)
        {
            throw new CoreOperationException(
                "INVALID_REQUEST", "validation", false,
                "apply request carries no registry authorizations", null);
        }

        var minted = HostAuthorizationMinter.Mint(planId, planDigest, kind, registryAuthorizations);
        var authorizationJson = CanonicalJson.Text(minted.Authorization);

        var known = _registry.List().ToDictionary(item => item.RegistryId, item => item);
        foreach (var item in minted.Authorizations)
        {
            var registryId = (string)item["registry_id"]!;
            if (!known.TryGetValue(registryId, out var knownRegistry))
            {
                throw new CoreOperationException(
                    "SOURCE_REGISTRY_UNAVAILABLE", "protocol", false,
                    "authorization references an unknown source registry", null);
            }
            var roots = knownRegistry.Roots
                .Where(root => root.Readable)
                .Select(root => root.Root)
                .ToArray();
            if (roots.Length == 0)
            {
                throw new CoreOperationException(
                    "SOURCE_REGISTRY_UNAVAILABLE", "protocol", false,
                    "source registry has no readable root", null);
            }
            _registry.Authorize(registryId, (int)item["generation"]!, roots);
        }

        var entry = _operations.Begin(
            planId, planDigest, kind, minted.RequestDigest, minted.OperationId, grantIds);
        _operations.Authorize(entry.OperationId, authorizationJson, minted.HostReceiptId);

        var injected = new Dictionary<string, object?>();
        if (payload.ValueKind == JsonValueKind.Object)
        {
            foreach (var property in payload.EnumerateObject())
            {
                if (property.Name is "operation_id" or "authorization")
                {
                    continue;
                }
                injected[property.Name] = JsonSerializer.Deserialize<object?>(property.Value.GetRawText());
            }
        }
        injected["operation_id"] = minted.OperationId;
        injected["authorization"] = minted.Authorization;
        var finalPayload = JsonSerializer.SerializeToElement(injected);

        var response = await call(finalPayload, token).ConfigureAwait(false);
        var result = response.Result ?? default;
        var operationRow = await _lookup(minted.OperationId, token).ConfigureAwait(false);
        var commitDigest = operationRow.ValueKind == JsonValueKind.Object
            && operationRow.TryGetProperty("commit_digest", out var digestValue)
            && digestValue.ValueKind == JsonValueKind.String
                ? digestValue.GetString()!
                : throw new CoreOperationException(
                    "SOURCE_OPERATION_NOT_FOUND", "conflict", false,
                    "operation receipt is unavailable", null);
        _operations.MarkCommitted(
            entry.OperationId, commitDigest,
            operationRow.ValueKind == JsonValueKind.Object ? operationRow.GetRawText() : null);
        return (entry.OperationId, result);
    }
}
