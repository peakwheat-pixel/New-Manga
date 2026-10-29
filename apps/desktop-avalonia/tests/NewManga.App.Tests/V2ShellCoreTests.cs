using Avalonia.Input;
using NewManga.App.Shell.V2;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-B-1 AC2/AC5: the shell state is the single source of truth; space/mode switches keep the
/// selection and the per-space scroll/filter context, and the overlay stack unwinds one level at a
/// time. Pure logic — no window required.
/// </summary>
public sealed class V2ShellStateTests
{
    [Fact]
    public void OverlayStack_ClosesOneLevelPerEsc_AndNeverPopsTheSpacesRoot()
    {
        var state = new ShellState();
        Assert.Equal(ShellSurface.Spaces, state.CurrentSurface);
        Assert.False(state.HasOverlay);

        Assert.True(state.PushSurface(ShellSurface.ThemeStudio));
        Assert.True(state.PushSurface(ShellSurface.ReaderOverlay));
        Assert.Equal(ShellSurface.ReaderOverlay, state.CurrentSurface);
        Assert.True(state.IsReaderOpen);

        Assert.True(state.CloseTopSurface());
        Assert.Equal(ShellSurface.ThemeStudio, state.CurrentSurface);
        Assert.True(state.CloseTopSurface());
        Assert.Equal(ShellSurface.Spaces, state.CurrentSurface);
        Assert.False(state.CloseTopSurface());
        Assert.Equal(ShellSurface.Spaces, state.CurrentSurface);
    }

    [Fact]
    public void SpaceAndModeSwitch_KeepSelectionFiltersAndScroll()
    {
        var state = new ShellState();
        state.SelectBook("b1");
        state.SelectChapter("c1");
        state.SetSearch(SpaceId.Library, null, "夜光");
        state.SetSort(SpaceId.Library, null, "updated");
        state.SetFilter(SpaceId.Library, null, "favorite");
        state.SetScroll(SpaceId.Library, null, 0, 240);

        state.SwitchSpace(SpaceId.Studio);
        state.ToggleStudioMode();
        state.SwitchSpace(SpaceId.Console);
        state.SwitchSpace(SpaceId.Library);

        Assert.Equal(SpaceId.Library, state.CurrentSpace);
        Assert.Equal("b1", state.Selection.BookId);
        Assert.Equal("c1", state.Selection.ChapterId);
        Assert.Equal("夜光", state.LibraryView.SearchText);
        Assert.Equal("updated", state.LibraryView.SortKey);
        Assert.Equal("favorite", state.LibraryView.FilterKey);
        Assert.Equal(240, state.LibraryView.ScrollOffsetY);
        Assert.Equal(StudioMode.Batch, state.StudioMode);
    }

    [Fact]
    public void SelectingBook_ClearsChapterAndPages_AndMultiPageIsSharedAcrossModes()
    {
        var state = new ShellState();
        state.SelectBook("b1");
        state.SelectChapter("c1");
        state.SelectPage("p1");
        Assert.True(state.Selection.HasPage);

        state.SelectBook("b2");
        Assert.Equal("b2", state.Selection.BookId);
        Assert.Null(state.Selection.ChapterId);
        Assert.Null(state.Selection.PageId);

        state.SelectChapter("c9");
        state.SetMultiPage(new[] { "p1", "p2", "p3" });
        Assert.Equal(3, state.Selection.MultiPageCount);

        state.SwitchSpace(SpaceId.Studio);
        state.ToggleStudioMode();
        Assert.Equal(3, state.Selection.MultiPageCount);

        state.ToggleMultiPage("p2");
        Assert.Equal(2, state.Selection.MultiPageCount);
        Assert.DoesNotContain("p2", state.Selection.MultiPage);
        state.ClearMultiPage();
        Assert.Equal(0, state.Selection.MultiPageCount);
    }

    [Fact]
    public void StudioPageAndBatch_KeepIndependentScrollContext()
    {
        var state = new ShellState();
        state.SetScroll(SpaceId.Studio, StudioMode.Page, 0, 120);
        state.SetStudioMode(StudioMode.Batch);
        state.SetScroll(SpaceId.Studio, StudioMode.Batch, 0, 900);
        state.SetStudioMode(StudioMode.Page);
        Assert.Equal(120, state.StudioPageView.ScrollOffsetY);
        state.SetStudioMode(StudioMode.Batch);
        Assert.Equal(900, state.StudioBatchView.ScrollOffsetY);
    }

    [Fact]
    public void StateRaisesPropertyChanged_ForBoundShellProperties()
    {
        var state = new ShellState();
        var changed = new List<string?>();
        state.PropertyChanged += (_, args) => changed.Add(args.PropertyName);

        state.SwitchSpace(SpaceId.Console);
        state.ToggleStudioMode();
        state.PushSurface(ShellSurface.ReaderOverlay);
        state.SelectBook("b1");

        Assert.Contains(nameof(ShellState.CurrentSpace), changed);
        Assert.Contains(nameof(ShellState.StudioMode), changed);
        Assert.Contains(nameof(ShellState.HasOverlay), changed);
        Assert.Contains(nameof(ShellState.Selection), changed);
    }

    [Fact]
    public void SelectionPath_DescribesExactObjectAddressing()
    {
        var state = new ShellState();
        state.SelectBook("b1");
        state.SelectChapter("c1");
        state.SelectPage("p1");
        Assert.Equal(new[] { "b1", "c1", "p1" }, state.SelectionPath());
        state.SelectRegion("r1");
        Assert.EndsWith("r1", state.SelectionPath()[^1], StringComparison.Ordinal);
        state.ClearSelection();
        Assert.Empty(state.SelectionPath());
    }
}

/// <summary>V11R-B-1 AC5: the single key registry is complete and conflict-free; conflicts fail hard.</summary>
public sealed class V2KeyMapTests
{
    private static void AssertBinding(KeyMap map, Key key, KeyModifiers modifiers, SpaceId space, StudioMode mode, string expectedId)
    {
        Assert.True(map.TryMatch(key, modifiers, space, mode, out var command), $"{ShortcutText.Format(key, modifiers)} 未注册");
        Assert.Equal(expectedId, command.Id);
    }

    [Fact]
    public void DefaultRegistry_HasNoConflicts_AndMatchesContractShortcuts()
    {
        var map = KeyMap.Default;
        Assert.Empty(map.Conflicts);
        Assert.True(map.IsValid);
        KeyMap.EnsureValid();

        var library = SpaceId.Library;
        var studio = SpaceId.Studio;
        var console = SpaceId.Console;

        AssertBinding(map, Key.D1, KeyModifiers.Control, library, StudioMode.Page, ShellCommandIds.SpaceLibrary);
        AssertBinding(map, Key.D2, KeyModifiers.Control, library, StudioMode.Page, ShellCommandIds.SpaceStudio);
        AssertBinding(map, Key.D3, KeyModifiers.Control, console, StudioMode.Page, ShellCommandIds.SpaceConsole);
        AssertBinding(map, Key.Tab, KeyModifiers.None, studio, StudioMode.Page, ShellCommandIds.StudioModeToggle);
        AssertBinding(map, Key.K, KeyModifiers.Control, studio, StudioMode.Batch, ShellCommandIds.CommandPalette);
        AssertBinding(map, Key.P, KeyModifiers.Control, library, StudioMode.Page, ShellCommandIds.QuickJump);
        AssertBinding(map, Key.E, KeyModifiers.Control, library, StudioMode.Page, ShellCommandIds.Export);
        AssertBinding(map, Key.OemComma, KeyModifiers.Control, console, StudioMode.Page, ShellCommandIds.ThemeStudio);
        AssertBinding(map, Key.F1, KeyModifiers.None, library, StudioMode.Page, ShellCommandIds.Help);
        AssertBinding(map, Key.F5, KeyModifiers.None, library, StudioMode.Page, ShellCommandIds.AttentionNext);
        AssertBinding(map, Key.F, KeyModifiers.Control | KeyModifiers.Shift, library, StudioMode.Page, ShellCommandIds.AttentionNext);
        AssertBinding(map, Key.Escape, KeyModifiers.None, studio, StudioMode.Batch, ShellCommandIds.SurfaceBack);
        AssertBinding(map, Key.J, KeyModifiers.None, library, StudioMode.Page, ShellCommandIds.ObjectNext);
        AssertBinding(map, Key.K, KeyModifiers.None, library, StudioMode.Page, ShellCommandIds.ObjectPrevious);
        AssertBinding(map, Key.OemOpenBrackets, KeyModifiers.None, library, StudioMode.Page, ShellCommandIds.PagePrevious);
        AssertBinding(map, Key.OemCloseBrackets, KeyModifiers.None, library, StudioMode.Page, ShellCommandIds.PageNext);
        AssertBinding(map, Key.OemOpenBrackets, KeyModifiers.Shift, library, StudioMode.Page, ShellCommandIds.ChapterPrevious);
        AssertBinding(map, Key.OemCloseBrackets, KeyModifiers.Shift, library, StudioMode.Page, ShellCommandIds.ChapterNext);
    }

    [Fact]
    public void Tab_OnlyTogglesModeInsideStudio_JAndK_OnlyApplyToLibrary()
    {
        var map = KeyMap.Default;
        Assert.False(map.TryMatch(Key.Tab, KeyModifiers.None, SpaceId.Library, StudioMode.Page, out _));
        Assert.False(map.TryMatch(Key.J, KeyModifiers.None, SpaceId.Console, StudioMode.Page, out _));
        Assert.False(map.TryMatch(Key.OemCloseBrackets, KeyModifiers.None, SpaceId.Studio, StudioMode.Page, out _));
    }

    [Fact]
    public void ConflictDetection_FlagsSameGestureOverlappingScopes_ButAllowsDisjointScopes()
    {
        var libraryA = new ShellCommandDefinition(
            "a",
            "A",
            "资料柜 · — · 测试",
            SpaceId.Library,
            null,
            new[] { new ShellKeyGesture(Key.Q, KeyModifiers.None) });
        var libraryB = new ShellCommandDefinition(
            "b",
            "B",
            "资料柜 · — · 测试",
            SpaceId.Library,
            null,
            new[] { new ShellKeyGesture(Key.Q, KeyModifiers.None) });
        var consoleC = new ShellCommandDefinition(
            "c",
            "C",
            "控制台 · — · 测试",
            SpaceId.Console,
            null,
            new[] { new ShellKeyGesture(Key.Q, KeyModifiers.None) });

        Assert.Single(KeyMap.FindConflicts(new[] { libraryA, libraryB }));
        Assert.Empty(KeyMap.FindConflicts(new[] { libraryA, consoleC }));

        var conflicting = new KeyMap(new[] { libraryA, libraryB });
        Assert.False(conflicting.IsValid);
        Assert.Throws<InvalidOperationException>(() => KeyMap.EnsureValid(conflicting));

        // The production registry stays valid even after the custom-map checks.
        Assert.True(KeyMap.Default.IsValid);
    }

    [Fact]
    public void UnavailableCommands_CarryAnExplicitReason_NeverFakeSuccess()
    {
        var createChapter = ShellCommands.Find(ShellCommandIds.LibraryNewChapter);
        Assert.NotNull(createChapter);
        Assert.False(createChapter!.IsAvailable);
        Assert.Contains("能力待接入", createChapter.UnavailableReason!, StringComparison.Ordinal);

        var export = ShellCommands.Find(ShellCommandIds.Export);
        Assert.NotNull(export);
        Assert.False(export!.IsAvailable);

        var attention = ShellCommands.Find(ShellCommandIds.AttentionNext);
        Assert.NotNull(attention);
        Assert.False(attention!.IsAvailable);
        Assert.Equal(2, attention.Gestures.Count);

        // Every registered command carries the palette annotation 「空间 · 模式 · 作用域」.
        Assert.All(ShellCommands.Definitions, definition =>
            Assert.Contains(" · ", definition.ScopeLabel, StringComparison.Ordinal));
    }

    [Fact]
    public void PaletteCatalog_ContainsEveryBoundCommand_ForItsOwnScope()
    {
        var map = KeyMap.Default;
        foreach (var definition in ShellCommands.Definitions.Where(item => item.HasGesture))
        {
            var space = definition.Space ?? SpaceId.Library;
            var mode = definition.Mode ?? StudioMode.Page;
            Assert.Contains(
                map.ForScope(space, mode),
                candidate => string.Equals(candidate.Id, definition.Id, StringComparison.Ordinal));
        }
    }
}

/// <summary>V11R-B-1: deep-link addressing for evidence runs and V11R-INT-1 wiring.</summary>
public sealed class V2DeepLinkTests
{
    [Fact]
    public void ParsesFullQuery_IntoExactObjectAddress()
    {
        Assert.True(ShellDeepLink.TryParse(
            "?space=studio&mode=batch&book=b1&chapter=c2&page=7&region=r3",
            out var link));
        Assert.Equal(SpaceId.Studio, link.Space);
        Assert.Equal(StudioMode.Batch, link.Mode);
        Assert.Equal("b1", link.BookId);
        Assert.Equal("c2", link.ChapterId);
        Assert.Equal(7, link.Page);
        Assert.Equal("r3", link.RegionId);
    }

    [Fact]
    public void RejectsUnknownSpaceOrMalformedInput()
    {
        Assert.False(ShellDeepLink.TryParse("?space=moon", out _));
        Assert.False(ShellDeepLink.TryParse("?page=abc", out _));
        Assert.False(ShellDeepLink.TryParse("", out _));
        Assert.False(ShellDeepLink.TryParse(null, out _));
        Assert.False(ShellDeepLink.TryParse("?mode=sideways", out _));
    }

    [Fact]
    public void ToQuery_RoundTripsTheAddress()
    {
        var original = new ShellDeepLink
        {
            Space = SpaceId.Console,
            Mode = StudioMode.Batch,
            BookId = "b1",
            Page = 12,
        };
        Assert.True(ShellDeepLink.TryParse(original.ToQuery(), out var parsed));
        Assert.Equal(SpaceId.Console, parsed.Space);
        Assert.Equal(StudioMode.Batch, parsed.Mode);
        Assert.Equal("b1", parsed.BookId);
        Assert.Equal(12, parsed.Page);
    }

    [Fact]
    public void PageZero_IsClampedToOne()
    {
        Assert.True(ShellDeepLink.TryParse("?page=0", out var link));
        Assert.Equal(1, link.Page);
    }
}

/// <summary>V11R-B-1: Chinese + pinyin-initial search used by the Library search field.</summary>
public sealed class V2PinyinTests
{
    [Fact]
    public void ChineseSubstring_Matches()
    {
        Assert.True(PinyinIndex.Matches("夜光列车", "夜光"));
        Assert.True(PinyinIndex.Matches("汉江之夜", "江之"));
        Assert.False(PinyinIndex.Matches("汉江之夜", "雾港"));
    }

    [Fact]
    public void PinyinInitials_MatchCommonTitles()
    {
        Assert.True(PinyinIndex.Matches("夜光列车", "yglc"));
        Assert.True(PinyinIndex.Matches("汉江之夜", "hjzy"));
        Assert.True(PinyinIndex.Matches("旧校舍的夏天", "jx"));
        Assert.True(PinyinIndex.Matches("雾港来信", "wglx"));
        Assert.False(PinyinIndex.Matches("雾港来信", "zzz"));
    }

    [Fact]
    public void MixedAsciiAndHan_AndEmptyQueries()
    {
        Assert.True(PinyinIndex.Matches("Saber 画集", "saber"));
        Assert.True(PinyinIndex.Matches("Saber 画集", "hj"));
        Assert.True(PinyinIndex.Matches("anything", ""));
        Assert.False(PinyinIndex.Matches(null, "x"));
        Assert.Equal("yglc", PinyinIndex.InitialsOf("夜光列车"));
    }
}
