/**
 * P15-C1 §9 — the closed error projection for every WebView-facing settings
 * error. Only (category, phase, action, message_key) may reach the UI; the
 * underlying ErrorEnvelope details / exception text / raw responses are
 * dropped here and never rendered.
 */

export type SettingsErrorCategory =
  | "validation"
  | "not_found"
  | "conflict"
  | "unavailable"
  | "cancelled"
  | "internal";

export type SettingsErrorPhase =
  | "profile"
  | "binding"
  | "credential_input"
  | "credential_store"
  | "credential_binding"
  | "network_proxy"
  | "dns"
  | "tcp"
  | "tls"
  | "http"
  | "provider_auth"
  | "settings_resolution";

export type SettingsErrorAction =
  | "retry"
  | "edit_profile"
  | "configure_credential"
  | "select_profile"
  | "review_tls_setting"
  | "clear_binding"
  | "contact_support"
  | "none";

export type SafeSettingsMessageKey =
  | "SETTINGS_INVALID_INPUT"
  | "SETTINGS_ITEM_NOT_FOUND"
  | "SETTINGS_CONFLICT"
  | "SETTINGS_UNAVAILABLE"
  | "CREDENTIAL_INPUT_CANCELLED"
  | "CREDENTIAL_STORE_UNAVAILABLE"
  | "NETWORK_STAGE_FAILED"
  | "TLS_CONFIRMATION_REQUIRED";

/** Contract §9 SettingsSurfaceError — the only shape UI code may render. */
export interface SettingsSurfaceError {
  category: SettingsErrorCategory;
  phase: SettingsErrorPhase;
  action: SettingsErrorAction;
  message_key: SafeSettingsMessageKey;
}

/** Fixed localized (zh-CN) copy per message_key — the message text is chosen
 * by the key alone, never built from underlying error payloads. */
export const SETTINGS_MESSAGE_TEXT: Readonly<Record<SafeSettingsMessageKey, string>> = {
  SETTINGS_INVALID_INPUT: "提交的内容不符合该分区的键域或值域要求，请检查后重试。",
  SETTINGS_ITEM_NOT_FOUND: "指定的条目不存在，可能已被删除或 ID 有误。",
  SETTINGS_CONFLICT: "操作与当前状态冲突（例如条目仍被引用），请先解除引用后重试。",
  SETTINGS_UNAVAILABLE: "设置服务当前不可用，请检查后台服务状态后重试。",
  CREDENTIAL_INPUT_CANCELLED: "已取消凭据输入，未做任何更改。",
  CREDENTIAL_STORE_UNAVAILABLE: "凭据存储当前不可用，请稍后重试。",
  NETWORK_STAGE_FAILED: "连接测试在某个阶段失败，详见各阶段结果；不会静默回退直连。",
  TLS_CONFIRMATION_REQUIRED: "关闭 TLS 校验属于危险操作，必须先完成明确确认。",
};

/** Human labels for the closed action enum. */
export const SETTINGS_ACTION_LABELS: Readonly<Record<SettingsErrorAction, string>> = {
  retry: "重试",
  edit_profile: "编辑配置",
  configure_credential: "配置凭据",
  select_profile: "选择 Profile",
  review_tls_setting: "检查 TLS 设置",
  clear_binding: "解除绑定",
  contact_support: "联系支持",
  none: "",
};

/** Human labels for the closed category enum. */
export const SETTINGS_CATEGORY_LABELS: Readonly<Record<SettingsErrorCategory, string>> = {
  validation: "参数校验失败",
  not_found: "未找到",
  conflict: "状态冲突",
  unavailable: "服务不可用",
  cancelled: "已取消",
  internal: "内部错误",
};

/**
 * Project an unknown channel failure into the closed §9 shape. Only a stable
 * error `code` (M2-C1 §8 enum or the P15-C1 keys below) is inspected; any
 * other payload (message text, details, paths) is discarded — it must never
 * reach the DOM.
 */
export function projectSettingsError(
  raw: unknown,
  phase: SettingsErrorPhase,
): SettingsSurfaceError {
  let code = "";
  if (typeof raw === "string") {
    code = raw;
  } else if (raw && typeof raw === "object") {
    const obj = raw as { code?: unknown };
    if (typeof obj.code === "string") {
      code = obj.code;
    }
  }

  switch (code) {
    case "INVALID_REQUEST":
      return {
        category: "validation",
        phase,
        action: phase === "binding" ? "select_profile" : phase.startsWith("credential") ? "configure_credential" : phase === "network_proxy" || phase === "tls" ? "review_tls_setting" : "edit_profile",
        message_key: "SETTINGS_INVALID_INPUT",
      };
    case "NOT_FOUND":
      return { category: "not_found", phase, action: "select_profile", message_key: "SETTINGS_ITEM_NOT_FOUND" };
    case "CONFLICT":
      return { category: "conflict", phase, action: phase === "binding" ? "clear_binding" : "edit_profile", message_key: "SETTINGS_CONFLICT" };
    case "CORE_UNAVAILABLE":
      return { category: "unavailable", phase, action: "retry", message_key: "SETTINGS_UNAVAILABLE" };
    case "CREDENTIAL_STORE_UNAVAILABLE":
      return { category: "unavailable", phase, action: "retry", message_key: "CREDENTIAL_STORE_UNAVAILABLE" };
    case "CANCELLED":
    case "CREDENTIAL_INPUT_CANCELLED":
      return { category: "cancelled", phase, action: "none", message_key: "CREDENTIAL_INPUT_CANCELLED" };
    case "TLS_CONFIRMATION_REQUIRED":
      return { category: "validation", phase, action: "review_tls_setting", message_key: "TLS_CONFIRMATION_REQUIRED" };
    case "NETWORK_STAGE_FAILED":
      return { category: "unavailable", phase, action: "retry", message_key: "NETWORK_STAGE_FAILED" };
    default:
      // Unknown codes (including transport garbage) collapse to a stable
      // internal projection — the raw value is NOT surfaced.
      return { category: "internal", phase, action: "retry", message_key: "SETTINGS_UNAVAILABLE" };
  }
}

/** Localize a stage-failure message_key defensively (unknown keys → a fixed
 * generic line, never the raw payload). */
export function localizeMessageKey(messageKey: string): string {
  if (messageKey in SETTINGS_MESSAGE_TEXT) {
    return SETTINGS_MESSAGE_TEXT[messageKey as SafeSettingsMessageKey];
  }
  return SETTINGS_MESSAGE_TEXT.SETTINGS_UNAVAILABLE;
}
