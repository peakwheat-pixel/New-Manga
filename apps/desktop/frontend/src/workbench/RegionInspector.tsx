/**
 * <RegionInspector> — inspector (M2-UI1 §2.2 mapping: QML
 * `RegionInspector.qml`). First slice showed the selected region row
 * verbatim from the read projection; M2-SFX-MISROUTE-UI-IMPL-1 adds the
 * SECOND retype entry (design §3.2 dual entry: context menu + Inspector
 * buttons), the suspect-flag line, and the policy-snapshot note.
 *
 * A9 discipline: every label is a LOOKUP of Core snapshot values (the
 * shared relabelMachine tables) — the UI never decides translation
 * behaviour. A12: retype buttons exist for speech<->sfx only; anything
 * else renders disabled WITH the reason. The revision-history entry
 * (design §4.3 "常驻历史入口") renders honestly disabled: Core exposes no
 * ListRegionRevisions runtime command yet (RC-4 domain) — registered
 * deviation.
 */

import type { RegionSummary, RegionType } from "../region/types";
import {
  RELABEL_SOURCE_SAFETY_NOTE,
  canRetype,
  derivePhase,
  type SuspectSet,
} from "./relabelMachine";

const WARN_TEXT = "var(--st-warn-t, #fbbf24)";
const SKIP_TEXT = "var(--st-skip, #7eb287)";

const POLICY_SNAPSHOT_LABELS: Record<string, string> = {
  skip: "跳过翻译 (skip)",
  manual: "手动处理模式 (manual)",
  translate: "拟声词翻译链 (translate)",
};

export interface RegionInspectorProps {
  region: RegionSummary | null;
  suspects?: SuspectSet;
  busy?: boolean;
  /** The confirm dialog owns the reverse-retype flow; the Inspector only
   * raises the request. */
  onRetypeRequest?: (region: RegionSummary, to: RegionType) => void;
  onToggleSuspect?: (regionId: string) => void;
}

export function RegionInspector({
  region,
  suspects,
  busy = false,
  onRetypeRequest,
  onToggleSuspect,
}: RegionInspectorProps) {
  const phase = region ? derivePhase(region, suspects ?? new Set()) : null;
  const toSfx = region ? canRetype(region, "sfx") : null;
  const toSpeech = region ? canRetype(region, "speech") : null;
  const suspect = phase === "SPEECH_SUSPECT";
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
          <dd data-testid="inspector-region-type" style={{ margin: 0, color: "#d8e0e8" }}>
            {region.region_type}
            {suspect && (
              <span
                data-testid="inspector-suspect-flag"
                style={{ color: WARN_TEXT, marginLeft: 6 }}
                title="疑似拟声词（人工标记，UI 辅助信号，不影响翻译决策）"
              >
                ♪? 疑似拟声词
              </span>
            )}
          </dd>
          <dt style={{ color: "#8a94a2" }}>sfx_policy</dt>
          <dd data-testid="inspector-sfx-policy" style={{ margin: 0, color: "#d8e0e8" }}>{region.sfx_policy}</dd>
          <dt style={{ color: "#8a94a2" }}>origin</dt>
          <dd data-testid="inspector-origin" style={{ margin: 0, color: "#d8e0e8" }}>{region.origin}</dd>
          <dt style={{ color: "#8a94a2" }}>revision_no</dt>
          <dd data-testid="inspector-revision-no" style={{ margin: 0, color: "#d8e0e8" }}>{region.revision_no}</dd>
        </dl>
      )}
      {region && (
        <p
          data-testid="inspector-policy-note"
          style={{ margin: 0, fontSize: 10, color: "#8a94a2" }}
        >
          当前该 region 策略快照：{POLICY_SNAPSHOT_LABELS[region.sfx_policy] ?? region.sfx_policy}
          。{RELABEL_SOURCE_SAFETY_NOTE}。撤销/历史入口待 Core restore 命令面 Task 落地后启用（当前 UI 通道未开通）。
        </p>
      )}
      {region && toSfx && toSpeech && onRetypeRequest && (
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {toSfx.enabled && (
            <button
              type="button"
              data-testid="inspector-mark-sfx"
              disabled={busy}
              onClick={() => onRetypeRequest(region, "sfx")}
              style={{
                background: "#12201a",
                color: SKIP_TEXT,
                border: "1px solid #2a4436",
                borderRadius: 4,
                padding: "4px 8px",
                fontSize: 11,
                cursor: busy ? "wait" : "pointer",
                textAlign: "left",
              }}
            >
              标记为拟声词 (sfx)
            </button>
          )}
          {toSpeech.enabled && (
            <button
              type="button"
              data-testid="inspector-retype-speech"
              disabled={busy}
              onClick={() => onRetypeRequest(region, "speech")}
              style={{
                background: "#221a10",
                color: "#e0b070",
                border: "1px solid #4a3a20",
                borderRadius: 4,
                padding: "4px 8px",
                fontSize: 11,
                cursor: busy ? "wait" : "pointer",
                textAlign: "left",
              }}
            >
              改回对白 (speech)…
            </button>
          )}
          {!toSfx.enabled && !toSpeech.enabled && (
            <p
              data-testid="inspector-retype-disabled-reason"
              style={{ margin: 0, fontSize: 10, color: "#5a6470" }}
            >
              改标不可用：{toSfx.reason}
            </p>
          )}
          {region.region_type === "speech" && onToggleSuspect && (
            <button
              type="button"
              data-testid="inspector-toggle-suspect"
              disabled={busy}
              onClick={() => onToggleSuspect(region.region_id)}
              style={{
                background: "#101418",
                color: suspect ? WARN_TEXT : "#d8e0e8",
                border: `1px solid ${suspect ? "#4a3a20" : "#2a3038"}`,
                borderRadius: 4,
                padding: "4px 8px",
                fontSize: 11,
                cursor: busy ? "wait" : "pointer",
                textAlign: "left",
              }}
            >
              {suspect ? "取消疑似拟声词标记" : "标记为疑似拟声词 ♪?"}
            </button>
          )}
          <button
            type="button"
            data-testid="inspector-revision-history"
            disabled
            title="revision 历史列表待 Core ListRegionRevisions 命令面（RC-4 域）落地后启用"
            style={{
              background: "#101418",
              color: "#5a6470",
              border: "1px solid #2a3038",
              borderRadius: 4,
              padding: "4px 8px",
              fontSize: 11,
              cursor: "not-allowed",
              textAlign: "left",
            }}
          >
            历史（预留）
          </button>
        </div>
      )}
    </section>
  );
}
