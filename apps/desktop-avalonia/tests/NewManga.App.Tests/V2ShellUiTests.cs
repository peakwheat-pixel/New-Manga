using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.VisualTree;
using System.Security.Cryptography;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.Shell.V2.Studio;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.Views.V2.Library;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.App.Views.V2.Shell;
using NewManga.App.Views.V2.Shell.Controls;
using NewManga.App.Views.V2.Studio;
using NewManga.CoreClient;
using NewManga.DesignSystem;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Tests;

/// <summary>Test-only file picker gateway (the real one needs a window StorageProvider).</summary>
internal sealed class RecordingFilePicker : IFilePickerGateway
{
    public List<string> Files { get; } = new();

    public string? Folder { get; set; }

    public Task<IReadOnlyList<string>> PickFilesAsync(CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<string>>(Files.ToList());

    public Task<string?> PickFolderAsync(CancellationToken cancellationToken = default) =>
        Task.FromResult(Folder);

    public Task<string?> PickExportTargetAsync(
        string suggestedFileName,
        string suggestedDirectory,
        CancellationToken cancellationToken = default) =>
        Task.FromResult<string?>(null);
}

/// <summary>Shared deterministic Library fixture (real DTO shapes, no fake UI data).</summary>
internal static class V2Fixture
{
    public static FakeHostController Create()
    {
        var snapshot = new HostViewSnapshot(
            HostViewState.Ready,
            "Host 就绪 · core_service protocol 2.3",
            "读写（隔离数据根） · sidecars ready",
            null,
            null,
            new[]
            {
                new BookSummary("book-0", "夜光列车", "夜光列車", false, false, 240, "2026-10-20T00:00:00Z", "2026-10-29T00:00:00Z"),
                new BookSummary("book-1", "雨の停車場", string.Empty, false, false, 180, "2026-10-18T00:00:00Z", "2026-10-28T00:00:00Z"),
                new BookSummary("book-2", "汉江之夜", string.Empty, true, false, 92, "2026-10-10T00:00:00Z", "2026-10-27T00:00:00Z"),
                new BookSummary("book-3", "旧校舍的夏天", string.Empty, false, true, null, "2026-10-01T00:00:00Z", "2026-10-26T00:00:00Z"),
            },
            4,
            true,
            null);

        var fake = new FakeHostController(snapshot);
        fake.ChaptersByBook["book-0"] = new[]
        {
            new ChapterSummary("ch-0-0", "第 10 话 · 灯を消すな", "10", 0),
            new ChapterSummary("ch-0-1", "第 12 话 · 雨の停車場", "12", 1),
            new ChapterSummary("ch-0-2", "第 13 话 · 車掌の記憶", "13", 2),
        };
        fake.ChapterPagesByChapter["ch-0-1"] = new[]
        {
            new ChapterPageSummary("page-0", "001.jpg", 0),
            new ChapterPageSummary("page-1", "002.jpg", 1),
            new ChapterPageSummary("page-2", "003.jpg", 2),
            new ChapterPageSummary("page-3", "004.jpg", 3),
        };

        var readerPages = new[]
        {
            new ReaderPageData("page-0", 0, 1200, 1800, _ => Task.FromResult<byte[]?>(null)),
            new ReaderPageData("page-1", 1, 1200, 1800, _ => Task.FromResult<byte[]?>(null)),
            new ReaderPageData("page-2", 2, 1200, 1800, _ => Task.FromResult<byte[]?>(null)),
            new ReaderPageData("page-3", 3, 1200, 1800, _ => Task.FromResult<byte[]?>(null)),
        };
        fake.ReaderBooksByChapterId["ch-0-1"] = new ReaderBookData(
            "book-0",
            "夜光列车",
            "ch-0-1",
            "第 12 话 · 雨の停車場",
            "webtoon_vertical",
            readerPages);
        return fake;
    }

    /// <summary>Scrollable Library fixture (many books) for real ScrollViewer.Offset retention tests.</summary>
    public static FakeHostController CreateScrollable(int bookCount = 24)
    {
        var titles = new string[bookCount];
        for (var index = 0; index < bookCount; index++)
        {
            titles[index] = index == 0 ? "夜光列车" : $"书架测试 {index:D2}";
        }

        var fake = new FakeHostController(FakeHostController.ReadySnapshot(titles));
        fake.ChaptersByBook["book-0"] = new[]
        {
            new ChapterSummary("ch-0-0", "第 10 话 · 灯を消すな", "10", 0),
            new ChapterSummary("ch-0-1", "第 12 话 · 雨の停車場", "12", 1),
        };
        fake.ChapterPagesByChapter["ch-0-1"] = new[]
        {
            new ChapterPageSummary("page-0", "001.jpg", 0),
            new ChapterPageSummary("page-1", "002.jpg", 1),
        };
        return fake;
    }
    /// <summary>V11R-B-2: real settings/credential/export fixtures for the Console space tests.</summary>
    public static void AddConsoleData(FakeHostController fake)
    {
        fake.ProviderProfiles.Add(new ProviderProfileInfo(
            "provider-1",
            "openai",
            "OpenAI · GPT",
            new[] { SettingsCapabilities.Translation, SettingsCapabilities.Ocr },
            "https://api.example.invalid/v1",
            "gpt-4o-mini",
            null,
            true,
            "missing"));
        fake.ProviderProfiles.Add(new ProviderProfileInfo(
            "provider-2",
            "local",
            "本地 Provider",
            new[] { SettingsCapabilities.Inpaint, SettingsCapabilities.Rendering },
            "http://127.0.0.1:8080",
            "local-model",
            "network-1",
            false,
            "configured"));

        fake.NetworkProfiles.Add(new NetworkProfileInfo(
            "network-1",
            "公司代理",
            "HTTP",
            "127.0.0.1:7890",
            true,
            "enabled",
            false,
            "missing"));
        fake.NetworkProfiles.Add(new NetworkProfileInfo(
            "network-2",
            "直连",
            "Direct",
            null,
            true,
            "enabled",
            true,
            "missing"));

        fake.CredentialTargets.Add(new CredentialTargetOption(
            CredentialKinds.ProviderApi, "provider-1", "OpenAI · GPT", "missing"));
        fake.CredentialTargets.Add(new CredentialTargetOption(
            CredentialKinds.ProviderApi, "provider-2", "本地 Provider", "configured"));
        fake.CredentialTargets.Add(new CredentialTargetOption(
            CredentialKinds.ProxyAuth, "network-1", "公司代理", "missing"));

        for (var resolveSeed = 0; resolveSeed < 3; resolveSeed++)
        {
            fake.ScriptedNetworkResolveResults.Enqueue(new NetworkResolveInfo("network-1", "HTTP", "global_default"));
        }
        fake.ScriptedRunSnapshots.Enqueue(new RunSnapshotInfo(
            "run-1",
            "translate",
            new RunScopeInfo("chapter", BookId: "book-0", ChapterId: "ch-0-1"),
            "running",
            new[] { new RunTargetInfo("page-0", "page", 0), new RunTargetInfo("page-1", "page", 1) }));
        fake.ScriptedTaskProjections.Enqueue(new TaskProjectionInfo(
            "run-1",
            "running",
            "第 12 话 · 雨の停車場",
            0.5,
            "page-1",
            "inpaint",
            new[]
            {
                new RunStepFlowInfo("translate", "翻译", "completed"),
                new RunStepFlowInfo("inpaint", "修复", "running"),
            },
            new[]
            {
                new RunRowInfo("page-0", 0, "001.jpg", "completed", false, true, null),
                new RunRowInfo("page-1", 1, "002.jpg", "running", false, true, null),
            },
            new[]
            {
                new RunTaskInfo("task-1", "page-0", "completed", null, null, new[]
                {
                    new RunStepInfo("step-1", "translate", "completed", null, null, null, "openai", "gpt-4o-mini", "cpu"),
                }),
                new RunTaskInfo("task-2", "page-1", "running", null, null, Array.Empty<RunStepInfo>()),
            },
            new RunCountsInfo(Total: 2, Completed: 1, Failed: 0, Skipped: 0, Blocked: 0, Waiting: 1, Processing: 0),
            Array.Empty<string>(),
            new RunControlsInfo(true, true, false, true, false, false)));
        fake.ExportHistory.Add(new ExportHistoryEntry(
            "exp-1", "zip", "completed", null, null, 240, "2026-10-29T01:00:00Z"));
        fake.ScriptedRunSnapshots.Enqueue(new RunSnapshotInfo(
            "run-1",
            "translate",
            new RunScopeInfo("chapter", BookId: "book-0", ChapterId: "ch-0-1"),
            "running",
            new[] { new RunTargetInfo("page-0", "page", 0), new RunTargetInfo("page-1", "page", 1) }));
        fake.ScriptedTaskProjections.Enqueue(new TaskProjectionInfo(
            "run-1",
            "running",
            "第 12 话 · 雨の停車場",
            0.5,
            "page-1",
            "inpaint",
            new[]
            {
                new RunStepFlowInfo("translate", "翻译", "completed"),
                new RunStepFlowInfo("inpaint", "修复", "running"),
            },
            new[]
            {
                new RunRowInfo("page-0", 0, "001.jpg", "completed", false, true, null),
                new RunRowInfo("page-1", 1, "002.jpg", "running", false, true, null),
            },
            new[]
            {
                new RunTaskInfo("task-1", "page-0", "completed", null, null, new[]
                {
                    new RunStepInfo("step-1", "translate", "completed", null, null, null, "openai", "gpt-4o-mini", "cpu"),
                }),
                new RunTaskInfo("task-2", "page-1", "running", null, null, Array.Empty<RunStepInfo>()),
            },
            new RunCountsInfo(Total: 2, Completed: 1, Failed: 0, Skipped: 0, Blocked: 0, Waiting: 1, Processing: 0),
            Array.Empty<string>(),
            new RunControlsInfo(true, true, false, true, false, false)));
        fake.ExportHistory.Add(new ExportHistoryEntry(
            "exp-2", "pdf", "failed", null, null, 0, "2026-10-28T22:00:00Z"));
    }
}

/// <summary>
/// V11R-B-1 L1 evidence: real headless rendering (Skia, UseHeadlessDrawing=false) of the new shell.
/// Proves AC1/AC2/AC3/AC5 with actual pixels + control tree assertions, not placeholders.
/// </summary>
public sealed class V2ShellUiTests
{
    private static (Window Window, AppShellV2 Shell) Host(
        IHostController controller,
        double width = 1600,
        double height = 1000,
        IFilePickerGateway? picker = null)
    {
        TestTheme.ResetToDefaults();
        var shell = new AppShellV2(controller, picker);
        var window = new Window
        {
            Width = width,
            Height = height,
            Content = shell,
            Background = Brushes.Black,
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();
        return (window, shell);
    }

    private static async Task<(Window Window, AppShellV2 Shell)> HostReadyAsync(
        IHostController controller,
        double width = 1600,
        double height = 1000,
        IFilePickerGateway? picker = null)
    {
        var host = Host(controller, width, height, picker);
        await host.Shell.Initialization;
        Dispatcher.UIThread.RunJobs();
        return host;
    }

    private static async Task<(Window Window, AppShellV2 Shell)> HostWithThemeAsync(
        IHostController controller,
        DesignSystemThemeManager themeManager,
        double width = 1600,
        double height = 1000)
    {
        var shell = new AppShellV2(controller, themeManager: themeManager);
        var window = new Window
        {
            Width = width,
            Height = height,
            Content = shell,
            Background = Brushes.Black,
        };
        window.Show();
        await shell.Initialization;
        Dispatcher.UIThread.RunJobs();
        return (window, shell);
    }

    private static string ScreenshotSha256(Window window)
    {
        Dispatcher.UIThread.RunJobs();
        var frame = window.CaptureRenderedFrame()
            ?? throw new InvalidOperationException("CaptureRenderedFrame() returned null");
        using var stream = new MemoryStream();
        frame.Save(stream);
        return Convert.ToHexString(SHA256.HashData(stream.ToArray()));
    }

    /// <summary>R-19: temp-first capture (unique name incl. test method); repo sync only when curated.</summary>
    private static void Capture(Window window, string name, string task = "V11R-B-1", [System.Runtime.CompilerServices.CallerMemberName] string? testName = null)
    {
        Dispatcher.UIThread.RunJobs();
        var frame = window.CaptureRenderedFrame()
            ?? throw new InvalidOperationException($"{name}: CaptureRenderedFrame() returned null");
        var bytes = EvidenceFiles.SaveFrame(frame, task, name, testName);
        Assert.True(bytes is null or > 4096, $"{name}: {bytes} bytes — blank/placeholder screenshot");
    }

    private static Color ColorOf(object? resource) =>
        resource is ISolidColorBrush brush ? brush.Color : default;

    private static Color ResourceColor(string key) =>
        ColorOf(Application.Current!.TryGetResource(key, null, out var value) ? value : null);

    [AvaloniaFact]
    public async Task Shell_RendersAt1600x1000_WithTopBandStatusBandAndLibrary()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        Assert.True(window.IsVisible);
        Assert.Equal(1600d, window.ClientSize.Width);
        Assert.Equal(1000d, window.ClientSize.Height);

        var topBand = shell.GetVisualDescendants().OfType<NewManga.App.Views.V2.Shell.TopBand>().Single();
        Assert.Equal(36, topBand.Bounds.Height); // screen spec §1: TopBand = 36px
        Assert.NotNull(shell.GetVisualDescendants().OfType<LibraryView>().SingleOrDefault());

        // The library loaded the 4 books from the scripted Host snapshot (no fake UI data).
        Assert.Equal(4, shell.ViewModel.Library.Books.Count);
        Assert.Equal(4, shell.ViewModel.Library.ColumnCount); // screen spec §2: 4 columns at 1600
        Assert.Equal("book-0", shell.ViewModel.State.Selection.BookId);
        Assert.Equal("ch-0-0", shell.ViewModel.State.Selection.ChapterId);

        // Three real spaces registered and only Library is active at start.
        Assert.Equal(3, shell.ViewModel.SpaceTabs.Count);
        Assert.True(shell.ViewModel.State.CurrentSpace == SpaceId.Library);

        Capture(window, "01-library-dark-1600x1000");
        window.Close();
    }

    [AvaloniaFact]
    public async Task SpaceAndModeSwitch_KeepsSelectionFiltersAndTheSameViewModels()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.CreateScrollable());
        var libraryBefore = shell.ViewModel.Library;
        var booksViewBefore = shell.ViewModel.Library.Books;

        // Make the library context non-trivial.
        shell.ViewModel.Library.SearchText = string.Empty;
        await shell.ViewModel.Library.SelectBookAsync(shell.ViewModel.Library.AllBooks[0]);
        await shell.ViewModel.Library.SelectChapterAsync(
            shell.ViewModel.Library.Chapters.First(chapter => chapter.ChapterId == "ch-0-1"));
        shell.ViewModel.Library.SearchText = "书架";
        var libraryView = shell.GetVisualDescendants().OfType<LibraryView>().Single();
        await Task.Delay(60);
        Dispatcher.UIThread.RunJobs();
        libraryView.BooksScrollView!.Offset = new Vector(0, 180);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(180, shell.ViewModel.State.LibraryView.ScrollOffsetY, 1);
        shell.ViewModel.Library.TogglePageSelection(shell.ViewModel.Library.Pages[1]);

        Assert.True(shell.HandleKeyForTest(Key.D2, KeyModifiers.Control)); // Ctrl+2 → Studio
        Assert.Equal(SpaceId.Studio, shell.ViewModel.State.CurrentSpace);
        Assert.True(shell.HandleKeyForTest(Key.Tab, KeyModifiers.None)); // Tab → Batch
        Assert.Equal(StudioMode.Batch, shell.ViewModel.State.StudioMode);

        Assert.True(shell.HandleKeyForTest(Key.D1, KeyModifiers.Control)); // Ctrl+1 → Library
        Dispatcher.UIThread.RunJobs();

        // No ViewModel rebuild, no context loss.
        Assert.Same(libraryBefore, shell.ViewModel.Library);
        Assert.Same(booksViewBefore, shell.ViewModel.Library.Books);
        Assert.Equal("book-0", shell.ViewModel.State.Selection.BookId);
        Assert.Equal("书架", shell.ViewModel.Library.SearchText);
        Assert.Equal(180, shell.ViewModel.State.LibraryView.ScrollOffsetY, 1);
        Assert.Equal(1, shell.ViewModel.State.Selection.MultiPageCount);

        Capture(window, "03-library-context-retained");
        window.Close();
    }

    [AvaloniaFact]
    public async Task CommandPalette_JumpAndHelp_OpenWithKeyMap_AndCloseWithEsc()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        var viewModel = shell.ViewModel;

        Assert.True(shell.HandleKeyForTest(Key.K, KeyModifiers.Control));
        Assert.True(viewModel.IsPaletteOpen);
        Assert.NotEmpty(viewModel.PaletteItems);
        // Palette rows carry the frozen 「空间 · 模式 · 作用域」 annotation.
        Assert.All(viewModel.PaletteItems, entry => Assert.Contains(" · ", entry.Annotation, StringComparison.Ordinal));

        viewModel.PaletteQuery = "导出";
        Assert.Contains(viewModel.PaletteItems, entry => entry.Id == ShellCommandIds.Export);
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Assert.False(viewModel.IsPaletteOpen);

        Assert.True(shell.HandleKeyForTest(Key.P, KeyModifiers.Control));
        Assert.True(viewModel.IsJumpOpen);
        Assert.NotEmpty(viewModel.JumpItems);
        Capture(window, "05-quick-jump");
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));

        Assert.True(shell.HandleKeyForTest(Key.F1, KeyModifiers.None));
        Assert.True(viewModel.IsHelpOpen);
        Assert.NotEmpty(viewModel.HelpGroups);
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Assert.False(viewModel.IsHelpOpen);

        // Ctrl+K palette capture with a populated list.
        Assert.True(shell.HandleKeyForTest(Key.K, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();
        Capture(window, "04-command-palette");
        window.Close();
    }

    [AvaloniaFact]
    public async Task ImeSafety_LetterShortcutsYieldWhileTextInputIsFocused()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        var chapters = shell.ViewModel.Library.Chapters.ToList();
        var selectedBefore = shell.ViewModel.Library.SelectedChapter?.ChapterId;

        // J/K must NOT navigate while a text box has focus (IME safety, AC5).
        Assert.False(shell.HandleKeyForTest(Key.J, KeyModifiers.None, textInputFocused: true));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(selectedBefore, shell.ViewModel.Library.SelectedChapter?.ChapterId);

        // ... but the same key navigates when no text input is focused.
        Assert.True(shell.HandleKeyForTest(Key.J, KeyModifiers.None, textInputFocused: false));
        Dispatcher.UIThread.RunJobs();
        Assert.NotEqual(selectedBefore, shell.ViewModel.Library.SelectedChapter?.ChapterId);
        Assert.Equal(chapters.Count, shell.ViewModel.Library.Chapters.Count);

        // Ctrl+K is a control shortcut and still works while typing.
        Assert.True(shell.HandleKeyForTest(Key.K, KeyModifiers.Control, textInputFocused: true));
        window.Close();
    }

    [AvaloniaFact]
    public async Task ThemeToggle_SwapsTokens_WithoutRebuildingShellOrLosingSelection()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        var darkCanvas = ResourceColor("Nm.Color.Bg.Canvas");
        var bookBefore = shell.ViewModel.State.Selection.BookId;

        shell.ViewModel.ToggleThemeCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        var lightCanvas = ResourceColor("Nm.Color.Bg.Canvas");
        Assert.NotEqual(darkCanvas, lightCanvas);
        Assert.Equal(AppearanceMode.Light, ResolveManagerAppearance(shell));
        Assert.Equal(bookBefore, shell.ViewModel.State.Selection.BookId);
        Assert.False(shell.ViewModel.Library.IsLoading);

        Capture(window, "02-library-light-1600x1000");

        shell.ViewModel.ToggleThemeCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(darkCanvas, ResourceColor("Nm.Color.Bg.Canvas"));
        window.Close();
    }

    private static AppearanceMode? ResolveManagerAppearance(AppShellV2 shell)
    {
        var field = typeof(AppShellV2).GetField(
            "_themeManager",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        return (field?.GetValue(shell) as DesignSystemThemeManager)?.Appearance;
    }

    [AvaloniaFact]
    public async Task ImportDock_ReportsRealPerFileStatus_AndRetriesFailures()
    {
        var controller = V2Fixture.Create();
        controller.ScriptedImportResults.Enqueue(ImportOutcome.Success(1, 0));
        controller.ScriptedImportResults.Enqueue(ImportOutcome.Failed("IMPORT_FAILED", "坏文件：解码失败"));
        controller.ScriptedImportResults.Enqueue(ImportOutcome.Success(0, 1));

        var (window, shell) = await HostReadyAsync(controller);
        var library = shell.ViewModel.Library;
        await library.ImportDock.OpenWithFilesAsync(new[] { "/pick/001.jpg", "/pick/broken.jpg", "/pick/002.jpg" });
        Dispatcher.UIThread.RunJobs();

        var rows = library.ImportDock.Rows;
        Assert.Equal(3, rows.Count);
        Assert.Equal(ImportRowState.Imported, rows[0].State);
        Assert.Equal(ImportRowState.Failed, rows[1].State);
        Assert.Equal(ImportRowState.Skipped, rows[2].State);
        Assert.True(library.ImportDock.HasFailures);
        Assert.Contains("失败 1", library.ImportDock.Summary, StringComparison.Ordinal);
        // One Host call per file, each targeting the selected chapter (no fabricated aggregate).
        Assert.Equal(3, controller.ImportFileCalls.Count);
        Assert.All(controller.ImportFileCalls, call => Assert.Equal("ch-0-0", call.ChapterId));
        Assert.DoesNotContain("/pick", rows[0].DisplayName, StringComparison.Ordinal);

        // Retry only the failed row (real second Host call) → all terminal states are honest.
        controller.ScriptedImportResults.Enqueue(ImportOutcome.Success(1, 0));
        library.ImportDock.RetryFailedCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(ImportRowState.Imported, rows[1].State);
        Assert.False(library.ImportDock.HasFailures);
        Assert.Equal(4, controller.ImportFileCalls.Count);
        Capture(window, "06-import-dock-partial-retry");
        window.Close();
    }

    [AvaloniaFact]
    public async Task ImportDock_WithoutChapter_ShowsRealCreateChapterEntry_AndUnlocksImport()
    {
        var controller = V2Fixture.Create();
        controller.ChaptersByBook["book-0"] = Array.Empty<ChapterSummary>();
        controller.ScriptedCreateChapters.Enqueue(new ChapterSummary("ch-new", "第 14 话 · 新章", "14", 9));
        var (window, shell) = await HostReadyAsync(controller);
        var library = shell.ViewModel.Library;

        Assert.Null(library.SelectedChapter);
        await library.ImportDock.OpenWithFilesAsync(new[] { "/pick/010.jpg" });
        Dispatcher.UIThread.RunJobs();
        Assert.True(library.ImportDock.ShowCreateChapterEntry);
        Assert.False(library.ImportDock.HasTargetChapter);

        // The dock's "新建章节" entry opens the real inline form (no fake success).
        library.ImportDock.RequestCreateChapterCommand.Execute(null);
        Assert.True(library.IsCreateChapterOpen);
        library.NewChapterTitle = "第 14 话 · 新章";
        // Script the chapter list the Host will return after the create command.
        controller.ChaptersByBook["book-0"] = new[] { new ChapterSummary("ch-new", "第 14 话 · 新章", "14", 9) };
        await library.CreateChapterAsync();
        Dispatcher.UIThread.RunJobs();

        Assert.Equal(1, controller.CreateChapterCalls);
        Assert.Equal("book-0", controller.CreateChapterRequests[0].BookId);
        Assert.Equal("ch-new", library.SelectedChapter?.ChapterId);
        Assert.True(library.ImportDock.HasTargetChapter);

        controller.ScriptedImportResults.Enqueue(ImportOutcome.Success(1, 0));
        library.ImportDock.StartCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(ImportRowState.Imported, library.ImportDock.Rows[0].State);
        Assert.Equal("ch-new", controller.ImportFileCalls[0].ChapterId);
        window.Close();
    }

    [AvaloniaFact]
    public async Task RecycleBin_DangerConfirm_IsCancelable_AndBlockedConfirmWritesNothing()
    {
        var controller = V2Fixture.Create();
        var (window, shell) = await HostReadyAsync(controller);
        var library = shell.ViewModel.Library;

        library.ShowRecycleBinCommand.Execute(null);
        Assert.True(library.IsRecycleBinView);
        library.RecyclePurgeCommand.Execute(null);

        var viewModel = shell.ViewModel;
        Assert.True(viewModel.IsConfirmOpen);
        Assert.Contains("能力待接入", viewModel.ConfirmBlockedReason, StringComparison.Ordinal);
        Assert.False(viewModel.ConfirmCanConfirm);
        Capture(window, "07-recycle-danger-confirm");

        // Confirm is blocked: it must NOT execute anything destructive or pretend success.
        viewModel.ConfirmCommand.Execute(null);
        Assert.Contains("能力待接入", viewModel.NoticeText, StringComparison.Ordinal);

        // Esc cancels the modal (level-by-level exit).
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Assert.False(viewModel.IsConfirmOpen);

        // Escape on the recycle view returns to the bookshelf.
        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Assert.False(library.IsRecycleBinView);
        Assert.True(viewModel.State.CurrentSpace == SpaceId.Library);
        window.Close();
    }

    [AvaloniaFact]
    public async Task ReaderOverlay_ShowsDualProgress_Navigates_SavesAndExitsWithEsc()
    {
        var controller = V2Fixture.Create();
        var (window, shell) = await HostReadyAsync(controller);
        var library = shell.ViewModel.Library;
        await library.SelectBookAsync(library.AllBooks[0]);
        await library.SelectChapterAsync(library.Chapters.First(chapter => chapter.ChapterId == "ch-0-1"));
        Dispatcher.UIThread.RunJobs();

        library.OpenReaderCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();

        var reader = library.Reader;
        Assert.True(reader.IsOpen);
        Assert.True(shell.ViewModel.State.IsReaderOpen);
        Assert.Equal(4, reader.PageCount);
        Assert.Equal("第 1 / 4 页", reader.PageLabel);
        Assert.Contains("%", reader.ProgressText, StringComparison.Ordinal);
        // The overlay opens in the layout reported by the Core projection (webtoon_vertical here).
        Assert.True(reader.IsWebtoon);

        // ← → navigate (reader keyboard); layout + direction toggles are real state changes.
        Assert.True(shell.HandleKeyForTest(Key.Right, KeyModifiers.None));
        Assert.Equal(1, reader.PageIndex);
        reader.ToggleLayoutCommand.Execute(null);
        reader.ToggleDirectionCommand.Execute(null);
        Dispatcher.UIThread.RunJobs();
        Assert.True(reader.IsPaged);
        Assert.Equal("LTR", reader.DirectionLabel);

        Capture(window, "08-reader-overlay");

        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.False(reader.IsOpen);
        Assert.False(shell.ViewModel.State.IsReaderOpen);
        // Real progress save through IHostController (typed outcome mapped to honest text).
        Assert.NotEmpty(controller.Progress.Attempts);
        Assert.Equal("ch-0-1", controller.Progress.Attempts[^1].ChapterId);
        window.Close();
    }

    [AvaloniaFact]
    public async Task Shell_RendersStudioAndConsoleRouting_WithoutCrashing()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        Assert.True(shell.HandleKeyForTest(Key.D2, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(SpaceId.Studio, shell.ViewModel.State.CurrentSpace);
        var studioWorkspace = window.GetVisualDescendants().OfType<StudioWorkspaceView>().Single();
        Assert.True(studioWorkspace.IsVisible);
        Assert.True(shell.ViewModel.State.IsWorkspaceRegistered(SpaceId.Studio));
        Capture(window, "09-studio-page");
        Assert.True(shell.HandleKeyForTest(Key.D3, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(SpaceId.Console, shell.ViewModel.State.CurrentSpace);
        await shell.ViewModel.Console.InitializeAsync();
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(9, shell.ViewModel.Console.Sections.Count);
        Capture(window, "10-console-providers");
        window.Close();
    }

    [AvaloniaFact]
    public async Task Shell_RendersAt1280And1024_WithoutBreakingLayout()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create(), 1280, 800);
        Assert.Equal(1280d, window.ClientSize.Width);
        Assert.True(shell.ViewModel.IsCompact); // R-18 compact band 1280..1599
        Assert.Equal(3, shell.ViewModel.Library.ColumnCount); // screen spec §2: 3 columns at 1280
        Capture(window, "11-library-1280x800");
        window.Close();

        var (small, smallShell) = await HostReadyAsync(V2Fixture.Create(), 1024, 700);
        Assert.Equal(1024d, small.ClientSize.Width);
        Assert.True(smallShell.ViewModel.IsNarrow); // R-18 narrow band < 1280 (overlay detail)
        Assert.True(smallShell.ViewModel.Library.IsOverlayDetailVisible);
        Assert.Equal(4, smallShell.ViewModel.Library.ColumnCount);
        Capture(small, "12-library-1024x700");
        small.Close();
    }
    [AvaloniaFact]
    public async Task ScrollOffset_IsRealShellState_AndRestoredAcrossSpaceSwitches()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.CreateScrollable());
        var libraryView = shell.GetVisualDescendants().OfType<LibraryView>().Single();
        var scroll = libraryView.BooksScrollView;
        Assert.NotNull(scroll);
        Assert.True(scroll!.Extent.Height > scroll.Viewport.Height, "fixture must be scrollable");

        await Task.Delay(60);
        Dispatcher.UIThread.RunJobs();
        scroll.Offset = new Vector(0, 180);
        Dispatcher.UIThread.RunJobs();
        var afterSetState = shell.ViewModel.Library.ScrollOffsetY;
        var afterSetView = scroll.Offset.Y;
        Assert.True(shell.ViewModel.Library.ScrollOffsetY > 0, $"ScrollChanged must write the offset into ShellState (view={afterSetView}, state={afterSetState}, extent={scroll.Extent.Height}, viewport={scroll.Viewport.Height})");
        var persisted = shell.ViewModel.Library.ScrollOffsetY;

        Assert.True(shell.HandleKeyForTest(Key.D2, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(SpaceId.Studio, shell.ViewModel.State.CurrentSpace);
        Assert.True(shell.HandleKeyForTest(Key.D1, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();

        Assert.True(
            Math.Abs(persisted - shell.ViewModel.Library.ScrollOffsetY) < 1 && Math.Abs(persisted - scroll.Offset.Y) < 1,
            $"persisted={persisted} state={shell.ViewModel.Library.ScrollOffsetY} offset={scroll.Offset.Y} extent={scroll.Extent.Height} viewport={scroll.Viewport.Height}");
        window.Close();
    }

    [AvaloniaFact]
    public async Task LoadingState_RendersSameGeometrySkeleton_WithoutSelfJustifyingCopy()
    {
        var fake = V2Fixture.Create();
        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        fake.SnapshotGate = gate.Task;
        var shell = new AppShellV2(fake);
        var window = new Window { Width = 1600, Height = 1000, Content = shell, Background = Brushes.Black };
        window.Show();
        _ = shell.Initialization;
        Dispatcher.UIThread.RunJobs();
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.ViewModel.Library.CardWidth > 0, "viewport metrics must be computed");
        _ = shell.ViewModel.Library.RefreshAsync();
        await fake.SnapshotGateStarted.Task.WaitAsync(TimeSpan.FromSeconds(5));
        Dispatcher.UIThread.RunJobs();
        Assert.True(shell.ViewModel.Library.IsLoading, "the gated Host read must keep the loading state");
        var skeletonCards = shell.GetVisualDescendants()
            .OfType<Border>()
            .Count(border => border.Classes.Contains("card") && Math.Abs(border.Bounds.Width - shell.ViewModel.Library.CardWidth) < 1);
        Assert.True(skeletonCards >= 4, $"expected same-size skeleton cards, got {skeletonCards}");
        Capture(window, "13-library-loading-skeleton");

        gate.SetResult(true);
        await shell.Initialization;
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ViewModel.Library.IsLoading);
        window.Close();
    }

    // ── V11R-INT-0: CreateRoot / built-in workspaces / ThemeStudio / shared Run StatusBand ─────

    [AvaloniaFact]
    public async Task Int0_CreateRoot_BuildsStandaloneWindow_WithBuiltInWorkspaces()
    {
        var fake = V2Fixture.Create();
        var options = AppOptions.Parse(Array.Empty<string>());
        var window = AppShellV2.CreateRoot(fake, options);
        var shell = Assert.IsType<AppShellV2>(window.Content);
        Assert.Equal("New Manga", window.Title);
        Assert.Equal(options.WindowWidth, window.Width);
        Assert.Equal(options.WindowHeight, window.Height);
        Assert.Equal(1024, window.MinWidth); // DS Nm.Size.Breakpoint.Narrow
        window.Show();
        _ = shell.Initialization;
        await shell.Initialization;
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.ViewModel.State.IsWorkspaceRegistered(SpaceId.Library));
        Assert.True(shell.ViewModel.State.IsWorkspaceRegistered(SpaceId.Console));
        Assert.True(shell.ViewModel.State.IsWorkspaceRegistered(SpaceId.Studio));
        Capture(window, "14-int0-create-root", task: "V11R-INT-0");
        window.Close();
    }

    [AvaloniaFact]
    public async Task Int0_StudioSpace_RendersRealSurface_TabStaysInStudio()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        Assert.True(shell.HandleKeyForTest(Key.D2, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();

        var studioView = window.GetVisualDescendants().OfType<StudioWorkspaceView>().Single();
        Assert.True(studioView.IsVisible);
        Assert.True(studioView.ViewModel.IsPageMode);
        Capture(window, "15-int0-studio-page", task: "V11R-INT-0");

        // R-17: Studio owns Tab; the shell's StudioMode stays in sync instead of being toggled again.
        Assert.True(shell.HandleKeyForTest(Key.Tab, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(StudioMode.Batch, shell.ViewModel.State.StudioMode);
        Assert.True(studioView.ViewModel.IsBatchMode);

        Assert.True(shell.HandleKeyForTest(Key.D1, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(SpaceId.Library, shell.ViewModel.State.CurrentSpace);
        Assert.Equal("book-0", shell.ViewModel.State.Selection.BookId);
        Capture(window, "19-int0-three-spaces-context", task: "V11R-INT-0");
        window.Close();
    }

    [AvaloniaFact]
    public async Task Int0_ThemeStudio_OpensAsHonestPlaceholder_AndEscCloses()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        shell.ViewModel.OpenThemeStudio();
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.ViewModel.State.IsThemeStudioOpen);
        Assert.False(shell.ViewModel.IsThemeStudioWorkspaceRegistered);
        Assert.True(shell.ViewModel.IsThemeStudioPlaceholderVisible);
        var placeholder = window.GetVisualDescendants()
            .OfType<WorkspacePlaceholderView>()
            .Single(view => view.IsVisible && view.Title == "主题中心");
        Assert.Contains("尚未注册", placeholder.Detail, StringComparison.Ordinal);
        Capture(window, "16-int0-theme-studio-placeholder", task: "V11R-INT-0");

        Assert.True(shell.HandleKeyForTest(Key.Escape, KeyModifiers.None));
        Dispatcher.UIThread.RunJobs();
        Assert.False(shell.ViewModel.State.IsThemeStudioOpen);
        Assert.Equal("book-0", shell.ViewModel.State.Selection.BookId); // context untouched
        window.Close();
    }

    [AvaloniaFact]
    public async Task Int0_StatusBand_UsesSharedRunMonitor_AndHidesWithoutRun()
    {
        var fake = V2Fixture.Create();
        V2Fixture.AddConsoleData(fake);
        var (window, shell) = await HostReadyAsync(fake);

        shell.ViewModel.TrackRun("run-1");
        Dispatcher.UIThread.RunJobs();
        if (!shell.ViewModel.RunMonitor.HasSnapshot)
        {
            await shell.ViewModel.RunMonitor!.RefreshAsync();
            Dispatcher.UIThread.RunJobs();
        }

        Assert.True(shell.ViewModel.IsStatusBandVisible);
        Assert.Contains("run-1", shell.ViewModel.StatusBandLeft, StringComparison.Ordinal);
        Assert.Single(fake.RunSnapshotRequests); // one shared read per poll (R-24)
        Assert.Single(fake.TaskProjectionRequests);
        Capture(window, "17-int0-statusband-run", task: "V11R-INT-0");

        shell.ViewModel.TrackRun(null);
        Dispatcher.UIThread.RunJobs();
        // V11R-INT-2 (P0): the band is the always-visible Host readiness channel; without a Run the
        // Run summary disappears but the Host state stays visible.
        Assert.True(shell.ViewModel.IsStatusBandVisible);
        Assert.DoesNotContain("run-1", shell.ViewModel.StatusBandLeft, StringComparison.Ordinal);
        Assert.Contains("Host 就绪", shell.ViewModel.StatusBandLeft, StringComparison.Ordinal);
        window.Close();
    }

    [AvaloniaFact]
    public async Task Int0_UnregisteredStudio_ShowsHonestPlaceholder_NoFakeWorkspace()
    {
        var (window, shell) = await HostReadyAsync(V2Fixture.Create());
        Assert.True(shell.ViewModel.UnregisterWorkspace(SpaceId.Studio));
        Assert.True(shell.HandleKeyForTest(Key.D2, KeyModifiers.Control));
        Dispatcher.UIThread.RunJobs();

        Assert.True(shell.ViewModel.IsStudioPlaceholderVisible);
        Assert.DoesNotContain(window.GetVisualDescendants().OfType<StudioWorkspaceView>(), view => view.IsVisible);
        var placeholder = window.GetVisualDescendants()
            .OfType<WorkspacePlaceholderView>()
            .Single(view => view.IsVisible && view.Title == "工位");
        Assert.Contains("尚未注册", placeholder.Detail, StringComparison.Ordinal);
        Capture(window, "18-int0-studio-unregistered", task: "V11R-INT-0");
        window.Close();
    }

    // ── V11R-INT-2: Host startup P0 + --variant appearance ─────────────────────────────────

    [AvaloniaFact]
    public async Task Int2_V2Shell_StartsHostBeforeFirstDataRead_AndShowsHostReady()
    {
        var fake = V2Fixture.Create();
        var (window, shell) = await HostReadyAsync(fake);

        Assert.Equal(1, fake.StartCalls); // v2 initialization requested startup exactly once
        Assert.Equal(HostViewState.Ready, fake.Snapshot.State);
        var firstStart = fake.LifecycleLog.IndexOf("start");
        var firstRefresh = fake.LifecycleLog.IndexOf("refresh");
        Assert.True(firstStart >= 0, "v2 shell never called IHostController.StartAsync (P0 regression)");
        Assert.True(firstRefresh < 0 || firstStart < firstRefresh,
            $"Host must start before the first data read; log={string.Join(",", fake.LifecycleLog)}");

        Assert.True(shell.ViewModel.IsStatusBandVisible);
        Assert.Contains("Host 就绪", shell.ViewModel.StatusBandLeft, StringComparison.Ordinal);
        Assert.True(shell.ViewModel.IsHostReady);
        Assert.Equal(NmStatus.Done, shell.ViewModel.StatusBandState);
        Capture(window, "01-int2-host-ready", task: "V11R-INT-2");

        // Re-awaiting initialization (window attach, deep link, external callers) must not start twice.
        await shell.Initialization;
        await shell.Initialization;
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(1, fake.StartCalls);
        window.Close();
    }

    [AvaloniaFact]
    public async Task Int2_HostStartFailure_IsSurfacedInStatusBand_WithoutCrashing()
    {
        var fake = V2Fixture.Create();
        fake.StartException = new InvalidOperationException("sidecar bundle missing: TYPED_E2E_FAILURE");
        var (window, shell) = await HostReadyAsync(fake);

        Assert.Equal(1, fake.StartCalls);
        Assert.True(shell.ViewModel.HasHostFailure);
        Assert.Contains("Host 启动失败", shell.ViewModel.StatusBandLeft, StringComparison.Ordinal);
        Assert.Contains("TYPED_E2E_FAILURE", shell.ViewModel.StatusBandLeft, StringComparison.Ordinal);
        Assert.Equal(NmStatus.Failed, shell.ViewModel.StatusBandState);
        Assert.True(shell.ViewModel.IsStatusBandVisible);
        Capture(window, "04-int2-host-start-failure", task: "V11R-INT-2");
        window.Close();
    }

    [AvaloniaFact]
    public async Task Int2_VariantDarkAndLight_ResolveDifferentTokensAndScreenshots()
    {
        TestTheme.ResetToDefaults();
        var darkManager = new DesignSystemThemeManager(Application.Current!);
        Assert.True(darkManager.Initialize(AppearanceMode.Dark));
        var (darkWindow, darkShell) = await HostWithThemeAsync(V2Fixture.Create(), darkManager);
        Assert.True(darkShell.ViewModel.IsDarkTheme);
        var darkColor = ResourceColor(NmKeys.Color.Bg.App);
        var darkHash = ScreenshotSha256(darkWindow);
        Capture(darkWindow, "02-int2-variant-dark", task: "V11R-INT-2");
        darkWindow.Close();
        darkManager.Dispose();

        var lightManager = new DesignSystemThemeManager(Application.Current!);
        Assert.True(lightManager.Initialize(AppearanceMode.Light));
        var (lightWindow, lightShell) = await HostWithThemeAsync(V2Fixture.Create(), lightManager);
        Assert.False(lightShell.ViewModel.IsDarkTheme);
        var lightColor = ResourceColor(NmKeys.Color.Bg.App);
        var lightHash = ScreenshotSha256(lightWindow);
        Capture(lightWindow, "03-int2-variant-light", task: "V11R-INT-2");
        lightWindow.Close();
        lightManager.Dispose();

        Assert.NotEqual(darkColor, lightColor);
        Assert.NotEqual(darkHash, lightHash);
        TestTheme.ResetToDefaults();
    }

    [Fact]
    public void Int2_SingleHostStartup_CallSites_AreOnlyTheLegacyShellAndTheV2ViewModel()
    {
        var root = FindAppSourceRoot();
        var mainWindow = File.ReadAllText(Path.Combine(root, "Views", "MainWindow.axaml.cs"));
        var shellVm = File.ReadAllText(Path.Combine(root, "ViewModels", "V2", "Shell", "AppShellViewModel.cs"));
        var app = File.ReadAllText(Path.Combine(root, "App.axaml.cs"));

        Assert.Equal(1, CountOccurrences(mainWindow, "_controller.StartAsync("));
        Assert.Equal(1, CountOccurrences(shellVm, "_controller.StartAsync("));
        Assert.DoesNotContain("StartAsync(", app, StringComparison.Ordinal);
    }

    [AvaloniaFact]
    public async Task Int2_LibraryCenterState_HasExactlyOneVisibleBlock_ForEveryCombination()
    {
        // (a) Host not ready + empty shelf -> only the Host state (highest priority).
        var starting = new HostViewSnapshot(
            HostViewState.Starting, "正在启动 Host…", "—", null, null,
            Array.Empty<BookSummary>(), 0, true, null);
        var (hostWindow, hostShell) = await HostReadyAsync(new FakeHostController(starting));
        Assert.True(VisibleEmptyStateCount(hostWindow) == 1, "visible states: " + string.Join(" | ", VisibleEmptyStateTitles(hostWindow)));
        Assert.Equal("Host 尚未就绪", VisibleEmptyStateTitle(hostWindow));
        Assert.False(hostShell.ViewModel.Library.ShowEmptyLibraryState);
        hostWindow.Close();

        // (b) Ready + empty shelf -> only the empty-shelf state.
        var (emptyWindow, emptyShell) = await HostReadyAsync(new FakeHostController(FakeHostController.ReadySnapshot()));
        Assert.True(VisibleEmptyStateCount(emptyWindow) == 1, "visible states: " + string.Join(" | ", VisibleEmptyStateTitles(emptyWindow)));
        Assert.Equal("书架还是空的", VisibleEmptyStateTitle(emptyWindow));
        Assert.True(emptyShell.ViewModel.Library.ShowEmptyLibraryState);
        Capture(emptyWindow, "05-int2-library-empty-only", task: "V11R-INT-2");
        emptyWindow.Close();

        // (c) Ready + loading -> only the same-geometry skeleton (no empty state in the tree).
        var gated = V2Fixture.Create();
        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        gated.SnapshotGate = gate.Task;
        var (loadingWindow, loadingShell) = Host(gated);
        _ = loadingShell.Initialization;
        await gated.SnapshotGateStarted.Task.WaitAsync(TimeSpan.FromSeconds(5));
        Dispatcher.UIThread.RunJobs();
        Assert.Equal(0, VisibleEmptyStateCount(loadingWindow));
        Assert.True(VisibleSkeletonCardCount(loadingWindow, loadingShell.ViewModel.Library.CardWidth) >= 4,
            "loading must show the same-geometry skeleton cards");
        Assert.True(loadingShell.ViewModel.Library.ShowLoadingState);
        Capture(loadingWindow, "06-int2-library-loading-only", task: "V11R-INT-2");
        gate.SetResult(true);
        await loadingShell.Initialization;
        loadingWindow.Close();

        // (d) Ready + error -> only the error block (error outranks empty states).
        var failing = V2Fixture.Create();
        failing.RefreshException = new InvalidOperationException("TYPED_READ_FAILURE");
        var (errorWindow, errorShell) = await HostReadyAsync(failing);
        Assert.True(VisibleEmptyStateCount(errorWindow) == 1, "visible states: " + string.Join(" | ", VisibleEmptyStateTitles(errorWindow)));
        Assert.Equal("书架读取失败", VisibleEmptyStateTitle(errorWindow));
        Assert.True(errorShell.ViewModel.Library.ShowErrorState);
        errorWindow.Close();

        // (e) Ready + data + zero filter matches -> only the no-results state.
        var (resultsWindow, resultsShell) = await HostReadyAsync(V2Fixture.Create());
        resultsShell.ViewModel.Library.SearchText = "zzz-no-such-book";
        Dispatcher.UIThread.RunJobs();
        Assert.True(VisibleEmptyStateCount(resultsWindow) == 1, "visible states: " + string.Join(" | ", VisibleEmptyStateTitles(resultsWindow)));
        Assert.Equal("没有匹配的作品", VisibleEmptyStateTitle(resultsWindow));
        Assert.True(resultsShell.ViewModel.Library.ShowNoResultsState);
        resultsWindow.Close();
    }

    private static int VisibleEmptyStateCount(Window window) =>
        CenterStateHost(window).GetVisualDescendants().OfType<EmptyState>().Count(state => state.IsEffectivelyVisible);

    private static string VisibleEmptyStateTitle(Window window) =>
        CenterStateHost(window).GetVisualDescendants().OfType<EmptyState>()
            .Single(state => state.IsEffectivelyVisible && state.Title.Length > 0)
            .Title;

    private static IEnumerable<string> VisibleEmptyStateTitles(Window window) =>
        CenterStateHost(window).GetVisualDescendants().OfType<EmptyState>()
            .Where(state => state.IsEffectivelyVisible)
            .Select(state => state.Title);

    private static Grid CenterStateHost(Window window) =>
        window.GetVisualDescendants().OfType<Grid>().Single(grid => grid.Name == "LibraryCenterStateHost");

    private static int VisibleSkeletonCardCount(Window window, double cardWidth) =>
        window.GetVisualDescendants()
            .OfType<Border>()
            .Count(border => border.Classes.Contains("card")
                && border.IsEffectivelyVisible
                && Math.Abs(border.Bounds.Width - cardWidth) < 1);

    private static int CountOccurrences(string text, string token)
    {
        var count = 0;
        var index = 0;
        while ((index = text.IndexOf(token, index, StringComparison.Ordinal)) >= 0)
        {
            count++;
            index += token.Length;
        }

        return count;
    }

    private static string FindAppSourceRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var candidate = Path.Combine(directory.FullName, "apps", "desktop-avalonia", "src", "NewManga.App");
            if (Directory.Exists(candidate))
            {
                return candidate;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException("apps/desktop-avalonia/src/NewManga.App not found above the test binaries");
    }
}
