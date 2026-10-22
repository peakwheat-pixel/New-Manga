import { useMemo } from "react";
import type { SettingsClient } from "./client";
import { SectionPanelFrame } from "./SectionPanelFrame";
import { SettingsField, settingsInputStyle, textFieldHandlers } from "./SectionField";
import {
  CONTEXT_PAGES_MAX,
  CONTEXT_PAGES_MIN,
  CONTEXT_TOKEN_BUDGET_MAX,
  CONTEXT_TOKEN_BUDGET_MIN,
  DEFAULT_CONTEXT_PAGES,
  DEFAULT_CONTEXT_TOKEN_BUDGET,
  DEFAULT_TRANSLATION_PARAMS_DRAFT,
  TRANSLATE_SECTION,
  describeTranslationParams,
  normalizeTranslationParams,
  translationParamsValues,
  validateTranslationParamsDraft,
  type TranslationParamsDraft,
} from "./sections";
import { useSettingsSection } from "./useSettingsSection";

/**
 * SETTINGS-OPEN-A-1 §3.2 — translation parameters / context (section
 * `translate`): `context_pages` (int 1–5, default 1) and
 * `context_token_budget` (int 200–8000, default 2000). The ranges are checked
 * before the write (Core re-validates and remains the authority); glossary and
 * context.strategy override keys stay closed in this batch.
 */
export function TranslationParamsPanel({ client }: { client: SettingsClient }) {
  const { phase, unset, effective, draft, setDraft, saving, loadError, saveError, save, reload } =
    useSettingsSection<TranslationParamsDraft>({
      client,
      section: TRANSLATE_SECTION,
      defaults: DEFAULT_TRANSLATION_PARAMS_DRAFT,
      normalize: normalizeTranslationParams,
    });

  const errors = validateTranslationParamsDraft(draft);
  const hasErrors = Object.keys(errors).length > 0;
  const dirty = useMemo(
    () =>
      JSON.stringify(draft) !==
      JSON.stringify(effective ?? DEFAULT_TRANSLATION_PARAMS_DRAFT),
    [draft, effective],
  );
  const ready = phase === "ready";

  return (
    <SectionPanelFrame
      testId="translation-params-panel"
      title="翻译参数 / 上下文策略"
      description="translate.context_pages / translate.context_token_budget — 多页上下文窗口与 Token 预算。"
      phase={phase}
      loadError={loadError}
      onRetry={() => void reload()}
      unset={unset}
      unsetText={`该节未设置（Core 返回 JSON null）——当前按 Core 默认值运行：context_pages=${DEFAULT_CONTEXT_PAGES}，context_token_budget=${DEFAULT_CONTEXT_TOKEN_BUDGET}。`}
      saving={saving}
      saveError={saveError}
      saveDisabled={!ready || !dirty || hasErrors}
      statusText={hasErrors ? "存在校验错误，无法保存" : dirty ? "有未保存的改动" : "无改动"}
      onSave={() => void save(translationParamsValues(draft))}
      effectiveText={describeTranslationParams(effective)}
    >
      <SettingsField
        id="translate-context-pages"
        label="上下文页数 (context_pages)"
        hint={`整数 ${CONTEXT_PAGES_MIN}–${CONTEXT_PAGES_MAX}，默认 ${DEFAULT_CONTEXT_PAGES}；越大越能利用相邻页上下文，但请求更慢。`}
        error={errors.context_pages}
      >
        <input
          id="translate-context-pages"
          data-testid="translate-context-pages"
          type="number"
          inputMode="numeric"
          min={CONTEXT_PAGES_MIN}
          max={CONTEXT_PAGES_MAX}
          step={1}
          value={draft.context_pages}
          disabled={saving}
          aria-invalid={errors.context_pages !== undefined}
          {...textFieldHandlers(setDraft, "context_pages")}
          style={settingsInputStyle}
        />
      </SettingsField>

      <SettingsField
        id="translate-context-token-budget"
        label="上下文 Token 预算 (context_token_budget)"
        hint={`整数 ${CONTEXT_TOKEN_BUDGET_MIN}–${CONTEXT_TOKEN_BUDGET_MAX}，默认 ${DEFAULT_CONTEXT_TOKEN_BUDGET}。`}
        error={errors.context_token_budget}
      >
        <input
          id="translate-context-token-budget"
          data-testid="translate-context-token-budget"
          type="number"
          inputMode="numeric"
          min={CONTEXT_TOKEN_BUDGET_MIN}
          max={CONTEXT_TOKEN_BUDGET_MAX}
          step={100}
          value={draft.context_token_budget}
          disabled={saving}
          aria-invalid={errors.context_token_budget !== undefined}
          {...textFieldHandlers(setDraft, "context_token_budget")}
          style={settingsInputStyle}
        />
      </SettingsField>
    </SectionPanelFrame>
  );
}
