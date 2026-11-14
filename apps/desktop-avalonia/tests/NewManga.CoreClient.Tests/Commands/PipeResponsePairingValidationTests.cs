using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// CORE-PIPE-EXCLUSIVE-1 / E-6 (P1), AC3: a response whose <c>request_id</c> does not match the request
/// means the shared core pipe handed back another command's answer. That is exactly how
/// <c>list_chapters</c> received <c>source_list_scan_targets</c>'s <c>{"targets": []}</c> and silently
/// produced an empty chapter list. The client must reject such a frame with a typed error instead of
/// accepting it.
///
/// r1 复核 R-005 pointed out this validation had **zero tests** (deleting it kept every test green).
/// These facts pin it directly, without needing a live sidecar.
/// </summary>
public sealed class PipeResponsePairingValidationTests
{
    private const string ResponseEnvelopePrefix =
        "{\"protocol\":\"new-manga.core\",\"version\":{\"major\":2,\"minor\":3},\"request_id\":\"";

    private static CoreResponse ResponseWithId(string requestId, string resultJson = "[]")
    {
        var json = ResponseEnvelopePrefix + requestId
            + "\",\"result\":" + resultJson + ",\"error\":null}";
        return CoreProtocol.Parse(json);
    }

    [Fact]
    public void MismatchedRequestId_ThrowsTypedMalformedResponse()
    {
        var response = ResponseWithId("req-999");

        var error = Assert.Throws<SidecarException>(
            () => CoreServiceClient.EnsureResponseBelongsToRequest(response, "req-1", stderrLogPath: null));

        Assert.Equal(SidecarErrorCode.MalformedResponse, error.Code);
        Assert.Contains("req-999", error.Message, StringComparison.Ordinal);
        Assert.Contains("req-1", error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void MatchingRequestId_IsAccepted()
    {
        var response = ResponseWithId("req-1");

        CoreServiceClient.EnsureResponseBelongsToRequest(response, "req-1", stderrLogPath: null);
    }

    /// <summary>
    /// Known limitation (r1 复核 R-001): a frame WITHOUT a request_id currently passes the check
    /// (fail-open). This fact documents the current behaviour so that any future change to fail-closed
    /// has to update it deliberately rather than silently.
    /// </summary>
    [Fact]
    public void MissingRequestId_CurrentlyFailsOpen_DocumentedLimitation()
    {
        var response = CoreProtocol.Parse(
            "{\"protocol\":\"new-manga.core\",\"version\":{\"major\":2,\"minor\":3},\"result\":[],\"error\":null}");

        Assert.Null(response.RequestId);
        CoreServiceClient.EnsureResponseBelongsToRequest(response, "req-1", stderrLogPath: null);
    }
}
