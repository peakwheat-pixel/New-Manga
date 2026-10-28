using System.Diagnostics;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text.Json;
using NewManga.Host.Tests.Support;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// EXPORT-E2E-CLOSE-1 AC1/AC2/AC3: the first real export end to end.
///
/// Preconditions (produced by this task's AC1 tool, <c>verification/EXPORT-E2E-CLOSE-1/tools/ac1_precheck.py</c>):
///   * <c>NEWMANGA_EXPORT_SIDECAR_DIR</c> — the RELEASE-REPACK-2 models sidecar (core_service sha c5531930…),
///   * <c>NEWMANGA_EXPORT_DATA_ROOT</c> — a private copy of that build's completed 8-page Run data root,
///     in which pages 1–3 carry real translated artifacts (identity translation is an EXPERIMENTAL
///     placeholder: input == output, recorded as such upstream — never a quality claim).
///
/// When either variable is absent the test returns immediately: ordinary <c>test.ps1</c> runs without the
/// repacked sidecar keep passing, and the export-specific environment is only exercised when the task
/// harness provides it. Evidence is written through <see cref="HostFixture.WriteEvidenceJson"/> under
/// <c>NEWMANGA_EVIDENCE_DIR</c> (private: no <c>%APPDATA%</c> writes).
/// </summary>
public sealed class ExportE2ETests
{
    private const string BookId = "14340ddad0ed472fbe687fe12340c5d8";
    private const string ChapterId = "240bdba549b74281bfc6d901b1a7abd7";
    private const string SidecarVariable = "NEWMANGA_EXPORT_SIDECAR_DIR";
    private const string DataRootVariable = "NEWMANGA_EXPORT_DATA_ROOT";
    private static readonly TimeSpan ExportTimeout = TimeSpan.FromSeconds(180);

    private static string? Env(string name)
    {
        var value = Environment.GetEnvironmentVariable(name);
        return string.IsNullOrWhiteSpace(value) ? null : value;
    }

    private static JsonElement Json(string text)
    {
        using var document = JsonDocument.Parse(text);
        return document.RootElement.Clone();
    }

    private static string Sha256OfFile(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    private static string Sha256OfBytes(byte[] bytes) =>
        Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

    private static string Quote(string value) => JsonSerializer.Serialize(value);

    /// <summary>Snapshot status values are the Core's export job states.</summary>
    private static readonly HashSet<string> TerminalStatuses = new(StringComparer.Ordinal)
    {
        "completed", "skipped", "cancelled", "failed",
    };

    private static async Task<JsonElement> SnapshotAsync(
        NewManga.CoreClient.Commands.HostCommandDispatcher commands,
        string exportId,
        CancellationToken cancellationToken)
    {
        var result = await commands.InvokeAsync(
            "library_get_export_snapshot",
            Json($"{{\"export_id\":{Quote(exportId)}}}"),
            cancellationToken);
        return result.Value;
    }

    [HostSidecarFact]
    public async Task Export_Zip_Produces_RealArtifact_AndSnapshotHistory()
    {
        var sidecar = Env(SidecarVariable);
        var dataRoot = Env(DataRootVariable);
        if (sidecar is null || dataRoot is null)
        {
            // AC1/2/3 harness not attached (ordinary test.ps1 run): nothing to prove here.
            return;
        }

        var options = new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", "export-e2e"),
            SidecarDirectoryOverride = sidecar,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            ParityReached = true,
            DetectLegacyShell = false,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(120),
            RequestTimeout = TimeSpan.FromSeconds(180),
        };
        var sidecarExe = Path.Combine(sidecar, "core_service.exe");
        var sidecarSha = Sha256OfFile(sidecarExe);
        var started = Stopwatch.StartNew();

        await using var runtime = await HostRuntime.StartAsync(options);
        Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
        Assert.NotNull(runtime.Commands);
        Assert.NotNull(runtime.Grants);

        // ------------------------------------------------------------ AC1 precheck
        var translated = new List<(string PageId, string Sha, string RevisionId)>();
        var projectionResult = await runtime.Commands!.InvokeAsync(
            "library_get_reader_projection",
            Json($"{{\"chapter_id\":{Quote(ChapterId)},\"mode\":\"translated\",\"start_position\":\"beginning\"}}"));
        foreach (var page in projectionResult.Value.GetProperty("pages").EnumerateArray())
        {
            var translatedElement = page.GetProperty("translated");
            var sha = translatedElement.GetProperty("sha256");
            if (sha.ValueKind != JsonValueKind.String)
            {
                continue;
            }

            translated.Add((
                page.GetProperty("page_id").GetString()!,
                sha.GetString()!,
                translatedElement.GetProperty("artifact_revision_id").GetString()!));
        }

        Assert.Equal(3, translated.Count);
        var historyBefore = await runtime.Commands.InvokeAsync("library_get_export_history");
        var historyBeforeCount = historyBefore.Value.GetProperty("exports").GetArrayLength();

        // ------------------------------------------------------------ AC2 export
        var exportDirectory = Path.Combine(dataRoot, "exports");
        Directory.CreateDirectory(exportDirectory);
        var stamp = DateTimeOffset.UtcNow.ToString("yyyyMMdd-HHmmss");
        var target = Path.Combine(exportDirectory, $"book-fixture-{stamp}.zip");
        var pageIds = translated.Select(item => item.PageId).ToArray();
        var requestJson = JsonSerializer.Serialize(new
        {
            book_id = BookId,
            chapter_ids = new[] { ChapterId },
            ordered_page_ids = pageIds,
            format = "zip",
            format_options = new { compression = "standard" },
            stale_policy = "abort",
        });
        var request = Json(requestJson);

        var exportStarted = Stopwatch.StartNew();
        var startResult = await runtime.Grants!.StartExportAsync(request, target);
        var exportId = startResult.GetProperty("export_id").GetString()!;
        Assert.False(string.IsNullOrWhiteSpace(exportId));

        var timeline = new List<(double Ms, string? Status)>();
        JsonElement snapshot = default;
        string? status = null;
        while (exportStarted.Elapsed < ExportTimeout)
        {
            snapshot = await SnapshotAsync(runtime.Commands, exportId, CancellationToken.None);
            var current = snapshot.GetProperty("status").GetString();
            if (current != status)
            {
                timeline.Add((Math.Round(exportStarted.Elapsed.TotalMilliseconds, 1), current));
                status = current;
            }

            if (current is not null && TerminalStatuses.Contains(current))
            {
                break;
            }

            await Task.Delay(25);
        }

        Assert.Equal("completed", status);
        var output = snapshot.GetProperty("output");
        var outputPath = output.GetProperty("output_path").GetString()!;
        var snapshotSha = output.GetProperty("sha256").GetString()!;
        Assert.Equal(Path.GetFullPath(target), Path.GetFullPath(outputPath));
        Assert.True(File.Exists(outputPath), $"export artifact missing: {outputPath}");
        var artifactBytes = new FileInfo(outputPath).Length;
        var artifactSha = Sha256OfFile(outputPath);
        Assert.Equal(snapshotSha, artifactSha);

        // real archive: 3 page entries + manifest.json, every entry decodable and hash-pinned
        using var archive = ZipFile.OpenRead(outputPath);
        var entries = archive.Entries.ToDictionary(entry => entry.FullName, StringComparer.Ordinal);
        Assert.Equal(4, entries.Count);
        Assert.True(entries.ContainsKey("manifest.json"));
        using var manifestStream = entries["manifest.json"].Open();
        using var manifestDocument = JsonDocument.Parse(manifestStream);
        var manifestPages = manifestDocument.RootElement.GetProperty("pages").EnumerateArray().ToList();
        Assert.Equal(3, manifestPages.Count);
        var pageOrder = 0;
        foreach (var manifestPage in manifestPages)
        {
            pageOrder++;
            var pageId = manifestPage.GetProperty("page_id").GetString();
            var filename = manifestPage.GetProperty("filename").GetString()!;
            var manifestSha = manifestPage.GetProperty("sha256").GetString()!;
            var expected = translated.Single(item => item.PageId == pageId);
            Assert.StartsWith($"{pageOrder:0000}_", filename, StringComparison.Ordinal);
            Assert.Equal(expected.Sha, manifestSha);
            Assert.True(entries.ContainsKey(filename), $"archive entry missing: {filename}");
            using var pageStream = new MemoryStream();
            using (var entryStream = entries[filename].Open())
            {
                entryStream.CopyTo(pageStream);
            }

            Assert.Equal(manifestSha, Sha256OfBytes(pageStream.ToArray()));
            Assert.True(pageStream.Length > 0);
        }

        Assert.Equal(3, manifestDocument.RootElement.GetProperty("lineage").GetArrayLength());

        // history sees the same durable record
        var historyAfter = await runtime.Commands.InvokeAsync("library_get_export_history");
        var record = historyAfter.Value.GetProperty("exports")
            .EnumerateArray()
            .Single(entry => entry.GetProperty("export_id").GetString() == exportId);
        Assert.Equal("completed", record.GetProperty("status").GetString());
        Assert.Equal(Path.GetFullPath(target), Path.GetFullPath(record.GetProperty("output_path").GetString()!));
        Assert.Equal(record.GetProperty("sha256").GetString(), artifactSha);
        Assert.Equal(3, record.GetProperty("ordered_page_ids").GetArrayLength());

        // grant chain really went over the wire to the frozen Core
        Assert.Contains(runtime.CoreService!.Wire.Frames, frame =>
            frame.RequestLine.Contains("RegisterExportTarget", StringComparison.Ordinal));

        started.Stop();
        HostFixture.WriteEvidenceJson("export/export-success.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2");
            writer.WriteString("sidecar_core_service_sha256", sidecarSha);
            writer.WriteString("data_root", dataRoot);
            writer.WriteNumber("export_history_before", historyBeforeCount);
            writer.WriteString("book_id", BookId);
            writer.WriteString("chapter_id", ChapterId);
            writer.WriteStartArray("translated_pages");
            foreach (var (pageId, sha, revisionId) in translated)
            {
                writer.WriteStartObject();
                writer.WriteString("page_id", pageId);
                writer.WriteString("translated_sha256", sha);
                writer.WriteString("translated_revision_id", revisionId);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteString("export_id", exportId);
            writer.WriteString("format", "zip");
            writer.WriteString("target_path", Path.GetFullPath(target));
            writer.WriteNumber("artifact_bytes", artifactBytes);
            writer.WriteString("artifact_sha256", artifactSha);
            writer.WriteNumber("archive_entries", entries.Count);
            writer.WriteNumber("archive_page_entries", pageOrder);
            writer.WriteStartArray("snapshot_timeline");
            foreach (var (ms, state) in timeline)
            {
                writer.WriteStartObject();
                writer.WriteNumber("elapsed_ms", ms);
                writer.WriteString("status", state);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteStartObject("history_record");
            writer.WriteString("status", record.GetProperty("status").GetString());
            writer.WriteString("output_path", record.GetProperty("output_path").GetString());
            writer.WriteString("sha256", record.GetProperty("sha256").GetString());
            writer.WriteNumber("ordered_page_ids", record.GetProperty("ordered_page_ids").GetArrayLength());
            writer.WriteEndObject();
            writer.WriteNumber("host_start_to_export_complete_ms", Math.Round(started.Elapsed.TotalMilliseconds, 1));
            writer.WriteNumber("export_elapsed_ms", Math.Round(exportStarted.Elapsed.TotalMilliseconds, 1));
            writer.WriteEndObject();
        });
    }

    [HostSidecarFact]
    public async Task Export_Cancel_LeavesNoArtifact()
    {
        var sidecar = Env(SidecarVariable);
        var dataRoot = Env(DataRootVariable);
        if (sidecar is null || dataRoot is null)
        {
            return;
        }

        var options = new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", "export-e2e-cancel"),
            SidecarDirectoryOverride = sidecar,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            ParityReached = true,
            DetectLegacyShell = false,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(120),
            RequestTimeout = TimeSpan.FromSeconds(180),
        };
        await using var runtime = await HostRuntime.StartAsync(options);
        Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);

        // the three translated pages are stable inputs for every attempt
        var projection = await runtime.Commands!.InvokeAsync(
            "library_get_reader_projection",
            Json($"{{\"chapter_id\":{Quote(ChapterId)},\"mode\":\"translated\",\"start_position\":\"beginning\"}}"));
        var translated = new List<string>();
        foreach (var page in projection.Value.GetProperty("pages").EnumerateArray())
        {
            if (page.GetProperty("translated").GetProperty("sha256").ValueKind == JsonValueKind.String)
            {
                translated.Add(page.GetProperty("page_id").GetString()!);
            }
        }

        Assert.Equal(3, translated.Count);
        var exportDirectory = Path.Combine(dataRoot, "exports");
        Directory.CreateDirectory(exportDirectory);
        var requestJson = JsonSerializer.Serialize(new
        {
            book_id = BookId,
            chapter_ids = new[] { ChapterId },
            ordered_page_ids = translated,
            format = "zip",
            format_options = new { compression = "store" },
            stale_policy = "abort",
        });

        var attempts = new List<(string ExportId, string Target, string Status, bool FileExists, double Ms)>();
        var cancelled = false;
        for (var attempt = 1; attempt <= 5 && !cancelled; attempt++)
        {
            var target = Path.Combine(exportDirectory, $"book-fixture-cancel-{attempt}.zip");
            var started = Stopwatch.StartNew();
            var startResult = await runtime.Grants!.StartExportAsync(Json(requestJson), target);
            var exportId = startResult.GetProperty("export_id").GetString()!;
            // cancel immediately, while the job is still pending: the Core's job object must
            // flip to cancelled and must never publish a half-written file.
            await runtime.Commands.InvokeAsync(
                "library_cancel_export",
                Json($"{{\"export_id\":{Quote(exportId)}}}"));

            string? status = null;
            while (started.Elapsed < ExportTimeout)
            {
                var snapshot = await SnapshotAsync(runtime.Commands, exportId, CancellationToken.None);
                status = snapshot.GetProperty("status").GetString();
                if (status is not null && TerminalStatuses.Contains(status))
                {
                    break;
                }

                await Task.Delay(20);
            }

            var exists = File.Exists(target);
            attempts.Add((exportId, target, status ?? "timeout", exists, Math.Round(started.Elapsed.TotalMilliseconds, 1)));
            if (status == "cancelled")
            {
                Assert.False(exists, "a cancelled export must not leave a published artifact");
                cancelled = true;
            }
        }

        Assert.True(cancelled, "no cancel attempt reached the cancelled state (export too fast): " +
                               string.Join("; ", attempts.Select(a => $"{a.Status} file={a.FileExists}")));

        HostFixture.WriteEvidenceJson("export/export-cancel.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3");
            writer.WriteString("chapter_id", ChapterId);
            writer.WriteNumber("ordered_page_ids", translated.Count);
            writer.WriteStartArray("attempts");
            foreach (var (attemptExportId, target, status, exists, ms) in attempts)
            {
                writer.WriteStartObject();
                writer.WriteString("export_id", attemptExportId);
                writer.WriteString("target_path", Path.GetFullPath(target));
                writer.WriteString("terminal_status", status);
                writer.WriteBoolean("artifact_published", exists);
                writer.WriteNumber("elapsed_ms", ms);
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
            writer.WriteBoolean("cancelled_observed", cancelled);
            writer.WriteEndObject();
        });
    }
}
