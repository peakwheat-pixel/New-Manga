import { useMemo } from "react";
import type { SettingsClient } from "./client";
import { SectionPanelFrame } from "./SectionPanelFrame";
import { SettingsField, settingsSelectStyle } from "./SectionField";
import {
  DEFAULT_MODEL_GPU_SETTINGS_DRAFT,
  DEVICE_PREFERENCE_LABELS,
  DEVICE_PREFERENCE_VALUES,
  MODEL_GPU_SECTION,
  describeModelGpuSettings,
  modelGpuSettingsValues,
  normalizeModelGpuSettings,
  validateModelGpuSettingsDraft,
  type DevicePreference,
  type ModelGpuSettingsDraft,
} from "./sections";
import { useSettingsSection } from "./useSettingsSection";
import { tokens } from "../theme/tokens";

function ReadonlyNote({ testId, children }: { testId: string; children: string }) {
  return (
    <div
      data-testid={testId}
      style={{
        padding: tokens.spacing.sm,
        border: `1px dashed ${tokens.color.border.default}`,
        borderRadius: tokens.radius.button,
        color: tokens.color.text.secondary,
        fontSize: tokens.typography.size.secondary,
        lineHeight: tokens.typography.lineHeight,
      }}
    >
      {children}
    </div>
  );
}

/**
 * SETTINGS-OPEN-B-1 §4.1 — model / GPU (section `model_gpu`):
 * `device_preference` (auto | cpu | gpu, default auto) and
 * `allow_cpu_fallback` (default true). Only the preference and the user half
 * of the fallback rule are editable; actual device capability is probed by the
 * Provider at Run time, and GPU concurrency / model download stay closed in
 * this batch (design §4.1 "未开放") — so this panel renders explanation only
 * for those, never a fake control (§2.4 "不伪造").
 */
export function ModelGpuSettingsPanel({ client }: { client: SettingsClient }) {
  const { phase, unset, effective, draft, setDraft, saving, loadError, saveError, save, reload } =
    useSettingsSection<ModelGpuSettingsDraft>({
      client,
      section: MODEL_GPU_SECTION,
      defaults: DEFAULT_MODEL_GPU_SETTINGS_DRAFT,
      normalize: normalizeModelGpuSettings,
    });

  const errors = validateModelGpuSettingsDraft(draft);
  const hasErrors = Object.keys(errors).length > 0;
  const dirty = useMemo(
    () =>
      JSON.stringify(draft) !==
      JSON.stringify(effective ?? DEFAULT_MODEL_GPU_SETTINGS_DRAFT),
    [draft, effective],
  );
  const ready = phase === "ready";

  return (
    <SectionPanelFrame
      testId="model-gpu-settings-panel"
      title="模型 / GPU"
      description="model_gpu.device_preference / model_gpu.allow_cpu_fallback — 设备偏好与 CPU 回退策略；auto 保持既有行为，显式偏好由 DeviceManager 在 Run 启动时校验。"
      phase={phase}
      loadError={loadError}
      onRetry={() => void reload()}
      unset={unset}
      unsetText={`该节未设置（Core 返回 JSON null）——当前按 Core 默认值运行：device_preference=auto，allow_cpu_fallback=true（允许 CPU 回退）。`}
      saving={saving}
      saveError={saveError}
      saveDisabled={!ready || !dirty || hasErrors}
      statusText={hasErrors ? "存在校验错误，无法保存" : dirty ? "有未保存的改动" : "无改动"}
      onSave={() => void save(modelGpuSettingsValues(draft))}
      effectiveText={describeModelGpuSettings(effective)}
    >
      <ReadonlyNote testId="model-gpu-settings-panel-runtime-note">
        只读说明：GPU / CPU 设备能力由 Provider 在运行时探测（此处不展示探测结果，也不提供设备状态面板）；本设置只表达偏好与回退策略。
      </ReadonlyNote>

      <ReadonlyNote testId="model-gpu-settings-panel-scope-note">
        本批不开放：GPU 并发策略（单槽 gate 是既有不变量）、模型下载 / 路径管理。
      </ReadonlyNote>

      <SettingsField
        id="model-gpu-device-preference"
        label="设备偏好 (device_preference)"
        hint={`默认：${DEVICE_PREFERENCE_LABELS[DEFAULT_MODEL_GPU_SETTINGS_DRAFT.device_preference]}；auto 保持历史行为。`}
      >
        <select
          id="model-gpu-device-preference"
          data-testid="model-gpu-device-preference"
          value={draft.device_preference}
          disabled={saving}
          onChange={(event) => {
            const next = event.target.value;
            if ((DEVICE_PREFERENCE_VALUES as readonly string[]).includes(next)) {
              setDraft((prev) => ({ ...prev, device_preference: next as DevicePreference }));
            }
          }}
          style={settingsSelectStyle}
        >
          {DEVICE_PREFERENCE_VALUES.map((value) => (
            <option key={value} value={value}>
              {DEVICE_PREFERENCE_LABELS[value]}
            </option>
          ))}
        </select>
      </SettingsField>

      <SettingsField
        id="model-gpu-allow-cpu-fallback"
        label="允许 CPU 回退 (allow_cpu_fallback)"
        hint="默认开启。仅当 Provider 声明支持 CPU 回退且此开关开启时，GPU 不可用才回退 CPU；禁止回退时 GPU 不可用会让该任务以设备不可用错误结束。"
        error={errors.allow_cpu_fallback}
      >
        <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm }}>
          <input
            id="model-gpu-allow-cpu-fallback"
            data-testid="model-gpu-allow-cpu-fallback"
            type="checkbox"
            checked={draft.allow_cpu_fallback}
            disabled={saving}
            aria-invalid={errors.allow_cpu_fallback !== undefined}
            onChange={(event) =>
              setDraft((prev) => ({ ...prev, allow_cpu_fallback: event.target.checked }))
            }
            style={{ width: 16, height: 16, cursor: saving ? "not-allowed" : "pointer" }}
          />
          <span
            data-testid="model-gpu-allow-cpu-fallback-state"
            style={{
              fontSize: tokens.typography.size.secondary,
              color: tokens.color.text.secondary,
            }}
          >
            {draft.allow_cpu_fallback ? "已允许回退" : "禁止回退"}
          </span>
        </div>
      </SettingsField>
    </SectionPanelFrame>
  );
}
