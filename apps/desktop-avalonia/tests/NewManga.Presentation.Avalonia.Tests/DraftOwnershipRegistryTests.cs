using System.Reflection;
using System.Runtime.CompilerServices;
using NewManga.Presentation.Avalonia.Windows;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-1: the window-layer <c>(SessionId, RegionId)</c> draft owner registry. Every
/// case exercises one mechanical clause of the frozen AC; the rules themselves are referenced from C-13
/// SC-D03 (<c>doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66</c>) and the frozen R4a interpretation
/// (<c>doc/tasks/FEA-07-RESIDUAL-2.md:45</c>), never restated as a second authority.
/// </summary>
public sealed class DraftOwnershipRegistryTests
{
    private static DraftKey Key(string session = "session-1", string region = "region-1") =>
        DraftKey.ForRegion(session, region);

    [Fact]
    public void FirstClaim_GrantsEditorAndAssignsDraftId()
    {
        var registry = new DraftOwnershipRegistry();

        var claim = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        Assert.Equal(DraftClaimStatus.Granted, claim.Status);
        Assert.True(claim.CanEdit);
        Assert.True(claim.IsEditable);
        Assert.False(string.IsNullOrWhiteSpace(claim.DraftId));
        Assert.Equal("window-main", claim.OwnerWindowToken);
        Assert.Equal("session-1", claim.OwnerSessionId);
        Assert.Equal(DraftDenialReason.None, claim.Denial);
        Assert.Equal(1, registry.Count);
    }

    [Fact]
    public void SameKeyFromSecondOsWindow_IsReadOnlyWithTypedDenial()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        var second = registry.TryClaim(Key(), "window-inspector", WindowRole.Inspector);

        Assert.Equal(DraftClaimStatus.ReadOnly, second.Status);
        Assert.False(second.CanEdit);
        Assert.Equal(DraftDenialReason.OtherWindowOwner, second.Denial);
        Assert.Equal(owner.DraftId, second.DraftId);
        Assert.Equal("window-main", second.OwnerWindowToken);
        Assert.Equal(1, registry.Count);
        Assert.Equal(owner.DraftId, registry.Snapshot().Single().DraftId);
    }

    [Fact]
    public void FloatingWindowClaim_IsAlwaysReadOnly_EvenAsFirstClaimer()
    {
        var registry = new DraftOwnershipRegistry();

        var claim = registry.TryClaim(Key(), "window-floating", WindowRole.Floating);

        Assert.Equal(DraftClaimStatus.ReadOnly, claim.Status);
        Assert.False(claim.CanEdit);
        Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, claim.Denial);
        Assert.Null(claim.DraftId);
        Assert.Equal(0, registry.Count);
        Assert.False(registry.TryGetOwnership(Key(), out _));
    }

    [Fact]
    public void FloatingWindowClaimOnOwnedKey_ReturnsOwnerDraftIdButStaysReadOnly()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        var floating = registry.TryClaim(Key(), "window-floating", WindowRole.Floating);

        Assert.Equal(DraftClaimStatus.ReadOnly, floating.Status);
        Assert.False(floating.CanEdit);
        Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, floating.Denial);
        Assert.Equal(owner.DraftId, floating.DraftId);
        Assert.Equal("window-main", floating.OwnerWindowToken);
    }

    [Fact]
    public void SameWindowPanels_ShareOneDraftIdWithoutRejection()
    {
        var registry = new DraftOwnershipRegistry();
        var first = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        var secondPanel = registry.TryClaim(Key(), "window-main", WindowRole.Main);
        var thirdPanel = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        Assert.Equal(DraftClaimStatus.Shared, secondPanel.Status);
        Assert.Equal(DraftClaimStatus.Shared, thirdPanel.Status);
        Assert.True(secondPanel.CanEdit);
        Assert.True(thirdPanel.CanEdit);
        Assert.Equal(DraftDenialReason.None, secondPanel.Denial);
        Assert.Equal(first.DraftId, secondPanel.DraftId);
        Assert.Equal(first.DraftId, thirdPanel.DraftId);
        Assert.Equal(1, registry.Count);
    }

    [Fact]
    public void PageLevelKeyWithoutRegion_IsClaimable()
    {
        var registry = new DraftOwnershipRegistry();
        var pageKey = DraftKey.ForPage("session-1");

        var claim = registry.TryClaim(pageKey, "window-main", WindowRole.Main);

        Assert.Equal(DraftClaimStatus.Granted, claim.Status);
        Assert.True(claim.CanEdit);
        Assert.Null(pageKey.RegionId);
        Assert.True(registry.TryGetOwnership(pageKey, out var ownership));
        Assert.Equal(claim.DraftId, ownership.DraftId);
    }

    [Fact]
    public void RegionKey_RejectsBlankIds()
    {
        var registry = new DraftOwnershipRegistry();

        Assert.ThrowsAny<ArgumentException>(() => registry.TryClaim(DraftKey.ForRegion(" ", "region-1"), "window-main", WindowRole.Main));
        Assert.ThrowsAny<ArgumentException>(() => registry.TryClaim(DraftKey.ForRegion("session-1", "  "), "window-main", WindowRole.Main));
        Assert.ThrowsAny<ArgumentException>(() => registry.TryClaim(Key(), " ", WindowRole.Main));
        Assert.ThrowsAny<ArgumentException>(() => registry.TryClaim(Key(), null!, WindowRole.Main));
    }

    [Fact]
    public void CrossSessionSameRegion_IsReadOnlyThenClaimableAfterOwnerRelease()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = registry.TryClaim(Key("session-a", "region-1"), "window-a", WindowRole.Main);

        var otherSession = registry.TryClaim(Key("session-b", "region-1"), "window-b", WindowRole.Main);

        Assert.Equal(DraftClaimStatus.ReadOnly, otherSession.Status);
        Assert.False(otherSession.CanEdit);
        Assert.Equal(DraftDenialReason.CrossSessionRegionOwner, otherSession.Denial);
        Assert.Equal("session-a", otherSession.OwnerSessionId);
        Assert.Equal(1, registry.Count);

        Assert.True(registry.Release(Key("session-a", "region-1"), "window-a"));
        var reclaimed = registry.TryClaim(Key("session-b", "region-1"), "window-b", WindowRole.Main);

        Assert.Equal(DraftClaimStatus.Granted, reclaimed.Status);
        Assert.True(reclaimed.CanEdit);
        Assert.NotEqual(owner.DraftId, reclaimed.DraftId);
    }

    [Fact]
    public void ExplicitTransfer_MovesOwnershipExclusivelyAndKeepsTheDraftId()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = registry.TryClaim(Key(), "window-main", WindowRole.Main);
        registry.RememberWindow("window-inspector", WindowRole.Inspector);

        var transfer = registry.RequestTransfer(Key(), "window-main", "window-inspector");
        var newOwnerClaim = registry.TryClaim(Key(), "window-inspector", WindowRole.Inspector);
        var oldOwnerClaim = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        Assert.Equal(DraftClaimStatus.Transferred, transfer.Status);
        Assert.True(transfer.CanEdit);
        Assert.Equal("window-inspector", transfer.OwnerWindowToken);
        Assert.Equal(owner.DraftId, transfer.DraftId);

        Assert.Equal(DraftClaimStatus.Shared, newOwnerClaim.Status);
        Assert.True(newOwnerClaim.CanEdit);
        Assert.Equal(owner.DraftId, newOwnerClaim.DraftId);

        Assert.Equal(DraftClaimStatus.ReadOnly, oldOwnerClaim.Status);
        Assert.Equal(DraftDenialReason.OtherWindowOwner, oldOwnerClaim.Denial);
        Assert.Equal(owner.DraftId, oldOwnerClaim.DraftId);
    }

    [Fact]
    public void ExplicitTransfer_IsIdempotent()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = registry.TryClaim(Key(), "window-main", WindowRole.Main);
        registry.RememberWindow("window-inspector", WindowRole.Inspector);

        var first = registry.RequestTransfer(Key(), "window-main", "window-inspector");
        var second = registry.RequestTransfer(Key(), "window-main", "window-inspector");
        var third = registry.RequestTransfer(Key(), "window-main", "window-inspector");

        Assert.Equal(DraftClaimStatus.Transferred, first.Status);
        Assert.Equal(DraftClaimStatus.Retained, second.Status);
        Assert.Equal(DraftClaimStatus.Retained, third.Status);
        // R1 P3-001: a repeat by the FORMER owner changes nothing and must not report edit rights,
        // otherwise a stale caller could believe it still owns the draft.
        Assert.False(second.CanEdit);
        Assert.False(third.CanEdit);
        Assert.Equal(DraftDenialReason.NotOwner, second.Denial);
        Assert.Equal(first.OwnerWindowToken, second.OwnerWindowToken);
        Assert.Equal(first.OwnerWindowToken, third.OwnerWindowToken);
        Assert.Equal(owner.DraftId, third.DraftId);
        Assert.Equal(1, registry.Count);

        // The current owner repeating the same request is the idempotent no-op with edit rights.
        var byNewOwner = registry.RequestTransfer(Key(), "window-inspector", "window-inspector");
        Assert.Equal(DraftClaimStatus.Retained, byNewOwner.Status);
        Assert.True(byNewOwner.CanEdit);
        Assert.Equal(DraftDenialReason.None, byNewOwner.Denial);
        Assert.Equal(owner.DraftId, byNewOwner.DraftId);

        // A transfer never creates a second draft row: the same key keeps exactly one draft id.
        var snapshot = registry.Snapshot();
        Assert.Single(snapshot);
        Assert.Equal(owner.DraftId, snapshot[0].DraftId);
        Assert.Equal("window-inspector", snapshot[0].OwnerWindowToken);
    }

    [Fact]
    public void ExplicitTransfer_ToUnknownWindow_IsTypedRefusalWithoutGuessingARole()
    {
        var registry = new DraftOwnershipRegistry();
        registry.TryClaim(Key(), "window-main", WindowRole.Main);

        // R1 P2-003: an unregistered token has no known role; the registry refuses typed instead of
        // falling back to "Main" and silently treating the target as editable.
        var transfer = registry.RequestTransfer(Key(), "window-main", "window-never-seen");

        Assert.Equal(DraftClaimStatus.ReadOnly, transfer.Status);
        Assert.False(transfer.CanEdit);
        Assert.Equal(DraftDenialReason.UnknownWindow, transfer.Denial);
        // R2-008: the diagnostic role field says Unknown instead of guessing an editable Main role.
        Assert.Equal(WindowRole.Unknown, transfer.WindowRole);
        Assert.Equal("window-main", registry.Snapshot().Single().OwnerWindowToken);
    }

    [Fact]
    public void ExplicitTransfer_ByNonOwner_IsTypedRefusalWithoutMutation()
    {
        var registry = new DraftOwnershipRegistry();
        registry.TryClaim(Key(), "window-main", WindowRole.Main);
        registry.RememberWindow("window-inspector", WindowRole.Inspector);

        var transfer = registry.RequestTransfer(Key(), "window-inspector", "window-inspector");

        Assert.Equal(DraftClaimStatus.ReadOnly, transfer.Status);
        Assert.False(transfer.CanEdit);
        Assert.Equal(DraftDenialReason.NotOwner, transfer.Denial);
        Assert.Equal("window-main", registry.Snapshot().Single().OwnerWindowToken);
    }

    [Fact]
    public void ExplicitTransfer_ToFloatingWindow_IsTypedRefusalWithoutMutation()
    {
        var registry = new DraftOwnershipRegistry();
        registry.TryClaim(Key(), "window-main", WindowRole.Main);
        var floating = registry.TryClaim(Key(), "window-floating", WindowRole.Floating);
        Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, floating.Denial);

        var transfer = registry.RequestTransfer(Key(), "window-main", "window-floating");

        Assert.Equal(DraftClaimStatus.ReadOnly, transfer.Status);
        Assert.False(transfer.CanEdit);
        Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, transfer.Denial);
        Assert.Equal("window-main", registry.Snapshot().Single().OwnerWindowToken);
    }

    [Fact]
    public void ExplicitTransfer_OfUnownedKey_IsTypedRefusal()
    {
        var registry = new DraftOwnershipRegistry();

        var transfer = registry.RequestTransfer(Key(), "window-main", "window-inspector");

        Assert.Equal(DraftClaimStatus.ReadOnly, transfer.Status);
        Assert.False(transfer.CanEdit);
        Assert.Equal(DraftDenialReason.UnknownKey, transfer.Denial);
        Assert.Equal(0, registry.Count);
    }

    [Fact]
    public void Release_ByOwnerAllowsReclaimWithFreshDraftId()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        Assert.True(registry.Release(Key(), "window-main"));
        Assert.Equal(0, registry.Count);
        Assert.False(registry.TryGetOwnership(Key(), out _));

        var reclaimed = registry.TryClaim(Key(), "window-inspector", WindowRole.Inspector);

        Assert.Equal(DraftClaimStatus.Granted, reclaimed.Status);
        Assert.True(reclaimed.CanEdit);
        Assert.NotEqual(owner.DraftId, reclaimed.DraftId);
        Assert.Equal(1, registry.Count);
    }

    [Fact]
    public void Release_ByNonOwner_IsRefusedAndKeepsOwner()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        Assert.False(registry.Release(Key(), "window-inspector"));
        Assert.Equal(1, registry.Count);
        Assert.True(registry.TryGetOwnership(Key(), out var ownership));
        Assert.Equal(owner.DraftId, ownership.DraftId);
        Assert.Equal("window-main", ownership.OwnerWindowToken);
        Assert.False(registry.Release(DraftKey.ForPage("session-1"), "window-main"));
    }

    [Fact]
    public void ConcurrentClaims_ProduceExactlyOneOwner()
    {
        var registry = new DraftOwnershipRegistry();
        const int contenders = 64;
        var results = new DraftOwnershipResult[contenders];

        Parallel.For(0, contenders, i => results[i] = registry.TryClaim(Key(), $"window-{i:D2}", WindowRole.Main));

        var editors = results.Where(result => result.CanEdit).ToArray();
        var owner = Assert.Single(editors);
        Assert.Equal(DraftClaimStatus.Granted, owner.Status);
        foreach (var other in results)
        {
            if (string.Equals(other.WindowToken, owner.WindowToken, StringComparison.Ordinal))
            {
                continue;
            }

            Assert.Equal(DraftClaimStatus.ReadOnly, other.Status);
            Assert.Equal(DraftDenialReason.OtherWindowOwner, other.Denial);
            Assert.Equal(owner.DraftId, other.DraftId);
        }

        var snapshot = registry.Snapshot();
        Assert.Single(snapshot);
        Assert.Equal(owner.DraftId, snapshot[0].DraftId);
        Assert.Equal(owner.WindowToken, snapshot[0].OwnerWindowToken);
    }

    [Fact]
    public void ConcurrentClaimsFromTheSameWindow_ShareOneDraftId()
    {
        var registry = new DraftOwnershipRegistry();
        const int panels = 32;
        var results = new DraftOwnershipResult[panels];

        Parallel.For(0, panels, i => results[i] = registry.TryClaim(Key(), "window-main", WindowRole.Main));

        Assert.All(results, result => Assert.True(result.CanEdit));
        Assert.Single(results.Select(result => result.DraftId).Distinct());
        Assert.Equal(1, registry.Count);
    }

    [Fact]
    public void ReadOnlyResult_TypedWriteGateThrowsWithoutChangingState()
    {
        var registry = new DraftOwnershipRegistry();
        var key = Key();
        var owner = registry.TryClaim(key, "window-main", WindowRole.Main);
        var readOnly = registry.TryClaim(key, "window-floating", WindowRole.Floating);
        var before = registry.Snapshot();

        var refusal = Assert.Throws<DraftWriteRejectedException>(() => readOnly.EnsureEditable());

        Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, refusal.Reason);
        Assert.Equal(key, refusal.Key);
        Assert.Same(readOnly, refusal.Ownership);
        Assert.Equal(owner.DraftId, registry.Snapshot().Single().DraftId);
        Assert.Equal(before[0], registry.Snapshot()[0]);
        Assert.NotNull(owner);
    }

    [Fact]
    public void EditableResult_TypedWriteGateDoesNotThrow()
    {
        var registry = new DraftOwnershipRegistry();
        var claim = registry.TryClaim(Key(), "window-main", WindowRole.Main);

        claim.EnsureEditable();
    }

    [Fact]
    public void ResultRecord_IsImmutableAndCarriesTypedDenial()
    {
        var properties = typeof(DraftOwnershipResult).GetProperties(BindingFlags.Public | BindingFlags.Instance);

        Assert.NotEmpty(properties);
        Assert.All(
            properties,
            property => Assert.True(
                property.SetMethod is null || property.SetMethod.ReturnParameter.GetRequiredCustomModifiers().Contains(typeof(IsExternalInit)),
                $"{property.Name} must be init-only so an ownership result cannot be rewritten"));
    }

    [Fact]
    public void Snapshot_IsAnImmutableCopyOrderedBySessionThenRegion()
    {
        var registry = new DraftOwnershipRegistry();
        registry.TryClaim(DraftKey.ForRegion("session-b", "region-1"), "window-b", WindowRole.Main);
        registry.TryClaim(DraftKey.ForRegion("session-a", "region-2"), "window-a", WindowRole.Main);
        registry.TryClaim(DraftKey.ForRegion("session-a", "region-3"), "window-a", WindowRole.Main);

        var snapshot = registry.Snapshot();
        registry.Release(DraftKey.ForRegion("session-a", "region-2"), "window-a");

        Assert.Equal(3, snapshot.Count);
        Assert.Equal(
            new[] { ("session-a", "region-2"), ("session-a", "region-3"), ("session-b", "region-1") },
            snapshot.Select(entry => (entry.Key.SessionId, entry.Key.RegionId ?? string.Empty)).ToArray());
        Assert.Equal(2, registry.Count);
    }

    [Fact]
    public void RepeatedRelease_IsIdempotentFalseAfterFirst()
    {
        var registry = new DraftOwnershipRegistry();
        registry.TryClaim(Key(), "window-main", WindowRole.Main);

        Assert.True(registry.Release(Key(), "window-main"));
        Assert.False(registry.Release(Key(), "window-main"));
        Assert.Equal(0, registry.Count);
    }
}
