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

    private JsonElement CallerPayload()
    {
        var known = _registry.List().Single();
        return JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["plan_id"] = "pl-1",
            ["plan_digest"] = new string('a', 64),
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
    public async Task Apply_KeepsHostAuthorizedStateWhenTheCoreCallFails()
    {
        var orchestrator = NewOrchestrator();
        var payload = CallerPayload();

        await Assert.ThrowsAsync<CoreOperationException>(() => orchestrator.ApplyAsync(
            "source_resync", payload,
            (_, _) => throw new CoreOperationException(
                "SOURCE_ACCESS_DENIED", "protocol", false, "denied", null),
            CancellationToken.None));

        var entries = Directory.GetFiles(Path.Combine(_root, "host", "source-operations"), "*.dat");
        Assert.Single(entries);
        var operationId = Path.GetFileName(entries[0])
            .Replace(".v1.dat", string.Empty, StringComparison.Ordinal);
        Assert.Equal("host-authorized", _operations.Get(operationId)!.State);
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
}
