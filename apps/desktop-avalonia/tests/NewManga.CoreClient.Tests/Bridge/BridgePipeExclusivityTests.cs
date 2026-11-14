using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Tests.Support;
using Xunit;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// PIPE-EXCLUSIVE-TRANSPORT-1 / E-7 (window 1): <c>HostBridgeClient</c> owns a SECOND sidecar pipe
/// (<c>host_bridge.exe</c>, its own <c>SidecarProcess</c>) which had no exclusivity at all — every call
/// went straight to <c>_process.ExchangeAsync</c>, and <c>ParseResponse</c> never checked the response
/// id. Two concurrent callers therefore read the same shared <c>StreamReader</c>, which throws
/// "The stream is currently in use by a previous operation on the stream" and can also hand back the
/// wrong response.
///
/// This test drives that pipe concurrently. Before the fix it fails (the shared stream is entered twice);
/// after the fix every call must complete successfully.
/// </summary>
public sealed class BridgePipeExclusivityTests
{
    private const int Rounds = 12;

    [SidecarFact]
    public async Task ConcurrentBridgePings_DoNotTripTheSharedStream()
    {
        using var context = SidecarFixture.CreateBridgeContext("bridge-pipe-exclusive");
        await using var bridge = await HostBridgeClient.StartAsync(context.Options);

        // Warm up so the concurrent phase is not racing the handshake.
        Assert.True(await bridge.PingAsync());

        var pending = Enumerable.Range(0, Rounds).Select(_ => bridge.PingAsync()).ToArray();
        await Task.WhenAll(pending);

        foreach (var task in pending)
        {
            Assert.True(task.Result, "a concurrent host_bridge ping returned false");
        }
    }

    /// <summary>
    /// Same pipe, two DIFFERENT commands that need no catalog rows: a ping (answers true) and a resolve of
    /// a grant id that cannot exist (answers a typed error). If the two responses cross, the resolve would
    /// receive the ping's success payload and stop throwing — so this pins "no crossed responses" on the
    /// second pipe without depending on seeded resources.
    /// </summary>
    [SidecarFact]
    public async Task ConcurrentMixedBridgeCommands_DoNotCrossResponses()
    {
        using var context = SidecarFixture.CreateBridgeContext("bridge-pipe-mixed");
        await using var bridge = await HostBridgeClient.StartAsync(context.Options);

        Assert.True(await bridge.PingAsync());

        var pings = Enumerable.Range(0, 6).Select(_ => bridge.PingAsync()).ToArray();
        var resolves = Enumerable.Range(0, 6)
            .Select(i => ResolveAsyncOutcome(bridge, $"grant-that-does-not-exist-{i}"))
            .ToArray();

        await Task.WhenAll(pings.Cast<Task>().Concat(resolves.Cast<Task>()));

        foreach (var ping in pings)
        {
            Assert.True(ping.Result, "a concurrent host_bridge ping returned false");
        }

        foreach (var resolve in resolves)
        {
            // Every resolve must have produced a TYPED bridge error. If it had received the ping's
            // response instead, it would have returned normally and this would fail.
            Assert.False(
                resolve.Result.Succeeded,
                "a resolve of a non-existent grant succeeded: its response was probably crossed with a ping");
            Assert.False(string.IsNullOrEmpty(resolve.Result.ErrorCode), "a failed resolve reported no typed code");
        }
    }

    private readonly record struct ResolveOutcome(bool Succeeded, string? ErrorCode);

    private static async Task<ResolveOutcome> ResolveAsyncOutcome(HostBridgeClient bridge, string grantId)
    {
        try
        {
            var grant = await bridge.ResolveAsync(grantId);
            _ = grant;
            return new ResolveOutcome(true, null);
        }
        catch (BridgeException error)
        {
            return new ResolveOutcome(false, error.Code.ToString());
        }
    }
}
