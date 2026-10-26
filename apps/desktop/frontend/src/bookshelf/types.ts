import type { BookSummary, ChapterNavSummary } from "../library/types";

export type BookshelfViewMode = "grid" | "list";

export type BookshelfSortField = "title" | "updated_at";

export interface BookshelfFilterState {
  search: string;
  favoriteOnly: boolean;
  archivedOnly: boolean;
  sortBy: BookshelfSortField;
  viewMode: BookshelfViewMode;
}

export type DuplicatePolicy = "skip" | "import_as_new";

export interface BookshelfNavigationCallbacks {
  onEnterWorkbench?: (bookId: string, chapterId: string) => void;
  onEnterReader?: (bookId: string, chapterId: string) => void;
}

export interface BookWithChapters {
  book: BookSummary;
  chapters: ChapterNavSummary[];
  chapterPageCounts: Record<string, number>;
}
