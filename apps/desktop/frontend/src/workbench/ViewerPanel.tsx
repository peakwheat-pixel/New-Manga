/**
 * <ViewerPanel> — first-slice viewer (M2-UI1 §2.2 mapping: QML
 * `ViewerPanel.qml`). Shows the page image fetched through the EXISTING
 * resource channel (issue + chunked fetch, `loadPageImageUrl`) when a
 * resource is addressable, with the read-only <RegionOverlay> absolutely
 * positioned above. Production page->resource catalogization does not exist
 * yet (resource catalog entries are only seeded by the acceptance bridge),
 * so the honest empty states below are first-slice behaviour (registered as
 * a deviation in the Task).
 *
 * The page size the overlay consumes comes ONLY from the region read
 * projection — never from the <img> element (single math + "size only from
 * the projection").
 */

import { useCallback, useRef, useState } from "react";
import { RegionOverlay } from "../region/RegionOverlay";
import type { PageSizeProjection, RegionSummary } from "../region/types";

export interface ViewerPanelProps {
  imageUrl: string | null;
  imageError: string | null;
  regions: RegionSummary[];
  pageSize: PageSizeProjection | null;
  selectedRegionId: string | null;
  onSelectRegion: (regionId: string | null) => void;
}

export function ViewerPanel({
  imageUrl,
  imageError,
  regions,
  pageSize,
  selectedRegionId,
  onSelectRegion,
}: ViewerPanelProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  const measure = useCallback((node: HTMLDivElement | null) => {
    hostRef.current = node;
    if (node) {
      // `|| 0` keeps non-browser environments (and a hidden host) at the
      // honest empty projection instead of NaN math.
      setSize({
        width: node.clientWidth || 0,
        height: node.clientHeight || 0,
      });
    }
  }, []);

  return (
    <section
      data-testid="viewer-panel"
      style={{
        border: "1px solid #2a3038",
        borderRadius: 6,
        padding: 8,
        position: "relative",
        display: "flex",
        flexDirection: "column",
        gap: 6,
        minHeight: 240,
        flex: 1,
      }}
      onClick={() => onSelectRegion(null)}
    >
      <h2 style={{ fontSize: 12, margin: 0, color: "#d8e0e8" }}>Viewer</h2>
      <div
        ref={measure}
        data-testid="viewer-stage"
        style={{
          position: "relative",
          flex: 1,
          background: "#0b0e12",
          borderRadius: 4,
          overflow: "hidden",
          minHeight: 200,
        }}
      >
        {imageUrl && (
          <img
            data-testid="viewer-image"
            src={imageUrl}
            alt="page"
            style={{ display: "block", maxWidth: "none" }}
          />
        )}
        {!imageUrl && (
          <div
            data-testid="viewer-empty"
            style={{
              color: "#8a94a2",
              fontSize: 11,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
            }}
          >
            {imageError ?? "no page resource addressed"}
          </div>
        )}
        <RegionOverlay
          regions={regions}
          pageSize={pageSize}
          selectedRegionId={selectedRegionId}
          containerWidth={size.width}
          containerHeight={size.height}
        />
      </div>
    </section>
  );
}
