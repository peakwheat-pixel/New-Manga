/**
 * <WorkbenchToolbar> — first-slice toolbar (M2-UI1 §2.2 mapping: QML
 * `WorkbenchToolbar.qml`). This slice renders the context readout and the
 * RESERVED DISABLED retype entry; the start-translate command face and the
 * viewer-mode toggles belong to the later parity slices.
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
      {/* Reserved command entry — disabled in this slice (IMPL-1 owns the
          enabled flow); no command is invoked from here yet. */}
      <button
        type="button"
        data-testid="toolbar-retype-reserved"
        disabled
        title="改标入口属 M2-SFX-MISROUTE-UI-IMPL-1（本刀预留禁用态）"
        style={{
          background: "#161b22",
          color: "#5a6470",
          border: "1px solid #2a3038",
          borderRadius: 4,
          padding: "3px 8px",
          fontSize: 11,
          cursor: "not-allowed",
        }}
      >
        改标工具（预留）
      </button>
    </section>
  );
}
