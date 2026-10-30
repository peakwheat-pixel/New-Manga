using Avalonia.Headless.XUnit;
using NewManga.App.Shell.V2;

namespace NewManga.App.Tests;

/// <summary>
/// REALUSE-DATA-SAFETY-3 AC2 (audit MA-07): the Console's "任务与队列" section asked the user to type
/// a run_id because the frozen contract has no "list runs" command. The shared monitor now remembers
/// the ids the session actually obtained from the Host, which is what makes the section usable — but
/// it must stay a memory aid: no invented ids, no duplicates, bounded size, most recent first.
/// </summary>
public sealed class RunIndexTests
{
    private static RunStatusMonitor Monitor()
    {
        var monitor = new RunStatusMonitor(V2Fixture.Create());
        monitor.SetPollingEnabled(false); // no timer in unit tests; explicit refresh only
        return monitor;
    }

    [AvaloniaFact]
    public void Track_RemembersMostRecentFirst()
    {
        var monitor = Monitor();

        monitor.RememberRunId("run-a");
        monitor.RememberRunId("run-b");
        monitor.RememberRunId("run-c");

        Assert.Equal(new[] { "run-c", "run-b", "run-a" }, monitor.KnownRunIds);
    }

    [AvaloniaFact]
    public void Track_DeduplicatesAndPromotes()
    {
        var monitor = Monitor();
        monitor.RememberRunId("run-a");
        monitor.RememberRunId("run-b");

        monitor.RememberRunId("run-a");

        Assert.Equal(new[] { "run-a", "run-b" }, monitor.KnownRunIds);
    }

    [AvaloniaFact]
    public void Track_IgnoresEmptyIds_AndBoundsTheList()
    {
        var monitor = Monitor();
        monitor.RememberRunId(string.Empty);
        monitor.RememberRunId("   ");

        Assert.Empty(monitor.KnownRunIds);

        for (var index = 0; index < 20; index++)
        {
            monitor.RememberRunId($"run-{index:00}");
        }

        Assert.Equal(12, monitor.KnownRunIds.Count);
        Assert.Equal("run-19", monitor.KnownRunIds[0]);
        Assert.Equal("run-08", monitor.KnownRunIds[^1]);
    }

    [AvaloniaFact]
    public void Track_Alone_DoesNotRemember_SoATypoNeverBecomesAChip()
    {
        // Review r1 M5: typing a non-existent id used to be recorded immediately, which both lied
        // about what the session had seen and left a chip that polled a run that does not exist.
        var monitor = Monitor();

        monitor.Track("typo-run-id");

        Assert.Empty(monitor.KnownRunIds);
        Assert.Equal("typo-run-id", monitor.RunId); // still tracked (the read attempt must show its failure)
    }

    [AvaloniaFact]
    public void KnownRunIds_AreTrimmedAndNeverInvented()
    {
        var monitor = Monitor();

        monitor.RememberRunId("  run-trimmed  ");

        Assert.Equal(new[] { "run-trimmed" }, monitor.KnownRunIds);
        Assert.Empty(Monitor().KnownRunIds); // a fresh session knows nothing
    }
}
