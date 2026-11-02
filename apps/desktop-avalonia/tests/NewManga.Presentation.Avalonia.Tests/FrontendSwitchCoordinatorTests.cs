using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>FEA-07 switch transaction: stage order, per-stage fault rollback and recovery (§7.1/§15.5).</summary>
public sealed class FrontendSwitchCoordinatorTests : IDisposable
{
    private readonly string _root = TempRoot.Create("switch");

    public void Dispose() => TempRoot.Delete(_root);

    private string JournalPath => Path.Combine(_root, "switch-journal.json");

    private static SwitchRequest Request() => new("builtin.fluent", "builtin.current-v2");

    [Fact]
    public async Task HappyPath_CommitsAndClearsJournal()
    {
        var journal = new SwitchJournal(JournalPath);
        var stages = new List<SwitchStage>();
        var committed = false;
        var coordinator = new FrontendSwitchCoordinator(journal);
        var callbacks = new SwitchCallbacks
        {
            ValidateAsync = _ => Task.CompletedTask,
            BuildTreeAsync = _ => Task.CompletedTask,
            CommitAsync = _ =>
            {
                committed = true;
                return Task.CompletedTask;
            },
            RollbackAsync = _ => Task.CompletedTask,
            OnStage = stages.Add,
        };

        var result = await coordinator.SwitchAsync(Request(), callbacks);

        Assert.True(result.Succeeded);
        Assert.Equal(SwitchStage.Committed, result.FinalStage);
        Assert.True(committed);
        Assert.False(File.Exists(JournalPath));
        Assert.Contains(SwitchStage.Preparing, stages);
        Assert.Contains(SwitchStage.Building, stages);
        Assert.Contains(SwitchStage.Committed, stages);
    }

    [Theory]
    [InlineData(SwitchStage.Preparing)]
    [InlineData(SwitchStage.Building)]
    [InlineData(SwitchStage.Layout)]
    [InlineData(SwitchStage.Loaded)]
    [InlineData(SwitchStage.Rendered)]
    [InlineData(SwitchStage.Committed)]
    public async Task FailureAtAnyStage_RollsBackToPreviousUi(SwitchStage failingStage)
    {
        var journal = new SwitchJournal(JournalPath);
        var rollbacks = 0;
        var coordinator = new FrontendSwitchCoordinator(
            journal,
            faultInjector: stage => stage == failingStage ? new InvalidOperationException("injected") : null);
        var callbacks = new SwitchCallbacks
        {
            ValidateAsync = _ => Task.CompletedTask,
            BuildTreeAsync = _ => Task.CompletedTask,
            CommitAsync = _ => Task.CompletedTask,
            RollbackAsync = _ =>
            {
                rollbacks++;
                return Task.CompletedTask;
            },
        };

        var result = await coordinator.SwitchAsync(Request(), callbacks);

        Assert.False(result.Succeeded);
        Assert.Equal(failingStage, result.FinalStage);
        Assert.True(result.RolledBack);
        Assert.Equal(1, rollbacks);
        Assert.True(journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        Assert.Contains("injected", entry.Failure);
    }

    [Fact]
    public async Task RollbackFailure_StillReportsFailure()
    {
        var journal = new SwitchJournal(JournalPath);
        var coordinator = new FrontendSwitchCoordinator(journal);
        var callbacks = new SwitchCallbacks
        {
            ValidateAsync = _ => Task.CompletedTask,
            BuildTreeAsync = _ => Task.CompletedTask,
            CommitAsync = _ => throw new InvalidOperationException("commit failed"),
            RollbackAsync = _ => throw new InvalidOperationException("rollback also failed"),
        };

        var result = await coordinator.SwitchAsync(Request(), callbacks);

        Assert.False(result.Succeeded);
        Assert.False(result.RolledBack);
        Assert.Contains("commit failed", result.Failure);
    }

    [Fact]
    public async Task ConcurrentSwitches_AreSerialized()
    {
        var journal = new SwitchJournal(JournalPath);
        var coordinator = new FrontendSwitchCoordinator(journal);
        var order = new List<string>();
        SwitchCallbacks Callbacks(string id) => new()
        {
            ValidateAsync = _ =>
            {
                order.Add(id + ":validate");
                return Task.CompletedTask;
            },
            BuildTreeAsync = async _ =>
            {
                order.Add(id + ":build");
                await Task.Delay(20);
            },
            CommitAsync = _ =>
            {
                order.Add(id + ":commit");
                return Task.CompletedTask;
            },
            RollbackAsync = _ => Task.CompletedTask,
        };

        var first = coordinator.SwitchAsync(new SwitchRequest("builtin.fluent", "builtin.current-v2"), Callbacks("a"));
        var second = coordinator.SwitchAsync(new SwitchRequest("builtin.current-v2", "builtin.fluent"), Callbacks("b"));
        await Task.WhenAll(first, second);

        Assert.Equal(new[] { "a:validate", "a:build", "a:commit", "b:validate", "b:build", "b:commit" }, order);
    }

    [Fact]
    public void TryRecoverInterrupted_SeesInFlightJournal()
    {
        var journal = new SwitchJournal(JournalPath);
        journal.Begin("builtin.fluent");
        journal.Advance(SwitchStage.Rendered);
        var coordinator = new FrontendSwitchCoordinator(journal);

        Assert.True(coordinator.TryRecoverInterrupted(out var entry));
        Assert.Equal(SwitchStage.Rendered, entry!.Stage);
    }
}
