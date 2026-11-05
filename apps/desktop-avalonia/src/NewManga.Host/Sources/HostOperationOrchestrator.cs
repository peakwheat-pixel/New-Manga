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

    /// <summary>C-17 §3.2 line 159: a typed Core business rejection means the
    /// Core wrote nothing, so the Host journal must record failed + code. Only
    /// transport/ambiguity codes (CORE_*) leave the journal host-authorized for
    /// receipt re-read / recovery.</summary>
    /// <summary>C-17 §3.2 line 163: retry a failed (never committed) operation
    /// with the SAME operation/request digest but a FRESH HostAuthorization —
    /// the registry is re-read/authorized and the new authorization is recorded
    /// durably before the dispatch.</summary>
    public async Task<(string OperationId, JsonElement Result)> RetryAsync(
        string hostCommandName,
        string operationId,
        JsonElement payload,
        Func<JsonElement, CancellationToken, Task<CoreResponse>> call,
        CancellationToken token)
    {
        await _capability(hostCommandName, token).ConfigureAwait(false);
        var entry = _operations.Get(operationId)
            ?? throw new CoreOperationException(
                "SOURCE_OPERATION_NOT_FOUND", "conflict", false, "unknown operation", null);
        var kind = hostCommandName switch
        {
            "source_relink" => "relink",
            "source_repoint" => "repoint",
            _ => "resync",
        };
        // C-17 §3.2:163 — retry keys off the same kind/digest; a mismatched
        // command or a missing durable authorization must fail before any
        // registry authorization happens.
        if (!string.Equals(entry.Kind, kind, StringComparison.Ordinal))
        {
            throw new CoreOperationException(
                "SOURCE_SYNC_STATE_CONFLICT", "conflict", false,
                "retry kind does not match the journaled operation", null);
        }
        if (entry.State != "failed" || entry.CommitDigest is not null || entry.Retryable == false)
        {
            throw new SourceAccessException("SOURCE_SYNC_STATE_CONFLICT");
        }
        var registryAuthorizations = new List<Dictionary<string, object?>>();
        if (payload.ValueKind == JsonValueKind.Object
            && payload.TryGetProperty("authorization", out var incoming)
            && incoming.ValueKind == JsonValueKind.Object
            && incoming.TryGetProperty("authorizations", out var items)
            && items.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in items.EnumerateArray())
            {
                var registryId = StringField(item, "registry_id");
                var identityDigest = StringField(item, "identity_digest");
                var generation = item.ValueKind == JsonValueKind.Object
                    && item.TryGetProperty("generation", out var generationValue)
                    && generationValue.ValueKind == JsonValueKind.Number
                    && generationValue.TryGetInt32(out var parsedGeneration)
                        ? parsedGeneration : 0;
                if (string.IsNullOrWhiteSpace(registryId)
                    || string.IsNullOrWhiteSpace(identityDigest) || generation < 1)
                {
                    throw new CoreOperationException(
                        "INVALID_REQUEST", "validation", false,
                        "retry request carries a malformed authorizations entry", null);
                }
                registryAuthorizations.Add(new Dictionary<string, object?>
                {
                    ["registry_id"] = registryId,
                    ["generation"] = generation,
                    ["identity_digest"] = identityDigest,
                });
            }
        }
        var minted = HostAuthorizationMinter.Mint(
            entry.PlanId, entry.PlanDigest, kind, registryAuthorizations,
            operationId: entry.OperationId);
        if (!string.Equals(minted.RequestDigest, entry.RequestDigest, StringComparison.Ordinal))
        {
            throw new CoreOperationException(
                "SOURCE_SYNC_STATE_CONFLICT", "conflict", false,
                "retried operation must keep its request digest", null);
        }
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
        var authorizationJson = CanonicalJson.Text(minted.Authorization);
        _operations.RetryFailed(
            entry.OperationId, authorizationJson, minted.HostReceiptId);

        var injected = new Dictionary<string, object?>
        {
            ["operation_id"] = entry.OperationId,
            ["plan_id"] = entry.PlanId,
            ["plan_digest"] = entry.PlanDigest,
            ["grant_ids"] = (entry.GrantIds ?? string.Empty)
                .Split(',', StringSplitOptions.RemoveEmptyEntries),
            ["authorization"] = minted.Authorization,
        };
        var finalPayload = JsonSerializer.SerializeToElement(injected);
        CoreResponse response;
        try
        {
            response = await call(finalPayload, token).ConfigureAwait(false);
        }
        catch (CoreOperationException error) when (IsPreCommitRejection(error.Code))
        {
            _operations.MarkFailed(
                entry.OperationId, error.Code, retryable: error.Retryable ?? true);
            throw;
        }
        catch (Exception)
        {
            throw new CoreOperationException(
                "CORE_UNAVAILABLE", "unavailable", true,
                "source operation " + entry.OperationId
                + " is host-authorized; recover or retry it", entry.OperationId);
        }
        var result = response.Result ?? default;
        var row = await _lookup(entry.OperationId, token).ConfigureAwait(false);
        var commitDigest = row.ValueKind == JsonValueKind.Object
            && row.TryGetProperty("commit_digest", out var digestValue)
            && digestValue.ValueKind == JsonValueKind.String
                ? digestValue.GetString()!
                : throw new CoreOperationException(
                    "SOURCE_OPERATION_NOT_FOUND", "conflict", false,
                    "operation receipt is unavailable", null);
        _operations.MarkCommitted(
            entry.OperationId, commitDigest,
            row.ValueKind == JsonValueKind.Object ? row.GetRawText() : null);
        return (entry.OperationId, result);
    }

    private static string? StringField(JsonElement element, string key) =>
        element.ValueKind == JsonValueKind.Object
        && element.TryGetProperty(key, out var value)
        && value.ValueKind == JsonValueKind.String
            ? value.GetString() : null;

    private static bool IsPreCommitRejection(string code) => code is
        not ("CORE_UNAVAILABLE" or "CORE_TIMEOUT" or "CORE_PROTOCOL_ERROR"
             or "CORE_SESSION_MISMATCH" or "CORE_SHUTDOWN" or "CORE_BUSY"
             or "OPERATION_CANCELLED" or "INVALID_RESPONSE");

    public async Task<(string OperationId, JsonElement Result)> ApplyAsync(
        string hostCommandName,
        JsonElement payload,
        Func<JsonElement, CancellationToken, Task<CoreResponse>> call,
        CancellationToken token)
    {
        await _capability(hostCommandName, token).ConfigureAwait(false);
        var planId = StringField(payload, "plan_id");
        var planDigest = StringField(payload, "plan_digest");
        if (string.IsNullOrWhiteSpace(planId) || planDigest is null)
        {
            throw new CoreOperationException(
                "INVALID_REQUEST", "validation", false,
                "apply request lacks a plan id or plan digest", null);
        }
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
                if (grant.ValueKind != JsonValueKind.String
                    || string.IsNullOrWhiteSpace(grant.GetString())
                    || grant.GetString()!.Contains(','))
                {
                    throw new CoreOperationException(
                        "INVALID_REQUEST", "validation", false,
                        "grant_ids must be non-empty strings without commas", null);
                }
                grantIds.Add(grant.GetString()!);
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
                var generation = 0;
                if (item.ValueKind == JsonValueKind.Object
                    && item.TryGetProperty("generation", out var generationValue)
                    && generationValue.ValueKind == JsonValueKind.Number
                    && generationValue.TryGetInt32(out var parsedGeneration))
                {
                    generation = parsedGeneration;
                }
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

        CoreResponse response;
        try
        {
            response = await call(finalPayload, token).ConfigureAwait(false);
        }
        catch (CoreOperationException error) when (IsPreCommitRejection(error.Code))
        {
            // C-17 §3.2: a typed pre-commit rejection is durable on the Host as
            // failed + error_code/retryable (the Core wrote nothing).
            _operations.MarkFailed(
                minted.OperationId, error.Code, retryable: error.Retryable ?? true);
            throw;
        }
        catch (Exception)
        {
            // Ambiguous (transport/cancel): keep host-authorized so recovery can
            // re-read the Core receipt; the operation id stays reachable via the
            // journal and the thrown exception message.
            throw new CoreOperationException(
                "CORE_UNAVAILABLE", "unavailable", true,
                "source operation " + minted.OperationId
                + " is host-authorized; recover or retry it", minted.OperationId);
        }
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
