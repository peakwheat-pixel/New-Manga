import { useCallback, useEffect, useState } from "react";
import { LibraryClient, LibraryClientError } from "../library/client";
import type { BookSummary } from "../library/types";
import { tokens } from "../theme/tokens";
import { PermanentDeleteConfirmDialog } from "../recycleBin/PermanentDeleteConfirmDialog";

/**
 * SETTINGS-OPEN-C-1-RECYCLE — the recycle-bin operation surface (design
 * doc/design/SETTINGS_SECTION_C_SCHEMAS.md §2, decisions D1/D2/D11).
 *
 * Not a settings form: there is no `settings_update_section` path for
 * `recycle_bin`. The panel only exposes real actions backed by the existing
 * Core wire:
 * - view: `library_list_recycle_bin_books` (the same projection the bookshelf
 *   recycle bin uses — no new `deleted_at` field, decision D2);
 * - clear: `library_delete_books_permanently`, batched at the frozen 20-book
 *   Core limit, each batch carrying the exact confirmation tuple. The whole
 *   library protection (`BOOK_DELETE_BATCH_WHOLE_LIBRARY`) is surfaced
 *   verbatim, never bypassed.
 *
 * The retention policy (`auto_cleanup_days`) is deliberately NOT exposed:
 * no scheduler consumes it, so a control here would be a fake control.
 */

const BATCH_LIMIT = 20;

/** Narrow client face so tests can inject a fake without Tauri. */
export interface RecycleBinClientLike {
  listRecycleBinBooks(): Promise<BookSummary[]>;
  deleteBooksPermanently(payload: {
    book_ids: string[];
    confirmed_book_ids: string[];
    confirm_count: number;
    confirm_permanent_delete: true;
  }): Promise<unknown>;
}

function mapLoadError(error: unknown): string {
  const code =
    error instanceof LibraryClientError ? error.code : "CORE_UNAVAILABLE";
  return `回收站读取失败（${code}）：无法确认软删除作品列表，请勿据此判断作品已被清空，稍后重试。`;
}

function mapClearError(error: unknown): string {
  if (error instanceof LibraryClientError) {
    switch (error.code) {
      case "BOOK_DELETE_BATCH_WHOLE_LIBRARY":
        // Decision D1/§2.3: never bypass the whole-library guard.
        return "不能删除整个书库：回收站包含全部作品，请保留至少一部作品。";
      case "BOOK_DELETE_BATCH_PREFLIGHT_FAILED":
        return "有任务或导出正在进行，稍后再试；本次没有删除任何作品。";
      case "BOOK_NOT_FOUND":
        return "部分作品已不存在，请刷新后重试。";
      case "BOOK_DELETE_BATCH_LIMIT_EXCEEDED":
        return "单批上限 20 本（客户端已分批），请重试。";
      default:
        return `清空失败（${error.code}），请稍后重试。`;
    }
  }
  return "清空失败，请稍后重试。";
}

export interface RecycleBinSettingsPanelProps {
  client?: RecycleBinClientLike;
}

export function RecycleBinSettingsPanel({ client }: RecycleBinSettingsPanelProps) {
  const [activeClient] = useState<RecycleBinClientLike>(
    () => client ?? new LibraryClient(),
  );
  const [books, setBooks] = useState<BookSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState<boolean>(false);
  const [clearing, setClearing] = useState<boolean>(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const rows = await activeClient.listRecycleBinBooks();
      setBooks(rows);
      setLoadError(null);
    } catch (error) {
      setBooks([]);
      setLoadError(mapLoadError(error));
    } finally {
      setLoading(false);
    }
  }, [activeClient]);

  useEffect(() => {
    void load();
  }, [load]);

  /**
   * Clear the whole bin in ≤20-book batches. Each batch is a self-consistent
   * confirmation tuple (D1): the Core validates `confirmed_book_ids` equals
   * `book_ids` and `confirm_count` matches, so a partially-applied clear can
   * never masquerade as a full one.
   */
  const handleConfirmClear = useCallback(async () => {
    setActionError(null);
    setNotice(null);
    setClearing(true);
    const ids = books.map((book) => book.book_id);
    try {
      for (let offset = 0; offset < ids.length; offset += BATCH_LIMIT) {
        const batch = ids.slice(offset, offset + BATCH_LIMIT);
        await activeClient.deleteBooksPermanently({
          book_ids: batch,
          confirmed_book_ids: [...batch],
          confirm_count: batch.length,
          confirm_permanent_delete: true,
        });
      }
      setNotice(`已永久删除 ${ids.length} 部作品。`);
    } catch (error) {
      // The dialog renders this message and stays open so the user can retry
      // or cancel; the list below is re-read on close.
      throw new Error(mapClearError(error));
    } finally {
      setClearing(false);
    }
  }, [activeClient, books]);

  const closeConfirm = useCallback(() => {
    setConfirmOpen(false);
    void load();
  }, [load]);

  return (
    <section
      data-testid="recycle-bin-settings-panel"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: tokens.spacing.lg,
        maxWidth: 780,
      }}
    >
      <header style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
        <h2 style={{ margin: 0, fontSize: tokens.typography.size.panelTitle, color: tokens.color.text.primary }}>
          回收站
        </h2>
        <p
          data-testid="recycle-bin-settings-description"
          style={{ margin: 0, color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}
        >
          查看已软删除的作品，并在确认后永久清空。永久删除不可恢复。
        </p>
      </header>

      {loading && (
        <div data-testid="recycle-bin-settings-loading" style={{ color: tokens.color.text.muted }}>
          正在读取回收站…
        </div>
      )}

      {!loading && loadError && (
        <div
          data-testid="recycle-bin-settings-load-error"
          style={{
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.card,
            padding: tokens.spacing.md,
            color: "#ff9999",
            backgroundColor: "rgba(255, 107, 107, 0.08)",
            fontSize: tokens.typography.size.secondary,
            lineHeight: tokens.typography.lineHeight,
            display: "flex",
            flexDirection: "column",
            gap: tokens.spacing.sm,
          }}
        >
          <span>{loadError}</span>
          <button
            type="button"
            data-testid="recycle-bin-settings-retry-btn"
            onClick={() => void load()}
            style={{ alignSelf: "flex-start" }}
          >
            重试
          </button>
        </div>
      )}

      {!loading && !loadError && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: tokens.spacing.md,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.card,
            padding: tokens.spacing.md,
            backgroundColor: tokens.color.surface.card,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.md }}>
            <span
              data-testid="recycle-bin-settings-summary"
              style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.primary }}
            >
              回收站：{books.length} 部作品
            </span>
            <button
              type="button"
              data-testid="recycle-bin-settings-refresh-btn"
              onClick={() => void load()}
              disabled={clearing}
            >
              刷新
            </button>
            <button
              type="button"
              data-testid="recycle-bin-settings-clear-btn"
              onClick={() => setConfirmOpen(true)}
              disabled={clearing || books.length === 0}
              title="永久删除回收站中的全部作品（不可恢复）"
            >
              清空回收站
            </button>
          </div>

          {notice && (
            <div
              data-testid="recycle-bin-settings-notice"
              style={{
                padding: tokens.spacing.sm,
                borderRadius: tokens.radius.button,
                backgroundColor: "rgba(80, 200, 120, 0.12)",
                color: "#8fe3a5",
                fontSize: tokens.typography.size.secondary,
              }}
            >
              {notice}
            </div>
          )}

          {actionError && (
            <div
              data-testid="recycle-bin-settings-error"
              style={{
                padding: tokens.spacing.sm,
                borderRadius: tokens.radius.button,
                backgroundColor: "rgba(255, 107, 107, 0.12)",
                color: "#ff9999",
                fontSize: tokens.typography.size.secondary,
              }}
            >
              {actionError}
            </div>
          )}

          {books.length === 0 ? (
            <div
              data-testid="recycle-bin-settings-empty"
              style={{ color: tokens.color.text.muted, fontSize: tokens.typography.size.secondary }}
            >
              回收站为空。
            </div>
          ) : (
            <ul
              data-testid="recycle-bin-settings-list"
              style={{
                margin: 0,
                padding: "8px 12px 8px 28px",
                maxHeight: 240,
                overflowY: "auto",
                backgroundColor: tokens.color.bg.toolbar,
                borderRadius: tokens.radius.button,
                border: `1px solid ${tokens.color.border.default}`,
                fontSize: 13,
                color: tokens.color.text.secondary,
              }}
            >
              {books.map((book) => (
                <li
                  key={book.book_id}
                  data-testid={`recycle-bin-settings-item-${book.book_id}`}
                  style={{ marginBottom: 4 }}
                >
                  <span style={{ fontWeight: 500, color: tokens.color.text.primary }}>{book.title}</span>
                  {typeof book.page_count === "number" ? ` · ${book.page_count} 页` : ""}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <section
        data-testid="recycle-bin-settings-policy-note"
        style={{
          padding: tokens.spacing.md,
          backgroundColor: tokens.color.surface.card,
          border: `1px solid ${tokens.color.border.default}`,
          borderRadius: tokens.radius.card,
          color: tokens.color.text.secondary,
          fontSize: tokens.typography.size.secondary,
          lineHeight: tokens.typography.lineHeight,
        }}
      >
        只读说明：回收站自动清理策略未开放——当前没有调度器消费自动清理天数，因此本页不提供该设置；
        此处只提供手动清空。
      </section>

      {confirmOpen && books.length > 0 && (
        <PermanentDeleteConfirmDialog
          targets={books}
          onClose={closeConfirm}
          onConfirm={handleConfirmClear}
        />
      )}
    </section>
  );
}
