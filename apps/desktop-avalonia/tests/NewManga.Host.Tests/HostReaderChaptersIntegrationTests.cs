using NewManga.CoreClient;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// CHAPTER-SELECTOR-1 AC1: the reader's chapter list goes through the real frozen sidecars
/// (ListBooks → list_chapters) and is consistent with the ordered reader projection. Also pins the
/// reader I/O gate: chapter lists and projections share one request/response pipe, so concurrent
/// reads must be serialized instead of crossing responses.
/// </summary>
public sealed class HostReaderChaptersIntegrationTests
{
    private static string NewCopy(string label)
    {
        var dataRoot = HostFixture.NewDataRoot(label);
        BookFixture.CopyTo(BookFixture.DataRoot, dataRoot);
        return dataRoot;
    }

    private static HostOptions OptionsFor(string testName, string dataRoot) => new()
    {
        DataRoot = dataRoot,
        LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", testName),
        SidecarDirectoryOverride = HostFixture.SidecarDirectory,
        MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
        ParityReached = true,
        DetectLegacyShell = false,
        EnableWireEvidence = true,
        StartupTimeout = TimeSpan.FromSeconds(90),
        RequestTimeout = TimeSpan.FromSeconds(90),
    };

    [BookFixtureFact]
    public async Task ListChapters_MatchesReaderProjection()
    {
        var dataRoot = NewCopy("reader-chapters-list");
        try
        {
            await using var runtime = await HostRuntime.StartAsync(OptionsFor("reader-chapters-list", dataRoot));
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);

            var books = await runtime.ListBooksAsync();
            Assert.NotEmpty(books);
            var book = books[0];
            var chapters = await runtime.ListChaptersAsync(book.BookId);
            Assert.NotEmpty(chapters);
            var chapter = chapters[0];

            var projection = await runtime.GetReaderProjectionAsync(chapter.ChapterId, ReaderStartPosition.Beginning);
            Assert.Equal(chapter.ChapterId, projection.ChapterId);
            Assert.Equal(book.BookId, projection.BookId);
            Assert.True(projection.Pages.Count > 0, $"pages={projection.Pages.Count}");

            HostFixture.WriteEvidenceJson("host/reader-chapters-list.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1");
                writer.WriteString("book_id", book.BookId);
                writer.WriteString("chapter_id", chapter.ChapterId);
                writer.WriteNumber("chapter_count", chapters.Count);
                writer.WriteNumber("page_count", projection.Pages.Count);
                writer.WriteString("projection_mode", projection.Mode);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [BookFixtureFact]
    public async Task ConcurrentChapterAndProjectionReads_AreSerialized()
    {
        var dataRoot = NewCopy("reader-chapters-concurrent");
        try
        {
            await using var runtime = await HostRuntime.StartAsync(OptionsFor("reader-chapters-concurrent", dataRoot));
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            var book = Assert.Single(await runtime.ListBooksAsync());
            var chapter = Assert.Single(await runtime.ListChaptersAsync(book.BookId));

            // Without the reader I/O gate these frames would interleave on the single core_service
            // pipe: one request would read the other's response and fail with INVALID_RESPONSE.
            var tasks = new List<Task>(12);
            for (var i = 0; i < 6; i++)
            {
                tasks.Add(runtime.ListChaptersAsync(book.BookId));
                tasks.Add(runtime.GetReaderProjectionAsync(chapter.ChapterId, ReaderStartPosition.Beginning));
            }

            await Task.WhenAll(tasks);
            for (var i = 0; i < tasks.Count; i += 2)
            {
                var chapters = Assert.IsAssignableFrom<IReadOnlyList<ChapterSummary>>(((Task<IReadOnlyList<ChapterSummary>>)tasks[i]).Result);
                Assert.NotEmpty(chapters);
                var projection = ((Task<ReaderProjection>)tasks[i + 1]).Result;
                Assert.Equal(chapter.ChapterId, projection.ChapterId);
                Assert.NotEmpty(projection.Pages);
            }

            HostFixture.WriteEvidenceJson("host/reader-chapters-concurrent.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1");
                writer.WriteNumber("concurrent_tasks", tasks.Count);
                writer.WriteNumber("pages_observed", ((Task<ReaderProjection>)tasks[1]).Result.Pages.Count);
                writer.WriteString("result", "all_succeeded");
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }
}
