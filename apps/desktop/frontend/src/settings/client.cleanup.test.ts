import { describe, expect, it, vi } from "vitest";
import {
  CLEANUP_PREVIEW_COMMAND,
  CLEANUP_RETRY_PENDING_COMMAND,
  CLEANUP_RUN_COMMAND,
  SettingsClient,
  SettingsClientError,
} from "./client";

/**
 * SETTINGS-OPEN-B-2 §4.3 — the cleanup wire surface. These tests pin the
 * payload-free command names and the defensive projection parsing: the UI
 * accepts the frozen items/counts shape AND the Python
 * `CleanupOutcome.to_dict()` mapping shape ({path: {status, reason}}), and
 * never throws on an unexpected/empty payload.
 */
describe("SettingsClient cleanup wire surface (SETTINGS-OPEN-B-2 §4.3)", () => {
  it("pins the payload-free cleanup command names", () => {
    expect(CLEANUP_PREVIEW_COMMAND).toBe("cleanup_preview");
    expect(CLEANUP_RUN_COMMAND).toBe("cleanup_run");
    expect(CLEANUP_RETRY_PENDING_COMMAND).toBe("cleanup_retry_pending");
  });

  it("getCleanupPreview invokes cleanup_preview without a payload and normalizes the projection", async () => {
    const invoke = vi.fn(async (command: string) => {
      expect(command).toBe("cleanup_preview");
      return {
        targets: [
          { relative_path: "cache/webtoon-tiles/a.png", size_bytes: 2048 },
          { relative_path: "", size_bytes: 1 }, // invalid row → dropped
          { size_bytes: 3 }, // invalid row → dropped
        ],
        // total_bytes omitted → derived from the accepted targets.
        // pending_cleanups as a path list (manifest shape) → length.
        pending_cleanups: ["cache/webtoon-tiles/b.png"],
      };
    });
    const preview = await new SettingsClient(invoke).getCleanupPreview();
    expect(invoke).toHaveBeenCalledWith("cleanup_preview");
    expect(preview).toEqual({
      targets: [{ relative_path: "cache/webtoon-tiles/a.png", size_bytes: 2048 }],
      total_bytes: 2048,
      pending_cleanups: 1,
    });
  });

  it("runCleanup invokes cleanup_run without a payload and accepts items + counts", async () => {
    const invoke = vi.fn(async (command: string) => {
      expect(command).toBe("cleanup_run");
      return {
        items: [
          { relative_path: "cache/webtoon-tiles/a.png", status: "ok" },
          { relative_path: "cache/webtoon-tiles/b.png", status: "failed", detail: "EBUSY" },
          { relative_path: "cache/other.png", status: "skipped", detail: "outside safe prefixes" },
        ],
        removed: 1,
        failed: 1,
        skipped: 1,
      };
    });
    const outcome = await new SettingsClient(invoke).runCleanup();
    expect(invoke).toHaveBeenCalledWith("cleanup_run");
    expect(outcome.removed).toBe(1);
    expect(outcome.failed).toBe(1);
    expect(outcome.skipped).toBe(1);
    expect(outcome.items[1]).toEqual({
      relative_path: "cache/webtoon-tiles/b.png",
      status: "failed",
      detail: "EBUSY",
    });
  });

  it("accepts the ruled task-7 projection (items is a path → result mapping)", async () => {
    // wire-report final JSON: items object, top-level numeric counts.
    const invoke = vi.fn(async () => ({
      items: {
        "cache/webtoon-tiles/a.png": { status: "ok", reason: "" },
        "cache/webtoon-tiles/b.png": { status: "failed", reason: "EBUSY" },
      },
      removed: 1,
      failed: 1,
      skipped: 0,
    }));
    const outcome = await new SettingsClient(invoke).runCleanup();
    expect(outcome.items).toEqual([
      { relative_path: "cache/webtoon-tiles/a.png", status: "ok" },
      { relative_path: "cache/webtoon-tiles/b.png", status: "failed", detail: "EBUSY" },
    ]);
    expect(outcome.removed).toBe(1);
    expect(outcome.failed).toBe(1);
    expect(outcome.skipped).toBe(0);
  });

  it("accepts the Python CleanupOutcome.to_dict() mapping shape and derives the counts", async () => {
    // cleanup.py:92 — {relative_path: {"status": ..., "reason": ...}} with no
    // top-level counts. Unknown statuses are fail-closed to "failed".
    const invoke = vi.fn(async () => ({
      "cache/webtoon-tiles/a.png": { status: "ok", reason: "" },
      "cache/webtoon-tiles/b.png": { status: "failed", reason: "EBUSY" },
      "cache/other.png": { status: "skipped", reason: "outside safe cache prefixes" },
      "cache/tampered.png": { status: "not-a-status", reason: "" },
    }));
    const outcome = await new SettingsClient(invoke).runCleanup();
    expect(outcome.removed).toBe(1);
    expect(outcome.failed).toBe(2);
    expect(outcome.skipped).toBe(1);
    expect(outcome.items).toHaveLength(4);
    expect(outcome.items.find((item) => item.relative_path === "cache/tampered.png")?.status).toBe(
      "failed",
    );
  });

  it("retryPendingCleanups invokes cleanup_retry_pending without a payload", async () => {
    const invoke = vi.fn(async (command: string) => {
      expect(command).toBe("cleanup_retry_pending");
      return {
        items: [{ relative_path: "cache/webtoon-tiles/a.png", status: "ok" }],
        removed: 1,
        failed: 0,
        skipped: 0,
      };
    });
    const outcome = await new SettingsClient(invoke).retryPendingCleanups();
    expect(invoke).toHaveBeenCalledWith("cleanup_retry_pending");
    expect(outcome).toEqual({
      items: [{ relative_path: "cache/webtoon-tiles/a.png", status: "ok" }],
      removed: 1,
      failed: 0,
      skipped: 0,
    });
  });

  it("collapses unexpected payload shapes to empty results instead of throwing", async () => {
    const client = new SettingsClient(vi.fn(async () => null));
    await expect(client.getCleanupPreview()).resolves.toEqual({
      targets: [],
      total_bytes: 0,
      pending_cleanups: 0,
    });
    await expect(client.runCleanup()).resolves.toEqual({
      items: [],
      removed: 0,
      failed: 0,
      skipped: 0,
    });
  });

  it("maps a rejected invoke to SettingsClientError with the stable code", async () => {
    const client = new SettingsClient(
      vi.fn(async () => {
        throw { code: "CORE_UNAVAILABLE" };
      }),
    );
    await expect(client.getCleanupPreview()).rejects.toBeInstanceOf(SettingsClientError);
    await expect(client.getCleanupPreview()).rejects.toMatchObject({
      code: "CORE_UNAVAILABLE",
    });
  });
});
