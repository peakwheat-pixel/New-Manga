import { describe, expect, it, vi } from "vitest";
import {
  GET_READER_PROJECTION_COMMAND,
  ReaderClient,
  ReaderClientError,
  SAVE_READING_PROGRESS_COMMAND,
} from "./client";
import type { ReaderProjection, ReadingProgressSnapshot } from "./types";

describe("ReaderClient (W18 / W19)", () => {
  it("has exact command names matching host permissions", () => {
    expect(GET_READER_PROJECTION_COMMAND).toBe("library_get_reader_projection");
    expect(SAVE_READING_PROGRESS_COMMAND).toBe("library_save_reading_progress");
  });

  describe("getReaderProjection (W18)", () => {
    it("invokes library_get_reader_projection with chapterId, mode, and startPosition", async () => {
      const mockProjection: ReaderProjection = {
        book_id: "book-1",
        chapter_id: "chap-1",
        mode: "original",
        layout: "rtl",
        pages: [
          {
            page_id: "p1",
            order: 0,
            width_px: 800,
            height_px: 1200,
            original: { resource_ref: { resource_id: "res-1", revision: "original" }, artifact_revision_id: "rev-1", sha256: "a".repeat(64) },
            translated: { resource_ref: null, artifact_revision_id: null, rendered_from_revision_id: null, current_source_revision_id: null, sha256: null },
          },
        ],
        saved_progress: null,
        initial_position: { page_id: "p1", scroll_offset_y: 0 },
      };

      const invoke = vi.fn().mockResolvedValue(mockProjection);
      const client = new ReaderClient(invoke);

      const result = await client.getReaderProjection("chap-1", "translated", "beginning");

      expect(invoke).toHaveBeenCalledWith("library_get_reader_projection", {
        chapterId: "chap-1",
        mode: "translated",
        startPosition: "beginning",
      });
      expect(result).toEqual(mockProjection);
    });

    it("defaults to mode=original and startPosition=resume", async () => {
      const mockProjection: ReaderProjection = {
        book_id: "book-1",
        chapter_id: "chap-1",
        mode: "original",
        layout: "ltr",
        pages: [],
        saved_progress: null,
        initial_position: { page_id: "p1", scroll_offset_y: 0 },
      };

      const invoke = vi.fn().mockResolvedValue(mockProjection);
      const client = new ReaderClient(invoke);

      await client.getReaderProjection("chap-1");

      expect(invoke).toHaveBeenCalledWith("library_get_reader_projection", {
        chapterId: "chap-1",
        mode: "original",
        startPosition: "resume",
      });
    });

    it("wraps transport errors into ReaderClientError", async () => {
      const invoke = vi.fn().mockRejectedValue("TARGET_NOT_FOUND");
      const client = new ReaderClient(invoke);

      await expect(client.getReaderProjection("non-existent")).rejects.toThrowError(ReaderClientError);
      await expect(client.getReaderProjection("non-existent")).rejects.toMatchObject({
        code: "TARGET_NOT_FOUND",
      });
    });
  });

  describe("saveReadingProgress (W19)", () => {
    it("omits elapsed_seconds_delta when missing or undefined (AC2 contract red line)", async () => {
      const mockSnapshot: ReadingProgressSnapshot = {
        book_id: "book-1",
        chapter_id: "chap-1",
        mode: "original",
        last_page_id: "p2",
        scroll_offset_y: 0,
        progress_percent: 50,
        last_read_at: "2026-10-16T12:00:00Z",
        total_read_seconds: 120,
      };

      const invoke = vi.fn().mockResolvedValue(mockSnapshot);
      const client = new ReaderClient(invoke);

      await client.saveReadingProgress({
        chapterId: "chap-1",
        mode: "original",
        pageId: "p2",
        scrollOffsetY: 0,
        // elapsedSecondsDelta omitted!
      });

      expect(invoke).toHaveBeenCalledWith("library_save_reading_progress", {
        chapterId: "chap-1",
        mode: "original",
        pageId: "p2",
        scrollOffsetY: 0,
      });

      const calledPayload = invoke.mock.calls[0][1];
      expect(calledPayload).not.toHaveProperty("elapsedSecondsDelta");
    });

    it("includes elapsed_seconds_delta when positive finite number is provided", async () => {
      const mockSnapshot: ReadingProgressSnapshot = {
        book_id: "book-1",
        chapter_id: "chap-1",
        mode: "translated",
        last_page_id: "p1",
        scroll_offset_y: 450,
        progress_percent: 30,
        last_read_at: "2026-10-16T12:00:00Z",
        total_read_seconds: 15,
      };

      const invoke = vi.fn().mockResolvedValue(mockSnapshot);
      const client = new ReaderClient(invoke);

      await client.saveReadingProgress({
        chapterId: "chap-1",
        mode: "translated",
        pageId: "p1",
        scrollOffsetY: 450,
        elapsedSecondsDelta: 15.5,
      });

      expect(invoke).toHaveBeenCalledWith("library_save_reading_progress", {
        chapterId: "chap-1",
        mode: "translated",
        pageId: "p1",
        scrollOffsetY: 450,
        elapsedSecondsDelta: 15.5,
      });
    });
  });
});
