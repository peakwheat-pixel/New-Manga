import {
  SETTINGS_ACTION_LABELS,
  SETTINGS_CATEGORY_LABELS,
  SETTINGS_MESSAGE_TEXT,
  type SettingsSurfaceError,
} from "./errors";
import { tokens } from "../theme/tokens";

/**
 * P15-C1 §9 — the only way a settings-surface error may reach the DOM.
 * Renders the fixed localized copy for the error's message_key plus the
 * closed category/phase/action labels; the underlying payload (message
 * text, details, paths, raw responses) never reaches this component.
 */
export function SettingsErrorBar({
  testId,
  error,
  onRetry,
}: {
  testId: string;
  error: SettingsSurfaceError;
  onRetry?: () => void;
}) {
  return (
    <div
      data-testid={testId}
      data-error-category={error.category}
      data-error-phase={error.phase}
      data-error-action={error.action}
      data-message-key={error.message_key}
      role="alert"
      style={{
        padding: tokens.spacing.md,
        background: "#fff1f0",
        border: `1px solid ${tokens.color.state.failed}`,
        borderRadius: tokens.radius.button,
        color: tokens.color.state.failed,
        fontSize: tokens.typography.size.base,
        lineHeight: tokens.typography.lineHeight,
      }}
    >
      <div style={{ fontWeight: 600 }}>
        {SETTINGS_CATEGORY_LABELS[error.category]}（阶段：{error.phase}）
      </div>
      <div data-testid={`${testId}-text`} style={{ marginTop: tokens.spacing.xs }}>
        {SETTINGS_MESSAGE_TEXT[error.message_key]}
      </div>
      <div style={{ marginTop: tokens.spacing.xs, display: "flex", gap: tokens.spacing.sm, alignItems: "center" }}>
        <span style={{ color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}>
          可采取动作：{SETTINGS_ACTION_LABELS[error.action] || "—"}
        </span>
        {error.action === "retry" && onRetry && (
          <button
            type="button"
            data-testid={`${testId}-retry`}
            onClick={onRetry}
            style={{
              padding: "2px 10px",
              fontSize: tokens.typography.size.secondary,
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              background: tokens.color.surface.card,
              color: tokens.color.text.primary,
              cursor: "pointer",
            }}
          >
            重试
          </button>
        )}
      </div>
    </div>
  );
}
