import type { ReactNode } from "react";
import type { SettingsSurfaceError } from "./errors";
import { SettingsErrorBar } from "./SettingsErrorBar";
import type { SettingsSectionPhase } from "./useSettingsSection";
import { tokens } from "../theme/tokens";

/** The §2 "快照语义不变" sentence every batch A panel must surface (design
 * §2.3): writes land in pipeline_defaults.settings and only affect Runs
 * started afterwards; a running Run keeps its frozen snapshot. */
export const SECTION_EFFECT_NOTE =
  "对之后启动的任务生效：保存写入默认设置，进行中的任务继续使用已冻结的设置快照。";

/**
 * The shared card / loading / error / unset / save frame for the four batch A
 * panels. It renders no values of its own — the panel supplies the form
 * fields (as children) and the persisted-value summary; the frame only owns
 * the lifecycle affordances copied from SfxPolicyControl.
 */
export function SectionPanelFrame({
  testId,
  title,
  description,
  phase,
  loadError,
  onRetry,
  unset,
  unsetText,
  children,
  saving,
  saveError,
  saveDisabled,
  statusText,
  onSave,
  effectiveText,
}: {
  testId: string;
  title: string;
  description: string;
  phase: SettingsSectionPhase;
  loadError: SettingsSurfaceError | null;
  onRetry: () => void;
  unset: boolean;
  unsetText: string;
  children: ReactNode;
  saving: boolean;
  saveError: SettingsSurfaceError | null;
  saveDisabled: boolean;
  statusText: string;
  onSave: () => void;
  effectiveText: string;
}) {
  const blocked = saving || saveDisabled;

  return (
    <section
      data-testid={testId}
      style={{
        padding: tokens.spacing.lg,
        backgroundColor: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        borderRadius: tokens.radius.card,
        maxWidth: 780,
      }}
    >
      <h3
        data-testid={`${testId}-title`}
        style={{
          margin: 0,
          marginBottom: tokens.spacing.sm,
          fontSize: tokens.typography.size.cardTitle,
          fontWeight: 600,
          color: tokens.color.text.primary,
        }}
      >
        {title}
      </h3>
      <p
        data-testid={`${testId}-description`}
        style={{
          margin: 0,
          marginBottom: tokens.spacing.xs,
          fontSize: tokens.typography.size.secondary,
          color: tokens.color.text.secondary,
        }}
      >
        {description}
      </p>
      <p
        data-testid={`${testId}-effect-note`}
        style={{
          margin: 0,
          marginBottom: tokens.spacing.md,
          fontSize: tokens.typography.size.secondary,
          color: tokens.color.text.secondary,
        }}
      >
        {SECTION_EFFECT_NOTE}
      </p>

      {phase === "loading" && (
        <div
          data-testid={`${testId}-loading`}
          aria-busy="true"
          style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}
        >
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                height: 14,
                borderRadius: tokens.radius.button,
                background: tokens.color.bg.toolbar,
                width: `${70 - i * 15}%`,
              }}
            />
          ))}
        </div>
      )}

      {phase === "error" && loadError && (
        <SettingsErrorBar testId={`${testId}-load-error`} error={loadError} onRetry={onRetry} />
      )}

      {phase === "ready" && (
        <>
          {unset && (
            <div
              data-testid={`${testId}-unset`}
              style={{
                marginBottom: tokens.spacing.md,
                padding: tokens.spacing.md,
                border: `1px dashed ${tokens.color.border.default}`,
                borderRadius: tokens.radius.button,
                color: tokens.color.text.secondary,
                fontSize: tokens.typography.size.secondary,
              }}
            >
              {unsetText}
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
            {children}
          </div>

          <div
            style={{
              marginTop: tokens.spacing.md,
              display: "flex",
              alignItems: "center",
              gap: tokens.spacing.md,
            }}
          >
            <button
              type="button"
              data-testid={`${testId}-save-btn`}
              disabled={blocked}
              aria-disabled={blocked}
              onClick={onSave}
              style={{
                padding: "4px 14px",
                fontSize: tokens.typography.size.base,
                border: `1px solid ${!blocked ? tokens.color.accent.primary : tokens.color.border.default}`,
                borderRadius: tokens.radius.button,
                background: !blocked ? tokens.color.accent.selected : tokens.color.bg.toolbar,
                color: tokens.color.text.primary,
                cursor: blocked ? "not-allowed" : "pointer",
                opacity: blocked ? 0.45 : 1,
              }}
            >
              {saving ? "保存中…" : "保存"}
            </button>
            <span
              data-testid={`${testId}-dirty-state`}
              style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}
            >
              {saving ? "正在保存并重新读取…" : statusText}
            </span>
          </div>

          {saveError && (
            <div style={{ marginTop: tokens.spacing.md }}>
              <SettingsErrorBar testId={`${testId}-save-error`} error={saveError} />
            </div>
          )}

          <div
            style={{
              marginTop: tokens.spacing.md,
              fontSize: tokens.typography.size.secondary,
              color: tokens.color.text.secondary,
            }}
          >
            当前持久化值：
            <span data-testid={`${testId}-effective`}>{effectiveText}</span>
          </div>
        </>
      )}
    </section>
  );
}
