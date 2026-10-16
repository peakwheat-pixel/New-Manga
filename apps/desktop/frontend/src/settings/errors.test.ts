import { describe, expect, it } from "vitest";
import {
  SETTINGS_MESSAGE_TEXT,
  localizeMessageKey,
  projectSettingsError,
} from "./errors";

/**
 * P15-C1 §9 — the WebView error projection is CLOSED: any underlying
 * payload (message text, exception objects, raw responses) collapses into
 * (category, phase, action, message_key) and only fixed localized copy is
 * rendered. These tests pin the mapping and prove hostile payloads never
 * surface.
 */
describe("projectSettingsError (P15-C1 §9 closed projection)", () => {
  it("maps the known stable codes onto the closed enum", () => {
    expect(projectSettingsError("INVALID_REQUEST", "profile")).toEqual({
      category: "validation",
      phase: "profile",
      action: "edit_profile",
      message_key: "SETTINGS_INVALID_INPUT",
    });
    expect(projectSettingsError("INVALID_REQUEST", "binding")).toMatchObject({
      action: "select_profile",
    });
    expect(projectSettingsError("CORE_UNAVAILABLE", "profile")).toEqual({
      category: "unavailable",
      phase: "profile",
      action: "retry",
      message_key: "SETTINGS_UNAVAILABLE",
    });
    expect(projectSettingsError("CONFLICT", "binding")).toEqual({
      category: "conflict",
      phase: "binding",
      action: "clear_binding",
      message_key: "SETTINGS_CONFLICT",
    });
    expect(projectSettingsError("TLS_CONFIRMATION_REQUIRED", "tls")).toEqual({
      category: "validation",
      phase: "tls",
      action: "review_tls_setting",
      message_key: "TLS_CONFIRMATION_REQUIRED",
    });
    expect(projectSettingsError("CREDENTIAL_STORE_UNAVAILABLE", "credential_store")).toEqual({
      category: "unavailable",
      phase: "credential_store",
      action: "retry",
      message_key: "CREDENTIAL_STORE_UNAVAILABLE",
    });
  });

  it("drops hostile payloads — raw messages, paths, stack traces never survive projection", () => {
    const hostile = [
      "C:\\Users\\secret\\api_key.txt is invalid",
      "RuntimeError: boom at C:/repo/src/secret.py",
      JSON.stringify({ code: "INVALID_REQUEST", details: { path: "C:/x/y", auth: "Bearer abc" } }),
    ];
    for (const raw of hostile) {
      const projected = projectSettingsError(raw, "profile");
      expect(Object.keys(projected).sort()).toEqual(["action", "category", "message_key", "phase"]);
      expect(JSON.stringify(projected)).not.toContain("secret");
      expect(JSON.stringify(projected)).not.toContain("C:");
      expect(JSON.stringify(projected)).not.toContain("Bearer");
    }
  });

  it("collapses unknown codes and non-string garbage to a stable internal projection", () => {
    for (const raw of ["SOMETHING_NEW", "", undefined, null, 42, { weird: true }, new Error("boom")]) {
      const projected = projectSettingsError(raw, "network_proxy");
      expect(projected.category).toBe("internal");
      expect(projected.message_key).toBe("SETTINGS_UNAVAILABLE");
    }
  });

  it("every message_key has fixed zh-CN copy and localizeMessageKey never echoes unknown keys", () => {
    for (const key of Object.keys(SETTINGS_MESSAGE_TEXT) as (keyof typeof SETTINGS_MESSAGE_TEXT)[]) {
      expect(SETTINGS_MESSAGE_TEXT[key].length).toBeGreaterThan(0);
    }
    expect(localizeMessageKey("SETTINGS_INVALID_INPUT")).toBe(SETTINGS_MESSAGE_TEXT.SETTINGS_INVALID_INPUT);
    expect(localizeMessageKey("totally_unknown_key")).toBe(SETTINGS_MESSAGE_TEXT.SETTINGS_UNAVAILABLE);
  });
});
