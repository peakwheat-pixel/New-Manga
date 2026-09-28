import React from "react";
import { renderToString } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { LibraryPanel } from "./LibraryPanel";
import { LibraryClient } from "./client";
import type { BookSummary } from "./types";

describe("LibraryPanel Component", () => {
  it("renders books list in success state", () => {
    const books: BookSummary[] = [
      {
        book_id: "book-001",
        title: "海贼王",
        original_title: "ONE PIECE",
        is_favorite: true,
        is_archived: false,
        page_count: 24,
        created_at: "2026-09-28T10:00:00Z",
        updated_at: "2026-09-28T10:00:00Z",
      },
    ];

    const html = renderToString(
      <LibraryPanel initialState={{ books, loading: false, error: null }} />
    );

    expect(html).toContain("海贼王");
    expect(html).toContain("ONE PIECE");
    expect(html).toContain("页数: 24");
    expect(html).toContain("2026-09-28T10:00:00Z");
    expect(html).toContain("★ 收藏");
    expect(html).toContain('data-testid="library-book-list"');
  });

  it("renders empty state message when book list is empty", () => {
    const html = renderToString(
      <LibraryPanel initialState={{ books: [], loading: false, error: null }} />
    );

    expect(html).toContain("书架为空，暂无书目");
    expect(html).toContain('data-testid="library-empty"');
    expect(html).not.toContain('data-testid="library-book-list"');
  });

  it("renders explicit CORE_UNAVAILABLE error UI with no auto-retry notice", () => {
    const html = renderToString(
      <LibraryPanel
        initialState={{
          books: null,
          loading: false,
          error: "CORE_UNAVAILABLE",
        }}
      />
    );

    expect(html).toContain("Core 服务不可用 (CORE_UNAVAILABLE)");
    expect(html).toContain("系统不会自动重试");
    expect(html).toContain('data-testid="library-error"');
    expect(html).not.toContain('data-testid="library-book-list"');
  });

  it("renders loading indicator when loading is true", () => {
    const html = renderToString(
      <LibraryPanel initialState={{ loading: true, books: null, error: null }} />
    );

    expect(html).toContain("正在加载书目数据...");
    expect(html).toContain('data-testid="library-loading"');
  });

  it("interacts with LibraryClient without auto-retrying on failure", async () => {
    let callCount = 0;
    const invoke = vi.fn(async (cmd: string) => {
      callCount += 1;
      if (cmd === "library_list_books") {
        throw "CORE_UNAVAILABLE";
      }
      return null;
    });

    const client = new LibraryClient(invoke);
    await expect(client.listBooks()).rejects.toMatchObject({
      code: "CORE_UNAVAILABLE",
    });

    // Verify it was called exactly once, no retry loop
    expect(callCount).toBe(1);
  });
});
