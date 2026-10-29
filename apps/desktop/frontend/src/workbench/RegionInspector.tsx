import { useState } from "react";

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
 * (design §4.3 "常驻历史入口") reads the frozen RC-4 revision summary and
 * requires explicit confirmation before restoring a historical snapshot.
 */

import type { RegionSummary, RegionType, RevisionSummary } from "../region/types";
import { DisabledFeature } from "./DisabledFeature";
import {
  RELABEL_SOURCE_SAFETY_NOTE,
  canRetype,
  derivePhase,
  type SuspectSet,
} from "./relabelMachine";

const WARN_TEXT = "#9a6700";
const SKIP_TEXT = "#1a7f37";

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
  revisions?: RevisionSummary[] | null;
  currentRevisionNo?: number | null;
  historyBusy?: boolean;
  historyError?: string | null;
  restoreBusy?: boolean;
  restoreError?: string | null;
  onLoadHistory?: (regionId: string) => void;
  onRestoreRevision?: (revision: RevisionSummary) => Promise<boolean>;
}

export function RegionInspector({
  region,
  suspects,
  busy = false,
  onRetypeRequest,
  onToggleSuspect,
  revisions = null,
  currentRevisionNo = null,
  historyBusy = false,
  historyError = null,
  restoreBusy = false,
  restoreError = null,
  onLoadHistory,
  onRestoreRevision,
}: RegionInspectorProps) {
  const [restoreTarget, setRestoreTarget] = useState<RevisionSummary | null>(null);
  const phase = region ? derivePhase(region, suspects ?? new Set()) : null;
  const toSfx = region ? canRetype(region, "sfx") : null;
  const toSpeech = region ? canRetype(region, "speech") : null;
  const suspect = phase === "SPEECH_SUSPECT";
  return (
    <section
      data-testid="region-inspector"
      style={{
        border: "1px solid #d9d9d6",
        background: "#fff",
        borderRadius: 6,
        padding: 8,
        minWidth: 220,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <h2 style={{ fontSize: 12, margin: 0, color: "#1f2328" }}>Inspector</h2>
      {!region && (
        <p data-testid="inspector-empty" style={{ color: "#6b7280", fontSize: 11, margin: 0 }}>
          no region selected
        </p>
      )}
      {region && (
        <dl
          data-testid={`inspector-row-${region.region_id}`}
          style={{ margin: 0, display: "grid", gridTemplateColumns: "auto 1fr", gap: "2px 8px", fontSize: 11 }}
        >
          <dt style={{ color: "#6b7280" }}>region_id</dt>
          <dd style={{ margin: 0, color: "#1f2328", fontFamily: "Consolas, monospace" }}>{region.region_id}</dd>
          <dt style={{ color: "#6b7280" }}>region_type</dt>
          <dd data-testid="inspector-region-type" style={{ margin: 0, color: "#1f2328" }}>
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
          <dt style={{ color: "#6b7280" }}>sfx_policy</dt>
          <dd data-testid="inspector-sfx-policy" style={{ margin: 0, color: "#1f2328" }}>{region.sfx_policy}</dd>
          <dt style={{ color: "#6b7280" }}>origin</dt>
          <dd data-testid="inspector-origin" style={{ margin: 0, color: "#1f2328" }}>{region.origin}</dd>
          <dt style={{ color: "#6b7280" }}>revision_no</dt>
          <dd data-testid="inspector-revision-no" style={{ margin: 0, color: "#1f2328" }}>{region.revision_no}</dd>
        </dl>
      )}
      {region && (
        <p
          data-testid="inspector-policy-note"
          style={{ margin: 0, fontSize: 10, color: "#6b7280" }}
        >
          当前该 region 策略快照：{POLICY_SNAPSHOT_LABELS[region.sfx_policy] ?? region.sfx_policy}
          。{RELABEL_SOURCE_SAFETY_NOTE}。撤销仅在改标后 10 秒内、当前页且没有新操作时可用；修订历史可读取，恢复旧修订前需要确认。
        </p>
      )}
      <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 11, color: "#6b7280" }}>
        人工译文
        <textarea data-testid="manual-translation-input" disabled placeholder="等待译文保存能力接入" rows={3} />
      </label>
      <DisabledFeature id="gap-g9-save-manual-translation" label="保存人工译文" reason="SaveManualTranslation 写入接口尚未冻结，因此人工译文与 Ctrl+Enter 提交保持禁用。" />
      <DisabledFeature id="gap-g12-region-lock" label="设置/解除锁定" reason="Lock 写入接口尚未冻结；当前锁态只读显示。" />
      <DisabledFeature id="gap-g13-revision-pin" label="固定此修订" reason="Revision pin 写入接口尚未冻结；历史固定状态只读显示。" />
      {region && toSfx && toSpeech && onRetypeRequest && (
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {toSfx.enabled && (
            <button
              type="button"
              data-testid="inspector-mark-sfx"
              disabled={busy}
              onClick={() => onRetypeRequest(region, "sfx")}
              style={{
                background: "#f1f8f3",
                color: SKIP_TEXT,
                border: "1px solid #b7dfc4",
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
                background: "#fff8e8",
                color: "#7a4b00",
                border: "1px solid #e7c17a",
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
              style={{ margin: 0, fontSize: 10, color: "#6b7280" }}
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
                background: "#fff",
                color: suspect ? WARN_TEXT : "#1f2328",
                border: `1px solid ${suspect ? "#e7c17a" : "#d9d9d6"}`,
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
            disabled={busy || historyBusy}
            aria-expanded={revisions !== null}
            onClick={() => onLoadHistory?.(region.region_id)}
            style={{
              background: "#fff",
              color: busy || historyBusy ? "#6b7280" : "#1f2328",
              border: "1px solid #d9d9d6",
              borderRadius: 4,
              padding: "4px 8px",
              fontSize: 11,
              cursor: busy || historyBusy ? "wait" : "pointer",
              textAlign: "left",
            }}
          >
            {historyBusy ? "读取历史中…" : revisions === null ? "修订历史" : "刷新修订历史"}
          </button>
          {historyError && (
            <p data-testid="inspector-history-error" role="alert" style={{ margin: 0, fontSize: 10, color: "var(--wb-fail, #e07a7a)" }}>
              历史读取失败：{historyError}
            </p>
          )}
          {revisions && (
            <ol data-testid="inspector-revision-list" style={{ margin: 0, paddingLeft: 20, display: "flex", flexDirection: "column", gap: 4, fontSize: 10 }}>
              {revisions.length === 0 && <li style={{ color: "#6b7280" }}>暂无修订记录</li>}
              {revisions.map((revision) => {
                const source = revision.restored_from_revision_id
                  ? revisions.find((item) => item.region_revision_id === revision.restored_from_revision_id)
                  : undefined;
                return (
                  <li key={revision.region_revision_id} data-testid={`inspector-revision-${revision.revision_no}`}>
                    <div style={{ color: "#1f2328" }}>
                      revision {revision.revision_no} · {revision.origin} · {revision.review_state} · {revision.region_type} · {revision.sfx_policy} · {revision.created_at}
                      {revision.is_current && " · 当前"}
                      {revision.is_pinned && " · 已固定"}
                    </div>
                    {revision.restored_from_revision_id && (
                      <div style={{ color: "#6b7280" }}>
                        来源：revision {source?.revision_no ?? revision.restored_from_revision_id}
                      </div>
                    )}
                    <button
                      type="button"
                      data-testid={`restore-revision-${revision.revision_no}`}
                      disabled={busy || restoreBusy || revision.is_current}
                      onClick={() => setRestoreTarget(revision)}
                      style={{
                        marginTop: 2,
                        background: "#fff",
                        color: revision.is_current || busy || restoreBusy ? "#6b7280" : "#1f2328",
                        border: "1px solid #d9d9d6",
                        borderRadius: 4,
                        padding: "2px 6px",
                        fontSize: 10,
                        cursor: revision.is_current || busy || restoreBusy ? "not-allowed" : "pointer",
                      }}
                    >
                      {revision.is_current ? "当前修订" : "恢复此修订…"}
                    </button>
                  </li>
                );
              })}
            </ol>
          )}
        </div>
      )}
      {restoreTarget && (
        <div
          data-testid="revision-restore-overlay"
          style={{ position: "fixed", inset: 0, zIndex: 40, background: "rgba(0,0,0,0.45)", display: "flex", alignItems: "center", justifyContent: "center" }}
          onClick={() => { if (!restoreBusy) setRestoreTarget(null); }}
        >
          <div
            data-testid="revision-restore-dialog"
            role="dialog"
            aria-modal="true"
            style={{ background: "#fff", color: "#1f2328", border: "1px solid #e7c17a", borderRadius: 8, padding: 12, width: 320, display: "flex", flexDirection: "column", gap: 8 }}
            onClick={(event) => event.stopPropagation()}
          >
            <strong style={{ fontSize: 12, color: "#7a4b00" }}>恢复 revision {restoreTarget.revision_no}？</strong>
            <p data-testid="revision-restore-target" style={{ margin: 0, fontSize: 11, color: "#1f2328" }}>
              目标：revision {restoreTarget.revision_no} · {restoreTarget.origin} · {restoreTarget.region_type} · {restoreTarget.sfx_policy}
              {restoreTarget.is_pinned ? " · 已固定" : ""}
              {restoreTarget.restored_from_revision_id ? ` · 来源 ${restoreTarget.restored_from_revision_id}` : ""}
            </p>
            <p style={{ margin: 0, fontSize: 10, color: "#6b7280" }}>
              将恢复该修订的文字、类型、策略与锁状态（可能回退当前锁）；当前 revision {currentRevisionNo ?? region?.revision_no ?? "未知"} 与历史都会保留，Core 会新增 restored revision，不改动原图。
            </p>
            {restoreError && (
              <p data-testid="revision-restore-error" role="alert" style={{ margin: 0, fontSize: 11, color: "var(--wb-fail, #e07a7a)" }}>
                恢复失败：{restoreError}
              </p>
            )}
            <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
              <button type="button" data-testid="revision-restore-cancel" disabled={restoreBusy} onClick={() => setRestoreTarget(null)}>
                取消
              </button>
              <button
                type="button"
                data-testid="revision-restore-confirm"
                disabled={restoreBusy}
                onClick={async () => {
                  if (await onRestoreRevision?.(restoreTarget)) setRestoreTarget(null);
                }}
              >
                {restoreBusy ? "恢复中…" : `确认恢复 revision ${restoreTarget.revision_no}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
