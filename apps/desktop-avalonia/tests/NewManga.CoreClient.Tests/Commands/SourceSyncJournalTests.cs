using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// FEA-11 (C-17 §5.2): the dispatcher must route the four operation-kind
/// source-sync writes through the Host-injected journal delegate, and must
/// leave every other command on its ordinary path. These tests use a fake
/// journal (no Core process, no real user data).
/// </summary>
public sealed class SourceSyncJournalTests
{
    [Theory]
    [InlineData("source_apply_sync_plan")]
    [InlineData("source_relink")]
    [InlineData("source_repoint")]
    [InlineData("source_resync")]
    public async Task OperationWrites_AreJournalWrapped(string command)
    {
        var calls = new List<(string Name, JsonElement Args)>();
        var dispatcher = new HostCommandDispatcher(
            bridge: null,
            hostLocal: null,
            journal: (name, args, call, _) =>
            {
                calls.Add((name, args.Clone()));
                return Task.FromResult(("op-test-" + name, JsonSerializer.SerializeToElement(
                    new Dictionary<string, object?> { ["operation_id"] = "op-test-" + name })));
            });

        using var args = JsonDocument.Parse(
            "{\"plan_id\":\"plan-1\",\"plan_digest\":\"" + new string('a', 64) + "\"}");
        var result = await dispatcher.InvokeAsync(command, args.RootElement.Clone());

        Assert.Equal(command, Assert.Single(calls).Name);
        Assert.True(result.Value.TryGetProperty("operation_id", out var operationId));
        Assert.Equal("op-test-" + command, operationId.GetString());
        Assert.True(result.Value.TryGetProperty("result", out _));
    }

    [Theory]
    [InlineData("source_scan_sync")]
    [InlineData("source_acknowledge_operation")]
    public async Task NonOperationWrites_AreNotJournalWrapped(string command)
    {
        var journalCalls = 0;
        var dispatcher = new HostCommandDispatcher(
            bridge: null,
            hostLocal: null,
            journal: (name, args, _, _) =>
            {
                journalCalls += 1;
                return Task.FromResult(("op", JsonSerializer.SerializeToElement(new { })));
            });

        await Assert.ThrowsAsync<NewManga.CoreClient.Diagnostics.SidecarException>(
            () => dispatcher.InvokeAsync(command, JsonSerializer.SerializeToElement(new { })));
        Assert.Equal(0, journalCalls);
    }
}
