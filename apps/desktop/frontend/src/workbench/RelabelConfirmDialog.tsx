/**
 * <RelabelConfirmDialog> — the explicit confirmation step for the DESTRUCTIVE
 * reverse retype sfx->speech (design §4.1 R3 / assertion A5: no one-click
 * path back into the speech chain).
 *
 * FROZEN copy obligations carried here:
 * - the consequence must be stated (re-enters the speech chain, may produce
 *   new translations) — RELABEL_X2S_CONFIRM_TEXT;
 * - the source-safety line ("only annotations change, never source files")
 *   is fixed copy — §4.3 / contract §10.
 *
 * Cancel/failure returns to the ORIGINATING state (guard ② — the caller
 * simply keeps the region untouched; nothing optimistic to roll back).
 */

import {
  RELABEL_SOURCE_SAFETY_NOTE,
  RELABEL_X2S_CONFIRM_TEXT,
} from "./relabelMachine";
import type { RegionSummary } from "../region/types";

const BORDER_FAIL = "var(--wb-fail, #e07a7a)";

export interface RelabelConfirmDialogProps {
  target: RegionSummary;
  busy: boolean;
  errorText: string | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export function RelabelConfirmDialog({
  target,
  busy,
  errorText,
  onConfirm,
  onCancel,
}: RelabelConfirmDialogProps) {
  return (
    <div
      data-testid="relabel-confirm-overlay"
      style={{
        position: "absolute",
        inset: 0,
        background: "rgba(0,0,0,0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 30,
      }}
      onClick={onCancel}
    >
      <div
        data-testid="relabel-confirm-dialog"
        role="dialog"
        aria-modal="true"
        style={{
          background: "var(--wb-bg-raised, #161b22)",
          border: `1px solid ${BORDER_FAIL}`,
          borderRadius: 8,
          padding: 12,
          maxWidth: 320,
          display: "flex",
          flexDirection: "column",
          gap: 8,
          boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
        }}
        onClick={(event) => event.stopPropagation()}
      >
        <strong style={{ fontSize: 12, color: BORDER_FAIL }}>
          ♪ 改回对白（speech）？
        </strong>
        <p data-testid="relabel-confirm-text" style={{ margin: 0, fontSize: 11, color: "#d8e0e8" }}>
          <span style={{ fontFamily: "Consolas, monospace" }}>{target.region_id}</span>
          ：{RELABEL_X2S_CONFIRM_TEXT}
        </p>
        <p style={{ margin: 0, fontSize: 10, color: "#8a94a2" }}>
          {RELABEL_SOURCE_SAFETY_NOTE}
        </p>
        {errorText && (
          <p
            data-testid="relabel-confirm-error"
            style={{ margin: 0, fontSize: 11, color: BORDER_FAIL }}
          >
            {errorText}
          </p>
        )}
        <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
          <button
            type="button"
            data-testid="relabel-confirm-cancel"
            onClick={onCancel}
            disabled={busy}
            style={{
              background: "#101418",
              color: "#d8e0e8",
              border: "1px solid #2a3038",
              borderRadius: 4,
              padding: "4px 10px",
              fontSize: 11,
              cursor: busy ? "wait" : "pointer",
            }}
          >
            取消
          </button>
          <button
            type="button"
            data-testid="relabel-confirm-accept"
            onClick={onConfirm}
            disabled={busy}
            style={{
              background: "#2a1518",
              color: BORDER_FAIL,
              border: `1px solid ${BORDER_FAIL}`,
              borderRadius: 4,
              padding: "4px 10px",
              fontSize: 11,
              cursor: busy ? "wait" : "pointer",
            }}
          >
            {busy ? "执行中…" : "确认改回对白"}
          </button>
        </div>
      </div>
    </div>
  );
}
