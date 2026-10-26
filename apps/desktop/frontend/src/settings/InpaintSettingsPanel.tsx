import { useMemo } from "react";
import type { SettingsClient } from "./client";
import { SectionPanelFrame } from "./SectionPanelFrame";
import { SettingsField, settingsInputStyle, settingsSelectStyle, textFieldHandlers } from "./SectionField";
import {
  BACKGROUND_COMPLEXITY_LABELS,
  BACKGROUND_COMPLEXITY_VALUES,
  DEFAULT_INPAINT_SETTINGS_DRAFT,
  DILATE_RADIUS_MAX,
  DILATE_RADIUS_MIN,
  ERODE_RADIUS_MAX,
  ERODE_RADIUS_MIN,
  INPAINT_QUALITY_LABELS,
  INPAINT_QUALITY_VALUES,
  INPAINT_SECTION,
  describeInpaintSettings,
  inpaintSettingsValues,
  normalizeInpaintSettings,
  validateInpaintSettingsDraft,
  type BackgroundComplexity,
  type InpaintQuality,
  type InpaintSettingsDraft,
} from "./sections";
import { useSettingsSection } from "./useSettingsSection";

/**
 * SETTINGS-OPEN-A-1 §3.3 — inpaint section (`inpaint`): preferred_quality
 * (fast/balanced/quality, default balanced), background_complexity
 * (low/medium/high, default low), dilate_radius (0–10, default 2) and
 * erode_radius (0–10, default 0). Region-level routing signals and
 * route_policy stay internal / closed (design §3.3).
 */
export function InpaintSettingsPanel({ client }: { client: SettingsClient }) {
  const { phase, unset, effective, draft, setDraft, saving, loadError, saveError, save, reload } =
    useSettingsSection<InpaintSettingsDraft>({
      client,
      section: INPAINT_SECTION,
      defaults: DEFAULT_INPAINT_SETTINGS_DRAFT,
      normalize: normalizeInpaintSettings,
    });

  const errors = validateInpaintSettingsDraft(draft);
  const hasErrors = Object.keys(errors).length > 0;
  const dirty = useMemo(
    () =>
      JSON.stringify(draft) !== JSON.stringify(effective ?? DEFAULT_INPAINT_SETTINGS_DRAFT),
    [draft, effective],
  );
  const ready = phase === "ready";

  return (
    <SectionPanelFrame
      testId="inpaint-settings-panel"
      title="图片修复"
      description="inpaint.preferred_quality / background_complexity / dilate_radius / erode_radius — 质量越高通常越慢。"
      phase={phase}
      loadError={loadError}
      onRetry={() => void reload()}
      unset={unset}
      unsetText={`该节未设置（Core 返回 JSON null）——当前按 Core 默认值运行：preferred_quality=${DEFAULT_INPAINT_SETTINGS_DRAFT.preferred_quality}，background_complexity=${DEFAULT_INPAINT_SETTINGS_DRAFT.background_complexity}，dilate_radius=${DEFAULT_INPAINT_SETTINGS_DRAFT.dilate_radius}，erode_radius=${DEFAULT_INPAINT_SETTINGS_DRAFT.erode_radius}。`}
      saving={saving}
      saveError={saveError}
      saveDisabled={!ready || !dirty || hasErrors}
      statusText={hasErrors ? "存在校验错误，无法保存" : dirty ? "有未保存的改动" : "无改动"}
      onSave={() => void save(inpaintSettingsValues(draft))}
      effectiveText={describeInpaintSettings(effective)}
    >
      <SettingsField
        id="inpaint-preferred-quality"
        label="首选质量 (preferred_quality)"
        hint="质量越高越慢；默认 balanced。"
      >
        <select
          id="inpaint-preferred-quality"
          data-testid="inpaint-preferred-quality"
          value={draft.preferred_quality}
          disabled={saving}
          onChange={(event) => {
            const next = event.target.value;
            if ((INPAINT_QUALITY_VALUES as readonly string[]).includes(next)) {
              setDraft((prev) => ({ ...prev, preferred_quality: next as InpaintQuality }));
            }
          }}
          style={settingsSelectStyle}
        >
          {INPAINT_QUALITY_VALUES.map((value) => (
            <option key={value} value={value}>
              {INPAINT_QUALITY_LABELS[value]}
            </option>
          ))}
        </select>
      </SettingsField>

      <SettingsField
        id="inpaint-background-complexity"
        label="背景复杂度 (background_complexity)"
        hint="default low。"
      >
        <select
          id="inpaint-background-complexity"
          data-testid="inpaint-background-complexity"
          value={draft.background_complexity}
          disabled={saving}
          onChange={(event) => {
            const next = event.target.value;
            if ((BACKGROUND_COMPLEXITY_VALUES as readonly string[]).includes(next)) {
              setDraft((prev) => ({
                ...prev,
                background_complexity: next as BackgroundComplexity,
              }));
            }
          }}
          style={settingsSelectStyle}
        >
          {BACKGROUND_COMPLEXITY_VALUES.map((value) => (
            <option key={value} value={value}>
              {BACKGROUND_COMPLEXITY_LABELS[value]}
            </option>
          ))}
        </select>
      </SettingsField>

      <SettingsField
        id="inpaint-dilate-radius"
        label="膨胀半径 (dilate_radius)"
        hint={`整数 ${DILATE_RADIUS_MIN}–${DILATE_RADIUS_MAX}，默认 2；扩大掩膜以覆盖描边。`}
        error={errors.dilate_radius}
      >
        <input
          id="inpaint-dilate-radius"
          data-testid="inpaint-dilate-radius"
          type="number"
          inputMode="numeric"
          min={DILATE_RADIUS_MIN}
          max={DILATE_RADIUS_MAX}
          step={1}
          value={draft.dilate_radius}
          disabled={saving}
          aria-invalid={errors.dilate_radius !== undefined}
          {...textFieldHandlers(setDraft, "dilate_radius")}
          style={settingsInputStyle}
        />
      </SettingsField>

      <SettingsField
        id="inpaint-erode-radius"
        label="腐蚀半径 (erode_radius)"
        hint={`整数 ${ERODE_RADIUS_MIN}–${ERODE_RADIUS_MAX}，默认 0。`}
        error={errors.erode_radius}
      >
        <input
          id="inpaint-erode-radius"
          data-testid="inpaint-erode-radius"
          type="number"
          inputMode="numeric"
          min={ERODE_RADIUS_MIN}
          max={ERODE_RADIUS_MAX}
          step={1}
          value={draft.erode_radius}
          disabled={saving}
          aria-invalid={errors.erode_radius !== undefined}
          {...textFieldHandlers(setDraft, "erode_radius")}
          style={settingsInputStyle}
        />
      </SettingsField>
    </SectionPanelFrame>
  );
}
