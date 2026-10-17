import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LibraryClient } from "../library/client";
import type { BookSummary, ChapterNavSummary, ImportSummary, PageNavSummary } from "../library/types";
import { BookCard } from "./BookCard";
import { BookList } from "./BookList";
import { BookshelfPage } from "./BookshelfPage";
import { ImportDialog } from "./ImportDialog";

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
    page_count: null, // W1: unknown page count MUST render as "—", NOT 0
    created_at: "2026-09-05T00:00:00Z",
    updated_at: "2026-10-05T00:00:00Z",
  },
  {
    book_id: "book-3",
    title: "火影忍者",
    original_title: "NARUTO",
    is_favorite: false,
    is_archived: false,
    page_count: 0, // Known 0 pages
    created_at: "2026-09-10T00:00:00Z",
    updated_at: "2026-09-20T00:00:00Z",
  },
];

const MOCK_CHAPTERS: ChapterNavSummary[] = [
  {
    chapter_id: "ch-101",
    title: "第 1 话：冒险的黎明",
    chapter_number: "1",
    sort_order: 1,
  },
  {
    chapter_id: "ch-102",
    title: "第 2 话：戴草帽的路飞",
    chapter_number: "2",
    sort_order: 2,
  },
];

const MOCK_PAGES: PageNavSummary[] = [
  { page_id: "p-1", source_filename: "001.jpg", sort_order: 1 },
  { page_id: "p-2", source_filename: "002.jpg", sort_order: 2 },
];

describe("Bookshelf UI - Data Binding & State Matrix (W1, W2, W3, W28, W30)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: ReturnType<typeof createRoot>;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
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

  // ---- W1: ListBooks page_count=null 渲染「—」，不得渲染为 0 ----
  describe("W1 BookCard & BookList page_count rules", () => {
    it("BookCard renders '—' when page_count is null, never 0", () => {
      const html = renderToString(
        <BookCard book={MOCK_BOOKS[1]} onSelect={vi.fn()} />,
      );
      expect(html).toContain("进击的巨人");
      expect(html).toContain("—");
      expect(html).not.toContain("0 页");
    });

    it("BookCard renders '0 页' when page_count is explicitly 0", () => {
      const html = renderToString(
        <BookCard book={MOCK_BOOKS[2]} onSelect={vi.fn()} />,
      );
      expect(html).toContain("火影忍者");
      expect(html).toContain("0 页");
    });

    it("BookCard renders positive page count correctly", () => {
      const html = renderToString(
        <BookCard book={MOCK_BOOKS[0]} onSelect={vi.fn()} />,
      );
      expect(html).toContain("24 页");
    });

    it("BookList renders '—' when page_count is null in list view", () => {
      const html = renderToString(
        <BookList books={MOCK_BOOKS} selectedBookId="book-2" onSelect={vi.fn()} />,
      );
      expect(html).toContain("data-testid=\"book-row-page-count-book-2\"");
      expect(html).toContain("—");
    });
  });

  // ---- §2.4 State Matrix: loading / empty / error / disabled / progress ----
  describe("State Matrix (§2.4)", () => {
    it("renders loading state with skeleton cards when client listBooks is pending", async () => {
      const pendingClient = new LibraryClient(vi.fn().mockReturnValue(new Promise(() => {})));
      await act(async () => {
        root.render(<BookshelfPage client={pendingClient} />);
      });

      const skeleton = container.querySelector('[data-testid="bookshelf-loading-skeleton"]');
      expect(skeleton).not.toBeNull();
    });

    it("renders empty library guide when listBooks returns an empty array", async () => {
      const emptyClient = new LibraryClient(vi.fn().mockResolvedValue([]));
      await act(async () => {
        root.render(<BookshelfPage client={emptyClient} />);
      });

      const emptyState = container.querySelector('[data-testid="bookshelf-empty-state"]');
      expect(emptyState).not.toBeNull();
      expect(container.textContent).toContain("还没有作品");

      // Empty-shelf import remains visible while create book is available.
      const importBtn = container.querySelector('[data-testid="empty-import-btn"]') as HTMLButtonElement;
      expect(importBtn).not.toBeNull();
      expect(importBtn.disabled).toBe(false);

      const newBookBtn = container.querySelector('[data-testid="empty-new-book-btn"]') as HTMLButtonElement;
      expect(newBookBtn.disabled).toBe(false);
    });

    it("renders error card with localized code and retry button on CORE_UNAVAILABLE (W28)", async () => {
      const errorClient = new LibraryClient(vi.fn().mockRejectedValue("CORE_UNAVAILABLE"));
      await act(async () => {
        root.render(<BookshelfPage client={errorClient} />);
      });

      const errorCard = container.querySelector('[data-testid="bookshelf-error-card"]');
      expect(errorCard).not.toBeNull();
      expect(container.textContent).toContain("服务不可用");
      expect(container.textContent).toContain("CORE_UNAVAILABLE");

      const retryBtn = container.querySelector('[data-testid="bookshelf-retry-btn"]') as HTMLButtonElement;
      expect(retryBtn).not.toBeNull();
    });

    it("renders disabled state for missing wires (GAP-G1..G8)", async () => {
      const invoke = vi.fn().mockImplementation((cmd: string) => {
        if (cmd === "library_list_books") return Promise.resolve(MOCK_BOOKS);
        if (cmd === "list_chapters") return Promise.resolve({ chapters: MOCK_CHAPTERS });
        if (cmd === "list_chapter_pages") return Promise.resolve({ pages: MOCK_PAGES });
        return Promise.resolve(null);
      });
      const client = new LibraryClient(invoke);

      await act(async () => {
        root.render(<BookshelfPage client={client} initialBooks={MOCK_BOOKS} />);
      });

      // Create Book is available from the toolbar.
      const newBookToolbar = container.querySelector('[data-testid="toolbar-new-book-btn"]') as HTMLButtonElement;
      expect(newBookToolbar.disabled).toBe(false);

      // GAP-G2: Delete book disabled
      const deleteBookBtn = container.querySelector('[data-testid="detail-delete-btn"]') as HTMLButtonElement;
      expect(deleteBookBtn.disabled).toBe(true);
      expect(deleteBookBtn.getAttribute("title")).toContain("GAP-G2");

      // New chapter is available for the selected book.
      const newChapterBtn = container.querySelector('[data-testid="new-chapter-btn"]') as HTMLButtonElement;
      expect(newChapterBtn.disabled).toBe(false);

      // GAP-G7: Tag management disabled
      const tagsBtn = container.querySelector('[data-testid="detail-tags-btn"]') as HTMLButtonElement;
      expect(tagsBtn.disabled).toBe(true);
      expect(tagsBtn.getAttribute("title")).toContain("GAP-G7");

      // GAP-G8: Glossary / translation constraints disabled
      const glossaryBtn = container.querySelector('[data-testid="detail-glossary-btn"]') as HTMLButtonElement;
      expect(glossaryBtn.disabled).toBe(true);
      expect(glossaryBtn.getAttribute("title")).toContain("GAP-G8");
    });
  });

  // ---- W2 & W3: Chapter list & navigation callbacks ----
  describe("W2 / W3 Chapter Navigation", () => {
    it("renders chapters and fires onEnterWorkbench and onEnterReader callbacks", async () => {
      const onEnterWorkbench = vi.fn();
      const onEnterReader = vi.fn();

      const invoke = vi.fn().mockImplementation((cmd: string) => {
        if (cmd === "library_list_books") return Promise.resolve(MOCK_BOOKS);
        if (cmd === "list_chapters") return Promise.resolve({ chapters: MOCK_CHAPTERS });
        if (cmd === "list_chapter_pages") return Promise.resolve({ pages: MOCK_PAGES });
        return Promise.resolve(null);
      });
      const client = new LibraryClient(invoke);

      await act(async () => {
        root.render(
          <BookshelfPage
            client={client}
            initialBooks={MOCK_BOOKS}
            onEnterWorkbench={onEnterWorkbench}
            onEnterReader={onEnterReader}
          />,
        );
      });

      // Chapter items should be rendered
      const ch1Item = container.querySelector('[data-testid="chapter-item-ch-101"]');
      expect(ch1Item).not.toBeNull();
      expect(ch1Item?.textContent).toContain("第 1 话：冒险的黎明");

      // Click "翻译" button
      const wbBtn = container.querySelector('[data-testid="chapter-enter-workbench-btn-ch-101"]') as HTMLButtonElement;
      await act(async () => {
        wbBtn.click();
      });
      expect(onEnterWorkbench).toHaveBeenCalledWith("book-1", "ch-101");

      // Click "阅读" button
      const readerBtn = container.querySelector('[data-testid="chapter-enter-reader-btn-ch-101"]') as HTMLButtonElement;
      await act(async () => {
        readerBtn.click();
      });
      expect(onEnterReader).toHaveBeenCalledWith("book-1", "ch-101");
    });
  });

  // ---- AC3 / W30: ImportDialog workflow (the core of P12) ----
  describe("AC3 / W30 ImportDialog Flow", () => {
    it("opens visible import feedback from the bookshelf entry", async () => {
      await act(async () => {
        root.render(<BookshelfPage initialBooks={[]} />);
      });

      const importBtn = container.querySelector('[data-testid="toolbar-import-btn"]') as HTMLButtonElement;
      await act(async () => importBtn.click());

      expect(container.querySelector('[data-testid="import-dialog"]')).not.toBeNull();
      expect(container.querySelector('[data-testid="import-unavailable-notice"]')?.textContent).toContain("空书架暂不支持创建作品和章节");
      expect((container.querySelector('[data-testid="import-file-btn"]') as HTMLButtonElement).disabled).toBe(true);
      expect((container.querySelector('[data-testid="import-folder-btn"]') as HTMLButtonElement).disabled).toBe(true);
    });

    it("keeps no-target feedback consistent across toolbar, empty-state, and book-detail import entries", async () => {
      const expectUnavailable = (reason: string) => {
        expect(container.querySelector('[data-testid="import-dialog"]')).not.toBeNull();
        expect(container.querySelector('[data-testid="import-unavailable-notice"]')?.textContent).toContain(reason);
        expect((container.querySelector('[data-testid="import-file-btn"]') as HTMLButtonElement).disabled).toBe(true);
        expect((container.querySelector('[data-testid="import-folder-btn"]') as HTMLButtonElement).disabled).toBe(true);
      };

      await act(async () => {
        root.render(<BookshelfPage initialBooks={[]} />);
      });

      await act(async () => {
        (container.querySelector('[data-testid="toolbar-import-btn"]') as HTMLButtonElement).click();
      });
      expectUnavailable("空书架暂不支持创建作品和章节");
      await act(async () => {
        (container.querySelector('[data-testid="import-dialog-close-btn"]') as HTMLButtonElement).click();
      });

      await act(async () => {
        (container.querySelector('[data-testid="empty-import-btn"]') as HTMLButtonElement).click();
      });
      expectUnavailable("空书架暂不支持创建作品和章节");
      await act(async () => {
        (container.querySelector('[data-testid="import-dialog-close-btn"]') as HTMLButtonElement).click();
      });
      await act(async () => root.unmount());
      root = createRoot(container);

      const client = new LibraryClient(vi.fn().mockImplementation((command: string) => {
        if (command === "list_chapters") return Promise.resolve({ chapters: [] });
        return Promise.resolve({ pages: [] });
      }));
      await act(async () => {
        root.render(<BookshelfPage client={client} initialBooks={[MOCK_BOOKS[0]]} />);
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      await act(async () => {
        (container.querySelector('[data-testid="detail-import-btn"]') as HTMLButtonElement).click();
      });
      expectUnavailable("当前没有可导入的目标章节");
    });

    it("renders duplicate policy options with skip as default", () => {
      const html = renderToString(
        <ImportDialog
          isOpen={true}
          books={MOCK_BOOKS}
          chapters={MOCK_CHAPTERS}
          initialBookId="book-1"
          initialChapterId="ch-101"
          onClose={vi.fn()}
        />,
      );

      expect(html).toContain("跳过重复 (skip - 默认)");
      expect(html).toContain("作为新页面导入 (import_as_new)");
      expect(html).toContain("选择图片 / PDF 文件");
      expect(html).toContain("选择图片文件夹");
    });

    it("invokes library_import_file and displays ImportReport on completion", async () => {
      const mockSummary: ImportSummary = {
        chapter_id: "ch-101",
        cancelled: false,
        imported_files: 8,
        skipped_files: 2,
        rejected_files: 0,
        pending_files: 0,
      };

      const invoke = vi.fn().mockImplementation((cmd: string) => {
        if (cmd === "library_import_file") return Promise.resolve(mockSummary);
        return Promise.resolve(null);
      });
      const client = new LibraryClient(invoke);
      const onImportSuccess = vi.fn();

      await act(async () => {
        root.render(
          <ImportDialog
            isOpen={true}
            books={MOCK_BOOKS}
            chapters={MOCK_CHAPTERS}
            initialBookId="book-1"
            initialChapterId="ch-101"
            client={client}
            onClose={vi.fn()}
            onImportSuccess={onImportSuccess}
          />,
        );
      });

      const fileBtn = container.querySelector('[data-testid="import-file-btn"]') as HTMLButtonElement;
      await act(async () => {
        fileBtn.click();
      });

      expect(invoke).toHaveBeenCalledWith("library_import_file", {
        chapterId: "ch-101",
        duplicatePolicy: "skip",
      });

      // Report should be visible
      const reportView = container.querySelector('[data-testid="import-report-view"]');
      expect(reportView).not.toBeNull();
      expect(container.querySelector('[data-testid="report-imported-files"]')?.textContent).toBe("8");
      expect(container.querySelector('[data-testid="report-skipped-files"]')?.textContent).toBe("2");
      expect(container.querySelector('[data-testid="report-rejected-files"]')?.textContent).toBe("0");

      // Click finish button
      const finishBtn = container.querySelector('[data-testid="import-finish-btn"]') as HTMLButtonElement;
      await act(async () => {
        finishBtn.click();
      });
      expect(onImportSuccess).toHaveBeenCalledWith("ch-101", mockSummary);
    });

    it("handles cancellation gracefully without error state (cancelled path)", async () => {
      const cancelledSummary: ImportSummary = {
        chapter_id: "ch-101",
        cancelled: true,
        imported_files: 0,
        skipped_files: 0,
        rejected_files: 0,
        pending_files: 0,
      };

      const invoke = vi.fn().mockImplementation((cmd: string) => {
        if (cmd === "library_import_folder") return Promise.resolve(cancelledSummary);
        return Promise.resolve(null);
      });
      const client = new LibraryClient(invoke);

      await act(async () => {
        root.render(
          <ImportDialog
            isOpen={true}
            books={MOCK_BOOKS}
            chapters={MOCK_CHAPTERS}
            initialBookId="book-1"
            initialChapterId="ch-101"
            client={client}
            onClose={vi.fn()}
          />,
        );
      });

      const folderBtn = container.querySelector('[data-testid="import-folder-btn"]') as HTMLButtonElement;
      await act(async () => {
        folderBtn.click();
      });

      // No error banner should be present
      expect(container.querySelector('[data-testid="import-error-banner"]')).toBeNull();
      // Should show cancellation message
      expect(container.textContent).toContain("取消了文件夹选择");
      // Buttons remain available
      expect(folderBtn.disabled).toBe(false);
    });

    it("shows a visible error when the native picker or import fails", async () => {
      const client = new LibraryClient(vi.fn().mockRejectedValue("CORE_UNAVAILABLE"));

      await act(async () => {
        root.render(
          <ImportDialog
            isOpen={true}
            books={MOCK_BOOKS}
            chapters={MOCK_CHAPTERS}
            initialBookId="book-1"
            initialChapterId="ch-101"
            client={client}
            onClose={vi.fn()}
          />,
        );
      });

      await act(async () => {
        (container.querySelector('[data-testid="import-file-btn"]') as HTMLButtonElement).click();
      });

      expect(container.querySelector('[data-testid="import-error-banner"]')?.textContent).toContain("CORE_UNAVAILABLE");
    });
  });

  describe("AC1–AC4 create workflow", () => {
    async function submitTitle(title: string) {
      const input = container.querySelector('[data-testid="create-title-input"]') as HTMLInputElement;
      await act(async () => {
        const setter = Object.getOwnPropertyDescriptor(dom.window.HTMLInputElement.prototype, "value")?.set;
        setter?.call(input, title);
        input.dispatchEvent(new dom.window.Event("input", { bubbles: true }));
      });
      await act(async () => {
        (container.querySelector('[data-testid="create-title-submit-btn"]') as HTMLButtonElement).click();
        await new Promise((resolve) => setTimeout(resolve, 0));
      });
    }

    it("creates a book from the empty shelf through library_create_book", async () => {
      const createdBook: BookSummary = {
        book_id: "book-created",
        title: "新建作品",
        original_title: "",
        is_favorite: false,
        is_archived: false,
        page_count: null,
        created_at: "2026-10-17T00:00:00Z",
        updated_at: "2026-10-17T00:00:00Z",
      };
      const invoke = vi.fn().mockImplementation((command: string) => {
        if (command === "library_list_books") return Promise.resolve([]);
        if (command === "library_create_book") return Promise.resolve(createdBook);
        if (command === "list_chapters") return Promise.resolve({ chapters: [] });
        if (command === "list_chapter_pages") return Promise.resolve({ pages: [] });
        return Promise.resolve(null);
      });

      await act(async () => {
        root.render(<BookshelfPage client={new LibraryClient(invoke)} />);
        await new Promise((resolve) => setTimeout(resolve, 0));
      });
      const emptyCreate = container.querySelector('[data-testid="empty-new-book-btn"]') as HTMLButtonElement;
      expect(emptyCreate.disabled).toBe(false);
      await act(async () => emptyCreate.click());
      expect(container.querySelector('[data-testid="create-title-dialog"]')).not.toBeNull();
      expect((container.querySelector('[data-testid="create-title-input"]') as HTMLInputElement).maxLength).toBe(-1);

      await submitTitle("新建作品");

      expect(invoke).toHaveBeenCalledWith("library_create_book", { payload: { title: "新建作品" } });
      expect(container.querySelector('[data-testid="book-card-book-created"]')?.textContent).toContain("新建作品");
      expect(container.querySelector('[data-testid="create-title-dialog"]')).toBeNull();
    });

    it("creates a chapter, exposes reader navigation, and enables import for the target chapter", async () => {
      const createdChapter: ChapterNavSummary = {
        chapter_id: "chapter-created",
        title: "第一话",
        chapter_number: "",
        sort_order: 1,
      };
      const invoke = vi.fn().mockImplementation((command: string) => {
        if (command === "list_chapters") return Promise.resolve({ chapters: [] });
        if (command === "list_chapter_pages") return Promise.resolve({ pages: [] });
        if (command === "create_chapter") return Promise.resolve(createdChapter);
        return Promise.resolve(null);
      });
      const onEnterReader = vi.fn();

      await act(async () => {
        root.render(
          <BookshelfPage
            client={new LibraryClient(invoke)}
            initialBooks={[MOCK_BOOKS[0]]}
            onEnterReader={onEnterReader}
          />,
        );
        await new Promise((resolve) => setTimeout(resolve, 0));
      });
      await act(async () => {
        (container.querySelector('[data-testid="new-chapter-btn"]') as HTMLButtonElement).click();
      });
      await submitTitle("第一话");

      expect(invoke).toHaveBeenCalledWith("create_chapter", {
        payload: { book_id: "book-1", title: "第一话" },
      });
      expect(container.querySelector('[data-testid="chapter-item-chapter-created"]')?.textContent).toContain("第一话");
      await act(async () => {
        (container.querySelector('[data-testid="chapter-enter-reader-btn-chapter-created"]') as HTMLButtonElement).click();
      });
      expect(onEnterReader).toHaveBeenCalledWith("book-1", "chapter-created");

      await act(async () => {
        (container.querySelector('[data-testid="toolbar-import-btn"]') as HTMLButtonElement).click();
      });
      expect(container.querySelector('[data-testid="import-unavailable-notice"]')).toBeNull();
      const chapterSelect = container.querySelector('[data-testid="import-target-chapter-select"]') as HTMLSelectElement;
      await act(async () => {
        const setter = Object.getOwnPropertyDescriptor(dom.window.HTMLSelectElement.prototype, "value")?.set;
        setter?.call(chapterSelect, "chapter-created");
        chapterSelect.dispatchEvent(new dom.window.Event("change", { bubbles: true }));
      });
      expect((container.querySelector('[data-testid="import-file-btn"]') as HTMLButtonElement).disabled).toBe(false);
      expect((container.querySelector('[data-testid="import-folder-btn"]') as HTMLButtonElement).disabled).toBe(false);
    });

    it("renders only the fixed creation error copy when the host rejects with private details", async () => {
      const invoke = vi.fn().mockImplementation((command: string) => {
        if (command === "library_create_book") {
          return Promise.reject({
            category: "internal",
            phase: "persistence",
            action: "retry_after_refresh",
            message_key: "LIBRARY_WRITE_FAILED",
            message: "C:\\private\\catalog.sqlite token=secret-value",
            details: { path: "C:\\private\\catalog.sqlite", secret: "secret-value" },
          });
        }
        if (command === "library_list_books") return Promise.resolve([]);
        return Promise.resolve(null);
      });

      await act(async () => root.render(<BookshelfPage client={new LibraryClient(invoke)} initialBooks={[]} />));
      await act(async () => {
        (container.querySelector('[data-testid="empty-new-book-btn"]') as HTMLButtonElement).click();
      });
      await submitTitle("标题");

      const failure = container.querySelector('[data-testid="create-title-error"]');
      expect(failure?.textContent).toContain("保存失败");
      expect(container.textContent).not.toContain("C:\\private");
      expect(container.textContent).not.toContain("secret-value");
      expect(container.textContent).not.toContain("catalog.sqlite");
    });

    it("allows a repeated book title and displays both returned book records", async () => {
      const repeated: BookSummary = { ...MOCK_BOOKS[0], book_id: "book-duplicate" };
      const invoke = vi.fn().mockImplementation((command: string) => {
        if (command === "library_create_book") return Promise.resolve(repeated);
        if (command === "list_chapters") return Promise.resolve({ chapters: [] });
        if (command === "list_chapter_pages") return Promise.resolve({ pages: [] });
        return Promise.resolve(null);
      });

      await act(async () => root.render(<BookshelfPage client={new LibraryClient(invoke)} initialBooks={[MOCK_BOOKS[0]]} />));
      await act(async () => {
        (container.querySelector('[data-testid="toolbar-new-book-btn"]') as HTMLButtonElement).click();
      });
      await submitTitle(MOCK_BOOKS[0].title);

      expect(invoke).toHaveBeenCalledWith("library_create_book", {
        payload: { title: MOCK_BOOKS[0].title },
      });
      expect(container.querySelector('[data-testid="book-card-book-1"]')).not.toBeNull();
      expect(container.querySelector('[data-testid="book-card-book-duplicate"]')).not.toBeNull();
      expect(container.querySelector('[data-testid="create-title-error"]')).toBeNull();
    });

    it("allows a repeated chapter title within the selected book", async () => {
      const duplicateChapter: ChapterNavSummary = {
        chapter_id: "chapter-duplicate",
        title: "重复章节",
        chapter_number: "",
        sort_order: 2,
      };
      const invoke = vi.fn().mockImplementation((command: string) => {
        if (command === "list_chapters") {
          return Promise.resolve({
            chapters: [{ chapter_id: "chapter-existing", title: "重复章节", chapter_number: "", sort_order: 1 }],
          });
        }
        if (command === "list_chapter_pages") return Promise.resolve({ pages: [] });
        if (command === "create_chapter") return Promise.resolve(duplicateChapter);
        return Promise.resolve(null);
      });

      await act(async () => {
        root.render(<BookshelfPage client={new LibraryClient(invoke)} initialBooks={[MOCK_BOOKS[0]]} />);
        await new Promise((resolve) => setTimeout(resolve, 0));
      });
      await act(async () => {
        (container.querySelector('[data-testid="new-chapter-btn"]') as HTMLButtonElement).click();
      });
      await submitTitle("重复章节");

      expect(invoke).toHaveBeenCalledWith("create_chapter", {
        payload: { book_id: "book-1", title: "重复章节" },
      });
      expect(container.querySelector('[data-testid="chapter-item-chapter-existing"]')?.textContent).toContain("重复章节");
      expect(container.querySelector('[data-testid="chapter-item-chapter-duplicate"]')?.textContent).toContain("重复章节");
      expect(container.querySelector('[data-testid="create-title-error"]')).toBeNull();
    });
  });

  // ---- UI-local Search, Filters, and View toggle ----
  describe("UI-local Search & Filters", () => {
    it("filters books by search query", async () => {
      await act(async () => {
        root.render(<BookshelfPage initialBooks={MOCK_BOOKS} />);
      });

      // Search input
      const searchInput = container.querySelector('[data-testid="bookshelf-search-input"]') as HTMLInputElement;
      await act(async () => {
        const setter = Object.getOwnPropertyDescriptor(dom.window.HTMLInputElement.prototype, "value")?.set;
        setter?.call(searchInput, "海贼");
        searchInput.dispatchEvent(new dom.window.Event("input", { bubbles: true }));
      });

      // Should only show One Piece
      expect(container.textContent).toContain("海贼王");
      expect(container.textContent).not.toContain("进击的巨人");
    });

    it("filters books by favorite status", async () => {
      await act(async () => {
        root.render(<BookshelfPage initialBooks={MOCK_BOOKS} />);
      });

      const favBtn = container.querySelector('[data-testid="toolbar-filter-favorite-btn"]') as HTMLButtonElement;
      await act(async () => {
        favBtn.click();
      });

      // Only book-1 is favorite
      expect(container.textContent).toContain("海贼王");
      expect(container.textContent).not.toContain("进击的巨人");
      expect(container.textContent).not.toContain("火影忍者");
    });

    it("toggles between grid and list views", async () => {
      await act(async () => {
        root.render(<BookshelfPage initialBooks={MOCK_BOOKS} />);
      });

      // Default is grid view
      expect(container.querySelector('[data-testid="book-grid-container"]')).not.toBeNull();
      expect(container.querySelector('[data-testid="book-list-container"]')).toBeNull();

      // Click list view toggle
      const listBtn = container.querySelector('[data-testid="toolbar-view-list-btn"]') as HTMLButtonElement;
      await act(async () => {
        listBtn.click();
      });

      expect(container.querySelector('[data-testid="book-grid-container"]')).toBeNull();
      expect(container.querySelector('[data-testid="book-list-container"]')).not.toBeNull();
    });
  });
});
