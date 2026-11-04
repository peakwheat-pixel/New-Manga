using System.Text;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11 (C-17 §5.2): the Host durable operation journal. These are unit
/// tests over the journal/state machine only — the Core round-trips live in
/// the IPC tests (C4). They run entirely inside a scratch data root and never
/// touch real user data.
/// </summary>
public sealed class SourceOperationTests : IDisposable
{
    private readonly string root = Path.Combine(
        Path.GetTempPath(), "nm-fea11-ops-" + Guid.NewGuid().ToString("N"));

    public void Dispose()
    {
        try { if (Directory.Exists(root)) Directory.Delete(root, recursive: true); }
        catch { /* best effort */ }
    }

    private SourceOperationCoordinator NewCoordinator() =>
        new(null, root);

    [Fact]
    public void Begin_JournalsStartedEntry_BeforeAnyAuthorization()
    {
        var coordinator = NewCoordinator();
        var entry = coordinator.Begin("plan-1", new string('a', 64), "resync", new string('b', 64));

        Assert.Equal("started", entry.State);
        Assert.StartsWith("op-", entry.OperationId);
        var journalPath = Path.Combine(root, "host", "source-operations", entry.OperationId + ".v1.dat");
        Assert.True(File.Exists(journalPath));

        var bytes = File.ReadAllBytes(journalPath);
        Assert.True(bytes.AsSpan(0, SourceOperationCoordinator.Magic.Length)
            .SequenceEqual(Encoding.ASCII.GetBytes(SourceOperationCoordinator.Magic)));
        // DPAPI wrapped: the plan id must not be readable in the raw file.
        Assert.DoesNotContain("plan-1", Encoding.UTF8.GetString(bytes), StringComparison.Ordinal);

        var loaded = coordinator.Get(entry.OperationId);
        Assert.NotNull(loaded);
        Assert.Equal(entry.PlanId, loaded!.PlanId);
        Assert.Equal(entry.PlanDigest, loaded.PlanDigest);
        Assert.Equal(entry.RequestDigest, loaded.RequestDigest);
    }

    [Fact]
    public void Journal_SurvivesProcessRestart()
    {
        var first = NewCoordinator();
        var entry = first.Begin("plan-2", new string('c', 64), "relink", new string('d', 64));
        var authorized = first.Authorize(entry.OperationId, "{\"grant\":1}", "receipt-1");
        Assert.Equal("host-authorized", authorized.State);
        Assert.Equal("receipt-1", authorized.HostReceiptId);
        Assert.Equal(64, authorized.AuthorizationDigest!.Length);

        // A fresh coordinator over the same data root reads the journal back.
        var second = NewCoordinator();
        var loaded = second.Get(entry.OperationId);
        Assert.NotNull(loaded);
        Assert.Equal("host-authorized", loaded!.State);
        Assert.Equal(authorized.AuthorizationDigest, loaded.AuthorizationDigest);
    }

    [Fact]
    public async Task IllegalStateTransitions_AreTypedRefusals()
    {
        var coordinator = NewCoordinator();
        var entry = coordinator.Begin("plan-3", new string('e', 64), "repoint", new string('f', 64));

        // Acknowledge before commit is refused (never a silent Core call).
        await Assert.ThrowsAsync<SourceAccessException>(() => coordinator.AcknowledgeAsync(entry.OperationId));
        // Recover before a commit is refused as well.
        await Assert.ThrowsAsync<SourceAccessException>(() => coordinator.RecoverAsync(entry.OperationId));

        coordinator.Authorize(entry.OperationId, "{}", "receipt-2");
        // Authorize twice is refused (started-only transition).
        Assert.Throws<SourceAccessException>(() =>
            coordinator.Authorize(entry.OperationId, "{}", "receipt-3"));
        Assert.Null(coordinator.Get("op-does-not-exist"));
        Assert.Throws<SourceAccessException>(() => coordinator.Get("../escape"));
    }

    [Fact]
    public void FailureRecord_IsTerminalAndIdempotent()
    {
        var coordinator = NewCoordinator();
        var entry = coordinator.Begin("plan-4", new string('1', 64), "resync", new string('2', 64));
        coordinator.MarkFailed(entry.OperationId);
        var failed = coordinator.Get(entry.OperationId);
        Assert.Equal("failed", failed!.State);
        // Re-marking is a no-op, not a refusal.
        Assert.Equal("failed", coordinator.MarkFailed(entry.OperationId).State);
    }

    [Fact]
    public void ReusedOperationId_CannotOverwriteJournalState()
    {
        var coordinator = NewCoordinator();
        var entry = coordinator.Begin("plan-5", new string('3', 64), "resync", new string('4', 64));
        coordinator.Authorize(entry.OperationId, "{\"host_receipt_id\":\"r\"}", "r");
        coordinator.MarkCommitted(entry.OperationId, new string('5', 64));

        // A second Begin with the same operation id is refused (r2 P2-6).
        Assert.Throws<SourceAccessException>(() => coordinator.Begin(
            "plan-5", new string('3', 64), "resync", new string('4', 64),
            entry.OperationId));
        Assert.Equal("core-committed", coordinator.Get(entry.OperationId)!.State);
    }
}
