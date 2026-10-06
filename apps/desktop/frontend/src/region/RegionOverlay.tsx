/**
 * <RegionOverlay> — the read-only SVG frame layer (M2-UI1 §2.2 mapping:
 * QML `RegionOverlay.qml` Canvas -> React SVG; M2-WORKBENCH-REACT-1 first
 * slice).
 *
 * Hard rules carried verbatim from the mapping contract:
 * - page size comes ONLY from the projection (`pageSize` prop fed from the
 *   `list_regions` result) — never from a decoded image element;
 * - ONLY normalized region values cross the boundary — the geometry arrives
 *   normalized and the viewport math lives solely in `region/geometry.ts`
 *   (single math).
 *
 * First slice = read-only frames: existing regions render as stroked SVG
 * shapes (rectangle bbox always; polygon ring when present), the selected
 * region is accented. Draft drawing, delete and retype interactions belong
 * to M2-SFX-MISROUTE-UI-IMPL-1 / later slices and are deliberately absent.
 */

import { Fragment } from "react";
import type { RegionSummary } from "./types";
import {
  letterboxView,
  projectRegionBox,
  projectRegionPolygon,
} from "./geometry";

const STROKE_REGION = "var(--wb-region-stroke, #7aa2c8)";
const STROKE_SELECTED = "var(--wb-region-selected, #d8a03c)";

export interface RegionOverlayProps {
  regions: RegionSummary[];
  /** Projected page pixel size (the ONLY size source; null = no page). */
  pageSize: { width: number; height: number } | null;
  selectedRegionId: string | null;
  containerWidth: number;
  containerHeight: number;
}

export function RegionOverlay({
  regions,
  pageSize,
  selectedRegionId,
  containerWidth,
  containerHeight,
}: RegionOverlayProps) {
  const view = letterboxView(pageSize, containerWidth, containerHeight);
  const drawable = view.width > 0 && view.height > 0;
  return (
    <svg
      data-testid="region-overlay"
      width={containerWidth}
      height={containerHeight}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
      aria-hidden="true"
    >
      {drawable &&
        regions.map((region) => {
          if (!region.geometry) {
            // An older Core projection without geometry: no fabricated frame.
            return null;
          }
          const selected = region.region_id === selectedRegionId;
          const stroke = selected ? STROKE_SELECTED : STROKE_REGION;
          const box = projectRegionBox(region.geometry, view);
          const ring = projectRegionPolygon(region.geometry, view);
          return (
            <Fragment key={region.region_id}>
              <rect
                data-testid={`region-frame-${region.region_id}`}
                x={box.x}
                y={box.y}
                width={box.width}
                height={box.height}
                fill="none"
                stroke={stroke}
                strokeWidth={selected ? 2.5 : 1.5}
              />
              {ring.length >= 3 && (
                <polygon
                  data-testid={`region-ring-${region.region_id}`}
                  points={ring.map(([x, y]) => `${x},${y}`).join(" ")}
                  fill="none"
                  stroke={stroke}
                  strokeWidth={1}
                  strokeDasharray="4 3"
                />
              )}
            </Fragment>
          );
        })}
    </svg>
  );
}
