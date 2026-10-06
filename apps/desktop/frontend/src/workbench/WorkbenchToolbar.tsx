/**
 * <WorkbenchToolbar> — first-slice toolbar (M2-UI1 §2.2 mapping: QML
 * `WorkbenchToolbar.qml`). Renders the context readout only; the retype
 * entries live at the region level (Inspector buttons + overlay context
 * menu, M2-SFX-MISROUTE-UI-IMPL-1) — the toolbar carries no retype control
 * (the first-slice reserved placeholder was retired by that Task). The
 * start-translate command face and the viewer-mode toggles belong to later
 * parity slices.
 */

export interface WorkbenchToolbarProps {
  contextInfo: string;
  regionCount: number;
}

export function WorkbenchToolbar({ contextInfo, regionCount }: WorkbenchToolbarProps) {
  return (
    <section
      data-testid="workbench-toolbar"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        border: "1px solid #2a3038",
        borderRadius: 6,
        padding: "6px 10px",
      }}
    >
      <span data-testid="toolbar-context" style={{ fontSize: 12, color: "#d8e0e8" }}>
        {contextInfo}
      </span>
      <span data-testid="toolbar-region-count" style={{ fontSize: 11, color: "#8a94a2" }}>
        regions: {regionCount}
      </span>
    </section>
  );
}
