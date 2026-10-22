/**
 * Section schemas — the single front-end source of truth for every settings
 * section the UI may read/write, frozen by
 * doc/design/SETTINGS_SECTION_SCHEMAS.md:
 *
 *   ocr        — §3.1 script / direction (batch A)
 *   translate  — §3.2 context_pages / context_token_budget (batch A)
 *   inpaint    — §3.3 preferred_quality / background_complexity /
 *                       dilate_radius / erode_radius (batch A)
 *   typeset    — §3.4 default text style (font_family stays closed, batch A)
 *   model_gpu  — §4.1 device_preference / allow_cpu_fallback (batch B-1)
 *   tasks      — §4.2 retry_max_attempts / retry_backoff_seconds (batch B-1)
 *
 * Every default below is the documented Core default (design table, or the
 * Python constant it names) — the UI never invents values. A section read as
 * JSON null renders the explicit "未设置" affordance; a missing key falls back
 * to its default for display only and is never written until the user saves a
 * changed draft.
 *
 * Number inputs are held as strings in the draft (so an empty / partially
 * typed field stays representable); the `*Values` builders turn the validated
 * draft into the exact JSON values sent to `settings_update_section`.
 */

/* --------------------------------------------------------------------------
 * Shared helpers
 * ------------------------------------------------------------------------ */

function asRecord(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function pickOne<T extends string>(value: unknown, allowed: readonly T[], fallback: T): T {
  return typeof value === "string" && (allowed as readonly string[]).includes(value)
    ? (value as T)
    : fallback;
}

function pickBoolean(value: unknown, fallback: boolean): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function pickInt(value: unknown, fallback: number): number {
  const numeric =
    typeof value === "number"
      ? value
      : typeof value === "string" && value.trim() !== ""
        ? Number(value)
        : Number.NaN;
  return Number.isFinite(numeric) ? Math.trunc(numeric) : fallback;
}

function pickNumber(value: unknown, fallback: number): number {
  const numeric =
    typeof value === "number"
      ? value
      : typeof value === "string" && value.trim() !== ""
        ? Number(value)
        : Number.NaN;
  return Number.isFinite(numeric) ? numeric : fallback;
}

function pickOptionalNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const numeric = Number(value);
    if (Number.isFinite(numeric)) return numeric;
  }
  return null;
}

/** `#RRGGBB` only (the frozen value domain of every typeset color key). */
export function isHexColor(value: string): boolean {
  return /^#[0-9a-fA-F]{6}$/.test(value);
}

/** Parse an integer draft string; null when the text is not an integer. */
export function parseIntDraft(value: string): number | null {
  const trimmed = value.trim();
  if (!/^-?\d+$/.test(trimmed)) return null;
  const numeric = Number(trimmed);
  return Number.isSafeInteger(numeric) ? numeric : null;
}

/** Parse a decimal draft string; null when the text is not a finite number. */
export function parseNumberDraft(value: string): number | null {
  const trimmed = value.trim();
  if (trimmed === "") return null;
  const numeric = Number(trimmed);
  return Number.isFinite(numeric) ? numeric : null;
}

/* --------------------------------------------------------------------------
 * §3.1 OCR (section `ocr`)
 * ------------------------------------------------------------------------ */

export const OCR_SECTION = "ocr";

export type OcrScript = "japanese" | "korean" | "chinese" | "latin";
export type OcrDirection = "horizontal" | "vertical";

export const OCR_SCRIPT_VALUES: readonly OcrScript[] = [
  "japanese",
  "korean",
  "chinese",
  "latin",
] as const;

export const OCR_DIRECTION_VALUES: readonly OcrDirection[] = ["horizontal", "vertical"] as const;

export const OCR_SCRIPT_LABELS: Readonly<Record<OcrScript, string>> = {
  japanese: "日语 (japanese)",
  korean: "韩语 (korean)",
  chinese: "中文 (chinese)",
  latin: "拉丁 (latin)",
};

export const OCR_DIRECTION_LABELS: Readonly<Record<OcrDirection, string>> = {
  horizontal: "横排 (horizontal)",
  vertical: "竖排 (vertical)",
};

export interface OcrSettings {
  script: OcrScript;
  direction: OcrDirection;
}

/** Core defaults (`SCRIPT_JAPANESE` / `TEXT_DIRECTION_HORIZONTAL`). */
export const DEFAULT_OCR_SETTINGS: OcrSettings = {
  script: "japanese",
  direction: "horizontal",
};

export function normalizeOcrSettings(value: unknown): OcrSettings {
  const raw = asRecord(value);
  return {
    script: pickOne(raw.script, OCR_SCRIPT_VALUES, DEFAULT_OCR_SETTINGS.script),
    direction: pickOne(raw.direction, OCR_DIRECTION_VALUES, DEFAULT_OCR_SETTINGS.direction),
  };
}

export function describeOcrSettings(settings: OcrSettings | null): string {
  if (settings === null) return "未设置（按 Core 默认值运行）";
  return `${OCR_SCRIPT_LABELS[settings.script]} · ${OCR_DIRECTION_LABELS[settings.direction]}`;
}

/* --------------------------------------------------------------------------
 * §3.2 Translation parameters / context (section `translate`)
 * ------------------------------------------------------------------------ */

export const TRANSLATE_SECTION = "translate";

/** Core defaults (`DEFAULT_CONTEXT_PAGES` / `DEFAULT_CONTEXT_TOKEN_BUDGET`). */
export const DEFAULT_CONTEXT_PAGES = 1;
export const DEFAULT_CONTEXT_TOKEN_BUDGET = 2000;

export const CONTEXT_PAGES_MIN = 1;
export const CONTEXT_PAGES_MAX = 5;
export const CONTEXT_TOKEN_BUDGET_MIN = 200;
export const CONTEXT_TOKEN_BUDGET_MAX = 8000;

/** Number-input draft (strings so an empty field stays representable). */
export interface TranslationParamsDraft {
  context_pages: string;
  context_token_budget: string;
}

export const DEFAULT_TRANSLATION_PARAMS_DRAFT: TranslationParamsDraft = {
  context_pages: String(DEFAULT_CONTEXT_PAGES),
  context_token_budget: String(DEFAULT_CONTEXT_TOKEN_BUDGET),
};

export function normalizeTranslationParams(value: unknown): TranslationParamsDraft {
  const raw = asRecord(value);
  return {
    context_pages: String(pickInt(raw.context_pages, DEFAULT_CONTEXT_PAGES)),
    context_token_budget: String(
      pickInt(raw.context_token_budget, DEFAULT_CONTEXT_TOKEN_BUDGET),
    ),
  };
}

/** Front-end range check (the Core re-validates and stays the authority). */
export function validateTranslationParamsDraft(
  draft: TranslationParamsDraft,
): Record<string, string> {
  const errors: Record<string, string> = {};
  const pages = parseIntDraft(draft.context_pages);
  if (pages === null || pages < CONTEXT_PAGES_MIN || pages > CONTEXT_PAGES_MAX) {
    errors.context_pages = `context_pages 必须是 ${CONTEXT_PAGES_MIN}–${CONTEXT_PAGES_MAX} 的整数`;
  }
  const budget = parseIntDraft(draft.context_token_budget);
  if (budget === null || budget < CONTEXT_TOKEN_BUDGET_MIN || budget > CONTEXT_TOKEN_BUDGET_MAX) {
    errors.context_token_budget = `context_token_budget 必须是 ${CONTEXT_TOKEN_BUDGET_MIN}–${CONTEXT_TOKEN_BUDGET_MAX} 的整数`;
  }
  return errors;
}

export function translationParamsValues(
  draft: TranslationParamsDraft,
): Record<string, unknown> {
  return {
    context_pages: parseIntDraft(draft.context_pages),
    context_token_budget: parseIntDraft(draft.context_token_budget),
  };
}

export function describeTranslationParams(draft: TranslationParamsDraft | null): string {
  if (draft === null) return "未设置（按 Core 默认值运行）";
  return `上下文页数 ${draft.context_pages} · Token 预算 ${draft.context_token_budget}`;
}

/* --------------------------------------------------------------------------
 * §3.3 Inpaint (section `inpaint`)
 * ------------------------------------------------------------------------ */

export const INPAINT_SECTION = "inpaint";

export type InpaintQuality = "fast" | "balanced" | "quality";
export type BackgroundComplexity = "low" | "medium" | "high";

export const INPAINT_QUALITY_VALUES: readonly InpaintQuality[] = [
  "fast",
  "balanced",
  "quality",
] as const;

export const BACKGROUND_COMPLEXITY_VALUES: readonly BackgroundComplexity[] = [
  "low",
  "medium",
  "high",
] as const;

export const INPAINT_QUALITY_LABELS: Readonly<Record<InpaintQuality, string>> = {
  fast: "快速 (fast)",
  balanced: "均衡 (balanced)",
  quality: "高质量 (quality)",
};

export const BACKGROUND_COMPLEXITY_LABELS: Readonly<Record<BackgroundComplexity, string>> = {
  low: "低 (low)",
  medium: "中 (medium)",
  high: "高 (high)",
};

export const DILATE_RADIUS_MIN = 0;
export const DILATE_RADIUS_MAX = 10;
export const ERODE_RADIUS_MIN = 0;
export const ERODE_RADIUS_MAX = 10;

export interface InpaintSettingsDraft {
  preferred_quality: InpaintQuality;
  background_complexity: BackgroundComplexity;
  dilate_radius: string;
  erode_radius: string;
}

/** Core defaults (`handlers.py:524/525/596/597`). */
export const DEFAULT_INPAINT_SETTINGS_DRAFT: InpaintSettingsDraft = {
  preferred_quality: "balanced",
  background_complexity: "low",
  dilate_radius: "2",
  erode_radius: "0",
};

export function normalizeInpaintSettings(value: unknown): InpaintSettingsDraft {
  const raw = asRecord(value);
  return {
    preferred_quality: pickOne(
      raw.preferred_quality,
      INPAINT_QUALITY_VALUES,
      DEFAULT_INPAINT_SETTINGS_DRAFT.preferred_quality,
    ),
    background_complexity: pickOne(
      raw.background_complexity,
      BACKGROUND_COMPLEXITY_VALUES,
      DEFAULT_INPAINT_SETTINGS_DRAFT.background_complexity,
    ),
    dilate_radius: String(pickInt(raw.dilate_radius, 2)),
    erode_radius: String(pickInt(raw.erode_radius, 0)),
  };
}

export function validateInpaintSettingsDraft(
  draft: InpaintSettingsDraft,
): Record<string, string> {
  const errors: Record<string, string> = {};
  const dilate = parseIntDraft(draft.dilate_radius);
  if (dilate === null || dilate < DILATE_RADIUS_MIN || dilate > DILATE_RADIUS_MAX) {
    errors.dilate_radius = `dilate_radius 必须是 ${DILATE_RADIUS_MIN}–${DILATE_RADIUS_MAX} 的整数`;
  }
  const erode = parseIntDraft(draft.erode_radius);
  if (erode === null || erode < ERODE_RADIUS_MIN || erode > ERODE_RADIUS_MAX) {
    errors.erode_radius = `erode_radius 必须是 ${ERODE_RADIUS_MIN}–${ERODE_RADIUS_MAX} 的整数`;
  }
  return errors;
}

export function inpaintSettingsValues(
  draft: InpaintSettingsDraft,
): Record<string, unknown> {
  return {
    preferred_quality: draft.preferred_quality,
    background_complexity: draft.background_complexity,
    dilate_radius: parseIntDraft(draft.dilate_radius),
    erode_radius: parseIntDraft(draft.erode_radius),
  };
}

export function describeInpaintSettings(draft: InpaintSettingsDraft | null): string {
  if (draft === null) return "未设置（按 Core 默认值运行）";
  return `${INPAINT_QUALITY_LABELS[draft.preferred_quality]} · 背景 ${BACKGROUND_COMPLEXITY_LABELS[draft.background_complexity]} · dilate ${draft.dilate_radius} / erode ${draft.erode_radius}`;
}

/* --------------------------------------------------------------------------
 * §3.4 Typeset default text style (section `typeset`)
 * ------------------------------------------------------------------------ */

export const TYPESET_SECTION = "typeset";

// M2（review r1）：值域收窄为 left | center —— 两个 compositor 只实现 center
// 特判，`right` 会被渲染成左对齐，因此不再作为可选项展示/提交。
export type TextAlign = "left" | "center";
export type TextDirection = "auto" | "horizontal" | "vertical";

export const TEXT_ALIGN_VALUES: readonly TextAlign[] = ["left", "center"] as const;
export const TEXT_DIRECTION_VALUES: readonly TextDirection[] = [
  "auto",
  "horizontal",
  "vertical",
] as const;

export const TEXT_ALIGN_LABELS: Readonly<Record<TextAlign, string>> = {
  left: "左对齐 (left)",
  center: "居中 (center)",
};

export const TEXT_DIRECTION_LABELS: Readonly<Record<TextDirection, string>> = {
  auto: "自动 (auto)",
  horizontal: "横排 (horizontal)",
  vertical: "竖排 (vertical)",
};

export const STROKE_WIDTH_MIN = 0;
export const STROKE_WIDTH_MAX = 20;
export const LINE_SPACING_MIN = 1;
export const LINE_SPACING_MAX = 3;
export const FONT_SIZE_OFFSET_MIN = -5;
export const FONT_SIZE_OFFSET_MAX = 5;
export const MANUAL_FONT_SIZE_MIN = 1;
export const MANUAL_FONT_SIZE_MAX = 500;

export interface TypesetSettingsDraft {
  text_color: string;
  stroke_enabled: boolean;
  stroke_color: string;
  stroke_width: string;
  line_spacing: string;
  text_align: TextAlign;
  text_direction: TextDirection;
  auto_font_size: boolean;
  font_size_offset: string;
  /** Empty string = null (the key's Core default). */
  manual_font_size: string;
}

/**
 * Core defaults from `application/rendering/style.py` (D03 §11.6):
 * DEFAULT_TEXT_COLOR #000000, DEFAULT_STROKE_COLOR #FFFFFF,
 * DEFAULT_STROKE_WIDTH 3.0, DEFAULT_LINE_SPACING 1.0, auto font size on,
 * offset 0, manual size null.
 *
 * B2（review r1）：`fill_color` 已从本节移除 —— RenderOp/compositor 全链路没有
 * 该字段的消费者，保留控件会违反设计 §2.4「不伪造」。设计表与 Core 白名单需
 * 由 Lead/Core writer 同步（前端已不再读写该键）。
 *
 * text_align: 冻结值域 left | center（M2 返修）。Python 默认常量是 "start"，
 * 旧持久化值 "start" / "right" 读取时折叠为 "left" 展示，且永远不会被写回。
 */
export const DEFAULT_TYPESET_SETTINGS_DRAFT: TypesetSettingsDraft = {
  text_color: "#000000",
  stroke_enabled: true,
  stroke_color: "#ffffff",
  stroke_width: "3",
  line_spacing: "1",
  text_align: "left",
  text_direction: "auto",
  auto_font_size: true,
  font_size_offset: "0",
  manual_font_size: "",
};

function normalizeColor(value: unknown, fallback: string): string {
  return typeof value === "string" && isHexColor(value.trim())
    ? value.trim().toLowerCase()
    : fallback;
}

export function normalizeTypesetSettings(value: unknown): TypesetSettingsDraft {
  const raw = asRecord(value);
  const manualFontSize = pickOptionalNumber(raw.manual_font_size);
  return {
    text_color: normalizeColor(raw.text_color, DEFAULT_TYPESET_SETTINGS_DRAFT.text_color),
    stroke_enabled: pickBoolean(raw.stroke_enabled, DEFAULT_TYPESET_SETTINGS_DRAFT.stroke_enabled),
    stroke_color: normalizeColor(
      raw.stroke_color,
      DEFAULT_TYPESET_SETTINGS_DRAFT.stroke_color,
    ),
    stroke_width: String(pickNumber(raw.stroke_width, 3)),
    line_spacing: String(pickNumber(raw.line_spacing, 1)),
    text_align:
      raw.text_align === "start" || raw.text_align === "right"
        ? "left"
        : pickOne(raw.text_align, TEXT_ALIGN_VALUES, DEFAULT_TYPESET_SETTINGS_DRAFT.text_align),
    text_direction: pickOne(
      raw.text_direction,
      TEXT_DIRECTION_VALUES,
      DEFAULT_TYPESET_SETTINGS_DRAFT.text_direction,
    ),
    auto_font_size: pickBoolean(
      raw.auto_font_size,
      DEFAULT_TYPESET_SETTINGS_DRAFT.auto_font_size,
    ),
    font_size_offset: String(pickInt(raw.font_size_offset, 0)),
    manual_font_size: manualFontSize === null ? "" : String(manualFontSize),
  };
}

export function validateTypesetSettingsDraft(
  draft: TypesetSettingsDraft,
): Record<string, string> {
  const errors: Record<string, string> = {};

  if (!isHexColor(draft.text_color)) errors.text_color = "text_color 必须是 #RRGGBB";
  if (!isHexColor(draft.stroke_color)) errors.stroke_color = "stroke_color 必须是 #RRGGBB";

  const strokeWidth = parseNumberDraft(draft.stroke_width);
  if (strokeWidth === null || strokeWidth < STROKE_WIDTH_MIN || strokeWidth > STROKE_WIDTH_MAX) {
    errors.stroke_width = `stroke_width 必须在 ${STROKE_WIDTH_MIN}–${STROKE_WIDTH_MAX} 之间`;
  }

  const lineSpacing = parseNumberDraft(draft.line_spacing);
  if (lineSpacing === null || lineSpacing < LINE_SPACING_MIN || lineSpacing > LINE_SPACING_MAX) {
    errors.line_spacing = `line_spacing 必须在 ${LINE_SPACING_MIN}.0–${LINE_SPACING_MAX}.0 之间`;
  }

  const offset = parseIntDraft(draft.font_size_offset);
  if (offset === null || offset < FONT_SIZE_OFFSET_MIN || offset > FONT_SIZE_OFFSET_MAX) {
    errors.font_size_offset = `font_size_offset 必须是 ${FONT_SIZE_OFFSET_MIN} 到 +${FONT_SIZE_OFFSET_MAX} 的整数`;
  }

  // M1（review r1）：跨字段约束 —— 关闭自动字号后必须给出手动字号，否则
  // RenderService 会抛 StyleResolutionError / rerender 映射为
  // MISSING_REQUIRED_INPUT，整页渲染失败。auto=true 时手动字号可留空。
  const manualRaw = draft.manual_font_size.trim();
  if (!draft.auto_font_size && manualRaw === "") {
    errors.manual_font_size =
      "关闭自动字号 (auto_font_size=false) 时必须填写 manual_font_size";
  } else if (manualRaw !== "") {
    const manual = parseNumberDraft(draft.manual_font_size);
    if (manual === null || manual < MANUAL_FONT_SIZE_MIN || manual > MANUAL_FONT_SIZE_MAX) {
      errors.manual_font_size = `manual_font_size 必须在 ${MANUAL_FONT_SIZE_MIN}–${MANUAL_FONT_SIZE_MAX} 之间`;
    }
  }

  if (!TEXT_ALIGN_VALUES.includes(draft.text_align)) {
    errors.text_align = "text_align 必须是 left / center";
  }
  if (!TEXT_DIRECTION_VALUES.includes(draft.text_direction)) {
    errors.text_direction = "text_direction 必须是 auto / horizontal / vertical";
  }

  return errors;
}

export function typesetSettingsValues(draft: TypesetSettingsDraft): Record<string, unknown> {
  return {
    text_color: draft.text_color,
    stroke_enabled: draft.stroke_enabled,
    stroke_color: draft.stroke_color,
    stroke_width: parseNumberDraft(draft.stroke_width),
    line_spacing: parseNumberDraft(draft.line_spacing),
    text_align: draft.text_align,
    text_direction: draft.text_direction,
    auto_font_size: draft.auto_font_size,
    font_size_offset: parseIntDraft(draft.font_size_offset),
    manual_font_size:
      draft.manual_font_size.trim() === "" ? null : parseNumberDraft(draft.manual_font_size),
  };
}

export function describeTypesetSettings(draft: TypesetSettingsDraft | null): string {
  if (draft === null) return "未设置（按 Core 默认样式运行）";
  const manual =
    draft.manual_font_size.trim() === "" ? "手动字号缺失" : `手动 ${draft.manual_font_size}px`;
  return [
    `文字 ${draft.text_color}`,
    draft.stroke_enabled ? `描边 ${draft.stroke_color} / ${draft.stroke_width}` : "描边关闭",
    `行距 ${draft.line_spacing}`,
    TEXT_ALIGN_LABELS[draft.text_align],
    TEXT_DIRECTION_LABELS[draft.text_direction],
    draft.auto_font_size ? "字号自动" : manual,
    `偏移 ${draft.font_size_offset}`,
  ].join(" · ");
}

/* --------------------------------------------------------------------------
 * §4.1 Model / GPU (section `model_gpu`, SETTINGS-OPEN-B-1)
 * ------------------------------------------------------------------------ */

export const MODEL_GPU_SECTION = "model_gpu";

/**
 * §4.1 — `device_preference` is a VALIDATION / FALLBACK preference, not a
 * device selector (review-b1 M1 adjudication):
 *
 *   auto — historical behaviour (no explicit device gate);
 *   cpu  — skip the GPU availability check and run;
 *   gpu  — validate GPU availability first; when it is unavailable the
 *          `allow_cpu_fallback` + provider `supports_cpu_fallback` rule
 *          decides between a CPU fallback and a typed DeviceUnavailable.
 *
 * The provider APIs expose no device parameter, so a preference never forces
 * the provider's internal device implementation. `gpu_concurrency` is
 * intentionally absent — the single-slot gate is an existing invariant, not
 * a user setting (design §4.1 "未开放").
 */
export type DevicePreference = "auto" | "cpu" | "gpu";

export const DEVICE_PREFERENCE_VALUES: readonly DevicePreference[] = [
  "auto",
  "cpu",
  "gpu",
] as const;

/**
 * The labels carry the adjudicated semantics: the value only gates the GPU
 * availability check and the CPU-fallback decision — it is not a hard device
 * switch (the provider API has no device parameter).
 */
export const DEVICE_PREFERENCE_LABELS: Readonly<Record<DevicePreference, string>> = {
  auto: "自动 (auto)",
  cpu: "仅 CPU (cpu，跳过 GPU 校验)",
  gpu: "优先 GPU (gpu，GPU 不可用时按回退策略)",
};

/**
 * Review-b1 M1 adjudication — the one sentence rendered next to the control
 * so the value can never be read as a hard device switch.
 */
export const DEVICE_PREFERENCE_SEMANTICS_NOTE =
  "设备偏好用于 GPU 可用性校验与 CPU 回退决策，不强制 Provider 内部设备实现。";

export interface ModelGpuSettingsDraft {
  device_preference: DevicePreference;
  /**
   * User half of the D06 §82 rule: falling back to CPU additionally requires
   * the Provider descriptor's `supports_cpu_fallback` (the two are ANDed by
   * the Core, this flag alone cannot force a fallback).
   */
  allow_cpu_fallback: boolean;
}

/** Core defaults (design §4.1): auto preference, CPU fallback allowed. */
export const DEFAULT_MODEL_GPU_SETTINGS_DRAFT: ModelGpuSettingsDraft = {
  device_preference: "auto",
  allow_cpu_fallback: true,
};

export function normalizeModelGpuSettings(value: unknown): ModelGpuSettingsDraft {
  const raw = asRecord(value);
  return {
    device_preference: pickOne(
      raw.device_preference,
      DEVICE_PREFERENCE_VALUES,
      DEFAULT_MODEL_GPU_SETTINGS_DRAFT.device_preference,
    ),
    allow_cpu_fallback: pickBoolean(
      raw.allow_cpu_fallback,
      DEFAULT_MODEL_GPU_SETTINGS_DRAFT.allow_cpu_fallback,
    ),
  };
}

/**
 * Both keys are closed enums / booleans, so the controls cannot produce an
 * invalid draft; the check still runs before every write (the Core re-validates
 * and remains the authority) and guards against a future widened control.
 */
export function validateModelGpuSettingsDraft(
  draft: ModelGpuSettingsDraft,
): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!DEVICE_PREFERENCE_VALUES.includes(draft.device_preference)) {
    errors.device_preference = "device_preference 必须是 auto / cpu / gpu";
  }
  if (typeof draft.allow_cpu_fallback !== "boolean") {
    errors.allow_cpu_fallback = "allow_cpu_fallback 必须是布尔值";
  }
  return errors;
}

export function modelGpuSettingsValues(
  draft: ModelGpuSettingsDraft,
): Record<string, unknown> {
  return {
    device_preference: draft.device_preference,
    allow_cpu_fallback: draft.allow_cpu_fallback,
  };
}

export function describeModelGpuSettings(draft: ModelGpuSettingsDraft | null): string {
  if (draft === null) return "未设置（按 Core 默认值运行）";
  return `设备偏好 ${DEVICE_PREFERENCE_LABELS[draft.device_preference]} · CPU 回退 ${
    draft.allow_cpu_fallback ? "允许" : "禁止"
  }`;
}

/* --------------------------------------------------------------------------
 * §4.2 Tasks / concurrency (section `tasks`, SETTINGS-OPEN-B-1)
 * ------------------------------------------------------------------------ */

export const TASKS_SECTION = "tasks";

/** Core defaults (design §4.2; `runtime.DEFAULT_RETRY_POLICY`). */
export const DEFAULT_RETRY_MAX_ATTEMPTS = 3;
export const DEFAULT_RETRY_BACKOFF_SECONDS = 1.0;

export const RETRY_MAX_ATTEMPTS_MIN = 1;
export const RETRY_MAX_ATTEMPTS_MAX = 3;
export const RETRY_BACKOFF_SECONDS_MIN = 0.1;
export const RETRY_BACKOFF_SECONDS_MAX = 30;

/**
 * The concurrency count itself is NOT part of this section: the scheduler's
 * `max_parallel_pages = 1` / `max_parallel_steps = 1` are forced invariants
 * (design §4.2), so the panel renders a read-only "任务串行执行" note and
 * never a fake control.
 */
export interface TasksSettingsDraft {
  retry_max_attempts: string;
  retry_backoff_seconds: string;
}

export const DEFAULT_TASKS_SETTINGS_DRAFT: TasksSettingsDraft = {
  retry_max_attempts: String(DEFAULT_RETRY_MAX_ATTEMPTS),
  // `1.0`, not `1`: the documented Core default is a float.
  retry_backoff_seconds: DEFAULT_RETRY_BACKOFF_SECONDS.toFixed(1),
};

export function normalizeTasksSettings(value: unknown): TasksSettingsDraft {
  const raw = asRecord(value);
  return {
    retry_max_attempts: String(pickInt(raw.retry_max_attempts, DEFAULT_RETRY_MAX_ATTEMPTS)),
    retry_backoff_seconds: String(
      pickNumber(raw.retry_backoff_seconds, DEFAULT_RETRY_BACKOFF_SECONDS),
    ),
  };
}

export function validateTasksSettingsDraft(draft: TasksSettingsDraft): Record<string, string> {
  const errors: Record<string, string> = {};
  const attempts = parseIntDraft(draft.retry_max_attempts);
  if (
    attempts === null ||
    attempts < RETRY_MAX_ATTEMPTS_MIN ||
    attempts > RETRY_MAX_ATTEMPTS_MAX
  ) {
    errors.retry_max_attempts = `retry_max_attempts 必须是 ${RETRY_MAX_ATTEMPTS_MIN}–${RETRY_MAX_ATTEMPTS_MAX} 的整数`;
  }
  const backoff = parseNumberDraft(draft.retry_backoff_seconds);
  if (
    backoff === null ||
    backoff < RETRY_BACKOFF_SECONDS_MIN ||
    backoff > RETRY_BACKOFF_SECONDS_MAX
  ) {
    errors.retry_backoff_seconds = `retry_backoff_seconds 必须在 ${RETRY_BACKOFF_SECONDS_MIN}–${RETRY_BACKOFF_SECONDS_MAX} 之间`;
  }
  return errors;
}

export function tasksSettingsValues(draft: TasksSettingsDraft): Record<string, unknown> {
  return {
    retry_max_attempts: parseIntDraft(draft.retry_max_attempts),
    retry_backoff_seconds: parseNumberDraft(draft.retry_backoff_seconds),
  };
}

export function describeTasksSettings(draft: TasksSettingsDraft | null): string {
  if (draft === null) return "未设置（沿用 Core 默认重试策略）";
  return `重试上限 ${draft.retry_max_attempts} 次 · 退避 ${draft.retry_backoff_seconds} 秒`;
}
