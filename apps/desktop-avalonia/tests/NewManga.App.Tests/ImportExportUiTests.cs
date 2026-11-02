using System.Text.Json;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Threading;
using NewManga.App;
using NewManga.App.Services;
using NewManga.App.Views;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// IMPORT-EXPORT-UI-1 AC3: headless coverage of the import/export entries.
///
/// Everything is driven through the real page controls and the real controller seam
/// (<see cref="IHostController"/>), with a recording fake + a fake system picker:
///  * import: picker → destination book/chapter → exact import call parameters → result text
///    → shelf refresh (only on success);
///  * export: reader context → translated pages → StartExport parameters → snapshot state
///    transitions (running → completed / cancelled) → history + reveal.
/// No real files, no real Core, no fabricated result: every assertion is on the controller
/// traffic or on the Host-reported typed outcome.
/// </summary>
public sealed class ImportExportUiTests
{
    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static void Pump() => Dispatcher.UIThread.RunJobs();

    private sealed class FakePicker : IFilePickerGateway
    {
        public Queue<IReadOnlyList<string>> Files { get; } = new();

        public Queue<string?> Folders { get; } = new();

        public int FilePickCalls { get; private set; }

        public int FolderPickCalls { get; private set; }

        public Task<IReadOnlyList<string>> PickFilesAsync(CancellationToken cancellationToken = default)
        {
            FilePickCalls++;
            return Task.FromResult(Files.Count > 0 ? Files.Dequeue() : (IReadOnlyList<string>)Array.Empty<string>());
        }

        public Task<string?> PickFolderAsync(CancellationToken cancellationToken = default)
        {
            FolderPickCalls++;
            return Task.FromResult(Folders.Count > 0 ? Folders.Dequeue() : null);
        }

        public Task<string?> PickExportTargetAsync(
            string suggestedFileName,
            string suggestedDirectory,
            CancellationToken cancellationToken = default) =>
            Task.FromResult<string?>(null);
    }

    private static FakeHostController ReadyHost(string bookId = "book-0", string title = "书一")
    {
        var fake = new FakeHostController(FakeHostController.ReadySnapshot(title));
        fake.ChaptersByBook[bookId] = new[] { new ChapterSummary("ch-1", "第 1 章", "1", 0) };
        return fake;
    }

    private static (MainWindow Window, FakeHostController Host, FakePicker Picker) OpenShell()
    {
        var host = ReadyHost();
        var picker = new FakePicker();
        var window = new MainWindow(host, new AppOptions(), picker);
        window.Show();
        Pump();
        return (window, host, picker);
    }

    // ---------------------------------------------------------------- AC3 payload contract

    [AvaloniaFact]
    public void Payloads_MatchTheImportExportCommandFaces()
    {
        var importFile = ImportExportPayloads.LibraryImportFile("ch-1", new[] { "a.png" }, "skip");
        Assert.Equal(
            new[] { "chapter_id", "duplicate_policy", "paths" },
            importFile.EnumerateObject().Select(property => property.Name).OrderBy(name => name));
        Assert.Equal("ch-1", importFile.GetProperty("chapter_id").GetString());

        var importFolder = ImportExportPayloads.LibraryImportFolder("ch-1", "C:/in", "import_as_new");
        Assert.Equal(
            new[] { "chapter_id", "duplicate_policy", "path" },
            importFolder.EnumerateObject().Select(property => property.Name).OrderBy(name => name));

        var export = ImportExportPayloads.StartExportRequest("book-0", new[] { "ch-1" }, new[] { "p1", "p2" });
        var keys = export.EnumerateObject().Select(property => property.Name).OrderBy(name => name).ToArray();
        Assert.Equal(
            new[] { "book_id", "chapter_ids", "format", "format_options", "ordered_page_ids", "stale_policy" },
            keys);
        // The Host appends the minted target_ref itself; the UI request must not carry one.
        Assert.DoesNotContain("target_ref", keys);
        Assert.Equal("zip", export.GetProperty("format").GetString());
        Assert.Equal("standard", export.GetProperty("format_options").GetProperty("compression").GetString());
        Assert.Equal("abort", export.GetProperty("stale_policy").GetString());

        var exportId = ImportExportPayloads.ExportId("exp-1");
        Assert.Equal(new[] { "export_id" }, exportId.EnumerateObject().Select(property => property.Name));
        Assert.Equal("exp-1", exportId.GetProperty("export_id").GetString());

        var name = ImportExportFormatting.DefaultExportFileName("书/名:称", "第 1 章");
        Assert.EndsWith(".zip", name);
        Assert.DoesNotContain('/', name);
        Assert.DoesNotContain(':', name);
        Assert.StartsWith("书_名_称-第 1 章-", name);

        Evidence.Write("import-export-ui/payload-contract.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3");
            writer.WriteString("scope", "import/export wire payload builders");
            writer.WriteStartArray("import_file_keys");
            foreach (var key in importFile.EnumerateObject().Select(property => property.Name).OrderBy(k => k))
            {
                writer.WriteStringValue(key);
            }

            writer.WriteEndArray();
            writer.WriteStartArray("import_folder_keys");
            foreach (var key in importFolder.EnumerateObject().Select(property => property.Name).OrderBy(k => k))
            {
                writer.WriteStringValue(key);
            }

            writer.WriteEndArray();
            writer.WriteStartArray("start_export_keys");
            foreach (var key in keys)
            {
                writer.WriteStringValue(key);
            }

            writer.WriteEndArray();
            writer.WriteString("start_export_format", export.GetProperty("format").GetString());
            writer.WriteString("start_export_compression", export.GetProperty("format_options").GetProperty("compression").GetString());
            writer.WriteString("start_export_stale_policy", export.GetProperty("stale_policy").GetString());
            writer.WriteBoolean("target_ref_appended_by_host_only", !keys.Contains("target_ref"));
            writer.WriteString("default_export_file_name", name);
            writer.WriteEndObject();
        });
    }

    // ---------------------------------------------------------------- AC1 import

    [AvaloniaFact]
    public async Task Bookshelf_ImportFiles_CallsHostWithPickerPathsChapterAndRefreshes()
    {
        var (window, host, picker) = OpenShell();
        picker.Files.Enqueue(new[] { "C:\\in\\a.png", "C:\\in\\b.png" });
        var refreshBefore = host.RefreshCalls;

        Click(window.BookshelfPageControl.ImportFilesButton);
        await window.BookshelfPageControl.LastImportOperation;
        Pump();

        var panel = window.BookshelfPageControl.ImportPanelControl;
        Assert.NotNull(panel);
        Assert.True(panel!.IsVisible);
        Assert.Equal(1, picker.FilePickCalls);
        Assert.Equal(2, panel.SelectedPaths.Count);
        Assert.NotNull(panel.ChapterSelector.SelectedItem);

        Click(panel.StartButton);
        await panel.LastOperation;
        Pump();

        var call = Assert.Single(host.ImportFileCalls);
        Assert.Equal("ch-1", call.ChapterId);
        Assert.Equal(new[] { "C:\\in\\a.png", "C:\\in\\b.png" }, call.Paths);
        Assert.Equal("skip", call.DuplicatePolicy);
        Assert.True(host.RefreshCalls > refreshBefore, "a successful import must refresh the shelf");
        Assert.Contains("已导入 2 个文件", panel.StatusText.Text);
        Evidence.Write("import-export-ui/import-files.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC3");
            writer.WriteString("entry", "BookshelfPage.ImportFilesButton");
            writer.WriteString("picker_files_returned", "C:\\in\\a.png, C:\\in\\b.png");
            writer.WriteString("host_chapter_id", call.ChapterId);
            writer.WriteNumber("host_paths", call.Paths.Count);
            writer.WriteString("host_duplicate_policy", call.DuplicatePolicy);
            writer.WriteBoolean("shelf_refreshed", host.RefreshCalls > refreshBefore);
            writer.WriteString("panel_status", panel.StatusText.Text);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Bookshelf_ImportFolder_PassesTheFolderPathAndPolicy()
    {
        var (window, host, picker) = OpenShell();
        picker.Folders.Enqueue("C:\\in\\chapter-01");

        Click(window.BookshelfPageControl.ImportFolderButton);
        await window.BookshelfPageControl.LastImportOperation;
        Pump();
        var panel = window.BookshelfPageControl.ImportPanelControl!;
        panel.PolicySelector.SelectedIndex = 1; // import_as_new

        Click(panel.StartButton);
        await panel.LastOperation;
        Pump();

        var call = Assert.Single(host.ImportFolderCalls);
        Assert.Equal("ch-1", call.ChapterId);
        Assert.Equal("C:\\in\\chapter-01", call.FolderPath);
        Assert.Equal("import_as_new", call.DuplicatePolicy);
        Assert.Empty(host.ImportFileCalls);
        Evidence.Write("import-export-ui/import-folder.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC3");
            writer.WriteString("entry", "BookshelfPage.ImportFolderButton");
            writer.WriteString("host_chapter_id", call.ChapterId);
            writer.WriteString("host_folder_path", call.FolderPath);
            writer.WriteString("host_duplicate_policy", call.DuplicatePolicy);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Bookshelf_ImportTypedFailure_ShowsCodeAndDoesNotRefresh()
    {
        var (window, host, picker) = OpenShell();
        picker.Files.Enqueue(new[] { "C:\\in\\bad.png" });
        host.ScriptedImportResults.Enqueue(
            ImportOutcome.Failed("IMPORT_SOURCE_UNAVAILABLE", "导入失败：源文件不可用"));
        var refreshBefore = host.RefreshCalls;

        Click(window.BookshelfPageControl.ImportFilesButton);
        await window.BookshelfPageControl.LastImportOperation;
        Pump();
        var panel = window.BookshelfPageControl.ImportPanelControl!;
        Click(panel.StartButton);
        await panel.LastOperation;
        Pump();

        Assert.Contains("IMPORT_SOURCE_UNAVAILABLE", panel.StatusText.Text);
        Assert.Equal(refreshBefore, host.RefreshCalls);
        Assert.Single(host.ImportFileCalls);
    }

    [AvaloniaFact]
    public async Task Bookshelf_ImportPickerCancel_LeavesFlowClosed()
    {
        var (window, host, picker) = OpenShell();
        picker.Files.Enqueue(Array.Empty<string>());

        Click(window.BookshelfPageControl.ImportFilesButton);
        await window.BookshelfPageControl.LastImportOperation;
        Pump();

        Assert.False(window.BookshelfPageControl.ImportPanelControl!.IsVisible);
        Assert.Contains("未选择文件", window.BookshelfPageControl.StatusLine);
        Assert.Empty(host.ImportFileCalls);
        Assert.Empty(host.ImportFolderCalls);
    }

    [AvaloniaFact]
    public async Task Workbench_ImportFiles_OpensTheSameFlow()
    {
        var (window, host, picker) = OpenShell();
        picker.Files.Enqueue(new[] { "C:\\in\\w.png" });

        Click(window.Workbench.ImportFilesButton);
        await window.Workbench.LastImportOperation;
        Pump();

        var panel = window.Workbench.ImportPanelControl;
        Assert.NotNull(panel);
        Assert.True(panel!.IsVisible);
        Assert.Equal(1, picker.FilePickCalls);

        Click(panel.StartButton);
        await panel.LastOperation;
        Pump();
        Assert.Single(host.ImportFileCalls);
        Assert.True(host.RefreshCalls >= 1);
    }

    // ---------------------------------------------------------------- AC2 export

    private static ReaderBookData ExportBook() => new(
        "book-0",
        "书一",
        "ch-1",
        "第 1 章",
        "single",
        new[]
        {
            new ReaderPageData("p1", 0, 800, 1200),
            new ReaderPageData("p2", 1, 800, 1200),
        });

    private static (MainWindow Window, FakeHostController Host, FakePicker Picker) OpenReaderWithExport()
    {
        var host = ReadyHost();
        host.ReaderBook = ExportBook();
        host.ExportDirectorySuggestionValue = Path.Combine(Path.GetTempPath(), "import-export-ui-exports");
        host.TranslatedPagesByChapter["ch-1"] = new[] { "p1", "p2" };
        var picker = new FakePicker();
        var window = new MainWindow(host, new AppOptions(), picker);
        window.Show();
        Pump();
        return (window, host, picker);
    }

    [AvaloniaFact]
    public async Task Reader_ExportFlow_StartPollCompleteHistoryReveal()
    {
        var (window, host, _) = OpenReaderWithExport();
        var loaded = await window.LoadReaderAsync(null, null);
        Assert.True(loaded);
        Pump();
        Assert.True(window.Reader.ExportButton.IsVisible);

        Click(window.Reader.ExportButton);
        await window.Reader.LastExportOperation;
        Pump();
        var panel = window.Reader.ExportPanelControl;
        Assert.NotNull(panel);
        panel!.AutoPoll = false;
        Assert.True(panel.IsVisible);
        Assert.True(panel.StartButton.IsEnabled);
        Assert.Contains("2 页已翻译内容", panel.StatusText.Text);

        host.ScriptedSnapshots.Enqueue(
            ExportSnapshotInfo.FromState("exp-fake-1", ExportJobState.Running, 1, 2));
        host.ScriptedSnapshots.Enqueue(
            ExportSnapshotInfo.FromState(
                "exp-fake-1",
                ExportJobState.Completed,
                2,
                2,
                Path.Combine(host.ExportDirectorySuggestionValue, "out.zip"),
                "abc123",
                format: "zip"));
        host.ExportHistory = new List<ExportHistoryEntry>
        {
            new ExportHistoryEntry(
                "exp-fake-1",
                "zip",
                "completed",
                Path.Combine(host.ExportDirectorySuggestionValue, "out.zip"),
                "abc123",
                2,
                "2026-10-27T00:00:00Z"),
        };

        Click(panel.StartButton);
        await panel.LastOperation;
        Pump();

        var startCall = Assert.Single(host.StartExportCalls);
        Assert.Equal("book-0", startCall.BookId);
        Assert.Equal("ch-1", startCall.ChapterId);
        Assert.Equal(new[] { "p1", "p2" }, startCall.PageIds);
        Assert.StartsWith(host.ExportDirectorySuggestionValue, startCall.TargetPath);
        Assert.EndsWith(".zip", startCall.TargetPath);

        // first snapshot: running (1/2) → progress visible, cancel offered
        Assert.Contains("导出中", panel.StatusText.Text);
        Assert.True(panel.ProgressBar.IsVisible);
        Assert.Equal(50d, panel.ProgressBar.Value);
        Assert.True(panel.CancelButton.IsEnabled);

        // second snapshot: completed → reveal + history
        await panel.TickAsync();
        Pump();
        Assert.Contains("导出完成", panel.StatusText.Text);
        Assert.True(panel.RevealButton.IsEnabled);
        Assert.False(panel.CancelButton.IsEnabled);
        Assert.Single(panel.HistoryList.ItemsSource!.OfType<string>());

        Evidence.Write("import-export-ui/export-flow.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2/AC3");
            writer.WriteString("entry", "ReaderPage.ExportButton -> ExportPanel");
            writer.WriteString("book_id", startCall.BookId);
            writer.WriteString("chapter_id", startCall.ChapterId);
            writer.WriteNumber("page_ids", startCall.PageIds.Count);
            writer.WriteString("target_path", startCall.TargetPath);
            writer.WriteBoolean("target_inside_host_exports_dir", startCall.TargetPath.StartsWith(host.ExportDirectorySuggestionValue, StringComparison.Ordinal));
            writer.WriteStartArray("snapshot_states");
            writer.WriteStringValue("running(1/2)");
            writer.WriteStringValue("completed(2/2)");
            writer.WriteEndArray();
            writer.WriteStartObject("history");
            writer.WriteString("export_id", "exp-fake-1");
            writer.WriteString("status", "completed");
            writer.WriteString("sha256", "abc123");
            writer.WriteEndObject();
            writer.WriteEndObject();
        });

        Click(panel.RevealButton);
        await panel.LastOperation;
        Pump();
        Assert.Equal("exp-fake-1", Assert.Single(host.RevealCalls));
        Assert.Contains("已打开导出目录", panel.StatusText.Text);
        Evidence.Write("import-export-ui/export-reveal.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC2/AC3");
            writer.WriteString("reveal_export_id", Assert.Single(host.RevealCalls));
            writer.WriteString("status_text", panel.StatusText.Text);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Reader_ExportCancel_WhileRunning_MarksRecordCancelled()
    {
        var (window, host, _) = OpenReaderWithExport();
        await window.LoadReaderAsync(null, null);
        Pump();
        Click(window.Reader.ExportButton);
        await window.Reader.LastExportOperation;
        Pump();
        var panel = window.Reader.ExportPanelControl!;
        panel.AutoPoll = false;

        host.ScriptedSnapshots.Enqueue(
            ExportSnapshotInfo.FromState("exp-fake-1", ExportJobState.Running, 0, 2));
        Click(panel.StartButton);
        await panel.LastOperation;
        Pump();
        Assert.True(panel.CancelButton.IsEnabled);

        Click(panel.CancelButton);
        await panel.LastOperation;
        Pump();

        Assert.Equal("exp-fake-1", Assert.Single(host.CancelCalls));
        Assert.Contains("已取消", panel.StatusText.Text);
        Assert.False(panel.RevealButton.IsEnabled);
        Evidence.Write("import-export-ui/export-cancel.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC3");
            writer.WriteString("cancelled_export_id", Assert.Single(host.CancelCalls));
            writer.WriteString("terminal_status", "cancelled");
            writer.WriteString("status_text", panel.StatusText.Text);
            writer.WriteBoolean("reveal_disabled_after_cancel", !panel.RevealButton.IsEnabled);
            writer.WriteEndObject();
        });
    }

    [AvaloniaFact]
    public async Task Reader_ExportWithoutTranslatedPages_DisablesStart()
    {
        var host = ReadyHost();
        host.ReaderBook = ExportBook();
        host.ExportDirectorySuggestionValue = Path.Combine(Path.GetTempPath(), "import-export-ui-exports");
        var picker = new FakePicker();
        var window = new MainWindow(host, new AppOptions(), picker);
        window.Show();
        Pump();
        await window.LoadReaderAsync(null, null);
        Pump();

        Click(window.Reader.ExportButton);
        await window.Reader.LastExportOperation;
        Pump();

        var panel = window.Reader.ExportPanelControl!;
        Assert.False(panel.StartButton.IsEnabled);
        Assert.Contains("没有可导出的翻译页", panel.StatusText.Text);
        Assert.Empty(host.StartExportCalls);
    }

    [AvaloniaFact]
    public async Task Reader_ExportStartRefused_ShowsTypedReason()
    {
        var (window, host, _) = OpenReaderWithExport();
        await window.LoadReaderAsync(null, null);
        Pump();
        Click(window.Reader.ExportButton);
        await window.Reader.LastExportOperation;
        Pump();
        var panel = window.Reader.ExportPanelControl!;
        panel.AutoPoll = false;
        host.ScriptedStartResults.Enqueue(null);

        Click(panel.StartButton);
        await panel.LastOperation;
        Pump();

        Assert.Contains("导出被拒绝", panel.StatusText.Text);
        Assert.Null(panel.ActiveExportId);
        Assert.Single(host.StartExportCalls);
    }
}
