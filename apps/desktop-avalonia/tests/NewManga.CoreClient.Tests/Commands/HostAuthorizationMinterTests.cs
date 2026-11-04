using NewManga.CoreClient.Commands;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// FEA-11-HOST-AUTH-1 (C-17 §5.2): the Host mints the durable
/// HostAuthorization — six fields, canonical digests, sorted authorizations.
/// </summary>
public sealed class HostAuthorizationMinterTests
{
    private const string A64 = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    private const string B64 = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

    [Fact]
    public void Mint_ProducesTheSixFieldAuthorizationWithCanonicalDigests()
    {
        var now = DateTimeOffset.Parse("2026-01-02T03:04:05.000Z");
        // Deliberately out of registry order: the minter must sort by registry_id.
        var minted = HostAuthorizationMinter.Mint(
            "pl-1", A64, "resync",
            new[]
            {
                new Dictionary<string, object?> { ["registry_id"] = "reg-b", ["generation"] = 2, ["identity_digest"] = B64 },
                new Dictionary<string, object?> { ["registry_id"] = "reg-a", ["generation"] = 1, ["identity_digest"] = A64 },
            },
            now);

        Assert.Matches("^op-[0-9a-f]{32}$", minted.OperationId);
        Assert.Matches("^hr-[0-9a-f]{32}$", minted.HostReceiptId);
        Assert.Equal("2026-01-02T03:04:05.000Z", minted.AuthorizedAt);
        Assert.Equal(new[] { "reg-a", "reg-b" },
            minted.Authorizations.Select(item => (string)item["registry_id"]!));
        Assert.Equal(
            CanonicalJson.Sha256Hex(new Dictionary<string, object?>
            {
                ["operation_id"] = minted.OperationId,
                ["plan_id"] = "pl-1",
                ["plan_digest"] = A64,
                ["kind"] = "resync",
            }),
            minted.RequestDigest);
        Assert.Equal(
            CanonicalJson.Sha256Hex(minted.Authorizations),
            minted.AuthorizationDigest);

        var authorization = minted.Authorization;
        Assert.Equal(minted.OperationId, authorization["operation_id"]);
        Assert.Equal(minted.RequestDigest, authorization["request_digest"]);
        Assert.Equal(minted.AuthorizationDigest, authorization["authorization_digest"]);
        Assert.Equal(minted.HostReceiptId, authorization["host_receipt_id"]);
        Assert.Equal(minted.AuthorizedAt, authorization["authorized_at"]);
        Assert.Equal(6, authorization.Count);
        Assert.Equal(minted.Authorizations, authorization["authorizations"]);
    }

    [Fact]
    public void Mint_RejectsAnEmptyAuthorizationSet()
    {
        var error = Assert.Throws<NewManga.CoreClient.Wire.CoreOperationException>(() =>
            HostAuthorizationMinter.Mint("pl-1", A64, "resync", Array.Empty<Dictionary<string, object?>>()));
        Assert.Equal("INVALID_REQUEST", error.Code);
    }

    [Fact]
    public void Mint_ProducesADistinctOperationIdPerCall()
    {
        var authorizations = new[]
        {
            new Dictionary<string, object?> { ["registry_id"] = "reg-a", ["generation"] = 1, ["identity_digest"] = A64 },
        };
        var first = HostAuthorizationMinter.Mint("pl-1", A64, "resync", authorizations);
        var second = HostAuthorizationMinter.Mint("pl-1", A64, "resync", authorizations);
        Assert.NotEqual(first.OperationId, second.OperationId);
        Assert.NotEqual(first.HostReceiptId, second.HostReceiptId);
    }
}
