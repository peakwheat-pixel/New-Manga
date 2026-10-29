import { describe, expect, it, vi } from "vitest";
import {
  LIST_REGIONS_COMMAND,
  LIST_REGION_REVISIONS_COMMAND,
  RERENDER_PAGE_COMMAND,
  RegionClient,
  RESTORE_REGION_REVISION_COMMAND,
  SET_REGION_TYPE_COMMAND,
} from "./client";
import type { ListRegionsResult, SetRegionTypeResult } from "./types";

/**
 * RegionClient unit pins (M2-WORKBENCH-REACT-1). The wire names were ruled
 * by M2-REGION-RETYPE-CORE (contract M2-C1 §5.4) and are pinned here as the
 * drift alarm; the rev 1.5 read widening (optional geometry/page_size) is
 * consumed verbatim from the Core projection.
 */

function makeInvoke(
  handler: (command: string, args?: Record<string, unknown>) => unknown,
) {
  return vi.fn(async (command: string, args?: Record<string, unknown>) =>
    handler(command, args),
  );
}

const FIXTURE_LIST: ListRegionsResult = {
  regions: [
    {
      region_id: "region-1",
      region_type: "sfx",
      sfx_policy: "translate",
      origin: "user",
      revision_no: 3,
      geometry: {
        bbox: [0.1, 0.2, 0.3, 0.4],
        polygon: [],
      },
    },
  ],
  page_size: { width: 100, height: 50 },
};

describe("RegionClient command surface (RULED wire names)", () => {
  it("pins the two RULED wire names", () => {
    expect(LIST_REGIONS_COMMAND).toBe("list_regions");
    expect(SET_REGION_TYPE_COMMAND).toBe("set_region_type");
  });
});

describe("RegionClient.listRegions (read face)", () => {
  it("invokes list_regions with the pageId camelCase arg and returns the projection verbatim", async () => {
    const invoke = makeInvoke((command, args) => {
      expect(command).toBe("list_regions");
      expect(args).toEqual({ pageId: "page-1" });
      return FIXTURE_LIST;
    });
    const client = new RegionClient(invoke);

    const result = await client.listRegions("page-1");

    expect(result).toEqual(FIXTURE_LIST);
    expect(result.page_size).toEqual({ width: 100, height: 50 });
    // the rev 1.5 optional geometry rides through untouched (zero UI-side
    // reinterpretation of the Core projection)
    expect(result.regions[0].geometry).toEqual({
      bbox: [0.1, 0.2, 0.3, 0.4],
      polygon: [],
    });
  });

  it("reads an older projection without the optional fields (additive widening, §3.2)", async () => {
    // a pre-1.5 Core never sends geometry/page_size; the client passes the
    // five-field rows through verbatim and leaves absent optional fields
    // absent (undefined) -- the UI side collapses them with ?? (WorkbenchPage)
    const invoke = makeInvoke(() => ({
      regions: [
        {
          region_id: "region-old",
          region_type: "speech",
          sfx_policy: "skip",
          origin: "machine",
          revision_no: 1,
        },
      ],
    }));
    const client = new RegionClient(invoke);

    const result = await client.listRegions("page-old");

    expect(result.page_size).toBeUndefined();
    expect(result.regions[0].geometry).toBeUndefined();
  });

  it("treats a rejection with a code string as a typed RegionClientError", async () => {
    const client = new RegionClient(makeInvoke(() => {
      throw "INVALID_REQUEST";
    }));
    await expect(client.listRegions("page-1")).rejects.toMatchObject({
      name: "RegionClientError",
      code: "INVALID_REQUEST",
    });
  });

  it("wraps a malformed projection (no regions array) as REGION_PROJECTION_MALFORMED", async () => {
    const client = new RegionClient(makeInvoke(() => ({ nothing: true })));
    await expect(client.listRegions("page-1")).rejects.toMatchObject({
      code: "REGION_PROJECTION_MALFORMED",
    });
  });

  it("falls back to REGION_CHANNEL_UNAVAILABLE when a rejection carries no code/message", async () => {
    // r1 P4-2: the fallback code itself is pinned, not just the error type.
    // An Error WITH a message passes the message through as the code (the
    // settings-client precedent: Tauri string codes and Error messages are
    // both informative); the fallback fires for code/message-less objects.
    const client = new RegionClient(makeInvoke(() => {
      throw {};
    }));
    await expect(client.listRegions("page-1")).rejects.toMatchObject({
      name: "RegionClientError",
      code: "REGION_CHANNEL_UNAVAILABLE",
    });
  });
});

describe("RegionClient.setRegionType (write face; UI interaction belongs to IMPL-1)", () => {
  it("invokes set_region_type with regionId/newRegionType and no expectedRevision when omitted", async () => {
    const effective: SetRegionTypeResult = {
      region_id: "region-1",
      revision_no: 4,
      region_type: "narration",
      sfx_policy: "skip",
    };
    const invoke = makeInvoke((command, args) => {
      expect(command).toBe("set_region_type");
      expect(args).toEqual({
        regionId: "region-1",
        newRegionType: "narration",
      });
      return effective;
    });
    const client = new RegionClient(invoke);

    await expect(
      client.setRegionType("region-1", "narration"),
    ).resolves.toEqual(effective);
  });

  it("carries the optional optimistic guard (C4) as expectedRevision", async () => {
    const invoke = makeInvoke((_command, args) => {
      expect(args).toEqual({
        regionId: "region-1",
        newRegionType: "sfx",
        expectedRevision: 3,
      });
      // the C4 mismatch path is the typed rejection below; here the guard
      // simply rides the payload
      return { region_id: "region-1", revision_no: 4, region_type: "sfx", sfx_policy: "translate" };
    });
    const client = new RegionClient(invoke);

    await client.setRegionType("region-1", "sfx", 3);
    expect(invoke).toHaveBeenCalledTimes(1);
  });

  it("surfaces the typed conflict code (INPUT_REVISION_CHANGED) verbatim", async () => {
    const client = new RegionClient(makeInvoke(() => {
      throw "INPUT_REVISION_CHANGED";
    }));
    await expect(
      client.setRegionType("region-1", "sfx", 999),
    ).rejects.toMatchObject({ code: "INPUT_REVISION_CHANGED" });
  });

  it("surfaces the typed not-found code (TARGET_NOT_FOUND) verbatim", async () => {
    const client = new RegionClient(makeInvoke(() => {
      throw "TARGET_NOT_FOUND";
    }));
    await expect(
      client.setRegionType("no-such-region", "sfx"),
    ).rejects.toMatchObject({ code: "TARGET_NOT_FOUND" });
  });

  it("wraps a malformed effective-state result as REGION_PROJECTION_MALFORMED", async () => {
    const client = new RegionClient(makeInvoke(() => null));
    await expect(
      client.setRegionType("region-1", "sfx"),
    ).rejects.toMatchObject({ code: "REGION_PROJECTION_MALFORMED" });
  });
});

describe("RegionClient RC-4 command face", () => {
  it("lists revisions using the Tauri camelCase arg and keeps the Core summary verbatim", async () => {
    const result = {
      region_id: "region-1",
      current_revision_no: 4,
      revisions: [{
        region_revision_id: "revision-2",
        revision_no: 2,
        origin: "user",
        review_state: "accepted",
        is_pinned: true,
        restored_from_revision_id: null,
        created_at: "2026-10-07T00:00:00Z",
        region_type: "speech",
        sfx_policy: "skip",
        is_current: false,
      }],
    };
    const invoke = makeInvoke((command, args) => {
      expect(command).toBe(LIST_REGION_REVISIONS_COMMAND);
      expect(args).toEqual({ regionId: "region-1" });
      return result;
    });

    await expect(new RegionClient(invoke).listRegionRevisions("region-1")).resolves.toEqual(result);
  });

  it("restores an explicit target with the current revision guard", async () => {
    const result = {
      region_id: "region-1",
      revision_no: 5,
      region_type: "speech",
      sfx_policy: "skip",
    };
    const invoke = makeInvoke((command, args) => {
      expect(command).toBe(RESTORE_REGION_REVISION_COMMAND);
      expect(args).toEqual({ regionId: "region-1", revisionNo: 2, expectedRevision: 4 });
      return result;
    });

    await expect(new RegionClient(invoke).restoreRegionRevision("region-1", 2, 4)).resolves.toEqual(result);
  });

  it("rerenders by page id and carries an opaque preview resource", async () => {
    const result = {
      page_id: "page-1",
      artifact_id: "artifact-1",
      revision_no: 8,
      reports: [{ region_id: "region-1", status: "rendered", skip_reason: null, font_substituted: false }],
      preview: { resource_id: "preview-1", revision: "rev-8" },
      preview_error: null,
    };
    const invoke = makeInvoke((command, args) => {
      expect(command).toBe(RERENDER_PAGE_COMMAND);
      expect(args).toEqual({ pageId: "page-1" });
      return result;
    });

    await expect(new RegionClient(invoke).rerenderPage("page-1")).resolves.toEqual(result);
  });

  it("surfaces restore conflicts and rejects malformed rerender results", async () => {
    const conflict = new RegionClient(makeInvoke(() => { throw "INPUT_REVISION_CHANGED"; }));
    await expect(conflict.restoreRegionRevision("region-1", 2, 4)).rejects.toMatchObject({
      name: "RegionClientError",
      code: "INPUT_REVISION_CHANGED",
    });
    const malformed = new RegionClient(makeInvoke(() => ({ page_id: "page-1" })));
    await expect(malformed.rerenderPage("page-1")).rejects.toMatchObject({
      code: "REGION_PROJECTION_MALFORMED",
    });
  });
});
