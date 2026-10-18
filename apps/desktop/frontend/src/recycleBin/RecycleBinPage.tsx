import { useCallback, useEffect, useState } from "react";
import { LibraryClient } from "../library/client";
import type { BookSummary } from "../library/types";
import { tokens } from "../theme/tokens";
import { PermanentDeleteConfirmDialog } from "./PermanentDeleteConfirmDialog";

export interface RecycleBinPageProps {
  client?: LibraryClient;
  totalBooksCount?: number;
  initialBooks?: BookSummary[];
  onClose?: () => void;
  onDeleteSuccess?: (deletedBookIds: string[]) => void;
}

export function RecycleBinPage({
  client,
  totalBooksCount,
  initialBooks,
  onClose,
  onDeleteSuccess,
}: RecycleBinPageProps) {
  const [activeClient] = useState(() => client || new LibraryClient());
  const [books, setBooks] = useState<BookSummary[]>(initialBooks || []);
  const [loading, setLoading] = useState<boolean>(!initialBooks);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [batchError, setBatchError] = useState<string | null>(null);

  // Frozen snapshot passed to the confirmation dialog
  const [confirmTargets, setConfirmTargets] = useState<BookSummary[] | null>(null);

  const fetchRecycleBooks = useCallback(async () => {
    setLoading(true);
    try {
      const allBooks = await activeClient.listBooks();
      setBooks(allBooks);
    } catch {
      // Fail-soft
      setBooks([]);
    } finally {
      setLoading(false);
    }
  }, [activeClient]);

  useEffect(() => {
    if (!initialBooks) {
      void fetchRecycleBooks();
    }
  }, [fetchRecycleBooks, initialBooks]);

  const handleToggleSelect = (bookId: string) => {
    setBatchError(null);
    setSelectedIds((prev) =>
      prev.includes(bookId) ? prev.filter((id) => id !== bookId) : [...prev, bookId],
    );
  };

  const handleToggleSelectAll = () => {
    setBatchError(null);
    if (selectedIds.length === books.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(books.map((b) => b.book_id));
    }
  };

  const handleOpenPermanentDelete = () => {
    setBatchError(null);
    if (selectedIds.length === 0) return;

    // AC5 Rule 5: Batch limit 20
    if (selectedIds.length > 20) {
      setBatchError(
        `批量删除上限为 20 本，当前已选择 ${selectedIds.length} 本，请减少选择后再试。`,
      );
      return;
    }

    // AC5 Rule 5: Whole library deletion blocked
    const effectiveTotal =
      typeof totalBooksCount === "number" ? totalBooksCount : books.length;
    if (effectiveTotal > 0 && selectedIds.length === effectiveTotal) {
      setBatchError("不能单次批量清空整库，请保留至少一部作品或分批处理。");
      return;
    }

    // Freeze snapshot from the currently selected books in precise order
    const snapshot = selectedIds
      .map((id) => books.find((b) => b.book_id === id))
      .filter((b): b is BookSummary => b !== undefined);

    setConfirmTargets(snapshot);
  };

  const handleExecutePermanentDelete = async () => {
    if (!confirmTargets || confirmTargets.length === 0) return;

    // AC5 Rule 3: Assemble payload strictly from the SAME frozen snapshot
    const book_ids = confirmTargets.map((b) => b.book_id);
    const confirmed_book_ids = [...book_ids]; // Same order guaranteed
    const confirm_count = book_ids.length;

    if (book_ids.length === 1) {
      await activeClient.deleteBookPermanently({
        book_id: book_ids[0],
        confirm_permanent_delete: true,
      });
    } else {
      await activeClient.deleteBooksPermanently({
        book_ids,
        confirmed_book_ids,
        confirm_count,
        confirm_permanent_delete: true,
      });
    }

    // On success: remove deleted books and clear selection
    setBooks((prev) => prev.filter((b) => !book_ids.includes(b.book_id)));
    setSelectedIds((prev) => prev.filter((id) => !book_ids.includes(id)));
    setConfirmTargets(null);
    onDeleteSuccess?.(book_ids);
  };

  return (
    <div
      data-testid="recycle-bin-page"
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        backgroundColor: tokens.color.bg.app,
        boxSizing: "border-box",
        overflow: "hidden",
      }}
    >
      {/* Header Toolbar */}
      <header
        data-testid="recycle-bin-toolbar"
        style={{
          height: 48,
          padding: "0 16px",
          backgroundColor: tokens.color.bg.toolbar,
          borderBottom: `1px solid ${tokens.color.border.default}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 18 }}>🗑️</span>
          <h2
            data-testid="recycle-bin-title"
            style={{
              margin: 0,
              fontSize: 16,
              fontWeight: 600,
              color: tokens.color.text.primary,
            }}
          >
            回收站
          </h2>
          <span
            data-testid="recycle-bin-count"
            style={{
              fontSize: 13,
              color: tokens.color.text.muted,
            }}
          >
            ({books.length} 部作品)
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {/* Permanent delete entry point - ONLY exists in Recycle Bin */}
          <button
            type="button"
            data-testid="recycle-bin-permanent-delete-btn"
            onClick={handleOpenPermanentDelete}
            disabled={selectedIds.length === 0}
            style={{
              height: 30,
              padding: "0 14px",
              fontSize: 13,
              fontWeight: 500,
              backgroundColor: selectedIds.length > 0 ? "#c62828" : tokens.color.surface.card,
              color: selectedIds.length > 0 ? "#ffffff" : tokens.color.text.muted,
              border: `1px solid ${selectedIds.length > 0 ? "#b71c1c" : tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              cursor: selectedIds.length > 0 ? "pointer" : "not-allowed",
              transition: "background-color 0.15s ease",
            }}
          >
            永久删除{selectedIds.length > 0 ? ` (${selectedIds.length})` : ""}
          </button>

          {onClose && (
            <button
              type="button"
              data-testid="recycle-bin-close-btn"
              onClick={onClose}
              style={{
                height: 30,
                padding: "0 12px",
                fontSize: 13,
                backgroundColor: tokens.color.surface.card,
                color: tokens.color.text.secondary,
                border: `1px solid ${tokens.color.border.default}`,
                borderRadius: tokens.radius.button,
                cursor: "pointer",
              }}
            >
              返回
            </button>
          )}
        </div>
      </header>

      {/* Batch or Whole-library validation errors */}
      {batchError && (
        <div
          data-testid={
            batchError.includes("20")
              ? "recycle-bin-batch-limit-error"
              : "recycle-bin-whole-library-error"
          }
          style={{
            padding: "8px 16px",
            backgroundColor: "rgba(255, 107, 107, 0.15)",
            borderBottom: "1px solid rgba(255, 107, 107, 0.3)",
            color: "#ff6b6b",
            fontSize: 13,
            fontWeight: 500,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <span>⚠️ {batchError}</span>
          <button
            type="button"
            data-testid="dismiss-batch-error-btn"
            onClick={() => setBatchError(null)}
            style={{
              background: "none",
              border: "none",
              color: "#ff6b6b",
              cursor: "pointer",
              fontSize: 14,
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Main List */}
      <main
        data-testid="recycle-bin-content"
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "16px",
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        {loading && (
          <div data-testid="recycle-bin-loading" style={{ color: tokens.color.text.muted, padding: 20 }}>
            正在加载回收站...
          </div>
        )}

        {!loading && books.length === 0 && (
          <div
            data-testid="recycle-bin-empty"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: 60,
              color: tokens.color.text.muted,
            }}
          >
            <div style={{ fontSize: 40, marginBottom: 12 }}>🗑️</div>
            <div style={{ fontSize: 16, fontWeight: 500 }}>回收站为空</div>
            <div style={{ fontSize: 13, marginTop: 4 }}>暂无待清理的作品</div>
          </div>
        )}

        {!loading && books.length > 0 && (
          <>
            {/* Table Header / Select All */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                padding: "8px 12px",
                backgroundColor: tokens.color.bg.toolbar,
                borderRadius: tokens.radius.button,
                fontSize: 12,
                fontWeight: 600,
                color: tokens.color.text.secondary,
                border: `1px solid ${tokens.color.border.default}`,
              }}
            >
              <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", width: 60 }}>
                <input
                  type="checkbox"
                  data-testid="recycle-select-all-checkbox"
                  checked={selectedIds.length === books.length && books.length > 0}
                  onChange={handleToggleSelectAll}
                  style={{ width: 15, height: 15, cursor: "pointer" }}
                />
                <span>全选</span>
              </label>
              <div style={{ flex: 2 }}>作品标题</div>
              <div style={{ flex: 1 }}>原名</div>
              <div style={{ width: 80, textAlign: "right" }}>页数</div>
            </div>

            {/* Book Rows */}
            {books.map((book) => {
              const selected = selectedIds.includes(book.book_id);
              return (
                <div
                  key={book.book_id}
                  data-testid={`recycle-item-${book.book_id}`}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "10px 12px",
                    backgroundColor: selected ? tokens.color.accent.selected : tokens.color.surface.card,
                    borderRadius: tokens.radius.button,
                    border: `1px solid ${selected ? tokens.color.accent.primary : tokens.color.border.default}`,
                    fontSize: 13,
                    transition: "all 0.12s ease",
                  }}
                >
                  <div style={{ width: 60, display: "flex", alignItems: "center" }}>
                    <input
                      type="checkbox"
                      data-testid={`recycle-item-checkbox-${book.book_id}`}
                      checked={selected}
                      onChange={() => handleToggleSelect(book.book_id)}
                      style={{ width: 16, height: 16, cursor: "pointer" }}
                    />
                  </div>
                  <div
                    style={{
                      flex: 2,
                      fontWeight: 500,
                      color: tokens.color.text.primary,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {book.title}
                  </div>
                  <div
                    style={{
                      flex: 1,
                      color: tokens.color.text.secondary,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {book.original_title || "—"}
                  </div>
                  <div style={{ width: 80, textAlign: "right", color: tokens.color.text.muted }}>
                    {book.page_count !== null ? `${book.page_count} 页` : "—"}
                  </div>
                </div>
              );
            })}
          </>
        )}
      </main>

      {/* Second Confirmation Dialog (AC5) */}
      {confirmTargets && (
        <PermanentDeleteConfirmDialog
          targets={confirmTargets}
          onClose={() => setConfirmTargets(null)}
          onConfirm={handleExecutePermanentDelete}
        />
      )}
    </div>
  );
}
