using System.Globalization;
using System.Text.Json;
using NewManga.CoreClient.Commands;
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

    [Fact]
    public async Task Retry_PersistsTheFreshAuthorizationInTheJournal()
    {
        var orchestrator = NewOrchestrator();
        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", CallerPayload(),
            (_, _) => throw new CoreOperationException("SOURCE_PLAN_STALE", "conflict", true, "stale", null),
            CancellationToken.None));
        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        var before = _operations.Get(operationId)!;

        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.RetryAsync(
            "source_resync", operationId, CallerPayload(),
            (_, _) => throw new CoreOperationException("SOURCE_SYNC_UNSTABLE", "conflict", true, "unstable", null),
            CancellationToken.None));
        var after = _operations.Get(operationId)!;

        Assert.Equal(before.RequestDigest, after.RequestDigest);
        Assert.NotEqual(before.HostReceiptId, after.HostReceiptId);
        Assert.NotEqual(before.AuthorizationJson, after.AuthorizationJson);
        Assert.Equal("failed", after.State);
        Assert.Equal("SOURCE_SYNC_UNSTABLE", after.ErrorCode);
    }

    [Fact]
    public async Task Retry_RefusesACommandKindMismatch()
    {
        var orchestrator = NewOrchestrator();
        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", CallerPayload(),
            (_, _) => throw new CoreOperationException("SOURCE_PLAN_STALE", "conflict", true, "stale", null),
            CancellationToken.None));
        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);

        var error = await Assert.ThrowsAsync<CoreOperationException>(() =>
            orchestrator.RetryAsync("source_relink", operationId, CallerPayload(),
                (_, _) => Task.FromResult(new CoreResponse(null, default, null)),
                CancellationToken.None));
        Assert.Equal("SOURCE_SYNC_STATE_CONFLICT", error.Code);
    }

    [Fact]
    public async Task Retry_RunsTheCapabilityGateBeforeTouchingTheJournal()
    {
        var orchestrator = NewOrchestrator((_, _) => throw new CoreOperationException(
            "CORE_CAPABILITY_MISSING", "protocol", false, "missing", null));
        var payload = CallerPayload();

        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new CoreOperationException("SOURCE_PLAN_STALE", "conflict", true, "stale", null),
            CancellationToken.None));
        // Apply used the same orchestrator: with a failing gate it cannot have
        // journaled anything, so the retry itself must also fail on the gate.
        Assert.False(Directory.Exists(Path.Combine(_root, "host", "source-operations")));
        var retryError = await Assert.ThrowsAsync<CoreOperationException>(() =>
            orchestrator.RetryAsync("source_resync", "op-00000000000000000000000000000000", payload,
                (_, _) => Task.FromResult(new CoreResponse(null, default, null)),
                CancellationToken.None));
        Assert.Equal("CORE_CAPABILITY_MISSING", retryError.Code);
    }

    [Fact]
    public async Task Retry_RefusesAJournaledRequestDigestMismatch()
    {
        // r7-P2-01: journal a failed operation whose request digest would not be
        // reproduced by the retry mint — the digest guard must reject it before
        // the registry authorization happens.
        var operationId = "op-" + new string('0', 32);
        _operations.Begin(
            "pl-1", new string('a', 64), "resync", new string('f', 64), operationId);
        _operations.MarkFailed(operationId, "SOURCE_PLAN_STALE", retryable: true);
        var lastUsedBefore = _registry.List().Single().LastUsedAt;
        var orchestrator = NewOrchestrator();

        var error = await Assert.ThrowsAsync<CoreOperationException>(() =>
            orchestrator.RetryAsync("source_resync", operationId, CallerPayload(),
                (_, _) => Task.FromResult(new CoreResponse(null, default, null)),
                CancellationToken.None));

        Assert.Equal("SOURCE_SYNC_STATE_CONFLICT", error.Code);
        Assert.Equal("failed", _operations.Get(operationId)!.State);
        Assert.Equal(lastUsedBefore, _registry.List().Single().LastUsedAt);
    }

    [Fact]
    public async Task Retry_RefusesACommittedFailedOperationWithCommitDigest()
    {
        // r7-P2-01: C-17 §3.2:162 records a committed failure with a commit
        // digest; such an operation must go through recovery, never retry.
        var orchestrator = NewOrchestrator();
        await orchestrator.ApplyAsync("source_resync", CallerPayload(),
            (_, _) => Task.FromResult(new CoreResponse(
                null, JsonSerializer.SerializeToElement(new { state = "core-committed" }), null)),
            CancellationToken.None);
        var operationId = Path.GetFileName(Directory.GetFiles(
                Path.Combine(_root, "host", "source-operations"), "*.dat").Single())
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        _operations.MarkFailed(operationId, "SOURCE_SYNC_STORAGE_FAILED", retryable: true);

        var error = await Assert.ThrowsAsync<SourceAccessException>(() =>
            orchestrator.RetryAsync("source_resync", operationId, CallerPayload(),
                (_, _) => Task.FromResult(new CoreResponse(null, default, null)),
                CancellationToken.None));

        Assert.Equal("SOURCE_SYNC_STATE_CONFLICT", error.Code);
        var journaled = _operations.Get(operationId)!;
        Assert.Equal("failed", journaled.State);
        Assert.NotNull(journaled.CommitDigest);
    }
}

/// <summary>
/// FEA-11-HOST-AUTH-2 (C-17 §3.2:161/:169): ACK/recovery must not replay the
/// authorization the apply journaled. <c>PrepareCompletion</c> re-reads the LIVE
/// registry (advancing <c>LastUsedAt</c>), re-mints with the live generation plus
/// the COMMITTED baseline identity digest, keeps the operation id / request digest
/// / host receipt identity, and persists the fresh bytes BEFORE any Core frame.
///
/// Default gate: the seam is deliberately Core-free (<c>CoreServiceClient</c> is
/// sealed and cannot be faked), so the real Core round-trips live in the gated
/// <c>Fea11HostAuthIpcTests</c>.
/// </summary>
public sealed class Fea11HostAuth2FreshCompletionTests : IDisposable
{
    private const string PlanId = "pl-fresh";
    private const string Kind = "resync";

    private readonly string _root;
    private readonly string _sourceRoot;
    private readonly string _planDigest = new('a', 64);
    private readonly string _identityDigest = new('d', 64);
    private readonly string _commitDigest = new('e', 64);
    private readonly SourceAccessRegistry _registry;
    private readonly SourceOperationCoordinator _operations;

    public Fea11HostAuth2FreshCompletionTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-fea11-fresh-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_root);
        _sourceRoot = Path.Combine(_root, "source");
        Directory.CreateDirectory(_sourceRoot);
        _registry = new SourceAccessRegistry(_root);
        _registry.Register("loc-fresh", [_sourceRoot]);
        _operations = new SourceOperationCoordinator(null, _root, null, _registry);
    }

    public void Dispose()
    {
        try { Directory.Delete(_root, recursive: true); } catch { /* best effort */ }
    }

    private sealed record JournaledOperation(
        string OperationId, string ApplyAuthorizationJson, string HostReceiptId, string RequestDigest);

    private string JournalPath(string operationId) =>
        Path.Combine(_root, "host", "source-operations", operationId + ".v1.dat");

    /// <summary>A NEW coordinator over the same data root: proves the journal bytes
    /// (not an in-memory field) carry the fresh authorization.</summary>
    private SourceOperationCoordinator AfterRestart() =>
        new(null, _root, null, _registry);

    private JournaledOperation JournalCommittedOperation(
        int? baselineGeneration = null,
        string? requestDigest = null,
        Func<string, string, string>? receiptFactory = null)
    {
        var live = _registry.List().Single();
        var minted = HostAuthorizationMinter.Mint(PlanId, _planDigest, Kind,
        [
            new Dictionary<string, object?>
            {
                ["registry_id"] = live.RegistryId,
                ["generation"] = baselineGeneration ?? live.Generation,
                ["identity_digest"] = _identityDigest,
            },
        ]);
        _operations.Begin(PlanId, _planDigest, Kind,
            requestDigest ?? minted.RequestDigest, minted.OperationId, ["g-1"]);
        var applyAuthorizationJson = CanonicalJson.Text(minted.Authorization);
        _operations.Authorize(minted.OperationId, applyAuthorizationJson, minted.HostReceiptId);
        _operations.MarkCommitted(minted.OperationId, _commitDigest,
            receiptFactory is null
                ? OperationReceipt(minted.OperationId, minted.RequestDigest)
                : receiptFactory(minted.OperationId, minted.RequestDigest));
        return new JournaledOperation(
            minted.OperationId, applyAuthorizationJson, minted.HostReceiptId, minted.RequestDigest);
    }

    /// <summary>The frozen <c>source_get_operation</c> Operation DTO shape.</summary>
    private string OperationReceipt(
        string operationId, string requestDigest, string state = "core-committed") =>
        JsonSerializer.Serialize(new Dictionary<string, object?>
        {
            ["operation_id"] = operationId,
            ["plan_id"] = PlanId,
            ["plan_digest"] = _planDigest,
            ["request_digest"] = requestDigest,
            ["kind"] = Kind,
            ["origin"] = "core",
            ["state"] = state,
            ["commit"] = new Dictionary<string, object?>
            {
                ["operation_id"] = operationId,
                ["plan_id"] = PlanId,
                ["plan_digest"] = _planDigest,
                ["request_digest"] = requestDigest,
                ["bindings"] = Array.Empty<object>(),
                ["committed_at"] = "2026-11-08T00:00:00.000Z",
            },
            ["commit_digest"] = _commitDigest,
            ["error_code"] = null,
            ["retryable"] = false,
            ["acknowledged_at"] = null,
        });

    private string DivergentReceipt(string operationId, string requestDigest, string field)
    {
        var receipt = JsonSerializer.Deserialize<Dictionary<string, object?>>(
            OperationReceipt(operationId, requestDigest))!;
        receipt[field] = field switch
        {
            "state" => "acknowledged",
            "kind" => "relink",
            "plan_id" => "pl-other",
            _ => new string('9', 64),
        };
        return JsonSerializer.Serialize(receipt);
    }

    [Fact]
    public void PrepareCompletion_ReauthorizesTheLiveRegistryAndReSignsTheJournal()
    {
        var journaled = JournalCommittedOperation();
        var lastUsedAtBefore = _registry.List().Single().LastUsedAt;
        var journalBytesBefore = Convert.ToHexString(
            File.ReadAllBytes(JournalPath(journaled.OperationId)));

        var material = _operations.PrepareCompletion(journaled.OperationId);

        // (a) the LIVE registry was re-authorized: LastUsedAt advanced.
        var live = _registry.List().Single();
        Assert.NotEqual(lastUsedAtBefore, live.LastUsedAt);

        // (b) the FRESH authorization is durable: a brand-new coordinator over the
        // same data root reads it back (no in-memory illusion, C-17:160 先落盘).
        var onDisk = AfterRestart().Get(journaled.OperationId)!;
        Assert.Equal("core-committed", onDisk.State);
        Assert.NotEqual(journaled.ApplyAuthorizationJson, onDisk.AuthorizationJson);
        Assert.NotEqual(journalBytesBefore, Convert.ToHexString(
            File.ReadAllBytes(JournalPath(journaled.OperationId))));

        using var apply = JsonDocument.Parse(journaled.ApplyAuthorizationJson);
        using var fresh = JsonDocument.Parse(onDisk.AuthorizationJson!);
        var applyRoot = apply.RootElement;
        var freshRoot = fresh.RootElement;

        // (c) identity is reused, never re-invented.
        Assert.Equal(applyRoot.GetProperty("operation_id").GetString(),
            freshRoot.GetProperty("operation_id").GetString());
        Assert.Equal(applyRoot.GetProperty("request_digest").GetString(),
            freshRoot.GetProperty("request_digest").GetString());
        Assert.Equal(applyRoot.GetProperty("host_receipt_id").GetString(),
            freshRoot.GetProperty("host_receipt_id").GetString());
        Assert.Equal(journaled.OperationId, freshRoot.GetProperty("operation_id").GetString());
        Assert.Equal(journaled.RequestDigest, freshRoot.GetProperty("request_digest").GetString());
        Assert.Equal(journaled.HostReceiptId, freshRoot.GetProperty("host_receipt_id").GetString());
        Assert.Equal(journaled.HostReceiptId, onDisk.HostReceiptId);

        // (d) re-signed: authorized_at is strictly later than the apply one.
        var applyAt = DateTimeOffset.Parse(applyRoot.GetProperty("authorized_at").GetString()!,
            CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal);
        var freshAt = DateTimeOffset.Parse(freshRoot.GetProperty("authorized_at").GetString()!,
            CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal);
        Assert.True(freshAt > applyAt, $"fresh authorized_at {freshAt:O} must be later than {applyAt:O}");

        // (e) live generation + committed baseline identity digest.
        var baseline = applyRoot.GetProperty("authorizations").EnumerateArray().Single();
        var refreshed = freshRoot.GetProperty("authorizations").EnumerateArray().Single();
        Assert.Equal(live.RegistryId, refreshed.GetProperty("registry_id").GetString());
        Assert.Equal(live.Generation, refreshed.GetProperty("generation").GetInt32());
        Assert.Equal(_identityDigest, refreshed.GetProperty("identity_digest").GetString());
        Assert.Equal(baseline.GetProperty("identity_digest").GetString(),
            refreshed.GetProperty("identity_digest").GetString());

        // (f) C-17 §5.2:264 authorization_digest = sha256(canonical(authorizations)).
        var canonicalAuthorizations = freshRoot.GetProperty("authorizations").EnumerateArray()
            .Select(item => new Dictionary<string, object?>
            {
                ["registry_id"] = item.GetProperty("registry_id").GetString(),
                ["generation"] = item.GetProperty("generation").GetInt32(),
                ["identity_digest"] = item.GetProperty("identity_digest").GetString(),
            })
            .ToList();
        var expectedDigest = CanonicalJson.Sha256Hex(canonicalAuthorizations);
        Assert.Equal(expectedDigest, onDisk.AuthorizationDigest);
        Assert.Equal(expectedDigest, freshRoot.GetProperty("authorization_digest").GetString());
        Assert.Equal(expectedDigest, material.AuthorizationDigest);
        Assert.Equal(onDisk.AuthorizationJson, material.AuthorizationJson);
    }

    [Fact]
    public async Task AcknowledgeAsync_PersistsTheFreshAuthorizationBeforeTheCoreCall()
    {
        var journaled = JournalCommittedOperation();
        // No Core client at all: reaching the wire surfaces CORE_UNAVAILABLE.
        var error = await Assert.ThrowsAsync<SourceAccessException>(
            () => _operations.AcknowledgeAsync(journaled.OperationId));
        Assert.Equal("CORE_UNAVAILABLE", error.Code);

        // ... yet the journal is ALREADY durable with the fresh authorization and
        // still core-committed (a retry/recovery can finish the operation).
        var onDisk = AfterRestart().Get(journaled.OperationId)!;
        Assert.Equal("core-committed", onDisk.State);
        Assert.Null(onDisk.AcknowledgedAt);
        Assert.NotEqual(journaled.ApplyAuthorizationJson, onDisk.AuthorizationJson);
        using var fresh = JsonDocument.Parse(onDisk.AuthorizationJson!);
        Assert.Equal(journaled.HostReceiptId,
            fresh.RootElement.GetProperty("host_receipt_id").GetString());
    }

    [Theory]
    [InlineData("revoked", "SOURCE_GRANT_REVOKED")]
    [InlineData("registry-missing", "SOURCE_ACCESS_DENIED")]
    [InlineData("root-identity-changed", "SOURCE_REGISTRY_UNAVAILABLE")]
    [InlineData("baseline-generation-newer", "SOURCE_GRANT_REVOKED")]
    [InlineData("digest-not-reproducible", "SOURCE_SYNC_STATE_CONFLICT")]
    public void PrepareCompletion_RefusalMatrix_IsTypedAndLeavesTheJournalUntouched(
        string scenario, string expectedCode)
    {
        var live = _registry.List().Single();
        var journaled = scenario switch
        {
            "baseline-generation-newer" => JournalCommittedOperation(
                baselineGeneration: live.Generation + 4),
            "digest-not-reproducible" => JournalCommittedOperation(
                requestDigest: new string('f', 64)),
            _ => JournalCommittedOperation(),
        };
        switch (scenario)
        {
            case "revoked":
                _registry.Revoke(live.RegistryId);
                break;
            case "registry-missing":
                _registry.Reset(confirm: true);
                break;
            case "root-identity-changed":
                // Two live directories can never share a file id: the registered
                // root's physical identity is provably replaced.
                Directory.Move(_sourceRoot, _sourceRoot + "-moved");
                Directory.CreateDirectory(_sourceRoot);
                break;
        }
        var journalBytesBefore = Convert.ToHexString(
            File.ReadAllBytes(JournalPath(journaled.OperationId)));

        var error = Assert.Throws<SourceAccessException>(
            () => _operations.PrepareCompletion(journaled.OperationId));

        Assert.Equal(expectedCode, error.Code);
        // Zero Core call: a Core attempt would have surfaced CORE_UNAVAILABLE.
        Assert.NotEqual("CORE_UNAVAILABLE", error.Code);
        // Journal state AND authorization bytes are untouched.
        Assert.Equal(journalBytesBefore, Convert.ToHexString(
            File.ReadAllBytes(JournalPath(journaled.OperationId))));
        var entry = AfterRestart().Get(journaled.OperationId)!;
        Assert.Equal("core-committed", entry.State);
        Assert.Equal(journaled.ApplyAuthorizationJson, entry.AuthorizationJson);
    }

    [Theory]
    [InlineData("request_digest")]
    [InlineData("operation_id")]
    [InlineData("plan_id")]
    [InlineData("kind")]
    [InlineData("commit_digest")]
    [InlineData("state")]
    public void PrepareCompletion_RejectsADivergentCoreReceipt_WithZeroJournalWrites(string field)
    {
        // AC-F1c / limitation 5: the durable Core receipt is re-checked against the
        // journal before ANY completion (C-17 §3.2:160/:164).
        var journaled = JournalCommittedOperation(
            receiptFactory: (operationId, requestDigest) =>
                DivergentReceipt(operationId, requestDigest, field));
        var journalBytesBefore = Convert.ToHexString(
            File.ReadAllBytes(JournalPath(journaled.OperationId)));

        var error = Assert.Throws<SourceAccessException>(
            () => _operations.PrepareCompletion(journaled.OperationId));

        Assert.Equal("SOURCE_SYNC_STATE_CONFLICT", error.Code);
        Assert.Equal("core-committed", AfterRestart().Get(journaled.OperationId)!.State);
        Assert.Equal(journalBytesBefore, Convert.ToHexString(
            File.ReadAllBytes(JournalPath(journaled.OperationId))));
    }

    [Fact]
    public void PrepareCompletion_RecoverySemantics_AcceptAHostAuthorizedJournal()
    {
        var live = _registry.List().Single();
        var minted = HostAuthorizationMinter.Mint(PlanId, _planDigest, Kind,
        [
            new Dictionary<string, object?>
            {
                ["registry_id"] = live.RegistryId,
                ["generation"] = live.Generation,
                ["identity_digest"] = _identityDigest,
            },
        ]);
        _operations.Begin(PlanId, _planDigest, Kind, minted.RequestDigest, minted.OperationId);
        _operations.Authorize(minted.OperationId, CanonicalJson.Text(minted.Authorization),
            minted.HostReceiptId);

        // ACK semantics refuse a not-yet-committed operation ...
        var ackError = Assert.Throws<SourceAccessException>(
            () => _operations.PrepareCompletion(minted.OperationId));
        Assert.Equal("SOURCE_OPERATION_NOT_FOUND", ackError.Code);
        // ... recovery semantics (core-committed/host-authorized/failed) accept it.
        var material = _operations.PrepareCompletion(minted.OperationId, recovery: true);
        Assert.Equal(minted.OperationId, material.OperationId);
        Assert.Equal("host-authorized", AfterRestart().Get(minted.OperationId)!.State);
    }
}
