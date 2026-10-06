/**
 * Region channel wire types (contract M2-C1 §5.4; read face widened
 * additively by rev 1.5 / M2-WORKBENCH-REACT-1).
 *
 * The wire is the Core's authority projected verbatim: this module only
 * types the shapes and pins the enum closed sets -- zero UI-side
 * interpretation of region semantics (M2-SFX-MISROUTE-UI-MITIGATION A9:
 * display mapping, never decision logic).
 */

/** The RegionType six-value closed set (domain facts:
 * src/domain/regions/entities.py:20-28; contract §5.4 -- zero new enum
 * values, "ignore" is a processing action / filter state, NOT a RegionType). */
export const REGION_TYPE_VALUES = [
  "speech",
  "narration",
  "sfx",
  "title",
  "note",
  "other",
] as const;

export type RegionType = (typeof REGION_TYPE_VALUES)[number];

export function isRegionType(value: unknown): value is RegionType {
  return (
    typeof value === "string" &&
    (REGION_TYPE_VALUES as readonly string[]).includes(value)
  );
}

/** The region's own SFX policy snapshot (not the global live value). */
export type SfxPolicy = "skip" | "translate" | "manual";

/** The origin of the region's current revision (machine vs human pens stay
 * distinguishable -- UI design A7; the authoritative traceability field). */
export type RegionOrigin = "machine" | "user" | "imported" | "restored";

/**
 * Normalized region geometry (contract rev 1.5 optional `geometry` field):
 * every coordinate in 0..1, the exact reverse of the stored page-pixel
 * geometry (`normalized := pixel / size`, round-trip-stable against the
 * forward half-up writer). Only normalized values ever cross the IPC/UI
 * boundary (M2-UI1 §2.2 RegionOverlay hard rule).
 */
export interface NormalizedRegionGeometry {
  /** [x, y, w, h], normalized 0..1. */
  bbox: [number, number, number, number];
  /** Normalized ring points; an empty ring stays []. */
  polygon: [number, number][];
}

/**
 * RegionListSummary (contract §5.4): the frozen five-field minimal set plus
 * the rev 1.5 OPTIONAL geometry field. Consumers must treat `geometry` as
 * optional (an older Core never sends it; §3.2 receivers ignore unknown
 * optional fields).
 */
export interface RegionSummary {
  region_id: string;
  region_type: RegionType;
  sfx_policy: SfxPolicy;
  origin: RegionOrigin;
  revision_no: number;
  geometry?: NormalizedRegionGeometry;
}

/** The page's pixel-size projection (contract rev 1.5 optional wrapper
 * field): the ONLY size source the RegionOverlay letterbox math consumes
 * ("size only from the projection", M2-UI1 §2.2). null = the page_id hit no
 * page row (frozen-None channel semantics, distinguishable from zero). */
export interface PageSizeProjection {
  width: number;
  height: number;
}

/** The `list_regions` result wrapper. */
export interface ListRegionsResult {
  regions: RegionSummary[];
  page_size: PageSizeProjection | null;
}

/** The `set_region_type` result: the post-retype effective state, one round
 * trip (contract §5.4 SetRegionType). */
export interface SetRegionTypeResult {
  region_id: string;
  revision_no: number;
  region_type: RegionType;
  sfx_policy: SfxPolicy;
}
