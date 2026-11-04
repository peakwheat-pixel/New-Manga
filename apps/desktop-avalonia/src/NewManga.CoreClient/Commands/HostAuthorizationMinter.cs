using System.Globalization;
using System.Security.Cryptography;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Commands;

/// <summary>
/// FEA-11-HOST-AUTH-1 (C-17 §5.2): the Host mints the durable
/// <c>HostAuthorization</c> itself. operation_id and host_receipt_id are
/// Host-owned, request_digest and authorization_digest use canonical-json/1,
/// and the caller may only supply the registry authorizations it obtained.
/// </summary>
public static class HostAuthorizationMinter
{
    public sealed record Minted(
        string OperationId,
        string HostReceiptId,
        string RequestDigest,
        string AuthorizationDigest,
        IReadOnlyList<Dictionary<string, object?>> Authorizations,
        string AuthorizedAt,
        Dictionary<string, object?> Authorization);

    public static Minted Mint(
        string planId,
        string planDigest,
        string kind,
        IEnumerable<Dictionary<string, object?>> authorizations,
        DateTimeOffset? now = null)
    {
        var ordered = authorizations
            .Select(item => new Dictionary<string, object?>
            {
                ["registry_id"] = item["registry_id"],
                ["generation"] = item["generation"],
                ["identity_digest"] = item["identity_digest"],
            })
            .OrderBy(item => (string)item["registry_id"]!, StringComparer.Ordinal)
            .ToList();
        if (ordered.Count == 0)
        {
            throw new CoreOperationException(
                "INVALID_REQUEST", "validation", false,
                "apply request carries no registry authorizations", null);
        }

        var operationId = "op-" + Convert.ToHexString(
            RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
        var hostReceiptId = "hr-" + Convert.ToHexString(
            RandomNumberGenerator.GetBytes(16)).ToLowerInvariant();
        var requestDigest = CanonicalJson.Sha256Hex(new Dictionary<string, object?>
        {
            ["operation_id"] = operationId,
            ["plan_id"] = planId,
            ["plan_digest"] = planDigest,
            ["kind"] = kind,
        });
        var authorizationDigest = CanonicalJson.Sha256Hex(ordered);
        var authorizedAt = (now ?? DateTimeOffset.UtcNow).ToString(
            "yyyy-MM-dd'T'HH:mm:ss.fff'Z'", CultureInfo.InvariantCulture);
        var authorization = new Dictionary<string, object?>
        {
            ["operation_id"] = operationId,
            ["request_digest"] = requestDigest,
            ["authorization_digest"] = authorizationDigest,
            ["authorizations"] = ordered,
            ["host_receipt_id"] = hostReceiptId,
            ["authorized_at"] = authorizedAt,
        };
        return new Minted(
            operationId, hostReceiptId, requestDigest, authorizationDigest,
            ordered, authorizedAt, authorization);
    }
}
