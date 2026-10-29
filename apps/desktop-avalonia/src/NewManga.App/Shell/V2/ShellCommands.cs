using Avalonia.Input;

namespace NewManga.App.Shell.V2;

/// <summary>Stable command ids shared by the KeyMap, the command palette and the shell dispatcher.</summary>
public static class ShellCommandIds
{
    public const string SpaceLibrary = "space.library";
    public const string SpaceStudio = "space.studio";
    public const string SpaceConsole = "space.console";
    public const string StudioModeToggle = "studio.mode.toggle";
    public const string CommandPalette = "command.palette";
    public const string QuickJump = "go.to";
    public const string Export = "export.run";
    public const string ThemeStudio = "settings.theme";
    public const string Help = "help.shortcuts";
    public const string AttentionNext = "attention.next";
    public const string SurfaceBack = "surface.back";
    public const string ThemeToggle = "theme.toggle";

    public const string ObjectNext = "object.next";
    public const string ObjectPrevious = "object.previous";
    public const string PageNext = "page.next";
    public const string PagePrevious = "page.previous";
    public const string ChapterNext = "chapter.next";
    public const string ChapterPrevious = "chapter.previous";

    public const string LibraryRefresh = "library.refresh";
    public const string LibraryImportFiles = "library.import.files";
    public const string LibraryImportFolder = "library.import.folder";
    public const string LibraryRecycle = "library.recycle";
    public const string LibraryNewBook = "library.new.book";
    public const string LibraryNewChapter = "library.new.chapter";
    public const string LibraryOpenReader = "library.reader.open";
    public const string LibraryClearSelection = "library.selection.clear";

    public const string StudioPage = "studio.page";
    public const string StudioBatch = "studio.batch";
}

/// <summary>
/// V11R-B-1: the complete command registry of the new shell. Contract §6.3 shortcuts are declared
/// here once; the command palette (Ctrl+K) is generated from the same list so the two can never
/// drift apart. Commands whose backing service is not merged yet are marked unavailable with a
/// reason — they are never silently faked (AC1).
/// </summary>
public static class ShellCommands
{
    private const string NotWiredCreateChapter =
        "能力待接入：CreateChapterAsync 由 core-bridge（V11R-A-1）提供，尚未合入";

    private const string NotWiredRunData =
        "能力待接入：Run 投影由 core-bridge（V11R-A-2/IRunController）提供，尚未合入";

    private const string NotWiredExport =
        "能力待接入：V2 导出预检归 V11R-B-5，旧版导出流程未迁移";

    public static IReadOnlyList<ShellCommandDefinition> Definitions { get; } = new[]
    {
        // ── Global navigation (contract §6.3) ────────────────────────────────────────────────
        Define(ShellCommandIds.SpaceLibrary, "资料柜", "全局 · — · 空间", null, null, G(Key.D1, KeyModifiers.Control)),
        Define(ShellCommandIds.SpaceStudio, "工位", "全局 · — · 空间", null, null, G(Key.D2, KeyModifiers.Control)),
        Define(ShellCommandIds.SpaceConsole, "控制台", "全局 · — · 空间", null, null, G(Key.D3, KeyModifiers.Control)),
        Define(ShellCommandIds.StudioModeToggle, "切换工位模式（页面 / 批次）", "工位 · — · 模式", SpaceId.Studio, null, G(Key.Tab)),
        Define(ShellCommandIds.CommandPalette, "命令面板", "全局 · — · 命令", null, null, G(Key.K, KeyModifiers.Control)),
        Define(ShellCommandIds.QuickJump, "快速跳转（作品 / 章节 / 页）", "全局 · — · 跳转", null, null, G(Key.P, KeyModifiers.Control)),
        Define(ShellCommandIds.Export, "导出", "全局 · — · 导出", null, null, G(Key.E, KeyModifiers.Control), false, NotWiredExport),
        Define(ShellCommandIds.ThemeStudio, "主题工作室", "全局 · — · 外观", null, null, G(Key.OemComma, KeyModifiers.Control)),
        Define(ShellCommandIds.Help, "键位速查", "全局 · — · 帮助", null, null, G(Key.F1)),
        DefineMany(
            ShellCommandIds.AttentionNext,
            "下一个需要我处理",
            "全局 · — · 异常导航",
            null,
            null,
            new[] { G(Key.F5), G(Key.F, KeyModifiers.Control | KeyModifiers.Shift) },
            false,
            NotWiredRunData),
        Define(ShellCommandIds.SurfaceBack, "返回 / 关闭浮层", "全局 · — · 导航", null, null, G(Key.Escape)),

        // ── Library object navigation (contract §6.3) ───────────────────────────────────────
        Define(ShellCommandIds.ObjectNext, "下一个对象", "资料柜 · — · 对象", SpaceId.Library, null, G(Key.J)),
        Define(ShellCommandIds.ObjectPrevious, "上一个对象", "资料柜 · — · 对象", SpaceId.Library, null, G(Key.K)),
        Define(ShellCommandIds.PageNext, "下一页", "资料柜 · — · 页", SpaceId.Library, null, G(Key.OemCloseBrackets)),
        Define(ShellCommandIds.PagePrevious, "上一页", "资料柜 · — · 页", SpaceId.Library, null, G(Key.OemOpenBrackets)),
        Define(
            ShellCommandIds.ChapterNext,
            "下一章",
            "资料柜 · — · 章节",
            SpaceId.Library,
            null,
            G(Key.OemCloseBrackets, KeyModifiers.Shift)),
        Define(
            ShellCommandIds.ChapterPrevious,
            "上一章",
            "资料柜 · — · 章节",
            SpaceId.Library,
            null,
            G(Key.OemOpenBrackets, KeyModifiers.Shift)),

        // ── Library actions (palette only; no frozen shortcut assigned) ─────────────────────
        Define(ShellCommandIds.LibraryRefresh, "刷新书架", "资料柜 · — · 数据", SpaceId.Library, null, null),
        Define(ShellCommandIds.LibraryImportFiles, "导入文件到章节", "资料柜 · — · 导入", SpaceId.Library, null, null),
        Define(ShellCommandIds.LibraryImportFolder, "导入文件夹到章节", "资料柜 · — · 导入", SpaceId.Library, null, null),
        Define(ShellCommandIds.LibraryRecycle, "回收站", "资料柜 · — · 回收站", SpaceId.Library, null, null),
        Define(ShellCommandIds.LibraryNewBook, "新建作品", "资料柜 · — · 作品", SpaceId.Library, null, null),
        Define(
            ShellCommandIds.LibraryNewChapter,
            "新建章节",
            "资料柜 · — · 章节",
            SpaceId.Library,
            null,
            null,
            false,
            NotWiredCreateChapter),
        Define(ShellCommandIds.LibraryOpenReader, "阅读选中章节", "资料柜 · — · 阅读", SpaceId.Library, null, null),
        Define(ShellCommandIds.LibraryClearSelection, "清除多选", "资料柜 · — · 选择", SpaceId.Library, null, null),

        // ── Studio mode switch actions (content itself belongs to ui-studio B-3/B-4) ─────────
        Define(ShellCommandIds.StudioPage, "工位 · 页面模式", "工位 · 页面 · 模式", SpaceId.Studio, StudioMode.Page, null),
        Define(ShellCommandIds.StudioBatch, "工位 · 批次模式", "工位 · 批次 · 模式", SpaceId.Studio, StudioMode.Batch, null),

        // ── Appearance ──────────────────────────────────────────────────────────────────────
        Define(ShellCommandIds.ThemeToggle, "切换深浅外观", "全局 · — · 外观", null, null, null),
    };

    public static ShellCommandDefinition? Find(string id) =>
        Definitions.FirstOrDefault(definition => string.Equals(definition.Id, id, StringComparison.Ordinal));

    private static ShellCommandDefinition Define(
        string id,
        string title,
        string scopeLabel,
        SpaceId? space,
        StudioMode? mode,
        ShellKeyGesture? gesture,
        bool isAvailable = true,
        string? unavailableReason = null) =>
        new(
            id,
            title,
            scopeLabel,
            space,
            mode,
            gesture is null ? Array.Empty<ShellKeyGesture>() : new[] { gesture },
            isAvailable,
            unavailableReason);

    private static ShellCommandDefinition DefineMany(
        string id,
        string title,
        string scopeLabel,
        SpaceId? space,
        StudioMode? mode,
        IReadOnlyList<ShellKeyGesture> gestures,
        bool isAvailable,
        string? unavailableReason) =>
        new(id, title, scopeLabel, space, mode, gestures, isAvailable, unavailableReason);

    private static ShellKeyGesture G(Key key, KeyModifiers modifiers = KeyModifiers.None) => new(key, modifiers);
}
