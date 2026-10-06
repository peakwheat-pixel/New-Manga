/**
 * <PageListPanel> — page navigation (M2-UI1 §2.2 mapping: QML
 * `PageListPanel.qml` + `PageTile`). M2-PAGE-NAV-PROJECTION-1: the
 * three-level drill-down book -> chapter -> page over the frozen read-only
 * projections (`library_list_books` + `list_chapters` +
 * `list_chapter_pages`, contract M2-C1 rev 1.8 §5); a page click feeds
 * `onPageIdChange`, which drives the existing resolve -> image chain. The
 * page-id entry stays as the debug fallback. Drill-down data/loading state
 * is owned by <WorkbenchPage>; expand/collapse is local UI state there too
 * (clicking the open book/chapter again collapses it).
 */

import type { BookSummary, ChapterNavSummary, PageNavSummary } from "../library/types";

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
  onPageIdChange: (pageId: string) => void;
  onSelectBook: (bookId: string) => void;
  onSelectChapter: (chapterId: string) => void;
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
    background: selected ? "#1c2430" : "transparent",
    color: "#d8e0e8",
    border: "1px solid #2a3038",
    borderRadius: 4,
    padding: "4px 6px",
    cursor: "pointer",
    fontSize: 12,
  }) as const;

const noteStyle = { color: "#8a94a2", fontSize: 11 } as const;

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
  onSelectBook,
  onSelectChapter,
}: PageListPanelProps) {
  return (
    <section
      data-testid="page-list-panel"
      style={{
        border: "1px solid #2a3038",
        borderRadius: 6,
        padding: 8,
        minWidth: 200,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <h2 style={{ fontSize: 12, margin: 0, color: "#d8e0e8" }}>Pages</h2>
      <label style={{ fontSize: 11, color: "#8a94a2", display: "flex", flexDirection: "column", gap: 2 }}>
        page_id (region read channel)
        <input
          data-testid="page-id-input"
          value={pageId}
          onChange={(event) => onPageIdChange(event.target.value)}
          placeholder="page id…"
          style={{
            background: "#101418",
            color: "#d8e0e8",
            border: "1px solid #2a3038",
            borderRadius: 4,
            padding: "3px 6px",
            fontFamily: "Consolas, monospace",
          }}
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
              <span style={{ color: "#8a94a2", marginLeft: 6 }}>
                ({book.page_count ?? "—"})
              </span>
            </button>
          </li>
        ))}
        {books.length === 0 && (
          <li data-testid="page-list-empty" style={noteStyle}>
            no books
          </li>
        )}
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
              loading chapters…
            </li>
          )}
          {!chaptersBusy && chaptersError && (
            <li data-testid="chapters-error" style={{ ...noteStyle, color: "#e8a0a0" }}>
              {chaptersError}
            </li>
          )}
          {!chaptersBusy && !chaptersError && chapters.length === 0 && (
            <li data-testid="chapter-list-empty" style={noteStyle}>
              no chapters
            </li>
          )}
        </ul>
      )}
      {selectedChapterId && (
        <ul data-testid="page-nav-list" style={listStyle}>
          {pages.map((page) => (
            <li key={page.page_id}>
              <button
                data-testid={`page-tile-${page.page_id}`}
                type="button"
                onClick={() => onPageIdChange(page.page_id)}
                style={tileStyle(page.page_id === pageId.trim())}
              >
                {page.source_filename}
              </button>
            </li>
          ))}
          {pagesBusy && (
            <li data-testid="pages-busy" style={noteStyle}>
              loading pages…
            </li>
          )}
          {!pagesBusy && pagesError && (
            <li data-testid="pages-error" style={{ ...noteStyle, color: "#e8a0a0" }}>
              {pagesError}
            </li>
          )}
          {!pagesBusy && !pagesError && pages.length === 0 && (
            <li data-testid="page-nav-list-empty" style={noteStyle}>
              no pages
            </li>
          )}
        </ul>
      )}
    </section>
  );
}
