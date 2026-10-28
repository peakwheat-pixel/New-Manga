using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Views;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// READER-LIBRARY-WIRE-1: the reader page consumes the real library payload
/// (ListBooks → list_chapters → GetReaderProjection) and the immersive window is reachable
/// (button/double-click) with Esc/H/F/arrow behavior. Fixtures stay as the fallback source.
/// </summary>
public sealed class ReaderLibraryTests
{
    // 1x1 PNG: exercises the real "bytes → Bitmap" decode path without a sidecar.
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    private static byte[] OnePixelPng() => Convert.FromBase64String(OnePixelPngBase64);

    private static ReaderBookData FakeBook(int pages = 8, string layout = "webtoon_vertical")
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
            layout,
            items);
    }

    [AvaloniaFact]
    public async Task ReaderPage_Loads_Library_Book_And_Renders_Paged_Page()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(FakeBook(layout: "rtl"));
        Assert.NotNull(page.LibraryBook);
        Assert.Equal(8, page.ViewModel.PageCount);
        Assert.Contains("BOOK-FIXTURE-1", page.LibraryTitle.Text);
        await page.WaitForPageAsync(0);
        Assert.NotNull(page.PageImage.Source);
    }

    [AvaloniaFact]
    public async Task ReaderPage_Loads_Library_Webtoon_Stack()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        page.SetViewport(1200, 800, 2.0);
        page.LoadLibrary(FakeBook());
        Assert.NotNull(page.LibraryBook);
        Assert.True(page.LibraryBook!.IsWebtoon);
        Assert.Equal(ReaderFitMode.Webtoon, page.ViewModel.FitMode);
        Assert.True(page.WebtoonScroll.IsVisible);
        await page.WaitForPageAsync(0);
        await page.WaitForPageAsync(7);
    }

    [AvaloniaFact]
    public void ReaderPage_Empty_State_Keeps_Fixture_Fallback()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        page.SetLibraryEmpty("书架为空");
        Assert.Null(page.LibraryBook);
        Assert.True(page.EmptyState.IsVisible);
        Assert.Equal("fixture 回退", page.LibraryTitle.Text);
    }

    [AvaloniaFact]
    public void ReaderPage_Requests_Immersive_From_Button_And_Api()
    {
        var page = new ReaderPage(new ReaderViewModel(), Array.Empty<string>());
        var requested = 0;
        page.ImmersiveRequested += (_, _) => requested++;
        Assert.NotNull(page.ImmersiveButton);
        Assert.Equal("ImmersiveButton", page.ImmersiveButton.Name);
        page.RequestImmersive();
        Assert.Equal(1, requested);
    }

    [AvaloniaFact]
    public void ReaderWindow_Escape_Closes_And_H_F_Arrow_Keys_Work()
    {
        var viewModel = new ReaderViewModel();
        var window = new ReaderWindow(viewModel, FakeBook());
        window.Show();
        Dispatcher.UIThread.RunJobs();
        Assert.NotNull(window.Page.LibraryBook);

        var hudBefore = viewModel.HudVisible;
        Assert.True(window.TryHandleKey(Key.H));
        Assert.NotEqual(hudBefore, viewModel.HudVisible);

        var fitBefore = viewModel.FitMode;
        Assert.True(window.TryHandleKey(Key.F));
        Assert.NotEqual(fitBefore, viewModel.FitMode);

        var pageBefore = viewModel.CurrentPageIndex;
        Assert.True(window.TryHandleKey(Key.Right));
        Assert.NotEqual(pageBefore, viewModel.CurrentPageIndex);

        Assert.True(window.TryHandleKey(Key.Escape));
        Assert.Equal(1, window.EscapeCount);
        Assert.False(window.IsVisible);
    }

    [AvaloniaFact]
    public async Task MainWindow_Reader_Uses_Library_Book_And_Opens_Immersive()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot("BOOK-FIXTURE-1 日漫_JA 测试书"));
        controller.ReaderBook = FakeBook();
        var window = new MainWindow(controller, new AppOptions());
        await window.EnsureReaderLoadedAsync();
        Assert.True(controller.ReaderLoadCalled);
        Assert.NotNull(window.Reader.LibraryBook);
        Assert.Equal(8, window.Reader.ViewModel.PageCount);

        var immersive = window.OpenImmersiveReader();
        Dispatcher.UIThread.RunJobs();
        Assert.NotNull(window.LastImmersiveWindow);
        Assert.NotNull(immersive.Page.LibraryBook);
        immersive.Close();
    }

    [AvaloniaFact]
    public async Task MainWindow_Reader_Fixture_Override_Keeps_Fallback()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        controller.ReaderBook = FakeBook();
        Environment.SetEnvironmentVariable("NEWMANGA_READER_SOURCE", "fixtures");
        try
        {
            var window = new MainWindow(controller, new AppOptions());
            await window.EnsureReaderLoadedAsync();
            Assert.Null(window.Reader.LibraryBook);
            Assert.True(window.Reader.EmptyState.IsVisible);
        }
        finally
        {
            Environment.SetEnvironmentVariable("NEWMANGA_READER_SOURCE", null);
        }
    }

    [AvaloniaFact]
    public async Task MainWindow_Reader_Empty_Library_Shows_Empty_State()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        controller.ReaderBook = null;
        var window = new MainWindow(controller, new AppOptions());
        await window.EnsureReaderLoadedAsync();
        Assert.Null(window.Reader.LibraryBook);
        Assert.True(window.Reader.EmptyState.IsVisible);
    }
}
