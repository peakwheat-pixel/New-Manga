import { useEffect, useRef, useState, type ReactNode } from "react";
import { Icon } from "../components/Icon";
import { PagePlaceholder } from "../components/PagePlaceholder";
import { PrimaryNav } from "../components/PrimaryNav";
import { StatusMark } from "../components/StatusMark";
import { useAcrylicBudget } from "../design/useAcrylicBudget";
import type { DesignPage, Theme } from "../design/types";
import type { BookSummary, ChapterNavSummary, PageNavSummary } from "../library/types";
import type { ReaderLayout } from "../reader/types";
import { PageBlocked, PageEmpty, PageError, PageLoading } from "../ui/PageState";
import type { PageRuntime } from "../ui/types";
import "./reader-settings.css";

/**
 * 阅读器页（v2 语言）。
 *
 * 两条渲染路径，互斥：
 *   1. `runtime` 缺省 → 设计预览 fixtures（`?view=design`）。这里是原有骨架的
 *      原样保留：24 页固定占位、单页/双页与左右方向开关、页码 012/024。
 *   2. `runtime` 存在 → 真实 IPC 数据。章节列表、页面序列、阅读投影、页图资源
 *      全部经 `runtime.clients` 取得；**没有 IPC 来源的字段一律省略或显示
 *      「—」**（阅读完成度、已校对页数、流水线状态在 v2 阅读器里都没有来源，
 *      因此运行态不再渲染 fixtures 里的 62% / 15/24 / 「进行中」）。
 *
 * 页图链路（与历史内联样式实现一致，本页只重画 UI，不重写链路）：
 *   resolve_page_resource(page_id) → issue_resource_url(resource_id, revision)
 *   → fetchAll(chunked) → Blob URL；切页/卸载时 URL.revokeObjectURL。
 *
 * 进度：`library_get_reader_projection` 提供初始页与已保存进度
 * （`saved_progress.progress_percent`），翻页后用
 * `library_save_reading_progress` 写回。投影失败不清空阅读：页序列仍然来自
 * `list_chapter_pages`，只是进度显示为「—」并标明不可用原因。
 */

const FIXTURE_TOTAL_PAGES = 24;

export interface ReaderProps {
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
  /** 真实运行时注入；缺省为设计预览 fixtures。见 `ui/types.ts`。 */
  runtime?: PageRuntime;
}

export function Reader({ theme, onNavigate, onToggleTheme, runtime }: ReaderProps) {
  if (runtime) {
    return <ReaderRuntime theme={theme} onToggleTheme={onToggleTheme} runtime={runtime} />;
  }
  return <ReaderFixture theme={theme} onNavigate={onNavigate} onToggleTheme={onToggleTheme} />;
}

/* ---------------------------------------------------------------------
 * 共用外壳
 * ------------------------------------------------------------------ */

function ReaderTitlebar({
  activePage,
  onNavigate,
  onOpenCommand,
  commandOpen = false,
}: {
  activePage: DesignPage;
  onNavigate: (page: DesignPage) => void;
  /** 运行时由 `chrome.onOpenCommand` 提供；设计预览不传（没有命令面板）。 */
  onOpenCommand?: () => void;
  commandOpen?: boolean;
}) {
  return (
    <header className="nm-titlebar" data-testid="reader-titlebar">
      <div className="nm-titlebar__brand">
        <span className="nm-brand-mark" aria-hidden="true">
          NM
        </span>
        <span className="nm-brand-name">New Manga</span>
      </div>
      <PrimaryNav activePage={activePage} onNavigate={onNavigate} />
      <div className="nm-titlebar__actions" style={{ justifyContent: "flex-end" }}>
        {/* 四页标题栏统一提供命令入口（Shelf / Workbench / Reader / Settings）。 */}
        {onOpenCommand ? (
          <button
            type="button"
            className="nm-command-trigger"
            data-testid="command-trigger"
            onClick={onOpenCommand}
            aria-haspopup="dialog"
            aria-expanded={commandOpen}
          >
            <Icon name="search" size={14} />
            <span>搜索或执行命令</span>
            <span className="nm-command-trigger__keys">
              <kbd className="nm-kbd">Ctrl</kbd>
              <kbd className="nm-kbd">K</kbd>
            </span>
          </button>
        ) : null}
        <div className="nm-window-buttons" aria-hidden="true">
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
  );
}

/* ---------------------------------------------------------------------
 * 1. 设计预览 fixtures（原骨架，逐字节保留结构与类名）
 * ------------------------------------------------------------------ */

function ReaderFixture({
  theme,
  onNavigate,
  onToggleTheme,
}: {
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
}) {
  const [page, setPage] = useState(12);
  const [spread, setSpread] = useState("single");
  const [direction, setDirection] = useState("ltr");
  const budget = useAcrylicBudget("reader-top", ["reader-top", "reader-bottom"]);

  const step = (delta: number) => {
    setPage((current) => Math.min(FIXTURE_TOTAL_PAGES, Math.max(1, current + delta)));
  };

  /*
   * 底栏写着「← → 翻页」就必须真的能翻。骨架阶段只覆盖左右方向键；
   * 没实现的键（曾经的 F 全屏）不留提示，避免做出假承诺。
   */
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.isContentEditable === true;
      if (typing || event.ctrlKey || event.metaKey || event.altKey) return;
      // 焦点在 tablist（一级切换栏 / 检查器 rail）里时，方向键归 tab 导航，
      // 不能再同时翻页——否则一次按键既切页又翻页。
      // 注意 target 可能是 window（测试里就是），必须先确认是 Element 再调 closest。
      if (target instanceof Element && target.closest('[role="tablist"]')) return;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        step(-1);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        step(1);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <div className="nm-reader" data-testid="page-reader">
      <ReaderTitlebar activePage="reader" onNavigate={onNavigate} />

      <div className="nm-reader__body">
        <div className="nm-reader__page-area">
          <PagePlaceholder pageNumber={page} totalPages={FIXTURE_TOTAL_PAGES} chapter="第 12 话" />
        </div>

        <div
          className={`nm-reader__top ${budget.className("reader-top", "acrylic-24")}`}
          data-testid="reader-top"
        >
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            onClick={() => onNavigate("shelf")}
            aria-label="返回书架"
            title="返回书架"
          >
            <Icon name="arrow-left" size={17} />
          </button>
          <span className="nm-reader__chapter">
            <span className="nm-reader__book">雾港来信</span>
            <span className="nm-reader__sep">·</span>
            <span>第 12 话</span>
          </span>
          <span className="nm-data nm-reader__pager">
            {String(page).padStart(3, "0")} / {String(FIXTURE_TOTAL_PAGES).padStart(3, "0")}
          </span>
          <StatusMark state="running" />
          <span className="nm-divider" aria-hidden="true" />
          <div className="nm-segmented" role="group" aria-label="阅读模式">
            <button
              type="button"
              data-active={spread === "single"}
              aria-pressed={spread === "single"}
              onClick={() => setSpread("single")}
            >
              单页
            </button>
            <button
              type="button"
              data-active={spread === "double"}
              aria-pressed={spread === "double"}
              onClick={() => setSpread("double")}
            >
              双页
            </button>
          </div>
          <div className="nm-segmented" role="group" aria-label="阅读方向">
            <button
              type="button"
              data-active={direction === "ltr"}
              aria-pressed={direction === "ltr"}
              onClick={() => setDirection("ltr")}
            >
              左 → 右
            </button>
            <button
              type="button"
              data-active={direction === "rtl"}
              aria-pressed={direction === "rtl"}
              onClick={() => setDirection("rtl")}
            >
              右 → 左
            </button>
          </div>
          <span className="nm-reader__spacer" />
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            onClick={() => onNavigate("workbench")}
            aria-label="打开工作台"
            title="打开工作台"
          >
            <Icon name="tool" size={16} />
          </button>
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
            onClick={onToggleTheme}
          >
            <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
          </button>
          <button type="button" className="nm-btn" onClick={() => onNavigate("settings")}>
            <Icon name="settings" size={14} />
            设置
          </button>
        </div>

        <button
          type="button"
          className="nm-reader__nav nm-reader__nav--prev"
          onClick={() => step(-1)}
          aria-label="上一页"
        >
          <Icon name="chevron-left" size={20} />
        </button>
        <button
          type="button"
          className="nm-reader__nav nm-reader__nav--next"
          onClick={() => step(1)}
          aria-label="下一页"
        >
          <Icon name="chevron-right" size={20} />
        </button>

        <div
          className={`nm-reader__bottom ${budget.className("reader-bottom", "acrylic-24")}`}
          data-testid="reader-bottom"
        >
          <span className="nm-caption nm-tertiary">本话完成度</span>
          <span className="nm-data">62%</span>
          <div className="nm-progress nm-reader__progress">
            <span style={{ width: "62%" }} />
          </div>
          <span className="nm-caption nm-tertiary">已校对 15 / 24 页</span>
          <span className="nm-reader__spacer" />
          <span className="nm-keyhint">
            <kbd className="nm-kbd">←</kbd>
            <kbd className="nm-kbd">→</kbd>
            翻页
          </span>
          <span className="nm-keyhint">
            <kbd className="nm-kbd">Esc</kbd>
            返回
          </span>
        </div>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------
 * 2. 真实运行时
 * ------------------------------------------------------------------ */

type ReaderData =
  | { phase: "loading" }
  | { phase: "error"; code: string }
  | {
      phase: "empty";
      kind: "noChapters" | "noPages";
      bookTitle: string | null;
      chapterLabel: string | null;
    }
  | {
      phase: "ready";
      chapters: ChapterNavSummary[];
      chapter: ChapterNavSummary;
      bookTitle: string | null;
      pages: PageNavSummary[];
      /** 阅读投影给出的真实布局；投影不可用时为 null（不猜）。 */
      layout: ReaderLayout | null;
      /** `library_get_reader_projection` 失败时的错误码：进度未知，但可翻页。 */
      projectionCode: string | null;
    };

interface PageImageState {
  phase: "idle" | "loading" | "ready" | "error";
  url?: string;
  code?: string;
}

const LAYOUT_LABELS: Readonly<Record<ReaderLayout, string>> = {
  rtl: "右 → 左",
  ltr: "左 → 右",
  webtoon_vertical: "纵向条漫",
};

/** 从一个被 reject 的值里取稳定错误码（Core envelope / Error / 字符串）。 */
function errorCode(error: unknown): string {
  if (typeof error === "string" && error.length > 0) return error;
  if (error && typeof error === "object") {
    const code = (error as { code?: unknown }).code;
    if (typeof code === "string" && code.length > 0) return code;
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.length > 0) return message;
  }
  return "CORE_UNAVAILABLE";
}

/** 章节显示名：`章节号 · 标题`，两者都缺时显式「—」。 */
function chapterLabel(chapter: ChapterNavSummary): string {
  const number = chapter.chapter_number.trim();
  const title = chapter.title.trim();
  if (number && title) return `${number} · ${title}`;
  return title || number || "—";
}

function ReaderRuntime({
  theme,
  onToggleTheme,
  runtime,
}: {
  theme: Theme;
  onToggleTheme: () => void;
  runtime: PageRuntime;
}) {
  const { chrome, clients } = runtime;
  const bookId = chrome.context.bookId;
  const requestedChapterId = chrome.context.chapterId;

  const [reloadNonce, setReloadNonce] = useState(0);
  const [data, setData] = useState<ReaderData>({ phase: "loading" });
  const [pageIndex, setPageIndex] = useState(0);
  const [progressPercent, setProgressPercent] = useState<number | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [image, setImage] = useState<PageImageState>({ phase: "idle" });
  const [imageNonce, setImageNonce] = useState(0);
  /** 上一次已经写回过的 page_id：初始页不写回，只写用户真的翻到的页。 */
  const lastSavedPageRef = useRef<string | null>(null);

  /*
   * 亚克力预算：本页声明两层（顶栏、底栏）。命令面板是全屏模态，它自己也占
   * 一层 backdrop-filter，所以面板打开时本页把预算压到 1：顶栏保留、底栏降级
   * 为 .nm-acrylic-off。页面自身永远不超过同屏两层的硬上限。
   */
  const budget = useAcrylicBudget(
    "reader-top",
    ["reader-top", "reader-bottom"],
    chrome.commandOpen ? 1 : 2,
  );

  // 1. 取数：章节 → 页序列 →（非致命）阅读投影。
  useEffect(() => {
    if (!bookId) return;
    let active = true;
    setData({ phase: "loading" });
    setPageIndex(0);
    setProgressPercent(null);
    setSaveError(null);
    lastSavedPageRef.current = null;

    void (async () => {
      try {
        const [chapters, books] = await Promise.all([
          clients.library.listChapters(bookId),
          clients.library.listBooks().catch(() => [] as BookSummary[]),
        ]);
        if (!active) return;

        const bookTitle = books.find((book) => book.book_id === bookId)?.title ?? null;
        if (chapters.length === 0) {
          setData({
            phase: "empty",
            kind: "noChapters",
            bookTitle,
            chapterLabel: null,
          });
          return;
        }

        // context.chapterId 优先；为 null 时取第一章（chrome.onOpenBook 的契约：
        // chapterId 为 null = 「该书下有章节时取第一章」，不是页面自行编造）。
        const chapter = chapters.find((item) => item.chapter_id === requestedChapterId) ?? chapters[0];
        const pages = await clients.library.listChapterPages(chapter.chapter_id);
        if (!active) return;
        if (pages.length === 0) {
          setData({
            phase: "empty",
            kind: "noPages",
            bookTitle,
            chapterLabel: chapterLabel(chapter),
          });
          return;
        }

        let layout: ReaderLayout | null = null;
        let projectionCode: string | null = null;
        let initialPageId: string | null = null;
        let savedPercent: number | null = null;
        try {
          const projection = await clients.reader.getReaderProjection(
            chapter.chapter_id,
            "original",
            "resume",
          );
          layout = projection.layout;
          initialPageId = projection.initial_position.page_id;
          savedPercent = projection.saved_progress?.progress_percent ?? null;
        } catch (error) {
          // 投影只负责「初始页 + 进度」。它失败不妨碍按真实页序列阅读；
          // 进度显示为「—」并在底栏标明不可用原因，绝不回填假百分比。
          projectionCode = errorCode(error);
        }
        if (!active) return;

        const foundIndex =
          initialPageId === null ? -1 : pages.findIndex((page) => page.page_id === initialPageId);
        const resolvedIndex = foundIndex >= 0 ? foundIndex : 0;
        lastSavedPageRef.current = pages[resolvedIndex]?.page_id ?? null;
        setProgressPercent(savedPercent);
        setPageIndex(resolvedIndex);
        setData({
          phase: "ready",
          chapters,
          chapter,
          bookTitle,
          pages,
          layout,
          projectionCode,
        });
      } catch (error) {
        if (!active) return;
        setData({ phase: "error", code: errorCode(error) });
      }
    })();

    return () => {
      active = false;
    };
  }, [bookId, requestedChapterId, reloadNonce, clients.library, clients.reader]);

  const ready = data.phase === "ready" ? data : null;
  const pages = ready?.pages ?? [];
  const pageCount = pages.length;
  // 数据刚切换的中间帧里 pageIndex 可能越界，渲染前先收敛（不造页）。
  const safeIndex = pageCount > 0 ? Math.min(Math.max(pageIndex, 0), pageCount - 1) : 0;
  const currentPage = pages[safeIndex] ?? null;
  const currentPageId = currentPage?.page_id ?? null;
  const chapterId = ready?.chapter.chapter_id ?? null;
  const layout = ready?.layout ?? null;

  // 2. 进度写回：只在用户真的换了页时发生（初始页由投影决定，不回写）。
  useEffect(() => {
    if (chapterId === null || currentPageId === null) return;
    if (lastSavedPageRef.current === currentPageId) return;
    lastSavedPageRef.current = currentPageId;
    let active = true;
    void (async () => {
      try {
        const snapshot = await clients.reader.saveReadingProgress({
          chapterId,
          mode: "original",
          pageId: currentPageId,
          scrollOffsetY: 0,
        });
        if (!active) return;
        setProgressPercent(snapshot.progress_percent);
        setSaveError(null);
      } catch (error) {
        if (!active) return;
        // 写回失败不阻断阅读：底栏给出错误码，进度保持上一次已知值。
        setSaveError(errorCode(error));
      }
    })();
    return () => {
      active = false;
    };
  }, [chapterId, currentPageId, clients.reader]);

  // 3. 页图：resolve → issue → fetchAll → Blob URL；切页/卸载必须 revoke。
  //    纵向条漫布局被显式阻塞，不需要为它拉任何页图（不假装可读）。
  useEffect(() => {
    if (currentPageId === null || layout === "webtoon_vertical") return;
    let active = true;
    let createdUrl: string | null = null;
    setImage({ phase: "loading" });
    void (async () => {
      try {
        const resolved = await clients.library.resolvePageResource(currentPageId);
        const issued = await clients.resource.issue(resolved.resource_id, resolved.revision);
        if (!active) return;
        const blob = await clients.resource.fetchAll(issued.url, issued.size);
        if (!active) return;
        createdUrl = URL.createObjectURL(blob);
        setImage({ phase: "ready", url: createdUrl });
      } catch (error) {
        if (!active) return;
        setImage({ phase: "error", code: errorCode(error) });
      }
    })();
    return () => {
      active = false;
      if (createdUrl !== null) URL.revokeObjectURL(createdUrl);
    };
  }, [currentPageId, layout, clients.library, clients.resource, imageNonce]);

  // 4. ←/→ 翻页。tablist 内（一级切换栏 / 章节下拉之外的 tab）与输入框内不劫持。
  useEffect(() => {
    if (pageCount === 0) return;
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.tagName === "SELECT" ||
        target?.isContentEditable === true;
      if (typing || event.ctrlKey || event.metaKey || event.altKey) return;
      if (target instanceof Element && target.closest('[role="tablist"]')) return;
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      // RTL 作品里 ← 是下一页（与历史实现的翻页方向一致）。
      const rtl = layout === "rtl";
      const delta =
        event.key === "ArrowLeft" ? (rtl ? 1 : -1) : rtl ? -1 : 1;
      event.preventDefault();
      setPageIndex((current) => {
        const next = current + delta;
        if (next < 0 || next > pageCount - 1) return current;
        return next;
      });
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [pageCount, layout]);

  const move = (delta: number) => {
    setPageIndex((current) => {
      const next = current + delta;
      if (next < 0 || next > pageCount - 1) return current;
      return next;
    });
  };

  const webtoonBlocked = layout === "webtoon_vertical";
  const rtl = layout === "rtl";
  // 物理左/右按钮的翻页方向随布局反转，与 ←/→ 键保持一致。
  const leftDelta = rtl ? 1 : -1;
  const rightDelta = -leftDelta;
  const canMove = (delta: number) => {
    const next = safeIndex + delta;
    return next >= 0 && next <= pageCount - 1;
  };

  /*
   * 顶/底浮层带是阅读器设计的一部分，任何状态都在（设计稿：48 标题栏 +
   * 顶 48 浮层 + 底 40 浮层）。没有可读章节时浮层保留、翻页按钮 disabled，
   * 书名 / 章节 / 页码显示「—」，并在 aria-label / title 里写明原因——
   * 这样空态既不会"只剩一张卡片"，也不会为了好看填假数据。
   */
  const commandOpen = chrome.commandOpen === true;
  const navDisabledReason: string | null = !bookId
    ? "当前没有可读章节"
    : data.phase === "loading"
      ? "章节还在读取中"
      : data.phase === "error"
        ? "阅读数据不可用"
        : webtoonBlocked
          ? "纵向条漫布局尚未接线"
          : null;
  const canTurn = navDisabledReason === null;
  const leftLabel = canTurn ? (rtl ? "下一页" : "上一页") : "上一页";
  const rightLabel = canTurn ? (rtl ? "上一页" : "下一页") : "下一页";
  const withReason = (label: string) =>
    navDisabledReason === null ? label : `${label}（${navDisabledReason}）`;
  // 页码：有真实页序列时才给 x / y；未知一律「—/—」。
  const pagerText =
    ready !== null && !webtoonBlocked ? `${safeIndex + 1} / ${pageCount}` : "—/—";
  const layoutText =
    ready === null ? "—" : layout === null ? "布局未知" : LAYOUT_LABELS[layout];

  const backToShelf = (
    <button
      type="button"
      className="nm-btn nm-btn--primary"
      data-testid="reader-back-to-shelf"
      onClick={() => chrome.onNavigate("shelf")}
    >
      <Icon name="arrow-left" size={14} />
      返回书架
    </button>
  );

  let bodyContent: ReactNode;
  if (!bookId) {
    bodyContent = (
      <PageEmpty
        title="尚未选择阅读作品"
        description="请先在书架选择作品与章节，再进入阅读器；本页不会用占位内容冒充可读章节。"
        icon="book"
        testId="reader-no-context"
        action={backToShelf}
      />
    );
  } else if (data.phase === "loading") {
    bodyContent = (
      <PageLoading
        label="正在读取章节"
        detail="章节列表 / 页面序列 / 阅读进度"
        testId="reader-loading"
      />
    );
  } else if (data.phase === "error") {
    bodyContent = (
      <PageError
        title="阅读数据加载失败"
        message="无法读取章节或页面序列；这不代表作品没有内容，请重试。"
        code={data.code}
        retryable
        onRetry={() => setReloadNonce((nonce) => nonce + 1)}
        testId="reader-error"
      />
    );
  } else if (data.phase === "empty") {
    const title = data.kind === "noChapters" ? "该书暂无章节" : "该章节暂无页面";
    const description =
      data.kind === "noChapters"
        ? `${data.bookTitle ? `《${data.bookTitle}》` : "该作品"}还没有章节：请先在书架或工作台创建章节。`
        : `${data.chapterLabel ? `${data.chapterLabel} ` : "本话"}还没有可阅读页面：请先在书架或工作台导入页面。`;
    bodyContent = (
      <PageEmpty
        title={title}
        description={description}
        icon="book"
        testId="reader-empty"
        action={backToShelf}
      />
    );
  } else if (webtoonBlocked) {
    bodyContent = (
      <PageBlocked
        title="纵向条漫布局尚未接线"
        message="该章节的阅读布局是 webtoon_vertical（纵向滚动）。v2 阅读器目前只接线了分页布局（rtl / ltr）的取图与进度语义，不会用分页方式假装可读。"
        detail="READER_LAYOUT_WEBTOON_NOT_WIRED"
        testId="reader-webtoon-blocked"
      />
    );
  } else if (image.phase === "loading" || image.phase === "idle") {
    bodyContent = (
      <PageLoading
        label={`正在加载第 ${safeIndex + 1} 页`}
        detail={`共 ${pageCount} 页`}
        skeletonRows={0}
        testId="reader-page-loading"
      />
    );
  } else if (image.phase === "error") {
    bodyContent = (
      <PageError
        title="页面图像加载失败"
        message="资源通道没有返回本页图像；可以重试，或返回书架稍后再试。"
        code={image.code}
        retryable
        onRetry={() => setImageNonce((nonce) => nonce + 1)}
        testId="reader-page-error"
      />
    );
  } else {
    bodyContent = (
      <img
        className="nm-reader__image"
        data-testid="reader-page-image"
        src={image.url}
        alt={`第 ${safeIndex + 1} 页，共 ${pageCount} 页`}
        draggable={false}
      />
    );
  }

  return (
    <div className="nm-reader" data-testid="page-reader">
      <ReaderTitlebar
        activePage={chrome.activePage}
        onNavigate={chrome.onNavigate}
        onOpenCommand={chrome.onOpenCommand}
        commandOpen={commandOpen}
      />

      <div className="nm-reader__body">
        <div className="nm-reader__page-area">{bodyContent}</div>

        <div
          className={`nm-reader__top ${budget.className("reader-top", "acrylic-24")}`}
          data-testid="reader-top"
        >
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            onClick={() => chrome.onNavigate("shelf")}
            aria-label="返回书架"
            title="返回书架"
          >
            <Icon name="arrow-left" size={17} />
          </button>
          <span className="nm-reader__chapter">
            <span className="nm-reader__book" data-testid="reader-book-title">
              {ready?.bookTitle ?? "—"}
            </span>
            <span className="nm-reader__sep" aria-hidden="true">
              ·
            </span>
            <span data-testid="reader-chapter-title">
              {ready === null ? "—" : chapterLabel(ready.chapter)}
            </span>
          </span>
          <span className="nm-data nm-reader__pager" data-testid="reader-pager">
            {pagerText}
          </span>
          <span className="nm-tag" data-testid="reader-layout">
            {layoutText}
          </span>
          {ready !== null && ready.chapters.length > 1 ? (
            <label className="nm-select-wrap">
              <span className="nm-sr-only">切换章节</span>
              <select
                className="nm-select"
                data-testid="reader-chapter-select"
                value={ready.chapter.chapter_id}
                onChange={(event) => {
                  const next = event.target.value;
                  if (!bookId || next === ready.chapter.chapter_id) return;
                  chrome.onSelectChapter(bookId, next);
                }}
              >
                {ready.chapters.map((chapter) => (
                  <option key={chapter.chapter_id} value={chapter.chapter_id}>
                    {chapterLabel(chapter)}
                  </option>
                ))}
              </select>
              <Icon name="chevron-down" size={13} />
            </label>
          ) : null}
          <span className="nm-reader__spacer" />
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            onClick={() => chrome.onNavigate("workbench")}
            aria-label="打开工作台"
            title="打开工作台"
          >
            <Icon name="tool" size={16} />
          </button>
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
            onClick={onToggleTheme}
          >
            <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
          </button>
          <button
            type="button"
            className="nm-btn"
            data-testid="reader-open-settings"
            onClick={() => chrome.onNavigate("settings")}
          >
            <Icon name="settings" size={14} />
            设置
          </button>
        </div>

        <button
          type="button"
          className="nm-reader__nav nm-reader__nav--prev"
          data-testid="reader-prev"
          onClick={() => move(leftDelta)}
          disabled={!canTurn || !canMove(leftDelta)}
          aria-label={withReason(leftLabel)}
          title={withReason(leftLabel)}
        >
          <Icon name="chevron-left" size={20} />
        </button>
        <button
          type="button"
          className="nm-reader__nav nm-reader__nav--next"
          data-testid="reader-next"
          onClick={() => move(rightDelta)}
          disabled={!canTurn || !canMove(rightDelta)}
          aria-label={withReason(rightLabel)}
          title={withReason(rightLabel)}
        >
          <Icon name="chevron-right" size={20} />
        </button>

        <div
          className={`nm-reader__bottom ${budget.className("reader-bottom", "acrylic-24")}`}
          data-testid="reader-bottom"
        >
          <span className="nm-caption nm-tertiary">本话进度</span>
          <span className="nm-data" data-testid="reader-progress">
            {progressPercent === null ? "—" : `${Math.round(progressPercent)}%`}
          </span>
          {progressPercent === null ? null : (
            <div className="nm-progress nm-reader__progress" aria-hidden="true">
              <span style={{ width: `${Math.min(100, Math.max(0, progressPercent))}%` }} />
            </div>
          )}
          {ready?.projectionCode != null ? (
            <span className="nm-reader__warning" data-testid="reader-progress-unavailable">
              进度未知（{ready.projectionCode}）
            </span>
          ) : null}
          {saveError !== null ? (
            <span
              className="nm-reader__warning nm-reader__warning--failed"
              data-testid="reader-save-error"
            >
              进度写回失败（{saveError}）
            </span>
          ) : null}
          <span className="nm-reader__spacer" />
          {navDisabledReason === null ? (
            <span className="nm-keyhint">
              <kbd className="nm-kbd">←</kbd>
              <kbd className="nm-kbd">→</kbd>
              翻页
            </span>
          ) : (
            <span className="nm-caption nm-tertiary" data-testid="reader-band-note">
              {navDisabledReason}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
