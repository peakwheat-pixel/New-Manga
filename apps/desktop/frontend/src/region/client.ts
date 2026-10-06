/**
 * RegionClient — the React-side consumer of the region retype/read channel
 * (contract M2-C1 §5.4; M2-REGION-RETYPE-CORE runtime; read face widened by
 * rev 1.5 / M2-WORKBENCH-REACT-1).
 *
 * Both methods ride the production stdio bridge pinned since
 * M2-REGION-RETYPE-CORE (Tauri PRODUCTION_COMMANDS holds exactly
 * `set_region_type` + `list_regions`; the command names below are the RULED
 * wire names, pinned here as the drift alarm). Core is the sole region
 * authority: the six-value RegionType gate, the EV-8 policy re-snapshot and
 * the optimistic `expected_revision` guard all live Core-side BEFORE any
 * persistence; this client only forwards payloads and surfaces typed codes.
 *
 * Client form follows the settings/library precedents (typed error +
 * injectable invoke for tests).
 */

import type {
  ListRegionsResult,
  ListRegionRevisionsResult,
  RerenderPageResult,
  RegionType,
  RestoreRegionRevisionResult,
  SetRegionTypeResult,
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

/** RULED wire name (contract M2-C1 §5.4; pinned by the Rust suite). */
export const LIST_REGIONS_COMMAND = "list_regions";

/** RULED wire name (contract M2-C1 §5.4; pinned by the Rust suite). */
export const SET_REGION_TYPE_COMMAND = "set_region_type";

export const LIST_REGION_REVISIONS_COMMAND = "list_region_revisions";
export const RESTORE_REGION_REVISION_COMMAND = "restore_region_revision";
export const RERENDER_PAGE_COMMAND = "rerender_page";

export class RegionClientError extends Error {
  code: string;

  constructor(code: string, message?: string) {
    super(message || code);
    this.name = "RegionClientError";
    this.code = code;
  }
}

function typedError(operation: string, error: unknown): RegionClientError {
  // Tauri rejects map to the Core envelope's `code` string through the
  // host bridge (LibraryError.code pass-through, library_bridge.rs).
  const code =
    typeof error === "string"
      ? error
      : (error as Error)?.message || "REGION_CHANNEL_UNAVAILABLE";
  return new RegionClientError(code, `${operation} failed: ${code}`);
}

export class RegionClient {
  private invoke: InvokeFn;

  constructor(invoke?: InvokeFn) {
    this.invoke = invoke || getTauriInvoke();
  }

  /**
   * Read a page's live regions (reading_order ascending) plus the page
   * pixel-size projection. An unknown page or a page without live rows is
   * an EMPTY LIST (contract footnote a) -- not an error.
   */
  async listRegions(pageId: string): Promise<ListRegionsResult> {
    try {
      const res = (await this.invoke(LIST_REGIONS_COMMAND, {
        pageId,
      })) as ListRegionsResult;
      if (!res || !Array.isArray(res.regions)) {
        throw new RegionClientError(
          "REGION_PROJECTION_MALFORMED",
          "list_regions returned no regions array",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof RegionClientError) {
        throw error;
      }
      throw typedError("list_regions", error);
    }
  }

  /**
   * Retype one region (the write face; the UI interaction consuming it
   * belongs to M2-SFX-MISROUTE-UI-IMPL-1 -- the client layer is callable and
   * unit-pinned here). `expectedRevision` is the optional optimistic guard
   * (C4): a mismatch is a typed INPUT_REVISION_CHANGED rejection with zero
   * write; omitted = user direct write.
   */
  async setRegionType(
    regionId: string,
    newRegionType: RegionType,
    expectedRevision?: number,
  ): Promise<SetRegionTypeResult> {
    try {
      const args: Record<string, unknown> = {
        regionId,
        newRegionType,
      };
      if (expectedRevision !== undefined) {
        args.expectedRevision = expectedRevision;
      }
      const res = (await this.invoke(
        SET_REGION_TYPE_COMMAND,
        args,
      )) as SetRegionTypeResult;
      if (!res || typeof res.region_id !== "string") {
        throw new RegionClientError(
          "REGION_PROJECTION_MALFORMED",
          "set_region_type returned no effective state",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof RegionClientError) {
        throw error;
      }
      throw typedError("set_region_type", error);
    }
  }

  async listRegionRevisions(regionId: string): Promise<ListRegionRevisionsResult> {
    try {
      const res = (await this.invoke(LIST_REGION_REVISIONS_COMMAND, {
        regionId,
      })) as ListRegionRevisionsResult;
      if (
        !res ||
        typeof res.region_id !== "string" ||
        typeof res.current_revision_no !== "number" ||
        !Array.isArray(res.revisions)
      ) {
        throw new RegionClientError(
          "REGION_PROJECTION_MALFORMED",
          "list_region_revisions returned no revision list",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof RegionClientError) throw error;
      throw typedError("list_region_revisions", error);
    }
  }

  async restoreRegionRevision(
    regionId: string,
    revisionNo: number,
    expectedRevision: number,
  ): Promise<RestoreRegionRevisionResult> {
    try {
      const res = (await this.invoke(RESTORE_REGION_REVISION_COMMAND, {
        regionId,
        revisionNo,
        expectedRevision,
      })) as RestoreRegionRevisionResult;
      if (!res || typeof res.region_id !== "string" || typeof res.revision_no !== "number") {
        throw new RegionClientError(
          "REGION_PROJECTION_MALFORMED",
          "restore_region_revision returned no effective state",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof RegionClientError) throw error;
      throw typedError("restore_region_revision", error);
    }
  }

  async rerenderPage(pageId: string): Promise<RerenderPageResult> {
    try {
      const res = (await this.invoke(RERENDER_PAGE_COMMAND, {
        pageId,
      })) as RerenderPageResult;
      if (
        !res ||
        typeof res.page_id !== "string" ||
        typeof res.artifact_id !== "string" ||
        typeof res.revision_no !== "number" ||
        !Array.isArray(res.reports) ||
        !(res.preview === null || (typeof res.preview?.resource_id === "string" && res.preview.revision !== undefined)) ||
        !(res.preview_error === null || typeof res.preview_error === "string")
      ) {
        throw new RegionClientError(
          "REGION_PROJECTION_MALFORMED",
          "rerender_page returned no render result",
        );
      }
      return res;
    } catch (error) {
      if (error instanceof RegionClientError) throw error;
      throw typedError("rerender_page", error);
    }
  }
}
