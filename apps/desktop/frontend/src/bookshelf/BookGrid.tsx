import type { BookSummary } from "../library/types";
import { BookCard } from "./BookCard";
import { tokens } from "../theme/tokens";

export interface BookGridProps {
  books: BookSummary[];
  selectedBookId: string | null;
  onSelect: (bookId: string) => void;
}

export function BookGrid({ books, selectedBookId, onSelect }: BookGridProps) {
  return (
    <div
      data-testid="book-grid-container"
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(auto-fill, minmax(${tokens.dimensions.cardGridWidth}px, ${tokens.dimensions.cardGridWidth}px))`,
        gap: tokens.spacing.sm,
        padding: tokens.spacing.sm,
        alignContent: "start",
      }}
    >
      {books.map((book) => (
        <BookCard
          key={book.book_id}
          book={book}
          isSelected={selectedBookId === book.book_id}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
