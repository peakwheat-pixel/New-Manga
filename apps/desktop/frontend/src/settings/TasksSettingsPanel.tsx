import { useMemo } from "react";
import type { SettingsClient } from "./client";
import { SectionPanelFrame } from "./SectionPanelFrame";
import { SettingsField, settingsInputStyle, textFieldHandlers } from "./SectionField";
import {
  DEFAULT_RETRY_BACKOFF_SECONDS,
  DEFAULT_RETRY_MAX_ATTEMPTS,
  DEFAULT_TASKS_SETTINGS_DRAFT,
  RETRY_BACKOFF_SECONDS_MAX,
  RETRY_BACKOFF_SECONDS_MIN,
  RETRY_MAX_ATTEMPTS_MAX,
  RETRY_MAX_ATTEMPTS_MIN,
  TASKS_SECTION,
  describeTasksSettings,
  normalizeTasksSettings,
  tasksSettingsValues,
  validateTasksSettingsDraft,
  type TasksSettingsDraft,
} from "./sections";
import { useSettingsSection } from "./useSettingsSection";
import { tokens } from "../theme/tokens";

/**
 * SETTINGS-OPEN-B-1 §4.2 — tasks / concurrency (section `tasks`):
 * `retry_max_attempts` (int 1–3, default 3) and `retry_backoff_seconds`
 * (float 0.1–30, default 1.0). Both feed the per-Run RetryPolicy constructed
 * by the handlers; the concurrency count is a forced invariant
 * (`max_parallel_pages = 1` / `max_parallel_steps = 1`) and is surfaced as a
 * read-only "任务串行执行" note instead of a fake control (design §4.2).
 */
export function TasksSettingsPanel({ client }: { client: SettingsClient }) {
  const { phase, unset, effective, draft, setDraft, saving, loadError, saveError, save, reload } =
    useSettingsSection<TasksSettingsDraft>({
      client,
      section: TASKS_SECTION,
      defaults: DEFAULT_TASKS_SETTINGS_DRAFT,
      normalize: normalizeTasksSettings,
    });

  const errors = validateTasksSettingsDraft(draft);
  const hasErrors = Object.keys(errors).length > 0;
  const dirty = useMemo(
    () => JSON.stringify(draft) !== JSON.stringify(effective ?? DEFAULT_TASKS_SETTINGS_DRAFT),
    [draft, effective],
  );
  const ready = phase === "ready";

  return (
    <SectionPanelFrame
      testId="tasks-settings-panel"
      title="任务 / 并发"
      description="tasks.retry_max_attempts / tasks.retry_backoff_seconds — 失败重试策略；每次 Run 启动时据此构造 RetryPolicy。"
      phase={phase}
      loadError={loadError}
      onRetry={() => void reload()}
      unset={unset}
      unsetText={`该节未设置（Core 返回 JSON null）——当前沿用 Core 默认重试策略：retry_max_attempts=${DEFAULT_RETRY_MAX_ATTEMPTS}，retry_backoff_seconds=${DEFAULT_RETRY_BACKOFF_SECONDS.toFixed(1)}。`}
      saving={saving}
      saveError={saveError}
      saveDisabled={!ready || !dirty || hasErrors}
      statusText={hasErrors ? "存在校验错误，无法保存" : dirty ? "有未保存的改动" : "无改动"}
      onSave={() => void save(tasksSettingsValues(draft))}
      effectiveText={describeTasksSettings(effective)}
    >
      <div
        data-testid="tasks-settings-panel-serial-note"
        style={{
          padding: tokens.spacing.sm,
          border: `1px dashed ${tokens.color.border.default}`,
          borderRadius: tokens.radius.button,
          color: tokens.color.text.secondary,
          fontSize: tokens.typography.size.secondary,
          lineHeight: tokens.typography.lineHeight,
        }}
      >
        只读说明：任务串行执行（并发数不开放）——调度器固定 max_parallel_pages=1 /
        max_parallel_steps=1，本批不提供并发数控件。
      </div>

      <SettingsField
        id="tasks-retry-max-attempts"
        label="最大尝试次数 (retry_max_attempts)"
        hint={`整数 ${RETRY_MAX_ATTEMPTS_MIN}–${RETRY_MAX_ATTEMPTS_MAX}，默认 ${DEFAULT_RETRY_MAX_ATTEMPTS}。`}
        error={errors.retry_max_attempts}
      >
        <input
          id="tasks-retry-max-attempts"
          data-testid="tasks-retry-max-attempts"
          type="number"
          inputMode="numeric"
          min={RETRY_MAX_ATTEMPTS_MIN}
          max={RETRY_MAX_ATTEMPTS_MAX}
          step={1}
          value={draft.retry_max_attempts}
          disabled={saving}
          aria-invalid={errors.retry_max_attempts !== undefined}
          {...textFieldHandlers(setDraft, "retry_max_attempts")}
          style={settingsInputStyle}
        />
      </SettingsField>

      <SettingsField
        id="tasks-retry-backoff-seconds"
        label="重试退避秒数 (retry_backoff_seconds)"
        hint={`${RETRY_BACKOFF_SECONDS_MIN}–${RETRY_BACKOFF_SECONDS_MAX}，默认 ${DEFAULT_RETRY_BACKOFF_SECONDS.toFixed(1)}。`}
        error={errors.retry_backoff_seconds}
      >
        <input
          id="tasks-retry-backoff-seconds"
          data-testid="tasks-retry-backoff-seconds"
          type="number"
          min={RETRY_BACKOFF_SECONDS_MIN}
          max={RETRY_BACKOFF_SECONDS_MAX}
          step={0.1}
          value={draft.retry_backoff_seconds}
          disabled={saving}
          aria-invalid={errors.retry_backoff_seconds !== undefined}
          {...textFieldHandlers(setDraft, "retry_backoff_seconds")}
          style={settingsInputStyle}
        />
      </SettingsField>
    </SectionPanelFrame>
  );
}
