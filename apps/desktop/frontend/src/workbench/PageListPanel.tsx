/**
 * <PageListPanel> — page navigation (M2-UI1 §2.2 mapping: QML
 * `PageListPanel.qml` + `PageTile`). M2-PAGE-NAV-PROJECTION-1: the
 * three-level drill-down book -> chapter -> page over the frozen read-only
 * projections (`library_list_books` + `list_chapters` +
 * `list_chapter_pages`, contract M2-C1 rev 1.8 §5); a page click feeds
 * `onPageIdChange`, which drives the existing resolve -> image chain. The
 * page-id entry stays as the known-page locator. Drill-down data/loading state
 * is owned by <WorkbenchPage>; expand/collapse is local UI state there too
 * (clicking the open book/chapter again collapses it).
 */

import type { BookSummary, ChapterNavSummary, PageNavSummary } from "../library/types";
import type { TaskProjection } from "./client";
import { DisabledFeature } from "./DisabledFeature";
import { parseSemanticError } from "../bookshelf/error";
import { useEffect, useRef } from "react";

export interface PageListPanelProps {
  books: BookSummary[];
  selectedBookId: string | null;
  chapters: ChapterNavSummary[];
  chaptersBusy: boolean;
  chaptersError: string | null;
  selectedChapterId: string | null;
  pages: PageNavSummary[];
  pagesBusy: boolean;
  pagesError: string | null;
  pageId: string;
  onPageIdChange: (pageId: string, modifiers?: { ctrlKey: boolean; shiftKey: boolean }) => void;
  onPageSelect?: (pageId: string, modifiers?: { ctrlKey: boolean; shiftKey: boolean }) => void;
  onSelectBook: (bookId: string) => void;
  onSelectChapter: (chapterId: string) => void;
  selectedPageIds?: string[];
  taskProjection?: TaskProjection | null;
  pageFilter?: string | null;
  booksBusy?: boolean;
  booksError?: string | null;
  onClearPageFilter?: () => void;
  onRetryBooks?: () => void;
  onRetryChapters?: () => void;
  onRetryPages?: () => void;
}

const listStyle = {
  listStyle: "none",
  margin: 0,
  padding: 0,
  display: "flex",
  flexDirection: "column",
  gap: 2,
} as const;

const tileStyle = (selected: boolean) =>
  ({
    width: "100%",
    textAlign: "left",
    background: selected ? "#e8edff" : "transparent",
    color: "#1f2328",
    border: "1px solid #d9d9d6",
    borderRadius: 4,
    padding: "4px 6px",
    cursor: "pointer",
    fontSize: 12,
  }) as const;

const noteStyle = { color: "#6b7280", fontSize: 11 } as const;

export function PageListPanel({
  books,
  selectedBookId,
  chapters,
  chaptersBusy,
  chaptersError,
  selectedChapterId,
  pages,
  pagesBusy,
  pagesError,
  pageId,
  onPageIdChange,
  onPageSelect,
  onSelectBook,
  onSelectChapter,
  selectedPageIds = [],
  taskProjection = null,
  pageFilter = null,
  booksBusy = false,
  booksError = null,
  onClearPageFilter,
  onRetryBooks,
  onRetryChapters,
  onRetryPages,
}: PageListPanelProps) {
  const panelRef = useRef<HTMLElement | null>(null);
  useEffect(() => {
    const target = Array.from(panelRef.current?.querySelectorAll<HTMLButtonElement>('button[data-testid^="page-tile-"]') ?? [])
      .find((button) => button.getAttribute("data-testid") === `page-tile-${pageId.trim()}`);
    target?.scrollIntoView?.({ block: "nearest" });
  }, [pageId, pageFilter, pages]);
  const projectedRows = taskProjection?.rows ?? [];
  const visiblePages = pages.filter((page) => {
    if (!pageFilter) return true;
    const row = projectedRows.find((item) => item.page_id === page.page_id);
    if (!row) return false;
    return pageFilter === "waiting" ? row.status === "waiting" || row.status === "processing" : row.status === pageFilter;
  });
  return (
    <section
      ref={panelRef}
      data-testid="page-list-panel"
      style={{
        border: "1px solid #d9d9d6",
        background: "#fff",
        borderRadius: 6,
        padding: 8,
        width: 240,
        minWidth: 200,
        maxWidth: 320,
        flex: "0 0 240px",
        overflow: "auto",
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <h2 style={{ fontSize: 13, margin: 0, color: "#1f2328" }}>{selectedChapterId ? "页面列表" : "选择作品与章节"}</h2>
      <DisabledFeature id="gap-g14-page-order" label="拖动调整页序" reason="页序写入 wire 尚未冻结，页面顺序保持 Core 投影结果。" />
      <DisabledFeature id="gap-g18-page-thumbnails" label="页面缩略图" reason="当前只有原图资源通道，低清缩略图能力尚未接入。" />
      <label style={{ fontSize: 11, color: "#6b7280", display: "flex", flexDirection: "column", gap: 2 }}>
        按页面 ID 定位
        <input
          data-testid="page-id-input"
          aria-label="按页面 ID 定位"
          value={pageId}
          onChange={(event) => onPageIdChange(event.target.value)}
          placeholder="输入已知页面 ID"
          style={{ background: "#fff", color: "#1f2328", border: "1px solid #d9d9d6", borderRadius: 4, padding: "4px 6px", fontFamily: "ui-monospace, Consolas, monospace" }}
        />
      </label>
      <ul data-testid="book-list" style={listStyle}>
        {books.map((book) => (
          <li key={book.book_id}>
            <button
              data-testid={`book-tile-${book.book_id}`}
              type="button"
              onClick={() => onSelectBook(book.book_id)}
              style={tileStyle(book.book_id === selectedBookId)}
            >
              {book.title}
              <span style={{ color: "#6b7280", marginLeft: 6 }}>
                ({book.page_count ?? "—"})
              </span>
            </button>
          </li>
        ))}
        {books.length === 0 && (
          <li data-testid="page-list-empty" style={noteStyle}>
            暂无作品
          </li>
        )}
        {booksBusy && <li data-testid="books-busy" style={noteStyle}>正在读取作品…</li>}
        {booksError && <li data-testid="books-error" role="alert" style={{ ...noteStyle, color: "#cf222e" }}>{parseSemanticError(booksError).message} <small>错误代码：{parseSemanticError(booksError).code}</small>{parseSemanticError(booksError).retryable && onRetryBooks && <> <button type="button" onClick={onRetryBooks}>重试</button></>}</li>}
      </ul>
      {selectedBookId && (
        <ul data-testid="chapter-list" style={listStyle}>
          {chapters.map((chapter) => (
            <li key={chapter.chapter_id}>
              <button
                data-testid={`chapter-tile-${chapter.chapter_id}`}
                type="button"
                onClick={() => onSelectChapter(chapter.chapter_id)}
                style={tileStyle(chapter.chapter_id === selectedChapterId)}
              >
                {chapter.chapter_number ? `#${chapter.chapter_number} · ` : ""}
                {chapter.title}
              </button>
            </li>
          ))}
          {chaptersBusy && (
            <li data-testid="chapters-busy" style={noteStyle}>
              正在读取章节…
            </li>
          )}
          {!chaptersBusy && chaptersError && (
            <li data-testid="chapters-error" role="alert" style={{ ...noteStyle, color: "#cf222e" }}>
              {parseSemanticError(chaptersError).message} <small>错误代码：{parseSemanticError(chaptersError).code}</small>{parseSemanticError(chaptersError).retryable && onRetryChapters && <> <button type="button" onClick={onRetryChapters}>重试</button></>}
            </li>
          )}
          {!chaptersBusy && !chaptersError && chapters.length === 0 && (
            <li data-testid="chapter-list-empty" style={noteStyle}>
              暂无章节
            </li>
          )}
        </ul>
      )}
      {selectedChapterId && (
        <ul
          data-testid="page-nav-list"
          style={listStyle}
          onKeyDown={(event) => {
            if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
            const buttons = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>('button[data-testid^="page-tile-"]'));
            const currentIndex = buttons.indexOf(event.currentTarget.ownerDocument.activeElement as HTMLButtonElement);
            if (currentIndex < 0) return;
            const nextIndex = Math.max(0, Math.min(visiblePages.length - 1, currentIndex + (event.key === "ArrowDown" ? 1 : -1)));
            if (nextIndex === currentIndex) return;
            event.preventDefault();
            buttons[nextIndex].focus();
            (onPageSelect ?? onPageIdChange)(visiblePages[nextIndex].page_id, { ctrlKey: false, shiftKey: false });
          }}
        >
          {visiblePages.map((page) => {
            const row = projectedRows.find((item) => item.page_id === page.page_id);
            const selected = page.page_id === pageId.trim();
            const included = selectedPageIds.includes(page.page_id);
            return (
            <li key={page.page_id}>
              <button
                data-testid={`page-tile-${page.page_id}`}
                type="button"
                aria-pressed={included}
                onClick={(event) => (onPageSelect ?? onPageIdChange)(page.page_id, { ctrlKey: event.ctrlKey || event.metaKey, shiftKey: event.shiftKey })}
                style={{ ...tileStyle(selected), outline: included ? "2px solid #4f6bed" : undefined }}
              >
                <span style={{ display: "flex", justifyContent: "space-between", gap: 4 }}>
                  <span>{page.source_filename}</span>
                  <span style={{ color: "#6b7280", fontSize: 10 }}>{row?.status ?? "未处理"}{row?.is_locked ? " · 已锁定" : ""}</span>
                </span>
              </button>
            </li>
            );
          })}
          {pagesBusy && (
            <li data-testid="pages-busy" style={noteStyle}>
              正在读取页面…
            </li>
          )}
          {!pagesBusy && pagesError && (
            <li data-testid="pages-error" role="alert" style={{ ...noteStyle, color: "#cf222e" }}>
              {parseSemanticError(pagesError).message} <small>错误代码：{parseSemanticError(pagesError).code}</small>{parseSemanticError(pagesError).retryable && onRetryPages && <> <button type="button" onClick={onRetryPages}>重试</button></>}
            </li>
          )}
          {!pagesBusy && !pagesError && visiblePages.length === 0 && (
            <li data-testid="page-nav-list-empty" style={noteStyle}>
              {pageFilter ? "此状态下没有页面" : "本章节暂无页面；可使用工具栏导入入口。"}
            </li>
          )}
          {pageFilter && <li><button type="button" onClick={onClearPageFilter}>清除状态筛选</button></li>}
        </ul>
      )}
    </section>
  );
}
