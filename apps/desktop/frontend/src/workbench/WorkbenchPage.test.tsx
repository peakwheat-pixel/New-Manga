import { renderToString } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { RegionOverlay } from "../region/RegionOverlay";
import type { RegionSummary } from "../region/types";
import { WorkbenchPage } from "./WorkbenchPage";

/**
 * First-slice component smoke pins (M2-WORKBENCH-REACT-1). Component
 * structure and the read-only overlay math are asserted on the static
 * render; interaction/data coverage lives at the client layer
 * (region/client.test.ts), the established test split of this frontend.
 *
 * The container's data-loading effects do not run under renderToString by
 * design (React SSR semantics); WorkbenchPage therefore renders its honest
 * initial empty state here.
 */

// A page 100x50 letterboxed into a 200x100 container fills it exactly
// (aspect 2:1 both) — view = {x:0, y:0, w:200, h:100}. The normalized bbox
// [0.1, 0.2, 0.3, 0.4] projects to x=20, y=20, w=60, h=40.
const FRAME_REGION: RegionSummary = {
  region_id: "region-1",
  region_type: "sfx",
  sfx_policy: "translate",
  origin: "user",
  revision_no: 3,
  geometry: {
    bbox: [0.1, 0.2, 0.3, 0.4],
    polygon: [[0.1, 0.2], [0.4, 0.2], [0.4, 0.6], [0.1, 0.6]],
  },
};

describe("<WorkbenchPage> five-zone skeleton (mapping-contract names)", () => {
  it("renders the five zones with their data-testid pins", () => {
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain('data-testid="workbench-page"');
    expect(html).toContain('data-testid="workbench-toolbar"');
    expect(html).toContain('data-testid="page-list-panel"');
    expect(html).toContain('data-testid="viewer-panel"');
    expect(html).toContain('data-testid="region-inspector"');
    expect(html).toContain('data-testid="task-progress-panel"');
  });

  it("renders the honest empty states before any data channel resolves", () => {
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain('data-testid="page-list-empty"');
    expect(html).toContain('data-testid="viewer-empty"');
    expect(html).toContain('data-testid="inspector-empty"');
    expect(html).toContain('data-testid="task-progress-placeholder"');
    expect(html).not.toContain('data-testid="workbench-error"');
  });

  it("keeps the retype entries RESERVED and disabled (IMPL-1 owns enablement)", () => {
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain('data-testid="inspector-retype-reserved"');
    expect(html).toContain('data-testid="toolbar-retype-reserved"');
    // the disabled attribute renders on both reserved controls
    expect((html.match(/disabled=""|\bdisabled\b/g) ?? []).length).toBeGreaterThanOrEqual(2);
  });

  it("keeps the task progress placeholder free of any new command face", () => {
    // the placeholder text documents WHY there is no data wire: standing up
    // a command face for a placeholder is explicitly forbidden (Task AC2)
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain("占位不扩命令面");
  });
});

describe("<RegionOverlay> read-only SVG frames (M2-UI1 hard rules)", () => {
  it("draws the frame from normalized geometry through the single math", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[FRAME_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId="region-1"
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain('data-testid="region-overlay"');
    expect(html).toContain('data-testid="region-frame-region-1"');
    expect(html).toContain('x="20"');
    expect(html).toContain('y="20"');
    expect(html).toContain('width="60"');
    expect(html).toContain('height="40"');
    // the polygon ring rides the same view (dashed detail line):
    // normalized ring x 0.1/0.4 -> 20/80, y 0.2/0.6 -> 20/60
    expect(html).toContain('data-testid="region-ring-region-1"');
    expect(html).toContain("20,20 80,20 80,60 20,60");
  });

  it("stays silent for rows without geometry (an older Core projection)", () => {
    const noGeometry: RegionSummary = {
      region_id: "region-old",
      region_type: "speech",
      sfx_policy: "skip",
      origin: "machine",
      revision_no: 1,
    };
    const html = renderToString(
      <RegionOverlay
        regions={[noGeometry]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain('data-testid="region-overlay"');
    expect(html).not.toContain("region-frame-region-old");
  });

  it("renders no fabricated placement when the page projection is absent", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[FRAME_REGION]}
        pageSize={null}
        selectedRegionId={null}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).not.toContain("region-frame-region-1");
  });

  it("renders no frame before the container has been measured", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[FRAME_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        containerWidth={0}
        containerHeight={0}
      />,
    );
    expect(html).not.toContain("region-frame-region-1");
  });
});
