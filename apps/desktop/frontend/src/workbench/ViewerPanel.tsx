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
 *
 * IMPL-1 additions: the retype context menu host (right click on a region
 * frame opens <RelabelContextMenu> in stage-relative coordinates) and the
 * E4 feedback bar (design §3.2: canvas bottom-center) with its HONEST
 * disabled action buttons — Core has no restore/rerender runtime command
 * yet (PROTOCOL_MINOR=3), and simulating undo with a reverse retype would
 * violate A6, so the affordances render disabled with their reasons.
 */

import { useCallback, useRef, useState } from "react";
import { RegionOverlay } from "../region/RegionOverlay";
import type { PageSizeProjection, RegionSummary, RegionType } from "../region/types";
import { RelabelContextMenu, type ContextMenuState } from "./RelabelContextMenu";

/** E4 feedback-bar payload (design §3.2 / §4.3 R4). */
export interface RelabelFeedbackState {
  regionId: string;
  text: string;
  isError: boolean;
  showRerenderAction?: boolean;
}

export interface ViewerPanelProps {
  imageUrl: string | null;
  imageError: string | null;
  regions: RegionSummary[];
  pageSize: PageSizeProjection | null;
  selectedRegionId: string | null;
  onSelectRegion: (regionId: string | null) => void;
  /** Pure-UI suspect flags passed through to the overlay warning layers. */
  suspects?: ReadonlySet<string>;
  relabelFeedback?: RelabelFeedbackState | null;
  relabelBusy?: boolean;
  relabelBusyRegionId?: string | null;
  undoAvailable?: boolean;
  rerenderBusy?: boolean;
  canRerender?: boolean;
  onUndo?: () => void;
  onRerender?: () => void;
  onRetypeRequest?: (region: RegionSummary, to: RegionType) => void;
  onToggleSuspect?: (regionId: string) => void;
}

export function ViewerPanel({
  imageUrl,
  imageError,
  regions,
  pageSize,
  selectedRegionId,
  onSelectRegion,
  suspects,
  relabelFeedback,
  relabelBusy = false,
  relabelBusyRegionId,
  undoAvailable = false,
  rerenderBusy = false,
  canRerender = false,
  onUndo,
  onRerender,
  onRetypeRequest,
  onToggleSuspect,
}: ViewerPanelProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [menu, setMenu] = useState<ContextMenuState | null>(null);

  const openMenu = useCallback(
    (regionId: string, x: number, y: number) => {
      if (!onRetypeRequest || !onToggleSuspect) {
        return;
      }
      const host = hostRef.current;
      const maxX = host ? Math.max(0, host.clientWidth - 210) : x;
      const maxY = host ? Math.max(0, host.clientHeight - 120) : y;
      setMenu({
        regionId,
        x: Math.min(Math.max(2, x), maxX),
        y: Math.min(Math.max(2, y), maxY),
      });
    },
    [onRetypeRequest, onToggleSuspect],
  );
  const closeMenu = useCallback(() => setMenu(null), []);
  const menuRegion = menu
    ? regions.find((region) => region.region_id === menu.regionId) ?? null
    : null;

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
        tabIndex={-1}
        onKeyDown={(event) => {
          // r1 P3-5: Escape dismisses the context menu (no focus trap — the
          // stage is a passive host; keydown reaches it once clicked).
          if (event.key === "Escape") {
            closeMenu();
          }
        }}
        onContextMenu={(event) => {
          // Right click on EMPTY canvas dismisses the menu (region frames
          // stopPropagation and reopen it at the new anchor instead).
          event.preventDefault();
          closeMenu();
        }}
        style={{
          position: "relative",
          flex: 1,
          background: "var(--bg-canvas, #0b0e12)",
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
          suspects={suspects}
          containerWidth={size.width}
          containerHeight={size.height}
          onRegionClick={(regionId) => {
            closeMenu();
            onSelectRegion(regionId);
          }}
          onRegionContextMenu={openMenu}
        />
        {menu && menuRegion && onRetypeRequest && onToggleSuspect && (
          <RelabelContextMenu
            region={menuRegion}
            x={menu.x}
            y={menu.y}
            suspects={suspects ?? new Set()}
            busy={relabelBusy || relabelBusyRegionId === menuRegion.region_id}
            onRetypeRequest={onRetypeRequest}
            onToggleSuspect={onToggleSuspect}
            onClose={closeMenu}
          />
        )}
        {relabelFeedback && (
          <div
            data-testid="relabel-feedback"
            role="status"
            style={{
              position: "absolute",
              bottom: 8,
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 15,
              display: "flex",
              alignItems: "center",
              gap: 8,
              maxWidth: "92%",
              background: "var(--wb-bg-raised, #161b22)",
              border: `1px solid ${relabelFeedback.isError ? "var(--wb-fail, #e07a7a)" : "var(--border-strong, #2a3038)"}`,
              borderRadius: 6,
              padding: "6px 10px",
              fontSize: 11,
              color: relabelFeedback.isError
                ? "var(--wb-fail, #e07a7a)"
                : "#d8e0e8",
              boxShadow: "0 2px 8px rgba(0,0,0,0.35)",
              height: 36,
              whiteSpace: "nowrap",
              overflow: "hidden",
            }}
            onClick={(event) => event.stopPropagation()}
          >
            <span
              data-testid="relabel-feedback-text"
              style={{ overflow: "hidden", textOverflow: "ellipsis" }}
            >
              {relabelFeedback.isError ? "" : "✅ "}
              {relabelFeedback.text}
            </span>
            {(!relabelFeedback.isError || relabelFeedback.showRerenderAction) && (
              <>
                {!relabelFeedback.isError && undoAvailable && onUndo && (
                <button
                  type="button"
                  data-testid="feedback-undo"
                  disabled={rerenderBusy}
                  title="10 秒内恢复到改标前 revision"
                  onClick={onUndo}
                  style={{
                    background: "#101418",
                    color: "#d8e0e8",
                    border: "1px solid #3a4858",
                    borderRadius: 4,
                    padding: "2px 8px",
                    fontSize: 11,
                    cursor: rerenderBusy ? "wait" : "pointer",
                  }}
                >
                  撤销（10 秒内）
                </button>
                )}
                {onRerender && (
                <button
                  type="button"
                  data-testid="feedback-rerender"
                  disabled={!canRerender || rerenderBusy}
                  title={canRerender ? "使用当前 clean 与区域 revision 重渲染本页" : "请先输入 page_id"}
                  onClick={onRerender}
                  style={{
                    background: "#101418",
                    color: canRerender && !rerenderBusy ? "#d8e0e8" : "#5a6470",
                    border: "1px solid #2a3038",
                    borderRadius: 4,
                    padding: "2px 8px",
                    fontSize: 11,
                    cursor: canRerender && !rerenderBusy ? "pointer" : "not-allowed",
                  }}
                >
                  {rerenderBusy ? "重渲染中…" : "重渲染本页"}
                </button>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
