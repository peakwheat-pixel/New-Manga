/**
 * <PageListPanel> — first-slice page list (M2-UI1 §2.2 mapping: QML
 * `PageListPanel.qml` + `PageTile`). The production page-level command face
 * (ListChapters/ListPages) is a §5 PROPOSAL, not implemented: this slice
 * consumes the EXISTING `library_list_books` projection only (Task AC2),
 * renders the book rows, and holds the page-id entry that feeds the region
 * read channel. Page-level selection parity is NOT_IN_SCOPE (registered in
 * the Task's deviation list).
 */

import type { BookSummary } from "../library/types";

export interface PageListPanelProps {
  books: BookSummary[];
  selectedBookId: string | null;
  pageId: string;
  onPageIdChange: (pageId: string) => void;
  onSelectBook: (bookId: string) => void;
}

export function PageListPanel({
  books,
  selectedBookId,
  pageId,
  onPageIdChange,
  onSelectBook,
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
      <ul data-testid="book-list" style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 2 }}>
        {books.map((book) => (
          <li key={book.book_id}>
            <button
              data-testid={`book-tile-${book.book_id}`}
              type="button"
              onClick={() => onSelectBook(book.book_id)}
              style={{
                width: "100%",
                textAlign: "left",
                background: book.book_id === selectedBookId ? "#1c2430" : "transparent",
                color: "#d8e0e8",
                border: "1px solid #2a3038",
                borderRadius: 4,
                padding: "4px 6px",
                cursor: "pointer",
                fontSize: 12,
              }}
            >
              {book.title}
              <span style={{ color: "#8a94a2", marginLeft: 6 }}>
                ({book.page_count ?? "—"})
              </span>
            </button>
          </li>
        ))}
        {books.length === 0 && (
          <li data-testid="page-list-empty" style={{ color: "#8a94a2", fontSize: 11 }}>
            no books
          </li>
        )}
      </ul>
    </section>
  );
}
