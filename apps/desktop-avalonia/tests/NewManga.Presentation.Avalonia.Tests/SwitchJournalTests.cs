using NewManga.Presentation.Avalonia.Switching;

namespace NewManga.Presentation.Avalonia.Tests;

/// <summary>FEA-07 switch journal: durable stage tracking, rollback and crash recovery (proposal §7.1).</summary>
public sealed class SwitchJournalTests : IDisposable
{
    private readonly string _root = TempRoot.Create("journal");

    public void Dispose() => TempRoot.Delete(_root);

    private string JournalPath => Path.Combine(_root, "switch-journal.json");

    [Fact]
    public void BeginAndAdvance_PersistsEveryStage()
    {
        var journal = new SwitchJournal(JournalPath);
        journal.Begin("builtin.fluent");

        Assert.True(File.Exists(JournalPath));
        Assert.True(journal.TryRead(out var entry, out var error), error);
        Assert.Equal(SwitchStage.Preparing, entry!.Stage);
        Assert.Equal("builtin.fluent", entry.TargetFrontendId);

        journal.Advance(SwitchStage.Building);
        journal.Advance(SwitchStage.Layout);
        Assert.True(journal.TryRead(out entry, out _));
        Assert.Equal(SwitchStage.Layout, entry!.Stage);
    }

    [Fact]
    public void Commit_RemovesTheJournal()
    {
        var journal = new SwitchJournal(JournalPath);
        journal.Begin("builtin.fluent");
        journal.Advance(SwitchStage.Building);
        journal.Commit();

        Assert.False(File.Exists(JournalPath));
        Assert.False(journal.TryRead(out _, out _));
    }

    [Fact]
    public void Rollback_KeepsTerminalEntryAndFailure()
    {
        var journal = new SwitchJournal(JournalPath);
        journal.Begin("builtin.fluent");
        journal.Advance(SwitchStage.Building);
        journal.Rollback("Building: injected failure");

        Assert.True(journal.TryRead(out var entry, out _));
        Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        Assert.Contains("injected failure", entry.Failure);
        Assert.False(journal.HasInterruptedSwitch(out _));
    }

    [Fact]
    public void InFlightStage_IsRecoverable()
    {
        var journal = new SwitchJournal(JournalPath);
        journal.Begin("builtin.current-v2");
        journal.Advance(SwitchStage.Rendered);

        Assert.True(journal.HasInterruptedSwitch(out var entry));
        Assert.Equal(SwitchStage.Rendered, entry!.Stage);
    }

    [Fact]
    public void CorruptJournal_IsTreatedAsMissing()
    {
        File.WriteAllText(JournalPath, "{ not json");
        var journal = new SwitchJournal(JournalPath);

        Assert.False(journal.TryRead(out _, out var error));
        Assert.NotNull(error);
        Assert.False(journal.HasInterruptedSwitch(out _));
    }

    [Fact]
    public void AdvanceBackwards_Throws()
    {
        var journal = new SwitchJournal(JournalPath);
        journal.Begin("builtin.fluent");
        journal.Advance(SwitchStage.Layout);

        Assert.Throws<InvalidOperationException>(() => journal.Advance(SwitchStage.Building));
    }

    [Fact]
    public void AdvanceWithoutActiveEntry_Throws()
    {
        var journal = new SwitchJournal(JournalPath);
        Assert.Throws<InvalidOperationException>(() => journal.Advance(SwitchStage.Building));
    }
}

internal static class TempRoot
{
    public static string Create(string label)
    {
        var path = Path.Combine(Path.GetTempPath(), $"nm-fea07-{label}-{Guid.NewGuid():N}");
        Directory.CreateDirectory(path);
        return path;
    }

    public static void Delete(string path)
    {
        try
        {
            Directory.Delete(path, recursive: true);
        }
        catch (IOException)
        {
            // best effort test cleanup
        }
    }
}
