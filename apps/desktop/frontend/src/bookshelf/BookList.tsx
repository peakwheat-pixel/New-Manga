import type { BookSummary } from "../library/types";
import { tokens } from "../theme/tokens";

export interface BookListProps {
  books: BookSummary[];
  selectedBookId: string | null;
  onSelect: (bookId: string) => void;
}

export function BookList({ books, selectedBookId, onSelect }: BookListProps) {
  return (
    <div
      data-testid="book-list-container"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 2,
        width: "100%",
      }}
    >
      {/* Header row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "32px 1fr 1fr 100px",
          height: 28,
          alignItems: "center",
          fontSize: tokens.typography.size.secondary,
          color: tokens.color.text.secondary,
          borderBottom: `1px solid ${tokens.color.border.divider}`,
          padding: `0 ${tokens.spacing.sm}px`,
          fontWeight: 600,
        }}
      >
        <span>★</span>
        <span>标题</span>
        <span>原名</span>
        <span style={{ textAlign: "right" }}>页数</span>
      </div>

      {/* Rows */}
      {books.map((book) => {
        const isSelected = selectedBookId === book.book_id;
        const pageCountText = book.page_count === null ? "—" : `${book.page_count} 页`;

        return (
          <div
            key={book.book_id}
            role="button"
            tabIndex={0}
            data-testid={`book-row-${book.book_id}`}
            data-selected={isSelected}
            onClick={() => onSelect(book.book_id)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onSelect(book.book_id);
              }
            }}
            style={{
              display: "grid",
              gridTemplateColumns: "32px 1fr 1fr 100px",
              height: tokens.dimensions.chapterRowHeight,
              alignItems: "center",
              fontSize: tokens.typography.size.base,
              backgroundColor: isSelected ? tokens.color.accent.selected : "transparent",
              color: tokens.color.text.primary,
              borderRadius: tokens.radius.button,
              padding: `0 ${tokens.spacing.sm}px`,
              cursor: "pointer",
              transition: "background-color 0.1s ease",
              outline: "none",
            }}
          >
            <span
              style={{
                color: book.is_favorite ? tokens.color.state.favorite : tokens.color.text.muted,
                opacity: book.is_favorite ? 1 : 0.3,
              }}
            >
              ★
            </span>
            <span
              style={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                fontWeight: isSelected ? 600 : 400,
              }}
            >
              {book.title}
              {book.is_archived && (
                <span
                  style={{
                    marginLeft: 6,
                    fontSize: tokens.typography.size.badge,
                    color: tokens.color.state.archived,
                    border: `1px solid ${tokens.color.state.archived}`,
                    borderRadius: tokens.radius.pill,
                    padding: "1px 4px",
                  }}
                >
                  归档
                </span>
              )}
            </span>
            <span
              style={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                color: tokens.color.text.secondary,
                fontSize: tokens.typography.size.secondary,
              }}
            >
              {book.original_title || "—"}
            </span>
            <span
              data-testid={`book-row-page-count-${book.book_id}`}
              style={{
                textAlign: "right",
                fontVariantNumeric: "tabular-nums",
                color: book.page_count === null ? tokens.color.text.muted : tokens.color.text.primary,
              }}
            >
              {pageCountText}
            </span>
          </div>
        );
      })}
    </div>
  );
}
