import { useMemo } from "react";
import type { SettingsClient } from "./client";
import { SectionPanelFrame } from "./SectionPanelFrame";
import { SettingsField, settingsInputStyle, settingsSelectStyle, textFieldHandlers } from "./SectionField";
import {
  DEFAULT_TYPESET_SETTINGS_DRAFT,
  FONT_SIZE_OFFSET_MAX,
  FONT_SIZE_OFFSET_MIN,
  LINE_SPACING_MAX,
  LINE_SPACING_MIN,
  MANUAL_FONT_SIZE_MAX,
  MANUAL_FONT_SIZE_MIN,
  STROKE_WIDTH_MAX,
  STROKE_WIDTH_MIN,
  TEXT_ALIGN_LABELS,
  TEXT_ALIGN_VALUES,
  TEXT_DIRECTION_LABELS,
  TEXT_DIRECTION_VALUES,
  TYPESET_SECTION,
  describeTypesetSettings,
  normalizeTypesetSettings,
  typesetSettingsValues,
  validateTypesetSettingsDraft,
  type TextAlign,
  type TextDirection,
  type TypesetSettingsDraft,
} from "./sections";
import { useSettingsSection } from "./useSettingsSection";
import { tokens } from "../theme/tokens";

function ColorControl({
  id,
  testId,
  value,
  disabled,
  onChange,
}: {
  id: string;
  testId: string;
  value: string;
  disabled: boolean;
  onChange: (next: string) => void;
}) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm }}>
      <input
        id={id}
        data-testid={testId}
        type="color"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        onInput={(event) => onChange((event.target as HTMLInputElement).value)}
        style={{
          width: 48,
          height: 28,
          padding: 0,
          border: `1px solid ${tokens.color.border.default}`,
          borderRadius: tokens.radius.button,
          background: tokens.color.surface.card,
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      />
      {/* Text echo: the color input only yields #rrggbb, so the exact value
       * that will be saved is always visible next to the swatch. */}
      <code
        data-testid={`${testId}-value`}
        style={{
          fontFamily: tokens.typography.monospace,
          fontSize: tokens.typography.size.monospace,
          color: tokens.color.text.primary,
        }}
      >
        {value}
      </code>
    </div>
  );
}

function ToggleControl({
  id,
  testId,
  checked,
  disabled,
  onChange,
}: {
  id: string;
  testId: string;
  checked: boolean;
  disabled: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm }}>
      <input
        id={id}
        data-testid={testId}
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
        style={{ width: 16, height: 16, cursor: disabled ? "not-allowed" : "pointer" }}
      />
      <span
        data-testid={`${testId}-state`}
        style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}
      >
        {checked ? "已开启" : "已关闭"}
      </span>
    </div>
  );
}

/**
 * SETTINGS-OPEN-A-1 §3.4 — typeset default text style (section `typeset`).
 * Eleven editable keys; font_family is intentionally NOT rendered in this
 * batch (design §3.4 / task scope). Colors are #RRGGBB with a text echo,
 * every numeric key carries its frozen range.
 */
export function TypesetSettingsPanel({ client }: { client: SettingsClient }) {
  const { phase, unset, effective, draft, setDraft, saving, loadError, saveError, save, reload } =
    useSettingsSection<TypesetSettingsDraft>({
      client,
      section: TYPESET_SECTION,
      defaults: DEFAULT_TYPESET_SETTINGS_DRAFT,
      normalize: normalizeTypesetSettings,
    });

  const errors = validateTypesetSettingsDraft(draft);
  const hasErrors = Object.keys(errors).length > 0;
  const dirty = useMemo(
    () =>
      JSON.stringify(draft) !== JSON.stringify(effective ?? DEFAULT_TYPESET_SETTINGS_DRAFT),
    [draft, effective],
  );
  const ready = phase === "ready";

  return (
    <SectionPanelFrame
      testId="typeset-settings-panel"
      title="排版样式"
      description="typeset.* — 渲染默认文字样式（本批不开放字体选择 font_family，字体仍按 FontCatalog 默认）。Region 已持久化的样式仍覆盖此处默认值。"
      phase={phase}
      loadError={loadError}
      onRetry={() => void reload()}
      unset={unset}
      unsetText={`该节未设置（Core 返回 JSON null）——当前按 Core 默认文字样式运行：文字 ${DEFAULT_TYPESET_SETTINGS_DRAFT.text_color}，描边 ${DEFAULT_TYPESET_SETTINGS_DRAFT.stroke_color} / ${DEFAULT_TYPESET_SETTINGS_DRAFT.stroke_width}，行距 ${DEFAULT_TYPESET_SETTINGS_DRAFT.line_spacing}，自动字号。`}
      saving={saving}
      saveError={saveError}
      saveDisabled={!ready || !dirty || hasErrors}
      statusText={hasErrors ? "存在校验错误，无法保存" : dirty ? "有未保存的改动" : "无改动"}
      onSave={() => void save(typesetSettingsValues(draft))}
      effectiveText={describeTypesetSettings(effective)}
    >
      <SettingsField id="typeset-text-color" label="文字颜色 (text_color)" hint="默认 #000000。">
        <ColorControl
          id="typeset-text-color"
          testId="typeset-text-color"
          value={draft.text_color}
          disabled={saving}
          onChange={(next) => setDraft((prev) => ({ ...prev, text_color: next }))}
        />
      </SettingsField>

      <SettingsField id="typeset-stroke-enabled" label="启用描边 (stroke_enabled)" hint="默认开启；关闭后 stroke_width 不生效。">
        <ToggleControl
          id="typeset-stroke-enabled"
          testId="typeset-stroke-enabled"
          checked={draft.stroke_enabled}
          disabled={saving}
          onChange={(next) => setDraft((prev) => ({ ...prev, stroke_enabled: next }))}
        />
      </SettingsField>

      <SettingsField id="typeset-stroke-color" label="描边颜色 (stroke_color)" hint="默认 #FFFFFF。">
        <ColorControl
          id="typeset-stroke-color"
          testId="typeset-stroke-color"
          value={draft.stroke_color}
          disabled={saving}
          onChange={(next) => setDraft((prev) => ({ ...prev, stroke_color: next }))}
        />
      </SettingsField>

      <SettingsField
        id="typeset-stroke-width"
        label="描边宽度 (stroke_width)"
        hint={`${STROKE_WIDTH_MIN}–${STROKE_WIDTH_MAX}，默认 3.0。`}
        error={errors.stroke_width}
      >
        <input
          id="typeset-stroke-width"
          data-testid="typeset-stroke-width"
          type="number"
          min={STROKE_WIDTH_MIN}
          max={STROKE_WIDTH_MAX}
          step={0.5}
          value={draft.stroke_width}
          disabled={saving}
          aria-invalid={errors.stroke_width !== undefined}
          {...textFieldHandlers(setDraft, "stroke_width")}
          style={settingsInputStyle}
        />
      </SettingsField>

      <SettingsField
        id="typeset-line-spacing"
        label="行距 (line_spacing)"
        hint={`${LINE_SPACING_MIN}.0–${LINE_SPACING_MAX}.0，默认 1.0。`}
        error={errors.line_spacing}
      >
        <input
          id="typeset-line-spacing"
          data-testid="typeset-line-spacing"
          type="number"
          min={LINE_SPACING_MIN}
          max={LINE_SPACING_MAX}
          step={0.1}
          value={draft.line_spacing}
          disabled={saving}
          aria-invalid={errors.line_spacing !== undefined}
          {...textFieldHandlers(setDraft, "line_spacing")}
          style={settingsInputStyle}
        />
      </SettingsField>

      <SettingsField id="typeset-text-align" label="文字对齐 (text_align)" hint="默认左对齐；渲染器仅实现居中特判，值域为 left / center。">
        <select
          id="typeset-text-align"
          data-testid="typeset-text-align"
          value={draft.text_align}
          disabled={saving}
          onChange={(event) => {
            const next = event.target.value;
            if ((TEXT_ALIGN_VALUES as readonly string[]).includes(next)) {
              setDraft((prev) => ({ ...prev, text_align: next as TextAlign }));
            }
          }}
          style={settingsSelectStyle}
        >
          {TEXT_ALIGN_VALUES.map((value) => (
            <option key={value} value={value}>
              {TEXT_ALIGN_LABELS[value]}
            </option>
          ))}
        </select>
      </SettingsField>

      <SettingsField id="typeset-text-direction" label="文字方向 (text_direction)" hint="默认 auto。">
        <select
          id="typeset-text-direction"
          data-testid="typeset-text-direction"
          value={draft.text_direction}
          disabled={saving}
          onChange={(event) => {
            const next = event.target.value;
            if ((TEXT_DIRECTION_VALUES as readonly string[]).includes(next)) {
              setDraft((prev) => ({ ...prev, text_direction: next as TextDirection }));
            }
          }}
          style={settingsSelectStyle}
        >
          {TEXT_DIRECTION_VALUES.map((value) => (
            <option key={value} value={value}>
              {TEXT_DIRECTION_LABELS[value]}
            </option>
          ))}
        </select>
      </SettingsField>

      <SettingsField
        id="typeset-auto-font-size"
        label="自动字号 (auto_font_size)"
        hint="默认开启；关闭后必须填写 manual_font_size（否则无法保存）。"
      >
        <ToggleControl
          id="typeset-auto-font-size"
          testId="typeset-auto-font-size"
          checked={draft.auto_font_size}
          disabled={saving}
          onChange={(next) => setDraft((prev) => ({ ...prev, auto_font_size: next }))}
        />
      </SettingsField>

      <SettingsField
        id="typeset-font-size-offset"
        label="字号偏移 (font_size_offset)"
        hint={`整数 ${FONT_SIZE_OFFSET_MIN} 到 +${FONT_SIZE_OFFSET_MAX}，默认 0。`}
        error={errors.font_size_offset}
      >
        <input
          id="typeset-font-size-offset"
          data-testid="typeset-font-size-offset"
          type="number"
          inputMode="numeric"
          min={FONT_SIZE_OFFSET_MIN}
          max={FONT_SIZE_OFFSET_MAX}
          step={1}
          value={draft.font_size_offset}
          disabled={saving}
          aria-invalid={errors.font_size_offset !== undefined}
          {...textFieldHandlers(setDraft, "font_size_offset")}
          style={settingsInputStyle}
        />
      </SettingsField>

      <SettingsField
        id="typeset-manual-font-size"
        label="手动字号 (manual_font_size)"
        hint={`自动字号开启时可留空（未设置）；关闭自动字号时必填。范围 ${MANUAL_FONT_SIZE_MIN}–${MANUAL_FONT_SIZE_MAX}。`}
        error={errors.manual_font_size}
      >
        <input
          id="typeset-manual-font-size"
          data-testid="typeset-manual-font-size"
          type="number"
          min={MANUAL_FONT_SIZE_MIN}
          max={MANUAL_FONT_SIZE_MAX}
          step={1}
          placeholder="留空 = 未设置"
          value={draft.manual_font_size}
          disabled={saving}
          aria-invalid={errors.manual_font_size !== undefined}
          {...textFieldHandlers(setDraft, "manual_font_size")}
          style={settingsInputStyle}
        />
      </SettingsField>
    </SectionPanelFrame>
  );
}
