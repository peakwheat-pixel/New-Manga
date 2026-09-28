import React, { useCallback, useEffect, useState } from "react";
import { LibraryClient, LibraryClientError } from "./client";
import type { BookSummary } from "./types";

export interface LibraryPanelProps {
  client?: LibraryClient;
  /** Optional initial state for testing or static preview */
  initialState?: {
    loading?: boolean;
    books?: BookSummary[] | null;
    error?: string | null;
  };
}

export function LibraryPanel({ client, initialState }: LibraryPanelProps) {
  const [loading, setLoading] = useState<boolean>(initialState?.loading ?? (initialState ? false : true));
  const [books, setBooks] = useState<BookSummary[] | null>(initialState?.books ?? null);
  const [error, setError] = useState<string | null>(initialState?.error ?? null);

  const fetchBooks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const activeClient = client || new LibraryClient();
      const list = await activeClient.listBooks();
      setBooks(list);
    } catch (err) {
      const code = err instanceof LibraryClientError ? err.code : String(err);
      setError(code);
    } finally {
      setLoading(false);
    }
  }, [client]);

  useEffect(() => {
    // Only auto-fetch if no static initial state was passed
    if (!initialState) {
      void fetchBooks();
    }
  }, [fetchBooks, initialState]);

  return (
    <section
      data-testid="library-panel"
      style={{
        marginTop: 20,
        padding: 16,
        border: "1px solid #2a3441",
        borderRadius: 6,
        background: "#161b22",
        color: "#e6edf3",
      }}
    >
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <h2 style={{ fontSize: 16, margin: 0, fontWeight: 600 }}>书库书目 (Library)</h2>
        <button
          data-testid="library-refresh-btn"
          onClick={() => void fetchBooks()}
          disabled={loading}
          style={{
            padding: "4px 10px",
            fontSize: 12,
            background: "#21262d",
            color: "#c9d1d9",
            border: "1px solid #30363d",
            borderRadius: 4,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "加载中..." : "刷新"}
        </button>
      </header>

      {/* Loading state */}
      {loading && (
        <div data-testid="library-loading" style={{ color: "#8b949e", padding: "12px 0" }}>
          正在加载书目数据...
        </div>
      )}

      {/* Error state (explicit UI, no automatic retry) */}
      {!loading && error && (
        <div
          data-testid="library-error"
          style={{
            padding: 12,
            background: "#3c1618",
            border: "1px solid #f85149",
            borderRadius: 4,
            color: "#ff7b72",
          }}
        >
          <div style={{ fontWeight: "bold" }}>
            {error === "CORE_UNAVAILABLE" ? "Core 服务不可用 (CORE_UNAVAILABLE)" : `加载失败: ${error}`}
          </div>
          <div style={{ fontSize: 12, marginTop: 4, color: "#e6edf3" }}>
            无法连接到 Python Core 服务。请检查后台服务状态并点击上方“刷新”按钮重试（系统不会自动重试）。
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && books && books.length === 0 && (
        <div
          data-testid="library-empty"
          style={{
            padding: "24px 0",
            textAlign: "center",
            color: "#8b949e",
            fontSize: 13,
          }}
        >
          书架为空，暂无书目。
        </div>
      )}

      {/* Success list state */}
      {!loading && !error && books && books.length > 0 && (
        <div data-testid="library-book-list" style={{ display: "grid", gap: 10 }}>
          {books.map((book) => (
            <div
              key={book.book_id}
              data-testid={`book-item-${book.book_id}`}
              style={{
                padding: 10,
                background: "#0d1117",
                border: "1px solid #30363d",
                borderRadius: 4,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <span style={{ fontWeight: 600, fontSize: 14 }}>{book.title}</span>
                {book.original_title && (
                  <span style={{ fontSize: 12, color: "#8b949e" }}>{`(${book.original_title})`}</span>
                )}
              </div>
              <div style={{ fontSize: 12, color: "#8b949e", marginTop: 6, display: "flex", gap: 16 }}>
                <span>{`页数: ${book.page_count}`}</span>
                <span>{`创建时间: ${book.created_at}`}</span>
                {book.is_favorite && <span style={{ color: "#e3b341" }}>★ 收藏</span>}
                {book.is_archived && <span style={{ color: "#8b949e" }}>[已归档]</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
