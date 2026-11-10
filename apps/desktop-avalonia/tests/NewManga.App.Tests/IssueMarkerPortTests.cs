using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-14-EDIT-1 (PREQ EDIT P16-P20): the five issue-marker ports must degrade
/// safely on the null host and be observable on the headless fake, so a future
/// editor UI card cannot silently lose a command or throw on the UI thread.
/// </summary>
public sealed class IssueMarkerPortTests
{
    [Fact]
    public async Task NullHost_IssueMarkerPorts_DegradeWithoutThrowing()
    {
        IHostController host = NullHostController.Instance;
        Assert.Empty(await host.ListIssueMarkersAsync("book-1", cancellationToken: CancellationToken.None));
        Assert.Null(await host.CreateIssueMarkerAsync(
            "book-1", "chapter-1", "page-1", "kind", cancellationToken: CancellationToken.None));
        Assert.False(await host.ResolveIssueMarkerAsync("marker-1", CancellationToken.None));
        Assert.False(await host.ReopenIssueMarkerAsync("marker-1", CancellationToken.None));
        Assert.False(await host.DeleteIssueMarkerAsync("marker-1", CancellationToken.None));
    }

    [Fact]
    public async Task FakeHost_RecordsListAndCreateCommands()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var listed = await host.ListIssueMarkersAsync("book-0", "open", CancellationToken.None);
        Assert.Empty(listed);
        Assert.Equal(("book-0", "open"), host.LastIssueMarkerList);

        var markerId = await host.CreateIssueMarkerAsync(
            "book-0", "chapter-1", "page-1", "translation-check",
            note: "check", position: new IssueMarkerPosition(0.25, 0.75), CancellationToken.None);
        Assert.NotNull(markerId);
        var created = Assert.Single(host.IssueMarkers);
        Assert.Equal(markerId, created.MarkerId);
        Assert.Equal("open", created.State);
        Assert.Equal(0.25, created.Position!.X);
        Assert.Equal(0.75, created.Position!.Y);
        Assert.NotNull(host.LastIssueMarkerCreate);
        var createCall = host.LastIssueMarkerCreate!.Value;
        Assert.Equal("book-0", createCall.BookId);
        Assert.Equal("chapter-1", createCall.ChapterId);
        Assert.Equal("page-1", createCall.PageId);
        Assert.Equal("translation-check", createCall.Kind);
        Assert.Equal("check", createCall.Note);
        Assert.Equal(new IssueMarkerPosition(0.25, 0.75), createCall.Position);
    }

    [Fact]
    public async Task FakeHost_ModelsTheStateMachineAndLedger()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var createdMarkerId = await host.CreateIssueMarkerAsync(
            "book-0", "chapter-1", "page-1", "kind", cancellationToken: CancellationToken.None);
        var markerId = Assert.IsType<string>(createdMarkerId);

        Assert.True(await host.ResolveIssueMarkerAsync(markerId, CancellationToken.None));
        Assert.Equal("resolved", Assert.Single(host.IssueMarkers).State);
        Assert.Empty(await host.ListIssueMarkersAsync("book-0", "open", CancellationToken.None));
        Assert.Single(await host.ListIssueMarkersAsync("book-0", "resolved", CancellationToken.None));

        Assert.True(await host.ReopenIssueMarkerAsync(markerId, CancellationToken.None));
        Assert.Equal("open", Assert.Single(host.IssueMarkers).State);

        Assert.True(await host.DeleteIssueMarkerAsync(markerId, CancellationToken.None));
        Assert.Empty(host.IssueMarkers);
        Assert.Equal(
            new[]
            {
                ("ResolveIssueMarker", markerId),
                ("ReopenIssueMarker", markerId),
                ("DeleteIssueMarker", markerId),
            },
            host.IssueMarkerCommands);
    }

    [Fact]
    public async Task FakeHost_ListFiltersByBookAndDefaultsToOpen()
    {
        // F-03 (r1): the fake must not be laxer than the Core projection -- the
        // list is per book and a missing state means "open".
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var first = await host.CreateIssueMarkerAsync(
            "book-0", "chapter-1", "page-1", "kind", cancellationToken: CancellationToken.None);
        await host.CreateIssueMarkerAsync(
            "book-1", "chapter-2", "page-2", "kind", cancellationToken: CancellationToken.None);

        Assert.Single(await host.ListIssueMarkersAsync("book-0", cancellationToken: CancellationToken.None));
        Assert.Empty(await host.ListIssueMarkersAsync("book-2", cancellationToken: CancellationToken.None));
        Assert.True(await host.ResolveIssueMarkerAsync(Assert.IsType<string>(first), CancellationToken.None));
        Assert.Empty(await host.ListIssueMarkersAsync("book-0", cancellationToken: CancellationToken.None));
        Assert.Single(await host.ListIssueMarkersAsync("book-0", "resolved", CancellationToken.None));
    }

    [Fact]
    public async Task FakeHost_StateCommands_ReportMissingMarkers()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        Assert.False(await host.ResolveIssueMarkerAsync("missing", CancellationToken.None));
        Assert.False(await host.ReopenIssueMarkerAsync("missing", CancellationToken.None));
        Assert.False(await host.DeleteIssueMarkerAsync("missing", CancellationToken.None));
    }
}
