using NewManga.Presentation.Avalonia.Windows;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-1: the window broker stays a thin forwarder — it adds no second ownership
/// authority and keeps its existing registration API untouched while exposing
/// <c>TryClaimDraft</c>/<c>ReleaseDraft</c>/<c>RequestDraftTransfer</c>.
/// </summary>
public sealed class WindowBrokerDraftForwardingTests
{
    private static readonly DraftKey Key = DraftKey.ForRegion("session-1", "region-1");

    [Fact]
    public void BrokerForwardsClaimsToItsRegistry()
    {
        var registry = new DraftOwnershipRegistry();
        var broker = new WindowBroker(registry);
        broker.RegisterMain("window-main");

        var claim = broker.TryClaimDraft(Key, "window-main", WindowRole.Main);

        Assert.Same(registry, broker.Drafts);
        Assert.Equal(DraftClaimStatus.Granted, claim.Status);
        Assert.True(claim.CanEdit);
        Assert.True(registry.TryGetOwnership(Key, out var ownership));
        Assert.Equal(claim.DraftId, ownership.DraftId);
    }

    [Fact]
    public void DefaultConstructor_KeepsOneRegistryPerBroker()
    {
        var first = new WindowBroker();
        var second = new WindowBroker();

        var firstClaim = first.TryClaimDraft(Key, "window-main", WindowRole.Main);
        var secondClaim = second.TryClaimDraft(Key, "window-other", WindowRole.Main);

        Assert.NotSame(first.Drafts, second.Drafts);
        Assert.Equal(DraftClaimStatus.Granted, firstClaim.Status);
        Assert.Equal(DraftClaimStatus.Granted, secondClaim.Status);
        Assert.True(firstClaim.CanEdit && secondClaim.CanEdit);
        Assert.Equal(1, first.Drafts.Count);
        Assert.Equal(1, second.Drafts.Count);
    }

    [Fact]
    public void SharedRegistryAcrossBrokers_KeepsASingleOwner()
    {
        var registry = new DraftOwnershipRegistry();
        var main = new WindowBroker(registry);
        main.RegisterMain("window-main");
        var floating = new WindowBroker(registry);
        floating.RegisterMain("window-floating");

        var owner = main.TryClaimDraft(Key, "window-main", WindowRole.Main);
        var second = floating.TryClaimDraft(Key, "window-floating", WindowRole.Main);

        Assert.Equal(DraftClaimStatus.Granted, owner.Status);
        Assert.Equal(DraftClaimStatus.ReadOnly, second.Status);
        Assert.Equal(DraftDenialReason.OtherWindowOwner, second.Denial);
        Assert.Equal(owner.DraftId, second.DraftId);
        Assert.Equal(1, registry.Count);
    }

    [Fact]
    public void BrokerForwardsReleaseAndTransfer()
    {
        var registry = new DraftOwnershipRegistry();
        var broker = new WindowBroker(registry);
        broker.RegisterMain("window-main");
        registry.RememberWindow("window-inspector", WindowRole.Inspector);
        broker.TryClaimDraft(Key, "window-main", WindowRole.Main);

        var transfer = broker.RequestDraftTransfer(Key, "window-main", "window-inspector");

        Assert.Equal(DraftClaimStatus.Transferred, transfer.Status);
        Assert.Equal("window-inspector", registry.Snapshot().Single().OwnerWindowToken);

        Assert.False(broker.ReleaseDraft(Key, "window-main"));
        Assert.True(broker.ReleaseDraft(Key, "window-inspector"));
        Assert.Equal(0, registry.Count);
    }

    [Fact]
    public void BrokerWithNullRegistry_IsRejected()
    {
        Assert.Throws<ArgumentNullException>(() => new WindowBroker(null!));
    }
}
