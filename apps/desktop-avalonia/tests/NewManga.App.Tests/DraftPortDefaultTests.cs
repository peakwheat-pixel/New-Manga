using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-05-PORT-1: the Draft command surface has to degrade safely in the two hosts
/// that cannot reach a Core (null host and the headless fake). These tests pin that
/// contract so a future implementation cannot silently throw on the UI thread.
/// </summary>
public sealed class DraftPortDefaultTests
{
    public static IEnumerable<object[]> Hosts()
    {
        yield return new object[] { NullHostController.Instance };
        yield return new object[] { new FakeHostController(FakeHostController.ReadySnapshot("book")) };
    }

    [Theory]
    [MemberData(nameof(Hosts))]
    public async Task OpenDraft_ReturnsNullWhenTheHostIsNotReady(IHostController host)
    {
        var lease = await host.OpenDraftAsync("s1", "p1", "r1", null, 1, CancellationToken.None);
        Assert.Null(lease);
    }

    [Theory]
    [MemberData(nameof(Hosts))]
    public async Task PatchDraft_And_PrepareCandidate_ReturnNull(IHostController host)
    {
        var patch = new DraftPatchRequest(new Dictionary<string, object?> { ["text"] = "x" });
        Assert.Null(await host.PatchDraftAsync("d1", "s1", patch, null, CancellationToken.None));
        Assert.Null(await host.PrepareCandidateAsync("r1", patch, "user", null, null, CancellationToken.None));
    }

    [Theory]
    [MemberData(nameof(Hosts))]
    public async Task Draft_Reads_ReturnEmptyAndDiscard_Completes(IHostController host)
    {
        Assert.Null(await host.GetDraftAsync("d1", CancellationToken.None));
        Assert.Empty(await host.ListDraftsAsync("s1", CancellationToken.None));
        Assert.Empty(await host.ApplyCandidatesAsync(
            new EditToken("t1", "d1", 1, "s1", "a", "b"),
            new[] { "c1" },
            CancellationToken.None));
        await host.DiscardDraftAsync("d1", "s1", CancellationToken.None);
    }
}
