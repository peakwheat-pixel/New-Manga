using NewManga.Presentation.Avalonia.Windows;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-1 (r1 rework): the window-scoped view registers its role at construction, so an
/// explicit transfer target never has to be guessed, and the typed write gate is bound to the scope's window
/// identity plus the live owner (a stale result from before a transfer is refused). Rules are referenced from
/// C-13 SC-D03 (<c>doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66</c>), never restated here.
/// </summary>
public sealed class DraftOwnershipScopeTests
{
    private static readonly DraftKey Key = DraftKey.ForRegion("session-1", "region-1");

    private static (DraftOwnershipScope Scope, WindowBroker Broker) CreateScope(
        DraftOwnershipRegistry registry,
        string windowToken,
        WindowRole role)
    {
        var broker = new WindowBroker(registry);
        broker.RegisterMain(windowToken);
        return (new DraftOwnershipScope(broker, windowToken, role), broker);
    }

    [Fact]
    public void ScopeRegistersItsRoleAtConstruction_SoAFloatingTransferTargetIsRefusedBeforeAnyClaim()
    {
        var registry = new DraftOwnershipRegistry();
        var (owner, _) = CreateScope(registry, "window-main", WindowRole.Main);
        // The floating window is only CONSTRUCTED here — it never claims anything.
        var (floating, _) = CreateScope(registry, "window-floating", WindowRole.Floating);

        var claim = owner.TryClaimDraft(Key);
        Assert.True(claim.CanEdit);

        var transfer = owner.RequestDraftTransfer(Key, floating.WindowToken);

        // R1 P2-003: the constructed role is already known, so the transfer is refused as read-only
        // instead of guessing "Main" for a never-claimed token and handing it edit rights.
        Assert.Equal(DraftClaimStatus.ReadOnly, transfer.Status);
        Assert.False(transfer.CanEdit);
        Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, transfer.Denial);
        Assert.True(registry.IsCurrentOwner(Key, "window-main"));
        Assert.True(owner.TryClaimDraft(Key).CanEdit);
        Assert.False(floating.TryClaimDraft(Key).CanEdit);
        Assert.False(floating.CanEdit);
    }

    [Fact]
    public void EnsureWritable_AcceptsTheCurrentOwnerResult()
    {
        var registry = new DraftOwnershipRegistry();
        var (scope, _) = CreateScope(registry, "window-main", WindowRole.Main);
        var claim = scope.TryClaimDraft(Key);

        scope.EnsureWritable(claim);

        Assert.True(claim.CanEdit);
        Assert.True(registry.IsCurrentOwner(Key, scope.WindowToken));
    }

    [Fact]
    public void EnsureWritable_RejectsAResultIssuedToAnotherWindow()
    {
        var registry = new DraftOwnershipRegistry();
        var (owner, _) = CreateScope(registry, "window-main", WindowRole.Main);
        var (other, _) = CreateScope(registry, "window-other", WindowRole.Main);
        var claim = owner.TryClaimDraft(Key);

        var refusal = Assert.Throws<DraftWriteRejectedException>(() => other.EnsureWritable(claim));

        Assert.Equal(DraftDenialReason.NotOwner, refusal.Reason);
        Assert.Equal(Key, refusal.Key);
        Assert.Equal("window-main", refusal.Ownership.OwnerWindowToken);
        Assert.True(registry.IsCurrentOwner(Key, "window-main"));
    }

    [Fact]
    public void EnsureWritable_RejectsAStaleResultAfterATransfer()
    {
        var registry = new DraftOwnershipRegistry();
        var (owner, _) = CreateScope(registry, "window-main", WindowRole.Main);
        var (target, _) = CreateScope(registry, "window-inspector", WindowRole.Inspector);
        var claim = owner.TryClaimDraft(Key);
        Assert.True(claim.CanEdit);

        var transfer = owner.RequestDraftTransfer(Key, target.WindowToken);
        Assert.Equal(DraftClaimStatus.Transferred, transfer.Status);

        // R1 P3-010: the pre-transfer result must not still open the Host write path.
        var refusal = Assert.Throws<DraftWriteRejectedException>(() => owner.EnsureWritable(claim));

        Assert.Equal(DraftDenialReason.NotOwner, refusal.Reason);
        Assert.True(registry.IsCurrentOwner(Key, target.WindowToken));
        Assert.False(registry.IsCurrentOwner(Key, owner.WindowToken));

        var refreshed = target.TryClaimDraft(Key);
        target.EnsureWritable(refreshed);
        Assert.True(refreshed.CanEdit);
    }

    [Fact]
    public void TransferToAConstructedButUnclaimedInspectorWindow_IsAllowedAndKeepsIdentity()
    {
        var registry = new DraftOwnershipRegistry();
        var (owner, _) = CreateScope(registry, "window-main", WindowRole.Main);
        var (inspector, _) = CreateScope(registry, "window-inspector", WindowRole.Inspector);
        var claim = owner.TryClaimDraft(Key);

        var transfer = owner.RequestDraftTransfer(Key, inspector.WindowToken);

        Assert.Equal(DraftClaimStatus.Transferred, transfer.Status);
        Assert.True(transfer.CanEdit);
        Assert.Equal(claim.DraftId, transfer.DraftId);
        inspector.EnsureWritable(inspector.TryClaimDraft(Key));
        Assert.Throws<DraftWriteRejectedException>(() => owner.EnsureWritable(claim));
    }

    [Fact]
    public void EnsureWritable_RejectsAStaleResultAfterReleaseAndReclaim()
    {
        var registry = new DraftOwnershipRegistry();
        var (scope, _) = CreateScope(registry, "window-main", WindowRole.Main);
        var staleClaim = scope.TryClaimDraft(Key);
        Assert.True(staleClaim.CanEdit);

        Assert.True(scope.ReleaseDraft(Key));
        var reclaimed = scope.TryClaimDraft(Key);
        Assert.True(reclaimed.CanEdit);
        Assert.NotEqual(staleClaim.DraftId, reclaimed.DraftId);

        // R2-005: same window, but a different draft identity — the pre-release result must not write.
        var refusal = Assert.Throws<DraftWriteRejectedException>(() => scope.EnsureWritable(staleClaim));

        Assert.Equal(DraftDenialReason.NotOwner, refusal.Reason);
        scope.EnsureWritable(reclaimed);
    }
}
