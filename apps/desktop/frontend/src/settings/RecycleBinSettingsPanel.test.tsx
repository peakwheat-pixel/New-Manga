import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LibraryClientError } from "../library/client";
import type { BookSummary } from "../library/types";
import { RecycleBinSettingsPanel, type RecycleBinClientLike } from "./RecycleBinSettingsPanel";

/**
 * SETTINGS-OPEN-C-1-RECYCLE §2 / AC1-AC3 — recycle-bin operation surface:
 * real list from `library_list_recycle_bin_books`, empty state distinct from
 * a load failure, clear through the existing `library_delete_books_permanently`
 * confirmation tuple batched at the frozen 20-book limit, the whole-library
 * protection surfaced verbatim (never bypassed), and the retention policy as
 * a read-only note (no fake control).
 */

function book(id: string, title: string, pageCount: number | null = 3): BookSummary {
  return {
    book_id: id,
    title,
    original_title: "",
    is_favorite: false,
    is_archived: true,
    page_count: pageCount,
    created_at: "2026-10-01T00:00:00.000Z",
    updated_at: "2026-10-02T00:00:00.000Z",
  };
}

class FakeRecycleClient implements RecycleBinClientLike {
  books: BookSummary[];
  failLoad: unknown = null;
  failDelete: unknown = null;
  deleteCalls: Array<Record<string, unknown>> = [];
  listCalls = 0;

  constructor(books: BookSummary[]) {
    this.books = books;
  }

  async listRecycleBinBooks(): Promise<BookSummary[]> {
    this.listCalls += 1;
    if (this.failLoad) throw this.failLoad;
    return this.books;
  }

  async deleteBooksPermanently(payload: {
    book_ids: string[];
    confirmed_book_ids: string[];
    confirm_count: number;
    confirm_permanent_delete: true;
  }): Promise<unknown> {
    this.deleteCalls.push(payload as unknown as Record<string, unknown>);
    if (this.failDelete) throw this.failDelete;
    this.books = this.books.filter((item) => !payload.book_ids.includes(item.book_id));
    return {
      requested_count: payload.book_ids.length,
      completed_count: payload.book_ids.length,
      items: payload.book_ids.map((book_id) => ({ book_id, status: "deleted" })),
    };
  }
}

describe("RecycleBinSettingsPanel (SETTINGS-OPEN-C-1-RECYCLE §2)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    container = dom.window.document.createElement("div");
    dom.window.document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    vi.unstubAllGlobals();
  });

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;
  const button = (testId: string) =>
    q(`[data-testid="${testId}"]`) as HTMLButtonElement | null;
  const checkbox = () =>
    q('[data-testid="confirm-understand-checkbox"]') as HTMLInputElement | null;
  const submitButton = () =>
    q('[data-testid="confirm-permanent-delete-btn"]') as HTMLButtonElement | null;

  const render = async (client: RecycleBinClientLike) => {
    await act(async () => {
      root.render(<RecycleBinSettingsPanel client={client} />);
    });
  };

  it("shows the loading skeleton while the first list request is pending", async () => {
    const client: RecycleBinClientLike = {
      listRecycleBinBooks: vi.fn(() => new Promise<BookSummary[]>(() => {})),
      deleteBooksPermanently: vi.fn(),
    };
    act(() => {
      root.render(<RecycleBinSettingsPanel client={client} />);
    });
    expect(q('[data-testid="recycle-bin-settings-loading"]')).not.toBeNull();
    expect(button("recycle-bin-settings-clear-btn")).toBeNull();
  });

  it("renders the real list (count, titles, page counts) and the read-only retention note", async () => {
    const client = new FakeRecycleClient([
      book("b1", "作品一", 12),
      book("b2", "作品二", null),
    ]);
    await render(client);

    expect(client.listCalls).toBe(1);
    expect(q('[data-testid="recycle-bin-settings-summary"]')?.textContent).toContain(
      "回收站：2 部作品",
    );
    expect(q('[data-testid="recycle-bin-settings-item-b1"]')?.textContent).toContain("作品一");
    expect(q('[data-testid="recycle-bin-settings-item-b1"]')?.textContent).toContain("12 页");
    expect(q('[data-testid="recycle-bin-settings-item-b2"]')?.textContent).toContain("作品二");
    // D11/§2.1: retention policy is a read-only note, not a settings control.
    expect(q('[data-testid="recycle-bin-settings-policy-note"]')?.textContent).toContain(
      "没有调度器",
    );
    expect(button("recycle-bin-settings-clear-btn")?.disabled).toBe(false);
  });

  it("distinguishes an empty bin from a load failure", async () => {
    await render(new FakeRecycleClient([]));
    expect(q('[data-testid="recycle-bin-settings-empty"]')?.textContent).toContain("回收站为空");
    expect(button("recycle-bin-settings-clear-btn")?.disabled).toBe(true);
    expect(q('[data-testid="recycle-bin-settings-load-error"]')).toBeNull();
  });

  it("shows a load error with a retry action and never reports an empty bin", async () => {
    const client = new FakeRecycleClient([book("b1", "作品一")]);
    client.failLoad = new LibraryClientError("CORE_UNAVAILABLE", "core down");
    await render(client);

    expect(q('[data-testid="recycle-bin-settings-load-error"]')?.textContent).toContain(
      "CORE_UNAVAILABLE",
    );
    expect(q('[data-testid="recycle-bin-settings-empty"]')).toBeNull();

    client.failLoad = null;
    await act(async () => {
      button("recycle-bin-settings-retry-btn")?.click();
      await Promise.resolve();
    });
    expect(q('[data-testid="recycle-bin-settings-load-error"]')).toBeNull();
    expect(q('[data-testid="recycle-bin-settings-item-b1"]')).not.toBeNull();
  });

  it("clears the bin through the confirmation dialog with one strict batch", async () => {
    const client = new FakeRecycleClient([book("b1", "作品一"), book("b2", "作品二")]);
    await render(client);

    await act(async () => {
      button("recycle-bin-settings-clear-btn")?.click();
      await Promise.resolve();
    });
    expect(q('[data-testid="permanent-delete-confirm-dialog"]')).not.toBeNull();
    expect(q('[data-testid="confirm-targets-count"]')?.textContent).toContain("2 部作品");
    expect(submitButton()?.disabled).toBe(true);

    await act(async () => {
      checkbox()?.click();
      await Promise.resolve();
    });
    expect(submitButton()?.disabled).toBe(false);

    await act(async () => {
      submitButton()?.click();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(client.deleteCalls).toHaveLength(1);
    expect(client.deleteCalls[0]).toEqual({
      book_ids: ["b1", "b2"],
      confirmed_book_ids: ["b1", "b2"],
      confirm_count: 2,
      confirm_permanent_delete: true,
    });
    // Dialog closed, list reloaded (now empty), success notice visible.
    expect(q('[data-testid="permanent-delete-confirm-dialog"]')).toBeNull();
    expect(q('[data-testid="recycle-bin-settings-empty"]')).not.toBeNull();
    expect(q('[data-testid="recycle-bin-settings-notice"]')?.textContent).toContain("已永久删除 2");
  });

  it("splits a large bin into ≤20-book batches, each with its own strict tuple", async () => {
    const many = Array.from({ length: 25 }, (_, index) =>
      book(`bk-${String(index).padStart(2, "0")}`, `作品${index}`),
    );
    const client = new FakeRecycleClient(many);
    await render(client);

    await act(async () => {
      button("recycle-bin-settings-clear-btn")?.click();
      await Promise.resolve();
    });
    await act(async () => {
      checkbox()?.click();
      await Promise.resolve();
    });
    await act(async () => {
      submitButton()?.click();
      await Promise.resolve();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(client.deleteCalls).toHaveLength(2);
    expect((client.deleteCalls[0].book_ids as string[]).length).toBe(20);
    expect((client.deleteCalls[1].book_ids as string[]).length).toBe(5);
    for (const call of client.deleteCalls) {
      const ids = call.book_ids as string[];
      expect(call.confirmed_book_ids).toEqual(ids);
      expect(call.confirm_count).toBe(ids.length);
      expect(call.confirm_permanent_delete).toBe(true);
    }
  });

  it("surfaces the whole-library protection verbatim instead of bypassing it", async () => {
    const client = new FakeRecycleClient([book("b1", "唯一作品")]);
    client.failDelete = new LibraryClientError(
      "BOOK_DELETE_BATCH_WHOLE_LIBRARY",
      "whole library",
    );
    await render(client);

    await act(async () => {
      button("recycle-bin-settings-clear-btn")?.click();
      await Promise.resolve();
    });
    await act(async () => {
      checkbox()?.click();
      await Promise.resolve();
    });
    await act(async () => {
      submitButton()?.click();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(q('[data-testid="permanent-delete-error"]')?.textContent).toContain(
      "不能删除整个书库",
    );
    // Still open for the user to cancel; nothing was removed locally.
    expect(q('[data-testid="permanent-delete-confirm-dialog"]')).not.toBeNull();
    expect(button("recycle-bin-settings-clear-btn")?.disabled).toBe(false);
  });
});
