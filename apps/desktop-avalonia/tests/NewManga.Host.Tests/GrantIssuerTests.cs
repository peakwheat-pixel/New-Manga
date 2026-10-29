using System.Text.Json;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// GRANT-ISSUER-1 end-to-end: real sidecars, isolated writable data root. Proves the C# HostIssuer
/// chain against the frozen Core (signature bytes must match or the Core answers REF_SIGNATURE_INVALID):
///   - import: host_issuer grant → RegisterImportSource (host-control) → ImportPages (application);
///   - export: host_issuer grant → RegisterExportTarget (host-control) → StartExport (application);
///   - shell actions: whitelisted directories only, typed refusals otherwise.
/// </summary>
public sealed class GrantIssuerTests
{
    private static string RepoRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null &&
               !Directory.Exists(Path.Combine(directory.FullName, "verification")))
        {
            directory = directory.Parent;
        }

        return directory?.FullName ?? throw new InvalidOperationException("repo root not found");
    }

    /// <summary>
    /// Deterministic import sources. The repo ships one real page fixture
    /// (<c>verification/CORE-SLIM-1/ac1/fixtures/alpha.png</c>, a decodable 40x30 RGBA PNG); the
    /// grant/import chain only needs real decodable images, so it is copied under distinct names.
    /// A valid embedded 1x1 PNG is the fallback for checkouts that lack verification/.
    /// </summary>
    private static IReadOnlyList<string> FixtureImages(int count)
    {
        const string embeddedPng =
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
        var repoImage = Path.Combine(RepoRoot(), "verification", "CORE-SLIM-1", "ac1", "fixtures", "alpha.png");
        var bytes = File.Exists(repoImage)
            ? File.ReadAllBytes(repoImage)
            : Convert.FromBase64String(embeddedPng);
        var folder = Path.Combine(Path.GetTempPath(), "grant-fixtures-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(folder);
        var paths = new List<string>();
        for (var index = 0; index < count; index++)
        {
            var path = Path.Combine(folder, $"page-{index + 1:00}.png");
            File.WriteAllBytes(path, bytes);
            paths.Add(path);
        }

        return paths;
    }

    private static JsonElement Json(string text)
    {
        using var document = JsonDocument.Parse(text);
        return document.RootElement.Clone();
    }

    [HostSidecarFact]
    public async Task Import_IntoNewChapter_Executes_AndRegistersGrant()
    {
        var options = HostFixture.CreateOptions("grant-import", out var dataRoot, parity: true);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.NotNull(runtime.Grants);
            Assert.NotNull(runtime.Commands);
            Assert.NotNull(runtime.CoreService!.HostSession);

            var book = await runtime.CreateBookAsync("GRANT-ISSUER-1 import fixture");
            var chapter = await runtime.CreateChapterAsync(book.BookId, "ch-1");
            var images = FixtureImages(8);
            Assert.Equal(8, images.Count);

            var pathsJson = JsonSerializer.Serialize(images);
            var imported = await runtime.Commands!.InvokeAsync(
                "library_import_file",
                Json($"{{\"chapter_id\":\"{chapter.ChapterId}\",\"paths\":{pathsJson},\"duplicate_policy\":\"import_as_new\"}}"));
            Assert.Equal(
                8,
                imported.Value.GetProperty("imported_files").GetInt32());

            var projection = await runtime.GetReaderProjectionAsync(chapter.ChapterId, "beginning");
            Assert.Equal(8, projection.Pages.Count);

            var grantsEvidence = Directory.GetFiles(runtime.Grants!.EvidenceDirectory, "import-*.json");
            Assert.NotEmpty(grantsEvidence);
            var evidenceText = File.ReadAllText(grantsEvidence[0]);
            Assert.Contains("\"registered\":true", evidenceText, StringComparison.Ordinal);
            Assert.Contains("\"operation\":\"import\"", evidenceText, StringComparison.Ordinal);

            HostFixture.WriteEvidenceJson("grants/import-success.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1");
                writer.WriteString("book_id", book.BookId);
                writer.WriteString("chapter_id", chapter.ChapterId);
                writer.WriteNumber("source_files", images.Count);
                writer.WriteNumber("imported_files", imported.Value.GetProperty("imported_files").GetInt32());
                writer.WriteNumber("projection_pages", projection.Pages.Count);
                writer.WriteBoolean("host_session_opened", runtime.CoreService!.HostSession is not null);
                writer.WriteNumber("core_wire_frames", runtime.CoreService.Wire.Count);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [HostSidecarFact]
    public async Task Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages()
    {
        var options = HostFixture.CreateOptions("grant-export", out var dataRoot, parity: true);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            var book = await runtime.CreateBookAsync("GRANT-ISSUER-1 export fixture");
            var chapter = await runtime.CreateChapterAsync(book.BookId, "ch-1");
            var imported = await runtime.Commands!.InvokeAsync(
                "library_import_file",
                Json($"{{\"chapter_id\":\"{chapter.ChapterId}\",\"paths\":{JsonSerializer.Serialize(FixtureImages(2))},\"duplicate_policy\":\"import_as_new\"}}"));
            Assert.Equal(2, imported.Value.GetProperty("imported_files").GetInt32());
            var projection = await runtime.GetReaderProjectionAsync(chapter.ChapterId, "beginning");
            var pageIds = projection.Pages.Select(page => page.PageId).ToList();

            var exportDirectory = Path.Combine(dataRoot, "exports");
            Directory.CreateDirectory(exportDirectory);
            var target = Path.Combine(exportDirectory, "grant-probe.pdf");
            var request = Json(
                $"{{\"book_id\":\"{book.BookId}\",\"chapter_ids\":[\"{chapter.ChapterId}\"],\"ordered_page_ids\":{JsonSerializer.Serialize(pageIds)},\"format\":\"pdf\",\"format_options\":{{\"pdf_content\":\"image_only\"}},\"stale_policy\":\"abort\"}}");

            // The grant is registered with the Core (host-control round trip) before StartExport;
            // the frozen Core then refuses because BOOK-FIXTURE-style imports have no translated
            // pages yet (the translation chain is a separate slice) — a typed refusal, never a fake
            // success.
            var error = await Assert.ThrowsAsync<CoreOperationException>(
                () => runtime.Grants!.StartExportAsync(request, target));
            Assert.Equal("EXPORT_INPUT_UNAVAILABLE", error.Code);

            var exportEvidence = Directory.GetFiles(runtime.Grants!.EvidenceDirectory, "export-*.json");
            Assert.NotEmpty(exportEvidence);
            var text = File.ReadAllText(exportEvidence[0]);
            Assert.Contains("\"registered\":true", text, StringComparison.Ordinal);
            Assert.Contains(runtime.CoreService!.Wire.Frames, frame =>
                frame.RequestLine.Contains("RegisterExportTarget", StringComparison.Ordinal));

            // Arbitrary user paths are refused before any grant is minted.
            var outside = Path.Combine(Path.GetTempPath(), "grant-outside", "x.pdf");
            Directory.CreateDirectory(Path.GetDirectoryName(outside)!);
            var refused = await Assert.ThrowsAsync<ShellActionException>(
                () => runtime.Grants!.StartExportAsync(request, outside));
            Assert.Equal("EXPORT_PATH_UNAVAILABLE", refused.Code);

            HostFixture.WriteEvidenceJson("grants/export-attempt.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC1/AC2/AC3");
                writer.WriteString("book_id", book.BookId);
                writer.WriteString("typed_error", error.Code);
                writer.WriteBoolean("grant_registered", true);
                writer.WriteBoolean("outside_path_refused", refused.Code == "EXPORT_PATH_UNAVAILABLE");
                writer.WriteString("translated_pages_available", "false (translation chain is a separate slice)");
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    /// <summary>
    /// Manual AC2 evidence run: the real opener (explorer.exe) is exercised only when
    /// NEWMANGA_REAL_SHELL=1, because it opens a visible desktop window. The directory is the Host
    /// data root's plugins folder (whitelist path); the screenshot evidence is captured by the
    /// task harness after this test returns.
    /// </summary>
    [HostSidecarFact]
    public async Task ShellActions_RealOpener_OpensExplorer_WhenEnabled()
    {
        if (Environment.GetEnvironmentVariable("NEWMANGA_REAL_SHELL") != "1")
        {
            return;
        }

        var root = Environment.GetEnvironmentVariable("NEWMANGA_REAL_SHELL_ROOT");
        if (string.IsNullOrWhiteSpace(root))
        {
            throw new InvalidOperationException("NEWMANGA_REAL_SHELL_ROOT is required for the real-shell run");
        }

        Directory.CreateDirectory(root);
        var options = new HostOptions
        {
            DataRoot = root,
            LogDirectory = Path.Combine(root, "logs"),
            SidecarDirectoryOverride = HostFixture.SidecarDirectory,
            MutexName = @"Local\NewManga.Host.RealShell." + Guid.NewGuid().ToString("N")[..12],
            ParityReached = true,
            DetectLegacyShell = false,
            EnableWireEvidence = false,
            StartupTimeout = TimeSpan.FromSeconds(60),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
        await using var runtime = await HostRuntime.StartAsync(options);
        Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
        await runtime.Grants!.OpenPluginsDirectoryAsync();
        var pluginDirectory = Path.Combine(Path.GetFullPath(root), "plugins");
        Assert.True(Directory.Exists(pluginDirectory));
        HostFixture.WriteEvidenceJson("grants/real-shell-opened.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2");
            writer.WriteString("opened_directory", pluginDirectory);
            writer.WriteBoolean("explorer_launched", true);
            writer.WriteEndObject();
        });
        await Task.Delay(1500);
    }

    [HostSidecarFact]
    public async Task ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths()
    {
        var options = HostFixture.CreateOptions("grant-shell", out var dataRoot, parity: true);
        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            var opened = new List<string>();
            var coordinator = new HostGrantCoordinator(
                runtime.CoreService!,
                options.DataRoot,
                options.LogDirectory,
                TimeSpan.FromSeconds(30),
                directory => opened.Add(directory));

            await coordinator.OpenPluginsDirectoryAsync();
            var pluginDirectory = Path.Combine(Path.GetFullPath(options.DataRoot), "plugins");
            Assert.Equal(new[] { pluginDirectory }, opened);
            Assert.True(Directory.Exists(pluginDirectory));

            var outside = Assert.Throws<ShellActionException>(
                () => coordinator.EnsureWithinRoot(@"C:\Windows", "PLUGIN_DIRECTORY_UNAVAILABLE"));
            Assert.Equal("PLUGIN_DIRECTORY_UNAVAILABLE", outside.Code);

            var unknownExport = await Assert.ThrowsAsync<ShellActionException>(
                () => coordinator.RevealExportFolderAsync("export-does-not-exist"));
            Assert.Equal("EXPORT_PATH_UNAVAILABLE", unknownExport.Code);

            HostFixture.WriteEvidenceJson("grants/shell-actions.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2/AC3");
                writer.WriteBoolean("plugins_directory_created", Directory.Exists(pluginDirectory));
                writer.WriteString("opened_directory", opened[0]);
                writer.WriteString("outside_path_code", outside.Code);
                writer.WriteString("unknown_export_code", unknownExport.Code);
                writer.WriteEndObject();
            });
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }
}
