/**
 * Settings-domain types for the React settings surface
 * (M2-SETTINGS-UI-SFX-POLICY).
 *
 * `sfx.policy` semantics come from M2-SFX-TRANSLATE-ENTRY (verification/
 * M2-SFX-TRANSLATE-ENTRY/integration.md): three values, default SKIP,
 * re-assembled per region — the policy is consumed when a region is
 * created (newly-created regions only; existing regions are never
 * retro-fitted, recovery = re-checkout or a fresh data root).
 */

/** The three SFX translation policies understood by the Python Core. */
export type SfxPolicy = "skip" | "translate" | "manual";

/** All legal values, in display order. The Core fail-fasts on anything else. */
export const SFX_POLICY_VALUES: readonly SfxPolicy[] = ["skip", "translate", "manual"] as const;

/** The Core default when `settings["sfx"]["policy"]` is unset. */
export const DEFAULT_SFX_POLICY: SfxPolicy = "skip";

/** Human-readable labels, following the bilingual style of LibraryPanel. */
export const SFX_POLICY_LABELS: Readonly<Record<SfxPolicy, string>> = {
  skip: "跳过翻译 (skip)",
  translate: "翻译 (translate)",
  manual: "手动处理 (manual)",
};

/** Runtime check for values crossing the IPC boundary (Core is the
 * authority; the UI treats anything unexpected as unset → default). */
export function isSfxPolicy(value: unknown): value is SfxPolicy {
  return (
    value === "skip" || value === "translate" || value === "manual"
  );
}

/* ------------------------------------------------------------------------
 * P15-C1 typed DTOs (contract §3 G21 / §4 G22 / §5 G23). Field names follow
 * the frozen Core command shapes verbatim; the Host constructs the safe
 * projections — the WebView never sees Secret/CredentialRef values.
 * ---------------------------------------------------------------------- */

/** Contract §3.1: Capability enum (exactly five values). */
export type Capability = "OCR" | "Translation" | "Inpaint" | "Detection" | "Rendering";

export const CAPABILITY_VALUES: readonly Capability[] = [
  "OCR",
  "Translation",
  "Inpaint",
  "Detection",
  "Rendering",
] as const;

export function isCapability(value: unknown): value is Capability {
  return (
    value === "OCR" ||
    value === "Translation" ||
    value === "Inpaint" ||
    value === "Detection" ||
    value === "Rendering"
  );
}

/** Contract §3.1/§5.1: read-only credential projection states. */
export type CredentialState = "configured" | "missing";

/** Contract §3.1: ProviderProfile — credential fields are read-only
 * projections; no Secret or CredentialRef ever appears in this DTO. */
export interface ProviderProfile {
  profile_id: string;
  provider_id: string;
  display_name: string;
  capabilities: Capability[];
  endpoint: string;
  model: string;
  network_profile_id: string | null;
  enabled: boolean;
  credential_state: CredentialState;
  credential_hint?: string;
}

/** Create payload (contract §3.2) — the exact editable key set of G25. */
export interface ProviderProfileInput {
  provider_id: string;
  display_name: string;
  capabilities: Capability[];
  endpoint: string;
  model: string;
  network_profile_id: string | null;
  enabled: boolean;
}

/** Update payload (contract §3.2) — provider_id is not editable. */
export interface ProviderProfileUpdateInput extends Omit<ProviderProfileInput, "provider_id"> {
  profile_id: string;
}

/** Contract §3.2: BindingScope. */
export type BindingScope =
  | { kind: "global" }
  | { kind: "book"; book_id: string }
  | { kind: "chapter"; chapter_id: string };

/** Contract §3.2: CapabilityBinding. */
export interface CapabilityBinding {
  scope: BindingScope;
  capability: Capability;
  profile_id: string;
}

/** Contract §4.1: CredentialTarget — identifies the entity, never carries a
 * Secret (the Host collects the secret outside the WebView). */
export type CredentialTarget =
  | { kind: "provider_api"; profile_id: string }
  | { kind: "proxy_auth"; network_profile_id: string };

export type CredentialIntent = "create" | "replace";

/** Contract §5.1: NetworkMode. */
export type NetworkMode = "Direct" | "System" | "HTTP" | "HTTPS" | "SOCKS5";

export const NETWORK_MODE_VALUES: readonly NetworkMode[] = [
  "Direct",
  "System",
  "HTTP",
  "HTTPS",
  "SOCKS5",
] as const;

export function isNetworkMode(value: unknown): value is NetworkMode {
  return NETWORK_MODE_VALUES.includes(value as NetworkMode);
}

/** Contract §5.1: NetworkProfile. */
export interface NetworkProfile {
  network_profile_id: string;
  display_name: string;
  mode: NetworkMode;
  proxy_endpoint: string | null;
  verify_tls: boolean;
  tls_verification_state: "enabled" | "disabled_confirmed";
  allow_proxy_failure_direct_fallback: boolean;
  credential_state: CredentialState;
  credential_hint?: string;
}

/** Create payload (contract §5.1). */
export interface NetworkProfileInput {
  display_name: string;
  mode: NetworkMode;
  proxy_endpoint: string | null;
  verify_tls?: boolean;
  confirm_disable_tls_verification?: boolean;
  allow_proxy_failure_direct_fallback?: boolean;
}

/** Update payload (contract §5.1). */
export interface NetworkProfileUpdateInput {
  network_profile_id: string;
  display_name: string;
  mode: NetworkMode;
  proxy_endpoint: string | null;
  verify_tls: boolean;
  confirm_disable_tls_verification?: boolean;
  allow_proxy_failure_direct_fallback: boolean;
}

/** Contract §5.2: six-stage connection test projection. */
export type NetworkStage = "Proxy" | "DNS" | "TCP" | "TLS" | "HTTP" | "ProviderAuth";

export type StageStatus = "passed" | "failed" | "not_run" | "not_applicable";

export type NotRunReason =
  | "upstream_stage_failed"
  | "provider_profile_not_selected"
  | "direct_mode";

export interface StageFailureProjection {
  category: string;
  action: string;
  message_key: string;
}

export type StageResult =
  | { stage: NetworkStage; status: "passed"; duration_ms?: number }
  | { stage: NetworkStage; status: "failed"; failure: StageFailureProjection; duration_ms?: number }
  | { stage: NetworkStage; status: "not_run" | "not_applicable"; reason: NotRunReason };

export interface NetworkTestResult {
  status: "passed" | "failed";
  failed_stage: NetworkStage | null;
  direct_fallback_used: false;
  stages: StageResult[];
}

/** Contract §5.1 ResolveNetworkProfile result. */
export interface ResolvedNetworkProfile {
  network_profile_id: string | null;
  mode: NetworkMode;
  source: "provider" | "global" | "system" | "direct";
}

/* ------------------------------------------------------------------------
 * Client-side input validation (UI affordance only — Core re-validates and
 * remains the authority; used for INVALID_REQUEST field highlighting).
 * ---------------------------------------------------------------------- */

/** Absolute HTTP(S) endpoint without userinfo/query/fragment (§3.2). */
export function isValidHttpEndpoint(endpoint: string): boolean {
  let url: URL;
  try {
    url = new URL(endpoint);
  } catch {
    return false;
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") return false;
  if (url.username !== "" || url.password !== "") return false;
  if (url.search !== "") return false;
  if (url.hash !== "") return false;
  return true;
}

/** Proxy endpoint scheme must match the selected mode (§5.1). */
export function proxyEndpointMatchesMode(endpoint: string, mode: NetworkMode): boolean {
  const expectedScheme =
    mode === "HTTP" ? "http:" : mode === "HTTPS" ? "https:" : mode === "SOCKS5" ? "socks5:" : null;
  if (expectedScheme === null) return false;
  try {
    return new URL(endpoint).protocol === expectedScheme;
  } catch {
    return false;
  }
}

/** Modes that require (HTTP/HTTPS/SOCKS5) vs forbid (Direct/System) a proxy
 * endpoint (§5.1). */
export function modeRequiresProxyEndpoint(mode: NetworkMode): boolean {
  return mode === "HTTP" || mode === "HTTPS" || mode === "SOCKS5";
}

/** Validate a provider-profile draft against the G25 key set. Returns a map
 * of field → error message (empty = valid). */
export function validateProviderProfileDraft(
  draft: Pick<ProviderProfileInput, "provider_id" | "display_name" | "capabilities" | "endpoint" | "model">,
): Record<string, string> {
  const errors: Record<string, string> = {};
  if (draft.provider_id.trim() === "") errors.provider_id = "provider_id 不能为空";
  if (draft.display_name.trim() === "") errors.display_name = "display_name 不能为空";
  if (draft.capabilities.length === 0) errors.capabilities = "至少选择一个 Capability";
  if (new Set(draft.capabilities).size !== draft.capabilities.length) {
    errors.capabilities = "Capability 不得重复";
  }
  if (!isValidHttpEndpoint(draft.endpoint.trim())) {
    errors.endpoint = "endpoint 必须是绝对 HTTP(S) 地址，且不含 userinfo/query/fragment";
  }
  if (draft.model.trim() === "") errors.model = "model 不能为空";
  return errors;
}

/** Validate a network-profile draft; proxy/endpoint combination and the TLS
 * danger confirmation are checked per §5.1. */
export function validateNetworkProfileDraft(input: {
  display_name: string;
  mode: NetworkMode;
  proxy_endpoint: string | null;
  verify_tls: boolean;
  tlsDangerConfirmed: boolean;
}): Record<string, string> {
  const errors: Record<string, string> = {};
  if (input.display_name.trim() === "") errors.display_name = "display_name 不能为空";
  if (modeRequiresProxyEndpoint(input.mode)) {
    if (input.proxy_endpoint === null || input.proxy_endpoint.trim() === "") {
      errors.proxy_endpoint = `${input.mode} 模式必须提供代理 endpoint`;
    } else if (!proxyEndpointMatchesMode(input.proxy_endpoint.trim(), input.mode)) {
      errors.proxy_endpoint = `代理 endpoint 的 scheme 必须与 ${input.mode} 模式一致`;
    }
  } else if (input.proxy_endpoint !== null && input.proxy_endpoint.trim() !== "") {
    errors.proxy_endpoint = `${input.mode} 模式不接受代理 endpoint（必须为 null）`;
  }
  if (!input.verify_tls && !input.tlsDangerConfirmed) {
    errors.verify_tls = "关闭 TLS 校验必须先完成危险确认";
  }
  return errors;
}
