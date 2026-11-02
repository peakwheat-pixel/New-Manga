/**
 * The single projection math for the region read face (M2-WORKBENCH-REACT-1).
 *
 * M2-UI1 §2.2 RegionOverlay hard rules, translated verbatim:
 * - "size only from the projection": the page pixel extent comes from the
 *   `list_regions` result projection (`page_size`), never from a decoded
 *   image element;
 * - "only normalized values cross the boundary": region geometry enters this
 *   module normalized (0..1) and leaves as viewport pixels; nothing else
 *   crosses.
 *
 * "Single math" constraint: every normalized->viewport conversion lives in
 * this one module; components consume its results, they never re-derive the
 * mapping.
 */

import type { NormalizedRegionGeometry, PageSizeProjection } from "./types";

/** The image display rectangle inside the viewer container (letterbox):
 * the largest aspect-preserving rect centered in the container, computed
 * from the PROJECTED page size only. */
export interface LetterboxView {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Letterbox the projected page size into the container. Degenerate inputs
 * (no page projection, zero container extent) collapse to an empty rect at
 * the origin -- the overlay then renders nothing instead of fabricating a
 * placement.
 */
export function letterboxView(
  pageSize: PageSizeProjection | null,
  containerWidth: number,
  containerHeight: number,
): LetterboxView {
  if (
    !pageSize ||
    pageSize.width <= 0 ||
    pageSize.height <= 0 ||
    containerWidth <= 0 ||
    containerHeight <= 0
  ) {
    return { x: 0, y: 0, width: 0, height: 0 };
  }
  const scale = Math.min(
    containerWidth / pageSize.width,
    containerHeight / pageSize.height,
  );
  const width = pageSize.width * scale;
  const height = pageSize.height * scale;
  return {
    x: (containerWidth - width) / 2,
    y: (containerHeight - height) / 2,
    width,
    height,
  };
}

/** A projected axis-aligned box in viewport pixels (SVG rect attributes). */
export interface ProjectedBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Project one region's normalized geometry into the letterbox view. The
 * normalized 0..1 domain maps onto the IMAGE DISPLAY AREA (the letterbox
 * rect), so frames stay glued to the image at any container size.
 */
export function projectRegionBox(
  geometry: NormalizedRegionGeometry,
  view: LetterboxView,
): ProjectedBox {
  const [nx, ny, nw, nh] = geometry.bbox;
  return {
    x: view.x + nx * view.width,
    y: view.y + ny * view.height,
    width: nw * view.width,
    height: nh * view.height,
  };
}

/**
 * Project one normalized ring into viewport pixel points (SVG polygon
 * points). An empty ring stays empty.
 */
export function projectRegionPolygon(
  geometry: NormalizedRegionGeometry,
  view: LetterboxView,
): [number, number][] {
  return geometry.polygon.map(([nx, ny]) => [
    view.x + nx * view.width,
    view.y + ny * view.height,
  ] as [number, number]);
}
