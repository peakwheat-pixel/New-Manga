using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Views;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// READER-OVERLAY-HEADLESS-PNG-1: render the immersive reader (ReaderWindow) to a PNG in a
/// headless session, so the reader overlay has VISUAL evidence without a physical F11.
///
/// Why this exists: `GATE3-READER-OVERLAY-1` proved `PostMessage(WM_KEYDOWN, VK_F11)` does NOT
/// open the overlay on a real window, so the overlay had no screenshot. `ReaderWindow` derives
/// from `Window` (ReaderWorkbenchPages.cs:2583) and `Residual2Evidence.Capture` uses
/// `window.CaptureRenderedFrame()` (Residual2Evidence.cs:133-137), which works for any Window.
///
/// This test ADDS evidence; it does not relax anything:
///   - it reuses the same F11 path the existing F11HotkeyTests drive (production public method);
///   - it keeps the same positive assertions (IsVisible / PageCount / restore page);
///   - it never skips. If rendering fails, the test fails loudly.
/// </summary>
public sealed class ImmersiveReaderVisualEvidenceTests
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    private static byte[] OnePixelPng() => Convert.FromBase64String(OnePixelPngBase64);

    private static ReaderBookData FakeBook(int pages = 8)
    {
        var items = Enumerable.Range(0, pages)
            .Select(index => new ReaderPageData(
                $"page-{index}",
                index,
                1200,
                1660,
                _ => Task.FromResult<byte[]?>(OnePixelPng())))
            .ToList();
        return new ReaderBookData(
            "book-fixture-1",
            "BOOK-FIXTURE-1 日漫_JA 测试书",
            "chapter-1",
            "第 1 章",
            "webtoon_vertical",
            items);
    }

    private static MainWindow NewWindow()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot("BOOK-FIXTURE-1 日漫_JA 测试书"));
        controller.ReaderBook = FakeBook();
        return new MainWindow(controller, LegacyUiTestOptions.Isolated());
    }

    /// <summary>
    /// Opens the immersive reader through the production F11 path, asserts the same invariants
    /// the existing hotkey test asserts, then renders the overlay window to a PNG on disk.
    /// </summary>
    [AvaloniaFact]
    public async Task ImmersiveReader_AfterF11_RendersToPng()
    {
        var window = NewWindow();
        Assert.Equal("bookshelf", window.CurrentPage);

        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();

        var immersive = window.LastImmersiveWindow;
        Assert.NotNull(immersive);
        Assert.True(immersive!.IsVisible);
        Assert.Equal("reader", window.CurrentPage);
        Assert.NotNull(window.Reader.LibraryBook);
        Assert.Equal(8, immersive.Page.ViewModel.PageCount);
        Assert.Equal("bookshelf", window.ImmersiveRestorePage);

        // Render. This throws (never skips) if the platform cannot capture a frame.
        using var bitmap = Residual2Evidence.Capture(immersive);
        Assert.True(bitmap.PixelSize.Width > 0 && bitmap.PixelSize.Height > 0,
            $"captured frame has invalid size {bitmap.PixelSize}");

        var root = Residual2Evidence.Root;
        // GOV-TEST-SIDE-EFFECT-1: the canonical evidence lives in the repo, but a plain test run
        // (test.ps1 without -CanonicalEvidence) must not rewrite those pinned bytes. The runner
        // points this at its own evidence root; unset means "repo path", i.e. the old behaviour.
        var overlayOverride = Environment.GetEnvironmentVariable("NEWMANGA_READER_OVERLAY_EVIDENCE_DIR");
        var output = string.IsNullOrWhiteSpace(overlayOverride)
            ? Path.Combine(root, "verification", "READER-OVERLAY-HEADLESS-PNG-1")
            : Path.Combine(overlayOverride, "READER-OVERLAY-HEADLESS-PNG-1");
        Directory.CreateDirectory(output);
        var path = Path.Combine(output, "immersive-reader.png");
        bitmap.Save(path);

        var bytes = new FileInfo(path).Length;
        Assert.True(bytes > 0, "rendered PNG is empty");

        var sha = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(path)));
        var head = Residual2Evidence.Git("rev-parse", "HEAD");
        File.WriteAllText(Path.Combine(output, "render-info.md"),
            "# READER-OVERLAY-HEADLESS-PNG-1\n\n" +
            $"渲染 HEAD：`{head}`\n\n" +
            "| 项 | 值 |\n|---|---|\n" +
            $"| 文件 | `immersive-reader.png` |\n" +
            $"| 尺寸 | {bitmap.PixelSize.Width}x{bitmap.PixelSize.Height} |\n" +
            $"| 字节 | {bytes} |\n" +
            $"| SHA256 | `{sha}` |\n" +
            $"| 来源 | `[AvaloniaFact]` headless + `Window.CaptureRenderedFrame()` |\n" +
            $"| 入口 | production `MainWindow.TryHandleGlobalKey(Key.F11)` |\n" +
            $"| 命令 | `dotnet test --filter FullyQualifiedName~ImmersiveReaderVisualEvidenceTests` |\n\n" +
            "**这张图是 headless 渲染，不是真实显示器截图。** 它证明 `ReaderWindow` 的内容树能渲染出非空帧，\n" +
            "不证明真实窗口在物理屏幕上的显示效果。签署：NOT_RUN。\n");
    }
}
