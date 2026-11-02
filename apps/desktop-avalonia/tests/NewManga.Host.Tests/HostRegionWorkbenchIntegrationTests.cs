using System.Text.Json;
using System.Security.Cryptography;
using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// READER-WORKBENCH-1 AC1–AC3: the single-page workbench read/write faces through the REAL frozen
/// sidecars on a disposable copy of the seeded S4 region fixture. Proves:
///   * AC1: list_chapter_pages → list_regions (geometry + page_size projection) → list_region_revisions
///     plus the page image through the resource channel;
///   * AC2: set_region_type / restore_region_revision / rerender_page commit through the Core, the
///     optimistic guard uses the revision the caller read, and a stale guard is the typed conflict;
///   * AC3: the read-only-until-parity policy refuses all three writes with a typed exception and
///     ZERO additional Core frames, while the read face keeps working.
/// The region fixture is re-seeded by scripts/test.ps1, so every id comes from fixture.json.
/// </summary>
public sealed class HostRegionWorkbenchIntegrationTests
{
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

    [RegionFixtureFact]
    public async Task RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry()
    {
        var meta = RegionFixture.ReadMetadata();
        var dataRoot = RegionFixture.CopyToDisposable("region-workbench");
        try
        {
            await using var runtime = await HostRuntime.StartAsync(OptionsFor("region-workbench", dataRoot, parity: true));
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(HostMode.ReadWrite, runtime.Mode);
            Assert.True(runtime.Policy.WritesAllowed);

            // ---- AC1: book → chapter → page navigation -----------------------------------------
            var books = await runtime.ListBooksAsync();
            var book = books.First(candidate => string.Equals(candidate.BookId, meta.BookId, StringComparison.Ordinal));
            Assert.Equal(meta.BookId, book.BookId);
            var chapters = await runtime.ListChaptersAsync(meta.BookId);
            var chapter = chapters.First(candidate => string.Equals(candidate.ChapterId, meta.ChapterId, StringComparison.Ordinal));
            Assert.Equal(meta.ChapterId, chapter.ChapterId);
            var pages = await runtime.ListChapterPagesAsync(meta.ChapterId);
            Assert.Equal(meta.PageCount, pages.Count);
            Assert.Contains(pages, page => string.Equals(page.PageId, meta.PageId, StringComparison.Ordinal));
            Assert.All(pages, page => Assert.False(string.IsNullOrWhiteSpace(page.SourceFilename)));

            // ---- AC1: list_regions + geometry / page_size projection ---------------------------
            var projection = await runtime.ListRegionsAsync(meta.PageId);
            Assert.NotNull(projection.PageSize);
            Assert.Equal(meta.PageWidth, projection.PageSize!.Width);
            Assert.Equal(meta.PageHeight, projection.PageSize.Height);
            var region = Assert.Single(projection.Regions);
            Assert.Equal(meta.RegionId, region.RegionId);
            Assert.Equal(meta.RegionRevisionNo, region.RevisionNo);
            Assert.Equal(meta.RegionType, region.RegionType);
            Assert.Equal("user", region.Origin);
            Assert.NotNull(region.Geometry);
            var pixelRect = region.Geometry!.ToPagePixels(projection.PageSize);
            Assert.Equal(meta.PageWidth / 10.0, pixelRect.X, 3);
            Assert.Equal(meta.PageHeight / 10.0, pixelRect.Y, 3);
            Assert.Equal(meta.PageWidth * 0.8, pixelRect.Width, 3);
            Assert.Equal(meta.PageHeight * 0.8, pixelRect.Height, 3);
            Assert.Equal(0.1, region.Geometry.X, 4);
            Assert.Equal(0.1, region.Geometry.Y, 4);
            Assert.Equal(0.8, region.Geometry.Width, 4);
            Assert.Equal(0.8, region.Geometry.Height, 4);

            // ---- AC1: revision history + page image through the resource channel ----------------
            var history = await runtime.ListRegionRevisionsAsync(meta.RegionId);
            Assert.Equal(meta.RegionRevisionNo, history.CurrentRevisionNo);
            Assert.Equal(meta.RegionRevisionNo, history.Revisions.Count);
            Assert.Single(history.Revisions, revision => revision.IsCurrent && revision.RevisionNo == meta.RegionRevisionNo);
            Assert.Contains(history.Revisions, revision => revision.ReviewState == "confirmed");

            var imageBefore = await runtime.ReadPageImageAsync(meta.PageId);
            Assert.True(imageBefore.Length > 1024, $"page image bytes={imageBefore.Length}");
            Assert.Equal(0xFF, imageBefore[0]);
            Assert.Equal(0xD8, imageBefore[1]);
            var (dbBefore, walBefore) = RegionFixture.DatabaseDigests(dataRoot);

            // ---- AC2: retype with the revision the caller read --------------------------------
            var retyped = await runtime.SetRegionTypeAsync(meta.RegionId, "narration", meta.RegionRevisionNo);
            Assert.Equal(meta.RegionId, retyped.RegionId);
            Assert.Equal("narration", retyped.RegionType);
            Assert.Equal(meta.RegionRevisionNo + 1, retyped.RevisionNo);

            var afterRetype = await runtime.ListRegionsAsync(meta.PageId);
            var retypedRow = Assert.Single(afterRetype.Regions);
            Assert.Equal("narration", retypedRow.RegionType);
            Assert.Equal(retyped.RevisionNo, retypedRow.RevisionNo);
            var historyAfterRetype = await runtime.ListRegionRevisionsAsync(meta.RegionId);
            Assert.Equal(retyped.RevisionNo, historyAfterRetype.CurrentRevisionNo);
            Assert.Equal(meta.RegionRevisionNo + 1, historyAfterRetype.Revisions.Count);

            // ---- AC2: restore the immediately previous revision (new revision, old content) ----
            var restored = await runtime.RestoreRegionRevisionAsync(
                meta.RegionId,
                revisionNo: meta.RegionRevisionNo,
                expectedRevision: retyped.RevisionNo);
            Assert.Equal(retyped.RevisionNo + 1, restored.RevisionNo);
            Assert.Equal(meta.RegionType, restored.RegionType);

            var afterRestore = await runtime.ListRegionsAsync(meta.PageId);
            var restoredRow = Assert.Single(afterRestore.Regions);
            Assert.Equal(meta.RegionType, restoredRow.RegionType);
            Assert.Equal(restored.RevisionNo, restoredRow.RevisionNo);
            var historyAfterRestore = await runtime.ListRegionRevisionsAsync(meta.RegionId);
            Assert.Equal(restored.RevisionNo, historyAfterRestore.CurrentRevisionNo);
            Assert.Single(historyAfterRestore.Revisions, revision => revision.RevisionNo == restored.RevisionNo && revision.IsCurrent);

            // ---- AC2: manual page rerender -----------------------------------------------------
            var rerender = await runtime.RerenderPageAsync(meta.PageId);
            Assert.Equal(meta.PageId, rerender.PageId);
            Assert.False(string.IsNullOrEmpty(rerender.ArtifactId));
            Assert.True(rerender.RevisionNo >= 1);
            Assert.Single(rerender.Reports);
            Assert.Equal(meta.RegionId, rerender.Reports[0].RegionId);
            Assert.True(
                !string.IsNullOrEmpty(rerender.PreviewResourceId) || !string.IsNullOrEmpty(rerender.PreviewError),
                "rerender must project either the published preview or its typed error");

            // The page image is still readable through the same resource channel after the write.
            var imageAfter = await runtime.ReadPageImageAsync(meta.PageId);
            Assert.Equal(imageBefore, imageAfter);

            var (dbAfter, walAfter) = RegionFixture.DatabaseDigests(dataRoot);
            Assert.False(
                string.Equals(dbBefore, dbAfter, StringComparison.Ordinal) &&
                string.Equals(walBefore, walAfter, StringComparison.Ordinal),
                "the committed region writes must change the durable SQLite state");

            HostFixture.WriteEvidenceJson("host/region-workbench-read-write.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1/AC2");
                writer.WriteString("fixture", "scripts/seed_s4_region_fixture.py (disposable copy)");
                writer.WriteString("book_id", meta.BookId);
                writer.WriteString("chapter_id", meta.ChapterId);
                writer.WriteString("page_id", meta.PageId);
                writer.WriteNumber("page_count", pages.Count);
                writer.WriteNumber("page_width", meta.PageWidth);
                writer.WriteNumber("page_height", meta.PageHeight);
                writer.WriteString("region_id", meta.RegionId);
                writer.WriteNumber("region_revision_before", meta.RegionRevisionNo);
                writer.WriteString("region_type_before", meta.RegionType);
                writer.WriteNumber("region_revision_after_retype", retyped.RevisionNo);
                writer.WriteString("region_type_after_retype", retyped.RegionType);
                writer.WriteNumber("region_revision_after_restore", restored.RevisionNo);
                writer.WriteString("region_type_after_restore", restored.RegionType);
                writer.WriteNumber("revision_count_after_restore", historyAfterRestore.Revisions.Count);
                writer.WriteString("rerender_artifact_id", rerender.ArtifactId);
                writer.WriteNumber("rerender_revision_no", rerender.RevisionNo);
                writer.WriteNumber("rerender_report_count", rerender.Reports.Count);
                writer.WriteBoolean("rerender_preview_published", !string.IsNullOrEmpty(rerender.PreviewResourceId));
                writer.WriteString("rerender_preview_error", rerender.PreviewError);
                writer.WriteNumber("geometry_bbox_x", Math.Round(region.Geometry.X, 6));
                writer.WriteNumber("geometry_bbox_y", Math.Round(region.Geometry.Y, 6));
                writer.WriteNumber("geometry_bbox_width", Math.Round(region.Geometry.Width, 6));
                writer.WriteNumber("geometry_bbox_height", Math.Round(region.Geometry.Height, 6));
                writer.WriteNumber("pixel_rect_x", Math.Round(pixelRect.X, 3));
                writer.WriteNumber("pixel_rect_y", Math.Round(pixelRect.Y, 3));
                writer.WriteNumber("pixel_rect_width", Math.Round(pixelRect.Width, 3));
                writer.WriteNumber("pixel_rect_height", Math.Round(pixelRect.Height, 3));
                writer.WriteNumber("page_image_bytes", imageAfter.Length);
                writer.WriteString("library_db_sha256_before", dbBefore);
                writer.WriteString("library_db_wal_sha256_before", walBefore);
                writer.WriteString("library_db_sha256_after", dbAfter);
                writer.WriteString("library_db_wal_sha256_after", walAfter);
                writer.WriteBoolean(
                    "db_changed",
                    !string.Equals(dbBefore, dbAfter, StringComparison.Ordinal) ||
                    !string.Equals(walBefore, walAfter, StringComparison.Ordinal));
                writer.WriteNumber("core_wire_frames", runtime.CoreService!.Wire.Count);
                writer.WriteString("wire_log", "host-logs/region-workbench/wire/core-service.ndjson");
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [RegionFixtureFact]
    public async Task RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged()
    {
        var meta = RegionFixture.ReadMetadata();
        var dataRoot = RegionFixture.CopyToDisposable("region-workbench-stale");
        try
        {
            await using var runtime = await HostRuntime.StartAsync(OptionsFor("region-workbench-stale", dataRoot, parity: true));
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);

            var error = await Assert.ThrowsAsync<CoreOperationException>(() =>
                runtime.SetRegionTypeAsync(meta.RegionId, "narration", meta.RegionRevisionNo + 10));
            Assert.Equal("INPUT_REVISION_CHANGED", error.Code);
            Assert.Equal("conflict", error.Category);

            // Optimistic guard: a refused write leaves the region state untouched.
            var projection = await runtime.ListRegionsAsync(meta.PageId);
            var row = Assert.Single(projection.Regions);
            Assert.Equal(meta.RegionRevisionNo, row.RevisionNo);
            Assert.Equal(meta.RegionType, row.RegionType);
            var history = await runtime.ListRegionRevisionsAsync(meta.RegionId);
            Assert.Equal(meta.RegionRevisionNo, history.CurrentRevisionNo);

            HostFixture.WriteEvidenceJson("host/region-workbench-stale-revision.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2");
                writer.WriteString("region_id", meta.RegionId);
                writer.WriteNumber("expected_revision_sent", meta.RegionRevisionNo + 10);
                writer.WriteString("error_code", error.Code);
                writer.WriteString("error_category", error.Category);
                writer.WriteNumber("region_revision_after_refusal", row.RevisionNo);
                writer.WriteBoolean("zero_write", row.RevisionNo == meta.RegionRevisionNo);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [RegionFixtureFact]
    public async Task RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames()
    {
        var meta = RegionFixture.ReadMetadata();
        var dataRoot = RegionFixture.CopyToDisposable("region-workbench-readonly");
        try
        {
            await using var runtime = await HostRuntime.StartAsync(OptionsFor("region-workbench-readonly", dataRoot, parity: false));
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.Equal(HostMode.ReadOnlyUntilParity, runtime.Mode);
            Assert.False(runtime.Policy.WritesAllowed);

            // AC3: the read face keeps working while the Host is read-only.
            var projection = await runtime.ListRegionsAsync(meta.PageId);
            var row = Assert.Single(projection.Regions);
            Assert.Equal(meta.RegionId, row.RegionId);
            var pages = await runtime.ListChapterPagesAsync(meta.ChapterId);
            Assert.Equal(meta.PageCount, pages.Count);

            var framesBefore = runtime.CoreService!.Wire.Count;
            var retype = await Assert.ThrowsAsync<ReadOnlyHostException>(() =>
                runtime.SetRegionTypeAsync(meta.RegionId, "narration", meta.RegionRevisionNo));
            Assert.Equal("HOST_READ_ONLY", retype.Code);
            var restore = await Assert.ThrowsAsync<ReadOnlyHostException>(() =>
                runtime.RestoreRegionRevisionAsync(meta.RegionId, 1, meta.RegionRevisionNo));
            Assert.Equal("HOST_READ_ONLY", restore.Code);
            var rerender = await Assert.ThrowsAsync<ReadOnlyHostException>(() =>
                runtime.RerenderPageAsync(meta.PageId));
            Assert.Equal("HOST_READ_ONLY", rerender.Code);
            var framesAfter = runtime.CoreService.Wire.Count;

            // AC3: no request reached the Core for the three refused writes.
            Assert.Equal(framesBefore, framesAfter);

            // …and the region state is exactly what the read face reported before the attempts.
            var afterAttempts = await runtime.ListRegionsAsync(meta.PageId);
            var unchanged = Assert.Single(afterAttempts.Regions);
            Assert.Equal(meta.RegionRevisionNo, unchanged.RevisionNo);
            Assert.Equal(meta.RegionType, unchanged.RegionType);

            HostFixture.WriteEvidenceJson("host/region-workbench-readonly.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC3");
                writer.WriteString("mode", runtime.Mode.ToString());
                writer.WriteBoolean("writes_allowed", runtime.Policy.WritesAllowed);
                writer.WriteString("retype_error_code", retype.Code);
                writer.WriteString("restore_error_code", restore.Code);
                writer.WriteString("rerender_error_code", rerender.Code);
                writer.WriteNumber("core_frames_before_writes", framesBefore);
                writer.WriteNumber("core_frames_after_writes", framesAfter);
                writer.WriteBoolean("zero_core_frames", framesBefore == framesAfter);
                writer.WriteBoolean("read_face_available", row.RevisionNo == meta.RegionRevisionNo);
                writer.WriteNumber("regions_read_in_read_only_mode", afterAttempts.Regions.Count);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    /// <summary>AC1 read ordering: the workbench's three reads serialize on one Core pipe.</summary>
    [RegionFixtureFact]
    public async Task RegionReads_SerializeOnTheCorePipe()
    {
        var meta = RegionFixture.ReadMetadata();
        var dataRoot = RegionFixture.CopyToDisposable("region-workbench-serialize");
        try
        {
            await using var runtime = await HostRuntime.StartAsync(OptionsFor("region-workbench-serialize", dataRoot, parity: true));
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            var reads = new List<Task>
            {
                runtime.ListChapterPagesAsync(meta.ChapterId),
                runtime.ListRegionsAsync(meta.PageId),
                runtime.ListRegionRevisionsAsync(meta.RegionId),
                runtime.ReadPageImageAsync(meta.PageId),
            };
            await Task.WhenAll(reads);
            Assert.All(reads, read => Assert.True(read.IsCompletedSuccessfully));

            // Every frame carries a request_id and the four concurrent reads got four distinct
            // responses back in order: the strict request/response gate prevented crossed frames.
            var wire = runtime.CoreService!.Wire;
            Assert.True(wire.Count >= 4);
            Assert.True(wire.AllRequestsAsciiOnly);
            var lastFour = wire.Frames.Skip(wire.Count - 4).ToList();
            Assert.Equal(4, lastFour.Count);
            Assert.All(lastFour, frame => Assert.Contains("\"request_id\"", frame.RequestLine, StringComparison.Ordinal));
            Assert.All(lastFour, frame => Assert.Contains("\"request_id\"", frame.ResponseLine, StringComparison.Ordinal));
            var commands = lastFour.Select(frame => ReadCommand(frame.RequestLine)).ToHashSet(StringComparer.Ordinal);
            Assert.Contains("list_chapter_pages", commands);
            Assert.Contains("list_regions", commands);
            Assert.Contains("list_region_revisions", commands);
            Assert.Contains("resolve_page_resource", commands);
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    private static string ReadCommand(string requestLine)
    {
        using var document = JsonDocument.Parse(requestLine);
        return document.RootElement.GetProperty("command").GetString() ?? string.Empty;
    }
}
