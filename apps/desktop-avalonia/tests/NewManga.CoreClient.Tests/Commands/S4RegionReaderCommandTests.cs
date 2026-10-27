using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Tests.Support;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// S4-CMD-BATCH-1 AC2: the region write face (set_region_type, restore_region_revision,
/// rerender_page, resolve_page_resource) and the reader progress face (SaveReadingProgress,
/// GetReaderProjection) really execute against the frozen core_service with VALID targets from
/// the seeded region fixture (library.db + managed originals + clean artifact + translated region).
///
/// The fixture is produced by <c>scripts/seed_s4_region_fixture.py</c> (invoked by
/// <c>scripts/test.ps1</c>); the test copies its durable state into a disposable data root, so the
/// shared fixture is never mutated. Fixture-wide evidence lands in
/// <c>$NEWMANGA_EVIDENCE_DIR/commands/s4-region-reader-results.json</c>.
/// </summary>
public sealed class S4RegionReaderCommandTests
{
    private static JsonElement Args(object payload)
    {
        using var document = JsonDocument.Parse(JsonSerializer.Serialize(payload));
        return document.RootElement.Clone();
    }

    private static void WriteEvidence(
        string ac,
        S4RegionFixture.Metadata meta,
        IReadOnlyList<(string Command, string CoreCommand, bool Ok, string Detail)> rows,
        bool allOk)
    {
        SidecarFixture.WriteEvidenceJson("commands/s4-region-reader-results.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", ac);
            writer.WriteString("fixture", "scripts/seed_s4_region_fixture.py");
            writer.WriteString("book_id", meta.BookId);
            writer.WriteString("chapter_id", meta.ChapterId);
            writer.WriteString("chapter_type", meta.ChapterType);
            writer.WriteString("page_id", meta.PageId);
            writer.WriteNumber("page_count", meta.PageCount);
            writer.WriteString("region_id", meta.RegionId);
            writer.WriteNumber("region_revision_no", meta.RegionRevisionNo);
            writer.WriteString("region_type", meta.RegionType);
            writer.WriteBoolean("all_ok", allOk);
            writer.WriteNumber("executed_count", rows.Count);
            writer.WriteStartArray("results");
            foreach (var row in rows)
            {
                writer.WriteStartObject();
                writer.WriteString("command", row.Command);
                writer.WriteString("core_command", row.CoreCommand);
                writer.WriteBoolean("ok", row.Ok);
                writer.WriteString("detail", row.Detail);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    private static void TryDelete(string directory)
    {
        try
        {
            Directory.Delete(directory, recursive: true);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            // Best effort: the temp root is outside the repository.
        }
    }

    [S4RegionFixtureFact]
    public async Task RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore()
    {
        Assert.True(
            S4RegionFixture.TryGet(out var fixtureRoot, out var metaPath, out var reason),
            reason);
        var meta = S4RegionFixture.ReadMetadata(metaPath);
        var dataRoot = S4RegionFixture.CopyDurableToDisposable(fixtureRoot, "s4-region-reader");
        var rows = new List<(string Command, string CoreCommand, bool Ok, string Detail)>();
        try
        {
            await using var core = await CoreServiceClient.StartAsync(
                S4RegionFixture.CreateCoreOptions("s4-region-reader", dataRoot));
            var dispatcher = new HostCommandDispatcher(core);

            // list_regions (already implemented read face) provides the CURRENT revision the
            // optimistic guard must carry -- the same read-then-write choreography the UI uses.
            var regions = await dispatcher.InvokeAsync(
                "list_regions", Args(new { page_id = meta.PageId }));
            var regionRow = regions.Value.GetProperty("regions").EnumerateArray()
                .First(row => row.GetProperty("region_id").GetString() == meta.RegionId);
            var currentRevision = regionRow.GetProperty("revision_no").GetInt32();
            Assert.Equal(meta.RegionRevisionNo, currentRevision);
            Assert.Equal(meta.RegionType, regionRow.GetProperty("region_type").GetString());
            rows.Add(("list_regions (read-then-write setup)", "list_regions", true,
                $"revision_no={currentRevision}"));

            var retyped = await dispatcher.InvokeAsync(
                "set_region_type",
                Args(new { region_id = meta.RegionId, new_region_type = "narration", expected_revision = currentRevision }));
            Assert.Equal(meta.RegionId, retyped.Value.GetProperty("region_id").GetString());
            Assert.Equal("narration", retyped.Value.GetProperty("region_type").GetString());
            var retypedRevision = retyped.Value.GetProperty("revision_no").GetInt32();
            Assert.Equal(currentRevision + 1, retypedRevision);
            rows.Add(("set_region_type", "set_region_type", true,
                $"region_type=narration revision_no={retypedRevision}"));

            var restored = await dispatcher.InvokeAsync(
                "restore_region_revision",
                Args(new { region_id = meta.RegionId, revision_no = 1, expected_revision = retypedRevision }));
            Assert.Equal("speech", restored.Value.GetProperty("region_type").GetString());
            var restoredRevision = restored.Value.GetProperty("revision_no").GetInt32();
            Assert.Equal(retypedRevision + 1, restoredRevision);
            Assert.Equal(meta.RegionId, restored.Value.GetProperty("region_id").GetString());
            rows.Add(("restore_region_revision", "restore_region_revision", true,
                $"restored revision_no=1 -> new revision_no={restoredRevision} region_type=speech"));

            var rerendered = await dispatcher.InvokeAsync(
                "rerender_page", Args(new { page_id = meta.PageId }));
            Assert.Equal(meta.PageId, rerendered.Value.GetProperty("page_id").GetString());
            var artifactId = rerendered.Value.GetProperty("artifact_id").GetString();
            Assert.False(string.IsNullOrEmpty(artifactId), "rerender_page must publish a translated artifact");
            var translatedRevision = rerendered.Value.GetProperty("revision_no").GetInt32();
            Assert.True(translatedRevision >= 1);
            Assert.Equal(JsonValueKind.Array, rerendered.Value.GetProperty("reports").ValueKind);
            Assert.True(
                rerendered.Value.TryGetProperty("preview", out _) ||
                rerendered.Value.TryGetProperty("preview_error", out _),
                "rerender_page must project the preview channel state");
            rows.Add(("rerender_page", "rerender_page", true,
                $"artifact_id={artifactId} revision_no={translatedRevision} " +
                $"reports={rerendered.Value.GetProperty("reports").GetArrayLength()}"));

            var resolved = await dispatcher.InvokeAsync(
                "resolve_page_resource", Args(new { page_id = meta.PageId }));
            Assert.Equal(
                "page-original-" + meta.PageId,
                resolved.Value.GetProperty("resource_id").GetString());
            var resourceRevision = resolved.Value.GetProperty("revision").GetString();
            Assert.False(string.IsNullOrEmpty(resourceRevision), "resolve_page_resource must return a revision");
            rows.Add(("resolve_page_resource", "resolve_page_resource", true,
                $"resource_id=page-original-{meta.PageId} revision={resourceRevision}"));

            var progress = await dispatcher.InvokeAsync(
                "library_save_reading_progress",
                Args(new
                {
                    chapter_id = meta.ChapterId,
                    mode = "original",
                    page_id = meta.PageId,
                    scroll_offset_y = 0,
                    elapsed_seconds_delta = 1.5,
                }));
            Assert.Equal(meta.ChapterId, progress.Value.GetProperty("chapter_id").GetString());
            Assert.Equal(meta.PageId, progress.Value.GetProperty("last_page_id").GetString());
            Assert.Equal("original", progress.Value.GetProperty("mode").GetString());
            Assert.True(progress.Value.GetProperty("total_read_seconds").GetDouble() >= 1.5);
            rows.Add(("library_save_reading_progress", "SaveReadingProgress", true,
                "mode=original scroll_offset_y=0 elapsed_seconds_delta=1.5 persisted"));

            var projection = await dispatcher.InvokeAsync(
                "library_get_reader_projection",
                Args(new
                {
                    chapter_id = meta.ChapterId,
                    mode = "original",
                    start_position = "beginning",
                }));
            Assert.Equal(meta.ChapterId, projection.Value.GetProperty("chapter_id").GetString());
            Assert.Equal("webtoon_vertical", projection.Value.GetProperty("layout").GetString());
            var pages = projection.Value.GetProperty("pages");
            Assert.Equal(meta.PageCount, pages.GetArrayLength());
            var firstPage = pages[0];
            var firstPageId = firstPage.GetProperty("page_id").GetString();
            Assert.Equal(
                "page-original-" + firstPageId,
                firstPage.GetProperty("original").GetProperty("resource_ref")
                    .GetProperty("resource_id").GetString());
            Assert.Equal(
                firstPageId,
                projection.Value.GetProperty("initial_position").GetProperty("page_id").GetString());
            rows.Add(("library_get_reader_projection", "GetReaderProjection", true,
                $"layout=webtoon_vertical pages={meta.PageCount} initial_page={firstPageId}"));

            var evidencePath = WriteAndReturnEvidencePath(meta, rows);
            Assert.True(File.Exists(evidencePath), $"AC2 evidence missing at {evidencePath}");
        }
        finally
        {
            TryDelete(dataRoot);
        }
    }

    private static string WriteAndReturnEvidencePath(
        S4RegionFixture.Metadata meta,
        IReadOnlyList<(string Command, string CoreCommand, bool Ok, string Detail)> rows)
    {
        WriteEvidence("AC2", meta, rows, rows.All(row => row.Ok));
        return Path.Combine(SidecarFixture.EvidenceDirectory, "commands", "s4-region-reader-results.json");
    }
}
