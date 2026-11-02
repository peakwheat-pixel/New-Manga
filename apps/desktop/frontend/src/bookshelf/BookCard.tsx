import type { BookSummary } from "../library/types";
import { tokens } from "../theme/tokens";

export interface BookCardProps {
  book: BookSummary;
  isSelected?: boolean;
  onSelect: (bookId: string) => void;
}

export function BookCard({ book, isSelected = false, onSelect }: BookCardProps) {
  // W1 CRITICAL: page_count=null 必须渲染为「—」，绝对不能渲染为 0
  const pageCountText = book.page_count === null ? "—" : `${book.page_count} 页`;

  return (
    <div
      role="button"
      tabIndex={0}
      data-testid={`book-card-${book.book_id}`}
      data-selected={isSelected}
      onClick={() => onSelect(book.book_id)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(book.book_id);
        }
      }}
      style={{
        width: tokens.dimensions.cardGridWidth,
        height: tokens.dimensions.cardGridHeight,
        boxSizing: "border-box",
        backgroundColor: isSelected ? tokens.color.accent.selected : tokens.color.surface.card,
        border: `1px solid ${isSelected ? tokens.color.accent.primary : tokens.color.surface.border}`,
        borderRadius: tokens.radius.card,
        padding: tokens.spacing.sm,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        cursor: "pointer",
        transition: "border-color 0.15s ease, background-color 0.15s ease",
        outline: "none",
        position: "relative",
      }}
    >
      {/* Top badges: Favorite & Archived */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        {book.is_favorite ? (
          <span
            data-testid={`book-favorite-badge-${book.book_id}`}
            title="收藏（等待能力接入 GAP-G3）"
            style={{
              color: tokens.color.state.favorite,
              fontSize: 14,
              lineHeight: 1,
            }}
          >
            ★
          </span>
        ) : (
          <span
            data-testid={`book-favorite-placeholder-${book.book_id}`}
            title="收藏切换（等待能力接入 GAP-G3）"
            style={{
              color: tokens.color.text.muted,
              fontSize: 14,
              lineHeight: 1,
              opacity: 0.4,
            }}
          >
            ☆
          </span>
        )}

        {book.is_archived && (
          <span
            data-testid={`book-archived-badge-${book.book_id}`}
            title="已归档"
            style={{
              fontSize: tokens.typography.size.badge,
              color: tokens.color.state.archived,
              border: `1px solid ${tokens.color.state.archived}`,
              borderRadius: tokens.radius.pill,
              padding: "1px 5px",
              lineHeight: 1.2,
            }}
          >
            归档
          </span>
        )}
      </div>

      {/* Middle: Title & Original title */}
      <div style={{ flex: 1, marginTop: tokens.spacing.sm, overflow: "hidden" }}>
        <h3
          data-testid={`book-title-${book.book_id}`}
          style={{
            margin: 0,
            fontSize: tokens.typography.size.cardTitle,
            fontWeight: 600,
            color: tokens.color.text.primary,
            overflow: "hidden",
            textOverflow: "ellipsis",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            lineHeight: 1.3,
          }}
        >
          {book.title}
        </h3>

        {book.original_title && (
          <div
            data-testid={`book-original-title-${book.book_id}`}
            style={{
              marginTop: 4,
              fontSize: tokens.typography.size.secondary,
              color: tokens.color.text.secondary,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {book.original_title}
          </div>
        )}
      </div>

      {/* Bottom: Page count */}
      <div
        style={{
          borderTop: `1px solid ${tokens.color.border.divider}`,
          paddingTop: tokens.spacing.xs,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: tokens.typography.size.secondary,
          color: tokens.color.text.secondary,
        }}
      >
        <span>页数</span>
        <span
          data-testid={`book-page-count-${book.book_id}`}
          style={{
            fontWeight: 600,
            fontVariantNumeric: "tabular-nums",
            color: book.page_count === null ? tokens.color.text.muted : tokens.color.text.primary,
          }}
        >
          {pageCountText}
        </span>
      </div>
    </div>
  );
}
