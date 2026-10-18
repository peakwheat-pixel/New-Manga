import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { BookshelfPage } from "../bookshelf/BookshelfPage";
import {
  LIBRARY_DELETE_BOOK_PERMANENTLY_COMMAND,
  LIBRARY_DELETE_BOOKS_PERMANENTLY_COMMAND,
  LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND,
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

  // 7. R-007: Real service data source assertion for soft-deleted books
  it("R-007: queries real service data source for soft-deleted books and never displays active books", async () => {
    const activeBooks: BookSummary[] = [
      {
        book_id: "active-1",
        title: "活动书-未软删",
        original_title: "Active Book",
        is_favorite: false,
        is_archived: false,
        page_count: 10,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-10-01T00:00:00Z",
      },
    ];

    const softDeletedBooks: BookSummary[] = [
      {
        book_id: "trashed-1",
        title: "已软删除书-回收站目标",
        original_title: "Trashed Book",
        is_favorite: false,
        is_archived: false,
        page_count: 5,
        created_at: "2026-09-02T00:00:00Z",
        updated_at: "2026-10-02T00:00:00Z",
      },
    ];

    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === "library_list_books") {
        return activeBooks;
      }
      if (cmd === LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND) {
        return softDeletedBooks;
      }
      return {};
    });

    const client = new LibraryClient(mockInvoke);

    // Render RecycleBinPage WITHOUT initialBooks -> must trigger real fetchRecycleBooks query
    await act(async () => {
      root.render(<RecycleBinPage client={client} activeBooksCount={1} />);
    });

    // Verify it invoked the dedicated recycle bin command, NOT library_list_books
    expect(mockInvoke).toHaveBeenCalledWith(LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND);
    expect(mockInvoke).not.toHaveBeenCalledWith("library_list_books");

    // Verify the recycle bin displays the soft-deleted book
    const trashedItem = q('[data-testid="recycle-item-trashed-1"]');
    expect(trashedItem).not.toBeNull();
    expect(trashedItem?.textContent).toContain("已软删除书-回收站目标");

    // Verify the recycle bin does NOT display active books (semantic inversion fixed)
    const activeItem = q('[data-testid="recycle-item-active-1"]');
    expect(activeItem).toBeNull();
  });

  // 8. R-007: Whole library deletion validation considers all existing books in library
  it("R-007: allows deleting all recycle bin items if library still retains active books", async () => {
    const trashedBooks: BookSummary[] = [
      {
        book_id: "trashed-1",
        title: "软删书 1",
        original_title: "",
        is_favorite: false,
        is_archived: false,
        page_count: 1,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-10-01T00:00:00Z",
      },
      {
        book_id: "trashed-2",
        title: "软删书 2",
        original_title: "",
        is_favorite: false,
        is_archived: false,
        page_count: 1,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-10-01T00:00:00Z",
      },
    ];

    const mockInvoke = vi.fn(async () => ({}));
    const client = new LibraryClient(mockInvoke);

    // Scenario A: Library has 2 active books, recycle bin has 2 soft-deleted books. Total existing = 4.
    await act(async () => {
      root.render(
        <RecycleBinPage client={client} initialBooks={trashedBooks} activeBooksCount={2} />,
      );
    });

    // Select all 2 items in recycle bin
    await act(async () => {
      q<HTMLInputElement>('[data-testid="recycle-select-all-checkbox"]')?.click();
    });

    // Click permanent delete
    await act(async () => {
      q<HTMLButtonElement>('[data-testid="recycle-bin-permanent-delete-btn"]')?.click();
    });

    // Dialog SHOULD open because 2 deleted != 4 total books in library
    expect(q('[data-testid="permanent-delete-confirm-dialog"]')).not.toBeNull();
    expect(q('[data-testid="recycle-bin-whole-library-error"]')).toBeNull();
  });
  // AC3 (N-002): a partially succeeded batch keeps its per-item targets
  it("AC3: a partially succeeded batch drops deleted books and keeps only cleanup_pending selected", async () => {
    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === LIBRARY_DELETE_BOOKS_PERMANENTLY_COMMAND) {
        // book-1 really was deleted; book-2 is still cleanup_pending
        throw {
          code: "BOOK_DELETE_BATCH_CLEANUP_PENDING",
          details: {
            phase: "cleanup",
            requested_count: 2,
            completed_count: 1,
            items: [
              { book_id: "book-1", status: "deleted", error_code: null },
              { book_id: "book-2", status: "cleanup_pending", error_code: null },
            ],
          },
        };
      }
      return {};
    });
    const client = new LibraryClient(mockInvoke);

    await act(async () => {
      root.render(<RecycleBinPage client={client} initialBooks={MOCK_BOOKS} totalBooksCount={10} />);
    });

    await act(async () => {
      q<HTMLInputElement>('[data-testid="recycle-item-checkbox-book-1"]')?.click();
    });
    await act(async () => {
      q<HTMLInputElement>('[data-testid="recycle-item-checkbox-book-2"]')?.click();
    });
    await act(async () => {
      q<HTMLButtonElement>('[data-testid="recycle-bin-permanent-delete-btn"]')?.click();
    });
    await act(async () => {
      q<HTMLInputElement>('[data-testid="confirm-understand-checkbox"]')?.click();
    });
    await act(async () => {
      q<HTMLButtonElement>('[data-testid="confirm-permanent-delete-btn"]')?.click();
    });

    // The book that really was deleted is gone from the recycle list, so it can
    // never be submitted again (which would answer BOOK_NOT_FOUND) ...
    expect(q('[data-testid="recycle-item-checkbox-book-1"]')).toBeNull();

    // ... while the cleanup_pending book is still listed AND still selected, so
    // the next submit retries just the pending subset.
    const pending = q<HTMLInputElement>('[data-testid="recycle-item-checkbox-book-2"]');
    expect(pending).not.toBeNull();
    expect(pending?.checked).toBe(true);

    // The outcome keeps both per-item counts instead of collapsing to a message.
    expect(document.body.textContent).toContain("cleanup_pending");
    expect(document.body.textContent).toContain("已永久删除 1 本");
  });

  // AC1 (R-007): a failed query must not be reported as an empty recycle bin
  it("AC1: a failed recycle bin query is reported instead of showing an empty bin", async () => {
    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND) {
        throw { code: "CORE_UNAVAILABLE" };
      }
      return {};
    });
    const client = new LibraryClient(mockInvoke);

    await act(async () => {
      root.render(<RecycleBinPage client={client} totalBooksCount={5} />);
    });

    // The failure is surfaced, with a retry affordance ...
    const notice = q('[data-testid="recycle-bin-load-error"]');
    expect(notice).not.toBeNull();
    expect(notice?.textContent).toContain("回收站读取失败");
    // ... and it explicitly warns against reading the empty list as fact.
    expect(notice?.textContent).toContain("请勿据此判断作品已被清空");
    expect(q('[data-testid="retry-recycle-bin-load-btn"]')).not.toBeNull();
  });

  // AC1: a successful query clears the notice
  it("AC1: a successful recycle bin query shows no load error", async () => {
    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND) {
        return [];
      }
      return {};
    });
    const client = new LibraryClient(mockInvoke);

    await act(async () => {
      root.render(<RecycleBinPage client={client} totalBooksCount={5} />);
    });

    expect(q('[data-testid="recycle-bin-load-error"]')).toBeNull();
  });
});
