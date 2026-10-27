using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Shell;
using NewManga.App.Views;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// F11-HOTKEY-1: application-level F11 toggles the immersive reader.
/// Record Decision: bare F11 only (no modifiers); ignored while a text input has focus; pressed
/// outside the reader the app first enters the reader page for the current book and remembers that
/// page, so closing the immersive window (Esc or F11) returns there; pressed on the reader page the
/// return target stays the reader page. No OS-global hotkey is registered.
/// </summary>
public sealed class F11HotkeyTests
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

    private static MainWindow NewWindow(bool withBook = true)
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot("BOOK-FIXTURE-1 日漫_JA 测试书"));
        controller.ReaderBook = withBook ? FakeBook() : null;
        return new MainWindow(controller, new AppOptions());
    }

    [AvaloniaFact]
    public async Task F11_FromBookshelf_OpensImmersiveForCurrentBook_AndEscRestoresBookshelf()
    {
        var window = NewWindow();
        Assert.Equal("bookshelf", window.CurrentPage);

        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();

        var immersive = window.LastImmersiveWindow;
        Assert.NotNull(immersive);
        Assert.True(immersive!.IsVisible);
        Assert.Equal("reader", window.CurrentPage); // F11 first enters the reader page
        Assert.NotNull(window.Reader.LibraryBook);
        Assert.Equal(8, immersive.Page.ViewModel.PageCount);
        Assert.Equal("bookshelf", window.ImmersiveRestorePage);

        // Esc inside the immersive window closes it and returns to the page F11 came from.
        Assert.True(immersive.TryHandleKey(Key.Escape));
        Dispatcher.UIThread.RunJobs();
        Assert.Null(window.LastImmersiveWindow);
        Assert.Null(window.ImmersiveRestorePage);
        Assert.Equal("bookshelf", window.CurrentPage);
        window.Close();
    }

    [AvaloniaFact]
    public async Task F11_WhileImmersiveIsOpen_ClosesItAndRestoresOriginPage()
    {
        var window = NewWindow();
        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();
        var immersive = window.LastImmersiveWindow;
        Assert.NotNull(immersive);

        // Second F11 is the toggle-off half: no restart of the reader, window closes.
        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();

        Assert.False(immersive!.IsVisible);
        Assert.Null(window.LastImmersiveWindow);
        Assert.Equal("bookshelf", window.CurrentPage);
        window.Close();
    }

    [AvaloniaFact]
    public async Task F11_OnReaderPage_ReturnsToReaderPageAfterClose()
    {
        var window = NewWindow();
        window.Navigate("reader");
        await window.EnsureReaderLoadedAsync();
        Dispatcher.UIThread.RunJobs();
        Assert.Equal("reader", window.CurrentPage);

        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();
        Assert.NotNull(window.LastImmersiveWindow);
        Assert.Null(window.ImmersiveRestorePage); // origin was the reader page

        Assert.True(window.LastImmersiveWindow!.TryHandleKey(Key.Escape));
        Dispatcher.UIThread.RunJobs();
        Assert.Null(window.LastImmersiveWindow);
        Assert.Equal("reader", window.CurrentPage);
        window.Close();
    }

    [AvaloniaFact]
    public async Task F11_IsIgnoredWhileSearchBoxHasFocus_AndDoesNotEatText()
    {
        var window = NewWindow();
        window.Show();
        Dispatcher.UIThread.RunJobs();
        var search = window.BookshelfPageControl.SearchBox;
        search.Text = "雾港";
        search.Focus();
        Dispatcher.UIThread.RunJobs();
        Assert.True(
            window.IsTextInputFocused(),
            $"search.IsFocused={search.IsFocused} focused={window.FocusManager?.GetFocusedElement()?.GetType().Name}");

        Assert.False(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();

        Assert.Null(window.LastImmersiveWindow);
        Assert.Equal("bookshelf", window.CurrentPage);
        Assert.Equal("雾港", search.Text); // the hotkey neither fires nor modifies the input

        // Focus elsewhere (a nav button = not a text input) and F11 works again.
        window.NavButtons["bookshelf"].Focus();
        Dispatcher.UIThread.RunJobs();
        Assert.False(window.IsTextInputFocused());
        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();
        Assert.NotNull(window.LastImmersiveWindow);
        window.LastImmersiveWindow!.Close();
        Dispatcher.UIThread.RunJobs();
        window.Close();
    }

    [AvaloniaFact]
    public async Task F11_WithModifier_IsNotTreatedAsTheHotkey()
    {
        var window = NewWindow();
        Assert.False(window.TryHandleGlobalKey(Key.F11, KeyModifiers.Control));
        Assert.False(window.TryHandleGlobalKey(Key.F11, KeyModifiers.Alt));
        Assert.False(window.TryHandleGlobalKey(Key.F11, KeyModifiers.Shift));
        Assert.False(window.TryHandleGlobalKey(Key.F11, KeyModifiers.Control | KeyModifiers.Shift));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();
        Assert.Null(window.LastImmersiveWindow);
        Assert.Equal("bookshelf", window.CurrentPage);
        window.Close();
    }

    [AvaloniaFact]
    public async Task F11_DoesNotSwallowOtherKeys()
    {
        var window = NewWindow();
        Assert.False(window.TryHandleGlobalKey(Key.H));
        Assert.False(window.TryHandleGlobalKey(Key.F));
        Assert.False(window.TryHandleGlobalKey(Key.Escape));
        Assert.False(window.TryHandleGlobalKey(Key.Left));
        await window.LastImmersiveToggle;
        Assert.Null(window.LastImmersiveWindow);
        window.Close();
    }

    [AvaloniaFact]
    public async Task F11_InImmersiveWindow_ClosesAndKeepsH_F_ArrowBehaviour()
    {
        var window = NewWindow();
        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();
        var immersive = window.LastImmersiveWindow!;
        Assert.Equal(0, immersive.F11Count);

        var hudBefore = immersive.Page.ViewModel.HudVisible;
        Assert.True(immersive.TryHandleKey(Key.H));
        Assert.NotEqual(hudBefore, immersive.Page.ViewModel.HudVisible);
        var fitBefore = immersive.Page.ViewModel.FitMode;
        Assert.True(immersive.TryHandleKey(Key.F));
        Assert.NotEqual(fitBefore, immersive.Page.ViewModel.FitMode);
        var pageBefore = immersive.Page.ViewModel.CurrentPageIndex;
        Assert.True(immersive.TryHandleKey(Key.Right));
        Assert.NotEqual(pageBefore, immersive.Page.ViewModel.CurrentPageIndex);

        Assert.True(immersive.TryHandleKey(Key.F11));
        Assert.Equal(1, immersive.F11Count);
        Dispatcher.UIThread.RunJobs();
        Assert.False(immersive.IsVisible);
        window.Close();
    }

    [AvaloniaFact]
    public async Task F11_WithoutLibraryBook_StillOpensFixtureImmersive_AndRestoresPage()
    {
        var window = NewWindow(withBook: false);
        Assert.True(window.TryHandleGlobalKey(Key.F11));
        await window.LastImmersiveToggle;
        Dispatcher.UIThread.RunJobs();

        var immersive = window.LastImmersiveWindow;
        Assert.NotNull(immersive);
        Assert.Null(immersive!.Page.LibraryBook); // fixture fallback
        Assert.Equal("bookshelf", window.ImmersiveRestorePage);

        immersive.Close();
        Dispatcher.UIThread.RunJobs();
        Assert.Null(window.LastImmersiveWindow);
        Assert.Equal("bookshelf", window.CurrentPage);
        window.Close();
    }
}
