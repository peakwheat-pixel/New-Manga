import type { BookSummary, PingResult } from "./types";

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
}
