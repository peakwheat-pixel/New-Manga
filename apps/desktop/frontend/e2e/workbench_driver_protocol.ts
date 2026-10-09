/**
 * P02 Workbench Real WebView2 Driver & Assertion Protocol (Stage A r4).
 *
 * NOTE: This file specifies Stage A data contracts, type structures, and WCAG 2.1
 * mathematical models. Full interactive CDP / WebView behavioral driving is NOT yet
 * active in Stage A (held BLOCKED under the Hard Build Barrier awaiting authorized
 * scratch-build registration by Codex).
 */

export interface HostRuntimeProof {
  isWebView2: boolean;
  userAgent: string;
  hasTauriBridge: boolean;
  hasChromeWebView: boolean;
  runtimeIdentity: string;
}

export interface TimingSample {
  action: string;
  timestampMs: number;
  deltaMs?: number;
}

export interface ContrastSample {
  elementSelector: string;
  role: "text" | "large_text" | "ui_component" | "disabled";
  computedForeground: string;
  computedBackground: string;
  tokenMapping: "MAPPED" | "UNMAPPED" | "NOT_APPLICABLE";
  contrastRatio: number | null;
  contrastResult: "PASS" | "FAIL" | "NOT_VERIFIABLE";
  notes?: string;
}

/**
 * Scenario verdict contract matching the exact schema emitted by the Python harness (H-07).
 */
export interface ScenarioVerdict {
  scenario_id: string;
  scenario_name: string;
  status: "PASS" | "FAIL" | "BLOCKED" | "NOT_RUN";
  layer:
    | "REAL_WEBVIEW2"
    | "REAL_WEBVIEW_MOCK_IPC"
    | "FILESYSTEM"
    | "STATIC_AST"
    | "TOKEN_MODEL"
    | "BLOCKED_NO_BUILD";
  exit_code: number | null;
  details?: Record<string, unknown>;
  blocker_reason?: string | null;
  timestamp: string;
}

/**
 * AC1 Contract: Proves whether the current execution context is a real Windows WebView2
 * host rather than JSDOM, external Chrome/Firefox, or SSR.
 */
export function proveWebView2Runtime(): HostRuntimeProof {
  const win = window as unknown as {
    chrome?: { webview?: Record<string, unknown> };
    __TAURI__?: { core?: { invoke?: unknown } };
  };

  const hasChromeWebView = typeof win.chrome?.webview !== "undefined";
  const hasTauriBridge = typeof win.__TAURI__?.core?.invoke !== "undefined";
  const userAgent = navigator.userAgent;
  const isWebView2 = hasChromeWebView || /Edg\/\d+.*AppX|WebView/i.test(userAgent);

  return {
    isWebView2,
    userAgent,
    hasTauriBridge,
    hasChromeWebView,
    runtimeIdentity: isWebView2 ? "Microsoft_Edge_WebView2" : "NON_WEBVIEW2_ENVIRONMENT",
  };
}

/**
 * Calculates relative luminance according to WCAG 2.1 spec.
 * https://www.w3.org/WAI/GL/wiki/Relative_luminance
 */
export function calculateRelativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((val) => {
    const s = val / 255;
    return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

/**
 * Performs alpha blending of a color over an opaque background.
 * Composite = alpha * color + (1 - alpha) * background
 */
export function blendAlpha(
  colorRgba: [number, number, number, number],
  opaqueBaseRgb: [number, number, number],
): [number, number, number] {
  const [rc, gc, bc, a] = colorRgba;
  const [rb, gb, bb] = opaqueBaseRgb;
  return [
    Math.round(a * rc + (1 - a) * rb),
    Math.round(a * gc + (1 - a) * gb),
    Math.round(a * bc + (1 - a) * bb),
  ];
}

/**
 * Parses CSS rgb/rgba/hex string into [r, g, b, a].
 */
export function parseCssColor(colorStr: string): [number, number, number, number] | null {
  const trimmed = colorStr.trim().toLowerCase();
  if (trimmed.startsWith("#")) {
    const hex = trimmed.slice(1);
    if (hex.length === 3) {
      const [r, g, b] = hex.split("").map((c) => parseInt(c + c, 16));
      return [r, g, b, 1.0];
    }
    if (hex.length === 6) {
      const r = parseInt(hex.slice(0, 2), 16);
      const g = parseInt(hex.slice(2, 4), 16);
      const b = parseInt(hex.slice(4, 6), 16);
      return [r, g, b, 1.0];
    }
  }
  const match = trimmed.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
  if (match) {
    const r = parseInt(match[1], 10);
    const g = parseInt(match[2], 10);
    const b = parseInt(match[3], 10);
    const a = match[4] !== undefined ? parseFloat(match[4]) : 1.0;
    return [r, g, b, a];
  }
  return null;
}

/**
 * AC6 Math Model: Calculates contrast ratio between foreground and background.
 * If background has alpha, an opaque base background must be supplied; otherwise NOT_VERIFIABLE.
 * Composite foreground is then blended over the effective background before calculating WCAG ratio.
 */
export function calculateContrastRatio(
  fgRgba: [number, number, number, number],
  bgRgba: [number, number, number, number],
  knownOpaqueBaseRgb?: [number, number, number],
): { ratio: number | null; status: "PASS" | "FAIL" | "NOT_VERIFIABLE"; notes?: string } {
  let effectiveBg: [number, number, number];

  if (bgRgba[3] < 1.0) {
    if (!knownOpaqueBaseRgb) {
      return {
        ratio: null,
        status: "NOT_VERIFIABLE",
        notes: "Background has alpha < 1.0 but no known opaque base background was provided",
      };
    }
    effectiveBg = blendAlpha(bgRgba, knownOpaqueBaseRgb);
  } else {
    effectiveBg = [bgRgba[0], bgRgba[1], bgRgba[2]];
  }

  const effectiveFg = fgRgba[3] < 1.0 ? blendAlpha(fgRgba, effectiveBg) : [fgRgba[0], fgRgba[1], fgRgba[2]];

  const l1 = calculateRelativeLuminance(...effectiveFg);
  const l2 = calculateRelativeLuminance(...effectiveBg);
  const brighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  const ratio = Number(((brighter + 0.05) / (darker + 0.05)).toFixed(2));

  return { ratio, status: "PASS" };
}

/**
 * Evaluates contrast compliance according to UI/UX GUI Design Contract §7.2 / §9.
 */
export function evaluateContrast(
  fgStr: string,
  bgStr: string,
  role: "text" | "large_text" | "ui_component" | "disabled",
  selector: string,
  tokenMapping: "MAPPED" | "UNMAPPED" | "NOT_APPLICABLE" = "UNMAPPED",
  knownOpaqueBaseRgb?: [number, number, number],
): ContrastSample {
  const fg = parseCssColor(fgStr);
  const bg = parseCssColor(bgStr);

  if (!fg || !bg) {
    return {
      elementSelector: selector,
      role,
      computedForeground: fgStr,
      computedBackground: bgStr,
      tokenMapping,
      contrastRatio: null,
      contrastResult: "NOT_VERIFIABLE",
      notes: "Could not parse foreground or background color string",
    };
  }

  const result = calculateContrastRatio(fg, bg, knownOpaqueBaseRgb);
  if (result.status === "NOT_VERIFIABLE" || result.ratio === null) {
    return {
      elementSelector: selector,
      role,
      computedForeground: fgStr,
      computedBackground: bgStr,
      tokenMapping,
      contrastRatio: null,
      contrastResult: "NOT_VERIFIABLE",
      notes: result.notes,
    };
  }

  const minRequired = role === "text" ? 4.5 : 3.0;
  const isPass = result.ratio >= minRequired;

  return {
    elementSelector: selector,
    role,
    computedForeground: fgStr,
    computedBackground: bgStr,
    tokenMapping,
    contrastRatio: result.ratio,
    contrastResult: isPass ? "PASS" : "FAIL",
    notes: `Required: >=${minRequired}:1, Actual: ${result.ratio}:1`,
  };
}
