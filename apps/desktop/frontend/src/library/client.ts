import type { BookSummary, PageResourceResolve, PingResult } from "./types";

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

export class LibraryClient {
  private invoke: InvokeFn;

  constructor(invoke?: InvokeFn) {
    this.invoke = invoke || getTauriInvoke();
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
      return res as BookSummary[];
    } catch (error) {
      const code = typeof error === "string" ? error : (error as Error)?.message || "CORE_UNAVAILABLE";
      throw new LibraryClientError(code, `library_list_books failed: ${code}`);
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
}
