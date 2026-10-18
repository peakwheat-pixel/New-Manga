import type {
  BookSummary,
  ChapterNavSummary,
  ImportSummary,
  PageNavSummary,
  PageResourceResolve,
  PermanentlyDeleteBookPayload,
  PermanentlyDeleteBookResult,
  PermanentlyDeleteBooksPayload,
  PermanentlyDeleteBooksResult,
  PingResult,
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

export class LibraryClientError extends Error {
  code: string;

  constructor(code: string, message?: string) {
    super(message || code);
    this.name = "LibraryClientError";
    this.code = code;
  }
}

/** RULED wire name (contract M2-C1 rev 1.7 §5; pinned by the Rust suite). */
export const RESOLVE_PAGE_RESOURCE_COMMAND = "resolve_page_resource";

/**
 * RULED wire names (contract M2-C1 rev 1.8 §5; pinned by the Rust suite):
 * the read-only page navigation projections (M2-PAGE-NAV-PROJECTION-1).
 */
export const LIST_CHAPTERS_COMMAND = "list_chapters";
export const LIST_CHAPTER_PAGES_COMMAND = "list_chapter_pages";
export const LIBRARY_CREATE_BOOK_COMMAND = "library_create_book";
export const CREATE_CHAPTER_COMMAND = "create_chapter";

/**
 * HOST-ISSUER-1 wire names (AD-001 §6 W30):
 * User actions via native pickers. Paths and raw references stay in Rust.
 */
export const LIBRARY_IMPORT_FILE_COMMAND = "library_import_file";
export const LIBRARY_IMPORT_FOLDER_COMMAND = "library_import_folder";

/**
 * P09-AC3-DELETE-1 wire names (contract M2-C1 rev 2.10 §5.11).
 */
export const LIBRARY_DELETE_BOOK_PERMANENTLY_COMMAND = "library_delete_book_permanently";
export const LIBRARY_DELETE_BOOKS_PERMANENTLY_COMMAND = "library_delete_books_permanently";
export const LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND = "library_list_recycle_bin_books";

const CREATE_ERROR_KEYS = [
  "LIBRARY_INVALID_INPUT",
  "LIBRARY_BOOK_NOT_FOUND",
  "LIBRARY_WRITE_FAILED",
  "LIBRARY_UNAVAILABLE",
  "LIBRARY_OPERATION_FAILED",
] as const;

function createErrorCode(error: unknown): string {
  const value = error && typeof error === "object"
    ? (error as { message_key?: unknown; code?: unknown }).message_key ?? (error as { code?: unknown }).code
    : error;
  if (typeof value === "string" && CREATE_ERROR_KEYS.includes(value as (typeof CREATE_ERROR_KEYS)[number])) {
    return value;
  }
  if (value === "INVALID_REQUEST") return "LIBRARY_INVALID_INPUT";
  if (value === "TARGET_NOT_FOUND") return "LIBRARY_BOOK_NOT_FOUND";
  if (value === "CORE_UNAVAILABLE" || value === "TAURI_BRIDGE_MISSING") return "LIBRARY_UNAVAILABLE";
  if (value === "LIBRARY_WRITE_FAILED") return value;
  return "LIBRARY_OPERATION_FAILED";
}

export class LibraryClient {
  private invoke: InvokeFn;

  constructor(invoke?: InvokeFn) {
    if (invoke) {
      this.invoke = invoke;
    } else {
      try {
        this.invoke = getTauriInvoke();
      } catch {
        this.invoke = () => Promise.reject(new LibraryClientError("TAURI_BRIDGE_MISSING", "Tauri bridge is missing"));
      }
    }
  }

  async corePing(): Promise<PingResult> {
    try {
      const res = await this.invoke("core_ping");
      return res as PingResult;
    } catch (error) {
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `core_ping failed: ${code}`);
    }
  }

  async listBooks(): Promise<BookSummary[]> {
    try {
      const res = await this.invoke("library_list_books");
      return Array.isArray(res) ? (res as BookSummary[]) : [];
    } catch (error) {
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `library_list_books failed: ${code}`);
    }
  }

  async listRecycleBinBooks(): Promise<BookSummary[]> {
    try {
      const res = await this.invoke(LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND);
      return Array.isArray(res) ? (res as BookSummary[]) : [];
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `library_list_recycle_bin_books failed: ${code}`);
    }
  }

  async createBook(title: string): Promise<BookSummary> {
    try {
      const result = await this.invoke(LIBRARY_CREATE_BOOK_COMMAND, { payload: { title } });
      if (!result || typeof result !== "object" || typeof (result as BookSummary).book_id !== "string") {
        throw new LibraryClientError("LIBRARY_OPERATION_FAILED");
      }
      return result as BookSummary;
    } catch (error) {
      throw new LibraryClientError(createErrorCode(error));
    }
  }

  async createChapter(bookId: string, title: string): Promise<ChapterNavSummary> {
    try {
      const result = await this.invoke(CREATE_CHAPTER_COMMAND, {
        payload: { book_id: bookId, title },
      });
      if (!result || typeof result !== "object" || typeof (result as ChapterNavSummary).chapter_id !== "string") {
        throw new LibraryClientError("LIBRARY_OPERATION_FAILED");
      }
      return result as ChapterNavSummary;
    } catch (error) {
      throw new LibraryClientError(createErrorCode(error));
    }
  }

  /**
   * M2-PAGE-RESOURCE-RESOLVE-1 (contract M2-C1 rev 1.7 §5): resolve one
   * page's immutable managed original to its servable resource catalog key.
   * An unknown page (or one without a managed original) rejects with the
   * typed PAGE_NOT_FOUND code -- the caller keeps the manual fallback.
   */
  async resolvePageResource(pageId: string): Promise<PageResourceResolve> {
    try {
      const res = (await this.invoke(RESOLVE_PAGE_RESOURCE_COMMAND, {
        pageId,
      })) as PageResourceResolve;
      if (!res || typeof res.resource_id !== "string" || typeof res.revision !== "string") {
        throw new LibraryClientError(
          "PAGE_RESOURCE_MALFORMED",
          "resolve_page_resource returned no {resource_id, revision} pair",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `resolve_page_resource failed: ${code}`);
    }
  }

  /**
   * M2-PAGE-NAV-PROJECTION-1 (contract M2-C1 rev 1.8 §5): one book's
   * chapter navigation summaries in the user's current sort order. An
   * unknown book id resolves to an EMPTY list (fail-soft; no new error
   * code) -- only a transport/Core failure rejects here.
   */
  async listChapters(bookId: string): Promise<ChapterNavSummary[]> {
    try {
      const res = (await this.invoke(LIST_CHAPTERS_COMMAND, { bookId })) as {
        chapters?: unknown;
      };
      if (!res || !Array.isArray(res.chapters)) {
        throw new LibraryClientError(
          "PAGE_NAV_MALFORMED",
          "list_chapters returned no {chapters} array",
        );
      }
      return res.chapters as ChapterNavSummary[];
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `list_chapters failed: ${code}`);
    }
  }

  /**
   * M2-PAGE-NAV-PROJECTION-1 (contract M2-C1 rev 1.8 §5): one chapter's
   * committed page navigation summaries in the user's current sort order.
   * Same fail-soft contract as listChapters: an unknown chapter id is an
   * empty list, not an error.
   */
  async listChapterPages(chapterId: string): Promise<PageNavSummary[]> {
    try {
      const res = (await this.invoke(LIST_CHAPTER_PAGES_COMMAND, { chapterId })) as {
        pages?: unknown;
      };
      if (!res || !Array.isArray(res.pages)) {
        throw new LibraryClientError(
          "PAGE_NAV_MALFORMED",
          "list_chapter_pages returned no {pages} array",
        );
      }
      return res.pages as PageNavSummary[];
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `list_chapter_pages failed: ${code}`);
    }
  }

  /**
   * HOST-ISSUER-1 (AD-001 §6 W30): import a single file (image or PDF) into a chapter.
   * Host Rust launches the native file picker; WebView never touches OS paths.
   * If user cancels the picker, returns an ImportSummary with `cancelled: true`.
   */
  async importFile(
    chapterId: string,
    duplicatePolicy: "skip" | "import_as_new" = "skip",
  ): Promise<ImportSummary> {
    try {
      const res = (await this.invoke(LIBRARY_IMPORT_FILE_COMMAND, {
        chapterId,
        duplicatePolicy,
      })) as ImportSummary;
      if (!res || typeof res.cancelled !== "boolean") {
        throw new LibraryClientError(
          "IMPORT_REPORT_MALFORMED",
          "library_import_file returned malformed summary",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `library_import_file failed: ${code}`);
    }
  }

  /**
   * HOST-ISSUER-1 (AD-001 §6 W30): import a folder of images into a chapter.
   * Host Rust launches the native folder picker; WebView never touches OS paths.
   * If user cancels the picker, returns an ImportSummary with `cancelled: true`.
   */
  async importFolder(
    chapterId: string,
    duplicatePolicy: "skip" | "import_as_new" = "skip",
  ): Promise<ImportSummary> {
    try {
      const res = (await this.invoke(LIBRARY_IMPORT_FOLDER_COMMAND, {
        chapterId,
        duplicatePolicy,
      })) as ImportSummary;
      if (!res || typeof res.cancelled !== "boolean") {
        throw new LibraryClientError(
          "IMPORT_REPORT_MALFORMED",
          "library_import_folder returned malformed summary",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `library_import_folder failed: ${code}`);
    }
  }

  /**
   * P09-AC3-DELETE-1 (contract M2-C1 rev 2.10 §5.11): permanently delete a single book.
   */
  async deleteBookPermanently(
    payload: PermanentlyDeleteBookPayload,
  ): Promise<PermanentlyDeleteBookResult> {
    try {
      const res = (await this.invoke(LIBRARY_DELETE_BOOK_PERMANENTLY_COMMAND, {
        payload,
      })) as PermanentlyDeleteBookResult;
      if (!res || typeof res.deleted !== "boolean" || typeof res.book_id !== "string") {
        throw new LibraryClientError(
          "LIBRARY_OPERATION_FAILED",
          "library_delete_book_permanently returned malformed result",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code =
        typeof error === "string"
          ? error
          : (error as { code?: string })?.code ||
            (error as Error)?.message ||
            "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `library_delete_book_permanently failed: ${code}`);
    }
  }

  /**
   * P09-AC3-DELETE-1 (contract M2-C1 rev 2.10 §5.11): permanently delete multiple books (1..20).
   */
  async deleteBooksPermanently(
    payload: PermanentlyDeleteBooksPayload,
  ): Promise<PermanentlyDeleteBooksResult> {
    try {
      const res = (await this.invoke(LIBRARY_DELETE_BOOKS_PERMANENTLY_COMMAND, {
        payload,
      })) as PermanentlyDeleteBooksResult;
      if (
        !res ||
        typeof res.requested_count !== "number" ||
        typeof res.completed_count !== "number" ||
        !Array.isArray(res.items)
      ) {
        throw new LibraryClientError(
          "LIBRARY_OPERATION_FAILED",
          "library_delete_books_permanently returned malformed result",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof LibraryClientError) {
        throw error;
      }
      const code =
        typeof error === "string"
          ? error
          : (error as { code?: string })?.code ||
            (error as Error)?.message ||
            "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `library_delete_books_permanently failed: ${code}`);
    }
  }
}

