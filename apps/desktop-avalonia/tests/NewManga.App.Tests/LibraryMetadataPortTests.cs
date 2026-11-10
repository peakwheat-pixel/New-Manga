using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-14-LIB-1 (PREQ LIB P5-P8): the four additive metadata/reorder ports must
/// degrade safely on the null host and be observable (recorded) on the headless
/// fake, so a future UI card cannot silently lose the command or throw on the UI
/// thread.
/// </summary>
public sealed class LibraryMetadataPortTests
{
    [Fact]
    public async Task NullHost_MetadataPorts_ReturnFalseAndNull_InsteadOfThrowing()
    {
        IHostController host = NullHostController.Instance;
        Assert.False(await host.UpdateBookMetadataAsync(
            "book-1", new Dictionary<string, object?> { ["title"] = "x" }, CancellationToken.None));
        Assert.False(await host.ReorderChaptersAsync("book-1", new[] { "c1" }, CancellationToken.None));
        Assert.False(await host.UpdateChapterMetadataAsync(
            "c1", new Dictionary<string, object?> { ["notes"] = "x" }, CancellationToken.None));
        Assert.Null(await host.CreateChapterWithMetadataAsync(
            "book-1", "Ch", cancellationToken: CancellationToken.None));
    }

    [Fact]
    public async Task FakeHost_RecordsTheLastMetadataAndReorderCalls()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var bookPatch = new Dictionary<string, object?> { ["title"] = "Renamed", ["tags"] = new[] { "t1", "t2" } };
        var chapterPatch = new Dictionary<string, object?> { ["kind"] = "webtoon", ["custom_rank"] = 2 };

        Assert.True(await host.UpdateBookMetadataAsync("book-0", bookPatch, CancellationToken.None));
        Assert.True(await host.UpdateChapterMetadataAsync("chapter-1", chapterPatch, CancellationToken.None));
        Assert.True(await host.ReorderChaptersAsync("book-0", new[] { "c2", "c1" }, CancellationToken.None));

        Assert.Equal(("book-0", (IReadOnlyDictionary<string, object?>)bookPatch), host.LastBookMetadata);
        Assert.Equal(("chapter-1", (IReadOnlyDictionary<string, object?>)chapterPatch), host.LastChapterMetadata);
        Assert.True(host.LastReorderCalled);
        Assert.Equal(new[] { "c2", "c1" }, host.LastReorderIds);
    }

    [Fact]
    public async Task FakeHost_Reorder_AcceptsTheEmptyBookNoOp()
    {
        // R-13/P3-1 (r2): the empty list is the only way to say "reorder an empty
        // book"; the Host port must pass it through instead of rejecting it.
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        Assert.True(await host.ReorderChaptersAsync("book-0", System.Array.Empty<string>(), CancellationToken.None));
        Assert.NotNull(host.LastReorderIds);
        Assert.Empty(host.LastReorderIds!);
    }

    [Fact]
    public async Task FakeHost_CreateWithMetadata_AppendsTheSortOrder()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        host.ChaptersByBook["book-0"] = new[] { new ChapterSummary("c1", "C1", "1", 1) };
        var created = await host.CreateChapterWithMetadataAsync(
            "book-0", "Extra", kind: "webtoon", number: "99", importOrder: 7, CancellationToken.None);
        Assert.NotNull(created);
        Assert.Equal("Extra", created!.Title);
        Assert.Equal("99", created.ChapterNumber);
        // R-04/P3-2 (r2): appended sort_order (max+1), never the caller import_order.
        Assert.Equal(2, created.SortOrder);
    }
}
