using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// READER-PROGRESS-1 AC1–AC3: reading progress through the real frozen sidecars on a copy of the
/// BOOK-FIXTURE data root. Proves the whole chain ListBooks → list_chapters → GetReaderProjection
/// (resume) → SaveReadingProgress → restart → resume, plus the read-only and typed-rejection edges.
/// </summary>
public sealed class HostReaderProgressIntegrationTests
{
    private static string NewCopy(string label)
    {
        var dataRoot = HostFixture.NewDataRoot(label);
        BookFixture.CopyTo(BookFixture.DataRoot, dataRoot);
        return dataRoot;
    }

    private static HostOptions OptionsFor(string testName, string dataRoot, bool parity) => new()
    {
        DataRoot = dataRoot,
        LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", testName),
        SidecarDirectoryOverride = HostFixture.SidecarDirectory,
        MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
        ParityReached = parity,
        DetectLegacyShell = false,
        EnableWireEvidence = true,
        StartupTimeout = TimeSpan.FromSeconds(90),
        RequestTimeout = TimeSpan.FromSeconds(90),
    };

    [BookFixtureFact]
    public async Task SaveReadingProgress_PersistsAcrossHostRestart_AndResumes()
    {
        var dataRoot = NewCopy("reader-progress-restart");
        try
        {
            string bookId;
            string chapterId;
            IReadOnlyList<ReaderPageSummary> pages;
            ReadingProgressSnapshot firstSave;
            ReadingProgressSnapshot secondSave;

            // ---- session 1: open (beginning), save page 5, save page 2 without a time delta ----
            await using (var runtime = await HostRuntime.StartAsync(OptionsFor("reader-progress-a", dataRoot, parity: true)))
            {
                Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
                Assert.Equal(HostMode.ReadWrite, runtime.Mode);
                Assert.True(runtime.Policy.WritesAllowed);

                var books = await runtime.ListBooksAsync();
                var book = Assert.Single(books);
                bookId = book.BookId;
                var chapters = await runtime.ListChaptersAsync(bookId);
                var chapter = Assert.Single(chapters);
                chapterId = chapter.ChapterId;

                var projection = await runtime.GetReaderProjectionAsync(chapterId, ReaderStartPosition.Beginning);
                Assert.Equal("original", projection.Mode);
                Assert.True(projection.Pages.Count >= 8, $"pages={projection.Pages.Count}");
                pages = projection.Pages;
                Assert.Equal(pages[0].PageId, projection.InitialPageId); // nothing saved yet
                Assert.Null(projection.SavedProgress);

                firstSave = await runtime.SaveReadingProgressAsync(
                    chapterId,
                    "original",
                    pages[5].PageId,
                    // The fixture chapter is webtoon_vertical: the Core derives progress_percent from
                    // the logical-page offset, so a non-zero in-page offset is what proves the write.
                    scrollOffsetY: 120,
                    elapsedSecondsDelta: 2.5);
                Assert.Equal(bookId, firstSave.BookId);
                Assert.Equal(chapterId, firstSave.ChapterId);
                Assert.Equal("original", firstSave.Mode);
                Assert.Equal(pages[5].PageId, firstSave.LastPageId);
                Assert.True(firstSave.ProgressPercent > 0, $"percent={firstSave.ProgressPercent}");
                Assert.InRange(firstSave.ScrollOffsetY, 119.9, 120.1);
                Assert.InRange(firstSave.TotalReadSeconds, 2.4, 3.0);

                // Same page again without elapsed_seconds_delta (MISSING = NOT SENT): the accepted
                // interval must not be replayed, so the total stays where it was.
                secondSave = await runtime.SaveReadingProgressAsync(
                    chapterId,
                    "original",
                    pages[1].PageId,
                    scrollOffsetY: null,
                    elapsedSecondsDelta: null);
                Assert.Equal(pages[1].PageId, secondSave.LastPageId);
                Assert.InRange(secondSave.TotalReadSeconds, firstSave.TotalReadSeconds - 0.001, firstSave.TotalReadSeconds + 0.001);
            }

            // ---- session 2: a fresh Host/Core reads the durable row and resumes it ----
            await using (var runtime = await HostRuntime.StartAsync(OptionsFor("reader-progress-b", dataRoot, parity: true)))
            {
                Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
                var resumed = await runtime.GetReaderProjectionAsync(chapterId, ReaderStartPosition.Resume);
                Assert.Equal(pages.Count, resumed.Pages.Count);
                Assert.Equal(pages[1].PageId, resumed.InitialPageId);
                Assert.NotNull(resumed.SavedProgress);
                Assert.Equal(pages[1].PageId, resumed.SavedProgress!.LastPageId);
                Assert.InRange(resumed.SavedProgress.TotalReadSeconds, 2.4, 3.0);

                // Read-only projection must not mutate: "beginning" stays at page 1.
                var beginning = await runtime.GetReaderProjectionAsync(chapterId, ReaderStartPosition.Beginning);
                Assert.Equal(pages[0].PageId, beginning.InitialPageId);

                HostFixture.WriteEvidenceJson("host/reader-progress-restart.json", writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("ac", "AC1/AC3");
                    writer.WriteString("book_id", bookId);
                    writer.WriteString("chapter_id", chapterId);
                    writer.WriteNumber("page_count", pages.Count);
                    writer.WriteString("first_saved_page_id", firstSave.LastPageId);
                    writer.WriteString("second_saved_page_id", secondSave.LastPageId);
                    writer.WriteNumber("first_total_read_seconds", firstSave.TotalReadSeconds);
                    writer.WriteNumber("second_total_read_seconds", secondSave.TotalReadSeconds);
                    writer.WriteString("resumed_page_id", resumed.InitialPageId);
                    writer.WriteNumber("resumed_total_read_seconds", resumed.SavedProgress.TotalReadSeconds);
                    writer.WriteBoolean("restart_resume_ok", resumed.InitialPageId == pages[1].PageId);
                    writer.WriteNumber("core_wire_frames", runtime.CoreService!.Wire.Count);
                    writer.WriteString("wire_log", "wire/core-service.ndjson");
                    writer.WriteEndObject();
                });
            }
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [BookFixtureFact]
    public async Task SaveReadingProgress_UnknownPage_IsTypedCoreRejection()
    {
        var dataRoot = NewCopy("reader-progress-reject");
        try
        {
            await using var runtime = await HostRuntime.StartAsync(OptionsFor("reader-progress-reject", dataRoot, parity: true));
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            var book = Assert.Single(await runtime.ListBooksAsync());
            var chapter = Assert.Single(await runtime.ListChaptersAsync(book.BookId));

            var error = await Assert.ThrowsAsync<CoreOperationException>(() =>
                runtime.SaveReadingProgressAsync(chapter.ChapterId, "original", "page-not-in-chapter", 0, 1.0));
            Assert.Equal("TARGET_NOT_FOUND", error.Code);

            HostFixture.WriteEvidenceJson("host/reader-progress-reject.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1/AC2");
                writer.WriteString("error_code", error.Code);
                writer.WriteBoolean("typed_rejection", error.Code == "TARGET_NOT_FOUND");
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [HostSidecarFact]
    public async Task SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall()
    {
        var options = HostFixture.CreateOptions("reader-progress-readonly", out var dataRoot, parity: false);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.False(runtime.Policy.WritesAllowed);

            var refusal = await Assert.ThrowsAsync<ReadOnlyHostException>(() =>
                runtime.SaveReadingProgressAsync("chapter-x", "original", "page-x", 0, 0));
            Assert.Equal("HOST_READ_ONLY", refusal.Code);

            HostFixture.WriteEvidenceJson("host/reader-progress-readonly.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2");
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("error_code", refusal.Code);
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }
}
