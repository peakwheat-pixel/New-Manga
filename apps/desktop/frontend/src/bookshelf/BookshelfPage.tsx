import { useCallback, useEffect, useMemo, useState } from "react";
import { LibraryClient } from "../library/client";
import type { BookSummary, ChapterNavSummary, ImportSummary } from "../library/types";
import { BookDetailPanel } from "./BookDetailPanel";
import { BookGrid } from "./BookGrid";
import { BookList } from "./BookList";
import { BookshelfToolbar } from "./BookshelfToolbar";
import { EmptyStateBookshelf } from "./EmptyStateBookshelf";
import { ImportDialog } from "./ImportDialog";
import { CreateTitleDialog } from "./CreateTitleDialog";
import { RecycleBinPage } from "../recycleBin/RecycleBinPage";
import { parseSemanticError, type SemanticErrorInfo } from "./error";
import type { BookshelfFilterState } from "./types";
import { tokens } from "../theme/tokens";

export interface BookshelfPageProps {
  client?: LibraryClient;
  onEnterWorkbench?: (bookId: string, chapterId: string) => void;
  onEnterReader?: (bookId: string, chapterId: string) => void;
  initialBooks?: BookSummary[];
}

export function BookshelfPage({
  client,
  onEnterWorkbench,
  onEnterReader,
  initialBooks,
}: BookshelfPageProps) {
  const activeClient = useMemo(() => client || new LibraryClient(), [client]);

  const [loading, setLoading] = useState<boolean>(!initialBooks);
  const [books, setBooks] = useState<BookSummary[]>(initialBooks || []);
  const [errorInfo, setErrorInfo] = useState<SemanticErrorInfo | null>(null);

  // Selected book and its chapters
  const [selectedBookId, setSelectedBookId] = useState<string | null>(
    initialBooks && initialBooks.length > 0 ? initialBooks[0].book_id : null,
  );
  const [chapters, setChapters] = useState<ChapterNavSummary[]>([]);
  const [loadingChapters, setLoadingChapters] = useState(false);
  const [chapterPageCounts, setChapterPageCounts] = useState<Record<string, number>>({});

  // UI-local filters & view mode (M2-C1 §5.2)
  const [filter, setFilter] = useState<BookshelfFilterState>({
    search: "",
    favoriteOnly: false,
    archivedOnly: false,
    sortBy: "updated_at",
    viewMode: "grid",
  });

  // Import dialog state
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importTargetChapterId, setImportTargetChapterId] = useState<string | null>(null);
  const [createEntity, setCreateEntity] = useState<"book" | "chapter" | null>(null);
  const [recycleBinOpen, setRecycleBinOpen] = useState(false);

  const fetchBooks = useCallback(async () => {
    setLoading(true);
    setErrorInfo(null);
    try {
      const rawList = await activeClient.listBooks();
      const list = Array.isArray(rawList) ? rawList : [];
      setBooks(list);
      // Auto-select first book if nothing selected
      setSelectedBookId((current) => {
        if (current && list.some((b) => b.book_id === current)) return current;
        return list.length > 0 ? list[0].book_id : null;
      });
    } catch (err) {
      setErrorInfo(parseSemanticError(err));
    } finally {
      setLoading(false);
    }
  }, [activeClient]);

  useEffect(() => {
    if (!initialBooks) {
      void fetchBooks();
    }
  }, [fetchBooks, initialBooks]);

  // When selected book changes, load its chapters
  const fetchChaptersForBook = useCallback(
    async (bookId: string) => {
      setLoadingChapters(true);
      try {
        const chapterList = await activeClient.listChapters(bookId);
        setChapters(chapterList);

        // Fetch page counts for all chapters asynchronously
        const counts: Record<string, number> = {};
        await Promise.all(
          chapterList.map(async (ch) => {
            try {
              const pages = await activeClient.listChapterPages(ch.chapter_id);
              counts[ch.chapter_id] = pages.length;
            } catch {
              counts[ch.chapter_id] = 0;
            }
          }),
        );
        setChapterPageCounts(counts);
      } catch (err) {
        // Chapters fail-soft: keep empty list, don't break whole page
        setChapters([]);
        setChapterPageCounts({});
      } finally {
        setLoadingChapters(false);
      }
    },
    [activeClient],
  );

  useEffect(() => {
    if (selectedBookId) {
      void fetchChaptersForBook(selectedBookId);
    } else {
      setChapters([]);
      setChapterPageCounts({});
    }
  }, [selectedBookId, fetchChaptersForBook]);

  const handleFilterChange = (update: Partial<BookshelfFilterState>) => {
    setFilter((prev) => ({ ...prev, ...update }));
  };

  const handleOpenImport = (chapterId?: string | null) => {
    setImportTargetChapterId(chapterId || null);
    setImportDialogOpen(true);
  };

  const handleImportSuccess = (_chapterId: string, _summary: ImportSummary) => {
    // Refresh books and chapter list
    void fetchBooks();
    if (selectedBookId) {
      void fetchChaptersForBook(selectedBookId);
    }
  };

  const handleCreateTitle = async (title: string) => {
    if (createEntity === "book") {
      try {
        const created = await activeClient.createBook(title);
        setBooks((current) => [...current, created]);
        setSelectedBookId(created.book_id);
      } catch (error) {
        await fetchBooks();
        throw error;
      }
      return;
    }

    if (createEntity === "chapter" && selectedBookId) {
      const bookId = selectedBookId;
      try {
        const created = await activeClient.createChapter(bookId, title);
        setChapters((current) => [...current, created].sort((a, b) => a.sort_order - b.sort_order));
        setChapterPageCounts((current) => ({ ...current, [created.chapter_id]: 0 }));
      } catch (error) {
        await fetchChaptersForBook(bookId);
        throw error;
      }
    }
  };

  // Filter and sort books in-memory (UI-local)
  const filteredBooks = useMemo(() => {
    let result = [...books];

    if (filter.search.trim()) {
      const q = filter.search.toLowerCase().trim();
      result = result.filter(
        (b) =>
          b.title.toLowerCase().includes(q) ||
          (b.original_title && b.original_title.toLowerCase().includes(q)),
      );
    }

    if (filter.favoriteOnly) {
      result = result.filter((b) => b.is_favorite);
    }

    if (filter.archivedOnly) {
      result = result.filter((b) => b.is_archived);
    }

    result.sort((a, b) => {
      if (filter.sortBy === "title") {
        return a.title.localeCompare(b.title);
      }
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    });

    return result;
  }, [books, filter]);

  const selectedBook = useMemo(
    () => books.find((b) => b.book_id === selectedBookId) || null,
    [books, selectedBookId],
  );

  return (
    <div
      data-testid="bookshelf-page"
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        boxSizing: "border-box",
        backgroundColor: tokens.color.bg.app,
        overflow: "hidden",
      }}
    >
      {/* 1. Global Toolbar */}
      <BookshelfToolbar
        filter={filter}
        onFilterChange={handleFilterChange}
        onCreateBook={() => setCreateEntity("book")}
        onOpenImport={() => handleOpenImport(null)}
        onOpenRecycleBin={() => setRecycleBinOpen(true)}
      />

      {/* 2. Main content area: Book content on the left, BookDetailPanel on the right */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Books display area (Grid or List) */}
        <main
          data-testid="bookshelf-main-content"
          style={{
            flex: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* Loading state: skeleton */}
          {loading && (
            <div
              data-testid="bookshelf-loading-skeleton"
              style={{
                display: "grid",
                gridTemplateColumns: `repeat(auto-fill, minmax(${tokens.dimensions.cardGridWidth}px, ${tokens.dimensions.cardGridWidth}px))`,
                gap: tokens.spacing.sm,
                padding: tokens.spacing.md,
              }}
            >
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div
                  key={i}
                  style={{
                    width: tokens.dimensions.cardGridWidth,
                    height: tokens.dimensions.cardGridHeight,
                    backgroundColor: tokens.color.surface.card,
                    border: `1px solid ${tokens.color.surface.border}`,
                    borderRadius: tokens.radius.card,
                    opacity: 0.5,
                  }}
                />
              ))}
            </div>
          )}

          {/* Error state (W28 semantic ErrorEnvelope card) */}
          {!loading && errorInfo && (
            <div
              data-testid="bookshelf-error-card"
              style={{
                margin: tokens.spacing.lg,
                padding: tokens.spacing.lg,
                backgroundColor: tokens.color.surface.card,
                border: `1px solid ${tokens.color.state.failed}`,
                borderRadius: tokens.radius.card,
                maxWidth: 520,
              }}
            >
              <div
                style={{
                  fontSize: tokens.typography.size.panelTitle,
                  fontWeight: 600,
                  color: tokens.color.state.failed,
                  marginBottom: tokens.spacing.xs,
                }}
              >
                {errorInfo.title}
              </div>
              <div
                style={{
                  fontSize: tokens.typography.size.base,
                  color: tokens.color.text.secondary,
                  marginBottom: tokens.spacing.md,
                }}
              >
                {errorInfo.message}
              </div>
              <div
                style={{
                  fontSize: tokens.typography.size.secondary,
                  fontFamily: tokens.typography.monospace,
                  color: tokens.color.text.muted,
                  marginBottom: tokens.spacing.md,
                }}
              >
                错误代码：{errorInfo.code}
              </div>
              {errorInfo.retryable && (
                <button
                  type="button"
                  data-testid="bookshelf-retry-btn"
                  onClick={() => void fetchBooks()}
                  style={{
                    padding: "6px 16px",
                    backgroundColor: tokens.color.accent.primary,
                    color: tokens.color.text.inverse,
                    border: "none",
                    borderRadius: tokens.radius.button,
                    fontSize: tokens.typography.size.base,
                    cursor: "pointer",
                  }}
                >
                  重试
                </button>
              )}
            </div>
          )}

          {/* Empty state: empty library or filtered empty */}
          {!loading && !errorInfo && books.length === 0 && (
            <EmptyStateBookshelf
              isFiltered={false}
              onCreateBook={() => setCreateEntity("book")}
              onOpenImport={() => handleOpenImport(null)}
            />
          )}

          {!loading && !errorInfo && books.length > 0 && filteredBooks.length === 0 && (
            <EmptyStateBookshelf
              isFiltered={true}
              onClearFilter={() =>
                setFilter((prev) => ({
                  ...prev,
                  search: "",
                  favoriteOnly: false,
                  archivedOnly: false,
                }))
              }
            />
          )}

          {/* Success state: Grid or List */}
          {!loading && !errorInfo && filteredBooks.length > 0 && (
            <div style={{ flex: 1, padding: tokens.spacing.sm }}>
              {filter.viewMode === "grid" ? (
                <BookGrid
                  books={filteredBooks}
                  selectedBookId={selectedBookId}
                  onSelect={setSelectedBookId}
                />
              ) : (
                <BookList
                  books={filteredBooks}
                  selectedBookId={selectedBookId}
                  onSelect={setSelectedBookId}
                />
              )}
            </div>
          )}
        </main>

        {/* 3. Fixed right BookDetailPanel (320px) */}
        <BookDetailPanel
          book={selectedBook}
          chapters={chapters}
          chapterPageCounts={chapterPageCounts}
          loadingChapters={loadingChapters}
          onEnterWorkbench={onEnterWorkbench}
          onEnterReader={onEnterReader}
          onOpenImport={handleOpenImport}
          onCreateChapter={selectedBook ? () => setCreateEntity("chapter") : undefined}
        />
      </div>

      {createEntity && (
        <CreateTitleDialog
          key={createEntity}
          entity={createEntity === "book" ? "作品" : "章节"}
          onClose={() => setCreateEntity(null)}
          onSubmit={handleCreateTitle}
        />
      )}

      {/* 4. Import Dialog Modal (W30 / W4) */}
      <ImportDialog
        isOpen={importDialogOpen}
        books={books}
        chapters={chapters}
        initialBookId={selectedBookId}
        initialChapterId={importTargetChapterId}
        client={activeClient}
        onClose={() => setImportDialogOpen(false)}
        onImportSuccess={handleImportSuccess}
      />

      {/* 5. Recycle Bin Modal (AC5: Permanent Delete entry point ONLY in Recycle Bin) */}
      {recycleBinOpen && (
        <div
          data-testid="recycle-bin-modal-overlay"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.7)",
            zIndex: 1500,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 40,
            boxSizing: "border-box",
          }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: 900,
              height: "100%",
              maxHeight: 650,
              borderRadius: tokens.radius.card,
              overflow: "hidden",
              boxShadow: "0 12px 32px rgba(0, 0, 0, 0.5)",
              border: `1px solid ${tokens.color.border.default}`,
            }}
          >
            <RecycleBinPage
              client={activeClient}
              totalBooksCount={books.length}
              onClose={() => setRecycleBinOpen(false)}
              onDeleteSuccess={() => {
                void fetchBooks();
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

