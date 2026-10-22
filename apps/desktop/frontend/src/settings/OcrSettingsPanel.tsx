import { useMemo } from "react";
import type { SettingsClient } from "./client";
import { SectionPanelFrame } from "./SectionPanelFrame";
import { SettingsField, settingsSelectStyle } from "./SectionField";
import {
  DEFAULT_OCR_SETTINGS,
  OCR_DIRECTION_LABELS,
  OCR_DIRECTION_VALUES,
  OCR_SCRIPT_LABELS,
  OCR_SCRIPT_VALUES,
  OCR_SECTION,
  describeOcrSettings,
  normalizeOcrSettings,
  type OcrDirection,
  type OcrScript,
  type OcrSettings,
} from "./sections";
import { useSettingsSection } from "./useSettingsSection";

/**
 * SETTINGS-OPEN-A-1 §3.1 — OCR section (`ocr`): two enum keys consumed by the
 * OCR handler from the Run settings snapshot (`script` default japanese,
 * `direction` default horizontal). No other key of the section is editable
 * here; state machine copied from SfxPolicyControl (loading / load-error /
 * unset / ready / saving / save-error).
 */
export function OcrSettingsPanel({ client }: { client: SettingsClient }) {
  const { phase, unset, effective, draft, setDraft, saving, loadError, saveError, save, reload } =
    useSettingsSection<OcrSettings>({
      client,
      section: OCR_SECTION,
      defaults: DEFAULT_OCR_SETTINGS,
      normalize: normalizeOcrSettings,
    });

  const dirty = useMemo(
    () => JSON.stringify(draft) !== JSON.stringify(effective ?? DEFAULT_OCR_SETTINGS),
    [draft, effective],
  );
  const ready = phase === "ready";

  return (
    <SectionPanelFrame
      testId="ocr-settings-panel"
      title="OCR 参数"
      description="ocr.script / ocr.direction — 识别脚本与文字方向；其余 OCR 键本批不开放。"
      phase={phase}
      loadError={loadError}
      onRetry={() => void reload()}
      unset={unset}
      unsetText={`该节未设置（Core 返回 JSON null）——当前按 Core 默认值运行：脚本 ${OCR_SCRIPT_LABELS[DEFAULT_OCR_SETTINGS.script]}，方向 ${OCR_DIRECTION_LABELS[DEFAULT_OCR_SETTINGS.direction]}。`}
      saving={saving}
      saveError={saveError}
      saveDisabled={!ready || !dirty}
      statusText={dirty ? "有未保存的改动" : "无改动"}
      onSave={() => void save({ script: draft.script, direction: draft.direction })}
      effectiveText={describeOcrSettings(effective)}
    >
      <SettingsField
        id="ocr-script"
        label="识别脚本 (ocr.script)"
        hint={`默认：${OCR_SCRIPT_LABELS[DEFAULT_OCR_SETTINGS.script]}`}
      >
        <select
          id="ocr-script"
          data-testid="ocr-script"
          value={draft.script}
          disabled={saving}
          onChange={(event) => {
            const next = event.target.value;
            if ((OCR_SCRIPT_VALUES as readonly string[]).includes(next)) {
              setDraft((prev) => ({ ...prev, script: next as OcrScript }));
            }
          }}
          style={settingsSelectStyle}
        >
          {OCR_SCRIPT_VALUES.map((value) => (
            <option key={value} value={value}>
              {OCR_SCRIPT_LABELS[value]}
            </option>
          ))}
        </select>
      </SettingsField>

      <SettingsField
        id="ocr-direction"
        label="文字方向 (ocr.direction)"
        hint={`默认：${OCR_DIRECTION_LABELS[DEFAULT_OCR_SETTINGS.direction]}`}
      >
        <select
          id="ocr-direction"
          data-testid="ocr-direction"
          value={draft.direction}
          disabled={saving}
          onChange={(event) => {
            const next = event.target.value;
            if ((OCR_DIRECTION_VALUES as readonly string[]).includes(next)) {
              setDraft((prev) => ({ ...prev, direction: next as OcrDirection }));
            }
          }}
          style={settingsSelectStyle}
        >
          {OCR_DIRECTION_VALUES.map((value) => (
            <option key={value} value={value}>
              {OCR_DIRECTION_LABELS[value]}
            </option>
          ))}
        </select>
      </SettingsField>
    </SectionPanelFrame>
  );
}
