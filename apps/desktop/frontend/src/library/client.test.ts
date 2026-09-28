import { describe, expect, it, vi } from "vitest";
import { LibraryClient, LibraryClientError } from "./client";
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
});
