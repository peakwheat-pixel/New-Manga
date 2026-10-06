/**
 * <RegionInspector> — first-slice read-only inspector (M2-UI1 §2.2 mapping:
 * QML `RegionInspector.qml`). Shows the selected region row verbatim from
 * the read projection: region_id / region_type / sfx_policy / origin /
 * revision_no. Zero UI-side interpretation (the UI-MITIGATION A9 display-
 * mapping discipline: labels are a lookup of Core snapshot values).
 *
 * The retype entry is a RESERVED DISABLED control: its enablement logic and
 * confirmation/undo interactions belong to M2-SFX-MISROUTE-UI-IMPL-1.
 */

import type { RegionSummary } from "../region/types";

export interface RegionInspectorProps {
  region: RegionSummary | null;
}

export function RegionInspector({ region }: RegionInspectorProps) {
  return (
    <section
      data-testid="region-inspector"
      style={{
        border: "1px solid #2a3038",
        borderRadius: 6,
        padding: 8,
        minWidth: 220,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <h2 style={{ fontSize: 12, margin: 0, color: "#d8e0e8" }}>Inspector</h2>
      {!region && (
        <p data-testid="inspector-empty" style={{ color: "#8a94a2", fontSize: 11, margin: 0 }}>
          no region selected
        </p>
      )}
      {region && (
        <dl
          data-testid={`inspector-row-${region.region_id}`}
          style={{ margin: 0, display: "grid", gridTemplateColumns: "auto 1fr", gap: "2px 8px", fontSize: 11 }}
        >
          <dt style={{ color: "#8a94a2" }}>region_id</dt>
          <dd style={{ margin: 0, color: "#d8e0e8", fontFamily: "Consolas, monospace" }}>{region.region_id}</dd>
          <dt style={{ color: "#8a94a2" }}>region_type</dt>
          <dd data-testid="inspector-region-type" style={{ margin: 0, color: "#d8e0e8" }}>{region.region_type}</dd>
          <dt style={{ color: "#8a94a2" }}>sfx_policy</dt>
          <dd data-testid="inspector-sfx-policy" style={{ margin: 0, color: "#d8e0e8" }}>{region.sfx_policy}</dd>
          <dt style={{ color: "#8a94a2" }}>origin</dt>
          <dd data-testid="inspector-origin" style={{ margin: 0, color: "#d8e0e8" }}>{region.origin}</dd>
          <dt style={{ color: "#8a94a2" }}>revision_no</dt>
          <dd data-testid="inspector-revision-no" style={{ margin: 0, color: "#d8e0e8" }}>{region.revision_no}</dd>
        </dl>
      )}
      {/* Reserved retype entry — permanently disabled in this slice; the
          enabled flow (typed SetRegionType via RegionClient) is wired and
          unit-pinned at the client layer, the UI interaction is IMPL-1. */}
      <button
        type="button"
        data-testid="inspector-retype-reserved"
        disabled
        title="改标交互属 M2-SFX-MISROUTE-UI-IMPL-1（本刀预留禁用态）"
        style={{
          background: "#161b22",
          color: "#5a6470",
          border: "1px solid #2a3038",
          borderRadius: 4,
          padding: "4px 8px",
          fontSize: 11,
          cursor: "not-allowed",
        }}
      >
        改标（预留）
      </button>
    </section>
  );
}
