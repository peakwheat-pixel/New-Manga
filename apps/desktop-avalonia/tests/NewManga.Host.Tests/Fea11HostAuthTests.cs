using System.Text.Json;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-HOST-AUTH-1 (C-17 §3.2/§5.2): the Host orchestrator mints its own
/// operation id/authorization, authorizes the registry durably before the
/// journal, injects the frozen payload, and only then calls the Core.
/// </summary>
public sealed class Fea11HostAuthTests : IDisposable
{
    private readonly string _root;
    private readonly SourceOperationCoordinator _operations;
    private readonly SourceAccessRegistry _registry;

    public Fea11HostAuthTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-fea11-hostauth-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_root);
        _operations = new SourceOperationCoordinator(null, _root);
        _registry = new SourceAccessRegistry(_root);
        _registry.Register("loc-1", new[] { _root });
    }

    public void Dispose()
    {
        try { Directory.Delete(_root, recursive: true); } catch { /* best effort */ }
    }

    private JsonElement CallerPayload(string? planDigest = null)
    {
        var known = _registry.List().Single();
        return JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["plan_id"] = "pl-1",
            ["plan_digest"] = planDigest ?? new string('a', 64),
            ["operation_id"] = "op-CALLER-CONTROLLED",
            ["grant_ids"] = new[] { "g-1" },
            ["authorization"] = new Dictionary<string, object?>
            {
                ["operation_id"] = "op-CALLER-CONTROLLED",
                ["request_digest"] = new string('b', 64),
                ["authorization_digest"] = new string('c', 64),
                ["host_receipt_id"] = "hr-caller",
                ["authorized_at"] = "2026-01-01T00:00:00.000Z",
                ["authorizations"] = new[]
                {
                    new Dictionary<string, object?>
                    {
                        ["registry_id"] = known.RegistryId,
                        ["generation"] = known.Generation,
                        ["identity_digest"] = new string('d', 64),
                    },
                },
            },
        });
    }

    private HostOperationOrchestrator NewOrchestrator(
        Func<string, CancellationToken, Task>? capability = null)
    {
        return new HostOperationOrchestrator(
            _operations,
            _registry,
            capability ?? ((_, _) => Task.CompletedTask),
            (_, _) => Task.FromResult(JsonSerializer.SerializeToElement(new Dictionary<string, object?>
            {
                ["operation_id"] = "op-x",
                ["state"] = "core-committed",
                ["commit_digest"] = new string('e', 64),
            })));
    }

    [Fact]
    public async Task Apply_InjectsTheHostMintedAuthorizationNotTheCallers()
    {
        JsonElement? seen = null;
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();

        var (operationId, _) = await orchestrator.ApplyAsync("source_resync", payload, (finalPayload, _) =>
        {
            seen = finalPayload.Clone();
            return Task.FromResult(new CoreResponse(
                null, JsonSerializer.SerializeToElement(new { state = "core-committed" }), null));
        }, CancellationToken.None);

        Assert.Matches("^op-[0-9a-f]{32}$", operationId);
        Assert.NotNull(seen);
        var sent = seen!.Value;
        Assert.Equal(operationId, sent.GetProperty("operation_id").GetString());
        var authorization = sent.GetProperty("authorization");
        Assert.Equal(operationId, authorization.GetProperty("operation_id").GetString());
        Assert.NotEqual("hr-caller", authorization.GetProperty("host_receipt_id").GetString());
        Assert.Equal(6, authorization.EnumerateObject().Count());
        Assert.Equal("core-committed", _operations.Get(operationId)!.State);
    }

    [Fact]
    public async Task Apply_TypedPreCommitRejection_IsDurablyFailedWithErrorCode()
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();

        var error = await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new CoreOperationException(
                "SOURCE_ACCESS_DENIED", "protocol", false, "denied", null),
            CancellationToken.None));
        Assert.Equal("SOURCE_ACCESS_DENIED", error.Code);

        var entries = Directory.GetFiles(Path.Combine(_root, "host", "source-operations"), "*.dat");
        Assert.Single(entries);
        var operationId = Path.GetFileName(entries[0])
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        var journaled = _operations.Get(operationId)!;
        Assert.Equal("failed", journaled.State);
        Assert.Equal("SOURCE_ACCESS_DENIED", journaled.ErrorCode);
        Assert.False(journaled.Retryable);
    }

    [Fact]
    public async Task Apply_AmbiguousCoreFailure_KeepsHostAuthorizedAndExposesTheOperationId()
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();

        var error = await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new IOException("transport lost"),
            CancellationToken.None));

        Assert.Equal("CORE_UNAVAILABLE", error.Code);
        Assert.Contains("op-", error.Message);
        var entries = Directory.GetFiles(Path.Combine(_root, "host", "source-operations"), "*.dat");
        var operationId = Path.GetFileName(entries.Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        Assert.Equal("host-authorized", _operations.Get(operationId)!.State);
    }

    [Fact]
    public async Task Apply_AuthorizesTheRegistryBeforeTheCoreCall()
    {
        // LastUsedAt is only advanced by SourceAccessRegistry.Authorize; if the
        // orchestrator skipped Authorize, the probe below would stay at the
        // registration timestamp and fail (r2 P2-01: the old probe was vacuous).
        var before = _registry.List().Single().LastUsedAt;
        await Task.Delay(5);
        string? duringCall = null;
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();

        await orchestrator.ApplyAsync("source_resync", payload, (_, _) =>
        {
            duringCall = _registry.List().Single().LastUsedAt;
            return Task.FromResult(new CoreResponse(
                null, JsonSerializer.SerializeToElement(new { state = "core-committed" }), null));
        }, CancellationToken.None);

        Assert.NotNull(duringCall);
        Assert.NotEqual(before, duringCall);
    }

    [Fact]
    public async Task Apply_RejectsAMissingPlanDigestWithoutJournal()
    {
        var orchestrator = NewOrchestrator();
        var payload = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["plan_id"] = "pl-1",
            ["grant_ids"] = Array.Empty<string>(),
            ["authorization"] = new { authorizations = Array.Empty<object>() },
        });

        var error = await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new InvalidOperationException("must not reach Core"),
            CancellationToken.None));
        Assert.Equal("INVALID_REQUEST", error.Code);
        Assert.False(Directory.Exists(Path.Combine(_root, "host", "source-operations")));
    }

    [Fact]
    public async Task Apply_RunsTheCapabilityGateBeforeAnyJournalEntry()
    {
        var orchestrator = NewOrchestrator((_, _) => throw new CoreOperationException(
            "CORE_CAPABILITY_MISSING", "protocol", false, "missing", null));
        var payload = CallerPayload();

        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new InvalidOperationException("must not reach Core"),
            CancellationToken.None));

        var journalDir = Path.Combine(_root, "host", "source-operations");
        Assert.False(Directory.Exists(journalDir) && Directory.GetFiles(journalDir).Length > 0);
    }

    [Fact]
    public async Task Apply_RejectsAMalformedPlanDigestWithoutJournal()
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload(planDigest: "not-a-digest");

        var error = await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new InvalidOperationException("must not reach Core"),
            CancellationToken.None));

        Assert.Equal("INVALID_REQUEST", error.Code);
        Assert.False(Directory.Exists(Path.Combine(_root, "host", "source-operations")));
    }

    [Theory]
    [InlineData("SOURCE_PLAN_STALE", true)]
    [InlineData("SOURCE_GRANT_EXPIRED", true)]
    [InlineData("SOURCE_ACCESS_DENIED", false)]
    public async Task Apply_PersistsTheCoreRetryableFlag(string code, bool retryable)
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();

        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new CoreOperationException(code, "conflict", retryable, "x", null),
            CancellationToken.None));

        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        var journaled = _operations.Get(operationId)!;
        Assert.Equal("failed", journaled.State);
        Assert.Equal(code, journaled.ErrorCode);
        Assert.Equal(retryable, journaled.Retryable);
    }

    [Fact]
    public async Task Retry_ReusesTheSameOperationAndDigestAndCommits()
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();
        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new CoreOperationException("SOURCE_PLAN_STALE", "conflict", true, "stale", null),
            CancellationToken.None));
        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        var failedEntry = _operations.Get(operationId)!;

        var retriedCallPayload = default(JsonElement);
        var retryPayload = CallerPayload();
        var (retriedId, _) = await orchestrator.RetryAsync("source_resync", operationId, retryPayload,
            (finalPayload, _) =>
            {
                retriedCallPayload = finalPayload.Clone();
                return Task.FromResult(new CoreResponse(
                    null, JsonSerializer.SerializeToElement(new { state = "core-committed" }), null));
            }, CancellationToken.None);

        Assert.Equal(operationId, retriedId);
        Assert.Equal(failedEntry.RequestDigest,
            retriedCallPayload.GetProperty("authorization").GetProperty("request_digest").GetString());
        Assert.NotEqual(
            failedEntry.HostReceiptId,
            retriedCallPayload.GetProperty("authorization").GetProperty("host_receipt_id").GetString());
        Assert.Equal("core-committed", _operations.Get(operationId)!.State);
    }

    [Fact]
    public async Task Retry_TypedRejectionIsDurablyFailedAgain()
    {
        var orchestrator = NewOrchestrator();
        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", CallerPayload(),
            (_, _) => throw new CoreOperationException("SOURCE_PLAN_STALE", "conflict", true, "stale", null),
            CancellationToken.None));
        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);

        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.RetryAsync(
            "source_resync", operationId, CallerPayload(),
            (_, _) => throw new CoreOperationException("SOURCE_GRANT_EXPIRED", "protocol", true, "expired", null),
            CancellationToken.None));

        var journaled = _operations.Get(operationId)!;
        Assert.Equal("failed", journaled.State);
        Assert.Equal("SOURCE_GRANT_EXPIRED", journaled.ErrorCode);
        Assert.True(journaled.Retryable);
    }

    [Fact]
    public async Task Retry_RefusesACommittedFailure()
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();
        await orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => Task.FromResult(new CoreResponse(
                null, JsonSerializer.SerializeToElement(new { state = "core-committed" }), null)),
            CancellationToken.None);
        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        // A committed operation is terminal for retry (recovery instead).
        await Assert.ThrowsAsync<SourceAccessException>(() =>
            orchestrator.RetryAsync("source_resync", operationId, payload,
                (_, _) => Task.FromResult(new CoreResponse(null, default, null)),
                CancellationToken.None));
    }

    [Fact]
    public async Task Retry_RefusesANonRetryableFailure()
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();
        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new CoreOperationException("SOURCE_ACCESS_DENIED", "protocol", false, "denied", null),
            CancellationToken.None));
        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);

        await Assert.ThrowsAsync<SourceAccessException>(() =>
            orchestrator.RetryAsync("source_resync", operationId, payload,
                (_, _) => Task.FromResult(new CoreResponse(null, default, null)),
                CancellationToken.None));
    }

    [Fact]
    public async Task Apply_RejectsCommaInGrantIds()
    {
        var orchestrator = NewOrchestrator();
        var payload = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["plan_id"] = "pl-1",
            ["plan_digest"] = new string('a', 64),
            ["grant_ids"] = new[] { "g-1,g-2" },
            ["authorization"] = new { authorizations = Array.Empty<object>() },
        });

        var error = await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new InvalidOperationException("must not reach Core"),
            CancellationToken.None));
        Assert.Equal("INVALID_REQUEST", error.Code);
    }

    [Theory]
    [InlineData("SOURCE_PLAN_STALE", true)]
    [InlineData("SOURCE_GRANT_EXPIRED", true)]
    [InlineData("SOURCE_ACCESS_DENIED", false)]
    [InlineData("SOURCE_SYNC_STATE_CONFLICT", false)]
    public void HostErrorCodes_ProjectTheC17RetryableColumn(string code, bool retryable)
    {
        Assert.True(HostErrorCodes.IsKnown(code));
        Assert.Equal(retryable, HostErrorCodes.RetryableOf(code));
        Assert.False(HostErrorCodes.IsKnown("NOT_A_C17_CODE"));
    }
}
