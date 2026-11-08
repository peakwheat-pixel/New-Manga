using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.CoreClient;
using NewManga.Presentation.Avalonia.Switching;
using NewManga.Presentation.Avalonia.Windows;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-1 at the window layer: <see cref="PresentationWindow"/> exposes its own
/// <see cref="DraftOwnershipScope"/>, a <see cref="WindowRole.Floating"/> window is constructed read-only,
/// a second OS window gets a typed read-only claim, the same window's panels share one draft id, and a
/// read-only write attempt is refused typed before any Host write exists. The ownership rules are
/// referenced from C-13 SC-D03 (<c>doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66</c>) and the frozen
/// R4a interpretation (<c>doc/tasks/FEA-07-RESIDUAL-2.md:45</c>) — never restated here.
/// </summary>
public sealed class DraftOwnershipWindowTests : IDisposable
{
    private static readonly DraftKey Key = DraftKey.ForRegion("session-1", "region-1");

    private readonly string _root;
    private readonly AppearanceCoordinator _appearance;
    private readonly SwitchJournal _journal;

    public DraftOwnershipWindowTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-draft-window-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
        _appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        _appearance.Reload();
        _journal = new SwitchJournal(Path.Combine(_root, "switch-journal.json"));
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    private static Border Content(string id, string marker) => new()
    {
        Child = new TextBlock { Text = $"{marker}:{id}" },
    };

    private PresentationWindow CreateWindow(
        DraftOwnershipRegistry? registry = null,
        WindowRole role = WindowRole.Main,
        IHostController? host = null)
    {
        var options = AppOptions.Parse(Array.Empty<string>());
        return new PresentationWindow(
            options,
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: host,
            _appearance,
            _journal,
            id => Content(id, "hosted"),
            role: role,
            drafts: registry);
    }

    [AvaloniaFact]
    public void Window_ExposesItsOwnDraftOwnershipIdentity()
    {
        var first = CreateWindow();
        var second = CreateWindow();
        try
        {
            Assert.NotNull(first.DraftOwnership);
            Assert.Equal(WindowRole.Main, first.DraftOwnership.Role);
            Assert.True(first.DraftOwnership.CanEdit);
            Assert.False(string.IsNullOrWhiteSpace(first.WindowToken));
            Assert.Equal(first.WindowToken, first.Broker.Main!.Token);
            Assert.Equal(first.WindowToken, first.DraftOwnership.WindowToken);
            Assert.NotEqual(first.WindowToken, second.WindowToken);
            Assert.NotEqual(first.Broker.Main!.Token, second.Broker.Main!.Token);
        }
        finally
        {
            first.Close();
            second.Close();
        }
    }

    [AvaloniaFact]
    public void FloatingWindow_IsConstructedReadOnly()
    {
        var floating = CreateWindow(role: WindowRole.Floating);
        try
        {
            Assert.Equal(WindowRole.Floating, floating.DraftOwnership.Role);
            Assert.False(floating.DraftOwnership.CanEdit);

            var claim = floating.DraftOwnership.TryClaimDraft(Key);

            Assert.Equal(DraftClaimStatus.ReadOnly, claim.Status);
            Assert.False(claim.CanEdit);
            Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, claim.Denial);
            Assert.Null(claim.DraftId);
        }
        finally
        {
            floating.Close();
        }
    }

    [AvaloniaFact]
    public void SecondOsWindowClaim_IsReadOnlyWithTheOwnerDraftId()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = CreateWindow(registry);
        var second = CreateWindow(registry);
        try
        {
            var firstClaim = owner.DraftOwnership.TryClaimDraft(Key);
            var secondClaim = second.DraftOwnership.TryClaimDraft(Key);

            Assert.Equal(DraftClaimStatus.Granted, firstClaim.Status);
            Assert.True(firstClaim.CanEdit);
            Assert.Equal(DraftClaimStatus.ReadOnly, secondClaim.Status);
            Assert.False(secondClaim.CanEdit);
            Assert.Equal(DraftDenialReason.OtherWindowOwner, secondClaim.Denial);
            Assert.Equal(firstClaim.DraftId, secondClaim.DraftId);
            Assert.Equal(owner.WindowToken, secondClaim.OwnerWindowToken);
            Assert.Equal(1, registry.Count);
        }
        finally
        {
            owner.Close();
            second.Close();
        }
    }

    [AvaloniaFact]
    public void SameWindowPanels_ShareOneDraftIdWithoutRejection()
    {
        var registry = new DraftOwnershipRegistry();
        var window = CreateWindow(registry);
        try
        {
            var mainCanvas = window.DraftOwnership.TryClaimDraft(Key);
            var floatingPanel = window.DraftOwnership.TryClaimDraft(Key);

            Assert.Equal(DraftClaimStatus.Granted, mainCanvas.Status);
            Assert.Equal(DraftClaimStatus.Shared, floatingPanel.Status);
            Assert.True(floatingPanel.CanEdit);
            Assert.Equal(DraftDenialReason.None, floatingPanel.Denial);
            Assert.Equal(mainCanvas.DraftId, floatingPanel.DraftId);
            Assert.Equal(1, registry.Count);
        }
        finally
        {
            window.Close();
        }
    }

    [AvaloniaFact]
    public async Task ReadOnlyWindowWrite_IsRefusedTypedBeforeAnyHostWrite()
    {
        var registry = new DraftOwnershipRegistry();
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book-a"));
        var owner = CreateWindow(registry, host: host);
        var floating = CreateWindow(registry, WindowRole.Floating, host);
        try
        {
            var ownerClaim = owner.DraftOwnership.TryClaimDraft(Key);
            var readOnlyClaim = floating.DraftOwnership.TryClaimDraft(Key);
            Assert.True(ownerClaim.CanEdit);
            Assert.False(readOnlyClaim.CanEdit);

            var writeAttempts = 0;
            async Task WriteAsync(PresentationWindow window, DraftOwnershipResult claim)
            {
                // The typed gate is the only path to a Host draft write in this pipeline, so a refusal
                // here means nothing reached the Host (the fake records every open/patch/discard frame).
                window.DraftOwnership.EnsureWritable(claim);
                writeAttempts++;
                await host.PatchDraftAsync(
                    claim.DraftId!,
                    Key.SessionId,
                    new DraftPatchRequest(new Dictionary<string, object?> { ["text"] = "edited" }));
            }

            var refusal = await Assert.ThrowsAsync<DraftWriteRejectedException>(
                () => WriteAsync(floating, readOnlyClaim));

            Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, refusal.Reason);
            Assert.Equal(0, writeAttempts);
            Assert.Empty(host.DraftWriteLog);
            Assert.Equal(0, host.StartCalls);
            Assert.Equal(0, host.DisposeCalls);

            // Control: the owning window passes the same gate and its write does reach the Host once.
            await WriteAsync(owner, ownerClaim);
            Assert.Equal(1, writeAttempts);
            Assert.Equal("patch", Assert.Single(host.DraftWriteLog));
        }
        finally
        {
            owner.Close();
            floating.Close();
        }
    }

    [AvaloniaFact]
    public void ExplicitTransferBetweenWindows_MovesOwnershipExclusively()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = CreateWindow(registry);
        var target = CreateWindow(registry);
        try
        {
            var claim = owner.DraftOwnership.TryClaimDraft(Key);
            Assert.True(claim.CanEdit);

            var transfer = owner.DraftOwnership.RequestDraftTransfer(Key, target.WindowToken);
            var idempotent = owner.DraftOwnership.RequestDraftTransfer(Key, target.WindowToken);

            Assert.Equal(DraftClaimStatus.Transferred, transfer.Status);
            Assert.True(transfer.CanEdit);
            Assert.Equal(DraftClaimStatus.Retained, idempotent.Status);
            // R1 P3-001: the former owner repeating the request must not be told it may still write.
            Assert.False(idempotent.CanEdit);
            Assert.Equal(DraftDenialReason.NotOwner, idempotent.Denial);
            Assert.Equal(claim.DraftId, transfer.DraftId);
            Assert.Equal(target.WindowToken, transfer.OwnerWindowToken);

            var targetClaim = target.DraftOwnership.TryClaimDraft(Key);
            var previousOwnerClaim = owner.DraftOwnership.TryClaimDraft(Key);

            Assert.True(targetClaim.CanEdit);
            Assert.Equal(claim.DraftId, targetClaim.DraftId);
            Assert.Equal(DraftClaimStatus.ReadOnly, previousOwnerClaim.Status);
            Assert.Equal(DraftDenialReason.OtherWindowOwner, previousOwnerClaim.Denial);
            Assert.Equal(1, registry.Count);
        }
        finally
        {
            owner.Close();
            target.Close();
        }
    }

    [AvaloniaFact]
    public void TransferToAConstructedButUnclaimedFloatingWindow_IsRefusedAndTheOwnerKeepsEdit()
    {
        var registry = new DraftOwnershipRegistry();
        var owner = CreateWindow(registry);
        // R1 P2-003 ordering case: the floating window is constructed but never claims anything.
        var floating = CreateWindow(registry, WindowRole.Floating);
        try
        {
            var claim = owner.DraftOwnership.TryClaimDraft(Key);
            Assert.True(claim.CanEdit);

            var transfer = owner.DraftOwnership.RequestDraftTransfer(Key, floating.WindowToken);

            Assert.Equal(DraftClaimStatus.ReadOnly, transfer.Status);
            Assert.False(transfer.CanEdit);
            Assert.Equal(DraftDenialReason.FloatingWindowReadOnly, transfer.Denial);
            // The original owner was not robbed of the draft.
            Assert.True(registry.IsCurrentOwner(Key, owner.WindowToken));
            Assert.False(registry.IsCurrentOwner(Key, floating.WindowToken));
            var ownerClaim = owner.DraftOwnership.TryClaimDraft(Key);
            Assert.True(ownerClaim.CanEdit);
            Assert.Equal(claim.DraftId, ownerClaim.DraftId);
        }
        finally
        {
            owner.Close();
            floating.Close();
        }
    }

    [AvaloniaFact]
    public void ReleaseThroughTheWindow_AllowsReclaim()
    {
        var registry = new DraftOwnershipRegistry();
        var window = CreateWindow(registry);
        try
        {
            var claim = window.DraftOwnership.TryClaimDraft(Key);
            Assert.True(claim.CanEdit);

            Assert.True(window.DraftOwnership.ReleaseDraft(Key));
            Assert.False(window.DraftOwnership.ReleaseDraft(Key));
            Assert.Equal(0, registry.Count);

            var reclaimed = window.DraftOwnership.TryClaimDraft(Key);
            Assert.Equal(DraftClaimStatus.Granted, reclaimed.Status);
            Assert.True(reclaimed.CanEdit);
            Assert.NotEqual(claim.DraftId, reclaimed.DraftId);
        }
        finally
        {
            window.Close();
        }
    }
}
