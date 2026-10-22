import { describe, expect, it, vi } from "vitest";
import { SettingsClient, SettingsClientError } from "./client";

/**
 * SETTINGS-OPEN-A-1 AC3 — the generic section read/write pair used by the four
 * batch A panels. It reuses the frozen settings_get / settings_update_section
 * wire names and the same closed SettingsClientError mapping as the SFX
 * surface; it adds no new channel and no new key semantics.
 */
describe("SettingsClient generic section read/write (SETTINGS-OPEN-A-1)", () => {
  it("getSection sends exactly settings_get {section} and returns the section object", async () => {
    const invoke = vi.fn(async () => ({
      settings: { ocr: { script: "chinese", direction: "vertical" } },
    }));
    const client = new SettingsClient(invoke);
    await expect(client.getSection("ocr")).resolves.toEqual({
      script: "chinese",
      direction: "vertical",
    });
    expect(invoke).toHaveBeenCalledTimes(1);
    expect(invoke).toHaveBeenCalledWith("settings_get", { section: "ocr" });
  });

  it("getSection keeps JSON null / a missing section distinguishable as null", async () => {
    const nullInvoke = vi.fn(async () => ({ settings: { translate: null } }));
    await expect(new SettingsClient(nullInvoke).getSection("translate")).resolves.toBeNull();

    const missingInvoke = vi.fn(async () => ({ settings: {} }));
    await expect(new SettingsClient(missingInvoke).getSection("inpaint")).resolves.toBeNull();

    const emptyResult = vi.fn(async () => ({}));
    await expect(new SettingsClient(emptyResult).getSection("typeset")).resolves.toBeNull();
  });

  it("getSection fails closed to null for a non-object payload (never guesses a shape)", async () => {
    const invoke = vi.fn(async () => ({ settings: { ocr: "not-an-object" } }));
    await expect(new SettingsClient(invoke).getSection("ocr")).resolves.toBeNull();
  });

  it("getSection maps a rejected read to SettingsClientError with the stable code", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    const client = new SettingsClient(invoke);
    await expect(client.getSection("ocr")).rejects.toBeInstanceOf(SettingsClientError);
    await expect(client.getSection("ocr")).rejects.toMatchObject({ code: "CORE_UNAVAILABLE" });
  });

  it("saveSection sends exactly the whole-section upsert {section, values}", async () => {
    const invoke = vi.fn(async () => ({}));
    const client = new SettingsClient(invoke);
    await client.saveSection("translate", { context_pages: 3, context_token_budget: 4000 });
    expect(invoke).toHaveBeenCalledTimes(1);
    expect(invoke).toHaveBeenCalledWith("settings_update_section", {
      section: "translate",
      values: { context_pages: 3, context_token_budget: 4000 },
    });
  });

  it("saveSection maps a rejected write to SettingsClientError with the stable code", async () => {
    const invoke = vi.fn(async () => {
      throw { code: "INVALID_REQUEST" };
    });
    const client = new SettingsClient(invoke);
    await expect(client.saveSection("typeset", { stroke_width: 3 })).rejects.toMatchObject({
      code: "INVALID_REQUEST",
    });
    await expect(client.saveSection("typeset", { stroke_width: 3 })).rejects.toBeInstanceOf(
      SettingsClientError,
    );
  });
});
