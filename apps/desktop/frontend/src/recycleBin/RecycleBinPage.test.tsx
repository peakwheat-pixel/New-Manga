import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { BookshelfPage } from "../bookshelf/BookshelfPage";
import {
  LIBRARY_DELETE_BOOK_PERMANENTLY_COMMAND,
  LIBRARY_DELETE_BOOKS_PERMANENTLY_COMMAND,
  LibraryClient,
} from "../library/client";
import type { BookSummary } from "../library/types";
import { RecycleBinPage } from "./RecycleBinPage";

const MOCK_BOOKS: BookSummary[] = [
  {
    book_id: "book-1",
    title: "海贼王",
    original_title: "ONE PIECE",
    is_favorite: true,
    is_archived: false,
    page_count: 24,
    created_at: "2026-09-01T00:00:00Z",
    updated_at: "2026-10-01T00:00:00Z",
  },
  {
    book_id: "book-2",
    title: "进击的巨人",
    original_title: "進撃の巨人",
    is_favorite: false,
    is_archived: true,
    page_count: null,
    created_at: "2026-09-05T00:00:00Z",
    updated_at: "2026-10-05T00:00:00Z",
  },
  {
    book_id: "book-3",
    title: "火影忍者",
    original_title: "NARUTO",
    is_favorite: false,
    is_archived: false,
    page_count: 0,
    created_at: "2026-09-10T00:00:00Z",
    updated_at: "2026-09-20T00:00:00Z",
  },
];

describe("AC5: Recycle Bin Permanent Delete & Confirmation Workflow", () => {
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

  const q = <T extends HTMLElement = HTMLElement>(sel: string): T | null =>
    container.querySelector(sel);

  // 1. Requirement 1: Bookshelf MUST NOT have permanent delete entry point
  it("bookshelf page has NO permanent delete entry point", async () => {
    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === "library_list_books") return MOCK_BOOKS;
      if (cmd === "list_chapters") return { chapters: [] };
      return {};
    });
    const client = new LibraryClient(mockInvoke);

    await act(async () => {
      root.render(<BookshelfPage client={client} initialBooks={MOCK_BOOKS} />);
    });

    // Bookshelf itself has NO permanent delete button anywhere
    expect(q('[data-testid="recycle-bin-permanent-delete-btn"]')).toBeNull();
    const allButtons = Array.from(container.querySelectorAll("button"));
    const permDeleteButtons = allButtons.filter((b) => b.textContent?.includes("永久删除"));
    expect(permDeleteButtons).toHaveLength(0);

    // Toolbar DOES have the Recycle Bin opener button
    const recycleBinBtn = q('[data-testid="toolbar-recycle-bin-btn"]');
    expect(recycleBinBtn).not.toBeNull();
  });

  // 2. Requirement 1: Recycle bin page DOES provide the permanent delete entry point
  it("recycle bin provides the permanent delete entry point (disabled when none selected)", async () => {
    const mockInvoke = vi.fn(async () => ({}));
    const client = new LibraryClient(mockInvoke);

    await act(async () => {
      root.render(<RecycleBinPage client={client} initialBooks={MOCK_BOOKS} totalBooksCount={10} />);
    });

    const permDeleteBtn = q<HTMLButtonElement>('[data-testid="recycle-bin-permanent-delete-btn"]');
    expect(permDeleteBtn).not.toBeNull();
    expect(permDeleteBtn?.disabled).toBe(true);
  });

  // 3. Requirement 2 & 4: Second confirmation lists targets & count, requires checkbox, and shows all notices
  it("second confirmation dialog lists target titles and total count, displays mandatory notices, and requires explicit checkbox", async () => {
    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === LIBRARY_DELETE_BOOK_PERMANENTLY_COMMAND) {
        return { book_id: "book-1", deleted: true };
      }
      return {};
    });
    const client = new LibraryClient(mockInvoke);

    await act(async () => {
      root.render(<RecycleBinPage client={client} initialBooks={MOCK_BOOKS} totalBooksCount={10} />);
    });

    // Select book-1
    const cb1 = q<HTMLInputElement>('[data-testid="recycle-item-checkbox-book-1"]');
    expect(cb1).not.toBeNull();
    await act(async () => {
      cb1?.click();
    });

    // Click permanent delete button
    const permDeleteBtn = q<HTMLButtonElement>('[data-testid="recycle-bin-permanent-delete-btn"]');
    expect(permDeleteBtn?.disabled).toBe(false);
    await act(async () => {
      permDeleteBtn?.click();
    });

    // Verify dialog opened
    const dialog = q('[data-testid="permanent-delete-confirm-dialog"]');
    expect(dialog).not.toBeNull();

    // Verify targets count and titles listed individually
    const targetsCount = q('[data-testid="confirm-targets-count"]');
    expect(targetsCount?.textContent).toContain("即将永久删除 1 部作品");
    const targetItem = q('[data-testid="confirm-target-item-book-1"]');
    expect(targetItem?.textContent).toContain("海贼王");

    // Verify all 3 mandatory notices
    const noticeIrreversible = q('[data-testid="notice-irreversible"]');
    expect(noticeIrreversible?.textContent).toContain("App 回收站无法恢复");
    const noticeExport = q('[data-testid="notice-user-export"]');
    expect(noticeExport?.textContent).toContain("用户导出目录内的文件会保留");
    const noticeBackup = q('[data-testid="notice-history-backup"]');
    expect(noticeBackup?.textContent).toContain("全库历史备份不处理且可能含旧快照");

    // Verify submit button is disabled before checking "我理解不可恢复"
    const confirmBtn = q<HTMLButtonElement>('[data-testid="confirm-permanent-delete-btn"]');
    expect(confirmBtn?.disabled).toBe(true);

    // Check "我理解不可恢复"
    const understandCb = q<HTMLInputElement>('[data-testid="confirm-understand-checkbox"]');
    expect(understandCb).not.toBeNull();
    await act(async () => {
      understandCb?.click();
    });
    expect(confirmBtn?.disabled).toBe(false);

    // Click confirm -> calls single permanent delete IPC
    await act(async () => {
      confirmBtn?.click();
    });

    expect(mockInvoke).toHaveBeenCalledWith(LIBRARY_DELETE_BOOK_PERMANENTLY_COMMAND, {
      payload: {
        book_id: "book-1",
        confirm_permanent_delete: true,
      },
    });
  });

  // 4. Requirement 3: Same frozen snapshot for batch delete with identical ID order and count
  it("batch delete uses the same frozen snapshot for book_ids, confirmed_book_ids, and confirm_count", async () => {
    let capturedPayload: any = null;
    const mockInvoke = vi.fn(async (cmd: string, args: any) => {
      if (cmd === LIBRARY_DELETE_BOOKS_PERMANENTLY_COMMAND) {
        capturedPayload = args?.payload;
        return {
          requested_count: 2,
          completed_count: 2,
          items: [
            { book_id: "book-2", status: "deleted", error_code: null },
            { book_id: "book-1", status: "deleted", error_code: null },
          ],
        };
      }
      return {};
    });
    const client = new LibraryClient(mockInvoke);

    await act(async () => {
      root.render(<RecycleBinPage client={client} initialBooks={MOCK_BOOKS} totalBooksCount={10} />);
    });

    // Select book-2 first, then book-1
    await act(async () => {
      q<HTMLInputElement>('[data-testid="recycle-item-checkbox-book-2"]')?.click();
    });
    await act(async () => {
      q<HTMLInputElement>('[data-testid="recycle-item-checkbox-book-1"]')?.click();
    });

    // Click permanent delete button
    await act(async () => {
      q<HTMLButtonElement>('[data-testid="recycle-bin-permanent-delete-btn"]')?.click();
    });

    // Check targets in confirmation dialog
    expect(q('[data-testid="confirm-target-item-book-2"]')).not.toBeNull();
    expect(q('[data-testid="confirm-target-item-book-1"]')).not.toBeNull();
    expect(q('[data-testid="confirm-targets-count"]')?.textContent).toContain("即将永久删除 2 部作品");

    // Check understanding and submit
    await act(async () => {
      q<HTMLInputElement>('[data-testid="confirm-understand-checkbox"]')?.click();
    });
    await act(async () => {
      q<HTMLButtonElement>('[data-testid="confirm-permanent-delete-btn"]')?.click();
    });

    // Verify batch payload
    expect(capturedPayload).not.toBeNull();
    expect(capturedPayload.book_ids).toEqual(["book-2", "book-1"]);
    expect(capturedPayload.confirmed_book_ids).toEqual(["book-2", "book-1"]);
    expect(capturedPayload.confirm_count).toBe(2);
    expect(capturedPayload.confirm_permanent_delete).toBe(true);
  });

  // 5. Requirement 5: Batch limit > 20 is blocked and alerts
  it("blocks and displays an error when selection exceeds batch limit of 20", async () => {
    const mockInvoke = vi.fn(async () => ({}));
    const client = new LibraryClient(mockInvoke);

    // Create 25 mock books
    const manyBooks: BookSummary[] = Array.from({ length: 25 }, (_, i) => ({
      book_id: `book-${i + 1}`,
      title: `Book ${i + 1}`,
      original_title: "",
      is_favorite: false,
      is_archived: false,
      page_count: 10,
      created_at: "2026-09-01T00:00:00Z",
      updated_at: "2026-10-01T00:00:00Z",
    }));

    await act(async () => {
      root.render(<RecycleBinPage client={client} initialBooks={manyBooks} totalBooksCount={100} />);
    });

    // Select all (25 books)
    await act(async () => {
      q<HTMLInputElement>('[data-testid="recycle-select-all-checkbox"]')?.click();
    });

    // Click permanent delete
    await act(async () => {
      q<HTMLButtonElement>('[data-testid="recycle-bin-permanent-delete-btn"]')?.click();
    });

    // Dialog must NOT open
    expect(q('[data-testid="permanent-delete-confirm-dialog"]')).toBeNull();

    // Batch limit error must appear
    const errorEl = q('[data-testid="recycle-bin-batch-limit-error"]');
    expect(errorEl).not.toBeNull();
    expect(errorEl?.textContent).toContain("批量删除上限为 20 本，当前已选择 25 本");
    expect(mockInvoke).not.toHaveBeenCalled();
  });

  // 6. Requirement 5: Whole library deletion is blocked
  it("blocks and displays an error when attempting to permanently delete the whole library", async () => {
    const mockInvoke = vi.fn(async () => ({}));
    const client = new LibraryClient(mockInvoke);

    // Total books in library is 3, same as MOCK_BOOKS.length
    await act(async () => {
      root.render(<RecycleBinPage client={client} initialBooks={MOCK_BOOKS} totalBooksCount={3} />);
    });

    // Select all 3 books
    await act(async () => {
      q<HTMLInputElement>('[data-testid="recycle-select-all-checkbox"]')?.click();
    });

    // Click permanent delete
    await act(async () => {
      q<HTMLButtonElement>('[data-testid="recycle-bin-permanent-delete-btn"]')?.click();
    });

    // Dialog must NOT open
    expect(q('[data-testid="permanent-delete-confirm-dialog"]')).toBeNull();

    // Whole library error must appear
    const errorEl = q('[data-testid="recycle-bin-whole-library-error"]');
    expect(errorEl).not.toBeNull();
    expect(errorEl?.textContent).toContain("不能单次批量清空整库");
    expect(mockInvoke).not.toHaveBeenCalled();
  });
});
