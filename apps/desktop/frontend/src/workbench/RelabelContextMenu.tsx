/**
 * <RelabelContextMenu> — the overlay right-click retype entry (design §3.2
 * dual entry: context menu + Inspector buttons). Rendered by ViewerPanel in
 * stage-relative coordinates when the right click lands on an EXISTING
 * region; the draft-polygon right-click closure of M2-UI1 #19 does not exist
 * in the React workbench yet, so the two-state exclusivity note of the
 * design degrades to "menu only opens on region frames".
 *
 * Entries follow A12 via the shared `canRetype` lookup: speech<->sfx are the
 * only enabled retype items; every other type shows a disabled item WITH the
 * reason. The suspect flag toggle (pure UI signal, R1) is offered for speech
 * regions only.
 */

import { canRetype, suspectWarningVisible } from "./relabelMachine";
import type { RegionSummary, RegionType } from "../region/types";

/** Stage-relative menu anchor (held by ViewerPanel). */
export interface ContextMenuState {
  regionId: string;
  x: number;
  y: number;
}

export interface RelabelContextMenuProps {
  region: RegionSummary;
  /** Stage-relative anchor of the right click (clamped by the caller). */
  x: number;
  y: number;
  suspects: ReadonlySet<string>;
  busy: boolean;
  onRetypeRequest: (region: RegionSummary, to: RegionType) => void;
  onToggleSuspect: (regionId: string) => void;
  onClose: () => void;
}

export function RelabelContextMenu({
  region,
  x,
  y,
  suspects,
  busy,
  onRetypeRequest,
  onToggleSuspect,
  onClose,
}: RelabelContextMenuProps) {
  const toSfx = canRetype(region, "sfx");
  const toSpeech = canRetype(region, "speech");
  const speech = region.region_type === "speech";
  const suspect = suspectWarningVisible(region, suspects);

  const itemStyle = (enabled: boolean) => ({
    display: "block",
    width: "100%",
    textAlign: "left" as const,
    background: "transparent",
    color: enabled ? "#d8e0e8" : "#5a6470",
    border: "none",
    padding: "5px 8px",
    fontSize: 11,
    cursor: enabled && !busy ? "pointer" : "not-allowed",
  });

  return (
    <div
      data-testid="retype-context-menu"
      style={{
        position: "absolute",
        left: x,
        top: y,
        zIndex: 20,
        background: "#101418",
        border: "1px solid #2a3038",
        borderRadius: 6,
        padding: 4,
        minWidth: 200,
        boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
      }}
      onClick={(event) => event.stopPropagation()}
    >
      {toSfx.enabled && (
        <button
          type="button"
          data-testid="menu-mark-sfx"
          style={itemStyle(true)}
          disabled={busy}
          onClick={() => {
            onClose();
            onRetypeRequest(region, "sfx");
          }}
        >
          标记为拟声词 (sfx)
        </button>
      )}
      {toSpeech.enabled && (
        <button
          type="button"
          data-testid="menu-retype-speech"
          style={{ ...itemStyle(true), color: "#e0b070" }}
          disabled={busy}
          onClick={() => {
            onClose();
            onRetypeRequest(region, "speech");
          }}
        >
          改回对白 (speech)…
        </button>
      )}
      {!toSfx.enabled && !toSpeech.enabled && (
        <p
          data-testid="menu-retype-disabled-reason"
          style={{ margin: 0, padding: "5px 8px", fontSize: 10, color: "#5a6470" }}
        >
          {toSfx.reason}
        </p>
      )}
      {speech && (
        <button
          type="button"
          data-testid="menu-toggle-suspect"
          style={itemStyle(true)}
          disabled={busy}
          onClick={() => {
            onClose();
            onToggleSuspect(region.region_id);
          }}
        >
          {suspect ? "取消疑似拟声词标记" : "标记为疑似拟声词 ♪?"}
        </button>
      )}
    </div>
  );
}
