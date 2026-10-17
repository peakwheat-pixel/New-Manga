import { describe, expect, it, vi } from "vitest";
import {
  LibraryClient,
  LibraryClientError,
  LIST_CHAPTERS_COMMAND,
  LIST_CHAPTER_PAGES_COMMAND,
  RESOLVE_PAGE_RESOURCE_COMMAND,
  LIBRARY_CREATE_BOOK_COMMAND,
  CREATE_CHAPTER_COMMAND,
} from "./client";
import type { BookSummary, PingResult } from "./types";

describe("LibraryClient", () => {
  it("calls core_ping and returns PingResult", async () => {
    const mockPingResult: PingResult = {
      status: "ready",
      protocol_version: { major: 1, minor: 0 },
      capabilities: ["library.list_books"],
    };
    const invoke = vi.fn().mockResolvedValue(mockPingResult);
    const client = new LibraryClient(invoke);

    const result = await client.corePing();
    expect(invoke).toHaveBeenCalledWith("core_ping");
    expect(result.status).toBe("ready");
    expect(result.protocol_version.major).toBe(1);
    expect(result.capabilities).toContain("library.list_books");
  });

  it("calls library_list_books and returns BookSummary array", async () => {
    const mockBooks: BookSummary[] = [
      {
        book_id: "book-1",
        title: "Test Manga",
        original_title: "テスト漫画",
        is_favorite: true,
        is_archived: false,
        page_count: 10,
        created_at: "2026-09-28T12:00:00Z",
        updated_at: "2026-09-28T12:00:00Z",
      },
    ];
    const invoke = vi.fn().mockResolvedValue(mockBooks);
    const client = new LibraryClient(invoke);

    const books = await client.listBooks();
    expect(invoke).toHaveBeenCalledWith("library_list_books");
    expect(books).toHaveLength(1);
    expect(books[0].book_id).toBe("book-1");
    expect(books[0].title).toBe("Test Manga");
    expect(books[0].page_count).toBe(10);
  });

  it("uses the frozen book and chapter create commands with closed payloads", async () => {
    expect(LIBRARY_CREATE_BOOK_COMMAND).toBe("library_create_book");
    expect(CREATE_CHAPTER_COMMAND).toBe("create_chapter");
    const createdBook = {
      book_id: "book-new",
      title: "新作",
      original_title: "",
      is_favorite: false,
      is_archived: false,
      page_count: null,
      created_at: "2026-10-17T00:00:00Z",
      updated_at: "2026-10-17T00:00:00Z",
    };
    const createdChapter = {
      chapter_id: "chapter-new",
      title: "第一话",
      chapter_number: "",
      sort_order: 1,
    };
    const invoke = vi.fn().mockResolvedValueOnce(createdBook).mockResolvedValueOnce(createdChapter);
    const client = new LibraryClient(invoke);

    await expect(client.createBook("新作")).resolves.toEqual(createdBook);
    expect(invoke).toHaveBeenNthCalledWith(1, "library_create_book", { payload: { title: "新作" } });
    await expect(client.createChapter("book-new", "第一话")).resolves.toEqual(createdChapter);
    expect(invoke).toHaveBeenNthCalledWith(2, "create_chapter", {
      payload: { book_id: "book-new", title: "第一话" },
    });
  });

  it("keeps creation failures on the closed message-key projection", async () => {
    const invoke = vi.fn().mockRejectedValue({
      category: "internal",
      phase: "persistence",
      action: "retry_after_refresh",
      message_key: "LIBRARY_WRITE_FAILED",
      details: { path: "C:\\private\\catalog.sqlite", secret: "token-value" },
    });
    const client = new LibraryClient(invoke);

    const failure = await client.createBook("标题").catch((error) => error);
    expect(failure).toMatchObject({ code: "LIBRARY_WRITE_FAILED", message: "LIBRARY_WRITE_FAILED" });
    expect(failure.message).not.toContain("private");
    expect(failure.message).not.toContain("token-value");
  });

  it("propagates CORE_UNAVAILABLE as LibraryClientError", async () => {
    const invoke = vi.fn().mockRejectedValue("CORE_UNAVAILABLE");
    const client = new LibraryClient(invoke);

    await expect(client.listBooks()).rejects.toThrow(LibraryClientError);
    await expect(client.listBooks()).rejects.toMatchObject({
      code: "CORE_UNAVAILABLE",
    });
  });

  it("handles general error and extracts code", async () => {
    const invoke = vi.fn().mockRejectedValue(new Error("PROTOCOL_VERSION_UNSUPPORTED"));
    const client = new LibraryClient(invoke);

    await expect(client.corePing()).rejects.toMatchObject({
      code: "PROTOCOL_VERSION_UNSUPPORTED",
    });
  });

  it("pins the resolve wire name and round-trips the page id (M2-PAGE-RESOURCE-RESOLVE-1)", async () => {
    // DSH r1 PR-02: the ruled wire name is an asserted constant, not a
    // literal that matches only by convention (commandSurface pins the
    // production-only literal list; this pins the client constant to the
    // same contract rev 1.7 §5 wire name).
    expect(RESOLVE_PAGE_RESOURCE_COMMAND).toBe("resolve_page_resource");
    const invoke = vi.fn().mockResolvedValue({
      resource_id: "page-original-p1",
      revision: "original",
    });
    const client = new LibraryClient(invoke);

    const result = await client.resolvePageResource("p1");
    expect(invoke).toHaveBeenCalledWith("resolve_page_resource", { pageId: "p1" });
    expect(result).toEqual({ resource_id: "page-original-p1", revision: "original" });
  });

  it("rejects a malformed resolve payload as PAGE_RESOURCE_MALFORMED", async () => {
    // DSH r1 PR-02: both malformed shapes -- field of the wrong type and a
    // non-object result -- must surface as the typed malformed code.
    const badField = vi.fn().mockResolvedValue({ resource_id: 7, revision: "original" });
    await expect(new LibraryClient(badField).resolvePageResource("p1")).rejects.toMatchObject({
      code: "PAGE_RESOURCE_MALFORMED",
    });

    const notAnObject = vi.fn().mockResolvedValue(null);
    await expect(new LibraryClient(notAnObject).resolvePageResource("p1")).rejects.toMatchObject({
      code: "PAGE_RESOURCE_MALFORMED",
    });
  });

  it("passes a typed resolve failure through unwrapped (Tauri rejects with a bare string)", async () => {
    // The real Tauri invoke rejects Core's error code as a bare string;
    // the client must wrap it into the typed code, never the generic
    // CORE_UNAVAILABLE fallback (DSH r1 PR-02).
    const invoke = vi.fn().mockRejectedValue("PAGE_NOT_FOUND");
    const client = new LibraryClient(invoke);

    await expect(client.resolvePageResource("no-such-page")).rejects.toMatchObject({
      code: "PAGE_NOT_FOUND",
    });
    await expect(client.resolvePageResource("no-such-page")).rejects.toBeInstanceOf(
      LibraryClientError,
    );
  });

  it("pins the navigation wire names and round-trips the parent ids (M2-PAGE-NAV-PROJECTION-1)", async () => {
    // The ruled wire names are asserted constants, not literals that match
    // only by convention (contract M2-C1 rev 1.8 §5; the Rust suite pins
    // the production-only list on the same names).
    expect(LIST_CHAPTERS_COMMAND).toBe("list_chapters");
    expect(LIST_CHAPTER_PAGES_COMMAND).toBe("list_chapter_pages");

    const invoke = vi.fn()
      .mockResolvedValueOnce({
        chapters: [
          { chapter_id: "ch-1", title: "Vol. 1", chapter_number: "1", sort_order: 1 },
        ],
      })
      .mockResolvedValueOnce({
        pages: [
          { page_id: "p-1", source_filename: "001.png", sort_order: 1 },
        ],
      });
    const client = new LibraryClient(invoke);

    const chapters = await client.listChapters("book-1");
    expect(invoke).toHaveBeenCalledWith("list_chapters", { bookId: "book-1" });
    expect(chapters).toEqual([
      { chapter_id: "ch-1", title: "Vol. 1", chapter_number: "1", sort_order: 1 },
    ]);

    const pages = await client.listChapterPages("ch-1");
    expect(invoke).toHaveBeenCalledWith("list_chapter_pages", { chapterId: "ch-1" });
    expect(pages).toEqual([{ page_id: "p-1", source_filename: "001.png", sort_order: 1 }]);
  });

  it("rejects a malformed navigation payload as PAGE_NAV_MALFORMED", async () => {
    // Both malformed shapes per method -- a non-object result and a result
    // without the wrapped array -- must surface as the typed malformed
    // code, never as an implicit undefined list.
    const client = new LibraryClient(vi.fn().mockResolvedValue(null));
    await expect(client.listChapters("book-1")).rejects.toMatchObject({
      code: "PAGE_NAV_MALFORMED",
    });
    await expect(client.listChapterPages("ch-1")).rejects.toMatchObject({
      code: "PAGE_NAV_MALFORMED",
    });

    const missingArray = new LibraryClient(vi.fn().mockResolvedValue({}));
    await expect(missingArray.listChapters("book-1")).rejects.toMatchObject({
      code: "PAGE_NAV_MALFORMED",
    });
    await expect(missingArray.listChapterPages("ch-1")).rejects.toMatchObject({
      code: "PAGE_NAV_MALFORMED",
    });
  });

  it("passes navigation failures through unwrapped (an empty list is data, a rejection is a code)", async () => {
    // The fail-soft empty list lives on the Core side (unknown parent id);
    // a rejection here is a real transport/Core failure and keeps its code.
    const invoke = vi.fn().mockRejectedValue("CORE_UNAVAILABLE");
    const client = new LibraryClient(invoke);

    await expect(client.listChapters("book-1")).rejects.toMatchObject({
      code: "CORE_UNAVAILABLE",
    });
    await expect(client.listChapterPages("ch-1")).rejects.toBeInstanceOf(LibraryClientError);
  });

  it("calls library_import_file and returns ImportSummary", async () => {
    const mockSummary = {
      chapter_id: "ch-1",
      cancelled: false,
      imported_files: 5,
      skipped_files: 1,
      rejected_files: 0,
      pending_files: 0,
    };
    const invoke = vi.fn().mockResolvedValue(mockSummary);
    const client = new LibraryClient(invoke);

    const summary = await client.importFile("ch-1", "skip");
    expect(invoke).toHaveBeenCalledWith("library_import_file", {
      chapterId: "ch-1",
      duplicatePolicy: "skip",
    });
    expect(summary).toEqual(mockSummary);
    expect(summary.cancelled).toBe(false);
    expect(summary.imported_files).toBe(5);
  });

  it("handles cancelled library_import_file", async () => {
    const cancelledSummary = {
      chapter_id: "ch-1",
      cancelled: true,
      imported_files: 0,
      skipped_files: 0,
      rejected_files: 0,
      pending_files: 0,
    };
    const invoke = vi.fn().mockResolvedValue(cancelledSummary);
    const client = new LibraryClient(invoke);

    const summary = await client.importFile("ch-1");
    expect(invoke).toHaveBeenCalledWith("library_import_file", {
      chapterId: "ch-1",
      duplicatePolicy: "skip",
    });
    expect(summary.cancelled).toBe(true);
  });

  it("calls library_import_folder and returns ImportSummary", async () => {
    const mockSummary = {
      chapter_id: "ch-1",
      cancelled: false,
      imported_files: 12,
      skipped_files: 2,
      rejected_files: 1,
      pending_files: 0,
    };
    const invoke = vi.fn().mockResolvedValue(mockSummary);
    const client = new LibraryClient(invoke);

    const summary = await client.importFolder("ch-1", "import_as_new");
    expect(invoke).toHaveBeenCalledWith("library_import_folder", {
      chapterId: "ch-1",
      duplicatePolicy: "import_as_new",
    });
    expect(summary).toEqual(mockSummary);
  });

  it("rejects malformed import report payload", async () => {
    const badClient = new LibraryClient(vi.fn().mockResolvedValue(null));
    await expect(badClient.importFile("ch-1")).rejects.toMatchObject({
      code: "IMPORT_REPORT_MALFORMED",
    });
    await expect(badClient.importFolder("ch-1")).rejects.toMatchObject({
      code: "IMPORT_REPORT_MALFORMED",
    });
  });
});
