import { describe, expect, it, vi } from "vitest";
import { LibraryClient, LibraryClientError, RESOLVE_PAGE_RESOURCE_COMMAND } from "./client";
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
});
