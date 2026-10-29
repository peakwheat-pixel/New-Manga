/**
 * M2-AC1 acceptance driver (doc/tasks/M2-AC1.md).
 *
 * Mounted only when the host runs in the explicit test startup
 * configuration (the `ac1_request` probe succeeds). The driver walks the
 * frozen deterministic loop across two REAL process launches against one
 * isolated data root:
 *
 *   launch 1 (phase "empty"):   seed synthetic fixture -> run the Mock/Local
 *     pipeline -> re-read the saved result -> catalog the generated pages
 *     for the m2res protocol -> consume page 1 through the real resource
 *     channel -> write run evidence -> exit the process.
 *   launch 2 (phase "restore"): re-open the SAME data root WITHOUT re-running
 *     the pipeline -> display and turn at least two Reader pages through the
 *     real resource channel -> persist reading progress -> export one PNG ->
 *     write run evidence -> exit.
 *
 * Evidence digests are content-derived only (sha256 of stored/served bytes,
 * never per-run ids), so the runner can compare the two independent samples.
 * Any failure writes its evidence and exits non-zero: the loop never reports
 * a pass it did not earn (AC6 honest gate).
 */

import { ResourceChannelClient } from "../resourceChannel/client";

export type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

export interface Ac1Hooks {
  log: (line: string) => void;
  status: (value: string) => void;
}

export interface ViewedPage {
  index: number;
  sha256: string;
  size: number;
  naturalWidth: number;
}

interface PingResult {
  pid?: number;
  pong?: boolean;
}

interface StatusResult {
  phase?: string;
}

/** The launch decision is made purely from the persisted state of the data
 * root: an empty root means the pipeline launch, anything already complete
 * means the restore launch (no flag, no memory — the restart is real). */
export function decidePhase(status: StatusResult): "run1" | "run2" {
  if (status.phase === "empty") return "run1";
  if (status.phase === "restore") return "run2";
  throw new Error(`AC1_UNKNOWN_PHASE:${String(status.phase)}`);
}

export async function sha256Hex(blob: Blob): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", await blob.arrayBuffer());
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** Decode the assembled bytes as an image so "the page was displayed" is an
 * observed WebView fact (naturalWidth > 0), not an assumption. */
export function decodeToImage(objectUrl: string): Promise<number> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image.naturalWidth);
    image.onerror = () => reject(new Error("AC1_IMAGE_DECODE_FAILED"));
    image.src = objectUrl;
  });
}

async function viewResource(
  client: ResourceChannelClient,
  resourceId: string,
  revision: string,
  index: number,
): Promise<ViewedPage> {
  const issued = await client.issue(resourceId, revision);
  const blob = await client.fetchAll(issued.url, issued.size);
  const naturalWidth = await decodeToImage(URL.createObjectURL(blob));
  if (naturalWidth <= 0) {
    throw new Error("AC1_IMAGE_DECODE_FAILED");
  }
  return { index, sha256: await sha256Hex(blob), size: blob.size, naturalWidth };
}

async function bridgeRequest(
  invoke: InvokeFn,
  method: string,
  params: Record<string, unknown> = {},
): Promise<Record<string, unknown>> {
  return (await invoke("ac1_request", { method, params })) as Record<string, unknown>;
}

export async function startAc1Loop(invoke: InvokeFn, hooks: Ac1Hooks): Promise<void> {
  const client = new ResourceChannelClient(invoke);
  const ping = (await bridgeRequest(invoke, "ping")) as PingResult;
  const corePid = Number(ping.pid ?? -1);
  hooks.log(`ac1 bridge ping ok (core pid ${corePid})`);
  hooks.status(`ac1-core-pid-${corePid}`);

  const status = (await bridgeRequest(invoke, "status")) as StatusResult;
  const phase = decidePhase(status);
  hooks.log(`ac1 phase ${phase} (persisted state decides, no in-memory carry-over)`);

  if (phase === "run1") {
    await runPipelineLaunch(invoke, client, corePid, hooks);
  } else {
    await runRestoreLaunch(invoke, client, corePid, hooks);
  }
}

async function runPipelineLaunch(
  invoke: InvokeFn,
  client: ResourceChannelClient,
  corePid: number,
  hooks: Ac1Hooks,
): Promise<void> {
  hooks.log("ac1 seed_fixture");
  const seed = await bridgeRequest(invoke, "seed_fixture");
  hooks.log(`ac1 seeded ${String(seed.page_count)} pages (real import path)`);

  hooks.log("ac1 run_pipeline (Mock/Local providers, production seam)");
  const run = await bridgeRequest(invoke, "run_pipeline");
  hooks.log(`ac1 pipeline ${String(run.status)}`);

  const saved = await bridgeRequest(invoke, "saved_summary");
  hooks.log("ac1 saved result re-read from SQLite + managed files");

  const cataloged = await bridgeRequest(invoke, "catalog_pages");
  const pages = (cataloged.pages as { index: number; resource_id: string; revision: string }[]) ?? [];

  hooks.log("ac1 consuming page 1 through the m2res protocol");
  const first = pages[0];
  const viewed = [await viewResource(client, first.resource_id, first.revision, first.index)];

  const summary = { phase: "run1", core_pid: corePid, seed, run, saved, viewed };
  await invoke("ac1_write_results", { payload: JSON.stringify(summary) });
  hooks.status("ac1-run1-complete");
  await invoke("ac1_exit", { code: 0 });
}

async function runRestoreLaunch(
  invoke: InvokeFn,
  client: ResourceChannelClient,
  corePid: number,
  hooks: Ac1Hooks,
): Promise<void> {
  hooks.log("ac1 reader_pages (restore from persisted state, no pipeline rerun)");
  const reader = await bridgeRequest(invoke, "reader_pages");
  const pages = (reader.pages as { index: number; resource_id: string; revision: string }[]) ?? [];

  hooks.log(`ac1 reading ${pages.length} pages through the m2res protocol`);
  const viewed: ViewedPage[] = [];
  for (const page of pages) {
    viewed.push(await viewResource(client, page.resource_id, page.revision, page.index));
  }

  const reading = await bridgeRequest(invoke, "record_reading", {
    visited: viewed.map((entry) => entry.index),
  });
  hooks.log(`ac1 reading progress persisted (final page ${String(reading.final_page_index)})`);

  const lastIndex = viewed.length - 1;
  hooks.log(`ac1 exporting page ${lastIndex + 1} as PNG`);
  const exported = await bridgeRequest(invoke, "export_page", { page_index: lastIndex });

  const saved = await bridgeRequest(invoke, "saved_summary");

  const summary = { phase: "run2", core_pid: corePid, reader, viewed, reading, exported, saved };
  await invoke("ac1_write_results", { payload: JSON.stringify(summary) });
  hooks.status("ac1-run2-complete");
  await invoke("ac1_exit", { code: 0 });
}

/** Fail-closed wrapper: any driver error becomes written evidence plus a
 * non-zero process exit, so the runner can only see an honest failure. */
export async function runAc1OrFailClosed(
  invoke: InvokeFn,
  hooks: Ac1Hooks,
  writeResults: (payload: string) => Promise<void>,
  exit: (code: number) => Promise<void>,
): Promise<void> {
  try {
    await startAc1Loop(invoke, hooks);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    hooks.log(`ac1 FAILED: ${detail}`);
    try {
      await writeResults(JSON.stringify({ phase: "failed", error: detail }));
    } catch {
      // the write channel itself is broken; the non-zero exit still speaks
    }
    hooks.status("ac1-failed");
    await exit(1);
  }
}
