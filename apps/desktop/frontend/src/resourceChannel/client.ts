/**
 * ResourceChannelClient — the React-side consumer of the `m2res` protocol
 * (M2-RC1). The WebView-visible surface is exactly: an opaque protocol URL
 * (`http://m2res.localhost/m2id/<id>`) and the presentation size. No OS path,
 * no digest, no revision fingerprint, no scope root ever crosses this
 * boundary (Contract 1.1 T5 / §10.2).
 *
 * Chunks are fetched with `?chunk=<n>` (host serves ≤16 MiB per request,
 * T4 resident-buffer rule) and assembled into a Blob for <img> consumption.
 * Typed rejections (Contract §10.2 codes) surface as `TypedChannelError`.
 */

export const CHUNK_SIZE = 16 * 1024 * 1024;

export interface IssuedResource {
  url: string;
  size: number;
  opaqueId: string;
}

export class TypedChannelError extends Error {
  readonly code: string;
  constructor(code: string) {
    super(code);
    this.code = code;
  }
}

export function chunkCount(size: number): number {
  if (size <= 0) return 0;
  return Math.ceil(size / CHUNK_SIZE);
}

export function parseTypedCode(status: number, body: string): string | null {
  if (status >= 200 && status < 300) return null;
  try {
    const parsed = JSON.parse(body) as { code?: string };
    if (typeof parsed.code === "string") return parsed.code;
  } catch {
    // fall through
  }
  return "REF_MALFORMED";
}

type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;
type FetchFn = typeof fetch;

export class ResourceChannelClient {
  // NB: the default fetch is wrapped in an arrow so it keeps its `window`
  // binding — storing bare `fetch` makes every call "Illegal invocation".
  constructor(
    private readonly invoke: InvokeFn,
    private readonly fetchFn: FetchFn = (...args) => fetch(...args),
  ) {}

  /** Ask the host/Core for a fresh opaque reference; never reuse across mounts. */
  async issue(resourceId: string, revision: string): Promise<IssuedResource> {
    const raw = (await this.invoke("issue_resource_url", {
      resourceId,
      revision,
    })) as { url?: string; size?: number; opaque_id?: string };
    if (!raw || typeof raw.url !== "string" || typeof raw.size !== "number") {
      throw new TypedChannelError("REF_MALFORMED");
    }
    return { url: raw.url, size: raw.size, opaqueId: String(raw.opaque_id ?? "") };
  }

  async revoke(opaqueId: string): Promise<void> {
    await this.invoke("revoke_ref", { opaqueId });
  }

  async fetchChunk(url: string, chunk: number): Promise<Uint8Array> {
    const response = await this.fetchFn(`${url}?chunk=${chunk}`);
    if (!response.ok) {
      const text = await response.text();
      throw new TypedChannelError(parseTypedCode(response.status, text) ?? "REF_MALFORMED");
    }
    return new Uint8Array(await response.arrayBuffer());
  }

  async fetchAll(url: string, size: number, fetchFn?: FetchFn): Promise<Blob> {
    const doFetch = fetchFn ?? this.fetchFn;
    const parts: BlobPart[] = [];
    for (let chunk = 0; chunk < chunkCount(size); chunk += 1) {
      const response = await doFetch(`${url}?chunk=${chunk}`);
      if (!response.ok) {
        const text = await response.text();
        throw new TypedChannelError(parseTypedCode(response.status, text) ?? "REF_MALFORMED");
      }
      parts.push(await response.arrayBuffer());
    }
    return new Blob(parts, { type: "application/octet-stream" });
  }
}
