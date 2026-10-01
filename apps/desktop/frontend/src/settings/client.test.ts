import { describe, expect, it, vi } from "vitest";
import {
  buildSfxPolicySection,
  SETTINGS_GET_COMMAND,
  SETTINGS_UPDATE_SECTION_COMMAND,
  SettingsClient,
  SettingsClientError,
  sfxPolicyFromProjection,
  SFX_SECTION,
} from "./client";
import type { SfxPolicy } from "./types";

describe("SettingsClient command surface (PROPOSED wire names — BLOCKED_ON_CONTRACT)", () => {
  it("pins the proposed command names and section key", () => {
    // These names are this Task's PROPOSAL for the frozen-contract ruling
    // (production Tauri surface has no settings commands today). If the
    // integrator's ruling lands different names, this pin is the drift alarm.
    expect(SETTINGS_GET_COMMAND).toBe("settings_get");
    expect(SETTINGS_UPDATE_SECTION_COMMAND).toBe("settings_update_section");
    expect(SFX_SECTION).toBe("sfx");
  });
});

describe("buildSfxPolicySection (wire payload builder)", () => {
  it("builds the save_settings_section('sfx', {policy}) mirror for each of the three values", () => {
    expect(buildSfxPolicySection("skip")).toEqual({
      section: "sfx",
      values: { policy: "skip" },
    });
    expect(buildSfxPolicySection("translate")).toEqual({
      section: "sfx",
      values: { policy: "translate" },
    });
    expect(buildSfxPolicySection("manual")).toEqual({
      section: "sfx",
      values: { policy: "manual" },
    });
  });
});

describe("sfxPolicyFromProjection", () => {
  it("maps each legal policy value", () => {
    expect(sfxPolicyFromProjection({ settings: { sfx: { policy: "skip" } } })).toBe("skip");
    expect(sfxPolicyFromProjection({ settings: { sfx: { policy: "translate" } } })).toBe("translate");
    expect(sfxPolicyFromProjection({ settings: { sfx: { policy: "manual" } } })).toBe("manual");
  });

  it("collapses an unset section/key and an illegal value to the Core default (skip)", () => {
    // default skip must never be re-interpreted, just surfaced as-is
    expect(sfxPolicyFromProjection({ settings: {} })).toBe("skip");
    expect(sfxPolicyFromProjection({ settings: { sfx: {} } })).toBe("skip");
    expect(sfxPolicyFromProjection({ settings: { sfx: { policy: "bogus" } } })).toBe("skip");
    expect(sfxPolicyFromProjection(null)).toBe("skip");
    expect(sfxPolicyFromProjection(undefined)).toBe("skip");
  });
});

describe("SettingsClient save/get over a mocked invoke channel", () => {
  it("saveSfxPolicy invokes the section-update command with the exact payload, per value", async () => {
    for (const policy of ["skip", "translate", "manual"] as const satisfies readonly SfxPolicy[]) {
      const invoke = vi.fn(async () => ({}));
      const client = new SettingsClient(invoke);
      await client.saveSfxPolicy(policy);
      expect(invoke).toHaveBeenCalledTimes(1);
      expect(invoke).toHaveBeenCalledWith("settings_update_section", {
        section: "sfx",
        values: { policy },
      });
    }
  });

  it("getSfxPolicy invokes the read command and returns the effective policy", async () => {
    const invoke = vi.fn(async () => ({ settings: { sfx: { policy: "translate" } } }));
    const client = new SettingsClient(invoke);
    await expect(client.getSfxPolicy()).resolves.toBe("translate");
    expect(invoke).toHaveBeenCalledTimes(1);
    expect(invoke).toHaveBeenCalledWith("settings_get");
  });

  it("wraps a string rejection into a typed SettingsClientError (no retry)", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    const client = new SettingsClient(invoke);
    await expect(client.getSfxPolicy()).rejects.toMatchObject({ code: "CORE_UNAVAILABLE" });
    await expect(client.saveSfxPolicy("skip")).rejects.toBeInstanceOf(SettingsClientError);
    // exactly one attempt per operation — no retry loop (LibraryPanel rule)
    expect(invoke).toHaveBeenCalledTimes(2);
  });
});
