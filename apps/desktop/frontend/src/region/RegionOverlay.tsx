/**
 * <RegionOverlay> — the SVG frame layer (M2-UI1 §2.2 mapping: QML
 * `RegionOverlay.qml` Canvas -> React SVG; M2-WORKBENCH-REACT-1 first slice,
 * interaction + mitigation layers added by M2-SFX-MISROUTE-UI-IMPL-1).
 *
 * Hard rules carried verbatim from the mapping contract:
 * - page size comes ONLY from the projection (`pageSize` prop fed from the
 *   `list_regions` result) — never from a decoded image element;
 * - ONLY normalized region values cross the boundary — the geometry arrives
 *   normalized and the viewport math lives solely in `region/geometry.ts`
 *   (single math).
 *
 * Layers (design `M2-SFX-MISROUTE-UI-MITIGATION` §3.2 — five independent
 * layers, never merged into one badge):
 * - base frame: st-run stroke, accent when selected (unchanged first slice);
 * - E1 warning outline (speech + UI suspect flag only): warn 2px solid
 *   OUTSIDE the base frame with a 2px gap; co-exists with the selection
 *   stroke (selected inner accent + warning outer warn);
 * - E2 warning pill / E3 sfx type pill: top-left anchored, mutually
 *   exclusive per region (state machine guarantee); glyph+color+text
 *   together (A8 triple coding);
 * - interaction: frames are clickable/focusable (select) and right-clickable
 *   (retype menu anchor). The SVG ROOT stays pointer-events:none so empty-canvas
 *   clicks keep clearing the selection; individual frames re-enable
 *   pointer-events and stopPropagation.
 *
 * The machine-pen glyph ⧉ (design §3.4) is deliberately NOT rendered: the
 * six-field read face cannot distinguish an arbitrated sfx region
 * (`sfx-arb-` label prefix) from a detector-born one — registered deviation.
 */

import { Fragment } from "react";
import type { RegionSummary } from "./types";
import {
  letterboxView,
  projectRegionBox,
  projectRegionPolygon,
} from "./geometry";
import { sfxBadgeLabel, suspectWarningVisible } from "../workbench/relabelMachine";
import type { SuspectSet } from "../workbench/relabelMachine";

const STROKE_REGION = "var(--wb-region-stroke, #7aa2c8)";
const STROKE_SELECTED = "var(--wb-region-selected, #d8a03c)";
const STROKE_WARN = "var(--st-warn, #fbbf24)";
const PILL_WARN_BG = "var(--warn-soft, rgba(251, 191, 36, 0.16))";
const PILL_WARN_TEXT = "var(--st-warn-t, #fbbf24)";
const PILL_SKIP_BG = "var(--skip-soft, rgba(126, 178, 135, 0.16))";
const PILL_SKIP_TEXT = "var(--st-skip, #7eb287)";

const PILL_HEIGHT = 20;
const PILL_PAD_X = 8;
const PILL_FONT = 12;
const PILL_RADIUS = 8;

export interface RegionOverlayProps {
  regions: RegionSummary[];
  /** Projected page pixel size (the ONLY size source; null = no page). */
  pageSize: { width: number; height: number } | null;
  selectedRegionId: string | null;
  /** Pure-UI suspect flags (design R1; never a Core field). */
  suspects?: SuspectSet;
  containerWidth: number;
  containerHeight: number;
  onRegionClick?: (regionId: string) => void;
  onRegionContextMenu?: (regionId: string, x: number, y: number) => void;
}

/** Pill width estimate: the CJK glyph ≈ font size, ASCII ≈ 0.62em; +padding.
 * Kept as a component constant (EVOLVING-3: literal registered per the
 * M2-UI1 D-2 precedent, token promotion is a later visual-baseline call). */
function pillWidth(text: string): number {
  let units = 0;
  for (const ch of text) {
    units += ch.charCodeAt(0) > 0x2e7f ? 1 : 0.62;
  }
  return Math.ceil(units * PILL_FONT) + PILL_PAD_X * 2;
}

export function RegionOverlay({
  regions,
  pageSize,
  selectedRegionId,
  suspects,
  containerWidth,
  containerHeight,
  onRegionClick,
  onRegionContextMenu,
}: RegionOverlayProps) {
  const view = letterboxView(pageSize, containerWidth, containerHeight);
  const drawable = view.width > 0 && view.height > 0;
  const interactive = Boolean(onRegionClick || onRegionContextMenu);
  return (
    <svg
      data-testid="region-overlay"
      width={containerWidth}
      height={containerHeight}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
    >
      {drawable &&
        regions.map((region) => {
          if (!region.geometry) {
            // An older Core projection without geometry: no fabricated frame
            // (and no interaction anchor — the honest absence is registered).
            return null;
          }
          const selected = region.region_id === selectedRegionId;
          const box = projectRegionBox(region.geometry, view);
          const ring = projectRegionPolygon(region.geometry, view);
          const warned = suspects
            ? suspectWarningVisible(region, suspects)
            : false;
          const badge =
            region.region_type === "sfx"
              ? sfxBadgeLabel(region.sfx_policy)
              : warned
                ? { glyph: "♪?", text: "疑似拟声词" }
                : null;
          const badgeText = badge ? `${badge.glyph} ${badge.text}` : null;
          const badgeWidth = badgeText ? pillWidth(badgeText) : 0;
          // Top-left anchor; falls INSIDE the frame when it would leave the
          // stage through the top edge.
          const badgeY =
            box.y - PILL_HEIGHT - 2 < 0 ? box.y + 2 : box.y - PILL_HEIGHT - 2;
          const badgeFill = warned
            ? PILL_WARN_BG
            : region.region_type === "sfx"
              ? PILL_SKIP_BG
              : "none";
          const badgeTextColor = warned ? PILL_WARN_TEXT : PILL_SKIP_TEXT;
          const interaction = interactive
            ? {
                pointerEvents: "auto" as const,
                cursor: "pointer" as const,
                onClick: (event: React.MouseEvent) => {
                  event.stopPropagation();
                  onRegionClick?.(region.region_id);
                },
                onKeyDown: (event: React.KeyboardEvent) => {
                  if (event.key === "Tab") {
                    const frame = event.currentTarget as SVGRectElement;
                    const frames = Array.from(frame.ownerSVGElement?.querySelectorAll<SVGRectElement>('[data-testid^="region-frame-"]') ?? []);
                    const currentIndex = frames.indexOf(frame);
                    if (frames.length > 1 && currentIndex >= 0) {
                      event.preventDefault();
                      frames[(currentIndex + (event.shiftKey ? frames.length - 1 : 1)) % frames.length].focus();
                    }
                    return;
                  }
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    event.stopPropagation();
                    onRegionClick?.(region.region_id);
                  }
                },
                onContextMenu: (event: React.MouseEvent) => {
                  event.preventDefault();
                  event.stopPropagation();
                  onRegionContextMenu?.(
                    region.region_id,
                    event.nativeEvent.offsetX,
                    event.nativeEvent.offsetY,
                  );
                },
              }
            : {};
          return (
            <Fragment key={region.region_id}>
              {warned && (
                // E1: warning outline OUTSIDE the base frame, 2px gap.
                <rect
                  data-testid={`region-warn-${region.region_id}`}
                  x={box.x - 4}
                  y={box.y - 4}
                  width={box.width + 8}
                  height={box.height + 8}
                  fill="none"
                  stroke={STROKE_WARN}
                  strokeWidth={2}
                  pointerEvents="none"
                />
              )}
              <rect
                data-testid={`region-frame-${region.region_id}`}
                x={box.x}
                y={box.y}
                width={box.width}
                height={box.height}
                fill="none"
                stroke={selected ? STROKE_SELECTED : STROKE_REGION}
                strokeWidth={selected ? 2.5 : 1.5}
                role="button"
                tabIndex={0}
                aria-label={`选择 Region ${region.region_id}`}
                aria-pressed={selected}
                {...interaction}
              />
              {ring.length >= 3 && (
                <polygon
                  data-testid={`region-ring-${region.region_id}`}
                  points={ring.map(([x, y]) => `${x},${y}`).join(" ")}
                  fill="none"
                  stroke={selected ? STROKE_SELECTED : STROKE_REGION}
                  strokeWidth={1}
                  strokeDasharray="4 3"
                  pointerEvents="none"
                />
              )}
              {badgeText && (
                <g
                  data-testid={`region-badge-${region.region_id}`}
                  pointerEvents="none"
                >
                  <rect
                    x={box.x}
                    y={badgeY}
                    width={badgeWidth}
                    height={PILL_HEIGHT}
                    rx={PILL_RADIUS}
                    fill={badgeFill}
                  />
                  <text
                    x={box.x + PILL_PAD_X}
                    y={badgeY + PILL_HEIGHT / 2 + PILL_FONT * 0.36}
                    fontSize={PILL_FONT}
                    fill={badgeTextColor}
                    style={{ userSelect: "none" }}
                  >
                    {badgeText}
                  </text>
                </g>
              )}
            </Fragment>
          );
        })}
    </svg>
  );
}
