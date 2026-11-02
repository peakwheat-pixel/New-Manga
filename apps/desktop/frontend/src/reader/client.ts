/**
 * Client for READER-IPC-1 (contract M2-C1 rev 2.1 §5 / §6.3)
 * Commands:
 * - library_get_reader_projection
 * - library_save_reading_progress
 */

import type {
  ReaderProjection,
  ReaderStartPosition,
  ReadingMode,
  ReadingProgressSnapshot,
  SaveReadingProgressParams,
} from "./types";

export type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

function getTauriInvoke(): InvokeFn {
  const globalWindow = typeof window !== "undefined"
    ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } })
    : undefined;
  const invoke = globalWindow?.__TAURI__?.core?.invoke;
  if (!invoke) {
    throw new Error("TAURI_BRIDGE_MISSING");
  }
  return invoke;
}

export class ReaderClientError extends Error {
  readonly code: string;

  constructor(code: string, message?: string) {
    super(message || code);
    this.name = "ReaderClientError";
    this.code = code;
  }
}

export const GET_READER_PROJECTION_COMMAND = "library_get_reader_projection";
export const SAVE_READING_PROGRESS_COMMAND = "library_save_reading_progress";

export class ReaderClient {
  private readonly invoke: InvokeFn;

  constructor(invoke?: InvokeFn) {
    if (invoke) {
      this.invoke = invoke;
    } else {
      try {
        this.invoke = getTauriInvoke();
      } catch {
        this.invoke = () => Promise.reject(new ReaderClientError("TAURI_BRIDGE_MISSING", "Tauri bridge is missing"));
      }
    }
  }

  /**
   * Retrieves the reader projection for a chapter.
   * start_position="resume" restores saved position for (book, chapter, mode).
   * start_position="beginning" starts at page 1 / offset 0 WITHOUT mutating saved progress.
   */
  async getReaderProjection(
    chapterId: string,
    mode: ReadingMode = "original",
    startPosition: ReaderStartPosition = "resume",
  ): Promise<ReaderProjection> {
    try {
      const res = (await this.invoke(GET_READER_PROJECTION_COMMAND, {
        chapterId,
        mode,
        startPosition,
      })) as ReaderProjection;

      if (!res || !Array.isArray(res.pages) || !res.layout || !res.initial_position) {
        throw new ReaderClientError("READER_PROJECTION_MALFORMED", "get_reader_projection returned malformed payload");
      }
      return res;
    } catch (error) {
      if (error instanceof ReaderClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new ReaderClientError(code, `get_reader_projection failed: ${code}`);
    }
  }

  /**
   * Persists reading progress for (book, chapter, mode).
   * CRITICAL DISCIPLINE:
   * - elapsed_seconds_delta is omitted from payload if not provided or undefined (MISSING = NOT SENT).
   * - Webtoon offset uses logical Page original image pixel coordinate.
   */
  async saveReadingProgress(params: SaveReadingProgressParams): Promise<ReadingProgressSnapshot> {
    const { chapterId, mode, pageId, scrollOffsetY, elapsedSecondsDelta } = params;

    const payload: Record<string, unknown> = {
      chapterId,
      mode,
      pageId,
    };

    if (scrollOffsetY !== undefined && scrollOffsetY !== null && Number.isFinite(scrollOffsetY)) {
      payload.scrollOffsetY = scrollOffsetY;
    }

    if (elapsedSecondsDelta !== undefined && elapsedSecondsDelta !== null && Number.isFinite(elapsedSecondsDelta) && elapsedSecondsDelta > 0) {
      payload.elapsedSecondsDelta = elapsedSecondsDelta;
    }

    try {
      const res = (await this.invoke(SAVE_READING_PROGRESS_COMMAND, payload)) as ReadingProgressSnapshot;
      if (!res || typeof res.progress_percent !== "number") {
        throw new ReaderClientError("READING_PROGRESS_MALFORMED", "save_reading_progress returned malformed payload");
      }
      return res;
    } catch (error) {
      if (error instanceof ReaderClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new ReaderClientError(code, `save_reading_progress failed: ${code}`);
    }
  }
}
