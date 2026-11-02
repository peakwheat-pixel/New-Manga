import { renderToString } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { SettingsPanel } from "./SettingsPanel";
import { SettingsClient } from "./client";
import type { SfxPolicy } from "./types";
import { installMockDom } from "../testSupport/mockDom";

/**
 * M2-SETTINGS-UI-SFX-POLICY AC2/AC3 — minimal SFX policy wiring on the
 * (new, minimal) settings section. Component tests follow the established
 * pattern: renderToString for static states, createRoot over the shared
 * mock DOM for mount/effect flows; every save parameter is asserted at the
 * client layer (SettingsClient — see client.test.ts) because the mock DOM
 * does not dispatch synthetic events.
 */

function selectOptionSelected(html: string, value: SfxPolicy): boolean {
  const pattern = new RegExp(
    `<option[^>]*value="${value}"[^>]*selected|<option[^>]*selected[^>]*value="${value}"`,
  );
  return pattern.test(html);
}

describe("SettingsPanel rendering (AC2)", () => {
  it("renders the Translation & Detection group with all three policy options, skip selected by default", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ sfxPolicy: "skip" }} />,
    );

    expect(html).toContain('data-testid="settings-panel"');
    expect(html).toContain("设置 (Settings)");
    expect(html).toContain("翻译与检测 (Translation &amp; Detection)");
    // three values, in display order, each with its bilingual label
    expect(html).toContain("跳过翻译 (skip)");
    expect(html).toContain("翻译 (translate)");
    expect(html).toContain("手动处理 (manual)");
    // the effective value is marked selected on the select
    expect(selectOptionSelected(html, "skip")).toBe(true);
    expect(selectOptionSelected(html, "translate")).toBe(false);
    expect(selectOptionSelected(html, "manual")).toBe(false);
    // effective-value line marks the Core default
    expect(html).toContain("当前生效值：");
    expect(html).toContain("（默认）");
  });

  it("marks translate as the current effective value when the Core reports it", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ sfxPolicy: "translate" }} />,
    );
    expect(selectOptionSelected(html, "translate")).toBe(true);
    expect(selectOptionSelected(html, "skip")).toBe(false);
    expect(html).not.toContain("（默认）");
  });

  it("marks manual as the current effective value when the Core reports it", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ sfxPolicy: "manual" }} />,
    );
    expect(selectOptionSelected(html, "manual")).toBe(true);
    expect(selectOptionSelected(html, "skip")).toBe(false);
  });

  it("renders the unset (null) state as the Core default skip, never as a stored value", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ sfxPolicy: null }} />,
    );
    expect(selectOptionSelected(html, "skip")).toBe(true);
    expect(html).toContain("（默认）");
  });

  it("carries the scope note verbatim (fact source: M2-SFX-TRANSLATE-ENTRY r1 R1)", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ sfxPolicy: "skip" }} />,
    );
    expect(html).toContain("保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）");
    expect(html).toContain('data-testid="sfx-policy-scope-note"');
  });

  it("disables the save button while the draft equals the effective value (nothing to save)", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ sfxPolicy: "skip" }} />,
    );
    expect(html).toContain('data-testid="sfx-policy-save-btn"');
    expect(html).toMatch(/<button[^>]*disabled[^>]*data-testid="sfx-policy-save-btn"|<button[^>]*data-testid="sfx-policy-save-btn"[^>]*disabled/);
  });

  it("renders the loading indicator when loading is true", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ loading: true }} />,
    );
    expect(html).toContain("正在加载设置数据...");
    expect(html).toContain('data-testid="settings-loading"');
  });

  it("renders the explicit load-error UI with no auto-retry notice", () => {
    const html = renderToString(
      <SettingsPanel initialState={{ error: "CORE_UNAVAILABLE" }} />,
    );
    // SSR splits interpolated text with comment markers ("加载失败: <!-- -->CODE"),
    // so the label and the code are asserted separately
    expect(html).toContain("加载失败:");
    expect(html).toContain("CORE_UNAVAILABLE");
    expect(html).toContain("系统不会自动重试");
    expect(html).toContain('data-testid="settings-load-error"');
    expect(html).not.toContain('data-testid="sfx-policy-select"');
  });
});

describe("SettingsPanel mounted flows (createRoot over the shared mock DOM)", () => {
  it("mounts, reads the effective policy via settings_get, and renders it as current", async () => {
    installMockDom();
    const { createRoot } = await import("react-dom/client");

    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_get") {
        return { settings: { sfx: { policy: "translate" } } };
      }
      return null;
    });
    const client = new SettingsClient(invoke);

    const doc = (globalThis as unknown as { document: { createElement(tag: string): unknown } })
      .document;
    const container = doc.createElement("DIV") as unknown as HTMLElement;
    const root = createRoot(container);

    root.render(<SettingsPanel client={client} />);

    await vi.waitFor(() => {
      expect(invoke).toHaveBeenCalledTimes(1);
      expect(invoke).toHaveBeenCalledWith("settings_get");
      expect(container.textContent).toContain("翻译与检测 (Translation & Detection)");
      expect(container.textContent).toContain("当前生效值：");
      expect(container.textContent).toContain("翻译 (translate)");
      expect(container.textContent).not.toContain("（默认）");
    });
  });

  it("mounts into the explicit load-error state when the read channel rejects, with no retry", async () => {
    installMockDom();
    const { createRoot } = await import("react-dom/client");

    let callCount = 0;
    const invoke = vi.fn(async () => {
      callCount += 1;
      throw "CORE_UNAVAILABLE";
    });
    const client = new SettingsClient(invoke);

    const doc = (globalThis as unknown as { document: { createElement(tag: string): unknown } })
      .document;
    const container = doc.createElement("DIV") as unknown as HTMLElement;
    const root = createRoot(container);

    root.render(<SettingsPanel client={client} />);

    await vi.waitFor(() => {
      expect(callCount).toBe(1);
      expect(container.textContent).toContain("加载失败: CORE_UNAVAILABLE");
      expect(container.textContent).toContain("系统不会自动重试");
    });
  });
});
