import { describe, expect, it, vi } from "vitest";
import { ResourceChannelClient, chunkCount, parseTypedCode } from "./client";

function makeInvoke() {
  const revoked = new Set<string>();
  const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
    if (command === "issue_resource_url") {
      // exact convention: m2id.v1.<43-char segment> (8 + 43 = 51 chars)
      const segment = (Math.random().toString(36).slice(2) + Date.now().toString(36))
        .padEnd(43, "0")
        .slice(0, 43)
        .replace(/[^A-Za-z0-9_-]/g, "0");
      const opaque = `m2id.v1.${segment}`;
      // build_url serves only the 43-char segment in the path, never the
      // prefixed opaque id (R-05)
      return { url: `http://m2res.localhost/m2id/${segment}`, size: 1024, opaque_id: opaque };
    }
    if (command === "revoke_ref") {
      revoked.add(String(args?.opaqueId));
      return null;
    }
    throw new Error(`unexpected command ${command}`);
  });
  return { invoke, revoked };
}

describe("chunkCount", () => {
  it("rounds partial chunks up", () => {
    expect(chunkCount(0)).toBe(0);
    expect(chunkCount(1)).toBe(1);
    expect(chunkCount(16 * 1024 * 1024)).toBe(1);
    expect(chunkCount(16 * 1024 * 1024 + 1)).toBe(2);
  });
});

describe("parseTypedCode", () => {
  it("extracts the stable code from a typed error body", () => {
    expect(parseTypedCode(410, '{"code":"REF_REVOKED"}')).toBe("REF_REVOKED");
  });
  it("returns null for successful statuses", () => {
    expect(parseTypedCode(200, "")).toBeNull();
  });
  it("falls back to REF_MALFORMED when the body is not typed JSON", () => {
    expect(parseTypedCode(500, "boom")).toBe("REF_MALFORMED");
  });
});

describe("ResourceChannelClient", () => {
  it("issues a reference and exposes only the opaque URL and size", async () => {
    const { invoke } = makeInvoke();
    const client = new ResourceChannelClient(invoke);
    const issued = await client.issue("res-001", "rev-1");
    expect(issued.url.startsWith("http://m2res.localhost/m2id/")).toBe(true);
    expect(issued.size).toBe(1024);
    // wire shape pinned: opaque id = "m2id.v1." + 43-char segment (51 chars);
    // the URL path carries only the segment, never the prefixed form (R-05)
    expect(issued.opaqueId).toMatch(/^m2id\.v1\.[A-Za-z0-9_-]{43}$/);
    expect(issued.opaqueId.length).toBe(51);
    expect(issued.url.slice("http://m2res.localhost/m2id/".length)).toMatch(
      /^[A-Za-z0-9_-]{43}$/,
    );
    // no path/digest/revision fingerprint ever crosses the WebView boundary
    expect(JSON.stringify(issued)).not.toMatch(/C:\\|asset\.png|sha256|rev-1/);
  });

  it("fetches all chunks and assembles the blob", async () => {
    const { invoke } = makeInvoke();
    const client = new ResourceChannelClient(invoke);
    const issued = await client.issue("res-001", "rev-1");
    const fetchMock = vi.fn(async (url: string) => {
      expect(url.startsWith(issued.url)).toBe(true);
      return new Response(new Uint8Array(1024), { status: 200 });
    });
    const progress: [number, number][] = [];
    const blob = await client.fetchAll(issued.url, issued.size, fetchMock as unknown as typeof fetch, (loaded, total) => progress.push([loaded, total]));
    expect(blob.size).toBe(1024);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(progress).toEqual([[0, 1], [1, 1]]);
  });

  it("surfaces typed rejection codes from the protocol", async () => {
    const { invoke } = makeInvoke();
    const client = new ResourceChannelClient(invoke);
    const issued = await client.issue("res-001", "rev-1");
    await client.revoke(issued.opaqueId);
    const fetchMock = vi.fn(async () =>
      new Response('{"code":"REF_REVOKED"}', { status: 410 })
    );
    await expect(
      client.fetchAll(issued.url, issued.size, fetchMock as unknown as typeof fetch)
    ).rejects.toMatchObject({ code: "REF_REVOKED" });
  });

  it("never reuses a stale URL after remount (fresh issue per mount)", async () => {
    const { invoke } = makeInvoke();
    const client = new ResourceChannelClient(invoke);
    const first = await client.issue("res-001", "rev-1");
    const second = await client.issue("res-001", "rev-1");
    expect(first.opaqueId).not.toBe(second.opaqueId);
    expect(first.url).not.toBe(second.url);
  });
});
