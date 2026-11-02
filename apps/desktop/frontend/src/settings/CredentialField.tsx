import { useState } from "react";
import { SettingsClient, SettingsClientError } from "./client";
import { projectSettingsError, type SettingsSurfaceError } from "./errors";
import type { CredentialState, CredentialTarget, CredentialIntent } from "./types";
import { SettingsErrorBar } from "./SettingsErrorBar";
import { tokens } from "../theme/tokens";

/**
 * G22 credential affordance (P15-C1 §4). The WebView NEVER collects,
 * echoes, or transports a Secret: `credential_put` only carries
 * (target, intent) and the Host opens its own secure input outside the
 * WebView. This component therefore renders no text inputs at all — only
 * the read-only state projection (configured | missing), the optional
 * masked hint, and the one-shot buttons.
 */
export function CredentialField({
  testId,
  client,
  state,
  hint,
  target,
  onCredentialChanged,
  phaseLabel,
}: {
  testId: string;
  client: SettingsClient;
  state: CredentialState;
  hint?: string;
  target: CredentialTarget;
  onCredentialChanged?: () => void;
  phaseLabel: string;
}) {
  const [busy, setBusy] = useState<null | "put" | "clear">(null);
  const [error, setError] = useState<SettingsSurfaceError | null>(null);
  const [lastHint, setLastHint] = useState<string | undefined>(hint);

  const intent: CredentialIntent = state === "configured" ? "replace" : "create";

  const runPut = async () => {
    setBusy("put");
    setError(null);
    try {
      const res = await client.putCredential(target, intent);
      setLastHint(res.masked_hint);
      onCredentialChanged?.();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setError(projectSettingsError(code, "credential_input"));
    } finally {
      setBusy(null);
    }
  };

  const runClear = async () => {
    setBusy("clear");
    setError(null);
    try {
      await client.clearCredential(target);
      setLastHint(undefined);
      onCredentialChanged?.();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setError(projectSettingsError(code, "credential_input"));
    } finally {
      setBusy(null);
    }
  };

  const buttonStyle = (kind: "primary" | "danger"): React.CSSProperties => ({
    padding: "2px 10px",
    fontSize: tokens.typography.size.secondary,
    border: `1px solid ${kind === "danger" ? tokens.color.state.failed : tokens.color.border.default}`,
    borderRadius: tokens.radius.button,
    background: kind === "danger" ? "#fff1f0" : tokens.color.surface.card,
    color: kind === "danger" ? tokens.color.state.failed : tokens.color.text.primary,
    cursor: busy ? "not-allowed" : "pointer",
    opacity: busy ? 0.45 : 1,
  });

  return (
    <div data-testid={testId} data-credential-state={state} style={{ display: "inline-flex", flexDirection: "column", gap: tokens.spacing.xs }}>
      <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm }}>
        <span
          data-testid={`${testId}-state`}
          style={{
            fontSize: tokens.typography.size.badge,
            padding: "1px 8px",
            borderRadius: tokens.radius.pill,
            background: state === "configured" ? "#e6f4ea" : "#f0f0ef",
            color: state === "configured" ? tokens.color.state.completed : tokens.color.text.muted,
            border: `1px solid ${state === "configured" ? tokens.color.state.completed : tokens.color.border.default}`,
          }}
        >
          {phaseLabel}凭据：{state === "configured" ? "已配置" : "未配置"}
        </span>
        {lastHint && (
          <span
            data-testid={`${testId}-hint`}
            style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}
          >
            ({lastHint})
          </span>
        )}
        <button
          type="button"
          data-testid={`${testId}-put-btn`}
          disabled={busy !== null}
          onClick={() => void runPut()}
          style={buttonStyle("primary")}
        >
          {busy === "put" ? "处理中…" : state === "configured" ? "替换凭据" : "配置凭据"}
        </button>
        {state === "configured" && (
          <button
            type="button"
            data-testid={`${testId}-clear-btn`}
            disabled={busy !== null}
            onClick={() => void runClear()}
            style={buttonStyle("danger")}
          >
            {busy === "clear" ? "清除中…" : "清除凭据"}
          </button>
        )}
      </div>
      {/* P15-C1 §4: no secret ever enters the WebView — there is no input
       * element in this component, by construction. */}
      {error && <SettingsErrorBar testId={`${testId}-error`} error={error} />}
    </div>
  );
}
