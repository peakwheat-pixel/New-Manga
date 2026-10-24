/**
 * <ViewerPanel> — first-slice viewer (M2-UI1 §2.2 mapping: QML
 * `ViewerPanel.qml`). Shows page images fetched through the existing
 * resource channel, with the read-only <RegionOverlay> absolutely positioned
 * above. Initial page images resolve through the frozen page-resource command;
 * rerender previews use the same channel.
 *
 * The page size the overlay consumes comes ONLY from the region read
 * projection — never from the <img> element (single math + "size only from
 * the projection").
 *
 * IMPL-1 additions: the retype context menu host (right click on a region
 * frame opens <RelabelContextMenu> in stage-relative coordinates) and the
 * E4 feedback bar (design §3.2: canvas bottom-center). Since M2-RC4-DOMAIN-
 * COMMANDS (envelope protocol minor 4) the affordances call the real Core
 * commands: undo runs restore_region_revision inside its 10 s window, and
 * rerender calls rerender_page through the same resource channel; until the
 * first undo-capable revision exists the affordances render disabled with
 * their reasons.
 */

import { useCallback, useRef, useState } from "react";
import { RegionOverlay } from "../region/RegionOverlay";
import type { PageSizeProjection, RegionSummary, RegionType } from "../region/types";
import { RelabelContextMenu, type ContextMenuState } from "./RelabelContextMenu";
import { WorkbenchError } from "./WorkbenchError";

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
  isLoading?: boolean;
  imageProgress?: { loadedChunks: number; totalChunks: number } | null;
  regionsLoading?: boolean;
  noRegions?: boolean;
  onRetryImage?: () => void;
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
  viewerMode?: "view" | "pan" | "region";
  onSetViewerMode?: (mode: "view" | "pan" | "region") => void;
}

export function ViewerPanel({
  imageUrl,
  imageError,
  isLoading = false,
  imageProgress = null,
  regionsLoading = false,
  noRegions = false,
  onRetryImage,
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
  viewerMode = "view",
  onSetViewerMode,
}: ViewerPanelProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<{ x: number; y: number; panX: number; panY: number } | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [spacePan, setSpacePan] = useState(false);
  const [menu, setMenu] = useState<ContextMenuState | null>(null);
  const effectiveMode = spacePan ? "pan" : viewerMode;

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
        border: "1px solid #d9d9d6",
        background: "#fff",
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
      <header style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <h2 style={{ fontSize: 13, margin: 0, flex: 1, color: "#1f2328" }}>页面查看器</h2>
        <button type="button" aria-label="缩小页面" onClick={() => setZoom((value) => Math.max(0.25, value / 1.2))}>−</button>
        <output aria-label="缩放比例">{Math.round(zoom * 100)}%</output>
        <button type="button" aria-label="放大页面" onClick={() => setZoom((value) => Math.min(4, value * 1.2))}>＋</button>
        <button type="button" aria-label="重置缩放和平移" onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}>适配</button>
      </header>
      <div
        ref={measure}
        data-testid="viewer-stage"
        tabIndex={0}
        aria-label="页面画布；加减键缩放，0 重置，平移模式下拖动"
        onKeyDown={(event) => {
          // r1 P3-5: Escape dismisses the context menu (no focus trap — the
          // stage is a passive host; keydown reaches it once clicked).
          if (event.key === "Escape") {
            closeMenu();
          } else if (event.key.toLowerCase() === "v") {
            onSetViewerMode?.("pan");
          } else if (event.key.toLowerCase() === "r") {
            onSetViewerMode?.("region");
          } else if (event.key === " ") {
            event.preventDefault();
            setSpacePan(true);
          } else if (event.key === "+" || event.key === "=") {
            setZoom((value) => Math.min(4, value * 1.2));
          } else if (event.key === "-") {
            setZoom((value) => Math.max(0.25, value / 1.2));
          } else if (event.key === "0") {
            setZoom(1); setPan({ x: 0, y: 0 });
          }
        }}
        onKeyUp={(event) => { if (event.key === " ") setSpacePan(false); }}
        onBlur={() => setSpacePan(false)}
        onPointerDown={(event) => {
          if (effectiveMode !== "pan") return;
          dragRef.current = { x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
          event.currentTarget.setPointerCapture(event.pointerId);
        }}
        onPointerMove={(event) => {
          const drag = dragRef.current;
          if (effectiveMode === "pan" && drag) setPan({ x: drag.panX + event.clientX - drag.x, y: drag.panY + event.clientY - drag.y });
        }}
        onPointerUp={() => { dragRef.current = null; }}
        onPointerCancel={() => { dragRef.current = null; }}
        onContextMenu={(event) => {
          // Right click on EMPTY canvas dismisses the menu (region frames
          // stopPropagation and reopen it at the new anchor instead).
          event.preventDefault();
          closeMenu();
        }}
        style={{
          position: "relative",
          flex: 1,
          background: "#ececea",
          borderRadius: 4,
          overflow: "hidden",
          minHeight: 200,
          cursor: effectiveMode === "pan" ? "grab" : "default",
        }}
      >
        <div data-testid="viewer-content" style={{ position: "absolute", inset: 0, transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, transformOrigin: "center center" }}>
        {imageUrl && (
          <img
            data-testid="viewer-image"
            src={imageUrl}
            alt="page"
            style={{ display: "block", position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain" }}
          />
        )}
        {!imageUrl && (
          <div
            data-testid={isLoading ? "resource-resolve-busy" : "viewer-empty"}
            role={isLoading ? "status" : undefined}
            style={{
              color: "#6b7280",
              fontSize: 11,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
            }}
          >
            {imageError
              ? <WorkbenchError code={imageError} onRetry={onRetryImage} />
              : imageProgress && imageProgress.totalChunks > 0
                ? `正在读取页图（${imageProgress.loadedChunks} / ${imageProgress.totalChunks} 块）`
                : isLoading ? "正在解析页面资源…" : "选择页面以查看图像"}
          </div>
        )}
        {!regionsLoading && noRegions && (
          <div data-testid="viewer-no-regions" role="status" style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", color: "#6b7280", fontSize: 12, pointerEvents: "none" }}>
            本页暂无 Region
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
        </div>
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
              background: "#fff",
              border: `1px solid ${relabelFeedback.isError ? "#cf222e" : "#d9d9d6"}`,
              borderRadius: 6,
              padding: "6px 10px",
              fontSize: 11,
              color: relabelFeedback.isError ? "#cf222e" : "#1f2328",
              boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
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
                    background: "#fff",
                    color: "#1f2328",
                    border: "1px solid #d9d9d6",
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
                    background: "#fff",
                    color: canRerender && !rerenderBusy ? "#1f2328" : "#6b7280",
                    border: "1px solid #d9d9d6",
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
