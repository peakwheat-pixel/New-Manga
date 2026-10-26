using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Tests.Support;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// AC2 dual channel: the existing <c>host_bridge.exe</c> (wire v1) issues/resolves/revokes a grant
/// against a catalog seeded by the packaged <c>catalog_loader.exe</c>. Typed errors are asserted so
/// the UI layer can render codes instead of guessing from strings.
/// </summary>
public sealed class HostBridgeIntegrationTests
{
    [SidecarFact]
    public async Task Ping_IssueResolveRevoke_FullLifecycle()
    {
        using var context = SidecarFixture.CreateBridgeContext("bridge-lifecycle");
        await using var bridge = await HostBridgeClient.StartAsync(context.Options);

        Assert.True(await bridge.PingAsync());

        var issued = await bridge.IssueAsync("res-1", "rev-1");
        Assert.False(string.IsNullOrEmpty(issued.GrantId));
        Assert.True(issued.Size > 0);

        var grant = await bridge.ResolveAsync(issued.GrantId);
        Assert.Equal("managed-read-only", grant.ScopeClass);
        Assert.Equal("res-1", grant.ResourceId);
        Assert.Equal("rev-1", grant.RevisionFingerprint);
        Assert.Equal("book/page01.jpg", grant.RelPath);
        Assert.True(grant.Size > 0);
        Assert.Equal(64, grant.Sha256.Length);
        Assert.True(grant.VolumeSerial > 0);
        Assert.True(grant.FileIndex > 0);

        await bridge.RevokeAsync(issued.GrantId);
        var revoked = await Assert.ThrowsAsync<BridgeException>(() => bridge.ResolveAsync(issued.GrantId));
        Assert.Equal("REF_REVOKED", revoked.Code);

        Assert.True(bridge.Wire.AllRequestsAsciiOnly);
        SidecarFixture.WriteEvidenceJson("wire/host-bridge-lifecycle.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteString("catalog_loader_stdout", context.CatalogLoaderStdout);
            writer.WriteNumber("catalog_loader_exit_code", context.CatalogLoaderExitCode);
            writer.WriteString("grant_id", issued.GrantId);
            writer.WriteString("rel_path", grant.RelPath);
            writer.WriteNumber("size", grant.Size);
            writer.WriteString("sha256", grant.Sha256);
            writer.WriteString("error_after_revoke", revoked.Code);
            SidecarFixture.WriteFrameSummary(writer, "frames", bridge.Wire.Frames);
            writer.WriteEndObject();
        });
    }

    [SidecarFact]
    public async Task TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling()
    {
        using var context = SidecarFixture.CreateBridgeContext("bridge-errors");
        await using var bridge = await HostBridgeClient.StartAsync(context.Options);

        var unknown = await Assert.ThrowsAsync<BridgeException>(() => bridge.IssueAsync("does-not-exist", "rev-1"));
        Assert.Equal("RESOURCE_NOT_CATALOGED", unknown.Code);

        // The RC2 hardening refuses host-supplied rel_path on the wire (core-owned catalog state).
        var smuggled = await Assert.ThrowsAsync<BridgeException>(async () =>
            await bridge.SendRawAsync(
                "{\"id\":99,\"method\":\"issue\",\"params\":{\"resource_id\":\"res-1\",\"revision_fingerprint\":\"rev-1\",\"rel_path\":\"escape.jpg\"}}"));
        Assert.Equal("REF_MALFORMED", smuggled.Code);

        SidecarFixture.WriteEvidenceJson("wire/host-bridge-errors.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2/AC4");
            writer.WriteString("unknown_resource_error", unknown.Code);
            writer.WriteString("unknown_resource_message", unknown.UserMessage);
            writer.WriteString("smuggled_rel_path_error", smuggled.Code);
            SidecarFixture.WriteFrameSummary(writer, "frames", bridge.Wire.Frames);
            writer.WriteEndObject();
        });
    }

    [SidecarFact]
    public async Task WireFrames_AreSingleLineJson_AsciiOnly()
    {
        using var context = SidecarFixture.CreateBridgeContext("bridge-wire");
        await using var bridge = await HostBridgeClient.StartAsync(context.Options);
        await bridge.PingAsync();

        foreach (var frame in bridge.Wire.Frames)
        {
            Assert.True(frame.RequestAsciiOnly);
            Assert.True(frame.ResponseAsciiOnly);
            Assert.StartsWith("{", frame.RequestLine, StringComparison.Ordinal);
            Assert.StartsWith("{", frame.ResponseLine, StringComparison.Ordinal);
        }
    }
}
