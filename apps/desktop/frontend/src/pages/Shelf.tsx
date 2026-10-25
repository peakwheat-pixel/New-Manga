import { useCallback, useEffect, useMemo, useState, type CSSProperties, type ReactNode } from "react";
import { CreateTitleDialog } from "../bookshelf/CreateTitleDialog";
import { ImportDialog } from "../bookshelf/ImportDialog";
import { parseSemanticError, type SemanticErrorInfo } from "../bookshelf/error";
import { Icon } from "../components/Icon";
import { PrimaryNav } from "../components/PrimaryNav";
import { StatusMark, type StatusState } from "../components/StatusMark";
import { useAcrylicBudget } from "../design/useAcrylicBudget";
import type { DesignPage, Theme } from "../design/types";
import type { BookSummary, ChapterNavSummary } from "../library/types";
import { RecycleBinPage } from "../recycleBin/RecycleBinPage";
import { CommandPalette } from "../ui/CommandPalette";
import { PageEmpty, PageError, PageLoading } from "../ui/PageState";
import type { CommandSpec, PageRuntime } from "../ui/types";

/* ================================================================== *
 * 视图模型
 *
 * 页面只有一套 DOM：设计预览（`?view=design`，无 `runtime`）与真实运行时
 * （有 `runtime`）各自把数据适配成同一个 `ShelfView`，再由 `ShelfShell` 画一次。
 * 这样"设计稿"和"运行时"不可能长成两套 UI。
 *
 * 诚实性约束：`progress` / `state` / `volume` / 封面图在运行时没有 IPC 来源，
 * 一律为 null 并在渲染时整块省略，而不是画一根假进度条。
 * ================================================================== */

interface ShelfBook {
  id: string;
  title: string;
  subtitle: string;
  coverKicker: string;
  volume: string | null;
  chaptersLabel: string;
  pagesLabel: string;
  updatedLabel: string;
  /** null = 该字段没有 IPC 来源（未知），渲染时省略而不是造假。 */
  progress: number | null;
  state: StatusState | null;
  favorite: boolean;
  archived: boolean;
  coverA: string;
  coverB: string;
}

interface ShelfChapter {
  id: string;
  index: string;
  title: string;
  pagesLabel: string;
  state: StatusState | null;
}

interface ShelfView {
  phase: "loading" | "ready" | "empty" | "error";
  error: SemanticErrorInfo | null;
  books: ShelfBook[];
  chapters: ShelfChapter[];
  chaptersPhase: "idle" | "loading" | "ready" | "error";
  chaptersError: SemanticErrorInfo | null;
  selectedId: string | null;
  activeChapterId: string | null;
  coreLabel: string;
  coreState: StatusState;
  statusText: string;
  statusDetail: string | null;
  statusProgress: number | null;
  statusRight: string;
  canMutate: boolean;
  onRetry(): void;
  onSelectBook(bookId: string): void;
  onSelectChapter(chapterId: string): void;
  onEnter(target: "workbench" | "reader"): void;
}

/* ------------------------------------------------------------------ *
 * 共用工具
 * ------------------------------------------------------------------ */

/**
 * 运行时 IPC 不提供封面图，封面是用 book_id 派生的确定性渐变：它不冒充任何
 * 作品的真实封面，也不会每次渲染跳色。设计预览用 fixtures 里真实的配色。
 */
const COVER_TINTS: ReadonlyArray<readonly [string, string]> = [
  ["#284867", "#101C29"],
  ["#5C3131", "#231012"],
  ["#315643", "#0F1F18"],
  ["#5A4726", "#221A0D"],
  ["#443058", "#181020"],
  ["#274B57", "#0D1B20"],
  ["#533040", "#211018"],
  ["#2E3F61", "#111827"],
];

function hashString(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function generatedCover(seed: string): { coverA: string; coverB: string } {
  const [coverA, coverB] = COVER_TINTS[hashString(seed) % COVER_TINTS.length];
  return { coverA, coverB };
}

function coverStyle(book: { coverA: string; coverB: string }): CSSProperties {
  return { "--cover-a": book.coverA, "--cover-b": book.coverB } as CSSProperties;
}

/** ISO 时间 → 相对标签；无法解析返回「未知」。 */
function formatUpdated(iso: string | null | undefined): string {
  if (!iso) return "未知";
  const time = new Date(iso).getTime();
  if (!Number.isFinite(time)) return "未知";
  const delta = Date.now() - time;
  if (delta < 0) return "刚刚";
  const minutes = Math.floor(delta / 60_000);
  if (minutes < 1) return "刚刚";
  if (minutes < 60) return `${minutes} 分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} 小时前`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} 天前`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months} 个月前`;
  return `${Math.floor(months / 12)} 年前`;
}

/* ------------------------------------------------------------------ *
 * 设计预览数据源（`?view=design`）
 * ------------------------------------------------------------------ */

const PREVIEW_BOOKS: ReadonlyArray<{
  id: string;
  title: string;
  author: string;
  volume: string;
  chapters: number;
  pages: number;
  progress: number;
  updated: string;
  state: StatusState;
  coverA: string;
  coverB: string;
}> = [
  { id: "b-01", title: "雾港来信", author: "南野灯", volume: "VOL.07", chapters: 42, pages: 1280, progress: 68, updated: "12 分钟前", state: "running", coverA: "#284867", coverB: "#101C29" },
  { id: "b-02", title: "白昼残响", author: "绫濑千景", volume: "VOL.03", chapters: 28, pages: 892, progress: 100, updated: "1 小时前", state: "done", coverA: "#5C3131", coverB: "#231012" },
  { id: "b-03", title: "春日构造", author: "远山青", volume: "VOL.02", chapters: 18, pages: 540, progress: 31, updated: "3 小时前", state: "queued", coverA: "#315643", coverB: "#0F1F18" },
  { id: "b-04", title: "铁与麦穗", author: "小坂井", volume: "VOL.11", chapters: 61, pages: 1904, progress: 84, updated: "昨天", state: "stale", coverA: "#5A4726", coverB: "#221A0D" },
  { id: "b-05", title: "夜航西飞", author: "三浦真白", volume: "VOL.05", chapters: 35, pages: 1042, progress: 12, updated: "昨天", state: "blocked", coverA: "#443058", coverB: "#181020" },
  { id: "b-06", title: "深蓝回声", author: "橘朱里", volume: "VOL.09", chapters: 50, pages: 1512, progress: 47, updated: "2 天前", state: "running", coverA: "#274B57", coverB: "#0D1B20" },
  { id: "b-07", title: "无人车站", author: "冬月透", volume: "VOL.01", chapters: 12, pages: 360, progress: 0, updated: "3 天前", state: "notStarted", coverA: "#533040", coverB: "#211018" },
  { id: "b-08", title: "玻璃星图", author: "白鸟悠", volume: "VOL.04", chapters: 33, pages: 980, progress: 73, updated: "4 天前", state: "failed", coverA: "#2E3F61", coverB: "#111827" },
  { id: "b-09", title: "午后三点", author: "森下葵", volume: "VOL.06", chapters: 39, pages: 1128, progress: 55, updated: "5 天前", state: "skipped", coverA: "#4D4A2D", coverB: "#1C1B0F" },
  { id: "b-10", title: "黑箱手记", author: "九条莲", volume: "VOL.08", chapters: 44, pages: 1336, progress: 91, updated: "上周", state: "done", coverA: "#3A3A3E", coverB: "#141416" },
];

const PREVIEW_CHAPTERS: ReadonlyArray<{
  index: string;
  title: string;
  pages: number;
  state: StatusState;
}> = [
  { index: "012", title: "潮汐留下的名字", pages: 24, state: "running" },
  { index: "011", title: "第七盏路灯", pages: 22, state: "done" },
  { index: "010", title: "没有寄出的信", pages: 26, state: "done" },
  { index: "009", title: "雾中的仓库", pages: 20, state: "stale" },
  { index: "008", title: "雨夜访客", pages: 24, state: "done" },
];

function usePreviewView(): ShelfView {
  const [selectedId, setSelectedId] = useState(PREVIEW_BOOKS[0].id);
  const selected = PREVIEW_BOOKS.find((book) => book.id === selectedId) ?? PREVIEW_BOOKS[0];

  return {
    phase: "ready",
    error: null,
    books: PREVIEW_BOOKS.map((book) => ({
      id: book.id,
      title: book.title,
      subtitle: book.author,
      coverKicker: "NEW MANGA",
      volume: book.volume,
      chaptersLabel: `${book.chapters} 话`,
      pagesLabel: `${book.pages} 页`,
      updatedLabel: book.updated,
      progress: book.progress,
      state: book.state,
      favorite: false,
      archived: false,
      coverA: book.coverA,
      coverB: book.coverB,
    })),
    chapters: PREVIEW_CHAPTERS.map((chapter) => ({
      id: chapter.index,
      index: chapter.index,
      title: chapter.title,
      pagesLabel: `${chapter.pages}p`,
      state: chapter.state,
    })),
    chaptersPhase: "ready",
    chaptersError: null,
    selectedId,
    activeChapterId: "012",
    coreLabel: "Core 正常",
    coreState: "done",
    statusText: "流水线运行中",
    statusDetail: `第 012 话 · ${selected.title}`,
    statusProgress: selected.progress,
    statusRight: "设计预览 · 固定数据",
    canMutate: false,
    onRetry: () => undefined,
    onSelectBook: setSelectedId,
    onSelectChapter: () => undefined,
    onEnter: () => undefined,
  };
}

/* ------------------------------------------------------------------ *
 * 真实运行时数据源
 * ------------------------------------------------------------------ */

interface RuntimeShelfState {
  view: ShelfView;
  rawBooks: BookSummary[];
  rawChapters: ChapterNavSummary[];
  onCreateBook(title: string): Promise<void>;
  onImportSuccess(): void;
}

function useRuntimeShelf(runtime: PageRuntime): RuntimeShelfState {
  const { library } = runtime.clients;
  const { chrome } = runtime;

  const [books, setBooks] = useState<BookSummary[]>([]);
  const [phase, setPhase] = useState<"loading" | "ready" | "empty" | "error">("loading");
  const [error, setError] = useState<SemanticErrorInfo | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(chrome.context.bookId);
  const [chapters, setChapters] = useState<ChapterNavSummary[]>([]);
  const [chaptersPhase, setChaptersPhase] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [chaptersError, setChaptersError] = useState<SemanticErrorInfo | null>(null);
  const [pageCounts, setPageCounts] = useState<Record<string, number | null>>({});
  const [coreState, setCoreState] = useState<StatusState>("queued");
  const [coreLabel, setCoreLabel] = useState("正在连接 Core");
  const [reloadToken, setReloadToken] = useState(0);

  const reload = useCallback(() => setReloadToken((value) => value + 1), []);

  useEffect(() => {
    let cancelled = false;
    setPhase("loading");
    setError(null);

    void (async () => {
      try {
        const list = await library.listBooks();
        if (cancelled) return;
        const safeList = Array.isArray(list) ? list : [];
        setBooks(safeList);
        setPhase(safeList.length === 0 ? "empty" : "ready");
        setSelectedId((current) => {
          if (current && safeList.some((book) => book.book_id === current)) return current;
          return safeList.length > 0 ? safeList[0].book_id : null;
        });
      } catch (caught) {
        if (cancelled) return;
        setError(parseSemanticError(caught));
        setPhase("error");
      }
    })();

    void (async () => {
      try {
        const ping = await library.corePing();
        if (cancelled) return;
        setCoreState("done");
        setCoreLabel(`Core ${ping.status || "正常"}`);
      } catch {
        if (cancelled) return;
        setCoreState("failed");
        setCoreLabel("Core 不可用");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [library, reloadToken]);

  useEffect(() => {
    if (chrome.context.bookId) setSelectedId(chrome.context.bookId);
  }, [chrome.context.bookId]);

  useEffect(() => {
    let cancelled = false;
    if (!selectedId) {
      setChapters([]);
      setChaptersPhase("idle");
      setPageCounts({});
      return () => {
        cancelled = true;
      };
    }
    setChaptersPhase("loading");
    setChaptersError(null);

    void (async () => {
      try {
        const list = await library.listChapters(selectedId);
        if (cancelled) return;
        const safeList = Array.isArray(list) ? list : [];
        setChapters(safeList);
        setChaptersPhase(safeList.length === 0 ? "idle" : "ready");

        const counts: Record<string, number | null> = {};
        await Promise.all(
          safeList.map(async (chapter) => {
            try {
              const pages = await library.listChapterPages(chapter.chapter_id);
              counts[chapter.chapter_id] = Array.isArray(pages) ? pages.length : 0;
            } catch {
              counts[chapter.chapter_id] = null;
            }
          }),
        );
        if (cancelled) return;
        setPageCounts(counts);
      } catch (caught) {
        if (cancelled) return;
        setChapters([]);
        setChaptersError(parseSemanticError(caught));
        setChaptersPhase("error");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [library, selectedId]);

  const viewBooks = useMemo<ShelfBook[]>(
    () =>
      books.map((book) => {
        const cover = generatedCover(book.book_id);
        return {
          id: book.book_id,
          title: book.title,
          subtitle: book.original_title || "—",
          coverKicker: book.is_favorite ? "收藏" : "NEW MANGA",
          volume: null,
          chaptersLabel: "章节数见详情",
          pagesLabel: book.page_count === null ? "页数未知" : `${book.page_count} 页`,
          updatedLabel: formatUpdated(book.updated_at),
          progress: null,
          state: null,
          favorite: book.is_favorite,
          archived: book.is_archived,
          coverA: cover.coverA,
          coverB: cover.coverB,
        };
      }),
    [books],
  );

  const viewChapters = useMemo<ShelfChapter[]>(
    () =>
      chapters.map((chapter, index) => {
        const count = pageCounts[chapter.chapter_id];
        return {
          id: chapter.chapter_id,
          index: chapter.chapter_number || String(index + 1).padStart(3, "0"),
          title: chapter.title,
          pagesLabel: count === undefined || count === null ? "页数未知" : `${count}p`,
          state: null,
        };
      }),
    [chapters, pageCounts],
  );

  const selectedBook = books.find((book) => book.book_id === selectedId) ?? null;
  const activeChapterId =
    chrome.context.bookId === selectedId && chrome.context.chapterId
      ? chrome.context.chapterId
      : chapters.length > 0
      ? chapters[0].chapter_id
      : null;

  const onSelectChapter = useCallback(
    (chapterId: string) => {
      if (!selectedId) return;
      chrome.onSelectChapter(selectedId, chapterId);
    },
    [chrome, selectedId],
  );

  const onEnter = useCallback(
    (target: "workbench" | "reader") => {
      if (!selectedId) return;
      chrome.onOpenBook(selectedId, activeChapterId, target);
    },
    [activeChapterId, chrome, selectedId],
  );

  const onCreateBook = useCallback(
    async (title: string) => {
      await library.createBook(title);
      reload();
    },
    [library, reload],
  );

  const view: ShelfView = {
    phase,
    error,
    books: viewBooks,
    chapters: viewChapters,
    chaptersPhase,
    chaptersError,
    selectedId,
    activeChapterId,
    coreLabel,
    coreState,
    statusText: coreState === "done" ? "Core 在线" : "Core 连接异常",
    statusDetail: selectedBook ? selectedBook.title : null,
    statusProgress: null,
    statusRight: `${books.length} 部作品`,
    canMutate: true,
    onRetry: reload,
    onSelectBook: setSelectedId,
    onSelectChapter,
    onEnter,
  };

  return { view, rawBooks: books, rawChapters: chapters, onCreateBook, onImportSuccess: reload };
}

/* ------------------------------------------------------------------ *
 * 呈现层（唯一一套 DOM）
 * ------------------------------------------------------------------ */

type BookFilter = "all" | "favorite" | "archived";
type SortMode = "updated" | "title";

const FILTERS: ReadonlyArray<{ id: BookFilter; label: string }> = [
  { id: "all", label: "全部" },
  { id: "favorite", label: "收藏" },
  { id: "archived", label: "已归档" },
];

interface ShelfShellProps {
  view: ShelfView;
  activePage: DesignPage;
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
  /** 运行时由 UiRoot 托管命令面板（传 null）；设计预览由书架自己渲染。 */
  palette: { open: boolean; onOpen(): void; onClose(): void } | null;
  onRequestImport?: () => void;
  onRequestCreate?: () => void;
  onRequestRecycle?: () => void;
  dialogs?: ReactNode;
}

function ShelfShell({
  view,
  activePage,
  theme,
  onNavigate,
  onToggleTheme,
  palette,
  onRequestImport,
  onRequestCreate,
  onRequestRecycle,
  dialogs,
}: ShelfShellProps) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<BookFilter>("all");
  const [sort, setSort] = useState<SortMode>("updated");

  const paletteOpen = palette?.open ?? false;
  // 命令面板最多占掉一层预算；打开时把状态条挤出模糊层。
  const layers = paletteOpen
    ? ["shelf-command", "shelf-detail", "shelf-status"]
    : ["shelf-detail", "shelf-status"];
  const budget = useAcrylicBudget(paletteOpen ? "shelf-command" : "shelf-detail", layers);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const result = view.books.filter((book) => {
      if (filter === "favorite" && !book.favorite) return false;
      if (filter === "archived" && !book.archived) return false;
      if (!needle) return true;
      return (
        book.title.toLowerCase().includes(needle) || book.subtitle.toLowerCase().includes(needle)
      );
    });
    if (sort === "title") result.sort((a, b) => a.title.localeCompare(b.title));
    return result;
  }, [filter, query, sort, view.books]);

  const selected = view.books.find((book) => book.id === view.selectedId) ?? null;

  const commands: CommandSpec[] = useMemo(
    () => [
      {
        id: "workbench",
        label: "打开工作台",
        hint: selected ? selected.title : "先在书架里选择一部作品",
        icon: "tool",
        disabledReason: selected ? undefined : "未选择作品",
        run: () => view.onEnter("workbench"),
      },
      {
        id: "reader",
        label: "进入阅读器",
        hint: selected ? selected.title : "先在书架里选择一部作品",
        icon: "reader",
        disabledReason: selected ? undefined : "未选择作品",
        run: () => view.onEnter("reader"),
      },
      {
        id: "theme",
        label: theme === "dark" ? "切换到浅色主题" : "切换到深色主题",
        hint: "Mica / Acrylic 同步换色",
        icon: theme === "dark" ? "sun" : "moon",
        run: onToggleTheme,
      },
      {
        id: "settings",
        label: "前往设置",
        hint: "识别 / 翻译 / 存储与插件",
        icon: "settings",
        run: () => onNavigate("settings"),
      },
      {
        id: "import",
        label: "导入本地图片",
        hint: view.canMutate ? "通过系统文件选择器导入" : "设计预览 · 未接 IPC",
        icon: "upload",
        disabledReason: view.canMutate ? undefined : "设计预览模式不可导入",
        run: () => onRequestImport?.(),
      },
      {
        id: "create",
        label: "新建作品",
        hint: "从空白作品开始",
        icon: "plus",
        disabledReason: view.canMutate ? undefined : "设计预览模式不可新建",
        run: () => onRequestCreate?.(),
      },
    ],
    [onNavigate, onRequestCreate, onRequestImport, onToggleTheme, selected, theme, view],
  );

  return (
    <div className="nm-shelf nm-mica" data-testid="page-shelf">
      <header className="nm-titlebar" data-testid="shelf-titlebar">
        <div className="nm-titlebar__brand">
          <span className="nm-brand-mark" aria-hidden="true">
            NM
          </span>
          <span className="nm-brand-name">New Manga</span>
        </div>

        <PrimaryNav activePage={activePage} onNavigate={onNavigate} />

        <div className="nm-titlebar__actions">
          <button
            type="button"
            className="nm-command-trigger"
            data-testid="command-trigger"
            onClick={() => palette?.onOpen()}
            aria-haspopup="dialog"
            aria-expanded={paletteOpen}
          >
            <Icon name="search" size={14} />
            <span>搜索或执行命令</span>
            <span className="nm-command-trigger__keys">
              <kbd className="nm-kbd">Ctrl</kbd>
              <kbd className="nm-kbd">K</kbd>
            </span>
          </button>
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
            data-testid="theme-toggle"
            onClick={onToggleTheme}
          >
            <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
          </button>
          <div className="nm-window-buttons" data-testid="window-buttons" aria-hidden="true">
            <span className="nm-window-btn">
              <Icon name="minus" size={12} />
            </span>
            <span className="nm-window-btn">
              <Icon name="maximize" size={11} />
            </span>
            <span className="nm-window-btn nm-window-btn--close">
              <Icon name="close" size={12} />
            </span>
          </div>
        </div>
      </header>

      <div className="nm-toolbar" data-testid="shelf-toolbar">
        <label className="nm-input nm-search">
          <Icon name="search" size={15} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索书名或原名"
            aria-label="搜索书架"
          />
          {query ? (
            <button
              type="button"
              className="nm-search__clear"
              aria-label="清除搜索"
              onClick={() => setQuery("")}
            >
              <Icon name="close" size={12} />
            </button>
          ) : (
            <span className="nm-data nm-tertiary">/</span>
          )}
        </label>

        <div className="nm-chips" role="group" aria-label="筛选">
          {FILTERS.map((item) => (
            <button
              key={item.id}
              type="button"
              className="nm-chip"
              data-active={filter === item.id}
              aria-pressed={filter === item.id}
              onClick={() => setFilter(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="nm-toolbar__right">
          <label className="nm-select-wrap nm-sort">
            <span className="nm-sr-only">排序方式</span>
            <select
              className="nm-select"
              value={sort}
              onChange={(event) => setSort(event.target.value === "title" ? "title" : "updated")}
              aria-label="排序方式"
            >
              <option value="updated">最近更新</option>
              <option value="title">书名 A–Z</option>
            </select>
            <Icon name="chevron-down" size={13} />
          </label>

          <button
            type="button"
            className="nm-btn"
            data-testid="shelf-import"
            disabled={!view.canMutate}
            title={view.canMutate ? undefined : "设计预览模式不可导入"}
            onClick={() => onRequestImport?.()}
          >
            <Icon name="upload" size={15} />
            导入
          </button>
          <button
            type="button"
            className="nm-btn nm-btn--primary"
            data-testid="shelf-create"
            disabled={!view.canMutate}
            title={view.canMutate ? undefined : "设计预览模式不可新建"}
            onClick={() => onRequestCreate?.()}
          >
            <Icon name="plus" size={15} />
            新建
          </button>
        </div>
      </div>

      <main className="nm-shelf__main">
        <section className="nm-shelf__library" aria-label="书架内容">
          <div className="nm-section-head">
            <div>
              <h1 className="nm-title">全部作品</h1>
              <p className="nm-caption nm-tertiary">
                {view.books.length} 部作品 · {filtered.length} 部正在显示
              </p>
            </div>
            <div className="nm-section-head__meta">
              <span className="nm-tag">
                <Icon name="clock" size={12} />
                {view.canMutate ? "来自 Core 的最新读取" : "设计预览"}
              </span>
              <button
                type="button"
                className="nm-btn nm-btn--ghost nm-btn--icon"
                aria-label="回收站"
                onClick={() => onRequestRecycle?.()}
                disabled={!view.canMutate}
                title={view.canMutate ? "回收站" : "设计预览模式不可用"}
              >
                <Icon name="more" size={16} />
              </button>
            </div>
          </div>

          {view.phase === "loading" && (
            <PageLoading label="正在读取书架" detail="数据来自 Python Core" testId="shelf-loading" />
          )}

          {view.phase === "error" && view.error && (
            <PageError
              title={view.error.title}
              message={view.error.message}
              code={view.error.code}
              retryable={view.error.retryable}
              onRetry={view.onRetry}
              testId="shelf-error"
            />
          )}

          {view.phase === "empty" && (
            <PageEmpty
              title="书架还是空的"
              description="导入本地图片或新建一部作品，数据会写入 Core 管理的媒体库。"
              action={
                <button
                  type="button"
                  className="nm-btn nm-btn--primary"
                  disabled={!view.canMutate}
                  onClick={() => onRequestCreate?.()}
                >
                  <Icon name="plus" size={14} />
                  新建作品
                </button>
              }
              testId="shelf-empty"
            />
          )}

          {view.phase === "ready" && filtered.length === 0 && (
            <PageEmpty
              kind="filtered"
              icon="filter"
              title="没有匹配的作品"
              description="当前搜索或筛选条件下没有作品。"
              action={
                <button
                  type="button"
                  className="nm-btn"
                  onClick={() => {
                    setQuery("");
                    setFilter("all");
                  }}
                >
                  清除筛选
                </button>
              }
              testId="shelf-filtered-empty"
            />
          )}

          {view.phase === "ready" && filtered.length > 0 && (
            <div className="nm-book-grid" data-testid="shelf-grid">
              {filtered.map((book) => (
                <button
                  key={book.id}
                  type="button"
                  className="nm-book-card"
                  data-active={book.id === view.selectedId}
                  aria-pressed={book.id === view.selectedId}
                  data-testid={`book-${book.id}`}
                  onClick={() => view.onSelectBook(book.id)}
                >
                  <span className="nm-book-cover" style={coverStyle(book)}>
                    <span className="nm-book-cover__wash" aria-hidden="true" />
                    <span className="nm-book-cover__kicker">{book.coverKicker}</span>
                    <span className="nm-book-cover__title">{book.title}</span>
                    {book.volume ? (
                      <span className="nm-book-cover__volume">{book.volume}</span>
                    ) : null}
                    {book.state ? (
                      <StatusMark
                        state={book.state}
                        showLabel={false}
                        className="nm-book-cover__status"
                      />
                    ) : null}
                  </span>
                  <span className="nm-book-meta">
                    <span className="nm-book-title">{book.title}</span>
                    <span className="nm-book-count">
                      {book.chaptersLabel} · {book.pagesLabel}
                    </span>
                    {book.progress !== null ? (
                      <span className="nm-progress" aria-hidden="true">
                        <span style={{ width: `${book.progress}%` }} />
                      </span>
                    ) : null}
                    <span className="nm-book-foot">
                      <span>{book.updatedLabel}</span>
                      {book.progress !== null ? (
                        <span className="nm-data">{book.progress}%</span>
                      ) : null}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          )}
        </section>

        <aside
          className={`nm-detail ${budget.className("shelf-detail", "acrylic")}`}
          data-testid="shelf-detail"
          aria-label="作品详情"
        >
          {selected ? (
            <>
              <div className="nm-detail__head">
                <div className="nm-detail__cover" style={coverStyle(selected)} aria-hidden="true">
                  <span>{selected.volume ?? selected.title.slice(0, 2)}</span>
                </div>
                <div className="nm-detail__identity">
                  <h2 className="nm-detail__title">{selected.title}</h2>
                  <p className="nm-caption nm-tertiary">{selected.subtitle}</p>
                  <div className="nm-detail__tags">
                    {selected.favorite ? <span className="nm-tag">收藏</span> : null}
                    {selected.archived ? <span className="nm-tag">已归档</span> : null}
                    <span className="nm-tag">{selected.updatedLabel}</span>
                  </div>
                </div>
              </div>

              <div className="nm-detail__stats">
                <div className="nm-stat">
                  <span className="nm-stat__value nm-data">{view.chapters.length}</span>
                  <span className="nm-stat__label">章节</span>
                </div>
                <div className="nm-stat">
                  <span className="nm-stat__value nm-data">{selected.pagesLabel}</span>
                  <span className="nm-stat__label">页数</span>
                </div>
              </div>

              <div className="nm-detail__section-head">
                <span className="nm-body-strong">章节</span>
                <span className="nm-data nm-tertiary">{view.chapters.length}</span>
              </div>

              {view.chaptersPhase === "loading" && (
                <PageLoading label="正在读取章节" skeletonRows={2} testId="shelf-chapters-loading" />
              )}
              {view.chaptersPhase === "error" && view.chaptersError && (
                <PageError
                  title={view.chaptersError.title}
                  message={view.chaptersError.message}
                  code={view.chaptersError.code}
                  retryable={view.chaptersError.retryable}
                  onRetry={() => view.onSelectBook(selected.id)}
                  testId="shelf-chapters-error"
                />
              )}
              {view.chaptersPhase !== "loading" &&
                view.chaptersPhase !== "error" &&
                view.chapters.length === 0 && (
                  <PageEmpty
                    icon="book"
                    title="还没有章节"
                    description="导入图片时会自动创建章节，或在工作台新建章节。"
                    testId="shelf-chapters-empty"
                  />
                )}
              {view.chapters.length > 0 && (
                <ul className="nm-chapter-list" data-testid="chapter-list">
                  {view.chapters.map((chapter) => (
                    <li key={chapter.id}>
                      <button
                        type="button"
                        className="nm-chapter"
                        data-active={view.activeChapterId === chapter.id}
                        onClick={() => view.onSelectChapter(chapter.id)}
                      >
                        <span className="nm-chapter__index nm-data">{chapter.index}</span>
                        <span className="nm-chapter__title">{chapter.title}</span>
                        <span className="nm-chapter__pages nm-data">{chapter.pagesLabel}</span>
                        {chapter.state ? <StatusMark state={chapter.state} showLabel={false} /> : null}
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              <div className="nm-detail__actions">
                <button
                  type="button"
                  className="nm-btn nm-btn--primary"
                  onClick={() => view.onEnter("reader")}
                >
                  <Icon name="play" size={14} />
                  继续阅读
                </button>
                <button type="button" className="nm-btn" onClick={() => view.onEnter("workbench")}>
                  <Icon name="tool" size={14} />
                  工作台
                </button>
              </div>
            </>
          ) : (
            <PageEmpty
              icon="book"
              title="未选择作品"
              description="从左侧网格选择一部作品查看章节与详情。"
              testId="shelf-detail-empty"
            />
          )}
        </aside>
      </main>

      <div
        className={`nm-floating-status ${budget.className("shelf-status", "acrylic-24")}`}
        data-testid="shelf-statusbar"
        role="status"
        aria-live="polite"
      >
        <StatusMark state={view.coreState} />
        <span className="nm-floating-status__text">{view.statusText}</span>
        {view.statusDetail ? (
          <span className="nm-caption nm-tertiary">{view.statusDetail}</span>
        ) : null}
        {view.statusProgress !== null ? (
          <div className="nm-floating-status__progress">
            <div className="nm-progress">
              <span style={{ width: `${view.statusProgress}%` }} />
            </div>
          </div>
        ) : null}
        <span className="nm-floating-status__spacer" />
        <span className="nm-core">
          <span className="nm-core__dot" aria-hidden="true" />
          {view.coreLabel}
        </span>
        <span className="nm-divider" aria-hidden="true" />
        <span className="nm-data nm-tertiary">{view.statusRight}</span>
      </div>

      {palette ? (
        <CommandPalette
          open={palette.open}
          onClose={palette.onClose}
          commands={commands}
          title="命令面板"
        />
      ) : null}

      {dialogs}
    </div>
  );
}

/* ------------------------------------------------------------------ *
 * 两种数据源各自的薄壳
 * ------------------------------------------------------------------ */

function PreviewShelf(props: Omit<ShelfProps, "runtime">) {
  const view = usePreviewView();
  const [paletteOpen, setPaletteOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPaletteOpen((open) => !open);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <ShelfShell
      view={view}
      activePage={props.activePage}
      theme={props.theme}
      onNavigate={props.onNavigate}
      onToggleTheme={props.onToggleTheme}
      palette={{
        open: paletteOpen,
        onOpen: () => setPaletteOpen(true),
        onClose: () => setPaletteOpen(false),
      }}
    />
  );
}

function RuntimeShelf(props: ShelfProps & { runtime: PageRuntime }) {
  const { runtime } = props;
  const state = useRuntimeShelf(runtime);
  const [importOpen, setImportOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [recycleOpen, setRecycleOpen] = useState(false);

  return (
    <ShelfShell
      view={state.view}
      activePage={props.activePage}
      theme={props.theme}
      onNavigate={props.onNavigate}
      onToggleTheme={props.onToggleTheme}
      palette={null}
      onRequestImport={() => setImportOpen(true)}
      onRequestCreate={() => setCreateOpen(true)}
      onRequestRecycle={() => setRecycleOpen(true)}
      dialogs={
        <>
          <ImportDialog
            isOpen={importOpen}
            books={state.rawBooks}
            chapters={state.rawChapters}
            initialBookId={state.view.selectedId}
            initialChapterId={state.view.activeChapterId}
            client={runtime.clients.library}
            onClose={() => setImportOpen(false)}
            onImportSuccess={() => {
              setImportOpen(false);
              state.onImportSuccess();
            }}
          />
          {createOpen ? (
            <CreateTitleDialog
              entity="作品"
              onClose={() => setCreateOpen(false)}
              onSubmit={async (title: string) => {
                await state.onCreateBook(title);
                setCreateOpen(false);
              }}
            />
          ) : null}
          {recycleOpen ? (
            <div className="nm-command-backdrop" data-testid="shelf-recycle-overlay">
              <div className="nm-shelf-recycle-surface">
                <RecycleBinPage
                  client={runtime.clients.library}
                  activeBooksCount={state.rawBooks.length}
                  onClose={() => setRecycleOpen(false)}
                  onDeleteSuccess={() => state.onImportSuccess()}
                />
              </div>
            </div>
          ) : null}
        </>
      }
    />
  );
}

/* ------------------------------------------------------------------ *
 * 页面入口
 * ------------------------------------------------------------------ */

export interface ShelfProps {
  activePage: DesignPage;
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
  /**
   * 真实运行时注入。缺省时本页渲染设计预览的固定 fixtures（`?view=design`）；
   * 存在时改为经 `runtime.clients` 取真实 IPC 数据，并且**不得**回填任何
   * fixtures 数值冒充真实数据。
   */
  runtime?: PageRuntime;
}

export function Shelf(props: ShelfProps) {
  return props.runtime ? <RuntimeShelf {...props} runtime={props.runtime} /> : <PreviewShelf {...props} />;
}
