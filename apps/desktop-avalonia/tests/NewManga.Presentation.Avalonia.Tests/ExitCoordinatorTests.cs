using NewManga.Presentation.Avalonia.Lifecycle;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>FEA-07 exit coordination: unsaved edits / active runs block process exit (§7.3).</summary>
public sealed class ExitCoordinatorTests
{
    [Fact]
    public void NoPendingWork_AllowsExit()
    {
        var coordinator = new ExitCoordinator();
        var decision = coordinator.RequestExit();
        Assert.True(decision.Allowed);
        Assert.Null(decision.Reason);
    }

    [Fact]
    public void PendingEdit_BlocksExitUntilCompleted()
    {
        var coordinator = new ExitCoordinator();
        coordinator.RegisterPendingEdit("shelf");
        Assert.False(coordinator.RequestExit().Allowed);

        Assert.True(coordinator.CompletePendingEdit("shelf"));
        Assert.True(coordinator.RequestExit().Allowed);
    }

    [Fact]
    public void ActiveRun_BlocksExitUntilCompleted()
    {
        var coordinator = new ExitCoordinator();
        coordinator.RegisterActiveRun("run-1");
        var decision = coordinator.RequestExit();
        Assert.False(decision.Allowed);
        Assert.Contains("active runs", decision.Reason);

        coordinator.CompleteActiveRun("run-1");
        Assert.True(coordinator.RequestExit().Allowed);
    }

    [Fact]
    public void DuplicateRegistration_IsRejected()
    {
        var coordinator = new ExitCoordinator();
        coordinator.RegisterPendingEdit("a");
        Assert.Throws<InvalidOperationException>(() => coordinator.RegisterPendingEdit("a"));
        coordinator.RegisterActiveRun("r");
        Assert.Throws<InvalidOperationException>(() => coordinator.RegisterActiveRun("r"));
    }

    [Fact]
    public void CompletingUnknownToken_ReturnsFalse()
    {
        var coordinator = new ExitCoordinator();
        Assert.False(coordinator.CompletePendingEdit("missing"));
        Assert.False(coordinator.CompleteActiveRun("missing"));
    }
}
