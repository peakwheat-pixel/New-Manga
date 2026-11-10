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
            "book-1", new Dictionary<string, string> { ["title"] = "x" }, CancellationToken.None));
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
        var bookPatch = new Dictionary<string, string> { ["title"] = "Renamed" };
        var chapterPatch = new Dictionary<string, object?> { ["kind"] = "webtoon", ["custom_rank"] = 2 };

        Assert.True(await host.UpdateBookMetadataAsync("book-0", bookPatch, CancellationToken.None));
        Assert.True(await host.UpdateChapterMetadataAsync("chapter-1", chapterPatch, CancellationToken.None));
        Assert.True(await host.ReorderChaptersAsync("book-0", new[] { "c2", "c1" }, CancellationToken.None));

        Assert.Equal(("book-0", (IReadOnlyDictionary<string, string>)bookPatch), host.LastBookMetadata);
        Assert.Equal(("chapter-1", (IReadOnlyDictionary<string, object?>)chapterPatch), host.LastChapterMetadata);
        Assert.True(host.LastReorderCalled);
    }

    [Fact]
    public async Task FakeHost_CreateWithMetadata_ReturnsTheProjectedChapterSummary()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book"));
        var created = await host.CreateChapterWithMetadataAsync(
            "book-0", "Extra", kind: "webtoon", number: "99", importOrder: 7, CancellationToken.None);
        Assert.NotNull(created);
        Assert.Equal("Extra", created!.Title);
        Assert.Equal("99", created.ChapterNumber);
        Assert.Equal(7, created.SortOrder);
    }
}
