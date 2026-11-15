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
    /// E-7 #2 (Codex ruling 2026-11-16 §5.1/§5.3): this used to document fail-open for a frame WITHOUT a
    /// request_id. The ruling made the production predicate strict and requires the kept judge to reuse it,
    /// so a missing id is now a typed rejection instead of being accepted.
    /// </summary>
    [Fact]
    public void MissingRequestId_ThrowsTypedMalformedResponse()
    {
        var response = CoreProtocol.Parse(
            "{\"protocol\":\"new-manga.core\",\"version\":{\"major\":2,\"minor\":3},\"result\":[],\"error\":null}");

        Assert.Null(response.RequestId);

        var error = Assert.Throws<SidecarException>(
            () => CoreServiceClient.EnsureResponseBelongsToRequest(response, "req-1", stderrLogPath: null));

        Assert.Equal(SidecarErrorCode.MalformedResponse, error.Code);
        // r2 R2-01: the message now distinguishes "no usable id" from "wrong id", so assert the
        // missing-id wording rather than a placeholder.
        Assert.Contains("no usable request_id", error.Message, StringComparison.Ordinal);
    }

    /// <summary>
    /// E-7 #2 裁决 §5.3: every non-string shape of request_id must be rejected, not just the missing key.
    /// (The parser maps all of these to a null RequestId.)
    /// </summary>
    [Theory]
    [InlineData("null")]
    [InlineData("123")]
    [InlineData("true")]
    [InlineData("{}")]
    [InlineData("[]")]
    [InlineData("\"\"")]
    public void NonStringOrEmptyRequestId_ThrowsTypedMalformedResponse(string requestIdJson)
    {
        var response = CoreProtocol.Parse(
            "{\"protocol\":\"new-manga.core\",\"version\":{\"major\":2,\"minor\":3},\"request_id\":"
            + requestIdJson + ",\"result\":[],\"error\":null}");

        // "" parses as an empty STRING (not null) and therefore fails the equality check; the others
        // parse as null and fail the "must be present" part of the strict predicate. Both are rejections.
        var error = Assert.Throws<SidecarException>(
            () => CoreServiceClient.EnsureResponseBelongsToRequest(response, "req-1", stderrLogPath: null));

        Assert.Equal(SidecarErrorCode.MalformedResponse, error.Code);
    }

    /// <summary>
    /// The strict predicate itself (shared by the production resync path and the kept judge) must agree
    /// with the judge for the same inputs.
    /// </summary>
    [Fact]
    public void BelongsToRequest_IsStrict_ForMissingAndMismatchedIds()
    {
        Assert.False(CoreServiceClient.BelongsToRequest(CoreProtocol.Parse("{\"result\":[]}"), "req-1"));
        Assert.False(CoreServiceClient.BelongsToRequest(ResponseWithId("req-999"), "req-1"));
        Assert.True(CoreServiceClient.BelongsToRequest(ResponseWithId("req-1"), "req-1"));
    }
}
