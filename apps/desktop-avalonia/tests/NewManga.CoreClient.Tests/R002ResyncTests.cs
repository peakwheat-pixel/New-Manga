using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// E-7 / R-002 (P1): a response carrying a DIFFERENT request id used to throw immediately and leave the
/// real response on the wire, so the next command read its predecessor's answer — a permanent off-by-one
/// until the sidecar was restarted.
///
/// <para>These tests drive <c>CoreServiceClient.ReadResponseForRequestAsync</c> directly with a fake
/// "next line" delegate, so the resynchronisation logic is exercised without a real core process (which
/// would additionally require the <c>core.ping</c> handshake).</para>
/// </summary>
public sealed class R002ResyncTests
{
    private static string Response(string requestId, string resultJson = "null") =>
        "{\"request_id\":\"" + requestId + "\",\"result\":" + resultJson + "}";

    [Fact]
    public async Task MismatchedFirstFrame_IsDrainedUntilTheMatchingResponseArrives()
    {
        // First frame belongs to someone else (the off-by-one that R-002 is about), second is ours.
        var frames = new Queue<string>(new[]
        {
            Response("req-999999"),
            Response("req-7", "{\"ok\":true}"),
        });

        var poisoned = false;
        var response = await CoreServiceClient.ReadResponseForRequestAsync(
            frames.Dequeue(),
            "req-7",
            _ => Task.FromResult(frames.Dequeue()),
            () => poisoned = true,
            CoreServiceClient.ResyncMaxDrainFrames,
            stderrLogPath: null,
            CancellationToken.None);

        Assert.Equal("req-7", response.RequestId);
        Assert.False(poisoned, "resynchronisation succeeded, so the channel must NOT be poisoned");
    }

    [Fact]
    public async Task EventFramesAreStillSkippedWhileResynchronising()
    {
        // Event frames carry no request_id and are single-direction notifications: skip them on the way.
        var frames = new Queue<string>(new[]
        {
            "{\"event_type\":\"ReadingProgressChanged\",\"event_id\":1}",
            Response("req-999999"),
            "{\"event_type\":\"ReadingProgressChanged\",\"event_id\":2}",
            Response("req-7", "{\"ok\":true}"),
        });

        var poisoned = false;
        var response = await CoreServiceClient.ReadResponseForRequestAsync(
            frames.Dequeue(),
            "req-7",
            _ => Task.FromResult(frames.Dequeue()),
            () => poisoned = true,
            CoreServiceClient.ResyncMaxDrainFrames,
            stderrLogPath: null,
            CancellationToken.None);

        Assert.Equal("req-7", response.RequestId);
        Assert.False(poisoned);
    }

    [Fact]
    public async Task ResyncGivesUpAfterMaxFrames_AndPoisonsTheChannel()
    {
        // Never correct: every frame belongs to another request.
        var poisoned = false;
        var drained = 0;
        var ex = await Assert.ThrowsAsync<SidecarException>(() =>
            CoreServiceClient.ReadResponseForRequestAsync(
                Response("req-1"),
                "req-7",
                _ =>
                {
                    drained++;
                    return Task.FromResult(Response("req-" + (100 + drained)));
                },
                () => poisoned = true,
                maxDrainFrames: 4,
                stderrLogPath: null,
                CancellationToken.None));

        Assert.Equal(SidecarErrorCode.MalformedResponse, ex.Code);
        Assert.Contains("resynchronised", ex.Message, StringComparison.OrdinalIgnoreCase);
        Assert.Equal(4, drained);
        Assert.True(poisoned, "an unresynchronisable pipe must be poisoned so later calls fail closed");
    }

    [Fact]
    public async Task ResponseWithoutRequestId_IsAcceptedWithoutDraining()
    {
        // The frozen core omits request_id on some frames; those belong to the request by definition.
        var called = false;
        var response = await CoreServiceClient.ReadResponseForRequestAsync(
            "{\"result\":{\"ok\":true}}",
            "req-7",
            _ =>
            {
                called = true;
                return Task.FromResult(Response("req-7"));
            },
            () => { },
            CoreServiceClient.ResyncMaxDrainFrames,
            stderrLogPath: null,
            CancellationToken.None);

        Assert.Null(response.RequestId);
        Assert.False(called, "a response without a request id must not trigger draining");
    }
}
