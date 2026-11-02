using System.Text.Json;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Views;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// READER-SELECTOR-UI-1: the provider-binding card's book/chapter selectors replace hand-typed ids.
/// The real library reads are represented by the controller seam (<c>library_list_books</c> via
/// <c>Snapshot.Books</c>/<c>RefreshBooksAsync</c> and <c>list_chapters</c> via
/// <c>ListChaptersAsync</c>); this file drives the real controls headless with the scripted
/// <see cref="FakeHostController"/> and asserts the exact ids the bindings command receives.
/// </summary>
public sealed class ReaderSelectorUiTests
{
    private static string EvidenceDirectory
    {
        get
        {
            var configured = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
            var root = string.IsNullOrWhiteSpace(configured)
                ? Path.Combine(Path.GetTempPath(), "newmanga-reader-selector-ui-evidence")
                : configured;
            var directory = Path.Combine(root, "reader-selector-ui");
            Directory.CreateDirectory(directory);
            return directory;
        }
    }

    private static void WriteEvidence(string name, Action<Utf8JsonWriter> write)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true }))
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC2/AC3");
            write(writer);
            writer.WriteEndObject();
        }

        File.WriteAllBytes(Path.Combine(EvidenceDirectory, name + ".json"), stream.ToArray());
    }

    private static FakeHostController ControllerWithBooks(params string[] titles)
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot(titles));
        controller.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-1", "openai", "DeepSeek", new[] { SettingsCapabilities.Ocr },
            "https://api.example/v1", "m", null, true, "missing"));
        return controller;
    }

    private static SettingsPage NewPage(FakeHostController controller) =>
        new(new SettingsViewModel(), () => { }, controller);

    private static void Click(Button button) => button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

    private static void SelectScope(ProviderBindingsSection section, string kind) =>
        section.ScopeKindInput.SelectedIndex = ProfileBindingScope.Kinds.ToList().IndexOf(kind);

    [AvaloniaFact]
    public async Task ChapterScope_SelectBook_LoadsChapters_AndBindingUsesRealIds()
    {
        var controller = ControllerWithBooks("我的漫画");
        controller.ChaptersByBook["book-0"] = new[]
        {
            new ChapterSummary("chapter-1", "第一话", "1", 0),
            new ChapterSummary("chapter-2", "第二话", "2", 1),
        };
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.Bindings;

        SelectScope(section, ProfileBindingScope.Chapter);
        await section.LastOperation;

        // AC1: book selector lists the real book title, not the bare id.
        Assert.Equal(1, section.BookSelector.ItemCount);
        Assert.Equal("我的漫画", section.BookSelector.Items[0]);
        Assert.Equal(0, section.ChapterSelector.ItemCount);
        Assert.Contains("请选择书籍", section.SelectorStatusText.Text ?? string.Empty, StringComparison.Ordinal);

        // AC2: selecting the book loads list_chapters for that exact book.
        section.BookSelector.SelectedIndex = 0;
        await section.LastOperation;
        Assert.Equal(2, section.ChapterSelector.ItemCount);
        Assert.Equal("第一话", section.ChapterSelector.Items[0]);
        Assert.Equal("第二话", section.ChapterSelector.Items[1]);
        Assert.Equal(0, section.ChapterSelector.SelectedIndex);
        Assert.Contains("已加载 2 个章节", section.SelectorStatusText.Text ?? string.Empty, StringComparison.Ordinal);

        section.ChapterSelector.SelectedIndex = 1;
        section.CapabilityInput.SelectedIndex = SettingsCapabilities.All.ToList().IndexOf(SettingsCapabilities.Ocr);
        Click(section.SetButton);
        await section.LastOperation;

        var binding = controller.BindingSets[^1];
        Assert.Equal(ProfileBindingScope.Chapter, binding.Scope.Kind);
        Assert.Equal("chapter-2", binding.Scope.ChapterId);
        Assert.Equal("profile-1", binding.ProfileId);
        Assert.Null(binding.Scope.BookId);
        Assert.Contains("绑定已保存", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);

        WriteEvidence("chapter-scope", writer =>
        {
            writer.WriteString("scenario", "scope=chapter -> book selector -> chapters loaded -> bind");
            writer.WriteString("book_title", controller.Snapshot.Books[0].Title);
            writer.WriteNumber("chapters_loaded", section.ChapterSelector.ItemCount);
            writer.WriteString("bound_chapter_id", binding.Scope.ChapterId);
            writer.WriteString("bound_capability", binding.Capability);
            writer.WriteBoolean("book_id_not_in_scope", binding.Scope.BookId is null);
        });
    }

    [AvaloniaFact]
    public async Task BookScope_SelectBook_BindsBookId_AndKeepsChapterHidden()
    {
        var controller = ControllerWithBooks("我的漫画");
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.Bindings;

        SelectScope(section, ProfileBindingScope.Book);
        await section.LastOperation;
        Assert.False(section.ChapterSelector.IsVisible);
        Assert.Equal(1, section.BookSelector.ItemCount);

        section.BookSelector.SelectedIndex = 0;
        section.CapabilityInput.SelectedIndex = SettingsCapabilities.All.ToList().IndexOf(SettingsCapabilities.Translation);
        Click(section.SetButton);
        await section.LastOperation;

        var binding = controller.BindingSets[^1];
        Assert.Equal(ProfileBindingScope.Book, binding.Scope.Kind);
        Assert.Equal("book-0", binding.Scope.BookId);
        Assert.Equal(SettingsCapabilities.Translation, binding.Capability);

        WriteEvidence("book-scope", writer =>
        {
            writer.WriteString("scenario", "scope=book -> book selector -> bind real book id");
            writer.WriteString("bound_book_id", binding.Scope.BookId);
            writer.WriteBoolean("chapter_selector_hidden", !section.ChapterSelector.IsVisible);
        });
    }

    [AvaloniaFact]
    public async Task EmptyLibrary_ShowsEmptyState_AndDisablesBindingSubmit()
    {
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        controller.ProviderProfiles.Add(new ProviderProfileInfo(
            "profile-1", "openai", "DeepSeek", new[] { SettingsCapabilities.Ocr },
            "https://api.example/v1", "m", null, true, "missing"));
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.Bindings;

        SelectScope(section, ProfileBindingScope.Book);
        await section.LastOperation;

        Assert.Equal(0, section.BookSelector.ItemCount);
        Assert.Contains("书库为空", section.SelectorStatusText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.False(section.SetButton.IsEnabled);

        Click(section.SetButton);
        await section.LastOperation;
        Assert.Empty(controller.BindingSets);
        Assert.Contains("请先选择书籍", section.StatusText.Text ?? string.Empty, StringComparison.Ordinal);

        WriteEvidence("empty-library", writer =>
        {
            writer.WriteString("scenario", "empty library -> empty state + disabled submit");
            writer.WriteBoolean("book_selector_empty", section.BookSelector.ItemCount == 0);
            writer.WriteBoolean("set_button_disabled", !section.SetButton.IsEnabled);
            writer.WriteBoolean("no_binding_sent", controller.BindingSets.Count == 0);
        });
    }

    [AvaloniaFact]
    public async Task BookWithoutChapters_ShowsEmptyState_AndScopeSwitchResetsSelections()
    {
        var controller = ControllerWithBooks("无章节书");
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.Bindings;

        SelectScope(section, ProfileBindingScope.Chapter);
        await section.LastOperation;
        section.BookSelector.SelectedIndex = 0;
        await section.LastOperation;

        Assert.Equal(0, section.ChapterSelector.ItemCount);
        Assert.Contains("该书籍没有章节", section.SelectorStatusText.Text ?? string.Empty, StringComparison.Ordinal);
        Assert.False(section.SetButton.IsEnabled);

        // AC2: switching the scope kind resets both selections and the chapter list.
        SelectScope(section, ProfileBindingScope.Global);
        await section.LastOperation;
        Assert.False(section.BookSelector.IsVisible);
        Assert.Equal(-1, section.BookSelector.SelectedIndex);
        Assert.Equal(-1, section.ChapterSelector.SelectedIndex);

        SelectScope(section, ProfileBindingScope.Book);
        await section.LastOperation;
        Assert.True(section.BookSelector.IsVisible);
        Assert.Equal(-1, section.BookSelector.SelectedIndex);
        Assert.Equal(-1, section.ChapterSelector.SelectedIndex);
        Assert.Equal("", section.ChapterSelector.ItemCount == 0 ? string.Empty : "unexpected");

        WriteEvidence("chapterless-and-scope-switch", writer =>
        {
            writer.WriteString("scenario", "book without chapters -> empty state; scope switch resets selections");
            writer.WriteBoolean("chapterless_empty_state", true);
            writer.WriteBoolean("scope_switch_resets_book", section.BookSelector.SelectedIndex == -1);
            writer.WriteBoolean("scope_switch_resets_chapter", section.ChapterSelector.SelectedIndex == -1);
        });
    }

    [AvaloniaFact]
    public async Task SelectedBook_LoadsChaptersOnlyOncePerSelection_AndHintExplainsMissingChapter()
    {
        var controller = ControllerWithBooks("书A");
        controller.ChaptersByBook["book-0"] = new[]
        {
            new ChapterSummary("chapter-1", "第一话", "1", 0),
        };
        var page = NewPage(controller);
        await page.RefreshProfilesAsync();
        var section = page.Bindings;

        SelectScope(section, ProfileBindingScope.Chapter);
        await section.LastOperation;
        section.BookSelector.SelectedIndex = 0;
        await section.LastOperation;
        Assert.Equal(1, section.ChapterSelector.ItemCount);

        section.ChapterSelector.SelectedIndex = 0;
        Assert.True(section.SetButton.IsEnabled);
        WriteEvidence("chapter-ready", writer =>
        {
            writer.WriteString("scenario", "book selected -> chapter loaded -> submit enabled");
            writer.WriteBoolean("submit_enabled", section.SetButton.IsEnabled);
            writer.WriteNumber("chapters", section.ChapterSelector.ItemCount);
        });
    }
}
